"""E2 — recompute the beyond-contact-range figure on the biological dimer.

Task doc `MANUSCRIPT_REVIEW_RESPONSE.md`, Group E, Task E2 (E2a-E2c).
PRE-REGISTERED: this docstring was written before the first (and only)
run of this script. Every definition, gate, denominator, and threshold
below was fixed before any number produced here was seen.

WHY: the published project figure "96.22% of the frame is beyond
10 A from position 222" (RELIABILITY_LOG L1058/L1105: 9,232/9,595
beyond 10 A, <=10 A = 363) was computed on CHAIN A ALONE — script 77
called `load_pdb(data/raw/6FCX.pdb, ["A"])` (script 77 L261, verified
this session) over a catalytic-domain monomer construct, and the 59
atlas positions without chain-A coordinates are structurally absent
(scripts/68 L24, scripts/85 L106: positions 2-39, 161-171, 392-396,
652-656). MTHFR is an obligate homodimer, so a variant position can
sit close to residue 222 THROUGH the opposite subunit while being far
from it within its own chain. E2 recomputes the figure on the
biological dimer.

E2a — REUSE, NO RESCORING: no model is run here. Coordinates come
from the SAME vendor parse of the SAME structure used by both the
original figure's session (script 77, chain A) and the AD7
dimer-scoring session (script 80, chains A+B): ThermoMPNN's
`load_pdb` from `data/external/ThermoMPNN-D/thermompnn/ssm_utils.py`
— the exact machinery, not a reimplementation. The AD7 session's
scored tables `task80_dimer_positions.csv` / `task80_dimer_variants.csv`
are READ for the frame cross-check (G6); their ddG scoring is not
recomputed (that is what "rather than rescoring from scratch"
mandates).

DEFINITIONS (fixed here):
- Atlas position universe U = {2..656}, 655 positions (file-verified:
  phase5_analysis_table.csv's unique positions == U minus {222};
  scripts/85 L106's 59-position policy list has tail "652-656" and
  head "2-39"; OVERNIGHT_LOG L1673 "atlas positions 655").
- Position p "has monomer coordinates" iff the chain-A parse resolves
  it (resn_list_A/p and seq_chain_A != '-'); "has dimer
  coordinates" iff chain A OR chain B resolves it.
- Monomer distance (the original figure): d_AA(p) = C-alpha distance
  p(chain A) to 222(chain A) — must reproduce the stored
  `ca_dist_222` column (G1) and the published 9,232/363 counts (G2).
- DIMER-AWARE DISTANCE (E2b, PRIMARY): d_min(p) = minimum C-alpha
  distance over ALL FOUR available pairings of the variant site's
  copy {chain A, chain B} x residue 222's copy {chain A, chain B}.
  Pre-registered rationale: in the biological experiment both
  subunits carry both mutations (homodimer construct), so every copy
  of p is physically present; taking the min over all four pairings
  is the complete two-fold-symmetry accounting, and it can only
  decrease distances — the honest direction for a "long-range"
  claim (any change can only move rows TOWARD contact, never away).
- SENSITIVITY (literal-task reading, printed, no decision): d_minA(p)
  = min(d_AA, d_AB) = variant copy fixed in chain A, min over 222's
  two copies ("close to 222 through the opposite subunit"). Under
  exact two-fold symmetry this equals d_min; both are printed with
  their difference (G7 reports whether they ever differ).
- Contact cutoff: 10.0 Angstrom C-alpha-C-alpha, the original
  figure's cutoff (script 77: `0 < dmat < 10.0`; script 96:
  `ca_dist_222 > 10.0` = far).
- PRIMARY PERCENTAGE (E2b): per-VARIANT-ROW on the original figure's
  own frozen frame — rows of task77_thermompnnD_doubles.csv with
  own_e_b finite, expected exactly 9,595 rows / 586 positions (same
  denominator as 96.22%, so the two numbers are directly
  comparable). Position-level percentages (586) and E2c's
  position-level coordinate counts are also reported, each with its
  denominator stated (AGENTS sec 5 accounting).

GATES (failure => print, sys.exit(1); no retry, no threshold change):
  G0  inputs exist: data/raw/6FCX.pdb, task77_thermompnnD_doubles.csv,
      task80_dimer_positions.csv, phase5_analysis_table.csv.
  G1  mapping + monomer reproduction: for every frame row,
      |d_AA(p) - stored ca_dist_222| < 1e-6 (this empirically proves
      position p <-> resn index p-40 alignment AND that the original
      figure used chain A's C-alpha only — if it fails, the monomer
      baseline itself is in question, so STOP). Also: resn_list_A is
      exactly 40..651, resn_list_B exactly 41..648, residue 222
      resolved ('A') in both chains, stored ca_dist_222 constant
      within position.
  G2  original figure reproduced exactly: far(>10 A) == 9,232,
      near(<=10 A) == 363, n == 9,595, positions == 586 -> 96.2167%
      prints as the published 96.22% (RELIABILITY_LOG L1058/L1105,
      VERIFIED_FINDINGS_TABLE row 90).
  G3  phase5's unique position set == U - {222} (654 exact) — the
      universe is file-derived, not asserted from memory.
  G4  chain-A missing set over U == EXACTLY the 59-position policy
      list {2-39, 161-171, 392-396, 652-656} (scripts/68 L24,
      scripts/85 L106, task E2a's "missing 59 atlas positions").
      Two independent sources agree on this list; a mismatch means a
      third source disagrees => STOP, print the set difference.
  G5  identity for the dimer definition: d_min <= d_AA + 1e-12 on
      every frame row (four-pair min contains the chain-A pair), and
      the far(dimer) row set is a SUBSET of the far(monomer) row set.
      AGENTS sec 4 identity check, inside this null's own output —
      (no resampled null here: this is a deterministic census of one
      structure; there is no N_BOOT/N_PERM to smoke-test and no
      p-value or CI is computed or needed — percentages are exact
      given the structure).
  G6  frame cross-check (E2a's reuse): task80_dimer_positions.csv's
      position set == the frame's 586 positions (AD7 session scored
      exactly this frame's positions). Printed as counts + symmetric
      difference; informational, not a failure path — the denominator
      for E2b is task77's frame regardless.
  G7  dimer-missing subset identity: (U minus A-coords) minus
      B-rescued == (U minus (A or B)) by construction — printed with
      the exact position lists so every count is auditable.

E2c OUTPUT: exact counts of atlas positions with NO coordinates under
each definition — monomer missing (expected 59, gated), dimer
missing (the measured unknown), chain-B missing, and the positions
chain B rescues — each printed with its full position list.

OUTPUT CSV: data/processed/task107_e2_dimer_distances.csv, one row
per U position (655), columns: position, in_phase5, in_frame, has_A,
has_B, d_AA, d_AB, d_BA, d_BB, d_min_four, d_min_variantA, far_AA,
far_dimer_four, far_dimer_variantA.

LIMITATIONS (printed with results, AGENTS sec 6):
  1. C-alpha only, one static crystal structure (6FCX) — the same
     atom choice and structure as the original figure (comparability
     over refinement); solution-state dynamics are not represented.
  2. The four-pair min is a GEOMETRIC lower envelope — it says a
     contact is structurally possible, not that it is occupied or
     functionally relevant.
  3. Chain B's parsed window (41-648) is narrower than chain A's
     (40-651); positions 40 and 649-651 have coordinates only in A
     (harmless: A covers them; reported).
  4. Row-level (9,595) and position-level (586/655) denominators are
     different populations — always labeled; never mixed.
  5. Descriptive census: no resampling, no p-value, no CI, no null —
     nothing here tests a hypothesis; it restates a fact about
     geometry under a corrected definition.
  6. Existing scripts/CSVs are read-only; nothing is overwritten.
Next free script number after this: 108.
"""
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data" / "external" / "ThermoMPNN-D"))

