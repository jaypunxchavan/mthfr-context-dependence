"""
Script 63 (I1 follow-up, tasks M1a-M1e): does ESM-2's context-shift
strength scale with how damaging it rates the background mutation?

WHY (mechanism hypothesis H1a from the task doc)
-------------------------------------------------
S2 says the atlas calls A222V strongly deleterious; H1a says ESM-2 itself
rates A222V near-neutral. If a background mutation doesn't register as
damaging to the model, the model has little reason to propagate a
correction from it elsewhere -> weak/backward delta_ESM. This script tests
that mechanism directly: pick backgrounds spanning ESM-2's OWN severity
rating, rescore a fixed position subset in each, and ask whether
mean |delta_ESM_b| tracks S(b|WT) and whether A222V sits OUTLIER-LOW on
that relationship.

STAGES (env M1_STAGE, so M1a gets its own actual run before any scoring)
------------------------------------------------------------------------
  M1_STAGE=select  -> M1a only: select backgrounds from the on-disk WT
                      table (no model, no new scoring), write the
                      selection CSV, exit.
  default (run)    -> M1a..M1e in one run: selection, timed rescoring
                      (M1b), delta summaries (M1c), relationship +
                      A222V outlier test (M1d), position-cluster
                      bootstrap CIs (M1e).

PRE-REGISTERED RULES (fixed before any run; AGENTS 6)
-----------------------------------------------------
M1a selection (deterministic, no randomness):
  * Candidates = data/processed/esm2_wt_scores.csv rows (script 10's
    single-mutant WT table), position != 222, region from
    scripts/lib/regions.py REGION_BOUNDS (R1 2-147, R2 148-294,
    R3 295-474, R4 475-656) -> spread across the protein "like the
    existing region checks".
  * Per region pick TWO backgrounds: the most damaging substitution in
    that region (min esm2_score; more negative = more damaging) and the
    least damaging (max esm2_score; near-neutral, like A222V) => 8
    backgrounds. Sort key (esm2_score, position, mut_aa) makes ties
    deterministic; if both extremes fall at one position, the least-
    damaging pick moves to the next-highest score at a DIFFERENT
    position. Regions are disjoint -> all 8 positions distinct, none is
    222. No atlas-measurability filter (any substitution is constructible
    as a background; disclosed here as an assumption).
M1b subset (identical for every background, incl. A222V's arm):
  * size M1_N_SUB (default 120, within the task's ~100-150), drawn with
    default_rng(M1_SEED=0) without replacement from the 655 table
    positions MINUS {222} U {the 8 background positions} (a background's
    own position is not a target; excluding 9 positions keeps hgvs_pro
    naming unambiguous, same reason script 11 scored pos 222 separately).
  * Scoring reuses scripts/lib/esm_scoring.get_position_logprobs and
    scripts/lib/sequence.load_sequence exactly as scripts 10/11 -- no new
    scoring logic. One forward pass per (background, position).
  * TIMING RULE (task runtime note + AGENTS 1): time the FIRST
    background; if t1 > 180 s, REDUCE n_sub to
    max(60, round(n_sub * 180 / t1)), re-draw the subset (same seed,
    new size), rescore from scratch, and print a REDUCTION block for the
    log. At most ONE reduction is attempted; if a rescore is still
    > 180 s the run proceeds at floor size and flags it (no loop).
    If t1 <= 180 s, no reduction (projection printed either way).
  * Cache: raw scores -> data/processed/task63_m1_bg_raw.csv; reused
    verbatim on a later run iff it matches the current spec exactly
    (8 backgrounds x subset positions x 19 subs). Model scoring is
    deterministic (eval mode, no dropout), so cache reuse is exact --
    this exists only so the N_BOOT smoke -> full protocol does not
    re-pay the model cost.
M1c (same delta definition as script 12, byte-for-byte semantics):
  delta_ESM_b(v) = S(v|b) - S(v|WT), merged on hgvs_pro (built with the
  WT table's wt_aa at each target position -- target positions are never
  background positions, so the WT letter is identical in every
  background); the summary statistic per background is
  mean |delta_ESM_b| over subset x 19 substitutions.
  A222V's arm comes from the EXISTING data/processed/merged_wt_a222v_
  scores.csv (script 12's own output, delta_esm column, join column
  position_wt) restricted to the same subset -- no rescoring of A222V.
M1d verdict (task wording taken literally, ambiguity resolved toward the
task's own phrasing and logged): fit OLS mean|delta| ~ S on the 8 NEW
backgrounds only, predict A222V, residual r = observed - predicted.
  * r's 95% CI (position-cluster bootstrap, cluster = subset position,
    same resampled indices for all 9 backgrounds) entirely < 0
      -> SUPPORTS H1a: A222V is outlier-LOW (unusually little shift
         GIVEN its severity rating).
  * CI entirely > 0 -> CONTRARY: outlier-HIGH.
  * CI contains 0   -> NOT SUPPORTED: A222V sits within trend -> per the
         task, the weak signal needs a different explanation.
  Descriptive companions printed regardless: A222V's absolute rank of
  mean|delta| among the 9, and whether it is the lowest of the 9.
  NOTE (disclosed): "outlier-LOW" here means BELOW THE TREND, not merely
  lowest-in-absolute-terms -- if A222V happens to have the most favorable
  S of the nine, the trend already predicts a low value for it; only an
  unusually low residual is evidence beyond the generic severity->shift
  relationship. Both numbers are printed so either reading can be checked.
M1e (primary = Spearman rho across the 9 backgrounds, project convention;
  Pearson reported alongside): 95% position-cluster bootstrap CI,
  cluster = subset position (resample the n_sub positions with
  replacement, SAME indices for all 9 backgrounds so the pairing
  survives; recompute each background's mean|delta| from its per-position
  mean-abs-delta vector, then recompute the correlation). Direction
  expected under H1a's severity->shift story: NEGATIVE (more damaging =
  lower S = larger shift). N_BOOT env (default 2000; 200-500 for smoke).

SANITY GATES (sys.exit(1); AGENTS 4/5)
---------------------------------------
(g1) S(A222V|WT) from the table must equal -5.200276 +/- 1e-5 -- the value
     H1a itself reported (OVERNIGHT_LOG H1a entry: "S(A222V|WT) =
     -5.200276 sits inside (p10=-12.80, p90=-1.19); 68.0% of all 12,445
     substitutions are at least as deleterious"; repeated in the run
     summary as "-5.200276, z=+0.502"). This run FAILED g1 on its first
     execution because the constant was initially encoded as +1.840757 --
     a misattribution: 1.840757 is p.Val2Ala (position 2, the WT table's
     first data row) and its companion 1.851107 / delta 0.010351 is the
     merged file's row-2 delta-sign check, neither is A222V's severity.
     The gate caught the misattribution (that is what it is for); the
     constant was corrected to the independently verified -5.200276
     (corroborated in TWO prior log entries + this script reproduces the
     68.0% percentile), and ONLY the constant/docstring changed -- the
     selection rule, subset rule, and M1d/M1e verdict rules were untouched,
     no scoring had started (M1a stage only). Disclosed per AGENTS 6/7.
(g2) subset disjoint from {222} U bg positions; |subset| == n_sub (after
     any reduction redraw); the 8 background positions pairwise distinct
     and none is 222; every background's WT letter in data/raw/P42898.fasta
     matches the table's wt_aa (catches numbering mismatch before scoring).
(g3) every background's merged delta table has exactly n_sub*19 rows and
     every hgvs_pro resolves (no silent row loss, AGENTS 5).
(g4) A222V's restricted arm has exactly n_sub*19 rows.
(g5) bootstrap: all stored draws finite, actual draw count == N_BOOT,
     percentile CI ordered, and each primary point estimate lies inside
     its own CI (if the point estimate falls outside its own bootstrap
     CI the resampling is broken -> fail, do not raise N).
(g6) timing: if the reduction rule fires it must print the REDUCTION
     block AND shrink n_sub; projection printed either way.

LIMITATIONS (printed by the script too, AGENTS 6)
--------------------------------------------------
  - n = 9 backgrounds (8 selected extremes + A222V). The bootstrap CIs
    resample POSITIONS, so they quantify mean|delta|-estimation error at
    fixed backgrounds; they do NOT include background-sampling
    variability. Treat the correlation as descriptive across deliberately
    chosen extremes (range-restricted design), not a population estimate.
  - The 8 backgrounds are selected ON the severity axis (min/max per
    region), which maximizes leverage for the trend test by construction;
    the A222V residual test is unaffected by that selection because the
    fit is on the 8 and A222V is held out of it.
  - A222V's arm is pre-existing data from script 12 (same code path, not
    re-run) -- so M1d compares like with like only insofar as script 11's
    scoring used identical settings; it did (same model, same function).
  - delta here is a MODEL-internal quantity (log-odds shifts), not
    fitness epistasis; nothing in this script measures real epistasis.

Output files (results -> data/processed/):
  task63_m1_selection.csv   (M1a selection, both stages)
  task63_m1_bg_raw.csv      (scoring cache)
  task63_m1_backgrounds.csv (9-row final table + verdict scalars)
  task63_m1_bootstrap.csv   (CI summary + residual CI)
Env: M1_STAGE (select|run), N_BOOT (2000), M1_N_SUB (120), M1_SEED (0).
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
WT_CSV = ROOT / "data" / "processed" / "esm2_wt_scores.csv"
A222V_MERGED = ROOT / "data" / "processed" / "merged_wt_a222v_scores.csv"
FASTA = ROOT / "data" / "raw" / "P42898.fasta"
SEL_CSV = ROOT / "data" / "processed" / "task63_m1_selection.csv"
RAW_CACHE = ROOT / "data" / "processed" / "task63_m1_bg_raw.csv"
BG_CSV = ROOT / "data" / "processed" / "task63_m1_backgrounds.csv"
BOOT_CSV = ROOT / "data" / "processed" / "task63_m1_bootstrap.csv"

STAGE = os.environ.get("M1_STAGE", "run").strip().lower()
N_BOOT = int(os.environ.get("N_BOOT", "2000"))
N_SUB = int(os.environ.get("M1_N_SUB", "120"))
SEED = int(os.environ.get("M1_SEED", "0"))
S_A222V_KNOWN = -5.200276  # H1a's reported value, see g1 (+ first-run
                            # misattribution of 1.840757 disclosed in g1)
T1_REDUCE_S = 180.0        # timing rule: >3 min for one background -> reduce


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def label_of(region, wt_aa, position, mut_aa):
    """Single source of truth for background ids (used by selection,
    scoring, and the summary table -- must never diverge)."""
    return f"R{int(region)}_{wt_aa}{int(position)}{mut_aa}"


def select_backgrounds(wt):
    """M1a rule: min & max esm2_score per region, pos != 222, deterministic
    ties, all positions distinct. Returns DataFrame of 8 rows."""
    from scripts.lib.regions import assign_region

    cand = wt[wt["position"] != 222].copy()
    cand["region"] = assign_region(cand["position"])
    if cand["region"].isna().any():
        fail("positions outside REGION_BOUNDS present in WT table")
    rows = []
    for r in (1, 2, 3, 4):
        sub = cand[cand["region"] == r].sort_values(
            ["esm2_score", "position", "mut_aa"], kind="mergesort")
        mn = sub.iloc[0]
        desc = sub.iloc[::-1]  # descending score; ties keep sorted order
        mx = None
        for i in range(len(desc)):
            if desc.iloc[i]["position"] != mn["position"]:
                mx = desc.iloc[i]
                break
        if mx is None:
            fail(f"region {r} has no second position for least-damaging pick")
        for tag, row in (("most_damaging", mn), ("least_damaging", mx)):
            rows.append(dict(region=r, pick=tag,
                             position=int(row["position"]),
                             wt_aa=row["wt_aa"], mut_aa=row["mut_aa"],
                             hgvs_pro=row["hgvs_pro"],
                             esm2_score=float(row["esm2_score"])))
    bg = pd.DataFrame(rows)
    bg["bg_id"] = [label_of(r.region, r.wt_aa, r.position, r.mut_aa)
                   for r in bg.itertuples()]
    if bg["position"].nunique() != 8 or (bg["position"] == 222).any():
        fail(f"selection positions not 8 distinct non-222: "
             f"{sorted(bg['position'])}")
    if bg["bg_id"].nunique() != 8:
        fail(f"background labels not unique: {list(bg['bg_id'])}")
    return bg


def print_selection(bg, wt):
    print("=== M1a: selected backgrounds (rule: min/max esm2_score per "
          "region, pos!=222, deterministic ties) ===")
    s222 = float(wt[(wt["position"] == 222) & (wt["mut_aa"] == "V")]
                 ["esm2_score"].iloc[0])
    for _, r in bg.iterrows():
        print(f"  R{r['region']} {r['pick']:14s} pos {r['position']:3d} "
              f"{r['wt_aa']}>{r['mut_aa']}  {r['hgvs_pro']:16s} "
              f"S(b|WT)={r['esm2_score']:+.6f}")
    print(f"  (reference)   pos 222 A>V   p.Ala222Val        "
          f"S(b|WT)={s222:+.6f}  <- A222V arm uses existing script-12 data")
    lo, hi = bg["esm2_score"].min(), bg["esm2_score"].max()
    print(f"severity span of the 8: [{lo:+.6f}, {hi:+.6f}] ; A222V "
          f"{s222:+.6f} sits {'INSIDE' if lo <= s222 <= hi else 'OUTSIDE'} "
          f"that span")


def draw_subset(wt_positions, bg_positions, n_sub, seed):
    excl = set(int(p) for p in bg_positions) | {222}
    pool = np.array(sorted(set(int(p) for p in wt_positions) - excl))
    if len(pool) < n_sub:
        fail(f"pool {len(pool)} < n_sub {n_sub}")
    rng = np.random.default_rng(seed)
    return sorted(int(x) for x in rng.choice(pool, size=n_sub,
                                              replace=False))


def check_subset(subset, bg_positions, n_sub):
    excl = set(int(p) for p in bg_positions) | {222}
    if set(subset) & excl:
        fail(f"(g2) subset overlaps exclusions: "
             f"{sorted(set(subset) & excl)}")
    if len(subset) != n_sub or len(set(subset)) != n_sub:
        fail(f"(g2) subset size {len(subset)} != n_sub {n_sub} "
             f"(or duplicates)")
    print(f"(g2) subset OK: n_sub={n_sub}, seed={SEED}, disjoint from "
          f"{{222}} U {{8 bg positions}} -- OK")


def score_backgrounds(bg, wt_seq, subset):
    """M1b: one forward pass per (background, position), timed.
    Returns (DataFrame, t1_seconds_for_first_background).
    Reuses scripts/lib/esm_scoring.get_position_logprobs unchanged."""
    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    device = get_device()
    print(f"Using device: {device}")
    print("Loading ESM-2 650M...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    rows = []
    t_start_all = time.time()
    t1 = None
    n_bg = len(bg)
    for i, r in enumerate(bg.itertuples()):
        bid = r.bg_id
        seq = wt_seq[:int(r.position) - 1] + r.mut_aa + \
            wt_seq[int(r.position):]
        t0 = time.time()
        for p in subset:
            scores = get_position_logprobs(model, alphabet, batch_converter,
                                           seq, p, device)
            for m, sc in scores.items():
                # hgvs_pro placeholder: main() rebuilds it from the WT
                # table's wt_aa (target positions are never background
                # positions, so the WT letter is the same in every bg)
                rows.append(dict(bg_id=bid, position=p, mut_aa=m,
                                 hgvs_pro=None, score_bg=sc))
        t1 = time.time() - t0
        print(f"M1b timed: background {i + 1}/{n_bg} {bid} -> {t1:.1f} s "
              f"for {len(subset)} positions "
              f"({t1 / len(subset) * 1000:.0f} ms/pass); "
              f"projected total for {n_bg} = {t1 * n_bg:.1f} s")
        if i == 0:
            if t1 > T1_REDUCE_S:
                print(f"(g6) t1={t1:.1f}s > {T1_REDUCE_S}s -> reduction "
                      f"rule fires (handled by caller)")
            else:
                print(f"(g6) timing rule: t1={t1:.1f}s <= {T1_REDUCE_S}s "
                      f"-> NO reduction (n_sub stays {len(subset)})")
    print(f"scoring wall time: {time.time() - t_start_all:.1f} s total")
    return pd.DataFrame(rows), t1


def main():
    global N_SUB
    from scripts.lib.sequence import load_sequence
    from scripts.lib.esm_scoring import hgvs_pro as build_hgvs

    wt = pd.read_csv(WT_CSV)
    if len(wt) != 12445 or wt["position"].nunique() != 655:
        fail(f"WT table shape unexpected: {len(wt)} rows, "
             f"{wt['position'].nunique()} positions")
    bg = select_backgrounds(wt)
    bg.to_csv(SEL_CSV, index=False)
    print_selection(bg, wt)

    s222 = float(wt[(wt["position"] == 222) & (wt["mut_aa"] == "V")]
                 ["esm2_score"].iloc[0])
    if abs(s222 - S_A222V_KNOWN) > 1e-5:
        fail(f"(g1) S(A222V|WT)={s222} != known {S_A222V_KNOWN}")
    print(f"(g1) S(A222V|WT) matches prior verified value "
          f"{S_A222V_KNOWN} -- OK")
    print(f"selection saved -> {SEL_CSV}")

    if STAGE == "select":
        print("\nM1_STAGE=select -> M1a done, exiting before any scoring.")
        return

    wt_seq = load_sequence(FASTA)
    if len(wt_seq) != 656:
        fail(f"sequence length {len(wt_seq)} != 656")
    for _, r in bg.iterrows():
        seq_aa = wt_seq[r["position"] - 1]
        if seq_aa != r["wt_aa"]:
            fail(f"(g2) pos {r['position']} fasta {seq_aa} != table "
                 f"{r['wt_aa']}")
    if wt_seq[221] != "A":
        fail("(g2) fasta position 222 is not Ala")
    print("(g2) fasta letters match table at all 8 background positions, "
          "222==A -- OK")

    wt_aa_by_pos = wt.drop_duplicates("position").set_index("position")[
        "wt_aa"].to_dict()

    subset = draw_subset(wt["position"].unique(), bg["position"], N_SUB,
                         SEED)
    check_subset(subset, bg["position"], N_SUB)

    # ---- M1b: score with cache + pre-registered reduction rule ----
    n_bg = len(bg)
    use_cache = False
    raw = None
    if RAW_CACHE.exists():
        raw = pd.read_csv(RAW_CACHE)
        ok = (
            set(raw.columns) == {"bg_id", "position", "mut_aa", "hgvs_pro",
                                 "score_bg"}
            and len(raw) == n_bg * N_SUB * 19
            and raw["bg_id"].nunique() == n_bg
            and sorted(raw["position"].unique()) == subset
            and (raw.groupby("bg_id").size() == N_SUB * 19).all()
        )
        if ok:
            use_cache = True
            print(f"CACHE REUSED: {RAW_CACHE} matches spec "
                  f"({n_bg} bgs x {N_SUB} x 19 = {len(raw)}) -- model not "
                  f"loaded (scoring is deterministic; cache exists so the "
                  f"smoke->full N_BOOT protocol is exact)")
        else:
            print("cache present but spec mismatch -> rescoring")
    if not use_cache:
        reduced = False
        while True:
            raw, t1 = score_backgrounds(bg, wt_seq, subset)
            if t1 > T1_REDUCE_S and not reduced:
                new_n = max(60, int(round(N_SUB * T1_REDUCE_S / t1)))
                print(f"REDUCTION APPLIED (g6): t1={t1:.1f}s > "
                      f"{T1_REDUCE_S}s -> n_sub {N_SUB} -> {new_n}; "
                      f"re-drawing subset (same seed) and restarting "
                      f"scoring (one reduction attempt only)")
                N_SUB = new_n
                subset = draw_subset(wt["position"].unique(),
                                     bg["position"], N_SUB, SEED)
                check_subset(subset, bg["position"], N_SUB)
                reduced = True
                continue
            if t1 > T1_REDUCE_S and reduced:
                print(f"REDUCTION FLOOR FLAG: still {t1:.1f}s > "
                      f"{T1_REDUCE_S}s at n_sub={N_SUB}; proceeding and "
                      f"flagging for the log (no second reduction, per "
                      f"pre-registered rule)")
            break
        # (g3) hgvs built with WT letters, must resolve in the WT table
        wt_index = set(wt["hgvs_pro"])
        raw["hgvs_pro"] = [
            build_hgvs(wt_aa_by_pos[p], int(p), m)
            for p, m in zip(raw["position"], raw["mut_aa"])
        ]
        if not raw["hgvs_pro"].isin(wt_index).all():
            bad = raw.loc[~raw["hgvs_pro"].isin(wt_index)].iloc[0]
            fail(f"(g3) unresolved hgvs_pro: {bad['hgvs_pro']} "
                 f"(pos {bad['position']} {bad['mut_aa']})")
        raw.to_csv(RAW_CACHE, index=False)
        print(f"scoring cache saved -> {RAW_CACHE}")

    # ---- M1c: delta summaries (definition identical to script 12) ----
    wt_lookup = wt.set_index("hgvs_pro")["esm2_score"]
    per_pos, means = {}, {}
    for bid, g in raw.groupby("bg_id"):
        g = g.copy()
        if len(g) != N_SUB * 19 or g["hgvs_pro"].isna().any():
            fail(f"(g3) {bid}: {len(g)} rows (expect {N_SUB * 19})")
        if not g["hgvs_pro"].isin(wt_lookup.index).all():
            miss = g.loc[~g["hgvs_pro"].isin(wt_lookup.index), "hgvs_pro"]
            fail(f"(g3) {bid}: {len(miss)} hgvs_pro not in WT table, "
                 f"e.g. {miss.iloc[0]}")
        g["score_wt"] = g["hgvs_pro"].map(wt_lookup)
        g["absdelta"] = (g["score_bg"] - g["score_wt"]).abs()
        pv = g.groupby("position")["absdelta"].mean().reindex(subset)
        if pv.isna().any():
            fail(f"(g3) {bid}: {int(pv.isna().sum())} subset positions "
                 f"missing from groupby")
        per_pos[bid] = pv.to_numpy()
        means[bid] = float(g["absdelta"].mean())
        print(f"M1c {bid:16s} mean|delta_ESM_b| = {means[bid]:.8f} "
              f"over {len(g)} values ({N_SUB} pos x 19)")

    merged = pd.read_csv(A222V_MERGED)
    a222v = merged[merged["position_wt"].isin(subset)]
    if len(a222v) != N_SUB * 19 or a222v["delta_esm"].isna().any():
        fail(f"(g4) A222V arm {len(a222v)} rows (expect {N_SUB * 19})")
    pv = a222v.assign(absd=a222v["delta_esm"].abs()).groupby(
        "position_wt")["absd"].mean().reindex(subset)
    if pv.isna().any():
        fail(f"(g4) A222V arm missing {int(pv.isna().sum())} positions")
    per_pos["A222V"] = pv.to_numpy()
    means["A222V"] = float(a222v["delta_esm"].abs().mean())
    print(f"M1c {'A222V':16s} mean|delta_ESM_b| = {means['A222V']:.8f} "
          f"over {len(a222v)} values ({N_SUB} pos x 19) [existing "
          f"script-12 data, not rescored]")

    # ---- assemble the 9-row table, sorted by severity ----
    labels = list(bg["bg_id"])
    s_map = {lab: float(s) for lab, s in zip(labels, bg["esm2_score"])}
    pos_map = {lab: int(p) for lab, p in zip(labels, bg["position"])}
    s_map["A222V"] = s222
    pos_map["A222V"] = 222
    order = sorted(s_map, key=lambda k: s_map[k])
    if set(order) != set(labels) | {"A222V"} or len(order) != 9:
        fail(f"table assembly wrong: {order}")
    tab = pd.DataFrame([dict(bg_id=lab, position=pos_map[lab],
                             S_b_given_WT=s_map[lab],
                             mean_abs_delta=means[lab]) for lab in order])

    # ---- M1d: OLS on the 8 new only, predict A222V ----
    X = np.column_stack([np.ones(len(labels)),
                         [s_map[i] for i in labels]])
    y8 = np.array([means[i] for i in labels])
    beta, *_ = np.linalg.lstsq(X, y8, rcond=None)
    pred = beta[0] + beta[1] * s222
    r_obs = means["A222V"] - pred
    resid8 = y8 - X @ beta

    # ---- M1e + M1d CI: position-cluster bootstrap ----
    M = np.vstack([per_pos[lab] for lab in order])   # 9 x n_sub
    s_vec = np.array([s_map[lab] for lab in order])
    idx_new = [order.index(i) for i in labels]
    i_a222v = order.index("A222V")

    def corr(y, method):
        if method == "spearman":
            return float(stats.spearmanr(s_vec, y).statistic)
        return float(stats.pearsonr(s_vec, y)[0])

    y_tab = tab["mean_abs_delta"].to_numpy()
    rho_sp = corr(y_tab, "spearman")
    rho_pe = corr(y_tab, "pearson")

    rng = np.random.default_rng(SEED + 1)
    sp_d = np.empty(N_BOOT)
    pe_d = np.empty(N_BOOT)
    r_d = np.empty(N_BOOT)
    for b in range(N_BOOT):
        idx = rng.integers(0, N_SUB, N_SUB)   # cluster = subset position
        y_star = M[:, idx].mean(axis=1)
        sp_d[b] = corr(y_star, "spearman")
        pe_d[b] = corr(y_star, "pearson")
        bs, *_ = np.linalg.lstsq(X, y_star[idx_new], rcond=None)
        r_d[b] = y_star[i_a222v] - (bs[0] + bs[1] * s222)
    if not (np.isfinite(sp_d).all() and np.isfinite(pe_d).all()
            and np.isfinite(r_d).all()):
        fail("(g5) non-finite bootstrap draws present")
    if len(sp_d) != N_BOOT:
        fail(f"(g5) {len(sp_d)} draws != N_BOOT {N_BOOT}")

    def ci(x, obs, name):
        lo, hi = np.percentile(x, [2.5, 97.5])
        if not (lo <= obs <= hi):
            fail(f"(g5) {name}: point {obs:.6f} outside own CI "
                 f"[{lo:.6f}, {hi:.6f}] -- resampling broken")
        return float(lo), float(hi)

    sp_ci = ci(sp_d, rho_sp, "spearman")
    pe_ci = ci(pe_d, rho_pe, "pearson")
    r_ci = ci(r_d, r_obs, "a222v_residual")
    print(f"(g5) bootstrap OK: {N_BOOT} position-cluster draws, all "
          f"finite, point estimates inside own CIs")

    # ---- report ----
    print("\n=== M1d: mean|delta_ESM_b| vs S(b|WT), sorted by severity ===")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.8f}"))
    print(f"\nOLS on the 8 new backgrounds: mean|delta| = {beta[0]:.6f} "
          f"+ ({beta[1]:.6f}) * S(b|WT)   [resid RMS on the 8 = "
          f"{np.sqrt((resid8 ** 2).mean()):.8f}]")
    print(f"A222V: observed {means['A222V']:.8f}, predicted {pred:.8f}, "
          f"residual r = {r_obs:+.8f}")
    print(f"residual 95% position-cluster CI = [{r_ci[0]:+.8f}, "
          f"{r_ci[1]:+.8f}]  (N_BOOT={N_BOOT}, cluster=subset position)")
    rank = int((tab["mean_abs_delta"] < means["A222V"]).sum() + 1)
    print(f"A222V absolute rank of mean|delta| among the 9: {rank} "
          f"(1 = lowest); lowest-of-nine = {rank == 1}")
    if r_ci[1] < 0:
        verdict = ("SUPPORTS H1a: A222V sits outlier-LOW -- below the trend "
                   "the other 8 define, residual CI excludes 0 (unusually "
                   "little context-shift GIVEN how damaging ESM-2 rates it)")
    elif r_ci[0] > 0:
        verdict = ("CONTRARY to H1a: A222V sits outlier-HIGH -- residual CI "
                   "excludes 0 from above")
    else:
        verdict = ("NOT SUPPORTED: A222V sits within the trend (residual CI "
                   "contains 0) -> per the task's wording the weak signal "
                   "needs a different explanation; if it is nevertheless "
                   "lowest in absolute terms (printed above) that is "
                   "severity-EXPLAINED, not outlier-LOW")
    print(f"M1d VERDICT (pre-registered): {verdict}")

    print("\n=== M1e: correlation across the 9 backgrounds ===")
    print(f"Spearman rho = {rho_sp:+.6f}  95% cluster CI "
          f"[{sp_ci[0]:+.6f}, {sp_ci[1]:+.6f}]  [PRIMARY]")
    print(f"Pearson  r   = {rho_pe:+.6f}  95% cluster CI "
          f"[{pe_ci[0]:+.6f}, {pe_ci[1]:+.6f}]")
    dirn = "negative" if rho_sp < 0 else "positive"
    consistent = "consistent" if rho_sp < 0 else "INCONSISTENT"
    excl0 = (sp_ci[1] < 0 or sp_ci[0] > 0)
    print(f"H1a expected direction: NEGATIVE (more damaging = lower S = "
          f"larger shift); observed sign = {dirn} -> {consistent} with the "
          f"severity->shift story in sign "
          f"({'CI excludes 0' if excl0 else 'CI contains 0'})")

    print("\nLIMITATIONS (printed by the script, AGENTS 6):")
    print("  - n=9 deliberately selected backgrounds (extremes per region);")
    print("    bootstrap resamples POSITIONS, so CIs cover mean|delta|")
    print("    estimation error at fixed backgrounds, NOT background-")
    print("    sampling variability. Correlation is descriptive.")
    print("  - delta is a MODEL-internal log-odds shift, not fitness")
    print("    epistasis; nothing here measures real epistasis.")
    print("  - A222V arm reuses script 12's existing merged file (same")
    print("    model/function, not rescored) -- like-for-like by code path.")

    # ---- save ----
    tab["verdict_m1d"] = verdict
    tab["residual_a222v"] = r_obs
    tab["resid_ci_lo"] = r_ci[0]
    tab["resid_ci_hi"] = r_ci[1]
    tab["spearman_rho"] = rho_sp
    tab["spearman_lo"] = sp_ci[0]
    tab["spearman_hi"] = sp_ci[1]
    tab["pearson_r"] = rho_pe
    tab["pearson_lo"] = pe_ci[0]
    tab["pearson_hi"] = pe_ci[1]
    tab["n_boot"] = N_BOOT
    tab["n_sub"] = N_SUB
    tab.to_csv(BG_CSV, index=False)
    pd.DataFrame([
        dict(stat="spearman_rho", point=rho_sp, lo=sp_ci[0], hi=sp_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="pearson_r", point=rho_pe, lo=pe_ci[0], hi=pe_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_residual", point=r_obs, lo=r_ci[0], hi=r_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="ols_slope_on8", point=float(beta[1]), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_predicted", point=float(pred), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_observed", point=means["A222V"], lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="resid8_rms",
             point=float(np.sqrt((resid8 ** 2).mean())), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
    ]).to_csv(BOOT_CSV, index=False)
    print(f"\nSaved: {BG_CSV}\nSaved: {BOOT_CSV}")


if __name__ == "__main__":
    main()
