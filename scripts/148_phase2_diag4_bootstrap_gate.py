"""Script 148 -- Phase 2 diagnostics IV, Task D18: BOOTSTRAP REPRODUCTION
GATE, AND CORRECTED CIs FOR A222V's RHO.

WHY THIS SCRIPT EXISTS (task doc, section 0, item 1)
----------------------------------------------------
Diagnostics III gated the position-cluster bootstrap only on "every cluster
once reproduces the point estimate".  That check is invariant to WHICH rows a
cluster contains, so it cannot catch a cluster-to-row mapping error.  D15's
A222V CIs are 2.8x wider than Phase 1's CI for the same statistic on
overlapping rows and sit ~0.05 off-centre, which a valid bootstrap should not
do.  D18 closes that gap with (a) a session-wide reproduction gate against
D15's own printed numbers, (b) a reproduction of Phase 1's published CI using
Phase 1's own routine, and (c) a draw-by-draw comparison of script 144's
bootstrap against a slow, obvious reference implementation.

SCOPE: descriptive.  Nothing frozen is redefined.  No decision rule changes.
NO MODEL SCORING.  No torch / esm / thermompnn / Biopython import anywhere.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
-----------------------------------------------------
STAGE 1 -- D18-G1 (HARD, SESSION-WIDE).  Every row of the D18-G1 table in
PHASE2_DIAGNOSTICS_IV.md is recomputed independently and printed BESIDE its
target (the doc's targets are Claude's recomputations, not facts; a mismatch
means the DOC is wrong and the item stops with both numbers reported):
  * 4 file sha256 (rho table, 3D table, DIAG II corrections, DIAG II/III
    corrections) -- exact string match;
  * A222V's re-derived rho, full and H -- |diff| < 1e-9 on 9-dp targets;
  * frozen p_spec and its named beaters -- k and names must match exactly,
    p within 1e-9 of the 9-dp target (the doc's "2/79" is (1+k)/(1+|N|) with
    |N| = 78, i.e. 1 beater on full; "4/79" = 3 beaters on H);
  * k_R at R = 10/20/30, both views -- exact integers;
  * S1 A222V rho (9-dp targets) -- < 1e-9; S1 gradient n=67 (9-dp) -- < 1e-9;
    S1 p_spec n=78 (6-dp) -- < 2e-6;
  * matched-deletion gradient ranges at R = 10/20/30, both views, from the
    SAME GENERATOR CALLS as script 144's control loop (fresh
    np.random.default_rng(SEED) per (view, R); each draw
    rg.choice(univ, size=k_R, replace=False)), N_DRAW=200, SEED=0 -- each
    bound < 2e-6 (6-dp targets).
  If ANY row fails: print `D18-G1 FAIL` and sys.exit(1) -- the WHOLE session
  stops.  No threshold is loosened and N is not raised (AGENTS 10).

STAGE 2 -- D18.0/D18.1, gate D18-G2 (HARD for D18).  Quote verbatim, with
file and line numbers: Phase 1's [A1] line in PHASE1_LOG.md containing
"headline row reproduced exactly", the script that printed it, the bootstrap
routine behind it (scripts/lib/stats.py position_cluster_bootstrap), how
clusters are drawn, what a cluster is, how rho is computed on a resample,
N_BOOT and the seed.  Then run PHASE 1'S OWN ROUTINE (imported, unmodified)
on A222V's unrestricted rows with n_boot=10000, seed=0 and gate:
|ci - published| < 1e-9 on both endpoints, where the published values are
read at run time from data/processed/task32_delta_esm_primary.csv, row
(stage=primary, quantity='signed, own e_b').  If N_BOOT != 10000 the numeric
gate prints SKIPPED(smoke) and is not evaluated.

STAGE 3 -- D18.2/D18.3, gate D18-G3 (HARD for D18).
  3a. Transcription fidelity: replay script 144's run loop for both views,
      in its own order (UNRESTRICTED, R=0 resolved, S1 R=0/10/20/30,
      SEQ Rs=25/50), with ONE np.random.default_rng(SEED) stream shared
      across all sixteen runs exactly as in script 144 line 505, calling the
      TRANSCRIPTION of pos_cluster_boot and of grad_boot (scripts/lib/
      phase2_diag4.py), and compare all sixteen printed CIs with the sixteen
      CI lines parsed at run time from
      docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D15_FULL_OUTPUT.txt
      (6-dp print precision -> tolerance 2e-6) and the cluster counts
      exactly.  This is rule 15's "gate the transcription against the
      original's printed output".
  3b. D18-G3: for FIVE row sets -- (i) the same unrestricted rows,
      (ii) the R = 0 resolved rows (full view), (iii) S1 R = 10, 20, 30
      (full view) -- pre-draw 200 cluster-index arrays with a fresh
      np.random.default_rng(SEED), drive (a) script 144's routine (via the
      pre-drawn variant, after 3a/3c prove that variant identical to the
      verbatim transcription for an identical stream) and (b) the slow
      reference (idx = concatenate([rows_of[p] for p in ids]);
      scipy.stats.spearmanr) with the SAME ids, and require
      max|diff| < 1e-12 over the first 200 draws on each row set.
  3c. Fidelity of the pre-drawn variant: verbatim routine with a fresh
      np.random.default_rng(SEED) over 200 draws == pre-drawn variant with
      ids from the same generator -- EXACT (max|diff| = 0).

STAGE 4 -- D18.4.  Quote the failing lines of script 144 (458-479, read at
run time), say what is wrong, and use the corrected routine written in
scripts/lib/phase2_diag4.py.  Script 144 is NOT edited.
  GATE D18-G4a: corrected routine vs the reference, same pre-drawn ids,
      max|diff| < 1e-12 on each of the five row sets (first 200 draws).
  GATE D18-G4b: corrected routine on the unrestricted rows with n_boot=10000,
      seed=0 reproduces Phase 1's published CI on BOTH endpoints to 1e-9
      (the corrected routine uses Phase 1's first-appearance cluster order
      and the same integer stream Generator.choice consumes, so this is
      expected to be an exact match; if it fails the whole number, the
      failure is printed and D18 is FAIL -- no tolerance is widened).
  GATE D18-G4c: identity -- every retained cluster once reproduces the point
      estimate to 1e-12 for all twelve D18.5 cells.
  FALLBACK BRANCH (task doc D18.4, only if nothing fails): if D15's routine
  passes G3 AND matches Phase 1 on unrestricted rows, run Phase 1's routine
  on the RESOLVED rows and report whether it, too, widens.
  If D18-G2 fails, D18 stops there (STAGE 4-5 do not run) and D19-D21
  continue, per the task doc.

STAGE 5 -- D18.5.  Recompute all twelve A222V CIs with the validated
corrected routine, N_BOOT=10000, SEED=0: S1 R = 0, 10, 20, 30 on both views
(8 cells) and the sequence sensitivities Rs = 25 and 50 on both views
(4 cells).  Per cell a FRESH np.random.default_rng(SEED) is used (pre-
registered: each cell's CI depends only on its own retained clusters).
Report point, 2.5/97.5 percentiles, median, SE (ddof=1), centre-minus-point,
width, whether the CI excludes zero, the OLD D15 CI parsed from D15's own
printed output beside it, and a flag for any |centre - point| > 0.01.

RESAMPLING UNIT: POSITION CLUSTER (whole retained target positions) for
every bootstrap in this script; the matched-deletion control has no resampling
unit inside a draw (deterministic recomputation), as script 144 states.

WORDING: the three frozen outcome words are never used as a label for any
result computed here.

Smoke first (N_BOOT=200 N_DRAW=20), then full (N_BOOT=10000 N_DRAW=200);
the full run is timed in its own output.  Usage:
  N_BOOT=10000 N_DRAW=200 SEED=0 venv/bin/python3 scripts/148_phase2_diag4_bootstrap_gate.py
"""

