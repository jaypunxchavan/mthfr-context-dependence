"""
Task 2 / Phase 3: The central-error hypothesis test.

Decomposes ESM-2's prediction error against the REAL eight measured
conditions into:
  central error       |f_bar(v) - prediction(v)|   <- primary DV
  condition-specific  mean_c |f_c(v) - f_bar(v)|   <- unavailable to any
                                                      context-free predictor

Predictor: WT-background ESM-2 score ONLY. It is the field's convention
(one number from the canonical sequence), and it keeps the predictor
algebraically disjoint from delta_ESM, which is Task 3's test statistic.
Any WT/A222V blend would embed delta_ESM inside the predictor being tested.

IMPORTANT: univariate correlations between error and context dependence are
confounded. Context dependence correlates with base fitness by construction,
and both error metrics vary with position in the fitness distribution -- in
OPPOSITE directions (rank error rises with fitness, calibrated error is
U-shaped). Partial correlation controlling for f_bar is therefore the
primary test; univariate is reported only for comparison.

Pre-registered secondary arms:
  matched_WT     S(v|WT)    vs f_bar over the 4 WT-background conditions
  matched_A222V  S(v|A222V) vs f_bar over the 4 A222V-background conditions
  base_func      S(v|WT)    vs the atlas's own base functionality parameter
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from scripts.lib.io import CONDITION_COLS, WT_COND_COLS, A222V_COND_COLS
from scripts.lib.stats import (position_cluster_bootstrap, crossfit_isotonic_by_position,
                               partial_spearman_cluster_bootstrap)

import os
N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

CONTEXT_METRICS = [
    ("folinate_response", "environment-dependent"),
    ("GI_folinate_independent", "sequence-encoded genetic"),
    ("GI_folinate_dependent", "both"),
]


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    ctx = pd.read_csv(PROC / "context_metrics.csv")
    esm_wt = pd.read_csv(PROC / "esm2_wt_scores.csv")[["hgvs_pro", "esm2_score"]]
    bg = pd.read_csv(PROC / "merged_wt_a222v_scores.csv")[["hgvs_pro", "esm2_score_a222v_bg"]]

    df = ctx.merge(esm_wt, on="hgvs_pro", how="inner").merge(bg, on="hgvs_pro", how="left")
    print(f"Variants with context metrics + ESM-2 WT score: {len(df)}")
    print(f"  ...also with A222V-background score: {df['esm2_score_a222v_bg'].notna().sum()}")

    df["f_bar"] = df[CONDITION_COLS].mean(axis=1, skipna=True)
    df["n_conditions"] = df[CONDITION_COLS].notna().sum(axis=1)
    df["f_bar_wt"] = df[WT_COND_COLS].mean(axis=1, skipna=True)
    df["f_bar_a222v"] = df[A222V_COND_COLS].mean(axis=1, skipna=True)
    df["condition_specific"] = df[CONDITION_COLS].sub(df["f_bar"], axis=0).abs() \
                                 .mean(axis=1, skipna=True)
    df = df[df["n_conditions"] >= 1].copy()
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    # ---------- error metrics ----------
    df["pred_cal"] = crossfit_isotonic_by_position(df, "position", "esm2_score",
                                                   "f_bar", n_folds=5, seed=SEED)
    df["central_error_cal"] = (df["f_bar"] - df["pred_cal"]).abs()
    df["central_error_rank"] = (df["esm2_score"].rank() - df["f_bar"].rank()).abs()

    print("\n" + "=" * 72)
    print("ERROR DECOMPOSITION (proposal 5.5)")
    print("=" * 72)
    ok = df["pred_cal"].notna()
    total = df.loc[ok, CONDITION_COLS].sub(df.loc[ok, "pred_cal"], axis=0).abs() \
              .mean(axis=1, skipna=True).mean()
    cond = df.loc[ok, "condition_specific"].mean()
    cent = df.loc[ok, "central_error_cal"].mean()
    print(f"  mean total error       mean_c|f_c - pred| = {total:.4f}")
    print(f"  mean condition-specific mean_c|f_c-f_bar| = {cond:.4f}  ({100*cond/total:.1f}% of total)")
    print(f"  mean central error         |f_bar - pred| = {cent:.4f}")
    print("  The condition-specific share is unavailable to ANY context-free")
    print("  predictor under this task -- a property of one-number prediction,")
    print("  not a finding about ESM-2.")

    # ---------- primary + univariate ----------
    print("\n" + "=" * 72)
    print(f"CENTRAL ERROR vs CONTEXT DEPENDENCE (n_boot={N_BOOT}, seed={SEED})")
    print("=" * 72)
    rows = []
    for err_col, err_label in [("central_error_rank", "rank-based"),
                               ("central_error_cal", "calibrated")]:
        for metric, ctx_label in CONTEXT_METRICS:
            df["_ctx"] = df[metric].abs()
            uni = position_cluster_bootstrap(df, "position", "_ctx", err_col,
                                             n_boot=N_BOOT, seed=SEED)
            par = partial_spearman_cluster_bootstrap(df, "position", "_ctx", err_col,
                                                     "f_bar", n_boot=N_BOOT, seed=SEED)
            print(f"\n|{metric}| ({ctx_label}) vs {err_label} central error")
            print(f"  n={uni['n_rows']} rows / {uni['n_clusters']} positions")
            print(f"  univariate (CONFOUNDED): rho={uni['observed_rho']:+.4f} "
                  f"CI=[{uni['ci_lo']:+.4f},{uni['ci_hi']:+.4f}] p={pstr(uni['p_boot'])}")
            print(f"  PARTIAL, controlling f_bar: rho={par['observed_rho']:+.4f} "
                  f"CI=[{par['ci_lo']:+.4f},{par['ci_hi']:+.4f}] p={pstr(par['p_boot'])}")
            crosses = par["ci_lo"] < 0 < par["ci_hi"]
            print(f"  -> partial CI {'INCLUDES zero' if crosses else 'excludes zero'}")
            rows.append({"error_metric": err_label, "context_metric": metric,
                         "context_class": ctx_label, "n_rows": uni["n_rows"],
                         "n_positions": uni["n_clusters"],
                         "univariate_rho": uni["observed_rho"],
                         "univariate_ci_lo": uni["ci_lo"], "univariate_ci_hi": uni["ci_hi"],
                         "partial_rho": par["observed_rho"], "partial_ci_lo": par["ci_lo"],
                         "partial_ci_hi": par["ci_hi"], "partial_p": par["p_boot"],
                         "partial_ci_includes_zero": crosses})
    pd.DataFrame(rows).to_csv(PROC / "phase3_primary_results.csv", index=False)

    # ---------- pre-registered matched arms ----------
    print("\n" + "=" * 72)
    print("PRE-REGISTERED ARMS: predictive accuracy against different targets")
    print("=" * 72)
    arms = [
        ("primary (8-way mean)", "esm2_score", "f_bar"),
        ("matched WT (4 WT conds)", "esm2_score", "f_bar_wt"),
        ("matched A222V (4 A222V conds)", "esm2_score_a222v_bg", "f_bar_a222v"),
        ("base functionality", "esm2_score", "base_functionality"),
    ]
    arm_rows = []
    for name, xcol, ycol in arms:
        r = position_cluster_bootstrap(df, "position", xcol, ycol, n_boot=N_BOOT, seed=SEED)
        print(f"  {name:32s} rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] n={r['n_rows']}")
        arm_rows.append({"arm": name, "predictor": xcol, "target": ycol,
                         "n_rows": r["n_rows"], "rho": r["observed_rho"],
                         "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"]})
    pd.DataFrame(arm_rows).to_csv(PROC / "phase3_matched_arms.csv", index=False)

    df.to_csv(PROC / "phase3_analysis_table.csv", index=False)
    print(f"\nSaved results to {PROC}")
