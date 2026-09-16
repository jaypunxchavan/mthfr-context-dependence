"""
Subtask C: Precision filtering (proposal 5.6a).

Uses the per-variant uncertainty that has been available since the first
data audit but never applied: the se columns on every condition, and the
atlas's own posterior probabilities (e.post.b / e.post.r) that a variant
genuinely interacts.

If the Phase 3 associations are driven by imprecisely-measured variants
rather than real signal, restricting to high-confidence variants should
weaken or remove them.

Region check is NOT included: the four mutagenesis regions' residue
boundaries are not published in the paper, the GitHub repository, or any
released data file. Guessing them from tile counts would risk either
masking a real artifact or manufacturing a fake one. Disclosed limitation.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import os
import numpy as np, pandas as pd
from scripts.lib.io import CONDITION_COLS, load_derived_maps
from scripts.lib.stats import position_cluster_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 10000))
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
SE_COLS = ["w12.se", "w25.se", "w100.se", "w200.se",
           "m12.se", "m25.se", "m100.se", "m200.se"]
CONTEXT = [("folinate_response", "GI_indep_post"),
           ("GI_folinate_independent", "GI_indep_post"),
           ("GI_folinate_dependent", "GI_dep_post")]


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase3_analysis_table.csv")
    d = load_derived_maps()[["hgvs"] + SE_COLS].rename(columns={"hgvs": "hgvs_pro"})
    df = df.merge(d, on="hgvs_pro", how="left")
    df["mean_se"] = df[SE_COLS].mean(axis=1, skipna=True)
    print(f"{len(df)} variants; mean se available for {df['mean_se'].notna().sum()}")
    print(f"mean se quartiles: {df['mean_se'].quantile([.25,.5,.75]).round(4).to_dict()}")

    rows = []
    for err_col, err_lbl in [("central_error_rank", "rank-based"),
                             ("central_error_cal", "calibrated")]:
        for ctx_col, post_col in CONTEXT:
            df["_ctx"] = df[ctx_col].abs()
            sets = [("all variants", df)]
            thr = df["mean_se"].quantile(0.5)
            sets.append((f"precise half (se<{thr:.3f})", df[df["mean_se"] < thr]))
            if post_col in df.columns:
                sets.append((f"{post_col}>0.95", df[df[post_col] > 0.95]))

            print(f"\n{err_lbl} error vs |{ctx_col}|")
            for lbl, sub in sets:
                if len(sub) < 200:
                    print(f"  {lbl:28s} SKIPPED (n={len(sub)} too small)")
                    continue
                r = position_cluster_bootstrap(sub, "position", "_ctx", err_col,
                                               n_boot=N_BOOT, seed=0)
                crosses = r["ci_lo"] < 0 < r["ci_hi"]
                print(f"  {lbl:28s} n={r['n_rows']:5d} rho={r['observed_rho']:+.4f} "
                      f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'])}"
                      f" {'(crosses 0)' if crosses else ''}")
                rows.append({"error_metric": err_lbl, "context_metric": ctx_col,
                             "subset": lbl, "n": r["n_rows"], "rho": r["observed_rho"],
                             "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
                             "p_boot": r["p_boot"], "ci_includes_zero": crosses})

    pd.DataFrame(rows).to_csv(PROC / "tier2_precision_checks.csv", index=False)
    print(f"\nSaved to {PROC / 'tier2_precision_checks.csv'}")
