"""
Script 71 (task AB2, group AB of DETECTION_FLOOR_AND_MECHANISM.md):
one multi-model comparison table against measured e.b, now that AB1
found ProteinGym ships precomputed scores for this project's own assay
(MTHR_HUMAN_Weile_2021).

WHY (task doc AB2a)
------------------------------------------------------------------
Our headline is a single number: delta_ESM rho = -0.08811806424891734
(signed, own e_b, n=10757, position-cluster bootstrap).  Without
running any model ourselves, AB2a asks for the same statistic for
EVERY model ProteinGym already scored on this exact assay, giving the
immediately comparable multi-model context.  AB2b (do ProteinGym's
ESM-1v scores satisfy AC4's five-seed question?) and AB2c (does an
EVmutation/coupling score exist, satisfying Group T?) are column-
inspection verdicts recorded in DEEPDIVE_LOG.md, not script outputs.

INPUTS (fixed paths -- the file-location choice, stated per AGENTS 2)
------------------------------------------------------------------
  data/processed/task32_analysis_table.csv
      script 32's analysis table: own_e_b, GI_folinate_independent
      (published e.b), delta_esm, position, wt_aa, mut_aa.
  data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv
      fetched in AB1 by HTTP-Range extraction from
      https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/
      zero_shot_substitutions_scores.zip (entry
      MTHR_HUMAN_Weile_2021.csv, csize 9650420, usize 29370765),
      md5 7f9ddcc0589f5f93821e8c0a3e5bb539.  12464 rows, 95 model
      score columns, zero NaNs (verified in AB1).
  data/processed/task32_delta_esm_primary.csv   (anchor row, read-only)

PRE-REGISTERED RULES (fixed in this docstring BEFORE any run; AGENTS 6)
------------------------------------------------------------------
R1  Analysis base = rows non-null on own_e_b,
    GI_folinate_independent AND delta_esm.  Measured before writing
    this script: own and pub dropna sets are the SAME 10757 rows /
    654 positions (the 587 e.b-NaN rows are identical for both
    columns), so a single shared frame serves both targets and every
    model row shares one n, directly comparable with the delta_ESM
    reference row.  Every filtering step's row count is printed
    (AGENTS 5: account for every dropped row).
R2  Join key = f"{wt_aa}{position}{mut_aa}" vs ProteinGym's `mutant`
    string (both sources number the same 656-aa sequence 1-based).
    Inner join.  FAIL gate: joined n < 95% of base n -> exit(1)
    (a priori: ProteinGym covers ALL 12464 single substitutions, a
    superset of the atlas missense set, so expected coverage ~100%;
    95% is fixed here before the run).  Identity gate: the A222V row
    must carry ESM2_650M = -5.200280666351318 (the value AB1 measured
    directly from the same file) to atol 1e-12, else exit(1).
R3  Statistic = Spearman rho with position-cluster bootstrap,
    seed=0, n_boot=$N_BOOT, via scripts/lib/stats.py
    (position_cluster_bootstrap) -- literally script 32's estimator
    and its conventions (position-level resampling, p_boot reported as
    primary, p_boot==0 printed as p<1/n_boot).  SIGNED ONLY: the task
    says "correlate each model's scores against measured e.b";
    script 32's absolute arm existed for |delta| vs |e.b| magnitude
    questions and does not transfer to raw score columns (this is the
    AB2 interpretation assumption, logged as such).  Targets:
    own_e_b (own) and GI_folinate_independent (published).  N_PERM is
    read from the environment and reported UNUSED: AB2a is a
    bootstrap comparison table; sign-flip / re-derivation nulls belong
    to AA2/AA3 and are out of this script's scope.
R4  Shared-draw engine with an IDENTITY GATE.  lib re-seeds
    default_rng(seed) inside every position_cluster_bootstrap call,
    and after R1/R2 every score column is NaN-free on the same frame,
    so all 192 pairs see the byte-identical draw sequence; drawing
    once per iteration and applying it to all columns is therefore
    mathematically identical to 192 independent lib calls (which at
    ~35 s per call would take ~2 h).  Gates, both must pass or
    exit(1) with the mismatch printed (AGENTS 4: never relax a check):
      G-anchor: observed rho(delta_esm, own_e_b) must equal
        -0.08811806424891734 (row "signed, own e_b" of
        task32_delta_esm_primary.csv) to 1e-12.  Both paths call the
        same _spearman, so this should be bit-identical.
      G-lib: for the three fixed pairs (delta_esm x own,
        ESM2_650M x own, EVmutation x published) the lib function is
        re-run independently at the same n_boot/seed and
        max |diff| across (observed, ci_lo, ci_hi, p_boot) must be
        < 1e-9.  Observed uses the identical _spearman; boot values
        differ only by float op order (np.corrcoef pairwise vs a
        normalized Gram matrix), expected at ~1e-13.  A p_boot
        boundary flip would trip this gate loudly and be diagnosed,
        never by widening the threshold.
R5  Output = data/processed/task_AB2_proteingym_model_comparison.csv,
    one row per model (95 ProteinGym columns + 1 reference row
    REF_delta_ESM_our_run computed from our own delta_esm column),
    columns: model, own_rho, own_ci_lo, own_ci_hi, own_p_boot,
    pub_rho, pub_ci_lo, pub_ci_hi, pub_p_boot, own_n, own_n_positions,
    pub_n, pub_n_positions; sorted by own_rho ascending (most
    negative first, matching the sign of our headline anchor -- sort
    is cosmetic and fixed here a priori).  N_BOOT < 1000 = smoke run:
    file gets a _smoke suffix and the output says the numbers are
    machinery checks only, NOT findings.

LIMITATIONS (printed with the output, AGENTS 6)
------------------------------------------------------------------
  * Aggregate columns are not seeds: ProteinGym ships TWO ESM-1v
    columns (ESM1v_single, ESM1v_ensemble), not the five individual
    members, so nothing here can answer AC4's seed-agreement question.
  * Score orientation differs per model by design; rho is
    orientation-preserving, so sign disagreement across rows is real
    disagreement in score direction, not a processing artifact.
  * Every row shares ONE measured e.b vector; rows are not
    independent of each other.  This is a descriptive comparison
    table, not 96 independent hypothesis tests, and claims no
    multiple-comparison correction.
  * Reproduction of script 32's anchor row validates this pipeline
    against script 32's (AGENTS 6: reproduction is not replication).
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.stats import position_cluster_bootstrap, _spearman  # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))   # read for convention; UNUSED here (R3)
SEED = 0
SMOKE = N_BOOT < 1000

PG_PATH = ROOT / "data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv"
T32_PATH = ROOT / "data/processed/task32_analysis_table.csv"
ANCHOR_PATH = ROOT / "data/processed/task32_delta_esm_primary.csv"
OUT_PATH = ROOT / ("data/processed/task_AB2_proteingym_model_comparison"
                   + ("_smoke.csv" if SMOKE else ".csv"))

ANCHOR_RHO = -0.08811806424891734     # task32_delta_esm_primary.csv, signed own
A222V_ESM2_650M = -5.200280666351318  # measured in AB1 from the same PG file
TARGETS = [("own_e_b", "own"), ("GI_folinate_independent", "pub")]
META_COLS = {"mutant", "mutated_sequence", "DMS_score", "DMS_score_bin"}
GATE_PAIRS = [("delta_esm", "own_e_b"),
              ("ESM2_650M", "own_e_b"),
              ("EVmutation", "GI_folinate_independent")]


def pstr(p, n_boot):
    return f"<{1.0 / n_boot:.5f}" if p == 0.0 else f"{p:.4f}"


def summarize(boot):
    """Exactly scripts.lib.stats._summarize's two lines (ci + p)."""
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    p = min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0)
    return float(ci_lo), float(ci_hi), float(p)


