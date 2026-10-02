"""scripts/lib/phase3_common.py -- dataset-agnostic statistics for Phase 3.

PRE-REGISTRATION (this docstring was written BEFORE this module's first run;
it is not edited after any Phase 3 score exists)
--------------------------------------------------------------------------------
PURPOSE.  Generic, dataset-agnostic functions: arrays in, numbers out.  No
dataset file is read here, no column is named here, no MTHFR/GB1/RBD constant
appears here.  Task A2 (docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md)
gates this module against the cached MTHFR numbers in scripts/159_*; if that
gate (A2-G1) fails, this library is not trusted for GB1 or RBD (A4-A5 stop).

FUNCTIONS CONTAINED (Task A2's list, item by item)
--------------------------------------------------
1.  spearman(x, y)  -- Spearman rho with AVERAGE ranks (rankdata method
    "average" on each vector, then Pearson correlation of the ranks).  NaN if
    n < 3 or either ranked vector is constant.  Gate A2 checks this against
    scipy.stats.spearmanr to 1e-12 on the real anchor arrays.
2.  pos_cluster_boot(x, y, clusters, n_boot, seed) and
    pos_cluster_boot_from_ids(x, y, clusters, ids)  -- THE CORRECTED
    position-cluster bootstrap.  Each drawn cluster contributes ALL of its
    rows, with multiplicity.  Implementation delegates to
    `pos_cluster_boot_corrected` / `pos_cluster_boot_corrected_from_ids` in
    scripts/lib/phase2_diag4.py (imported, unmodified; that module imports
    no torch/esm/thermompnn -- verified in A2).  Script 144's routine is
    NEVER used here.  Cluster index space = FIRST-APPEARANCE order of the
    retained rows (Phase 1's convention, scripts/lib/stats.py line 35);
    ids are drawn one `rng.integers(0, nk, nk)` per draw from
    np.random.default_rng(seed), the same stream
    Generator.choice(pop, size, replace=True) consumes (verified in
    scripts/148).
    RESAMPLING UNIT: position clusters -- for a statistic computed INSIDE
    one background (a target's rho on a row subset).
3.  reference_boot(x, y, clusters, ids)  -- THE SLOW, OBVIOUS REFERENCE:
    rebuild cluster -> row indices from scratch with flatnonzero, for each
    draw concatenate the drawn clusters' row indices and compute
    scipy.stats.spearmanr.  No clever indexing.  Used draw-by-draw against
    (2) on identical pre-drawn ids (gate A2-G2, tolerance 1e-12).
4.  background_boot(x, y=None, n_boot, seed, stat)  -- BACKGROUND-level
    bootstrap: resample background indices with replacement, each
    background's already-computed value(s) held FIXED within a draw.
    stat(x, y) -> float; if y is None the default statistic is the mean of
    x (distribution summaries), else spearman(x, y) (covariate tests).
    RESAMPLING UNIT: backgrounds -- for statistics ACROSS backgrounds.
    Never positions.
5.  label_permutation_p(x, y, n_perm, seed, mode)  -- association null:
    permute y across x, statistic = spearman; p = (1 + #{permuted statistic
    at least as extreme}) / (1 + n_perm), mode in {"neg", "pos", "abs"}
    ("abs": |rho_perm| >= |rho_obs|; "neg": rho_perm <= rho_obs; "pos":
    rho_perm >= rho_obs).  Tests whether an ASSOCIATION beats chance; it is
    NOT a re-derivation null (AGENTS 4 -- labelled here so users can choose).
6.  p_spec(rho_target, rho_nulls, mode)  -- the frozen project form,
    mode in {"neg", "pos", "abs"}:
        "neg": (1 + #{rho_b <= rho_T}) / (1 + n)
        "pos": (1 + #{rho_b >= rho_T}) / (1 + n)
        "abs": (1 + #{|rho_b| >= |rho_T|}) / (1 + n)
    Returns (p, k, n).
7.  ols_fit_predict(y, x, x_new) and loo_ols_residuals(y, x)  -- OLS with
    intercept via np.linalg.lstsq (the same design matrix Diagnostics II
    D9 used, scripts/137 lines 177-187); loo_ols_residuals returns the
    leave-one-out residual y_i - pred_i where the fit excluded point i
    (D9's primary construction).
8.  spearman_gradient(rho_b, distance)  -- Spearman of per-background
    values against a distance covariate.  Its CI comes from background_boot
    (RESAMPLING UNIT: backgrounds).
9.  pct_ci(draws)  -- 95% percentile CI [2.5, 97.5] of finite draws,
    script 125's convention (scripts/lib/phase2_diag.py lines 238-244).

RESAMPLING UNITS (state in every caller's docstring too)
--------------------------------------------------------
Inside one background (a target's rho on a row subset, a background's own
rho_b CI): POSITION CLUSTERS.  Across backgrounds (a covariate's Spearman,
a distribution's mean): BACKGROUNDS, values held fixed.  They are not
interchangeable.

LIMITATIONS (AGENTS 4, 6)
-------------------------
* label_permutation_p is an association null, not a re-derivation null.
* background_boot assumes backgrounds are independent draws; within-module
  shared-target structure (all rho_b share one y-vector) is disclosed by
  callers, not modelled here.
* p_spec's "neg"/"pos" are one-sided signed rank counts, not tail areas of
  an exchangeable distribution; callers report them as counts over n.

NO torch, NO esm, NO thermompnn import anywhere in this file (rule 1).

Usage:
    from scripts.lib import phase3_common as p3c
"""

