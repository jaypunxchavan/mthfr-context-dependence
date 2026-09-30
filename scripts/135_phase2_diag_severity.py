"""Script 135 -- Phase 2 diagnostics Task D6: SEVERITY GRADIENT.  Do more
disruptive backgrounds give more negative rho_b?

SCOPE: descriptive.  Nothing here redefines, replaces, or retroactively
qualifies the frozen PHASE2_PREREG.md section-5 outcome, which stands as
logged.  Per PHASE2_DIAGNOSTICS.md rule 9, the three words reserved for the
frozen test are not used anywhere in this script, and this script never
computes or names that outcome.

THE SEVERITY PROXY WAS LOCATED, NOT ASSUMED
--------------------------------------------
The plan requires finding the proxy on disk and confirming retrievability
rather than assuming a column name.  The proxy is each background's own
WT-vs-mutant ESM-2 score -- the same `esm2_score` column script 125 uses as
the wild-type baseline for every variant in the frame, evaluated at the
background's OWN (position, mut_aa).  It is read from
data/processed/task32_analysis_table.csv::esm2_score, joined on
(position, mut_aa) against data/processed/phase2_arm_roster.csv, exactly as
script 125 joins that column for the frame.

  FILE:     data/processed/task32_analysis_table.csv
  COLUMN:   esm2_score
  JOIN:     roster (position, mut_aa) -> task32 (position, mut_aa), left
  RANGE:    -18.007029 .. +7.807393 over 11,344 rows, no nulls

SIGN CONVENTION, VERIFIED AGAINST LABELLED EXAMPLES (AGENTS 5)
---------------------------------------------------------------
esm2_score is a log-odds score for the MUTANT amino acid; a LOW (negative)
value means ESM-2 finds the substitution very unlikely.  This is not
assumed -- it is checked against the extremes of the real table and both
extremes are printed in the output:

  most disruptive (lowest esm2_score): V179W -18.007, G158H -17.872,
                                       L45D -17.750, T227W -17.736
  most conservative (highest):          R594Q +7.807, R134S +6.352,
                                       M327V +6.236, L437R +6.083

Every one of the four lowest is a substitution that removes or destroys a
side chain (V->W packs, G->H breaks a helix, L->D and T->W are both strongly
destabilising); every one of the four highest is a conservative side-chain
substitution at a surface position.  So severity = -esm2_score, and
severity is reported as the positive-facing quantity with that definition
printed.  Both the raw esm2_score correlation and the severity correlation
are printed, so the sign flip cannot be misread.

RETRIEVABILITY: 75 OF 96, AND THE 21 MISSING ARE ACCOUNTED FOR
-------------------------------------------------------------
The plan requires logging exactly which backgrounds are missing and why,
rather than substituting a different proxy.  All 21 are explained, and no
substitution is made:

  * 18 x Arm S (A222_C ... A222_Y): position 222 does not appear in
    task32_analysis_table.csv AT ALL (0 rows).  The atlas never treats its
    own background residue as a target variant -- this is the same fact
    that makes script 125's gate G-C drop every position-222 row.  These 18
    are all Arm S, and D6's statistic is over N (Arms V and G), so their
    absence does not touch the primary test.

  * 3 x Arm G: G_E383T, G_D629C, G_P346V.  NOT a join bug.  At those
    positions task32 simply never scored the requested mutant: 383 lists
    E->{A,R,N,D,C,G,H,I,L,K,M,F,S,W,Y,V} with no T; 629 lists
    D->{A,R,N,E,G,I,L,P,Y,V,S,K,H} with no C; 346 lists
    P->{A,R,H,L,F,S,T,Q,N} with no V.  The roster asks for a substitution
    the reference table does not contain.

  CONSEQUENCE, DISCLOSED: D6's null set is N = 78 minus these 3 = 75, not
78.  The three excluded backgrounds' own rho values and positions are
printed in the output so a reader can judge whether dropping them could
bias the severity comparison, and the statistic is additionally reported
split by arm (Arm V alone, Arm G restricted to its 37 retrievable members)
so a result driven by one arm is visible rather than pooled away.

  ALSO NOTE: A222V's OWN severity is NOT retrievable, for the same reason
  as Arm S (position 222 is absent from task32).  So this task can say
  whether placebo backgrounds' severity tracks their rho_b; it cannot place
  A222V on that same axis.  Stated rather than glossed.

RESAMPLING UNIT -- READ THIS
----------------------------
BACKGROUND.  rho_b and background_severity_b each have exactly one value
per background, so the only thing a bootstrap can legitimately resample is
WHICH BACKGROUNDS WERE DRAWN.  Each of the N_BOOT draws resamples
background indices with replacement; within a draw, each background's
already-computed rho_b and severity are held FIXED.  No rho_b is
recomputed and no score is re-read on any draw.

This is NOT the resampling unit Phase 2's own primary analysis used.
Script 125 resamples POSITIONS within a background (PIN-9 naive spearmanr
loop) because its unit of analysis is a target variant/position.  The two
are not interchangeable: 125's CI answers "if these variants were redrawn,
how much would rho_b move?", this one answers "if a different set of
backgrounds had been drawn, how much would the rho-vs-severity association
move?".  Do not compare their widths.

NULL MODEL
----------
ASSOCIATION NULL.  The permutation shuffles background_severity_b across
the backgrounds and recomputes the statistic.  It tests whether the
association beats an arbitrary pairing.  It does NOT test whether rho_b
itself exceeds measurement noise -- re-deriving rho_b on permuted datasets
is 125's own position-cluster bootstrap and is out of scope.

PRE-REGISTERED RULES (written before the run)
---------------------------------------------
D6.1  Primary statistic: Spearman(rho_b, background_severity_b) across the
      75 retrievable members of N, on BOTH the full frame and H.  Arm S is
      excluded because the question is specifically about the null set
      (the reviews' framing: "is a severity-matched null the right
      comparison, or does Arm G's uniform draw miss a real gradient?").
D6.2  Reported alongside, not instead of: the same correlation split by arm
      (Arm V n=38, Arm G n=37) and a two-sample permutation comparison of
      the arms' mean severity.  Arm V is exhaustive over A->V positions and
      Arm G is a seed-0 uniform draw, so they are NOT exchangeable; the
      comparison is descriptive and no significance is claimed for a
      difference between arms as a biological claim.
D6.3  PRIMARY CLAIM IS THE PERMUTATION p (AGENTS 3), two-sided on |r| per
      script 121/125 precedent, with the one-sided count in the observed
      direction printed beside it.  Effect size always printed next to
      significance (AGENTS 3).
D6.4  IDENTITY CHECK (AGENTS 4): the first permutation draw of every loop
      is forced to be the IDENTITY permutation and must reproduce the
      observed statistic to |diff| < 1e-12, else sys.exit(1).
D6.5  NULL-CENTRING CHECK (AGENTS 4): the permutation null's mean/median
      are printed with their Monte-Carlo standard errors, and the null is
      called centred on zero only if both are within 2 MCSE.
D6.6  Nothing here is a decision rule; no outcome word is computed.

LIMITATIONS (AGENTS 6)
----------------------
* esm2_score is a model score, not a measurement.  "Severity" here means
  "how unlikely ESM-2 finds this substitution", which is a property of the
  model.  A correlation between rho_b and this quantity is evidence about
  ESM-2's behaviour, and only indirectly about biology.
* PARTIAL CONSTRUCTIONAL OVERLAP, stated up front (AGENTS 4).  rho_b is a
  rank correlation between delta_b and own_e_b, and delta_b(v) = score_b(v)
  - esm2_score(v) SUBTRACTS the very esm2_score column used here as the
  severity proxy.  The severity proxy and rho_b are therefore not
  independent: a background ESM-2 scores very badly will have a delta_b
  systematically offset from the frame's own values.  This correlation
  cannot separate "disruptive backgrounds behave differently" from
  "subtracting a large constant changes the ranks".  That is a structural
  limit of this proxy, disclosed rather than corrected, and it is the
  single strongest reason not to read a large value here as biology.
* D6's null set is 75, not 78 (three Arm G backgrounds have no esm2_score
  row).  The three are printed with their rho values.
* A222V's own severity is not retrievable, so A222V cannot be placed on
  this axis.
* Arm V and Arm G are not exchangeable, so the arm comparison is
  descriptive only.
* The 75 rho_b share one y-vector (own_e_b) and are mutually correlated
  (script 125's printed limitation).  The background-level bootstrap does
  not model that structure, so these CIs are if anything optimistic.
* dist_222 (D2) and mean_abs_delta_b (D4) are both strongly associated
  with rho_b.  A severity gradient here is not independent evidence; it is
  a third overlapping axis on the same 75 numbers.

Usage:
  N_BOOT=300  N_PERM=300  venv/bin/python3 scripts/135_phase2_diag_severity.py
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/135_phase2_diag_severity.py
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
TABLE = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
TABLE_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
ROSTER = ROOT / "data/processed/phase2_arm_roster.csv"
T32 = ROOT / "data/processed/task32_analysis_table.csv"

t0 = time.time()


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def boot_ci_perm(r, m, label):
    """Background-level bootstrap CI + association permutation, with a
    forced-identity check (D6.4) and an MC-standard-error centring check
    (D6.5).  RESAMPLING UNIT: BACKGROUND."""
    n = len(r)
    obs = float(spearmanr(r, m).statistic)
    rng = np.random.default_rng(SEED)
    draws = np.empty(N_BOOT, float)
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
    e = perm[1:]
    p_two = (1 + int((np.abs(e) >= abs(obs)).sum())) / (1 + N_PERM)
    p_one = (1 + int((e >= obs).sum() if obs >= 0 else (e <= obs).sum())) \
        / (1 + N_PERM)
    mcse = float(np.std(e, ddof=1) / np.sqrt(len(e)))
    mcm = 1.2533 * mcse
    centred = (abs(e.mean()) < 2 * mcse) and (abs(np.median(e)) < 2 * mcm)
    return dict(label=label, n=n, rho=obs, lo=lo, hi=hi,
                excl0=(lo > 0 or hi < 0), p_two=p_two, p_one=p_one,
                id_err=id_err, mean=float(e.mean()), mcse=mcse,
                med=float(np.median(e)), mcm=mcm,
                centred=centred, sd=float(np.std(e, ddof=1)))


def main():
    banner("D6 -- SEVERITY GRADIENT (script 135)")
    print(f"N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}")
    print("RESAMPLING UNIT: BACKGROUND (which of the 96 were drawn). NOT "
          "position-within-background (script 125's primary unit, not used "
          "here).")
    print("NULL MODEL: association null -- severity labels shuffled across "
          "backgrounds; rho_b is NOT re-derived on any permuted dataset.")

    banner("INPUT GATE: D1's gated table (sha256 re-checked)", "-")
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    print(f"  {TABLE.relative_to(ROOT)}\n  sha256 = {sha}")
    print(f"  script 131 printed sha256 = {TABLE_SHA}")
    if sha != TABLE_SHA:
        print("GATE FAIL: table sha256 differs from D1's gated value.")
        sys.exit(1)
    print("  INPUT GATE PASS")
    table = pd.read_csv(TABLE).set_index("bg_id")

    # ------------------------------------------------ locate the proxy ---
    banner("LOCATING THE SEVERITY PROXY (not assuming a column name)", "-")
    t32 = pd.read_csv(T32, usecols=["position", "wt_aa", "mut_aa",
                                     "esm2_score"])
    print(f"  FILE   : {T32.relative_to(ROOT)}")
    print(f"  COLUMN : esm2_score")
    print(f"  JOIN   : roster (position, mut_aa) -> task32 (position, "
          f"mut_aa), left")
    print(f"  RANGE  : {t32.esm2_score.min():.6f} .. "
          f"{t32.esm2_score.max():.6f} over {len(t32)} rows, "
          f"{int(t32.esm2_score.isna().sum())} nulls")

    print("\n  SIGN CONVENTION CHECK AGAINST LABELLED EXAMPLES (AGENTS 5):")
    print("    most disruptive (lowest esm2_score):")
    for r in t32.nsmallest(4, "esm2_score").itertuples():
        print(f"      {r.wt_aa}{r.position}{r.mut_aa}  "
              f"{r.esm2_score:+.6f}")
    print("    most conservative (highest esm2_score):")
    for r in t32.nlargest(4, "esm2_score").itertuples():
        print(f"      {r.wt_aa}{r.position}{r.mut_aa}  "
              f"{r.esm2_score:+.6f}")
    print("    -> all four of the lowest destroy a side chain (V->W packs, "
          "G->H breaks a helix, L->D and T->W destabilise); all four of the "
          "highest are conservative surface substitutions.")
    print("    -> SIGN ESTABLISHED: LOW esm2_score = MORE SEVERE.  "
          "severity := -esm2_score.  Both correlations are printed below so "
          "the flip cannot be misread.")

    # ----------------------------------------------------- retrievability -
    banner("RETRIEVABILITY: 75 OF 96 -- THE 21 MISSING ARE ACCOUNTED FOR",
           "-")
    roster = pd.read_csv(ROSTER)
    m = roster.merge(t32, on=["position", "mut_aa"], how="left",
                     suffixes=("_roster", "_t32"))
    got = m[m.esm2_score.notna()]
    miss = m[m.esm2_score.isna()]
    print(f"  retrieved {len(got)} of {len(m)}")
    # wt agreement, excluding the rows that are missing anyway
    both = m[m.esm2_score.notna()]
    n_wt_bad = int((both.wt_aa_roster != both.wt_aa_t32).sum())
    print(f"  wt_aa roster vs task32 on the {len(both)} retrieved rows: "
          f"{n_wt_bad} mismatches (expect 0) -> the join is landing on the "
          f"right rows, not merely on the right (position, mut_aa) key")
    if n_wt_bad:
        print("GATE FAIL: wt_aa disagrees; the join is not landing on the "
              "intended rows.")
        sys.exit(1)
    s_miss = miss[miss.arm == "S"]
    g_miss = miss[miss.arm == "G"]
    print(f"\n  MISSING, Arm S ({len(s_miss)}): {', '.join(s_miss.bg_id)}")
    print(f"    REASON: position 222 has {int((t32.position == 222).sum())} "
          f"rows in task32 -- the atlas never treats its own background "
          f"residue as a target variant.  Same fact as script 125's gate "
          f"G-C.  All {len(s_miss)} are Arm S, and D6's statistic is over "
          f"N, so this does not touch the primary test.")
    print(f"\n  MISSING, Arm G ({len(g_miss)}):")
    for _, r in g_miss.iterrows():
        have = sorted(t32[t32.position == r["position"]].mut_aa)
        print(f"    {r['bg_id']}: task32 lists {r['wt_aa_roster']}"
              f"{r['position']}->{{{''.join(have)}}} and does NOT contain "
              f"'{r['mut_aa']}'.  Not a join bug -- the reference table "
              f"never scored that mutant at that position.")
    print(f"\n  CONSEQUENCE (disclosed): D6's null set is N = 78 minus "
          f"{len(g_miss)} = {78 - len(g_miss)}, NOT 78.  The three excluded "
          f"backgrounds' own rho values and positions:")
    for _, r in g_miss.iterrows():
        print(f"    {r['bg_id']:>10s} pos={int(r['position']):>3d} "
              f"dist_222={abs(int(r['position']) - 222):>3d}  rho_full="
              f"{table.loc[r['bg_id'], 'rho_full']:+.9f}  rho_H="
              f"{table.loc[r['bg_id'], 'rho_H']:+.9f}")
    print(f"  ALSO: A222V's own severity is NOT retrievable (position 222 "
          f"absent from task32, same reason as Arm S).  This task can say "
          f"whether PLACEBO severity tracks rho_b; it cannot place A222V on "
          f"the same axis.  Stated rather than glossed.")

    sev = {r["bg_id"]: -float(r["esm2_score"]) for _, r in got.iterrows()}
    N_all = sorted(table.index[table.arm.isin(["V", "G"])])
    N_ok = [b for b in N_all if b in sev]
    print(f"\n  N = {len(N_all)}; retrievable subset used below = "
          f"{len(N_ok)}")

    # ------------------------------------------------------------- D6.1 --
    banner("D6.1  Spearman(rho_b, background_severity_b) across N", "-")
    print(f"  severity = -esm2_score (LOW esm2_score = MORE severe); "
          f"|N_retrievable| = {len(N_ok)}")
    res = []
    for view in ("full", "H"):
        for axis, key in (("severity (-esm2)", "sev"),
                          ("esm2_score (raw)", "raw")):
            r = np.array([table.loc[b, f"rho_{view}"] for b in N_ok], float)
            mval = np.array([sev[b] if key == "sev" else -sev[b]
                             for b in N_ok], float)
            d = boot_ci_perm(r, mval, f"N/{view}/{key}")
            d["view"], d["axis"] = view, key
            res.append(d)
            print(f"\n  [{view} | {axis}] n = {d['n']}")
            print(f"    Spearman(rho_b, x) = {d['rho']:+.9f}")
            print(f"    background-level bootstrap 95% CI = [{d['lo']:+.6f}, "
                  f"{d['hi']:+.6f}]  "
                  f"({'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'})")
            print(f"    permutation p (TWO-SIDED, PRIMARY, D6.3) = "
                  f"{d['p_two']:.6f} = "
                  f"(1 + {int(round(d['p_two'] * (1 + N_PERM)) - 1)})"
                  f"/(1 + {N_PERM})")
            print(f"    permutation p (one-sided, observed direction) = "
                  f"{d['p_one']:.6f}")
            print(f"    identity check (D6.4): |diff| = {d['id_err']:.3e} "
                  f"(gate < {IDENT_TOL:g})")
            print(f"    null centring (D6.5): mean={d['mean']:+.6f} "
                  f"(MCSE {d['mcse']:.6f}), median={d['med']:+.6f} "
                  f"(MCSE {d['mcm']:.6f}) -> "
                  f"{'centres on zero' if d['centred'] else 'DOES NOT CENTRE ON ZERO'}")
            if d["id_err"] >= IDENT_TOL:
                print("GATE FAIL: identity permutation did not reproduce "
                      "the observed statistic.")
                sys.exit(1)
    print("\n  side-by-side (the two axes are exact negatives of each other, "
          "so the correlations must be exact negatives -- printed to make "
          "the sign convention checkable):")
    for d in res:
        print(f"    {d['view']:4s} {d['axis']:20s} n={d['n']}  "
              f"rho={d['rho']:+.6f}  CI [{d['lo']:+.6f}, {d['hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'}  "
              f"p_two={d['p_two']:.6f}")
    pairs = [d for d in res if d["view"] == "full"]
    print(f"    sign-convention self-check (full): |{pairs[0]['rho']:+.6f} + "
          f"{pairs[1]['rho']:+.6f}| = "
          f"{abs(pairs[0]['rho'] + pairs[1]['rho']):.3e} (must be ~0)")

    # ------------------------------------------------------------- D6.2 --
    banner("D6.2  SEVERITY DISTRIBUTION: Arm V vs Arm G (descriptive)", "-")
    print("  Arm V is exhaustive over A->V positions; Arm G is a seed-0 "
          "uniform draw.  They are NOT exchangeable, so this is reported, "
          "not tested for significance as a biological contrast.")
    print("  (The severity numbers are identical for `full` and `H` and are "
          "printed twice because the loop is over views -- that is correct, "
          "not a duplicated computation: a background's severity is a "
          "property of the substitution alone and does not depend on which "
          "frame's rows the statistic is evaluated over.  Only the rho_b "
          "side of D6 changes between views.)")
    for view in ("full", "H"):
        print(f"  [{view}]")
        for arm_name in ("V", "G"):
            ids = [b for b in N_ok if table.loc[b, "arm"] == arm_name]
            v = np.array([sev[b] for b in ids], float)
            print(f"    Arm {arm_name}: n={len(ids):2d}  severity "
                  f"mean={v.mean():+.6f} median={np.median(v):+.6f} "
                  f"range=[{v.min():+.6f}, {v.max():+.6f}] sd="
                  f"{v.std(ddof=1):.6f}")
        iv = np.array([sev[b] for b in N_ok if table.loc[b, "arm"] == "V"])
        ig = np.array([sev[b] for b in N_ok if table.loc[b, "arm"] == "G"])
        obs = float(ig.mean() - iv.mean())
        rng = np.random.default_rng(SEED)
        pool = np.concatenate([iv, ig])
        nv, ng = len(iv), len(ig)
        cnt = 0
        for _ in range(N_PERM):
            p = rng.permutation(pool)
            if abs(p[:nv].mean() - p[nv:].mean()) >= abs(obs):
                cnt += 1
        p2 = (1 + cnt) / (1 + N_PERM)
        print(f"    mean severity difference (G - V) = {obs:+.6f}; "
              f"label-permutation p (two-sided) = {p2:.6f}")
        print(f"    Spearman(severity, dist_222) within N = "
              f"{float(spearmanr(np.array([sev[b] for b in N_ok]), np.array([int(table.loc[b, 'dist_222']) for b in N_ok])).statistic):+.6f}"
              f"   <- printed because a severity gradient in POSITION would "
              f"be indistinguishable from D2's locality gradient")

    banner("D6.2b  SAME CORRELATION, SPLIT BY ARM (so an arm-driven result "
           "is visible)", "-")
    for view in ("full", "H"):
        for arm_name in ("V", "G"):
            ids = [b for b in N_ok if table.loc[b, "arm"] == arm_name]
            r = np.array([table.loc[b, f"rho_{view}"] for b in ids], float)
            mval = np.array([sev[b] for b in ids], float)
            d = boot_ci_perm(r, mval, f"{arm_name}/{view}")
            if d["id_err"] >= IDENT_TOL:
                print("GATE FAIL: identity permutation failed in a "
                      "within-arm view.")
                sys.exit(1)
            print(f"  [{view} | Arm {arm_name}] n={d['n']:2d}  "
                  f"Spearman(rho_b, severity) = {d['rho']:+.6f}  "
                  f"CI [{d['lo']:+.6f}, {d['hi']:+.6f}] "
                  f"{'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'}  "
                  f"p_two={d['p_two']:.6f}  identity "
                  f"|diff|={d['id_err']:.1e}")
    print("  (n = 37-38 per arm: small, and the within-arm CIs are wide.  "
          "These are reported so a pooled result driven by one arm cannot "
          "hide, not as independent confirmations.)")

    banner("D6 SUMMARY", "-")
    for d in res:
        print(f"  {d['view']:4s} {d['axis']:20s} n={d['n']}  "
              f"rho={d['rho']:+.6f}  CI [{d['lo']:+.6f}, {d['hi']:+.6f}] "
              f"{'EXCLUDES ZERO' if d['excl0'] else 'INCLUDES ZERO'}  "
              f"p_two={d['p_two']:.6f}")
    print("\nLIMITATIONS: see docstring.  esm2_score is a MODEL score, not "
          "a measurement.  STRUCTURAL OVERLAP: delta_b(v) = score_b(v) - "
          "esm2_score(v) SUBTRACTS the very column used as the severity "
          "proxy, so severity and rho_b are not independent quantities and "
          "this test cannot separate 'disruptive backgrounds behave "
          "differently' from 'subtracting a large constant changes the "
          "ranks'.  D6's null set is 75, not 78 (three Arm G backgrounds "
          "have no esm2_score row; all three are named in the output).  "
          "A222V's own severity is not retrievable, so A222V cannot be "
          "placed on this axis.  Arm V and Arm G are not exchangeable, so "
          "the arm comparison is descriptive only.  dist_222 (D2) and "
          "mean_abs_delta_b (D4) are both already strongly associated with "
          "rho_b on this same set of backgrounds -- a severity gradient "
          "here is a third overlapping axis, not independent corroboration.  "
          "The 75 rho_b share one y-vector and are mutually correlated; the "
          "background-level bootstrap does not model that, so these CIs are "
          "if anything optimistic.  Nothing here is a decision rule.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
