"""Script 123 (Phase 2 session 2a, task R1) -- Phase 2 ARM ROSTER.

PRE-REGISTERED: this docstring was written before the first run of this
script (PHASE2_EXECUTION.md, Task R1; binding text PHASE2_PREREG.md
frozen sections 3 and 7).  It is not edited after its first run.

WHAT THIS DOES (no model; no torch/esm import anywhere):
Builds data/processed/phase2_arm_roster.csv with columns
bg_id, arm, position, wt_aa, mut_aa for all 96 Phase 2 backgrounds,
per PIN-1..PIN-3 of PHASE2_EXECUTION.md section 2 (implementation pins
resolve ambiguity; they change no frozen rule):

  PIN-1 (Arm G draw, pinned): rng = numpy.random.default_rng(0);
    pool = sorted frame positions (654; 222 is not in the frame);
    pos = rng.choice(pool, size=40, replace=False); then, for each
    position IN THE ORDER DRAWN, mut = rng.choice(sorted 19 one-letter
    residues excluding the wild-type residue at that position).
    WT residue from data/raw/P42898.fasta, residue p = FASTA index
    p-1 (mapping verified in Phase 1b P1/Q3: 12,445/12,445 against
    esm2_wt_scores.csv).  The seed is PINNED AT 0 by PIN-1; the SEED
    env var is printed for the session banner but does NOT affect
    this draw.
  PIN-2 (duplicates): an Arm G entry with the same position AND the
    same mutant as an Arm V entry keeps BOTH roster rows as drawn
    (both are then scored); the collision is disclosed, not removed.
    Not a gate -- reporting only, per the pin.
  PIN-3 (arms): Arm S = the 18 backgrounds A222_X, X among the 19
    non-wild-type residues at 222 excluding V (A222V itself is NOT
    rescored -- its full-frame arm is cached); Arm V = A->V at every
    non-222 alanine position in the frame (Q3: 38 <= 60, so the frozen
    section 3 cap rule does not trigger; all 38 used); Arm G = 40 per
    PIN-1.  Total 96.  bg_ids: A222_<X>, AV_<pos>, G_<wt><pos><mut>.

ROW ORDER (assumption, logged; no rule depends on it): Arm S sorted by
bg_id, then Arm V sorted by position, then Arm G in draw order.  G1's
"first Arm S row, first Arm V row, last Arm V row" therefore mean
A222_C, AV_5, AV_655 under this ordering.

FRAME (same construction as script 122 Q2, cached CSVs only): rows of
data/processed/task32_analysis_table.csv with non-null (delta_esm,
own_e_b); frame = its unique positions (expect 654).

GATES (failure -> "R1-Gx FAIL: ..." + exit 1; thresholds never
loosened, never re-run to force a pass):
  R1-G1 arm counts 18 / 38 / 40, total 96.
  R1-G2 every roster wt_aa equals the FASTA residue at its position
        (checked row by row on all 96 rows), AND the FASTA agrees
        with esm2_wt_scores.csv wt_aa at every one of the 654 frame
        positions -- two independent sources for "wild-type sequence"
        (same cross-check as script 122's Q3-G1).
  R1-G3 no Arm V and no Arm G background sits at position 222, and
        222 is not in the frame.  ASSUMPTION (logged): the execution
        doc's gate wording "no position is 222" cannot include Arm S
        rows -- Arm S backgrounds are BY DEFINITION A222X at position
        222 (frozen section 3 / PIN-3), so the roster records
        position=222 for them and the gate is read as applying to the
        null arms (V and G) and to the frame.  Also asserted here:
        no A222_V row exists (A222V is not rescored, PIN-3).
  R1-G4 Arm V positions equal Q3's list of 38 exactly -- the list as
        read off disk from PHASE1B_Q3_FULL_OUTPUT.txt (Phase 1b).
  R1-G5 Arm G: all 40 positions distinct, all in the frame, none = 222;
        every Arm G mutant != its WT residue (candidates are the 19
        non-WT residues only).
  PIN-2 collisions are REPORTED, never dropped (reporting, not a gate).

BEFORE-ANY-SCORING CHECK: prints whether data/processed/phase2/ exists
and how many bg_*.csv it holds (expected 0 -- the roster must exist on
disk before any Phase 2 score, frozen section 3 "drawn and written to
disk before any scoring").

DETERMINISM: no bootstrap and no inference in this script; N_BOOT and
SEED are read per the session convention but UNUSED for the draw
(PIN-1 pins default_rng(0)).  Smoke and full runs are identical apart
from the banner; both are executed and disclosed, and the roster
sha256 must be identical across them (printed by the script and
re-checked externally with shasum -a 256).

Usage (session convention):
  N_BOOT=300   venv/bin/python3 scripts/123_phase2_arm_roster.py   # smoke
  N_BOOT=10000 venv/bin/python3 scripts/123_phase2_arm_roster.py   # full

LIMITATIONS (AGENTS 6): deterministic enumeration and one pinned
fitness-blind draw only; no inference; no scoring; all arms are fixed
before scoring by construction (frozen section 3: fitness-blind).
"""

