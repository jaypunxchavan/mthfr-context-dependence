"""Script 167 -- Task A4, Module M: mechanism-matched analyses
(docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md Task A4, implementing
docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md exactly).

PRE-REGISTRATION: this docstring was written BEFORE the first run of this
script and is not edited after any Phase 4 number exists (AGENTS 6).  The
frozen block's sha256
8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b and its
56 lines are re-checked at startup (G-M0) and the whole frozen file is
re-printed verbatim from disk at runtime, so the rules this script applies
cannot drift from the file.  The frozen file is read-only and is never
edited.  Per its section 0/5 nothing here changes any frozen Phase 1/2
result, and no result here may be described as confirming or undermining a
GB1, RBD, neighbour-arm or model-ladder result.

WHAT THIS SCRIPT IS: cached data only.  No torch / esm / thermompnn is
imported anywhere (PHASE4 rule 1); no model is scored; no network is used.
It writes nothing except this script and, by the caller's redirect,
docs/tasks/phase4-strengthening/PHASE4_A4_{SMOKE,FULL}_OUTPUT.txt.

SOURCES QUOTED VERBATIM AT RUNTIME with file names and line numbers, read
from disk so a quote cannot drift from the code:
  * rebuild_interaction_fit (the project's own two-pass own-context fit,
    UNMODIFIED -- the simulation calls it through phase4_common)
        scripts/lib/stats_ext.py   lines 63-88
  * the weighted aggregation of per-condition residuals
        wls_line                   scripts/lib/own_context.py lines 48-66
        fit_interaction            scripts/lib/own_context.py lines 143-187
  * the sign sentence of Module S (PHASE4 line 241: state it wherever a
    rho is discussed)
        docs/tasks/phase4-strengthening/SIGN_CONVENTION.md  lines 6-15

IMPORTED, NEVER RE-DERIVED (AGENTS 2): script 125's cached construction
(`pdg.build`, `pdg.rho_table`, `pdg.usable_rows`), the D3 loader
(`p3d.parse_pdb_float64`, `p3d.d3_of`), Phase 1/3 statistics
(`p3c.p_spec`, `p3c.ols_fit_predict`, `p3c.loo_ols_residuals`) and the A2
library `phase4_common` (partial Spearman, stratified Spearman,
decomposition, permutation, simulation harness, planting, power curve,
whole-placebo bootstrap and every frozen outcome-word function).  New
machinery that phase4_common does not carry (the position-cluster draw loop
for a CUSTOM statistic, and its slow scipy reference) lives in THIS script,
not in scripts/lib (AGENTS 7: scripts/lib is never edited).

PRE-REGISTERED DECISIONS (M-DEC1..M-DEC9; each interprets the frozen text
and changes no frozen constant; all nine are printed in the run output
BEFORE the first M draw exists):
  M-DEC1 (frozen M-3, sw_i).  The raw atlas carries only PER-CONDITION
      WT-arm standard errors (w12.se, w25.se, w100.se, w200.se).  It does
      NOT carry an SE of the fitted scalar w_i = fit["w"]["fitness"], which
      is the quantity frozen M-3 perturbs ("w^sim_i = w_i + N(0, sw_i^2)").
      The per-condition columns therefore do NOT qualify as "the
      per-variant WT-background standard error" in M-3's sense.
      CONSEQUENCE: PRIMARY sw_i = 0 exactly as the frozen fallback says,
      and the SENSITIVITY is the frozen block's own alternative sw_i = the
      median m_se over the frame (pooled over frame rows x 4 conditions).
      The sensitivity's noise is applied per condition cell by
      phase4_common.zero_epistasis_draw (independent N(0,1) per cell x
      sw_i); the frozen text writes one scalar draw per variant.  The two
      differ only where sw_i > 0, i.e. only in the sensitivity; with
      sw_i = 0 (PRIMARY) w_sim == w identically.  Stated here, before any
      M draw.
  M-DEC2 (frozen M-3, the linear sensitivity).  "Sensitivity: the
      generating relation linear (E_c^lin)" = e2["expected"], the project's
      own linear expectation straight from rebuild_interaction_fit -- i.e.
      script 153's identity plug-in ("the project's own linear
      expectation").  Script 153's GE-LIN-CF is NAMED HERE AS THE
      ALTERNATIVE THAT IS NOT RUN: running it would change the
      cross-fitting and the functional shape at the same time, so it could
      not be attributed to linearity.  One sensitivity, one change.
  M-DEC3 (frozen M-3/M-4, the draw loop).  phase4_common.simulate_rho
      cannot be called on the real data: it passes delta straight to
      `spearman`, whose rankdata propagates a single NaN (verified:
      rankdata([1, nan, 3, 4]) -> four NaNs), while delta exists only on
      the 10,757 frame rows and G-M4 forces the pipeline onto all 13,134
      raw rows (a frame+reference-only rebuild misses the recorded
      own_e.b by up to 3.3e-1 on every row -- measured; and p.Ala222Val at
      raw index 3010 is absent from task32, so a partial rebuild crashes).
      THIS SCRIPT therefore runs simulate_rho's own draw loop, in
      simulate_rho's exact rng order (u first when r0 is given, then the
      w-noise draw, then the m-noise draw), calling
      p4c.zero_epistasis_draw and p4c.own_eb_from_arrays UNMODIFIED, and
      computes rho on the rows where both delta_real and own_e.b^sim are
      finite.  This is a wrapper-level deviation, disclosed here and in the
      output; no frozen constant, no library function and no rng stream is
      changed.
  M-DEC4 (frozen M-4, planting).  z = rank_normal_z of delta over the
      10,757 frame rows and 0 on the 2,377 off-frame raw rows (so z has one
      entry per raw row); u ~ N(0,1) is drawn for EVERY raw row on every
      draw, which keeps simulate_rho's rng stream intact; s_e = the SD of
      the recorded own_e.b over the frame rows, ddof = 0.  A plant on an
      off-frame row can reach frame rows only through the shared
      correction curves (disclosed).  At r0 = 0 the frozen formula gives
      e_plant = s_e * u -- pure independent noise of the right SD, NOT a
      zero plant; it is implemented literally, as frozen.
  M-DEC5 (frozen M-2, deciles).  The deciles of S_W are computed ONCE over
      the full frame's S_W (p4c.equal_count_bins, 10 bins); every
      background's rows and the H view inherit those frame-level labels
      through their row alignment.  No view and no background re-cuts its
      own deciles.
  M-DEC6 (frozen G-M5, planting response).  The monotonicity rule,
      pre-registered before the grid is run: with the 9 grid means sorted
      by r0 ascending, EVERY one of the 8 adjacent pairs must satisfy
      mean[j] >= mean[i] - 2*sqrt(SE_i^2 + SE_j^2), where SE = sd/sqrt(n)
      of that band's observed rhos (sd ddof = 1).  All 8 pairs must pass;
      otherwise G-M5 fails and the script exits 3.  (The frozen text says
      "up to Monte-Carlo error"; 2 combined SEs is this script's fixed
      reading of that phrase, fixed here, not after seeing the grid.)
  M-DEC7 (frozen M-5, S2 groups).  3D distance to residue 222 is a
      POSITION-level quantity, so the "10 equal-count bins of 3D distance
      ... over the resolved positions" are computed over the DISTINCT
      resolved frame positions (one d3 value per position, equal-count
      over those positions); unresolved positions form the eleventh bin
      (label 10) and every row inherits its position's bin.  d3 comes from
      the D3 loader on data/raw/6FCX.pdb, NEVER imputed.
  M-DEC8 (frozen M-3 thresholds).  The fraction, the ratio and the
      outcome word all use the frozen literal -0.088118 exactly as the
      block writes it; the full-precision recomputed anchor
      (-0.08811806424891734) is printed beside every use.
  M-DEC9 (draw streams).  Each simulation run -- one per M-3 variant and
      one per r0 grid point -- is one simulate_rho-equivalent call and gets
      its OWN np.random.default_rng(SEED) stream; S1 and S2 each get their
      own default_rng(SEED) stream.  The bootstrap draw ids come from the
      imported p4c.draw_ids (same stream as every other Phase 4 script).

REPORT-SET DECISIONS (also printed before the analyses):
  * M-1 CIs are computed for BOTH controls x BOTH views of the A222V
    partial; the frozen word uses the PRIMARY control's full-frame CI.
    p_spec(neg), p_spec(abs) and p_spec_adj are reported for both
    controls; the word uses the primary control's p_spec(neg).
  * M-5's position-cluster CIs are computed for BOTH views of BOTH
    components (both components recomputed per resample); the frozen word
    uses the full-frame values.
  * M-6: the per-view probability behind the word is P(p_spec <= 0.05) on
    the full frame and P(p_spec <= 0.10) on H, exactly as the block
    writes them.
  * Nothing is reported outside the frozen words: M-2 and M-4 carry no
    word, the M-3 sensitivities carry no word, M-1's secondary control
    carries no word.

GATES (ALL HARD; a failure prints GATE FAIL and the script exits 3; the
driver never retries exit 3; thresholds are never loosened and N is never
raised to pass a gate).  G-M0..G-M7 are the frozen block's gates, verbatim;
G-XFOLD and G-ALIGN are EXTRA gates pre-registered here (stricter than the
frozen text, never looser) and the whole-placebo reference is capped at
min(N_REF, 50) draws for runtime, disclosed in its own gate line.
  G-M0  inputs: frozen prereg sha256 + 56 lines; rho-table sha256
        e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796;
        3D-table sha256
        69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de;
        6FCX.pdb sha256 95133130645cead0252d05b6ce9ddd578164cbc856ac1c82d1a6bb15e4148fbf;
        script 153 sha256 e9fd90aff973be1c03dcfa15c80298f5cd54df4dbf5775a41de1839adf0b5133;
        m1_own_e_b_ge.csv sha256 0dd63b4acfabee2e299b5c184ff649d4b27c2c914978acd1f15b0e0550e44523;
        m1_fitted_expectations.csv sha256 e353330dd4541d672517238ac148160431e6aa7d4a2b20ddd44f15f6252d9915;
        structure: 96 backgrounds, |N| = 78, arms G40/V38/S18, frame
        10,757 rows / 654 positions, H = 455 positions / 7,526 rows, 67
        resolved nulls; and the D3 loader reproduces the stored d3_CA of
        all 67 resolved nulls to 1e-6.
  G-M1  A222V rho -0.088118064 (full) / -0.090021683 (H), each from two
        independent sources agreeing with each other to 1e-12; p_spec 2/79
        (k = 1, beaters {G_P254F}) and 4/79 (k = 3, beaters
        {AV_195, AV_220, G_P254F}), both exact.
  G-M2  the Phase 1 partials reproduce: the linear rank partial controlling
        S_W = -0.06414804421216103 (< 1e-12) and the two-covariate linear
        rank partial rounds to -0.0829 (4 dp).
  G-M3  bootstrap identity (every position exactly once reproduces each
        point estimate: the anchor rho, the A222V partial, the stratified
        rho, both decomposition components, < 1e-12); draw-by-draw
        agreement at 1e-12 of each fast path with its own slow reference
        (closed-form partial from scipy pairwise ranks; scipy stratified;
        scipy decomposition; the imported pos_cluster_boot_from_ids vs
        reference_boot; whole_placebo_boot_from_ids vs
        whole_placebo_reference on min(N_REF,50) identical id rows); and,
        at N_BOOT = 10000, Phase 1's published CI
        [-0.1173334458953319, -0.0595113844951173] reproduced endpooint-by-
        endpoint (< 1e-9) with the imported routine.  SKIPPED (non-fatal,
        explicitly marked) when N_BOOT != 10000; such a run cannot call
        G-M3 PASS.
  G-M4  simulation identity: with every noise term zero (sw = 0 and
        m_noise = zeros, the recorded m_se left in place as the WEIGHT
        column) and E_c replaced by the observed m, the unmodified
        pipeline returns the recorded own_e.b (< 1e-12 over the 10,757
        recorded rows, zero recorded rows missing); PLUS every M-3 and M-4
        draw keeps exactly 10,757 rows (one gate line per run).
  G-M5  planting response: M-DEC6's rule over all 8 adjacent pairs.
  G-M6  toy gates for the stratified statistic and for the decomposition
        (hand-built expectations, not taken from a prior run).
  G-M7  the whole-placebo bootstrap with every position exactly once
        returns the observed p_spec and k: k = 1, p = 2/79, rho_A =
        -0.088118064 (full); k = 3, p = 4/79, rho_A = -0.090021683 (H).
  G-XFOLD (extra)  the transcribed 5-fold isotonic construction reproduces
        script 153's saved output: fold vector exact; aggregate(E_iso) vs
        saved own_e_b_ge_iso max|diff| < 1e-12 with zero NaN
        disagreements; all 20 (condition, fold) isotonic transition lists
        vs m1_fitted_expectations.csv max|diff| < 1e-12.
  G-ALIGN (extra, AGENTS 5)  script 125's own score join is re-run for all
        96 backgrounds and gated rowwise against A.bg_rows (position
        exact, own_e_b exact, recomputed delta < 1e-12, recomputed
        rho_full and rho_H == A.point / the cached table to 1e-12); the
        97 x n delta matrix used by M-6 must reproduce every cached rho_b
        (full and H) to 1e-12 and row 0 must equal the frame's delta.

RESAMPLING UNITS (PHASE4 rule 7; printed in the output as well):
  * Everything inside one background (the anchor rho, the partial, the
    stratified rho, the decomposition components, their CIs and G-M3):
    POSITION CLUSTERS -- never rows (effective n is 654 positions, not
    10,757 variants).
  * The whole-placebo test (M-6): positions, with every background's rho_b
    re-derived on the resampled rows each draw (a re-derivation null).
  * Across backgrounds: never resampled here -- p_spec is an exact rank
    count over the 78 fixed nulls; no background-level CI is produced in
    this module.
  * S1/S2 (M-5 surrogate nulls) and M-3/M-4 are SIMULATION / RE-LABELLING
    loops, not bootstraps: they carry no resampling unit, and they are
    reported as distributions, not as CIs.
  Bootstrap p-values are the primary claim wherever the block asks for
  one; the frozen M-6 z is printed because the block asks for it and is
  LABELLED illustrative scale context only (AGENTS 3); effect sizes are
  printed beside every significance claim.

SMOKE RULE: N_BOOT != 10000 or N_SIM < 1000 or N_PLANT < 200 or
N_PERM < 1000 or N_STAB < 2000 makes this a SMOKE run: the output says so,
every frozen word computed on it is marked PROVISIONAL, and G-M3's Phase 1
CI sub-gate prints SKIPPED.  The record is the full run.

LIMITATIONS (printed again with the output, AGENTS 6):
  * Reproduction is not replication: G-M0..G-M4 / G-XFOLD / G-ALIGN
    re-derive cached project numbers to validate this code -- a unit test,
    not independent evidence for any claim.
  * The frozen block's own section 0: these constructions use quantities
    seen in earlier exploratory work; they are NOT independent of what was
    already seen.  Out-of-sample evidence in this programme comes only
    from the neighbour-arm and model-ladder pre-registrations.
  * p_spec / p_spec_adj are one-sided signed rank counts over 78 nulls,
    not tail areas of an exchangeable distribution.
  * M-3/M-4 re-run the project's own estimator on simulated inputs (a
    re-derivation null, AGENTS 4) and inherit every assumption of that
    estimator, including the multiplicative no-interaction expectation.
  * M-5's S1/S2 re-label own_e.b within groups; they preserve position
    structure (S1) or the regional distance profile (S2) and nothing else.
  * The anchor frame is one background (the A222V arm); every CI here
    resamples 654 (or 455) positions, never rows.

Usage:
  smoke:  N_BOOT=300 N_SIM=100 N_PLANT=100 N_PERM=100 N_STAB=100 \
            N_REF=100 venv/bin/python3 scripts/167_mech_anchor.py \
            > docs/tasks/phase4-strengthening/PHASE4_A4_SMOKE_OUTPUT.txt
  full:   SEED=0 venv/bin/python3 scripts/167_mech_anchor.py \
            > docs/tasks/phase4-strengthening/PHASE4_A4_FULL_OUTPUT.txt
          (defaults are the frozen values: N_BOOT 10000, N_SIM 1000,
           N_PLANT 200, N_PERM 1000, N_STAB 2000, N_REF 500)
"""

