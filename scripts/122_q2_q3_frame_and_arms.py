"""Script 122 (Phase 1b, tasks Q2 + Q3) -- held-out position set H and
arm roster counts.  READ-ONLY over the real files; writes nothing;
NO MODEL SCORING (cached CSVs + the repo's wild-type FASTA only).
PRE-REGISTERED: this docstring was written before the first run of this
script (PHASE1B_PLACEBO_FOLLOWUP.md, Part B).

NO RANDOMNESS, NO SELECTION ANYWHERE: Q3 is an enumeration task
("enumerate only, choose nothing"; selection rules are frozen in
Appendix A).  This script contains no rng and draws no backgrounds.
N_BOOT/SEED are read per the session convention but are UNUSED (no
bootstrap statistic exists here); the mandated smoke and full runs are
therefore identical apart from the banner label, both executed,
disclosed.

Q2 -- HELD-OUT POSITIONS (pre-registered construction):
  frame  = positions with >=1 usable row in
           data/processed/task32_analysis_table.csv after dropna on
           (delta_esm, own_e_b)  [the 654-position analysis frame].
  AE set = unique positions in data/processed/task82_ae_raw.csv (120).
  W set  = unique positions in data/processed/task69_w2_bg_raw.csv (120).
  H      = frame MINUS (AE set UNION W set).
  Reported: |frame|, |AE|, |W|, |AE n W|, |AE u W|, |H|, and the number
  of usable variants (rows of the dropna'd frame) whose position is in
  H.  Also printed: usable rows at the held-in positions (frame
  minus H) so the row accounting closes: usable(H) +
  usable(frame \ H) = 10,757.
  GATES (failure -> `GATE FAIL: ...` + exit 1, no retry):
    Q2-G1 |frame| == 654, |AE| == 120, |W| == 120, usable rows == 10757.
    Q2-G2 |AE n W| == 41 (the value script 109's G1 recorded and
          gated from these same files).
    Q2-G3 position 222 NOT in frame, NOT in AE, NOT in W (hence not in
          H).  Citations printed by the script: PHASE1_LOG.md [L1]
          (entry starts line 1517) established 0 rows at 222 in every
          analysis table ("rows at position 222: base = 0, task77 all
          = 0, task77 analysis = 0"); PHASE1_LOG.md [K1] (entry starts
          line 1348; quote at lines 1462-1463) independently verified
          "222 in AE grid: False | 222 in W grid: False".

Q3 -- ARM ROSTER COUNTS (pre-registered construction):
  N_V = number of positions p with p in the 654-position frame,
        p != 222, and wild-type residue Ala at p, read from THE
        WILD-TYPE SEQUENCE IN THE REPO (data/raw/P42898.fasta,
        residue p = FASTA index p-1, mapping previously verified
        12,445/12,445 against esm2_wt_scores.csv in P1).
  Reported: N_V, the sorted list of those positions (enumeration, not
  selection), and whether N_V > 60 (the count alone decides whether
  Appendix A's frozen seed-0 cap rule would apply -- reported, never
  executed here).
  GATES (failure -> exit 1):
    Q3-G1 FASTA residue vs esm2_wt_scores.csv wt_aa agrees at EVERY
          frame position (any disagreement is printed and fails the
          gate: the two sources for "wild-type sequence" must match).
    Q3-G2 222 not counted (explicit; it is not in the frame anyway).
  Cross-check printed: Q1 computed N_V = 38 inline to fill its cost
  table; this script re-derives it independently and the two must
  agree (a mismatch would be reported plainly and gated).

LIMITATIONS (printed with the output, AGENTS 6):
  * counts only; no inference; no scoring; nothing here selects a
    background (Appendix A freezes selection for Phase 2).

Usage (session convention; both runs executed, identical apart from
the banner):
  N_BOOT=300   venv/bin/python3 scripts/122_q2_q3_frame_and_arms.py   # smoke
  N_BOOT=10000 venv/bin/python3 scripts/122_q2_q3_frame_and_arms.py   # full
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]

Q1_NV = 38          # N_V computed inline in Q1 (cross-check target)
INTERSECTION_41 = 41  # F1/script-109 recorded AE n W

t0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"Q2+Q3 -- held-out positions and arm roster counts "
           f"(script 122)  N_BOOT={N_BOOT} SEED={SEED} "
           f"(no bootstrap, no randomness, no selection)")

    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    use = atlas.dropna(subset=["delta_esm", "own_e_b"]).copy()
    ae = pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv",
                     usecols=["position"])
    w = pd.read_csv(ROOT / "data/processed/task69_w2_bg_raw.csv",
                    usecols=["position"])
    frame = set(use.position.unique())
    ae_set = set(ae.position.unique())
    w_set = set(w.position.unique())

    # ------------------------------------------------------------ Q2 -----
    banner("Q2 -- HELD-OUT POSITIONS", "-")
    held_in = frame & (ae_set | w_set)
    H = frame - (ae_set | w_set)
    usable_H = int((use.position.isin(H)).sum())
    usable_in = int((use.position.isin(held_in)).sum())
    print(f"  |frame|  = {len(frame)} (expect 654)")
    print(f"  |AE set| = {len(ae_set)} (expect 120)")
    print(f"  |W set|  = {len(w_set)} (expect 120)")
    print(f"  |AE n W| = {len(ae_set & w_set)} (F1/script-109 recorded 41)")
    print(f"  |AE u W| = {len(ae_set | w_set)}")
    print(f"  |H| = |frame \\ (AE u W)| = {len(H)}")
    print(f"  usable variants in H = {usable_H}")
    print(f"  usable variants at held-in frame positions = {usable_in}")
    print(f"  row accounting: {usable_H} + {usable_in} = "
          f"{usable_H + usable_in} (frame total = {len(use)}; expect 10757)")
    print(f"  H positions (sorted): {sorted(H)}")

    if len(frame) != 654:
        gfail(f"Q2-G1 |frame| = {len(frame)}")
    if len(ae_set) != 120 or len(w_set) != 120:
        gfail(f"Q2-G1 |AE| = {len(ae_set)} |W| = {len(w_set)}")
    if len(use) != 10757:
        gfail(f"Q2-G1 usable rows = {len(use)}")
    if len(ae_set & w_set) != INTERSECTION_41:
        gfail(f"Q2-G2 |AE n W| = {len(ae_set & w_set)}")
    bad = {s: (222 in s) for s, nm in [(frame, "frame"), (ae_set, "AE"),
                                       (w_set, "W"), (H, "H")] if 222 in s}
    print("  citations: PHASE1_LOG.md [L1] (line 1517): \"rows at position "
          "222: base = 0, task77 all = 0, task77 analysis = 0\"; "
          "PHASE1_LOG.md [K1] (lines 1462-1463): \"independently verified "
          "(`222 in AE grid: False | 222 in W grid: False`\")")
    if bad:
        gfail(f"Q2-G3 position 222 present in: {bad}")
    print("  Q2-G1 PASS  Q2-G2 PASS  Q2-G3 PASS (222 excluded from every "
          "set as a target position)")

    # ------------------------------------------------------------ Q3 -----
    banner("Q3 -- ARM ROSTER COUNTS (enumerate only, choose nothing)", "-")
    seq = "".join(l.strip() for l in
                  open(ROOT / "data/raw/P42898.fasta")
                  if not l.startswith(">"))
    wt = pd.read_csv(ROOT / "data/processed/esm2_wt_scores.csv")
    wt_by_pos = wt.groupby("position").wt_aa.first().to_dict()
    disagree = [p for p in sorted(frame)
                if wt_by_pos.get(p, None) != seq[p - 1]]
    print(f"  FASTA vs esm2_wt_scores.csv agreement over all "
          f"{len(frame)} frame positions: {len(frame) - len(disagree)}/"
          f"{len(frame)}")
    if disagree:
        gfail(f"Q3-G1 FASTA/table WT disagreement at frame positions: "
              f"{disagree}")
    N_V_pos = sorted(p for p in frame if p != 222 and seq[p - 1] == "A")
    print(f"  Q3-G2: 222 in frame = {222 in frame} -> not counted")
    print(f"  alanine positions in frame != 222 (N_V) = {len(N_V_pos)}")
    print(f"  sorted positions: {N_V_pos}")
    print(f"  N_V > 60 ? {len(N_V_pos) > 60} (reported only; the frozen "
          f"Appendix A cap rule is decided by this count alone and is "
          f"NOT executed here)")
    print(f"  cross-check vs Q1's inline count: Q1 = {Q1_NV}, "
          f"Q3 = {len(N_V_pos)} -> "
          f"{'AGREE' if len(N_V_pos) == Q1_NV else 'DISAGREE (report plainly)'}")
    if len(N_V_pos) != Q1_NV:
        gfail(f"Q3-G2 cross-check: Q3 N_V = {len(N_V_pos)} vs Q1 {Q1_NV}")

    banner("SUMMARY", "-")
    print(f"  Q2: frame 654, AE 120, W 120, overlap 41, |H| = {len(H)}, "
          f"usable variants in H = {usable_H}; 222 excluded everywhere")
    print(f"  Q3: N_V = {len(N_V_pos)} (<= 60 -> no cap rule would "
          f"trigger); enumeration only, no backgrounds selected")
    print("\nLIMITATIONS (AGENTS 6): counts only; no scoring; no "
          "inference; no selection (Appendix A freezes selection).")
    print(f"Elapsed {time.time() - t0:.1f}s")
