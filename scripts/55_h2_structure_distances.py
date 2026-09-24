"""
Task H2 (review-triage): sequence vs. structural distance [items 27, 28].

H2a: Recompute the proximity confound (5.4) using C-alpha 3D distance on
6FCX instead of linear sequence distance, and separately distance to the
FAD cofactor site. If delta_ESM tracks sequence distance but not 3D
structure, that confirms attention locality rather than biophysics.

H2b: Pre-register a focused local test restricted to 3D neighbors of 222
plus FAD contacts, properly powered with position-clustered inference.
The one place the pooled result was directionally positive (within 25
residues, though underprinted) deserves its own clean test rather than
being folded into the pooled negative result.

PRE-REGISTERED DESIGN (stated before running -- AGENTS.md §6)
--------------------------------------------------------------
Structure: RCSB 6FCX (human MTHFR catalytic domain + FAD/SAH), chain A.
DBREF maps PDB residues 37-644 directly to UniProt P42898 numbering
(identity numbering, verified in the PDB header). FAD = HETATM resi 701
chain A. The PDB is downloaded once to data/raw/6FCX.pdb and reused.
Gates before anything runs: 222 has a CA atom; FAD 701 has heavy atoms;
else exit 1.

Coverage (stated up front): 6FCX covers positions 37-644 of 656. All 3D
statistics are restricted to structure-covered positions; the linear
statistic is computed BOTH on the full set (for reconciliation against
the published 5.4 value) and on the restricted set (for the paired
comparison with 3D, same rows -- AGENTS.md §5).

H2a statistics (variant level, position-cluster bootstrap, N_BOOT):
  GATE: Spearman(|delta_ESM|, linear |pos-222|) on the full published set
  (phase5, non-null delta_esm AND GI_folinate_independent -- the
  n=10,757 / 654-position set behind the published rho = -0.298) must
  reproduce to |delta| <= 0.005, else sys.exit(1) (sanity, no retry).
  On the restricted (structure-covered) set:
    rho_lin  = Spearman(|delta_ESM|, linear distance)         [same rows]
    rho_3D   = Spearman(|delta_ESM|, C-alpha distance to 222)
    rho_FAD  = Spearman(|delta_ESM|, min heavy-atom distance to FAD)
  Paired cluster bootstraps (positions resampled, both rhos recomputed
  per draw):
    D1 = |rho_lin| - |rho_3D|
    D2 = |rho_lin| - |rho_FAD|
  Pre-registered verdict:
    LINEAR-STRONGER (attention locality confirmed) iff ci_lo(D1) > 0 AND
       ci_lo(D2) > 0 -- sequence distance tracks |delta_ESM| more than
       either 3D metric, on identical rows.
    3D-RELEVANT (biophysics not ruled out) iff ci_hi(D1) < 0 OR
       ci_hi(D2) < 0 -- at least one 3D metric tracks MORE than linear.
    MIXED-INDETERMINATE otherwise.
  Absolute values are used because "tracks distance" is about strength
  of monotone association either way; SIGNED rhos are printed alongside
  so a sign-flip interpretation is visible (disclosed here rather than
  assumed away).

H2b design (mirrors script 32's locality split, swapping the linear
neighborhood for structural ones):
  Sets (fixed now):
    PRIMARY  = union( C-alpha distance to 222 <= 10 A ,
                      min heavy-atom distance to FAD <= 5 A )
               -- the review says "3D neighbors of 222 plus FAD contacts"
               as ONE restricted test; the 5 A FAD cutoff mirrors the
               project's own structure script (MTHFR_structural_alignment
               .pml uses "within 5A").
    COMPONENTS (reported, not cherry-picked): neighbors-10A only;
               FAD-contact-5A only; neighbors-15A (labeled sensitivity).
    REPRODUCTION GATES: linear within-25 residues rho = +0.067 and
               beyond-25 rho = -0.075 (log 5.4 / script 32) to
               |delta| <= 0.005 each, else sys.exit(1).
  Statistic per set: SIGNED Spearman(delta_ESM, GI_folinate_independent)
  with position-cluster bootstrap CI (N_BOOT) + n rows / n positions.
  Pre-registered verdict:
    LOCAL-POSITIVE-SURVIVES iff PRIMARY CI excludes 0 on the POSITIVE
       side (replicating the +0.067 direction with clustered inference).
    NEGATIVE-IN-PRIMARY iff PRIMARY CI excludes 0 on the negative side.
    INCONCLUSIVE-POWER otherwise; power context printed as n_positions
    vs the within-25 set's, and CI width vs the published within-25 CI.
  No retuning of the 10 A / 5 A cutoffs after results.

Null/CI conventions: position-cluster bootstrap throughout (AGENTS §3);
this task reports CIs, not permutation p-values, because the review's
question is directional replication of a published point estimate, and
the primary claims will be reported as CIs with effect sizes alongside
(AGENTS §3).

Env: N_BOOT (default 2000). Smoke with 50-100.
Outputs: data/processed/task55_h2_distances.csv
"""
import sys, os, urllib.request, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import _spearman, position_cluster_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PDB_PATH = RAW / "6FCX.pdb"
PDB_URL = "https://files.rcsb.org/download/6FCX.pdb"
POS222 = 222
CA_CUT_3D = 10.0
CA_CUT_3D_SENS = 15.0
FAD_CUT = 5.0
CHAIN = "A"
FAD_RESI = 701


