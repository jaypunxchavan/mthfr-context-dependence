"""
Script 150 (task D20 of docs/tasks/phase2-diagnostics-iv-shells/
PHASE2_DIAGNOSTICS_IV.md) -- SHELL DECOMPOSITION of the far-variant effect,
with size-matched controls for every shell.

PRE-REGISTERED: this docstring was written BEFORE the first run of this
script.  Nothing below was chosen after seeing a result.

WHY
---
D15 bracketed the signal (R = 10 changes nothing, R = 20 marginal, R = 30
collapses the gradient) but did not locate it.  This task locates it in
FIXED shells, each judged only against its own size-matched control.

SHELLS (fixed now, not tuned -- task doc line 203)
-------------------------------------------------
On d3_222(p) over each view's RESOLVED target positions (D15's universe:
595 full / 418 H):
    (0, 10]   (10, 20]   (20, 30]   (30, 45]   (45, inf)
Position 222 is NOT a frame target position (D15 full output line 37:
"frame positions = 654;  position 222 itself IS NOT a frame target
position") and the minimum d3_222 among resolved positions is 3.805 A
(line 45), so no resolved position has d3_222 = 0 and shell (0,10] is
exactly {d3_222 <= 10}, i.e. D15's k_R(10) removal set.  The script
VERIFIES both premises at run time (min d3 printed; union of the first
three shells checked equal to {d3 <= 30} as a boolean array).

VARIANTS (2 per shell per view)
-------------------------------
* REMOVE-ONE-SHELL (NECESSITY): delete all positions in shell s, keep
  everything else that is resolved.
* KEEP-ONLY-SHELL (SUFFICIENCY): retain only positions in shell s.
Rows at unresolved positions are dropped from EVERY variant, including
the R = 0 baseline, and counted; NEVER imputed (D15 convention:
`keep_from_removed` ANDs the mask with `resolved`).

DOC TARGETS RECOMPUTED INDEPENDENTLY (rule 2) -- printed beside their
targets and gated; a mismatch means the DOC is wrong, BOTH numbers are
printed and that item stops (no forcing agreement):
* full-frame shell counts, first three shells: 23, 98, 126 (task doc
  lines 203-204, "targets from D15's k_R differences").  Checked against
  TWO independent recomputations: (i) direct count from d3_222, and
  (ii) derived at run time from D15's printed k_R values (parsed from
  PHASE2_DIAG3_D15_FULL_OUTPUT.txt, never copied).
* REMOVE of the union of shells (0,10] + (10,20] + (20,30] reproduces
  D15's S1 R = 30 statistics: A222V rho -0.027360127 and gradient
  +0.400678440 (full), task doc lines 215-217.  Gate < 1e-9 (values D15
  printed with 9 decimals); the union's boolean keep-mask must ALSO be
  IDENTICAL to the R = 30 keep-mask (exact, 0 difference).
Shell counts for the H view and for the two large shells have NO doc
target: they are REPORTED (and gated against D15's printed k_R
differences, which are an independent source).

GATES (pre-registered)
----------------------
D20-G1 (HARD -- any failure stops D20; task doc rule 6):
  (a) deleting ZERO positions reproduces the R = 0 baseline EXACTLY
      (keep arrays identical; max|diff| over rho_A222V, both gradients
      and both k's = 0), AND the baseline recomputes to D15's printed
      R = 0 row (A222V rho, gradient n = 67, p_spec n = 78).
  (b) REMOVE of the union of the first three shells is EXACTLY the
      R = 30 removal set (keep arrays identical), reproduces the doc's
      targets (-0.027360127 / +0.400678440, full), and reproduces
      D15's printed R = 30 row for BOTH views.  Second instance of the
      same construction (added before the full run, still G1b): REMOVE
      of shell (0,10] ALONE is D15's R = 10 removal set (min d3_222 =
      3.805 > 0, verified and printed), so it must reproduce D15's
      printed R = 10 row too.
  For every comparison against D15's PRINTED row the tolerance is that
  quantity's own PRINT PRECISION: rho and gradient are printed with 9
  decimals (script 144 lines 779/781) -> 1e-9; p_spec is printed with 6
  DECIMALS (script 144 line 783, f"{s['p_n78']:>13.6f}") -> 5e-7, the
  half-ulp of a 6-dp print.  DISCLOSURE (AGENTS 6): the first smoke run
  gated all three at a uniform 1e-9, which is unachievable for a 6-dp
  print by ANY implementation (the observed p_spec difference was
  3.2e-07 while rho and gradient matched to < 4e-10); the tolerance was
  corrected to the source's print precision BEFORE the full run.  No
  analysis result -- no shell statistic -- had been seen at that point;
  G1 is a deterministic reproduction gate that runs before any variant.
  (c) shell counts equal their targets exactly (doc target for full's
      first three; D15-derived k_R differences for both views' first
      three).
G1 is DETERMINISTIC -- it runs at any N_DRAW / N_BOOT (smoke included).
No threshold is loosened and N is not raised if it fails.

MATCHED CONTROLS (per variant, per view; task doc lines 209-213)
----------------------------------------------------------------
N_DRAW = 200 (smoke at 20), SEED = 0.
* REMOVE-ONE-SHELL is matched by deleting k_s random positions, and
  KEEP-ONLY-SHELL by retaining a random subset of k_s positions, where
  k_s = that shell's position count, chosen UNIFORMLY WITHOUT
  REPLACEMENT from the SAME view's resolved universe.  Whole positions,
  all their variants; the SAME chosen set is applied to EVERY background
  within a draw (script 144's control construction, lines 717-721).
* A FRESH np.random.default_rng(SEED) per (view, shell, variant-type)
  block, exactly as script 144 created a fresh rng per (view, R) -- so
  draws and ranges are reproducible and do not depend on loop order.
* RESAMPLING UNIT: NONE inside a draw.  Each draw is a deterministic
  recomputation on a deleted/retained position set; the spread over
  draws is the DELETION EFFECT, a RE-DERIVATION null, not a bootstrap CI.

WHAT IS REPORTED (per variant: 5 shells x 2 types x 2 views = 20)
-----------------------------------------------------------------
1. Rows retained (A222V; per-background min/median/max; positions kept).
2. A222V's rho (point statistic).  NO position-cluster CI is computed
   here: D18.5 is this session's CI record; D20 reports rho against its
   OWN size-matched range.  Stated in the output too.
3. The gradient Spearman(rho_b, d3_b) on the resolved nulls (n = 67)
   with a BACKGROUND-level bootstrap 95% CI (N_BOOT = 10000, SEED = 0,
   rho_b held FIXED within a draw; a FRESH default_rng(SEED) per variant
   so a variant's CI does not depend on iteration order).  The n = 85
   all-resolved-background gradient is printed as context (no CI; the
   task specifies n = 67).
4. p_spec (n = 78) with k, the nulls at or below A222V, and the frozen
   NUMERIC threshold comparison only (0.05 full / 0.10 H; "at or below"
   / "above", rule 10 -- never a frozen outcome word).
5. rho, gradient and p_spec EACH beside its own size-matched range with
   rule 11's four numbers -- value, range, empirical fraction at or
   below, empirical fraction at or above, distance to the nearest bound
   -- and the flag INSIDE / OUTSIDE / MARGINAL (MARGINAL = outside but
   within 0.002 of a bound, or the one-sided fraction on the outside is
   between 0.01 and 0.05).

RESAMPLING UNITS (rule 4, stated, not interchangeable)
------------------------------------------------------
* matched-control draws -> NONE inside a draw (re-derivation null).
* the gradient CI        -> BACKGROUND, N_BOOT draws, rho_b fixed.
* p_spec, row counts     -> no resampling.
* A222V's rho            -> point statistic this task; no CI run here.

SUMMARY (pre-registered definitions; computed from the same arrays as
the tables, never hand-written numbers)
-----------------------------------------
* "MOST DAMAGING REMOVAL" = the shell whose REMOVE variant has the
  LARGEST DROP in the gradient from the R = 0 baseline
  (drop = grad_R0 - grad_REMOVE).  The rho ordering (largest
  attenuation toward zero: rho_REMOVE - rho_R0, positive = magnitude
  lost) is reported beside it, with whether the two orderings agree.
* "BEST PRESERVES ALONE" = the shell whose KEEP-ONLY variant retains
  the LARGEST FRACTION of the R = 0 gradient (grad_KEEP / grad_R0).
  The rho fraction (rho_KEEP / rho_R0; rho_R0 < 0, so a fraction above 1
  means the magnitude EXCEEDS the baseline) is reported beside it.
* The answer is stated SEPARATELY for each view and the script says
  plainly whether the two views agree.  Overlap of the top shells' own
  matched ranges is printed: overlapping ranges mean their ordering is
  NOT separated by their own controls, and the output says so.

LIMITS STATED IN THE OUTPUT (task doc lines 223-225, plus AGENTS 4/6)
---------------------------------------------------------------------
* Shells differ in SIZE, so effects are compared ONLY with their own
  size-matched control, never across shells.
* The (30,45] and (45,inf) shells are large; KEEP-ONLY of a small shell
  (about 23 positions full, 13 H) leaves few rows per background and a
  noisy rho_b.
* p_spec under a variant compares DIFFERENTLY-THINNED row sets (each
  background has its own usable rows) -- disclosed, not corrected, as
  in D15.
* d3_222 is a CA-CA distance in ONE 2.50 A crystal structure of the
  dimer; a CA-CA distance is not a contact.
* Unresolved positions and their rows are dropped and counted, never
  imputed.
* Rank fractions over small n are rank fractions, not tests (rule 10).

WATERMARKS: descriptive only; no GENERIC / BEATS / INDETERMINATE label
anywhere; no torch / esm / thermompnn import; nothing frozen is
redefined; the frozen PHASE2_PREREG.md verdict is not touched.

RUN (smoke first, then full; time the run, never guess) --
    N_DRAW=20  N_BOOT=200  SEED=0 venv/bin/python3 scripts/150_phase2_diag4_shells.py
    N_DRAW=200 N_BOOT=10000 SEED=0 venv/bin/python3 scripts/150_phase2_diag4_shells.py
Full output is redirected to
    docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D20_FULL_OUTPUT.txt
"""

