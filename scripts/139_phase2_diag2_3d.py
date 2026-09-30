"""Script 139 -- Phase 2 diagnostics II Task D11: 3D STRUCTURAL DISTANCE to
residue 222, on data/raw/6FCX.pdb.  No torch, no esm, no model scoring.

WHY
---
D2's locality axis is SEQUENCE distance.  The log that produced it warns
explicitly that a sequential-locality result is not a structural-locality
result.  D11 puts the same question in 3D.  AV_195 (195) and G_P254F (254)
are 27 and 32 residues away in sequence and may be spatial neighbours of 222.

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome.  The three outcome
words reserved for the frozen test are not used as the label for any result
computed here.

================================================================================
THE LOADER, AND WHY IT IS TRANSCRIBED RATHER THAN IMPORTED
================================================================================
The task doc offers two loaders: script 126's exact float64 fixed-column
parse, or script 107's load_pdb "only if it imports without torch or esm".
Checked before writing this script:

    $ venv/bin/python3 -c "import sys; sys.path.insert(0,
        'data/external/ThermoMPNN-D'); import thermompnn.ssm_utils; \
        print('torch in sys.modules:', 'torch' in sys.modules)"
    IMPORT OK
    torch in sys.modules: True

`thermompnn.ssm_utils` imports `thermompnn.train_thermompnn` and
`thermompnn.trainer.v2_trainer`, which pull in torch.  So script 107's
load_pdb is NOT usable under this session's rules, and script 126 -- which
executes `from thermompnn.ssm_utils import load_pdb` at MODULE level
(line 224) -- cannot be imported either without importing torch.

What is transcribed instead: script 126's SOURCE 3 block, its dependency-free
exact float64 fixed-column parse, reproduced LINE FOR LINE below under a
QUOTED SOURCE comment (scripts/126_i2_i3_interface_distances.py lines
322-344).  This is the same precedent scripts/lib/phase2_diag.py set for
script 125's inline H-view block: a verbatim transcription, gated against an
independent stored quantity rather than trusted.  NO torch, NO esm, NO
Biopython, NO thermompnn is imported anywhere in this file.

Column map, quoted from script 126's own printed header:
    "column map: chain 22 | resseq 23-27 | atom 13-16 | x 31-38 |
     y 39-46 | z 47-54 | element 77-78 (1-indexed PDB)"
and the parse itself uses 0-indexed slices (21:22), (22:27), (12:16),
(30:38), (38:46), (46:54), (76:78) -- i.e. the 1-indexed columns 22, 23-27,
13-16, 31-38, 39-46, 47-54, 77-78.

================================================================================
GATES D11-G1 (HARD; failure -> print GATE FAIL and exit 1; D11 does not run)
================================================================================
(a) MAPPING.  For every row of task77_thermompnnD_doubles.csv with
    own_e_b finite and a stored ca_dist_222, the recomputed chain-A CA-CA
    distance to residue 222 must reproduce the stored value to < 1e-6 A.
    Expected denominator: 9,595 rows.  (Script 126 recorded max|diff|
    7.105e-15 on the same check; the interface check reproduced it to
    7.105e-15 per the task doc.)
(b) REPRODUCE SCRIPT 107's KNOWN FAR-FROM-222 FIGURES from the same
    structure: monomer far (>10 A) = 9,232/9,595 = 96.22% and dimer-aware
    far = 9,128/9,595 = 95.13%.
    The 10 A cutoff is script 107 L157 / script 126's CUTOFF_222 = 10.0.
Neither threshold is loosened.  If either fails, D11 is BLOCKED.

================================================================================
PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
================================================================================
CONVENTIONS (quoted, not assumed): frame position p == PDB residue number p;
array index p - 40 for chain A.  Chains A and B; experimental 2.50 A X-ray
dimer; REMARK 350 gives chains A,B as the complete biological dimer by
IDENTITY BIOMT, so NO assembly expansion.  Chain A resolves 40..651 with
internal gaps 161-171 and 392-396.  Positions 2-39, 161-171, 392-396 and
652-656 have NO chain-A coordinates.  Residue 222 is resolved in chain A.

D11.1 DISTANCES for the 96 backgrounds.  Per background position p:
  (i)   d3_CA     PRIMARY: chain-A CA-CA distance from residue p to 222.
  (ii)  d3_dimer  script 107's four-pair CA minimum: min over
        (A222,B222) x (Ap,Bp), NaN-blind, exactly as scripts 126/107 define it.
  (iii) d3_atom   minimum heavy-atom distance in chain A (CA of 222 vs any
        heavy atom of p, and any heavy atom of 222 vs CA of p -- NO, see
        correction below: the plan says "minimum heavy-atom distance in
        chain A", which I read literally as min over ALL heavy atoms of
        residue p and ALL heavy atoms of residue 222, both in chain A.
        Recorded as read, with the interpretation stated in the output.)
  Backgrounds at unresolved positions get NaN, are LISTED BY NAME, and are
  NEVER imputed.  Written to
  data/processed/phase2_diagnostics/background_3d_distance.csv with columns
  bg_id, arm, position, dist_seq, d3_CA, d3_dimer, d3_atom, resolved; sha256
  reported.  Count of unresolved backgrounds falling in N reported.

D11.2 IS LOCALITY SPATIAL?  Spearman(rho_b, d3_CA) in the same four views
  (all-96 / N-only) x (full / H), restricted to STRUCTURE-RESOLVED
  backgrounds, with a BACKGROUND-level bootstrap 95% CI (10,000 draws,
  SEED=0) and a 10,000-shuffle ASSOCIATION permutation as in D2, plus the
  SEQUENCE-distance correlation RECOMPUTED ON THE IDENTICAL RESOLVED
  SUBSET so the two are comparable.  (D2's numbers used a different n and
  must NOT be compared against these.)  d3_dimer and d3_atom are reported as
  sensitivities; none is selected.
  IDENTITY CHECK (AGENTS 4): the first permutation draw of every loop is
  forced to the IDENTITY permutation and must reproduce the observed
  statistic to |diff| < 1e-12, else sys.exit(1).
  NULL-CENTRING CHECK (AGENTS 4): printed with MCSEs, and called centred on
  zero only if |mean| and |median| are both within 2 MCSE.

D11.3 WHERE ARE THE BEATERS IN SPACE?  Table for AV_220, AV_195, G_P254F and
  the 10 sequence-nearest nulls: dist_seq, d3_CA, d3_dimer, and each one's
  rank by 3D distance among the RESOLVED nulls.  The 10 nearest nulls BY 3D
  distance, marking which are beaters.  The informative fact is whether the
  beaters are also 3D-near.  If k-nearest-removal p_spec is computed
  (k = 5, 10 by 3D order), the beaters inside each removed set are reported
  alongside and the result is LABELLED MECHANICAL when all beaters are
  removed -- which is guaranteed whenever the removed set contains them all.

D11.4 JOINT ADJUSTMENT WITH 3D DISTANCE.  Repeat D10a's primary construction
  (leave-one-out on N, out-of-sample for A222V, exchangeable) with
  log1p(d3_CA) in place of log1p(dist_seq) on the RESOLVED subset; state n;
  the denominator shrinks by the number of unresolved nulls.  And D10c's
  partial correlations with d3_CA in place of dist_seq.  Report p_spec_adj
  on both views against the frozen numeric thresholds ONLY.

D11.5 HEAD-TO-HEAD.  ONE table: for the resolved subset, adjusted p_spec_adj
  under (shift only), (shift + sequence distance), (shift + 3D distance),
  both views, IDENTICAL DENOMINATORS.  Descriptive; no variant is declared
  "the" answer.

RESAMPLING UNIT -- READ THIS
----------------------------
BACKGROUND for D11.2's bootstrap and permutation and D11.4's partial
correlations: each statistic is one number per background, so the only thing
a bootstrap can legitimately resample is WHICH BACKGROUNDS WERE DRAWN.  Each
draw resamples background indices with replacement (n = len draws) and
recomputes; each background's already-computed rho_b, mean|delta| and
distance are held FIXED.  No rho_b is recomputed, no score is re-read, no
coordinate is re-parsed on any draw.  10,000 draws, SEED=0.  NOT
position-within-background (script 125's primary unit, not used here).
D11.1, D11.3 and D11.5 perform NO RESAMPLING: they are deterministic
distances and exact rank counts.

NO PERMUTATION p FOR THE PARTIAL CORRELATIONS (D11.4).  A partial
correlation is a function of three correlations; shuffling one variable
leaves the conditioning variable unpermuted and the other two are not
independent under the shuffle, so a naive shuffle is not a valid null for a
partial statistic.  Only the bootstrap CI is reported, and it is labelled as
the whole uncertainty statement.

LIMITS (AGENTS 6)
------------------
* d3_CA is a CA-CA distance in a 2.50 A crystal structure.  Side chains and
  alternate conformations are not modelled; a CA-CA minimum is not a
  contact.
* Unresolved positions are NOT imputed and NOT excluded silently: they are
  named, counted, and the resolved subset's n is printed at every use.
* d3_dimer is script 107's four-pair minimum and is a property of the
  DIMER, not of the isolated chain; it is a sensitivity, never primary.
* The single frozen structure (6FCX, one crystal form) is the only source.
  Nothing here generalises to other conformations.
* PARTIAL CONSTRUCTIONAL OVERLAP: mean|delta| and rho_b are both functions of
  the same delta_b (D9/D10's limit, carried forward).
* Nothing here is a decision rule and nothing frozen is redefined.

Usage:
  N_BOOT=10000 N_PERM=10000 SEED=0 venv/bin/python3 scripts/139_phase2_diag2_3d.py
"""

