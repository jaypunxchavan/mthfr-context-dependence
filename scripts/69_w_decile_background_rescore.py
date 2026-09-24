"""
Script 69 (tasks W1-W4): decile-based background design for the M1
context-shift test -- fixes the bimodal-design limitation M1a/M1e flagged.

WHY (task doc Group W)
-------------------------------------------------
Script 63's M1a picked min/max esm2_score PER REGION => 8 backgrounds in
two severity clusters plus interpolated A222V; M1e's n=9 correlation
therefore rested on a bimodal design. W1 replaces that rule with a
DECILE-stratified one spanning ESM-2's FULL severity range; W2 rescoring
is time-budgeted; W3 re-runs the M1d/M1e tests; W4 reports old vs new.

STAGES (env W_STAGE, so W1 gets its own actual run before any scoring)
------------------------------------------------------------------------
  W_STAGE=select  -> W1 only: selection from the on-disk WT table (no
                     model, no scoring), write the selection CSV, exit.
  default (run)   -> W1..W4 in one run: selection, timed rescoring (W2),
                     delta summaries + M1d/M1e re-runs (W3), side-by-
                     side vs the original 9-point result (W4).

PRE-REGISTERED RULES (fixed in this docstring before ANY run; AGENTS 6)
------------------------------------------------------------------------
W1 selection (deterministic, no randomness anywhere):
  * Distribution for deciles = the `esm2_score` column of
    data/processed/esm2_wt_scores.csv, ALL 12,445 rows (literal reading
    of "deciles of esm2_wt_scores.csv's score distribution"; the 19
    position-222 rows are part of the distribution but not of the
    candidate pool).  Edges = np.quantile(scores, [0.1..0.9]) (numpy
    default linear interpolation).  Bin of a row = searchsorted(edges,
    score, 'right'), so bin 1 = [min, p10) ... bin 10 = [p90, max]:
    the ten bins jointly cover the FULL severity range.
  * Candidates = rows with position != 222 AND position NOT in the
    ORIGINAL M1 subset (the 120 positions actually scored in
    task63_m1_bg_raw.csv).  DESIGN-A ASSUMPTION, disclosed: W2 says to
    rescore "the same ~100-150-position subset used in the original M1
    (for comparability)"; keeping that subset BYTE-IDENTICAL while
    honoring script 63's rule that a background's own position is never
    a scoring target means excluding subset positions from the candidate
    pool rather than swapping subset positions.  This is the most
    conservative literal reading; it is logged as an assumption.
  * Within each bin: rows sorted by (esm2_score, position, mut_aa)
    ascending (mergesort = deterministic tie-break, same key as M1a),
    deduplicated to ONE row per position (first occurrence = that
    position's most damaging substitution inside the bin), then positions
    already chosen for an earlier bin are dropped.  Take THREE picks from
    the remaining list L: slot A = L[0] (bin's most damaging), slot B =
    L[len(L)//2] (middle), slot C = L[-1] (least damaging).  10 bins x 3
    slots = 30 backgrounds (task: "~20-30").  Gates: every bin yields
    >= 3 unused positions; all 30 positions distinct, none is 222, none
    in the subset.
W2 rescoring (time-budgeted; task budget 90 min):
  * Subset = the ORIGINAL M1 subset VERBATIM (read from
    task63_m1_bg_raw.csv's unique positions; original n_sub=120, seed 0,
    verified on disk).  The position subset is NEVER reduced (W2 says
    reduce the background COUNT, not the subset size).
  * Scoring = scripts/lib/esm_scoring.get_position_logprobs exactly as
    scripts 10/11/63 -- one forward pass per (background, position);
    model ESM-2 650M, eval mode, deterministic.
  * TIMING RULE: score the FIRST background (scoring order = bin then
    slot A/B/C, so first = bin1 slot A) and time it as t1; projection =
    t1 * 30.  Keep k = min(30, floor(5400 / t1)) backgrounds (5400 s =
    90 min budget, applied to scoring time -- the task's subject is
    rescoring).  Achieved by dropping from a PRE-REGISTERED drop order:
    slot C of bins 1..10 first, then slot B of bins 1..10; slot A (each
    decile's most damaging representative) is NEVER dropped, so at least
    one pick per decile survives as long as k >= 10.  If k < 10 the
    decile-spanning design would break AND the task forbids shrinking
    the subset -> BLOCKED with the actual t1 (no attempt is made).
    The projection and any REDUCTION block are always printed (g6).
  * Cache: raw scores -> task69_w2_bg_raw.csv, reused verbatim on a
    later run iff it matches the current spec (columns, subset, bg_ids
    all in this selection, >= 10 and <= 30 bgs, 120*19 rows each) --
    scoring is deterministic, so cache reuse is exact; this exists so
    the N_BOOT smoke -> full protocol does not re-pay the model cost.
W3 (methodology identical to script 63's M1d/M1e, re-run on the new set):
  * delta_ESM_b(v) = S(v|b) - S(v|WT) on hgvs_pro (WT letters from the
    WT table; target positions are never background positions);
    mean|delta_ESM_b| per background over 120 x 19 values.
    A222V's arm = existing merged_wt_a222v_scores.csv restricted to the
    same subset (script 12's data, NOT rescored) -- g4 exact row count.
  * M1d: OLS mean|delta| ~ S on the k NEW backgrounds only, predict
    A222V, residual r = observed - predicted; 95% position-cluster
    bootstrap CI (cluster = subset position, SAME resampled indices for
    all k+1 rows).  CI entirely < 0 -> SUPPORTS (outlier-LOW); > 0 ->
    CONTRARY (outlier-HIGH); contains 0 -> NOT SUPPORTED (within trend),
    same three-way wording as script 63.
  * M1e: Spearman rho across the k+1 backgrounds (PRIMARY, project
    convention) + Pearson, 95% position-cluster bootstrap CI; expected
    direction under H1a = NEGATIVE.
  * N_BOOT env, default 2000 (SAME as the original run so W4's CI
    comparison is like-for-like); 200-500 for smoke (AGENTS 1).
    Bootstrap rng = default_rng(W_SEED + 1), W_SEED default 0 (seed 1,
    same as script 63).
W4 side-by-side (reporting only; originals read from disk, not re-run):
  * Original numbers = task63_m1_bootstrap.csv (+ n/n_sub from
    task63_m1_backgrounds.csv).  The task doc quotes residual +0.00954
    CI [-0.00573,+0.02640], rho -0.467 CI [-0.583,-0.067]: the script
    prints disk values beside those quoted values with tolerance 5e-4
    (rounding) and flags CONTRADICTION (prints both) if outside --
    never silently prefers one (log rule).
  * Mechanical labels printed: M1d verdict changed or unchanged vs the
    original "NOT SUPPORTED"; M1e strengthens (same sign, CI excludes 0,
    larger |rho|) / weakens (CI contains 0, or same verdict but smaller
    |rho|, or sign flip flagged separately).  The PLAIN "changes /
    strengthens / weakens" sentence for the log is written from these
    printed numbers (AGENTS: report effect size alongside significance).

SANITY GATES (sys.exit(1); AGENTS 4/5)
---------------------------------------
(g0) inputs exist: task63_m1_bg_raw.csv, task63_m1_bootstrap.csv,
     task63_m1_backgrounds.csv, task63_m1_selection.csv,
     merged_wt_a222v_scores.csv, esm2_wt_scores.csv, P42898.fasta --
     exact path printed if missing (BLOCKED, never guessed).
(g1) S(A222V|WT) == -5.200276 +/- 1e-5 (same verified constant as
     script 63; carried over, not re-derived).
(g2) subset has exactly 120 positions == task63 n_sub, contains neither
     222 nor any of the original 8 background positions; selection: 30
     rows, distinct positions, none 222, none in subset, exactly 3 per
     decile bin; every selected position's FASTA letter == table wt_aa;
     FASTA position 222 == A.
(g3) every scored row's hgvs_pro resolves in the WT table; every
     background contributes exactly 120*19 rows (no silent row loss).
(g4) A222V's restricted arm has exactly 120*19 rows, no NaN delta.
(g5) bootstrap: all draws finite, count == N_BOOT, CIs ordered, each
     primary point estimate inside its own CI (fail -> do not raise N).
(g6) timing: projection always printed; if a reduction fires, the
     REDUCTION block prints and k < 30; kept backgrounds always >= 10
     and still cover all 10 decile bins (checked directly).

LIMITATIONS (printed by the script too, AGENTS 6)
--------------------------------------------------
  - Decile stratification REDUCES but does not eliminate severity-driven
    selection: picks are still chosen ON the severity axis (that is the
    design's point), just spread across all ten deciles instead of two
    regional extremes.  The correlation remains descriptive at fixed
    backgrounds; the position-cluster bootstrap covers mean|delta|
    estimation error, NOT background-sampling variability.
  - k+1 backgrounds (30 selected, fewer only if the pre-registered
    budget reduction fires) vs the original 9; W4 compares two DESIGNS
    (extremes-per-region vs decile-stratified) on the SAME subset --
    a design comparison, not an independent replication.
  - delta is a MODEL-internal log-odds shift, not fitness epistasis;
    nothing here measures real epistasis.
  - A222V's arm reuses script 12's merged file (same model/function
    code path, not rescored).
  - The 90-min budget is applied to scoring time; model load (~1 min)
    and analysis are extra but small (bootstrap runs on a k+1 x 120
    matrix).

Output files (results -> data/processed/):
  task69_w1_selection.csv  (W1: the 30 decile backgrounds, both stages)
  task69_w2_bg_raw.csv     (W2: scoring cache)
  task69_w3_backgrounds.csv (W3: k+1-row table + verdict scalars)
  task69_w3_bootstrap.csv  (W3/W4: CI summary incl. original comparison)
Env: W_STAGE (select|run), N_BOOT (2000), W_SEED (0).
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
ORIG_RAW = ROOT / "data" / "processed" / "task63_m1_bg_raw.csv"
ORIG_BOOT = ROOT / "data" / "processed" / "task63_m1_bootstrap.csv"
ORIG_BG = ROOT / "data" / "processed" / "task63_m1_backgrounds.csv"
ORIG_SEL = ROOT / "data" / "processed" / "task63_m1_selection.csv"
SEL_CSV = ROOT / "data" / "processed" / "task69_w1_selection.csv"
RAW_CSV = ROOT / "data" / "processed" / "task69_w2_bg_raw.csv"
BG_CSV = ROOT / "data" / "processed" / "task69_w3_backgrounds.csv"
BOOT_CSV = ROOT / "data" / "processed" / "task69_w3_bootstrap.csv"

STAGE = os.environ.get("W_STAGE", "run").strip().lower()
N_BOOT = int(os.environ.get("N_BOOT", "2000"))
SEED = int(os.environ.get("W_SEED", "0"))
BUDGET_S = 90 * 60          # W2: 90 min of SCORING time
N_BIN = 10
SLOTS = ("A", "B", "C")     # A=bin-min, B=bin-mid, C=bin-max
N_SUB_EXPECT = 120          # original M1 n_sub (verified on disk)
S_A222V_KNOWN = -5.200276   # carried from script 63's g1
# task-doc quoted originals for W4's contradiction check (rounding tol)
DOC_M1D = dict(point=0.00954, lo=-0.00573, hi=0.02640)
DOC_M1E = dict(point=-0.467, lo=-0.583, hi=-0.067)
TOL = 5e-4


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def label_of(decile, slot, wt_aa, position, mut_aa):
    return f"D{int(decile)}{slot}_{wt_aa}{int(position)}{mut_aa}"


def require_inputs():
    for p in (WT_CSV, A222V_MERGED, FASTA, ORIG_RAW, ORIG_BOOT, ORIG_BG,
              ORIG_SEL):
        if not p.exists():
            fail(f"(g0) missing required input: {p}")
    print("(g0) all required inputs present (incl. original M1 artifacts) "
          "-- OK")


def original_subset():
    """The subset the original M1 actually scored (evidence, not
    re-draw): unique positions of task63_m1_bg_raw.csv."""
    raw = pd.read_csv(ORIG_RAW)
    sub = sorted(int(x) for x in raw["position"].unique())
    orig_bg = pd.read_csv(ORIG_BG)
    n_sub_col = int(orig_bg["n_sub"].iloc[0])
    if len(sub) != n_sub_col:
        fail(f"(g0) original subset n={len(sub)} != task63 n_sub="
             f"{n_sub_col}")
    return sub, raw


def select_backgrounds(wt, subset):
    """W1 rule: 3 picks (A=min, B=mid, C=max) x 10 score-decile bins."""
    scores = wt["esm2_score"].to_numpy()
    edges = np.quantile(scores, [0.1 * i for i in range(1, N_BIN)])
    sub_set = set(subset)
    cand = wt[(wt["position"] != 222)
              & (~wt["position"].isin(sub_set))].copy()
    cand["bin"] = np.searchsorted(edges, cand["esm2_score"].to_numpy(),
                                  side="right") + 1
    if cand["bin"].min() != 1 or cand["bin"].max() != N_BIN:
        fail(f"(g2) bin coverage {cand['bin'].min()}.."
             f"{cand['bin'].max()} != 1..{N_BIN}")
    taken = set()
    rows = []
    for b in range(1, N_BIN + 1):
        sub = cand[cand["bin"] == b].sort_values(
            ["esm2_score", "position", "mut_aa"], kind="mergesort")
        sub = sub.drop_duplicates("position", keep="first")
        unused = sub[~sub["position"].isin(taken)]
        if len(unused) < 3:
            fail(f"(g2) decile {b} has only {len(unused)} unused "
                 "positions -- cannot take 3")
        picks = [unused.iloc[0], unused.iloc[len(unused) // 2],
                 unused.iloc[-1]]
        for slot, row in zip(SLOTS, picks):
            rows.append(dict(bin=b, slot=slot,
                             position=int(row["position"]),
                             wt_aa=row["wt_aa"], mut_aa=row["mut_aa"],
                             hgvs_pro=row["hgvs_pro"],
                             esm2_score=float(row["esm2_score"])))
            taken.add(int(row["position"]))
    bg = pd.DataFrame(rows)
    bg["bg_id"] = [label_of(r.bin, r.slot, r.wt_aa, r.position, r.mut_aa)
                   for r in bg.itertuples()]
    if len(bg) != N_BIN * 3:
        fail(f"(g2) selection has {len(bg)} rows != 30")
    if bg["position"].nunique() != 30:
        fail(f"(g2) selection positions not 30 distinct: "
             f"{sorted(bg['position'])}")
    if (bg["position"] == 222).any():
        fail("(g2) selection contains position 222")
    if bg["position"].isin(sub_set).any():
        fail(f"(g2) selection overlaps the original subset: "
             f"{sorted(bg.loc[bg['position'].isin(sub_set), 'position'])}")
    per_bin = bg.groupby("bin").size()
    if not (per_bin == 3).all():
        fail(f"(g2) per-decile counts != 3: {dict(per_bin)}")
    if bg["bg_id"].nunique() != 30:
        fail(f"(g2) background labels not unique: {list(bg['bg_id'])}")
    return bg


def print_selection(bg, s222):
    print("=== W1: selected backgrounds (rule: 3 per score-decile "
          "bin x 10 bins, pos!=222, subset-excluded, deterministic) ===")
    for _, r in bg.iterrows():
        print(f"  D{r['bin']:2d}{r['slot']}  pos {r['position']:3d} "
              f"{r['wt_aa']}>{r['mut_aa']}  {r['hgvs_pro']:16s} "
              f"S(b|WT)={r['esm2_score']:+.6f}  {r['bg_id']}")
    lo, hi = bg["esm2_score"].min(), bg["esm2_score"].max()
    print(f"severity span of the 30: [{lo:+.6f}, {hi:+.6f}] ; A222V "
          f"{s222:+.6f} sits {'INSIDE' if lo <= s222 <= hi else 'OUTSIDE'} "
          f"that span")
    by_bin = bg.groupby("bin")["esm2_score"].agg(["min", "max"])
    print("decile bin ranges (selected picks):")
    for b, r in by_bin.iterrows():
        print(f"  bin {b:2d}: [{r['min']:+.3f}, {r['max']:+.3f}]")


def check_g2(wt, bg, subset, wt_seq):
    if len(subset) != N_SUB_EXPECT:
        fail(f"(g2) subset n={len(subset)} != {N_SUB_EXPECT}")
    if 222 in subset:
        fail("(g2) subset contains 222")
    orig_sel = pd.read_csv(ORIG_SEL)
    orig8 = set(int(p) for p in orig_sel["position"])
    if set(subset) & orig8:
        fail(f"(g2) subset overlaps original 8 bg positions: "
             f"{sorted(set(subset) & orig8)}")
    print(f"(g2) original subset OK: n={len(subset)}, no 222, disjoint "
          f"from the original 8 background positions -- OK")
    if wt_seq[221] != "A":
        fail("(g2) fasta position 222 is not Ala")
    n_checked = 0
    for _, r in bg.iterrows():
        seq_aa = wt_seq[int(r["position"]) - 1]
        if seq_aa != r["wt_aa"]:
            fail(f"(g2) pos {r['position']} fasta {seq_aa} != table "
                 f"{r['wt_aa']}")
        n_checked += 1
    print(f"(g2) fasta letters match table at all {n_checked} selected "
          "background positions, 222==A -- OK")


def score_backgrounds(bg_kept, wt_seq, subset, hgvs_of):
    """W2: one forward pass per (background, position), timed.
    Scoring order: (bin, slot). First background timed as t1."""
    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    device = get_device()
    print(f"Using device: {device}")
    print("Loading ESM-2 650M...")
    t_load = time.time()
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()
    print(f"model loaded in {time.time() - t_load:.1f}s")

    rows = []
    t1 = None
    n_bg = len(bg_kept)
    t_start_all = time.time()
    for i, r in enumerate(bg_kept.itertuples()):
        bid = r.bg_id
        seq = wt_seq[:int(r.position) - 1] + r.mut_aa \
            + wt_seq[int(r.position):]
        t0 = time.time()
        for p in subset:
            scores = get_position_logprobs(model, alphabet, batch_converter,
                                           seq, p, device)
            for m, sc in scores.items():
                rows.append(dict(bg_id=bid, position=p, mut_aa=m,
                                 hgvs_pro=hgvs_of[(p, m)], score_bg=sc))
        dt = time.time() - t0
        print(f"M1b-timed: background {i + 1}/{n_bg} {bid} -> {dt:.1f} s "
              f"for {len(subset)} positions "
              f"({dt / len(subset) * 1000:.0f} ms/pass)")
        if i == 0:
            t1 = dt
            proj = t1 * 30
            print(f"(g6) t1={t1:.1f}s for the first background; "
                  f"projection for 30 = {proj:.1f}s "
                  f"(budget {BUDGET_S}s)")
    print(f"scoring wall time: {time.time() - t_start_all:.1f}s total")
    return pd.DataFrame(rows), t1


def keep_by_budget(t1):
    """W2 pre-registered reduction: k = min(30, floor(budget/t1)),
    dropping slot C (bins 1..10) then slot B (bins 1..10); slot A never
    dropped; k < 10 => BLOCKED."""
    k = min(N_BIN * 3, int(BUDGET_S // t1))
    if k < N_BIN:
        print("*** W2 BLOCKED: t1={:.1f}s -> k={} < 10 backgrounds "
              "would fit the {}s budget, and shrinking the position "
              "subset is forbidden by the task; no reduction of the "
              "subset is attempted. ***".format(t1, k, BUDGET_S))
        sys.exit(1)
    return k


def drop_order():
    """Pre-registered drop priority: C of bins 1..10, then B of bins
    1..10.  Slot A (each decile's most damaging pick) never dropped."""
    return [(b, "C") for b in range(1, N_BIN + 1)] + \
           [(b, "B") for b in range(1, N_BIN + 1)]


def valid_cache(path, subset, allowed_ids):
    if not path.exists():
        return None
    raw = pd.read_csv(path)
    ok = (
        set(raw.columns) == {"bg_id", "position", "mut_aa", "hgvs_pro",
                             "score_bg"}
        and raw["bg_id"].nunique() >= N_BIN
        and raw["bg_id"].nunique() <= 30
        and set(raw["bg_id"].unique()) <= set(allowed_ids)
        and sorted(raw["position"].unique()) == list(subset)
        and (raw.groupby("bg_id").size() == len(subset) * 19).all()
        and len(raw) == raw["bg_id"].nunique() * len(subset) * 19
    )
    return raw if ok else None


def main():
    require_inputs()
    wt = pd.read_csv(WT_CSV)
    if len(wt) != 12445 or wt["position"].nunique() != 655:
        fail(f"WT table shape unexpected: {len(wt)} rows, "
             f"{wt['position'].nunique()} positions")
    subset, orig_raw = original_subset()

    s222 = float(wt[(wt["position"] == 222) & (wt["mut_aa"] == "V")]
                 ["esm2_score"].iloc[0])
    if abs(s222 - S_A222V_KNOWN) > 1e-5:
        fail(f"(g1) S(A222V|WT)={s222} != known {S_A222V_KNOWN}")
    print(f"(g1) S(A222V|WT) matches prior verified value "
          f"{S_A222V_KNOWN} -- OK")

    bg = select_backgrounds(wt, subset)
    bg.to_csv(SEL_CSV, index=False)
    print_selection(bg, s222)
    print(f"selection saved -> {SEL_CSV}")

    if STAGE == "select":
        print("\nW_STAGE=select -> W1 done, exiting before any scoring.")
        return

    from scripts.lib.sequence import load_sequence
    from scripts.lib.esm_scoring import hgvs_pro as build_hgvs

    wt_seq = load_sequence(FASTA)
    if len(wt_seq) != 656:
        fail(f"sequence length {len(wt_seq)} != 656")
    check_g2(wt, bg, subset, wt_seq)

    # pre-build every hgvs the scoring will emit; must all resolve NOW
    # (cheap pre-gate so a naming failure cannot cost a scoring run)
    wt_aa_by_pos = wt.drop_duplicates("position").set_index("position")[
        "wt_aa"].to_dict()
    wt_index = set(wt["hgvs_pro"])
    hgvs_of = {}
    for p in subset:
        letters = [a for a in "ACDEFGHIKLMNPQRSTVWY"
                   if a != wt_aa_by_pos[p]]
        for m in letters:
            h = build_hgvs(wt_aa_by_pos[p], int(p), m)
            if h not in wt_index:
                fail(f"(g3) pre-scoring: unresolved hgvs_pro {h}")
            hgvs_of[(p, m)] = h
    print(f"(g3) pre-scoring: all {len(hgvs_of)} (position,alt) hgvs "
          "resolve in the WT table -- OK")

    # ---- W2: scoring with cache + pre-registered budget rule ----
    allowed = list(bg["bg_id"])
    raw = valid_cache(RAW_CSV, subset, allowed)
    if raw is not None:
        k = int(raw["bg_id"].nunique())
        print(f"CACHE REUSED: {RAW_CSV} matches spec ({k} bgs x "
              f"{len(subset)} x 19 = {len(raw)}) -- model not loaded; "
              "(g6) timing rule not exercised on this run; k as scored "
              "in the W2 run")
        kept_ids = sorted(raw["bg_id"].unique())
        kept = bg[bg["bg_id"].isin(kept_ids)].copy()
    else:
        bg_sorted = bg.sort_values(["bin", "slot"],
                                   kind="mergesort").reset_index(drop=True)
        first = bg_sorted.iloc[[0]]
        rest_all = bg_sorted.iloc[1:]
        # score ONLY the first background first (its time decides k)
        raw1, t1 = score_backgrounds(first, wt_seq, subset, hgvs_of)
        k = keep_by_budget(t1)
        drop = set(drop_order()[:N_BIN * 3 - k])
        kept = bg[~bg[["bin", "slot"]].apply(
            lambda r: (int(r["bin"]), r["slot"]) in drop, axis=1)].copy()
        kept = kept.sort_values(["bin", "slot"], kind="mergesort")
        if len(kept) != k:
            fail(f"(g6) kept {len(kept)} != k {k}")
        if kept["bin"].nunique() != N_BIN:
            fail(f"(g6) kept backgrounds cover "
                 f"{kept['bin'].nunique()} deciles != {N_BIN}")
        if k < N_BIN * 3:
            print(f"REDUCTION APPLIED (g6): t1={t1:.1f}s -> keep "
                  f"k={k} of 30 backgrounds (budget {BUDGET_S}s); "
                  f"dropped by pre-registered priority (C then B, bins "
                  f"1..10): {sorted(drop)}; the position subset is NOT "
                  "reduced (task W2); all 10 decile bins still covered "
                  "-- OK")
        else:
            print(f"(g6) no reduction: t1={t1:.1f}s x 30 = "
                  f"{t1 * 30:.1f}s <= {BUDGET_S}s budget")
        rest = rest_all[rest_all["bg_id"].isin(set(kept["bg_id"]))]
        raw_rest, _ = score_backgrounds(rest, wt_seq, subset, hgvs_of)
        raw = pd.concat([raw1, raw_rest], ignore_index=True)
        if raw["bg_id"].nunique() != k:
            fail(f"(g3) scored {raw['bg_id'].nunique()} bgs != k {k}")
        if len(raw) != k * len(subset) * 19:
            fail(f"(g3) {len(raw)} rows != {k}x{len(subset)}x19")
        if not raw["hgvs_pro"].isin(wt_index).all():
            bad = raw.loc[~raw["hgvs_pro"].isin(wt_index)].iloc[0]
            fail(f"(g3) unresolved hgvs_pro: {bad['hgvs_pro']}")
        raw.to_csv(RAW_CSV, index=False)
        print(f"scoring cache saved -> {RAW_CSV}")
        kept = bg[bg["bg_id"].isin(set(raw["bg_id"].unique()))].copy()
        k = len(kept)

    # ---- W3: delta summaries (definition identical to script 63) ----
    N_SUB = len(subset)
    wt_lookup = wt.set_index("hgvs_pro")["esm2_score"]
    per_pos, means = {}, {}
    for bid, g in raw.groupby("bg_id"):
        g = g.copy()
        if len(g) != N_SUB * 19 or g["hgvs_pro"].isna().any():
            fail(f"(g3) {bid}: {len(g)} rows (expect {N_SUB * 19})")
        if not g["hgvs_pro"].isin(wt_lookup.index).all():
            fail(f"(g3) {bid}: hgvs_pro not in WT table")
        g["score_wt"] = g["hgvs_pro"].map(wt_lookup)
        g["absdelta"] = (g["score_bg"] - g["score_wt"]).abs()
        pv = g.groupby("position")["absdelta"].mean().reindex(subset)
        if pv.isna().any():
            fail(f"(g3) {bid}: {int(pv.isna().sum())} subset positions "
                 "missing from groupby")
        per_pos[bid] = pv.to_numpy()
        means[bid] = float(g["absdelta"].mean())
        print(f"W3 {bid:14s} mean|delta_ESM_b| = {means[bid]:.8f} "
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
    print(f"W3 {'A222V':14s} mean|delta_ESM_b| = {means['A222V']:.8f} "
          f"over {len(a222v)} values ({N_SUB} pos x 19) [existing "
          "script-12 data, not rescored]")

    labels = list(kept["bg_id"])
    s_map = {lab: float(s) for lab, s in zip(labels, kept["esm2_score"])}
    pos_map = {lab: int(p) for lab, p in zip(labels, kept["position"])}
    s_map["A222V"] = s222
    pos_map["A222V"] = 222
    order = sorted(s_map, key=lambda k_: s_map[k_])
    n_total = k + 1
    if set(order) != set(labels) | {"A222V"} or len(order) != n_total:
        fail(f"table assembly wrong: {order}")
    tab = pd.DataFrame([dict(bg_id=lab, position=pos_map[lab],
                             S_b_given_WT=s_map[lab],
                             mean_abs_delta=means[lab]) for lab in order])

    # ---- W3: M1d -- OLS on the k new only, predict A222V ----
    X = np.column_stack([np.ones(len(labels)),
                         [s_map[i] for i in labels]])
    y_k = np.array([means[i] for i in labels])
    beta, *_ = np.linalg.lstsq(X, y_k, rcond=None)
    pred = beta[0] + beta[1] * s222
    r_obs = means["A222V"] - pred
    resid_k = y_k - X @ beta

    # ---- W3: M1e + M1d CI: position-cluster bootstrap ----
    M = np.vstack([per_pos[lab] for lab in order])   # (k+1) x n_sub
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
          "finite, point estimates inside own CIs")

    # ---- report (M1d / M1e re-run on the decile set) ----
    print("\n=== M1d re-run (W3): mean|delta_ESM_b| vs S(b|WT), "
          "sorted by severity ===")
    print(tab.to_string(index=False, float_format=lambda v: f"{v:.8f}"))
    print(f"\nOLS on the {k} new decile backgrounds: mean|delta| = "
          f"{beta[0]:.6f} + ({beta[1]:.6f}) * S(b|WT)   [resid RMS on "
          f"the {k} = {np.sqrt((resid_k ** 2).mean()):.8f}]")
    print(f"A222V: observed {means['A222V']:.8f}, predicted {pred:.8f}, "
          f"residual r = {r_obs:+.8f}")
    print(f"residual 95% position-cluster CI = [{r_ci[0]:+.8f}, "
          f"{r_ci[1]:+.8f}]  (N_BOOT={N_BOOT}, cluster=subset position)")
    rank = int((tab["mean_abs_delta"] < means["A222V"]).sum() + 1)
    print(f"A222V absolute rank of mean|delta| among the {n_total}: "
          f"{rank} (1 = lowest); lowest = {rank == 1}")
    if r_ci[1] < 0:
        verdict = ("SUPPORTS H1a: A222V sits outlier-LOW -- below the trend "
                   "the other backgrounds define, residual CI excludes 0 "
                   "(unusually little context-shift GIVEN how damaging "
                   "ESM-2 rates it)")
    elif r_ci[0] > 0:
        verdict = ("CONTRARY to H1a: A222V sits outlier-HIGH -- residual "
                   "CI excludes 0 from above")
    else:
        verdict = ("NOT SUPPORTED: A222V sits within the trend (residual "
                   "CI contains 0) -> per the task's wording the weak "
                   "signal needs a different explanation; if it is "
                   "nevertheless lowest in absolute terms (printed above) "
                   "that is severity-EXPLAINED, not outlier-LOW")
    print(f"M1d VERDICT (pre-registered, same rule as script 63): "
          f"{verdict}")

    print(f"\n=== M1e re-run (W3): correlation across the {n_total} "
          "backgrounds ===")
    print(f"Spearman rho = {rho_sp:+.6f}  95% cluster CI "
          f"[{sp_ci[0]:+.6f}, {sp_ci[1]:+.6f}]  [PRIMARY]")
    print(f"Pearson  r   = {rho_pe:+.6f}  95% cluster CI "
          f"[{pe_ci[0]:+.6f}, {pe_ci[1]:+.6f}]")
    dirn = "negative" if rho_sp < 0 else "positive"
    consistent = "consistent" if rho_sp < 0 else "INCONSISTENT"
    excl0 = (sp_ci[1] < 0 or sp_ci[0] > 0)
    print(f"H1a expected direction: NEGATIVE (more damaging = lower S = "
          f"larger shift); observed sign = {dirn} -> {consistent} with "
          f"the severity->shift story in sign "
          f"({'CI excludes 0' if excl0 else 'CI contains 0'})")

    # ---- W4: side-by-side vs the original 9-point result ----
    ob = pd.read_csv(ORIG_BOOT).set_index("stat")
    obg = pd.read_csv(ORIG_BG)
    o_n = len(obg)
    o_nsub = int(obg["n_sub"].iloc[0])
    o_nb = int(obg["n_boot"].iloc[0])
    o_verdict = str(obg["verdict_m1d"].iloc[0])
    o_r = float(ob.loc["a222v_residual", "point"])
    o_rlo = float(ob.loc["a222v_residual", "lo"])
    o_rhi = float(ob.loc["a222v_residual", "hi"])
    o_rho = float(ob.loc["spearman_rho", "point"])
    o_rho_lo = float(ob.loc["spearman_rho", "lo"])
    o_rho_hi = float(ob.loc["spearman_rho", "hi"])
    print("\n=== W4: original bimodal design vs new decile design "
          "(SAME subset, both position-cluster bootstrap) ===")
    print(f"ORIGINAL (task63, n={o_n} = 8 extremes-per-region + A222V, "
          f"n_sub={o_nsub}, N_BOOT={o_nb}):")
    print(f"  M1d residual {o_r:+.5f} CI [{o_rlo:+.5f}, {o_rhi:+.5f}] "
          f"-> {'CI contains 0' if o_rlo <= 0 <= o_rhi else 'CI excludes 0'}"
          f"; original verdict starts '{o_verdict[:30]}...'")
    print(f"  M1e rho {o_rho:+.3f} CI [{o_rho_lo:+.3f}, {o_rho_hi:+.3f}]")
    print("  task-doc quoted: M1d +0.00954 CI [-0.00573,+0.02640]; "
          "M1e rho -0.467 CI [-0.583,-0.067]")
    for name, disk, doc in (("M1d point", o_r, DOC_M1D["point"]),
                            ("M1d lo", o_rlo, DOC_M1D["lo"]),
                            ("M1d hi", o_rhi, DOC_M1D["hi"]),
                            ("M1e point", o_rho, DOC_M1E["point"]),
                            ("M1e lo", o_rho_lo, DOC_M1E["lo"]),
                            ("M1e hi", o_rho_hi, DOC_M1E["hi"])):
        if abs(disk - doc) > TOL:
            print(f"  CONTRADICTION ({name}): disk {disk:+.6f} vs "
                  f"task-doc {doc:+.6f} (tol {TOL}) -- BOTH printed, "
                  "neither silently preferred")
    print(f"NEW (W3, n={n_total} = {k} decile backgrounds + A222V, "
          f"n_sub={N_SUB}, N_BOOT={N_BOOT}):")
    new_incl0 = r_ci[0] <= 0 <= r_ci[1]
    orig_incl0 = o_rlo <= 0 <= o_rhi
    print(f"  M1d residual {r_obs:+.5f} CI [{r_ci[0]:+.5f}, "
          f"{r_ci[1]:+.5f}] -> {'CI contains 0' if new_incl0 else 'CI excludes 0'}")
    print(f"  M1e rho {rho_sp:+.3f} CI [{sp_ci[0]:+.3f}, "
          f"{sp_ci[1]:+.3f}]")
    if new_incl0 == orig_incl0:
        m1d_label = ("M1d verdict UNCHANGED (residual CI still contains "
                     "0: A222V still within trend)") if new_incl0 else \
            ("M1d verdict CHANGED (residual CI now excludes 0 where the "
             "original contained it -- read the sign above)")
    else:
        m1d_label = ("M1d verdict CHANGED (residual CI relationship to 0 "
                     "flipped vs the original)")
    if excl0 and np.sign(rho_sp) == np.sign(o_rho) \
            and abs(rho_sp) > abs(o_rho):
        m1e_label = "M1e STRENGTHENS (same negative sign, CI excludes 0, |rho| larger)"
    elif not excl0:
        m1e_label = "M1e WEAKENS (new CI contains 0)"
    elif np.sign(rho_sp) != np.sign(o_rho):
        m1e_label = "M1e SIGN FLIPPED vs original"
    elif abs(rho_sp) <= abs(o_rho):
        m1e_label = ("M1e WEAKENS in magnitude (same sign, CI excludes 0, "
                     "|rho| smaller)")
    else:
        m1e_label = "M1e comparable"
    print(f"  mechanical label: {m1d_label}")
    print(f"  mechanical label: {m1e_label}")
    print(f"  design note: original = bimodal 8 extremes + interpolated "
          f"A222V; new = 10 deciles x 3 picks (k={k} kept under the "
          f"pre-registered budget rule) + same A222V arm, identical "
          f"subset -- a DESIGN comparison, not an independent "
          f"replication (same underlying scores machinery)")

    print("\nLIMITATIONS (printed by the script, AGENTS 6):")
    print("  - Decile stratification reduces but does not eliminate")
    print("    severity-driven selection: picks are still chosen ON the")
    print("    severity axis (the design's point) -- spread across all")
    print("    10 deciles instead of two regional extremes.")
    print("  - Bootstrap resamples POSITIONS: CIs cover mean|delta|")
    print("    estimation error at fixed backgrounds, NOT background-")
    print("    sampling variability. Correlation is descriptive.")
    print("  - delta is a MODEL-internal log-odds shift, not fitness")
    print("    epistasis; nothing here measures real epistasis.")
    print("  - A222V arm reuses script 12's merged file (same code path,")
    print("    not rescored) -- like-for-like by code path.")
    print("  - The 90-min budget is applied to scoring time; model load")
    print("    and analysis are extra (small).")

    tab["n_selected"] = 30
    tab["n_kept"] = k
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
    tab["m1d_label"] = m1d_label
    tab["m1e_label"] = m1e_label
    tab.to_csv(BG_CSV, index=False)
    pd.DataFrame([
        dict(stat="spearman_rho", point=rho_sp, lo=sp_ci[0], hi=sp_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="pearson_r", point=rho_pe, lo=pe_ci[0], hi=pe_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_residual", point=r_obs, lo=r_ci[0], hi=r_ci[1],
             n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="ols_slope_on_k", point=float(beta[1]), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_predicted", point=float(pred), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="a222v_observed", point=means["A222V"], lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="resid_k_rms",
             point=float(np.sqrt((resid_k ** 2).mean())), lo=np.nan,
             hi=np.nan, n_boot=N_BOOT, cluster="subset_position"),
        dict(stat="original_spearman_rho", point=o_rho, lo=o_rho_lo,
             hi=o_rho_hi, n_boot=o_nb, cluster="subset_position"),
        dict(stat="original_a222v_residual", point=o_r, lo=o_rlo,
             hi=o_rhi, n_boot=o_nb, cluster="subset_position"),
    ]).to_csv(BOOT_CSV, index=False)
    print(f"\nSaved: {BG_CSV}\nSaved: {BOOT_CSV}")


if __name__ == "__main__":
    main()
