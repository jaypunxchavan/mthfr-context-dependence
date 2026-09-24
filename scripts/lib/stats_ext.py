"""Additions supporting scripts 32-36.

DELIBERATELY A SEPARATE MODULE, not an edit to stats.py. An out-of-order
deploy script previously overwrote stats.py wholesale and silently dropped
crossfit_isotonic_stratified/within_group (see commit 25033ff). Adding new
machinery in its own file means a deploy can never clobber the existing,
load-bearing functions.

Contents:
  wls_line_se                       analytic SE of the WLS intercept/slope,
                                    i.e. SE(e_b) and SE(e_r)
  rebuild_interaction_fit           the two-pass own-context fit that scripts
                                    20/21/24/26/28 each re-inline; factored
                                    out so 33/35 cannot drift from it
  paired_metric_difference_bootstrap  cluster bootstrap for MAE/RMSE
                                    differences between two predictors
  group_mean_bootstrap              cluster bootstrap for a group mean
"""
import numpy as np
import pandas as pd

from scripts.lib.own_context import (fit_single_arm, fit_interaction,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS,
                                     MT_SCORE_COLS, MT_SE_COLS)


def wls_line_se(se, x=CONCS, valid=None):
    """Analytic standard errors of the WLS intercept and slope.

    For y ~ 1 + x with KNOWN per-point error (weights w = 1/se^2), the
    coefficient covariance is (X'WX)^-1 exactly -- no residual-scale
    estimation, no t-distribution. With
        S0 = sum w,  S1 = sum w*x,  S2 = sum w*x^2,  det = S0*S2 - S1^2
    the variances are Var(intercept) = S2/det and Var(slope) = S0/det.

    This is the same known-variance Gaussian assumption fitModels.R already
    makes when it fits with dnorm(..., sd = se); it introduces no new
    assumption beyond the atlas's own. If the reported se are themselves
    optimistic, these SEs inherit that optimism -- stated, not hidden.

    Returns (se_intercept, se_slope), NaN where the fit is unusable
    (>2 missing points), matching wls_line's own convention.
    """
    se = np.asarray(se, dtype=float)
    if valid is None:
        valid = np.isfinite(se) & (se > 0)
    w = np.where(valid, 1.0 / np.where(valid, se, 1.0) ** 2, 0.0)
    xx = np.broadcast_to(np.asarray(x, dtype=float), se.shape)
    S0 = w.sum(axis=1)
    S1 = (w * xx).sum(axis=1)
    S2 = (w * xx ** 2).sum(axis=1)
    det = S0 * S2 - S1 ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        se_b = np.where(det > 0, np.sqrt(np.abs(S2 / det)), np.nan)
        se_r = np.where(det > 0, np.sqrt(np.abs(S0 / det)), np.nan)
    bad = (~valid).sum(axis=1) > 2
    se_b = np.where(bad, np.nan, se_b)
    se_r = np.where(bad, np.nan, se_r)
    return se_b, se_r


def rebuild_interaction_fit(raw):
    """Two-pass own-context fit, exactly as scripts 17/20/21/24/26/28 do it.

    Returns a dict with the pieces every downstream null needs: the WT-arm
    fit, the corrected interaction fit, the per-point residual/se/valid
    matrices, and the row index of the A222V reference line.
    """
    W = raw[WT_SCORE_COLS].to_numpy(float)
    Wse = raw[WT_SE_COLS].to_numpy(float)
    M = raw[MT_SCORE_COLS].to_numpy(float)
    Mse = raw[MT_SE_COLS].to_numpy(float)

    w = fit_single_arm(W, Wse)
    w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(raw["hgvs"].to_numpy() == "p.Ala222Val")[0][0])

    e1 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"],
                         w_mean, w["fitness"][i222], w["remediation"][i222])
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1["e_r"][keep])
    e2 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"],
                         w_mean, w["fitness"][i222], w["remediation"][i222],
                         correction=(cb, cr))
    return {"w": w, "e2": e2, "M_se": Mse, "resid": e2["resid"],
            "valid": e2["valid"], "i222": i222, "correction": (cb, cr)}


def _mae(a, b):
    return float(np.nanmean(np.abs(np.asarray(a, float) - np.asarray(b, float))))


def _rmse(a, b):
    return float(np.sqrt(np.nanmean((np.asarray(a, float) - np.asarray(b, float)) ** 2)))


_METRICS = {"mae": _mae, "rmse": _rmse}


def paired_metric_difference_bootstrap(df, cluster_col, pred_a, pred_b,
                                       target_col, metric="mae",
                                       n_boot=2000, seed=0):
    """Cluster bootstrap of metric(pred_b) - metric(pred_a) on the same rows.

    Needed because rank correlation CANNOT separate a no-interaction
    phenotype model from the score it is built on: adding or multiplying a
    fixed background constant leaves rank order untouched (the same
    degeneracy script 16 found for model_B). A scale-sensitive metric is
    the only way to compare them, so the comparison needs its own interval.

    Negative difference = pred_b has LOWER error = pred_b is better.
    """
    f = _METRICS[metric]
    d = df[[cluster_col, pred_a, pred_b, target_col]].dropna().reset_index(drop=True)
    clusters = d[cluster_col].unique()
    idx_by = {c: d.index[d[cluster_col] == c].to_numpy() for c in clusters}
    a, b, y = (d[pred_a].to_numpy(), d[pred_b].to_numpy(), d[target_col].to_numpy())

    observed = f(b, y) - f(a, y)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        j = np.concatenate([idx_by[c] for c in drawn])
        boot[i] = f(b[j], y[j]) - f(a[j], y[j])
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return {"observed_diff": observed, "ci_lo": float(lo), "ci_hi": float(hi),
            "metric_a": f(a, y), "metric_b": f(b, y),
            "n_rows": len(d), "n_clusters": len(clusters)}


def group_mean_bootstrap(df, cluster_col, value_col, n_boot=2000, seed=0):
    """Cluster bootstrap of a plain group mean, resampling positions."""
    d = df[[cluster_col, value_col]].dropna().reset_index(drop=True)
    if len(d) == 0:
        return None
    clusters = d[cluster_col].unique()
    idx_by = {c: d.index[d[cluster_col] == c].to_numpy() for c in clusters}
    v = d[value_col].to_numpy()

    observed = float(np.mean(v))
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        j = np.concatenate([idx_by[c] for c in drawn])
        boot[i] = np.mean(v[j])
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return {"mean": observed, "ci_lo": float(lo), "ci_hi": float(hi),
            "n_rows": len(d), "n_clusters": len(clusters)}
