"""AE3 — The phylogenetic/clade hypothesis (task doc L331-345).
PRE-REGISTERED: this docstring was written before the first run.

AE3a (L332-335): fraction of MTHFR homologs carrying Val at the column
aligned to human residue 222.
  ALIGNMENT REUSE (budget convention, disclosed): Group AB's fetch,
  data/external/ProteinGym/MTHR_HUMAN_2023-08-07_b02.a2m (3,316,659 B,
  AB1 fetched it within the session budget; 0 new bytes fetched here)
  — the same file AD6/script 79 parsed read-only, so it is demonstrably
  suitable and no new fetch is needed (the alternative the task allows
  is not taken; disclosed rather than silently skipped).
  Denominator (frozen): homologs = all non-query records (4,782);
  "carries Val" = uppercase 'V' at 222's match column (a gap or other
  letter does NOT carry Val). Primary fraction = V / all homologs;
  companion = V / homologs with an uppercase residue at that column
  (gap-excluded denominator). Wilson 95% CI printed but LABELED
  DESCRIPTIVE ONLY: MSA sequences are not independent (clade
  redundancy), so this is a sequence-count fraction, not an
  independent-sample estimate.

AE3b (L336-345), CONDITIONAL: "If V222 is common in some clades: test
whether the positions where delta_ESM is largest show clade-specific
residue preferences that co-vary with residue 222's identity."
  FROZEN operationalization (stated before any number is seen):
  - "clade" := grouping homologs BY THEIR RESIDUE AT 222's MATCH COLUMN
    (V-carriers vs A-carriers). This IS the proposed subfamily; NO
    phylogenetic tree is built (disclosed: grouping-by-222 is an
    operationalization of "clade", not a phylogeny).
  - CONDITION to run AE3b (frozen power floor): BOTH groups >= 50
    sequences. If not met -> AE3b NOT RUN, reported plainly (no
    alternative grouping invented post-hoc).
  - "positions where delta_ESM is largest" := per-position mean
    |delta_esm| over ALL finite-delta rows of
    task32_analysis_table.csv (11,344 rows / 654 positions; MEAN
    chosen over max as the robust statistic — alternatives not used,
    disclosed).
  - Eligible position p: p has a query match column (query-lowercase
    insert positions excluded, accounting printed); AND >= 30 uppercase
    canonical-AA residues per group at p's column (coverage floor,
    frozen); if eligible < 50 positions -> AE3b UNDETERMINED, no test
    claimed.
  - Per-position divergence := JSD (Jensen-Shannon, base 2, in [0,1])
    between the V-group and A-group residue distributions over the 20
    canonical AAs at p's column (gaps and non-canonical letters
    excluded from both distributions with counts accounted;
    distributions renormalized over 20).
  - PRIMARY: Spearman(JSD_p, mean|delta_esm|_p) over eligible
    positions; position-cluster bootstrap (positions are the unit;
    resampled with replacement), N_BOOT env default 10,000, seed 0.
  - CONTRAST: quartiles of mean|delta_esm| computed ONCE on the
    observed eligible positions (frozen edges; membership fixed, not
    recomputed per draw); dJSD = mean(JSD top quartile) - mean(JSD
    bottom quartile), same bootstrap, seed 2.
  - REQUIRED CONSISTENCY CHECK (task L343-345, mandatory): AD6's
    alignment-depth result must be checked. Mechanism: per-position
    Neff from AD6's own output (data/processed/task79_depth_positions.csv,
    586 rows) joined to eligible positions; compute the Neff-adjusted
    rank-partial correlation (rank JSD and rank mean|delta| on
    rank Neff, Pearson on residuals; ranking re-done inside every
    bootstrap draw). ALSO print the raw Spearman restricted to the SAME
    joined rows so raw and adjusted are like-for-like. If the join
    yields < 100 rows -> adjusted = UNAVAILABLE (printed), and the
    verdict must then say no unifying claim is made (the task's own
    instruction cannot be satisfied without the check).
  - FROZEN VERDICT RULE:
      "consistent with the evaluator's clade mechanism" IFF
      (a) primary rho CI excludes 0 on the POSITIVE side AND
      (b) dJSD CI excludes 0 on the POSITIVE side.
      If consistent AND adjusted CI excludes 0 positive -> the verdict
      may note, per the task's own wording, that this would offer a
      CANDIDATE explanation for the wrong-sign result AND the region-4
      failure — explicitly qualified: observational not causal, and
      AD6's own region-4 depth reversal ([AD6], log L2614) limits any
      single unifying story. If consistent but adjusted CI includes 0
      -> the verdict MUST state the association does not survive AD6's
      depth control and that the unifying story must NOT be
      over-claimed (alignment-depth structure is the surviving
      alternative). If adjusted UNAVAILABLE -> same no-claim line.
      Otherwise -> "NOT SUPPORTED: <which condition failed> — null
      reported plainly", adjusted printed regardless.
  Effect sizes always printed with significance: rho magnitude, top and
  bottom mean JSDs, dJSD, group sizes, eligible counts (AGENTS s3).

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G1 a2m integrity: 4,783 records, raw query length 656, match-state
     filter (uppercase or '-', exactly script 79's rule) yields 630
     match columns (cumsum), non-conforming records <= 1% (79's rule;
     actual count printed). Literals cross-checked against script 79's
     own module constants (two independent bindings must agree).
  G2 sequence/label identity: raw query letters == esm2_wt_scores.csv
     wt_aa at ALL 655 table positions (else STOP — the alignment's
     query is not our human sequence); query[221] == 'A' explicitly
     (222's column must exist: 222 uppercase in query).
  G3 AE3a counts add up: V + A + gap + other == 4,782 homologs.
  G4 delta frame: task32_analysis_table.csv 11,344 rows / 654
     positions / 0 finite-delta NaN (else two-sources disagree -> STOP).
  G5 Neff source: task79_depth_positions.csv exists with 586 rows and
     a neff column (AD6's record missing/mismatched -> STOP).
  G6 bootstrap sanity (each statistic): all draws finite (NaN draws
     excluded and counted), draw count == N_BOOT, point estimate
     inside its own 95% CI (else resampling broken -> fail; do not
     raise N).
  G7 CSV row accounting: positions CSV rows == candidate count; every
     eligible row has finite JSD.

SMOKE: N_BOOT=300, same code path (stats-only script, no model — full
path minus draw count). Full: N_BOOT=10000.

OUTPUTS: data/processed/task83_ae3a_222_column.csv (1 row),
task83_ae3b_positions.csv (candidate positions with JSD/coverage),
task83_ae3b_results.csv (statistics + CIs + verdict scalars).
No existing script/lib/result modified; alignment read-only. Next free
script number after this: 84.
"""
import importlib.util
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
A2M_PATH = ROOT / "data" / "external" / "ProteinGym" / "MTHR_HUMAN_2023-08-07_b02.a2m"
WT_CSV = ROOT / "data" / "processed" / "esm2_wt_scores.csv"
T32 = ROOT / "data" / "processed" / "task32_analysis_table.csv"
T79 = ROOT / "data" / "processed" / "task79_depth_positions.csv"
OUT_A = ROOT / "data" / "processed" / "task83_ae3a_222_column.csv"
OUT_POS = ROOT / "data" / "processed" / "task83_ae3b_positions.csv"
OUT_RES = ROOT / "data" / "processed" / "task83_ae3b_results.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SEED_Q = 2
FLOOR_GROUP = 50       # AE3b condition: both 222-groups >= 50 seqs
FLOOR_POS = 30         # per-position coverage floor per group
FLOOR_ELIG = 50        # minimum eligible positions to claim a test
FLOOR_JOIN = 100       # minimum neff-join rows for the depth check
T0 = time.time()

