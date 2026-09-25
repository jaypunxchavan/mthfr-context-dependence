"""
Script 86 (task AC4c/AC4d, group AC of DETECTION_FLOOR_AND_MECHANISM.md):
score MTHFR with ALL FIVE ESM-1v ensemble members (the evaluator's top-3
pick), staged fetch-score-delete, then the cross-member agreement analysis
and the decisive AC4d verdict.

AC4's exact text (task doc L189-207), quoted:
    AC4b. fetch all 5 ESM-1v ensemble members ... same size-verification
      discipline as before (confirm the 7.83GB-per-member figure by
      loading and counting parameters -- optimizer state in the checkpoint
      is the most likely explanation per the evaluator, verify rather than
      assume).  Check total available disk space before starting and
      report it.
    AC4c. Score MTHFR with each of the 5 members, same procedure as
      650M/150M.  Compute delta_ESM-vs-e.b for each of the 5, AND the
      cross-member agreement on WT scores vs cross-member agreement on
      the delta-vs-e.b correlations themselves.
    AC4d. State the decisive verdict plainly: if the five members agree
      tightly on WT scores but scatter across zero (some positive, some
      negative) on their delta-vs-e.b correlation, that is strong
      evidence the "epistasis signal" reported elsewhere in this project
      is seed noise rather than a stable model property.  If they agree
      in direction too, that's evidence for a real, reproducible signal.
      Either answer is valuable -- report whichever the data shows.

WEIGHTS PROVENANCE SAGA (disclosed per AGENTS 6; decided 2026-09-25,
the user's staging authorization was for "fetch its model weights
yourself -- <=3GB per file, one member's weights on disk at a time,
fetch-score-delete"):
    * Canonical source dl.fbaipublicfiles.com (fair-esm's only official
      host; AC4b's Range probes there returned HTTP 206 x5 on 2026-09-23
      with total_bytes=7,828,635,339 for each member) now returns
      HOST-WIDE HTTP 403: two full attempts today (16:09:25, 16:16:43,
      both curl rc=56 / HTTP 403 in 0.3s), plus read-only probes of the
      root URL, a known-good file (esm2_t33_650M_UR50D.pt), HEAD, Range,
      browser UA, and urllib -- all 403.  This host served this project's
      esmfold/esm3b downloads as recently as 2026-09-24 10:28, so the
      block started between then and now (server-side; cannot be fixed
      from here).
    * Fallback chosen: Meta's OWN official HuggingFace repos
      facebook/esm1v_t33_650M_UR90S_{1..5} (discovered via HF API query,
      not guessed).  They carry pytorch_model.bin = 2,609,603,341 B --
      the fp32 weights in Transformers format, NOT the 7.83GB original
      fair-esm .pt (no byte-identical mirror of the original exists;
      Rocketknight1's copy is the same conversion).  2,609,603,341 B is
      also < 3GB, inside the standing fetch cap.
    * Consequence (disclosed): scoring therefore runs through the
      HuggingFace Transformers ESM implementation instead of fair-esm's.
      The PROCEDURE (masked-marginal log-odds, one forward per position,
      WT + A222V backgrounds, scripts 10/11's position set, same
      subtraction) is unchanged; the LIBRARY differs.  R5's three-way
      parity gate exists precisely to keep this honest: fair-esm and
      Transformers must reproduce the project's OWN historical
      esm2_wt_scores.csv values on the same model to 1e-3 before any
      ESM-1v member is scored.  (ESM-2 650M and ESM-1v 650M are the same
      architecture class and tokenizer; parity is established on the
      sibling for which BOTH libraries' weights are obtainable -- the
      original ESM-1v .pt is unreachable while the CDN is blocked, so
      direct ESM-1v cross-library parity cannot be run today.  This is a
      real limitation, stated here, not papered over.)

STAGES (env STAGE):
    parity   -- R5 three-way parity gate (once, before any member).
    member   -- fetch+score+delete ONE member (env MEMBER=1..5).
    summ     -- R6/R7 analysis across the 5 member CSVs + AC4d verdict.
Other env: N_BOOT (default 10000), SMOKE=1 (member: 4 positions, keeps
the file instead of deleting; parity always uses its 8 fixed positions --
it IS a gate, run once; summ: N_BOOT=300 machinery run).

PRE-REGISTERED RULES (fixed in this docstring BEFORE any run; AGENTS 6)
------------------------------------------------------------------
R1  Staging: at most ONE member's files exist under the staging dir at
    any time.  The member stage refuses to start (exit 1) if any OTHER
    member's directory is present, deletes the current member's
    directory only AFTER its CSV is written, and fetches only
    pytorch_model.bin + config.json + vocab.txt + tokenizer_config.json
    + special_tokens_map.json (tf_model.h5 excluded: duplicate format,
    wasted 2.61GB).  Disk available is printed before every fetch and
    the fetch aborts (exit 1) if avail < bin size + 1GiB.
R2  Size/identity gates: pytorch_model.bin must match its OWN repo's
    HF-API size -- 2,609,603,341 B for each esm1v member, 2,609,621,831 B
    for the esm2 parity checkpoint (the first parity attempt used the
    esm1v size for esm2 and failed its gate at 2,609,621,831 != 
    2,609,603,341; code fixed before any scoring, disclosed) -- else exit 1;
    its md5 is computed and printed BEFORE deletion (provenance record).
    AC4b verification (verify, do not assume): count parameters from the
    loaded model; report fp32 bytes = params*4 and the ratio
    7,828,635,339 / fp32_bytes.  The optimizer-state explanation is
    ACCEPTED only if that ratio lies in [2.99, 3.01] (model + Adam first
    moment + Adam second moment = 3 fp32 copies); otherwise print
    "ratio UNEXPECTED -- do not assume the optimizer explanation".
    Direct inspection of the original .pt's keys is NOT possible while
    the CDN 403s; that residual is logged, not claimed.
R3  Scoring procedure = scripts 10/11 exactly: same atlas position set
    (load_primary_maps hgvs_pro regex), same P42898 FASTA, same A222V
    construction (wt[:221] + "V" + wt[222:], assert wt[221] == "A"),
    one masked forward per position per background, score = logP(mut) -
    logP(bg-wt) at the masked position (scripts.lib.esm_scoring's
    get_position_logprobs math, reimplemented only where the library
    differs), delta_esm_member = S(v|A222V bg) - S(v|WT bg) (script 16's
    model_C - model_A subtraction).  Device: get_device() with an
    explicit one-forward probe; on MPS failure print the exception and
    fall back to CPU with a printed budget warning (never silent).
R4  Row accounting at every step (AGENTS 5): positions scored, rows per
    background, merged rows, analysis join size; the join to
    task32_analysis_table must be EXACTLY 10,757 rows / 654 positions
    (same base as script 32's anchor), else exit 1.
R5  Parity gate (STAGE=parity), three-way, positions
    [10, 100, 222, 354, 429, 594, 600, 650] x their 19 non-WT alts:
    (a) historical artifact esm2_wt_scores.csv; (b) fair-esm +
    local original esm2_t33_650M_UR50D.pt via the project's own
    get_position_logprobs; (c) Transformers + facebook/esm2_t33_650M_
    UR50D (fetched, then deleted).  Require max|b-a| < 1e-3 AND
    max|c-b| < 1e-3 (fp32 device/op-order tolerance, same 1e-3 as script
    70's G3 precedent), else exit 1 printing the argmax location.  The
    fair-esm snapshot for (c) is deleted after the gate.
R6  Per-member analysis: delta_k = av_logodds - wt_logodds on the joined
    10,757-row frame; rho(delta_k, own_e_b) PRIMARY and
    rho(delta_k, GI_folinate_independent) secondary, both via
    scripts.lib.stats.position_cluster_bootstrap (cluster=position,
    n_boot=N_BOOT, seed=0 -- script 32's exact estimator), reporting
    observed_rho, ci_lo, ci_hi, p_boot (p=0 -> report p < 1/N_BOOT).
R7  Agreement + verdict:
    a) WT-score agreement: all 10 member pairs' Spearman over the
       joined 10,757 rows of wt_logodds; report min/median/max.
    b) delta-score agreement (supplementary): same 10 pairs on
       delta_k vectors.
    c) Agreement of the delta-vs-e.b correlations THEMSELVES: the 5
       observed rhos with mean/SD/min/max, sign count, and how many
       CIs exclude zero.
    d) AC4d verdict = the task's own dichotomy, no new thresholds:
       mixed signs among the 5 rhos -> "seed noise" branch; all five
       same sign -> "reproducible signal" branch (k/5 CI-excluding-zero
       reported alongside).  Report whichever the data shows.
R8  Ensemble provenance diagnostic: mean-member wt_logodds vs
    ProteinGym's ESM1v_ensemble column, Spearman computed RAW (printed)
    and after per-position mean-centering (convention-invariant);
    the centered value must exceed 0.99 else exit 1 (indexing/orientation
    sanity for the swapped scoring path).  This is machinery sanity, not
    a hypothesis test; it is my addition, disclosed here as such.

LIMITATIONS (printed at runtime too, AGENTS 6): see the provenance saga
above -- canonical-host block, Transformers-format weights, parity on the
sibling model only, optimizer-state accepted on arithmetic (3.00x) rather
than direct key inspection, and transformers/huggingface_hub/torch
versions printed at start for reproducibility.
"""
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = os.environ.get("SMOKE", "") == "1"
STAGE = os.environ.get("STAGE", "summ")
MEMBER = int(os.environ.get("MEMBER", "0"))

