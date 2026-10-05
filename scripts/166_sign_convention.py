#!/usr/bin/env python3
"""Script 166 (Phase 4 session 4a, task A3) -- Module S: the sign convention.

PRE-REGISTERED: this docstring was written before the first run of the
script.  It implements task A3 of
``docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md`` (read-only;
that file is a protected path and is never written by this script).

No bootstrap, no permutation, no model, no network, no resampling: this is
an audit of what the words mean, so there is nothing to smoke-test and
nothing to run twice -- N_BOOT is deliberately NOT read.  Every check below
runs once, in order.  On the first mismatch the script prints the failure
with the target beside the computed value, prints the summary, and exits 1.
It never relaxes, re-frames or re-selects an expectation after seeing a
result (AGENTS 0).  The targets in this file are Claude's recomputations
recorded in the planning document, not facts; they are re-derived here
independently and printed beside the target.

CHECKS, IN ORDER:

S-1  Quote, with file and line numbers, (a) how own_e.b is built
     (``rebuild_interaction_fit``; ``wls_line`` and ``fit_interaction``:
     the residual ``m_score - expected`` and its weighted intercept),
     (b) how delta is defined (``esm2_score_a222v_bg - esm2_score``) and
     (c) which tail ``PHASE2_PREREG.md`` pre-stated.  Each check prints the
     line of code found at the cited line number AND the expectation from
     the planning document, side by side, then asserts the quoted tokens
     are on that line.  The planning document supplies no line numbers; the
     numbers below are this script's and are verified at run time, so a
     line that moves FAILS instead of being quoted wrongly.
S-2  Worked example, computed not typed: inside the analysis set (finite
     delta, own_e_b, S_W, base functionality) restricted to variants with
     ``se_e_b`` below its median, print the 3 most positive and the 3 most
     negative own_e.b with every field the task lists -- position, wild
     type, mutant, S_W, S_A, delta, base functionality, the observed
     A222V-background fitness per condition, the expectation, the residual,
     own_e.b and its standard error -- plus one plain sentence per variant
     built from the computed signs.  Row counts are printed at every
     filtering step (AGENTS 5).  Identity gates: rebuilt own_e.b vs the
     recorded column; an independent numpy-only closed-form intercept and
     SE vs both the library and the recorded values; stored delta vs
     S_A - S_W.
S-3  Descriptive 2x2: counts and means of delta by sign of own_e_b and the
     reverse, overall and within tertiles of S_W; plus the two Phase 1 C1
     Spearmans (targets -0.3238 and +0.0854, full precision at planning
     line 145).  Each rho is computed FOUR ways -- the project's own
     ``spearman``, ``scipy.stats.spearmanr``, ``pandas.corr(method=
     'spearman')`` and a numpy-only average-rank Pearson -- printed side by
     side, then compared with the target.
S-4  Cross-system sign statements, QUOTED, never inferred: GB1 e_b (scripts
     155/73/128) and RBD e_T / delta_bind (the data's own README, scripts
     158/163, and the bc_binding.csv header).  For each system, state
     whether a positive value means fitter/tighter than expected -- and
     where no local document says so, report UNAVAILABLE rather than
     infer it.  For RBD the repository's column descriptions live in
     ``data/README.md`` and ``results/summary/summary.md`` of the cloned
     repo, which were never fetched; the direction word is therefore
     UNAVAILABLE locally.  Not downloading them: the only authorised
     download in Phase 4 is ``esm2_t12_35M_UR50D``.  The local Ka/KD
     wording inconsistency is printed as an open question.
S-5  Write ``docs/tasks/phase4-strengthening/SIGN_CONVENTION.md`` (at most
     forty lines): the convention sentence, the worked example, and what a
     negative rho means in words.  Each number in it is WRITTEN from one
     source and RE-DERIVED from a different one (pandas/numpy only); the
     pair is printed, and the script then re-reads the file, parses every
     ``label = value`` back out and asserts it equals the independent
     recomputation.  Digits that are task ids, file names or line numbers
     never appear in ``label = value`` form and are excluded by
     construction (stated in the note's header).

LIMITATIONS (printed again in the run output, per AGENTS 6):
  - This is an orientation audit, not evidence.  It corroborates nothing;
    it only pins down what the words mean, before anything is written
    about the anchor.
  - The 2x2 panels are descriptive cross-sectional summaries of ONE
    dataset: no resampling interval and no p-value by design, and they
    cannot support a claim of direction on their own.
  - The panels group on the SIGN of own_e.b, whose magnitude is estimated
    with error (se_e_b varies by variant); sign misclassification
    attenuates any real difference.  The below-median se_e_b restriction
    reduces but does not remove that (the SE itself is estimated).
  - RBD's direction word is UNAVAILABLE locally; its absence is not
    evidence in either direction, and it is an open question for review.
  - GB1's direction statement rests on the quoted formula, not on a local
    document that uses the words "fitter than expected"; the phrase count
    over scripts/ and docs/ is printed.

Usage (foreground, project interpreter, per AGENTS 1):
  venv/bin/python3 scripts/166_sign_convention.py
  venv/bin/python3 scripts/166_sign_convention.py | tee docs/tasks/phase4-strengthening/PHASE4_A3_OUTPUT.txt
"""
import re
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scipy.stats import spearmanr  # noqa: E402

from scripts.lib.phase3_common import spearman as proj_spearman  # noqa: E402
from scripts.lib.stats_ext import (  # noqa: E402
    rebuild_interaction_fit, wls_line_se)
from scripts.lib.own_context import CONCS, MT_SCORE_COLS  # noqa: E402

