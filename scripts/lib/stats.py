"""Statistical machinery for the primary analysis (proposal sections 5.5-5.6).

Not implemented yet -- these are the functions Week 3-4 work fills in.
Signatures sketched now so scripts/ and notebooks/ can both target a stable
interface as they get built out.
"""

def decompose_error(fitness_by_condition, prediction):
    """Central error vs condition-specific component (section 5.5).
    fitness_by_condition: dict of {(background, conc): fitness}
    """
    raise NotImplementedError

def position_cluster_bootstrap(data, statistic_fn, n_resamples=10000):
    """Position-level bootstrap, the primary inferential framework (5.6a)."""
    raise NotImplementedError
