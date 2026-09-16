"""
Task: put the accuracy-degradation finding through the full gauntlet.

THE ORIGINAL FINDING (script 16): splitting variants into three coarse
interaction strata gave ESM-2 correlations of 0.53 / 0.35 / 0.17 against
real A222V-background fitness. It was the largest effect in the project
and the only claim never stress-tested.

WHY IT NEEDED TESTING, SPECIFICALLY: it stratifies on the same quantity
(folinate-independent genetic interaction) whose own correlation with
error turned out to be 77-82% structural artifact once run against a
proper null (script 21). A pattern built on that quantity is downstream
of the same foundation, so it cannot be assumed independent.

SHARPER MEASUREMENT: three buckets throw away information and the bucket
count was never itself justified. This reframes the identical question
continuously -- define per-variant error for ESM-2 scoring the CORRECT
A222V background, then relate that error to interaction strength directly.

Four checks, the same battery applied to every other claim tonight:
  1b baseline correlation, position-cluster bootstrap
  1c multivariable controls (fitness, Grantham, BLOSUM62, RSA, domain)
  1d sign-flip re-derivation null  <- the test that killed one result
                                      and cut another by 80%
  1e region check
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr
from scripts.lib.io import load_structural_features
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import (position_cluster_bootstrap, crossfit_isotonic_by_position,
                               partial_spearman_cluster_bootstrap, _spearman)
from scripts.lib.own_context import (fit_single_arm, fit_interaction, wls_line,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS, MT_SCORE_COLS, MT_SE_COLS)

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = df.dropna(subset=["model_C", "target"]).copy()
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    # --- 1a: per-variant error for ESM-2 scoring the CORRECT background ---
    df["err_rank_C"] = (df["model_C"].rank() - df["target"].rank()).abs()
    df["pred_C"] = crossfit_isotonic_by_position(df, "position", "model_C",
                                                 "target", n_folds=5, seed=SEED)
    df["err_cal_C"] = (df["target"] - df["pred_C"]).abs()
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df["abs_gi_own"] = df["own_e_b"].abs()
    df["region"] = assign_region(df["position"])

    print("\nReplicating the original three-stratum framing for reference:")
    s = df.dropna(subset=["abs_gi"]).copy()
    s["stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    for lvl in ["low", "mid", "high"]:
        sub = s[s["stratum"] == lvl]
        print(f"  GI {lvl:4s} n={len(sub):5d}  rho(model_C, real fitness)="
              f"{_spearman(sub['model_C'], sub['target']):+.4f}")

    ERRS = [("err_rank_C", "rank-based"), ("err_cal_C", "calibrated")]
    rows = []

    print(f"\n{'='*72}\n1b BASELINE: error vs interaction strength (n_boot={N_BOOT})\n{'='*72}")
    for ec, el in ERRS:
        for gc, gl in [("abs_gi", "published e.b"), ("abs_gi_own", "own e_b")]:
            r = position_cluster_bootstrap(df, "position", gc, ec, n_boot=N_BOOT, seed=SEED)
            print(f"  {el:11s} vs {gl:14s} rho={r['observed_rho']:+.4f} "
                  f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'])} n={r['n_rows']}")
            rows.append({"stage": "baseline", "error_metric": el, "gi_source": gl,
                         "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                         "ci_hi": r["ci_hi"], "p": r["p_boot"], "n": r["n_rows"]})

    print(f"\n{'='*72}\n1c MULTIVARIABLE CONTROLS\n{'='*72}")
    d2 = add_structural_features(add_substitution_features(df), load_structural_features())
    for ec, el in ERRS:
        cont = ["abs_gi", "f_bar_a222v", "grantham", "blosum62", "rsa"]
        d = d2.dropna(subset=cont + [ec, "domain", "position"]).copy()
        for c in cont:
            sd = d[c].std(); d[c] = (d[c] - d[c].mean()) / (sd if sd > 0 else 1)
        X = sm.add_constant(pd.concat([d[cont], pd.get_dummies(d["domain"], prefix="dom",
                                       drop_first=True, dtype=float)], axis=1))
        y = (d[ec] - d[ec].mean()) / d[ec].std()
        m = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": d["position"]})
        b, se = m.params["abs_gi"], m.bse["abs_gi"]
        lo, hi = b - 1.96 * se, b + 1.96 * se
        surv = not (lo < 0 < hi)
        print(f"  {el:11s} coef={b:+.4f} CI=[{lo:+.4f},{hi:+.4f}] p={m.pvalues['abs_gi']:.4g}"
              f"  -> {'SURVIVES' if surv else 'does NOT survive'}  (n={len(d)})")
        rows.append({"stage": "multivariable", "error_metric": el, "gi_source": "published e.b",
                     "rho": b, "ci_lo": lo, "ci_hi": hi, "p": m.pvalues["abs_gi"], "n": len(d)})

    print(f"\n{'='*72}\n1d SIGN-FLIP RE-DERIVATION NULL ({N_PERM} perms)\n{'='*72}")
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
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in df["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    chk, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    ok = np.isfinite(chk) & np.isfinite(df["own_e_b"].to_numpy())
    print(f"  sanity: zero-flip reproduces own_e_b, max|diff|="
          f"{np.abs(chk[ok]-df['own_e_b'].to_numpy()[ok]).max():.3e}")

    for ec, el in ERRS:
        errv = df[ec].to_numpy()
        good = np.isfinite(df["own_e_b"].to_numpy()) & np.isfinite(errv)
        obs = _spearman(np.abs(df["own_e_b"].to_numpy()[good]), errv[good])
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(errv)
            null[p] = _spearman(np.abs(eb_p[g]), errv[g])
        pv = (np.abs(null) >= abs(obs)).mean()
        excess = obs - null.mean()
        frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
        print(f"  {el}: observed={obs:+.4f} null mean={null.mean():+.4f} "
              f"sd={null.std():.4f} p={pstr(pv)}")
        print(f"    excess over null={excess:+.4f}  ({100*frac:.0f}% structural artifact)"
              f"  -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'}")
        rows.append({"stage": "signflip_null", "error_metric": el, "gi_source": "own e_b",
                     "rho": obs, "null_mean": null.mean(), "excess_over_null": excess,
                     "frac_artifact": frac, "p": pv, "n": int(good.sum())})

    print(f"\n{'='*72}\n1e REGION CHECK\n{'='*72}")
    for ec, el in ERRS:
        pooled = position_cluster_bootstrap(df, "position", "abs_gi", ec,
                                            n_boot=N_BOOT, seed=SEED)
        print(f"  {el}: pooled rho={pooled['observed_rho']:+.4f} "
              f"CI=[{pooled['ci_lo']:+.4f},{pooled['ci_hi']:+.4f}]")
        for rg in sorted(REGION_BOUNDS):
            sub = df[df["region"] == rg]
            if sub["position"].nunique() < 30:
                continue
            res = position_cluster_bootstrap(sub, "position", "abs_gi", ec,
                                             n_boot=N_BOOT, seed=SEED)
            ov = not (res["ci_hi"] < pooled["ci_lo"] or res["ci_lo"] > pooled["ci_hi"])
            lo, hi = REGION_BOUNDS[rg]
            print(f"    region {rg} ({lo}-{hi}) rho={res['observed_rho']:+.4f} "
                  f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}]"
                  f"{'' if ov else '  <-- does NOT overlap pooled'}")
            rows.append({"stage": "region", "error_metric": el, "gi_source": f"region_{rg}",
                         "rho": res["observed_rho"], "ci_lo": res["ci_lo"],
                         "ci_hi": res["ci_hi"], "p": res["p_boot"],
                         "n": res["n_rows"], "overlaps_pooled": ov})

    pd.DataFrame(rows).to_csv(PROC / "task_accuracy_degradation.csv", index=False)
    print(f"\nSaved to {PROC / 'task_accuracy_degradation.csv'}")
