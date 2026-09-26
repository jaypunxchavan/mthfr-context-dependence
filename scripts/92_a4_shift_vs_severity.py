"""
Script 92 (Tasks A4b-premise + A4c, reliability-and-decompositions):
isolate the SHIFT component from the SEVERITY term in the calibrated
member deltas, and test cross-member agreement on the shift alone.

PRE-REGISTRATION (written before any number below existed; AGENTS s6)

WHY THIS EXISTS (task A4c, the most delicate task in the doc)
-------------------------------------------------------------
Script 89 (N4) reported cross-member agreement on RAW delta_cal
(median pair rho 0.084365 -> 0.655966) and fired its pre-registered
IMPROVED verdict on that quantity. delta_cal = phi2(av) - phi1(wt)
CONTAINS a shared severity term, so agreement on delta_cal can rise
for a purely mechanical reason (members share a common additive
component), not because the interaction SHIFT became seed-stable.
Script 89 did NOT compute the isolated shift component. This script
supplies the missing number; per A4c, BOTH numbers are reported side
by side and THE SHIFT-COMPONENT CARRIES THE VERDICT.

THE DECOMPOSITION (exact, per member k, x = wt_logodds, d = av - wt)
---------------------------------------------------------------------
    delta_cal_k = phi2(av_k) - phi1(wt_k)
                = [phi2(wt_k) - phi1(wt_k)] + [phi2(av_k) - phi2(wt_k)]
                = severity_k + shift_exact_k
    severity_k      = Delta_phi(wt_k)  (the shared "severity term",
                      a function of the WT score only; wt scores agree
                      across members at median pair rho 0.882637)
    shift_exact_k   = phi2(av_k) - phi2(wt_k)   (= phi2'(xi)*d by the
                      mean value theorem -- the task's phi2'(x)*d term)
    shift_first_k   = phi2'(wt_k) * d_k          (first-order form,
                      reported alongside as the task states it)
    phi2'(x) = b2 / (1 + exp(b2*(x + c2)))   (analytic derivative of
    script 87's phi(x) = -log(1+exp(-b(x+c)))); verified against central
    differences of script 87's own phi (GATE G2).

A4b-PREMISE SECTION (secondary, reported regardless of outcome)
---------------------------------------------------------------
The external analysis's algebraic prediction for N3 rested on two
claims: (p1) Delta_phi = phi2 - phi1 is NON-MONOTONE on the score
range; (p2) the severity term dominates the shift term. N3's existing
run already established (p2) on ESM-2 (CALIBRATION_LOG [N3]:
Spearman(delta_cal, delta_esm) = -0.0307 vs Spearman(delta_cal,
levels) = +0.4139/+0.4186). This script checks (p1) directly: evaluate
Delta_phi'(x) = phi2'(x) - phi1'(x) on a 1001-point grid over the
union of all observed scores; count sign changes with nonzero slope
crossings. PRE-REGISTERED: the premise is CONFIRMED iff >= 1 sign
change exists (a function with a derivative sign change is not
monotone). Result reported either way; NOT a gate (the task says
report the actual result regardless).

GATES (failure => STOP; AGENTS s4)
----------------------------------
G1  analysis base exactly 10,757 rows / 654 positions; R4 joins exact
    (script 86/89 discipline); params loaded from
    task87_calibration_params.csv (NEVER refit).
G2  phi' central-difference check vs script 87's phi: max abs rel err
    < 1e-6 over the observed range (h=1e-5).
G3  exact additive identity: max|severity + shift_exact - delta_cal|
    < 1e-12 for every member.
G4  machinery identity vs script 89's logged output: recomputed median
    pairwise Spearman must equal RAW 0.084365 AND CALIB 0.655966 each
    to < 1e-6 (CALIBRATION_LOG [N4] L438-441).

STATISTICS
----------
10 member pairs (AC2a convention), Spearman, min/median/max on:
  a) severity   (Delta_phi(wt))     -- expected very high (mechanical)
  b) shift_exact                        \ BOTH labeled "THE VALID TEST"
  c) shift_first_order                  /
  d) raw delta, delta_cal              -- references, recomputed
Secondary DIAGNOSTIC (not part of the verdict, labeled as such):
  per-member Spearman(shift_exact, own_e_b) with position-cluster
  bootstrap CI (N_BOOT, seed 0) -- shows whether script 89's 5/5
  positive calibrated rhos survive severity-isolation.

VERDICT RULE (fixed here, before running; A4c)
----------------------------------------------
REAL stability improvement  iff  median pair rho on the SHIFT component
(shift_exact, primary; shift_first_order reported as the same test in
first-order form) >= 2 * raw median (= 0.168730, the same 2x bar
script 89's rule (i) used, now applied to the valid quantity).
Otherwise: MECHANICAL -- the delta_cal improvement does not survive
isolation of the shift; the shared severity term carries it, and A4c's
verdict rests on the shift-component number, NOT on delta_cal's 0.655966.
Both numbers + the severity number always print. No threshold is tuned
after seeing results.

LIMITATIONS printed with results (AGENTS s6):
- phi1/phi2 fit on ESM-2's score range, applied fit-once to ESM-1v
  (script 89's disclosed convention; out-of-domain <=0.2% per member).
- Rank-based (Spearman) agreement only.
- This does not re-run N4's verdict; it supplies the missing isolation
  N4's own mechanism caveat called for, and flags (not edits) that
  script 89's rule (i) fired on the severity-contaminated quantity.

Run: SMOKE=1 N_BOOT=500 venv/bin/python3 scripts/92_...
     then full: N_BOOT=10000 venv/bin/python3 scripts/92_...
Output: data/processed/task92_a4c_shift_vs_severity.csv
"""
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import position_cluster_bootstrap, _spearman

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = os.environ.get("SMOKE", "") == "1"

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RAW_MED_LOGGED = 0.084365      # script 89 / AC4d (gate G4)
CAL_MED_LOGGED = 0.655966      # script 89 (gate G4)


