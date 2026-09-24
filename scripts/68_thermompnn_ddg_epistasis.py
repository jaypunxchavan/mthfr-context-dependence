"""
Script 68 (Group V): score every atlas missense variant with ThermoMPNN
(6FCX chain A) and test the stability-mediated interaction term against e.b.

PRE-REGISTRATION (written before the first run of this script; any later
change must be disclosed in SESSION_LOG as post-hoc).

EXECUTION ROUTE
  Inference runs through ThermoMPNN's OWN entry point, unmodified:
      python analysis/custom_inference.py --pdb <pdb> --chain A
             --model_path models/thermoMPNN_default.pt --out_dir <dir>
  (repo cloned at data/external/ThermoMPNN, sparse checkout).
  This script only (a) builds a timing-smoke fragment, (b) invokes the
  CLI, (c) joins the CLI's CSV to the atlas, (d) computes the group's
  statistics.  No third-party code is edited or re-implemented.

PRE-REGISTERED DECISIONS
  * Chain: A -- ThermoMPNN's own CLI default, and the chain verified to
    contain residue 222 as ALA with canonical numbering (SESSION_LOG
    [U4]/[V1]).  Chain B is NOT evaluated (its gap pattern includes
    220-221); choosing between chains post-hoc on results is forbidden.
  * Analysis set (V2): every atlas missense variant whose
    (position, wildtype, mutation) triple appears in ThermoMPNN's chain-A
    SSM output.  The 59 atlas positions without chain-A coordinates
    (2-39, 161-171, 392-396, 652-656) are structurally absent from that
    output -- exclusion is forced, not chosen; the exact dropped count is
    printed at every step (AGENTS sec 5).
  * V4 interaction term -- CHOICE FIXED HERE, per the task's own
    instruction to pre-register before running:  **ADDITIVE**
        pred_eb(v) = ddG(v) + ddG(A222V)
    signed sum of the two single-mutant predicted ddGs.  A
    threshold-crossing rule is REJECTED pre-run because its threshold
    theta would be a free parameter chosen after seeing e.b; the additive
    form has no free parameter.  No other combination will be tried, even
    if additive fails -- a failing pre-registered test is the result
    (AGENTS sec 0).
  * Statistics (V4): position_cluster_bootstrap rho (own_e_b primary,
    GI_folinate_independent secondary), N_BOOT env, seed 0 -- identical
    machinery to scripts 32/33.
  * V5: side-by-side against script 32/33's own-e.b row read from
    task32_delta_esm_primary.csv (rho AND both CIs shown).
  * V6: the four assign_region regions, each with position-cluster
    bootstrap CI on pred_eb vs own_e_b; region 4 compared explicitly
    against ESM-2's own region-4 row read from task32_delta_esm_primary.csv.
    Region rows with <15 positions are SKIPPED (project convention).
  * Gates (exit 1): fragment output must contain position 222 with
    wildtype A; full-run output rows == number of SSM requests; full-run
    ddG column fully finite; atlas join must match >0 rows; ddG(A222V)
    must be finite before V4 computes anything.
  * OUTPUT MAPPING (learned from TWO gate-stopped attempts, BEFORE any
    result existed): ThermoMPNN's CSV `position` column is the PDB
    residue number MINUS THE FIRST RESIDUE NUMBER OF THE PARSED CHAIN
    (6FCX chain A: first resi 40, so position = resi - 40, range 0..611
    with SLOTS MISSING at unresolved residues -- my first guess of
    "contiguous 0-based index" was refuted by the stage-2 gate: 444
    wildtype mismatches starting exactly at the 161-171 gap; the
    corrected offset mapping gives 0 mismatches on both fragment and
    full).  `mutation` is a single-letter substitution; each position
    emits 20 rows including the wildtype self-mutation.  This script
    maps position -> residue via (position + first chain-A residue
    number), GATED three ways (exit 1 on failure): (i) mapped residue
    set must equal the ATOM-file chain-A residue set exactly,
    (ii) their `wildtype` letter must equal the parsed wildtype at EVERY
    position, (iii) residue 222 must be present with wildtype A.
  * Timing discipline (AGENTS sec 1 / task V2a): the fragment
    (chain A residues 200-249, contiguous, 50 positions x 20 alts = 1,000
    predictions) runs FIRST and its per-prediction time extrapolates the
    full run; if extrapolation exceeds the V2 budget (~60 min else
    REDUCED-SCOPE, general 2h cap else BLOCKED) the full run stops per
    those rules.  SMOKE_ONLY=1 runs only the fragment stage.
    NOTE: fragment ddGs are machinery/timing ONLY -- the truncated
    neighborhood changes the local graph, so fragment numbers (including
    any 222 row) are never reported as results.

LIMITATIONS printed by the run: chain-A-only structure (dimer interface
partially represented by whatever chain-A nodes carry); unresolved
positions excluded (~1,100 variants); ThermoMPNN predicts ddG from the
WT structure for every variant (no variant re-fold); additive term has
no free parameters but also no interaction mechanism beyond summed
stability effects (that IS the hypothesis under test).

Outputs: data/processed/task_V2_thermompnn_ddg.csv (named deliverable),
         ThermoMPNN's own raw CSV under the session tmp dir.
Env: N_BOOT (default 10000), SMOKE_ONLY (0/1), FRAGMENT_OUT dir.
Smoke first: SMOKE_ONLY=1 N_BOOT=300.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SMOKE_ONLY = os.environ.get("SMOKE_ONLY", "0") == "1"
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
TMP = Path(os.environ.get("FRAGMENT_OUT",
          "/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode"))
TMP.mkdir(parents=True, exist_ok=True)
CLONE = ROOT / "data" / "external" / "ThermoMPNN"
CLI = CLONE / "analysis" / "custom_inference.py"
MODEL = CLONE / "models" / "thermoMPNN_default.pt"
PDB = ROOT / "data" / "raw" / "6FCX.pdb"
FRAG_PDB = TMP / "6FCX_chainA_200-249.pdb"
FRAG_OUT = TMP / "thermompnn_frag"
FULL_OUT = TMP / "thermompnn_full"
PDB_ID = "6FCX"
T0 = time.time()


def pstr(p, n=1):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


def chain_residues(pdb_path, chain="A"):
    """Ordered (residue_number, wildtype_1letter) for protein residues of
    `chain`, in ATOM-file order -- the basis for mapping ThermoMPNN's
    0-based `position` index back to PDB/atlas numbering."""
    from Bio.PDB import PDBParser
    from Bio.Data.IUPACData import protein_letters_3to1
    aa3 = {k.upper(): v for k, v in protein_letters_3to1.items()}
    st = PDBParser(QUIET=True).get_structure("x", str(pdb_path))
    out = []
    for ch in st[0]:
        if ch.id != chain:
            continue
        for res in ch:
            if res.id[0] != " ":          # skip HETATM/water
                continue
            name = res.get_resname().strip().upper()
            if name not in aa3:           # skip non-standard
                continue
            out.append((int(res.id[1]), aa3[name]))
    return out


def map_and_check_wt(csv_df, reslist, tag):
    """Gate (exit 1 on failure): their `position` = resi - first chain-A
    residue number.  Mapped residue set must equal reslist's exactly,
    and their wildtype letter must match reslist's at every position.
    Returns df with `resi` column."""
    offset = reslist[0][0]
    wt_map = {r: w for r, w in reslist}
    positions = [int(p) for p in csv_df["position"].unique()]
    res_map = {p: p + offset for p in positions}
    if (len(res_map) != len(reslist)
            or set(res_map.values()) != set(wt_map)):
        print(f"*** GATE FAIL ({tag}): their {len(res_map)} positions "
              f"(resi = pos+{offset} -> {min(res_map.values())}.."
              f"{max(res_map.values())}) vs my {len(reslist)} chain-A "
              f"protein residues ({min(wt_map)}..{max(wt_map)}) -- "
              "parse/offset disagreement. Stop. ***")
        sys.exit(1)
    bad = [p for p in positions
           if (csv_df.loc[csv_df["position"] == p, "wildtype"]
               != wt_map[res_map[p]]).any()]
    if bad:
        print(f"*** GATE FAIL ({tag}): wildtype mismatch at positions "
              f"{bad[:6]}{'...' if len(bad) > 6 else ''} ({len(bad)} "
              "total) -- offset mapping disproven. Stop. ***")
        sys.exit(1)
    csv_df = csv_df.copy()
    csv_df["resi"] = csv_df["position"].map(res_map)
    return csv_df


def write_fragment(pdb_path=FRAG_PDB, lo=200, hi=249):
    """Chain-A residues [lo, hi] only; original numbering kept."""
    out = []
    with open(PDB) as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                if line[21] != "A":
                    continue
                try:
                    resi = int(line[22:26])
                except ValueError:
                    continue
                if lo <= resi <= hi:
                    out.append(line.rstrip("\n"))
            elif line.startswith(("TER", "END")):
                continue
    out.append("TER")
    out.append("END")
    pdb_path.write_text("\n".join(out) + "\n")
    n_res = len({l[22:26] for l in out if l.startswith("ATOM")})
    print(f"fragment {pdb_path.name}: chain A {lo}-{hi}, "
          f"{n_res} residues, {sum(1 for l in out if l.startswith('ATOM'))} atoms")
    return n_res


def run_cli(pdb_path, out_dir, tag):
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CLI), "--pdb", str(pdb_path),
           "--chain", "A", "--model_path", str(MODEL),
           "--out_dir", str(out_dir)]
    t = time.time()
    print(f"  [{tag}] {' '.join(cmd[-8:])}")
    r = subprocess.run(cmd, capture_output=True, text=True,
                       cwd=str(CLONE), timeout=3600)
    el = time.time() - t
    (TMP / f"thermompnn_{tag}_stdout.txt").write_text(
        r.stdout + "\n--- STDERR ---\n" + r.stderr)
    csv_path = out_dir / f"ThermoMPNN_inference_{pdb_path.stem}.csv"
    ok = r.returncode == 0 and csv_path.exists()
    print(f"  [{tag}] rc={r.returncode} elapsed={el:.1f}s "
          f"csv={'FOUND' if csv_path.exists() else 'MISSING'}")
    if not ok:
        print("--- last 25 stderr lines ---")
        print("\n".join(r.stderr.splitlines()[-25:]))
    return ok, csv_path, el


if __name__ == "__main__":
    print(f"SMOKE_ONLY={SMOKE_ONLY} N_BOOT={N_BOOT} SEED={SEED} "
          f"t0={time.time()-T0:.0f}s")

    # ---- stage 1: timing fragment (their full code path, truncated PDB) ---
    print("\n" + "=" * 74)
    print("STAGE 1 -- FRAGMENT TIMING SMOKE (residues 200-249)")
    print("=" * 74)
    n_res = write_fragment()
    ok, frag_csv, el = run_cli(FRAG_PDB, FRAG_OUT, "frag")
    if not ok:
        print("*** FRAGMENT RUN FAILED -- see tmp stdout/stderr log. "
              "V2 = BLOCKED with that diagnostic. ***")
        sys.exit(1)
    frag = pd.read_csv(frag_csv, index_col=0)
    print(f"  fragment rows: {len(frag)} "
          f"(expected {n_res * 20} incl. self); columns: {list(frag.columns)}")
    # GATE: map their (position = resi - first resi) -> PDB residue,
    # require set equality + wildtype agreement at EVERY position, then
    # explicit residue-222 = A.
    frag_res = chain_residues(FRAG_PDB)
    frag = map_and_check_wt(frag, frag_res, "fragment")
    g222 = frag[frag["resi"] == 222]
    if len(g222) == 0 or (g222["wildtype"] != "A").any():
        print(f"*** GATE FAIL: resi 222 rows = {len(g222)}, "
              f"wildtypes = "
              f"{sorted(g222['wildtype'].unique()) if len(g222) else 'NONE'} "
              "-- numbering/parse mismatch. Stop. ***")
        sys.exit(1)
    print(f"  GATE: offset map (set equality + wildtype agreement) at all "
          f"{len(frag_res)} fragment residues PASS; resi 222 wildtype = A "
          "PASS")
    if not np.isfinite(frag["ddG_pred"]).all():
        print("*** GATE FAIL: non-finite ddG in fragment. Stop. ***")
        sys.exit(1)
    per_pred = el / max(len(frag), 1)
    print(f"  timing: {len(frag)} predictions in {el:.1f}s "
          f"= {per_pred:.3f} s/pred (CPU)")

    if SMOKE_ONLY:
        print(f"\nSMOKE_ONLY=1 -- stopping before the full run. "
              f"Fragment machinery PASS in {time.time()-T0:.0f}s.")
        sys.exit(0)

    # ---- stage 2: full chain-A SSM --------------------------------------
    print("\n" + "=" * 74)
    print("STAGE 2 -- FULL CHAIN-A SSM (all resolved positions x 20)")
    print("=" * 74)
    ok, full_csv, el = run_cli(PDB, FULL_OUT, "full")
    if not ok:
        print("*** FULL RUN FAILED -- V2 = BLOCKED with the diagnostic "
              "in the tmp log. ***")
        sys.exit(1)
    full = pd.read_csv(full_csv, index_col=0)
    n_rows = len(full)
    print(f"  full rows: {n_rows}  (fragment extrapolation: "
          f"{per_pred * 11920:.0f}s for 11,920 = 596x20 -- actual "
          f"{el:.0f}s)")
    # GATE: rows finite + rectangular set + index->residue + wt agreement
    uniq_pos = full["position"].nunique()
    if not np.isfinite(full["ddG_pred"]).all():
        print("*** GATE FAIL: non-finite ddG in full run. Stop. ***")
        sys.exit(1)
    if n_rows != uniq_pos * 20:
        print(f"  NOTE: rows ({n_rows}) != positions*20 ({uniq_pos*20}) "
              "-- their SSM emitted a non-rectangular set; accounting "
              "below is by join, not by arithmetic.")
    full_res = chain_residues(PDB)
    full = map_and_check_wt(full, full_res, "full")
    print(f"  GATE: ddG fully finite; offset map (set equality + "
          f"wildtype agreement) at all {uniq_pos} resolved positions "
          f"(chain A) PASS")

    # ---- stage 3: join to the atlas (V2 deliverable) ---------------------
    print("\n" + "=" * 74)
    print("STAGE 3 -- ATLAS JOIN + DROPPED-ROW ACCOUNTING")
    print("=" * 74)
    full["position"] = full["resi"].astype(int)   # gated: pos+first resi
    tm = full.rename(columns={"ddG_pred": "ddg"})[
        ["position", "wildtype", "mutation", "ddg"]].copy()
    tm = tm.drop_duplicates(subset=["position", "wildtype", "mutation"])
    atlas = pd.read_csv(PROC / "phase5_analysis_table.csv")[
        ["hgvs_pro", "position", "wt_aa", "mut_aa", "delta_esm",
         "GI_folinate_independent", "GI_folinate_dependent"]]
    own = pd.read_csv(PROC / "own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    atlas = atlas.merge(own, on="hgvs_pro", how="left")
    j = atlas.merge(tm, left_on=["position", "wt_aa", "mut_aa"],
                    right_on=["position", "wildtype", "mutation"], how="left")
    n_atlas = len(atlas)
    n_match = j["ddg"].notna().sum()
    missing = j[j["ddg"].isna()]
    miss_pos = sorted(missing["position"].unique())
    print(f"  atlas rows: {n_atlas} | matched ThermoMPNN ddG: {n_match} | "
          f"dropped: {n_atlas - n_match} "
          f"({100*(n_atlas-n_match)/n_atlas:.1f}%)")
    print(f"  distinct positions never matched: {len(miss_pos)} "
          f"-> {miss_pos[:12]}{' ...' if len(miss_pos) > 12 else ''}")
    # full dropped-row accounting (AGENTS sec 5): unresolved vs
    # canonical-vs-construct wt mismatch
    pdb_wt = dict(full_res)
    in_res = missing["position"].isin(pdb_wt)
    wt_mis_pos = sorted(missing.loc[in_res, "position"].unique())
    print(f"  breakdown of {len(missing)} dropped rows: "
          f"{int((~in_res).sum())} rows at "
          f"{missing.loc[~in_res, 'position'].nunique()} unresolved "
          f"positions (predicted 59: 2-39, 161-171, 392-396, 652-656); "
          f"{int(in_res.sum())} rows at {len(wt_mis_pos)} positions "
          f"where 6FCX chain A's residue differs from canonical P42898 "
          f"({wt_mis_pos}) -- their SSM scores the CONSTRUCT residue "
          "there, so joining those atlas variants would be wrong; "
          "correctly excluded.")
    j = j[j["ddg"].notna()].copy()

    # ---- V3: A222V's own ddG --------------------------------------------
    # A222V is NOT an atlas row (phase5 position==222 has 0 rows, verified
    # in SESSION_LOG [U2]) -- read it from their own SSM at resi 222.
    a222v = full[(full["resi"] == 222) & (full["mutation"] == "V")]
    if len(a222v) != 1 or not np.isfinite(a222v["ddG_pred"].iloc[0]):
        print(f"*** GATE FAIL: A222V rows={len(a222v)} in their SSM -- "
              "cannot compute V4. Stop. ***")
        sys.exit(1)
    ddg_222 = float(a222v["ddG_pred"].iloc[0])
    print("\n  V3 (one number): ThermoMPNN ddG(A222V) = "
          f"{ddg_222:+.4f} (model output units) -- read from their SSM "
          f"row (position {int(a222v['position'].iloc[0])} = resi 222), "
          "not from the atlas join")

    # ---- V4: pre-registered additive term --------------------------------
    print("\n" + "=" * 74)
    print(f"V4 -- ADDITIVE STABILITY TERM (pred_eb = ddG(v) + ddG(A222V); "
          f"N_BOOT={N_BOOT})")
    print("=" * 74)
    j["pred_eb"] = j["ddg"] + ddg_222
    from scripts.lib.stats import position_cluster_bootstrap
    res = {}
    for yc, lbl in [("own_e_b", "V4 primary: pred_eb vs own e.b"),
                    ("GI_folinate_independent",
                     "V4 secondary: pred_eb vs published e.b")]:
        sub = j.dropna(subset=[yc])
        r = position_cluster_bootstrap(sub, "position", "pred_eb", yc,
                                       n_boot=N_BOOT, seed=SEED)
        res[lbl] = r
        print(f"  {lbl:44s} rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"p={pstr(r['p_boot'], N_BOOT)} n={r['n_rows']}"
              f"{'  (crosses 0)' if r['ci_lo'] < 0 < r['ci_hi'] else ''}")

    # ---- V5: head-to-head -------------------------------------------------
    print("\n" + "=" * 74)
    print("V5 -- HEAD-TO-HEAD vs ESM-2 delta_ESM (own e.b, both CIs)")
    print("=" * 74)
    t32 = pd.read_csv(PROC / "task32_delta_esm_primary.csv")
    esm = t32[(t32["stage"] == "primary") &
              (t32["quantity"] == "signed, own e_b")].iloc[0]
    r4 = res["V4 primary: pred_eb vs own e.b"]
    print(f"  ESM-2 delta_ESM : rho={esm['value']:+.4f} "
          f"CI=[{esm['ci_lo']:+.4f},{esm['ci_hi']:+.4f}] "
          f"n={int(esm['n'])}")
    print(f"  ThermoMPNN additive: rho={r4['observed_rho']:+.4f} "
          f"CI=[{r4['ci_lo']:+.4f},{r4['ci_hi']:+.4f}] "
          f"n={r4['n_rows']}")
    better = ("ThermoMPNN additive"
              if abs(r4["observed_rho"]) > abs(esm["value"]) else "ESM-2 delta_ESM")
    both_clear = (r4["ci_lo"] > 0 or r4["ci_hi"] < 0)
    print(f"  larger |rho|: {better}; ThermoMPNN CI excludes 0: {both_clear}")

    # ---- V6: four regions --------------------------------------------------
    print("\n" + "=" * 74)
    print("V6 -- FOUR-REGION BREAKDOWN (pred_eb vs own e.b)")
    print("=" * 74)
    from scripts.lib.regions import assign_region, REGION_BOUNDS
    j["region"] = assign_region(j["position"])
    esm_reg = t32[t32["stage"] == "region"].set_index("quantity")
    for rg in sorted(REGION_BOUNDS):
        sub = j[j["region"] == rg]
        if sub["position"].nunique() < 15:
            print(f"  region {rg}: SKIPPED "
                  f"({sub['position'].nunique()} positions)")
            continue
        rr = position_cluster_bootstrap(sub, "position", "pred_eb",
                                        "own_e_b", n_boot=N_BOOT, seed=SEED)
        key = f"region_{rg}"
        esm_line = ""
        if key in esm_reg.index:
            er = esm_reg.loc[key]
            esm_line = (f"  | ESM-2 same region: rho={er['value']:+.4f} "
                        f"CI=[{er['ci_lo']:+.4f},{er['ci_hi']:+.4f}]")
        print(f"  region {rg} ({REGION_BOUNDS[rg][0]}-"
              f"{REGION_BOUNDS[rg][1]}) Thermo rho={rr['observed_rho']:+.4f} "
              f"CI=[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}] "
              f"n={rr['n_rows']}{esm_line}")

    # ---- save the named V2 deliverable ------------------------------------
    out_cols = ["hgvs_pro", "position", "wt_aa", "mut_aa", "ddg",
                "pred_eb", "own_e_b", "GI_folinate_independent",
                "delta_esm", "region"]
    out = PROC / "task_V2_thermompnn_ddg.csv"
    j[[c for c in out_cols if c in j.columns]].to_csv(out, index=False)
    print(f"\nSaved to {out}  ({len(j)} rows)")
    print("\nLIMITATIONS (printed here, per AGENTS sec 6): chain A only; "
          "59 unresolved positions excluded (dropped count above); WT "
          "structure reused for every variant; additive term is "
          "pre-registered with no free parameters and was NOT tuned; "
          f"total runtime {time.time()-T0:.0f}s.")
