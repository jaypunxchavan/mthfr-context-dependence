"""Step 3: Load and merge the eight primary maps. Logic lives in lib/io.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.io import load_primary_maps

if __name__ == "__main__":
    df = load_primary_maps()
    print(df.shape)
    print(df.head())
    df.to_csv(Path(__file__).resolve().parents[1] / "data" / "processed" / "primary_maps.csv", index=False)
