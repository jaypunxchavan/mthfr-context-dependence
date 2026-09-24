"""
Script 72 (task AA4, group AA of DETECTION_FLOOR_AND_MECHANISM.md):
a detection floor for MTHFR's OWN design - how small a correlation
could this pipeline have detected against its real e.b?

WHY (task doc AA4a-AA4d)
------------------------------------------------------------------
The project's headline is a NULL-ish result: delta_ESM rho = -0.088
against measured interaction.  Absence of evidence is only informative
if we know the instrument's floor.  AA4 injects predictors with KNOWN
correlation into the real design (actual n, actual position
clustering, actual per-condition noise) and pushes them through the
EXACT two-test pipeline used on delta_ESM (position-cluster bootstrap
+ script 33's sign-flip re-derivation null, same N_BOOT/N_PERM), then
reports the smallest rho_true detected at ~80% power as:
"we could have detected rho >= X; we observed -0.088."

PRE-REGISTERED RULES (fixed in this docstring before ANY run; AGENTS 6)
------------------------------------------------------------------
F1  Analysis frame = script 33's exact construction, reused not
    rewritten: rebuild_interaction_fit(folate_response_model5.csv) ->
    per-cell residuals Rs / se Ss / valid Vs; merge phase5_analysis_
    table with own_context_metrics; dropna(delta_esm, own_e_b);
    reset_index.  Expected 10757 rows / 654 positions (printed).
    Identity checks copied from script 33 (all-+1 flips reproduce
    own_e_b to <=1e-6, all--1 give its exact negation) run FIRST and
    sys.exit(1) on failure - the test is tested before it is used.
F2  What is injected, and the AA4a "partial correlation" reading
    (logged as an interpretation, rule 6): the headline -0.088 is a
    PLAIN position-cluster Spearman between a predictor and own_e_b,
    so AA4 injects a plain Spearman rho between X and the REAL
    own_e_b (outcome side untouched - that is what keeps n,
    clustering, and measured noise real).  "Partial" is read as
    "a real, nonzero correlation," not a covariate-adjusted partial
    coefficient; injecting a partial would not be comparable to -0.088.
F3  Construction of one simulated predictor replicate (rho_true, r):
      z_e    = Phi^-1((rankdata(own_e_b) - 0.5)/n)   (rank-normal; monotone)
      sigma_i= row-wise nanmedian of the 8 measured per-condition SE
               cells (w12.se..w200.se, m12.se..m200.se; own_context's
               own WT_SE_COLS/MT_SE_COLS) on this row's raw record,
               normalized to mean 1 - the "measured per-condition
               noise" ingredient; all-NaN rows filled with the
               row-median (count printed).
      w      = measured within-position variance share of z_e:
               one-way ANOVA method of moments,
               w = (MSB - MSW) / (MSB + (k_bar - 1)*MSW), clipped to
               [0, 0.999] - the "actual position clustering
               structure" ingredient (printed).
      v_raw  = sqrt(w)*p_pos + sqrt(1-w)*(sigma*eps)/sd(sigma*eps),
               p_pos ~ N(0,1) per position, eps ~ N(0,1) per row
      v      = v_raw orthogonalised against z_e, re-centred, sd 1
               (guarantees the injected Pearson equals r exactly per
               replicate despite realized Cov(z_e, v_raw))
      r      = SOLVED, not formula-assumed: bisection on r in [0,1]
               so that the MEAN achieved Spearman over a fixed pilot
               batch (pilot rng seed=1, M=25 noise draws, rng
               re-seeded each evaluation so the objective is a pure
               function of r, 24 bisection iterations) equals
               rho_true; the Gaussian-copula closed form
               r = 2*sin(pi*rho_true/6) is kept only as conceptual
               motivation.  rho_true = 0.0 uses r = 0 directly.
               *** AMENDMENT, disclosed per AGENTS 6: chosen AFTER the
               N_BOOT=300 smoke, BEFORE any full run.  The smoke's
               real numbers showed the closed form overshooting the
               target by +0.020 (rho 0.10) to +0.044 (rho 0.20-0.25)
               because v is a heteroscedastic scale mixture, not
               bivariate-normal, so 2*sin(pi*rho/6) is not the exact
               inverse here.  Fixing the GENERATOR to hit its
               specified input is a construction bug fix; the +-0.01
               F3 criterion below is UNCHANGED, and the smoke values
               are quoted verbatim in DEEPDIVE_LOG [AA4]. ***
    ACHIEVED Spearman(X, own_e_b) is measured, never assumed, and
    reported per replicate; hard construction gate in full runs only
    (R >= 20): |mean(achieved) - rho_true| <= 0.01 per grid point
    (smoke runs print but do not gate).
F4  Grid = AA4a's literal list plus a null-calibration point, all at
    equal weight: rho_true in {0.0, 0.05, 0.10, 0.15, 0.20, 0.25}.
    0.0 is the CALIBRATION row (type-I check, not part of the floor):
    with R >= 20 full runs, sign-flip rejection rate at rho=0 must be
    <= 0.15 (a priori: >3x the nominal 0.05 means the machinery is
    broken -> FAIL the task); a LOW rate is not a failure.
    NO adaptive refinement: the floor is reported at the grid's
    native 0.05 resolution (pre-empting post-hoc grid extension).
F5  Replicates R = AA4_R env, default 50 (binomial se of power at
    0.80 ~ 5.7pp, matching "at ~80% power"); smoke convention:
    N_BOOT < 1000 -> R defaults to 3, output file gets _smoke suffix.
F6  Both tests of the real pipeline, same N_BOOT/N_PERM (env,
    default 10000, seed 0 everywhere):
    - sign-flip re-derivation null, script 33's path REUSED
      (wls_line on randomly sign-flipped per-cell residuals, re-fit
      own_e_b, _spearman(pred, eb_p), p = mean(|null| >= |obs|)).
      The null e_b vectors do not depend on the predictor, so the
      N_PERM flips are drawn ONCE (default_rng(0), the project's
      seed convention) and reused across all replicates - identical
      math to re-running per replicate, disclosed here.
      DETECTION (primary, this is the instrument that produced the
      headline): signflip p < 0.05.
    - position-cluster bootstrap (scripts/lib/stats.py
      position_cluster_bootstrap semantics): cluster draws are shared
      across replicates for the same reason lib itself reseeds
      default_rng(0) on every call (every call in this project sees
      the same draws).  DETECTION (secondary): 95% CI excludes 0.
    SHARED-DRAW IDENTITY GATE (AGENTS 4): three fixed (rho,rep)
    pairs are also computed by calling lib's
    position_cluster_bootstrap independently; max|diff| across
    (observed, ci_lo, ci_hi, p_boot) must be < 1e-9 or exit(1).
    Sign-flip construction identity: all-+1/all--1 checks (F1).
    Sign-flip null non-finite cells: structurally impossible (flips
    do not change weights/validity); count is asserted 0 or exit(1).
F7  Floor statement (AA4c) = smallest rho_true in {0.05..0.25} with
    signflip power >= 0.80 over the R replicates; if none, report
    ">= 0.25 not reached" with the power AT 0.25 - no rounding
    inward.  Calibration power printed alongside.
F8  Output = data/processed/task_AA4_detection_floor.csv (exactly the
    AA4d name), one row per (rho,replicate) at level=replicate plus
    one row per rho at level=rho_summary:
    level, rho_true, replicate, obs_rho, boot_ci_lo, boot_ci_hi,
    boot_p, detected_boot, signflip_p, signflip_null_mean,
    signflip_null_sd, detected_signflip, n, n_positions, N_BOOT,
    N_PERM, R.

LIMITATIONS (printed with the output, AGENTS 6)
------------------------------------------------------------------
  * Design-based power on the REAL outcome: X is injected against the
    measured own_e_b (literal AA4a reading), so the floor answers
    "can this pipeline detect an association of strength rho with the
    measured e.b" - not a latent-signal recovery claim.
  * Grid resolution 0.05; R=50 gives power se ~5.7pp near 0.80.
  * Positive-rho injection, two-sided tests (|null| >= |obs|), so
    direction does not affect the floor.
  * Sign-flip flips share the seed-0 convention but are drawn by this
    script's own rng instance (script 33 interleaves its signed and
    absolute arms in one stream; that interleaving is irrelevant to
    the null's validity and is disclosed here).
  * p-values apply to own_e_b; transfer to the published e.b only as
    far as the two agree (script 17 prints that agreement).
  * Reproduction of script 33's estimator here is reuse, not
    replication (AGENTS 6).
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.own_context import wls_line, CONCS, WT_SE_COLS, MT_SE_COLS  # noqa: E402
from scripts.lib.stats import _spearman, position_cluster_bootstrap  # noqa: E402
from scripts.lib.stats_ext import rebuild_interaction_fit  # noqa: E402
from scripts.lib.regions import assign_region  # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
R = int(os.environ.get("AA4_R", "3" if N_BOOT < 1000 else "50"))
SEED = 0
SMOKE = N_BOOT < 1000
GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]
HARD_GATES = (not SMOKE) and R >= 20      # F3/F4 gates need real R
CAL_MAX = 0.15                             # F4 a priori type-I ceiling
GATE_RHO_TOL = 0.01                        # F3 construction tolerance

PROC = ROOT / "data/processed"
RAW = ROOT / "data/raw/mthfrModel"
OUT = PROC / ("task_AA4_detection_floor" + ("_smoke.csv" if SMOKE else ".csv"))


def summarize(boot):
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    p = min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0)
    return float(ci_lo), float(ci_hi), float(p)


def main():
    T = {}
    t0 = time.time()
    print(f"Script 72 / AA4 detection floor  N_BOOT={N_BOOT} N_PERM={N_PERM} "
          f"R={R} seed={SEED} smoke={SMOKE} hard_gates={HARD_GATES}")
    print("F3 generator NOTE: r solved by pilot bisection (post-smoke "
          "amendment, disclosed in docstring F3 and DEEPDIVE_LOG [AA4]); "
          "F3 +-0.01 criterion unchanged.")
    if SMOKE:
        print("*** SMOKE RUN: machinery checks only, NOT findings, "
              "NOT for quoting. ***")
    print(f"grid (F4, incl. 0.0 calibration): {GRID}  floor resolution 0.05")

    # ---- F1: exact script-33 frame ----------------------------------------
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse = fit["e2"], fit["M_se"]
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left").dropna(subset=["delta_esm", "own_e_b"])
    df = df.reset_index(drop=True)
    df["region"] = assign_region(df["position"])
    n, npos = len(df), df["position"].nunique()
    print(f"frame: {n} rows / {npos} positions (script 33 published: 10757/654: "
          f"{'MATCH' if (n, npos) == (10757, 654) else 'DIFFERS'})")

    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in df["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]
    own_eb = df["own_e_b"].to_numpy()

    # ---- F1 identity checks (script 33's, verbatim logic) -----------------
    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    d_p = float(np.abs(chk_p[ok] - own_eb[ok]).max())
    d_m = float(np.abs(chk_m[ok] + own_eb[ok]).max())
    print(f"  all-+1 flips reproduce own_e_b exactly: max|diff|={d_p:.3e}")
    print(f"  all--1 flips give exactly -own_e_b:     max|diff|={d_m:.3e}")
    if d_p > 1e-6 or d_m > 1e-6:
        print("*** IDENTITY CHECK FAILED - stop here (AGENTS 4). ***")
        sys.exit(1)

    # ---- F3 ingredients: measured noise + position structure --------------
    se_cells = np.hstack([raw[WT_SE_COLS].to_numpy(float),
                          raw[MT_SE_COLS].to_numpy(float)])[src]
    with np.errstate(invalid="ignore"):
        sigma = np.nanmedian(se_cells, axis=1)
    n_fill = int(np.isnan(sigma).sum())
    if n_fill:
        sigma = np.where(np.isnan(sigma), np.nanmedian(sigma), sigma)
    if not np.isfinite(sigma).all() or np.nanmean(sigma) <= 0:
        print("*** sigma (measured per-condition noise) unusable - FAIL. ***")
        sys.exit(1)
    sigma = sigma / sigma.mean()
    print(f"measured per-condition noise: sigma_i from 8 SE cells "
          f"(median per row), {n_fill} rows filled, "
          f"sd(sigma)={sigma.std():.4f}")

    z_e = norm.ppf((rankdata(own_eb) - 0.5) / n)
    pos_ids, pos_idx = np.unique(df["position"].to_numpy(), return_inverse=True)
    J = len(pos_ids)
    gsum = np.bincount(pos_idx, weights=z_e)
    gcnt = np.bincount(pos_idx)
    gmean = gsum / gcnt
    grand = z_e.mean()
    ssb = float(np.sum(gcnt * (gmean - grand) ** 2))
    ssw = float(np.sum((z_e - gmean[pos_idx]) ** 2))
    msb = ssb / (J - 1)
    msw = ssw / (n - J)
    kbar = n / J
    icc = (msb - msw) / (msb + (kbar - 1) * msw)
    w_pos = float(np.clip(icc, 0.0, 0.999))
    print(f"position clustering: J={J} positions, k_bar={kbar:.2f}, "
          f"MSB={msb:.4f} MSW={msw:.4f} -> ICC={icc:.4f} "
          f"-> w={w_pos:.4f} (structure ingredient)")

    # ---- F3: build all replicates ----------------------------------------
    # r is SOLVED per target (F3 amendment, post-smoke/pre-full-run): the
    # closed-form copula overshoots on this scale-mixture noise, so bisect
    # against mean achieved Spearman over a fixed pilot batch.
    pilot_rng_seed = 1
    M_PILOT = 25   # pre-full-run: pilot mean se ~0.001, well under F3's 0.01

    def pilot_mean_achieved(rt, r_cand):
        rng_p = np.random.default_rng(pilot_rng_seed)   # re-seeded: pure f(r)
        out = np.empty(M_PILOT)
        for m in range(M_PILOT):
            p_pos = rng_p.standard_normal(J)
            e = sigma * rng_p.standard_normal(n)
            e = e / e.std()
            v_raw = np.sqrt(w_pos) * p_pos[pos_idx] + np.sqrt(1 - w_pos) * e
            v_raw = v_raw - v_raw.mean()
            v = v_raw - z_e * (float(v_raw @ z_e) / float(z_e @ z_e))
            v = v / v.std()
            X = r_cand * z_e + np.sqrt(max(0.0, 1 - r_cand ** 2)) * v
            out[m] = _spearman(X, own_eb)
        return float(out.mean())

    r_cal = {}
    for rt in GRID:
        if rt == 0.0:
            r_cal[rt] = 0.0
            continue
        lo, hi = 0.0, 1.0
        for _ in range(24):
            mid = 0.5 * (lo + hi)
            if pilot_mean_achieved(rt, mid) >= rt:
                hi = mid
            else:
                lo = mid
        r_cal[rt] = 0.5 * (lo + hi)
        print(f"  calibration rho_true={rt:.2f}: r={r_cal[rt]:.6f} "
              f"(copula closed form would be "
              f"{2 * np.sin(np.pi * rt / 6):.6f}), pilot mean achieved="
              f"{pilot_mean_achieved(rt, r_cal[rt]):+.5f}")

    rng = np.random.default_rng(SEED)
    pairs = [(rt, r) for rt in GRID for r in range(R)]
    Xmat = np.empty((len(pairs), n))
    achieved = np.empty(len(pairs))
    tB = time.time()
    for k, (rt, r) in enumerate(pairs):
        p_pos = rng.standard_normal(J)
        e = sigma * rng.standard_normal(n)
        e = e / e.std()
        v_raw = np.sqrt(w_pos) * p_pos[pos_idx] + np.sqrt(1 - w_pos) * e
        v_raw = v_raw - v_raw.mean()
        v = v_raw - z_e * (float(v_raw @ z_e) / float(z_e @ z_e))
        v = v / v.std()
        rc = r_cal[rt]
        X = rc * z_e + np.sqrt(1 - rc ** 2) * v
        Xmat[k] = X
        achieved[k] = _spearman(X, own_eb)
    T["build"] = time.time() - tB
    print(f"built {len(pairs)} predictors ({len(GRID)} rho x R={R}) in "
          f"{T['build']:.1f}s")

    obs = np.array([_spearman(Xmat[k], own_eb) for k in range(len(pairs))])
    for i_rt, rt in enumerate(GRID):
        sl = slice(i_rt * R, (i_rt + 1) * R)
        print(f"  rho_true={rt:.2f}: achieved rho mean={obs[sl].mean():+.4f} "
              f"sd={obs[sl].std():.4f} (target {rt:.2f})")
    if HARD_GATES:
        worst = max(abs(obs[i_rt * R:(i_rt + 1) * R].mean() - rt)
                    for i_rt, rt in enumerate(GRID))
        print(f"F3 construction gate: worst |mean achieved - target| = "
              f"{worst:.4f} (tol {GATE_RHO_TOL}) -> "
              f"{'PASS' if worst <= GATE_RHO_TOL else 'FAIL'}")
        if worst > GATE_RHO_TOL:
            sys.exit(1)

    # ---- F6a: sign-flip null (script 33's path, flips drawn once) ---------
    tS = time.time()
    rng_sf = np.random.default_rng(SEED)
    n_nf = 0
    null_rhos = np.empty((N_PERM, len(pairs)))
    # ranks of X once (centered), for the chunked GEMM below
    XR = rankdata(Xmat, axis=1)
    XR = XR - XR.mean(axis=1, keepdims=True)
    Xn = np.sqrt((XR * XR).sum(axis=1))          # (K,)
    chunk = 500
    for a in range(0, N_PERM, chunk):
        b = min(a + chunk, N_PERM)
        blk = np.empty((b - a, n))
        for p in range(a, b):
            eb_p, _, _ = wls_line(Rs * rng_sf.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            blk[p - a] = eb_p
        n_nf += int((~np.isfinite(blk)).sum())
        RB = rankdata(blk, axis=1)
        RB = RB - RB.mean(axis=1, keepdims=True)
        Rn = np.sqrt((RB * RB).sum(axis=1))
        null_rhos[a:b] = (RB @ XR.T) / np.outer(Rn, Xn)
    T["signflip"] = time.time() - tS
    if n_nf:
        print(f"*** {n_nf} non-finite re-derived e_b cells - structurally "
              f"impossible (F6) - FAIL. ***")
        sys.exit(1)
    print(f"sign-flip null: {N_PERM} re-derivations x {len(pairs)} predictors "
          f"in {T['signflip']:.1f}s (flips drawn once, seed={SEED}; "
          f"non-finite cells = {n_nf})")

    sf_p = np.array([(np.abs(null_rhos[:, k]) >= abs(obs[k])).mean()
                     for k in range(len(pairs))])
    sf_mean = null_rhos.mean(axis=0)
    sf_sd = null_rhos.std(axis=0)

    # ---- F6b: position-cluster bootstrap (shared draws, lib semantics) ----
    tBt = time.time()
    clusters = df["position"].unique()
    idx_by = {c: df.index[df["position"] == c].to_numpy() for c in clusters}
    pos_map = {c: np.searchsorted(df.index.to_numpy(), idx_by[c]) for c in clusters}
    rng_b = np.random.default_rng(SEED)
    K = len(pairs)
    boot = np.empty((N_BOOT, K))
    pre = np.empty(K)
    for k in range(K):
        pre[k] = _spearman(Xmat[k], own_eb)
    for b in range(N_BOOT):
        drawn = rng_b.choice(clusters, size=len(clusters), replace=True)
        i = np.concatenate([pos_map[c] for c in drawn])
        Reb = rankdata(own_eb[i])
        Reb = Reb - Reb.mean()
        eb_n = np.sqrt(float(Reb @ Reb))
        RX = rankdata(Xmat[:, i], axis=1)
        RX = RX - RX.mean(axis=1, keepdims=True)
        xn = np.sqrt((RX * RX).sum(axis=1))
        boot[b] = (RX @ Reb) / (xn * eb_n)
        if (b + 1) % 1000 == 0:
            el = time.time() - tBt
            print(f"  bootstrap {b + 1}/{N_BOOT} {el:.0f}s eta "
                  f"{el / (b + 1) * (N_BOOT - b - 1):.0f}s", flush=True)
    T["boot"] = time.time() - tBt
    print(f"bootstrap: {N_BOOT} draws x {K} predictors in {T['boot']:.1f}s")

    ci_lo = np.empty(K); ci_hi = np.empty(K); b_p = np.empty(K)
    for k in range(K):
        ci_lo[k], ci_hi[k], b_p[k] = summarize(boot[:, k])

    # ---- F6 identity gate: 3 fixed pairs vs lib verbatim ------------------
    maxdiff = 0.0
    for (rt, rp) in [(0.10, 0), (0.25, 0), (0.0, 0)]:
        k = GRID.index(rt) * R + rp
        gdf = pd.DataFrame({"position": df["position"], "own_e_b": own_eb,
                            "Xsim": Xmat[k]})
        ref = position_cluster_bootstrap(gdf, "position", "Xsim", "own_e_b",
                                         n_boot=N_BOOT, seed=SEED)
        diffs = [abs(pre[k] - ref["observed_rho"]),
                 abs(ci_lo[k] - ref["ci_lo"]),
                 abs(ci_hi[k] - ref["ci_hi"]),
                 abs(b_p[k] - ref["p_boot"])]
        maxdiff = max(maxdiff, *diffs)
        print(f"G-lib rho={rt:.2f} rep={rp}: engine obs={pre[k]:+.12f} "
              f"CI=[{ci_lo[k]:+.12f},{ci_hi[k]:+.12f}] p={b_p[k]:.6f} | "
              f"lib obs={ref['observed_rho']:+.12f} "
              f"CI=[{ref['ci_lo']:+.12f},{ref['ci_hi']:+.12f}] "
              f"p={ref['p_boot']:.6f} | max|diff|={max(diffs):.3e}")
    print(f"G-lib overall max|diff| = {maxdiff:.3e} (threshold 1e-9) -> "
          f"{'PASS' if maxdiff < 1e-9 else 'FAIL'}")
    if maxdiff >= 1e-9:
        print("*** shared-draw engine does not reproduce lib - FAIL (AGENTS 4). ***")
        sys.exit(1)

    # ---- verdicts: F4 calibration, F7 floor --------------------------------
    det_sf = sf_p < 0.05
    det_bt = (ci_lo > 0) | (ci_hi < 0)
    print("\n" + "=" * 74)
    print("POWER TABLE (primary test = script-33 sign-flip; secondary = bootstrap CI)")
    print("=" * 74)
    summary = []
    for i_rt, rt in enumerate(GRID):
        sl = slice(i_rt * R, (i_rt + 1) * R)
        pw_sf = float(det_sf[sl].mean())
        pw_bt = float(det_bt[sl].mean())
        half = float(np.mean((ci_hi[sl] - ci_lo[sl]) / 2))
        tag = " (CALIBRATION)" if rt == 0.0 else ""
        print(f"  rho_true={rt:.2f}{tag}: power_signflip={pw_sf:.2f} "
              f"power_boot={pw_bt:.2f} achieved={obs[sl].mean():+.4f} "
              f"mean_CI_halfwidth={half:.4f}")
        summary.append({"rt": rt, "pw_sf": pw_sf, "pw_bt": pw_bt,
                        "ach": obs[sl].mean(), "ach_sd": obs[sl].std(),
                        "half": half})

    cal = summary[0]
    cal_ok = cal["pw_sf"] <= CAL_MAX
    print(f"\nF4 calibration at rho=0: sign-flip rejection "
          f"{cal['pw_sf']:.2f} of R={R} (ceiling {CAL_MAX}, nominal 0.05) -> "
          f"{'PASS' if cal_ok else 'FAIL (machinery broken)'}")
    signed_means = np.array([sf_mean[k] for k in range(len(pairs))])
    print(f"F6 sign-flip null centring across all {len(pairs)} predictors: "
          f"mean of null means={signed_means.mean():+.5f}, "
          f"mean null sd={np.mean(sf_sd):.4f} "
          f"({'centred' if abs(signed_means.mean()) < 0.01 else 'NOT centred - INVESTIGATE'})")
    if HARD_GATES and not cal_ok:
        print("*** F4 CALIBRATION FAIL - floor NOT quotable. ***")
        # still save the CSV (record), but task verdict is FAIL

    floor_rt = None
    for s in summary[1:]:
        if s["pw_sf"] >= 0.80:
            floor_rt = s["rt"]
            break
    if floor_rt is None:
        last = summary[-1]
        stmt = (f"we could NOT establish 80% power anywhere on the grid "
                f"(power={last['pw_sf']:.2f} even at rho={last['rt']:.2f}); "
                f"we observed -0.088")
    else:
        stmt = (f"we could have detected rho >= {floor_rt:.2f}; "
                f"we observed -0.088")
    print(f"\nAA4c statement: \"{stmt}\"")
    print(f"(grid resolution 0.05; R={R}; primary test = sign-flip; "
          f"calibration power at rho=0 = {cal['pw_sf']:.2f})")

    # ---- F8: save ----------------------------------------------------------
    rows = []
    for k, (rt, rp) in enumerate(pairs):
        rows.append({"level": "replicate", "rho_true": rt, "replicate": rp,
                     "obs_rho": obs[k], "boot_ci_lo": ci_lo[k],
                     "boot_ci_hi": ci_hi[k], "boot_p": b_p[k],
                     "detected_boot": bool(det_bt[k]), "signflip_p": sf_p[k],
                     "signflip_null_mean": sf_mean[k],
                     "signflip_null_sd": sf_sd[k],
                     "detected_signflip": bool(det_sf[k]),
                     "n": n, "n_positions": npos, "N_BOOT": N_BOOT,
                     "N_PERM": N_PERM, "R": R})
    for s in summary:
        rows.append({"level": "rho_summary", "rho_true": s["rt"],
                     "replicate": "all", "obs_rho": s["ach"],
                     "boot_ci_lo": np.nan, "boot_ci_hi": np.nan,
                     "boot_p": np.nan, "detected_boot": s["pw_bt"],
                     "signflip_p": s["pw_sf"], "signflip_null_mean": np.nan,
                     "signflip_null_sd": s["ach_sd"],
                     "detected_signflip": s["pw_sf"] >= 0.80,
                     "n": n, "n_positions": npos, "N_BOOT": N_BOOT,
                     "N_PERM": N_PERM, "R": R})
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nsaved {OUT} ({len(rows)} rows: {len(pairs)} replicate + "
          f"{len(summary)} summary)")

    print("\nLIMITATIONS: design-based power on the REAL own_e_b (injection is "
          "against the measured outcome - literal AA4a reading); floor "
          "resolution 0.05; R=50 -> power se ~5.7pp at 0.80; positive "
          "injection / two-sided tests; sign-flip flips share seed-0 but "
          "own rng stream vs script 33's interleaving (disclosed); p applies "
          "to own_e_b only; reuse of script 33's estimator is reproduction "
          "of machinery, not replication.")
    for kk, v in T.items():
        print(f"phase {kk}: {v:.1f}s")
    print(f"total {time.time() - t0:.1f}s")
    if HARD_GATES and not cal_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
