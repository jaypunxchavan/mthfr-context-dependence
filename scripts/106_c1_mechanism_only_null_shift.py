"""C1 — shift-side mechanism-only null for the delta_ESM/own_e_b anchor
(task doc `MANUSCRIPT_REVIEW_RESPONSE.md`, Group C, Task C1).

PRE-REGISTERED (this docstring written before the first run of this
script; C1e; AGENTS sec 6). Every frame, gate, generative choice,
threshold, bootstrap convention, and comparison rule below was fixed
before any number produced here was seen.

WHY (task background):
  Y2 (script 101) shows what a severity-only predictor with ZERO
  interaction capacity mechanically produces against measured e.b
  (rho ~ +0.590, quoted from the task doc's own summary of Y2). No
  equivalent reference point exists for the SHIFT statistic: what
  rho(delta_ESM, own_e_b) would mechanically be under an identical
  no-interaction generative mechanism. That number is needed to read
  the real anchor rho = -0.088 honestly (is it large, comparable, or
  small relative to what pure severity-scale structure alone gives a
  shift statistic?).

C1a MANDATE — read script 101 in full first (done before writing
  this) and reuse its exact generative approach: the real MTHFR
  fitness distribution (f_bar), a monotone severity-to-fitness
  relationship, and no interaction term of any kind. Y2's machinery,
  mirrored here: pool = task32_analysis_table.csv's f_bar (dropna,
  checked non-negative — the multiplicative model presumes a ratio
  scale, same check as script 101 L302); values drawn iid with
  replacement from that pool (seed 0); the severity->fitness map is
  the identity-through-the-empirical-pool as in Y2 (the empirical
  distribution IS the monotone map's realization), and the only
  composition anywhere is the atlas's multiplicative no-interaction
  expectation (the own_context construction, below). No non-monotone
  term, no severity-by-background term, no planted coupling of any
  kind.

C1b — TWO-BACKGROUND SIMULATION, the central design:
  For every row of the analysis frame (n = 10,757), draw TWO values:
      f_wt = rng.choice(f_bar)      (f(v | WT))
      f_av = rng.choice(f_bar)      (f(v | A222V))
  as TWO SEPARATE, INDEPENDENT draws from the IDENTICAL model (same
  pool, same generator, no shared noise, no term in the generator
  references both draws at once). The arms share ONLY the
  severity-to-fitness map (the pool F); there is NO interaction term
  connecting them. Therefore any correlation between the simulated
  shift and the simulated e.b-analog below is purely a MECHANICAL
  ARTIFACT of the measurement construction being tested, not a planted
  effect.

  ZERO-PLANTED-INTERACTION VERIFICATION IS A GATE, run BEFORE the
  statistic is computed (task requirement; failure => print,
  sys.exit(1), no retry, no threshold change):
  V1  Empirical arm independence: |Spearman(f_wt, f_av)| < 0.05.
      Threshold pre-registered: under true independence with
      n = 10,757 the sd of Spearman is ~1/sqrt(n-1) = 0.0096, so
      0.05 is ~5.2 sd; any coupling of practical size exceeds it,
      while an honest iid draw essentially never does.
  V2  Structural: the background enters ONLY through ONE GLOBAL
      constant line — the real p.Ala222Val row's own WT-arm fit
      (w["fitness"][i222], w["remediation"][i222] from
      rebuild_interaction_fit) — printed; no per-variant background
      array exists anywhere in the generator. A shared constant is a
      main effect, not an interaction.
  V3  Construction identity (AGENTS sec 4: every null carries an
      identity check in its own output): because Y2's noise structure
      has no per-concentration term (see below), the simulated
      residuals are EXACTLY linear in concentration, and the WLS
      intercept must equal the analytic form
          eb_analog = f_av - b_A * f_wt - cb(f_wt)
      to |diff| < 1e-9 (fixed pre-run). Fail => the construction did
      not run what it claims => STOP.
  V4  Accounting: eb_analog finite on all 10,757 rows (derivation in
      the code comment: frame rows have real own_e_b finite =>
      <=2 invalid concentration points under the stricter real mask
      => >=2 valid under the sim's mask => wls_line det > 0). Fail =>
      print the count and STOP.

C1c — CONSTRUCTION (the same weighted-least-squares own_context.py
  machinery used for the real own_e_b, run as the real code path):
  * shift_sim = f_av - f_wt, mirroring delta_esm = S(v|A222V) -
    S(v|WT) exactly.
  * e.b-analog: own_context.fit_interaction(m_score=f_av replicated
    across CONCS, m_se=REAL per-point standard errors, w_fitness=f_wt,
    w_remediation=0, w_post=1, w_mean_score=f_wt,
    a222v_fitness=REAL b_A, a222v_remediation=REAL r_A,
    correction=REAL two-pass (cb, cr) from rebuild_interaction_fit).
    That is the real expected(c) = sm(c) * a222v_line(c) [+ correction]
    (the atlas's MULTIPLICATIVE NO-INTERACTION expectation — the same
    composition Y2 calls its TRUE model), resid = m - expected, and
    e_b = wls_line(resid, m_se, CONCS, valid)[0] with the real
    >2-missing -> NA rule. The pipeline's FIXED parts (concentration
    grid, SE design, validity logic, global background line, the
    fitness-dependent correction) are reused real; only the two
    VARIANT-level arms are simulated, per C1b.
  * Noise structure = Y2's: the draw from the empirical pool IS the
    noise; there is NO per-concentration measurement noise, so
    m_score is constant across CONCS and the simulated residual is
    exactly linear in c (V3's identity). DISCLOSED consequence: the
    WLS machinery runs for real but its intercept reduces to the
    analytic form above — the concentration dimension carries the
    real background line's slope and the correction, not noise.
  * DISCLOSED scale note: f_bar draws (Y2's pool) are placed in the
    slots where the real pipeline holds fitted wt/m scores from the
    same atlas assay; treated as the same functionality scale (Y2
    makes the same identification), disclosed, not verified here.
  * DISCLOSED normalization note: the real own_context expected()
    does NOT divide by f_wt (unlike Y2's f_ij = f_i*f_j/f_wt);
    C1c mandates the own_context construction, so the atlas form
    governs.
  * STATISTIC: Spearman(shift_sim, eb_analog) via the project's
    standard position_cluster_bootstrap (scripts.lib.stats: clusters =
    the 654 real positions, resampled with replacement, rows of drawn
    positions concatenated, ranks recomputed per draw = re-derivation,
    N_BOOT from env default 10000, seed 0, two-sided sign-crossing
    p_boot; p == 0 reported as p < 1/N_BOOT). Identity check in the
    null's own output: bootstrap observed_rho must equal a direct
    _spearman(shift, eb_analog) to <1e-12.

C1d — COMPARISON AND VERDICT (pre-registered decision rule, fixed
  before running):
  The real anchor rho(delta_esm, own_e_b) is RE-DERIVED LIVE on this
  frame and gated: |rho_real - (-0.08811806424891734)| < 1e-9 (the
  canonical anchor: CALIBRATION_LOG L290, CLOSEOUT_LOG L1228,
  DEEPDIVE_LOG L3019 — three prior sources agree to all digits).
  Its CI is computed FRESH here with the same position-cluster
  convention (disclosed: computed in this script, not quoted from a
  prior log). The task quotes the anchor as -0.088 (4 dp); the
  re-derived full-precision value is printed either way.
  The mechanism-only reference |rho_sim| (point + 95% bootstrap CI)
  is placed beside |rho_real| = 0.08811806424891734, and the verdict
  maps EXACTLY as follows (C1d's own three words):
      |rho_real| below  the |rho_sim| CI  -> "-0.088 is SMALL
                                             relative to the
                                             reference"
      |rho_real| inside the |rho_sim| CI  -> "-0.088 is COMPARABLE
                                             to the reference"
      |rho_real| above  the |rho_sim| CI  -> "-0.088 is LARGE
                                             relative to the
                                             reference"
  All raw numbers (both points, both CIs, both p's, the SIGN of each)
  are printed regardless of which branch fires.
  SIGN is reported as its own observation: the mechanical artifact
  under this construction is expected to be POSITIVE (both statistics
  contain +f_av), while the anchor is negative — the sign contrast is
  itself a result and is printed, not folded into the magnitude
  verdict.
  DESCRIPTIVE SENSITIVITY (no decision attached): the same statistic
  with correction=None (the one invented knob — the real pipeline's
  fitness-dependent bias correction) is reported as a point estimate.

OUTPUT OF THE LIMITATIONS BLOCK (printed with results):
  1. Zero planted interaction is guaranteed by construction (V1-V2)
     and is a gate; it does NOT prove the REAL -0.088 is free of
     interaction — the sim says what mechanism ALONE can produce,
     nothing more.
  2. The sim forces shift and e.b-analog to share the SAME two arm
     draws (that shared-driver structure IS the construction being
     measured); in reality delta_ESM (ESM scores) and own_e_b
     (folinate measurements) are different measurement channels whose
     only shared driver is the variant's true biology — so the
     reference is an UPPER-bound-style stress test of shared-driver
     coupling, not a like-for-like null of the real pipelines.
  3. The two simulated arms are identically distributed (no
     background main effect inside the arms themselves); the real
     atlas background line enters only through expected() (V2).
     Identical-map arms are exactly what C1b mandates.
  4. Y2's noise structure carries no per-concentration term, so the
     WLS intercept reduces analytically (V3) — the machinery runs,
     but the concentration dimension contributes the background
     line's slope and the correction, not noise.
  5. Cluster bootstrap on iid simulated rows: the draws have no
     position structure (as Y2 disclosed), yet C1c mandates the
     position-cluster convention for comparability with the anchor's
     convention — run as mandated, disclosed.
  6. p_boot for the SIM is about whether the mechanical rho excludes
     zero; the MEANINGFUL comparison here is magnitude-vs-magnitude
     (C1d), not the sim's p.
  7. n = 10,757 rows / 654 positions (script 33's frame); pool =
     task32 f_bar dropna (printed); N_BOOT env default 10000
     (smoke 300), seed 0.

GATES SUMMARY (failure => print, sys.exit(1); no N-raise, no rule
  change): G0 inputs exist (exact path printed if missing); G1 frame
  == 10,757/654 and every hgvs_pro maps to a raw row; G2 real anchor
  reproduction to 1e-9; G3 f_bar pool non-negative (ratio-scale
  presumption, script 101's check); V1-V4 as above; I1 bootstrap
  observed_rho == direct _spearman (<1e-12).

SMOKE: N_BOOT=300 first (all gates + point values), then full 10000.
OUTPUT: data/processed/task106_c1_mechanism_null.csv (tidy long).
Existing scripts/CSVs untouched; next free script number after this:
107.
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Cosmetic (disclosed): the REAL pipeline's np.nanmean on rows whose
# WT-arm scores are entirely NaN emits "Mean of empty slice" from
# rebuild_interaction_fit — pre-existing behavior of scripts 101/33's
# shared code path, unrelated to this simulation. Suppressed so the
# gate/verification output stays readable; nothing is hidden from any
# gate (all counts are printed explicitly below).
warnings.filterwarnings("ignore", message="Mean of empty slice")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.own_context import CONCS, fit_interaction  # noqa: E402
from scripts.lib.stats import _spearman, position_cluster_bootstrap  # noqa: E402
from scripts.lib.stats_ext import rebuild_interaction_fit  # noqa: E402

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = N_BOOT <= 500

G_ANCHOR = -0.08811806424891734   # canonical rho(delta_esm, own_e_b)
V1_TOL = 0.05                     # pre-registered arm-independence gate
V3_TOL = 1e-9                     # pre-registered WLS-identity tolerance
V4_EXPECT_NAN = 0


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def main():
    t0 = time.time()
    banner(f"C1 — shift-side mechanism-only null (scripts/106)  "
           f"N_BOOT={N_BOOT} seed={SEED}"
           + ("  [SMOKE]" if SMOKE else ""))

    # ---- G0: inputs -------------------------------------------------
    paths = {
        "raw fit": RAW / "results" / "folate_response_model5.csv",
        "phase5": PROC / "phase5_analysis_table.csv",
        "own metrics": PROC / "own_context_metrics.csv",
        "f_bar pool": PROC / "task32_analysis_table.csv",
    }
    for label, p in paths.items():
        if not p.exists():
            gfail(f"G0 FAIL: {label} input missing: {p} — stop.")
    print("  G0 PASS: all 4 inputs present")

    # ---- G1: frame (script 101's exact construction) ----------------
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
    print(f"  G1 PASS: script-33 frame = {n_rows} rows / {n_pos} "
          f"positions; all hgvs_pro map to raw fit rows")

    # ---- G2: real anchor reproduced live ----------------------------
    delta = df["delta_esm"].to_numpy(float)
    own_eb = df["own_e_b"].to_numpy(float)
    r_real = _spearman(delta, own_eb)
    if abs(r_real - G_ANCHOR) > 1e-9:
        gfail(f"G2 FAIL: rho(delta_esm, own_e_b) = {r_real!r} vs "
              f"canonical {G_ANCHOR!r} (tol 1e-9) — two sources "
              f"disagree, stop.")
    print(f"  G2 PASS: real anchor reproduced live: rho(delta_esm, "
          f"own_e_b) = {r_real!r} == {G_ANCHOR!r} (tol 1e-9; task "
          f"quotes -0.088 at 4 dp)")

    # ---- G3: f_bar pool (Y2's generative base) ----------------------
    t32 = pd.read_csv(paths["f_bar pool"], usecols=["f_bar", "f_bar_wt"])
    f = t32["f_bar"].dropna().to_numpy(float)
    if (f < 0).any():
        gfail("G3 FAIL: negative f_bar values — multiplicative model "
              "presumes ratio scale (script 101's check) — stop.")
    fwt = float(np.median(t32["f_bar_wt"].dropna()))
    print(f"  G3 PASS: f_bar pool n={len(f)} "
          f"range=[{f.min():.4f}, {f.max():.4f}] non-negative; "
          f"f_wt (median f_bar_wt)={fwt:.4f} printed for Y2 context")

    # ---- C1b: two independent draws ---------------------------------
    # Real pipeline's fixed parts reused (V2 prints them):
    w = fit["w"]
    i222 = fit["i222"]
    b_A = float(w["fitness"][i222])
    r_A = float(w["remediation"][i222])
    cb, cr = fit["correction"]
    Mse = fit["M_se"][src]

    rng = np.random.default_rng(SEED)
    f_wt = rng.choice(f, size=n_rows, replace=True)   # f(v | WT)
    f_av = rng.choice(f, size=n_rows, replace=True)   # f(v | A222V)
    shift = f_av - f_wt                               # mirrors delta_esm

    banner("ZERO-PLANTED-INTERACTION VERIFICATION (gate BEFORE the "
           "statistic)", "-")
    print(f"  generator: two SEPARATE rng.choice calls over the same "
          f"pool; no term references both draws; arms share ONLY the "
          f"severity-to-fitness map (pool of {len(f)} real f_bar "
          f"values, Y2's generative base)")
    print(f"  mean/median: f_wt {f_wt.mean():.6f}/{np.median(f_wt):.6f} "
          f"| f_av {f_av.mean():.6f}/{np.median(f_av):.6f} "
          f"(identical-model sanity)")
    v1 = _spearman(f_wt, f_av)
    print(f"  V1 Spearman(f_wt, f_av) = {v1!r}  (gate: |rho| < "
          f"{V1_TOL})")
    if abs(v1) >= V1_TOL:
        gfail(f"V1 FAIL: arms are not independent (|rho| = "
              f"{abs(v1):.6f} >= {V1_TOL}) — planted coupling "
              f"suspected — stop.")
    print(f"  V1 PASS: arms independent — no planted interaction")
    print(f"  V2 structural: background enters ONLY via ONE GLOBAL "
          f"constant line — p.Ala222Val row index {i222}, "
          f"b_A={b_A!r}, r_A={r_A!r}; no per-variant background array "
          f"exists in the generator (shared constant = main effect, "
          f"not interaction) — PASS")

    # ---- e.b-analog through the REAL own_context construction -------
    m_sim = np.repeat(f_av[:, None], len(CONCS), axis=1)
    sim_e2 = fit_interaction(m_sim, Mse, f_wt, np.zeros(n_rows),
                             np.ones(n_rows), f_wt, b_A, r_A,
                             correction=(cb, cr))
    eb = sim_e2["e_b"]
    n_nan = int(np.isnan(eb).sum())
    print(f"  V4 accounting: eb_analog finite = "
          f"{n_rows - n_nan}/{n_rows} (expected all; frame rows have "
          f"real own_e_b finite => <=2 invalid concs under the "
          f"stricter real mask) ")
    if n_nan != V4_EXPECT_NAN:
        gfail(f"V4 FAIL: {n_nan} NaN in eb_analog "
              f"(expected {V4_EXPECT_NAN}) — stop.")
    print(f"  V4 PASS")
    analytic = f_av - b_A * f_wt - cb(f_wt)
    v3 = float(np.nanmax(np.abs(eb - analytic)))
    print(f"  V3 identity: max|eb_analog - (f_av - b_A*f_wt - "
          f"cb(f_wt))| = {v3:.3e}  (gate < {V3_TOL:.0e})")
    if v3 >= V3_TOL:
        gfail(f"V3 FAIL: WLS intercept does not equal its analytic "
              f"form ({v3:.3e}) — the construction did not run what "
              f"it claims — stop.")
    print(f"  V3 PASS: the real wls_line path reproduces the analytic "
          f"intercept exactly — eb_analog = f_av - {b_A:.6f}*f_wt - "
          f"cb(f_wt), i.e. the mechanical coupling between shift and "
          f"e.b-analog is fully characterized")
    for i in range(5):
        print(f"    row {i}: f_wt={f_wt[i]:.6f} f_av={f_av[i]:.6f} "
              f"shift={shift[i]:+.6f} eb_analog={eb[i]:+.6f} "
              f"analytic={analytic[i]:+.6f}")

    # ---- statistic: position-cluster bootstrap ----------------------
    banner(f"MECHANISM-ONLY STATISTIC + REAL ANCHOR (both "
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
              f"{sim_bs['observed_rho']!r} != direct "
              f"_spearman {r_sim!r} — stop.")
    print(f"  I1 PASS: bootstrap observed == direct Spearman "
          f"({r_sim!r}), identity check inside the null's own output")
    real_bs = position_cluster_bootstrap(df, "position", "delta_esm",
                                         "own_e_b", n_boot=N_BOOT,
                                         seed=SEED)

    def pp(tag, bs, r):
        p = bs["p_boot"]
        pstr = f"<{1.0 / N_BOOT:.1e}" if p == 0 else f"{p:.4f}"
        print(f"  [{tag}] rho={float(r)!r}  "
              f"CI [{float(bs['ci_lo'])!r}, {float(bs['ci_hi'])!r}]  "
              f"p_boot={pstr}  "
              f"(n={bs['n_rows']}, {bs['n_clusters']} positions)")

    pp("MECHANISM-ONLY (sim shift vs sim e.b)", sim_bs, r_sim)
    pp("REAL anchor (delta_esm vs own_e_b)", real_bs, real_bs["observed_rho"])
    if abs(real_bs["observed_rho"] - r_real) >= 1e-12:
        gfail("I1b FAIL: real bootstrap observed != direct Spearman — "
              "stop.")

    # descriptive sensitivity: without the pipeline's correction
    sim_nc = fit_interaction(m_sim, Mse, f_wt, np.zeros(n_rows),
                             np.ones(n_rows), f_wt, b_A, r_A,
                             correction=None)
    r_nc = _spearman(shift, sim_nc["e_b"])
    print(f"  descriptive sensitivity (correction=None, point "
          f"estimate only, no decision): rho={r_nc!r}")

    # ---- C1d: pre-registered verdict --------------------------------
    banner("C1d — PREDICTION-STYLE COMPARISON (pre-registered rule)", "-")
    obs = abs(real_bs["observed_rho"])
    mech = abs(sim_bs["observed_rho"])
    lo = float(min(abs(sim_bs["ci_lo"]), abs(sim_bs["ci_hi"])))
    hi = float(max(abs(sim_bs["ci_lo"]), abs(sim_bs["ci_hi"])))
    print(f"  mechanism-only |rho| = {mech!r}, 95% CI on |rho| "
          f"[{lo!r}, {hi!r}]")
    print(f"  real observed |rho| = {obs!r} (task quotes -0.088; "
          f"canonical {G_ANCHOR!r})")
    if obs < lo:
        verdict = ("SMALL relative to the mechanical reference point — "
                   "the observed |−0.088| sits BELOW the mechanism-only "
                   "CI")
    elif obs > hi:
        verdict = ("LARGE relative to the mechanical reference point — "
                   "the observed |−0.088| sits ABOVE the mechanism-only "
                   "CI")
    else:
        verdict = ("COMPARABLE to the mechanical reference point — the "
                   "observed |−0.088| sits INSIDE the mechanism-only CI")
    print(f"  SIGN observation: mechanism rho = {r_sim:+.6f} "
          f"({'+pos' if r_sim > 0 else '-neg'}), real rho = "
          f"{real_bs['observed_rho']:+.6f} ({'+pos' if real_bs['observed_rho'] > 0 else '-neg'})"
          f" — sign contrast reported as its own result, not folded "
          f"into the magnitude verdict")
    print(f"  VERDICT: −0.088 is {verdict}")
    print(f"  context: Y2's sibling reference (severity predictor vs "
          f"e.b) = +0.590, quoted from the task doc's own Y2 summary — "
          f"not recomputed here")

    # ---- save --------------------------------------------------------
    out = PROC / "task106_c1_mechanism_null.csv"
    rows = []

    def add(section, key, value, note=""):
        rows.append(dict(section=section, key=key, value=value,
                         note=note))

    add("real", "rho_delta_esm_vs_own_e_b", real_bs["observed_rho"],
        "gated == -0.08811806424891734 (1e-9); CI computed fresh here")
    add("real", "ci_lo", real_bs["ci_lo"])
    add("real", "ci_hi", real_bs["ci_hi"])
    add("real", "p_boot", real_bs["p_boot"])
    add("sim", "rho_shift_vs_eb_analog", sim_bs["observed_rho"],
        "mechanism-only reference (zero planted interaction, V1-V4)")
    add("sim", "ci_lo", sim_bs["ci_lo"])
    add("sim", "ci_hi", sim_bs["ci_hi"])
    add("sim", "p_boot", sim_bs["p_boot"])
    add("sim", "rho_no_correction", r_nc, "descriptive sensitivity only")
    add("verify", "v1_arm_spearman", v1, "gate |rho| < 0.05")
    add("verify", "v3_wls_identity_maxabs", v3, "gate < 1e-9")
    add("verify", "v4_nan_count", n_nan, "gate == 0")
    add("verify", "b_A_global", b_A, "single global background base")
    add("verify", "r_A_global", r_A, "single global background slope")
    add("compare", "obs_abs", obs)
    add("compare", "mech_abs", mech)
    add("compare", "mech_ci_lo_abs", lo)
    add("compare", "mech_ci_hi_abs", hi)
    add("compare", "verdict", verdict, "pre-registered 3-way rule")
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\n  saved {len(rows)} rows -> {out.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. Zero planted interaction (V1-V2, gated) guarantees the SIM
     has none; it does not prove the real -0.088 is free of
     interaction. This script says what mechanism ALONE can produce.
  2. Shift and e.b-analog share the SAME two arm draws by design —
     that shared-driver structure is the construction under test. In
     reality delta_ESM (ESM scores) and own_e_b (folinate
     measurements) are different channels sharing only true variant
     biology, so this reference is an upper-bound-style stress test
     of shared-driver coupling, not a like-for-like null of the two
     real pipelines.
  3. The simulated arms are identically distributed (no background
     main effect inside the arms — exactly C1b's identical-model
     mandate); the real A222V line enters only through expected()
     as one global constant (V2).
  4. Y2's noise structure has no per-concentration term, so the
     simulated residuals are exactly linear in concentration and the
     WLS intercept reduces to its analytic form (V3) — the real
     machinery runs, but the concentration dimension carries the
     background line's slope and the correction, not noise.
  5. The bootstrap resamples the 654 real positions over iid
     simulated rows (no position structure exists in the draws, as
     Y2 disclosed); the convention is run because C1c mandates it
     for comparability with the anchor's convention.
  6. The sim's p_boot only tests exclusion of zero; the meaningful
     comparison is magnitude-vs-magnitude (C1d's rule), and the sim's
     p is not used as evidence for anything.
  7. The real anchor CI is computed fresh in this script (same
     convention as the sim's), NOT quoted from a prior log.
  8. n = 10,757 / 654; f_bar pool = task32 dropna (printed); two
     draws per row from that pool; N_BOOT={N_BOOT} seed {SEED};
     smoke flag SMOKE={SMOKE}.{os.linesep}"""
    )
    print(f"\nSCRIPT 106 DONE ({time.time() - t0:.1f}s)  "
          f"mech_rho={r_sim:+.6f} [{sim_bs['ci_lo']:+.6f}, "
          f"{sim_bs['ci_hi']:+.6f}] | real={real_bs['observed_rho']:+.6f} "
          f"| verdict: {verdict}")


if __name__ == "__main__":
    main()
