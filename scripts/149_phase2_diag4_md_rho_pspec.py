"""
Script 149 (task D19 of docs/tasks/phase2-diagnostics-iv-shells/
PHASE2_DIAGNOSTICS_IV.md) -- matched-deletion ranges for A222V's rho, for
the number of nulls at or below A222V (k), and for p_spec.

PRE-REGISTERED: this docstring was written BEFORE the first run of this
script.  Nothing below was chosen after seeing a result.

WHY
---
Diagnostics III's task doc required matched-deletion ranges for rho and
p_spec; the Diagnostics III LOG reported ranges only for the GRADIENT (see
PHASE2_DIAGNOSTICS_III_LOG.md line 772 and the summary table at line 1232).
Script 144 DID compute and print rho and p_spec ranges in its full output
(PHASE2_DIAG3_D15_FULL_OUTPUT.txt), so those printed numbers become this
script's REPRODUCTION GATE: this run recomputes them from scratch and gates
against them.  The Diagnostics III log itself reported no such ranges, so
the new reporting here is the log-level record.

RESAMPLING UNIT / NULL MODEL (task doc rule 4)
----------------------------------------------
NONE inside a draw.  The matched-deletion control is a DETERMINISTIC
recomputation on a deleted row set, repeated over N_DRAW random deletions
(script 144 lines 113-115, quoted in its docstring: "The matched-deletion
control: NEITHER.  It is a deterministic recomputation on a deleted row set,
repeated over N_DRAW random deletions").  The spread over draws is the
DELETION EFFECT, not a bootstrap CI.  It is a RE-DERIVATION null: the whole
statistic is re-derived on each randomly-deleted data set.
This is stated in the printed output too.

DRAW GENERATION (transcribed from script 144's control loop, lines 705-724;
the loop is quoted in this script's output)
---------------------------------------------
For each view in p3.VIEWS, for each R in (10, 20, 30):
    rm  = sorted(POSV[resolved & (d3 <= R)].tolist())      # the S1 deletions
    k_R = len(rm)
    rg  = np.random.default_rng(SEED)          # FRESH stream per (view, R)
    for i in range(N_DRAW):
        drop = rg.choice(univ, size=k_R, replace=False)   # univ = resolved
        keep = keep_from_removed(POSV, resolved, drop)
        s    = stats(...)                               # full recompute
Each draw removes k_R whole POSITIONS chosen uniformly without replacement
from the SAME resolved universe, and the SAME removed set is applied to
EVERY background within a draw.  A fresh rng per (view, R) is script 144's
own construction (line 717 sits inside both loops), which is what makes the
draws -- and therefore the ranges -- exactly reproducible.

GATES (pre-registered)
----------------------
D19-G1 (HARD): for all six (view, R) cells and for BOTH statistics (A222V's
  rho and p_spec n=78), the recomputed random-deletion mean, sd, 2.5th and
  97.5th percentiles match the values script 144 printed in D15's full
  output to 1e-9 (9-dp print) and the two fractions match to 5e-5 (4-dp
  print).  The gradient's 2.5/97.5 range is gated too (1e-9), as a check
  that this loop draws the SAME deletions D15 drew.  If D19-G1 fails, D19
  stops (rule 6): no threshold is loosened and N is not raised.
D19-G2 (doc-target check): the R = 0 resolved baselines recompute to the
  task doc's targets (full -0.076685523, H -0.080432398) to 1e-9.  A
  mismatch means the DOC is wrong: both numbers are printed and the item
  stops.
D19-G3 (doc-target check): the task doc's quoted D15 claim, "A222V's rho
  falls 64% (full) and 70% (H) at R = 30", is recomputed here as
  fall = 1 - rho(R30)/rho(R0) and compared with the doc's 64% / 70% at
  rounding precision (tolerance 0.5 percentage points, i.e. rounding).
  The script ALSO searches Diagnostics III's log for that sentence and
  prints what D15 actually wrote, with line numbers -- because mandate 2
  says the doc's expected values are recomputations, not facts, and the
  attribution "the claim D15 made" is itself a claim to check.

WHAT IS REPORTED (per view x R x statistic: rho, k, p_spec)
-----------------------------------------------------------
S1 value; random-deletion mean; sd (ddof=1); 2.5th and 97.5th percentiles;
fraction of draws at or below the S1 value; fraction at or above; distance
to the nearest bound; and the rule-11 flag INSIDE / OUTSIDE / MARGINAL
MARGINAL = outside but within 0.002 of a bound, or empirical one-sided
fraction between 0.01 and 0.05 -- flags11 from scripts/lib/phase2_diag4.py.
Also: the random-deletion MEAN of A222V's rho beside the R = 0 resolved
baseline for each view (does thinning alone move it?), and the names of the
nulls at or below A222V in each real S1 case (aob_n78).
Also: the R = 30 "fall" statistic fall = 1 - rho(R30)/rho(R0), its own
matched-deletion distribution (fall_i = 1 - rho_i/rho(R0), a monotone
increasing transform of rho_i because rho(R0) < 0, so its INSIDE/OUTSIDE
decision must equal the rho decision -- printed as a cross-check) with the
rule-11 flag on the fall scale AND on the rho scale, and both distances to
the nearest bound (the 0.002 MARGINAL distance is scale-dependent; both are
printed).

LIMITS STATED IN THE OUTPUT
---------------------------
* k and p_spec are the SAME statistic at different scales: p_spec =
  (1 + k)/79 is strictly increasing in k, so their flags must agree; they
  are reported as two views of one quantity, not as two pieces of evidence.
* p_spec's draws are DISCRETE (multiples of 1/79), so its empirical
  fractions contain ties and frac_le + frac_ge > 1.  Rank fractions over
  small n are rank fractions, not tests (rule 10).
* The matched-deletion range is a 95% range over 200 deletions; the
  smallest empirical one-sided fraction it can resolve is 1/200 = 0.005.
* p_spec is compared ONLY to the frozen numeric thresholds (0.05 full,
  0.10 H), never to the frozen outcome words (rule 10).

WATERMARKING RULES: no GENERIC / BEATS / INDETERMINATE label anywhere; no
torch / esm / thermompnn import; nothing frozen is redefined.

RUN
---
Smoke first, then full (rule 5).  N_DRAW and SEED come from the
environment, as everywhere in this project:
    N_DRAW=20  SEED=0 venv/bin/python3 scripts/149_phase2_diag4_md_rho_pspec.py
    N_DRAW=200 SEED=0 venv/bin/python3 scripts/149_phase2_diag4_md_rho_pspec.py
Full output is redirected to
    docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D19_FULL_OUTPUT.txt
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
SEED = int(os.environ.get("SEED", "0"))
DRAW_FULL = (N_DRAW == 200)

D15_OUT = ROOT / "docs/tasks/phase2-diagnostics-iii-mechanism" / \
    "PHASE2_DIAG3_D15_FULL_OUTPUT.txt"
D3_LOG = ROOT / "docs/tasks/phase2-diagnostics-iii-mechanism" / \
    "PHASE2_DIAGNOSTICS_III_LOG.md"

TOL9 = 1e-9          # values D15 printed with 9 decimals
TOL4 = 5e-5          # fractions D15 printed with 4 decimals (0.0005 half-ulp
                     # is the print rounding; 5e-5 is generous and far
                     # tighter than the 0.005 spacing of a 200-draw fraction)
TOL_BASE = 1e-9      # doc-target check on the R = 0 baselines
TOL_PCT = 0.5        # percentage points; the doc's 64% / 70% are roundings

RADII = (10, 20, 30)

GATES = []
T0 = time.time()


def banner(t, ch="="):
    p3.banner(t, ch)


def gate(gid, ok, detail):
    GATES.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}", flush=True)
    return ok


def skip(gid, why):
    print(f"  [SKIP] {gid}: {why}", flush=True)


def qline(path, a, b):
    lines = path.read_text().splitlines()
    for i in range(a, b + 1):
        print(f"  {path.relative_to(ROOT)}:{i}: {lines[i - 1]}")


def find_lines(path, needle):
    return [i for i, l in enumerate(path.read_text().splitlines(), start=1)
            if needle in l]


# ==========================================================================
# Parse script 144's PRINTED matched-deletion blocks out of D15's full
# output.  These are the reproduction targets for D19-G1 -- read at run time,
# never copied into this file.
# ==========================================================================
STAT_LABELS = ("A222V rho", "p_spec, 78 nulls", "k at or below, 78 nulls",
               "gradient Spearman(rho_b,d3_b), resolved nulls n=67")


def parse_d15_md():
    """-> {(view, R): {statlabel: dict(s1, mean, sd, lo, hi, fle, fge)}}"""
    hdr = re.compile(r"\s*=== (\w+), R = (\d+) A: k_R = (\d+) positions")
    out, ctx, cur = {}, None, None

    def flush():
        nonlocal cur
        if cur and "mean" in cur and "lo" in cur:
            out.setdefault((cur["view"], cur["R"]), {})[cur["stat"]] = cur
        cur = None

    for line in D15_OUT.read_text().splitlines():
        m = hdr.match(line)
        if m:
            flush()
            ctx = (m.group(1), int(m.group(2)))
            continue
        if ctx is None:
            continue
        s = line.strip()
        if s in STAT_LABELS:
            flush()
            cur = dict(view=ctx[0], R=ctx[1], stat=s)
            continue
        if cur is None:
            continue
        m = re.match(r"\s*S1 value\s+= (\S+)", line)
        if m:
            cur["s1"] = float(m.group(1))
            continue
        m = re.match(r"\s*random-deletion mean\s+= (\S+)\s+sd = (\S+)",
                     line)
        if m:
            cur["mean"] = float(m.group(1))
            cur["sd"] = float(m.group(2))
            continue
        m = re.match(r"\s*random-deletion 2\.5 / 97\.5 pct = \[([^,]+), "
                     r"([^\]]+)\]", line)
        if m:
            cur["lo"] = float(m.group(1))
            cur["hi"] = float(m.group(2))
            continue
        m = re.match(r"\s*fraction of draws at or below S1 = (\S+);\s+"
                     r"at or above = (\S+)", line)
        if m:
            cur["fle"] = float(m.group(1))
            cur["fge"] = float(m.group(2))
            flush()
            continue
    flush()
    return out


def main():
    banner("D19 -- MATCHED-DELETION RANGES FOR A222V's RHO, k AND "
           "p_spec  (script 149)")
    print("SCOPE: descriptive; nothing frozen is redefined; the frozen "
          "PHASE2_PREREG.md verdict is not touched.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn import anywhere "
          "in this file.")
    print(f"  N_DRAW={N_DRAW} SEED={SEED}   (DRAW_FULL={DRAW_FULL})")
    print("  RESAMPLING UNIT: NONE inside a draw.  Each draw is a "
          "deterministic recomputation on a deleted row set; the spread "
          "over draws is the DELETION EFFECT, not a bootstrap CI.  "
          "RE-DERIVATION null: the whole statistic is re-derived per draw.")
    print("  Statistics: A222V's rho; k = number of the 78 nulls at or "
          "below A222V; p_spec = (1+k)/79.  k and p_spec are ONE "
          "statistic at two scales (p_spec strictly increasing in k), so "
          "their flags must agree.")

    # ------------------------------------------------------------- build --
    print("\n  --- building the shared state (script 125 construction via "
          "phase2_diag3.build) ---")
    tb = time.time()
    st = p3.build(verbose=False)
    print(f"  build() elapsed {time.time() - tb:.1f}s")
    bgs, N_ids, resN = st["bgs"], st["N_ids"], st["resN"]
    df3 = st["df3"]
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]
    vs = p4.build_view_state(st)
    print(f"  bgs = {len(bgs)}, N_ids = {len(N_ids)}, resN = {len(resN)}, "
          f"res96 = {len(res96)}")

    # ------------------------------------------------ D19-G2: R=0 baseline --
    banner("D19-G2 (doc-target check) -- the R = 0 resolved baselines", "-")
    print("  Target (task doc): full -0.076685523, H -0.080432398.")
    base = {}
    for view in p3.VIEWS:
        POSV, resolved = vs[view]["POSV"], vs[view]["resolved"]
        keep0 = p4.keep_from_removed(POSV, resolved, [])
        base[view] = vs[view]["A"].rho(keep0)
        want = -0.076685523 if view == "full" else -0.080432398
        d = abs(base[view] - want)
        gate(f"D19-G2 R=0 resolved baseline ({view})", d < TOL_BASE,
             f"recomputed {base[view]!r} vs doc target {want!r} "
             f"|diff| = {d:.3e} (gate < {TOL_BASE:g})")

    # ------------------------------------------------------- S1 statistics --
    banner("S1 statistics (the real deletions), both views", "-")
    s1 = {}
    for view in p3.VIEWS:
        POSV, resolved, d3 = vs[view]["POSV"], vs[view]["resolved"], \
            vs[view]["d3"]
        for R in RADII:
            rm = POSV[resolved & (d3 <= R)]
            keep = p4.keep_from_removed(POSV, resolved, rm)
            s = p4.stats(vs[view], bgs, N_ids, resN, res96, df3, keep)
            s["k_R"] = int(len(rm))
            s1[(view, R)] = s
            print(f"  {view:>4s} R = {R}: k_R = {s['k_R']} positions removed "
                  f"from a universe of {int(resolved.sum())};  A222V rho = "
                  f"{s['rho_a']:+.9f};  k (n=78) = {s['k_n78']};  "
                  f"p_spec = {s['p_n78']:.9f};  gradient n=67 = "
                  f"{s['grad_n67']:+.9f}")
            print(f"        nulls at or below A222V in this S1 case "
                  f"(n=78): {s['aob_n78'] if s['aob_n78'] else 'NONE'}")

    # --------------------------------------------- the control loop itself --
    banner("THE MATCHED-DELETION CONTROL (S1 only) -- NOT OPTIONAL", "-")
    print("  QUOTED SOURCE of the loop being transcribed -- "
          "scripts/144_phase2_diag3_farvariants.py lines 705-724:")
    qline(ROOT / "scripts/144_phase2_diag3_farvariants.py", 705, 724)
    print(f"\n  N_DRAW = {N_DRAW} random deletions, SEED = {SEED}.  Each "
          "draw removes k_R positions chosen UNIFORMLY WITHOUT REPLACEMENT "
          "from the same RESOLVED universe -- WHOLE POSITIONS, all their "
          "variants -- and the SAME removed set is applied to EVERY "
          "background within a draw.")
    print("  A FRESH np.random.default_rng(SEED) IS CREATED PER (view, R) "
          "-- script 144 line 717 sits inside both loops, so this is its "
          "own construction, not a simplification.")
    print("  REPORTING RULE (task doc rule 11): the S1 value, the range, "
          "the fraction of draws at or below and at or above it, the "
          "distance to the nearest bound, and INSIDE / OUTSIDE / MARGINAL.")

    if not DRAW_FULL:
        skip("D19-G1", f"N_DRAW={N_DRAW}, not 200; the reproduction gate "
                       "against D15's printed values only applies at "
                       "N_DRAW=200 (smoke run)")

    T15 = parse_d15_md()
    print(f"  parsed {len(T15)} (view, R) cells with printed matched-"
          f"deletion blocks from {D15_OUT.name}")

    acc_all = {}
    for view in p3.VIEWS:
        POSV, resolved = vs[view]["POSV"], vs[view]["resolved"]
        univ = vs[view]["univ_pos"]
        for R in RADII:
            k_R = s1[(view, R)]["k_R"]
            keys = ("rho_a", "grad_n67", "k_n78", "p_n78")
            acc = {kk: np.empty(N_DRAW, float) for kk in keys}
            rg = np.random.default_rng(SEED)
            for i in range(N_DRAW):
                drop = rg.choice(univ, size=k_R, replace=False) if k_R else \
                    np.array([], dtype=univ.dtype)
                keep = p4.keep_from_removed(POSV, resolved, drop)
                s = p4.stats(vs[view], bgs, N_ids, resN, res96, df3, keep)
                for kk in keys:
                    acc[kk][i] = float(s[kk])
            acc_all[(view, R)] = acc

            print(f"\n  === {view}, R = {R}: k_R = {k_R} positions removed "
                  f"from a universe of {len(univ)} (matched-deletion "
                  f"draws: {N_DRAW}) ===")
            for kk, lbl in (("rho_a", "A222V rho"),
                            ("k_n78", "k at or below, 78 nulls"),
                            ("p_n78", "p_spec, 78 nulls")):
                a = acc[kk]
                v = float(s1[(view, R)][kk])
                f = p4.flag11(v, a)
                mean = float(a.mean())
                sd = float(a.std(ddof=1)) if N_DRAW > 1 else 0.0
                print(f"    {lbl}")
                print(f"      S1 value                      = {v:+.9f}")
                print(f"      random-deletion mean          = {mean:+.9f}"
                      f"   sd = {sd:.9f}")
                print(f"      random-deletion 2.5 / 97.5 pct = [{f['lo']:+.9f}, "
                      f"{f['hi']:+.9f}]")
                print(f"      fraction of draws at or below S1 = "
                      f"{f['frac_le']:.4f};  at or above = "
                      f"{f['frac_ge']:.4f}")
                print(f"      distance to nearest bound     = "
                      f"{f['dist']:.9f}   (MARGINAL distance threshold "
                      f"0.002)")
                print(f"      -> FLAG (rule 11): {f['flag']}")

            # ---------------- D19-G1: reproduction against D15's printing --
            if DRAW_FULL:
                cell = T15.get((view, R), {})
                for kk, lbl in (("rho_a", "A222V rho"),
                                ("k_n78", "k at or below, 78 nulls"),
                                ("p_n78", "p_spec, 78 nulls"),
                                ("grad_n67", "gradient Spearman(rho_b,d3_b), "
                                             "resolved nulls n=67")):
                    t = cell.get(lbl)
                    if not t:
                        gate(f"D19-G1 {view} R={R} {lbl} present in D15 "
                             f"output", False,
                             "no printed block parsed -- D15 did not print "
                             "this statistic; STOP and report")
                        continue
                    a = acc[kk]
                    mean = float(a.mean())
                    sd = float(a.std(ddof=1)) if N_DRAW > 1 else 0.0
                    lo, hi = np.percentile(a, [2.5, 97.5])
                    fle = float((a <= s1[(view, R)][kk]).mean())
                    fge = float((a >= s1[(view, R)][kk]).mean())
                    parts = [
                        ("mean", mean, t["mean"], TOL9),
                        ("sd", sd, t["sd"], TOL9),
                        ("lo", lo, t["lo"], TOL9),
                        ("hi", hi, t["hi"], TOL9),
                        ("frac_le", fle, t["fle"], TOL4),
                        ("frac_ge", fge, t["fge"], TOL4),
                    ]
                    worst = max(parts, key=lambda p: abs(p[1] - p[2]))
                    dmax = abs(worst[1] - worst[2])
                    tol = max(p[3] for p in parts)
                    gate(f"D19-G1 matched-deletion {lbl} ({view}, R={R}) "
                         f"reproduces D15's printed value",
                         all(abs(p[1] - p[2]) < p[3] for p in parts),
                         f"worst is {worst[0]}: got {worst[1]!r} vs D15 "
                         f"{worst[2]!r} |diff| = {dmax:.3e} "
                         f"(gate < {tol:g}); all six: " + ", ".join(
                             f"{p[0]} {abs(p[1] - p[2]):.2e}" for p in parts))

    # ------------------------------- random-deletion mean vs R=0 baseline --
    banner("Does THINNING ALONE move A222V's rho?  "
           "random-deletion mean vs the R = 0 baseline", "-")
    print("  The R = 0 resolved baseline is the statistic on the SAME rows "
          "before any deletion; the random-deletion mean is what deleting "
          "k_R RANDOM positions does to it.")
    print(f"  {'view':>5s} {'R':>4s} {'k_R':>5s} {'R=0 baseline':>15s} "
          f"{'random mean':>15s} {'shift':>13s} {'S1 (real)':>13s} "
          f"{'S1 - random mean':>18s}")
    for view in p3.VIEWS:
        for R in RADII:
            acc = acc_all[(view, R)]
            rm = float(acc["rho_a"].mean())
            sv = float(s1[(view, R)]["rho_a"])
            print(f"  {view:>5s} {R:>4d} {s1[(view, R)]['k_R']:>5d} "
                  f"{base[view]:>+15.9f} {rm:>+15.9f} "
                  f"{rm - base[view]:>+13.9f} {sv:>+13.9f} "
                  f"{sv - rm:>+18.9f}")

    # ------------------------------------------------ the R = 30 "fall" ----
    banner("THE R = 30 'FALL' -- is it inside or outside what deleting 247 "
           "(172) RANDOM positions produces?", "-")
    print("  The task doc asks me to report D15's claim 'in its own terms' "
          "as: \"A222V's rho falls 64% (full) and 70% (H) at R = 30\".")
    hits = find_lines(D3_LOG, "halved")
    print("\n  FIRST, THE ATTRIBUTION CHECK: that sentence does not occur "
          "in Diagnostics III's log.  A grep for 'falls 64' / '64% (full)' "
          "over docs/ and scripts/ returns only the task doc itself "
          "(PHASE2_DIAGNOSTICS_IV.md line 192).  What D15 actually wrote, "
          "verbatim:")
    for i in hits:
        qline(D3_LOG, i, i)
    print("  So D15's own wording is 'halved' / 'roughly halved', and the "
          "64% / 70% figures are a RECOMPUTATION (the task doc's, and mine "
          "below), not D15's printed words.  D15's 'roughly halved' "
          "UNDERSTATES its own printed numbers: the fall computed from "
          "them is larger than 50%.")
    print("  fall = 1 - rho(R = 30) / rho(R = 0), on the R = 0 resolved "
          "rows of the same view.  Percentages of the ASSOCIATION'S "
          "MAGNITUDE lost.")

    fall_t = {"full": 64.0, "H": 70.0}
    fall = {}
    for view in p3.VIEWS:
        s30 = s1[(view, 30)]["rho_a"]
        f = 1.0 - s30 / base[view]
        fall[view] = f
        pct = 100.0 * f
        d = abs(pct - fall_t[view])
        gate(f"D19-G3 fall at R=30 ({view}) vs the doc's "
             f"{fall_t[view]:.0f}%", d < TOL_PCT,
             f"recomputed {pct:.4f}%  = 1 - ({s30:+.9f})/({base[view]:+.9f}) "
             f"vs doc target {fall_t[view]:.0f}%  |diff| = {d:.4f} "
             f"percentage points (gate < {TOL_PCT:g} = rounding); the doc "
             f"rounds {pct:.2f}% to {round(pct):.0f}%")

        acc = acc_all[(view, 30)]
        rho_draws = acc["rho_a"]
        fall_draws = 1.0 - rho_draws / base[view]      # monotone in rho_draws
        fr = p4.flag11(f, fall_draws)                  # fall scale
        frho = p4.flag11(float(s30), rho_draws)        # rho scale
        agree = (fr["flag"] == frho["flag"])
        print(f"\n  --- {view}, R = 30 (k_R = {s1[(view, 30)]['k_R']}) ---")
        print(f"    S1 fall                          = {f:+.9f} "
              f"({100 * f:.4f}% of the association's magnitude lost)")
        print(f"    random-deletion fall mean        = "
              f"{fall_draws.mean():+.9f}   sd = "
              f"{fall_draws.std(ddof=1):.9f}")
        print(f"    random-deletion fall 2.5/97.5    = [{fr['lo']:+.9f}, "
              f"{fr['hi']:+.9f}]")
        print(f"    fraction at or below S1 fall     = {fr['frac_le']:.4f};"
              f"  at or above = {fr['frac_ge']:.4f}")
        print(f"    distance to nearest bound        = {fr['dist']:.9f}"
              f"   (on the FALL scale; 0.002 threshold)")
        print(f"    FLAG on the fall scale (rule 11) : {fr['flag']}")
        print(f"    FLAG on the rho scale  (rule 11) : {frho['flag']}  "
              f"[S1 rho {float(s30):+.9f} vs range "
              f"[{frho['lo']:+.9f}, {frho['hi']:+.9f}]; frac at/below "
              f"{frho['frac_le']:.4f}, at/above {frho['frac_ge']:.4f}; "
              f"distance to nearest bound {frho['dist']:.9f}]")
        print(f"    the two scales must agree (fall is a monotone "
              f"increasing transform of rho because rho(R0) < 0): "
              f"{'AGREE' if agree else 'DISAGREE <-- INVESTIGATE'}")

        # a cross-check on the transform itself, draw by draw
        md = float(np.max(np.abs(fall_draws -
                                 (1.0 - rho_draws / base[view]))))
        print(f"    transform identity check: max|fall_i - "
              f"(1 - rho_i/rho(R0))| = {md:.3e}")

    # ------------------------------------------------------------- summary --
    banner("D19 SUMMARY TABLE -- S1 value, matched-deletion range, "
           "rule-11 flag", "-")
    hdr = (f"  {'view':>5s} {'R':>4s} {'k_R':>5s} {'stat':>9s} "
           f"{'S1 value':>14s} {'range lo':>14s} {'range hi':>14s} "
           f"{'f<=':>7s} {'f>=':>7s} {'dist':>11s} {'flag':>9s}")
    print(hdr)
    for view in p3.VIEWS:
        for R in RADII:
            for kk, lbl in (("rho_a", "rho"), ("k_n78", "k"),
                            ("p_n78", "p_spec")):
                a = acc_all[(view, R)][kk]
                v = float(s1[(view, R)][kk])
                f = p4.flag11(v, a)
                print(f"  {view:>5s} {R:>4d} {s1[(view, R)]['k_R']:>5d} "
                      f"{lbl:>9s} {v:>+14.9f} {f['lo']:>+14.9f} "
                      f"{f['hi']:>+14.9f} {f['frac_le']:>7.4f} "
                      f"{f['frac_ge']:>7.4f} {f['dist']:>11.9f} "
                      f"{f['flag']:>9s}")

    print("\n  p_spec against the frozen NUMERIC thresholds only (rule 10):")
    for view in p3.VIEWS:
        thr = 0.05 if view == "full" else 0.10
        for R in RADII:
            p = float(s1[(view, R)]["p_n78"])
            where = "at or below" if p <= thr else "above"
            print(f"    {view:>4s} R = {R}: p_spec = {p:.9f} vs threshold "
                  f"{thr} -> {where} the threshold")

    print("\n  INSIDE / OUTSIDE / MARGINAL counts over the six (view, R) "
          "cells:")
    for kk, lbl in (("rho_a", "rho"), ("k_n78", "k"), ("p_n78", "p_spec")):
        c = {"INSIDE": 0, "OUTSIDE": 0, "MARGINAL": 0}
        for view in p3.VIEWS:
            for R in RADII:
                c[p4.flag11(float(s1[(view, R)][kk]),
                            acc_all[(view, R)][kk])["flag"]] += 1
        print(f"    {lbl:>7s}: INSIDE {c['INSIDE']}, OUTSIDE "
              f"{c['OUTSIDE']}, MARGINAL {c['MARGINAL']}  (of 6 cells)")

    print("\n  LIMITS: k and p_spec are one statistic at two scales, so "
          "their agreeing flags are NOT two pieces of evidence.  p_spec's "
          "draws are discrete (multiples of 1/79), so its fractions carry "
          "ties and frac_le + frac_ge can exceed 1; over 200 draws the "
          "smallest resolvable one-sided fraction is 0.005.  Rank "
          "fractions over small n are rank fractions, not tests.")
    print("  LIMIT: the matched-deletion range answers 'is this what "
          "deleting the same NUMBER of random positions does?'; it says "
          "nothing about WHICH positions, and it is not a significance "
          "test of the deletion itself.")

    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D19 gates: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("*** D19 GATE FAIL -- D19 stops here (task doc rule 6).  No "
              "threshold was loosened and N was not raised. ***")
    print(f"\nElapsed {time.time() - T0:.1f}s")


if __name__ == "__main__":
    main()