import hashlib
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3                    # noqa: E402
from scripts.lib import phase2_diag4 as p4                    # noqa: E402
from scripts.lib.stats import position_cluster_bootstrap      # noqa: E402

N_DRAW = int(os.environ.get("N_DRAW", "200"))
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
BOOT_FULL = (N_BOOT == 10000)
DRAW_FULL = (N_DRAW == 200)

TOL9 = 1e-9
TOL6 = 2e-6

D15_OUT = ROOT / ("docs/tasks/phase2-diagnostics-iii-mechanism/"
                  "PHASE2_DIAG3_D15_FULL_OUTPUT.txt")
P1_LOG = ROOT / "docs/tasks/phase1-corrections-diagnostics/PHASE1_LOG.md"
P1_CSV = ROOT / "data/processed/task32_delta_esm_primary.csv"
S144 = ROOT / "scripts/144_phase2_diag3_farvariants.py"
S111 = ROOT / "scripts/111_a1_b1_within_family_disattenuation.py"
S32 = ROOT / "scripts/32_delta_esm_primary.py"
S_STATS = ROOT / "scripts/lib/stats.py"

# ---------------------------------------------------------------- D18-G1 ---
# The task doc's D18-G1 table, transcribed as TARGETS.  Every row is
# recomputed by this script and printed beside its target.
SHA_TARGETS = [
    (ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv",
     "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"),
    (ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv",
     "69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de"),
    (ROOT / ("docs/tasks/phase2-diagnostics-iii-mechanism/"
             "PHASE2_DIAGNOSTICS_II_CORRECTIONS.md"),
     "8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176"),
    (ROOT / ("docs/tasks/phase2-diagnostics-iii-mechanism/"
             "PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md"),
     "c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d"),
]
T_RHO_A = {"full": -0.088118064, "H": -0.090021683}
T_P = {"full": 0.025316456, "H": 0.050632911}
T_BEAT = {"full": ["G_P254F"], "H": ["AV_195", "AV_220", "G_P254F"]}
T_KR = {"full": {10: 23, 20: 121, 30: 247}, "H": {10: 13, 20: 86, 30: 172}}
T_S1_RHO = {"full": {10: -0.079237139, 20: -0.065947891, 30: -0.027360127},
            "H": {10: -0.082101889, 20: -0.063596629, 30: -0.024367374}}
T_S1_GRAD = {"full": {10: 0.689454255, 20: 0.662097177, 30: 0.400678440},
             "H": {10: 0.686580864, 20: 0.640347202, 30: 0.241344907}}
T_S1_P = {"full": {10: 0.037975, 20: 0.037975, 30: 0.063291},
          "H": {10: 0.037975, 20: 0.050633, 30: 0.101266}}
T_MD = {"full": {10: (0.680407, 0.706900), 20: (0.663147, 0.723051),
                 30: (0.615026, 0.731210)},
        "H": {10: (0.675494, 0.702836), 20: (0.642047, 0.720172),
              30: (0.602547, 0.726413)}}

RADII = (0.0, 10.0, 20.0, 30.0)
RS_SEQ = (25, 50)
# D144's run() order, one block per view (16 CI lines in D15's output).
RUN_ORDER = ["UNRESTRICTED (no 3D filter)", "R = 0 resolved rows",
             "S1 R = 0", "S1 R = 10", "S1 R = 20", "S1 R = 30",
             "SEQ Rs = 25", "SEQ Rs = 50"]