# script 79's parser reused (AD6's validated a2m path)
_s79_spec = importlib.util.spec_from_file_location(
    "s79", ROOT / "scripts" / "79_alignment_depth_discriminator.py")
_s79 = importlib.util.module_from_spec(_s79_spec)
_s79_spec.loader.exec_module(_s79)
parse_a2m = _s79.parse_a2m

CANON20 = np.frombuffer(b"ACDEFGHIKLMNPQRSTVWY", dtype=np.uint8)  # sorted
LUT = np.full(256, -1, dtype=np.int8)
for _i, _c in enumerate(CANON20):
    LUT[_c] = _i


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def pfmt(p):
    return "<1/N" if p == 0 else f"{p:.4f}"


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(center - half), float(center + half)


def jsd(p, q):
    """Jensen-Shannon divergence, base 2, in [0,1]; 0*log0 = 0.
    (Smoke 1 caught log2(2*p/m) — an exact +1 level shift; correct term
    is log2(p/m) == log2(2p/(p+q)). Shift-invariant for rho/dJSD, but
    levels must be on the true [0,1] scale. Range self-check added.)"""
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl_pm = np.where(p > 0,
                         p * np.log2(np.where(p > 0,
                                              p / np.where(m > 0, m, 1), 1)),
                         0.0)
        kl_qm = np.where(q > 0,
                         q * np.log2(np.where(q > 0,
                                              q / np.where(m > 0, m, 1), 1)),
                         0.0)
    val = float(0.5 * kl_pm.sum() + 0.5 * kl_qm.sum())
    if not (-1e-12 <= val <= 1.0 + 1e-12):
        gfail(f"JSD range FAIL: {val} outside [0,1] — divergence broken")
    return min(max(val, 0.0), 1.0)


