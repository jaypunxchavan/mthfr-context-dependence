"""scripts/lib/phase2_diag4.py -- shared helpers for the Phase 2 diagnostics
IV session (tasks D18-D22 of
docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV.md).

WHY THIS MODULE EXISTS
----------------------
D18-D21 all need the same machinery that script 144 used for D15: the per-view
row stores, the whole-position deletion function, `stats()`, the
matched-deletion control loop and the position-cluster bootstrap.  Task-doc
rule 15 says: import an earlier script only if that is safe, otherwise
TRANSCRIBE the needed function verbatim under a QUOTED SOURCE comment with
file and line numbers and GATE the transcription against the original's
printed output.  Script 144 keeps `Store`, `stats`, `pos_cluster_boot`,
`grad_boot` and the geometry bookkeeping nested inside `main()` (they are not
importable), so they are transcribed here, line-numbered, and gated in
scripts/148 (D18-G1 against D15's printed values, and the bootstrap
transcription against all sixteen CIs in
docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D15_FULL_OUTPUT.txt).

scripts/lib/phase2_diag.py and scripts/lib/phase2_diag3.py ARE NOT MODIFIED,
and neither is script 144 (it is read, never edited) nor any script numbered
147 or lower.  This is a NEW module.

NO torch, NO esm, NO thermompnn, NO Biopython import anywhere in this file.

TRANSCRIBED vs NEW
------------------
TRANSCRIBED from scripts/144_phase2_diag3_farvariants.py (closure variables
lifted to arguments; NO arithmetic changed -- the comment on each says so):
    rho_of .................... lines 199-202
    Store ..................... lines 206-223
    keep_from_removed ......... lines 411-417
    cluster_index ............. lines 444-456
    pos_cluster_boot_144 ...... lines 458-479
    grad_boot ................. lines 490-500
    build_view_state .......... lines 296-309 (store construction) and
                                lines 365-401 (geometry bookkeeping)
    stats ..................... lines 419-441
NEW (this session):
    pos_cluster_boot_144_preadrawn   -- the transcribed routine driven by
        PRE-DRAWN cluster-index arrays instead of an internal rng; one line
        differs (`cnt = np.bincount(ids[i], ...)`), everything else is the
        transcription.  Used only so the routine under test and the
        reference implementation can be driven with the SAME sampled
        positions (D18-G3).
    retained_parts .................. retained rows grouped by cluster, in
        FIRST-APPEARANCE order of the retained rows (scripts/lib/stats.py
        lines 34-36 convention -- Phase 1's), returning labels/sizes/base/
        rows_sorted/d/y.
    pos_cluster_boot_corrected ...... THE CORRECTED ROUTINE: each drawn
        cluster contributes ALL of its rows (see defect note below).
    pos_cluster_boot_corrected_from_ids  same, driven by pre-drawn ids (for
        the gate against the reference).
    reference_boot .................. the slow, obvious reference: for each
        draw, `idx = np.concatenate([rows_of[p] for p in ids])` and
        `rho = scipy.stats.spearmanr(x[idx], y[idx])`.
    flag11 ......................... the rule-11 INSIDE / OUTSIDE / MARGINAL
        flagger used by D19-D21.

THE DEFECT D18 EXISTS TO CATCH (stated before any run, from reading the
source; the numbers are produced by scripts/148, not assumed here)
-------------------------------------------------------------------
Script 144 line 477 builds each draw's row index as

    idx = np.repeat(kept_base, cnt)[rep] + j

where `j` (line 475) is the occurrence index WITHIN a cluster's draw slot, not
the row offset within that cluster's rows.  A correct position-cluster draw
must take EVERY row of every sampled cluster; this line takes `cnt[s]` row
offsets 0..cnt[s]-1 from base `kept_base[... ]`, so a draw contains exactly
m = sum(cnt) = nk ROWS (one per sampled cluster occurrence, plus any rows of
the NEXT cluster when cnt[s] exceeds the cluster size) instead of the
~sum of the sampled clusters' sizes.  The consequences are a much wider CI
and a centre displaced from the point estimate -- exactly the two symptoms
D18 was asked to investigate.  This paragraph is a prediction from the code;
scripts/148 prints the measured draw-by-draw disagreement against the
reference implementation, and the gate result governs.

RESAMPLING UNIT
---------------
A222V's rho on a row subset: POSITION CLUSTER (whole retained target
positions), 10,000 draws, SEED=0.  Nothing else in this module resamples.

Usage (helpers only -- no script runs on import):
    from scripts.lib import phase2_diag4 as p4
"""

