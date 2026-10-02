#!/usr/bin/env python3
"""PHASE 3a / TASK A4a + A4b -- GB1 input verification (gate G-5) and the
frozen roster draw, before any GB1 score exists.

IMPLEMENTS
----------
PHASE3_OVERNIGHT.md Task A4 (A4a inputs, A4b roster) exactly as
prereg/GB1_REGIME_PREREG_v2.md (76 lines, sha256 b3c82d589afc2889f60ad8626
dcb24d0496f77303d0696b52db700129fd1357e) states them:
  - A4a: verify sha256 of the three data files and the Phase 3a roster;
    build the ASSAYED sequence (project's 2GB1 constant with position 2 = Q,
    the documented template change T228Q) and the PROJECT sequence (T at
    position 2); confirm they differ at exactly position 2; gate G-5 --
    "the sequence used for scoring (assayed) matches the sequence the
    fitness data implies at every position 2..56".
  - A4b: draw 400 backgrounds per frozen block A4
    (default_rng(0).choice(sorted_ids, 400, replace=False), sorted_ids sorted
    lexicographically by (position, mutant)), write
    data/processed/phase3/gb1/roster_v2.csv and its sha256 BEFORE any
    scoring, record the first 20 of the draw order as the two-sequence
    subset, report n_partners at thresholds 23, 25 (primary), 28 and
    unfiltered, and confirm all 400 clear the 100-partner floor (frozen A1).

NO MODEL IS LOADED. No torch, no esm, no weights. Enumeration only
(AGENTS: torch/esm only in scoring scripts and G-1'/timing smokes).

INPUTS AND TARGETS (recomputed independently here and printed beside every
target; a mismatch is a STOP, never a rewrite of the target):
  data/external/gb1_olson2014/gb1_olson2014_doubles.csv
      target sha256 89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769
      target rows   535,917 (PHASE3_OVERNIGHT A4a)
  data/external/gb1_olson2014/gb1_olson2014_singles.csv
      target sha256 0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3
      target rows   1,045
  data/external/GB1_fitness_landscape.txt
      target sha256 7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2
  data/processed/gb1_background_roster.csv
      The planning doc names this file WITHOUT a hash. The target used here
      is the sha256 recorded when Phase 3a wrote it (PHASE3A_LOG.md lines 580
      and 1014): ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac9230e79aae4.
      This script also requires that string to appear in PHASE3A_LOG.md, so
      the provenance of the target is in this script's own output (disclosed
      as a choice made here, not a hash supplied by the frozen block).

PRE-REGISTERED DECISIONS (fixed in this docstring before the first run):
  R1  "sorted lexicographically by (position, mutant)" (frozen A4) is read as
      a lexicographic ordering of the sort-key TUPLE (position, mutant) with
      position its integer value (2..56 ascending, mutants alphabetical
      within position) -- i.e. the roster file's own script-129 order
      (sorted_values by ["pos", "mut"], script 129 line 233). The alternative
      reading (pure string sort of the background_id, which would place
      "G10.." before "G2..") would draw a different but equally
      fitness-blind subsample; it is NOT used. Rationale: the frozen text
      names the key as the pair (position, mutant), and positions are
      integers in the data. Printed at run time: first/last sorted ids, so
      the order used is unambiguous in the record.
  R2  The draw is the literal frozen call
      numpy.random.default_rng(0).choice(sorted_ids, 400, replace=False)
      on the list of background_id strings; roster order = draw order.
      Reproduced twice inside the run and compared (G-A4b-1).
  R3  n_partners per background: the Phase 3a roster columns are RECOMPUTED
      here from the doubles file (both mutation slots of every double row,
      groupby (pos, mut), input_count >= t for t in {23, 25, 28} and
      unfiltered; a double row never places two mutations at the same
      position, Phase 3a T4-G3) and compared against the stored columns for
      all 1,045 singles, gate max|diff| = 0. The stored columns are used
      downstream only if this gate passes.
  R4  G-5 uses TWO independent derivations of the wild-type residue the
      fitness data implies at each position: (i) the 19 non-WT muts in the
      singles block leave exactly one letter of ACDEFGHIKLMNPQRSTVWY unused;
      (ii) the publisher's workbook WT-amino-acid columns (B, E, N; script
      128's T2-G4 derivation, quoted here with line numbers). The roster's
      stored wt_aa column is a third read-out checked against both. All
      three must agree at every position 2..56, and the assayed sequence
      must equal them there. If the workbook is missing, G-5 FAILS (exit 3);
      there is no silent fallback to a single derivation.

GATES (a failed gate stops the task: printed FAIL, exit 3; thresholds never
loosened; N never raised):
  G-A4a-1  four sha256 values equal their targets (above).
  G-A4a-2  doubles rows = 535,917 and singles rows = 1,045 (data rows,
           header excluded, both counted from the files).
  G-A4a-3  roster input structure: 1,045 rows, 1,045 unique background ids,
           positions 2..56 contiguous (55 positions), mut != wt_aa in every
           row, n_partners columns present.
  G-A4a-4  sequence construction: GB1_SEQ quoted at run time from
           scripts/73_gb1_estimator_transplant.py line 135 equals the
           constant used here; both sequences are 56 aa; assayed and
           project differ at exactly position 2 (Q vs T) and nowhere else.
  G-5      HARD (frozen section 6): three WT derivations agree at every
           position 2..56 (0 mismatches, lists printed), AND assayed
           matches them at every position 2..56 (0 mismatches), AND the
           project sequence differs from the data-derived sequence ONLY at
           position 2. Every one of the 1,045 roster rows' wt_aa matches
           the assayed residue at its position.
  G-A4b-1  draw: 400 ids, all unique, all drawn from the 1,045; the draw
           reproduces exactly on a second independent call (R2); draw order
           preserved in the draw_order column.
  G-A4b-2  floor: min n_partners over the 400 drawn >= 100 at each of t23,
           t25, t28 and unfiltered (frozen A1 floor; reported as inert).
  G-A4b-3  roster_v2.csv written, re-read, sha256 recomputed on the file
           on disk equals the printed one (write-before-scoring record).
           Nothing has been scored at this point in the pipeline.

OUTPUTS
  data/processed/phase3/gb1/roster_v2.csv      (400 rows, draw order)
  data/processed/phase3/gb1/sequences.csv      (assayed, project; single
                                               source of truth for 154/155)
  stdout is the record; tee'd to
  docs/tasks/phase3-overnight/PHASE3_A4a_A4b_FULL_OUTPUT.txt by the caller.

LIMITATIONS (printed at run time, AGENTS section 6)
  * Roster membership and order depend on decision R1, an interpretation of
    an ambiguous frozen phrase, fixed before any score exists; both readings
    are fitness-blind, so no reading can bias the draw toward an outcome.
  * The workbook WT derivation shares the publisher's file with the compacts
    (it is an independent COLUMN derivation, not an independent experiment).
  * n_partners here are read-depth-qualified counts under the disclosed
    proxy of frozen A1; they are reported at every threshold, none selected.
  * This script creates no statistical result: it fixes the analysis set.
"""
import sys
import os
import re
import time
import hashlib
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "external" / "gb1_olson2014"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "data" / "processed" / "phase3" / "gb1"
LOG3A = ROOT / "docs" / "tasks" / "phase3a-gb1-acquisition" / "PHASE3A_LOG.md"

