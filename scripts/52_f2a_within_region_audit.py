"""
Task F2a (REVIEW_TRIAGE item 22): within-region isotonic calibration audit.

Question under audit: was the within-region calibration behind results-log
4.3 (region-2 sign reversal resolved; pooled correlation +0.090 -> +0.191)
cross-fitted WITHIN region -- held-out positions inside that region -- rather
than merely position-held-out globally with an in-region fit, or in-sample?

PRE-REGISTERED CHECKS (written before running):
1. CODE AUDIT: print the source of scripts/lib/stats.py::
   crossfit_isotonic_within_group and crossfit_isotonic_by_position; the
   group loop must subset to the group BEFORE position folds are formed.
2. IDENTITY CHECKS (failure -> sys.exit(1), no larger run):
   a. within-group predictions on the full table must equal, for every
      region r, crossfit_isotonic_by_position applied to region r's subset
      alone (max |diff| < 1e-12) -> the calibration for region r never sees
      another region's rows and holds out positions within region r.
   b. within-group predictions must DIFFER from globally position-held-out
      pooled predictions (max |diff| > 1e-6) -> the two mechanisms are
      distinguishable on this data (otherwise 2a proves nothing here).
3. RE-DERIVATION: recompute 4.3's published numbers under all three schemes
   (pooled folds / region-stratified folds / within-region) for
   x = |GI_folinate_independent| vs calibrated error |target - pred|, and
   compare with the published constants:
     region2 rho: pooled -0.112, stratified -0.112  (scripts/22 literal)
     pooled rho:  +0.090 -> +0.191 (MTHFR_RESULTS_LOG 4.3 line ~127-132;
                 +0.090 and the four region values are also literals in
                 scripts/22_update_writeup.py, written from the since-lost
                 task_region2_diagnostic.csv)
     within-region per-region rhos: +0.163, +0.075, +0.161, +0.186 (scripts/22)
   PRE-REGISTERED TOLERANCE: every published constant must be reproduced to
   |delta| <= 0.01, AND the sign pattern must reproduce (region2 < 0 under
   pooled folds; region2 > 0 and pooled rho larger under within-region).
   x = |own_e_b| is printed as a secondary, non-scored line for transparency.

VERDICT (pre-registered): CONFIRMED-WITHIN-REGION iff identity checks 2a/2b
pass AND every published constant is within 0.01 AND the sign pattern holds;
else DIVERGENT.

PROVENANCE CAVEAT (printed by the script, AGENTS 6): no file in this
repository writes data/processed/task_region2_diagnostic.csv (scanned
scripts/ and notebooks/ at runtime; the CSV itself is absent). The original
producing code is missing, so this audit identifies WHICH library mechanism
reproduces the published values (re-derivation), it cannot read the
historical script itself. Deltas between re-derived and published values
therefore also cover any drift between the current phase5 table and the data
the original run saw.

N_BOOT (env, default 2000) is used for ONE position-cluster bootstrap CI on
the within-region pooled rho.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import (crossfit_isotonic_by_position,
                                crossfit_isotonic_stratified,
                                crossfit_isotonic_within_group,
                                position_cluster_bootstrap, _spearman)

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
N_FOLDS = 5
TOL = 0.01

# Published constants (provenance in docstring)
PUB = {"region2_pooled": -0.112, "region2_stratified": -0.112,
       "pooled_pooled": 0.090, "pooled_within": 0.191,
       "within_r1": 0.163, "within_r2": 0.075, "within_r3": 0.161,
       "within_r4": 0.186}


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = df.dropna(subset=["model_C", "target"]).copy()
    df["region"] = assign_region(df["position"])
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df["abs_own"] = df["own_e_b"].abs()
    print(f"Analysis frame: {len(df)} variants, {df['position'].nunique()} positions")
    print("region counts:", df["region"].value_counts().sort_index().to_dict())
    print("positions per region:",
          df.groupby("region")["position"].nunique().to_dict())

    # ---- Check 1: code audit (source printed so the script is the record) ----
    print("\n" + "=" * 72)
    print("CHECK 1: source audit")
    print("=" * 72)
    import inspect
    import scripts.lib.stats as st
    src_group = inspect.getsource(st.crossfit_isotonic_within_group)
    src_pos = inspect.getsource(st.crossfit_isotonic_by_position)
    print(src_group)
    # Normalize whitespace first: the audited call is wrapped across lines
    # ("crossfit_isotonic_by_position(\n            sub, ..."), so a naive
    # same-line substring check misreports subset-first as False. Smoke-test
    # bug, fixed before any numeric check ran; the printed source above is
    # the ground truth the matcher must agree with.
    def _flat(s):
        return " ".join(s.split())
    fg, fp = _flat(src_group), _flat(src_pos)
    subset_first = "for g, sub in df.groupby(group_col)" in fg and \
                   "crossfit_isotonic_by_position( sub" in fg
    pos_holds_out = "position_col].isin(fold)" in fp and \
                    "train, test = d[~test_mask], d[test_mask]" in fp
    print(f"  -> subsets to group BEFORE calling by_position: {subset_first}")
    print(f"  -> by_position holds out POSITIONS (train excludes test fold): "
          f"{pos_holds_out}")
    if not (subset_first and pos_holds_out):
        print("CHECK 1 FAIL: code path is not within-group position-held-out.")
        sys.exit(1)

    # ---- Check 2: identity checks ----
    print("\n" + "=" * 72)
    print("CHECK 2: identity checks")
    print("=" * 72)
    pred_within = crossfit_isotonic_within_group(df, "position", "model_C",
                                                  "target", "region",
                                                  n_folds=N_FOLDS, seed=SEED)
    parts = {}
    for r in sorted(REGION_BOUNDS):
        sub = df[df["region"] == r]
        parts[r] = crossfit_isotonic_by_position(sub, "position", "model_C",
                                                  "target", n_folds=N_FOLDS,
                                                  seed=SEED)
    pred_regions = pd.concat([parts[r] for r in sorted(REGION_BOUNDS)]).loc[df.index]
    d2a = float((pred_within - pred_regions).abs().max())
    pred_pooled = crossfit_isotonic_by_position(df, "position", "model_C",
                                                 "target", n_folds=N_FOLDS,
                                                 seed=SEED)
    d2b = float((pred_within - pred_pooled).abs().max())
    print(f"  2a max|within - per-region-by-position| = {d2a:.3e}  "
          f"(gate < 1e-12)  -> {'OK' if d2a < 1e-12 else 'FAIL'}")
    print(f"  2b max|within - pooled-by-position|      = {d2b:.3e}  "
          f"(gate > 1e-6)   -> {'OK' if d2b > 1e-6 else 'FAIL'}")
    if not (d2a < 1e-12 and d2b > 1e-6):
        print("CHECK 2 FAIL. Sanity check failed; stopping (no retry).")
        sys.exit(1)
    print("  -> 2a proves: predictions for every region are bit-identical to a")
    print("     fit whose training AND test rows are only that region's rows,")
    print("     with positions (not variants) held out inside the region.")
    print("  -> 2b proves: this mechanism is distinguishable from the pooled one")

    # ---- Check 3: re-derive the published 4.3 numbers ----
    print("\n" + "=" * 72)
    print("CHECK 3: re-derivation of results-log 4.3 (three calibration schemes)")
    print("=" * 72)
    schemes = {
        "pooled":     crossfit_isotonic_by_position(df, "position", "model_C",
                                                     "target", n_folds=N_FOLDS,
                                                     seed=SEED),
        "stratified": crossfit_isotonic_stratified(df, "position", "model_C",
                                                    "target", "region",
                                                    n_folds=N_FOLDS, seed=SEED),
        "within":     pred_within,
    }
    rows = []
    derived = {}
    for sname, pred in schemes.items():
        df[f"err_{sname}"] = (df["target"] - pred).abs()
        for x in ("abs_gi", "abs_own"):
            g = df.dropna(subset=[x, f"err_{sname}"])
            pool = _spearman(g[x], g[f"err_{sname}"])
            regs = {r: _spearman(g[g["region"] == r][x],
                                 g[g["region"] == r][f"err_{sname}"])
                    for r in sorted(REGION_BOUNDS)}
            if x == "abs_gi":
                derived[(sname, "pooled")] = pool
                for r in sorted(REGION_BOUNDS):
                    derived[(sname, f"r{r}")] = regs[r]
            tag = "  <- published target" if x == "abs_gi" else ""
            print(f"{sname:10s} x={x:8s} pooled={pool:+.4f} "
                  f"regions={{{', '.join(f'{k}: {v:+.4f}' for k, v in regs.items())}}}{tag}")
            for scope, val in [("pooled", pool)] + [(f"r{k}", v)
                                                     for k, v in regs.items()]:
                rows.append({"scheme": sname, "x": x, "scope": scope,
                             "rho": val})

    checks = {
        "pooled_pooled": derived[("pooled", "pooled")],
        "pooled_within": derived[("within", "pooled")],
        "region2_pooled": derived[("pooled", "r2")],
        "region2_stratified": derived[("stratified", "r2")],
        "within_r1": derived[("within", "r1")],
        "within_r2": derived[("within", "r2")],
        "within_r3": derived[("within", "r3")],
        "within_r4": derived[("within", "r4")],
    }
    print("\n  published-constant deltas (tolerance |delta| <= 0.01):")
    all_ok = True
    for k, pub in PUB.items():
        d = abs(checks[k] - pub)
        ok = d <= TOL
        all_ok &= ok
        print(f"    {k:20s} derived={checks[k]:+.4f}  published={pub:+.4f}  "
              f"|delta|={d:.4f}  -> {'OK' if ok else 'FAIL'}")
    sign_ok = (derived[("pooled", "r2")] < 0 and derived[("within", "r2")] > 0
               and derived[("within", "pooled")] > derived[("pooled", "pooled")])
    print(f"  sign pattern (region2 pooled<0, region2 within>0, pooled rises): "
          f"{'OK' if sign_ok else 'FAIL'}")

    # ---- Provenance scan (the missing producing script) ----
    print("\n" + "=" * 72)
    print("PROVENANCE: who writes task_region2_diagnostic.csv?")
    print("=" * 72)
    writers, readers = [], []
    for pat in ("scripts/*.py", "notebooks/*.ipynb"):
        for f in sorted(ROOT.glob(pat)):
            txt = f.read_text(errors="replace")
            if "task_region2_diagnostic" in txt:
                for line in txt.splitlines():
                    if "task_region2_diagnostic" in line:
                        kind = "WRITER" if "to_csv" in line else "reader"
                        (writers if kind == "WRITER" else readers).append(
                            f"{f.name}: {line.strip()[:100]}")
    exists = (PROC / "task_region2_diagnostic.csv").exists()
    resmd = (ROOT / "RESULTS.md").read_text(errors="replace") \
        if (ROOT / "RESULTS.md").exists() else ""
    has_tbl = "pooled random folds" in resmd
    print(f"  writers found: {len(writers)}  -> {writers if writers else 'NONE'}")
    print(f"  readers found: {len(readers)}  -> {readers}")
    print(f"  CSV present on disk: {exists}")
    print(f"  RESULTS.md contains the region-2 table: {has_tbl}")

    verdict = all_ok and sign_ok
    print("\nF2a VERDICT (pre-registered): "
          f"{'CONFIRMED-WITHIN-REGION' if verdict else 'DIVERGENT'} "
          f"(identity 2a/2b pass, constants within 0.01: {all_ok}, "
          f"sign pattern: {sign_ok})")
    if not verdict:
        print("Pre-registered checks failed; do not interpret 4.3 as verified.")
        sys.exit(1)

    r = position_cluster_bootstrap(df, "position", "abs_gi", "err_within",
                                   n_boot=N_BOOT, seed=SEED)
    print(f"\nwithin-region pooled rho cluster bootstrap (N_BOOT={N_BOOT}): "
          f"rho={r['observed_rho']:+.4f} CI=[{r['ci_lo']:+.4f},"
          f"{r['ci_hi']:+.4f}] n={r['n_rows']} pos={r['n_clusters']}")

    pd.DataFrame(rows).to_csv(PROC / "task52_f2a_within_region.csv", index=False)
    print(f"Saved {PROC / 'task52_f2a_within_region.csv'}")
    print("\nLIMITATIONS (script is the record, AGENTS 6): the ORIGINAL script "
          "that produced task_region2_diagnostic.csv is missing from the repo "
          "(no writer exists; CSV absent; RESULTS.md lacks the table because "
          "script 22 skips it when the CSV is missing). This audit therefore "
          "identifies the mechanism by RE-DERIVATION: the within-group library "
          "function reproduces every published constant to <=0.01, which is "
          "strong evidence but not a reading of the lost historical code. "
          "Nonzero deltas may reflect data drift in phase5_analysis_table.csv "
          "since the original run. n_folds=5, seed=0 assumed (the values match; "
          "other settings were not searched).")