import numpy as np
from scipy.stats import rankdata, spearmanr

from . import phase2_diag4 as p4


# ==========================================================================
# 1. Spearman with average ranks
# ==========================================================================
def spearman(x, y):
    """Spearman rho with AVERAGE ranks (ties get the average rank).

    Arrays in, number out.  NaN if n < 3 or either ranked vector is
    constant.  Gate A2 verifies agreement with scipy.stats.spearmanr to
    1e-12 on the real anchor arrays.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.shape != y.shape:
        raise ValueError(f"shape mismatch: {x.shape} vs {y.shape}")
    if x.size < 3:
        return float("nan")
    rx = rankdata(x, method="average")
    ry = rankdata(y, method="average")
    if rx.std() == 0.0 or ry.std() == 0.0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


# ==========================================================================
# 2. Corrected position-cluster bootstrap (delegates to phase2_diag4)
# ==========================================================================
def _first_appearance_labels(cl):
    """Distinct labels in FIRST-APPEARANCE order (Phase 1's convention)."""
    cl = np.asarray(cl)
    uniq, first = np.unique(cl, return_index=True)
    return uniq[np.argsort(first, kind="stable")]


def _adapter(x, y, clusters):
    """Build the (sa, keep) pair scripts/lib/phase2_diag4.retained_parts
    expects from plain arrays: integer cluster codes in first-appearance
    order, `pos` = the same codes, keep = all True.

    Filtering rows before calling this is the caller's way to express
    "positions removed"; retained_parts then computes first-appearance
    order over the retained rows, identically to the reference.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    cl = np.asarray(clusters)
    if not (x.shape == y.shape == cl.shape):
        raise ValueError("x, y, clusters must have identical shapes")
    labels = _first_appearance_labels(cl)
    code_of = {lab: i for i, lab in enumerate(labels)}
    codes = np.array([code_of[v] for v in cl], dtype=np.int64)
    sa = _Store(code=codes, pos=codes, delta=x, y=y)
    keep = np.ones(len(labels), dtype=bool)
    return sa, keep, labels


class _Store:
    """Minimal attribute store matching phase2_diag4.Store's interface
    fields used by retained_parts (code, pos, delta, y)."""

    def __init__(self, code, pos, delta, y):
        self.code = code
        self.pos = pos
        self.delta = delta
        self.y = y


def pos_cluster_boot(x, y, clusters, n_boot, seed=0):
    """Corrected position-cluster bootstrap, drawing its own cluster ids.

    RESAMPLING UNIT: position clusters; every row of every drawn cluster
    comes with it, with multiplicity.  Delegates the arithmetic to
    scripts/lib/phase2_diag4.pos_cluster_boot_corrected (imported,
    unmodified); this function only adapts arrays to its Store interface
    and owns the rng stream (default_rng(seed), one
    integers(0, nk, nk) per draw -- the stream phase2_diag4's own
    pos_cluster_boot_corrected consumes).
    """
    sa, keep, _ = _adapter(x, y, clusters)
    rng = np.random.default_rng(seed)
    return p4.pos_cluster_boot_corrected(sa, None, keep, n_boot, rng)


def pos_cluster_boot_from_ids(x, y, clusters, ids):
    """Same corrected routine driven by PRE-DRAWN cluster ids so it and
    reference_boot can be compared draw by draw on identical draws.

    ids: (n_draw, nk) in the first-appearance index space of the retained
    rows (exactly what this function's own parts dict uses).
    """
    sa, keep, _ = _adapter(x, y, clusters)
    parts = p4.retained_parts(sa, None, keep)
    return p4.pos_cluster_boot_corrected_from_ids(parts, ids)


def draw_ids(clusters, n_draw, seed=0):
    """Pre-draw (n_draw, nk) cluster ids in the first-appearance index
    space of the given rows' retained clusters (the index space both
    pos_cluster_boot_from_ids and reference_boot expect)."""
    labels = _first_appearance_labels(clusters)
    nk = len(labels)
    rng = np.random.default_rng(seed)
    ids = np.empty((n_draw, nk), dtype=np.int64)
    for i in range(n_draw):
        ids[i] = rng.integers(0, nk, nk)
    return ids, labels


# ==========================================================================
# 3. Slow, obvious reference implementation
# ==========================================================================
def reference_boot(x, y, clusters, ids):
    """SLOW, OBVIOUS REFERENCE bootstrap.  Rebuilds cluster -> row indices
    from scratch (flatnonzero over the full cluster array); for each draw
    concatenates the drawn clusters' row indices (every row, multiplicity
    included) and computes scipy.stats.spearmanr.  No clever indexing of
    any kind.

    ids' index space = first-appearance order of the labels in `clusters`
    (what draw_ids returns).  This is the reference for gate A2-G2:
    max |reference - corrected| must be < 1e-12 draw by draw.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    cl = np.asarray(clusters)
    labels = _first_appearance_labels(cl)
    rows_of = {lab: np.flatnonzero(cl == lab) for lab in labels}
    ids = np.asarray(ids)
    draws = np.empty(len(ids), dtype=float)
    for i in range(len(ids)):
        idx = np.concatenate([rows_of[labels[s]] for s in ids[i]])
        draws[i] = float(spearmanr(x[idx], y[idx]).statistic)
    return draws


