"""Script 169 (Phase 4 session 4a, task A6) -- Module G: GB1 locality of
model shifts versus measured epistasis.  NO TORCH, NO ESM (checked at the
end).  Cached data only; the one optional download (PDB 1PGA) happens only
AFTER the primary G-1/G-2 sections are printed.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements the frozen
`docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md`
(sha256 10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8,
26 lines; gated at start) sections 1-5 exactly.

FROZEN QUANTITIES (prereg section 2; primary threshold Input Count >= 25;
all rows as in script 155; s = |pos(b) - pos(v)| in residues):
  G-1  Per background: lambda_model,b = Spearman(|delta_b(v)|, s);
       lambda_data,b = Spearman(|e_b(v)|, s); d_b = lambda_model,b -
       lambda_data,b.  Across the 400 backgrounds: the mean, SD and
       fraction negative of each, and a background-level bootstrap CI
       (10,000 draws, SEED 0) for the mean of each.
  G-2  Separation strata near 1-5, mid 6-15, far 16-54.  Per background
       and stratum with at least 50 partners: rho_b,stratum =
       Spearman(delta_b, e_b).  Across backgrounds per stratum: the mean
       with a background-level bootstrap CI; and the paired difference
       near - far with its CI.
  G-3  (secondary) If PDB 1PGA chain A Calpha can be obtained and its
       numbering verified against the assayed 56-mer, repeat G-1 and G-2
       with the Calpha distance in place of s, strata < 8, 8-14, > 14 A;
       otherwise skip and say why.  Attempted ONLY after G-1 and G-2 are
       printed (planning doc A6).

FROZEN OUTCOME WORDS (prereg section 3; numeric; decided at N_BOOT=10000):
  MODEL-DECAYS        iff the CI of the mean lambda_model lies entirely
                       below zero.
  DATA-DECAYS         iff the CI of the mean lambda_data lies entirely
                       below zero.
  LOCALITY-DIFFERS    iff the CI of the mean d_b excludes zero.
  SEPARATION-MATTERS  iff the CI of the mean paired difference (near -
                       far) excludes zero; SEPARATION-NOT-RESOLVED
                       otherwise, reported as "n cannot resolve this",
                       never as "no relationship".

FROZEN GATES (prereg section 4; all hard for the item they guard; a FAIL
exits 3):
  G-D0  the prereg hash; the partner table reproduces script 155's
        410,271 rows and its 400 rho_b values (max |diff| < 1e-12 on 10
        sampled backgrounds) and the primary mean -0.009125.
  G-D1  no partner at a background's own position enters.
  G-D2  planted decay on synthetic scores: with |delta| built to decay
        with s plus noise the mean lambda_model is negative with its CI
        below zero; with |delta| independent of s it is not (fire rate
        <= 0.15 over 100 draws).
  G-D3  bootstrap identity, draw-by-draw reference and Phase 1 CI
        reproduction (Phase 1 CI always at N = 10000 fixed, following
        script 155's G-3(iii) precedent: the published interval is a
        10,000-draw quantity, so this sub-gate decides in EVERY mode).

PRE-REGISTERED DECISIONS (G-DEC1..G-DEC8; fixed here before any run):
  G-DEC1  The partner-table construction is script 155's own code,
        EXECUTED VERBATIM from disk at runtime: lines 346-417 (data
        load, F_B,wt pin, partner table incl. the 400-roster merge) and
        431-455 (delta build + coverage gate) are quoted with line
        numbers and exec'd in a copy of this module's globals seeded
        with script 155's constants; the two gates inside them re-run as
        EXTRA hard checks, their names marked [155 transcript].
        Everything else reused is imported from script 155 (load_scores,
        constants, SHAS) via importlib -- never re-implemented (AGENTS
        2).  The 410,271-row count and the rho_b comparison are my own
        gates (G-D0).
  G-DEC2  Qualification: Input Count >= 25, the frozen primary and the
        only threshold here (the locality prereg defines no
        sensitivities).  Script 155's 100-partner floor is retained
        (expected inert; counts printed).  Rows missing a delta are
        dropped with a printed count (script 155's behaviour); the
        recomputed n per background is printed beside the stored
        n_partners_t25 to reconcile the two sources (AGENTS 5).
  G-DEC3  Strata exactly near = 1-5, mid = 6-15, far = 16-54 on
        s = |b_pos - v_pos|, inclusive bounds (s is an integer >= 1); a
        background x stratum enters iff it has >= 50 partners (frozen).
        The paired near - far difference is taken over backgrounds
        having BOTH near and far (n printed).  G-3's distance strata:
        d < 8, 8 <= d <= 14, d > 14 (Angstrom) -- strict outside,
        inclusive middle, exactly as the frozen "< 8, 8-14, > 14".
  G-DEC4  SD is ddof=0 (numpy default; project precedent F5, disclosed
        here too); "fraction negative" counts strict < 0; Spearman via
        p3c.spearman (average ranks; identical maths to script 155).
  G-DEC5  Background-level bootstrap: N_BOOT draws (env, default
        10000), SEED 0, percentile 2.5/97.5 via p3c.pct_ci, resampling
        BACKGROUNDS (the 400 units) with replacement -- never
        positions, never rows.  Draw ids are pre-drawn in
        p3c.background_boot's own loop order (`rng.integers(0, n, n)`
        per draw from default_rng(SEED)), one ids array per sample
        size, SHARED by all statistics of that size (so cross-
        statistic differences are paired).  Every G-1/G-2 statistic's
        draws are checked draw-by-draw against p3c.background_boot
        (same seed) AND against a slow obvious reference over the first
        N_REF draws (G-D3(ii)).
  G-DEC6  G-D2 synthetic construction, fixed here: real geometry (each
        background's real qualifying partner rows and their s values).
        DECAY arm: |delta_syn| = exp(-s/10) * (1 + 0.25 * |Z|), Z ~
        N(0,1), one construction from default_rng(3) streamed in roster
        order (non-negative, monotone in expectation); gate = its
        background-level CI for mean lambda_model lies entirely below
        zero.  NULL arm: exactly 100 datasets (the count is part of the
        frozen rule, so D2_N is a constant, not an env knob), rows
        filled iid |Z| (half-normal; independent of s; non-negative as
        |delta| must be) from one default_rng(1000) stream in roster
        order; a draw FIRES iff the MODEL-DECAYS decision would fire
        (CI of mean lambda_model entirely below zero, same machinery);
        gate = fires / 100 <= 0.15.  Backgrounds whose synthetic vector
        is constant (lambda NaN) are dropped with a printed count, as
        in G-1.
  G-DEC7  Exit rule: every hard gate decides in BOTH modes (there are
        no smoke skips: G-D3(iii) runs at its fixed 10000 in smoke
        too).  Any hard FAIL -> exit 3 in both modes; otherwise exit 0.
        Words are printed as PROVISIONAL when N_BOOT != 10000 (the
        G-1/G-2 CIs are then Monte-Carlo-reduced); the rule text and
        every threshold are identical between modes.
  G-DEC8  G-3 numbering verification: extract chain A Calpha residues;
        accept EXACTLY ONE contiguous, resnum-contiguous match of the
        56-mer assayed sequence (script 155's ASSAYED constant).  If
        there is no such match, fall back to exactly one contiguous,
        resnum-contiguous match of ASSAYED[1:] -- positions 2..56, the
        only positions the analysis ever uses (script 155's POSITIONS)
        -- and say which form matched.  Round-trip residue check over
        every matched position must pass.  If the fetch fails or neither
        form matches uniquely: skip with ONE line giving the reason
        (frozen: "otherwise skip and say why").  No partial or fuzzy
        alignment is ever accepted.

DISCLOSURES (pre-registered here, printed every run):
  (1) Cached-data analysis: the Phase 3 results for these 400
      backgrounds HAVE been seen (prereg line 3); G-1/G-2/G-3 are new
      quantities computed from the same scores -- not out-of-sample.
  (2) EXTRA gates beyond the frozen list (stricter, disclosed): script
      155's F_B,wt pin and its coverage G-4 re-run via the executed
      transcript, the partner-table row count, the n reconciliation
      print, and a final no-torch/no-esm sys.modules check.
  (3) G-D2's decay arm is ONE fixed-seed construction (the frozen text
      describes one construction); the null arm is the frozen 100
      draws.  A single synthetic draw is not a number (AGENTS 3) --
      these are mechanics checks of the gate, not estimates.
  (4) The optional 1PGA download records URL, HTTP status, bytes and
      sha256, obeys the 5 GiB free-disk abort, and is authorised by the
      planning doc (line 46, "RCSB for GB1 PDB 1PGA (GB1D G-3,
      optional)"); on failure G-3 alone skips with a one-line reason
      and nothing is substituted.

LIMITATIONS (printed by the script itself, AGENTS 6):
  * Frozen section 5: this characterises the statistic in GB1 only; no
    sentence here reads for or against any MTHFR or RBD result -- the
    systems, backgrounds and measurement platforms differ.
  * The background-level bootstrap treats the 400 backgrounds as
    independent draws; all deltas within a background share one WT arm
    (disclosed, not modelled; script 155's same caveat).
  * delta_b is read from script 154's cached scores, never recomputed
    from the model here; e_b uses the read-depth-derived W proxy of the
    frozen Phase 3a construction (zero-count doubles kept, printed).
  * G-1's lambda uses |e_b| and |delta| against s (frozen); G-2's
    rho_b,stratum uses the SIGNED delta and e_b (frozen wording
    "Spearman(delta_b, e_b)") -- the two sections answer different
    questions and their numbers are not interchangeable.
  * The G-3 distance repeat drops rows without a Calpha atom (printed);
    its words are secondary and reported beside the primary, never
    instead of it.
  * Reproduction of script 155's rho_b validates this implementation;
    it is a unit test, not new evidence (AGENTS 6).

Usage:
  N_BOOT=300 N_REF=500 venv/bin/python3 scripts/169_gb1_locality.py   # smoke
  N_BOOT=10000 N_REF=500 SEED=0 venv/bin/python3 \\
      scripts/169_gb1_locality.py                                     # full
"""

