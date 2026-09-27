"""
Script 103 (true-final-closeout task G2a) -- AC3's exact precision/hardware
grid (script 75's machinery) applied to the five ESM-1v members' cached
delta columns (script 86's producers).

TASK (docs/tasks/true-final-closeout/TRUE_FINAL_CLOSEOUT.md, L21-28):
  G2a. Run the exact same precision/hardware grid used for the original
       ESM-2 delta check (dtype, batch size, device -- reuse that script's
       exact machinery, do not rewrite it) on the five ESM-1v checkpoints'
       delta scores. Report whether they reproduce to the same tolerance
       the original check used.

PRE-DECIDED BEFORE ANY G2 RESCORE VALUE EXISTED (AGENTS Sec 6):

  WHAT IS REUSED, BY IMPORT, VERBATIM (never re-typed):
    - scripts/75_numerical_precision_rescore.py is loaded as a module
      (importlib from file; its whole body lives under
      `if __name__ == "__main__"`, so loading executes only its
      constants + function definitions): batched_odds, score_deltas,
      mask_at, spearman, MASK, HGVS_RX, THREE_TO_ONE, SEED -- i.e. the
      entire scoring path and all conventions.
    - scripts/lib/esm_scoring.get_position_logprobs (script 75's own G1
      reference implementation) and AA_LIST.
    - scripts/86_ac4_esm1v_five_members.hf_fetch: the member-weight
      download with its size gate (EXPECTED_BIN = 2,609,603,341 B), md5
      provenance, disk gate and one-member-at-a-time staging discipline.
  WHAT IS NEW, EACH ITEM DISCLOSED:
    - HFAdapter (~8 lines): lets a Transformers EsmForMaskedLM answer
      script 75's fair-esm call signature
      `model(tokens, repr_layers=[], return_contacts=False)["logits"]`
      plus .eval()/.double(). Pure pass-through; no math is added.
    - TOK gate: fair-esm batch_converter token ids must equal the HF
      tokenizer's input_ids on EVERY sampled masked sequence in BOTH
      contexts. Rationale: script 86's producer tokenized with the HF
      tokenizer (script 86 L264); a silent tokenizer mismatch would
      invalidate every comparison. It can only block a wrong PASS; it
      changes no statistic and no threshold. (A design-time probe on a
      106-token sequence showed identical ids; this gate re-checks every
      sampled sequence on every model load.)
    - Data prep (pool, sample, hgvs parse, assert set) re-derived
      literally from script 75 L234-237 / L255-259 / L313-337, and the
      fp32 arm-drop / fp64 tier decision blocks follow script 75
      L380-390 / L425-460 -- those lines sit inside script 75's __main__
      and cannot be imported; they are re-typed with the same caps
      (7200 s) and the same tier names.
    - Checkpoint layout: one CSV per member + one state JSON, written
      after every chunk (same discipline as script 75's write_ckpt).

  PRODUCER FACTS for the cached columns (scripts/86, read this session):
    task_AC4_esm1v_member{k}_scores.csv -- 12,446 rows / 655 positions;
    `delta = av_logodds - wt_logodds` (script 86 L344) from
    masked_marginal_tf (L258-272): HF EsmForMaskedLM facebook/
    esm1v_t33_650M_UR90S_{k}, ONE masked sequence per forward (batch 1),
    torch default fp32, device = lib get_device() (mps-preferred),
    HF tokenizer. The wt/av merge is OUTER (L343), leaving exactly two
    NaN deltas ((222,A,A) and (222,A,V)); position 222 has 0 rows in
    this script's pool (verified before any scoring, this session), and
    any NaN-after-join row would be counted and its rows excluded from
    that member's R1/R2 with disclosure (verified pre-run: 0 for all
    five members at the default sample).

  GRID (identical to AC3, script 75 L230 / L380): device FORCED cpu;
  C0_fp32_b1 (device change alone), C1_fp32_b8 (batch, producer-conformant
  sequence count), C2_fp32_b16 (batch refinement), C3_fp64_b8 (dtype).

  THRESHOLDS (identical to AC3; fixed before any rescore value existed):
    G1 identity gate: batched vs lib get_position_logprobs, max|diff|
      < 1e-5 (script 75 L365);
    R1 value gate: max|rescore - cached| <= 1e-3 (script 75 L495);
    R2 finding gate: paired |Spearman(cond, own_e_b) -
      Spearman(cached, own_e_b)| <= 0.01 (script 75 L496-498).
    Each applied PER MEMBER PER CONDITION (5 x 4 = 20 R1 + 20 R2
    verdicts). Overall PASS iff every TOK and G1 gate passes, coverage
    is full, and all 40 verdicts pass.

  SAMPLE: script 75's exact pool (phase5 rows with delta_esm AND
  own_e_b non-null: 10,757 rows / 654 positions) and its seed-0
  rng.choice convention; N = env N_RESAMPLE, default 100. N=100 rather
  than AC3's 500 is a TIMING decision recorded here BEFORE any gate
  result existed: AC3's measured per-member cost at N=500 was
  919.7 + 937.7 + 948.6 s (three fp32 arms) + 3219.3 s (fp64) = 6025 s
  (DEEPDIVE_LOG L1597-1614) -> five members ~8.4 h, incompatible with
  this session's short-closeout mandate; at N=100 the same measurements
  project ~100 min of scoring for all five members. N=100 is also AC3's
  own pre-registered fp64 tier-(b) size. THE TOLERANCES ARE UNCHANGED;
  only the sample size differs, disclosed here in the script's own
  docstring. If the SMOKE projection exceeds 2.5 h, a smaller
  N_RESAMPLE may be used instead and must be logged as timing-driven --
  no R1/R2 value may exist at the time of any such reduction.

  fp64 feasibility ladder: same as script 75 (tier a = full N if the
  projection <= FP64_MAX_PROJ_S, default 7200 s; else tier b =
  min(100, N) -- which collapses onto tier a at N=100 --; else tier c =
  skip, feasibility determination NOT feasible, DISCLOSED). fp32
  arm-drop ladder: same while-loop as script 75 (drop C2, then C1) to
  fit FP32_MAX_PROJ_S (default 7200 s).

  NO bootstrap, NO permutation, NO p-values: this is a deterministic
  numerical-reproducibility grid (AC3 had none either).

ENV: N_RESAMPLE (default 100), SMOKE=1 (load member 1, run TOK + G1 +
timing smokes, exit before any arm; staged weights are KEPT for the
full run), G2_CHUNK (default 50), FP32_MAX_PROJ_S, FP64_MAX_PROJ_S.

LIMITATIONS (printed at runtime too, AGENTS Sec 6):
  - Version drift: the cached columns were produced by script 86 under
    whatever torch/transformers were installed then; this run prints its
    versions, and drift would masquerade as a device/batch term and
    cannot be separated here (disclosed).
  - CPU-vs-MPS compares implementations, not rounding alone; the
    producer's mps/batch-1/fp32 origin and the grid's CPU conditions are
    not separable from each other (same caveat as AC3).
  - Asymmetric with AC3: AC3's grid model was fair-esm ESM-2, the same
    library that produced the cached ESM-2 deltas; here the grid model
    is the SAME Transformers library that produced the cached ESM-1v
    columns (closer to the producer), with fair-esm used only for
    tokenization and alphabet (gated by TOK on every load).
  - R1/R2 are computed on the N-row sample, not on all 12,446 cached
    rows; rho baselines printed per member are SAMPLE baselines, not
    the published full-set five-member rhos (T1a) or the ensemble rho.
  - Member weights were deleted after script 86's run; this script
    re-downloads each member (2.6 GB, staged one at a time) and deletes
    it after that member's arms complete, so re-running an incomplete
    member re-fetches it (complete members are skipped with no fetch).
"""
import importlib.util
import json
import shutil
import sys
import os
import time
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


