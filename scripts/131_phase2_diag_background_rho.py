"""Script 131 -- Phase 2 diagnostics Task D1: build and GATE the canonical
per-background rho table.  HARD GATE: D2-D8 must not run on an
unverified table.

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  This script does not compute, print, or comment on that outcome
word.  Per PHASE2_DIAGNOSTICS.md rule 9, the three words reserved for the
frozen test are not used anywhere in this script.

WHAT THIS DOES
--------------
1. Checks whether script 125's --mode phase2 run persisted a per-background
   rho table to disk.  (Finding: it did NOT -- 125 has no to_csv anywhere;
   only its stdout survives, at data/processed/phase2/analysis_run.log.)
2. Recomputes rho_b for all 96 roster backgrounds on BOTH the full frame and
   H by IMPORTING script 125 and driving its own build path.  Nothing is
   reimplemented from memory; the only transcription is 125's inline H-view
   block (main() lines 531-539), reproduced verbatim in
   scripts/lib/phase2_diag.point_rhos_H and cross-checked against 125's
   own printed log.
3. Writes data/processed/phase2_diagnostics/background_rho_table.csv
   (bg_id, arm, position, dist_222, rho_full, rho_H) and reports its sha256.
4. Runs gate D1-G1 and then INDEPENDENTLY cross-checks all 96 recomputed
   rho_full and rho_H values against the numbers script 125 actually
   printed in data/processed/phase2/analysis_run.log.

RESAMPLING UNIT
---------------
NONE.  This script performs no resampling of any kind: every quantity is a
deterministic point rho or an exact rank count.  Phase 2's own primary
analysis resamples POSITIONS within a background (script 125, PIN-9 naive
spearmanr loop); that loop is NOT invoked here.  The background-level
bootstrap used by D2/D4/D6 is likewise not invoked here.  N_BOOT/N_PERM
are therefore not read by this script and smoke-testing them is n/a; the
run is deterministic and idempotent.

PRE-REGISTERED GATE D1-G1 (HARD; failure -> print GATE FAIL and exit 1,
no loosening, no retry, no re-run at a different tolerance)
--------------------------------------------------------------------------
All targets are the values PHASE2_DIAGNOSTICS.md D1 quotes, which are in
turn the values script 125 printed in data/processed/phase2/analysis_run.log
(9 decimal places). Tolerance |diff| < 1e-9 on every numeric target.

G1.1  A222V rho, full frame = -0.088118064
G1.2  A222V rho, held-out H  = -0.090021683
G1.3  p_spec(full) = 2/79 = 0.025316456
G1.4  exactly {G_P254F} is at or below A222V on the full frame, and
      G_P254F rho_full = -0.096243863
G1.5  p_spec(H) = 4/79 = 0.050632911
G1.6  exactly {G_P254F, AV_220, AV_195} are at or below A222V on H, with
      rho_H = -0.101954441 / -0.094480281 / -0.093420822
G1.7  arm means, full frame: S=-0.065159334  V=-0.019532174  G=-0.000230296
G1.8  arm means, H:          S=-0.070181243  V=-0.022540725  G=+0.000869556
G1.9  arm medians, full:     S=-0.064728255  V=-0.023411207  G=+0.010076945
G1.10 arm medians, H:        S=-0.068991235  V=-0.022628334  G=+0.009295575
G1.11 arm ranges, full: S=[-0.093529969,-0.045641128]
                        V=[-0.084598081,+0.047573205]
                        G=[-0.096243863,+0.063116028]
G1.12 arm ranges, H:    S=[-0.090964259,-0.048929841]
                        V=[-0.094480281,+0.040588603]
                        G=[-0.101954441,+0.068247435]
G1.13 null set N: full n=78 mean=-0.009633775 median=-0.002701665
                   H    n=78 mean=-0.010535453 median=-0.006633288
G1.14 signed rank of A222V within N u {A222V}: 2/79 (full), 4/79 (H)

G1.15 CROSS-CHECK (not from the plan doc; from 125's own stdout on disk):
      max |recomputed rho_full - 125's printed rho| < 1e-9 over all 96, and
      likewise for rho_H.  This is a check that the import-driven rebuild
      is the same computation, not a coincidence of aggregates.

IF ANY G1.x FAILS: print "GATE FAIL: <which>" and exit 1.  The session
stops there; D2-D8 do not run on an unverified table.

LIMITATIONS (AGENTS 6)
----------------------
* Rebuilding 125's rhos is REPRODUCTION, NOT REPLICATION (AGENTS 6).  It
  validates that this session's inputs and code path are the same as the
  frozen run's.  It is not independent evidence for any claim.
* The H-view rhos are a verbatim transcription of 125's inline block, not a
  function import, because 125 computes them inside main().  The
  transcription is gated against 125's own printed log (G1.15), which is
  what makes it safe to rely on.
* rho_b shares one y-vector (own_e_b) across all 96 backgrounds, so the
  rho_b are mutually correlated.  A per-background table inherits that; it
  says nothing about independence and must not be read as 96 independent
  observations.  Any uncertainty in D2-D6 comes from the background-level
  bootstrap, not from treating the table as independent rows.
* This table contains no CIs.  Script 125's position-cluster bootstrap CIs
  are not recomputed here (hours of compute, and not needed for this
  session's descriptive questions).
* dist_222 is a derived convenience column computed here (|position - 222|)
  and used by D2.  It is not part of the frozen analysis.

Usage:
  venv/bin/python3 scripts/131_phase2_diag_background_rho.py
"""

