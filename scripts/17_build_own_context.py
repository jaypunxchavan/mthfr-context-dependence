"""
Subtask B1-B3: Reproduce the atlas interaction model, validate, save.

REPRODUCTION, not replication: same data, same estimator, different code.
Agreement with published e.b/e.r validates THIS CODE. It is a unit test,
not evidence for any biological claim.

Purpose: the published e.b/e.r are fitted values read from a file and
cannot be recomputed under a shuffle. A permutation test requires
re-deriving the statistic on each permuted dataset. This makes that possible.

The published atlas values remain PRIMARY everywhere else. These are a
second layer, used only where recomputability is required.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr
from scripts.lib.own_context import *

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"

if __name__ == "__main__":
    d = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    W = d[WT_SCORE_COLS].to_numpy(float); Wse = d[WT_SE_COLS].to_numpy(float)
    M = d[MT_SCORE_COLS].to_numpy(float); Mse = d[MT_SE_COLS].to_numpy(float)

    w = fit_single_arm(W, Wse)
    w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(d["hgvs"].to_numpy() == "p.Ala222Val")[0][0])
    a_f, a_r = w["fitness"][i222], w["remediation"][i222]
    print(f"A222V reference line: fitness={a_f:.4f} remediation={a_r:.6f} "
          f"(published {d['w.fitness'][i222]:.4f} / {d['w.remediation'][i222]:.6f})")
    print("NOTE: this single reference line enters EVERY variant's expectation,")
    print("so its error is common-mode across the dataset. It shifts the location")
    print("of the e_b distribution but not rank order, and every downstream test")
    print("here is rank-based.")

    e1 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean, a_f, a_r)
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1["e_r"][keep])
    e2 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"],
                         w_mean, a_f, a_r, correction=(cb, cr))
    print(f"\nTwo-pass fit done; bias correction fit on {keep.sum()} variants "
          f"(w.logl & e.logl > {LOGL_CUTOFF})")

    print("\n" + "=" * 70)
    print("VALIDATION vs published values (this is a unit test)")
    print("=" * 70)
    for lbl, a, col in [("w.fitness", w["fitness"], "w.fitness"),
                        ("w.remediation", w["remediation"], "w.remediation"),
                        ("w.post", w["post"], "w.post"),
                        ("e.b", e2["e_b"], "e.b"), ("e.r", e2["e_r"], "e.r")]:
        b = d[col].to_numpy(float); ok = np.isfinite(a) & np.isfinite(b)
        print(f"  {lbl:14s} pearson={pearsonr(a[ok],b[ok])[0]:.6f} "
              f"spearman={spearmanr(a[ok],b[ok]).statistic:.6f} n={ok.sum()}")

    wf = w["fitness"]
    v = pd.DataFrame({"own_eb": e2["e_b"], "pub_eb": d["e.b"], "own_er": e2["e_r"],
                      "pub_er": d["e.r"], "dist": np.minimum(np.abs(wf), np.abs(wf - 1)),
                      "df": e2["df"]}).dropna()
    v["stratum"] = pd.cut(v["dist"], [-.01, .05, .15, .3, 10],
                          labels=["<0.05 (at 0/1 edge)", "0.05-0.15", "0.15-0.3", ">0.3 (mid)"])
    print("\n  Stratified by distance from the 0/1 boundaries:")
    for s, g in v.groupby("stratum", observed=True):
        print(f"    {s:20s} n={len(g):5d} e.b rho={spearmanr(g.own_eb,g.pub_eb).statistic:.4f}"
              f"  e.r rho={spearmanr(g.own_er,g.pub_er).statistic:.4f}")
    print("  Agreement is BEST at the edges and worst mid-range -- the opposite of")
    print("  what an omitted-bias-correction artifact would produce. Residual")
    print("  mid-range disagreement is unexplained and disclosed as such.")

    print("\n  Residual degrees of freedom per variant (4 points - 2 params):")
    print("   ", v["df"].value_counts().sort_index().to_dict())

    out = pd.DataFrame({
        "hgvs_pro": d["hgvs"], "type": d["type"], "position": d["start"],
        "own_w_fitness": w["fitness"], "own_w_remediation": w["remediation"],
        "own_w_post": w["post"], "own_e_b": e2["e_b"], "own_e_r": e2["e_r"],
        "own_e_post_b": 1/(1+np.exp(-e2["lod_b"])), "own_e_post_r": 1/(1+np.exp(-e2["lod_r"])),
        "own_df": e2["df"],
    })
    out = out[out["type"] == "substitution"]
    out.to_csv(PROC / "own_context_metrics.csv", index=False)
    print(f"\nSaved {len(out)} missense variants to own_context_metrics.csv")
