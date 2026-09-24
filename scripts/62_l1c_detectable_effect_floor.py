"""
Script 62 (I1 follow-up, task L1c): the detectable-effect-size floor of
I1's null test AS ACTUALLY CONSTRUCTED (script 49), at power 0.8.

This is the single most important number in the task doc: it decides
whether L2 (find a better comparator) is attempted or skipped.

WHAT THE TEST IS (script 49, unchanged)
---------------------------------------
Pooled Spearman rho(delta_ESM, e) over n=570 (variant, background) pairs
in 57 (site, variant) position-like clusters; one-sided POSITIVE
permutation gate, N_PERM=10000, alpha=0.05; the permutation null for
this dataset does NOT center on zero (mean +0.3880, sd 0.0532), so the
critical value sits high on the rho scale.

INPUTS AND WHERE EACH COMES FROM (nothing invented)
---------------------------------------------------
* rho_obs, null_mean, p_one, ci_lo, ci_hi, n, n_clusters: read from
  data/processed/task49_i1_gb1.csv (script 49's own output).
* null sd sigma0 = 0.0532: script 49's full-run stdout (it printed
  "mean=+0.3880 sd=0.0532"), pasted verbatim in
  docs/tasks/review-triage/OVERNIGHT_LOG.md entry "I1". The CSV did not
  store the sd, so it is a cited constant here; the script CROS-CHECKS
  it against the empirical p (gate (c) below) before using it.
* z quantiles: scipy norm.isf/cdf.

CALCULATION (shown step by step in the output)
----------------------------------------------
1. crit        = null_mean + z(1-alpha) * sigma0        [Gaussian null]
2. se(rho_hat) = (ci_hi - ci_lo) / (2 * z(0.975))       [position-cluster
   bootstrap percentile CI width -> sd; respects the 57 clusters, AGENTS 3]
3. floor       = crit + z(0.80) * se                    [smallest TRUE
   pooled rho for which the pre-registered gate rejects with prob >= 0.8]
4. power at the observed effect size = 1 - Phi((crit - rho_obs)/se)
Sensitivities printed: row-level Fisher se = 1/sqrt(n-3) (ignores
clustering, labeled anti-conservative); sigma0 recalibrated from the
empirical p_one (removes reliance on the Gaussian-null sd for the crit).

SANITY GATES (sys.exit(1), AGENTS 4)
------------------------------------
(a) round-trip: (crit - null_mean)/sigma0 == z(1-alpha) to 1e-9.
(b) power round-trip: feeding `floor` back through the power function
    returns 0.80 to 1e-9.
(c) null-model consistency: p implied by (rho_obs - null_mean)/sigma0
    under the Gaussian null must agree with the EMPIRICAL permutation
    p from the CSV to within 0.01 (draw noise at N_PERM=10000). If not,
    the Gaussian-null approximation is unusable and the floor number
    would be fiction -> exit 1, report FAIL (do not raise N, do not
    tweak; troubleshooting rule 2 for this session).
(d) gate consistency: rho_obs < crit must agree with the CSV's
    gate_pass=0 / p_one > 0.05.

PRE-REGISTERED DECISION RULE (fixed before running; AGENTS 6)
-------------------------------------------------------------
The comparator's known effect size is quoted in ln-fitness units from
L1a (epsilon = +5 / -4.5; range +/-7.5), but THIS test's effect-size
scale is rho: the paper publishes no delta-vs-epsilon association, so no
published rho exists. The only unit-consistent instantiation of "the
comparator's known effect size" for this test is its REALIZED estimate,
rho_obs, with its cluster-bootstrap CI (assumption logged, rule 6 of the
session instructions). Rule:
  * rho_obs < floor  -> COMPARATOR-UNDERPOWERED for this test ->
    attempt L2 (CI straddle reported either way, not hidden).
  * rho_obs >= floor -> PIPELINE-SIDE (the test had power for an effect
    that large) -> skip L2, go to L3.
The L1a epsilon-scale magnitudes are printed alongside as context, with
an explicit statement that the two scales cannot be converted into each
other (rho depends on how delta couples to epsilon, not on |epsilon|
alone) -- that mismatch is disclosed, not papered over.

Limitations (also printed by the script, AGENTS 6): Gaussian-null
approximation for crit (empirical null sample not stored on disk; the
agreement gate (c) bounds the error); se(rho_hat) treated as constant
across alternatives (local-power approximation); power one-sided to
match the pre-registered gate; no claim about power for MTHFR-sized
effects follows from this GB1-design calculation.

Output: data/processed/task62_l1c_floor.csv
N_BOOT/N_PERM do not apply (this script resamples nothing; it reads the
frozen run's numbers).
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "data" / "processed" / "task49_i1_gb1.csv"
OUT_CSV = ROOT / "data" / "processed" / "task62_l1c_floor.csv"

ALPHA = 0.05            # pre-registered gate, one-sided positive
POWER = 0.80            # task requirement
SIGMA0 = 0.0532         # script 49 full-run stdout sd, via OVERNIGHT_LOG "I1"
L1A_EPS_POS = 5.0       # Wu 2016 Fig 3D (context only, not convertible)
L1A_EPS_NEG = -4.5      # Wu 2016 Fig 3D (context only, not convertible)


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def main():
    d = pd.read_csv(IN_CSV).set_index("quantity")["value"]
    rho = float(d["pooled_rho"])
    lo = float(d["ci_lo"])
    hi = float(d["ci_hi"])
    p_emp = float(d["p_one_sided"])
    mu0 = float(d["null_mean"])
    n = int(d["n_pairs"])
    n_cl = int(d["n_clusters"])
    gate_pass = int(d["gate_pass"])

    z_a = norm.isf(ALPHA)          # 1.6448536
    z_80 = norm.isf(1 - POWER)     # 0.8416212
    z_975 = norm.isf(0.025)        # 1.9599640

    print("=== inputs (sources cited in docstring) ===")
    print(f"rho_obs={rho:.7f}  ci=[{lo:.7f}, {hi:.7f}]  p_one_emp={p_emp:.6f}")
    print(f"null_mean={mu0:.7f}  sigma0={SIGMA0}  (script 49 stdout via "
          f"OVERNIGHT_LOG I1 entry)")
    print(f"n={n} pairs, {n_cl} (site,variant) position-like clusters, "
          f"gate: one-sided positive alpha={ALPHA}, gate_pass={gate_pass}")

    # ---- sanity gates (a)-(d) ----
    crit = mu0 + z_a * SIGMA0
    z_rt = (crit - mu0) / SIGMA0
    if abs(z_rt - z_a) > 1e-9:
        fail(f"round-trip z {z_rt} != {z_a}")
    p_gauss = norm.sf((rho - mu0) / SIGMA0)
    if abs(p_gauss - p_emp) > 0.01:
        fail(f"Gaussian-null p {p_gauss:.6f} disagrees with empirical "
             f"{p_emp:.6f} by > 0.01")
    if not ((rho < crit) == (gate_pass == 0) == (p_emp > ALPHA)):
        fail("crit/gate consistency broken")

    se_cluster = (hi - lo) / (2 * z_975)
    floor = crit + z_80 * se_cluster
    pwr_rt = norm.sf((crit - floor) / se_cluster)
    if abs(pwr_rt - POWER) > 1e-9:
        fail(f"power round-trip {pwr_rt} != {POWER}")
    print("\nsanity gates: (a) crit round-trip OK (1e-9), (b) power "
          f"round-trip OK (p={pwr_rt:.12f}), (c) Gaussian p={p_gauss:.6f} "
          f"vs empirical p={p_emp:.6f} |diff|={abs(p_gauss-p_emp):.6f} < 0.01, "
          f"(d) rho<crit={rho < crit} matches gate_pass=0 -- ALL PASS")

    # ---- the calculation, every step printed ----
    se_fisher_row = 1.0 / np.sqrt(n - 3)
    z_emp = norm.isf(p_emp)
    sigma0_emp = (rho - mu0) / z_emp
    crit_emp = mu0 + z_a * sigma0_emp
    floor_emp = crit_emp + z_80 * se_cluster
    floor_row = crit + z_80 * se_fisher_row
    power_obs = norm.sf((crit - rho) / se_cluster)

    print("\n=== step 1: critical value (Gaussian null) ===")
    print(f"crit = null_mean + z(1-{ALPHA}) * sigma0")
    print(f"     = {mu0:.7f} + {z_a:.7f} * {SIGMA0}")
    print(f"     = {mu0:.7f} + {z_a * SIGMA0:.7f} = {crit:.7f}")
    print(f"     (empirical-p-calibrated sigma0={sigma0_emp:.7f} -> "
          f"crit={crit_emp:.7f})")

    print("\n=== step 2: sampling sd of rho_hat (position-cluster) ===")
    print(f"se = (ci_hi - ci_lo) / (2*z_0.975) = ({hi:.7f} - {lo:.7f}) / "
          f"{2 * z_975:.7f} = {se_cluster:.7f}   [PRIMARY, cluster-based]")
    print(f"row-level Fisher 1/sqrt(n-3) = 1/sqrt({n - 3}) = "
          f"{se_fisher_row:.7f}   [sensitivity, ignores clustering -> "
          f"anti-conservative]")

    print("\n=== step 3: detectable-effect floor at power 0.8 ===")
    print(f"floor = crit + z(0.80) * se")
    print(f"      = {crit:.7f} + {z_80:.7f} * {se_cluster:.7f}")
    print(f"      = {crit:.7f} + {z_80 * se_cluster:.7f} = {floor:.7f}")
    print(f"sensitivities: row-level se -> floor={floor_row:.7f}; "
          f"sigma0 from empirical p -> floor={floor_emp:.7f}")
    print(f"same floor as excess-over-null: {floor - mu0:.7f} "
          f"(z95*sigma0 {z_a * SIGMA0:.7f} + z80*se {z_80 * se_cluster:.7f}); "
          f"observed excess = rho - null_mean = {rho - mu0:.7f}")

    print("\n=== step 4: power of this test AT the observed effect ===")
    print(f"power(rho_obs) = 1 - Phi((crit - rho_obs)/se) = "
          f"1 - Phi({(crit - rho) / se_cluster:.7f}) = {power_obs:.7f}")

    # ---- comparison + pre-registered verdict ----
    below = bool(rho < floor)
    straddle = bool(lo < floor < hi)
    print("\n=== comparator's known effect size vs floor ===")
    print(f"test-scale (rho): known/realized effect rho_obs = {rho:.7f} "
          f"CI [{lo:.7f}, {hi:.7f}]  vs  floor = {floor:.7f}  -> "
          f"{'BELOW floor' if below else 'ABOVE floor'}"
          f"  (CI {'STRADDLES' if straddle else 'does not straddle'} floor)")
    print(f"L1a scale (ln-fitness, from Wu 2016 Fig 3D): epsilon = "
          f"{L1A_EPS_POS:+.1f} / {L1A_EPS_NEG:+.1f}, heat-map range "
          f"[-7.5, +7.5] -- NOT convertible to rho (no published "
          f"delta-epsilon association exists); printed as context only")

    if below:
        verdict = (f"COMPARATOR-UNDERPOWERED for this test: the comparator's "
                   f"known effect in test units (rho {rho:.4f}) sits BELOW the "
                   f"detectable floor ({floor:.4f}); this gate had only "
                   f"{power_obs:.1%} power at that effect -> ATTEMPT L2 "
                   f"(per task doc). CI upper bound {hi:.4f} exceeds the "
                   f"floor, so the straddle is disclosed alongside.")
    else:
        verdict = (f"PIPELINE-SIDE: known effect {rho:.4f} >= floor "
                   f"{floor:.4f} -> the test had power for an effect that "
                   f"large -> SKIP L2, go to L3")
    print(f"\nL1c VERDICT (pre-registered rule): {verdict}")

    print("\nLIMITATIONS (printed by the script, AGENTS 6):")
    print("  - crit uses a Gaussian null; empirical null sample not stored.")
    print("    Gate (c) bounds the error at |dp| < 0.01 vs the real p.")
    print("  - se(rho_hat) from the frozen run's percentile CI width is a")
    print("    local-power approximation (se treated as constant).")
    print("  - Unit bridge: the comparator's 'known effect size' is taken as")
    print("    its realized rho because the source paper's epsilon scale has")
    print("    no mapping to rho; assumption logged in the log entry.")
    print("  - This calibrates power for the GB1 design (570 pairs, 57")
    print("    clusters, null mean +0.388). It says nothing direct about")
    print("    power on MTHFR's own effect scale.")

    out = pd.DataFrame([
        {"quantity": "rho_obs", "value": rho},
        {"quantity": "null_mean", "value": mu0},
        {"quantity": "sigma0", "value": SIGMA0},
        {"quantity": "crit", "value": crit},
        {"quantity": "se_cluster", "value": se_cluster},
        {"quantity": "se_fisher_row", "value": se_fisher_row},
        {"quantity": "floor_primary", "value": floor},
        {"quantity": "floor_row_sens", "value": floor_row},
        {"quantity": "floor_sigma0emp_sens", "value": floor_emp},
        {"quantity": "power_at_observed", "value": power_obs},
        {"quantity": "p_gauss_vs_emp_diff", "value": abs(p_gauss - p_emp)},
        {"quantity": "known_below_floor", "value": int(below)},
        {"quantity": "ci_straddles_floor", "value": int(straddle)},
        {"quantity": "excess_floor", "value": floor - mu0},
        {"quantity": "excess_observed", "value": rho - mu0},
    ])
    out.to_csv(OUT_CSV, index=False)
    print(f"\nSaved to {OUT_CSV}")


if __name__ == "__main__":
    main()
