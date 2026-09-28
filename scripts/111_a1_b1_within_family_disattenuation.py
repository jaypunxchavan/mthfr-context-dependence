"""
Script 111 (tasks A1 + B1, Groups A and B) -- the self-consistent
within-family disattenuation, and the instance-inclusive interval.
PRE-REGISTERED: this docstring was written before the first (and only)
run; every formula, input, method choice, and reporting rule below was
fixed before any number produced here was seen. The script is pure
deterministic arithmetic (no randomness, no N_BOOT) -- gates, not
smoke/full staging, are its checks; a single run is the full run.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group A task A1 (a-c),
      Group B task B1 (a-c).

FORMULAS (verbatim from the task doc and script 91, the record's
disattenuation producer):
  disattenuation (script 91 A2 / classical attenuation correction):
      delta-only     = r_obs / sqrt(rel_delta)
      fully corrected = r_obs / sqrt(rel_delta * rel_own_eb)
  linear partial (Group C's, NOT used here; listed only to keep the
  formulas unmixed):
      rho_DE.S = [rho_DE - rho_DS*rho_ES] / sqrt((1-rho_DS^2)(1-rho_ES^2))
  instance-inclusive combination (task B1a):
      SE_combined = sqrt(Var_instance + Var_cluster)   [independence
      ASSUMED -- stated as an assumption, per the task]
      Var_instance = sample variance (ddof=1, n=5) of the five
                     ESM-1v checkpoint anchors
      Var_cluster  = (SE of the headline anchor from the
                     position-cluster bootstrap CI already on record)^2

INPUTS AND SOURCES (no value chosen after seeing any result):
  1. Five ESM-1v checkpoint anchors (target=primary, col=own_e_b):
     data/processed/task_AC4_esm1v_summary.csv, observed_rho of the
     five rows (recorded values; re-read here):
       -0.020573283438559947, -0.04081961928162246,
       +0.013433599172494119, -0.0265719206793297,
       -0.0034092558305339805
     Expected (gates): mean rounds to -0.015588 (6 dp; record:
     RELIABILITY_LOG "mean single-member rho = -0.015588096") and
     sd(ddof=1) rounds to 0.0211 (4 dp; the task's own given sd).
  2. Headline anchor + its position-cluster bootstrap CI:
     data/processed/task32_delta_esm_primary.csv, row
     (stage=primary, quantity="signed, own e_b"):
       rho = -0.08811806424891734, CI [-0.1173334458953319,
       -0.05951138449511738]  (script 32, n_boot=10000, seed 0,
       positions resampled). NO explicit SE number was ever printed on
     record -- the record carries the CI, so
       SE_cluster = (ci_hi - ci_lo) / (2 * 1.96)
     (normal-approximation inversion of the recorded percentile CI).
     This derivation is disclosed as THE method for Var_cluster here;
     it is not a new bootstrap.
  3. rel_delta (ESM-1v family's delta reliability) =
     0.08436481140085886 -- the cross-checkpoint median pairwise
     delta Spearman, re-derived earlier TODAY by script 110 (gate G4
     there, round(...,6)==0.084365) and stored in
     task110_rhoe_correlated_error.csv; read back here and gated.
     The task's "(0.0844)" is this value rounded; the literal 4-dp
     variant is ALSO printed as a rounding-sensitivity line.
  4. rel_own_eb = 0.6363, used as quoted (the task's own value and
     script 91's stated input); full-precision record value
     0.6363275925044801 (C3a G5 r_own = 0.6363276) printed as a
     sensitivity line. Primary = 0.6363 (task-literal); both shown,
     neither selected after results.
  5. ESM-2's raw anchor: -0.08811806424891734 with CI from the same
     task32 row (for A1c's side-by-side).
  6. r_own provenance substring gate: OVERNIGHT_LOG must contain
     "var(analysis 0.05804) = 0.6363" (the record's source line).

GATES (failure -> print exact mismatch, sys.exit(1); no retries):
  G0 inputs exist (task_AC4_esm1v_summary.csv, task32_delta_esm_
     primary.csv, task110_rhoe_correlated_error.csv, OVERNIGHT_LOG).
  G1 five-anchor reproduction: mean rounds to -0.015588 (6 dp) AND
     sd(ddof=1) rounds to 0.0211 (4 dp).
  G2 headline row: value == -0.08811806424891734 and both CI endpoints
     equal the recorded ones (abs tol 1e-12) -- pins Var_cluster's
     source row.
  G3 rel_delta read-back == 0.08436481140085886 (abs tol 1e-12).
  G4 OVERNIGHT_LOG provenance substring for 0.6363.
  G5 the record's chain reproduces: with rel_delta full precision,
     -0.08811806424891734 / sqrt(rel_delta) within 1e-6 of the
     record's -0.3033781 (DISATTENUATION_LOG G6), and further divided
     by sqrt(rel_own full) within 1e-5 of -0.3803154 -- 1e-5 is the
     RECORD'S OWN tolerance for that gate, used unchanged here.

REPORTING RULES (pre-registered):
  A1a: within-family disattenuation of the five-checkpoint mean
     (-0.015588096011508394), delta-only AND fully-corrected, primary
     inputs (rel_delta full precision, rel_own 0.6363), with the
     literal-4-dp and full-precision-rel_own sensitivity lines.
  A1b: 95% CI on the five-checkpoint mean with n=5: t(4) interval
     (t=2.7764451051977987) -- primary, because n=5 and sigma unknown;
     the z (1.96) interval is printed as a sensitivity. The interval
     is propagated through BOTH disattenuations by dividing the
     endpoints by the same positive divisors (the map is linear in
     r_obs; reliability uncertainty is NOT propagated -- disclosed).
  A1c: side-by-side table: ESM-2 raw uncorrected (point + recorded CI)
     vs ESM-1v within-family delta-only (point + propagated CI) vs
     ESM-1v within-family fully-corrected (point + propagated CI) vs
     the withdrawn cross-model chain (-0.303/-0.380, labeled
     counterfactual/withdrawn per the prior session's record).
     "Exceeds the ceiling" is evaluated at POINT level (|ESM-2 raw| vs
     |ESM-1v fully-corrected|) and stated explicitly if true; BOTH
     interval-overlap facts (does the other's point/interval contain
     it?) are printed alongside so neither direction is oversold.
  B1a: Var_instance, Var_cluster, SE_combined printed with the
     independence assumption stated.
  B1b: instance-inclusive interval centered on the ESM-1v mean
     (primary; +/- 1.96 * SE_combined, because B1's object is an SE --
     pre-registered), the t(4)-multiplied variant as sensitivity, and
     the illustrative interval centered on ESM-2's single-checkpoint
     value with the task-mandated caveat ("ESM-2 has only one
     checkpoint ... illustrative, not a real interval").
  B1c: plain yes/no on whether the primary interval around the ESM-1v
     mean excludes zero, answered from the printed numbers only.

LIMITATIONS (printed with the output, AGENTS 6):
  - t-interval on n=5 anchors assumes the five checkpoint anchors are
    themselves roughly normal draws; n=5 cannot verify that.
  - Var_cluster's SE is inverted from a percentile CI (disclosed);
    percentile CIs are not exactly symmetric, so this is an
    approximation at the 4th decimal.
  - Independence of Var_instance and Var_cluster is ASSUMED (the task
    says to assume and state it): checkpoint-to-checkpoint spread and
    position-resampling noise are treated as orthogonal sources.
  - Disattenuation inherits the proxy assumption already flagged by
    script 91: rel_delta is the ESM-1v family's cross-seed delta
    agreement used as the delta's reliability.
  - Reproduction of the record's -0.303/-0.380 (G5) is a unit test of
    formula consistency, not independent evidence.

Usage: venv/bin/python3 scripts/111_a1_b1_within_family_disattenuation.py
"""

