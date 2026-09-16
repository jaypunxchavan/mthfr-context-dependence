"""Step 12: Validate A222V-background scores against WT scores and atlas."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from scipy import stats

wt = pd.read_csv("data/processed/esm2_wt_scores.csv")
a222v = pd.read_csv("data/processed/esm2_a222v_bg_scores.csv")

print(f"WT rows: {len(wt)}, A222V-bg rows: {len(a222v)}")

none_hgvs = a222v["hgvs_pro"].isna().sum()
print(f"Rows with hgvs_pro=None (should be exactly 19, for position 222): {none_hgvs}")

merged = wt.merge(
    a222v[a222v["hgvs_pro"].notna()],
    on="hgvs_pro", suffixes=("_wt", "_a222v_bg")
)
print(f"\nMerged on hgvs_pro: {len(merged)} rows (expect 12445 - 19 = 12426)")

rho, p = stats.spearmanr(merged["esm2_score"], merged["esm2_score_a222v_bg"])
print(f"\nSpearman correlation, WT-background score vs A222V-background score: "
      f"rho = {rho:.4f} (p = {p:.2e})")
print("Expected: strongly positive (most mutations similarly damaging regardless")
print("of background) but NOT 1.0 -- the departure from perfect correlation is")
print("exactly the epistasis signal Phase 5 is testing for.")

merged["delta_esm"] = merged["esm2_score_a222v_bg"] - merged["esm2_score"]
print(f"\ndelta_ESM = S(v|A222V) - S(v|WT), summary:")
print(merged["delta_esm"].describe())

out_path = Path("data/processed/merged_wt_a222v_scores.csv")
merged.to_csv(out_path, index=False)
print(f"\nSaved merged table to {out_path}")
