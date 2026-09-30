"""Script 138 -- Phase 2 diagnostics II Task D10: joint adjustment for shift
and distance, neighbourhood rank fractions, and partial rank correlations.

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome.  The three outcome
words reserved for the frozen test are not used as the label for any result
computed here.  p_spec_adj is a descriptive companion to the frozen p_spec.

A222V SITS AT THE EDGE OF THE DISTANCE RANGE -- STATED FIRST, BECAUSE IT
DRIVES EVERY CHOICE BELOW
-------------------------------------------------------------------------
Distance is SEQUENCE distance dist_b = |position_b - 222|.  A222V has
dist = 0.  The smallest null distance is 2 (AV_220); the largest is 433
(AV_655).  So A222V is at the exact boundary of the observed range: any
covariate function of distance is being evaluated at a point no null can
reach, which makes A222V's prediction an EXTRAPOLATION in every variant that
includes a distance term.  This is printed with the leverage (hat) value and
the clamped sensitivity below, and it is a limitation on D10a, not a reason
to drop the distance term.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
----------------------------------------------------
D10a JOINT OLS.  Primary: rho ~ a + c1*mean|delta| + c2*log1p(dist), fit on
  N (the 78 nulls); leave-one-out residuals for the nulls; out-of-sample
  residual for A222V (A222V is not in the fit) -- exactly D9's primary, so
  A222V and the nulls are exchangeable.  log1p is chosen because the gradient
  is expected to be steep near 222 and flat far away, and it is DEFINED AT
  0, which linear dist is not in a bounded-range sense.
  DISCLOSED SENSITIVITIES, all reported, NONE selected:
    (i)   linear dist instead of log1p(dist);
    (ii)  CLAMPED -- A222V evaluated at dist = 2 (the null minimum) instead
          of 0, which removes the extrapolation.  Nulls are UNCHANGED (their
          distances are real).  This is a one-line change to one covariate
          value and is labelled as such in the output;
    (iii) shift-only (= D9 primary), printed for side-by-side.
  For each: p_spec_adj and the at-or-below nulls, both views.

D10b NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals.  Among the k
  nearest nulls by sequence distance (k = 10 and 20, both reported, neither
  selected; ties by ascending bg_id), A222V's rank fraction
  (1 + #{r_b <= r_A}) / (1 + k) on both views.
  *** RANK FRACTIONS, NOT TESTS.  n is tiny; these are descriptive. ***

D10c PARTIAL RANK CORRELATIONS across N (78):
  Spearman(rho, dist | mean|delta|)  and  Spearman(rho, mean|delta| | dist),
  via the standard partial-correlation formula applied to the pairwise
  Spearman coefficients:
      r_xy.z = (r_xy - r_xz*r_yz) / sqrt((1 - r_xz^2)(1 - r_yz^2))
  Uncertainties: BACKGROUND-level bootstrap 95% CI, 10,000 draws, SEED=0.
  *** NO PERMUTATION p IS COMPUTED, AND NONE MAY BE. ***  A partial
  correlation is a function of THREE correlations; shuffling ONE variable
  and recomputing it does not produce a null distribution for the partial
  statistic, because the conditioning variable is left unpermuted and the
  two remaining correlations are not independent under the shuffle.  A naive
  shuffle is invalid here, so the bootstrap CI is the whole of the
  uncertainty statement and is labelled as a CI on a descriptive coefficient.
  Purpose (stated in the plan): which axis carries the association once the
  other is held fixed.

RESAMPLING UNIT -- READ THIS
----------------------------
BACKGROUND, for D10c ONLY.  The statistic is one number per background
(rho_b, mean|delta_b, dist_b are all per-background), so the only thing a
bootstrap can legitimately resample is WHICH BACKGROUNDS WERE DRAWN.  Each
draw resamples background indices with replacement (n = len draws) and
recomputes the statistic; each background's already-computed rho_b,
mean|delta| and dist are held FIXED within a draw.  Nothing is re-derived:
no rho_b is recomputed and no score is re-read on any draw.  10,000 draws,
SEED=0.  This is NOT script 125's position-cluster resampling unit and the
two are not interchangeable.
D10a and D10b perform NO RESAMPLING: they are deterministic OLS fits and
exact rank counts.  Their `p_spec_adj` values have no Monte-Carlo component.

LIMITS (AGENTS 6; AGENTS 4 on a covariate built from the same quantities)
-------------------------------------------------------------------------
* PARTIAL CONSTRUCTIONAL OVERLAP: mean|delta| and rho_b are both functions of
  the SAME delta_b (D9's limit, carried forward unchanged).
* dist is SEQUENCE distance.  Residues 440 apart in sequence can be adjacent
  in the folded structure.  D11 repeats this axis in 3D; nothing here
  licenses a spatial reading.
* A222V's distance covariate is an EXTRAPOLATION in every variant with a
  distance term (dist = 0, null minimum 2).  The clamped variant exists for
  exactly this and is reported, not selected.
* The neighbourhood rank fractions in D10b are rank counts with n = 10 and
  20.  They are not tests and their denominators are tiny by construction.
* D10c's CIs are background-level and do NOT model the fact that the 96
  rho_b share one y-vector (own_e_b) and are mutually correlated; if
  anything the CI is optimistic about that.  Disclosed, not corrected.
* Leave-one-out residuals are exact but not exchangeable draws from a common
  population (D9's limit, carried forward).

WORDING
-------
Adjusted p_spec is compared to the frozen NUMERIC thresholds and reported
only as "at or below" or "above" each.

Usage:
  N_BOOT=10000 SEED=0 venv/bin/python3 scripts/138_phase2_diag2_joint.py
"""

