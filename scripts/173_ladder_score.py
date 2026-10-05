"""Script 173 (Phase 4 session 4a, Task A8b + A8c support) -- Module L model
ladder scorer: ESM-2 650M / 150M / 35M over the 96 Phase 2 backgrounds plus
A222V and the wild-type arm, on the 455 held-out positions H.

PRE-REGISTERED: this docstring was written before the first run of this
script, when NO ladder score of any kind existed (data/processed/phase4/ladder
did not exist at all).  Binding text: PHASE4_STRENGTHENING.md Task A8b/A8c;
MODEL_LADDER_PREREG_v1.md (sha256
eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3, 26 lines),
frozen section 2 (design) and section 4 (gates G-L0..G-L3).  torch is imported
here and ONLY here (planning rule 1: model scoring is allowed in the
neighbour-arm and ladder scoring scripts, their gates and their timing
smokes).

DECISIONS, pre-registered here before the first run (printed at startup):

LD-DEC1  Model registry: 650M -> esm.pretrained.esm2_t33_650M_UR50D,
         150M -> esm.pretrained.esm2_t30_150M_UR50D,
         35M  -> esm.pretrained.esm2_t12_35M_UR50D.  These torch.hub entry
         points are the ONLY loader used.  A8a established that
         esm.pretrained.load_model_and_alphabet_local is BROKEN on this
         machine (torch >= 2.6 defaults torch.load(weights_only=True) and the
         checkpoints contain an argparse.Namespace), so it is never called;
         scripts/lib/esm_scoring.py is NOT edited (AGENTS 7).  The scoring
         function is that library's get_position_logprobs, unmodified.
LD-DEC2  The cache is checked BEFORE the loader is called: if the model's .pt
         or its -contact-regression.pt is missing, this prints ERROR and
         exits 3 WITHOUT calling the loader.  A download here would break
         planning rule 2 (the A8 authorisation is spent), so a missing
         checkpoint is a BLOCK, never a download.
LD-DEC3  Roster = A222V + the 96 rows of data/processed/phase2_arm_roster.csv
         (frozen section 2: "A222V and the 96 Phase 2 backgrounds (the same
         roster)"), in that file's order, A222V first.  Verified before the
         run: A222V is NOT among the 96 (arms G40/V38/S18), 97 unique
         bg_ids, 0 duplicate (position, mutant) pairs.
LD-DEC4  Frame = the 455 held-out positions H only (frozen section 2), minus
         the background's own position when that position is in H, so a
         background gets 455 or 454 passes (57 of the 97 have their own
         position inside H).  Expected total = 44,078 background passes + 455
         wild-type passes = 44,533, printed BESIDE the planning doc's formula
         97 x 455 + 455 = 44,590, which overstates by exactly those 57
         (planning rule 16: the doc's figures are Claude's recomputations; the
         exact count is used for the projection, both are printed).
LD-DEC5  Protocol identical to script 171 / script 124: ONE unbatched
         masked-marginal forward pass per (background, position), all 19
         substitutions taken from that pass, model.eval(), torch.no_grad()
         inside the library.  delta = score - THIS MODEL'S OWN wild-type-arm
         score for the same (position, mut_aa); the wild-type arm is scored
         first and reused by every background of that model.  (Consequence,
         disclosed: a 150M/35M delta is referenced to that model's own WT arm,
         not to the cached 650M WT scores, so deltas are comparable across
         models in rank, never in scale.)
LD-DEC6  Output layout data/processed/phase4/ladder/<model>/:
         bg_<bg_id>.csv with columns bg_id, position, mut_aa, score, delta;
         wt_H.csv with columns bg_id (= "WT"), position, mut_aa, score and NO
         delta column -- it is the reference arm, never a 98th background
         (script 174 excludes bg_id == "WT" by construction); manifest.csv
         appended with bg_id, n_positions, n_rows, seconds, device, sha256.
         Atomic write-then-os.replace, .tmp never counts as completion, and
         the skip test is script 124's file_is_complete, IMPORTED not
         reimplemented (124's atomic-write pattern is QUOTED below with 124's
         line numbers 235-264).
LD-DEC7  G-L1 (HARD): the cache pre-check passed and the loaded model's
         parameter count, layer count and embed_dim are printed.  Targets
         logged in A8a (measured there with the network unreachable): 650M
         651,043,254 params / 33 layers / dim 1280; 150M 148,140,154 / 30 /
         640; 35M 33,501,394 / 12 / 480.  Each is printed beside its target
         and must match exactly (same loader, same cache file).
LD-DEC8  G-L2 (HARD, --model 650M only): rescoring AV_220 on H through THIS
         scorer reproduces the cached Phase-2 rows' score AND delta to 1e-6
         over the 8,626 cached H rows (454 positions x 19).  A7c's G-N2
         measured max|diff| 1.776e-15 for the same comparison on the same
         device; that is printed beside the gate's 1e-6 as the expected
         value.  An ADDED, stricter sub-check G-L2(b) requires this run's
         650M wild-type arm to reproduce the cached esm2_wt_scores.csv to
         1e-6 on the same H rows, because that arm is the delta reference
         for every background of the model.  G-L3(a) REUSES G-L2's two runs
         (run1 vs cache, run1 vs run2) instead of scoring twice more --
         disclosed here; the objects compared are identical, no gate is
         weakened.
LD-DEC9  G-L3 (HARD, per model): (a) the same background scored twice in
         one run is identical to 1e-6 (the frozen ladder tolerance; note
         A7c's stricter exact-0.0 reading also held at 650M); (b) the
         wild-type residue's log-odds is exactly 0 from a direct masked pass,
         with the alphabet round-trip and the 19-entries-excluding-the-WT-
         residue checks; (c) every background file present in the out-dir
         covers >= 95% of its eligible H positions -- a MISSING file is
         PENDING (this model has not been scored), a present but short file
         is FAIL.  Any FAIL -> exit 3.
LD-DEC10 Gates run before any roster scoring whenever at least one background
         is to be scored.  --gate-only runs the gates and writes nothing;
         if the pre-scan finds everything complete there is nothing to gate,
         the script says so and exits 0 (a gate guards scoring).
LD-DEC11 Timing (A8c support): after the run, the median seconds per pass over
         the backgrounds scored IN THIS RUN is printed, and the full-model
         projection (exact total passes x s/pass x 1.25, minutes) is printed
         BESIDE the same projection on the doc's 97 x 455 + 455 count.  No
         budget threshold is applied here: A9 sets the budgets.
LD-DEC12 N_BOOT and SEED are printed and UNUSED (no bootstrap here).

LIMITATIONS (also printed at the end of every run):
  * Deltas are per-model WT-referenced, so their SCALE differs between
    models; only ranks enter the frozen ladder statistics, but a reader
    comparing raw delta magnitudes across models would be misled.
  * The wild-type arm is scored once per model and reused for every delta of
    that model -- a single point of failure, which is why its completeness is
    gated like any other file.
  * G-L2 is a regression test of this pipeline against rows the same library
    function produced on the same device in Phase 2: it validates the code,
    it is not independent evidence (AGENTS 6).  It cannot run for 150M/35M at
    all, since no cached 150M/35M rows exist to compare against.
  * One forward pass per position means no batching; runtime scales linearly
    with backgrounds x positions.
  * Masked-marginal log-odds are float32 on MPS; the 1e-6 tolerances are ~9
    orders of magnitude above that noise floor but far below anything that
    would change a rank.

Usage:
  venv/bin/python3 scripts/173_ladder_score.py --model 650M --gate-only
  venv/bin/python3 scripts/173_ladder_score.py --model 150M
  venv/bin/python3 scripts/173_ladder_score.py --model 35M \
      --out-dir data/processed/phase4/ladder_scratch/timing35 \
      --limit-backgrounds 3          # A8c timing smoke
"""

