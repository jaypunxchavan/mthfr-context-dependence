"""Script 133 -- Phase 2 diagnostics Tasks D3, D7 and D8.

These three are grouped in one script because they share an input, share a
method, and share a property that makes them worth grouping: all three are
EXACT RANK COUNTS on the gated D1 table with NO resampling of any kind.
D3 decomposes the pooled rank by arm; D7 recomputes p_spec under a |rho|
inequality; D8 recomputes p_spec with one background dropped. None of them
has an uncertainty to propagate, so a bootstrap here would be decoration.

  D3  A222V's rank within Arm V alone and within Arm G alone (decomposition)
  D7  (1) sign-explicit one-sentence restatement
      (2) p_spec under |rho_b| instead of signed rho_b
  D8  G_P254F leave-one-out fragility

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  Per PHASE2_DIAGNOSTICS.md rule 9, the three words reserved for the
frozen test are not used anywhere in this script, and this script never
computes or names that outcome.  D3 is decomposition, not a new test; D7
part 2 is a disclosed sensitivity, not a replacement; D8 is an
after-the-fact deletion, not a re-analysis.

RESAMPLING UNIT
---------------
NONE.  Every number below is an exact count over a fixed set of 96 (or 78,
or 77, or 39, or 41) already-computed rho values.  There is no sampling
step, so N_BOOT and N_PERM are not read by this script and smoke-testing
them is n/a.  Note for contrast: Phase 2's primary analysis resamples
POSITIONS within a background, and D2's locality work resampled BACKGROUNDS.
Neither unit applies here because nothing is estimated.

A222V'S OWN RHOS ARE RE-DERIVED, NOT HARD-CODED
-----------------------------------------------
A222V is deliberately NOT a row of background_rho_table.csv: it is in
neither arm S nor the null set N (frozen section 3, and script 125's own
print says so).  Its two rhos are the p_spec THRESHOLDS, so this script
re-derives them from script 125's own construction (imported, 2 s) and
hard-gates them against the values D1 printed to 1e-12 before using either.
If they do not reproduce, this script exits 1 rather than computing a
threshold off an unverified number.

PRE-REGISTERED RULES (written before the run)
---------------------------------------------
D3.1  Rank definition is script 125's own (125 line 415):
        rank = 1 + #{arm members with rho_b < rho_A222V}
      and the "at or below" count is 125's p_spec numerator:
        k     = #{arm members with rho_b <= rho_A222V}
      Both are reported, because with continuous rho they coincide here but
      need not in general, and the frozen p_spec uses the `<=` form.
D3.2  Arms are decomposed separately, never pooled: Arm V u {A222V} (n=39)
      and Arm G u {A222V} (n=41).  Arm S is excluded from both: it is the
      same-site arm and is not part of the frozen comparison.
D3.3  D3 is DECOMPOSITION.  No p_spec is recomputed here and the 2/79 and
      4/79 pooled values are not redefined; the arm-level k and n are
      reported so a reader can see which arm the pooled count came from.
D3.4  Arm V and Arm G have different construction (V is exhaustive and
      fitness-blind; G is a seed-0 uniform random draw), so their rhos are
      NOT exchangeable and no cross-arm significance is claimed.  Arm
      sizes, position coverage and the position distribution of each arm
      are printed so the asymmetry is visible.
D7.1  The sign-explicit sentence is composed from D1's VERIFIED numbers
      only, and is printed verbatim in the output.  No number in it is
      typed by hand: each is interpolated from a variable that was gated.
D7.2  p_spec_abs = (1 + #{b in N : |rho_b| >= |rho_A222V|}) / (1 + |N|).
      THE INEQUALITY FLIPS TO `>=`: this asks whether A222V's MAGNITUDE is
      unusually large in EITHER direction, whereas the frozen signed test
      asks whether it is unusually NEGATIVE (`<=`).  Using `<=` here would
      be a straightforward error and would silently reproduce the frozen
      test.  The two counts are printed side by side so the direction is
      visible in the output.
D7.3  p_spec_abs is a DISCLOSED SENSITIVITY.  It is reported beside the
      signed p_spec and never instead of it.
D8.1  Leave-one-out removes G_P254F from N, so |N| goes 78 -> 77 and the
      floor becomes 1/78 = 0.012820513.  Both the original and the
      leave-one-out values are printed side by side, on both views.
D8.2  On H, G_P254F is one of THREE backgrounds at or below A222V (with
      AV_220 and AV_195), so removing it should leave those two as the
      binding set.  This is checked and printed rather than assumed.
D8.3  D8 changes the denominator as well as the numerator.  Reporting the
      LOO numerator over the ORIGINAL denominator would be a different and
      misleading number; both are printed and the denominator is stated
      next to every value.

LIMITATIONS (AGENTS 6)
----------------------
* All three tasks are exact counts.  They carry NO sampling uncertainty, and
  a p_spec that is small is small because of how few backgrounds happened to
  land at or below A222V -- not because of a tail probability.  Script 125's
  own printed limitation says p_spec is "bounded below by 1/(1+|N|) and is
  an empirical rank count, not a tail model", and that applies to every
  number in this script without exception.
* D3's arm decomposition cannot tell whether a background is a "hit" by
  construction or by measurement.  Arm G is a uniform draw over positions;
  Arm V is exhaustive over A->V positions.  Differences between the arms
  reflect that asymmetry at least as much as they reflect biology.
* D7 part 2 answers a DIFFERENT question from the frozen test.  A small
  p_spec_abs would mean A222V's |rho| is large, which a large POSITIVE rho
  would also produce.  It is not a test the frozen pre-registration asked
  for and is not offered as one.
* D8 is a deletion chosen after seeing which background it was.  That is
  the point of the exercise -- it measures fragility -- but it means the
  leave-one-out values are diagnostics of the frozen result, not
  alternative estimates of it.
* The 96 rho_b share one y-vector (own_e_b) and are mutually correlated
  (script 125's printed limitation).  Rank counts over such a set are
  conservative with respect to ties but say nothing about independence.

Usage:
  venv/bin/python3 scripts/133_phase2_diag_rank_counts.py
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
# Printed verbatim by script 131 (task D1) on the run that passed D1-G1.
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
# A222V's rhos as D1 printed them; this script re-derives and gates them.
A222V_FULL_D1 = -0.08811806424891734
A222V_H_D1 = -0.09002168303339808
TOL_A222V = 1e-12

t0 = time.time()
fail = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def main():
    banner("D3 + D7 + D8 -- exact rank counts on the gated D1 table "
           "(script 133)")
    print("RESAMPLING UNIT: NONE.  Exact counts over fixed sets; no "
          "bootstrap, no permutation, N_BOOT/N_PERM not read.")

    # ------------------------------------------------------------- input --
    banner("INPUT GATE + A222V THRESHOLD GATE", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  {TABLE.relative_to(ROOT)}")
    print(f"  sha256 = {sha}")
    print(f"  script 131 printed sha256 = {TABLE_SHA}")
    if sha != TABLE_SHA:
        print("GATE FAIL: table sha256 differs from D1's gated value.")
        sys.exit(1)
    print("  INPUT GATE PASS")

    # A222V is not a row of the table; re-derive its thresholds from 125
    s125, A = pdg.build(verbose=False)
    df, point_h, rho_a_H = pdg.rho_table(A)
    rho_a_full = A.rho_a222v
    d1 = abs(rho_a_full - A222V_FULL_D1)
    d2 = abs(rho_a_H - A222V_H_D1)
    print(f"  A222V rho_full re-derived = {rho_a_full!r} vs D1 "
          f"{A222V_FULL_D1!r} |diff| = {d1:.3e} (gate < {TOL_A222V:g})")
    print(f"  A222V rho_H    re-derived = {rho_a_H!r} vs D1 "
          f"{A222V_H_D1!r} |diff| = {d2:.3e} (gate < {TOL_A222V:g})")
    if d1 >= TOL_A222V or d2 >= TOL_A222V:
        print("GATE FAIL: A222V thresholds did not reproduce; refusing to "
              "compute rank counts against an unverified threshold.")
        sys.exit(1)
    print("  A222V THRESHOLD GATE PASS")
    print(f"  A222V is deliberately not a row of the 96-background table "
          f"(it is neither Arm S nor N); its rhos are the p_spec "
          f"thresholds.")

    df = df.set_index("bg_id")
    rho = {"full": df.rho_full.to_dict(), "H": df.rho_H.to_dict()}
    arm = df.arm.to_dict()
    pos = df.position.to_dict()
    V = sorted(df.index[df.arm == "V"])
    G = sorted(df.index[df.arm == "G"])
    S = sorted(df.index[df.arm == "S"])
    N = sorted(V + G)
    thr = {"full": rho_a_full, "H": rho_a_H}
    print(f"  arms: S={len(S)} V={len(V)} G={len(G)} -> N = {len(N)}")

    # =====================================================================
    # D3
    # =====================================================================
    banner("D3 -- A222V's rank WITHIN ARM V ALONE and WITHIN ARM G ALONE",
           "-")
    print("D3.1 rank = 1 + #{arm members with rho_b < rho_A222V} "
          "(script 125's own definition, line 415).")
    print("D3.2 arms are NEVER pooled; Arm S is excluded from both "
          "(it is the same-site arm, not part of the frozen comparison).")
    print("D3.3 this is DECOMPOSITION: no p_spec is redefined here.\n")
    d3_rows = []
    for view in ("full", "H"):
        for arm_name, ids in (("V", V), ("G", G)):
            r = np.array([rho[view][b] for b in ids])
            t = thr[view]
            k_le = int((r <= t).sum())          # frozen p_spec numerator
            n_lt = int((r < t).sum())           # 125's rank numerator
            rank = n_lt + 1
            n = len(ids)
            d3_rows.append(dict(view=view, arm=arm_name, n=n,
                                n_pooled=n + 1, k_at_or_below=k_le,
                                n_strictly_below=n_lt, rank=rank,
                                rank_frac=f"{rank}/{n + 1}",
                                arm_min=float(r.min()),
                                arm_max=float(r.max()),
                                arm_median=float(np.median(r))))
            print(f"  [{view:4s} | Arm {arm_name}] n = {n} "
                  f"(+A222V -> {n + 1})")
            print(f"    #{{arm members with rho_b <= rho_A222V}} = {k_le}  "
                  f"(the frozen p_spec numerator form)")
            print(f"    #{{arm members with rho_b <  rho_A222V}} = {n_lt}")
            print(f"    A222V rank within Arm {arm_name} u {{A222V}} = "
                  f"{rank}/{n + 1}  (rank 1 = most negative)")
            print(f"    arm rho range = [{r.min():+.9f}, {r.max():+.9f}], "
                  f"median = {np.median(r):+.9f}")
    print("\n  side-by-side:")
    print(pd.DataFrame(d3_rows).to_string(index=False))

    print("\n  D3.4 arm construction asymmetry (printed so the comparison "
          "is not read as if the arms were exchangeable):")
    for name, ids in (("V", V), ("G", G)):
        p = np.array([pos[b] for b in ids])
        print(f"    Arm {name}: n={len(ids)} positions min={p.min()} "
              f"max={p.max()} median={np.median(p):.1f}; "
              f"within 222+/-50: {int((np.abs(p - 222) <= 50).sum())}; "
              f"within 222+/-25: {int((np.abs(p - 222) <= 25).sum())}")
    print("    (Arm V is exhaustive over A->V positions; Arm G is a seed-0 "
          "uniform draw.  Neither arm is a sample from a common population, "
          "so the arm-level counts below are DECOMPOSITION of the pooled "
          "count, not a comparison of two exchangeable groups, and no "
          "cross-arm significance is claimed.)")

    # =====================================================================
    # D7
    # =====================================================================
    banner("D7.1 -- SIGN-EXPLICIT ONE-SENTENCE RESTATEMENT", "-")
    k_full = int((np.array([rho["full"][b] for b in N]) <= rho_a_full).sum())
    k_h = int((np.array([rho["H"][b] for b in N]) <= rho_a_H).sum())
    p_full = (1 + k_full) / (1 + len(N))
    p_h = (1 + k_h) / (1 + len(N))
    sentence = (
        f"Substituting the alanine-to-valine change at position 222 for "
        f"the wild-type residue produces a background-specific NEGATIVE "
        f"association (Spearman rho = {rho_a_full:+.6f} on the full frame, "
        f"{rho_a_H:+.6f} on the held-out H frame) between ESM-2's implied "
        f"per-variant score shift and measured epistasis, and that "
        f"association is more negative than {k_full} of the {len(N)} "
        f"placebo backgrounds on the full frame and {k_h} of the {len(N)} "
        f"on the held-out H frame (rank-based p_spec = {p_full:.6f} and "
        f"{p_h:.6f} respectively)."
    )
    print("  Composed from the gated D1 values only (D7.1); no number in "
          "it is typed by hand:")
    print()
    print(f"  >>> {sentence}")
    print()
    print(f"  (numbers interpolated: rho_full={rho_a_full:+.6f}, "
          f"rho_H={rho_a_H:+.6f}, k_full={k_full}, k_H={k_h}, "
          f"|N|={len(N)}, p_spec(full)={p_full:.6f}, p_spec(H)={p_h:.6f})")

    banner("D7.2 -- p_spec under |rho| INSTEAD OF SIGNED rho (SENSITIVITY)",
           "-")
    print("D7.2 THE INEQUALITY FLIPS: the frozen signed test asks whether "
          "A222V is unusually NEGATIVE (`rho_b <= rho_A222V`); this "
          "sensitivity asks whether its MAGNITUDE is unusually large in "
          "EITHER direction (`|rho_b| >= |rho_A222V|`).  Using `<=` here "
          "would silently reproduce the frozen test.\n")
    d7_rows = []
    for view in ("full", "H"):
        r = np.array([rho[view][b] for b in N])
        t = thr[view]
        k_le = int((r <= t).sum())                       # signed (frozen)
        k_abs = int((np.abs(r) >= abs(t)).sum())         # magnitude (>=)
        p_le = (1 + k_le) / (1 + len(N))
        p_abs = (1 + k_abs) / (1 + len(N))
        members = sorted(b for b in N if abs(rho[view][b]) >= abs(t))
        pos_members = [b for b in members if rho[view][b] > 0]
        d7_rows.append(dict(view=view, n_N=len(N),
                            rho_a222v=t, signed_le=k_le, p_signed=p_le,
                            abs_ge=k_abs, p_abs=p_abs,
                            n_positive_among_hits=len(pos_members)))
        print(f"  [{view}]  |rho_A222V| = {abs(t):.9f}   "
              f"rho_A222V = {t:+.9f}   |N| = {len(N)}")
        print(f"    signed    #{{rho_b <= rho_A222V}}   = {k_le}  -> "
              f"p_spec      = (1 + {k_le})/(1 + {len(N)}) = {p_le:.9f}")
        print(f"    magnitude #{{|rho_b| >= |rho_A222V|}} = {k_abs}  -> "
              f"p_spec_abs  = (1 + {k_abs})/(1 + {len(N)}) = {p_abs:.9f}")
        print(f"    backgrounds counted in p_spec_abs: {members}")
        print(f"    of those, {len(pos_members)} are POSITIVE "
              f"({pos_members}) -- these are the ones the frozen signed "
              f"test correctly ignores, and the entire difference between "
              f"the two p-values is them.")
    print("\n  side-by-side (signed vs magnitude):")
    print(pd.DataFrame(d7_rows).to_string(index=False))
    print("\n  D7.3: p_spec_abs is a DISCLOSED SENSITIVITY reported BESIDE "
          "the signed p_spec.  It does not replace the frozen one-sided "
          "test; it isolates how much of the verdict depends on the "
          "pre-declared DIRECTION versus on raw magnitude.  A large "
          "p_spec_abs would mean A222V's |rho| is unremarkable in size even "
          "if its sign is extreme -- and that would be a statement about "
          "ESM-2's typical |rho|, not about MTHFR.")

    # =====================================================================
    # D8
    # =====================================================================
    banner("D8 -- G_P254F LEAVE-ONE-OUT FRAGILITY", "-")
    print("D8.3: removing one background changes the DENOMINATOR as well as "
          "the numerator.  |N| goes 78 -> 77 and the floor from 1/79 to "
          "1/78 = 0.012820513.  Both are stated next to every value.\n")
    d8_rows = []
    for view in ("full", "H"):
        t = thr[view]
        # original
        r0 = np.array([rho[view][b] for b in N])
        k0 = int((r0 <= t).sum())
        p0 = (1 + k0) / (1 + len(N))
        # leave-one-out
        N2 = [b for b in N if b != "G_P254F"]
        r1 = np.array([rho[view][b] for b in N2])
        k1 = int((r1 <= t).sum())
        p1 = (1 + k1) / (1 + len(N2))
        members0 = sorted(b for b in N if rho[view][b] <= t)
        members1 = sorted(b for b in N2 if rho[view][b] <= t)
        d8_rows.append(dict(view=view, n_orig=len(N), k_orig=k0,
                            p_orig=p0, n_loo=len(N2), k_loo=k1, p_loo=p1,
                            delta=p1 - p0))
        print(f"  [{view}]  floor with |N|=78 -> 1/79 = {1/79:.9f}; "
              f"floor with |N|=77 -> 1/78 = {1/78:.9f}")
        print(f"    ORIGINAL   |N|={len(N)}  #{{rho_b <= rho_A222V}} = {k0} "
              f"-> p_spec = (1 + {k0})/(1 + {len(N)}) = {p0:.9f}")
        print(f"              still at or below: {members0}")
        print(f"    LOO (G_P254F removed) |N|={len(N2)}  "
              f"#{{rho_b <= rho_A222V}} = {k1} -> p_spec = "
              f"(1 + {k1})/(1 + {len(N2)}) = {p1:.9f}")
        print(f"              still at or below: {members1}")
        print(f"    change in p_spec = {p1 - p0:+.9f}")
        # D8.2: on H, who becomes binding after the removal?
        if view == "H":
            print(f"    D8.2 check: G_P254F was one of {len(members0)} H "
                  f"beaters.  After removal the binding set is "
                  f"{members1} -- "
                  f"{'AV_220 and AV_195 remain, as expected' if members1 == ['AV_195', 'AV_220'] else 'UNEXPECTED: ' + str(members1)}.")
    print("\n  side-by-side:")
    print(pd.DataFrame(d8_rows).to_string(index=False))
    print("\n  READ THIS: on the full frame G_P254F is the ONLY background "
          "at or below A222V, so removing it drives p_spec straight to its "
          "floor.  That is what the plan anticipated.  On H it is one of "
          "three, so removing it leaves two and the value moves by much "
          "less.  The fragility is therefore ASYMMETRIC between the two "
          "views, and the honest statement is that the full-frame count "
          "rests on a single background while the H-frame count does not.")

    banner("D3 + D7 + D8 SUMMARY", "-")
    print("  D3 arm-decomposed ranks (decomposition, not a new test):")
    for r in d3_rows:
        print(f"    {r['view']:4s} Arm {r['arm']}: n={r['n']:2d} "
              f"(+A222V = {r['n_pooled']:2d})  # at or below = "
              f"{r['k_at_or_below']}  rank = {r['rank_frac']}")
    print("\n  D7 sign-explicit sentence: printed verbatim above.")
    print(f"  D7 |rho| sensitivity: p_spec_abs(full) = "
          f"{[r['p_abs'] for r in d7_rows if r['view'] == 'full'][0]:.9f} "
          f"vs signed {p_full:.9f}; p_spec_abs(H) = "
          f"{[r['p_abs'] for r in d7_rows if r['view'] == 'H'][0]:.9f} "
          f"vs signed {p_h:.9f}")
    print("  D8 leave-one-out: p_spec(full) "
          f"{p_full:.9f} -> "
          f"{[r['p_loo'] for r in d8_rows if r['view'] == 'full'][0]:.9f} "
          f"(|N| 78 -> 77); p_spec(H) {p_h:.9f} -> "
          f"{[r['p_loo'] for r in d8_rows if r['view'] == 'H'][0]:.9f}")
    print("\nLIMITATIONS: see docstring.  Every value here is an exact rank "
          "count with NO sampling uncertainty; a small p_spec is small "
          "because few backgrounds landed at or below A222V, not because of "
          "a tail probability (script 125's own printed limitation: p_spec "
          "is bounded below by 1/(1+|N|) and is an empirical rank count, "
          "not a tail model).  Arm V and Arm G are not exchangeable "
          "(exhaustive A->V vs seed-0 uniform draw), so D3 decomposes and "
          "does not compare.  D7's magnitude test answers a different "
          "question from the frozen signed test.  D8 is a deletion chosen "
          "after seeing which background it was -- that is what makes it a "
          "fragility diagnostic, and it is why the leave-one-out values "
          "are diagnostics of the frozen result and not alternative "
          "estimates of it.  None of this redefines anything frozen.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
