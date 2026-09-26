"""
Task B3 (reliability-and-decompositions): does AE3's clade signal
survive proper controls, or is it generic heterogeneity?
  B3a — size-matched null for the V-group's JSD-vs-|delta_esm| rho
  B3b — placebo columns with comparable minority-residue rarity
  B3c — the pre-registered honest-verdict statement

PRE-REGISTRATION (written before any number below existed; AGENTS s0/s6)

RECORD VALUE UNDER TEST (script 83 / DEEPDIVE_LOG L3004, cited):
  AE3b primary rho(JSD, mean|delta_esm|) = +0.1077795872908862
  [0.024259, 0.191756] p=0.0120, on 580 eligible positions; groups
  V=104 vs A=4,244 at match col 206 (frac_V = 0.021748).

MACHINERY (single implementation, imported not copied): scripts/83's
  parse_a2m (itself script 79's validated parser), LUT/CANON20, scalar
  jsd(), and its gate literals — imported via importlib. JSD is
  additionally computed in a vectorized form for speed and GATED for
  identity against 83's scalar jsd on the actual V/A distributions
  (max|diff| < 1e-12) before any null draw is taken.

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 MSA identity — same structural checks as script 83: 4,783
     records; script-79 constants MATCH_LEN=630/QUERY_LEN=656 agree;
     match-state filter <=1% non-conforming; 630 query match columns;
     query[221]=='A' -> col 206.
  G2 AE3b reproduction — task83_ae3b_positions.csv (654 rows, 580
     eligible): recomputed V/A canonical counts identical to the
     stored nV_res/nA_res (|diff| == 0), vectorized JSD identical to
     the stored JSD (<1e-12), recomputed rho identical to the record
     value (<1e-9). Counts V=104, A=4,244, pool V+A = 4,348 exactly
     (the task's own size statement).
  G4 null-machinery identity (the AGENTS s4 sanity check): feeding the
     ACTUAL V-group indices through the exact per-draw code path must
     reproduce rho within 1e-9. If not -> sys.exit(1) BEFORE any N is
     used.
  G5 draw validity: all N_PERM draws finite (non-finite counted; >50%
     -> fail); discarded draws reported; observed included in the
     reported accounting.
  G6 placebos: every placebo rho finite; if fewer than MIN_PLACEBOS=5
     columns qualify under the frozen window, the shortfall is printed
     plainly (NOT a machinery failure and NOT a reason to widen the
     window).

B3a — SIZE-MATCHED NULL (frozen spec):
  Pool = the 4,348 sequences carrying V or A at 222's match column
  (104+4,244; the task's stated pool). Each draw: 104 sequences drawn
  WITHOUT replacement (seed 0 generator, one rng stream), comparison
  group = the remaining 4,244 — exactly the observed group SIZES.
  Per draw, the full AE3b procedure is re-derived: per-position JSD
  (base 2) between the drawn group's and the remainder's 20-AA
  distributions at every one of the 629 match-column candidate
  positions, gaps/non-canonical excluded with counts accounted,
  positions eligible iff BOTH groups have >= 30 canonical residues
  there (83's FLOOR_POS), >= 50 eligible positions to score a draw
  (83's FLOOR_ELIG), statistic = Spearman(JSD, mean|delta_esm|) on
  that draw's eligible positions (mean|delta_esm| frozen from task32
  via 83's stored per-position values).
  N_PERM env, default 1,000 (smoke 100). Primary p (AGENTS s3):
  p = (1 + #{rho_null >= rho_obs}) / (N_PERM + 1), ONE-SIDED (the
  question is whether the real grouping EXCEEDS random size-matched
  groupings). Null mean/sd/percentiles reported; (obs - mean)/sd is
  printed ONLY as "illustrative z scale", never as the claim.

B3b — PLACEBO COLUMNS (frozen selection, script 29's convention):
  Script 29's convention (its own docstring): run the IDENTICAL
  comparison with placebo inputs; "if within the placebos' range ->
  the pattern belongs to the construction, not the specific claim";
  "the excess over the placebos, with a position-bootstrap interval,
  is the finding."
  Frozen selection rule: candidate columns = 222's match column
  excluded; among script 83's 629 match-column candidates, a column
  qualifies iff (i) its dominant canonical residue (over homologs,
  denominator 4,782 — AE3a's convention) covers >= 50% of homologs;
  (ii) some OTHER canonical residue there has a homolog fraction in
  the rarity window [0.5x, 2x] of 0.021748 = [0.010874, 0.043496]
  (comparable rarity — the residue IDENTITY need not match, per the
  task); (iii) both groups >= 50 carriers (83's frozen power floor).
  Among qualifiers take the residue closest to 222's rarity by
  |log(frac/0.021748)|, columns ordered by that distance (ties ->
  lower column index), CAP = K_MAX = 10. No window widening, no
  hand-picking; fewer than 5 qualifiers -> reported as a shortfall.
  At each placebo column: AE3b's EXACT grouping-and-JSD procedure with
  groups = minority-residue carriers vs dominant-residue carriers
  (same >=30/group position floors, same eligible-set rule), then
  rho(placebo JSD, mean|delta_esm|) on the placebo's own eligible set.
  VERDICT RULE (script 29 reading, frozen):
    actual (0.107780 on its own 580 positions) is compared to the
    STRONGEST placebo rho (max over placebos, on their own eligible
    sets, matching how script 29 compared against both placebos'
    ranges). Additionally a PAIRED position-bootstrap interval
    (N_BOOT, seed 0) of rho_actual - rho_strongest is computed on the
    SHARED eligible positions of the two vectors (resample shared
    positions with replacement, both rhos recomputed per draw).
    - actual <= strongest placebo rho -> "WITHIN PLACEBO RANGE ->
      generic per-position distributional heterogeneity"
    - actual > strongest AND paired-diff 95% CI excludes 0 on the
      positive side -> "EXCEEDS ALL PLACEBOS -> 222-specific excess"
    - actual > strongest BUT paired CI includes 0 -> "point-excess
      only, difference NOT established"

B3c — FROZEN CONDITIONAL (printed verbatim from the task when it
  fires): the restatement "ESM-2's background-shift is larger at
  positions with more sequence heterogeneity in general, not
  anything specific to A222V's biology or clade structure" is
  declared IFF BOTH controls indicate genericness — B3a's one-sided
  p >= 0.05 (actual does NOT exceed the size-matched null) AND B3b's
  verdict is not "EXCEEDS ALL PLACEBOS". If both controls instead
  show specificity the candidate explanation stands (with script
  83's own observational/causal and region-4 caveats restated, never
  dropped). If the two controls disagree, MIXED is printed naming
  which fired. No branch is chosen after seeing results.

LIMITATIONS (printed with results, AGENTS s6):
  - B3a's null draws sequences; it controls GROUP COMPOSITION at fixed
    sizes, not phylogenetic non-independence of the MSA (unchanged
    from AE3's own disclosure).
  - All placebos share one alignment; columns are not independent —
    the comparison is a convention adapted from script 29, not an
    independent replication.
  - rho^2 ~1.2% of rank variance (the effect is small regardless of
    which branch fires — effect size printed alongside every p).
  - The rare-residue window and K_MAX are fixed here BEFORE any
    placebo rho exists; widening them after seeing results would be
    a post-hoc rule change and is not done.

Run: SMOKE=1 venv/bin/python3 scripts/95_b3_clade_controls.py   (timed)
     full: venv/bin/python3 scripts/95_b3_clade_controls.py
Output: data/processed/task95_b3_clade_controls.csv
"""
import importlib.util
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
A2M_PATH = ROOT / "data" / "external" / "ProteinGym" / \
    "MTHR_HUMAN_2023-08-07_b02.a2m"
