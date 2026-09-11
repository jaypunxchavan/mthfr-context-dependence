"""Step 6: Merge structural covariates by position. Logic lives in lib/io.py.

Spot-check 5-10 positions by hand after merging to confirm the join key
isn't off by one.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.io import load_structural_features

if __name__ == "__main__":
    df = load_structural_features()
    print(df["Domain"].value_counts())
