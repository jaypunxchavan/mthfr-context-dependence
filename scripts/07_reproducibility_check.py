"""Step 7: PolyPhen-2 / SIFT / PROVEAN reproducibility check.
Logic lives in lib/validate.py and lib/io.py.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.io import load_pathogenicity_llrs, load_insilico_predictors
from scripts.lib.validate import reproducibility_check

if __name__ == "__main__":
    llr_df = load_pathogenicity_llrs()
    insilico_df = load_insilico_predictors()
    results = reproducibility_check(llr_df, insilico_df)
    for pred, r in results.items():
        print(f"{pred:10s}: rho = {r['rho']:+.3f}  (p = {r['p']:.2e}, n = {r['n']})")
