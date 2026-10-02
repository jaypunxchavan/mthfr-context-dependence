"""Script 159 -- Task A2 gates for scripts/lib/phase3_common.py (Phase 3
session 3a, planning doc PHASE3_OVERNIGHT.md Task A2).

PRE-REGISTRATED: this docstring was written BEFORE the first run of this
script.  Per the planning doc's rule 3 it is not edited after any Phase 3
score exists (no Phase 3 score exists here at all -- this gate runs on the
cached MTHFR inputs only).

WHAT THIS SCRIPT IS
-------------------
A REFERENCE GATE, NOT AN IDENTITY GATE (planning doc rule 5).  Diagnostics
IV found a position-cluster bootstrap that passed "every cluster once
reproduces the point estimate" while drawing one row per cluster instead of
all of them; the identity gate cannot see that.  Therefore every bootstrap
routine here must additionally agree DRAW BY DRAW to 1e-12 with a slow,
obvious reference implementation on identical pre-drawn cluster ids, and the
corrected routine must reproduce Phase 1's published MTHFR CI.

GATES (ALL HARD; a failed gate prints GATE FAIL and the script exits 3 --
the driver never retries exit 3; planning doc rule 4.  Thresholds are never
loosened, N is never raised to make a gate pass.)

GATE A2-G1 (HARD) -- the generic library reproduces Diagnostics II/IV's
MTHFR numbers through its own API, applied to the cached inputs:
  * data/processed/phase2_diagnostics/background_rho_table.csv must have
    sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796;
  * data/processed/task32_analysis_table.csv (the 10,757-row anchor frame);
  * the 96 data/processed/phase2/bg_*.csv files via script 125's own cached
    construction (scripts.lib.phase2_diag.build -- IMPORTED, never
    reimplemented; AGENTS 2).
  Targets and tolerances (1e-9 on 9-dp values, 2e-6 on 6-dp values; the
  table in the planning doc governs, and every target is re-printed next to
  the value computed here -- rule 14):
    (a) input rho-table sha256                      (exact)
    (b) generic spearman == scipy.stats.spearmanr   (< 1e-12, anchor rows,
        both views)
    (c) A222V rho  full  = -0.088118064             (< 1e-9)
        (also computed directly from task32's own columns: 10,757 rows at
        654 positions -- row counts gated)
    (d) A222V rho  H     = -0.090021683             (< 1e-9; H = 455
        positions, script 125's own held-out set)
    (e) p_spec(neg) full = 2/79, k = 1, beaters = {G_P254F}
    (f) p_spec(neg) H    = 4/79, k = 3, beaters = {AV_195, AV_220, G_P254F}
        (both exact)
    (g) Spearman(rho_b, mean|delta|) over the 96 backgrounds, full
        = -0.614188823                              (< 1e-9)
    (h) same, H = -0.612696690                       (< 1e-9)
    (i) D9 PRIMARY leave-one-out r_A, full = -0.066425 (< 2e-6), k = 2
    (j) D9 PRIMARY leave-one-out r_A, H    = -0.068692 (< 2e-6), k = 2
    (k) corrected position-cluster CI for the UNRESTRICTED anchor =
        [-0.1173334458953319, -0.0595113844951173] (each endpoint < 1e-9),
        N_BOOT = 10000, SEED = 0.  Cross-checked against Phase 1's OWN
        routine (scripts/lib/stats.py position_cluster_bootstrap,
        imported unmodified) on the same rows, same tolerance.  This
        sub-gate runs ONLY when N_BOOT == 10000; at any other N it prints
        SKIPPED (smoke) and A2-G1 cannot be called PASS -- the gate
        decision rule below is evaluated on the N_BOOT == 10000 run.
    (l) column identity (AGENTS 5): the rho table's rho_full / rho_H must
        equal script 125's own A.point / point_rhos_H to < 1e-9 (a
        nominal disagreement between two sources would be a duplication
        bug until proven otherwise);
    (m) structure counts: 96 backgrounds, N = 78 (arms G = 40, V = 38,
        S = 18), anchor 10,757 rows / 654 positions, H = 455 positions.
  Toy-array self-checks for the library functions with no MTHFR target
  (p_spec all three modes, loo_ols on an exact line, background_boot on a
  constant, label_permutation_p bounds, spearman +/-1) are gated too --
  their expected values are fixed by hand, not by a prior run.

  DECISION RULE: if ANY A2-G1 sub-gate fails, this library is NOT trusted
  for GB1 or RBD: A4-A5 stop (planning doc Task A2).  Exit code 3.

GATE A2-G2 (HARD) -- reference bootstrap, draw by draw:
  (i)   identity: every retained cluster exactly once reproduces the point
        estimate (< 1e-12), on the anchor rows and on the restricted set;
  (ii)  max |corrected - reference| < 1e-12 over N_REF pre-drawn draws
        (ids from np.random.default_rng(SEED), one integers(0, nk, nk) per
        draw) on the ANCHOR ROWS;
  (iii) the same on a RESTRICTED row set with POSITIONS REMOVED -- the
        restriction is fixed here: a seed-SEED sample of 200 of the
        anchor's 654 positions is removed (np.random.default_rng(SEED)
        over np.unique(positions)), rows at the remaining 454 positions
        only.

RESAMPLING UNITS (AGENTS 3 / planning doc rule 6): every bootstrap in this
script resamples POSITION CLUSTERS (the anchor rho is computed inside one
background -- the A222V arm).  No background-level resampling is performed
by this gate.  The state in every docstring.

PROTECTED PATHS: nothing is written except this script and, by the caller's
redirect, docs/tasks/phase3-overnight/PHASE3_A2_FULL_OUTPUT.txt.  No
existing script or library is modified.  No torch / esm / thermompnn is
imported here (rule 1).

ENV: N_BOOT (default 10000), SEED (default 0), N_REF (default 500),
N_PERM (default 1000, used only by the label-permutation toy).

Usage:
  smoke:  N_BOOT=300 venv/bin/python3 scripts/159_phase3_common_gate.py
  full:   N_BOOT=10000 SEED=0 venv/bin/python3 scripts/159_phase3_common_gate.py
"""

