"""
Group B2-B5: the frozen confirmation run.

Uses the split saved by script 27 (confirmation_split_assignment.csv) so
every step reads the SAME split rather than regenerating it. The pipeline
is fit entirely on the EXPLORE half and applied once, unmodified, to the
CONFIRM half.

Includes the multivariable-controls step. Finding #4 was called the
strongest result specifically because it got STRONGER under controls,
unlike everything else tonight -- a confirmation pipeline that skips that
step validates a materially weaker claim than the one actually being
tested. Added here rather than scoping the claim down.

Note on GI-tercile stratification (script 27): stratifying the split on
the MARGINAL distribution of abs_gi never touches the error~GI
relationship under test -- that requires looking at error, which
balancing does not do. It protects against range restriction (an unlucky
split that leaves one half short on high-GI positions, which would
mechanically shrink an observed correlation regardless of whether the
true relationship is stable). Not circular; stated here explicitly.

z-scores reported alongside p-values throughout this project assume the
permutation null's tail is Gaussian, which a few hundred draws cannot
verify that far out. The p-value (bounded by 1/n_perm) is the
empirically demonstrated claim; z-scores are scale context only.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.regions import assign_region
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.io import load_structural_features
from scripts.lib.stats import crossfit_isotonic_within_group, position_cluster_bootstrap, _spearman
from scripts.lib.own_context import (fit_single_arm, fit_interaction, wls_line,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS, MT_SCORE_COLS, MT_SE_COLS)

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p, n):
    return f"<{1/n:.4f}" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    split = pd.read_csv(PROC / "confirmation_split_assignment.csv")
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df = add_substitution_features(df)
    df = add_structural_features(df, load_structural_features())
    df["region"] = assign_region(df["position"])
    df = df.merge(split, on="position", how="left")
    explore = df[df["set"] == "explore"].copy()
    confirm = df[df["set"] == "confirm"].copy()
    print(f"explore: {len(explore)} rows / confirm: {len(confirm)} rows")
    print("Pipeline fit on EXPLORE only, applied once to CONFIRM. No iteration.\n")

    # --- calibration fit on explore, applied to confirm ---
    def within_region_predict(train_df, test_df):
        from sklearn.isotonic import IsotonicRegression
        preds = pd.Series(np.nan, index=test_df.index, dtype=float)
        for r, tr in train_df.groupby("region"):
            te = test_df[test_df["region"] == r]
            if len(te) == 0 or len(tr) < 10:
                continue
            iso = IsotonicRegression(out_of_bounds="clip", increasing="auto")
            iso.fit(tr["model_C"].to_numpy(), tr["target"].to_numpy())
            preds.loc[te.index] = iso.predict(te["model_C"].to_numpy())
        return preds

    confirm["pred"] = within_region_predict(explore, confirm)
    confirm["err_cal"] = (confirm["target"] - confirm["pred"]).abs()
    confirm["err_rank"] = (confirm["model_C"].rank() - confirm["target"].rank()).abs()

    results = []
    print("=" * 72)
    print("B2/B3a: BASELINE CORRELATION on confirmation half")
    print("=" * 72)
    for ec, el in [("err_rank", "rank-based"), ("err_cal", "calibrated")]:
        sub = confirm.dropna(subset=["abs_gi", ec])
        r = position_cluster_bootstrap(sub, "position", "abs_gi", ec, n_boot=N_BOOT, seed=SEED)
        print(f"  {el}: rho={r['observed_rho']:+.4f} CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"n={r['n_rows']} pos={r['n_clusters']}")
        results.append({"stage": "baseline", "error_metric": el, "rho": r["observed_rho"],
                        "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"], "n": r["n_rows"]})

    print("\n" + "=" * 72)
    print("B3b: MULTIVARIABLE CONTROLS on confirmation half")
    print("=" * 72)
    for ec, el in [("err_rank", "rank-based"), ("err_cal", "calibrated")]:
        cont = ["abs_gi", "f_bar_a222v", "grantham", "blosum62", "rsa"]
        d = confirm.dropna(subset=cont + [ec, "domain", "position"]).copy()
        for c in cont:
            sd = d[c].std(); d[c] = (d[c] - d[c].mean()) / (sd if sd > 0 else 1)
        X = sm.add_constant(pd.concat([d[cont], pd.get_dummies(d["domain"], prefix="dom",
                                       drop_first=True, dtype=float)], axis=1))
        y = (d[ec] - d[ec].mean()) / d[ec].std()
        m = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": d["position"]})
        b, se = m.params["abs_gi"], m.bse["abs_gi"]
        lo, hi = b - 1.96 * se, b + 1.96 * se
        surv = not (lo < 0 < hi)
        print(f"  {el}: coef={b:+.4f} CI=[{lo:+.4f},{hi:+.4f}] "
              f"-> {'SURVIVES' if surv else 'does NOT survive'} (n={len(d)})")
        results.append({"stage": "multivariable", "error_metric": el, "rho": b,
                        "ci_lo": lo, "ci_hi": hi, "n": len(d), "survives": surv})

    print("\n" + "=" * 72)
    print(f"B3c: SIGN-FLIP NULL on confirmation half (n_perm={N_PERM})")
    print("=" * 72)
    rng = np.random.default_rng(SEED)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    W = raw[WT_SCORE_COLS].to_numpy(float); Wse = raw[WT_SE_COLS].to_numpy(float)
    M = raw[MT_SCORE_COLS].to_numpy(float); Mse = raw[MT_SE_COLS].to_numpy(float)
    w = fit_single_arm(W, Wse); w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(raw["hgvs"].to_numpy() == "p.Ala222Val")[0][0])
    e1 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                         w["fitness"][i222], w["remediation"][i222])
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1["e_r"][keep])
    e2 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                         w["fitness"][i222], w["remediation"][i222], correction=(cb, cr))
    own = pd.DataFrame({"hgvs_pro": raw["hgvs"], "type": raw["type"], "own_e_b": e2["e_b"]})
    conf_own = confirm.merge(own[own.type == "substitution"], on="hgvs_pro", how="inner")
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in conf_own["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    for ec, el in [("err_rank", "rank-based"), ("err_cal", "calibrated")]:
        errv = conf_own[ec].to_numpy()
        good = np.isfinite(conf_own["own_e_b"].to_numpy()) & np.isfinite(errv)
        obs = _spearman(np.abs(conf_own["own_e_b"].to_numpy()[good]), errv[good])
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1., 1.], size=Rs.shape), Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(errv)
            null[p] = _spearman(np.abs(eb_p[g]), errv[g])
        pv = (np.abs(null) >= abs(obs)).mean()
        print(f"  {el}: observed={obs:+.4f} null_mean={null.mean():+.4f} "
              f"p={pstr(pv, N_PERM)}")
        results.append({"stage": "signflip_null", "error_metric": el, "rho": obs,
                        "null_mean": null.mean(), "p": pv, "n_perm": N_PERM})

    out = pd.DataFrame(results)
    out.to_csv(PROC / "confirmation_run_results.csv", index=False)
    print(f"\nSaved to {PROC / 'confirmation_run_results.csv'}")
    print("\nThis run was executed exactly once. No result above should be used to")
    print("justify rerunning with a different seed, covariate set, or calibration choice.")