T83_POS = PROC / "task83_ae3b_positions.csv"
T83_RES = PROC / "task83_ae3b_results.csv"
WT_CSV = PROC / "esm2_wt_scores.csv"
OUT = PROC / ("task95_b3_smoke.csv" if os.environ.get("SMOKE") == "1"
              else "task95_b3_clade_controls.csv")

N_PERM = int(os.environ.get("N_PERM", "1000"))
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SMOKE = os.environ.get("SMOKE") == "1"
SEED = 0
REC_FRAC_V = 0.021748222501045588
REC_RHO = 0.1077795872908862
REC_RHO_TOL = 1e-9
WIN_LO, WIN_HI = 0.5 * REC_FRAC_V, 2.0 * REC_FRAC_V
FLOOR_GROUP, FLOOR_POS, FLOOR_ELIG = 50, 30, 50
K_MAX, MIN_PLACEBOS = 10, 5
DOM_MIN = 0.50
T0 = time.time()


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


# ---- script 83's machinery (THE single implementation) ----
_s83_spec = importlib.util.spec_from_file_location(
    "ae3", ROOT / "scripts" / "83_ae3_clade_test.py")
_s83 = importlib.util.module_from_spec(_s83_spec)
_s83_spec.loader.exec_module(_s83)
parse_a2m, LUT, jsd_scalar = _s83.parse_a2m, _s83.LUT, _s83.jsd
_s79 = _s83._s79                      # script 79's parser module (literals)