# index within a view's block, for D18.5's "old D15 CI" column
OLD_IDX = {"S1 R = 0": 2, "S1 R = 10": 3, "S1 R = 20": 4, "S1 R = 30": 5,
           "SEQ Rs = 25": 6, "SEQ Rs = 50": 7}

t0 = time.time()
GATES = []


def banner(t, ch="="):
    p3.banner(t, ch)


def gate(gid, ok, detail):
    GATES.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}", flush=True)
    return ok


def skip(gid, why):
    print(f"  [SKIP] {gid}: {why}", flush=True)


def numcheck(gid, got, want, tol):
    d = abs(float(got) - float(want))
    return gate(gid, d < tol, f"got {got!r} vs target {want!r} "
                              f"|diff| = {d:.3e} (gate < {tol:g})")


def qline(path, a, b):
    lines = path.read_text().splitlines()
    for i in range(a, b + 1):
        print(f"  {path.relative_to(ROOT)}:{i}: {lines[i - 1]}")


def find_line(path, needle):
    for i, l in enumerate(path.read_text().splitlines(), start=1):
        if needle in l:
            return i
    raise AssertionError(f"needle not found in {path}: {needle!r}")


def keeps_for_view(vs):
    """Script 144 lines 560-572, transcribed: the eight keep masks of one
    view, in run() order."""
    POSV, resolved, d3 = vs["POSV"], vs["resolved"], vs["d3"]
    out = [np.ones(len(POSV), bool)]
    out.append(p4.keep_from_removed(POSV, resolved, []))
    for R in RADII:
        rm = POSV[resolved & (d3 <= R)]
        out.append(p4.keep_from_removed(POSV, resolved, rm))
    for Rs in RS_SEQ:
        rm = POSV[np.abs(POSV - 222) <= Rs]
        out.append(resolved & ~np.isin(POSV, rm))
    return out


def ci_stats(draws, point):
    lo, hi, v = p3.pdg.pct_ci(draws)
    med = float(np.nanmedian(draws))
    se = float(np.nanstd(draws, ddof=1))
    return dict(lo=lo, hi=hi, med=med, se=se, n=v, centre=0.5 * (lo + hi),
                width=hi - lo, c_minus_p=0.5 * (lo + hi) - point)


