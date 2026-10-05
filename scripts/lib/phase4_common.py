"""scripts/lib/phase4_common.py -- dataset-agnostic statistics for Phase 4.

PRE-REGISTRATION (this docstring was written BEFORE this module's first run;
it is not edited after any Phase 4 score exists)
================================================================================
PURPOSE.  Generic, dataset-agnostic functions for PHASE4_STRENGTHENING.md
Task A2: arrays in, numbers out.  No dataset file is read here, no column is
named here, no MTHFR / GB1 / RBD constant appears here.  Task A2's gates
(scripts/165_phase4_common_gate.py) are A2-G1 (script 159 rerun unchanged,
40/40), A2-G2 (the cached MTHFR numbers reproduced THROUGH this library) and
A2-G3 (toy gates for every function here).  No torch, no esm, no thermompnn is
imported anywhere in this file (PHASE4 rule 1).

WHAT IS IMPORTED, NEVER RE-DERIVED (AGENTS 2)
---------------------------------------------
* `spearman`, `p_spec`, `pct_ci`, `pos_cluster_boot`,
  `pos_cluster_boot_from_ids`, `draw_ids`, `reference_boot`,
  `background_boot`, `label_permutation_p` -- scripts/lib/phase3_common.py.
* `pos_cluster_boot_corrected`,
  `pos_cluster_boot_corrected_from_ids` -- scripts/lib/phase2_diag4.py (the
  CORRECTED position-cluster routine; script 144's routine is never used).
* `rebuild_interaction_fit` -- scripts/lib/stats_ext.py (the project's own
  two-pass own-context fit, unmodified).
* `CONCS`, `WT_SCORE_COLS`, `WT_SE_COLS`, `MT_SCORE_COLS`, `MT_SE_COLS` --
  scripts/lib/own_context.py (the project's own column names).
They are re-exported below so a Phase 4 script can import this module alone.

RESAMPLING UNITS (PHASE4 rule 7; stated in every function that resamples)
------------------------------------------------------------------------
* Inside one background (an anchor rho, a component's CI, a partial
  correlation): POSITION CLUSTERS.
* Across backgrounds (a gradient, a cell mean, a distribution, per-background
  rho_b values): BACKGROUNDS, with each rho_b held fixed.
* The whole-placebo-test bootstrap resamples POSITIONS and re-derives every
  background's rho_b on the resampled rows (it is a re-derivation null, not a
  re-labelling of already-computed rho_b -- AGENTS 4).

FUNCTIONS CONTAINED (Task A2's list, item by item)
--------------------------------------------------
 1. Average-rank PARTIAL SPEARMAN by OLS residualisation on ranks, any number
    of controls: `partial_spearman`.  Rank-transform every variable
    (scipy rankdata, method="average"), regress rank(x) and rank(y) on an
    intercept plus the rank-transformed controls with np.linalg.lstsq, take
    the Pearson correlation of the two residual vectors.
 2. Decile-stratified Spearman: `equal_count_bins` (equal-count bin labels)
    and `stratified_spearman` (weighted mean of the within-bin Spearmans,
    weights = rows in the bin).
 3. Between/within-position decomposition: `between_within_decomposition`.
 4. Within-position and within-bin permutation:
    `permute_within_groups`, `permuted_spearman`.
 5. The zero-epistasis simulation harness wrapping the project's UNMODIFIED
    own_e.b pipeline with a pluggable noise model and planting:
    `raw_frame`, `own_eb_from_arrays`, `rank_normal_z`, `plant_term`,
    `zero_epistasis_draw`, `simulate_rho`.
 6. The planting power curve and minimum-detectable-effect interpolation:
    `draw_summary`, `power_curve`, `min_detectable_effect`,
    `attenuation_slope`.
 7. The whole-placebo-test position bootstrap: `whole_placebo_boot`,
    `whole_placebo_boot_from_ids`, `whole_placebo_reference`.
 8. 2x2 geometry helpers: `cell_labels`, `interval_labels`,
    `seq_separation`.
 9. AUROC and balanced-PR area: `auroc`, `balanced_pr_curve`,
    `balanced_pr_auc`.
10. The outcome-word functions of each frozen block, exactly as written:
    `word_m1_partial`, `word_m3_artifact`, `word_m5_carry`, `word_m6_stable`,
    `word_conditioning`, `word_underpowered`, `gb1_model_decays`,
    `gb1_data_decays`, `gb1_locality_differs`, `gb1_separation`,
    `word_neighbour`, `word_distance`, `word_ladder`.

INTERPRETATION DECISIONS (fixed here, before any Phase 4 number exists; each
one covers a point the frozen text leaves open, exactly as script 153's D1-D11
did.  They interpret the frozen text; they never change a frozen constant.)
  I1  `stratified_spearman`: a bin whose within-bin Spearman is undefined
      (fewer than 3 rows, or a constant vector) is DROPPED and the remaining
      weights are re-normalised.  The frozen text is silent on this case.
  I2  `between_within_decomposition`: rows with a non-finite x or y are
      dropped before positions are counted, so "at least 5 rows" means 5
      FINITE rows; the weight of a position is its number of finite rows.
  I3  `permute_within_groups`: groups are visited in np.unique sorted order
      so a given (values, groups, seed) triple is reproducible; the values of
      each group are shuffled among that group's rows only.
  I4  `rank_normal_z` (MECH frozen M-4's "standardised rank-normal score of
      delta_real"): r = average ranks of v; q = (r - 0.5)/n; g = Phi^-1(q)
      (scipy.special.ndtri); z = (g - mean(g)) / sd(g, ddof=0).  Standardised
      to mean 0 and sd 1 so that s_e * (r0 z + sqrt(1-r0^2) u) has the SD the
      frozen text asks for.
  I5  `min_detectable_effect`: the frozen text asks for ONE "minimum
      detectable |r0| at 80% power" while power is a V-shape in r0 (lower
      tail for r0 < 0, upper for r0 > 0).  Power is therefore interpolated
      separately on each side of zero -- origin point (|r0| = 0, power =
      0.025, the tail fraction the r0 = 0 band is defined by) plus that
      side's grid points, sorted by |r0|, first point at or above the target
      bracketed linearly -- and BOTH are printed; the headline value is the
      SMALLER of the two, with "above the grid" when neither side reaches the
      target.  Both sides are always shown so the headline cannot hide one.
  I6  `balanced_pr_auc` curve convention: points sit at the DISTINCT score
      thresholds (ties grouped), the curve is anchored with an extra first
      point at recall 0 whose balanced precision is that of the top
      threshold, and the area is the trapezoid of sklearn.metrics.auc over
      (recall, balanced precision).  Balanced precision is
      TPR / (TPR + FPR), which is 0.5 for a chance classifier.  The frozen
      text names the curve and its precision definition but not the
      integration rule; stated here before any label set is seen.
  I7  Outcome-word precedence where two clauses of one frozen block could
      both hold (UTIL U-1/U-2: a CI entirely above zero that also lies inside
      (-0.02, +0.02)): the frozen text lists CONDITIONING-HELPS first, so the
      functions test the clauses in the order the frozen block writes them
      and return the FIRST that holds.
  I8  GB1D gives an outcome word only as an "iff" with no else-word for
      MODEL-DECAYS / DATA-DECAYS / LOCALITY-DIFFERS.  Those three functions
      return the iff-condition as a BOOL so no unregistered word can be
      invented; every other word function returns a frozen word string.

BOOTSTRAP REFERENCE GATE (PHASE4 rule 6 -- a REFERENCE gate, not an identity
gate).  Every bootstrap routine reachable from this module either (a) is the
imported corrected routine, gated in script 159 against a slow reference draw
by draw and against Phase 1's CI
[-0.1173334458953319, -0.0595113844951173], or (b) is
`whole_placebo_boot_from_ids`, which script 165 gates three ways: identity
(every position exactly once returns the observed p_spec and k -- the frozen
G-M7 rule), draw by draw against `whole_placebo_reference` at 1e-12 on
identical pre-drawn position ids, and by delegating its per-draw rho to the
same imported `spearman` the identity uses.  The Phase 1 CI reproduction is
re-run in script 165 itself (it is a property of the imported routine, and
the imported routine is what this module re-exports).

LIMITATIONS (AGENTS 4, 6)
-------------------------
* Reproduction is not replication: A2-G2 re-derives CACHED Phase 1/2 numbers
  through this library.  It validates the code; it is not evidence for any
  claim and produces no new inference.
* `partial_spearman` is a LINEAR partial on ranks (a rank-partial); it is not
  the spline partial of script 43 and must never be compared with it as if it
  were (Phase 1 C1's L1/D1 cells).
* `background_boot` and every per-background CI here resample backgrounds
  that share one y-vector across backgrounds; that shared-target structure is
  disclosed by callers, not modelled.
* `power_curve` measures the pipeline's power against ITS OWN simulation
  null; it is not a statement about a true biological effect size.
* The zero-epistasis harness re-runs the project's own estimator on simulated
  inputs (a re-derivation null, AGENTS 4).  It inherits every assumption of
  that estimator, including the multiplicative no-interaction expectation.

Usage:
    from scripts.lib import phase4_common as p4c
"""

