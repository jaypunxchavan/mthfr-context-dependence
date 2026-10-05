"""Script 165 -- Task A2 gates for scripts/lib/phase4_common.py
(docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md Task A2).

PRE-REGISTRATION: this docstring was written BEFORE the first run of this
script and is not edited after any Phase 4 number exists (AGENTS 6).
WHAT THIS SCRIPT IS: the HARD gates of Task A2 for the new shared library.
It writes nothing except this script and, by the caller's redirect,
docs/tasks/phase4-strengthening/PHASE4_A2_FULL_OUTPUT.txt.  No existing
script or library is modified.  No torch / esm / thermompnn is imported
(rule 1).

RESAMPLING UNITS (PHASE4 rule 7): the anchor statistics here are computed
INSIDE one background (the A222V arm) -> POSITION CLUSTERS.  Script 165
performs no background-level resampling.  Every bootstrap routine it
exercises either is the imported corrected routine (reference-gated draw by
draw, plus Phase 1's CI) or is the new whole-placebo routine (identity,
draw-by-draw reference, and an independently computed observed statistic).

GATES (ALL HARD; a failed gate prints GATE FAIL and the script exits 3;
the driver never retries exit 3; thresholds are never loosened and N is
never raised to pass a gate).

A2-G1 (HARD) -- re-run scripts/159_phase3_common_gate.py UNCHANGED in a
    subprocess with N_BOOT=10000 SEED=0 and require the line
    "40/40 checks PASS, 0 FAIL".  The subprocess's own output is printed
    verbatim (its tail is enough to identify the run; the exit code must
    be 0).  This is PHASE4_STRENGTHENING.md Task A2's A2-G1 literally: the
    Phase 3 library gate must still print 40/40 after phase4_common exists.
    A smoke run of this script (N_BOOT != 10000) runs 159 with N_BOOT=300
    instead and CANNOT call A2-G1 PASS -- it prints that A2-G1 is decided
    only on the N_BOOT=10000 run, exactly as 159 itself does.

A2-G2 (HARD) -- the cached MTHFR numbers, reproduced THROUGH the new
    library (p4c.spearman / p4c.p_spec / p4c.partial_spearman), every
    target printed beside the value (rule 16: the doc's expected values are
    Claude's recomputations, not facts -- a mismatch means the DOC is
    wrong: report both, stop, do not force agreement):
      (a) data/processed/phase2_diagnostics/background_rho_table.csv
          sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
      (b) A222V rho full = -0.088118064   (< 1e-9), from task32's own rows
          AND from script 125's A.a222v_rows; the two sources must agree
          with EACH OTHER to 1e-12 (AGENTS 5 column identity)
      (c) A222V rho H    = -0.090021683   (< 1e-9), H = script 125's
          held-out set (455 positions)
      (d) p_spec(neg) full = 2/79, k = 1, beaters {G_P254F}   (exact)
      (e) p_spec(neg) H    = 4/79, k = 3,
          beaters {AV_195, AV_220, G_P254F}                    (exact)
      (f) rho(delta, S_W)     = -0.32376573717755663  (< 1e-12)
      (g) rho(own_e.b, S_W)   = +0.085391652432165    (< 1e-12)
      (h) the linear (rank) partial controlling S_W
          = -0.06414804421216103 (< 1e-12), and its retention
          |partial|/|raw| rounds to 0.728 (72.8%)
      (i) the two-covariate linear (rank) partial controlling S_W and the
          base functionality rounds to -0.0829 (4 dp, Phase 1 L2)
    Rows for (b)-(i): task32_analysis_table.csv rows with finite
    delta_esm, own_e_b, position, esm2_score and base_functionality
    (expected 10,757 rows / 654 positions, gated -- if the row count does
    not match the doc's 10,757/654 this gate fails rather than being
    silently compared on a different set).

A2-G3 (HARD) -- toy-data gates for EVERY new function of phase4_common,
    with hand-fixed expectations written below, not taken from a prior run:
    * equal_count_bins: the exact split of 10 values into 2 bins and of
      11 values into 4 bins (sizes 3/3/3/2); rejection of n_bins > n.
    * stratified_spearman: two strata each perfectly monotone -> 1.0;
      strata with rhos 1.0 and 0.0 at weights 4 and 4 -> 0.5 exactly
      (the 0.0 stratum is x = 1,2,3,4 with y = 3,1,4,2, whose rank
      correlation is 0 by construction); a constant-y stratum is DROPPED
      and the rest renormalised (decision I1).
    * between_within_decomposition: PLANTED PURE-BETWEEN (each position's
      y is the fixed within-position permutation 3,1,4,2 of its x, position
      means strictly ordered) -> rho_between = 1.0 and rho_within = 0.0
      exactly; PLANTED PURE-WITHIN (position means ordered 1,2,3,4 against
      3,1,4,2, within-position y = x + const) -> rho_within = 1.0 and
      rho_between = 0.0 exactly; a position with fewer than min_rows rows
      is excluded (n_qualifying drops by exactly that count).
    * partial_spearman == the closed-form partial: for 1 control
      (r_xy - r_xz r_yz)/sqrt((1-r_xz^2)(1-r_yz^2)) and for 2 controls the
      matrix-inversion formula, both built from scipy.stats.spearmanr on
      the same arrays (< 1e-12).
    * permute_within_groups: per-group multiset AND per-group mean
      preserved exactly; global multiset preserved; deterministic for a
      fixed seed; the global x/y association actually changes (the shuffle
      is not an identity).
    * the simulation harness: own_eb_from_arrays == the project's
      rebuild_interaction_fit called directly on the same raw frame
      (< 1e-12); simulate_rho with sw = 0, m_noise = 0 (m_se left
      RECORDED -- it is the se column the pipeline weights by, scripts
      106/17) and E = the observed m returns the UNPERTURBED rho exactly
      (the frozen G-M4 identity, on toy rows); rank_normal_z has mean 0 and
      sd 1 (< 1e-12), is 0 at the median of an odd-length monotone vector
      and is antisymmetric there;
      plant_term at r0 = +1 / -1 / 0 is s_e*z / -s_e*z / s_e*u exactly.
    * power_curve: a hand-built zero band (all draws 0.0, so both
      percentiles are 0.0) with four hand-counted bands -> power 0.90,
      0.10, 0.10, 0.90 and the r0 = 0 band 1.00; mean_rho equals each
      band's mean.
    * min_detectable_effect: powers [0.9, 0.1, 0.025, 0.1, 0.9] on
      r0 [-0.1, -0.05, 0, 0.05, 0.1] -> 0.05 + (0.8-0.1)/(0.9-0.1)*0.05
      = 0.09375 on each side, headline 0.09375; all-low powers ->
      "above the grid"; one side only -> headline = the numeric side.
    * attenuation_slope: r0 = [-1, 0, 1] against [-2, 0, 2] -> 2.0, 0.0.
    * whole_placebo_boot: IDENTITY -- ids covering every position exactly
      once return the independently computed observed k and p_spec(neg)
      (< 1e-12); DRAW-BY-DRAW -- max|new - slow reference| < 1e-12 over
      N_REF_PRE pre-drawn id rows; DETERMINISM -- the same seed reproduces.
      (This is the frozen G-M7 rule plus PHASE4 rule 6's reference gate.)
    * cell_labels / interval_labels / seq_separation: the boundary cases
      of the frozen cells (d3 = 12 in, 12.000001 out; dseq = 20 in, 21
      out of C1 but out of C2 until 40; d3 = 18 not > 18; the gap
      positions return ""), the frozen GB1 separation strata 1-5 / 6-15 /
      16-54 and the Angstrom strata <8 / 8-14 / >14, and |100-222| = 122.
    * auroc == sklearn.metrics.roc_auc_score (< 1e-12) on three toys:
      with ties, perfect, and inverted.
    * balanced_pr_curve == scikit-learn's OWN balanced precision computed
      through sklearn.metrics.precision_recall_curve with sample weights
      (N for positives, P for negatives), whose precision is
      N*TP/(N*TP + P*FP) = TPR/(TPR + FPR) exactly: recall and balanced
      precision must agree at every point but the anchor
      (< 1e-12), the anchor equals the top threshold's own value, and the
      area must equal sklearn.metrics.auc over the same re-anchored
      coordinates (< 1e-12).  A second independent path,
      sklearn.metrics.roc_curve(drop_intermediate=False), must give the
      identical tpr/(tpr+fpr) coordinates (< 1e-12).  (sklearn's own
      precision_recall_curve writes an artificial precision = 1.0 at
      recall 0, where no threshold predicts anything and TPR/(TPR+FPR) is
      0/0; decision I6 anchors recall 0 at the TOP THRESHOLD's value
      instead, and that single point is the only difference tested.)
    * every outcome-word function of all five frozen blocks: boundary
      cases for each word, including p = 0.05 and 0.10 exactly,
      |NB| = 30 vs 29, CI touching zero, and UTIL's precedence rule I7.
    * the re-exports are the imported objects, not copies
      (p4c.spearman is p3c.spearman, p4c.pos_cluster_boot_corrected is
      phase2_diag4.pos_cluster_boot_corrected).

BOOTSTRAP REFERENCE GATE (PHASE4 rule 6 -- a REFERENCE gate, not an
identity gate), exercised here in addition to A2-G3's whole-placebo
reference: on the real anchor rows, p4c.pos_cluster_boot_from_ids must
agree draw by draw with p4c.reference_boot (< 1e-12, N_REF draws), the
every-cluster-once identity must reproduce the point estimate (< 1e-12),
and at N_BOOT = 10000 p4c.pos_cluster_boot must reproduce Phase 1's CI
[-0.1173334458953319, -0.0595113844951173] (each endpoint < 1e-9).  At
N_BOOT != 10000 the CI sub-gate prints SKIPPED and A2-G2/G3 cannot be
called PASS on that run (the decision is taken on N_BOOT = 10000).

DECISION RULE (pre-registered): any A2-G1, A2-G2 or A2-G3 sub-gate FAIL ->
exit 3; phase4_common is NOT trusted for Modules M, U, G, N or L.  No
threshold is loosened, no N is raised, nothing is re-extracted.

SMOKE-PHASE FIXES (disclosed per AGENTS 6; all made BEFORE any Phase 4
number existed, on the N_BOOT=300 smoke run, and none of them moved a
threshold toward passing): (1) own_eb_from_arrays indexed
rebuild_interaction_fit's return as ["e_b"] -- the project's own
convention (scripts 17/33/47) is fit["e2"]["e_b"]; (2) the whole-placebo
fast and reference paths ranked arrays containing the per-background NaNs
(scipy rankdata propagates one NaN through the whole rank vector), so
every rho was NaN -- both now mask to each background's finite rows
(_rho_masked), which is what "rho_b over a background's rows" means when
that background's rows exclude its own position; (3) simulate_rho used
one array for both the m NOISE SD and the SE COLUMN the pipeline weights
by, so frozen G-M4's "every noise term zero" would have zeroed the weights
too (scripts 106 line 340 and 17 feed the recorded Mse) -- m_noise was
split off, defaulting to m_se so frozen M-3 is unchanged; (4) two of this
script's own toy expectations were wrong against the frozen text and were
corrected TO the frozen text: NEIGH section 2 says C1 is dseq <= 20 (my
toy had asserted dseq 40 -> C1), and a CI touching zero (0.0, 0.05) does
not exclude zero, same convention as M-1 (my toy had asserted it does).
The G-M3/whole-placebo identity and reference gates below are unaffected
by (4) and were re-run after every fix.

LIMITATIONS (AGENTS 6): A2-G2 re-derives CACHED Phase 1/2 numbers through
the new library -- it validates the library code, it is not independent
evidence for any claim, and it produces no new inference.  A2-G3's toys
fix the arithmetic, not the biology.

ENV: N_BOOT (default 10000), SEED (default 0), N_REF (default 500),
N_REF_PRE (default 20, pre-drawn whole-placebo draws against the slow
reference), N_PERM (default 1000, unused here but kept for parity).

Usage:
  smoke:  N_BOOT=300   venv/bin/python3 scripts/165_phase4_common_gate.py
  full:   N_BOOT=10000 SEED=0 venv/bin/python3 scripts/165_phase4_common_gate.py
"""