import os
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3          # noqa: E402
from scripts.lib import phase2_diag4 as p4          # noqa: E402

N_DRAW = int(os.environ.get("N_DRAW", "200"))
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))

D15_OUT = ROOT / "docs/tasks/phase2-diagnostics-iii-mechanism" / \
    "PHASE2_DIAG3_D15_FULL_OUTPUT.txt"
TASK_DOC = ROOT / "docs/tasks/phase2-diagnostics-iv-shells" / \
    "PHASE2_DIAGNOSTICS_IV.md"

TOL9 = 1e-9                      # values D15 printed with 9 decimals
                                 # (rho, gradient: script 144 lines 779/781)
TOL6 = 5e-7                      # values D15 printed with 6 DECIMALS
                                 # (p_spec: script 144 line 783
                                 #  f"{s['p_n78']:>13.6f}"); 5e-7 is the
                                 #  half-ulp of a 6-dp print.  DISCLOSED IN
                                 #  THE OUTPUT: the first smoke run gated
                                 #  p_spec at 1e-9 too; that is unachievable
                                 #  for a 6-dp print by ANY implementation,
                                 #  so the tolerance was set to the source's
                                 #  own print precision BEFORE the full run
                                 #  (no analysis result was involved).
TGT_SHELL_FULL = (23, 98, 126)   # task doc lines 203-204 (first three)
TGT_R30_RHO = -0.027360127       # task doc line 217 (full)
TGT_R30_GRAD = 0.400678440       # task doc line 217 (full)

# shell boundaries on d3_222, in Angstrom: (lo, hi), lo None = 0,
# hi None = inf.  Fixed by the task doc before any run.
SHELLS = ((0.0, 10.0), (10.0, 20.0), (20.0, 30.0),
          (30.0, 45.0), (45.0, np.inf))
SHELL_LABELS = ("(0,10]", "(10,20]", "(20,30]", "(30,45]", "(45,inf)")

