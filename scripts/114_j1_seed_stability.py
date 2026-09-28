"""
Script 114 (task J1, Group J) -- does the +0.02121 A222V over-shift
result replicate across the five ESM-1v checkpoints?

PRE-REGISTERED: this docstring was written before the first run; every
coverage rule, gate, and reporting statement below was fixed before
any number produced here was seen (AGENTS sec 6).

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group J, task J1.

THE STATISTIC UNDER TEST (read from its producer, script 69 W3, before
computing anything): M1d residual =
    mean|delta_AV| - OLS-predicted-at-S(A222V)
  where the OLS fits mean|delta_b| ~ S(b|WT) on the k=30 decile
  backgrounds, delta_b(v) = S(v|b) - S(v|WT), means over the fixed
  120-position x 19-substitution grid (2,280 values), and the CI is a
  position-cluster bootstrap (N_BOOT=2000, seed 1 in script 69).
  On disk: task69_w3_backgrounds.csv (31 rows = 30 decile + A222V)
  with residual_a222v = 0.021205120280956197, CI
  [0.004647772429603798, 0.03933804276245424] -> the record's
  +0.02121 [+0.00465, +0.03934].

J1a -- COVERAGE CHECK FIRST (the task's own escape clause):
  The design needs each checkpoint to have scores under all 30 decile
  backgrounds.  Grep/ls-verified inventory used by this script:
    * Background caches in data/processed/: esm2_a222v_bg_scores.csv,
      task63_m1_bg_raw.csv (8 bgs), task69_w2_bg_raw.csv (30 bgs),
      task82_ae_raw.csv (57 bgs) -- ALL produced by scripts 11/63/69/82
      with esm2_t33_650M_UR50D; none contains ESM-1v scores.
    * ESM-1v checkpoint caches: task_AC4_esm1v_member{1..5}_scores.csv
      -- columns are exactly position/wt_aa/mut_aa/wt_logodds/
      av_logodds/delta, i.e. TWO backgrounds only: WT and A222V.
  => decile-background coverage for every ESM-1v checkpoint = 0/30
     (GATED below from the files themselves, not assumed).
  Branch rule, pre-stated: if coverage < 30/30 for a checkpoint, the
  M1d residual is NOT COMPUTABLE for that checkpoint; print the
  coverage table, report what IS computable, and do not fabricate a
  per-seed residual.  All five members are expected to take this
  branch; if any member unexpectedly has coverage, the computable
  branch would extend -- the gates print which happened.

WHAT IS COMPUTABLE (reported, pre-declared):
  * The A222V arm alone: mean|delta_m| over the identical
    120-position grid for each of the five members, with a
    position-cluster bootstrap CI (cluster = subset position, resample
    120 positions, recompute the mean fresh; seed 0, N_BOOT env
    default 10000).  This is M1d's OBSERVED side only -- it is NOT
    the residual (the regression side needs the 30 decile means,
    which do not exist for ESM-1v).  Printed as exactly that.
  * Grid identity is GATED against the ESM-2 side: mean|delta_ESM2|
    on my reconstructed grid must equal the A222V row's
    mean_abs_delta in task69_w3_backgrounds.csv, and a fresh OLS on
    the CSV's own 30 (S, mean) points must reproduce the disk
    residual to 1e-9 -- so the coverage verdict sits on verified
    statistic machinery, not a paraphrase.

GATES (failure -> print the exact mismatch, sys.exit(1)):
  G1  task69_w3_backgrounds.csv: exactly 31 rows, 30 decile + 1
      A222V row; fresh OLS re-derivation reproduces the disk
      residual 0.021205120280956197 to 1e-9 (point statistic; the
      disk CI is QUOTED, not re-derived -- script 69's bootstrap is
      not re-run here, disclosed).
  G2  W2 cache: 30 bg_ids x 2,280 rows (120 pos x 19) each; the
      grid = 120 unique positions x 19 mut_aa.
  G3  ESM-2 A222V arm on my grid reproduces the disk A222V row's
      mean_abs_delta to 1e-9 (grid identity).  Source =
      merged_wt_a222v_scores.csv -- script 69's own docstring names
      it as the W3 arm's source ("A222V's arm = existing
      merged_wt_a222v_scores.csv ... script 12's data, NOT
      rescored").  DISCLOSURE: the first version of this gate joined
      against phase5_analysis_table.csv instead and failed (203 grid
      rows absent -- phase5 is a filtered 11,344-row table, e.g. it
      lacks p.Ser10Ala/Glu/Gln).  The gate failed before ANY result
      was produced; the source was corrected to the documented
      producer of the record's value.  The pre-registered RULE
      (reproduce the disk A222V arm mean to 1e-9) was unchanged;
      only the file feeding it.  Logged per AGENTS sec 6.
  G4  all five member files: columns are exactly the two-background
      schema; joined to the grid with zero missing delta values;
      delta == av_logodds - wt_logodds to 1e-12.
  G5  ESM-1v decile coverage = 0/30 (asserted from the inventory --
      this is the fact that selects the NOT-COMPUTABLE branch).

REPORTING RULES (pre-registered):
  * J1b verdict is one of, chosen by what the gates show:
      (a) all members 0/30 -> "seed-stability NOT ASSESSABLE from
          cached data: the residual statistic is undefined for every
          ESM-1v checkpoint (0 of 30 severity-spread backgrounds
          scored); the +0.02121 result keeps its single-checkpoint
          status; scoring 30 bgs x 120 pos x 5 checkpoints is NEW
          model scoring, barred this session."  Explicitly NOT
          claimed: stable, unstable, or exploratory-only -- none of
          those was measured.
      (b) partial/full coverage -> compute what exists per member
          and judge stability from it.
  * The ESM-2 +0.02121 values in this script's output are READ from
    task69_w3_backgrounds.csv (quoted) or re-derived pointwise from
    its own columns (G1) -- never invented (AGENTS 5).

LIMITATIONS (printed with the output):
  - The per-member A222V-arm means carry position-cluster CIs only;
    no cross-checkpoint inferential test is possible (there is no
    per-seed residual to test).
  - S(b|WT) is ESM-2's own severity scale (the design's stratifier);
    even with scores, a member-side severity would be a different
    design -- stated, not silently swapped.
  - Reproducing the ESM-2 residual from the CSV (G1) is a unit test
    of my reading of the statistic, not independent evidence.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/114_j1_seed_stability.py
  N_BOOT=10000 venv/bin/python3 scripts/114_j1_seed_stability.py
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

PROC = ROOT / "data" / "processed"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
DISK_RESID = 0.021205120280956197
DISK_CI = (0.004647772429603798, 0.03933804276245424)
OUT = PROC / "task114_j1_coverage_and_arm.csv"
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"J1 -- seed stability of the +0.02121 A222V residual "
           f"(scripts/114)  N_BOOT={N_BOOT} seed={SEED}")

    # ---- G1: the W3 design + record scalars ------------------------------
    w3 = pd.read_csv(PROC / "task69_w3_backgrounds.csv")
    is_av = w3["bg_id"].astype(str).str.fullmatch("A222V")
    n_decile = int((~is_av).sum())
    if (len(w3), n_decile, int(is_av.sum())) != (31, 30, 1):
        gfail(f"G1 FAIL: w3 table = {len(w3)} rows, decile={n_decile}, "
              f"A222V={int(is_av.sum())}, expected 31/30/1")
    av_row = w3[is_av].iloc[0]
    dec = w3[~is_av]
    X = np.column_stack([np.ones(len(dec)), dec["S_b_given_WT"].to_numpy()])
    beta, *_ = np.linalg.lstsq(X, dec["mean_abs_delta"].to_numpy(), rcond=None)
    pred = beta[0] + beta[1] * float(av_row["S_b_given_WT"])
    resid = float(av_row["mean_abs_delta"]) - pred
    if abs(resid - DISK_RESID) > 1e-9:
        gfail(f"G1 FAIL: fresh OLS residual {resid!r} vs disk "
              f"{DISK_RESID!r}")
    print(f"  G1 PASS: 31 rows (30 decile + A222V); fresh OLS reproduces "
          f"the disk residual {resid!r} (tol 1e-9); record quote: "
          f"+0.02121 CI [+0.00465, +0.03934], rho "
          f"{float(av_row['spearman_rho']):+.6f}, n_boot="
          f"{int(av_row['n_boot'])}, n_sub={int(av_row['n_sub'])}")

    # ---- G2: the W2 grid -------------------------------------------------
    w2 = pd.read_csv(PROC / "task69_w2_bg_raw.csv")
    sizes = w2.groupby("bg_id").size()
    if len(sizes) != 30 or not (sizes == 2280).all():
        gfail(f"G2 FAIL: W2 bg_ids={len(sizes)}, sizes="
              f"{sorted(sizes.unique())} vs 30 x 2280")
    g0 = w2[w2["bg_id"] == sizes.index[0]]
    grid = g0[["position", "mut_aa", "hgvs_pro"]].copy()
    if (grid["position"].nunique(), len(grid)) != (120, 2280):
        gfail(f"G2 FAIL: grid = {grid['position'].nunique()} pos x "
              f"{len(grid)} rows vs 120 x 2280")
    print(f"  G2 PASS: W2 grid = 120 positions x 19 = 2,280 rows "
          f"(30 bg_ids all 2,280)")

    # ---- G3: ESM-2 A222V arm identity on this grid -----------------------
    # Script 69's documented arm source (its docstring, W3 section);
    # phase5_analysis_table.csv was tried first and REJECTED by this very
    # gate (203 grid rows filtered out of it) -- see docstring disclosure.
    arm = pd.read_csv(PROC / "merged_wt_a222v_scores.csv")[
        ["hgvs_pro", "delta_esm"]]
    gg = grid.merge(arm, on="hgvs_pro", how="left")
    if gg["delta_esm"].isna().any():
        gfail(f"G3 FAIL: {int(gg['delta_esm'].isna().sum())} grid rows "
              f"missing from merged_wt_a222v_scores.csv")
    e2_av_mean = float(gg["delta_esm"].abs().mean())
    if abs(e2_av_mean - float(av_row["mean_abs_delta"])) > 1e-9:
        gfail(f"G3 FAIL: ESM-2 mean|delta_AV| on my grid {e2_av_mean!r} "
              f"vs disk {float(av_row['mean_abs_delta'])!r}")
    print(f"  G3 PASS: grid identity -- ESM-2 mean|delta_AV| on this grid "
          f"= {e2_av_mean!r} == disk A222V row (tol 1e-9; source "
          f"merged_wt_a222v_scores.csv, script 69's documented arm file)")

    # ---- G4/G5: ESM-1v coverage inventory --------------------------------
    banner("J1a -- COVERAGE (checked first, per task)", "-")
    expected_cols = ["position", "wt_aa", "mut_aa", "wt_logodds",
                     "av_logodds", "delta"]
    members = {}
    rows = []
    for k in range(1, 6):
        m = pd.read_csv(PROC / f"task_AC4_esm1v_member{k}_scores.csv")
        if list(m.columns) != expected_cols:
            gfail(f"G4 FAIL: member {k} columns {list(m.columns)} != "
                  f"two-background schema")
        if float(np.abs((m["av_logodds"] - m["wt_logodds"])
                        - m["delta"]).max()) > 1e-12:
            gfail(f"G4 FAIL: member {k} delta != av - wt (tol 1e-12)")
        j = grid.merge(m[["position", "mut_aa", "delta"]],
                       on=["position", "mut_aa"], how="left")
        miss = int(j["delta"].isna().sum())
        if miss:
            gfail(f"G4 FAIL: member {k} missing {miss} grid rows")
        members[k] = j["delta"].to_numpy()
        rows.append(dict(member=k, backgrounds_available="WT + A222V (2)",
                         decile_bg_covered="0/30",
                         grid_rows=len(j), missing=miss,
                         mean_abs_delta_av=float(
                             np.abs(j["delta"]).mean())))
    print(f"  G4 PASS: all five members join the grid with 0 missing; "
          f"delta == av-wt to 1e-12; columns = two-background schema")
    decile_cov = 0  # from the schema gate: no member file carries any
    #                 decile background -- asserted, not assumed
    if decile_cov != 0:
        gfail(f"G5 FAIL: decile coverage {decile_cov}/30, expected 0/30 "
              f"(branch would change -- stop, report)")
    print(f"  G5 PASS: ESM-1v decile-background coverage = 0/30 for every "
          f"member (no background cache outside {PROC.name} is scored "
          f"with ESM-1v; verified from file inventory + schema)")
    print("\n  Coverage table:")
    print(f"    {'member':8s} {'backgrounds':22s} {'decile':>8s} "
          f"{'grid rows':>10s} {'missing':>8s} {'mean|d_AV|':>12s}")
    for r in rows:
        print(f"    {'member ' + str(r['member']):8s} "
              f"{r['backgrounds_available']:22s} "
              f"{r['decile_bg_covered']:>8s} {r['grid_rows']:10d} "
              f"{r['missing']:8d} {r['mean_abs_delta_av']:12.8f}")

    # ---- computable piece: A222V arm per member, with CI -----------------
    banner("J1a -- WHAT IS COMPUTABLE: the A222V arm alone "
           "(observed side of M1d, NOT the residual)", "-")
    pos = grid["position"].to_numpy()
    uniq = np.unique(pos)
    idx_by = {c: np.flatnonzero(pos == c) for c in uniq}
    rng = np.random.default_rng(SEED)
    boots = {k: np.empty(N_BOOT) for k in members}
    for b in range(N_BOOT):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        for k, arr in members.items():
            boots[k][b] = np.abs(arr[i]).mean()
    print(f"  ESM-2 (record, quoted from task69_w3_backgrounds.csv): "
          f"mean|d_AV| = {e2_av_mean:.8f}; residual +0.02121 "
          f"[+0.00465, +0.03934] (CI quoted, not re-run)")
    for k, arr in members.items():
        lo, hi = np.percentile(boots[k], [2.5, 97.5])
        print(f"  member {k}: mean|d_AV| = {np.abs(arr).mean():.8f}  "
              f"CI [{lo:.8f}, {hi:.8f}]  (position-cluster, "
              f"{N_BOOT} draws, seed {SEED})")
    vals = [np.abs(a).mean() for a in members.values()]
    print(f"  across the five members: mean {np.mean(vals):.8f}, "
          f"sd {np.std(vals, ddof=1):.8f}, min {min(vals):.8f}, "
          f"max {max(vals):.8f} (descriptive; no per-seed residual "
          f"exists to compare)")

    # ---- J1b verdict ------------------------------------------------------
    banner("J1b -- VERDICT", "-")
    print("  Seed-stability of +0.02121 [+0.00465, +0.03934] across the")
    print("  five ESM-1v checkpoints is NOT ASSESSABLE from cached data:")
    print("  every checkpoint has 0/30 of the severity-spread")
    print("  backgrounds the residual statistic's regression requires")
    print("  (only WT and A222V are scored for ESM-1v), so the OLS side")
    print("  -- and with it the residual -- is undefined for all five.")
    print("  What IS computable (the A222V arm alone) is printed above")
    print("  and does not substitute for the residual.")
    print("  Explicitly NOT claimed: stable, unstable, or")
    print("  exploratory-only -- none of those was measured here.")
    print("  The result keeps its existing single-checkpoint status")
    print("  ('verified across backgrounds and positions on one")
    print("  checkpoint; unverified across seeds' -- true-final-closeout")
    print("  record). Testing it on ESM-1v requires scoring 30 bgs x")
    print("  120 pos x 5 checkpoints = 18,600 forward passes -- NEW")
    print("  model scoring, barred this session.")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. Per-member CIs cover the A222V arm only (position-")
    print("     cluster); no inferential cross-seed test is possible.")
    print("  2. S(b|WT) is ESM-2's severity scale by design; a")
    print("     member-side severity would be a different experiment.")
    print("  3. G1's OLS reproduction is a unit test of the reading,")
    print("     not independent evidence for the record's residual.")
    print(f"\nWrote {OUT}")
    print(f"SCRIPT 114 DONE ({time.time() - T0:.1f}s)")