def jsd_rows(cnt1, cnt2):
    """Vectorized mirror of 83's scalar jsd over rows of count tables
    (n,20); identity vs the scalar form is a GATE, not an assumption.
    Degenerate rows (a group with 0 canonical residues there -> the
    distribution is undefined) return NaN instead of 0/0 garbage — the
    scalar original never saw such rows because 83 only called it after
    its >=30/group floors; every caller here applies the same floors
    first, so NaNs never enter a statistic (count printed in G2)."""
    s1 = cnt1.sum(axis=1)
    s2 = cnt2.sum(axis=1)
    ok = (s1 > 0) & (s2 > 0)
    out = np.full(len(cnt1), np.nan)
    p = cnt1[ok] / s1[ok, None]
    q = cnt2[ok] / s2[ok, None]
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
    val = 0.5 * kl_pm.sum(axis=1) + 0.5 * kl_qm.sum(axis=1)
    if np.any((val < -1e-12) | (val > 1 + 1e-12)):
        gfail(f"jsd_rows range FAIL: min {val.min()} max {val.max()}")
    out[ok] = np.clip(val, 0.0, 1.0)
    return out


def counts_for(mat, rows, cols):
    """(len(rows) x len(cols)) uint8 matrix -> (len(cols), 20) canonical
    counts; non-canonical/gap (-1) excluded with counts accounted."""
    sub = mat[np.ix_(rows, cols)]
    codes = LUT[sub]                                   # int8, -1 = none
    valid = codes >= 0
    pos_idx = np.broadcast_to(np.arange(len(cols), dtype=np.int64),
                              codes.shape)
    flat = codes.astype(np.int64)[valid] + 20 * pos_idx[valid]
    cnt = np.bincount(flat, minlength=20 * len(cols))
    return cnt.reshape(len(cols), 20).astype(float)