def boot(idx_ranges, stat_fn, n_boot, seed, label):
    """Generic position-level bootstrap: stat_fn(idx_array) -> scalar.
    Resample rows (positions) with replacement; re-derive per draw."""
    obs = stat_fn(np.arange(idx_ranges))
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot)
    for b in range(n_boot):
        draws[b] = stat_fn(rng.integers(0, idx_ranges, idx_ranges))
    n_nan = int((~np.isfinite(draws)).sum())
    d = draws[np.isfinite(draws)]
    if d.size != n_boot:
        print(f"  ({label}: {n_nan} NaN draws excluded)")
    if d.size < 0.5 * n_boot:
        gfail(f"G6 FAIL ({label}): >50% NaN draws — statistic broken")
    lo, hi = np.percentile(d, [2.5, 97.5])
    p = min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0)
    if not np.isfinite(obs):
        gfail(f"G6 FAIL ({label}): point estimate non-finite")
    if not (lo <= obs <= hi):
        gfail(f"G6 FAIL ({label}): obs {obs:.6f} outside own CI "
              f"[{lo:.6f},{hi:.6f}] — resampling broken")
    if d.size != n_boot and d.size == n_boot - n_nan:
        pass  # accounted
    return float(obs), float(lo), float(hi), float(p), n_nan


