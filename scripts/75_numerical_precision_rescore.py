"""
Script 75 (deepdive task AC3) -- numerical-precision rescore of delta_ESM.

TASK (DETECTION_FLOOR_AND_MECHANISM.md, L178-187):
  AC3a. Report delta_ESM's typical magnitude in nats, and the dtype and
        batch size that originally produced it.
  AC3b. Rescore a few hundred variants (reusing the established subset
        convention) in fp32 (and fp64 if feasible), at a different batch
        size, and on CPU instead of the original device. Check whether
        delta_ESM reproduces to the precision the finding actually needs.
        If it does NOT reproduce, that is a more mundane and more urgent
        explanation for 11.1's instability than model-family disagreement,
        and several downstream results would need re-running -- the FAIL
        path of this script prints exactly that.

PRE-DECIDED BEFORE ANY RESCORE RAN (AGENTS Sec6; nothing below was chosen
after seeing a result):

  PRODUCER FACTS (AC3a, verified from source this session, not assumed):
    - scripts/10_score_all_variants_esm2.py:49 (WT background) and
      scripts/11_score_a222v_background_esm2.py:59 (A222V background) both
      call scripts.lib.esm_scoring.get_position_logprobs, which runs ONE
      masked sequence per model() call (lib lines 17-38) inside a loop over
      positions  =>  ORIGINAL BATCH SIZE = 1.
    - No .half()/.bfloat16()/.double()/.float() cast exists anywhere in
      scripts/*.py or scripts/lib/*.py (grep, this session)  =>
      ORIGINAL DTYPE = torch default float32.
    - scripts.lib.esm_scoring.get_device() prefers mps and the original
      runs printed "Using device: mps"  =>  ORIGINAL DEVICE = mps.
    - data/processed/phase5_analysis_table.csv (the delta_ESM source) is
      assembled by scripts/16_phase5_model_abc.py from scripts 10/11's
      outputs; delta_ESM = esm2_score_a222v_bg - esm2_score.

  SUBSET CONVENTION (established, reused literally): seed-0
    np.random.default_rng(SEED).choice(len(pool), size=N_RESAMPLE,
    replace=False) -- the same call script 67's phase-3 (L295-299) and
    script 58 (L207-209) make. "A few hundred variants" read literally as
    N_RESAMPLE=500 (also script 58's matched-set floor of 500).
    Pool = rows with delta_esm AND own_e_b non-null (n=10,757): the
    finding's own primary-CI set. Reconciliation of the two n's seen in
    this repo (AGENTS Sec5): 11,344 = delta_esm-only (script 67's print);
    10,757 = delta_esm AND own_e_b (what position_cluster_bootstrap drops
    to, hence task32's n_rows) -- verified this session by re-merging.

  CONDITIONS (ALL forced to CPU; original device was mps):
    C0: fp32, batch 1   -- isolates the device change alone (mps -> cpu)
    C1: fp32, batch 8   -- the task's literal ask: fp32 + different batch + CPU
    C2: fp32, batch 16  -- batch-size refinement
    C3: fp64, batch 8   -- dtype refinement ("fp64 if feasible", gated below)

  GATES:
    G1 (implementation identity; STOP on failure): this script's batched
      masked-marginal vs scripts.lib.esm_scoring.get_position_logprobs on
      the same CPU fp32 model, first min(10, N_RESAMPLE) variants x 2
      contexts: max|diff| < 1e-5. On failure: print the exact mismatch and
      sys.exit(1) -- no retry, no raised threshold, no bigger N (AGENTS).
    R1 (value precision): for every condition that runs,
      max|delta_cond - delta_cached| <= 1.0e-3 nats.
      Rationale: 2.1% of the pool's median |delta_ESM| = 0.0465, and
      ~1,126x the float32 rounding floor 8.885e-07 (task_delta_esm_
      noise_floor.csv). An effect with sd=0.118 nats cannot be carried by
      errors at the 1e-3 scale.
    R2 (finding precision, PAIRED on the same sampled rows):
      |Spearman(delta_cond, own_e_b) - Spearman(delta_cached, own_e_b)|
      <= 0.01. Rationale: the published clustered CI half-width is 0.029
      (task32_delta_esm_primary.csv), so rescore-induced movement of rho
      must stay under one third of it. Pairing removes subset sampling
      noise; only value changes can move this number.
    PASS = G1 and R1 and R2 all hold. FAIL prints the AC3 consequence
      plainly (downstream re-runs would be needed).
    Informational, not gated: condition-vs-condition max|diff|, and
      Spearman(delta_cond, delta_cached).

  fp64 FEASIBILITY TIERS (pre-registered, "fp64 if feasible"): time the
    first 8 variants in fp64; (a) projected full-N <= FP64_MAX_PROJ_S
    (default 7200 s) -> full N; (b) else if projected at N=100 <= that cap
    -> fp64 on the first 100 sampled variants, disclosed; (c) else skip
    fp64 entirely and print the measured timing + projection as the
    feasibility determination, disclosed.
  fp32 ARM-DROP TIER (pre-registered): if the 8-variant timing smoke
    projects C0+C1+C2 together above FP32_MAX_PROJ_S (default 7200 s),
    arms are dropped from the tail (C2 first, then C0) until the projection
    fits, each drop printed; C1 always runs.

ENV: N_RESAMPLE (default 500), FP32_MAX_PROJ_S (7200), FP64_MAX_PROJ_S
(7200). Run smoke-first: N_RESAMPLE=8.

OUTPUT: data/processed/task_AC3_rescore.csv + stdout (quoted into
DEEPDIVE_LOG's [AC3] entry).

  REVISION AFTER THE N=8 SMOKE, BEFORE ANY FULL RUN (disclosed, AGENTS Sec6):
    (1) The smoke exposed that scoring one two-row batch per variant never
        reached the labeled batch sizes -- C1 ("b8") and C2 ("b16") both
        ran as batch-of-2 (their smoke pairwise max|diff| was exactly
        0.000e+00, the tell), making the batch arm vacuous beyond 1-vs-2.
        Fixed BEFORE the full run: each condition now scores the whole
        wt-block and bg-block across variants at its true batch size
        (1/8/16 sequences per forward). No gate, threshold, condition
        label, N, subset convention, or decision rule changed; smoke
        numbers are superseded by the full-run numbers.
    (2) The smoke's projection line multiplied by len(smoke) and was
        labeled "full" -- it projected the smoke's own arms at N=8, not the
        canonical full run (I mis-read it as N=500 and chose a too-short
        harness timeout; that first N=500 attempt was killed at 30 min
        with its output lost). Projections now use the canonical
        FULL_N=500 and say so; tier thresholds (7,200 s) unchanged.
    Both fixes were made before any N=500 rescore value existed.
    (3) Attempt 2 (G1 PASS; all three fp32 arms finished; fp64 tier (a)
        decided) was then interrupted mid-fp64-arm at ~48 min, and because
        values were held in memory only, everything was lost. Per-chunk
        checkpointing + resume was added (task_AC3_rescore.csv written
        every AC3_CHUNK=100 variants, task_AC3_state.json persists the
        sample and the fp64 tier decision). This is execution machinery
        only -- same conditions, order, thresholds, N, and gates; it
        bounds any future interruption's loss to one chunk. RESUME-mode
        prints are expected on re-invocation and are not a result.
    (4) Attempt 3 (the first full N=500 completion) exposed a stale-state
        bug: the N=8 smoke's stored fp64 tier (n=8) was reused for the
        500-row sample because state.json's sample_hgvs was refreshed on
        mismatch while fp64_n was not reset -- so the fp64 arm silently
        ran only 8 of 500 rows while the run still printed a combined
        PASS line. The giveaways in that output: C3's printed
        "|d-rho_base| = 0.3823" (8-row rho vs the 500-row baseline) and
        the C3 timing trace "n=8". Fixes, all machinery: (a) sample
        mismatch now discards state entirely; (d) a stored tier/n is
        validated against the current sample before reuse (tier a must
        equal len(sub)); (b) the comparison print now shows the paired
        same-row |d rho| and n_ok per condition, so partial coverage
        cannot hide; (c) a post-hoc COVERAGE gate requires each planned
        arm's row count to match its pre-registered coverage BEFORE any
        verdict is issued (added after seeing attempt 3 -- it can only
        block a false PASS; it changes no threshold or statistic).
        Attempt 3's verdict line is therefore NOT the AC3 result; only a
        run that passes the COVERAGE gate is. Disclosure: resume chunks
        start at the first NaN rather than a CHUNK boundary, so rows at a
        resumed chunk junction can sit in a differently-composed batch
        than in an uninterrupted run (fp64 reduction-order effects,
        ~1e-14 scale here -- 11 orders below the 1e-3 gate).
    (5) Attempt 4 completed every condition's data (all four arms
        n_ok=500/500 in its comparison block) but the new COVERAGE gate
        then refused the verdict due to an unpack bug IN THE GATE ITSELF:
        `for name in arms` iterated (name, batch) tuples, so expected keys
        were tuples and cov.get(tuple) returned 0 for the three fp32 arms.
        Fixed to `for name, _ in arms`. The gate's design intent (block a
        verdict unless every planned arm has its full pre-registered row
        count) and threshold are unchanged; attempt 4's own comparison
        block already showed n_ok=500/500 for all four conditions, which
        is the evidence that this was a key-type bug and not missing data.

LIMITATIONS (stated here, not only in the writeup): one model load per
dtype; cached deltas were produced by scripts 10/11 earlier in this same
repository -- if the installed torch/fair-esm versions changed since, part
of any device-term would be library-version drift, which this check
cannot separate (disclosed); CPU-vs-MPS compares implementations, not
rounding alone; the thresholds above were fixed before any rescore value
existed.
"""
import sys, os, re, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import torch
import esm

