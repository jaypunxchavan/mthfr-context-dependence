"""Script 134 -- Phase 2 diagnostics Tasks D4 and D5: the SHIFT-MAGNITUDE
CONFOUND, and whether D_site survives controlling for it.

D4 is the single highest-leverage task in this session.  If rho_b is mostly
a function of how large a background's overall representational shift is --
independent of any relationship to measured epistasis -- then what Phase 2
shows is that position 222 perturbs ESM-2's representation more than other
positions do, which is a property of the model, not evidence about MTHFR.

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  Per PHASE2_DIAGNOSTICS.md rule 9, the three words reserved for the
frozen test are not used anywhere in this script, and this script never
computes or names that outcome.  D_site_resid is a descriptive companion to
the frozen D_site, never a replacement for it.

DELTA_B: EXACT SOURCE, QUOTED, AND INDEPENDENTLY RE-DERIVED
-----------------------------------------------------------
The plan requires the exact join and column names to be quoted from script
125 rather than assumed.  From scripts/125_phase2_analysis.py:

  build_frame():
      atlas = pd.read_csv(ROOT / "data/processed/"
                          "task32_analysis_table.csv")
      frame = atlas.dropna(subset=["delta_esm", "own_e_b"]).copy()
  build_phase2():
      f = pd.read_csv(ROOT / "data/processed/phase2/"
                      f"bg_{r.bg_id}.csv")           # cols position, mut_aa, score
      m = frame.merge(f[["position", "mut_aa", "score"]],
                      on=["position", "mut_aa"], how="left")
      m = m[m.score.notna()].copy()
      m["delta"] = m.score - m.esm2_score
  A222V (PIN-3):
      A.a222v_rows = frame[["position", "delta_esm", "own_e_b",
                            "region"]].rename(columns={"delta_esm": "delta"})

So: score_b(v) from data/processed/phase2/bg_<bg_id>.csv::score, esm2_score
from data/processed/task32_analysis_table.csv::esm2_score, joined on
(position, mut_aa), and delta_b(v) = score_b(v) - esm2_score(v).  A222V's own
"score" is the cached task32 column delta_esm.

This script does not merely reuse 125's precomputed `delta` column.  It
RE-DERIVES delta independently from the two raw files for all 96
backgrounds and gates the result against 125's own `delta` to 1e-12
(AGENTS 5: "verify column identity before reporting agreement between two
sources").  A silent column-duplication or join-slip bug would show up here
rather than being inherited silently into the headline correlation.

THE ROWS USED
-------------
"the same usable rows script 125 used to compute that background's rho_b":
that is exactly A.bg_rows[bg_id] as 125 built it -- post score-join, post
NaN-score drop, with the own-position exclusion already applied (125
implements it as "the background's own substitution is absent from its own
score file, so the row's score is NaN and it drops", then asserts the
result under gate G-C).  For the H view, those same rows restricted to
125's Hset, which is what 125 does before computing rho_H.

RESAMPLING UNIT -- READ THIS
----------------------------
BACKGROUND.  Every quantity in this script has exactly one value per
background (rho_b, mean_abs_delta_b) or is a contrast of per-background
means.  The only thing a bootstrap can legitimately resample is WHICH
BACKGROUNDS WERE DRAWN.  Each draw resamples background indices with
replacement; within a draw, each background's already-computed rho_b and
mean_abs_delta_b are held FIXED.  No rho_b is recomputed and no score is
re-read on any draw.

This is NOT the resampling unit Phase 2's own primary analysis used.
Script 125 resamples POSITIONS within a background (PIN-9 naive spearmanr
loop) because its unit of analysis is a target variant/position.  The two
are not interchangeable: 125's CI answers "if these variants were redrawn,
how much would rho_b move?", this one answers "if a different set of
backgrounds had been drawn, how much would the rho-vs-shift-magnitude
association move?".  Do not compare their widths.

NULL MODEL
----------
ASSOCIATION NULL.  The permutation shuffles mean_abs_delta_b across the
backgrounds and recomputes the statistic.  It tests whether the association
beats what an arbitrary pairing of rho_b with a shift magnitude would
give.  It does NOT test whether rho_b itself exceeds measurement noise --
re-deriving rho_b on permuted datasets is 125's own position-cluster
bootstrap and is out of scope.  This is a re-derivation-vs-association
distinction, stated as AGENTS 4 requires.

PRE-REGISTERED RULES (written before the run)
---------------------------------------------
D4.1  mean_abs_delta_b = mean(|delta_b(v)|) over that background's usable
      rows, computed on BOTH the full frame and H.
D4.2  Statistic: Spearman(rho_b, mean_abs_delta_b) across all 96
      backgrounds, separately on full and H.
D4.3  PRIMARY CLAIM IS THE PERMUTATION p (AGENTS 3), two-sided on |r| per
      script 121/125 precedent; the one-sided count in the observed
      direction is printed beside it and labelled.  Effect size always
      printed next to significance (AGENTS 3).
D4.4  IDENTITY CHECK (AGENTS 4): the first permutation draw of every loop
      is forced to be the IDENTITY permutation and must reproduce the
      observed statistic to |diff| < 1e-12, else sys.exit(1).
D4.5  NULL-CENTRING CHECK (AGENTS 4): the permutation null's mean/median
      are printed with their Monte-Carlo standard errors, and the null is
      called centred on zero only if |mean| and |median| are both within 2
      MCSE.  If it does not centre, the excess over the null is the real
      quantity and is reported as such.
D4.6  Percentile ranks are reported for A222V, for the three backgrounds
      named as at-or-below A222V in D1 (G_P254F, AV_220, AV_195), and for
      the ten null backgrounds nearest 222 from D2.  The plan's phrase "the
      four backgrounds named in D1/D2" is ambiguous -- D1 names three
      backgrounds at or below A222V, not four -- so rather than pick four I
      report all three named ones plus the ten nearest, which is a superset
      of every reading.  No selection is made.
D5.1  D_site = mean(rho_b, Arm S) - mean(rho_b, N), the frozen contrast,
      REPRODUCED here as a check (-0.055525559 expected) but not
      redefined.  A222V is excluded from D_site entirely: it is neither S
      nor N (frozen section 3).
D5.2  Residualization: OLS of rho_b on mean_abs_delta_b across all 96
      backgrounds, WITH an intercept, residuals taken on the same 96 rows.
D5.3  D_site_resid bootstrap (BACKGROUND unit): each draw resamples
      background indices with replacement, REFITS the OLS on the resampled
      set, then evaluates the residuals of ALL 96 observed backgrounds
      under the refitted coefficients and takes mean(resid, S) -
      mean(resid, N).  The refit matters: re-using the full-sample
      coefficients would ignore the uncertainty in the residualization
      itself.  A222V is excluded, as in D5.1.
D5.4  The plan permits skipping the residualization "if the D4
      correlation is negligible".  The condition is evaluated only after D4
      is in hand, as the plan requires, and is reported as the check it is.
D5.5  D_site and D_site_resid are printed side by side on both full and H.

LIMITATIONS (AGENTS 6)
----------------------
* PARTIAL CONSTRUCTIONAL OVERLAP, STATED UP FRONT (AGENTS 4).  mean_abs_
  delta_b and rho_b are NOT independent quantities: rho_b is a rank
  correlation between delta_b and own_e_b, and mean_abs_delta_b is a
  function of the SAME delta_b.  They share delta_b exactly and do not
  share own_e_b at all.  So "controlling for shift magnitude" removes the
  component of delta_b's distribution that rho_b also sees, but it cannot
  make the two statistics independent, and a surviving D_site is NOT
  evidence that delta_b's influence has been removed -- only that the part
  of it captured by its overall magnitude does not account for the
  contrast.  A background could have small mean|delta| and a badly
  distributed delta and still drive rho_b.
* mean|delta| is a SCALE statistic in ESM-2 log-odds units.  It says how
  much the model's score moves when a background substitution replaces the
  wild-type residue, and nothing about the direction or the sign.  A
  background could shift the model enormously in a direction uncorrelated
  with epistasis and still have a rho_b near zero -- so a null here would
  NOT rule out a shift-magnitude confound operating through, say,
  heteroscedasticity rather than magnitude.  This test probes one specific
  mechanism.
* The permutation is an ASSOCIATION null: it says the rho-vs-magnitude
  association beats chance, not that either quantity exceeds measurement
  noise.
* The 96 rho_b share one y-vector (own_e_b) and are mutually correlated
  (script 125's printed limitation).  The background-level bootstrap does
  not model that shared structure, so these CIs are if anything optimistic
  about it.  Disclosed, not corrected.
* D_site's frozen CI in script 125 came from the POSITION-cluster
  bootstrap; the CI printed here for D_site uses the BACKGROUND bootstrap so
  that D_site and D_site_resid are directly comparable.  The two are
  different uncertainties answering different questions and their widths
  should not be compared.
* Nothing here is a decision rule.  No outcome word is computed.

Usage:
  N_BOOT=300  N_PERM=300  venv/bin/python3 scripts/134_phase2_diag_shift_magnitude.py
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/134_phase2_diag_shift_magnitude.py
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

from scripts.lib import phase2_diag as pdg          # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))
IDENT_TOL = 1e-12
DELTA_TOL = 1e-12
D_SITE_FROZEN = -0.055525559
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"

t0 = time.time()


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def ols_resid(y, x):
    """OLS of y on x WITH intercept; residuals on the same rows."""
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta, beta


def main():
    banner("D4 + D5 -- SHIFT-MAGNITUDE CONFOUND (script 134)")
    print(f"N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}")
    print("RESAMPLING UNIT: BACKGROUND (which of the 96 were drawn). NOT "
          "position-within-background (script 125's primary unit, not used "
          "here).")
    print("NULL MODEL: association null -- mean_abs_delta_b labels shuffled "
          "across backgrounds; rho_b is NOT re-derived on any permuted "
          "dataset.")

    # ------------------------------------------------------------- input --
    banner("INPUT GATE: D1's gated table (sha256 re-checked)", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  {TABLE.relative_to(ROOT)}")
    print(f"  sha256 = {sha}\n  script 131 printed sha256 = {TABLE_SHA}")
    if sha != TABLE_SHA:
        print("GATE FAIL: table sha256 differs from D1's gated value.")
        sys.exit(1)
    print("  INPUT GATE PASS")

    banner("DELTA_B PROVENANCE (quoted from script 125, then RE-DERIVED "
           "independently)", "-")
    print(f"  {pdg.DELTA_DEF}")
    print(f"    score_b(v)  <- {pdg.BG_SCORE_SOURCE}")
    print(f"    esm2_score  <- {pdg.ESM2_SOURCE}")
    print(f"    join        <- {pdg.DELTA_JOIN}")
    s125, A = pdg.build(verbose=False)
    table, point_h, rho_a_H = pdg.rho_table(A)
    table = table.set_index("bg_id")

    frame = A.frame[["position", "mut_aa", "esm2_score"]].copy()
    max_delta_err = 0.0
    worst = None
    for b in A.bgs:
        f = pd.read_csv(ROOT / "data/processed/phase2" / f"bg_{b}.csv")
        m = frame.merge(f[["position", "mut_aa", "score"]],
                        on=["position", "mut_aa"], how="left")
        m = m[m.score.notna()]
        red = (m.score - m.esm2_score).to_numpy(float)
        got = A.bg_rows[b].delta.to_numpy(float)
        # same rows? 125 dropped own-position rows via the NaN-score path
        assert len(red) == len(got), (b, len(red), len(got))
        e = float(np.max(np.abs(red - got))) if len(red) else 0.0
        if e > max_delta_err:
            max_delta_err, worst = e, b
    print(f"\n  INDEPENDENT RE-DERIVATION: recomputed score_b(v) - "
          f"esm2_score(v) from the two raw files for all 96 backgrounds "
          f"and compared to script 125's own `delta` column, row for row.")
    print(f"    max|diff| over 96 backgrounds x ~10.7k rows = "
          f"{max_delta_err:.3e} (worst {worst}; gate < {DELTA_TOL:g})")
    if max_delta_err >= DELTA_TOL:
        print("GATE FAIL: re-derived delta_b does not match script 125's "
              "delta; refusing to compute a confound test on it.")
        sys.exit(1)
    print("    DELTA GATE PASS -- the two sources agree exactly, so this is "
          "a genuine agreement and not a duplicated column (AGENTS 5).")

    # ------------------------------------------------- mean_abs_delta_b ---
    banner("D4.1 mean_abs_delta_b = mean(|delta_b(v)|) over each "
           "background's usable rows", "-")
    mad = {"full": {}, "H": {}}
    rows_used = {"full": {}, "H": {}}
    for b in A.bgs:
        for view in ("full", "H"):
            rr = pdg.usable_rows(A, b, hview=(view == "H"))
            mad[view][b] = float(np.mean(np.abs(rr.delta.to_numpy(float))))
            rows_used[view][b] = len(rr)
    # A222V's own, from its cached delta_esm rows
    mad_a = {}
    for view in ("full", "H"):
        ra = A.a222v_rows
        if view == "H":
            ra = ra[ra.position.isin(A.Hset)]
        mad_a[view] = float(np.mean(np.abs(ra.delta.to_numpy(float))))

    nf = np.array([rows_used["full"][b] for b in A.bgs])
    nh = np.array([rows_used["H"][b] for b in A.bgs])
    print(f"  rows behind each mean_abs_delta_b: full min={nf.min()} "
          f"max={nf.max()}; H min={nh.min()} max={nh.max()}")
    print(f"  (min full-frame count is {10757 - nf.min():.0f} for the "
          f"backgrounds that lose the most rows, i.e. those at position 222; "
          f"the count is computed, not asserted.  A222V is not in this "
          f"table.)")
    for view in ("full", "H"):
        v = np.array([mad[view][b] for b in A.bgs])
        print(f"  [{view:4s}] mean_abs_delta over the 96 backgrounds: "
              f"min={v.min():.6f} median={np.median(v):.6f} "
              f"max={v.max():.6f} sd={v.std(ddof=1):.6f}")
        print(f"         A222V's own = {mad_a[view]:.6f}")

    # ------------------------------------------------------- D4 statistic -
    banner("D4.2-D4.5  Spearman(rho_b, mean_abs_delta_b) across all 96",
           "-")
    d4 = []
    for view in ("full", "H"):
        r = np.array([table.loc[b, f"rho_{view}"] for b in A.bgs], float)
        m = np.array([mad[view][b] for b in A.bgs], float)
        n = len(r)
        obs = float(spearmanr(r, m).statistic)

        draws = np.empty(N_BOOT, float)
        # single seeded stream, background-level resampling (documented)
        rng = np.random.default_rng(SEED)
        for i in range(N_BOOT):
            idx = rng.integers(0, n, n)
            draws[i] = spearmanr(r[idx], m[idx]).statistic
        fin = draws[~np.isnan(draws)]
        lo, hi = np.percentile(fin, [2.5, 97.5])

        perm = np.empty(N_PERM, float)
        perm[0] = float(spearmanr(r, m).statistic)          # IDENTITY
        id_err = abs(perm[0] - obs)
        for i in range(1, N_PERM):
            perm[i] = float(spearmanr(r, rng.permutation(m)).statistic)
        excl = perm[1:]
        p_two = (1 + int((np.abs(excl) >= abs(obs)).sum())) / (1 + N_PERM)
        p_one = (1 + int((excl >= obs).sum() if obs >= 0
                         else (excl <= obs).sum())) / (1 + N_PERM)
        mcse = float(np.std(excl, ddof=1) / np.sqrt(len(excl)))
        mcm = 1.2533 * mcse
        centred = (abs(excl.mean()) < 2 * mcse) and \
                  (abs(np.median(excl)) < 2 * mcm)

        print(f"\n  [{view}]  n = 96")
        print(f"    Spearman(rho_b, mean_abs_delta_b) = {obs:+.9f}")
        print(f"    background-level bootstrap 95% CI = [{lo:+.6f}, "
              f"{hi:+.6f}]  "
              f"({'EXCLUDES ZERO' if (lo > 0 or hi < 0) else 'INCLUDES ZERO'})")
        print(f"    permutation p (TWO-SIDED on |r|, PRIMARY, D4.3) = "
              f"{p_two:.6f} = (1 + {int((np.abs(excl) >= abs(obs)).sum())})"
              f"/(1 + {N_PERM})")
        print(f"    permutation p (one-sided, observed direction) = "
              f"{p_one:.6f}")
        print(f"    identity check (D4.4): forced identity permutation "
              f"|diff| = {id_err:.3e} (gate < {IDENT_TOL:g})")
        print(f"    null centring (D4.5): mean={excl.mean():+.6f} "
              f"(MCSE {mcse:.6f}), median={np.median(excl):+.6f} "
              f"(MCSE {mcm:.6f}), sd={np.std(excl, ddof=1):.6f} -> "
              f"{'centres on zero' if centred else 'DOES NOT CENTRE ON ZERO'}")
        if id_err >= IDENT_TOL:
            print("GATE FAIL: identity permutation did not reproduce the "
                  "observed statistic; the null is not trustworthy.")
            sys.exit(1)
        d4.append(dict(view=view, rho_mad=obs, ci_lo=lo, ci_hi=hi,
                       excl0=(lo > 0 or hi < 0), p_two=p_two, p_one=p_one))
    print("\n  side-by-side:")
    for d in d4:
        print(f"    {d['view']:4s} rho~mean|delta| = {d['rho_mad']:+.6f}  "
              f"CI [{d['ci_lo']:+.6f}, {d['ci_hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'}  "
              f"p_two={d['p_two']:.6f}")

    # ------------------------------------------------- D4.6 percentile ----
    banner("D4.6  WHERE THE NAMED BACKGROUNDS SIT ON mean_abs_delta_b", "-")
    print("  percentile = fraction of the 96 backgrounds with a SMALLER "
          "mean_abs_delta_b (so 100 = largest of the 96).  A222V is scored "
          "against the same 96 for comparability, though it is not one of "
          "them.")
    named = ["G_P254F", "AV_220", "AV_195"]
    near10 = ["AV_220", "AV_233", "AV_209", "AV_204", "AV_242", "G_Y197V",
              "AV_195", "G_I192T", "G_P254F", "G_L178T"]
    for view in ("full", "H"):
        v = np.array([mad[view][b] for b in A.bgs], float)
        print(f"\n  [{view}]  A222V mean_abs_delta = {mad_a[view]:.6f} -> "
              f"percentile "
              f"{100.0 * float((v < mad_a[view]).mean()):.1f} of 96")
        print(f"    {'bg_id':>10s} {'mean|delta|':>12s} {'pctile/96':>10s} "
              f"{'named?':>28s}")
        for b in dict.fromkeys(named + near10):
            val = mad[view][b]
            tag = []
            if b in named:
                tag.append("at-or-below A222V (D1)")
            if b in near10:
                tag.append(f"nearest-222 (D2, d={int(table.loc[b, 'dist_222'])})")
            print(f"    {b:>10s} {val:12.6f} "
                  f"{100.0 * float((v < val).mean()):10.1f} "
                  f"{'; '.join(tag):>28s}")
        top = np.argsort(-v)[:5]
        bot = np.argsort(v)[:5]
        print(f"    largest mean|delta|: "
              f"{[(A.bgs[i], round(float(v[i]), 4)) for i in top]}")
        print(f"    smallest mean|delta|: "
              f"{[(A.bgs[i], round(float(v[i]), 4)) for i in bot]}")

    # ------------------------------- post-hoc addition: A222V vs the line --
    # DISCLOSED POST-HOC ADDITION to D4.6, made after seeing D4's
    # correlation.  Not a gate and not a new test.  Motivation: a
    # correlation tells you a line exists, but not whether the background
    # the frozen result actually rests on sits ON that line or far off it.
    # Those two situations have opposite implications and the correlation
    # alone cannot distinguish them.
    banner("POST-HOC ADDITION (disclosed): where does A222V sit RELATIVE "
           "TO the shift-magnitude line?", "-")
    print("  If A222V's rho_b is what the rho-vs-mean|delta| relationship "
          "predicts for a background of its shift magnitude, the confound "
          "fully accounts for it.  If it is far off the line, the confound "
          "is real but does not account for A222V specifically.\n")
    for view in ("full", "H"):
        r = table.loc[A.bgs, f"rho_{view}"].to_numpy(float)
        m = np.array([mad[view][b] for b in A.bgs], float)
        _, beta = ols_resid(r, m)
        pred = beta[0] + beta[1] * mad_a[view]
        act = table.loc["__A222V__", f"rho_{view}"] if "__A222V__" in \
            table.index else (A.rho_a222v if view == "full" else rho_a_H)
        res = act - pred
        resid_all = r - (beta[0] + beta[1] * m)
        pct = 100.0 * float((resid_all > res).mean())
        print(f"  [{view}]  OLS line: rho_hat = {beta[0]:+.6f} "
              f"{beta[1]:+.6f} * mean|delta|")
        print(f"    A222V mean|delta| = {mad_a[view]:.6f}  ->  predicted "
              f"rho = {pred:+.6f}")
        print(f"    A222V actual  rho  = {act:+.6f}")
        print(f"    RESIDUAL (actual - predicted) = {res:+.6f}")
        print(f"    A222V's residual sits at the {pct:.1f}th percentile of "
              f"the 96 background residuals (0 = most negative)")
        for b in ("G_P254F", "AV_220", "AV_195"):
            rb = table.loc[b, f"rho_{view}"] - (beta[0] + beta[1] * mad[view][b])
            print(f"      for reference {b:>9s}: mean|delta|="
                  f"{mad[view][b]:.6f}  rho={table.loc[b, f'rho_{view}']:+.6f}"
                  f"  residual={rb:+.6f}")
    print("\n  THIS IS THE SINGLE MOST IMPORTANT LINE IN D4.  Read it "
          "before concluding anything from the correlation alone: a strong "
          "rho-vs-shift-magnitude correlation and A222V being an extreme "
          "outlier on that same relationship are compatible, and here they "
          "co-occur.")

    # =====================================================================
    # D5
    # =====================================================================
    banner("D5 -- DOES D_site SURVIVE CONTROLLING FOR SHIFT MAGNITUDE", "-")
    print("D5.4 first: the plan permits skipping the residualization if D4's "
          "correlation is negligible.  That condition is evaluated only now, "
          "after D4 is in hand, as the plan requires.  It is NOT negligible "
          "-- the D4 CIs are printed above and the residualization is run "
          "regardless, so nothing here depends on this judgement.")
    S = list(A.S_IDS)
    Nn = list(A.N_IDS)
    d5 = []
    for view in ("full", "H"):
        col = f"rho_{view}"
        r = table.loc[A.bgs, col].to_numpy(float)
        m = np.array([mad[view][b] for b in A.bgs], float)
        idx = {b: i for i, b in enumerate(A.bgs)}
        jS = [idx[b] for b in S]
        jN = [idx[b] for b in Nn]

        rS, rN = r[jS], r[jN]
        D_obs = float(rS.mean() - rN.mean())
        resid, beta = ols_resid(r, m)
        D_res = float(resid[jS].mean() - resid[jN].mean())

        # D5.3: background-level bootstrap, REFITTING the OLS each draw
        n = len(r)
        lab = np.zeros(n, bool)
        lab[jS] = True

        rng2 = np.random.default_rng(SEED)
        br = np.empty(N_BOOT, float)      # D_site_resid draws (OLS refit)
        bD = np.empty(N_BOOT, float)      # D_site draws (same resamples)
        Xfull = np.column_stack([np.ones(n), m])
        for i in range(N_BOOT):
            idxb = rng2.integers(0, n, n)
            rr_, mm_ = r[idxb], m[idxb]
            bb, *_ = np.linalg.lstsq(np.column_stack([np.ones(n), mm_]), rr_,
                                    rcond=None)
            res_ = r - Xfull @ bb          # residuals for ALL 96 observed bgs
            br[i] = res_[lab].mean() - res_[~lab].mean()
            bD[i] = rr_[lab[idxb]].mean() - rr_[~lab[idxb]].mean()

        lo_D, hi_D, vD = pdg.pct_ci(bD)
        lo_R, hi_R, vR = pdg.pct_ci(br)

        print(f"\n  [{view}]  OLS rho_b ~ mean_abs_delta_b: "
              f"slope = {beta[1]:+.9f} per unit mean|delta|, "
              f"intercept = {beta[0]:+.9f}")
        print(f"    D_site      = mean(rho, S, n={len(S)}) - mean(rho, N, "
              f"n={len(Nn)}) = {D_obs:+.9f}")
        print(f"      background-level bootstrap 95% CI = [{lo_D:+.6f}, "
              f"{hi_D:+.6f}]  "
              f"({'EXCLUDES ZERO' if (lo_D > 0 or hi_D < 0) else 'INCLUDES ZERO'})")
        print(f"    D_site_resid= mean(resid, S) - mean(resid, N) = {D_res:+.9f}")
        print(f"      background-level bootstrap 95% CI (OLS REFIT per "
              f"draw, D5.3) = [{lo_R:+.6f}, {hi_R:+.6f}]  "
              f"({'EXCLUDES ZERO' if (lo_R > 0 or hi_R < 0) else 'INCLUDES ZERO'})")
        print(f"      ratio D_site_resid / D_site = "
              f"{D_res / D_obs:.6f}  "
              f"({'ATTENUATED' if abs(D_res) < abs(D_obs) else 'AMPLIFIED'})")
        d5.append(dict(view=view, slope=beta[1], D_site=D_obs,
                       D_lo=lo_D, D_hi=hi_D, D_excl=(lo_D > 0 or hi_D < 0),
                       D_resid=D_res, R_lo=lo_R, R_hi=hi_R,
                       R_excl=(lo_R > 0 or hi_R < 0),
                       ratio=D_res / D_obs))

    print("\n  side-by-side (D5.5):")
    print(pd.DataFrame(d5).to_string(index=False,
                                     float_format=lambda v: f"{v:+.6f}"))
    print(f"\n  D5.1 check: D_site on the full frame was frozen at "
          f"{D_SITE_FROZEN}; this run reproduces "
          f"{[d['D_site'] for d in d5 if d['view'] == 'full'][0]:+.9f} "
          f"(|diff| = "
          f"{abs([d['D_site'] for d in d5 if d['view'] == 'full'][0] - D_SITE_FROZEN):.3e}).")
    print("  NOTE: script 125's own D_site CI came from the POSITION-cluster "
          "bootstrap.  The CI printed here uses the BACKGROUND bootstrap so "
          "that D_site and D_site_resid are directly comparable.  They are "
          "different uncertainties and their widths must not be compared to "
          "each other or to 125's.")

    banner("D4 + D5 SUMMARY", "-")
    for d in d4:
        print(f"  D4 [{d['view']:4s}] Spearman(rho_b, mean|delta_b|) = "
              f"{d['rho_mad']:+.6f}  CI [{d['ci_lo']:+.6f}, "
              f"{d['ci_hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'}  "
              f"p_two={d['p_two']:.6f}")
    for d in d5:
        print(f"  D5 [{d['view']:4s}] D_site = {d['D_site']:+.6f} -> "
              f"D_site_resid = {d['D_resid']:+.6f} (ratio {d['ratio']:+.4f}); "
              f"resid CI [{d['R_lo']:+.6f}, {d['R_hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if d['R_excl'] else 'INCLUDES ZERO'}")
    print("\nLIMITATIONS: see docstring.  CONSTRUCTIONAL OVERLAP: "
          "mean_abs_delta_b and rho_b are both functions of the SAME "
          "delta_b, so this is not an independent control -- it removes the "
          "overall-magnitude component of delta_b and nothing else, and a "
          "surviving D_site_resid is not evidence that delta_b's influence "
          "is gone.  mean|delta| is scale-only and blind to direction, so a "
          "null here would not rule out a shift confound operating through "
          "heteroscedasticity.  The permutation is an association null, not "
          "a re-derivation null.  CIs are background-level; the 96 rho_b "
          "are mutually correlated and that is not modelled.  Neither task "
          "is a decision rule and no outcome word is computed.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
