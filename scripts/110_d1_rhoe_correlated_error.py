"""
Script 110 (task D1, Group D) -- solve for the error correlation rho_E
via the correlated-error formula (replaces the -191 headline).
PRE-REGISTERED: this docstring was written before any run of this
script; every formula, gate, variant, and reporting rule below was
fixed before any number produced here was seen.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group D, task D1 (D1a-D1d).
      The task doc supplies the formula EXACTLY; per the session rules it
      is used verbatim -- no remembered or substituted variant.

THE FORMULA (verbatim from the task doc; do not alter):
      reliability(D) = [Num_Lord + 2*rho_E*sqrt((1-r_XX)(1-r_YY)*Var(X)*Var(Y))] / Var(D)
      where:
        Num_Lord = r_XX*Var(X) + r_YY*Var(Y) - 2*r_XY*sqrt(Var(X)*Var(Y))
        Var(D)   = Var(X) + Var(Y) - 2*r_XY*sqrt(Var(X)*Var(Y))   [measured directly from D = Y-X data]
      solved for rho_E:
        rho_E = [observed_reliability * Var(D) - Num_Lord]
                / [2*sqrt((1-r_XX)(1-r_YY)*Var(X)*Var(Y))]

INPUTS (D1a): the five quantities from the prior session's D1 entry
(script 105 / REVIEW_RESPONSE_LOG [D1], construction R = rank scale,
the primary), RE-DERIVED here from the five ESM-1v checkpoint CSVs and
gated against the recorded values:
      r_XX = 0.8826369680851056   (median of 10 pairwise Spearman on X)
      r_YY = 0.8821503142468713   (median of 10 pairwise Spearman on Y)
      r_XY = 0.9993872509298699   (median of the 5 within-checkpoint Spearmans)
      Var(X) = 9642753.999990705  (mean over checkpoints, ddof=0, average RANKS)
      Var(Y) = 9642753.999981407  (same, Y ranks)
      observed_reliability(D) = 0.08436481140085886
        (the real, re-derived cross-checkpoint delta agreement; printed
        as 0.084365 in the task text; its CI [+0.052159, +0.122589] is
        quoted from T5a/T4a, not recomputed here)
Data build is byte-identical to script 105's: base =
task32_analysis_table.csv dropna(own_e_b, GI_folinate_independent,
delta_esm) -> 10,757 rows / 654 positions; each member CSV left-merged
1:1 on (position, mut_aa), 0 unmatched, wt_aa labels identical.

VAR(D) -- the task's bracket says "[measured directly from D = Y-X
data]". On the mandated rank scale that is mean over checkpoints of
var(rank(Y_i) - rank(X_i), ddof=0) (recorded in script 105's output as
12145.400177). PRE-REGISTERED VARIANTS, BOTH reported, no selection:
  * PRIMARY: Var(D) measured directly (the bracket's literal reading).
  * SENSITIVITY: Var(D) via the identity from the five inputs
    (= 11817.177093967795 in script 105's output; the identity is exact
    per checkpoint, ~2.7% off on the aggregate medians/means -- printed
    as the aggregate residual, per script 105's informational line).

GATES (failure -> print exact mismatch, sys.exit(1); no retries, no
tolerance changes):
  G0 inputs exist (task32 CSV + 5 member CSVs).
  G1 base == 10,757 rows / 654 positions; every member joins 1:1, 0
     unmatched, wt_aa identical (script 89 R4 / script 105 discipline).
  G2 member integrity: max|delta - (av_logodds - wt_logodds)| < 1e-9
     (pins D = Y - X against the files themselves).
  G3 the five inputs reproduce the recorded values (rtol 1e-9; r_XX
     additionally round(...,6) == 0.882637 per script 105's task-
     mandated gate). Reproduction here is a unit test of implementation
     consistency, NOT independent evidence for anything (AGENTS sec 6).
  G4 observed_reliability reproduces round(...,6) == 0.084365 and the
     recorded full precision (rtol 1e-9).
  G5 Var(D)_measured reproduces 12145.400177 (rtol 1e-6; recorded to
     6 dp).
  G6 (D1b identity gate): plugging the solved rho_E back into the
     forward formula must reproduce the observed reliability with
     RELATIVE error < 1e-12 ("numerical precision"). *** This is an
     ALGEBRAIC IDENTITY, NOT independent validation: the forward
     formula is the exact rearrangement used to solve for rho_E, so
     this check confirms only that the arithmetic was implemented
     consistently with itself. It says nothing about whether the
     correlated-error model is true. This sentence is printed in the
     output itself, as the task doc intends. ***

D1c BOOTSTRAP (project-standard position-cluster): resample the 654
positions with replacement (default_rng seed 0 fixed, N_BOOT from env,
default 10000; smoke 300 first), concatenate the drawn positions' rows
(duplicates included), and RECOMPUTE ALL FIVE INPUTS fresh inside every
draw (re-derivation null, ranks recomputed per draw), then rho_E.
PRE-REGISTERED two variants, BOTH reported, no selection:
  * PRIMARY (literal reading of "recompute all five inputs and rho_E
    fresh"): observed_reliability held at the recorded point value
    0.08436481140085886; only the five inputs are re-derived per draw.
  * SECONDARY (full-data uncertainty): observed_reliability ALSO
    re-derived per draw (median of the 10 pairwise delta Speirmans on
    the resampled rows), since it is itself data-derived.
  Var(D) is re-measured fresh per draw in BOTH variants (primary
  construction above). The identity-Var(D) sensitivity is a point-level
  report only and is NOT part of the bootstrap (pre-registered here;
  its gap is a ~2.7% aggregate-input residual, deterministic given the
  inputs -- excluded to keep the draw meaning single-valued).
  Report: n draws, nan/inf counts, percentiles [2.5, 25, 50, 75, 97.5]
  of finite draws, min, max, fraction in [0,1], fraction > 1. NO
  clipping, NO winsorization -- if draws land outside [0,1] they are
  reported exactly as computed (same discipline as the -191 record).

D1d: one quote-ready sentence built from the PRIMARY point value and
the PRIMARY bootstrap interval: what fraction of each checkpoint's
idiosyncratic deviation is SHARED between the WT and A222V backgrounds
and what fraction is not, under the equal-loading common-factor reading
of rho_E (rho_E = Var(common error) / Var(total error); stated in the
printed sentence's caveat). The -191 forward prediction stays in the
record as the labeled illustration of why the naive independent-error
formula fails (prior session: script 105 / REVIEW_RESPONSE_LOG
[D1]-[D2], pred_R = -190.9323334249339, bootstrap [p2.5=-301.758,
p97.5=-130.314], 10000/10000 draws negative) -- never as a headline.

LIMITATIONS (printed with the output, AGENTS sec 6):
  1. Reproducing the inputs validates the code, not the claim
     (reproduction is not replication).
  2. The G6 gate is an algebraic identity by construction (stated).
  3. rho_E absorbs every violation of the model's assumptions -- shared
     checkpoint construction, any rank-scale artifact, any non-
     stationarity across checkpoints -- not only "true" shared noise;
     the sentence is quotable as a model-conditional quantity.
  4. Rank scale (construction R) throughout, as the task's five inputs
     are; the raw-scale (W) construction is not re-solved here because
     the task specifies these five inputs (disclosed).
  5. observed_reliability's own wide CI [+0.052159, +0.122589] enters
     the SECONDARY variant only; the PRIMARY holds it fixed by the
     task's literal wording.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/110_d1_rhoe_correlated_error.py   # smoke
  N_BOOT=10000 venv/bin/python3 scripts/110_d1_rhoe_correlated_error.py   # full
"""