import hashlib
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr as _spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg                             # noqa
from scripts.lib import phase2_diag4 as p4d                            # noqa
from scripts.lib import phase3_common as p3c                           # noqa
from scripts.lib import phase4_common as p4c                           # noqa
from scripts.lib.stats_ext import rebuild_interaction_fit              # noqa

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_REF = int(os.environ.get("N_REF", "500"))
N_REF_PRE = int(os.environ.get("N_REF_PRE", "20"))

RHO_TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
RHO_TABLE_SHA = ("e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796")
TASK32 = ROOT / "data/processed/task32_analysis_table.csv"
S159 = ROOT / "scripts/159_phase3_common_gate.py"

# ---- A2-G2 targets: the planning doc's table, quoted, not recomputed ----
T_RHO_FULL = -0.088118064
T_RHO_H = -0.090021683
T_P_FULL = 2.0 / 79.0
T_P_H = 4.0 / 79.0
T_BEATERS_FULL = ["G_P254F"]
T_BEATERS_H = ["AV_195", "AV_220", "G_P254F"]
T_RHO_DS = -0.32376573717755663
T_RHO_ES = 0.085391652432165
T_PARTIAL_SW = -0.06414804421216103
T_RETENTION_4DP = 0.728
T_PARTIAL_2COV = -0.0829
T_ROWS, T_POS, T_HPOS = 10757, 654, 455
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.0595113844951173

TOL_9DP = 1e-9
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


# ==========================================================================
def gate_a2_g1():
    banner("GATE A2-G1 -- script 159 rerun UNCHANGED (HARD)", "-")
    nb = N_BOOT if N_BOOT == 10000 else 300
    env = dict(os.environ, N_BOOT=str(nb), SEED=str(SEED))
    print(f"  running: N_BOOT={nb} SEED={SEED} {sys.executable} {S159.name}")
    proc = subprocess.run([sys.executable, str(S159)], cwd=str(ROOT),
                          env=env, capture_output=True, text=True)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    print("  ---- subprocess tail (verbatim) ----")
    for ln in lines[-8:]:
        print("  " + ln)
    if proc.stderr.strip():
        print("  ---- subprocess stderr (verbatim) ----")
        for ln in proc.stderr.splitlines()[-10:]:
            print("  " + ln)
    print("  ---- end subprocess ----")
    want = f"{40} checks PASS, 0 FAIL" if nb == 10000 else None
    if nb == 10000:
        ok = (want in proc.stdout) and proc.returncode == 0
        gate("A2-G1 script 159 prints 40/40 PASS", ok,
             f"returncode {proc.returncode}; found {want!r} = "
             f"{want in proc.stdout} (target: the line "
             "'40/40 checks PASS, 0 FAIL', exit 0)")
    else:
        gate("A2-G1 script 159 rerun unchanged",
             "35/36 checks PASS, 1 FAIL (1 of the FAILs are smoke SKIPS)"
             in proc.stdout and proc.returncode == 0,
             f"SMOKE: N_BOOT={nb}; subprocess exit {proc.returncode}, "
             f"printed '"
             + next((ln.strip() for ln in lines
                     if "checks PASS" in ln), "<no summary line>")
             + "'. A2-G1 is DECIDED ONLY on the N_BOOT=10000 run -- this "
               "smoke cannot call it PASS.")


