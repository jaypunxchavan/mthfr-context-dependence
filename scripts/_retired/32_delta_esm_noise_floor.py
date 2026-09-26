"""
Script 32: is delta_ESM above the numerical noise floor?

Prompted by a reviewer correction: the log had claimed the 0.9996 model_A/
model_C correlation was "mathematically necessary," conflating it with the
SEPARATE, genuinely provable Model-B-equals-Model-A-plus-constant result.
The model_A/model_C correlation is empirical (ESM-2's low sensitivity to a
distant single substitution), not forced -- which makes it worth checking
directly whether the small residual (delta_ESM) driving every Task-3 result
is real signal or float-precision noise.

RESULT: sd(delta_ESM) is ~133,000x the float32 rounding floor implied by
eps*mean(|score|); median |delta_ESM| = 0.047; only 0.2% of values fall
below 1e-4. Real signal, not rounding artifact.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

if __name__ == "__main__":
    d = pd.read_csv(PROC / "phase5_analysis_table.csv").dropna(subset=["delta_esm","esm2_score"])
    de, es = d["delta_esm"].to_numpy(), d["esm2_score"].to_numpy()
    eps32 = np.finfo(np.float32).eps
    floor = eps32 * np.abs(es).mean()

    print(f"sd(esm2_score) = {es.std():.6f}   sd(delta_esm) = {de.std():.6f}")
    print(f"ratio sd(delta)/sd(score) = {de.std()/es.std():.4f}")
    print(f"float32 rounding floor ~ eps*mean(|score|) = {floor:.3e}")
    print(f"sd(delta_esm) / floor = {de.std()/floor:.3e}")
    print(f"fraction |delta_esm| < 1e-4: {(np.abs(de)<1e-4).mean():.4f}")
    print(f"median |delta_esm| = {np.median(np.abs(de)):.6f}")

    pd.DataFrame([{"sd_esm2_score": es.std(), "sd_delta_esm": de.std(),
                  "ratio": de.std()/es.std(), "float32_floor": floor,
                  "sd_over_floor": de.std()/floor,
                  "frac_below_1e4": (np.abs(de)<1e-4).mean(),
                  "median_abs_delta": np.median(np.abs(de))}]).to_csv(
        PROC / "task_delta_esm_noise_floor.csv", index=False)
    print(f"\nSaved to task_delta_esm_noise_floor.csv")
