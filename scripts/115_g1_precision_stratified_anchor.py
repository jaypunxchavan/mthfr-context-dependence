"""
Script 115 (task G1, Group G) -- precision-stratified anchor: does
|rho(delta_ESM, own_e.b)| rise as the per-variant precision of own_e.b
improves?

PRE-REGISTERED: this docstring was written before the first run; the
delta-method formula, quintile construction, verdict rule, gates, and
sensitivities below were all fixed before any number produced here was
seen (AGENTS sec 6).  Nothing here is selected after results.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group G, task G1.

G1a -- PER-VARIANT SE ON own_e.b BY THE DELTA METHOD
----------------------------------------------------
The construction (scripts/lib/own_context.py, reproduced verbatim via
stats_ext.rebuild_interaction_fit, which is scripts 17/20/21/24/26/28's
own two-pass fit):

    expected_c = sm_c * A_c [+ cb(wf) + cr(wf)*c]
    resid_c    = m_c - expected_c
    e_b        = SUM_c h_c * resid_c      (WLS intercept of resid ~ 1 + c,
                                           weights 1/m_se^2, valid points)

with, per variant v and condition c in {12,25,100,200}:
    A_c  = a_f + c * a_r          (A222V reference line = row i222's own
                                   WT-arm fit -- script 17 L34-35)
    sm_c = b_w + c * r_w          (WT-arm line)  when w.post > 0.5,
         = w_mean                 (unweighted mean WT score) otherwise
    wf   = b_w (the fitted WT-arm intercept that the correction curves
           cb, cr are a function of)
    h_c  = w_c * (S2 - S1*c) / det  (M-arm WLS weights w_c = 1/m_se_c^2)

Delta method (first order), with the independent parameter sources
theta = (m_1..m_4, b_w, r_w, w_mean, a_f, a_r):

    Var(e_b) = SUM_c h_c^2 * m_se_c^2                    [MEASUREMENT]
             + Var(b_w)   * (SUM_c h_c * dExp_c/d b_w)^2
             + Var(r_w)   * (SUM_c h_c * dExp_c/d r_w)^2
             + 2*Cov(b_w,r_w) * (SUM h d_b)(SUM h d_r)   [WT ARM]
             + Var(w_mean) * (SUM_{use_line=0} h_c * A_c)^2
                                                        (non-use_line rows)
             + Var(a_f)   * (SUM_c h_c * sm_c)^2
             + Var(a_r)   * (SUM_c h_c * sm_c * c)^2
             + 2*Cov(a_f,a_r) * (SUM h sm)(SUM h sm*c)   [A222V LINE]

where, on use_line rows:
    dExp_c/d b_w = A_c + cb'(wf) + cr'(wf)*c
    dExp_c/d r_w = c * A_c
and on non-use_line rows (sm = w_mean, independent of b_w):
    dExp_c/d b_w = cb'(wf) + cr'(wf)*c
    dExp_c/d r_w = 0
    dExp_c/d w_mean = A_c

Var/Cov of each WLS line = (X'WX)^-1 of that row's own fit with KNOWN
per-point errors (Var(b)=S2/det, Var(r)=S0/det, Cov=-S1/det), the same
known-variance assumption fitModels.R already makes.  Var(w_mean) =
SUM finite(Wse^2) / n_finite^2 (unweighted mean, as fitModels.R uses).
cb', cr' by central difference on the fitted callables,
eps = 1e-6*(1+|wf|) (the callables are degree-4 polynomial + matched
linear tail -- differentiable at the knot by construction).

    PRIMARY  se_eb_delta = sqrt(MEASUREMENT + WT ARM + A222V LINE)
    Reported decomposition: the three component variances (shares).
    SENSITIVITY (reported, never selected over the primary):
      se_eb_delta_noA = sqrt(MEASUREMENT + WT ARM) -- drops the A222V
      reference line on script 17's own printed argument (its error is
      common-mode across the dataset).  Both the Spearman correlation
      between the two SEs and the full G1b/G1c result under the noA
      partition are printed alongside the primary; whichever agrees
      with the task's verdict branches is NOT chosen -- both are shown.

G1b -- QUINTILES AND THE ANCHOR WITHIN EACH
-------------------------------------------
  * Quintiles by se_eb_delta over the 10,757-row analysis base
    (task32 dropna(own_e_b, GI_folinate_independent, delta_esm)),
    rank-based qcut, Q1 = most precise (smallest SE) ... Q5 = least.
    Boundaries, n, positions, mean/median SE per quintile printed.
  * Within each: rho(delta_esm, own_e_b) with the project's standard
    position-cluster bootstrap CI (cluster = position, resample, seed
    0, N_BOOT env, default 10000), p_boot reported as primary.

G1c -- VERDICT RULE (pre-stated)
--------------------------------
Let step_i = |rho_Q(i+1)| - |rho_Q(i)|, i = 1..4 (precision worsens
along the index); k = number of steps with step_i <= 0.
  * k = 4  -> the task's FIRST branch: |rho| rises monotonically as
    precision improves -> "direct empirical evidence the anchor is
    real signal attenuated by noise -- a positive, affirmative finding
    that does not depend on any disattenuation assumption."
  * k = 0  -> the task's SECOND branch (|rho| flat-to-rising with
    imprecision, i.e. it does NOT rise with precision) -> stated
    plainly as such.
  * 1 <= k <= 3 -> neither pre-stated branch holds; the actual step
    pattern, the point values, and the adjacent CI overlaps are
    printed and described factually, without forcing a branch.
  The same k is computed under the noA sensitivity partition and
  printed next to the primary; the PRIMARY k decides the wording.

GATES (failure -> print the exact mismatch, sys.exit(1)):
  G1  Recomputed own_e_b (rebuild_interaction_fit) matches
      own_context_metrics.csv AND task32's own_e_b on the analysis
      base to max|diff| < 1e-9 (the delta method propagates around
      the SAME e_b the anchor uses).
  G2  Analysis base = (10,757 rows, 654 positions); se_eb_delta
      finite on ALL of them (count of non-finite printed; 0 required).
  G3  The MEASUREMENT component reproduces task35's recorded se_e_b
      to max|diff| < 1e-9 on common rows (both come from
      wls_line_se on the same fit -- identity, not evidence).
  G4  Quintiles: exactly 5 non-empty groups, sizes printed.

LIMITATIONS (printed with the output, AGENTS sec 6):
  - First-order delta method: higher-order terms are dropped; the SE
    is APPROXIMATE by construction (the task's own wording).
  - Known-se Gaussian assumption inherited from the atlas's fitter;
    if reported se are optimistic these inherit that optimism
    (script 35's stats_ext docstring says the same).
  - On non-use_line rows, Cov(w_mean, b_w) is truncated to 0 (both
    are functions of the same four WT points) -- this makes those
    rows' SE slightly off in an unknown direction; the count of such
    rows is printed.
  - The A222V-line component is common-mode in expectation (script
    17's own note); it is INCLUDED in the primary because the task
    says propagate through the multiplicative-expectation
    construction, and dropped only in the disclosed sensitivity.
  - Quintile membership is estimated-SE membership: measurement
    error in the SE itself blurs the boundaries (attenuates any
    monotone pattern -- a bias against the positive branch).
  - Within-quintile rho is still a cross-sectional correlation on
    one dataset; monotonicity would be evidence, not proof.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/115_g1_precision_stratified_anchor.py  # smoke
  N_BOOT=10000 venv/bin/python3 scripts/115_g1_precision_stratified_anchor.py  # full
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib.own_context import CONCS, WT_SE_COLS
from scripts.lib.stats import position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit, wls_line_se

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel" / "results"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
OUT_VARIANTS = PROC / "task115_g1_variant_se.csv"
OUT_QUINT = PROC / "task115_g1_quintiles.csv"
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"G1 -- precision-stratified anchor (scripts/115)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ---- build the fit, exactly as scripts 17/35 -------------------------
    raw = pd.read_csv(RAW / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    w, e2 = fit["w"], fit["e2"]
    Mse, valid, resid = fit["M_se"], fit["valid"], fit["resid"]
    cb, cr = fit["correction"]
    i222 = fit["i222"]

    Wse = raw[WT_SE_COLS].to_numpy(float)
    b_w, r_w = w["fitness"], w["remediation"]
    w_mean = np.nanmean(raw[["w12.score", "w25.score", "w100.score",
                             "w200.score"]].to_numpy(float), axis=1)
    a_f, a_r = b_w[i222], r_w[i222]
    use_line = (w["post"] > 0.5) & np.isfinite(b_w)

    # ---- WLS covariances (known-se, (X'WX)^-1) ---------------------------
    def line_cov(se_mat):
        ok = np.isfinite(se_mat) & (se_mat > 0)
        wv = np.where(ok, 1.0 / np.where(ok, se_mat, 1.0) ** 2, 0.0)
        S0 = wv.sum(axis=1)
        S1 = (wv * CONCS[None, :]).sum(axis=1)
        S2 = (wv * CONCS[None, :] ** 2).sum(axis=1)
        det = S0 * S2 - S1 ** 2
        with np.errstate(divide="ignore", invalid="ignore"):
            vb = np.where(det != 0, S2 / det, np.nan)
            vr = np.where(det != 0, S0 / det, np.nan)
            cv = np.where(det != 0, -S1 / det, np.nan)
        return vb, vr, cv

    vb_w, vr_w, cv_wr = line_cov(Wse)
    vb_a, vr_a, cv_ar = line_cov(Wse[i222][None, :])
    vb_a, vr_a, cv_ar = vb_a[0], vr_a[0], cv_ar[0]
    n_w_ok = np.isfinite(Wse).sum(axis=1)
    with np.errstate(invalid="ignore"):
        v_wmean = np.where(
            n_w_ok > 0,
            np.nansum(Wse ** 2, axis=1) / np.maximum(n_w_ok, 1) ** 2,
            np.nan)

    # ---- M-arm intercept weights h_c -------------------------------------
    w_m = np.where(valid, 1.0 / np.where(valid, Mse, 1.0) ** 2, 0.0)
    S0m = w_m.sum(axis=1)
    S1m = (w_m * CONCS[None, :]).sum(axis=1)
    S2m = (w_m * CONCS[None, :] ** 2).sum(axis=1)
    det_m = S0m * S2m - S1m ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        h = w_m * (S2m[:, None] - S1m[:, None] * CONCS[None, :]) / \
            np.where(det_m != 0, det_m, np.nan)[:, None]
    h = np.where(np.isfinite(h), h, 0.0)

    # ---- correction derivatives (central difference) ---------------------
    wf = b_w
    eps = 1e-6 * (1.0 + np.abs(wf))
    cbp = (cb(wf + eps) - cb(wf - eps)) / (2 * eps)
    crp = (cr(wf + eps) - cr(wf - eps)) / (2 * eps)
    cbp, crp = np.nan_to_num(cbp), np.nan_to_num(crp)

    A_line = a_f + CONCS[None, :] * a_r                     # (n, 4)
    sm = np.where(use_line[:, None],
                  b_w[:, None] + CONCS[None, :] * r_w[:, None],
                  w_mean[:, None])

    # ---- gradients --------------------------------------------------------
    dexp_db = np.where(use_line[:, None],
                       A_line + cbp[:, None] + crp[:, None] * CONCS[None, :],
                       cbp[:, None] + crp[:, None] * CONCS[None, :])
    dexp_dr = np.where(use_line[:, None],
                       CONCS[None, :] * A_line, 0.0)
    Gm = (h ** 2 * np.where(valid, Mse, 0.0) ** 2).sum(axis=1)   # measurement
    gb = -(h * dexp_db).sum(axis=1)
    gr = -(h * dexp_dr).sum(axis=1)
    gw = -(h * np.where(use_line[:, None], 0.0, A_line)).sum(axis=1)
    Ga = ((h * sm).sum(axis=1), (h * sm * CONCS[None, :]).sum(axis=1))

    v_wt = (vb_w * gb ** 2 + vr_w * gr ** 2 + 2 * cv_wr * gb * gr
            + v_wmean * gw ** 2)
    v_av = (vb_a * Ga[0] ** 2 + vr_a * Ga[1] ** 2
            + 2 * cv_ar * Ga[0] * Ga[1])
    se_delta = np.sqrt(Gm + v_wt + v_av)
    se_noA = np.sqrt(Gm + v_wt)
    se_meas = np.sqrt(Gm)
    # SE of an undefined e_b is undefined: rows with <=1 valid M point have
    # h == 0 by construction (det_m == 0) and would otherwise print a
    # meaningless 0.  They are never in the analysis base (e_b NaN); this
    # keeps the reported min meaningful over the full raw file.
    undef = ~np.isfinite(e2["e_b"])
    se_delta[undef] = np.nan
    se_noA[undef] = np.nan
    se_meas[undef] = np.nan

    # ---- G1: e_b identity -------------------------------------------------
    own = pd.read_csv(PROC / "own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    j = pd.DataFrame({"hgvs_pro": raw["hgvs"],
                      "rebuild_eb": e2["e_b"]}).merge(
        own, on="hgvs_pro", how="left")
    both = j[np.isfinite(j["rebuild_eb"]) & np.isfinite(j["own_e_b"])]
    d1 = float(np.abs(both["rebuild_eb"] - both["own_e_b"]).max())
    if d1 > 1e-9:
        gfail(f"G1 FAIL: rebuild own_e_b vs own_context_metrics "
              f"max|diff| = {d1!r} > 1e-9 (n={len(both)})")
    print(f"  G1a PASS: recomputed e_b == recorded own_e_b, "
          f"max|diff| = {d1:.3e} over {len(both)} rows")

    # ---- analysis base ----------------------------------------------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G2 FAIL: base = ({len(base)}, {base['position'].nunique()}), "
              f"expected (10757, 654)")
    chk = base[["hgvs_pro", "own_e_b"]].merge(
        own.rename(columns={"own_e_b": "own_ref"}), on="hgvs_pro",
        how="left")
    if chk["own_ref"].isna().any():
        gfail(f"G2 FAIL: {int(chk['own_ref'].isna().sum())} base rows "
              f"absent from own_context_metrics")
    d2 = float(np.abs(chk["own_e_b"] - chk["own_ref"]).max())
    if d2 > 1e-9:
        gfail(f"G2 FAIL: task32 own_e_b vs recorded own_e_b "
              f"max|diff| = {d2!r} > 1e-9")
    se_df = pd.DataFrame({"hgvs_pro": raw["hgvs"],
                          "se_eb_delta": se_delta,
                          "se_eb_noA": se_noA,
                          "se_eb_meas": se_meas})
    base = base.merge(se_df, on="hgvs_pro", how="left")
    nbad = int(base["se_eb_delta"].isna().sum())
    if nbad:
        gfail(f"G2 FAIL: {nbad} analysis-base rows have non-finite "
              f"se_eb_delta")
    print(f"  G2 PASS: base (10757, 654); se_eb_delta finite on all "
          f"10757 rows; task32 own_e_b == recorded (max|diff| "
          f"{d2:.3e})")

    # ---- G3: measurement component vs recorded se_e_b ---------------------
    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")[
        ["hgvs_pro", "se_e_b"]]
    k = base.merge(t35, on="hgvs_pro", how="inner")
    k = k[np.isfinite(k["se_eb_meas"]) & np.isfinite(k["se_e_b"])]
    d3 = float(np.abs(k["se_eb_meas"] - k["se_e_b"]).max())
    if d3 > 1e-9:
        gfail(f"G3 FAIL: measurement component vs task35 se_e_b "
              f"max|diff| = {d3!r} > 1e-9 (n={len(k)})")
    print(f"  G3 PASS: MEASUREMENT component == recorded se_e_b, "
          f"max|diff| = {d3:.3e} over {len(k)} common rows (identity)")

    # ---- quintiles --------------------------------------------------------
    for col, tag in [("se_eb_delta", "primary"), ("se_eb_noA", "noA")]:
        base[f"q_{tag}"] = pd.qcut(base[col].rank(method="first"), 5,
                                   labels=False) + 1
    sizes = base.groupby("q_primary").size()
    if len(sizes) != 5 or (sizes == 0).any():
        gfail(f"G4 FAIL: quintile sizes {sizes.to_dict()} (need 5 "
              f"non-empty)")
    print(f"  G4 PASS: 5 quintiles; sizes {sizes.to_dict()} "
          f"(Q1 = most precise)")

    banner("G1a -- SE decomposition (variance shares)", "-")
    mask = np.isfinite(se_delta)
    tot = se_delta[mask] ** 2
    for nm, arr in [("MEASUREMENT (m.se)", Gm), ("WT ARM (+correction)",
                                                 v_wt), ("A222V LINE", v_av)]:
        a2 = arr[mask]
        print(f"  {nm:26s} mean share of Var = "
              f"{np.mean(a2 / np.maximum(tot, 1e-300)):6.4f}")
    print(f"  se_eb_delta: min {np.nanmin(se_delta):.6f}  median "
          f"{np.nanmedian(se_delta):.6f}  max {np.nanmax(se_delta):.6f}")
    print(f"  se_eb_meas  : median {np.nanmedian(se_meas):.6f} "
          f"(the recorded se_e_b); delta-method median/recorded median = "
          f"{np.nanmedian(se_delta) / np.nanmedian(se_meas):.3f}x")
    print(f"  Spearman(se_delta, se_noA) = "
          f"{pd.Series(se_delta).corr(pd.Series(se_noA), method='spearman'):.6f}")
    print(f"  rows with w.post <= 0.5 (sm = w_mean branch): "
          f"{int((~use_line).sum())} of {len(use_line)}")
    moved = int((base["q_primary"] != base["q_noA"]).sum())
    print(f"  sensitivity: {moved} of {len(base)} variants change "
          f"quintile if the A222V line is dropped from the SE")

    # ---- G1b: anchor within quintiles -------------------------------------
    banner("G1b -- ANCHOR WITHIN EACH PRECISION QUINTILE", "-")
    print(f"  {'q':14s} {'n':>6s} {'pos':>5s} {'mean SE':>9s} "
          f"{'median SE':>10s} {'rho':>9s} {'95% CI':>22s} {'p_boot':>8s}")
    res = []
    for q in range(1, 6):
        gq = base[base["q_primary"] == q]
        r = position_cluster_bootstrap(gq, "position", "delta_esm",
                                       "own_e_b", N_BOOT, SEED)
        res.append(dict(q=q, n=len(gq), npos=int(gq["position"].nunique()),
                        mean_se=float(gq["se_eb_delta"].mean()),
                        med_se=float(gq["se_eb_delta"].median()),
                        rho=r["observed_rho"], lo=r["ci_lo"],
                        hi=r["ci_hi"], p=r["p_boot"]))
        print(f"  {'Q' + str(q) + ' (most->least)':14s} {len(gq):6d} "
              f"{int(gq['position'].nunique()):5d} "
              f"{gq['se_eb_delta'].mean():9.5f} "
              f"{gq['se_eb_delta'].median():10.5f} "
              f"{r['observed_rho']:+.6f} [{r['ci_lo']:+.6f},"
              f"{r['ci_hi']:+.6f}] {r['p_boot']:8.4f}")
    print("  (sensitivity, noA partition -- same table, reported not "
          "selected):")
    res_noa = []
    for q in range(1, 6):
        gq = base[base["q_noA"] == q]
        r = position_cluster_bootstrap(gq, "position", "delta_esm",
                                       "own_e_b", N_BOOT, SEED)
        res_noa.append(dict(q=q, rho=r["observed_rho"], lo=r["ci_lo"],
                            hi=r["ci_hi"]))
        print(f"    Q{q}: rho {r['observed_rho']:+.6f} "
              f"[{r['ci_lo']:+.6f},{r['ci_hi']:+.6f}]")

    # ---- G1c: verdict by the pre-stated rule ------------------------------
    banner("G1c -- VERDICT (pre-registered rule)", "-")
    rhos = np.array([r["rho"] for r in res])
    steps = np.abs(rhos[1:]) - np.abs(rhos[:-1])   # Q1 -> Q5
    ksteps = int((steps <= 0).sum())
    for i, s in enumerate(steps):
        print(f"  step Q{i + 1}->Q{i + 2} (precision worsening): "
              f"|rho| {abs(rhos[i]):.6f} -> {abs(rhos[i + 1]):.6f} "
              f"({s:+.6f})  {'OK (expected direction)' if s <= 0 else 'REVERSED'}")
    rhos_n = np.array([r["rho"] for r in res_noa])
    steps_n = np.abs(rhos_n[1:]) - np.abs(rhos_n[:-1])
    kn = int((steps_n <= 0).sum())
    print(f"  k (steps in expected direction): PRIMARY = {ksteps}/4; "
          f"noA sensitivity = {kn}/4")
    if ksteps == 4:
        print("  VERDICT (task branch 1, applies to the PRIMARY): "
              "|rho| rises monotonically as precision improves -> direct "
              "empirical evidence the anchor is real signal attenuated by "
              "noise; a positive, affirmative finding that does NOT "
              "depend on any disattenuation assumption.")
    elif ksteps == 0:
        print("  VERDICT (task branch 2, applies to the PRIMARY): "
              "|rho| is flat or falls as precision improves -> stated "
              "plainly: precision stratification does NOT show the anchor "
              "strengthening with target precision.")
    else:
        print(f"  VERDICT (neither pre-stated branch; k={ksteps}/4): the "
              "step pattern above is reported as-is -- the anchor does "
              "not rise monotonically with precision, and it does not "
              "fall monotonically either; see the individual steps and "
              "adjacent CI overlap for the factual pattern. No branch "
              "wording is forced.")

    pd.DataFrame(res).to_csv(OUT_QUINT, index=False)
    base[["hgvs_pro", "position", "se_eb_delta", "se_eb_noA",
          "se_eb_meas", "q_primary", "q_noA"]].to_csv(OUT_VARIANTS,
                                                      index=False)
    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. First-order delta method: approximate by construction;")
    print("     higher-order terms dropped.")
    print("  2. Known-se Gaussian assumption inherited from the atlas's")
    print("     fitter; optimistic reported se propagate optimistically.")
    print("  3. Non-use_line rows: Cov(w_mean, b_w) truncated to 0")
    print(f"     ({int((~use_line).sum())} rows, direction unknown).")
    print("  4. A222V-line variance is common-mode in expectation")
    print("     (script 17's note); included in primary, dropped only")
    print("     in the disclosed noA sensitivity.")
    print("  5. SE itself is estimated -> quintile boundaries are fuzzy,")
    print("     which attenuates monotone patterns (bias against the")
    print("     positive branch).")
    print("  6. Cross-sectional correlation within quintiles on one")
    print("     dataset: monotonicity would be evidence, not proof.")
    print(f"\nWrote {OUT_VARIANTS}\nWrote {OUT_QUINT}")
    print(f"SCRIPT 115 DONE ({time.time() - T0:.1f}s)")
