"""
Script 117 (task I1, Group I) -- per-condition anchors: free internal
replication across the four folinate concentrations.

PRE-REGISTERED: this docstring was written before the first run; inputs,
frame, diagnostics, and statement rule below were fixed before any
number produced here was seen (AGENTS sec 6).  Nothing is selected
after results.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group I, task I1.

I1a -- FOUR ANCHORS, ONE PER CONDITION
--------------------------------------
The anchor convention elsewhere in this project is
rho(delta_ESM, own_e.b) with position-cluster bootstrap.  own_e.b is
the POOLED WLS intercept across the four conditions (the task says:
not the pooled residual).  Here each condition gets its own outcome:

    resid_c = m_score(c) - expected(c)

taken from the project's own two-pass fit (the SAME e2["resid"] whose
WLS-intercept-with-weights-1/m_se^2 equals own_e.b -- identity-checked
in G2 below, so these four columns are literally the ingredients of
the quantity the anchor correlates).

For c in {12, 25, 100, 200}:
  - rho_c = spearman(delta_ESM, resid_c) over analysis-base rows with
    a finite resid_c in that condition (n_c printed),
  - 95% position-cluster bootstrap CI, seed 0, N_BOOT env, p_boot
    reported as primary (the project's standard convention),
  - mean measured fitness of the condition: mean m_score(c) over the
    same rows (the "mean fitness level" I1b asks about),
  - mean expected(c) = mean(m_c - resid_c), and mean resid_c.

Reference line printed alongside: the pooled anchor
rho(delta_ESM, own_e_b) on the identical base.

I1b -- STATEMENT DIAGNOSTICS (pre-stated)
-----------------------------------------
  D1. sign set: do all four rho_c share one sign, and is it the
      pooled anchor's sign?
  D2. magnitude: max/min |rho_c|, range, and whether all four point
      estimates fall on the same side of the pooled value within
      0.05 absolute (descriptive label, printed with the numbers).
  D3. fitness tracking: Kendall tau-b between the four-condition
      ordering of mean fitness and the ordering of rho_c.  With n=4
      this is DESCRIPTIVE ONLY (no p claimed); |tau| = 1 is a perfect
      ordering correspondence.

Statement rule (pre-registered):
  - all signs equal AND |tau| < 1  -> "sign and magnitude consistent
    across conditions; no exact mean-fitness ordering tracking."
  - |tau| == 1                     -> "rho ordering tracks the
    mean-fitness ordering exactly (consistent with a measurement-
    scale artifact reading); descriptive only at n=4."
  - signs differ                   -> name the condition(s) whose
    sign differs, print it plainly, no reframing.
  Combinations print all applicable facts.

GATES (failure -> print exact mismatch, sys.exit(1)):
  G1  Analysis base = (10,757 rows, 654 positions), same frame as
      Groups G/H.
  G2  The WLS intercept of resid (weights 1/m_se^2, the fit's own
      valid mask) reproduces the recorded own_e_b to max|diff| < 1e-9
      -- identity proving resid_c above IS what own_e.b was fitted to.
  G3  Every condition has >= 9,000 finite resid_c rows in the base
      (misalignment safety net; exact n_c printed).

LIMITATIONS (printed with the output):
  - resid_c are four correlated views of the same variants, NOT four
    independent replications; CIs within a condition do not speak to
    between-condition differences.
  - mean-fitness comparison is n=4 points; any "tracking" statement
    is descriptive, never inferential.
  - The condition residuals share the same expected() construction
    (same A222V line, same correction curve), so a construction-level
    artifact would appear in all four -- consistency is necessary
    but not sufficient for genuineness.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/117_i1_per_condition_anchor.py
  N_BOOT=10000 venv/bin/python3 scripts/117_i1_per_condition_anchor.py
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scipy.stats import kendalltau

from scripts.lib.own_context import CONCS, MT_SCORE_COLS
from scripts.lib.stats import position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel" / "results"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
OUT = PROC / "task117_i1_per_condition.csv"
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"I1 -- per-condition anchors (scripts/117)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ---- fit + frames ------------------------------------------------------
    raw = pd.read_csv(RAW / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    resid = fit["resid"]                    # (n_raw, 4)
    Mse, valid = fit["M_se"], fit["valid"]
    w_m = np.where(valid, 1.0 / np.where(valid, Mse, 1.0) ** 2, 0.0)
    S0m = w_m.sum(axis=1)
    S1m = (w_m * CONCS[None, :]).sum(axis=1)
    S2m = (w_m * CONCS[None, :] ** 2).sum(axis=1)
    det = S0m * S2m - S1m ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        eb_re = np.where(det != 0,
                         (S2m * (w_m * np.nan_to_num(resid)).sum(axis=1)
                          - S1m * (w_m * CONCS[None, :]
                                   * np.nan_to_num(resid)).sum(axis=1)) / det,
                         np.nan)

    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G1 FAIL: base = ({len(base)}, {base['position'].nunique()}), "
              f"expected (10757, 654)")
    print(f"  G1 PASS: base (10757, 654) -- same frame as Groups G/H")

    rmap = pd.DataFrame({"hgvs_pro": raw["hgvs"], "eb_re": eb_re})
    n_before = len(base)
    base = base.merge(rmap, on="hgvs_pro", how="left")
    if len(base) != n_before:
        gfail(f"G1 FAIL: join changed row count {n_before} -> {len(base)}")
    n_missing = int(base["eb_re"].isna().sum())
    if n_missing:
        gfail(f"G2 FAIL: {n_missing} base rows have non-finite "
              f"recomputed intercept while own_e_b is finite")
    d = float(np.abs(base["eb_re"] - base["own_e_b"]).max())
    if d > 1e-9:
        gfail(f"G2 FAIL: WLS intercept of resid vs recorded own_e_b "
              f"max|diff| = {d!r} > 1e-9")
    print(f"  G2 PASS: intercept of resid == recorded own_e_b, "
          f"max|diff| = {d:.3e} (identity: these residuals ARE own_e.b's "
          f"ingredients)")

    # per-condition resid + m score for base rows
    lookup = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    base_rows = np.array([lookup[h] for h in base["hgvs_pro"]], dtype=int)
    R = resid[base_rows]                                   # (n_base, 4)
    M = raw[MT_SCORE_COLS].to_numpy(float)[base_rows]      # (n_base, 4)
    per_cond = np.isfinite(R).sum(axis=0)
    if (per_cond < 9000).any():
        gfail(f"G3 FAIL: per-condition finite-resid counts "
              f"{per_cond.tolist()} (need >= 9000 each)")
    print(f"  G3 PASS: finite resid_c rows per condition "
          f"{per_cond.tolist()} (>= 9000 each)")

    # ---- the four anchors + reference -------------------------------------
    banner("I1a -- ANCHOR PER FOLINATE CONDITION (rho [95% cluster CI])", "-")
    pooled = position_cluster_bootstrap(base, "position", "delta_esm",
                                        "own_e_b", N_BOOT, SEED)
    print(f"  REF pooled anchor rho(delta_ESM, own_e.b) = "
          f"{pooled['observed_rho']:+.6f} "
          f"[{pooled['ci_lo']:+.6f}, {pooled['ci_hi']:+.6f}] "
          f"p={pooled['p_boot']:.4f} (n={len(base)})")

    res = []
    for k, c in enumerate(CONCS):
        mask = np.isfinite(R[:, k])
        g = base.loc[mask, ["position", "delta_esm"]].copy()
        g["resid_c"] = R[mask, k]
        r = position_cluster_bootstrap(g, "position", "delta_esm",
                                       "resid_c", N_BOOT, SEED)
        mean_m = float(np.nanmean(M[mask, k]))
        mean_resid = float(np.nanmean(R[mask, k]))
        res.append(dict(cond=int(c), n=int(mask.sum()),
                        rho=r["observed_rho"], lo=r["ci_lo"],
                        hi=r["ci_hi"], p=r["p_boot"],
                        mean_fitness=mean_m, mean_resid=mean_resid,
                        mean_expected=mean_m - mean_resid))
        print(f"  c={int(c):3d}: n={int(mask.sum()):5d}  rho "
              f"{r['observed_rho']:+.6f} [{r['ci_lo']:+.6f}, "
              f"{r['ci_hi']:+.6f}] p={r['p_boot']:.4f}   mean fitness "
              f"(m_score) {mean_m:+.4f}   mean resid {mean_resid:+.4f}   "
              f"mean expected {mean_m - mean_resid:+.4f}")

    # ---- I1b diagnostics ----------------------------------------------------
    banner("I1b -- DIAGNOSTICS (pre-stated)", "-")
    rhos = np.array([r["rho"] for r in res])
    fits = np.array([r["mean_fitness"] for r in res])
    pooled_rho = pooled["observed_rho"]
    signs = np.sign(rhos)
    same_sign = bool(len(set(signs)) == 1)
    same_as_pooled = bool((signs == np.sign(pooled_rho)).all())
    print(f"  D1 signs: {signs.astype(int).tolist()} -> "
          f"{'all four share one sign' if same_sign else 'SIGNS DIFFER'}"
          f"{'; matches pooled anchor sign' if same_as_pooled else ''}")
    ab = np.abs(rhos)
    print(f"  D2 |rho| min {ab.min():.6f} max {ab.max():.6f} "
          f"ratio {ab.max() / ab.min():.3f} range {ab.max() - ab.min():.6f}; "
          f"pooled {abs(pooled_rho):.6f}; all within 0.05 abs of pooled: "
          f"{bool((np.abs(rhos - pooled_rho) <= 0.05).all())}")
    tau, p_tau = kendalltau(fits, rhos)
    print(f"  D3 Kendall tau-b(mean fitness, rho) over 4 conditions = "
          f"{tau:+.4f} (|tau|=1 would be perfect ordering "
          f"correspondence; n=4 -> DESCRIPTIVE ONLY, no p claimed "
          f"(scipy p={p_tau:.4g} shown for completeness only))")
    print("  mean fitness by condition:", np.round(fits, 4).tolist())
    print("  rho by condition:        ", np.round(rhos, 6).tolist())

    print("\n  STATEMENT (by pre-registered rule):")
    if not same_sign:
        flip = [int(CONCS[i]) for i in range(4)
                if signs[i] != np.sign(pooled_rho)]
        print(f"  - SIGNS DIFFER from the pooled sign at condition(s) "
              f"{flip}: the anchor's sign is not consistent across "
              f"conditions (reported plainly, no reframing).")
    if abs(tau) == 1.0:
        print("  - rho ordering tracks the mean-fitness ordering "
              "EXACTLY (|tau| = 1) -> consistent with a measurement-"
              "scale artifact reading; descriptive only at n=4.")
    elif same_sign:
        print("  - sign and magnitude consistent across conditions "
              "(all four same sign; rho ordering does NOT match mean-"
              "fitness ordering exactly -> no exact fitness tracking).")
    else:
        print("  - mixed pattern: see D1-D3 above; no single branch "
              "applies.")

    pd.DataFrame(res).to_csv(OUT, index=False)
    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. Four correlated views of the same variants, not four")
    print("     independent replications.")
    print("  2. Fitness-tracking diagnostic is n=4 -> descriptive.")
    print("  3. All four residuals share expected() (same A222V line,")
    print("     same correction): consistency is necessary, not")
    print("     sufficient for genuineness.")
    print(f"\nWrote {OUT}")
    print(f"SCRIPT 117 DONE ({time.time() - T0:.1f}s)")