import hashlib
import importlib
import os
import shutil
import sys
import textwrap
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase3_common as p3c                # noqa: E402

S155 = importlib.import_module("scripts.155_gb1_regime_analysis")

PREREG = (ROOT / "docs" / "tasks" / "phase4-strengthening" / "prereg" /
          "GB1_LOCALITY_PREREG_v1.md")
PREREG_SHA = "10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8"
PREREG_LINES = 26

OUT155 = ROOT / "data" / "processed" / "phase3" / "gb1"
RHO_STORED = OUT155 / "gb1_rho_b_full.csv"
RCSB_DIR = ROOT / "data" / "external" / "rcsb"
PDB_URL = "https://files.rcsb.org/download/1PGA.pdb"

T_CI_LO = -0.1173334458953319
T_CI_HI = -0.05951138449511738
G3III_N = 10000                 # frozen: the published interval is a
                                # 10,000-draw quantity (script 155 G-3(iii))
TOL_12 = 1e-12
TOL_9 = 1e-9
T155_ROWS = 410271              # script 155's printed partner-row count
T155_MEAN = -0.009125           # frozen primary mean rho_b (6 dp)
T155_MEAN_TOL = 1e-6            # rounding tolerance at the printed 6 dp
PRIMARY_T = 25                  # frozen primary threshold
FLOOR = 100                     # script 155's floor (retained, inert)
STRATA = (("near", 1, 5), ("mid", 6, 15), ("far", 16, 54))
MIN_STRATUM = 50                # frozen: >= 50 partners per bg x stratum
D2_N = 100                      # frozen rule count -> constant (G-DEC6)
RCSB_MIN_FREE = 5 * 1024 ** 3   # planning rule 2: abort below 5 GiB free

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_REF = int(os.environ.get("N_REF", "500"))
SEED = int(os.environ.get("SEED", "0"))

GATES = []
TRANSCRIPT = False


def smoke_mode():
    return N_BOOT != 10000


def gate(name, verdict, value, note="", hard=True):
    nm = name + (" [155 transcript]" if TRANSCRIPT else "")
    GATES.append((nm, verdict, hard))
    tail = f"  ({note})" if note else ""
    print(f"  [{verdict}] {nm}: {value}{tail}", flush=True)


def rule(t=""):
    print("\n" + "-" * 78 + (f"\n{t}" if t else "") + "\n" + "-" * 78,
          flush=True)


def banner(t=""):
    print("=" * 78 + (f"\n{t}" if t else "") + "\n" + "=" * 78, flush=True)


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def quote(path, a, b, label):
    lines = Path(path).read_text().splitlines()
    print(f"  QUOTED SOURCE: {label} ({path}, lines {a}-{b}):")
    for i in range(a - 1, min(b, len(lines))):
        print(f"    {i + 1:4d}| {lines[i]}")


# --------------------------------------------------------------------------
# bootstrap machinery (G-DEC5): ids replicate p3c.background_boot's stream
# --------------------------------------------------------------------------
_IDS_CACHE = {}


