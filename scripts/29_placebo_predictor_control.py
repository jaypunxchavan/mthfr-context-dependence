"""
Script 29: Placebo-predictor control for the accuracy-degradation finding.

WHY THIS IS NEEDED
------------------
abs_gi = |e.b| is, by construction, the magnitude of the residual of the
A222V arm from an expectation built out of the WT arm:

    expected(c) = (b_v + c*r_v) * (b_A222V + c*r_A222V)      <- WT-arm fit
    e_b         = weighted mean_c [ m_score(c) - expected(c) ]
    target      = f_bar_a222v = mean_c m_score(c)

so  |e_b| ~ |target - (something derived from the WT arm)|.

ESM-2 is a predictor of a variant's general functional effect, which is
essentially what the WT arm measures (and model_C ~ model_A, since delta_ESM
is small). Therefore ANY WT-informed predictor must correlate less well with
`target` inside high-|e_b| strata -- not because the predictor fails on
epistasis, but because high |e_b| SELECTS variants whose target deviates from
what the WT arm implies.

Controlling for f_bar_a222v (script 24, step 1c) does NOT remove this: the
mechanism runs through (target - expected), not through the level of target.

THE TEST
--------
Re-run the identical stratified comparison with predictors that are not
ESM-2 and contain no model at all. If they degrade as steeply, the pattern
belongs to the stratification variable, not to ESM-2.

  placebo_wt_mean   f_bar_wt   (the WT arm's own measured mean)
  placebo_wfitness  w.fitness  (the atlas's own base-functionality fit)
  model_C           ESM-2, A222V background      <- the actual claim
  model_A           ESM-2, WT background

READING THE OUTPUT
------------------
  * If model_C's drop is within the placebos' range -> the degradation is a
    property of how abs_gi is defined. Finding #4 does not support a claim
    about ESM-2 specifically.
  * If model_C drops MEANINGFULLY MORE than both placebos -> that excess is
    the real, attributable effect, and it is the number to report.
    The excess, not the raw 0.53 -> 0.17, is the finding.

The difference-in-degradation is bootstrapped by position so the comparison
carries an interval rather than being eyeballed.
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scripts.lib.io import load_derived_maps, WT_COND_COLS
from scripts.lib.stats import _spearman

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def strat_rhos(d, pred_col, gi_col="abs_gi", target_col="target", n=3):
    """rho(pred, target) within each |GI| stratum, low -> high."""
    s = d.dropna(subset=[pred_col, gi_col, target_col])
    cuts = np.quantile(s[gi_col], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s[gi_col], cuts)
    return [_spearman(s[pred_col].to_numpy()[k == i],
                      s[target_col].to_numpy()[k == i]) for i in range(n)]


def degradation(d, pred_col):
    """high-stratum rho minus low-stratum rho (negative = degrades)."""
    r = strat_rhos(d, pred_col)
    return r[-1] - r[0], r


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()

    # placebo predictors: measured data only, no model anywhere
    derived = load_derived_maps()
    df = df.merge(
        pd.DataFrame({
            "hgvs_pro": derived["hgvs"],
            "placebo_wfitness": derived["w.fitness"],
            "placebo_wt_mean": derived[WT_COND_COLS].mean(axis=1, skipna=True),
        }), on="hgvs_pro", how="left")

    PREDS = [("model_C", "ESM-2 (A222V bg)  [the claim]"),
             ("model_A", "ESM-2 (WT bg)"),
             ("placebo_wt_mean", "PLACEBO: WT-arm measured mean"),
             ("placebo_wfitness", "PLACEBO: atlas w.fitness")]

    print("=" * 78)
    print("STRATIFIED rho(predictor, target) BY |e.b| TERCILE")
    print("=" * 78)
    obs = {}
    for col, lbl in PREDS:
        if col not in df.columns or df[col].notna().sum() == 0:
            print(f"  {lbl:34s} -- column missing, skipped")
            continue
        drop, r = degradation(df, col)
        obs[col] = drop
        pct = 100 * (1 - r[-1] / r[0]) if r[0] != 0 else np.nan
        print(f"  {lbl:34s} {r[0]:+.4f} -> {r[1]:+.4f} -> {r[2]:+.4f}"
              f"   drop={drop:+.4f} ({pct:.0f}%)")

    print("\n" + "=" * 78)
    print(f"IS ESM-2'S DEGRADATION LARGER THAN A PLACEBO'S? "
          f"(position cluster bootstrap, {N_BOOT})")
    print("=" * 78)
    rng = np.random.default_rng(SEED)
    d = df.dropna(subset=["model_C", "abs_gi", "target"]).reset_index(drop=True)
    positions = d["position"].unique()
    rows_by_pos = {p: d.index[d["position"] == p].to_numpy() for p in positions}

    for placebo, lbl in [("placebo_wt_mean", "WT-arm measured mean"),
                         ("placebo_wfitness", "atlas w.fitness")]:
        if placebo not in d.columns or d[placebo].notna().sum() == 0:
            continue
        sub = d.dropna(subset=[placebo]).reset_index(drop=True)
        rbp = {p: sub.index[sub["position"] == p].to_numpy()
               for p in sub["position"].unique()}
        clusters = np.array(list(rbp.keys()))
        point = degradation(sub, "model_C")[0] - degradation(sub, placebo)[0]

        boot = np.empty(N_BOOT)
        for b in range(N_BOOT):
            drawn = rng.choice(clusters, size=len(clusters), replace=True)
            idx = np.concatenate([rbp[c] for c in drawn])
            bs = sub.iloc[idx]
            boot[b] = degradation(bs, "model_C")[0] - degradation(bs, placebo)[0]
        lo, hi = np.nanpercentile(boot, [2.5, 97.5])
        verdict = ("ESM-2 degrades MORE than placebo -- real excess"
                   if hi < 0 else
                   "ESM-2 degrades LESS than placebo" if lo > 0 else
                   "INDISTINGUISHABLE from placebo -- finding is mechanical")
        print(f"  vs {lbl:24s} diff={point:+.4f} CI=[{lo:+.4f},{hi:+.4f}]")
        print(f"     -> {verdict}")

    print("\nNote: 'diff' is (ESM-2 degradation) - (placebo degradation).")
    print("More negative = ESM-2 falls off faster than a pure measurement does.")
