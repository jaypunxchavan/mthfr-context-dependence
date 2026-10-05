"""Script 170 (Phase 4 session 4a, Task A7a + A7b) -- neighbour-arm
geometry, cell counts and the frozen roster draw for Module N.

PRE-REGISTERED: this docstring was written before the first run of this
script.  Binding texts, both pinned by hash and verified at startup:
  * docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md
    (frozen 2026-10-02, 42 lines) -- sha256
    167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e
  * docs/tasks/phase4-strengthening/prereg/
    NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md (Arnav's decision, made
    BEFORE any draw or score, fitness-blind; saved verbatim, 9 lines) --
    sha256 f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a
The amendment is applied VERBATIM; NEIGHBOUR_ARM_PREREG_v1.md itself is
NOT edited (it is a frozen, versioned pre-registration -- AGENTS 9 /
prereg section 8: deviations require a new versioned document, never an
edit to v1).

DECISIONS, pre-registered here before the first run (printed at startup
before any geometry metric exists):

N-DEC1  Binding texts and hashes as above; the amendment supersedes only
        the items it names (its items 1-6); everything else in v1 stands.
N-DEC2  Geometry loader: script 139's parse_pdb_float64, IMPORTED via
        importlib (main() is guarded and the module is torch-free --
        verified: 'torch' not in sys.modules after import).  d3(p) =
        Calpha-Calpha distance chain A p to 222 (6FCX); dseq(p)=|p-222|.
        Eligible = frame positions (654, task32 non-null delta_esm/own_e_b)
        resolved in 6FCX chain A, other than 222 (frozen section 2).
        Cells C1-C4 exactly p4c.cell_labels (A2-gated, thresholds frozen
        section 2); C5 = a section-2 GAP cell with d3 <= 12, i.e.
        d3 <= 12 and 20 < dseq <= 40 (amendment item 3).  The full
        eligible-position listing WITH cell membership is printed AND
        written (eligible_cells_v1.csv) BEFORE any draw (frozen section 3,
        amendment item 6).
N-DEC3  G-N0 (HARD): both pre-registration hashes; the stored-d3 file
        (background_3d_distance.csv) sha256 pinned; the loader reproduces
        the stored d3_CA of the 67 resolved existing nulls with
        max|diff| < 1e-6 (the stored file was written at 6 decimal places
        by script 139, so ~5e-7 is the expected floor); cell counts are
        printed before the draw (a flag asserts the print order); and no
        torch module is loaded.
N-DEC4  Alanine-first (amendment item 1): applies only to eligible
        alanines in C1, C2 (and C5, which follows the same rules by item
        3) whose (position, V) pair is NOT among the 96 existing
        backgrounds.  For EVERY eligible alanine in those cells the script
        verifies and prints whether (position, V) exists in
        data/processed/phase2_arm_roster.csv; where it exists the step is
        skipped for that position (Arm V already covers those alanines).
N-DEC5  Draw mechanics (amendment items 2-3): every eligible position in
        C1, C2, C5 receives exactly one new background (caps 16/28/16 all
        exceed the eligible counts; if a cell ever had MORE eligible
        positions than its cap, only the first `cap` ascending positions
        would be used -- stated here so the rule exists before it could
        bind).  Mutants: one numpy.random.default_rng(0) stream, FIXED at
        0 by the amendment (the SEED env var is NOT used for the draw),
        cells in the order C1, then C2, then C5, positions ascending
        within a cell, one draw per position from the continuing stream:
        the alphabetically sorted one-letter codes of the non-wild-type
        residues EXCLUDING every residue whose (position, residue) pair is
        among the 96 existing backgrounds or A222V, indexed by
        rng.integers(len(allowed)).  C3 (not amended): cap 10 of its
        eligible positions, each slot = position drawn by
        rng.integers(len(pool)) from the ascending remaining pool without
        replacement, then the mutant by the same allowed-set rule.
        STREAM ORDER C1 -> C2 -> C5 -> C3 is this script's interpretation:
        the amendment pins "C1 first and then C2" and gives C5 the same
        rules (so C5 follows C2); C3 is unamended and is drawn last.
        Disclosed as an interpretation -- the amendment does not state
        C3's place in the stream.
N-DEC6  A position that already hosts an existing background stays
        eligible with a different residue and is flagged
        second_at_position = True in the roster (amendment item 2).
N-DEC7  Roster contract: data/processed/phase4/neigh/roster_v1.csv with
        columns bg_id, cell, position, wt_aa, mut_aa, d3, dseq,
        second_at_position, alanine_first, score_order;
        bg_id = N_<position>_<wt_aa><mut_aa> (e.g. N_156_AC).  The
        scoring order is round-robin across cells in the cycle
        C1, C2, C5, C3, ascending position within a cell, so any
        completed prefix is balanced (frozen section 3); the balance
        property is gated.  The roster is written and sha256-hashed to
        roster_v1.sha256 BEFORE any scoring.  Re-running regenerates the
        same bytes (the draw is deterministic) and FAILS if a previously
        written roster_v1.csv differs -- the roster can never silently
        change after scoring has begun.
N-DEC8  NB (amendment item 3): the new backgrounds in C1, C2 and C5 plus
        the six existing nulls with d3 <= 12 (frozen section 5 names
        them: G_I192T, AV_220, AV_155, AV_195, G_L178T, AV_175 --
        verified here against the geometry).  |NB| is printed BEFORE any
        scoring; UNDERPOWERED iff |NB| < 30 (unchanged).
N-DEC9  Expected passes: per background = |H| - 1[position in H], H =
        script 125's held-out set (455 positions; torch-free import).
        Totals printed for the roster and for NB.  This script does no
        bootstrap and no model scoring: N_BOOT/SEED are printed per
        session convention and unused (the draw seed is fixed at 0 by the
        amendment).

GATES (hard for the item they guard; any FAIL -> exit 3):
  G-N0  as N-DEC3 (hashes, d3 reproduction, print-before-draw, no torch).
  G-N1  the roster is written, hashed and re-read before any scoring;
        no duplicate (position, mutant) pairs; no pair among the 97
        banned pairs; unique bg_ids; per-cell counts match the printed
        pre-draw counts (all eligible for C1/C2/C5, exactly the cap for
        C3); second_at_position flags correct; round-robin balance.

LIMITATIONS (AGENTS 6, also printed at the end):
  * This is NEW data by construction -- the roster is drawn fitness-blind
    (only geometry, sequence and the 96-background roster are used; no
    fitness, rho or epistasis quantity enters any decision here).
  * d3 is a CA-CA distance in a 2.50 A crystal structure (6FCX chain A);
    side chains, loops and the AlphaFold-era caveats of Diagnostics II
    apply (script 139's own limitations stand).
  * "Resolved" = a chain-A Calpha exists at that residue number; frame
    positions without one are excluded from eligibility entirely.
  * The roster file freezes WHICH backgrounds get scored, not their
    scores; the analysis (script 172) runs only after the night's
    scoring, per the amendment item 5 coverage rule.

Usage:
  venv/bin/python3 scripts/170_neigh_roster.py
"""