def bg_ids(n):
    """(N_BOOT, n) int64 ids drawn exactly as p3c.background_boot(seed=SEED)
    draws them internally, so vectorized draws equal its draws."""
    if n not in _IDS_CACHE:
        rng = np.random.default_rng(SEED)
        _IDS_CACHE[n] = np.asarray(
            [rng.integers(0, n, n) for _ in range(N_BOOT)], dtype=np.int64)
    return _IDS_CACHE[n]


def boot_mean_checked(values, label):
    """Background-level bootstrap of mean(values) WITH full G-D3 checks.
    Returns (draws, lo, hi, n_finite)."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    n = v.size
    if n < 2:
        gate(f"G-D3(i) identity {label}", "FAIL", f"n = {n}",
             "need >= 2 finite units")
        gate(f"G-D3(ii) draw-by-draw {label}", "FAIL", f"n = {n}",
             "need >= 2 finite units")
        return np.full(N_BOOT, np.nan), np.nan, np.nan, 0
    ids = bg_ids(n)
    draws = v[ids].mean(axis=1)
    # identity: every unit drawn once reproduces the point estimate
    ident = abs(float(v[np.arange(n)].mean()) - float(np.mean(v)))
    gate(f"G-D3(i) identity {label}", "PASS" if ident < TOL_12 else "FAIL",
         f"|diff| = {ident:.3e}", "every unit once == point estimate")
    # draw-by-draw vs p3c.background_boot (same seed -> same stream)
    ref, _ = p3c.background_boot(v, None, n_boot=N_BOOT, seed=SEED)
    d_ref = float(np.nanmax(np.abs(draws - ref)))
    # draw-by-draw vs slow obvious reference, first N_REF draws
    n_ref = min(N_REF, N_BOOT)
    slow = np.array([float(np.mean([v[i] for i in ids[k]]))
                     for k in range(n_ref)])
    d_slow = float(np.max(np.abs(draws[:n_ref] - slow)))
    gate(f"G-D3(ii) draw-by-draw {label}", "PASS"
         if max(d_ref, d_slow) < TOL_12 else "FAIL",
         f"vs background_boot max|diff| {d_ref:.3e} over {N_BOOT} draws; "
         f"vs slow reference {d_slow:.3e} over {n_ref} draws",
         f"tolerance {TOL_12}")
    lo, hi, nf = p3c.pct_ci(draws)
    return draws, lo, hi, nf


def boot_mean_ci(values):
    """Plain background-level CI (same ids machinery, no re-check) -- used
    by G-D2 and G-3 after G-D3 has validated the machinery on the primary
    statistics (disclosed).  Returns (lo, hi, n_finite)."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return np.nan, np.nan, 0
    draws = v[bg_ids(v.size)].mean(axis=1)
    lo, hi, nf = p3c.pct_ci(draws)
    return lo, hi, nf


def ci_below0(lo, hi):
    """MODEL-DECAYS / DATA-DECAYS rule: CI entirely below zero."""
    return (not np.isnan(lo)) and hi < 0.0


def ci_excludes0(lo, hi):
    """LOCALITY-DIFFERS / SEPARATION-MATTERS rule: CI excludes zero."""
    return (not np.isnan(lo)) and (lo > 0.0 or hi < 0.0)


