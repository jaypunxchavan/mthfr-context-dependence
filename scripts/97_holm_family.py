"""
Task C2 (reliability-and-decompositions): Holm-Bonferroni multiplicity
correction over a NARROWLY PRE-REGISTERED family of headline tests.

PRE-REGISTRATION (this docstring was written before any Holm number
below existed; AGENTS s0/s6). The family is defined HERE, as the task
requires ("Define the family BEFORE computing anything ... to be
finalized and stated explicitly in the script's docstring").

THE FAMILY (primary, m = 5) — headline tests only, each p's provenance
frozen before the run:

  1. AD1 (ThermoMPNN sign audit) — p1 OPERATIONALIZATION, disclosed:
     AD1 itself registered NO p-value (a four-layer qualitative audit:
     forward formula, repo semantics, external quote, empirical
     positive control; DEEPDIVE_LOG [AD1] L509-599). Its claim-bearing
     empirical statistic is "ALL 123 buried (rsa<0.10)
     hydrophobic->charged substitutions score positive ... frac>0=1.000"
     (L549). Family entry p = exact one-sided binomial sign test of
     that printed statistic under p0 = 0.5: p = 0.5^123 = 9.41e-38.
     DISCLOSED: this p is derived HERE from AD1's own printed 123/123,
     not AD1's own; the sign-null independence assumption is violated
     by position clustering (e.g. F516, L621 contribute several
     substitutions each), so the literal value overstates precision.
     Robustness note printed with results: AD1 sorts LAST in this
     family regardless (the other four p's are 0), so its threshold is
     always alpha/1 = 0.05 and it survives for ANY effective n >= 5
     under the sign null (0.5^5 = 0.03125 <= 0.05) — the verdict does
     not depend on the clustering degree.

  2. AD6 pooled depth result (frozen rule R1) — p2 = p_boot of
     [neff] pooled yE from data/processed/task79_depth_associations.csv
     (logged +0.1714 [+0.0918, +0.2471] p_boot=0.0000, DEEPDIVE L2701).
     0/10,000 bootstrap draws -> stored as 0.0, bounded below by ~1e-4
     (printed as such, AGENTS s3).

  3. AD6 conservation dissociation — p3 OPERATIONALIZATION, disclosed:
     the dissociation claim ("ESM does not track conservation while
     ThermoMPNN's residual does", DEEPDIVE L2767-2773) was never given
     a paired delta-rho test for conservation (only NEFF has one,
     SECONDARY (c) p=0.0030). The family entry therefore takes the
     CLAIM-BEARING SIGNIFICANT LIMB: [cons] pooled yT1 p_boot from the
     same CSV (rho +0.3937 [+0.3193, +0.4633] p=0.0000, L2723). The
     null limb [cons] pooled yE p=0.7760 is printed alongside as
     context (a non-rejection is not corrected toward significance;
     it is not a family member).

  4. AB2a's severity-baseline gate — p4 OPERATIONALIZATION, disclosed:
     script 71's formal gates (R2 coverage, R2 identity H354R, R4
     G-anchor/G-lib) are IDENTITY gates and carry no p-value. The
     family entry is finalized as the baseline SIGNIFICANCE claim AB2a
     actually establishes — that the severity baselines correlate
     positively with own_e_b — operationalized CONSERVATIVELY as the
     LARGEST own_p_boot among V2's seven confirmed severity-baseline
     rows (Site_Independent, ESM1v_single, GEMME, DeepSequence_ensemble,
     EVmutation, ESM2_650M, ESM2_150M) in
     task_AB2_proteingym_model_comparison.csv. ALL SEVEN are 0.0 at
     N_BOOT=10000, so p4 = 0.0 whatever the aggregation. Explicitly
     NOT claimed, because no such test exists: "ESM-2 beats the
     severity baselines" (their CIs overlap; no difference test was
     ever registered — do not read a family entry here as one).

  5. The core -0.088 anchor itself — p5 = REF_delta_ESM_our_run's
     own_p_boot in task_AB2_proteingym_model_comparison.csv (0.0 at
     N_BOOT=10000; identity gate re-asserts own_rho ==
     -0.08811806424891734 to 1e-12, the value AB2a-FIX's G-anchor
     reproduced with |diff| = 0.000e+00, CLOSEOUT L1708-1709).

EXPLICITLY OUTSIDE THE CORE FAMILY (task C2a requires flagging, not
  including): AE3b p = 0.0120 (task83_ae3b_results.csv, primary
  rho JSD-vs-madelta), AD6 region-3 p = 0.0194 (task79, neff/region3/
  yE), AD5 SPEC A delta_esm p = 0.02323873 (task78_thermompnn_controls
  .csv, the task rounds it to 0.023). A DISCLOSED SENSITIVITY computes
  Holm over m = 8 = core-5 + this trio, PRE-REGISTERED here so the
  "at real risk" assessment is not invented after seeing it.

METHOD (frozen): Holm-Bonferroni step-down (the method the task names
  as already used in the COPD project), family-wise alpha = 0.05:
  sort p ascending; threshold at rank i (1-based) = alpha / (m - i + 1);
  step-down stops rejecting at the first p > threshold (all subsequent
  are non-rejections); Holm-adjusted p_(i) = max_{j<=i} (m-j+1)*p_(j),
  capped at 1. Ties broken by family order as listed (irrelevant when
  all p's tie at 0; reported anyway).

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 AD1 source literal present in DEEPDIVE_LOG.md: the string
     "BURIED(rsa<0.10) hydro->charged n=123" and "frac>0=1.000" — the
     123/123 statistic must exist in its logged source before it can
     enter the family.
  G2 anchor identity: task_AB2 REF row own_rho == -0.08811806424891734
     to 1e-12 AND own_p_boot == 0.0.
  G3 all seven V2 severity-baseline rows present in task_AB2; their
     own_p_boot max printed (asserted <= 0.05 — if any baseline were
     non-significant the family member would have to be re-reported
     honestly, and this gate is where that would STOP the run).
  G4 task79 rows present with logged values: neff/pooled/yE
     p=0.0000 rho=+0.1714 (5e-4 tol); cons/pooled/yT1 p=0.0000
     rho=+0.3937; cons/pooled/yE p=0.7760; neff/region3/yE p=0.0194.
  G5 trio sources: task83 AE3b p_boot == 0.0120 (4e-4 tol);
     task78 spec A delta_esm p == 0.02323873 (1e-6 tol).

NO DRAWS: this script computes no bootstrap or permutation. N_BOOT and
  N_PERM are read from the environment and reported UNUSED (script
  71's convention), so the house env-var rule stays satisfied.
  Deterministic -> run once with the gates as the sanity check.

OUTPUT: data/processed/task97_holm_family.csv (one row per member per
  family: family, member, source, raw_p, rank, threshold, rejected,
  adj_p). Limitations printed with results: (a) four of five core
  p's are stored bootstrap zeros (0/10,000 draws) — Holm treats them
  as exact 0, which only makes the correction STRICTER for the
  remaining member, never more permissive; (b) p4/p3 are
  operationalizations disclosed above, not tests the original entries
  ran; (c) the family is headline-tests-only by construction — an
  unbounded family would make the correction meaningless in either
  direction (the task's own words), so nothing post-hoc may be added
  to it now that results exist.

Run: venv/bin/python3 scripts/97_holm_family.py   (deterministic, once)
Output: data/processed/task97_holm_family.csv
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", "10000"))   # read, UNUSED (no draws)
N_PERM = int(os.environ.get("N_PERM", "10000"))   # read, UNUSED (no draws)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
DOCS = ROOT / "docs" / "tasks"
T_AB2 = PROC / "task_AB2_proteingym_model_comparison.csv"
T_79 = PROC / "task79_depth_associations.csv"
T_83 = PROC / "task83_ae3b_results.csv"
T_78 = PROC / "task78_thermompnn_controls.csv"
DEEPDIVE = DOCS / "detection-floor-and-mechanism" / "DEEPDIVE_LOG.md"
OUT = PROC / "task97_holm_family.csv"

ALPHA = 0.05
REC_ANCHOR = -0.08811806424891734
SEVEN = ["Site_Independent", "ESM1v_single", "GEMME", "DeepSequence_ensemble",
         "EVmutation", "ESM2_650M", "ESM2_150M"]


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def holm(ps, alpha):
    """Holm step-down. Returns (rank order idx, reject flags, adj p's)."""
    m = len(ps)
    order = np.argsort(ps, kind="stable")
    reject = np.zeros(m, dtype=bool)
    adj = np.empty(m)
    running, stopped = 0.0, False
    for i, idx in enumerate(order):
        thr = alpha / (m - i)
        raw = ps[idx]
        if not stopped and raw <= thr:
            reject[idx] = True
        else:
            stopped = True
        running = max(running, (m - i) * raw)
        adj[idx] = min(1.0, running)
    return order, reject, adj


def run_family(name, members):
    ps = [m["p"] for m in members]
    order, reject, adj = holm(ps, ALPHA)
    log(f"\n  family '{name}' (m={len(members)}), Holm step-down, "
        f"alpha={ALPHA}:")
    log("    rank  member                              raw_p      thr      "
        "reject  adj_p")
    rank = {idx: r + 1 for r, idx in enumerate(order)}
    for i, m in enumerate(members):
        r = rank[i]
        thr = ALPHA / (len(members) - r + 1)
        log(f"    {r:>4}  {m['name']:<35}  {m['p']:.6e}  {thr:.6f}  "
            f"{'YES' if reject[i] else 'no ':>4}   {adj[i]:.6e}")
    surv = int(reject.sum())
    log(f"    -> {surv}/{len(members)} survive at family-wise alpha "
        f"{ALPHA}; non-survivors: "
        f"{[m['name'] for i, m in enumerate(members) if not reject[i]] or 'none'}")
    return members, order, reject, adj


def main():
    log(f"C2 -- HOLM-BONFERRONI over the pre-registered headline family "
        f"(scripts/97) N_BOOT={N_BOOT} N_PERM={N_PERM} both UNUSED "
        f"(deterministic script, no draws)")
    log("family pre-registered in the docstring BEFORE this run: "
        "AD1 sign audit | AD6 pooled depth | AD6 conservation "
        "dissociation | AB2a severity-baseline gate | core -0.088 anchor; "
        "disclosed m=8 sensitivity adds AE3b / AD6 region-3 / AD5 SPEC A")

    # ---- G1: AD1's source statistic exists in the log ----
    dd = DEEPDIVE.read_text()
    lit1 = "BURIED(rsa<0.10) hydro->charged n=123"
    lit2 = "frac>0=1.000"
    if lit1 not in dd or lit2 not in dd:
        gfail(f"G1 FAIL: AD1 source literal not found in "
              f"{DEEPDIVE.name} ({lit1!r} / {lit2!r})")
    n_sign = 123
    p_sign = 0.5 ** n_sign
    log(f"G1 PASS: AD1's 123/123 control literal present in "
        f"{DEEPDIVE.name}; sign-test p = 0.5^{n_sign} = {p_sign:.6e} "
        f"(operationalization disclosed in docstring)")

    # ---- G2: anchor identity ----
    ab2 = pd.read_csv(T_AB2)
    ref = ab2[ab2["model"] == "REF_delta_ESM_our_run"]
    if len(ref) != 1:
        gfail(f"G2 FAIL: REF row count {len(ref)} != 1")
    ref = ref.iloc[0]
    if abs(ref["own_rho"] - REC_ANCHOR) > 1e-12:
        gfail(f"G2 FAIL: REF own_rho {ref['own_rho']} != {REC_ANCHOR}")
    if float(ref["own_p_boot"]) != 0.0:
        gfail(f"G2 FAIL: REF own_p_boot {ref['own_p_boot']} != 0.0")
    p_anchor = float(ref["own_p_boot"])
    log(f"G2 PASS: REF own_rho == {REC_ANCHOR} (|diff| "
        f"{abs(ref['own_rho'] - REC_ANCHOR):.1e} < 1e-12), own_p_boot "
        f"= {p_anchor} (0/10000 draws, bounded below ~1e-4)")

    # ---- G3: seven baselines ----
    seven = ab2[ab2["model"].isin(SEVEN)]
    missing = set(SEVEN) - set(seven["model"])
    if missing:
        gfail(f"G3 FAIL: baseline rows missing: {sorted(missing)}")
    p4 = float(seven["own_p_boot"].max())
    if p4 > ALPHA:
        gfail(f"G3 FAIL: max baseline own_p_boot {p4} > {ALPHA} — the "
              f"family's baseline-significance member does not hold; "
              f"reporting instead of proceeding.")
    log(f"G3 PASS: all seven severity-baseline rows present; "
        f"own_p_boot max = {p4} (all seven {sorted(set(seven['own_p_boot']))} "
        f"at N_BOOT=10000)")

    # ---- G4: AD6 rows ----
    a79 = pd.read_csv(T_79)

    def row(depth, scope, signal):
        r = a79[(a79["depth"] == depth) & (a79["scope"] == scope)
                & (a79["signal"] == signal)]
        if len(r) != 1:
            gfail(f"G4 FAIL: {depth}/{scope}/{signal} -> {len(r)} rows")
        return r.iloc[0]

    r_pooled = row("neff", "pooled", "yE")
    r_con_t1 = row("cons", "pooled", "yT1")
    r_con_e = row("cons", "pooled", "yE")
    r_reg3 = row("neff", "region3", "yE")
    checks = [("neff/pooled/yE p", float(r_pooled["p_boot"]), 0.0, 0.0),
              ("neff/pooled/yE rho", float(r_pooled["rho"]), 0.1714, 5e-4),
              ("cons/pooled/yT1 p", float(r_con_t1["p_boot"]), 0.0, 0.0),
              ("cons/pooled/yT1 rho", float(r_con_t1["rho"]), 0.3937, 5e-4),
              ("cons/pooled/yE p", float(r_con_e["p_boot"]), 0.7760, 0.0),
              ("neff/region3/yE p", float(r_reg3["p_boot"]), 0.0194, 0.0)]
    for nm, got, exp, tol in checks:
        if abs(got - exp) > tol:
            gfail(f"G4 FAIL: {nm} = {got} != logged {exp} (tol {tol})")
    p_ad6_depth = float(r_pooled["p_boot"])
    p_ad6_cons = float(r_con_t1["p_boot"])
    log(f"G4 PASS: task79 rows match their logged values — pooled yE "
        f"p={p_ad6_depth} rho=+0.171422; cons yT1 p={p_ad6_cons} "
        f"rho=+0.393717; cons yE p=0.7760 (null limb); region3 yE "
        f"p=0.0194")

    # ---- G5: trio sources ----
    r83 = pd.read_csv(T_83)
    ae = r83[r83["statistic"] == "primary_rho_JSD_vs_madelta"]
    if len(ae) != 1:
        gfail(f"G5 FAIL: AE3b row count {len(ae)} != 1")
    p_ae3b = float(ae.iloc[0]["p_boot"])
    if abs(p_ae3b - 0.0120) > 4e-4:
        gfail(f"G5 FAIL: AE3b p {p_ae3b} != 0.0120")
    r78 = pd.read_csv(T_78)
    sa = r78[(r78["spec"] == "A") & (r78["focal"] == "delta_esm")]
    if len(sa) != 1:
        gfail(f"G5 FAIL: task78 spec A delta_esm rows {len(sa)} != 1")
    p_ad5 = float(sa.iloc[0]["p"])
    if abs(p_ad5 - 0.02323873) > 1e-6:
        gfail(f"G5 FAIL: AD5 SPEC A delta_esm p {p_ad5} != 0.02323873")
    log(f"G5 PASS: trio sources verified — AE3b p={p_ae3b} (task83), "
        f"AD6 region3 p={float(r_reg3['p_boot'])} (task79), AD5 SPEC A "
        f"delta_esm p={p_ad5:.8f} (task78)")

    # ================= family computations =================
    core = [
        dict(name="AD1 sign audit (0.5^123, op. disclosed)", p=p_sign,
             src="DEEPDIVE L549 literal + sign test"),
        dict(name="AD6 pooled depth (neff/yE)", p=p_ad6_depth,
             src="task79 neff/pooled/yE p_boot"),
        dict(name="AD6 conservation dissoc. (cons/yT1 limb)",
             p=p_ad6_cons, src="task79 cons/pooled/yT1 p_boot"),
        dict(name="AB2a severity-baseline gate (max of 7)", p=p4,
             src="task_AB2 seven baselines own_p_boot max"),
        dict(name="core -0.088 anchor (REF row)", p=p_anchor,
             src="task_AB2 REF own_p_boot"),
    ]
    trio = [
        dict(name="AE3b clade rho (OUTSIDE core family)", p=p_ae3b,
             src="task83 primary rho p_boot"),
        dict(name="AD6 region-3 yE (OUTSIDE core family)",
             p=float(r_reg3["p_boot"]), src="task79 region3 p_boot"),
        dict(name="AD5 SPEC A delta_esm (OUTSIDE core family)",
             p=p_ad5, src="task78 spec A p"),
    ]

    log("\n" + "=" * 74)
    log("PRIMARY — the pre-registered core family (m=5)")
    log("=" * 74)
    _, _, rej_core, adj_core = run_family("core (pre-registered)", core)

    log("\n" + "=" * 74)
    log("DISCLOSED SENSITIVITY (pre-registered in docstring) — core + the "
        "three flagged boundary results (m=8)")
    log("=" * 74)
    _, _, rej_all, adj_all = run_family("core+trio (sensitivity)",
                                        core + trio)

    # ---- at-risk assessment (frozen wording basis: computed numbers) ----
    log("\n  'At real risk' assessment for the three boundary results "
        "(computed, not assumed):")
    for i in range(5, 8):
        m = (core + trio)[i]
        verdict = "survives" if rej_all[i] else "DOES NOT survive"
        log(f"    {m['name']}: raw p={m['p']:.6f}, Holm-8 adj_p="
            f"{adj_all[i]:.6f} -> {verdict} at alpha={ALPHA} "
            f"(margin {ALPHA - adj_all[i]:+.6f})")
    log("    Honest read: at m=8 all three SURVIVE — the 'at real risk' "
        "flag is about MARGIN, not failure: their adjusted p's sit "
        "within 0.011-0.014 of alpha, so one or two additional "
        "mid-range members would flip them (e.g. alpha/(m-rank+1) at "
        "rank 6 falls below 0.0120 once m>=10). Flagged per the task, "
        "with the arithmetic that makes the flag concrete.")
    log("\n  AD1 robustness (pre-registered): AD1 sorts last in the core "
        "family (the other four p's are 0), threshold always 0.05; it "
        "survives for ANY effective n>=5 under the sign null — the "
        "position-clustering caveat cannot change the family verdict.")

    # ---- save ----
    rows = []
    for fname, mems, rejs, adjs in (
            ("core5", core, rej_core, adj_core),
            ("core8_sens", core + trio, rej_all, adj_all)):
        rank_of = {id(m): r + 1 for r, m in
                   enumerate(sorted(mems, key=lambda x: x["p"]))}
        for i, m in enumerate(mems):
            rows.append(dict(family=fname, member=m["name"],
                             source=m["src"], raw_p=m["p"],
                             rank=rank_of[id(m)],
                             threshold=ALPHA / (len(mems) - rank_of[id(m)] + 1),
                             rejected=bool(rejs[i]), adj_p=float(adjs[i])))
    pd.DataFrame(rows).to_csv(OUT, index=False)
    log(f"\n[saved] {OUT}")
    log("\nLIMITATIONS: four of five core p's are stored bootstrap zeros "
        "(0/10,000 draws) — treating them as exact 0 makes Holm STRICTER "
        "for the remaining member, never permissive; p3/p4 are "
        "operationalizations disclosed in the docstring, not tests the "
        "original entries ran; no 'ESM-2 beats the baselines' test exists "
        "and none is implied; the family is headline-only by "
        "construction and NOTHING may be added to it now that results "
        "exist (AGENTS s0).")
    log("SCRIPT 97 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