GATES = []
T0 = time.time()


def banner(t, ch="="):
    p3.banner(t, ch)


def gate(gid, ok, detail):
    GATES.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}", flush=True)
    return ok


def qline(path, a, b):
    lines = path.read_text().splitlines()
    for i in range(a, b + 1):
        print(f"  {path.relative_to(ROOT)}:{i}: {lines[i - 1]}")


def ov_verdict(ov):
    """Human verdict for 'do the top two shells' own ranges overlap?'"""
    if ov is None:
        return "NOT COMPUTABLE (a range is NaN)"
    if ov:
        return ("OVERLAP: their ordering is NOT separated by their own "
                "matched ranges")
    return ("do NOT overlap: the ordering IS separated by their own "
            "matched ranges")


# ==========================================================================
# Parse D15's printed S1 table (rho / gradient / p_spec per view and R) and
# its printed k_R geometry block out of D15's full output.  Read at run time,
# never copied into this file -- these are the reproduction targets for G1.
# ==========================================================================
TBL = re.compile(r"^\s*(full|H)\s+(\d+)\s+(\d+)\s+([-+]\d+\.\d+)\s+"
                 r"\[[^\]]+\]\s+(?:True|False)\s+([-+]\d+\.\d+)\s+"
                 r"\[[^\]]+\]\s+(\d+\.\d+)")
KR = re.compile(r"^\s+R =\s+(\d+) A: k_R =\s+(\d+) positions removed")
KR_CTX = re.compile(r"^\s*\[(full|H)\] frame positions within each R")


def parse_d15():
    """-> (table, kR): table {(view,R): dict(rho, grad, p, k_R)};
    kR {view: {R: k_R}} from D15's printed geometry block."""
    table, kR, ctx = {}, {}, None
    for line in D15_OUT.read_text().splitlines():
        m = KR_CTX.match(line)
        if m:
            ctx = m.group(1)
            kR.setdefault(ctx, {})
            continue
        m = KR.match(line)
        if m and ctx:
            r, k = int(m.group(1)), int(m.group(2))
            # first occurrence wins: D15's geometry block comes before the
            # matched-deletion headers, which repeat the same values.
            if r not in kR[ctx]:
                kR[ctx][r] = k
            continue
        m = TBL.match(line)
        if m:
            table[(m.group(1), int(m.group(2)))] = dict(
                k_R=int(m.group(3)), rho=float(m.group(4)),
                grad=float(m.group(5)), p=float(m.group(6)))
    return table, kR


# ==========================================================================
# Rule-11 reporting for one statistic against its OWN size-matched draws.
# Prints value, range, BOTH one-sided fractions, distance to nearest bound,
# and the INSIDE / OUTSIDE / MARGINAL flag (rule 11).  NaN-safe: NaN draws
# are counted and excluded from the range/fractions; a NaN observed value
# gets no flag and says so.
# ==========================================================================
def rule11(v, draws, lbl):
    a = np.asarray(draws, float)
    nn = int(np.isnan(a).sum())
    fin = a[~np.isnan(a)]
    print(f"    {lbl}")
    print(f"      variant value                  = {float(v):+.9f}"
          if not np.isnan(v) else
          f"      variant value                  = NaN (not computable "
          f"on this row set)")
    if nn:
        print(f"      *** {nn} of {len(a)} control draws are NaN and are "
              f"EXCLUDED from the range and fractions ({len(fin)} "
              f"finite) ***")
    if np.isnan(v) or len(fin) == 0:
        print("      -> FLAG (rule 11): NONE (NaN; flag not computable)")
        return dict(flag="NAN", lo=np.nan, hi=np.nan, frac_le=np.nan,
                    frac_ge=np.nan, dist=np.nan)
    f = p4.flag11(float(v), fin)
    mean = float(fin.mean())
    sd = float(fin.std(ddof=1)) if len(fin) > 1 else 0.0
    print(f"      matched-control mean           = {mean:+.9f}"
          f"   sd = {sd:.9f}")
    print(f"      matched-control 2.5 / 97.5 pct = [{f['lo']:+.9f}, "
          f"{f['hi']:+.9f}]")
    print(f"      fraction of draws at or below  = {f['frac_le']:.4f};  "
          f"at or above = {f['frac_ge']:.4f}")
    print(f"      distance to nearest bound      = {f['dist']:.9f}   "
          f"(MARGINAL distance threshold 0.002)")
    print(f"      -> FLAG (rule 11): {f['flag']}")
    return f


