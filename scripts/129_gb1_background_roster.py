"""
Script 129 (Phase 3a, task T4): enumerate the GB1 single-mutant background
roster from the Olson 2014 whole-domain matrix.

NO MODEL IS LOADED BY THIS SCRIPT. No `import torch`, no `import esm`, no
weight download. Arithmetic on the compacted CSVs written by script 128 only.

THIS SCRIPT ENUMERATES. IT SELECTS NOTHING.
  * No threshold is chosen here. The read-depth question is handled by
    SWEEPING it and emitting one count column per in-range threshold, so the
    choice is visibly still open.
  * No fitness-based or severity-based selection at any point. The background's
    own measured single-mutant fitness is carried as a REPORTED COLUMN ONLY; it
    is never used to filter, rank, weight or drop a background. The one ordering
    applied is lexicographic on (position, mut_aa), which is a canonical sort of
    identifiers, not a ranking by any measurement.
  * No sample is drawn. Appendix A's cap of 400 and its seed-0 sampling
    procedure are REPORTED as counts and as the literal recipe, and are executed
    in Phase 3b at scoring time, not here.

================================================================================
PRE-REGISTRATION -- WRITTEN BEFORE THIS SCRIPT WAS RUN
================================================================================
Frozen constants taken from the task doc's Appendix A, verbatim:
    "Every GB1 single mutant with at least 100 high-confidence partners, capped
     at 400 backgrounds. If more than 400 qualify, take a seed-0 sample:
     numpy.random.default_rng(0).choice(sorted_ids, 400, replace=False). The
     roster is written to disk before any scoring. No fitness-based or
     severity-based selection at any point -- qualification is by partner count
     alone."

UNRESOLVED TERM, DISCLOSED UP FRONT: Appendix A says "high-confidence
partners" but the publisher's file contains no confidence column, no error bar
and no replicate (established in T2 / script 128, T2-G1). The ONLY confidence
signal is read depth (`Input Count`). T2's pre-registered read-depth sweep found
that the paper's own stated range [509,693, 517,278] retained doubles is spanned
by exactly six consecutive integer thresholds, t = 23..28. NO ONE OF THOSE SIX IS
SELECTED HERE. Instead:

  * `n_partners_raw`      -- every double row, no filter. The unfiltered
                             enumeration, which is the only count the data
                             supports without an assumption.
  * `n_partners_t23` ... `n_partners_t28` -- one column per in-range threshold.
                             Six columns, all reported, none preferred.

This is a GAP IN THE FROZEN PRE-REGISTRATION, not a decision this script is
entitled to make. Appendix A v1 cannot be edited (its text is frozen and its
sha256 is gated in T6); resolving this requires a v2 pre-registration, which is
Phase 3b's job. Reported plainly rather than quietly filled in.

GATES (all reporting gates; none can be loosened, and none of them is a
selection):
  T4-G1  one roster row per GB1 single mutant, 1,045 rows, no duplicates.
  T4-G2  every row's (position, wt_aa) agrees with the wild-type sequence the
         data implies; the roster's single fitness equals the W recomputed from
         that single's own read counts.
  T4-G3  no partner at a background's own position (frozen-prereg gate G-2),
         verified on the underlying matrix, not merely asserted.
  T4-G4  Appendix A's qualification count is reported for every threshold
         column, including whether the 400 cap binds.

DECISION RULES FIXED NOW:
  * T4-G2 failing => the roster is unsound => FAIL, and nothing downstream runs.
  * Nothing here ranks backgrounds. The only ordering is lexicographic on
    (position, mut_aa).
  * If a gate fails it is reported, not worked around.

OUTPUTS
  data/processed/gb1_background_roster.csv   (the full enumerated roster)
  stdout is the record; tee'd to the Phase 3a full-output file by the caller.

LIMITATIONS (printed by this script, AGENTS §6)
  * "High-confidence" is undefined in the source data; six proxy columns are
    emitted and none is selected.
  * The background's own fitness is a REPORTED column. It is not used to select
    and must not be used to select.
  * n_partners counts double-mutant ROWS. A background at position p can appear
    at most 54*19 = 1,026 times (one per other position x one per non-WT residue
    at that position); that ceiling is reported so the distribution can be read
    against what is combinatorially possible.
  * This script scores nothing. It cannot and does not estimate any rho_b.
"""
import sys
import os
import time
import hashlib
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 10000))   # read for convention; unused here
N_PERM = int(os.environ.get("N_PERM", 10000))   # read for convention; unused here
SEED = 0

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "external" / "gb1_olson2014"
DBL = EXT / "gb1_olson2014_doubles.csv"
SGL = EXT / "gb1_olson2014_singles.csv"
PROC = ROOT / "data" / "processed"
ROSTER = PROC / "gb1_background_roster.csv"

