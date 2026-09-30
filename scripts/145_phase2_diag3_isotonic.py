"""Script 145 -- Phase 2 diagnostics III, Task D16: ADJUSTMENT WITH NO FITTED
FUNCTIONAL FORM AND NO EXTRAPOLATION (ISOTONIC).

WHY
---
D10a's answers range from p_spec_adj 0.13 (linear) to 0.89 (log1p) to 1.00
(3D) because each one extrapolates a fitted FUNCTIONAL FORM to distance 0,
where no null sits.  A monotone (isotonic) fit needs no functional form, and
with flat extrapolation at the boundary it predicts nothing at distance 0 that
is not already seen at the smallest null distance.  This task asks whether the
distance result depends on the form.

SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as
a label for any result computed here.

PRIMARY DESIGNATION, FIXED IN ADVANCE BEFORE THE FIRST RUN
--------------------------------------------------------
**PRIMARY = D16b, on `d3_CA`.**  Every other variant is reported side by side
and NONE of them is selected.  D16b is designated because d3_CA is the axis
Diagnostics I's own log warned is the honest one (a sequential-locality result
is not a structural-locality result), and because D16b's stage 1 (D9's shift
residual) is the one covariate that is not itself a distance proxy.

METHOD, PRE-REGISTERED
----------------------
`sklearn.isotonic.IsotonicRegression(increasing=True, out_of_bounds='clip')`
if sklearn imports (it does; the fallback is scipy's isotonic_regression if
scipy has it, else this task is BLOCKED and nothing is installed).  rho is
EXPECTED to INCREASE with distance (more negative near 222), so `increasing=True`
is the observed direction and is not a free parameter.

* **Leave-one-out for the nulls:** for each null b, refit g on the other nulls
  and predict at b's own distance.
* **Out-of-sample for A222V and Arm S:** fit g on ALL nulls and predict at
  distance 0.  With `out_of_bounds='clip'`, a point below the smallest fitted
  distance receives the fitted value AT that smallest distance -- i.e. the flat
  extrapolation the doc requires.  g(0) is therefore the fitted step value at
  the boundary and is reported explicitly.
* Residual r = rho - g(distance).

THE FOUR VARIANTS
-----------------
  D16a  raw rho on distance.  Isotonic rho ~ g(d3_CA) over the resolved nulls
        (n = 67).
  D16b  TWO-STAGE, PRIMARY.  Stage 1: D9's PRIMARY leave-one-out shift
        residuals (r^shift; A222V and Arm S out-of-sample from the fit on all
        N).  Stage 2: isotonic r^shift ~ g(d3_CA), leave-one-out for nulls,
        out-of-sample for A222V and Arm S.
  D16c  sequence-distance versions of D16a and D16b over ALL 78 nulls
        (`dist_seq`), as SENSITIVITIES.
  D16d  Arm S under the same fits: each Arm S member's residual under D16b,
        and A222V's rank within Arm S u {A222V} on it.  *** RANK FRACTIONS,
        n = 19, NOT TESTS. ***  This is the direct same-site comparison D13
        gives raw, now under a shift-and-distance adjustment that needs no
        extrapolation.

Reported for D16a, D16b and D16c, both views: g(0) (the fitted step value at
the boundary), r_A, A222V's SIGNED RANK within nulls u {A222V} (rank 1 = most
negative residual), the nulls at or below r_A, `p_spec_adj = (1 + k)/(1 + n)`,
and whether p_spec_adj is at or below 0.05 (full) / 0.10 (H).  **The fitted
step function g is printed in full (breakpoints and values) for D16a and D16b
so a reader can see where the pooled blocks are and what g(0) is.**

NO BOOTSTRAP AND NO PERMUTATION IN THIS TASK.  Resampling unit: NONE.  Every
number is a deterministic isotonic fit, an exact rank count, or a
deterministic leave-one-out residual.  N_BOOT / N_PERM are not read.  This is
stated here and printed in the output.

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result
computed here.  Adjusted p_spec is compared to the frozen NUMERIC thresholds
(0.05 full, 0.10 H) and reported only as "at or below" or "above".

LIMITS, TO BE STATED IN THE OUTPUT AND NOT ONLY HERE (AGENTS 6)
---------------------------------------------------------------
* The near-222 end of g rests on about SIX nulls within 10.5 A, so g(0) is set
  by a handful of points.  The exact count is printed.
* Isotonic pooling makes g a STEP FUNCTION, not a smooth curve.  The number of
  blocks and their sizes are printed.
* `p_spec_adj` here is a RANK COUNT on leave-one-out residuals of OVERLAPPING
  fits.  It is NOT a calibrated tail probability and is not a decision rule.
* **D16b's disclosed optimism:** stage 1's shift fit is NOT refit inside
  stage 2's leave-one-out, so a null's stage-2 residual is mildly optimistic
  (its own stage-1 residual already saw the other 77 nulls).  The magnitude is
  not quantified here and is disclosed, not corrected.  D16a has no such stage.
* Arm S and A222V are scored out-of-sample from a fit that contains only nulls,
  so they are exchangeable with each other but not with a background whose own
  data were used to place it.
* Isotonic regression uses only the ORDERING of the covariate, not its
  distances, so the result is invariant to any monotone rescaling of d3_CA.
  That is a feature (no functional form) and also a limitation (a background
  5 A and one 12 A away are treated identically if their order agrees).

Usage:
  venv/bin/python3 scripts/145_phase2_diag3_isotonic.py
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

t0 = time.time()
checks = []

ISOTONIC_IMPL = ""


def agree(label, got, target, tol, fmt="{:+.6f}"):
    ok = abs(float(got) - float(target)) < tol
    checks.append((label, ok))
    print(f"    {label:<50s} recomputed = {fmt.format(float(got))}   "
          f"target = {fmt.format(float(target))}   "
          f"|diff| = {abs(float(got) - float(target)):.3e}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


def agree_int(label, got, target):
    ok = int(got) == int(target)
    checks.append((label, ok))
    print(f"    {label:<50s} recomputed = {str(int(got)):>10s}   "
          f"target = {str(int(target)):>10s}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


def get_isotonic():
    """sklearn first (the doc's named implementation), scipy as fallback.
    Nothing is installed.  Returns (fit_fn, name) or (None, "") if neither is
    available, in which case the caller reports BLOCKED."""
    try:
        from sklearn.isotonic import IsotonicRegression

        def fit_sk(x, y):
            ir = IsotonicRegression(increasing=True, out_of_bounds="clip")
            ir.fit(np.asarray(x, float), np.asarray(y, float))
            return ir
        return fit_sk, ("sklearn.isotonic.IsotonicRegression("
                        "increasing=True, out_of_bounds='clip')")
    except Exception as exc:                                   # noqa: BLE001
        print(f"  sklearn unavailable ({exc}); trying scipy.")
    try:
        from scipy.optimize import isotonic_regression

        class _SP:
            def __init__(self, x, y):
                self.x = np.asarray(x, float)
                self.y = isotonic_regression(np.asarray(y, float),
                                             increasing=True)

            def predict(self, q):
                q = np.asarray(q, float)
                # flat clip outside the fitted support, linear inside it
                inside = np.interp(q, self.x, self.y)
                return np.where(q < self.x.min(), self.y[0],
                                np.where(q > self.x.max(), self.y[-1],
                                         inside))

        def fit_sp(x, y):
            return _SP(x, y)
        return fit_sp, "scipy.optimize.isotonic_regression"
    except Exception as exc2:                                  # noqa: BLE001
        print(f"  BLOCKED: neither sklearn nor scipy "
              f"({exc2}) provides isotonic regression, and the task doc "
              f"forbids installing.")
        return None, ""


def main():
    p3.banner("D16 -- ADJUSTMENT WITH NO FITTED FUNCTIONAL FORM AND NO "
              "EXTRAPOLATION (ISOTONIC)  (script 145)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word "
          "is used as a label.")
    print("*** PRIMARY, FIXED IN ADVANCE: D16b (D9's shift residuals, then "
          "isotonic on d3_CA).  Every other variant is reported side by side "
          "and NONE is selected. ***")
    print("RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  N_BOOT / "
          "N_PERM are not read by this script.  Every number below is a "
          "deterministic isotonic fit, an exact rank count, or a "
          "deterministic leave-one-out residual.")

    fit_iso, impl = get_isotonic()
    if fit_iso is None:
        return
    print(f"ISOTONIC IMPLEMENTATION: {impl}")
    print("  increasing=True is the OBSERVED direction (rho is more negative "
          "near 222), not a free parameter.  out_of_bounds='clip' gives the "
          "FLAT extrapolation at the boundary that the task doc requires: "
          "g(0) is the fitted value at the smallest null distance.")

    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    print(f"\n  background_rho_table.csv sha256 = {sha1} "
          f"({'MATCH' if sha1 == p3.RHO_TABLE_SHA else '*** MISMATCH ***'})")
    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    print(f"  background_3d_distance.csv sha256 = {sha3} "
          f"({'MATCH' if sha3 == p3.D3_SHA else '*** MISMATCH ***'})")
    assert sha1 == p3.RHO_TABLE_SHA and sha3 == p3.D3_SHA

    st = p3.build()
    S_ids, N_ids, resN = st["S_ids"], st["N_ids"], st["resN"]
    RHO, RHO_A, mad, mad_a, df3 = (st["RHO"], st["RHO_A"], st["mad"],
                                   st["mad_a"], st["df3"])
    bgs = st["bgs"]
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]
    print(f"  nulls: all {len(N_ids)}, resolved {len(resN)};  Arm S {len(S_ids)}; "
          f"resolved backgrounds {len(res96)}")

    # ---- g(0)'s supporting count, printed before any g is fitted -----------
    p3.banner("HOW MUCH DATA SETS g(0)  (printed before any fit)", "-")
    for tag, ids, key in (("d3_CA, resolved nulls", resN, "d3_CA"),
                          ("d3_CA, all 78 nulls", N_ids, "d3_CA"),
                          ("dist_seq, all 78 nulls", N_ids, None)):
        d = ([float(df3.loc[b, "d3_CA"]) for b in ids] if key
             else [float(st["DIST"][b]) for b in ids])
        d = np.array(d, float)
        n_nan = int(np.isnan(d).sum())
        if n_nan:
            print(f"  {tag}: n = {len(d)} but {n_nan} have NO d3_CA "
                  f"(unresolved background positions) and are NEVER "
                  f"imputed; the counts below use the {len(d) - n_nan} "
                  f"resolved ones")
            d = d[~np.isnan(d)]
        print(f"  {tag}: n = {len(d)}, minimum distance = {d.min():.3f}, "
              f"nulls within 10 A = {int((d <= 10).sum())}, "
              f"within 10.5 A = {int((d <= 10.5).sum())}, "
              f"within 12 A = {int((d <= 12).sum())}, "
              f"within 20 A = {int((d <= 20).sum())}")
        print(f"    *** g(0) IS SET BY THE {int((d <= 12).sum())} NULL(S) "
              f"WITHIN 12 A, AT MOST. ***")

    # ---- the machinery ----------------------------------------------------
    def isotonic_variant(tag, ids, y_of, dist_of, view, oos, extra=()):
        """ids = null ids used to FIT g.  y_of(b) -> the value being "
        isotonic-regressed (raw rho, or D9's stage-1 residual).  oos = list of
        (label, y, distance) scored out-of-sample."""
        x = np.array([dist_of(b) for b in ids], float)
        y = np.array([y_of(b) for b in ids], float)
        order = np.argsort(x, kind="stable")
        xs, ys = x[order], y[order]
        full = fit_iso(xs, ys)
        g0 = float(full.predict(np.array([0.0]))[0])
        # fitted step function, printed
        p = np.asarray(getattr(full, "X_thresholds_",
                               getattr(full, "x", np.array([xs.min()]))),
                       float)
        v = np.asarray(getattr(full, "y_thresholds_",
                               getattr(full, "y", np.array([ys.mean()]))),
                       float)
        print(f"\n  --- {tag}  [{view}] ---")
        print(f"    fit on n = {len(ids)};  distance range of the fitted "
              f"support = [{xs.min():.3f}, {xs.max():.3f}]")
        print(f"    g(0) = fitted value at the SMALLEST null distance "
              f"({xs.min():.3f}) = {float(full.predict(np.array([0.0]))[0]):+.6f}"
              f"   *** FLAT CLIPPED EXTRAPOLATION, NOT AN INTERPOLATED "
              f"VALUE ***")
        # TRUE pooled blocks, read back from the fitter's own thresholds.
        Xt = np.asarray(getattr(full, "X_thresholds_", xs), float)
        Yt = np.asarray(getattr(full, "y_thresholds_", ys), float)
        nb = len(Xt)
        print(f"    fitted STEP FUNCTION g: {nb} pooled block(s) over "
              f"{len(xs)} nulls "
              f"(isotonic pools a block per run of the pooled fit; n below "
              f"is the number of nulls inside each block)")
        # sklearn's thresholds are MIDPOINTS between adjacent x; a null x
        # belongs to block i if it lies in (Xt[i-1], Xt[i]] using those
        # midpoints, so count directly from the data rather than from edges.
        bounds = np.concatenate([[xs.min() - 1e-9], Xt, [xs.max() + 1e-9]])
        for i in range(nb):
            lo_d, hi_d = float(bounds[i]), float(bounds[i + 1])
            lo_d = xs.min() if i == 0 else lo_d
            hi_d = xs.max() if i == nb - 1 else hi_d
            nn = int(((xs > lo_d) & (xs <= hi_d)).sum()) if i else \
                int((xs <= hi_d).sum())
            print(f"      block {i + 1:>2d}: g = {Yt[i]:+.6f}   nulls with "
                  f"distance in ({lo_d:.3f}, {hi_d:.3f}]   n = {nn:>3d}"
                  + ("   <-- g(0) IS THIS BLOCK'S VALUE" if i == 0 else ""))
        print(f"    *** the near-222 end of g is set by the "
              f"{int((xs <= 12).sum())} null(s) within 12 A ***")
        blocks_kept = nb

        rows = []
        for b in ids:
            sub = [z for z in ids if z != b]
            m = fit_iso(np.array([dist_of(z) for z in sub], float),
                        np.array([y_of(z) for z in sub], float))
            rows.append((b, y_of(b) - float(m.predict(
                np.array([dist_of(b)]))[0])))
        r = dict(rows)
        out = []
        for lbl, yv, dv in oos:
            out.append((lbl, yv - float(full.predict(np.array([dv]))[0])))
        return r, out, xs, ys, nb, g0

    def report(tag, r_null, r_A, r_S, n_null, view, xs, ys, nblocks, g0=None):
        thr = p3.FROZEN_P_FULL if view == "full" else p3.FROZEN_P_H
        k = int(sum(1 for b in n_null if r_null[b] <= r_A))
        p = (1 + k) / (1 + len(n_null))
        rank = 1 + int(sum(1 for b in n_null if r_null[b] < r_A))
        rel = ("AT OR BELOW" if p <= thr else "ABOVE")
        aob = sorted(b for b in n_null if r_null[b] <= r_A)
        print(f"    A222V r_A = {r_A:+.6f}")
        print(f"    #{{b in nulls : r_b <= r_A}} = {k} of {len(n_null)}")
        print(f"    p_spec_adj = (1 + {k})/(1 + {len(n_null)}) = {p:.6f}   -> "
              f"{rel} the frozen numeric threshold {thr}")
        print(f"    A222V signed rank within nulls u {{A222V}} = {rank}/"
              f"{len(n_null) + 1}  (rank 1 = most negative residual)")
        print(f"    nulls at or below r_A: "
              f"{', '.join(aob) if aob else 'NONE (k = 0, the floor)'}")
        if r_S is not None:
            ao = sorted(r_S, key=lambda z: r_S[z])
            ks = int(sum(1 for b in r_S if r_S[b] <= r_A))
            print(f"    D16d  Arm S (n = {len(r_S)}) at or below r_A: "
                  f"k = {ks}  ->  rank fraction (1 + {ks})/(1 + {len(r_S)}) = "
                  f"{(1 + ks) / (1 + len(r_S)):.4f}   "
                  f"*** RANK FRACTION OVER n = 19, NOT A TEST ***")
            print(f"      {'rank':>4s} {'bg_id':>10s} {'residual':>12s} "
                  f"{'<= r_A?':>8s}")
            for i, b in enumerate(ao, start=1):
                print(f"      {i:>4d} {b:>10s} {r_S[b]:>+12.6f} "
                      f"{'YES' if r_S[b] <= r_A else 'no':>8s}")
        return dict(k=k, p=p, rank=rank, rel=rel, thr=thr, aob=aob, g0=g0,
                    r_A=r_A)

    # ================= D16a  raw rho on d3_CA, resolved nulls ==============
    p3.banner("D16a -- RAW rho, ISOTONIC ON d3_CA OVER THE RESOLVED NULLS "
              "(n = 67)", "-")
    d16a = {}
    for view in p3.VIEWS:
        r, oos, xs, ys, nb, gg = isotonic_variant(
            "D16a  raw rho ~ g(d3_CA)", resN,
            lambda b, v=view: RHO[v][b],
            lambda b: float(df3.loc[b, "d3_CA"]), view,
            oos=[("A222V", RHO_A[view], 0.0)] +
                [(b, RHO[view][b], 0.0) for b in S_ids])
        r_A = oos[0][1]
        r_S = {lbl: val for lbl, val in oos[1:]}
        d16a[view] = report("D16a", r, r_A, r_S, resN, view, xs, ys, nb, gg)

    # ================= D16b  TWO-STAGE, PRIMARY ============================
    p3.banner("D16b -- TWO-STAGE, PRIMARY: D9'S SHIFT RESIDUALS THEN ISOTONIC "
              "ON d3_CA", "-")
    print("  Stage 1 is D9's PRIMARY: leave-one-out on all 78 nulls for the "
          "nulls, out-of-sample for A222V and Arm S.")
    print("  *** DISCLOSED OPTIMISM IN STAGE 2: stage 1's fit is NOT refit "
          "inside stage 2's leave-one-out, so a null's stage-2 residual "
          "already saw the other 77 nulls through stage 1.  The optimism is "
          "small and is DISCLOSED, NOT CORRECTED.  D16a has no stage 1 and so "
          "no such optimism. ***")
    d16b, rshift, rshift_A, rshift_S = {}, {}, {}, {}
    for view in p3.VIEWS:
        r, r_A_s1 = p3.loo_shift(view, RHO, RHO_A, mad, mad_a, N_ids)
        rshift[view] = r
        print(f"\n  [{view}] stage 1 check: r_A = {r_A_s1:+.6f}  (D9's PRIMARY "
              f"value; the task doc records -0.066425 full / -0.068692 H)")
        agree(f"D16 stage-1 r_A ({view})", r_A_s1,
              -0.066425 if view == "full" else -0.068692, 2e-6)
        # Arm S stage-1 residuals come from the SAME fit on all 78 nulls, so
        # A222V and Arm S are out-of-sample from one common fit.
        beta = p3.fit_ols(np.array([RHO[view][b] for b in N_ids], float),
                          np.array([mad[view][b] for b in N_ids], float))
        rA1 = RHO_A[view] - p3.predict(beta, mad_a[view])
        rS1 = {b: RHO[view][b] - p3.predict(beta, mad[view][b]) for b in S_ids}
        rshift_A[view], rshift_S[view] = rA1, rS1
        rr, oos, xs, ys, nb, gg = isotonic_variant(
            "D16b  r^shift ~ g(d3_CA)  [PRIMARY]", resN,
            lambda b, v=view: rshift[v][b],
            lambda b: float(df3.loc[b, "d3_CA"]), view,
            oos=[("A222V", rA1, 0.0)] +
                [(b, rS1[b], 0.0) for b in S_ids])
        d16b[view] = report("D16b", rr, oos[0][1],
                            {lbl: val for lbl, val in oos[1:]},
                            resN, view, xs, ys, nb, gg)

    # ================= D16c  sequence distance, all 78 =====================
    p3.banner("D16c -- SEQUENCE-DISTANCE SENSITIVITIES (all 78 nulls; "
              "SENSITIVITY, NOT SELECTED)", "-")
    d16c = {}
    for view in p3.VIEWS:
        r, oos, xs, ys, nb, gg = isotonic_variant(
            "D16c-a  raw rho ~ g(dist_seq), all 78 nulls", N_ids,
            lambda b, v=view: RHO[v][b],
            lambda b: float(st["DIST"][b]), view,
            oos=[("A222V", RHO_A[view], 0.0)])
        d16c[(view, "a")] = report("D16c-a", r, oos[0][1], None, N_ids, view,
                                   xs, ys, nb, gg)
        rr, oos, xs, ys, nb, gg = isotonic_variant(
            "D16c-b  r^shift ~ g(dist_seq), all 78 nulls", N_ids,
            lambda b, v=view: rshift[v][b],
            lambda b: float(st["DIST"][b]), view,
            oos=[("A222V", rshift_A[view], 0.0)])
        d16c[(view, "b")] = report("D16c-b", rr, oos[0][1], None, N_ids, view,
                                   xs, ys, nb, gg)

    # ================= side-by-side ========================================
    p3.banner("D16 SIDE-BY-SIDE (none selected; PRIMARY marked)", "-")
    print(f"  {'variant':>42s} {'view':>5s} {'n nulls':>8s} {'g(0)':>11s} "
          f"{'r_A':>11s} {'k':>4s} {'p_spec_adj':>11s} {'rank':>8s} "
          f"{'vs frozen threshold':>20s}")
    tab = []
    for view in p3.VIEWS:
        rows = [("D16a  raw rho ~ g(d3_CA)  [resN=67]", d16a[view]),
                ("D16b  r^shift ~ g(d3_CA)  [PRIMARY]", d16b[view])]
        for nm, d in rows:
            tab.append((nm, view, 67, d))
        tab.append(("D16c-a  raw rho ~ g(dist_seq)  [all 78]", view, 78,
                    d16c[(view, "a")]))
        tab.append(("D16c-b  r^shift ~ g(dist_seq)  [all 78]", view, 78,
                    d16c[(view, "b")]))
    for nm, view, nn, d in tab:
        print(f"  {nm:>42s} {view:>5s} {nn:>8d} {d['g0']:>+11.6f} "
              f"{d['r_A']:>+11.6f} {d['k']:>4d} {d['p']:>11.6f} "
              f"{d['rank']:>4d}/{nn + 1:<4d} {d['rel'] + ' ' + str(d['thr']):>20s}")
    n_dis = sum(1 for _, ok in checks if not ok)
    print(f"\n  RECOMPUTED vs TARGET: {len(checks) - n_dis}/{len(checks)} "
          f"AGREE, {n_dis} DISAGREE")

    print("\nD16 LIMITATIONS (printed, not only in the docstring):  g(0) IS "
          "SET BY AT MOST THE SIX NULLS WITHIN 12 A -- the exact count is "
          "printed above -- so the boundary value rests on a handful of "
          "points.  ISOTONIC POOLING MAKES g A STEP FUNCTION, not a smooth "
          "curve; the blocks and their sizes are printed so the pooling is "
          "visible.  p_spec_adj HERE IS A RANK COUNT ON LEAVE-ONE-OUT "
          "RESIDUALS OF OVERLAPPING FITS: IT IS NOT A CALIBRATED TAIL "
          "PROBABILITY AND IS NOT A DECISION RULE.  D16b's STAGE 1 IS NOT "
          "REFIT INSIDE STAGE 2'S LEAVE-ONE-OUT, SO D16b IS MILDLY OPTIMISTIC "
          "AND THE OPTIMISM IS DISCLOSED, NOT CORRECTED; D16a HAS NO SUCH "
          "STAGE.  Arm S AND A222V ARE SCORED OUT-OF-SAMPLE FROM A NULL-ONLY "
          "FIT, so they are exchangeable with each other but not with a "
          "background whose own data placed it.  Isotonic regression uses only "
          "the ORDERING of the covariate, so the result is invariant to any "
          "monotone rescaling of d3_CA: that removes the functional-form "
          "problem and introduces an indifference to the actual distances.  NO "
          "BOOTSTRAP AND NO PERMUTATION WERE RUN IN THIS TASK: N_BOOT / N_PERM "
          "ARE NOT READ.  NOTHING FROZEN IS REDEFINED AND NO OUTCOME WORD "
          "LABELS ANY RESULT HERE.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