def main():
    log(f"B3 -- AE3 CLADE-SIGNAL CONTROLS (scripts/95) "
        f"{'SMOKE ' if SMOKE else ''}N_PERM={N_PERM} N_BOOT={N_BOOT}")
    log("pre-registered: size-matched null (104 of 4,348, seed 0), "
        "frozen rarity window [0.5x,2x] of 0.021748, K_MAX=10, "
        "script-29 placebo-range reading, B3c conditional fixed")

    # ---- G1: MSA identity (83's checks) ----
    recs = parse_a2m(A2M_PATH)
    if (len(recs) != 4783 or _s79.N_RECORDS != 4783
            or _s79.MATCH_LEN != 630 or _s79.QUERY_LEN != 656):
        gfail(f"G1 FAIL: records {len(recs)} (s79 {_s79.N_RECORDS}/"
              f"{_s79.MATCH_LEN}/{_s79.QUERY_LEN}) != 4783/630/656")
    qhdr, query = recs[0]
    if len(query) != 656:
        gfail(f"G1 FAIL: query raw len {len(query)} != 656")
    filtered = ["".join(c for c in s if c.isupper() or c == "-")
                for _, s in recs]
    n_bad = sum(1 for f in filtered if len(f) != 630)
    if n_bad > 0.01 * 4783:
        gfail(f"G1 FAIL: {n_bad} records do not filter to 630 (>1%)")
    qcol_of_pos, col = {}, 0
    for i, c in enumerate(query, start=1):
        if c.isupper():
            qcol_of_pos[i] = col
            col += 1
    if col != 630 or 222 not in qcol_of_pos or query[221].upper() != "A":
        gfail(f"G1 FAIL: match cols {col}, 222 present="
              f"{222 in qcol_of_pos}, query[221]={query[221]!r}")
    wt = pd.read_csv(WT_CSV)
    wt_map = wt.drop_duplicates("position").set_index("position")["wt_aa"]
    mism = [p for p, w in wt_map.items()
            if query[int(p) - 1].upper() != w]
    if mism:
        gfail(f"G1 FAIL: query letter != WT-table at {len(mism)} "
              f"positions; first 5 {mism[:5]}")
    log(f"G1 PASS: 4,783 records, 630 match cols ({n_bad} non-conforming "
        f"<=1%), query[221]='A' -> col {qcol_of_pos[222]}, query letters "
        f"== esm2_wt_scores at all 655 positions (83's G1/G2 checks)")

    hom_f = filtered[1:]
    mat = (np.frombuffer("".join(hom_f).encode(), dtype=np.uint8)
           .reshape(4782, 630))
    c222 = qcol_of_pos[222]
    colv = mat[:, c222]
    maskV, maskA = colv == ord("V"), colv == ord("A")
    n_V, n_A = int(maskV.sum()), int(maskA.sum())
    idx_pool = np.flatnonzero(maskV | maskA)
    if (n_V, n_A, len(idx_pool)) != (104, 4244, 4348):
        gfail(f"G2 FAIL: V={n_V} A={n_A} pool={len(idx_pool)} != "
              f"104/4244/4348")
    log(f"G2 pool PASS: V={n_V} + A={n_A} = {len(idx_pool)} (the task's "
        f"4,348-sequence V+A set confirmed, not assumed)")

    # ---- G2: AE3b reproduction from 83's stored table ----
    p83 = pd.read_csv(T83_POS)
    if len(p83) != 654:
        gfail(f"G2 FAIL: task83 positions {len(p83)} != 654")
    r83 = pd.read_csv(T83_RES)
    rec_rho = float(r83.loc[r83["statistic"] == "primary_rho_JSD_vs_madelta",
                            "value"].iloc[0])
    if abs(rec_rho - REC_RHO) > 1e-12:
        gfail(f"G2 FAIL: record rho {rec_rho} != {REC_RHO}")
    cand = p83[p83["match_col"].notna()].reset_index(drop=True)
    cand_cols = cand["match_col"].astype(int).to_numpy()
    m_ad = cand["mean_abs_delta_esm"].to_numpy(float)
    if len(cand) != 629:
        gfail(f"G2 FAIL: candidates {len(cand)} != 629")
    cnt_V = counts_for(mat, np.flatnonzero(maskV), cand_cols)
    cnt_A = counts_for(mat, np.flatnonzero(maskA), cand_cols)
    el83 = cand["eligible"].to_numpy(bool)
    d_nV = np.abs(cnt_V.sum(1) - cand["nV_res"].fillna(0).to_numpy())
    d_nA = np.abs(cnt_A.sum(1) - cand["nA_res"].fillna(0).to_numpy())
    if d_nV.max() != 0 or d_nA.max() != 0:
        gfail(f"G2 FAIL: grouping counts differ from 83's stored "
              f"nV_res/nA_res (max {d_nV.max()}/{d_nA.max()})")
    jsd_vec = jsd_rows(cnt_V, cnt_A)
    n_deg = int(np.isnan(jsd_vec).sum())   # degenerate: 0 canonical in a
    # group at that candidate -> JSD undefined there (never scored: the
    # >=30/group floors exclude them exactly as in 83)
    d_jsd = float(np.max(np.abs(jsd_vec[el83]
                                - cand.loc[el83, "JSD"].to_numpy())))
    if d_jsd >= 1e-12:
        gfail(f"G2 FAIL: vectorized JSD vs 83's stored JSD max|diff| "
              f"{d_jsd:.3e} >= 1e-12")
    rho_g2 = float(spearmanr(jsd_vec[el83], m_ad[el83]).statistic)
    if abs(rho_g2 - rec_rho) > REC_RHO_TOL:
        gfail(f"G2 FAIL: rho {rho_g2} vs record {rec_rho} "
              f"(|diff| {abs(rho_g2-rec_rho):.3e}) >= {REC_RHO_TOL}")
    n_elig = int(el83.sum())
    log(f"G2 AE3b reproduction PASS: {n_elig} eligible of 629 candidates "
        f"({n_deg} degenerate/undefined -> NaN, all floor-excluded); "
        f"counts identical (max diff 0), vectorized JSD vs stored "
        f"max|diff|={d_jsd:.2e}, rho {rho_g2:+.12f} == record "
        f"{rec_rho:+.12f} (|diff|={abs(rho_g2-rec_rho):.2e})")

    # ==================================================================
    # B3a — size-matched null
    # ==================================================================
    log("\n" + "=" * 74)
    log("B3a  SIZE-MATCHED NULL: draw 104 of the 4,348 V+A pool vs the "
        "remaining 4,244, exact AE3b procedure per draw")
    log("=" * 74)

    def draw_rho(rows_g1, rows_g2):
        """Exact per-draw path: JSD(g1 vs g2) over candidates, >=30/group
        floors, >=50 eligible, Spearman vs frozen mean|delta_esm|."""
        cg1 = counts_for(mat, rows_g1, cand_cols)
        cg2 = counts_for(mat, rows_g2, cand_cols)
        elig = (cg1.sum(1) >= FLOOR_POS) & (cg2.sum(1) >= FLOOR_POS)
        if int(elig.sum()) < FLOOR_ELIG:
            return np.nan, int(elig.sum())
        j = jsd_rows(cg1[elig], cg2[elig])
        return float(spearmanr(j, m_ad[elig]).statistic), int(elig.sum())

    # G4 identity: the actual V-group through the SAME path
    rho_g4, n_el_g4 = draw_rho(np.flatnonzero(maskV), np.flatnonzero(maskA))
    if abs(rho_g4 - rec_rho) > REC_RHO_TOL or n_el_g4 != n_elig:
        gfail(f"G4 FAIL: actual-group draw rho {rho_g4} (eligible "
              f"{n_el_g4}) vs record {rec_rho} (eligible {n_elig}) — "
              f"null machinery does not reproduce AE3b. STOP.")
    log(f"G4 null-machinery identity PASS: actual V-group through the "
        f"per-draw path -> rho {rho_g4:+.12f}, eligible {n_el_g4} "
        f"(== record, tol {REC_RHO_TOL})")

    rng = np.random.default_rng(SEED)
    rho_obs = rho_g2
    null = np.empty(N_PERM)
    n_dropped = 0
    for b in range(N_PERM):
        draw = rng.choice(idx_pool, size=n_V, replace=False)
        rest = np.setdiff1d(idx_pool, draw, assume_unique=False)
        r, _ = draw_rho(draw, rest)
        if not np.isfinite(r):
            n_dropped += 1
            r = np.nan
        null[b] = r
    fin = null[np.isfinite(null)]
    if fin.size < 0.5 * N_PERM or fin.size < N_PERM - n_dropped:
        gfail(f"G5 FAIL: {n_dropped} non-finite draws (>50% rule)")
    ge = int((fin >= rho_obs).sum())
    p_null = (1 + ge) / (1 + fin.size)
    nmean, nsd = float(fin.mean()), float(fin.std(ddof=1))
    q025, q50, q975 = np.percentile(fin, [2.5, 50, 97.5])
    z_ill = (rho_obs - nmean) / nsd
    log(f"  draws: {N_PERM} requested, {fin.size} finite "
        f"({n_dropped} discarded and counted)")
    log(f"  NULL rho: mean={nmean:+.6f} sd={nsd:.6f} "
        f"p2.5={q025:+.6f} median={q50:+.6f} p97.5={q975:+.6f}")
    log(f"  OBSERVED rho = {rho_obs:+.6f}")
    log(f"  PRIMARY (one-sided): p = (1+{{null >= obs}})/(1+N) = "
        f"(1+{ge})/(1+{fin.size}) = {p_null:.4f}")
    log(f"  effect: obs - null mean = {rho_obs - nmean:+.6f} "
        f"(illustrative z scale only: {z_ill:+.2f} sd — NOT the claim)")
    b3a_exceeds = p_null < 0.05
    log(f"  B3a VERDICT (frozen: p<0.05 = actual exceeds size-matched "
        f"null): {'EXCEEDS the null' if b3a_exceeds else 'does NOT exceed the null -> a rho of this size arises from random 104-groupings'}")

    # ==================================================================
    # B3b — placebo columns, script 29's convention
    # ==================================================================
    log("\n" + "=" * 74)
    log("B3b  PLACEBO COLUMNS: comparable minority rarity, exact AE3b "
        "grouping-and-JSD procedure (script 29 convention)")
    log("=" * 74)
    cnt_hom = counts_for(mat, np.arange(4782), cand_cols)
    frac_hom = cnt_hom / 4782.0                      # AE3a's denominator
    dom_i = frac_hom.argmax(axis=1)
    dom_frac = frac_hom.max(axis=1)
    quals = []
    for j in range(len(cand_cols)):
        if dom_frac[j] < DOM_MIN:
            continue
        others = np.array([k for k in range(20) if k != dom_i[j]])
        fo = frac_hom[j, others]
        in_win = others[(fo >= WIN_LO) & (fo <= WIN_HI)]
        if in_win.size == 0:
            continue
        fracs = frac_hom[j, in_win]
        r_pick = in_win[int(np.argmin(np.abs(np.log(fracs / REC_FRAC_V))))]
        if (cnt_hom[j, r_pick] < FLOOR_GROUP
                or cnt_hom[j, dom_i[j]] < FLOOR_GROUP):
            continue
        dist = abs(float(np.log(frac_hom[j, r_pick] / REC_FRAC_V)))
        quals.append((dist, cand_cols[j], int(r_pick), int(dom_i[j]),
                      float(frac_hom[j, r_pick]), float(dom_frac[j])))
    quals.sort(key=lambda t: (t[0], t[1]))
    sel = quals[:K_MAX]
    AA = "ACDEFGHIKLMNPQRSTVWY"
    log(f"  window [{WIN_LO:.6f}, {WIN_HI:.6f}] (0.5x-2x of "
        f"{REC_FRAC_V:.6f}), dominant >= {DOM_MIN:.0%}, floors >="
        f"{FLOOR_GROUP}: {len(quals)} columns qualify; top {len(sel)} "
        f"taken by |log(frac/222frac)| (K_MAX={K_MAX}, no widening)")
    if len(sel) < MIN_PLACEBOS:
        log(f"  *** SHORTFALL: only {len(sel)} placebo columns (< "
            f"{MIN_PLACEBOS}); reported plainly, window NOT widened ***")
    rows_b = []
    for (dist, mc, r_i, d_i, f_r, f_d) in sel:
        g1 = np.flatnonzero(mat[:, mc] == ord(AA[r_i]))
        g2 = np.flatnonzero(mat[:, mc] == ord(AA[d_i]))
        cg1 = counts_for(mat, g1, cand_cols)
        cg2 = counts_for(mat, g2, cand_cols)
        el = (cg1.sum(1) >= FLOOR_POS) & (cg2.sum(1) >= FLOOR_POS)
        if int(el.sum()) < FLOOR_ELIG:
            log(f"  col {mc:3d}: minority {AA[r_i]} {f_r:.4%} vs "
                f"dominant {AA[d_i]} {f_d:.4%} -> only {int(el.sum())} "
                f"eligible (<{FLOOR_ELIG}) — skipped, counted")
            continue
        j = jsd_rows(cg1[el], cg2[el])
        rp = float(spearmanr(j, m_ad[el]).statistic)
        if not np.isfinite(rp):
            gfail(f"G6 FAIL: placebo col {mc} rho non-finite")
        rows_b.append(dict(col=int(mc), minority=AA[r_i], frac_min=f_r,
                           dominant=AA[d_i], frac_dom=f_d,
                           n_min=len(g1), n_dom=len(g2),
                           n_eligible=int(el.sum()), rho_placebo=rp))
        log(f"  col {mc:3d}: minority {AA[r_i]} {f_r:.4%} ({len(g1)}) vs "
            f"dominant {AA[d_i]} {f_d:.4%} ({len(g2)}); eligible "
            f"{int(el.sum())} -> rho = {rp:+.6f}")
    if not rows_b:
        gfail("G6 FAIL: no placebo produced a scoreable rho")
    rp_max = max(r["rho_placebo"] for r in rows_b)
    n_ge = sum(1 for r in rows_b if r["rho_placebo"] >= rho_obs)
    log(f"  placebo rhos: n={len(rows_b)}, max={rp_max:+.6f}, "
        f"min={min(r['rho_placebo'] for r in rows_b):+.6f}; "
        f"{n_ge}/{len(rows_b)} >= actual ({rho_obs:+.6f})")

    # paired position bootstrap of actual - strongest placebo
    strong = max(rows_b, key=lambda r: r["rho_placebo"])
    smc = strong["col"]
    g1 = np.flatnonzero(mat[:, smc] == ord(strong["minority"]))
    g2 = np.flatnonzero(mat[:, smc] == ord(strong["dominant"]))
    cgs1, cgs2 = counts_for(mat, g1, cand_cols), counts_for(mat, g2,
                                                            cand_cols)
    el_s = (cgs1.sum(1) >= FLOOR_POS) & (cgs2.sum(1) >= FLOOR_POS)
    jsd_s = np.full(len(cand_cols), np.nan)      # candidate-space, NaN off
    jsd_s[el_s] = jsd_rows(cgs1[el_s], cgs2[el_s])   # the placebo's own
    # eligible-set rho above is unchanged; candidate space only makes the
    # SHARED-position pairing indexable against jsd_vec
    shared = np.flatnonzero(el83 & el_s)
    if shared.size < FLOOR_ELIG:
        gfail(f"G6 FAIL: shared eligible positions {shared.size} < "
              f"{FLOOR_ELIG} for the paired comparison")
    jsd_a_sh, m_sh = jsd_vec[shared], m_ad[shared]
    jsd_p_sh = jsd_s[shared]

    def two_rhos(idx):
        return (float(spearmanr(jsd_a_sh[idx], m_sh[idx]).statistic),
                float(spearmanr(jsd_p_sh[idx], m_sh[idx]).statistic))

    pt_a, pt_p = two_rhos(np.arange(shared.size))
    rg = np.random.default_rng(SEED)
    diffs = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rg.integers(0, shared.size, shared.size)
        a, p_ = two_rhos(idx)
        diffs[b] = a - p_
    if not np.isfinite(diffs).all():
        gfail(f"G6 FAIL: {(~np.isfinite(diffs)).sum()} non-finite "
              f"paired-bootstrap draws")
    d_lo, d_hi = np.percentile(diffs, [2.5, 97.5])
    p_exc = (1 + int((diffs <= 0).sum())) / (1 + N_BOOT)
    log(f"  PAIRED comparison on {shared.size} shared positions "
        f"(actual rho {pt_a:+.6f} vs strongest placebo col {smc} "
        f"rho {pt_p:+.6f} on shared):")
    log(f"    diff = {pt_a - pt_p:+.6f} CI [{d_lo:+.6f}, {d_hi:+.6f}] "
        f"p_exceeds = {p_exc:.4f}  (N_BOOT={N_BOOT}, seed 0)")
    if rho_obs <= rp_max:
        b3b_v = "WITHIN PLACEBO RANGE -> generic"
        b3b_specific = False
    elif d_lo > 0:
        b3b_v = "EXCEEDS ALL PLACEBOS -> 222-specific excess"
        b3b_specific = True
    else:
        b3b_v = "point-excess only, difference NOT established"
        b3b_specific = False
    log(f"  B3b VERDICT (script-29 reading, frozen): {b3b_v}")

    # ==================================================================
    # B3c — frozen conditional
    # ==================================================================
    log("\n" + "=" * 74)
    log("B3c  HONEST VERDICT (conditional fixed in docstring)")
    log("=" * 74)
    generic = (not b3a_exceeds) and (not b3b_specific)
    specific = b3a_exceeds and b3b_specific
    if generic:
        log("  BOTH controls indicate genericness -> RESTATED as the "
            "task requires:")
        log("  \"ESM-2's background-shift is larger at positions with "
            "more sequence heterogeneity in general,\" — not as "
            "anything specific to A222V's biology or clade structure.")
    elif specific:
        log("  BOTH controls show specificity: the actual V-group "
            "exceeds the size-matched null AND the strongest placebo. "
            "AE3's candidate explanation stands — with its standing "
            "caveats restated: observational not causal, grouping-by-222 "
            "is an operationalization (no phylogeny), and AD6's region-4 "
            "depth reversal limits any single unifying story.")
    else:
        log(f"  MIXED: B3a "
            f"{'exceeds' if b3a_exceeds else 'does not exceed'} the "
            f"size-matched null (p={p_null:.4f}); B3b -> {b3b_v}. "
            f"The two controls disagree; the restate-the-candidate "
            f"conditional does NOT fire (it requires both).")

    # ---- save ----
    srows = [dict(section="B3a", key="observed_rho", value=rho_obs),
             dict(section="B3a", key="null_mean", value=nmean),
             dict(section="B3a", key="null_sd", value=nsd),
             dict(section="B3a", key="null_p2.5", value=q025),
             dict(section="B3a", key="null_median", value=q50),
             dict(section="B3a", key="null_p97.5", value=q975),
             dict(section="B3a", key="p_one_sided", value=p_null),
             dict(section="B3a", key="n_draws_finite", value=int(fin.size)),
             dict(section="B3a", key="n_ge_observed", value=ge)]
    for r in rows_b:
        srows.append(dict(section="B3b", key=f"placebo_col{r['col']}",
                          value=r["rho_placebo"]))
    srows.append(dict(section="B3b", key="strongest_placebo_rho",
                      value=rp_max))
    srows.append(dict(section="B3b", key="paired_diff_ci_lo",
                      value=float(d_lo)))
    srows.append(dict(section="B3b", key="paired_diff_ci_hi",
                      value=float(d_hi)))
    srows.append(dict(section="B3b", key="paired_p_exceeds", value=p_exc))
    pd.DataFrame(srows).to_csv(OUT, index=False)
    log(f"\n[saved] {OUT}")
    log("\nLIMITATIONS: B3a's null controls GROUP COMPOSITION at fixed "
        "sizes, not MSA phylogenetic non-independence; all placebos "
        "share one alignment (columns not independent) — the comparison "
        "is script 29's convention adapted, not an independent "
        "replication; rho^2 ~1.2% of rank variance (small regardless of "
        "branch); rarity window and K_MAX frozen before any placebo rho "
        "existed; effect sizes printed with every p (AGENTS s3).")
    log(f"[done] {time.time() - T0:.1f}s")
    log("SCRIPT 95 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
