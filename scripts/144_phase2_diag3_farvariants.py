"""Script 144 -- Phase 2 diagnostics III, Task D15: FAR-VARIANT RESTRICTION.
DOES THE ANCHOR SURVIVE WITHOUT VARIANTS NEAR 222?  (the mechanism test)

HYPOTHESIS UNDER TEST (the task doc's, stated so that it can fail)
------------------------------------------------------------------
rho_b is hypothesised to track the overlap between the region a background
perturbs and the region where A222V's own epistasis is concentrated.  If that is
what drives rho_b, then dropping target variants NEAR 222 should collapse the
gradient of rho_b against distance-to-222 and should weaken or remove A222V's
own rho.  If the gradient and the anchor PERSIST among distal variants, the
statistic carries long-range information beyond spatial overlap.  **EITHER
OUTCOME IS INFORMATIVE AND IS REPORTED WITH EQUAL DIRECTNESS.**

THE CONFOUND THIS MUST CONTROL, AND WHY THE CONTROL IS NOT OPTIONAL
------------------------------------------------------------------
Removing rows shrinks every background's row count, which adds noise to every
rho_b and attenuates any cross-background correlation BY ITSELF.  A fall in the
gradient after removing rows near 222 is therefore UNINTERPRETABLE without a
matched control.  The matched-deletion control below is NOT OPTIONAL: for each
radius it deletes the SAME NUMBER OF WHOLE POSITIONS at random and recomputes
every statistic.  A fall that stays INSIDE the matched-deletion 95% range is
NOT attributable to the removed positions; one that falls OUTSIDE it is.

CONSTRUCTION, PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
-------------------------------------------------------------------
* Start from script 125's usable rows for each background and for A222V, via
  scripts/lib/phase2_diag.py (IMPORTED, never reimplemented).  A222V's rho is
  RE-DERIVED from its own cached delta_esm over the same usable rows, exactly
  as in D0/D9.  Views: full and H.
* DISTANCES.  Chain-A CA-CA distance from each frame position p to residue 222,
  d3_222(p), and from p to a background's position, d3_b(p), using script 139's
  structure conventions and loader -- `parse_pdb_float64` in
  scripts/lib/phase2_diag3.py, a LINE-FOR-LINE transcription of script 126's
  dependency-free float64 fixed-column parse (script 126 cannot be imported:
  it runs `from thermompnn.ssm_utils import load_pdb` at MODULE level and that
  pulls in torch).  Frame position p == PDB residue number p.
* ROWS AT UNRESOLVED POSITIONS ARE DROPPED FROM EVERY 3D VARIANT, INCLUDING
  R = 0, and their count is reported.  THEY ARE NEVER IMPUTED.  Chain A
  resolves 40..651 with internal gaps 161-171 and 392-396, so positions 2-39,
  161-171, 392-396 and 652-656 have no chain-A coordinates.
* All four radii R in {0, 10, 20, 30} A are REPORTED.  NONE IS SELECTED.  Both
  sequence sensitivities Rs in {25, 50} are reported.  R = 0 on resolved rows
  is the like-for-like baseline; the UNRESTRICTED all-rows value is also
  printed for reference, because D11.2's published figures are unrestricted.
  - **S1 (PRIMARY): far from 222.**  Keep rows with `d3_222(p) > R`.
  - **S2 (SENSITIVITY): far from both.**  Keep rows with `d3_222(p) > R` AND
    `d3_b(p) > R`.  Backgrounds at unresolved positions have no d3_b and drop
    out of S2; they are listed by name.  Arm S and A222V have
    d3_b = d3_222, so S2 = S1 for them.  *** S2 HAS NO MATCHED CONTROL, because
    the row sets differ per background, and is labelled DESCRIPTIVE. ***
  - **SEQUENCE SENSITIVITY:** keep rows with `|p - 222| > Rs`, S1 only, no
    unresolved-row issue.
* STATISTICS per (variant, R, view):
  1. Rows retained: min / median / max across backgrounds; positions retained.
  2. A222V's rho on the retained rows with a **POSITION-CLUSTER** bootstrap
     95% CI, 10,000 draws, SEED=0, clusters = retained TARGET POSITIONS, with
     an identity gate (every retained cluster once must reproduce the point
     estimate to 1e-12) and a statement of whether the CI excludes zero.
  3. `p_spec` on the restricted rho_b, FROZEN construction and direction
     (`rho_b <= rho_A222V`), with the at-or-below nulls named.  n is stated at
     every use.  **REPORTED ON BOTH DENOMINATORS for the 3D variants -- n = 78
     (every null background still has a computable rho on resolved rows, so S1
     keeps the full null set) and n = 67 (resolved nulls only, for
     comparability with the gradient).  NEITHER IS SELECTED.**  The task doc's
     parenthetical "N = 78 for S1 (S2 and 3D use the resolved nulls)" is
     ambiguous for the 3D variants; both denominators are printed so the
     ambiguity cannot bite a reader.
  4. The gradient: Spearman(rho_b, d3_b) across resolved NULLS (n = 67) and
     across all RESOLVED BACKGROUNDS (n = 85), with a background-level
     bootstrap CI, 10,000 draws, SEED=0, on the restricted rho_b.

THE MATCHED-DELETION CONTROL (S1 only, 3D variants only)
---------------------------------------------------------
For each R and view, k_R = the number of POSITIONS the S1 filter removes from
that view's RESOLVED UNIVERSE (for the H view the universe is the H positions).
N_DRAW = 200 (smoke at 20), SEED = 0.  Each draw removes k_R positions chosen
UNIFORMLY WITHOUT REPLACEMENT from the same universe -- WHOLE POSITIONS, all
their variants, matching the filter's cluster structure -- and the SAME removed
set is applied to EVERY background within a draw, so backgrounds are perturbed
identically.  It then recomputes A222V's rho, all 96 rho_b, the gradient
(n = 67) and p_spec (n = 78).  Reported for each statistic: the random-deletion
mean, the 2.5th / 97.5th percentiles, the S1 value, and the fraction of random
draws at or below and at or above the S1 value.

GATES -- BOTH HARD.  EITHER FAILING STOPS D15.
-----------------------------------------------------------------------------
D15-G1 (HARD):
  (a) the loader reproduces the stored `ca_dist_222` for the 9,595
      task77_thermompnnD_doubles.csv rows to max|diff| < 1e-6 A;
  (b) the monomer far (>10 A) fraction is 9,232/9,595 = 96.2168% and the
      dimer-aware far fraction is 9,128/9,595 = 95.1329%;
  (c) UNRESTRICTED baselines: all 96 rho_full and rho_H against
      background_rho_table.csv to 1e-9, and A222V's rho to 1e-9;
  (d) baseline targets on the unrestricted resolved-NULL subset (n = 67):
      gradient +0.731577372 (full) / +0.713319366 (H); A222V rho
      -0.088118064 / -0.090021683.
D15-G2 (HARD):
  (a) deleting ZERO positions through the deletion function reproduces the
      R = 0 restricted baseline EXACTLY (|diff| = 0);
  (b) applying the ACTUAL S1 removed set through the same deletion function
      reproduces the S1 statistic EXACTLY (|diff| = 0).

RESAMPLING UNITS -- STATED, AND NOT INTERCHANGEABLE
---------------------------------------------------
  * A222V's rho on a row subset (statistic 2): **POSITION CLUSTER**, i.e. whole
    retained TARGET POSITIONS resampled with replacement, 10,000 draws,
    SEED=0, identity gate at 1e-12.  Up to 19 substitutions share a residue
    position and are not independent; row-level resampling would overstate
    significance badly.
  * Anything ACROSS backgrounds (the gradient, statistic 4): **BACKGROUND**,
    10,000 draws, SEED=0, each background's already-computed rho_b held FIXED
    within a draw, nothing re-derived.
  * The matched-deletion control: NEITHER.  It is a deterministic recomputation
    on a deleted row set, repeated over N_DRAW random deletions; there is no
    resampling unit inside a draw.
  * p_spec and every row count: NO RESAMPLING.  Deterministic rank counts.

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result
computed here.  `p_spec` here is the frozen construction on restricted rows and
is compared to nothing; the frozen outcome thresholds are invoked only where
this task explicitly says so, and then only as "at or below" / "above".
Reporting rule for the far-filter comparisons: each statistic is flagged
"outside the matched-deletion 95% range" or "inside it".  No other wording.

LIMITS (AGENTS 6)
-----------------
* **A FALL IN THE GRADIENT THAT STAYS INSIDE THE MATCHED-DELETION RANGE IS NOT
  ATTRIBUTABLE TO THE REMOVED POSITIONS.  A FALL THAT FALLS OUTSIDE IT IS.**
  This is the only attribution statement this task licenses.
* S2 HAS NO MATCHED CONTROL (per-background row sets differ) and is DESCRIPTIVE.
* d3_CA is a CA-CA distance in ONE 2.50 A crystal structure of the DIMER.  A
  CA-CA distance is not a contact; side chains and alternate conformations are
  not modelled.
* Unresolved target positions and unresolved background positions are never
  imputed.  Both are named and counted.
* A222V's own rho on a restricted row set and the nulls' rho_b on their own
  restricted row sets are NOT computed on identical row sets (each background
  has its own usable rows), so p_spec under restriction is a comparison of
  differently-thinned statistics.  Disclosed, not corrected.
* mean|delta| and rho_b are both functions of the same delta_b; no shift
  covariate is used here at all.
* Nothing frozen is redefined.  No decision rule is changed.

Usage:
  N_DRAW=200 N_BOOT=10000 SEED=0 venv/bin/python3 scripts/144_phase2_diag3_farvariants.py
"""