TARGETS = {
    "doubles": ("data/external/gb1_olson2014/gb1_olson2014_doubles.csv",
                "89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769",
                535917),
    "singles": ("data/external/gb1_olson2014/gb1_olson2014_singles.csv",
                "0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3",
                1045),
    "landscape": ("data/external/GB1_fitness_landscape.txt",
                  "7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2",
                  None),
    "phase3a_roster": ("data/processed/gb1_background_roster.csv",
                       "ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac9230e79aae4",
                       None),
}
ROSTER_SHA_PROVENANCE = ("ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac"
                         "9230e79aae4")
XLSX = EXT / "1-s2.0-S0960982214012688-mmc2.xlsx"
DBL = EXT / "gb1_olson2014_doubles.csv"
SGL = EXT / "gb1_olson2014_singles.csv"
LAND = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
ROSTER_IN = PROC / "gb1_background_roster.csv"
SCRIPT73 = ROOT / "scripts" / "73_gb1_estimator_transplant.py"

# project's 2GB1 constant, quoted from scripts/73_gb1_estimator_transplant.py
# line 135 (verified at run time against that file, gate G-A4a-4)
GB1_SEQ_PROJECT = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
POS_ASSAYED_CHANGE = 2          # 1-based; T228Q template change
AA_ASSAYED = "Q"