import hashlib
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr as _spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib import phase2_diag as pdg                             # noqa
from scripts.lib import phase2_diag3 as p3d                            # noqa
from scripts.lib import phase3_common as p3c                           # noqa
from scripts.lib import phase4_common as p4c                           # noqa
from scripts.lib.own_context import (CONCS, MT_SCORE_COLS, MT_SE_COLS, # noqa
                                     WT_SCORE_COLS, WT_SE_COLS, wls_line)
from scripts.lib.stats_ext import rebuild_interaction_fit              # noqa
from sklearn.isotonic import IsotonicRegression                        # noqa

# ---------------------------------------------------------------------------
# Environment (frozen defaults; smoke values are set by the caller's env)
# ---------------------------------------------------------------------------
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_REF = int(os.environ.get("N_REF", "500"))
N_SIM = int(os.environ.get("N_SIM", "1000"))
N_PLANT = int(os.environ.get("N_PLANT", "200"))
N_PERM = int(os.environ.get("N_PERM", "1000"))
N_STAB = int(os.environ.get("N_STAB", "2000"))
N_REF_PLACEBO = min(int(N_REF), 50)          # disclosed cap (M-DEC7 gates)
N_FOLDS = 5

SMOKE = (N_BOOT != 10000 or N_SIM < 1000 or N_PLANT < 200
         or N_PERM < 1000 or N_STAB < 2000)

# ---------------------------------------------------------------------------
# Paths and frozen input hashes / targets (printed beside every value)
# ---------------------------------------------------------------------------
PREREG = ROOT / "docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md"
PREREG_SHA = ("8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b")
PREREG_LINES = 56
SIGN_NOTE = ROOT / "docs/tasks/phase4-strengthening/SIGN_CONVENTION.md"
RHO_TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
RHO_TABLE_SHA = ("e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796")
D3_TABLE = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
D3_TABLE_SHA = ("69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de")
PDB_PATH = ROOT / "data/raw/6FCX.pdb"
PDB_SHA = ("95133130645cead0252d05b6ce9ddd578164cbc856ac1c82d1a6bb15e4148fbf")
S153 = ROOT / "scripts/153_m1_ge_target.py"
S153_SHA = ("e9fd90aff973be1c03dcfa15c80298f5cd54df4dbf5775a41de1839adf0b5133")
M1_GEO = ROOT / "data/processed/phase3/m1_own_e_b_ge.csv"
M1_GEO_SHA = ("0dd63b4acfabee2e299b5c184ff649d4b27c2c914978acd1f15b0e0550e44523")
M1_FIT = ROOT / "data/processed/phase3/m1_fitted_expectations.csv"
M1_FIT_SHA = ("e353330dd4541d672517238ac148160431e6aa7d4a2b20ddd44f15f6252d9915")
STATS_EXT = ROOT / "scripts/lib/stats_ext.py"
OWN_CONTEXT = ROOT / "scripts/lib/own_context.py"
RAW_PATH = ROOT / "data/raw/mthfrModel/results/folate_response_model5.csv"
T32_PATH = ROOT / "data/processed/task32_analysis_table.csv"

# ---- frozen / Phase 1 targets, printed beside every recomputed value ----
T_RHO_FULL = -0.088118064            # 9 dp (G-M1)
T_RHO_H = -0.090021683               # 9 dp (G-M1)
T_ANCHOR_LIT = -0.088118             # the frozen literal (M-DEC8)
T_RHO_FULL_PREC = -0.08811806424891734
T_P_FULL = 2.0 / 79.0
T_P_H = 4.0 / 79.0
T_BEATERS_FULL = ["G_P254F"]
T_BEATERS_H = ["AV_195", "AV_220", "G_P254F"]
T_PARTIAL_SW = -0.06414804421216103  # G-M2, 1e-12
T_PARTIAL_2COV_4DP = -0.0829         # G-M2, 4 dp
T_CI_LO = -0.1173334458953319        # G-M3 Phase 1 CI
T_CI_HI = -0.0595113844951173
T_ROWS, T_POS, T_HPOS, T_HROWS = 10757, 654, 455, 7526
T_NBGS, T_NN, T_RESN = 96, 78, 67
T_ARMS = {"G": 40, "V": 38, "S": 18}
R0_GRID = [-0.30, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30]

TOL_12 = 1e-12
TOL_9DP = 1e-9
TOL_6DP = 1e-6
TOL_EXACT = 1e-15

t0 = time.time()
gates = []


class GateFail(Exception):
    pass


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail, hard=True):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}", flush=True)
    if not ok and hard:
        raise GateFail(gid)
    return bool(ok)


def note(item, got, target, tol, fmt="{!r}"):
    d = abs(float(got) - float(target))
    return gate(item, d < tol,
                f"got {fmt.format(got)} target {fmt.format(target)} "
                f"|diff| = {d:.3e} (gate < {tol:g})")