from scripts.lib.esm_scoring import get_position_logprobs, AA_LIST
from scripts.lib.sequence import load_sequence

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FULL_N = 500   # canonical full-run target for projections/gates
N_RESAMPLE = int(os.environ.get("N_RESAMPLE", FULL_N))
FP32_MAX = float(os.environ.get("FP32_MAX_PROJ_S", 7200))
FP64_MAX = float(os.environ.get("FP64_MAX_PROJ_S", 7200))
SEED = 0

THREE_TO_ONE = {
    "Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
    "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
    "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
    "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V",
}
HGVS_RX = re.compile(r"^p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})$")

MASK = "<mask>"


def mask_at(seq, idx0):
    return seq[:idx0] + MASK + seq[idx0 + 1:]


def batched_odds(alphabet, bc, model, rows, device, batch_size):
    """rows: list of (masked_seq, var_aa, ref_aa) -> list of
    logP(var) - logP(ref) at the masked position, native dtype."""
    out = []
    for s in range(0, len(rows), batch_size):
        chunk = rows[s:s + batch_size]
        _, _, tokens = bc([(f"q{i}", m) for i, (m, _, _) in enumerate(chunk)])
        tokens = tokens.to(device)
        with torch.no_grad():
            logits = model(tokens, repr_layers=[], return_contacts=False)["logits"]
        lp = torch.log_softmax(logits, dim=-1)
        for r, (m, var, ref) in enumerate(chunk):
            idx0 = m.index(MASK)
            tpos = idx0 + 1
            vi = alphabet.get_idx(var)
            wi = alphabet.get_idx(ref)
            out.append(float(lp[r, tpos, vi] - lp[r, tpos, wi]))
    return out