import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.stats import _spearman  # noqa: E402  (same fn as script 105)

PROC = ROOT / "data" / "processed"
T32_PATH = PROC / "task32_analysis_table.csv"
MEMBER_PATHS = {k: PROC / f"task_AC4_esm1v_member{k}_scores.csv"
                for k in range(1, 6)}
OUT = PROC / "task110_rhoe_correlated_error.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0  # fixed, as script 105
T0 = time.time()

# recorded values (construction R) -- the gates
REC = dict(rxx=0.8826369680851056, ryy=0.8821503142468713,
           rxy=0.9993872509298699, vx=9642753.999990705,
           vy=9642753.999981407, obs=0.08436481140085886,
           vard_meas=12145.400177)
RTOL = 1e-9
K_RXX_TARGET = 0.882637
K_OBS_TARGET = 0.084365
K_IDENTITY_REL_TOL = 1e-12  # "numerical precision", fixed pre-run

IDENTITY_CAVEAT = (
    "D1b GATE CAVEAT (stated exactly as the task intends): this "
    "reproduction is an ALGEBRAIC IDENTITY -- the forward formula is "
    "the exact rearrangement used to solve for rho_E -- so agreement "
    "to 1e-12 verifies only that the arithmetic is internally "
    "consistent with itself. It is NOT independent validation of the "
    "correlated-error model or of any claim built on it."
)


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def solve_rho_e(rxx, ryy, rxy, vx, vy, obs, vd):
    """The task's exact inverse formula."""
    cross = rxy * math.sqrt(vx * vy)
    num_lord = rxx * vx + ryy * vy - 2.0 * cross
    denom = 2.0 * math.sqrt((1.0 - rxx) * (1.0 - ryy) * vx * vy)
    rho = (obs * vd - num_lord) / denom
    return rho, num_lord, denom


