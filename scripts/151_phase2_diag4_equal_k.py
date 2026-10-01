"""
Script 151 (task D21 of docs/tasks/phase2-diagnostics-iv-shells/
PHASE2_DIAGNOSTICS_IV.md) -- EQUAL-k ORDERING TEST: sequence, 3D, or random?

PRE-REGISTERED: this docstring was written BEFORE the first run of this
script.  Nothing below was chosen after seeing a result.

WHY
---
Diagnostics III (D15) compared removing the 100 sequence-nearest positions
(SEQ Rs = 50) with removing the 247 3D-nearest positions (3D R = 30) and
concluded the statistic "tracks 3D distance".  Unequal counts cannot support
that.  This task compares SEQ-k against 3D-k AT THE SAME k, each against its
own RANDOM-k range (task doc lines 231-232, quoted in the output).

UNIVERSE AND k VALUES (task doc lines 234-237; every target recomputed
independently here and printed beside the doc's number -- rule 2)
--------------------------------------------------------------------
Universe = each view's RESOLVED target positions (doc targets: 595 full /
418 H).  For each view, four k values: k_seq(25), k_seq(50), k_R(20 A),
k_R(30 A).  Doc targets for the FULL frame: 50, 100, 121, 247; H: computed
here (the doc gives no H target).  A mismatch means the DOC is wrong: both
numbers are printed and that item stops (no forcing agreement).

CONFIRMATION BY READING scripts/144 (quoted in the output, lines 565-572)
--------------------------------------------------------------------------
D15's sequence sensitivities kept `resolved & ~np.isin(POSV, rm)` (line
572) -- i.e. they DID drop unresolved-position rows -- so D15's printed SEQ
values are on the RESOLVED universe, the same row set as D21's SEQ-k, and
under the task doc's conditional (lines 245-247) they therefore ARE identity
gates.  This also reconciles D15's printed "positions retained = 495" for
Rs = 50: 495 = 595 - 100 (resolved universe), not 654 - 100 = 554 (frame
size; D15 line 37 frame = 654, line 40 resolved = 595, line 141 retained =
495).  The reconciliation arithmetic is printed at run time.

THE THREE SETS (per view, per k)
-------------------------------
* SEQ-k   : the k resolved positions with the smallest |p - 222|, ties by
            ascending position.
* 3D-k    : the k resolved positions with the smallest d3_222, ties by
            ascending position.
* RANDOM-k: k random positions drawn UNIFORMLY WITHOUT REPLACEMENT from the
            same view's resolved universe, N_DRAW = 200 draws (smoke at 20),
            SEED = 0, with a FRESH np.random.default_rng(SEED) per (view, k)
            block -- script 144's control construction (lines 717-721).
            At k = k_R(20) and k = k_R(30) this block is bit-for-bit D15's
            own matched-deletion stream (same seed, same universe, same
            size), so it is gated against D15's printed ranges (G1g).

At each slot BOTH sets are computed at that slot's k: e.g. at the
k_R(20) slot (k = 121 full / 86 H) the report shows SEQ-121 against
3D-121 (= D15's R = 20 set), and at the k_seq(25) slot (k = 50 full /
25 H) it shows SEQ-50 (= D15's SEQ Rs = 25 set) against 3D-50.

REPORTED (per view per k)
-------------------------
1. SEQ-k vs 3D-k OVERLAP: intersection count and Jaccard.
2. For each of SEQ-k and 3D-k: A222V's rho (POINT -- no bootstrap CI is
   computed in this script; D18.5 is this session's CI record), the
   gradient Spearman(rho_b, d3_b) on the resolved nulls (n = 67), p_spec
   (n = 78) with the frozen NUMERIC threshold comparison only ("at or
   below" / "above" 0.05 full / 0.10 H, rule 10), and EACH beside its own
   RANDOM-k range with rule 11's numbers (value, 2.5/97.5 pct range,
   fraction at or below, fraction at or above, distance to nearest bound)
   and the flag INSIDE / OUTSIDE / MARGINAL.

GATES (pre-registered; HARD -- any failure stops D21, task doc rule 6)
----------------------------------------------------------------------
"Exactly 0 difference" against a PRINTED value is checked as: (i) the keep
MASKS are identical boolean arrays (a true zero), and (ii) |value - printed|
<= 5e-10, the half-ulp of D15's 9-decimal print (rho and gradient: script
144 lines 779/781); p_spec is a 6-decimal print (line 783) -> 5e-7;
fractions are 4-decimal prints -> 5e-5.  A difference above those bounds is
a real disagreement and fails the gate.
* D21-G1a (per view): resolved count == doc target 595 / 418 (line 234)
  AND == D15's printed retained count at R = 0 (D15 lines 45 / 55).
* D21-G1b (per view, per k): recomputed k vs the doc target (full only,
  lines 235-237) AND vs D15's independent prints -- SEQ: resolved minus
  positions-retained from D15's SEQ blocks (lines 131 / 141 / 211 / 221);
  3D: D15's printed k_R (lines 45-48 / 55-58).  Plus the 495
  reconciliation itself (doc line 237).
* D21-G1c (per slot): SET EQUIVALENCE where a D15 construction exists --
  at the SEQ-window slots, SEQ-k's keep mask == D15's window keep mask
  `resolved & ~isin(|p - 222| <= Rs)`; at the 3D slots, 3D-k's keep mask ==
  D15's keep_from_removed of {d3_222 <= R} (script 144 lines 566-568: rm =
  POSV[resolved & (d3 <= R)], then keep = resolved & ~rm, i.e. resolved &
  (d3 > R) -- a KEEP mask, never the removed set); boolean arrays IDENTICAL.
  DISCLOSURE (AGENTS 6): smoke attempt 1 (2026-09-30) FAILED these four
  checks because I first wrote the 3D comparison as `resolved & (d3 <= R)` -
  the REMOVED set, which keeps 121 where the keep mask keeps 474.  The
  comparison expression was corrected to script 144's actual construction
  after that 0.8s gate-only run, which computed NO statistic and NO control
  draw; the gate's RULE (mask identity vs D15's construction) is unchanged,
  only its expression was fixed.
  (The other method's set at a slot has no D15 counterpart and is gated by
  nothing but the same code path; said in the output.)
* D21-G1d (task doc line 244, HARD): 3D-k at k_R(20) and k_R(30)
  reproduces D15's S1 R = 20 / R = 30 A222V rho and gradient (n = 67) --
  plus p_spec, k and k_R -- for BOTH views, within the print precisions
  above.
* D21-G1e: SEQ-k at k_seq(25) and k_seq(50) reproduces D15's printed SEQ
  rows (rho, gradient n = 67, p_spec k, positions retained), both views.
* D21-G1f (per view): deleting ZERO positions reproduces the baseline
  EXACTLY (keep arrays identical, max|diff| = 0 over rho, gradient, both
  k's) AND the baseline reproduces D15's printed R = 0 row.
* D21-G1g (full run only, N_DRAW = 200): the RANDOM-k blocks at
  k_R(20)/k_R(30) reproduce D15's printed matched-deletion gradient range
  and BOTH fractions (same seed and stream as D15's control).  A run with
  N_DRAW != 200 cannot equal a 200-draw range: the check prints SKIP with
  that reason and RUNS IN THE FULL RUN.
  DISCLOSURE (AGENTS 6): full-run attempt 1 (2026-09-30, N_DRAW = 200,
  118.1s) EXITED 1 with a KeyError at this gate BEFORE evaluating any
  G1g check: the MD pattern expected the header "(n=200):" but D15
  prints "(n=200 draws):", so 0 matched-deletion lines were parsed and the
  gate crashed on MD15[(view, R)].  This was a REGEX DEFECT IN THIS SCRIPT --
  not a disagreement between two sources (a parser miss is not evidence
  about anything).  The crashed run's own output already showed the four
  recomputed RANDOM-k gradient ranges equal D15's printed ones exactly
  (full R=20/30 and H R=20/30, output lines 180/186/204/210 vs D15 lines
  645/647/653/655), i.e. the stream identity the gate tests held; only
  the pattern was wrong.  Fix: the word " draws" added to the pattern and
  a parse-count guard (8/8/4) added so a future parse miss fails with a
  clear message instead of a KeyError.  NO threshold, tolerance or
  decision rule was changed, and no G1g value had been printed when the
  attempt failed.
* D21-G1h (null identity, AGENTS 4; deterministic at any N): every RANDOM
  draw keeps exactly len(universe) - k positions; recomputing a block's
  FIRST draw from a fresh default_rng(SEED) reproduces it exactly
  (max|diff| = 0).

DECISION RULES (pre-registered -- task doc lines 249-251)
---------------------------------------------------------
At each (view, k):
* gradient drop     = grad(R = 0 baseline) - grad(set)  (positive = fell)
* rho attenuation   = rho(set) - rho(R = 0)  (rho_0 < 0; positive = the
  association's magnitude was lost)
* "3D-k IS MORE DESTRUCTIVE THAN SEQ-k" is asserted only if 3D-k has the
  LARGER gradient drop AND the LARGER rho attenuation; if the two metrics
  disagree the output prints DISAGREE with both pairs (no metric is picked
  after seeing which one it favours).
* On the gradient (the statistic D15's claim was about), against RANDOM-k:
    3D-k OUTSIDE while SEQ-k INSIDE -> "SUPPORTED at this k"
    both INSIDE                     -> "UNSUPPORTED at this k: the '3D not
                                        sequence' claim is WITHDRAWN at
                                        this k"
    any other combination           -> printed with the exact flags and no
                                        stronger word than the flags
  rho and p_spec flags are printed per statistic beside it.

RESAMPLING UNITS (rule 4)
--------------------------
* RANDOM-k draws -> NONE inside a draw: a deterministic recomputation on a
  deleted position set; the spread over draws is the DELETION EFFECT (a
  re-derivation null), not a bootstrap CI.  Smallest one-sided fraction it
  can resolve: 1/N_DRAW.
* NO bootstrap CI of any kind is computed in this script (D18.5 holds this
  session's CIs).  N_BOOT is read for the house convention and is unused;
  said here so the output cannot imply otherwise.

LIMITS STATED IN THE OUTPUT
---------------------------
* The two views have DIFFERENT universes, so their k values differ (H's are
  computed); comparisons are within a view at equal k, and between views
  only at the same construction slot.
* SEQ-k and 3D-k overlap; the intersection count and Jaccard are printed at
  every k so the comparison is read against the size of the differing part.
* p_spec under a deletion compares DIFFERENTLY-THINNED row sets (each
  background has its own usable rows) -- disclosed, as in D15.
* |p - 222| is a RESIDUE-INDEX distance, not a structural distance; d3_222
  is a CA-CA distance in ONE 2.50 A crystal structure of the dimer.
* Unresolved positions and their rows are dropped and counted, never
  imputed (D15 convention: keep_from_removed ANDs with `resolved`).
* Rank fractions over small n are rank fractions, not tests (rule 10).

WATERMARKS: descriptive only; no GENERIC / BEATS / INDETERMINATE label
anywhere; no torch / esm / thermompnn import; nothing frozen is redefined;
the frozen PHASE2_PREREG.md verdict is not touched.

RUN (smoke first, then full; time the run, never guess) --
    N_DRAW=20  SEED=0 venv/bin/python3 scripts/151_phase2_diag4_equal_k.py
    N_DRAW=200 SEED=0 venv/bin/python3 scripts/151_phase2_diag4_equal_k.py
Full output is redirected to
    docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D21_FULL_OUTPUT.txt
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
SCRIPT144 = ROOT / "scripts/144_phase2_diag3_farvariants.py"

# tolerances = the SOURCE's own print precision (see docstring GATES):
TOL9 = 5e-10                      # half-ulp of a 9-decimal print
TOL6 = 5e-7                       # half-ulp of a 6-decimal print
TOL4 = 5e-5                       # half-ulp of a 4-decimal print

TGT_UNIV = {"full": 595, "H": 418}          # task doc line 234
TGT_K_FULL = {"seq25": 50, "seq50": 100,    # task doc lines 235-237
              "R20": 121, "R30": 247}
RS = (25, 50)                       # sequence windows (script 144 line 170)
RR = (20, 30)                       # radii gated by task doc line 244
KS = ("seq25", "seq50", "R20", "R30")
K_LABEL = {"seq25": "SEQ-window Rs = 25", "seq50": "SEQ-window Rs = 50",
           "R20": "3D R = 20 A", "R30": "3D R = 30 A"}
R_OF = {"R20": 20.0, "R30": 30.0}
RS_OF = {"seq25": 25, "seq50": 50}

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


def gate_table_and_stop(msg):
    banner("D21 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in GATES:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D21 gates so far: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")
    print(msg)
    print(f"\nElapsed {time.time() - T0:.1f}s")
    sys.exit(1)


# ==========================================================================
# PARSERS over D15's printed output -- read at run time, never copied into
# this file.  TBL / KR / KR_CTX patterns transcribed from
# scripts/150_phase2_diag4_shells.py lines 256-260 (KR extended to capture
# the printed RETAINED count), plus the matched-deletion line and D15's four
# SEQ blocks.
# ==========================================================================
TBL = re.compile(r"^\s*(full|H)\s+(\d+)\s+(\d+)\s+([-+]\d+\.\d+)\s+"
                 r"\[[^\]]+\]\s+(?:True|False)\s+([-+]\d+\.\d+)\s+"
                 r"\[[^\]]+\]\s+(\d+\.\d+)")
KR = re.compile(r"^\s+R =\s+(\d+) A: k_R =\s+(\d+) positions removed,\s+"
                r"(\d+) retained")
KR_CTX = re.compile(r"^\s*\[(full|H)\] frame positions within each R")
MD = re.compile(r"^\s+matched-deletion range for the gradient \(n=(\d+) draws\): "
                r"\[([-+]\d+\.\d+), ([-+]\d+\.\d+)\]\s+-> S1 gradient is "
                r"\w+ it;\s+frac draws at or below S1 = (\d+\.\d+), "
                r"at or above = (\d+\.\d+)")
SEQ_HDR = re.compile(r"^\s*--- S1  SEQ Rs = (\d+)\s+\(keep \|p - 222\| > "
                     r"\d+\)\s+\[(full|H)\] ---")
ANY_HDR = re.compile(r"^\s*--- .+ ---\s*$")
BANNER_RX = re.compile(r"^-{20,}")
F_POS = re.compile(r"positions retained = (\d+)")
F_RHO = re.compile(r"A222V rho on the retained rows = ([-+]\d+\.\d+)")
F_GR = re.compile(r"gradient Spearman\(rho_b, d3_b\) on resolved NULLS "
                  r"n = 67: ([-+]\d+\.\d+)")
F_P = re.compile(r"p_spec \(n78 nulls, frozen direction rho_b <= "
                 r"rho_A222V\): k = (\d+) of 78, p_spec = (\d+\.\d+)")


def parse_d15():
    """-> (table, kR, md):
      table {(view,R): dict(k_R, rho, grad, p)}   from D15's S1 table
      kR    {view: {R: (k_R, retained)}}          from D15's geometry block
      md    {(view,R): dict(n, lo, hi, fb, fa)}   matched-deletion gradient
                                                  range printed under each row"""
    table, kR, md, ctx, last = {}, {}, {}, None, None
    for line in D15_OUT.read_text().splitlines():
        m = KR_CTX.match(line)
        if m:
            ctx = m.group(1)
            kR.setdefault(ctx, {})
            continue
        m = KR.match(line)
        if m and ctx:
            r = int(m.group(1))
            if r not in kR[ctx]:        # first occurrence wins (geometry)
                kR[ctx][r] = (int(m.group(2)), int(m.group(3)))
            continue
        m = TBL.match(line)
        if m:
            last = (m.group(1), int(m.group(2)))
            table[last] = dict(k_R=int(m.group(3)), rho=float(m.group(4)),
                               grad=float(m.group(5)), p=float(m.group(6)))
            continue
        m = MD.match(line)
        if m and last:
            md[last] = dict(n=int(m.group(1)), lo=float(m.group(2)),
                            hi=float(m.group(3)), fb=float(m.group(4)),
                            fa=float(m.group(5)))
            last = None
            continue
    return table, kR, md


def parse_d15_seq():
    """-> {(Rs, view): dict(pos_ret, rho, grad, k, p)} from D15's four
    printed SEQ blocks (lines 130-148 and 210-228 of its full output)."""
    out, cur = {}, None
    for line in D15_OUT.read_text().splitlines():
        m = SEQ_HDR.match(line)
        if m:
            cur = (int(m.group(1)), m.group(2))
            out[cur] = {}
            continue
        if cur is not None and (ANY_HDR.match(line) or BANNER_RX.match(line)):
            cur = None
            continue
        if cur is None:
            continue
        mm = F_POS.search(line)
        if mm:
            out[cur]["pos_ret"] = int(mm.group(1))
            continue
        mm = F_RHO.search(line)
        if mm:
            out[cur]["rho"] = float(mm.group(1))
            continue
        mm = F_GR.search(line)
        if mm:
            out[cur]["grad"] = float(mm.group(1))
            continue
        mm = F_P.search(line)
        if mm:
            out[cur]["k"] = int(mm.group(1))
            out[cur]["p"] = float(mm.group(2))
    return out


# ==========================================================================
# Rule-11 reporting for one statistic against ITS OWN RANDOM-k draws.
# TRANSCRIBED from scripts/150_phase2_diag4_shells.py lines 296-325; the
# ONE text difference is the control's name in two labels ("RANDOM-k"
# instead of "matched-control"), which is the only change.
# Prints value, 2.5/97.5 range, mean/sd, BOTH one-sided fractions, distance
# to nearest bound, and the INSIDE / OUTSIDE / MARGINAL flag (rule 11).
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
        print(f"      *** {nn} of {len(a)} RANDOM-k draws are NaN and are "
              f"EXCLUDED from the range and fractions ({len(fin)} "
              f"finite) ***")
    if np.isnan(v) or len(fin) == 0:
        print("      -> FLAG (rule 11): NONE (NaN; flag not computable)")
        return dict(flag="NAN", lo=np.nan, hi=np.nan, frac_le=np.nan,
                    frac_ge=np.nan, dist=np.nan)
    f = p4.flag11(float(v), fin)
    mean = float(fin.mean())
    sd = float(fin.std(ddof=1)) if len(fin) > 1 else 0.0
    print(f"      RANDOM-k mean                 = {mean:+.9f}"
          f"   sd = {sd:.9f}")
    print(f"      RANDOM-k 2.5 / 97.5 pct       = [{f['lo']:+.9f}, "
          f"{f['hi']:+.9f}]")
    print(f"      fraction of draws at or below  = {f['frac_le']:.4f};  "
          f"at or above = {f['frac_ge']:.4f}")
    print(f"      distance to nearest bound      = {f['dist']:.9f}   "
          f"(MARGINAL distance threshold 0.002)")
    print(f"      -> FLAG (rule 11): {f['flag']}")
    return f


def main():
    banner("D21 -- EQUAL-k ORDERING TEST: SEQUENCE, 3D, OR RANDOM?  "
           "(script 151)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No frozen "
          "outcome word is used as a label anywhere.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn import anywhere "
          "in this file.")
    print(f"  N_DRAW={N_DRAW} N_BOOT={N_BOOT} SEED={SEED}  (N_BOOT is READ "
          "FOR CONVENTION AND UNUSED: no bootstrap CI is computed in this "
          "script -- D18.5 holds this session's CIs.)")
    print("RESAMPLING UNITS (not interchangeable):")
    print("  * RANDOM-k draws -> NONE inside a draw: a deterministic "
          "recomputation on a deleted position set; the spread is the "
          "DELETION EFFECT (re-derivation null), not a bootstrap CI.")
    print("  * NO bootstrap CI anywhere in this script.")
    print("  * p_spec, row counts, overlap -> NO resampling.")
    print("  * A222V's rho -> point statistic here; no CI run here.")
    if N_DRAW != 200:
        print(f"  *** N_DRAW = {N_DRAW}, NOT 200 (smoke run): ranges and "
              "flags below are smoke values, and gate D21-G1g (which needs "
              "D15's 200-draw stream) prints SKIP; the full run uses 200. "
              "***")

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

    T15, K15, MD15 = parse_d15()
    SQ15 = parse_d15_seq()
    print(f"  parsed {len(T15)} S1 table rows, k_R geometry for views "
          f"{sorted(K15)}, {len(MD15)} matched-deletion lines and "
          f"{len(SQ15)} SEQ blocks from {D15_OUT.name}")

    # Parser sanity guard (AGENTS 5/6): D15's table has exactly 8 rows, 8
    # matched-deletion lines and 4 SEQ blocks.  A short parse is a DEFECT IN
    # THIS FILE'S REGEXES, not a disagreement between two sources, and must
    # say so rather than crash later with a KeyError.
    if (len(T15), len(MD15), len(SQ15)) != (8, 8, 4):
        print(f"\n  [PARSER FAIL] expected 8 S1 table rows / 8 "
              f"matched-deletion lines / 4 SEQ blocks, parsed "
              f"{len(T15)} / {len(MD15)} / {len(SQ15)}.  This is a defect "
              "in this script's parsers over D15's output, NOT a data "
              "disagreement: no statistic has been compared.  Fix the "
              "pattern; do not touch any threshold.")
        sys.exit(1)

    # ======================================================== QUOTED SRC ===
    banner("QUOTED SOURCE -- what D21 is testing, and the script-144 "
           "determination", "-")
    print("  Task doc, why and the equal-k requirement (lines 231-237):")
    qline(TASK_DOC, 231, 237)
    print("  Task doc, identity gates and the SEQ conditional (lines "
          "244-247):")
    qline(TASK_DOC, 244, 247)
    print("  Task doc, the answer rule (lines 249-251):")
    qline(TASK_DOC, 249, 251)
    print("  scripts/144, the radii and windows (lines 169-170):")
    qline(SCRIPT144, 169, 170)
    print("  scripts/144, BOTH variant constructions (lines 565-572) -- "
          "line 572 answers the doc's question about unresolved rows:")
    qline(SCRIPT144, 565, 572)
    print("  scripts/144, the deletion function (lines 411-417):")
    qline(SCRIPT144, 411, 417)
    print("  DETERMINATION (read before any run of this script): line 572 "
          "keeps `resolved & ~np.isin(POSV, rm)` -- D15's sequence "
          "sensitivities DID drop unresolved-position rows, so D15's "
          "printed SEQ values are on the RESOLVED universe, the same row "
          "set as D21's SEQ-k, and under the doc's conditional they ARE "
          "identity gates (D21-G1e).")
    print("  D15's own prints that pin the counts (frame / resolved / "
          "retained):")
    qline(D15_OUT, 37, 37)
    qline(D15_OUT, 40, 40)
    qline(D15_OUT, 45, 48)
    qline(D15_OUT, 50, 50)
    qline(D15_OUT, 55, 58)
    qline(D15_OUT, 131, 132)
    qline(D15_OUT, 141, 142)
    qline(D15_OUT, 211, 212)
    qline(D15_OUT, 221, 222)

    # ======================================================== GEOMETRY =====
    banner("GEOMETRY AND k COUNTS -- recomputed here, targets printed "
           "beside (rule 2)", "-")
    ks = {}           # view -> {kkey: k}
    masks = {}        # (view, kkey, kind) -> keep mask ('seq' / '3d')
    delsets = {}      # (view, kkey, kind) -> the DELETED positions
    slotmasks = {}    # (view, kkey) -> the slot's OWN construction mask
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved, d3 = v["POSV"], v["resolved"], v["d3"]
        univ_pos = v["univ_pos"]
        sd = np.abs(univ_pos - 222)
        d3r = d3[resolved]
        n_res = int(resolved.sum())
        print(f"\n  [{view}] frame positions = {len(POSV)};  RESOLVED "
              f"universe = {n_res};  unresolved = {len(POSV) - n_res};  "
              f"min |p - 222| among resolved = {int(sd.min())};  "
              f"min d3_222 = {float(d3r.min()):.3f} A;  NaN in d3_222 = "
              f"{int(np.isnan(d3r).sum())}")
        ra_unres = int((~resolved)[v["A"].code].sum())
        per = [int((~resolved)[s.code].sum()) for s in v["B"].values()]
        print(f"  [{view}] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM "
              f"EVERY SET AND FROM THE BASELINE, NEVER IMPUTED: A222V "
              f"{ra_unres} of {len(v['A'].pos)} rows; per background min = "
              f"{min(per)}, max = {max(per)} ***")
        # ---- counts vs targets (doc and D15) ----------------------------
        kmap = {}
        for Rs in RS:
            kmap[f"seq{Rs}"] = int((sd <= Rs).sum())
        for R in RR:
            kmap[f"R{R}"] = int((resolved & (d3 <= R)).sum())
        ks[view] = kmap
        print(f"  [{view}] recomputed k: " + ", ".join(
            f"{K_LABEL[kk]} -> k = {kmap[kk]}" for kk in KS))
        for kk in KS:
            doc_t = TGT_K_FULL.get(kk) if view == "full" else None
            if kk.startswith("seq"):
                Rs = RS_OF[kk]
                d15_t = n_res - SQ15[(Rs, view)]["pos_ret"]
                src = (f"D15 printed retained {SQ15[(Rs, view)]['pos_ret']} "
                       f"-> {n_res} - {SQ15[(Rs, view)]['pos_ret']} = "
                       f"{d15_t}")
            else:
                R = int(R_OF[kk])
                d15_t = K15[view][R][0]
                src = f"D15 printed k_R = {d15_t}"
            ok_doc = True if doc_t is None else (kmap[kk] == doc_t)
            ok_d15 = (kmap[kk] == d15_t)
            if doc_t is None:
                tgt_txt = "no doc target (H: compute)"
            else:
                tgt_txt = f"doc target {doc_t}"
            if not ok_doc:
                note = ("MISMATCH: the DOC number and the recomputed number "
                        "are BOTH printed above; this item stops (rule 2)")
            elif doc_t is None:
                note = "exact integer equality vs D15"
            else:
                note = "exact integer equality vs doc and D15"
            gate(f"D21-G1b {view} {K_LABEL[kk]} count vs {tgt_txt}",
                 ok_doc and ok_d15,
                 f"recomputed = {kmap[kk]};  {tgt_txt};  {src};  -> "
                 f"{'PASS' if (ok_doc and ok_d15) else 'FAIL'} ({note})")
        # ---- the 495 reconciliation (doc line 237's puzzle) -------------
        if view == "full":
            ret50 = n_res - kmap["seq50"]
            print(f"  [full] 495 RECONCILIATION (doc line 237): D15 "
                  f"printed positions retained for Rs = 50 = "
                  f"{SQ15[(50, 'full')]['pos_ret']};  recomputed here = "
                  f"resolved({n_res}) - k_seq(50)({kmap['seq50']}) = "
                  f"{ret50};  frame-based arithmetic = {len(POSV)} - "
                  f"{kmap['seq50']} = {len(POSV) - kmap['seq50']} "
                  f"(NOT 495).  The retained count is over the RESOLVED "
                  f"universe.")
            gate("D21-G1b full 495 retained for Rs = 50 == resolved - "
                 "k_seq(50) (doc line 237)",
                 ret50 == SQ15[(50, "full")]["pos_ret"],
                 f"resolved - k = {ret50};  D15 printed retained = "
                 f"{SQ15[(50, 'full')]['pos_ret']};  frame - k = "
                 f"{len(POSV) - kmap['seq50']} -- exact integer equality "
                 f"required")
        # ---- universe gates --------------------------------------------
        d15_ret0 = K15[view][0][1]
        gate(f"D21-G1a {view} resolved universe == doc target "
             f"{TGT_UNIV[view]} and == D15's R = 0 retained",
             n_res == TGT_UNIV[view] and n_res == d15_ret0,
             f"recomputed = {n_res};  doc target (line 234) = "
             f"{TGT_UNIV[view]};  D15 printed retained at R = 0 = "
             f"{d15_ret0} (exact integer equality)")
        # ---- the two sets AT EVERY k, and mask equivalence (G1c) --------
        ord_s = np.lexsort((univ_pos, sd))            # primary |p - 222|
        ord_t = np.lexsort((univ_pos, d3r))           # primary d3_222
        for kk in KS:
            k = kmap[kk]
            s_set = np.sort(univ_pos[ord_s[:k]])
            t_set = np.sort(univ_pos[ord_t[:k]])
            delsets[(view, kk, "seq")] = s_set
            delsets[(view, kk, "3d")] = t_set
            masks[(view, kk, "seq")] = p4.keep_from_removed(POSV, resolved,
                                                            s_set)
            masks[(view, kk, "3d")] = p4.keep_from_removed(POSV, resolved,
                                                           t_set)
            if kk.startswith("seq"):
                Rs = RS_OF[kk]
                win = POSV[np.abs(POSV - 222) <= Rs]
                d15_mask = resolved & ~np.isin(POSV, win)
                own = "seq"
                desc = (f"SEQ-{k} == D15's window mask "
                        f"resolved & ~isin(|p - 222| <= {Rs})")
            else:
                # script 144 lines 566-568: rm = POSV[resolved & (d3 <= R)]
                # then keep = keep_from_removed(POSV, resolved, rm), i.e.
                # resolved & (d3 > R) -- a KEEP mask, NOT the removed set.
                R = R_OF[kk]
                rm = POSV[resolved & (d3 <= R)]
                d15_mask = p4.keep_from_removed(POSV, resolved, rm)
                own = "3d"
                desc = (f"3D-{k} == D15's keep_from_removed of "
                        f"{{d3_222 <= {R:.0f}}} (script 144 lines 566-568)")
            slotmasks[(view, kk)] = (own, d15_mask)
            mine = masks[(view, kk, own)]
            same = bool(np.array_equal(mine, d15_mask))
            gate(f"D21-G1c {view} {desc}", same,
                 f"keep arrays identical = {same} (required EXACTLY True); "
                 f"set size = {k}; mine keeps {int(mine.sum())}, D15-style "
                 f"keeps {int(d15_mask.sum())}; the OTHER method's set at "
                 f"this k has no D15 counterpart and is gated only by the "
                 f"same code path")
        for kk in KS:
            print(f"  [{view}] {K_LABEL[kk]}: SEQ-{kmap[kk]} and "
                  f"3D-{kmap[kk]} sets both built at k = {kmap[kk]} "
                  f"(ties by ascending position)")

    # ======================================================== GATE EARLY ==
    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  Count/set gates: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        gate_table_and_stop("*** D21 GATE FAIL at the count/set stage -- "
                            "D21 stops here (task doc rule 6).  No "
                            "threshold was loosened and N was not raised. "
                            "***")

    # ======================================================== POINTS =======
    banner("GATE D21-G1d/e/f -- reproduction of D15's printed rows "
           "(deterministic)", "-")
    print("  TOLERANCES: each quantity is gated at the source's own print "
          "precision -- rho and gradient are 9-decimal prints (script 144 "
          "lines 779/781) -> 5e-10 half-ulp; p_spec is a 6-decimal print "
          "(line 783) -> 5e-7; '0 difference' additionally means the keep "
          "MASKS are identical arrays (G1c above).")
    base, s3d, sseq = {}, {}, {}
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved = v["POSV"], v["resolved"]
        # ---- baseline: zero deletion + D15's printed R = 0 row (G1f) ----
        k0 = p4.keep_from_removed(POSV, resolved, [])
        k0d = resolved.copy()
        s0 = p4.stats(v, bgs, N_ids, resN, res96, df3, k0)
        s0d = p4.stats(v, bgs, N_ids, resN, res96, df3, k0d)
        base[view] = s0
        same = bool(np.array_equal(k0, k0d))
        dstat = max(abs(float(s0[q]) - float(s0d[q])) for q in
                    ("rho_a", "grad_n67", "k_n78", "k_n67"))
        gate(f"D21-G1f zero-deletion == baseline ({view})",
             same and dstat == 0.0,
             f"keep arrays identical = {same} (required True); "
             f"max|diff| over rho_A222V, gradient n=67 and both k's = "
             f"{dstat:.3e} (required EXACTLY 0)")
        t0 = T15[(view, 0)]
        parts = [("rho", s0["rho_a"], t0["rho"], TOL9),
                 ("gradient n=67", s0["grad_n67"], t0["grad"], TOL9),
                 ("p_spec n=78", s0["p_n78"], t0["p"], TOL6)]
        worst = max(parts, key=lambda p: abs(p[1] - p[2]))
        allp = ", ".join(f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                         for p in parts)
        gate(f"D21-G1f baseline reproduces D15's printed R = 0 row "
             f"({view})", all(abs(p[1] - p[2]) < p[3] for p in parts),
             f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 printed "
             f"{worst[2]!r} |diff| = {abs(worst[1] - worst[2]):.3e} "
             f"(gate < {worst[3]:g} = that quantity's print precision); "
             f"all: {allp}")
        print(f"    [{view}] baseline: A222V rho = {s0['rho_a']:+.9f}; "
              f"gradient n=67 = {s0['grad_n67']:+.9f}; p_spec n=78 = "
              f"{s0['p_n78']:.9f} (k = {s0['k_n78']})")
        # ---- BOTH methods at all four k (needed for the report) ---------
        for kk in KS:
            sseq[(view, kk)] = p4.stats(v, bgs, N_ids, resN, res96, df3,
                                        masks[(view, kk, "seq")])
            s3d[(view, kk)] = p4.stats(v, bgs, N_ids, resN, res96, df3,
                                       masks[(view, kk, "3d")])
        # ---- 3D-k at k_R(20)/k_R(30) vs D15's S1 rows (G1d, HARD) ------
        for R in RR:
            kk = f"R{R}"
            s = s3d[(view, kk)]
            t = T15[(view, R)]
            parts = [("rho", s["rho_a"], t["rho"], TOL9),
                     ("gradient n=67", s["grad_n67"], t["grad"], TOL9),
                     ("p_spec n=78", s["p_n78"], t["p"], TOL6),
                     ("k_R count", float(ks[view][kk]), float(t["k_R"]),
                      0.0)]
            ok = all(abs(p[1] - p[2]) <= p[3] for p in parts)
            worst = max(parts, key=lambda p: abs(p[1] - p[2]))
            allp = ", ".join(f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                             for p in parts)
            gate(f"D21-G1d 3D-k at k_R({R}) reproduces D15's S1 R = {R} "
                 f"row ({view}) -- task doc line 244 HARD identity", ok,
                 f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 "
                 f"printed {worst[2]!r} |diff| = "
                 f"{abs(worst[1] - worst[2]):.3e}; all: {allp}")
            print(f"    [{view}] 3D-{ks[view][kk]} (R = {R} A): A222V rho "
                  f"= {s['rho_a']:+.9f}; gradient n=67 = "
                  f"{s['grad_n67']:+.9f}; p_spec n=78 = {s['p_n78']:.9f} "
                  f"(k = {s['k_n78']})")
        # ---- SEQ-k vs D15's printed SEQ rows (G1e) ----------------------
        n_res = int(resolved.sum())
        for Rs in RS:
            kk = f"seq{Rs}"
            s = sseq[(view, kk)]
            t = SQ15[(Rs, view)]
            parts = [("rho", s["rho_a"], t["rho"], TOL9),
                     ("gradient n=67", s["grad_n67"], t["grad"], TOL9),
                     ("p_spec k", float(s["k_n78"]), float(t["k"]), 0.0),
                     ("positions retained",
                      float(n_res - ks[view][kk]), float(t["pos_ret"]),
                      0.0)]
            ok = all(abs(p[1] - p[2]) <= p[3] for p in parts)
            worst = max(parts, key=lambda p: abs(p[1] - p[2]))
            allp = ", ".join(f"{p[0]} {abs(p[1] - p[2]):.2e} (tol {p[3]:g})"
                             for p in parts)
            gate(f"D21-G1e SEQ-k at k_seq({Rs}) reproduces D15's printed "
                 f"SEQ Rs = {Rs} row ({view})", ok,
                 f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 "
                 f"printed {worst[2]!r} |diff| = "
                 f"{abs(worst[1] - worst[2]):.3e}; all: {allp}")
            print(f"    [{view}] SEQ-{ks[view][kk]} (Rs = {Rs}): A222V rho "
                  f"= {s['rho_a']:+.9f}; gradient n=67 = "
                  f"{s['grad_n67']:+.9f}; p_spec n=78 = {s['p_n78']:.9f} "
                  f"(k = {s['k_n78']})")
        # the cross-method sets at each slot have no D15 counterpart:
        for kk in KS:
            other = "3d" if kk.startswith("seq") else "seq"
            s = sseq[(view, kk)] if other == "seq" else s3d[(view, kk)]
            print(f"    [{view}] cross-method set at {K_LABEL[kk]}: "
                  f"{other.upper()}-{ks[view][kk]} (no D15 counterpart; "
                  f"reported, not gated): rho = {s['rho_a']:+.9f}, "
                  f"gradient = {s['grad_n67']:+.9f}")

    # ======================================================== CONTROLS =====
    banner("THE RANDOM-k CONTROLS -- N_DRAW draws per (view, k), fresh "
           "default_rng(SEED) per block", "-")
    print(f"  N_DRAW = {N_DRAW}, SEED = {SEED}.  A FRESH "
          "np.random.default_rng(SEED) per (view, k) block, exactly as "
          "script 144 created a fresh rng per (view, R) (lines 717-721), "
          "so the stream does not depend on loop order.")
    print("  Each draw deletes k positions chosen UNIFORMLY WITHOUT "
          "REPLACEMENT from the SAME view's resolved universe -- whole "
          "positions, all their variants -- and the SAME removed set is "
          "applied to EVERY background within a draw.")
    print("  RESAMPLING UNIT: none inside a draw (re-derivation null).  "
          "The smallest one-sided fraction these draws can resolve is "
          f"{1.0 / N_DRAW:.4f}.")

    ctrl = {}
    all_kept_ok, all_d0_ok, worst_d0 = True, True, 0.0
    for view in p3.VIEWS:
        v = vs[view]
        POSV, resolved = v["POSV"], v["resolved"]
        univ_pos = v["univ_pos"]
        for kk in KS:
            k = ks[view][kk]
            acc = {q: np.empty(N_DRAW, float)
                   for q in ("rho_a", "grad_n67", "p_n78")}
            rg = np.random.default_rng(SEED)
            kept = []
            for i in range(N_DRAW):
                drop = rg.choice(univ_pos, size=k, replace=False)
                keep = p4.keep_from_removed(POSV, resolved, drop)
                kept.append(int(keep.sum()))
                sd_ = p4.stats(v, bgs, N_ids, resN, res96, df3, keep)
                for q in acc:
                    acc[q][i] = float(sd_[q])
            # -- identity checks on this block's own draws (G1h) ---------
            exp_kept = len(univ_pos) - k
            k_ok = all(c == exp_kept for c in kept)
            all_kept_ok = all_kept_ok and k_ok
            rg0 = np.random.default_rng(SEED)
            drop0 = rg0.choice(univ_pos, size=k, replace=False)
            s_d0 = p4.stats(v, bgs, N_ids, resN, res96, df3,
                            p4.keep_from_removed(POSV, resolved, drop0))
            d0 = max(abs(float(s_d0[q]) - acc[q][0]) for q in acc)
            worst_d0 = max(worst_d0, d0)
            all_d0_ok = all_d0_ok and (d0 == 0.0)
            ctrl[(view, kk)] = dict(acc=acc, kept_min=min(kept),
                                    kept_max=max(kept), exp=exp_kept,
                                    d0=d0, k_ok=k_ok)
            print(f"\n  === [{view}] RANDOM-{k} ({K_LABEL[kk]}): k = {k} "
                  f"deleted per draw from the {len(univ_pos)}-position "
                  f"resolved universe; N_DRAW = {N_DRAW}, SEED = {SEED} "
                  f"===")
            print(f"    kept positions per draw: min = {min(kept)}, max = "
                  f"{max(kept)} (expected {exp_kept});  first-draw "
                  f"determinism |diff| = {d0:.3e}")
            for q, lbl in (("rho_a", "A222V rho"),
                           ("grad_n67", "gradient n=67"),
                           ("p_n78", "p_spec n=78")):
                a = acc[q]
                fin = a[~np.isnan(a)]
                lo, hi = np.percentile(fin, [2.5, 97.5])
                print(f"    RANDOM-k {lbl}: mean = {fin.mean():+.9f}, "
                      f"sd = {fin.std(ddof=1):.9f}, min = {fin.min():+.9f}, "
                      f"max = {fin.max():+.9f}, 2.5/97.5 pct = "
                      f"[{lo:+.9f}, {hi:+.9f}]")

    gate("D21-G1h every RANDOM draw keeps exactly len(universe) - k "
         "positions (all blocks)", all_kept_ok,
         "all draw keep-counts equal universe - k = " +
         ("True" if all_kept_ok else "FALSE") + " (required True); " +
         ";  ".join(f"{view}/{kk}: {ctrl[(view, kk)]['kept_min']}-"
                    f"{ctrl[(view, kk)]['kept_max']} of expected "
                    f"{ctrl[(view, kk)]['exp']}"
                    for view in p3.VIEWS for kk in KS))
    gate("D21-G1h first draw of every block reproduces from a fresh "
         f"default_rng(SEED)", all_d0_ok,
         f"max|diff| over all blocks = {worst_d0:.3e} (required EXACTLY 0)")

    # ---- G1g: the k_R blocks ARE D15's control stream --------------------
    if N_DRAW == 200:
        for view in p3.VIEWS:
            for R in RR:
                kk = f"R{R}"
                t = MD15[(view, R)]
                a = ctrl[(view, kk)]["acc"]["grad_n67"]
                lo, hi = np.percentile(a, [2.5, 97.5])
                fb = float((a <= s3d[(view, kk)]["grad_n67"]).mean())
                fa = float((a >= s3d[(view, kk)]["grad_n67"]).mean())
                parts = [("range lo", lo, t["lo"], TOL9),
                         ("range hi", hi, t["hi"], TOL9),
                         ("frac at or below", fb, t["fb"], TOL4),
                         ("frac at or above", fa, t["fa"], TOL4),
                         ("n draws", float(len(a)), float(t["n"]), 0.0)]
                ok = all(abs(p[1] - p[2]) <= p[3] for p in parts)
                worst = max(parts, key=lambda p: abs(p[1] - p[2]))
                allp = ", ".join(f"{p[0]} {abs(p[1] - p[2]):.2e} "
                                 f"(tol {p[3]:g})" for p in parts)
                gate(f"D21-G1g RANDOM-{ks[view][kk]} reproduces D15's "
                     f"printed matched-deletion gradient line (R = {R}, "
                     f"{view}) -- same seed, same stream", ok,
                     f"worst is {worst[0]}: recomputed {worst[1]!r} vs D15 "
                     f"printed {worst[2]!r} |diff| = "
                     f"{abs(worst[1] - worst[2]):.3e}; all: {allp}")
    else:
        print(f"\n  [SKIP] D21-G1g: needs D15's 200-draw matched-deletion "
              f"range, but N_DRAW = {N_DRAW} (smoke run).  A {N_DRAW}-draw "
              "stream cannot equal a 200-draw range; this gate RUNS IN THE "
              "FULL RUN at N_DRAW = 200.")

    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  Gates before the analysis: {len(GATES) - n_fail}/"
          f"{len(GATES)} PASS, {n_fail} FAIL")
    if n_fail:
        gate_table_and_stop("*** D21 GATE FAIL -- D21 stops here (task "
                            "doc rule 6).  No threshold was loosened and N "
                            "was not raised. ***")
    print("  GATE PASS so far: D21-G1 satisfied.  The equal-k analysis may "
          "be reported.")

    # ======================================================== REPORT =======
    banner("THE EQUAL-k REPORT -- overlap, then SEQ-k and 3D-k each vs its "
           "own RANDOM-k range", "-")
    print("  Per (view, k): overlap first, then A222V's rho (point; no CI "
          "here -- D18.5 holds the CIs), the gradient n = 67, p_spec n = 78 "
          "(numeric threshold comparison only, rule 10), and each statistic "
          "beside its RANDOM-k range with rule 11's numbers and flag.")

    flags, stats_ics, overlaps = {}, {}, {}
    for view in p3.VIEWS:
        thr = 0.05 if view == "full" else 0.10
        n_res = int(vs[view]["resolved"].sum())
        for kk in KS:
            k = ks[view][kk]
            acc = ctrl[(view, kk)]["acc"]
            seq_pos = delsets[(view, kk, "seq")]
            three_pos = delsets[(view, kk, "3d")]
            inter = int(np.intersect1d(seq_pos, three_pos).size)
            union = int(np.union1d(seq_pos, three_pos).size)
            jac = inter / union if union else float("nan")
            overlaps[(view, kk)] = (inter, jac)
            print(f"\n  === [{view}] k = {k}  ({K_LABEL[kk]}): SEQ-{k} vs "
                  f"3D-{k}, each vs RANDOM-{k} ===")
            if union:
                print(f"    OVERLAP: |SEQ-{k} intersect 3D-{k}| = {inter} "
                      f"positions;  union = {union};  Jaccard = {jac:.4f}  "
                      f"(the two sets differ in {union - inter} positions)")
            for kind, lbl in (
                    ("seq", f"SEQ-{k} (smallest |p - 222|, ties ascending "
                            f"position)"),
                    ("3d", f"3D-{k} (smallest d3_222, ties ascending "
                           f"position)")):
                s = sseq[(view, kk)] if kind == "seq" else \
                    s3d[(view, kk)]
                stats_ics[(view, kk, kind)] = s
                print(f"    --- {lbl}: {k} positions removed, "
                      f"{s['n_pos']} of {n_res} resolved kept ---")
                print(f"      rows retained: A222V = {s['n_rows_a']};  "
                      f"across the {len(bgs)} backgrounds min = "
                      f"{s['rows'].min()}, median = "
                      f"{int(np.median(s['rows']))}, max = "
                      f"{s['rows'].max()}")
                print(f"      A222V rho (point; no cluster CI run here, "
                      f"D18.5 holds the CIs) = {s['rho_a']:+.9f}")
                print(f"      gradient Spearman(rho_b, d3_b) on resolved "
                      f"nulls n = {len(resN)} = {s['grad_n67']:+.9f}")
                where = ("at or below" if s["p_n78"] <= thr else "above")
                aob = ", ".join(s["aob_n78"]) if s["aob_n78"] else "NONE"
                print(f"      p_spec (n = {len(N_ids)} nulls, frozen "
                      f"direction rho_b <= rho_A222V): k = {s['k_n78']}, "
                      f"p_spec = {s['p_n78']:.9f}   at or below: {aob}   "
                      f"-> {where} the frozen numeric threshold {thr} "
                      f"({view})")
                fl = {}
                for q, olbl in (("rho_a", "A222V rho"),
                                ("grad_n67", "gradient n=67"),
                                ("p_n78", "p_spec n=78")):
                    fl[q] = rule11(s[q], acc[q], olbl)
                flags[(view, kk, kind)] = fl

    # ======================================================== THE ANSWER ===
    banner("THE ANSWER AT EQUAL k -- is 3D-k more destructive than SEQ-k, "
           "and is either outside the RANDOM-k range?", "-")
    print("  Pre-registered definitions (docstring): gradient drop = "
          "baseline gradient - set gradient (positive = fell); rho "
          "attenuation = set rho - baseline rho (rho_0 < 0; positive = "
          "magnitude lost).  '3D-k MORE DESTRUCTIVE' requires BOTH larger "
          "for 3D-k; disagreement prints DISAGREE with both pairs.  "
          "Gradient verdict: 3D OUTSIDE + SEQ INSIDE -> SUPPORTED at this "
          "k; both INSIDE -> UNSUPPORTED at this k (claim WITHDRAWN at "
          "this k); anything else is printed with its exact flags.")
    print("  D15's original comparison was UNEQUAL-k (SEQ Rs = 50, k = 100 "
          "vs 3D R = 30, k = 247 -- task doc line 231): the equal-k "
          "versions are the seq50 slot and the R30 slot below.")
    verdicts = {}
    for view in p3.VIEWS:
        g0 = base[view]["grad_n67"]
        r0 = base[view]["rho_a"]
        kk_txt = ", ".join(f"{kk} = {ks[view][kk]}" for kk in KS)
        print(f"\n  --- {view} view (baseline gradient {g0:+.9f}, "
              f"baseline rho {r0:+.9f}; k values: {kk_txt}) ---")
        for kk in KS:
            k = ks[view][kk]
            sq = stats_ics[(view, kk, "seq")]
            tr = stats_ics[(view, kk, "3d")]
            fl_s = flags[(view, kk, "seq")]
            fl_t = flags[(view, kk, "3d")]
            d_s, d_t = g0 - sq["grad_n67"], g0 - tr["grad_n67"]
            a_s, a_t = sq["rho_a"] - r0, tr["rho_a"] - r0
            if d_t > d_s and a_t > a_s:
                dest = "3D-k IS MORE DESTRUCTIVE THAN SEQ-k (both metrics)"
            elif d_t < d_s and a_t < a_s:
                dest = "3D-k IS LESS DESTRUCTIVE THAN SEQ-k (both metrics)"
            else:
                gd = "3D" if d_t > d_s else "SEQ"
                ad = "3D" if a_t > a_s else "SEQ"
                dest = (f"DISAGREE: gradient drop SEQ {d_s:+.6f} vs 3D "
                        f"{d_t:+.6f} -> {gd}; rho attenuation SEQ "
                        f"{a_s:+.6f} vs 3D {a_t:+.6f} -> {ad}")
            gs, gt = fl_s["grad_n67"]["flag"], fl_t["grad_n67"]["flag"]
            if gs == "INSIDE" and gt == "INSIDE":
                verd = ("UNSUPPORTED at this k: BOTH SEQ-k and 3D-k are "
                        "INSIDE the RANDOM-k range on the gradient -> the "
                        "'3D not sequence' claim is WITHDRAWN at this k")
                cat = "WITHDRAWN"
            elif gt == "OUTSIDE" and gs == "INSIDE":
                verd = ("SUPPORTED at this k: 3D-k is OUTSIDE the "
                        "RANDOM-k range while SEQ-k is INSIDE (gradient)")
                cat = "SUPPORTED"
            else:
                verd = (f"NOT decidable by the pre-registered rule at this "
                        f"k: gradient flags are SEQ = {gs}, 3D = {gt} -- "
                        f"reported with those exact flags, no stronger "
                        f"word")
                cat = "OTHER"
            verdicts[(view, kk)] = cat
            inter, jac = overlaps[(view, kk)]
            print(f"    [{K_LABEL[kk]}, k = {k}]  overlap = {inter}, "
                  f"Jaccard = {jac:.4f}")
            print(f"      gradient drop   : SEQ-k {d_s:+.9f},  3D-k "
                  f"{d_t:+.9f}")
            print(f"      rho attenuation : SEQ-k {a_s:+.9f},  3D-k "
                  f"{a_t:+.9f}")
            print(f"      MORE DESTRUCTIVE: {dest}")
            fg_s, fg_t = fl_s["rho_a"]["flag"], fl_t["rho_a"]["flag"]
            fp_s, fp_t = fl_s["p_n78"]["flag"], fl_t["p_n78"]["flag"]
            print(f"      flags vs RANDOM-{k}: gradient SEQ = {gs}, 3D = "
                  f"{gt};  rho SEQ = {fg_s}, 3D = {fg_t};  p_spec SEQ = "
                  f"{fp_s}, 3D = {fp_t}")
            print(f"      GRADIENT VERDICT: {verd}")
    print("\n  OVERALL AT EQUAL k (per construction slot; the two views' k "
          "values differ because their universes differ):")
    for view in p3.VIEWS:
        by = {c: [kk for kk in KS if verdicts[(view, kk)] == c]
              for c in ("SUPPORTED", "WITHDRAWN", "OTHER")}
        sup = ", ".join(by["SUPPORTED"]) if by["SUPPORTED"] else "NONE"
        wdr = ", ".join(by["WITHDRAWN"]) if by["WITHDRAWN"] else "NONE"
        oth = ", ".join(by["OTHER"]) if by["OTHER"] else "NONE"
        print(f"    {view}: SUPPORTED at slots {sup};  WITHDRAWN (both "
              f"inside) at slots {wdr};  other flags at slots {oth}")
    same = all(verdicts[("full", kk)] == verdicts[("H", kk)] for kk in KS)
    print(f"    both views give the SAME verdict at every slot: "
          f"{'YES' if same else 'NO'}")

    # ======================================================== LIMITS ======
    banner("LIMITS STATED WITH THE RESULT (AGENTS 6; task doc lines "
           "249-251)", "-")
    fullk = ", ".join(str(ks["full"][kk]) for kk in KS)
    hk = ", ".join(str(ks["H"][kk]) for kk in KS)
    print("  * COMPARISONS ARE WITHIN A VIEW AT EQUAL k only: SEQ-k and "
          "3D-k are deleted at the SAME k, each judged against ITS OWN "
          "RANDOM-k range.  The two views have different universes, so "
          f"their k values differ (full: {fullk}; H: {hk}).")
    print("  * SEQ-k and 3D-k OVERLAP (printed at every k above); any "
          "difference between their effects comes only from the positions "
          "in the union-minus-intersection part.")
    print("  * |p - 222| is a RESIDUE-INDEX distance, not a structural "
          "distance; d3_222 is a CA-CA distance in ONE 2.50 A crystal "
          "structure of the dimer; a CA-CA distance is not a contact.")
    print("  * p_spec under a deletion compares DIFFERENTLY-THINNED row "
          "sets (each background has its own usable rows), exactly as in "
          "D15: disclosed, not corrected.")
    print("  * Unresolved positions and their rows are dropped and counted "
          "(printed in the geometry section), never imputed.")
    print("  * No bootstrap CI is computed in this script: the matched "
          "range answers 'is this what the same NUMBER of random positions "
          "does?', not 'is it nonzero'.  D18.5 holds this session's "
          "corrected CIs.")
    print("  * Rank fractions over small n are rank fractions, not tests "
          "(rule 10).  p_spec is compared only to the frozen numeric "
          "thresholds 0.05 (full) / 0.10 (H).")
    print("  * The RANDOM-k spread is a RE-DERIVATION null over "
          f"{N_DRAW} draws; the smallest one-sided fraction it can resolve "
          f"is {1.0 / N_DRAW:.4f}.")

    # ======================================================== GATE TABLE ==
    banner("D21 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in GATES:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D21 gates: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("*** D21 GATE FAIL -- see above (task doc rule 6). ***")
    if N_DRAW != 200:
        print("  NOTE: this is the SMOKE run (N_DRAW != 200); the D21-G1g "
              "reproduction gates did not run here and run in the full "
              "run.")
    print(f"\nElapsed {time.time() - T0:.1f}s")


if __name__ == "__main__":
    main()
