"""Script 171 (Phase 4 session 4a, Task A7c + A7d) -- Module N neighbour-arm
scorer, gate G-N2, and the A7d timing projection.

PRE-REGISTERED: this docstring was written before the first run of this
script (no score of any kind existed for Module N when it was written).
Binding texts: PHASE4_STRENGTHENING.md A7c/A7d; NEIGHBOUR_ARM_PREREG_v1.md
frozen section 3/4 (scoring protocol) + its Amendment 1 (item 6: the
scoring protocol is unchanged).

DECISIONS, pre-registered here before the first run (printed at startup):

NS-DEC1  No-download guard: before the model is requested, this script
         checks that the local torch.hub cache already holds
         esm2_t33_650M_UR50D.pt AND its -contact-regression.pt; if either
         is missing it prints ERROR and exits 3 WITHOUT calling the ESM
         loader (network use outside the approved A8 list is forbidden;
         a missing checkpoint is a BLOCK, never a download).
NS-DEC2  Frames: H = script 125's held-out positions (455, torch-free
         import, its own gates print); nonH = the 654-position frame
         minus H (199).  Expected positions per background = the chosen
         frame minus the background's own position (frozen PIN-5 / 124's
         semantics, imported from script 124 -- 454 expected on H when
         the own position is in H, else 455).
NS-DEC3  Output contract: per-background file bg_<id>.csv with columns
         bg_id, position, mut_aa, score, delta -- score is the
         masked-marginal log-odds from get_position_logprobs (scripts
         124 protocol: ONE unbatched forward pass per (background,
         position), all 19 substitutions from that pass, ESM-2 650M,
         eval mode, torch.no_grad inside the library), and delta = score
         minus the CACHED WT-background esm2_score for that
         (position, mut_aa) (data/processed/esm2_wt_scores.csv, the same
         cache Phase 2 used; the join is asserted complete, no NaN).
         Skip logic and the completeness test are IMPORTED from script
         124 (file_is_complete / expected_positions); the atomic
         write-then-os.replace pattern is quoted from 124's scoring loop
         (QUOTED SOURCE: scripts/124_phase2_score_backgrounds.py lines
         235-264) -- .tmp files never count as complete.
NS-DEC4  Gate G-N2 (HARD, model, scratch directory only -- always in
         data/processed/phase4/neigh_scratch/, never the roster's output
         dir) runs before ANY roster scoring on every invocation that has
         at least one background to score (if every file is already
         complete there is nothing to gate and it is skipped with a
         printed note):
           (a) rescoring AV_220 on H reproduces its cached rows -- max
               |score diff| < 1e-6 AND max |delta diff| < 1e-6 over all
               8,626 (454 positions x 19) cached H rows;
           (b) the same background scored twice in this run is
               identical -- max |diff| == 0.0 exactly (float32 values
               either match bit-for-bit or they do not; if MPS ever
               returned a 1-ulp difference this gate FAILs and the run
               stops rather than tolerating it -- disclosed reading of
               "identical");
           (c) the wild-type residue's log-odds is exactly 0.0 from a
               direct masked pass at a fixed H position (true by the
               definition of masked-marginals; what it actually verifies
               is that the alphabet index for the WT residue resolves to
               that same residue, i.e. no token-mapping bug), and
               get_position_logprobs returns exactly 19 entries that
               exclude the residue at the scored position.
         Any G-N2 failure -> exit 3, before any roster row is written.
NS-DEC5  Model/device: esm_scoring.get_device() (mps on this machine) is
         printed; device is recorded in the manifest; device parity with
         Phase 2 is what makes the 1e-6 cache reproduction meaningful
         (Phase 2 manifest: device=mps).
NS-DEC6  Roster integrity: data/processed/phase4/neigh/roster_v1.csv must
         hash to the value in roster_v1.sha256 (written by script 170
         BEFORE any scoring, G-N1) or this script exits 3 without
         loading the model.  --limit-roster N takes the FIRST N roster
         rows in score_order, i.e. a balanced round-robin prefix.
NS-DEC7  Timing (A7d): after each scored background the elapsed seconds
         are recorded; at exit the script prints the median seconds per
         pass over the backgrounds scored IN THIS RUN and projects the
         full H stage as (total_roster_H_passes x s/pass) x 1.25 against
         the 330-minute budget (total roster H passes computed from the
         frozen roster, 22,719).  The projection formula is fixed by the
         plan and does NOT include G-N2's own ~908 gate passes; that
         cost is disclosed here and absorbed by the 1.25 slack.  If the
         projection exceeds 330 minutes the script says so plainly and
         the stage rule is applied in A9 -- the roster is never shrunk
         to make the budget (frozen Amendment item 6 / A7d).

LIMITATIONS (also printed at the end):
  * delta references the Phase 2 WT cache rather than re-deriving WT
    scores; that is a consistency feature (identical WT cache on both
    sides of the delta) but it inherits any error in that cache.
  * G-N2's cache reproduction compares against rows produced by the same
    library function on the same device -- it is a regression/unit test
    of this pipeline, not independent evidence (AGENTS 6).
  * The A7d s/pass is measured on a 3-background sample; the projection
    assumes the rate is uniform across roster cells and backgrounds
    (Phase 2's own runs varied ~0.5-1.4 s/pass with system load, so the
    1.25 slack may be optimistic -- disclosed).
  * One forward pass per position means no batching: runtime scales
    linearly with backgrounds x positions; there is no caching of
    repeated positions across backgrounds (each background is a
    different sequence).

Usage:
  venv/bin/python3 scripts/171_neigh_score.py --frame H
      [--only BG_ID] [--out-dir DIR] [--limit-roster N]
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

ROSTER = ROOT / "data/processed/phase4/neigh/roster_v1.csv"
ROSTER_SHA = ROOT / "data/processed/phase4/neigh/roster_v1.sha256"
WT_CACHE = ROOT / "data/processed/esm2_wt_scores.csv"
SCRATCH = ROOT / "data/processed/phase4/neigh_scratch"
WT_CKPT = ("esm2_t33_650M_UR50D.pt", "esm2_t33_650M_UR50D-contact-regression.pt")


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_helper(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    t_script = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", choices=["H", "nonH"], default="H")
    ap.add_argument("--only", default=None,
                    help="score/skip only this bg_id")
    ap.add_argument("--out-dir", default="data/processed/phase4/neigh")
    ap.add_argument("--limit-roster", type=int, default=None,
                    help="only first N roster rows in score_order")
    args = ap.parse_args()

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    banner(f"171 -- Module N neighbour-arm scorer  N_BOOT={N_BOOT} "
           f"SEED={SEED} (both UNUSED: no bootstrap/randomness here)  "
           f"frame={args.frame}  out_dir={args.out_dir}")
    print("PRE-REGISTERED DECISIONS (full text in the docstring):")
    for k, v in [
        ("NS-DEC1", "torch.hub cache pre-check for 650M + contact-regression; "
                    "missing -> exit 3, NEVER a download."),
        ("NS-DEC2", f"frame {args.frame}; expected = frame minus own "
                    "(script 124 semantics, imported)."),
        ("NS-DEC3", "bg_<id>.csv = bg_id, position, mut_aa, score, delta; "
                    "delta vs the Phase 2 WT cache; 124's skip logic "
                    "imported, atomic-write pattern quoted from 124."),
        ("NS-DEC4", "G-N2 before any scoring when something is to score: "
                    "AV_220 on H vs cache to 1e-6 (both score and delta), "
                    "same-bg-twice identical to 0.0, WT log-odds 0.0; "
                    "scratch dir only; FAIL -> exit 3."),
        ("NS-DEC5", "device from esm_scoring.get_device(), printed and "
                    "manifested (Phase 2 used mps)."),
        ("NS-DEC6", "roster_v1.csv must hash to its sidecar before the "
                    "model loads; --limit-roster = balanced prefix."),
        ("NS-DEC7", "median s/pass over this run x 22,719 roster H passes "
                    "x 1.25 vs the 330-min budget; G-N2's ~908 passes "
                    "excluded from the formula, disclosed; never shrink "
                    "the roster."),
    ]:
        print(f"  {k}: {v}")

    # ------------------------------------------------- roster integrity ---
    banner("ROSTER INTEGRITY (G-N1 handoff)", "-")
    if not ROSTER.exists() or not ROSTER_SHA.exists():
        print("ERROR: roster_v1.csv or its sha256 sidecar missing; "
              "run script 170 first. Exit 3.")
        sys.exit(3)
    sidecar = ROSTER_SHA.read_text().split()[0]
    actual = sha256(ROSTER)
    if actual != sidecar:
        print(f"ERROR [G-N2 pre]: roster sha256 {actual} != sidecar "
              f"{sidecar}; the frozen roster changed after scoring began. "
              "Exit 3.")
        sys.exit(3)
    print(f"  roster sha256 OK: {actual[:16]}... (frozen before scoring)")

    roster = pd.read_csv(ROSTER)
    if args.limit_roster is not None:
        roster = roster.sort_values("score_order").head(args.limit_roster)
    if args.only is not None:
        roster = roster[roster.bg_id == args.only]
        if len(roster) != 1:
            print(f"ERROR: --only {args.only} matched {len(roster)} rows")
            sys.exit(1)
    roster = roster.sort_values("score_order")

    # ------------------------------------------------------ frames + WT ---
    s125 = load_helper("s125_phase2_analysis", "scripts/125_phase2_analysis.py")
    s124 = load_helper("s124_phase2_score_backgrounds",
                       "scripts/124_phase2_score_backgrounds.py")
    full_frame = sorted(int(p) for p in
                        pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
                        .dropna(subset=["delta_esm", "own_e_b"])
                        .position.unique())
    if len(full_frame) != 654:
        print(f"ERROR: frame {len(full_frame)} (expect 654). Exit 3.")
        sys.exit(3)
    H = sorted(s125.holdout(s125.build_frame()))
    if args.frame == "H":
        frame = H
    else:
        frame = sorted(set(full_frame) - set(H))
    print(f"  frame {args.frame}: {len(frame)} positions "
          f"({'455 held-out' if args.frame == 'H' else '654 - H = 199'})")

    from scripts.lib.sequence import load_sequence, verify_sequence
    wt_seq = load_sequence(str(ROOT / "data/raw/P42898.fasta"))
    verify_sequence(wt_seq)

    wt = pd.read_csv(WT_CACHE)
    wt_map = {(int(r.position), r.mut_aa): float(r.esm2_score)
              for r in wt.itertuples()}
    print(f"  WT cache: {len(wt_map)} (position, mut_aa) rows")

    def delta_of(rows):
        """Attach delta = score - cached WT score; join must be complete."""
        d = [wt_map.get((int(p), m)) for p, m in
             zip(rows["position"], rows["mut_aa"])]
        if any(x is None for x in d):
            miss = [(int(p), m) for p, m, x in
                    zip(rows["position"], rows["mut_aa"], d) if x is None]
            raise SystemExit(f"ERROR: WT cache missing {len(miss)} joins, "
                             f"e.g. {miss[:5]}")
        rows = rows.copy()
        rows["delta"] = [s - x for s, x in zip(rows["score"], d)]
        return rows

    # ---------------------------------------------------------- pre-scan --
    todo = []
    n_skip = 0
    for r in roster.itertuples():
        exp = s124.expected_positions(frame, int(r.position))
        final = out_dir / f"bg_{r.bg_id}.csv"
        if s124.file_is_complete(final, r.bg_id, exp):
            n_skip += 1
            print(f"  SKIP {r.bg_id}: complete ({len(exp) * 19} rows)")
        else:
            todo.append((r, exp))
    print(f"  pre-scan: {n_skip} complete, {len(todo)} to score")
    if not todo:
        print("Nothing to score -> G-N2 not run (it gates scoring, and "
              "no scoring occurs in this invocation).")
        return

    # ------------------------------------------------------- NS-DEC1 ------
    import torch
    ckpt_dir = Path(torch.hub.get_dir()) / "checkpoints"
    missing = [c for c in WT_CKPT if not (ckpt_dir / c).exists()]
    if missing:
        print(f"ERROR [NS-DEC1]: checkpoint(s) missing from the local "
              f"torch.hub cache: {missing} -- this is a BLOCK (the "
              "approved download list does not cover 650M; it must "
              "already be cached). Exit 3. No download attempted.")
        sys.exit(3)
    print(f"  NS-DEC1 local cache OK: {WT_CKPT[0]} "
          f"({(ckpt_dir / WT_CKPT[0]).stat().st_size:,} B) + contact-regression")

    import esm
    from scripts.lib.esm_scoring import get_position_logprobs, get_device

    device = get_device()
    print(f"Using device: {device}")
    print("Loading ESM-2 650M from the local cache (loader never reached "
          "because the cache pre-check passed)...", flush=True)
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    def score_positions(bg_id, seq, positions):
        rows = []
        for p in positions:
            sc = get_position_logprobs(model, alphabet, batch_converter,
                                       seq, p, device)
            for m, s in sc.items():
                rows.append(dict(bg_id=bg_id, position=p, mut_aa=m, score=s))
        return pd.DataFrame(rows, columns=["bg_id", "position",
                                           "mut_aa", "score"])

    # --------------------------------------------------------- G-N2 -------
    banner("G-N2 (HARD) -- AV_220 on H, twice, vs cache; WT zero", "-")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    r220 = pd.read_csv(ROOT / "data/processed/phase2_arm_roster.csv")
    r220 = r220[r220.bg_id == "AV_220"]
    if len(r220) != 1:
        print("ERROR: AV_220 not found in the 96-roster. Exit 3.")
        sys.exit(3)
    r220 = r220.iloc[0]
    own, wt_aa, mut_aa = int(r220.position), r220.wt_aa, r220.mut_aa
    assert wt_seq[own - 1] == wt_aa, (wt_seq[own - 1], wt_aa)
    av_seq = wt_seq[:own - 1] + mut_aa + wt_seq[own:]
    # G-N2 is defined on H regardless of --frame (spec: "AV_220 on H")
    g_positions = [p for p in H if p != own]

    t_g = time.time()
    run1 = delta_of(score_positions("AV_220", av_seq, g_positions))
    run2 = delta_of(score_positions("AV_220", av_seq, g_positions))
    g_dt = time.time() - t_g
    run1.to_csv(SCRATCH / "gate_n2_av220_run1.csv", index=False)
    run2.to_csv(SCRATCH / "gate_n2_av220_run2.csv", index=False)

    cache = pd.read_csv(ROOT / "data/processed/phase2/bg_AV_220.csv")
    cache = cache[cache.position.isin(frame)].copy()
    cache = delta_of(cache)
    m1 = run1.merge(cache, on=["bg_id", "position", "mut_aa"],
                    suffixes=("_new", "_cache"), how="inner")
    d_score = float((m1.score_new - m1.score_cache).abs().max())
    d_delta = float((m1.delta_new - m1.delta_cache).abs().max())
    ok_a = (len(m1) == len(cache) == len(run1)
            and d_score < 1e-6 and d_delta < 1e-6)
    print(f"  (a) AV_220 vs cache: {len(m1)} rows, max|d score| "
          f"{d_score:.3e}, max|d delta| {d_delta:.3e} (gate 1e-6) -> "
          f"{'PASS' if ok_a else 'FAIL'}")

    m2 = run1.merge(run2, on=["bg_id", "position", "mut_aa"],
                    suffixes=("_r1", "_r2"))
    d1 = float((m2.score_r1 - m2.score_r2).abs().max())
    d2 = float((m2.delta_r1 - m2.delta_r2).abs().max())
    ok_b = len(m2) == len(run1) and d1 == 0.0 and d2 == 0.0
    print(f"  (b) same bg twice: {len(m2)} rows, max|d score| {d1:.3e}, "
          f"max|d delta| {d2:.3e} (gate exactly 0.0) -> "
          f"{'PASS' if ok_b else 'FAIL'}")

    # (c) WT residue log-odds == 0.0 from a direct masked pass
    p_c = frame[0]
    idx0 = p_c - 1
    masked = av_seq[:idx0] + "<mask>" + av_seq[idx0 + 1:]
    _, _, tokens = batch_converter([("query", masked)])
    with torch.no_grad():
        out = model(tokens.to(device), repr_layers=[], return_contacts=False)
    lp = torch.log_softmax(out["logits"][0, idx0 + 1], dim=-1)
    gidx = alphabet.get_idx(av_seq[idx0])
    tok_ok = alphabet.get_tok(gidx) == av_seq[idx0]
    wt_logodds = float(lp[gidx].item() - lp[gidx].item())
    one = get_position_logprobs(model, alphabet, batch_converter, av_seq,
                                p_c, device)
    excl_ok = (len(one) == 19 and av_seq[idx0] not in one)
    ok_c = tok_ok and wt_logodds == 0.0 and excl_ok
    print(f"  (c) WT log-odds at pos {p_c} ({av_seq[idx0]}): "
          f"{wt_logodds:.1f} (gate == 0.0), alphabet token round-trip "
          f"{tok_ok}, get_position_logprobs returns {len(one)} entries "
          f"excluding wt {excl_ok} -> {'PASS' if ok_c else 'FAIL'}")

    if not (ok_a and ok_b and ok_c):
        print("G-N2 FAIL -- no roster scoring performed. Exit 3.")
        sys.exit(3)
    print(f"  G-N2 PASS (gate cost {g_dt:.1f}s = {len(g_positions) * 2} "
          "passes, run twice, scratch only; NOT in the A7d projection "
          "formula -- disclosed NS-DEC7)")

    # -------------------------------------------------------- scoring -----
    manifest = out_dir / "manifest.csv"
    t_run0 = time.time()
    per_bg_times = []
    for k, (r, exp) in enumerate(todo):
        bg_id = r.bg_id
        own, wt_aa, mut_aa = int(r.position), r.wt_aa, r.mut_aa
        assert wt_seq[own - 1] == wt_aa, (bg_id, wt_seq[own - 1], wt_aa)
        bg_seq = wt_seq[:own - 1] + mut_aa + wt_seq[own:]
        assert bg_seq[own - 1] == mut_aa, (bg_id, bg_seq[own - 1], mut_aa)

        # QUOTED SOURCE: scripts/124_phase2_score_backgrounds.py lines
        # 235-264 (atomic tmp -> os.replace publish; .tmp never counts;
        # on exception the tmp is removed and the script exits nonzero).
        tmp = out_dir / f".bg_{bg_id}.csv.tmp"
        final = out_dir / f"bg_{bg_id}.csv"
        t0 = time.time()
        try:
            rows = delta_of(score_positions(bg_id, bg_seq, exp))
            assert len(rows) == 19 * len(exp), (bg_id, len(rows),
                                                19 * len(exp))
            assert len({(x, y) for x, y in
                        zip(rows.position, rows.mut_aa)}) == len(rows), bg_id
            assert not rows.delta.isna().any(), bg_id
            with open(tmp, "w") as fh:
                rows.to_csv(fh, index=False)
            os.replace(tmp, final)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            print(f"ERROR: background {bg_id} failed; no partial file "
                  "published; exiting nonzero.")
            traceback.print_exc()
            sys.exit(1)

        dt = time.time() - t0
        per_bg_times.append((bg_id, dt, len(exp)))
        row = dict(bg_id=bg_id, frame=args.frame, n_positions=len(exp),
                   n_rows=len(rows), seconds=round(dt, 3),
                   device=str(device), sha256=sha256(final))
        pd.DataFrame([row]).to_csv(manifest, mode="a",
                                   header=not manifest.exists(), index=False)
        elapsed = time.time() - t_run0
        avg = elapsed / (k + 1)
        eta_s = avg * (len(todo) - k - 1)
        print(f"  scored {bg_id} ({r.cell}): {len(exp)} positions, "
              f"{len(rows)} rows in {dt:.1f}s "
              f"({dt / len(exp) * 1000:.0f} ms/pass) | {k + 1}/{len(todo)}, "
              f"elapsed {elapsed / 60:.1f}m, ETA {eta_s / 60:.1f}m",
              flush=True)

    # ------------------------------------------------------------ A7d -----
    banner("A7d TIMING + PROJECTION (roster is never shrunk)", "-")
    if per_bg_times:
        passes = [n for _, _, n in per_bg_times]
        s_per_pass = sorted(dt / n for _, dt, n in per_bg_times)
        med = s_per_pass[len(s_per_pass) // 2]
        fset = set(frame)
        roster_passes = sum(
            len(frame) - (1 if int(p) in fset else 0)
            for p in pd.read_csv(ROSTER).position)
        proj_min = (roster_passes * med * 1.25) / 60.0
        print(f"  this run: {len(per_bg_times)} backgrounds, "
              f"{sum(passes)} passes, median {med:.3f} s/pass "
              f"(per-bg {[f'{x:.3f}' for x in s_per_pass]})")
        budget_note = (
            f"vs the 330-minute budget -> "
            + ("WITHIN budget" if proj_min <= 330
               else "EXCEEDS BUDGET -- recorded; the A9 stage rule "
                    "applies (roster NOT shrunk)")
            if args.frame == "H" else
            "(the 330-min budget governs the H stage only; the nonH "
            "stage budget is set in A9 from this same formula)")
        print(f"  projection for the {args.frame} stage: "
              f"({roster_passes} roster passes x {med:.3f} s/pass) "
              f"x 1.25 = {proj_min:.0f} min " + budget_note)
        print(f"  G-N2's own gate passes ({len(g_positions) * 2}) are "
              "outside the fixed projection formula (NS-DEC7); at this "
              f"rate they add ~{len(g_positions) * 2 * med * 1.25 / 60:.0f} "
              "min, inside the 1.25 slack.")
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the docstring):")
    print("    * delta uses the Phase 2 WT cache (consistency, but it "
          "inherits that cache's errors).")
    print("    * G-N2 is a regression test of this pipeline against its "
          "own cached rows, not independent evidence.")
    print("    * s/pass from a 3-background sample; Phase 2 varied "
          "~0.5-1.4 s/pass under load.")
    print("\nA7c RESULT: G-N2 PASS -- exit 0")
    print(f"  script wall time {time.time() - t_script:.1f}s")


if __name__ == "__main__":
    main()
