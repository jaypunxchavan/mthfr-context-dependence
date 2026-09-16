"""
Region-stratified check (proposal 5.6b), previously disclosed as impossible.

Region boundaries obtained by direct query to the atlas's co-authors (see
scripts/lib/regions.py for provenance and cross-validation). Scores from
each region were rescaled independently by the original authors before
being combined into one map -- exactly the kind of artifact this check
exists to catch.

Applied to the two results still standing after Task 1 and Tier 2:
  1. |GI_folinate_independent| vs central error (survived the sign-flip
     null, but 77-82% of its raw magnitude was structural artifact)
  2. The same relationship after the multivariable controls

If one region drives either result, pooling was hiding a region-specific
artifact rather than a real, distributed effect.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import position_cluster_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase3_analysis_table.csv")
    df["region"] = assign_region(df["position"])
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    print(f"{len(df)} variants; region assignment: "
          f"{df['region'].value_counts(dropna=False).sort_index().to_dict()}")

    rows = []
    for err_col, err_lbl in [("central_error_rank", "rank-based"),
                             ("central_error_cal", "calibrated")]:
        print(f"\n{'='*72}\n|GI_folinate_independent| vs {err_lbl} central error, by region\n{'='*72}")
        pooled = position_cluster_bootstrap(df, "position", "abs_gi", err_col,
                                            n_boot=N_BOOT, seed=SEED)
        print(f"  {'pooled':10s} n={pooled['n_rows']:5d} pos={pooled['n_clusters']:3d} "
              f"rho={pooled['observed_rho']:+.4f} "
              f"CI=[{pooled['ci_lo']:+.4f},{pooled['ci_hi']:+.4f}] p={pstr(pooled['p_boot'])}")
        rows.append({"error_metric": err_lbl, "region": "pooled", **pooled,
                     "ci_includes_zero": pooled["ci_lo"] < 0 < pooled["ci_hi"]})
        for r in sorted(REGION_BOUNDS):
            sub = df[df["region"] == r]
            if sub["position"].nunique() < 30:
                print(f"  region {r:<3d}  SKIPPED (only {sub['position'].nunique()} positions)")
                continue
            res = position_cluster_bootstrap(sub, "position", "abs_gi", err_col,
                                             n_boot=N_BOOT, seed=SEED)
            lo, hi = REGION_BOUNDS[r]
            crosses = res["ci_lo"] < 0 < res["ci_hi"]
            agrees = not (res["ci_hi"] < pooled["ci_lo"] or res["ci_lo"] > pooled["ci_hi"])
            print(f"  region {r} ({lo}-{hi}) n={res['n_rows']:5d} pos={res['n_clusters']:3d} "
                  f"rho={res['observed_rho']:+.4f} "
                  f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}] p={pstr(res['p_boot'])}"
                  f"{'  (crosses 0)' if crosses else ''}"
                  f"{'' if agrees else '  <-- CI does not overlap pooled'}")
            rows.append({"error_metric": err_lbl, "region": f"region_{r}", **res,
                         "ci_includes_zero": crosses, "overlaps_pooled": agrees})

    out = pd.DataFrame(rows)
    out.to_csv(PROC / "task_region_check.csv", index=False)

    no_overlap = out[out.get("overlaps_pooled") == False]
    print(f"\n{'='*72}")
    if len(no_overlap):
        print(f"{len(no_overlap)} region(s) have a CI that does not overlap the pooled result --")
        print("possible region-specific artifact, listed above.")
    else:
        print("Every region's CI overlaps the pooled estimate. No single region is driving")
        print("the result; pooling does not appear to be hiding a rescaling artifact.")
    print(f"{'='*72}")
    print(f"\nSaved to {PROC / 'task_region_check.csv'}")
