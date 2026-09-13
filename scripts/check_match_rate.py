import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

scored = pd.read_csv("data/processed/esm2_wt_scores.csv")
atlas = pd.read_csv("data/raw/mthfrModel/map_data/WT25.csv")

atlas_missense = {v for v in atlas["hgvs_pro"] if "=" not in str(v) and "Ter" not in str(v)}
matched = len(atlas_missense & set(scored["hgvs_pro"]))

print(f"Atlas missense variants: {len(atlas_missense)}")
print(f"Found in scored table: {matched}")
print(f"Match rate: {100*matched/len(atlas_missense):.1f}%")