import numpy as np
import pandas as pd
from scipy.special import ndtri
from scipy.stats import rankdata, spearmanr

from . import phase2_diag4 as _p4d
from . import phase3_common as _p3c
from .own_context import (CONCS, MT_SCORE_COLS, MT_SE_COLS, WT_SCORE_COLS,
                          WT_SE_COLS)
from .stats_ext import rebuild_interaction_fit

# ---------------------------------------------------------------------------
# Re-exports: the corrected bootstrap and phase3_common, never re-derived.
# ---------------------------------------------------------------------------
spearman = _p3c.spearman
p_spec = _p3c.p_spec
pct_ci = _p3c.pct_ci
pos_cluster_boot = _p3c.pos_cluster_boot
pos_cluster_boot_from_ids = _p3c.pos_cluster_boot_from_ids
draw_ids = _p3c.draw_ids
reference_boot = _p3c.reference_boot
background_boot = _p3c.background_boot
label_permutation_p = _p3c.label_permutation_p
pos_cluster_boot_corrected = _p4d.pos_cluster_boot_corrected
pos_cluster_boot_corrected_from_ids = _p4d.pos_cluster_boot_corrected_from_ids
first_appearance_labels = _p3c._first_appearance_labels


def _finite(*arrays):
    """Boolean mask of rows where every given array is finite."""
    m = np.ones(np.asarray(arrays[0]).shape, dtype=bool)
    for a in arrays:
        m &= np.isfinite(np.asarray(a, dtype=float))
    return m


def _rank(v):
    return rankdata(np.asarray(v, dtype=float), method="average")