import numpy as np
from scipy.stats import spearmanr

from . import phase2_diag3 as p3


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 199-202
#
#     def rho_of(x, y):
#         if len(x) < 3:
#             return float("nan")
#         return float(spearmanr(x, y).statistic)
# ==========================================================================
def rho_of(x, y):
    if len(x) < 3:
        return float("nan")
    return float(spearmanr(x, y).statistic)


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 205-223
# (module-level class; no closure variables)
# ==========================================================================
class Store:
    """Per-view row store.  Rows are grouped by TARGET POSITION so that any
    whole-position deletion is a cheap numpy boolean mask."""

    def __init__(self, pos, delta, y, POSV):
        self.POSV = POSV
        self.delta = delta
        self.y = y
        self.pos = pos
        self.code = np.searchsorted(POSV, pos)

    def rho(self, keep_pos):
        """keep_pos: boolean array over POSV."""
        m = keep_pos[self.code]
        return rho_of(self.delta[m], self.y[m])

    def n_rows(self, keep_pos):
        return int(keep_pos[self.code].sum())


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 411-417
# (verbatim: no closure variables in the original body)
# ==========================================================================
def keep_from_removed(POSV, resolved, removed):
    """Whole positions in `removed` are deleted; everything else that is
    resolved is kept.  THE SAME FUNCTION is used by the S1 filter, by the
    R = 0 baseline and by the matched-deletion control, which is what makes
    gate D15-G2 possible."""
    rm = np.isin(POSV, np.asarray(sorted(removed), dtype=POSV.dtype))
    return resolved & (~rm)


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 296-309
# (store construction) and lines 365-401 (geometry bookkeeping).
# Closure variables lifted: `bgs` and `ca` come from the build state `st`.
# ==========================================================================
def build_view_state(st):
    """Per-view state used by every D18-D21 computation.

    Returns {view: dict(view, POSV, A, B, resolved, d3, univ, univ_pos)}.
    Arithmetic and ordering are script 144's; only the closure variables
    (`store`, `geo`, `ca`, `bgs`) are passed in instead of captured.
    """
    bgs, ca, A = st["bgs"], st["ca"], st["A"]
    out = {}
    for view in p3.VIEWS:
        hview = (view == "H")
        ra = A.a222v_rows
        if hview:
            ra = ra[ra.position.isin(A.Hset)]
        POSV = np.array(sorted(set(ra.position.to_numpy(int).tolist())))
        sa = Store(ra.position.to_numpy(int), ra.delta.to_numpy(float),
                   ra.own_e_b.to_numpy(float), POSV)
        sb = {}
        for b in bgs:
            r = p3.pdg.usable_rows(A, b, hview=hview)
            sb[b] = Store(r.position.to_numpy(int), r.delta.to_numpy(float),
                          r.own_e_b.to_numpy(float), POSV)
        resolved = np.array([p in ca["A"] for p in POSV])
        d3 = np.array([p3.d3_of(int(p), ca) for p in POSV])
        univ = np.flatnonzero(resolved)
        out[view] = dict(view=view, POSV=POSV, A=sa, B=sb,
                         resolved=resolved, d3=d3, univ=univ,
                         univ_pos=POSV[univ])
    return out


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 419-441.
# Closure variables lifted to arguments: `store[view]["A"]` -> vs["A"],
# `store[view]["B"]` -> vs["B"], `store[view]["POSV"]` -> vs["POSV"], and
# `bgs / N_ids / resN / res96 / df3` from the build state.  NO arithmetic,
# key name or denominator changed.
# ==========================================================================
def stats(vs, bgs, N_ids, resN, res96, df3, keep):
    """All statistics for one (variant, view, row set)."""
    POSV = vs["POSV"]
    sa = vs["A"]
    rho_a = sa.rho(keep)
    rho_b = {b: vs["B"][b].rho(keep) for b in bgs}
    rows = np.array([vs["B"][b].n_rows(keep) for b in bgs])
    posn = int(keep.sum())
    out = dict(rho_a=rho_a, rho_b=rho_b, rows=rows,
               n_pos=posn, n_rows_a=int(keep[sa.code].sum()))
    # p_spec on both denominators
    for lbl, ids in (("n78", N_ids), ("n67", resN)):
        arr = np.array([rho_b[b] for b in ids], float)
        k = int((arr <= rho_a).sum())
        out[f"k_{lbl}"] = k
        out[f"p_{lbl}"] = (1 + k) / (1 + len(ids))
        out[f"aob_{lbl}"] = sorted(b for b in ids if rho_b[b] <= rho_a)
    # gradient on both denominators
    for lbl, ids in (("n67", resN), ("n85", res96)):
        x = np.array([rho_b[b] for b in ids], float)
        g = np.array([float(df3.loc[b, "d3_CA"]) for b in ids], float)
        out[f"grad_{lbl}"] = float(spearmanr(x, g).statistic)
    return out


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 443-456
# (cluster_index: unchanged; `npos` comes from POSV as in the original)
# ==========================================================================
def cluster_index(POSV, code, keep):
    """Rows grouped by retained cluster, for a vectorised cluster bootstrap.

    `sizes` and `base` are defined over ALL npos position slots (zero size
    for a slot with no rows), so they can be indexed by `keep` directly."""
    npos = len(POSV)
    sel = np.flatnonzero(keep[code])
    c = code[sel]
    sizes = np.bincount(c, minlength=npos)
    order = np.argsort(c, kind="stable")
    rows_sorted = sel[order]
    base = np.concatenate([[0], np.cumsum(sizes)])[:-1]
    return rows_sorted, sizes, base, npos


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 458-479
# Closure variables lifted: `store[view]["A"]` -> sa,
# `store[view]["POSV"]` -> POSV.  Body otherwise line-for-line.
# ==========================================================================
def pos_cluster_boot_144(sa, POSV, keep, n_boot, rng):
    """POSITION-CLUSTER bootstrap: whole retained target positions are
    resampled with replacement; all their rows come with them."""
    rows_sorted, sizes, base, npos = cluster_index(POSV, sa.code, keep)
    d, y = sa.delta[rows_sorted], sa.y[rows_sorted]
    kept_sizes = sizes[keep]
    kept_base = base[keep]
    draws = np.empty(n_boot, float)
    nk = len(kept_sizes)
    for i in range(n_boot):
        cnt = np.bincount(rng.integers(0, nk, nk), minlength=nk)
        m = int(cnt.sum())
        rep = np.repeat(np.arange(nk), cnt)
        cum = np.concatenate([[0], np.cumsum(cnt)])
        j = np.arange(m) - np.repeat(cum[:-1], cnt)
        # `kept_base`/`j` are offsets into rows_sorted, i.e. into
        # the RETAINED arrays d and y -- NOT into the original rows.
        idx = np.repeat(kept_base, cnt)[rep] + j
        draws[i] = rho_of(d[idx], y[idx])
    return draws


