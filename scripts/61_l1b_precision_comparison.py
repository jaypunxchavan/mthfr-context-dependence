"""
Script 61 (I1 follow-up, task L1b): compare the GB1 comparator's per-variant
measurement precision against MTHFR's own SE distribution.

WHY (I1_MECHANISM_FOLLOWUP L1b)
-------------------------------
I1 (script 49) failed its gate on GB1. The task: "If the comparator is
noisier than MTHFR itself, a gate failure there says little about the
MTHFR pipeline specifically." GB1 reports NO per-variant SE and NO
replicate count anywhere (file has only sequence+fitness; paper has no
error column) -- "whatever it reports" is:
  * cross-study fitness correlation vs Olson et al. 2014: R = 0.97
    (Wu et al. 2016, Figure 1--figure supplement 3B; Methods line:
    "fitness ... highly consistent with our previous study ... R = 0.97")
  * system detection limit w ~ 0.01 (Wu et al. 2016 Methods, citing
    Olson et al. 2014) and the paper's own three epsilon-adjustment
    rules that exist BECAUSE precision collapses near that limit
  * count_input >= 10 read filter: 149,361/160,000 measured (93.4%);
    10,639 rows in our file are lasso-IMPUTED (no measurement at all)

PRECISION BRIDGE (derived here, assumptions stated -- rule: log them)
---------------------------------------------------------------------
The paper gives a correlation, not an SE, so an SE must be derived.
Classical test theory on the cross-study pair (X = this study,
Y = Olson 2014, both measuring shared truth T, equal error variance):
    R = var(T)/var(X)  =>  sigma_e = sigma_X * sqrt(1 - R)
Primary sigma_X = sd of the distributed file's fitness (population as
distributed). Two disclosed sensitivities: (S1) treat Olson 2014 as
error-free instead: sigma_e = sigma_X * sqrt(1 - R^2); (S2) robust
sigma_X = IQR/1.349 (the file is zero-inflated and right-skewed, so a
global sd is outlier-inflated -- this sensitivity matters and its
disagreement with the primary is reported, not hidden).
Epistasis-level SE: I1's e is a 4-fitness double-mutant cycle, so under
independent errors SE(e_GB1) = 2 * sigma_e (sqrt(4)). This is the
quantity like-for-like comparable to MTHFR's SE(e_b).

DIRECTIONS OF BIAS (printed, AGENTS section 6)
-----------------------------------------------
* R=0.97 is CROSS-STUDY (protocol/lab differences included), so the
  derived sigma_e likely OVERSTATES this study's own error -> biases
  toward the "comparator noisier" verdict.
* A global sd is inflated by fitness outliers up to 9.91 -> same
  direction; the robust sensitivity shows how far the verdict moves.
* The equality of units is approximate: GB1 fitness = sort-based
  enrichment ratio, MTHFR = folate-response growth-model score. Both
  are linear relative-fitness units; comparability is approximate.
* MTHFR's se_e_b is ANALYTIC (WLS intercept SE, script 35 docstring),
  mean_m_se is the mean per-condition measurement SE -- different
  construction from a cross-study-derived SE; reported side by side.

I1-SAMPLE POPULATION CHECK (the part that matters most)
-------------------------------------------------------
Precision is fitness-dependent in GB1 (detection limit 0.01). So the
script also rebuilds I1's EXACT design (seed 0, sites 39/40/41,
K=10 backgrounds -- mirror of script 49's design block, no ESM needed)
and counts how many of the fitness lookups that build I1's e values sit
at/below 0.01 / 0.02 / 0.05. Cycles built from near-detection-limit
fitnesses are the regime where "R = 0.97" does not describe precision.

PRE-REGISTERED DECISION RULE (fixed before running)
---------------------------------------------------
"Comparator noisier than MTHFR" fires IFF the PRIMARY implied
epistasis-level precision, SE(e_GB1) = 2 * sigma_X * sqrt(1 - R) with
sigma_X = full-file sd, is GREATER than MTHFR's median se_e_b from
task35_epistatic_set.csv. Sensitivities S1/S2 and the per-variant-level
comparison (vs median mean_m_se) are printed; if a sensitivity
disagrees, the disagreement is printed explicitly and the verdict is
downgraded to NOISIER-BUT-SENSITIVE (both readings stated). No rule is
changed after seeing the numbers.

Output: data/processed/task61_l1b_precision.csv
No bootstrap/resampling is required by the task (it asks for the
reported SE/precision), so N_BOOT/N_PERM do not apply here.

DISCLOSURE (pre-verdict execution note, AGENTS 7/6): the first execution
of this script exited 1 at its own lookup-count gate because the EXPECTED
constant in that gate was miscounted here (+3 double-counting the b0
fitnesses, which are already among the 11 f(WT,b) terms; correct
expectation 3*11*39 = 1287, verified by hand against script 49's loop
structure). The gate fired BEFORE any comparison or verdict statistic was
computed; only the constant and its message were corrected, no statistic
or rule was touched, and the script was rerun in full.
"""
import sys, hashlib, itertools, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GB1 = ROOT / "data" / "external" / "GB1_fitness_landscape.txt"
MTHFR_SE = ROOT / "data" / "processed" / "task35_epistatic_set.csv"
PROC = ROOT / "data" / "processed"

