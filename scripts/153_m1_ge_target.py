"""Script 153 -- Task A3, Module M1: MTHFR monotone global-epistasis
target (GE-ISO primary; GE-SIG and GE-LIN-CF as sensitivities).

PRE-REGISTRATED: this docstring was written BEFORE the first run of this
script (AGENTS 6).  Nothing below is edited after any number produced
here has been seen.  The script implements the FROZEN block
docs/tasks/phase3-overnight/prereg/MTHFR_GE_TARGET_PREREG_v1.md (47
lines, sha256
73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c)
exactly; the sha256 and line count are re-checked at startup (gate
G-M0) and the frozen section 2.6-5 is re-printed verbatim from disk at
runtime.  The frozen file is read-only and never edited.  Per its
section 1 this changes NO frozen Phase 2 result -- it re-targets the
anchor, and no result here may be described as confirming or
undermining a GB1 or RBD result (frozen section 7).

SOURCES QUOTED VERBATIM AT RUNTIME with file names and line numbers,
read from disk so the quote cannot drift from the code:
  * rebuild_interaction_fit (the two-pass own-context fit)
        scripts/lib/stats_ext.py   lines 63-88
  * the weighted aggregation of per-condition residuals
        wls_line                   scripts/lib/own_context.py lines 48-66
        fit_interaction (expected / resid / valid, the aggregation at
        line 165, and the >2-missing NaN rule at lines 179-181)
                                   scripts/lib/own_context.py lines 143-187

THE ONLY PLUGGABLE COMPONENT (frozen 2.1) is the per-condition
expectation E_c(v) as a function of w(v).  FOUR expectations are pushed
through ONE shared code path `aggregate(E)` so that any difference
between variants comes from E and from nothing else:

  identity   E = e2["expected"] -- the project's own linear expectation
             straight from rebuild_interaction_fit (frozen 2.2: with
             this plugged in the rebuild must reproduce the recorded
             own_e.b; that is gate G-M1).
  GE-LIN-CF  (frozen 2.5) the project's own linear expectation with
             ONLY the correction curves (cb, cr) cross-fit by fold --
             attributes any change to cross-fitting vs monotonicity.
  GE-ISO     (frozen 2.3) PRIMARY: weighted isotonic (non-decreasing)
             regression of m_score_c on w, weights 1/m_se^2, 5-fold
             position cross-fitting.
  GE-SIG     (frozen 2.4) SENSITIVITY: four-parameter logistic
             a + b/(1+exp(-k(w-m))), weighted least squares, same folds.

  r_c^GE = m_score_c - E_c(w)          (frozen 2.6)
  own_e.b^GE = wls_line(r^GE, m_se, CONCS, valid) intercept -- the
             project's own aggregation, with the project's valid mask
             and the project's >2-missing NaN rule.

INTERPRETATION DECISIONS (each fixed here before running; they
interpret the frozen text, they do not change any frozen constant):
 D1  w(v) = fit["w"]["fitness"], the WT-arm fitted fitness returned by
     rebuild_interaction_fit.
 D2  The shared pipeline `aggregate(E)` is literally the project's own
     lines: resid = where(valid, m_score - E, nan) (own_context 163),
     e_b = wls_line(resid, m_se, concs, valid) (own_context 165),
     rows with >2 invalid cells set to NaN (own_context 179-181).
 D3  valid = fit["valid"] (the project's second-pass valid mask) is
     used for ALL FOUR expectations, so the variants differ only in E.
 D4  GE-LIN-CF cross-fits ONLY cb/cr.  The A222V reference line and the
     per-variant WT-arm fits are single-row / per-variant quantities
     with no training set, so they cannot be cross-fit and are left as
     the project has them.  cb/cr for fold k are fitted on the
     project's own keep-mask rows (w.logl > LOGL_CUTOFF and
     e1.logl > LOGL_CUTOFF, stats_ext 81-83) outside fold k.
 D5  Folds (frozen 2.3): positions = np.unique(raw["start"]) sorted;
     perm = np.random.default_rng(0).permutation(positions); a
     position's fold = (its rank in perm) mod 5; every variant inherits
     its position's fold.  5 folds.
 D6  Fit rows for GE-ISO / GE-SIG (frozen 2.3/2.4: "regression of
     m_score_c on w, weights 1/m_se^2"): all raw rows with finite
     m_score_c, m_se_c > 0 and finite w; the frozen block adds no logl
     cutoff, so none is applied here.  train = folds != k, test =
     fold == k.  Isotonic out_of_bounds="clip" (the frozen block is
     silent on extrapolation; clip is the non-extrapolating standard
     and is stated here).
 D7  GE-SIG is constrained b >= 0 and k >= 0 so the fitted function is
     non-decreasing BY CONSTRUCTION -- G-M2 is a hard gate in the
     frozen block.  p0 = (min y, max y - min y, median w, 1/sd w).  If
     curve_fit raises RuntimeError the pre-registered retry chain is
     the same p0 with k0 scaled by 0.2, then by 5; if all three fail
     the script exits 3 (no threshold loosened, no N raised).  Every
     retry is printed.
 D8  A raw row's position is the raw file's own `start` column,
     cross-checked against task32's `position` for every overlapping
     hgvs (gate).
 D9  Row alignment for (c)-(f): A.a222v_rows is frame-order
     (verified here); each background's rows are aligned to frame rows
     by re-running script 125's own score join (125 lines 855-866) and
     are GATED rowwise against A.bg_rows -- position exact, own_e_b
     exact, recomputed delta < 1e-12, recomputed original rho_b and
     rho_H == the cached table to 1e-12 -- before any rho_b^GE is
     formed.  This is a gated transcription of 125's join, not a new
     construction.
 D10 (e) rank fraction = (1 + #{b in S : rho_b^GE <= rho_A^GE}) / 19,
     the ascending rank of A222V among Arm S u {A222V} (n = 18 + 1).
 D11 p_boot reported beside each rho^GE CI uses Phase 1's own formula,
     scripts/lib/stats.py lines 27-31, quoted:
         p = min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0)
     "p_boot == 0.0 means no resample crossed zero -> report
     p < 1/n_boot."

GATES (ALL HARD; a failure prints GATE FAIL and the script exits 3;
the driver never retries exit 3; thresholds are never loosened and N is
never raised to pass a gate).  A smoke run (N_BOOT != 10000) SKIPS
G-M3(iii) exactly as script 159 did: such a run cannot call G-M3 PASS,
and the decision is taken on the N_BOOT=10000 run.
  G-M0  inputs: frozen prereg sha256/line count (above); rho-table
        sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796;
        3d-distance table sha256
        69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de.
  G-M1  identity (frozen 2.2), four sub-checks:
        (a) my e1 + keep reproduce the correction curves inside
            rebuild_interaction_fit (< 1e-12 on a w-grid);
        (b) aggregate(e2["expected"]) == e2["e_b"]: identical NaN
            pattern, max|diff| < 1e-12 (expected exactly 0);
        (c) aggregate(identity) == the RECORDED own_e_b: the comparison
            set is exactly the rows with a RECORDED own_e_b (the frozen
            rule's 10,757 rows), max|diff| < 1e-12 and zero rows above
            1e-12 there, plus zero rows that are recorded but not
            rebuildable (a recorded value must always rebuild).  Rows
            where the rebuild is finite but no value was recorded are
            EXPECTED (the raw file carries nonsense/synonymous rows the
            atlas never assigned own_e_b to) and are counted and
            printed as information only.
            *** DISCLOSURE (AGENTS 6): the first smoke run
            (N_BOOT=300, before any GE quantity was computed) failed
            this sub-gate because the initial text above my own
            addition demanded zero finite/NaN disagreements over ALL
            13,134 raw rows -- stricter than the frozen rule, which
            compares the recorded rows.  The clause was corrected to
            the frozen comparison set on that evidence alone, with the
            1e-12 threshold unchanged and before a single GE number
            existed.  This is a gate-text correction, not a result-
            driven change; the failure output is preserved in the
            build log. ***
        (d) on every valid (row, condition) cell, each of the three GE
            expectations is finite (so no NaN can enter the shared
            aggregation).
  G-M2  each fitted monotone expectation (GE-ISO, GE-SIG; 4 conditions
        x 5 folds each) is non-decreasing on a fixed 201-point
        w-grid (min diff >= -1e-12).  GE-LIN-CF is not a function of w
        alone; its effective slopes are printed instead (decision).
  G-M3  the bootstrap: (i) every-cluster-once reproduces each anchor
        point estimate (< 1e-12: original, GE-LIN-CF, GE-ISO,
        GE-SIG); (ii) draw-by-draw agreement of the corrected routine
        with the slow reference on identical pre-drawn ids for the
        GE-ISO anchor (N_REF draws, < 1e-12); (iii) at N_BOOT=10000
        the Phase 1 published CI [-0.1173334458953319,
        -0.0595113844951173] reproduces with Phase 1's own routine
        (endpoints < 1e-9) and the corrected routine matches Phase
        1's routine draw-set to < 1e-12 (SKIPPED in smoke).
  G-M4  Phase 2 reproduction rows: A222V rho -0.088118064 (full) /
        -0.090021683 (H), each < 1e-9 from two independent sources
        (task32 columns directly and script 125's frame rows, agreeing
        with each other to 1e-12); frozen p_spec 2/79 (beaters
        {G_P254F}) and 4/79 (beaters {AV_195, AV_220, G_P254F}), both
        exact; rho-table sha256 (G-M0); structure counts: 96
        backgrounds, |N| = 78, arms G40/V38/S18, anchor 10,757 rows /
        654 positions, H = 455 positions / 7,526 rows.
  G-M5  fold integrity: every position belongs to exactly one fold;
        for every fold k the train positions and test positions are
        disjoint (hence every variant is predicted by a fit that
        excluded its whole position); every row is in exactly one test
        fold.
  G-ALIGN (AGENTS 5, see D9): the 96 background row sets and the
        A222V row set reproduce script 125's own construction exactly
        before rho_b^GE is formed; original rho_b recomputed from the
        aligned rows must match A.point[b] and the cached rho table to
        1e-12.

FROZEN OUTCOME RULE (verbatim, frozen section 4; the primary governs;
the two sensitivities are reported with the same words, and any
disagreement is stated plainly):
  GE-SURVIVES: the CI of rho^GE (GE-ISO) excludes zero in the
      negative direction AND p_spec^GE(full) <= 0.05 AND
      p_spec^GE(H) <= 0.10.
  GE-WEAKENS: the CI excludes zero in the negative direction but at
      least one p_spec^GE condition fails.
  GE-DOES-NOT-SURVIVE: the CI includes zero or the sign reverses.
No other outcome word appears anywhere in this script's output, and
nothing here is interpreted beyond these words (frozen section 4: "Do
not interpret beyond the pre-registered words").

QUANTITIES (frozen section 3), reported side by side for GE-ISO,
GE-SIG, GE-LIN-CF, each next to its reference value, which is
RECOMPUTED independently here and printed beside the frozen target
(planning doc rule 14):
  (a) Spearman(own_e.b^GE, own_e.b) over the 10,757 rows;
  (b) rho^GE = Spearman(delta_ESM, own_e.b^GE) with corrected
      position-cluster bootstrap CI (10,000 draws, seed 0) next to
      -0.088118, plus the shrinkage 1 - rho^GE / rho;
  (c) all 96 backgrounds' rho_b^GE (script 125's rows, own-position
      exclusion as in 125) and frozen-form p_spec^GE on the full frame
      and on H (455 positions), at-or-below nulls named;
  (d) shift-adjusted p_spec_adj^GE (leave-one-out OLS on
      mean|delta_b|, Diagnostics II D9), full and H;
  (e) A222V's rank fraction within Arm S u {A222V} (n = 19, not a
      test);
  (f) Spearman(rho_b^GE, d3_b) across the 67 resolved nulls with a
      background-level bootstrap CI, next to +0.7316.

RESAMPLING UNITS (AGENTS 3, stated again in the output): (b) and G-M3
resample POSITION clusters (654 positions of the 10,757-row anchor
frame -- effective n is the number of positions, never the number of
rows); (f) resamples BACKGROUNDS with their already-computed values
held fixed.  Bootstrap p-values are reported as primary (Phase 1's
formula, D11); no z-score is reported anywhere; effect sizes are
printed beside every significance claim.

LIMITATIONS (printed again with the output, AGENTS 6):
  * Reproduction is not replication: G-M1/G-M3/G-M4 re-derive cached
    project numbers to validate this code -- a unit test, not
    independent evidence for any claim.
  * All four expectations share the A222V reference line and the
    per-variant WT-arm fits (D4); only GE-ISO/GE-SIG replace the
    expectation wholesale.  A construction-level artifact common to
    the WT-arm fits would appear in every variant.
  * GE-ISO and GE-SIG score the same variants they are fit on, but
    never the tested variant's own position: fold is a function of
    position (G-M5).
  * The anchor frame is one background (the A222V arm); the
    position-cluster bootstrap resamples 654 positions.
  * p_spec / p_spec_adj are one-sided signed rank counts over 78
    nulls, not tail areas of an exchangeable distribution.
  * This script imports no torch / esm / thermompnn (rule 1); it runs
    fully in session 3a on cached data.

Usage:
  smoke:  N_BOOT=300 venv/bin/python3 scripts/153_m1_ge_target.py
  full:   N_BOOT=10000 SEED=0 venv/bin/python3 scripts/153_m1_ge_target.py \
            > docs/tasks/phase3-overnight/PHASE3_A3_FULL_OUTPUT.txt
"""