# Cosmetic (disclosed): the vendor parse triggers Biopython's
# pairwise2 deprecation warning at import. Nothing is hidden from any
# gate (all counts are printed explicitly below).
warnings.filterwarnings("ignore",
                        message="Bio.pairwise2 has been deprecated")

from thermompnn.ssm_utils import load_pdb  # noqa: E402

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

CUTOFF = 10.0
UNIVERSE = set(range(2, 657))                     # 655 atlas positions
POLICY_MISSING = (set(range(2, 40))                # scripts/85 L106,
                  | set(range(161, 172))           # scripts/68 L24,
                  | set(range(392, 397))           # task E2a's 59
                  | set(range(652, 657)))
EXPECTED_FRAME = (9595, 586)
EXPECTED_FAR = 9232
EXPECTED_NEAR = 363
TOL = 1e-6


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def main():
    t0 = time.time()
    banner("E2 — dimer-aware beyond-contact-range figure (scripts/107)")

    # ---- G0: inputs -------------------------------------------------
    files = {
        "6FCX structure": RAW / "6FCX.pdb",
        "original figure frame": PROC / "task77_thermompnnD_doubles.csv",
        "AD7 dimer positions": PROC / "task80_dimer_positions.csv",
        "analysis table": PROC / "phase5_analysis_table.csv",
    }
    for label, p in files.items():
        if not p.exists():
            gfail(f"G0 FAIL: {label} input missing: {p} — stop.")
    print("  G0 PASS: all 4 inputs present")

    # ---- vendor parse (same machinery as scripts 77 and 80) ---------
    pdb = load_pdb(str(files["6FCX structure"]), ["A", "B"])
    pos = {}          # chain -> {position: CA xyz}
    resn_all = {}
    for ch in ("A", "B"):
        resn = [int(r) for r in pdb[f"resn_list_{ch}"]]
        seqc = pdb[f"seq_chain_{ch}"]
        ca = pdb[f"coords_chain_{ch}"][f"CA_chain_{ch}"]
        if not (len(resn) == len(seqc) == len(ca)):
            gfail(f"G1 FAIL: chain {ch} lengths resn={len(resn)} "
                  f"seq={len(seqc)} ca={len(ca)} — stop.")
        resn_all[ch] = resn
        pos[ch] = {resn[i]: np.asarray(ca[i], float)
                   for i in range(len(resn)) if seqc[i] != "-"}
    if resn_all["A"] != list(range(40, 652)):
        gfail(f"G1 FAIL: chain A resn_list is not 40..651 "
              f"(first/last {resn_all['A'][0]}/{resn_all['A'][-1]}) — stop.")
    if resn_all["B"] != list(range(41, 649)):
        gfail(f"G1 FAIL: chain B resn_list is not 41..648 "
              f"(first/last {resn_all['B'][0]}/{resn_all['B'][-1]}) — stop.")
    for ch in ("A", "B"):
        if 222 not in pos[ch]:
            gfail(f"G1 FAIL: residue 222 not resolved in chain {ch} — "
                  "the dimer-aware definition is impossible — stop.")
    if pdb["seq_chain_A"][182] != "A" or pdb["seq_chain_B"][181] != "A":
        gfail(f"G1 FAIL: residue 222 WT is not 'A' (A[182] = "
              f"{pdb['seq_chain_A'][182]!r}, B[181] = "
              f"{pdb['seq_chain_B'][181]!r}) — wrong residue mapping, "
              f"script 77's G2 precedent — stop.")
    print(f"  G1a PASS: chain A resn 40..651 resolved {len(pos['A'])}/612; "
          f"chain B resn 41..648 resolved {len(pos['B'])}/608; "
          f"residue 222 = 'A' and resolved in BOTH chains")

    a222, b222 = pos["A"][222], pos["B"][222]
    d_222_inter = float(np.linalg.norm(a222 - b222))
    print(f"  inter-subunit 222(A)-222(B) C-alpha distance: "
          f"{d_222_inter:.3f} A")

    # ---- G3: universe file-verified ---------------------------------
    ph = pd.read_csv(files["analysis table"], usecols=["position"])
    ph_set = set(int(p) for p in ph["position"].unique())
    if ph_set != UNIVERSE - {222}:
        gfail(f"G3 FAIL: phase5 positions ({len(ph_set)}) != U-{{222}} "
              f"({len(UNIVERSE - {222})}); missing="
              f"{sorted(UNIVERSE - {222} - ph_set)[:5]} "
              f"extra={sorted(ph_set - (UNIVERSE - {222}))[:5]} — stop.")
    print(f"  G3 PASS: atlas universe U = {{2..656}} = {len(UNIVERSE)} "
          f"positions file-verified (phase5 = U minus {{222}}, "
          f"{len(ph_set)} exact)")

    # ---- G4: monomer missing set == the 59-position policy list -----
    mono_missing = UNIVERSE - set(pos["A"])
    if mono_missing != POLICY_MISSING:
        gfail(f"G4 FAIL: chain-A missing set ({len(mono_missing)}) != "
              f"59-position policy list; only-in-parse="
              f"{sorted(mono_missing - POLICY_MISSING)}; only-in-policy="
              f"{sorted(POLICY_MISSING - mono_missing)} — stop.")
    print(f"  G4 PASS: monomer missing over U == the 59-position list "
          f"EXACTLY ({len(mono_missing)} = 38+11+5+5): "
          f"2-39, 161-171, 392-396, 652-656 — scripts/68 L24 + "
          f"scripts/85 L106 + task E2a all agree")

    # ---- frame + G1/G2 monomer reproduction -------------------------
    t77 = pd.read_csv(files["original figure frame"])
    fr = t77[t77["own_e_b"].notna()].copy()
    if (len(fr), fr["position"].nunique()) != EXPECTED_FRAME:
        gfail(f"G2 FAIL: frame {len(fr)}/{fr['position'].nunique()} != "
              f"{EXPECTED_FRAME[0]}/{EXPECTED_FRAME[1]} — stop.")
    if not np.isfinite(fr["ca_dist_222"].to_numpy(float)).all():
        gfail("G2 FAIL: stored ca_dist_222 non-finite on frame — stop.")
    per_pos = fr.groupby("position")["ca_dist_222"].nunique().max()
    if per_pos != 1:
        gfail(f"G1 FAIL: stored ca_dist_222 not constant within position "
              f"(max distinct {per_pos}) — stop.")
    stored = fr["ca_dist_222"].to_numpy(float)
    dAA = np.array([float(np.linalg.norm(pos["A"][p] - a222))
                    for p in fr["position"]])
    max_dev = float(np.max(np.abs(dAA - stored)))
    if max_dev >= TOL:
        gfail(f"G1 FAIL: chain-A distance does not reproduce stored "
              f"ca_dist_222 (max|diff| = {max_dev:.3e} >= {TOL}) — the "
              f"monomer baseline itself is in question — stop.")
    print(f"  G1b PASS: d_AA reproduces stored ca_dist_222 on all "
          f"{len(fr)} frame rows (max|diff| = {max_dev:.3e} < {TOL}) — "
          f"mapping p<->resn p-40 and 'chain A alone' both confirmed")

    farA = dAA > CUTOFF
    n_farA, n_nearA = int(farA.sum()), int((~farA).sum())
    if (n_farA, n_nearA) != (EXPECTED_FAR, EXPECTED_NEAR):
        gfail(f"G2 FAIL: monomer far/near = {n_farA}/{n_nearA} != "
              f"{EXPECTED_FAR}/{EXPECTED_NEAR} — published figure not "
              f"reproduced — stop.")
    pctA = 100.0 * n_farA / len(fr)
    print(f"  G2 PASS: original figure reproduced EXACTLY: far(>{CUTOFF:.0f} A) "
          f"= {n_farA}, near = {n_nearA}, n = {len(fr)}, "
          f"positions = {fr['position'].nunique()} -> {pctA:.4f}% "
          f"= the published 96.22% (RELIABILITY_LOG L1058)")

    # ---- E2b: dimer-aware minimum over both copies of both sites -----
    dAB = np.array([float(np.linalg.norm(pos["A"][p] - b222))
                    for p in fr["position"]])       # p in A, 222 in B
    hasB = np.array([p in pos["B"] for p in fr["position"]])
    dBA = np.where(hasB,
                   [float(np.linalg.norm(pos["B"][p] - a222))
                    if p in pos["B"] else np.nan
                    for p in fr["position"]], np.nan)
    dBB = np.where(hasB,
                   [float(np.linalg.norm(pos["B"][p] - b222))
                    if p in pos["B"] else np.nan
                    for p in fr["position"]], np.nan)
    stack4 = np.vstack([dAA, dAB,
                        np.where(hasB, dBA, np.nan),
                        np.where(hasB, dBB, np.nan)])
    dmin4 = np.nanmin(stack4, axis=0)              # PRIMARY
    dminA = np.minimum(dAA, dAB)                   # sensitivity (variant
    #                                          fixed in chain A, task's
    #                                          literal reading)

    # G5: identity checks (inside the definition's own output)
    if np.any(dmin4 > dAA + 1e-12):
        gfail(f"G5 FAIL: d_min exceeds d_AA on "
              f"{int((dmin4 > dAA + 1e-12).sum())} rows — the four-pair "
              f"min does not contain the chain-A pair — stop.")
    farD = dmin4 > CUTOFF
    if np.any(farD & ~farA):
        gfail(f"G5 FAIL: {int((farD & ~farA).sum())} rows far under the "
              f"dimer definition but near under the monomer — impossible "
              f"by construction — stop.")
    print(f"  G5 PASS: identity holds — d_min <= d_AA everywhere "
          f"(max excess = {float(np.max(dmin4 - dAA)):+.3e} <= 0) and "
          f"far(dimer) rows are a SUBSET of far(monomer) rows")

    # ---- E2b results -------------------------------------------------
    farD4 = int((dmin4 > CUTOFF).sum())
    farDA = int((dminA > CUTOFF).sum())
    pctD = 100.0 * farD4 / len(fr)
    flipped = int((farA & ~farD).sum())      # rows pulled into contact
    n_changed_pos = int((dmin4 < dAA - 1e-12).sum())

    banner("E2b — LONG-RANGE PERCENTAGE, both definitions side by side", "-")
    print(f"  denominator: the ORIGINAL figure's frozen frame — "
          f"{len(fr)} variant rows / {fr['position'].nunique()} positions "
          f"(task77 rows with own_e_b finite)")
    print(f"  ORIGINAL monomer-only (chain A):  far(>{CUTOFF:.0f} A) = "
          f"{n_farA}/{len(fr)} = {pctA:.4f}%   [published as 96.22%]")
    print(f"  DIMER-AWARE (four-pair min, PRIMARY): far = {farD4}/{len(fr)} "
          f"= {pctD:.4f}%")
    print(f"  sensitivity (variant fixed in chain A, min over 222's two "
          f"copies): far = {farDA}/{len(fr)} = {100.0 * farDA / len(fr):.4f}%")
    print(f"  rows pulled INTO contact range through the opposite "
          f"subunit: {flipped} (and {n_changed_pos} rows have d_min "
          f"< d_AA at all)")
    d_hist = dmin4 - dAA
    q = np.percentile(d_hist, [0, 25, 50, 75, 100])
    print(f"  d_min - d_AA quantiles [0/25/50/75/100%]: "
          f"[{q[0]:+.4f}, {q[1]:+.4f}, {q[2]:+.4f}, {q[3]:+.4f}, "
          f"{q[4]:+.4f}] A  (all <= 0 by construction)")
    n_differ = int((np.abs(dmin4 - dminA) > 1e-12).sum())
    if n_differ == 0:
        print(f"  SENS (four-pair vs chain-A-variant min): differ on "
              f"0/{len(fr)} rows — the two readings coincide exactly on "
              f"this frame (two-fold symmetry holds to 1e-12 here)")
    else:
        print(f"  SENS (four-pair vs chain-A-variant min): differ on "
              f"{n_differ}/{len(fr)} rows — PRIMARY (four-pair) is the "
              f"smaller/enveloping one by construction")
    # two-fold symmetry diagnostics (descriptive)
    both = [p for p in fr["position"].unique() if p in pos["B"]]
    sym1 = max(abs(float(np.linalg.norm(pos["A"][p] - a222)) -
                   float(np.linalg.norm(pos["B"][p] - b222)))
               for p in both)
    sym2 = max(abs(float(np.linalg.norm(pos["A"][p] - b222)) -
                   float(np.linalg.norm(pos["B"][p] - a222)))
               for p in both)
    print(f"  symmetry diagnostics (descriptive): max|d_AA - d_BB| = "
          f"{sym1:.4f} A; max|d_AB - d_BA| = {sym2:.4f} A over "
          f"{len(both)} frame positions present in both chains")
    pos_farA = len({p for p, f in zip(fr['position'], farA) if f})
    pos_farD = len({p for p, f in zip(fr['position'], farD) if f})
    print(f"  position-level (descriptive): monomer far = {pos_farA}/586; "
          f"dimer far = {pos_farD}/586")

    # ---- G6: AD7 session reuse cross-check ---------------------------
    t80 = pd.read_csv(files["AD7 dimer positions"], usecols=["position"])
    s80 = set(int(p) for p in t80["position"].unique())
    sfr = set(int(p) for p in fr["position"].unique())
    print(f"  G6 INFO: task80_dimer_positions has {len(s80)} positions; "
          f"frame has {len(sfr)}; symmetric difference = "
          f"{sorted(s80 ^ sfr) if s80 ^ sfr else 'EMPTY (identical)'} "
          f"— AD7 session scored exactly this frame's positions"
          if s80 == sfr else
          f"  G6 INFO: task80 positions {len(s80)} vs frame {len(sfr)}; "
          f"only-task80={sorted(s80 - sfr)[:10]} only-frame="
          f"{sorted(sfr - s80)[:10]} — reported, not gated")

    # ---- E2c: coordinate counts per definition -----------------------
    dimer_missing = UNIVERSE - (set(pos["A"]) | set(pos["B"]))
    b_missing = UNIVERSE - set(pos["B"])
    rescued = mono_missing & set(pos["B"])
    if not dimer_missing <= mono_missing:
        gfail(f"G7 FAIL: dimer-missing not a subset of monomer-missing "
              f"({sorted(dimer_missing - mono_missing)}) — impossible — "
              f"stop.")
    banner("E2c — ATLAS POSITIONS WITH NO COORDINATES, by definition", "-")
    print(f"  G7 PASS: dimer-missing ({len(dimer_missing)}) is a subset "
          f"of monomer-missing ({len(mono_missing)}) — required by "
          f"construction (A-or-B absent implies A absent)")
    print(f"  atlas universe U: {len(UNIVERSE)} positions ({{2..656}})")
    print(f"  monomer (chain A) missing:   {len(mono_missing)} "
          f"-> with coordinates {len(set(pos['A']) & UNIVERSE)}; "
          f"list = {sorted(mono_missing)}")
    print(f"  chain B missing over U:      {len(b_missing)} "
          f"-> with coordinates {len(set(pos['B']) & UNIVERSE)}")
    print(f"  DIMER (A or B) missing:      {len(dimer_missing)} "
          f"-> with coordinates {len(UNIVERSE - dimer_missing)}; "
          f"list = {sorted(dimer_missing)}")
    print(f"  positions chain B RESCUES that A lacks: {len(rescued)} "
          f"-> {sorted(rescued) if rescued else 'none'}")
    only_A = set(pos["A"]) - set(pos["B"])
    print(f"  (chain-B window 41..648 is narrower: positions A has but B "
          f"lacks = {len(only_A)} -> {sorted(only_A)} — reported per "
          f"limitation 3)")

    # ---- CSV ---------------------------------------------------------
    rows = []
    for p in sorted(UNIVERSE):
        in_A, in_B = p in pos["A"], p in pos["B"]
        d = {}
        d["d_AA"] = (float(np.linalg.norm(pos["A"][p] - a222))
                     if in_A else np.nan)
        d["d_AB"] = (float(np.linalg.norm(pos["A"][p] - b222))
                     if in_A else np.nan)
        d["d_BA"] = (float(np.linalg.norm(pos["B"][p] - a222))
                     if in_B else np.nan)
        d["d_BB"] = (float(np.linalg.norm(pos["B"][p] - b222))
                     if in_B else np.nan)
        vals = [v for v in (d["d_AA"], d["d_AB"], d["d_BA"], d["d_BB"])
                if np.isfinite(v)]
        dmin = min(vals) if vals else np.nan
        dminAv = (min(d["d_AA"], d["d_AB"]) if in_A else np.nan)
        rows.append(dict(
            position=p, in_phase5=p in ph_set, in_frame=p in sfr,
            has_A=in_A, has_B=in_B,
            d_AA=d["d_AA"], d_AB=d["d_AB"], d_BA=d["d_BA"], d_BB=d["d_BB"],
            d_min_four=dmin, d_min_variantA=dminAv,
            far_AA=(d["d_AA"] > CUTOFF) if in_A else None,
            far_dimer_four=(dmin > CUTOFF) if np.isfinite(dmin) else None,
            far_dimer_variantA=(dminAv > CUTOFF)
                                if np.isfinite(dminAv) else None))
    out = PROC / "task107_e2_dimer_distances.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n  saved {len(rows)} position rows -> {out.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print("""  1. C-alpha only, one static crystal structure (6FCX) — same
     atom choice and structure as the original figure (comparability
     over refinement); solution dynamics not represented.
  2. The four-pair min is a GEOMETRIC lower envelope: contact
     structurally possible, not proven occupied or functional.
  3. Chain B's window (41-648) is narrower than chain A's (40-651);
     positions 40, 649-651 have A-only coordinates (A covers them).
  4. Denominators never mixed: rows 9,595 (primary), frame positions
     586, atlas universe 655 — each number labeled with its own.
  5. Descriptive deterministic census: no resampling, no p-value, no
     CI, no null — it restates geometry under a corrected definition.
  6. Existing scripts/CSVs read-only; nothing overwritten.
""")
    print(f"\nSCRIPT 107 DONE ({time.time() - t0:.1f}s)  "
          f"monomer {n_farA}/{len(fr)} = {pctA:.4f}%  |  "
          f"dimer {farD4}/{len(fr)} = {pctD:.4f}%  |  "
          f"mono-missing {len(mono_missing)} / dimer-missing "
          f"{len(dimer_missing)}")


if __name__ == "__main__":
    main()