def forward_rel(rxx, ryy, rxy, vx, vy, rho, vd):
    """The task's exact forward formula."""
    cross = rxy * math.sqrt(vx * vy)
    num_lord = rxx * vx + ryy * vy - 2.0 * cross
    add = 2.0 * rho * math.sqrt((1.0 - rxx) * (1.0 - ryy) * vx * vy)
    return (num_lord + add) / vd


def summarize(a, label):
    a = np.asarray(a, dtype=float)
    fin = np.isfinite(a)
    f = a[fin]
    print(f"  [{label}] n_draws={len(a)} finite={int(fin.sum())} "
          f"nan={int(np.isnan(a).sum())} inf={int(np.isinf(a).sum())}")
    if len(f):
        p2_5, p25, p50, p75, p97_5 = np.percentile(
            f, [2.5, 25, 50, 75, 97.5])
        print(f"    percentiles of finite draws: p2.5={p2_5:.10g} "
              f"p25={p25:.10g} p50={p50:.10g} p75={p75:.10g} "
              f"p97.5={p97_5:.10g}")
        print(f"    min={f.min():.10g} max={f.max():.10g} | fraction "
              f"in [0,1]={float(((f >= 0) & (f <= 1)).mean()):.4f} | "
              f"fraction >1={float((f > 1).mean()):.4f}")
        return dict(p2_5=p2_5, p25=p25, p50=p50, p75=p75,
                    p97_5=p97_5, min=float(f.min()), max=float(f.max()))
    return {}


def five_inputs(X, Y, idx):
    """Recompute the five rank-scale inputs on row indices idx
    (structure identical to script 105's inputs_on, construction R)."""
    xd = X[:, idx]
    yd = Y[:, idx]
    rx = rankdata(xd, axis=1)
    ry = rankdata(yd, axis=1)
    C = np.corrcoef(np.vstack([rx, ry]))
    iu = np.triu_indices(5, 1)
    rxx = float(np.median(C[:5, :5][iu]))
    ryy = float(np.median(C[5:, 5:][iu]))
    rxy = float(np.median(np.diag(C[:5, 5:])))
    vx = float(np.mean(np.var(rx, axis=1, ddof=0)))
    vy = float(np.mean(np.var(ry, axis=1, ddof=0)))
    vd = float(np.mean(np.var(ry - rx, axis=1, ddof=0)))
    return rxx, ryy, rxy, vx, vy, vd


