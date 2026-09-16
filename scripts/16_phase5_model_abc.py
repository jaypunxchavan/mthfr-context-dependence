"""
Task 3 / Phase 5: Can ESM-2 use context it can see?

Three scoring schemes, evaluated against REAL measured fitness in the
p.Ala222Val background (mean of the four A222V-background conditions):

  A  S(v | WT)                      background ignored
  B  S(v | WT) + S(A222V | WT)      additive baseline IN SCORE SPACE
  C  S(v | A222V background)        background supplied as sequence

STRUCTURAL NOTE ON MODEL B: S(A222V|WT) is a single constant (-5.2003),
identical for every variant. Adding a constant cannot change rank order,
so under rank correlation -- which the proposal specifies, because B and C
are not on a commensurate fitness scale -- Model B is EXACTLY equivalent to
Model A. This is verified numerically below rather than assumed. The
meaningful comparison is therefore A(=B) vs C, i.e. whether putting the
background into the model's input changes anything.

Key prediction: C gains over B specifically among variants with strong
measured genetic interaction, not uniformly.

Direct endpoint: delta_ESM = C - A, correlated against measured e.b.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scripts.lib.io import A222V_COND_COLS
from scripts.lib.stats import (position_cluster_bootstrap, paired_rho_difference_bootstrap,
                               _spearman)

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase3_analysis_table.csv")
    esm = pd.read_csv(PROC / "esm2_wt_scores.csv")
    const = esm.loc[esm["hgvs_pro"] == "p.Ala222Val", "esm2_score"].iloc[0]

    df["model_A"] = df["esm2_score"]
    df["model_B"] = df["esm2_score"] + const
    df["model_C"] = df["esm2_score_a222v_bg"]
    df["delta_esm"] = df["model_C"] - df["model_A"]
    df["target"] = df["f_bar_a222v"]

    d = df.dropna(subset=["model_A", "model_B", "model_C", "target"]).copy()
    print(f"Analysis set: {len(d)} variants, {d['position'].nunique()} positions")
    print(f"S(A222V | WT) constant = {const:.4f}")

    print("\n" + "=" * 72)
    print("STRUCTURAL CHECK: is Model B distinguishable from Model A?")
    print("=" * 72)
    ra, rb = _spearman(d["model_A"], d["target"]), _spearman(d["model_B"], d["target"])
    print(f"  rho(A, target) = {ra:.10f}")
    print(f"  rho(B, target) = {rb:.10f}")
    print(f"  Identical: {ra == rb}")
    print("  Model B adds a CONSTANT to every score, so it cannot change rank")
    print("  order. Under the proposal's specified rank-correlation comparison,")
    print("  B is degenerate with A. Reported, not hidden: the real test is A vs C.")

    print("\n" + "=" * 72)
    print(f"MODEL COMPARISON vs measured A222V-background fitness "
          f"(n_boot={N_BOOT}, seed={SEED})")
    print("=" * 72)
    rows = []
    for name in ["model_A", "model_B", "model_C"]:
        r = position_cluster_bootstrap(d, "position", name, "target",
                                       n_boot=N_BOOT, seed=SEED)
        print(f"  {name}: rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] n={r['n_rows']}")
        rows.append({"model": name, "rho": r["observed_rho"],
                     "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"], "n_rows": r["n_rows"]})
    pd.DataFrame(rows).to_csv(PROC / "phase5_model_comparison.csv", index=False)

    diff = paired_rho_difference_bootstrap(d, "position", "model_B", "model_C",
                                           "target", n_boot=N_BOOT, seed=SEED)
    print(f"\n  C - B difference: {diff['observed_diff']:+.4f} "
          f"CI=[{diff['ci_lo']:+.4f},{diff['ci_hi']:+.4f}] p={pstr(diff['p_boot'])}")
    print(f"  -> CI {'INCLUDES zero' if diff['ci_lo'] < 0 < diff['ci_hi'] else 'excludes zero'}")

    print("\n" + "=" * 72)
    print("KEY PREDICTION: does C beat B specifically where GI is strong?")
    print("=" * 72)
    s = d.dropna(subset=["GI_folinate_independent"]).copy()
    s["abs_gi"] = s["GI_folinate_independent"].abs()
    s["gi_stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])

    strat_rows = []
    for lvl in ["low", "mid", "high"]:
        sub = s[s["gi_stratum"] == lvl]
        dd = paired_rho_difference_bootstrap(sub, "position", "model_B", "model_C",
                                             "target", n_boot=N_BOOT, seed=SEED)
        rc = position_cluster_bootstrap(sub, "position", "model_C", "target",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"  GI {lvl:4s} (n={len(sub):5d}, {sub['position'].nunique():3d} pos): "
              f"rho_C={rc['observed_rho']:+.4f}  C-B={dd['observed_diff']:+.4f} "
              f"CI=[{dd['ci_lo']:+.4f},{dd['ci_hi']:+.4f}] p={pstr(dd['p_boot'])}")
        strat_rows.append({"gi_stratum": lvl, "n_rows": len(sub),
                           "n_positions": sub["position"].nunique(),
                           "rho_C": rc["observed_rho"], "diff_C_minus_B": dd["observed_diff"],
                           "ci_lo": dd["ci_lo"], "ci_hi": dd["ci_hi"], "p_boot": dd["p_boot"]})
    pd.DataFrame(strat_rows).to_csv(PROC / "phase5_stratified.csv", index=False)
    print("\n  Prediction was: C gains over B in the HIGH stratum specifically.")

    print("\n" + "=" * 72)
    print("DIRECT ENDPOINT: delta_ESM vs measured genetic interaction")
    print("=" * 72)
    s["abs_delta"] = s["delta_esm"].abs()
    for xa, xb, lbl in [("delta_esm", "GI_folinate_independent", "signed"),
                        ("abs_delta", "abs_gi", "absolute")]:
        r = position_cluster_bootstrap(s, "position", xa, xb, n_boot=N_BOOT, seed=SEED)
        print(f"  {lbl:8s}: rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'])} n={r['n_rows']}")

    d.to_csv(PROC / "phase5_analysis_table.csv", index=False)
    print(f"\nSaved results to {PROC}")