# ===========================================================================
# 1. Average-rank partial Spearman by OLS residualisation on ranks
# ===========================================================================
def partial_spearman(x, y, controls):
    """Rank-partial Spearman of x and y controlling any number of controls.

    Average ranks for every variable (scipy rankdata method "average"), OLS
    of rank(x) and rank(y) on an intercept plus the control ranks
    (np.linalg.lstsq), Pearson correlation of the two residual vectors.
    Single precision check: with one control this equals the closed form
    (r_xy - r_xz r_yz) / sqrt((1-r_xz^2)(1-r_yz^2)) built from the three
    Spearman values; gate A2-G3 checks exactly that, and gate A2-G2 checks it
    against Phase 1 C1's -0.06414804421216103 to 1e-12.

    RESAMPLING UNIT when a CI is wanted: position clusters (caller's job) --
    this function computes a point estimate on the rows it is given.
    NaN if n < 3, if a control is constant, or if a residual vector is
    constant.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    Cs = [np.asarray(c, dtype=float) for c in controls]
    if not all(c.shape == x.shape for c in Cs):
        raise ValueError("x, y and every control must have the same shape")
    m = _finite(x, y, *Cs)
    x, y, Cs = x[m], y[m], [c[m] for c in Cs]
    if x.size < 3:
        return float("nan")
    rx, ry = _rank(x), _rank(y)
    D = np.column_stack([np.ones(x.size)] + [_rank(c) for c in Cs])
    if np.linalg.matrix_rank(D) < D.shape[1]:
        return float("nan")
    bx, *_ = np.linalg.lstsq(D, rx, rcond=None)
    by, *_ = np.linalg.lstsq(D, ry, rcond=None)
    ex, ey = rx - D @ bx, ry - D @ by
    if ex.std() == 0.0 or ey.std() == 0.0:
        return float("nan")
    return float(np.corrcoef(ex, ey)[0, 1])


# ===========================================================================
# 2. Equal-count bins and decile-stratified Spearman
# ===========================================================================
def equal_count_bins(values, n_bins):
    """Equal-count bin labels 0..n_bins-1 over the sorted values.

    The sorted rows are split with np.array_split, so bin sizes differ by at
    most one row (larger bins first).  Ties are broken by sort order
    (stable), so bin membership of tied values is deterministic but not
    grouped -- the frozen text says "equal-count over the frame".
    """
    v = np.asarray(values, dtype=float)
    if not np.isfinite(v).all():
        raise ValueError("equal_count_bins expects finite values")
    n = v.size
    if n_bins < 1 or n_bins > n:
        raise ValueError("n_bins must be in 1..n")
    order = np.argsort(v, kind="stable")
    labels = np.empty(n, dtype=np.int64)
    for i, idx in enumerate(np.array_split(order, n_bins)):
        labels[idx] = i
    return labels


def _strata_parts(x, y, strata, weights=None):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    lab = np.asarray(strata)
    if not (x.shape == y.shape == lab.shape):
        raise ValueError("x, y and strata must have identical shapes")
    if weights is None:
        w = np.ones(x.size, dtype=float)
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape != x.shape:
            raise ValueError("weights must have the same shape as x")
    out = []
    for g in np.unique(lab):
        idx = lab == g
        n = int(idx.sum())
        rho = spearman(x[idx], y[idx])
        out.append({"stratum": g, "n": n, "weight": float(w[idx].sum()),
                    "rho": rho})
    return out


def stratified_spearman(x, y, strata, weights=None):
    """Weighted mean of the within-stratum Spearmans (M-2's statistic).

    weight of a stratum = rows in the stratum (or the caller's weights).
    Strata whose within-stratum Spearman is undefined are DROPPED and the
    remaining weights are re-normalised (decision I1); NaN if none survive.
    """
    parts = _strata_parts(x, y, strata, weights)
    keep = [p for p in parts if np.isfinite(p["rho"])]
    if not keep:
        return float("nan")
    tot = sum(p["weight"] for p in keep)
    if tot <= 0:
        return float("nan")
    return float(sum(p["weight"] * p["rho"] for p in keep) / tot)


def stratified_spearman_parts(x, y, strata, weights=None):
    """Per-stratum detail of `stratified_spearman` (n, weight, rho)."""
    return _strata_parts(x, y, strata, weights)


# ===========================================================================
# 3. Between/within-position decomposition
# ===========================================================================
def between_within_decomposition(x, y, positions, min_rows=5):
    """Between- and within-position Spearman (MECH frozen M-5).

    RESAMPLING UNIT when a CI is wanted: position clusters, both components
    recomputed per resample (caller's job).

    Qualifying positions: at least `min_rows` FINITE rows (decision I2).
      rho_between = Spearman across qualifying positions of (mean x, mean y)
      rho_within   = mean over qualifying positions of the within-position
                     Spearman, weights = finite rows in the position,
                     positions whose within-position Spearman is undefined
                     skipped (frozen text).
    Returns a dict: rho_between, rho_within, n_qualifying, n_positions,
    weights and the per-position detail list.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    pos = np.asarray(positions)
    if not (x.shape == y.shape == pos.shape):
        raise ValueError("x, y and positions must have identical shapes")
    m = _finite(x, y, pos.astype(float))
    x, y, pos = x[m], y[m], pos[m]
    uniq, inv = np.unique(pos, return_inverse=True)
    counts = np.bincount(inv)
    means_x = np.bincount(inv, weights=x) / counts
    means_y = np.bincount(inv, weights=y) / counts
    qualifies = counts >= int(min_rows)
    detail = []
    for i in range(len(uniq)):
        if not qualifies[i]:
            continue
        idx = inv == i
        rho = spearman(x[idx], y[idx])
        detail.append({"position": uniq[i], "n": int(counts[i]),
                       "mean_x": float(means_x[i]),
                       "mean_y": float(means_y[i]), "rho": rho})
    q = [d for d in detail]
    rho_between = (spearman([d["mean_x"] for d in q],
                            [d["mean_y"] for d in q]) if len(q) >= 3
                   else float("nan"))
    keep = [d for d in q if np.isfinite(d["rho"])]
    if keep:
        wsum = sum(d["n"] for d in keep)
        rho_within = float(sum(d["n"] * d["rho"] for d in keep) / wsum)
    else:
        rho_within = float("nan")
    return {"rho_between": rho_between, "rho_within": rho_within,
            "n_qualifying": len(q), "n_positions": int(len(uniq)),
            "positions": [d["position"] for d in q], "detail": detail}


# ===========================================================================
# 4. Within-position / within-bin permutation
# ===========================================================================
def permute_within_groups(values, groups, rng):
    """Shuffle `values` among the rows of each group (decision I3).

    Groups are visited in np.unique sorted order; only rows inside a group
    are shuffled, so every group's value multiset AND every group's value
    mean are preserved (that is what S1 "keeps position-level structure"
    and S2 "keeps only the regional profile" rely on).  `rng` is a
    np.random.Generator.  RESAMPLING UNIT: the rows inside a group (this is
    a re-labelling null within a cluster, not a cluster resample).
    """
    v = np.asarray(values).copy()
    g = np.asarray(groups)
    if v.shape != g.shape:
        raise ValueError("values and groups must have identical shapes")
    for lab in np.unique(g):
        idx = np.flatnonzero(g == lab)
        v[idx] = rng.permutation(v[idx])
    return v


def permuted_spearman(x, y, groups, rng):
    """spearman(x, y-within-groups-shuffled); the M-5 S1/S2 statistic."""
    return spearman(np.asarray(x, dtype=float),
                    permute_within_groups(y, groups, rng))


# ===========================================================================
# 5. The zero-epistasis simulation harness (MECH frozen M-3 / M-4)
# ===========================================================================
def raw_frame(w, w_se, m, m_se, hgvs, concs=CONCS):
    """A DataFrame in the PROJECT'S OWN raw-column schema, for the rebuild.

    w, w_se, m, m_se: (n_variants, n_concs) arrays ordered as `concs`.
    Column names are exactly scripts/lib/own_context.py's own
    WT_SCORE_COLS / WT_SE_COLS / MT_SCORE_COLS / MT_SE_COLS plus "hgvs".
    Nothing else is invented.
    """
    w = np.asarray(w, dtype=float)
    w_se = np.asarray(w_se, dtype=float)
    m = np.asarray(m, dtype=float)
    m_se = np.asarray(m_se, dtype=float)
    hgvs = np.asarray(hgvs)
    n, k = w.shape
    if not (w_se.shape == m.shape == m_se.shape == (n, k)):
        raise ValueError("w, w_se, m, m_se must share one shape")
    if len(hgvs) != n:
        raise ValueError("hgvs must have one entry per variant")
    if k != len(concs):
        raise ValueError("column count must match `concs`")
    data = {"hgvs": hgvs}
    for j, c in enumerate(concs):
        tag = f"{int(round(float(c)))}"
        data[f"w{tag}.score"] = w[:, j]
        data[f"w{tag}.se"] = w_se[:, j]
        data[f"m{tag}.score"] = m[:, j]
        data[f"m{tag}.se"] = m_se[:, j]
    return pd.DataFrame(data)


def own_eb_from_arrays(w, w_se, m, m_se, hgvs, concs=CONCS):
    """own_e.b rebuilt through the project's UNMODIFIED pipeline.

    Calls scripts/lib/stats_ext.rebuild_interaction_fit (imported,
    unmodified -- the two-pass fit, the correction curves, the weighted
    aggregation and the >2-missing NaN rule are all the project's own) on a
    frame built by `raw_frame`.  Returns the (n,) e_b array.
    """
    raw = raw_frame(w, w_se, m, m_se, hgvs, concs=concs)
    return np.asarray(rebuild_interaction_fit(raw)["e2"]["e_b"], dtype=float)


def rank_normal_z(v):
    """Standardised rank-normal score (decision I4)."""
    v = np.asarray(v, dtype=float)
    n = v.size
    if n < 3:
        raise ValueError("need at least 3 values")
    r = _rank(v)
    g = ndtri((r - 0.5) / n)
    sd = g.std(ddof=0)
    if sd == 0.0:
        raise ValueError("constant input")
    return (g - g.mean()) / sd


def plant_term(r0, s_e, z, u):
    """e_plant_i = s_e * (r0 * z_i + sqrt(1 - r0^2) * u_i)  (frozen M-4).

    r0 in [-1, 1]; z the standardised rank-normal score of delta_real
    (rank_normal_z), u ~ N(0,1) independent, s_e the SD of the recorded
    own_e.b.  Returns a 1-D array over variants; add it to every condition.
    """
    r0 = float(r0)
    if abs(r0) > 1.0:
        raise ValueError("r0 must lie in [-1, 1]")
    z = np.asarray(z, dtype=float)
    u = np.asarray(u, dtype=float)
    if z.shape != u.shape:
        raise ValueError("z and u must have the same shape")
    return float(s_e) * (r0 * z + np.sqrt(1.0 - r0 ** 2) * u)


def zero_epistasis_draw(w, E, m_se, sw, rng, plant=None, m_noise=None):
    """One draw of the frozen zero-epistasis world: (w_sim, m_sim).

    w_sim_i = w_i + N(0, sw_i^2)          (pluggable noise model: pass
               sw = zeros for the frozen PRIMARY of "the data does not carry
               a per-variant WT-background standard error", or any other
               per-variant array; the model is the caller's choice and must
               be stated in the caller's output)
    m_sim_ic = E_c(w*_i) + N(0, m_noise_ic^2) [+ plant_i, the same plant
               for every condition]
    E is the (n_variants, n_concs) expectation ALREADY EVALUATED at w* (the
    proxy truth), e.g. script 153's GE-ISO curve; `plant` is an optional
    (n,) array (see plant_term).  No background-specific epistasis is
    generated anywhere: any own_e.b that comes out is artefact.

    m_noise vs m_se (decision recorded before any Phase 4 number existed):
    frozen M-3 writes the m noise as N(0, m_se_ic^2), i.e. the noise SD IS
    the recorded m_se -- that is the default here (m_noise = m_se).  But
    m_se is ALSO the se column the unmodified pipeline weights by (scripts
    106 line 340 and 17 both feed the recorded Mse), so a caller that wants
    "every noise term zero" (frozen G-M4) must zero the NOISE without
    zeroing the WEIGHTS: pass m_noise = zeros and leave m_se recorded.
    The w side already separates the two (sw is the noise, w_se the se
    column); this parameter gives m the same separation.  Nothing else
    about the frozen model changes.
    """
    w = np.asarray(w, dtype=float)
    E = np.asarray(E, dtype=float)
    m_se = np.asarray(m_se, dtype=float)
    noise = m_se if m_noise is None else np.asarray(m_noise, dtype=float)
    sw = np.zeros_like(w[:, 0]) if sw is None else np.asarray(sw, dtype=float)
    if E.shape != m_se.shape or E.shape[0] != w.shape[0]:
        raise ValueError("E, m_se and w disagree in shape")
    if noise.shape != E.shape:
        raise ValueError("m_noise must have the shape of E")
    if sw.shape != w[:, 0].shape:
        raise ValueError("sw must have one entry per variant")
    w_sim = w + rng.normal(0.0, 1.0, size=w.shape) * sw[:, None]
    m_sim = E + rng.normal(0.0, 1.0, size=E.shape) * noise
    if plant is not None:
        m_sim = m_sim + np.asarray(plant, dtype=float)[:, None]
    return w_sim, m_sim


def simulate_rho(w, w_se, E, m_se, sw, delta, hgvs, n_draw=1, seed=0, r0=None,
                 s_e=None, z=None, concs=CONCS, keep_own_eb=False,
                 m_noise=None):
    """rho^sim_r = Spearman(delta_real, own_e.b^sim_r) for r = 1..n_draw.

    MECH frozen M-3 / M-4.  Every draw: `zero_epistasis_draw` (one
    np.random.default_rng(seed) drives the whole loop), then the project's
    UNMODIFIED pipeline (`own_eb_from_arrays`), then the frozen rho over the
    rows where both delta_real and the simulated own_e.b are finite.  `hgvs`
    is the variant vector the project's own rebuild needs to locate its
    A222V reference line (it is data the caller supplies, never a constant
    here).  If r0 is not None the planting term is drawn fresh per draw with
    u ~ N(0,1) (frozen M-4) and added to every condition.
    m_noise: the SD of the added m noise; None (default) = m_se, exactly as
    frozen M-3 writes it.  The SE COLUMN fed to the pipeline is always the
    recorded m_se, never m_noise -- see zero_epistasis_draw's note; pass
    m_noise = zeros for frozen G-M4's identity and nothing else changes.
    RESAMPLING UNIT: none -- this is a SIMULATION loop, not a bootstrap.
    Returns {"rho": (n_draw,), "own_eb": (n_draw, n) if keep_own_eb}.
    """
    w = np.asarray(w, dtype=float)
    delta = np.asarray(delta, dtype=float)
    hgvs = np.asarray(hgvs)
    rng = np.random.default_rng(seed)
    rhos = np.empty(int(n_draw), dtype=float)
    ebs = (np.empty((int(n_draw), w.shape[0]), dtype=float)
           if keep_own_eb else None)
    for r in range(int(n_draw)):
        plant = None
        if r0 is not None:
            u = rng.normal(0.0, 1.0, size=w.shape[0])
            plant = plant_term(r0, s_e, z, u)
        w_sim, m_sim = zero_epistasis_draw(w, E, m_se, sw, rng, plant=plant,
                                           m_noise=m_noise)
        eb = own_eb_from_arrays(w_sim, w_se, m_sim, m_se, hgvs, concs=concs)
        if ebs is not None:
            ebs[r] = eb
        rhos[r] = spearman(delta, eb)
    out = {"rho": rhos}
    if keep_own_eb:
        out["own_eb"] = ebs
    return out


def draw_summary(draws):
    """mean, SD, 2.5th and 97.5th percentiles of a simulation band.

    MECH frozen M-3's reporting set.  Returns a dict (n counts the finite
    draws).  The tail fraction at a caller-supplied threshold is
    `tail_fraction` -- this module never hard-codes the observed anchor.
    """
    a = np.asarray(draws, dtype=float)
    a = a[np.isfinite(a)]
    lo, hi = np.percentile(a, [2.5, 97.5])
    return {"mean": float(a.mean()), "sd": float(a.std(ddof=1)),
            "p2_5": float(lo), "p97_5": float(hi), "n": int(a.size)}


def tail_fraction(draws, threshold, side="le"):
    """Fraction of finite draws <= ("le") or >= ("ge") `threshold`."""
    a = np.asarray(draws, dtype=float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return float("nan")
    if side == "le":
        return float(np.mean(a <= float(threshold)))
    if side == "ge":
        return float(np.mean(a >= float(threshold)))
    raise ValueError("side must be 'le' or 'ge'")


def power_curve(r0_grid, draws_by_r0, r0_zero=None):
    """Planting power curve (MECH frozen M-4).

    r0_grid: the planted r0 values; draws_by_r0: {r0: array of observed rho}
    for every grid point INCLUDING r0 = 0.  The r0 = 0 band (or `r0_zero`
    if the grid key is 0.0) defines the tails: its 2.5th and 97.5th
    percentiles.  power(r0) = fraction of that r0's draws at or below the
    lower percentile for r0 < 0, at or above the upper percentile for r0 > 0,
    and at or below the lower percentile for r0 = 0 (the frozen text's
    "lower tail for r0 < 0, upper for r0 > 0"; r0 = 0 is reported for
    completeness).  Returns {"r0", "mean_rho", "power"} as arrays in grid
    order plus the two percentile bounds.
    """
    grid = [float(v) for v in r0_grid]
    key0 = 0.0 if r0_zero is None else float(r0_zero)
    if key0 not in {float(k) for k in draws_by_r0}:
        raise ValueError("power_curve needs the r0 = 0 simulation band")
    base = np.asarray(draws_by_r0[key0], dtype=float)
    base = base[np.isfinite(base)]
    q_lo, q_hi = np.percentile(base, [2.5, 97.5])
    mean_rho, power = [], []
    for r0 in grid:
        d = np.asarray(draws_by_r0[r0], dtype=float)
        d = d[np.isfinite(d)]
        mean_rho.append(float(d.mean()))
        if r0 < 0:
            power.append(float(np.mean(d <= q_lo)))
        elif r0 > 0:
            power.append(float(np.mean(d >= q_hi)))
        else:
            power.append(float(np.mean(d <= q_lo)))
    return {"r0": np.array(grid), "mean_rho": np.array(mean_rho),
            "power": np.array(power), "q_lo": float(q_lo),
            "q_hi": float(q_hi)}


def min_detectable_effect(r0_grid, power, target=0.80):
    """Minimum detectable |r0| at `target` power, by linear interpolation.

    Decision I5: interpolated separately for r0 < 0 and for r0 > 0 (each
    side gets the origin point (0, 0.025), the tail fraction the r0 = 0 band
    is defined by, then that side's grid points sorted by |r0| ascending);
    the first point at or above `target` is bracketed with the point
    immediately before it and linearly interpolated.  Returns
    {"neg", "pos", "headline"} where each is a float |r0| or the string
    "above the grid" for that side and "headline" is the smaller of the two
    (or "above the grid" if neither side reaches the target).  Both sides
    are always returned so the headline cannot hide one.
    """
    grid = np.asarray(r0_grid, dtype=float)
    pw = np.asarray(power, dtype=float)

    def one_side(mask):
        r = grid[mask]
        p = pw[mask]
        o = np.argsort(np.abs(r))
        r, p = np.abs(r[o]), p[o]
        r = np.concatenate([[0.0], r])
        p = np.concatenate([[0.025], p])
        hit = np.flatnonzero(p >= float(target))
        if hit.size == 0:
            return "above the grid"
        i = int(hit[0])
        if i == 0:
            return float(r[0])
        if p[i] == p[i - 1]:
            return float(r[i])
        frac = (target - p[i - 1]) / (p[i] - p[i - 1])
        return float(r[i - 1] + frac * (r[i] - r[i - 1]))

    neg = one_side(grid < 0)
    pos = one_side(grid > 0)
    numeric = [v for v in (neg, pos) if not isinstance(v, str)]
    if not numeric:
        head = "above the grid"
    else:
        head = float(min(numeric))
    return {"neg": neg, "pos": pos, "headline": head}


def attenuation_slope(r0_grid, mean_rho):
    """Least-squares slope of mean observed rho against r0 (frozen M-4)."""
    r = np.asarray(r0_grid, dtype=float)
    m = np.asarray(mean_rho, dtype=float)
    if r.size < 2:
        return float("nan")
    slope, intercept = np.polyfit(r, m, 1)
    return float(slope), float(intercept)


# ===========================================================================
# 7. The whole-placebo-test position bootstrap (MECH frozen M-6)
# ===========================================================================
def _sp_scipy(a, b):
    """scipy.stats.spearmanr's statistic -- the SLOW reference path only."""
    return float(spearmanr(a, b).statistic)


def _rho_masked(a, b, rho_fn, n_min=3):
    """rho over the rows where BOTH inputs are finite.

    DECISION (recorded before any Phase 4 number existed): a background's
    rho_b is Spearman(delta_b, own_e.b) over ITS OWN finite rows -- delta is
    (B, n_rows) with NaN wherever a background has no row (each
    background's rows exclude its own position, frozen M-6), so without
    this mask every rho would be NaN: scipy's rankdata propagates a single
    NaN through the whole rank vector (verified: rankdata([1, nan, 3, 4])
    returns four NaNs) and spearmanr returns NaN outright.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = np.isfinite(a) & np.isfinite(b)
    if int(m.sum()) < n_min:
        return float("nan")
    return float(rho_fn(a[m], b[m]))


def _placebo_from_ids(delta, own_eb, positions, t_idx, n_idx, ids, rho_fn):
    delta = np.asarray(delta, dtype=float)     # (B, n_rows)
    own_eb = np.asarray(own_eb, dtype=float)
    positions = np.asarray(positions)
    ids = np.asarray(ids, dtype=np.int64)
    uniq = np.unique(positions)
    rows_of = {p: np.flatnonzero(positions == p) for p in uniq}
    nulls = np.asarray(n_idx, dtype=int)
    n_null = nulls.size
    n_draw = ids.shape[0]
    rho_A = np.empty(n_draw)
    rho_N = np.empty((n_draw, n_null))
    k = np.empty(n_draw, dtype=np.int64)
    for d in range(n_draw):
        idx = np.concatenate([rows_of[uniq[s]] for s in ids[d]])
        e = own_eb[idx]
        vals = delta[:, idx]
        r_t = _rho_masked(vals[t_idx], e, rho_fn)
        rho_A[d] = r_t
        rn = np.array([_rho_masked(vals[j], e, rho_fn) for j in nulls],
                      dtype=float)
        rho_N[d] = rn
        finite = np.isfinite(rn)
        k[d] = int(np.sum(rn[finite] <= r_t))
    p = (1.0 + k) / (1.0 + n_null)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (rho_A - rho_N.mean(axis=1)) / rho_N.std(axis=1, ddof=0)
    return {"rho_A": rho_A, "rho_N": rho_N, "k": k, "p_spec_neg": p,
            "z": z}


def whole_placebo_boot_from_ids(delta, own_eb, positions, t_idx, n_idx, ids):
    """The frozen M-6 test, driven by PRE-DRAWN position ids.

    delta: (B, n_rows) array of per-background delta, NaN where a background
    has no row (each background's rows exclude its own position); own_eb and
    positions: (n_rows,).  t_idx / n_idx: indices of the target and of the
    78 null backgrounds in delta's first axis.  ids: (n_draw, nk) indices
    into np.unique(positions).  Each rho_b is taken over that background's
    own finite rows (_rho_masked), which is where the NaNs land.

    Per draw: resample POSITIONS with replacement and RE-DERIVE the target's
    rho, every null's rho, k = #{b : rho_b <= rho_target} and
    p_spec(neg) = (1+k)/(1+n_null) on the resampled rows.  RESAMPLING UNIT:
    position clusters (a re-derivation null, AGENTS 4).
    Returns dict with rho_A, rho_N, k, p_spec_neg, z
    (z = (rho_A - mean rho_N) / sd rho_N per draw).
    """
    return _placebo_from_ids(delta, own_eb, positions, t_idx, n_idx, ids,
                             rho_fn=lambda a, b: spearman(a, b))


def whole_placebo_reference(delta, own_eb, positions, t_idx, n_idx, ids):
    """SLOW, OBVIOUS reference for the M-6 bootstrap.

    Rebuilds position -> row indices from scratch with flatnonzero over the
    full positions array for every draw, concatenates, and computes
    scipy.stats.spearmanr per background over the finite pairs (the same
    rows the fast path keeps -- _rho_masked).  No indexing tricks.  Gate
    A2-G3 compares it with whole_placebo_boot_from_ids draw by draw on
    identical ids (tolerance 1e-12).
    """
    delta = np.asarray(delta, dtype=float)
    own_eb = np.asarray(own_eb, dtype=float)
    positions = np.asarray(positions)
    ids = np.asarray(ids, dtype=np.int64)
    uniq = np.unique(positions)
    nulls = np.asarray(n_idx, dtype=int)
    n_null = nulls.size
    n_draw = ids.shape[0]
    rho_A = np.empty(n_draw)
    rho_N = np.empty((n_draw, n_null))
    k = np.empty(n_draw, dtype=np.int64)
    for d in range(n_draw):
        idx = np.concatenate([np.flatnonzero(positions == uniq[s])
                              for s in ids[d]])
        e = own_eb[idx]
        r_t = _rho_masked(delta[t_idx, idx], e, _sp_scipy)
        rho_A[d] = r_t
        rn = np.array([_rho_masked(delta[j, idx], e, _sp_scipy)
                       for j in nulls], dtype=float)
        rho_N[d] = rn
        k[d] = int(np.sum(rn <= r_t))
    p = (1.0 + k) / (1.0 + n_null)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (rho_A - rho_N.mean(axis=1)) / rho_N.std(axis=1, ddof=0)
    return {"rho_A": rho_A, "rho_N": rho_N, "k": k, "p_spec_neg": p,
            "z": z}


def whole_placebo_boot(delta, own_eb, positions, t_idx, n_idx, n_draw=100,
                       seed=0):
    """The frozen M-6 test drawing its own position ids (seeded).

    See whole_placebo_boot_from_ids for the construction and the resampling
    unit (positions; every background's rho_b re-derived each draw).
    ids: one rng.integers(0, nk, nk) per draw from default_rng(seed), the
    same stream phase3_common.draw_ids consumes.
    """
    positions = np.asarray(positions)
    nk = np.unique(positions).size
    rng = np.random.default_rng(seed)
    ids = np.empty((int(n_draw), nk), dtype=np.int64)
    for i in range(int(n_draw)):
        ids[i] = rng.integers(0, nk, nk)
    return whole_placebo_boot_from_ids(delta, own_eb, positions, t_idx,
                                       n_idx, ids)


def observed_placebo(delta, own_eb, positions, t_idx, n_idx):
    """The observed (undrawn) M-6 statistic: every position exactly once.

    This is the identity target of gate G-M7: whole_placebo_boot_from_ids
    with ids = arange(nk) must return exactly these k and p_spec values.
    """
    positions = np.asarray(positions)
    nk = np.unique(positions).size
    ids = np.tile(np.arange(nk, dtype=np.int64), (1, 1))
    return whole_placebo_boot_from_ids(delta, own_eb, positions, t_idx,
                                       n_idx, ids)


# ===========================================================================
# 8. 2x2 geometry helpers
# ===========================================================================
def cell_labels(d3, dseq, thr=(12.0, 20.0, 40.0, 18.0, 25.0, 20.0, 40.0)):
    """Neighbour-arm cell labels, NEIGH frozen section 2, verbatim:

        C1  d3 <= 12 and dseq <= 20
        C2  d3 <= 12 and dseq > 40
        C3  d3 > 18 and dseq <= 25
        C4  d3 > 20 and dseq > 40
        ""  in every gap (the frozen text defines no cell there)

    Thresholds are parameters with those defaults so a toy can probe the
    boundaries; the frozen constants are the defaults.  First match wins;
    the four rules are mutually exclusive anyway.  NaN -> "".
    """
    t_c1_3, t_c1_s, t_c2_s, t_c3_3, t_c3_s, t_c4_3, t_c4_s = thr
    d3 = np.asarray(d3, dtype=float)
    dseq = np.asarray(dseq, dtype=float)
    out = np.full(d3.shape, "", dtype=object)
    ok = np.isfinite(d3) & np.isfinite(dseq)
    c1 = ok & (d3 <= t_c1_3) & (dseq <= t_c1_s)
    c2 = ok & (d3 <= t_c1_3) & (dseq > t_c2_s)
    c3 = ok & (d3 > t_c3_3) & (dseq <= t_c3_s)
    c4 = ok & (d3 > t_c4_3) & (dseq > t_c4_s)
    out[c4] = "C4"
    out[c3] = "C3"
    out[c2] = "C2"
    out[c1] = "C1"
    return out


def seq_separation(pos_a, pos_b):
    """s = |pos(a) - pos(b)| in residues (GB1D section 2; NEIGH dseq)."""
    return np.abs(np.asarray(pos_a, dtype=float) -
                  np.asarray(pos_b, dtype=float))


def interval_labels(values, rules, default=""):
    """Generic interval labelling: rules = [(lo, hi, label, lo_incl,
    hi_incl), ...], first match wins, `default` elsewhere.

    Used for the frozen separation strata (GB1D G-2: near 1-5, mid 6-15,
    far 16-54; and the Angstrom strata <8, 8-14, >14) and any other frozen
    stratum definition, so each stratum's inclusivity is stated in the call
    instead of being implied by code.
    """
    v = np.asarray(values, dtype=float)
    out = np.full(v.shape, default, dtype=object)
    free = np.isfinite(v)
    for lo, hi, label, lo_incl, hi_incl in rules:
        m = free & ((v >= lo) if lo_incl else (v > lo)) & \
                ((v <= hi) if hi_incl else (v < hi)) & \
                (out == default)
        out[m] = label
    return out


# ===========================================================================
# 9. AUROC and balanced-PR area (UTIL frozen section 3)
# ===========================================================================
def auroc(y_true, scores):
    """AUROC = Mann-Whitney U with average ranks (ties worth half).

    Identical in value to sklearn.metrics.roc_auc_score; gate A2-G3 checks
    that to 1e-12 on toy data with ties.  NaN if a class is absent.
    """
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(scores, dtype=float)
    m = np.isfinite(s)
    y, s = y[m], s[m]
    n1 = int(y.sum())
    n0 = int((~y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = _rank(s)
    u = float(r[y].sum()) - n1 * (n1 + 1) / 2.0
    return u / (n1 * n0)


def balanced_pr_curve(y_true, scores):
    """The balanced precision-recall curve (UTIL frozen section 3).

    balanced precision = TPR / (TPR + FPR), so a chance classifier sits at
    0.5.  Points sit at the DISTINCT score thresholds (ties grouped, scores
    processed high to low); the curve is anchored with one extra first point
    at recall 0 whose balanced precision is that of the top threshold
    (decision I6); the last point is recall 1 with balanced precision 0.5.
    Returns (recall, balanced_precision), both non-decreasing recall.
    """
    y = np.asarray(y_true).astype(bool)
    s = np.asarray(scores, dtype=float)
    m = np.isfinite(s)
    y, s = y[m], s[m]
    P = int(y.sum())
    N = int((~y).sum())
    if P == 0 or N == 0:
        return np.array([np.nan]), np.array([np.nan])
    order = np.argsort(-s, kind="mergesort")
    s_sorted, y_sorted = s[order], y[order]
    # last index of each distinct score (ties grouped)
    distinct = np.r_[np.diff(s_sorted) != 0, True]
    ends = np.flatnonzero(distinct)
    tp = np.cumsum(y_sorted)[ends].astype(float)
    fp = (ends + 1 - tp).astype(float)
    tpr = tp / P
    fpr = fp / N
    bp = tpr / (tpr + fpr)
    recall = tpr
    recall = np.r_[0.0, recall]
    bp = np.r_[bp[0], bp]
    return recall, bp


def balanced_pr_auc(y_true, scores):
    """Trapezoidal area under the balanced precision-recall curve (I6)."""
    from sklearn.metrics import auc
    r, bp = balanced_pr_curve(y_true, scores)
    if not np.isfinite(r).all() or not np.isfinite(bp).all():
        return float("nan")
    return float(auc(r, bp))


# ===========================================================================
# 10. Outcome-word functions of the five frozen blocks, exactly as written
# ===========================================================================
def _excludes_zero(lo, hi):
    return bool(lo > 0.0 or hi < 0.0)


def word_m1_partial(ci_lo, ci_hi, p_full, p_h):
    """MECH M-1, verbatim: PARTIAL-SURVIVES iff the CI excludes zero in the
    negative direction AND p_spec(neg) <= 0.05 (full) AND <= 0.10 (H);
    PARTIAL-WEAKENS iff the CI excludes zero in the negative direction but a
    p_spec condition fails; PARTIAL-DOES-NOT-SURVIVE iff the CI includes
    zero or the sign reverses."""
    if ci_hi < 0.0:
        if p_full <= 0.05 and p_h <= 0.10:
            return "PARTIAL-SURVIVES"
        return "PARTIAL-WEAKENS"
    return "PARTIAL-DOES-NOT-SURVIVE"


def word_m3_artifact(obs_rho, p2_5):
    """MECH M-3, verbatim: EXCESS-OVER-ARTIFACT iff -0.088118 is at or below
    the 2.5th percentile of the primary simulation; CONSISTENT-WITH-ARTIFACT
    otherwise.  `obs_rho` is the observed anchor, `p2_5` the simulation's
    2.5th percentile (neither is a constant of this module)."""
    return ("EXCESS-OVER-ARTIFACT" if float(obs_rho) <= float(p2_5)
            else "CONSISTENT-WITH-ARTIFACT")


def word_m5_carry(ci_within, p_within, ci_between, p_between):
    """MECH M-5, verbatim: WITHIN-CARRIED iff rho_within's CI excludes zero
    in the negative direction AND its p_spec(neg) <= 0.05 AND the between
    component does not meet both conditions; BETWEEN-CARRIED iff the
    reverse; BOTH-CARRY iff both meet both conditions; NEITHER-CARRIES
    otherwise."""
    w_ok = ci_within[1] < 0.0 and p_within <= 0.05
    b_ok = ci_between[1] < 0.0 and p_between <= 0.05
    if w_ok and b_ok:
        return "BOTH-CARRY"
    if w_ok:
        return "WITHIN-CARRIED"
    if b_ok:
        return "BETWEEN-CARRIED"
    return "NEITHER-CARRIES"


def word_m6_stable(probability):
    """MECH M-6, verbatim: STABLE iff the probability is >= 0.80; FRAGILE
    iff it is < 0.50; MODERATE otherwise."""
    p = float(probability)
    if p >= 0.80:
        return "STABLE"
    if p < 0.50:
        return "FRAGILE"
    return "MODERATE"


def word_conditioning(ci_lo, ci_hi, margin=0.02):
    """UTIL U-1 / U-2, verbatim, clauses tested in the frozen order (I7):
    CONDITIONING-HELPS iff the CI lies entirely above zero;
    CONDITIONING-HURTS iff it lies entirely below zero;
    EQUIVALENT iff it lies inside (-margin, +margin);
    INCONCLUSIVE otherwise."""
    if ci_lo > 0.0:
        return "CONDITIONING-HELPS"
    if ci_hi < 0.0:
        return "CONDITIONING-HURTS"
    if ci_lo > -float(margin) and ci_hi < float(margin):
        return "EQUIVALENT"
    return "INCONCLUSIVE"


def word_underpowered(n_class_a, n_class_b, min_n=15):
    """UTIL, verbatim: UNDERPOWERED iff either class has fewer than 15
    variants; then no word is given.  Returns "UNDERPOWERED" or None."""
    if int(n_class_a) < int(min_n) or int(n_class_b) < int(min_n):
        return "UNDERPOWERED"
    return None


def gb1_model_decays(ci_lo, ci_hi):
    """GB1D G-1, verbatim iff-condition as a BOOL (decision I8):
    MODEL-DECAYS iff the CI of the mean lambda_model lies entirely below
    zero."""
    return bool(ci_hi < 0.0)


def gb1_data_decays(ci_lo, ci_hi):
    """GB1D G-1, verbatim iff-condition as a BOOL (I8): DATA-DECAYS iff the
    CI of the mean lambda_data lies entirely below zero."""
    return bool(ci_hi < 0.0)


def gb1_locality_differs(ci_lo, ci_hi):
    """GB1D, verbatim iff-condition as a BOOL (I8): LOCALITY-DIFFERS iff the
    CI of the mean d_b excludes zero."""
    return bool(_excludes_zero(ci_lo, ci_hi))


def gb1_separation(ci_lo, ci_hi):
    """GB1D G-2, verbatim: SEPARATION-MATTERS iff the CI of the mean paired
    difference (near - far) excludes zero; SEPARATION-NOT-RESOLVED
    otherwise -- reported as "n cannot resolve this", never as "no
    relationship"."""
    return ("SEPARATION-MATTERS" if _excludes_zero(ci_lo, ci_hi)
            else "SEPARATION-NOT-RESOLVED")


def word_neighbour(p_nb, n_nb, n_min=30):
    """NEIGH section 5, verbatim: POSITION-SPECIFIC iff |NB| >= 30 AND
    p_NB(neg) <= 0.05; REGION-LIKE iff |NB| >= 30 AND p_NB(neg) > 0.10;
    UNRESOLVED iff |NB| >= 30 and 0.05 < p_NB(neg) <= 0.10; UNDERPOWERED
    iff |NB| < 30 (no interpretation)."""
    if int(n_nb) < int(n_min):
        return "UNDERPOWERED"
    if float(p_nb) <= 0.05:
        return "POSITION-SPECIFIC"
    if float(p_nb) > 0.10:
        return "REGION-LIKE"
    return "UNRESOLVED"


def word_distance(ci_d3, ci_dseq):
    """NEIGH section 6, verbatim: 3D-LOCAL iff the d3 partial's CI excludes
    zero and the dseq partial's CI includes zero; SEQUENCE-LOCAL iff the
    reverse; BOTH-LOCAL iff both exclude zero; NEITHER-RESOLVED iff both
    include zero."""
    a = _excludes_zero(ci_d3[0], ci_d3[1])
    b = _excludes_zero(ci_dseq[0], ci_dseq[1])
    if a and b:
        return "BOTH-LOCAL"
    if a:
        return "3D-LOCAL"
    if b:
        return "SEQUENCE-LOCAL"
    return "NEITHER-RESOLVED"


def word_ladder(ci_lo, ci_hi, p_spec_neg):
    """LADDER section 3, verbatim: MODEL-REPLICATES iff the CI of rho_A222V
    on H lies below zero AND p_spec_H(neg) <= 0.10; MODEL-DOES-NOT-
    REPLICATE iff the CI includes zero or the sign reverses; MODEL-PARTIAL
    otherwise."""
    if ci_hi < 0.0 and float(p_spec_neg) <= 0.10:
        return "MODEL-REPLICATES"
    if ci_lo > 0.0 or (ci_lo <= 0.0 <= ci_hi):
        return "MODEL-DOES-NOT-REPLICATE"
    return "MODEL-PARTIAL"