if __name__ == "__main__":
    banner(f"D1 -- rho_E via the correlated-error formula (scripts/110)"
           f"  N_BOOT={N_BOOT} seed={SEED}")

    # ---- G0 ---------------------------------------------------------
    for p in [T32_PATH, *MEMBER_PATHS.values()]:
        if not p.exists():
            gfail(f"G0 FAIL: {p} missing -- input not found. Stop.")
    print("  G0 PASS: task32_analysis_table.csv + all 5 member CSVs "
          "present")

    # ---- G2 (member integrity) --------------------------------------
    memb = {}
    for k, p in MEMBER_PATHS.items():
        d = pd.read_csv(p)
        gap = float(np.abs(d["delta"] - (d["av_logodds"]
                                         - d["wt_logodds"])).max())
        if gap >= 1e-9:
            gfail(f"G2 FAIL: member {k} delta != av - wt "
                  f"(max|diff| = {gap:.3e}). Stop.")
        memb[k] = d
    print(f"  G2 PASS: all 5 members: delta == av_logodds - "
          f"wt_logodds on all {len(d)} rows (max|diff| < 1e-9) -- "
          f"D = Y - X sign convention pinned against the files")

    # ---- G1 base + join --------------------------------------------
    t32 = pd.read_csv(T32_PATH)
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G1 FAIL: base n={len(base)} "
              f"pos={base['position'].nunique()}, expected 10757/654")
    joined = {}
    for k, md in memb.items():
        j = base.merge(md[["position", "wt_aa", "mut_aa", "wt_logodds",
                           "av_logodds", "delta"]],
                       on=["position", "mut_aa"], how="left",
                       validate="1:1")
        miss = int(j["wt_logodds"].isna().sum())
        if miss:
            gfail(f"G1 FAIL: member {k} left {miss} base rows "
                  f"unmatched -- exit (R4). Stop.")
        if not (j["wt_aa_x"] == j["wt_aa_y"]).all():
            gfail(f"G1 FAIL: member {k} wt_aa label mismatch. Stop.")
        joined[k] = j
    ks = sorted(joined)
    X = np.vstack([joined[k]["wt_logodds"].to_numpy() for k in ks])
    Y = np.vstack([joined[k]["av_logodds"].to_numpy() for k in ks])
    Dl = np.vstack([joined[k]["delta"].to_numpy() for k in ks])
    pos = joined[1]["position"].to_numpy()
    n_rows = X.shape[1]
    uniq_pos = np.unique(pos)
    print(f"  G1 PASS: base {len(base)} rows / {len(uniq_pos)} "
          f"positions; all 5 members joined 1:1, 0 unmatched, wt_aa "
          f"match ({n_rows} rows)")

    # ---- G3 the five inputs, point level ----------------------------
    banner("D1a -- THE FIVE INPUTS, re-derived and gated", "-")
    rxx, ryy, rxy, vx, vy, vd_meas = five_inputs(
        X, Y, np.arange(n_rows))
    # cross-check r_XX/r_YY/r_XY via script 105's _spearman route
    iu = np.triu_indices(5, 1)
    pair_xx = [float(_spearman(X[i], X[j])) for i, j in zip(*iu)]
    pair_yy = [float(_spearman(Y[i], Y[j])) for i, j in zip(*iu)]
    pair_d = [float(_spearman(Dl[i], Dl[j])) for i, j in zip(*iu)]
    rxx_s, ryy_s = float(np.median(pair_xx)), float(np.median(pair_yy))
    rxy_s = float(np.median([float(_spearman(X[i], Y[i]))
                             for i in range(5)]))
    obs = float(np.median(pair_d))
    print(f"  r_XX (corrcoef-of-ranks route) = {rxx!r}")
    print(f"  r_XX (_spearman route, as script 105) = {rxx_s!r}  "
          f"(median of 10 pairwise; min={min(pair_xx):.6f} "
          f"max={max(pair_xx):.6f})")
    print(f"  r_YY = {ryy!r}  (_spearman route {ryy_s!r}; "
          f"min={min(pair_yy):.6f} max={max(pair_yy):.6f})")
    print(f"  r_XY = {rxy!r}  (_spearman route {rxy_s!r}; median of "
          f"the 5 within-checkpoint values)")
    print(f"  Var(X) = {vx!r}   Var(Y) = {vy!r}   (mean rank "
          f"variances, ddof=0)")
    print(f"  Var(D) measured directly = {vd_meas!r}  (mean over "
          f"checkpoints of var(rank(Y)-rank(X)))")
    print(f"  observed reliability(D) = {obs!r}  "
          f"(6 dp target {K_OBS_TARGET}; CI [+0.052159, +0.122589] "
          f"QUOTED from T5a/T4a, not recomputed)")
    if round(rxx_s, 6) != K_RXX_TARGET:
        gfail(f"G3 FAIL: r_XX {rxx_s!r} != {K_RXX_TARGET} (6 dp)")
    for name, got in [("rxx", rxx_s), ("ryy", ryy_s), ("rxy", rxy_s),
                      ("vx", vx), ("vy", vy)]:
        if not math.isclose(got, REC[name], rel_tol=RTOL):
            gfail(f"G3 FAIL: {name} = {got!r} does not reproduce "
                  f"{REC[name]!r} (rtol {RTOL})")
    if round(obs, 6) != K_OBS_TARGET:
        gfail(f"G4 FAIL: observed {obs!r} != {K_OBS_TARGET} (6 dp)")
    if not math.isclose(obs, REC["obs"], rel_tol=RTOL):
        gfail(f"G4 FAIL: observed {obs!r} != {REC['obs']!r}")
    if not math.isclose(vd_meas, REC["vard_meas"], rel_tol=1e-6):
        gfail(f"G5 FAIL: Var(D)_measured {vd_meas!r} != "
              f"{REC['vard_meas']!r} (rtol 1e-6)")
    print(f"  G3 PASS: all five inputs reproduce the recorded values "
          f"(rtol {RTOL}); G4 PASS: observed reliability reproduces; "
          f"G5 PASS: Var(D)_measured reproduces")
    print("    (reproduction is a unit test of implementation "
          "consistency -- NOT independent evidence, AGENTS sec 6)")

    # ---- D1a: solve -------------------------------------------------
    cross = rxy * math.sqrt(vx * vy)
    vd_ident = vx + vy - 2.0 * cross
    rho_m, num_lord, denom = solve_rho_e(rxx, ryy, rxy, vx, vy, obs,
                                         vd_meas)
    rho_i, _, _ = solve_rho_e(rxx, ryy, rxy, vx, vy, obs, vd_ident)
    banner("D1a -- rho_E SOLVED (exact task formula)", "-")
    print(f"  inputs: r_XX={rxx!r} r_YY={ryy!r} r_XY={rxy!r}")
    print(f"          VarX={vx!r} VarY={vy!r}")
    print(f"  Num_Lord            = {num_lord!r}")
    print(f"  Var(D) measured     = {vd_meas!r}  (PRIMARY)")
    print(f"  Var(D) identity     = {vd_ident!r}  (SENSITIVITY; "
          f"aggregate residual vs measured = "
          f"{abs(vd_meas - vd_ident) / vd_meas:.3e})")
    print(f"  denominator 2*sqrt((1-rXX)(1-rYY)VarXVarY) = {denom!r}")
    print(f"  rho_E (PRIMARY, Var(D) measured)     = {rho_m!r}")
    print(f"  rho_E (SENSITIVITY, Var(D) identity) = {rho_i!r}")
    print(f"  observed reliability held for the solve = {obs!r}")

    # ---- D1b: identity gate ----------------------------------------
    fwd_m = forward_rel(rxx, ryy, rxy, vx, vy, rho_m, vd_meas)
    fwd_i = forward_rel(rxx, ryy, rxy, vx, vy, rho_i, vd_ident)
    rel_m = abs(fwd_m - obs) / abs(obs)
    rel_i = abs(fwd_i - obs) / abs(obs)
    banner("D1b -- IDENTITY GATE", "-")
    print(f"  forward(rho_E measured-VarD) = {fwd_m!r}  "
          f"rel err = {rel_m:.3e}")
    print(f"  forward(rho_E identity-VarD) = {fwd_i!r}  "
          f"rel err = {rel_i:.3e}")
    if rel_m >= K_IDENTITY_REL_TOL or rel_i >= K_IDENTITY_REL_TOL:
        gfail(f"G6 FAIL: identity rel err {rel_m:.3e} / {rel_i:.3e} "
              f">= {K_IDENTITY_REL_TOL}")
    print(f"  G6 PASS: both reproduce {obs!r} to rel < "
          f"{K_IDENTITY_REL_TOL}")
    print(f"  *** {IDENTITY_CAVEAT} ***")

    # ---- D1c: bootstrap --------------------------------------------
    banner(f"D1c -- POSITION-CLUSTER BOOTSTRAP (654 positions, "
           f"N_BOOT={N_BOOT}, seed {SEED})", "-")
    rng = np.random.default_rng(SEED)
    # per-position row index lists (cluster bootstrap, duplicates kept)
    pos_codes, _ = pd.factorize(pos, sort=True)
    k = len(uniq_pos)
    clusters = [np.flatnonzero(pos_codes == p) for p in range(k)]
    all_idx = np.concatenate(clusters)
    rho_primary = np.empty(N_BOOT)
    rho_secondary = np.empty(N_BOOT)
    n_nan = 0
    for b in range(N_BOOT):
        draw = rng.integers(0, k, k)
        idx = np.concatenate([clusters[d] for d in draw])
        rxx_b, ryy_b, rxy_b, vx_b, vy_b, vd_b = five_inputs(X, Y, idx)
        rho_primary[b] = solve_rho_e(rxx_b, ryy_b, rxy_b, vx_b, vy_b,
                                     obs, vd_b)[0]
        # secondary: observed re-derived fresh on the same rows
        obs_b = float(np.median(
            [_spearman(Dl[i][idx], Dl[j][idx]) for i, j in zip(*iu)]))
        rho_secondary[b] = solve_rho_e(rxx_b, ryy_b, rxy_b, vx_b, vy_b,
                                       obs_b, vd_b)[0]
        if not (np.isfinite(rho_primary[b])
                and np.isfinite(rho_secondary[b])):
            n_nan += 1
    print(f"  non-finite draws (either variant): {n_nan}")
    s1 = summarize(rho_primary, "PRIMARY (obs held at recorded point)")
    s2 = summarize(rho_secondary,
                   "SECONDARY (obs re-derived fresh per draw)")

    # ---- D1d: quote-ready sentence ---------------------------------
    banner("D1d -- QUOTE-READY SENTENCE", "-")
    a = rho_primary[np.isfinite(rho_primary)]
    p2_5, p97_5 = np.percentile(a, [2.5, 97.5])
    pt = rho_m
    print(f"  \"Across the five ESM-1v checkpoints, the WT and A222V "
          f"backgrounds share {pt * 100:.1f}% "
          f"[95% bootstrap {p2_5 * 100:.1f}-{p97_5 * 100:.1f}%] of "
          f"each checkpoint's idiosyncratic (non-reproducible) "
          f"deviation, leaving only {(1 - pt) * 100:.1f}% "
          f"[{(1 - p97_5) * 100:.1f}-{(1 - p2_5) * 100:.1f}%] "
          f"arm-specific -- a checkpoint essentially errs in "
          f"lockstep across the two backgrounds.\"")
    print("  (Caveat carried with the sentence: 'shared fraction' is "
          "the equal-loading common-factor reading of rho_E = "
          "Var(common error)/Var(total error); rho_E absorbs every "
          "violation of the model's assumptions, not only true shared "
          "noise.)")
    print("  LABEL ILLUSTRATION, retained not headline: the naive "
          "independent-error (rho_E = 0) forward formula returns "
          "pred_R = -190.9323334249339, bootstrap [p2.5=-301.758, "
          "p97.5=-130.314], 10000/10000 draws negative (script 105 / "
          "REVIEW_RESPONSE_LOG [D1]-[D2]) -- shown to explain WHY the "
          "independent-error formula fails; the correlated-error "
          "rho_E above is the primary number for this section "
          "going forward.")

    # ---- write CSV --------------------------------------------------
    rows = [
        ("input", "r_XX", rxx, "rank scale, median of 10 pairwise"),
        ("input", "r_YY", ryy, "rank scale, median of 10 pairwise"),
        ("input", "r_XY", rxy, "median of 5 within-checkpoint"),
        ("input", "VarX", vx, "mean rank variance, ddof=0"),
        ("input", "VarY", vy, "mean rank variance, ddof=0"),
        ("input", "observed_rel_D", obs, "re-derived; CI quoted T5a/T4a"),
        ("input", "VarD_measured", vd_meas, "PRIMARY Var(D)"),
        ("input", "VarD_identity", vd_ident, "SENSITIVITY Var(D)"),
        ("derived", "Num_Lord", num_lord, "task formula verbatim"),
        ("derived", "denominator", denom,
         "2*sqrt((1-rXX)(1-rYY)VarXVarY)"),
        ("point", "rho_E_primary", rho_m, "Var(D) measured"),
        ("point", "rho_E_sensitivity", rho_i, "Var(D) identity"),
        ("gate", "forward_from_rho_E_primary", fwd_m,
         "algebraic identity, not validation"),
        ("gate", "rel_err_primary", rel_m, "must be < 1e-12"),
        ("boot", "primary_p2_5", s1.get("p2_5", float("nan")), ""),
        ("boot", "primary_p25", s1.get("p25", float("nan")), ""),
        ("boot", "primary_p50", s1.get("p50", float("nan")), ""),
        ("boot", "primary_p75", s1.get("p75", float("nan")), ""),
        ("boot", "primary_p97_5", s1.get("p97_5", float("nan")), ""),
        ("boot", "primary_min", s1.get("min", float("nan")), ""),
        ("boot", "primary_max", s1.get("max", float("nan")), ""),
        ("boot", "secondary_p2_5", s2.get("p2_5", float("nan")), ""),
        ("boot", "secondary_p50", s2.get("p50", float("nan")), ""),
        ("boot", "secondary_p97_5", s2.get("p97_5", float("nan")), ""),
        ("label", "pred_R_independent_error", -190.9323334249339,
         "prior session, illustration only"),
    ]
    pd.DataFrame(rows, columns=["section", "key", "value", "note"]
                 ).to_csv(OUT, index=False)
    print(f"\nLIMITATIONS (AGENTS 6):")
    print("  1. Reproduction of inputs = unit test, not replication.")
    print("  2. D1b gate is an algebraic identity by construction.")
    print("  3. rho_E absorbs every model-assumption violation, not "
          "only true shared noise.")
    print("  4. Rank scale throughout (the task's five inputs are "
          "rank-scale); raw-scale variant not re-solved.")
    print("  5. PRIMARY holds observed reliability fixed (task's "
          "literal wording); SECONDARY re-derives it fresh -- both "
          "reported, neither selected after seeing results.")
    print(f"\nWrote {OUT}")
    print(f"SCRIPT 110 DONE ({time.time() - T0:.1f}s) "
          f"rho_E={rho_m!r} primary CI [{p2_5:.6g}, {p97_5:.6g}]")