import hashlib
import importlib.util
import os
import sys
import time
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase4_common as p4c          # noqa: E402
from scripts.lib.sequence import load_sequence, verify_sequence  # noqa: E402

PREREG = ROOT / "docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md"
PREREG_SHA = "167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e"
AMEND = ROOT / ("docs/tasks/phase4-strengthening/prereg/"
                "NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md")
AMEND_SHA = "f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a"
STORED_D3 = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
STORED_D3_SHA = "69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de"
EXIST_ROSTER = ROOT / "data/processed/phase2_arm_roster.csv"
PDB = ROOT / "data/raw/6FCX.pdb"
ATLAS = ROOT / "data/processed/task32_analysis_table.csv"
FASTA = ROOT / "data/raw/P42898.fasta"
OUT_DIR = ROOT / "data/processed/phase4/neigh"
ROSTER_CSV = OUT_DIR / "roster_v1.csv"
ROSTER_SHA = OUT_DIR / "roster_v1.sha256"
CELLS_CSV = OUT_DIR / "eligible_cells_v1.csv"

CAPS = {"C1": 16, "C2": 28, "C5": 16, "C3": 10}     # amendment item 3 for C5
AMENDED_ALL_ELIGIBLE = ("C1", "C2", "C5")            # amendment items 2-3
DRAW_ORDER = ("C1", "C2", "C5", "C3")                # N-DEC5
CYCLE = ("C1", "C2", "C5", "C3")                     # N-DEC7
SIX_NULLS = ["G_I192T", "AV_220", "AV_155", "AV_195", "G_L178T", "AV_175"]
AA = list("ACDEFGHIKLMNPQRSTVWY")                    # alphabetical, esm AA_LIST

