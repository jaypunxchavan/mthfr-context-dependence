"""scripts/lib/phase2_diag3.py -- shared helpers for the Phase 2 diagnostics III
session (tasks D13-D16 of
docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III.md).

WHY THIS MODULE EXISTS
----------------------
D13, D14, D15 and D16 all need the same two things: script 125's own
construction (via scripts/lib/phase2_diag.py, which is IMPORTED and never
modified), and a handful of OLS / partial-correlation helpers.  AGENTS section 2
says import from scripts/lib and do not reimplement, so those helpers live here
instead of being copied four times.

scripts/lib/phase2_diag.py IS NOT MODIFIED, and neither is any earlier script.
This is a NEW module.  Nothing in it re-derives script 125's rho_b, delta_b,
A222V rows, arms or null set: those are obtained by calling phase2_diag.build()
and phase2_diag.rho_table(), which drive script 125's own --mode phase2 path.

NO torch, NO esm, NO thermompnn, NO Biopython import anywhere in this file.

THE 3D LOADER
-------------
`parse_pdb_float64` is scripts/139_phase2_diag2_3d.py's transcription of script
126's "SOURCE 3 (EXACT)" block (scripts/126_i2_i3_interface_distances.py lines
322-344), reproduced here verbatim because D15 needs the same dependency-free
float64 fixed-column parse and script 126 cannot be imported: it executes
`from thermompnn.ssm_utils import load_pdb` at MODULE level (line 224) and that
package pulls in torch (verified by Diagnostics II: `import thermompnn.ssm_utils`
-> IMPORT OK, `'torch' in sys.modules` -> True).  The transcription is GATED in
D15 against the stored `ca_dist_222` column of
data/processed/task77_thermompnnD_doubles.csv, exactly as D11 gated it.

RESAMPLING UNITS -- the single source of truth for this session
--------------------------------------------------------------
  * Statistics that are ONE NUMBER PER BACKGROUND (rho_b vs mean|delta|,
    rho_b vs distance, partial correlations): BACKGROUND.  Each draw resamples
    which backgrounds were drawn; each background's already-computed values are
    held FIXED within a draw.  Used by D14's discontinuity CI and D15's
    gradient CI.  Never positions.
  * Statistics computed INSIDE ONE BACKGROUND (A222V's own rho on a row
    subset): POSITION CLUSTER, with an identity gate (every retained cluster
    once must reproduce the point estimate to 1e-12).  Used by D15.
  * D13, D14, D16: deterministic fits and exact rank counts; no resampling.
    D16 has no bootstrap at all.
Every calling script states its unit in its own docstring and in its own
printed output.  These units are NOT interchangeable with script 125's
position-within-background primary unit and are not used for it.
"""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from . import phase2_diag as pdg

ROOT = Path(__file__).resolve().parents[2]
PDB = ROOT / "data/raw/6FCX.pdb"
D3_CSV = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
D3_SHA = ("69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de")
RHO_TABLE = (ROOT / "data/processed/phase2_diagnostics/"
             "background_rho_table.csv")
RHO_TABLE_SHA = ("e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796")
T77 = ROOT / "data/processed/task77_thermompnnD_doubles.csv"

RES222 = 222
FROZEN_P_FULL = 0.05
FROZEN_P_H = 0.10
VIEWS = ("full", "H")


# --------------------------------------------------------------------------
# Presentation helpers (identical wording rules to every script in this repo)
# --------------------------------------------------------------------------
def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def verdict(p, view):
    """Adjusted p_spec vs the FROZEN NUMERIC thresholds.  Returns only
    'AT OR BELOW' or 'ABOVE'.  The three frozen outcome words are never
    produced here."""
    thr = FROZEN_P_FULL if view == "full" else FROZEN_P_H
    return ("AT OR BELOW" if p <= thr else "ABOVE"), thr


