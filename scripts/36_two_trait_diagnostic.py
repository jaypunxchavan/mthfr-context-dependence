"""
Script 36: is a SECOND latent trait behind the region-4 anomaly?

THE HYPOTHESIS, AND WHERE IT COMES FROM
---------------------------------------
Carlson, Andrews & Simons (PNAS 2025) show that fitting a single-latent-trait
global-epistasis model to a system that actually has TWO latent traits
produces SPURIOUS specific epistasis, and that the spurious signal tracks the
omitted trait. Their demonstration is GB1: binding is governed by folding
energy AND binding energy, a one-trait fit mis-orders mutations, and a
mutation's rank residual correlates with its independently measured folding
energy (R^2 = 0.26). They reproduce the whole pattern in simulation with no
real specific epistasis present at all.

MTHFR has exactly that architecture in real life: a catalytic domain and a
regulatory AdoMet-binding domain that allosterically modulates it. The
atlas's interaction model fits ONE global correction curve, correction(w.fitness),
and this repo reimplements it faithfully in own_context.py. If two traits are
operating, that single curve is misspecified -- and two of this project's
longest-standing puzzles are exactly what that misspecification would produce:

  1. region 4 (475-656, most of the regulatory domain) does not overlap the
     pooled estimate in EITHER error metric, and crosses zero in one
  2. own_e_b vs published e.b agree best at the 0/1 fitness extremes and
     worst mid-range -- where a degree-4 polynomial fit to a running median
     has the most freedom and the least anchoring

WHAT THIS SCRIPT IS, AND IS NOT
-------------------------------
This is the CHEAP diagnostic that decides whether a full two-trait refit
(MoCHI, bidimensional global epistasis) is worth the effort. It is a weaker
analogue of Carlson's test: they average each mutation's rank across MANY
backgrounds, and MTHFR has exactly one alternate background (A222V). With a
single background the rank residual is noisier and cannot be averaged, so
this detects only a strong effect. A null result here is not evidence of
absence.

THE TEST STATISTIC
------------------
    rank_resid(v) = rank(f_bar_a222v) - rank(f_bar_wt)

Under single-trait monotone global epistasis with no specific epistasis, a
monotone g preserves order across backgrounds, so rank_resid is mean-zero
noise. Systematic structure in rank_resid across DOMAIN or REGION is the
signature Carlson attributes to an omitted second latent trait.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.io import load_structural_features
from scripts.lib.features import add_structural_features
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import position_cluster_bootstrap, _spearman
from scripts.lib.stats_ext import group_mean_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = add_structural_features(df, load_structural_features())
    df = df.dropna(subset=["f_bar_wt", "f_bar_a222v"]).reset_index(drop=True)
    df["region"] = assign_region(df["position"])

    # rank residual, on a common 0-1 scale so it is comparable across subsets
    n = len(df)
    df["rank_resid"] = (df["f_bar_a222v"].rank() - df["f_bar_wt"].rank()) / n
    # the own-vs-published disagreement, the second puzzle
    df["eb_disagreement"] = (df["own_e_b"] - df["GI_folinate_independent"]).abs()
    df["fit_mid"] = 1.0 - (df["f_bar_wt"].clip(0, 1) - 0.5).abs() * 2  # 1 = mid-range
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")
    print(f"Domains present: {df['domain'].value_counts(dropna=False).to_dict()}")

    rows = []

    print("\n" + "=" * 74)
    print("36a  RANK RESIDUAL BY DOMAIN  (Carlson's omitted-trait signature)")
    print("=" * 74)
    print("  Under one monotone latent trait, every domain's mean should sit on")
    print("  zero. A domain that does not is the signature of a second trait.")
    for dom, sub in df.groupby("domain"):
        if sub["position"].nunique() < 10:
            print(f"  {str(dom):14s} SKIPPED ({sub['position'].nunique()} positions)")
            continue
        r = group_mean_bootstrap(sub, "position", "rank_resid",
                                 n_boot=N_BOOT, seed=SEED)
        off = not (r["ci_lo"] < 0 < r["ci_hi"])
        print(f"  {str(dom):14s} n={r['n_rows']:5d}  mean={r['mean']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}]"
              f"{'  <-- excludes zero' if off else ''}")
        rows.append({"stage": "domain_rank_resid", "group": str(dom),
                     "mean": r["mean"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
                     "n": r["n_rows"], "excludes_zero": off})

    print("\n" + "=" * 74)
    print("36b  RANK RESIDUAL BY MUTAGENESIS REGION")
    print("=" * 74)
    for rg in sorted(REGION_BOUNDS):
        sub = df[df["region"] == rg]
        if sub["position"].nunique() < 10:
            continue
        r = group_mean_bootstrap(sub, "position", "rank_resid",
                                 n_boot=N_BOOT, seed=SEED)
        lo, hi = REGION_BOUNDS[rg]
        off = not (r["ci_lo"] < 0 < r["ci_hi"])
        print(f"  region {rg} ({lo}-{hi}) n={r['n_rows']:5d}  mean={r['mean']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}]"
              f"{'  <-- excludes zero' if off else ''}")
        rows.append({"stage": "region_rank_resid", "group": f"region_{rg}",
                     "mean": r["mean"], "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
                     "n": r["n_rows"], "excludes_zero": off})
    print("  Region 4 is ~the regulatory domain and is the region that already")
    print("  fails to overlap the pooled estimate in the error-based analyses.")

    print("\n" + "=" * 74)
    print("36c  DOES THE own_e_b / published e.b DISAGREEMENT TRACK STRUCTURE?")
    print("=" * 74)
    print("  Puzzle 2: agreement is best at the 0/1 fitness extremes and worst")
    print("  mid-range. A single global correction curve misfitting a two-trait")
    print("  system predicts exactly that, AND predicts the misfit concentrates")
    print("  in one domain. Both are testable; neither has been tested before.")
    r = position_cluster_bootstrap(df, "position", "fit_mid", "eb_disagreement",
                                   n_boot=N_BOOT, seed=SEED)
    print(f"  disagreement vs mid-range-ness: rho={r['observed_rho']:+.4f} "
          f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] n={r['n_rows']}")
    rows.append({"stage": "disagreement_midrange", "group": "fit_mid",
                 "mean": r["observed_rho"], "ci_lo": r["ci_lo"],
                 "ci_hi": r["ci_hi"], "n": r["n_rows"]})
    for dom, sub in df.groupby("domain"):
        if sub["position"].nunique() < 10:
            continue
        rr = group_mean_bootstrap(sub, "position", "eb_disagreement",
                                  n_boot=N_BOOT, seed=SEED)
        print(f"    mean |own_e_b - published e.b| in {str(dom):14s} "
              f"= {rr['mean']:.5f} CI=[{rr['ci_lo']:.5f},{rr['ci_hi']:.5f}]")
        rows.append({"stage": "disagreement_domain", "group": str(dom),
                     "mean": rr["mean"], "ci_lo": rr["ci_lo"],
                     "ci_hi": rr["ci_hi"], "n": rr["n_rows"]})

    print("\n" + "=" * 74)
    print("36d  DOES THE RANK RESIDUAL TRACK THE INTERACTION STATISTIC?")
    print("=" * 74)
    print("  If rank_resid and e_b measure the same thing they should correlate.")
    print("  Where they DIVERGE is where the one-trait model is doing work that")
    print("  the rank-based view does not support.")
    r = position_cluster_bootstrap(df.dropna(subset=["own_e_b"]), "position",
                                   "rank_resid", "own_e_b", n_boot=N_BOOT, seed=SEED)
    print(f"  rank_resid vs own_e_b: rho={r['observed_rho']:+.4f} "
          f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] n={r['n_rows']}")
    rows.append({"stage": "rank_resid_vs_eb", "group": "pooled",
                 "mean": r["observed_rho"], "ci_lo": r["ci_lo"],
                 "ci_hi": r["ci_hi"], "n": r["n_rows"]})
    for rg in sorted(REGION_BOUNDS):
        sub = df[(df["region"] == rg)].dropna(subset=["own_e_b"])
        if sub["position"].nunique() < 15:
            continue
        rr = position_cluster_bootstrap(sub, "position", "rank_resid", "own_e_b",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"    region {rg}: rho={rr['observed_rho']:+.4f} "
              f"CI=[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}]")
        rows.append({"stage": "rank_resid_vs_eb", "group": f"region_{rg}",
                     "mean": rr["observed_rho"], "ci_lo": rr["ci_lo"],
                     "ci_hi": rr["ci_hi"], "n": rr["n_rows"]})

    out = PROC / "task36_two_trait_diagnostic.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    df.to_csv(PROC / "task36_analysis_table.csv", index=False)
    print(f"\nSaved to {out}")
    print("\nDECISION RULE, fixed in advance:")
    print("  If 36a or 36b shows a domain/region mean excluding zero, a two-trait")
    print("  refit (MoCHI, bidimensional global epistasis) is justified and the")
    print("  region-4 anomaly has a named candidate mechanism.")
    print("  If everything centres on zero, the anomaly is NOT explained by an")
    print("  omitted latent trait and that hypothesis should be dropped rather")
    print("  than pursued into an expensive refit.")
    print("\nPOWER CAVEAT: one alternate background only. Carlson average ranks")
    print("over many backgrounds; this cannot. A null here is weak evidence of")
    print("absence, and Carlson also report that both their method and MoCHI are")
    print("underpowered for negative epistasis among deleterious mutations --")
    print("which is most of MTHFR.")
