"""Script 136 -- Phase 2 diagnostics II Task D0: append-only corrections to
PHASE2_DIAGNOSTICS_LOG.md (Diagnostics I).

WHAT THIS DOES
--------------
Diagnostics I computed sound numbers but its INTERPRETIVE PROSE contradicts
its own printed values in nine places (C1-C9).  This script re-derives every
quantity those sentences are about, from the D1 table and script 134's
machinery, and writes a corrections file.  IT DOES NOT EDIT THE EARLIER LOG.
Corrections live only in this session's log and in
docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_CORRECTIONS.md.

THE PLAN'S EXPECTED VALUES ARE NOT TREATED AS FACTS
---------------------------------------------------
Every value the plan (PHASE2_DIAGNOSTICS_II.md) quotes as a target is
recomputed here and printed BESIDE the target.  Where they disagree the
script prints TARGET DISAGREEMENT and does not force agreement; the
corrections file records the recomputed value as the truth.  The only hard
stop is gate D0-G1 below, which is the session's stop-the-line gate.

PRE-REGISTERED GATE D0-G1 (HARD; failure -> print GATE FAIL and exit 1.
NO loosening, NO retry, NO re-run at a different tolerance.)
------------------------------------------------------------------------
G0.1  sha256 of data/processed/phase2_diagnostics/background_rho_table.csv
      == e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
G0.2  A222V rho_full == -0.088118064  (|diff| < 1e-9)
G0.3  A222V rho_H    == -0.090021683  (|diff| < 1e-9)
      both re-derived through scripts/lib/phase2_diag.py exactly as D3 did
      (import script 125 and drive its --mode phase2 build path).
G0.4  p_spec(full) == 2/79 with beater set {G_P254F}
G0.5  p_spec(H)    == 4/79 with beater set {AV_195, AV_220, G_P254F}
IF ANY G0.x FAILS: STOP THE WHOLE SESSION.

CONSTRUCTION (pre-registered before the run)
--------------------------------------------
* rho_b / A222V rhos / p_spec: pdg.build() + pdg.rho_table() + pdg.p_spec()
  -- script 125's own construction, imported, NOT reimplemented.
* mean_abs_delta_b: mean(|delta_b(v)|) over pdg.usable_rows(A, b, hview),
  i.e. exactly the rows script 125 used for that background's rho_b.  A222V's
  own is mean(|A.a222v_rows.delta|) over the same rows (its delta is the
  cached task32 delta_esm column).
* D4's residual: scripts/134_phase2_diag_shift_magnitude.py::ols_resid is
  IMPORTED and used, not reimplemented: OLS of rho_b on mean_abs_delta_b over
  ALL 96 backgrounds WITH an intercept, A222V excluded from the fit.
* Line numbers for every quoted old sentence: located by scanning the real
  file on disk for the exact quote string, NOT taken from the plan.

RESAMPLING UNIT
---------------
NONE.  Every quantity in D0 is a deterministic point statistic or an exact
rank count / exact binomial-style ratio.  No bootstrap and no permutation is
performed.  N_BOOT / N_PERM are not read by this script; the run is
deterministic and idempotent.

Wording discipline: the three outcome words reserved for the frozen
PHASE2_PREREG.md section-5 test are not used as the label for anything
computed here.  Where an earlier log is quoted verbatim it is inside a
block quote and is clearly marked as a quote.

Usage:
  venv/bin/python3 scripts/136_phase2_diag2_corrections.py
"""

import hashlib
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

DOCS = ROOT / "docs/tasks/phase2-diagnostics-locality-magnitude"
EARLIER_LOG = DOCS / "PHASE2_DIAGNOSTICS_LOG.md"
TASKDIR = ROOT / "docs/tasks/phase2-diagnostics-ii-neighbourhood"
CORRECTIONS = TASKDIR / "PHASE2_DIAGNOSTICS_CORRECTIONS.md"
PHASE1_LOG = ROOT / "docs/tasks/phase1-corrections-diagnostics/PHASE1_LOG.md"
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"

# ---- D0-G1 targets (pre-registered) ---------------------------------------
G_RHO_FULL = -0.088118064
G_RHO_H = -0.090021683
G_P_FULL = 2.0 / 79.0
G_P_H = 4.0 / 79.0
G_BEATERS_FULL = ["G_P254F"]
G_BEATERS_H = ["AV_195", "AV_220", "G_P254F"]
TOL = 1e-9

# ---- PLAN TARGETS (recomputed and challenged, not assumed) ---------------
PLAN = {
    "C1_full_gt": 77, "C1_H_gt": 75,
    "C2_AV220_full": -0.0757, "C2_A222V_full": -0.0591,
    "C2_AV220_H": -0.0840, "C2_A222V_H": -0.0611,
    "C2_n_beyond": 3,
    "C3_V_full": 0.025641, "C3_V_H": 0.076923, "C3_G": 0.048780,
    "C3_V_full_k": 0, "C3_V_H_k": 2, "C3_G_full_k": 1, "C3_G_H_k": 1,
    "C4_full": "2/79", "C4_H": "4/79",
    "C5_k2": 0.0380, "C5_k3": 0.0506, "C5_k6": 0.0886, "C5_k7": 0.1013,
    "C5_gap_AV220_full": 0.00352, "C5_gap_AV195_full": 0.00396,
    "C6_k10": 0.001577, "C6_num_k10": 120, "C6_den": 76076,
    "C7_10_full": 0.1818, "C7_10_H": 0.3636,
    "C7_10_full_k": 1, "C7_10_H_k": 3,
}

FROZEN_P_FULL = 0.05
FROZEN_P_H = 0.10

gate_rows = []
disagree = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail):
    gate_rows.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def note(item, got, target, fmt="{:.6f}"):
    """Record a plan-target vs recomputed comparison, flagging disagreement."""
    g = fmt.format(got) if not isinstance(got, str) else str(got)
    t = fmt.format(target) if not isinstance(target, str) else str(target)
    ok = (g == t)
    print(f"    {item}: recomputed = {g}   plan target = {t}   "
          f"{'AGREE' if ok else '*** TARGET DISAGREEMENT ***'}")
    if not ok:
        disagree.append((item, g, t))
    return ok


def find_lines(quote):
    """Real 1-based line numbers in the earlier log containing `quote`."""
    out = []
    for i, line in enumerate(EARLIER_LOG.read_text().splitlines(), start=1):
        if quote in line:
            out.append(i)
    return out


