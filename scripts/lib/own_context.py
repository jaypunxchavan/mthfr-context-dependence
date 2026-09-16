"""Reimplementation of the atlas's folinate-response and genetic-interaction model.

This is a REPRODUCTION, not an independent replication: same data, same
estimator, different code. A match against the published e.b/e.r validates
that this code is correct -- it is a unit test, not corroborating evidence
for any biological claim.

Its purpose is to make the interaction statistic RECOMPUTABLE, which the
published values are not. A permutation test requires re-deriving the
statistic on each shuffled dataset; reading fitted values from a file
cannot support one.

Spec taken directly from fitModels.R:
  - concentrations are c(12,25,100,200) in the CODE (the paper text says
    12.5); the code's values are used here so fits are comparable
  - per-variant fit: score(c) = base + c*remediation, Gaussian likelihood
    with known se. That is exactly weighted least squares with w=1/se^2,
    so a closed-form vectorized solve replaces the per-variant optimizer
  - >2 missing points -> NA;  all scores <=0 -> (0,0)
  - priorProb 0.01; lod = logl - null.logl + priorLogOdds; post = logistic(lod)
  - expected(c) = (b_v + c*r_v) * (b_A222V + c*r_A222V), using the variant's
    weighted mean score instead of (b_v + c*r_v) when w.post <= 0.5
  - two-pass: fit raw e.b/e.r, fit a fitness-dependent correction via
    interpolate(), then REFIT with that correction inside expected()
"""
import numpy as np

CONCS = np.array([12.0, 25.0, 100.0, 200.0])
PRIOR_PROB = 0.01
PRIOR_LOG_ODDS = np.log(PRIOR_PROB / (1 - PRIOR_PROB))
LOGL_CUTOFF = -6.0
WT_SCORE_COLS = ["w12.score", "w25.score", "w100.score", "w200.score"]
WT_SE_COLS = ["w12.se", "w25.se", "w100.se", "w200.se"]
MT_SCORE_COLS = ["m12.score", "m25.score", "m100.score", "m200.score"]
MT_SE_COLS = ["m12.se", "m25.se", "m100.se", "m200.se"]


def _logistic(x):
    return 1.0 / (1.0 + np.exp(-x))


def _gauss_logl(pred, obs, se, valid):
    """Sum of dnorm(pred, obs, se, log=TRUE) over valid points, per row."""
    ll = -0.5 * np.log(2 * np.pi * se**2) - (pred - obs) ** 2 / (2 * se**2)
    return np.where(valid, ll, 0.0).sum(axis=1)


def wls_line(y, se, x, valid):
    """Vectorized weighted least squares of y ~ 1 + x, weights 1/se^2.

    Exact maximum likelihood for Gaussian error with known se, which is what
    fitModels.R optimizes numerically. Returns (intercept, slope, df).
    """
    w = np.where(valid, 1.0 / np.where(valid, se, 1.0) ** 2, 0.0)
    yy = np.where(valid, y, 0.0)
    xx = np.broadcast_to(x, y.shape)
    S0 = w.sum(axis=1)
    S1 = (w * xx).sum(axis=1)
    S2 = (w * xx**2).sum(axis=1)
    T0 = (w * yy).sum(axis=1)
    T1 = (w * xx * yy).sum(axis=1)
    det = S0 * S2 - S1**2
    with np.errstate(divide="ignore", invalid="ignore"):
        base = np.where(det != 0, (S2 * T0 - S1 * T1) / det, np.nan)
        slope = np.where(det != 0, (S0 * T1 - S1 * T0) / det, np.nan)
    return base, slope, valid.sum(axis=1) - 2


def fit_single_arm(score, se, concs=CONCS):
    """Fit base functionality + folinate remediation for one genetic background.

    Mirrors runFit() in fitModels.R including both special cases.
    Returns dict of arrays: fitness, remediation, logl, null_logl, lod, post, df.
    """
    valid = np.isfinite(score) & np.isfinite(se) & (se > 0)
    n_missing = (~valid).sum(axis=1)

    base, slope, df = wls_line(score, se, concs, valid)

    # null model: constant at the (unweighted) mean, no remediation -- matches
    # fitModels.R, which uses mean(score) rather than a weighted mean here
    with np.errstate(invalid="ignore"):
        mean_score = np.where(valid, score, np.nan)
        null_base = np.nanmean(mean_score, axis=1)
    safe_se = np.where(valid, se, 1.0)
    logl = _gauss_logl(base[:, None] + concs[None, :] * slope[:, None],
                       np.where(valid, score, 0.0), safe_se, valid)
    null_logl = _gauss_logl(np.broadcast_to(null_base[:, None], score.shape),
                            np.where(valid, score, 0.0), safe_se, valid)

    # special case: everything dead -> fitness 0, remediation 0
    all_dead = np.where(valid, score <= 0, True).all(axis=1) & (n_missing <= 2)
    dead_logl = _gauss_logl(np.zeros_like(score), np.zeros_like(score), safe_se, valid)
    base = np.where(all_dead, 0.0, base)
    slope = np.where(all_dead, 0.0, slope)
    logl = np.where(all_dead, dead_logl, logl)
    null_logl = np.where(all_dead, dead_logl, null_logl)

    # special case: more than two missing -> unusable
    bad = n_missing > 2
    for arr in (base, slope, logl, null_logl):
        arr[bad] = np.nan

    lod = logl - null_logl + PRIOR_LOG_ODDS
    return {"fitness": base, "remediation": slope, "logl": logl,
            "null_logl": null_logl, "lod": lod, "post": _logistic(lod), "df": df}


