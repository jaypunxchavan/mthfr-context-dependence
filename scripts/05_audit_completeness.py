"""
Step 5: Completeness audit.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.io import load_primary_maps

if __name__ == "__main__":
    df = load_primary_maps()

    n_cells = df.groupby("hgvs_pro").apply(
        lambda g: g[["background", "folinate_ugml"]].drop_duplicates().shape[0]
    )

    complete = (n_cells == 8).sum()
    total = n_cells.shape[0]

    print(f"Total distinct variants across primary maps: {total}")
    print(f"Variants with all 8 background x concentration cells present: {complete}")
    print(f"Variants missing at least one cell: {total - complete}")
    print()
    print("Distribution of cell-count per variant:")
    print(n_cells.value_counts().sort_index())

    nan_scores = df["score"].isna().sum()
    print(f"\nRows with NaN score (cell present but no value): {nan_scores}")