# ==========================================================================
def gate_a2_g2():
    banner("GATE A2-G2 -- cached MTHFR numbers through phase4_common "
           "(HARD)", "-")
    sha = hashlib.sha256(RHO_TABLE.read_bytes()).hexdigest()
    gate("A2-G2(a) rho table sha256", sha == RHO_TABLE_SHA,
         f"{sha}  (target {RHO_TABLE_SHA})")

    tb = time.time()
    _, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    print(f"  [pdg.build] {time.time() - tb:.1f}s -- script 125's cached "
          "construction, imported (AGENTS 2), not reimplemented")
    bgs = list(A.bgs)
    N_ids = list(A.N_IDS)

    # rows: task32, gated to the doc's 10,757 / 654
    t32 = pd.read_csv(TASK32, float_precision="round_trip")
    cols = ["delta_esm", "own_e_b", "position", "esm2_score",
            "base_functionality"]
    t32r = t32[t32[cols].notna().all(axis=1)]
    gate("A2-G2 rows / positions (target 10,757 / 654)",
         len(t32r) == T_ROWS and t32r.position.nunique() == T_POS,
         f"got {len(t32r)} rows / {t32r.position.nunique()} positions; "
         f"target {T_ROWS} / {T_POS}")

    dlt = t32r.delta_esm.to_numpy(float)
    own = t32r.own_e_b.to_numpy(float)
    sw = t32r.esm2_score.to_numpy(float)
    bf = t32r.base_functionality.to_numpy(float)

    # (b) rho full, two sources, through the library
    rho_t32 = p4c.spearman(dlt, own)
    ar = A.a222v_rows
    rho_125 = p4c.spearman(ar.delta.to_numpy(float),
                           ar.own_e_b.to_numpy(float))
    note("A2-G2(b) A222V rho full (task32 via p4c.spearman)", rho_t32,
         T_RHO_FULL, TOL_9DP)
    note("A2-G2(b) A222V rho full (script 125 rows via p4c.spearman)",
         rho_125, T_RHO_FULL, TOL_9DP)
    gate("A2-G2(b) the two sources agree with each other",
         abs(rho_t32 - rho_125) < TOL_12,
         f"|diff| {abs(rho_t32 - rho_125):.3e} (AGENTS 5 column identity)")

    # (c) rho H
    ah = ar[ar.position.isin(A.Hset)]
    gate("A2-G2(c) H positions (target 455)",
         len(A.Hset) == T_HPOS, f"got {len(A.Hset)} target {T_HPOS} "
         f"({len(ah)} anchor rows on H)")
    rho_h = p4c.spearman(ah.delta.to_numpy(float),
                         ah.own_e_b.to_numpy(float))
    note("A2-G2(c) A222V rho H", rho_h, T_RHO_H, TOL_9DP)
    note("A2-G2(c) A222V rho H (pdg.point_rhos_H cross-check)",
         float(rho_a_H), T_RHO_H, TOL_9DP)

    # (d)/(e) p_spec through the library
    rho_nf = table.loc[N_ids, "rho_full"].to_numpy(float)
    rho_nh = table.loc[N_ids, "rho_H"].to_numpy(float)
    p_f, k_f, n_f = p4c.p_spec(rho_t32, rho_nf, mode="neg")
    p_h, k_h, n_h = p4c.p_spec(rho_h, rho_nh, mode="neg")
    beat_f = sorted(table.loc[N_ids].index[rho_nf <= rho_t32].tolist())
    beat_h = sorted(table.loc[N_ids].index[rho_nh <= rho_h].tolist())
    gate("A2-G2(d) p_spec(neg) full",
         abs(p_f - T_P_FULL) < TOL_EXACT and k_f == 1 and n_f == 78
         and beat_f == T_BEATERS_FULL,
         f"p = (1+{k_f})/(1+{n_f}) = {p_f!r} target {T_P_FULL!r} "
         f"(2/79); k = {k_f} target 1; beaters {beat_f} target "
         f"{T_BEATERS_FULL}")
    gate("A2-G2(e) p_spec(neg) H",
         abs(p_h - T_P_H) < TOL_EXACT and k_h == 3 and n_h == 78
         and beat_h == T_BEATERS_H,
         f"p = (1+{k_h})/(1+{n_h}) = {p_h!r} target {T_P_H!r} (4/79); "
         f"k = {k_h} target 3; beaters {beat_h} target {T_BEATERS_H}")

    # (f)/(g) Phase 1 C1's two rank correlations, through the library
    r_ds = p4c.spearman(dlt, sw)
    r_es = p4c.spearman(own, sw)
    note("A2-G2(f) rho(delta, S_W)", r_ds, T_RHO_DS, TOL_12)
    note("A2-G2(g) rho(own_e.b, S_W)", r_es, T_RHO_ES, TOL_12)

    # (h) the rank partial with one control, through the library
    part1 = p4c.partial_spearman(dlt, own, [sw])
    note("A2-G2(h) partial rho controlling S_W (p4c.partial_spearman)",
         part1, T_PARTIAL_SW, TOL_12)
    ret = abs(part1) / abs(rho_t32)
    note("A2-G2(h) retention |partial|/|raw| (3 dp)", round(ret, 3),
         T_RETENTION_4DP, TOL_EXACT)
    print(f"       retention full precision = {ret!r}")

    # (i) the two-covariate rank partial (Phase 1 L2), through the library
    part2 = p4c.partial_spearman(dlt, own, [sw, bf])
    note("A2-G2(i) two-covariate partial (4 dp)", round(part2, 4),
         T_PARTIAL_2COV, TOL_EXACT)
    print(f"       full precision = {part2!r} (Phase 1 L2 printed -0.0829)")

    # ---- bootstrap reference gate on the real anchor rows (rule 6) ------
    banner("A2-G2 REFERENCE BOOTSTRAP on the real anchor rows "
           "(PHASE4 rule 6)", "-")
    ax, ay = dlt, own
    ap = t32r.position.to_numpy()
    point = p4c.spearman(ax, ay)
    nk = np.unique(ap).size
    ids_one = np.arange(nk, dtype=np.int64)[None, :]
    one = p4c.pos_cluster_boot_from_ids(ax, ay, ap, ids_one)[0]
    gate("rule 6 identity: every position once == point estimate",
         abs(float(one) - point) < TOL_12,
         f"every-once {float(one)!r} point {point!r} |diff| "
         f"{abs(float(one) - point):.3e} (gate < 1e-12)")
    ids, _ = p4c.draw_ids(ap, n_draw=N_REF, seed=SEED)
    d_new = p4c.pos_cluster_boot_from_ids(ax, ay, ap, ids)
    d_ref = p4c.reference_boot(ax, ay, ap, ids)
    md = float(np.max(np.abs(d_new - d_ref)))
    gate(f"rule 6 draw-by-draw reference ({N_REF} draws)", md < TOL_12,
         f"max|corrected - reference| = {md:.3e} (gate < 1e-12)")
    if N_BOOT == 10000:
        draws = p4c.pos_cluster_boot(ax, ay, ap, n_boot=N_BOOT, seed=SEED)
        lo, hi, nf = p4c.pct_ci(draws)
        note("rule 6 Phase 1 CI lo", lo, T_CI_LO, TOL_9DP)
        note("rule 6 Phase 1 CI hi", hi, T_CI_HI, TOL_9DP)
        print(f"       ({nf} finite draws, N_BOOT={N_BOOT}, SEED={SEED}; "
              "the routine is phase2_diag4's, imported)")
    else:
        gate("rule 6 Phase 1 CI reproduction", False,
             f"SKIPPED (smoke): N_BOOT={N_BOOT} != 10000 -- A2-G2/G3 "
             "cannot be called PASS on this run")


