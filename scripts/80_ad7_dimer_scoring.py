"""
AD7 — Does the region-4 result survive dimer scoring? (task doc L300-305).
PRE-REGISTERED: this docstring was written before the first run.

AMBIGUITY LOG (task says "the region-4 discriminator result (Part II
§12.4)" -- Part II is an EXTERNAL evaluator document and is NOT in this
repo (grep for "12.4" finds nothing relevant). Most-literal resolution,
fixed here before running: anchor §12.4 to the two IN-REPO region-4
records and check BOTH under dimer scoring:
  (E) the ESM-2/e.b region-4 FAILURE:
      data/processed/task_region_check.csv + RESULTS.md L88 +
      MTHFR_RESULTS_LOG L95/L326 ("region 4 does not overlap the pooled
      estimate"; claim table "3.2 ... Fails (region 4)"). Quoted
      verbatim by the run (S5), NOT recomputed -- and stated plainly:
      ThermoMPNN dimer scoring CANNOT alter an ESM result; what it can
      alter is ThermoMPNN's half of the §12.4 discrimination (whether
      the structural side's region-4 behaviour was a monomer artifact).
  (T) ThermoMPNN's side of §12 (§12 IS the ThermoMPNN section): the
      per-region rho(ddg, own_e_b) pattern from V2, recomputed for
      BOTH scorings (monomer = published frame after G1; dimer = this
      rerun).
If Part II §12.4 later surfaces and names a different quantity, this
entry's anchor choice must be revisited -- flagged here, not hidden.

ACTION (AD7a, literal): rerun ThermoMPNN's structural scoring against
the biological dimer assembly (6FCX chains A+B) rather than chain A
alone, at least for region-4 positions (all positions are scored --
cheaper than subsetting, and the task says "at least").
  Machinery = scripts/68's exact path, reused not rewritten:
  helpers chain_residues / map_and_check_wt / write_fragment are
  IMPORTED from script 68 (importlib, module guards __main__); the CLI
  subprocess call is mirrored with only the --chain argument exposed
  (script 68's run_cli hardcodes "A"). Vendored repo data/external/
  ThermoMPNN is READ-ONLY: ZERO third-party edits (unlike AD4's
  disclosed patches) -- same model models/thermoMPNN_default.pt, same
  input data/raw/6FCX.pdb, same custom_inference.py code path.
  Multi-chain support is the vendor's OWN: alt_parse_PDB iterates the
  --chain string letter by letter ("AB" -> parse A, then B, concat_seq
  accumulates both, coords_chain_A and coords_chain_B both populated);
  TransferModel.forward featurizes the WHOLE complex ONCE (chain-B
  atoms enter the MPNN spatial neighbour graph) then loops the cheap
  per-mutation head -- so peak memory is independent of mutation count
  (no chunking needed) and dimer context reaches chain-A predictions.
  Expected geometry: chain A resi 40-651 (612 parsed), chain B resi
  41-648; their `position` = 0-based index into the concat sequence ->
  A rows 0..611 (resi = pos+40, same map as script 68), B rows start
  at 612 (resi = pos-571). Rows = (n_A + n_B) * 20 (20 = ALPHABET[:-1]
  of 'ACDEFGHIKLMNPQRSTVWYX', incl. the self row).

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G1 MONOMER REPRODUCTION (the load-bearing gate): rerun --chain A on
     the full 6FCX must reproduce V2's ddg at every one of the 10,141
     V2 rows (join on position/wt_aa/mut_aa) with max|delta| < 1e-6,
     else STOP -- without this the dimer change measures nothing. The
     rerun CSV also passes script 68's own map_and_check_wt (set
     equality + wildtype agreement at all 612 positions).
  G2 DIMER PARSE: the --chain AB CSV must contain BOTH parts: A rows
     (position < 612, map via chain_residues(A), offset +40) and B
     rows (position >= 612, shifted then map via chain_residues(B)),
     each with exact residue-set equality and wildtype agreement at
     EVERY position -- this proves chain B was actually parsed and not
     silently skipped; B count printed; row count == (n_A+n_B)*20
     printed (rectangularity NOTE, not a gate, mirroring script 68);
     all ddG finite.
  G3 DIMER JOIN: all 10,141 V2 rows receive a finite ddg_dimer (same
     join keys as script 68 stage 3), row count == V2's 10,141, and
     the dimer join's wildtype letters equal V2 wt_aa at every row,
     else STOP.
  G2b SANITY (added after the smoke showed exactly-0 deltas at the
     off-interface fragment window, BEFORE any full run): dimer minus
     monomer must be nonzero at SOME variants/positions — the 39
     struct-table interface residues have inter-chain heavy-atom
     contacts of 2.4-5.9 A (measured pre-run), so all-exact-zero would
     mean chain B never reaches chain-A predictions = pipeline defect,
     STOP. (The fragment window 200-249 has no interface residues and
     an external kNN probe showed 0/50 of its A nodes have any B
     neighbour within their 30 nearest — exactly-0 there is expected
     physics, documented in the [AD7] log entry.)
  G4 BURIAL TABLE: struct table Position covers every V2 position
     (join space check); NaN burial counts printed. NaN burial is
     EXCLUDED from burial tests only (S4), NEVER from region stats.

PRE-REGISTERED STATISTICS (house position_cluster_bootstrap, seed 0;
position-level bootstraps seed 2; paired delta-rho seed 1; N_BOOT env,
default 10,000):
  S1 per-region rho(scoring, own_e_b) -- pooled + regions 1-4, BOTH
     scorings, CIs + p_boot (analysis frame = V2 dropna(own_e_b) =
     9,595 rows / 586 positions, same as AD3-AD6).
  S2 change itself: per-variant Delta = ddg_dimer - ddg_monomer; rho
     (monomer, dimer) pooled; per-position mean|Delta| by region with
     position-bootstrap CI (seed 2); per-position mean Delta table.
  S3 THE §12.4 CHECK (frozen verdict): region 4 HOLDS iff
       (a) sign of rho(scoring, own_e_b) in region 4 unchanged between
           scorings, OR both scorings' region-4 CIs include 0
           (a sign flip between two nulls is not a change -- clause
           fixed here before any number is seen), AND
       (b) region-4 CI zero-inclusion status unchanged, AND
       (c) paired position bootstrap (seed 1) CI of Delta-rho_4 =
           rho_dimer,4 - rho_mono,4 includes 0.
     Else CHANGED -> report plainly. Pooled Delta-rho printed alongside
     (NOT part of the verdict). Effect sizes always beside significance.
  S4 mechanism (does change concentrate at the interface?):
     continuous Spearman(position-mean |Delta|, 'Dimer relative
     burial') pooled + region 4 (position bootstrap seed 0); interface
     (rel. burial > 0) vs non-interface difference in mean position
     mean|Delta| (position bootstrap seed 2). Sparse-tie caveat
     (measured pre-run: 39/597 nonzero, 558 zeros, 54 NaN) printed
     with the result.
  S5 ESM region-4 anchor quoted verbatim from task_region_check.csv
     (both error metrics, pooled + region_4 rows) + the plain statement
     that this rerun cannot touch ESM's number.

SMOKE (SMOKE=1): fragment stages only -- chain-A fragment 200-249
(script 68's writer) + a NEW chain-A(200-249)+chain-B(200-249)
fragment for the --chain AB plumbing (parse gates + Delta at fragment
scale) + S1 monomer-only + S4 struct-join check + S5 quote, then exit
0. The full dimer CSV join and S2/S3/S4-on-full are exercised only in
the FULL run -- disclosed as smoke scope. Full run skips fragments (G1
covers monomer mapping).
TIMING (measure first, AGENTS sec 1): the fragment prints s/pred; a
projection for full A + full AB is printed after G1; if projected total
remaining runtime would push the task past 7,200 s the script STOPS
(exit 1) for a timing decision rather than guessing. Script 68's full
A run completed under its 3,600 s subprocess timeout in a prior
session; dimer subprocess timeout 7,200 s.

DISCLOSED: Part II §12.4 not in repo (anchor strategy above); burial
columns come from the atlas reference table
data/raw/mthfrModel/reference_data/MTHFR_structural_features.csv (read-
only, provenance = atlas authors, assembly used to compute them not
stated in-file -- treated as given, printed); Δ magnitudes are in
ThermoMPNN model units; their multi-chain parse/featurize is used
UNMODIFIED (any chain-separation quirk inside tied_featurize is theirs
and is reported via the parse diagnostics + result pattern, not patched);
S1 monomer numbers are a recomputation of the published frame (G1 makes
them = V2's, so this is reproduction not replication); smoke scope as
above.

OUTPUTS: data/processed/task80_dimer_variants.csv (10,141 rows),
task80_dimer_positions.csv (position-level table incl. burial),
task80_region_rhos.csv (S1 rows, both scorings). CLI CSVs stay in TMP
(mirroring script 68; ephemeral, regenerable). Existing scripts/libs/
results untouched. Next free script number after this: 81.
"""
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from scripts.lib.stats import position_cluster_bootstrap

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
CLONE = ROOT / "data" / "external" / "ThermoMPNN"
CLI = CLONE / "analysis" / "custom_inference.py"
MODEL = CLONE / "models" / "thermoMPNN_default.pt"
PDB = ROOT / "data" / "raw" / "6FCX.pdb"
STRUCT = ROOT / "data" / "raw" / "mthfrModel" / "reference_data" / \
    "MTHFR_structural_features.csv"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