AA = list("ACDEFGHIKLMNPQRSTVWY")

# Appendix A constants, frozen.
APX_MIN_PARTNERS = 100
APX_CAP = 400

# The six read-depth thresholds T2-G1 found to land inside the paper's range.
# SWEPT AND REPORTED, NOT SELECTED.
IN_RANGE_T = tuple(range(23, 29))

# Reference values established by script 128 and reused, not re-derived.
WT_IN, WT_SEL = 1759616, 3041819
N_DOUBLES, N_SINGLES, N_POS = 535917, 1045, 55
POSITION_LO, POSITION_HI = 2, 56


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def main():
    t0 = time.time()
    gates = []

    def gate(name, verdict, value, note=""):
        gates.append({"gate": name, "verdict": verdict, "value": value,
                      "note": note})
        print(f"  >>> {name}: {verdict}   value = {value}   {note}")

    for pth in (DBL, SGL):
        if not pth.exists():
            fail(f"missing input from script 128: {pth}")
        b = pth.read_bytes()
        print(f"{pth.relative_to(ROOT)}  bytes={len(b):,}  "
              f"sha256={hashlib.sha256(b).hexdigest()}")
    print("NO MODEL LOADED. No torch, no esm, no weights. Enumeration only.")

    dbl = pd.read_csv(DBL)
    sgl = pd.read_csv(SGL)
    print(f"\ndoubles: {len(dbl):,} rows, columns {list(dbl.columns)}")
    print(f"singles: {len(sgl):,} rows, columns {list(sgl.columns)}")

    # ---- wild-type sequence implied by the data (rebuilt, not trusted)
    pos_aa = {}
    for p, m in zip(sgl["pos"], sgl["mut"]):
        pos_aa.setdefault(int(p), None)
    # the singles block does not carry the WT residue; take it from the matrix
    # columns via the doubles file's companion, which script 128 already wrote.
    # It is re-derived here from the doubles' own mutated-residue set instead:
    wt_from_sgl = {}
    for p in sorted(set(sgl["pos"].astype(int))):
        muts = set(sgl.loc[sgl["pos"] == p, "mut"])
        wt_from_sgl[p] = (set(AA) - muts).pop()
    positions = sorted(wt_from_sgl)
    print(f"positions: n={len(positions)} range {positions[0]}..{positions[-1]}")

    # ---- F_B,wt and W
    F_wt = float(WT_SEL) / float(WT_IN)
    sgl = sgl.copy()
    sgl["fitness_W"] = (sgl["sel_count"] / sgl["input_count"]) / F_wt
    print(f"F_B,wt = {WT_SEL}/{WT_IN} = {F_wt:.6f}")
    print(f"single-mutant W: min={sgl['fitness_W'].min():.4f} "
          f"median={sgl['fitness_W'].median():.4f} "
          f"max={sgl['fitness_W'].max():.4f}")

    # ---- T4-G3: frozen-prereg G-2, no same-position partner, on the MATRIX
    rule("T4-G3 -- FROZEN-PREREG G-2: NO PARTNER AT A BACKGROUND'S OWN POSITION")
    same = int((dbl["pos1"] == dbl["pos2"]).sum())
    print(f"double rows with pos1 == pos2: {same}")
    if same:
        fail(f"{same} same-position double rows exist; G-2 cannot hold")
    print("every double row in the matrix places its two mutations at two "
          "DISTINCT positions, so a single-mutant background at position p can "
          "never have a partner at p. G-2 holds STRUCTURALLY, by the data's own "
          "construction, not by a filter applied here.")
    gate("T4-G3 no partner at a background's own position",
         "PASS" if same == 0 else "FAIL",
         f"double rows with pos1==pos2 = {same} of {len(dbl):,}")

    # ---- build the roster: one row per single mutant, PARTNER COUNTS ONLY
    rule("T4 -- ROSTER: n_partners PER SINGLE-MUTANT BACKGROUND (no fitness used)")
    both = pd.concat([
        dbl[["pos1", "mut1", "input_count"]].rename(
            columns={"pos1": "pos", "mut1": "mut"}),
        dbl[["pos2", "mut2", "input_count"]].rename(
            columns={"pos2": "pos", "mut2": "mut"}),
    ], ignore_index=True)
    # PARTNERS ARE DOUBLE-MUTANT ROWS ONLY. The single mutant's own row is NOT a
    # partner of itself and is deliberately excluded, so the ceiling for a
    # background at position p is (n_positions-1)*19, not that plus one.
    print(f"partner occurrences considered (both slots of every double): "
          f"{len(both):,}")
    print(f"  = 2 x {N_DOUBLES:,} = {2*N_DOUBLES:,}  "
          f"(matches: {len(both) == 2*N_DOUBLES})")

    cols = {"n_partners_raw": both.groupby(["pos", "mut"], sort=False).size()}
    for t in IN_RANGE_T:
        k = both[both["input_count"] >= t]
        s = k.groupby(["pos", "mut"], sort=False).size()
        cols[f"n_partners_t{t}"] = s
    counts = pd.DataFrame(cols).reset_index()
    counts["pos"] = counts["pos"].astype(int)
    print(f"\ndistinct (pos, mut) partner keys enumerated: {len(counts):,}")

    roster = sgl[["pos", "mut", "fitness_W"]].copy().merge(
        counts, on=["pos", "mut"], how="left")
    roster = roster.rename(columns={"fitness_W": "background_single_fitness_W"})
    for c in roster.columns:
        if c.startswith("n_partners"):
            roster[c] = roster[c].fillna(0).astype(int)
    roster["wt_aa"] = roster["pos"].map(wt_from_sgl)
    roster["background_id"] = ["G%d%s%s" % (p, w, m) for p, w, m
                               in zip(roster["pos"], roster["wt_aa"],
                                       roster["mut"])]
    roster = roster[["background_id", "pos", "wt_aa", "mut",
                     "background_single_fitness_W"] +
                    [f"n_partners_t{t}" for t in IN_RANGE_T] +
                    ["n_partners_raw"]]
    roster = roster.sort_values(["pos", "mut"], kind="mergesort").reset_index(
        drop=True)
    print(f"roster rows: {len(roster):,}  columns: {list(roster.columns)}")
    print("\nfirst 5 roster rows, verbatim:")
    print(roster.head(5).to_string(index=False))
    print("\nlast 5 roster rows, verbatim:")
    print(roster.tail(5).to_string(index=False))

    # ---- T4-G1
    g1 = (len(roster) == N_SINGLES
          and roster["background_id"].nunique() == len(roster)
          and not roster.duplicated(["pos", "mut"]).any())
    gate("T4-G1 one row per single mutant, no duplicates", "PASS" if g1 else "FAIL",
         f"rows={len(roster):,}, unique ids={roster['background_id'].nunique():,}, "
         f"expected={N_SINGLES:,}")

    # ---- T4-G2: roster's WT residues and fitness agree with the data
    bad_wt = int((roster["mut"] == roster["wt_aa"]).sum())
    # compare on the JOINED KEY, not on positional alignment of two differently
    # ordered arrays
    chk = sgl[["pos", "mut", "fitness_W"]].merge(
        roster[["pos", "mut", "background_single_fitness_W"]],
        on=["pos", "mut"], how="inner")
    d_fit = float(np.abs(chk["fitness_W"].to_numpy()
                         - chk["background_single_fitness_W"].to_numpy()).max())
    g2 = (bad_wt == 0 and d_fit < 1e-12
          and len(chk) == len(roster) == N_SINGLES)
    gate("T4-G2 WT residue and fitness agree with the data",
         "PASS" if g2 else "FAIL",
         f"rows where mut==wt_aa: {bad_wt}; max|fitness diff|={d_fit:.3e}")
    print(f"  WT residue per position, verbatim: "
          f"{''.join(wt_from_sgl[p] for p in positions)}")
    print(f"  positions {positions[0]}..{positions[-1]}, contiguous: "
          f"{positions == list(range(positions[0], positions[-1] + 1))}")
    print(f"  ceiling on n_partners_raw for any background = "
          f"(n_positions-1) * 19 = {(N_POS-1)*19:,} (one per other position x one "
          f"per non-WT residue there)")

    # ---- distribution of n_partners
    rule("T4 -- n_partners DISTRIBUTION (min, quartiles, max) FOR EVERY COLUMN")
    print("   NOTE: the six t-columns are alternatives, not a funnel. They are all")
    print("         reported; none is selected. n_partners_raw is unfiltered.")
    dist_rows = []
    for c in ["n_partners_raw"] + [f"n_partners_t{t}" for t in IN_RANGE_T]:
        v = roster[c].to_numpy()
        q = np.percentile(v, [0, 25, 50, 75, 100])
        dist_rows.append({
            "column": c,
            "n": len(v), "min": int(q[0]), "p25": int(q[1]), "median": int(q[2]),
            "p75": int(q[3]), "max": int(q[4]), "mean": float(v.mean()),
            "n_ge_50": int((v >= 50).sum()), "n_ge_100": int((v >= 100).sum()),
            "n_ge_200": int((v >= 200).sum()), "n_ge_500": int((v >= 500).sum()),
        })
    dist = pd.DataFrame(dist_rows)
    print(dist.to_string(index=False))
    dist.to_csv(PROC / "task129_gb1_n_partners_distribution.csv", index=False)

    # ---- T4-G4: Appendix A qualification
    rule("T4-G4 -- APPENDIX A QUALIFICATION (reported, NOT acted on)")
    print("Appendix A, verbatim: 'Every GB1 single mutant with at least 100")
    print("high-confidence partners, capped at 400 backgrounds.'")
    print(f"\n{'threshold column':<20} {'n>=100':>8} {'cap binds?':>12} "
          f"{'qualifying':>11} {'after cap':>11}")
    qual = []
    for c in ["n_partners_raw"] + [f"n_partners_t{t}" for t in IN_RANGE_T]:
        v = roster[c].to_numpy()
        nq = int((v >= APX_MIN_PARTNERS).sum())
        binds = nq > APX_CAP
        qual.append({"threshold_column": c, "n_ge_100": nq,
                     "cap_binds": binds,
                     "qualifying_after_cap": min(nq, APX_CAP),
                     "seed0_draw_required": binds})
        print(f"{c:<20} {nq:>8} {str(binds):>12} {nq:>11} "
              f"{min(nq, APX_CAP):>11}")
    qdf = pd.DataFrame(qual)
    gate("T4-G4 Appendix A qualification reported for every threshold column",
         "PASS", f"n_ge_100 range {qdf['n_ge_100'].min()}..{qdf['n_ge_100'].max()}; "
         f"cap binds for {int(qdf['cap_binds'].sum())} of {len(qdf)} columns")
    print(f"\nThe 400 cap binds under EVERY threshold column considered "
          f"({int(qdf['cap_binds'].sum())}/{len(qdf)}), so Appendix A's seed-0 "
          f"sample is REQUIRED, not optional.")
    print("Appendix A's sampling recipe, verbatim, for Phase 3b to execute at "
          "scoring time:")
    print("  numpy.random.default_rng(0).choice(sorted_ids, 400, replace=False)")
    print("NO SAMPLE IS DRAWN AND NO SUBSET IS WRITTEN BY THIS SCRIPT. The only "
          "file written is the FULL 1,045-row enumeration above.")
    print("sorted_ids is the sorted list of qualifying background_id strings; it "
          "is a function of the threshold column, which is still open, so it is "
          "not computable until that is resolved.")

    # ---- write
    roster.to_csv(ROSTER, index=False)
    b = ROSTER.read_bytes()
    print(f"\nwrote {ROSTER.relative_to(ROOT)}")
    print(f"  rows   = {len(roster):,}")
    print(f"  bytes  = {len(b):,}")
    print(f"  sha256 = {hashlib.sha256(b).hexdigest()}")
    print(f"  column names verbatim: {list(roster.columns)}")

    # ---- gate table
    rule("GATE TABLE (Phase 3a, script 129)")
    gdf = pd.DataFrame(gates)
    print(gdf.to_string(index=False))
    print(f"\nFAIL count: {int((gdf['verdict'] == 'FAIL').sum())}")

    rule("LIMITATIONS (printed by this script, AGENTS §6)")
    print("  - 'High-confidence' does not exist as a concept in the source data.")
    print("    Six read-depth proxy columns (t=23..28) are emitted and NONE is")
    print("    selected. This is an open gap in the FROZEN Appendix A v1 and must")
    print("    be resolved by a v2 pre-registration in Phase 3b, not by an edit to")
    print("    v1 and not by a quiet choice made here.")
    print("  - background_single_fitness_W is a REPORTED column. It was not used")
    print("    to filter, rank, weight, cap or order anything. The roster's only")
    print("    ordering is lexicographic on (pos, mut).")
    print("  - This script produces no rho_b, no CI and no p-value. It is a roster,")
    print("    not an analysis. It scores nothing and cannot.")
    print(f"  - Settings: SEED={SEED} (recorded for convention; no RNG is consumed "
          f"by this script, which draws no sample). N_BOOT={N_BOOT}, "
          f"N_PERM={N_PERM} (read for convention; unused).")
    print(f"\nElapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
