"""Position-level association null for a Spearman rho (new module; scripts/lib/stats.py untouched).

Extracted verbatim from scripts/76_threshold_sigmoid_model.py (where it was
first written and run for [AD3]) so scripts 77+ can import it instead of
reimplementing. Per AGENTS sections 3-4 the shuffle is over POSITION means,
never rows (rows within a position are not independent), and an identity
permutation must reproduce the observed statistic exactly before any draws
are trusted.
"""
import numpy as np
from scipy.stats import spearmanr

IDENT_TOL = 1e-12


def position_shuffle_test(df, x_col, y_col, n_perm, seed):
    """Association null: shuffle y-side POSITION MEANS vs fixed x means.

    Returns (rho_obs, p_two_sided, n_positions). p uses the +1 correction:
    p = (1 + #{|rho_perm| >= |rho_obs|}) / (1 + n_perm).

    Identity check: permuting y by the identity index array must reproduce
    rho_obs to IDENT_TOL, or SystemExit (AGENTS section 4: sanity-check the
    null before trusting it).
    """
    g = df.groupby("position")[[x_col, y_col]].mean().dropna()
    xo, yo = g[x_col].to_numpy(), g[y_col].to_numpy()
    rho_obs = float(spearmanr(xo, yo).statistic)
    # identity check through the SAME indexing path as the draws below
    rho_ident = float(spearmanr(xo, yo[np.arange(len(yo))]).statistic)
    if abs(rho_obs - rho_ident) > IDENT_TOL:
        raise SystemExit("*** identity permutation did not reproduce "
                         f"observed rho ({rho_obs} vs {rho_ident})")
    rng = np.random.default_rng(seed)
    ge = 0
    for _ in range(n_perm):
        perm = rng.permutation(len(yo))
        rp = float(spearmanr(xo, yo[perm]).statistic)
        if not np.isfinite(rp):
            raise SystemExit("*** non-finite permuted rho")
        if abs(rp) >= abs(rho_obs) - 1e-15:
            ge += 1
    p = (1 + ge) / (1 + n_perm)
    return rho_obs, p, len(g)
