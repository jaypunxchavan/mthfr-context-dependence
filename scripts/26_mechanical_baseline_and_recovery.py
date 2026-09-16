"""
Group A: proper distribution-based versions of two tests, plus recovery
of finding #4's null standard deviation.

Both the mechanical-baseline test and the region-2 magnitude test were
run as full N-draw distributions last round, but only summary numbers
were carried into the write-up rather than the saved percentile/p-value.
This reruns both properly, saves the full result, and separately recovers
finding #4's null_sd, which was computed in memory but never persisted.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scipy.stats import spearmanr
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import crossfit_isotonic_by_position, _spearman
from scripts.lib.own_context import (fit_single_arm, fit_interaction, wls_line,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS, MT_SCORE_COLS, MT_SE_COLS)

N = int(os.environ.get("N_MECH", 500))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"

if __name__ == "__main__":
    rng = np.random.default_rng(SEED)

    print("=" * 72)
    print(f"MECHANICAL BASELINE: {N} draws, matched predictor correlation")
    print("=" * 72)
    df = pd.read_csv(PROC / "phase5_analysis_table.csv").dropna(
        subset=["model_C", "target", "f_bar"])
    n = len(df)
    f_bar, target = df["f_bar"].to_numpy(), df["target"].to_numpy()
    real_pred_corr = spearmanr(df["esm2_score"], df["model_C"]).statistic
    real_err_corr = 0.6581

    lo, hi = 0.0, 3.0
    for _ in range(30):
        mid = (lo + hi) / 2
        z = rng.standard_normal(2000)
        r = spearmanr(z + rng.standard_normal(2000) * mid,
                     z + rng.standard_normal(2000) * mid).statistic
        lo, hi = (mid, hi) if r > real_pred_corr else (lo, mid)
    noise_scale = mid

    null_err = np.empty(N)
    for i in range(N):
        z = rng.standard_normal(n)
        s1 = z + rng.standard_normal(n) * noise_scale
        s2 = z + rng.standard_normal(n) * noise_scale
        e1 = np.abs(pd.Series(s1).rank().to_numpy() - pd.Series(f_bar).rank().to_numpy())
        e2 = np.abs(pd.Series(s2).rank().to_numpy() - pd.Series(target).rank().to_numpy())
        null_err[i] = _spearman(e1, e2)

    z_score = (real_err_corr - null_err.mean()) / null_err.std()
    pct = (null_err <= real_err_corr).mean()
    print(f"  real predictor correlation matched: {real_pred_corr:.6f}")
    print(f"  null: mean={null_err.mean():.4f} sd={null_err.std():.4f} "
          f"range=[{null_err.min():.4f},{null_err.max():.4f}]")
    print(f"  real observed error-metric correlation: {real_err_corr:.4f}")
    print(f"  z={z_score:.2f} sd below mechanical floor; "
          f"{(null_err<=real_err_corr).sum()}/{N} draws reached that low")
    pd.DataFrame([{"test": "mechanical_baseline", "n_draws": N,
                  "null_mean": null_err.mean(), "null_sd": null_err.std(),
                  "null_min": null_err.min(), "null_max": null_err.max(),
                  "observed": real_err_corr, "z_score": z_score,
                  "p_below_floor": pct}]).to_csv(
        PROC / "task_mechanical_baseline.csv", index=False)

    print("\n" + "=" * 72)
    print(f"REGION-2 MAGNITUDE: {N} draws")
    print("=" * 72)
    df["region"] = assign_region(df["position"])
    pred_pooled = crossfit_isotonic_by_position(df, "position", "model_C",
                                                "target", n_folds=5, seed=SEED)
    df["err_pooled"] = (df["target"] - pred_pooled).abs()
    real_r2 = -0.1124
    null_r2 = np.empty(N)
    for i in range(N):
        fake = rng.permutation(df["target"].to_numpy())
        df["_fake"] = fake
        sub = df[df.region == 2]
        null_r2[i] = _spearman(sub["err_pooled"], sub["_fake"])
    z2 = (real_r2 - null_r2.mean()) / null_r2.std()
    pct2 = (np.abs(null_r2) >= abs(real_r2)).mean()
    print(f"  null: mean={null_r2.mean():+.4f} sd={null_r2.std():.4f} "
          f"range=[{null_r2.min():+.4f},{null_r2.max():+.4f}]")
    print(f"  real observed region-2 rho: {real_r2:+.4f}")
    print(f"  z={z2:.2f} sd; {(np.abs(null_r2)>=abs(real_r2)).sum()}/{N} draws matched or exceeded")
    pd.DataFrame([{"test": "region2_magnitude", "n_draws": N,
                  "null_mean": null_r2.mean(), "null_sd": null_r2.std(),
                  "null_min": null_r2.min(), "null_max": null_r2.max(),
                  "observed": real_r2, "z_score": z2, "p_value": pct2}]).to_csv(
        PROC / "task_region2_magnitude.csv", index=False)

    print("\n" + "=" * 72)
    print(f"FINDING #4 NULL RECOVERY: {N} perms, null_sd now persisted")
    print("=" * 72)
    d = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    W = d[WT_SCORE_COLS].to_numpy(float); Wse = d[WT_SE_COLS].to_numpy(float)
    M = d[MT_SCORE_COLS].to_numpy(float); Mse = d[MT_SE_COLS].to_numpy(float)
    w = fit_single_arm(W, Wse); w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(d["hgvs"].to_numpy() == "p.Ala222Val")[0][0])
    e1x = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                          w["fitness"][i222], w["remediation"][i222])
    keep = (w["logl"] > LOGL_CUTOFF) & (e1x["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1x["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1x["e_r"][keep])
    e2x = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                          w["fitness"][i222], w["remediation"][i222], correction=(cb, cr))

    own = pd.DataFrame({"hgvs_pro": d["hgvs"], "type": d["type"], "own_e_b": e2x["e_b"]})
    merged = df.merge(own[own.type == "substitution"], on="hgvs_pro", how="inner")
    merged["err_rank_C"] = (merged["model_C"].rank() - merged["target"].rank()).abs()
    merged["pred_cal_C"] = crossfit_isotonic_by_position(
        merged, "position", "model_C", "target", n_folds=5, seed=SEED)
    merged["err_cal_C"] = (merged["target"] - merged["pred_cal_C"]).abs()

    row_of = {h: i for i, h in enumerate(d["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in merged["hgvs_pro"]])
    Rs, Ss, Vs = e2x["resid"][src], Mse[src], e2x["valid"][src]

    rows = []
    for ec, el in [("err_rank_C", "rank-based"), ("err_cal_C", "calibrated")]:
        errv = merged[ec].to_numpy()
        good = np.isfinite(merged["own_e_b"].to_numpy()) & np.isfinite(errv)
        obs = _spearman(np.abs(merged["own_e_b"].to_numpy()[good]), errv[good])
        null = np.empty(N)
        for p in range(N):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1., 1.], size=Rs.shape), Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(errv)
            null[p] = _spearman(np.abs(eb_p[g]), errv[g])
        pv = (np.abs(null) >= abs(obs)).mean()
        z = (obs - null.mean()) / null.std()
        excess = obs - null.mean()
        frac = 1 - abs(excess) / abs(obs)
        print(f"  {el}: observed={obs:+.4f} null_mean={null.mean():+.4f} "
              f"null_sd={null.std():.4f} z={z:.2f} p={pv:.4f}")
        rows.append({"error_metric": el, "gi_source": "own e_b", "rho": obs,
                     "null_mean": null.mean(), "null_sd": null.std(), "z_score": z,
                     "excess_over_null": excess, "frac_artifact": frac,
                     "p": pv, "n": int(good.sum()), "n_perm": N})
    pd.DataFrame(rows).to_csv(PROC / "task4_signflip_recovered.csv", index=False)

    print(f"\nSaved: task_mechanical_baseline.csv, task_region2_magnitude.csv, "
          f"task4_signflip_recovered.csv")
