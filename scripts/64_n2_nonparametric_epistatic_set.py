"""
Script 64 (I1 follow-up, tasks N2a-N2c): NONPARAMETRIC replacement for
script 35's retired SE-threshold epistatic flag.

WHY (the problem this solves)
-----------------------------
Script 35 called a variant epistatic when |e_b| > N * SE(e_b). That flag
is retired (DEPRECATED header, task N1a): J4a showed no cutoff controls
FDR (0.91-1.00 at every N=2..10, FDR=0.9312 even after the empirical
3.76x SE inflation) and J4b showed the 3.76 factor itself varies 2.54-5.16
by region. The per-condition SE values are miscalibrated, so ANY
threshold built on them inherits the failure.

The fix is to stop using SE values entirely and go to the atlas's own
assumption-free noise floor: SYNONYMOUS variants encode an identical
protein, cannot interact, and their observed |e_b| spread IS the empirical
noise distribution (the same control that carried weight in D1).

PRE-REGISTERED DESIGN (fixed before running; AGENTS 6)
------------------------------------------------------
N2a -- stratifier:
  * Analysis set: rows with own_e_b notna AND se_e_b notna -- the SAME
    row-validity mask script 35 used, inherited ONLY so counts are
    directly comparable to J4/J4a's 570/10,757/538 (notna-ness is a
    validity flag, not a scale). The SE VALUES are never used to flag
    anything; they enter only (i) in this mask and (ii) in gate (g6)'s
    reproduction of the RETIRED numbers, for verification only. Both the
    ok-mask counts and the own_e_b-only counts are printed (row
    accounting, AGENTS 5).
  * Null distribution: |own_e_b| of the n_syn synonymous variants on that
    set.
  * Statistic per variant: syn_ecdf_pct = mean(|e_syn| <= |e_own|) over
    the synonymous null (ECDF percentile in [0,1]; 0.95 = sits beyond the
    95th percentile of the noise floor).
  * Primary flag: epistatic_ecdf := syn_ecdf_pct > 0.95 (nominal 5% FPR --
    choose the cutoff by the FPR you will carry, the ethos script 35's own
    docstring preaches; the synonymous pass fraction at this cutoff is
    printed as the built-in empirical FPR).
  * Sensitivity cutoff: 0.99 (nominal 1% FPR), region table printed for
    it too so the ordering claim can be checked at two cutoffs.
  * Method choice disclosed: ECDF percentile chosen over an empirical-Bayes
    local FDR because it needs no parametric null-mixture fit (assumption-
    free, same logic D1's synonymous control used). No EB local FDR is
    computed; do not describe this file as an FDR estimate.
N2b -- region comparison (mirrors script 35's region table exactly in
  rows/n): per region 1-4, missense n, OLD frac (script 35's N=2 flag,
  RECOMPUTED here from the raw fit -- not read from the retired file),
  NEW frac at 0.95 (and 0.99 sensitivity), delta in percentage points,
  plus median |e_b| as the nonparametric stand-in for script 35's median-
  SE column. Synonymous and nonsense pass fractions at the new cutoffs are
  printed alongside (script 35 reported nonsense as a second reference).
  PRE-REGISTERED pattern rule: the qualitative regional pattern CHANGES
  iff the rank ORDERING of the four region fractions differs between the
  old N=2 flag and the new 0.95 flag (primary); the 0.99 ordering is
  reported as sensitivity. Ordering, not levels: the old flag's
  synonymous FPR is 44.7% and no threshold on disk gets it to 5% (even
  N=3 leaves 28.4%), so old-vs-new FRACTION LEVELS are not comparable by
  construction -- that asymmetry is the finding, not a nuisance, and is
  printed as such.
N2c -- save: data/processed/task_N2_nonparametric_epistatic_set.csv,
  distinct from the retired task35_epistatic_set.csv. This script does
  NOT read the retired per-variant file (N1b audit: no new reader is
  added); it reads only the raw model fit, scripts/lib, and
  task35_summary.csv (script 35's own summary, for gate g6 + the old
  region table).

SANITY GATES (sys.exit(1); AGENTS 4/5)
---------------------------------------
(g1) synonymous n on the analysis set == 570 (agrees with J4a's
     n_syn=570 and L1b's count).
(g2) missense n == 10,757 and nonsense n == 538 (agree with
     task35_summary.csv's threshold rows and J4a's n_mis). Any mismatch
     -> fail with counts printed (reconcile n before interpreting, AGENTS
     5), no retry.
(g3) empirical FPR of the primary flag AMONG SYNONYMOUS in [0.03, 0.08]
     (the 0.95 ECDF self-consistency check; ties in the ECDF make it
     slightly conservative). Outside -> the ECDF is broken -> fail.
(g4) every missense row on the analysis set maps to a region (positions
     are inside REGION_BOUNDS 2-656); any NaN region -> fail.
(g5) all syn_ecdf_pct in [0,1]; epistatic flags are a subset of rows.
(g6) REPRODUCTION CHECK: recomputing the RETIRED N=2 flag (|e_b/SE| > 2)
     must reproduce script 35's own region fractions in
     task35_summary.csv to < 1e-9. This proves the rebuild matches script
     35 column-for-column before any old-vs-new comparison is trusted
     (verification duty, AGENTS 5). Failure -> fail, do not compare.

Limitations (also printed by the script):
  - The 0.95 flag's FPR among synonymous is ~5% BY CONSTRUCTION (it is an
    ECDF quantile of that very distribution); it is a calibration of the
    CUTOFF, not independent evidence that missense calls are true.
    What the flag buys is freedom from the miscalibrated SE scale.
  - Old-vs-new comparison is ORDERING-only (see N2b rule); fraction
    levels differ by design (44.7% vs ~5% synonymous FPR).
  - e_b itself still comes from the same atlas WLS fit -- this replaces
    only the thresholding layer, not the interaction estimate.
  - No new reader of task35_epistatic_set.csv is created (N1b); existing
    readers (50, 59, 61) untouched.

No resampling anywhere -> N_BOOT/N_PERM do not apply (stated per house
convention). Output: task_N2_nonparametric_epistatic_set.csv (N2c).
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.own_context import MT_SE_COLS, CONCS
from scripts.lib.stats_ext import rebuild_interaction_fit, wls_line_se
from scripts.lib.regions import assign_region, REGION_BOUNDS

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"
OUT_CSV = PROC / "task_N2_nonparametric_epistatic_set.csv"

C_PRIMARY = 0.95     # pre-registered primary ECDF cutoff (5% nominal FPR)
C_SENS = 0.99        # sensitivity cutoff (1% nominal FPR)
EXPECT_SYN, EXPECT_SUB, EXPECT_NON = 570, 10757, 538


def fail(msg):
    print(f"GATE FAILED: {msg}")
    sys.exit(1)


def main():
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse, valid = fit["e2"], fit["M_se"], fit["valid"]
    se_b, _ = wls_line_se(Mse, CONCS, valid)

    tab = pd.DataFrame({
        "hgvs_pro": raw["hgvs"], "type": raw["type"],
        "position": raw["start"], "own_e_b": e2["e_b"],
        "_se_ref": se_b,
    })
    tab["region"] = assign_region(tab["position"])

    ok = tab["own_e_b"].notna() & tab["_se_ref"].notna()
    n_own_only = int(tab["own_e_b"].notna().sum())
    print("=== N2a: row accounting (AGENTS 5) ===")
    print(f"total rows in folate_response_model5.csv: {len(tab)}")
    print(f"own_e_b notna (no SE involvement)        : {n_own_only}")
    print(f"analysis set (own_e_b & SE notna mask)   : {int(ok.sum())}  "
          f"[mask inherited from script 35 for count comparability; "
          f"SE VALUES unused for flagging]")
    for t, exp in [("synonymous", EXPECT_SYN), ("substitution", EXPECT_SUB),
                   ("nonsense", EXPECT_NON)]:
        n = int(((tab["type"] == t) & ok).sum())
        print(f"  {t:14s}: {n:>6}  (expected {exp})")
        if n != exp:
            fail(f"(g1/g2) {t} n={n} != {exp} -- reconcile n before "
                 f"interpreting (AGENTS 5)")
    print("(g1)(g2) counts match J4a / task35_summary exactly -- OK")

    # ---- ECDF over the synonymous noise floor ----
    # NOTE (first-run crash fix, disclosed in the log entry): syn/mis were
    # originally sliced HERE, before the flag columns existed. Pandas
    # copy-on-write never propagates columns added later to `tab` into
    # those stale copies, so line 177 raised KeyError 'epistatic_ecdf'.
    # Slices moved to AFTER the flag columns are built; nothing else
    # changed and no gate/verdict had run at crash time.
    syn_mask = (tab["type"] == "synonymous") & ok
    abs_syn = np.sort(tab.loc[syn_mask, "own_e_b"].abs().to_numpy())
    n_syn = len(abs_syn)
    abs_all = tab["own_e_b"].abs().to_numpy()
    # ECDF percentile: fraction of synonymous |e| <= this |e| (ties incl.)
    pct = np.searchsorted(abs_syn, abs_all, side="right") / n_syn
    tab["syn_ecdf_pct"] = pct
    if not ((pct >= 0).all() and (pct <= 1).all()):
        fail("(g5) ECDF percentiles outside [0,1]")
    tab["epistatic_ecdf"] = pct > C_PRIMARY
    tab["epistatic_ecdf_99"] = pct > C_SENS
    # RECOMPUTED retired flag (verification only -- never read the file)
    tab["_z_old"] = tab["own_e_b"] / tab["_se_ref"]
    tab["epistatic_N2_old"] = tab["_z_old"].abs() > 2
    if not tab.loc[ok, "epistatic_ecdf"].isin([True, False]).all():
        fail("(g5) flag not boolean on all rows")

    # slices taken AFTER the flag columns exist (see crash-fix note above)
    syn = tab[syn_mask]
    mis = tab[(tab["type"] == "substitution") & ok]

    fpr_syn = float(syn["epistatic_ecdf"].mean())
    if not (0.03 <= fpr_syn <= 0.08):
        fail(f"(g3) synonymous FPR {fpr_syn:.4f} outside [0.03,0.08] -- "
             f"ECDF self-consistency broken")
    print(f"(g3) empirical FPR among synonymous at {C_PRIMARY}: "
          f"{fpr_syn:.4f} ({int(syn['epistatic_ecdf'].sum())}/{n_syn}) "
          f"-> inside [0.03, 0.08] -- OK (by-construction check)")

    sub_mis = mis[mis["region"].notna()]
    if len(sub_mis) != len(mis):
        fail(f"(g4) {int(mis['region'].isna().sum())} missense rows outside "
             f"REGION_BOUNDS")
    print(f"(g4) all {len(mis)} missense rows map to a region -- OK")

    # ---- gate g6: reproduce script 35's own region fractions ----
    summ = pd.read_csv(PROC / "task35_summary.csv")
    old_tbl = summ[summ["stage"] == "region"][["region", "frac_epistatic",
                                               "n"]].astype(
        {"region": int, "n": int})
    diffs = []
    for _, r in old_tbl.iterrows():
        mine = float(mis[mis["region"] == r["region"]]
                     ["epistatic_N2_old"].mean())
        diffs.append(abs(mine - float(r["frac_epistatic"])))
        if int((mis["region"] == r["region"]).sum()) != int(r["n"]):
            fail(f"(g6) region {r['region']} n mismatch vs "
                 f"task35_summary.csv")
    if max(diffs) > 1e-9:
        fail(f"(g6) reproduction of retired N=2 fractions off by "
             f"{max(diffs):.3e} (> 1e-9)")
    print(f"(g6) REPRODUCTION: recomputed retired N=2 region fractions "
          f"match task35_summary.csv to {max(diffs):.1e} "
          f"(4/4 regions, n's match) -- rebuild == script 35 -- OK")

    # ---- N2a threshold table (mirror script 35's FPR framing) ----
    print("\n" + "=" * 74)
    print("N2a: EPISTATIC SET BY SYNONYMOUS ECDF (SE values not used)")
    print("=" * 74)
    for c in (C_PRIMARY, C_SENS):
        col = "epistatic_ecdf" if c == C_PRIMARY else "epistatic_ecdf_99"
        line = f"  cutoff pct > {c:.2f}  "
        for t, lbl in [("substitution", "missense"),
                       ("synonymous", "syn (FPR)"),
                       ("nonsense", "nonsense")]:
            sub = tab[(tab["type"] == t) & ok]
            n_pass = int(sub[col].sum())
            line += (f"  {lbl}: {n_pass:>5}/{len(sub):<5} "
                     f"({100 * sub[col].mean():4.1f}%)")
        print(line)
    print("  (syn column = empirical FPR of the cutoff; it is ~5%/1% BY")
    print("   CONSTRUCTION -- the ECDF is that distribution. The win is")
    print("   freedom from the miscalibrated SE scale, not this number.)")
    print("  For contrast, the RETIRED N=2 flag's own FPRs "
          f"(task35_summary.csv): syn 44.7%, missense 44.8% -- and even")
    print("  N=3 leaves syn at 28.4%, so no cutoff on the old machinery")
    print("  can reach 5%.")

    # ---- N2b: region table, old vs new ----
    print("\n" + "=" * 74)
    print("N2b: REGION TABLE (missense) -- retired N=2 vs new ECDF flags")
    print("=" * 74)
    rows = []
    old_order, new_order, new99_order = [], [], []
    for rg in sorted(REGION_BOUNDS):
        sub = mis[mis["region"] == rg]
        if len(sub) == 0:
            continue
        lo, hi = REGION_BOUNDS[rg]
        f_old = float(sub["epistatic_N2_old"].mean())
        f_new = float(sub["epistatic_ecdf"].mean())
        f_99 = float(sub["epistatic_ecdf_99"].mean())
        med_abs = float(sub["own_e_b"].abs().median())
        print(f"  region {rg} ({lo}-{hi}) n={len(sub):5d}  "
              f"old_N2={100 * f_old:5.1f}%  new_0.95={100 * f_new:5.1f}%  "
              f"new_0.99={100 * f_99:5.1f}%  "
              f"delta_0.95={100 * (f_new - f_old):+6.1f} pp  "
              f"median|e_b|={med_abs:.4f}")
        rows.append(dict(region=rg, n=len(sub), frac_old_n2=f_old,
                         frac_new_095=f_new, frac_new_099=f_99,
                         delta_pp=100 * (f_new - f_old),
                         median_abs_e_b=med_abs))
        old_order.append((f_old, rg))
        new_order.append((f_new, rg))
        new99_order.append((f_99, rg))
    old_rank = [rg for _, rg in sorted(old_order, reverse=True)]
    new_rank = [rg for _, rg in sorted(new_order, reverse=True)]
    rank99 = [rg for _, rg in sorted(new99_order, reverse=True)]
    changed = old_rank != new_rank
    print(f"\n  ordering by fraction (high->low):")
    print(f"    retired N=2  : {old_rank}")
    print(f"    new pct>0.95 : {new_rank}")
    print(f"    new pct>0.99 : {rank99}  (sensitivity)")
    if changed:
        verdict = (f"CHANGED: old {old_rank} vs new {new_rank} -- the "
                   f"qualitative regional pattern does NOT survive the "
                   f"nonparametric replacement"
                   + ("" if new_rank == rank99 else
                      f"; note the 0.99 ordering {rank99} also differs "
                      f"from 0.95's, so the new pattern is itself "
                      f"cutoff-sensitive"))
    else:
        verdict = (f"UNCHANGED: both flags order the regions {new_rank} "
                   f"-- the qualitative regional pattern survives "
                   f"(0.99 sensitivity ordering {rank99} "
                   f"{'matches' if rank99 == new_rank else 'DIFFERS'})")
    print(f"\n  PRE-REGISTERED N2b VERDICT (ordering rule): {verdict}")
    print("  (LEVELS are not comparable by construction: old syn FPR "
          "44.7% vs new ~5%;")
    print("   ordering is the pre-registered comparison.)")

    # ---- N2c: save ----
    out = tab.loc[ok, ["hgvs_pro", "type", "position", "own_e_b", "region",
                       "syn_ecdf_pct", "epistatic_ecdf", "epistatic_ecdf_99",
                       "epistatic_N2_old"]].copy()
    out = out.rename(columns={"epistatic_N2_old": "epistatic_N2_old_RECOMPUTED"})
    out.to_csv(OUT_CSV, index=False)
    pd.DataFrame(rows).to_csv(PROC / "task_N2_region_comparison.csv",
                              index=False)
    print(f"\nN2c: saved {len(out)} rows -> {OUT_CSV}")
    print(f"N2c: region comparison -> "
          f"{PROC / 'task_N2_region_comparison.csv'}")
    print("     (distinct file from the retired task35_epistatic_set.csv; "
          "no reader of the")
    print("      retired file was added or changed -- N1b constraint "
          "respected)")

    print("\nLIMITATIONS (printed by the script, AGENTS 6):")
    print(f"  - The synonymous FPR at cutoff {C_PRIMARY} is ~5% BY")
    print("    CONSTRUCTION (ECDF quantile of that distribution): it")
    print("    calibrates the cutoff, not the truth of missense calls.")
    print("  - Old-vs-new is ORDERING-only; levels differ by design")
    print("    (44.7% vs ~5% synonymous FPR).")
    print("  - e_b still comes from the same atlas WLS fit: only the")
    print("    thresholding layer was replaced, not the estimate.")
    print("  - Counts fixed to script 35's row-validity mask for")
    print("    comparability; own_e_b-only count printed above if it")
    print("    differs (both disclosed).")
    print("  - No EB local-FDR computed (method choice disclosed in the")
    print("    docstring); this file is percentile ranks, not FDRs.")


if __name__ == "__main__":
    main()