import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg                       # noqa: E402
from scripts.lib import phase3_common as p3c                     # noqa: E402
from scripts.lib.stats import position_cluster_bootstrap          # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_REF = int(os.environ.get("N_REF", "500"))
N_PERM = int(os.environ.get("N_PERM", "1000"))

RHO_TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
RHO_TABLE_SHA = ("e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796")
TASK32 = ROOT / "data/processed/task32_analysis_table.csv"

# ---- A2-G1 targets: the planning doc's table, quoted, not recomputed ----
T_RHO_FULL = -0.088118064
T_RHO_H = -0.090021683
T_P_FULL = 2.0 / 79.0
T_P_H = 4.0 / 79.0
T_BEATERS_FULL = ["G_P254F"]
T_BEATERS_H = ["AV_195", "AV_220", "G_P254F"]
T_RHOMAD_FULL = -0.614188823
T_RHOMAD_H = -0.612696690
T_RA_FULL = -0.066425
T_RA_H = -0.068692
T_K_D9 = 2
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.0595113844951173
T_ROWS, T_POS, T_HPOS = 10757, 654, 455
T_NBGS, T_NN = 96, 78

TOL_9DP = 1e-9
TOL_6DP = 2e-6
TOL_12 = 1e-12
TOL_EXACT = 1e-15

t0 = time.time()
gates = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}", flush=True)
    return bool(ok)


def note(item, got, target, tol, fmt="{!r}"):
    d = abs(float(got) - float(target))
    return gate(item, d < tol,
                f"got {fmt.format(got)} target {fmt.format(target)} "
                f"|diff| = {d:.3e} (gate < {tol:g})")


