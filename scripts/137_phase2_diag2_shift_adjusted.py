"""Script 137 -- Phase 2 diagnostics II Task D9: SHIFT-ADJUSTED p_spec, the
frozen construction run on residuals.

WHY
---
Diagnostics I computed Spearman(rho_b, mean|delta_b|) = -0.614 (full) / -0.613
(H) across the 96 backgrounds, and separately computed A222V's residual from
that fitted line -- but never ran the frozen p_spec construction ON the
residuals.  D9 does.  This is the shift-matched null the second external
review asked for.

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  The three outcome words reserved for the frozen test are not used as
the label for any result computed here.  p_spec_adj is a DESCRIPTIVE
companion to the frozen p_spec, not a replacement for it.

CONSTRUCTION (pre-registered in this docstring BEFORE the first run)
--------------------------------------------------------------------
Covariate:  mean_abs_delta_b = mean(|delta_b(v)|) over exactly the usable
rows script 125 used for that background's rho_b (pdg.usable_rows), both
views, built exactly as script 134 built it.  A222V's own is
mean(|A.a222v_rows.delta|) over the same rows; its delta is the cached
task32 delta_esm column.

Gate D9-G1 is run FIRST and must pass before any new analysis is printed.
Its targets are D4's printed values, quoted from
docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAG_D4_D5_FULL_OUTPUT.txt
and re-derived by IMPORTING script 134 (its ols_resid) and pdg.build, not
reimplementing.  Tolerance |diff| < 2e-6 for the 6-dp quantities and
< 1e-8 for the 9-dp correlations.  If any fails: print GATE FAIL, exit 1,
D9-D11 do not run.

THREE VARIANTS; THE FIRST IS PRIMARY, DESIGNATED NOW; ALL THREE REPORTED
------------------------------------------------------------------------
PRIMARY -- leave-one-out residuals on N (|N| = 78).
  For each null b in N:  fit OLS  rho ~ a + c*mean|delta|  on N \\ {b},
  then  r_b = rho_b - (a_hat + c_hat * mad_b)   (out-of-sample for b).
  For A222V:  fit on ALL of N (A222V is not in the fit),
  then  r_A = rho_A - (a_hat + c_hat * mad_A).
  This makes A222V and the nulls EXCHANGEABLE: every residual comes from a
  fit that excluded that background.  Using in-sample null residuals against
  an out-of-sample A222V residual would be subtly unfair, which is exactly
  why this is primary.

SENSITIVITY 1 -- in-sample fit on N.  Fit once on the 78; every null's
  in-sample residual; A222V's out-of-sample residual.

SENSITIVITY 2 -- D4's all-96 fit (includes Arm S; A222V excluded).  Ties this
  task back to Diagnostics I.

For each variant and each view:
  p_spec_adj = (1 + #{b in N : r_b <= r_A}) / (1 + |N|)
  -- same form, same ONE-SIDED SIGNED `<=` direction as the frozen test.  The
  inequality direction is FROZEN and is not flipped anywhere in this script.
  Reported alongside: the identity of every null at or below r_A (with arm,
  sequence distance, mean|delta|); A222V's r_A; A222V's signed rank within
  N u {A222V} (rank 1 = most negative); and whether p_spec_adj is AT OR BELOW
  or ABOVE the frozen numeric thresholds (0.05 full, 0.10 H).
The TEN MOST NEGATIVE NULL RESIDUALS are printed for the PRIMARY variant so a
reader can see who lies beyond A222V.

RESAMPLING UNIT -- READ THIS
----------------------------
NONE.  There is no bootstrap and no permutation anywhere in D9.  Every
quantity is a deterministic OLS fit on a fixed set of points and an exact
rank count, so there is no Monte-Carlo uncertainty to propagate and
N_BOOT / N_PERM are not read by this script.  The task is a construction, not
an inference; the counts are exact.  (Contrast D10c and D11, which do
resample BACKGROUNDS, 10,000 draws, SEED=0, per-background rho_b held fixed
-- never positions.)

WORDING
-------
Adjusted p_spec is compared to the frozen NUMERIC thresholds and the result
is reported only as "at or below" or "above" each.  The three outcome words
reserved for the frozen PHASE2_PREREG.md section-5 test are not used as the
label for any result computed here.

LIMITS, STATED UP FRONT (AGENTS 6, and AGENTS 4's warning about a covariate
constructed from the same quantities as the outcome)
-------------------------------------------------------------------------
* PARTIAL CONSTRUCTIONAL OVERLAP.  mean_abs_delta_b and rho_b are both
  functions of the SAME delta_b.  They share delta_b exactly and do not
  share own_e_b at all.  So this adjustment removes the component of
  delta_b's distribution that rho_b also sees, but it CANNOT make the two
  statistics independent.
* A SURVIVAL IS NOT EVIDENCE THAT DELTA'S INFLUENCE IS GONE -- only that
  the overall magnitude of delta does not account for the ranking.  A
  background can have small mean|delta| and a badly shaped delta and still
  drive rho_b.
* mean|delta| is SCALE-ONLY and blind to sign pattern.  A shift confound
  operating through heteroscedasticity or sign-pattern rather than magnitude
  would not be removed by this and is not ruled out by it.
* Leave-one-out residuals are exact but they are NOT a null distribution:
  the 78 residuals are not exchangeable draws from a common population, they
  are the result of 78 overlapping fits on the same 78 data points.  A
  background at a leverage point gets a larger LOO residual mechanically.
  This is a real limit on reading a small p_spec_adj as a "tail probability".
* Arm S is excluded from every fit here (fits are on N only, or on the 96
  with S included and A222V excluded -- never A222V).  Arm S's 18
  position-222 backgrounds are not candidates for "beating" A222V in any
  view of this task, and the 96-background sensitivity is reported as a
  sensitivity for that reason, not selected.
* The 96 rho_b share one y-vector (own_e_b) and are mutually correlated;
  this is not modelled and is disclosed, not corrected.

Usage:
  venv/bin/python3 scripts/137_phase2_diag2_shift_adjusted.py
"""

