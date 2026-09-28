"""
Script 118 (task K1, Group K) -- PC1 / global-mode check on the A222V
delta matrix.

PRE-REGISTERED: this docstring was written before the first run; matrix
definitions, centering/imputation convention, comparison set, and the
K1c verdict rule were fixed before any number produced here was seen
(AGENTS sec 6).  Nothing is selected after results.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group K, task K1.

WHAT THE "REAL A222V DELTA MATRIX" IS
  atlas delta_ESM(p, a) = esm2_score_a222v_bg - esm2_score
  (script 109's G3 already proved this identity to 1e-9), i.e. the
  shift of variant (position p, mutant AA a) when the background is
  A222V instead of WT.  K1a builds it from the analysis table
  (task32_analysis_table.csv, delta_ESM column) -- the SAME rows the
  anchor correlates.

K1a -- SVD OF THE 654 x 19 MATRIX
---------------------------------
  * Grid: the 654 analysis-base positions x the 20 amino acids as
    mutant columns.  Per position exactly 19 cells exist (the WT cell
    is structurally absent: 654x20 - 654 = 12,426 possible cells;
    the task's "654x19" = these 12,426).  Present cells = 10,757
    (the base itself); the remaining 1,669 possible cells are
    fitness-dropout missing.  Both counts printed; zero invented.
  * Convention (used for EVERY matrix in this script, real or
    placebo): column-center (subtract each mutant column's mean over
    that matrix's present cells), then mean-impute in centered space
    (missing -> 0, i.e. the column mean).  SVD of the centered,
    imputed matrix; variance fractions from squared singular values.
    This convention is fixed for all of K1a-K1b so fractions are
    comparable; imputation is disclosed with cell counts.
  * Report: PC1 fraction, PC2, PC3, PC1-PC3 cumulative -- plus a
    SENSITIVITY: the same SVD on the subset of positions having all
    19 non-WT cells present (pure-position subset; count printed).
  * Additional sensitivity: the atlas-grid matrix (merged_wt_a222v_
    scores.csv delta_esm on the same 654 positions, which has no
    fitness-dropout missingness -- only structural WT cells) with the
    same convention; its PC1 fractions are reported alongside.

K1b -- THE SAME SVD ON GROUP F'S PLACEBO-BACKGROUND MATRICES
------------------------------------------------------------
  For each placebo background b of Group F (script 109's caches,
  exact shapes re-gated below: AE = task82_ae_raw.csv 129,960 rows =
  57 bgs x 120 pos x 19 subs; W = task69_w2_bg_raw.csv 68,400 rows =
  30 bgs x 120 x 19; position overlap = 41), build the identical
  object: frame positions x mutant columns, cell = delta_b(p, a) =
  score_bg - esm2_score (script 109's exact formula), same
  centering/imputation convention.  A222_V is EXCLUDED from the
  placebo set (it enters as the real matrix, below) -- matching
  script 109's F1b rule.
  * REAL-in-frame comparator per frame: the atlas A222V delta
    restricted to the SAME frame cells (identical shape/structure to
    each placebo matrix -> fractions directly comparable).
  * Frames analysed: AE (56 placebos, 120 pos), W (30 placebos,
    120 pos), COMMON sensitivity (86 placebos, 41 pos).
  * Per matrix: PC1 fraction; PC1 position scores (s1 * u1);
    position 222's |loading| percentile within the frame (or an
    explicit "222 not in this frame" if absent); Spearman rho
    between the matrix's PC1 position scores and the real-in-frame
    PC1 position scores on the shared positions (PC1 sign is
    arbitrary -- RAW signed rho reported, both signs shown, no
    post-hoc sign fixing).
  * Frame summary: placebo PC1-fraction distribution (mean, sd,
    min, max) vs the real-in-frame fraction, printed side by side.
    REAL_FULL (K1a) is printed as context only -- different row
    count, fractions are mildly row-count dependent (disclosed).

K1c -- PROJECT OUT PC1, RECOMPUTE THE ANCHOR
--------------------------------------------
  Residualized cell: delta'(p, a) = delta(p, a) - s1 * u1[p] * v1[a]
  (PC1 removed from the centered matrix, then the column means left
  intact -- i.e. X - PC1_component).  On the 10,757 base rows:
    anchor_before = rho(delta_ESM, own_e.b)        [gate: must equal
                   the canonical -0.08811806424891734 to 1e-9]
    anchor_after  = rho(delta', own_e.b)           [position-cluster
                   bootstrap CI, seed 0, N_BOOT env, p primary]
  Diagnostic: rho(PC1 component at base rows, own_e.b) with CI --
  how much of the anchor rides on the global mode itself.
  SENSITIVITY (reported, not selected over): the same projection
  using the atlas-grid basis (K1a's second sensitivity matrix).
  VERDICT RULE (pre-stated, applied to the PRIMARY):
    - "disappears"  iff the anchor_after CI includes 0;
    - "grows"       iff CI excludes 0 AND |anchor_after| >
                     |anchor_before|;
    - "survives"    iff CI excludes 0 AND |anchor_after| <=
                     |anchor_before|.
  Any outcome is reportable; all three values are printed unrounded
  so the label can be checked against the numbers.

GATES (failure -> print exact mismatch, sys.exit(1)):
  K1  task32 pivot: 654 positions, 20 mutant columns, present cells
      == 10,757, structural WT-cell missing == 654, total missing ==
      2,323; every row's present-cell count EXACTLY equals the base's
      per-position row count (identity -- catches cell misalignment);
      no empty row; canonical anchor identity
      |rho_ref + 0.08811806424891734| < 1e-9.

      DISCLOSURE -- POST-HOC GATE FIX (script 114's G3 precedent):
      the first draft of K1 required >= 15 present cells per row.
      The first run failed it ("a row has only 1 present cells") and
      was STOPPED before any result was computed.  Diagnosis: the
      pivot's per-position present counts match the analysis base's
      per-position row counts exactly, and the atlas grid has all 19
      rows at the affected positions (347, 635, 346, ...) -- so the
      short rows are REAL analysis-set coverage (own_e_b /
      GI_folinate_independent are NaN for many variants at ~123
      positions), not misalignment.  The >= 15 floor was an
      assumption about coverage that the data violates; it is
      replaced by the exact identity it was meant to proxy (row
      counts == base per-position counts + no empty row), which
      catches the bug the floor existed to catch.  No statistic,
      formula, or result threshold was touched.  The coverage
      distribution is printed as data.
  K2  SVD reconstruction max|X_centered - U S Vt| < 1e-9 (task32
      basis and atlas basis).
  K3  cache shapes exactly as script 109's G1 (129,960/57/120,
      68,400/30/120, overlap 41) and every cache cell joins WT
      scores with 0 nulls.
  K4  every placebo matrix: present cells == n_pos x 19 (the caches
      are complete grids) and pivot rows == frame positions.

LIMITATIONS (printed with the output):
  * Mean-imputed cells carry no structure; ~13% of the real matrix's
    possible cells are imputed (1,669/12,426) -- the complete-position
    and atlas-grid sensitivities bound this.
  * PC1 of a positions-x-substitutions matrix mixes "positions that
    move a lot" with "substitutions that move a lot"; the fractions
    describe this matrix, not a universal property of ESM-2.
  * Frame matrices (120 or 41 rows) have noisier fractions than the
    654-row real matrix; the real-in-frame comparator exists exactly
    to remove that row-count confound from the comparison.
  * K1c removes a data-ESTIMATED component; the anchor's own rows
    contributed to the basis being removed (no cross-fitting at the
    position level) -- stated, so the after-value is read with that
    dependence in mind.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/118_k1_pc1_global_mode.py
  N_BOOT=10000 venv/bin/python3 scripts/118_k1_pc1_global_mode.py
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scipy.stats import spearmanr

from scripts.lib.stats import position_cluster_bootstrap

PROC = ROOT / "data" / "processed"
CANON = -0.08811806424891734
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
AA = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L", "M", "N", "P",
      "Q", "R", "S", "T", "V", "W", "Y"]
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def center_impute(pivot):
    """Column-center on present cells; missing -> 0 (centered space).

    Returns (X_centered, col_means, n_present, n_missing)."""
    X = pivot.to_numpy(float)
    with np.errstate(invalid="ignore"):
        col_means = np.nanmean(X, axis=0)
    n_present = int(np.isfinite(X).sum())
    n_missing = int((~np.isfinite(X)).sum())
    Xc = X - col_means[None, :]
    return np.where(np.isfinite(Xc), Xc, 0.0), col_means, n_present, n_missing


def svd_fracs(Xc):
    """Full SVD -> (fracs, U, s, Vt, recon_err)."""
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = s ** 2
    fracs = var / var.sum()
    recon = (U * s) @ Vt
    return fracs, U, s, Vt, float(np.abs(Xc - recon).max())


def pctl_abs(scores, pos, target):
    """Percentile of |target score| among |scores| (0-100) or None."""
    if target is None or not np.isfinite(target):
        return None
    a = np.abs(scores)
    return float((a <= np.abs(target)).mean() * 100.0)


if __name__ == "__main__":
    banner(f"K1 -- PC1 / global-mode check (scripts/118)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ================= K1a: the real matrix ==============================
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"K1 FAIL: base = ({len(base)}, {base['position'].nunique()})")
    piv = base.pivot_table(index="position", columns="mut_aa",
                           values="delta_esm", aggfunc="first")
    piv = piv.reindex(index=sorted(base["position"].unique()),
                      columns=AA)
    Xc, cm, n_pres, n_miss = center_impute(piv)
    wt_pos = t32[["position", "wt_aa"]].drop_duplicates()
    wt_map = dict(zip(wt_pos["position"], wt_pos["wt_aa"]))
    missing_wt = set(piv.index) - set(wt_map)
    if missing_wt:
        gfail(f"K1 FAIL: {len(missing_wt)} base positions lack wt_aa "
              f"(e.g. {sorted(missing_wt)[:5]})")
    # structural missing = cells where mut == WT at that position
    struct = sum(1 for p in piv.index for a in piv.columns
                 if wt_map.get(p) == a and not np.isfinite(
                     piv.loc[p, a]))
    if (len(piv), len(piv.columns)) != (654, 20):
        gfail(f"K1 FAIL: pivot shape {(len(piv), len(piv.columns))} != "
              f"(654, 20)")
    if n_pres != 10757:
        gfail(f"K1 FAIL: present cells {n_pres} != 10757")
    if struct != 654:
        gfail(f"K1 FAIL: structural WT-cell missing {struct} != 654")
    if n_miss != 1669 + 654:
        gfail(f"K1 FAIL: total missing {n_miss} != {1669 + 654}")
    row_pres = np.isfinite(piv.to_numpy(float)).sum(axis=1)
    base_per_pos = (base.groupby("position").size()
                    .reindex(piv.index).to_numpy())
    if not np.array_equal(row_pres, base_per_pos):
        bad = np.where(row_pres != base_per_pos)[0][:5].tolist()
        gfail(f"K1 FAIL: pivot present-counts != base per-position counts "
              f"(cell misalignment) at row indices {bad} "
              f"(pivot {row_pres[bad].tolist()} vs base "
              f"{base_per_pos[bad].tolist()})")
    if row_pres.min() < 1:
        gfail(f"K1 FAIL: empty row(s) with 0 present cells")
    if base.duplicated(["position", "mut_aa"]).any():
        gfail("K1 FAIL: duplicate (position, mut_aa) cells in the base")
    present_mut_eq_wt = sum(
        1 for p in piv.index
        if np.isfinite(piv.loc[p, wt_map[p]]))
    if present_mut_eq_wt:
        gfail(f"K1 FAIL: {present_mut_eq_wt} cells have mut == WT "
              f"(should be structurally absent)")
    ref = position_cluster_bootstrap(base, "position", "delta_esm",
                                     "own_e_b", N_BOOT, SEED)
    if abs(ref["observed_rho"] - CANON) > 1e-9:
        gfail(f"K1 FAIL: reference anchor {ref['observed_rho']!r} != "
              f"canonical {CANON!r}")
    print(f"  K1 PASS: pivot (654 pos x 20 AA cols) present={n_pres} "
          f"(== base rows), structural WT-missing={struct}, total "
          f"missing={n_miss} (= 1669 dropout + 654 structural); row "
          f"present-counts == base per-position counts (identity), min "
          f"present/row={row_pres.min()}")
    print(f"           per-position coverage (cells of 19): "
          f"==19: {(row_pres == 19).sum()}, 15-18: "
          f"{((row_pres >= 15) & (row_pres <= 18)).sum()}, 10-14: "
          f"{((row_pres >= 10) & (row_pres <= 14)).sum()}, 1-9: "
          f"{(row_pres < 10).sum()} (uneven base coverage = data, "
          f"not misalignment -- see GATE K1 disclosure)")
    print(f"           reference anchor rho = {ref['observed_rho']!r} "
          f"== canonical (identity, tol 1e-9)")

    fr, U, s, Vt, err = svd_fracs(Xc)
    if err > 1e-9:
        gfail(f"K2 FAIL: task32-basis SVD reconstruction max|diff| = "
              f"{err!r}")
    print(f"  K2 PASS: task32-basis SVD reconstruction max|diff| = "
          f"{err:.3e}")
    print(f"\n  [K1a] REAL A222V delta matrix, {Xc.shape[0]} pos x "
          f"{Xc.shape[1]} cols, {n_pres} present / {n_miss} imputed:")
    print(f"    PC1 = {fr[0]:.10f}   PC2 = {fr[1]:.10f}   "
          f"PC3 = {fr[2]:.10f}   PC1-PC3 cumulative = "
          f"{fr[:3].sum():.10f}")
    print(f"    singular values (first 5): "
          f"{np.round(s[:5], 6).tolist()}")

    # K1a sensitivity 1: complete-position subset (all 19 non-WT present)
    complete_pos = [p for p, r in zip(piv.index, row_pres) if r == 19]
    sub = piv.loc[complete_pos]
    Xc2, _, np2, nm2 = center_impute(sub)
    fr2, _, _, _, err2 = svd_fracs(Xc2)
    print(f"    SENSITIVITY complete-position subset: "
          f"{len(complete_pos)} positions x {Xc2.shape[1]} cols "
          f"({np2} present, {nm2} structural) -> PC1 = {fr2[0]:.10f}, "
          f"PC1-3 = {fr2[:3].sum():.10f} (recon err {err2:.2e})")

    # K1a sensitivity 2: atlas-grid basis (no fitness-dropout missing)
    mg = pd.read_csv(PROC / "merged_wt_a222v_scores.csv").rename(
        columns={"position_wt": "position", "mut_aa_wt": "mut_aa"})
    piv_a = mg[mg.position.isin(piv.index)].pivot_table(
        index="position", columns="mut_aa", values="delta_esm",
        aggfunc="first").reindex(index=piv.index, columns=AA)
    Xca, _, npa, nma = center_impute(piv_a)
    fra, Ua, sa, Vta, erra = svd_fracs(Xca)
    if erra > 1e-9:
        gfail(f"K2 FAIL: atlas-basis SVD recon max|diff| = {erra!r}")
    print(f"  K2 PASS: atlas-basis SVD reconstruction max|diff| = "
          f"{erra:.3e}")
    print(f"    SENSITIVITY atlas grid on same 654 positions: {npa} "
          f"present / {nma} missing -> PC1 = {fra[0]:.10f}, "
          f"PC1-3 = {fra[:3].sum():.10f}")

    # position-222 loading on the real matrix
    idx222 = list(piv.index).index(222) if 222 in piv.index else None
    scores_full = s[0] * U[:, 0]
    if idx222 is None:
        print("    position 222: NOT among the 654 base positions "
              "(no row -> no loading; consistent with L1's expected "
              "zero-row exclusion)")
    else:
        pct = pctl_abs(scores_full, piv.index, scores_full[idx222])
        print(f"    position 222 PC1 loading = {scores_full[idx222]:+.6f}; "
              f"|loading| percentile within 654 = {pct:.1f}")

    # ================= K1b: placebo matrices =============================
    banner("K1b -- SAME SVD ON GROUP F PLACEBO-BACKGROUND MATRICES", "-")
    wt = pd.read_csv(PROC / "esm2_wt_scores.csv")
    ae = pd.read_csv(PROC / "task82_ae_raw.csv")
    w = pd.read_csv(PROC / "task69_w2_bg_raw.csv")
    pos_ae, pos_w = set(ae.position.unique()), set(w.position.unique())
    inter = pos_ae & pos_w
    if not (len(ae) == 129960 and ae.bg_id.nunique() == 57
            and len(pos_ae) == 120):
        gfail(f"K3 FAIL: AE shape rows={len(ae)} bg={ae.bg_id.nunique()} "
              f"pos={len(pos_ae)}")
    if not (len(w) == 68400 and w.bg_id.nunique() == 30
            and len(pos_w) == 120):
        gfail(f"K3 FAIL: W shape rows={len(w)} bg={w.bg_id.nunique()} "
              f"pos={len(pos_w)}")
    if len(inter) != 41:
        gfail(f"K3 FAIL: position overlap {len(inter)} != 41")
    print(f"  K3 PASS: AE 129,960/57bg/120pos, W 68,400/30bg/120pos, "
          f"overlap {len(inter)} (== script 109's G1)")

    wt2 = wt[["position", "mut_aa", "hgvs_pro", "esm2_score"]]
    aej = ae.merge(wt2, on=["position", "mut_aa"], how="left")
    wj = w.merge(wt[["hgvs_pro", "esm2_score"]], on="hgvs_pro", how="left")
    if aej[["hgvs_pro", "esm2_score"]].isna().any().any() or \
            wj[["hgvs_pro", "esm2_score"]].isna().any().any():
        gfail("K3 FAIL: WT-score join produced nulls")
    aej["delta"] = aej["score_bg"] - aej["esm2_score"]
    wj["delta"] = wj["score_bg"] - wj["esm2_score"]

    def matrix_slice(df, positions):
        d = df[df.position.isin(positions)]
        return d.pivot_table(index="position", columns="mut_aa",
                             values="delta", aggfunc="first").reindex(
            index=sorted(positions), columns=AA)

    def real_in_frame(fdf, positions):
        """Atlas A222V delta on the frame's cache cells (same structure)."""
        cells = fdf[fdf.position.isin(positions)][
            ["position", "mut_aa"]].drop_duplicates()
        a = mg.merge(cells, on=["position", "mut_aa"], how="right")
        return a.pivot_table(index="position", columns="mut_aa",
                             values="delta_esm", aggfunc="first").reindex(
            index=sorted(positions), columns=AA)

    frames = [("AE", aej, sorted(pos_ae)), ("W", wj, sorted(pos_w)),
              ("COMMON", pd.concat([aej, wj], ignore_index=True),
               sorted(inter))]
    rows_out = []
    for fname, fdf, fpos in frames:
        piv_r = real_in_frame(fdf, fpos)
        Xr, _, nr, nmr = center_impute(piv_r)
        frr, Ur, sr, Vtr, err_r = svd_fracs(Xr)
        if err_r > 1e-9:
            gfail(f"K2 FAIL: {fname} real-in-frame recon {err_r!r}")
        sc_real = sr[0] * Ur[:, 0]
        has222 = 222 in piv_r.index
        p222_real = (pctl_abs(sc_real, piv_r.index,
                              sc_real[list(piv_r.index).index(222)])
                     if has222 else None)
        print(f"\n  [{fname}] frame: {len(fpos)} positions, "
              f"real-in-frame PC1 = {frr[0]:.10f} "
              f"(PC1-3 {frr[:3].sum():.10f}), present {nr} / imputed "
              f"{nmr}; pos222 in frame: {has222}"
              + (f", its |loading| pct = {p222_real:.1f}"
                 if p222_real is not None else ""))
        bgs = sorted(set(fdf.bg_id.unique()) - {"A222_V"})
        pfracs = []
        for b in bgs:
            piv_b = matrix_slice(fdf[fdf.bg_id == b], fpos)
            ncell = int(np.isfinite(piv_b.to_numpy(float)).sum())
            if ncell != len(fpos) * 19:
                gfail(f"K4 FAIL: {fname}/{b} present cells {ncell} != "
                      f"{len(fpos) * 19}")
            Xb, _, _, _ = center_impute(piv_b)
            frb, Ub, sb, Vtb, errb = svd_fracs(Xb)
            if errb > 1e-9:
                gfail(f"K2 FAIL: {fname}/{b} recon {errb!r}")
            sc_b = sb[0] * Ub[:, 0]
            raw_rho = float(spearmanr(sc_b, sc_real).statistic)
            p222 = (pctl_abs(sc_b, piv_b.index,
                             sc_b[list(piv_b.index).index(222)])
                    if has222 else None)
            pfracs.append(frb[0])
            rows_out.append(dict(frame=fname, bg_id=b,
                                 pc1_frac=float(frb[0]),
                                 p222_pct=p222,
                                 load_rho_real_raw=raw_rho,
                                 load_rho_abs=abs(raw_rho)))
        pf = np.array(pfracs)
        print(f"    placebo matrices n={len(pf)}: PC1 frac mean "
              f"{pf.mean():.6f} sd {pf.std(ddof=1):.6f} "
              f"range [{pf.min():.6f}, {pf.max():.6f}] | real-in-frame "
              f"{frr[0]:.6f} -> "
              f"{'ABOVE' if frr[0] > pf.max() else 'within'} the placebo "
              f"range")
        if rows_out:
            sub = [r for r in rows_out if r["frame"] == fname]
            lr = np.array([r["load_rho_abs"] for r in sub])
            print(f"    |loading-rho| vs real-in-frame: mean "
                  f"{lr.mean():.4f} max {lr.max():.4f} "
                  f"(PC1 spatial pattern agreement)")
            p222s = [r["p222_pct"] for r in sub if r["p222_pct"] is not None]
            if p222s:
                print(f"    placebo pos222 |loading| percentiles: "
                      f"median {np.median(p222s):.1f} range "
                      f"[{min(p222s):.1f}, {max(p222s):.1f}] "
                      f"(real-in-frame: "
                      f"{p222_real:.1f})" if p222_real is not None else
                      f"    placebo pos222 percentiles: median "
                      f"{np.median(p222s):.1f}")

    pd.DataFrame(rows_out).to_csv(PROC / "task118_k1_placebo_pc1.csv",
                                  index=False)

    # ================= K1c: project out PC1, recompute anchor ============
    banner("K1c -- PROJECT OUT PC1, RECOMPUTE THE ANCHOR", "-")
    comp = s[0] * np.outer(U[:, 0], Vt[0, :])       # centered-space PC1
    pos_index = {p: i for i, p in enumerate(piv.index)}
    col_index = {a: i for i, a in enumerate(piv.columns)}
    # delta' = delta - PC1 component at that cell
    delta_pc1out = []
    comp_vals = []
    raw_vals = base["delta_esm"].to_numpy(float)
    poss = base["position"].to_numpy()
    muts = base["mut_aa"].to_numpy()
    for i in range(len(base)):
        ri = col_index[muts[i]]
        pi = pos_index[poss[i]]
        delta_pc1out.append(raw_vals[i] - comp[pi, ri])
        comp_vals.append(comp[pi, ri])
    base = base.copy()
    base["delta_pc1out"] = np.array(delta_pc1out)
    base["pc1_component"] = np.array(comp_vals)

    after = position_cluster_bootstrap(base, "position", "delta_pc1out",
                                       "own_e_b", N_BOOT, SEED)
    diag = position_cluster_bootstrap(base, "position", "pc1_component",
                                      "own_e_b", N_BOOT, SEED)
    print(f"  PC1 fraction removed (task32 basis): {fr[0]:.6f}")
    print(f"  anchor BEFORE = {ref['observed_rho']:+.9f} "
          f"[{ref['ci_lo']:+.9f}, {ref['ci_hi']:+.9f}] "
          f"p={ref['p_boot']:.4f}  (canonical {CANON!r})")
    print(f"  anchor AFTER  = {after['observed_rho']:+.9f} "
          f"[{after['ci_lo']:+.9f}, {after['ci_hi']:+.9f}] "
          f"p={after['p_boot']:.4f}  (PC1 projected out)")
    print(f"  diagnostic: rho(PC1 component, own_e.b) = "
          f"{diag['observed_rho']:+.6f} "
          f"[{diag['ci_lo']:+.6f}, {diag['ci_hi']:+.6f}] "
          f"p={diag['p_boot']:.4f}")

    # sensitivity: atlas-grid basis projection
    comp_a = sa[0] * np.outer(Ua[:, 0], Vta[0, :])
    delta_a = raw_vals - np.array(
        [comp_a[pos_index[poss[i]], col_index[muts[i]]]
         for i in range(len(base))])
    base["delta_atlas_pc1out"] = delta_a
    after_a = position_cluster_bootstrap(base, "position",
                                         "delta_atlas_pc1out", "own_e_b",
                                         N_BOOT, SEED)
    print(f"  SENSITIVITY (atlas-grid basis): anchor AFTER = "
          f"{after_a['observed_rho']:+.9f} "
          f"[{after_a['ci_lo']:+.9f}, {after_a['ci_hi']:+.9f}] "
          f"p={after_a['p_boot']:.4f}")

    excl0 = not (after["ci_lo"] <= 0 <= after["ci_hi"])
    if not excl0:
        verdict = ("DISAPPEARS: the after-CI includes 0 -- the anchor is "
                   "not distinguishable from zero once PC1 is removed.")
    elif abs(after["observed_rho"]) > abs(ref["observed_rho"]):
        verdict = ("GROWS: the after-CI excludes 0 AND |rho| is larger "
                   "than before -- removing the global mode strengthened "
                   "the anchor.")
    else:
        verdict = ("SURVIVES: the after-CI excludes 0 AND |rho| is not "
                   "larger than before -- the anchor is not carried by "
                   "PC1 alone.")
    print(f"  VERDICT (pre-registered rule): {verdict}")
    print(f"    |before| = {abs(ref['observed_rho']):.9f}, |after| = "
          f"{abs(after['observed_rho']):.9f}, CI after "
          f"[{after['ci_lo']:+.9f}, {after['ci_hi']:+.9f}]")

    pd.DataFrame([
        dict(what="before", rho=ref["observed_rho"], lo=ref["ci_lo"],
             hi=ref["ci_hi"], p=ref["p_boot"]),
        dict(what="after", rho=after["observed_rho"], lo=after["ci_lo"],
             hi=after["ci_hi"], p=after["p_boot"]),
        dict(what="pc1_component_diag", rho=diag["observed_rho"],
             lo=diag["ci_lo"], hi=diag["ci_hi"], p=diag["p_boot"]),
        dict(what="after_atlas_basis", rho=after_a["observed_rho"],
             lo=after_a["ci_lo"], hi=after_a["ci_hi"], p=after_a["p_boot"]),
    ]).to_csv(PROC / "task118_k1_anchor_pc1out.csv", index=False)

    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. Mean-imputed cells carry no structure (1669/12426 =")
    print("     13.4% of possible cells on the primary matrix); the")
    print("     complete-position and atlas-grid sensitivities bound it.")
    print("  2. Fractions describe THIS matrix (positions x muts), not")
    print("     a universal property of ESM-2; row count affects them")
    print("     (real-in-frame comparator exists to remove that for")
    print("     the placebo comparison).")
    print("  3. PC1 was estimated on the same rows whose anchor is")
    print("     recomputed (no position-level cross-fit) -- disclosed.")
    print("  4. Placebo PC1 fractions from 120- or 41-row frames are")
    print("     noisy; real-in-frame is the like-for-like comparator.")
    print("  5. Per-position base coverage is uneven (min 1 of 19;")
    print("     22 positions have <10 cells) -- PC1 loadings at")
    print("     sparse positions are largely mean-imputation-driven;")
    print("     coverage printed with the fractions.")
    print(f"\nWrote {PROC / 'task118_k1_placebo_pc1.csv'}, "
          f"{PROC / 'task118_k1_anchor_pc1out.csv'}")
    print(f"SCRIPT 118 DONE ({time.time() - T0:.1f}s)")