T0 = time.time()

TASK32 = ROOT / "data" / "processed" / "task32_analysis_table.csv"
TASK35 = ROOT / "data" / "processed" / "task35_epistatic_set.csv"
RAW = ROOT / "data" / "raw" / "mthfrModel" / "results" / "folate_response_model5.csv"
RBD_DIR = ROOT / "data" / "external" / "rbd_starr2022"
NOTE = ROOT / "docs" / "tasks" / "phase4-strengthening" / "SIGN_CONVENTION.md"

# Targets as recorded in the planning document (Claude's recomputations).
T_RHO_DS = -0.32376573717755663   # planning line 145 (full precision)
T_RHO_ES = 0.085391652432165      # planning line 145 (full precision)
T_RHO_DE = -0.088118064           # planning line 144 / 314 (9 dp)
T_DOC_DS = -0.3238                # planning line 159 (4 dp, the A3 target)
T_DOC_ES = 0.0854                 # planning line 159 (4 dp, the A3 target)
T_ROWS, T_POS = 10757, 654        # analysis set (A2 gate, planning line 143)
TOL_12, TOL_9 = 1e-12, 1e-9

N_PASS, N_FAIL = 0, 0


def _summary(tag):
    print(f"\n{'=' * 74}", flush=True)
    print(f"A3 SUMMARY: {N_PASS} checks PASS, {N_FAIL} FAIL  ({tag})", flush=True)
    print(f"elapsed {time.time() - T0:.1f}s", flush=True)
    print("=" * 74, flush=True)


def note(label, ok, detail=""):
    """Print PASS/FAIL beside the evidence; STOP at the first mismatch."""
    global N_PASS, N_FAIL
    if ok:
        N_PASS += 1
        print(f"  PASS  {label}")
        if detail:
            print(f"        {detail}")
    else:
        N_FAIL += 1
        print(f"  FAIL  {label}")
        if detail:
            print(f"        {detail}")
        _summary("STOPPED AT FIRST MISMATCH; no expectation was adjusted")
        sys.exit(1)


def banner(txt, ch="="):
    print(f"\n{ch * 74}\n{txt}\n{ch * 74}", flush=True)


def quote(label, rel, lineno, tokens, expectation):
    """Print code line and expectation side by side; assert the tokens."""
    p = ROOT / rel
    if not p.is_file():
        note(label, False, f"MISSING FILE {rel}")
        return
    lines = p.read_text(errors="replace").splitlines()
    if lineno > len(lines):
        note(label, False, f"{rel} has only {len(lines)} lines; cited {lineno}")
        return
    code = lines[lineno - 1].rstrip()
    print(f"    {rel}:{lineno}")
    print(f"      code | {code.strip()}")
    print(f"      doc  | {expectation}")
    missing = [t for t in tokens if t not in code]
    note(label, not missing,
         "all quoted tokens present on the cited line" if not missing
         else f"tokens NOT on that line: {missing}")


# ==========================================================================
# Independent recomputations (pandas/numpy only -- no scipy, no lib calls)
# ==========================================================================
def rho_pandas(x, y):
    """Spearman via pandas' own ranking + Pearson (independent of scipy)."""
    df = pd.DataFrame({"x": np.asarray(x, float), "y": np.asarray(y, float)})
    df = df.dropna()
    return float(df["x"].rank(method="average").corr(
        df["y"].rank(method="average")))