R_CROSSSTUDY = 0.97          # Wu 2016 Fig 1--figsupp3B (vs Olson 2014)
DETECTION_LIMIT = 0.01       # Wu 2016 Methods (Olson 2014)
FOCAL_SITES = (39, 40, 41)   # I1's sites (site 54 held at WT, script 49)
WT_COLS = ("V", "D", "G")
COL4_WT = "V"
SEED = 0
K_BG = 10

GB1_SEQ = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def main():
    # ---------------- GB1 side ----------------
    md5 = hashlib.md5(GB1.read_bytes()).hexdigest()
    raw = pd.read_csv(GB1, sep="\t")
    fit = raw.set_index("sequence")["fitness"]
    n = len(fit)
    sigma_full = float(fit.std(ddof=1))
    q1, q3 = np.percentile(fit, [25, 75])
    sigma_robust = float((q3 - q1) / 1.349)
    print("=== GB1 comparator: what it reports (Wu et al. 2016) ===")
    print(f"file={GB1.name} md5={md5} n={n} unique={fit.index.nunique()}")
    print(f"reported per-variant precision: cross-study R = {R_CROSSSTUDY} "
          f"(Fig 1--figsupp3B vs Olson 2014); NO SE column, NO replicate "
          f"count anywhere; detection limit w ~ {DETECTION_LIMIT}; "
          f"measured 149,361 (93.4%), imputed 10,639")
    print(f"fitness distribution: mean={fit.mean():.6f} sd={sigma_full:.6f} "
          f"median={fit.median():.6f} IQR=[{q1:.6f},{q3:.6f}] "
          f"zeros={int((fit == 0).sum())} max={fit.max():.4f}")

    se_per_variant = sigma_full * np.sqrt(1 - R_CROSSSTUDY)
    se_per_variant_s1 = sigma_full * np.sqrt(1 - R_CROSSSTUDY ** 2)
    se_per_variant_s2 = sigma_robust * np.sqrt(1 - R_CROSSSTUDY)
    se_cycle = 2 * se_per_variant
    se_cycle_s1 = 2 * se_per_variant_s1
    se_cycle_s2 = 2 * se_per_variant_s2
    print("\n=== derived GB1 precision (bridge assumptions in docstring) ===")
    print(f"primary : sigma_e(per genotype) = sd*sqrt(1-R)      = "
          f"{sigma_full:.6f}*sqrt({1-R_CROSSSTUDY:.2f}) = {se_per_variant:.6f}")
    print(f"          SE(e) for a 4-fitness cycle = 2*sigma_e    = "
          f"{se_cycle:.6f}")
    print(f"S1 error-free external (sd*sqrt(1-R^2)): per-genotype = "
          f"{se_per_variant_s1:.6f}  cycle = {se_cycle_s1:.6f}")
    print(f"S2 robust sigma (IQR/1.349={sigma_robust:.6f}): per-genotype = "
          f"{se_per_variant_s2:.6f}  cycle = {se_cycle_s2:.6f}")

    # ---------------- MTHFR side ----------------
    m = pd.read_csv(MTHFR_SE)
    ok = m["se_e_b"].notna()
    syn = ok & (m["type"] == "synonymous")
    print("\n=== MTHFR SE distribution (data/processed/task35_epistatic_set.csv) ===")
    print(f"rows={len(m)}  se_e_b valid n={int(ok.sum())}  "
          f"synonymous n={int(syn.sum())}")
    print(f"se_e_b   : median={m.loc[ok,'se_e_b'].median():.6f} "
          f"mean={m.loc[ok,'se_e_b'].mean():.6f} "
          f"IQR=[{m.loc[ok,'se_e_b'].quantile(.25):.6f},"
          f"{m.loc[ok,'se_e_b'].quantile(.75):.6f}] "
          f"(analytic WLS SE of e_b, script 35)")
    print(f"se_e_b among synonymous: median="
          f"{m.loc[syn,'se_e_b'].median():.6f}")
    mm = m["mean_m_se"].dropna()
    print(f"mean_m_se: median={mm.median():.6f} mean={mm.mean():.6f} "
          f"IQR=[{mm.quantile(.25):.6f},{mm.quantile(.75):.6f}] "
          f"(mean per-condition measurement SE)")

    med_se_eb = float(m.loc[ok, "se_e_b"].median())
    med_mse = float(mm.median())

    # ---------------- I1-sample population: precision where I1 looked ----------------
    rng = np.random.default_rng(SEED)
    AA = list("ACDEFGHIKLMNPQRSTVWY")
    sub = raw[raw["sequence"].str[3] == COL4_WT]
    if len(sub) != 8000:
        fail(f"I1 sub-landscape expected 8,000 rows, got {len(sub)}")
    sfit = sub.set_index("sequence")["fitness"]

    def gt_key(letters):
        return "".join(letters) + COL4_WT

    lookups = []
    for focal in FOCAL_SITES:
        idx = FOCAL_SITES.index(focal)
        others = [j for j in range(3) if j != idx]
        wt_conf = tuple(WT_COLS[j] for j in others)
        all_conf = list(itertools.product(AA, repeat=2))
        alt_conf = [c for c in all_conf if c != wt_conf]
        chosen = [alt_conf[int(i)] for i in
                  rng.choice(len(alt_conf), size=K_BG, replace=False)]
        for conf in [wt_conf] + chosen:
            letters = list(WT_COLS)
            letters[others[0]], letters[others[1]] = conf
            bg_fit = float(sfit[gt_key(letters)])          # f(WT, b)
            if conf == wt_conf:
                if abs(bg_fit - 1.0) > 1e-9:
                    fail("b0 fitness != 1.0")
            for v in AA:                                   # f(v, b), f(v, b0)
                if v == WT_COLS[idx]:
                    continue
                with_v = letters.copy()
                with_v[idx] = v
                f_vb = float(sfit[gt_key(with_v)])
                b0 = list(WT_COLS)
                b0[idx] = v
                f_vb0 = float(sfit[gt_key(b0)])
                lookups.extend([f_vb, f_vb0])
            lookups.append(bg_fit)                         # f(WT, b)
    lookups = np.asarray(lookups)
    print("\n=== precision in the population I1 actually sampled "
          "(rebuild of script 49's design, seed 0, no ESM) ===")
    print(f"fitness lookups building I1's e values: n={len(lookups)} "
          f"(expected 3 sites * 11 backgrounds * (1 f(WT,b) + 19 f(v,b) + "
          f"19 f(v,b0)) = {3 * 11 * 39}; b0 fitness 1.0 is one of the 11 "
          f"f(WT,b) terms, not extra)")
    if len(lookups) != 3 * 11 * 39:
        fail(f"lookup count {len(lookups)} != {3 * 11 * 39}")
    for thr in (DETECTION_LIMIT, 0.02, 0.05, 0.10):
        frac = float((lookups < thr).mean())
        print(f"  fraction < {thr:.2f}: {frac:.4f}  "
              f"({int((lookups < thr).sum())}/{len(lookups)})")
    print(f"  median lookup fitness = {np.median(lookups):.6f} "
          f"(detection limit {DETECTION_LIMIT})")
    # relative-error implication at the detection limit (order-of-magnitude
    # illustration, not a measured SE): a value reported at 0.01 sits AT the
    # limit where the paper itself forbids trusting unsigned epistasis.
    low = lookups[lookups < 0.02]
    print(f"  lookups within 2x of the detection limit: {len(low)} "
          f"({len(low)/len(lookups):.4f}) -> these dominate cycles like the "
          f"paper's own Fig 3D inputs (0.01, 0.02)")

    # ---------------- comparison + pre-registered verdict ----------------
    ratio_primary = se_cycle / med_se_eb
    ratio_s1 = se_cycle_s1 / med_se_eb
    ratio_s2 = se_cycle_s2 / med_se_eb
    noisier_primary = bool(se_cycle > med_se_eb)
    noisier_s1 = bool(se_cycle_s1 > med_se_eb)
    noisier_s2 = bool(se_cycle_s2 > med_se_eb)
    agree = (noisier_primary == noisier_s1 == noisier_s2)
    print("\n=== comparison (epistasis level: GB1 cycle SE vs MTHFR se_e_b) ===")
    print(f"primary : GB1 SE(e)={se_cycle:.6f} vs MTHFR median se_e_b="
          f"{med_se_eb:.6f}  ratio={ratio_primary:.3f}  "
          f"-> {'NOISIER' if noisier_primary else 'NOT noisier'}")
    print(f"S1      : cycle={se_cycle_s1:.6f}  ratio={ratio_s1:.3f}  "
          f"-> {'NOISIER' if noisier_s1 else 'NOT noisier'}")
    print(f"S2      : cycle={se_cycle_s2:.6f}  ratio={ratio_s2:.3f}  "
          f"-> {'NOISIER' if noisier_s2 else 'NOT noisier'}")
    print("=== per-variant level (GB1 per-genotype sigma_e vs MTHFR "
          "mean_m_se) ===")
    print(f"primary : {se_per_variant:.6f} vs median mean_m_se={med_mse:.6f} "
          f"ratio={se_per_variant/med_mse:.3f}")
    print(f"S1      : {se_per_variant_s1:.6f}  ratio="
          f"{se_per_variant_s1/med_mse:.3f}")
    print(f"S2      : {se_per_variant_s2:.6f}  ratio="
          f"{se_per_variant_s2/med_mse:.3f}")

    if noisier_primary and agree:
        verdict = ("NOISIER: at the epistasis level GB1's implied SE exceeds "
                   "MTHFR's median SE(e_b) under primary AND both "
                   "sensitivities -> per L1b, a gate failure there says "
                   "little about the MTHFR pipeline specifically")
    elif noisier_primary and not agree:
        verdict = ("NOISIER-BUT-SENSITIVE: primary rule fires NOISIER, but at "
                   "least one precision-bridge sensitivity disagrees -> both "
                   "readings stand; the verdict must not be quoted without "
                   "the sensitivity (see printed ratios)")
    else:
        verdict = ("NOT NOISIER: GB1's implied epistasis-level SE does not "
                   "exceed MTHFR's median SE(e_b) under the primary rule -> "
                   "a gate failure there is not attributable to comparator "
                   "noise alone")
    print(f"\nL1b VERDICT (pre-registered rule): {verdict}")
    print("\nLIMITATIONS (printed by the script, AGENTS 6):")
    print("  - sigma_e is DERIVED from a cross-study R (the paper reports no")
    print("    SE); equal-error-variance assumption; cross-lab differences")
    print("    inflate it -> biases toward NOISIER.")
    print("  - global sd is outlier-inflated (fitness up to 9.91) -> same")
    print("    direction; S2 (robust) shows the verdict's sensitivity.")
    print("  - GB1 fitness (sort-based ratio) vs MTHFR score units:")
    print("    approximate comparability only; constructions differ")
    print("    (cross-study-derived vs analytic WLS SE).")
    print("  - 10,639/160,000 rows are imputed (model, not measurement) and")
    print("    the file does not flag which; precision statements apply to")
    print("    the measured bulk as the paper reports it.")
    print("  - GB1 precision is heteroscedastic: the I1-sample counts above")
    print("    show how much of I1's design sits at the detection limit,")
    print("    where R=0.97 does not describe precision.")

    out = pd.DataFrame([
        {"quantity": "gb1_R_crossstudy", "value": R_CROSSSTUDY},
        {"quantity": "gb1_sd_fitness_full", "value": sigma_full},
        {"quantity": "gb1_sd_fitness_robust", "value": sigma_robust},
        {"quantity": "gb1_sigma_e_primary", "value": se_per_variant},
        {"quantity": "gb1_sigma_e_s1", "value": se_per_variant_s1},
        {"quantity": "gb1_sigma_e_s2", "value": se_per_variant_s2},
        {"quantity": "gb1_se_cycle_primary", "value": se_cycle},
        {"quantity": "gb1_se_cycle_s1", "value": se_cycle_s1},
        {"quantity": "gb1_se_cycle_s2", "value": se_cycle_s2},
        {"quantity": "mthfr_se_eb_median", "value": med_se_eb},
        {"quantity": "mthfr_mean_m_se_median", "value": med_mse},
        {"quantity": "ratio_cycle_over_se_eb_primary", "value": ratio_primary},
        {"quantity": "ratio_cycle_over_se_eb_s1", "value": ratio_s1},
        {"quantity": "ratio_cycle_over_se_eb_s2", "value": ratio_s2},
        {"quantity": "n_lookups_i1_design", "value": len(lookups)},
        {"quantity": "frac_lookups_below_0.01",
         "value": float((lookups < 0.01).mean())},
        {"quantity": "frac_lookups_below_0.05",
         "value": float((lookups < 0.05).mean())},
        {"quantity": "median_lookup_fitness", "value": float(np.median(lookups))},
        {"quantity": "verdict_noisier_primary", "value": int(noisier_primary)},
        {"quantity": "sensitivities_agree", "value": int(agree)},
    ])
    out.to_csv(PROC / "task61_l1b_precision.csv", index=False)
    print(f"\nSaved to {PROC / 'task61_l1b_precision.csv'}")


if __name__ == "__main__":
    main()