def score_deltas(alphabet, bc, model, wt_rows, bg_rows, device, batch_size):
    """wt_rows/bg_rows: aligned lists of (masked_seq, var_aa, ref_aa) for the
    WHOLE block; each block is scored at exactly batch_size sequences per
    forward, then delta = bg-odds - wt-odds elementwise."""
    ow = batched_odds(alphabet, bc, model, wt_rows, device, batch_size)
    ob = batched_odds(alphabet, bc, model, bg_rows, device, batch_size)
    return np.asarray(ob, dtype=float) - np.asarray(ow, dtype=float)


def spearman(a, b):
    return pd.Series(a).corr(pd.Series(b), method="spearman")


if __name__ == "__main__":
    t_start = time.perf_counter()
    print(f"Script 75 (AC3) | N_RESAMPLE={N_RESAMPLE} SEED={SEED} "
          f"FP32_MAX_PROJ_S={FP32_MAX:.0f} FP64_MAX_PROJ_S={FP64_MAX:.0f}")
    device = torch.device("cpu")
    print(f"Using device: {device} (FORCED -- original producer device was mps)")

    # ---------------- AC3a report (from disk + code-verified facts) -------
    nf = pd.read_csv(PROC / "task_delta_esm_noise_floor.csv").iloc[0]
    d5 = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    d5 = d5.merge(own, on="hgvs_pro", how="left")
    pool = d5[d5["delta_esm"].notna() & d5["own_e_b"].notna()].copy()
    print("\nAC3a -- delta_ESM magnitude (nats) and original producer settings:")
    print(f"  n reconciliation: delta_esm non-null = {d5['delta_esm'].notna().sum()}  |  "
          f"delta_esm AND own_e_b (primary-CI pool) = {len(pool)} "
          f"({pool['position'].nunique()} positions)")
    print(f"  median |delta_ESM| (noise-floor file, n=11,344 set) = {nf['median_abs_delta']:.15f}")
    print(f"  median |delta_ESM| (this pool, n={len(pool)})          = {pool['delta_esm'].abs().median():.15f}")
    print(f"  sd(delta_ESM) = {nf['sd_delta_esm']:.15f}   sd(esm2_score) = {nf['sd_esm2_score']:.15f}")
    print(f"  float32 rounding floor eps*mean|score| = {nf['float32_floor']:.6e}   "
          f"sd/floor = {nf['sd_over_floor']:.1f}   frac |delta|<1e-4 = {nf['frac_below_1e4']:.6f}")
    print("  ORIGINAL DTYPE = float32 (torch default; no .half()/.bfloat16()/.double()/.float()")
    print("    cast exists anywhere in scripts/*.py or scripts/lib/*.py -- grep this session)")
    print("  ORIGINAL BATCH SIZE = 1 (scripts/10:49 and scripts/11:59 call lib")
    print("    get_position_logprobs, which runs ONE masked sequence per model() call -- lib L17-38)")
    print("  ORIGINAL DEVICE = mps (lib get_device() prefers mps; original runs printed")
    print("    'Using device: mps')   producer of phase5_analysis_table.csv: scripts/16")

    # ---------------- subset (established convention, literal) ------------
    rng = np.random.default_rng(SEED)
    pool = pool.reset_index(drop=True)
    idx = rng.choice(len(pool), size=min(N_RESAMPLE, len(pool)), replace=False)
    sub = pool.iloc[np.sort(idx)].copy().reset_index(drop=True)
    print(f"\nSUBSET: {len(sub)} variants, {sub['position'].nunique()} positions "
          f"(default_rng({SEED}).choice over the {len(pool)}-row pool, replace=False "
          f"-- script-67/script-58 convention)")

    # ---- checkpoint / resume state (machinery only; see REVISION (3)) -----
    STATE_PATH = PROC / "task_AC3_state.json"
    CKPT_PATH = PROC / "task_AC3_rescore.csv"
    base = sub[["hgvs_pro", "position", "own_e_b", "delta_esm"]].copy()
    state, results, resume = {}, {}, False
    if STATE_PATH.exists() and CKPT_PATH.exists():
        try:
            state = json.loads(STATE_PATH.read_text())
            prev = pd.read_csv(CKPT_PATH)
            if list(prev.get("hgvs_pro", [])) == list(sub["hgvs_pro"]):
                resume = True
                results = {c: prev[c].to_numpy(dtype=float).copy()
                           for c in prev.columns
                           if c.startswith(("C0_", "C1_", "C2_", "C3_"))}
                done = [c for c in results
                        if not np.isnan(results[c]).any()]
                print(f"RESUME mode: checkpoint matches this sample "
                      f"({len(results)} column(s), complete: {done or 'none'}; "
                      f"conditions/thresholds unchanged -- machinery only)")
            else:
                print("Checkpoint sample MISMATCH -- discarding it, fresh run")
                state = {}
        except Exception as e:  # unreadable checkpoint -> fresh, disclosed
            print(f"Checkpoint unreadable ({e}) -- fresh run")
    # (d) validate any stored fp64 tier/n against THIS sample before reuse:
    # attempt 3's stale n=8 survived a sample change because only
    # sample_hgvs was refreshed (REVISION (4) below).
    _fn, _tier = state.get("fp64_n"), state.get("fp64_tier")
    if _fn is not None:
        _ok_n = ((_tier == "a" and _fn == len(sub))
                 or (_tier == "b" and _fn == min(100, len(sub)))
                 or (_tier == "c" and _fn == 0))
        if not _ok_n:
            print(f"STALE fp64 tier state (tier={_tier!r}, n={_fn}, "
                  f"len(sub)={len(sub)}) -- discarding; tier will be "
                  f"re-decided (machinery fix, docstring REVISION (4))")
            state.pop("fp64_n", None)
            state.pop("fp64_tier", None)
    state["sample_hgvs"] = list(sub["hgvs_pro"])
    STATE_PATH.write_text(json.dumps(state))
    CHUNK = int(os.environ.get("AC3_CHUNK", 100))

    def write_ckpt():
        out = base.copy()
        for name in ("C0_fp32_b1", "C1_fp32_b8", "C2_fp32_b16", "C3_fp64_b8"):
            if name in results:
                out[name] = results[name]
        out.to_csv(CKPT_PATH, index=False)

    # parse hgvs -> wt/var 1-letter; sanity: wt must match the FASTA residue
    wt_seq = load_sequence(ROOT / "data" / "raw" / "P42898.fasta")
    assert wt_seq[221] == "A", f"P42898 position 222 is {wt_seq[221]!r}, expected A"
    bg_seq = wt_seq[:221] + "V" + wt_seq[222:]
    parse_fail = wt_mismatch = var_is_wt = 0
    wt_aas, var_aas, poss = [], [], []
    for h in sub["hgvs_pro"]:
        m = HGVS_RX.match(str(h))
        if not m:
            parse_fail += 1
            wt_aas.append(None); var_aas.append(None); poss.append(None)
            continue
        w3, p1, v3 = m.group(1), int(m.group(2)), m.group(3)
        w1, v1 = THREE_TO_ONE.get(w3), THREE_TO_ONE.get(v3)
        if w1 is None or v1 is None or wt_seq[p1 - 1] != w1:
            wt_mismatch += 1
        if w1 == v1:
            var_is_wt += 1
        wt_aas.append(w1); var_aas.append(v1); poss.append(p1)
    sub["wt_aa"], sub["var_aa"], sub["pos1"] = wt_aas, var_aas, poss
    print(f"hgvs parse: fail={parse_fail}  wt-vs-FASTA mismatch={wt_mismatch}  var==wt={var_is_wt}")
    assert parse_fail == 0 and wt_mismatch == 0 and var_is_wt == 0, "hgvs/FASTA sanity failed"
    bad_pos = int((sub["pos1"].astype(int) != sub["position"].astype(int)).sum())
    print(f"hgvs position vs table position mismatches: {bad_pos}")
    assert bad_pos == 0, "position mismatch between hgvs_pro and table"

    # ---------------- model load ------------------------------------------
    print("\nLoading ESM-2 t33 650M (esm2_t33_650M_UR50D, cached -- no download)...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    bc = alphabet.get_batch_converter()

    def build_rows(pos_list, var_list):
        rows = []
        for p, v in zip(pos_list, var_list):
            i = int(p) - 1
            rows.append((mask_at(wt_seq, i), v, wt_seq[i]))
            rows.append((mask_at(bg_seq, i), v, bg_seq[i]))
        return rows

    n_g1 = min(10, len(sub))
    g1_rows = build_rows(sub["pos1"].iloc[:n_g1], sub["var_aa"].iloc[:n_g1])
    mine = batched_odds(alphabet, bc, model, g1_rows, device, batch_size=8)
    libv = []
    for j in range(n_g1):
        p = int(sub["pos1"].iloc[j]); v = sub["var_aa"].iloc[j]
        d_wt = get_position_logprobs(model, alphabet, bc, wt_seq, p, device)
        d_bg = get_position_logprobs(model, alphabet, bc, bg_seq, p, device)
        libv.extend([d_wt[v], d_bg[v]])
    g1_max = max(abs(a - b) for a, b in zip(mine, libv))
    print(f"\nG1 identity gate (batched CPU fp32 vs lib get_position_logprobs, "
          f"{n_g1} variants x 2 ctx): max|diff| = {g1_max:.3e}  (threshold 1e-5)")
    if not g1_max < 1e-5:
        print(f"G1 FAIL: max|diff| = {g1_max:.6e} >= 1e-5 -- STOP (no retry, no threshold change)")
        sys.exit(1)
    print("G1 PASS")

    # ---------------- timing smoke + fp32 arm-drop gate --------------------
    smoke_n = min(8, len(sub))
    wt_rows = [(mask_at(wt_seq, int(p) - 1), v, wt_seq[int(p) - 1])
               for p, v in zip(sub["pos1"], sub["var_aa"])]
    bg_rows = [(mask_at(bg_seq, int(p) - 1), v, bg_seq[int(p) - 1])
               for p, v in zip(sub["pos1"], sub["var_aa"])]
    t0 = time.perf_counter()
    _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n], bg_rows[:smoke_n],
                     device, 8)
    t32 = (time.perf_counter() - t0) / smoke_n
    arms = [("C0_fp32_b1", 1), ("C1_fp32_b8", 8), ("C2_fp32_b16", 16)]
    proj32_full = t32 * FULL_N * len(arms)
    print(f"\nTIMING SMOKE (fp32, batch 8, n={smoke_n}): {t32:.3f} s/variant -> "
          f"projected C0+C1+C2 at full N={FULL_N} = {proj32_full:.0f} s "
          f"(cap {FP32_MAX:.0f})")
    while arms and (t32 * FULL_N * len(arms)) > FP32_MAX:
        dropped, arms = arms[-1], arms[:-1]
        print(f"  ARM-DROP TIER: dropped {dropped} to fit the fp32 projection cap "
              f"(remaining {len(arms)} arm(s) project "
              f"{t32 * FULL_N * len(arms):.0f} s at full N={FULL_N})")
    assert arms, "even C1 alone exceeds the fp32 projection cap -- STOP"

    # ---------------- run fp32 arms (chunked, checkpointed, resumable) -----
    arm_times = {}
    for name, bsz in arms:
        if name in results and not np.isnan(results[name]).any():
            print(f"  {name}: already complete in checkpoint (resume) -- skipped")
            continue
        vals = results.get(name, np.full(len(sub), np.nan))
        nan_idx = np.where(np.isnan(vals))[0]
        start = int(nan_idx[0]) if len(nan_idx) else len(sub)
        if start > 0:
            print(f"  {name}: resuming from variant {start}/{len(sub)}")
        t0 = time.perf_counter()
        for s in range(start, len(sub), CHUNK):
            e = min(s + CHUNK, len(sub))
            vals[s:e] = score_deltas(alphabet, bc, model,
                                     wt_rows[s:e], bg_rows[s:e], device, bsz)
            results[name] = vals
            write_ckpt()
            print(f"    {name}: {e}/{len(sub)} checkpointed "
                  f"@ {time.strftime('%H:%M:%S')}", flush=True)
        arm_times[name] = time.perf_counter() - t0
        n_this = max(len(sub) - start, 1)
        print(f"  {name}: {arm_times[name]:.1f} s this invocation "
              f"({arm_times[name] / n_this:.3f} s/variant)")

    # ---------------- fp64 feasibility tiers (stored decision = resume) -----
    t64 = None
    c3 = results.get("C3_fp64_b8")
    c3_have = (state.get("fp64_n") is not None and c3 is not None
               and int(np.count_nonzero(~np.isnan(c3))) >= int(state["fp64_n"]))
    if c3_have:
        print(f"\nC3_fp64_b8: already complete in checkpoint (resume, "
              f"n={state['fp64_n']}, tier {state.get('fp64_tier', '?')}) -- skipped")
    elif FP64_MAX > 0:
        t0 = time.perf_counter()
        _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n], bg_rows[:smoke_n],
                         device, 8)
        t32_b8 = (time.perf_counter() - t0) / smoke_n
        model = model.double()
        t0 = time.perf_counter()
        _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n], bg_rows[:smoke_n],
                         device, 8)
        t64 = (time.perf_counter() - t0) / smoke_n
        proj64_full = t64 * FULL_N
        proj64_100 = t64 * 100
        print(f"\nTIMING SMOKE fp64 (batch 8, n={smoke_n}): {t64:.3f} s/variant "
              f"(fp32 same-config {t32_b8:.3f} s/variant, fp64/fp32 = {t64 / t32_b8:.2f}x) "
              f"-> projected at full N={FULL_N} = {proj64_full:.0f} s, at N=100 = "
              f"{proj64_100:.0f} s (cap {FP64_MAX:.0f})")
        if state.get("fp64_n") is not None:
            fp64_n = int(state["fp64_n"])
            print(f"  fp64 tier: reusing stored decision from prior invocation "
                  f"(tier {state.get('fp64_tier', '?')}, n={fp64_n}) -- not re-decided")
        elif proj64_full <= FP64_MAX:
            fp64_n = len(sub)
            state["fp64_tier"] = "a"
            print("  fp64 tier (a): FULL N")
        elif proj64_100 <= FP64_MAX:
            fp64_n = min(100, len(sub))
            state["fp64_tier"] = "b"
            print(f"  fp64 tier (b): N=100 only -- full-N projection {proj64_full:.0f} s "
                  f"> cap {FP64_MAX:.0f} -- DISCLOSED reduced-N fp64 arm")
        else:
            fp64_n = 0
            state["fp64_tier"] = "c"
            print(f"  fp64 tier (c): SKIPPED -- even N=100 projects {proj64_100:.0f} s "
                  f"> cap {FP64_MAX:.0f} -- feasibility determination: NOT feasible "
                  f"(measured {t64:.3f} s/variant), DISCLOSED")
        state["fp64_n"] = fp64_n
        STATE_PATH.write_text(json.dumps(state))
        if fp64_n > 0:
            vals64 = (c3 if c3 is not None
                      else np.full(len(sub), np.nan))
            start = int(np.count_nonzero(~np.isnan(vals64)))
            if start > 0:
                print(f"  C3_fp64_b8: resuming from variant {start}/{fp64_n}")
            t0 = time.perf_counter()
            for s in range(start, fp64_n, CHUNK):
                e = min(s + CHUNK, fp64_n)
                vals64[s:e] = score_deltas(alphabet, bc, model,
                                           wt_rows[s:e], bg_rows[s:e], device, 8)
                results["C3_fp64_b8"] = vals64
                write_ckpt()
                print(f"    C3_fp64_b8: {e}/{fp64_n} checkpointed "
                      f"@ {time.strftime('%H:%M:%S')}", flush=True)
            print(f"  C3_fp64_b8: {time.perf_counter() - t0:.1f} s this invocation "
                  f"(n={fp64_n})")
            write_ckpt()

    # ---------------- comparisons -----------------------------------------
    cached = sub["delta_esm"].to_numpy()
    own_eb = sub["own_e_b"].to_numpy()
    rho_base = spearman(cached, own_eb)
    print(f"\nSpearman(delta_cached, own_e_b) on these {len(sub)} rows (baseline): "
          f"rho = {rho_base:+.4f}   [full-set published: -0.088118, CI [-0.117333,-0.059511]]")

    verdicts = {}
    for name, vals in results.items():
        v = np.asarray(vals, dtype=float)
        if np.isnan(v).all():
            continue
        ok = ~np.isnan(v)
        diff = np.abs(v[ok] - cached[ok])
        r1 = float(diff.max()) <= 1e-3
        rho_c = spearman(v[ok], own_eb[ok])
        rho_pair = spearman(cached[ok], own_eb[ok])
        r2 = abs(rho_c - rho_pair) <= 0.01
        rank_agree = spearman(v[ok], cached[ok])
        verdicts[name] = (r1, r2)
        print(f"  {name}: max|d-cached| = {diff.max():.3e}  median = {np.median(diff):.3e} "
              f"rmse = {np.sqrt((diff ** 2).mean()):.3e} | rho(own_e_b) = {rho_c:+.4f} "
              f"n_ok = {int(ok.sum())}/{len(sub)} | paired |d rho| vs cached on same "
              f"rows = {abs(rho_c - rho_pair):.4f} | rho vs cached = {rank_agree:+.6f} "
              f"| R1 {'PASS' if r1 else 'FAIL'} (<=1e-3), R2 {'PASS' if r2 else 'FAIL'} (<=0.01)")

    # pairwise condition-vs-condition (informational)
    names = [n for n in results if not np.isnan(np.asarray(results[n], dtype=float)).all()]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = np.asarray(results[names[i]], dtype=float)
            b = np.asarray(results[names[j]], dtype=float)
            ok = ~np.isnan(a) & ~np.isnan(b)
            print(f"  pairwise {names[i]} vs {names[j]}: max|diff| = {np.abs(a[ok] - b[ok]).max():.3e}")

    # ---- COVERAGE gate (post-hoc guard, disclosed): added after attempt 3's
    # stale-fp64_n bug let an 8-row fp64 arm print alongside a combined
    # PASS. Can only block a false PASS; changes no threshold or statistic.
    expected_cov = {name: len(sub) for name, _ in arms}
    if "C3_fp64_b8" in results and state.get("fp64_n") is not None:
        expected_cov["C3_fp64_b8"] = int(state["fp64_n"])
    cov = {name: int(np.sum(~np.isnan(np.asarray(results[name], dtype=float))))
           for name in results}
    bad_cov = {k: (cov.get(k, 0), expected_cov[k])
               for k in expected_cov if cov.get(k, 0) != expected_cov[k]}
    if bad_cov:
        print("\nCOVERAGE FAIL (post-hoc guard): (rows run, pre-registered "
              f"coverage) = {bad_cov} -- conditions incomplete; NO verdict "
              "issued. Re-run to resume the incomplete condition(s).")
        sys.exit(1)

    # pairwise condition-vs-cached rho table already printed; verdict:
    r1_all = all(v[0] for v in verdicts.values())
    r2_all = all(v[1] for v in verdicts.values())
    overall = r1_all and r2_all
    print("\n" + "=" * 74)
    print(f"R1 (value, all conditions <= 1e-3): {'PASS' if r1_all else 'FAIL'}")
    print(f"R2 (finding, paired |rho shift| <= 0.01): {'PASS' if r2_all else 'FAIL'}")
    if overall:
        print("AC3 VERDICT: PASS -- delta_ESM reproduces under CPU/fp32/batch/fp64 changes "
              "to the precision the finding needs (G1+R1+R2).")
    else:
        print("AC3 VERDICT: FAIL -- delta_ESM does NOT reproduce to the precision the "
              "finding needs.")
        print("  Per AC3b's own text: this would be a more mundane and more urgent "
              "explanation for 11.1's instability than model-family disagreement, and "
              "several downstream results would need re-running. DO NOT quote any "
              "downstream number as safe until this is resolved.")
    print("=" * 74)

    write_ckpt()
    print(f"Saved to {CKPT_PATH} (columns: "
          f"{[c for c in results]})")

    print("\nLIMITATIONS (stated in the script's own output):")
    print("  * Cached deltas were produced by scripts 10/11 earlier in this repository;")
    print("    torch/fair-esm version drift since then would masquerade as a device-term")
    print("    and cannot be separated here (disclosed).")
    print("  * CPU-vs-MPS compares implementations, not rounding alone.")
    print("  * Thresholds (G1 1e-5, R1 1e-3, R2 0.01) were fixed before any rescore")
    print("    value existed; no threshold was changed after seeing a result.")
    print(f"  * Total runtime {time.perf_counter() - t_start:.1f}s.")