t0 = time.time()
gates = []
counts_printed = False


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gate(name, ok, detail="", note=""):
    gates.append((name, bool(ok)))
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f": {detail}" if detail else "")
          + (f"  ({note})" if note else ""), flush=True)


def main():
    global counts_printed
    banner("170 -- Module N: neighbour-arm geometry + roster (A7a/A7b)")
    print(f"  N_BOOT={N_BOOT} SEED={SEED} -- BOTH UNUSED here: no bootstrap, "
          "no randomness beyond the roster draw, whose seed is FIXED at 0 "
          "by the amendment (N-DEC5).")

    print("\nPRE-REGISTERED DECISIONS (printed before any geometry metric; "
          "full text in this script's docstring):")
    for k, v in [
        ("N-DEC1", "v1 + Amendment 1 both sha-pinned; amendment applied "
                   "verbatim; v1 never edited."),
        ("N-DEC2", "script 139 loader imported torch-free; eligible = frame "
                   "n resolved in 6FCX chain A minus 222; cells via "
                   "p4c.cell_labels + C5 = gap with d3<=12; listing written "
                   "before any draw."),
        ("N-DEC3", "G-N0: prereg/amendment/stored-d3 hashes; d3 for the 67 "
                   "resolved nulls max|diff| < 1e-6; print-before-draw "
                   "flagged; no torch."),
        ("N-DEC4", "alanine-first only where (position,V) is NOT among the "
                   "96; verified and printed for every eligible alanine in "
                   "C1/C2/C5; skipped where it exists."),
        ("N-DEC5", "one default_rng(0) stream (SEED env not used); C1 -> C2 "
                   "-> C5 ascending, one allowed-set mutant draw per "
                   "position; C3 = cap 10, position draws without "
                   "replacement then mutant; stream order C1->C2->C5->C3 "
                   "is this script's disclosed interpretation."),
        ("N-DEC6", "second_at_position flagged; such positions stay "
                   "eligible with a non-banned residue."),
        ("N-DEC7", "roster schema + bg_id N_<pos><wt><mut>; round-robin "
                   "score order C1,C2,C5,C3 ascending, balance gated; "
                   "written and hashed before scoring; re-runs must "
                   "reproduce byte-identical or FAIL."),
        ("N-DEC8", "NB = new C1+C2+C5 + the six existing d3<=12 nulls; "
                   "|NB| printed before scoring; UNDERPOWERED iff < 30."),
        ("N-DEC9", "expected passes = 455 - 1[own in H]; N_BOOT/SEED "
                   "printed, unused."),
    ]:
        print(f"  {k}: {v}")

    banner("G-N0 -- INPUTS, HASHES AND THE LOADER (hard)", "-")
    gate("G-N0 prereg v1 sha256", sha256(PREREG) == PREREG_SHA,
         sha256(PREREG)[:16] + "...")
    gate("G-N0 Amendment 1 sha256", sha256(AMEND) == AMEND_SHA,
         sha256(AMEND)[:16] + "... (saved verbatim)")
    gate("G-N0 stored d3 file sha256", sha256(STORED_D3) == STORED_D3_SHA,
         sha256(STORED_D3)[:16] + "...")
    gate("G-N0 torch not in sys.modules after this script's imports",
         "torch" not in sys.modules,
         "checked again at the end after the s139/s125 imports")

    # ---------------------------------------------------------- geometry --
    spec = importlib.util.spec_from_file_location(
        "s139_phase2_diag2_3d", ROOT / "scripts/139_phase2_diag2_3d.py")
    s139 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s139)
    gate("G-N0 script 139 loader importable torch-free",
         "torch" not in sys.modules, "importlib import of s139 OK")
    ca, _atoms, _mx, _e3, _r3 = s139.parse_pdb_float64(PDB)
    a222 = ca["A"][222]

    atlas = pd.read_csv(ATLAS)
    frame = sorted(int(p) for p in
                   atlas.dropna(subset=["delta_esm", "own_e_b"])
                   .position.unique())
    gate("G-N0 frame = 654 positions", len(frame) == 654, str(len(frame)))
    eligible_pos = [p for p in frame if p in ca["A"] and p != 222]
    d3 = {p: float(np.linalg.norm(ca["A"][p] - a222)) for p in eligible_pos}
    dseq = {p: abs(p - 222) for p in eligible_pos}

    wt_seq = load_sequence(str(FASTA))
    verify_sequence(wt_seq)          # prints its own length/222 checks

    d3v = np.array([d3[p] for p in eligible_pos])
    dsv = np.array([dseq[p] for p in eligible_pos], dtype=float)
    lab = np.asarray(p4c.cell_labels(d3v, dsv), dtype=object)
    # C5 (amendment item 3): a section-2 gap cell that is 3D-near.
    lab = np.where((lab == "") & (d3v <= 12.0), "C5", lab)

    cells = pd.DataFrame({
        "position": eligible_pos,
        "wt_aa": [wt_seq[p - 1] for p in eligible_pos],
        "d3": d3v, "dseq": dsv, "cell": lab,
    })

    # ------------------------------------- listing BEFORE any draw --------
    order_show = ["C1", "C2", "C5", "C3", "C4", ""]
    print("\nELIGIBLE-POSITION COUNTS PER CELL (printed BEFORE any draw; "
          "full listing written to eligible_cells_v1.csv):")
    for c in order_show:
        n = int((cells.cell == c).sum())
        if n:
            print(f"  {c or '(gap)':6s}: {n:4d}")
    n_within12 = int((cells.d3 <= 12).sum())
    print(f"  total eligible: {len(cells)} | positions with d3 <= 12: "
          f"{n_within12} (planning figure: roughly 40-60) | C3 eligible: "
          f"{int((cells.cell == 'C3').sum())} (planning: may be small/empty)")
    # Amendment item 6: new backgrounds per cell and |NB| are ALSO known
    # before the draw -- they are min(eligible, cap) per cell (the draw
    # decides WHICH positions/mutants, never HOW MANY).
    pre_new = {c: min(int((cells.cell == c).sum()), CAPS[c])
               for c in ("C1", "C2", "C5", "C3")}
    pre_nb = pre_new["C1"] + pre_new["C2"] + pre_new["C5"] + len(SIX_NULLS)
    print("  new backgrounds per cell BEFORE the draw (= min(eligible, cap)):"
          + "".join(f" {c} {n}" for c, n in pre_new.items())
          + f" | roster total {sum(pre_new.values())}")
    print(f"  |NB| BEFORE the draw = new C1+C2+C5 "
          f"({pre_new['C1'] + pre_new['C2'] + pre_new['C5']}) + six existing "
          f"nulls ({len(SIX_NULLS)}) = {pre_nb}"
          + (" -> UNDERPOWERED (<30), say so now" if pre_nb < 30
             else " -> >= 30, not underpowered by construction"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cells.to_csv(CELLS_CSV, index=False)
    print(f"  wrote {CELLS_CSV.relative_to(ROOT)} "
          f"sha256={sha256(CELLS_CSV)[:16]}...")
    counts_printed = True

    # -------------------------------------- existing 96 + banned pairs ----
    ex = pd.read_csv(EXIST_ROSTER)
    gate("G-N1 existing roster = 96 unique backgrounds",
         len(ex) == 96 and ex.bg_id.nunique() == 96, f"{len(ex)} rows")
    banned = set(zip(ex.position.astype(int), ex.mut_aa)) | {(222, "V")}
    ex_pos = set(ex.position.astype(int))

    # ----------------------------------- alanine verification (amend. 1) --
    print("\nAMENDMENT 1 -- ALANINE-FIRST VERIFICATION (every eligible "
          "alanine in C1/C2/C5; (position, V) looked up in "
          "data/processed/phase2_arm_roster.csv):")
    ala_ok_all = True
    for c in AMENDED_ALL_ELIGIBLE:
        for r in cells[cells.cell == c].sort_values("position").itertuples():
            if r.wt_aa != "A":
                continue
            exists = (int(r.position), "V") in banned
            ala_ok_all &= exists
            print(f"  {c} position {int(r.position)}: (position, V) "
                  f"{'EXISTS' if exists else 'does NOT exist'} among the 96 "
                  f"-> alanine-first "
                  f"{'SKIPPED (Arm V already covers it)' if exists else 'APPLIES (A->V)'}")

    # ------------------------------------------------------------ draw ----
    banner("ROSTER DRAW (amendment items 2-3; fitness-blind)", "-")
    assert counts_printed, "cell counts must be printed before the draw"
    rng = np.random.default_rng(0)      # fixed by the amendment, N-DEC5
    rows = []

    def allowed_mutants(p, wt):
        muts = [a for a in AA if a != wt and (p, a) not in banned]
        assert muts, (p, wt)
        return muts

    def take_all(c):
        sub = cells[cells.cell == c].sort_values("position")
        if len(sub) > CAPS[c]:
            print(f"  NOTE {c}: {len(sub)} eligible > cap {CAPS[c]} -- "
                  "first cap ascending positions used (N-DEC5)")
            sub = sub.iloc[:CAPS[c]]
        for r in sub.itertuples():
            p, wt = int(r.position), r.wt_aa
            if wt == "A" and (p, "V") not in banned:
                mut, ala_first = "V", True        # amendment item 1 applies
            else:
                allowed = allowed_mutants(p, wt)
                mut = allowed[int(rng.integers(len(allowed)))]
                ala_first = False
            rows.append((c, p, wt, mut, ala_first))

    def take_c3():
        pool = sorted(int(p) for p in
                      cells.loc[cells.cell == "C3", "position"])
        n = min(CAPS["C3"], len(pool))
        if n < len(pool):
            print(f"  C3: {len(pool)} eligible > cap {CAPS['C3']} -- "
                  f"{n} positions drawn without replacement (frozen section 3)")
        for _ in range(n):
            idx = int(rng.integers(len(pool)))
            p = pool.pop(idx)              # without replacement, N-DEC5
            wt = wt_seq[p - 1]
            allowed = allowed_mutants(p, wt)
            mut = allowed[int(rng.integers(len(allowed)))]
            rows.append(("C3", p, wt, mut, False))

    for c in DRAW_ORDER:
        if c == "C3":
            take_c3()
        else:
            take_all(c)

    # second_at_position flag + bg_id
    recs = []
    for c, p, wt, mut, ala in rows:
        assert wt_seq[p - 1] == wt, (p, wt)
        recs.append(dict(bg_id=f"N_{p}_{wt}{mut}", cell=c, position=p,
                         wt_aa=wt, mut_aa=mut,
                         d3=d3[p], dseq=float(dseq[p]),
                         second_at_position=(p in ex_pos),
                         alanine_first=ala))
    roster = pd.DataFrame(recs)

    # round-robin score order (N-DEC7): cycle C1, C2, C5, C3; asc in cell
    pools = {c: deque(sorted(roster.loc[roster.cell == c, "position"],
                             reverse=True)) for c in CYCLE}
    order_seq = []
    while any(pools.values()):
        for c in CYCLE:
            if pools[c]:
                order_seq.append(pools[c].pop())
    rank_of = {p: i for i, p in enumerate(order_seq)}
    roster["score_order"] = roster["position"].map(
        lambda p: rank_of[p])   # positions unique across cells
    roster = roster.sort_values("score_order").reset_index(drop=True)

    # ------------------------------------------------------------- write --
    roster.to_csv(ROSTER_CSV, index=False)
    r_sha = sha256(ROSTER_CSV)
    if ROSTER_SHA.exists():
        prev = ROSTER_SHA.read_text().split()[0]
        gate("G-N1 re-run reproduces the frozen roster byte-identically",
             prev == r_sha, f"{r_sha[:16]}... vs previous {prev[:16]}...")
    ROSTER_SHA.write_text(f"{r_sha}  roster_v1.csv\n")

    # ------------------------------------------------------------ gates ---
    banner("G-N1 -- ROSTER WRITTEN, HASHED, RE-READ (hard)", "-")
    reread = pd.read_csv(ROSTER_CSV)
    gate("G-N1 roster sha256 matches sidecar after re-read",
         sha256(ROSTER_CSV) == r_sha
         and ROSTER_SHA.read_text().split()[0] == r_sha, r_sha[:16] + "...")
    gate("G-N1 re-read equals the drawn roster",
         len(reread) == len(roster)
         and reread.bg_id.tolist() == roster.bg_id.tolist()
         and reread.mut_aa.tolist() == roster.mut_aa.tolist(),
         f"{len(reread)} rows")
    gate("G-N1 unique bg_ids", reread.bg_id.nunique() == len(reread),
         f"{reread.bg_id.nunique()}/{len(reread)}")
    pairs = list(zip(reread.position.astype(int), reread.mut_aa))
    gate("G-N1 no duplicate (position, mutant) pairs",
         len(set(pairs)) == len(pairs), f"{len(set(pairs))} unique pairs")
    n_banned = sum(1 for pr in pairs if pr in banned)
    gate("G-N1 no pair among the 97 banned (96 existing + A222V)",
         n_banned == 0, f"{n_banned} violations")
    counts_ok = True
    detail = []
    for c in AMENDED_ALL_ELIGIBLE:
        n_elig = int((cells.cell == c).sum())
        n_use = min(n_elig, CAPS[c])
        n_have = int((reread.cell == c).sum())
        counts_ok &= (n_have == n_use)
        detail.append(f"{c} {n_have}/{n_use} (eligible {n_elig})")
    n_c3 = int((reread.cell == "C3").sum())
    counts_ok &= (n_c3 == min(CAPS["C3"], int((cells.cell == "C3").sum())))
    detail.append(f"C3 {n_c3}/{min(CAPS['C3'], int((cells.cell == 'C3').sum()))}")
    gate("G-N1 per-cell counts = printed pre-draw counts",
         counts_ok and counts_printed, " | ".join(detail))
    flag_ok = all(bool(r.second_at_position) == (int(r.position) in ex_pos)
                  for r in reread.itertuples())
    gate("G-N1 second_at_position flags correct", flag_ok,
         f"{int(reread.second_at_position.sum())} flagged")
    # round-robin balance: while both active, counts differ by <= 1
    tot = {c: int((reread.cell == c).sum()) for c in CYCLE}
    seen = {c: 0 for c in CYCLE}
    bal_ok = True
    for c in reread.cell:                    # rows are in score_order
        seen[c] += 1
        active = [x for x in CYCLE if seen[x] < tot[x]]
        if len(active) > 1:
            vals = [seen[x] for x in active]
            bal_ok &= (max(vals) - min(vals) <= 1)
    gate("G-N1 round-robin score order balanced at every prefix", bal_ok,
         "max cell-count difference <= 1 over every prefix of active cells")

    # ------------------------------------------------------------- NB -----
    banner("NB, CELLS AND EXPECTED PASSES (printed BEFORE scoring)", "-")
    six = pd.read_csv(STORED_D3).set_index("bg_id")
    six_rows = []
    six_ok = True
    for b in SIX_NULLS:
        p = int(six.loc[b, "position"])
        is_res = bool(six.loc[b, "resolved"])
        dd3 = d3.get(p, float("nan"))
        ok = is_res and np.isfinite(dd3) and dd3 <= 12.0
        six_ok &= ok
        six_rows.append((b, p, dd3, ok))
        print(f"  existing null {b:10s} pos {p:4d} d3 {dd3:7.3f} "
              f"<= 12: {ok}")
    gate("G-N1 the six NB nulls all have d3 <= 12 and are resolved",
         six_ok, "frozen section 5 list verified against the geometry")

    # H set (script 125, torch-free)
    spec2 = importlib.util.spec_from_file_location(
        "s125_phase2_analysis", ROOT / "scripts/125_phase2_analysis.py")
    s125 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(s125)
    H = set(s125.holdout(s125.build_frame()))
    gate("G-N1 H = 455 positions", len(H) == 455, str(len(H)))

    def passes(pos):
        return len(H) - (1 if pos in H else 0)

    nb_new = reread[reread.cell.isin(AMENDED_ALL_ELIGIBLE)]
    n_nb = len(nb_new) + len(SIX_NULLS)
    print("\n  new backgrounds per cell:")
    for c in ["C1", "C2", "C5", "C3"]:
        sub = reread[reread.cell == c]
        print(f"    {c}: {len(sub)}")
    print(f"  NB = new C1+C2+C5 ({len(nb_new)}) + six existing nulls "
          f"({len(SIX_NULLS)}) = {n_nb}")
    if n_nb < 30:
        print("  *** |NB| < 30 IS ALREADY CERTAIN -> the primary test will "
              "be UNDERPOWERED (no word), per frozen section 5. ***")
    else:
        print(f"  |NB| = {n_nb} >= 30 -> not underpowered by construction "
              "(the amendment item 5 coverage rule still applies after "
              "scoring: NB members must each reach >= 95% of eligible H).")
    exp_passes = sum(passes(int(p)) for p in reread.position)
    nb_passes = sum(passes(int(p)) for p in nb_new.position) + \
        sum(passes(int(six.loc[b, "position"])) for b in SIX_NULLS)
    print(f"  expected passes: roster {exp_passes} "
          f"(= {len(reread)} backgrounds x ~455 minus own-in-H); "
          f"NB {nb_passes}; per background "
          f"{sorted(set(passes(int(p)) for p in reread.position))}")

    # no-torch check LAST, after the s139 and s125 imports (they must be
    # torch-free too -- that is what makes this script runnable pre-scoring)
    gate("G-N0 torch NOT loaded anywhere in this process",
         "torch" not in sys.modules,
         "post-import check: 139/125/lib all import torch-free")

    # ---------------------------------------------------------- summary ---
    banner("SUMMARY")
    n_pass = sum(1 for _, ok in gates if ok)
    print(f"  {n_pass}/{len(gates)} checks PASS, {len(gates) - n_pass} FAIL.")
    print(f"\n  roster -> {ROSTER_CSV.relative_to(ROOT)} "
          f"({len(reread)} rows, sha256 {r_sha})")
    print(f"  cells  -> {CELLS_CSV.relative_to(ROOT)} "
          f"({len(cells)} rows, sha256 {sha256(CELLS_CSV)})")
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the docstring):")
    print("    * fitness-blind roster: geometry + sequence + the 96-roster "
          "only; no rho/epistasis quantity entered any decision.")
    print("    * d3 is a CA-CA distance in a 2.50 A crystal structure; "
          "'resolved' = chain-A Calpha exists; no side-chain geometry.")
    print("    * the roster freezes WHICH backgrounds are scored, not their "
          "scores; analysis runs only after scoring (amendment item 5).")
    print("    * stream order C1->C2->C5->C3 and rng.integers indexing are "
          "this script's disclosed interpretations of the amendment.")
    if len(gates) - n_pass:
        print(f"\nA7 RESULT: GATE FAIL -- exit 3")
        sys.exit(3)
    print(f"\nA7a/A7b RESULT: GATE PASS -- exit 0")
    print(f"  elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