def main():
    banner("D18 -- BOOTSTRAP REPRODUCTION GATE + CORRECTED CIs FOR "
           "A222V's RHO  (script 148)")
    print("SCOPE: descriptive; nothing frozen is redefined; the frozen "
          "PHASE2_PREREG.md verdict is not touched.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn import anywhere "
          "in this file.")
    print(f"  N_BOOT={N_BOOT} N_DRAW={N_DRAW} SEED={SEED}   "
          f"(BOOT_FULL={BOOT_FULL}, DRAW_FULL={DRAW_FULL})")
    print("  RESAMPLING UNIT: POSITION CLUSTER for every bootstrap below "
          "(whole retained target positions).  The matched-deletion control "
          "has no resampling unit inside a draw.")

    # ======================================================== D18-G1 ======
    banner("D18-G1 (HARD, SESSION-WIDE) -- reproduce Diagnostics III's "
           "machinery before anything new", "-")
    print("  Every row: MY recomputed value beside the doc's target.  A "
          "mismatch means the DOC is wrong; the item stops and both numbers "
          "are reported.  Any FAIL here stops the whole session.")

    print("\n  --- sha256 rows ---")
    for path, want in SHA_TARGETS:
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        gate(f"D18-G1 sha256 {path.name}", got == want, got)

    print("\n  --- building the shared state (script 125 construction via "
          "phase2_diag3.build) ---")
    tb = time.time()
    st = p3.build(verbose=False)
    print(f"  build() elapsed {time.time() - tb:.1f}s")
    bgs, N_ids, resN = st["bgs"], st["N_ids"], st["resN"]
    df3 = st["df3"]
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]
    print(f"  bgs = {len(bgs)}, N_ids = {len(N_ids)}, resN = {len(resN)}, "
          f"res96 = {len(res96)}")
    vs = p4.build_view_state(st)

    print("\n  --- A222V rho (re-derived) ---")
    for view in p3.VIEWS:
        got = vs[view]["A"].rho(np.ones(len(vs[view]["POSV"]), bool))
        numcheck(f"D18-G1 A222V rho re-derived ({view})", got, T_RHO_A[view],
                 TOL9)

    print("\n  --- frozen p_spec and beaters ---")
    for view in p3.VIEWS:
        rhos = np.array([st["RHO"][view][b] for b in N_ids], float)
        thr = st["RHO_A"][view]
        k = int((rhos <= thr).sum())
        p = (1 + k) / (1 + len(N_ids))
        aob = sorted(b for b in N_ids if st["RHO"][view][b] <= thr)
        ok = gate(f"D18-G1 frozen p_spec k/n ({view})",
                  p == (1 + k) / 79 and len(N_ids) == 78,
                  f"k = {k}, n = {len(N_ids)}, p = (1+k)/(1+n) = "
                  f"{(1 + k) / (1 + len(N_ids)):.9f}  "
                  f"[the doc writes this as {1 + k}/79]")
        numcheck(f"D18-G1 frozen p_spec value ({view})", p, T_P[view], TOL9)
        gate(f"D18-G1 frozen beaters ({view})",
             aob == T_BEAT[view], f"{aob} vs target {T_BEAT[view]}")

    print("\n  --- k_R (positions removed from the resolved universe) ---")
    for view in p3.VIEWS:
        # QUOTED SOURCE -- scripts/144_phase2_diag3_farvariants.py line 388:
        #     u = geo[view]["d3"][geo[view]["univ"]]
        #     k = int((u <= R).sum())            (line 397)
        u = vs[view]["d3"][vs[view]["univ"]]     # d3_222 over RESOLVED pos
        for R in (10, 20, 30):
            k = int((u <= R).sum())
            gate(f"D18-G1 k_R ({view}, R={R})", k == T_KR[view][R],
                 f"got {k} vs target {T_KR[view][R]}")

    print("\n  --- S1 statistics (R = 10/20/30, both views) ---")
    s1 = {}
    for view in p3.VIEWS:
        POSV, resolved, d3 = vs[view]["POSV"], vs[view]["resolved"], vs[view]["d3"]
        for R in (10, 20, 30):
            rm = POSV[resolved & (d3 <= R)]
            keep = p4.keep_from_removed(POSV, resolved, rm)
            s = p4.stats(vs[view], bgs, N_ids, resN, res96, df3, keep)
            s1[(view, R)] = s
            numcheck(f"D18-G1 S1 A222V rho ({view}, R={R})", s["rho_a"],
                     T_S1_RHO[view][R], TOL9)
            numcheck(f"D18-G1 S1 gradient n=67 ({view}, R={R})",
                     s["grad_n67"], T_S1_GRAD[view][R], TOL9)
            numcheck(f"D18-G1 S1 p_spec n=78 ({view}, R={R})", s["p_n78"],
                     T_S1_P[view][R], TOL6)
            print(f"        [{view}, R={R}] at or below (n=78): "
                  f"{s['aob_n78']}")

    print("\n  --- matched-deletion gradient ranges (same generator calls "
          "as script 144's control loop) ---")
    if not DRAW_FULL:
        skip("D18-G1 matched-deletion ranges",
             f"N_DRAW={N_DRAW}, not 200; ranges are only deterministic and "
             f"comparable at N_DRAW=200 (smoke run)")
        md = {}
    else:
        md = {}
        for view in p3.VIEWS:
            POSV = vs[view]["POSV"]
            resolved, d3, univ = (vs[view]["resolved"], vs[view]["d3"],
                                  vs[view]["univ_pos"])
            for R in (10, 20, 30):
                rm = sorted(POSV[resolved & (d3 <= R)].tolist())
                k_R = len(rm)
                acc = {kk: np.empty(N_DRAW, float)
                       for kk in ("rho_a", "grad_n67", "grad_n85", "p_n78",
                                  "p_n67", "k_n78")}
                rg = np.random.default_rng(SEED)
                for i in range(N_DRAW):
                    drop = rg.choice(univ, size=k_R, replace=False) if k_R \
                        else np.array([], dtype=univ.dtype)
                    s = p4.stats(vs[view], bgs, N_ids, resN, res96, df3,
                                 p4.keep_from_removed(POSV, resolved, drop))
                    for kk in acc:
                        acc[kk][i] = float(s[kk])
                md[(view, R)] = acc
                lo, hi = np.percentile(acc["grad_n67"], [2.5, 97.5])
                tw = T_MD[view][R]
                gate(f"D18-G1 matched-deletion gradient range ({view}, "
                     f"R={R})",
                     abs(lo - tw[0]) < TOL6 and abs(hi - tw[1]) < TOL6,
                     f"got [{lo:+.9f}, {hi:+.9f}] vs target "
                     f"[{tw[0]:+.6f}, {tw[1]:+.6f}] "
                     f"|diff| = {abs(lo - tw[0]):.3e} / "
                     f"{abs(hi - tw[1]):.3e} (gate < {TOL6:g})")

    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    print(f"\n  D18-G1 SUMMARY: {len(GATES) - n_fail}/{len(GATES)} checks "
          f"PASS, {n_fail} FAIL")
    if n_fail:
        print("\n*** D18-G1 FAIL -- THE WHOLE SESSION STOPS.  No threshold "
              "was loosened and N was not raised. ***")
        sys.exit(1)
    print("  GATE PASS: D18-G1 satisfied.  D15's machinery reproduces, so "
          "the deletion routine may be used for new statistics (D19-D21).")

    # ======================================================== D18.0 =======
    banner("D18.0 -- what did Phase 1 do?  (verbatim quotes, file:line)", "-")
    i = find_line(P1_LOG, "headline row reproduced exactly")
    print(f"  PHASE1_LOG.md line {i} (section [A1]), verbatim:")
    qline(P1_LOG, i, i)
    j = find_line(S111, "G2 PASS: headline row reproduced exactly")
    print(f"\n  The script that printed it is {S111.name} (print spans "
          f"lines {j}-{j + 1}); the CI it reads comes from "
          f"{P1_CSV.name}:")
    qline(S111, j, j + 1)
    pri = pd.read_csv(P1_CSV)
    row = pri[(pri["stage"] == "primary")
              & (pri["quantity"] == "signed, own e_b")].iloc[0]
    pub_lo, pub_hi = float(row["ci_lo"]), float(row["ci_hi"])
    pub_pt = float(row["value"])
    print(f"  {P1_CSV.relative_to(ROOT)}, row (primary,'signed, own e_b'): "
          f"value = {pub_pt!r}, ci_lo = {pub_lo!r}, ci_hi = {pub_hi!r}, "
          f"n = {int(row['n'])}")
    print("\n  The bootstrap behind it -- scripts/lib/stats.py lines 34-56 "
          "(what a cluster is; how clusters are drawn; how rho is computed "
          "on a resample):")
    qline(S_STATS, 34, 56)
    print("\n  N_BOOT and the seed -- scripts/32_delta_esm_primary.py lines "
          "48-49 and the call at 101-102:")
    qline(S32, 48, 49)
    qline(S32, 101, 102)
    print("\n  In words: a CLUSTER is one residue position (all "
          "substitutions sharing it); each draw samples len(clusters) "
          "cluster LABELS with replacement via rng.choice(..., replace=True)"
          " from a np.random.default_rng(0) stream; the drawn clusters' row "
          "indices are CONCATENATED (every row of every sampled cluster, "
          "repeats included) and rho is recomputed on that resampled row set "
          "as Spearman (ranks + Pearson, _spearman, line 13-15); N_BOOT = "
          "10000, seed = 0.")

    # ======================================================== D18.1 =======
    banner("D18.1 -- reproduce Phase 1's CI with Phase 1's OWN routine "
           "(gate D18-G2)", "-")
    df1 = st["A"].a222v_rows
    print(f"  rows: {len(df1)}, positions: {df1.position.nunique()}, "
          f"columns {list(df1.columns)}")
    print(f"  calling scripts/lib/stats.py position_cluster_bootstrap(df, "
          f"'position', 'delta', 'own_e_b', n_boot={N_BOOT}, seed={SEED}) "
          f"-- imported, unmodified")
    tr = time.time()
    r1 = position_cluster_bootstrap(df1, "position", "delta", "own_e_b",
                                    n_boot=N_BOOT, seed=SEED)
    print(f"  elapsed {time.time() - tr:.1f}s")
    print(f"  Phase 1 routine: observed = {r1['observed_rho']!r}, "
          f"CI = [{r1['ci_lo']!r}, {r1['ci_hi']!r}], median n/a, "
          f"n_rows = {r1['n_rows']}, n_clusters = {r1['n_clusters']}, "
          f"p_boot = {r1['p_boot']}")
    print(f"  published CI (task32 CSV)          = [{pub_lo!r}, "
          f"{pub_hi!r}], point = {pub_pt!r}")
    if BOOT_FULL:
        d1_ok = gate("D18-G2 Phase 1 routine reproduces the published CI "
                     "(1e-9)",
                     abs(r1["ci_lo"] - pub_lo) < 1e-9
                     and abs(r1["ci_hi"] - pub_hi) < 1e-9
                     and abs(r1["observed_rho"] - pub_pt) < 1e-9,
                     f"|diff| lo = {abs(r1['ci_lo'] - pub_lo):.3e}, "
                     f"hi = {abs(r1['ci_hi'] - pub_hi):.3e}, point = "
                     f"{abs(r1['observed_rho'] - pub_pt):.3e} "
                     f"(gate < 1e-9)")
        if not d1_ok:
            print("\n*** D18-G2 FAIL -- STOP D18.  D19-D21 do not use this "
                  "bootstrap and continue. ***")
            print_gate_table()
            sys.exit(2)
    else:
        d1_ok = None
        skip("D18-G2", f"N_BOOT={N_BOOT} != 10000 (smoke run)")

    # ======================================================== D18.2 =======
    banner("D18.2 -- script 144's pos_cluster_boot on the same rows "
           "(transcribed; its rng stream is its own)", "-")
    POSVf = vs["full"]["POSV"]
    resolved_f, d3_f = vs["full"]["resolved"], vs["full"]["d3"]
    rowsets = [
        ("(i) UNRESTRICTED (same rows as Phase 1)", "full",
         np.ones(len(POSVf), bool)),
        ("(ii) R = 0 resolved rows (full)", "full",
         p4.keep_from_removed(POSVf, resolved_f, [])),
    ]
    for R in (10, 20, 30):
        rm = POSVf[resolved_f & (d3_f <= R)]
        rowsets.append((f"(iii) S1 R = {R} (full)", "full",
                        p4.keep_from_removed(POSVf, resolved_f, rm)))
    print(f"  {'row set':32s} {'point':>12s} {'p2.5':>10s} {'p50':>10s} "
          f"{'p97.5':>10s} {'SE':>10s} {'centre-pt':>10s} {'width':>10s} "
          f"{'nk':>5s} {'rows/draw':>9s}")
    d182 = {}
    for name, view, keep in rowsets:
        point = vs[view]["A"].rho(keep)
        draws = p4.pos_cluster_boot_144(vs[view]["A"], vs[view]["POSV"],
                                        keep, N_BOOT,
                                        np.random.default_rng(SEED))
        cs = ci_stats(draws, point)
        d182[name] = cs
        nk = int(keep.sum())
        print(f"  {name:32s} {point:+12.9f} {cs['lo']:+10.6f} "
              f"{cs['med']:+10.6f} {cs['hi']:+10.6f} {cs['se']:10.6f} "
              f"{cs['c_minus_p']:+10.6f} {cs['width']:10.6f} {nk:5d} "
              f"{nk:9d}")
    print("  ('rows/draw' is what script 144's routine actually evaluates: "
          "exactly nk rows per draw (one per sampled cluster occurrence), "
          "not the sampled clusters' full row complement.)")
    c1 = d182["(i) UNRESTRICTED (same rows as Phase 1)"]
    print(f"  D18.1 (Phase 1) on the SAME rows:  point {pub_pt:+.9f}, CI "
          f"[{pub_lo:+.6f}, {pub_hi:+.6f}], width {pub_hi - pub_lo:.6f}")
    print(f"  script 144 on the SAME rows:       point "
          f"{vs['full']['A'].rho(np.ones(len(POSVf), bool)):+.9f}, CI "
          f"[{c1['lo']:+.6f}, {c1['hi']:+.6f}], width {c1['width']:.6f};  "
          f"width ratio = {c1['width'] / (pub_hi - pub_lo):.2f}x, "
          f"centre - point = {c1['c_minus_p']:+.6f}")

    # ======================================================== D18.3 =======
    banner("D18.3 -- transcription fidelity vs D15's printed output, then "
           "gate D18-G3 (draw-by-draw reference)", "-")
    # ---- 3a: replay script 144's run loop and its ONE shared rng stream --
    txt = D15_OUT.read_text()
    pat = re.compile(r"POSITION-CLUSTER bootstrap 95% CI = \[([-+0-9.]+), "
                     r"([-+0-9.]+)\] \((\d+) usable draws, clusters = (\d+) "
                     r"retained")
    parsed = [(float(a), float(b), int(c), int(d))
              for a, b, c, d in pat.findall(txt)]
    print(f"  parsed {len(parsed)} CI lines from D15's full output "
          f"({D15_OUT.name}); expected 16")
    if BOOT_FULL and len(parsed) == 16:
        rng = np.random.default_rng(SEED)     # ONE stream, script 144 line 505
        worst = 0.0
        ridx = 0
        for view in p3.VIEWS:
            keeps = keeps_for_view(vs[view])
            sa = vs[view]["A"]
            for name, keep in zip(RUN_ORDER, keeps):
                draws = p4.pos_cluster_boot_144(sa, vs[view]["POSV"], keep,
                                                N_BOOT, rng)
                lo, hi, _ = p3.pdg.pct_ci(draws)
                s = p4.stats(vs[view], bgs, N_ids, resN, res96, df3, keep)
                p4.grad_boot(s["rho_b"], resN, df3, N_BOOT, rng)
                p4.grad_boot(s["rho_b"], res96, df3, N_BOOT, rng)
                plo, phi, pn, pcl = parsed[ridx]
                dmax = max(abs(lo - plo), abs(hi - phi))
                worst = max(worst, dmax)
                nk = int(keep.sum())
                if dmax >= TOL6 or nk != pcl:
                    gate(f"D18 transcription CI [{view} / {name}]", False,
                         f"got [{lo:+.6f}, {hi:+.6f}] clusters {nk} vs "
                         f"D15 [{plo:+.6f}, {phi:+.6f}] clusters {pcl}")
                ridx += 1
        gate("D18 transcription of pos_cluster_boot vs all 16 CIs in D15's "
             "printed output", worst < TOL6,
             f"max|diff| over 16 CIs = {worst:.3e} (gate < {TOL6:g}); "
             f"cluster counts all matched")
    else:
        skip("D18 transcription vs D15 printed CIs",
             f"N_BOOT={N_BOOT} (smoke) or parsed {len(parsed)} CI lines")

    # ---- 3c: pre-drawn variant == verbatim routine for the same stream ---
    print("\n  --- 3c: pre-drawn variant vs the verbatim transcription "
          "(same generator) ---")
    ids_store = {}
    for name, view, keep in rowsets:
        sa, POSV = vs[view]["A"], vs[view]["POSV"]
        nk = int(keep.sum())
        rng = np.random.default_rng(SEED)
        ids = np.empty((200, nk), dtype=np.int64)
        for i in range(200):
            ids[i] = rng.integers(0, nk, nk)
        verbatim = p4.pos_cluster_boot_144(sa, POSV, keep, 200,
                                           np.random.default_rng(SEED))
        pre = p4.pos_cluster_boot_144_preadrawn(sa, POSV, keep, ids)
        d = float(np.max(np.abs(verbatim - pre)))
        gate(f"D18 pre-drawn variant == verbatim ({name})", d == 0.0,
             f"max|diff| over 200 draws = {d:.3e} (required EXACTLY 0)")
        ids_store[name] = (ids, keep, view)

    # ---- 3b: gate D18-G3, reference vs the routine under test ------------
    print("\n  --- D18-G3: script 144's routine vs the slow reference, "
          "SAME pre-drawn positions, 200 draws ---")
    g3_fail = []
    for name, view, keep in rowsets:
        ids, _, _ = ids_store[name]
        sa, POSV = vs[view]["A"], vs[view]["POSV"]
        asc_labels = POSV[keep]              # 144's index space (ascending)
        ref = p4.reference_boot(sa, asc_labels, ids)
        under = p4.pos_cluster_boot_144_preadrawn(sa, POSV, keep, ids)
        d = float(np.max(np.abs(ref - under)))
        ok = d < 1e-12
        if not ok:
            g3_fail.append(name)
        # diagnosis: rows per draw in each implementation
        n_ref = int(sum(len(np.flatnonzero(sa.pos == p))
                        for p in asc_labels[ids[0]]))
        _, sizes, _, _ = p4.cluster_index(POSV, sa.code, keep)
        nk = int(keep.sum())
        gate(f"D18-G3 first 200 draws agree to 1e-12 ({name})", ok,
             f"max|diff| = {d:.3e}; draw 0 uses {n_ref} rows in the "
             f"reference vs exactly {nk} rows in script 144's routine "
             f"(retained clusters = {nk}, retained rows = "
             f"{int(keep[sa.code].sum())})")
        if not ok:
            ref_idx = np.concatenate([np.flatnonzero(sa.pos == p)
                                      for p in asc_labels[ids[0][:5]]])
            print(f"        first 5 clusters of draw 0 -> labels "
                  f"{list(map(int, asc_labels[ids[0][:5]]))}")
            print(f"        reference idx[:10]  = "
                  f"{ref_idx[:10].tolist()}")
            print(f"        144 idx[:10]       = see line 477 of the "
                  f"transcription (base + occurrence offset)")
    print(f"  D18-G3 result: {'all five row sets agree' if not g3_fail else 'DISAGREE on: ' + ', '.join(g3_fail)}")

    # ======================================================== D18.4 =======
    banner("D18.4 -- the defect, the corrected routine, and its gates", "-")
    if not g3_fail:
        print("  NOTHING FAILED: script 144's routine matches the reference "
              "on all five row sets and matches Phase 1 on the unrestricted "
              "rows.  Per the task doc's fallback branch, Phase 1's routine "
              "is now run on the RESOLVED rows to see whether it, too, "
              "widens:")
        keep_r0 = p4.keep_from_removed(POSVf, resolved_f, [])
        dfr = vs["full"]["A"]
        sub = pd.DataFrame(dict(position=dfr.pos[keep_r0[dfr.code]],
                                delta=dfr.delta[keep_r0[dfr.code]],
                                own_e_b=dfr.y[keep_r0[dfr.code]]))
        rr = position_cluster_bootstrap(sub, "position", "delta", "own_e_b",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"  Phase 1 routine on RESOLVED rows: point "
              f"{rr['observed_rho']!r}, CI [{rr['ci_lo']!r}, "
              f"{rr['ci_hi']!r}], width "
              f"{rr['ci_hi'] - rr['ci_lo']:.6f} (vs unrestricted width "
              f"{pub_hi - pub_lo:.6f}), n_rows {rr['n_rows']}, n_clusters "
              f"{rr['n_clusters']}")
    else:
        print("  D18-G3 FAILED -- script 144's routine does not reproduce "
              "the reference.  QUOTED SOURCE, scripts/144_phase2_diag3_"
              "farvariants.py lines 458-479 (the routine under test):")
        qline(S144, 458, 479)
        print("""
  WHAT IS WRONG (line by line):
    line 470  cnt[s] = how often cluster s was drawn this draw.
    line 475  j = np.arange(m) - np.repeat(cum[:-1], cnt) is the OCCURRENCE
              index within a draw slot (0,1,2,... for slot s), NOT the row
              offset within that cluster's rows.
    line 477  idx = np.repeat(kept_base, cnt)[rep] + j therefore addresses
              kept_base[s'] + occurrence-index, so a cluster drawn cnt[s]
              times contributes rows base+0 .. base+cnt[s]-1 -- ONE row per
              occurrence -- instead of ALL of the cluster's
              sizes[s] rows.  Every draw evaluates exactly m = nk rows
              (~595) rather than the sampled clusters' full complement
              (~9,740 on the R = 0 resolved set), and the rows it does take
              are the FIRST rows of each cluster, not the whole cluster.
              The point-estimate identity gate cannot see this: it only ever
              concatenates every cluster ONCE (line 486), a path that never
              uses cnt or j.
  CONSEQUENCE MEASURED ABOVE: a CI ~2.8x wider than Phase 1's and a centre
  displaced from the point estimate, because the resample is a different
  (one-row-per-cluster, order-biased) statistic.
  FIX: scripts/lib/phase2_diag4.py pos_cluster_boot_corrected -- each drawn
  cluster contributes ALL of its rows, concatenated in draw order (the
  construction scripts/lib/stats.py lines 51-53 performs).  Script 144 is
  NOT edited.""")
        # gate D18-G4a: corrected vs reference, same pre-drawn positions
        print("  --- D18-G4a: corrected routine vs the reference, same "
              "pre-drawn positions (200 draws) ---")
        for name, view, keep in rowsets:
            ids, _, _ = ids_store[name]
            sa, POSV = vs[view]["A"], vs[view]["POSV"]
            parts = p4.retained_parts(sa, POSV, keep)
            fa_lookup = {int(p): i for i, p in enumerate(parts["labels"])}
            asc_labels = POSV[keep]
            ids_fa = np.vectorize(lambda s: fa_lookup[int(asc_labels[s])])(
                ids)
            corr = p4.pos_cluster_boot_corrected_from_ids(parts, ids_fa)
            ref = p4.reference_boot(sa, parts["labels"], ids_fa)
            d = float(np.max(np.abs(corr - ref)))
            gate(f"D18-G4a corrected vs reference ({name})", d < 1e-12,
                 f"max|diff| over 200 draws = {d:.3e} (gate < 1e-12); "
                 f"{parts['n_rows']} retained rows over "
                 f"{len(parts['labels'])} clusters")
        # gate D18-G4b: corrected vs Phase 1's published CI
        print("  --- D18-G4b: corrected routine vs Phase 1's published CI "
              "on the unrestricted rows ---")
        if BOOT_FULL:
            keep_all = np.ones(len(vs["full"]["POSV"]), bool)
            parts = p4.retained_parts(vs["full"]["A"], vs["full"]["POSV"],
                                      keep_all)
            draws = p4.pos_cluster_boot_corrected(vs["full"]["A"],
                                                  vs["full"]["POSV"],
                                                  keep_all, N_BOOT,
                                                  np.random.default_rng(SEED))
            lo, hi, _ = p3.pdg.pct_ci(draws)
            gate("D18-G4b corrected routine reproduces Phase 1's published "
                 "CI (1e-9)",
                 abs(lo - pub_lo) < 1e-9 and abs(hi - pub_hi) < 1e-9,
                 f"corrected CI [{lo!r}, {hi!r}] vs published "
                 f"[{pub_lo!r}, {pub_hi!r}]; |diff| "
                 f"{abs(lo - pub_lo):.3e} / {abs(hi - pub_hi):.3e} "
                 f"(gate < 1e-9)")
            print(f"  (cluster order: first appearance in row order, "
                  f"Phase 1's own convention -- scripts/lib/stats.py lines "
                  f"34-36; draw stream: rng.integers(0, nk, nk), the same "
                  f"stream Generator.choice consumes; verified in this "
                  f"run by G4b itself.)")
        else:
            skip("D18-G4b", f"N_BOOT={N_BOOT} != 10000 (smoke run)")

    # ======================================================== D18.5 =======
    banner("D18.5 -- the twelve corrected CIs (N_BOOT=10000, SEED=0, fresh "
           "rng per cell)", "-")
    print(f"  {'view':>5s} {'cell':12s} {'point':>12s} {'CI lo':>10s} "
          f"{'CI hi':>10s} {'median':>10s} {'SE':>9s} {'ctr-pt':>9s} "
          f"{'width':>9s} {'excl0':>6s} {'nk':>4s} {'old D15 CI':>24s} "
          f"{'old w':>8s}")
    twelve = []
    for view in p3.VIEWS:
        POSV, resolved, d3 = (vs[view]["POSV"], vs[view]["resolved"],
                              vs[view]["d3"])
        sa = vs[view]["A"]
        keeps = {"S1 R = 0": p4.keep_from_removed(POSV, resolved, []),
                 "S1 R = 10": p4.keep_from_removed(
                     POSV, resolved, POSV[resolved & (d3 <= 10)]),
                 "S1 R = 20": p4.keep_from_removed(
                     POSV, resolved, POSV[resolved & (d3 <= 20)]),
                 "S1 R = 30": p4.keep_from_removed(
                     POSV, resolved, POSV[resolved & (d3 <= 30)])}
        for Rs in RS_SEQ:
            rm = POSV[np.abs(POSV - 222) <= Rs]
            keeps[f"SEQ Rs = {Rs}"] = resolved & ~np.isin(POSV, rm)
        v_off = 0 if view == "full" else 8
        for cell in ["S1 R = 0", "S1 R = 10", "S1 R = 20", "S1 R = 30",
                     "SEQ Rs = 25", "SEQ Rs = 50"]:
            keep = keeps[cell]
            point = sa.rho(keep)
            draws = p4.pos_cluster_boot_corrected(
                sa, POSV, keep, N_BOOT, np.random.default_rng(SEED))
            cs = ci_stats(draws, point)
            nk = int(keep.sum())
            # identity gate: every retained cluster once == point estimate
            parts = p4.retained_parts(sa, POSV, keep)
            one = p4.pos_cluster_boot_corrected_from_ids(
                parts, np.arange(len(parts["labels"]))[None, :])
            ident = abs(float(one[0]) - point)
            plo, phi, pn, pcl = parsed[v_off + OLD_IDX[cell]]
            excl = bool(cs["lo"] > 0 or cs["hi"] < 0)
            flag = "  <-- |centre - point| > 0.01" if \
                abs(cs["c_minus_p"]) > 0.01 else ""
            print(f"  {view:>5s} {cell:12s} {point:+12.9f} "
                  f"{cs['lo']:+10.6f} {cs['hi']:+10.6f} {cs['med']:+10.6f} "
                  f"{cs['se']:9.6f} {cs['c_minus_p']:+9.6f} "
                  f"{cs['width']:9.6f} {str(excl):>6s} {nk:4d} "
                  f"[{plo:+.6f}, {phi:+.6f}] {phi - plo:8.6f}{flag}")
            gate(f"D18.5 identity, every cluster once ({view} / {cell})",
                 ident < 1e-12, f"|diff| = {ident:.3e} (gate < 1e-12); "
                                f"old D15 clusters {pcl} vs now {nk}"
                                + ("" if pcl == nk else "  <-- DIFFER"))
            twelve.append(dict(view=view, cell=cell, point=point, cs=cs,
                               old=(plo, phi), excl=excl))
    print("\n  widths and zero-exclusion, corrected vs old:")
    n_excl_new = sum(1 for t in twelve if t["excl"])
    n_excl_old = sum(1 for t in twelve
                     if t["old"][0] > 0 or t["old"][1] < 0)
    print(f"  corrected CIs excluding zero: {n_excl_new}/12;  old D15 CIs "
          f"excluding zero: {n_excl_old}/12")
    for t in twelve:
        print(f"    {t['view']:>5s} {t['cell']:12s} corrected "
              f"[{t['cs']['lo']:+.6f}, {t['cs']['hi']:+.6f}] "
              f"{'EXCLUDES' if t['excl'] else 'includes'} zero;  old "
              f"[{t['old'][0]:+.6f}, {t['old'][1]:+.6f}] "
              f"{'excludes' if (t['old'][0] > 0 or t['old'][1] < 0) else 'includes'} "
              f"zero;  width {t['cs']['width']:.6f} vs "
              f"{t['old'][1] - t['old'][0]:.6f} "
              f"({(t['cs']['width']) / (t['old'][1] - t['old'][0]):.2f}x)")

    print_gate_table()
    print(f"\nElapsed {time.time() - t0:.1f}s")


def print_gate_table():
    banner("D18 GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _ in GATES if not ok)
    for gid, ok, detail in GATES:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print(f"\n  D18 gates: {len(GATES) - n_fail}/{len(GATES)} PASS, "
          f"{n_fail} FAIL")


if __name__ == "__main__":
    main()