# ==========================================================================
# 4. Background-level bootstrap
# ==========================================================================
def background_boot(x, y=None, n_boot=10000, seed=0, stat=None):
    """BACKGROUND-level bootstrap.

    RESAMPLING UNIT: the background.  Each draw resamples background
    indices with replacement (n = len(x) draws); each background's
    already-computed value(s) are held fixed within a draw -- no
    re-derivation of any rho_b.  Never positions.

    stat(x, y) -> float; default: mean(x) when y is None, else
    spearman(x, y).  Returns (draws, nan_count).
    """
    x = np.asarray(x, dtype=float)
    y_arr = None if y is None else np.asarray(y, dtype=float)
    if stat is None:
        stat = (lambda a, b: float(np.mean(a))) if y_arr is None else spearman
    n = len(x)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        draws[i] = stat(x[idx], y_arr[idx]) if y_arr is not None else stat(x[idx], None)
    return draws, int(np.isnan(draws).sum())


# ==========================================================================
# 5. Label-permutation p (association null)
# ==========================================================================
def label_permutation_p(x, y, n_perm=10000, seed=0, mode="abs"):
    """Label-permutation p for spearman(x, y): permute y across x.

    ASSOCIATION NULL (tests whether the association beats chance), NOT a
    re-derivation null -- see the module docstring, AGENTS 4.
    mode "abs": |rho_perm| >= |rho_obs|;  "neg": rho_perm <= rho_obs;
    "pos": rho_perm >= rho_obs.  p = (1 + k) / (1 + n_perm).
    Returns (p, k, n_perm).
    """
    if mode not in ("neg", "pos", "abs"):
        raise ValueError(f"mode must be neg/pos/abs, got {mode!r}")
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    obs = spearman(x, y)
    rng = np.random.default_rng(seed)
    k = 0
    for _ in range(int(n_perm)):
        rp = spearman(x, rng.permutation(y))
        if mode == "abs":
            hit = abs(rp) >= abs(obs)
        elif mode == "neg":
            hit = rp <= obs
        else:
            hit = rp >= obs
        if bool(hit) and not np.isnan(rp):
            k += 1
    return (1 + k) / (1 + int(n_perm)), k, int(n_perm)