def main():
    t0 = time.time()
    print(f"Script 71 / AB2a  N_BOOT={N_BOOT} seed={SEED} "
          f"smoke={SMOKE}  (N_PERM={N_PERM} read but UNUSED -- R3)")
    if SMOKE:
        print("*** SMOKE RUN: numbers below are machinery checks only, "
              "NOT findings, NOT for quoting. ***")

    # ---- R1: analysis base -------------------------------------------------
    d0 = pd.read_csv(T32_PATH)
    base = d0.dropna(subset=["own_e_b", "GI_folinate_independent", "delta_esm"]).copy()
    print(f"row accounting: task32 table = {len(d0)} rows -> "
          f"non-null on own_e_b + GI_folinate_independent + delta_esm = "
          f"{len(base)} rows / {base['position'].nunique()} positions "
          f"(script 32's published set = 10757 / 654)")

    # ---- R2: join to ProteinGym -------------------------------------------
    pg = pd.read_csv(PG_PATH)
    model_cols = [c for c in pg.columns if c not in META_COLS]
    print(f"ProteinGym file: {len(pg)} rows, {len(model_cols)} model score "
          f"columns, NaNs = {int(pg[model_cols].isna().sum().sum())}")

    base["key"] = (base["wt_aa"].astype(str) + base["position"].astype(int).astype(str)
                   + base["mut_aa"].astype(str))
    import re
    pat = re.compile(r"^([A-Z])(\d{1,4})([A-Z])$")
    parsed = pg["mutant"].astype(str).str.extract(pat)
    bad = int(parsed.isna().any(axis=1).sum())
    if bad:
        print(f"FAIL R2: {bad} PG mutant strings do not match ^[A-Z]{{d}}[A-Z]$")
        sys.exit(1)
    pg = pg.assign(key=parsed[0] + parsed[1] + parsed[2])
    # wt-letter agreement is enforced by string equality of the key itself
    # (our key vs PG key), so no separate tautological check is claimed.
    d = base.merge(pg[["key"] + model_cols], on="key", how="inner")
    cov = len(d) / len(base)
    print(f"join: matched {len(d)} / {len(base)} base rows "
          f"(coverage {cov:.4f}); dropped {len(base) - len(d)}")
    if cov < 0.95:
        print(f"FAIL R2: coverage {cov:.4f} < 0.95 pre-registered gate")
        sys.exit(1)
    a222v = d.loc[d["key"] == "A222V", "ESM2_650M"]
    ok_id = (len(a222v) == 1
             and np.isclose(float(a222v.iloc[0]), A222V_ESM2_650M,
                            rtol=0, atol=1e-12))
    print(f"R2 identity gate A222V ESM2_650M = "
          f"{float(a222v.iloc[0]) if len(a222v) else 'MISSING'} "
          f"(expected {A222V_ESM2_650M}) -> {'PASS' if ok_id else 'FAIL'}")
    if not ok_id:
        sys.exit(1)
    d = d.sort_index().reset_index(drop=True)   # ascending original order (lib searchsorted needs it)
    n_rows, n_pos = len(d), d["position"].nunique()
    print(f"analysis frame: {n_rows} rows / {n_pos} positions "
          f"(R1 expectation 10757 / 654: "
          f"{'MATCH' if (n_rows, n_pos) == (10757, 654) else 'DIFFERS -- see output'})")

    all_models = model_cols + ["delta_esm"]

    # ---- R4 engine ---------------------------------------------------------
    cols = [t for t, _ in TARGETS] + all_models          # (own, pub) + 96 models
    A = d[cols].to_numpy(dtype=float)                    # (K, n)
    K = len(cols)
    clusters = d["position"].unique()
    idx_by = {c: d.index[d["position"] == c].to_numpy() for c in clusters}
    pos = {c: np.searchsorted(d.index.to_numpy(), idx_by[c]) for c in clusters}
    col_ix = {c: i for i, c in enumerate(cols)}
    m_ix = [col_ix[m] for m in all_models]               # 96
    t_ix = [col_ix[t] for t, _ in TARGETS]               # 2
    pi = np.array([mi for mi in m_ix for _ in t_ix])
    pj = np.array([ti for _ in m_ix for ti in t_ix])
    n_pairs = len(pi)

    # observed via lib's own _spearman (bit-identical to lib by construction)
    obs = np.empty(n_pairs)
    for j, (mi, ti) in enumerate(zip(pi, pj)):
        obs[j] = _spearman(A[mi], A[ti])

    print(f"engine: {K} columns x {N_BOOT} boot draws, "
          f"{n_pairs} pairs (shared-draw, R4)")
    boot = np.empty((N_BOOT, n_pairs))
    rng = np.random.default_rng(SEED)
    nC = len(clusters)
    cl_arr = np.asarray(clusters)
    t_draw = time.time()
    for b in range(N_BOOT):
        drawn = rng.choice(cl_arr, size=nC, replace=True)
        i = np.concatenate([pos[c] for c in drawn])
        R = np.empty((K, i.size))
        for k in range(K):
            r = rankdata(A[k][i])
            R[k] = r - r.mean()
        norms = np.sqrt((R * R).sum(1))
        C = (R @ R.T) / np.outer(norms, norms)
        boot[b] = C[pi, pj]
        if (b + 1) % 1000 == 0:
            el = time.time() - t_draw
            print(f"  {b + 1}/{N_BOOT} draws, {el:.0f}s elapsed, "
                  f"eta {el / (b + 1) * (N_BOOT - b - 1):.0f}s", flush=True)
    print(f"engine done: {time.time() - t_draw:.1f}s")

    # ---- R4 gates ----------------------------------------------------------
    anchor_col = all_models.index("delta_esm")
    anchor_obs = obs[anchor_col * len(t_ix) + 0]   # delta_esm x own (targets order: own, pub)
    d_anchor = abs(anchor_obs - ANCHOR_RHO)
    print(f"G-anchor: observed rho(delta_esm, own) = {anchor_obs!r} "
          f"vs {ANCHOR_RHO!r} |diff| = {d_anchor:.3e} -> "
          f"{'PASS' if d_anchor < 1e-12 else 'FAIL'}")
    if d_anchor >= 1e-12:
        print("FAIL G-anchor (R4): pre-registered 1e-12 threshold not met; "
              "diagnosis required, threshold NOT relaxed.")
        sys.exit(1)

    maxdiff = 0.0
    for mc, tc in GATE_PAIRS:
        ref = position_cluster_bootstrap(d, "position", mc, tc,
                                         n_boot=N_BOOT, seed=SEED)
        mi = all_models.index(mc)
        ti = [t for t, _ in TARGETS].index(tc)
        j = mi * len(t_ix) + ti
        ci_lo, ci_hi, p = summarize(boot[:, j])
        diffs = [abs(obs[j] - ref["observed_rho"]),
                 abs(ci_lo - ref["ci_lo"]),
                 abs(ci_hi - ref["ci_hi"]),
                 abs(p - ref["p_boot"])]
        maxdiff = max(maxdiff, *diffs)
        print(f"G-lib {mc} x {tc}: engine rho={obs[j]:+.12f} "
              f"CI=[{ci_lo:+.12f},{ci_hi:+.12f}] p={p:.6f} | "
              f"lib rho={ref['observed_rho']:+.12f} "
              f"CI=[{ref['ci_lo']:+.12f},{ref['ci_hi']:+.12f}] "
              f"p={ref['p_boot']:.6f} | max|diff|={max(diffs):.3e}")
    print(f"G-lib overall max|diff| = {maxdiff:.3e} "
          f"(threshold 1e-9) -> {'PASS' if maxdiff < 1e-9 else 'FAIL'}")
    if maxdiff >= 1e-9:
        print("FAIL G-lib (R4): shared-draw engine does not reproduce lib; "
              "diagnosis required, threshold NOT relaxed.")
        sys.exit(1)

    # ---- R5 table ----------------------------------------------------------
    rows = []
    for mi, mname in enumerate(all_models):
        row = {"model": (mname if mname != "delta_esm" else "REF_delta_ESM_our_run")}
        for ti, (tcol, tag) in enumerate(TARGETS):
            j = mi * len(t_ix) + ti
            ci_lo, ci_hi, p = summarize(boot[:, j])
            sub = d
            row[f"{tag}_rho"] = obs[j]
            row[f"{tag}_ci_lo"] = ci_lo
            row[f"{tag}_ci_hi"] = ci_hi
            row[f"{tag}_p_boot"] = p
            row[f"{tag}_n"] = int(sub[tcol].notna().sum())
            row[f"{tag}_n_positions"] = int(sub.loc[sub[tcol].notna(), "position"].nunique())
        rows.append(row)
    tbl = pd.DataFrame(rows).sort_values("own_rho").reset_index(drop=True)
    tbl.to_csv(OUT_PATH, index=False)
    print(f"\nwrote {OUT_PATH}  ({len(tbl)} model rows, sorted by own_rho ascending)")

    print("\nfull table (own block, then pub block):")
    with pd.option_context("display.width", 200, "display.max_rows", 200):
        print(tbl[["model", "own_rho", "own_ci_lo", "own_ci_hi", "own_p_boot",
                   "pub_rho", "pub_ci_lo", "pub_ci_hi", "pub_p_boot"]].to_string(index=False))

    print("\ntop 5 / bottom 5 by own_rho:")
    print(tbl.head(5)[["model", "own_rho", "own_ci_lo", "own_ci_hi"]].to_string(index=False))
    print(tbl.tail(5)[["model", "own_rho", "own_ci_lo", "own_ci_hi"]].to_string(index=False))

    for m in ["REF_delta_ESM_our_run", "ESM2_650M", "ESM2_150M", "ESM1v_single",
              "ESM1v_ensemble", "EVmutation", "Site_Independent", "EVE_ensemble",
              "GEMME", "MSA_Transformer_ensemble", "DeepSequence_ensemble"]:
        r = tbl[tbl["model"] == m]
        if len(r):
            r = r.iloc[0]
            print(f"  {m:26s} own_rho={r['own_rho']:+.6f} "
                  f"CI=[{r['own_ci_lo']:+.4f},{r['own_ci_hi']:+.4f}] "
                  f"p={pstr(r['own_p_boot'], N_BOOT)} | "
                  f"pub_rho={r['pub_rho']:+.6f}")

    print(f"\nAB2 column facts: ESM-1v columns present = "
          f"{[c for c in model_cols if 'ESM1v' in c or 'ESM-1v' in c]} "
          f"(TWO aggregates, not five seeds -> AB2b/AC4 cross-ref); "
          f"EVmutation column present = {'EVmutation' in model_cols} (AB2c/T cross-ref)")
    print("\nLIMITATIONS (R5): aggregate columns are not seeds; rows share one "
          "e.b vector and are not independent of each other; descriptive table, "
          "no multiple-comparison claim; reproducing script 32's anchor row "
          "validates this pipeline against script 32 (reproduction, not "
          "replication).")
    print(f"total runtime {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