import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

OUT_CSV = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
S125_LOG = ROOT / "data/processed/phase2/analysis_run.log"

# ---------------------------------------------------------------------------
# PRE-REGISTERED GATE TARGETS (see docstring).  Keys are gate ids.
# ---------------------------------------------------------------------------
G_FULL = -0.088118064
G_H = -0.090021683
G_P_FULL = 2.0 / 79.0
G_P_H = 4.0 / 79.0
G_BEATERS_FULL = {"G_P254F": -0.096243863}
G_BEATERS_H = {"G_P254F": -0.101954441,
               "AV_220": -0.094480281,
               "AV_195": -0.093420822}
G_ARM_FULL = {
    "S": dict(n=18, mean=-0.065159334, med=-0.064728255,
              lo=-0.093529969, hi=-0.045641128),
    "V": dict(n=38, mean=-0.019532174, med=-0.023411207,
              lo=-0.084598081, hi=0.047573205),
    "G": dict(n=40, mean=-0.000230296, med=0.010076945,
              lo=-0.096243863, hi=0.063116028),
}
G_ARM_H = {
    "S": dict(n=18, mean=-0.070181243, med=-0.068991235,
              lo=-0.090964259, hi=-0.048929841),
    "V": dict(n=38, mean=-0.022540725, med=-0.022628334,
              lo=-0.094480281, hi=0.040588603),
    "G": dict(n=40, mean=0.000869556, med=0.009295575,
              lo=-0.101954441, hi=0.068247435),
}
G_N_FULL = dict(n=78, mean=-0.009633775, med=-0.002701665)
G_N_H = dict(n=78, mean=-0.010535453, med=-0.006633288)
G_RANK_FULL, G_RANK_H = 2, 4
TOL = 1e-9

results = []          # (gate_id, passed, detail_string)


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, passed, detail):
    results.append((gid, bool(passed), detail))
    print(f"  [{'PASS' if passed else 'FAIL'}] {gid}: {detail}")


def near(got, want, tol=TOL):
    return abs(float(got) - float(want)) < tol


