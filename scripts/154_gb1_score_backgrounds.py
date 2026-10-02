"""Script 154 (Phase 3a session 3a, task A4c) -- GB1 background scorer.

PRE-REGISTERED: this docstring was written before the first run of this
script. It implements PHASE3_OVERNIGHT.md Task A4c under the frozen
prereg/GB1_REGIME_PREREG_v2.md (76 lines, sha256 b3c82d589afc2889f60ad8626
dcb24d0496f77303d0696b52db700129fd1357e), sections 2 (statistic), 3 (A2:
passes per arm), 6 (gates), 7 (execution: detached, resumable, one output
file per background, in roster order). Session 3a runs this only for the
gates G-1' (A4d) and the timing smoke (A4e, scratch out-dir); the 400-
background stage itself is run by the A7 driver overnight, not here.

WHAT IT IMPLEMENTS (frozen pins, modeled on scripts/124_phase2_score_
backgrounds.py including its atomic-write and skip logic):
  * Scoring primitive: scripts/lib/esm_scoring.py::get_position_logprobs +
    get_device exactly as scripts 73/124 do -- ESM-2 esm2_t33_650M_UR50D,
    eval mode, torch.no_grad (inside the lib fn), ONE UNBATCHED forward
    pass per (background, position), masked-marginal, all 19 non-wild-type
    substitutions from that pass (S = log-odds against the wild-type
    residue at the pass position, frozen section 2).  No batching, no
    reimplementation.  The weights come from the local torch.hub cache;
    this script CHECKS the checkpoint file exists before loading and exits
    3 if it does not (never downloads).
  * WT arm (frozen A2): one pass at each of the 55 positions 2..56 under
    the CHOSEN sequence, computed once into <out-dir>/wt_arm.csv
    (1,045 rows).  Never a pass at position 1.
  * Background b at position p: sequence = chosen sequence with the roster
    substitution applied (wt residue asserted BEFORE substitution, mut
    asserted AFTER -- script 124's PIN-6 pattern); passes at the 54
    positions 2..56 excluding p (frozen A2: 55 minus its own).  The
    background's own position never appears in its own file (frozen G-2
    holds structurally; also asserted here).
  * delta_b(v) = S(v|b) - S(v|WT) is NOT computed here; script 155 joins
    each background file to wt_arm.csv on (position, mut_aa).

SEQUENCES AND INPUTS (sha256 gates, exit 3 on mismatch):
  data/processed/phase3/gb1/sequences.csv  sha256 f0d1d2d5b1376113568b17a04f5c9dfd9661517415c630e1d63a89b7032ca25f
    (written by script 160 before any scoring; contents additionally
    checked against the constants below, and the project constant is
    re-quoted at run time from scripts/73_gb1_estimator_transplant.py
    line 135 so a silent edit of either file is caught).
  data/processed/phase3/gb1/roster_v2.csv  sha256 edc259d460691c244ba293bc9e3e8675e11e2ce27638cf5cd88796524b7dbe4e
    (400 rows, written and hashed by script 160 BEFORE any scoring, frozen
    A4: no fitness-based or severity-based selection at any point).
  ASSAYED = project 2GB1 constant with position 2 = Q (frozen A2);
  PROJECT = the 2GB1 constant as script 73 uses it (T at position 2).

OUTPUT CONTRACT (one file per background, written ONLY after all 54
positions are done, ATOMICALLY):
  rows accumulated in memory -> <out-dir>/.bg_<bg_id>.csv.tmp ->
  os.replace() -> <out-dir>/bg_<bg_id>.csv.
  Columns: bg_id, sequence, position, mut_aa, score  (wt_arm.csv uses the
  same schema with bg_id = "WT").  Integrity asserted BEFORE the rename:
  rows == 19 x n_positions, unique (position, mut_aa), position set ==
  expected (own position absent), sequence column == the chosen sequence.
  After each published file: append file, kind, bg_id, sequence,
  n_positions, n_rows, seconds, median_pass_s, device to
  <out-dir>/manifest.csv (header if new; skipped files append nothing).
  Per-background time, ms/pass and a running ETA are printed.
  Any exception: current .tmp removed, traceback + ERROR printed, exit 1
  (never continues past a half-written file).

SKIP/RESUME (resumable stage, frozen section 7): a final file is skipped
only if it exists with the expected row count, the expected position set,
no duplicate (position, mut_aa), the expected bg_id AND the expected
sequence column.  A .tmp NEVER counts as completion.  Because roster order
= draw order (frozen A4), any completed prefix of an interrupted stage is
a random subsample.

ONE OUT-DIR PER SEQUENCE (decision S1, pre-registered): the frozen block
pins the per-background name as bg_<id>.csv, so the first-20 two-sequence
subset (frozen A7) cannot share a directory between sequences.  The
default out-dir data/processed/phase3/gb1 is the ASSAYED sequence; project
runs use a different out-dir (data/processed/phase3/gb1_project).  On
start, an existing manifest.csv or wt_arm.csv in the out-dir is read and
any sequence value differing from --sequence is a gate failure (exit 3),
so files of the two sequences can never overwrite or skip each other.

CLI (the four flags the planning doc requires, plus two for this session's
gates/timing; tests never touch the real output directory):
  --only BG_ID          score/skip just that roster background
  --limit-positions N   only the first N expected positions (sorted);
                        row expectation becomes N x 19; a file written
                        with this flag is INCOMPLETE for a later full run
                        and will be re-scored then -- by design; test and
                        timing use only
  --out-dir DIR         default data/processed/phase3/gb1
  --sequence {assayed,project}   default assayed
  --limit-roster N      only the first N backgrounds in roster (draw)
                        order -- used by the A4e timing smoke
  --wt-arm-only         score/skip only the WT arm

GATES (failed gate -> message + exit 3; thresholds never loosened):
  G-154-1 sequences.csv sha256 + content (both sequences) + script 73
          line-135 quote all agree with the constants above.
  G-154-2 roster_v2.csv sha256; 400 rows / 400 unique ids / draw_order
          1..400; every background's wt residue in the chosen sequence
          equals the roster wt_aa (G-5 echo), mut != wt, position in 2..56.
          ONE DOCUMENTED EXCEPTION (decision S2, added after test (d) of
          the A4c test plan failed, BEFORE any real score existed, with no
          threshold or frozen constant changed): under --sequence project
          the roster row(s) at position 2 have wt_aa = Q while the project
          sequence carries T there -- exactly the single difference G-5
          established.  Frozen A7 REQUIRES the first 20 backgrounds (which
          include G2QE, draw order 7) to be scored on BOTH sequences, so
          for --sequence project and own position 2 this check accepts
          (wt_aa == Q, seq[1] == T) and nothing else; every other row and
          every other sequence must still match exactly.  The same
          exception is applied to the background-sequence assert in the
          scoring loop.  Under the project arm a position-2 background's
          own position is excluded from its 54 passes anyway (frozen A2),
          so no log-odds is ever taken against the differing T reference.
  G-154-3 per-file integrity before the atomic rename (rows, uniqueness,
          position set, sequence column) + background-sequence asserts.
  G-154-4 out-dir belongs to the chosen sequence (decision S1).
  G-154-5 local ESM-2 650M checkpoint exists (never downloads).

CONVENTION: N_BOOT / SEED are read and printed but UNUSED -- this script
performs no bootstrap, no permutation and no randomness (the roster draw
already happened, pinned, in script 160).

TEST PLAN (before handing over, all inside
data/processed/phase3/gb1_scratch/, per AGENTS section 7):
  (a) --only G4KV --limit-positions 3 --out-dir .../gb1_scratch
      -> wt_arm.csv NOT written under --only? (WT arm IS written: 55
      positions, it is its own file) and bg_G4KV.csv has 3 x 19 = 57 rows;
  (b) repeat (a) -> both files skipped, untouched;
  (c) fake .bg_G4KV.csv.tmp left in scratch -> never treated as
      completion; real publish overwrites it;
  (d) --sequence project into the assayed scratch dir -> G-154-4 exit 3
      (the FIRST attempt instead died at G-154-2 on the position-2 rows;
      that is what prompted documented decision S2 above -- preserved as
      PHASE3_A4c_TESTS2_D_FAIL_OUTPUT.txt; after S2 the run reaches and
      must fail at G-154-4, the out-dir conflict this test is for);
  (e) corrupt roster/sequences sha in a scratch copy -> G-154-1/2 exit 3
      (path-overridden copies; the real files are never modified).

Usage:
  venv/bin/python3 scripts/154_gb1_score_backgrounds.py --wt-arm-only
      --out-dir data/processed/phase3/gb1_scratch
  venv/bin/python3 scripts/154_gb1_score_backgrounds.py --only G4KV

LIMITATIONS (AGENTS section 6, printed by the script itself): scores are
masked-marginal log-odds on one model (650M) on one device (mps here);
determinism across devices is NOT claimed.  This script creates no
statistic: it produces the two score tables that script 155 joins.  Pass
timing printed at the end is a property of this machine at this moment;
the stage projection is informational (the 100-minute budget comparison
is the A4e log entry's record, and a projection over budget never shrinks
the roster -- frozen A8/execution rule).
"""

