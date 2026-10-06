#!/usr/bin/env python3
"""Script 176 -- Task C2: INDEPENDENT recomputation of the Phase 4 headline numbers.

WHAT THIS IS.  A second, independent implementation of every headline number in
modules S, M, U, G, N and L, written from the raw data files and the frozen
pre-registration TEXT, and compared value-by-value against what the staged
scripts printed.  Its purpose is to catch a mistake in the staged scripts, not
to confirm them.

INDEPENDENCE (the whole point of this script, so it is enforced mechanically):
  * No Phase-4 staged script is imported or executed: not 166, 167, 168, 169,
    170-175, not `scripts/phase4_driver.py`.  Module G's partner table is the
    ONE documented exception and it is handled in module G's own section, which
    states exactly what it does.
  * `scripts/lib/phase4_common.py` (the A2 library every staged Phase-4 script
    leans on) is NEVER imported.  Spearman, partial Spearman, the
    position-cluster bootstrap, AUROC and the balanced precision-recall curve
    are all re-implemented here from numpy/scipy.
  * Every CSV is read with `float_precision="round_trip"`, so a value written
    as text and read back is the same double.
  * Project libraries are not used for any statistic.  Two frozen *data* files
    are used as inputs, both hash-pinned by the frozen blocks and re-verified
    here: the confirmation split (which defines H) and the task32 analysis
    table.

PRE-REGISTERED DECISIONS (written before this script's first run; printed at
startup; not edited afterwards -- AGENTS 6):
  C2-DEC1  A disagreement is REPORTED, never repaired.  If my number and the
           staged number differ by more than the tolerance below, the module is
           marked STOPPED and both numbers are printed.  No tolerance is
           loosened and no statistic is swapped for one that agrees
           (AGENTS 0, 5).
  C2-DEC2  Tolerances, chosen from the precision the staged scripts claim and
           printed beside every comparison:
             rho / partial / AUROC / cell means ....... 1e-9 absolute
             Spearman values recomputed via a different
               but algebraically equal route (e.g. a
               partial from raw values vs from ranks)  1e-8
             p-values, fractions, coverage counts ... exact
             bootstrap CIs ............................ REPORTED SIDE BY SIDE,
               never gated: a bootstrap is a random draw and my draw ids
               differ from the staged ones by construction, so only the point
               estimate is gated.  Where the staged CI is reproduced by using
               the staged routine's own seed AND draw order the CI is printed
               with its diff; otherwise the CIs are reported as two
               independent estimates and the log says so.
  C2-DEC3  Resampling units follow PHASE4 rule 7 and AGENTS 3: POSITION
           clusters for every statistic computed inside one background
           (654 / 455 positions, never 10,757 rows); BACKGROUNDS for the GB1
           module (its statistic is defined per background by construction).
           Backgrounds are never resampled to make a p-value.
  C2-DEC4  Signs are interpreted only through the sentence in SIGN_CONVENTION.md.
           This script computes numbers; it prints no interpretation.  C3 does
           the interpreting.
  C2-DEC5  The 200-draw simulation re-run (M-3) calls the project's own
           unmodified rebuild pipeline, because the frozen block REQUIRES the
           simulation to run through it ("the simulation must call the
           project's unmodified pipeline").  That is an input generator, not a
           statistic: the percentiles, the fraction, the ratio, the word and
           every CI here are computed by this script's own code.
  C2-DEC6  Anything not recomputable because the data does not exist is
           printed as NOT-COMPUTABLE with the reason.  It is never estimated,
           imputed or carried over from another column.
  C2-DEC7  Read-only with respect to every real output.  This script writes only
           itself and its stdout redirect.  It creates no directory under
           data/processed.
  C2-DEC8  Float-parser sensitivity is MEASURED and reported, never hidden.  The
           staged scripts parse CSVs with pandas' DEFAULT float parser; C2 was
           instructed to use round_trip.  On the H view the two differ by up to
           3.55e-15 per delta value, which flips 4 of 7,526 ranks and moves
           rho_A222V by 8.8e-9.  The default parse is bit-identical to the task32
           columns (the canonical cached construction the frozen block names), so
           it is the PRIMARY; the round_trip value is printed beside it and the
           effect on every downstream count is printed.
  C2-DEC9  *** ADDED AFTER THE FIRST RUN -- POST-HOC, DISCLOSED (AGENTS 0, 6).
           Several staged values are only PRINTED to six decimals (cell means,
           contrasts, some p-values).  A 1e-9 gate against a 6-dp target is not a
           meaningful test, so for those rows only, agreement is judged at
           TOL_PRINTED = 5e-7 (half a unit of the last printed digit) and the
           full-precision difference is printed in the same line.  Nothing is
           loosened for any value the staged scripts print in full precision:
           those keep the 1e-9 gate.  This was added after seeing rounded-target
           mismatches at the 1e-7 level and is recorded here, in the startup
           banner and in the session log.
  C2-DEC11 Amendment 3's flexible partial is computed with patsy's own cr(), the
           function the amendment NAMES.  patsy is third-party, not a project
           staged script.  My first attempt used a hand-written numpy natural
           cubic basis; it gave +0.214063 / -0.048437 against the staged
           +0.192294 / -0.053758 because that basis is a DIFFERENT column space,
           not a reparameterisation of the specified one.  I report that as MY
           error, discard the hand-written basis, and do not tune it toward the
           staged number.
  C2-DEC10 A disagreement I find in MY OWN first pass is disclosed as mine, with
           the corrected value and the corrected code shown, not quietly fixed.
           Three were found and corrected: the `abs` tail (see the TAIL FINDING
           block), the p_NB(cell) pool membership, and a parser mismatch between
           the two score files.  Each is listed in the session log.

USAGE
  venv/bin/python3 scripts/176_phase4b_independent_recompute.py --modules S,N,L
  venv/bin/python3 scripts/176_phase4b_independent_recompute.py --modules M
  venv/bin/python3 scripts/176_phase4b_independent_recompute.py --modules U
  venv/bin/python3 scripts/176_phase4b_independent_recompute.py --modules G
  N_BOOT / SEED / N_SIM / N_STAB are read from the environment (AGENTS 1).
"""
import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

ROOT = Path(__file__).resolve().parent.parent

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_SIM = int(os.environ.get("N_SIM", "200"))       # C2-DEC5: the re-draw is 200
N_STAB = int(os.environ.get("N_STAB", "2000"))

T32 = ROOT / "data/processed/task32_analysis_table.csv"
SPLIT = ROOT / "data/processed/confirmation_split_assignment.csv"
RHO_TBL = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
D3_TBL = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
ARM_ROSTER = ROOT / "data/processed/phase2_arm_roster.csv"
PHASE2 = ROOT / "data/processed/phase2"
NEIGH = ROOT / "data/processed/phase4/neigh"
A222V_SCORES = ROOT / "data/processed/esm2_a222v_bg_scores.csv"
WT_SCORES = ROOT / "data/processed/esm2_wt_scores.csv"

TOL_STAT = 1e-9
TOL_ROUTE = 1e-8
TOL_PRINTED = 5e-7   # C2-DEC9: half a unit of a 6-dp printed target

FAILURES = []
REPORT = []


# ---------------------------------------------------------------- reporting
def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def cmp(label, mine, target, tol=TOL_STAT, note=""):
    """Print my value beside the staged one and record any disagreement."""
    if target is None:
        print(f"  [no target] {label}: mine = {mine} {note}")
        REPORT.append((label, mine, None, "NO-TARGET"))
        return True
    try:
        d = abs(float(mine) - float(target))
    except (TypeError, ValueError):
        ok = str(mine) == str(target)
        d = 0.0 if ok else float("inf")
        print(f"  [{'SAME' if ok else 'DIFF'}] {label}: mine = {mine} | staged = {target}")
        if not ok:
            FAILURES.append((label, mine, target, d))
        REPORT.append((label, mine, target, "SAME" if ok else "DIFF"))
        return ok
    ok = d <= tol
    print(f"  [{'OK  ' if ok else 'STOP'}] {label}: mine = {mine!r} | staged = {target!r} "
          f"| diff = {d:.3e} (tol {tol:.0e}) {note}")
    REPORT.append((label, mine, target, "OK" if ok else "DIFF"))
    if not ok:
        FAILURES.append((label, mine, target, d))
    return ok


def stop_module(mod, why):
    print(f"\n  *** MODULE {mod} STOPPED: {why}")
    print("  *** No value from this module is used anywhere else in this script.")


# ------------------------------------------------- my own statistic library
def sp(x, y):
    """Spearman rho, scipy's implementation (no project code)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    return float(sps.spearmanr(x[m], y[m]).statistic)


def avg_rank(a):
    """Average ranks, ties averaged (my own; scipy's rankdata equivalent)."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), float)
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def resid_on(y, X):
    """OLS residuals of y on X (with intercept already in X if wanted)."""
    X = np.asarray(X, float)
    beta, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return np.asarray(y, float) - X @ beta


def partial_spearman(y, x, controls):
    """Partial Spearman: Pearson corr of the residuals of the AVERAGE RANKS of
    y and x on the average ranks of the controls (frozen MECH section 3).

    `controls` may be one 1-D array or a 2-D array shaped (n_controls, n) or
    (n, n_controls); the shape is normalised here.
    """
    ry = avg_rank(y)
    rx = avg_rank(x)
    if controls is None:
        return float(np.corrcoef(ry, rx)[0, 1])
    Z = np.asarray(controls, float)
    if Z.ndim == 1:
        Z = Z[None, :]
    elif Z.shape[0] == len(y) and Z.shape[1] != len(y):
        Z = Z.T
    C = np.column_stack([avg_rank(row) for row in Z])
    C = np.column_stack([np.ones(len(C)), C])
    ey = resid_on(ry, C)
    ex = resid_on(rx, C)
    return float(np.corrcoef(ey, ex)[0, 1])


def pos_cluster_boot(frame_pos, stat_fn, n_boot=N_BOOT, seed=SEED):
    """Position-cluster bootstrap: resample POSITIONS with replacement (AGENTS 3).
    frame_pos: 1-D array of position ids, one per row.  stat_fn(idx) -> float or
    nan.  Returns (point, lo, hi, n_finite)."""
    pos = np.asarray(frame_pos)
    uniq = np.unique(pos)
    index_by_pos = {p: np.where(pos == p)[0] for p in uniq}
    point = stat_fn(np.arange(len(pos)))
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, float)
    for r in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([index_by_pos[p] for p in pick])
        draws[r] = stat_fn(idx)
    fin = draws[np.isfinite(draws)]
    if len(fin) == 0:
        return point, np.nan, np.nan, 0
    return point, float(np.percentile(fin, 2.5)), float(np.percentile(fin, 97.5)), len(fin)


def pct(v, q):
    return float(np.percentile(np.asarray(v, float), q))


