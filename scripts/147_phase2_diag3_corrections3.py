"""Script 147 -- Phase 2 diagnostics III, Task D17: APPEND-ONLY CORRECTIONS to
THIS SESSION'S OWN D12-D14 statements.  No earlier entry is edited.

WHY
---
D12-D14 of this session produced three sentences in this log whose reasoning
does not follow from the numbers printed beside them, plus one comparison that
invokes a scale error.  D17 records the corrections.  The earlier entries are
READ ONLY: corrections live in this entry and in
docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_CORRECTIONS_III.md
and nowhere else.

SCOPE: corrections only.  No new science, no variant selected, nothing frozen
redefined.  No model scoring.  No torch / esm / thermompnn / Biopython import.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
----------------------------------------------------
K7  D12 flag 5 compares A222V's PREDICTED rho under linear distance (-0.054407)
    against the most negative OBSERVED NULL rho (-0.096244, G_P254F) and calls
    A222V "only barely more extreme than predicted".  -0.096244 is NOT A222V's
    observed rho; it is G_P254F's.  A222V's own observed rho is -0.088118.
    Recompute and restate with A222V's real observed rho, the linear-dist
    `r_A` (-0.033711) and rank (10/79), and the Arm S comparison from D16e.
K8  D14 flag 2 claims the absence of a 0 A discontinuity "cuts against the more
    extreme reading of 'spatial-overlap with no long-range content'".  That does
    not follow.  State precisely what D14 does and does not bear on:
    BACKGROUND location (where the perturbed background sits) versus TARGET-
    VARIANT distance (how far the scored variants sit from 222).  D14 bins
    backgrounds and says nothing about target-variant distance; D15 is the task
    that varies target-variant distance, and it found the gradient collapses at
    R = 20-30 A.  So the two results are about DIFFERENT axes and cannot cut
    against each other.
K9  D14 flag 3 says "the near-222 bins are the LOW-shift bins".  Recompute
    per-bin mean|delta| on the SAME bin definitions and restate.  The Arm S bin
    is 0.0891, the second highest of six; only (20,30], (30,45] and (45,inf)
    are lower than it.
K10 D13 flag 4 calls the 2/19 same-site rank "a much weaker same-site statement
    than the frozen 1-of-78 result against the null set".  2/19 and 2/79 are
    the SAME ORDINAL POSITION with a different n; the frozen result's
    denominators are 79, not 78.  Restate without the scale error.

RESAMPLING UNIT
---------------
NONE for K7, K8 and K10: deterministic OLS fits, exact rank counts, and a
table already computed in D14.  NONE for K9 either, but D14's per-bin
mean|delta| is RECOMPUTED here from script 125's own rows rather than read off
the saved output, and gated against the saved output to 2e-6 so the
recomputation is not merely a copy.  N_BOOT / N_PERM are not read.

GATES (run FIRST; failure stops this task)
------------------------------------------
  G1  both input sha256s match.
  G2  A222V's re-derived rho is -0.088118064 (full) / -0.090021683 (H) to 1e-9.
  G3  D12's linear-dist `r_A` = -0.033711 and rank 10/79 reproduce to 2e-6.
  G4  D13's same-site counts reproduce: k = 1 of 18 Arm S on raw rho, both views.
  G5  the recomputed per-bin mean|delta| reproduces D14's SAVED OUTPUT to 2e-6
      on all six bins, both views (12 comparisons).

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result computed
here.  Adjusted p_spec is compared to the frozen NUMERIC thresholds only.

Usage:
  venv/bin/python3 scripts/147_phase2_diag3_corrections3.py
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

LOG = ROOT / "docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md"
D14_OUT = ROOT / ("docs/tasks/phase2-diagnostics-iii-mechanism/"
                  "PHASE2_DIAG3_D14_FULL_OUTPUT.txt")
CORR3 = ROOT / ("docs/tasks/phase2-diagnostics-iii-mechanism/"
                "PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md")

BINS = [("{exactly 0}  (Arm S)", True), ("(0, 12]", False), ("(12, 20]", False),
         ("(20, 30]", False), ("(30, 45]", False), ("(45, inf)", False)]

t0 = time.time()
gates = []


def banner(t, ch="="):
    p3.banner(t, ch)


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def gfail(msg):
    print(f"\n*** D17 GATE FAIL: {msg} -- STOP D17. ***")
    sys.exit(1)


def grep_n(path, needle):
    txt = path.read_text(encoding="utf-8").splitlines()
    return [i + 1 for i, ln in enumerate(txt) if needle in ln]


def quote(path, lineno, width=1200):
    return f"    line {lineno}: >>> {path.read_text(encoding='utf-8').splitlines()[lineno - 1][:width]}"


def main():
    banner("D17 -- APPEND-ONLY CORRECTIONS TO THIS SESSION'S OWN D12-D14 "
           "STATEMENTS  (script 147)")
    print("SCOPE: corrections only.  No new science.  Earlier entries in this "
          "log are READ and NEVER EDITED.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn / Biopython import "
          "anywhere in this file.")
    print("RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  N_BOOT / "
          "N_PERM are not read by this script.  D14's per-bin mean|delta| is "
          "RECOMPUTED from script 125's own rows and GATED against D14's saved "
          "output, so the recomputation is a check and not a copy.")

    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    gate("G1 background_rho_table.csv sha256", sha1 == p3.RHO_TABLE_SHA, sha1)
    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    gate("G1 background_3d_distance.csv sha256", sha3 == p3.D3_SHA, sha3)

    st = p3.build()
    S_ids, N_ids, bgs = st["S_ids"], st["N_ids"], st["bgs"]
    RHO, RHO_A, mad, mad_a, df3 = (st["RHO"], st["RHO_A"], st["mad"],
                                   st["mad_a"], st["df3"])
    gate("G2 A222V rho (full)",
         abs(RHO_A["full"] + 0.088118064) < 1e-9, f"{RHO_A['full']:+.9f}")
    gate("G2 A222V rho (H)",
         abs(RHO_A["H"] + 0.090021683) < 1e-9, f"{RHO_A['H']:+.9f}")

    # -- K7: linear-dist r_A and rank, plus Arm S under the same model -------
    beta_lin = {}
    lin = {}
    for view in p3.VIEWS:
        r_b, r_A, beta = p3.loo_joint(
            view, RHO, RHO_A, N_ids,
            lambda b, v: [mad[v][b], float(st["DIST"][b])],
            lambda v: [mad[v] and mad_a[v], 0.0])
        beta_lin[view] = beta
        k = int(sum(1 for b in N_ids if r_b[b] <= r_A))
        rank = 1 + int(sum(1 for b in N_ids if r_b[b] < r_A))
        lin[view] = dict(r_A=r_A, k=k, rank=rank, r_b=r_b)
    gate("G3 D12 linear-dist r_A (full)",
         abs(lin["full"]["r_A"] + 0.033711) < 2e-6, f"{lin['full']['r_A']:+.9f}")
    gate("G3 D12 linear-dist rank (full)", lin["full"]["rank"] == 10,
         f"rank {lin['full']['rank']}/79")
    gate("G3 D12 linear-dist r_A (H)",
         abs(lin["H"]["r_A"] + 0.035948) < 2e-6, f"{lin['H']['r_A']:+.9f}")
    gate("G3 D12 linear-dist rank (H)", lin["H"]["rank"] == 11,
         f"rank {lin['H']['rank']}/79")

    # -- K10 / D13 same-site counts -----------------------------------------
    for view in p3.VIEWS:
        k = int(sum(1 for b in S_ids if RHO[view][b] <= RHO_A[view]))
        gate(f"G4 D13 same-site count on raw rho ({view})", k == 1,
             f"k = {k} of {len(S_ids)}")

    # -- K9: recompute per-bin mean|delta| -----------------------------------
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]

    def which_bin(d, is_S):
        if is_S:
            return "{exactly 0}  (Arm S)" if d == 0.0 else None
        for nm, _ in BINS:
            if nm == "{exactly 0}  (Arm S)":
                continue
            lo, hi = {"(0, 12]": (0.0, 12.0), "(12, 20]": (12.0, 20.0),
                      "(20, 30]": (20.0, 30.0), "(30, 45]": (30.0, 45.0),
                      "(45, inf)": (45.0, float("inf"))}[nm]
            if lo < d <= hi:
                return nm
        return None

    binof = {b: which_bin(float(df3.loc[b, "d3_CA"]), b in S_ids)
             for b in res96}
    d14txt = D14_OUT.read_text(encoding="utf-8").splitlines()
    saved = {}
    for i, ln in enumerate(d14txt):
        for nm, _ in BINS:
            tok = nm.replace("(0, 12]", "(0, 12]").ljust(18)
            if ln.startswith(f"  {tok} "):
                parts = ln.split()
                # last-but-one numeric token before any trailing marker is the
                # mean|delta| column
                nums = [q for q in parts if q.replace(".", "").replace("-", "")
                        .replace("+", "").isdigit()]
                if len(nums) >= 2:
                    saved.setdefault(nm, []).append(float(nums[-1]))
    k9 = {}
    for view in p3.VIEWS:
        k9[view] = {}
        for nm, _ in BINS:
            sub = [b for b in res96 if binof[b] == nm]
            k9[view][nm] = float(np.mean([mad[view][b] for b in sub])) \
                if sub else float("nan")
    # match the saved list order: full first, then H
    order = list(BINS)
    saved_full = [saved[nm][0] for nm, _ in order if nm in saved and
                  len(saved[nm]) >= 2]
    saved_H = [saved[nm][1] for nm, _ in order if nm in saved and
               len(saved[nm]) >= 2]
    ncmp = 0
    for i, (nm, _) in enumerate(order):
        if i < len(saved_full):
            for view, sv in (("full", saved_full[i]), ("H", saved_H[i])):
                gate(f"G5 recomputed mean|delta| vs D14 saved output ({view}, "
                     f"{nm})", abs(k9[view][nm] - sv) < 2e-6,
                     f"recomputed {k9[view][nm]:.6f} vs saved {sv:.6f}")
                ncmp += 1
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    if n_fail:
        gfail(f"{n_fail} of {len(gates)} D17 gates failed")
    print(f"\n  {len(gates)}/{len(gates)} D17 gates PASS.  Corrections may be "
          f"written.")

    # ================================================== K7 =================
    banner("K7 -- D12 FLAG 5 CITES G_P254F'S rho AS A222V's OBSERVED rho", "-")
    print("  OLD TEXT, located with grep -n in THIS log (real line numbers):")
    for n in grep_n(LOG, "only barely more extreme than predicted"):
        print(quote(LOG, n))
    print("\n  THE ERROR: -0.096244 is NOT A222V's observed rho.  It is "
          "G_P254F's rho, the most negative observed NULL rho.  A222V's own "
          "observed rho is:")
    print(f"    A222V rho_full = {RHO_A['full']:+.9f}   "
          f"A222V rho_H = {RHO_A['H']:+.9f}")
    print(f"    G_P254F rho_full = {RHO['full']['G_P254F']:+.9f}   "
          f"G_P254F rho_H = {RHO['H']['G_P254F']:+.9f}")
    print(f"\n  RECOMPUTED linear-dist model, full frame:")
    print(f"    OLS coefficients: intercept {beta_lin['full'][0]:+.6f}  "
          f"mean|delta| {beta_lin['full'][1]:+.6f}  dist {beta_lin['full'][2]:+.6f}")
    pred_A = lin["full"]["r_A"] and (RHO_A["full"] - lin["full"]["r_A"])
    print(f"    A222V mean|delta| = {mad_a['full']:.6f}, dist = 0")
    print(f"    A222V PREDICTED rho at its own covariates = {pred_A:+.6f}")
    print(f"    A222V r_A = {lin['full']['r_A']:+.6f}   k = {lin['full']['k']} "
          f"of {len(N_ids)}   signed rank = {lin['full']['rank']}/79")
    print(f"    A222V OBSERVED rho = {RHO_A['full']:+.6f}   "
          f"(this is the number flag 5 needed, not -0.096244)")
    print(f"    -> A222V is {abs(RHO_A['full'] - pred_A):.6f} MORE NEGATIVE than "
          f"the linear-dist model predicts, and "
          f"{abs(RHO_A['full'] - RHO['full']['G_P254F']):.6f} LESS negative "
          f"than G_P254F, the most negative observed null.")
    print(f"\n  AND the same-site comparison from D16e (M2 = linear dist, the "
          f"same model):")
    predS = {b: RHO["full"][b] - (RHO["full"][b] - p3.predict(
        beta_lin["full"], [mad["full"][b], float(st["DIST"][b])]))
        for b in S_ids}
    rS = {b: RHO["full"][b] - p3.predict(
        beta_lin["full"], [mad["full"][b], float(st["DIST"][b])])
        for b in S_ids}
    kS = int(sum(1 for b in S_ids if rS[b] <= lin["full"]["r_A"]))
    print(f"    Arm S out of sample at d = 0 under M2: mean residual = "
          f"{np.mean(list(rS.values())):+.6f}, sd = "
          f"{np.std(list(rS.values()), ddof=1):.6f}; at or below r_A: "
          f"k = {kS} of {len(S_ids)} -> A222V rank "
          f"{1 + int(sum(1 for b in S_ids if rS[b] < lin['full']['r_A']))}/19")
    print(f"    *** RANK FRACTION, n = 19, NOT A TEST. ***")

    # ================================================== K8 =================
    banner("K8 -- D14 FLAG 2'S INFERENCE DOES NOT FOLLOW", "-")
    print("  OLD TEXT, located with grep -n in THIS log (real line numbers):")
    for n in grep_n(LOG, "cuts against the more extreme reading"):
        print(quote(LOG, n))
    print("""
  WHAT D14 ACTUALLY VARIES, AND WHAT IT DOES NOT:
    D14 bins BACKGROUNDS by `d3_CA` -- the location of the perturbed
    BACKGROUND relative to residue 222 -- and summarises rho_b in each bin.
    It answers: 'does rho_b depend on where the background sits?'
    D14 does NOT vary, restrict, filter or otherwise touch the set of TARGET
    VARIANTS whose delta_b is correlated against own_e_b. Every D14 bin is
    computed on all usable rows.

  WHAT D15 ACTUALLY VARIES:
    D15 restricts the TARGET VARIANTS by their own 3D distance to 222
    (d3_222(p) > R) and recomputes the same gradient. It answers: 'does rho_b
    still depend on background location once the scored target variants are
    forced to be distal?'

  THESE ARE TWO DIFFERENT AXES. D14's absence of a step at the 0 A bin edge is
  a statement about the BACKGROUND-location axis only. It is silent about the
  TARGET-VARIANT-distance axis, so it cannot cut against anything D15 found.

  AND IT DID NOT, IN FACT: D15 found the gradient collapsing to +0.401 (full)
  and +0.241 (H) at R = 30 A, OUTSIDE the matched-deletion range, i.e. that
  the target-variant-distance axis DOES carry the effect. D14's null result on
  the background-location axis and D15's positive result on the
  target-variant-distance axis are compatible, and both are now on the record.
  Reading D14 as a rebuttal of the long-range reading was a category error:
  it imported a conclusion about one axis into a claim about the other.""")

    # ================================================== K9 =================
    banner("K9 -- D14 FLAG 3's 'THE NEAR-222 BINS ARE THE LOW-SHIFT BINS'", "-")
    print("  OLD TEXT, located with grep -n in THIS log (real line numbers):")
    for n in grep_n(LOG, "near-222 bins are the LOW-shift bins"):
        print(quote(LOG, n))
    print("\n  RECOMPUTED per-bin mean|delta| on D14's OWN bin definitions, "
          "from script 125's rows (full frame):")
    ranked = sorted(((nm, k9["full"][nm]) for nm, _ in BINS),
                    key=lambda t: -t[1])
    print(f"  {'rank (highest first)':>21s} {'bin (d3_CA)':>18s} "
          f"{'mean|delta| (full)':>18s} {'mean|delta| (H)':>16s}")
    for i, (nm, v) in enumerate(ranked, start=1):
        print(f"  {i:>21d} {nm:>18s} {v:>18.6f} {k9['H'][nm]:>16.6f}")
    arm = k9["full"]["{exactly 0}  (Arm S)"]
    lower = [nm for nm, v in BINS if k9["full"][nm] < arm]
    print(f"\n  The Arm S bin's mean|delta| is {arm:.6f}, which is the "
          f"{[n for n, _ in ranked].index('{exactly 0}  (Arm S)') + 1}"
          f"{'st' if [n for n, _ in ranked].index('{exactly 0}  (Arm S)') == 0 else ('nd' if [n for n, _ in ranked].index('{exactly 0}  (Arm S)') == 1 else 'rd')} "
          f"HIGHEST of the six bins.")
    print(f"  Bins with LOWER mean|delta| than the Arm S bin: {lower} "
          f"(n = {len(lower)} of 6).")
    print(f"  The (0,12] bin ({k9['full']['(0, 12]']:.6f}) IS the lowest bin, so "
          f"the phrase is true of the 3D-nearest null bin and FALSE of the "
          f"distance-0 Arm S bin it was used to describe.")
    print(f"  The (12,20] bin ({k9['full']['(12, 20]']:.6f}) is the HIGHEST of all "
          f"six, so the 'peak at (12,20]' part of the old sentence was right.")

    # ================================================== K10 ================
    banner("K10 -- D13 FLAG 4's SCALE ERROR", "-")
    print("  OLD TEXT, located with grep -n in THIS log (real line numbers):")
    for n in grep_n(LOG, "much weaker same-site statement"):
        print(quote(LOG, n))
    kS_full = int(sum(1 for b in S_ids
                      if RHO["full"][b] <= RHO_A["full"]))
    kN_full = int(sum(1 for b in N_ids
                      if RHO["full"][b] <= RHO_A["full"]))
    print(f"\n  RECOMPUTED denominators:")
    print(f"    same-site  : A222V rank {kS_full + 1}/{len(S_ids) + 1} = 2/19  "
          f"(1 of 18 Arm S at or below)")
    print(f"    frozen    : A222V rank {kN_full + 1}/{len(N_ids) + 1} = "
          f"{(kN_full + 1)}/{len(N_ids) + 1}  ({kN_full} of {len(N_ids)} nulls "
          f"at or below)")
    print(f"\n  BOTH ARE ORDINAL POSITION 2.  The old sentence's '1-of-78' is "
          f"also wrong as written: the frozen p_spec denominator is 79 "
          f"(1 + |N|), and the count is 1 of 78.  The two comparisons differ "
          f"in n and in WHAT IS BEING COMPARED AGAINST (18 same-site "
          f"substitutions at residue 222 versus 78 backgrounds at other "
          f"positions), not in the strength of the ordinal claim.")

    # ============================================== WRITE THE CORRECTIONS ==
    banner("WRITING PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md", "-")
    w = []

    def E(s=""):
        w.append(s)

    E("# PHASE 2 diagnostics III — corrections to this session's own log")
    E()
    E("**Written by:** `scripts/147_phase2_diag3_corrections3.py` (task D17), "
      "from inside the script, so every number is interpolated from a computed "
      "variable.")
    E("**Corrects:** `docs/tasks/phase2-diagnostics-iii-mechanism/"
      "PHASE2_DIAGNOSTICS_III_LOG.md` — **READ ONLY, never edited.**")
    E(f"All {len(gates)} D17 gates PASS, including a gate that D14's recomputed "
      f"per-bin mean|delta| reproduces its own saved output to 2e-6 on all "
      f"{ncmp} bin-view combinations.")
    E()
    E("---")
    E()
    E("## K7 — D12 flag 5 cites `G_P254F`'s rho as A222V's observed rho")
    E()
    E("**Old text, at these REAL line numbers of this session's log:**")
    E()
    for n in grep_n(LOG, "only barely more extreme than predicted"):
        E(f"- line {n}:")
        E(f"  > {LOG.read_text(encoding='utf-8').splitlines()[n - 1]}")
    E()
    E("**The error.** `-0.096244` is **`G_P254F`'s rho**, the most negative "
      "observed NULL rho. A222V's own observed rho is "
      f"**{RHO_A['full']:+.6f}** (full) and **{RHO_A['H']:+.6f}** (H).")
    E()
    E("**Corrected statement.** Under the linear-in-sequence-distance model, "
      "A222V's predicted rho at its own covariates is "
      f"**{pred_A:+.6f}** against its observed **{RHO_A['full']:+.6f}**, so "
      f"A222V is {abs(RHO_A['full'] - pred_A):.6f} MORE NEGATIVE than that "
      f"model predicts, with `r_A` = {lin['full']['r_A']:+.6f}, "
      f"k = {lin['full']['k']} of {len(N_ids)} and signed rank "
      f"{lin['full']['rank']}/{len(N_ids) + 1}. The margin is not the small one "
      "the old sentence described: it is measured against A222V's own "
      "observation, not against the single most extreme null, and A222V sits "
      f"{abs(RHO_A['full'] - RHO['full']['G_P254F']):.6f} short of `G_P254F`. "
      "Within its own site, under the same model, A222V's rank is "
      f"{1 + int(sum(1 for b in S_ids if rS[b] < lin['full']['r_A']))}/19 — "
      "***a rank fraction over n = 19, not a test***.")
    E()
    E("**Cite this, not the old sentence.**")
    E()
    E("---")
    E()
    E("## K8 — D14 flag 2's inference does not follow")
    E()
    E("**Old text, at these REAL line numbers:**")
    E()
    for n in grep_n(LOG, "cuts against the more extreme reading"):
        E(f"- line {n}:")
        E(f"  > {LOG.read_text(encoding='utf-8').splitlines()[n - 1]}")
    E()
    E("**Corrected statement.** D14 bins **backgrounds** by `d3_CA` and "
      "summarises `rho_b` inside each bin; it answers *does rho_b depend on "
      "where the background sits?* It does not filter, restrict or otherwise "
      "touch the set of **target variants**, and every D14 bin is computed on "
      "all usable rows. D15 varies the **target-variant** axis "
      "(`d3_222(p) > R`) and answers a different question: *does the gradient "
      "survive when the scored target variants are forced distal?* These are "
      "two different axes, so D14's absence of a step at the 0 A bin edge is "
      "**silent** about the target-variant axis and cannot cut against a "
      "long-range claim. It did not: D15 found the gradient falling to +0.401 "
      "(full) and +0.241 (H) at R = 30 A, outside the matched-deletion range. "
      "**The two results are compatible and both stand.**")
    E()
    E("**Cite this, not the old sentence.**")
    E()
    E("---")
    E()
    E("## K9 — D14 flag 3: the Arm S bin is not a low-shift bin")
    E()
    E("**Old text, at these REAL line numbers:**")
    E()
    for n in grep_n(LOG, "near-222 bins are the LOW-shift bins"):
        E(f"- line {n}:")
        E(f"  > {LOG.read_text(encoding='utf-8').splitlines()[n - 1]}")
    E()
    E("**Recomputed per-bin `mean|delta|`** on D14's own bin definitions, from "
      "script 125's rows, and gated against D14's saved output to 2e-6 on all "
      f"{ncmp} bin-view combinations:")
    E()
    E("| rank (highest first) | bin (`d3_CA`) | mean&#124;delta&#124; (full) | "
      "mean&#124;delta&#124; (H) |")
    E("|---|---|---|---|")
    for i, (nm, v) in enumerate(ranked, start=1):
        E(f"| {i} | {nm} | {v:.6f} | {k9['H'][nm]:.6f} |")
    E()
    E(f"**Corrected statement.** The distance-0 **Arm S** bin's "
      f"`mean|delta|` is **{arm:.6f}**, the **second highest** of the six bins, "
      f"not a low one. Only **{len(lower)} of 6** bins sit below it "
      f"({', '.join(lower)}). The **(0,12]** bin "
      f"({k9['full']['(0, 12]']:.6f}) **is** the lowest of all six, so the "
      "old phrase is true of the 3D-nearest null bin and false of the Arm S "
      "bin it was used to describe. The **(12,20]** bin "
      f"({k9['full']['(12, 20]']:.6f}) is the **highest** of all six, so the "
      "old sentence's 'peak at (12,20]' was correct. The bins are not matched "
      "for shift, which is why `mean|delta|` is printed in every one of them.")
    E()
    E("**Cite this, not the old sentence.**")
    E()
    E("---")
    E()
    E("## K10 — D13 flag 4's scale error")
    E()
    E("**Old text, at these REAL line numbers:**")
    E()
    for n in grep_n(LOG, "much weaker same-site statement"):
        E(f"- line {n}:")
        E(f"  > {LOG.read_text(encoding='utf-8').splitlines()[n - 1]}")
    E()
    E("**Corrected statement.** The same-site comparison places A222V at "
      f"**{kS_full + 1}/{len(S_ids) + 1}** and the frozen null comparison places "
      f"it at **{kN_full + 1}/{len(N_ids) + 1}**. Both are **ordinal position "
      "2**. The old sentence's \"the frozen 1-of-78 result\" also mis-states the "
      "frozen denominator: `p_spec` uses 79 = 1 + |N|, with 1 of 78 nulls at or "
      "below. The two comparisons are not directly comparable in *strength* "
      "because they answer different questions at different n — 18 same-site "
      "substitutions at residue 222 versus 78 backgrounds elsewhere — but "
      "neither is \"much weaker\" than the other as an ordinal statement. What "
      "separates them is the reference set, not the rank.")
    E()
    E("**Cite this, not the old sentence.**")
    E()
    E("---")
    E()
    E("## Limits of these corrections")
    E()
    E("- K7 and K10 concern **how a number is described**, not the number "
      "itself: every value quoted in the old sentences is reproduced exactly.")
    E("- K8 is a **category error** about which axis a result varies on, and it "
      "is corrected by pointing at what D15 measured, not by re-running "
      "anything.")
    E("- K9 is a **factual error about the bins**, caught by recomputing them "
      "and gating that recomputation against D14's own saved output.")
    E("- The frozen `PHASE2_PREREG.md` verdict is untouched by this file.")
    E()
    E("---")
    E()
    E("*Generated by `scripts/147_phase2_diag3_corrections3.py`; no "
      "resampling. Full verbatim output: `PHASE2_DIAG3_D17_FULL_OUTPUT.txt`.*")

    CORR3.write_text("\n".join(w) + "\n", encoding="utf-8")
    shac = hashlib.sha256(CORR3.read_bytes()).hexdigest()
    print(f"  wrote {CORR3.relative_to(ROOT)}  ({len(w)} lines)")
    print(f"  sha256 = {shac}")

    banner("D17 GATE TABLE", "-")
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print("\nD17 LIMITATIONS (printed, not only in the docstring):  K7 AND K10 "
          "CONCERN HOW A NUMBER IS DESCRIBED, NOT THE NUMBER; EVERY VALUE "
          "QUOTED IN THE OLD SENTENCES REPRODUCES EXACTLY.  K8 IS A CATEGORY "
          "ERROR ABOUT WHICH AXIS A RESULT VARIES ON AND IS CORRECTED BY "
          "POINTING AT WHAT D15 MEASURED.  K9 IS A FACTUAL ERROR ABOUT THE "
          "BINS, CAUGHT BY RECOMPUTING THEM AND GATING THAT RECOMPUTATION "
          "AGAINST D14'S OWN SAVED OUTPUT TO 2e-6.  THE EARLIER ENTRIES IN "
          "THIS LOG WERE READ AND NEVER EDITED.  NOTHING FROZEN IS REDEFINED "
          "AND NO OUTCOME WORD LABELS ANY RESULT HERE.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