import argparse
import hashlib
import os
import re
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SEQS_CSV = ROOT / "data" / "processed" / "phase3" / "gb1" / "sequences.csv"
ROSTER_CSV = ROOT / "data" / "processed" / "phase3" / "gb1" / "roster_v2.csv"
SCRIPT73 = ROOT / "scripts" / "73_gb1_estimator_transplant.py"

SEQS_SHA = ("f0d1d2d5b1376113568b17a04f5c9dfd9661517415c630e1d63a89b7032ca25f")
ROSTER_SHA = ("edc259d460691c244ba293bc9e3e8675e11e2ce27638cf5cd88796524b7dbe4e")
ASSAYED = "MQYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
PROJECT = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
N_ROSTER = 400
POSITIONS = list(range(2, 57))          # 55 WT-arm passes; no position 1
STAGE_PASSES = N_ROSTER * 54 + 55       # A4e projection formula
STAGE_BUDGET_S = 100 * 60               # 100-minute stage budget
PROJ_FACTOR = 1.25                      # A4e projection factor
CKPT = (Path(os.environ.get("TORCH_HOME", Path.home() / ".cache" / "torch"))
        / "hub" / "checkpoints" / "esm2_t33_650M_UR50D.pt")
ROWS_PER_PASS = 19


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gate_fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(3)