def log(msg=""):
    print(msg, flush=True)


def main():
    tag = "SMOKE=True" if SMOKE else "SMOKE=False"
    log(f"A4c -- SHIFT vs SEVERITY isolation (scripts/92) {tag} "
        f"N_BOOT={N_BOOT}")

    # ---- load script 87's phi (single implementation) ----
    spec = importlib.util.spec_from_file_location(
        "n2_calibration", ROOT / "scripts" / "87_n2_calibration_fit.py")
    n2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(n2)
    phi = n2.phi

    par = pd.read_csv(PROC / "task87_calibration_params.csv")
    b1 = float(par.loc[par.arm == "phi1_wt", "b"].iloc[0])
    c1 = float(par.loc[par.arm == "phi1_wt", "c"].iloc[0])
    b2 = float(par.loc[par.arm == "phi2_a222v", "b"].iloc[0])
    c2 = float(par.loc[par.arm == "phi2_a222v", "c"].iloc[0])
    log(f"phi1 b={b1:.6f} c={c1:.6f}; phi2 b={b2:.6f} c={c2:.6f} "
        f"(loaded, NOT refit -- G1)")

    def phi1(x):
        return phi(np.asarray(x, dtype=float), b1, c1)

    def phi2(x):
        return phi(np.asarray(x, dtype=float), b2, c2)

    def phi1p(x):   # analytic derivative b/(1+exp(b(x+c)))
        x = np.asarray(x, dtype=float)
        return b1 / (1.0 + np.exp(b1 * (x + c1)))

    def phi2p(x):
        x = np.asarray(x, dtype=float)
        return b2 / (1.0 + np.exp(b2 * (x + c2)))

    # ---- G2: phi' vs central differences of script 87's phi ----
    xs = np.linspace(-20.0, 10.0, 1001)
    h = 1e-5
    num2 = (phi(xs + h, b2, c2) - phi(xs - h, b2, c2)) / (2 * h)
    rel = np.max(np.abs(phi2p(xs) - num2) / np.maximum(np.abs(num2), 1e-12))
    log(f"G2 phi' analytic vs central-difference of script 87's phi: "
        f"max rel err = {rel:.3e} -> {'OK' if rel < 1e-6 else 'FAIL'}")
    if rel >= 1e-6:
        log("*** G2 FAIL -- derivative wrong. STOP. ***")
        sys.exit(1)

    # ---- A4b premise p1: is Delta_phi non-monotone on observed range? ----
    dphi_prime = phi2p(xs) - phi1p(xs)
    sgn = np.sign(dphi_prime)
    crossings = int(np.sum(sgn[:-1] * sgn[1:] < 0))
    log(f"\nA4b-PREMISE p1 (pre-registered check): Delta_phi'(x) on a "
        f"1001-pt grid over [-20, 10]:")
    log(f"  min={dphi_prime.min():+.6f}  max={dphi_prime.max():+.6f}  "
        f"sign changes={crossings}")
    log(f"  -> Delta_phi = phi2 - phi1 is "
        f"{'NON-MONOTONE (premise CONFIRMED)' if crossings >= 1 else 'monotone on this grid (premise NOT confirmed)'}")
    log(f"  (p2 severity-dominance was already established by N3's run: "
        f"Spearman(delta_cal, delta_esm) = -0.0307 while levels agree at "
        f"+0.4139/+0.4186 -- quoted from CALIBRATION_LOG [N3], not recomputed)")

    # ---- G1: analysis base + joins ----
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    log(f"\nanalysis base: {len(base)} rows / "
        f"{base['position'].nunique()} positions (expect 10757 / 654)")
    if (len(base), base["position"].nunique()) != (10757, 654):
        log("G1 FAIL -- base differs from the published set. STOP.")
        sys.exit(1)

    comp = {}
    for k in range(1, 6):
        m = pd.read_csv(PROC / f"task_AC4_esm1v_member{k}_scores.csv")
        j = base.merge(m[["position", "wt_aa", "mut_aa",
                          "wt_logodds", "av_logodds", "delta"]],
                       on=["position", "mut_aa"], how="left", validate="1:1")
        if int(j["delta"].isna().sum()):
            log(f"G1 FAIL -- member {k} unmatched rows. STOP.")
            sys.exit(1)
        if not (j["wt_aa_x"] == j["wt_aa_y"]).all():
            log(f"G1 FAIL -- member {k} wt_aa mismatch. STOP.")
            sys.exit(1)
        wt, av = j["wt_logodds"].to_numpy(), j["av_logodds"].to_numpy()
        d = j["delta"].to_numpy()
        j["delta_cal"] = phi2(av) - phi1(wt)
        j["severity"] = phi2(wt) - phi1(wt)          # Delta_phi(wt)
        j["shift_exact"] = phi2(av) - phi2(wt)        # = delta_cal - severity
        j["shift_first"] = phi2p(wt) * d              # phi2'(x)*d, first order
        # G3 exact additive identity
        g3 = float(np.max(np.abs(j["severity"] + j["shift_exact"]
                                 - j["delta_cal"])))
        if g3 >= 1e-12:
            log(f"G3 FAIL -- member {k} decomposition |diff|={g3:.3e}. STOP.")
            sys.exit(1)
        comp[k] = j
    log("G3 exact additive identity severity + shift_exact == delta_cal: "
        "max|diff| < 1e-12 for all 5 members -> OK")

    ks = list(range(1, 6))

    def pair_med(col):
        vals = []
        for a in range(5):
            for b in range(a + 1, 5):
                vals.append(_spearman(comp[ks[a]][col].to_numpy(),
                                      comp[ks[b]][col].to_numpy()))
        return np.array(vals)

    p_raw = pair_med("delta")
    p_cal = pair_med("delta_cal")
    p_sev = pair_med("severity")
    p_shx = pair_med("shift_exact")
    p_shf = pair_med("shift_first")

    # ---- G4: machinery identity vs script 89's logged numbers ----
    d_raw = abs(float(np.median(p_raw)) - RAW_MED_LOGGED)
    d_cal = abs(float(np.median(p_cal)) - CAL_MED_LOGGED)
    ok4 = (d_raw < 1e-6) and (d_cal < 1e-6)
    log(f"\nG4 machinery identity: recomputed RAW median "
        f"{np.median(p_raw):.6f} vs logged {RAW_MED_LOGGED} "
        f"(|diff|={d_raw:.2e}); CALIB median {np.median(p_cal):.6f} vs "
        f"logged {CAL_MED_LOGGED} (|diff|={d_cal:.2e}) -> "
        f"{'OK' if ok4 else 'FAIL'}")
    if not ok4:
        log("*** G4 FAIL -- reproduction of script 89's numbers broke. STOP. ***")
        sys.exit(1)

    # ---- the two numbers, side by side ----
    def fmt(p):
        return (f"min={p.min():.6f} median={np.median(p):.6f} "
                f"max={p.max():.6f}")

    log("\n" + "=" * 74)
    log("A4c  CROSS-MEMBER AGREEMENT, SIDE BY SIDE (10 pairs, Spearman)")
    log("=" * 74)
    log(f"  RAW delta            : {fmt(p_raw)}   (reference)")
    log(f"  delta_cal (script 89): {fmt(p_cal)}   <- mechanically inflated?")
    log(f"  severity Delta_phi(wt): {fmt(p_sev)}   (the shared additive term)")
    log(f"  SHIFT exact           : {fmt(p_shx)}   ** THE VALID TEST **")
    log(f"  SHIFT first-order     : {fmt(p_shf)}   (phi2'(wt)*d, same test)")

    # variance/spread context (diagnostic)
    for col in ("delta_cal", "severity", "shift_exact"):
        sds = [float(comp[k][col].std()) for k in ks]
        log(f"  spread sd({col}) per member: "
            f"{', '.join(f'{s:.4f}' for s in sds)}")

    # ---- secondary DIAGNOSTIC: per-member shift_exact vs own_e_b ----
    log("\nSECONDARY DIAGNOSTIC (not part of the A4c verdict; descriptive):")
    log("  per-member Spearman(shift_exact, own_e_b), position-cluster CI")
    rhos_shift, rows = [], []
    for k in ks:
        if SMOKE:
            # smoke: point rho only (machinery check)
            r = float(_spearman(comp[k]["shift_exact"].to_numpy(),
                                comp[k]["own_e_b"].to_numpy()))
            lo = hi = np.nan
        else:
            bb = position_cluster_bootstrap(comp[k], "position",
                                            "shift_exact", "own_e_b",
                                            n_boot=N_BOOT, seed=SEED)
            r, lo, hi = float(bb["observed_rho"]), bb["ci_lo"], bb["ci_hi"]
        rhos_shift.append(r)
        raw_ref = pd.read_csv(PROC / "task_AC4_esm1v_summary.csv")
        rr = raw_ref[(raw_ref["member"] == k) &
                     (raw_ref["target_col"] == "own_e_b")].iloc[0]
        log(f"  member {k}: shift rho={r:+.6f} "
            f"CI=[{lo:+.6f},{hi:+.6f}]  (raw={float(rr['observed_rho']):+.6f})")
        rows.append({"member": k, "arm": "shift_exact", "rho": r,
                     "ci_lo": lo, "ci_hi": hi,
                     "rho_raw_ref": float(rr["observed_rho"])})
    signs_pos = sum(1 for r in rhos_shift if r > 0)
    log(f"  shift-arm signs: {signs_pos} pos / {5 - signs_pos} neg "
        f"(script 89's delta_cal arm was 5 pos / 0 neg)")

    # ---- VERDICT (rule fixed in docstring before running) ----
    raw_med = float(np.median(p_raw))
    shx_med = float(np.median(p_shx))
    shf_med = float(np.median(p_shf))
    bar = 2 * raw_med
    real = shx_med >= bar
    log("\n" + "=" * 74)
    log("A4c VERDICT (rule fixed in the docstring before running)")
    log("=" * 74)
    log(f"  raw median = {raw_med:.6f}; bar (2x raw) = {bar:.6f}")
    log(f"  delta_cal median = {np.median(p_cal):.6f} "
        f"(script 89's rule-(i) quantity)")
    log(f"  SHIFT exact median = {shx_med:.6f}  -> "
        f"{'MET' if real else 'NOT MET'}")
    log(f"  SHIFT first-order median = {shf_med:.6f}  -> "
        f"{'MET' if shf_med >= bar else 'NOT MET'}")
    if real:
        log("  -> REAL STABILITY IMPROVEMENT: cross-member agreement on "
            "the ISOLATED SHIFT meets the 2x bar; calibration's gain "
            "survives severity-isolation. Verdict rests on the shift "
            "number.")
    else:
        log("  -> MECHANICAL: cross-member agreement on the ISOLATED "
            "SHIFT does NOT meet the 2x bar. The delta_cal improvement "
            "(0.655966) is carried by the shared severity term, not by "
            "a seed-stable shift. Per A4c, THE VERDICT RESTS ON THIS "
            "SHIFT NUMBER, not on delta_cal.")

    # ---- save ----
    out = PROC / ("task92_a4c_smoke.csv" if SMOKE
                  else "task92_a4c_shift_vs_severity.csv")
    srows = []
    for name, p in [("raw_delta", p_raw), ("delta_cal", p_cal),
                    ("severity_deltaphi_wt", p_sev),
                    ("shift_exact", p_shx), ("shift_first_order", p_shf)]:
        srows.append({"stat": f"pairmed_{name}", "min": p.min(),
                      "median": np.median(p), "max": p.max(),
                      "value": np.median(p)})
    srows += [{"stat": "bar_2x_raw", "min": np.nan, "median": bar,
               "max": np.nan, "value": bar},
              {"stat": "verdict_real_improvement", "min": np.nan,
               "median": np.nan, "max": np.nan, "value": float(real)},
              {"stat": "a4b_premise_signchanges", "min": np.nan,
               "median": np.nan, "max": np.nan, "value": float(crossings)}]
    for r in rows:
        srows.append({"stat": f"member{r['member']}_shift_rho",
                      "min": r["ci_lo"], "median": r["rho"],
                      "max": r["ci_hi"], "value": r["rho"]})
    pd.DataFrame(srows).to_csv(out, index=False)
    log(f"\n[saved] {out}")
    log("\nLIMITATIONS: phi1/phi2 fit on ESM-2's range, applied fit-once "
        "to ESM-1v (<=0.2% out-of-domain, disclosed by script 89); "
        "rank agreement only; this supplies A4c's missing isolation and "
        "does NOT edit script 89's pre-registered verdict -- it flags "
        "that rule (i) fired on the severity-contaminated quantity.")
    if SMOKE:
        log("*** SMOKE RUN: machinery only, NOT findings. ***")
    log("SCRIPT 92 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