import hashlib
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib import phase2_diag as pdg                       # noqa: E402
from scripts.lib import phase3_common as p3c                     # noqa: E402
from scripts.lib.own_context import (CONCS, LOGL_CUTOFF,         # noqa: E402
                                     MT_SCORE_COLS, MT_SE_COLS,
                                     WT_SCORE_COLS, fit_interaction,
                                     interpolate_correction,
                                     wls_line)
from scripts.lib.stats import position_cluster_bootstrap         # noqa: E402
from scripts.lib.stats_ext import rebuild_interaction_fit        # noqa: E402
from sklearn.isotonic import IsotonicRegression                  # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_REF = int(os.environ.get("N_REF", "500"))

PREREG = ROOT / "docs/tasks/phase3-overnight/prereg/MTHFR_GE_TARGET_PREREG_v1.md"
PREREG_SHA = ("73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c")
PREREG_LINES = 47
STATS_EXT = ROOT / "scripts/lib/stats_ext.py"
OWN_CONTEXT = ROOT / "scripts/lib/own_context.py"
RHO_TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
RHO_TABLE_SHA = ("e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796")
D3_PATH = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
D3_SHA = ("69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de")
RAW_PATH = ROOT / "data/raw/mthfrModel/results/folate_response_model5.csv"
T32_PATH = ROOT / "data/processed/task32_analysis_table.csv"
OUTDIR = ROOT / "data/processed/phase3"

# ---- targets from the frozen block / planning doc, printed beside every
# ---- value computed here (rule 14: recompute independently, print both)
T_RHO_FULL = -0.088118064
T_RHO_H = -0.090021683
T_ANCHOR_DOC = -0.088118
T_P_FULL = 2.0 / 79.0
T_P_H = 4.0 / 79.0
T_BEATERS_FULL = ["G_P254F"]
T_BEATERS_H = ["AV_195", "AV_220", "G_P254F"]
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.0595113844951173
T_GRAD_DOC = 0.7316
T_GRAD_140 = 0.731577372          # script 140's recorded 9-dp value
T_ROWS, T_POS, T_HPOS, T_HROWS = 10757, 654, 455, 7526
T_NBGS, T_NN = 96, 78
T_RESN = 67

VARIANTS = ["GE-ISO", "GE-SIG", "GE-LIN-CF"]
N_FOLDS = 5

TOL_12 = 1e-12
TOL_9DP = 1e-9
TOL_EXACT = 1e-15

t0 = time.time()
gates = []
sig_retries = []


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