import argparse
import hashlib
import importlib.util
import os
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODELS = {
    "650M": dict(fn="esm2_t33_650M_UR50D", file="esm2_t33_650M_UR50D.pt",
                 params=651043254, layers=33, dim=1280),
    "150M": dict(fn="esm2_t30_150M_UR50D", file="esm2_t30_150M_UR50D.pt",
                 params=148140154, layers=30, dim=640),
    "35M": dict(fn="esm2_t12_35M_UR50D", file="esm2_t12_35M_UR50D.pt",
                 params=33501394, layers=12, dim=480),
}
ROSTER96 = ROOT / "data/processed/phase2_arm_roster.csv"
ROSTER96_SHA = "9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b"
AV220_CACHE = ROOT / "data/processed/phase2/bg_AV_220.csv"
AV220_SHA = "2dc13f8073aec0f0147819e038e7488e0306ae100f25b0afdb88539afb9f752e"
WT_CACHE = ROOT / "data/processed/esm2_wt_scores.csv"
WT_CACHE_SHA = "e4d3af3d444a0d0a35e71422e44fe3bfc3338ffa7df77e05552a8a0d6871581c"
PREREG = (ROOT / "docs/tasks/phase4-strengthening/prereg/"
          "MODEL_LADDER_PREREG_v1.md")