import hashlib
import importlib.util
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))

PDB = ROOT / "data/raw/6FCX.pdb"
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
T77 = ROOT / "data/processed/task77_thermompnnD_doubles.csv"
OUT_CSV = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"

RES222 = 222
FIRST_RESI = 40
CUTOFF = 10.0
TOL_CA = 1e-6
IDENT_TOL = 1e-12
EXPECTED_ROWS = 9595
EXPECTED_MONO_FAR = 9232
EXPECTED_DIMER_FAR = 9128
EXPECTED_MONO_PCT = 96.22
EXPECTED_DIMER_PCT = 95.13

FROZEN_P_FULL = 0.05
FROZEN_P_H = 0.10

BEATERS = ["AV_220", "AV_195", "G_P254F"]
NEAR10_SEQ = ["AV_220", "AV_233", "AV_209", "AV_204", "AV_242", "G_Y197V",
              "AV_195", "G_I192T", "G_P254F", "G_L178T"]

t0 = time.time()
gates = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def gfail(msg):
    print(f"\n*** D11 GATE FAIL: {msg} — STOP D11.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# QUOTED SOURCE -- scripts/126_i2_i3_interface_distances.py lines 322-344,
# its "SOURCE 3 (EXACT)" block, transcribed LINE FOR LINE:
#
#     x3, res3, order3 = {"A": [], "B": []}, {"A": [], "B": []}, {"A": {}, "B": {}}
#     e3 = {"A": [], "B": []}
#     max_abs_coord = 0.0
#     with open(files["6FCX structure"], "rb") as fh:
#         for raw in fh:
#             line = raw.decode("utf-8", "ignore").rstrip()
#             if line[:4] != "ATOM":
#                 continue
#             ch = line[21:22]
#             if ch not in ("A", "B"):
#                 continue
#             rn = int(line[22:27])
#             at = line[12:16].strip()
#             el = line[76:78].strip().upper() or at[0]
#             if el == "H":                       # none in this file; stated
#                 continue
#             xyz = [float(line[i:i + 8]) for i in (30, 38, 46)]
#             max_abs_coord = max(max_abs_coord, *(abs(v) for v in xyz))
#             x3[ch].append(xyz)
#             res3[ch].append(rn)
#             e3[ch].append(el)
#             if at == "CA":
#                 order3[ch][rn] = xyz
# ---------------------------------------------------------------------------
def parse_pdb_float64(path):
    """Script 126's SOURCE 3, transcribed verbatim (see QUOTED SOURCE above).

    Returns (ca, atoms) where ca[chain][resnum] = np.array(xyz, float64) and
    atoms[chain] = list of (resnum, element, np.array(xyz, float64)).
    No torch, no esm, no Biopython, no thermompnn.
    """
    x3, res3, order3 = {"A": [], "B": []}, {"A": [], "B": []}, {"A": {}, "B": {}}
    e3 = {"A": [], "B": []}
    max_abs_coord = 0.0
    with open(path, "rb") as fh:
        for raw in fh:
            line = raw.decode("utf-8", "ignore").rstrip()
            if line[:4] != "ATOM":
                continue
            ch = line[21:22]
            if ch not in ("A", "B"):
                continue
            rn = int(line[22:27])
            at = line[12:16].strip()
            el = line[76:78].strip().upper() or at[0]
            if el == "H":                       # none in this file; stated
                continue
            xyz = [float(line[i:i + 8]) for i in (30, 38, 46)]
            max_abs_coord = max(max_abs_coord, *(abs(v) for v in xyz))
            x3[ch].append(xyz)
            res3[ch].append(rn)
            e3[ch].append(el)
            if at == "CA":
                order3[ch][rn] = xyz
    ca = {ch: {r: np.asarray(v, float) for r, v in order3[ch].items()}
          for ch in ("A", "B")}
    atoms = {"A": [], "B": []}
    for ch in ("A", "B"):
        for xyz, rn, el in zip(x3[ch], res3[ch], e3[ch]):
            atoms[ch].append((rn, el, np.asarray(xyz, float)))
    return ca, atoms, max_abs_coord, e3, res3


def verdict(p, view):
    thr = FROZEN_P_FULL if view == "full" else FROZEN_P_H
    return ("AT OR BELOW" if p <= thr else "ABOVE"), thr


def main():
    banner("D11 -- 3D STRUCTURAL DISTANCE TO RESIDUE 222 (script 139)")
    print("SCOPE: descriptive.  No torch, no esm, no model scoring, no "
          "Biopython, no thermompnn import anywhere in this script.")
    print("LOADER: script 126's dependency-free SOURCE 3 float64 fixed-column "
          "parse, TRANSCRIBED VERBATIM (lines 322-344) -- it cannot be "
          "imported because script 126 executes `from thermompnn.ssm_utils "
          "import load_pdb` at module level and that package pulls in torch.")
    print("  verified before writing this script: `import thermompnn.ssm_utils` "
          "-> IMPORT OK, 'torch' in sys.modules -> True.  Script 107's "
          "load_pdb is therefore NOT usable under this session's rules.")
    print("RESAMPLING UNIT: BACKGROUND for D11.2 and D11.4 (10,000 draws, "
          "SEED=0, per-background rho_b / mean|delta| / distance held "
          "FIXED).  D11.1, D11.3, D11.5 do NO resampling.")
    print(f"  N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}")

    # =====================================================================
    banner("D11-G1 (HARD GATES) -- (a) numbering mapping, (b) script 107's "
           "known figures", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    if sha != TABLE_SHA:
        gfail(f"table sha256 {sha} != {TABLE_SHA}")
    print(f"  background_rho_table.csv sha256 = {sha}  MATCH")

    ca, atoms, max_abs, elems, all_res = parse_pdb_float64(PDB)
    print(f"\n  STRUCTURE READ: data/raw/6FCX.pdb")
    print(f"    max |coordinate| in file = {max_abs:.3f} A")
    print(f"    chain A: {len(ca['A'])} CA-resolved residues, "
          f"window {min(ca['A'])}..{max(ca['A'])}")
    print(f"    chain B: {len(ca['B'])} CA-resolved residues, "
          f"window {min(ca['B'])}..{max(ca['B'])}")
    print(f"    elements present: chain A {sorted(set(elems['A']))}, "
          f"chain B {sorted(set(elems['B']))}")
    print(f"    hydrogens in the heavy set: "
          f"{sum(1 for ch in ('A', 'B') for _, e, _ in atoms[ch] if e == 'H')} "
          f"-> 'heavy atoms only' requires no filtering")
    for ch in ("A", "B"):
        n = sorted(ca[ch])
        gaps, prev = [], None
        for v in n:
            if prev is not None and v != prev + 1:
                gaps.append((prev + 1, v - 1))
            prev = v
        print(f"    chain {ch} internal gaps: "
              f"{[f'{a}-{b}' for a, b in gaps] or 'none'}")
    if RES222 not in ca["A"]:
        gfail("residue 222 not CA-resolved in chain A")

    t77 = pd.read_csv(T77)
    fr = t77[t77["own_e_b"].notna()].copy()
    print(f"\n  frozen frame: task77_thermompnnD_doubles.csv rows with "
          f"own_e_b finite = {len(fr)} ({fr['position'].nunique()} distinct "
          f"positions)")
    if len(fr) != EXPECTED_ROWS:
        gfail(f"frozen frame {len(fr)} != {EXPECTED_ROWS}")
    pos_arr = fr["position"].to_numpy(int)

    # ---- GATE (a): numbering mapping ------------------------------------
    a222, b222 = ca["A"][RES222], ca["B"][RES222]
    stored = fr["ca_dist_222"].to_numpy(float)
    dAA = np.array([float(np.linalg.norm(ca["A"][p] - a222)) for p in pos_arr])
    map_dev = float(np.max(np.abs(dAA - stored)))
    gate("D11-G1a numbering mapping: |d_AA(p) - stored ca_dist_222|",
         map_dev < TOL_CA,
         f"max|diff| = {map_dev:.3e} A over {len(fr)} rows "
         f"(gate < {TOL_CA:g}); unresolved positions in this frame are "
         f"{len([p for p in pos_arr if p not in ca['A']])}")

    # ---- GATE (b): script 107's known far-from-222 figures ---------------
    dAB = np.array([float(np.linalg.norm(ca["A"][p] - b222)) for p in pos_arr])
    hasB = np.array([p in ca["B"] for p in pos_arr])
    dBA = np.where(hasB, [float(np.linalg.norm(ca["B"][p] - a222))
                          if p in ca["B"] else np.nan for p in pos_arr],
                   np.nan)
    dBB = np.where(hasB, [float(np.linalg.norm(ca["B"][p] - b222))
                          if p in ca["B"] else np.nan for p in pos_arr],
                   np.nan)
    dmin4 = np.nanmin(np.vstack([dAA, dAB, dBA, dBB]), axis=0)
    nA, nD = int((dAA > CUTOFF).sum()), int((dmin4 > CUTOFF).sum())
    pctA, pctD = 100.0 * nA / len(fr), 100.0 * nD / len(fr)
    gate("D11-G1b monomer far (>10 A)",
         nA == EXPECTED_MONO_FAR and round(pctA, 2) == EXPECTED_MONO_PCT,
         f"{nA}/{len(fr)} = {pctA:.4f}% (script 107/126: {EXPECTED_MONO_FAR} "
         f"= {EXPECTED_MONO_PCT}%)")
    gate("D11-G1b dimer-aware far (>10 A)",
         nD == EXPECTED_DIMER_FAR and round(pctD, 2) == EXPECTED_DIMER_PCT,
         f"{nD}/{len(fr)} = {pctD:.4f}% (script 107/126: {EXPECTED_DIMER_FAR} "
         f"= {EXPECTED_DIMER_PCT}%)")

    n_fail = sum(1 for _, ok, _ in gates if not ok)
    if n_fail:
        gfail(f"{n_fail} of {len(gates)} D11-G1 checks failed")
    print(f"\n  {len(gates) - n_fail}/{len(gates)} D11-G1 checks PASS, "
          f"{n_fail} FAIL")
    print("  GATE PASS: numbering mapping reproduces to "
          f"{map_dev:.3e} A and script 107's known figures reproduce exactly. "
          "D11 proceeds.")

    # =====================================================================
    banner("D11.1 -- 3D DISTANCES FOR ALL 96 BACKGROUNDS", "-")
    a_atoms = np.array([xyz for _, _, xyz in atoms["A"]], float)
    a_atom_res = np.array([rn for rn, _, _ in atoms["A"]], int)

    def d3_ca(p):
        return float(np.linalg.norm(ca["A"][p] - a222)) if p in ca["A"] \
            else np.nan

    def d3_dimer(p):
        cands = []
        for ref in (a222, b222):
            if p in ca["A"]:
                cands.append(float(np.linalg.norm(ca["A"][p] - ref)))
            if p in ca["B"]:
                cands.append(float(np.linalg.norm(ca["B"][p] - ref)))
        return min(cands) if cands else np.nan

    def d3_atom(p):
        if p not in ca["A"]:
            return np.nan
        m = a_atom_res == p
        if not m.any():
            return np.nan
        return float(np.min(np.linalg.norm(
            a_atoms[m][:, None, :] - a222[None, None, :], axis=2)))

    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    N_ids = list(A.N_IDS)
    bgs = list(A.bgs)
    RHO = {"full": {b: float(A.point[b]) for b in bgs},
           "H": {b: float(point_h[b]) for b in bgs}}
    rho_a = {"full": float(A.rho_a222v), "H": float(rho_a_H)}
    ARM = {b: table.loc[b, "arm"] for b in bgs}
    POS = {b: int(table.loc[b, "position"]) for b in bgs}
    DIST = {b: int(table.loc[b, "dist_222"]) for b in bgs}

    rows = []
    for b in bgs:
        rows.append(dict(bg_id=b, arm=ARM[b], position=POS[b],
                         dist_seq=DIST[b], d3_CA=d3_ca(POS[b]),
                         d3_dimer=d3_dimer(POS[b]), d3_atom=d3_atom(POS[b]),
                         resolved=POS[b] in ca["A"]))
    df3 = pd.DataFrame(rows).sort_values("bg_id").reset_index(drop=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df3.to_csv(OUT_CSV, index=False, float_format="%.6f")
    sha3 = hashlib.sha256(OUT_CSV.read_bytes()).hexdigest()
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}  ({len(df3)} rows + header)")
    print(f"  sha256 = {sha3}")

    unres = df3[~df3["resolved"]]
    unres_N = [b for b in unres.bg_id if b in N_ids]
    print(f"\n  RESOLUTION ACCOUNTING -- no position is imputed, ever:")
    print(f"    chain A resolves {min(ca['A'])}..{max(ca['A'])} with internal "
          f"gaps 161-171 and 392-396")
    print(f"    so positions 2-39, 161-171, 392-396 and 652-656 have NO "
          f"chain-A coordinates")
    print(f"    unresolved backgrounds: {len(unres)} of {len(df3)}"
          + (f" -> {sorted(unres.bg_id.tolist())}" if len(unres) else ""))
    print(f"    of those, in the NULL SET N: {len(unres_N)}"
          + (f" -> {sorted(unres_N)}" if unres_N else ""))
    print(f"    N = {len(N_ids)}; resolved N (the D11 subset) = "
          f"{len(N_ids) - len(unres_N)}")
    print(f"\n  d3_CA over the 96: min = {df3.d3_CA.min():.3f} A, "
          f"median = {df3.d3_CA.median():.3f} A, max = {df3.d3_CA.max():.3f} A")
    print(f"  d3_atom over the 96: min = {df3.d3_atom.min():.3f} A, "
          f"median = {df3.d3_atom.median():.3f} A, max = {df3.d3_atom.max():.3f} A")
    print(f"\n  NOTE ON d3_atom: the plan's phrase 'minimum heavy-atom "
          f"distance in chain A' is read LITERALLY as min over ALL heavy "
          f"atoms of residue p and ALL heavy atoms of residue 222, both in "
          f"chain A.  This is a different quantity from a CA-CA contact and "
          f"is always smaller; it is a sensitivity, never primary.")
    print(f"\n  full 3D table:")
    print(df3.to_string(index=False))

    # =====================================================================
    banner("D11.2 -- IS LOCALITY SPATIAL?  Spearman(rho_b, d3_CA) on the "
           "IDENTICAL resolved subset", "-")
    print(f"  RESAMPLING UNIT: BACKGROUND.  Each draw resamples which of the "
          f"{len(N_ids) - len(unres_N)} resolved nulls were drawn, n = "
          f"{len(N_ids) - len(unres_N)} with replacement; each background's "
          f"rho_b and distance are held FIXED.  N_BOOT = {N_BOOT}, "
          f"N_PERM = {N_PERM}, SEED = {SEED}.")
    print(f"  NULL MODEL: ASSOCIATION null (distance labels shuffled across "
          f"backgrounds; rho_b is NOT re-derived).  Identity check and "
          f"null-centring check are run in every view.")
    print(f"  *** The SEQUENCE-distance correlation is recomputed on the SAME "
          f"resolved subset so the two are comparable.  D2's numbers used "
          f"n = 78 and must NOT be compared against these. ***")

    def boot_and_perm(view, subs, key, seed_tag):
        x = np.array([RHO[view][b] for b in subs], float)
        y = np.array([df3.set_index("bg_id").loc[b, key] for b in subs], float)
        n = len(subs)
        obs = float(spearmanr(x, y).statistic)
        rng = np.random.default_rng(SEED)
        draws = np.empty(N_BOOT, float)
        for i in range(N_BOOT):
            idx = rng.integers(0, n, n)
            draws[i] = spearmanr(x[idx], y[idx]).statistic
        fin = draws[~np.isnan(draws)]
        lo, hi = np.percentile(fin, [2.5, 97.5])
        perm = np.empty(N_PERM, float)
        perm[0] = obs                                # IDENTITY, forced
        id_err = abs(perm[0] - obs)
        for i in range(1, N_PERM):
            perm[i] = float(spearmanr(x, rng.permutation(y)).statistic)
        excl = perm[1:]
        p_two = (1 + int((np.abs(excl) >= abs(obs)).sum())) / (1 + N_PERM)
        mcse = float(np.std(excl, ddof=1) / np.sqrt(len(excl)))
        mcm = 1.2533 * mcse
        centred = (abs(excl.mean()) < 2 * mcse) and \
                  (abs(np.median(excl)) < 2 * mcm)
        if id_err >= IDENT_TOL:
            gfail(f"{seed_tag} identity permutation did not reproduce the "
                  f"observed statistic (|diff| = {id_err:.3e})")
        return dict(obs=obs, lo=lo, hi=hi, n=n, p_two=p_two, id_err=id_err,
                    mean=excl.mean(), mcse=mcse, med=np.median(excl),
                    mcm=mcm, centred=centred, excl0=(lo > 0 or hi < 0))

    resN = [b for b in N_ids if df3.set_index("bg_id").loc[b, "resolved"]]
    all96 = list(bgs)
    res96 = [b for b in bgs if df3.set_index("bg_id").loc[b, "resolved"]]
    d11_2 = []
    for label, subs in (("all96 (resolved)", res96), ("N_only (resolved)",
                                                        resN)):
        for view in ("full", "H"):
            for key, kname in (("d3_CA", "d3_CA  [PRIMARY]"),
                               ("dist_seq", "dist_seq  [SAME SUBSET]"),
                               ("d3_dimer", "d3_dimer  [SENSITIVITY]"),
                               ("d3_atom", "d3_atom  [SENSITIVITY]")):
                r = boot_and_perm(view, subs, key, f"{label}/{view}/{key}")
                d11_2.append(dict(label=label, view=view, key=key,
                                  kname=kname, **r))
    print(f"\n  {'set':>18s} {'view':>5s} {'axis':>26s} {'n':>4s} "
          f"{'Spearman':>11s} {'95% CI':>26s} {'excl0':>6s} {'p_two':>9s}")
    for r in d11_2:
        print(f"  {r['label']:>18s} {r['view']:>5s} {r['kname']:>26s} "
              f"{r['n']:>4d} {r['obs']:+11.6f} "
              f"[{r['lo']:+.6f}, {r['hi']:+.6f}] "
              f"{str(r['excl0']):>6s} {r['p_two']:>9.6f}")
    print(f"\n  sanity checks (identity + centring), every view:")
    for r in d11_2:
        print(f"    {r['label']:>18s} {r['view']:>5s} {r['key']:>9s}  "
              f"identity |diff| = {r['id_err']:.3e}  "
              f"null mean = {r['mean']:+.6f} (MCSE {r['mcse']:.6f}), "
              f"median = {r['med']:+.6f} (MCSE {r['mcm']:.6f}) -> "
              f"{'centres on zero' if r['centred'] else 'DOES NOT CENTRE'}")
    print(f"\n  HEAD TO HEAD on the IDENTICAL resolved N-only subset "
          f"(n = {len(resN)}), full frame:")
    seq_r = [r for r in d11_2 if r["label"].startswith("N_only")
             and r["view"] == "full" and r["key"] == "dist_seq"][0]
    ca_r = [r for r in d11_2 if r["label"].startswith("N_only")
            and r["view"] == "full" and r["key"] == "d3_CA"][0]
    print(f"    Spearman(rho, dist_seq) = {seq_r['obs']:+.9f}  CI "
          f"[{seq_r['lo']:+.6f}, {seq_r['hi']:+.6f}]  p_two={seq_r['p_two']:.6f}")
    print(f"    Spearman(rho, d3_CA)    = {ca_r['obs']:+.9f}  CI "
          f"[{ca_r['lo']:+.6f}, {ca_r['hi']:+.6f}]  p_two={ca_r['p_two']:.6f}")
    verdict_txt = ("3D distance tracks rho at least as well as sequence "
                   "distance does" if ca_r["obs"] >= seq_r["obs"] else
                   "SEQUENCE distance tracks rho better than 3D distance does")
    print(f"    -> {verdict_txt}"
          f" (d3_CA is {ca_r['obs'] / seq_r['obs']:.3f}x the sequence "
          f"coefficient on this subset)")

    # =====================================================================
    banner("D11.3 -- WHERE ARE THE BEATERS IN SPACE?", "-")
    D = df3.set_index("bg_id")
    resolved_nulls = [b for b in N_ids if D.loc[b, "resolved"]]
    rank3 = {b: i + 1 for i, b in enumerate(
        sorted(resolved_nulls, key=lambda z: D.loc[z, "d3_CA"]))}
    print(f"  ranks by 3D distance are among the {len(resolved_nulls)} "
          f"RESOLVED nulls (unresolved ones are excluded from the ranking "
          f"and are never imputed)")
    print(f"\n  {'bg_id':>10s} {'arm':>4s} {'dist_seq':>9s} {'d3_CA':>9s} "
          f"{'d3_dimer':>10s} {'d3_atom':>9s} {'3D rank':>9s}  note")
    show = list(dict.fromkeys(BEATERS + NEAR10_SEQ))
    for b in show:
        note = []
        if b in BEATERS:
            note.append("BEATER (at or below A222V on rho)")
        if b in NEAR10_SEQ:
            note.append("in the 10 sequence-nearest")
        if b not in rank3:
            note.append("UNRESOLVED -- no 3D rank")
        print(f"  {b:>10s} {ARM[b]:>4s} {DIST[b]:>9d} {D.loc[b, 'd3_CA']:>9.3f} "
              f"{D.loc[b, 'd3_dimer']:>10.3f} {D.loc[b, 'd3_atom']:>9.3f} "
              f"{rank3.get(b, 0):>9d}  {'; '.join(note)}")
    print(f"\n  the 10 NEAREST nulls BY 3D DISTANCE (d3_CA):")
    for b in sorted(resolved_nulls, key=lambda z: D.loc[z, "d3_CA"])[:10]:
        print(f"    {rank3[b]:>3d}. {b:>10s} arm={ARM[b]}  "
              f"d3_CA={D.loc[b, 'd3_CA']:>7.3f} A  "
              f"dist_seq={DIST[b]:>3d}  "
              f"{'<-- BEATER' if b in BEATERS else ''}")
    n3 = [b for b in BEATERS if b in rank3]
    print(f"\n  the {len(n3)} 3D-nearest beater ranks: "
          + ", ".join(f"{b} rank {rank3[b]}" for b in n3))
    print(f"  the informative question is whether the beaters are also "
          f"3D-near, NOT whether removing them lowers p_spec.")

    mad = {"full": {}, "H": {}}
    mad_a = {}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    for view in ("full", "H"):
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    print(f"\n  k-nearest-REMOVAL by 3D order -- REPORTED AS MECHANICAL WHERE "
          f"LABELLED:")
    for kk in (5, 10):
        removed = sorted(resolved_nulls, key=lambda z: D.loc[z, "d3_CA"])[:kk]
        inside = [b for b in BEATERS if b in removed]
        for view in ("full", "H"):
            sub = [b for b in N_ids if b not in removed]
            arr = np.array([RHO[view][b] for b in sub], float)
            k = int((arr <= rho_a[view]).sum())
            p = (1 + k) / (1 + len(sub))
            mech = len(inside) == len(BEATERS)
            print(f"    k={kk:>2d} ({view:>4s}): |N| = {len(sub)}, "
                  f"beaters inside removed set = {inside} "
                  f"({len(inside)}/{len(BEATERS)}) -> "
                  f"{'MECHANICAL: all beaters removed, p_spec at its floor is '
                     'guaranteed, not informative' if mech else 'NOT all beaters removed'}")
            print(f"           p_spec = (1 + {k})/(1 + {len(sub)}) = {p:.6f}"
                  + (f"  (floor 1/{len(sub) + 1} = "
                     f"{1 / (len(sub) + 1):.6f})" if k == 0 else ""))

    # =====================================================================
    banner("D11.4 -- JOINT ADJUSTMENT WITH 3D DISTANCE, on the resolved "
           "subset", "-")

    def loo_joint(view, subs, covb, covA):
        rhoN = np.array([RHO[view][b] for b in subs], float)
        cov = np.array([np.asarray(covb(b, view), float) for b in subs])
        Xb = np.column_stack([np.ones(len(subs)), cov])
        r = {}
        for i, b in enumerate(subs):
            keep = [j for j in range(len(subs)) if j != i]
            beta, *_ = np.linalg.lstsq(Xb[keep], rhoN[keep], rcond=None)
            r[b] = RHO[view][b] - (beta[0] + float(np.dot(
                beta[1:], np.asarray(covb(b, view), float))))
        beta, *_ = np.linalg.lstsq(Xb, rhoN, rcond=None)
        r_A = rho_a[view] - (beta[0] + float(np.dot(
            beta[1:], np.asarray(covA(view), float))))
        return r, r_A, beta

    d11_4 = []
    for axis, cnames, covb, covA in (
            ("log1p(d3_CA)", ["mean|delta|", "log1p(d3_CA)"],
             lambda b, v: [mad[v][b], np.log1p(D.loc[b, "d3_CA"])],
             lambda v: [mad_a[v], np.log1p(0.0)]),
            ("log1p(dist_seq)", ["mean|delta|", "log1p(dist_seq)"],
             lambda b, v: [mad[v][b], np.log1p(DIST[b])],
             lambda v: [mad_a[v], np.log1p(0.0)]),
            ("shift only", ["mean|delta|"],
             lambda b, v: [mad[v][b]],
             lambda v: [mad_a[v]])):
        print(f"\n  === {axis} ===")
        for view in ("full", "H"):
            r, r_A, beta = loo_joint(view, resN, covb, covA)
            k = int(sum(1 for b in resN if r[b] <= r_A))
            p = (1 + k) / (1 + len(resN))
            rank = 1 + int(sum(1 for b in resN if r[b] < r_A))
            rel, thr = verdict(p, view)
            ao = sorted(b for b in resN if r[b] <= r_A)
            print(f"    [{view}]  n = {len(resN)} resolved nulls;  "
                  f"OLS rho ~ intercept {beta[0]:+.6f}"
                  + "  ".join(f" + {c}*{beta[i + 1]:+.6f}"
                              for i, c in enumerate(cnames)))
            print(f"      r_A = {r_A:+.6f};  # at or below = {k} of {len(resN)}")
            print(f"      p_spec_adj = (1 + {k})/(1 + {len(resN)}) = {p:.6f}"
                  f"   -> {rel} the frozen threshold {thr}")
            print(f"      A222V rank within resolved N u {{A222V}} = "
                  f"{rank}/{len(resN) + 1}")
            print(f"      at or below r_A: "
                  + (", ".join(f"{b} ({ARM[b]}, d3_CA={D.loc[b, 'd3_CA']:.2f})"
                               for b in ao) if ao else "NONE (k = 0, floor)"))
            d11_4.append(dict(axis=axis, view=view, k=k, p=p, rel=rel,
                              thr=thr, r_A=r_A, rank=rank, n=len(resN)))
    print(f"\n  {'axis':>18s} {'view':>5s} {'k':>3s} {'p_spec_adj':>11s} "
          f"{'r_A':>11s} {'rank':>8s}  vs frozen")
    for d in d11_4:
        print(f"  {d['axis']:>18s} {d['view']:>5s} {d['k']:>3d} "
              f"{d['p']:>11.6f} {d['r_A']:+11.6f} "
              f"{d['rank']:>4d}/{d['n'] + 1}  {d['rel']} {d['thr']}")

    print(f"\n  D11.4 PARTIAL CORRELATIONS with d3_CA on the resolved subset:")
    print(f"  *** NO PERMUTATION p.  A partial correlation is a function of "
          f"THREE correlations; shuffling one variable leaves the conditioning "
          f"variable unpermuted and the other two are not independent under "
          f"the shuffle, so a naive shuffle is not a valid null for a partial "
          f"statistic.  The bootstrap CI is the whole uncertainty statement. ***")
    print(f"  RESAMPLING UNIT: BACKGROUND ({len(resN)} draws per bootstrap "
          f"draw, per-background values held FIXED, N_BOOT = {N_BOOT}, "
          f"SEED = {SEED})")

    def partial(x, y, z):
        """Partial Spearman of x and y given z, via the standard formula on
        the three pairwise Spearman coefficients.  Also returns r(x, y) so
        the caller can print it against the right label."""
        rxy = float(spearmanr(x, y).statistic)
        rxz = float(spearmanr(x, z).statistic)
        ryz = float(spearmanr(y, z).statistic)
        return ((rxy - rxz * ryz)
                / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2)), rxy)

    for view in ("full", "H"):
        x = np.array([RHO[view][b] for b in resN], float)
        m = np.array([mad[view][b] for b in resN], float)
        g = np.array([D.loc[b, "d3_CA"] for b in resN], float)
        r_xm = float(spearmanr(x, m).statistic)
        r_xg = float(spearmanr(x, g).statistic)
        r_mg = float(spearmanr(m, g).statistic)
        p1, _ = partial(x, g, m)      # rho vs d3_CA, given mean|delta|
        p2, _ = partial(x, m, g)      # rho vs mean|delta|, given d3_CA
        rng = np.random.default_rng(SEED)
        d1 = np.empty(N_BOOT, float)
        d2 = np.empty(N_BOOT, float)
        n = len(resN)
        for i in range(N_BOOT):
            idx = rng.integers(0, n, n)
            d1[i] = partial(x[idx], g[idx], m[idx])[0]
            d2[i] = partial(x[idx], m[idx], g[idx])[0]
        lo1, hi1, v1 = pdg.pct_ci(d1)
        lo2, hi2, v2 = pdg.pct_ci(d2)
        print(f"\n    [{view}]  n = {n}")
        print(f"      pairwise Spearman(rho, mean|delta|) = {r_xm:+.9f};  "
              f"Spearman(rho, d3_CA) = {r_xg:+.9f};  "
              f"Spearman(mean|delta|, d3_CA) = {r_mg:+.9f}")
        print(f"      PARTIAL Spearman(rho, d3_CA | mean|delta|) = {p1:+.9f}")
        print(f"        background bootstrap 95% CI = [{lo1:+.6f}, {hi1:+.6f}] "
              f"({v1} draws)  "
              f"({'EXCLUDES ZERO' if (lo1 > 0 or hi1 < 0) else 'INCLUDES ZERO'})")
        print(f"      PARTIAL Spearman(rho, mean|delta| | d3_CA) = {p2:+.9f}")
        print(f"        background bootstrap 95% CI = [{lo2:+.6f}, {hi2:+.6f}] "
              f"({v2} draws)  "
              f"({'EXCLUDES ZERO' if (lo2 > 0 or hi2 < 0) else 'INCLUDES ZERO'})")

    # =====================================================================
    banner("D11.5 -- HEAD-TO-HEAD, identical denominators", "-")
    print(f"  ONE table, ONE denominator per view.  The resolved N-only "
          f"subset has n = {len(resN)} in BOTH views, so the three variants "
          f"are directly comparable and no denominator differs between them.")
    print(f"  DESCRIPTIVE.  No variant is declared \"the\" answer.")
    print(f"\n  {'view':>5s} {'adjustment':>26s} {'k':>3s} {'n':>4s} "
          f"{'p_spec_adj':>11s}  vs frozen")
    for d in d11_4:
        print(f"  {d['view']:>5s} {d['axis']:>26s} {d['k']:>3d} {d['n']:>4d} "
              f"{d['p']:>11.6f}  {d['rel']} {d['thr']}")
    print(f"\n  denominators: n = {len(resN)} in every row above.  The "
          f"unadjusted frozen p_spec used n = 78 and is NOT in this table "
          f"because its denominator differs; comparing the two would be "
          f"comparing different null sets.")

    banner("D11 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print(f"\n  D11-G1: {'PASS' if not n_fail else 'FAIL'} "
          f"({len(gates) - n_fail}/{len(gates)} checks).")

    print("\nLIMITATIONS (printed, not only in the docstring):  d3_CA is a "
          "CA-CA distance in ONE 2.50 A crystal structure of the DIMER; "
          "side chains and alternate conformations are not modelled and a "
          "CA-CA minimum is not a contact.  d3_dimer is a property of the "
          "dimer, not the isolated chain, and is a sensitivity only.  "
          "Unresolved positions are never imputed: they are named, counted, "
          "and the resolved n is printed at every use.  Partial correlations "
          "have NO permutation p by design (a naive shuffle of one variable "
          "is not a valid null for a three-correlation statistic) and only a "
          "background-level bootstrap CI, which does NOT model the fact that "
          "the 96 rho_b share one y-vector and are mutually correlated.  "
          "PARTIAL CONSTRUCTIONAL OVERLAP: mean|delta| and rho_b are both "
          "functions of the same delta_b.  Nothing here is a decision rule "
          "and nothing frozen is redefined.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()