def _load_module(name, path):
    """Literal reuse: load a sibling script as a module (its __main__
    guard keeps side effects out; AGENTS Sec 7 -- reuse, never rewrite)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AC3 = _load_module("ac3_grid", ROOT / "scripts" / "75_numerical_precision_rescore.py")
AC4 = _load_module("ac4_fetch", ROOT / "scripts" / "86_ac4_esm1v_five_members.py")

mask_at = AC3.mask_at
batched_odds = AC3.batched_odds
score_deltas = AC3.score_deltas
spearman = AC3.spearman
MASK = AC3.MASK
HGVS_RX = AC3.HGVS_RX
THREE_TO_ONE = AC3.THREE_TO_ONE
SEED = AC3.SEED
hf_fetch = AC4.hf_fetch

N_RESAMPLE = int(os.environ.get("N_RESAMPLE", "100"))
SMOKE = os.environ.get("SMOKE", "") == "1"
CHUNK = int(os.environ.get("G2_CHUNK", "50"))
FP32_MAX = float(os.environ.get("FP32_MAX_PROJ_S", "7200"))
FP64_MAX = float(os.environ.get("FP64_MAX_PROJ_S", "7200"))
STATE_PATH = PROC / "task_G2_state.json"
OUT_PATH = PROC / "task_G2_esm1v_rescore.csv"
ARMS32 = [("C0_fp32_b1", 1), ("C1_fp32_b8", 8), ("C2_fp32_b16", 16)]


def member_csv_path(k):
    return PROC / f"task_G2_member{k}_rescore.csv"


class HFAdapter:
    """Pass-through shim so script 75's fair-esm-style calls
    `model(tokens, repr_layers=[], return_contacts=False)["logits"]`
    drive a Transformers EsmForMaskedLM. No math is added or altered;
    logits are returned untouched (disclosed in the module docstring)."""

    def __init__(self, m):
        self.m = m

    def __call__(self, tokens, repr_layers=None, return_contacts=None):
        out = self.m(input_ids=tokens)
        return {"logits": out.logits}

    def eval(self):
        self.m.eval()
        return self

    def double(self):
        self.m = self.m.double()
        return self


def member_complete(mstate, results):
    for name in mstate.get("arms_planned", [a for a, _ in ARMS32]):
        if name not in results or np.isnan(results[name]).any():
            return False
    f64n = mstate.get("fp64_n")
    if f64n is None:
        return False
    if int(f64n) > 0:
        if "C3_fp64_b8" not in results:
            return False
        if int(np.count_nonzero(~np.isnan(results["C3_fp64_b8"]))) < int(f64n):
            return False
    return True


if __name__ == "__main__":
    t_start = time.perf_counter()
    import transformers
    import huggingface_hub

    print(f"Script 103 (G2) | N_RESAMPLE={N_RESAMPLE} SEED={SEED} SMOKE={int(SMOKE)} "
          f"CHUNK={CHUNK} FP32_MAX_PROJ_S={FP32_MAX:.0f} FP64_MAX_PROJ_S={FP64_MAX:.0f}")
    print("versions: torch {v}, transformers {t}, huggingface_hub {h}, numpy {n}, "
          "pandas {p}".format(v=torch.__version__, t=transformers.__version__,
                              h=huggingface_hub.__version__, n=np.__version__,
                              p=pd.__version__))
    device = torch.device("cpu")
    print(f"Using device: {device} (FORCED -- producer was mps, batch 1, fp32)")

    # ---- pool + sample (script 75 L234-237 / L255-259, re-derived) -----
    d5 = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    d5 = d5.merge(own, on="hgvs_pro", how="left")
    pool = d5[d5["delta_esm"].notna() & d5["own_e_b"].notna()].copy().reset_index(drop=True)
    print(f"pool: {len(pool)} rows / {pool['position'].nunique()} positions "
          f"(delta_esm AND own_e_b non-null -- script 75's exact pool)")
    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(pool), size=min(N_RESAMPLE, len(pool)), replace=False)
    sub = pool.iloc[np.sort(idx)].copy().reset_index(drop=True)
    print(f"SUBSET: {len(sub)} variants / {sub['position'].nunique()} positions "
          f"(default_rng({SEED}).choice, replace=False -- script 75's convention)")

    # ---- hgvs parse (script 75 L313-337, same asserts) ------------------
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
    print(f"hgvs parse: fail={parse_fail}  wt-vs-FASTA mismatch={wt_mismatch}  "
          f"var==wt={var_is_wt}")
    assert parse_fail == 0 and wt_mismatch == 0 and var_is_wt == 0, "hgvs/FASTA sanity failed"
    bad_pos = int((sub["pos1"].astype(int) != sub["position"].astype(int)).sum())
    assert bad_pos == 0, "position mismatch between hgvs_pro and table"
    print(f"hgvs position vs table position mismatches: {bad_pos}")

    # ---- cached deltas for this sample, all five members ----------------
    cached_by_k = {}
    for k in range(1, 6):
        col = f"cached_{k}"
        mc = pd.read_csv(PROC / f"task_AC4_esm1v_member{k}_scores.csv")
        mc = mc.rename(columns={"mut_aa": "mmut", "delta": col})
        j = sub.merge(mc[["position", "wt_aa", "mmut", col]],
                      left_on=["pos1", "wt_aa", "var_aa"],
                      right_on=["position", "wt_aa", "mmut"], how="left",
                      validate="one_to_one")
        n_nan = int(j[col].isna().sum())
        print(f"member {k}: cached join {len(j)}/{len(sub)}, NaN (unmatched) = {n_nan}, "
              f"max|cached| = {np.nanmax(np.abs(j[col])):.3f}")
        cached_by_k[k] = j[col].to_numpy(dtype=float)

    # ---- state / checkpoint state (script 75's resume discipline) -------
    state = {"sample_hgvs": list(sub["hgvs_pro"]), "N_RESAMPLE": N_RESAMPLE,
             "members": {}}
    if STATE_PATH.exists():
        try:
            prev_state = json.loads(STATE_PATH.read_text())
        except Exception as e:
            prev_state = None
            print(f"State unreadable ({e}) -- fresh run")
        if prev_state is not None:
            if (prev_state.get("sample_hgvs") == state["sample_hgvs"]
                    and prev_state.get("N_RESAMPLE") == N_RESAMPLE):
                state = prev_state
                print(f"RESUME: state matches this sample (N={N_RESAMPLE}) -- "
                      f"completed members will be skipped without re-download")
            else:
                print("Sample/N_RESAMPLE MISMATCH vs prior state -- discarding it "
                      "(fresh run; old member CSVs will be overwritten)")
                for k in range(1, 6):
                    p = member_csv_path(k)
                    if p.exists():
                        p.unlink()
    STATE_PATH.write_text(json.dumps(state, indent=1))

    # ---- scoring rows (script 75 L372-375, re-derived) ------------------
    wt_rows = [(mask_at(wt_seq, int(p) - 1), v, wt_seq[int(p) - 1])
               for p, v in zip(sub["pos1"], sub["var_aa"])]
    bg_rows = [(mask_at(bg_seq, int(p) - 1), v, bg_seq[int(p) - 1])
               for p, v in zip(sub["pos1"], sub["var_aa"])]

    for k in range(1, 6):
        t_member = time.perf_counter()
        mstate = state["members"].setdefault(str(k), {})
        results = {}
        cp = member_csv_path(k)
        if cp.exists():
            prev = pd.read_csv(cp)
            if list(prev.get("hgvs_pro", [])) == list(sub["hgvs_pro"]):
                results = {c: prev[c].to_numpy(dtype=float).copy()
                           for c in prev.columns if c.startswith("C")}
                print(f"\nmember {k}: checkpoint loaded ({len(results)} condition "
                      f"column(s))")
            else:
                print(f"\nmember {k}: checkpoint sample MISMATCH -- discarding it")
        if member_complete(mstate, results):
            print(f"member {k}: ALL FOUR ARMS COMPLETE in checkpoint -- skipped "
                  f"(no download, no scoring)")
            continue

        # ---- weights (script 86's hf_fetch: size gate + md5 + disk gate) -
        print(f"\n=== member {k}: fetching/staging weights ===")
        t0 = time.time()
        dest = hf_fetch(k)
        binp = dest / "pytorch_model.bin"
        print(f"member {k}: staged {binp.stat().st_size:,} B "
              f"({time.time() - t0:.0f}s fetch incl. md5 provenance)")

        from transformers import AutoTokenizer, EsmForMaskedLM
        tok = AutoTokenizer.from_pretrained(str(dest))
        hf = EsmForMaskedLM.from_pretrained(str(dest))
        hf.eval()
        model = HFAdapter(hf)
        # fair-esm side: ESM-1b is fair-esm's architecture for the esm1v
        # family; the TOK gate below verifies it against the producer's
        # HF tokenizer on every sampled sequence before any scoring.
        alphabet = esm.Alphabet.from_architecture("ESM-1b")
        bc = alphabet.get_batch_converter()

        # ---- TOK gate (new; can only block a wrong PASS) -----------------
        n_bad = 0
        first_bad = None
        for j2 in range(len(sub)):
            for seq_ctx in (wt_rows[j2][0], bg_rows[j2][0]):
                _, _, t1 = bc([("q", seq_ctx)])
                t2 = tok(seq_ctx, return_tensors="pt")["input_ids"]
                if t1.shape != t2.shape or not bool((t1[0] == t2[0]).all()):
                    n_bad += 1
                    if first_bad is None:
                        first_bad = (j2, t1.shape, t2.shape)
        print(f"TOK gate (member {k}): {2 * len(sub)} sampled masked sequences, "
              f"fair-esm-vs-HF id mismatches = {n_bad} (threshold 0)")
        if n_bad:
            print(f"TOK FAIL: {n_bad} mismatch(es); first at sample row "
                  f"{first_bad} -- STOP (no grid may run on a mismatched tokenizer; "
                  "no retry, no threshold change)")
            sys.exit(1)
        print("TOK PASS")

        # ---- G1 identity gate (script 75 L353-368, re-derived) -----------
        n_g1 = min(10, len(sub))
        g1_rows = []
        for j2 in range(n_g1):
            i = int(sub["pos1"].iloc[j2]) - 1
            v = sub["var_aa"].iloc[j2]
            g1_rows.append((mask_at(wt_seq, i), v, wt_seq[i]))
            g1_rows.append((mask_at(bg_seq, i), v, bg_seq[i]))
        mine = batched_odds(alphabet, bc, model, g1_rows, device, batch_size=8)
        libv = []
        for j2 in range(n_g1):
            p = int(sub["pos1"].iloc[j2]); v = sub["var_aa"].iloc[j2]
            d_wt = get_position_logprobs(model, alphabet, bc, wt_seq, p, device)
            d_bg = get_position_logprobs(model, alphabet, bc, bg_seq, p, device)
            libv.extend([d_wt[v], d_bg[v]])
        g1_max = max(abs(a - b) for a, b in zip(mine, libv))
        print(f"G1 identity gate (batched CPU fp32 vs lib get_position_logprobs, "
              f"{n_g1} variants x 2 ctx): max|diff| = {g1_max:.3e}  (threshold 1e-5)")
        if not g1_max < 1e-5:
            print(f"G1 FAIL: max|diff| = {g1_max:.6e} >= 1e-5 -- STOP "
                  "(no retry, no threshold change)")
            sys.exit(1)
        print("G1 PASS")

        def write_member_csv(results):
            out = sub[["hgvs_pro", "position", "own_e_b"]].copy()
            out["cached"] = cached_by_k[k]
            for name in ("C0_fp32_b1", "C1_fp32_b8", "C2_fp32_b16", "C3_fp64_b8"):
                if name in results:
                    out[name] = results[name]
            out.to_csv(cp, index=False)

        # ---- timing smoke + fp32 arm-drop tier (script 75 L370-390) ------
        smoke_n = min(8, len(sub))
        t0 = time.perf_counter()
        _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n], bg_rows[:smoke_n],
                         device, 8)
        t32 = (time.perf_counter() - t0) / smoke_n
        arms = list(mstate.get("arms_planned", [])) or list(ARMS32)
        if not mstate.get("arms_planned"):
            print(f"\nTIMING SMOKE (fp32, batch 8, n={smoke_n}): {t32:.3f} s/variant "
                  f"-> projected C0+C1+C2 at N={N_RESAMPLE} = "
                  f"{t32 * N_RESAMPLE * len(ARMS32):.0f} s (cap {FP32_MAX:.0f})")
            while arms and (t32 * N_RESAMPLE * len(arms)) > FP32_MAX:
                dropped, arms = arms[-1], arms[:-1]
                print(f"  ARM-DROP TIER: dropped {dropped} to fit the fp32 "
                      f"projection cap (remaining {len(arms)} arm(s) project "
                      f"{t32 * N_RESAMPLE * len(arms):.0f} s at N={N_RESAMPLE})")
            assert arms, "even C1 alone exceeds the fp32 projection cap -- STOP"
            mstate["arms_planned"] = [a for a, _ in arms]
            state["members"][str(k)] = mstate
            STATE_PATH.write_text(json.dumps(state, indent=1))
        else:
            arms = [(n, b) for n, b in ARMS32 if n in mstate["arms_planned"]]
            print(f"\nfp32 arm plan reused from state: {mstate['arms_planned']}")

        if SMOKE:
            # fp64 timing smoke for the projection. Script 75 takes this
            # measurement AFTER its fp32 arms; in SMOKE mode no arm runs, so
            # the same two measurements are taken here (disclosed) to project
            # the full grid. No tier decision is stored at smoke time -- tiers
            # are decided by the full run, exactly as script 75 does.
            t0 = time.perf_counter()
            _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n],
                             bg_rows[:smoke_n], device, 8)
            t32_b8 = (time.perf_counter() - t0) / smoke_n
            model = model.double()
            t0 = time.perf_counter()
            _ = score_deltas(alphabet, bc, model, wt_rows[:smoke_n],
                             bg_rows[:smoke_n], device, 8)
            t64 = (time.perf_counter() - t0) / smoke_n
            proj32 = t32 * N_RESAMPLE * len(arms)
            proj64 = t64 * N_RESAMPLE
            print(f"TIMING SMOKE fp64 (batch 8, n={smoke_n}): {t64:.3f} s/variant "
                  f"(fp32 same-config {t32_b8:.3f} s/variant, fp64/fp32 = "
                  f"{t64 / t32_b8:.2f}x)")
            print(f"PROJECTION at N={N_RESAMPLE}: fp32 arms {proj32:.0f} s + fp64 "
                  f"{proj64:.0f} s = {proj32 + proj64:.0f} s/member "
                  f"({(proj32 + proj64) / 60:.1f} min) -> x5 members = "
                  f"{5 * (proj32 + proj64) / 60:.0f} min of scoring")
            state["members"][str(k)] = mstate
            STATE_PATH.write_text(json.dumps(state, indent=1))
            print(f"\nSMOKE=1: member 1 TOK + G1 gates and timing only; no arms "
                  f"were run; staged weights KEPT for the full run ({dest})")
            print(f"Total runtime {time.perf_counter() - t_start:.1f}s.")
            sys.exit(0)

        # ---- run fp32 arms (script 75 L392-415, chunked + resumable) -----
        for name, bsz in arms:
            if name in results and not np.isnan(results[name]).any():
                print(f"  {name}: already complete in checkpoint -- skipped")
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
                write_member_csv(results)
                print(f"    {name}: {e}/{len(sub)} checkpointed "
                      f"@ {time.strftime('%H:%M:%S')}", flush=True)
            el = time.perf_counter() - t0
            n_this = max(len(sub) - start, 1)
            print(f"  {name}: {el:.1f} s this invocation "
                  f"({el / n_this:.3f} s/variant)")

        # ---- fp64 feasibility tier + arm (script 75 L417-479) ------------
        c3 = results.get("C3_fp64_b8")
        f64n_stored = mstate.get("fp64_n")
        c3_have = (f64n_stored is not None and c3 is not None
                   and int(np.count_nonzero(~np.isnan(c3))) >= int(f64n_stored))
        if c3_have:
            print(f"  C3_fp64_b8: already complete in checkpoint (n={f64n_stored}, "
                  f"tier {mstate.get('fp64_tier', '?')}) -- skipped")
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
            proj64_full = t64 * N_RESAMPLE
            proj64_100 = t64 * min(100, N_RESAMPLE)
            print(f"TIMING SMOKE fp64 (batch 8, n={smoke_n}): {t64:.3f} s/variant "
                  f"(fp32 same-config {t32_b8:.3f} s/variant, fp64/fp32 = "
                  f"{t64 / t32_b8:.2f}x) -> projected at N={N_RESAMPLE} = "
                  f"{proj64_full:.0f} s (cap {FP64_MAX:.0f})")
            if mstate.get("fp64_n") is not None:
                fp64_n = int(mstate["fp64_n"])
                print(f"  fp64 tier: reusing stored decision (tier "
                      f"{mstate.get('fp64_tier', '?')}, n={fp64_n}) -- not re-decided")
            elif proj64_full <= FP64_MAX:
                fp64_n = len(sub)
                mstate["fp64_tier"] = "a"
                print("  fp64 tier (a): FULL N")
            elif proj64_100 <= FP64_MAX:
                fp64_n = min(100, len(sub))
                mstate["fp64_tier"] = "b"
                print(f"  fp64 tier (b): N={fp64_n} only -- full-N projection "
                      f"{proj64_full:.0f} s > cap {FP64_MAX:.0f} -- DISCLOSED "
                      "reduced-N fp64 arm")
            else:
                fp64_n = 0
                mstate["fp64_tier"] = "c"
                print(f"  fp64 tier (c): SKIPPED -- even N=100 projects "
                      f"{proj64_100:.0f} s > cap {FP64_MAX:.0f} -- feasibility "
                      "determination: NOT feasible (measured "
                      f"{t64:.3f} s/variant), DISCLOSED")
            mstate["fp64_n"] = fp64_n
            state["members"][str(k)] = mstate
            STATE_PATH.write_text(json.dumps(state, indent=1))
            if fp64_n > 0:
                vals64 = c3 if c3 is not None else np.full(len(sub), np.nan)
                start = int(np.count_nonzero(~np.isnan(vals64)))
                if start > 0:
                    print(f"  C3_fp64_b8: resuming from variant {start}/{fp64_n}")
                t0 = time.perf_counter()
                for s in range(start, fp64_n, CHUNK):
                    e = min(s + CHUNK, fp64_n)
                    vals64[s:e] = score_deltas(alphabet, bc, model,
                                               wt_rows[s:e], bg_rows[s:e], device, 8)
                    results["C3_fp64_b8"] = vals64
                    write_member_csv(results)
                    print(f"    C3_fp64_b8: {e}/{fp64_n} checkpointed "
                          f"@ {time.strftime('%H:%M:%S')}", flush=True)
                print(f"  C3_fp64_b8: {time.perf_counter() - t0:.1f} s this "
                      f"invocation (n={fp64_n})")

        mstate["done"] = True
        state["members"][str(k)] = mstate
        STATE_PATH.write_text(json.dumps(state, indent=1))
        write_member_csv(results)

        # script 86's staging discipline: one member at a time, delete
        # before the next fetch (hf_fetch exits on a STAGING VIOLATION).
        shutil.rmtree(dest, ignore_errors=True)
        print(f"member {k}: staged weights deleted (one-member staging discipline)")
        print(f"member {k}: total {time.perf_counter() - t_member:.1f}s")

    # ---------------- comparisons (script 75 L481-505, per member) -------
    print("\n" + "=" * 74)
    verdicts = {}
    for k in range(1, 6):
        cp = member_csv_path(k)
        if not cp.exists():
            print(f"COVERAGE FAIL: member {k} has no result file -- NO verdict.")
            sys.exit(1)
        df = pd.read_csv(cp)
        cached = df["cached"].to_numpy(dtype=float)
        own_eb = df["own_e_b"].to_numpy(dtype=float)
        mstate = state["members"].get(str(k), {})
        plan = mstate.get("arms_planned", [a for a, _ in ARMS32])
        f64n = int(mstate.get("fp64_n", -1))
        expected = {name: len(sub) for name in plan}
        if f64n > 0:
            expected["C3_fp64_b8"] = f64n
        cov_bad = {}
        for name, exp_n in expected.items():
            have = int(np.count_nonzero(~np.isnan(df[name].to_numpy(dtype=float)))) \
                if name in df.columns else 0
            if have != exp_n:
                cov_bad[name] = (have, exp_n)
        if cov_bad:
            print(f"member {k} COVERAGE FAIL: (rows run, pre-registered coverage) = "
                  f"{cov_bad} -- conditions incomplete; NO verdict for this member.")
            sys.exit(1)
        okc = ~np.isnan(cached)
        rho_pair = spearman(cached[okc], own_eb[okc])
        print(f"member {k}: Spearman(cached, own_e_b) on these {int(okc.sum())} rows "
              f"(SAMPLE baseline, not the published full-set member rho) = "
              f"{rho_pair:+.6f}")
        for name in ("C0_fp32_b1", "C1_fp32_b8", "C2_fp32_b16", "C3_fp64_b8"):
            if name not in df.columns:
                continue
            v = df[name].to_numpy(dtype=float)
            ok = ~np.isnan(v) & okc
            diff = np.abs(v[ok] - cached[ok])
            r1 = float(diff.max()) <= 1e-3
            rho_c = spearman(v[ok], own_eb[ok])
            paired = abs(rho_c - spearman(cached[ok], own_eb[ok]))
            r2 = paired <= 0.01
            verdicts[(k, name)] = (r1, r2)
            print(f"  {name}: max|d-cached| = {diff.max():.3e}  median = "
                  f"{np.median(diff):.3e}  rmse = {np.sqrt((diff ** 2).mean()):.3e} | "
                  f"rho(own_e_b) = {rho_c:+.4f}  n_ok = {int(ok.sum())}/{len(df)} | "
                  f"paired |d rho| vs cached on same rows = {paired:.4f} | "
                  f"R1 {'PASS' if r1 else 'FAIL'} (<=1e-3), "
                  f"R2 {'PASS' if r2 else 'FAIL'} (<=0.01)")

    n_v = len(verdicts)
    n_expected_total = 0
    for k in range(1, 6):
        ms = state["members"].get(str(k), {})
        n_expected_total += len(ms.get("arms_planned", [a for a, _ in ARMS32]))
        if int(ms.get("fp64_n", 0)) > 0:
            n_expected_total += 1
    if n_v != n_expected_total:
        print(f"\nCOVERAGE FAIL: {n_v} member-conditions present, "
              f"{n_expected_total} pre-registered -- NO verdict.")
        sys.exit(1)
    r1_all = all(v[0] for v in verdicts.values())
    r2_all = all(v[1] for v in verdicts.values())
    overall = r1_all and r2_all
    print("\n" + "=" * 74)
    print(f"R1 (value, all {n_v} member-conditions <= 1e-3): "
          f"{'PASS' if r1_all else 'FAIL'}")
    print(f"R2 (finding, all {n_v} paired |rho shifts| <= 0.01): "
          f"{'PASS' if r2_all else 'FAIL'}")
    if overall:
        print("G2 VERDICT: PASS -- all five ESM-1v members' cached deltas reproduce "
              "under the same CPU / fp32-b1 / fp32-b8 / fp32-b16 / fp64-b8 grid to "
              "the same tolerances the original ESM-2 check used (G1 + TOK + R1 + "
              "R2; thresholds 1e-5 / 1e-3 / 0.01 unchanged).")
    else:
        print("G2 VERDICT: FAIL -- one or more ESM-1v members' cached deltas do NOT "
              "reproduce to the precision the original check used.")
        print("  Adapted from script 75's own FAIL text: if this grid fails, a "
              "mundane numerical explanation is more urgent than any model-family "
              "interpretation, and the five-member rhos (T1a) and the ensemble "
              "delta must not be quoted as safe until this is resolved.")
    print("=" * 74)

    # ---- combined deliverable -------------------------------------------
    frames = []
    for k in range(1, 6):
        df = pd.read_csv(member_csv_path(k))
        df.insert(0, "member", k)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(OUT_PATH, index=False)
    print(f"\nSaved combined: {OUT_PATH} ({len(out)} rows) and per-member "
          f"task_G2_member{{k}}_rescore.csv (state: {STATE_PATH})")

    print("\nLIMITATIONS (stated in the script's own output, AGENTS Sec 6):")
    print("  * Version drift: cached deltas came from script 86's run under "
          "whatever torch/transformers were installed then; versions printed at "
          "start cannot be separated from the device/batch term here (disclosed).")
    print("  * CPU-vs-MPS compares implementations, not rounding alone; the "
          "producer's mps/batch-1 origin is not separable from the grid's CPU "
          "term (same caveat as AC3).")
    print("  * Asymmetric with AC3: the grid model here is the same Transformers "
          "library that PRODUCED the cached columns (closer to the producer than "
          "AC3's fair-esm rescore of fair-esm-produced values); fair-esm is used "
          "only for tokenization/alphabet, gated by TOK on every load.")
    print("  * R1/R2 are computed on the sampled rows only, not all 12,446 cached "
          "rows; per-member rho baselines printed are SAMPLE baselines, not the "
          "published full-set five-member rhos or the ensemble rho.")
    print("  * Thresholds (G1 1e-5, R1 1e-3, R2 0.01) were fixed before any G2 "
          "rescore value existed; no threshold was changed after seeing a result.")
    print(f"  * Total runtime {time.perf_counter() - t_start:.1f}s.")
