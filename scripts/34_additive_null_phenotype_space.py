"""
Script 34: a real no-interaction (additive) null, built in PHENOTYPE space.

WHY THE PROJECT HAS NEVER HAD ONE
---------------------------------
Visani/Verma/DeWitt (2026) argue that nothing can be attributed to learned
epistasis until it has been benchmarked against a model with no capacity to
represent epistasis at all. This repo has never had such a baseline.
Model B was the attempt, and it failed structurally: S(A222V|WT) is a single
constant, so adding it cannot change rank order, and model B is rank-identical
to model A.

THE KEY STRUCTURAL POINT, GENERALISED
-------------------------------------
Model B's degeneracy is not a quirk of score space. With ONE fixed background,
*every* no-interaction model is rank-degenerate with its own single-variant
input, because the background term is the same constant for every variant:

    multiplicative   pred(v) = w_hat(v) * A          A constant -> rank preserved
    additive         pred(v) = w_hat(v) + (A - 1)    A constant -> rank preserved

So Spearman CANNOT distinguish a no-interaction phenotype model from the raw
WT-background score. This is verified numerically below rather than asserted.
The consequence: the additive null must be judged on a SCALE-SENSITIVE metric
(MAE / RMSE on the fitness scale), not on rank correlation. That is the whole
reason this script exists and why it does not simply reuse the project's
rank-correlation machinery.

THE FOUR PREDICTORS
-------------------
  pred_A      isotonic(model_A -> target)      background ignored, but the
                                               calibration sees the A222V target
  pred_C      isotonic(model_C -> target)      background supplied to the model
  pred_mult   isotonic(model_A -> f_bar_wt) * A            no-interaction null
  pred_add    isotonic(model_A -> f_bar_wt) + (A - 1)      no-interaction null

A = the measured WT-background fitness of p.Ala222Val itself. The two nulls
never see the A222V-background target at any point; they are built purely
from the WT arm plus the atlas's own no-interaction algebra. Every isotonic
fit is cross-fitted by POSITION, so no variant is calibrated on its own
residue.

READING IT
----------
  pred_C beats both nulls on MAE  -> supplying the background genuinely helps
  pred_C indistinguishable        -> the background buys nothing a
                                     no-interaction model does not already have
  pred_C worse                    -> the background actively misleads the model
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import crossfit_isotonic_by_position, _spearman
from scripts.lib.stats_ext import paired_metric_difference_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    # A222V background constant, read BEFORE the model_C dropna below.
    # By design (script 11), p.Ala222Val is never assigned a model_C value --
    # its own hgvs_pro is written as None in the A222V-background scoring
    # file, since scoring A222V "in the A222V background" is not a meaningful
    # row. Reading A from a table filtered on model_C therefore always drops
    # exactly the one row this constant needs. phase3_analysis_table.csv
    # (script 15's output) carries f_bar_wt for every variant with >=1
    # measured condition, with no model_C requirement -- use that instead.
    p3_path = PROC / "phase3_analysis_table.csv"
    a_source = pd.read_csv(p3_path) if p3_path.exists() else df
    a_row = a_source[a_source["hgvs_pro"] == "p.Ala222Val"]
    if len(a_row) == 0 or a_row["f_bar_wt"].isna().all():
        print(f"p.Ala222Val not found with a valid f_bar_wt in {p3_path.name} either --")
        print("stopping rather than silently substituting a different constant.")
        sys.exit(1)
    A = float(a_row["f_bar_wt"].dropna().iloc[0])
    print(f"A222V background constant A = f_bar_wt(p.Ala222Val) = {A:.4f} "
          f"(read from {p3_path.name}, unaffected by the model_C filter below)")

    df = df.dropna(subset=["model_A", "model_C", "target", "f_bar_wt"]).reset_index(drop=True)
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    # --- build the four predictors ------------------------------------------
    df["pred_A"] = crossfit_isotonic_by_position(df, "position", "model_A",
                                                 "target", n_folds=5, seed=SEED)
    df["pred_C"] = crossfit_isotonic_by_position(df, "position", "model_C",
                                                 "target", n_folds=5, seed=SEED)
    w_hat = crossfit_isotonic_by_position(df, "position", "model_A",
                                          "f_bar_wt", n_folds=5, seed=SEED)
    df["w_hat"] = w_hat
    df["pred_mult"] = w_hat * A
    df["pred_add"] = w_hat + (A - 1.0)

    d = df.dropna(subset=["pred_A", "pred_C", "pred_mult", "pred_add", "target"]).copy()
    print(f"Rows with all four predictions: {len(d)}")

    # --- structural check: the degeneracy, demonstrated ----------------------
    print("\n" + "=" * 74)
    print("STRUCTURAL CHECK: is rank correlation able to see the null at all?")
    print("=" * 74)
    r_mult = _spearman(d["pred_mult"], d["target"])
    r_add = _spearman(d["pred_add"], d["target"])
    r_what = _spearman(d["w_hat"], d["target"])
    print(f"  rho(w_hat,     target) = {r_what:.10f}")
    print(f"  rho(pred_mult, target) = {r_mult:.10f}")
    print(f"  rho(pred_add,  target) = {r_add:.10f}")
    print(f"  mult identical to additive: {r_mult == r_add}")
    print(f"  both identical to w_hat:    {r_mult == r_what}")
    print("  A is a single constant, so both no-interaction forms are monotone")
    print("  transforms of w_hat. Rank correlation is blind to the distinction.")
    print("  Everything below is therefore reported on MAE, not rho.")

    rows = [{"stage": "degeneracy", "predictor": "pred_mult", "spearman": r_mult},
            {"stage": "degeneracy", "predictor": "pred_add", "spearman": r_add},
            {"stage": "degeneracy", "predictor": "w_hat", "spearman": r_what}]

    # --- headline: error on the fitness scale --------------------------------
    print("\n" + "=" * 74)
    print("MEAN ABSOLUTE ERROR against measured A222V-background fitness")
    print("=" * 74)
    for col, lbl in [("pred_C", "ESM-2, A222V background  [the claim]"),
                     ("pred_A", "ESM-2, WT background"),
                     ("pred_mult", "NULL: multiplicative no-interaction"),
                     ("pred_add", "NULL: additive no-interaction")]:
        mae = float(np.mean(np.abs(d[col] - d["target"])))
        rmse = float(np.sqrt(np.mean((d[col] - d["target"]) ** 2)))
        print(f"  {lbl:38s} MAE={mae:.4f}  RMSE={rmse:.4f}")
        rows.append({"stage": "metric", "predictor": col, "label": lbl,
                     "mae": mae, "rmse": rmse, "n": len(d)})

    print("\n" + "=" * 74)
    print(f"PAIRED DIFFERENCES, cluster-bootstrapped by position ({N_BOOT} draws)")
    print("=" * 74)
    COMPARISONS = [("pred_mult", "pred_C", "ESM-2(A222V bg) vs multiplicative null"),
                   ("pred_add", "pred_C", "ESM-2(A222V bg) vs additive null"),
                   ("pred_A", "pred_C", "ESM-2(A222V bg) vs ESM-2(WT bg)")]
    for a, b, lbl in COMPARISONS:
        r = paired_metric_difference_bootstrap(d, "position", a, b, "target",
                                               metric="mae", n_boot=N_BOOT, seed=SEED)
        better = ("ESM-2 LOWER error -- background helps" if r["ci_hi"] < 0 else
                  "ESM-2 HIGHER error -- background hurts" if r["ci_lo"] > 0 else
                  "INDISTINGUISHABLE")
        print(f"  {lbl}")
        print(f"    MAE diff = {r['observed_diff']:+.5f} "
              f"CI=[{r['ci_lo']:+.5f},{r['ci_hi']:+.5f}]  -> {better}")
        rows.append({"stage": "paired_mae", "predictor": lbl,
                     "diff": r["observed_diff"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "n": r["n_rows"],
                     "n_clusters": r["n_clusters"], "verdict": better})

    # --- stratified: does the background help WHERE interaction is strong? ---
    print("\n" + "=" * 74)
    print("STRATIFIED BY |e.b|: the original key prediction, on MAE")
    print("=" * 74)
    print("  Prediction under 'ESM-2 uses the background': the gap versus the")
    print("  no-interaction null should widen in the HIGH stratum specifically.")
    s = d.dropna(subset=["abs_gi"]).copy()
    s["stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    for lvl in ["low", "mid", "high"]:
        sub = s[s["stratum"] == lvl]
        if sub["position"].nunique() < 15:
            print(f"  {lvl:4s} SKIPPED ({sub['position'].nunique()} positions)")
            continue
        r = paired_metric_difference_bootstrap(sub, "position", "pred_mult",
                                               "pred_C", "target", metric="mae",
                                               n_boot=N_BOOT, seed=SEED)
        print(f"  {lvl:4s} (n={len(sub):5d})  MAE(null)={r['metric_a']:.4f}  "
              f"MAE(ESM-2)={r['metric_b']:.4f}  diff={r['observed_diff']:+.5f} "
              f"CI=[{r['ci_lo']:+.5f},{r['ci_hi']:+.5f}]")
        rows.append({"stage": "stratified_mae", "predictor": f"gi_{lvl}",
                     "mae_null": r["metric_a"], "mae_esm": r["metric_b"],
                     "diff": r["observed_diff"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "n": r["n_rows"]})

    out = PROC / "task34_additive_null.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    d.to_csv(PROC / "task34_predictions.csv", index=False)
    print(f"\nSaved to {out}")
    print("\nCAVEAT, stated rather than buried: pred_A and pred_C are calibrated")
    print("directly against the A222V target (cross-fit by position), while the")
    print("two nulls are calibrated against the WT target and then transformed by")
    print("a fixed constant. That asymmetry FAVOURS ESM-2. If ESM-2 still fails")
    print("to beat the nulls here, the conclusion is safe in the direction that")
    print("matters; if it wins narrowly, the margin is not clean evidence.")
