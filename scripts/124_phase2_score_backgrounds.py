"""Script 124 (Phase 2 session 2a, task G2) -- overnight background scorer.

PRE-REGISTERED: this docstring was written before the first run of this
script (PHASE2_EXECUTION.md, Task G2; binding text PHASE2_PREREG.md
frozen sections 3, 7, 8).  Per execution-doc rule 7 this script is NOT
edited after any Phase 2 score exists (the only scores it produces in
session 2a are test artifacts confined to data/processed/phase2_scratch/;
from Arnav's launch onward it is frozen -- a later bug would be fixed in
a NEW numbered script, with both reported).

WHAT IT IMPLEMENTS (frozen pins):
  PIN-4 (scoring): scripts/lib/esm_scoring.py::get_position_logprobs +
    get_device exactly as scripts 63/69/82 do -- ESM-2
    esm2_t33_650M_UR50D, eval mode, torch.no_grad (inside the lib fn),
    ONE UNBATCHED forward pass per (background, position), masked-
    marginal, all 19 non-wild-type substitutions from that pass.  No
    batching, no reimplementation.  Weights come from the local torch.hub
    cache; if a download were ever attempted this script stops (never
    downloads).
  PIN-5 (positions scored): every frame position except the background's
    own position (rows with target == background position are never
    produced; frozen G-C).  Frame = unique positions of the non-null
    (delta_esm, own_e_b) rows of task32_analysis_table.csv (654; same
    construction as scripts 122/123).  Arm S: 654 positions; Arms V/G:
    653.  Expected rows: 654*19 = 12,426 (S) and 653*19 = 12,407 (V/G).
  PIN-6 (background sequence): WT sequence from
    scripts.lib.sequence.load_sequence (data/raw/P42898.fasta) with the
    single roster substitution applied; the WT residue at the background
    position is asserted equal to the roster wt_aa BEFORE substituting,
    and the substituted residue is asserted after (the corrected reading
    of PIN-6 -- see PHASE2_LOG.md [G1] flag 1 for why the mutated-
    sequence reading is impossible).

OUTPUT CONTRACT (execution doc G2, followed literally):
  One file per background, written ONLY after all of that background's
  positions are done, ATOMICALLY: rows are first accumulated in memory,
  then written to <out-dir>/.bg_<bg_id>.csv.tmp, then os.replace()d to
  <out-dir>/bg_<bg_id>.csv.  Columns exactly: bg_id, position, mut_aa,
  score  (the execution doc's schema; note it differs from cached
  task82_ae_raw.csv's score_bg -- disclosed, not a guess; the analysis
  script maps accordingly).
  After each background: append bg_id, n_positions, n_rows, seconds,
  device to <out-dir>/manifest.csv (header written if the file is new;
  skipped backgrounds append nothing).
  Per-background time, ms/pass and a running ETA are printed.
  Any exception: the current .tmp is removed, the traceback plus an
  "ERROR" line are printed, and the process EXITS NONZERO -- it never
  continues past a half-written file.

SKIP/RESUME RULE: a background whose FINAL file already exists with the
expected row count (positions x 19 for the current flags) is skipped.
Strengthening (disclosed; can only fail earlier, never pass a bad file):
the skip check also requires the file's position set to equal the
expected position set and no duplicate (position, mut_aa) pairs.  A
.tmp file is NEVER treated as completion.

CLI (tests never touch the real output directory):
  --only <bg_id>          score/skip just that roster background
  --limit-positions N     only the first N expected positions (sorted);
                           row expectation becomes N x 19; a file written
                           with --limit-positions is therefore INCOMPLETE
                           for a later full run (row count mismatch) and
                           will be re-scored and overwritten then -- by
                           design, and only test runs use this flag
  --out-dir DIR           default data/processed/phase2

IN-SCRIPT CHECKS (failure -> print + exit 1, never loosened):
  roster has 96 rows with 96 unique bg_ids; FASTA length 656; every
  scored background's WT assert (PIN-6); the row count and position set
  actually written are asserted equal to expectation BEFORE the atomic
  rename.

CONVENTION: N_BOOT / SEED are read and printed per session convention
but are UNUSED -- this script performs no bootstrap, no permutation and
no randomness (the Arm G draw already happened, pinned, in script 123).

TEST PLAN (task G2, all inside data/processed/phase2_scratch/):
  (a) --only A222_C --limit-positions 5        -> writes 95 rows
  (b) repeat (a)                               -> skipped, untouched
  (c) fake .bg_AV_5.csv.tmp left in scratch    -> not treated as
      completion; overwritten by the real write; re-created fake .tmp
      while bg_AV_5.csv is complete -> skip ignores it
  (d) row counts asserted exactly 5 x 19 = 95

Usage:
  venv/bin/python3 scripts/124_phase2_score_backgrounds.py
  venv/bin/python3 scripts/124_phase2_score_backgrounds.py \\
      --only A222_C --limit-positions 5 --out-dir data/processed/phase2_scratch

LIMITATIONS (AGENTS 6): scores are masked-marginal log-odds on one
model (650M) on one device (mps here); determinism across devices is
NOT claimed -- frozen gate G-B's 1e-6 reproduction (PHASE2_LOG [G1])
covers same-device reproduction, and session 2b's A3 extends it
descriptively to every cached background.  No inference of any kind
lives in this script.
"""

