"""
Task B1a + B1b (review-triage): is the delta_ESM <-> e.b correlation just
both variables tracking deleteriousness ("flattening" confound)?

B1a — PARTIAL CORRELATION
  Raw rho(delta_ESM, e.b) = -0.088 (own) / -0.071 (published). Both
  delta_ESM and e.b plausibly track baseline deleteriousness: if the
  correlation collapses once S(v|WT) and w.fitness are controlled
  NONLINEARLY, the "ESM-2 moves the opposite direction" story reduces to
  "both variables track deleteriousness independently."

B1b — COMPRESSION TEST (delta_ESM ≈ -k * S(v|WT)?)
  If supplying V222 merely flattens ESM-2's output distribution toward
  zero, then C ≈ c*A with c<1, so delta = C - A ≈ (c-1)*A: a straight
  line through the origin with negative slope. Then the e.b correlation
  could be inherited from e.b's own relation to S(v|WT).

PRE-REGISTERED DECISION RULES (fixed before running; AGENTS.md §6):
  * Nuisance model: natural cubic spline, df=4, per covariate (patsy cr),
    fit jointly on RANKS (spearman semantics). Variables: S(v|WT) =
    esm2_score column, and w.fitness = base_functionality (the atlas's
    fitted w.fitness; f_bar_wt run as a robustness variant, both reported).
  * Inference: position-cluster bootstrap; the nuisance model is REFIT
    inside every draw (not fixed), positions sampled with replacement.
  * "Collapse" criterion: |partial rho| < 50% of |raw rho| => the script
    prints COLLAPSE. Otherwise SURVIVES-SHAPED. CI reported either way;
    this threshold is NOT to be revised after seeing results.
  * Both own_e_b and published GI_folinate_independent are reported for
    every configuration — no selection across the two.
  * N_BOOT from environment (default 2000).

LIMITATIONS STATED UP FRONT:
  * w.fitness sits inside e.b's own construction (e.b is the residual of
    the A222V arm against an expectation built from the WT arm, which
    contains w.fitness). Controlling for it is part-whole coupling: a
    collapse here is CONSISTANT with the deleteriousness story but not
    proof of it, and non-collapse is the stronger direction of evidence.
    This is the review's requested test; the caveat is stated, not hidden.
  * A spline with df=4 controls smooth nonlinearity only; a highly
    discontinuous confound could survive it.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
import patsy
from scripts.lib.stats import position_cluster_bootstrap, _spearman

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
SPLINE_DF = 4


def basis(cols):
    """Natural cubic spline design matrix for each column of cols (df=4 each)."""
    parts = [patsy.cr(cols[:, j], df=SPLINE_DF) for j in range(cols.shape[1])]
    return np.column_stack([np.ones(len(cols))] + parts)


def resid_ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def partial_spearman_spline(x, y, z_mat):
    """Spearman(x,y) after spline-residualizing both on z (ranks throughout)."""
    rx, ry = rankdata(x), rankdata(y)
    RZ = np.column_stack([rankdata(z_mat[:, j]) for j in range(z_mat.shape[1])])
    B = basis(RZ)
    ex, ey = resid_ols(B, rx), resid_ols(B, ry)
    return float(np.corrcoef(ex, ey)[0, 1])


def partial_bootstrap(df, xcol, ycol, zcols, n_boot, seed):
    d = df[[xcol, ycol] + zcols + ["position"]].dropna().reset_index(drop=True)
    x = d[xcol].to_numpy()
    y = d[ycol].to_numpy()
    Z = d[zcols].to_numpy()
    pos = d["position"].to_numpy()
    clusters = np.unique(pos)
    idx_by = {c: np.flatnonzero(pos == c) for c in clusters}
    obs = partial_spearman_spline(x, y, Z)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        boot[b] = partial_spearman_spline(x[i], y[i], Z[i])
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    # house convention (scripts.lib.stats._summarize): p = 2*min(frac<=0, frac>=0)
    pv = float(min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0))
    return {"partial_rho": obs, "ci_lo": float(lo), "ci_hi": float(hi),
            "p_boot": pv, "n_rows": len(d), "n_clusters": len(clusters),
            "boot_mean": float(np.nanmean(boot))}


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    base = df.dropna(subset=["delta_esm", "own_e_b", "GI_folinate_independent",
                             "esm2_score", "base_functionality"]).copy()
    print(f"Analysis set: {len(base)} variants, {base['position'].nunique()} positions")
    rows = []

    print("\n" + "=" * 74)
    print("B1a  PARTIAL CORRELATION: delta_ESM vs e.b controlling S(v|WT)+w.fitness")
    print(f"     spline df={SPLINE_DF} on ranks, refit inside each of {N_BOOT} position draws")
    print("=" * 74)
    print("  Raw correlations for reference:")
    for eb in ["own_e_b", "GI_folinate_independent"]:
        r = _spearman(base["delta_esm"], base[eb])
        print(f"    rho(delta, {eb:26s}) = {r:+.4f}")
        rows.append({"stage": "raw", "e_b": eb, "value": r})
    for z in ["esm2_score", "base_functionality", "f_bar_wt"]:
        print(f"    rho(delta, {z:26s}) = {_spearman(base['delta_esm'], base[z]):+.4f}"
              f"   rho(own_e_b, {z:20s}) = {_spearman(base['own_e_b'], base[z]):+.4f}"
              f"   rho(pub_e_b, {z:16s}) = {_spearman(base['GI_folinate_independent'], base[z]):+.4f}")

    for eb in ["own_e_b", "GI_folinate_independent"]:
        for fit in [["esm2_score", "base_functionality"],
                    ["esm2_score", "f_bar_wt"]]:
            res = partial_bootstrap(base, "delta_esm", eb, fit, N_BOOT, SEED)
            raw = _spearman(base["delta_esm"], base[eb])
            ratio = abs(res["partial_rho"]) / abs(raw) if raw != 0 else np.nan
            collapse = ratio < 0.5
            lbl = f"{eb} | ctrl {fit[0]}+{fit[1]}"
            verdict = "COLLAPSE (<50% of raw)" if collapse else "does NOT collapse (>=50% of raw)"
            crosses = res["ci_lo"] < 0 < res["ci_hi"]
            print(f"\n  {lbl}")
            print(f"    raw rho={raw:+.4f}  partial rho={res['partial_rho']:+.4f} "
                  f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}] "
                  f"p_boot={res['p_boot'] if res['p_boot'] else '<'+str(1/N_BOOT)}")
            print(f"    |partial|/|raw| = {ratio:.3f}  -> {verdict}"
                  f"{'  (CI crosses 0)' if crosses else ''}")
            print(f"    boot mean={res['boot_mean']:+.4f}  "
                  f"n={res['n_rows']} positions={res['n_clusters']}")
            rows.append({"stage": "partial", "e_b": eb, "controls": "+".join(fit),
                         "raw": raw, "partial_rho": res["partial_rho"],
                         "ci_lo": res["ci_lo"], "ci_hi": res["ci_hi"],
                         "p_boot": res["p_boot"], "ratio": ratio,
                         "collapse": collapse, "n": res["n_rows"]})

    print("\n" + "=" * 74)
    print("B1b  COMPRESSION: is delta_ESM ≈ -k * S(v|WT)?")
    print("=" * 74)
    r_pb = position_cluster_bootstrap(base, "position", "delta_esm", "esm2_score",
                                      n_boot=N_BOOT, seed=SEED)
    print(f"  Spearman(delta_ESM, S(v|WT)): rho={r_pb['observed_rho']:+.4f} "
          f"CI=[{r_pb['ci_lo']:+.4f},{r_pb['ci_hi']:+.4f}] "
          f"p={r_pb['p_boot'] if r_pb['p_boot'] else '<'+str(1/N_BOOT)} "
          f"n={r_pb['n_rows']}")
    A = base["esm2_score"].to_numpy()
    D = base["delta_esm"].to_numpy()
    b1, a1 = np.polyfit(A, D, 1)
    yhat = a1 + b1 * A
    r2 = 1 - np.sum((D - yhat) ** 2) / np.sum((D - D.mean()) ** 2)
    b0 = float(np.sum(A * D) / np.sum(A * A))          # through-origin slope
    yhat0 = b0 * A
    r20 = 1 - np.sum((D - yhat0) ** 2) / np.sum((D - D.mean()) ** 2)
    print(f"  OLS delta = {a1:+.5f} + {b1:+.5f} * S   R^2={r2:.4f}")
    print(f"  through-origin delta = {b0:+.5f} * S      R^2={r20:.4f}")
    print(f"  compression form predicts negative slope with small intercept:")
    print(f"    slope {b1:+.5f} -> k = {-b1:.5f}; intercept {a1:+.5f}")
    rows.append({"stage": "compression", "slope": b1, "intercept": a1, "r2": r2,
                 "slope_origin": b0, "r2_origin": r20,
                 "spearman": r_pb["observed_rho"],
                 "ci_lo": r_pb["ci_lo"], "ci_hi": r_pb["ci_hi"]})
    base["_sd"] = pd.qcut(base["esm2_score"], 10, labels=False, duplicates="drop")
    print("  Decile means (S(v|WT) -> mean delta_ESM):")
    dec = base.groupby("_sd").agg(n=("delta_esm", "size"),
                                  mean_S=("esm2_score", "mean"),
                                  mean_delta=("delta_esm", "mean"))
    print(dec.round(5).to_string())
    for _, rr in dec.iterrows():
        rows.append({"stage": "decile", "n": rr["n"], "mean_S": rr["mean_S"],
                     "mean_delta": rr["mean_delta"]})

    out = PROC / "task43_flattening.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved to {out}")
    print("\nInterpretation guardrails: collapse under w.fitness control is")
    print("part-whole-consistent (w.fitness sits inside e.b's expectation) —")
    print("stated in the docstring. Nuisance refit per draw; positions are the")
    print("resampling unit throughout (AGENTS.md §3/§4).")