def main():
    banner("D20 -- SHELL DECOMPOSITION: WHERE DOES THE FAR-VARIANT SIGNAL "
           "LIVE?  (script 150)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No frozen "
          "outcome word is used as a label anywhere.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn import anywhere "
          "in this file.")
    print(f"  N_DRAW={N_DRAW} N_BOOT={N_BOOT} SEED={SEED}")
    print("RESAMPLING UNITS (not interchangeable):")
    print("  * matched-control draws -> NONE inside a draw: a deterministic "
          "recomputation on a deleted/retained position set; the spread is "
          "the DELETION EFFECT (re-derivation null), not a bootstrap CI.")
    print("  * the gradient 95% CI   -> BACKGROUND, N_BOOT draws, rho_b held "
          "FIXED.")
    print("  * p_spec, row counts    -> NO resampling.")
    print("  * A222V's rho           -> point statistic here; NO "
          "position-cluster CI is run in this script (D18.5 is this "
          "session's CI record).")

    # ------------------------------------------------------------ build --
    print("\n  --- building the shared state (script 125 construction via "
          "phase2_diag3.build) ---")
    tb = time.time()
    st = p3.build(verbose=False)
    print(f"  build() elapsed {time.time() - tb:.1f}s")
    bgs, N_ids, resN = st["bgs"], st["N_ids"], st["resN"]
    df3 = st["df3"]
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]
    vs = p4.build_view_state(st)
    print(f"  bgs = {len(bgs)}, N_ids (p_spec nulls) = {len(N_ids)}, "
          f"resN (gradient nulls) = {len(resN)}, res96 = {len(res96)}")

    T15, K15 = parse_d15()
    print(f"  parsed {len(T15)} S1 table rows and k_R geometry for views "
          f"{sorted(K15)} from {D15_OUT.name}")

    # ======================================================== GEOMETRY ====
    banner("GEOMETRY -- THE FIVE SHELLS ON d3_222, PER VIEW", "-")
    print("  QUOTED SOURCE of the premises (D15 full output):")
    qline(D15_OUT, 37, 37)
    qline(D15_OUT, 45, 48)
    qline(D15_OUT, 55, 58)
    print("  QUOTED SOURCE of the shell definition and its targets "
          "(task doc lines 202-204):")
    qline(TASK_DOC, 202, 204)

    shell_pos, counts = {}, {}
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved, d3 = v["POSV"], v["resolved"], v["d3"]
        u = d3[resolved]
        print(f"\n  [{view}] resolved universe = {len(u)} positions;  "
              f"min d3_222 = {u.min():.3f} A;  max = {u.max():.3f} A;  "
              f"positions with d3_222 == 0 = {int((u == 0).sum())}")
        masks, poss, cnts = [], [], []
        for (lo, hi), lbl in zip(SHELLS, SHELL_LABELS):
            m = resolved & (d3 > lo) & (d3 <= hi)
            masks.append(m)
            poss.append(POSV[m])
            cnts.append(int(m.sum()))
        shell_pos[view], counts[view] = poss, cnts
        # every resolved position falls in exactly one shell
        tot = int(np.sum([m.sum() for m in masks]))
        covered = int(np.logical_or.reduce(masks).sum())
        disjoint = all(
            int(np.logical_and(masks[i], masks[j]).sum()) == 0
            for i in range(5) for j in range(i + 1, 5))
        print(f"  [{view}] shell counts: " + "  ".join(
            f"{lbl} = {c}" for lbl, c in zip(SHELL_LABELS, cnts)) +
            f"   (sum = {tot}, resolved = {int(resolved.sum())})")
        gate(f"D20-G1c shells partition the {view} resolved universe",
             tot == int(resolved.sum()) and covered == int(resolved.sum())
             and disjoint,
             f"sum of shell counts = {tot} vs resolved = "
             f"{int(resolved.sum())}; union = {covered}; pairwise "
             f"intersections all empty = {disjoint}")
        # unresolved rows dropped from EVERY variant, counted, never imputed
        ra_unres = int((~resolved)[v["A"].code].sum())
        per = [int((~resolved)[s.code].sum()) for s in v["B"].values()]
        print(f"  [{view}] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM "
              f"EVERY VARIANT INCLUDING THE R = 0 BASELINE, NEVER IMPUTED: "
              f"A222V {ra_unres} of {len(v['A'].pos)} rows; per background "
              f"min = {min(per)}, max = {max(per)} ***")

    # ------------------- shell-count targets (rule 2: recompute vs doc) --
    print("\n  SHELL COUNTS vs THEIR TARGETS (rule 2 -- the doc's values "
          "are recomputations, not facts):")
    for i in range(3):                      # first three shells
        doc_t = TGT_SHELL_FULL[i]
        mine_full = counts["full"][i]
        d15_full = K15["full"][10 * (i + 1)] - (K15["full"][10 * i] if i
                                                else 0)
        ok_doc = gate(
            f"D20-G1c full shell {SHELL_LABELS[i]} count vs doc target "
            f"{doc_t}", mine_full == doc_t,
            f"recomputed from d3_222 = {mine_full};  D15 k_R-derived = "
            f"{d15_full};  doc target = {doc_t}  (MISMATCH would mean the "
            f"doc is wrong -- both numbers printed above)")
        gate(f"D20-G1c full shell {SHELL_LABELS[i]} count vs D15 k_R "
             f"difference", mine_full == d15_full,
             f"recomputed = {mine_full} vs D15 k_R-derived = {d15_full} "
             f"(exact integer equality)")
        if not ok_doc:
            print("    *** DOC TARGET MISMATCH on a shell count: the two "
                  "numbers are printed above; this item STOPS (rule 2). ***")
    for i in range(3):                      # H view, D15-derived only
        mine_h = counts["H"][i]
        d15_h = K15["H"][10 * (i + 1)] - (K15["H"][10 * i] if i else 0)
        gate(f"D20-G1c H shell {SHELL_LABELS[i]} count vs D15 k_R "
             f"difference", mine_h == d15_h,
             f"recomputed = {mine_h} vs D15 k_R-derived = {d15_h} (exact "
             f"integer equality)")
    print("  The two large shells have no doc target; REPORTED:")
    for view in p3.VIEWS:
        print(f"    {view}: (30,45] = {counts[view][3]}, (45,inf) = "
              f"{counts[view][4]}  (no target exists -- reported as is)")

    # ======================================================== GATE G1 =====
    banner("GATE D20-G1 (HARD) -- zero-deletion == R = 0 baseline; union of "
           "the first three shells == D15's R = 30", "-")
    print("  QUOTED SOURCE of the gate (task doc lines 215-217):")
    qline(TASK_DOC, 215, 217)
    print("  TOLERANCES: compared against D15's PRINTED rows, each "
          "quantity is gated at its own print precision -- rho and "
          "gradient 9-dp prints -> 1e-9; p_spec is a 6-dp print (script "
          "144 line 783) -> 5e-7.  DISCLOSURE: the first smoke run used a "
          "uniform 1e-9, which a 6-dp print cannot satisfy for ANY "
          "implementation; corrected to print precision before the full "
          "run, with no shell statistic seen (G1 runs first).")

    base, keep0 = {}, {}
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved = v["POSV"], v["resolved"]
        k0 = p4.keep_from_removed(POSV, resolved, [])
        k_direct = resolved.copy()
        s0 = p4.stats(v, bgs, N_ids, resN, res96, df3, k0)
        s_direct = p4.stats(v, bgs, N_ids, resN, res96, df3, k_direct)
        base[view], keep0[view] = s0, k0
        same_mask = bool(np.array_equal(k0, k_direct))
        dstat = max(abs(float(s0[kk]) - float(s_direct[kk])) for kk in
                    ("rho_a", "grad_n67", "grad_n85", "k_n78", "k_n67"))
        gate(f"D20-G1a zero-deletion == R = 0 baseline ({view})",
             same_mask and dstat == 0.0,
             f"keep arrays identical = {same_mask} (required True); "
             f"max|diff| over rho_A222V, both gradients and both k's = "
             f"{dstat:.3e} (required EXACTLY 0)")
        t = T15[(view, 0)]
        parts = [("rho", s0["rho_a"], t["rho"], TOL9),
                 ("gradient n=67", s0["grad_n67"], t["grad"], TOL9),
                 ("p_spec n=78", s0["p_n78"], t["p"], TOL6)]
        worst = max(parts, key=lambda p: abs(p[1] - p[2]))
        gate(f"D20-G1a R = 0 baseline reproduces D15's printed row "
             f"({view})", all(abs(p[1] - p[2]) < p[3] for p in parts),
             f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 printed "
             f"{worst[2]!r} |diff| = {abs(worst[1] - worst[2]):.3e} "
             f"(gate < {worst[3]:g} = that quantity's print precision); "
             f"all: " + ", ".join(
                 f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                 for p in parts))
        print(f"    [{view}] R = 0 baseline: A222V rho = {s0['rho_a']:+.9f}; "
              f"gradient n=67 = {s0['grad_n67']:+.9f}; gradient n=85 = "
              f"{s0['grad_n85']:+.9f}; p_spec n=78 = {s0['p_n78']:.9f} "
              f"(k = {s0['k_n78']})")

    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved, d3 = v["POSV"], v["resolved"], v["d3"]
        union = np.concatenate(shell_pos[view][:3])
        k_union = p4.keep_from_removed(POSV, resolved, union)
        rm30 = POSV[resolved & (d3 <= 30.0)]
        k_30 = p4.keep_from_removed(POSV, resolved, rm30)
        same_mask = bool(np.array_equal(k_union, k_30))
        s = p4.stats(v, bgs, N_ids, resN, res96, df3, k_union)
        t = T15[(view, 30)]
        print(f"\n  [{view}] REMOVE union of shells (0,10]+(10,20]+"
              f"(20,30] = {len(union)} positions; D15's R = 30 removed "
              f"{t['k_R']} positions from D15's own k_R print")
        gate(f"D20-G1b union keep-mask == R = 30 keep-mask ({view})",
             same_mask,
             f"boolean arrays identical = {same_mask} (required EXACTLY "
             f"True); union count = {len(union)}, R = 30 count = "
             f"{len(rm30)}")
        parts = [("rho", s["rho_a"], t["rho"], TOL9),
                 ("gradient n=67", s["grad_n67"], t["grad"], TOL9),
                 ("p_spec n=78", s["p_n78"], t["p"], TOL6)]
        worst = max(parts, key=lambda p: abs(p[1] - p[2]))
        gate(f"D20-G1b union removal reproduces D15's printed R = 30 row "
             f"({view})", all(abs(p[1] - p[2]) < p[3] for p in parts),
             f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 printed "
             f"{worst[2]!r} |diff| = {abs(worst[1] - worst[2]):.3e} "
             f"(gate < {worst[3]:g} = that quantity's print precision); "
             f"all: " + ", ".join(
                 f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                 for p in parts))
        if view == "full":
            for lbl, got, want in (("A222V rho", s["rho_a"], TGT_R30_RHO),
                                   ("gradient n=67", s["grad_n67"],
                                    TGT_R30_GRAD)):
                d = abs(got - want)
                gate(f"D20-G1b union removal reproduces the DOC target "
                     f"({lbl}, full)", d < TOL9,
                     f"recomputed {got!r}  vs  doc target {want!r}  "
                     f"|diff| = {d:.3e} (gate < {TOL9:g})")
        # second instance of the same construction: shell (0,10] alone IS
        # D15's R = 10 removal set (min d3_222 = 3.805 > 0, printed above)
        k10 = p4.keep_from_removed(POSV, resolved, shell_pos[view][0])
        s10 = p4.stats(v, bgs, N_ids, resN, res96, df3, k10)
        t10 = T15[(view, 10)]
        parts10 = [("rho", s10["rho_a"], t10["rho"], TOL9),
                   ("gradient n=67", s10["grad_n67"], t10["grad"], TOL9),
                   ("p_spec n=78", s10["p_n78"], t10["p"], TOL6)]
        worst10 = max(parts10, key=lambda p: abs(p[1] - p[2]))
        gate(f"D20-G1b REMOVE shell (0,10] reproduces D15's printed "
             f"R = 10 row ({view})",
             all(abs(p[1] - p[2]) < p[3] for p in parts10),
             f"worst is {worst10[0]}: recomputed {worst10[1]!r} vs D15 "
             f"printed {worst10[2]!r} |diff| = "
             f"{abs(worst10[1] - worst10[2]):.3e} (gate < {worst10[3]:g} = "
             f"that quantity's print precision); all: " + ", ".join(
                 f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                 for p in parts10))

    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D20-G1: {len(GATES) - n_fail}/{len(GATES)} checks PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("*** D20 GATE FAIL -- D20 stops here (task doc rule 6).  No "
              "threshold was loosened and N was not raised. ***")
        print(f"\nElapsed {time.time() - T0:.1f}s")
        sys.exit(1)
    print("  GATE PASS: D20-G1 satisfied.  The shell analysis may run.")

    # ======================================================== VARIANTS ====
    banner("THE VARIANTS -- 5 shells x REMOVE / KEEP-ONLY x 2 views, each "
           "against its OWN size-matched control", "-")
    print(f"  Matched controls: N_DRAW = {N_DRAW}, SEED = {SEED}.  A FRESH "
          "np.random.default_rng(SEED) per (view, shell, variant-type) "
          "block, exactly as script 144 created a fresh rng per (view, R), "
          "so draws do not depend on loop order.")
    print("  REMOVE is matched by DELETING k_s random positions from the "
          "resolved universe; KEEP-ONLY by RETAINING a random subset of "
          "k_s positions; whole positions, same chosen set for every "
          "background within a draw.")
    print("  REPORTING RULE (task doc rule 11): value, range, fraction at "
          "or below, fraction at or above, distance to nearest bound, "
          "INSIDE / OUTSIDE / MARGINAL.")
    if N_DRAW != 200:
        print(f"  *** N_DRAW = {N_DRAW}, NOT 200 (smoke run): ranges and "
              "flags below are smoke values; the full run uses 200. ***")

    res = {}       # (view, si, kind) -> dict
    ctrl = {}      # (view, si, kind) -> dict of draw arrays
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved = v["POSV"], v["resolved"]
        univ = v["univ_pos"]
        for si in range(5):
            lbl = SHELL_LABELS[si]
            sp = shell_pos[view][si]
            k_s = counts[view][si]
            for kind in ("rm", "kp"):
                if kind == "rm":
                    keep = p4.keep_from_removed(POSV, resolved, sp)
                    cdesc = (f"DELETING {k_s} random positions per draw "
                             f"from the {len(univ)}-position resolved "
                             f"universe")
                else:
                    keep = resolved & np.isin(POSV, sp)
                    cdesc = (f"RETAINING a random {k_s}-position subset "
                             f"per draw of the {len(univ)}-position "
                             f"resolved universe")
                s = p4.stats(v, bgs, N_ids, resN, res96, df3, keep)
                glo, ghi, gv, gnan = p4.grad_boot(
                    s["rho_b"], resN, df3, N_BOOT,
                    np.random.default_rng(SEED))
                kind_lbl = ("REMOVE-ONE-SHELL" if kind == "rm"
                            else "KEEP-ONLY-SHELL")
                rwl = "removed" if kind == "rm" else "retained"
                print(f"\n  === [{view}] {kind_lbl} shell {lbl}: k_s = "
                      f"{k_s} positions ({rwl}), {int(keep.sum())} of "
                      f"{int(resolved.sum())} resolved positions kept ===")
                print(f"    rows retained: A222V = {s['n_rows_a']};  across "
                      f"the {len(bgs)} backgrounds min = "
                      f"{s['rows'].min()}, median = "
                      f"{int(np.median(s['rows']))}, max = "
                      f"{s['rows'].max()};  positions kept = "
                      f"{s['n_pos']}")
                print(f"    A222V rho (point; no cluster CI run here, "
                      f"D18.5 holds the CIs) = {s['rho_a']:+.9f}")
                excl = (glo > 0 or ghi < 0)
                print(f"    gradient Spearman(rho_b, d3_b) on resolved "
                      f"nulls n = {len(resN)}: {s['grad_n67']:+.9f}  "
                      f"BACKGROUND-level bootstrap 95% CI = "
                      f"[{glo:+.6f}, {ghi:+.6f}] ({gv} usable, {gnan} nan, "
                      f"{N_BOOT} draws, SEED={SEED})  "
                      f"{'EXCLUDES ZERO' if excl else 'INCLUDES ZERO'}")
                print(f"    gradient on all resolved backgrounds "
                      f"n = {len(res96)} (context only, no CI -- the task "
                      f"specifies n = 67): {s['grad_n85']:+.9f}")
                thr = 0.05 if view == "full" else 0.10
                where = ("at or below" if s["p_n78"] <= thr else "above")
                print(f"    p_spec (n = {len(N_ids)} nulls, frozen "
                      f"direction rho_b <= rho_A222V): k = {s['k_n78']}, "
                      f"p_spec = {s['p_n78']:.9f}   at or below: "
                      f"{', '.join(s['aob_n78']) if s['aob_n78'] else 'NONE'}"
                      f"   -> {where} the frozen numeric threshold {thr} "
                      f"({view})")

                # ---- matched control -----------------------------------
                acc = {kk: np.empty(N_DRAW, float)
                       for kk in ("rho_a", "grad_n67", "p_n78")}
                if k_s == 0:
                    print("    *** k_s = 0 (empty shell): no matched "
                          "control is possible; skipped with the count "
                          "printed. ***")
                    for kk in acc:
                        acc[kk][:] = np.nan
                else:
                    rg = np.random.default_rng(SEED)
                    for i in range(N_DRAW):
                        if kind == "rm":
                            drop = rg.choice(univ, size=k_s, replace=False)
                            kk_keep = p4.keep_from_removed(POSV, resolved,
                                                           drop)
                        else:
                            sub = rg.choice(univ, size=k_s, replace=False)
                            kk_keep = resolved & np.isin(POSV, sub)
                        sd_ = p4.stats(v, bgs, N_ids, resN, res96, df3,
                                       kk_keep)
                        acc["rho_a"][i] = float(sd_["rho_a"])
                        acc["grad_n67"][i] = float(sd_["grad_n67"])
                        acc["p_n78"][i] = float(sd_["p_n78"])
                print(f"    --- matched control ({cdesc}; N_DRAW = "
                      f"{N_DRAW}, SEED = {SEED}; no resampling inside a "
                      f"draw) ---")
                fl = {}
                for kk, olbl in (("rho_a", "A222V rho"),
                                 ("grad_n67", "gradient n=67"),
                                 ("p_n78", "p_spec n=78")):
                    fl[kk] = rule11(s[kk], acc[kk], olbl)
                res[(view, si, kind)] = dict(s=s, fl=fl, glo=glo, ghi=ghi)
                ctrl[(view, si, kind)] = acc

    # ======================================================== SUMMARY =====
    banner("D20 SUMMARY TABLE A -- the GRADIENT (n = 67): REMOVE effect and "
           "KEEP-ONLY retained fraction, each with its own matched flag",
           "-")
    print(f"  {'view':>5s} {'shell':>9s} {'k_s':>5s} {'R0 grad':>12s} "
          f"{'REMOVE grad':>14s} {'drop':>12s} {'drop %':>8s} "
          f"{'flag':>9s} {'KEEP grad':>13s} {'frac of R0':>11s} "
          f"{'flag':>9s}")
    for view in p3.VIEWS:
        g0 = base[view]["grad_n67"]
        for si in range(5):
            r_rm = res[(view, si, "rm")]
            r_kp = res[(view, si, "kp")]
            gr, gk = r_rm["s"]["grad_n67"], r_kp["s"]["grad_n67"]
            drop = g0 - gr
            frac = gk / g0 if g0 != 0 else float("nan")
            print(f"  {view:>5s} {SHELL_LABELS[si]:>9s} "
                  f"{counts[view][si]:>5d} {g0:>+12.9f} {gr:>+14.9f} "
                  f"{drop:>+12.9f} {100.0 * drop / g0:>7.2f}% "
                  f"{r_rm['fl']['grad_n67']['flag']:>9s} {gk:>+13.9f} "
                  f"{frac:>11.4f} {r_kp['fl']['grad_n67']['flag']:>9s}")
    print("  drop = R0 - REMOVE (positive = gradient fell);  drop % = drop "
          "relative to that view's R = 0 gradient;  frac of R0 = "
          "KEEP / R0 (fraction of the baseline gradient retained).")

    banner("D20 SUMMARY TABLE B -- A222V's RHO: REMOVE effect and "
           "KEEP-ONLY retained fraction, each with its own matched flag",
           "-")
    print(f"  {'view':>5s} {'shell':>9s} {'k_s':>5s} {'R0 rho':>13s} "
          f"{'REMOVE rho':>13s} {'change':>12s} {'|chg| %R0':>10s} "
          f"{'flag':>9s} {'KEEP rho':>13s} {'frac of R0':>11s} "
          f"{'flag':>9s}")
    for view in p3.VIEWS:
        r0 = base[view]["rho_a"]
        for si in range(5):
            r_rm = res[(view, si, "rm")]
            r_kp = res[(view, si, "kp")]
            rr, rk = r_rm["s"]["rho_a"], r_kp["s"]["rho_a"]
            chg = rr - r0
            frac = rk / r0 if r0 != 0 else float("nan")
            print(f"  {view:>5s} {SHELL_LABELS[si]:>9s} "
                  f"{counts[view][si]:>5d} {r0:>+13.9f} {rr:>+13.9f} "
                  f"{chg:>+12.9f} {100.0 * chg / abs(r0):>9.2f}% "
                  f"{r_rm['fl']['rho_a']['flag']:>9s} {rk:>+13.9f} "
                  f"{frac:>11.4f} {r_kp['fl']['rho_a']['flag']:>9s}")
    print("  change = REMOVE - R0 (rho_R0 < 0, so a POSITIVE change means "
          "the association's magnitude was attenuated);  frac of R0 = "
          "KEEP / R0 (both negative is a positive fraction; ABOVE 1 means "
          "the magnitude EXCEEDS the baseline).")

    banner("D20 SUMMARY TABLE C -- p_spec (n = 78) values and flags "
           "against the frozen NUMERIC thresholds (rule 10)", "-")
    for view in p3.VIEWS:
        thr = 0.05 if view == "full" else 0.10
        for si in range(5):
            for kind in ("rm", "kp"):
                s = res[(view, si, kind)]["s"]
                where = ("at or below" if s["p_n78"] <= thr else "above")
                knd = "REMOVE" if kind == "rm" else "KEEP  "
                print(f"    {view:>4s} {knd} shell {SHELL_LABELS[si]:>9s}: "
                      f"p_spec = {s['p_n78']:.9f} (k = {s['k_n78']}) -> "
                      f"{where} the threshold {thr}   flag vs its own "
                      f"size-matched range: "
                      f"{res[(view, si, kind)]['fl']['p_n78']['flag']}")

    # ======================================================== THE ANSWER ===
    banner("THE ANSWER -- which shell's removal is most damaging, which "
           "shell alone best preserves the signal", "-")
    print("  Pre-registered definitions (docstring): 'most damaging "
          "removal' = largest gradient drop from R = 0; 'best preserves "
          "alone' = largest retained fraction of the R = 0 gradient.  "
          "Both computed from the tables above.")
    answer = {}
    for view in p3.VIEWS:
        g0 = base[view]["grad_n67"]
        r0 = base[view]["rho_a"]
        drops = np.array([g0 - res[(view, si, "rm")]["s"]["grad_n67"]
                          for si in range(5)])
        fracs = np.array([res[(view, si, "kp")]["s"]["grad_n67"] / g0
                          for si in range(5)])
        atten = np.array([res[(view, si, "rm")]["s"]["rho_a"] - r0
                          for si in range(5)])
        rfracs = np.array([res[(view, si, "kp")]["s"]["rho_a"] / r0
                           for si in range(5)])
        order_drop = np.argsort(-drops)          # most damaging first
        order_frac = np.argsort(-fracs)          # best preserving first
        order_att = np.argsort(-atten)           # most rho attenuation first
        i1, i2 = int(order_drop[0]), int(order_drop[1])
        j1, j2 = int(order_frac[0]), int(order_frac[1])
        # are the top two separated by their OWN matched ranges?
        def _ov(f1, f2):
            if np.isnan(f1["lo"]) or np.isnan(f2["lo"]):
                return None                      # ranges not computable
            return not (f1["hi"] < f2["lo"] or f2["hi"] < f1["lo"])
        gi1 = res[(view, i1, "rm")]["fl"]["grad_n67"]
        gi2 = res[(view, i2, "rm")]["fl"]["grad_n67"]
        rm_overlap = _ov(gi1, gi2)
        gj1 = res[(view, j1, "kp")]["fl"]["grad_n67"]
        gj2 = res[(view, j2, "kp")]["fl"]["grad_n67"]
        kp_overlap = _ov(gj1, gj2)
        answer[view] = dict(i1=i1, j1=j1, drops=drops, fracs=fracs,
                            atten=atten, rfracs=rfracs,
                            rm_overlap=rm_overlap, kp_overlap=kp_overlap,
                            i2=i2, j2=j2)
        print(f"\n  --- {view} view (R = 0 gradient {g0:+.9f}, R = 0 rho "
              f"{r0:+.9f}) ---")
        print(f"    gradient drop by shell (REMOVE, descending): " +
              ", ".join(f"{SHELL_LABELS[si]} {drops[si]:+.6f}"
                        for si in order_drop))
        print(f"    MOST DAMAGING REMOVAL = shell {SHELL_LABELS[i1]} "
              f"(k = {counts[view][i1]}): gradient {g0:+.9f} -> "
              f"{res[(view, i1, 'rm')]['s']['grad_n67']:+.9f} (drop "
              f"{drops[i1]:+.9f}, {100.0 * drops[i1] / g0:.2f}% of R0), "
              f"flag {gi1['flag']}")
        print(f"    next = shell {SHELL_LABELS[i2]} (drop "
              f"{drops[i2]:+.9f}, flag {gi2['flag']})")
        print(f"    separation check (rule 11, own ranges): the top two "
              f"REMOVE gradient ranges are "
              f"[{gi1['lo']:+.9f}, {gi1['hi']:+.9f}] and "
              f"[{gi2['lo']:+.9f}, {gi2['hi']:+.9f}] -> "
              f"{ov_verdict(rm_overlap)}")
        print(f"    rho attenuation by shell (REMOVE, descending): " +
              ", ".join(f"{SHELL_LABELS[si]} {atten[si]:+.6f}"
                        for si in order_att))
        print(f"    the rho ordering says most damaging = shell "
              f"{SHELL_LABELS[int(order_att[0])]} -> "
              f"{'AGREES' if int(order_att[0]) == i1 else 'DIFFERS'} with "
              f"the gradient ordering")
        print(f"    retained fraction of R = 0 gradient by shell "
              f"(KEEP-ONLY, descending): " +
              ", ".join(f"{SHELL_LABELS[si]} {fracs[si]:.4f}"
                        for si in order_frac))
        print(f"    BEST PRESERVES ALONE = shell {SHELL_LABELS[j1]} "
              f"(k = {counts[view][j1]}): gradient "
              f"{res[(view, j1, 'kp')]['s']['grad_n67']:+.9f} = "
              f"{100.0 * fracs[j1]:.2f}% of R0, flag {gj1['flag']}")
        print(f"    next = shell {SHELL_LABELS[j2]} (fraction "
              f"{fracs[j2]:.4f}, flag {gj2['flag']})")
        print(f"    separation check: the top two KEEP gradient ranges are "
              f"[{gj1['lo']:+.9f}, {gj1['hi']:+.9f}] and "
              f"[{gj2['lo']:+.9f}, {gj2['hi']:+.9f}] -> "
              f"{ov_verdict(kp_overlap)}")
        print(f"    rho fraction (KEEP / R0) by shell: " +
              ", ".join(f"{SHELL_LABELS[si]} {rfracs[si]:.4f}"
                        for si in range(5)) +
              "   (above 1.0000 = magnitude exceeds baseline)")
        print(f"    rho ordering of KEEP preservation says best = shell "
              f"{SHELL_LABELS[int(np.argsort(-rfracs)[0])]} -> "
              f"{'AGREES' if int(np.argsort(-rfracs)[0]) == j1 else 'DIFFERS'} "
              f"with the gradient ordering")

    same_rm = answer["full"]["i1"] == answer["H"]["i1"]
    same_kp = answer["full"]["j1"] == answer["H"]["j1"]
    print("\n  BETWEEN THE TWO VIEWS:")
    print(f"    most damaging removal: full = "
          f"{SHELL_LABELS[answer['full']['i1']]}, H = "
          f"{SHELL_LABELS[answer['H']['i1']]} -> "
          f"{'the SAME shell in both views' if same_rm else 'DIFFERS between the two views'}")
    print(f"    best preserving alone: full = "
          f"{SHELL_LABELS[answer['full']['j1']]}, H = "
          f"{SHELL_LABELS[answer['H']['j1']]} -> "
          f"{'the SAME shell in both views' if same_kp else 'DIFFERS between the two views'}")

    # ======================================================== LIMITS ======
    banner("LIMITS STATED WITH THE RESULT (AGENTS 6; task doc lines "
           "223-225)", "-")
    print("  * SHELLS DIFFER IN SIZE, so every effect above is compared "
          "ONLY with its own size-matched control, never across shells: "
          "the tables report each variant against the range from deleting/"
          "retaining the SAME NUMBER of random positions.")
    print("  * The (30,45] and (45,inf) shells are LARGE: " +
          ", ".join(f"{view} (30,45] = {counts[view][3]}, (45,inf) = "
                    f"{counts[view][4]}" for view in p3.VIEWS) + ".")
    print("  * KEEP-ONLY of a SMALL shell leaves few rows per background "
          "and a noisy rho_b:")
    for view in p3.VIEWS:
        rkp = res[(view, 0, "kp")]["s"]
        print(f"      {view} (0,10] keeps {int(rkp['rows'].min())}-"
              f"{int(rkp['rows'].max())} rows per background (A222V "
              f"{rkp['n_rows_a']} rows, {rkp['n_pos']} positions)")
    print("  * p_spec under a variant compares DIFFERENTLY-THINNED row "
          "sets (each background has its own usable rows), exactly as in "
          "D15: disclosed, not corrected.")
    print("  * A222V's rho here has NO bootstrap CI by construction of "
          "this task; D18.5 holds the session's corrected CIs.  The "
          "matched range answers only 'is this what the same NUMBER of "
          "random positions does?', not 'is it nonzero'.")
    print("  * d3_222 is a CA-CA distance in ONE 2.50 A crystal structure "
          "of the dimer; a CA-CA distance is not a contact.")
    print("  * Unresolved positions and their rows are dropped and "
          "counted (printed per view above), never imputed.")
    print("  * Rank fractions over small n are rank fractions, not tests "
          "(rule 10).  p_spec is compared only to the frozen numeric "
          "thresholds 0.05 (full) / 0.10 (H).")
    print("  * The matched-deletion spread is a RE-DERIVATION null over "
          f"{N_DRAW} draws; the smallest one-sided fraction it can "
          f"resolve is {1.0 / N_DRAW:.4f}.")

    # ======================================================== GATE TABLE ==
    banner("D20 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in GATES:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D20 gates: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("*** D20 GATE FAIL -- see above (task doc rule 6). ***")
    print(f"\nElapsed {time.time() - T0:.1f}s")


if __name__ == "__main__":
    main()