if __name__ == "__main__":
    banner(f"AE3 — CLADE TEST: Val-fraction at aligned col 222 + "
           f"JSD-vs-|delta| association (scripts/83)  N_BOOT={N_BOOT} "
           f"seeds {SEED}/{SEED_Q}")

    # ---------------- parse + gates -------------------------------------
    recs = parse_a2m(A2M_PATH)
    if (len(recs) != 4783 or _s79.N_RECORDS != 4783
            or _s79.MATCH_LEN != 630 or _s79.QUERY_LEN != 656):
        gfail(f"G1 FAIL: records {len(recs)} (s79 N_RECORDS "
              f"{_s79.N_RECORDS}) != 4783, or s79 constants "
              f"MATCH_LEN={_s79.MATCH_LEN}/QUERY_LEN={_s79.QUERY_LEN} "
              f"disagree with 630/656")
    qhdr, query = recs[0]
    if len(query) != 656:
        gfail(f"G1 FAIL: query raw len {len(query)} != 656")
    filtered = ["".join(c for c in s if c.isupper() or c == "-")
                for _, s in recs]
    n_bad = sum(1 for f in filtered if len(f) != 630)
    if n_bad > 0.01 * 4783:
        gfail(f"G1 FAIL: {n_bad} records do not filter to 630 match "
              f"chars (>1%)")
    print(f"  G1 PASS: 4,783 records, query raw len 656, match state "
          f"630 cols, {n_bad} non-conforming (<=1% rule, s79 constants "
          f"agree)")

    qcol_of_pos = {}
    col = 0
    for i, c in enumerate(query, start=1):
        if c.isupper():
            qcol_of_pos[i] = col
            col += 1
    if col != 630:
        gfail(f"G1 FAIL: cumsum {col} != 630")
    if 222 not in qcol_of_pos or query[221].upper() != "A":
        gfail(f"G2 FAIL: position 222 not a query match column or "
              f"query[221]={query[221]!r} upper != 'A'")

    # G2 implementation note (smoke 1 caught this): esm2_wt_scores.csv is
    # VARIANT-level (12,445 rows, positions repeat) and a2m case encodes
    # match/insert state, so identity = one letter per UNIQUE position,
    # compared case-insensitively. Gate intent (docstring): the
    # alignment's query carries the WT-table residue letters at all 655.
    wt = pd.read_csv(WT_CSV)
    if wt["position"].nunique() != 655:
        gfail(f"G2 FAIL: WT table {wt['position'].nunique()} unique "
              f"positions != 655")
    wt_letters = wt.groupby("position")["wt_aa"].nunique()
    if int((wt_letters != 1).sum()) != 0:
        gfail(f"G2 FAIL: {int((wt_letters != 1).sum())} positions carry "
              f"conflicting wt_aa within the WT table")
    wt_map = wt.drop_duplicates("position").set_index("position")["wt_aa"]
    mism = [(int(p), w, query[int(p) - 1])
            for p, w in wt_map.items()
            if query[int(p) - 1].upper() != w]
    if mism:
        gfail(f"G2 FAIL: query letter != WT-table letter at "
              f"{len(mism)} unique positions; first 5: {mism[:5]}")
    n_lower = sum(1 for c in query if c.islower())
    print(f"  G2 PASS: query letters (case-insensitive; a2m case = "
          f"match/insert state) == esm2_wt_scores wt_aa at all 655 "
          f"unique positions of 12,445 variant rows; {n_lower} query "
          f"residues in insert state (no match col, accounted); "
          f"query[221]='A' -> match col {qcol_of_pos[222]}")

    # ---------------- AE3a: Val fraction at aligned col 222 -------------
    hom_f = filtered[1:]                      # homologs = non-query
    # all homolog filtered strings are exactly 630 chars (G1); stack them
    mat = (np.frombuffer("".join(hom_f).encode(), dtype=np.uint8)
           .reshape(len(hom_f), 630))
    if mat.shape != (4782, 630):
        gfail(f"G3 FAIL: homolog matrix {mat.shape} != (4782, 630)")
    c222 = qcol_of_pos[222]
    colv = mat[:, c222]
    n_V = int((colv == ord("V")).sum())
    n_A = int((colv == ord("A")).sum())
    n_gap = int((colv == ord("-")).sum())
    n_other = int(4782 - n_V - n_A - n_gap)
    if n_V + n_A + n_gap + n_other != 4782 or n_other < 0:
        gfail(f"G3 FAIL: counts do not sum to 4,782")
    n_hom = 4782
    frac_V = n_V / n_hom
    n_res = n_hom - n_gap
    frac_V_res = n_V / n_res if n_res else float("nan")
    w_lo, w_hi = wilson(n_V, n_hom)
    run_b = (n_V >= FLOOR_GROUP and n_A >= FLOOR_GROUP)

    banner("AE3a — fraction of MTHFR homologs carrying Val at the "
           "column aligned to human 222", "-")
    print(f"  alignment: AB1's MTHR_HUMAN a2m reused read-only (0 new "
          f"bytes fetched); {n_hom} homologs (query excluded)")
    print(f"  aligned col for human 222 = match col {c222} (query[221]"
          f"='A' in match state)")
    print(f"  counts: V {n_V} | A {n_A} | gap {n_gap} | other-"
          f"uppercase {n_other}  (sum {n_V + n_A + n_gap + n_other} == "
          f"{n_hom})")
    print(f"  PRIMARY: fraction carrying Val = {frac_V:.6f} "
          f"({n_V}/{n_hom})  Wilson95% [{w_lo:.6f},{w_hi:.6f}] "
          f"DESCRIPTIVE ONLY (MSA sequences non-independent — clade "
          f"redundancy; this is a sequence-count fraction)")
    print(f"  companion (gap-excluded denominator): {frac_V_res:.6f} "
          f"({n_V}/{n_res})")
    print(f"  AE3b CONDITION (frozen floor: both groups >= "
          f"{FLOOR_GROUP}): V-group {n_V} {'>=' if n_V >= FLOOR_GROUP else '<'} "
          f"{FLOOR_GROUP}, A-group {n_A} {'>=' if n_A >= FLOOR_GROUP else '<'} "
          f"{FLOOR_GROUP} -> {'RUN' if run_b else 'NOT RUN'} "
          f"(grouping-by-222 IS the operationalized 'clade'; no tree "
          f"built)")
    pd.DataFrame([dict(n_records=4783, n_homologs=n_hom,
                       match_col_222=c222, n_V=n_V, n_A=n_A,
                       n_gap=n_gap, n_other=n_other, frac_V=frac_V,
                       wilson_lo=w_lo, wilson_hi=w_hi,
                       frac_V_gap_excluded=frac_V_res,
                       floor_met=bool(run_b))]).to_csv(OUT_A, index=False)
    print(f"  saved 1 row -> {OUT_A.name}")

    # ---------------- AE3b conditional ----------------------------------
    verdict = ""
    res_rows = [dict(statistic="AE3a_frac_V", value=frac_V,
                     ci_lo=w_lo, ci_hi=w_hi, p_boot=np.nan)]
    if not run_b:
        banner("AE3b — NOT RUN (frozen condition not met)", "-")
        verdict = (f"AE3b NOT RUN: V-group {n_V} or A-group {n_A} below "
                   f"the frozen {FLOOR_GROUP}-sequence floor — the "
                   f"task's conditional antecedent ('V222 common in "
                   f"some clades') is not met on this alignment; "
                   f"reported plainly, no alternative grouping "
                   f"invented.")
        print(f"  {verdict}")
    else:
        t32 = pd.read_csv(T32)
        if len(t32) != 11344 or t32["position"].nunique() != 654 \
                or int(t32["delta_esm"].isna().sum()) != 0:
            gfail(f"G4 FAIL: task32 table {len(t32)} rows / "
                  f"{t32['position'].nunique()} positions / "
                  f"{int(t32['delta_esm'].isna().sum())} delta NaN != "
                  f"11,344 / 654 / 0")
        print(f"  G4 PASS: delta frame 11,344 rows / 654 positions / "
              f"0 delta NaN")
        pos_stat = (t32.assign(ad=t32["delta_esm"].abs())
                        .groupby("position")
                        .agg(mean_abs_delta_esm=("ad", "mean"),
                             region=("region", "first"),
                             n_var=("ad", "size")).reset_index())
        n_cand = len(pos_stat)

        maskV = (mat[:, c222] == ord("V"))
        maskA = (mat[:, c222] == ord("A"))
        rows = []
        n_no_col = 0
        n_floor_fail = 0
        for r in pos_stat.itertuples():
            mc = qcol_of_pos.get(int(r.position))
            if mc is None:
                n_no_col += 1
                rows.append(dict(position=int(r.position),
                                 region=r.region,
                                 match_col=np.nan,
                                 mean_abs_delta_esm=r.mean_abs_delta_esm,
                                 n_var=r.n_var, nV_res=np.nan,
                                 nA_res=np.nan, JSD=np.nan,
                                 eligible=False))
                continue
            cv = mat[maskV, mc]
            ca = mat[maskA, mc]
            lv = LUT[cv]
            la = LUT[ca]
            kv = lv[lv >= 0]
            ka = la[la >= 0]
            if len(kv) < FLOOR_POS or len(ka) < FLOOR_POS:
                n_floor_fail += 1
                rows.append(dict(position=int(r.position),
                                 region=r.region, match_col=mc,
                                 mean_abs_delta_esm=r.mean_abs_delta_esm,
                                 n_var=r.n_var, nV_res=len(kv),
                                 nA_res=len(ka), JSD=np.nan,
                                 eligible=False))
                continue
            pv = np.bincount(kv, minlength=20).astype(float)
            pa = np.bincount(ka, minlength=20).astype(float)
            pv /= pv.sum()
            pa /= pa.sum()
            rows.append(dict(position=int(r.position), region=r.region,
                             match_col=mc,
                             mean_abs_delta_esm=r.mean_abs_delta_esm,
                             n_var=r.n_var, nV_res=len(kv),
                             nA_res=len(ka), JSD=jsd(pv, pa),
                             eligible=True))
        pos_df = pd.DataFrame(rows)
        if len(pos_df) != n_cand:
            gfail(f"G7 FAIL: positions CSV {len(pos_df)} != candidates "
                  f"{n_cand}")
        elig = pos_df[pos_df["eligible"]].reset_index(drop=True)
        print(f"  accounting: 654 delta positions -> {n_no_col} at "
              f"query-insert columns (no match col, excluded) -> "
              f"{n_floor_fail} below the {FLOOR_POS}/group coverage "
              f"floor -> {len(elig)} eligible "
              f"({'test claimed' if len(elig) >= FLOOR_ELIG else 'below FLOOR_ELIG'})")

        if len(elig) < FLOOR_ELIG:
            verdict = (f"AE3b UNDETERMINED: only {len(elig)} eligible "
                       f"positions (< {FLOOR_ELIG} frozen floor) — no "
                       f"test claimed.")
            banner("AE3b — UNDETERMINED", "-")
            print(f"  {verdict}")
        else:
            jsd_arr = elig["JSD"].to_numpy()
            mad_arr = elig["mean_abs_delta_esm"].to_numpy()
            n_e = len(elig)

            def stat_rho(idx):
                return float(spearmanr(jsd_arr[idx],
                                       mad_arr[idx]).statistic)

            rho, r_lo, r_hi, r_p, r_nan = boot(
                n_e, stat_rho, N_BOOT, SEED, "primary_rho")
            q25, q75 = np.percentile(mad_arr, [25, 75])
            top = mad_arr >= q75
            bot = mad_arr <= q25

            def stat_d(idx):
                t = idx[top[idx]]
                b = idx[bot[idx]]
                if t.size == 0 or b.size == 0:
                    return np.nan
                return float(jsd_arr[t].mean() - jsd_arr[b].mean())

            dJ, d_lo, d_hi, d_p, d_nan = boot(
                n_e, stat_d, N_BOOT, SEED_Q, "quartile_dJSD")
            mean_top = float(jsd_arr[top].mean())
            mean_bot = float(jsd_arr[bot].mean())

            t79 = pd.read_csv(T79)
            if len(t79) != 586 or "neff" not in t79.columns:
                gfail(f"G5 FAIL: task79 {len(t79)} rows / neff col "
                      f"present={('neff' in t79.columns)} != 586/True")
            print(f"  G5 PASS: AD6's depth table 586 rows with neff")
            joined = elig.merge(t79[["position", "neff"]],
                                on="position", how="inner")
            n_j = len(joined)
            raw_lo = raw_hi = raw_p = np.nan
            adj = adj_lo = adj_hi = adj_p = np.nan
            adj_label = ""
            if n_j >= FLOOR_JOIN:
                jsd_j = joined["JSD"].to_numpy()
                mad_j = joined["mean_abs_delta_esm"].to_numpy()
                nef_j = joined["neff"].to_numpy()

                def stat_raw(idx):
                    return float(spearmanr(jsd_j[idx],
                                           mad_j[idx]).statistic)

                raw, raw_lo, raw_hi, raw_p, _ = boot(
                    n_j, stat_raw, N_BOOT, SEED, "raw_on_joined")

                def stat_adj(idx):
                    rj = rankdata(jsd_j[idx])
                    rd = rankdata(mad_j[idx])
                    rn = rankdata(nef_j[idx])
                    rn = rn - rn.mean()
                    if (rn * rn).sum() == 0:
                        return np.nan
                    bj = (rn * (rj - rj.mean())).sum() / (rn * rn).sum()
                    bd = (rn * (rd - rd.mean())).sum() / (rn * rn).sum()
                    rjr = (rj - rj.mean()) - bj * rn
                    rdr = (rd - rd.mean()) - bd * rn
                    sj, sd_ = rjr.std(), rdr.std()
                    if sj == 0 or sd_ == 0:
                        return np.nan
                    return float(np.corrcoef(rjr, rdr)[0, 1])

                adj, adj_lo, adj_hi, adj_p, adj_nan = boot(
                    n_j, stat_adj, N_BOOT, SEED, "neff_adjusted")
                adj_label = "available"
                print(f"  depth join: {n_j} eligible positions carry "
                      f"neff (raw-on-joined rho {raw:+.6f} "
                      f"[{raw_lo:+.6f},{raw_hi:+.6f}] p={pfmt(raw_p)}; "
                      f"adjusted {adj:+.6f} [{adj_lo:+.6f},"
                      f"{adj_hi:+.6f}] p={pfmt(adj_p)})")
            else:
                adj_label = f"UNAVAILABLE (join n={n_j} < {FLOOR_JOIN})"
                print(f"  depth join: {n_j} eligible positions carry "
                      f"neff -> {adj_label} — per the task, no "
                      f"unifying claim can be made without this check")

            pos_df.to_csv(OUT_POS, index=False)

            banner("AE3b — statistics (position unit; JSD base 2; "
                   "Neff-adjusted check is MANDATORY per task L343-345)",
                   "-")
            print(f"  group sizes: V {n_V} / A {n_A} at col {c222}; "
                  f"eligible positions {n_e}; quartile edges "
                  f"[{q25:.6f},{q75:.6f}] (observed, membership fixed)")
            print(f"  PRIMARY rho(JSD, mean|delta|) = {rho:+.6f} "
                  f"[{r_lo:+.6f},{r_hi:+.6f}] p={pfmt(r_p)}"
                  + ("" if r_nan == 0 else f" ({r_nan} NaN draws)"))
            print(f"  CONTRAST mean JSD top quartile {mean_top:.6f} - "
                  f"bottom {mean_bot:.6f} = dJSD {dJ:+.6f} "
                  f"[{d_lo:+.6f},{d_hi:+.6f}] p={pfmt(d_p)}"
                  + ("" if d_nan == 0 else f" ({d_nan} NaN draws)"))
            print(f"  effect sizes: rho magnitude {abs(rho):.6f}, dJSD "
                  f"{abs(dJ):.6f} JSD units on a [0,1] scale (top "
                  f"{mean_top:.6f} vs bottom {mean_bot:.6f})")

            res_rows += [
                dict(statistic="primary_rho_JSD_vs_madelta",
                     value=rho, ci_lo=r_lo, ci_hi=r_hi, p_boot=r_p),
                dict(statistic="quartile_dJSD_top_minus_bottom",
                     value=dJ, ci_lo=d_lo, ci_hi=d_hi, p_boot=d_p),
                dict(statistic="meanJSD_top", value=mean_top,
                     ci_lo=np.nan, ci_hi=np.nan, p_boot=np.nan),
                dict(statistic="meanJSD_bottom", value=mean_bot,
                     ci_lo=np.nan, ci_hi=np.nan, p_boot=np.nan),
                dict(statistic="raw_rho_on_neff_joined", value=raw,
                     ci_lo=raw_lo, ci_hi=raw_hi, p_boot=raw_p),
                dict(statistic="neff_adjusted", value=adj,
                     ci_lo=adj_lo, ci_hi=adj_hi, p_boot=adj_p)]

            # ---- frozen verdict rule -----------------------------------
            cond_a = r_lo > 0
            cond_b = d_lo > 0
            banner("VERDICT (frozen rule; stated before any number "
                   "was seen)", "-")
            print(f"  (a) primary rho CI excludes 0 on + side: "
                  f"{cond_a} | (b) dJSD CI excludes 0 on + side: "
                  f"{cond_b} | depth check: {adj_label}")
            if cond_a and cond_b:
                if adj_label == "available" and adj_lo > 0:
                    verdict = (
                        "CONSISTENT with the evaluator's clade mechanism "
                        "(both frozen conditions met) AND the association "
                        "survives AD6's depth control (adjusted CI "
                        "excludes 0). Per the task's own wording this "
                        "would offer a CANDIDATE explanation for the "
                        "wrong-sign result AND the region-4 failure — "
                        "offered explicitly as a candidate, observational "
                        "not causal; AD6's own region-4 depth reversal "
                        "([AD6], log L2614) remains a limit on any "
                        "single unifying story.")
                elif adj_label == "available":
                    verdict = (
                        "both frozen conditions met, BUT the association "
                        "does NOT survive AD6's depth control (adjusted "
                        "CI includes 0) — per the task's instruction do "
                        "NOT over-claim a unifying story: what survives "
                        "may be alignment-depth structure (AD6), not "
                        "clade-specific residue preference.")
                else:
                    verdict = (
                        "both frozen conditions met, BUT the depth "
                        f"consistency check is {adj_label} — per the "
                        "task's instruction no unifying claim is made.")
            else:
                failed = " and ".join(
                    [n for n, c in (("primary rho", cond_a),
                                    ("quartile dJSD", cond_b))
                     if not c])
                verdict = (f"NOT SUPPORTED: {failed} failed the frozen "
                           f"condition(s) — null reported plainly. "
                           f"Depth check result: {adj_label}"
                           + (f", adjusted {adj:+.6f} "
                              f"[{adj_lo:+.6f},{adj_hi:+.6f}]"
                              if adj_label == "available" else ""))
            print(f"  VERDICT: {verdict}")
    # ---------------- outputs + limitations ------------------------------
    pd.DataFrame(res_rows).to_csv(OUT_RES, index=False)
    if "pos_df" in dir():
        print(f"\n  saved positions CSV ({len(pos_df)} rows) -> "
              f"{OUT_POS.name}")
    print(f"  saved results CSV ({len(res_rows)} rows) -> {OUT_RES.name}")
    banner("LIMITATIONS (printed with results, AGENTS s6)", "-")
    print(f"""  1. MSA fractions are sequence-counts over non-independent
     sequences (clade redundancy); Wilson CI is descriptive only.
  2. 'Clade' := grouping by the 222-column residue — an
     operationalization of the proposed subfamily; NO phylogeny/tree
     was built; the floor is a power floor, not clade detection.
  3. Gaps/non-canonical letters excluded per position from residue
     distributions (coverage floors printed; accounting in
     task83_ae3b_positions.csv).
  4. Positions at query-insert columns (no match column) excluded —
     {0 if 'n_no_col' not in dir() else n_no_col} of 654, accounted.
  5. mean|delta_esm| uses the full 11,344-row delta frame (e.b not
     needed here); quartile membership fixed by observed edges.
  6. Neff comes from AD6's 586-position frame — the depth check runs
     only on the joined subset; raw-on-joined is printed alongside so
     raw and adjusted compare like-for-like.""")
    print(f"\nAE3 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