# --------------------------------------------------------------------------
# QUOTED SOURCE -- scripts/126_i2_i3_interface_distances.py lines 322-344, its
# "SOURCE 3 (EXACT)" block, transcribed LINE FOR LINE (same block, same
# precedent, as scripts/139_phase2_diag2_3d.py lines 230-256):
#
#     x3, res3, order3 = {"A": [], "B": []}, {"A": [], "B": []}, {"A": {}, "B": {}}
#     e3 = {"A": [], "B": []}
#     max_abs_coord = 0.0
#     with open(files["6FCX structure"], "rb") as fh:
#         for raw in fh:
#             line = raw.decode("utf-8", "ignore").rstrip()
#             if line[:4] != "ATOM":
#                 continue
#             ch = line[21:22]
#             if ch not in ("A", "B"):
#                 continue
#             rn = int(line[22:27])
#             at = line[12:16].strip()
#             el = line[76:78].strip().upper() or at[0]
#             if el == "H":                       # none in this file; stated
#                 continue
#             xyz = [float(line[i:i + 8]) for i in (30, 38, 46)]
#             max_abs_coord = max(max_abs_coord, *(abs(v) for v in xyz))
#             x3[ch].append(xyz)
#             res3[ch].append(rn)
#             e3[ch].append(el)
#             if at == "CA":
#                 order3[ch][rn] = xyz
# --------------------------------------------------------------------------
def parse_pdb_float64(path):
    """Returns (ca, atoms, max_abs_coord, elements, resnums).
    ca[chain][resnum] = np.array(xyz, float64);  atoms[chain] is a list of
    (resnum, element, xyz).  No torch, no esm, no Biopython, no thermompnn."""
    x3, res3, order3 = {"A": [], "B": []}, {"A": [], "B": []}, {"A": {}, "B": {}}
    e3 = {"A": [], "B": []}
    max_abs_coord = 0.0
    with open(path, "rb") as fh:
        for raw in fh:
            line = raw.decode("utf-8", "ignore").rstrip()
            if line[:4] != "ATOM":
                continue
            ch = line[21:22]
            if ch not in ("A", "B"):
                continue
            rn = int(line[22:27])
            at = line[12:16].strip()
            el = line[76:78].strip().upper() or at[0]
            if el == "H":                       # none in this file; stated
                continue
            xyz = [float(line[i:i + 8]) for i in (30, 38, 46)]
            max_abs_coord = max(max_abs_coord, *(abs(v) for v in xyz))
            x3[ch].append(xyz)
            res3[ch].append(rn)
            e3[ch].append(el)
            if at == "CA":
                order3[ch][rn] = xyz
    ca = {ch: {r: np.asarray(v, float) for r, v in order3[ch].items()}
          for ch in ("A", "B")}
    atoms = {"A": [], "B": []}
    for ch in ("A", "B"):
        for xyz, rn, el in zip(x3[ch], res3[ch], e3[ch]):
            atoms[ch].append((rn, el, np.asarray(xyz, float)))
    return ca, atoms, max_abs_coord, e3, res3


# --------------------------------------------------------------------------
# THE COMMON BUILD -- script 125's construction, imported, never re-derived
# --------------------------------------------------------------------------
def build(verbose=False):
    """One call, one shared state object, used by D13, D14, D15 and D16.

    Returns a dict with:
      A          script 125's Analysis (needed for row subsets in D15)
      bgs        sorted 96 background ids
      S_ids      the 18 Arm S ids (all at position 222)
      N_ids      the 78 null ids (Arms V and G)
      resN       the resolved subset of N_ids (67), from background_3d_distance
      ARM, POS, DIST   per-background arm / position / |position - 222|
      RHO        {"full": {b: rho}, "H": {b: rho}}
      RHO_A      {"full": rho_A222V, "H": rho_A222V_H}
      mad        {"full": {b: mean|delta|}, "H": {...}}
      mad_a      {"full": float, "H": float}
      df3        background_3d_distance.csv indexed by bg_id
      ca         chain-A / chain-B CA coordinates from parse_pdb_float64
    """
    s125, A = pdg.build(verbose=verbose)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")
    bgs = list(A.bgs)
    RHO = {"full": {b: float(A.point[b]) for b in bgs},
           "H": {b: float(point_h[b]) for b in bgs}}
    RHO_A = {"full": float(A.rho_a222v), "H": float(rho_a_H)}
    mad = {"full": {}, "H": {}}
    for b in bgs:
        for view in VIEWS:
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
    mad_a = {}
    for view in VIEWS:
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    df3 = pd.read_csv(D3_CSV).set_index("bg_id")
    N_ids = list(A.N_IDS)
    S_ids = list(A.S_IDS)
    resN = [b for b in N_ids if bool(df3.loc[b, "resolved"])]
    ca, atoms, max_abs, e3, res3 = parse_pdb_float64(PDB)
    return dict(
        s125=s125, A=A, bgs=bgs, N_ids=N_ids, S_ids=S_ids, resN=resN,
        ARM={b: table.loc[b, "arm"] for b in bgs},
        POS={b: int(table.loc[b, "position"]) for b in bgs},
        DIST={b: int(table.loc[b, "dist_222"]) for b in bgs},
        RHO=RHO, RHO_A=RHO_A, mad=mad, mad_a=mad_a, df3=df3, ca=ca,
        atoms=atoms, max_abs=max_abs)