REGCHK = PROC / "task_region_check.csv"
OUT_VAR = PROC / "task80_dimer_variants.csv"
OUT_POS = PROC / "task80_dimer_positions.csv"
OUT_RHO = PROC / "task80_region_rhos.csv"
TMP = Path(os.environ.get("AD7_TMP",
          "/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode"))
TMP.mkdir(parents=True, exist_ok=True)

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
SEED, SEED1, SEED2 = 0, 1, 2
TOL = 1e-6
T0 = time.time()

# reuse script 68's helpers verbatim (module guards __main__)
_s68_spec = importlib.util.spec_from_file_location(
    "s68", ROOT / "scripts" / "68_thermompnn_ddg_epistasis.py")
_s68 = importlib.util.module_from_spec(_s68_spec)
_s68_spec.loader.exec_module(_s68)
chain_residues = _s68.chain_residues
map_and_check_wt = _s68.map_and_check_wt
write_fragment = _s68.write_fragment


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def run_cli2(pdb_path, out_dir, chain, tag, timeout=3600):
    """script 68's run_cli with --chain exposed (its version hardcodes
    'A'); same cwd, same capture, log to TMP."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CLI), "--pdb", str(pdb_path),
           "--chain", chain, "--model_path", str(MODEL),
           "--out_dir", str(out_dir)]
    t = time.time()
    print(f"  [{tag}] chain={chain} {' '.join(cmd[-8:])}")
    r = subprocess.run(cmd, capture_output=True, text=True,
                       cwd=str(CLONE), timeout=timeout)
    el = time.time() - t
    (TMP / f"ad7_{tag}_stdout.txt").write_text(
        r.stdout + "\n--- STDERR ---\n" + r.stderr)
    csv_path = out_dir / f"ThermoMPNN_inference_{pdb_path.stem}.csv"
    ok = r.returncode == 0 and csv_path.exists()
    print(f"  [{tag}] rc={r.returncode} elapsed={el:.1f}s "
          f"csv={'FOUND' if csv_path.exists() else 'MISSING'}")
    if not ok:
        print("--- last 25 stderr lines ---")
        print("\n".join(r.stderr.splitlines()[-25:]))
    return ok, csv_path, el


def write_fragment_ab(out_path, lo=200, hi=249):
    """Chain-A residues [lo,hi] PLUS chain-B residues [lo,hi] -- the
    --chain AB plumbing smoke (A part numbered first in their concat
    parse; full-B coverage is gated in the full run, not here, so the
    smoke stays ~2x the cheap fragment-A cost)."""
    out = []
    with open(PDB) as f:
        for line in f:
            if line.startswith(("ATOM", "HETATM")):
                c = line[21]
                try:
                    resi = int(line[22:26])
                except ValueError:
                    continue
                if c in "AB" and lo <= resi <= hi:
                    out.append(line.rstrip("\n"))
            elif line.startswith(("TER", "END")):
                continue
    out.append("TER")
    out.append("END")
    out_path.write_text("\n".join(out) + "\n")
    n_a = len({l[22:26] for l in out
               if l.startswith("ATOM") and l[21] == "A"})
    n_b = len({l[22:26] for l in out
               if l.startswith("ATOM") and l[21] == "B"})
    print(f"  fragment {out_path.name}: chain A {lo}-{hi} = {n_a} res, "
          f"chain B {lo}-{hi} = {n_b} res")
    return n_a, n_b


def map_part(df, reslist, tag, shift):
    """map_and_check_wt on a position-part shifted so its min is 0.
    Returned resi is the true PDB residue number (their positions are
    sequential-from-first-residue, same assumption script 68 gates)."""
    d = df.copy()
    d["position"] = d["position"].astype(int) - shift
    d = map_and_check_wt(d, reslist, tag)
    return d


def boot_mean_ci(vals, n_boot, seed, n_rep=None):
    """Row (== position) bootstrap CI of the mean; position-level table
    only. n_rep > 1 draws n_rep rows per draw (unused, kept simple)."""
    rng = np.random.default_rng(seed)
    v = np.asarray(vals, dtype=float)
    n = len(v)
    draws = np.empty(n_boot)
    for b in range(n_boot):
        draws[b] = v[rng.integers(0, n, n)].mean()
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return float(v.mean()), float(lo), float(hi)


def paired_delta_rho(df, col_mono, col_dimer, ycol, n_boot, seed):
    """Paired position-CLUSTER bootstrap of rho(mono) - rho(dimer) on
    variant rows: same cluster draw evaluated for both rhos."""
    rng = np.random.default_rng(seed)
    df = df.reset_index(drop=True)   # cluster labels -> array positions
    clusters = [g.index.to_numpy() for _, g in df.groupby("position")]
    nc = len(clusters)
    x1 = df[col_mono].to_numpy()
    x2 = df[col_dimer].to_numpy()
    y = df[ycol].to_numpy()

    def dr(idx):
        return (spearmanr(x1[idx], y[idx]).statistic
                - spearmanr(x2[idx], y[idx]).statistic)

    all_idx = np.arange(len(df))
    obs = dr(all_idx)
    draws = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, nc, nc)
        idx = np.concatenate([clusters[p] for p in pick])
        draws[b] = dr(idx)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = min(2 * min((draws <= 0).mean(), (draws >= 0).mean()), 1.0)
    return float(obs), float(lo), float(hi), float(p)


if __name__ == "__main__":
    banner(f"AD7 — DIMER SCORING vs MONOMER (scripts/80) "
           f"SMOKE={SMOKE} N_BOOT={N_BOOT}")

    v2 = pd.read_csv(V2_PATH)
    a_res = chain_residues(PDB, "A")
    b_res = chain_residues(PDB, "B")
    print(f"  parse targets: chain A {len(a_res)} res "
          f"({a_res[0][0]}-{a_res[-1][0]}) | chain B {len(b_res)} res "
          f"({b_res[0][0]}-{b_res[-1][0]})")
    print(f"  V2 rows {len(v2)}, positions {v2['position'].nunique()}, "
          f"own_e_b finite {v2['own_e_b'].notna().sum()}")

    # ---- stage 1: fragment smoke (both chain paths) --------------------
    banner("STAGE 1 — FRAGMENT SMOKE (A 200-249, then AB plumbing)", "-")
    frag_a = TMP / "6FCX_chainA_200-249.pdb"
    n_fa = write_fragment(frag_a)
    ok, fa_csv, el = run_cli2(frag_a, TMP / "ad7_frag_A", "A", "frag_A")
    if not ok:
        gfail("FRAGMENT A RUN FAILED — see TMP log. AD7 = BLOCKED there.")
    fa = pd.read_csv(fa_csv, index_col=0)
    if not np.isfinite(fa["ddG_pred"]).all():
        gfail("fragment A: non-finite ddG. Stop.")
    fa = map_and_check_wt(fa, chain_residues(frag_a, "A"), "frag-A")
    per_pred = el / max(len(fa), 1)
    print(f"  frag A rows {len(fa)} in {el:.1f}s = {per_pred:.3f} s/pred")

    frag_ab = TMP / "6FCX_chainAB_frag.pdb"
    n_fa2, n_fb = write_fragment_ab(frag_ab)
    ok, fab_csv, el2 = run_cli2(frag_ab, TMP / "ad7_frag_AB", "AB",
                                "frag_AB")
    if not ok:
        gfail("FRAGMENT AB RUN FAILED — see TMP log. AD7 = BLOCKED there.")
    fab = pd.read_csv(fab_csv, index_col=0)
    fab["position"] = fab["position"].astype(int)
    if not np.isfinite(fab["ddG_pred"]).all():
        gfail("fragment AB: non-finite ddG. Stop.")
    a_cut = int(fa["position"].max()) + 1   # A slot count (their
    # position indexing is resi-offset-style with gap slots; rows skip
    # '-', so slot count = max position + 1, not the observed-row count)
    dfa = fab[fab["position"] < a_cut]
    dfb = fab[fab["position"] >= a_cut]
    dfa = map_part(dfa, chain_residues(frag_a, "A"), "frag-AB/A", 0)
    dfb = map_part(dfb, chain_residues(frag_ab, "B"), "frag-AB/B",
                   a_cut)
    print(f"  G2-frag parse PASS: A part {len(dfa)} rows "
          f"({dfa['position'].nunique()} pos), B part {len(dfb)} rows "
          f"({dfb['position'].nunique()} pos), "
          f"expected rows {(n_fa2 + n_fb) * 20}, "
          f"CSV rows {len(fab)}, chain col "
          f"{sorted(fab['chain'].unique()) if 'chain' in fab else 'n/a'}")
    if len(fab) != (n_fa2 + n_fb) * 20:
        print(f"  NOTE: fragment AB rows {len(fab)} != "
              f"(n_A+n_B)*20 = {(n_fa2 + n_fb) * 20} — rectangularity "
              f"NOTE (accounting by join below, as in script 68).")
    # plumbing proof: dimer-vs-monomer delta at fragment A positions
    m = dfa.merge(fa[["resi", "mutation", "ddG_pred"]],
                  left_on=["resi", "mutation"],
                  right_on=["resi", "mutation"], suffixes=("_AB", "_A"))
    dfrag = m["ddG_pred_AB"] - m["ddG_pred_A"]
    print(f"  fragment Delta (AB - A) at {dfa['position'].nunique()} A "
          f"positions: mean {dfrag.mean():+.4f}, "
          f"mean|D| {dfrag.abs().mean():.4f}, "
          f"max|D| {dfrag.abs().max():.4f} — zero here means this "
          f"window's A nodes have no B neighbour in their spatial kNN; "
          f"the full run carries gate G2b (deltas must be nonzero "
          f"SOMEWHERE given the 2.4-5.9 A inter-chain contacts at the "
          f"39 interface residues)")

    # ---- struct-join + ESM anchor (also run in smoke) ------------------
    st = pd.read_csv(STRUCT)[["Position", "Dimer burial",
                              "Dimer relative burial"]]
    miss = set(v2["position"]) - set(st["Position"])
    if miss:
        gfail(f"G4 FAIL: {len(miss)} V2 positions absent from struct "
              f"table: {sorted(miss)[:8]}")
    n_nan = int(st["Dimer relative burial"].isna().sum())
    n_nz = int((st["Dimer relative burial"] > 0).sum())
    print(f"  G4 struct join PASS: all V2 positions present; burial "
          f"NaN {n_nan}, >0 {n_nz}, ==0 "
          f"{int((st['Dimer relative burial'] == 0).sum())} (full table)")

    rc = pd.read_csv(REGCHK)
    banner("S5 — ESM region-4 anchor (verbatim from "
           "task_region_check.csv; NOT recomputed)", "-")
    for _, row in rc[rc["region"].isin(["pooled", "region_4"])].iterrows():
        print(f"  {row['error_metric']:10s} {row['region']:9s} "
              f"rho={row['observed_rho']:+.4f} "
              f"CI=[{row['ci_lo']:+.4f},{row['ci_hi']:+.4f}] "
              f"p_boot={row['p_boot']:.4f} "
              f"includes0={row['ci_includes_zero']} "
              f"overlaps_pooled={row['overlaps_pooled']} "
              f"n={int(row['n_rows'])}")
    print("  Plain statement: these are ESM-2/e.b numbers; ThermoMPNN "
          "dimer scoring CANNOT alter them. The rerun tests only "
          "whether ThermoMPNN's half of the §12.4 discrimination was a "
          "monomer-scoring artifact.")

    if SMOKE:
        banner("SMOKE S1 — monomer per-region rho(ddg, own_e_b) only "
               "(S2/S3/S4 full = deferred to full run)", "-")
        sub = v2.dropna(subset=["own_e_b"]).copy()
        rows = []
        for scope, s in ([("pooled", sub)]
                         + [(f"region{int(r)}", sub[sub["region"] == r])
                            for r in sorted(sub["region"].unique())]):
            rr = position_cluster_bootstrap(s, "position", "ddg",
                                            "own_e_b",
                                            n_boot=N_BOOT, seed=SEED)
            print(f"  [mono ] {scope:8s} rho={rr['observed_rho']:+.4f} "
                  f"[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}] "
                  f"p={rr['p_boot']:.4f} n={rr['n_rows']}")
            rows.append((scope, rr))
        print(f"\nSMOKE=1 — fragment plumbing + gates PASS in "
              f"{time.time() - T0:.0f}s; FULL dimer run and S2/S3/S4 "
              f"verdict deferred to the full run (disclosed smoke "
              f"scope).")
        sys.exit(0)

    # ---- stage 2: full monomer rerun (G1) -----------------------------
    banner("STAGE 2 — FULL CHAIN-A RERUN (G1 reproduction vs V2)", "-")
    ok, full_a_csv, el_a = run_cli2(PDB, TMP / "ad7_full_A", "A",
                                    "full_A", timeout=3600)
    if not ok:
        gfail("FULL A RUN FAILED — see TMP log. AD7 = BLOCKED there.")
    fa_full = pd.read_csv(full_a_csv, index_col=0)
    fa_full = map_and_check_wt(fa_full, a_res, "full-A")
    print(f"  script-68 map gate re-passed at {len(a_res)} chain-A "
          f"positions; rows {len(fa_full)}, elapsed {el_a:.1f}s "
          f"({el_a / max(len(fa_full), 1):.4f} s/pred)")
    proj_ab = (el_a / max(len(fa_full), 1)) * (len(a_res) + len(b_res)) * 20
    remain = proj_ab + (time.time() - T0)
    print(f"  projection: full AB ~{proj_ab:.0f}s; total task so far + "
          f"AB ~{remain:.0f}s")
    if remain > 7200:
        gfail(f"G TIMING: projected total {remain:.0f}s > 7,200s cap — "
              f"stopping for a timing decision (measure-first rule).")
    # key frame only (fa_full also carries a raw 0-based `position`
    # column that would collide with V2's resi-space `position` in a
    # bare merge -- selected away here, found at write time)
    mono = fa_full.rename(columns={"ddG_pred": "ddg_mono"})[
        ["resi", "wildtype", "mutation", "ddg_mono"]]
    m = v2.merge(mono, how="left",
                 left_on=["position", "wt_aa", "mut_aa"],
                 right_on=["resi", "wildtype", "mutation"])
    if m["ddg_mono"].notna().sum() != len(v2):
        gfail(f"G1 FAIL: only {m['ddg_mono'].notna().sum()}/{len(v2)} V2 "
              f"rows matched the monomer rerun. Stop.")
    max_d = float((m["ddg"] - m["ddg_mono"]).abs().max())
    if max_d >= TOL:
        gfail(f"G1 FAIL: monomer rerun != V2 ddg, max|delta| = "
              f"{max_d:.3e} >= {TOL}. Stop.")
    print(f"  G1 PASS: monomer rerun reproduces V2 ddg at all {len(v2)} "
          f"rows, max|delta| = {max_d:.3e} (< {TOL})")
    m = m.drop(columns=["resi", "wildtype", "mutation"])

    # ---- stage 3: full dimer run (G2/G3) ------------------------------
    banner("STAGE 3 — FULL DIMER SSM (--chain AB, both chains)", "-")
    ok, full_ab_csv, el_ab = run_cli2(PDB, TMP / "ad7_full_AB", "AB",
                                      "full_AB", timeout=7200)
    if not ok:
        gfail("FULL AB RUN FAILED — see TMP log. AD7 = BLOCKED there.")
    fb_full = pd.read_csv(full_ab_csv, index_col=0)
    fb_full["position"] = fb_full["position"].astype(int)
    if not np.isfinite(fb_full["ddG_pred"]).all():
        gfail("G2: non-finite ddG in AB run. Stop.")
    # A slot count = their full-A position max + 1 (their slot indexing
    # is resi-40-style with '-' gap slots: positions run 0..611 with
    # rows only at the 596 observed -- proven by script 68's historical
    # set-equality gate; len(a_res)=596 would MISCLASSIFY the 16 tail
    # rows >= 596, found by review before the full run)
    nA_pos = int(fa_full["position"].max()) + 1
    exp_span = max(r for r, _ in a_res) - min(r for r, _ in a_res) + 1
    print(f"  A slot count from their full-A CSV = {nA_pos} "
          f"(observed rows {len(a_res)}, resi span {exp_span})")
    if nA_pos != exp_span:
        gfail(f"G2: their A slot count {nA_pos} != resi span "
              f"{exp_span} -- parse numbering unexpected. Stop.")
    dfa = fb_full[fb_full["position"] < nA_pos]
    dfb = fb_full[fb_full["position"] >= nA_pos]
    dfa = map_part(dfa, a_res, "full-AB/A", 0)
    dfb = map_part(dfb, b_res, "full-AB/B", nA_pos)
    print(f"  G2 parse PASS: A part {len(dfa)} rows / "
          f"{dfa['position'].nunique()} pos == {nA_pos} expected; "
          f"B part {len(dfb)} rows / {dfb['position'].nunique()} pos "
          f"== {len(b_res)} expected")
    print(f"  rows: CSV {len(fb_full)} vs (n_A+n_B)*20 = "
          f"{(nA_pos + len(b_res)) * 20}"
          + ("" if len(fb_full) == (nA_pos + len(b_res)) * 20
             else "  <-- NOTE: non-rectangular; accounting by join"))
    print(f"  elapsed full AB {el_ab:.1f}s (monomer {el_a:.1f}s)")
    din = dfa.rename(columns={"ddG_pred": "ddg_dimer"})[
        ["resi", "wildtype", "mutation", "ddg_dimer"]]
    m = m.merge(din, how="left",
                left_on=["position", "wt_aa", "mut_aa"],
                right_on=["resi", "wildtype", "mutation"])
    if m["ddg_dimer"].notna().sum() != len(v2):
        gfail(f"G3 FAIL: only {m['ddg_dimer'].notna().sum()}/{len(v2)} "
              f"V2 rows got a dimer score. Stop.")
    if (m["wildtype"] != m["wt_aa"]).any():
        gfail("G3 FAIL: dimer wildtype != V2 wt_aa somewhere. Stop.")
    print(f"  G3 PASS: dimer join complete at all {len(v2)} rows, "
          f"wildtypes agree with V2 at every row")

    # ---- stage 4: statistics ------------------------------------------
    m["delta"] = m["ddg_dimer"] - m["ddg_mono"]
    m["abs_delta"] = m["delta"].abs()
    # G2b sanity gate (pre-registered before the full run): the 39
    # struct-table interface residues have inter-chain heavy-atom
    # contacts of 2.4-5.9 A (measured pre-run), so SOME deltas must be
    # nonzero once B atoms enter the spatial 30-NN graph; all-exact-zero
    # would mean B never reaches chain-A predictions = pipeline defect.
    n_nz = int((m["abs_delta"] > 1e-12).sum())
    n_nz_pos = int(m.loc[m["abs_delta"] > 1e-12, "position"].nunique())
    print(f"  G2b sanity: {n_nz} variants / {n_nz_pos} positions have "
          f"nonzero dimer-minus-monomer (pre-run measured: 39 interface "
          f"residues, contacts 2.4-5.9 A)")
    if n_nz == 0:
        gfail("G2b FAIL: dimer context changed NOTHING (all deltas "
              "exactly 0) despite verified inter-chain contacts -- "
              "pipeline sanity failure. Stop.")
    sub = m.dropna(subset=["own_e_b"]).copy()
    banner(f"S1 — rho(scoring, own_e_b): pooled + regions, BOTH "
           f"scorings (N_BOOT={N_BOOT})", "-")
    rho_rows = []
    scopes = [("pooled", sub)] + [
        (f"region{int(r)}", sub[sub["region"] == r])
        for r in sorted(sub["region"].unique())]
    for scope, s in scopes:
        for tag, col in (("mono", "ddg_mono"), ("dimer", "ddg_dimer")):
            rr = position_cluster_bootstrap(s, "position", col,
                                            "own_e_b",
                                            n_boot=N_BOOT, seed=SEED)
            rho_rows.append({"scoring": tag, "scope": scope,
                             "rho": rr["observed_rho"],
                             "ci_lo": rr["ci_lo"], "ci_hi": rr["ci_hi"],
                             "p_boot": rr["p_boot"],
                             "n_rows": rr["n_rows"]})
            flag = "" if rr["ci_lo"] <= 0 <= rr["ci_hi"] else "  (excl 0)"
            print(f"  [{tag:5s}] {scope:8s} rho="
                  f"{rr['observed_rho']:+.4f} "
                  f"[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}] "
                  f"p={rr['p_boot']:.4f} n={rr['n_rows']}{flag}")

    banner("S2 — change itself (dimer - monomer)", "-")
    rm = position_cluster_bootstrap(m, "position", "ddg_mono",
                                    "ddg_dimer", n_boot=N_BOOT,
                                    seed=SEED)
    print(f"  rho(mono, dimer) pooled = {rm['observed_rho']:+.6f} "
          f"[{rm['ci_lo']:+.6f},{rm['ci_hi']:+.6f}] n={rm['n_rows']} "
          f"(how much the scoring change moves rankings at all)")
    print(f"  Delta: mean {m['delta'].mean():+.5f}, "
          f"mean|D| {m['abs_delta'].mean():.5f}, "
          f"max|D| {m['abs_delta'].max():.5f} (model units, "
          f"{len(m)} variants)")
    pos_tbl = (m.groupby(["position", "region"])
                 .agg(mean_delta=("delta", "mean"),
                      mean_abs_delta=("abs_delta", "mean"),
                      n_var=("position", "size"),
                      ddg_mono=("ddg_mono", "mean"),
                      ddg_dimer=("ddg_dimer", "mean"),
                      own_e_b=("own_e_b", "mean"))
                 .reset_index())
    for r in sorted(pos_tbl["region"].unique()):
        v = pos_tbl.loc[pos_tbl["region"] == r, "mean_abs_delta"]
        mu, lo, hi = boot_mean_ci(v, N_BOOT, SEED2)
        print(f"  region{int(r)} mean over positions of mean|Delta| "
              f"= {mu:.5f} [{lo:.5f},{hi:.5f}] (n_pos={len(v)})")

    banner("S3 — THE §12.4 CHECK (frozen rule)", "-")
    r4 = {t: next(x for x in rho_rows
                  if x["scoring"] == t and x["scope"] == "region4")
          for t in ("mono", "dimer")}
    m4, lo4, hi4, p4 = paired_delta_rho(sub[sub["region"] == 4],
                                        "ddg_mono", "ddg_dimer",
                                        "own_e_b", N_BOOT, SEED1)
    mp, lop, hip, pp = paired_delta_rho(sub, "ddg_mono", "ddg_dimer",
                                        "own_e_b", N_BOOT, SEED1)
    mono_excl = not (r4["mono"]["ci_lo"] <= 0 <= r4["mono"]["ci_hi"])
    dim_excl = not (r4["dimer"]["ci_lo"] <= 0 <= r4["dimer"]["ci_hi"])
    both_null = (not mono_excl) and (not dim_excl)
    same_sign = np.sign(r4["mono"]["rho"]) == np.sign(r4["dimer"]["rho"])
    cond_a = same_sign or both_null
    cond_b = mono_excl == dim_excl
    cond_c = lo4 <= 0 <= hi4
    holds = cond_a and cond_b and cond_c
    print(f"  region4 mono : rho={r4['mono']['rho']:+.4f} "
          f"[{r4['mono']['ci_lo']:+.4f},{r4['mono']['ci_hi']:+.4f}]")
    print(f"  region4 dimer: rho={r4['dimer']['rho']:+.4f} "
          f"[{r4['dimer']['ci_lo']:+.4f},{r4['dimer']['ci_hi']:+.4f}]")
    print(f"  (a) sign unchanged or both null: {'PASS' if cond_a else 'FAIL'} "
          f"(mono sign {np.sign(r4['mono']['rho']):+.0f}, dimer "
          f"{np.sign(r4['dimer']['rho']):+.0f}, both_null={both_null})")
    print(f"  (b) CI zero-status unchanged: {'PASS' if cond_b else 'FAIL'} "
          f"(excl0 mono={mono_excl}, dimer={dim_excl})")
    print(f"  (c) paired Delta-rho_4 CI includes 0: "
          f"{'PASS' if cond_c else 'FAIL'} — Delta-rho_4 = {m4:+.4f} "
          f"[{lo4:+.4f},{hi4:+.4f}] p={p4:.4f} "
          f"(n_pos={int((sub['region'] == 4).sum())})")
    print(f"  pooled Delta-rho (context): {mp:+.4f} "
          f"[{lop:+.4f},{hip:+.4f}] p={pp:.4f} — NOT part of verdict")

    banner("S4 — mechanism: does the change concentrate at the "
           "interface?", "-")
    pos_tbl = pos_tbl.merge(st, left_on="position", right_on="Position",
                            how="left")
    nan_pos = int(pos_tbl["Dimer relative burial"].isna().sum())
    print(f"  burial coverage on {len(pos_tbl)} analysis positions: "
          f"NaN {nan_pos} (excluded from S4 only), "
          f">0 {int((pos_tbl['Dimer relative burial'] > 0).sum())}, "
          f"==0 {int((pos_tbl['Dimer relative burial'] == 0).sum())} "
          f"— sparse ties: the continuous test is dominated by "
          f"zero-vs-nonzero")
    for scope, s in (("pooled", pos_tbl),
                     ("region4", pos_tbl[pos_tbl["region"] == 4])):
        sb = s.dropna(subset=["Dimer relative burial"])
        if len(sb) < 10:
            print(f"  {scope}: n={len(sb)} with burial — too few, "
                  f"skipped (pre-registered floor 10)")
            continue
        rr = position_cluster_bootstrap(sb, "position",
                                        "Dimer relative burial",
                                        "mean_abs_delta",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"  [{scope:6s}] rho(|Delta|-pos-mean, dimer-rel-burial) "
              f"= {rr['observed_rho']:+.4f} "
              f"[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}] "
              f"p={rr['p_boot']:.4f} n={rr['n_rows']}")
    itf = pos_tbl.dropna(subset=["Dimer relative burial"])
    g1v = itf.loc[itf["Dimer relative burial"] > 0, "mean_abs_delta"]
    g0v = itf.loc[itf["Dimer relative burial"] == 0, "mean_abs_delta"]
    if len(g1v) >= 5 and len(g0v) >= 5:
        rng = np.random.default_rng(SEED2)
        diffs = np.empty(N_BOOT)
        a1, a0 = g1v.to_numpy(), g0v.to_numpy()
        for b in range(N_BOOT):
            diffs[b] = (a1[rng.integers(0, len(a1), len(a1))].mean()
                        - a0[rng.integers(0, len(a0), len(a0))].mean())
        obs_d = a1.mean() - a0.mean()
        dlo, dhi = np.percentile(diffs, [2.5, 97.5])
        print(f"  interface(>0, n={len(a1)}) - non-interface(n={len(a0)}) "
              f"mean position mean|Delta| = {obs_d:+.5f} "
              f"[{dlo:+.5f},{dhi:+.5f}] (position bootstrap, seed 2)")

    # ---- verdict -------------------------------------------------------
    banner("VERDICT (frozen S3 rule; §12.4 anchors disclosed)", "-")
    if holds:
        print("  region-4 result HOLDS under dimer scoring: sign "
              "(or both-null), CI zero-status, and paired Delta-rho all "
              "unchanged — the structural half of §12.4 is NOT a "
              "monomer-scoring artifact (per the in-repo anchors "
              "printed in S5; Part II itself is not in this repo).")
    else:
        print("  region-4 result CHANGED under dimer scoring — which "
              "condition failed is printed in S3; report as-is (a "
              "changed result is a result).")
    print("  ESM side (S5): unaffected by construction — any §12.4 claim "
          "combining both families must quote both this verdict and the "
          "S5 quote together.")

    # ---- outputs + limitations ----------------------------------------
    m[["position", "wt_aa", "mut_aa", "region", "ddg_mono",
       "ddg_dimer", "delta", "own_e_b"]].to_csv(OUT_VAR, index=False)
    pos_tbl.to_csv(OUT_POS, index=False)
    pd.DataFrame(rho_rows).to_csv(OUT_RHO, index=False)
    print(f"\n  saved {len(m)} variant rows -> {OUT_VAR.name}")
    print(f"  saved {len(pos_tbl)} position rows -> {OUT_POS.name}")
    print(f"  saved {len(rho_rows)} region-rho rows -> {OUT_RHO.name}")

    banner("LIMITATIONS (printed with results, AGENTS section 6)", "-")
    print(f"""  1. Part II §12.4 is not in this repo; anchors were the in-repo
     region-4 records (task_region_check.csv quoted in S5 + ThermoMPNN's
     per-region rho here). If §12.4 names a different quantity, revisit.
  2. ESM's region-4 number cannot be altered by this rerun; only
     ThermoMPNN's half of the discrimination is under test.
  3. One structure, one dimer conformation (6FCX A+B as parsed by the
     vendor's own multi-chain path, UNMODIFIED); chain B's contribution
     is whatever their parser+featurizer does with it (parse diagnostics
     printed above; zero third-party edits).
  4. Burial columns are the atlas reference table's (assembly used to
     compute them not stated in-file); {nan_pos} analysis positions lack
     burial values and are excluded from S4 only.
  5. Interface sparse (measured: 39/597 nonzero in full table) — the
     continuous test is dominated by zero-vs-nonzero; printed with result.
  6. Delta in ThermoMPNN model units; G1 max|delta| = {max_d:.3e}
     (reproduction of the published monomer numbers, not replication).
  7. Smoke scope: fragment stages only — the full dimer join and S2/S3
     verdict code ran first at full scale in this run (disclosed).""")

    print(f"\nAD7 DONE  ({time.time() - T0:.1f}s)  VERDICT: "
          f"{'HOLDS' if holds else 'CHANGED'} under dimer scoring "
          f"(ESM side untouched by construction)")