# ==========================================================================
# 6. p_spec -- the frozen project form
# ==========================================================================
def p_spec(rho_target, rho_nulls, mode="neg"):
    """(p, k, n) with p = (1 + k) / (1 + n).

    "neg": k = #{rho_b <= rho_T}   (the frozen one-sided signed form)
    "pos": k = #{rho_b >= rho_T}
    "abs": k = #{|rho_b| >= |rho_T|}
    """
    if mode not in ("neg", "pos", "abs"):
        raise ValueError(f"mode must be neg/pos/abs, got {mode!r}")
    nulls = np.asarray(rho_nulls, dtype=float)
    n = int(nulls.size)
    if mode == "neg":
        k = int(np.sum(nulls <= float(rho_target)))
    elif mode == "pos":
        k = int(np.sum(nulls >= float(rho_target)))
    else:
        k = int(np.sum(np.abs(nulls) >= abs(float(rho_target))))
    return (1 + k) / (1 + n), k, n


# ==========================================================================
# 7. OLS with intercept; leave-one-out residuals (Diagnostics II D9)
# ==========================================================================
def ols_fit_predict(y, x, x_new):
    """OLS of y on x with intercept (np.linalg.lstsq, the same design
    matrix scripts/137 lines 177-187 uses).  Returns
    (slope, intercept, predictions at x_new)."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = beta[0] + beta[1] * np.asarray(x_new, dtype=float)
    return float(beta[1]), float(beta[0]), pred


def loo_ols_residuals(y, x):
    """Leave-one-out OLS residuals, D9's primary construction: for point i
    fit y ~ 1 + x on all points EXCEPT i, then residual_i = y_i - pred_i
    (out-of-sample for i).  Returns the (n,) residual array."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    n = len(y)
    res = np.empty(n, dtype=float)
    for i in range(n):
        m = np.ones(n, dtype=bool)
        m[i] = False
        _, _, pred = ols_fit_predict(y[m], x[m], [x[i]])
        res[i] = y[i] - float(pred[0])
    return res


# ==========================================================================
# 8. Spearman gradient against a distance covariate
# ==========================================================================
def spearman_gradient(rho_b, distance):
    """Spearman(rho_b, distance) across backgrounds.  Its CI comes from
    background_boot -- RESAMPLING UNIT: backgrounds, values held fixed."""
    return spearman(rho_b, distance)


# ==========================================================================
# 9. Percentile CI (script 125's convention)
# ==========================================================================
def pct_ci(draws):
    """95% percentile CI [2.5, 97.5] over the finite draws; returns
    (lo, hi, n_finite).  NaN draws dropped (125's convention)."""
    a = np.asarray(draws, dtype=float)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return float("nan"), float("nan"), 0
    lo, hi = np.percentile(a, [2.5, 97.5])
    return float(lo), float(hi), int(len(a))
