"""
Script 39: formal range-restriction correction on the tercile trajectories.

Stratifying by |e.b| restricts the TARGET's variance within each stratum
(confirmed directly -- earlier diagnostics showed target IQR narrows in
the mid stratum). Spearman correlation is mechanically sensitive to this
even under a perfectly stable, homoscedastic underlying relationship,
independent of anything about wild-type-informedness -- a genuinely
distinct mechanism from the circularity concern scripts 29-38 test.

METHOD, AND ITS EXPLICIT LIMITATION: applies the standard Thorndike Case
II range-restriction correction --

    r_corrected = r * (SD_full/SD_stratum) /
                  sqrt(1 - r^2 + r^2 * (SD_full/SD_stratum)^2)

-- to each stratum's Spearman rho, using that stratum's target SD against
the full-sample target SD. This formula is DERIVED for Pearson correlations
under bivariate normality. Applying it to Spearman rank correlations is an
approximation, not exact, and is reported as such throughout -- corrected
values here are diagnostic (does the DIRECTION of degradation survive),
not a replacement for the permutation-based inference used everywhere
else in this project.

If corrected correlations converge across strata, the apparent
"degradation" is substantially arithmetic (range restriction), not
biological. If a real decline survives correction, that argues for
something beyond range restriction.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scripts.lib.io import load_insilico_predictors, load_derived_maps, WT_COND_COLS
from scripts.lib.stats import _spearman

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def thorndike_correct(r, sd_full, sd_restricted):
    """Case II range-restriction correction. r, sd_restricted from the
    restricted (stratum) sample; sd_full from the unrestricted (full) sample."""
    if sd_restricted == 0 or np.isnan(r):
        return np.nan
    ratio = sd_full / sd_restricted
    denom = 1 - r**2 + (r**2) * (ratio**2)
    if denom <= 0:
        return np.nan
    return r * ratio / np.sqrt(denom)


def strat_with_sd(d, pred, n=3):
    s = d.dropna(subset=[pred, "abs_gi", "target"])
    cuts = np.quantile(s["abs_gi"], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s["abs_gi"], cuts)
    sd_full = s["target"].std()
    out = []
    for i in range(n):
        sub = s[k == i]
        r = _spearman(sub[pred], sub["target"])
        sd_i = sub["target"].std()
        r_corr = thorndike_correct(r, sd_full, sd_i)
        out.append({"stratum": i, "n": len(sub), "raw_rho": r, "sd_ratio": sd_full/sd_i,
                   "corrected_rho": r_corr})
    return out


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    ins = load_insilico_predictors()
    df = df.merge(ins.rename(columns={"pos": "position", "ref": "wt_aa", "alt": "mut_aa"}),
                 on=["position", "wt_aa", "mut_aa"], how="left")
    df["pp2div_flip"] = -df["pp2div"]; df["pp2var_flip"] = -df["pp2var"]

    PREDS = [("model_C", "ESM-2"), ("provean", "PROVEAN"), ("sift", "SIFT"),
             ("pp2div_flip", "PolyPhen-2 HumDiv"), ("pp2var_flip", "PolyPhen-2 HumVar")]

    print("=" * 84)
    print("RANGE-RESTRICTION-CORRECTED TERCILE TRAJECTORIES")
    print("(correction is a Pearson-derived approximation applied to Spearman rho --")
    print(" diagnostic for direction/magnitude, not a substitute for permutation inference)")
    print("=" * 84)

    rows = []
    for col, lbl in PREDS:
        res = strat_with_sd(df, col)
        raw = [r["raw_rho"] for r in res]
        corr = [r["corrected_rho"] for r in res]
        raw_drop = raw[2] - raw[0]
        corr_drop = corr[2] - corr[0] if not any(np.isnan(corr)) else np.nan
        print(f"\n{lbl}:")
        print(f"  raw:       {raw[0]:+.4f} -> {raw[1]:+.4f} -> {raw[2]:+.4f}   drop={raw_drop:+.4f}")
        print(f"  corrected: {corr[0]:+.4f} -> {corr[1]:+.4f} -> {corr[2]:+.4f}   "
              f"drop={corr_drop:+.4f}" if not np.isnan(corr_drop) else "  corrected: undefined")
        print(f"  SD ratios (full/stratum): "
              f"{[f'{r['sd_ratio']:.3f}' for r in res]}")
        for i, r in enumerate(res):
            rows.append({"predictor": col, "label": lbl, "stratum": i, "n": r["n"],
                        "raw_rho": r["raw_rho"], "sd_ratio": r["sd_ratio"],
                        "corrected_rho": r["corrected_rho"]})

    out = pd.DataFrame(rows)
    out.to_csv(PROC / "task_range_restriction_correction.csv", index=False)

    print(f"\n{'='*84}")
    print("SUMMARY: raw drop vs corrected drop, all predictors")
    print("=" * 84)
    summary = []
    for col, lbl in PREDS:
        sub = out[out.predictor == col].sort_values("stratum")
        raw_drop = sub.iloc[2]["raw_rho"] - sub.iloc[0]["raw_rho"]
        corr_drop = sub.iloc[2]["corrected_rho"] - sub.iloc[0]["corrected_rho"]
        pct_explained = 100 * (1 - corr_drop/raw_drop) if raw_drop != 0 and not np.isnan(corr_drop) else np.nan
        print(f"  {lbl:20s} raw_drop={raw_drop:+.4f}  corrected_drop={corr_drop:+.4f}  "
              f"({pct_explained:.0f}% of raw drop explained by range restriction)"
              if not np.isnan(pct_explained) else f"  {lbl:20s} correction undefined")
        summary.append({"predictor": col, "label": lbl, "raw_drop": raw_drop,
                       "corrected_drop": corr_drop, "pct_explained_by_range_restriction": pct_explained})
    pd.DataFrame(summary).to_csv(PROC / "task_range_restriction_summary.csv", index=False)
    print(f"\nSaved to task_range_restriction_correction.csv and task_range_restriction_summary.csv")