# ==========================================================================
def gate_a2_g3():
    banner("GATE A2-G3 -- toy-data gates for every phase4_common function "
           "(HARD)", "-")
    g = gate

    # ---- re-exports are the imported objects, not copies ----------------
    g("A2-G3 re-exports are the imported objects",
      p4c.spearman is p3c.spearman
      and p4c.p_spec is p3c.p_spec
      and p4c.pos_cluster_boot is p3c.pos_cluster_boot
      and p4c.pos_cluster_boot_corrected is p4d.pos_cluster_boot_corrected
      and p4c.reference_boot is p3c.reference_boot,
      "p4c.spearman/p_spec/pos_cluster_boot/reference_boot are "
      "phase3_common's objects; p4c.pos_cluster_boot_corrected is "
      "phase2_diag4's object (script 144's routine is never importable "
      "from this path)")

    # ---- equal_count_bins ------------------------------------------------
    lab = p4c.equal_count_bins(np.arange(10.0), 2)
    sizes = np.bincount(lab, minlength=2).tolist()
    b0 = np.sort(np.arange(10.0)[lab == 0]).tolist()
    g("A2-G3 equal_count_bins 10 -> 2",
      sizes == [5, 5] and b0 == [0.0, 1.0, 2.0, 3.0, 4.0],
      f"sizes {sizes} target [5, 5]; lower bin {b0} target "
      "[0.0, 1.0, 2.0, 3.0, 4.0]")
    lab4 = p4c.equal_count_bins(np.arange(11.0), 4)
    sizes4 = np.bincount(lab4, minlength=4).tolist()
    g("A2-G3 equal_count_bins 11 -> 4", sizes4 == [3, 3, 3, 2],
      f"sizes {sizes4} target [3, 3, 3, 2]")
    try:
        p4c.equal_count_bins(np.arange(5.0), 7)
        g("A2-G3 equal_count_bins rejects n_bins > n", False,
          "no error raised; target: ValueError")
    except ValueError as e:
        g("A2-G3 equal_count_bins rejects n_bins > n", True,
          f"ValueError: {e}")

    # ---- stratified_spearman --------------------------------------------
    xs = np.arange(1, 9.0)
    st = np.array(["a"] * 4 + ["b"] * 4)
    v = p4c.stratified_spearman(xs, xs, st)
    g("A2-G3 stratified_spearman both strata monotone",
      abs(v - 1.0) < TOL_EXACT, f"got {v!r} target 1.0")
    x2 = np.array([1.0, 2, 3, 4, 1, 2, 3, 4])
    y2 = np.array([1.0, 2, 3, 4, 3, 1, 4, 2])     # stratum b rho = 0 exactly
    v2 = p4c.stratified_spearman(x2, y2, st)
    g("A2-G3 stratified_spearman weighted mean (1.0, 0.0) at 4/4",
      abs(v2 - 0.5) < TOL_EXACT,
      f"got {v2!r} target 0.5 = (4*1.0 + 4*0.0)/8")
    st3 = np.array(["a"] * 4 + ["b"] * 4 + ["c"] * 4)
    x3 = np.concatenate([x2, np.arange(1, 5.0)])   # stratum c: x = 1..4
    y3 = np.concatenate([y2, np.full(4, 7.0)])    # c constant -> NaN rho
    v3 = p4c.stratified_spearman(x3, y3, st3)
    g("A2-G3 stratified_spearman drops the undefined stratum (I1)",
      abs(v3 - 0.5) < TOL_EXACT,
      f"got {v3!r} target 0.5 (stratum c constant y dropped, weights "
      "renormalised over a and b)")

    # ---- decomposition: planted pure-between and pure-within ------------
    pb_x, pb_y, pb_p = [], [], []
    for p in range(6):
        base = 10.0 * (p + 1)
        xv = base + np.array([1.0, 2, 3, 4])
        yv = 3.0 * p + np.array([3.0, 1, 4, 2])
        pb_x += list(xv); pb_y += list(yv); pb_p += [p] * 4
    dpb = p4c.between_within_decomposition(pb_x, pb_y, pb_p, min_rows=4)
    g("A2-G3 decomposition PLANTED PURE-BETWEEN",
      abs(dpb["rho_between"] - 1.0) < TOL_EXACT
      and abs(dpb["rho_within"] - 0.0) < TOL_EXACT,
      f"rho_between {dpb['rho_between']!r} target 1.0; rho_within "
      f"{dpb['rho_within']!r} target 0.0 (each position's y is the fixed "
      "permutation 3,1,4,2 of its x -> within-rho 0; position means "
      "strictly ordered -> between-rho 1)")
    pw_x, pw_y, pw_p = [], [], []
    base_x = [10.0, 20.0, 30.0, 40.0]
    base_y = [30.0, 10.0, 40.0, 20.0]            # ranks 3,1,4,2
    for p in range(4):
        off = np.array([1.0, 2, 3, 4]) * 0.1
        pw_x += list(base_x[p] + off)
        pw_y += list(base_y[p] + off)             # y = x + const per position
        pw_p += [p] * 4
    dpw = p4c.between_within_decomposition(pw_x, pw_y, pw_p, min_rows=4)
    g("A2-G3 decomposition PLANTED PURE-WITHIN",
      abs(dpw["rho_within"] - 1.0) < TOL_EXACT
      and abs(dpw["rho_between"] - 0.0) < TOL_EXACT,
      f"rho_within {dpw['rho_within']!r} target 1.0; rho_between "
      f"{dpw['rho_between']!r} target 0.0 (position means ordered 1,2,3,4 "
      "against 3,1,4,2 -> 0; within-position y = x + const -> 1)")
    dmr = p4c.between_within_decomposition(
        list(pb_x) + [1.0, 2.0, 3.0], list(pb_y) + [1.0, 5.0, 9.0],
        list(pb_p) + [99, 99, 99], min_rows=4)
    g("A2-G3 decomposition excludes a position below min_rows (I2)",
      dmr["n_qualifying"] == 6 and dmr["n_positions"] == 7,
      f"n_qualifying {dmr['n_qualifying']} target 6; n_positions "
      f"{dmr['n_positions']} target 7 (the 3-row position is excluded)")

    # ---- partial_spearman vs the closed-form formulas --------------------
    rng = np.random.default_rng(7)
    n = 500
    a = rng.normal(size=n)
    c1 = rng.normal(size=n)
    c2 = rng.normal(size=n)
    b = 0.6 * a + 0.4 * c1 + rng.normal(size=n) * 0.5
    r_xy = float(_spearmanr(a, b).statistic)
    r_xz = float(_spearmanr(a, c1).statistic)
    r_yz = float(_spearmanr(b, c1).statistic)
    closed1 = _closed_partial_1cov(r_xy, r_xz, r_yz)
    got1 = p4c.partial_spearman(a, b, [c1])
    d1 = abs(got1 - closed1)
    g("A2-G3 partial == closed form (1 control)", d1 < TOL_12,
      f"library {got1!r} closed form {closed1!r} |diff| {d1:.3e} "
      "(gate < 1e-12)")
    r_x1 = float(_spearmanr(a, c1).statistic)
    r_x2 = float(_spearmanr(a, c2).statistic)
    r_y1 = float(_spearmanr(b, c1).statistic)
    r_y2 = float(_spearmanr(b, c2).statistic)
    r_12 = float(_spearmanr(c1, c2).statistic)
    closed2 = _closed_partial_2cov(r_xy, r_x1, r_x2, r_y1, r_y2, r_12)
    got2 = p4c.partial_spearman(a, b, [c1, c2])
    d2 = abs(got2 - closed2)
    g("A2-G3 partial == closed form (2 controls, matrix inversion)",
      d2 < TOL_12,
      f"library {got2!r} closed form {closed2!r} |diff| {d2:.3e} "
      "(gate < 1e-12)")

    # ---- within-group permutation ---------------------------------------
    vals = np.arange(12.0)
    grp = np.array([0] * 4 + [1] * 4 + [2] * 4)
    r1 = np.random.default_rng(3)
    sh = p4c.permute_within_groups(vals, grp, r1)
    ok_multiset = all(np.array_equal(np.sort(sh[grp == k]),
                                     np.sort(vals[grp == k]))
                      for k in (0, 1, 2))
    ok_mean = all(abs(sh[grp == k].mean() - vals[grp == k].mean()) < TOL_12
                  for k in (0, 1, 2))
    ok_global = np.array_equal(np.sort(sh), np.sort(vals))
    g("A2-G3 permute_within_groups preserves each group's multiset and "
      "mean", ok_multiset and ok_mean and ok_global,
      f"per-group multiset {ok_multiset}, per-group means {ok_mean} "
      f"(position-level structure kept), global multiset {ok_global}")
    sh2 = p4c.permute_within_groups(vals, grp, np.random.default_rng(3))
    sh3 = p4c.permute_within_groups(vals, grp, np.random.default_rng(4))
    g("A2-G3 permute_within_groups is seeded and actually shuffles",
      np.array_equal(sh, sh2) and not np.array_equal(sh, sh3)
      and not np.array_equal(sh, vals),
      f"same seed reproduces {np.array_equal(sh, sh2)}; different seed "
      f"differs {not np.array_equal(sh, sh3)}; not the identity "
      f"{not np.array_equal(sh, vals)}")

    # ---- simulation harness --------------------------------------------
    nvar = 12
    hgvs = np.array([f"p.X{i}Val" for i in range(nvar)], dtype=object)
    hgvs[0] = "p.Ala222Val"
    w_s = np.linspace(0.35, 0.75, nvar)[:, None] * np.ones((1, 4))
    w_se = np.full((nvar, 4), 0.05)
    m_s = w_s * np.linspace(0.9, 1.1, 4)[None, :] + 0.02
    m_se = np.full((nvar, 4), 0.04)
    raw = p4c.raw_frame(w_s, w_se, m_s, m_se, hgvs)
    eb_direct = np.asarray(rebuild_interaction_fit(raw)["e2"]["e_b"],
                           dtype=float)
    eb_lib = p4c.own_eb_from_arrays(w_s, w_se, m_s, m_se, hgvs)
    dd = float(np.nanmax(np.abs(eb_lib - eb_direct)))
    g("A2-G3 harness == the project's rebuild_interaction_fit", dd < TOL_12,
      f"max|diff| {dd:.3e} (gate < 1e-12); own_eb_from_arrays must be the "
      "unmodified pipeline, not a re-derivation")

    delta_toy = rng.normal(size=nvar)
    # frozen G-M4: EVERY NOISE TERM ZERO, E = the observed m -> the
    # pipeline must return the RECORDED own_e.b.  m_se stays RECORDED (it
    # is the se column the pipeline weights by, scripts 106/17); only the
    # added noise is zeroed, via m_noise (zero_epistasis_draw's note).
    res = p4c.simulate_rho(w_s, w_se, m_s, m_se,
                           np.zeros(nvar), delta_toy, hgvs, n_draw=1,
                           seed=SEED, m_noise=np.zeros((nvar, 4)))
    eb0 = p4c.own_eb_from_arrays(w_s, w_se, m_s, m_se, hgvs)
    rho0 = p4c.spearman(delta_toy, eb0)
    g("A2-G3 G-M4 simulation identity (zero noise, E = observed m)",
      abs(float(res["rho"][0]) - rho0) < TOL_12,
      f"simulate_rho {float(res['rho'][0])!r} direct {rho0!r} |diff| "
      f"{abs(float(res['rho'][0]) - rho0):.3e} (gate < 1e-12)")

    z = p4c.rank_normal_z(np.arange(1, 6.0))
    g("A2-G3 rank_normal_z: mean 0, sd 1, 0 at the median, antisymmetric",
      abs(z.mean()) < TOL_12 and abs(z.std(ddof=0) - 1.0) < TOL_12
      and abs(z[2]) < TOL_12 and abs(z[0] + z[4]) < TOL_12
      and abs(z[1] + z[3]) < TOL_12,
      f"mean {z.mean():.3e}, sd {z.std(ddof=0)!r}, z[2] {z[2]:.3e}, "
      f"z[0]+z[4] {z[0] + z[4]:.3e}, z[1]+z[3] {z[1] + z[3]:.3e} "
      "(v = 1..5, q = (r-0.5)/5 = 0.1/0.3/0.5/0.7/0.9)")
    se_plant = 0.25
    u = np.ones(5)
    p_pos = p4c.plant_term(1.0, se_plant, z, u)
    p_neg = p4c.plant_term(-1.0, se_plant, z, u)
    p_zer = p4c.plant_term(0.0, se_plant, z, u)
    g("A2-G3 plant_term at r0 = +1 / -1 / 0",
      np.max(np.abs(p_pos - se_plant * z)) < TOL_EXACT
      and np.max(np.abs(p_neg + se_plant * z)) < TOL_EXACT
      and np.max(np.abs(p_zer - se_plant * u)) < TOL_EXACT,
      f"r0=+1 == s_e*z {np.max(np.abs(p_pos - se_plant * z)):.3e}; "
      f"r0=-1 == -s_e*z {np.max(np.abs(p_neg + se_plant * z)):.3e}; "
      f"r0=0 == s_e*u {np.max(np.abs(p_zer - se_plant * u)):.3e}")

    # ---- power curve and minimum detectable effect -----------------------
    zero = np.zeros(100)
    bands = {-0.1: np.r_[np.full(90, -0.5), np.full(10, 0.1)],
             -0.05: np.r_[np.full(10, -0.5), np.full(90, 0.1)],
             0.0: zero,
             0.05: np.r_[np.full(10, 0.5), np.full(90, -0.1)],
             0.1: np.r_[np.full(90, 0.5), np.full(10, -0.1)]}
    pc = p4c.power_curve(list(bands), bands)
    pw = dict(zip([float(x) for x in pc["r0"]],
                  [float(x) for x in pc["power"]]))
    mr = dict(zip([float(x) for x in pc["r0"]],
                  [float(x) for x in pc["mean_rho"]]))
    g("A2-G3 power_curve hand-built bands",
      abs(pc["q_lo"] - 0.0) < TOL_EXACT and abs(pc["q_hi"] - 0.0) < TOL_EXACT
      and abs(pw[-0.1] - 0.90) < TOL_EXACT
      and abs(pw[-0.05] - 0.10) < TOL_EXACT
      and abs(pw[0.05] - 0.10) < TOL_EXACT
      and abs(pw[0.1] - 0.90) < TOL_EXACT
      and abs(pw[0.0] - 1.00) < TOL_EXACT,
      f"q_lo {pc['q_lo']!r} q_hi {pc['q_hi']!r} (both 0.0); power "
      f"r0=-0.1 {pw[-0.1]!r} (target 0.90), -0.05 {pw[-0.05]!r} (0.10), "
      f"+0.05 {pw[0.05]!r} (0.10), +0.1 {pw[0.1]!r} (0.90), 0 {pw[0.0]!r} "
      "(1.00, all zero-band draws <= 0)")
    g("A2-G3 power_curve mean_rho is each band's mean",
      abs(mr[-0.1] - bands[-0.1].mean()) < TOL_EXACT
      and abs(mr[0.1] - bands[0.1].mean()) < TOL_EXACT,
      f"r0=-0.1 mean {mr[-0.1]!r} vs {bands[-0.1].mean()!r}; r0=+0.1 mean "
      f"{mr[0.1]!r} vs {bands[0.1].mean()!r}")
    r0g = [-0.1, -0.05, 0.0, 0.05, 0.1]
    md = p4c.min_detectable_effect(r0g, [0.9, 0.1, 0.025, 0.1, 0.9])
    expect = 0.05 + (0.8 - 0.1) / (0.9 - 0.1) * 0.05     # = 0.09375
    g("A2-G3 min_detectable_effect interpolation (I5)",
      abs(md["neg"] - expect) < TOL_EXACT
      and abs(md["pos"] - expect) < TOL_EXACT
      and abs(md["headline"] - expect) < TOL_EXACT,
      f"neg {md['neg']!r} pos {md['pos']!r} headline {md['headline']!r} "
      f"target {expect!r} (= 0.05 + (0.8-0.1)/(0.9-0.1)*0.05 = 0.09375)")
    md2 = p4c.min_detectable_effect(r0g, [0.1, 0.2, 0.025, 0.2, 0.1])
    g("A2-G3 min_detectable_effect 'above the grid'",
      md2["neg"] == "above the grid" and md2["pos"] == "above the grid"
      and md2["headline"] == "above the grid",
      f"neg {md2['neg']!r} pos {md2['pos']!r} headline "
      f"{md2['headline']!r}; target the string 'above the grid' on all "
      "three")
    md3 = p4c.min_detectable_effect(r0g, [0.9, 0.2, 0.025, 0.3, 0.4])
    g("A2-G3 min_detectable_effect one side only -> headline = that side",
      isinstance(md3["pos"], str) and md3["pos"] == "above the grid"
      and abs(md3["headline"] - md3["neg"]) < TOL_EXACT,
      f"neg {md3['neg']!r} pos {md3['pos']!r} headline "
      f"{md3['headline']!r} (headline must be the numeric side)")
    sl, ic = p4c.attenuation_slope([-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0])
    g("A2-G3 attenuation_slope", abs(sl - 2.0) < TOL_12
      and abs(ic - 0.0) < TOL_12,
      f"slope {sl!r} intercept {ic!r} target 2.0 / 0.0")

    # ---- whole-placebo bootstrap: identity, reference, determinism -------
    B, POS, ROWS = 5, 12, 4
    rr = np.random.default_rng(11)
    delta = rr.normal(size=(B, POS * ROWS))
    own_t = rr.normal(size=POS * ROWS)
    post = np.repeat(np.arange(POS), ROWS)
    for b in range(B):                      # each background lacks its own pos
        own_pos = b * 2 % POS
        delta[b][post == own_pos] = np.nan
    # observed statistic, computed independently (scipy, all rows at once)
    rhos_obs = []
    for b in range(B):
        m = np.isfinite(delta[b]) & np.isfinite(own_t)
        rhos_obs.append(float(_spearmanr(delta[b][m], own_t[m]).statistic))
    t_idx, n_idx = 0, [1, 2, 3, 4]
    obs = p4c.observed_placebo(delta, own_t, post, t_idx, n_idx)
    k_obs = int(sum(1 for j in n_idx if rhos_obs[j] <= rhos_obs[0]))
    p_obs = (1 + k_obs) / (1 + len(n_idx))
    g("A2-G3 whole_placebo IDENTITY (every position once == observed, "
      "frozen G-M7)",
      abs(float(obs["p_spec_neg"][0]) - p_obs) < TOL_EXACT
      and int(obs["k"][0]) == k_obs
      and abs(float(obs["rho_A"][0]) - rhos_obs[0]) < TOL_12,
      f"p_spec {float(obs['p_spec_neg'][0])!r} target {p_obs!r}; "
      f"k {int(obs['k'][0])} target {k_obs}; rho_A "
      f"{float(obs['rho_A'][0])!r} target {rhos_obs[0]!r}")
    nk = POS
    rng_ids = np.random.default_rng(SEED)
    ids = np.array([rng_ids.integers(0, nk, nk) for _ in range(N_REF_PRE)])
    d_new = p4c.whole_placebo_boot_from_ids(delta, own_t, post, t_idx,
                                            n_idx, ids)
    d_ref = p4c.whole_placebo_reference(delta, own_t, post, t_idx, n_idx,
                                        ids)
    md1 = float(np.max(np.abs(d_new["rho_A"] - d_ref["rho_A"])))
    md2 = float(np.max(np.abs(d_new["rho_N"] - d_ref["rho_N"])))
    md3 = float(np.max(np.abs(d_new["k"] - d_ref["k"])))
    md4 = float(np.max(np.abs(d_new["p_spec_neg"] - d_ref["p_spec_neg"])))
    g(f"A2-G3 whole_placebo DRAW-BY-DRAW reference ({N_REF_PRE} draws)",
      max(md1, md2, md4) < TOL_12 and md3 == 0.0,
      f"max|new - reference|: rho_A {md1:.3e}, rho_N {md2:.3e}, k {md3}, "
      f"p_spec {md4:.3e} (gate < 1e-12; the reference rebuilds "
      "position -> rows with flatnonzero and calls scipy per background)")
    det1 = p4c.whole_placebo_boot(delta, own_t, post, t_idx, n_idx,
                                  n_draw=5, seed=SEED)
    det2 = p4c.whole_placebo_boot(delta, own_t, post, t_idx, n_idx,
                                  n_draw=5, seed=SEED)
    g("A2-G3 whole_placebo DETERMINISM (same seed)",
      np.array_equal(det1["rho_A"], det2["rho_A"])
      and np.array_equal(det1["k"], det2["k"]),
      f"rho_A identical {np.array_equal(det1['rho_A'], det2['rho_A'])}, k "
      f"identical {np.array_equal(det1['k'], det2['k'])}")

    # ---- 2x2 geometry ----------------------------------------------------
    d3 = np.array([12.0, 12.000001, 18.0, 18.000001, 20.0, 20.000001,
                   15.0, 11.0, np.nan])
    ds = np.array([20.0, 20.0, 25.0, 25.0, 41.0, 41.0, 30.0, 50.0, 10.0])
    got_cells = list(p4c.cell_labels(d3, ds))
    want_cells = ["C1", "", "", "C3", "", "C4", "", "C2", ""]
    g("A2-G3 cell_labels frozen boundaries and gaps",
      got_cells == want_cells,
      f"got {got_cells} target {want_cells} (d3=12 in C1, 12.000001 out; "
      "d3=18 is NOT > 18 so out of C3 until 18.000001; d3=20 is NOT > 20 "
      "so out of C4 until 20.000001; dseq 21..40 in no cell; NaN -> '')")
    ds2 = np.array([20.0, 20.000001, 40.0, 40.000001, 21.0])
    d32 = np.array([11.0, 11.0, 11.0, 11.0, 11.0])
    g("A2-G3 cell_labels C1/C2 dseq boundary (frozen NEIGH section 2: "
      "C1 is dseq <= 20, C2 is dseq > 40)",
      list(p4c.cell_labels(d32, ds2)) == ["C1", "", "", "C2", ""],
      f"got {list(p4c.cell_labels(d32, ds2))} target "
      "['C1', '', '', 'C2', ''] (dseq 20 -> C1, 20.000001 -> gap, 40 -> "
      "gap because C2 needs > 40, 40.000001 -> C2, 21 -> gap; the frozen "
      "text is C1: d3 <= 12 AND dseq <= 20; C2: d3 <= 12 AND dseq > 40)")
    s = np.array([1.0, 5.0, 6.0, 15.0, 16.0, 54.0, 55.0])
    rules = [(1, 5, "near", True, True), (6, 15, "mid", True, True),
             (16, 54, "far", True, True)]
    g("A2-G3 interval_labels GB1 separation strata 1-5 / 6-15 / 16-54",
      list(p4c.interval_labels(s, rules)) ==
      ["near", "near", "mid", "mid", "far", "far", ""],
      f"got {list(p4c.interval_labels(s, rules))} target "
      "['near', 'near', 'mid', 'mid', 'far', 'far', '']")
    sa = np.array([7.9, 8.0, 14.0, 14.0001])
    rules_a = [(-np.inf, 8, "d3_lt8", True, False),
               (8, 14, "d3_8_14", True, True),
               (14, np.inf, "d3_gt14", False, True)]
    g("A2-G3 interval_labels GB1 Angstrom strata <8 / 8-14 / >14",
      list(p4c.interval_labels(sa, rules_a)) ==
      ["d3_lt8", "d3_8_14", "d3_8_14", "d3_gt14"],
      f"got {list(p4c.interval_labels(sa, rules_a))} target "
      "['d3_lt8', 'd3_8_14', 'd3_8_14', 'd3_gt14']")
    g("A2-G3 seq_separation",
      abs(float(p4c.seq_separation(100, 222)) - 122.0) < TOL_EXACT
      and abs(float(p4c.seq_separation(222, 100)) - 122.0) < TOL_EXACT,
      f"|100-222| = {float(p4c.seq_separation(100, 222))!r} target 122.0")

    # ---- AUROC and balanced-PR vs scikit-learn ---------------------------
    from sklearn.metrics import auc as sk_auc
    from sklearn.metrics import precision_recall_curve, roc_auc_score
    from sklearn.metrics import roc_curve as sk_roc_curve
    toys = [
        ("with ties", np.array([0, 0, 1, 1, 1, 0, 1, 0], dtype=bool),
         np.array([0.1, 0.5, 0.5, 0.9, 0.2, 0.5, 0.7, 0.3])),
        ("perfect", np.array([0, 0, 0, 1, 1, 1], dtype=bool),
         np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])),
        ("inverted", np.array([1, 1, 1, 0, 0, 0], dtype=bool),
         np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])),
    ]
    for name, yy, ss in toys:
        mine = p4c.auroc(yy, ss)
        theirs = float(roc_auc_score(yy, ss))
        g(f"A2-G3 auroc == sklearn ({name})", abs(mine - theirs) < TOL_12,
          f"library {mine!r} sklearn {theirs!r} |diff| "
          f"{abs(mine - theirs):.3e} (gate < 1e-12)")
    # balanced-PR against sklearn's OWN weighted precision_recall_curve
    yy, ss = np.array([0, 0, 1, 1, 1, 0, 1, 0, 1, 0] * 3, dtype=bool), \
        np.array([0.1, 0.5, 0.5, 0.9, 0.2, 0.5, 0.7, 0.3, 0.6, 0.4] * 3)
    rr_, bp_ = p4c.balanced_pr_curve(yy, ss)
    P_, N_ = int(yy.sum()), int((~yy).sum())
    pr_, rc_, _ = precision_recall_curve(
        yy, ss, sample_weight=np.where(yy, N_, P_))
    rc_a = rc_[::-1]
    pr_a = pr_[::-1]
    d_recall = float(np.max(np.abs(rr_[1:] - rc_a[1:])))
    d_bp = float(np.max(np.abs(bp_[1:] - pr_a[1:])))
    g("A2-G3 balanced_pr_curve coordinates == sklearn's weighted "
      "precision_recall_curve (recall 1..end)",
      d_recall < TOL_12 and d_bp < TOL_12,
      f"max|diff| recall {d_recall:.3e}, balanced precision {d_bp:.3e} "
      f"(gate < 1e-12).  sklearn's precision with sample weights "
      f"N={N_} on positives and P={P_} on negatives is "
      "N*TP/(N*TP+P*FP) = TPR/(TPR+FPR) exactly")
    g("A2-G3 balanced_pr anchor equals the top threshold's own value "
      "(decision I6)",
      abs(bp_[0] - bp_[1]) < TOL_EXACT,
      f"bp[0] {bp_[0]!r} bp[1] {bp_[1]!r} (recall 0 is anchored at the top "
      f"threshold, not at sklearn's artificial precision=1.0 point "
      f"{pr_a[0]!r}; that one conventional difference is "
      f"{abs(bp_[0] - pr_a[0]):.3e} and is documented by decision I6)")
    mine_area = p4c.balanced_pr_auc(yy, ss)
    pr_anchor = np.r_[pr_a[1], pr_a[1:]]
    their_area = float(sk_auc(rc_a, pr_anchor))
    d_area = abs(mine_area - their_area)
    g("A2-G3 balanced_pr_auc == sklearn.metrics.auc on the same "
      "coordinates", d_area < TOL_12,
      f"library {mine_area!r} sklearn-path {their_area!r} |diff| "
      f"{d_area:.3e} (gate < 1e-12)")
    fpr_, tpr_, _ = sk_roc_curve(yy, ss, drop_intermediate=False)
    bp_roc = tpr_[1:] / (tpr_[1:] + fpr_[1:])
    d_roc = float(np.max(np.abs(bp_[1:] - bp_roc)))
    g("A2-G3 balanced_pr coordinates == sklearn's roc_curve path "
      "(second independent sklearn path)", d_roc < TOL_12,
      f"max|diff| {d_roc:.3e} (gate < 1e-12); chance level 0.5 = "
      f"{1.0 / 2.0!r}")
    # balanced-PR of a chance classifier sits at 0.5
    chance = p4c.balanced_pr_auc(np.array([1, 0] * 50, dtype=bool),
                                 np.random.default_rng(0).normal(size=100))
    g("A2-G3 balanced_pr_auc of a chance-level toy is finite and "
      "near 0.5", np.isfinite(chance) and abs(chance - 0.5) < 0.1,
      f"got {chance!r}, target finite and within 0.1 of 0.5 "
      "(balanced precision = TPR/(TPR+FPR) = 0.5 at chance)")

    # ---- outcome words: every frozen block, boundary cases ---------------
    g("A2-G3 word_m1_partial (MECH M-1)",
      p4c.word_m1_partial(-0.12, -0.05, 0.03, 0.08) == "PARTIAL-SURVIVES"
      and p4c.word_m1_partial(-0.12, -0.05, 0.05, 0.10)
      == "PARTIAL-SURVIVES"
      and p4c.word_m1_partial(-0.12, -0.05, 0.051, 0.10)
      == "PARTIAL-WEAKENS"
      and p4c.word_m1_partial(-0.12, -0.05, 0.03, 0.101)
      == "PARTIAL-WEAKENS"
      and p4c.word_m1_partial(-0.05, 0.01, 0.01, 0.01)
      == "PARTIAL-DOES-NOT-SURVIVE"
      and p4c.word_m1_partial(0.01, 0.05, 0.01, 0.01)
      == "PARTIAL-DOES-NOT-SURVIVE",
      "targets: (<=0.05, <=0.10) -> PARTIAL-SURVIVES including exactly "
      "0.05/0.10; a failing p -> PARTIAL-WEAKENS; CI touching 0 or a "
      "positive CI -> PARTIAL-DOES-NOT-SURVIVE")
    g("A2-G3 word_m3_artifact (MECH M-3)",
      p4c.word_m3_artifact(-0.088118, -0.088117) == "EXCESS-OVER-ARTIFACT"
      and p4c.word_m3_artifact(-0.09, -0.09) == "EXCESS-OVER-ARTIFACT"
      and p4c.word_m3_artifact(-0.08, -0.09) == "CONSISTENT-WITH-ARTIFACT",
      "targets: obs <= p2.5 (including equal) -> EXCESS-OVER-ARTIFACT, "
      "else CONSISTENT-WITH-ARTIFACT")
    g("A2-G3 word_m5_carry (MECH M-5)",
      p4c.word_m5_carry((-0.1, -0.02), 0.04, (-0.2, 0.05), 0.4)
      == "WITHIN-CARRIED"
      and p4c.word_m5_carry((-0.2, 0.05), 0.4, (-0.1, -0.02), 0.04)
      == "BETWEEN-CARRIED"
      and p4c.word_m5_carry((-0.1, -0.02), 0.04, (-0.1, -0.02), 0.05)
      == "BOTH-CARRY"
      and p4c.word_m5_carry((-0.2, 0.05), 0.4, (-0.2, 0.05), 0.4)
      == "NEITHER-CARRIES"
      and p4c.word_m5_carry((-0.1, -0.02), 0.0501, (-0.2, 0.05), 0.4)
      == "NEITHER-CARRIES",
      "targets: both meet -> BOTH-CARRY; only within -> WITHIN-CARRIED; "
      "only between -> BETWEEN-CARRIED; neither -> NEITHER-CARRIES; "
      "p = 0.05 exactly meets, 0.0501 does not")
    g("A2-G3 word_m6_stable (MECH M-6)",
      p4c.word_m6_stable(0.80) == "STABLE"
      and p4c.word_m6_stable(0.79) == "MODERATE"
      and p4c.word_m6_stable(0.50) == "MODERATE"
      and p4c.word_m6_stable(0.499) == "FRAGILE",
      "targets: >= 0.80 STABLE; [0.50, 0.80) MODERATE (0.50 is MODERATE); "
      "< 0.50 FRAGILE")
    g("A2-G3 word_conditioning (UTIL U-1 / U-2)",
      p4c.word_conditioning(0.01, 0.03) == "CONDITIONING-HELPS"
      and p4c.word_conditioning(-0.03, -0.01) == "CONDITIONING-HURTS"
      and p4c.word_conditioning(-0.019, 0.019) == "EQUIVALENT"
      and p4c.word_conditioning(-0.02, 0.02) == "INCONCLUSIVE"
      and p4c.word_conditioning(-0.03, 0.01) == "INCONCLUSIVE"
      and p4c.word_conditioning(0.005, 0.015) == "CONDITIONING-HELPS",
      "targets: entirely above 0 -> HELPS; entirely below 0 -> HURTS; "
      "strictly inside (-0.02, +0.02) -> EQUIVALENT; touching -0.02/+0.02 "
      "-> INCONCLUSIVE; a positive CI inside the margin -> HELPS "
      "(precedence rule I7, the frozen order)")
    g("A2-G3 word_underpowered (UTIL)",
      p4c.word_underpowered(14, 100) == "UNDERPOWERED"
      and p4c.word_underpowered(100, 14) == "UNDERPOWERED"
      and p4c.word_underpowered(15, 15) is None,
      "targets: 14 vs 100 (either side) -> UNDERPOWERED; 15 and 15 -> "
      "no word (None)")
    g("A2-G3 GB1D outcome words",
      p4c.gb1_model_decays(-0.05, -0.01) is True
      and p4c.gb1_model_decays(-0.05, 0.01) is False
      and p4c.gb1_model_decays(0.01, 0.05) is False
      and p4c.gb1_data_decays(-0.05, -0.01) is True
      and p4c.gb1_data_decays(-0.05, 0.0) is False
      and p4c.gb1_locality_differs(-0.05, -0.01) is True
      and p4c.gb1_locality_differs(-0.05, 0.01) is False
      and p4c.gb1_separation(-0.05, -0.01) == "SEPARATION-MATTERS"
      and p4c.gb1_separation(-0.05, 0.01) == "SEPARATION-NOT-RESOLVED",
      "targets: iff-conditions returned as BOOL for the three blocks with "
      "no else-word (I8), CI touching 0 -> False; SEPARATION-MATTERS iff "
      "the CI excludes 0, else SEPARATION-NOT-RESOLVED")
    g("A2-G3 word_neighbour (NEIGH section 5)",
      p4c.word_neighbour(0.05, 30) == "POSITION-SPECIFIC"
      and p4c.word_neighbour(0.04, 30) == "POSITION-SPECIFIC"
      and p4c.word_neighbour(0.05, 29) == "UNDERPOWERED"
      and p4c.word_neighbour(0.10, 40) == "UNRESOLVED"
      and p4c.word_neighbour(0.0500001, 40) == "UNRESOLVED"
      and p4c.word_neighbour(0.1000001, 40) == "REGION-LIKE"
      and p4c.word_neighbour(0.5, 29) == "UNDERPOWERED",
      "targets: |NB| 30 & p <= 0.05 -> POSITION-SPECIFIC (0.05 exactly "
      "meets); |NB| 29 -> UNDERPOWERED whatever p; 0.05 < p <= 0.10 -> "
      "UNRESOLVED; p > 0.10 -> REGION-LIKE")
    g("A2-G3 word_distance (NEIGH section 6)",
      p4c.word_distance((-0.05, -0.01), (-0.2, 0.2)) == "3D-LOCAL"
      and p4c.word_distance((-0.2, 0.2), (-0.05, -0.01)) == "SEQUENCE-LOCAL"
      and p4c.word_distance((-0.05, -0.01), (-0.05, -0.01)) == "BOTH-LOCAL"
      and p4c.word_distance((-0.2, 0.2), (-0.2, 0.2)) == "NEITHER-RESOLVED"
      and p4c.word_distance((0.01, 0.05), (-0.2, 0.2)) == "3D-LOCAL"
      and p4c.word_distance((-0.2, 0.2), (0.01, 0.05)) == "SEQUENCE-LOCAL"
      and p4c.word_distance((0.0, 0.05), (-0.2, 0.2))
      == "NEITHER-RESOLVED",
      "targets: only d3 excludes 0 -> 3D-LOCAL; only dseq -> "
      "SEQUENCE-LOCAL; both -> BOTH-LOCAL; neither -> NEITHER-RESOLVED; a "
      "strictly positive CI excludes 0 as well; and a CI TOUCHING zero "
      "(0.0, 0.05) does NOT exclude it, same convention as M-1 -- "
      "_excludes_zero is lo > 0 or hi < 0")
    g("A2-G3 word_ladder (LADDER section 3)",
      p4c.word_ladder(-0.12, -0.05, 0.09) == "MODEL-REPLICATES"
      and p4c.word_ladder(-0.12, -0.05, 0.10) == "MODEL-REPLICATES"
      and p4c.word_ladder(-0.12, -0.05, 0.11) == "MODEL-PARTIAL"
      and p4c.word_ladder(-0.05, 0.01, 0.03) == "MODEL-DOES-NOT-REPLICATE"
      and p4c.word_ladder(0.01, 0.05, 0.03) == "MODEL-DOES-NOT-REPLICATE",
      "targets: CI below 0 and p <= 0.10 -> MODEL-REPLICATES (0.10 "
      "exactly meets); CI below 0 but p > 0.10 -> MODEL-PARTIAL; CI "
      "including 0 or above 0 -> MODEL-DOES-NOT-REPLICATE")