def main():
    banner("D1 -- build + gate the canonical per-background rho table "
           "(script 131)")

    # ---------------------------------------------------- step 0: on disk --
    print("\n[step 0] Does script 125's --mode phase2 run already persist a "
          "per-background rho table?")
    src = (ROOT / "scripts/125_phase2_analysis.py").read_text()
    writers = re.findall(r"to_csv|np\.save|write_text|open\(.*['\"]w",
                         src)
    print(f"  script 125 contains {len(writers)} file-writing call(s): "
          f"{writers or 'NONE'}")
    print("  -> script 125 writes NO output file; its rhos survive only in "
          "its stdout.")
    existing = sorted((ROOT / "data/processed").glob("*rho*")) + \
        sorted((ROOT / "data/processed/phase2").glob("*.csv"))
    csvs = [p for p in existing if p.suffix == ".csv"]
    looks = []
    for p in csvs:
        try:
            head = p.open("r").readline()
        except Exception:
            continue
        if re.search(r"rho", head):
            looks.append(p.name)
    print(f"  CSVs under data/processed/ with a 'rho' column in the header: "
          f"{looks or 'NONE'}")
    print(f"  data/processed/phase2_diagnostics/ exists: "
          f"{(ROOT / 'data/processed/phase2_diagnostics').exists()}")
    print("  FINDING: no per-background rho table exists as a file. "
          "Recomputing from script 125's own construction (imported).")

    # ------------------------------------- step 1: drive script 125's build
    print("\n[step 1] Driving script 125's --mode phase2 build path "
           "(imported, not reimplemented)")
    print(f"  {pdg.DELTA_DEF}")
    print(f"    score_b(v)  <- {pdg.BG_SCORE_SOURCE}")
    print(f"    esm2_score  <- {pdg.ESM2_SOURCE}")
    print(f"    join        <- {pdg.DELTA_JOIN}")
    print("  (all four lines quoted from scripts/125_phase2_analysis.py)")
    s125, A = pdg.build(verbose=True)

    print("\n[step 2] H-view rhos (125 main() lines 531-539, transcribed "
           "verbatim; gated in G1.15)")
    df, point_h, rho_a_H = pdg.rho_table(A)
    rho_a_full = A.rho_a222v

    print("\n[step 3] Canonical table")
    print(df.to_string(index=False))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, float_format="%.9f")
    digest = hashlib.sha256(OUT_CSV.read_bytes()).hexdigest()
    print(f"\n  wrote {OUT_CSV.relative_to(ROOT)}  (96 rows + header)")
    print(f"  sha256 = {digest}")

    # ------------------------------------------------------------- GATE ---
    banner("GATE D1-G1 (HARD; tolerance |diff| < 1e-9 on every target)",
           "-")

    # G1.1 / G1.2
    gate("G1.1 A222V rho full", near(rho_a_full, G_FULL),
         f"got {rho_a_full!r} vs {G_FULL} |diff|="
         f"{abs(rho_a_full - G_FULL):.3e}")
    gate("G1.2 A222V rho H", near(rho_a_H, G_H),
         f"got {rho_a_H!r} vs {G_H} |diff|={abs(rho_a_H - G_H):.3e}")

    N_ids = list(A.N_IDS)
    print(f"  null set N = V u G, n = {len(N_ids)} (125 printed "
          f"{len(N_ids)}; expect 78)")

    # G1.3 / G1.4
    rf = np.array([A.point[b] for b in N_ids])
    k_f, p_f = pdg.p_spec(N_ids, rho_a_full, rf)
    beaters_f = sorted(b for b in N_ids if A.point[b] <= rho_a_full)
    gate("G1.3 p_spec(full) == 2/79", near(p_f, G_P_FULL),
         f"got {p_f!r} = (1 + {k_f})/(1 + {len(N_ids)}) vs {G_P_FULL!r} "
         f"|diff|={abs(p_f - G_P_FULL):.3e}")
    want_f = sorted(G_BEATERS_FULL)
    gate("G1.4 full-frame beater set == {G_P254F}",
         beaters_f == want_f,
         f"got {beaters_f} vs {want_f}; "
         + "; ".join(f"{b}={A.point[b]:+.9f}" for b in beaters_f))
    for b, want in G_BEATERS_FULL.items():
        gate(f"G1.4 {b} rho_full", near(A.point[b], want),
             f"got {A.point[b]!r} vs {want} |diff|="
             f"{abs(A.point[b] - want):.3e}")

    # G1.5 / G1.6
    rh = np.array([point_h[b] for b in N_ids])
    k_h, p_h = pdg.p_spec(N_ids, rho_a_H, rh)
    beaters_h = sorted(b for b in N_ids if point_h[b] <= rho_a_H)
    gate("G1.5 p_spec(H) == 4/79", near(p_h, G_P_H),
         f"got {p_h!r} = (1 + {k_h})/(1 + {len(N_ids)}) vs {G_P_H!r} "
         f"|diff|={abs(p_h - G_P_H):.3e}")
    want_h = sorted(G_BEATERS_H)
    gate("G1.6 H-frame beater set == {G_P254F, AV_220, AV_195}",
         beaters_h == want_h,
         f"got {beaters_h} vs {want_h}; "
         + "; ".join(f"{b}={point_h[b]:+.9f}" for b in beaters_h))
    for b, want in G_BEATERS_H.items():
        gate(f"G1.6 {b} rho_H", near(point_h[b], want),
             f"got {point_h[b]!r} vs {want} |diff|="
             f"{abs(point_h[b] - want):.3e}")

    # G1.7 - G1.12: arm summaries
    def arm_stats(arm, src_rho):
        ids = getattr(A, f"{arm}_IDS")
        v = np.array([src_rho[b] for b in ids])
        return v

    for tag, tgt, src_rho in (("full", G_ARM_FULL, A.point),
                              ("H", G_ARM_H, point_h)):
        for arm in ("S", "V", "G"):
            v = arm_stats(arm, src_rho)
            t = tgt[arm]
            gate(f"G1 arm {arm} n ({tag})", len(v) == t["n"],
                 f"got {len(v)} vs {t['n']}")
            gate(f"G1 arm {arm} mean ({tag})", near(v.mean(), t["mean"]),
                 f"got {v.mean()!r} vs {t['mean']} |diff|="
                 f"{abs(v.mean() - t['mean']):.3e}")
            gate(f"G1 arm {arm} median ({tag})",
                 near(float(np.median(v)), t["med"]),
                 f"got {float(np.median(v))!r} vs {t['med']} |diff|="
                 f"{abs(float(np.median(v)) - t['med']):.3e}")
            gate(f"G1 arm {arm} range lo ({tag})", near(v.min(), t["lo"]),
                 f"got {v.min()!r} vs {t['lo']} |diff|="
                 f"{abs(v.min() - t['lo']):.3e}")
            gate(f"G1 arm {arm} range hi ({tag})", near(v.max(), t["hi"]),
                 f"got {v.max()!r} vs {t['hi']} |diff|="
                 f"{abs(v.max() - t['hi']):.3e}")
            print(f"      arm {arm} ({tag}): n={len(v)} mean={v.mean():+.9f} "
                  f"median={np.median(v):+.9f} "
                  f"range=[{v.min():+.9f}, {v.max():+.9f}]")

    # G1.13 null-set summaries
    for tag, tgt, src_rho, arr in (("full", G_N_FULL, A.point, rf),
                                   ("H", G_N_H, point_h, rh)):
        gate(f"G1.13 N n ({tag})", len(N_ids) == tgt["n"],
             f"got {len(N_ids)} vs {tgt['n']}")
        gate(f"G1.13 N mean ({tag})", near(arr.mean(), tgt["mean"]),
             f"got {arr.mean()!r} vs {tgt['mean']} |diff|="
             f"{abs(arr.mean() - tgt['mean']):.3e}")
        gate(f"G1.13 N median ({tag})", near(float(np.median(arr)),
                                              tgt["med"]),
             f"got {float(np.median(arr))!r} vs {tgt['med']} |diff|="
             f"{abs(float(np.median(arr)) - tgt['med']):.3e}")

    # G1.14 signed ranks
    rank_f = int((rf < rho_a_full).sum() + 1)
    rank_h = int((rh < rho_a_H).sum() + 1)
    gate("G1.14 A222V signed rank within N u {A222V} (full)",
         rank_f == G_RANK_FULL, f"got {rank_f}/79 vs {G_RANK_FULL}/79")
    gate("G1.14 A222V signed rank within N u {A222V} (H)",
         rank_h == G_RANK_H, f"got {rank_h}/79 vs {G_RANK_H}/79")

    # G1.15 cross-check against script 125's own printed log
    print("\n  [G1.15] independent cross-check of all 96 recomputed values "
          "against script 125's own stdout")
    log_txt = S125_LOG.read_text()
    logged_full, logged_h = {}, {}
    for line in log_txt.splitlines():
        m = re.match(r"^\s*(\S+)\s+arm=(\S)\s+rho=([-+0-9.eE]+)\s*$", line)
        if m:
            logged_full[m.group(1)] = (m.group(2), float(m.group(3)))
        m = re.match(r"^\s*(\S+)\s+arm=(\S)\s+rho_H=([-+0-9.eE]+)\s+CI=",
                     line)
        if m:
            logged_h[m.group(1)] = (m.group(2), float(m.group(3)))
    print(f"    parsed {len(logged_full)} full-frame rho lines and "
          f"{len(logged_h)} rho_H lines from {S125_LOG.relative_to(ROOT)}")
    dmax_f = dmax_h = 0.0
    worst_f = worst_h = None
    for b in A.bgs:
        if b in logged_full:
            arm_l, val = logged_full[b]
            d = abs(A.point[b] - val)
            if d > dmax_f:
                dmax_f, worst_f = d, b
            if arm_l != A.arm[b]:
                gate(f"G1.15 arm agreement for {b}", False,
                     f"125 logged arm={arm_l}, roster says {A.arm[b]}")
        if b in logged_h:
            arm_l, val = logged_h[b]
            d = abs(point_h[b] - val)
            if d > dmax_h:
                dmax_h, worst_h = d, b
    gate("G1.15 all 96 rho_full match 125's printed log", dmax_f < TOL,
         f"parsed {len(logged_full)}/96; max|diff| = {dmax_f:.3e} "
         f"(worst {worst_f})")
    gate("G1.15 all 96 rho_H match 125's printed log", dmax_h < TOL,
         f"parsed {len(logged_h)}/96; max|diff| = {dmax_h:.3e} "
         f"(worst {worst_h})")

    # --------------------------------------------------------- verdict ----
    banner("D1-G1 VERDICT", "-")
    n_fail = sum(1 for _, ok, _ in results if not ok)
    n_pass = len(results) - n_fail
    for gid, ok, detail in results:
        if not ok:
            print(f"  FAILED: {gid}: {detail}")
    print(f"  {n_pass}/{len(results)} checks PASS, {n_fail} FAIL")
    if n_fail:
        print(f"\nGATE FAIL: D1-G1 failed on {n_fail} check(s). "
              f"STOP THE ENTIRE SESSION -- D2-D8 must not run on an "
              f"unverified table.")
        sys.exit(1)
    print("  GATE PASS: D1-G1 satisfied at |diff| < 1e-9 on every target.")

    banner("D1 OUTPUT TABLE (canonical; sha256 above)", "-")
    print(df.to_string(index=False))
    banner("D1 VERBATIM VALUES USED DOWNSTREAM", "-")
    print(f"  A222V rho_full = {rho_a_full!r}")
    print(f"  A222V rho_H    = {rho_a_H!r}")
    print(f"  p_spec(full)   = {p_f!r}  ({k_f}/{len(N_ids)} at or below)")
    print(f"  p_spec(H)      = {p_h!r}  ({k_h}/{len(N_ids)} at or below)")
    print(f"  full-frame beaters: {beaters_f}")
    print(f"  H-frame beaters:    {beaters_h}")
    print(f"  table sha256  = {digest}")
    print(f"  table path    = {OUT_CSV.relative_to(ROOT)}")
    print("\nLIMITATIONS: see docstring.  Rebuilt rhos are a REPRODUCTION "
          "of script 125's printed run, not an independent replication; all "
          "96 share one y-vector and are mutually correlated; no CIs are "
          "attached to this table.")


if __name__ == "__main__":
    main()
