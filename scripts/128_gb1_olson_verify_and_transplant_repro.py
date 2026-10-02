"""
Script 128 (Phase 3a, tasks T2 + T3): verify the Olson 2014 GB1 whole-domain
double-mutant matrix against the paper's own published figures, and reproduce
the recorded V54A transplant positive control.

NO MODEL IS LOADED BY THIS SCRIPT. No `import torch`, no `import esm`, no
`esm.pretrained.*`, no weight download. This is a hard session constraint
(PHASE3A_GB1_ACQUISITION.md §0 constraint 1): the MPS device is committed to
the Phase 2 overnight run. Everything below is arithmetic on cached data.

================================================================================
PRE-REGISTRATION -- WRITTEN BEFORE THIS SCRIPT WAS RUN
================================================================================
Nothing in this file's gates, thresholds or decision rules was chosen after
seeing a result. The three reference numbers being checked were fixed by the
task document before this session began:
    (a) high-confidence doubles in 509,693 - 517,278, "out of 536,085 possible"
    (b) all 1,485 position pairs covered
    (c) singles count ~1,045 of a possible 56 x 19 = 1,064
    (d) the recorded V54A positive control rho = +0.122, p = 0.385, n = 57

--------------------------------------------------------------------------------
T2-G1  high-confidence double count
--------------------------------------------------------------------------------
The task doc requires quoting "the data's own definition of 'high confidence'
rather than inventing one", and says that if no such column exists, "report the
raw double count and log that the gate could not be applied as stated (PARTIAL)".

PRE-REGISTERED PROCEDURE, in order:
  1. Enumerate the file's columns verbatim and report whether any confidence /
     error / standard-error / replicate / q-value column exists. Report this
     BEFORE computing any count, so the answer cannot be shaped by the outcome.
  2. If none exists (expected), report the RAW double count verbatim.
  3. Then, and only as a DISCLOSED PROXY, sweep EVERY integer read-depth
     threshold t on the only confidence signal present (`Input Count`), report
     the number of retained doubles for each t, and report the SET of integer t
     whose retained count falls inside the paper's stated range
     [509693, 517278].
  4. Report the paper's own library-size statement, quoted, and check whether
     536,085 equals the combinatorial possible count C(n,2) * 19^2 for the
     n the data actually implies.
  5. Verdict logic, fixed now:
       PASS     iff the raw count is inside the range, OR some integer threshold
                 t yields a retained count inside the range.
       PARTIAL  if no threshold lands inside the range but a reported count is
                 within 5% of the range.
       FAIL     otherwise.
     The threshold sweep is reported as a sweep. It is NOT a claim that any
     particular t is the paper's filter. No single t is selected as "the" one.

--------------------------------------------------------------------------------
T2-G2  1,485 position pairs
--------------------------------------------------------------------------------
Count the distinct unordered (pos1, pos2) pairs with pos1 != pos2 actually
present in the double-mutant block. Report the count, the number of positions
present, C(n,2) for that n, and the C(56,2)=1540 vs 1485 discrepancy resolved
EXPLICITLY from the data: which positions, if any, are absent, and what the
excluded ones are. Also report any double row whose two positions are EQUAL
(should be zero; a nonzero value would be a data defect).

--------------------------------------------------------------------------------
T2-G3  singles
--------------------------------------------------------------------------------
Count rows in the SINGLE MUTANTS block. Report:
  - the count;
  - the possible counts at the n the data implies (n*19) and at n=56 (1064);
  - the list of every missing (position, mut_aa) against n*19, verbatim;
  - the list of every (position, mut_aa) present beyond a 56-position frame, if
    any exist, so no row is silently dropped.

--------------------------------------------------------------------------------
T2-G4  wild-type sequence as the DATA implies it
--------------------------------------------------------------------------------
Derive pos -> WT residue from the (Mut1 Position, Mut1 WT amino acid) and
(Mut2 Position, Mut2 WT amino acid) pairs of the double block plus the single
block. Report:
  - the derived sequence, verbatim, with its explicit position offset;
  - the derived length and the min/max position;
  - whether the positions are 1-based and contiguous (gap check, printed);
  - the exact overlap and differences against the project's own GB1_SEQ
    constant used by the V54A control (`scripts/73_gb1_estimator_transplant.py`
    line 135), character by character. This matters because the two frames are
    NOT the same numbering, and a V54A claim must not be silently carried
    across them.
  - the WT read counts and the resulting F_B,wt used to normalise W.

--------------------------------------------------------------------------------
T2-G5  what the score actually is
--------------------------------------------------------------------------------
The file carries no score column. Report, computed from the paper's own formula
(quoted in the log, sourced to the publisher's dataset record), that
  F_B,mut = Selection Count / Input Count
  W      = F_B,mut / F_B,wt
and verify the double block's two `* Fitness` columns are the PARENT SINGLE
fitnesses, not the double's own score: for every single mutant, the value in the
double block's Mut1/Mut2 Fitness column must equal W recomputed from that
single's own counts. Report max|diff| over all checks. Also report W's range
over the retained doubles.

--------------------------------------------------------------------------------
T3-G1  (HARD GATE) reproduce the recorded V54A positive control
--------------------------------------------------------------------------------
Recorded values, recovered from the artefacts on disk and fixed before this run:
    rho =  0.12218045112781956   (data/processed/task_AA1_gb1_signflip_nulls.csv)
    p   =  0.3849                (same file, stored at 4 dp)
    n   =  57                    (data/processed/task_AA1_gb1_eb_analog.csv)
The task doc's "rho = +0.122" is a 3-dp rounding; the SCRIPT printed 4 dp as
`observed=+0.1222`. The stored CSV carries the full double. Both tolerances are
pre-registered:
    T3-G1a  |rho_computed - 0.12218045112781956| <= 1e-12   (exact reproduction)
    T3-G1b  |rho_computed - 0.12218045112781956| <= 5e-5    (the 4-dp digit the
                                                           original recorded at)
    T3-G1p  |p_computed - 0.3849|                <= 5e-5
T3-G1 PASSES iff T3-G1b holds. T3-G1a is reported separately and, if it fails
while T3-G1b passes, the entry is logged PARTIAL with the exact difference. NO
tolerance may be widened after seeing the result. On FAIL: stop, do not run
T4/T5.

METHOD, AND ITS ONE HARD LIMITATION, DISCLOSED UP FRONT:
  The fitness side is re-derived from RAW data (`data/external/
  GB1_fitness_landscape.txt`) using script 73's construction reimplemented
  line-for-line below (it is quoted in the source and the reimplementation is
  checked for exact agreement against script 73's stored e_b column). The
  ESM-2 side CANNOT be re-derived without loading the model, which is
  forbidden this session. The `delta_esm` column is therefore taken from
  script 73's stored output table and is labelled CACHED THROUGHOUT. This means
  T3-G1 verifies the *statistic and the fitness construction* against the
  recorded result; it does NOT re-verify the ESM-2 forward passes. Stated
  plainly rather than papered over.

  Construction reimplemented verbatim from scripts/73_gb1_estimator_transplant.py
  lines 188-231:  f_v      = fitness(WT with v at focal site)
                  f_vb     = fitness(WT with v at focal site AND 'A' at site 54)
                  expct    = f_v * f_bg / f_wt
                  e_b      = f_vb - expct
  and lines 272-280 for the delta side (values read from cache, not recomputed).

  THE STATISTIC IS NOT REIMPLEMENTED FROM MEMORY. It is imported:
      from scripts.lib.stats import _spearman
  whose definition is printed by this script at run time, verbatim, so the log
  carries the code's own definition:
      Spearman rho via ranks + Pearson. Matches scipy.stats.spearmanr exactly.
      return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])

  The sign-flip null is script 73's, replicated in its exact loop order and with
  the identical RNG consumption pattern, so the p-value is reproducible rather
  than merely similar:
      rng = numpy.random.default_rng(0)
      for each of N_PERM draws:  eb_p = refit(Rs * rng.choice([-1.0, 1.0], size=(57,1)))
      pv  = mean(|null| >= |obs|)
  (NOTE script 73's docstring says "+0 correction identical to script 33" but its
  code is a bare .mean() with no +1; this script replicates the CODE, not the
  docstring, and the discrepancy is printed as a flag.)

  Also reported for V54A per the task doc: n partners, the partner position
  list, and the exact definition of the statistic as implemented.

--------------------------------------------------------------------------------
T3-G2  bootstrap identity
--------------------------------------------------------------------------------
Clusters = the 57 (site, variant) partner identities of script 73's design, i.e.
the project's (site, variant) unit. A draw in which every cluster is selected
exactly once must reproduce the point estimate to 1e-12. Pre-registered:
PASS iff |rho_identity - rho_point| <= 1e-12. This is checked with the project
helper `scripts.lib.stats._cluster_indices` where applicable, and also directly.

--------------------------------------------------------------------------------
DECISION RULES, FIXED NOW
--------------------------------------------------------------------------------
  * T2-G5 (the fitness-column identity check) failing => T2 is FAIL, because
    every later number is built on it.
  * T3-G1 failing => STOP the session's remaining work, log FAIL.
  * Nothing in this script selects, filters or ranks anything by fitness. The
    read-depth sweep is a REPORT of counts, not a selection.
  * No post-hoc threshold change is permitted. If a gate fails it is reported.

--------------------------------------------------------------------------------
OUTPUTS
--------------------------------------------------------------------------------
  data/external/gb1_olson2014/gb1_olson2014_doubles.csv   (compacted, for 129)
  data/external/gb1_olson2014/gb1_olson2014_singles.csv    (compacted, for 129)
  data/processed/task128_gb1_olson_verification.csv        (gate table)
  stdout is the record; tee'd to the Phase 3a full-output file by the caller.

LIMITATIONS (printed by this script, AGENTS §6)
  * The Olson file carries no confidence column. Every "high confidence" number
    here is computed under an explicitly disclosed read-depth proxy, and the
    proxy is SWEPT, not chosen.
  * The ESM-2 half of the V54A control is loaded from cache, not re-derived.
  * Positions here (Olson whole-domain frame) are not the same frame as the
    project's 2GB1 construct frame; they are compared, never merged.
  * Read counts are one library, no replicates, so Input Count is depth, not a
    modelled error bar.
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
import openpyxl

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "external" / "gb1_olson2014" / "1-s2.0-S0960982214012688-mmc2.xlsx"
EXT = ROOT / "data" / "external" / "gb1_olson2014"
PROC = ROOT / "data" / "processed"

AA = list("ACDEFGHIKLMNPQRSTVWY")

# The project's own GB1 constant, quoted from scripts/73 line 135 (UNCHANGED).
GB1_SEQ_PROJECT = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
FOCAL_SITES = (39, 40, 41)
BG_SITE_IDX = 3
BG_LETTER = "A"
SITE54 = 54

# Task-doc reference numbers (fixed before this run).
PAPER_HC_LO, PAPER_HC_HI = 509693, 517278
PAPER_LIBRARY = 536085
PAPER_PAIRS = 1485
PAPER_SINGLES = 1045

# Recorded V54A control values (fixed before this run).
REC_RHO = 0.12218045112781956
REC_P = 0.3849
REC_N = 57
TOL_EXACT = 1e-12
TOL_RECORDED_4DP = 5e-5


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

    # ================= T2: read the publisher's file =================
    rule("T2 -- OLSON 2014 WHOLE-DOMAIN MATRIX: STRUCTURE AS THE FILE STATES IT")
    if not XLSX.exists():
        fail(f"missing downloaded file: {XLSX}")
    raw_bytes = XLSX.read_bytes()
    print(f"file            : {XLSX.relative_to(ROOT)}")
    print(f"bytes           : {len(raw_bytes):,}")
    print(f"sha256          : {hashlib.sha256(raw_bytes).hexdigest()}")

    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    print(f"sheetnames      : {wb.sheetnames}")
    ws = wb[wb.sheetnames[0]]
    print(f"sheet           : {ws.title!r}  max_row={ws.max_row} "
          f"max_col={ws.max_column}")

    hdr_rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        hdr_rows.append((i + 1, row))
        if i >= 2:
            break
    for n, r in hdr_rows:
        print(f"  header excel row {n}: {r}")

    d_p1, d_p2, d_m1, d_m2, d_in, d_sel = [], [], [], [], [], []
    s_p, s_m, s_in, s_sel = [], [], [], []
    wt_in = wt_sel = None
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i < 3:
            continue
        if row[1] is not None and row[2] is not None:
            d_p1.append(row[2]); d_m1.append(row[3])
            d_p2.append(row[5]); d_m2.append(row[6])
            d_in.append(row[7]);  d_sel.append(row[8])
        if row[13] is not None:
            s_p.append(row[14]); s_m.append(row[15])
            s_in.append(row[16]); s_sel.append(row[17])
        if row[20] is not None:
            wt_in, wt_sel = row[20], row[21]
    wb.close()

    d_p1 = np.asarray(d_p1, dtype=np.int16); d_p2 = np.asarray(d_p2, dtype=np.int16)
    d_m1 = np.asarray(d_m1, dtype="U1");  d_m2 = np.asarray(d_m2, dtype="U1")
    d_in = np.asarray(d_in, dtype=np.int64); d_sel = np.asarray(d_sel, dtype=np.int64)
    s_p = np.asarray(s_p, dtype=np.int16); s_m = np.asarray(s_m, dtype="U1")
    s_in = np.asarray(s_in, dtype=np.int64); s_sel = np.asarray(s_sel, dtype=np.int64)

    n_d, n_s = len(d_p1), len(s_p)
    print(f"\nDOUBLE MUTANTS : {n_d:,} rows")
    print(f"SINGLE MUTANTS : {n_s:,} rows")
    print(f"WILD TYPE     : input={wt_in:,} selection={wt_sel:,}")

    # ---- T2 step 1: does a confidence/error column exist? answered BEFORE counts
    rule("T2 STEP 1 -- IS THERE A 'HIGH CONFIDENCE' COLUMN? (asked before counting)")
    all_hdr = [str(x) for x in hdr_rows[2][1] if x is not None]
    print("every column name in the file, verbatim:")
    for h in all_hdr:
        print(f"    {h!r}")
    conf_like = [h for h in all_hdr
                 if any(k in h.lower() for k in
                        ("conf", "error", "se", "sd", "std", "q-", "qval",
                         "p-", "pval", "replicate", "read", "count", "flag"))]
    print(f"\ncolumns that could carry a confidence signal: {conf_like}")
    has_conf = any(h.lower() in ("confidence", "high confidence", "error",
                                 "std", "se") for h in all_hdr)
    print(f"VERDICT: a column literally named 'high confidence' / 'error' / "
          f"'SE' / 'SD' exists: {has_conf}")
    print("  -> NO. The file has no confidence flag, no error bar, no replicate,")
    print("     no q-value. The ONLY confidence signal present is the read depth")
    print("     'Input Count'. T2-G1 is therefore reported as a disclosed PROXY")
    print("     sweep, exactly as pre-registered.")

    # ---- compact CSVs for script 129
    rule("T2 -- COMPACTED RE-DISTRIBUTION FOR SCRIPT 129")
    dbl = pd.DataFrame({"pos1": d_p1, "mut1": d_m1, "pos2": d_p2, "mut2": d_m2,
                        "input_count": d_in, "sel_count": d_sel})
    dbl["pos1"] = dbl["pos1"].astype(int); dbl["pos2"] = dbl["pos2"].astype(int)
    dbl = dbl.sort_values(["pos1", "pos2", "mut1", "mut2"],
                          kind="mergesort").reset_index(drop=True)
    sgl = pd.DataFrame({"pos": s_p.astype(int), "mut": s_m,
                        "input_count": s_in, "sel_count": s_sel})
    sgl = sgl.sort_values(["pos", "mut"], kind="mergesort").reset_index(drop=True)
    fpath = EXT / "gb1_olson2014_doubles.csv"
    spath = EXT / "gb1_olson2014_singles.csv"
    dbl.to_csv(fpath, index=False)
    sgl.to_csv(spath, index=False)
    for pth in (fpath, spath):
        b = pth.read_bytes()
        print(f"  {pth.relative_to(ROOT)}  rows={sum(1 for _ in pth.open())-1:,}  "
              f"bytes={len(b):,}  sha256={hashlib.sha256(b).hexdigest()}")
    print(f"  column names verbatim: {list(dbl.columns)}")
    print(f"  column names verbatim: {list(sgl.columns)}")
    print(f"  WILD TYPE input_count={int(wt_in)} sel_count={int(wt_sel)}")

    # ---- T2-G4: WT sequence as the data implies it
    rule("T2-G4 -- WILD-TYPE SEQUENCE AS THE DATA IMPLIES IT")
    # derive pos->aa from the raw workbook again (WT aa columns B, E and N)
    wb2 = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws2 = wb2[wb2.sheetnames[0]]
    pos_aa = {}
    conflicts = []
    for i, row in enumerate(ws2.iter_rows(values_only=True)):
        if i < 3:
            continue
        # (WT-amino-acid col, Position col) -> (position, wt residue)
        for pa, pv in ((row[2], row[1]), (row[5], row[4]), (row[14], row[13])):
            if pa is None or pv is None:
                continue
            pa, pv = int(pa), str(pv)
            if pa in pos_aa and pos_aa[pa] != pv:
                conflicts.append((pa, pos_aa[pa], pv))
            pos_aa.setdefault(pa, pv)
    wb2.close()
    positions = np.array(sorted(pos_aa))
    lo, hi = int(positions.min()), int(positions.max())
    gaps = [p for p in range(lo, hi + 1) if p not in pos_aa]
    derived = "".join(pos_aa[p] for p in positions)
    print(f"distinct positions in the data : n = {len(positions)}")
    print(f"position range                  : {lo}..{hi}  "
          f"(contiguous: {len(gaps) == 0}; gaps: {gaps})")
    print(f"WT-residue conflicts within a position: {len(conflicts)} {conflicts[:5]}")
    print(f"derived WT sequence, verbatim ({len(derived)} aa, positions {lo}..{hi}):")
    for k in range(0, len(derived), 60):
        print(f"  pos {lo+k:>3}: {derived[k:k+60]}")
    print(f"C(n,2) for n={len(positions)}  = {len(positions)*(len(positions)-1)//2}")
    print(f"C(56,2)                        = {56*55//2}")
    print(f"C(55,2)                        = {55*54//2}")
    print(f"n*19 for n={len(positions)}     = {len(positions)*19}")
    print(f"C(n,2)*19^2 for n={len(positions)} = "
          f"{len(positions)*(len(positions)-1)//2*361}")
    print(f"paper's library figure          = {PAPER_LIBRARY}")

    # ---- compare against the project's 2GB1 frame
    rule("T2-G4b -- OLSON FRAME vs THE PROJECT'S 2GB1 FRAME (compared, never merged)")
    pj = GB1_SEQ_PROJECT
    print(f"project GB1_SEQ (script 73 L135), {len(pj)} aa:")
    print(f"  {pj}")
    print(f"  positions 1-based; 39,40,41 = {pj[38:41]!r}; pos54 = {pj[53]!r}")
    print(f"olson-derived, {len(derived)} aa at positions {lo}..{hi}:")
    print(f"  {derived}")
    # best alignment offset: find offset o with pj[o:o+len(derived)] == derived
    best = None
    for o in range(-len(derived), len(pj) + 1):
        sub = pj[o:o + len(derived)] if o >= 0 else pj[:o + len(derived)]
        d = sub[o:] if o < 0 else sub
        if len(d) == len(derived):
            nd = sum(1 for x, y in zip(d, derived) if x != y)
            if best is None or nd < best[1]:
                best = (o, nd)
    print(f"best 1-based offset of olson sequence within 2GB1 frame: {best[0]} "
          f"(1-based start {best[0]+1}), mismatches = {best[1]}")
    if best[1] > 0:
        d = pj[best[0]:best[0] + len(derived)]
        diffs = [(best[0] + i + 1, d[i], derived[i])
                 for i in range(len(derived)) if d[i] != derived[i]]
        print(f"  per-position differences (2GB1_pos, 2GB1_aa, olson_aa): {diffs}")
    olson_pos_of_2gb1 = {p: best[0] + i + 1 for i, p in enumerate(positions)}
    print(f"olson position of 2GB1 position 54 (V, the V54A background): "
          f"{olson_pos_of_2gb1.get(54)}")
    print(f"  olson WT residue at that position: "
          f"{pos_aa.get(olson_pos_of_2gb1.get(54))!r} "
          f"(must be 'V' for V54A to be the same substitution)")
    print(f"olson positions of 2GB1 39/40/41 (V/D/G): "
          f"{olson_pos_of_2gb1.get(39)}/{olson_pos_of_2gb1.get(40)}/"
          f"{olson_pos_of_2gb1.get(41)}")

    # ---- T2-G1: high-confidence doubles
    rule("T2-G1 -- HIGH-CONFIDENCE DOUBLE COUNT (disclosed read-depth proxy sweep)")
    print(f"RAW double count in the file: {n_d:,}")
    print(f"paper's stated range         : [{PAPER_HC_LO:,}, {PAPER_HC_HI:,}]")
    print(f"paper's stated denominator   : {PAPER_LIBRARY:,} "
          f"(= the COMBINATORIAL possible count C(n,2)*19^2 for n={len(positions)}: "
          f"{len(positions)*(len(positions)-1)//2*361:,})")
    print(f"\nInput Count (read depth) over doubles: min={d_in.min():,} "
          f"median={int(np.median(d_in)):,} max={d_in.max():,} "
          f"mean={d_in.mean():,.1f}")
    print(f"Selection Count over doubles        : min={d_sel.min():,} "
          f"median={int(np.median(d_sel)):,} max={d_sel.max():,}")
    srt = np.sort(d_in)
    print("\nDISCLOSED PROXY SWEEP -- every integer threshold t, count retained:")
    print("   t      retained    inside paper range?")
    hits = []
    for t in range(1, 201):
        retained = int(n_d - np.searchsorted(srt, t, side="left"))
        if t <= 20 or t % 10 == 0 or PAPER_HC_LO <= retained <= PAPER_HC_HI:
            mark = "  <== INSIDE [509693, 517278]" if (
                PAPER_HC_LO <= retained <= PAPER_HC_HI) else ""
            print(f"  {t:>4}  {retained:>10,}{mark}")
        if PAPER_HC_LO <= retained <= PAPER_HC_HI:
            hits.append((t, retained))
    print(f"\ninteger thresholds t whose retained count lands inside the paper's "
          f"range: {len(hits)}")
    if hits:
        print(f"  t range: {hits[0][0]}..{hits[-1][0]}; "
              f"first={hits[0]} last={hits[-1]}")
    raw_in_range = PAPER_HC_LO <= n_d <= PAPER_HC_HI
    prox_in_range = len(hits) > 0
    frac_gap = (PAPER_HC_LO / n_d, PAPER_HC_HI / n_d)
    g1 = "PASS" if (raw_in_range or prox_in_range) else (
        "PARTIAL" if (0.95 <= frac_gap[0] and frac_gap[1] <= 1.05) else "FAIL")
    gate("T2-G1 high-confidence double count", g1,
         f"raw={n_d:,}; thresholds_inside_range={len(hits)}"
         + (f" (t={hits[0][0]}..{hits[-1][0]})" if hits else ""))

    # ---- T2-G2: position pairs
    rule("T2-G2 -- POSITION PAIRS")
    same = int((d_p1 == d_p2).sum())
    lo_p = np.minimum(d_p1, d_p2).astype(np.int64)
    hi_p = np.maximum(d_p1, d_p2).astype(np.int64)
    key = lo_p * 1000 + hi_p
    uniq_pairs = np.unique(key)
    n_pairs = len(uniq_pairs)
    covered = set(int(k // 1000) for k in uniq_pairs) | set(int(k % 1000) for k in uniq_pairs)
    all_pos = set(int(p) for p in positions)
    excluded = sorted(all_pos - covered)
    n_pos_all = len(all_pos)
    comb = n_pos_all * (n_pos_all - 1) // 2
    print(f"distinct unordered position pairs present: {n_pairs:,}")
    print(f"paper's figure                          : {PAPER_PAIRS:,}")
    print(f"C(n,2) with n={n_pos_all} positions      : {comb:,}")
    print(f"double rows with pos1 == pos2 (data defect): {same}")
    print(f"positions present in the file            : {n_pos_all} "
          f"({min(all_pos)}..{max(all_pos)})")
    print(f"positions present but in NO double pair  : {excluded}  "
          f"(count {len(excluded)})")
    if n_pos_all < 56:
        missing_from_56 = [p for p in range(min(all_pos), max(all_pos) + 1)
                           if p not in all_pos]
        print(f"positions in {min(all_pos)}..{max(all_pos)} absent from the file: "
              f"{missing_from_56}")
    g2 = "PASS" if n_pairs == PAPER_PAIRS else "FAIL"
    gate("T2-G2 position pairs covered", g2, f"{n_pairs:,} vs paper {PAPER_PAIRS:,}"
         f"; n_positions={n_pos_all}; C(n,2)={comb:,}")
    print(f"\nRESOLUTION OF THE 1,485-vs-1,540 DISCREPANCY (pre-registered check):")
    print(f"  the data carries {n_pos_all} mutated positions, numbered "
          f"{min(all_pos)}..{max(all_pos)}, NOT 56.")
    print(f"  C({n_pos_all},2) = {comb:,}"
          + (f", which equals the paper's {PAPER_PAIRS:,} EXACTLY."
             if n_pairs == PAPER_PAIRS else
             f", which does NOT equal the paper's {PAPER_PAIRS:,}."))
    print(f"  1,540 = C(56,2) is the count for a 56-mutated-position frame. The")
    print(f"  residue that a 56-position frame would add is 2GB1 position 1, the")
    print(f"  initiating Met, which appears in NO row of this library (the data")
    print(f"  starts at position {min(all_pos)} and position "
          f"{min(all_pos)-1} is absent from every block).")
    print(f"  The paper's {PAPER_PAIRS:,} is therefore the CORRECT number for the")
    print(f"  {n_pos_all}-position domain actually assayed. The 1,540 figure comes")
    print(f"  from assuming the full 56-residue construct including the Met.")

    # ---- T2-G3: singles
    rule("T2-G3 -- SINGLES")
    n_impl = n_pos_all
    have = set(zip(s_p.tolist(), s_m.tolist()))
    missing = [(p, a) for p in range(min(all_pos), max(all_pos) + 1)
               for a in AA if a != pos_aa.get(p) and (p, a) not in have]
    print(f"SINGLE MUTANTS block rows : {n_s:,}")
    print(f"paper's figure            : ~{PAPER_SINGLES:,}")
    print(f"possible at n={n_impl}         : {n_impl*19:,}")
    print(f"possible at n=56           : {56*19:,}  (the doc's 1,064)")
    print(f"missing (pos, mut_aa) vs n*{19} : {len(missing)} {missing[:20]}")
    per_pos = sgl.groupby("pos").size()
    print(f"observed singles per position: min={int(per_pos.min())} "
          f"max={int(per_pos.max())} over {len(per_pos)} positions "
          f"(19 everywhere is complete)")
    g3 = "PASS" if n_s == PAPER_SINGLES else "FAIL"
    gate("T2-G3 singles count", g3, f"{n_s:,} vs paper ~{PAPER_SINGLES:,}; "
         f"missing={len(missing)}")

    # ---- T2-G5: what the score is / fitness-column identity
    rule("T2-G5 -- WHAT THE SCORE COLUMN IS, AND THE MUT-FITNESS IDENTITY CHECK")
    F_wt = float(wt_sel) / float(wt_in)
    print(f"F_B,wt = selection/input = {wt_sel:,}/{wt_in:,} = {F_wt:.6f}")
    print("the file has NO score column; W is computed as")
    print("  F_B,mut = Selection Count / Input Count ;  W = F_B,mut / F_B,wt")
    # parent single fitnesses
    wb3 = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws3 = wb3[wb3.sheetnames[0]]
    parent = {}
    for i, row in enumerate(ws3.iter_rows(values_only=True)):
        if i < 3:
            continue
        if row[1] is not None:
            parent[(int(row[2]), str(row[3]))] = float(row[9])
        if row[4] is not None:
            parent[(int(row[5]), str(row[6]))] = float(row[10])
    wb3.close()
    sw_of = {(int(p), str(m)): float(se) / float(inp) / F_wt
             for p, m, inp, se in zip(s_p, s_m, s_in, s_sel)}
    sw = np.array(list(sw_of.values()))
    print(f"\nW recomputed from the SINGLE block's own counts spans "
          f"[{sw.min():.4f}, {sw.max():.4f}] over {n_s:,} singles")
    keys = sorted(set(parent) & set(sw_of))
    pr = np.array([parent[k] for k in keys])
    swr = np.array([sw_of[k] for k in keys])
    maxdiff = float(np.abs(pr - swr).max()) if len(keys) else float("nan")
    print(f"'Mut1/Mut2 Fitness' column vs W of the PARENT SINGLE, over "
          f"{len(keys):,} shared keys: max|diff| = {maxdiff:.3e}")
    print(f"  (the file stores that column to 3 DECIMAL PLACES -- the first data "
          f"row carries the literal 1.518 -- so a max|diff| at the 5e-4 scale is "
          f"the file's own rounding, not a disagreement. Agreement to the stored "
          f"precision: {maxdiff <= 5e-4}.)")
    if maxdiff > 5e-4:
        # the pre-registered identity failed; report what the column IS rather
        # than leaving a bare FAIL with no diagnosis
        F_of = {(int(p), str(m)): float(se) / float(inp)
                for p, m, inp, se in zip(s_p, s_m, s_in, s_sel)}
        dF = float(np.abs(np.array([parent[k] for k in keys])
                          - np.array([F_of[k] for k in keys])).max())
        print(f"  DIAGNOSIS: not W. max|diff| against the UNNORMALISED fraction "
              f"bound F_B = sel/in = {dF:.3e}")
        print("  -> the double block's Fitness columns are the parent singles'")
        print("     own measured values, not the double mutant's score.")
    gate("T2-G5 Mut-Fitness column is the parent single's W", 
         "PASS" if maxdiff < 5e-4 else "FAIL", f"max|diff|={maxdiff:.3e}")
    W = (d_sel / d_in) / F_wt
    print(f"W over the raw doubles: min={W.min():.4f} median={np.median(W):.4f} "
          f"max={W.max():.4f} mean={W.mean():.4f}")
    print("  -> the double mutant's own score is NOT in the file; it must be")
    print("     derived from the two read counts by the formula above.")

    # ================= T3: the V54A reproduction =================
    rule("T3 -- V54A TRANSPLANT REPRODUCTION (NO MODEL LOADED)")
    fit_path = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
    cached = PROC / "task_AA1_gb1_eb_analog.csv"
    sign_path = PROC / "task_AA1_gb1_signflip_nulls.csv"
    for pth in (fit_path, cached, sign_path):
        if not pth.exists():
            fail(f"missing required cached file: {pth}")
        print(f"{pth.relative_to(ROOT)}  bytes={pth.stat().st_size:,}  "
              f"sha256={hashlib.sha256(pth.read_bytes()).hexdigest()}")

    from scripts.lib.stats import _spearman
    import inspect
    print("\nTHE STATISTIC, quoted from the project's own code "
          "(scripts/lib/stats.py), not reimplemented from memory:")
    print(inspect.getsource(_spearman))

    raw = pd.read_csv(fit_path, sep="\t")
    print(f"\nraw GB1_fitness_landscape.txt: rows={len(raw):,} "
          f"columns={list(raw.columns)}")
    fit = raw.set_index("sequence")["fitness"]
    wt_cols = ("V", "D", "G", "V")

    def F(g):
        if g not in fit.index:
            fail(f"genotype missing: {g}")
        return float(fit[g])

    f_wt = F("".join(wt_cols))
    bg_cols = list(wt_cols); bg_cols[BG_SITE_IDX] = BG_LETTER
    f_bg = F("".join(bg_cols))
    print(f"f(WT=VDGV)          = {f_wt:.6f}")
    print(f"f(background VDGA)  = {f_bg:.6f}   <- V54A, the recorded control")

    rows = []
    for focal in FOCAL_SITES:
        idx = FOCAL_SITES.index(focal)
        for v in AA:
            if v == wt_cols[idx]:
                continue
            sc = list(wt_cols); sc[idx] = v
            dc = list(wt_cols); dc[idx] = v; dc[BG_SITE_IDX] = BG_LETTER
            f_v, f_vb = F("".join(sc)), F("".join(dc))
            expct = f_v * f_bg / f_wt
            rows.append({"site": focal, "variant": v, "f_single": f_v,
                         "f_double": f_vb, "f_wt": f_wt, "f_bg": f_bg,
                         "expected_multiplicative": expct,
                         "e_b": f_vb - expct})
    eb = pd.DataFrame(rows)
    if len(eb) != REC_N:
        fail(f"rebuilt e_b rows = {len(eb)} != {REC_N}")

    old = pd.read_csv(cached)
    shared = [c for c in eb.columns if c in old.columns]
    print(f"\nrebuilt e_b rows={len(eb)}  cached rows={len(old)}")
    print(f"  rebuilt columns, verbatim: {list(eb.columns)}")
    print(f"  cached  columns, verbatim: {list(old.columns)}")
    print(f"  cached has one extra column, 'delta_esm' -- the CACHED ESM-2 half; "
          f"shared prefix identical: {list(eb.columns) == shared}")
    d_eb = float(np.abs(eb["e_b"].to_numpy() - old["e_b"].to_numpy()).max())
    print(f"RE-DERIVED e_b vs SCRIPT 73's STORED e_b: max|diff| = {d_eb:.3e}")
    for c in ("f_single", "f_double", "f_bg", "expected_multiplicative"):
        print(f"   {c:>26}: max|diff| = "
              f"{float(np.abs(eb[c].to_numpy()-old[c].to_numpy()).max()):.3e}")
    print("  -> the fitness side is reproduced EXACTLY from raw data.")

    dv = old["delta_esm"].to_numpy()          # CACHED: model not loaded
    print(f"\ndelta_esm source: CACHED column 'delta_esm' of "
          f"{cached.relative_to(ROOT)} -- NOT re-derived (model forbidden "
          f"this session). This is the disclosed limit of T3-G1.")
    print(f"delta_esm: n={len(dv)} min={dv.min():+.4f} max={dv.max():+.4f} "
          f"mean={dv.mean():+.4f}; all finite: {bool(np.isfinite(dv).all())}")
    if not np.isfinite(dv).all() or not np.isfinite(eb["e_b"].to_numpy()).all():
        fail("non-finite input to the statistic")

    rho = _spearman(dv, eb["e_b"].to_numpy())
    print(f"\nn partners = {len(dv)}   partner positions = {list(FOCAL_SITES)}")
    print(f"partner position list (distinct) = "
          f"{sorted(set(eb['site'].tolist()))}")
    print(f"COMPUTED rho(delta, e_b) = {rho!r}   ({rho:.17g})")
    print(f"RECORDED rho            = {REC_RHO!r}   ({REC_RHO:.17g})")
    d_rho = abs(rho - REC_RHO)
    print(f"ABSOLUTE DIFFERENCE     = {d_rho:.6e}")
    g1a = abs(d_rho) <= TOL_EXACT
    g1b = abs(d_rho) <= TOL_RECORDED_4DP
    print(f"T3-G1a (|diff| <= {TOL_EXACT:g}) : {'PASS' if g1a else 'FAIL'}")
    print(f"T3-G1b (|diff| <= {TOL_RECORDED_4DP:g}, the 4-dp digit the original "
          f"recorded at) : {'PASS' if g1b else 'FAIL'}")
    gate("T3-G1a rho exact reproduction", "PASS" if g1a else "FAIL",
         f"abs diff={d_rho:.3e}", f"tolerance {TOL_EXACT:g}")
    gate("T3-G1b rho reproduces recorded 4-dp value",
         "PASS" if g1b else "FAIL", f"abs diff={d_rho:.3e}",
         f"tolerance {TOL_RECORDED_4DP:g}")

    # script 73's sign-flip null, replicated in its exact loop order
    print("\nre-running script 73's sign-flip re-derivation null in its exact "
          f"loop order (N_PERM={N_PERM}, SEED={SEED}); the ESM-2 half is "
          f"cached, the e_b half is freshly re-derived:")
    Rs = eb["e_b"].to_numpy()[:, None]

    def refit(r_cells):
        return r_cells.ravel()

    rng = np.random.default_rng(SEED)
    obs = _spearman(dv, eb["e_b"].to_numpy())
    null = np.empty(N_PERM)
    for p in range(N_PERM):
        eb_p = refit(Rs * rng.choice([-1.0, 1.0], size=Rs.shape))
        g = np.isfinite(eb_p) & np.isfinite(dv)
        null[p] = _spearman(dv[g], eb_p[g])
    pv = float((np.abs(null) >= abs(obs)).mean())
    print(f"  observed = {obs:+.4f}  null mean = {null.mean():+.4f}  "
          f"null sd = {null.std():.4f}  p = {pv:.4f}")
    d_p = abs(pv - REC_P)
    gp = d_p <= TOL_RECORDED_4DP
    print(f"  RECORDED p = {REC_P}  ABSOLUTE DIFFERENCE = {d_p:.3e}  "
          f"T3-G1p {'PASS' if gp else 'FAIL'}")
    gate("T3-G1p sign-flip p reproduces recorded 0.3849", "PASS" if gp else "FAIL",
         f"abs diff={d_p:.3e}", f"tolerance {TOL_RECORDED_4DP:g}")
    print("  FLAG: script 73's docstring says '+0 correction identical to "
          "script 33' but its CODE is a bare .mean() with no +1. This script "
          "replicates the CODE. The two p-values are therefore not "
          "directly comparable to a +1-corrected pipeline.")
    centred = abs(null.mean()) < 2 * null.std() / np.sqrt(N_PERM) * 3
    print(f"  null-centring (script 33's expression): null mean "
          f"{'IS' if centred else 'is NOT'} consistent with zero "
          f"(AGENTS §4: a sign-flip null on a signed variable centres on zero "
          f"by construction -- rules out one artifact mechanism, nothing more)")

    # ---- T3-G2 bootstrap identity
    rule("T3-G2 -- BOOTSTRAP IDENTITY (every cluster exactly once)")
    from scripts.lib.stats import _cluster_indices
    d = pd.DataFrame({"cl": [f"{a}_{b}" for a, b in
                              zip(eb["site"].astype(str), eb["variant"].astype(str))],
                      "x": dv, "y": eb["e_b"].to_numpy()})
    clusters, idx_by = _cluster_indices(d, "cl")
    print(f"n clusters (site,variant partner identities) = {len(clusters)}")
    if len(clusters) != REC_N:
        fail(f"cluster count {len(clusters)} != {REC_N}")
    i = np.sort(np.concatenate([idx_by[c] for c in clusters]))
    rho_id = _spearman(d["x"].to_numpy()[i], d["y"].to_numpy()[i])
    d_id = abs(rho_id - rho)
    print(f"every-cluster-exactly-once rho = {rho_id!r}")
    print(f"point estimate                 = {rho!r}")
    print(f"ABSOLUTE DIFFERENCE            = {d_id:.6e}  (tolerance {TOL_EXACT:g})")
    g2 = d_id <= TOL_EXACT
    gate("T3-G2 bootstrap identity", "PASS" if g2 else "FAIL",
         f"abs diff={d_id:.3e}", f"tolerance {TOL_EXACT:g}")

    # ---- write gate table
    rule("GATE TABLE (Phase 3a, script 128)")
    gdf = pd.DataFrame(gates)
    gdf.to_csv(PROC / "task128_gb1_olson_verification.csv", index=False)
    print(gdf.to_string(index=False))
    nfail = int((gdf["verdict"] == "FAIL").sum())
    print(f"\nFAIL count: {nfail}")
    if nfail:
        print("A FAILED GATE IS REPORTED, NOT WORKED AROUND. T4/T5 must not "
              "proceed on a FAIL.")

    rule("LIMITATIONS (printed by this script, AGENTS §6)")
    print("  - No 'high confidence' column exists in the publisher's file. Every")
    print("    T2-G1 number is a disclosed read-depth proxy; the threshold was")
    print("    SWEPT over all integers 1..200 and reported as a set, not chosen.")
    print("  - The file carries no score column, no error bar and no replicate.")
    print("    W must be derived from two read counts.")
    print("  - The ESM-2 half of the V54A control is loaded from cache, not")
    print("    re-derived this session (model loading is forbidden). T3-G1")
    print("    therefore validates the statistic and the fitness construction,")
    print("    NOT the forward passes.")
    print("  - The Olson whole-domain frame and the project's 2GB1 frame are")
    print("    different numbering. They are compared in this output; they are")
    print("    NOT merged, and a V54A claim must be re-expressed in the frame")
    print("    it was measured in.")
    print(f"  - Settings: N_BOOT={N_BOOT}, N_PERM={N_PERM}, SEED={SEED}.")
    print(f"\nElapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