import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

N_DRAW = int(os.environ.get("N_DRAW", "200"))
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))

RADII = (0.0, 10.0, 20.0, 30.0)
RS_SEQ = (25, 50)
IDENT_TOL = 1e-12
TOL_G1 = 1e-9
CUTOFF = 10.0
EXPECTED_ROWS = 9595
EXPECTED_MONO_FAR = 9232
EXPECTED_DIMER_FAR = 9128

TGT_GRAD = {"full": 0.731577372, "H": 0.713319366}
TGT_RHO_A = {"full": -0.088118064, "H": -0.090021683}

t0 = time.time()
gates = []


def banner(t, ch="="):
    p3.banner(t, ch)


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def gfail(msg):
    print(f"\n*** D15 GATE FAIL: {msg} -- STOP D15. ***")
    sys.exit(1)


def rho_of(x, y):
    if len(x) < 3:
        return float("nan")
    return float(spearmanr(x, y).statistic)


# ---------------------------------------------------------------- row store -
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


def main():
    banner("D15 -- FAR-VARIANT RESTRICTION: DOES THE ANCHOR SURVIVE WITHOUT "
           "VARIANTS NEAR 222?  (script 144)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word "
          "is used as a label.")
    print("NO MODEL SCORING.  NO torch / esm / thermompnn / Biopython import "
          "anywhere in this file.")
    print(f"  N_DRAW={N_DRAW} N_BOOT={N_BOOT} SEED={SEED}")
    print("RESAMPLING UNITS (not interchangeable):")
    print("  * A222V's rho on a row subset  -> POSITION CLUSTER (whole retained "
          "target positions), identity gate 1e-12.")
    print("  * anything ACROSS backgrounds   -> BACKGROUND, per-background rho_b "
          "held FIXED.")
    print("  * the matched-deletion control  -> NO resampling inside a draw; it "
          "is a recomputation on a deleted row set.")
    print("  * p_spec and every row count    -> NO resampling.")

    # ================================================================ GATES ==
    banner("GATE D15-G1 (HARD) -- loader, far fractions, unrestricted "
           "baselines, baseline targets", "-")
    st = p3.build()
    bgs, S_ids, N_ids, resN = st["bgs"], st["S_ids"], st["N_ids"], st["resN"]
    RHO, RHO_A, df3, ca = (st["RHO"], st["RHO_A"], st["df3"], st["ca"])
    ARM, POS, DIST = st["ARM"], st["POS"], st["DIST"]
    res96 = [b for b in bgs if bool(df3.loc[b, "resolved"])]

    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    gate("D15-G1 rho table sha256", sha1 == p3.RHO_TABLE_SHA, sha1)
    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    gate("D15-G1 3D table sha256", sha3 == p3.D3_SHA, sha3)

    # ---- (a) numbering mapping against the stored ca_dist_222 -------------
    t77 = pd.read_csv(p3.T77)
    fr = t77[t77["own_e_b"].notna()].copy()
    a222, b222 = ca["A"][p3.RES222], ca["B"][p3.RES222]
    pos77 = fr["position"].to_numpy(int)
    stored = fr["ca_dist_222"].to_numpy(float)
    dAA = np.array([float(np.linalg.norm(ca["A"][p] - a222)) for p in pos77])
    map_dev = float(np.max(np.abs(dAA - stored)))
    gate("D15-G1a loader vs stored ca_dist_222", map_dev < TOL_G1,
         f"max|diff| = {map_dev:.3e} A over {len(fr)} rows (gate < {TOL_G1:g}); "
         f"unresolved positions in this frame = "
         f"{len([p for p in pos77 if p not in ca['A']])}")
    if len(fr) != EXPECTED_ROWS:
        gfail(f"frozen frame {len(fr)} != {EXPECTED_ROWS}")

    # ---- (b) script 107's far-from-222 fractions ---------------------------
    dAB = np.array([float(np.linalg.norm(ca["A"][p] - b222)) for p in pos77])
    hasB = np.array([p in ca["B"] for p in pos77])
    dBA = np.where(hasB, [float(np.linalg.norm(ca["B"][p] - a222))
                          if p in ca["B"] else np.nan for p in pos77], np.nan)
    dBB = np.where(hasB, [float(np.linalg.norm(ca["B"][p] - b222))
                          if p in ca["B"] else np.nan for p in pos77], np.nan)
    dmin4 = np.nanmin(np.vstack([dAA, dAB, dBA, dBB]), axis=0)
    nA, nD = int((dAA > CUTOFF).sum()), int((dmin4 > CUTOFF).sum())
    gate("D15-G1b monomer far (>10 A)",
         nA == EXPECTED_MONO_FAR and
         round(100.0 * nA / len(fr), 2) == 96.22,
         f"{nA}/{len(fr)} = {100.0 * nA / len(fr):.4f}% (script 107/126: "
         f"{EXPECTED_MONO_FAR} = 96.22%)")
    gate("D15-G1b dimer-aware far (>10 A)",
         nD == EXPECTED_DIMER_FAR and
         round(100.0 * nD / len(fr), 2) == 95.13,
         f"{nD}/{len(fr)} = {100.0 * nD / len(fr):.4f}% (script 107/126: "
         f"{EXPECTED_DIMER_FAR} = 95.13%)")

    # ---- (c) unrestricted baselines vs the D1 table ------------------------
    d1 = pd.read_csv(p3.RHO_TABLE).set_index("bg_id")
    A = st["A"]
    store = {}
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
        store[view] = dict(POSV=POSV, A=sa, B=sb, Hset=A.Hset, view=view)
        print(f"  [{view}] frame positions in view = {len(POSV)}, "
              f"A222V rows = {len(sa.pos)}, "
              f"per-background rows min = "
              f"{min(len(s.delta) for s in sb.values())}, median = "
              f"{int(np.median([len(s.delta) for s in sb.values()]))}, "
              f"max = {max(len(s.delta) for s in sb.values())}")
    # D1 table vs the INDEPENDENT re-derivation through script 125's own rows
    dmax_rho, dmax_a, n_cmp = 0.0, 0.0, 0
    for view in p3.VIEWS:
        col = "rho_H" if view == "H" else "rho_full"
        for b in bgs:
            v = store[view]["B"][b].rho(np.ones(len(store[view]["POSV"]), bool))
            dmax_rho = max(dmax_rho, abs(v - float(d1.loc[b, col])))
            dmax_rho = max(dmax_rho, abs(RHO[view][b] - float(d1.loc[b, col])))
            n_cmp += 1
        v = store[view]["A"].rho(np.ones(len(store[view]["POSV"]), bool))
        dmax_a = max(dmax_a, abs(v - RHO_A[view]))
    gate("D15-G1c all 96 rho_full and rho_H vs background_rho_table.csv",
         dmax_rho < TOL_G1,
         f"{n_cmp} comparisons (re-derived AND script-125 value, against the "
         f"D1 table); max|diff| = {dmax_rho:.3e} (gate < {TOL_G1:g})")
    gate("D15-G1c A222V rho (full and H)", dmax_a < TOL_G1,
         f"max|diff| = {dmax_a:.3e} (gate < {TOL_G1:g}); values "
         f"{RHO_A['full']:+.9f} / {RHO_A['H']:+.9f}")

    # ---- (d) baseline targets on the unrestricted resolved-NULL subset -----
    for view in p3.VIEWS:
        x = np.array([RHO[view][b] for b in resN], float)
        g = np.array([float(df3.loc[b, "d3_CA"]) for b in resN], float)
        v = float(spearmanr(x, g).statistic)
        gate(f"D15-G1d unrestricted gradient on resolved N (n={len(resN)}) "
             f"({view})", abs(v - TGT_GRAD[view]) < TOL_G1,
             f"got {v:+.9f} vs {TGT_GRAD[view]:+.9f} "
             f"|diff|={abs(v - TGT_GRAD[view]):.3e}")
        gate(f"D15-G1d A222V rho unrestricted ({view})",
             abs(RHO_A[view] - TGT_RHO_A[view]) < TOL_G1,
             f"got {RHO_A[view]:+.9f} vs {TGT_RHO_A[view]:+.9f} "
             f"|diff|={abs(RHO_A[view] - TGT_RHO_A[view]):.3e}")

    n_fail = sum(1 for _, ok, _ in gates if not ok)
    print(f"\n  {len(gates) - n_fail}/{len(gates)} D15-G1 checks PASS, "
          f"{n_fail} FAIL")
    if n_fail:
        gfail(f"{n_fail} of {len(gates)} D15-G1 checks failed")
    print("  GATE PASS: D15-G1 satisfied.  The far-filter analysis may run.")

    # ================================================= geometry bookkeeping =
    banner("GEOMETRY BOOKKEEPING -- what each R removes, and what is dropped "
           "for being unresolved", "-")
    frame_pos = sorted(A.frame.position.unique())
    print(f"  frame positions = {len(frame_pos)};  position 222 itself "
          f"{'IS' if 222 in frame_pos else 'IS NOT'} a frame target position")
    print(f"  chain A resolves {min(ca['A'])}..{max(ca['A'])} with internal "
          f"gaps 161-171 and 392-396, so positions 2-39, 161-171, 392-396 and "
          f"652-656 have NO chain-A coordinates")
    geo = {}
    for view in p3.VIEWS:
        POSV = store[view]["POSV"]
        resolved = np.array([p in ca["A"] for p in POSV])
        d3 = np.array([p3.d3_of(int(p), ca) for p in POSV])
        # univ = INDICES into POSV of the resolved positions (so it can index
        # d3); univ_pos = the same positions as VALUES (for the deletion
        # draws and for printing).
        univ = np.flatnonzero(resolved)
        geo[view] = dict(resolved=resolved, d3=d3, univ=univ,
                         univ_pos=POSV[univ])
        nres = int((~resolved).sum())
        rows_unres = int((~resolved)[store[view]["A"].code].sum())
        print(f"\n  [{view}] positions in view = {len(POSV)};  resolved = "
              f"{int(resolved.sum())};  UNRESOLVED = {nres} "
              f"({', '.join(str(int(p)) for p in POSV[~resolved])})")
        print(f"  [{view}] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM EVERY "
              f"3D VARIANT INCLUDING R = 0, NEVER IMPUTED: A222V "
              f"{rows_unres} of {len(store[view]['A'].pos)} rows; per "
              f"background min = "
              f"{min(int((~resolved)[s.code].sum()) for s in store[view]['B'].values())}, "
              f"max = "
              f"{max(int((~resolved)[s.code].sum()) for s in store[view]['B'].values())}")
        u = geo[view]["d3"][geo[view]["univ"]]
        print(f"  [{view}] d3_222(p) over the {len(u)} RESOLVED view "
              f"positions, percentiles:")
        qs = [0, 1, 5, 10, 25, 50, 75, 90, 100]
        print(f"           " + "  ".join(f"p{q}={np.percentile(u, q):.3f}"
                                         for q in qs) + "   (A)")
        print(f"  [{view}] frame positions within each R of 222 (resolved "
              f"only), i.e. what the S1 filter removes:")
        for R in RADII:
            k = int((u <= R).sum())
            lo = u[u > R].min() if (u > R).any() else float("nan")
            print(f"           R = {R:>4.0f} A: k_R = {k:>3d} positions "
                  f"removed, {len(u) - k:>3d} retained  "
                  f"(min d3_222 among retained = {lo:.3f} A)")
    print("\n  *** THE PERMUTATION/BOOTSTRAP NOTE (AGENTS 3): every bootstrap "
          "in this script is at the unit stated above; no row-level resampling "
          "is performed anywhere, because up to 19 substitutions share one "
          "residue position. ***")

    # ================================================ the deletion machinery
    banner("THE DELETION FUNCTION (used by every variant and by the matched-"
           "deletion control)", "-")

    def keep_from_removed(POSV, resolved, removed):
        """Whole positions in `removed` are deleted; everything else that is
        resolved is kept.  THE SAME FUNCTION is used by the S1 filter, by the
        R = 0 baseline and by the matched-deletion control, which is what makes
        gate D15-G2 possible."""
        rm = np.isin(POSV, np.asarray(sorted(removed), dtype=POSV.dtype))
        return resolved & (~rm)

    def stats(view, keep):
        """All statistics for one (variant, view, row set)."""
        POSV = store[view]["POSV"]
        sa = store[view]["A"]
        rho_a = sa.rho(keep)
        rho_b = {b: store[view]["B"][b].rho(keep) for b in bgs}
        rows = np.array([store[view]["B"][b].n_rows(keep) for b in bgs])
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

    # ==================================================== position-cluster CI
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

    def pos_cluster_boot(view, keep, n_boot, rng):
        """POSITION-CLUSTER bootstrap: whole retained target positions are
        resampled with replacement; all their rows come with them."""
        sa = store[view]["A"]
        rows_sorted, sizes, base, npos = cluster_index(
            store[view]["POSV"], sa.code, keep)
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

    def identity_gate(view, keep):
        """Every retained cluster ONCE must reproduce the point estimate."""
        sa = store[view]["A"]
        rows_sorted, sizes, base, npos = cluster_index(
            store[view]["POSV"], sa.code, keep)
        idx = rows_sorted                      # already one row per cluster once
        v = rho_of(sa.delta[idx], sa.y[idx])
        return abs(v - sa.rho(keep)), v

    def grad_boot(rho_b, ids, n_boot, rng):
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

    # ================================================= the variants themselves
    banner("THE VARIANTS -- all four radii, both sequence sensitivities, "
           "S1 and S2, both views", "-")
    rng = np.random.default_rng(SEED)
    results = {}
    ident_max = 0.0

    def run(tag, view, keep, do_boot=True):
        nonlocal ident_max
        s = stats(view, keep)
        idd, idv = identity_gate(view, keep)
        ident_max = max(ident_max, idd)
        if idd >= IDENT_TOL:
            gfail(f"{tag}/{view} position-cluster identity gate: "
                  f"|diff| = {idd:.3e}")
        s["ident"] = idd
        s["ident_v"] = idv
        rowsA = s["n_rows_a"]
        print(f"\n  --- {tag}  [{view}] ---")
        print(f"    rows retained: A222V = {rowsA};  across the 96 backgrounds "
              f"min = {s['rows'].min()}, median = "
              f"{int(np.median(s['rows']))}, max = {s['rows'].max()};  "
              f"positions retained = {s['n_pos']}")
        print(f"    A222V rho on the retained rows = {s['rho_a']:+.9f}")
        if do_boot:
            draws = pos_cluster_boot(view, keep, N_BOOT, rng)
            lo, hi, v = p3.pdg.pct_ci(draws)
            s["a_lo"], s["a_hi"], s["a_v"] = lo, hi, v
            s["a_excl0"] = bool(lo > 0 or hi < 0)
            print(f"      POSITION-CLUSTER bootstrap 95% CI = [{lo:+.6f}, "
                  f"{hi:+.6f}] ({v} usable draws, clusters = {s['n_pos']} "
                  f"retained target positions, {N_BOOT} draws, SEED={SEED})  "
                  f"{'EXCLUDES ZERO' if s['a_excl0'] else 'INCLUDES ZERO'}")
            print(f"      identity gate (every cluster once vs point): "
                  f"|diff| = {idd:.3e} (gate < {IDENT_TOL:g})  PASS")
            for lbl, ids in (("n67", resN), ("n85", res96)):
                glo, ghi, gv, nan_n = grad_boot(s["rho_b"], ids, N_BOOT, rng)
                s[f"glo_{lbl}"], s[f"ghi_{lbl}"] = glo, ghi
                print(f"      gradient Spearman(rho_b, d3_b) on "
                      f"{'resolved NULLS' if lbl == 'n67' else 'all RESOLVED backgrounds'} "
                      f"n = {len(ids)}: {s['grad_' + lbl]:+.9f}  "
                      f"BACKGROUND-level bootstrap 95% CI = "
                      f"[{glo:+.6f}, {ghi:+.6f}] ({gv} usable, {nan_n} nan, "
                  f"{N_BOOT} draws, SEED={SEED})  "
                  f"{'EXCLUDES ZERO' if (glo > 0 or ghi < 0) else 'INCLUDES ZERO'}")
        for lbl in ("n78", "n67"):
            print(f"      p_spec ({lbl} nulls, frozen direction rho_b <= "
                  f"rho_A222V): k = {s['k_' + lbl]} of "
                  f"{len(N_ids) if lbl == 'n78' else len(resN)}, "
                  f"p_spec = {s['p_' + lbl]:.6f}   at or below: "
                  f"{', '.join(s['aob_' + lbl]) if s['aob_' + lbl] else 'NONE'}")
        results[(tag, view)] = s
        return s

    for view in p3.VIEWS:
        POSV, resolved, d3 = (store[view]["POSV"], geo[view]["resolved"],
                              geo[view]["d3"])
        # UNRESTRICTED reference (no 3D filter at all -- D11.2's setting)
        keep_all = np.ones(len(POSV), bool)
        run("UNRESTRICTED (no 3D filter; D11.2's setting)", view, keep_all)
        # R = 0 resolved
        run("R = 0 A, resolved rows only (3D like-for-like baseline)", view,
            keep_from_removed(POSV, resolved, []))
        for R in RADII:
            rm = POSV[resolved & (d3 <= R)]
            run(f"S1  3D  R = {R:.0f} A  (keep d3_222(p) > {R:.0f})", view,
                keep_from_removed(POSV, resolved, rm))
        for Rs in RS_SEQ:
            rm = POSV[np.abs(POSV - 222) <= Rs]
            run(f"S1  SEQ Rs = {Rs}  (keep |p - 222| > {Rs})", view,
                resolved & ~np.isin(POSV, rm))

    # ---- S2, which has a per-background row set ----------------------------
    print("\n  *** S2 (far from BOTH) HAS A DIFFERENT ROW SET PER BACKGROUND, "
          "SO IT IS HANDLED WITH ITS OWN CODE PATH BELOW AND HAS NO MATCHED "
          "CONTROL. ***")
    banner("S2 -- FAR FROM BOTH 222 AND THE BACKGROUND (SENSITIVITY; "
           "DESCRIPTIVE; NO MATCHED CONTROL)", "-")
    s2_dropped = []
    for view in p3.VIEWS:
        POSV = store[view]["POSV"]
        resolved = geo[view]["resolved"]
        d3 = geo[view]["d3"]
        for R in RADII:
            per = {}
            bad = [b for b in bgs if POS[b] not in ca["A"]]
            db_cache = {}
            for b in bgs:
                if b in bad:
                    continue
                if b not in db_cache:
                    db_cache[b] = np.array(
                        [p3.d3_of(int(p), ca) if ok else np.nan
                         for p, ok in zip(POSV, resolved)])
                per[b] = resolved & (d3 > R) & (db_cache[b] > R)
            for b in bad:
                per[b] = np.zeros(len(POSV), bool)
            rho_b = {}
            rows = []
            for b in bgs:
                if b in bad:
                    rho_b[b] = float("nan")
                    rows.append(0)
                else:
                    rho_b[b] = store[view]["B"][b].rho(per[b])
                    rows.append(store[view]["B"][b].n_rows(per[b]))
            # A222V has d3_b = d3_222, so its own filter is S1's
            keepA = keep_from_removed(POSV, resolved, POSV[resolved & (d3 <= R)])
            rho_a = store[view]["A"].rho(keepA)
            rows = np.array(rows)
            ids78 = [b for b in N_ids if b not in bad]
            ids67 = [b for b in resN if b not in bad]
            res85 = [b for b in res96 if b not in bad]
            k78 = int(sum(1 for b in ids78 if rho_b[b] <= rho_a))
            k67 = int(sum(1 for b in ids67 if rho_b[b] <= rho_a))
            g67 = float(spearmanr(np.array([rho_b[b] for b in ids67], float),
                                  np.array([float(df3.loc[b, "d3_CA"])
                                            for b in ids67], float)).statistic)
            g85 = float(spearmanr(np.array([rho_b[b] for b in res85], float),
                                  np.array([float(df3.loc[b, "d3_CA"])
                                            for b in res85], float)).statistic)
            s2_dropped.append((view, R, sorted(bad)))
            print(f"\n  --- S2  3D  R = {R:.0f} A  [{view}]  "
                  f"(DESCRIPTIVE, no matched control) ---")
            print(f"    backgrounds with NO d3_b (unresolved position) and so "
                  f"dropped: {len(bad)} -> {sorted(bad)}"
                  if bad else "    no background dropped")
            print(f"    rows retained per background: min = {rows.min()}, "
                  f"median = {int(np.median(rows))}, max = {rows.max()}")
            print(f"    A222V rho on its own S1 filter = {rho_a:+.9f}   "
                  f"(d3_b = d3_222 for A222V, so S2 = S1 for it)")
            print(f"    p_spec (n = {len(ids78)} usable nulls): k = {k78}, "
                  f"p_spec = {(1 + k78) / (1 + len(ids78)):.6f}   at or "
                  f"below: "
                  f"{', '.join(sorted(b for b in ids78 if rho_b[b] <= rho_a)) or 'NONE'}")
            print(f"    p_spec (n = {len(ids67)} resolved usable nulls): "
                  f"k = {k67}, p_spec = {(1 + k67) / (1 + len(ids67)):.6f}")
            print(f"    gradient on {len(ids67)} resolved usable nulls: "
                  f"{g67:+.9f}   on {len(res85)} resolved usable backgrounds: "
                  f"{g85:+.9f}   *** NO CI AND NO MATCHED CONTROL: S2 IS "
                  f"DESCRIPTIVE ***")
            results[(f"S2 3D R = {R:.0f} A", view)] = dict(
                rho_a=rho_a, rho_b=rho_b, rows=rows, k_n78=k78,
                p_n78=(1 + k78) / (1 + len(ids78)), k_n67=k67,
                p_n67=(1 + k67) / (1 + len(ids67)), grad_n67=g67,
                grad_n85=g85, n78=len(ids78), n67=len(ids67), n85=len(res85),
                dropped=sorted(bad))
    if not any(b for _, _, b in s2_dropped):
        print("  (S2 dropped no background in any view -- see per-line lists "
              "above; the lists are printed even when empty.)")

    # ================================================================ GATE G2
    banner("GATE D15-G2 (HARD) -- the deletion function is exact", "-")
    g2max = 0.0
    for view in p3.VIEWS:
        POSV, resolved, d3 = (store[view]["POSV"], geo[view]["resolved"],
                              geo[view]["d3"])
        base = results[("R = 0 A, resolved rows only (3D like-for-like "
                        "baseline)", view)]
        s = stats(view, keep_from_removed(POSV, resolved, []))
        for key in ("rho_a", "grad_n67", "grad_n85", "k_n78", "k_n67"):
            d = abs(float(s[key]) - float(base[key]))
            g2max = max(g2max, d)
        gate(f"D15-G2a zero-deletion == R=0 baseline ({view})", g2max == 0.0,
             f"max|diff| over rho_A222V, both gradients and both k's = "
             f"{g2max:.3e} (required EXACTLY 0)")
        for R in RADII:
            rm = POSV[resolved & (d3 <= R)]
            tag = f"S1  3D  R = {R:.0f} A  (keep d3_222(p) > {R:.0f})"
            if (tag, view) not in results:
                continue
            s1 = results[(tag, view)]
            s = stats(view, keep_from_removed(POSV, resolved, rm))
            dmax = 0.0
            for key in ("rho_a", "grad_n67", "grad_n85", "k_n78", "k_n67"):
                dmax = max(dmax, abs(float(s[key]) - float(s1[key])))
            dmax = max(dmax, float(np.max(np.abs(
                np.array([s["rho_b"][b] for b in bgs], float)
                - np.array([s1["rho_b"][b] for b in bgs], float)))))
            gate(f"D15-G2b actual S1 removed set reproduces S1 ({view}, "
                 f"R = {R:.0f})", dmax == 0.0,
                 f"{len(rm)} positions removed; max|diff| over all 97 rho and "
                 f"every reported statistic = {dmax:.3e} (required EXACTLY 0)")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    if n_fail:
        gfail(f"{n_fail} of {len(gates)} gate checks failed")

    # ================================================ matched-deletion control
    banner("THE MATCHED-DELETION CONTROL (S1 only) -- NOT OPTIONAL", "-")
    print("  For each R and view: k_R = the number of POSITIONS the S1 filter "
          f"removes from that view's resolved universe.")
    print(f"  N_DRAW = {N_DRAW} random deletions, SEED = {SEED}.  Each draw "
          "removes k_R positions chosen UNIFORMLY WITHOUT REPLACEMENT from the "
          "same universe -- WHOLE POSITIONS, all their variants -- and the SAME "
          "removed set is applied to EVERY background within a draw.")
    print("  REPORTING RULE: an S1 statistic is flagged OUTSIDE the "
          "matched-deletion 95% range or INSIDE it.  A fall in the gradient "
          "that stays INSIDE the range is NOT attributable to the removed "
          "positions; one that falls OUTSIDE it is.")
    print("  RESAMPLING UNIT: none inside a draw -- each draw is a "
          "deterministic recomputation on a deleted row set.  The spread over "
          "draws is the deletion effect, not a bootstrap CI.")
    md = {}
    for view in p3.VIEWS:
        POSV, resolved, d3 = (store[view]["POSV"], geo[view]["resolved"],
                              geo[view]["d3"])
        univ = geo[view]["univ_pos"]
        for R in RADII:
            rm = sorted(POSV[resolved & (d3 <= R)].tolist())
            k_R = len(rm)
            tag = f"S1  3D  R = {R:.0f} A  (keep d3_222(p) > {R:.0f})"
            s1 = results[(tag, view)]
            acc = {kk: np.empty(N_DRAW, float)
                   for kk in ("rho_a", "grad_n67", "grad_n85", "p_n78",
                              "p_n67", "k_n78")}
            rg = np.random.default_rng(SEED)
            for i in range(N_DRAW):
                drop = rg.choice(univ, size=k_R, replace=False) if k_R else \
                    np.array([], dtype=univ.dtype)
                s = stats(view, keep_from_removed(POSV, resolved, drop))
                for kk in acc:
                    acc[kk][i] = float(s[kk])
            md[(view, R)] = acc
            print(f"\n  === {view}, R = {R:.0f} A: k_R = {k_R} positions "
                  f"removed from a universe of {len(univ)} "
                  f"(matched-deletion draws: {N_DRAW}) ===")
            for kk, lbl in (("rho_a", "A222V rho"),
                            ("grad_n67", "gradient Spearman(rho_b,d3_b), "
                                         "resolved nulls n=67"),
                            ("grad_n85", "gradient Spearman(rho_b,d3_b), "
                                         "resolved backgrounds n=85"),
                            ("k_n78", "k at or below, 78 nulls"),
                            ("p_n78", "p_spec, 78 nulls"),
                            ("p_n67", "p_spec, 67 resolved nulls")):
                a = acc[kk]
                lo, hi = np.percentile(a, [2.5, 97.5])
                v = float(s1[kk])
                inside = (lo <= v <= hi)
                fb = float((a <= v).mean())
                fa = float((a >= v).mean())
                print(f"    {lbl}")
                print(f"      S1 value                      = {v:+.9f}")
                print(f"      random-deletion mean          = {a.mean():+.9f}"
                      f"   sd = {a.std(ddof=1) if N_DRAW > 1 else 0.0:.9f}")
                print(f"      random-deletion 2.5 / 97.5 pct = [{lo:+.9f}, "
                      f"{hi:+.9f}]")
                print(f"      fraction of draws at or below S1 = {fb:.4f};  "
                      f"at or above = {fa:.4f}")
                print(f"      -> S1 value is "
                      f"{'INSIDE' if inside else 'OUTSIDE'} the "
                      f"matched-deletion 95% range")
            print(f"    rows retained under S1: A222V "
                  f"{s1['n_rows_a']}; per background min {s1['rows'].min()}, "
                  f"median {int(np.median(s1['rows']))}, max "
                  f"{s1['rows'].max()}")
    print("\n  *** READING THE CONTROL: an S1 gradient that has FALLEN but is "
          "still INSIDE the matched-deletion range is NOT attributable to the "
          "removed near-222 positions -- deleting the same NUMBER of random "
          "positions does the same or more.  An S1 gradient OUTSIDE the range "
          "IS attributable to them. ***")

    # ================================================== the summary table ==
    banner("D15 FAR-VARIANT RESTRICTION TABLE -- S1, both views, all four "
           "radii", "-")
    print(f"  {'view':>5s} {'R (A)':>7s} {'k_R pos':>9s} {'A222V rho':>12s} "
          f"{'pos-cluster 95% CI':>26s} {'excl 0':>7s} {'gradient n=67':>22s} "
          f"{'its 95% CI':>26s} {'p_spec n=78':>13s} {'at or below':>22s}")
    for view in p3.VIEWS:
        for R in RADII:
            tag = f"S1  3D  R = {R:.0f} A  (keep d3_222(p) > {R:.0f})"
            s = results[(tag, view)]
            POSV = store[view]["POSV"]
            k_R = int((geo[view]["resolved"] &
                       (geo[view]["d3"] <= R)).sum())
            acc = md[(view, R)]
            glo, ghi = np.percentile(acc["grad_n67"], [2.5, 97.5])
            inside = bool(glo <= s["grad_n67"] <= ghi)
            print(f"  {view:>5s} {R:>7.0f} {k_R:>9d} {s['rho_a']:>+12.9f} "
                  f"[{s['a_lo']:+.6f}, {s['a_hi']:+.6f}]".ljust(0) +
                  f" {str(s['a_excl0']):>7s} {s['grad_n67']:>+14.9f}  "
                  f"[{s['glo_n67']:+.6f}, {s['ghi_n67']:+.6f}] "
                  f"{s['p_n78']:>13.6f} "
                  f"{(', '.join(s['aob_n78']) if s['aob_n78'] else 'NONE'):>22s}")
            print(f"        matched-deletion range for the gradient "
                  f"(n={len(acc['grad_n67'])} draws): "
                  f"[{glo:+.9f}, {ghi:+.9f}]   -> S1 gradient is "
                  f"{'INSIDE' if inside else 'OUTSIDE'} it;  "
                  f"frac draws at or below S1 = "
                  f"{float((acc['grad_n67'] <= s['grad_n67']).mean()):.4f}, "
                  f"at or above = "
                  f"{float((acc['grad_n67'] >= s['grad_n67']).mean()):.4f}")
    print("\n  (gradients quoted here are on the RESOLVED NULLS, n = 67, the "
          "D11.2 denominator.  The n = 85 all-resolved-background gradient and "
          "the n = 67 p_spec are printed in the per-variant blocks above.)")

    banner("D15 GATE TABLE (for the SUMMARY)", "-")
    for gid, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    print(f"\n  D15-G1: {'PASS' if not n_fail else 'FAIL'} "
          f"({len(gates) - n_fail}/{len(gates)} checks incl. D15-G2).")
    print(f"  max position-cluster identity |diff| across every variant and "
          f"view = {ident_max:.3e} (gate < {IDENT_TOL:g})")

    print("\nD15 LIMITATIONS (printed, not only in the docstring):  THE ONLY "
          "ATTRIBUTION THIS TASK LICENSES IS: a fall in the gradient that "
          "stays INSIDE the matched-deletion 95% range is NOT attributable to "
          "the removed near-222 positions; one that falls OUTSIDE it IS.  S2 "
          "HAS NO MATCHED CONTROL (per-background row sets differ) and is "
          "DESCRIPTIVE.  d3_CA is a CA-CA distance in ONE 2.50 A crystal "
          "structure of the dimer and a CA-CA distance is not a contact.  "
          "UNRESOLVED TARGET POSITIONS ARE DROPPED FROM EVERY 3D VARIANT "
          "INCLUDING R = 0 AND NEVER IMPUTED; the dropped ROW count is printed "
          "at the top of this output.  A222V's rho and each null's rho_b "
          "under restriction are computed on DIFFERENTLY THINNED row sets, so "
          "p_spec under restriction compares statistics that are not computed "
          "on identical rows.  Resampling units: POSITION CLUSTER for A222V's "
          "own rho on a row subset (identity gate 1e-12, printed above), "
          "BACKGROUND for anything across backgrounds, and NONE inside a "
          "matched-deletion draw.  NOTHING FROZEN IS REDEFINED.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
