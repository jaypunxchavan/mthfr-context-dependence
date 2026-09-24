"""
DEPRECATED (2026-09-22, I1-mechanism-followup task N1a) -- DO NOT USE THE
epistatic_N* FLAGS PRODUCED HERE. Kept intact as a documented, informative
dead end; the log entries explaining WHY it failed have value, so nothing
below is deleted or changed.

WHY IT IS DEAD (numbers from data/processed/task59_j4a_fdr.csv,
task59_j4b_ratios.csv and the J4a/J4b entries in
docs/tasks/review-triage/OVERNIGHT_LOG.md; readership audited in task N1b):

* J4a (scripts/59_j4_fdr_threshold.py), verdict NO-SUSTAINED-C-IN-GRID:
  with the synonymous empirical null, FDR_hat = 0.91-1.00 at EVERY z
  cutoff from 2 to 10 even after inflating the analytic SEs by the
  empirical synonymous factor 3.76. At the flat 3.76 fix, FDR = 0.9312
  (synonymous 116/570 pass vs missense 2,351/10,757 pass). No multiplier
  of this SE calibrates the flag.
* J4b, verdict NEEDS-TO-VARY: the 3.76 correction factor is itself not
  constant -- sd(syn e_b)/median(syn SE) = 5.16/2.54/4.04/2.59 for
  regions 1-4 (max/min = 2.03, above the pre-registered 2x gate), so a
  single global inflation under-corrects region 1 and over-corrects
  region 2. Fitness terciles were stable (3.44-3.55; low tercile
  underpowered, n_syn=11).
* This script's own raw behavior already says enough: at N=2 the flag
  marks 44.7% of SYNONYMOUS variants "epistatic" (255/570) -- essentially
  the same fraction as missense (44.8%, 4,822/10,757). Synonymous
  variants encode an identical protein and cannot interact.

REPLACEMENT (task N2): a nonparametric stratifier that ranks |e_b|
against the synonymous |e_b| ECDF directly, bypassing the miscalibrated
per-condition SEs entirely -- scripts/64_n2_nonparametric_epistatic_set.py,
output data/processed/task_N2_nonparametric_epistatic_set.csv (distinct
file from the retired task35_epistatic_set.csv).

-- original docstring below, unchanged --

Script 35: define the epistatic set by MEASUREMENT ERROR, not by quantile.

THE PROBLEM WITH THE CURRENT STRATIFIER
---------------------------------------
Every stratified result in this project splits |e.b| into terciles with
pd.qcut. The bucket count was never justified, and a tercile boundary is a
property of the sample, not of the biology: it guarantees that exactly a
third of variants are called "high interaction" whether or not a single one
of them exceeds measurement noise.

Kolchina et al. (2026) use the alternative: call a genotype epistatic only
when the deviation from the no-interaction expectation exceeds a multiple of
its own propagated experimental error. This repo already has everything
needed for that -- the per-condition se columns feed the WLS fit -- but the
resulting uncertainty on e_b has never been computed.

SE(e_b) IS ANALYTIC HERE, NOT BOOTSTRAPPED
------------------------------------------
e_b is the intercept of a weighted least-squares line with KNOWN per-point
error, which is exactly what fitModels.R fits. For that model the coefficient
covariance is (X'WX)^-1 in closed form, so SE(e_b) = sqrt(S2/det). No
resampling, no new distributional assumption beyond the one the atlas
already makes. See scripts/lib/stats_ext.py:wls_line_se.

THE CHECK THAT ACTUALLY MATTERS
-------------------------------
Kolchina's own validation is to show epistatic genotypes do not simply have
larger experimental error. That check is WEAK when transplanted here,
because a threshold of the form |e_b| > N*SE mechanically favours variants
with small SE -- it would look reassuring by construction. So it is reported,
with that caveat stated, and the load is carried instead by this project's
own assumption-free control: synonymous variants encode an identical protein
and cannot interact, so the fraction of them passing the threshold is a
direct empirical false-positive rate. Nonsense variants are reported
alongside as a second reference point.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.own_context import MT_SE_COLS, CONCS
from scripts.lib.stats_ext import rebuild_interaction_fit, wls_line_se
from scripts.lib.regions import assign_region, REGION_BOUNDS

N_LEVELS = [1.0, 2.0, 3.0]
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


if __name__ == "__main__":
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse, valid = fit["e2"], fit["M_se"], fit["valid"]

    se_b, se_r = wls_line_se(Mse, CONCS, valid)
    eb, er = e2["e_b"], e2["e_r"]

    tab = pd.DataFrame({
        "hgvs_pro": raw["hgvs"], "type": raw["type"], "position": raw["start"],
        "own_e_b": eb, "se_e_b": se_b, "own_e_r": er, "se_e_r": se_r,
        "mean_m_se": np.nanmean(Mse, axis=1),
        "n_valid": valid.sum(axis=1),
    })
    tab["z_e_b"] = tab["own_e_b"] / tab["se_e_b"]
    tab["region"] = assign_region(tab["position"])
    ok = tab["se_e_b"].notna() & tab["own_e_b"].notna()
    print(f"{len(tab)} rows; SE(e_b) computable for {ok.sum()}")

    print("\n" + "=" * 74)
    print("SANITY: is the analytic SE the right order of magnitude?")
    print("=" * 74)
    syn = tab[(tab["type"] == "synonymous") & ok]
    print(f"  median SE(e_b) over all variants : {tab.loc[ok,'se_e_b'].median():.4f}")
    print(f"  observed sd of synonymous e_b    : {syn['own_e_b'].std():.4f}")
    print(f"  median SE(e_b) among synonymous  : {syn['se_e_b'].median():.4f}")
    print("  Synonymous variants cannot interact, so their e_b spread IS noise.")
    print("  If the analytic SE and that spread disagree badly, the reported")
    print("  per-condition se are mis-scaled and every z below inherits it.")
    ratio = syn["own_e_b"].std() / syn["se_e_b"].median() if len(syn) else np.nan
    print(f"  ratio (empirical sd / analytic SE) = {ratio:.3f}   "
          f"[1.0 = perfectly calibrated]")

    rows = [{"stage": "sanity", "quantity": "syn_sd_over_analytic_se", "value": float(ratio)}]

    print("\n" + "=" * 74)
    print("EPISTATIC SET BY |e_b| > N * SE(e_b)   (Kolchina et al. criterion)")
    print("=" * 74)
    print(f"  {'N':>4}  {'missense':>18}  {'synonymous (FPR)':>20}  {'nonsense':>16}")
    for N in N_LEVELS:
        tab[f"epistatic_N{int(N)}"] = tab["z_e_b"].abs() > N
        line = [f"  {N:>4.0f}"]
        rec = {"stage": "threshold", "N": N}
        for t, lbl in [("substitution", "missense"), ("synonymous", "synonymous"),
                       ("nonsense", "nonsense")]:
            sub = tab[(tab["type"] == t) & ok]
            frac = sub[f"epistatic_N{int(N)}"].mean() if len(sub) else np.nan
            n_pass = int(sub[f"epistatic_N{int(N)}"].sum()) if len(sub) else 0
            line.append(f"  {n_pass:>6}/{len(sub):<5} ({100*frac:4.1f}%)")
            rec[f"{lbl}_n_pass"] = n_pass
            rec[f"{lbl}_n"] = len(sub)
            rec[f"{lbl}_frac"] = float(frac)
        print("".join(line))
        rows.append(rec)
    print("\n  The synonymous column IS the empirical false-positive rate: those")
    print("  variants encode an identical protein and cannot have real epistasis.")
    print("  Choose N by the FPR you are willing to carry, not by convention.")

    print("\n" + "=" * 74)
    print("KOLCHINA'S OWN CHECK (reported, but see the caveat)")
    print("=" * 74)
    mis = tab[(tab["type"] == "substitution") & ok]
    for N in N_LEVELS:
        e = mis[mis[f"epistatic_N{int(N)}"]]
        ne = mis[~mis[f"epistatic_N{int(N)}"]]
        if len(e) == 0 or len(ne) == 0:
            continue
        print(f"  N={N:.0f}  mean per-condition se: epistatic={e['mean_m_se'].mean():.4f}  "
              f"non-epistatic={ne['mean_m_se'].mean():.4f}  "
              f"ratio={e['mean_m_se'].mean()/ne['mean_m_se'].mean():.3f}")
        rows.append({"stage": "kolchina_check", "N": N,
                     "se_epistatic": float(e["mean_m_se"].mean()),
                     "se_non_epistatic": float(ne["mean_m_se"].mean())})
    print("  CAVEAT: this ratio is < 1 partly BY CONSTRUCTION -- thresholding on")
    print("  |e_b|/SE selects low-SE variants. It is not independent evidence the")
    print("  way it is in Kolchina et al., where the threshold is applied to a")
    print("  differently-constructed statistic. The synonymous FPR above is the")
    print("  check that carries real weight here.")

    print("\n" + "=" * 74)
    print("HOW MUCH DOES THIS CHANGE THE STRATIFIER? (vs pd.qcut terciles)")
    print("=" * 74)
    m = mis.dropna(subset=["own_e_b"]).copy()
    m["tercile_high"] = m["own_e_b"].abs() >= m["own_e_b"].abs().quantile(2 / 3)
    for N in N_LEVELS:
        col = f"epistatic_N{int(N)}"
        both = int((m[col] & m["tercile_high"]).sum())
        only_se = int((m[col] & ~m["tercile_high"]).sum())
        only_q = int((~m[col] & m["tercile_high"]).sum())
        print(f"  N={N:.0f}  in both={both:5d}   SE-only={only_se:5d}   "
              f"tercile-only={only_q:5d}")
        rows.append({"stage": "overlap", "N": N, "both": both,
                     "se_only": only_se, "tercile_only": only_q})
    print("  Large 'tercile-only' counts mean the old high stratum was mostly")
    print("  variants whose interaction never exceeded its own measurement error.")

    print("\n" + "=" * 74)
    print("EPISTATIC FRACTION BY REGION (missense, N=2)")
    print("=" * 74)
    for rg in sorted(REGION_BOUNDS):
        sub = mis[mis["region"] == rg]
        if len(sub) == 0:
            continue
        lo, hi = REGION_BOUNDS[rg]
        print(f"  region {rg} ({lo}-{hi}) n={len(sub):5d}  "
              f"epistatic={100*sub['epistatic_N2'].mean():5.1f}%  "
              f"median SE(e_b)={sub['se_e_b'].median():.4f}")
        rows.append({"stage": "region", "N": 2.0, "region": rg, "n": len(sub),
                     "frac_epistatic": float(sub["epistatic_N2"].mean()),
                     "median_se": float(sub["se_e_b"].median())})

    tab.to_csv(PROC / "task35_epistatic_set.csv", index=False)
    pd.DataFrame(rows).to_csv(PROC / "task35_summary.csv", index=False)
    print(f"\nSaved per-variant flags to {PROC / 'task35_epistatic_set.csv'}")
    print("Downstream scripts should stratify on epistatic_N2 (or the N chosen")
    print("from the synonymous FPR above) instead of pd.qcut terciles.")