# ==========================================================================
# THE ROUTINE UNDER TEST, DRIVEN BY PRE-DRAWN CLUSTER-INDEX ARRAYS
# Identical to the transcription above except for the SINGLE line marked
# <<< ONLY CHANGE: the cluster counts come from ids[i] instead of from
# rng.integers(0, nk, nk).  scripts/148 gates this variant against the
# verbatim transcription (identical output for an identical draw stream)
# before it is used in D18-G3.
# ==========================================================================
def pos_cluster_boot_144_preadrawn(sa, POSV, keep, ids):
    """ids: array of shape (n_draw, nk) of pre-drawn cluster indices, in
    script 144's index space (cluster index = position among the RETAINED
    positions in ASCENDING POSV order, i.e. `sizes[keep]` order)."""
    rows_sorted, sizes, base, npos = cluster_index(POSV, sa.code, keep)
    d, y = sa.delta[rows_sorted], sa.y[rows_sorted]
    kept_sizes = sizes[keep]
    kept_base = base[keep]
    n_draw = len(ids)
    draws = np.empty(n_draw, float)
    nk = len(kept_sizes)
    for i in range(n_draw):
        cnt = np.bincount(ids[i], minlength=nk)      # <<< ONLY CHANGE
        m = int(cnt.sum())
        rep = np.repeat(np.arange(nk), cnt)
        cum = np.concatenate([[0], np.cumsum(cnt)])
        j = np.arange(m) - np.repeat(cum[:-1], cnt)
        idx = np.repeat(kept_base, cnt)[rep] + j
        draws[i] = rho_of(d[idx], y[idx])
    return draws


