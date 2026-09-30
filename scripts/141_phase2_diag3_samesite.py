"""Script 141 -- Phase 2 diagnostics III, Task D13: A222V AGAINST ITS SAME-SITE
COMPARATORS (the 18 Arm S backgrounds), DIRECTLY.

WHY
---
The frozen design compared Arm S to the NULLS (`D_site`).  It never compared
A222V to Arm S.  Arm S are the 18 backgrounds at position 222 with a
substitution other than A or V (A222_C ... A222_Y).  They are the ONLY
backgrounds at distance 0, so they are the only distance-matched comparators
any adjustment could not supply.  They share A222V's SITE, not its
substitution: a comparison here speaks to substitution-specificity WITHIN the
site, and cannot separate "the residue" from "the region".

SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as
a label for any result computed here.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
----------------------------------------------------
n = 19 (18 Arm S + A222V).  THEREFORE:

* *** RANK FRACTIONS ONLY.  NO p-VALUES, NO NULL DISTRIBUTION, NO
  SIGNIFICANCE CLAIM OF ANY KIND. ***  At n = 19 a rank fraction is a
  descriptive count.  The frozen `p_spec` construction is NOT run on Arm S,
  because Arm S is not a null set and putting 18 same-site backgrounds into a
  "how many are more extreme" count would be a category error.
* The primary comparison is fixed in advance: **D13.2, the shift-adjusted
  out-of-sample residual**, on the D9 fit over all 78 nulls.
* Sensitivity, reported not selected: **D4's all-96 fit** (Arm S IN sample,
  A222V out of sample).  This is disclosed as in-sample for the 18 and is the
  exact fit Diagnostics I used, so it ties D13 back to D0's C2 output.

D13.1  RAW rho.  For both views:
  k = #{b in S : rho_b <= rho_A222V}
  rank fraction = (1 + k) / (1 + 18) = (1 + k) / 19
  A222V's signed rank within S u {A222V}, rank 1 = most negative.
  EVERY member at or below A222V is listed with its rho, and the full 18 are
  listed sorted so the reader sees the whole set.

D13.2  SHIFT-ADJUSTED RESIDUAL (PRIMARY).  Fit OLS rho ~ a + c*mean|delta| on
  ALL 78 NULLS -- the D9 fit.  A222V and all 18 Arm S members are then
  OUT OF SAMPLE from that same fit, so A222V and Arm S are exchangeable with
  each other.  Residual r = rho - (a_hat + c_hat * mean|delta|).  Rank
  fraction as in D13.1.  Sensitivity: the all-96 fit (Arm S in sample).
  Target to confirm (from Diagnostics II's D0 C2 output): `A222_C` is at or
  below A222V on raw rho (full -0.093530 vs -0.088118; H -0.090964 vs
  -0.090022) and on the all-96 residual (full -0.066534 vs -0.059133;
  H -0.063441 vs -0.061058).

D13.3  WHAT THIS CAN AND CANNOT SAY, printed as part of the output and not
  only here: Arm S shares the site and differs in substitution, so this speaks
  to substitution-specificity within the site at n = 19; the Grantham gradient
  over the same 18 was NOT RESOLVED (Phase 1b P3, Phase 2 A4); and it cannot
  separate "the residue" from "the region".

RESAMPLING UNIT
---------------
NONE.  No bootstrap, no permutation, no Monte-Carlo uncertainty.  N_BOOT /
N_PERM are not read by this script.  Every number below is a deterministic
Spearman, a deterministic OLS fit, or an exact rank count.

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result
computed here.  No adjusted p_spec is computed in this task, so the frozen
numeric thresholds are not invoked; the comparison A222V vs Arm S is a rank
fraction and is labelled as one.

LIMITS (AGENTS 6; AGENTS 3 on effect size)
------------------------------------------
* n = 19 and 18 of the 19 share a site.  Rank fractions over this set are
  rank fractions.  They are NOT tests and no CI is quoted.
* Arm S backgrounds differ from A222V in the substituted residue only, but
  their effects on the ESM-2 score distribution can differ a lot;
  mean|delta| is printed beside every member so a reader can see that.
* The shift covariate mean|delta| and rho_b are both functions of the SAME
  delta_b: this is a partial control, not an independent one.
* D13 is a comparison WITHIN Arm S.  It says nothing about the 78 nulls and
  does not replace the frozen p_spec, which is untouched.
* The Grantham gradient over these 18 was NOT RESOLVED in Phase 1b P3 /
  Phase 2 A4, so no monotonicity in substitution property is claimed here.

Usage:
  venv/bin/python3 scripts/141_phase2_diag3_samesite.py
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

t0 = time.time()
S_TABLE_SHA = p3.RHO_TABLE_SHA
D3_SHA = p3.D3_SHA

# D13 targets to confirm, quoted from Diagnostics II's D0 C2 verbatim output.
TGT_RAW = {"full": (-0.093530, -0.088118), "H": (-0.090964, -0.090022)}
TGT_A96 = {"full": (-0.066534, -0.059133), "H": (-0.063441, -0.061058)}
TOL6 = 2e-6
TOL9 = 1e-9

checks = []


def agree(label, got, target, tol, fmt="{:+.6f}"):
    ok = abs(float(got) - float(target)) < tol
    checks.append((label, ok))
    print(f"    {label:<52s} recomputed = {fmt.format(float(got))}   "
          f"target = {fmt.format(float(target))}   "
          f"|diff| = {abs(float(got) - float(target)):.3e}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


def main():
    p3.banner("D13 -- A222V AGAINST ITS SAME-SITE COMPARATORS (Arm S), "
              "DIRECTLY (script 141)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word "
          "is used as a label.")
    print("*** RANK FRACTIONS ONLY (n = 19).  NO p-VALUES, NO NULL "
          "DISTRIBUTION, NO SIGNIFICANCE CLAIM. ***")
    print("RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  "
          "N_BOOT / N_PERM are not read by this script.")

    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    print(f"\n  background_rho_table.csv sha256 = {sha1}")
    print(f"  {'MATCH' if sha1 == S_TABLE_SHA else '*** MISMATCH ***'} "
          f"(required {S_TABLE_SHA})")
    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    print(f"  background_3d_distance.csv sha256 = {sha3}")
    print(f"  {'MATCH' if sha3 == D3_SHA else '*** MISMATCH ***'}")
    assert sha1 == S_TABLE_SHA and sha3 == D3_SHA, "input sha256 mismatch"

    st = p3.build()
    S_ids, N_ids, bgs = st["S_ids"], st["N_ids"], st["bgs"]
    RHO, RHO_A, mad, mad_a = st["RHO"], st["RHO_A"], st["mad"], st["mad_a"]
    df3 = st["df3"]
    nS = len(S_ids)
    print(f"\n  Arm S (all at position 222, substitution != A and != V): "
          f"{nS} = {S_ids}")
    print(f"  All Arm S positions are 222: "
          f"{sorted(set(st['POS'][b] for b in S_ids))}, all dist_222 = "
          f"{sorted(set(st['DIST'][b] for b in S_ids))}")
    print(f"  A222V is in neither Arm S nor N and is out of sample for every "
          f"fit below.")
    print(f"  Arm S d3_CA = "
          f"{sorted(set(float(df3.loc[b, 'd3_CA']) for b in S_ids))} A "
          f"(it is position 222)")

    # ---------------------------------------------------------------- D13.1
    p3.banner("D13.1 -- RAW rho: A222V WITHIN Arm S u {A222V}  (n = 19)",
              "-")
    d131 = {}
    for view in p3.VIEWS:
        sub = sorted(S_ids, key=lambda b: RHO[view][b])
        ao = [b for b in sub if RHO[view][b] <= RHO_A[view]]
        k = len(ao)
        frac = (1 + k) / (1 + nS)
        rank = 1 + k
        d131[view] = dict(k=k, frac=frac, rank=rank, ao=ao, order=sub)
        print(f"\n  [{view}]  A222V rho = {RHO_A[view]:+.9f}")
        print(f"    {'rank':>4s} {'bg_id':>10s} {'position':>9s} "
              f"{'dist_222':>9s} {'d3_CA':>8s} {'mean|delta|':>12s} "
              f"{'rho':>14s}  <= A222V?")
        for i, b in enumerate(sub, start=1):
            print(f"    {i:>4d} {b:>10s} {st['POS'][b]:>9d} "
                  f"{st['DIST'][b]:>9d} "
                  f"{float(df3.loc[b, 'd3_CA']):>8.3f} "
                  f"{mad[view][b]:>12.6f} {RHO[view][b]:>+14.9f}  "
                  f"{'YES' if RHO[view][b] <= RHO_A[view] else 'no'}")
        print(f"    A222V  rho = {RHO_A[view]:+.9f}   mean|delta| = "
              f"{mad_a[view]:.6f}   dist_222 = 0   d3_CA = 0.000")
        print(f"    Arm S members at or below A222V: k = {k} of {nS}"
              + (f"  -> {', '.join(ao)}" if ao else "  -> NONE"))
        print(f"    A222V signed rank within S u {{A222V}} = {rank}/{nS + 1}"
              f"   rank fraction (1 + {k})/(1 + {nS}) = {frac:.4f}")
        print(f"    *** RANK FRACTION OVER n = 19.  NOT A TEST. ***")
    print("\n  RECOMPUTED vs TARGET (A222_C, from Diagnostics II's D0 C2 "
          "output):")
    for view in p3.VIEWS:
        agree(f"D13.1 A222_C raw rho ({view})", RHO[view]["A222_C"],
              TGT_RAW[view][0], TOL6)
        agree(f"D13.1 A222V raw rho ({view})", RHO_A[view],
              TGT_RAW[view][1], TOL6)
    print("    No target is given for how many OTHER Arm S members are at or "
          "below; the counts above are the recomputation and stand on their "
          "own.")

    # ---------------------------------------------------------------- D13.2
    p3.banner("D13.2 -- SHIFT-ADJUSTED RESIDUAL, EXCHANGEABLE CONSTRUCTION "
              "(PRIMARY)", "-")
    print("  PRIMARY: OLS rho ~ a + c*mean|delta| fitted on ALL 78 NULLS (the "
          "D9 fit).")
    print("  A222V and all 18 Arm S members are OUT OF SAMPLE from that same "
          "fit, so A222V and Arm S are exchangeable with each other.")
    print("  SENSITIVITY, REPORTED NOT SELECTED: D4's all-96 fit (Arm S IN "
          "sample; A222V out of sample).")
    print("  *** RANK FRACTIONS OVER n = 19.  NOT TESTS. ***")
    d132 = {}
    for view in p3.VIEWS:
        print(f"\n  === [{view}] ===")
        print(f"  {'variant':>34s} {'r_A':>11s} {'slope':>11s} "
              f"{'intercept':>11s} {'n_fit':>6s}  Arm S in sample?")
        for name, subs, insample in (
                ("PRIMARY  D9 fit on 78 nulls", N_ids, False),
                ("SENSITIVITY  D4 all-96 fit", bgs, True)):
            cov = np.array([mad[view][b] for b in subs], float)
            beta = p3.fit_ols(np.array([RHO[view][b] for b in subs], float),
                              cov)
            r_A = RHO_A[view] - p3.predict(beta, mad_a[view])
            r = {b: RHO[view][b] - p3.predict(beta, mad[view][b])
                 for b in subs}
            # A222V and any Arm S member NOT in `subs` are scored out of
            # sample from the same fit, so A222V and Arm S are exchangeable.
            for b in S_ids:
                if b not in r:
                    r[b] = RHO[view][b] - p3.predict(beta, mad[view][b])
            sub = sorted(S_ids, key=lambda b: r[b])
            ao = [b for b in sub if r[b] <= r_A]
            k = len(ao)
            frac = (1 + k) / (1 + nS)
            d132[(name, view)] = dict(r=r, r_A=r_A, k=k, frac=frac, ao=ao,
                                      order=sub, beta=beta, insample=insample)
            print(f"  {name:>34s} {r_A:>+11.6f} {float(beta[1]):>+11.6f} "
                  f"{float(beta[0]):>+11.6f} {len(subs):>6d}  "
                  f"{'YES -- disclosed' if insample else 'no'}")
            print(f"    {'rank':>4s} {'bg_id':>10s} {'rho':>14s} "
                  f"{'mean|delta|':>12s} {'residual':>12s}  <= r_A?")
            for i, b in enumerate(sub, start=1):
                print(f"    {i:>4d} {b:>10s} {RHO[view][b]:>+14.9f} "
                      f"{mad[view][b]:>12.6f} {r[b]:>+12.6f}  "
                      f"{'YES' if r[b] <= r_A else 'no'}")
            print(f"    A222V  rho = {RHO_A[view]:+.9f}  mean|delta| = "
                  f"{mad_a[view]:.6f}  predicted = "
                  f"{RHO_A[view] - r_A:+.6f}  r_A = {r_A:+.6f}")
            print(f"    Arm S at or below A222V: k = {k} of {nS}"
                  + (f"  -> {', '.join(ao)}" if ao else "  -> NONE"))
            print(f"    A222V rank fraction within S u {{A222V}} = "
                  f"(1 + {k})/(1 + {nS}) = {frac:.4f}   *** RANK FRACTION, "
                  f"NOT A TEST ***")

    print("\n  RECOMPUTED vs TARGET (A222_C on the ALL-96 residual, from D0 "
          "C2):")
    for view in p3.VIEWS:
        v96 = d132[("SENSITIVITY  D4 all-96 fit", view)]
        agree(f"D13.2 A222_C all-96 residual ({view})",
              v96["r"]["A222_C"], TGT_A96[view][0], TOL6)
        agree(f"D13.2 A222V all-96 residual ({view})", v96["r_A"],
              TGT_A96[view][1], TOL6)

    p3.banner("D13 HEAD-TO-HEAD (rank fractions; n = 19; none is a test)",
              "-")
    print(f"  {'view':>5s} {'statistic':>46s} {'k of 18':>8s} "
          f"{'rank frac':>10s}  Arm S at or below A222V")
    for view in p3.VIEWS:
        rows = [("raw rho", d131[view]),
                ("shift-adj. residual (PRIMARY, 78-null fit)",
                 d132[("PRIMARY  D9 fit on 78 nulls", view)]),
                ("shift-adj. residual (all-96 fit, SENSITIVITY)",
                 d132[("SENSITIVITY  D4 all-96 fit", view)])]
        for nm, d in rows:
            print(f"  {view:>5s} {nm:>46s} {d['k']:>8d} {d['frac']:>10.4f}"
                  f"  {', '.join(d['ao']) if d['ao'] else 'NONE'}")
    print("\n  effect size, stated alongside the rank fraction (AGENTS 3):")
    for view in p3.VIEWS:
        s = np.array([RHO[view][b] for b in S_ids])
        print(f"    [{view}] Arm S raw rho: mean = {s.mean():+.6f}, "
              f"median = {np.median(s):+.6f}, min = {s.min():+.6f}, "
              f"max = {s.max():+.6f}, sd = {s.std(ddof=1):.6f};  "
              f"A222V = {RHO_A[view]:+.6f}")
        r = np.array([d132[("PRIMARY  D9 fit on 78 nulls", view)]["r"][b]
                      for b in S_ids])
        rA = d132[("PRIMARY  D9 fit on 78 nulls", view)]["r_A"]
        print(f"    [{view}] Arm S primary residual: mean = {r.mean():+.6f}, "
              f"median = {np.median(r):+.6f}, min = {r.min():+.6f}, "
              f"max = {r.max():+.6f}, sd = {r.std(ddof=1):.6f};  "
              f"A222V r_A = {rA:+.6f}")
    s_full = np.array([RHO["full"][b] for b in S_ids])
    s_h = np.array([RHO["H"][b] for b in S_ids])
    print(f"    *** RAW rho: A222V is the "
          f"{1 + int((s_full <= RHO_A['full']).sum())}nd most negative of the "
          f"19 on the full frame and the "
          f"{1 + int((s_h <= RHO_A['H']).sum())}nd most negative on H; it "
          f"sits INSIDE the Arm S raw-rho range "
          f"[{s_full.min():+.6f}, {s_full.max():+.6f}] (full), not outside "
          f"it.  Exactly one Arm S member ({', '.join(d131['full']['ao'])}) is "
          f"more negative than A222V.  The rank fraction is the result; the "
          f"range statement is context and is not a test. ***")

    p3.banner("D13.3 -- WHAT THIS CAN AND CANNOT SAY", "-")
    print("  CAN: within position 222, replacing the alanine with valine "
          "changes rho_b relative to the other 18 substitutions at that same "
          "site, on this measure, at n = 19.  This is a "
          "substitution-specificity statement WITHIN the site.")
    print("  CANNOT: separate 'the residue' from 'the region around 222'.  "
          "Every member of this comparison is at position 222 and at "
          "d3_CA = 0, so the comparison carries no information about "
          "proximity at all.")
    print("  CANNOT: speak to a monotonic Grantham gradient over these 18.  "
          "The Grantham gradient over the same 18 was NOT RESOLVED (Phase 1b "
          "P3, Phase 2 A4), so no claim about substitution property is made "
          "here.")
    print("  CANNOT: be a test.  n = 19, all 18 comparators share a site, and "
          "no null distribution exists for this comparison.  These are "
          "rank fractions.")
    print("  CANNOT: replace the frozen p_spec.  The frozen comparison is "
          "A222V against the 78 nulls and is untouched by this task.")
    print("  CAVEAT: mean|delta| and rho_b are both functions of the SAME "
          "delta_b, so D13.2 is a partial control of shift MAGNITUDE and not "
          "an independent one; it is blind to shift sign pattern and to "
          "heteroscedasticity.")

    n_dis = sum(1 for _, ok in checks if not ok)
    print(f"\n  RECOMPUTED vs TARGET: {len(checks) - n_dis}/{len(checks)} "
          f"AGREE, {n_dis} DISAGREE")

    print("\nD13 LIMITATIONS (printed, not only in the docstring):  n = 19 "
          "and 18 of the 19 share a site, so every number here is a rank "
          "fraction and NOT a test; no CI, no p-value, no permutation.  "
          "mean|delta| and rho_b are both functions of the same delta_b, so "
          "the shift adjustment is partial and blind to sign pattern.  The "
          "all-96 sensitivity puts Arm S IN sample and is labelled so; it is "
          "reported, not selected.  The Grantham gradient over these 18 was "
          "NOT RESOLVED (Phase 1b P3, Phase 2 A4) and nothing here claims "
          "monotonicity in substitution property.  Nothing frozen is "
          "redefined and no outcome word labels any result here.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