def _avg_rank(a):
    """Average ranks for ties, written from scratch with numpy only."""
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    sa = a[order]
    ranks = np.empty(a.size, float)
    i = 0
    while i < a.size:
        j = i
        while j + 1 < a.size and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def rho_numpy(x, y):
    """Spearman as Pearson of average ranks, numpy only (no scipy/pandas)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    rx, ry = _avg_rank(x[m]), _avg_rank(y[m])
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    den = float(np.sqrt((rx * rx).sum() * (ry * ry).sum()))
    return float((rx * ry).sum() / den) if den > 0 else float("nan")


def closed_form_intercept(resid, m_se, concs, valid):
    """Weighted intercept of resid ~ 1 + concs, written from the closed form
    (independent of own_context.wls_line: w*x*x here vs w*(x**2) there, so
    the two paths differ only by floating-point summation order)."""
    w = np.where(valid, 1.0 / np.where(valid, m_se, 1.0) ** 2, 0.0)
    yy = np.where(valid, resid, 0.0)
    x = np.asarray(concs, float)
    S0 = w.sum(axis=1)
    S1 = (w * x).sum(axis=1)
    S2 = (w * x * x).sum(axis=1)
    T0 = (w * yy).sum(axis=1)
    T1 = (w * x * yy).sum(axis=1)
    det = S0 * S2 - S1 * S1
    with np.errstate(divide="ignore", invalid="ignore"):
        b = np.where(det != 0, (S2 * T0 - S1 * T1) / det, np.nan)
    return np.where((~valid).sum(axis=1) > 2, np.nan, b)


def closed_form_se(m_se, concs, valid):
    """Analytic SE of that intercept, written from (X'WX)^-1."""
    w = np.where(valid, 1.0 / np.where(valid, m_se, 1.0) ** 2, 0.0)
    x = np.asarray(concs, float)
    S0 = w.sum(axis=1)
    S1 = (w * x).sum(axis=1)
    S2 = (w * x * x).sum(axis=1)
    det = S0 * S2 - S1 * S1
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(det > 0, np.sqrt(np.abs(S2 / det)), np.nan)
    return np.where((~valid).sum(axis=1) > 2, np.nan, s)


def sign_sentence(hgvs, delta, eb, se=None):
    """One plain sentence per variant, built ONLY from computed signs.

    With ``se`` given the sentence carries that number too (run output);
    the SIGN_CONVENTION.md copy passes ``se=None`` so the note contains no
    number that is not written in ``label = value`` form and re-derived.
    """
    d_txt = ("positive: the model scores the substitution as MORE favourable "
             "in the A222V background"
             if delta > 0 else
             "negative: the model scores the substitution as LESS favourable "
             "in the A222V background")
    e_txt = ("positive: observed BETTER than the multiplicative no-interaction "
             "expectation" if eb > 0 else
             "negative: observed WORSE than the multiplicative no-interaction "
             "expectation")
    rel = "the same direction" if delta * eb > 0 else "OPPOSITE directions"
    se_txt = f" (se_e.b {se:.6f})" if se is not None else ""
    return (f"{hgvs}: delta is {d_txt}; own_e.b is {e_txt}{se_txt}; "
            f"the model's shift and the measured interaction point in "
            f"{rel}.")


# ==========================================================================
if __name__ == "__main__":
    banner("SCRIPT 166 -- Phase 4 task A3, Module S: the sign convention\n"
           "read-only with respect to the planning document and "
           "PHASE2_PREREG.md")

    # ---------------------------------------------------------------- S-1
    banner("S-1  quote, with file and line numbers (code beside expectation)",
           "-")
    S1 = [
        ("S-1a rebuild_interaction_fit defines own_e.b's construction",
         "scripts/lib/stats_ext.py", 63, ["def rebuild_interaction_fit(raw):"],
         "own_e.b is built by rebuild_interaction_fit in scripts/lib/stats_ext.py"),
        ("S-1b the corrected (second) pass is the one own_e.b comes from",
         "scripts/lib/stats_ext.py", 84, ["e2 = fit_interaction("],
         "fit_interaction is called a second time with the fitness-dependent correction"),
        ("S-1c the residual handed downstream is that second pass's",
         "scripts/lib/stats_ext.py", 87, ['"resid": e2["resid"]'],
         "the returned residual matrix is e2's, i.e. m_score - expected after the correction"),
        ("S-1d wls_line fits intercept + slope by weighted least squares",
         "scripts/lib/own_context.py", 48, ["def wls_line(y, se, x, valid):"],
         "wls_line in scripts/lib/own_context.py is the weighted fit own_e.b's intercept comes from"),
        ("S-1e its weights are 1/se^2",
         "scripts/lib/own_context.py", 49, ["weights 1/se^2"],
         "own_e.b's intercept is weighted by 1/se^2 (per-condition standard errors)"),
        ("S-1f the weighted-intercept closed form",
         "scripts/lib/own_context.py", 64, ["(S2 * T0 - S1 * T1) / det"],
         "the intercept is the closed-form weighted intercept (S2*T0 - S1*T1)/det"),
        ("S-1g fit_interaction's expectation is multiplicative (docstring)",
         "scripts/lib/own_context.py", 148,
         ["expected(c) = single_mutant_term(c) * (b_A222V + c*r_A222V)"],
         "the no-interaction expectation is the product of the two single-mutant terms"),
        ("S-1h ...and in code",
         "scripts/lib/own_context.py", 157, ["expected = sm * a222v_line"],
         "expected(c) = single-mutant term * the A222V background line"),
        ("S-1i the residual is m_score - expected",
         "scripts/lib/own_context.py", 163,
         ["resid = np.where(valid, m_score - expected, np.nan)"],
         "the residual subtracts the expectation from the observed A222V-arm score"),
        ("S-1j own_e.b is that residual's weighted intercept",
         "scripts/lib/own_context.py", 165,
         ["e_b, e_r, df = wls_line(resid, m_se, concs, valid)"],
         "own_e.b = wls_line(resid, m_se, concs, valid)'s intercept"),
        ("S-1k delta = esm2_score_a222v_bg - esm2_score (scripts/45)",
         "scripts/45_c1_reconciliation.py", 97,
         ['df["delta_esm"] = df["esm2_score_a222v_bg"] - df["esm2_score"]'],
         "delta is the model's A222V-background score minus its WT-background score"),
        ("S-1l the same definition written independently (scripts/12)",
         "scripts/12_validate_a222v_scores.py", 29,
         ['merged["delta_esm"] = merged["esm2_score_a222v_bg"] - merged["esm2_score"]'],
         "the second, independent definition of delta agrees"),
        ("S-1m delta's printed meaning, S(v|A222V) - S(v|WT)",
         "scripts/12_validate_a222v_scores.py", 30,
         ["delta_ESM = S(v|A222V) - S(v|WT)"],
         "delta is a background SHIFT of the model's score for one substitution"),
        ("S-1n the tail registered in PHASE2_PREREG.md is negative (read only)",
         "docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md", 36,
         ["direction pre-stated negative"],
         "PHASE2_PREREG.md pre-stated the negative tail for the anchor"),
    ]
    for item in S1:
        quote(*item)
    print(f"  S-1: {len(S1)} quote checks passed "
          "(each printed code beside expectation)")

    # ---------------------------------------------------------------- S-2
    banner("S-2  worked example (computed, not typed)", "-")
    t32 = pd.read_csv(TASK32, float_precision="round_trip")
    t35 = pd.read_csv(TASK35)
    cols = ["delta_esm", "own_e_b", "position", "esm2_score",
            "base_functionality"]
    base = t32[t32[cols].notna().all(axis=1)].copy()
    print(f"  task32 rows read: {len(t32):,}; after the finite-on-every-"
          f"analysis-column filter: {len(base):,}")
    note("S-2a analysis set = 10,757 rows at 654 positions (planning 143)",
         len(base) == T_ROWS and base.position.nunique() == T_POS,
         f"got {len(base):,} rows / {base.position.nunique()} positions; "
         f"target {T_ROWS:,} / {T_POS}")

    base = base.merge(t35[["hgvs_pro", "se_e_b"]], on="hgvs_pro", how="left")
    n_se = int(base.se_e_b.notna().sum())
    note("S-2b se_e_b joins completely (no row lost, none duplicated)",
         n_se == len(base) and not t35.hgvs_pro.duplicated().any(),
         f"{n_se:,} of {len(base):,} rows carry se_e_b; task35 duplicated "
         f"hgvs_pro: {bool(t35.hgvs_pro.duplicated().any())}")
    med_se = float(base.se_e_b.median())
    sub = base[base.se_e_b < med_se].copy()
    n_eq = int((base.se_e_b == med_se).sum())
    print(f"  median se_e_b = {med_se!r}; strictly below: {len(sub):,}; "
          f"exactly at the median: {n_eq} (excluded by 'below the median')")
    note("S-2c the se_e_b-below-median subset is non-trivial and accounted for",
         0 < len(sub) < len(base) and n_eq == 1,
         f"{len(sub):,} of {len(base):,} rows in the worked-example subset; "
         "every excluded row is above or at the median se_e_b")
    note("S-2d no zero-valued sign is silently grouped (delta, own_e.b)",
         int((sub.delta_esm == 0).sum()) == 0
         and int((sub.own_e_b == 0).sum()) == 0,
         f"delta == 0: {int((sub.delta_esm == 0).sum())}; own_e.b == 0: "
         f"{int((sub.own_e_b == 0).sum())} (so the 2x2 has no zero cell)")

    # the fit, imported from the library (AGENTS 2: never reimplemented)
    raw = pd.read_csv(RAW)
    fit = rebuild_interaction_fit(raw)
    e2, valid, Mse = fit["e2"], fit["valid"], fit["M_se"]

    reb = pd.DataFrame({"hgvs_pro": raw["hgvs"], "rebuild_eb": e2["e_b"],
                        "rebuild_row": np.arange(len(raw))})
    m = base.merge(reb, on="hgvs_pro", how="left")
    both = m[np.isfinite(m.rebuild_eb) & np.isfinite(m.own_e_b)]
    d_eb = float(np.abs(both.rebuild_eb - both.own_e_b).max())
    note("S-2e rebuilt own_e.b == recorded own_e_b (identity)",
         d_eb < TOL_12,
         f"max|diff| = {d_eb:.3e} over {len(both):,} rows "
         f"(tolerance {TOL_12:g})")

    idx = m.rebuild_row.to_numpy()
    fin = np.isfinite(idx)
    idx = idx[fin].astype(int)
    eb_cf = closed_form_intercept(e2["resid"], Mse, CONCS, valid)
    se_cf = closed_form_se(Mse, CONCS, valid)
    se_lib = wls_line_se(Mse, CONCS, valid)[0]
    m = m.assign(eb_cf=np.nan, se_cf=np.nan, se_lib=np.nan)
    m.loc[fin, "eb_cf"] = eb_cf[idx]
    m.loc[fin, "se_cf"] = se_cf[idx]
    m.loc[fin, "se_lib"] = se_lib[idx]

    d_cf = float(np.nanmax(np.abs(m.eb_cf.to_numpy() - m.own_e_b.to_numpy())))
    note("S-2f independent numpy closed-form intercept == recorded own_e_b",
         d_cf < TOL_12,
         f"max|diff| = {d_cf:.3e} over {len(m):,} rows "
         f"(w*x*x here vs w*(x**2) in wls_line: summation-order only)")

    t35_se = t35[["hgvs_pro", "se_e_b"]].rename(columns={"se_e_b": "se_t35"})
    mm = m.merge(t35_se, on="hgvs_pro", how="left")
    d_se = float(np.nanmax(np.abs(mm.se_cf.to_numpy()
                                  - mm.se_t35.to_numpy())))
    d_se2 = float(np.nanmax(np.abs(mm.se_lib.to_numpy()
                                   - mm.se_t35.to_numpy())))
    note("S-2g independent SE == recorded se_e_b (library path too)",
         d_se < TOL_12 and d_se2 < TOL_12,
         f"closed-form max|diff| = {d_se:.3e}, library max|diff| = "
         f"{d_se2:.3e} over {len(mm):,} rows")

    d_ds = float(np.nanmax(np.abs(m.esm2_score_a222v_bg.to_numpy()
                                  - m.esm2_score.to_numpy()
                                  - m.delta_esm.to_numpy())))
    note("S-2h stored delta == S_A - S_W recomputed (identity)",
         d_ds < TOL_12, f"max|diff| = {d_ds:.3e}")

    # the six variants
    sub = sub.merge(m[["hgvs_pro", "rebuild_row", "eb_cf", "se_cf"]],
                    on="hgvs_pro", how="left")
    top = sub.nlargest(3, "own_e_b")
    bot = sub.nsmallest(3, "own_e_b")
    rows_shown = 0
    sentences = []
    for title, dfx in (("3 MOST POSITIVE own_e.b", top),
                       ("3 MOST NEGATIVE own_e.b", bot)):
        print(f"\n  {title}  (within se_e_b < median = {med_se!r})")
        for _, r in dfx.iterrows():
            i = int(r.rebuild_row)
            obs_m = raw.loc[i, MT_SCORE_COLS].to_numpy(float)
            exp = e2["expected"][i]
            res = e2["resid"][i]
            obs_s = np.array2string(obs_m, precision=6, floatmode="fixed")
            exp_s = np.array2string(exp, precision=6, floatmode="fixed")
            res_s = np.array2string(res, precision=6, floatmode="fixed")
            sw_v = float(r.esm2_score)
            sa_v = float(r.esm2_score_a222v_bg)
            dl_v = float(r.delta_esm)
            eb_v = float(r.own_e_b)
            se_v = float(r.se_e_b)
            bf_v = float(r.base_functionality)
            print(f"    {r.hgvs_pro}  position {int(r.position)}  "
                  f"{r.wt_aa} -> {r.mut_aa}")
            print(f"      S_W (esm2_score)          = {sw_v!r}")
            print(f"      S_A (esm2_score_a222v_bg) = {sa_v!r}")
            print(f"      delta (stored)            = {dl_v!r}   "
                  f"[independent S_A - S_W = {sa_v - sw_v!r}]")
            print(f"      base functionality        = {bf_v!r}")
            print("      observed A222V fitness per condition "
                  "(12, 25, 100, 200):")
            print(f"        m.score  = {obs_s}")
            print("      expectation (multiplicative x correction) and "
                  "residual per condition:")
            print(f"        expected = {exp_s}")
            print(f"        residual = {res_s}")
            print(f"      own_e.b (recorded)        = {eb_v!r}   "
                  f"[independent closed-form = {float(r.eb_cf)!r}]")
            print(f"      se_e.b (recorded)         = {se_v!r}   "
                  f"[independent closed-form = {float(r.se_cf)!r}]")
            sentences.append(sign_sentence(r.hgvs_pro, dl_v, eb_v, se_v))
            rows_shown += 1
    print("\n  plain sentences built from the computed signs:")
    for s in sentences:
        print(f"    - {s}")
    note("S-2i six variants shown, each with one sign-built sentence",
         rows_shown == 6 and len(sentences) == 6
         and len(set(top.hgvs_pro) | set(bot.hgvs_pro)) == 6,
         f"rows printed {rows_shown}, sentences {len(sentences)}, "
         "all six variants distinct")

    # ---------------------------------------------------------------- S-3
    banner("S-3  descriptive 2x2 and the two Phase 1 C1 Spearmans", "-")
    delta = base.delta_esm.to_numpy(float)
    own = base.own_e_b.to_numpy(float)
    sw = base.esm2_score.to_numpy(float)

    def panel(df, title):
        n = len(df)
        print(f"  PANEL {title}   n = {n:,}")
        sg_e = np.where(df.own_e_b.to_numpy() > 0, "own_e.b > 0",
                        "own_e.b < 0")
        sg_d = np.where(df.delta_esm.to_numpy() > 0, "delta > 0", "delta < 0")
        tot = 0
        for lab in ("own_e.b < 0", "own_e.b > 0"):
            k = sg_e == lab
            tot += int(k.sum())
            md = float(df.delta_esm.to_numpy()[k].mean())
            print(f"    rows = {lab:<12}  n = {int(k.sum()):>6,}   "
                  f"mean(delta) = {md:+.9f}")
        print(f"    row accounting (delta by sign of own_e.b): {tot:,} "
              f"== {n:,} -> {tot == n}")
        tot2 = 0
        for lab in ("delta < 0", "delta > 0"):
            k = sg_d == lab
            tot2 += int(k.sum())
            mo = float(df.own_e_b.to_numpy()[k].mean())
            print(f"    rows = {lab:<12}  n = {int(k.sum()):>6,}   "
                  f"mean(own_e.b) = {mo:+.9f}")
        print(f"    row accounting (own_e.b by sign of delta): {tot2:,} "
              f"== {n:,} -> {tot2 == n}")
        return tot, tot2

    t1, t2 = panel(base, "overall (analysis set)")
    note("S-3a the overall 2x2 accounts for every row",
         t1 == T_ROWS and t2 == T_ROWS,
         f"both partitions sum to {t1:,} / {t2:,} against {T_ROWS:,}")

    try:
        base["sw_t"] = pd.qcut(base.esm2_score, 3,
                               labels=["T1 lowest S_W", "T2 middle S_W",
                                       "T3 highest S_W"])
        tb_ok = True
    except ValueError as exc:
        tb_ok = False
        print(f"  qcut failed: {exc}")
    note("S-3b tertiles of S_W cut the analysis set into three non-empty bins",
         tb_ok and int(base.sw_t.isna().sum()) == 0,
         f"bin sizes: "
         + ", ".join(f"{k} = {v:,}" for k, v in
                     base.sw_t.value_counts(sort=False).items())
         if tb_ok else "tertile cut failed")
    for lab, g in base.groupby("sw_t", observed=True):
        a, b = panel(g, f"tertile {lab}")
        note(f"S-3c tertile {lab} accounts for every row",
             a == len(g) and b == len(g),
             f"{a:,} / {b:,} against {len(g):,}")

    print("\n  the two Phase 1 C1 Spearmans, four independent routes each")
    routes = [("project spearman (phase3_common)", proj_spearman),
              ("scipy.stats.spearmanr",
               lambda x, y: float(spearmanr(x, y)[0])),
              ("pandas corr(method='spearman')", rho_pandas),
              ("numpy average-rank Pearson", rho_numpy)]

    def four_way(label, x, y, target, tol, doc4=None):
        vals = []
        for name, fn in routes:
            v = float(fn(x, y))
            vals.append((name, v))
            print(f"    {name:<36} = {v!r}")
        print(f"    {'TARGET (planning doc)':<36} = {target!r}"
              + (f"   [4 dp in the A3 task: {doc4}]" if doc4 else ""))
        spread = max(v for _, v in vals) - min(v for _, v in vals)
        worst = max(abs(v - target) for _, v in vals)
        note(label, spread < TOL_12 and worst <= tol,
             f"four routes agree to {spread:.3e}; worst deviation from the "
             f"target = {worst:.3e} (tolerance {tol:g})")

    four_way("S-3d rho(delta, S_W) reproduces the planning target",
             delta, sw, T_RHO_DS, TOL_12, T_DOC_DS)
    four_way("S-3e rho(own_e.b, S_W) reproduces the planning target",
             own, sw, T_RHO_ES, TOL_12, T_DOC_ES)
    four_way("S-3f rho(delta, own_e.b) reproduces the anchor rho "
             "(planning 144/314, 9 dp)",
             delta, own, T_RHO_DE, TOL_9)

    # ---------------------------------------------------------------- S-4
    banner("S-4  cross-system sign statements -- QUOTED, never inferred", "-")
    S4 = [
        ("S-4a GB1: e_b = f_vb - f_v * f_bg / f_wt",
         "scripts/155_gb1_regime_analysis.py", 21,
         ["e_b = f_vb - f_v * f_bg / f_wt"],
         "GB1's e_b is measured double minus the multiplicative expectation "
         "of the two singles"),
        ("S-4b GB1: the same in code, on the W scale with f_wt = 1",
         "scripts/155_gb1_regime_analysis.py", 394,
         ['long["e_b"] = long["W_double"] - long["W_v"] * long["W_bg"]'],
         "positive e_b = the measured double sits ABOVE the expectation"),
        ("S-4c GB1: what the W scale is",
         "scripts/155_gb1_regime_analysis.py", 24,
         ["W_x     = (sel_count / input_count) / F_B,wt"],
         "the assay's scale is selection enrichment -- the fitness scale "
         "the residual is taken on"),
        ("S-4d GB1: 'mirroring measured - expected'",
         "scripts/73_gb1_estimator_transplant.py", 58,
         ["e_b(v) = f(v + bg) - E[.] (additive-scale residual"],
         "GB1's e_b is an additive-scale residual of the measured double arm"),
        ("S-4e GB1: the formula restated",
         "scripts/128_gb1_olson_verify_and_transplant_repro.py", 135,
         ["e_b      = f_vb - expct"],
         "positive e_b = measured above expectation"),
        ("S-4f RBD: the data's own README names the quantities",
         "data/external/rbd_starr2022/README.md", 22,
         ["change in ACE2-binding affinity", "change in RBD expression"],
         "delta_bind / delta_expr are described by the repository as the "
         "CHANGE in affinity / expression caused by a mutation"),
        ("S-4g RBD: which column `bind` comes from",
         "scripts/158_multidms_rbd.py", 29,
         ["Phenotypes: bind = bc_binding.csv / log10Ka"],
         "`bind` is the bc_binding.csv measurement column log10Ka"),
        ("S-4h RBD: delta_bind's arithmetic (authors' own construction)",
         "scripts/163_rbd_targets.py", 30,
         ["`delta_bind` is the authors' own per-library construction"],
         "delta_bind is defined by the authors per library"),
        ("S-4i RBD: delta_bind = rep - that target's wild-type row's rep",
         "scripts/163_rbd_targets.py", 31,
         ["mean over libraries of (rep - that target's wild-type row's"],
         "positive delta_bind = this mutation's value ABOVE the wild-type "
         "row's value, per library"),
        ("S-4j RBD: wild-type rows are exactly zero",
         "scripts/163_rbd_targets.py", 35,
         ["every wild-type row has delta_bind = delta_expr = 0 exactly"],
         "the zero of the scale is the wild-type row"),
        ("S-4k RBD: e_T = delta_T(v) - delta_Wuhan(v)",
         "scripts/163_rbd_targets.py", 47,
         ["e_T(v) = delta_T(v) - delta_Wuhan(v)"],
         "e_T is the per-mutation effect in T minus that mutation's effect "
         "in Wuhan-Hu-1"),
        ("S-4l RBD: the frozen prereg words `log10 KD` (inconsistent with "
         "the column header -- printed as an open question)",
         "scripts/163_rbd_targets.py", 11,
         ["Phenotype PRIMARY: ACE2 binding (the per-mutation effect on log10 KD"],
         "the project's own frozen block says log10 KD where the data "
         "column is log10Ka -- flagged, not resolved"),
    ]
    for item in S4:
        quote(*item)

    hdr = (RBD_DIR / "bc_binding.csv").open().readline().strip()
    note("S-4m the barcode table's own header carries `log10Ka`",
         "log10Ka" in hdr, f"header: {hdr}")

    # the direction words, stated per system
    print("\n  DIRECTION STATEMENTS (one per system)")
    print("    MTHFR atlas own_e.b: POSITIVE = observed ABOVE the "
          "multiplicative expectation")
    print("      -> better than expected.  Quoted above: own_context.py "
          "lines 148/157/163/165.")
    print("    GB1 e_b: POSITIVE = measured double-arm fitness ABOVE the "
          "multiplicative")
    print("      expectation of the two singles (quotes S-4a..S-4e) on the "
          "selection-enrichment")
    print("      scale (S-4c) -> fitter than expected.")
    phrase_hits = []
    for sub_dir in ("scripts", "docs"):
        for p in (ROOT / sub_dir).rglob("*"):
            if p.is_file() and p.suffix in (".py", ".md", ".txt"):
                try:
                    if "fitter than expected" in p.read_text(errors="ignore"):
                        phrase_hits.append(str(p.relative_to(ROOT)))
                except OSError:
                    pass
    print(f"      files under scripts/ and docs/ containing the literal "
          f"phrase 'fitter than expected': {len(phrase_hits)}"
          + (f" -> {phrase_hits}" if phrase_hits else
             " (the GB1 wording above is derived from the quoted formula, "
             "not copied from a document)"))
    print("      (that search is not a quotation: of the hits, one is this "
          "task's own instruction line in")
    print("      PHASE4_STRENGTHENING.md and one is this script's search "
          "code -- neither states a")
    print("      sign convention.  The GB1 direction above therefore rests "
          "on the quoted formulas.)")
    print("\n  files actually on disk under data/external/rbd_starr2022/:")
    for p in sorted(RBD_DIR.rglob("*")):
        if p.is_file():
            print(f"    {p.relative_to(RBD_DIR)}")

    absent = [str(p.relative_to(ROOT))
              for p in (RBD_DIR / "data" / "README.md",
                        RBD_DIR / "results" / "summary" / "summary.md")
              if not p.exists()]
    print("    RBD e_T / delta_bind: ARITHMETIC (quoted) = positive means "
          "the mutation's value")
    print("      ABOVE the wild-type row's / Wuhan's value (S-4h, S-4i, "
          "S-4j, S-4k).")
    print("      DIRECTION WORD ('stronger' / 'tighter' / 'weaker'): "
          "UNAVAILABLE locally.")
    if len(absent) == 2:
        print("      reason: the repository's own column descriptions live "
              "in these two paths, which were")
        print("      never fetched (and are not fetched now -- the only "
              "authorised download in Phase 4")
        print("      is esm2_t12_35M_UR50D):")
        for a in absent:
            print(f"        {a}")
    else:
        print("      WARNING: a column description IS present locally "
              "(see S-4n): quote it before")
        print("      asserting any direction word.")
    print("      open question for review: the local wording disagrees -- "
          "bc_binding.csv and script 158 say")
    print("      `log10Ka` while the frozen block quoted at S-4l says "
          "`log10 KD`; the two run in")
    print("      opposite directions, so no direction word is asserted "
          "until the repository's own")
    print("      description is obtained and quoted.  Its absence is not "
          "evidence in either direction.")
    note("S-4n RBD direction word is UNAVAILABLE because the repository's "
         "column descriptions are genuinely absent from disk",
         len(absent) == 2,
         "absent: " + ", ".join(absent)
         + "  (if this FAILS, the description exists locally: read it and "
           "quote it instead of stopping)")

    # ---------------------------------------------------------------- S-5
    banner("S-5  write SIGN_CONVENTION.md (every number re-derived)", "-")
    ex = bot.iloc[0]  # pre-registered: most negative own_e.b of the S-2 set
    ex_i = int(ex.rebuild_row)
    label_vals = []   # (label, written A, independent B, tolerance)

    def add(label, a, b, tol):
        label_vals.append((label, a, b, tol))

    _c5 = ["delta_esm", "own_e_b", "position", "esm2_score",
           "base_functionality"]
    _mask = np.isfinite(t32[_c5].to_numpy(float)).all(axis=1)
    n_rows_a = len(base)
    n_rows_b = int(_mask.sum())
    add("n_rows", float(n_rows_a), float(n_rows_b), 0.0)
    n_pos_a = int(base.position.nunique())
    n_pos_b = int(np.unique(t32["position"].to_numpy(float)[_mask]).size)
    add("n_positions", float(n_pos_a), float(n_pos_b), 0.0)

    r_de_a = float(spearmanr(delta, own)[0])
    r_de_b = rho_pandas(delta, own)
    add("rho(delta, own_e_b)", r_de_a, r_de_b, TOL_12)
    r_ds_a = float(spearmanr(delta, sw)[0])
    r_ds_b = rho_pandas(delta, sw)
    add("rho(delta, S_W)", r_ds_a, r_ds_b, TOL_12)
    r_es_a = float(spearmanr(own, sw)[0])
    r_es_b = rho_pandas(own, sw)
    add("rho(own_e_b, S_W)", r_es_a, r_es_b, TOL_12)

    # worked-example numbers: written from the recorded columns,
    # re-derived from an independent path
    add("S_W", float(ex.esm2_score),
        float(ex.esm2_score_a222v_bg - ex.delta_esm), TOL_12)
    add("S_A", float(ex.esm2_score_a222v_bg),
        float(ex.esm2_score + ex.delta_esm), TOL_12)
    add("delta", float(ex.delta_esm),
        float(ex.esm2_score_a222v_bg - ex.esm2_score), TOL_12)
    add("own_e_b", float(ex.own_e_b), float(ex.eb_cf), TOL_12)
    add("se_e_b", float(ex.se_e_b), float(ex.se_cf), TOL_12)
    add("position", float(ex.position),
        float(t32.loc[t32.hgvs_pro == ex.hgvs_pro, "position"].iloc[0]),
        0.0)

    for lab, a, b, tol in label_vals:
        same = abs(float(a) - float(b)) <= max(tol, 0.0)
        print(f"    {lab:<22} written = {a!r}   "
              f"independent pandas/numpy = {b!r}   match = {same}")
    note("S-5a every number staged for the note has an independent "
         "recomputation that agrees",
         all(abs(float(a) - float(b)) <= max(tol, 0.0)
             for _, a, b, tol in label_vals),
         f"{len(label_vals)} numbers")

    d_ex = sign_sentence(ex.hgvs_pro, ex.delta_esm, ex.own_e_b)
    note("S-5b the example was chosen by the pre-registered rule, not by "
         "how well it reads",
         float(ex.own_e_b) == float(sub.own_e_b.min()),
         f"{ex.hgvs_pro} has the minimum own_e.b "
         f"({float(ex.own_e_b)!r}) of the {len(sub):,}-row worked-example "
         "subset")

    lines = [
        "# SIGN_CONVENTION.md -- Phase 4 Module S, generated by "
        "scripts/166_sign_convention.py.",
        "# Regenerate with that script; never hand-edit. Every derived "
        "number below (task ids, file",
        "# names and line numbers excepted) is written from one source and "
        "re-derived from a",
        "# different one using pandas/numpy only; the generator prints each "
        "pair and re-reads",
        "# this file to assert the numbers here equal the independent "
        "recomputation.",
        "SIGN SENTENCE (quote verbatim wherever a rho is discussed):",
        "  delta = S(v|A222V) - S(v|WT): positive delta means the model "
        "scores the substitution",
        "  as MORE favourable in the A222V background than in the wild-type "
        "background.",
        "  own_e_b = observed A222V-arm score minus the multiplicative "
        "no-interaction expectation,",
        "  taken as its concentration-weighted intercept: positive own_e_b "
        "means observed BETTER",
        "  than the expectation, negative own_e_b means observed WORSE than "
        "the expectation.",
        "  A NEGATIVE rho means the model's background shift runs OPPOSITE "
        "to the measured shift:",
        "  substitutions the model makes look better under A222V are, on "
        "average, the ones whose",
        "  measured interaction residual is lower -- direction only; no "
        "magnitude, mechanism or",
        "  causal claim follows from the sign.",
        "WORKED EXAMPLE (pre-registered selection: the most negative "
        "own_e.b in the se-below-median set):",
        f"  example {ex.hgvs_pro}: position = {int(ex.position)}, "
        f"wild_type = {ex.wt_aa}, mutant = {ex.mut_aa},",
        f"    S_W = {float(ex.esm2_score)!r}, S_A = "
        f"{float(ex.esm2_score_a222v_bg)!r}, delta = "
        f"{float(ex.delta_esm)!r}, own_e_b = {float(ex.own_e_b)!r}, "
        f"se_e_b = {float(ex.se_e_b)!r}",
        f"  {d_ex}",
        "ANCHOR NUMBERS (analysis set: variants with finite delta, "
        "own_e_b, S_W and base functionality):",
        f"  n_rows = {n_rows_a}",
        f"  n_positions = {n_pos_a}",
        f"  rho(delta, own_e_b) = {r_de_a!r}",
        f"  rho(delta, S_W) = {r_ds_a!r}",
        f"  rho(own_e_b, S_W) = {r_es_a!r}",
        "WHAT A NEGATIVE RHO MEANS IN WORDS: where the model says a "
        "substitution becomes more",
        "favourable in the A222V background, the measured interaction "
        "residual tends to sit lower,",
        "and where the model says it becomes less favourable the residual "
        "tends to sit higher: the",
        "model's direction of change and the data's direction of change "
        "disagree. This is a",
        "statement about direction alone, on one dataset, with no interval "
        "attached; it says",
        "nothing about how large either quantity is, and nothing about "
        "mechanism. Cross-system",
        "sign statements (MTHFR, GB1, RBD) are recorded in the task A3 run "
        "output, not here.",
    ]
    assert len(lines) <= 40, f"note is {len(lines)} lines"
    NOTE.write_text("\n".join(lines) + "\n")
    print(f"\n  wrote {NOTE.relative_to(ROOT)}  ({len(lines)} lines)")
    for lab, a, b, tol in label_vals:
        print(f"    {lab:<22} in the note = {a!r}   "
              f"independent pandas/numpy = {b!r}")

    text = NOTE.read_text()
    parsed_all = True
    for lab, a, b, tol in label_vals:
        pat = (r"(?<![A-Za-z_])" + re.escape(lab) + r"\s*=\s*"
               r"([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)")
        hits = re.findall(pat, text)
        ok = len(hits) == 1 and abs(float(hits[0]) - float(b)) <= max(tol, 0.0)
        print(f"    parsed back {lab:<22} -> {hits}  vs independent {b!r}  "
              f"{'OK' if ok else 'MISMATCH'}")
        parsed_all = parsed_all and ok
    note("S-5c every number parsed back out of the note equals its "
         "independent recomputation",
         parsed_all, f"{len(label_vals)} labels, each matched exactly once")
    note("S-5d SIGN_CONVENTION.md is at most forty lines",
         len(lines) <= 40, f"{len(lines)} lines written")

    # ---------------------------------------------------------- summary
    banner("READ-BACK OF THE NOTE (what later modules will quote)", "-")
    print(NOTE.read_text())
    print("\n  LIMITATIONS carried in this run's output (AGENTS 6):")
    print("    - orientation audit only; corroborates no estimate")
    print("    - 2x2 panels are descriptive: no interval, no p-value, one "
          "dataset")
    print("    - sign-of-own_e.b grouping attenuated by estimated-SE error; "
          "below-median se_e.b")
    print("      restricts the magnitude of that error but does not remove "
          "it")
    print("    - RBD direction word UNAVAILABLE locally; Ka/KD wording "
          "inconsistent; open question")
    print("    - GB1 direction rests on the quoted formula; the literal "
          "phrase count is printed above")
    _summary("ALL CHECKS PASSED")