# ==========================================================================
# TRANSCRIBED -- scripts/144_phase2_diag3_farvariants.py lines 490-500
# Closure variables lifted: `df3` (and p3.pdg.pct_ci, unchanged).
# ==========================================================================
def grad_boot(rho_b, ids, df3, n_boot, rng):
    x = np.array([rho_b[b] for b in ids], float)
    g = np.array([float(df3.loc[b, "d3_CA"]) for b in ids], float)
    n = len(ids)
    draws = np.empty(n_boot, float)
    for i in range(n_boot):
        k = rng.integers(0, n, n)
        draws[i] = spearmanr(x[k], g[k]).statistic
    fin = draws[~np.isnan(draws)]
    lo, hi, v = p3.pdg.pct_ci(fin)
    return lo, hi, v, int(np.isnan(draws).sum())


# ==========================================================================
# NEW -- retained rows grouped by cluster in FIRST-APPEARANCE order.
# This is scripts/lib/stats.py lines 34-36 (`_cluster_indices`: clusters =
# d[cluster_col].unique(), i.e. first appearance in row order) applied to the
# retained subset, so that the corrected routine's integer -> cluster map is
# the same one Phase 1's `rng.choice(clusters, ...)` used.
# ==========================================================================
def retained_parts(sa, POSV, keep):
    """Retained rows of one Store, grouped by cluster in first-appearance
    order of the retained rows (Phase 1's convention).

    Returns dict(labels, sizes, base, rows_sorted, d, y, n_rows).
      labels : (nk,) position labels, first-appearance order
      sizes  : (nk,) rows per retained cluster
      base   : (nk,) start offset of each cluster in rows_sorted
      rows_sorted : row indices (into sa.delta) grouped by cluster, and
                within a cluster in ORIGINAL row order -- identical to the
                row order Phase 1's `pos[c]` produces.
    """
    sel = np.flatnonzero(keep[sa.code])
    pos_sel = sa.pos[sel]
    # first-appearance order: np.unique gives sorted labels + first index;
    # argsort of the first indices yields first-appearance order.
    uniq_sorted, first = np.unique(pos_sel, return_index=True)
    labels = uniq_sorted[np.argsort(first, kind="stable")]
    nk = len(labels)
    lookup = {int(p): i for i, p in enumerate(labels)}
    fa = np.array([lookup[int(p)] for p in pos_sel], dtype=np.int64)
    sizes = np.bincount(fa, minlength=nk)
    order = np.argsort(fa, kind="stable")
    rows_sorted = sel[order]
    base = np.concatenate([[0], np.cumsum(sizes)])[:-1]
    return dict(labels=labels, sizes=sizes, base=base,
                rows_sorted=rows_sorted, d=sa.delta[rows_sorted],
                y=sa.y[rows_sorted], n_rows=len(rows_sorted))


# ==========================================================================
# NEW -- THE CORRECTED POSITION-CLUSTER BOOTSTRAP (D18.4)
# Each sampled cluster contributes ALL of its rows, concatenated in draw
# order -- the construction scripts/lib/stats.py lines 51-53 performs and
# the construction script 144's line 477 does not.
# ==========================================================================
def pos_cluster_boot_corrected_from_ids(parts, ids):
    """ids: (n_draw, nk) pre-drawn cluster indices in `parts`' index space
    (first-appearance order).  Returns one rho per draw."""
    d, y, sizes, base = parts["d"], parts["y"], parts["sizes"], parts["base"]
    n_draw = len(ids)
    draws = np.empty(n_draw, float)
    for i in range(n_draw):
        occ = ids[i]                                  # length nk, draw order
        sz = sizes[occ]
        lens = int(sz.sum())
        starts = np.concatenate([[0], np.cumsum(sz)])[:-1]
        rows_occ = np.repeat(base[occ], sz)
        idx = rows_occ + (np.arange(lens) - np.repeat(starts, sz))
        draws[i] = rho_of(d[idx], y[idx])
    return draws