def pstr(p, n):
    return f"<{1.0 / n:.6f}" if p == 0 else f"{p:.6f}"


def load_pdb():
    if not PDB_PATH.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(PDB_URL, PDB_PATH)
    ca, heavy = {}, {}
    fad = []
    with open(PDB_PATH) as fh:
        for line in fh:
            if not (line.startswith("ATOM") or line.startswith("HETATM")):
                continue
            if line[21] != CHAIN:
                continue
            alt = line[16]
            if alt not in (" ", "A"):
                continue
            elem = line[76:78].strip()
            if elem == "H":
                continue
            resn = line[17:20].strip()
            resi = int(line[22:26])
            xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
            if resn == "FAD" and resi == FAD_RESI:
                fad.append(xyz)
                continue
            if line.startswith("HETATM"):
                continue
            heavy.setdefault(resi, []).append(xyz)
            if line[12:16].strip() == "CA":
                ca[resi] = xyz
    return ca, {k: np.asarray(v) for k, v in heavy.items()}, np.asarray(fad)


def cluster_paired_abs_diff(df, col_x, col_a, col_b, n_boot, seed):
    """Position-cluster bootstrap of |rho(x,a)| - |rho(x,b)|."""
    df = df.reset_index(drop=True)   # positional indices for numpy arrays
    rng = np.random.default_rng(seed)
    idx_map = {p: df.index[df["position"] == p].to_numpy()
               for p in df["position"].unique()}
    keys = np.array(list(idx_map.keys()))
    xa = df[col_x].to_numpy()
    da = df[col_a].to_numpy()
    db = df[col_b].to_numpy()
    out = np.empty(n_boot)
    for i in range(n_boot):
        draw = rng.choice(keys, size=len(keys), replace=True)
        idx = np.concatenate([idx_map[p] for p in draw])
        out[i] = abs(_spearman(xa[idx], da[idx])) - \
                 abs(_spearman(xa[idx], db[idx]))
    obs = abs(_spearman(xa, da)) - abs(_spearman(xa, db))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return {"obs": obs, "ci_lo": lo, "ci_hi": hi, "draws": out}