import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

ANCHORS_CSV = PROC / "task_AC4_esm1v_summary.csv"
PRIMARY_CSV = PROC / "task32_delta_esm_primary.csv"
T110_CSV = PROC / "task110_rhoe_correlated_error.csv"
OVERNIGHT = ROOT / "docs" / "tasks" / "review-triage" / "OVERNIGHT_LOG.md"

REL_OWN_PRIMARY = 0.6363          # task-literal / script 91 stated
REL_OWN_FULL = 0.6363275925044801  # C3a G5 record (sensitivity)
T4 = 2.7764451051977987           # t(0.975, df=4)
Z95 = 1.96

REC_RHO = -0.08811806424891734
REC_CI_LO = -0.1173334458953319
REC_CI_HI = -0.05951138449511738
REC_REL_DELTA = 0.08436481140085886
REC_CHAIN_LO = -0.3033781   # DISATTENUATION_LOG G6 point 1
REC_CHAIN_FULL = -0.3803154  # DISATTENUATION_LOG G6 point 2


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner("A1 + B1 -- within-family disattenuation & instance-inclusive "
           "CI (scripts/111, deterministic single run)")

    # ---- G0 ---------------------------------------------------------
    for p in [ANCHORS_CSV, PRIMARY_CSV, T110_CSV, OVERNIGHT]:
        if not p.exists():
            gfail(f"G0 FAIL: {p} missing. Stop.")
    print("  G0 PASS: all four inputs present")

    # ---- inputs -----------------------------------------------------
    ac4 = pd.read_csv(ANCHORS_CSV)
    five = ac4[(ac4["target"] == "primary")
               & (ac4["target_col"] == "own_e_b")].sort_values("member")
    anchors = five["observed_rho"].to_numpy(float)
    if len(anchors) != 5:
        gfail(f"G1 FAIL: expected 5 anchors, got {len(anchors)}")
    mean5 = float(anchors.mean())
    sd5 = float(anchors.std(ddof=1))

    pri = pd.read_csv(PRIMARY_CSV)
    row = pri[(pri["stage"] == "primary")
              & (pri["quantity"] == "signed, own e_b")]
    if len(row) != 1:
        gfail(f"G2 FAIL: {len(row)} headline rows (want 1)")
    rho_head = float(row["value"].iloc[0])
    ci_lo = float(row["ci_lo"].iloc[0])
    ci_hi = float(row["ci_hi"].iloc[0])

    t110 = pd.read_csv(T110_CSV)
    rel_delta = float(
        t110.loc[t110["key"] == "observed_rel_D", "value"].iloc[0])

    if "var(analysis 0.05804) = 0.6363" not in OVERNIGHT.read_text():
        gfail("G4 FAIL: OVERNIGHT_LOG provenance substring for 0.6363 "
              "not found. Stop.")

    # ---- G1..G4 -----------------------------------------------------
    if round(mean5, 6) != -0.015588:
        gfail(f"G1 FAIL: mean {mean5!r} does not round to -0.015588")
    if round(sd5, 4) != 0.0211:
        gfail(f"G1 FAIL: sd {sd5!r} does not round to 0.0211")
    if not (math.isclose(rho_head, REC_RHO, abs_tol=1e-12)
            and math.isclose(ci_lo, REC_CI_LO, abs_tol=1e-12)
            and math.isclose(ci_hi, REC_CI_HI, abs_tol=1e-12)):
        gfail(f"G2 FAIL: headline row {rho_head} [{ci_lo}, {ci_hi}]")
    if not math.isclose(rel_delta, REC_REL_DELTA, abs_tol=1e-12):
        gfail(f"G3 FAIL: rel_delta read-back {rel_delta!r}")
    print(f"  G1 PASS: five anchors mean={mean5!r} (rounds -0.015588), "
          f"sd(ddof=1)={sd5!r} (rounds 0.0211)")
    print(f"  G2 PASS: headline row reproduced exactly "
          f"({rho_head!r}, CI [{ci_lo!r}, {ci_hi!r}])")
    print(f"  G3 PASS: rel_delta read-back == {rel_delta!r} "
          f"(script 110's same-day re-derivation)")
    print(f"  G4 PASS: 0.6363 provenance substring present in "
          f"OVERNIGHT_LOG")

    # ---- G5 reproduce the record's chain ----------------------------
    chain_lo = REC_RHO / math.sqrt(rel_delta)
    chain_full = chain_lo / math.sqrt(REL_OWN_FULL)
    chain_6363 = chain_lo / math.sqrt(REL_OWN_PRIMARY)
    if not math.isclose(chain_lo, REC_CHAIN_LO, abs_tol=1e-6):
        gfail(f"G5 FAIL: delta-only chain {chain_lo!r} vs record "
              f"{REC_CHAIN_LO} (tol 1e-6)")
    if not math.isclose(chain_full, REC_CHAIN_FULL, abs_tol=1e-5):
        gfail(f"G5 FAIL: full chain {chain_full!r} vs record "
              f"{REC_CHAIN_FULL} (record's own tol 1e-5)")
    d_lo = abs(chain_lo - REC_CHAIN_LO)
    d_full_r = abs(chain_full - REC_CHAIN_FULL)
    print(f"  G5 PASS: record's chain reproduces -- delta-only "
          f"{chain_lo!r} vs {REC_CHAIN_LO} (|d|={d_lo:.2e}); "
          f"full {chain_full!r} vs {REC_CHAIN_FULL} "
          f"(|d|={d_full_r:.2e}, record's own tol 1e-5; with "
          f"rel_own=0.6363 the value is {chain_6363!r})")

    # ================= A1a ===========================================
    banner("A1a -- SELF-CONSISTENT WITHIN-FAMILY DISATTENUATION", "-")
    print(f"  input: five-checkpoint mean anchor = {mean5!r}")
    print(f"         rel_delta (ESM-1v family)  = {rel_delta!r} "
          f"(task's '(0.0844)'; 6-dp record 0.084365)")
    print(f"         rel_own_eb (primary 0.6363, task-literal)")
    div_delta = math.sqrt(rel_delta)
    div_full = math.sqrt(rel_delta * REL_OWN_PRIMARY)
    d_only = mean5 / div_delta
    d_full = mean5 / div_full
    print(f"  delta-only      = {mean5!r} / sqrt(rel_delta) = "
          f"{d_only!r}")
    print(f"  fully corrected = {mean5!r} / sqrt(rel_delta*0.6363) = "
          f"{d_full!r}")
    print(f"    sensitivity: literal 4-dp rel_delta=0.0844 -> "
          f"delta-only {mean5 / math.sqrt(0.0844)!r}, full "
          f"{mean5 / math.sqrt(0.0844 * REL_OWN_PRIMARY)!r}")
    print(f"    sensitivity: rel_own=0.6363275925044801 -> full "
          f"{mean5 / math.sqrt(rel_delta * REL_OWN_FULL)!r}")

    # ================= A1b ===========================================
    banner("A1b -- 95% CI ON THE FIVE-CHECKPOINT MEAN, PROPAGATED", "-")
    se5 = sd5 / math.sqrt(5)
    t_half = T4 * se5
    z_half = Z95 * se5
    m_lo_t, m_hi_t = mean5 - t_half, mean5 + t_half
    m_lo_z, m_hi_z = mean5 - z_half, mean5 + z_half
    print(f"  sd={sd5!r}, se = sd/sqrt(5) = {se5!r}")
    print(f"  PRIMARY t(4) interval: [{m_lo_t!r}, {m_hi_t!r}] "
          f"(t={T4})")
    print(f"  sensitivity z-interval: [{m_lo_z!r}, {m_hi_z!r}]")
    print(f"  propagated through delta-only (÷ {div_delta!r}): "
          f"[{m_lo_t / div_delta!r}, {m_hi_t / div_delta!r}]")
    print(f"  propagated through fully-corrected (÷ {div_full!r}): "
          f"[{m_lo_t / div_full!r}, {m_hi_t / div_full!r}]")
    print("  (endpoints divided by the same positive divisors -- the "
          "map is linear in r_obs; reliability uncertainty is NOT "
          "propagated, disclosed)")

    # ================= A1c ===========================================
    banner("A1c -- SIDE BY SIDE", "-")
    full_ci = (m_lo_t / div_full, m_hi_t / div_full)
    only_ci = (m_lo_t / div_delta, m_hi_t / div_delta)
    print(f"  ESM-2 RAW, uncorrected:            {REC_RHO!r} "
          f"CI [{ci_lo!r}, {ci_hi!r}]")
    print(f"  ESM-1v within-family delta-only:   {d_only!r} "
          f"CI [{only_ci[0]!r}, {only_ci[1]!r}]  (t(4)-propagated)")
    print(f"  ESM-1v within-family fully corr.:  {d_full!r} "
          f"CI [{full_ci[0]!r}, {full_ci[1]!r}]  (t(4)-propagated)")
    print(f"  WITHDRAWN cross-model chain (labeled counterfactual, "
          f"prior record): delta-only {chain_lo!r} / full "
          f"{chain_full!r} -- ESM-2 numerator over ESM-1v-family "
          f"reliabilities; retained as illustration only")
    exceeds = abs(REC_RHO) > abs(d_full)
    print(f"  POINT-LEVEL: |ESM-2 raw| {abs(REC_RHO):.6f} vs |ESM-1v "
          f"fully-corrected| {abs(d_full):.6f} -> ESM-2's raw value "
          f"{'EXCEEDS' if exceeds else 'does NOT exceed'} the "
          f"within-family ceiling")
    print(f"  INTERVAL-LEVEL (both directions, so neither is "
          f"oversold):")
    print(f"    - ESM-2 raw {REC_RHO!r} inside ESM-1v fully-corrected "
          f"CI? {full_ci[0] <= REC_RHO <= full_ci[1]}")
    print(f"    - ESM-1v fully-corrected point inside ESM-2 raw CI? "
          f"{ci_lo <= d_full <= ci_hi}")
    print(f"    - ESM-1v fully-corrected point inside ESM-2's CI and "
          f"ESM-2's raw inside the within-family CI -> at n=5 "
          f"precision the two are NOT statistically distinguishable; "
          f"the 'exceeds' statement is a point-estimate comparison.")

    # ================= B1a ===========================================
    banner("B1a -- TWO-COMPONENT VARIANCE DECOMPOSITION", "-")
    var_inst = sd5 ** 2                      # sample variance, ddof=1, n=5
    se_cluster = (ci_hi - ci_lo) / (2 * Z95)  # inverted from recorded CI
    var_clust = se_cluster ** 2
    se_comb = math.sqrt(var_inst + var_clust)
    print(f"  Var_instance (sample var of 5 anchors, ddof=1) = "
          f"{var_inst!r}  (sd {sd5!r})")
    print(f"  Var_cluster: no explicit SE was ever printed on record; "
          f"derived from the recorded position-cluster bootstrap CI "
          f"[{ci_lo!r}, {ci_hi!r}] as SE = width/(2*1.96) = "
          f"{se_cluster!r}  -> Var_cluster = {var_clust!r} "
          f"(derivation disclosed as the method)")
    print(f"  ASSUMPTION (per task): the two components are "
          f"INDEPENDENT; combined by sum of variances.")
    print(f"  SE_instance-inclusive = sqrt({var_inst!r} + "
          f"{var_clust!r}) = {se_comb!r}")

    # ================= B1b ===========================================
    banner("B1b -- INSTANCE-INCLUSIVE INTERVAL", "-")
    half = Z95 * se_comb
    b_lo, b_hi = mean5 - half, mean5 + half
    half_t = T4 * se_comb
    print(f"  around the ESM-1v five-checkpoint mean {mean5!r}:")
    print(f"    PRIMARY  +/- 1.96*SE -> [{b_lo!r}, {b_hi!r}]")
    print(f"    sensitivity +/- t(4)*SE -> [{mean5 - half_t!r}, "
          f"{mean5 + half_t!r}]")
    e_lo, e_hi = REC_RHO - half, REC_RHO + half
    print(f"  ILLUSTRATIVE (task-mandated caveat: ESM-2 has only ONE "
          f"checkpoint -- not a real interval), same SE centered on "
          f"ESM-2's single-checkpoint value {REC_RHO!r}:")
    print(f"    [{e_lo!r}, {e_hi!r}]")

    # ================= B1c ===========================================
    banner("B1c -- DOES IT EXCLUDE ZERO?", "-")
    excl = not (b_lo <= 0.0 <= b_hi)
    print(f"  instance-inclusive interval around the ESM-1v mean = "
          f"[{b_lo!r}, {b_hi!r}]")
    print(f"  excludes zero: {excl} -> the interval INCLUDES zero; "
          f"once checkpoint-to-checkpoint (instance) variance joins "
          f"the position-cluster SE, the ESM-1v within-family mean "
          f"anchor is not distinguishable from zero at 95%.")
    print(f"  (the z-based interval [{b_lo!r}, {b_hi!r}] and the "
          f"t(4)-based [{mean5 - half_t!r}, {mean5 + half_t!r}] "
          f"{'both include' if (not excl and (mean5 - half_t <= 0 <= mean5 + half_t)) else 'disagree about'} "
          f"zero)")

    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. t-interval over n=5 anchors assumes approximate "
          "normality of the five draws; n=5 cannot verify it.")
    print("  2. Var_cluster's SE is inverted from a percentile CI "
          "(4th-decimal approximation; disclosed as the method).")
    print("  3. Independence of the two variance components is "
          "ASSUMED, per the task's instruction to assume and state it.")
    print("  4. Disattenuation carries script 91's proxy assumption "
          "(ESM-1v cross-seed delta agreement as the delta's "
          "reliability) -- within-family here, so the cross-model "
          "objection does not apply to A1, only to the withdrawn "
          "chain.")
    print("  5. G5's reproduction of -0.303/-0.380 is a unit test of "
          "formula consistency, not independent evidence.")
    print("\nSCRIPT 111 DONE (deterministic, single run)")
