"""AE1 + AE2 — Position vs residue identity at the 222 background:
the evaluator's 2x2 cells (task doc L318-329). PRE-REGISTERED: this
docstring was written before the first run. One script, ONE run, TWO
verdict blocks ([AE1] and [AE2] log entries quote their own block) —
a single scoring pass with one shared subset is what makes the two
cells comparable; splitting them into two scripts would draw two
different "random" subsets from two different pools.

PREMISE PROVENANCE (disclosed): "the outsized context-shift found for
A222V" is the evaluator's characterization (task doc L321; the digest
that coined it is external to this repo). This script does NOT assume
it: it defines the statistic, measures all three available cells, and
reports plainly even if A222V is not outsized at all (frozen rule iv).

STATISTIC (same construction as M1/script 63, byte-level semantics):
  delta_ESM_b(v) = S(v|b) - S(v|WT)  (merged on hgvs_pro; target
  positions are never background positions, so the WT letter at each
  target is identical across backgrounds); context-shift magnitude of
  background b = mean |delta_ESM_b| over the common subset x 19
  substitutions (M1's summary statistic).

CELLS (the task's own 2x2; the fourth cell is NOT requested by the
task text and is NOT measured — disclosed as a limitation):
  AE1 (task L318-323): ALL 19 substitutions at position 222 as
     backgrounds (A>X, X != A; the WT table has exactly these 19 rows).
     Question (verbatim): does the outsized context-shift track being
     AT position 222 generally, or is it specific to Val?
  AE2 (task L324-329): A>V at every OTHER Ala position (WT table rows
     wt_aa==A, position!=222, mut_aa==V = 38 backgrounds; measured
     before writing: 39 Ala positions total, 38 excluding 222). Same
     construction; compared against AE1's sweep.

MACHINERY (reuse, not reimplement; AGENTS 7):
  * subset rule: scripts/63's draw_subset/check_subset IMPORTED
    (importlib; module guards __main__): pool = WT-table positions
    MINUS ({222} U the 38 other-Ala positions) = 616 positions, draw
    AE_N_SUB=120 with AE_SEED=0 — one subset, identical for all 57
    backgrounds (M1's precedent: a background's own position is not a
    target; excluding all 39 keeps hgvs naming unambiguous and makes
    every cell directly comparable).
  * scoring: scripts/lib/esm_scoring.get_position_logprobs +
    scripts/lib/sequence.load_sequence, model = ESM-2 t33 650M
    (esm2_t33_650M_UR50D) — the SAME model and code path that
    produced the atlas delta_ESM (scripts 10/11/12/63 lineage). Zero
    third-party edits; fair-esm's previously disclosed portability
    patch is already in place (unchanged by this script). One forward
    pass per (background, position), as in M1.
  * scoring loop + timing policy are this script's own (63's loop is
    coupled to its M1 labels and its per-background-only timing rule,
    which does not budget for 57 backgrounds) — disclosed here.

CACHING: raw scores -> data/processed/task82_ae_raw.csv; reused iff it
matches the current spec exactly (57 backgrounds x subset x 19, same
subset positions, per-bg counts) — exists so the smoke -> full N_BOOT
protocol and any rerun does not re-pay the model cost (scoring is
deterministic: eval mode, no dropout).

TIMING RULE (measure first, AGENTS 1; pre-registered):
  Time the FIRST background t1; projection = t1 x 57. If projection >
  5,400 s, REDUCE AE_N_SUB ONCE to max(60, round(n_sub * 5400 /
  projection)), re-draw the subset (same seed, new size), rescore from
  scratch, print a REDUCTION block. If the post-reduction projection
  still exceeds 7,200 s -> gfail TIMING (stop for a timing decision
  rather than guess; AGENTS: >2h tasks measured first). At most one
  reduction (M1 precedent, no loop).

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G1 WT-table shape 12,445 rows / 655 positions (script 10's table).
  G2 AE1 = exactly 19 rows at position 222, all wt A, 19 distinct
     mut_aa; AE2 = exactly 38 rows (39 Ala positions - 222), all
     distinct positions, none is 222; FASTA (data/raw/P42898.fasta)
     letter matches the table wt_aa at all 39 background positions and
     FASTA[221] == 'A', sequence length 656.
  G3 subset: disjoint from {222} U all background positions, |subset|
     == n_sub after any reduction (63's check_subset).
  G4 every background has n_sub*19 rows, every hgvs_pro resolves in
     both the WT table and the merged script-12 file (no silent row
     loss).
  G5 A222V cross-provenance: my fresh A222V arm vs script 12's
     existing delta_esm (merged_wt_a222v_scores.csv) on the subset —
     max|diff| < 1e-4, else STOP with both constructions printed
     (sanity failure, unclear cause => stop; if the cause is visible
     in the print, it is a gate-found bug: fix code to match this
     frozen docstring and disclose). Tolerance rationale: same model,
     same lib, deterministic eval — float32 path/order noise is ~1e-6;
     a sign flip, WT/bg swap, or construction change lands orders of
     magnitude above 1e-4. The actual max diff is printed either way
     (mixed provenance resolved by measured agreement, disclosed).
  G6 timing: reduction prints REDUCTION and shrinks n_sub; projection
     printed either way (as in M1's g6).
  G7 bootstrap sanity: all draws finite, draw count == N_BOOT, CI
     ordered, each point estimate inside its own CI (else the
     resampling is broken -> fail; do not raise N).

STATISTICS + FROZEN VERDICT RULES (position-cluster bootstrap;
cluster = subset position; the SAME resampled position indices are
used across ALL backgrounds in a draw so pairing survives — M1e's
protocol; N_BOOT env default 10,000, seed 0; smoke uses 300):
  Per background: mean|delta_b| (balanced design: mean over subset x
  19 == mean of the per-position 19-sub means; the per-position
  vectors are what the bootstrap resamples).
  AE1 contrast (IDENTITY held at V? no — POSITION held fixed):
    D_identity = mean|d|(A222V) - mean over the OTHER 18 backgrounds
    AT 222. Holds position fixed, varies identity.
  AE2 contrast (IDENTITY held fixed at A>V):
    D_position = mean|d|(A222V) - mean over the 38 A>V ELSEWHERE.
    Holds identity fixed, varies position.
  Each with two-sided p_boot; classification per contrast:
    CI entirely > 0 -> "larger"; entirely < 0 -> "smaller";
    contains 0 -> "indistinguishable".
  FROZEN combined rule for the task's question (stated before any
  number is seen):
    (iv) both contrasts indistinguishable -> the "outsized" premise is
         NOT supported for this statistic; report plainly.
    (ii) D_identity indistinguishable AND D_position larger -> the
         shift TRACKS BEING AT 222 (A222V does not separate from other
         residues at 222 but does from A>V elsewhere).
    (iii) D_identity larger AND D_position indistinguishable ->
         SPECIFIC TO VAL: A222V separates from non-Val residues at 222
         and is not distinguishable from A>V elsewhere, i.e. the
         elevated shift follows the Val identity.
    (i) both larger -> BOTH factors contribute (interaction-like).
    Any "smaller" classification is reported with its sign as-is and
     overrides the paired story for that contrast (report, don't
     smooth). Descriptive companions always printed: A222V's rank
     among the 19, whether it is the max of the 19, A222V's percentile
     among the 38, and the mixed-identity group contrast (mean of 19
     vs mean of 38) with its own CI — LABELED descriptive because it
     confounds identity (18 non-Val vs all-Val).

DISCLOSED LIMITATIONS (printed with results, AGENTS 6):
  - Cell (other-Ala, non-Val) is unmeasured (task requests only A>V
    there), so a full two-factor decomposition is not identifiable;
    the two pre-registered contrasts each hold exactly one factor
    fixed and are what the task's cells support.
  - One-directional scoring (v after b only), same as the atlas
    construction (script 32's stated limitation).
  - Backends: backgrounds are not filtered for atlas measurability
    (M1's disclosed assumption, carried over).
  - Subset sampling: n_sub of a 616 pool; position-bootstrap CIs
    quantify mean|delta|-estimation error at FIXED backgrounds (they
    do not include background-sampling variability — same caveat M1
    printed).
  - mean|delta| over the model's own shifts is a magnitude statistic:
    it says nothing about direction/sign of the shift.

SMOKE (SMOKE=1): score ONLY the A222V background on an 8-position
subset, run G1-G3 + the G5 cross-check + the delta construction print,
then exit 0 — model-load/plumbing proof at minimal cost; the full
57-background run's join/bootstrap code runs first at full scale in the
full run (disclosed smoke scope, same pattern as AD7).

OUTPUTS: data/processed/task82_ae_raw.csv (scoring cache),
task82_ae_backgrounds.csv (57-row summary + contrast scalars),
task82_ae_position_vectors.csv (57 x n_sub per-position means),
task82_ae_contrasts.csv (D_identity, D_position, group contrast with
CIs/p/classification). Existing scripts/libs/results untouched. Next
free script number after this: 83.
"""
import importlib.util
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WT_CSV = ROOT / "data" / "processed" / "esm2_wt_scores.csv"
MERGED = ROOT / "data" / "processed" / "merged_wt_a222v_scores.csv"
FASTA = ROOT / "data" / "raw" / "P42898.fasta"
RAW_CACHE = ROOT / "data" / "processed" / "task82_ae_raw.csv"
OUT_BG = ROOT / "data" / "processed" / "task82_ae_backgrounds.csv"
OUT_VEC = ROOT / "data" / "processed" / "task82_ae_position_vectors.csv"
OUT_CON = ROOT / "data" / "processed" / "task82_ae_contrasts.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_SUB = int(os.environ.get("AE_N_SUB", "120"))
SEED = int(os.environ.get("AE_SEED", "0"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
PROJ_OK_S = 5400.0
PROJ_FAIL_S = 7200.0
T0 = time.time()

# subset rule reused verbatim from script 63 (M1 precedent)
_s63_spec = importlib.util.spec_from_file_location(
    "s63", ROOT / "scripts" / "63_m1_context_shift_vs_severity.py")
_s63 = importlib.util.module_from_spec(_s63_spec)
_s63_spec.loader.exec_module(_s63)
draw_subset = _s63.draw_subset
check_subset = _s63.check_subset


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def pfmt(p):
    return "<1/N" if p == 0 else f"{p:.4f}"


def build_backgrounds(wt):
    ae1 = wt[wt["position"] == 222].copy()
    if (len(ae1) != 19 or not (ae1["wt_aa"] == "A").all()
            or ae1["mut_aa"].nunique() != 19):
        gfail(f"G2 FAIL: AE1 sweep not 19 distinct A>X rows at 222: "
              f"{len(ae1)} rows, wts {sorted(ae1['wt_aa'].unique())}, "
              f"{ae1['mut_aa'].nunique()} distinct muts")
    ae1["cell"] = "AE1_at222"
    ae1["bg_id"] = ["A222_" + m for m in ae1["mut_aa"]]
    ae2 = wt[(wt["wt_aa"] == "A") & (wt["position"] != 222)
             & (wt["mut_aa"] == "V")].copy()
    if len(ae2) != 38 or ae2["position"].nunique() != 38 \
            or (ae2["position"] == 222).any():
        gfail(f"G2 FAIL: AE2 not 38 distinct other-Ala A>V rows: "
              f"{len(ae2)} rows, {ae2['position'].nunique()} positions")
    ae2["cell"] = "AE2_A2V_elsewhere"
    ae2["bg_id"] = ["AV_" + str(int(p)) for p in ae2["position"]]
    bg = pd.concat([ae1, ae2], ignore_index=True)
    if bg["bg_id"].nunique() != 57:
        gfail(f"G2 FAIL: background ids not 57 unique: "
              f"{bg['bg_id'].nunique()}")
    print(f"  G2 backgrounds PASS: AE1 = 19 rows at 222 (all wt A, "
          f"19 distinct muts); AE2 = 38 other-Ala A>V rows (39 Ala "
          f"positions - 222); total {len(bg)} unique ids")
    return bg


def score_all(bg, wt_seq, subset, part_path=None):
    """One forward pass per (background, position); 650M, eval mode;
    models/scoring lib untouched. Returns (raw_df, t_first_seconds) where
    t_first is the FIRST background's duration of THIS process — the
    frozen docstring's reduction rule keys on the first background.

    part_path (implementation-only, added after attempt 1 was externally
    interrupted at background 38/57; NO decision rule, gate, statistic,
    subset or seed changed): per-background append checkpoint. Complete
    backgrounds (validated: count == 19*n_sub, position set == subset,
    no duplicate (position, mut_aa) pairs) are skipped and reloaded."""
    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    # ---- checkpoint load + validation ----------------------------------
    kept = None
    done_ids = set()
    if part_path is not None and part_path.exists():
        cand = pd.read_csv(part_path)
        valid = []
        for bid, g in cand.groupby("bg_id"):
            ok = (len(g) == 19 * len(subset)
                  and set(int(x) for x in g["position"].unique())
                  == set(int(x) for x in subset)
                  and not g.duplicated(["position", "mut_aa"]).any())
            if ok:
                done_ids.add(bid)
                valid.append(g)
            else:
                print(f"  checkpoint: invalid rows for {bid} "
                      f"({len(g)} rows) -> dropped, will rescore")
        kept = (pd.concat(valid, ignore_index=True) if valid else None)
        if kept is not None and len(kept) < len(cand):
            kept.to_csv(part_path, index=False)   # purge stale rows
        elif kept is None:
            part_path.unlink()
        if done_ids:
            print(f"  CHECKPOINT RESUME: {len(done_ids)}/{len(bg)} "
                  f"backgrounds already complete in {part_path.name}")
    todo = bg[~bg["bg_id"].isin(done_ids)]

    device = get_device()
    print(f"Using device: {device}")
    print("Loading ESM-2 650M (same model as scripts 10/11/12/63)...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    rows = [] if kept is None else kept.to_dict("records")
    t_first = None
    n_todo = len(todo)
    t_start = time.time()
    for i, r in enumerate(todo.itertuples()):
        seq = wt_seq[:int(r.position) - 1] + r.mut_aa + \
            wt_seq[int(r.position):]
        t0 = time.time()
        rows_this = []
        for p in subset:
            scores = get_position_logprobs(model, alphabet, batch_converter,
                                           seq, p, device)
            for m, sc in scores.items():
                rows_this.append(dict(bg_id=r.bg_id, position=p, mut_aa=m,
                                      score_bg=sc))
        rows.extend(rows_this)
        dt = time.time() - t0
        if t_first is None:
            t_first = dt          # FIRST background of this process
        proj = dt * len(bg)
        if part_path is not None:
            pd.DataFrame(rows_this).to_csv(
                part_path, mode="a", header=not part_path.exists(),
                index=False)
        print(f"  timed: background {i + 1}/{n_todo} {r.bg_id} -> {dt:.1f}s "
              f"for {len(subset)} positions ({dt / len(subset) * 1000:.0f} "
              f"ms/pass); projection total = {proj:.1f}s", flush=True)
    if t_first is None:
        print("  scoring skipped: every background was already in the "
              "checkpoint (t_first not measured this run)")
    print(f"  scoring wall time: {time.time() - t_start:.1f}s total")
    return pd.DataFrame(rows), t_first


def paired_boot(vec_by_bg, names, obs_fn, n_boot, seed, label):
    """Position-cluster bootstrap: resample subset positions with
    replacement; SAME indices across every background so pairing
    survives (M1e). vec_by_bg: {bg_id: np.array over subset positions}.
    obs_fn(means_dict) -> scalar; means computed per draw as the mean of
    the resampled per-position means (balanced 19-sub design)."""
    rng = np.random.default_rng(seed)
    n_pos = len(next(iter(vec_by_bg.values())))
    obs = obs_fn({k: float(np.mean(v)) for k, v in vec_by_bg.items()})
    draws = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n_pos, n_pos)
        means = {k: float(v[idx].mean()) for k, v in vec_by_bg.items()}
        draws[b] = obs_fn(means)
    if not np.isfinite(draws).all():
        gfail(f"G7 FAIL ({label}): non-finite bootstrap draws")
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = min(2.0 * min((draws <= 0).mean(), (draws >= 0).mean()), 1.0)
    if not (lo <= obs <= hi):
        gfail(f"G7 FAIL ({label}): point estimate {obs:.6f} outside its "
              f"own CI [{lo:.6f},{hi:.6f}] — resampling broken")
    if draws.size != n_boot:
        gfail(f"G7 FAIL ({label}): draw count {draws.size} != N_BOOT")
    return float(obs), float(lo), float(hi), float(p)


def classify(lo, hi):
    if lo > 0:
        return "larger"
    if hi < 0:
        return "smaller"
    return "indistinguishable"


if __name__ == "__main__":
    banner(f"AE1+AE2 — 222 position vs residue identity (scripts/82)  "
           f"SMOKE={SMOKE} N_BOOT={N_BOOT} N_SUB={N_SUB} seed={SEED}")

    wt = pd.read_csv(WT_CSV)
    if len(wt) != 12445 or wt["position"].nunique() != 655:
        gfail(f"G1 FAIL: WT table {len(wt)} rows / "
              f"{wt['position'].nunique()} positions != 12,445 / 655")
    print(f"  G1 PASS: WT table 12,445 rows / 655 positions")
    bg = build_backgrounds(wt)

    from scripts.lib.sequence import load_sequence
    from scripts.lib.esm_scoring import hgvs_pro as build_hgvs
    wt_seq = load_sequence(FASTA)
    if len(wt_seq) != 656:
        gfail(f"G2 FAIL: FASTA length {len(wt_seq)} != 656")
    if wt_seq[221] != "A":
        gfail("G2 FAIL: FASTA position 222 is not Ala")
    n_mismatch = 0
    for _, r in bg.iterrows():
        if wt_seq[int(r.position) - 1] != r["wt_aa"]:
            n_mismatch += 1
    if n_mismatch:
        gfail(f"G2 FAIL: FASTA letter != table wt_aa at {n_mismatch} "
              f"background positions")
    print(f"  G2 FASTA PASS: len 656, [222]='A', wt letters match table "
          f"at all 39 background positions")

    bg_positions = sorted(int(p) for p in bg["position"].unique())
    n_sub_eff = 8 if SMOKE else N_SUB
    subset = draw_subset(wt["position"].unique(), bg_positions, n_sub_eff,
                         SEED)
    check_subset(subset, bg_positions, n_sub_eff)
    pool = 655 - len(bg_positions)
    print(f"  G3 PASS: subset n={n_sub_eff} from pool {pool} (655 - 39 "
          f"excluded), disjoint from {{222}} U bg positions, seed {SEED}")

    wt_aa_by_pos = wt.drop_duplicates("position").set_index("position")[
        "wt_aa"].to_dict()
    score_wt = {(int(r.position), r.mut_aa): float(r.esm2_score)
                for r in wt.itertuples()}

    if SMOKE:
        bg_eff = bg[bg["bg_id"] == "A222_V"].copy()
        print(f"  SMOKE=1: scoring ONLY {bg_eff['bg_id'].iloc[0]} on "
              f"{n_sub_eff} positions (plumbing proof; full run does the "
              f"57 backgrounds + joins + bootstraps)")
        raw, t1 = score_all(bg_eff, wt_seq, subset)
        merged = pd.read_csv(MERGED)
        raw["hgvs_pro"] = [build_hgvs(wt_aa_by_pos[int(p)], int(p), m)
                           for p, m in zip(raw["position"], raw["mut_aa"])]
        mm = raw.merge(merged[["hgvs_pro", "delta_esm"]], on="hgvs_pro",
                       how="left")
        if mm["delta_esm"].isna().any():
            gfail(f"G5 FAIL (smoke): {int(mm['delta_esm'].isna().sum())} "
                  f"subset rows missing from merged script-12 file")
        # rebuild delta directly from position/mut keys (same join the
        # full run uses)
        mm["score_wt"] = [score_wt[(int(p), m)]
                          for p, m in zip(mm["position"], mm["mut_aa"])]
        mm["delta_calc"] = mm["score_bg"] - mm["score_wt"]
        maxdiff = float((mm["delta_calc"] - mm["delta_esm"]).abs().max())
        print(f"  G5 cross-check (smoke subset): max|delta_calc - "
              f"script12 delta_esm| = {maxdiff:.3e} "
              f"({'PASS' if maxdiff < 1e-4 else 'FAIL'}) over "
              f"{len(mm)} rows")
        if maxdiff >= 1e-4:
            head = mm[["hgvs_pro", "score_bg", "score_wt", "delta_calc",
                       "delta_esm"]].head(8).to_string()
            gfail(f"G5 FAIL (smoke): constructions disagree; first rows "
                  f"follow:\n{head}")
        print(f"\nSMOKE=1 — plumbing + G1-G3 + G5 PASS in "
              f"{time.time() - T0:.0f}s; full 57-background run, joins, "
              f"and AE1/AE2 verdict blocks deferred (disclosed smoke "
              f"scope). t1(smoke, 8 pos) = {t1:.1f}s -> naive full "
              f"projection at n_sub={N_SUB}: {t1 / 8 * N_SUB * 57:.0f}s")
        sys.exit(0)

    # ---- full: cache or score with pre-registered reduction -----------
    use_cache = False
    raw = None
    if RAW_CACHE.exists():
        cand = pd.read_csv(RAW_CACHE)
        ok = (
            set(cand.columns) == {"bg_id", "position", "mut_aa",
                                  "score_bg"}
            and len(cand) == 57 * N_SUB * 19
            and cand["bg_id"].nunique() == 57
            and sorted(cand["position"].unique()) == subset
            and (cand.groupby("bg_id").size() == N_SUB * 19).all()
        )
        if ok:
            raw = cand
            use_cache = True
            print(f"  CACHE REUSED: {RAW_CACHE.name} matches spec "
                  f"(57 x {N_SUB} x 19 = {len(raw)}) — deterministic "
                  f"scoring not re-paid")
        else:
            print("  cache present but spec mismatch -> rescoring")
    if not use_cache:
        part = ROOT / "data" / "processed" / "task82_ae_raw_partial.csv"
        print("  NOTE (disclosed): per-background checkpoint active "
              "(implementation-only, added after attempt 1 was externally "
              "interrupted at bg 38/57; no decision rule/gate/statistic/"
              "subset/seed changed); reduction rule keys on t1 = FIRST "
              "background per the frozen docstring")
        raw, t_first = score_all(bg, wt_seq, subset, part_path=part)
        if t_first is None:
            print("  (G6) no timing measured this run (all checkpointed); "
                  "reduction rule not applicable")
        else:
            proj = t_first * 57
            if proj > PROJ_OK_S:
                new_n = max(60, int(round(N_SUB * PROJ_OK_S / proj)))
                if new_n < N_SUB:
                    print(f"  (G6) REDUCTION APPLIED: projection {proj:.0f}s "
                          f"> {PROJ_OK_S:.0f}s -> n_sub {N_SUB} -> {new_n}; "
                          f"re-drawing subset (same seed) and rescoring")
                    N_SUB = new_n
                    subset = draw_subset(wt["position"].unique(), bg_positions,
                                         N_SUB, SEED)
                    check_subset(subset, bg_positions, N_SUB)
                    if part.exists():
                        part.unlink()      # old-n_sub checkpoint discarded
                        print("  (G6) discarded old-n_sub checkpoint")
                    raw, t_first = score_all(bg, wt_seq, subset,
                                             part_path=part)
                    proj = (t_first if t_first else 0.0) * 57
                if proj > PROJ_FAIL_S:
                    gfail(f"G6 TIMING: post-reduction projection {proj:.0f}s "
                          f"> {PROJ_FAIL_S:.0f}s cap — stopping for a timing "
                          f"decision (measure-first rule)")
            else:
                print(f"  (G6) timing rule: projection {proj:.0f}s <= "
                      f"{PROJ_OK_S:.0f}s -> NO reduction (n_sub stays "
                      f"{N_SUB})")
        raw.to_csv(RAW_CACHE, index=False)
        if part.exists():
            part.unlink()
        print(f"  cache saved -> {RAW_CACHE.name}")

    # ---- joins + gates -------------------------------------------------
    raw["hgvs_pro"] = [build_hgvs(wt_aa_by_pos[int(p)], int(p), m)
                       for p, m in zip(raw["position"], raw["mut_aa"])]
    raw["score_wt"] = [score_wt[(int(p), m)]
                       for p, m in zip(raw["position"], raw["mut_aa"])]
    raw["delta"] = raw["score_bg"] - raw["score_wt"]
    counts = raw.groupby("bg_id").size()
    if len(raw) != 57 * N_SUB * 19 or not (counts == N_SUB * 19).all():
        gfail(f"G4 FAIL: rows {len(raw)} != {57 * N_SUB * 19} or per-bg "
              f"counts not all {N_SUB * 19}")
    merged = pd.read_csv(MERGED)
    hit = raw["hgvs_pro"].isin(set(merged["hgvs_pro"]))
    if not hit.all():
        gfail(f"G4 FAIL: {int((~hit).sum())} hgvs not in merged "
              f"script-12 file")
    print(f"  G4 PASS: {len(raw)} rows = 57 x {N_SUB} x 19, every hgvs "
          f"resolves in WT table + merged file")

    a222v_raw = raw[raw["bg_id"] == "A222_V"]
    chk = a222v_raw.merge(merged[["hgvs_pro", "delta_esm"]], on="hgvs_pro",
                          how="left")
    maxdiff = float((chk["delta"] - chk["delta_esm"]).abs().max())
    print(f"  G5 cross-provenance: fresh A222V arm vs script 12's "
          f"delta_esm on {len(chk)} subset rows: max|diff| = "
          f"{maxdiff:.3e} ({'PASS' if maxdiff < 1e-4 else 'FAIL'}, "
          f"tol 1e-4)")
    if maxdiff >= 1e-4:
        head = chk[["hgvs_pro", "delta", "delta_esm"]].head(8).to_string()
        gfail(f"G5 FAIL: constructions disagree (unclear cause = stop). "
              f"First rows:\n{head}")

    # ---- per-background statistics -------------------------------------
    summary = raw.groupby("bg_id").agg(
        mean_abs_delta=("delta", lambda s: float(s.abs().mean())),
        mean_delta=("delta", "mean"),
        max_abs_delta=("delta", lambda s: float(s.abs().max())),
        n=("delta", "size")).reset_index()
    summary = summary.merge(bg[["bg_id", "cell", "position", "wt_aa",
                                "mut_aa", "hgvs_pro"]], on="bg_id",
                            how="left")
    vec = (raw.assign(absd=raw["delta"].abs())
              .groupby(["bg_id", "position"])["absd"].mean()
              .reset_index(name="mean_abs_delta"))
    vec_by_bg = {b: g["mean_abs_delta"].to_numpy()
                 for b, g in vec.groupby("bg_id")}
    for b in summary["bg_id"]:
        if len(vec_by_bg[b]) != N_SUB:
            gfail(f"G4 FAIL: {b} has {len(vec_by_bg[b])} positions != "
                  f"{N_SUB}")

    m_a222v = float(summary.loc[summary["bg_id"] == "A222_V",
                                "mean_abs_delta"].iloc[0])
    ae1_ids = [b for b in summary["bg_id"] if b.startswith("A222_")]
    ae1_others = [b for b in ae1_ids if b != "A222_V"]
    ae2_ids = [b for b in summary["bg_id"] if b.startswith("AV_")]
    m19 = summary.set_index("bg_id").loc[ae1_ids, "mean_abs_delta"]
    m38 = summary.set_index("bg_id").loc[ae2_ids, "mean_abs_delta"]

    # ---- AE1 verdict block ---------------------------------------------
    banner("AE1 — all 19 substitutions at position 222 as backgrounds", "-")
    tbl1 = summary[summary["bg_id"].isin(ae1_ids)].sort_values(
        "mean_abs_delta", ascending=False)
    for r in tbl1.itertuples():
        print(f"  {r.bg_id:9s} {r.wt_aa}>{r.mut_aa}  mean|delta| = "
              f"{r.mean_abs_delta:.6f}   mean delta = {r.mean_delta:+.6f}")
    rank = int((m19 > m_a222v).sum()) + 1
    is_max = bool(m19.idxmax() == "A222_V")
    med18 = float(m19[m19.index != "A222_V"].median())
    print(f"  A222V rank among the 19 (1 = largest): {rank} ; "
          f"{'IS the max' if is_max else 'not the max'} ; median of the "
          f"other 18 = {med18:.6f} ; A222V - median18 = "
          f"{m_a222v - med18:+.6f}")

    d_id, lo_id, hi_id, p_id = paired_boot(
        vec_by_bg, ae1_ids,
        lambda mm: mm["A222_V"] - np.mean([mm[b] for b in ae1_others]),
        N_BOOT, SEED, "D_identity")
    c_id = classify(lo_id, hi_id)
    print(f"  D_identity = mean|d|(A222V) - mean(other 18 at 222) = "
          f"{d_id:+.6f} [{lo_id:+.6f},{hi_id:+.6f}] p={pfmt(p_id)} "
          f"-> {c_id} (position held fixed, identity varied)")

    # ---- AE2 verdict block ---------------------------------------------
    banner("AE2 — A>V at other Ala positions vs the 222 sweep", "-")
    print(f"  AE2 group (38 A>V elsewhere): mean|delta| min "
          f"{m38.min():.6f}, median {m38.median():.6f}, max "
          f"{m38.max():.6f}; A222V = {m_a222v:.6f} exceeds "
          f"{int((m38 < m_a222v).sum())}/38")
    d_pos, lo_pos, hi_pos, p_pos = paired_boot(
        vec_by_bg, ae2_ids,
        lambda mm: mm["A222_V"] - np.mean([mm[b] for b in ae2_ids]),
        N_BOOT, SEED, "D_position")
    c_pos = classify(lo_pos, hi_pos)
    print(f"  D_position = mean|d|(A222V) - mean(38 A>V elsewhere) = "
          f"{d_pos:+.6f} [{lo_pos:+.6f},{hi_pos:+.6f}] p={pfmt(p_pos)} "
          f"-> {c_pos} (identity held fixed at A>V, position varied)")

    d_grp, lo_grp, hi_grp, p_grp = paired_boot(
        vec_by_bg, ae1_ids + ae2_ids,
        lambda mm: np.mean([mm[b] for b in ae1_ids])
        - np.mean([mm[b] for b in ae2_ids]),
        N_BOOT, SEED, "group-contrast")
    print(f"  DESCRIPTIVE (identity-confounded: 18 non-Val+V vs 38 V): "
          f"mean(19 at 222) - mean(38 A>V elsewhere) = {d_grp:+.6f} "
          f"[{lo_grp:+.6f},{hi_grp:+.6f}] p={pfmt(p_grp)}")

    # ---- frozen combined rule ------------------------------------------
    banner("VERDICT (frozen rule; stated before any number was seen)", "-")
    if c_id == "larger" and c_pos == "larger":
        verdict = ("(i) BOTH factors contribute: A222V exceeds both its "
                   "same-position peers AND A>V elsewhere "
                   "(interaction-like).")
    elif c_id == "indistinguishable" and c_pos == "larger":
        verdict = ("(ii) TRACKS BEING AT 222: A222V does not separate "
                   "from other residues at 222 but does from A>V "
                   "elsewhere.")
    elif c_id == "larger" and c_pos == "indistinguishable":
        verdict = ("(iii) SPECIFIC TO VAL: A222V separates from non-Val "
                   "residues at 222 and is not distinguishable from A>V "
                   "elsewhere — the elevated shift follows the Val "
                   "identity.")
    elif c_id == "indistinguishable" and c_pos == "indistinguishable":
        verdict = ("(iv) NEITHER: A222V separates from neither "
                   "comparator on mean|delta_ESM_b| — the 'outsized' "
                   "premise is not supported for this statistic; "
                   "reported plainly.")
    else:
        verdict = (f"MIXED DIRECTION: D_identity {c_id}, D_position "
                   f"{c_pos} — at least one contrast points the other "
                   f"way; both CIs are printed above, read them as-is "
                   f"(report, don't smooth).")
    print(f"  D_identity: {c_id} | D_position: {c_pos}")
    print(f"  VERDICT: {verdict}")
    print(f"  Task question answered with effect sizes: A222V "
          f"mean|delta| = {m_a222v:.6f} (other-18 median {med18:.6f}, "
          f"A>V-elsewhere median {m38.median():.6f}) — third cell "
          f"(other-Ala, non-Val) unmeasured per task scope, so no full "
          f"two-factor decomposition is claimed.")

    summary.to_csv(OUT_BG, index=False)
    vec.to_csv(OUT_VEC, index=False)
    pd.DataFrame([
        {"contrast": "D_identity", "value": d_id, "ci_lo": lo_id,
         "ci_hi": hi_id, "p_boot": p_id, "classification": c_id},
        {"contrast": "D_position", "value": d_pos, "ci_lo": lo_pos,
         "ci_hi": hi_pos, "p_boot": p_pos, "classification": c_pos},
        {"contrast": "group_mixed_identity", "value": d_grp,
         "ci_lo": lo_grp, "ci_hi": hi_grp, "p_boot": p_grp,
         "classification": classify(lo_grp, hi_grp)},
    ]).to_csv(OUT_CON, index=False)
    print(f"\n  saved {len(summary)} background rows -> {OUT_BG.name}; "
          f"{len(vec)} position-vector rows -> {OUT_VEC.name}; "
          f"3 contrast rows -> {OUT_CON.name}")

    banner("LIMITATIONS (printed with results, AGENTS 6)", "-")
    print(f"""  1. Cell (other-Ala, non-Val) unmeasured (task requests A>V only
     there): full 2x2 decomposition not identifiable; the two frozen
     contrasts each hold exactly one factor fixed.
  2. One-directional scoring S(v|b) only (atlas construction's own
     stated limitation, script 32).
  3. Backgrounds not filtered for atlas measurability (M1's disclosed
     assumption).
  4. Subset = {N_SUB} of a 616-position pool (seed {SEED}); position
     bootstrap quantifies estimation error at FIXED backgrounds, not
     background-sampling variability.
  5. mean|delta| is a magnitude statistic: says nothing about shift
     direction/sign.
  6. A222V arm cross-provenance measured at max|diff| = {maxdiff:.3e}
     vs script 12's saved delta_esm (mixed provenance resolved by
     agreement, G5).""")

    print(f"\nAE1+AE2 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