if __name__ == "__main__":
    # ---------- structure ----------
    ca, heavy, fad = load_pdb()
    if POS222 not in ca:
        print("*** 6FCX chain A has no CA at 222. sys.exit(1)")
        sys.exit(1)
    if len(fad) == 0:
        print("*** 6FCX chain A has no FAD heavy atoms. sys.exit(1)")
        sys.exit(1)
    covered = sorted(p for p in ca if 37 <= p <= 644)
    print(f"6FCX chain A: {len(covered)} positions with CA in 37-644; "
          f"FAD heavy atoms: {len(fad)}")
    ca222 = np.array(ca[POS222])
    dist_ca = {p: float(np.linalg.norm(np.array(ca[p]) - ca222))
               for p in covered}
    fad_arr = fad
    dist_fad = {}
    for p in covered:
        atoms = heavy.get(p)
        if atoms is None:
            continue
        d = np.linalg.norm(atoms[:, None, :] - fad_arr[None, :, :], axis=2)
        dist_fad[p] = float(d.min())

    # ---------- data ----------
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df = df.dropna(subset=["delta_esm", "GI_folinate_independent"]).copy()
    df["abs_delta"] = df["delta_esm"].abs()
    df["dist_lin"] = (df["position"] - 222).abs()
    n_full, p_full = len(df), df["position"].nunique()
    print(f"Analysis set (delta_esm & GI non-null): {n_full} variants, "
          f"{p_full} positions")

    rows = []
    print("\n" + "=" * 74)
    print("H2a: 3D distance (6FCX) vs linear sequence distance")
    print("=" * 74)

    # GATE 1: reproduce published linear rho on the full set.
    # position_cluster_corrected_results.csv columns:
    #   label, n, positions, rho, ...
    pc = pd.read_csv(PROC / "position_cluster_corrected_results.csv")
    pub_mask = pc.iloc[:, 0].astype(str).str.startswith("|delta_ESM| vs distance")
    if pub_mask.sum() != 1:
        print("*** published 5.4 row not uniquely found. sys.exit(1)")
        sys.exit(1)
    rho_pub = float(pc.loc[pub_mask].iloc[0, 3])
    r_full = position_cluster_bootstrap(df, "position", "abs_delta",
                                        "dist_lin", n_boot=min(N_BOOT, 500),
                                        seed=SEED)
    gate1 = abs(r_full["observed_rho"] - rho_pub) <= 0.005
    print(f"  GATE reproduce published |delta| vs linear dist222: "
          f"derived={r_full['observed_rho']:+.6f} published={rho_pub:+.6f} "
          f"|diff|={abs(r_full['observed_rho'] - rho_pub):.2e} "
          f"(tol 0.005) -> {'OK' if gate1 else 'FAIL'}")
    if not gate1:
        print("  *** GATE FAILED -- sanity check failed, no retry. sys.exit(1)")
        sys.exit(1)
    rows.append({"section": "h2a", "stat": "rho_lin_full",
                 "value": r_full["observed_rho"],
                 "ci_lo": r_full["ci_lo"], "ci_hi": r_full["ci_hi"],
                 "n": r_full["n_rows"]})

    # restricted set: structure-covered positions
    df["dist_ca"] = df["position"].map(dist_ca)
    df["dist_fad"] = df["position"].map(dist_fad)
    rs = df.dropna(subset=["dist_ca", "dist_fad"]).copy()
    cov_pos = rs["position"].nunique()
    print(f"  structure-covered subset: {len(rs)} variants, {cov_pos} "
          f"positions (dropped {n_full - len(rs)} variants / "
          f"{p_full - cov_pos} positions outside 37-644 or missing CA)")
    if cov_pos < 50:
        print("*** coverage unexpectedly low. sys.exit(1)")
        sys.exit(1)

    r_lin = position_cluster_bootstrap(rs, "position", "abs_delta",
                                       "dist_lin", n_boot=N_BOOT, seed=SEED)
    r_3d = position_cluster_bootstrap(rs, "position", "abs_delta",
                                      "dist_ca", n_boot=N_BOOT, seed=SEED)
    r_fad = position_cluster_bootstrap(rs, "position", "abs_delta",
                                       "dist_fad", n_boot=N_BOOT, seed=SEED)
    for lbl, r in [("linear (restricted rows)", r_lin),
                   ("C-alpha 3D to 222", r_3d),
                   ("min heavy-atom dist to FAD", r_fad)]:
        print(f"  |delta_ESM| vs {lbl:26s}: rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"n={r['n_rows']} pos={r['n_clusters']}")
        rows.append({"section": "h2a", "stat": f"absdelta_vs_{lbl}",
                     "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "n": r["n_rows"]})

    d1 = cluster_paired_abs_diff(rs, "abs_delta", "dist_lin", "dist_ca",
                                 N_BOOT, SEED + 1)
    d2 = cluster_paired_abs_diff(rs, "abs_delta", "dist_lin", "dist_fad",
                                 N_BOOT, SEED + 2)
    print(f"  paired D1 = |rho_lin| - |rho_3D| = {d1['obs']:+.4f} "
          f"CI=[{d1['ci_lo']:+.4f},{d1['ci_hi']:+.4f}]")
    print(f"  paired D2 = |rho_lin| - |rho_FAD| = {d2['obs']:+.4f} "
          f"CI=[{d2['ci_lo']:+.4f},{d2['ci_hi']:+.4f}]")
    rows.append({"section": "h2a", "stat": "D1_lin_minus_3d",
                 "value": d1["obs"], "ci_lo": d1["ci_lo"], "ci_hi": d1["ci_hi"]})
    rows.append({"section": "h2a", "stat": "D2_lin_minus_fad",
                 "value": d2["obs"], "ci_lo": d2["ci_lo"], "ci_hi": d2["ci_hi"]})
    if d1["ci_lo"] > 0 and d2["ci_lo"] > 0:
        verdict = "LINEAR-STRONGER (attention locality confirmed)"
    elif d1["ci_hi"] < 0 or d2["ci_hi"] < 0:
        verdict = "3D-RELEVANT (biophysics not ruled out)"
    else:
        verdict = "MIXED-INDETERMINATE"
    print(f"  pre-registered H2a verdict: {verdict}")

    # ---------- H2b ----------
    print("\n" + "=" * 74)
    print("H2b: focused local test -- 3D neighbors of 222 + FAD contacts")
    print("=" * 74)
    # reproduction gates: script 32's linear splits
    near = df[df["dist_lin"] <= 25]
    far = df[df["dist_lin"] > 25]
    r_near = position_cluster_bootstrap(near, "position", "delta_esm",
                                        "GI_folinate_independent",
                                        n_boot=min(N_BOOT, 500), seed=SEED)
    r_far = position_cluster_bootstrap(far, "position", "delta_esm",
                                       "GI_folinate_independent",
                                       n_boot=min(N_BOOT, 500), seed=SEED)
    g_near = abs(r_near["observed_rho"] - 0.067) <= 0.005
    g_far = abs(r_far["observed_rho"] - (-0.075)) <= 0.005
    print(f"  GATE within-25:  derived={r_near['observed_rho']:+.6f} "
          f"published=+0.067 |diff|={abs(r_near['observed_rho'] - 0.067):.2e} "
          f"-> {'OK' if g_near else 'FAIL'}")
    print(f"  GATE beyond-25:  derived={r_far['observed_rho']:+.6f} "
          f"published=-0.075 |diff|={abs(r_far['observed_rho'] + 0.075):.2e} "
          f"-> {'OK' if g_far else 'FAIL'}")
    if not (g_near and g_far):
        print("  *** GATE FAILED -- sanity check failed, no retry. sys.exit(1)")
        sys.exit(1)

    nb10 = {p for p, d in dist_ca.items() if d <= CA_CUT_3D}
    nb15 = {p for p, d in dist_ca.items() if d <= CA_CUT_3D_SENS}
    fadc = {p for p, d in dist_fad.items() if d <= FAD_CUT}
    primary = nb10 | fadc
    print(f"  neighborhoods: 3D<=10A: {len(nb10)} positions; "
          f"3D<=15A: {len(nb15)}; FAD<=5A: {len(fadc)}; "
          f"PRIMARY union: {len(primary)}")

    sets = [("PRIMARY union (3D<=10A + FAD<=5A)", primary),
            ("component: 3D neighbors <=10A", nb10),
            ("component: FAD contacts <=5A", fadc),
            ("sensitivity: 3D neighbors <=15A", nb15),
            ("gate context: linear within-25", set(near["position"].unique()))]
    primary_ci = None
    for lbl, posset in sets:
        sub = df[df["position"].isin(posset)]
        if sub["position"].nunique() < 15:
            print(f"  {lbl:36s} SKIPPED ({sub['position'].nunique()} positions)")
            continue
        r = position_cluster_bootstrap(sub, "position", "delta_esm",
                                       "GI_folinate_independent",
                                       n_boot=N_BOOT, seed=SEED)
        print(f"  {lbl:36s} rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
              f"n={r['n_rows']} pos={r['n_clusters']} "
              f"p_boot={pstr(r['p_boot'], N_BOOT)}")
        rows.append({"section": "h2b", "stat": lbl,
                     "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "n": r["n_rows"],
                     "n_pos": r["n_clusters"]})
        if lbl.startswith("PRIMARY"):
            primary_ci = r
    if primary_ci is None:
        print("*** PRIMARY set did not compute. sys.exit(1)")
        sys.exit(1)
    if primary_ci["ci_lo"] > 0:
        v = "LOCAL-POSITIVE-SURVIVES"
    elif primary_ci["ci_hi"] < 0:
        v = "NEGATIVE-IN-PRIMARY"
    else:
        v = "INCONCLUSIVE-POWER"
    print(f"  pre-registered H2b verdict: {v}")
    print(f"  power context: PRIMARY pos={primary_ci['n_clusters']} vs "
          f"within-25 pos={r_near['n_clusters']} (published within-25 "
          f"underpowered claim rested on n=844 rows / CI crossing 0)")

    out = PROC / "task55_h2_distances.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved {out}")
    print("\nLIMITATIONS (script is the record, AGENTS §6): 6FCX covers only")
    print("positions 37-644, so 3D statistics exclude the termini (drops")
    print("printed above, paired D1/D2 use identical rows for fairness).")
    print("One structure, one chain, one FAD site -- chain B and the E. coli")
    print("2FMN structure were not used (would duplicate, not add, evidence).")
    print("CA distance is a coarse proxy for 'near'; side-chain orientation")
    print("and solvent exposure are not modeled. The 10A/5A cutoffs are")
    print("pre-registered and were NOT tuned after results. CIs are")
    print("position-cluster bootstrap (AGENTS §3); no permutation p-values")
    print("claimed here -- effect sizes + CIs are the report.")