import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]

# Same literal as scripts/lib/esm_scoring.py:6 AA_LIST (not imported:
# this script must not pull torch/esm in, per the execution doc).
AA20 = "ACDEFGHIKLMNPQRSTVWY"

# Q3's 38 non-222 frame alanine positions, exactly as printed on disk
# in docs/tasks/phase1b-placebo-followup/PHASE1B_Q3_FULL_OUTPUT.txt
# ("sorted positions: ...", cross-checked there Q1 = Q3 = 38 AGREE).
Q3_NV_POS = [5, 19, 70, 73, 84, 85, 98, 113, 116, 145, 155, 175, 195,
             204, 209, 220, 233, 242, 292, 293, 302, 311, 328, 350,
             353, 368, 396, 461, 462, 511, 522, 524, 551, 558, 587,
             589, 650, 655]

t0 = time.time()


def gfail(msg):
    print(f"R1 GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"R1 -- Phase 2 arm roster (script 123)  N_BOOT={N_BOOT} "
           f"SEED={SEED} (no bootstrap, no model; Arm G draw is PINNED "
           f"at default_rng(0) by PIN-1, not by SEED)")

    # ---------------------------------------------------------- frame -----
    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    use = atlas.dropna(subset=["delta_esm", "own_e_b"]).copy()
    frame = sorted(int(p) for p in use.position.unique())
    print(f"  usable rows = {len(use)} (expect 10757)")
    print(f"  |frame| = {len(frame)} (expect 654); 222 in frame = "
          f"{222 in frame}")
    if len(frame) != 654:
        gfail(f"R1-frame |frame| = {len(frame)} (expect 654)")
    if len(use) != 10757:
        gfail(f"R1-frame usable rows = {len(use)} (expect 10757)")
    if 222 in frame:
        gfail("R1-frame position 222 is in the frame")

    # ---------------------------------------------------------- FASTA -----
    seq = "".join(l.strip() for l in
                  open(ROOT / "data/raw/P42898.fasta")
                  if not l.startswith(">"))
    print(f"  FASTA length = {len(seq)}; residue p = FASTA index p-1")

    wt = pd.read_csv(ROOT / "data/processed/esm2_wt_scores.csv")
    wt_by_pos = wt.groupby("position").wt_aa.first().to_dict()
    disagree = [p for p in frame if wt_by_pos.get(p, None) != seq[p - 1]]

    # --------------------------------------------------------- Arm S -----
    # PIN-3: the 18 A222_X, X among the 19 non-WT residues at 222
    # excluding V (A222V itself is not rescored).
    s_muts = sorted(set(AA20) - {"A", "V"})     # WT at 222 is Ala
    rows = [{"bg_id": f"A222_{x}", "arm": "S", "position": 222,
             "wt_aa": seq[221], "mut_aa": x} for x in s_muts]

    # --------------------------------------------------------- Arm V -----
    # Q3 construction re-derived independently here: frame alanine
    # positions != 222 (must equal Q3_NV_POS -- gate R1-G4).
    nv_pos = sorted(p for p in frame if p != 222 and seq[p - 1] == "A")
    rows += [{"bg_id": f"AV_{p}", "arm": "V", "position": p,
              "wt_aa": seq[p - 1], "mut_aa": "V"} for p in nv_pos]

    # --------------------------------------------------------- Arm G -----
    # PIN-1, verbatim: default_rng(0); choice over sorted frame
    # positions, size 40, replace=False; then per position in drawn
    # order a choice over the sorted 19 non-WT residues.
    rng = np.random.default_rng(0)
    pool = np.array(frame)                      # sorted frame positions
    drawn = rng.choice(pool, size=40, replace=False)
    g_rows = []
    for p in drawn:
        p = int(p)
        wt_p = seq[p - 1]
        cands = sorted(a for a in AA20 if a != wt_p)   # 19 residues
        assert len(cands) == 19, (p, wt_p, len(cands))
        mut = str(rng.choice(cands))
        g_rows.append({"bg_id": f"G_{wt_p}{p}{mut}", "arm": "G",
                       "position": p, "wt_aa": wt_p, "mut_aa": mut})
    rows += g_rows

    # ------------------------------------------------- assemble + write ---
    df = pd.DataFrame(rows, columns=["bg_id", "arm", "position",
                                     "wt_aa", "mut_aa"])
    out = ROOT / "data/processed/phase2_arm_roster.csv"
    df.to_csv(out, index=False)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"  wrote {out.relative_to(ROOT)}  ({len(df)} rows)")
    print(f"  roster sha256 (computed in-script) = {sha}")

    phase2_dir = ROOT / "data/processed/phase2"
    n_bg = len(list(phase2_dir.glob("bg_*.csv"))) if phase2_dir.exists() \
        else 0
    print(f"  before-any-scoring check: data/processed/phase2/ exists = "
          f"{phase2_dir.exists()}, bg_*.csv files = {n_bg} (expect 0)")

    # ------------------------------------------------------------ gates ---
    banner("R1 GATES", "-")
    counts = df.arm.value_counts().to_dict()
    print(f"  counts by arm = {counts} (expect S=18, V=38, G=40)")
    if counts.get("S", 0) != 18 or counts.get("V", 0) != 38 \
            or counts.get("G", 0) != 40 or len(df) != 96:
        gfail(f"R1-G1 counts {counts}, total {len(df)}")
    print("  R1-G1 PASS (18 / 38 / 40, total 96)")

    bad_rows = [r for r in df.itertuples()
                if r.wt_aa != seq[r.position - 1]]
    print(f"  wt_aa == FASTA residue: {len(df) - len(bad_rows)}/{len(df)} "
          f"roster rows")
    print(f"  FASTA vs esm2_wt_scores.csv agreement over all "
          f"{len(frame)} frame positions: {len(frame) - len(disagree)}/"
          f"{len(frame)}")
    if bad_rows:
        gfail(f"R1-G2 roster wt_aa != FASTA at {bad_rows}")
    if disagree:
        gfail(f"R1-G2 FASTA/table WT disagreement at frame positions: "
              f"{disagree}")
    print("  R1-G2 PASS")

    vg_at_222 = df[(df.arm.isin(["V", "G"])) & (df.position == 222)]
    has_a222v = bool((df.bg_id == "A222_V").sum())
    print(f"  Arm V/G rows at position 222 = {len(vg_at_222)}; "
          f"222 in frame = {222 in frame}; A222_V row present = "
          f"{has_a222v}")
    print("  (assumption logged: 'no position is 222' is read as "
          "applying to the null arms V/G and to the frame -- Arm S rows "
          "are A222X by frozen section 3, position=222 by definition)")
    if len(vg_at_222) or 222 in frame or has_a222v:
        gfail("R1-G3 222 present where it must not be "
              f"(vg_at_222={len(vg_at_222)}, in_frame={222 in frame}, "
              f"A222_V={has_a222v})")
    print("  R1-G3 PASS")

    arm_v = sorted(df[df.arm == "V"].position.astype(int).tolist())
    print(f"  Arm V positions == Q3's 38-list: {arm_v == Q3_NV_POS}")
    print(f"    Arm V = {arm_v}")
    if arm_v != Q3_NV_POS:
        gfail(f"R1-G4 Arm V {arm_v} != Q3 {Q3_NV_POS}")
    print("  R1-G4 PASS")

    gpos = df[df.arm == "G"].position.astype(int).tolist()
    print(f"  Arm G: n = {len(gpos)}, distinct = {len(set(gpos))}, "
          f"all in frame = {set(gpos) <= set(frame)}, 222 among them = "
          f"{222 in gpos}, mut == wt rows = "
          f"{int((df[df.arm == 'G'].mut_aa == df[df.arm == 'G'].wt_aa).sum())}")
    if len(set(gpos)) != 40 or not set(gpos) <= set(frame) \
            or 222 in gpos or \
            (df[df.arm == "G"].mut_aa == df[df.arm == "G"].wt_aa).any():
        gfail("R1-G5 Arm G position/mutant invariant broken")
    print("  R1-G5 PASS")

    # ------------------------------------------------------- PIN-2 -------
    banner("PIN-2 COLLISION CHECK (report only, never dropped)", "-")
    v_keys = {(int(r.position), r.mut_aa) for r in
              df[df.arm == "V"].itertuples()}
    coll = [r for r in df[df.arm == "G"].itertuples()
            if (int(r.position), r.mut_aa) in v_keys]
    print(f"  Arm G rows with same position AND mutant as an Arm V row: "
          f"{len(coll)}")
    for r in coll:
        print(f"    COLLISION: {r.bg_id} (pos {r.position}, "
              f"{r.wt_aa}->{r.mut_aa}) duplicates AV_{r.position}")
    if not coll:
        print("    none")

    # ------------------------------------------------- full roster print --
    banner("FULL ROSTER (96 rows, verbatim)", "-")
    for r in df.itertuples():
        print(f"  {r.bg_id:>10s}  arm={r.arm}  pos={r.position:>3d}  "
              f"{r.wt_aa}->{r.mut_aa}")

    banner("SUMMARY", "-")
    print(f"  96 backgrounds written to "
          f"data/processed/phase2_arm_roster.csv BEFORE any scoring "
          f"(bg_*.csv = {n_bg})")
    print(f"  roster sha256 = {sha}")
    print("  gates: R1-G1 PASS  R1-G2 PASS  R1-G3 PASS  R1-G4 PASS  "
          "R1-G5 PASS")
    print(f"  PINs used: PIN-1 (draw, default_rng(0)), PIN-2 "
          f"(collisions reported: {len(coll)}), PIN-3 (arms/bg_ids)")
    print("\nLIMITATIONS (AGENTS 6): deterministic enumeration plus one "
          "pinned fitness-blind draw; no inference; no scoring; row "
          "order assumption logged in the docstring.")
    print(f"Elapsed {time.time() - t0:.1f}s")