def interpolate_correction(x, y, bin_mids=None, bin_width=0.1, cutoff=1.2):
    """Port of interpolate() from fitModels.R.

    Running median of y against x in overlapping bins, a degree-4 polynomial
    fit to that smoothed curve, and a linear tail past `cutoff` matched to the
    polynomial's value and finite-difference slope there (prevents the
    polynomial diverging at high fitness). Returns a callable.
    """
    if bin_mids is None:
        bin_mids = np.round(np.arange(0, 1.5001, 0.01), 4)
    ok = np.isfinite(x) & np.isfinite(y)
    xv, yv = x[ok], y[ok]
    running = np.array([
        np.median(yv[np.abs(xv - mid) < bin_width / 2])
        if np.any(np.abs(xv - mid) < bin_width / 2) else np.nan
        for mid in bin_mids
    ])
    good = np.isfinite(running)
    design = np.column_stack([np.ones(good.sum())] + [bin_mids[good] ** p for p in (1, 2, 3, 4)])
    coef, *_ = np.linalg.lstsq(design, running[good], rcond=None)

    def poly(v):
        return sum(coef[p] * v**p for p in range(5))

    tail_slope = (poly(cutoff + 0.05) - poly(cutoff)) / 0.05
    tail_int = poly(cutoff) - cutoff * tail_slope

    def model(v):
        v = np.asarray(v, dtype=float)
        return np.where(v < cutoff, poly(v), tail_int + tail_slope * v)

    return model


def fit_interaction(m_score, m_se, w_fitness, w_remediation, w_post, w_mean_score,
                    a222v_fitness, a222v_remediation, concs=CONCS, correction=None):
    """Fit e.b / e.r: the deviation of the A222V-background arm from the
    multiplicative no-interaction expectation.

    expected(c) = single_mutant_term(c) * (b_A222V + c*r_A222V) [+ correction]
    where single_mutant_term is the fitted line when w.post > 0.5, otherwise
    the variant's mean WT-background score (per fitModels.R).
    """
    a222v_line = a222v_fitness + concs[None, :] * a222v_remediation
    use_line = (w_post > 0.5) & np.isfinite(w_fitness)
    sm = np.where(use_line[:, None],
                  w_fitness[:, None] + concs[None, :] * w_remediation[:, None],
                  w_mean_score[:, None])
    expected = sm * a222v_line
    if correction is not None:
        cb, cr = correction
        expected = expected + cb(w_fitness)[:, None] + cr(w_fitness)[:, None] * concs[None, :]

    valid = np.isfinite(m_score) & np.isfinite(m_se) & (m_se > 0) & np.isfinite(expected)
    resid = np.where(valid, m_score - expected, np.nan)

    e_b, e_r, df = wls_line(resid, m_se, concs, valid)

    safe_se = np.where(valid, m_se, 1.0)
    obs = np.where(valid, resid, 0.0)
    logl = _gauss_logl(e_b[:, None] + concs[None, :] * e_r[:, None], obs, safe_se, valid)

    # static model: constant offset only (weighted mean residual), r fixed at 0
    w = np.where(valid, 1.0 / safe_se**2, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        e_b_static = np.where(w.sum(axis=1) > 0, (w * obs).sum(axis=1) / w.sum(axis=1), np.nan)
    logl_static = _gauss_logl(np.broadcast_to(e_b_static[:, None], resid.shape),
                              obs, safe_se, valid)
    logl_null = _gauss_logl(np.zeros_like(resid), obs, safe_se, valid)

    bad = (~valid).sum(axis=1) > 2
    for arr in (e_b, e_r, e_b_static, logl, logl_static, logl_null):
        arr[bad] = np.nan

    return {"e_b": e_b, "e_r": e_r, "e_b_static": e_b_static,
            "logl": logl, "logl_static": logl_static, "logl_null": logl_null,
            "lod_r": logl - logl_static + PRIOR_LOG_ODDS,
            "lod_b": logl_static - logl_null + PRIOR_LOG_ODDS,
            "df": df, "expected": expected, "resid": resid, "valid": valid}
