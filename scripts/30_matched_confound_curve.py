"""
Script 30: Matched-confound curve for the accuracy-degradation finding.

WHY THIS FOLLOWS SCRIPT 29
---------------------------
Script 29 showed the placebo predictors (pure WT-arm measurements, no model
at all) collapse to near-zero/negative correlation with target in the
high-|e.b| stratum -- confirming the mechanical circularity flagged in
Tier 1a is real and large.

But ESM-2 (model_C) degraded LESS than those placebos (68% vs ~105%), not
the same amount. That's ambiguous on its own:

  (a) ESM-2 is genuinely more robust to whatever it's missing about genetic
      interaction, OR
  (b) ESM-2 is simply a WEAKER, noisier proxy for w.fitness than the
      placebos are (0.53 vs 0.93 starting rho), so it has less of the
      confounding component to lose in the first place -- its smaller %
      drop is exactly what ANY predictor with ESM-2's overall coupling
      strength to w.fitness would show, model or not.

(a) and (b) are very different claims and % drop cannot tell them apart,
because it's sensitive to starting strength. This script builds a same-
STRENGTH comparison instead of a same-formula one.

METHOD
------
Synthetic predictor = alpha * z(w.fitness) + sqrt(1-alpha^2) * noise.
Bisection-search alpha (same pattern as script 26's mechanical baseline)
so the synthetic's LOW-stratum correlation with target matches ESM-2's
LOW-stratum correlation exactly -- same starting strength, no model behind
it, built purely from the same WT-arm quantity that drives the confound.

Compare HIGH-stratum rho: ESM-2 (real) vs. matched-strength synthetic.

  * Gap indistinguishable from 0 -> ESM's degradation is fully explained by
    its overall correlation with w.fitness. No ESM-2-specific finding.
  * Gap > 0 (ESM higher)         -> ESM retains real information beyond
    what the confound alone produces. THAT gap, not 0.53->0.17, is the
    number to report, with its own CI.
  * Gap < 0 (ESM lower)          -> the original epistasis-blindness claim
    survives this check, strengthened.

The gap is bootstrapped by position, refitting alpha inside every resample
so "matched starting strength" holds each time, not just at the point
estimate.
"""
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scripts.lib.io import load_derived_maps
from scripts.lib.stats import _spearman

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - np.nanmean(x)) / np.nanstd(x)


def strat_rho(d, pred, gi_col="abs_gi", target_col="target", n=3):
    s = d.dropna(subset=[pred, gi_col, target_col])
    cuts = np.quantile(s[gi_col], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s[gi_col], cuts)
    return [_spearman(s[pred].to_numpy()[k == i], s[target_col].to_numpy()[k == i])
            for i in range(n)]


def make_synthetic(alpha, anchor_z, rng):
    noise = rng.standard_normal(len(anchor_z))
    return alpha * anchor_z + np.sqrt(max(1 - alpha**2, 0.0)) * noise


def fit_alpha(d, target_low_rho, rng, iters=25):
    lo, hi = 0.0, 1.0
    mid = 0.5
    for _ in range(iters):
        mid = (lo + hi) / 2
        syn = make_synthetic(mid, d["anchor_z"].to_numpy(), rng)
        r = _spearman(syn[d["_lowmask"].to_numpy()],
                      d.loc[d["_lowmask"], "target"].to_numpy())
        lo, hi = (mid, hi) if r < target_low_rho else (lo, mid)
    return mid


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()

    derived = load_derived_maps()
    df = df.merge(
        pd.DataFrame({"hgvs_pro": derived["hgvs"],
                     "placebo_wfitness": derived["w.fitness"]}),
        on="hgvs_pro", how="left")

    d = df.dropna(subset=["model_C", "abs_gi", "target", "placebo_wfitness"]).copy()
    d["anchor_z"] = zscore(d["placebo_wfitness"])
    print(f"n={len(d)}, positions={d['position'].nunique()}")

    real = strat_rho(d, "model_C")
    print("\nActual ESM-2 (model_C) tercile rho:", [f"{r:+.4f}" for r in real])

    cuts = np.quantile(d["abs_gi"], [1 / 3, 2 / 3])
    d["_stratum"] = np.digitize(d["abs_gi"], cuts)
    d["_lowmask"] = d["_stratum"] == 0

    rng = np.random.default_rng(SEED)
    alpha = fit_alpha(d, real[0], rng)
    print(f"Matched alpha (synthetic's LOW-stratum rho == ESM-2's): {alpha:.4f}")

    d["_syn"] = make_synthetic(alpha, d["anchor_z"].to_numpy(), rng)
    syn_r = strat_rho(d, "_syn")
    print(f"Synthetic (matched strength) tercile rho: {[f'{r:+.4f}' for r in syn_r]}")
    print(f"\nHIGH stratum: ESM-2={real[2]:+.4f}  matched-strength synthetic={syn_r[2]:+.4f}")
    gap = real[2] - syn_r[2]
    print(f"Point-estimate gap (ESM-2 minus matched synthetic) = {gap:+.4f}")

    print(f"\nBootstrapping gap by position ({N_BOOT} draws)...")
    d = d.reset_index(drop=True)
    positions = d["position"].unique()
    idx_by_pos = {p: d.index[d["position"] == p].to_numpy() for p in positions}

    boot_gap = np.empty(N_BOOT)
    for b in range(N_BOOT):
        drawn = rng.choice(positions, size=len(positions), replace=True)
        rows = np.concatenate([idx_by_pos[p] for p in drawn])
        bs = d.iloc[rows].reset_index(drop=True)
        cuts_b = np.quantile(bs["abs_gi"], [1 / 3, 2 / 3])
        bs["_stratum"] = np.digitize(bs["abs_gi"], cuts_b)
        bs["_lowmask"] = bs["_stratum"] == 0
        r_real = strat_rho(bs, "model_C")
        a_b = fit_alpha(bs, r_real[0], rng, iters=15)
        bs["_syn"] = make_synthetic(a_b, bs["anchor_z"].to_numpy(), rng)
        boot_gap[b] = r_real[2] - strat_rho(bs, "_syn")[2]

    ci_lo, ci_hi = np.nanpercentile(boot_gap, [2.5, 97.5])
    print(f"Gap 95% CI: [{ci_lo:+.4f}, {ci_hi:+.4f}]")
    if ci_lo > 0:
        print("-> ESM-2 retains MORE signal in the high stratum than a matched-")
        print("   strength w.fitness-correlated proxy would. Real, reportable excess.")
    elif ci_hi < 0:
        print("-> ESM-2 retains LESS signal than a matched-strength proxy predicts.")
        print("   The original epistasis-blindness claim survives this check.")
    else:
        print("-> Indistinguishable from a matched-strength mechanical proxy.")
        print("   No ESM-2-specific finding here beyond the confound.")

    pd.DataFrame([{"real_low": real[0], "real_mid": real[1], "real_high": real[2],
                  "matched_alpha": alpha, "syn_low": syn_r[0], "syn_mid": syn_r[1],
                  "syn_high": syn_r[2], "gap_high": gap,
                  "gap_ci_lo": ci_lo, "gap_ci_hi": ci_hi}]).to_csv(
        PROC / "task_matched_confound_curve.csv", index=False)
    print(f"\nSaved to {PROC / 'task_matched_confound_curve.csv'}")