def p_boot_phase1(draws):
    """Phase 1's own p_boot formula, scripts/lib/stats.py lines 27-31."""
    b = np.asarray(draws, dtype=float)
    b = b[~np.isnan(b)]
    return min(2 * min((b <= 0).mean(), (b >= 0).mean()), 1.0)


def logi4(w, a, b, k, m):
    """Four-parameter logistic (frozen 2.4): a + b / (1 + exp(-k (w - m)))."""
    return a + b / (1.0 + np.exp(-k * (np.asarray(w, float) - m)))


def outcome_word(rho, lo, hi, p_full, p_h):
    """Frozen section 4, applied literally.  The primary (GE-ISO) governs;
    the same function is applied to each sensitivity."""
    if hi < 0:                                   # CI excludes zero, negative
        if p_full <= 0.05 and p_h <= 0.10:
            return "GE-SURVIVES"
        return "GE-WEAKENS"
    return "GE-DOES-NOT-SURVIVE"                 # includes 0 or reverses


def main():
    banner("A3 / M1 -- MTHFR monotone global-epistasis target (script 153)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}")
    print("RESAMPLING UNITS: (b) and G-M3 = POSITION clusters (654 "
          "positions of the 10,757-row anchor frame); (f) = BACKGROUNDS "
          "(values held fixed).  Bootstrap p reported as primary "
          "(Phase 1 formula); no z-score anywhere.")
    print("DECISION RULE (pre-registered): any hard gate FAIL -> exit 3; "
          "thresholds are never loosened and N is never raised to pass a "
          "gate.  Smoke (N_BOOT != 10000) SKIPS G-M3(iii), so G-M3 cannot "
          "be called PASS on a smoke run.")
    if N_BOOT != 10000:
        print("*** SMOKE RUN: N_BOOT != 10000 -- G-M3(iii) CI "
              "reproduction is SKIPPED ***")

    # =====================================================================
    banner("G-M0 -- INPUT INTEGRITY (frozen block, read-only)", "-")
    sha = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    n_lines = len(PREREG.read_text().splitlines())
    gate("G-M0 prereg sha256", sha == PREREG_SHA,
         f"{sha} (target {PREREG_SHA})")
    gate("G-M0 prereg line count", n_lines == PREREG_LINES,
         f"got {n_lines} target {PREREG_LINES}")
    sha_r = hashlib.sha256(RHO_TABLE.read_bytes()).hexdigest()
    gate("G-M0 rho table sha256", sha_r == RHO_TABLE_SHA,
         f"{sha_r} (target {RHO_TABLE_SHA})")
    sha_d = hashlib.sha256(D3_PATH.read_bytes()).hexdigest()
    gate("G-M0 3d-distance table sha256", sha_d == D3_SHA,
         f"{sha_d} (target {D3_SHA})")

    print("\n  Frozen block sections 3-5, verbatim from disk (the rules "
          "this script applies):")
    prereg_lines = PREREG.read_text().splitlines()
    for i in range(20, 40):
        print(f"  {i+1:3d}| {prereg_lines[i]}")

    banner("QUOTED SOURCES (verbatim from disk; the one pluggable "
           "component is E_c)", "-")
    quote(STATS_EXT, 63, 88, "rebuild_interaction_fit")
    quote(OWN_CONTEXT, 48, 66, "wls_line -- the weighted aggregation")
    quote(OWN_CONTEXT, 143, 187,
          "fit_interaction -- expected / resid / valid / aggregation "
          "at line 165, NaN rule at 179-181")

    # =====================================================================
    banner("CONSTRUCTION -- data, folds, the four expectations", "-")
    tc = time.time()
    raw = pd.read_csv(RAW_PATH)
    t32 = pd.read_csv(T32_PATH)
    print(f"  raw rows = {len(raw)} (types: "
          f"{raw.type.value_counts().to_dict()}); task32 rows = {len(t32)}")

    # D8: position = raw `start`, cross-checked against task32
    chk = t32.merge(raw[["hgvs", "start"]], left_on="hgvs_pro",
                    right_on="hgvs", how="left")
    n_pos_bad = int((chk["position"] != chk["start"]).sum())
    n_no_start = int(chk["start"].isna().sum())
    gate("D8 position: raw start == task32 position (all task32 rows)",
         n_pos_bad == 0 and n_no_start == 0,
         f"mismatches = {n_pos_bad}, task32 rows absent from raw = "
         f"{n_no_start} (both must be 0)")
    raw_pos = raw["start"].to_numpy(int)

    # ---- the project's fit (imported, never reimplemented) --------------
    tb = time.time()
    fit = rebuild_interaction_fit(raw)
    print(f"  [rebuild_interaction_fit] {time.time() - tb:.1f}s")
    w = fit["w"]
    wf, wrem, wpost = w["fitness"], w["remediation"], w["post"]
    M = raw[MT_SCORE_COLS].to_numpy(float)
    Mse = fit["M_se"]
    valid = fit["valid"]
    i222 = fit["i222"]
    e2 = fit["e2"]
    w_mean = np.nanmean(raw[WT_SCORE_COLS].to_numpy(float), axis=1)
    n_all4 = int((valid.sum(axis=1) == 4).sum())
    n_anyv = int((valid.sum(axis=1) > 0).sum())
    print(f"  rows with any valid cell = {n_anyv}, all four valid = "
          f"{n_all4}; finite w = {int(np.isfinite(wf).sum())}")

    # ---- my own e1 + keep (D4), gated against rebuild's correction ------
    e1 = fit_interaction(M, Mse, wf, wrem, wpost, w_mean,
                         wf[i222], wrem[i222])
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb0 = interpolate_correction(wf[keep], e1["e_b"][keep])
    cr0 = interpolate_correction(wf[keep], e1["e_r"][keep])
    cb_ref, cr_ref = fit["correction"]
    g_grid = np.linspace(float(np.nanmin(wf)) - 0.1,
                         float(np.nanmax(wf)) + 0.1, 501)
    d_cb = float(np.max(np.abs(cb0(g_grid) - cb_ref(g_grid))))
    d_cr = float(np.max(np.abs(cr0(g_grid) - cr_ref(g_grid))))
    gate("G-M1(a) my e1+keep reproduce rebuild's correction curves",
         d_cb < TOL_12 and d_cr < TOL_12,
         f"cb max|diff| = {d_cb:.3e}, cr max|diff| = {d_cr:.3e} on a "
         f"501-point w-grid (gate < 1e-12)")

    # ---- folds (D5) ------------------------------------------------------
    pos_sorted = np.unique(raw_pos)
    rng = np.random.default_rng(0)
    perm = rng.permutation(len(pos_sorted))
    fold_of_pos = np.empty(len(pos_sorted), dtype=np.int64)
    fold_of_pos[perm] = np.arange(len(pos_sorted)) % N_FOLDS
    fold = fold_of_pos[np.searchsorted(pos_sorted, raw_pos)]
    print(f"  folds: {len(pos_sorted)} positions -> per-fold position "
          f"counts {np.bincount(fold_of_pos, minlength=N_FOLDS).tolist()}"
          f"; per-fold row counts {np.bincount(fold, minlength=N_FOLDS).tolist()}")

    # ---- identity E and the shared aggregation --------------------------
    def aggregate(E):
        """The project's own pipeline (D2): own_context lines 163, 165,
        179-181, with the project's valid mask (D3)."""
        resid = np.where(valid, M - E, np.nan)
        eb, _er, _df = wls_line(resid, Mse, CONCS, valid)
        bad = (~valid).sum(axis=1) > 2
        return np.where(bad, np.nan, eb)

    E_id = e2["expected"]                       # frozen 2.2 identity plug-in

    # ---- GE-LIN-CF (frozen 2.5, D4) -------------------------------------
    a222_line = wf[i222] + CONCS[None, :] * wrem[i222]
    use_line = (wpost > 0.5) & np.isfinite(wf)
    sm = np.where(use_line[:, None],
                  wf[:, None] + CONCS[None, :] * wrem[:, None],
                  w_mean[:, None])
    base_lin = sm * a222_line
    E_lincf = np.empty_like(M)
    for k in range(N_FOLDS):
        tr = keep & (fold != k)
        te = fold == k
        cb_k = interpolate_correction(wf[tr], e1["e_b"][tr])
        cr_k = interpolate_correction(wf[tr], e1["e_r"][tr])
        E_lincf[te] = (base_lin[te]
                       + cb_k(wf[te])[:, None]
                       + cr_k(wf[te])[:, None] * CONCS[None, :])

    # ---- GE-ISO / GE-SIG (frozen 2.3 / 2.4, D6 / D7) --------------------
    E_iso = np.full_like(M, np.nan)
    E_sig = np.full_like(M, np.nan)
    iso_models = {}
    sig_models = {}
    wgrid = np.linspace(float(np.nanmin(wf)), float(np.nanmax(wf)), 201)
    tb = time.time()
    for c in range(4):
        msk = (np.isfinite(M[:, c]) & np.isfinite(Mse[:, c])
               & (Mse[:, c] > 0) & np.isfinite(wf))
        for k in range(N_FOLDS):
            tr = msk & (fold != k)
            te = msk & (fold == k)
            # GE-ISO
            iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
            iso.fit(wf[tr], M[tr, c],
                    sample_weight=1.0 / Mse[tr, c] ** 2)
            E_iso[te, c] = iso.predict(wf[te])
            iso_models[(c, k)] = iso
            # GE-SIG with the pre-registered retry chain (D7)
            x, y = wf[tr], M[tr, c]
            sd = float(x.std()) if float(x.std()) > 0 else 1.0
            span = float(y.max() - y.min()) if float(y.max() - y.min()) > 0 \
                else 1.0
            base_p0 = [float(y.min()), span, float(np.median(x)), 1.0 / sd]
            popt = None
            for attempt, kscale in enumerate([1.0, 0.2, 5.0]):
                p0 = list(base_p0)
                p0[3] = kscale / sd
                try:
                    popt, _ = curve_fit(
                        logi4, x, y, p0=p0, sigma=Mse[tr, c],
                        absolute_sigma=False,
                        bounds=([-np.inf, 0.0, -np.inf, 0.0],
                                [np.inf, np.inf, np.inf, np.inf]))
                except RuntimeError:
                    popt = None
                if popt is not None:
                    if attempt:
                        sig_retries.append((int(CONCS[c]), k, attempt,
                                            p0[3]))
                    break
            if popt is None:
                gate("G-M2 GE-SIG fit convergence",
                     False,
                     f"c={int(CONCS[c])} fold={k}: curve_fit failed all "
                     "three pre-registered starts (D7) -- no threshold "
                     "loosened, no N raised")
            sig_models[(c, k)] = popt
            E_sig[te, c] = logi4(wf[te], *popt)
    print(f"  [GE-ISO/GE-SIG fits: 4 conditions x 5 folds x 2] "
          f"{time.time() - tb:.1f}s; GE-SIG retries used: "
          f"{sig_retries if sig_retries else 'none'}")

    # ---- aggregate all four through the one shared path ------------------
    eb = {"identity": aggregate(E_id),
          "GE-LIN-CF": aggregate(E_lincf),
          "GE-ISO": aggregate(E_iso),
          "GE-SIG": aggregate(E_sig)}

    # =====================================================================
    banner("G-M1 -- IDENTITY (frozen 2.2, HARD)", "-")
    a_id, a_ref = eb["identity"], e2["e_b"]
    nan_disagree = int((np.isnan(a_id) ^ np.isnan(a_ref)).sum())
    both = ~np.isnan(a_id) & ~np.isnan(a_ref)
    d_id = float(np.max(np.abs(a_id[both] - a_ref[both]))) if both.any() \
        else float("inf")
    gate("G-M1(b) aggregate(e2.expected) == e2 e_b",
         nan_disagree == 0 and d_id < TOL_12,
         f"NaN-pattern disagreements = {nan_disagree}, max|diff| over "
         f"{int(both.sum())} finite rows = {d_id:.3e} (gate < 1e-12)")

    rec = pd.Series(t32["own_e_b"].to_numpy(float),
                    index=t32["hgvs_pro"]).reindex(raw["hgvs"]).to_numpy()
    m_rec = np.isfinite(rec)
    d_rec = float(np.nanmax(np.abs(a_id[m_rec] - rec[m_rec]))) \
        if m_rec.any() else float("inf")
    n_above = int((np.abs(a_id[m_rec] - rec[m_rec]) > TOL_12).sum())
    n_recorded_not_rebuildable = int((m_rec & ~np.isfinite(a_id)).sum())
    n_rebuildable_not_recorded = int((~m_rec & np.isfinite(a_id)).sum())
    gate("G-M1(c) aggregate(identity) == RECORDED own_e_b (frozen "
         "comparison set = recorded rows)",
         d_rec < TOL_12 and n_above == 0
         and n_recorded_not_rebuildable == 0,
         f"compared {int(m_rec.sum())} recorded rows (frozen: 10,757), "
         f"max|diff| = {d_rec:.3e}, rows > 1e-12 = {n_above}, recorded "
         f"but not rebuildable = {n_recorded_not_rebuildable} (gates: "
         f"<1e-12 / 0 / 0)")
    print(f"  [informational, per the G-M1(c) disclosure] rows with a "
          f"rebuild value but NO recorded own_e_b = "
          f"{n_rebuildable_not_recorded} (the raw file's "
          f"{int((raw['type'] != 'substitution').sum())} "
          f"nonsense/synonymous rows plus substitutions the atlas never "
          f"assigned own_e_b to -- nothing to compare against)")
    print("  DISCLOSURE (AGENTS 6): the first smoke run of this script "
          "failed G-M1(c) on an over-strict clause of my own (zero "
          "finite/NaN disagreements over ALL raw rows) that went beyond "
          "the frozen rule's comparison set (the recorded rows).  The "
          "clause was corrected to the frozen rule before any GE "
          "quantity was computed; the 1e-12 threshold and the "
          "comparison set are unchanged from the frozen block.  The "
          "failure output is preserved in the build log.")

    for name in VARIANTS:
        E = {"GE-ISO": E_iso, "GE-SIG": E_sig, "GE-LIN-CF": E_lincf}[name]
        n_bad = int((valid & ~np.isfinite(E)).sum())
        gate(f"G-M1(d) {name} expectation finite on every valid cell",
             n_bad == 0, f"{n_bad} of {int(valid.sum())} valid cells "
             "have non-finite E (must be 0)")

    # =====================================================================
    banner("G-M5 -- FOLD INTEGRITY (HARD)", "-")
    fold_tbl = pd.DataFrame({"position": raw_pos, "fold": fold})
    max_nf = int(fold_tbl.groupby("position")["fold"].nunique().max())
    gate("G-M5 every position in exactly one fold", max_nf == 1,
         f"max distinct folds per position = {max_nf} (must be 1)")
    n_unassigned = int(((fold < 0) | (fold >= N_FOLDS)).sum())
    disjoint_ok = True
    worst = None
    for k in range(N_FOLDS):
        p_tr = set(pos_sorted[fold_of_pos != k].tolist())
        p_te = set(pos_sorted[fold_of_pos == k].tolist())
        inter = p_tr & p_te
        if inter:
            disjoint_ok = False
            worst = (k, len(inter))
    gate("G-M5 every variant predicted by a fit that excluded its "
         "position", disjoint_ok and n_unassigned == 0,
         f"train/test position overlap per fold: "
         f"{'none for all 5 folds' if disjoint_ok else worst}; "
         f"unassigned rows = {n_unassigned}; every row is in exactly one "
         f"test fold by construction (fold is a function of position)")

    # =====================================================================
    banner("G-M2 -- MONOTONICITY OF EACH FITTED EXPECTATION (HARD)", "-")
    worst_iso = float("inf")
    worst_sig = float("inf")
    for (c, k), iso in iso_models.items():
        v = iso.predict(wgrid)
        worst_iso = min(worst_iso, float(np.diff(v).min()))
    for (c, k), popt in sig_models.items():
        v = logi4(wgrid, *popt)
        worst_sig = min(worst_sig, float(np.diff(v).min()))
    gate("G-M2 GE-ISO non-decreasing on the 201-point w-grid",
         worst_iso >= -TOL_12,
         f"min step over 20 fitted functions = {worst_iso:.3e} "
         "(gate >= -1e-12)")
    gate("G-M2 GE-SIG non-decreasing on the 201-point w-grid",
         worst_sig >= -TOL_12,
         f"min step over 20 fitted functions = {worst_sig:.3e} "
         "(gate >= -1e-12)")

    # =====================================================================
    banner("SCRIPT 125 ROW CONSTRUCTION (G-ALIGN, AGENTS 5) -- cached "
           "Phase 2 frames via phase2_diag (imported)", "-")
    tb = time.time()
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    bgs = list(A.bgs)
    N_ids = list(A.N_IDS)
    S_ids = list(A.S_IDS)
    print(f"  [pdg.build] {time.time() - tb:.1f}s -- script 125's cached "
          "construction, imported not reimplemented")
    frame = A.frame
    gate("structure: 96 backgrounds, |N| = 78, arms G40/V38/S18",
         len(bgs) == T_NBGS and len(N_ids) == T_NN
         and table.arm.value_counts().to_dict()
         == {"G": 40, "V": 38, "S": 18},
         f"got {len(bgs)} bgs, |N| = {len(N_ids)}, arms "
         f"{table.arm.value_counts().to_dict()}")
    gate("structure: anchor 10,757 rows / 654 positions, H = 455 "
         "positions / 7,526 rows",
         len(frame) == T_ROWS and frame.position.nunique() == T_POS
         and len(A.Hset) == T_HPOS
         and int(frame.position.isin(A.Hset).sum()) == T_HROWS,
         f"got ({len(frame)}, {frame.position.nunique()}), H = "
         f"{len(A.Hset)} positions / "
         f"{int(frame.position.isin(A.Hset).sum())} rows")

    # A222V rows are frame-order (verified before use, D9)
    av = A.a222v_rows
    same_order = (len(av) == len(frame)
                  and np.array_equal(av["position"].to_numpy(),
                                     frame["position"].to_numpy())
                  and np.array_equal(av["delta"].to_numpy(),
                                     frame["delta_esm"].to_numpy())
                  and np.array_equal(av["own_e_b"].to_numpy(),
                                     frame["own_e_b"].to_numpy()))
    gate("G-ALIGN A222V rows are frame-order (position/delta/own_e_b "
         "exact)", same_order,
         f"exact match = {same_order} over {len(frame)} rows")

    # per-background alignment (D9): re-run 125's join, gate rowwise
    ge_by_hgvs = {name: pd.Series(eb[name], index=raw["hgvs"])
                  for name in ["identity"] + VARIANTS}
    frame_ge = {name: s.reindex(frame["hgvs_pro"].to_numpy()).to_numpy()
                for name, s in ge_by_hgvs.items()}
    for name in ["identity"] + VARIANTS:
        n_nan = int(np.isnan(frame_ge[name]).sum())
        gate(f"G-ALIGN {name} maps onto all frame rows finite",
             n_nan == 0, f"{n_nan} of {len(frame)} frame rows NaN "
             "(must be 0: the identity NaN pattern equals recorded "
             "own_e_b's, G-M1(c))")

    worst_len = worst_pos = 0
    worst_own = 0.0
    worst_delta = 0.0
    worst_rho = 0.0
    worst_rhoH = 0.0
    rho_ge = {v: {"full": {}, "H": {}} for v in VARIANTS}
    for b in bgs:
        f = pd.read_csv(ROOT / "data/processed/phase2" / f"bg_{b}.csv")
        m = frame.merge(f[["position", "mut_aa", "score"]],
                        on=["position", "mut_aa"], how="left")
        if len(m) != len(frame):
            gate("G-ALIGN bg score join does not duplicate frame rows",
                 False, f"{b}: join length {len(m)} != {len(frame)}")
        pos_idx = np.flatnonzero(m["score"].notna().to_numpy())
        r = A.bg_rows[b]
        worst_len = max(worst_len, abs(len(r) - len(pos_idx)))
        if len(r) == len(pos_idx):
            worst_pos = max(worst_pos,
                            int(np.sum(r["position"].to_numpy()
                                       != frame["position"].to_numpy()[pos_idx])))
            worst_own = max(worst_own, float(np.max(np.abs(
                r["own_e_b"].to_numpy()
                - frame["own_e_b"].to_numpy()[pos_idx]))))
            d_re = (m["score"].to_numpy()[pos_idx]
                    - frame["esm2_score"].to_numpy()[pos_idx])
            worst_delta = max(worst_delta, float(np.max(np.abs(
                r["delta"].to_numpy() - d_re))))
            # original rho_b from the ALIGNED rows must match 125's own
            rho_f = p3c.spearman(r["delta"].to_numpy(),
                                 frame["own_e_b"].to_numpy()[pos_idx])
            worst_rho = max(worst_rho,
                            abs(rho_f - float(A.point[b])),
                            abs(rho_f - float(table.loc[b, "rho_full"])))
            hm = r["position"].to_numpy()
            hmask = np.isin(hm, list(A.Hset))
            if hmask.any():
                rho_h = p3c.spearman(r["delta"].to_numpy()[hmask],
                                     frame["own_e_b"].to_numpy()[pos_idx][hmask])
                worst_rhoH = max(worst_rhoH,
                                 abs(rho_h - float(table.loc[b, "rho_H"])))
            for v in VARIANTS:
                ge_v = frame_ge[v][pos_idx]
                rho_ge[v]["full"][b] = p3c.spearman(
                    r["delta"].to_numpy(), ge_v)
                rho_ge[v]["H"][b] = p3c.spearman(
                    r["delta"].to_numpy()[hmask], ge_v[hmask])
        else:
            gate("G-ALIGN background row count matches 125's join", False,
                 f"{b}: bg_rows {len(r)} != joined {len(pos_idx)}")
    gate("G-ALIGN 96 backgrounds reproduce 125's rows and original "
         "rho_b exactly",
         worst_len == 0 and worst_pos == 0 and worst_own < TOL_EXACT
         and worst_delta < TOL_12 and worst_rho < TOL_12
         and worst_rhoH < TOL_12,
         f"worst row-count diff = {worst_len}, position mismatches = "
         f"{worst_pos}, max|own_e_b diff| = {worst_own:.3e}, "
         f"max|delta diff| = {worst_delta:.3e}, max|original rho_b diff| "
         f"= {worst_rho:.3e} (full), {worst_rhoH:.3e} (H) (gates: "
         f"0/0/0/<1e-12/<1e-12/<1e-12)")

    # =====================================================================
    banner("G-M4 -- PHASE 2 REPRODUCTION ROWS (HARD, frozen section 5)", "-")
    x_av = frame["delta_esm"].to_numpy(float)
    y_own = frame["own_e_b"].to_numpy(float)
    pos_av = frame["position"].to_numpy()
    rho_full_direct = p3c.spearman(x_av, y_own)
    rho_full_125 = p3c.spearman(av["delta"].to_numpy(float),
                                av["own_e_b"].to_numpy(float))
    note("G-M4 A222V rho full (task32 columns directly)",
         rho_full_direct, T_RHO_FULL, TOL_9DP)
    note("G-M4 A222V rho full (script 125's frame rows)",
         rho_full_125, T_RHO_FULL, TOL_9DP)
    gate("G-M4 the two sources agree with each other",
         abs(rho_full_direct - rho_full_125) < TOL_12,
         f"|diff| = {abs(rho_full_direct - rho_full_125):.3e} "
         "(AGENTS 5 column identity)")
    hmask_av = np.isin(pos_av, list(A.Hset))
    rho_h_direct = p3c.spearman(x_av[hmask_av], y_own[hmask_av])
    note("G-M4 A222V rho H", rho_h_direct, T_RHO_H, TOL_9DP)
    note("G-M4 A222V rho H (pdg cross-check)", float(rho_a_H), T_RHO_H,
         TOL_9DP)

    nulls_full = table.loc[N_ids, "rho_full"].to_numpy(float)
    nulls_H = table.loc[N_ids, "rho_H"].to_numpy(float)
    p_f, k_f, n_f = p3c.p_spec(rho_full_direct, nulls_full, mode="neg")
    p_h, k_h, n_h = p3c.p_spec(rho_h_direct, nulls_H, mode="neg")
    beat_f = sorted(np.array(N_ids)[nulls_full <= rho_full_direct].tolist())
    beat_h = sorted(np.array(N_ids)[nulls_H <= rho_h_direct].tolist())
    gate("G-M4 frozen p_spec full = 2/79 with the named null",
         p_f == T_P_FULL and k_f == 1 and beat_f == T_BEATERS_FULL
         and n_f == T_NN,
         f"got (1+{k_f})/(1+{n_f}) = {k_f+1}/{n_f+1} = {p_f!r} target "
         f"2/79 = {T_P_FULL!r}; beaters {beat_f} target "
         f"{T_BEATERS_FULL}")
    gate("G-M4 frozen p_spec H = 4/79 with the named nulls",
         p_h == T_P_H and k_h == 3 and beat_h == T_BEATERS_H
         and n_h == T_NN,
         f"got (1+{k_h})/(1+{n_h}) = {k_h+1}/{n_h+1} = {p_h!r} target "
         f"4/79 = {T_P_H!r}; beaters {beat_h} target {T_BEATERS_H}")

    # =====================================================================
    banner("G-M3 -- BOOTSTRAP GATES (HARD)", "-")
    cl = pos_av
    x_cl = x_av
    for name, y_v in [("original own_e.b", y_own),
                      ("GE-LIN-CF", frame_ge["GE-LIN-CF"]),
                      ("GE-ISO", frame_ge["GE-ISO"]),
                      ("GE-SIG", frame_ge["GE-SIG"])]:
        point = p3c.spearman(x_cl, y_v)
        nk = np.unique(cl).size
        ids_one = np.arange(nk, dtype=np.int64)[None, :]
        v_c = float(p3c.pos_cluster_boot_from_ids(x_cl, y_v, cl,
                                                  ids_one)[0])
        v_r = float(p3c.reference_boot(x_cl, y_v, cl, ids_one)[0])
        d = max(abs(v_c - point), abs(v_r - point))
        gate(f"G-M3(i) identity (every cluster once), {name}", d < TOL_12,
             f"corrected {v_c!r}, reference {v_r!r}, point {point!r}; "
             f"max|diff| = {d:.3e} (gate < 1e-12)")

    tb = time.time()
    ids, _ = p3c.draw_ids(cl, n_draw=N_REF, seed=SEED)
    d_c = p3c.pos_cluster_boot_from_ids(x_cl, frame_ge["GE-ISO"], cl, ids)
    d_r = p3c.reference_boot(x_cl, frame_ge["GE-ISO"], cl, ids)
    md = float(np.max(np.abs(d_c - d_r)))
    gate("G-M3(ii) draw-by-draw corrected == slow reference, GE-ISO "
         "anchor", md < TOL_12,
         f"{N_REF} draws, max|corrected - reference| = {md:.3e} "
         f"(gate < 1e-12) in {time.time() - tb:.1f}s")

    ci_orig = None
    if N_BOOT == 10000:
        tb = time.time()
        base_df = frame[["position", "delta_esm", "own_e_b"]].copy()
        r1 = position_cluster_bootstrap(base_df, "position", "delta_esm",
                                        "own_e_b", N_BOOT, SEED)
        draws_gen = p3c.pos_cluster_boot(x_cl, y_own, cl, N_BOOT, SEED)
        lo_g, hi_g, _ = p3c.pct_ci(draws_gen)
        ci_orig = (float(r1["ci_lo"]), float(r1["ci_hi"]))
        print(f"  [Phase 1's own routine] CI = [{r1['ci_lo']!r}, "
              f"{r1['ci_hi']!r}], p_boot = {r1['p_boot']!r}, "
              f"observed = {r1['observed_rho']!r} in {time.time() - tb:.1f}s")
        note("G-M3(iii) Phase 1 CI lo reproduces", r1["ci_lo"], T_CI_LO,
             TOL_9DP)
        note("G-M3(iii) Phase 1 CI hi reproduces", r1["ci_hi"], T_CI_HI,
             TOL_9DP)
        d_lo, d_hi = abs(lo_g - float(r1["ci_lo"])), abs(hi_g - float(
            r1["ci_hi"]))
        gate("G-M3(iii) corrected routine == Phase 1 routine",
             d_lo < TOL_12 and d_hi < TOL_12,
             f"max|diff| lo = {d_lo:.3e}, hi = {d_hi:.3e} "
             "(gate < 1e-12)")
    else:
        gate("G-M3(iii) Phase 1 CI reproduction", False,
             f"SKIPPED (smoke): N_BOOT={N_BOOT} != 10000 -- G-M3 cannot "
             "be called PASS on this run; decided on the N_BOOT=10000 "
             "run", hard=False)

    # =====================================================================
    banner("QUANTITIES (a)-(f) -- GE-ISO (primary), GE-SIG, GE-LIN-CF "
           "side by side", "-")
    results = {}

    # (a) Spearman(own_e.b^GE, own_e.b) over the 10,757 rows
    print("\n  (a) Spearman(own_e.b^GE, own_e.b) over the 10,757 rows:")
    for v in VARIANTS:
        r_a = p3c.spearman(frame_ge[v], y_own)
        results.setdefault(v, {})["a"] = r_a
        print(f"      {v:10s} = {r_a:+.6f}")

    # (b) rho^GE with position-cluster CI + shrinkage
    print(f"\n  (b) rho^GE = Spearman(delta_ESM, own_e.b^GE), "
          f"position-cluster bootstrap N_BOOT={N_BOOT} seed={SEED}; "
          f"reference -0.088118 (frozen) / {rho_full_direct!r} "
          f"(recomputed):")
    print(f"      {'variant':10s} {'rho^GE':>12s} {'CI lo':>12s} "
          f"{'CI hi':>12s} {'p_boot':>8s} {'shrinkage':>10s}")
    print(f"      {'original':10s} {rho_full_direct:+12.6f} "
          f"{(f'{ci_orig[0]:+.6f}' if ci_orig else 'SKIPPED'):>12s} "
          f"{(f'{ci_orig[1]:+.6f}' if ci_orig else 'SKIPPED'):>12s} "
          f"{'':>8s} {'0.000000':>10s}")
    for v in VARIANTS:
        tb = time.time()
        rho_ge_v = p3c.spearman(x_cl, frame_ge[v])
        draws = p3c.pos_cluster_boot(x_cl, frame_ge[v], cl, N_BOOT, SEED)
        lo, hi, n_fin = p3c.pct_ci(draws)
        pb = p_boot_phase1(draws)
        shrink = 1.0 - rho_ge_v / rho_full_direct
        results[v].update(rho=rho_ge_v, lo=lo, hi=hi, p_boot=pb,
                          shrink=shrink)
        print(f"      {v:10s} {rho_ge_v:+12.6f} {lo:+12.6f} {hi:+12.6f} "
              f"{pb:8.4f} {shrink:+10.6f}   "
              f"({n_fin} finite draws, {time.time() - tb:.1f}s)")
        print(f"               doc target {T_ANCHOR_DOC} / recomputed "
              f"original {rho_full_direct!r}; p_boot is Phase 1's formula "
              f"(stats.py 27-31)")

    # (c) p_spec^GE full and H, nulls named
    print("\n  (c) p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / "
          "(1 + 78), N = Arm V u Arm G (78):")
    for v in VARIANTS:
        for view, nulls, thr in (("full", nulls_full, results[v]["rho"]),
                                 ("H", nulls_H,
                                  p3c.spearman(x_cl[hmask_av],
                                               frame_ge[v][hmask_av]))):
            p_v, k_v, n_v = p3c.p_spec(thr, nulls, mode="neg")
            beat = sorted(np.array(N_ids)[nulls <= thr].tolist())
            results[v].setdefault("c", {})[view] = (p_v, k_v, beat)
            print(f"      {v:10s} {view:4s}: rho^GE = {thr:+.6f}, "
                  f"p = (1+{k_v})/(1+{n_v}) = {k_v+1}/{n_v+1} = "
                  f"{p_v:.6f}; at-or-below nulls = {beat}")
        results[v]["c"]["H_thr"] = p3c.spearman(x_cl[hmask_av],
                                                frame_ge[v][hmask_av])
    print(f"      {'original':10s} full: p = 2/79 = {T_P_FULL:.6f} "
          f"beaters {T_BEATERS_FULL}; H: p = 4/79 = {T_P_H:.6f} "
          f"beaters {T_BEATERS_H}   (frozen, reproduced in G-M4)")

    # (d) shift-adjusted p_spec_adj (D9)
    print("\n  (d) p_spec_adj^GE: leave-one-out OLS of rho_b on "
          "mean|delta_b| (Diagnostics II D9):")
    mad = {"full": {}, "H": {}}
    mad_a = {}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(
                rr.delta.to_numpy(float))))
    for view in ("full", "H"):
        ra = av if view == "full" else av[av.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))
    for v in VARIANTS + ["original"]:
        for view in ("full", "H"):
            if v == "original":
                y_vec = np.array([float(table.loc[b, "rho_" + view])
                                  for b in N_ids])
                thr = (rho_full_direct if view == "full"
                       else rho_h_direct)
            else:
                y_vec = np.array([rho_ge[v][view][b] for b in N_ids])
                thr = (results[v]["rho"] if view == "full"
                       else results[v]["c"]["H_thr"])
            r_b = p3c.loo_ols_residuals(
                y_vec, np.array([mad[view][b] for b in N_ids]))
            _, _, predA = p3c.ols_fit_predict(
                y_vec, np.array([mad[view][b] for b in N_ids]),
                [mad_a[view]])
            r_A = thr - float(predA[0])
            k = int(np.sum(r_b <= r_A))
            beat = sorted(np.array(N_ids)[r_b <= r_A].tolist())
            p_adj = (1 + k) / (1 + len(N_ids))
            if v != "original":
                results[v].setdefault("d", {})[view] = (p_adj, k, beat,
                                                        r_A)
            print(f"      {v:10s} {view:4s}: r_A = {r_A:+.6f}, "
                  f"k = {k}/{len(N_ids)}, p_adj = (1+{k})/(1+78) = "
                  f"{p_adj:.6f}, beaters = {beat}")

    # (e) A222V's rank within Arm S u {A222V}, n = 19
    print("\n  (e) A222V rank fraction within Arm S u {A222V} "
          "(D10: (1 + #{b in S : rho_b <= rho_A}) / 19; a rank, not a "
          "test):")
    s_orig = np.array([float(table.loc[b, "rho_full"]) for b in S_ids])
    k_s_orig = int(np.sum(s_orig <= rho_full_direct))
    print(f"      {'original':10s}: rank = (1+{k_s_orig})/19 = "
          f"{(1 + k_s_orig) / 19:.6f}")
    for v in VARIANTS:
        s_nulls = np.array([rho_ge[v]["full"][b] for b in S_ids])
        k_s = int(np.sum(s_nulls <= results[v]["rho"]))
        frac = (1 + k_s) / 19.0
        results[v]["e"] = frac
        print(f"      {v:10s}: rank = (1+{k_s})/19 = {frac:.6f} "
              f"(n = 18 arm-S backgrounds + A222V)")

    # (f) Spearman(rho_b, d3_b) on the 67 resolved nulls
    d3 = pd.read_csv(D3_PATH).set_index("bg_id")
    resN = [b for b in N_ids if bool(d3.loc[b, "resolved"])]
    gate("structure: 67 resolved nulls", len(resN) == T_RESN,
         f"got {len(resN)} target {T_RESN}")
    g_d3 = np.array([float(d3.loc[b, "d3_CA"]) for b in resN])
    x_orig_g = np.array([float(table.loc[b, "rho_full"]) for b in resN])
    grad_orig = p3c.spearman(x_orig_g, g_d3)
    note("reference: original Spearman(rho_b, d3_b) vs the doc's +0.7316",
         grad_orig, T_GRAD_DOC, 5e-5, "{:+.6f}")
    print(f"      recomputed original = {grad_orig:+.9f}; script 140's "
          f"recorded value = {T_GRAD_140:+.9f} (9 dp)")
    d_orig, n_nan_orig = p3c.background_boot(x_orig_g, g_d3,
                                             n_boot=N_BOOT, seed=SEED)
    lo_o, hi_o, _ = p3c.pct_ci(d_orig)
    print(f"      original with background-level bootstrap CI = "
          f"[{lo_o:+.6f}, {hi_o:+.6f}] (N_BOOT={N_BOOT}, seed={SEED})")
    print("\n  (f) Spearman(rho_b^GE, d3_b) across the 67 resolved nulls, "
          "background-level bootstrap CI:")
    for v in VARIANTS:
        x_v = np.array([rho_ge[v]["full"][b] for b in resN])
        gr = p3c.spearman(x_v, g_d3)
        draws_f, n_nan = p3c.background_boot(x_v, g_d3, n_boot=N_BOOT,
                                             seed=SEED)
        lo_f, hi_f, nfin = p3c.pct_ci(draws_f)
        results[v]["f"] = (gr, lo_f, hi_f)
        print(f"      {v:10s} = {gr:+.6f}  CI [{lo_f:+.6f}, "
              f"{hi_f:+.6f}] ({nfin} usable, {n_nan} nan); next to "
              f"+0.7316 (frozen reference)")

    # =====================================================================
    banner("FROZEN OUTCOME WORDS (section 4, applied literally; primary "
           "GE-ISO governs)", "-")
    words = {}
    for v in VARIANTS:
        w_out = outcome_word(results[v]["rho"], results[v]["lo"],
                             results[v]["hi"],
                             results[v]["c"]["full"][0],
                             results[v]["c"]["H"][0])
        words[v] = w_out
        print(f"      {v:10s}: rho^GE = {results[v]['rho']:+.6f}, "
              f"CI [{results[v]['lo']:+.6f}, {results[v]['hi']:+.6f}], "
              f"p_spec^GE(full) = {results[v]['c']['full'][0]:.6f} "
              f"({results[v]['c']['full'][1] + 1}/79), p_spec^GE(H) = "
              f"{results[v]['c']['H'][0]:.6f} "
              f"({results[v]['c']['H'][1] + 1}/79)  ->  {w_out}")
    print("\n  Frozen rule (verbatim): GE-SURVIVES = the CI of rho^GE "
          "(GE-ISO) excludes zero in the negative direction AND "
          "p_spec^GE(full) <= 0.05 AND p_spec^GE(H) <= 0.10; "
          "GE-WEAKENS = the CI excludes zero in the negative direction "
          "but at least one p_spec^GE condition fails; "
          "GE-DOES-NOT-SURVIVE = the CI includes zero or the sign "
          "reverses.")
    if len(set(words.values())) == 1:
        print(f"  The three agree: all report {words['GE-ISO']}.  The "
              "primary governs; the sensitivities are reported with the "
              "same words (frozen section 4).")
    else:
        print("  DISAGREEMENT (stated plainly, frozen section 4): "
              f"GE-ISO = {words['GE-ISO']}, GE-SIG = {words['GE-SIG']}, "
              f"GE-LIN-CF = {words['GE-LIN-CF']}.  The primary "
              "(GE-ISO) governs; the two sensitivities are reported "
              "with their own words and no result is reinterpreted "
              "beyond them.")

    # =====================================================================
    banner("FITTED MONOTONE FUNCTIONS (printed so the shape is visible)", "-")
    print("  GE-SIG parameters (a + b/(1+exp(-k(w-m)))), 4 conditions x "
          "5 folds; b, k >= 0 by construction (D7):")
    for c in range(4):
        for k in range(N_FOLDS):
            a_, b_, k_, m_ = sig_models[(c, k)]
            print(f"      c={int(CONCS[c]):3d} fold={k}: a={a_:+.6f} "
                  f"b={b_:+.6f} k={k_:.6f} m={m_:+.6f}")
    print("  GE-ISO breakpoints: number of blocks and up to 40 evenly "
          "spaced (w, level) transitions per fit (full lists in "
          "m1_fitted_expectations.csv):")
    for c in range(4):
        for k in range(N_FOLDS):
            iso = iso_models[(c, k)]
            xs, ys = iso.X_thresholds_, iso.y_thresholds_
            n_b = len(ys)
            idx = np.unique(np.linspace(0, n_b - 1,
                                        min(n_b, 40)).astype(int))
            pairs = ", ".join(f"({xs[i]:.4f},{ys[i]:+.4f})"
                              for i in idx)
            print(f"      c={int(CONCS[c]):3d} fold={k}: blocks={n_b} "
                  f"transitions [{pairs}]")
    print("  GE-LIN-CF effective slopes (OLS of E on w over each fold's "
          "rows; not gated -- E is not a function of w alone):")
    for c in range(4):
        for k in range(N_FOLDS):
            te = fold == k
            m_fin = te & np.isfinite(E_lincf[:, c]) & np.isfinite(wf)
            sl, _, _ = p3c.ols_fit_predict(E_lincf[m_fin, c], wf[m_fin],
                                           [float(np.nanmedian(wf))])
            print(f"      c={int(CONCS[c]):3d} fold={k}: dE/dw "
                  f"= {sl:+.6f} (n = {int(m_fin.sum())})")

    # =====================================================================
    banner("SAVED OUTPUTS + ANALYSIS-SET ACCOUNTING (AGENTS 5)", "-")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out_rows = pd.DataFrame({
        "hgvs": raw["hgvs"].to_numpy(),
        "position": raw_pos,
        "fold": fold,
        "own_e_b_recorded": rec,
        "own_e_b_identity": eb["identity"],
        "own_e_b_ge_lin_cf": eb["GE-LIN-CF"],
        "own_e_b_ge_iso": eb["GE-ISO"],
        "own_e_b_ge_sig": eb["GE-SIG"],
    })
    p1 = OUTDIR / "m1_own_e_b_ge.csv"
    out_rows.to_csv(p1, index=False)
    print(f"  wrote {p1} ({len(out_rows)} raw rows) -- per-row own_e.b "
          "for all constructions, for session 3b re-verification")

    rho_recs = []
    for b in bgs:
        for view in ("full", "H"):
            rho_recs.append({"bg_id": b, "arm": table.loc[b, "arm"],
                             "own_pos": int(table.loc[b, "position"]),
                             "view": view, "variant": "OWN",
                             "rho": float(table.loc[b, "rho_" + view])})
            for v in VARIANTS:
                rho_recs.append({"bg_id": b, "arm": table.loc[b, "arm"],
                                 "own_pos": int(table.loc[b, "position"]),
                                 "view": view, "variant": v,
                                 "rho": rho_ge[v][view][b]})
    for view, val in (("full", rho_full_direct), ("H", rho_h_direct)):
        rho_recs.append({"bg_id": "A222V", "arm": "A222V", "own_pos": 222,
                         "view": view, "variant": "OWN", "rho": val})
        for v in VARIANTS:
            rho_recs.append({"bg_id": "A222V", "arm": "A222V",
                             "own_pos": 222, "view": view, "variant": v,
                             "rho": (results[v]["rho"] if view == "full"
                                     else results[v]["c"]["H_thr"])})
    p2 = OUTDIR / "m1_rho_b_ge.csv"
    pd.DataFrame(rho_recs).to_csv(p2, index=False)
    print(f"  wrote {p2} ({len(rho_recs)} rows = 97 backgrounds x 2 "
          "views x 4 constructions)")

    fit_recs = []
    for (c, k), iso in iso_models.items():
        for x_, y_ in zip(iso.X_thresholds_, iso.y_thresholds_):
            fit_recs.append({"kind": "iso_transition", "variant": "GE-ISO",
                             "condition": int(CONCS[c]), "fold": k,
                             "w": float(x_), "value": float(y_)})
    for (c, k), popt in sig_models.items():
        for x_ in wgrid:
            fit_recs.append({"kind": "sig_grid", "variant": "GE-SIG",
                             "condition": int(CONCS[c]), "fold": k,
                             "w": float(x_),
                             "value": float(logi4(x_, *popt))})
    p3 = OUTDIR / "m1_fitted_expectations.csv"
    pd.DataFrame(fit_recs).to_csv(p3, index=False)
    print(f"  wrote {p3} ({len(fit_recs)} rows: full isotonic "
          "breakpoints + 201-point logistic grids)")

    print("\n  Analysis-set accounting (every row accounted for):")
    print(f"    raw fit frame                     : {len(raw)} rows "
          f"({len(pos_sorted)} positions)")
    print(f"    rows with any valid cell          : {n_anyv}")
    print(f"    rows with all four cells valid    : {n_all4}")
    print(f"    task32 analysis table             : {len(t32)} rows "
          f"(recorded own_e_b finite: {int(np.isfinite(rec).sum())})")
    print(f"    anchor frame (delta_esm & own_e_b): {len(frame)} rows / "
          f"{frame.position.nunique()} positions")
    print(f"    H view                            : "
          f"{int(frame.position.isin(A.Hset).sum())} rows / "
          f"{len(A.Hset)} positions")
    print(f"    rho_b rows per background         : script 125's own "
          f"join, gated (G-ALIGN); own-position rows are absent from "
          f"the score files (125's G-C)")

    # =====================================================================
    banner("GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    n_skip = sum(1 for _, ok, d in gates if not ok and "SKIPPED" in d)
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    smoke = N_BOOT != 10000
    print(f"\n  {len(gates) - n_fail}/{len(gates)} checks PASS, "
          f"{n_fail} FAIL ({n_skip} of the FAILs are smoke SKIPS).")

    banner("LIMITATIONS (AGENTS 6; printed, not only written down)", "-")
    print("  1. Reproduction is not replication: G-M1/G-M3/G-M4 "
          "re-derive cached project numbers to validate this code; they "
          "are a unit test, not independent evidence for any claim.")
    print("  2. All four expectations share the A222V reference line and "
          "the per-variant WT-arm fits; a construction-level artifact "
          "common to those would appear in every variant.")
    print("  3. GE-ISO/GE-SIG score the same variants they are fit on, "
          "but never a tested variant's own position (fold = "
          "f(position), G-M5).")
    print("  4. One background (A222V arm); position-cluster bootstrap "
          "resamples 654 positions, never rows (effective n = 654).")
    print("  5. p_spec / p_spec_adj are one-sided signed rank counts "
          "over 78 nulls, not tail areas of an exchangeable "
          "distribution.")
    print("  6. (f) resamples BACKGROUNDS (values held fixed), a "
          "different unit from (b); the two CIs are not "
          "interchangeable.")
    print("  7. No frozen Phase 2 result changes here; this re-targets "
          "the anchor, and nothing here speaks to any GB1 or RBD "
          "result (frozen section 7).")
    print(f"\n  Elapsed {time.time() - t0:.1f}s")

    if n_fail:
        if smoke and n_fail == n_skip:
            print("\nSMOKE RESULT: all executed checks PASS; the only "
                  "FAIL is the intentional G-M3(iii) SKIP.  G-M3 is "
                  "decided on the N_BOOT=10000 run.")
            return 0
        print("\nGATE FAIL -- A3 stops here (exit 3).  Do not raise N, "
              "do not adjust a threshold.")
        return 3
    print("\nGATE PASS -- G-M0 through G-M5 and G-ALIGN all pass; the "
          "frozen outcome words above are the result of this block.")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except GateFail as e:
        print(f"\nGATE TABLE (up to the failure):")
        for gid, ok, detail in gates:
            print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
        print(f"\nGATE FAIL: {e} -- A3 stops here (exit 3).  Do not "
              "raise N, do not adjust a threshold.")
        print(f"Elapsed {time.time() - t0:.1f}s")
        rc = 3
    sys.exit(rc)