def main():
    global TRANSCRIPT
    t0 = time.time()
    banner("A6 -- MODULE G: GB1 LOCALITY (GB1_LOCALITY_PREREG_v1.md, "
           "implemented exactly)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}   "
          f"D2_N = {D2_N} (constant, frozen rule)")
    print("RESAMPLING UNIT: backgrounds (the 400 units), one ids set per "
          "sample size shared by all statistics of that size (paired).  "
          "Never positions, never rows.")
    print("DECISION RULE (pre-registered in the docstring): every hard "
          "gate (G-D0..G-D3 + disclosed extras) decides in BOTH modes; "
          "any FAIL -> exit 3.  Thresholds are never loosened; N is never "
          "raised to pass a gate.")
    if smoke_mode():
        print(f"*** SMOKE RUN: N_BOOT={N_BOOT} != 10000 -- every CI and "
              "every word is PROVISIONAL (Monte-Carlo only; G-D3(iii) "
              "still decides at its fixed 10000). ***")
    print("DISCLOSURES (pre-registered in the docstring): (1) cached-data "
          "analysis -- Phase 3 results for these 400 backgrounds have "
          "been seen (prereg line 3); these are NEW quantities from the "
          "same scores; (2) EXTRA gates beyond the frozen list: 155's "
          "F_B,wt pin and coverage G-4 re-run from the executed "
          "transcript, the 410,271-row count, the n reconciliation, and "
          "a final no-torch/no-esm check; (3) G-D2 decay arm = one "
          "fixed-seed construction, null arm = the frozen 100 draws "
          "(mechanics checks, not estimates); (4) the optional 1PGA "
          "download records url/status/bytes/sha256 and skips G-3 alone "
          "on failure.")

    # ======================================================================
    rule("G-D0 -- INFRASTRUCTURE (prereg hash, inputs, partner table, "
         "rho_b reproduction)")
    got = sha256_of(PREREG)
    n_lines = len(PREREG.read_text().splitlines())
    gate("G-D0 prereg sha256", "PASS"
         if (got == PREREG_SHA and n_lines == PREREG_LINES) else "FAIL",
         got, f"target {PREREG_SHA} ({PREREG_LINES} lines; got {n_lines})")
    for p, want in S155.SHAS.items():
        g = sha256_of(p)
        gate("G-D0 input sha256", "PASS" if g == want else "FAIL", g,
             f"{p.relative_to(ROOT)} target {want}")
    quote(PREREG, 9, 22, "frozen quantities + gates (prereg sections 2-4)")

    # (c) executed transcript: script 155 lines 346-417
    src = Path(S155.__file__).read_text().splitlines()
    block_a = textwrap.dedent("\n".join(src[345:417]))   # lines 346..417
    rule("QUOTED+EXECUTED SOURCE A -- script 155 lines 346-417 (data, "
         "F_B,wt pin, partner table)")
    quote(S155.__file__, 346, 417,
          "partner-table construction (executed verbatim, G-DEC1)")
    env = dict(globals())
    env.update(dict(DOUBLES=S155.DOUBLES, SINGLES=S155.SINGLES,
                    ROSTER_FULL=S155.ROSTER_FULL, ROSTER2=S155.ROSTER2,
                    SEQS_CSV=S155.SEQS_CSV, WT_IN=S155.WT_IN,
                    WT_SEL=S155.WT_SEL, ASSAYED=S155.ASSAYED))
    TRANSCRIPT = True
    exec(compile(block_a, f"{S155.__file__}:346-417", "exec"),
         env)                                # noqa: S102 (frozen, quoted)
    TRANSCRIPT = False
    long, ros400, same_pos = env["long"], env["ros400"], env["same_pos"]
    dbl, sgl, F_WT = env["dbl"], env["sgl"], env["F_WT"]
    n_long = len(long)
    gate("G-D0 partner table rows (script 155 printed 410,271)", "PASS"
         if n_long == T155_ROWS else "FAIL", f"{n_long:,}",
         f"target {T155_ROWS:,}")

    # (d) scores + deltas: script 155's load_scores + lines 431-455
    rule("SCORES + DELTAS -- script 155's loader and delta build")
    wt_map, completed, issues = S155.load_scores(OUT155, ros400, "assayed")
    for msg in issues:
        print(f"  note: {msg}")
    print(f"  completed backgrounds (roster order): {len(completed)} of "
          f"{len(ros400)}  | wt_arm present: {wt_map is not None}")
    block_b = textwrap.dedent("\n".join(src[430:455]))   # lines 431..455
    quote(S155.__file__, 431, 455,
          "delta build + coverage gate (executed verbatim, G-DEC1)")
    env["wt_map"], env["completed"] = wt_map, completed
    env["ELIGIBLE_PER_BG"] = S155.ELIGIBLE_PER_BG
    TRANSCRIPT = True
    exec(compile(block_b, f"{S155.__file__}:431-455", "exec"),
         env)                                # noqa: S102 (frozen, quoted)
    TRANSCRIPT = False
    deltas_all = env["deltas_all"]
    ASSAYED = env["ASSAYED"]   # post-hoc runtime fix (disclosed): the smoke run
    # crashed with NameError at G-3 because ASSAYED lived only in `env`. Binding it
    # here pulls the identical object (S155.ASSAYED, already sha-pinned by G-D0);
    # no value, threshold, or decision rule changes.
    print("  [POST-HOC FIX, DISCLOSED] ASSAYED bound from transcript env after "
          "smoke NameError at G-3 (same object, no gate/threshold change)")
    if wt_map is None or not completed:
        print("FATAL: no scores on disk -- G-1/G-2 cannot be computed.")
        sys.exit(3)

    # (e) rho_b recompute, script 155's exact loop form (lines 500-532)
    rule("rho_b RECOMPUTE -- script 155's loop (threshold 25, floor 100, "
         "delta lookup), compared with the stored table")
    per_bg = []
    excluded_floor = 0
    dropped_delta = 0
    for bid, _ in completed:
        q = long[long["background_id"] == bid]
        q = q[q["input_count"] >= PRIMARY_T]
        if len(q) < FLOOR:
            excluded_floor += 1
            continue
        dmap = deltas_all[bid]
        delta, keep_rows = [], []
        for r in q.itertuples():
            d = dmap.get((int(r.v_pos), r.v_mut))
            if d is None:
                dropped_delta += 1
                continue
            delta.append(d)
            keep_rows.append(r)
        if len(keep_rows) < FLOOR:
            excluded_floor += 1
            continue
        eb = np.array([r.e_b for r in keep_rows], dtype=float)
        dl = np.array(delta, dtype=float)
        vpos = np.array([int(r.v_pos) for r in keep_rows])
        bpos = np.array([int(r.b_pos) for r in keep_rows])
        rho = p3c.spearman(dl, eb)
        per_bg.append(dict(background_id=bid, rho_b=rho, n=len(keep_rows),
                           s=np.abs(bpos - vpos), delta=dl, eb=eb,
                           v_pos=vpos, b_pos=int(bpos[0])))
    print(f"  backgrounds with rho_b: {len(per_bg)} | excluded by "
          f"{FLOOR}-floor: {excluded_floor} | partner rows dropped for "
          f"missing delta: {dropped_delta}")
    stored = pd.read_csv(RHO_STORED)
    st_map = {r.background_id: (float(r.rho_b), int(r.n_partners_t25))
              for r in stored.itertuples()}
    ours = {p["background_id"]: p for p in per_bg}
    rng_s = np.random.default_rng(SEED)
    sample_idx = np.sort(rng_s.choice(len(per_bg), 10, replace=False))
    sample_ids = [per_bg[i]["background_id"] for i in sample_idx]
    d_sample = max(abs(ours[b]["rho_b"] - st_map[b][0])
                   for b in sample_ids)
    d_all = max(abs(ours[b]["rho_b"] - st_map[b][0])
                for b in ours if b in st_map)
    gate("G-D0 rho_b reproduces stored table on 10 sampled backgrounds",
         "PASS" if d_sample < TOL_12 else "FAIL",
         f"max|diff| = {d_sample:.3e} (roster positions "
         f"{[int(i) for i in sample_idx]})", f"tolerance {TOL_12}")
    print(f"  [context] all {len(ours)} backgrounds: max|diff| = "
          f"{d_all:.3e} (informational; the gate is the frozen 10)")
    mean_stored = float(stored["rho_b"].mean())
    mean_ours = float(np.mean([p["rho_b"] for p in per_bg]))
    gate("G-D0 primary mean rho_b == -0.009125", "PASS"
         if (abs(mean_stored - T155_MEAN) < T155_MEAN_TOL and
             abs(mean_ours - T155_MEAN) < T155_MEAN_TOL) else "FAIL",
         f"stored {mean_stored!r}, recomputed {mean_ours!r}",
         f"target {T155_MEAN!r} (+/- {T155_MEAN_TOL} at 6 dp)")
    n_diffs = [abs(ours[b]["n"] - st_map[b][1]) for b in ours
               if b in st_map]
    print(f"  [reconcile] n vs stored n_partners_t25: max|diff| = "
          f"{max(n_diffs) if n_diffs else 0} over {len(n_diffs)} "
          f"backgrounds (0 expected; reconcile before interpreting if "
          f"not)")

    # ======================================================================
    rule("G-D1 -- NO PARTNER AT A BACKGROUND'S OWN POSITION")
    same_pos_rows = int(sum(int((p["v_pos"] == p["b_pos"]).sum())
                            for p in per_bg))
    gate("G-D1 own-position partners in the analysis rows", "PASS"
         if same_pos_rows == 0 else "FAIL", f"{same_pos_rows} rows",
         "structural in the doubles table (pos1 != pos2) + re-checked "
         f"here; transcript same_pos = {int(same_pos)}")

    # ======================================================================
    rule("G-D2 -- PLANTED DECAY / PLANTED NULL ON SYNTHETIC |delta| "
         "(real geometry; G-DEC6)")
    # decay arm: |delta| = exp(-s/10) * (1 + 0.25|Z|), rng default_rng(3)
    rng = np.random.default_rng(3)
    lam_syn = []
    for p in per_bg:
        s = p["s"].astype(float)
        dsyn = np.exp(-s / 10.0) * (1.0 + 0.25 * np.abs(
            rng.standard_normal(s.size)))
        lam_syn.append(p3c.spearman(dsyn, s))
    lam_syn = np.asarray(lam_syn, dtype=float)
    finite_syn = np.isfinite(lam_syn)
    lo_d, hi_d, nf_d = boot_mean_ci(lam_syn[finite_syn])
    print(f"  DECAY arm: |delta_syn| = exp(-s/10)*(1+0.25|Z|), "
          f"default_rng(3), roster order; {int(finite_syn.sum())}/400 "
          f"finite lambdas")
    print(f"    mean lambda_model_syn = "
          f"{float(np.mean(lam_syn[finite_syn])):+.6f}  CI95 = "
          f"[{lo_d:+.6f}, {hi_d:+.6f}] ({nf_d} draws)  frac<0 = "
          f"{float(np.mean(lam_syn[finite_syn] < 0)):.4f}")
    gate("G-D2 decay arm: mean lambda_model negative, CI below zero",
         "PASS" if ci_below0(lo_d, hi_d) else "FAIL",
         f"CI = [{lo_d:+.6f}, {hi_d:+.6f}]",
         "MODEL-DECAYS machinery fires on a decaying construction")
    # null arm: D2_N datasets, iid half-normal, independent of s
    rng = np.random.default_rng(1000)
    fire_below, fire_above, includes = 0, 0, 0
    null_means = []
    for _k in range(D2_N):
        lam = []
        for p in per_bg:
            s = p["s"].astype(float)
            dsyn = np.abs(rng.standard_normal(s.size))
            lam.append(p3c.spearman(dsyn, s))
        lam = np.asarray(lam, dtype=float)
        lam = lam[np.isfinite(lam)]
        lo, hi, nf = boot_mean_ci(lam)
        null_means.append(float(lam.mean()))
        if ci_below0(lo, hi):
            fire_below += 1
        elif lo > 0.0:
            fire_above += 1
        else:
            includes += 1
    rate = fire_below / D2_N
    print(f"  NULL arm: {D2_N} datasets, iid |Z| (half-normal, "
          f"independent of s), one default_rng(1000) stream; fire = "
          f"MODEL-DECAYS decision fires")
    print(f"    fires (CI below 0) = {fire_below}/{D2_N} = {rate:.3f} | "
          f"CI above 0 = {fire_above} | CI includes 0 = {includes} | "
          f"mean of null means = {float(np.mean(null_means)):+.6f} "
          f"(must centre on 0 -- printed as its own check)")
    gate(f"G-D2 null arm fire rate <= 0.15 over {D2_N} draws", "PASS"
         if rate <= 0.15 else "FAIL", f"{rate:.3f}",
         "type-I calibration of the MODEL-DECAYS machinery")

    # ======================================================================
    rule("G-D3 -- BOOTSTRAP IDENTITY, DRAW-BY-DRAW REFERENCE, PHASE 1 CI "
         "(hard)")
    lam_m, lam_d, dd = [], [], []
    strata_rho = {name: [] for name, _, _ in STRATA}
    strata_bg = {name: [] for name, _, _ in STRATA}
    for p in per_bg:
        lm = p3c.spearman(np.abs(p["delta"]), p["s"])
        ld = p3c.spearman(np.abs(p["eb"]), p["s"])
        lam_m.append(lm)
        lam_d.append(ld)
        dd.append(lm - ld)
        for name, lo_s, hi_s in STRATA:
            mask = (p["s"] >= lo_s) & (p["s"] <= hi_s)
            if int(mask.sum()) >= MIN_STRATUM:
                strata_rho[name].append(
                    p3c.spearman(p["delta"][mask], p["eb"][mask]))
                strata_bg[name].append(p["background_id"])
    lam_m = np.asarray(lam_m, dtype=float)
    lam_d = np.asarray(lam_d, dtype=float)
    dd = np.asarray(dd, dtype=float)
    n_nan = int((~np.isfinite(lam_m)).sum() + (~np.isfinite(lam_d)).sum())
    print(f"  finite lambdas: lambda_model "
          f"{int(np.isfinite(lam_m).sum())}/400, lambda_data "
          f"{int(np.isfinite(lam_d).sum())}/400 (NaN = constant vector "
          f"or n < 3; NaN lambdas across both: {n_nan})")
    ci_m = boot_mean_checked(lam_m, "mean lambda_model")
    ci_d = boot_mean_checked(lam_d, "mean lambda_data")
    ci_db = boot_mean_checked(dd, "mean d_b")
    str_ci = {}
    for name, _, _ in STRATA:
        arr = np.asarray(strata_rho[name], dtype=float)
        str_ci[name] = boot_mean_checked(arr, f"mean rho_b,stratum [{name}]")
    near_map = dict(zip(strata_bg["near"], strata_rho["near"]))
    far_map = dict(zip(strata_bg["far"], strata_rho["far"]))
    paired_ids = [b for b in near_map if b in far_map]
    paired_diff = np.array([near_map[b] - far_map[b] for b in paired_ids])
    ci_paired = boot_mean_checked(paired_diff, "paired mean (near - far)")
    # G-D3(iii) Phase 1 CI, always at N = 10000 fixed
    rule("G-D3(iii) -- PHASE 1 CI REPRODUCTION ON THE MTHFR ANCHOR ROWS "
         f"(fixed N={G3III_N})")
    tb = time.time()
    from scripts.lib import phase2_diag as pdg
    s125, Aobj = pdg.build(verbose=False)
    ar = Aobj.a222v_rows
    ax = ar.delta.to_numpy(float)
    ay = ar.own_e_b.to_numpy(float)
    draws_p1 = p3c.pos_cluster_boot(ax, ay, ar.position.to_numpy(),
                                    n_boot=G3III_N, seed=SEED)
    lo_p1, hi_p1, nf_p1 = p3c.pct_ci(draws_p1)
    d_lo, d_hi = abs(lo_p1 - T_CI_LO), abs(hi_p1 - T_CI_HI)
    print(f"  anchor rows {len(ar):,} / {ar.position.nunique()} "
          f"positions; {G3III_N} draws in {time.time() - tb:.1f}s "
          f"({nf_p1} finite)")
    print(f"  lo got {lo_p1!r} target {T_CI_LO!r} |diff| = {d_lo:.3e}")
    print(f"  hi got {hi_p1!r} target {T_CI_HI!r} |diff| = {d_hi:.3e}")
    gate("G-D3(iii) Phase 1 CI reproduces (each endpoint < 1e-9)", "PASS"
         if (d_lo < TOL_9 and d_hi < TOL_9) else "FAIL",
         f"|diff| lo = {d_lo:.3e}, hi = {d_hi:.3e}",
         f"tolerance {TOL_9}; Phase 1 published interval")

    # ======================================================================
    prov = "PROVISIONAL (smoke)" if smoke_mode() else ""
    rule("G-1 -- DECAY OF |delta| AND |e_b| WITH SEPARATION s (frozen "
         "section 2)")
    print("  Per background: lambda_model = Spearman(|delta_b(v)|, s), "
          "lambda_data = Spearman(|e_b(v)|, s), d_b = difference; "
          "across-background stats + background-level CI (N_BOOT = "
          f"{N_BOOT}, SEED {SEED}).")
    for label, arr, ci in (("lambda_model (MODEL shifts)", lam_m, ci_m),
                           ("lambda_data (measured epistasis)", lam_d,
                            ci_d),
                           ("d_b = model - data", dd, ci_db)):
        fin = arr[np.isfinite(arr)]
        _dr, lo, hi, nf = ci
        print(f"\n    [{label}] n = {fin.size} backgrounds")
        print(f"      mean = {float(fin.mean()):+.9f}   SD(ddof=0) = "
              f"{float(fin.std()):.9f}   fraction negative = "
              f"{float(np.mean(fin < 0)):.4f}")
        print(f"      CI95 of the mean = [{lo:+.9f}, {hi:+.9f}] "
              f"({nf}/{N_BOOT} finite draws) {prov}".rstrip())
    w_model = ci_below0(ci_m[1], ci_m[2])
    w_data = ci_below0(ci_d[1], ci_d[2])
    w_diff = ci_excludes0(ci_db[1], ci_db[2])
    m_model = "lies entirely below zero" if w_model else \
        "does not lie entirely below zero"
    m_data = "lies entirely below zero" if w_data else \
        "does not lie entirely below zero"
    m_diff = "excludes zero" if w_diff else "includes zero"
    print(f"\n  OUTCOME WORD (frozen section 3): MODEL-DECAYS "
          f"{'FIRES' if w_model else 'does not fire'} -- CI of mean "
          f"lambda_model [{ci_m[1]:+.9f}, {ci_m[2]:+.9f}] {m_model} "
          f"{prov}".rstrip())
    print(f"  OUTCOME WORD (frozen section 3): DATA-DECAYS "
          f"{'FIRES' if w_data else 'does not fire'} -- CI of mean "
          f"lambda_data [{ci_d[1]:+.9f}, {ci_d[2]:+.9f}] {m_data} "
          f"{prov}".rstrip())
    print(f"  OUTCOME WORD (frozen section 3): LOCALITY-DIFFERS "
          f"{'FIRES' if w_diff else 'does not fire'} -- CI of mean d_b "
          f"[{ci_db[1]:+.9f}, {ci_db[2]:+.9f}] {m_diff} {prov}".rstrip())

    # ======================================================================
    rule("G-2 -- rho_b WITHIN SEPARATION STRATA (frozen section 2)")
    print("  Per background x stratum with >= "
          f"{MIN_STRATUM} partners: rho_b,stratum = Spearman(delta_b, "
          "e_b) (SIGNED, as frozen); across-background mean + "
          "background-level CI; paired near - far with CI.")
    for name, lo_s, hi_s in STRATA:
        arr = np.asarray(strata_rho[name], dtype=float)
        arr_f = arr[np.isfinite(arr)]
        _dr, lo, hi, nf = str_ci[name]
        n_partners = 0
        for p in per_bg:
            mask = (p["s"] >= lo_s) & (p["s"] <= hi_s)
            if int(mask.sum()) >= MIN_STRATUM:
                n_partners += int(mask.sum())
        print(f"\n    [{name}: s {lo_s}-{hi_s}] entering backgrounds = "
              f"{arr_f.size}/400 | partner rows = {n_partners:,}")
        print(f"      mean rho_b,stratum = {float(arr_f.mean()):+.9f}  "
              f"SD(ddof=0) = {float(arr_f.std()):.9f}  fraction negative "
              f"= {float(np.mean(arr_f < 0)):.4f}")
        print(f"      CI95 of the mean = [{lo:+.9f}, {hi:+.9f}] "
              f"({nf}/{N_BOOT} finite draws) {prov}".rstrip())
    _dr, lo_p, hi_p, nf_p = ci_paired
    print(f"\n    [paired near - far] backgrounds with BOTH strata = "
          f"{len(paired_ids)}")
    print(f"      mean paired difference = "
          f"{float(paired_diff.mean()):+.9f}  SD(ddof=0) = "
          f"{float(paired_diff.std()):.9f}")
    print(f"      CI95 of the mean = [{lo_p:+.9f}, {hi_p:+.9f}] "
          f"({nf_p}/{N_BOOT} finite draws) {prov}".rstrip())
    w_sep = ci_excludes0(lo_p, hi_p)
    if w_sep:
        sep_msg = (f"CI of the mean paired difference (near - far) "
                   f"[{lo_p:+.9f}, {hi_p:+.9f}] excludes zero")
        print(f"  OUTCOME WORD (frozen section 3): SEPARATION-MATTERS -- "
              f"{sep_msg} {prov}".rstrip())
    else:
        sep_msg = (f"CI of the mean paired difference (near - far) "
                   f"[{lo_p:+.9f}, {hi_p:+.9f}] includes zero")
        print(f"  OUTCOME WORD (frozen section 3): SEPARATION-NOT-"
              f"RESOLVED -- n cannot resolve this ({sep_msg}); never "
              f"reported as 'no relationship' {prov}".rstrip())

    # ======================================================================
    rule("G-3 (SECONDARY, OPTIONAL) -- CALPHA DISTANCE REPEAT (attempted "
         "only after G-1/G-2 are printed)")
    g3_skipped = None
    g3_words = {}
    g3_sep = None
    try:
        RCSB_DIR.mkdir(parents=True, exist_ok=True)
        pdb_path = RCSB_DIR / "1PGA.pdb"
        free = shutil.disk_usage(RCSB_DIR).free
        if free < RCSB_MIN_FREE:
            g3_skipped = (f"free disk {free / 1e9:.1f} GB < 5 GiB -- "
                          "download aborted (planning rule 2)")
        else:
            req = urllib.request.Request(
                PDB_URL, headers={"User-Agent": "phase4-g3-optional/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                body = resp.read()
            pdb_path.write_bytes(body)
            print(f"  download: {PDB_URL}  status={status}  bytes="
                  f"{len(body):,}  sha256="
                  f"{hashlib.sha256(body).hexdigest()}  saved "
                  f"{pdb_path.relative_to(ROOT)}")
            if status != 200 or len(body) < 1000:
                g3_skipped = (f"HTTP {status} or short body "
                              f"({len(body)} bytes) -- not a PDB file")
    except Exception as exc:                              # noqa: BLE001
        g3_skipped = f"fetch failed ({type(exc).__name__}: {exc})"
    if g3_skipped is None:
        ca = []
        for line in pdb_path.read_text().splitlines():
            if line.startswith("ATOM") and line[12:16].strip() == "CA" \
                    and line[21] == "A":
                ca.append((int(line[22:26]), line[17:20].strip(),
                           float(line[30:38]), float(line[38:46]),
                           float(line[46:54])))
        aa3to1 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D",
                  "CYS": "C", "GLN": "Q", "GLU": "E", "GLY": "G",
                  "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
                  "MET": "M", "PHE": "F", "PRO": "P", "SER": "S",
                  "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}
        seq = "".join(aa3to1.get(r[1], "X") for r in ca)
        # G-DEC8: exactly one contiguous, resnum-contiguous match;
        # 56-mer first, then the positions-2..56 55-mer fallback
        matched_form, matches = None, []
        for form, target, i_off in (("56-mer ASSAYED", ASSAYED, 0),
                                    ("ASSAYED[1:] (positions 2..56)",
                                     ASSAYED[1:], 1)):
            found = []
            for i in range(len(seq) - len(target) + 1):
                if seq[i:i + len(target)] == target:
                    span = ca[i:i + len(target)]
                    if all(span[k + 1][0] - span[k][0] == 1
                           for k in range(len(span) - 1)):
                        found.append((i, span[0][0], i_off, form))
            if len(found) == 1:
                matched_form, matches = form, found
                break
        if matched_form is None:
            # Informational only (no gate/threshold change): show exactly where
            # chain A and the assayed 56-mer diverge, so the skip is auditable.
            diffs = [(i + 1, a, b) for i, (a, b) in
                     enumerate(zip(seq, ASSAYED)) if a != b]
            print(f"  numbering diagnostic (informational): chain A CA sequence "
                  f"len {len(seq)} vs ASSAYED len {len(ASSAYED)}; {len(diffs)} "
                  f"differing position(s): "
                  + ", ".join(f"pos {p}: PDB {a} / assayed {b}"
                              for p, a, b in diffs[:5])
                  + (" ..." if len(diffs) > 5 else ""))
            g3_skipped = (f"numbering not verifiable: no unique "
                          f"contiguous 56-mer or 55-mer match of the "
                          f"assayed sequence in chain A (G-DEC8) -- skip")
        else:
            i0, r0, i_off, form = matches[0]
            offset = r0 - (i0 + i_off)
            resnum_of = {pos: pos + offset for pos in
                         range(i_off + 1, len(ASSAYED) + 1)}
            ca_map = {r[0]: aa3to1.get(r[1], "X") for r in ca}
            rt_ok = all(ca_map.get(resnum_of[p]) == ASSAYED[p - 1]
                        for p in range(i_off + 1, len(ASSAYED) + 1))
            print(f"  numbering: {form} matched at chain A residues "
                  f"{r0}-{r0 + len(ASSAYED) - 1 - i_off} (offset "
                  f"{offset:+d}), unique + contiguous, round-trip over "
                  f"{len(ASSAYED) - i_off} positions: {rt_ok}")
            if not rt_ok:
                g3_skipped = "round-trip residue check failed (G-DEC8)"
        if g3_skipped is None:
            xyz = {r[0]: np.array([r[2], r[3], r[4]]) for r in ca}
            dpos = {}
            for pb in range(2, 57):
                for pv in range(2, 57):
                    a_, b_ = resnum_of[pb], resnum_of[pv]
                    if a_ in xyz and b_ in xyz:
                        dpos[(pb, pv)] = float(
                            np.linalg.norm(xyz[a_] - xyz[b_]))
            n_missing = 0
            lm3, ld3, dd3 = [], [], []
            str3 = {name: [] for name in ("near<8A", "mid8-14A",
                                          "far>14A")}
            str3_bg = {name: [] for name in str3}
            for p in per_bg:
                bp = p["b_pos"]
                dv = np.array([dpos.get((bp, int(vp)), np.nan)
                               for vp in p["v_pos"]])
                ok = np.isfinite(dv)
                n_missing += int((~ok).sum())
                if not ok.any():
                    continue
                lm = p3c.spearman(np.abs(p["delta"][ok]), dv[ok])
                ld = p3c.spearman(np.abs(p["eb"][ok]), dv[ok])
                lm3.append(lm)
                ld3.append(ld)
                dd3.append(lm - ld)
                for name, m3 in (("near<8A", ok & (dv < 8.0)),
                                 ("mid8-14A", ok & (dv >= 8.0) &
                                  (dv <= 14.0)),
                                 ("far>14A", ok & (dv > 14.0))):
                    if int(m3.sum()) >= MIN_STRATUM:
                        str3[name].append(p3c.spearman(
                            p["delta"][m3], p["eb"][m3]))
                        str3_bg[name].append(p["background_id"])
            print(f"  rows without a Calpha distance (dropped): "
                  f"{n_missing:,} of {sum(p['n'] for p in per_bg):,}")
            lm3 = np.asarray(lm3, dtype=float)
            ld3 = np.asarray(ld3, dtype=float)
            dd3 = np.asarray(dd3, dtype=float)
            print("\n  [G-3 repeat of G-1, Calpha distance in place of "
                  "s]")
            for label, arr in (("lambda_model", lm3),
                               ("lambda_data", ld3), ("d_b", dd3)):
                fin = arr[np.isfinite(arr)]
                lo, hi, nf = boot_mean_ci(arr)
                g3_ci = (lo, hi, nf)
                print(f"    [{label}] n = {fin.size} | mean = "
                      f"{float(fin.mean()):+.9f} | SD(ddof=0) = "
                      f"{float(fin.std()):.9f} | frac<0 = "
                      f"{float(np.mean(fin < 0)):.4f} | CI95 = "
                      f"[{lo:+.9f}, {hi:+.9f}] ({nf} draws) "
                      f"{prov}".rstrip())
                g3_words[label] = ci_below0(lo, hi) if label != "d_b" \
                    else ci_excludes0(lo, hi)
            m3_model = "FIRES" if g3_words["lambda_model"] else \
                "does not fire"
            m3_data = "FIRES" if g3_words["lambda_data"] else \
                "does not fire"
            m3_diff = "FIRES" if g3_words["d_b"] else "does not fire"
            print(f"  [G-3, secondary] words: MODEL-DECAYS {m3_model}, "
                  f"DATA-DECAYS {m3_data}, LOCALITY-DIFFERS {m3_diff} "
                  f"{prov}".rstrip())
            print("\n  [G-3 repeat of G-2, distance strata: d < 8, "
                  "8-14 inclusive, > 14]")
            str3_ci = {}
            for name in ("near<8A", "mid8-14A", "far>14A"):
                arr = np.asarray(str3[name], dtype=float)
                lo, hi, nf = boot_mean_ci(arr)
                str3_ci[name] = (lo, hi, nf)
                fin = arr[np.isfinite(arr)]
                print(f"    [{name}] entering backgrounds = "
                      f"{fin.size}/400 | mean = "
                      f"{float(fin.mean()):+.9f} | CI95 = "
                      f"[{lo:+.9f}, {hi:+.9f}] ({nf} draws) "
                      f"{prov}".rstrip())
            near3 = dict(zip(str3_bg["near<8A"], str3["near<8A"]))
            far3 = dict(zip(str3_bg["far>14A"], str3["far>14A"]))
            both3 = [b for b in near3 if b in far3]
            if both3:
                pd3 = np.array([near3[b] - far3[b] for b in both3])
                lo, hi, nf = boot_mean_ci(pd3)
                g3_sep = ci_excludes0(lo, hi)
                print(f"    [paired near - far] n = {len(both3)} | mean "
                      f"= {float(pd3.mean()):+.9f} | CI95 = "
                      f"[{lo:+.9f}, {hi:+.9f}] ({nf} draws) "
                      f"{prov}".rstrip())
                if g3_sep:
                    w3s = "SEPARATION-MATTERS"
                else:
                    w3s = ("SEPARATION-NOT-RESOLVED (n cannot resolve "
                           "this)")
                print(f"    [G-3, secondary] word: {w3s} {prov}".rstrip())
            else:
                print("    [paired near - far] no background has both "
                      "distance strata at the >= 50-partner rule")
    if g3_skipped is not None:
        print(f"  G-3 SKIPPED: {g3_skipped}")

    # ======================================================================
    rule("EXTRA CHECK AND FINAL GATE TABLE")
    no_torch = not any(m in sys.modules for m in
                       ("torch", "esm", "thermompnn"))
    gate("[extra] no torch/esm/thermompnn imported", "PASS" if no_torch
         else "FAIL", str(no_torch), "planning rule 1 (Module G)")

    banner("A6 GATE TABLE")
    n_pass = sum(1 for _, v, _ in GATES if v == "PASS")
    n_fail = len(GATES) - n_pass
    for name, verdict, _hard in GATES:
        print(f"  [{verdict}] {name}")
    print(f"\n  {n_pass}/{len(GATES)} checks PASS, {n_fail} FAIL.")
    print("\nOUTCOME WORDS (frozen section 3; these are the result of "
          "this block):")
    mm = "FIRES" if w_model else "does not fire"
    md = "FIRES" if w_data else "does not fire"
    mx = "FIRES" if w_diff else "does not fire"
    print(f"  G-1  MODEL-DECAYS      : {mm}   "
          f"(CI [{ci_m[1]:+.9f}, {ci_m[2]:+.9f}]) {prov}".rstrip())
    print(f"  G-1  DATA-DECAYS       : {md}   "
          f"(CI [{ci_d[1]:+.9f}, {ci_d[2]:+.9f}]) {prov}".rstrip())
    print(f"  G-1  LOCALITY-DIFFERS  : {mx}   "
          f"(CI [{ci_db[1]:+.9f}, {ci_db[2]:+.9f}]) {prov}".rstrip())
    if w_sep:
        sep_line = "SEPARATION-MATTERS"
    else:
        sep_line = "SEPARATION-NOT-RESOLVED (n cannot resolve this)"
    print(f"  G-2  paired near-far   : {sep_line}   (CI [{lo_p:+.9f}, "
          f"{hi_p:+.9f}]) {prov}".rstrip())
    if g3_skipped is None:
        m3_model = "FIRES" if g3_words.get("lambda_model") else \
            "does not fire"
        m3_data = "FIRES" if g3_words.get("lambda_data") else \
            "does not fire"
        m3_diff = "FIRES" if g3_words.get("d_b") else "does not fire"
        if g3_sep is True:
            sep3 = "SEPARATION-MATTERS"
        elif g3_sep is False:
            sep3 = "SEPARATION-NOT-RESOLVED (n cannot resolve this)"
        else:
            sep3 = "paired n/a"
        print(f"  G-3  (secondary, Calpha distance): MODEL-DECAYS "
              f"{m3_model}, DATA-DECAYS {m3_data}, LOCALITY-DIFFERS "
              f"{m3_diff}, paired {sep3} {prov}".rstrip())
    else:
        print(f"  G-3  : SKIPPED -- {g3_skipped}")
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the "
          "docstring):")
    print("    * GB1 only (frozen section 5): no sentence here reads "
          "for or against any MTHFR or RBD\n      result -- systems, "
          "backgrounds and platforms differ.")
    print("    * cached scores; the Phase 3 results for these 400 "
          "backgrounds were already seen\n      (prereg line 3); "
          "reproduction of script 155's rho_b is a unit test, not new "
          "evidence.")
    print("    * background-level bootstrap treats 400 backgrounds as "
          "independent; all deltas\n      share one WT arm (disclosed, "
          "not modelled).")
    print("    * G-1 uses |delta|, |e_b| vs s; G-2 uses SIGNED delta, "
          "e_b within strata (frozen\n      wording) -- not "
          "interchangeable.")
    print("    * G-D2 is a mechanics check (one fixed-seed decay "
          "construction + 100 null draws),\n      not an estimate; G-3 "
          "drops rows without a Calpha atom (count printed).")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    print(f"\nA6 RESULT: {'GATE FAIL' if n_fail else 'GATE PASS'} -- "
          f"exit {3 if n_fail else 0}")
    sys.exit(3 if n_fail else 0)


if __name__ == "__main__":
    main()