def load_inputs(sequence: str):
    """Gates G-154-1 and G-154-2. Returns (seq, roster) for `sequence`."""
    if not SEQS_CSV.exists():
        gate_fail(f"G-154-1 missing {SEQS_CSV}")
    got = sha256_of(SEQS_CSV)
    if got != SEQS_SHA:
        gate_fail(f"G-154-1 sequences.csv sha256 {got} != {SEQS_SHA}")
    seqs = pd.read_csv(SEQS_CSV).set_index("name")["sequence"].to_dict()
    if seqs.get("assayed") != ASSAYED or seqs.get("project") != PROJECT:
        gate_fail(f"G-154-1 sequences.csv content mismatch: {seqs}")
    # re-quote the project constant from script 73 at run time
    m = re.search(r'^GB1_SEQ = "([A-Z]+)"', SCRIPT73.read_text(), flags=re.M)
    if not m or m.group(1) != PROJECT:
        gate_fail("G-154-1 script 73 line-135 quote != PROJECT constant")
    print(f"G-154-1 sequences: sha256 ok; assayed/project match constants; "
          f"script 73 quote ok")

    if not ROSTER_CSV.exists():
        gate_fail(f"G-154-2 missing {ROSTER_CSV}")
    got = sha256_of(ROSTER_CSV)
    if got != ROSTER_SHA:
        gate_fail(f"G-154-2 roster_v2.csv sha256 {got} != {ROSTER_SHA}")
    ros = pd.read_csv(ROSTER_CSV)
    if (len(ros) != N_ROSTER or ros["background_id"].nunique() != N_ROSTER
            or sorted(ros["draw_order"].tolist()) != list(range(1, N_ROSTER + 1))):
        gate_fail(f"G-154-2 roster structure: {len(ros)} rows / "
                  f"{ros['background_id'].nunique()} ids / draw_order not "
                  f"1..{N_ROSTER}")
    seq = {"assayed": ASSAYED, "project": PROJECT}[sequence]
    bad, n_doc2 = [], 0
    for r in ros.itertuples():
        own = int(r.pos)
        if not (2 <= own <= 56) or r.mut == r.wt_aa:
            bad.append(r.background_id)
        elif seq[own - 1] == r.wt_aa:
            continue
        elif (sequence == "project" and own == 2 and r.wt_aa == "Q"
              and seq[1] == "T"):
            n_doc2 += 1                      # decision S2: documented
        else:
            bad.append(r.background_id)
    if bad:
        gate_fail(f"G-154-2 roster vs {sequence} sequence: {len(bad)} bad "
                  f"rows, first {bad[:5]}")
    print(f"G-154-2 roster: sha256 ok; {N_ROSTER} rows; every wt_aa equals "
          f"the {sequence} residue at its position (G-5 echo)"
          + (f"; decision-S2 documented position-2 exception exercised for "
             f"{n_doc2} row(s)" if n_doc2 else ""))
    return seq, ros