def pos_cluster_boot_corrected(sa, POSV, keep, n_boot, rng):
    """Corrected routine, drawing its own cluster indices: each draw samples
    nk clusters with replacement via rng.integers(0, nk, nk) (the same
    stream Generator.choice(pop, size, replace=True) consumes -- verified in
    scripts/148) over the FIRST-APPEARANCE cluster order (Phase 1's)."""
    parts = retained_parts(sa, POSV, keep)
    nk = len(parts["labels"])
    ids = np.empty((n_boot, nk), dtype=np.int64)
    for i in range(n_boot):
        ids[i] = rng.integers(0, nk, nk)
    return pos_cluster_boot_corrected_from_ids(parts, ids)


def ids_translation(sa, POSV, keep, ids_asc):
    """Map cluster indices from script 144's ASCENDING index space to the
    FIRST-APPEARANCE index space of retained_parts(), elementwise, so that
    both implementations are driven by the same pre-drawn positions."""
    rows_sorted, sizes, base, npos = cluster_index(POSV, sa.code, keep)
    asc_labels = POSV[keep]                    # ascending, length nk
    parts = retained_parts(sa, POSV, keep)
    fa_lookup = {int(p): i for i, p in enumerate(parts["labels"])}
    map_asc_to_fa = np.array([fa_lookup[int(p)] for p in asc_labels],
                             dtype=np.int64)
    return map_asc_to_fa[ids_asc], parts, asc_labels


# ==========================================================================
# NEW -- THE SLOW, OBVIOUS REFERENCE IMPLEMENTATION (D18.3)
#   for a pre-drawn array of sampled position labels `ids`:
#       idx = np.concatenate([rows_of[p] for p in ids])
#       rho = scipy.stats.spearmanr(x[idx], y[idx])
# No clever indexing of any kind.
# ==========================================================================
def reference_boot(sa, labels, ids):
    """labels: (nk,) position labels aligned with the index space of `ids`
    (one label per integer).  ids: (n_draw, nk) pre-drawn label indices.
    x/y are the Store's FULL row arrays; rows_of is rebuilt from them, so
    nothing about the cluster layout is reused from the routine under test."""
    x, y = sa.delta, sa.y
    rows_of = {int(p): np.flatnonzero(sa.pos == p) for p in labels}
    n_draw = len(ids)
    draws = np.empty(n_draw, float)
    for i in range(n_draw):
        idx = np.concatenate([rows_of[int(labels[s])] for s in ids[i]])
        draws[i] = float(spearmanr(x[idx], y[idx]).statistic)
    return draws


# ==========================================================================
# NEW -- rule 11 flagging (D19-D21): INSIDE / OUTSIDE / MARGINAL
#   MARGINAL = outside but within 0.002 of a bound, OR the empirical
#               one-sided fraction on the outside is between 0.01 and 0.05.
# ==========================================================================
def flag11(v, draws, tol=0.002):
    """v: the observed value; draws: the matched-control draw array.
    Returns dict(lo, hi, frac_le, frac_ge, dist, flag)."""
    a = np.asarray(draws, float)
    lo, hi = np.percentile(a, [2.5, 97.5])
    v = float(v)
    frac_le = float((a <= v).mean())
    frac_ge = float((a >= v).mean())
    dist = float(min(abs(v - lo), abs(v - hi)))
    if lo <= v <= hi:
        return dict(lo=float(lo), hi=float(hi), frac_le=frac_le,
                    frac_ge=frac_ge, dist=dist, flag="INSIDE")
    tail = frac_le if v < lo else frac_ge
    marginal = (dist <= tol) or (0.01 <= tail <= 0.05)
    return dict(lo=float(lo), hi=float(hi), frac_le=frac_le,
                frac_ge=frac_ge, dist=dist,
                flag="MARGINAL" if marginal else "OUTSIDE")


def banner(t, ch="="):
    p3.banner(t, ch)