AA = list("ACDEFGHIKLMNPQRSTVWY")
N_DRAW = 400
FLOOR = 100                     # frozen A1 floor (stated inert)
T_REPORT = (23, 25, 28)         # frozen A1 primary = 25

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append({"gate": name, "verdict": verdict, "value": value,
                  "note": note})
    print(f"  >>> {name}: {verdict}   value = {value}   {note}")


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(3)


def main():
    t0 = time.time()
    print("PHASE 3a Task A4a + A4b -- GB1 inputs, gate G-5, frozen roster "
          "draw (no model, no scoring)")
    print(f"numpy {np.__version__} | pandas {pd.__version__} | "
          f"python {sys.version.split()[0]}")
    print("NO MODEL LOADED. torch/esm are not imported by this script.")

    # ================= A4a: inputs =================
    rule("A4a -- INPUT VERIFICATION (independently recomputed, targets "
         "printed beside)")
    derived = {}
    for key, (rel, want_sha, want_rows) in TARGETS.items():
        p = ROOT / rel
        if not p.exists():
            fail(f"missing input file: {rel}")
        got_sha = sha256_of(p)
        n = sum(1 for _ in p.open("rb")) - 1          # data rows, header off
        derived[key] = (got_sha, n)
        print(f"  {rel}")
        print(f"    sha256 got {got_sha}")
        print(f"          target {want_sha}   "
              f"{'MATCH' if got_sha == want_sha else 'MISMATCH'}")
        if got_sha != want_sha:
            gate(f"G-A4a-1 sha256 {key}", "FAIL", got_sha,
                 f"target {want_sha}")
            fail(f"sha256 mismatch for {rel}")
        if want_rows is not None:
            print(f"    rows got {n:,}   target {want_rows:,}   "
                  f"{'MATCH' if n == want_rows else 'MISMATCH'}")
            if n != want_rows:
                gate(f"G-A4a-2 rows {key}", "FAIL", n, f"target {want_rows}")
                fail(f"row count mismatch for {rel}: {n} != {want_rows}")
    gate("G-A4a-1 four sha256 match their targets", "PASS",
         "4/4", "doubles, singles, landscape, Phase 3a roster")
    gate("G-A4a-2 row counts match", "PASS",
         f"doubles {derived['doubles'][1]:,}; singles {derived['singles'][1]:,}",
         "targets 535,917 / 1,045")

    # provenance of the roster target (the planning doc supplies no hash)
    log_txt = LOG3A.read_text()
    print(f"\n  roster sha256 provenance: the target string "
          f"{ROSTER_SHA_PROVENANCE}\n"
          f"    appears in PHASE3A_LOG.md: "
          f"{ROSTER_SHA_PROVENANCE in log_txt} (required True)")
    if ROSTER_SHA_PROVENANCE not in log_txt:
        gate("G-A4a-1 roster sha provenance", "FAIL", "absent",
             "target not found in PHASE3A_LOG.md")
        fail("roster sha256 provenance not found in PHASE3A_LOG.md")
    print(f"  DISCLOSURE (R4-style, AGENTS 6): the planning doc names the "
          f"roster file without a hash;\n"
          f"    the target above is Phase 3a's own recorded value.")

    # landscape shape (report only; script 73 gates it at 160,000)
    land = pd.read_csv(LAND, sep="\t")
    print(f"\n  landscape: {len(land):,} rows, columns {list(land.columns)}, "
          f"unique sequences {land['sequence'].nunique():,}")

    # ================= A4a: sequences =================
    rule("A4a -- SEQUENCES: ASSAYED vs PROJECT, AND G-5")
    src73 = SCRIPT73.read_text()
    m = re.search(r'^GB1_SEQ = "([A-Z]+)"', src73, flags=re.M)
    if not m:
        fail("could not extract GB1_SEQ from scripts/73")
    q73 = m.group(1)
    ln73 = next(i + 1 for i, l in enumerate(src73.splitlines())
                if l.startswith('GB1_SEQ = "'))
    print(f"  quoted at run time from scripts/73_gb1_estimator_transplant.py "
          f"line {ln73}:")
    print(f"    GB1_SEQ = \"{q73}\"")
    if q73 != GB1_SEQ_PROJECT:
        gate("G-A4a-4 script 73 quote matches constant", "FAIL", q73,
             f"constant {GB1_SEQ_PROJECT}")
        fail("GB1_SEQ quoted from script 73 differs from the constant here")
    print("    MATCHES the constant used here")

    proj = GB1_SEQ_PROJECT
    assert len(proj) == 56 and proj[1] == "T"
    assayed = proj[:POS_ASSAYED_CHANGE - 1] + AA_ASSAYED + proj[POS_ASSAYED_CHANGE:]
    print(f"  project  (T at pos {POS_ASSAYED_CHANGE}): {proj}")
    print(f"  assayed  (Q at pos {POS_ASSAYED_CHANGE}): {assayed}")
    diffs = [(i + 1, a, b) for i, (a, b) in enumerate(zip(proj, assayed))
             if a != b]
    print(f"  differences project vs assayed: {diffs} (must be exactly "
          f"[(2, 'T', 'Q')])")
    ok_seq = (len(proj) == 56 and len(assayed) == 56
              and diffs == [(POS_ASSAYED_CHANGE, "T", "Q")])
    if not ok_seq:
        gate("G-A4a-4 sequence construction", "FAIL", str(diffs),
             "expected exactly [(2, 'T', 'Q')]")
        fail("assayed/project differ at something other than position 2")
    gate("G-A4a-4 sequence construction", "PASS", str(diffs),
         "56 aa each; differ at exactly position 2 (T vs Q)")

    # ---- WT residue the fitness data implies, derivation (i): singles ----
    sgl = pd.read_csv(SGL)
    dbl = pd.read_csv(DBL)
    wt_from_sgl = {}
    not_exactly_19 = []
    for p in sorted(set(sgl["pos"].astype(int))):
        muts = set(sgl.loc[sgl["pos"] == p, "mut"])
        rest = set(AA) - muts
        if len(rest) != 1:
            not_exactly_19.append((p, sorted(rest)))
        else:
            wt_from_sgl[p] = rest.pop()
    positions = sorted(wt_from_sgl)
    print(f"\n  derivation (i) singles complement: {len(positions)} positions "
          f"{positions[0]}..{positions[-1]}, "
          f"contiguous {positions == list(range(positions[0], positions[-1] + 1))}")
    print(f"    positions without exactly one unused letter: {not_exactly_19}")

    # ---- derivation (ii): publisher's workbook WT columns (script 128 T2-G4)
    # QUOTED SOURCE: scripts/128_gb1_olson_verify_and_transplant_repro.py
    # lines 357-373 -- for rows i >= 3 the (WT-amino-acid col, Position col)
    # pairs are (row[2], row[1]), (row[5], row[4]), (row[14], row[13]);
    # first occurrence wins, conflicts recorded.
    if not XLSX.exists():
        gate("G-5 derivation (ii) workbook present", "FAIL", "missing",
             str(XLSX.relative_to(ROOT)))
        fail("publisher workbook missing: G-5 cannot use two derivations")
    import openpyxl
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    wt_wb, conflicts = {}, []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 3:
            continue
        for pa, pv in ((row[2], row[1]), (row[5], row[4]), (row[14], row[13])):
            if pa is None or pv is None:
                continue
            pa, pv = int(pa), str(pv)
            if pa in wt_wb and wt_wb[pa] != pv:
                conflicts.append((pa, wt_wb[pa], pv))
            wt_wb.setdefault(pa, pv)
    wb.close()
    print(f"  derivation (ii) workbook WT columns (script 128 T2-G4): "
          f"{len(wt_wb)} positions, conflicts {len(conflicts)} {conflicts[:5]}")

    # ---- G-5 ----
    print("\n  G-5 -- the assayed sequence vs the sequence the fitness data "
          "implies (positions 2..56):")
    mism_i_ii = [p for p in positions if wt_from_sgl.get(p) != wt_wb.get(p)]
    mism_assayed = [p for p in positions
                    if assayed[p - 1] != wt_from_sgl.get(p)]
    mism_proj = [(p, proj[p - 1], wt_from_sgl.get(p)) for p in positions
                 if proj[p - 1] != wt_from_sgl.get(p)]
    print(f"    derivation (i) vs (ii) mismatches: {len(mism_i_ii)} {mism_i_ii}")
    print(f"    assayed vs data-derived mismatches: {len(mism_assayed)} "
          f"{mism_assayed}")
    print(f"    project vs data-derived mismatches: {len(mism_proj)} {mism_proj}")
    print(f"    data-derived WT sequence, positions 2..56 (55 aa): "
          f"{''.join(wt_from_sgl[p] for p in positions)}")
    if mism_i_ii or mism_assayed:
        gate("G-5 assayed matches the fitness-data sequence at 2..56", "FAIL",
             f"i-vs-ii {len(mism_i_ii)}, assayed {len(mism_assayed)}",
             "must both be 0")
        fail("G-5 failed: sequence mismatch")
    if mism_proj != [(2, "T", "Q")]:
        gate("G-5 project differs only at position 2", "FAIL",
             str(mism_proj), "expected only [(2, 'T', 'Q')]")
        fail("G-5 failed: project sequence differs outside position 2")
    gate("G-5 assayed matches the fitness-data sequence at 2..56", "PASS",
         "0 mismatches over 55 positions; two independent derivations agree",
         "project differs only at position 2 (T vs Q)")

    # ---- A4a roster input structure + third read-out of wt_aa ----
    rule("A4a -- PHASE 3a ROSTER FILE STRUCTURE (1,045 single mutants)")
    ros = pd.read_csv(ROSTER_IN)
    print(f"  rows {len(ros):,}, columns {list(ros.columns)}")
    need = (["background_id", "pos", "wt_aa", "mut",
             "background_single_fitness_W"]
            + [f"n_partners_t{t}" for t in T_REPORT] + ["n_partners_raw"])
    missing_cols = [c for c in need if c not in ros.columns]
    pos_ok = sorted(set(ros["pos"].astype(int))) == list(range(2, 57))
    bad_mut = int((ros["mut"] == ros["wt_aa"]).sum())
    bad_wt = [r.background_id for r in ros.itertuples()
              if r.wt_aa != wt_from_sgl.get(int(r.pos))]
    print(f"  unique ids {ros['background_id'].nunique():,} "
          f"(target 1,045) | positions 2..56 contiguous {pos_ok} | "
          f"rows mut==wt_aa {bad_mut} | wt_aa vs derivation (i) "
          f"mismatches {len(bad_wt)}")
    if (len(ros) != 1045 or ros["background_id"].nunique() != 1045
            or not pos_ok or bad_mut or missing_cols or bad_wt):
        gate("G-A4a-3 roster input structure", "FAIL",
             f"rows {len(ros)}, dup ids {ros['background_id'].nunique()}, "
             f"pos_ok {pos_ok}, mut==wt {bad_mut}, missing cols "
             f"{missing_cols}, wt mismatches {len(bad_wt)}", "see printed list")
        fail("roster input structure check failed")
    # every roster row's wt matches the ASSAYED residue at its position
    bad_assayed = [r.background_id for r in ros.itertuples()
                   if assayed[int(r.pos) - 1] != r.wt_aa]
    if bad_assayed:
        gate("G-5 roster wt_aa vs assayed residues", "FAIL",
             f"{len(bad_assayed)} rows", str(bad_assayed[:5]))
        fail("roster wt_aa does not match assayed sequence at its position")
    gate("G-A4a-3 roster input structure", "PASS",
         f"1,045 rows / 1,045 unique ids / positions 2..56 / no mut==wt / "
         f"all required columns", "wt_aa matches assayed at every row's position")
    gate("G-5 roster wt_aa vs assayed residues", "PASS",
         "0 mismatches over 1,045 rows", "third read-out agrees")

    # ================= A4b: roster draw =================
    rule("A4b -- FROZEN ROSTER DRAW (400 of 1,045, fitness-blind)")
    print("  decision R1 (pre-registered in this script's docstring): "
          "'sorted lexicographically by (position, mutant)'\n"
          "    = tuple sort (position as integer, mutant as string), which is "
          "the roster file's own order.")
    ordered = ros.sort_values(["pos", "mut"], kind="mergesort").reset_index(
        drop=True)
    sorted_ids = [str(x) for x in ordered["background_id"]]
    print(f"  sorted_ids: n={len(sorted_ids)}; first 5 {sorted_ids[:5]}; "
          f"last 5 {sorted_ids[-5:]}")
    draw = [str(x) for x in np.random.default_rng(0).choice(
        sorted_ids, N_DRAW, replace=False)]
    draw2 = [str(x) for x in np.random.default_rng(0).choice(
        sorted_ids, N_DRAW, replace=False)]
    print(f"  draw (decision R2, literal frozen call): n={len(draw)}; "
          f"first 10 {draw[:10]}")
    print(f"  draw reproduces on a second independent call: {draw == draw2}")
    uniq = len(set(draw)) == N_DRAW
    subset = set(draw) <= set(sorted_ids)
    if not (draw == draw2 and uniq and subset):
        gate("G-A4b-1 draw: 400 unique ids, reproducible", "FAIL",
             f"reproducible {draw == draw2}, unique {uniq}, subset {subset}",
             "all must hold")
        fail("roster draw check failed")
    gate("G-A4b-1 draw: 400 unique ids, reproducible", "PASS",
         f"n=400, unique 400, subset of 1,045 yes, second call identical",
         "default_rng(0).choice(sorted_ids, 400, replace=False)")

    first20 = draw[:20]
    print(f"\n  first 20 of the draw order = the two-sequence subset "
          f"(frozen A7):")
    for i, b in enumerate(first20, 1):
        print(f"    {i:>2}. {b}")

    # ---- R3: independent recomputation of n_partners from the doubles ----
    print("\n  R3 -- n_partners recomputed independently from the doubles "
          "file (both slots, groupby (pos, mut)):")
    both = pd.concat([
        dbl[["pos1", "mut1", "input_count"]].rename(
            columns={"pos1": "pos", "mut1": "mut"}),
        dbl[["pos2", "mut2", "input_count"]].rename(
            columns={"pos2": "pos", "mut2": "mut"}),
    ], ignore_index=True)
    both["pos"] = both["pos"].astype(int)
    same_pos = int((dbl["pos1"] == dbl["pos2"]).sum())
    print(f"    double rows with pos1 == pos2: {same_pos} (Phase 3a T4-G3 = 0; "
          f"a background can never count a partner at its own position)")
    counts = {"n_partners_raw": both.groupby(["pos", "mut"], sort=False).size()}
    for t in T_REPORT:
        counts[f"n_partners_t{t}"] = (both[both["input_count"] >= t]
                                      .groupby(["pos", "mut"], sort=False).size())
    counts = pd.DataFrame(counts).reset_index()
    counts["pos"] = counts["pos"].astype(int)
    chk = ros.merge(counts, on=["pos", "mut"], how="left",
                    suffixes=("", "_recomp"))
    all_ok = True
    for c in [f"n_partners_t{t}" for t in T_REPORT] + ["n_partners_raw"]:
        diff = np.abs(chk[c].to_numpy(dtype=float)
                      - chk[f"{c}_recomp"].to_numpy(dtype=float))
        n_nan = int(np.isnan(diff).sum())
        d = float(np.nanmax(diff)) if n_nan < len(diff) else float("nan")
        print(f"    {c:<18} max|stored - recomputed| = {d}   "
              f"NaN rows = {n_nan}")
        all_ok &= (n_nan == 0 and d == 0)
    if not all_ok:
        gate("G-A4b-2 n_partners recomputation", "FAIL",
             "nonzero max|diff| or NaN", "stored columns not trusted")
        fail("n_partners recomputation mismatch")
    gate("G-A4b-2 n_partners recomputation", "PASS",
         "max|stored - recomputed| = 0 for t23, t25, t28, unfiltered "
         "over all 1,045 singles", "")

    # ---- floor (frozen A1) on the 400 drawn ----
    sub = chk[chk["background_id"].isin(set(draw))].copy()
    print(f"\n  n_partners over the 400 drawn backgrounds (frozen A1 floor "
          f"{FLOOR}; primary t=25):")
    floor_ok = True
    for c in [f"n_partners_t{t}" for t in T_REPORT] + ["n_partners_raw"]:
        v = sub[c].to_numpy()
        print(f"    {c:<18} min {v.min():,}  median {int(np.median(v)):,}  "
              f"max {v.max():,}  (all >= {FLOOR}: {bool(v.min() >= FLOOR)})")
        floor_ok &= bool(v.min() >= FLOOR)
    if len(sub) != N_DRAW:
        fail("drawn subset does not join to exactly 400 roster rows")
    if not floor_ok:
        gate("G-A4b-2 floor: all 400 clear the 100-partner floor", "FAIL",
             f"min < {FLOOR}", "frozen A1")
        fail("100-partner floor not cleared by every drawn background")
    floor_min = int(min([sub[f"n_partners_t{t}"].min() for t in T_REPORT]
                        + [sub["n_partners_raw"].min()]))
    gate("G-A4b-2 floor: all 400 clear the 100-partner floor", "PASS",
         f"min over t23/t25/t28/unfiltered = {floor_min:,} >= {FLOOR}",
         "floor stated inert by frozen A1; still verified")

    # ---- write roster_v2 BEFORE any scoring ----
    rule("A4b -- WRITE data/processed/phase3/gb1/roster_v2.csv AND HASH IT")
    OUT.mkdir(parents=True, exist_ok=True)
    kept = ordered[ordered["background_id"].isin(set(draw))].copy()
    kept["draw_order"] = [draw.index(b) + 1 for b in kept["background_id"]]
    kept = kept.sort_values("draw_order", kind="mergesort")
    cols = (["draw_order", "background_id", "pos", "wt_aa", "mut",
             "background_single_fitness_W"]
            + [f"n_partners_t{t}" for t in T_REPORT] + ["n_partners_raw"])
    roster_out = OUT / "roster_v2.csv"
    kept[cols].to_csv(roster_out, index=False)
    sha_written = sha256_of(roster_out)
    reread = pd.read_csv(roster_out)
    sha_reread = sha256_of(roster_out)
    print(f"  rows written: {len(reread):,} (target {N_DRAW})")
    print(f"  first 3 rows verbatim:\n{reread.head(3).to_string(index=False)}")
    print(f"  last 1 row verbatim:\n{reread.tail(1).to_string(index=False)}")
    print(f"  sha256 of roster_v2.csv on disk: {sha_written}")
    print(f"  sha256 recomputed after re-read : {sha_reread}")
    if len(reread) != N_DRAW or sha_written != sha_reread:
        gate("G-A4b-3 roster_v2 written, hashed, re-read", "FAIL",
             f"rows {len(reread)}, sha stable {sha_written == sha_reread}",
             "")
        fail("roster_v2 write/re-read check failed")
    gate("G-A4b-3 roster_v2 written, hashed, re-read", "PASS",
         f"400 rows, sha256 {sha_written[:8]}... stable across re-read",
         "written before any scoring; nothing has been scored")

    seq_out = OUT / "sequences.csv"
    pd.DataFrame({"name": ["assayed", "project"],
                  "sequence": [assayed, proj],
                  "pos2": [assayed[1], proj[1]]}).to_csv(seq_out, index=False)
    print(f"\n  sequences.csv written: {seq_out.relative_to(ROOT)} "
          f"sha256 {sha256_of(seq_out)}")
    print(f"    assayed {assayed}")
    print(f"    project {proj}")

    # ================= summary =================
    rule("SUMMARY -- A4a + A4b")
    n_pass = sum(1 for g in GATES if g["verdict"] == "PASS")
    for g in GATES:
        print(f"  [{g['verdict']}] {g['gate']}: {g['value']}  {g['note']}")
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS, "
          f"{len(GATES) - n_pass} FAIL, exit "
          f"{0 if n_pass == len(GATES) else 3}")
    print("\n  LIMITATIONS (AGENTS 6, printed by the script itself):")
    print("    * Roster membership/order depends on decision R1, an "
          "interpretation of an ambiguous frozen phrase,\n"
          "      fixed before any score exists; both readings are "
          "fitness-blind.")
    print("    * The workbook WT derivation shares the publisher's file with "
          "the compact CSVs (independent\n"
          "      COLUMN derivation, not an independent experiment).")
    print("    * n_partners are read-depth-qualified counts under the "
          "disclosed proxy of frozen A1, reported\n      at every "
          "threshold; none is selected.")
    print("    * This script creates no statistical result: it fixes the "
          "analysis set.")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if n_pass == len(GATES) else 3)


if __name__ == "__main__":
    main()