def out_dir_sequence_gate(out_dir: Path, sequence: str):
    """G-154-4 (decision S1): an out-dir belongs to exactly one sequence."""
    for name in ("manifest.csv", "wt_arm.csv"):
        p = out_dir / name
        if not p.exists():
            continue
        try:
            df = pd.read_csv(p)
        except Exception:
            continue
        if "sequence" in df.columns:
            other = sorted(set(df["sequence"].astype(str)) - {sequence})
            if other:
                gate_fail(f"G-154-4 {p.name} in {out_dir} contains "
                          f"sequence(s) {other} but --sequence {sequence}: "
                          f"one out-dir per sequence (decision S1)")
    print(f"G-154-4 out-dir {out_dir.name}: belongs to sequence "
          f"'{sequence}' (no conflicting file)")


def expected_positions(own):
    """Frozen A2: the 55 positions 2..56 minus the background's own."""
    return [p for p in POSITIONS if p != own]


def file_is_complete(path, bg_id, sequence, exp_positions):
    """Skip check: final file only; .tmp never counts."""
    if not path.exists():
        return False
    try:
        df = pd.read_csv(path)
    except Exception:
        return False
    need = ROWS_PER_PASS * len(exp_positions)
    return (len(df) == need
           and set(df.bg_id.astype(str)) == {bg_id}
           and set(df.sequence.astype(str)) == {sequence}
           and set(int(p) for p in df.position.unique())
               == set(exp_positions)
           and not df.duplicated(["position", "mut_aa"]).any())


def publish(path, tmp, rows, bg_id, sequence, exp_positions):
    """Integrity (G-154-3) BEFORE the atomic rename."""
    df = pd.DataFrame(rows, columns=["bg_id", "sequence", "position",
                                     "mut_aa", "score"])
    assert len(df) == ROWS_PER_PASS * len(exp_positions), \
        (bg_id, len(df), ROWS_PER_PASS * len(exp_positions))
    assert not df.duplicated(["position", "mut_aa"]).any(), bg_id
    assert set(int(p) for p in df.position.unique()) == set(exp_positions), \
        (bg_id, sorted(df.position.unique()), exp_positions)
    assert set(df.sequence) == {sequence}, bg_id
    assert set(df.bg_id) == {bg_id}, bg_id
    with open(tmp, "w") as fh:
        df.to_csv(fh, index=False)
    os.replace(tmp, path)


