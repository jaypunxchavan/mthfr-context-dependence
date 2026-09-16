"""
Task 1 / Phase 2: Build the clean context-metrics table.

Pulls the three published context measures into one table with explicit
names, alongside position and base functionality. Everything downstream
(Tasks 2 and 3) reads from this.

Context classes (proposal section 3.3):
  folinate_response       (w.remediation) -> environment-dependent
  GI_folinate_independent (e.b)           -> sequence-encoded genetic
  GI_folinate_dependent   (e.r)           -> both simultaneously
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from scripts.lib.io import load_derived_maps, CONDITION_COLS

OUT = Path(__file__).resolve().parents[1] / "data" / "processed" / "context_metrics.csv"

if __name__ == "__main__":
    d = load_derived_maps()  # missense-only by default now
    print(f"Loaded {len(d)} missense variants")

    ctx = pd.DataFrame({
        "hgvs_pro": d["hgvs"],
        "position": d["start"],
        "wt_aa": d["ancestral"],
        "mut_aa": d["variant"],
        "base_functionality": d["w.fitness"],
        "folinate_response": d["w.remediation"],
        "GI_folinate_independent": d["e.b"],
        "GI_folinate_dependent": d["e.r"],
        # significance / confidence companions
        "folinate_response_lod": d["w.lod"],
        "folinate_response_post": d["w.post"],
        "GI_indep_lod": d["e.lod.b"],
        "GI_indep_post": d["e.post.b"],
        "GI_dep_lod": d["e.lod.r"],
        "GI_dep_post": d["e.post.r"],
    })
    for c in CONDITION_COLS:
        ctx[c] = d[c]

    print("\nNon-missing counts for the three primary context metrics:")
    for c in ["folinate_response", "GI_folinate_independent", "GI_folinate_dependent"]:
        print(f"  {c:26s}: {ctx[c].notna().sum():6d} / {len(ctx)}")

    print("\nDistributions (non-missing only):")
    print(ctx[["base_functionality", "folinate_response",
               "GI_folinate_independent", "GI_folinate_dependent"]].describe().to_string())

    n_all8 = ctx[CONDITION_COLS].notna().all(axis=1).sum()
    n_any = ctx[CONDITION_COLS].notna().any(axis=1).sum()
    print(f"\nCondition coverage: {n_all8} variants with all 8, {n_any} with >=1")
    print(f"Distinct positions: {ctx['position'].nunique()}")

    ctx.to_csv(OUT, index=False)
    print(f"\nSaved to {OUT}")