# ==========================================================================
def main():
    banner("A2 -- GATES FOR scripts/lib/phase4_common.py (script 165)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}   "
          f"N_REF_PRE = {N_REF_PRE}")
    print("RESAMPLING UNIT in this script: POSITION CLUSTERS (the anchor "
          "statistic is inside one background).  No background-level "
          "resampling here.")
    print("DECISION RULE (pre-registered): any A2-G1/A2-G2/A2-G3 sub-gate "
          "FAIL -> phase4_common is not trusted for M, U, G, N, L; exit 3.  "
          "Thresholds are never loosened; N is never raised.")
    print("NO torch / esm / thermompnn is imported here (rule 1).")
    if N_BOOT != 10000:
        print("*** SMOKE RUN: N_BOOT != 10000 -- the Phase 1 CI sub-gate "
              "and A2-G1's 40/40 decision are SKIPPED; A2 cannot be called "
              "PASS on this run ***")

    gate_a2_g1()
    gate_a2_g2()
    gate_a2_g3()

    banner("A2 GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    n_skip = sum(1 for _, ok, d in gates if not ok and "SKIPPED" in d)
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    smoke = N_BOOT != 10000
    print(f"\n  {len(gates) - n_fail}/{len(gates)} checks PASS, "
          f"{n_fail} FAIL ({n_skip} of the FAILs are smoke SKIPS).")
    print("\nLIMITATIONS (printed, per AGENTS 6): A2-G2 REPRODUCES cached "
          "Phase 1/2 numbers through the new library -- it validates the "
          "library code (reproduction is not replication), it is not "
          "independent evidence for any claim, and it produces no new "
          "inference.  A2-G3's toys fix the arithmetic, not the biology.  "
          "Every bootstrap exercised here resamples POSITION CLUSTERS; the "
          "corrected routine is phase2_diag4's, imported unmodified; script "
          "144's routine is never used.  A smoke run (N_BOOT != 10000) "
          "cannot PASS A2.")
    if n_fail:
        if smoke and n_fail == n_skip:
            print("\nSMOKE RESULT: all executed sub-gates PASS; the only "
                  "FAIL is the intentional CI SKIP.  A2 is decided on the "
                  "N_BOOT=10000 run.")
            print(f"Elapsed {time.time() - t0:.1f}s")
            sys.exit(0)
        print("\nGATE FAIL -- A2 stops here.  phase4_common is not trusted "
              "for Modules M, U, G, N, L.  Do not raise N, do not adjust a "
              "threshold, do not edit anything.")
        print(f"Elapsed {time.time() - t0:.1f}s")
        sys.exit(3)
    print("\nGATE PASS -- A2-G1, A2-G2 and A2-G3 all pass; "
          "phase4_common is trusted for the Phase 4 analyses per Task A2's "
          "decision rule.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