def score_positions(model, alphabet, bc, seq_str, seq_name, positions,
                    device):
    """One unbatched forward pass per position; returns (rows, pass_secs).

    rows carry seq_name (the --sequence label) in the `sequence` column,
    not the 56-aa string: every skip/manifest gate keys on the label.
    """
    from scripts.lib.esm_scoring import get_position_logprobs
    rows, pass_s = [], []
    for p in positions:
        t0 = time.perf_counter()
        scores = get_position_logprobs(model, alphabet, bc, seq_str, p,
                                       device)
        pass_s.append(time.perf_counter() - t0)
        for aa, sc in scores.items():
            rows.append(dict(bg_id=None, sequence=seq_name, position=p,
                             mut_aa=aa, score=sc))
    return rows, pass_s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="score/skip only this roster background_id")
    ap.add_argument("--limit-positions", type=int, default=None,
                    help="only first N expected positions (test mode)")
    ap.add_argument("--out-dir", default="data/processed/phase3/gb1")
    ap.add_argument("--sequence", choices=["assayed", "project"],
                    default="assayed")
    ap.add_argument("--limit-roster", type=int, default=None,
                    help="only first N backgrounds in roster (draw) order")
    ap.add_argument("--wt-arm-only", action="store_true",
                    help="score/skip only the WT arm file")
    args = ap.parse_args()

    t_start = time.time()
    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    banner(f"154 -- GB1 background scorer  N_BOOT={N_BOOT} SEED={SEED} "
           f"(both UNUSED: no bootstrap/randomness here)\n"
           f"sequence={args.sequence}  out_dir={args.out_dir}")

    # ------------------------------------------------------- input gates --
    seq, ros = load_inputs(args.sequence)
    out_dir_sequence_gate(out_dir, args.sequence)

    # ------------------------------------------------------- pre-scan -----
    todo_wt = False
    wt_final = out_dir / "wt_arm.csv"
    wt_exp = list(POSITIONS)
    if file_is_complete(wt_final, "WT", args.sequence, wt_exp):
        print(f"  SKIP wt_arm.csv: complete ({len(wt_exp)} x 19 = "
              f"{len(wt_exp) * 19} rows)")
    else:
        todo_wt = True

    todo = []
    n_skip = 0
    if not args.wt_arm_only:
        sub = ros.sort_values("draw_order")
        if args.only is not None:
            sub = sub[sub["background_id"] == args.only]
            if len(sub) != 1:
                gate_fail(f"--only {args.only} matched {len(sub)} roster "
                          f"rows (must be 1)")
        if args.limit_roster is not None:
            sub = sub.head(args.limit_roster)
        for r in sub.itertuples():
            exp = expected_positions(int(r.pos))
            if args.limit_positions is not None:
                exp = exp[:args.limit_positions]
            final = out_dir / f"bg_{r.background_id}.csv"
            if file_is_complete(final, r.background_id, args.sequence, exp):
                n_skip += 1
                print(f"  SKIP {r.background_id}: complete file "
                      f"({len(exp) * 19} rows expected)")
            else:
                todo.append((r, exp))
    n_planned_passes = (len(wt_exp) if todo_wt else 0) + \
        sum(len(e) for _, e in todo)
    print(f"  pre-scan: WT arm {'TO SCORE' if todo_wt else 'skip'}, "
          f"{n_skip} backgrounds complete, {len(todo)} to score; "
          f"{n_planned_passes} passes planned")
    if not todo_wt and not todo:
        print("Nothing to do.")
        return

    # ------------------------------------------------------- model --------
    if not CKPT.exists():
        gate_fail(f"G-154-5 local ESM-2 650M checkpoint missing: {CKPT} "
                  f"(this script never downloads)")
    import esm
    from scripts.lib.esm_scoring import get_device

    device = get_device()
    print(f"Using device: {device}")
    print(f"G-154-5 checkpoint present: {CKPT} ({CKPT.stat().st_size:,} "
          f"bytes); loading from local cache (never downloads)...",
          flush=True)
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    manifest = out_dir / "manifest.csv"
    all_pass_s = []
    n_files_done = 0
    t_run0 = time.time()
    total_files = (1 if todo_wt else 0) + len(todo)

    def write_manifest(file_, kind, bg_id, n_pos, n_rows, secs, med):
        row = dict(file=file_, kind=kind, bg_id=bg_id,
                   sequence=args.sequence, n_positions=n_pos, n_rows=n_rows,
                   seconds=round(secs, 3), median_pass_s=round(med, 4),
                   device=str(device))
        pd.DataFrame([row]).to_csv(manifest, mode="a",
                                   header=not manifest.exists(), index=False)

    # ------------------------------------------------------- WT arm -------
    if todo_wt:
        tmp = out_dir / ".wt_arm.csv.tmp"
        try:
            rows, pass_s = score_positions(model, alphabet, bc, seq,
                                           args.sequence, wt_exp, device)
            for r in rows:
                r["bg_id"] = "WT"
            all_pass_s.extend(pass_s)
            publish(wt_final, tmp, rows, "WT", args.sequence, wt_exp)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            print("ERROR: WT arm failed; no partial file published; "
                  "exiting nonzero")
            traceback.print_exc()
            sys.exit(1)
        med = sorted(pass_s)[len(pass_s) // 2]
        write_manifest("wt_arm.csv", "wt_arm", "WT", len(wt_exp), len(rows),
                       sum(pass_s), med)
        n_files_done += 1
        print(f"  scored WT arm: {len(wt_exp)} positions, {len(rows)} rows "
              f"in {sum(pass_s):.1f}s scoring ({med * 1000:.0f} ms/pass "
              f"median) | file {n_files_done}/{total_files}", flush=True)

    # ------------------------------------------------------- backgrounds ---
    for k, (r, exp) in enumerate(todo):
        bg_id = r.background_id
        own, wt_aa, mut_aa = int(r.pos), r.wt_aa, r.mut
        assert seq[own - 1] == wt_aa or (
            args.sequence == "project" and own == 2 and wt_aa == "Q"
            and seq[1] == "T"), (bg_id, seq[own - 1], wt_aa)  # decision S2
        bg_seq = seq[:own - 1] + mut_aa + seq[own:]
        assert bg_seq[own - 1] == mut_aa, (bg_id, bg_seq[own - 1], mut_aa)
        assert own not in exp, (bg_id, own)   # frozen G-2, structural

        tmp = out_dir / f".bg_{bg_id}.csv.tmp"
        final = out_dir / f"bg_{bg_id}.csv"
        t0 = time.time()
        try:
            rows, pass_s = score_positions(model, alphabet, bc, bg_seq,
                                           args.sequence, exp, device)
            for rr in rows:
                rr["bg_id"] = bg_id
            all_pass_s.extend(pass_s)
            publish(final, tmp, rows, bg_id, args.sequence, exp)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            print(f"ERROR: background {bg_id} failed; no partial file "
                  f"published; exiting nonzero (never continues past a "
                  f"half-written file)")
            traceback.print_exc()
            sys.exit(1)

        dt = time.time() - t0
        med = sorted(pass_s)[len(pass_s) // 2]
        write_manifest(final.name, "background", bg_id, len(exp), len(rows),
                       dt, med)
        n_files_done += 1
        elapsed = time.time() - t_run0
        avg = elapsed / max(n_files_done, 1)
        eta_s = avg * (total_files - n_files_done)
        print(f"  scored {bg_id}: {len(exp)} positions, {len(rows)} rows in "
              f"{dt:.1f}s ({dt / len(exp) * 1000:.0f} ms/pass) | file "
              f"{n_files_done}/{total_files}, elapsed {elapsed / 60:.1f}m, "
              f"ETA {eta_s / 60:.1f}m", flush=True)

    # ------------------------------------------------------- summary ------
    banner("154 SUMMARY")
    n_pass_total = len(all_pass_s)
    if n_pass_total:
        srt = sorted(all_pass_s)
        med = srt[len(srt) // 2]
        mean = sum(srt) / len(srt)
        print(f"passes timed this run: {n_pass_total} | median "
              f"{med:.4f} s/pass | mean {mean:.4f} s/pass")
        proj = STAGE_PASSES * med * PROJ_FACTOR
        print(f"A4e stage projection (informational): "
              f"({N_ROSTER} x 54 + 55) = {STAGE_PASSES} passes x "
              f"{med:.4f} s/pass x {PROJ_FACTOR} = {proj / 60:.1f} min "
              f"vs the 100-min stage budget "
              f"({'OVER' if proj > STAGE_BUDGET_S else 'within'} budget; "
              f"a projection over budget never shrinks the roster -- "
              f"frozen A8)")
    else:
        med = None
        print("no passes timed this run (everything was skipped)")
    print(f"files: {n_files_done} published/skipped-this-run; manifest -> "
          f"{manifest.relative_to(ROOT)}; out_dir={args.out_dir}; "
          f"sequence={args.sequence}")
    print("LIMITATIONS: masked-marginal log-odds on one model (650M) on one "
          "device; determinism across devices not claimed.\n"
          "  This script creates no statistic: it produces the two score "
          "tables script 155 joins.")
    print(f"wall {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    main()
