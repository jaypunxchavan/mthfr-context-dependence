"""
Task G1 (review-triage): global vs. specific epistasis decomposition.

WHY THIS EXISTS (REVIEW_TRIAGE.md item 23)
-------------------------------------------
G1a: How much of e.b's variance is explained by a monotone nonlinear
function of w.fitness alone? If most of it, the atlas's "interaction" is
substantially global/threshold epistasis -- which a single-site masked-
marginal model was never mechanistically positioned to capture. This
reframes the fair test as: does ESM-2 predict the SPECIFIC residual left
after removing global epistasis, not the raw e.b?

PRE-REGISTERED DESIGN (stated before running -- AGENTS.md §6)
--------------------------------------------------------------
Analysis set (stated explicitly, n reported at every drop -- AGENTS.md §5):
  phase5_analysis_table rows with non-null GI_folinate_independent (e.b),
  non-null delta_esm, and matched atlas w.fitness (raw
  data/raw/mthfrModel/results/folate_response_model5.csv, joined
  hgvs -> hgvs_pro, same join as script 51/F1b).

PART 1 -- variance share (G1a primary statistic):
  Cross-fitted isotonic R^2 of e.b on w.fitness, using the house function
  crossfit_isotonic_by_position (n_folds=5, seed=0): held-out positions,
  so the reported R^2 is out-of-sample and cannot be inflated by the
  calibration memorising its own rows. Also reported for context:
  (a) linear OLS R^2 (w.fitness alone, no nonlinearity),
  (b) in-sample isotonic R^2 -- labeled CEILING, optimistic, not the claim,
  (c) Spearman(e.b, w.fitness).
  CI: position-cluster bootstrap (positions resampled with replacement,
  N_BOOT draws) on the FIXED held-out predictions -- this conditions on
  the fitted calibration (disclosed in LIMITATIONS); it does not re-fit
  isotonic inside each draw.

  Pre-registered variance-share bands (conservative reading of "most of
  it", fixed before running):
    R^2_cf >= 0.50  -> MOST-GLOBAL
    0.25 <= R^2_cf < 0.50 -> SUBSTANTIAL-GLOBAL
    R^2_cf < 0.25  -> LIMITED-GLOBAL

PART 2 -- the fair test (does ESM-2 predict the SPECIFIC residual):
  residual = e.b - cross-fitted prediction (out-of-fold by construction).
  Statistic: Spearman(delta_ESM, residual), position-cluster bootstrap CI
  (N_BOOT) + POSITION-level sign-flip randomization null on delta_ESM
  (one Rademacher sign per residue position, shared by all its variants;
  N_PERM draws; identity check: all-+1 reproduces the observed statistic
  to <1e-12 or sys.exit(1)).
  Paired comparison (AGENTS.md §3 -- effect size alongside significance):
  position-cluster bootstrap of the DIFFERENCE
  Spearman(delta_ESM, residual) - Spearman(delta_ESM, raw e.b) on the same
  rows, so we can say whether removing global epistasis weakens, leaves, or
  strengthens ESM-2's signal.

  Pre-registered verdict for PART 2:
    SURVIVES iff sign-flip p < 0.05 AND the cluster-bootstrap 95% CI for
    Spearman(delta_ESM, residual) excludes 0.
    Otherwise NOT-DETECTED on this analysis set. No retuning after results.

Null type: ASSOCIATION randomization (sign symmetry of the pairing at
position granularity), not re-derivation -- e.b and the cross-fitted
calibration are fixed; we randomize whether delta_ESM's signed blocks line
up with the residual's signed blocks. Labeled as such in the output.
p is bounded by 1/N_PERM and is the primary claim; no z-scores.

RECONCILIATION (AGENTS.md §5): Spearman(delta_ESM, raw e.b) on this set is
printed next to script 32's on-disk published-e.b value (-0.070705) and its
n, so any set difference is visible, not silent.

Env: N_BOOT (default 2000), N_PERM (default 10000). Smoke with 100/200.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import (_spearman, crossfit_isotonic_by_position,
                               position_cluster_bootstrap)

N_BOOT = int(os.environ.get("N_BOOT", 2000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p, n):
    return f"<{1.0 / n:.6f}" if p == 0 else f"{p:.6f}"


def r2(y, yhat):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    g = np.isfinite(y) & np.isfinite(yhat)
    ss_res = float(((y[g] - yhat[g]) ** 2).sum())
    ss_tot = float(((y[g] - y[g].mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot


if __name__ == "__main__":
    # ---------------- data + analysis set (every drop reported) ----------------
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    n0 = len(df)
    df = df.dropna(subset=["GI_folinate_independent", "delta_esm"])
    n1 = len(df)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv",
                      usecols=["hgvs", "w.fitness"]).rename(
                          columns={"hgvs": "hgvs_pro"})
    df = df.merge(raw, on="hgvs_pro", how="left")
    df = df.dropna(subset=["w.fitness"]).reset_index(drop=True)
    n2 = len(df)
    n_pos = df["position"].nunique()
    print(f"phase5 rows: {n0}")
    print(f"  non-null e.b + delta_esm: {n1}  (dropped {n0 - n1})")
    print(f"  + matched atlas w.fitness: {n2}  (dropped {n1 - n2})")
    print(f"Analysis set: {n2} variants, {n_pos} positions")
    if n2 < 1000 or n_pos < 100:
        print("*** DATA GATE FAILED: analysis set unexpectedly small. sys.exit(1)")
        sys.exit(1)

    y = df["GI_folinate_independent"].to_numpy(float)
    w = df["w.fitness"].to_numpy(float)
    dv = df["delta_esm"].to_numpy(float)

    # ---------------- PART 1: variance share ----------------
    print("\n" + "=" * 74)
    print("PART 1 (G1a): variance in e.b explained by a monotone function of w.fitness")
    print("=" * 74)
    cf = crossfit_isotonic_by_position(df, "position", "w.fitness",
                                       "GI_folinate_independent",
                                       n_folds=5, seed=SEED)
    cf = np.asarray(cf, float)
    r2_cf = r2(y, cf)
    # linear OLS
    b = np.polyfit(w, y, 1)
    r2_lin = r2(y, np.polyval(b, w))
    # in-sample isotonic ceiling -- MUST mirror the house function's
    # increasing="auto" (Spearman(w.fitness, e.b) = -0.239 is decreasing;
    # forcing increasing=True fits a near-flat curve and understates the
    # ceiling. Smoke-stage bug, fixed before the full run -- disclosed.)
    from sklearn.isotonic import IsotonicRegression
    iso = IsotonicRegression(y_min=y.min(), y_max=y.max(), increasing="auto")
    r2_insample = r2(y, iso.fit_transform(w, y))
    rho_wf = _spearman(w, y)
    print(f"  cross-fitted isotonic R^2 (PRIMARY)  = {r2_cf:.4f}   (out-of-sample)")
    print(f"  linear OLS R^2 (w.fitness, no nonlin) = {r2_lin:.4f}")
    print(f"  in-sample isotonic R^2 (CEILING)      = {r2_insample:.4f}  (optimistic)")
    print(f"  Spearman(w.fitness, e.b)              = {rho_wf:+.4f}")
    band = ("MOST-GLOBAL" if r2_cf >= 0.5 else
            "SUBSTANTIAL-GLOBAL" if r2_cf >= 0.25 else "LIMITED-GLOBAL")
    print(f"  pre-registered band: R^2_cf -> {band}  "
          f"(>=0.50 MOST / >=0.25 SUBSTANTIAL / else LIMITED)")

    # cluster-bootstrap CI on the fixed held-out predictions
    tmp = pd.DataFrame({"position": df["position"], "eb": y, "cf": cf})
    rows_p1 = []
    rng = np.random.default_rng(SEED)
    pos_idx = {p: tmp.index[tmp["position"] == p].to_numpy()
               for p in tmp["position"].unique()}
    keys = np.array(list(pos_idx.keys()))
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        draw = rng.choice(keys, size=len(keys), replace=True)
        idx = np.concatenate([pos_idx[p] for p in draw])
        boot[i] = r2(tmp["eb"].to_numpy()[idx], tmp["cf"].to_numpy()[idx])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"  cross-fitted R^2 cluster bootstrap (N_BOOT={N_BOOT}): "
          f"CI=[{lo:.4f},{hi:.4f}]  (positions resampled, predictions fixed)")
    rows_p1.append({"stat": "r2_crossfit_isotonic", "value": r2_cf,
                    "ci_lo": lo, "ci_hi": hi, "band": band})
    rows_p1.append({"stat": "r2_linear", "value": r2_lin})
    rows_p1.append({"stat": "r2_insample_isotonic_ceiling", "value": r2_insample})
    rows_p1.append({"stat": "spearman_w_fitness_eb", "value": rho_wf})

    # ---------------- PART 2: specific residual ----------------
    print("\n" + "=" * 74)
    print("PART 2: does ESM-2 predict the SPECIFIC residual after global epistasis?")
    print("=" * 74)
    resid = y - cf
    df2 = pd.DataFrame({"position": df["position"], "delta": dv,
                        "resid": resid, "eb": y})
    print(f"  residual: e.b - crossfit-isotonic(w.fitness); "
          f"sd(resid)={resid.std():.4f} vs sd(e.b)={y.std():.4f} "
          f"({resid.std() / y.std():.3f} of raw scale)")

    b1 = position_cluster_bootstrap(df2, "position", "delta", "resid",
                                    n_boot=N_BOOT, seed=SEED)
    print(f"  Spearman(delta_ESM, residual) = {b1['observed_rho']:+.4f}  "
          f"CI=[{b1['ci_lo']:+.4f},{b1['ci_hi']:+.4f}]  "
          f"p_boot={pstr(b1['p_boot'], N_BOOT)}  (cluster, N_BOOT={N_BOOT})")

    rho_raw = _spearman(dv, y)
    print(f"  Spearman(delta_ESM, raw e.b)   = {rho_raw:+.4f}  "
          f"(same rows, same set)")
    ref = pd.read_csv(PROC / "task32_delta_esm_primary.csv")
    ref_row = ref[ref["quantity"] == "signed, published e.b"].iloc[0]
    print(f"  reconciliation vs script 32 on-disk: value={ref_row['value']:+.6f} "
          f"n={int(ref_row['n'])}  |diff|={abs(rho_raw - ref_row['value']):.2e}")

    # paired difference: resid vs raw, cluster bootstrap.
    # SIGNAL STRENGTH = |rho|: both correlations are negative here, so a more
    # negative rho is a STRONGER signal. A naive signed-difference label would
    # invert the plain-language verdict (smoke run showed exactly that:
    # signed diff -0.0748 labeled "WEAKENS" while |rho| grew 0.0707 -> 0.1455).
    # Bug fixed pre-full-run and disclosed in the log. We bootstrap the
    # MAGNITUDE difference directly and verify sign stability of both rhos.
    rng2 = np.random.default_rng(SEED + 1)
    pos_idx2 = {p: df2.index[df2["position"] == p].to_numpy()
                for p in df2["position"].unique()}
    keys2 = np.array(list(pos_idx2.keys()))
    xa, ya, yb = df2["delta"].to_numpy(), df2["resid"].to_numpy(), df2["eb"].to_numpy()
    diffs = np.empty(N_BOOT)
    sign_stable = 0
    for i in range(N_BOOT):
        draw = rng2.choice(keys2, size=len(keys2), replace=True)
        idx = np.concatenate([pos_idx2[p] for p in draw])
        r_res, r_raw = _spearman(xa[idx], ya[idx]), _spearman(xa[idx], yb[idx])
        diffs[i] = abs(r_res) - abs(r_raw)
        if r_res < 0 and r_raw < 0:
            sign_stable += 1
    d_obs = abs(b1["observed_rho"]) - abs(rho_raw)
    d_lo, d_hi = np.percentile(diffs, [2.5, 97.5])
    print(f"  paired magnitude difference |resid| - |raw|: {d_obs:+.4f}  "
          f"CI=[{d_lo:+.4f},{d_hi:+.4f}]  "
          f"(both rhos negative in {sign_stable}/{N_BOOT} draws)")
    print(f"    -> removing global epistasis "
          f"{'STRENGTHENS' if d_lo > 0 else 'WEAKENS' if d_hi < 0 else 'does not reliably change'} "
          f"the |delta_ESM| signal magnitude")

    # position-level sign-flip association null on delta_ESM
    print(f"\n  position-level sign-flip ASSOCIATION null on delta_ESM ({N_PERM} draws):")
    pos_codes, _ = pd.factorize(df2["position"])
    n_pos2 = len(np.unique(pos_codes))

    def stat(x, yy):
        return _spearman(x, yy)

    obs = stat(dv, resid)
    # identity check (AGENTS.md §4): all +1 must reproduce observed
    ones = np.ones(n_pos2)
    ident = stat(dv * ones[pos_codes], resid)
    if not abs(ident - obs) < 1e-12:
        print(f"    *** IDENTITY CHECK FAILED: |{ident:.12f} - {obs:.12f}| "
              f">= 1e-12. sys.exit(1)")
        sys.exit(1)
    negs = np.ones(n_pos2) * -1
    neg = stat(dv * negs[pos_codes], resid)
    if not abs(neg + obs) < 1e-12:
        print(f"    *** IDENTITY CHECK FAILED (all -1): |{neg:.12f} + {obs:.12f}| "
              f">= 1e-12. sys.exit(1)")
        sys.exit(1)
    print(f"    identity: all+1 == obs ({ident:+.12f}), "
          f"all-1 == -obs ({neg:+.12f})  -> OK")
    rng3 = np.random.default_rng(SEED + 2)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        s = rng3.choice([-1.0, 1.0], size=n_pos2)
        null[i] = stat(dv * s[pos_codes], resid)
    p_val = float((np.abs(null) >= abs(obs)).mean())
    centred = abs(null.mean()) < 3 * null.std() / np.sqrt(N_PERM)
    print(f"    observed={obs:+.4f}  null mean={null.mean():+.4f}  "
          f"sd={null.std():.4f}  p={pstr(p_val, N_PERM)}")
    print(f"    null-centring: mean {'IS' if centred else 'is NOT'} consistent "
          f"with zero (3 SE)")
    verdict = "SURVIVES" if (p_val < 0.05 and
                             not (b1["ci_lo"] <= 0 <= b1["ci_hi"])) else "NOT-DETECTED"
    print(f"    pre-registered verdict: {verdict}  "
          f"(p<0.05: {p_val < 0.05}; CI excludes 0: "
          f"{not (b1['ci_lo'] <= 0 <= b1['ci_hi'])})")

    # ---------------- save ----------------
    rows = rows_p1 + [
        {"stat": "spearman_delta_resid", "value": b1["observed_rho"],
         "ci_lo": b1["ci_lo"], "ci_hi": b1["ci_hi"], "p_boot": b1["p_boot"]},
        {"stat": "spearman_delta_raw_eb", "value": rho_raw},
        {"stat": "paired_magdiff_resid_minus_raw", "value": d_obs,
         "ci_lo": d_lo, "ci_hi": d_hi},
        {"stat": "signflip_null_mean", "value": float(null.mean())},
        {"stat": "signflip_p", "value": p_val, "n_perm": N_PERM},
        {"stat": "n_variants", "value": n2},
        {"stat": "n_positions", "value": n_pos2},
    ]
    out = PROC / "task53_g1_global_specific.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved {out}")
    print("\nPART 2 null is an ASSOCIATION (sign-symmetry) randomization at position")
    print("granularity; e.b/calibration fixed. p bounded by 1/N_PERM, primary claim.")
    print("A sign-flip null on a signed variable centers on zero by construction; it")
    print("does not rule out confounding (AGENTS.md §4). Cross-fitted R^2 CI")
    print("conditions on fixed fold predictions (folds from seed 0; isotonic not")
    print("re-fit inside bootstrap draws). Isotonic is the monotone class the review")
    print("named; other monotone estimators could give slightly different R^2.")
    print("w.fitness is the ATLAS's own column, joined on hgvs -> hgvs_pro; join loss")
    print(f"= {n1 - n2} rows (reported above), not silently absorbed.")