def main():
    banner("A2 -- GATES FOR scripts/lib/phase3_common.py (script 159)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}   "
          f"N_PERM = {N_PERM}")
    print("RESAMPLING UNIT in this script: POSITION CLUSTERS (the anchor "
          "rho is inside one background).  No background-level resampling "
          "here.")
    print("DECISION RULE (pre-registered): any A2-G1 sub-gate FAIL -> the "
          "library is not trusted for GB1 or RBD, A4-A5 stop; exit 3.  "
          "Any A2-G2 sub-gate FAIL -> exit 3 as well.  Thresholds are "
          "never loosened; N is never raised to pass a gate.")
    if N_BOOT != 10000:
        print("*** SMOKE RUN: N_BOOT != 10000 -- sub-gate (k) CI "
              "reproduction is SKIPPED and A2-G1 cannot be called PASS "
              "on this run ***")

    # =====================================================================
    banner("TOY SELF-CHECKS of the generic library (hand-fixed expected "
           "values)", "-")
    # spearman +1 / -1
    a = np.arange(1.0, 11.0)
    s_pos = p3c.spearman(a, a)
    s_neg = p3c.spearman(a, a[::-1])
    gate("TOY spearman identity", abs(s_pos - 1.0) < TOL_12,
         f"got {s_pos!r} target 1.0 |diff| {abs(s_pos - 1.0):.3e}")
    gate("TOY spearman reversed", abs(s_neg + 1.0) < TOL_12,
         f"got {s_neg!r} target -1.0 |diff| {abs(s_neg + 1.0):.3e}")
    # p_spec, all three modes, hand-computed.  Note "neg" is INCLUSIVE:
    # nulls <= -1.0 counts both -3.0 and -1.0 itself (k = 2, p = 3/5).
    nulls = np.array([-3.0, -1.0, 0.5, 2.0])
    p_neg, k_neg, n_neg = p3c.p_spec(-1.0, nulls, mode="neg")
    p_pos, k_pos, _ = p3c.p_spec(-1.0, nulls, mode="pos")
    p_abs, k_abs, _ = p3c.p_spec(-1.0, nulls, mode="abs")
    gate("TOY p_spec neg", k_neg == 2 and n_neg == 4
         and abs(p_neg - 3.0 / 5.0) < TOL_EXACT,
         f"got p={p_neg!r} k={k_neg} n={n_neg}; target p=0.6 k=2 n=4 "
         "(nulls <= -1.0: -3.0 and -1.0)")
    gate("TOY p_spec pos", k_pos == 3 and abs(p_pos - 4.0 / 5.0) < TOL_EXACT,
         f"got p={p_pos!r} k={k_pos}; target p=0.8 k=3 "
         "(nulls >= -1.0: -1.0, 0.5, 2.0)")
    gate("TOY p_spec abs", k_abs == 3 and abs(p_abs - 4.0 / 5.0) < TOL_EXACT,
         f"got p={p_abs!r} k={k_abs}; target p=0.8 k=3 "
         "(|nulls| >= |-1.0|: -3.0, -1.0, 2.0)")
    # loo OLS on an exact line -> residuals ~0
    xx = np.linspace(0, 1, 12)
    yy = 3.0 + 2.0 * xx
    res = p3c.loo_ols_residuals(yy, xx)
    gate("TOY loo_ols exact line", np.max(np.abs(res)) < TOL_12,
         f"max|residual| = {np.max(np.abs(res)):.3e} (gate < 1e-12)")
    sl, ic, pr = p3c.ols_fit_predict(yy, xx, [10.0])
    gate("TOY ols_fit_predict", abs(sl - 2.0) < 1e-12 and abs(ic - 3.0) < 1e-12
         and abs(float(pr[0]) - 23.0) < 1e-12,
         f"slope={sl!r} intercept={ic!r} pred(10)={float(pr[0])!r}; "
         f"target 2.0, 3.0, 23.0")
    # background_boot on a constant -> every draw equals the constant
    const = np.full(17, 0.42)
    draws_c, nan_c = p3c.background_boot(const, None, n_boot=200, seed=SEED)
    gate("TOY background_boot constant",
         np.max(np.abs(draws_c - 0.42)) < TOL_12 and nan_c == 0,
         f"max|draw - 0.42| = {np.max(np.abs(draws_c - 0.42)):.3e}, "
         f"nan={nan_c}")
    # label_permutation_p: perfect monotone, neg mode -> p == 1.0 exactly;
    # abs mode -> at most the identity and full-reversal permutations can
    # reach |rho| = 1 with distinct values, so k <= 2 (a hand bound).
    y_pm = a.copy()
    p_neg_t, k_neg_t, n_neg_t = p3c.label_permutation_p(
        a, y_pm, n_perm=N_PERM, seed=SEED, mode="neg")
    p_abs_t, k_abs_t, _ = p3c.label_permutation_p(
        a, y_pm, n_perm=N_PERM, seed=SEED, mode="abs")
    gate("TOY label_perm neg p == 1.0",
         k_neg_t == N_PERM and abs(p_neg_t - 1.0) < TOL_EXACT,
         f"got p={p_neg_t!r} k={k_neg_t}/{N_PERM}; target k = N_PERM, "
         "p = 1.0 (no shuffle can exceed rho = 1.0)")
    gate("TOY label_perm abs bound",
         0 <= k_abs_t <= 2 and abs(p_abs_t - (1 + k_abs_t) / (1 + N_PERM)
                                   ) < TOL_EXACT,
         f"got p={p_abs_t!r} k={k_abs_t}; target 0 <= k <= 2 (with "
         "distinct values only the identity or the full reversal can reach "
         "|rho| = 1; p = (1+k)/(1+N_PERM) exactly)")
    print(f"  (abs-mode toy actual k = {k_abs_t} of {N_PERM} shuffles)")

    # =====================================================================
    banner("GATE A2-G1 -- the generic library reproduces Diagnostics "
           "II/IV's MTHFR numbers (HARD)", "-")

    # (a) input sha256
    sha = hashlib.sha256(RHO_TABLE.read_bytes()).hexdigest()
    gate("A2-G1(a) rho table sha256", sha == RHO_TABLE_SHA,
         f"{sha}  (target {RHO_TABLE_SHA})")

    # Build the cached construction (script 125's own path, imported)
    tb = time.time()
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    print(f"  [pdg.build] {time.time() - tb:.1f}s -- script 125's cached "
          "construction via scripts.lib.phase2_diag.build (imported, not "
          "reimplemented)")
    table = table.set_index("bg_id")
    bgs = list(A.bgs)
    N_ids = list(A.N_IDS)

    # (m) structure counts
    gate("A2-G1(m) n backgrounds", len(bgs) == T_NBGS,
         f"got {len(bgs)} target {T_NBGS}")
    gate("A2-G1(m) |N| = |V u G|", len(N_ids) == T_NN,
         f"got {len(N_ids)} target {T_NN}")
    arm_counts = table.arm.value_counts().to_dict()
    gate("A2-G1(m) arm counts",
         arm_counts == {"G": 40, "V": 38, "S": 18},
         f"got {arm_counts} target {{'G': 40, 'V': 38, 'S': 18}}")

    # (b) generic spearman == scipy on the anchor rows
    ar = A.a222v_rows
    ax, ay = ar.delta.to_numpy(float), ar.own_e_b.to_numpy(float)
    g_full = p3c.spearman(ax, ay)
    sc_full = float(spearmanr(ax, ay).statistic)
    gate("A2-G1(b) generic spearman == scipy (anchor full)",
         abs(g_full - sc_full) < TOL_12,
         f"generic {g_full!r} scipy {sc_full!r} |diff| "
         f"{abs(g_full - sc_full):.3e} (gate < 1e-12)")

    # (c) A222V rho full -- from task32's own columns, AND from 125's rows
    t32 = pd.read_csv(TASK32)
    m = t32[["delta_esm", "own_e_b", "position"]].notna().all(axis=1)
    t32r = t32[m]
    gate("A2-G1(m) task32 anchor rows / positions",
         len(t32r) == T_ROWS and t32r.position.nunique() == T_POS,
         f"got {len(t32r)} rows / {t32r.position.nunique()} positions; "
         f"target {T_ROWS} / {T_POS}")
    rho_t32 = p3c.spearman(t32r.delta_esm.to_numpy(float),
                           t32r.own_e_b.to_numpy(float))
    note("A2-G1(c) A222V rho full (task32 direct)", rho_t32, T_RHO_FULL,
         TOL_9DP)
    note("A2-G1(c) A222V rho full (script 125 rows)", g_full, T_RHO_FULL,
         TOL_9DP)
    gate("A2-G1(c) the two sources agree with each other",
         abs(rho_t32 - g_full) < TOL_12,
         f"|diff| {abs(rho_t32 - g_full):.3e} (AGENTS 5 column identity)")

    # (d) A222V rho H
    ah = ar[ar.position.isin(A.Hset)]
    rho_h = p3c.spearman(ah.delta.to_numpy(float),
                         ah.own_e_b.to_numpy(float))
    gate("A2-G1(m) H positions", len(A.Hset) == T_HPOS,
         f"got {len(A.Hset)} target {T_HPOS} "
         f"({len(ah)} anchor rows on H)")
    note("A2-G1(d) A222V rho H", rho_h, T_RHO_H, TOL_9DP)
    note("A2-G1(d) A222V rho H (pdg.point_rhos_H cross-check)",
         float(rho_a_H), T_RHO_H, TOL_9DP)

    # (e)/(f) p_spec through the generic API, on the CACHED rho table
    rho_nulls_full = table.loc[N_ids, "rho_full"].to_numpy(float)
    rho_nulls_H = table.loc[N_ids, "rho_H"].to_numpy(float)
    p_f, k_f, n_f = p3c.p_spec(g_full, rho_nulls_full, mode="neg")
    p_h, k_h, n_h = p3c.p_spec(rho_h, rho_nulls_H, mode="neg")
    beaters_f = sorted(table.loc[N_ids].index[
        rho_nulls_full <= g_full].tolist())
    beaters_h = sorted(table.loc[N_ids].index[
        rho_nulls_H <= rho_h].tolist())
    gate("A2-G1(e) p_spec(neg) full",
         abs(p_f - T_P_FULL) < TOL_EXACT and k_f == 1
         and beaters_f == T_BEATERS_FULL and n_f == T_NN,
         f"p = (1+{k_f})/(1+{n_f}) = {k_f + 1}/{n_f + 1} = {p_f!r} "
         f"target 2/79 = {T_P_FULL!r}; "
         f"k = {k_f} target 1; beaters {beaters_f} target "
         f"{T_BEATERS_FULL}")
    gate("A2-G1(f) p_spec(neg) H",
         abs(p_h - T_P_H) < TOL_EXACT and k_h == 3
         and beaters_h == T_BEATERS_H and n_h == T_NN,
         f"p = (1+{k_h})/(1+{n_h}) = {k_h + 1}/{n_h + 1} = {p_h!r} "
         f"target 4/79 = {T_P_H!r}; "
         f"k = {k_h} target 3; beaters {beaters_h} target {T_BEATERS_H}")

    # mean|delta| per background -- script 125's usable rows (imported)
    mad = {"full": {}, "H": {}}
    mad_a = {}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    for view in ("full", "H"):
        ra = ar if view == "full" else ah
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    # (g)/(h) Spearman(rho_b, mean|delta|) over the 96 backgrounds
    RHO = {"full": table.loc[bgs, "rho_full"].to_numpy(float),
           "H": table.loc[bgs, "rho_H"].to_numpy(float)}
    M96 = {"full": np.array([mad["full"][b] for b in bgs]),
           "H": np.array([mad["H"][b] for b in bgs])}
    rhomad = {v: p3c.spearman(RHO[v], M96[v]) for v in ("full", "H")}
    note("A2-G1(g) Spearman(rho_b, mean|delta|) full", rhomad["full"],
         T_RHOMAD_FULL, TOL_9DP)
    note("A2-G1(h) Spearman(rho_b, mean|delta|) H", rhomad["H"],
         T_RHOMAD_H, TOL_9DP)

    # (i)/(j) D9 PRIMARY: LOO residuals on N, r_A from the fit on all N
    rho_A = {"full": g_full, "H": rho_h}
    d9 = {}
    for view in ("full", "H"):
        y = np.array([float(table.loc[b, "rho_" + view]) for b in N_ids])
        x = np.array([mad[view][b] for b in N_ids])
        r_b = p3c.loo_ols_residuals(y, x)          # D9 primary, generic API
        _, _, predA = p3c.ols_fit_predict(y, x, [mad_a[view]])
        r_A = rho_A[view] - float(predA[0])
        k = int(np.sum(r_b <= r_A))
        beat = sorted(np.array(N_ids)[r_b <= r_A].tolist())
        d9[view] = dict(r_A=r_A, k=k, beat=beat)
        print(f"  [{view}] D9 primary: r_A = {r_A!r}, k = {k} of {len(N_ids)}, "
              f"beaters {beat} (script 140 recorded beaters "
              f"['AV_220', 'AV_85'] -- printed, not gated here)")
    note("A2-G1(i) D9 primary r_A full", d9["full"]["r_A"], T_RA_FULL,
         TOL_6DP)
    gate("A2-G1(i) D9 primary k (full)", d9["full"]["k"] == T_K_D9,
         f"got {d9['full']['k']} target {T_K_D9}")
    note("A2-G1(j) D9 primary r_A H", d9["H"]["r_A"], T_RA_H, TOL_6DP)
    gate("A2-G1(j) D9 primary k (H)", d9["H"]["k"] == T_K_D9,
         f"got {d9['H']['k']} target {T_K_D9}")

    # (l) column identity: cached table vs script 125's own recomputation
    diff_full = float(np.max(np.abs(
        table.loc[bgs, "rho_full"].to_numpy(float)
        - np.array([float(A.point[b]) for b in bgs]))))
    diff_H = float(np.max(np.abs(
        table.loc[bgs, "rho_H"].to_numpy(float)
        - np.array([float(point_h[b]) for b in bgs]))))
    gate("A2-G1(l) rho table == script 125 (rho_full, rho_H)",
         diff_full < TOL_9DP and diff_H < TOL_9DP,
         f"max|diff| full = {diff_full:.3e}, H = {diff_H:.3e} "
         "(gate < 1e-9 each)")

    # (k) the corrected CI on the unrestricted anchor
    if N_BOOT == 10000:
        tb = time.time()
        draws_mine = p3c.pos_cluster_boot(ax, ay, ar.position.to_numpy(),
                                          n_boot=N_BOOT, seed=SEED)
        lo_m, hi_m, nf = p3c.pct_ci(draws_mine)
        t_ci = time.time() - tb
        print(f"  [generic pos_cluster_boot] N_BOOT={N_BOOT} seed={SEED} "
              f"in {t_ci:.1f}s over {nf} finite draws; observed point = "
              f"{g_full!r}")
        note("A2-G1(k) corrected CI lo", lo_m, T_CI_LO, TOL_9DP)
        note("A2-G1(k) corrected CI hi", hi_m, T_CI_HI, TOL_9DP)

        tb = time.time()
        r1 = position_cluster_bootstrap(ar, "position", "delta", "own_e_b",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"  [Phase 1's own routine, imported unmodified] in "
              f"{time.time() - tb:.1f}s: CI = [{r1['ci_lo']!r}, "
              f"{r1['ci_hi']!r}], observed = {r1['observed_rho']!r}, "
              f"n_rows = {r1['n_rows']}, n_clusters = {r1['n_clusters']}")
        note("A2-G1(k) Phase 1 routine CI lo", r1["ci_lo"], T_CI_LO, TOL_9DP)
        note("A2-G1(k) Phase 1 routine CI hi", r1["ci_hi"], T_CI_HI, TOL_9DP)
        gate("A2-G1(k) generic CI == Phase 1 routine CI",
             abs(lo_m - float(r1["ci_lo"])) < TOL_12
             and abs(hi_m - float(r1["ci_hi"])) < TOL_12,
             f"max|diff| lo = {abs(lo_m - float(r1['ci_lo'])):.3e}, "
             f"hi = {abs(hi_m - float(r1['ci_hi'])):.3e} (gate < 1e-12)")
    else:
        gate("A2-G1(k) corrected CI on the unrestricted anchor",
             False,
             f"SKIPPED (smoke): N_BOOT={N_BOOT} != 10000 -- A2-G1 cannot "
             "be called PASS on this run; run with N_BOOT=10000")

    # =====================================================================
    banner("GATE A2-G2 -- reference bootstrap, draw by draw (HARD)", "-")
    x_a, y_a, pos_a = ax, ay, ar.position.to_numpy()

    def two_stage(label, x_, y_, cl_):
        point = p3c.spearman(x_, y_)
        nk = p3c._first_appearance_labels(cl_).size
        ids_one = np.arange(nk, dtype=np.int64)[None, :]  # every cluster once
        one_c = p3c.pos_cluster_boot_from_ids(x_, y_, cl_, ids_one)
        one_r = p3c.reference_boot(x_, y_, cl_, ids_one)
        gate(f"A2-G2(i) identity, {label}",
             abs(float(one_c[0]) - point) < TOL_12
             and abs(float(one_r[0]) - point) < TOL_12,
             f"every-cluster-once corrected {float(one_c[0])!r}, "
             f"reference {float(one_r[0])!r}, point {point!r}; "
             f"max|diff| = "
             f"{max(abs(float(one_c[0]) - point), abs(float(one_r[0]) - point)):.3e} "
             "(gate < 1e-12)")
        ids, _ = p3c.draw_ids(cl_, n_draw=N_REF, seed=SEED)
        d_c = p3c.pos_cluster_boot_from_ids(x_, y_, cl_, ids)
        d_r = p3c.reference_boot(x_, y_, cl_, ids)
        md = float(np.max(np.abs(d_c - d_r)))
        gate(f"A2-G2(ii/iii) draw-by-draw, {label}", md < TOL_12,
             f"{N_REF} draws, max|corrected - reference| = {md:.3e} "
             "(gate < 1e-12)")

    two_stage("(ii) ANCHOR ROWS", x_a, y_a, pos_a)

    # (iii) restricted set: remove a seed-SEED sample of 200 positions
    uniq_pos = np.unique(pos_a)
    rng_rm = np.random.default_rng(SEED)
    removed = set(rng_rm.choice(uniq_pos, 200, replace=False).tolist())
    keep_m = ~np.isin(pos_a, list(removed))
    print(f"  [restricted set] removed {len(removed)} positions "
          f"(seed {SEED}); kept {int(keep_m.sum())} rows at "
          f"{np.unique(pos_a[keep_m]).size} positions")
    two_stage("(iii) RESTRICTED (positions removed)",
              x_a[keep_m], y_a[keep_m], pos_a[keep_m])

    # =====================================================================
    banner("A2 GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    n_skip = sum(1 for _, ok, d in gates if not ok and "SKIPPED" in d)
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    smoke = N_BOOT != 10000
    print(f"\n  {len(gates) - n_fail}/{len(gates)} checks PASS, "
          f"{n_fail} FAIL ({n_skip} of the FAILs are smoke SKIPS).")
    print("\nLIMITATIONS (printed, per AGENTS 6): this gate REPRODUCES "
          "cached Phase 1/2 numbers through the new generic API -- it "
          "validates the library code (reproduction is not replication, "
          "AGENTS 6), it is not independent evidence for any claim, and it "
          "produces no new inference.  The bootstrap it exercises "
          "resamples POSITION CLUSTERS only.  The corrected routine is "
          "imported from scripts/lib/phase2_diag4.py (unmodified); script "
          "144's routine is never used.  A smoke run (N_BOOT != 10000) "
          "cannot PASS A2-G1 because sub-gate (k) is skipped.")
    if n_fail:
        if smoke and n_fail == n_skip:
            print("\nSMOKE RESULT: all executed sub-gates PASS; the only "
                  "FAIL is the intentional CI SKIP.  A2-G1/A2-G2 are "
                  "decided on the N_BOOT=10000 run.")
            print(f"Elapsed {time.time() - t0:.1f}s")
            sys.exit(0)
        print("\nGATE FAIL -- A2 stops here.  The library is not trusted "
              "for GB1 or RBD (A4-A5 stop).  Do not raise N, do not "
              "adjust a threshold.")
        print(f"Elapsed {time.time() - t0:.1f}s")
        sys.exit(3)
    print("\nGATE PASS -- A2-G1 and A2-G2 both pass; the generic library "
          "is trusted for the M1/GB1/RBD analyses per the planning doc's "
          "Task A2 decision rule.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