def quote(path, start, end, label):
    lines = path.read_text().splitlines()
    print(f"\n  --- {label}: {path.relative_to(ROOT)} lines {start}-{end} "
          f"(verbatim from disk) ---")
    for i in range(start, end + 1):
        print(f"  {i:4d}| {lines[i-1]}")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Closed-form partial correlations (independent arithmetic for G-M3's
# reference path; the same two formulas script 165 gate A2-G3 used)
# ---------------------------------------------------------------------------
def _closed_partial_1cov(r_xy, r_xz, r_yz):
    return (r_xy - r_xz * r_yz) / np.sqrt((1 - r_xz ** 2) * (1 - r_yz ** 2))


def _closed_partial_2cov(rxy, rx1, rx2, ry1, ry2, r12):
    Rzz = np.array([[1.0, r12], [r12, 1.0]])
    inv = np.linalg.inv(Rzz)
    xz = np.array([rx1, rx2])
    zy = np.array([ry1, ry2])
    num = rxy - xz @ inv @ zy
    dx2 = 1.0 - xz @ inv @ xz
    dy2 = 1.0 - zy @ inv @ zy
    return float(num / np.sqrt(dx2 * dy2))


def ref_partial(x, y, ctrls, idx):
    """SLOW reference for p4c.partial_spearman on rows `idx`.

    Independent arithmetic: pairwise scipy.stats.spearmanr coefficients and
    the closed-form partial (1 control: the 3-coefficient formula; 2
    controls: the matrix-inversion formula) instead of the library's
    rank-residualisation.  Rows are rebuilt by the caller with flatnonzero,
    so an indexing bug cannot cancel between the two paths.
    """
    x = np.asarray(x, dtype=float)[idx]
    y = np.asarray(y, dtype=float)[idx]
    Cs = [np.asarray(c, dtype=float)[idx] for c in ctrls]

    def sp(a, b):
        return float(_spearmanr(a, b).statistic)

    r_xy = sp(x, y)
    if len(Cs) == 1:
        return _closed_partial_1cov(r_xy, sp(x, Cs[0]), sp(y, Cs[0]))
    if len(Cs) == 2:
        return _closed_partial_2cov(r_xy, sp(x, Cs[0]), sp(x, Cs[1]),
                                    sp(y, Cs[0]), sp(y, Cs[1]),
                                    sp(Cs[0], Cs[1]))
    raise ValueError("ref_partial supports 1 or 2 controls")


def ref_stratified(x, y, strata, idx):
    """SLOW reference for p4c.stratified_spearman (scipy per stratum)."""
    x = np.asarray(x, dtype=float)[idx]
    y = np.asarray(y, dtype=float)[idx]
    s = np.asarray(strata)[idx]
    num, den = 0.0, 0.0
    for g in np.unique(s):
        m = s == g
        if int(m.sum()) < 3:
            continue
        r = float(_spearmanr(x[m], y[m]).statistic)
        if not np.isfinite(r):
            continue                      # decision I1: drop, renormalise
        num += float(m.sum()) * r
        den += float(m.sum())
    return num / den if den > 0 else float("nan")


def ref_decomposition(x, y, positions, idx, min_rows=5):
    """SLOW reference for p4c.between_within_decomposition (scipy per
    position; decision I2's finite-row / min_rows semantics)."""
    x = np.asarray(x, dtype=float)[idx]
    y = np.asarray(y, dtype=float)[idx]
    p = np.asarray(positions)[idx]
    uniq = np.unique(p)
    means_x, means_y, rhos, counts = [], [], [], []
    for u in uniq:
        m = p == u
        xx, yy = x[m], y[m]
        f = np.isfinite(xx) & np.isfinite(yy)
        xx, yy = xx[f], yy[f]
        counts.append(int(xx.size))
        means_x.append(float(xx.mean()) if xx.size else np.nan)
        means_y.append(float(yy.mean()) if yy.size else np.nan)
        if xx.size >= 3:
            rhos.append(float(_spearmanr(xx, yy).statistic))
        else:
            rhos.append(np.nan)
    counts = np.asarray(counts)
    qualifies = counts >= int(min_rows)
    q = qualifies & np.isfinite(means_x) & np.isfinite(means_y)
    rho_between = (float(_spearmanr(np.asarray(means_x)[q],
                                    np.asarray(means_y)[q]).statistic)
                   if int(q.sum()) >= 3 else float("nan"))
    keep = q & np.isfinite(np.asarray(rhos))
    if keep.any():
        w = counts[keep].astype(float)
        rho_within = float((w * np.asarray(rhos)[keep]).sum() / w.sum())
    else:
        rho_within = float("nan")
    return np.array([rho_between, rho_within], dtype=float)


# ---------------------------------------------------------------------------
# Position-cluster draws for a CUSTOM statistic (fast path + slow reference)
# ---------------------------------------------------------------------------
def cluster_draws(pos, stat, n_draw, seed):
    """Draw ids from the imported p4c.draw_ids and evaluate `stat(idx)`.

    RESAMPLING UNIT: position clusters, multiplicity included.
    Returns (draws, ids, labels) where draws has shape (n_draw,) or
    (n_draw, k) depending on what `stat` returns.
    """
    ids, labels = p4c.draw_ids(pos, n_draw, seed)
    rows_of = {lab: np.flatnonzero(np.asarray(pos) == lab) for lab in labels}
    out = []
    for i in range(len(ids)):
        idx = np.concatenate([rows_of[labels[s]] for s in ids[i]])
        out.append(np.atleast_1d(np.asarray(stat(idx), dtype=float)))
    return np.array(out, dtype=float), ids, labels


def cluster_reference(pos, stat, ids, labels):
    """SLOW reference: rebuilds cluster -> rows with flatnonzero per draw."""
    pos = np.asarray(pos)
    out = []
    for i in range(len(ids)):
        idx = np.concatenate([np.flatnonzero(pos == labels[s])
                              for s in ids[i]])
        out.append(np.atleast_1d(np.asarray(stat(idx), dtype=float)))
    return np.array(out, dtype=float)


def one_draw(pos, labels, stat):
    """Every position exactly once (the identity draw), same row order rule
    as cluster_draws: first-appearance label order, multiplicity 1."""
    idx = np.concatenate([np.flatnonzero(np.asarray(pos) == lab)
                          for lab in labels])
    return np.atleast_1d(np.asarray(stat(idx), dtype=float))


# ---------------------------------------------------------------------------
# The simulation run (frozen M-3 / M-4 draw loop; M-DEC3)
# ---------------------------------------------------------------------------
def simulation_run(E, sw, n_draw, W, W_SE, M_SE, HGVS, delta_raw, r0=None,
                   s_e=None, z=None, seed=SEED):
    """One simulate_rho-equivalent run, UNMODIFIED library calls.

    Per draw, in simulate_rho's exact rng order: u (only when r0 is given),
    then zero_epistasis_draw's w-noise draw, then its m-noise draw; then the
    project's own pipeline; then rho over the rows where BOTH delta_real
    and own_e.b^sim are finite.
    Returns (rhos, kept_rows_per_draw).
    """
    n_raw = W.shape[0]
    rng = np.random.default_rng(seed)
    rhos = np.empty(int(n_draw), dtype=float)
    kept = np.empty(int(n_draw), dtype=np.int64)
    for r in range(int(n_draw)):
        plant = None
        if r0 is not None:
            u = rng.normal(0.0, 1.0, size=n_raw)
            plant = p4c.plant_term(float(r0), float(s_e), z, u)
        w_sim, m_sim = p4c.zero_epistasis_draw(W, E, M_SE, sw, rng,
                                               plant=plant)
        eb = p4c.own_eb_from_arrays(w_sim, W_SE, m_sim, M_SE, HGVS)
        msk = np.isfinite(delta_raw) & np.isfinite(eb)
        kept[r] = int(msk.sum())
        rhos[r] = p4c.spearman(delta_raw[msk], eb[msk])
    return rhos, kept


# ==========================================================================
def main():
    banner("A4 / M -- MECHANISM-MATCHED ANALYSES (script 167)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}   "
          f"N_SIM = {N_SIM}   N_PLANT = {N_PLANT}   N_PERM = {N_PERM}   "
          f"N_STAB = {N_STAB}   (whole-placebo reference capped at "
          f"{N_REF_PLACEBO} draws)")
    print("RESAMPLING UNITS: everything inside one background resamples "
          "POSITION clusters (654 frame positions / 455 on H -- effective "
          "n is positions, never rows); M-6 resamples positions and "
          "re-derives every background's rho_b each draw; no "
          "background-level resampling happens in this module.  S1/S2 and "
          "M-3/M-4 are simulation / re-labelling loops, not bootstraps.")
    print("DECISION RULE (pre-registered): any hard gate FAIL -> exit 3; "
          "thresholds are never loosened and N is never raised to pass a "
          "gate.  Extra gates G-XFOLD and G-ALIGN are stricter than the "
          "frozen text, never looser.")
    print("NO torch / esm / thermompnn is imported and no model is scored "
          "(PHASE4 rule 1).")
    if SMOKE:
        print(f"*** SMOKE RUN (N_BOOT={N_BOOT}, N_SIM={N_SIM}, "
              f"N_PLANT={N_PLANT}, N_PERM={N_PERM}, N_STAB={N_STAB}): "
              "every frozen word computed on this run is PROVISIONAL, "
              "G-M3's Phase 1 CI sub-gate is SKIPPED, and this run cannot "
              "call G-M3 PASS.  The record is the full run ***")

    # =====================================================================
    banner("G-M0 -- INPUT INTEGRITY (frozen; HARD)", "-")
    gate("G-M0 prereg sha256", sha(PREREG) == PREREG_SHA,
         f"{sha(PREREG)} (target {PREREG_SHA})")
    n_lines = len(PREREG.read_text().splitlines())
    gate("G-M0 prereg line count", n_lines == PREREG_LINES,
         f"got {n_lines} target {PREREG_LINES}")
    gate("G-M0 rho table sha256", sha(RHO_TABLE) == RHO_TABLE_SHA,
         f"{sha(RHO_TABLE)} (target {RHO_TABLE_SHA})")
    gate("G-M0 3D table sha256", sha(D3_TABLE) == D3_TABLE_SHA,
         f"{sha(D3_TABLE)} (target {D3_TABLE_SHA})")
    gate("G-M0 6FCX.pdb sha256", sha(PDB_PATH) == PDB_SHA,
         f"{sha(PDB_PATH)} (target {PDB_SHA})")
    gate("G-M0 script 153 sha256", sha(S153) == S153_SHA,
         f"{sha(S153)} (target {S153_SHA})")
    gate("G-M0 m1_own_e_b_ge.csv sha256", sha(M1_GEO) == M1_GEO_SHA,
         f"{sha(M1_GEO)} (target {M1_GEO_SHA})")
    gate("G-M0 m1_fitted_expectations.csv sha256", sha(M1_FIT) == M1_FIT_SHA,
         f"{sha(M1_FIT)} (target {M1_FIT_SHA})")

    print("\n  FROZEN BLOCK, verbatim from disk (the rules this script "
          "applies):")
    for i, ln in enumerate(PREREG.read_text().splitlines(), start=1):
        print(f"  {i:3d}| {ln}")

    banner("QUOTED SOURCES (verbatim from disk)", "-")
    quote(STATS_EXT, 63, 88, "rebuild_interaction_fit -- the project's own "
                             "pipeline, unmodified")
    quote(OWN_CONTEXT, 48, 66, "wls_line -- the weighted aggregation")
    quote(OWN_CONTEXT, 143, 187,
          "fit_interaction -- expected / resid / valid, the aggregation at "
          "line 165, the >2-missing NaN rule at 179-181")
    quote(SIGN_NOTE, 6, 15,
          "SIGN SENTENCE (PHASE4 line 241: state it wherever a rho is "
          "discussed)")

    banner("PRE-REGISTERED DECISIONS -- printed BEFORE any M draw exists",
           "-")
    print("""  M-DEC1 (frozen M-3, sw_i): the raw file carries only PER-CONDITION
    WT SEs (w12.se..w200.se), no SE of the fitted scalar w_i =
    fit["w"]["fitness"] that M-3 perturbs -> PRIMARY sw_i = 0 (the frozen
    fallback); SENSITIVITY sw_i = the median m_se over the frame, applied
    as per-condition noise by phase4_common.zero_epistasis_draw (one
    independent N(0,1) per condition cell; the frozen text writes one
    scalar draw per variant -- differs only where sw_i > 0, i.e. only in
    the sensitivity).
  M-DEC2 (frozen M-3, linear sensitivity): E_c^lin = e2["expected"], the
    project's own linear expectation (script 153's identity plug-in).
    Script 153's GE-LIN-CF is named as the alternative NOT run (it would
    change cross-fitting and shape at once).
  M-DEC3 (draw loop): phase4_common.simulate_rho cannot run on real data
    (delta is NaN off-frame and p3c.spearman does not drop NaNs; a
    frame+reference-only rebuild misses recorded own_e.b by up to 3.3e-1;
    p.Ala222Val is absent from task32).  This script runs simulate_rho's
    OWN loop in its exact rng order (u first when r0 is given, then the
    w-noise draw, then the m-noise draw), calling zero_epistasis_draw and
    own_eb_from_arrays UNMODIFIED, masking to rows where both delta_real
    and own_e.b^sim are finite.  Wrapper-level deviation; no frozen
    constant changed.
  M-DEC4 (planting): z = rank_normal_z over the 10,757 frame rows, z = 0
    on the 2,377 off-frame raw rows; u ~ N(0,1) drawn for EVERY raw row
    (keeps the rng stream); s_e = SD of the recorded own_e.b over frame
    rows (ddof = 0); an off-frame plant reaches frame rows only through the
    shared correction curves (disclosed); at r0 = 0 the plant is s_e*u --
    pure independent noise, implemented literally as frozen.
  M-DEC5 (deciles): the 10 deciles of S_W are cut ONCE over the full
    frame; backgrounds and the H view inherit those labels.
  M-DEC6 (G-M5 rule): over the 9 grid means sorted by r0, all 8 adjacent
    pairs must satisfy mean[j] >= mean[i] - 2*sqrt(SE_i^2 + SE_j^2), SE =
    sd/sqrt(n) (ddof = 1); any failing pair -> G-M5 FAIL -> exit 3.
  M-DEC7 (M-5 S2 groups): d3 is position-level, so the 10 equal-count bins
    are cut over the DISTINCT resolved frame positions; unresolved
    positions form the eleventh bin; rows inherit their position's bin.
    Extra hard gates beyond the frozen block: G-XFOLD and G-ALIGN
    (stricter only) and the whole-placebo reference capped at
    min(N_REF, 50) draws.
  M-DEC8 (thresholds): the M-3 fraction, ratio and word use the frozen
    literal -0.088118 exactly; the full-precision anchor
    -0.08811806424891734 is printed beside every use.
  M-DEC9 (streams): each simulation run (one per M-3 variant, one per r0)
    and each surrogate null (S1, S2) gets its OWN default_rng(SEED);
    bootstrap ids come from the imported p4c.draw_ids.""")
    if SMOKE:
        print("  REPORT-SET NOTE: this is a SMOKE run -- every frozen word "
              "below is PROVISIONAL until the full run.")

    # =====================================================================
    banner("CONSTRUCTION -- script 125's cached frame, script 153's folds "
           "and GE-ISO", "-")
    tb = time.time()
    raw = pd.read_csv(RAW_PATH)
    t32 = pd.read_csv(T32_PATH)
    fit = rebuild_interaction_fit(raw)
    W = raw[WT_SCORE_COLS].to_numpy(float)
    W_SE = raw[WT_SE_COLS].to_numpy(float)
    M = raw[MT_SCORE_COLS].to_numpy(float)
    M_SE = fit["M_se"]
    valid = fit["valid"]
    wf = fit["w"]["fitness"]
    e2 = fit["e2"]
    HGVS = raw["hgvs"].to_numpy()
    raw_pos = raw["start"].to_numpy(int)
    N_RAW = len(raw)
    print(f"  raw rows = {N_RAW}; [rebuild_interaction_fit] "
          f"{time.time() - tb:.1f}s (the project's own pipeline, imported)")

    tb = time.time()
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    bgs = list(A.bgs)
    N_ids = list(A.N_IDS)
    print(f"  [pdg.build] {time.time() - tb:.1f}s -- script 125's cached "
          "construction, imported (AGENTS 2), not reimplemented")

    frame = A.frame
    x = frame["delta_esm"].to_numpy(float)
    y = frame["own_e_b"].to_numpy(float)
    s_w = frame["esm2_score"].to_numpy(float)
    base_f = frame["base_functionality"].to_numpy(float)
    pos = frame["position"].to_numpy()
    hmask = np.isin(pos, list(A.Hset))

    gate("G-M0 structure: 96 backgrounds, |N| = 78, arms G40/V38/S18",
         len(bgs) == T_NBGS and len(N_ids) == T_NN
         and table.arm.value_counts().to_dict() == T_ARMS,
         f"got {len(bgs)} bgs, |N| = {len(N_ids)}, arms "
         f"{table.arm.value_counts().to_dict()} target {T_ARMS}")
    gate("G-M0 structure: frame 10,757 rows / 654 positions, H = 455 "
         "positions / 7,526 rows",
         len(frame) == T_ROWS and frame.position.nunique() == T_POS
         and len(A.Hset) == T_HPOS and int(hmask.sum()) == T_HROWS,
         f"got ({len(frame)}, {frame.position.nunique()}), H = "
         f"{len(A.Hset)} positions / {int(hmask.sum())} rows; target "
         f"({T_ROWS}, {T_POS}) / {T_HPOS} / {T_HROWS}")

    # ---- G-M0(d): the D3 loader vs the stored d3_CA (67 resolved nulls) --
    df3 = pd.read_csv(D3_TABLE).set_index("bg_id")
    resN = [b for b in N_ids if bool(df3.loc[b, "resolved"])]
    gate("G-M0 structure: 67 resolved nulls", len(resN) == T_RESN,
         f"got {len(resN)} target {T_RESN}")
    ca, _atoms, _mx, _e3, _r3 = p3d.parse_pdb_float64(PDB_PATH)
    d3_diffs = [abs(p3d.d3_of(int(df3.loc[b, "position"]), ca)
                    - float(df3.loc[b, "d3_CA"])) for b in resN]
    gate("G-M0 D3 loader reproduces the stored d3_CA for all 67 resolved "
         "nulls", max(d3_diffs) < TOL_6DP,
         f"max|d3_of - stored d3_CA| = {max(d3_diffs):.3e} (gate < 1e-6)")

    # ---- script 153's folds and GE-ISO, transcribed under QUOTED SOURCE --
    # QUOTED SOURCE (scripts/153_m1_ge_target.py lines 460-516, D5/D6 and
    # the shared aggregate()): folds = permutation of the sorted raw
    # positions under default_rng(0), fold = rank mod 5, every variant
    # inherits its position's fold; GE-ISO = 4 conditions x 5 folds
    # weighted isotonic (weights 1/m_se^2, out_of_bounds="clip") on rows
    # with finite m_score, finite positive m_se and finite w; aggregate =
    # own_context lines 163/165/179-181 with the project's valid mask.
    pos_sorted = np.unique(raw_pos)
    rng0 = np.random.default_rng(0)
    perm = rng0.permutation(len(pos_sorted))
    fold_of_pos = np.empty(len(pos_sorted), dtype=np.int64)
    fold_of_pos[perm] = np.arange(len(pos_sorted)) % N_FOLDS
    fold = fold_of_pos[np.searchsorted(pos_sorted, raw_pos)]

    E_iso = np.full_like(M, np.nan)
    tb = time.time()
    for c in range(4):
        msk = (np.isfinite(M[:, c]) & np.isfinite(M_SE[:, c])
               & (M_SE[:, c] > 0) & np.isfinite(wf))
        for k in range(N_FOLDS):
            tr = msk & (fold != k)
            te = msk & (fold == k)
            iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
            iso.fit(wf[tr], M[tr, c], sample_weight=1.0 / M_SE[tr, c] ** 2)
            E_iso[te, c] = iso.predict(wf[te])
    print(f"  [GE-ISO fits: 4 conditions x {N_FOLDS} folds] "
          f"{time.time() - tb:.1f}s (transcribed from script 153 under "
          "QUOTED SOURCE, gated in G-XFOLD)")

    def aggregate(E):
        """Script 153's shared pipeline (QUOTED SOURCE, own_context 163,
        165, 179-181) with the project's second-pass valid mask."""
        resid = np.where(valid, M - E, np.nan)
        eb, _er, _df = wls_line(resid, M_SE, CONCS, valid)
        bad = (~valid).sum(axis=1) > 2
        return np.where(bad, np.nan, eb)

    E_lin = e2["expected"]                     # M-DEC2, the linear E_c

    # ---- frame <-> raw alignment (the analysis set, accounted) -----------
    idx_of_hgvs = pd.Series(np.arange(N_RAW), index=raw["hgvs"])
    frame_idx = idx_of_hgvs.reindex(frame["hgvs_pro"].to_numpy()).to_numpy()
    gate("alignment: every frame row maps to exactly one raw row",
         not np.isnan(frame_idx).any(),
         f"{int(np.isnan(frame_idx).sum())} frame hgvs absent from raw "
         f"(must be 0)")
    frame_idx = frame_idx.astype(int)
    delta_raw = np.full(N_RAW, np.nan)
    delta_raw[frame_idx] = x
    n_off = N_RAW - T_ROWS
    print(f"  analysis set accounting: raw {N_RAW} rows -> frame {T_ROWS} "
          f"rows / {T_POS} positions (finite delta_real), "
          f"{n_off} off-frame raw rows (target 2,377); H = {T_HROWS} rows "
          f"/ {T_HPOS} positions")

    # =====================================================================
    banner("G-XFOLD -- transcribed 5-fold isotonic vs script 153's saved "
           "output (EXTRA, stricter; HARD)", "-")
    saved = pd.read_csv(M1_GEO)
    gate("G-XFOLD fold vector equals script 153's saved fold column",
         np.array_equal(fold, saved["fold"].to_numpy())
         and np.array_equal(raw_pos, saved["position"].to_numpy(int))
         and np.array_equal(HGVS, saved["hgvs"].to_numpy()),
         f"{len(saved)} rows: fold identical "
         f"{np.array_equal(fold, saved['fold'].to_numpy())}, position "
         f"identical {np.array_equal(raw_pos, saved['position'].to_numpy(int))}, "
         f"hgvs identical {np.array_equal(HGVS, saved['hgvs'].to_numpy())}")
    eb_iso = aggregate(E_iso)
    sv = saved["own_e_b_ge_iso"].to_numpy(float)
    both = np.isfinite(eb_iso) & np.isfinite(sv)
    d_iso = float(np.max(np.abs(eb_iso[both] - sv[both])))
    n_nan_dis = int((np.isnan(eb_iso) ^ np.isnan(sv)).sum())
    gate("G-XFOLD aggregate(E_iso) == script 153's saved own_e_b_ge_iso",
         d_iso < TOL_12 and n_nan_dis == 0,
         f"max|diff| = {d_iso:.3e} over {int(both.sum())} finite rows, "
         f"NaN-pattern disagreements = {n_nan_dis} (gates < 1e-12 / 0)")
    fe = pd.read_csv(M1_FIT)
    iso_rows = fe[fe.kind == "iso_transition"]
    worst_tr, n_fits = 0.0, 0
    for c in range(4):
        msk = (np.isfinite(M[:, c]) & np.isfinite(M_SE[:, c])
               & (M_SE[:, c] > 0) & np.isfinite(wf))
        for k in range(N_FOLDS):
            tr = msk & (fold != k)
            iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
            iso.fit(wf[tr], M[tr, c], sample_weight=1.0 / M_SE[tr, c] ** 2)
            sub = iso_rows[(iso_rows.condition == int(CONCS[c]))
                           & (iso_rows.fold == k)]
            xs = sub["w"].to_numpy(float)
            ys = sub["value"].to_numpy(float)
            if len(xs) != len(iso.X_thresholds_):
                worst_tr = float("inf")
                break
            worst_tr = max(worst_tr,
                           float(np.max(np.abs(xs - iso.X_thresholds_))),
                           float(np.max(np.abs(ys - iso.y_thresholds_))))
            n_fits += 1
    gate(f"G-XFOLD all {4 * N_FOLDS} isotonic transition lists equal "
         "script 153's saved m1_fitted_expectations.csv",
         n_fits == 20 and worst_tr < TOL_12,
         f"{n_fits} fits compared, max|diff| = {worst_tr:.3e} "
         "(gate < 1e-12)")

    # =====================================================================
    banner("G-ALIGN -- script 125's row join re-run, and the 97 x n delta "
           "matrix M-6 uses (EXTRA, AGENTS 5; HARD)", "-")
    tb = time.time()
    pos_idx_of = {}
    worst_pos = 0
    worst_own = 0.0
    worst_delta = 0.0
    worst_rho = 0.0
    worst_rhoH = 0.0
    for b in bgs:
        f = pd.read_csv(ROOT / "data/processed/phase2" / f"bg_{b}.csv")
        m = frame.merge(f[["position", "mut_aa", "score"]],
                        on=["position", "mut_aa"], how="left")
        if len(m) != len(frame):
            gate("G-ALIGN join does not duplicate frame rows", False,
                 f"{b}: join length {len(m)} != {len(frame)}")
        pidx = np.flatnonzero(m["score"].notna().to_numpy())
        pos_idx_of[b] = pidx
        r = A.bg_rows[b]
        if len(r) != len(pidx):
            gate("G-ALIGN background row count matches 125's rows", False,
                 f"{b}: bg_rows {len(r)} != joined {len(pidx)}")
        worst_pos = max(worst_pos,
                        int(np.sum(r["position"].to_numpy()
                                   != frame["position"].to_numpy()[pidx])))
        worst_own = max(worst_own, float(np.max(np.abs(
            r["own_e_b"].to_numpy() - frame["own_e_b"].to_numpy()[pidx]))))
        d_re = m["score"].to_numpy()[pidx] - s_w[pidx]
        worst_delta = max(worst_delta, float(np.max(np.abs(
            r["delta"].to_numpy() - d_re))))
        rho_f = p4c.spearman(r["delta"].to_numpy(), y[pidx])
        worst_rho = max(worst_rho, abs(rho_f - float(A.point[b])),
                        abs(rho_f - float(table.loc[b, "rho_full"])))
        hm = np.isin(r["position"].to_numpy(), list(A.Hset))
        if hm.any():
            rho_h = p4c.spearman(r["delta"].to_numpy()[hm], y[pidx][hm])
            worst_rhoH = max(worst_rhoH,
                             abs(rho_h - float(table.loc[b, "rho_H"])))
    gate("G-ALIGN 96 backgrounds reproduce 125's rows and cached rhos "
         "exactly",
         worst_pos == 0 and worst_own < TOL_EXACT
         and worst_delta < TOL_12 and worst_rho < TOL_12
         and worst_rhoH < TOL_12,
         f"position mismatches = {worst_pos}, max|own_e_b diff| = "
         f"{worst_own:.3e}, max|delta diff| = {worst_delta:.3e}, "
         f"max|rho_full diff| = {worst_rho:.3e}, max|rho_H diff| = "
         f"{worst_rhoH:.3e} (gates 0 / 0 / <1e-12 / <1e-12 / <1e-12) "
         f"in {time.time() - tb:.1f}s")

    # the 97 x n delta matrix: A222V first, then A.bgs order (frozen M-6)
    dmat = np.full((1 + len(bgs), T_ROWS), np.nan)
    dmat[0] = x
    for j, b in enumerate(bgs):
        dmat[1 + j, pos_idx_of[b]] = (A.bg_rows[b]["delta"].to_numpy(float))
    n_idx = [1 + bgs.index(b) for b in N_ids]
    gate("G-ALIGN delta matrix row 0 equals the frame's delta",
         np.array_equal(dmat[0], x, equal_nan=True),
         f"exact = {np.array_equal(dmat[0], x, equal_nan=True)} over "
         f"{T_ROWS} rows")
    worst_dm = 0.0
    worst_dmH = 0.0
    for j, b in enumerate(bgs):
        r_j = dmat[1 + j]
        fin = np.isfinite(r_j)
        worst_dm = max(worst_dm,
                       abs(p4c.spearman(r_j[fin], y[fin])
                           - float(table.loc[b, "rho_full"])))
        fh = fin & hmask
        worst_dmH = max(worst_dmH,
                        abs(p4c.spearman(r_j[fh], y[fh])
                            - float(table.loc[b, "rho_H"])))
    gate("G-ALIGN delta matrix reproduces every cached rho_b (full and H)",
         worst_dm < TOL_12 and worst_dmH < TOL_12,
         f"max|diff| rho_full = {worst_dm:.3e}, rho_H = {worst_dmH:.3e} "
         "over 96 backgrounds (gate < 1e-12)")

    # =====================================================================
    banner("G-M1 -- ANCHOR REPRODUCTION (frozen; HARD)", "-")
    rho_full_direct = p4c.spearman(x, y)
    rho_full_av = p4c.spearman(A.a222v_rows["delta"].to_numpy(float),
                               A.a222v_rows["own_e_b"].to_numpy(float))
    note("G-M1 A222V rho full (frame columns)", rho_full_direct,
         T_RHO_FULL, TOL_9DP)
    note("G-M1 A222V rho full (script 125's a222v_rows)", rho_full_av,
         T_RHO_FULL, TOL_9DP)
    gate("G-M1 the two sources agree with each other",
         abs(rho_full_direct - rho_full_av) < TOL_12,
         f"|diff| = {abs(rho_full_direct - rho_full_av):.3e} "
         "(AGENTS 5 column identity)")
    rho_h_direct = p4c.spearman(x[hmask], y[hmask])
    note("G-M1 A222V rho H (frame columns)", rho_h_direct, T_RHO_H,
         TOL_9DP)
    note("G-M1 A222V rho H (pdg.rho_table cross-check)", float(rho_a_H),
         T_RHO_H, TOL_9DP)
    nulls_full = table.loc[N_ids, "rho_full"].to_numpy(float)
    nulls_H = table.loc[N_ids, "rho_H"].to_numpy(float)
    p_f, k_f, n_f = p4c.p_spec(rho_full_direct, nulls_full, mode="neg")
    p_h, k_h, n_h = p4c.p_spec(rho_h_direct, nulls_H, mode="neg")
    beat_f = sorted(np.array(N_ids)[nulls_full <= rho_full_direct].tolist())
    beat_h = sorted(np.array(N_ids)[nulls_H <= rho_h_direct].tolist())
    gate("G-M1 p_spec(neg) full = 2/79 with the named beaters",
         abs(p_f - T_P_FULL) < TOL_EXACT and k_f == 1 and n_f == T_NN
         and beat_f == T_BEATERS_FULL,
         f"p = (1+{k_f})/(1+{n_f}) = {p_f!r} target {T_P_FULL!r} (2/79); "
         f"beaters {beat_f} target {T_BEATERS_FULL}")
    gate("G-M1 p_spec(neg) H = 4/79 with the named beaters",
         abs(p_h - T_P_H) < TOL_EXACT and k_h == 3 and n_h == T_NN
         and beat_h == T_BEATERS_H,
         f"p = (1+{k_h})/(1+{n_h}) = {p_h!r} target {T_P_H!r} (4/79); "
         f"beaters {beat_h} target {T_BEATERS_H}")
    print(f"  anchor (recomputed) = {rho_full_direct!r} = {T_RHO_FULL_PREC}"
          f"; frozen literal for M-3/M-5 fractions and words = "
          f"{T_ANCHOR_LIT} (M-DEC8)")

    # =====================================================================
    banner("G-M2 -- PHASE 1 PARTIALS REPRODUCE (frozen; HARD)", "-")
    part1 = p4c.partial_spearman(x, y, [s_w])
    note("G-M2 linear rank partial controlling S_W", part1, T_PARTIAL_SW,
         TOL_12)
    part2 = p4c.partial_spearman(x, y, [s_w, base_f])
    note("G-M2 two-covariate linear rank partial (4 dp)", round(part2, 4),
         T_PARTIAL_2COV_4DP, TOL_EXACT)
    print(f"       two-covariate full precision = {part2!r} "
          "(Phase 1 L2 printed -0.0829)")
    ret1 = abs(part1) / abs(rho_full_direct)
    print(f"       retained fraction |partial|/|raw| = {ret1!r} "
          f"(rounds to {round(ret1, 3)})")

    # =====================================================================
    banner("G-M6 -- TOY GATES for the stratified statistic and the "
           "decomposition (frozen; HARD)", "-")
    xs_t = np.arange(1, 9.0)
    st_t = np.array(["a"] * 4 + ["b"] * 4)
    v1 = p4c.stratified_spearman(xs_t, xs_t, st_t)
    gate("G-M6 stratified: two perfectly monotone strata -> 1.0",
         abs(v1 - 1.0) < TOL_EXACT, f"got {v1!r} target 1.0")
    x2 = np.array([1.0, 2, 3, 4, 1, 2, 3, 4])
    y2 = np.array([1.0, 2, 3, 4, 3, 1, 4, 2])      # stratum b rho = 0 exactly
    v2 = p4c.stratified_spearman(x2, y2, st_t)
    v2r = ref_stratified(x2, y2, st_t, np.arange(8))
    gate("G-M6 stratified: weighted mean of (1.0, 0.0) at weights 4/4, and "
         "the scipy reference agrees",
         abs(v2 - 0.5) < TOL_EXACT and abs(v2 - v2r) < TOL_12,
         f"library {v2!r} target 0.5, reference {v2r!r}, |diff| "
         f"{abs(v2 - v2r):.3e}")
    st3 = np.array(["a"] * 4 + ["b"] * 4 + ["c"] * 4)
    x3 = np.concatenate([x2, np.arange(1, 5.0)])
    y3 = np.concatenate([y2, np.full(4, 7.0)])     # stratum c constant -> NaN
    v3 = p4c.stratified_spearman(x3, y3, st3)
    v3r = ref_stratified(x3, y3, st3, np.arange(12))
    gate("G-M6 stratified: undefined stratum dropped and weights "
         "renormalised (decision I1), reference agrees",
         abs(v3 - 0.5) < TOL_EXACT and abs(v3 - v3r) < TOL_12,
         f"library {v3!r} reference {v3r!r} target 0.5")
    pb_x, pb_y, pb_p = [], [], []
    for p_ in range(6):
        base = 10.0 * (p_ + 1)
        pb_x += list(base + np.array([1.0, 2, 3, 4]))
        pb_y += list(3.0 * p_ + np.array([3.0, 1, 4, 2]))
        pb_p += [p_] * 4
    dpb = p4c.between_within_decomposition(pb_x, pb_y, pb_p, min_rows=4)
    dpr = ref_decomposition(pb_x, pb_y, pb_p, np.arange(24), min_rows=4)
    gate("G-M6 decomposition PLANTED PURE-BETWEEN (and scipy reference)",
         abs(dpb["rho_between"] - 1.0) < TOL_EXACT
         and abs(dpb["rho_within"] - 0.0) < TOL_EXACT
         and abs(dpr[0] - dpb["rho_between"]) < TOL_12
         and abs(dpr[1] - dpb["rho_within"]) < TOL_12,
         f"rho_between {dpb['rho_between']!r} target 1.0, rho_within "
         f"{dpb['rho_within']!r} target 0.0, reference "
         f"[{dpr[0]!r}, {dpr[1]!r}]")
    pw_x, pw_y, pw_p = [], [], []
    bx = [10.0, 20.0, 30.0, 40.0]
    by = [30.0, 10.0, 40.0, 20.0]
    for p_ in range(4):
        off = np.array([1.0, 2, 3, 4]) * 0.1
        pw_x += list(bx[p_] + off)
        pw_y += list(by[p_] + off)
        pw_p += [p_] * 4
    dpw = p4c.between_within_decomposition(pw_x, pw_y, pw_p, min_rows=4)
    dpwr = ref_decomposition(pw_x, pw_y, pw_p, np.arange(16), min_rows=4)
    gate("G-M6 decomposition PLANTED PURE-WITHIN (and scipy reference)",
         abs(dpw["rho_within"] - 1.0) < TOL_EXACT
         and abs(dpw["rho_between"] - 0.0) < TOL_EXACT
         and abs(dpwr[1] - dpw["rho_within"]) < TOL_12
         and abs(dpwr[0] - dpw["rho_between"]) < TOL_12,
         f"rho_within {dpw['rho_within']!r} target 1.0, rho_between "
         f"{dpw['rho_between']!r} target 0.0, reference "
         f"[{dpwr[0]!r}, {dpwr[1]!r}]")
    dmr = p4c.between_within_decomposition(
        list(pb_x) + [1.0, 2.0, 3.0], list(pb_y) + [1.0, 5.0, 9.0],
        list(pb_p) + [99, 99, 99], min_rows=4)
    gate("G-M6 decomposition excludes a position below min_rows (I2)",
         dmr["n_qualifying"] == 6 and dmr["n_positions"] == 7,
         f"n_qualifying {dmr['n_qualifying']} target 6; n_positions "
         f"{dmr['n_positions']} target 7")

    # =====================================================================
    banner("G-M3 -- BOOTSTRAP IDENTITY, DRAW-BY-DRAW REFERENCES, PHASE 1 CI "
           "(frozen; HARD)", "-")
    point_anchor = p4c.spearman(x, y)
    labels_full = p4c.first_appearance_labels(pos)
    nk_full = len(labels_full)
    ids_one = np.arange(nk_full, dtype=np.int64)[None, :]
    ids_ref, _ = p4c.draw_ids(pos, N_REF, SEED)

    # (a) identity: every position once == each point estimate
    one_anchor = float(p4c.pos_cluster_boot_from_ids(x, y, pos, ids_one)[0])
    gate("G-M3(i) identity: anchor rho, every position once",
         abs(one_anchor - point_anchor) < TOL_12,
         f"every-once {one_anchor!r} point {point_anchor!r} |diff| "
         f"{abs(one_anchor - point_anchor):.3e} (gate < 1e-12)")

    # deciles (M-DEC5) are cut ONCE, here, before any statistic uses them
    bins_frame = p4c.equal_count_bins(s_w, 10)
    bin_sizes = np.bincount(bins_frame, minlength=10).tolist()
    print(f"  deciles of S_W cut ONCE over the frame (M-DEC5); row counts "
          f"per decile {bin_sizes} (sum {sum(bin_sizes)})")

    part_stat = lambda idx: p4c.partial_spearman(x[idx], y[idx],
                                                 [s_w[idx]])
    part2_stat = lambda idx: p4c.partial_spearman(x[idx], y[idx],
                                                  [s_w[idx], base_f[idx]])
    strat_stat = lambda idx: p4c.stratified_spearman(x[idx], y[idx],
                                                     bins_frame[idx])
    def decomp_stat(idx):
        d = p4c.between_within_decomposition(x[idx], y[idx], pos[idx],
                                             min_rows=5)
        return np.array([d["rho_between"], d["rho_within"]])

    one_part = one_draw(pos, labels_full, part_stat)
    gate("G-M3(i) identity: A222V partial (primary), every position once",
         abs(float(one_part[0]) - p4c.partial_spearman(x, y, [s_w]))
         < TOL_12,
         f"every-once {float(one_part[0])!r} point "
         f"{p4c.partial_spearman(x, y, [s_w])!r} (gate < 1e-12)")
    one_strat = one_draw(pos, labels_full, strat_stat)
    gate("G-M3(i) identity: stratified rho, every position once",
         abs(float(one_strat[0])
             - p4c.stratified_spearman(x, y, bins_frame)) < TOL_12,
         f"every-once {float(one_strat[0])!r} point "
         f"{p4c.stratified_spearman(x, y, bins_frame)!r} (gate < 1e-12)")
    one_dec = one_draw(pos, labels_full, decomp_stat)
    d_point = p4c.between_within_decomposition(x, y, pos, min_rows=5)
    gate("G-M3(i) identity: both decomposition components, every position "
         "once",
         abs(float(one_dec[0]) - d_point["rho_between"]) < TOL_12
         and abs(float(one_dec[1]) - d_point["rho_within"]) < TOL_12,
         f"every-once [{float(one_dec[0])!r}, {float(one_dec[1])!r}] "
         f"point [{d_point['rho_between']!r}, {d_point['rho_within']!r}] "
         "(gate < 1e-12 each)")

    # (b) draw-by-draw references
    tb = time.time()
    d_part, _, _ = cluster_draws(pos, part_stat, N_REF, SEED)
    r_part = cluster_reference(pos,
                               lambda i: ref_partial(x, y, [s_w], i),
                               ids_ref, labels_full)
    md = float(np.max(np.abs(d_part[:, 0] - r_part[:, 0])))
    gate(f"G-M3(ii) partial draw-by-draw vs closed-form reference "
         f"({N_REF} draws)", md < TOL_12,
         f"max|fast - reference| = {md:.3e} (gate < 1e-12) in "
         f"{time.time() - tb:.1f}s")
    tb = time.time()
    d_part2, _, _ = cluster_draws(pos, part2_stat, N_REF, SEED)
    r_part2 = cluster_reference(pos,
                                lambda i: ref_partial(x, y,
                                                      [s_w, base_f], i),
                                ids_ref, labels_full)
    md2 = float(np.max(np.abs(d_part2[:, 0] - r_part2[:, 0])))
    gate(f"G-M3(ii) two-covariate partial draw-by-draw vs reference "
         f"({N_REF} draws)", md2 < TOL_12,
         f"max|fast - reference| = {md2:.3e} (gate < 1e-12) in "
         f"{time.time() - tb:.1f}s")
    tb = time.time()
    d_strat, _, _ = cluster_draws(pos, strat_stat, N_REF, SEED)
    r_strat = cluster_reference(pos,
                                lambda i: ref_stratified(x, y, bins_frame,
                                                         i),
                                ids_ref, labels_full)
    md3 = float(np.max(np.abs(d_strat[:, 0] - r_strat[:, 0])))
    gate(f"G-M3(ii) stratified draw-by-draw vs scipy reference "
         f"({N_REF} draws)", md3 < TOL_12,
         f"max|fast - reference| = {md3:.3e} (gate < 1e-12) in "
         f"{time.time() - tb:.1f}s")
    tb = time.time()
    d_dec, _, _ = cluster_draws(pos, decomp_stat, N_REF, SEED)
    r_dec = cluster_reference(pos,
                              lambda i: ref_decomposition(x, y, pos, i,
                                                          min_rows=5),
                              ids_ref, labels_full)
    md4 = float(np.max(np.abs(d_dec - r_dec)))
    gate(f"G-M3(ii) decomposition draw-by-draw vs scipy reference "
         f"({N_REF} draws)", md4 < TOL_12,
         f"max|fast - reference| = {md4:.3e} (gate < 1e-12) in "
         f"{time.time() - tb:.1f}s")
    tb = time.time()
    d_imp = p4c.pos_cluster_boot_from_ids(x, y, pos, ids_ref)
    d_imp_ref = p4c.reference_boot(x, y, pos, ids_ref)
    md5 = float(np.max(np.abs(d_imp - d_imp_ref)))
    gate(f"G-M3(ii) imported corrected routine vs reference_boot "
         f"({N_REF} draws)", md5 < TOL_12,
         f"max|corrected - reference| = {md5:.3e} (gate < 1e-12) in "
         f"{time.time() - tb:.1f}s")

    # (c) Phase 1 CI reproduction
    if N_BOOT == 10000:
        tb = time.time()
        draws_anchor = p4c.pos_cluster_boot(x, y, pos, N_BOOT, SEED)
        lo, hi, nf = p4c.pct_ci(draws_anchor)
        note("G-M3(iii) Phase 1 CI lo", lo, T_CI_LO, TOL_9DP)
        note("G-M3(iii) Phase 1 CI hi", hi, T_CI_HI, TOL_9DP)
        print(f"       ({nf} finite draws, N_BOOT={N_BOOT}, SEED={SEED}; "
              f"the routine is the imported corrected one) in "
              f"{time.time() - tb:.1f}s")
    else:
        gate("G-M3(iii) Phase 1 CI reproduction", False,
             f"SKIPPED (smoke): N_BOOT={N_BOOT} != 10000 -- G-M3 cannot "
             "be called PASS on this run; decided on the N_BOOT=10000 run",
             hard=False)

    # =====================================================================
    banner("G-M4 -- SIMULATION IDENTITY: zero noise, E = the observed m "
           "(frozen; HARD)", "-")
    rng_id = np.random.default_rng(SEED)
    w0, m0 = p4c.zero_epistasis_draw(W, M, M_SE, np.zeros(N_RAW), rng_id,
                                     m_noise=np.zeros_like(M))
    eb0 = p4c.own_eb_from_arrays(w0, W_SE, m0, M_SE, HGVS)
    rec = pd.Series(t32["own_e_b"].to_numpy(float),
                    index=t32["hgvs_pro"]).reindex(HGVS).to_numpy()
    m_rec = np.isfinite(rec)
    d_rec = float(np.nanmax(np.abs(eb0[m_rec] - rec[m_rec])))
    n_above = int((np.abs(eb0[m_rec] - rec[m_rec]) > TOL_12).sum())
    n_missing = int((m_rec & ~np.isfinite(eb0)).sum())
    gate("G-M4 zero-noise pipeline returns the recorded own_e.b",
         d_rec < TOL_12 and n_above == 0 and n_missing == 0,
         f"compared {int(m_rec.sum())} recorded rows (target 10,757), "
         f"max|diff| = {d_rec:.3e}, rows > 1e-12 = {n_above}, recorded but "
         f"not rebuildable = {n_missing} (gates < 1e-12 / 0 / 0)")
    n_extra = int((~m_rec & np.isfinite(eb0)).sum())
    print(f"  [informational] rows rebuilt finite but with NO recorded "
          f"own_e_b = {n_extra} (the raw file's "
          f"{int((raw['type'] != 'substitution').sum())} "
          "nonsense/synonymous rows plus unassigned substitutions -- the "
          "frozen comparison set is the recorded rows)")

    # =====================================================================
    banner("M-1 -- PARTIAL-CORRELATION PLACEBO TEST (frozen; PRIMARY "
           "control S_W)", "-")
    print(f"  SIGN SENTENCE (frozen wherever a rho is discussed): a "
          f"NEGATIVE rho means the model's background shift runs OPPOSITE "
          f"to the measured shift -- direction only (SIGN_CONVENTION.md "
          f"lines 6-15, quoted above).")
    raw_rho = {"full": rho_full_direct, "H": rho_h_direct}
    ctrls = {"PRIMARY (S_W)": [s_w], "SECONDARY (S_W + base functionality)":
             [s_w, base_f]}
    m1 = {}
    tb = time.time()
    for cname, cl in ctrls.items():
        for view in ("full", "H"):
            m_ = hmask if view == "H" else np.ones(T_ROWS, dtype=bool)
            pt = p4c.partial_spearman(x[m_], y[m_],
                                      [c[m_] for c in cl])
            d_ci, _, _ = cluster_draws(pos[m_] if view == "H" else pos,
                                       (lambda idx, cl=cl, m_=m_:
                                        p4c.partial_spearman(x[m_][idx],
                                                             y[m_][idx],
                                                             [c[m_][idx]
                                                              for c in cl])),
                                       N_BOOT, SEED)
            lo, hi, nfin = p4c.pct_ci(d_ci[:, 0])
            m1[(cname, view)] = {"rho": pt, "lo": lo, "hi": hi,
                                 "draws": d_ci[:, 0], "nfin": nfin}
        print(f"  [{cname}]")
        for view in ("full", "H"):
            r = m1[(cname, view)]
            print(f"      {view:4s}: partial rho = {r['rho']:+.9f}  "
                  f"CI [{r['lo']:+.6f}, {r['hi']:+.6f}] "
                  f"({r['nfin']} finite draws of {N_BOOT}, "
                  f"position-cluster)   raw rho = {raw_rho[view]:+.9f}   "
                  f"retained = {abs(r['rho']) / abs(raw_rho[view]):.6f}")
    print(f"  [per-background partial rho_b, both controls x both views "
          f"(raw rho_b beside each): {time.time() - tb:.1f}s]")
    print(f"      {'bg_id':10s} {'arm':4s} {'view':4s} {'raw':>12s} "
          f"{'partial_S_W':>12s} {'partial_2cov':>12s}")
    m1_bg = {}
    for b in bgs:
        pidx = pos_idx_of[b]
        rb = A.bg_rows[b]
        for view in ("full", "H"):
            m_ = np.isin(rb["position"].to_numpy(), list(A.Hset)) \
                if view == "H" else np.ones(len(rb), dtype=bool)
            xb = rb["delta"].to_numpy(float)[m_]
            yb = y[pidx][m_]
            p1 = p4c.partial_spearman(xb, yb, [s_w[pidx][m_]])
            p2 = p4c.partial_spearman(xb, yb,
                                      [s_w[pidx][m_], base_f[pidx][m_]])
            rho_b = p4c.spearman(xb, yb)
            m1_bg[(b, view)] = (rho_b, p1, p2)
            print(f"      {b:10s} {table.loc[b, 'arm']:4s} {view:4s} "
                  f"{rho_b:+12.6f} {p1:+12.6f} {p2:+12.6f}")
    # p_spec(neg) / p_spec(abs) on the partials, both controls, both views
    print("\n  p_spec on the partial rho_b (N = 78 nulls):")
    for cname in ctrls:
        for mode in ("neg", "abs"):
            for view in ("full", "H"):
                col = 1 if cname.startswith("PRIMARY") else 2
                tgt = m1[(cname, view)]["rho"]
                nuls = np.array([m1_bg[(b, view)][col] for b in N_ids])
                pv, kv, nv = p4c.p_spec(tgt, nuls, mode=mode)
                beat = sorted(np.array(N_ids)[nuls <= tgt].tolist()) \
                    if mode == "neg" else sorted(
                        np.array(N_ids)[np.abs(nuls) >= abs(tgt)].tolist())
                m1.setdefault("pspec", {})[(cname, mode, view)] = (pv, kv,
                                                                   beat)
                print(f"      {cname:40s} p_spec({mode:3s}) {view:4s}: "
                      f"rho_partial = {tgt:+.6f}, p = (1+{kv})/(1+{nv}) = "
                      f"{pv:.6f}, at-or-below/magnitude nulls = {beat}")
    # shift-adjusted p_spec_adj (Diagnostics II D9) on the partials
    print("\n  p_spec_adj: leave-one-out OLS of the partial rho_b on "
          "mean|delta_b| (Diagnostics II D9):")
    mad = {"full": {}, "H": {}}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(
                rr.delta.to_numpy(float))))
    mad_a = {}
    for view in ("full", "H"):
        ra = A.a222v_rows if view == "full" else \
            A.a222v_rows[A.a222v_rows.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))
    for cname in ctrls:
        col = 1 if cname.startswith("PRIMARY") else 2
        for view in ("full", "H"):
            yv = np.array([m1_bg[(b, view)][col] for b in N_ids])
            xv = np.array([mad[view][b] for b in N_ids])
            r_b = p3c.loo_ols_residuals(yv, xv)
            _, _, predA = p3c.ols_fit_predict(yv, xv, [mad_a[view]])
            r_A = m1[(cname, view)]["rho"] - float(predA[0])
            k_adj = int(np.sum(r_b <= r_A))
            p_adj = (1 + k_adj) / (1 + len(N_ids))
            beat = sorted(np.array(N_ids)[r_b <= r_A].tolist())
            m1.setdefault("padj", {})[(cname, view)] = (p_adj, k_adj, beat)
            print(f"      {cname:40s} {view:4s}: r_A = {r_A:+.6f}, "
                  f"k = {k_adj}/{len(N_ids)}, p_spec_adj = (1+{k_adj})/"
                  f"(1+78) = {p_adj:.6f}, beaters = {beat}")
    prim_full = m1[("PRIMARY (S_W)", "full")]
    prim_h = m1[("PRIMARY (S_W)", "H")]
    p_full_m1 = m1["pspec"][("PRIMARY (S_W)", "neg", "full")][0]
    p_h_m1 = m1["pspec"][("PRIMARY (S_W)", "neg", "H")][0]
    word_m1 = p4c.word_m1_partial(prim_full["lo"], prim_full["hi"],
                                  p_full_m1, p_h_m1)
    if SMOKE:
        word_m1_disp = f"{word_m1}  [PROVISIONAL: smoke run]"
    else:
        word_m1_disp = word_m1
    print(f"\n  FROZEN M-1 WORD (primary control, A222V partial): "
          f"CI [{prim_full['lo']:+.6f}, {prim_full['hi']:+.6f}], "
          f"p_spec(neg) full = {p_full_m1:.6f} (target condition <= 0.05), "
          f"H = {p_h_m1:.6f} (target condition <= 0.10)  ->  "
          f"{word_m1_disp}")
    print("  (the secondary control and p_spec(abs) are reported above "
          "with no word: the frozen block defines the word on the primary "
          "control only)")

    # =====================================================================
    banner("M-2 -- STRATIFIED CORRELATION (frozen; sensitivity, NO WORD)",
           "-")
    print("  deciles of S_W are the frame-level labels cut above "
          "(M-DEC5); every background and the H view inherit them.")
    tb = time.time()
    m2 = {}
    for view in ("full", "H"):
        m_ = hmask if view == "H" else np.ones(T_ROWS, dtype=bool)
        pt = p4c.stratified_spearman(x[m_], y[m_], bins_frame[m_])
        d_ci, _, _ = cluster_draws(
            pos[m_] if view == "H" else pos,
            (lambda idx, m_=m_: p4c.stratified_spearman(x[m_][idx],
                                                        y[m_][idx],
                                                        bins_frame[m_][idx])),
            N_BOOT, SEED)
        lo, hi, nfin = p4c.pct_ci(d_ci[:, 0])
        m2[view] = {"rho": pt, "lo": lo, "hi": hi, "nfin": nfin}
        print(f"      {view:4s}: stratified rho (A222V) = {pt:+.9f}  "
              f"CI [{lo:+.6f}, {hi:+.6f}] ({nfin} finite draws of "
              f"{N_BOOT}, position-cluster)")
    m2_bg = {}
    print(f"\n      {'bg_id':10s} {'arm':4s} {'view':4s} {'strat_rho':>12s}")
    for b in bgs:
        pidx = pos_idx_of[b]
        rb = A.bg_rows[b]
        for view in ("full", "H"):
            m_ = np.isin(rb["position"].to_numpy(), list(A.Hset)) \
                if view == "H" else np.ones(len(rb), dtype=bool)
            st = p4c.stratified_spearman(rb["delta"].to_numpy(float)[m_],
                                         y[pidx][m_], bins_frame[pidx][m_])
            m2_bg[(b, view)] = st
            print(f"      {b:10s} {table.loc[b, 'arm']:4s} {view:4s} "
                  f"{st:+12.6f}")
    print("\n  p_spec(neg) on the stratified rho_b (N = 78):")
    for view in ("full", "H"):
        nuls = np.array([m2_bg[(b, view)] for b in N_ids])
        pv, kv, nv = p4c.p_spec(m2[view]["rho"], nuls, mode="neg")
        beat = sorted(np.array(N_ids)[nuls <= m2[view]["rho"]].tolist())
        m2.setdefault("pspec", {})[view] = (pv, kv, beat)
        print(f"      {view:4s}: stratified rho = {m2[view]['rho']:+.6f}, "
              f"p = (1+{kv})/(1+{nv}) = {pv:.6f}, at-or-below nulls = "
              f"{beat}")
    print(f"      [per-background table {time.time() - tb:.1f}s]  "
          "M-2 carries NO word (frozen block).")

    # =====================================================================
    banner("M-3 -- ZERO-EPISTASIS SIMULATION NULL (frozen; A222V only)",
           "-")
    print("  DECISIONS IN FORCE (stated before the first draw):")
    print("    M-DEC1  PRIMARY sw_i = 0 (the data carries no SE of the "
          "fitted scalar w_i; the per-condition w12.se..w200.se are NOT "
          "that quantity); SENSITIVITY sw_i = the median m_se over the "
          "frame = computed below.")
    print("    M-DEC2  the linear sensitivity plugs E_c^lin = "
          "e2[\"expected\"] (the project's own linear expectation); "
          "GE-LIN-CF is named and NOT run.")
    print("    M-DEC3  simulate_rho's own draw loop, unmodified library "
          "calls, its exact rng order; rho masked to rows where both "
          "delta_real and own_e.b^sim are finite.")
    frame_mse = M_SE[frame_idx]
    med_mse = float(np.nanmedian(frame_mse[np.isfinite(frame_mse)]))
    print(f"    median m_se over the frame rows x 4 conditions = "
          f"{med_mse!r} (the frozen sensitivity's sw_i)")
    sw_primary = np.zeros(N_RAW)
    sw_median = np.full(N_RAW, med_mse)
    print(f"  frozen M-3 report set: mean, SD, 2.5th and 97.5th "
          f"percentiles, fraction <= {T_ANCHOR_LIT}, "
          f"mean/({T_ANCHOR_LIT}); word EXCESS-OVER-ARTIFACT iff "
          f"{T_ANCHOR_LIT} <= p2.5 (PRIMARY only; sensitivities "
          f"wordless).")
    runs = [
        ("PRIMARY  (E = GE-ISO cross-fitted isotonic, sw_i = 0)",
         E_iso, sw_primary),
        ("SENSITIVITY A (E = E_c^lin = e2.expected, sw_i = 0)",
         E_lin, sw_primary),
        ("SENSITIVITY B (E = GE-ISO, sw_i = median m_se)",
         E_iso, sw_median),
    ]
    m3 = {}
    for label, E_gen, sw in runs:
        tb = time.time()
        rhos, kept = simulation_run(E_gen, sw, N_SIM, W, W_SE, M_SE, HGVS,
                                    delta_raw)
        m3[label] = rhos
        gate(f"G-M4 every M-3 draw kept exactly {T_ROWS} rows -- {label[:28]}",
             int(kept.min()) == T_ROWS and int(kept.max()) == T_ROWS,
             f"kept rows: min {int(kept.min())}, max {int(kept.max())} "
             f"over {N_SIM} draws (both must be {T_ROWS})")
        s = p4c.draw_summary(rhos)
        frac = p4c.tail_fraction(rhos, T_ANCHOR_LIT, side="le")
        print(f"\n  {label}")
        print(f"      n = {s['n']}, mean = {s['mean']:+.6f}, SD = "
              f"{s['sd']:.6f}, p2.5 = {s['p2_5']:+.6f}, p97.5 = "
              f"{s['p97_5']:+.6f}, fraction <= {T_ANCHOR_LIT} = {frac:.4f}, "
              f"mean/({T_ANCHOR_LIT}) = {s['mean'] / T_ANCHOR_LIT:+.4f}   "
              f"({N_SIM} draws, {time.time() - tb:.1f}s)")
        print(f"      null-versus-observed placement: observed "
              f"{T_ANCHOR_LIT} (recomputed {rho_full_direct!r}) vs the "
              f"band [{s['p2_5']:+.6f}, {s['p97_5']:+.6f}] -> observed "
              f"is {'BELOW the 2.5th percentile' if T_ANCHOR_LIT <= s['p2_5'] else ('INSIDE the 95% band' if T_ANCHOR_LIT <= s['p97_5'] else 'ABOVE the 97.5th percentile')}")
        print(f"      draw mean vs 0 (AGENTS 4: does the null centre on "
              f"zero?): mean = {s['mean']:+.6f}, sd/sqrt(n) = "
              f"{s['sd'] / np.sqrt(s['n']):.6f}")
    word_m3 = p4c.word_m3_artifact(T_ANCHOR_LIT,
                                   p4c.draw_summary(m3[runs[0][0]])["p2_5"])
    word_m3_disp = word_m3 + ("  [PROVISIONAL: smoke run]" if SMOKE else "")
    print(f"\n  FROZEN M-3 WORD (primary only): {T_ANCHOR_LIT} vs p2.5 = "
          f"{p4c.draw_summary(m3[runs[0][0]])['p2_5']:+.6f}  ->  "
          f"{word_m3_disp}")
    print("  (both sensitivities are reported above with numbers and NO "
          "word, frozen M-3)")

    # =====================================================================
    banner("M-4 -- DETECTION LIMIT BY PLANTING (frozen; NO WORD)", "-")
    print("  M-DEC4 in force: z = rank_normal_z of delta over the frame, "
          "0 off-frame; u ~ N(0,1) for every raw row (u first, keeping "
          "simulate_rho's rng order); s_e = SD of the recorded own_e.b "
          "(ddof = 0); at r0 = 0 the plant is s_e*u -- pure independent "
          "noise, literal.")
    z_frame = p4c.rank_normal_z(x)
    z_raw = np.zeros(N_RAW)
    z_raw[frame_idx] = z_frame
    s_e = float(np.std(y, ddof=0))
    print(f"  s_e = {s_e!r} (SD of the recorded own_e.b over "
          f"{T_ROWS} frame rows, ddof = 0); z: mean "
          f"{z_frame.mean():.3e}, sd {z_frame.std(ddof=0)!r}; off-frame "
          f"z = 0 on {n_off} raw rows")
    grid = [float(v) for v in R0_GRID]
    m4 = {}
    for r0 in grid:
        tb = time.time()
        rhos, kept = simulation_run(E_iso, sw_primary, N_PLANT, W, W_SE,
                                    M_SE, HGVS, delta_raw,
                                    r0=r0, s_e=s_e, z=z_raw)
        m4[r0] = rhos
        gate(f"G-M4 every M-4 draw kept exactly {T_ROWS} rows -- r0 = "
             f"{r0:+.2f}",
             int(kept.min()) == T_ROWS and int(kept.max()) == T_ROWS,
             f"kept rows: min {int(kept.min())}, max {int(kept.max())} "
             f"over {N_PLANT} draws")
        print(f"      r0 = {r0:+.2f}: n = {len(rhos)}, mean observed rho = "
              f"{float(np.mean(rhos)):+.6f}, sd = "
              f"{float(np.std(rhos, ddof=1)):.6f}  ({time.time() - tb:.1f}s)")
    pc = p4c.power_curve(grid, m4)
    mde = p4c.min_detectable_effect(grid, list(pc["power"]), target=0.80)
    slope, intercept = p4c.attenuation_slope(grid, list(pc["mean_rho"]))
    print(f"\n  r0 = 0 band percentiles that define the tails: "
          f"q_lo = {pc['q_lo']:+.6f}, q_hi = {pc['q_hi']:+.6f}")
    print(f"      {'r0':>7s} {'mean observed rho':>18s} {'sd':>9s} "
          f"{'power':>8s}")
    for i, r0 in enumerate(grid):
        d = m4[r0]
        print(f"      {r0:+7.2f} {float(np.mean(d)):+18.6f} "
              f"{float(np.std(d, ddof=1)):9.6f} "
              f"{float(pc['power'][i]):8.4f}")
    print(f"  minimum detectable |r0| at 80% power (decision I5, both "
          f"sides shown): negative side = {mde['neg']}, positive side = "
          f"{mde['pos']}, headline (smaller of the two) = "
          f"{mde['headline']}")
    print(f"  attenuation slope of mean observed rho against r0 = "
          f"{slope:+.6f} (intercept {intercept:+.6f}) over the 9-point "
          f"grid")
    # ---- G-M5 (frozen) with M-DEC6's rule -------------------------------
    means = np.array([float(np.mean(m4[r0])) for r0 in grid])
    ses = np.array([float(np.std(m4[r0], ddof=1)) / np.sqrt(len(m4[r0]))
                    for r0 in grid])
    pair_ok = []
    for i in range(len(grid) - 1):
        tol_pair = 2.0 * np.sqrt(ses[i] ** 2 + ses[i + 1] ** 2)
        ok = means[i + 1] >= means[i] - tol_pair
        pair_ok.append(ok)
        print(f"  G-M5 pair {grid[i]:+.2f} -> {grid[i + 1]:+.2f}: mean "
              f"{means[i]:+.6f} -> {means[i + 1]:+.6f}; required "
              f"mean[j] >= mean[i] - 2*sqrt(SE_i^2+SE_j^2) = "
              f"{means[i] - tol_pair:+.6f} (SE_i = {ses[i]:.6f}, SE_j = "
              f"{ses[i + 1]:.6f}) -> {'OK' if ok else 'FAIL'}")
    gate("G-M5 planting response: all 8 adjacent pairs non-decreasing "
         "within Monte-Carlo error (M-DEC6)", all(pair_ok),
         f"{sum(pair_ok)}/8 pairs pass; a failing pair is not tolerated, "
         "N is not raised and the tolerance is not widened")

    # =====================================================================
    banner("M-5 -- BETWEEN- / WITHIN-POSITION DECOMPOSITION (frozen)", "-")
    print("  M-DEC7 in force: d3 is position-level; 10 equal-count bins "
          "over the DISTINCT resolved frame positions, unresolved "
          "positions in the eleventh bin; rows inherit their position's "
          "bin.  Positions with >= 5 finite rows qualify (frozen).")
    m5 = {}
    for view in ("full", "H"):
        m_ = hmask if view == "H" else np.ones(T_ROWS, dtype=bool)
        pt = p4c.between_within_decomposition(x[m_], y[m_], pos[m_],
                                              min_rows=5)
        d_ci, _, _ = cluster_draws(
            pos[m_] if view == "H" else pos,
            (lambda idx, m_=m_: (lambda d: np.array(
                [d["rho_between"], d["rho_within"]]))(
                p4c.between_within_decomposition(x[m_][idx], y[m_][idx],
                                                 pos[m_][idx],
                                                 min_rows=5))),
            N_BOOT, SEED)
        lo_b, hi_b, nf_b = p4c.pct_ci(d_ci[:, 0])
        lo_w, hi_w, nf_w = p4c.pct_ci(d_ci[:, 1])
        m5[view] = {"between": pt["rho_between"], "within": pt["rho_within"],
                    "lo_b": lo_b, "hi_b": hi_b, "lo_w": lo_w, "hi_w": hi_w,
                    "nqual": pt["n_qualifying"], "npos": pt["n_positions"],
                    "nf": nf_w}
        print(f"\n      {view:4s}: A222V components (qualifying positions "
              f"{pt['n_qualifying']} of {pt['n_positions']}):")
        print(f"          rho_between = {pt['rho_between']:+.9f}  CI "
              f"[{lo_b:+.6f}, {hi_b:+.6f}]  ({nf_b} finite draws, "
              f"position-cluster, both components recomputed per resample)")
        print(f"          rho_within   = {pt['rho_within']:+.9f}  CI "
              f"[{lo_w:+.6f}, {hi_w:+.6f}]  ({nf_w} finite draws)")
    m5_bg = {}
    print(f"\n      {'bg_id':10s} {'arm':4s} {'view':4s} {'between':>12s} "
          f"{'within':>12s} {'qualifying':>10s}")
    for b in bgs:
        rb = A.bg_rows[b]
        for view in ("full", "H"):
            m_ = np.isin(rb["position"].to_numpy(), list(A.Hset)) \
                if view == "H" else np.ones(len(rb), dtype=bool)
            d = p4c.between_within_decomposition(
                rb["delta"].to_numpy(float)[m_], y[pos_idx_of[b]][m_],
                rb["position"].to_numpy()[m_], min_rows=5)
            m5_bg[(b, view)] = (d["rho_between"], d["rho_within"])
            print(f"      {b:10s} {table.loc[b, 'arm']:4s} {view:4s} "
                  f"{d['rho_between']:+12.6f} {d['rho_within']:+12.6f} "
                  f"{d['n_qualifying']:10d}")
    print("\n  p_spec(neg) per component (N = 78):")
    m5_pspec = {}
    for view in ("full", "H"):
        for ci, cname in ((0, "between"), (1, "within")):
            nuls = np.array([m5_bg[(b, view)][ci] for b in N_ids])
            tgt = m5[view][cname]
            pv, kv, nv = p4c.p_spec(tgt, nuls, mode="neg")
            beat = sorted(np.array(N_ids)[nuls <= tgt].tolist())
            m5_pspec[(cname, view)] = (pv, kv, beat)
            print(f"      {cname:8s} {view:4s}: rho = {tgt:+.6f}, "
                  f"p = (1+{kv})/(1+{nv}) = {pv:.6f}, at-or-below nulls = "
                  f"{beat}")
    word_m5 = p4c.word_m5_carry(
        (m5["full"]["lo_w"], m5["full"]["hi_w"]),
        m5_pspec[("within", "full")][0],
        (m5["full"]["lo_b"], m5["full"]["hi_b"]),
        m5_pspec[("between", "full")][0])
    word_m5_disp = word_m5 + ("  [PROVISIONAL: smoke run]" if SMOKE else "")
    print(f"\n  FROZEN M-5 WORD (full frame, A222V): within CI "
          f"[{m5['full']['lo_w']:+.6f}, {m5['full']['hi_w']:+.6f}] "
          f"p_within = {m5_pspec[('within', 'full')][0]:.6f}; between CI "
          f"[{m5['full']['lo_b']:+.6f}, {m5['full']['hi_b']:+.6f}] "
          f"p_between = {m5_pspec[('between', 'full')][0]:.6f}  ->  "
          f"{word_m5_disp}")

    # ---- surrogate nulls S1 / S2 ---------------------------------------
    print("\n  M-5 surrogate nulls (frozen: 1,000 draws each, SEED 0): "
          "S1 permutes own_e.b within positions; S2 permutes within the "
          "11 d3-distance groups (M-DEC7).  Both preserve the frame's "
          "row count.  These are RE-LABELLING nulls, not bootstraps.")
    d3_pos = {}
    for p_ in sorted(frame.position.unique()):
        d3_pos[int(p_)] = p3d.d3_of(int(p_), ca)
    res_pos = [p_ for p_, v in d3_pos.items() if np.isfinite(v)]
    res_vals = np.array([d3_pos[p_] for p_ in res_pos])
    pos_bin_lab = p4c.equal_count_bins(res_vals, 10)
    bin_of = dict(zip(res_pos, pos_bin_lab))
    posbin = np.array([bin_of.get(int(p_), 10) for p_ in pos])
    print(f"      resolved frame positions = {len(res_pos)} of {T_POS}; "
          f"unresolved = {T_POS - len(res_pos)} (eleventh bin); rows per "
          f"bin = {np.bincount(posbin, minlength=11).tolist()}")
    obs_m5 = p4c.spearman(x, y)
    for sname, groups in (("S1 (within position)", pos),
                          ("S2 (within d3-distance group)", posbin)):
        rng_s = np.random.default_rng(SEED)
        draws = np.empty(N_PERM)
        for i in range(int(N_PERM)):
            draws[i] = p4c.permuted_spearman(x, y, groups, rng_s)
        s = p4c.draw_summary(draws)
        frac = s["mean"] / T_ANCHOR_LIT
        m5.setdefault("null", {})[sname] = (s, frac)
        print(f"      {sname}: mean = {s['mean']:+.6f}, SD = {s['sd']:.6f}, "
              f"95% range [{s['p2_5']:+.6f}, {s['p97_5']:+.6f}], "
              f"fraction of {T_ANCHOR_LIT} = {frac:+.4f}  "
              f"({N_PERM} draws)")
        zc = abs(s["mean"]) / (s["sd"] / np.sqrt(s["n"]))
        print(f"          centres on zero? |mean| / (sd/sqrt(n)) = "
              f"{zc:.2f} -> the null {'centres at zero' if zc < 3 else 'is offset from zero: the excess over it is the real result'} "
              f"(AGENTS 4)")
    print(f"      observed anchor = {obs_m5:+.9f} "
          f"(recomputed; frozen literal {T_ANCHOR_LIT})")
    print("      the S1/S2 retained fractions above are the frozen "
          "'fraction of -0.088118' (M-DEC8)")

    # =====================================================================
    banner("M-6 -- STABILITY OF THE FROZEN PLACEBO TEST (frozen)", "-")
    # ---- G-M7 first (frozen): every position exactly once ---------------
    obs_f = p4c.observed_placebo(dmat, y, pos, 0, n_idx)
    rho_A_f = float(obs_f["rho_A"][0])
    k_f7 = int(obs_f["k"][0])
    p_f7 = float(obs_f["p_spec_neg"][0])
    beat_f7 = sorted(np.array(N_ids)[
        obs_f["rho_N"][0] <= rho_A_f].tolist())
    note("G-M7 every-position-once rho_A222V (full)", rho_A_f, T_RHO_FULL,
         TOL_9DP)
    gate("G-M7 every-position-once k and p_spec (full) == observed",
         k_f7 == 1 and abs(p_f7 - T_P_FULL) < TOL_EXACT
         and beat_f7 == T_BEATERS_FULL,
         f"k = {k_f7} target 1; p = (1+{k_f7})/79 = {p_f7!r} target "
         f"{T_P_FULL!r} (2/79); beaters {beat_f7} target "
         f"{T_BEATERS_FULL}")
    obs_h = p4c.observed_placebo(dmat[:, hmask], y[hmask], pos[hmask], 0,
                                 n_idx)
    rho_A_h = float(obs_h["rho_A"][0])
    k_h7 = int(obs_h["k"][0])
    p_h7 = float(obs_h["p_spec_neg"][0])
    beat_h7 = sorted(np.array(N_ids)[
        obs_h["rho_N"][0] <= rho_A_h].tolist())
    note("G-M7 every-position-once rho_A222V (H)", rho_A_h, T_RHO_H,
         TOL_9DP)
    gate("G-M7 every-position-once k and p_spec (H) == observed",
         k_h7 == 3 and abs(p_h7 - T_P_H) < TOL_EXACT
         and beat_h7 == T_BEATERS_H,
         f"k = {k_h7} target 3; p = (1+{k_h7})/79 = {p_h7!r} target "
         f"{T_P_H!r} (4/79); beaters {beat_h7} target {T_BEATERS_H}")

    # ---- draw-by-draw reference for the whole-placebo bootstrap ---------
    # (per-view id arrays: np.unique positions differ between the full and
    # H views -- 654 vs 455 -- so each view draws ids in ITS OWN index
    # space; drawn once here, before any M-6 number exists.)
    for view, sub, subpos in (("full", dmat, pos),
                              ("H", dmat[:, hmask], pos[hmask])):
        tb = time.time()
        nk_v = int(np.unique(subpos).size)
        rng_p = np.random.default_rng(SEED)
        ids_placebo = np.empty((N_REF_PLACEBO, nk_v), dtype=np.int64)
        for i in range(N_REF_PLACEBO):
            ids_placebo[i] = rng_p.integers(0, nk_v, nk_v)
        fast = p4c.whole_placebo_boot_from_ids(sub, y if view == "full"
                                               else y[hmask], subpos, 0,
                                               n_idx, ids_placebo)
        ref = p4c.whole_placebo_reference(sub, y if view == "full"
                                          else y[hmask], subpos, 0,
                                          n_idx, ids_placebo)
        m1_ = float(np.max(np.abs(fast["rho_A"] - ref["rho_A"])))
        m2_ = float(np.max(np.abs(fast["rho_N"] - ref["rho_N"])))
        m3_ = float(np.max(np.abs(fast["k"].astype(float)
                                  - ref["k"].astype(float))))
        m4_ = float(np.max(np.abs(fast["p_spec_neg"] - ref["p_spec_neg"])))
        gate(f"G-M3(ii) whole-placebo draw-by-draw vs slow reference "
             f"({view}, {N_REF_PLACEBO} draws, capped at min(N_REF, 50))",
             max(m1_, m2_, m4_) < TOL_12 and m3_ == 0.0,
             f"max|fast - reference|: rho_A {m1_:.3e}, rho_N {m2_:.3e}, "
             f"k {m3_}, p_spec {m4_:.3e} (gate < 1e-12 / exact) in "
             f"{time.time() - tb:.1f}s")

    m6 = {}
    for view, sub, subpos, suby, thr in (
            ("full", dmat, pos, y, 0.05),
            ("H", dmat[:, hmask], pos[hmask], y[hmask], 0.10)):
        tb = time.time()
        res = p4c.whole_placebo_boot(sub, suby, subpos, 0, n_idx,
                                     n_draw=N_STAB, seed=SEED)
        m6[view] = {"res": res, "thr": thr, "t": time.time() - tb}
        kvals, kcnt = np.unique(res["k"], return_counts=True)
        prob = float(np.mean(res["p_spec_neg"] <= thr))
        z_draws = res["z"]
        z_lo, z_hi, z_nf = p4c.pct_ci(z_draws)
        rho_A_obs = rho_A_f if view == "full" else rho_A_h
        rn_obs = obs_f["rho_N"][0] if view == "full" else obs_h["rho_N"][0]
        z_obs = float((rho_A_obs - rn_obs.mean())
                      / rn_obs.std(ddof=0))
        m6[view].update(prob=prob, z_obs=z_obs, z_lo=z_lo, z_hi=z_hi,
                        z_mean=float(np.nanmean(z_draws)))
        word_v = p4c.word_m6_stable(prob)
        m6[view]["word"] = word_v + ("  [PROVISIONAL: smoke run]"
                                     if SMOKE else "")
        print(f"\n      {view} view ({N_STAB} draws, seed {SEED}, "
              f"{m6[view]['t']:.1f}s; every background's rho_b "
              f"re-derived each draw):")
        print(f"        distribution of k = #{{b in N: rho_b <= "
              f"rho_A222V}}: " + ", ".join(
                  f"k={int(a)}: {int(c)} draws"
                  for a, c in zip(kvals, kcnt)))
        print(f"        P(p_spec <= {thr}) = {prob:.4f}   "
              f"(p_spec observed = {float(obs_f['p_spec_neg'][0]) if view == 'full' else float(obs_h['p_spec_neg'][0]):.6f}; "
              f"frozen threshold {thr})")
        print(f"        z = (rho_A222V - mean rho_N) / SD rho_N: observed "
              f"{z_obs:+.4f}, bootstrap CI [{z_lo:+.4f}, {z_hi:+.4f}] "
              f"(mean of draws {m6[view]['z_mean']:+.4f}, {z_nf} finite) "
              "-- ILLUSTRATIVE SCALE CONTEXT ONLY (AGENTS 3: the primary "
              f"claim is the probability above and the frozen word)")
        print(f"        FROZEN M-6 WORD ({view}): {m6[view]['word']}")
    print(f"\n  FROZEN M-6 WORDS: full = {m6['full']['word']} "
          f"(P = {m6['full']['prob']:.4f} vs 0.80 STABLE / 0.50 FRAGILE "
          f"boundary); H = {m6['H']['word']} (P = {m6['H']['prob']:.4f}).")

    # =====================================================================
    banner("ANALYSIS-SET ACCOUNTING (AGENTS 5: every row accounted for)",
           "-")
    print(f"    raw fit frame                     : {N_RAW} rows "
          f"({len(pos_sorted)} positions)")
    print(f"    task32 analysis table             : {len(t32)} rows "
          f"(recorded own_e_b finite: {int(m_rec.sum())})")
    print(f"    anchor frame (delta & own_e_b)    : {len(frame)} rows / "
          f"{frame.position.nunique()} positions")
    print(f"    H view                            : {int(hmask.sum())} rows "
          f"/ {len(A.Hset)} positions")
    print(f"    off-frame raw rows (delta NaN)    : {n_off} rows (target "
          f"2,377)")
    print(f"    each simulation draw keeps        : {T_ROWS} rows "
          f"(gated per run, G-M4)")
    print(f"    rho_b rows per background         : script 125's own join, "
          f"gated (G-ALIGN); own-position rows are absent from the score "
          f"files (125's G-C)")

    # =====================================================================
    banner("GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    n_skip = sum(1 for _, ok, d in gates if not ok and "SKIPPED" in d)
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print(f"\n  {len(gates) - n_fail}/{len(gates)} checks PASS, "
          f"{n_fail} FAIL ({n_skip} of the FAILs are smoke SKIPS).")

    banner("LIMITATIONS (AGENTS 6; printed, not only written down)", "-")
    print("  1. Reproduction is not replication: G-M0..G-M4, G-XFOLD and "
          "G-ALIGN re-derive cached project numbers to validate this code "
          "-- a unit test, not independent evidence for any claim.")
    print("  2. Frozen block section 0: these constructions use quantities "
          "seen in earlier exploratory work; they are NOT independent of "
          "what was already seen.  Out-of-sample evidence in this "
          "programme comes only from the neighbour-arm and model-ladder "
          "pre-registrations.")
    print("  3. p_spec / p_spec_adj are one-sided signed rank counts over "
          "78 nulls, not tail areas of an exchangeable distribution.")
    print("  4. M-3/M-4 re-run the project's own estimator on simulated "
          "inputs (a re-derivation null, AGENTS 4) and inherit every "
          "assumption of that estimator, including the multiplicative "
          "no-interaction expectation.  M-3's PRIMARY sw_i = 0 by "
          "M-DEC1, so the WT side is not perturbed in the primary at all.")
    print("  5. M-5's S1/S2 re-label own_e.b within groups; they preserve "
          "position structure (S1) or the regional distance profile (S2) "
          "and nothing else.")
    print("  6. Every CI here resamples 654 (455 on H) positions, never "
          "rows; effective n is the number of positions.")
    print("  7. Nothing here changes a frozen Phase 1/2 result, and no "
          "result here may be described as confirming or undermining a "
          "GB1, RBD, neighbour-arm or model-ladder result (frozen "
          "section 5).")
    print(f"\n  Elapsed {time.time() - t0:.1f}s")

    if n_fail:
        if SMOKE and n_fail == n_skip:
            print("\nSMOKE RESULT: all executed checks PASS; the only "
                  "FAIL is the intentional G-M3(iii) SKIPPED sub-gate.  "
                  "G-M3 is decided on the N_BOOT=10000 run, and every "
                  "frozen word printed above is PROVISIONAL until the "
                  "full run.")
            return 0
        print("\nGATE FAIL -- A4 stops here (exit 3).  Do not raise N, "
              "do not adjust a threshold.")
        return 3
    print("\nGATE PASS -- G-M0..G-M7 plus G-XFOLD and G-ALIGN all pass; "
          "the frozen outcome words above are the result of this block."
          + ("  (SMOKE: words are PROVISIONAL until the full run.)"
             if SMOKE else ""))
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except GateFail as e:
        print("\nGATE TABLE (up to the failure):")
        for gid, ok, detail in gates:
            print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
        print(f"\nGATE FAIL: {e} -- A4 stops here (exit 3).  Do not raise "
              "N, do not adjust a threshold.")
        print(f"Elapsed {time.time() - t0:.1f}s")
        rc = 3
    sys.exit(rc)
