"""
Position-grouped, region-stratified confirmation split.

Positions (not variants) are the split unit throughout this project, since
variants at one position aren't independent. Splitting by region matters
specifically because region 2 has already been shown to behave differently
in a real, mechanistic way (100% catalytic domain, distinct fitness range).
An unstratified split risks loading one half with most of region 2 by
chance, making a weaker confirmation-set result ambiguous between "the
effect doesn't replicate" and "unlucky split."

This is StratifiedGroupKFold's pattern (group=position, stratum=region)
specialized to a single 50/50 split rather than k folds.

Region is a fixed, a priori label from the original paper's co-authors,
independent of anything ESM-2 or the interaction statistic produced --
stratifying on it is not outcome-informed leakage, the same distinction
that separates stratifying by trial site from stratifying by treatment
response.
"""
import numpy as np
import pandas as pd
from scripts.lib.regions import assign_region, REGION_BOUNDS


def stratified_position_split(df, position_col="position", gi_col="abs_gi",
                              frac=0.5, seed=0, n_gi_bins=3):
    """Split by position, jointly stratified on region AND per-position GI
    strength. Region-only stratification was tested and found to leave
    abs_gi -- the central variable in every downstream test -- imbalanced
    between halves (KS p=8.6e-4 on the first attempt), which would make a
    weaker confirmation-set result ambiguous between "doesn't replicate"
    and "unlucky split on the thing being tested." Joint region x GI-tercile
    strata fix this at the source rather than relying on a favorable seed.
    """
    rng = np.random.default_rng(seed)
    pos_summary = df.groupby(position_col).agg(
        region_pos=(position_col, "first"),
        gi_summary=(gi_col, "median"),
    )
    pos_summary["region"] = assign_region(pos_summary["region_pos"])
    pos_summary["gi_bin"] = pos_summary.groupby("region")["gi_summary"].transform(
        lambda x: pd.qcut(x, n_gi_bins, labels=False, duplicates="drop"))

    explore_positions, confirm_positions = [], []
    for (r, g), sub in pos_summary.groupby(["region", "gi_bin"]):
        positions = sub.index.to_numpy()
        shuffled = rng.permutation(positions)
        cut = int(round(len(shuffled) * frac))
        explore_positions.extend(shuffled[:cut])
        confirm_positions.extend(shuffled[cut:])

    explore_positions = set(explore_positions)
    confirm_positions = set(confirm_positions)
    explore_mask = df[position_col].isin(explore_positions)
    confirm_mask = df[position_col].isin(confirm_positions)
    return explore_mask, confirm_mask


def split_balance_report(df, explore_mask, confirm_mask, position_col="position"):
    """Balance checks: region counts in both halves, and distribution balance
    on other known covariates (severity, GI strength, burial) not explicitly
    stratified for."""
    d = df.copy()
    d["region"] = assign_region(d[position_col])
    rows = []

    for r in sorted(REGION_BOUNDS):
        e_pos = d.loc[explore_mask & (d.region == r), position_col].nunique()
        c_pos = d.loc[confirm_mask & (d.region == r), position_col].nunique()
        rows.append({"check": "region_position_count", "group": f"region_{r}",
                     "explore": e_pos, "confirm": c_pos,
                     "usable": min(e_pos, c_pos) >= 10})

    for col in ["grantham", "blosum62", "rsa", "abs_gi"]:
        if col not in d.columns:
            continue
        e = d.loc[explore_mask, col].dropna()
        c = d.loc[confirm_mask, col].dropna()
        if len(e) == 0 or len(c) == 0:
            continue
        from scipy.stats import ks_2samp
        stat, p = ks_2samp(e, c)
        rows.append({"check": "covariate_ks_test", "group": col,
                     "explore": e.mean(), "confirm": c.mean(),
                     "ks_stat": stat, "ks_p": p, "balanced": p > 0.05})

    return pd.DataFrame(rows)