def d3_of(pos, ca):
    """Chain-A CA-CA distance from residue `pos` to 222; NaN if unresolved.
    NEVER imputed."""
    a222 = ca["A"][RES222]
    if pos not in ca["A"]:
        return float("nan")
    return float(np.linalg.norm(ca["A"][pos] - a222))


# --------------------------------------------------------------------------
# OLS / partial-correlation helpers
# --------------------------------------------------------------------------
def ols_fit_predict(y, x, x_new):
    """OLS with intercept, the same np.linalg.lstsq design matrix script 134
    and script 137 use.  Returns (intercept, slope, prediction at x_new)."""
    X = np.column_stack([np.ones(len(x)), np.asarray(x, float)])
    beta, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return float(beta[0]), float(beta[1]), float(
        beta[0] + beta[1] * float(np.asarray(x_new, float)))


def fit_ols(y, cov):
    """OLS of y on [1, cov...] fitted on ALL rows given.  Returns beta."""
    cov = np.atleast_2d(np.asarray(cov, float))
    if cov.shape[0] != len(y) and cov.shape[1] == len(y):
        cov = cov.T
    X = np.column_stack([np.ones(len(y)), cov])
    beta, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return beta


def predict(beta, cov):
    cov = np.atleast_1d(np.asarray(cov, float))
    return float(beta[0] + float(np.dot(beta[1:], cov)))


def loo_shift(view, RHO, RHO_A, mad, mad_a, N_ids):
    """D9's PRIMARY: leave-one-out OLS rho ~ a + c*mean|delta| on N; A222V
    out-of-sample on the fit over all N.  Returns (r_b dict, r_A)."""
    r = {}
    for b in N_ids:
        sub = [x for x in N_ids if x != b]
        _, _, pred = ols_fit_predict(
            np.array([RHO[view][x] for x in sub], float),
            np.array([mad[view][x] for x in sub], float), mad[view][b])
        r[b] = RHO[view][b] - pred
    _, _, predA = ols_fit_predict(
        np.array([RHO[view][b] for b in N_ids], float),
        np.array([mad[view][b] for b in N_ids], float), mad_a[view])
    return r, RHO_A[view] - predA


def loo_joint(view, RHO, RHO_A, subs, covb, covA):
    """Leave-one-out on `subs` for the nulls; A222V out-of-sample on the fit
    over all of `subs`.  covb(b, view) -> covariates; covA(view) -> A222V's.
    Returns (r dict, r_A, beta_all)."""
    rhoN = np.array([RHO[view][b] for b in subs], float)
    cov = np.array([np.asarray(covb(b, view), float) for b in subs])
    Xb = np.column_stack([np.ones(len(subs)), cov])
    r = {}
    for i, b in enumerate(subs):
        keep = [j for j in range(len(subs)) if j != i]
        beta, *_ = np.linalg.lstsq(Xb[keep], rhoN[keep], rcond=None)
        r[b] = RHO[view][b] - (beta[0] + float(np.dot(
            beta[1:], np.asarray(covb(b, view), float))))
    beta, *_ = np.linalg.lstsq(Xb, rhoN, rcond=None)
    r_A = RHO_A[view] - predict(beta, covA(view))
    return r, r_A, beta


def all_fit(view, RHO, RHO_A, subs, covb, covA):
    """ONE fit on `subs`; residuals for every background IN `subs` are
    in-sample and for A222V out-of-sample.  Returns (r dict, r_A, beta)."""
    rhoN = np.array([RHO[view][b] for b in subs], float)
    cov = np.array([np.asarray(covb(b, view), float) for b in subs])
    beta = fit_ols(rhoN, cov)
    r = {b: RHO[view][b] - predict(beta, covb(b, view)) for b in subs}
    return r, RHO_A[view] - predict(beta, covA(view)), beta


def partial_formula(x, y, z):
    """Standard partial correlation from three pairwise Spearman coefficients.
    Returns (r_xy.z, r_xy, r_xz, r_yz).  x, y, z are aligned arrays."""
    rxy = float(spearmanr(x, y).statistic)
    rxz = float(spearmanr(x, z).statistic)
    ryz = float(spearmanr(y, z).statistic)
    den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    return (rxy - rxz * ryz) / den, rxy, rxz, ryz


def partial_rankresid(x, y, z):
    """Rank-transform x, y, z; OLS-residualise rank(x) and rank(y) on
    [1, rank(z)]; Pearson correlation of the two residual vectors.
    Independent of partial_formula by construction."""
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    A = np.column_stack([np.ones(len(rx)), rz])
    ex = rx - A @ np.linalg.lstsq(A, rx, rcond=None)[0]
    ey = ry - A @ np.linalg.lstsq(A, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def sp(x, y):
    return float(spearmanr(x, y).statistic)