import hashlib
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg          # noqa: E402

DOCS = ROOT / "docs/tasks/phase2-diagnostics-locality-magnitude"
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"

# ---- D9-G1 targets: D4's printed values, quoted from its FULL_OUTPUT -----
G_RHO_MAD_FULL = -0.614188823
G_RHO_MAD_H = -0.612696690
G_SLOPE_FULL, G_INT_FULL = -0.896326, +0.034053
G_SLOPE_H, G_INT_H = -0.964705, +0.037990
G_MADA_FULL, G_MADA_H = 0.070330, 0.069403
G_RESIDA_FULL, G_RESIDA_H = -0.059133, -0.061058
G_NAMED = {                                  # mean|delta| / residual
    "G_P254F": {"full": (0.208008, +0.056146), "H": (0.200143, +0.053135)},
    "AV_220":  {"full": (0.047893, -0.075724), "H": (0.050233, -0.084010)},
    "AV_195":  {"full": (0.095630, -0.032500), "H": (0.098154, -0.036722)},
}
TOL_CORR = 1e-8
TOL_6DP = 2e-6

FROZEN_P_FULL = 0.05
FROZEN_P_H = 0.10

t0 = time.time()
gates = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def near(got, want, tol):
    return abs(float(got) - float(want)) < tol


def load_s134():
    """Import script 134 once; its ols_resid is the residualiser used
    throughout (imported, not reimplemented)."""
    s = importlib.util.spec_from_file_location(
        "s134", ROOT / "scripts/134_phase2_diag_shift_magnitude.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def ols_fit_predict(y, x, x_new):
    """OLS with intercept of y on x; return (slope, intercept, prediction at x_new).

    Uses the SAME np.linalg.lstsq design matrix as script 134's ols_resid
    (which is imported and used for the residualiser), so the fit is
    literally the same code Diagnostics I used.
    """
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = beta[0] + beta[1] * np.asarray(x_new, float)
    return float(beta[1]), float(beta[0]), pred


def verdict(p, view):
    thr = FROZEN_P_FULL if view == "full" else FROZEN_P_H
    return ("AT OR BELOW" if p <= thr else "ABOVE"), thr


def main():
    banner("D9 -- SHIFT-ADJUSTED p_spec: THE FROZEN CONSTRUCTION ON RESIDUALS "
           "(script 137)")
    print("SCOPE: descriptive.  p_spec_adj is a companion to the frozen "
          "p_spec, never a replacement.  No outcome word is computed or used "
          "as a label.")
    print("RESAMPLING UNIT: NONE.  No bootstrap, no permutation, no "
          "Monte-Carlo uncertainty.  N_BOOT / N_PERM are not read by this "
          "script.  Every number below is a deterministic OLS fit on a fixed "
          "set of points or an exact rank count.")
    print("INEQUALITY DIRECTION: FROZEN.  one-sided, signed, r_b <= r_A.  It "
          "is not flipped anywhere in this script.")

    # =====================================================================
    # GATE D9-G1
    # =====================================================================
    banner("GATE D9-G1 (HARD; tol 1e-8 on correlations, 2e-6 on the 6-dp "
           "quantities) -- reproduce D4's PRINTED values before any new "
           "analysis", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  input table sha256 = {sha}")
    gate("D9-G1 input table sha256", sha == TABLE_SHA,
         f"{'match' if sha == TABLE_SHA else 'MISMATCH'}")

    s134 = load_s134()
    print("  script 134 imported; its ols_resid is the residualiser used "
          "throughout (imported, not reimplemented).")

    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    rho_a_full = A.rho_a222v
    N_ids = list(A.N_IDS)
    bgs = list(A.bgs)
    nN = len(N_ids)
    RHO = {"full": {b: float(A.point[b]) for b in bgs},
           "H": {b: float(point_h[b]) for b in bgs}}
    RHO_A = {"full": float(rho_a_full), "H": float(rho_a_H)}
    ARM = {b: table.loc[b, "arm"] for b in bgs}
    DIST = {b: int(table.loc[b, "dist_222"]) for b in bgs}

    mad = {"full": {}, "H": {}}
    mad_a = {}
    for b in bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    for view in ("full", "H"):
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    resid_all = {}
    for view in ("full", "H"):
        r96 = np.array([RHO[view][b] for b in bgs], float)
        m96 = np.array([mad[view][b] for b in bgs], float)
        res, beta = s134.ols_resid(r96, m96)
        pred_A = beta[0] + beta[1] * mad_a[view]
        r_A = RHO_A[view] - pred_A
        resid_all[view] = dict(
            beta=beta, r_A=r_A, pred_A=pred_A,
            res_b={b: float(res[i]) for i, b in enumerate(bgs)},
            rho_mad=float(spearmanr(r96, m96).statistic))

        gate(f"D9-G1 Spearman(rho_b, mean|delta|) ({view})",
             near(resid_all[view]["rho_mad"],
                  G_RHO_MAD_FULL if view == "full" else G_RHO_MAD_H,
                  TOL_CORR),
             f"got {resid_all[view]['rho_mad']!r} vs "
             f"{G_RHO_MAD_FULL if view == 'full' else G_RHO_MAD_H} "
             f"|diff|={abs(resid_all[view]['rho_mad'] - (G_RHO_MAD_FULL if view == 'full' else G_RHO_MAD_H)):.3e}")
        gate(f"D9-G1 all-96 OLS slope ({view})",
             near(beta[1], G_SLOPE_FULL if view == "full" else G_SLOPE_H,
                  TOL_6DP),
             f"got {beta[1]:+.9f} vs "
             f"{G_SLOPE_FULL if view == 'full' else G_SLOPE_H}")
        gate(f"D9-G1 all-96 OLS intercept ({view})",
             near(beta[0], G_INT_FULL if view == "full" else G_INT_H,
                  TOL_6DP),
             f"got {beta[0]:+.9f} vs {G_INT_FULL if view == 'full' else G_INT_H}")
        gate(f"D9-G1 A222V mean|delta| ({view})",
             near(mad_a[view], G_MADA_FULL if view == "full" else G_MADA_H,
                  TOL_6DP),
             f"got {mad_a[view]:.6f} vs "
             f"{G_MADA_FULL if view == 'full' else G_MADA_H}")
        gate(f"D9-G1 A222V residual, all-96 fit ({view})",
             near(r_A, G_RESIDA_FULL if view == "full" else G_RESIDA_H,
                  TOL_6DP),
             f"got {r_A:+.6f} vs "
             f"{G_RESIDA_FULL if view == 'full' else G_RESIDA_H}")
        for b, targ in G_NAMED.items():
            gm, gr = targ[view]
            gate(f"D9-G1 {b} mean|delta| ({view})",
                 near(mad[view][b], gm, TOL_6DP),
                 f"got {mad[view][b]:.6f} vs {gm}")
            gate(f"D9-G1 {b} residual, all-96 fit ({view})",
                 near(resid_all[view]["res_b"][b], gr, TOL_6DP),
                 f"got {resid_all[view]['res_b'][b]:+.6f} vs {gr:+.6f}")

    n_fail = sum(1 for _, ok, _ in gates if not ok)
    print(f"\n  {len(gates) - n_fail}/{len(gates)} D9-G1 checks PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        print("\nGATE FAIL: D9-G1 failed.  STOP D9-D11 (D0 stands; its own gate "
              "passed).  Do not raise N, do not adjust a tolerance.")
        sys.exit(1)
    print("  GATE PASS: D4's printed values reproduce.  New analysis below.")

    # =====================================================================
    # THE THREE VARIANTS
    # =====================================================================
    banner("D9 -- THE THREE RESIDUAL VARIANTS", "-")
    print("PRIMARY = leave-one-out on N (designated in advance; every residual "
          "comes from a fit that excluded that background, so A222V and the "
          "nulls are exchangeable).")
    print("SENS 1  = in-sample fit on N (fit once on the 78).")
    print("SENS 2  = D4's all-96 fit (Arm S included, A222V excluded).")

    def variant_loo(view):
        """PRIMARY. LOO residual for each null; A222V out-of-sample on all N."""
        r = {b: None for b in N_ids}
        for b in N_ids:
            sub = [x for x in N_ids if x != b]
            y = np.array([RHO[view][x] for x in sub], float)
            x = np.array([mad[view][x] for x in sub], float)
            _, _, pred = ols_fit_predict(y, x, [mad[view][b]])
            r[b] = RHO[view][b] - float(pred[0])
        y = np.array([RHO[view][b] for b in N_ids], float)
        x = np.array([mad[view][b] for b in N_ids], float)
        slope, inter, predA = ols_fit_predict(y, x, [mad_a[view]])
        r_A = RHO_A[view] - float(predA[0])
        return r, r_A, dict(slope=slope, intercept=inter, n_fit=len(N_ids))

    def variant_insample(view):
        """SENSITIVITY 1. One fit on all 78; nulls get in-sample residuals."""
        y = np.array([RHO[view][b] for b in N_ids], float)
        x = np.array([mad[view][b] for b in N_ids], float)
        res, beta = s134.ols_resid(y, x)
        r = {b: float(res[i]) for i, b in enumerate(N_ids)}
        r_A = RHO_A[view] - (beta[0] + beta[1] * mad_a[view])
        return r, r_A, dict(slope=float(beta[1]), intercept=float(beta[0]),
                            n_fit=len(N_ids))

    def variant_all96(view):
        """SENSITIVITY 2. D4's fit over all 96."""
        r = dict(resid_all[view]["res_b"])
        r_A = resid_all[view]["r_A"]
        beta = resid_all[view]["beta"]
        return r, r_A, dict(slope=float(beta[1]), intercept=float(beta[0]),
                            n_fit=len(bgs))

    VARIANTS = [("PRIMARY (leave-one-out on N)", variant_loo, True),
                ("SENSITIVITY 1 (in-sample fit on N)", variant_insample, False),
                ("SENSITIVITY 2 (D4's all-96 fit)", variant_all96, False)]

    summary_rows = []
    for name, fn, is_primary in VARIANTS:
        print(f"\n  === {name} ===")
        for view in ("full", "H"):
            r, r_A, meta = fn(view)
            k = int(sum(1 for b in N_ids if r[b] <= r_A))
            p_adj = (1 + k) / (1 + nN)
            rank = 1 + int(sum(1 for b in N_ids if r[b] < r_A))
            at_or_below = sorted(b for b in N_ids if r[b] <= r_A)
            rel, thr = verdict(p_adj, view)
            print(f"    [{view}]  fit on n = {meta['n_fit']};  "
                  f"OLS rho ~ {meta['intercept']:+.6f} {meta['slope']:+.6f}"
                  f"*mean|delta|")
            print(f"      A222V  mean|delta| = {mad_a[view]:.6f}  "
                  f"rho = {RHO_A[view]:+.6f}  ->  r_A = {r_A:+.6f}")
            print(f"      #{{b in N : r_b <= r_A}} = {k} of {nN}")
            print(f"      p_spec_adj = (1 + {k})/(1 + {nN}) = {p_adj:.6f}"
                  f"   -> {rel} the frozen threshold {thr}")
            print(f"      A222V signed rank within N u {{A222V}} = "
                  f"{rank}/{nN + 1}  (rank 1 = most negative)")
            if at_or_below:
                print(f"      nulls at or below r_A: "
                      f"{'bg_id':>10s} {'arm':>4s} {'dist_222':>9s} "
                      f"{'mean|delta|':>12s} {'rho':>12s} {'r_b':>12s}")
                for b in at_or_below:
                    print(f"        {'':>10s} {b:>10s} {ARM[b]:>4s} "
                          f"{DIST[b]:>9d} {mad[view][b]:>12.6f} "
                          f"{RHO[view][b]:+12.6f} {r[b]:+12.6f}")
            else:
                print("      nulls at or below r_A: NONE (k = 0, the floor "
                      "1/79)")
            summary_rows.append(dict(variant=name, view=view, k=k,
                                     p_adj=p_adj, rel=rel, thr=thr,
                                     r_A=r_A, rank=rank, slope=meta["slope"],
                                     inter=meta["intercept"],
                                     n_fit=meta["n_fit"],
                                     beaters=at_or_below))

    # ---- the ten most negative null residuals, PRIMARY -------------------
    banner("TEN MOST NEGATIVE NULL RESIDUALS -- PRIMARY (leave-one-out on N)",
           "-")
    print("So the reader can see exactly who lies beyond A222V.  "
          "A222V's own r_A is marked.  These are DETERMINISTIC fits, not "
          "resampled draws.")
    for view in ("full", "H"):
        r, r_A, _ = variant_loo(view)
        order = sorted(N_ids, key=lambda b: r[b])[:10]
        print(f"\n  [{view}]  A222V r_A = {r_A:+.6f}")
        print(f"    {'rank':>4s} {'bg_id':>10s} {'arm':>4s} {'dist_222':>9s} "
              f"{'mean|delta|':>12s} {'rho':>12s} {'r_b':>12s} {'<= r_A?':>8s}")
        for i, b in enumerate(order, start=1):
            print(f"    {i:>4d} {b:>10s} {ARM[b]:>4s} {DIST[b]:>9d} "
                  f"{mad[view][b]:>12.6f} {RHO[view][b]:+12.6f} "
                  f"{r[b]:+12.6f} {'YES' if r[b] <= r_A else 'no':>8s}")
        n_beyond = sum(1 for b in N_ids if r[b] <= r_A)
        print(f"    -> {n_beyond} of the {nN} nulls are at or below A222V's "
              f"residual on this view")

    # =====================================================================
    banner("D9 SUMMARY TABLE", "-")
    print(f"  {'variant':>34s} {'view':>5s} {'k':>3s} {'p_spec_adj':>11s} "
          f"{'r_A':>11s} {'rank':>7s}  vs frozen threshold")
    for d in summary_rows:
        print(f"  {d['variant']:>34s} {d['view']:>5s} {d['k']:>3d} "
              f"{d['p_adj']:>11.6f} {d['r_A']:+11.6f} "
              f"{d['rank']:>4d}/{nN + 1}  {d['rel']} {d['thr']}")
    print(f"\n  {'variant':>34s} {'view':>5s} {'slope':>11s} {'intercept':>11s} "
          f"{'n_fit':>6s}")
    for d in summary_rows:
        print(f"  {d['variant']:>34s} {d['view']:>5s} {d['slope']:+11.6f} "
              f"{d['inter']:+11.6f} {d['n_fit']:>6d}")

    banner("D9 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print(f"\n  D9-G1: {'PASS' if not n_fail else 'FAIL'} "
          f"({len(gates) - n_fail}/{len(gates)} checks).")

    print("\nLIMITATIONS (printed, not just in the docstring): "
          "PARTIAL CONSTRUCTIONAL OVERLAP -- mean_abs_delta_b and rho_b are "
          "both functions of the SAME delta_b, so this is not an independent "
          "control; it removes the overall-magnitude component of delta_b and "
          "nothing else.  A surviving (or failed) p_spec_adj is NOT evidence "
          "that delta_b's influence is gone or absent -- only that its "
          "overall magnitude does or does not account for the ranking.  "
          "mean|delta| is scale-only and blind to sign, so a shift confound "
          "operating through heteroscedasticity or sign pattern is neither "
          "removed nor ruled out.  Leave-one-out residuals are exact but not "
          "exchangeable draws from a common population: they come from 78 "
          "overlapping fits on the same 78 points, and a background at a "
          "leverage point gets a larger LOO residual mechanically, so a small "
          "p_spec_adj is a rank count and not a calibrated tail probability.  "
          "The 96 rho_b share one y-vector and are mutually correlated; that "
          "is disclosed, not modelled.  NOTHING HERE IS A DECISION RULE AND "
          "NOTHING FROZEN IS REDEFINED.  No resampling was performed in this "
          "task: no bootstrap, no permutation, N_BOOT/N_PERM not read.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