REPO = Path(__file__).resolve().parents[1]
PROC = REPO / "data" / "processed"
TMP = Path("/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode")
STAGING = TMP / "esm1v"
FASTA = REPO / "data" / "raw" / "P42898.fasta"
T32 = PROC / "task32_analysis_table.csv"
ESM2_CSV = PROC / "esm2_wt_scores.csv"
PG = REPO / "data" / "external" / "ProteinGym" / "MTHR_HUMAN_Weile_2021_scores.csv"

EXPECTED_BIN = 2_609_603_341          # esm1v repos, HF API, probed 2026-09-25
EXPECTED_BIN_ESM2 = 2_609_621_831     # esm2_t33_650M_UR50D repo, HF API (the two
                                      # files are NOT the same size -- first parity
                                      # attempt failed on this, disclosed)
ORIGINAL_FTP_BYTES = 7_828_635_339    # fbaipublicfiles Range probe (deepdive [AC4])
HF_FILES = ["pytorch_model.bin", "config.json", "vocab.txt",
            "tokenizer_config.json", "special_tokens_map.json"]
PARITY_POS = [10, 100, 222, 354, 429, 594, 600, 650]
PARITY_TOL = 1e-3
ENSEMBLE_CENTERED_TOL = 0.99


def log(msg):
    print(f"[AC4] {msg}", flush=True)


