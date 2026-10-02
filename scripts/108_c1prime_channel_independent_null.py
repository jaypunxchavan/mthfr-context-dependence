"""C1' — a CHANNEL-INDEPENDENT version of the shift-side mechanism-only
null (task doc `docs/tasks/c1-prime-independent-channels/
C1_PRIME_INDEPENDENT_CHANNELS.md`, tasks C1'a, C1'b, C1'c).

PRE-REGISTERED (this docstring written before the first run of this
script; AGENTS sec 6). Every design step, calibration method, seed,
gate, tolerance, bootstrap convention, and comparison rule below was
fixed before any number produced here was seen.

WHY (task background, quoted from the task doc):
  C1's original mechanism-only reference (rho = +0.937) "was built by
  constructing both the simulated shift and the simulated e.b-analog as
  two different affine functions of the exact same two random draws
  (f_wt, f_av). That makes it a legitimate upper-bound-style stress
  test, but not a like-for-like companion to Y2, because in reality
  delta_ESM (computed from ESM-2's internal representation) and own_e.b
  (computed from real folinate-assay fitness measurements) are two
  genuinely different physical/computational channels that share only
  the *true* underlying variant severity, not a literal shared random
  number." This script builds the tighter version with independently-
  noised channels calibrated to this project's already-measured
  reliabilities. C1's original result is NOT discarded or re-run: it is
  QUOTED side by side (from data/processed/task106_c1_mechanism_null.csv,
  read as an input, never recomputed) as the upper-bound construction.

C1'a — PRE-REGISTERED DESIGN (the task doc's exact 7 steps):
  Frame: script 106's exact frame — phase5_analysis_table merged with
  own_context_metrics on hgvs_pro, dropna(delta_esm, own_e_b) ->
  10,757 rows / 654 positions (script 33's frame). Real anchor
  re-derived live and gated: |rho - (-0.08811806424891734)| < 1e-9.
  Pool: script 106's exact pool — task32_analysis_table.csv f_bar
  dropna, non-negative check (ratio-scale presumption, script 101's
  check).
  1. SHARED TRUE SEVERITY: one s_v per row, rng.choice(f_bar) with
     SEED_S = 0 (script 106's exact pool and seed discipline). This is
     the one thing the two channels share: real biology both
     measurement processes are trying to capture.
  2. ESM CHANNEL (feeds the simulated shift): f_wt_ESM = s_v +
     noise_ESM_wt, f_av_ESM = s_v + noise_ESM_av, the two noises
     sequential iid draws from rng seed SEED_ESM = 1, scaled to the
     calibrated sigma_ESM (below).
  3. ASSAY CHANNEL (feeds the simulated e.b-analog): f_wt_assay =
     s_v + noise_assay_wt, f_av_assay = s_v + noise_assay_av,
     iid draws from rng seed SEED_ASSAY = 2, calibrated separately to
     sigma_assay.
     Noise shape: additive zero-mean GAUSSIAN for both channels —
     DISCLOSED pre-run: the SHAPE is an assumption (the standard
     measurement-error model); only the MAGNITUDE is calibrated to
     measured reliabilities, as the task doc requires.
  4. SEPARATE RANDOM STREAMS: severity seed 0, ESM seed 1, assay
     seed 2, calibration seeds 3 (ESM) and 4 (assay) — five distinct
     np.random.default_rng instances; no single random draw feeds both
     channels. Independence is MEASURED (gate V1a below), not asserted.
  5. shift_sim = f_av_ESM - f_wt_ESM (mirrors delta_esm).
  6. eb_analog_sim from f_wt_assay, f_av_assay through the exact real
     own_context WLS machinery script 106 used and verified — the SAME
     code path via import (own_context.fit_interaction with m_score =
     f_av_assay replicated across CONCS, m_se = REAL per-point SEs,
     w_fitness = f_wt_assay, w_post = 1, w_mean_score = f_wt_assay,
     a222v_fitness = REAL b_A, a222v_remediation = REAL r_A,
     correction = REAL (cb, cr) from rebuild_interaction_fit). Nothing
     is reimplemented.
  7. STATISTIC: Spearman(shift_sim, eb_analog) via the project's
     standard position_cluster_bootstrap (clusters = the 654 real
     positions, re-ranked per draw, N_BOOT from env default 10000,
     seed 0, two-sided sign-crossing p_boot; p == 0 reported as
     p < 1/N_BOOT). p_boot is the PRIMARY claim (AGENTS sec 3; no
     z-score is computed). Identity check I1 inside the null's own
     output: bootstrap observed_rho == direct _spearman < 1e-12.

C1'a — CALIBRATION METHOD (pre-registered before running):
  The noise magnitude per channel is chosen so the channel's own
  CROSS-DRAW RELIABILITY matches this project's own measured value:
    ESM channel target  = 0.8826369680851056
        (D1's r_xx_median — full-precision value read from
         data/processed/task105_difference_score_reliability.csv,
         the G2-gated 0.88 on record; on record as ~0.88)
    Assay channel target = 0.6363275925044801
        (C3a's rel_own — full-precision value read from
         data/processed/task47_c3a_disattenuation.csv, the
         synonymous-variant reliability 1 - var(syn 0.02111, n=570) /
         var(analysis 0.05804); on record as 0.6363)
  Measured the same way the project measured ESM-1v's real
  cross-checkpoint reliability (D1's convention): build N_REPS = 5
  replicate measurements of the SAME s_v vector — replicate_i = s_v +
  sigma * z_i, z_i iid standard normal from that channel's dedicated
  calibration stream (SEED_CAL_ESM = 3 / SEED_CAL_ASSAY = 4, streams
  that NEVER enter the statistic) — compute all 10 pairwise Spearmans,
  and take the MEDIAN over pairs (D1 reports the median over checkpoint
  pairs). The calibration search is a deterministic bisection on sigma:
  bracket [0, expand-by-doubling until achieved(sigma_hi) < target],
  100 bisection steps, inner search tolerance 0.002, evaluated on a
  FIXED achieved(sigma) function (deterministic given the seeds).
  A closed-form Pearson/classical-test-theory reference
  sigma_cf = sqrt(Var(s_v, ddof=1) * (1 - target) / target) is printed
  for context; the bisection result governs.
  Calibration replicates are built on the SAME s_v vector used
  downstream (so Var(s) matches the analysis), disclosed.

C1'b — VERIFICATION GATES (run BEFORE any correlation is trusted;
  failure => print, sys.exit(1); no N-raise, no threshold change):
  G0 inputs exist (exact path printed if missing), including C1's
     output table task106_c1_mechanism_null.csv (quoted side by side).
  G1 frame == 10,757/654 and every hgvs_pro maps to a raw row.
  G2 real anchor reproduction to 1e-9.
  G3 f_bar pool non-negative.
  C2a CALIBRATION GATE, ESM: |achieved_primary - 0.8826369680851056|
     <= CAL_TOL = 0.02 (tolerance fixed here, pre-run, per task doc).
  C2b CALIBRATION GATE, assay:
     |achieved_primary - 0.6363275925044801| <= 0.02.
  C3a/C3b SECONDARY achieved gates: the same cross-draw reliability
     measured on the ANALYSIS arm pair actually used downstream —
     |Spearman(f_wt_ch, f_av_ch) - target| <= 0.02 per channel (the
     two arms both measure s_v, so they are parallel measures; this is
     the realized, single-pair version of the primary measurement).
     A miss is a FAIL, reported with exact numbers — never a silent
     pass, never a re-seeded retry.
  V1a CROSS-CHANNEL NOISE INDEPENDENCE (the point of this
     construction): all four pairwise Spearmans between the ESM noise
     draws {wt, av} and the assay noise draws {wt, av} satisfy
     |rho| <= V1_TOL = 0.05 (same threshold as C1's V1: under true
     independence n = 10,757 gives sd(Spearman) ~ 1/sqrt(n-1) = 0.0096,
     so 0.05 is ~5.2 sd). All four values printed.
  V1b WITHIN-CHANNEL ARM-NOISE INDEPENDENCE (C1's V1 adapted):
     |Spearman(noise_wt, noise_av)| <= 0.05 within each channel.
  V1c STRUCTURAL, no shared random term except s_v: max|shift_sim -
     (noise_ESM_av - noise_ESM_wt)| < 1e-12 — the severity cancels
     identically in the difference, so shift_sim contains NO s_v term
     and NO assay-channel term at all (arithmetic of the task doc's
     step 5, verified numerically here).
  V1d STRUCTURAL, e.b-analog is assay-only: the script 106 V3
     identity re-applied to the assay inputs —
     max|eb_analog - (f_av_assay - b_A * f_wt_assay - cb(f_wt_assay))|
     < 1e-9 — eb_analog is a function of assay-channel quantities and
     the REAL pipeline's fixed constants only; no ESM-channel quantity
     appears anywhere in its construction (code path is shared with
     script 106 by import, not rewritten).
  V4 accounting: eb_analog finite on all 10,757 rows (expected 0 NaN;
     same argument as script 106 V4 — validity depends on the real
     Mse mask, not on simulated values).
  I1/I1b bootstrap identity checks (<1e-12) for sim and real.
  STRUCTURAL DISCLOSURE (pre-run, arithmetic of the mandated design,
  stated here before any output exists): because both ESM arms equal
  s_v + noise, their DIFFERENCE cancels s_v identically (V1c), and the
  channels' noise streams are independent (V1a) — so the two simulated
  statistics share NO random term, and this null is EXPECTED to center
  near zero, in stark contrast to C1's +0.937 (which came from both
  statistics reading the SAME two draws). Disclosed now, pre-run, so
  a near-zero outcome cannot be dressed up post-hoc as a surprise or
  rationalized after the fact; whatever value appears is reported as
  is. The shared-severity term s_v exists in all four arm values (the
  construction the task doc mandates) and lives on in eb_analog; it
  simply does not survive differencing into shift_sim.

C1'c — COMPARISON AND VERDICT (pre-registered decision rule):
  C1's original result is QUOTED from task106_c1_mechanism_null.csv
  (rho +0.9366244249321943, CI [+0.933389201160778,
  +0.9396189771832062]) and NEVER recomputed; this script's
  channel-independent result is computed fresh. Both are printed in
  one side-by-side table with the real anchor, each labeled with what
  it actually tests.
  The verdict maps EXACTLY as C1's C1d rule did, applied fresh to THIS
  construction's own CI (the rule does not carry over — the CI does):
      |rho_real| below  the |rho_sim| CI  -> "-0.088 is SMALL relative
                                              to the channel-independent
                                              reference (BELOW the CI)"
      |rho_real| inside the |rho_sim| CI  -> "... COMPARABLE (INSIDE)"
      |rho_real| above  the |rho_sim| CI  -> "... LARGE relative to the
                                              channel-independent
                                              reference (ABOVE the CI)"
  where |rho_sim| CI = [min |ci_lo|, max |ci_hi|] of THIS construction.
  All raw numbers (both points, both CIs, both p's, the SIGN of each,
  both calibrations, all independence measurements) print regardless of
  which branch fires. SIGN is reported as its own observation (C1's
  mechanical artifact was positive; the real anchor is negative; this
  null's sign is whatever it is), not folded into the magnitude
  verdict.
  DESCRIPTIVE SENSITIVITY (no decision attached): the same statistic
  with correction=None as a point estimate, for parity with C1.
  A plain-language comparison statement prints: whether the
  channel-independent |rho| is meaningfully smaller than C1's 0.937,
  with the explanation that decoupling the channels removes the
  artificial shared-draw inflation — per the task doc, if so, the
  channel-independent version is the stricter test and the manuscript
  should cite it as primary with C1 kept as the disclosed upper-bound
  sensitivity check. That recommendation is NARRATIVE for the log, not
  a gate; the only decision rule is the 3-way magnitude mapping above.

LIMITATIONS (printed with results, AGENTS sec 6):
  1. Near-zero expected outcome (disclosed pre-run above): with
     independent streams and a differencing shift, the null's content
     is largely an ARCHITECTURE CHECK — it demonstrates where C1's
     +0.937 came from (shared draws), and it bounds what mechanism-
     only structure can inject across INDEPENDENT channels. It cannot
     by itself rule out mechanisms that operate through quantities the
     difference cancels or through channel-specific biases that are
     part of the signal rather than the null.
  2. Calibrated MAGNITUDE, assumed SHAPE: noise is additive Gaussian;
     only the second-moment scale is pinned to measured reliabilities
     (0.8826369680851056 ESM / 0.6363275925044801 assay). Different
     noise shapes at the same reliability would be a different sim —
     not tested here.
  3. The two targets come from DIFFERENT measurement designs (D1:
     cross-checkpoint agreement on raw scores; C3a: synonymous-variant
     variance ratio on e.b) — reusing each exactly as recorded, per the
     task doc's "reuse it explicitly" mandate; their methodological
     non-equivalence is disclosed, not resolved.
  4. Zero planted channel coupling is guaranteed by construction and
     gated (V1a-V1d); it says nothing about whether the REAL -0.088 is
     free of interaction — the sim says what mechanism ALONE can
     produce across independent channels, nothing more.
  5. Inherited from C1/scale note: f_bar draws are placed in the arm
     slots where the real pipeline holds fitted wt/m scores from the
     same atlas assay (same functionality-scale identification Y2 and
     C1 make), disclosed, not verified here; the real A222V line
     enters only through expected() as one global constant.
  6. Y2/C1's noise structure has no per-concentration term, so the WLS
     intercept reduces to its analytic form (V1d's identity) — the real
     machinery runs, but the concentration dimension carries the
     background line's slope and the correction, not noise.
  7. Cluster bootstrap over iid simulated rows (the draws have no
     position structure; the 654-position convention is run because
     C1c mandates comparability with the anchor's convention),
     disclosed as in C1 limitation 5.
  8. p_boot of the SIM only tests exclusion of zero; the meaningful
     comparison is magnitude-vs-magnitude (C1'c rule). No z-score is
     computed anywhere (AGENTS sec 3).
  9. n = 10,757 / 654; N_BOOT env default 10000 (smoke 300), seed 0.

GATES SUMMARY (failure => print, sys.exit(1); no retry, no rule
  change): G0-G3 as script 106 (plus task106 table present); C2a/C2b
  primary calibration (tol 0.02); C3a/C3b secondary calibration
  (tol 0.02); V1a cross-channel noise independence (|rho| <= 0.05,
  all four pairs); V1b within-channel arm independence; V1c severity-
  cancellation identity (1e-12); V1d e.b-analog analytic identity
  (1e-9); V4 NaN count == 0; I1/I1b bootstrap identities (1e-12).

SMOKE: N_BOOT=300 first (all gates + point values), then full 10000.
OUTPUT: data/processed/task108_c1prime_channel_null.csv (tidy long).
Existing scripts/CSVs untouched (script 106 and its CSV are read-only
inputs here); next free script number after this: 109.
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Cosmetic (disclosed, inherited from script 106): rebuild_interaction_fit's
# np.nanmean on all-NaN WT rows emits "Mean of empty slice" — pre-existing
# behavior of the shared code path (scripts 101/33/106), unrelated to this
# simulation. Suppressed so gate output stays readable; nothing is hidden
# from any gate (all counts printed explicitly).
warnings.filterwarnings("ignore", message="Mean of empty slice")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.own_context import CONCS, fit_interaction  # noqa: E402
from scripts.lib.stats import _spearman, position_cluster_bootstrap  # noqa: E402
from scripts.lib.stats_ext import rebuild_interaction_fit  # noqa: E402

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0            # bootstrap seed — project convention, same as script 106
SEED_S = 0          # shared severity pool draws (script 106's discipline)
SEED_ESM = 1        # ESM-channel analysis noises
SEED_ASSAY = 2      # assay-channel analysis noises
SEED_CAL_ESM = 3    # ESM-channel calibration replicate noises
SEED_CAL_ASSAY = 4  # assay-channel calibration replicate noises
SMOKE = N_BOOT <= 500

G_ANCHOR = -0.08811806424891734     # canonical rho(delta_esm, own_e_b)
T_ESM = 0.8826369680851056          # D1 r_xx_median (task105 CSV)
T_ASSAY = 0.6363275925044801        # C3a rel_own (task47 CSV; record: 0.6363)
CAL_TOL = 0.02                      # pre-registered calibration gate tolerance
SEARCH_TOL = 0.002                  # bisection inner tolerance
N_REPS = 5                          # calibration replicates per channel
V1_TOL = 0.05                       # pre-registered independence gate
V1C_TOL = 1e-12                     # severity-cancellation identity
V3_TOL = 1e-9                       # e.b-analog analytic identity
V4_EXPECT_NAN = 0


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def calibrate(s_v, z_reps, target, tag):
    """Deterministic bisection on sigma so the channel's median pairwise
    cross-draw reliability (N_REPS replicates, C(N_REPS,2) pairs) hits
    `target` on the shared severity vector s_v."""
    var_s = float(np.var(s_v, ddof=1))
    sigma_cf = float(np.sqrt(var_s * (1.0 - target) / target)) if var_s > 0 else 1.0

    def achieved(sig):
        reps = s_v[None, :] + sig * z_reps
        vals = [_spearman(reps[i], reps[j])
                for i in range(N_REPS) for j in range(i + 1, N_REPS)]
        return float(np.median(vals))

    lo = 0.0                                   # achieved(0) = 1 > target
    hi = sigma_cf if sigma_cf > 0 else 1.0     # expand until below target
    for _ in range(200):
        if achieved(hi) < target:
            break
        hi *= 2.0
    else:
        gfail(f"C2 FAIL ({tag}): could not bracket sigma so that "
              f"achieved < target {target!r} — search did not converge — stop.")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if achieved(mid) > target:
            lo = mid
        else:
            hi = mid
    sigma = 0.5 * (lo + hi)
    ach = achieved(sigma)
    print(f"  [{tag}] closed-form sigma (Pearson ref) = {sigma_cf!r}")
    print(f"  [{tag}] bisected sigma = {sigma!r}")
    print(f"  [{tag}] achieved primary reliability (median of "
          f"{N_REPS} choose 2 pairwise Spearmans on s_v) = {ach!r}  "
          f"vs target {target!r}  (diff {ach - target:+.6f})")
    if abs(ach - target) > SEARCH_TOL:
        print(f"  [{tag}] NOTE: bisection did not reach the inner search "
              f"tolerance {SEARCH_TOL} — achieved diff is "
              f"{ach - target:+.6f}; reported as achieved (the gate is "
              f"+/-{CAL_TOL}), NOT re-searched.")
    return sigma, ach


def main():
    t0 = time.time()
    banner(f"C1' — channel-independent mechanism null (scripts/108)  "
           f"N_BOOT={N_BOOT} seed={SEED}" + ("  [SMOKE]" if SMOKE else ""))

    # ---- G0: inputs -------------------------------------------------
    paths = {
        "raw fit": RAW / "results" / "folate_response_model5.csv",
        "phase5": PROC / "phase5_analysis_table.csv",
        "own metrics": PROC / "own_context_metrics.csv",
        "f_bar pool": PROC / "task32_analysis_table.csv",
        "C1 reference table (quoted, never recomputed)":
            PROC / "task106_c1_mechanism_null.csv",
        "D1 r_xx (ESM calibration target)":
            PROC / "task105_difference_score_reliability.csv",
        "C3a rel_own (assay calibration target)":
            PROC / "task47_c3a_disattenuation.csv",
    }
    for label, p in paths.items():
        if not p.exists():
            gfail(f"G0 FAIL: {label} input missing: {p} — stop.")
    print("  G0 PASS: all 7 inputs present")

    # ---- calibration targets re-read from their own CSVs (no
    #      hardcoding-only targets: the recorded values are re-derived
    #      from the tables that carry them and gated against the
    #      pre-registered constants) -------------------------------
    d1 = pd.read_csv(paths["D1 r_xx (ESM calibration target)"])
    t_esm_disk = float(d1.loc[d1["key"] == "r_xx_median", "value"].iloc[0])
    if abs(t_esm_disk - T_ESM) > 1e-12:
        gfail(f"G0 FAIL: D1 r_xx_median on disk {t_esm_disk!r} != "
              f"pre-registered target {T_ESM!r} — sources disagree, stop.")
    c3a = pd.read_csv(paths["C3a rel_own (assay calibration target)"])
    t_assay_disk = float(c3a.iloc[0]["rel_own"])
    if abs(t_assay_disk - T_ASSAY) > 1e-12:
        gfail(f"G0 FAIL: C3a rel_own on disk {t_assay_disk!r} != "
              f"pre-registered target {T_ASSAY!r} — sources disagree, stop.")
    print(f"  G0 targets PASS: ESM {t_esm_disk!r} (task105 r_xx_median) | "
          f"assay {t_assay_disk!r} (task47 rel_own)")

    # ---- G1: frame (script 106's exact construction) ---------------
    raw = pd.read_csv(paths["raw fit"])
    fit = rebuild_interaction_fit(raw)
    df = pd.read_csv(paths["phase5"])
    own = pd.read_csv(paths["own metrics"])[["hgvs_pro", "own_e_b"]]
    df = (df.merge(own, on="hgvs_pro", how="left")
            .dropna(subset=["delta_esm", "own_e_b"])
            .reset_index(drop=True))
    n_rows = len(df)
    n_pos = df["position"].nunique()
    if (n_rows, n_pos) != (10757, 654):
        gfail(f"G1 FAIL: frame {n_rows}/{n_pos} != 10757/654 — stop.")
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    missing = [h for h in df["hgvs_pro"] if h not in row_of]
    if missing:
        gfail(f"G1 FAIL: {len(missing)} hgvs_pro absent from raw fit "
              f"(e.g. {missing[0]}) — stop.")
    src = np.array([row_of[h] for h in df["hgvs_pro"]])
    print(f"  G1 PASS: frame = {n_rows} rows / {n_pos} positions; all "
          f"hgvs_pro map to raw fit rows")

    # ---- G2: real anchor reproduced live ---------------------------
    delta = df["delta_esm"].to_numpy(float)
    own_eb = df["own_e_b"].to_numpy(float)
    r_real = _spearman(delta, own_eb)
    if abs(r_real - G_ANCHOR) > 1e-9:
        gfail(f"G2 FAIL: rho(delta_esm, own_e_b) = {r_real!r} vs canonical "
              f"{G_ANCHOR!r} (tol 1e-9) — stop.")
    print(f"  G2 PASS: real anchor reproduced live: rho = {r_real!r} "
          f"(tol 1e-9)")

    # ---- G3: f_bar pool --------------------------------------------
    t32 = pd.read_csv(paths["f_bar pool"], usecols=["f_bar"])
    f = t32["f_bar"].dropna().to_numpy(float)
    if (f < 0).any():
        gfail("G3 FAIL: negative f_bar values — ratio-scale presumption "
              "(script 101's check) — stop.")
    print(f"  G3 PASS: f_bar pool n={len(f)} "
          f"range=[{f.min():.4f}, {f.max():.4f}] non-negative")

    # ---- real pipeline fixed parts (V2-equivalent, printed) --------
    w = fit["w"]
    i222 = fit["i222"]
    b_A = float(w["fitness"][i222])
    r_A = float(w["remediation"][i222])
    cb, cr = fit["correction"]
    Mse = fit["M_se"][src]
    print(f"  pipeline constants (real, reused): b_A={b_A!r} "
          f"r_A={r_A!r} (p.Ala222Val row {i222})")

    # ---- C1'a: shared true severity --------------------------------
    banner("C1'a — SHARED SEVERITY + CALIBRATED CHANNELS (gates BEFORE "
           "any correlation)", "-")
    rng_s = np.random.default_rng(SEED_S)
    s_v = rng_s.choice(f, size=n_rows, replace=True)
    print(f"  s_v: rng.choice(f_bar) seed {SEED_S}, n={n_rows}, "
          f"mean {s_v.mean():.6f} median {np.median(s_v):.6f} "
          f"var(ddof=1) {np.var(s_v, ddof=1):.6f} — the ONE shared term")

    # calibration replicate noises (dedicated streams, never in stat)
    z_esm = np.random.default_rng(SEED_CAL_ESM).standard_normal(
        (N_REPS, n_rows))
    z_assay = np.random.default_rng(SEED_CAL_ASSAY).standard_normal(
        (N_REPS, n_rows))
    sigma_esm, ach_esm = calibrate(s_v, z_esm, T_ESM, "ESM channel")
    sigma_assay, ach_assay = calibrate(s_v, z_assay, T_ASSAY,
                                       "assay channel")

    # ---- C1'b: calibration gates -----------------------------------
    banner("C1'b — VERIFICATION GATES (calibration + independence, run "
           "BEFORE the statistic)", "-")
    d_esm = ach_esm - T_ESM
    print(f"  C2a ESM primary achieved {ach_esm!r} vs target {T_ESM!r} "
          f"diff {d_esm:+.6f} (gate |diff| <= {CAL_TOL})")
    if abs(d_esm) > CAL_TOL:
        gfail(f"C2a FAIL: ESM calibration misses target by {d_esm:+.6f} "
              f"(> {CAL_TOL}) — achieved reported, task stops as FAIL — "
              f"no forced pass, no re-seeded retry.")
    print(f"  C2a PASS: ESM-channel reliability achieved within "
          f"+/-{CAL_TOL}")
    d_ass = ach_assay - T_ASSAY
    print(f"  C2b assay primary achieved {ach_assay!r} vs target "
          f"{T_ASSAY!r} diff {d_ass:+.6f} (gate |diff| <= {CAL_TOL})")
    if abs(d_ass) > CAL_TOL:
        gfail(f"C2b FAIL: assay calibration misses target by "
              f"{d_ass:+.6f} (> {CAL_TOL}) — stop.")
    print(f"  C2b PASS: assay-channel reliability achieved within "
          f"+/-{CAL_TOL}")

    # ---- analysis draws (separate streams) -------------------------
    rng_esm = np.random.default_rng(SEED_ESM)
    e_wt = sigma_esm * rng_esm.standard_normal(n_rows)
    e_av = sigma_esm * rng_esm.standard_normal(n_rows)
    rng_as = np.random.default_rng(SEED_ASSAY)
    a_wt = sigma_assay * rng_as.standard_normal(n_rows)
    a_av = sigma_assay * rng_as.standard_normal(n_rows)

    f_wt_esm = s_v + e_wt
    f_av_esm = s_v + e_av
    f_wt_assay = s_v + a_wt
    f_av_assay = s_v + a_av
    shift = f_av_esm - f_wt_esm                 # mirrors delta_esm (step 5)

    # secondary achieved gates: analysis arm pair (parallel measures of s_v)
    sec_esm = _spearman(f_wt_esm, f_av_esm)
    sec_assay = _spearman(f_wt_assay, f_av_assay)
    print(f"  C3a ESM secondary achieved (analysis arm pair "
          f"Spearman) {sec_esm!r} vs target {T_ESM!r} "
          f"diff {sec_esm - T_ESM:+.6f} (gate |diff| <= {CAL_TOL})")
    if abs(sec_esm - T_ESM) > CAL_TOL:
        gfail(f"C3a FAIL: ESM analysis-arm reliability misses target by "
              f"{sec_esm - T_ESM:+.6f} — stop (reported, not re-seeded).")
    print(f"  C3a PASS")
    print(f"  C3b assay secondary achieved (analysis arm pair "
          f"Spearman) {sec_assay!r} vs target {T_ASSAY!r} "
          f"diff {sec_assay - T_ASSAY:+.6f} (gate |diff| <= {CAL_TOL})")
    if abs(sec_assay - T_ASSAY) > CAL_TOL:
        gfail(f"C3b FAIL: assay analysis-arm reliability misses target by "
              f"{sec_assay - T_ASSAY:+.6f} — stop.")
    print(f"  C3b PASS")

    # ---- V1a: cross-channel noise independence (measured) ----------
    pairs = [("noise_ESM_wt", e_wt, "noise_assay_wt", a_wt),
             ("noise_ESM_wt", e_wt, "noise_assay_av", a_av),
             ("noise_ESM_av", e_av, "noise_assay_wt", a_wt),
             ("noise_ESM_av", e_av, "noise_assay_av", a_av)]
    worst = 0.0
    for n1, v1, n2, v2 in pairs:
        rho = _spearman(v1, v2)
        worst = max(worst, abs(rho))
        print(f"  V1a Spearman({n1}, {n2}) = {rho!r}  (gate |rho| <= "
              f"{V1_TOL})")
    if worst >= V1_TOL:
        gfail(f"V1a FAIL: cross-channel noise correlation |rho| = "
              f"{worst:.6f} >= {V1_TOL} — streams are NOT independent — "
              f"stop.")
    print(f"  V1a PASS: all four cross-channel noise pairs independent "
          f"(worst |rho| = {worst:.6f}) — measured, not asserted")

    # ---- V1b: within-channel arm-noise independence (C1's V1) ------
    v1b_e = _spearman(e_wt, e_av)
    v1b_a = _spearman(a_wt, a_av)
    print(f"  V1b within-channel: Spearman(ESM_wt, ESM_av) = {v1b_e!r} | "
          f"Spearman(assay_wt, assay_av) = {v1b_a!r}  (gate |rho| <= "
          f"{V1_TOL})")
    if max(abs(v1b_e), abs(v1b_a)) >= V1_TOL:
        gfail(f"V1b FAIL: within-channel arm noises not independent "
              f"({v1b_e!r}, {v1b_a!r}) — stop.")
    print(f"  V1b PASS: arm noises independent within both channels")

    # ---- V1c: severity cancels identically in the shift ------------
    v1c = float(np.max(np.abs(shift - (e_av - e_wt))))
    print(f"  V1c structural: max|shift_sim - (noise_ESM_av - "
          f"noise_ESM_wt)| = {v1c:.3e}  (gate < {V1C_TOL:.0e}) — shift "
          f"carries NO s_v term and NO assay term by arithmetic")
    if v1c >= V1C_TOL:
        gfail(f"V1c FAIL: shift_sim is not exactly the ESM noise "
              f"difference ({v1c:.3e}) — stop.")
    print(f"  V1c PASS: shared severity cancels identically in the "
          f"difference; shift_sim = pure ESM-channel noise difference")

    # ---- e.b-analog through the REAL own_context path --------------
    m_sim = np.repeat(f_av_assay[:, None], len(CONCS), axis=1)
    sim_e2 = fit_interaction(m_sim, Mse, f_wt_assay, np.zeros(n_rows),
                             np.ones(n_rows), f_wt_assay, b_A, r_A,
                             correction=(cb, cr))
    eb = sim_e2["e_b"]
    n_nan = int(np.isnan(eb).sum())
    print(f"  V4 accounting: eb_analog finite = {n_rows - n_nan}/{n_rows}")
    if n_nan != V4_EXPECT_NAN:
        gfail(f"V4 FAIL: {n_nan} NaN in eb_analog "
              f"(expected {V4_EXPECT_NAN}) — stop.")
    print(f"  V4 PASS")
    analytic = f_av_assay - b_A * f_wt_assay - cb(f_wt_assay)
    v1d = float(np.nanmax(np.abs(eb - analytic)))
    print(f"  V1d identity: max|eb_analog - (f_av_assay - b_A*f_wt_assay - "
          f"cb(f_wt_assay))| = {v1d:.3e}  (gate < {V3_TOL:.0e})")
    if v1d >= V3_TOL:
        gfail(f"V1d FAIL: e.b-analog does not equal its analytic "
              f"assay-only form ({v1d:.3e}) — stop.")
    print(f"  V1d PASS: eb_analog is a function of ASSAY-channel "
          f"quantities + real pipeline constants only — no ESM quantity "
          f"enters its construction")
    print(f"  channel-separation statement (verified by V1a/V1c/V1d): the "
          f"ONLY term shared across channels is s_v itself, present in "
          f"all four arm values by design (task doc step 1); it cancels "
          f"identically from shift_sim (V1c) and persists only into "
          f"eb_analog (assay side). No other term references both "
          f"channels.")
    for i in range(5):
        print(f"    row {i}: s_v={s_v[i]:.4f} e_wt={e_wt[i]:+.4f} "
              f"e_av={e_av[i]:+.4f} a_wt={a_wt[i]:+.4f} "
              f"a_av={a_av[i]:+.4f} shift={shift[i]:+.4f} "
              f"eb_analog={eb[i]:+.4f}")

    # ---- statistic + real anchor (position-cluster bootstrap) ------
    banner(f"CHANNEL-INDEPENDENT STATISTIC + REAL ANCHOR (both "
           f"position-cluster bootstrap, N_BOOT={N_BOOT}, seed {SEED})",
           "-")
    sim_df = pd.DataFrame({"position": df["position"],
                           "shift_sim": shift, "eb_sim": eb})
    sim_bs = position_cluster_bootstrap(sim_df, "position", "shift_sim",
                                        "eb_sim", n_boot=N_BOOT,
                                        seed=SEED)
    r_sim = _spearman(shift, eb)
    if abs(sim_bs["observed_rho"] - r_sim) >= 1e-12:
        gfail(f"I1 FAIL: bootstrap observed_rho "
              f"{sim_bs['observed_rho']!r} != direct _spearman "
              f"{r_sim!r} — stop.")
    print(f"  I1 PASS: bootstrap observed == direct Spearman ({r_sim!r})")
    real_bs = position_cluster_bootstrap(df, "position", "delta_esm",
                                         "own_e_b", n_boot=N_BOOT,
                                         seed=SEED)
    if abs(real_bs["observed_rho"] - r_real) >= 1e-12:
        gfail("I1b FAIL: real bootstrap observed != direct Spearman — "
              "stop.")
    print(f"  I1b PASS")

    def pp(tag, bs, r):
        p = bs["p_boot"]
        pstr = f"<{1.0 / N_BOOT:.1e}" if p == 0 else f"{p:.4f}"
        print(f"  [{tag}] rho={float(r)!r}  "
              f"CI [{float(bs['ci_lo'])!r}, {float(bs['ci_hi'])!r}]  "
              f"p_boot={pstr}  (n={bs['n_rows']}, "
              f"{bs['n_clusters']} positions)")

    pp("CHANNEL-INDEPENDENT null (sim shift vs sim e.b)", sim_bs, r_sim)
    pp("REAL anchor (delta_esm vs own_e_b)", real_bs,
       real_bs["observed_rho"])

    sim_nc = fit_interaction(m_sim, Mse, f_wt_assay, np.zeros(n_rows),
                             np.ones(n_rows), f_wt_assay, b_A, r_A,
                             correction=None)
    r_nc = _spearman(shift, sim_nc["e_b"])
    print(f"  descriptive sensitivity (correction=None, point estimate "
          f"only, no decision): rho={r_nc!r}")

    # ---- C1'c: side-by-side + pre-registered verdict ---------------
    banner("C1'c — BOTH CONSTRUCTIONS SIDE BY SIDE (C1 quoted from its "
           "own CSV; never recomputed)", "-")
    c1_rows = pd.read_csv(paths["C1 reference table (quoted, never "
                                "recomputed)"])
    c1_sim = c1_rows[c1_rows["section"] == "sim"].set_index("key")
    c1_rho = float(c1_sim.loc["rho_shift_vs_eb_analog", "value"])
    c1_lo = float(c1_sim.loc["ci_lo", "value"])
    c1_hi = float(c1_sim.loc["ci_hi", "value"])
    print(f"  {'construction':<34} {'rho':>12}  "
          f"{'95% CI':<44} {'p_boot':>8}   what it tests")
    print(f"  {'C1 upper-bound (shared-draw)':<34} {c1_rho:>+12.6f}  "
          f"[{c1_lo:+.6f}, {c1_hi:+.6f}]{'':<20} {'<1e-04':>8}   both "
          f"stats = affine fns of the SAME two draws")
    p_sim = sim_bs["p_boot"]
    pstr = f"<{1.0 / N_BOOT:.1e}" if p_sim == 0 else f"{p_sim:.4f}"
    lab_ci = "C1' channel-independent"
    print(f"  {lab_ci:<34} "
          f"{float(sim_bs['observed_rho']):>+12.6f}  "
          f"[{float(sim_bs['ci_lo']):+.6f}, "
          f"{float(sim_bs['ci_hi']):+.6f}]{'':<20} {pstr:>8}   "
          f"independent channels calibrated to 0.88/0.6363, share only s_v")
    p_real = real_bs["p_boot"]
    pstr_r = f"<{1.0 / N_BOOT:.1e}" if p_real == 0 else f"{p_real:.4f}"
    print(f"  {'REAL anchor':<34} "
          f"{float(real_bs['observed_rho']):>+12.6f}  "
          f"[{float(real_bs['ci_lo']):+.6f}, "
          f"{float(real_bs['ci_hi']):+.6f}]{'':<20} {pstr_r:>8}   "
          f"actual delta_esm vs own_e_b")

    obs = abs(real_bs["observed_rho"])
    mech = abs(sim_bs["observed_rho"])
    lo = float(min(abs(sim_bs["ci_lo"]), abs(sim_bs["ci_hi"])))
    hi = float(max(abs(sim_bs["ci_lo"]), abs(sim_bs["ci_hi"])))
    print(f"  channel-independent |rho| = {mech!r}, 95% CI on |rho| "
          f"[{lo!r}, {hi!r}]")
    print(f"  real observed |rho| = {obs!r} (canonical "
          f"{G_ANCHOR!r})")
    if obs < lo:
        verdict = ("SMALL relative to the channel-independent reference "
                   "point — the observed |−0.088| sits BELOW the "
                   "channel-independent CI")
    elif obs > hi:
        verdict = ("LARGE relative to the channel-independent reference "
                   "point — the observed |−0.088| sits ABOVE the "
                   "channel-independent CI")
    else:
        verdict = ("COMPARABLE to the channel-independent reference "
                   "point — the observed |−0.088| sits INSIDE the "
                   "channel-independent CI")
    print(f"  SIGN observation: channel-independent rho = "
          f"{float(sim_bs['observed_rho']):+.6f} "
          f"({'+pos' if sim_bs['observed_rho'] > 0 else '-neg'}), C1 "
          f"upper-bound rho = {c1_rho:+.6f} (+pos), real rho = "
          f"{float(real_bs['observed_rho']):+.6f} "
          f"({'-neg' if real_bs['observed_rho'] < 0 else '+pos'}) — sign "
          f"reported as its own result, not folded into the verdict")
    print(f"  VERDICT: −0.088 is {verdict}")
    delta_mag = c1_hi - mech
    if mech < c1_lo:
        print(f"  COMPARISON: the channel-independent |rho| ({mech!r}) is "
              f"meaningfully SMALLER than C1's upper-bound |rho| "
              f"({c1_rho!r}) — smaller by {delta_mag:.6f} at minimum — "
              f"because decoupling the channels removes the artificial "
              f"shared-draw inflation: both statistics no longer read the "
              f"same random numbers. Per the task doc this makes the "
              f"channel-independent version the stricter, more "
              f"informative test; the manuscript should cite it as "
              f"primary, with C1 kept as a disclosed upper-bound "
              f"sensitivity check.")
    else:
        print(f"  COMPARISON: the channel-independent |rho| ({mech!r}) is "
              f"NOT smaller than C1's upper-bound reference "
              f"({c1_rho!r}) — report exactly what appeared; do not "
              f"narrate a reduction that did not occur.")
    print(f"  context: Y2's sibling reference (severity predictor vs "
          f"e.b) = +0.590, quoted from Y2's task summary — not recomputed")

    # ---- save -------------------------------------------------------
    out = PROC / "task108_c1prime_channel_null.csv"
    rows = []

    def add(section, key, value, note=""):
        rows.append(dict(section=section, key=key, value=value, note=note))

    add("cal", "target_esm", T_ESM, "D1 r_xx_median, task105 CSV")
    add("cal", "achieved_esm_primary", ach_esm, "median of 10 pairwise Spearmans, 5 reps on s_v")
    add("cal", "achieved_esm_secondary", sec_esm, "analysis arm pair")
    add("cal", "sigma_esm", sigma_esm)
    add("cal", "target_assay", T_ASSAY, "C3a rel_own, task47 CSV (record 0.6363)")
    add("cal", "achieved_assay_primary", ach_assay, "median of 10 pairwise Spearmans, 5 reps on s_v")
    add("cal", "achieved_assay_secondary", sec_assay, "analysis arm pair")
    add("cal", "sigma_assay", sigma_assay)
    add("verify", "v1a_worst_cross_channel_rho", worst, "gate <= 0.05")
    add("verify", "v1b_esm_arm_noise_rho", v1b_e, "gate <= 0.05")
    add("verify", "v1b_assay_arm_noise_rho", v1b_a, "gate <= 0.05")
    add("verify", "v1c_severity_cancellation_maxabs", v1c, "gate < 1e-12")
    add("verify", "v1d_eb_analytic_identity_maxabs", v1d, "gate < 1e-9")
    add("verify", "v4_nan_count", n_nan, "gate == 0")
    add("verify", "b_A_global", b_A)
    add("verify", "r_A_global", r_A)
    add("sim", "rho_shift_vs_eb_analog", sim_bs["observed_rho"],
        "channel-independent mechanism-only reference")
    add("sim", "ci_lo", sim_bs["ci_lo"])
    add("sim", "ci_hi", sim_bs["ci_hi"])
    add("sim", "p_boot", sim_bs["p_boot"])
    add("sim", "rho_no_correction", r_nc, "descriptive sensitivity only")
    add("c1_quoted", "rho_upper_bound", c1_rho,
        "quoted from task106 CSV, never recomputed")
    add("c1_quoted", "ci_lo", c1_lo)
    add("c1_quoted", "ci_hi", c1_hi)
    add("real", "rho_delta_esm_vs_own_e_b", real_bs["observed_rho"],
        "gated == -0.08811806424891734 (1e-9); CI fresh here")
    add("real", "ci_lo", real_bs["ci_lo"])
    add("real", "ci_hi", real_bs["ci_hi"])
    add("real", "p_boot", real_bs["p_boot"])
    add("compare", "obs_abs", obs)
    add("compare", "mech_abs", mech)
    add("compare", "mech_ci_lo_abs", lo)
    add("compare", "mech_ci_hi_abs", hi)
    add("compare", "verdict", verdict, "pre-registered 3-way rule (C1's rule, fresh CI)")
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n  saved {len(rows)} rows -> {out.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. Expected near-zero null (DISCLOSED PRE-RUN in this docstring):
     independent streams + a differencing shift cancel the shared
     severity identically (V1c), so this null's content is largely an
     ARCHITECTURE CHECK — it locates where C1's +0.937 came from
     (shared draws) and bounds mechanism-only injection across
     INDEPENDENT channels. It cannot rule out mechanisms operating
     through quantities the difference cancels.
  2. Calibrated MAGNITUDE, assumed SHAPE: additive Gaussian noise; only
     the scale is pinned to the measured 0.8826369680851056 (ESM) /
     0.6363275925044801 (assay). A different noise shape at the same
     reliability is a different sim — not tested.
  3. The two targets come from different measurement designs (D1:
     cross-checkpoint agreement on raw scores; C3a: synonymous-
     variant variance ratio); reused exactly as recorded per the task
     doc; the non-equivalence is disclosed, not resolved.
  4. Zero planted channel coupling is gated (V1a-V1d); it says nothing
     about whether the REAL -0.088 is free of interaction — the sim
     says what mechanism ALONE can produce across independent
     channels, nothing more.
  5. Inherited scale note (same as C1): f_bar draws sit in the arm
     slots where the real pipeline holds fitted wt/m scores from the
     same atlas assay (Y2/C1's identification), disclosed, not
     verified; the real A222V line enters only through expected() as
     one global constant (b_A/r_A printed).
  6. No per-concentration noise exists (Y2/C1 inheritance), so the WLS
     intercept reduces to its analytic form (V1d) — the real machinery
     runs, but the concentration dimension carries the background line
     and the correction, not noise.
  7. Cluster bootstrap over iid simulated rows (no position structure
     in the draws; the 654-position convention is mandated for
     comparability with the anchor's convention), disclosed.
  8. p_boot of the SIM only tests exclusion of zero; the meaningful
     comparison is magnitude-vs-magnitude (C1'c rule). No z-score is
     computed anywhere (AGENTS sec 3): p is the primary claim.
  9. n = 10,757 / 654; N_BOOT={N_BOOT} seed {SEED}; SMOKE={SMOKE}.
 10. C1's original numbers are quoted from task106_c1_mechanism_null.csv
     and never recomputed here — the two constructions are reported
     side by side, neither replacing the other.{os.linesep}""")
    print(f"\nSCRIPT 108 DONE ({time.time() - t0:.1f}s)  "
          f"ind_rho={float(sim_bs['observed_rho']):+.6f} "
          f"[{float(sim_bs['ci_lo']):+.6f}, "
          f"{float(sim_bs['ci_hi']):+.6f}] | C1_quoted={c1_rho:+.6f} | "
          f"real={float(real_bs['observed_rho']):+.6f} | verdict: "
          f"{verdict}")


if __name__ == "__main__":
    main()
