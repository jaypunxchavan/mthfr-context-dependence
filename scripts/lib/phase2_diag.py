"""scripts/lib/phase2_diag.py -- shared loader for the Phase 2 diagnostics
session (tasks D1-D8 of docs/tasks/phase2-diagnostics-locality-magnitude/
PHASE2_DIAGNOSTICS.md).

WHY THIS MODULE EXISTS
----------------------
The diagnostics session must not reimplement script 125's rho_b
construction.  Per PHASE2_DIAGNOSTICS.md rule 2 ("confirm inputs match
before recomputing anything") and rule 10 ("say so plainly and adapt
transparently"), this module IMPORTS scripts/125_phase2_analysis.py and
drives its own --mode phase2 build path verbatim:

    A = s125.Analysis("phase2")   # 125's build_frame() + holdout()
    s125.build_phase2(A)          # 125's own roster/join/delta construction
    A.finalize()                  # 125's arm sets + G-C assert
    A.point_rhos()                # 125's point_rhos()

Nothing in 125 is modified, subclassed, or re-derived here.  Script 125's
module-level code only defines N_BOOT/N_PERM/SEED/ROOT and t0; it does not
run anything at import time (its main() is guarded by
`if __name__ == "__main__"`), so importing is side-effect free apart from
125's own printed construction/gate output.

WHAT IS *TRANSCRIBED* RATHER THAN IMPORTED, AND WHY
----------------------------------------------------
Script 125 computes its H-view rhos inline inside main() (lines 531-539),
not in a function, so it cannot be called.  The exact source lines are
reproduced verbatim below under a QUOTED SOURCE comment.  This is a
line-for-line transcription of 125's own code, not a reimplementation from
memory, and D1-G1 gates the result against the values 125 actually printed
in data/processed/phase2/analysis_run.log.

NO BOOTSTRAP LIVES HERE.  The position-cluster bootstrap inside
Analysis.bootstrap() is deliberately NOT invoked: it is 10,000 draws x 97
rho recomputations and takes hours.  The diagnostics tasks that need
uncertainty (D2, D4, D6) use a BACKGROUND-LEVEL bootstrap -- resampling
which backgrounds were drawn, each background's already-computed rho_b held
fixed -- which is a different resampling unit from Phase 2's own primary
analysis (resampling positions within a background).  Every script that
uses the background-level bootstrap states this in its own docstring.

Resampling unit used by each task (single source of truth):
  * Phase 2 primary (script 125): POSITION within a background.
  * D2, D4, D6 diagnostics:      BACKGROUND (which of the 96 were drawn).
  * D5:                          BACKGROUND (D_site is a mean over arms).
  * D8, D3, D7:                  none -- exact rank counts, no resampling.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
S125_PATH = ROOT / "scripts" / "125_phase2_analysis.py"

# The exact join / column names script 125 uses for delta_b, quoted from
# scripts/125_phase2_analysis.py:
#   build_frame():   atlas = pd.read_csv(ROOT / "data/processed/"
#                       "task32_analysis_table.csv")
#                    frame = atlas.dropna(subset=["delta_esm", "own_e_b"])
#   build_phase2():  f = pd.read_csv(.../phase2/bg_<bg_id>.csv)
#                    m = frame.merge(f[["position","mut_aa","score"]],
#                                    on=["position","mut_aa"], how="left")
#                    m = m[m.score.notna()]
#                    m["delta"] = m.score - m.esm2_score
#   a222v (PIN-3):   A.a222v_rows = frame[["position","delta_esm",
#                                         "own_e_b","region"]].rename(
#                                         columns={"delta_esm": "delta"})
# So esm2_score comes from task32_analysis_table.csv, score from
# data/processed/phase2/bg_<bg_id>.csv, joined on (position, mut_aa), and
# delta_b(v) = score_b(v) - esm2_score(v).  A222V's own "score_b" is the
# cached task32 column delta_esm.
DELTA_DEF = "delta_b(v) = score_b(v) - esm2_score(v)"
ESM2_SOURCE = "data/processed/task32_analysis_table.csv::esm2_score"
BG_SCORE_SOURCE = "data/processed/phase2/bg_<bg_id>.csv::score"
DELTA_JOIN = "frame.merge(bg[[position, mut_aa, score]], on=[position, mut_aa], how='left')"


def load_script125():
    """Import scripts/125_phase2_analysis.py as a module object.

    The filename starts with a digit so a normal `import` statement is
    illegal; importlib is the only route.  125 does not execute main() on
    import, so this is side-effect free apart from 125's own printing.
    """
    if not S125_PATH.exists():
        raise FileNotFoundError(f"script 125 not found at {S125_PATH}")
    spec = importlib.util.spec_from_file_location("s125_phase2_analysis",
                                                  S125_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build(verbose=True):
    """Drive script 125's --mode phase2 build path and return (s125, A).

    `verbose=False` suppresses 125's own construction/gate printing for
    use inside larger scripts whose own output should dominate; the gates
    still run (they call gfail -> sys.exit(1) on failure).
    """
    s125 = load_script125()
    if not verbose:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            A = s125.Analysis("phase2")
            s125.build_phase2(A)
            A.finalize()
            A.point_rhos()
        return s125, A
    A = s125.Analysis("phase2")
    s125.build_phase2(A)
    A.finalize()
    A.point_rhos()
    return s125, A


# --------------------------------------------------------------------------
# QUOTED SOURCE -- scripts/125_phase2_analysis.py, main(), lines 531-539:
#
#         for b in A.bgs:
#             r = A.bg_rows[b]
#             rh = r[r.position.isin(A.Hset)]
#             point_h[b] = float(spearmanr(rh.delta.to_numpy(float),
#                                          rh.own_e_b.to_numpy(float)
#                                          ).statistic)
#         ah = A.a222v_rows[A.a222v_rows.position.isin(A.Hset)]
#         rho_h_a = float(spearmanr(ah.delta.to_numpy(float),
#                                   ah.own_e_b.to_numpy(float)).statistic)
# --------------------------------------------------------------------------
def point_rhos_H(A):
    """H-view rhos: 125's lines 531-539 transcribed verbatim.

    Returns (point_h_dict, rho_a222v_H).
    """
    point_h = {}
    for b in A.bgs:
        r = A.bg_rows[b]
        rh = r[r.position.isin(A.Hset)]
        point_h[b] = float(spearmanr(rh.delta.to_numpy(float),
                                     rh.own_e_b.to_numpy(float)
                                     ).statistic)
    ah = A.a222v_rows[A.a222v_rows.position.isin(A.Hset)]
    rho_h_a = float(spearmanr(ah.delta.to_numpy(float),
                              ah.own_e_b.to_numpy(float)).statistic)
    return point_h, rho_h_a


def rho_table(A, point_h=None, rho_a222v_H=None):
    """Assemble the canonical per-background rho table.

    Columns: bg_id, arm, position, dist_222, rho_full, rho_H
      * arm/position from the roster 125 used (A.arm, A.own_pos).
      * dist_222 = |position - 222|, computed here, used by D2.
      * rho_full = A.point[b]               (125's Analysis.point_rhos())
      * rho_H    = point_rhos_H(A)          (125's main(), transcribed)
    A222V itself is NOT a row of this table: it is in neither arm S nor the
    null set N (frozen section 3, confirmed by 125's own print).  Its two
    rhos are returned separately as the p_spec thresholds.
    """
    if point_h is None or rho_a222v_H is None:
        point_h, rho_a222v_H = point_rhos_H(A)
    recs = []
    for b in A.bgs:
        recs.append({
            "bg_id": b,
            "arm": A.arm[b],
            "position": A.own_pos[b],
            "dist_222": abs(A.own_pos[b] - 222),
            "rho_full": A.point[b],
            "rho_H": point_h[b],
        })
    df = pd.DataFrame(recs).sort_values("bg_id").reset_index(drop=True)
    return df, point_h, rho_a222v_H


def usable_rows(A, bg_id, hview=False):
    """The exact rows 125 used for this background's rho_b.

    Full view : A.bg_rows[bg_id] as built by 125 (post score-join, post
                NaN-score drop, G-C own-position exclusion already applied).
    H view    : that same frame restricted to A.Hset -- line-for-line what
                125's main() does before computing rho_H.
    """
    r = A.bg_rows[bg_id]
    if hview:
        r = r[r.position.isin(A.Hset)]
    return r


def p_spec(ids, rho_threshold, rhos):
    """125's p_spec, transcribed (125 lines 394-397 / 515-520).

        k = #{b in N : rho_b <= rho_threshold}
        p = (1 + k) / (1 + |N|)

    ONE-SIDED, signed, <= .  This is the frozen primary form and is NOT
    re-parameterised anywhere in this session.  D7's |rho| sensitivity uses
    a DIFFERENT and explicitly-flipped inequality (>= on magnitudes) and is
    reported beside it, never instead of it.
    """
    k = int((rhos <= rho_threshold).sum())
    return k, (1 + k) / (1 + len(ids))


def background_bootstrap_corr(x, y, n_boot, rng, stat=np.nan):
    """BACKGROUND-LEVEL bootstrap of a correlation between per-background
    numbers.

    RESAMPLING UNIT: the background.  Given arrays x[i], y[i] with one
    entry per background, each draw resamples the BACKGROUND INDICES with
    replacement (n = len(x) draws) and recomputes the statistic on that
    resampled set.  Each background's already-computed values are held
    fixed within a draw -- no re-derivation of rho_b, no re-derivation of
    mean(|delta|).

    This is NOT Phase 2's position-cluster resampling unit and is not
    interchangeable with it: here the uncertainty being propagated is
    "which backgrounds were drawn", not "which positions within a
    background".  `stat` is a callable(x, y) -> float; default Spearman.
    Returns (draws, nan_count).
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    draws = np.empty(n_boot, float)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        draws[i] = stat(x[idx], y[idx])
    return draws, int(np.isnan(draws).sum())


def pct_ci(a):
    """95% percentile CI, 125's own helper (125 lines 202-208)."""
    a = np.asarray(a, float)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return float("nan"), float("nan"), 0
    lo, hi = np.percentile(a, [2.5, 97.5])
    return float(lo), float(hi), len(a)