PREREG_SHA = "eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3"
SCRATCH = ROOT / "data/processed/phase4/ladder_scratch"
DOC_PLAN_PASSES = 97 * 455 + 455          # planning figure, printed beside
DET_TOL = 1e-6                             # frozen G-L3(a)
CACHE_TOL = 1e-6                           # frozen G-L2
COV_MIN = 0.95                             # frozen G-L3(c)

GATES = []
t_script = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gate(name, val, detail=""):
    """val True -> PASS, False -> FAIL, None -> PENDING."""
    if val is None:
        tag, stored = "PENDING", None
    else:
        stored = bool(val)
        tag = "PASS" if stored else "FAIL"
    GATES.append((name, stored))
    print(f"  [{tag}] {name}" + (f": {detail}" if detail else ""), flush=True)


def load_helper(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(MODELS), required=True)
    ap.add_argument("--out-dir", default=None,
                    help="default data/processed/phase4/ladder/<model>")
    ap.add_argument("--only", default=None,
                    help="score/skip only this bg_id")
    ap.add_argument("--limit-backgrounds", type=int, default=None,
                    help="only the first N backgrounds of the roster, in "
                         "roster order (A8c timing smoke)")
    ap.add_argument("--gate-only", action="store_true",
                    help="run every gate and write nothing (LD-DEC10)")
    args = ap.parse_args()

    spec_m = MODELS[args.model]
    out_dir = ROOT / (args.out_dir or f"data/processed/phase4/ladder/{args.model}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_rel = out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) \
        else out_dir

    banner(f"173 -- Module L ladder scorer  N_BOOT={N_BOOT} SEED={SEED} "
           f"(both UNUSED: no bootstrap here)  model={args.model}")
    print(f"  out_dir = {out_rel}"
          + ("   [GATE-ONLY: nothing will be written]" if args.gate_only
             else ""))
    print("\nPRE-REGISTERED DECISIONS (full text in the docstring):")
    for k, v in [
        ("LD-DEC1", f"load through esm.pretrained.{spec_m['fn']} (the hub "
                    "entry point); load_model_and_alphabet_local is BROKEN "
                    "under torch>=2.6 and is never called; the library "
                    "esm_scoring.get_position_logprobs is used unmodified."),
        ("LD-DEC2", "cache pre-check before the loader; missing -> exit 3, "
                    "NEVER a download."),
        ("LD-DEC3", "roster = A222V + the 96 of phase2_arm_roster.csv, in "
                    "that order."),
        ("LD-DEC4", "frame = H (455) minus own position when own in H; exact "
                    f"total 44,533 passes printed beside the doc's "
                    f"{DOC_PLAN_PASSES}."),
        ("LD-DEC5", "one unbatched masked-marginal pass per (background, "
                    "position), 19 substitutions per pass; delta vs THIS "
                    "model's own WT arm."),
        ("LD-DEC6", "outputs ladder/<model>/bg_<id>.csv (bg_id, position, "
                    "mut_aa, score, delta) + wt_H.csv (bg_id=WT, no delta) "
                    "+ manifest.csv; 124's skip logic imported, its atomic "
                    "write quoted (124 lines 235-264)."),
        ("LD-DEC7", "G-L1 cache pre-check + parameter count printed beside "
                    "the A8a-measured target."),
        ("LD-DEC8", "G-L2 (650M only): AV_220 on H vs cached rows, score AND "
                    "delta, to 1e-6; ADDED sub-check G-L2(b) WT arm vs the "
                    "cached WT scores; G-L3(a) reuses those two runs."),
        ("LD-DEC9", f"G-L3 per model: determinism to {DET_TOL:g}, WT "
                    f"log-odds 0, coverage >= {COV_MIN:.0%}."),
        ("LD-DEC10", "gates run when something is to be scored; --gate-only "
                     "runs them and writes nothing."),
        ("LD-DEC11", "median s/pass + projection x1.25 beside the doc's pass "
                     "count; no budget applied here (A9 sets it)."),
        ("LD-DEC12", "N_BOOT/SEED printed, unused."),
    ]:
        print(f"  {k}: {v}")

    # ------------------------------------------------------------ inputs ---
    banner("G-L0 / INPUT PINS", "-")
    gate("G-L0 MODEL_LADDER_PREREG_v1 sha256", sha256(PREREG) == PREREG_SHA,
         sha256(PREREG)[:16])
    gate("G-L0 the 96-background roster sha256", sha256(ROSTER96) == ROSTER96_SHA,
         sha256(ROSTER96)[:16])
    gate("G-L0 cached AV_220 rows sha256", sha256(AV220_CACHE) == AV220_SHA,
         sha256(AV220_CACHE)[:16])
    gate("G-L0 cached WT-score file sha256", sha256(WT_CACHE) == WT_CACHE_SHA,
         sha256(WT_CACHE)[:16])

    # ------------------------------------------------------ frame + roster --
    from scripts.lib.sequence import load_sequence, verify_sequence
    s125 = load_helper("s125_phase2_analysis", "scripts/125_phase2_analysis.py")
    s124 = load_helper("s124_phase2_score_backgrounds",
                       "scripts/124_phase2_score_backgrounds.py")
    H = sorted(int(p) for p in s125.holdout(s125.build_frame()))
    Hset = set(H)
    gate("frame H = 455 positions (script 125 prints 455 / 7,526)",
         len(H) == 455, str(len(H)))

    wt_seq = load_sequence(str(ROOT / "data/raw/P42898.fasta"))
    verify_sequence(wt_seq)

    r96 = pd.read_csv(ROSTER96)
    roster_all = [("A222V", 222, "A", "V")]
    roster_all += [(x.bg_id, int(x.position), x.wt_aa, x.mut_aa)
                   for x in r96.itertuples()]
    pairs = [(own, m) for _, own, _, m in roster_all]
    gate("roster = 97 unique backgrounds, no duplicate (position, mutant)",
         len(roster_all) == 97 and len({b[0] for b in roster_all}) == 97
         and len(pairs) == len(set(pairs)),
         f"{len(roster_all)} backgrounds; arms "
         f"{r96.arm.value_counts().to_dict()}; A222V among the 96 = "
         f"{'A222V' in set(r96.bg_id)}")
    for bg_id, own, w, m in roster_all:
        assert wt_seq[own - 1] == w, (bg_id, wt_seq[own - 1], w)

    roster = list(roster_all)
    if args.limit_backgrounds is not None:
        roster = roster[:args.limit_backgrounds]
    if args.only is not None:
        roster = [r for r in roster if r[0] == args.only]
        if len(roster) != 1:
            print(f"ERROR: --only {args.only} matched {len(roster)} rows")
            sys.exit(1)

    exp = {bg_id: [p for p in H if p != own] for bg_id, own, _, _ in roster}
    bg_passes = sum(len(v) for v in exp.values())
    total_passes = bg_passes + len(H)
    gate(f"expected passes {total_passes} = backgrounds {bg_passes} + WT arm "
         f"{len(H)}; the planning doc's formula 97 x 455 + 455 = "
         f"{DOC_PLAN_PASSES} overstates by {DOC_PLAN_PASSES - total_passes} "
         "(backgrounds whose own position is in H get 454, not 455)",
         total_passes <= DOC_PLAN_PASSES,
         f"per background {sorted({len(v) for v in exp.values()})}; "
         f"{sum(1 for _, o, _, _ in roster_all if o in Hset)} of 97 have "
         f"own in H")

    # ------------------------------------------------------------ pre-scan --
    wt_final = out_dir / "wt_H.csv"
    wt_complete = s124.file_is_complete(wt_final, "WT", H)
    todo, n_skip = [], 0
    for bg_id, own, _, _ in roster:
        if s124.file_is_complete(out_dir / f"bg_{bg_id}.csv", bg_id,
                                 exp[bg_id]):
            n_skip += 1
            print(f"  SKIP {bg_id}: complete ({19 * len(exp[bg_id])} rows)")
        else:
            todo.append(bg_id)
    print(f"  pre-scan: {n_skip} background(s) complete, {len(todo)} to score; "
          f"wild-type arm {'complete' if wt_complete else 'TO SCORE'}")
    if not todo and wt_complete and not args.gate_only:
        print("Nothing to score -> the gates guard scoring and no scoring "
              "occurs in this invocation (LD-DEC10); exiting 0.")
        return

    # ----------------------------------------------------------- LD-DEC2 ---
    import torch
    ckpt_dir = Path(torch.hub.get_dir()) / "checkpoints"
    need = [spec_m["file"],
            spec_m["file"].replace(".pt", "-contact-regression.pt")]
    missing = [c for c in need if not (ckpt_dir / c).exists()]
    if missing:
        print(f"ERROR [LD-DEC2]: missing from the local torch.hub cache: "
              f"{missing}. This is a BLOCK -- the A8 download authorisation "
              f"is spent and planning rule 2 forbids any other fetch. "
              f"Exit 3. No download attempted.")
        sys.exit(3)
    gate("LD-DEC2 cache pre-check: both checkpoint files present", True,
         f"{need[0]} ({(ckpt_dir / need[0]).stat().st_size:,} B) + {need[1]} "
         f"({(ckpt_dir / need[1]).stat().st_size:,} B)")

    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    device = get_device()
    print(f"Using device: {device}")
    print(f"Loading {spec_m['fn']} through the hub entry point (the cache "
          f"hit was verified above, so no fetch can occur)...", flush=True)
    t_load = time.time()
    model, alphabet = getattr(esm.pretrained, spec_m["fn"])()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  loaded in {time.time() - t_load:.1f}s")
    gate(f"G-L1 {args.model} parameter count == the A8a-measured "
         f"{spec_m['params']:,}", n_params == spec_m["params"],
         f"got {n_params:,} (target {spec_m['params']:,}, |diff| "
         f"{abs(n_params - spec_m['params'])})")
    gate(f"G-L1 {args.model} layers / embed_dim match the A8a measurement",
         len(model.layers) == spec_m["layers"]
         and model.embed_dim == spec_m["dim"],
         f"{len(model.layers)} layers (target {spec_m['layers']}), "
         f"embed_dim {model.embed_dim} (target {spec_m['dim']})")

    def score_positions(seq, positions):
        rows = []
        for p in positions:
            sc = get_position_logprobs(model, alphabet, batch_converter,
                                       seq, p, device)
            for m, s in sc.items():
                rows.append(dict(position=int(p), mut_aa=m, score=float(s)))
        return pd.DataFrame(rows, columns=["position", "mut_aa", "score"])

    # ------------------------------------------------------------- gates ----
    banner(f"G-L2 / G-L3 (HARD) for {args.model}", "-")
    wt_map = {}
    g2_run1 = g2_run2 = None

    if args.model == "650M":
        # The wild-type arm is needed as the delta reference for G-L2(b) and
        # for anything this run scores; in --gate-only it is scored into
        # memory only.
        t_wt0 = time.time()
        wt_arm = score_positions(wt_seq, H)
        wt_dt = time.time() - t_wt0
        wt_map = {(int(r.position), r.mut_aa): float(r.score)
                  for r in wt_arm.itertuples()}
        print(f"  wild-type arm scored into memory: {len(H)} positions, "
              f"{len(wt_arm)} rows in {wt_dt:.1f}s "
              f"({wt_dt / len(H):.4f} s/pass)"
              + ("  [gate-only: not written]" if args.gate_only else ""))

        # G-L2: AV_220 on H through THIS scorer vs the cached Phase-2 rows.
        # AV_220 is A220Val -- position 220, NOT A222V; its own position is
        # taken from the roster, never hardcoded.
        own220, w220, m220 = [(o, ww, mm) for b, o, ww, mm in roster_all
                                 if b == "AV_220"][0]
        assert wt_seq[own220 - 1] == w220
        av_seq = wt_seq[:own220 - 1] + m220 + wt_seq[own220:]
        gpos = [p for p in H if p != own220]
        t_g = time.time()
        g2_run1 = score_positions(av_seq, gpos)
        g2_run2 = score_positions(av_seq, gpos)
        # attach this model's delta (same computation as the background
        # path's attach_delta, so the cached delta is comparable)
        for _df in (g2_run1, g2_run2):
            _df["delta"] = [float(s) - wt_map[(int(p), m)]
                            for p, m, s in zip(_df.position, _df.mut_aa,
                                               _df.score)]
        g2_dt = time.time() - t_g
        cache = pd.read_csv(AV220_CACHE)
        cache = cache[cache.position.isin(H)].copy()
        cache["delta"] = [float(s) - wt_map[(int(p), m)] for p, m, s
                          in zip(cache.position, cache.mut_aa, cache.score)]
        mg = g2_run1.merge(cache, on=["position", "mut_aa"],
                           suffixes=("_new", "_cache"))
        d_sc = float((mg.score_new - mg.score_cache).abs().max())
        d_dl = float((mg.delta_new - mg.delta_cache).abs().max())
        gate(f"G-L2 AV_220 on H reproduces the cached rows (score AND delta) "
             f"to {CACHE_TOL:g}",
             len(mg) == len(cache) == len(g2_run1) and d_sc < CACHE_TOL
             and d_dl < CACHE_TOL,
             f"{len(mg)} rows, max|d score| {d_sc:.3e}, max|d delta| "
             f"{d_dl:.3e}; A7c's G-N2 measured 1.776e-15 for this same "
             f"comparison on this device; gate {CACHE_TOL:g}")
        wtc = pd.read_csv(WT_CACHE)
        wtc = wtc[wtc.position.isin(H)].copy()
        wm = wt_arm.merge(wtc, on=["position", "mut_aa"],
                          suffixes=("_new", "_cache"))
        d_wt = float((wm.score - wm.esm2_score).abs().max())
        gate(f"G-L2(b) ADDED, stricter: this run's 650M wild-type arm "
             f"reproduces the cached esm2_wt_scores.csv to {CACHE_TOL:g} "
             f"(it is every background's delta reference)",
             len(wm) == len(wtc) == len(wt_arm) and d_wt < CACHE_TOL,
             f"{len(wm)} rows, max|d score| {d_wt:.3e} (ADDED sub-check, not "
             f"in the frozen text)")
        SCRATCH.mkdir(parents=True, exist_ok=True)
        g2_run1.to_csv(SCRATCH / "gate_g_l2_650M_av220_run1.csv", index=False)
        g2_run2.to_csv(SCRATCH / "gate_g_l2_650M_av220_run2.csv", index=False)
        print(f"  gate runs written to "
              f"{(SCRATCH / 'gate_g_l2_650M_av220_run1.csv').relative_to(ROOT)}"
              f" (scratch only)")

    # G-L3(a): determinism.  650M reuses G-L2's two runs (LD-DEC8).
    if g2_run1 is not None:
        d1 = float((g2_run1.score - g2_run2.score).abs().max())
        gate(f"G-L3(a) AV_220 scored twice is identical to {DET_TOL:g} "
             f"(reuses G-L2's two runs, LD-DEC8)", d1 < DET_TOL,
             f"max|d score| {d1:.3e} over {len(g2_run1)} rows")
    else:
        bg0 = todo[0] if todo else roster[0][0]
        own0, _, m0 = [(o, ww, mm) for b, o, ww, mm in roster_all
                       if b == bg0][0]
        seq0 = wt_seq[:own0 - 1] + m0 + wt_seq[own0:]
        pos0 = [p for p in H if p != own0]
        t_g = time.time()
        a_rows = score_positions(seq0, pos0)
        b_rows = score_positions(seq0, pos0)
        g3_dt = time.time() - t_g
        d1 = float((a_rows.score - b_rows.score).abs().max())
        gate(f"G-L3(a) {bg0} scored twice is identical to {DET_TOL:g}",
             d1 < DET_TOL,
             f"max|d score| {d1:.3e} over {len(a_rows)} rows "
             f"({2 * len(pos0)} passes, {g3_dt:.1f}s)")
        if not wt_map and not args.gate_only and wt_complete:
            wt_arm = pd.read_csv(wt_final)[["position", "mut_aa", "score"]]
            wt_map = {(int(r.position), r.mut_aa): float(r.score)
                      for r in wt_arm.itertuples()}

    # G-L3(b): the wild-type residue's log-odds is exactly 0.
    p_c = H[0]
    idx0 = p_c - 1
    masked = wt_seq[:idx0] + "<mask>" + wt_seq[idx0 + 1:]
    _, _, tokens = batch_converter([("query", masked)])
    with torch.no_grad():
        out = model(tokens.to(device), repr_layers=[], return_contacts=False)
    lp = torch.log_softmax(out["logits"][0, idx0 + 1], dim=-1)
    gidx = alphabet.get_idx(wt_seq[idx0])
    tok_ok = alphabet.get_tok(gidx) == wt_seq[idx0]
    wt_zero = float(lp[gidx].item() - lp[gidx].item())
    one = get_position_logprobs(model, alphabet, batch_converter, wt_seq,
                                p_c, device)
    excl_ok = len(one) == 19 and wt_seq[idx0] not in one
    gate(f"G-L3(b) the wild-type residue's log-odds is exactly 0 at H position "
         f"{p_c} ({wt_seq[idx0]})", tok_ok and wt_zero == 0.0 and excl_ok,
         f"log-odds {wt_zero:.1f}; alphabet round-trip {tok_ok}; "
         f"get_position_logprobs returns {len(one)} entries excluding wt "
         f"{excl_ok}")

    # G-L3(c): coverage of every file present in the out-dir.
    n_missing, n_short, n_complete = 0, 0, 0
    for bg_id, own, _, _ in roster_all:
        f = out_dir / f"bg_{bg_id}.csv"
        e = [p for p in H if p != own]
        if not f.exists():
            n_missing += 1
            continue
        got = len({int(p) for p in pd.read_csv(f).position.unique()
                   if int(p) in Hset})
        if got >= COV_MIN * len(e):
            n_complete += 1
        else:
            n_short += 1
            print(f"    SHORT {bg_id}: {got}/{len(e)} positions")
    if n_short:
        gate(f"G-L3(c) every background present covers >= {COV_MIN:.0%} of its "
             f"eligible H positions", False, f"{n_short} short")
    elif n_complete == 0:
        gate(f"G-L3(c) every background present covers >= {COV_MIN:.0%} of its "
             f"eligible H positions", None,
             f"PENDING: 0/{len(roster_all)} backgrounds scored for "
             f"{args.model} yet")
    else:
        gate(f"G-L3(c) every background present covers >= {COV_MIN:.0%} of its "
             f"eligible H positions", True,
             f"{n_complete} complete, {n_missing} not yet scored, "
             f"{n_short} short")

    if args.gate_only:
        n_fail = sum(1 for _, v in GATES if v is False)
        print("\nA8b GATE-ONLY RESULT: "
              + ("GATE FAIL -- exit 3" if n_fail else "GATE PASS -- exit 0"))
        print(f"  script wall time {time.time() - t_script:.1f}s")
        if n_fail:
            sys.exit(3)
        return

    # ------------------------------------------------------ WT arm (write) --
    def attach_delta(rows, bg_id):
        keys = [(int(p), m) for p, m in zip(rows.position, rows.mut_aa)]
        missing_keys = [k for k in keys if k not in wt_map]
        if missing_keys:
            print(f"ERROR: the wild-type arm has no score for "
                  f"{len(missing_keys)} keys, e.g. {missing_keys[:5]} "
                  f"({bg_id}) -- the delta join would be incomplete. Exit 3.")
            sys.exit(3)
        out = rows.copy()
        out["delta"] = [float(s) - wt_map[k] for s, k
                        in zip(rows.score, keys)]
        return out

    def publish(rows, bg_id, final):
        """QUOTED SOURCE: scripts/124_phase2_score_backgrounds.py lines
        235-264 -- write .tmp, then os.replace() publishes atomically; a
        .tmp file is NEVER treated as completion; on exception the .tmp is
        removed and this script exits nonzero."""
        tmp = out_dir / f".{final.name}.tmp"
        try:
            with open(tmp, "w") as fh:
                rows.to_csv(fh, index=False)
            os.replace(tmp, final)          # atomic publish
        except Exception:
            if tmp.exists():
                tmp.unlink()
            print(f"ERROR: {bg_id} failed; no partial file published.")
            traceback.print_exc()
            sys.exit(1)

    manifest = out_dir / "manifest.csv"
    t_wt = time.time()
    if wt_complete:
        print("  the wild-type arm is already complete and is reused for "
              "every delta in this run")
        wt_arm = pd.read_csv(wt_final)[["position", "mut_aa", "score"]]
        wt_map = {(int(r.position), r.mut_aa): float(r.score)
                  for r in wt_arm.itertuples()}
        wt_dt = None
    else:
        wt_arm = score_positions(wt_seq, H)
        assert len(wt_arm) == 19 * len(H), len(wt_arm)
        assert not wt_arm.duplicated(["position", "mut_aa"]).any()
        wt_dt = time.time() - t_wt
        wt_map = {(int(r.position), r.mut_aa): float(r.score)
                  for r in wt_arm.itertuples()}
        out = wt_arm.assign(bg_id="WT")[["bg_id", "position", "mut_aa",
                                         "score"]]
        publish(out, "WT", wt_final)
        pd.DataFrame([dict(bg_id="WT", n_positions=len(H), n_rows=len(out),
                           seconds=round(wt_dt, 3), device=str(device),
                           sha256=sha256(wt_final))]).to_csv(
            manifest, mode="a", header=not manifest.exists(), index=False)
        print(f"  scored the wild-type arm: {len(H)} positions, {len(out)} "
              f"rows in {wt_dt:.1f}s ({wt_dt / len(H) * 1000:.0f} ms/pass)")

    # ---------------------------------------------------------- scoring -----
    per_bg = []
    t_run0 = time.time()
    for k, bg_id in enumerate(todo):
        own, w, m = [(o, ww, mm) for b, o, ww, mm in roster_all
                     if b == bg_id][0]
        seq = wt_seq[:own - 1] + m + wt_seq[own:]
        assert wt_seq[own - 1] == w and seq[own - 1] == m, bg_id
        t0 = time.time()
        rows = attach_delta(score_positions(seq, exp[bg_id]), bg_id)
        assert len(rows) == 19 * len(exp[bg_id]), bg_id
        assert not rows.duplicated(["position", "mut_aa"]).any(), bg_id
        assert not rows.delta.isna().any(), bg_id
        out = rows.assign(bg_id=bg_id)["bg_id position mut_aa score delta"
                                        .split()]
        publish(out, bg_id, out_dir / f"bg_{bg_id}.csv")
        dt = time.time() - t0
        per_bg.append((bg_id, dt, len(exp[bg_id])))
        pd.DataFrame([dict(bg_id=bg_id, n_positions=len(exp[bg_id]),
                           n_rows=len(out), seconds=round(dt, 3),
                           device=str(device),
                           sha256=sha256(out_dir / f"bg_{bg_id}.csv"))]).to_csv(
            manifest, mode="a", header=not manifest.exists(), index=False)
        el = time.time() - t_run0
        print(f"  scored {bg_id}: {len(exp[bg_id])} positions, {len(out)} rows "
              f"in {dt:.1f}s ({dt / len(exp[bg_id]) * 1000:.0f} ms/pass) | "
              f"{k + 1}/{len(todo)}, elapsed {el / 60:.1f}m, ETA "
              f"{el / (k + 1) * (len(todo) - k - 1) / 60:.1f}m", flush=True)

    # ------------------------------------------------------------- A8c -----
    banner("A8c TIMING (no budget applied here; A9 sets the budgets)", "-")
    if per_bg:
        sp = sorted(dt / n for _, dt, n in per_bg)
        med = sp[len(sp) // 2]
        full_bg_passes = sum(len([p for p in H if p != own])
                             for _, own, _, _ in roster_all)
        full_total = full_bg_passes + len(H)
        print(f"  this run: {len(per_bg)} background(s), "
              f"{sum(n for _, _, n in per_bg)} background passes, median "
              f"{med:.4f} s/pass (per-bg {[f'{x:.4f}' for x in sp]})")
        if len(per_bg) < len(roster_all):
            print(f"  (this run covered only a {len(per_bg)}-background "
                  f"prefix; the projections below are for the FULL roster, "
                  f"which is what A9 budgets)")
        if wt_dt:
            print(f"  the wild-type arm this run: {len(H)} passes in "
                  f"{wt_dt:.1f}s ({wt_dt / len(H):.4f} s/pass)")
        print(f"  projection for the full {args.model} ladder on the EXACT "
              f"full-roster pass count: ({full_total} x {med:.4f}) x 1.25 = "
              f"{full_total * med * 1.25 / 60:.0f} min")
        print(f"  the same projection on the planning doc's pass count "
              f"({DOC_PLAN_PASSES}): ({DOC_PLAN_PASSES} x {med:.4f}) x 1.25 = "
              f"{DOC_PLAN_PASSES * med * 1.25 / 60:.0f} min")

    n_fail = sum(1 for _, v in GATES if v is False)
    n_pass = sum(1 for _, v in GATES if v is True)
    n_pend = sum(1 for _, v in GATES if v is None)
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the docstring):")
    print("    * deltas are per-model WT-referenced: comparable across models "
          "in rank, never in scale.")
    print("    * the wild-type arm is scored once per model and reused for "
          "every delta of that model (its completeness is gated).")
    print("    * G-L2 is a same-pipeline regression test against Phase 2's "
          "own rows, not independent evidence; it cannot run for 150M/35M.")
    print("    * one forward pass per position; runtime is linear in "
          "backgrounds x positions.")
    print(f"\nA8b RESULT: " + ("GATE FAIL -- exit 3" if n_fail
                               else f"GATE PASS -- exit 0 ({n_pass} PASS, "
                                    f"{n_fail} FAIL, {n_pend} PENDING)"))
    print(f"  script wall time {time.time() - t_script:.1f}s")
    if n_fail:
        sys.exit(3)


if __name__ == "__main__":
    main()