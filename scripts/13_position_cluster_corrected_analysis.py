"""
Step 13: Position-cluster-corrected re-analysis.

Redoes four relationships originally computed treating each substitution
row as independent, which overstates significance whenever rows share a
position. Cluster bootstrap resamples POSITIONS, not rows.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from scipy import stats as scipy_stats
from scripts.lib.stats import position_cluster_bootstrap

N_BOOT = 10000
SEED = 0

if __name__ == "__main__":
    merged = pd.read_csv("data/processed/merged_wt_a222v_scores.csv")
    assert (merged["position_wt"] == merged["position_a222v_bg"]).all()
    merged["position"] = merged["position_wt"]
    merged["distance_from_222"] = (merged["position"] - 222).abs()

    derived = pd.read_csv("data/raw/mthfrModel/results/folate_response_model5.csv")
    derived = derived[derived["type"] == "substitution"].copy()

    combined = merged.merge(derived[["hgvs", "e.b"]], left_on="hgvs_pro", right_on="hgvs", how="inner")
    before = len(combined)
    combined = combined.dropna(subset=["e.b"])
    print(f"Combined: {len(combined)} rows (dropped {before - len(combined)} with missing e.b), "
          f"{combined['position'].nunique()} distinct positions")

    combined["abs_delta_esm"] = combined["delta_esm"].abs()
    combined["abs_eb"] = combined["e.b"].abs()

    print(f"\nRunning cluster bootstrap: n_boot={N_BOOT}, seed={SEED}\n")

    relationships = [
        ("WT-bg score vs A222V-bg score", merged, "esm2_score", "esm2_score_a222v_bg"),
        ("|delta_ESM| vs distance from 222", combined, "abs_delta_esm", "distance_from_222"),
        ("|e.b| vs distance from 222", combined, "abs_eb", "distance_from_222"),
        ("|delta_ESM| vs |e.b|  (headline)", combined, "abs_delta_esm", "abs_eb"),
    ]

    rows = []
    for name, df, xcol, ycol in relationships:
        naive_rho, naive_p = scipy_stats.spearmanr(df[xcol], df[ycol])
        result = position_cluster_bootstrap(df, "position", xcol, ycol, n_boot=N_BOOT, seed=SEED)

        print(f"{name}")
        print(f"  naive (n={len(df)} rows, treated as independent):     "
              f"rho={naive_rho:.4f}  p={naive_p:.2e}")
        print(f"  cluster bootstrap (n={result['n_clusters']} positions): "
              f"rho={result['observed_rho']:.4f}  "
              f"95% CI=[{result['ci_lo']:.4f}, {result['ci_hi']:.4f}]  "
              f"p={result['p_boot']:.4f}")
        crosses_zero = result['ci_lo'] < 0 < result['ci_hi']
        print(f"  -> CI {'INCLUDES' if crosses_zero else 'excludes'} zero "
              f"{'(naive significance likely overstated)' if crosses_zero else '(survives clustering correction)'}")
        print()

        rows.append({
            "relationship": name, "n_rows": len(df), "n_positions": result["n_clusters"],
            "naive_rho": naive_rho, "naive_p": naive_p,
            "cluster_rho": result["observed_rho"],
            "cluster_ci_lo": result["ci_lo"], "cluster_ci_hi": result["ci_hi"],
            "cluster_p": result["p_boot"],
        })

    out = pd.DataFrame(rows)
    out_path = Path("data/processed/position_cluster_corrected_results.csv")
    out.to_csv(out_path, index=False)
    print(f"Saved summary table to {out_path}")