import hashlib
import importlib.util
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
FROZEN_P_FULL = 0.05
FROZEN_P_H = 0.10
NEIGH_K = (10, 20)

t0 = time.time()


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def load_s134():
    s = importlib.util.spec_from_file_location(
        "s134", ROOT / "scripts/134_phase2_diag_shift_magnitude.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def fit_predict(y, X, x_new):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, beta[0] + X[:, 1:] @ beta[1:] if X.shape[1] > 1 else \
        beta[0] + beta[1] * x_new


def design(feats, vals):
    n = len(vals[0])
    return np.column_stack([np.ones(n)] + list(vals))


def loo_variant(view, RHO, mad, mad_a, N_ids, cov_names, cov_of,
                cov_of_A, s134):
    """Leave-one-out residuals on N.  cov_of(b) -> np.array of the background's
    covariates (length p); cov_of_A -> A222V's covariate array.  A222V is not
    in any fit, so its residual is out-of-sample exactly as each null's is.
    Returns (r_b dict, r_A, meta)."""
    rhoN = np.asarray([RHO[view][b] for b in N_ids], float)
    cov = np.array([np.asarray(cov_of(b), float) for b in N_ids])   # n x p
    Xb = np.column_stack([np.ones(len(N_ids)), cov])
    r = {}
    for i, b in enumerate(N_ids):
        keep = [j for j in range(len(N_ids)) if j != i]
        beta, *_ = np.linalg.lstsq(Xb[keep], rhoN[keep], rcond=None)
        pred = beta[0] + float(np.dot(beta[1:],
                                      np.asarray(cov_of(b), float)))
        r[b] = RHO[view][b] - pred
    beta, *_ = np.linalg.lstsq(Xb, rhoN, rcond=None)
    predA = beta[0] + float(np.dot(beta[1:], np.asarray(cov_of_A, float)))
    r_A = mad_a["rho"][view] - predA
    return r, r_A, dict(beta=beta, n_fit=len(N_ids))


def verdict(p, view):
    thr = FROZEN_P_FULL if view == "full" else FROZEN_P_H
    return ("AT OR BELOW" if p <= thr else "ABOVE"), thr


def main():
    banner("D10 -- JOINT ADJUSTMENT, NEIGHBOURHOOD RANKS, PARTIAL "
           "CORRELATIONS (script 138)")
    print("SCOPE: descriptive.  p_spec_adj is a companion to the frozen "
          "p_spec, never a replacement.  No outcome word is used as a label.")
    print("RESAMPLING UNIT: BACKGROUND for D10c only (10,000 draws, SEED=0, "
          "per-background rho_b / mean|delta| / dist held FIXED).  D10a and "
          "D10b do NO resampling -- deterministic fits and exact rank counts.")
    print(f"  N_BOOT={N_BOOT} SEED={SEED}")

    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    if sha != TABLE_SHA:
        print(f"\nINPUT GATE FAIL: table sha256 {sha} != {TABLE_SHA}")
        sys.exit(1)
    print(f"\nINPUT GATE PASS: table sha256 = {sha}")

    s134 = load_s134()
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    N_ids = list(A.N_IDS)
    bgs = list(A.bgs)
    nN = len(N_ids)
    RHO = {"full": {b: float(A.point[b]) for b in bgs},
           "H": {b: float(point_h[b]) for b in bgs}}
    rho_a = {"full": float(A.rho_a222v), "H": float(rho_a_H)}
    ARM = {b: table.loc[b, "arm"] for b in bgs}
    DIST = {b: int(table.loc[b, "dist_222"]) for b in bgs}
    DIST_A = 0                      # A222V's own position IS 222

    mad = {"full": {}, "H": {}}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    mad_a = {}
    for view in ("full", "H"):
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))
    mad_a["rho"] = rho_a

    # =====================================================================
    banner("A222V IS AT THE EDGE OF THE DISTANCE RANGE -- stated before any "
           "adjustment is reported", "-")
    nd = np.array([DIST[b] for b in N_ids])
    print(f"  sequence distance dist_b = |position_b - 222|")
    print(f"    A222V               dist = {DIST_A}")
    print(f"    null set N          dist min = {nd.min()} ({[b for b in N_ids if DIST[b]==nd.min()]}), "
          f"median = {int(np.median(nd))}, max = {nd.max()} "
          f"({[b for b in N_ids if DIST[b]==nd.max()]})")
    print(f"    -> A222V's distance covariate is an EXTRAPOLATION in every "
          f"variant with a distance term: no null can reach dist = 0.")
    print("    This is why the CLAMPED sensitivity below (A222V evaluated at "
          "dist = 2, the null minimum) is reported.  It is a sensitivity, "
          "NOT a selection.")

    # leverage of A222V in the D10a primary design
    X = np.column_stack([np.ones(nN),
                         np.array([mad["full"][b] for b in N_ids]),
                         np.array([np.log1p(DIST[b]) for b in N_ids])])
    xA = np.array([1.0, mad_a["full"], np.log1p(DIST_A)])
    XtX = np.linalg.pinv(X.T @ X)
    h_A = float(xA @ XtX @ xA)
    h_null = np.einsum("ij,jk,ik->i", X, XtX, X)
    print(f"\n  LEVERAGE (hat value) of A222V in the D10a primary design "
          f"(full frame; the H design gives the same covariate structure):")
    print(f"    h(A222V) at dist = 0          = {h_A:.6f}")
    print(f"    h(A222V) at dist = 2 (clamped)= "
          f"{float(np.array([1.0, mad_a['full'], np.log1p(2.0)]) @ XtX @ np.array([1.0, mad_a['full'], np.log1p(2.0)])):.6f}")
    print(f"    null leverage h_b: mean = {h_null.mean():.6f}, "
          f"max = {h_null.max():.6f} ({[N_ids[i] for i in np.argsort(-h_null)[:3]]}), "
          f"min = {h_null.min():.6f}")
    print(f"    the mean leverage of a {X.shape[1]}-parameter fit on "
          f"{nN} points is p/n = {X.shape[1] / nN:.6f}")
    print(f"    -> A222V's leverage at dist = 0 is "
          f"{'ABOVE' if h_A > h_null.max() else 'within'} the null leverage "
          f"range; the clamped value is "
          f"{'inside' if float(np.array([1.0, mad_a['full'], np.log1p(2.0)]) @ XtX @ np.array([1.0, mad_a['full'], np.log1p(2.0)])) <= h_null.max() else 'outside'} "
          f"it.  A high leverage point's residual is partly extrapolation, "
          f"not evidence.")

    # =====================================================================
    banner("D10a -- JOINT OLS: rho ~ a + c1*mean|delta| + c2*<distance>", "-")
    print("PRIMARY: log1p(dist).  Fit on N (78); leave-one-out residuals for "
          "the nulls, out-of-sample for A222V (exactly D9's primary, so the "
          "two are exchangeable).")
    print("SENSITIVITIES, ALL REPORTED, NONE SELECTED: (i) linear dist; "
          "(ii) CLAMPED (A222V at dist = 2); (iii) shift-only = D9 primary.")

    VARIANTS = [
        ("PRIMARY  log1p(dist)", ["mean|delta|", "log1p(dist)"],
         lambda b, view: [mad[view][b], np.log1p(DIST[b])],
         lambda view: [mad_a[view], np.log1p(DIST_A)]),
        ("SENS (i)  linear dist", ["mean|delta|", "dist"],
         lambda b, view: [mad[view][b], float(DIST[b])],
         lambda view: [mad_a[view], float(DIST_A)]),
        ("SENS (ii) CLAMPED: A222V at dist = 2", ["mean|delta|", "log1p(dist)"],
         lambda b, view: [mad[view][b], np.log1p(DIST[b])],
         lambda view: [mad_a[view], np.log1p(2)]),
        ("SENS (iii) shift-only (= D9 primary)", ["mean|delta|"],
         lambda b, view: [mad[view][b]],
         lambda view: [mad_a[view]]),
    ]

    d10a_rows = []
    resid_primary = {}
    for name, cnames, covb, covA in VARIANTS:
        print(f"\n  === {name} ===")
        for view in ("full", "H"):
            r, r_A, meta = loo_variant(view, RHO, None, mad_a, N_ids,
                                       cnames,
                                       lambda b, _v=view, _f=covb:
                                       np.asarray(_f(b, _v), float),
                                       np.asarray(covA(view), float), s134)
            k = int(sum(1 for b in N_ids if r[b] <= r_A))
            p_adj = (1 + k) / (1 + nN)
            rank = 1 + int(sum(1 for b in N_ids if r[b] < r_A))
            at_or_below = sorted(b for b in N_ids if r[b] <= r_A)
            rel, thr = verdict(p_adj, view)
            beta = meta["beta"]
            print(f"    [{view}]  fit on n = {meta['n_fit']};  "
                  f"OLS coefficients: intercept {beta[0]:+.6f}  "
                  + "  ".join(f"{c} {beta[i + 1]:+.6f}"
                              for i, c in enumerate(cnames)))
            print(f"      A222V covariates = "
                  + ", ".join(f"{c} {v:.6f}"
                              for c, v in zip(cnames, covA(view))))
            print(f"      r_A = {r_A:+.6f};  "
                  f"#{{b in N: r_b <= r_A}} = {k} of {nN}")
            print(f"      p_spec_adj = (1 + {k})/(1 + {nN}) = {p_adj:.6f}"
                  f"   -> {rel} the frozen threshold {thr}")
            print(f"      A222V signed rank within N u {{A222V}} = {rank}/{nN + 1}")
            if at_or_below:
                print(f"      at or below r_A: "
                      + "; ".join(f"{b} ({ARM[b]}, d={DIST[b]}, "
                                  f"mean|d|={mad[view][b]:.6f}, r_b={r[b]:+.6f})"
                                  for b in at_or_below))
            else:
                print("      at or below r_A: NONE (k = 0, the floor 1/79)")
            d10a_rows.append(dict(name=name, view=view, k=k, p=p_adj, rel=rel,
                                  thr=thr, r_A=r_A, rank=rank, beta=beta))
            if name.startswith("PRIMARY"):
                resid_primary[view] = (dict(r), r_A)
        print()

    print(f"  {'variant':>38s} {'view':>5s} {'k':>3s} {'p_spec_adj':>11s} "
          f"{'r_A':>11s} {'rank':>7s}  vs frozen")
    for d in d10a_rows:
        print(f"  {d['name']:>38s} {d['view']:>5s} {d['k']:>3d} {d['p']:>11.6f} "
              f"{d['r_A']:+11.6f} {d['rank']:>4d}/{nN + 1}  {d['rel']} {d['thr']}")

    # =====================================================================
    banner("D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals",
           "-")
    print("*** RANK FRACTIONS, NOT TESTS.  n is tiny by construction; these "
          "are descriptive counts. ***")
    near_by_dist = sorted(N_ids, key=lambda b: (DIST[b], b))
    d10b_rows = []
    for kk in NEIGH_K:
        sub = near_by_dist[:kk]
        for view in ("full", "H"):
            r, r_A = resid_primary[view]
            k = int(sum(1 for b in sub if r[b] <= r_A))
            frac = (1 + k) / (1 + kk)
            names = sorted(b for b in sub if r[b] <= r_A)
            print(f"  k={kk:>2d} nearest ({view:>4s}):  # at or below = {k:>2d}"
                  f" of {kk}  ->  rank fraction (1 + {k})/(1 + {kk}) = "
                  f"{frac:.4f}"
                  + (f"   at or below: {', '.join(names)}" if names else
                     "   at or below: NONE"))
            d10b_rows.append(dict(k=kk, view=view, count=k, frac=frac,
                                  names=names))
    print(f"\n  the {NEIGH_K[1]} nearest by sequence distance: "
          f"{near_by_dist[:NEIGH_K[1]]}")
    print(f"  ties in dist within N present at the cut? "
          f"{'none' if len({DIST[b] for b in near_by_dist[:20]}) == 20 else 'yes'}"
          f" (tie-break by ascending bg_id is the pre-registered rule)")

    # =====================================================================
    banner("D10c -- PARTIAL RANK CORRELATIONS across N (78)", "-")
    print("  RESAMPLING UNIT: BACKGROUND.  Each draw resamples which of the "
          f"{nN} nulls were drawn, n = {nN} with replacement, and recomputes "
          "the statistic; each background's rho_b, mean|delta| and dist are "
          "held FIXED.  Nothing is re-derived.  N_BOOT = "
          f"{N_BOOT}, SEED = {SEED}.")
    print("  *** NO PERMUTATION p IS COMPUTED, AND NONE MAY BE. ***  A partial "
          "correlation is a function of THREE correlations; shuffling ONE "
          "variable leaves the conditioning variable unpermuted and the other "
          "two correlations are not independent under the shuffle, so the "
          "resulting distribution is not a null for the partial statistic.  "
          "A naive shuffle is invalid here.  The bootstrap CI below is the "
          "whole uncertainty statement.")

    def partial(x, y, z):
        rxy = float(spearmanr(x, y).statistic)
        rxz = float(spearmanr(x, z).statistic)
        ryz = float(spearmanr(y, z).statistic)
        den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
        return (rxy - rxz * ryz) / den, rxy, rxz, ryz

    rng = np.random.default_rng(SEED)
    d10c_rows = []
    for view in ("full", "H"):
        x = np.array([RHO[view][b] for b in N_ids], float)          # outcome
        m = np.array([mad[view][b] for b in N_ids], float)           # shift
        d = np.array([float(DIST[b]) for b in N_ids], float)         # distance

        obs, rxy, rxm, rmd = partial(x, m, d)      # rho ~ dist | mean|delta|
        obs2, rxy2, rxd, ryd = partial(x, d, m)    # rho ~ mean|delta| | dist

        draws1 = np.empty(N_BOOT, float)
        draws2 = np.empty(N_BOOT, float)
        for i in range(N_BOOT):
            idx = rng.integers(0, nN, nN)
            draws1[i] = partial(x[idx], m[idx], d[idx])[0]
            draws2[i] = partial(x[idx], d[idx], m[idx])[0]
        lo1, hi1, v1 = pdg.pct_ci(draws1)
        lo2, hi2, v2 = pdg.pct_ci(draws2)

        print(f"\n  [{view}]  n = {nN}")
        print(f"    pairwise Spearman(rho, mean|delta|) = {rxy:+.9f}   "
              f"Spearman(rho, dist) = {rxy2:+.9f}   "
              f"Spearman(mean|delta|, dist) = {rmd:+.9f}")
        print(f"    PARTIAL  Spearman(rho, dist | mean|delta|) = {obs:+.9f}")
        print(f"      background-level bootstrap 95% CI = [{lo1:+.6f}, "
              f"{hi1:+.6f}]  ({v1} usable draws)  "
              f"({'EXCLUDES ZERO' if (lo1 > 0 or hi1 < 0) else 'INCLUDES ZERO'})")
        print(f"    PARTIAL  Spearman(rho, mean|delta| | dist) = {obs2:+.9f}")
        print(f"      background-level bootstrap 95% CI = [{lo2:+.6f}, "
              f"{hi2:+.6f}]  ({v2} usable draws)  "
              f"({'EXCLUDES ZERO' if (lo2 > 0 or hi2 < 0) else 'INCLUDES ZERO'})")
        print(f"    no permutation p is reported for either -- see the "
              f"reasoning above")
        d10c_rows.append(dict(view=view, p1=obs, lo1=lo1, hi1=hi1,
                              e1=(lo1 > 0 or hi1 < 0), p2=obs2, lo2=lo2,
                              hi2=hi2, e2=(lo2 > 0 or hi2 < 0),
                              rxy=rxy, rxy2=rxy2, rmd=rmd))

    print(f"\n  side-by-side (which axis carries the association once the "
          f"other is held fixed?):")
    print(f"  {'view':>5s} {'rho~dist | mean|d|':>22s} {'CI':>26s} "
          f"{'excl0':>6s}   {'rho~mean|d| | dist':>22s} {'CI':>26s} {'excl0':>6s}")
    for d in d10c_rows:
        print(f"  {d['view']:>5s} {d['p1']:+22.6f} "
              f"[{d['lo1']:+.6f}, {d['hi1']:+.6f}] {str(d['e1']):>6s}   "
              f"{d['p2']:+22.6f} [{d['lo2']:+.6f}, {d['hi2']:+.6f}] "
              f"{str(d['e2']):>6s}")

    banner("D10 LIMITATIONS (printed, not only in the docstring)", "-")
    print("  A222V's distance covariate is an EXTRAPOLATION (dist = 0, null "
          "minimum 2) in every variant with a distance term; the CLAMPED "
          "sensitivity addresses this and is reported, not selected.  dist is "
          "SEQUENCE distance and licenses no spatial reading -- D11 is that "
          "task.  D10a's and D10b's p_spec_adj and rank fractions are "
          "deterministic OLS fits and exact rank counts with NO Monte-Carlo "
          "component; only D10c has resampling, and its unit is the "
          "BACKGROUND, which does NOT model the fact that the 96 rho_b share "
          "one y-vector and are mutually correlated (disclosed, not "
          "corrected).  D10c has NO permutation p by design and the reason is "
          "printed above.  PARTIAL CONSTRUCTIONAL OVERLAP: mean|delta| and "
          "rho_b are both functions of the same delta_b.  Nothing here is a "
          "decision rule and nothing frozen is redefined.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()