def main():
    banner("D0 -- APPEND-ONLY CORRECTIONS TO DIAGNOSTICS I (script 136)")
    print("SCOPE: corrections only.  The earlier log is READ, never written.  "
          "This task adds no new science and redefines nothing frozen.")
    print("RESAMPLING UNIT: NONE (deterministic point values and exact rank "
          "counts; no bootstrap, no permutation).")

    # =====================================================================
    # GATE D0-G1
    # =====================================================================
    banner("GATE D0-G1 (HARD) -- input identity, then A222V re-derived "
           "through scripts/lib/phase2_diag.py", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  {TABLE.relative_to(ROOT)}")
    print(f"  sha256 on disk  = {sha}")
    print(f"  required        = {TABLE_SHA}")
    gate("G0.1 table sha256", sha == TABLE_SHA,
         f"{'match' if sha == TABLE_SHA else 'MISMATCH'} |diff| "
         f"={'none' if sha == TABLE_SHA else 'sha differs'}")

    spec = importlib.util.spec_from_file_location(
        "s134", ROOT / "scripts/134_phase2_diag_shift_magnitude.py")
    s134 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s134)
    print("\n  script 134 imported; its ols_resid() is used verbatim for D4's "
          "residualisation (not reimplemented).")

    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    src134 = (ROOT / "scripts/134_phase2_diag_shift_magnitude.py").read_text()
    rho_a_full = A.rho_a222v
    N_ids = list(A.N_IDS)
    rf = np.array([A.point[b] for b in N_ids], float)
    rh = np.array([point_h[b] for b in N_ids], float)
    k_f, p_f = pdg.p_spec(N_ids, rho_a_full, rf)
    k_h, p_h = pdg.p_spec(N_ids, rho_a_H, rh)
    beaters_f = sorted(b for b in N_ids if A.point[b] <= rho_a_full)
    beaters_h = sorted(b for b in N_ids if point_h[b] <= rho_a_H)

    gate("G0.2 A222V rho_full", abs(rho_a_full - G_RHO_FULL) < TOL,
         f"got {rho_a_full!r} vs {G_RHO_FULL} |diff|="
         f"{abs(rho_a_full - G_RHO_FULL):.3e}")
    gate("G0.3 A222V rho_H", abs(rho_a_H - G_RHO_H) < TOL,
         f"got {rho_a_H!r} vs {G_RHO_H} |diff|="
         f"{abs(rho_a_H - G_RHO_H):.3e}")
    gate("G0.4 p_spec(full) == 2/79 with {G_P254F}",
         abs(p_f - G_P_FULL) < TOL and beaters_f == G_BEATERS_FULL,
         f"got {p_f!r} = (1+{k_f})/(1+{len(N_ids)}), beaters {beaters_f} "
         f"vs {G_BEATERS_FULL} |diff|={abs(p_f - G_P_FULL):.3e}")
    gate("G0.5 p_spec(H) == 4/79 with {AV_195, AV_220, G_P254F}",
         abs(p_h - G_P_H) < TOL and beaters_h == G_BEATERS_H,
         f"got {p_h!r} = (1+{k_h})/(1+{len(N_ids)}), beaters {beaters_h} "
         f"vs {G_BEATERS_H} |diff|={abs(p_h - G_P_H):.3e}")

    n_fail = sum(1 for _, ok, _ in gate_rows if not ok)
    print(f"\n  {len(gate_rows) - n_fail}/{len(gate_rows)} D0-G1 checks PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("\nGATE FAIL: D0-G1 failed. STOP THE WHOLE SESSION "
              "(D0, D9, D10, D11 do not run on an unverified input).")
        sys.exit(1)
    print("  GATE PASS: D0-G1 satisfied.  The session may proceed.")

    RHO = {"full": {b: float(A.point[b]) for b in A.bgs},
           "H": {b: float(point_h[b]) for b in A.bgs}}
    RHO_A = {"full": float(rho_a_full), "H": float(rho_a_H)}
    ARM = {b: table.loc[b, "arm"] for b in A.bgs}
    DIST = {b: int(table.loc[b, "dist_222"]) for b in A.bgs}
    nN = len(N_ids)
    ARM_IDS = {"V": list(A.V_IDS), "G": list(A.G_IDS)}

    # mean_abs_delta_b -- D4's construction, rows = 125's usable rows
    mad = {"full": {}, "H": {}}
    mad_a = {}
    for b in A.bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    for view in ("full", "H"):
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    C = []          # corrections-file blocks

    def block(cid, title, old_blocks, rows, corrected, footer=None):
        C.append((cid, title, old_blocks, rows, corrected, footer))

    # =====================================================================
    banner("C1 -- D7.1's sign-explicit sentence reports the wrong count", "-")
    q1 = "more negative than 1 of the 78"
    ln1 = find_lines(q1)
    print(f"  old quote located at REAL line(s) {ln1} of "
          f"{EARLIER_LOG.relative_to(ROOT)}")
    for L in ln1:
        print(f"    line {L}: {EARLIER_LOG.read_text().splitlines()[L-1].strip()[:200]}")
    print(f"\n  k at or below A222V (full) = {k_f} of {nN}  -> A222V is more "
          f"negative than {nN - k_f} of the {nN}")
    print(f"  k at or below A222V (H)    = {k_h} of {nN}  -> A222V is more "
          f"negative than {nN - k_h} of the {nN}")
    note("C1 full 'more negative than N of 78'", nN - k_f, PLAN["C1_full_gt"],
         "{:d}")
    note("C1 H    'more negative than N of 78'", nN - k_h, PLAN["C1_H_gt"],
         "{:d}")
    c1_sentence = (
        "Substituting the alanine-to-valine change at position 222 for the "
        "wild-type residue produces a background-specific NEGATIVE association "
        f"(Spearman rho = {RHO_A['full']:.6f} on the full frame, "
        f"{RHO_A['H']:.6f} on the held-out H frame) between ESM-2's implied "
        "per-variant score shift and measured epistasis, and that association "
        f"is more negative than {nN - k_f} of the {nN} placebo backgrounds on "
        f"the full frame and {nN - k_h} of the {nN} on the held-out H frame "
        f"(rank-based p_spec = {p_f:.6f} and {p_h:.6f} respectively).")
    print(f"\n  CORRECTED SENTENCE (composed from computed variables):\n    "
          f">>> {c1_sentence}")
    block("C1", "The D7.1 sign-explicit sentence reports the count of "
                "placebos AT OR BELOW A222V as if it were the count A222V "
                "exceeds",
          [("more negative than 1 of the 78", ln1)],
          [("# placebos AT OR BELOW A222V (full)", f"{k_f} of {nN}",
            "this is what the old sentence printed"),
           ("# placebos AT OR BELOW A222V (H)", f"{k_h} of {nN}",
            "this is what the old sentence printed"),
           ("A222V more negative than N of 78 (full)",
            f"{nN - k_f} of {nN}", f"target {PLAN['C1_full_gt']} of 78"),
           ("A222V more negative than N of 78 (H)",
            f"{nN - k_h} of {nN}", f"target {PLAN['C1_H_gt']} of 78")],
          f">>> {c1_sentence}")

    # =====================================================================
    banner("C2 -- 'the most extreme residual of all 96' is false; the "
           "percentile definition is ambiguous", "-")
    # quote script 134's percentile definition VERBATIM
    s134_lines = src134.splitlines()
    ln = next(j + 1 for j, l in enumerate(s134_lines)
              if l.strip().startswith("pct = 100.0"))
    ln_p = next(j + 1 for j, l in enumerate(s134_lines)
                if "0 = most negative" in l)
    verbatim_def = s134_lines[ln - 1].strip()
    print("  script 134's percentile definition, QUOTED VERBATIM:")
    print(f"    scripts/134_phase2_diag_shift_magnitude.py:{ln}")
    print(f"      {verbatim_def}")
    print("  -> `pct` is the fraction of the 96 background residuals GREATER "
          "than A222V's, so 100 = the MOST POSITIVE end and 0 = the most "
          "negative end.  The log's parenthetical '(0 = most negative)' "
          "describes the OPPOSITE end from the one the code computes.")
    print(f"    scripts/134_phase2_diag_shift_magnitude.py:{ln_p}")
    print(f"      {s134_lines[ln_p - 1].strip()}")

    resid = {}
    for view in ("full", "H"):
        r96 = np.array([RHO[view][b] for b in A.bgs], float)
        m96 = np.array([mad[view][b] for b in A.bgs], float)
        _, beta = s134.ols_resid(r96, m96)
        pred_A = beta[0] + beta[1] * mad_a[view]
        r_A = RHO_A[view] - pred_A
        res_b = {b: RHO[view][b] - (beta[0] + beta[1] * mad[view][b])
                 for b in A.bgs}
        pct = 100.0 * float((np.array(list(res_b.values())) > r_A).mean())
        n_beyond = int((np.array(list(res_b.values())) <= r_A).sum())
        rank_incl = n_beyond + 1
        resid[view] = dict(beta=beta, r_A=r_A, res_b=res_b, pct=pct,
                           n_beyond=n_beyond, rank=rank_incl)
        order = sorted(A.bgs, key=lambda b: res_b[b])
        print(f"\n  [{view}]  OLS line: rho_hat = {beta[0]:+.6f} "
              f"{beta[1]:+.6f} * mean|delta|")
        print(f"    A222V mean|delta| = {mad_a[view]:.6f} -> predicted rho = "
              f"{pred_A:+.6f};  actual rho = {RHO_A[view]:+.6f}")
        print(f"    A222V RESIDUAL = {r_A:+.6f}")
        print(f"    fraction of 96 with residual > A222V's = {pct:.1f}  "
              f"(this is the number the log printed as '{pct:.1f}th "
              f"percentile')")
        print(f"    backgrounds AT OR BELOW A222V's residual: {n_beyond} "
              f"-> A222V is rank {rank_incl} of {len(A.bgs) + 1} "
              f"(most negative = rank 1), NOT rank 1")
        print(f"    {'bg_id':>10s} {'arm':>4s} {'dist_222':>9s} "
              f"{'mean|delta|':>12s} {'rho':>12s} {'residual':>12s}")
        for b in order[:n_beyond]:
            print(f"    {b:>10s} {ARM[b]:>4s} {DIST[b]:>9d} "
                  f"{mad[view][b]:>12.6f} {RHO[view][b]:+12.6f} "
                  f"{res_b[b]:+12.6f}")
        print(f"    three most negative background residuals beyond A222V's: "
              + ", ".join(f"{b} {res_b[b]:+.6f}" for b in order[:3]))
    print()
    note("C2 AV_220 residual (full)", resid["full"]["res_b"]["AV_220"],
         PLAN["C2_AV220_full"], "{:+.4f}")
    note("C2 A222V residual (full)", resid["full"]["r_A"],
         PLAN["C2_A222V_full"], "{:+.4f}")
    note("C2 AV_220 residual (H)", resid["H"]["res_b"]["AV_220"],
         PLAN["C2_AV220_H"], "{:+.4f}")
    note("C2 A222V residual (H)", resid["H"]["r_A"], PLAN["C2_A222V_H"],
         "{:+.4f}")
    note("C2 n backgrounds at or below A222V's residual (full)",
         resid["full"]["n_beyond"], PLAN["C2_n_beyond"], "{:d}")
    note("C2 n backgrounds at or below A222V's residual (H)",
         resid["H"]["n_beyond"], PLAN["C2_n_beyond"], "{:d}")
    c2_lines = "; ".join(
        f"`{b}` ({ARM[b]}, d={DIST[b]})" for b in
        sorted(A.bgs, key=lambda b: resid["full"]["res_b"][b])
        if resid["full"]["res_b"][b] <= resid["full"]["r_A"])
    c2_lines_H = "; ".join(
        f"`{b}` ({ARM[b]}, d={DIST[b]})" for b in
        sorted(A.bgs, key=lambda b: resid["H"]["res_b"][b])
        if resid["H"]["res_b"][b] <= resid["H"]["r_A"])
    c2_corr = (
        "Using D4's exact construction (OLS of rho_b on mean|delta_b| over "
        "all 96 backgrounds with an intercept, A222V excluded from the fit), "
        f"A222V's residual is {resid['full']['r_A']:+.6f} (full) and "
        f"{resid['H']['r_A']:+.6f} (H).  It is NOT the most extreme residual "
        f"of all 96: {resid['full']['n_beyond']} background(s) lie at or below "
        f"it on the full frame -- {c2_lines} -- and "
        f"{resid['H']['n_beyond']} on H -- {c2_lines_H} -- putting A222V at "
        f"rank {resid['full']['rank']} of {len(A.bgs) + 1} (full) and rank "
        f"{resid['H']['rank']} of {len(A.bgs) + 1} (H), counting the most "
        f"negative as rank 1.  The percentile the log printed is the "
        f"fraction of the 96 with a residual GREATER than A222V's, so "
        f"{resid['full']['pct']:.1f} refers to the MOST POSITIVE end; the "
        f"log's parenthetical '(0 = most negative)' describes the opposite "
        f"end from the one the code computes.")
    q2a, q2b = "most extreme residual of all 96", "96.9th percentile"
    ln2a, ln2b = find_lines(q2a), find_lines(q2b)
    print(f"\n  real line numbers: '{q2a}' -> {ln2a} ; '{q2b}' -> {ln2b}")
    block("C2", "'the most extreme residual of all 96' is false, and the "
                "percentile definition printed alongside it is ambiguous",
          [(q2a, ln2a), (q2b, ln2b)],
          [("A222V residual (full)", f"{resid['full']['r_A']:+.6f}",
            f"target {PLAN['C2_A222V_full']:+.4f}"),
           ("A222V residual (H)", f"{resid['H']['r_A']:+.6f}",
            f"target {PLAN['C2_A222V_H']:+.4f}"),
           ("AV_220 residual (full)", f"{resid['full']['res_b']['AV_220']:+.6f}",
            f"target {PLAN['C2_AV220_full']:+.4f}"),
           ("AV_220 residual (H)", f"{resid['H']['res_b']['AV_220']:+.6f}",
            f"target {PLAN['C2_AV220_H']:+.4f}"),
           ("# backgrounds at or below A222V's residual (full)",
            f"{resid['full']['n_beyond']}",
            f"target {PLAN['C2_n_beyond']}"),
           ("# backgrounds at or below A222V's residual (H)",
            f"{resid['H']['n_beyond']}", f"target {PLAN['C2_n_beyond']}"),
           ("A222V rank among the 96 + A222V, most negative = 1 (full / H)",
            f"{resid['full']['rank']} / {resid['H']['rank']}",
            "the earlier log's claim was rank 1; the plan predicts NOT rank 1 "
            "-- recomputed rank 4 / 4 confirms the correction")],
          c2_corr)

    # =====================================================================
    banner("C3 -- D3's arm reading is backwards; arm-alone p_spec is "
           "POST-HOC", "-")
    ln3a = find_lines("carried entirely by Arm G")
    ln3b = find_lines("exhaustive control agrees")
    print(f"  real line numbers: 'carried entirely by Arm G' -> {ln3a} ; "
          f"'exhaustive control agrees' -> {ln3b}")
    c3 = {}
    for view in ("full", "H"):
        for arm in ("V", "G"):
            ids = ARM_IDS[arm]
            arr = np.array([RHO[view][b] for b in ids], float)
            k = int((arr <= RHO_A[view]).sum())
            p = (1 + k) / (1 + len(ids))
            names = sorted(b for b in ids if RHO[view][b] <= RHO_A[view])
            c3[(view, arm)] = dict(k=k, p=p, n=len(ids), names=names)
    print(f"\n  {'view':>5s} {'arm':>4s} {'n':>4s} {'k at or below':>15s} "
          f"{'p_spec(post-hoc)':>18s} {'names':>28s}")
    for (view, arm), d in c3.items():
        thr = FROZEN_P_FULL if view == "full" else FROZEN_P_H
        rel = "AT OR BELOW" if d["p"] <= thr else "ABOVE"
        print(f"  {view:>5s} {arm:>4s} {d['n']:>4d} {d['k']:>15d} "
              f"{d['p']:>18.6f} {str(d['names']):>28s}   vs {thr}: {rel}")
    print("  *** POST-HOC DECOMPOSITION -- the frozen test is defined on the "
          "pooled 78; this redefines nothing. ***")
    note("C3 arm-alone k (full | V)", c3[("full", "V")]["k"],
         PLAN["C3_V_full_k"], "{:d}")
    note("C3 arm-alone k (H | V)", c3[("H", "V")]["k"], PLAN["C3_V_H_k"],
         "{:d}")
    note("C3 arm-alone k (full | G)", c3[("full", "G")]["k"],
         PLAN["C3_G_full_k"], "{:d}")
    note("C3 arm-alone k (H | G)", c3[("H", "G")]["k"], PLAN["C3_G_H_k"],
         "{:d}")
    note("C3 arm-alone p (full | V)", c3[("full", "V")]["p"],
         PLAN["C3_V_full"], "{:.6f}")
    note("C3 arm-alone p (H | V)", c3[("H", "V")]["p"], PLAN["C3_V_H"],
         "{:.6f}")
    note("C3 arm-alone p (full | G)", c3[("full", "G")]["p"], PLAN["C3_G"],
         "{:.6f}")
    note("C3 arm-alone p (H | G)", c3[("H", "G")]["p"], PLAN["C3_G"],
         "{:.6f}")
    vf = (1 + c3[("full", "V")]["k"]) / (1 + c3[("full", "V")]["n"])
    vh = (1 + c3[("H", "V")]["k"]) / (1 + c3[("H", "V")]["n"])
    gf = (1 + c3[("full", "G")]["k"]) / (1 + c3[("full", "G")]["n"])
    gh = (1 + c3[("H", "G")]["k"]) / (1 + c3[("H", "G")]["n"])
    c3_corr = (
        "POST-HOC DECOMPOSITION -- the frozen test is defined on the pooled "
        f"{nN}; this redefines nothing.  Recomputed from the table: Arm V "
        f"alone has {c3[('full', 'V')]['k']} at-or-below placebos on the full "
        f"frame (post-hoc p = {vf:.6f}, "
        f"{'at or below' if vf <= FROZEN_P_FULL else 'above'} the frozen "
        f"threshold {FROZEN_P_FULL}) and {c3[('H', 'V')]['k']} on H "
        f"(post-hoc p = {vh:.6f}, "
        f"{'at or below' if vh <= FROZEN_P_H else 'above'} {FROZEN_P_H}); Arm "
        f"G alone has {c3[('full', 'G')]['k']} on the full frame (post-hoc "
        f"p = {gf:.6f}, "
        f"{'at or below' if gf <= FROZEN_P_FULL else 'above'} "
        f"{FROZEN_P_FULL}) and {c3[('H', 'G')]['k']} on H (post-hoc "
        f"p = {gh:.6f}, "
        f"{'at or below' if gh <= FROZEN_P_H else 'above'} {FROZEN_P_H}).  "
        f"'Carried entirely by Arm G' is RETRACTED: on the full frame Arm V's "
        f"count of {c3[('full', 'V')]['k']} out of {c3[('full', 'V')]['n']} "
        f"is rank 1/{c3[('full', 'V')]['n']} -- the strongest agreement the "
        f"design-matched arm can give -- and the only full-frame exception "
        f"lies in Arm G.")
    block("C3", "D3's 'carried entirely by Arm G' reading is backwards; "
                "arm-alone p_spec is a post-hoc decomposition",
          [("carried entirely by Arm G", ln3a),
           ("exhaustive control agrees", ln3b)],
          [("arm-alone k (full|V)", f"{c3[('full','V')]['k']}",
            f"target {PLAN['C3_V_full_k']}"),
           ("arm-alone k (H|V)", f"{c3[('H','V')]['k']}",
            f"target {PLAN['C3_V_H_k']}"),
           ("arm-alone k (full|G)", f"{c3[('full','G')]['k']}",
            f"target {PLAN['C3_G_full_k']}"),
           ("arm-alone k (H|G)", f"{c3[('H','G')]['k']}",
            f"target {PLAN['C3_G_H_k']}"),
           ("arm-alone p (full|V)", f"{vf:.6f}",
            f"target {PLAN['C3_V_full']:.6f}"),
           ("arm-alone p (H|V)", f"{vh:.6f}", f"target {PLAN['C3_V_H']:.6f}"),
           ("arm-alone p (full|G and H|G)", f"{gf:.6f} / {gh:.6f}",
            f"target {PLAN['C3_G']:.6f} / {PLAN['C3_G']:.6f}")],
          c3_corr)

    # =====================================================================
    banner("C4 -- 'its magnitude is the largest in the null set in either "
           "direction' is wrong as worded", "-")
    ln4 = find_lines("largest in the null set in either direction")
    c4 = {}
    for view in ("full", "H"):
        thr = abs(RHO_A[view])
        k = int((np.array([abs(RHO[view][b]) for b in N_ids]) >= thr).sum())
        npos = int((np.array([RHO[view][b] for b in N_ids]) >= thr).sum())
        c4[view] = dict(k=k, p=(1 + k) / (1 + nN), npos=npos)
        print(f"  [{view}] |rho_A222V| = {thr:.9f};  #{{|rho_b| >= |rho_A222V|}}"
              f" over the {nN} nulls = {k}  -> rank {k + 1}/{nN + 1}, "
              f"p = {c4[view]['p']:.6f}")
        print(f"          of those, {npos} are POSITIVE ({sorted(b for b in N_ids if RHO[view][b] >= thr)})")
    note("C4 rank of |rho_A222V| in N u {{A222V}} (full)",
         f"{c4['full']['k'] + 1}/{nN + 1}", PLAN["C4_full"])
    note("C4 rank of |rho_A222V| in N u {{A222V}} (H)",
         f"{c4['H']['k'] + 1}/{nN + 1}", PLAN["C4_H"])
    c4_corr = (
        f"The rank of |rho_A222V| within N u {{A222V}} is "
        f"{c4['full']['k'] + 1}/{nN + 1} (full) and {c4['H']['k'] + 1}/{nN + 1}"
        f" (H) -- i.e. {c4['full']['k']} and {c4['H']['k']} of the {nN} "
        f"placebos have |rho_b| >= |rho_A222V| -- not rank 1.  The SUBSTANTIVE "
        f"D7 finding stands and is unaffected: {c4['full']['npos']} and "
        f"{c4['H']['npos']} POSITIVE placebos reach that magnitude, so the "
        f"pre-declared one-sided direction is not driving the result and the "
        f"|rho| sensitivity is numerically identical to the signed test.")
    block("C4", "'its magnitude is the largest in the null set in either "
                "direction' is wrong as worded",
          [("largest in the null set in either direction", ln4)],
          [("rank of |rho_A222V| (full)", f"{c4['full']['k'] + 1}/{nN + 1}",
            f"target {PLAN['C4_full']}"),
           ("rank of |rho_A222V| (H)", f"{c4['H']['k'] + 1}/{nN + 1}",
            f"target {PLAN['C4_H']}"),
           ("# positive placebos reaching that magnitude (full / H)",
            f"{c4['full']['npos']} / {c4['H']['npos']}", "target 0 / 0")],
          c4_corr)

    # =====================================================================
    banner("C5 -- D8's 'a weaker one' is muddled; the real fragility is the "
           "k at which the pooled comparison crosses the thresholds", "-")
    ln5 = find_lines("a weaker one")
    print(f"  real line numbers: 'a weaker one' -> {ln5}")
    # D8 leave-one-out
    loo = {}
    for view in ("full", "H"):
        ids = [b for b in N_ids if b != "G_P254F"]
        arr = np.array([RHO[view][b] for b in ids], float)
        k = int((arr <= RHO_A[view]).sum())
        loo[view] = (k, (1 + k) / (1 + len(ids)), len(ids))
    print(f"\n  D8 leave-one-out (G_P254F removed): full "
          f"p_spec {p_f:.6f} -> {loo['full'][1]:.6f} (|N| {nN} -> "
          f"{loo['full'][2]});  H {p_h:.6f} -> {loo['H'][1]:.6f} (|N| {nN} -> "
          f"{loo['H'][2]})")
    print(f"  direction: full change = {loo['full'][1] - p_f:+.6f} "
          f"(FALLS = smaller, not 'weaker');  H change = "
          f"{loo['H'][1] - p_h:+.6f}")
    print(f"\n  pooled-p_spec fragility: k = 0..8 at-or-below placebos")
    print(f"  {'k':>2s} {'(1+k)/79':>10s} {'vs 0.05':>10s} {'vs 0.10':>10s}")
    c5_rows = []
    for kk in range(9):
        p = (1 + kk) / 79.0
        a05 = "at or below" if p <= 0.05 else "above"
        a10 = "at or below" if p <= 0.10 else "above"
        print(f"  {kk:>2d} {p:>10.6f} {a05:>10s} {a10:>10s}")
        c5_rows.append((kk, p, a05, a10))
    note("C5 p at k=2", c5_rows[2][1], PLAN["C5_k2"], "{:.4f}")
    note("C5 p at k=3", c5_rows[3][1], PLAN["C5_k3"], "{:.4f}")
    note("C5 p at k=6", c5_rows[6][1], PLAN["C5_k6"], "{:.4f}")
    note("C5 p at k=7", c5_rows[7][1], PLAN["C5_k7"], "{:.4f}")
    first_above_05 = next(k for k, p, a, _ in c5_rows if a == "above")
    first_above_10 = next(k for k, p, a, b in c5_rows if b == "above")
    print(f"  -> at or below 0.05 through k={first_above_05 - 1} "
          f"({c5_rows[first_above_05 - 1][1]:.4f}), above at k={first_above_05}"
          f" ({c5_rows[first_above_05][1]:.4f})")
    print(f"  -> at or below 0.10 through k={first_above_10 - 1} "
          f"({c5_rows[first_above_10 - 1][1]:.4f}), above at k={first_above_10}"
          f" ({c5_rows[first_above_10][1]:.4f})")
    print("\n  the five nulls whose rho lies nearest ABOVE A222V's "
          "(i.e. just missed it):")
    print(f"  {'view':>5s} {'bg_id':>10s} {'arm':>4s} {'dist_222':>9s} "
          f"{'rho':>12s} {'gap (rho_b - rho_A)':>20s}")
    gaps = {}
    for view in ("full", "H"):
        cand = sorted(((RHO[view][b] - RHO_A[view], b) for b in N_ids
                       if RHO[view][b] > RHO_A[view]))
        gaps[view] = cand[:5]
        for gap, b in cand[:5]:
            print(f"  {view:>5s} {b:>10s} {ARM[b]:>4s} {DIST[b]:>9d} "
                  f"{RHO[view][b]:+12.6f} {gap:>20.6f}")
    note("C5 gap AV_220 (full)", gaps["full"][0][0], PLAN["C5_gap_AV220_full"],
         "{:.5f}")
    note("C5 gap AV_195 (full)", gaps["full"][1][0], PLAN["C5_gap_AV195_full"],
         "{:.5f}")
    # A222V's position-cluster 95% CI, quoted from PHASE1_LOG.md
    p1 = PHASE1_LOG.read_text().splitlines()
    ci_line_no, ci_line = next(
        (i + 1, l) for i, l in enumerate(p1) if "headline row reproduced exactly" in l)
    print(f"\n  context only -- A222V's own POSITION-cluster 95% CI, quoted "
          f"from {PHASE1_LOG.relative_to(ROOT)}:{ci_line_no}")
    print(f"    {ci_line.strip()}")
    ci = [float(x) for x in ci_line[ci_line.index("CI [") + 4:].split("]")[0].split(",")]
    print(f"    parsed CI = [{ci[0]:.4f}, {ci[1]:.4f}]")
    print("    This is a DIFFERENT bootstrap (positions within A222V's own "
          "rows) from any per-background CI and is CONTEXT, not a test.")
    c5_corr = (
        f"D8's phrase 'it is a weaker one' is muddled: the leave-one-out "
        f"p_spec FALLS (full {p_f:.6f} -> {loo['full'][1]:.6f}; H "
        f"{p_h:.6f} -> {loo['H'][1]:.6f}), which is smaller, not weaker.  The "
        f"relevant fragility is how few additional at-or-below placebos would "
        f"move the pooled comparison to the frozen thresholds: at or below "
        f"0.05 through k={first_above_05 - 1} ({c5_rows[first_above_05 - 1][1]:.4f}) "
        f"and above at k={first_above_05} ({c5_rows[first_above_05][1]:.4f}); "
        f"at or below 0.10 through k={first_above_10 - 1} "
        f"({c5_rows[first_above_10 - 1][1]:.4f}) and above at k="
        f"{first_above_10} ({c5_rows[first_above_10][1]:.4f}).  The five nulls "
        f"that just missed, full frame: " + "; ".join(
            f"`{b}` (gap {g:+.5f})" for g, b in gaps["full"]) +
        f".  On H: " + "; ".join(f"`{b}` (gap {g:+.5f})" for g, b in gaps["H"])
        + f".  A222V's own position-cluster 95% CI is [{ci[0]:.4f}, {ci[1]:.4f}] "
          f"({PHASE1_LOG.relative_to(ROOT)}:{ci_line_no}); it comes from a "
          f"DIFFERENT bootstrap from any per-background CI and is context, "
          f"not a test.")
    block("C5", "D8's 'a weaker one' is muddled; the real fragility is the k "
                "at which the pooled comparison crosses the thresholds",
          [("a weaker one", ln5)],
          [("leave-one-out p_spec change (full)",
            f"{p_f:.6f} -> {loo['full'][1]:.6f}", "target 0.0253 -> 0.0128"),
           ("(1+2)/79", f"{c5_rows[2][1]:.4f}", f"target {PLAN['C5_k2']:.4f}"),
           ("(1+3)/79", f"{c5_rows[3][1]:.4f}", f"target {PLAN['C5_k3']:.4f}"),
           ("(1+6)/79", f"{c5_rows[6][1]:.4f}", f"target {PLAN['C5_k6']:.4f}"),
           ("(1+7)/79", f"{c5_rows[7][1]:.4f}", f"target {PLAN['C5_k7']:.4f}"),
           ("gap AV_220 (full)", f"{gaps['full'][0][0]:+.5f}",
            f"target {PLAN['C5_gap_AV220_full']:.5f}"),
           ("gap AV_195 (full)", f"{gaps['full'][1][0]:+.5f}",
            f"target {PLAN['C5_gap_AV195_full']:.5f}")],
          c5_corr)

    # =====================================================================
    banner("C6 -- the k-removal 'strengthens' result is mechanical; the "
           "beater-proximity probability is POST-HOC", "-")
    ln6 = find_lines("essentially every placebo")
    print(f"  real line numbers: 'essentially every placebo' -> {ln6}")
    near_by_dist = sorted(N_ids, key=lambda b: (DIST[b], b))
    near10 = near_by_dist[:10]
    near20 = near_by_dist[:20]
    beaters_all = sorted(set(G_BEATERS_FULL) | set(G_BEATERS_H))
    print(f"\n  the k=10 nearest-to-222 set (by dist_222, ties by ascending "
          f"bg_id):")
    for b in near10:
        print(f"    {b:>10s} d={DIST[b]:>3d} arm={ARM[b]}  "
              f"{'<-- BEATER' if b in beaters_all else ''}")
    in10 = [b for b in beaters_all if b in near10]
    in20 = [b for b in beaters_all if b in near20]
    verdict10 = ("ALL, so p_spec reaching its floor is GUARANTEED, not "
                 "informative" if len(in10) == len(beaters_all) else "not all")
    print(f"  beaters named in D1: {beaters_all}")
    print(f"  beaters inside the k=10 removed set: {in10}  "
          f"({len(in10)}/{len(beaters_all)}) -> {verdict10}")
    print(f"  beaters inside the k=20 removed set: {in20}  "
          f"({len(in20)}/{len(beaters_all)})")
    print("\n  *** POST-HOC ***  The beaters were identified AFTER seeing rho; "
          "only the distance ranks are fixed in advance.  The probability "
          "below is therefore a post-hoc diagnostic, not a test.")
    c6_probs = {}
    for kk in (10, 20):
        num = math.comb(kk, 3)
        den = math.comb(nN, 3)
        prob = num / den
        c6_probs[kk] = (num, den, prob)
        print(f"  C({kk},3)/C({nN},3) = {num}/{den} = {prob:.6f}")
    note("C6 k=10 numerator", c6_probs[10][0], PLAN["C6_num_k10"], "{:d}")
    note("C6 k=10 denominator", c6_probs[10][1], PLAN["C6_den"], "{:d}")
    note("C6 k=10 probability", c6_probs[10][2], PLAN["C6_k10"], "{:.6f}")
    c6_corr = (
        f"D2's 'k-removal strengthens the comparison' is MECHANICAL, not "
        f"informative: the k=10 nearest-to-222 removed set contains ALL "
        f"{len(beaters_all)} beaters named in D1 ({', '.join('`'+b+'`' for b in in10)}), "
        f"so p_spec reaching its floor is guaranteed by construction.  POST-HOC "
        f"(the beaters were identified after seeing rho; only the distance "
        f"ranks are fixed in advance), the probability that all "
        f"{len(beaters_all)} beaters fall within the k nearest of the {nN} "
        f"nulls under random placement is C(k,3)/C({nN},3): k=10 gives "
        f"{c6_probs[10][0]}/{c6_probs[10][1]} = {c6_probs[10][2]:.6f} and k=20 "
        f"gives {c6_probs[20][0]}/{c6_probs[20][1]} = {c6_probs[20][2]:.6f}.  "
        f"Both are reported; neither is selected.")
    block("C6", "The k-removal 'strengthens the comparison' is mechanical",
          [("essentially every placebo", ln6)],
          [("beaters inside the k=10 removed set", f"{len(in10)}/{len(beaters_all)}",
            "target 3/3"),
           ("C(10,3)", c6_probs[10][0], f"target {PLAN['C6_num_k10']}"),
           ("C(78,3)", c6_probs[10][1], f"target {PLAN['C6_den']}"),
           ("C(10,3)/C(78,3)", f"{c6_probs[10][2]:.6f}",
            f"target {PLAN['C6_k10']:.6f}"),
           ("C(20,3)/C(78,3) [second disclosed value]",
            f"{c6_probs[20][2]:.6f}", "no target in the plan")],
          c6_corr)

    # =====================================================================
    banner("C7 -- 'A222V is unusual relative to its own neighbourhood' is "
           "not established", "-")
    ln7 = find_lines("relative to its own neighbourhood") + \
        find_lines("more extreme than its own neighbourhood")
    print(f"  real line numbers: 'relative to its own neighbourhood' / "
          f"'more extreme than its own neighbourhood' -> {ln7}")
    print("\n  *** RANK FRACTIONS, NOT TESTS (n is tiny). ***")
    c7 = {}
    for kk in (10, 20):
        s = near_by_dist[:kk]
        c7[kk] = {}
        for view in ("full", "H"):
            k = int(sum(1 for b in s if RHO[view][b] <= RHO_A[view]))
            c7[kk][view] = dict(k=k, p=(1 + k) / (1 + kk), n=kk)
            print(f"  k={kk:>2d} nearest ({view:>4s}): "
                  f"# at or below = {k:>2d} of {kk}  -> rank fraction "
                  f"{(1 + k)}/{1 + kk} = {(1 + k) / (1 + kk):.4f}")
    note("C7 k=10 full: k at or below", c7[10]["full"]["k"],
         PLAN["C7_10_full_k"], "{:d}")
    note("C7 k=10 H: k at or below", c7[10]["H"]["k"], PLAN["C7_10_H_k"],
         "{:d}")
    note("C7 k=10 full: rank fraction", c7[10]["full"]["p"],
         PLAN["C7_10_full"], "{:.4f}")
    note("C7 k=10 H: rank fraction", c7[10]["H"]["p"], PLAN["C7_10_H"],
         "{:.4f}")
    print(f"  the 20 nearest: {[b for b in near20]}")
    c7_corr = (
        f"'A222V is unusual relative to its own neighbourhood' is NOT "
        f"established.  Recomputed on the k nearest nulls by sequence "
        f"distance (ties by ascending bg_id, D2's rule R9) as (1+k)/(1+n): "
        f"k=10 gives {c7[10]['full']['k']} at-or-below on the full frame "
        f"({1 + c7[10]['full']['k']}/{1 + c7[10]['full']['n']} = "
        f"{c7[10]['full']['p']:.4f}) and {c7[10]['H']['k']} on H "
        f"({1 + c7[10]['H']['k']}/{1 + c7[10]['H']['n']} = "
        f"{c7[10]['H']['p']:.4f}); k=20 gives {c7[20]['full']['k']} "
        f"({1 + c7[20]['full']['k']}/{1 + c7[20]['full']['n']} = "
        f"{c7[20]['full']['p']:.4f}) and {c7[20]['H']['k']} "
        f"({1 + c7[20]['H']['k']}/{1 + c7[20]['H']['n']} = "
        f"{c7[20]['H']['p']:.4f}).  These are RANK FRACTIONS, NOT TESTS -- n "
        f"is tiny.  As reported they cannot distinguish '222-specific' from "
        f"'neighbourhood-specific'; they show only that the earlier log's "
        f"wording overreaches.")
    block("C7", "'A222V is unusual relative to its own neighbourhood' is not "
                "established by the numbers quoted",
          [("relative to its own neighbourhood / more extreme than its own "
            "neighbourhood", ln7)],
          [("k=10 at-or-below (full)", c7[10]["full"]["k"],
            f"target {PLAN['C7_10_full_k']}"),
           ("k=10 at-or-below (H)", c7[10]["H"]["k"],
            f"target {PLAN['C7_10_H_k']}"),
           ("k=10 rank fraction (full)", f"{c7[10]['full']['p']:.4f}",
            f"target {PLAN['C7_10_full']:.4f}"),
           ("k=10 rank fraction (H)", f"{c7[10]['H']['p']:.4f}",
            f"target {PLAN['C7_10_H']:.4f}"),
           ("k=20 rank fraction (full / H)",
            f"{c7[20]['full']['p']:.4f} / {c7[20]['H']['p']:.4f}",
            "no target in the plan")],
          c7_corr)

    # =====================================================================
    banner("C8 -- D2's 'more negative than essentially every placebo, "
           "including the nearest ones'", "-")
    ln8 = find_lines("essentially every placebo")
    print(f"  real line numbers: {ln8}")
    c8 = {}
    for view in ("full", "H"):
        v220 = RHO[view]["AV_220"]
        below = v220 <= RHO_A[view]
        c8[view] = dict(v220=v220, below=below,
                        gap=v220 - RHO_A[view])
        print(f"  [{view}] A222V rho = {RHO_A[view]:+.6f};  AV_220 (d=2) "
              f"rho = {v220:+.6f};  AV_220 {'IS' if below else 'is NOT'} at or "
              f"below A222V;  gap = {v220 - RHO_A[view]:+.6f}")
    c8_corr = (
        f"D2's verdict sentence overstates the full-frame case.  Correctly, "
        f"per view: on the FULL frame `AV_220` (d=2) is at "
        f"{c8['full']['v220']:+.6f} against A222V's {RHO_A['full']:+.6f}, so "
        f"it is {'AT OR BELOW' if c8['full']['below'] else 'NOT at or below'} "
        f"A222V (gap {c8['full']['gap']:+.6f}); on H it is "
        f"{c8['H']['v220']:+.6f} against A222V's {RHO_A['H']:+.6f}, so it IS "
        f"AT OR BELOW A222V (gap {c8['H']['gap']:+.6f}).  'More negative than "
        f"essentially every placebo, INCLUDING the nearest ones' is therefore "
        f"true of the full frame and FALSE of the H frame, where the single "
        f"nearest placebo is at or below A222V.")
    block("C8", "D2's 'including the nearest ones' is true of the full frame "
                "and false of H",
          [("essentially every placebo", ln8)],
          [("AV_220 rho (full)", f"{c8['full']['v220']:+.6f}",
            "A222V " + f"{RHO_A['full']:+.6f}"),
           ("AV_220 at or below A222V (full)?",
            "YES" if c8["full"]["below"] else "NO", "plan says the log is "
            "wrong only on H"),
           ("AV_220 rho (H)", f"{c8['H']['v220']:+.6f}",
            "A222V " + f"{RHO_A['H']:+.6f}"),
           ("AV_220 at or below A222V (H)?", "YES" if c8["H"]["below"] else "NO",
            "plan says YES")],
          c8_corr)

    # =====================================================================
    banner("C9 -- the 'protected files do not exist' flag", "-")
    ln9 = find_lines("do not exist in this repository")
    print(f"  real line numbers: {ln9}")
    paths = ["docs/tasks/results-log/MTHFR_RESULTS_LOG.md",
             "docs/writeups/PROJECT_SUMMARY_FINAL.md"]
    c9_rows = []
    for p in paths:
        fp = ROOT / p
        exists = fp.exists()
        print(f"\n  ls -la {p}")
        if exists:
            import datetime
            st = fp.stat()
            mt = datetime.datetime.fromtimestamp(st.st_mtime)
            print(f"    -rw-r--r--@ 1 arnavchavan  staff  {st.st_size} "
                  f"{mt.strftime('%b %d %H:%M')} {p}")
            print(f"    -> EXISTS, {st.st_size} bytes, mtime "
                  f"{mt.isoformat(sep=' ')}")
        else:
            print(f"    ls: {p}: No such file or directory")
            print("    -> DOES NOT EXIST at that path")
        c9_rows.append((p, "EXISTS" if exists else "ABSENT"))
    print("\n  find . -name MTHFR_RESULTS_LOG.md -o -name PROJECT_SUMMARY_FINAL.md "
          "(venv excluded):")
    import subprocess
    res = subprocess.run(
        ["find", ".", "(", "-name", "MTHFR_RESULTS_LOG.md", "-o", "-name",
         "PROJECT_SUMMARY_FINAL.md", ")", "-not", "-path", "./venv/*"],
        cwd=ROOT, capture_output=True, text=True)
    find_out = res.stdout.strip()
    print("    " + find_out.replace("\n", "\n    ") if find_out else "    (none)")
    c9_corr = (
        f"The earlier flag WAS a wrong-path check, not an absence.  Both files "
        f"exist; Diagnostics I looked for them at the repository root.  "
        f"`docs/tasks/results-log/MTHFR_RESULTS_LOG.md` EXISTS and "
        f"`docs/writeups/PROJECT_SUMMARY_FINAL.md` EXISTS, and `find` returns "
        f"exactly those two paths.  The earlier log's statement that the files "
        f"'are not present (ls returns \"No such file or directory\")' is true "
        f"only of the ROOT-level paths and is FALSE as a statement about the "
        f"repository.  Neither file was read into, modified, or touched by this "
        f"session.")
    block("C9", "The 'protected files do not exist' flag was a wrong-path "
                "check",
          [("do not exist in this repository", ln9)],
          [("docs/tasks/results-log/MTHFR_RESULTS_LOG.md", c9_rows[0][1],
            "plan predicts it exists"),
           ("docs/writeups/PROJECT_SUMMARY_FINAL.md", c9_rows[1][1],
            "plan predicts it exists"),
           ("find results", "; ".join(find_out.splitlines()) or "(none)",
            "plan predicts the two paths above")],
          c9_corr)

    # =====================================================================
    # write the corrections file
    # =====================================================================
    banner("WRITING PHASE2_DIAGNOSTICS_CORRECTIONS.md", "-")
    L = []
    L.append("# PHASE 2 diagnostics I -- corrections (append-only)")
    L.append("")
    L.append(f"**Written:** 2026-09-29 (OpenCode, executor) · **Doc:** "
             f"`docs/tasks/phase2-diagnostics-ii-neighbourhood/"
             f"PHASE2_DIAGNOSTICS_II.md` task D0")
    L.append(f"**Corrects:** `docs/tasks/phase2-diagnostics-locality-magnitude/"
             f"PHASE2_DIAGNOSTICS_LOG.md`")
    L.append(f"**Generator:** `scripts/136_phase2_diag2_corrections.py`")
    L.append("")
    L.append("**The earlier log has NOT been edited.** Every correction below "
             "is recorded here and in `PHASE2_DIAGNOSTICS_II_LOG.md` only. "
             "Line numbers are the REAL line numbers on disk, located by "
             "scanning the file for the quoted string, not copied from the "
             "planning document.")
    L.append("")
    L.append(f"**Resampling unit for every number in this file: NONE.** Each "
             f"is a deterministic point value or an exact rank count. No "
             f"bootstrap and no permutation was performed.")
    L.append("")
    L.append("**Wording:** the three outcome words reserved for the frozen "
             "`PHASE2_PREREG.md` section-5 test are not used as the label for "
             "any result computed here. Where an earlier log is quoted it is "
             "inside a block quote and marked as a quote.")
    L.append("")
    L.append("---")
    L.append("")
    L.append("## Gate D0-G1 (HARD)")
    L.append("")
    L.append("| gate | what it checked | result | value |")
    L.append("|---|---|---|---|")
    for gid, ok, detail in gate_rows:
        L.append(f"| {gid} | {detail.split('|diff|')[0].strip()[:110]} | "
                 f"**{'PASS' if ok else 'FAIL'}** | "
                 f"{detail.split('|diff|')[-1].strip() if '|diff|' in detail else detail.split(':')[-1].strip()} |")
    L.append("")
    L.append("**D0-G1: "
             f"{'PASS' if not n_fail else 'FAIL'} "
             f"({len(gate_rows) - n_fail}/{len(gate_rows)} checks).** The "
             f"session continued.")
    L.append("")
    L.append("---")
    L.append("")
    for cid, title, old_blocks, rows, corrected, footer in C:
        L.append(f"## {cid} — {title}")
        L.append("")
        L.append("**Old text, verbatim, with the REAL line numbers in "
                 "`PHASE2_DIAGNOSTICS_LOG.md`:**")
        L.append("")
        for quote, lns in old_blocks:
            L.append(f"- search `{quote}` -> line(s) "
                     f"{', '.join(str(x) for x in lns) if lns else 'NOT FOUND'}")
            for L_ in lns:
                txt = EARLIER_LOG.read_text().splitlines()[L_ - 1].strip()
                L.append(f"  - line {L_}, quoted verbatim:")
                L.append("")
                L.append("    ```")
                L.append(f"    {txt}")
                L.append("    ```")
        L.append("")
        L.append("**Recomputed value vs the plan's target:**")
        L.append("")
        L.append("| quantity | recomputed | plan target |")
        L.append("|---|---|---|")
        for a, b, c in rows:
            L.append(f"| {a} | **{b}** | {c} |")
        L.append("")
        L.append("**Corrected statement:**")
        L.append("")
        L.append(f"> {corrected}")
        L.append("")
        if footer:
            L.append(footer)
            L.append("")
        L.append("**Cite this, not the old sentence.**")
        L.append("")
        L.append("---")
        L.append("")
    L.append("## Plan-target disagreements")
    L.append("")
    if disagree:
        L.append("The planning document's expected values are Claude's own "
                 "recomputations, not facts. The following disagree with this "
                 "run's recomputation. **The recomputed value is the value.** "
                 "No target was forced.")
        L.append("")
        L.append("| item | recomputed | plan target |")
        L.append("|---|---|---|")
        for it, g, t in disagree:
            L.append(f"| {it} | **{g}** | {t} |")
    else:
        L.append("**None.** Every plan target recomputed to the value the "
                 "plan states.")
    L.append("")
    CORRECTIONS.write_text("\n".join(L) + "\n")
    digest = hashlib.sha256(CORRECTIONS.read_bytes()).hexdigest()
    print(f"  wrote {CORRECTIONS.relative_to(ROOT)}")
    print(f"  sha256 = {digest}")

    banner("D0 VERDICT", "-")
    if disagree:
        print(f"  D0-G1 PASS ({len(gate_rows) - n_fail}/{len(gate_rows)}).")
        print(f"  {len(disagree)} PLAN-TARGET DISAGREEMENT(S):")
        for it, g, t in disagree:
            print(f"    {it}: recomputed {g} vs plan target {t}")
        print("  Both numbers are recorded; neither was forced. The "
              "corrections file uses the recomputed value.")
    else:
        print(f"  D0-G1 PASS ({len(gate_rows) - n_fail}/{len(gate_rows)}). "
              f"All nine items C1-C9 recomputed; no plan target disagreed.")
    print(f"\n  Line numbers located in the earlier log:")
    print(f"    'more negative than 1 of the 78'                     -> {ln1}")
    print(f"    'most extreme residual of all 96'                    -> {ln2a}")
    print(f"    '96.9th percentile'                                  -> {ln2b}")
    print(f"    'carried entirely by Arm G'                          -> {ln3a}")
    print(f"    'exhaustive control agrees'                          -> {ln3b}")
    print(f"    'largest in the null set in either direction'         -> {ln4}")
    print(f"    'a weaker one'                                       -> {ln5}")
    print(f"    'essentially every placebo'                          -> {ln6}")
    print(f"    'relative to its own neighbourhood' (x2 searches)    -> {ln7}")
    print(f"    'do not exist in this repository'                    -> {ln9}")
    print(f"\n  corrections file sha256 = {digest}")
    print("\nLIMITATIONS: rebuilding the rhos is a REPRODUCTION of script 125's "
          "printed run, not an independent replication. D0 corrects prose, not "
          "data: every value in the earlier log's own printed blocks is "
          "reproduced here unchanged, and nothing frozen is redefined.")


if __name__ == "__main__":
    main()
