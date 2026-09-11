"""Step 4: Load derived context metrics. Logic lives in lib/io.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.io import load_derived_maps

if __name__ == "__main__":
    df = load_derived_maps()
    print(df.shape)
    print(df[["hgvs", "w.remediation", "e.b", "e.r"]].head())
    df.to_csv(Path(__file__).resolve().parents[1] / "data" / "processed" / "derived_maps.csv", index=False)