import argparse
import os
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
# Project convention (scripts 07/14/82/110/115/116/...): import
# scripts.lib.* when invoked as `python scripts/NN_*.py` (sys.path[0] is
# scripts/, not the repo root).  Added after the first test attempt
# crashed on ModuleNotFoundError BEFORE producing any score -- disclosed
# in PHASE2_LOG.md [G2]; no Phase 2 score existed at the time.
sys.path.insert(0, str(ROOT))


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def expected_positions(frame, own):
    """PIN-5: every frame position except the background's own."""
    return [p for p in frame if p != own]


def file_is_complete(path, bg_id, exp_positions):
    """Skip check: final file exists with expected rows/positions and no
    duplicate (position, mut_aa) pairs.  .tmp files never count."""
    if not path.exists():
        return False
    try:
        df = pd.read_csv(path)
    except Exception:
        return False
    need = 19 * len(exp_positions)
    return (len(df) == need
            and set(df.bg_id.astype(str)) == {bg_id}
            and set(int(p) for p in df.position.unique())
            == set(exp_positions)
            and not df.duplicated(["position", "mut_aa"]).any())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="score/skip only this bg_id")
    ap.add_argument("--limit-positions", type=int, default=None,
                    help="only first N expected positions (test mode)")
    ap.add_argument("--out-dir", default="data/processed/phase2")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    banner(f"124 -- Phase 2 background scorer  N_BOOT={N_BOOT} "
           f"SEED={SEED} (both UNUSED: no bootstrap/randomness here)  "
           f"out_dir={args.out_dir}")

    # ------------------------------------------------------- roster ------
    roster = pd.read_csv(ROOT / "data/processed/phase2_arm_roster.csv")
    if len(roster) != 96 or roster.bg_id.nunique() != 96:
        print(f"ERROR: roster {len(roster)} rows / "
              f"{roster.bg_id.nunique()} unique (expect 96/96)")
        sys.exit(1)
    if args.only is not None:
        roster = roster[roster.bg_id == args.only]
        if len(roster) != 1:
            print(f"ERROR: --only {args.only} matched {len(roster)} "
                  "roster rows")
            sys.exit(1)

    # ------------------------------------------------- frame + sequence --
    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    use = atlas.dropna(subset=["delta_esm", "own_e_b"])
    frame = sorted(int(p) for p in use.position.unique())
    if len(frame) != 654:
        print(f"ERROR: frame {len(frame)} positions (expect 654)")
        sys.exit(1)
    from scripts.lib.sequence import load_sequence, verify_sequence
    wt_seq = load_sequence(str(ROOT / "data/raw/P42898.fasta"))
    verify_sequence(wt_seq)

    print(f"  roster rows to process: {len(roster)}; frame = {len(frame)}")
    print(f"  skip logic checks FINAL files only; .tmp never counts")

    # ------------------------------------------------------- pre-scan ----
    todo = []
    n_skip = 0
    for r in roster.itertuples():
        exp = expected_positions(frame, int(r.position))
        if args.limit_positions is not None:
            exp = exp[:args.limit_positions]
        final = out_dir / f"bg_{r.bg_id}.csv"
        if file_is_complete(final, r.bg_id, exp):
            n_skip += 1
            print(f"  SKIP {r.bg_id}: complete file already exists "
                  f"({len(exp) * 19} rows expected)")
        else:
            todo.append((r, exp))
    print(f"  pre-scan: {n_skip} complete, {len(todo)} to score")
    if not todo:
        print("Nothing to do.")
        return

    # ------------------------------------------------------- scoring -----
    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    device = get_device()
    print(f"Using device: {device}")
    print("Loading ESM-2 650M from the local torch.hub cache "
          "(never downloads; stops if a download were attempted)...",
          flush=True)
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    manifest = out_dir / "manifest.csv"
    t_run0 = time.time()
    n_done_before = n_skip
    total_planned = len(todo) + n_skip

    for k, (r, exp) in enumerate(todo):
        bg_id = r.bg_id
        own, wt_aa, mut_aa = int(r.position), r.wt_aa, r.mut_aa
        # PIN-6: WT residue check BEFORE substitution, mut check after.
        assert wt_seq[own - 1] == wt_aa, (bg_id, wt_seq[own - 1], wt_aa)
        bg_seq = wt_seq[:own - 1] + mut_aa + wt_seq[own:]
        assert bg_seq[own - 1] == mut_aa, (bg_id, bg_seq[own - 1], mut_aa)

        tmp = out_dir / f".bg_{bg_id}.csv.tmp"
        final = out_dir / f"bg_{bg_id}.csv"
        t0 = time.time()
        try:
            rows = []
            for p in exp:
                scores = get_position_logprobs(model, alphabet,
                                               batch_converter, bg_seq,
                                               p, device)
                for m, sc in scores.items():
                    rows.append(dict(bg_id=bg_id, position=p, mut_aa=m,
                                     score=sc))
            # integrity BEFORE the atomic rename
            assert len(rows) == 19 * len(exp), (bg_id, len(rows),
                                                19 * len(exp))
            assert len({(x["position"], x["mut_aa"]) for x in rows}) \
                == len(rows), bg_id
            with open(tmp, "w") as fh:
                pd.DataFrame(rows, columns=["bg_id", "position",
                                            "mut_aa", "score"]).to_csv(
                                                fh, index=False)
            os.replace(tmp, final)          # atomic publish
        except Exception:
            if tmp.exists():
                tmp.unlink()
            print(f"ERROR: background {bg_id} failed; no partial file "
                  f"published; exiting nonzero (never continues past a "
                  f"half-written file)")
            traceback.print_exc()
            sys.exit(1)

        dt = time.time() - t0
        row = dict(bg_id=bg_id, n_positions=len(exp), n_rows=len(rows),
                   seconds=round(dt, 3), device=str(device))
        hdr = not manifest.exists()
        pd.DataFrame([row]).to_csv(manifest, mode="a", header=hdr,
                                   index=False)
        n_done = n_done_before + k + 1
        elapsed = time.time() - t_run0
        avg = elapsed / (k + 1)
        eta_s = avg * (total_planned - n_done)
        print(f"  scored {bg_id}: {len(exp)} positions, {len(rows)} rows "
              f"in {dt:.1f}s ({dt / len(exp) * 1000:.0f} ms/pass) | "
              f"run {n_done}/{total_planned}, elapsed {elapsed / 60:.1f}m, "
              f"ETA {eta_s / 3600:.2f}h", flush=True)

    print(f"\nDone. Scored {len(todo)}, skipped {n_skip}; "
          f"wall { (time.time() - t_run0) / 60:.1f}m; "
          f"manifest -> {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
