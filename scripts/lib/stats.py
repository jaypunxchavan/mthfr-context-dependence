"""Statistical machinery for the primary analysis (proposal sections 5.5-5.6).

Inference is by CLUSTER bootstrap, resampling positions rather than rows:
up to 19 substitutions share a position and are not independent, so
row-level resampling overstates significance.
"""
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.isotonic import IsotonicRegression


def _spearman(a, b):
    """Spearman rho via ranks + Pearson. Matches scipy.stats.spearmanr exactly."""
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def _partial_spearman(x, y, z):
    """Partial Spearman of x,y controlling z, closed form on ranks.
    Verified numerically identical to OLS-residual approach."""
    c = np.corrcoef(np.vstack([rankdata(x), rankdata(y), rankdata(z)]))
    rxy, rxz, ryz = c[0, 1], c[0, 2], c[1, 2]
    denom = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    return float((rxy - rxz * ryz) / denom) if denom > 0 else np.nan


def _summarize(observed, boot):
    boot = boot[~np.isnan(boot)]
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
    p = min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0)
    return {"observed_rho": observed, "ci_lo": ci_lo, "ci_hi": ci_hi, "p_boot": p}


def _cluster_indices(d, cluster_col):
    clusters = d[cluster_col].unique()
    return clusters, {c: d.index[d[cluster_col] == c].to_numpy() for c in clusters}


def position_cluster_bootstrap(df, cluster_col, x_col, y_col, n_boot=10000, seed=0):
    """Cluster bootstrap for a Spearman correlation.
    p_boot == 0.0 means no resample crossed zero -> report p < 1/n_boot."""
    d = df[[cluster_col, x_col, y_col]].dropna()
    clusters, idx_by = _cluster_indices(d, cluster_col)
    x, y = d[x_col].to_numpy(), d[y_col].to_numpy()
    pos = {c: np.searchsorted(d.index.to_numpy(), idx_by[c]) for c in clusters}

    observed = _spearman(x, y)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        i = np.concatenate([pos[c] for c in drawn])
        boot[b] = _spearman(x[i], y[i])
    out = _summarize(observed, boot)
    out.update({"n_rows": len(d), "n_clusters": len(clusters)})
    return out


def partial_spearman_cluster_bootstrap(df, cluster_col, x_col, y_col, covar_col,
                                       n_boot=10000, seed=0):
    """Partial Spearman of x,y controlling one covariate, cluster-bootstrapped.

    Required here: context dependence correlates with base fitness by
    construction, and both error metrics vary with position in the fitness
    distribution in OPPOSITE directions (proposal 5.6d). Univariate
    error-vs-context correlations are not interpretable alone.
    """
    d = df[[cluster_col, x_col, y_col, covar_col]].dropna()
    clusters, idx_by = _cluster_indices(d, cluster_col)
    x, y, z = d[x_col].to_numpy(), d[y_col].to_numpy(), d[covar_col].to_numpy()
    pos = {c: np.searchsorted(d.index.to_numpy(), idx_by[c]) for c in clusters}

    observed = _partial_spearman(x, y, z)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        i = np.concatenate([pos[c] for c in drawn])
        boot[b] = _partial_spearman(x[i], y[i], z[i])
    out = _summarize(observed, boot)
    out.update({"n_rows": len(d), "n_clusters": len(clusters)})
    return out


def paired_rho_difference_bootstrap(df, cluster_col, x1_col, x2_col, y_col,
                                    n_boot=10000, seed=0):
    """Cluster bootstrap for rho(x2,y) - rho(x1,y) on the same rows.
    Compares competing predictors against one outcome. Steiger's test is
    avoided: it assumes bivariate normality that rank data violate."""
    d = df[[cluster_col, x1_col, x2_col, y_col]].dropna()
    clusters, idx_by = _cluster_indices(d, cluster_col)
    x1, x2, y = d[x1_col].to_numpy(), d[x2_col].to_numpy(), d[y_col].to_numpy()
    pos = {c: np.searchsorted(d.index.to_numpy(), idx_by[c]) for c in clusters}

    observed = _spearman(x2, y) - _spearman(x1, y)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        i = np.concatenate([pos[c] for c in drawn])
        boot[b] = _spearman(x2[i], y[i]) - _spearman(x1[i], y[i])
    out = _summarize(observed, boot)
    out["observed_diff"] = out.pop("observed_rho")
    out.update({"n_rows": len(d), "n_clusters": len(clusters)})
    return out


def crossfit_isotonic_by_position(df, position_col, score_col, target_col,
                                  n_folds=5, seed=0):
    """Position-held-out cross-fitted isotonic calibration of score -> target.

    Splitting by POSITION, not variant: if 18 substitutions at residue 165
    are in the calibration set and one is held out, the calibration has
    effectively already seen that position.
    """
    d = df[[position_col, score_col, target_col]].dropna()
    rng = np.random.default_rng(seed)
    folds = np.array_split(rng.permutation(d[position_col].unique()), n_folds)

    preds = pd.Series(np.nan, index=df.index, dtype=float)
    for fold in folds:
        test_mask = d[position_col].isin(fold)
        train, test = d[~test_mask], d[test_mask]
        if len(train) == 0 or len(test) == 0:
            continue
        iso = IsotonicRegression(out_of_bounds="clip", increasing="auto")
        iso.fit(train[score_col].to_numpy(), train[target_col].to_numpy())
        preds.loc[test.index] = iso.predict(test[score_col].to_numpy())
    return preds


def crossfit_isotonic_stratified(df, position_col, score_col, target_col,
                                 stratify_col, n_folds=5, seed=0):
    """Position-held-out isotonic calibration with folds stratified by a group
    (e.g. mutagenesis region), so every fold gets a proportional mix rather
    than a random draw. Used to test whether fold composition drives a
    region-specific calibration artifact."""
    d = df[[position_col, score_col, target_col, stratify_col]].dropna()
    rng = np.random.default_rng(seed)
    pos_group = d.groupby(position_col)[stratify_col].first()

    assign = {}
    for g, positions in pos_group.groupby(pos_group):
        shuffled = rng.permutation(positions.index.to_numpy())
        for i, p in enumerate(shuffled):
            assign[p] = i % n_folds

    preds = pd.Series(np.nan, index=df.index, dtype=float)
    fold_of = d[position_col].map(assign)
    for k in range(n_folds):
        test_mask = fold_of == k
        train, test = d[~test_mask], d[test_mask]
        if len(train) == 0 or len(test) == 0:
            continue
        iso = IsotonicRegression(out_of_bounds="clip", increasing="auto")
        iso.fit(train[score_col].to_numpy(), train[target_col].to_numpy())
        preds.loc[test.index] = iso.predict(test[score_col].to_numpy())
    return preds


def crossfit_isotonic_within_group(df, position_col, score_col, target_col,
                                   group_col, n_folds=5, seed=0):
    """Isotonic calibration fit SEPARATELY within each group, still holding out
    positions. Tests whether a group needs its own score-to-fitness curve --
    i.e. whether pooling the calibration is what breaks it."""
    preds = pd.Series(np.nan, index=df.index, dtype=float)
    for g, sub in df.groupby(group_col):
        if sub[position_col].nunique() < n_folds * 2:
            continue
        preds.loc[sub.index] = crossfit_isotonic_by_position(
            sub, position_col, score_col, target_col, n_folds=n_folds, seed=seed)
    return preds