def load_wt_seq():
    seq = "".join(l.strip() for l in open(FASTA) if not l.startswith(">"))
    assert len(seq) == 656, f"FASTA length {len(seq)} != 656"
    assert seq[221] == "A", f"expected A at 222, found {seq[221]}"
    return seq


def atlas_positions():
    from scripts.lib.io import load_primary_maps
    import re
    maps = load_primary_maps()
    atlas_variants = set(maps["hgvs_pro"].unique())
    return sorted({
        int(m.group(1))
        for h in atlas_variants
        for m in [re.match(r"p\.[A-Za-z]{3}(\d+)", str(h))] if m
    }), atlas_variants


def avail_bytes():
    st = os.statvfs(TMP)
    return st.f_bavail * st.f_frsize


def stage_dirs():
    if not STAGING.exists():
        return []
    return [p for p in STAGING.iterdir() if p.is_dir()]


def hf_fetch(k):
    from huggingface_hub import snapshot_download
    others = [p for p in stage_dirs() if p.name != f"member{k}"]
    if others:
        log(f"STAGING VIOLATION: other member dirs present: {[p.name for p in others]} -- exit")
        sys.exit(1)
    dest = STAGING / f"member{k}"
    need = EXPECTED_BIN + (1 << 30)  # bin + 1GiB margin
    av = avail_bytes()
    log(f"disk before fetch: avail={av:,} B ({av/2**30:.2f} GiB); "
        f"required >= {need:,} B (AC4b: check and report)")
    if av < need:
        log("insufficient disk -- exit")
        sys.exit(1)
    repo = f"facebook/esm1v_t33_650M_UR90S_{k}"
    log(f"fetching {repo} files {HF_FILES} -> {dest} (resume-capable; tf_model.h5 excluded)")
    t0 = time.time()
    snapshot_download(repo_id=repo, allow_patterns=HF_FILES, local_dir=str(dest))
    log(f"fetch done in {time.time()-t0:.0f}s")
    binp = dest / "pytorch_model.bin"
    size = binp.stat().st_size
    if size != EXPECTED_BIN:
        log(f"SIZE GATE FAIL: {size} != {EXPECTED_BIN} -- exit")
        sys.exit(1)
    log(f"size gate OK: {size:,} B == EXPECTED_BIN")
    t0 = time.time()
    h = hashlib.md5()
    with open(binp, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    log(f"md5({binp.name}) = {h.hexdigest()}  (computed in {time.time()-t0:.0f}s; "
        f"recorded before staged deletion -- provenance)")
    return dest


def masked_marginal_tf(tok, model, seq, pos_1idx, device, torch):
    """scripts.lib.esm_scoring.get_position_logprobs math, Transformers lib."""
    from scripts.lib.esm_scoring import AA_LIST
    idx0 = pos_1idx - 1
    wt_aa = seq[idx0]
    masked = seq[:idx0] + "<mask>" + seq[idx0 + 1:]
    enc = tok(masked, return_tensors="pt")
    input_ids = enc["input_ids"].to(device)
    with torch.no_grad():
        logits = model(input_ids=input_ids).logits
    token_pos = idx0 + 1  # BOS/<cls> offset, same as fair-esm
    lp = torch.log_softmax(logits[0, token_pos], dim=-1)
    wt_score = lp[tok.convert_tokens_to_ids(wt_aa)].item()
    return {aa: lp[tok.convert_tokens_to_ids(aa)].item() - wt_score
            for aa in AA_LIST if aa != wt_aa}


def score_member(k):
    from transformers import AutoTokenizer, EsmForMaskedLM
    import torch
    from scripts.lib.esm_scoring import get_device

    dest = hf_fetch(k)
    seq = load_wt_seq()
    av_seq = seq[:221] + "V" + seq[222:]
    positions, _ = atlas_positions()
    if SMOKE:
        positions = positions[:4]
    log(f"positions to score: {len(positions)} (SMOKE={SMOKE})")

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(str(dest))
    model = EsmForMaskedLM.from_pretrained(str(dest))
    model.eval()
    load_s = time.time() - t0
    n_params = sum(p.numel() for p in model.parameters())
    fp32_bytes = n_params * 4
    ratio = ORIGINAL_FTP_BYTES / fp32_bytes
    log(f"AC4b param count: {n_params:,} ({n_params/1e6:.1f}M) loaded in {load_s:.0f}s")
    log(f"AC4b fp32 model bytes = {fp32_bytes:,}; original .pt figure (Range probe) "
        f"= {ORIGINAL_FTP_BYTES:,}; ratio = {ratio:.4f}")
    if 2.99 <= ratio <= 3.01:
        log("AC4b VERIFIED (arithmetic): ratio ~3.00 -> original = model + Adam first "
            "moment + Adam second moment (3 fp32 copies) -- optimizer-state explanation "
            "CONFIRMED against both independently measured sizes; direct key inspection "
            "of the original .pt residual: NOT POSSIBLE while dl.fbaipublicfiles.com "
            "returns 403 (attempt history in docstring).")
    else:
        log(f"AC4b ratio UNEXPECTED ({ratio:.4f}) -- do NOT assume the optimizer "
            "explanation; investigate before quoting.")

    device = get_device()
    model = model.to(device)
    try:
        probe = masked_marginal_tf(tok, model, seq, positions[0], device, torch)
        log(f"device probe on {device}: OK (1 forward, {len(probe)} alts)")
    except Exception as e:
        device = torch.device("cpu")
        model = model.to(device)
        log(f"device probe on MPS FAILED: {e!r} -- fell back to CPU "
            f"(DISCLOSED: slower; member may hit the 90-min supervisor cap)")

    t0 = time.time()
    rows_wt, rows_av = [], []
    n_done = 0
    for pos in positions:
        sw = masked_marginal_tf(tok, model, seq, pos, device, torch)
        for mut, v in sw.items():
            rows_wt.append({"position": pos, "wt_aa": seq[pos - 1],
                            "mut_aa": mut, "wt_logodds": v})
        sa = masked_marginal_tf(tok, model, av_seq, pos, device, torch)
        for mut, v in sa.items():
            rows_av.append({"position": pos, "wt_aa": seq[pos - 1],
                            "mut_aa": mut, "av_logodds": v})
        n_done += 1
        if n_done % 50 == 0 or n_done == len(positions):
            el = time.time() - t0
            rate = n_done / el
            rem = (len(positions) - n_done) / rate
            log(f"progress: {n_done}/{len(positions)} positions ({el:.0f}s elapsed, "
                f"~{rem:.0f}s remaining)")
    score_s = time.time() - t0

    dwt = pd.DataFrame(rows_wt)
    dav = pd.DataFrame(rows_av)
    merged = pd.merge(dwt, dav, on=["position", "wt_aa", "mut_aa"], how="outer")
    merged["delta"] = merged["av_logodds"] - merged["wt_logodds"]
    has222 = 222 in positions
    expected = ((len(positions) - 1) * 19 + 20) if has222 else len(positions) * 19
    log(f"row accounting: wt_rows={len(dwt)} av_rows={len(dav)} merged={len(merged)} "
        f"expected={expected} -> {'MATCH' if len(merged) == expected else 'MISMATCH -- exit'}")
    if len(merged) != expected:
        sys.exit(1)

    if SMOKE:
        out = PROC / f"task_AC4_esm1v_member{k}_scores_smoke.csv"
    else:
        out = PROC / f"task_AC4_esm1v_member{k}_scores.csv"
    merged.to_csv(out, index=False)
    log(f"[saved] {out} ({len(merged)} rows)")

    total_s = load_s + score_s
    log(f"member {k} timing: fetch+load={load_s:.0f}s (load part) score={score_s:.0f}s "
        f"member-internal total ~= {time.time() - t0 + load_s:.0f}s; "
        f"supervisor cap 5400s = the user's <=90 min/member")
    if not SMOKE:
        shutil.rmtree(dest)
        log(f"staged delete OK: {dest} removed; remaining staged dirs: "
            f"{[p.name for p in stage_dirs()] or 'none'}")
    else:
        log(f"SMOKE: keeping {dest} (will be deleted by the full member run)")
    log("LIMITATIONS (AGENTS 6): Transformers-format weights from Meta's official HF "
        "org because the canonical CDN 403s (docstring saga); procedure (math, "
        "backgrounds, positions, estimator) unchanged; parity gate ran on the ESM-2 "
        "sibling only; optimizer-state verified by 3.00x arithmetic, not key "
        "inspection.")


def parity():
    """R5: fair-esm vs Transformers vs the project's own historical CSV."""
    import torch
    from scripts.lib.esm_scoring import get_device, get_position_logprobs
    import esm
    from transformers import AutoTokenizer, EsmForMaskedLM

    seq = load_wt_seq()
    positions, _ = atlas_positions()
    for p in PARITY_POS:
        if p not in positions:
            log(f"PARITY POS {p} not in atlas positions -- exit")
            sys.exit(1)

    # (a) historical artifact
    hist = pd.read_csv(ESM2_CSV)
    a = hist[hist["position"].isin(PARITY_POS)].set_index(["position", "mut_aa"])["esm2_score"]
    log(f"parity (a): historical esm2_wt_scores.csv rows at parity positions: {len(a)}")

    # (b) fair-esm + local original checkpoint via the project's own function
    device = get_device()
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()
    b_vals = {}
    for pos in PARITY_POS:
        for mut, v in get_position_logprobs(model, alphabet, bc, seq, pos, device).items():
            b_vals[(pos, mut)] = v
    b = pd.Series(b_vals)
    log(f"parity (b): fair-esm get_position_logprobs rows: {len(b)}")

    # (c) Transformers + HF esm2 snapshot (fetched, then deleted)
    from huggingface_hub import snapshot_download
    dest = STAGING / "esm2_parity"
    others = [p for p in stage_dirs() if p.name != "esm2_parity"]
    if others:
        log(f"STAGING VIOLATION: {others} -- exit")
        sys.exit(1)
    log(f"disk before parity fetch: avail={avail_bytes():,} B")
    snapshot_download(repo_id="facebook/esm2_t33_650M_UR50D",
                      allow_patterns=HF_FILES, local_dir=str(dest))
    size = (dest / "pytorch_model.bin").stat().st_size
    if size != EXPECTED_BIN_ESM2:
        log(f"PARITY fetch SIZE GATE FAIL: {size} != {EXPECTED_BIN_ESM2} -- exit")
        sys.exit(1)
    tok = AutoTokenizer.from_pretrained(str(dest))
    tf_model = EsmForMaskedLM.from_pretrained(str(dest)).to(device).eval()
    c_vals = {}
    for pos in PARITY_POS:
        for mut, v in masked_marginal_tf(tok, tf_model, seq, pos, device, torch).items():
            c_vals[(pos, mut)] = v
    c = pd.Series(c_vals)
    log(f"parity (c): Transformers rows: {len(c)}")

    idx = a.index.intersection(b.index).intersection(c.index)
    if len(idx) != 19 * len(PARITY_POS):
        log(f"PARITY join size {len(idx)} != {19*len(PARITY_POS)} -- exit")
        sys.exit(1)
    d_ba = (b[idx] - a[idx]).abs()
    d_cb = (c[idx] - b[idx]).abs()
    ib, ic = d_ba.idxmax(), d_cb.idxmax()
    log(f"max|b-a| = {d_ba.max():.3e} at {ib} (tol {PARITY_TOL:g})")
    log(f"max|c-b| = {d_cb.max():.3e} at {ic} (tol {PARITY_TOL:g})")
    ok = (d_ba.max() < PARITY_TOL) and (d_cb.max() < PARITY_TOL)
    log(f"[G-AC4-PARITY] three-way parity (hist CSV / fair-esm / Transformers): "
        f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        log("PARITY FAIL -- the scoring path for ESM-1v is NOT validated; do not score. Exit.")
        sys.exit(1)
    shutil.rmtree(dest)
    log(f"parity snapshot deleted; staged dirs now: {[p.name for p in stage_dirs()] or 'none'}")
    log("Note (disclosed): parity is fair-esm-vs-Transformers on the ESM-2 sibling; "
        "direct ESM-1v parity impossible while the canonical 7.83GB .pt 403s.")


def summ():
    from scripts.lib.stats import position_cluster_bootstrap, _spearman

    if SMOKE:
        print("*** SMOKE RUN: machinery checks only, NOT findings, NOT for quoting. ***")
    t32 = pd.read_csv(T32)
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent", "delta_esm"]).copy()
    log(f"analysis base from task32: {len(base)} rows / {base['position'].nunique()} "
        f"positions (expect 10757 / 654)")
    if (len(base), base["position"].nunique()) != (10757, 654):
        log("analysis base differs from script 32's published set -- exit")
        sys.exit(1)

    members = {}
    for k in range(1, 6):
        p = PROC / f"task_AC4_esm1v_member{k}_scores.csv"
        if not p.exists():
            log(f"missing {p} -- exit")
            sys.exit(1)
        m = pd.read_csv(p)
        members[k] = m
    ref_rows = len(members[1])
    for k, m in members.items():
        if len(m) != ref_rows:
            log(f"member {k} has {len(m)} rows != member 1's {ref_rows} -- exit")
            sys.exit(1)
    log(f"5 member CSVs loaded, all {ref_rows} rows")

    # join to the analysis base
    joined = {}
    for k, m in members.items():
        j = base.merge(m[["position", "wt_aa", "mut_aa",
                          "wt_logodds", "av_logodds", "delta"]],
                       on=["position", "mut_aa"], how="left", validate="1:1")
        miss = j["delta"].isna().sum()
        if miss:
            log(f"member {k}: {miss} base rows unmatched -- exit (R4: exact join required)")
            sys.exit(1)
        if not (j["wt_aa_x"] == j["wt_aa_y"]).all():
            log(f"member {k}: wt_aa label mismatch vs base -- exit")
            sys.exit(1)
        joined[k] = j
    log(f"R4 join: all 5 members cover the base exactly "
        f"({len(joined[1])} rows / {joined[1]['position'].nunique()} positions)")

    # R6 per-member rhos
    rows = []
    for k in range(1, 6):
        d = joined[k]
        d = d.rename(columns={"delta": f"delta_m{k}"})
        for tgt, label in [("own_e_b", "primary"), ("GI_folinate_independent", "secondary")]:
            r = position_cluster_bootstrap(d, "position", f"delta_m{k}", tgt,
                                           n_boot=N_BOOT, seed=SEED)
            p_str = ("<1/%d" % N_BOOT) if r["p_boot"] == 0 else f"{r['p_boot']:.4f}"
            rows.append({"member": k, "target": label, "target_col": tgt,
                         "observed_rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                         "ci_hi": r["ci_hi"], "p_boot": r["p_boot"],
                         "p_report": p_str})
            log(f"member {k} delta-vs-{tgt} ({label}): "
                f"rho={r['observed_rho']:+.6f} CI=[{r['ci_lo']:+.6f}, "
                f"{r['ci_hi']:+.6f}] p={p_str}")
    res = pd.DataFrame(rows)
    out = PROC / ("task_AC4_esm1v_summary_smoke.csv" if SMOKE
                  else "task_AC4_esm1v_summary.csv")
    res.to_csv(out, index=False)
    log(f"[saved] {out}")

    # R8 ensemble provenance diagnostic vs ProteinGym
    pg = pd.read_csv(PG)
    # ProteinGym's mutant strings are already wt+pos+mut (e.g. "H354R")
    ens = pg.set_index("mutant")["ESM1v_ensemble"]
    # build mutant keys like the atlas: wt + pos + mut
    j1 = joined[1].copy()
    j1["key"] = j1["wt_aa_x"].astype(str) + j1["position"].astype(str) + j1["mut_aa"].astype(str)
    mean_wt = np.zeros(len(j1))
    for k in range(1, 6):
        mean_wt += joined[k]["wt_logodds"].to_numpy()
    mean_wt /= 5
    j1["mean_wt"] = mean_wt
    j1["pg_ens"] = j1["key"].map(ens)
    sub = j1.dropna(subset=["pg_ens"])
    log(f"R8 diagnostic: {len(sub)} rows matched to ProteinGym ESM1v_ensemble")
    raw = _spearman(sub["mean_wt"].to_numpy(), sub["pg_ens"].to_numpy())
    sub = sub.copy()
    sub["mw_c"] = sub["mean_wt"] - sub.groupby("position")["mean_wt"].transform("mean")
    sub["pg_c"] = sub["pg_ens"] - sub.groupby("position")["pg_ens"].transform("mean")
    ctr = _spearman(sub["mw_c"].to_numpy(), sub["pg_c"].to_numpy())
    log(f"R8 raw rho(our ensemble mean wt, PG ESM1v_ensemble) = {raw:.6f} (printed, "
        f"convention-sensitive -- not gated)")
    log(f"R8 per-position-centered rho = {ctr:.6f} (gated > {ENSEMBLE_CENTERED_TOL})")
    if ctr <= ENSEMBLE_CENTERED_TOL:
        log("[G-AC4-ENSEMBLE] FAIL -- swapped scoring path not validated against "
            "Meta's published ESM-1v scores; do NOT interpret member results. Exit.")
        sys.exit(1)
    log("[G-AC4-ENSEMBLE] PASS -- transformers-path ESM-1v scores reproduce "
        "ProteinGym's published ensemble ranks at the per-position level.")

    # R7a/b pairwise member agreement
    def pairs(colfn):
        vals = []
        for k in range(1, 6):
            for l in range(k + 1, 6):
                vals.append((k, l, _spearman(colfn(k), colfn(l))))
        return vals
    wt_pairs = pairs(lambda k: joined[k]["wt_logodds"].to_numpy())
    dl_pairs = pairs(lambda k: joined[k]["delta"].to_numpy())
    for name, pp in [("WT scores", wt_pairs), ("delta scores", dl_pairs)]:
        vals = [v for _, _, v in pp]
        log(f"R7 member-pair Spearman on {name}: min={min(vals):.6f} "
            f"median={np.median(vals):.6f} max={max(vals):.6f} (10 pairs)")

    # R7c the 5 correlation values themselves (primary target)
    prim = res[res["target"] == "primary"].sort_values("member")
    rhos = prim["observed_rho"].tolist()
    excl0 = int((prim.apply(lambda r: (r.ci_lo > 0) or (r.ci_hi < 0), axis=1)).sum())
    log(f"R7c the five delta-vs-own-e.b rhos: {[f'{r:+.6f}' for r in rhos]}")
    log(f"R7c mean={np.mean(rhos):+.6f} sd={np.std(rhos, ddof=1):.6f} "
        f"min={min(rhos):+.6f} max={max(rhos):+.6f}; "
        f"CIs excluding zero: {excl0}/5; signs: "
        f"{sum(r > 0 for r in rhos)} positive / {sum(r < 0 for r in rhos)} negative")

    # R7d AC4d verdict -- the task's own dichotomy, no new thresholds
    pos_n = sum(r > 0 for r in rhos)
    neg_n = sum(r < 0 for r in rhos)
    wt_min = min(v for _, _, v in wt_pairs)
    if pos_n and neg_n:
        branch = ("SEED-NOISE BRANCH: the five members' delta-vs-e.b correlations "
                  "SCATTER ACROSS ZERO (mixed signs) while WT-score agreement is "
                  f"min-pair-rho={wt_min:.6f} -- per AC4d this is strong evidence the "
                  "'epistasis signal' reported elsewhere in this project is seed noise "
                  "rather than a stable model property.")
    else:
        sgn = "positive" if pos_n else "negative"
        branch = (f"REPRODUCIBLE-SIGNAL BRANCH: all five agree in direction ({sgn}) "
                  f"with {excl0}/5 CIs excluding zero; WT-score agreement "
                  f"min-pair-rho={wt_min:.6f} -- per AC4d this is evidence for a real, "
                  "reproducible signal.")
    log(f"AC4d VERDICT: {branch}")
    log("AC4d text honored: both branches pre-registered above; the data's branch "
        "is reported as-is, with all five rhos and CIs printed for the reader.")


if __name__ == "__main__":
    import torch
    import transformers
    import huggingface_hub
    t_start = time.time()
    print(f"Script 86 AC4  STAGE={STAGE} MEMBER={MEMBER} N_BOOT={N_BOOT} seed={SEED} "
          f"SMOKE={SMOKE}")
    print(f"versions: torch={torch.__version__} transformers={transformers.__version__} "
          f"huggingface_hub={huggingface_hub.__version__} numpy={np.__version__}")
    if SMOKE:
        print("*** SMOKE RUN: machinery checks only, NOT findings, NOT for quoting. ***")
    if STAGE == "parity":
        parity()
    elif STAGE == "member":
        if MEMBER not in (1, 2, 3, 4, 5):
            print("MEMBER must be 1..5 -- exit")
            sys.exit(1)
        score_member(MEMBER)
    elif STAGE == "summ":
        summ()
    else:
        print(f"unknown STAGE={STAGE} -- exit")
        sys.exit(1)
    print(f"[total] {time.time()-t_start:.0f}s")