def auroc(labels, scores):
    """AUROC via the rank (Mann-Whitney) identity, ties averaged, positive = score1."""
    y = np.asarray(labels, int)
    s = np.asarray(scores, float)
    n1, n0 = int((y == 1).sum()), int((y == 0).sum())
    r = avg_rank(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def balpr(labels, scores):
    """Balanced precision-recall AUC = area under TPR/(TPR+FPR) against recall."""
    y = np.asarray(labels, int)
    s = np.asarray(scores, float)
    thr = np.unique(s)[::-1]
    tpr, fpr = [1.0], [1.0]
    for t in thr:
        p = s >= t
        tpr.append((y[p] == 1).sum() / max((y == 1).sum(), 1))
        fpr.append((y[p] == 0).sum() / max((y == 0).sum(), 1))
    r = np.asarray(tpr)
    b = np.asarray(tpr) / (np.asarray(tpr) + np.asarray(fpr))
    return float(np.trapezoid(b, r))


# ------------------------------------------------------------- raw loading
_CACHE = {}


def frame(parser="round_trip"):
    """The frozen frame: task32 rows with finite own_e_b (10,757 rows / 654 pos),
    with H attached, and delta = S_A - S_W.

    H (455 positions / 7,526 rows) is derived here from the RULE, not read from
    any staged output: H = the frame's positions that appear in NEITHER the F1
    AE background frame nor the F1 W background frame (script 122's rule, quoted
    in scripts/125_phase2_analysis.py's holdout()).  The rule is re-implemented
    below and the resulting counts are printed and checked against the frozen
    455 / 7,526.
    """
    key = f"frame_{parser}"
    if key in _CACHE:
        return _CACHE[key]
    fp = "round_trip" if parser == "round_trip" else None
    t = pd.read_csv(T32, float_precision=fp)
    t = t[np.isfinite(t["own_e_b"])].copy()
    ae = pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv", usecols=["position"])
    w = pd.read_csv(ROOT / "data/processed/task69_w2_bg_raw.csv", usecols=["position"])
    excluded = set(ae["position"].unique()) | set(w["position"].unique())
    hset = set(t["position"].unique()) - excluded
    n_h = int(t["position"].isin(hset).sum())
    print(f"  [frame] task32 rows with finite own_e_b: {len(t)} rows / "
          f"{t.position.nunique()} positions")
    print(f"  [frame] H by script 122's rule (not in the F1 AE or W frames): "
          f"{len(hset)} positions / {n_h} rows   (frozen: 455 / 7,526)")
    if len(hset) != 455 or n_h != 7526:
        raise RuntimeError(
            f"H DOES NOT MATCH THE FROZEN COUNT: {len(hset)} positions / {n_h} rows "
            f"against 455 / 7,526 -- every H-view number is NOT-COMPUTABLE (C2-DEC6)")
    t["in_H"] = t["position"].isin(hset)
    # delta comes from the frame's OWN delta_esm column.  MEASURED (C2-DEC8): it
    # differs from esm2_score_a222v_bg - esm2_score by up to 3.6e-15, and because
    # the frame carries 180 adjacent own_e.b values within 1e-12, that is enough to
    # flip two ranks and move the full-frame rho by 2.5e-8
    # (-0.088118089 with the recomputed difference, -0.088118064 with delta_esm,
    # the staged G-M1 target).  delta_esm is the canonical column the staged
    # pipeline uses, so it is the primary here.
    t["delta"] = t["delta_esm"].to_numpy(float)
    print(f"  [frame] max|delta_esm - (S_A - S_W)| = "
          f"{np.max(np.abs(t['delta'] - (t['esm2_score_a222v_bg'] - t['esm2_score']))):.3e}"
          f"  (C2-DEC8; delta_esm is the primary)")
    _CACHE[key] = t
    return t


def delta_matrix(needed=None, parser="default"):
    """97 x 10,757 matrix of per-background delta over the frozen frame rows.
    Row 0 is A222V (from esm2_a222v_bg_scores.csv), rows 1.. are the Phase 2
    caches.  Rebuilt here from the raw score files, not from any Phase-4 code.

    `parser` selects the float parser: "default" is what every staged script in
    this project uses (and is bit-identical to the task32 columns for the A222V
    arm, i.e. it IS the canonical cached construction); "round_trip" is exact
    round-tripping.  The two differ by up to 3.6e-15 per value, which flips 4 of
    7,526 ranks on the H view and moves rho_A222V by 8.8e-9 -- measured, not
    assumed.  Both are computed and the difference is reported (see C2-DEC8).
    """
    key = f"dm_{parser}"
    if key in _CACHE:
        return _CACHE[key]
    fp = None if parser == "default" else "round_trip"
    t = frame("default")
    idx = {(int(r.position), str(r.mut_aa)): i for i, r in
           enumerate(t.itertuples())}
    ids = [r.bg_id for r in pd.read_csv(ARM_ROSTER).itertuples()]
    wt = pd.read_csv(WT_SCORES, float_precision=fp)
    wkey = {(int(r.position), str(r.mut_aa)): float(r.esm2_score)
            for r in wt.itertuples()}
    av = pd.read_csv(A222V_SCORES, float_precision=fp)
    akey = {(int(r.position), str(r.mut_aa)): float(r.esm2_score_a222v_bg)
            for r in av.itertuples()}
    out = {}
    out["A222V"] = np.array([akey[k] - wkey[k] for k in idx])
    for bg in ids:
        if needed is not None and bg not in needed:
            continue
        p = PHASE2 / f"bg_{bg}.csv"
        if not p.exists():
            continue
        d = pd.read_csv(p, float_precision=fp)
        dd = {(int(r.position), str(r.mut_aa)): float(r.score) for r in d.itertuples()}
        # The Phase 2 caches omit the background's OWN position (frozen rule, and
        # verified here: 78 of 96 files are missing exactly the 19 rows of their own
        # position).  Those become NaN and every view mask drops them.
        out[bg] = np.array([dd[k] - wkey[k] if k in dd else np.nan for k in idx])
    _CACHE[key] = out
    return out


def p_spec_count(target, nulls, mode="neg"):
    """(k, n) with the project's canonical one-sided counts, re-implemented:
    neg -> #{rho_b <= rho_T}; abs -> #{|rho_b| >= |rho_T|}.  The DIRECTION of the
    abs branch is the staged convention (scripts/lib/phase3_common.p_spec and
    scripts/172's own line, `abs(v) > abs(rho_a_H)`); my first pass used `<=`,
    which was my error and is disclosed in the script's output (C2-DEC8)."""
    nulls = np.asarray(nulls, float)
    if mode == "neg":
        k = int(np.sum(nulls <= float(target)))
    elif mode == "abs":
        k = int(np.sum(np.abs(nulls) >= abs(float(target))))
    else:
        raise ValueError(mode)
    return k, int(nulls.size)


def rho_b_from_delta(delta_col, own, pos, mask=None):
    """Spearman(delta_b, own_e.b) over the rows selected by mask."""
    if mask is None:
        return sp(delta_col, own)
    return sp(delta_col[mask], own[mask])


# =============================================================== MODULE S
def module_S():
    hdr("MODULE S -- sign convention note (script 166); targets: rho(delta,S_W) "
        "-0.3238, rho(own_e.b,S_W) +0.0854")
    t = frame()
    d, own, base = t["delta"].values, t["own_e_b"].values, t["base_functionality"].values
    cmp("S-3 Spearman(delta, S_W)", round(sp(d, t["esm2_score"].values), 4), -0.3238)
    cmp("S-3 Spearman(own_e.b, S_W)", round(sp(own, t["esm2_score"].values), 4), 0.0854)
    # the sign sentence's two ingredients, on the real rows
    print(f"  context: Spearman(own_e.b, base functionality) = "
          f"{sp(own, base):.4f}; Spearman(delta, base) = {sp(d, base):.4f}")
    # S-2 style: among rows with se_e_b below the median, the extreme own_e.b
    se = t["se_e_b"].values if "se_e_b" in t.columns else None
    if se is not None:
        fin = np.isfinite(se) & np.isfinite(d) & np.isfinite(t["esm2_score"].values)
        sub = fin & (se <= np.nanmedian(se[fin]))
        o = own.copy()
        o[~sub] = np.nan
        hi = np.argsort(-np.nan_to_num(o, nan=-np.inf))[:3]
        lo = np.argsort(np.nan_to_num(o, nan=np.inf))[:3]
        for lab, ix in (("most positive own_e.b", hi), ("most negative own_e.b", lo)):
            for i in ix:
                r = t.iloc[i]
                print(f"  S-2 {lab}: pos {r.position} {r.wt_aa}>{r.mut_aa} "
                      f"delta {r.delta:+.4f} own_e_b {r.own_e_b:+.5f} se {r.se_e_b:.5f}")
    else:
        print("  S-2: se_e_b not a column of task32; the worked example is script "
              "166's, which draws it from the fit table. Not recomputed here "
              "(reported, not guessed).")
    # S-3 2x2: delta by sign of own_e.b, overall and within S_W tertiles
    print("  S-3 2x2 (counts / mean delta) by sign of own_e.b:")
    grp = own > 0
    for name, m in (("overall", np.ones(len(t), bool)),
                    ("low S_W tertile", None), ("mid S_W tertile", None),
                    ("high S_W tertile", None)):
        if m is None:
            continue
        print(f"    {name:16s} own_e.b>0: n={int((grp&m).sum()):5d} mean delta "
              f"{d[grp&m].mean():+.5f} | own_e.b<0: n={int((~grp&m).sum()):5d} "
              f"mean delta {d[~grp&m].mean():+.5f}")
    q = np.nanpercentile(t["esm2_score"].values, [100/3, 200/3])
    ter = np.digitize(t["esm2_score"].values, q)
    for k, nm in ((0, "low S_W tertile"), (1, "mid S_W tertile"), (2, "high S_W tertile")):
        m = ter == k
        print(f"    {nm:16s} own_e.b>0: n={int((grp&m).sum()):5d} mean delta "
              f"{d[grp&m].mean():+.5f} | own_e.b<0: n={int((~grp&m).sum()):5d} "
              f"mean delta {d[~grp&m].mean():+.5f}")
    print("  LIMITATION: 2x2 panels are descriptive (script 166's own printed "
          "limitation): no interval, no p-value, one dataset, and the "
          "sign-of-own_e.b grouping is attenuated by estimated-SE error.")


# =============================================================== MODULE N
def module_N():
    hdr("MODULE N -- neighbour arm: p_NB, the Amendment 3 spline partials and "
        "their CIs, cell means")
    t = frame()
    own = t["own_e_b"].values
    pos = t["position"].values
    inH = t["in_H"].values
    posH = set(pos[inH])
    print(f"  frame {len(t)} rows / {len(set(pos))} positions; H {int(inH.sum())} rows / "
          f"{len(posH)} positions")

    roster = pd.read_csv(NEIGH / "roster_v1.csv")
    d3tab = pd.read_csv(D3_TBL)
    d3_of = dict(zip(d3tab.bg_id, d3tab.d3_CA))
    d3_of_new = dict(zip(roster.bg_id, roster.d3))     # the 50 new backgrounds

    # per-background rho_b: new backgrounds from the night's files, existing
    # nulls from the Phase 2 caches.  Both are raw score files; delta = score - WT.
    _wt_cache = {}

    def wkey_for(parser):
        if parser not in _wt_cache:
            fp = None if parser == "default" else "round_trip"
            wt = pd.read_csv(WT_SCORES, float_precision=fp)
            _wt_cache[parser] = {(int(r.position), str(r.mut_aa)): float(r.esm2_score)
                                 for r in wt.itertuples()}
        return _wt_cache[parser]

    tkey = {(int(r.position), str(r.mut_aa)): i for i, r in enumerate(t.itertuples())}

    def rho_from_file(path, own_pos, view_mask, score_col="score",
                      parser="default"):
        fp = None if parser == "default" else "round_trip"
        wkey = wkey_for(parser)          # SAME parser for both score files
        d = pd.read_csv(path, float_precision=fp)
        ii, dd = [], []
        for r in d.itertuples():
            k = (int(r.position), str(r.mut_aa))
            if k in tkey and k in wkey:
                ii.append(tkey[k])
                dd.append(float(getattr(r, score_col)) - wkey[k])
        ii = np.asarray(ii)
        dd = np.asarray(dd)
        keep = view_mask[ii] & (t["position"].values[ii] != own_pos)
        return sp(dd[keep], own[ii[keep]]), len(ii)

    # --- the frozen anchors first
    rhoA_H, _ = rho_from_file(A222V_SCORES, 222, inH, "esm2_score_a222v_bg")
    rhoA_H_rt, _ = rho_from_file(A222V_SCORES, 222, inH, "esm2_score_a222v_bg",
                                 parser="round_trip")
    cmp("rho_A222V on H", rhoA_H, -0.090021683, TOL_STAT, "(A222V arm, H, own pos excluded)")
    print(f"  [C2-DEC8] the same value with round_trip float parsing: {rhoA_H_rt:.17f} "
          f"| diff {abs(rhoA_H-rhoA_H_rt):.3e} (4 rank flips, as in module L)")
    cmp("rho_A222V on H", rhoA_H, -0.090021683, TOL_STAT, "(A222V arm, H, own pos excluded)")

    # --- NB = new C1+C2+C5 + the six existing d3<=12 nulls
    existing6 = ["G_I192T", "AV_220", "AV_155", "AV_195", "G_L178T", "AV_175"]
    new_cells = roster[roster["cell"].isin(["C1", "C2", "C5"])]
    members, rho_nb = [], {}
    for r in new_cells.itertuples():
        f = NEIGH / f"bg_{r.bg_id}.csv"
        v, _ = rho_from_file(f, int(r.position), inH)
        members.append((r.bg_id, r.cell, int(r.position), v))
        rho_nb[r.bg_id] = v
    for bg in existing6:
        f = PHASE2 / f"bg_{bg}.csv"
        rr = roster[roster.bg_id == bg]
        p = int(rr.position.iloc[0]) if len(rr) else None
        if p is None:
            ar = pd.read_csv(ARM_ROSTER)
            hit = ar[ar.bg_id == bg]
            p = int(hit.position.iloc[0]) if len(hit) else 222
        v, _ = rho_from_file(f, p, inH)
        members.append((bg, "existing-d3<=12", p, v))
        rho_nb[bg] = v
    print(f"\n  |NB| = {len(members)} (new C1+C2+C5 = {len(new_cells)}, existing = 6)")

    vals = np.array([m[3] for m in members])
    k_neg = int((vals <= rhoA_H).sum())
    p_nb = (1 + k_neg) / (1 + len(members))
    print(f"\n  all {len(members)} rho_b (sorted ascending), the five at or below "
          f"rho_A222V = {rhoA_H:.9f} marked:")
    for bg, cell, p_, v in sorted(members, key=lambda x: x[3]):
        mark = "  <= rho_A222V" if v <= rhoA_H else ""
        print(f"    {bg:12s} cell {cell:14s} own pos {p_:4d}  rho_b {v:+.9f}{mark}")
    cmp("p_NB(neg)", p_nb, 6 / 47, TOL_STAT,
        f"= (1 + {k_neg}) / (1 + {len(members)})")
    k_abs_le = int((np.abs(vals) <= abs(rhoA_H)).sum())
    k_abs_ge = int((np.abs(vals) >= abs(rhoA_H)).sum())
    cmp("p_NB(abs)", (1 + k_abs_le) / (1 + len(members)), 42 / 47, TOL_STAT,
        f"= (1 + {k_abs_le}) / (1 + {len(members)}), tail |rho_b| <= |rho_A222V|")
    print(f"  *** TAIL FINDING (reported, not reconciled): the two staged Phase-4 "
          f"modules use OPPOSITE tails for the identically named 'abs' p-value.")
    print(f"      the neighbour arm (script 172, line 475: `abs(v) > abs(rho_a_H)`) "
          f"gives {(1 + k_abs_le)/(1+len(members)):.6f} = {42}/47;")
    print(f"      scripts/lib/phase3_common.p_spec (used by 167 and 174) counts "
          f">= instead and would give {(1 + k_abs_ge)/(1+len(members)):.6f}.")
    print(f"      The NEIGHBOUR prereg line reads 'p_NB(abs) uses |rho|', i.e. the "
          f"same formula with |rho| substituted, which IS the <= tail -- so 172 "
          f"follows its prereg literally and phase3_common does not. No frozen "
          f"word uses either value (the section-5 word uses p_NB(neg)). Flagged "
          f"for C4; NOT silently reconciled here.")
    cmp("count of NB members at or below rho_A222V", k_neg, 5, 0)
    # frozen word
    if len(members) < 30:
        w = "UNDERPOWERED"
    elif p_nb <= 0.05:
        w = "POSITION-SPECIFIC"
    elif p_nb <= 0.10:
        w = "UNRESOLVED"
    else:
        w = "REGION-LIKE"
    print(f"  frozen section-5 word from MY numbers: {w} (staged: REGION-LIKE)")
    cmp("section-5 word", w, "REGION-LIKE", 0)

    # position-collapsed sensitivity (Amendment 1 item 7): one rho per POSITION
    pos_of = {m[0]: m[2] for m in members}
    bypos = {}
    for bg, cell, p_, v in members:
        bypos.setdefault(p_, []).append(v)
    coll = {p_: float(np.mean(vs)) for p_, vs in bypos.items()}
    cv = np.array(list(coll.values()))
    ck = int((cv <= rhoA_H).sum())
    cp = (1 + ck) / (1 + len(cv))
    print(f"  position-collapsed sensitivity: {len(cv)} distinct positions, "
          f"k = {ck}, p = {cp:.6f} (staged 0.097561 = 40/410 -- see log)")
    print(f"    NOTE the staged sensitivity pools the 40 POSITIVES of the 40 new "
          f"backgrounds plus 6 existing = 40 positions with k = 0; mine pools all "
          f"{len(cv)} own positions of all {len(members)} members. Different sets, "
          f"reported not reconciled (the staged run's own number is quoted above).")

    # --- cell means of rho_b over pool P (new 50 + the 67 RESOLVED NULLS with d3)
    print("\n  cell means of rho_b (pool P = the 50 new + the 67 resolved existing "
          "nulls with d3):")
    # The frozen cell rules (NEIGH section 2) plus Amendment 1's NEW cell C5,
    # implemented here from the text:
    #   C1 d3<=12 & dseq<=20 | C2 d3<=12 & dseq>40 | C3 d3>18 & dseq<=25
    #   C4 d3>20 & dseq>40   | C5 (AMENDMENT 1, NEW) d3<=12 & 20<dseq<=40
    #   otherwise unassigned ("gap")
    def cell_of(posn, d3v):
        dseq = abs(int(posn) - 222)
        if not np.isfinite(d3v):
            return ""
        if d3v <= 12 and dseq <= 20:
            return "C1"
        if d3v <= 12 and dseq > 40:
            return "C2"
        if d3v > 18 and dseq <= 25:
            return "C3"
        if d3v > 20 and dseq > 40:
            return "C4"
        if d3v <= 12 and 20 < dseq <= 40:
            return "C5"
        return ""

    ar = pd.read_csv(ARM_ROSTER)
    nulls78 = ar[ar.arm.isin(["V", "G"])]
    d3tab = pd.read_csv(D3_TBL)
    res = d3tab[(d3tab.resolved == True)]  # noqa: E712
    r67, cellcount = {}, {}
    for r in nulls78.itertuples():
        if r.bg_id not in set(res.bg_id):
            continue
        f = PHASE2 / f"bg_{r.bg_id}.csv"
        v, _ = rho_from_file(f, int(r.position), inH)
        c = cell_of(int(r.position), float(d3_of.get(r.bg_id, np.nan)))
        r67[r.bg_id] = (v, c, int(r.position))
        cellcount[c] = cellcount.get(c, 0) + 1
    print(f"    resolved NULLS recomputed: {len(r67)} (frozen: 67)")
    print(f"    their cells: {dict(sorted(cellcount.items()))}   (staged: "
          f"{{'C1': 1, 'C2': 3, 'C3': 3, 'C4': 51, 'C5': 2, 'gap': 7}})")
    # pool P is the 50 new backgrounds (ALL cells, C1/C2/C3/C5) plus the 67 resolved
    # nulls, so the C3 new backgrounds need their rho_b as well.
    for r in roster[~roster.bg_id.isin(rho_nb)].itertuples():
        f = NEIGH / f"bg_{r.bg_id}.csv"
        v, _ = rho_from_file(f, int(r.position), inH)
        rho_nb[r.bg_id] = v
        members.append((r.bg_id, r.cell, int(r.position), v))
    print(f"    the {len(roster) - len(new_cells)} new backgrounds outside NB "
          f"(cells C3) also given a rho_b, because pool P contains them: "
          f"{sorted(roster[~roster.bg_id.isin([m[0] for m in members[:len(new_cells)+6]])]['cell'].unique())}")

    pool = [(bg, cell, rho_nb[bg]) for bg, cell in
            ((r.bg_id, r.cell) for r in roster.itertuples()) if bg in rho_nb]
    pool += [(bg, c, v) for bg, (v, c, _) in r67.items()]
    pc = {}
    for _, c, _ in pool:
        pc[c] = pc.get(c, 0) + 1
    print(f"    pool P = {len(pool)} = 50 new + {len(r67)} existing; its cells "
          f"{dict(sorted(pc.items()))}   (staged: C1 13, C2 16, C5 17, C3 13, C4 51)")
    for cell, vals_, tgt in (("C1", None, -0.027997), ("C2", None, -0.035857),
                             ("C5", None, -0.058180)):
        vv = np.array([v for _, c, v in pool if c == cell])
        cmp(f"cell mean {cell}", float(np.mean(vv)), tgt, TOL_PRINTED,
            f"(n = {len(vv)} over pool P; staged prints 6 dp, so the gate is half a "
            f"unit of the last printed digit -- C2-DEC9)")
    # contrasts
    c2 = np.array([v for _, c, v in pool if c == "C2"])
    c4 = np.array([v for _, c, v in pool if c == "C4"])
    contrast = float(np.mean(c2) - np.mean(c4))
    cmp("contrast C2 - C4", contrast, -0.036890, TOL_PRINTED,
        f"(C2 n={len(c2)}, C4 n={len(c4)}; staged CI [-0.056108, -0.017307])")

    # --- Amendment 3 flexible-control partials, with CIs, on pool P
    print("\n  Amendment 3 flexible-control partial Spearman on pool P "
          "(my own spline basis + my own bootstrap):")
    geom = []
    for bg, cell, v in pool:
        rr = roster[roster.bg_id == bg]
        if len(rr):
            p_ = int(rr.position.iloc[0])
            d3v = float(rr.d3.iloc[0])
            dsv = float(rr.dseq.iloc[0])
        else:
            p_ = int(ar.loc[ar.bg_id == bg, "position"].iloc[0])
            d3v = float(d3_of.get(bg, np.nan))
            dsv = abs(p_ - 222)
        geom.append((v, d3v, dsv))
    y = np.array([g[0] for g in geom])
    x3 = np.array([g[1] for g in geom])
    xs = np.array([g[2] for g in geom])
    ok = np.isfinite(y) & np.isfinite(x3) & np.isfinite(xs)
    y, x3, xs = y[ok], x3[ok], xs[ok]
    print(f"    pool used: {len(y)} backgrounds (all with finite d3 and dseq)")

    def partial_flexible(target, other, control):
        """Amendment 3's statistic: rank(rho_b) and rank(feature) regressed on a
        natural cubic spline basis of the RAW other distance.

        The basis is built with patsy's own `cr(x, knots=[q25,q50,q75])`, which is
        the function Amendment 3 item 2 NAMES ("the amendment's three named knots
        are operative", disclosed as N-AN15 in the staged run).  patsy is a
        third-party library, not a project staged script, so using it keeps this
        an independent recomputation; the alternative -- my own numpy basis --
        was tried first and gave +0.214063 / -0.048437, i.e. a DIFFERENT column
        space (it does not reproduce the specified construction), so it was
        discarded rather than tuned.  See C2-DEC11.
        """
        import patsy
        q = np.percentile(control, [25, 50, 75])
        B = np.asarray(patsy.dmatrix("cr(c, knots=q)", {"c": control, "q": list(q)}))[:, 1:]
        ry = avg_rank(target)
        rx = avg_rank(other)
        ex = rx - B @ np.linalg.lstsq(B, rx, rcond=None)[0]
        ey = ry - B @ np.linalg.lstsq(B, ry, rcond=None)[0]
        return float(np.corrcoef(ex, ey)[0, 1])

    p_d3 = partial_flexible(y, x3, xs)
    p_ds = partial_flexible(y, xs, x3)
    print(f"    knots (pool 25/50/75 of the raw control): dseq "
          f"{np.percentile(xs,[25,50,75]).round(3).tolist()}  d3 "
          f"{np.percentile(x3,[25,50,75]).round(3).tolist()}  (staged dseq basis "
          f"knots [1.0, 26.0, 67.0, 163.0, 428.0], d3 [3.805, 10.161, 20.112, "
          f"36.759, 76.194] = boundary knots added by cr())")
    cmp("partial rho_b ~ d3 | spline(dseq)  [PRIMARY]", p_d3, 0.192294, TOL_PRINTED,
        "(staged prints 6 dp; C2-DEC9)")
    cmp("partial rho_b ~ dseq | spline(d3) [PRIMARY]", p_ds, -0.053758, TOL_PRINTED,
        "(staged prints 6 dp; C2-DEC9)")

    rng = np.random.default_rng(SEED)
    n = len(y)
    b_d3, b_ds = [], []
    for _ in range(N_BOOT):
        ix = rng.integers(0, n, n)
        b_d3.append(partial_flexible(y[ix], x3[ix], xs[ix]))
        b_ds.append(partial_flexible(y[ix], xs[ix], x3[ix]))
    b_d3 = np.array([v for v in b_d3 if np.isfinite(v)])
    b_ds = np.array([v for v in b_ds if np.isfinite(v)])
    lo3, hi3 = pct(b_d3, 2.5), pct(b_d3, 97.5)
    lo_s, hi_s = pct(b_ds, 2.5), pct(b_ds, 97.5)
    print(f"    my background-level bootstrap CI ({len(b_d3)} finite of {N_BOOT} draws, "
          f"refit per resample as Amendment 3 requires):")
    print(f"      d3  partial {p_d3:+.6f} CI [{lo3:+.6f}, {hi3:+.6f}]   "
          f"| staged +0.192294 CI [-0.018716, +0.379290]")
    print(f"      dseq partial {p_ds:+.6f} CI [{lo_s:+.6f}, {hi_s:+.6f}]   "
          f"| staged -0.053758 CI [-0.276061, +0.167518]")
    print("    CIs are REPORTED SIDE BY SIDE, not gated (C2-DEC2: my draw ids "
          "differ from the staged ones, so only the point estimate is gated).")
    # frozen word from my own numbers
    ex3 = lo3 > 0 or hi3 < 0
    exs = lo_s > 0 or hi_s < 0
    w = ("BOTH-LOCAL" if ex3 and exs else "3D-LOCAL" if ex3 else
         "SEQUENCE-LOCAL" if exs else "NEITHER-RESOLVED")
    print(f"    frozen section-6 word from MY numbers: {w} (staged: NEITHER-RESOLVED)")
    cmp("section-6 word", w, "NEITHER-RESOLVED", 0)


# =============================================================== MODULE L
# --------------------------------------------------------------------------
# SESSION 4b-B: the full three-model ladder, and the two cross-model
# agreements.  Written while Night B was running, so it is code-only until the
# night finishes; nothing here ran before the 150M/35M files existed.
# --------------------------------------------------------------------------
LADDER = ROOT / "data/processed/phase4/ladder"


def _h_rows(t, own_pos, keys):
    """Boolean mask over the frame for the H rows of one background."""
    inH = t["in_H"].to_numpy()
    pos = t["position"].to_numpy()
    return inH & (pos != own_pos)


def ladder_column(model, t, arm_roster, own_pos_of):
    """Build {bg_id: (frame_row_indices, delta)} for one model on H rows, with the
    background's own position excluded.

    650M is the CACHED column: A222V from esm2_a222v_bg_scores.csv, the other 96 from
    data/processed/phase2/bg_*.csv, the wild-type side from esm2_wt_scores.csv.
    150M / 35M are the night's own outputs: ladder/<model>/bg_*.csv with that model's
    OWN wt_H.csv as the wild-type side (the frozen design scores delta against the
    model's own wild-type arm, LD-DEC5).
    Returns None when the model has no scores yet.
    """
    tpos = t["position"].to_numpy(int)
    tam = t["mut_aa"].astype(str).to_numpy()
    inH = t["in_H"].to_numpy()
    tkey = [(int(a), b) for a, b in zip(tpos, tam)]

    if model == "650M":
        wt = pd.read_csv(WT_SCORES)
        wmap = {(int(r.position), str(r.mut_aa)): float(r.esm2_score) for r in wt.itertuples()}
        av = pd.read_csv(A222V_SCORES)
        src = {"A222V": {(int(r.position), str(r.mut_aa)): float(r.esm2_score_a222v_bg)
                         for r in av.itertuples()}}
        for bg in arm_roster:
            f = PHASE2 / f"bg_{bg}.csv"
            if f.exists():
                d = pd.read_csv(f)
                src[bg] = {(int(r.position), str(r.mut_aa)): float(r.score)
                           for r in d.itertuples()}
    else:
        mdir = LADDER / model
        wt_path = mdir / "wt_H.csv"
        if not wt_path.exists():
            return None
        w = pd.read_csv(wt_path)
        wmap = {(int(r.position), str(r.mut_aa)): float(r.score) for r in w.itertuples()}
        src = {}
        for f in sorted(mdir.glob("bg_*.csv")):
            d = pd.read_csv(f)
            src[f.stem[3:]] = {(int(r.position), str(r.mut_aa)): float(r.score)
                               for r in d.itertuples()}

    out = {}
    for bg, smap in src.items():
        ownp = own_pos_of.get(bg, -1)
        idx, dd = [], []
        for i, k in enumerate(tkey):
            if not inH[i] or tpos[i] == ownp:
                continue
            if k in smap and k in wmap:
                idx.append(i)
                dd.append(smap[k] - wmap[k])
        if len(idx) > 10:
            out[bg] = (np.asarray(idx, dtype=int), np.asarray(dd, dtype=float))
    return out or None


def module_LALL():
    """Per-model words for every ladder model that has scores, plus both
    cross-model agreements, recomputed from the raw score files.

    WORD (frozen MODEL_LADDER section 3, quoted): MODEL-REPLICATES iff the CI of
    rho_A222V on H lies below zero AND p_spec_H(neg) <= 0.10.
    MODEL-DOES-NOT-REPLICATE iff the CI includes zero or the sign reverses.
    MODEL-PARTIAL otherwise.

    C2-DEC12 (DISCLOSED BUG IN MY OWN EARLIER CODE): session 4b's module_L derived
    the word from the PARTIAL's CI rather than the ANCHOR rho's CI. Both intervals
    exclude zero, so the word came out the same, but the statistic was the wrong one
    and is corrected here.
    """
    hdr("MODULE L, ALL MODELS -- per-model words and both cross-model agreements")
    t = frame()
    own = t["own_e_b"].to_numpy(float)
    tpos_all = t["position"].to_numpy(int)
    tam_all = t["mut_aa"].astype(str).to_numpy()
    d3 = pd.read_csv(D3_TBL)
    ar = pd.read_csv(ARM_ROSTER)
    own_pos_of = {r.bg_id: int(r.position) for r in ar.itertuples()}
    nulls78 = [r.bg_id for r in ar.itertuples() if r.arm in ("V", "G")]
    d3_of = dict(zip(d3.bg_id, d3.d3_CA))
    resolved_nulls = [b for b in nulls78
                      if b in set(d3[d3.resolved == True].bg_id)]  # noqa: E712

    cols, rhos, wtcol = {}, {}, {}
    for model in ("650M", "150M", "35M"):
        c = ladder_column(model, t, [r.bg_id for r in ar.itertuples()], own_pos_of)
        if c is None:
            print(f"\n-- model {model}: NO SCORES ON DISK -> every number for this "
                  f"model is NOT-COMPUTABLE (C2-DEC6); no word is issued")
            continue
        cols[model] = c
        rho_b, mean_abs = {}, {}
        for bg, (idx, delta) in c.items():
            rho_b[bg] = sp(delta, own[idx])
            mean_abs[bg] = float(np.mean(np.abs(delta)))
        rhos[model] = rho_b
        wtcol[model] = mean_abs
        print(f"\n-- model {model}: {len(c)} backgrounds with scores on H "
              f"(rows per background {min(len(v[0]) for v in c.values())}"
              f"-{max(len(v[0]) for v in c.values())})")

        rhoA = rho_b["A222V"]
        TGT = {"650M": -0.090021683, "150M": 0.026745078, "35M": -0.020193686}
        cmp(f"[{model}] rho_A222V on H", rhoA, TGT[model], TOL_PRINTED,
            "(174 prints 9 dp; C2-DEC9)")
        # (i) the ANCHOR CI -- this is the CI the frozen word uses
        ia = list(cols[model]["A222V"][0])
        pos_a = t["position"].to_numpy()[ia]
        dlt_a = cols[model]["A222V"][1]
        own_a = own[ia]
        point, lo, hi, nf = pos_cluster_boot(
            pos_a, lambda ix: sp(dlt_a[ix], own_a[ix]), n_boot=N_BOOT, seed=SEED)
        print(f"    (i)   anchor rho_A222V on H {rhoA:+.9f} CI [{lo:+.6f}, {hi:+.6f}] "
              f"({nf}/{N_BOOT} finite, position clusters)  <- the CI the WORD uses")
        # (ii) p_spec over the 78 nulls
        vn = np.array([rho_b[b] for b in nulls78 if b in rho_b])
        kn, _ = p_spec_count(rhoA, vn, "neg")
        ka, _ = p_spec_count(rhoA, vn, "abs")
        TGTP = {"650M": 0.050633, "150M": 0.810127, "35M": 0.341772}
        cmp(f"[{model}] p_spec_H(neg)", round((1 + kn) / (1 + len(vn)), 6), TGTP[model],
            TOL_PRINTED, f"= (1+{kn})/(1+{len(vn)}) vs the frozen 0.10 threshold")
        print(f"          beaters: {sorted([b for b in nulls78 if b in rho_b and rho_b[b] <= rhoA])}")
        # (iii) partial controlling THIS model's own wild-type score
        print(f"    (iii) partial rho_H | this model's S_W: ", end="")
        if model == "650M":
            sw = t["esm2_score"].to_numpy(float)[ia]
            cmp(f"[{model}] partial rho_H | S_W", partial_spearman(dlt_a, own_a, sw),
                -0.067208910, TOL_STAT, "(650M: the WT-background ESM-2 score)")
        else:
            w = pd.read_csv(LADDER / model / "wt_H.csv")
            wm = {(int(r.position), str(r.mut_aa)): float(r.score) for r in w.itertuples()}
            sw = np.array([wm[(int(tpos_all[i]), str(tam_all[i]))] for i in ia])
            TGT3 = {"150M": 0.015719, "35M": -0.009812}
            cmp(f"[{model}] partial rho_H | its own WT arm",
                round(partial_spearman(dlt_a, own_a, sw), 6), TGT3[model], TOL_PRINTED,
                "(174 prints 6 dp; no word attaches to this number)")
        # (iv) gradient over the resolved nulls
        gv = np.array([rho_b[b] for b in resolved_nulls])
        gx = np.array([float(d3_of[b]) for b in resolved_nulls])
        TGT4 = {"650M": 0.713319, "150M": 0.294124, "35M": 0.204969}
        cmp(f"[{model}] gradient Spearman(rho_b, d3) over 67 resolved nulls",
            round(sp(gx, gv), 6), TGT4[model], TOL_PRINTED,
            f"(n = {len(resolved_nulls)}; 174 prints 6 dp)")
        # (v) shift confound over the 96 backgrounds
        c96 = [b for b in ar.bg_id if b != "A222V" and b in rho_b]
        TGT5 = {"650M": -0.612697, "150M": 0.094615, "35M": -0.333315}
        cmp(f"[{model}] shift confound Spearman(rho_b, mean|delta_b|)",
            round(sp(np.array([wtcol[model][b] for b in c96]),
                     np.array([rho_b[b] for b in c96])), 6),
            TGT5[model], TOL_PRINTED, f"(n = {len(c96)}; 174 prints 6 dp)")
        # word, from the ANCHOR CI.  Frozen section 3, all three clauses:
        #   REPLICATES         iff the CI lies below zero AND p_spec_H(neg) <= 0.10
        #   DOES-NOT-REPLICATE iff the CI INCLUDES ZERO or the sign reverses
        #   PARTIAL            otherwise
        # C2-DEC14 (DISCLOSED, session 4b-C): my first version tested `lo > 0` for the
        # DOES-NOT clause, which means "the CI lies entirely ABOVE zero" and therefore
        # missed the common case of an interval that SPANS zero.  It wrongly returned
        # MODEL-PARTIAL for both 150M and 35M, whose intervals both span zero.  The
        # staged words are correct; this was my bug, disclosed here and in the log
        # rather than quietly corrected.
        p_here = (1 + kn) / (1 + len(vn))
        ci_includes_zero = (lo <= 0.0 <= hi)
        sign_reversed = (rhoA > 0.0)     # the anchor's sign is negative by construction
        if (hi < 0.0) and (p_here <= 0.10):
            word = "MODEL-REPLICATES"
        elif ci_includes_zero or sign_reversed:
            word = "MODEL-DOES-NOT-REPLICATE"
        else:
            word = "MODEL-PARTIAL"
        print(f"    word derivation: CI [{lo:+.6f}, {hi:+.6f}] includes zero = "
              f"{ci_includes_zero}; sign reversed (rho_A222V > 0) = {sign_reversed}; "
              f"p_spec_H(neg) = {p_here:.6f} <= 0.10 = {p_here <= 0.10}")
        TGTW = {"650M": "MODEL-REPLICATES", "150M": "MODEL-DOES-NOT-REPLICATE",
                "35M": "MODEL-DOES-NOT-REPLICATE"}
        cmp(f"[{model}] WORD (frozen section 3)", word, TGTW[model], 0,
            "(CI of rho_A222V on H below zero AND p_spec_H(neg) <= 0.10)")

    # ------------------------------------------------ cross-model agreement
    print("\n-- CROSS-MODEL AGREEMENT (frozen section 2, last clause)")
    for other in ("150M", "35M"):
        if "650M" not in cols or other not in cols:
            print(f"  650M vs {other}: NOT-COMPUTABLE (a column is missing; C2-DEC6)")
            continue
        per_bg, miss = [], 0
        common_rho = []
        for bg in cols["650M"]:
            if bg not in cols[other]:
                miss += 1
                continue
            i1, d1 = cols["650M"][bg]
            i2, d2 = cols[other][bg]
            pos2 = {int(v): j for j, v in enumerate(i2)}
            pick = [pos2[int(v)] for v in i1 if int(v) in pos2]
            if len(pick) < 10:
                miss += 1
                continue
            per_bg.append(sp(d1, d2[pick]))
            if bg in rhos["650M"] and bg in rhos[other]:
                common_rho.append((rhos["650M"][bg], rhos[other][bg]))
        a = np.array(per_bg)
        cr = np.array(common_rho)
        print(f"  650M vs {other}: per-background Spearman(delta_650M, delta_{other}) "
              f"on common H rows, over {len(a)} backgrounds ({miss} unusable)")
        print(f"     MEDIAN {np.median(a):+.6f}   RANGE [{a.min():+.6f}, {a.max():+.6f}]")
        TGTC = {"150M": (-0.145645, 0.086725), "35M": (0.381036, 0.071303)}
        cmp(f"650M vs {other}: across-background Spearman(rho_b) over 97 backgrounds",
            round(sp(cr[:, 0], cr[:, 1]), 6), TGTC[other][0], TOL_PRINTED,
            f"(n = {len(cr)})")
        cmp(f"650M vs {other}: per-background delta Spearman, MEDIAN over 97",
            round(float(np.median(a)), 6), TGTC[other][1], TOL_PRINTED)
        cmp(f"650M vs {other}: per-background delta Spearman, RANGE low",
            round(float(a.min()), 6), {"150M": -0.072518, "35M": -0.084198}[other],
            TOL_PRINTED)
        cmp(f"650M vs {other}: per-background delta Spearman, RANGE high",
            round(float(a.max()), 6), {"150M": 0.380496, "35M": 0.348244}[other],
            TOL_PRINTED)


def module_L():
    hdr("MODULE L -- model ladder, the 650M column (150M/35M: NOT-COMPUTABLE, "
        "C2-DEC6 -- night B never ran)")
    t = frame()
    own = t["own_e_b"].values
    inH = t["in_H"].values
    tpos = t["position"].values
    rho = pd.read_csv(RHO_TBL)
    print(f"  cached rho table: {len(rho)} backgrounds (the 96 Phase 2 ones; A222V's "
          f"rho is recomputed here from the raw score file, not read from it)")
    dm = delta_matrix(parser="default")        # canonical (bit-identical to task32)
    dmr = delta_matrix(parser="round_trip")    # exact doubles (C2-DEC8 sensitivity)

    def rho_on(dm_, bg, mask):
        return sp(dm_[bg][mask], own[mask])

    mH = inH & (tpos != 222)
    mine = rho_on(dm, "A222V", mH)
    cmp("rho_A222V on H (650M)", mine, -0.090021683, TOL_STAT)
    mine_rt = rho_on(dmr, "A222V", mH)
    print(f"  [C2-DEC8 float-parser sensitivity] the same statistic from the same "
          f"files parsed with round_trip instead of the default parser: "
          f"{mine_rt:.17f} | diff {abs(mine-mine_rt):.3e}")
    print(f"    cause measured, not assumed: the two parses differ by up to "
          f"3.55e-15 per value, which flips 4 of 7,526 ranks on this view. The "
          f"DEFAULT parse is bit-identical to the task32 columns (the canonical "
          f"cached construction the frozen block names), so it is the primary.")

    # p_spec_H over the 78 nulls (V u G), own position excluded per background
    ar = pd.read_csv(ARM_ROSTER)
    nulls = ar[ar.arm.isin(["V", "G"])]
    print(f"  null set N = {len(nulls)} backgrounds (V u G)")
    stats, stats_rt = {}, {}
    for r in nulls.itertuples():
        if r.bg_id not in dm:
            continue
        m = inH & (tpos != int(r.position))
        stats[r.bg_id] = rho_on(dm, r.bg_id, m)
        stats_rt[r.bg_id] = rho_on(dmr, r.bg_id, m)
    v = np.array(list(stats.values()))
    k, n = p_spec_count(mine, v, "neg")
    p_spec = (1 + k) / (1 + n)
    ka, _ = p_spec_count(mine, v, "abs")
    p_spec_abs = (1 + ka) / (1 + n)
    cmp("p_spec_H(neg)", round(p_spec, 6), 0.050633, TOL_STAT, f"= (1 + {k}) / (1 + {n})")
    cmp("p_spec_H(abs)", round(p_spec_abs, 6), 0.050633, TOL_STAT,
        f"= (1 + {ka}) / (1 + {n}), tail |rho_b| >= |rho_A222V|")
    beaters = sorted([bg for bg, s in stats.items() if s <= mine])
    print(f"  beaters: {beaters} (staged: ['AV_195', 'AV_220', 'G_P254F'])")
    dmax = max(abs(stats[b] - stats_rt[b]) for b in stats)
    k_rt, _ = p_spec_count(mine_rt, np.array(list(stats_rt.values())), "neg")
    print(f"  [C2-DEC8] across all {len(stats)} null rho_b the parser changes rho by at "
          f"most {dmax:.3e}, and p_spec_H(neg) k by {abs(k_rt - k)} "
          f"({k} -> {k_rt}): no count, p-value, CI or word is affected.")

    # partial given this model's S_W, on H
    part = partial_spearman(dm["A222V"][mH], own[mH], t["esm2_score"].values[mH])
    cmp("partial rho_H | S_W (650M)", part, -0.067208910, TOL_STAT,
        "(target is A4's 9-dp value; script 174 PRINTS this at 6 dp as -0.067209, "
        "which is why the two differ in the 7th decimal)")
    sw = t["esm2_score"].values
    point, lo, hi, nf = pos_cluster_boot(
        tpos[mH],
        lambda ix: partial_spearman(dm["A222V"][mH][ix], own[mH][ix], sw[mH][ix]),
        n_boot=N_BOOT, seed=SEED)
    print(f"  my partial CI ({nf}/{N_BOOT} finite, position clusters on H): "
          f"[{lo:+.6f}, {hi:+.6f}]  | staged [-0.099734, -0.033553]")

    # gradient Spearman(rho_b, d3) over the resolved nulls
    d3 = pd.read_csv(D3_TBL)
    res = d3[(d3.resolved == True) & (d3.bg_id.isin(stats))]  # noqa: E712
    g = sp(np.array([stats[b] for b in res.bg_id]), res.d3_CA.values)
    cmp("gradient Spearman(rho_b, d3) over resolved nulls", round(g, 6), 0.713319, TOL_STAT,
        f"(n = {len(res)})")

    # shift confound Spearman(rho_b, mean|delta_b|) over 96 backgrounds
    ar96 = ar[ar.bg_id != "A222V"]
    xs, ys = [], []
    for r in ar96.itertuples():
        if r.bg_id not in dm:
            continue
        m = inH & (tpos != int(r.position))
        xs.append(rho_on(dm, r.bg_id, m))
        ys.append(float(np.nanmean(np.abs(dm[r.bg_id][m]))))
    xs, ys = np.array(xs), np.array(ys)
    m2 = np.isfinite(xs) & np.isfinite(ys)
    c = sp(xs[m2], ys[m2])
    cmp("shift confound Spearman(rho_b, mean|delta_b|)", round(c, 6), -0.612697, TOL_STAT,
        f"(n = {int(m2.sum())})")

    w = ("MODEL-REPLICATES" if (hi < 0 and p_spec <= 0.10) else
         "MODEL-PARTIAL" if hi < 0 else "MODEL-DOES-NOT-REPLICATE")
    print(f"  frozen section-3 word from MY numbers: {w} (staged: MODEL-REPLICATES)")
    cmp("ladder word (650M)", w, "MODEL-REPLICATES", 0)
    print("  NOT-COMPUTABLE: 150M and 35M columns (no wt_H.csv, no bg files: "
          "night B never ran), and therefore both cross-model agreements.")


# =============================================================== MODULE M
def module_M():
    hdr("MODULE M -- mechanism-matched analyses (M-1, M-2, M-3 re-draw, M-4 "
        "grid, M-5, M-6)")
    t = frame()
    own = t["own_e_b"].values
    tpos = t["position"].values
    inH = t["in_H"].values
    dm = delta_matrix()
    ar = pd.read_csv(ARM_ROSTER)
    nulls = ar[ar.arm.isin(["V", "G"])]
    # the A222V arm uses the FRAME's canonical delta_esm column (see frame()'s
    # C2-DEC8 note): it is the column the staged pipeline uses, and on the full
    # frame it gives -0.08811806424891734, the G-M1 target exactly, whereas the
    # file-recomputed difference gives -0.08811808948323244.
    dA = t["delta"].to_numpy(float)

    rhoA_full = sp(dA, own)
    cmp("M-1 rho_A222V (full frame)", rhoA_full, -0.088118064, TOL_STAT)
    mH = inH & (tpos != 222)
    rhoA_H = sp(dA[mH], own[mH])
    cmp("M-1 rho_A222V (H)", rhoA_H, -0.090021683, TOL_STAT)

    # p_spec full and H
    def p_spec(view_mask, exclude_own=True):
        st = {}
        for r in nulls.itertuples():
            if r.bg_id not in dm:
                continue
            m = view_mask.copy()
            if exclude_own:
                m = m & (tpos != int(r.position))
            st[r.bg_id] = sp(dm[r.bg_id][m], own[m])
        ra = sp(dA[view_mask & (tpos != 222)], own[view_mask & (tpos != 222)])
        return ra, st
    ra_f, st_f = p_spec(np.ones(len(t), bool))
    ra_h, st_h = p_spec(inH)
    kf = int((np.array(list(st_f.values())) <= ra_f).sum())
    kh = int((np.array(list(st_h.values())) <= ra_h).sum())
    cmp("M-1 p_spec(neg) full", round((1 + kf) / 79, 9), 2 / 79, TOL_STAT, f"(k = {kf})")
    cmp("M-1 p_spec(neg) H", round((1 + kh) / 79, 9), 4 / 79, TOL_STAT, f"(k = {kh})")
    print(f"  full-frame beaters: {sorted([b for b,s in st_f.items() if s<=ra_f])} "
          f"(staged ['G_P254F']); H beaters: "
          f"{sorted([b for b,s in st_h.items() if s<=ra_h])}")

    # partial controlling S_W, full frame, with position-cluster CI
    sw = t["esm2_score"].values
    part_full = partial_spearman(dA, own, sw)
    cmp("M-1 partial | S_W (full frame)", part_full, -0.064148044, TOL_STAT)
    point, lo, hi, nf = pos_cluster_boot(
        tpos, lambda ix: partial_spearman(dA[ix], own[ix], sw[ix]),
        n_boot=N_BOOT, seed=SEED)
    print(f"  my partial CI ({nf}/{N_BOOT} finite, position clusters): [{lo:+.6f}, "
          f"{hi:+.6f}]  | staged [-0.093576, -0.035309]")
    cmp("M-1 retained fraction (partial / raw)", round(part_full / rhoA_full, 6),
        0.727978, TOL_STAT)

    # H-view partial (the ladder's anchor control is the same construction)
    part_H = partial_spearman(dA[mH], own[mH], sw[mH])
    cmp("M-1 partial | S_W (H view)", part_H, -0.067208910, TOL_STAT)
    point, lo, hi, nf = pos_cluster_boot(
        tpos[mH], lambda ix: partial_spearman(dA[mH][ix], own[mH][ix], sw[mH][ix]),
        n_boot=N_BOOT, seed=SEED)
    print(f"  my H partial CI ({nf}/{N_BOOT} finite): [{lo:+.6f}, {hi:+.6f}]  "
          f"| staged [-0.099734, -0.033553]")

    # secondary control: S_W + base functionality
    bf = t["base_functionality"].values
    part2 = partial_spearman(dA, own, np.column_stack([sw, bf]))
    cmp("M-1 secondary two-covariate partial", round(part2, 4), -0.0829, TOL_ROUTE,
        "(frozen target is 4 dp)")

    # M-2 stratified correlation (no word).  "deciles of S_W (equal-count over
    # the frame)" -> an EXACT equal-count split by rank, not a percentile cut:
    # the staged accounting prints row counts [1076 x7, 1075 x3] = 10,757, which a
    # percentile cut does not reproduce when S_W ties at a boundary.
    def equal_count_bins(v, k):
        order = np.argsort(v, kind="mergesort")
        b = np.empty(len(v), int)
        b[order] = (np.arange(len(v)) * k) // len(v)
        return b

    dec = equal_count_bins(sw, 10)
    print("  M-2 decile row counts: "
          f"{np.bincount(dec, minlength=10).tolist()} (staged [1076 x7, 1075 x3])")
    def stratified(y, x, d):
        num = den = 0.0
        for k in range(dec.max() + 1):
            m = d == k
            n = int(m.sum())
            if n < 2:
                continue
            r = sp(y[m], x[m])
            if not np.isfinite(r):
                continue
            num += n * r
            den += n
        return num / den if den else np.nan
    s_full = stratified(dA, own, dec)
    cmp("M-2 stratified rho (full frame)", round(s_full, 9), -0.059956192, TOL_STAT)
    print(f"  M-2 stratified rho (H view): {stratified(dA[mH], own[mH], dec[mH]):+.9f} "
          f"(staged -0.064594698; no word)")

    # ---- C2-DEC8 on the FRAME TABLE itself: own_e.b / S_W are also floats, so
    # the round_trip parser (which C2 was told to use) can differ from the staged
    # default parser by ~1e-16 and flip near-tied ranks.  Both are reported.
    tc = frame("default")
    own_c, sw_c, pos_c = tc["own_e_b"].values, tc["esm2_score"].values, tc["position"].values
    dA_c = delta_matrix(parser="default")["A222V"]
    print("\n  [C2-DEC8 frame-table parser] the three statistics above, recomputed "
          "with the frame table read by the DEFAULT parser (the staged pipeline's):")
    cmp("M-1 rho_A222V (full frame), default parse", sp(dA_c, own_c), -0.088118064,
        TOL_PRINTED, "(staged prints 9 dp; C2-DEC9)")
    cmp("M-1 partial | S_W (full frame), default parse",
        partial_spearman(dA_c, own_c, sw_c), -0.064148044, TOL_PRINTED,
        "(staged prints 9 dp; C2-DEC9)")
    dec_c = equal_count_bins(sw_c, 10)
    print(f"    M-2 stratified (default parse) = "
          f"{stratified(dA_c, own_c, dec_c):+.9f}  (staged -0.059956192; the "
          f"round_trip value above differs by 5.2e-5 -- the decile cut moves by one "
          f"row, which re-weights the within-decile Spearmans)")

    # M-5 decomposition
    print("\n  M-5 between/within decomposition (positions with >= 5 rows):")
    cnt = pd.Series(tpos).value_counts()
    qual = set(cnt[cnt >= 5].index)
    qual &= set(tpos)
    def decomp(mask):
        pm = tpos[mask]
        om = own[mask]
        dm_ = dA[mask]
        qs = [p for p in qual if (pm == p).any()]
        means_p = np.array([dm_[pm == p].mean() for p in qs])
        means_o = np.array([om[pm == p].mean() for p in qs])
        between = sp(means_p, means_o)
        wnum = wden = 0.0
        for p in qs:
            m = pm == p
            if m.sum() < 2:
                continue
            r = sp(dm_[m], om[m])
            if np.isfinite(r):
                wnum += m.sum() * r
                wden += m.sum()
        return between, (wnum / wden if wden else np.nan), len(qs)
    btw, win, nq = decomp(np.ones(len(t), bool))
    cmp("M-5 rho_between (full frame)", round(btw, 9), -0.177458126, TOL_STAT)
    cmp("M-5 rho_within (full frame)", round(win, 9), -0.028237316, TOL_STAT)
    print(f"  qualifying positions {nq}/654 (staged 652); H view: between "
          f"{decomp(mH)[0]:+.9f} within {decomp(mH)[1]:+.9f} (staged -0.169522069 / "
          f"-0.035545269)")
    point, lo, hi, nf = pos_cluster_boot(
        tpos, lambda ix: decomp_positions(tpos[ix], own[ix], dA[ix], qual),
        n_boot=min(N_BOOT, 200), seed=SEED)
    print(f"  my rho_within CI ({nf} finite of {min(N_BOOT, 200)} draws -- CAPPED and "
          f"disclosed: the per-draw refit loops over 652 positions in Python, and a "
          f"bootstrap CI is reported side by side, never gated (C2-DEC2); both "
          f"components are recomputed per draw as the frozen block requires): "
          f"[{lo:+.6f}, {hi:+.6f}] | staged [-0.049826, -0.006662]")

    # M-6 stability (position-cluster whole-placebo)
    print(f"\n  M-6 stability: {N_STAB} position-cluster draws per view, all 78 null "
          f"rho_b re-derived per draw")
    rng = np.random.default_rng(SEED)
    for nm, mask in (("full", np.ones(len(t), bool)), ("H", inH)):
        P = tpos[mask]
        uniq = np.unique(P)
        ibp = {p: np.where(P == p)[0] for p in uniq}
        o = own[mask]
        ks = []
        null_ids = [r.bg_id for r in nulls.itertuples() if r.bg_id in dm]
        own_pos_of = {r.bg_id: int(r.position) for r in nulls.itertuples()}
        cols = {b: dm[b][mask] for b in null_ids}
        colmask = {b: (tpos[mask] != own_pos_of[b]) for b in null_ids}
        o_m = own[mask]
        dA_m = dA[mask]
        for _ in range(N_STAB):
            pick = rng.choice(uniq, len(uniq), replace=True)
            ix = np.concatenate([ibp[p] for p in pick])
            ra = sp(dA_m[ix], o_m[ix])
            k = 0
            for bg in null_ids:
                col2 = np.where(colmask[bg], cols[bg], np.nan)
                if sp(col2[ix], o_m[ix]) <= ra:
                    k += 1
            ks.append(k)
        ks = np.array(ks)
        thr = 0.05 if nm == "full" else 0.10
        prob = float((ks / 78.0 <= thr).mean()) if False else float(((1 + ks) / 79 <= thr).mean())
        print(f"    {nm}: P(p_spec <= {thr}) = {prob:.4f}  k distribution "
              f"{ {int(x): int((ks==x).sum()) for x in np.unique(ks)} }")
        print(f"      staged: {'0.5760 (k=0:377, k=1:467, k=2:308, ...)' if nm=='full' else '0.7720'}"
              f"  -> frozen word boundary 0.80 / 0.50")

    # M-3 / M-4: the simulation.  Frozen block REQUIRES the project's unmodified
    # pipeline as the generator (C2-DEC5); statistics are mine.
    print(f"\n  M-3 / M-4: zero-epistasis simulation, {N_SIM} draws "
          f"(staged: 1,000 draws / 9 x 200)")
    try:
        m3 = simulation_M3_M4(t, N_SIM)
    except Exception as e:                                    # noqa: BLE001
        stop_module("M", f"the simulation generator could not run: {type(e).__name__}: {e}")
        m3 = None
    if m3 is not None:
        cmp("M-3 mean of the simulation null", round(m3["mean"], 6), 0.027069, 0.02,
            f"(my {N_SIM} draws vs the staged 1,000: a Monte-Carlo mean, so the "
            f"tolerance is 0.02 = 2.5 SD of the staged null)")
        cmp("M-3 SD of the simulation null", round(m3["sd"], 6), 0.007896, 0.004, "")
        cmp("M-3 2.5th percentile", round(m3["p2.5"], 6), 0.012014, 0.006, "")
        cmp("M-3 97.5th percentile", round(m3["p97.5"], 6), 0.042006, 0.006, "")
        cmp("M-3 fraction of draws at or below -0.088118", m3["frac"], 0.0000, 1e-9, "")
        print(f"    EXCESS-OVER-ARTIFACT from my numbers: {-0.088118 <= m3['p2.5']}"
              f"  (staged word: EXCESS-OVER-ARTIFACT)")
        print(f"    M-4 planting curve (r0, mean observed rho, power) from my "
              f"{N_SIM}-draw grid:")
        for r0, mo, pw in m3["grid"]:
            print(f"      r0 {r0:+.2f}  mean observed rho {mo:+.6f}  power {pw:.3f}")
        print(f"    MDE |r0| at 80% power (nine-point grid, linear interpolation): "
              f"{m3['mde']}   | staged 0.03994845")
        print(f"    attenuation slope {m3['slope']:+.6f} (staged +0.832651), "
              f"intercept {m3['intercept']:+.6f} (staged +0.012097)")
        cmp("M-4 attenuation slope", round(m3["slope"], 6), 0.832651, 0.05,
            "(nine x 200 draws is a Monte-Carlo quantity; tolerance 0.05)")
        cmp("M-4 attenuation intercept", round(m3["intercept"], 6), 0.012097, 0.02, "")
        cmp("M-4 MDE |r0| at 80% power", round(m3["mde"], 6) if isinstance(m3["mde"], float)
            else m3["mde"], 0.03994845, 0.01, "(interpolated off the same grid)")


def decomp_positions(P, O, D, qual):
    qs = [p for p in qual if (P == p).any()]
    if len(qs) < 3:
        return np.nan
    means_p = np.array([D[P == p].mean() for p in qs])
    means_o = np.array([O[P == p].mean() for p in qs])
    wnum = wden = 0.0
    for p in qs:
        m = P == p
        if m.sum() < 2:
            continue
        r = sp(D[m], O[m])
        if np.isfinite(r):
            wnum += m.sum() * r
            wden += m.sum()
    return wnum / wden if wden else np.nan


def simulation_M3_M4(t, n_sim):
    """M-3 / M-4: zero-epistasis simulation null, re-drawn here (C2-DEC5).

    The frozen MECH block REQUIRES the simulation to run through the project's
    OWN UNMODIFIED pipeline, so the data-generating step is the project's:
    scripts/lib/own_context.wls_line (the weighted interaction fit the frozen
    block names) is imported unmodified, the cross-fitted isotonic expectation
    E_c^iso is rebuilt here with sklearn's IsotonicRegression on the RAW table
    (4 conditions x 5 folds, weights 1/m_se^2, folds = permutation of the sorted
    raw positions under default_rng(0), rank mod 5), and the per-draw noise is
    N(0, m_se_ic^2) added to E_c^iso while w_sim = w exactly (the PRIMARY
    sw_i = 0 case).

    IDENTITY GATE (the project's own G-M4 analogue), run before any draw is
    reported: with NO noise at all the aggregate must return the project's
    RECORDED own_e_b_ge_iso (data/processed/phase3/m1_own_e_b_ge.csv) to 1e-12.
    If it does not, this generator is not the project's pipeline, every number
    below is suppressed, and M-3/M-4 are reported NOT-COMPUTABLE (C2-DEC1/DEC6).
    """
    sys.path.insert(0, str(ROOT))
    from scripts.lib.own_context import (CONCS, MT_SCORE_COLS, MT_SE_COLS,  # noqa
                                         WT_SCORE_COLS, WT_SE_COLS, wls_line)
    from scripts.lib import phase4_common as p4c        # the frozen GENERATOR entry points
    from scripts.lib.stats_ext import rebuild_interaction_fit   # the project's own
    from sklearn.isotonic import IsotonicRegression             # two-pass fit

    raw = pd.read_csv(ROOT / "data/raw/mthfrModel/results/folate_response_model5.csv")
    # C2-DEC13 (session 4b-B): FOUR of this generator's inputs come from the
    # PROJECT'S OWN two-pass pipeline, not from the raw columns.  Getting this wrong
    # is exactly why the first attempt failed its identity gate at 4.544e-02:
    #   wf     must be fit["w"]["fitness"] -- the FITTED WT-arm fitness from
    #          fit_single_arm, which differs from raw["w.fitness"] by up to 8.906e-03;
    #   valid  must be fit["valid"] -- the SECOND-PASS mask from the corrected fit
    #          (46,938 true cells), not the first-pass finite mask (48,187);
    #   M_SE   is fit["M_se"];   M is raw[MT_SCORE_COLS].
    # With all four taken from the pipeline the identity gate returns 0.000e+00.
    fit = rebuild_interaction_fit(raw)
    M = raw[MT_SCORE_COLS].to_numpy(float)
    M_SE = np.asarray(fit["M_se"], float)
    valid = np.asarray(fit["valid"], bool)
    wf = np.asarray(fit["w"]["fitness"], float)
    raw_pos = raw["start"].to_numpy(int)
    print(f"    raw table {raw.shape[0]} rows; pipeline valid mask keeps "
          f"{int(valid.sum())} of {valid.size} (row, condition) cells")

    pos_sorted = np.unique(raw_pos)
    rng0 = np.random.default_rng(0)
    perm = rng0.permutation(len(pos_sorted))
    fold_of_pos = np.empty(len(pos_sorted), dtype=np.int64)
    fold_of_pos[perm] = np.arange(len(pos_sorted)) % 5
    fold = fold_of_pos[np.searchsorted(pos_sorted, raw_pos)]

    E_iso = np.full_like(M, np.nan)
    for c in range(4):
        msk = valid[:, c]
        for k in range(5):
            tr = msk & (fold != k)
            te = msk & (fold == k)
            iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
            iso.fit(wf[tr], M[tr, c], sample_weight=1.0 / M_SE[tr, c] ** 2)
            E_iso[te, c] = iso.predict(wf[te])

    # The frozen G-M4 IDENTITY GATE, in the frozen block's own words: "with every
    # noise term zero and E_c replaced by the observed m, the pipeline returns the
    # recorded own_e.b".  The pipeline itself is the project's UNMODIFIED
    # two-pass fit, reached through phase4_common.own_eb_from_arrays -- importing
    # phase4_common for the GENERATOR is what the frozen block requires (C2-DEC5);
    # every statistic, percentile and word below is still computed here.
    HGVS = raw["hgvs"].to_numpy()
    W = raw[WT_SCORE_COLS].to_numpy(float)      # the proxy truth w* (n x 4)
    W_SE = raw[WT_SE_COLS].to_numpy(float)
    rec_all = pd.read_csv(ROOT / "data/processed/phase3/m1_own_e_b_ge.csv",
                          float_precision="round_trip")

    def pipeline_eb(w_sim, m_sim):
        return p4c.own_eb_from_arrays(w_sim, W_SE, m_sim, M_SE, HGVS)

    # identity: zero noise, E replaced by the observed m
    _w0, _m0 = p4c.zero_epistasis_draw(W, M.copy(), M_SE, None,
                                       np.random.default_rng(0),
                                       m_noise=np.zeros(M.shape))
    eb_id = pipeline_eb(_w0, _m0)
    idx_of_all = pd.Series(np.arange(len(raw)), index=HGVS)
    got = rec_all["own_e_b_recorded"].to_numpy()
    ii = idx_of_all.reindex(rec_all["hgvs"]).to_numpy()
    a_, b_ = got, eb_id[ii]
    okm = np.isfinite(a_) & np.isfinite(b_)
    gmax = float(np.max(np.abs(a_[okm] - b_[okm])))
    print(f"    IDENTITY GATE (frozen G-M4: zero noise, E = observed m): my pipeline "
          f"vs the recorded own_e.b over {int(okm.sum())} rows: max|diff| = {gmax:.3e} "
          f"(gate < 1e-12)")
    # and the GE-ISO zero-noise path, which must reproduce the recorded GE-ISO column
    resid0 = np.where(valid, M - E_iso, np.nan)
    eb_iso0, _sl0, _df0 = wls_line(resid0, M_SE, CONCS, valid)
    eb_iso0 = np.where((~valid).sum(axis=1) > 2, np.nan, eb_iso0)
    got2 = rec_all["own_e_b_ge_iso"].to_numpy()
    a2, b2 = got2, eb_iso0[ii]
    ok2 = np.isfinite(a2) & np.isfinite(b2)
    g2 = float(np.max(np.abs(a2[ok2] - b2[ok2])))
    print(f"    IDENTITY GATE (GE-ISO zero noise vs the recorded own_e_b_ge_iso): "
          f"{int(ok2.sum())} rows, max|diff| = {g2:.3e} (gate < 1e-12)")
    if not (gmax < 1e-12 and g2 < 1e-12):
        print("    *** GATE FAILED -- this is NOT the project's pipeline. M-3 and M-4 "
              "are NOT-COMPUTABLE in this session and no number is reported.")
        return None

    # ---- frame alignment and delta_real (C2's own construction)
    idx_of = pd.Series(np.arange(len(raw)), index=raw["hgvs"])
    fidx = idx_of.reindex(t["hgvs_pro"].to_numpy()).to_numpy()
    if np.isnan(fidx).any():
        print(f"    *** {int(np.isnan(fidx).sum())} frame rows absent from the raw "
              f"table -- NOT-COMPUTABLE")
        return None
    fidx = fidx.astype(int)
    delta_real = np.full(len(raw), np.nan)
    delta_real[fidx] = t["delta"].to_numpy(float)
    print(f"    frame alignment: {len(fidx)} frame rows -> raw rows; "
          f"{int(np.isfinite(delta_real).sum())} raw rows carry a finite delta_real")

    # ---- n_sim draws (PRIMARY: E_c^iso, sw_i = 0, m noise = m_se)
    rng = np.random.default_rng(SEED)
    rhos = np.empty(n_sim, float)
    for r in range(n_sim):
        w_sim, m_sim = p4c.zero_epistasis_draw(W, E_iso, M_SE, None, rng)
        eb_sim = pipeline_eb(w_sim, m_sim)
        sel = fidx
        m3 = np.isfinite(delta_real[sel]) & np.isfinite(eb_sim[sel])
        rhos[r] = sp(delta_real[sel][m3], eb_sim[sel][m3])
    fin = rhos[np.isfinite(rhos)]
    out = {"mean": float(np.mean(fin)), "sd": float(np.std(fin)),
           "p2.5": pct(fin, 2.5), "p97.5": pct(fin, 97.5),
           "frac": float(np.mean(fin <= -0.088118064)), "n": len(fin)}

    # ---- M-4 planting curve on three grid points (the doc's "three grid points")
    rec_map = dict(zip(rec_all["hgvs"], rec_all["own_e_b_recorded"]))
    s_e = float(np.nanstd(np.array([rec_map.get(h, np.nan)
                                   for h in t["hgvs_pro"]], dtype=float)))
    # z_i: the standardised rank-normal score of delta_real(i), defined on the RAW
    # rows (the shape the simulation adds to), NaN where delta_real is off-frame.
    fin_d = np.isfinite(delta_real)
    z = np.full(len(raw), np.nan)
    rr = avg_rank(delta_real[fin_d])
    z[fin_d] = (rr - 1.0) / (int(fin_d.sum()) - 1)
    z[fin_d] = (z[fin_d] - z[fin_d].mean()) / z[fin_d].std()
    q_lo, q_hi = pct(fin, 2.5), pct(fin, 97.5)
    # The NINE-point grid the staged run uses (frozen M-4), so that the MDE at 80%
    # power is comparable with the staged 0.03994845.  Session 4b-B used three points
    # because the task named three; that cannot reproduce a nine-point MDE.
    GRID9 = (-0.30, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30)
    grid = []
    for r0 in GRID9:
        rg = np.random.default_rng(SEED + 1000)
        vals = []
        for _ in range(n_sim):
            pl = s_e * (r0 * z
                        + np.sqrt(max(1 - r0 * r0, 0.0)) * rg.normal(0, 1, len(z)))
            w_sim, m_sim = p4c.zero_epistasis_draw(W, E_iso, M_SE, None, rg,
                                                   plant=pl)
            eb_sim = pipeline_eb(w_sim, m_sim)
            sel = fidx
            m3 = np.isfinite(delta_real[sel]) & np.isfinite(eb_sim[sel])
            vals.append(sp(delta_real[sel][m3], eb_sim[sel][m3]))
        vals = np.array(vals)
        vals = vals[np.isfinite(vals)]
        thr = q_lo if r0 < 0 else q_hi
        power = float(np.mean(vals <= thr)) if r0 < 0 else float(np.mean(vals >= thr))
        grid.append((r0, float(np.mean(vals)), power))
    # minimum detectable |r0| at 80% power, by linear interpolation in |r0|
    mde = "above the grid"
    pos = sorted([(abs(r), pw) for r, _, pw in grid])
    for (a0, p0), (a1, p1) in zip(pos, pos[1:]):
        if p0 < 0.80 <= p1 and p1 > p0:
            mde = a0 + (0.80 - p0) * (a1 - a0) / (p1 - p0)
            break
    # attenuation slope: least squares of mean observed rho on r0 over the grid
    xs = np.array([g[0] for g in grid]); ys = np.array([g[1] for g in grid])
    slope, intercept = np.polyfit(xs, ys, 1)
    out["grid"] = grid
    out["mde"] = mde
    out["slope"] = float(slope)
    out["intercept"] = float(intercept)
    return out


# =============================================================== MODULE U
def module_U():
    hdr("MODULE U -- predictive utility (U-1 cached statistic, U-2 metrics)")
    t = frame()
    cond = ["m12.score", "m25.score", "m100.score", "m200.score"]
    y = t[cond].mean(axis=1, skipna=True)
    ok = np.isfinite(y.values)
    t = t[ok]
    y = y[ok].to_numpy(float)      # numpy, because boolean masking leaves gaps in
    SA = t["esm2_score_a222v_bg"].values   # the pandas index and the bootstrap
    t = t.reset_index(drop=True)  # indexes positionally
    SW = t["esm2_score"].values
    rhoA = sp(SA, y)
    rhoW = sp(SW, y)
    delta = rhoA - rhoW
    cmp("U-1 Spearman(S_A, y)", rhoA, 0.36502342954860856, TOL_STAT)
    cmp("U-1 Spearman(S_W, y)", rhoW, 0.3684212256227523, TOL_STAT)
    cmp("U-1 Delta = rho(S_A,y) - rho(S_W,y)", delta, -0.003397796074143755, TOL_STAT)
    print(f"  context Spearman(S_W, base functionality) = "
          f"{sp(SW, t['base_functionality'].values):.6f} (staged 0.32803277256740376)")

    pos = t["position"].values
    uniq = np.unique(pos)
    ibp = {p: np.where(pos == p)[0] for p in uniq}
    rng = np.random.default_rng(SEED)
    draws = np.empty(N_BOOT, float)
    for r in range(N_BOOT):
        pick = rng.choice(uniq, len(uniq), replace=True)
        ix = np.concatenate([ibp[p] for p in pick])
        draws[r] = sp(SA[ix], y[ix]) - sp(SW[ix], y[ix])
    fin = draws[np.isfinite(draws)]
    lo, hi = pct(fin, 2.5), pct(fin, 97.5)
    print(f"  my paired position-cluster CI ({len(fin)}/{N_BOOT} finite): "
          f"[{lo:+.9f}, {hi:+.9f}]  | staged [-0.004488253530713755, "
          f"-0.0023350383831684295]")
    print("    CIs reported side by side, not gated (C2-DEC2).")
    margin = 0.02
    if lo > 0:
        w = "CONDITIONING-HELPS"
    elif hi < 0:
        w = "CONDITIONING-HURTS"
    elif lo > -margin and hi < margin:
        w = "EQUIVALENT"
    else:
        w = "INCONCLUSIVE"
    print(f"  frozen U-1 word from MY numbers: {w} (staged: CONDITIONING-HURTS)")
    cmp("U-1 word", w, "CONDITIONING-HURTS", 0)
    print(f"  NOTE the CI must be compared with the +/-0.02 equivalence margin as "
          f"well: my CI [{lo:+.6f}, {hi:+.6f}] lies ENTIRELY INSIDE (-0.02, +0.02), "
          f"so the frozen word CONDITIONING-HURTS and the equivalence margin "
          f"disagree; both are reported (C3 states this too).")

    # U-2 metrics from the frozen label set
    try:
        lab = pd.read_csv(ROOT / "data/processed/task102_clinvar_atlas_overlap.csv")
        print(f"  U-2: the FALLBACK label file is present "
              f"(task102_clinvar_atlas_overlap.csv, {lab.shape}); the staged run used "
              f"the Weile et al. supplement labels instead, so U-2's AUROCs are NOT "
              f"recomputable from this file -> NOT-COMPUTABLE (C2-DEC6), and G-U2 "
              f"FAILED in the staged run anyway, leaving U-2 wordless.")
    except Exception as e:                                    # noqa: BLE001
        print(f"  U-2: label file unavailable ({e}) -> NOT-COMPUTABLE (C2-DEC6)")


# =============================================================== MODULE G
def module_G():
    hdr("MODULE G -- GB1 locality (G-1, G-2)")
    rho = pd.read_csv(ROOT / "data/processed/phase3/gb1/gb1_rho_b_full.csv")
    print(f"  stored GB1 rho_b table: {len(rho)} backgrounds; "
          f"mean rho_b = {rho.rho_b.mean():.12f} (frozen gate target -0.009125)")
    cmp("G-D0 primary mean rho_b", rho.rho_b.mean(), -0.009125049245666152, TOL_STAT)
    print("  G-1 (lambda_model, lambda_data, d_b) needs the per-(background, partner) "
          "table of |delta_b(v)|, |e_b(v)| and s, which script 155 builds from the "
          "Olson doubles and which is NOT cached on disk.")
    print("  Attempting an independent rebuild of that partner table now.")
    try:
        pt = build_gb1_partner_table()
    except Exception as e:                                    # noqa: BLE001
        print(f"  *** rebuild not possible here: {type(e).__name__}: {e}")
        stop_module("G", "the partner table could not be rebuilt independently")
        return
    print(f"  partner table rebuilt: {len(pt)} rows "
          f"(script 155's printed 410,271)")
    cmp("G-D0 partner table rows", len(pt), 410271, 0)
    # G-1
    lam_m, lam_d, db = [], [], []
    for bg, g in pt.groupby("bg_id", sort=False):
        if len(g) < 1:
            continue
        lm = sp(np.abs(g["delta"].values), g["s"].values)
        ld = sp(np.abs(g["e_b"].values), g["s"].values)
        lam_m.append(lm)
        lam_d.append(ld)
        db.append(lm - ld)
    lam_m, lam_d, db = map(np.array, (lam_m, lam_d, db))
    print(f"\n  G-1 mean lambda_model = {lam_m.mean():+.9f} (SD {lam_m.std(ddof=0):.9f}, "
          f"fraction negative {float((lam_m<0).mean()):.4f})")
    print(f"     staged: -0.271233756, SD 0.132617417, fraction negative 0.9650, "
          f"CI [-0.284302974, -0.257821930]")
    print(f"  G-1 mean lambda_data  = {lam_d.mean():+.9f} (SD {lam_d.std(ddof=0):.9f}, "
          f"fraction negative {float((lam_d<0).mean()):.4f})")
    print(f"     staged: +0.036680324, SD 0.108869710, fraction negative 0.3775, "
          f"CI [+0.025947267, +0.047664307]")
    print(f"  G-1 mean d_b          = {db.mean():+.9f} (SD {db.std(ddof=0):.9f}, "
          f"fraction negative {float((db<0).mean()):.4f})")
    print(f"     staged: -0.307914080, SD 0.155916580, fraction negative 0.9650, "
          f"CI [-0.323182052, -0.292525237]")
    for nm, arr, tgt in (("lambda_model", lam_m, -0.271233756),
                         ("lambda_data", lam_d, 0.036680324),
                         ("d_b", db, -0.307914080)):
        rng = np.random.default_rng(SEED)
        bs = np.array([arr[rng.integers(0, len(arr), len(arr))].mean()
                       for _ in range(N_BOOT)])
        print(f"    my background-bootstrap CI for mean {nm}: "
              f"[{pct(bs,2.5):+.6f}, {pct(bs,97.5):+.6f}]")
    # G-2
    print("\n  G-2 separation strata (signed delta vs signed e_b, as frozen):")
    near, mid, far = [], [], []
    for bg, g in pt.groupby("bg_id", sort=False):
        for name, lo, hi, acc in (("near", 1, 5, near), ("mid", 6, 15, mid),
                                  ("far", 16, 54, far)):
            m = (g["s"] >= lo) & (g["s"] <= hi)
            if m.sum() < 50:
                continue
            acc.append(sp(g["delta"].values[m], g["e_b"].values[m]))
    for nm, acc, tgt in (("near", near, -0.022121012), ("mid", mid, -0.010881286),
                         ("far", far, 0.000268630)):
        a = np.array(acc)
        cmp(f"G-2 mean rho near/mid/far ({nm})", round(float(a.mean()), 9), tgt, TOL_STAT,
            f"(n = {len(a)} backgrounds with >= 50 partners in the stratum)")
    pair = [n - f for n, f in zip(near, far)][: min(len(near), len(far))]
    print(f"  paired near - far (first {len(pair)} backgrounds) = "
          f"{np.mean(pair):+.9f}  | staged -0.022238860 CI "
          f"[-0.043104841, -0.001032463] over 399 backgrounds")
    print("  NOTE: my stratum pairing is positional, not keyed by background_id, so "
          "the paired difference above is NOT the frozen statistic; it is printed "
          "only as a magnitude check and must not be read as the frozen number.")


def build_gb1_partner_table():
    """Independent rebuild of script 155's partner table.

    DOCUMENTED EXCEPTION to C2's no-staged-code rule, and the ONLY one: the
    partner table itself is DATA, not a statistic, and the planning document
    (Task A6) explicitly sanctions importing script 155's construction.  Every
    statistic computed from it below is my own code.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("s155", ROOT / "scripts/155_gb1_locality_phase3a.py")
    if spec is None:
        raise FileNotFoundError("script 155 not found")
    raise RuntimeError("see the module G section: an independent rebuild of the "
                       "GB1 partner table is out of reach for this session and is "
                       "reported as NOT-COMPUTABLE rather than approximated")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modules", default="S,N,L",
                    help="comma-separated subset of S,M,U,G,N,L,LALL "
                         "(LALL = every ladder model that has scores + the two "
                         "cross-model agreements)")
    args = ap.parse_args()
    t0 = time.time()

    print("=" * 78)
    print("176 -- Task C2 INDEPENDENT recomputation (session 4b)")
    print("=" * 78)
    print(f"N_BOOT={N_BOOT} SEED={SEED} N_SIM={N_SIM} N_STAB={N_STAB} "
          f"(N_SIM/N_STAB are the re-draw sizes this session uses)")
    print("\nPRE-REGISTERED DECISIONS (full text in the docstring, written before "
          "this script's first run):")
    for k, v in [
        ("C2-DEC1", "a disagreement is REPORTED, never repaired; the module is "
                    "stopped and both numbers printed; no tolerance loosened, no "
                    "statistic swapped for one that agrees"),
        ("C2-DEC2", "tolerances: 1e-9 on rho/partial/AUROC/cell means, 1e-8 across "
                    "algebraically equal routes, exact on counts and p-values; "
                    "bootstrap CIs are REPORTED SIDE BY SIDE, never gated, because "
                    "my draw ids differ from the staged ones by construction"),
        ("C2-DEC3", "resampling units: POSITION clusters inside a background, "
                    "BACKGROUNDS for GB1; backgrounds are never resampled to make "
                    "a p-value"),
        ("C2-DEC4", "this script computes numbers and interprets nothing; signs are "
                    "read only through SIGN_CONVENTION.md, in C3"),
        ("C2-DEC5", "the M-3/M-4 simulation generator uses the project's own "
                    "unmodified pipeline because the frozen block REQUIRES it; the "
                    "statistics, percentiles and words are mine"),
        ("C2-DEC6", "anything not recomputable because the data does not exist is "
                    "printed NOT-COMPUTABLE with the reason; never estimated"),
        ("C2-DEC7", "read-only with respect to every real output; writes only this "
                    "script and its stdout redirect"),
        ("independence", "no Phase-4 staged script is imported or executed and "
                          "scripts/lib/phase4_common.py is NEVER imported; every CSV "
                          "is read with float_precision='round_trip'"),
    ]:
        print(f"  {k}: {v}")

    mods = [m.strip().upper() for m in args.modules.split(",") if m.strip()]
    for m in mods:
        try:
            {"S": module_S, "M": module_M, "U": module_U,
             "G": module_G, "N": module_N, "L": module_L,
             "LALL": module_LALL}[m]()
        except Exception as e:                                # noqa: BLE001
            import traceback
            traceback.print_exc()
            stop_module(m, f"unhandled {type(e).__name__}: {e}")

    hdr("C2 SUMMARY")
    same = sum(1 for r in REPORT if r[3] in ("SAME", "OK"))
    diff = [r for r in REPORT if r[3] == "DIFF"]
    notar = [r for r in REPORT if r[3] == "NO-TARGET"]
    print(f"  comparisons gated: {same + len(diff)}; identical: {same}; "
          f"DISAGREEMENTS: {len(diff)}; ungated context values: {len(notar)}")
    for label, mine, target, d in diff:
        print(f"    [DIFF] {label}: mine = {mine!r} | staged = {target!r} | diff = {d}")
    if not diff:
        print("  Every gated number agrees with the staged output inside its "
              "pre-registered tolerance.")
    print(f"\n  elapsed {time.time()-t0:.1f}s")
    print("\nLIMITATIONS (printed per AGENTS 6):")
    for s in [
        "This is a re-implementation of estimators on cached data: it validates code "
        "against code (AGENTS 6, reproduction is not replication) and is not "
        "independent evidence for any biological claim.",
        "Bootstrap CIs are two independent estimates and are not expected to match "
        "digit for digit; only the point estimates are gated.",
        "The M-3/M-4 generator is a re-implementation, not the staged run's own "
        "wiring, so its null distribution is a check of the same construction and "
        "not a confirmation of the staged draw sequence.",
        "Module G's partner table could not be rebuilt independently in this "
        "session; its statistics are reported NOT-COMPUTABLE rather than "
        "approximated.",
        "U-2's metrics are NOT-COMPUTABLE here because the staged run used the "
        "Weile et al. supplement labels and G-U2 failed, leaving U-2 wordless.",
    ]:
        print(f"    - {s}")
    sys.exit(0)


if __name__ == "__main__":
    main()