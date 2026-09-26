"""
Task B4 (reliability-and-decompositions): de-bias AD4's interaction
term for its distance-independent offset and re-test against own_e_b.
  B4a — residualize interaction_D on ca_dist_222, re-test
  B4b — the pre-registered verdict (null confirmed vs restated)
  B4c — the >10 A proportion as a standalone fact + Nambiar 2.4 link

PRE-REGISTRATION (written before any number below existed; AGENTS s0/s6)

CONTEXT (AD4's own logged results, DEEPDIVE_LOG L2327-2336, cited not
  recomputed-from-memory):
  PRIMARY rho(interaction_D, own_e_b) = +0.0154 [-0.0166, +0.0465]
      p_boot=0.3406 n=9595 clusters=586  (the NULL under test)
  (b) rho(interaction_D, Ca-dist 222) = +0.0246 | near<=10A n=363
      rho=-0.0250 | far>10A n=9232 rho=+0.0146
  offset: interaction_D mean=-1.31853 sd=0.37904 (B4a's premise: a
      large, mostly distance-independent offset)

FRAME (frozen): data/processed/task77_thermompnnD_doubles.csv rows with
  own_e_b non-null -> 9,595 rows / 586 positions (AD4's own analysis
  set t = v2[own_e_b.notna()], script 77 L432).

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 frame: exactly 9,595 / 586, interaction_D and ca_dist_222 finite
     on every analysis row.
  G2 AD4 reproduction: recomputed rho(interaction_D, own_e_b) matches
     +0.0154 within 5e-4 AND recomputed mean(interaction_D) matches
     -1.31853 within 5e-4 (4-dp rounding tolerance, house convention).
  G3 B4c claim check: counts beyond 10 A must be exactly 9,232 with
     363 within (AD4's logged (b) counts AND the task doc's claimed
     9,232/9,595 — checked, not assumed; mismatch -> STOP, since B4c's
     claim would then be false as stated).

B4a — the de-biasing (literal task spec):
  OLS with intercept: interaction_D = a + b * ca_dist_222 + e on the
  9,595 rows (LINEAR residualization, exactly as the task words it —
  "regress X on ca_dist_222, take the residuals"; no polynomial, no
  binning, no alternative functional form is tried after seeing this).
  Residuals are computed ONCE and then treated as the residualized
  variable, exactly the way AD4 treats interaction_D itself as given;
  the position-cluster bootstrap therefore resamples pairs of
  (resid, own_e_b) — disclosed as the same convention, not a
  re-derivation-per-draw design.
  PRIMARY: position_cluster_bootstrap(t, position, resid_D, own_e_b,
  N_BOOT, seed 0) — AD4's exact convention. Companion:
  position_shuffle_test(t, resid_D, own_e_b, N_PERM, seed 1) — AD4's
  exact position-level association null (identity check internal to
  lib). Effect sizes printed: R^2 of the de-biasing regression (how
  much of interaction_D's variance distance explains at all), resid
  mean/sd, and the descriptive rho(interaction_D, ca_dist_222) on this
  frame (AD4's (b) recomputed as context).
  ENV: N_BOOT/N_PERM default 10000/10000; SMOKE=1 -> 300/300.

B4b — FROZEN VERDICT RULE (from the task's own wording):
    residual rho 95% CI excludes 0 (either sign)
        -> "A REAL RELATIONSHIP EMERGES AFTER DE-BIASING" and AD4's
           original null must be restated as a
           comparator-calibration failure, not a genuine absence.
    residual rho 95% CI includes 0
        -> "AD4's NULL IS CONFIRMED AS REAL, not an artifact of the
           offset."
  Nothing else can fire. Magnitude always reported alongside.

B4c — report the proportion beyond 10 A from G3's verified counts
  (9,232/9,595) as a STANDALONE FACT in the script's printed output,
  and print the required connection to Nambiar Section 2.4 as
  characterized by the task doc (L213-220) — labeled as that source's
  verified characterization, not re-fetched here: "raw, uncalibrated
  PLM epistasis tracks structural contact proximity; only their
  calibrated epistasis reveals long-range functional coupling." The
  connection statement itself (pre-registered here): if ~96% of the
  frame is beyond 10 A, MTHFR/A222V is overwhelmingly a long-range
  system, so this project's comparators (ESM-2's raw scores and
  ThermoMPNN's stability term) may be instruments better suited to
  short-range structural coupling than to the regime the question
  actually sits in — offered as an interpretation, not a tested claim
  (no new test is claimed for it).

LIMITATIONS (printed with results, AGENTS s6):
  - Linear residualization only: a nonlinear distance dependence would
    remain. (AD4's own (b) says the LINEAR rank association with
    distance is +0.0246 — tiny — which is why the linear form is the
    task's literal one; this is stated, not assumed away.)
  - Residualizing a variable whose rank correlation with the covariate
    is ~0.02 changes little by construction; a null here is therefore
    the EXPECTED outcome and is reported as confirmation only in the
    weak sense the rule allows.
  - Observational: nothing about mechanism follows from the residual
    correlation.
  - The 96% fact describes THIS frame's distance composition only.

Run:  SMOKE=1 venv/bin/python3 scripts/96_b4_debias_interaction.py
      full: venv/bin/python3 scripts/96_b4_debias_interaction.py
Output: data/processed/task96_b4_debias.csv
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

from scripts.lib.stats import position_cluster_bootstrap
from scripts.lib.position_null import position_shuffle_test

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SMOKE = os.environ.get("SMOKE", "") == "1"
if SMOKE:
    N_BOOT = min(N_BOOT, 300)
    N_PERM = min(N_PERM, 300)
SEED_BOOT, SEED_PERM = 0, 1

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "task77_thermompnnD_doubles.csv"
OUT = ROOT / "data" / "processed" / "task96_b4_debias.csv"

REC_RHO, REC_MEAN = 0.0154, -1.31853
TOL = 5e-4
EXPECT_N, EXPECT_POS = 9595, 586
EXPECT_FAR, EXPECT_NEAR = 9232, 363


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def main():
    log(f"B4 -- DE-BIAS interaction_D on ca_dist_222 + re-test "
        f"(scripts/96) {'SMOKE ' if SMOKE else ''}N_BOOT={N_BOOT} "
        f"N_PERM={N_PERM}")
    log("pre-registered: linear OLS residuals (literal task wording), "
        "residuals computed once (AD4's given-variable convention), "
        "frozen B4b verdict rule (CI excludes/includes 0)")

    d = pd.read_csv(CSV)
    t = d[d["own_e_b"].notna()].copy()
    if (len(t), t["position"].nunique()) != (EXPECT_N, EXPECT_POS):
        gfail(f"G1 FAIL: frame {len(t)}/{t['position'].nunique()} != "
              f"{EXPECT_N}/{EXPECT_POS}")
    if not (np.isfinite(t["interaction_D"]).all()
            and np.isfinite(t["ca_dist_222"]).all()):
        gfail("G1 FAIL: interaction_D or ca_dist_222 non-finite on "
              "analysis rows")
    log(f"G1 frame PASS: n={len(t)} / {t['position'].nunique()} "
        f"positions, interaction_D and ca_dist_222 finite everywhere")

    rho_raw = float(spearmanr(t["interaction_D"],
                              t["own_e_b"]).statistic)
    mean_i = float(t["interaction_D"].mean())
    d_rho, d_mean = abs(rho_raw - REC_RHO), abs(mean_i - REC_MEAN)
    log(f"G2 AD4 reproduction: rho(interaction_D, own_e_b) "
        f"{rho_raw:+.6f} vs record {REC_RHO:+.4f} (|diff|={d_rho:.2e}); "
        f"mean {mean_i:+.6f} vs record {REC_MEAN:+.5f} "
        f"(|diff|={d_mean:.2e}) -> "
        f"{'OK' if max(d_rho, d_mean) < TOL else 'FAIL'}")
    if max(d_rho, d_mean) >= TOL:
        gfail("G2 FAIL -- cannot reproduce AD4's logged primary/offset")

    n_far = int((t["ca_dist_222"] > 10.0).sum())
    n_near = len(t) - n_far
    if (n_far, n_near) != (EXPECT_FAR, EXPECT_NEAR):
        gfail(f"G3 FAIL: >10A {n_far} / <=10A {n_near} != "
              f"{EXPECT_FAR}/{EXPECT_NEAR} — the task's 9,232/9,595 "
              f"claim does not hold as stated; STOP before B4c.")
    pct = n_far / len(t) * 100
    log(f"G3 B4c claim check PASS: >10 A = {n_far}/{len(t)} "
        f"({pct:.2f}%), <=10 A = {n_near} — matches both AD4's logged "
        f"(b) counts and the task's claimed 9,232/9,595 (~96%)")

    # ---- B4a: the de-biasing ----
    log("\n" + "=" * 74)
    log("B4a  interaction_D ~ ca_dist_222 (linear OLS), residuals "
        "re-tested vs own_e_b (AD4's exact conventions)")
    log("=" * 74)
    X = sm.add_constant(t["ca_dist_222"].to_numpy(float))
    reg = sm.OLS(t["interaction_D"].to_numpy(float), X).fit()
    resid = t["interaction_D"].to_numpy(float) - reg.fittedvalues
    r2 = float(reg.rsquared)
    rho_dist = float(spearmanr(t["interaction_D"],
                               t["ca_dist_222"]).statistic)
    log(f"  de-biasing regression: interaction_D ~ ca_dist_222, "
        f"slope b = {reg.params[1]:+.6f} A^-1, R^2 = {r2:.6f} "
        f"(distance explains {r2:.4%} of the offset term's variance)")
    log(f"  residuals: mean = {resid.mean():+.2e} (OLS), "
        f"sd = {resid.std(ddof=0):.6f} (original sd "
        f"{t['interaction_D'].std(ddof=0):.6f})")
    log(f"  context (AD4's (b) recomputed): rho(interaction_D, "
        f"ca_dist_222) = {rho_dist:+.4f}")
    t = t.assign(resid_D=resid)

    cb = position_cluster_bootstrap(t, "position", "resid_D", "own_e_b",
                                    n_boot=N_BOOT, seed=SEED_BOOT)
    rho_res = float(cb["observed_rho"])
    lo, hi, p_b = float(cb["ci_lo"]), float(cb["ci_hi"]), float(cb["p_boot"])
    log(f"  PRIMARY rho(resid_D, own_e_b) = {rho_res:+.4f} "
        f"[{lo:+.4f}, {hi:+.4f}] p_boot={p_b:.4f} n={cb['n_rows']} "
        f"clusters={cb['n_clusters']}")
    sh = position_shuffle_test(t, "resid_D", "own_e_b", N_PERM,
                               SEED_PERM)
    log(f"  POSITION-LEVEL association null: rho_pos={sh[0]:+.4f} "
        f"p={sh[1]:.4f} (N_PERM={N_PERM}, positions={sh[2]}, identity "
        f"check PASS)")
    log(f"  vs ORIGINAL AD4: rho {REC_RHO:+.4f} "
        f"[-0.0166, +0.0465] -> de-biased {rho_res:+.4f} "
        f"[{lo:+.4f}, {hi:+.4f}] (delta {rho_res - REC_RHO:+.4f})")

    # ---- B4b: frozen verdict ----
    log("\n" + "=" * 74)
    log("B4b  VERDICT (frozen: CI excludes/includes 0)")
    log("=" * 74)
    emerges = not (lo <= 0 <= hi)
    if emerges:
        verdict = ("A REAL RELATIONSHIP EMERGES AFTER DE-BIASING "
                   f"(resid rho {rho_res:+.4f}, CI [{lo:+.4f}, "
                   f"{hi:+.4f}] excludes 0) -> AD4's original null must "
                   "be RESTATED as a comparator-calibration failure, "
                   "not a genuine absence of signal.")
    else:
        verdict = (f"AD4's NULL IS CONFIRMED AS REAL, not an artifact "
                   f"of the offset: the de-biased residual rho "
                   f"{rho_res:+.4f} [{lo:+.4f}, {hi:+.4f}] still "
                   f"includes 0 (p_boot={p_b:.4f}). Removing the "
                   f"distance-independent offset (itself {r2:.4%} "
                   f"distance-explained) changes the association by "
                   f"{rho_res - REC_RHO:+.4f}.")
    log(f"  {verdict}")

    # ---- B4c: standalone fact + connection ----
    log("\n" + "=" * 74)
    log("B4c  THE >10 A PROPORTION (standalone fact) + Nambiar 2.4 link")
    log("=" * 74)
    log(f"  STANDALONE FACT: {n_far} of {len(t)} analysis-frame variants "
        f"({pct:.2f}%) sit BEYOND 10 A from position 222's C-alpha; "
        f"only {n_near} ({100 - pct:.2f}%) are within 10 A. MTHFR/"
        f"A222V is overwhelmingly a long-range system.")
    log("  Connection required by the task (task doc L213-220, "
        "Nambiar Section 2.4 as VERIFIED by the external analysis — "
        "quoted, not re-fetched): 'raw, uncalibrated PLM epistasis "
        "tracks structural contact proximity; only their calibrated "
        "epistasis reveals long-range functional coupling.'")
    log("  Interpretation (pre-registered as this task's own "
        "connection, offered as interpretation — no new test claimed): "
        f"with ~{pct:.0f}% of the frame beyond 10 A, this project's "
        "comparators (ESM-2's raw scores and ThermoMPNN's stability "
        "term) may be instruments better suited to short-range "
        "structural coupling than to the long-range regime MTHFR/"
        "A222V actually sits in — a candidate unifying reading of "
        "B1/B2/B4/A2, held as a hypothesis.")

    out = pd.DataFrame([
        dict(statistic="frame_n", value=len(t)),
        dict(statistic="frame_positions", value=int(t["position"].nunique())),
        dict(statistic="rho_interaction_raw", value=rho_raw),
        dict(statistic="mean_interaction_offset", value=mean_i),
        dict(statistic="debias_slope_per_A", value=float(reg.params[1])),
        dict(statistic="debias_R2", value=r2),
        dict(statistic="rho_interaction_vs_dist", value=rho_dist),
        dict(statistic="rho_resid_vs_own_e_b", value=rho_res),
        dict(statistic="ci_lo", value=lo),
        dict(statistic="ci_hi", value=hi),
        dict(statistic="p_boot", value=p_b),
        dict(statistic="n_beyond_10A", value=n_far),
        dict(statistic="pct_beyond_10A", value=pct),
    ])
    out.to_csv(OUT, index=False)
    log(f"\n[saved] {OUT}")
    log("\nLIMITATIONS: linear residualization only (nonlinear distance "
        "dependence would remain; AD4's (b) linear rho with distance is "
        "+0.0246, which is why the linear form is the literal task "
        "wording); rank correlation with the covariate is ~0.02 so a "
        "near-null residual result is the EXPECTED outcome — reported as "
        "the rule allows, not as strong evidence of absence; "
        "observational, no mechanism; the 96% fact describes this "
        "frame's distance composition only.")
    log("SCRIPT 96 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
