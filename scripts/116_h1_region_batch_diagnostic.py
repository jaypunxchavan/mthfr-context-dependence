"""
Script 116 (task H1, Group H) -- region batch-effect diagnostic.

PRE-REGISTERED: this docstring was written before the first run; axes,
frames, decision rule, and gates below were fixed before any number
produced here was seen (AGENTS sec 6).  Nothing is selected after
results.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group H, task H1.

H1a -- FOUR AXES, four regions
-------------------------------
Regions: scripts/lib/regions.py REGION_BOUNDS =
  R1 (2,147)  R2 (148,294)  R3 (295,474)  R4 (475,656)
(provenance: primer-design file via 2nd author, Sept 2026; union of the
ranges = the atlas's position set; tile counts 4/4/5/6 match the paper).

Axes (per the task: read depth IF AVAILABLE, per-variant SE,
synonymous-variant variance, WT-arm fitness):

  1. READ DEPTH -- availability sweep first: every CSV under
     data/raw/mthfrModel/ (header scan for depth/n_read/read_count/
     coverage/rd columns).  If none: report NOT AVAILABLE in the
     project's data and say exactly what was searched.  Never
     substitute a proxy and call it read depth.
  2. PER-VARIANT SE -- recorded se_e_b (scripts/35 via
     task35_epistatic_set.csv, known-se WLS intercept SE) on the
     10,757-row analysis base (the same frame Group G used).
  3. SYNONYMOUS-VARIANT VARIANCE -- sample variance of own_e_b among
     type == "synonymous" rows with finite own_e_b (recorded values,
     scripts/35/17 fits; one row per position by construction).
     This is the region's assay-noise proxy: synonymous variants are
     neutral controls, so their spread measures measurement noise.
     Reported per region with n and positions.
  4. WT-ARM FITNESS -- published w.fitness column of
     folate_response_model5.csv (raw; PRIMARY, not a re-fit) on the
     analysis base.

Per region per axis: n rows, n positions, mean, median, and a 95%
position-cluster bootstrap CI of the mean (resample positions WITHIN
the region; for the synonymous variance axis the statistic is the
variance itself, with its own cluster-bootstrap CI; seed 0, N_BOOT
env, default 10000).  Positions are the resampling unit everywhere:
the 19 substitutions at a position are not independent (AGENTS 3).

Also printed per axis: a 4-region Kruskal-Wallis on POSITION-level
aggregates (each position's mean across its rows) -- positions are
the units because region is a deterministic function of position; a
row-level test would be pseudoreplication.  Descriptive diagnostic;
no multiplicity correction across the three testable axes, stated.

Primary contrast (the task asks about region 4): region 4 vs pooled
regions 1-3, difference in means (variance difference for axis 3),
with an independent within-group position-cluster bootstrap CI.

H1b -- DECISION RULE (pre-stated)
---------------------------------
Per axis: region 4 differs systematically on that axis iff the 95% CI
of the region-4-vs-rest contrast excludes 0.  The verdict prints:
  - each axis's contrast, CI, and verdict;
  - if >=1 axis differs: region 4 flagged as the LEADING CANDIDATE
    explanation for region 4's anomalous findings (depth reversal,
    -237/+010 anchor pattern -- context quoted from the task doc, not
    re-derived here) as a mutagenesis library/batch effect, not
    necessarily biology, with the recommendation that region FIXED
    EFFECTS become the default treatment in future analyses rather
    than a sensitivity check;
  - if NO axis differs: say so plainly (region 4 does not differ
    systematically on the axes measurable here) and note read depth
    was unavailable.
Either outcome is reportable as-is.  Axis 3's contrast sign is
interpreted as "more noise in R4" if variance_R4 > variance_rest.

GATES (failure -> print exact mismatch, sys.exit(1)):
  G1  Region mapping: bounds exactly equal REGION_BOUNDS, pairwise
      disjoint, every analysis-base position maps to exactly one
      region, zero unmapped; per-region position counts printed.
  G2  Analysis base = (10,757 rows, 654 positions) -- same frame as
      Group G.
  G3  w.fitness joins the base with 0 missing rows and 0 NaN values.
  G4  Synonymous axis: >= 100 finite rows total AND >= 50 per region
      (variance otherwise too unstable to report; counts printed).

LIMITATIONS (printed with the output):
  - Read depth unavailable => three axes, not four; a library/batch
    effect could exist on read depth alone and remain invisible here.
  - Region = position range => axis values are compared across
    DISJOINT position sets; any position-composition difference
    (e.g. buried vs exposed) is part of the signal being measured,
    not separable from it in this design.
  - Synonymous variance uses one row per position; variance CIs are
    wide with ~130-160 positions per region -- report the CI width,
    do not over-read.
  - Published w.fitness inherits the atlas's own WT-arm fit
    assumptions; not re-derived.
  - Three axes tested, no multiplicity correction (diagnostic, not
    confirmatory).

Usage:
  N_BOOT=300   venv/bin/python3 scripts/116_h1_region_batch_diagnostic.py
  N_BOOT=10000 venv/bin/python3 scripts/116_h1_region_batch_diagnostic.py
"""
import os
import re
import sys
import time
import warnings
from glob import glob
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scipy.stats import kruskal

from scripts.lib.regions import REGION_BOUNDS

PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
OUT = PROC / "task116_h1_region_metrics.csv"
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def _cluster_counts(positions, n_boot, rng):
    """(n_boot, n_pos) resample counts over unique positions + row->pos map."""
    uniq, inverse = np.unique(positions, return_inverse=True)
    n_pos = len(uniq)
    draws = rng.integers(0, n_pos, size=(n_boot, n_pos))
    counts = np.zeros((n_boot, n_pos), dtype=np.int64)
    rows = np.repeat(np.arange(n_boot), n_pos)
    np.add.at(counts, (rows, draws.ravel()), 1)
    return counts, inverse, n_pos


def _stat_distributions(v, counts, inverse, n_pos, stat):
    """Per-draw `stat` of values, resampling positions as clusters."""
    fin = np.isfinite(v).astype(float)
    vv = np.where(fin > 0, v, 0.0)
    N = counts @ np.bincount(inverse, weights=fin, minlength=n_pos)
    S = counts @ np.bincount(inverse, weights=vv * fin, minlength=n_pos)
    S2 = counts @ np.bincount(inverse, weights=vv * vv * fin, minlength=n_pos)
    if stat == "mean":
        return S / np.maximum(N, 1)
    # sample variance, ddof = 1, over finite values in the resample
    return (S2 - S * S / np.maximum(N, 1)) / np.maximum(N - 1, 1)


def cluster_ci_stat(df, val_col, stat, n_boot, seed):
    """95% CI of `stat` over values, resampling positions (clusters)."""
    rng = np.random.default_rng(seed)
    counts, inverse, n_pos = _cluster_counts(
        df["position"].to_numpy(), n_boot, rng)
    sv = _stat_distributions(df[val_col].to_numpy(float), counts, inverse,
                             n_pos, stat)
    return (float(np.nanpercentile(sv, 2.5)),
            float(np.nanpercentile(sv, 97.5)))


def cluster_diff_ci(df, val_col, stat, n_boot, seed):
    """CI of (region-4 stat) - (pooled rest), independent within-group draws."""
    def grp(d, rng):
        counts, inverse, n_pos = _cluster_counts(d["position"].to_numpy(),
                                                 n_boot, rng)
        return _stat_distributions(d[val_col].to_numpy(float), counts,
                                   inverse, n_pos, stat)

    a = df[df["region"] == 4]
    b = df[df["region"] != 4]
    s_a = grp(a, np.random.default_rng(seed))
    s_b = grp(b, np.random.default_rng(seed + 1))
    diff = s_a - s_b
    obs_a = a[val_col].mean() if stat == "mean" else a[val_col].var(ddof=1)
    obs_b = b[val_col].mean() if stat == "mean" else b[val_col].var(ddof=1)
    return (float(obs_a - obs_b),
            float(np.nanpercentile(diff, 2.5)),
            float(np.nanpercentile(diff, 97.5)))


if __name__ == "__main__":
    banner(f"H1 -- region batch-effect diagnostic (scripts/116)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ---- axis 1: read-depth availability sweep ---------------------------
    hits = []
    searched = 0
    for f in glob(str(RAW / "**" / "*.csv"), recursive=True):
        searched += 1
        try:
            hdr = open(f, errors="ignore").readline()
        except OSError:
            continue
        cols = [c.strip('"') for c in hdr.split(",")]
        found = [c for c in cols
                 if re.search(r"depth|n_read|read_?count|coverage|\brd\b",
                              c, re.I)]
        if found:
            hits.append((f, found))
    print(f"  Axis 1 READ DEPTH: {searched} CSVs under data/raw/mthfrModel "
          f"header-scanned -> " +
          (f"columns found: {hits}" if hits else
           "NOT AVAILABLE (no depth/n_read/read_count/coverage/rd column "
           "in any released file). Reportable as unavailable; no proxy "
           "substituted."))

    # ---- regions + frames (gates) ----------------------------------------
    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G2 FAIL: base = ({len(base)}, {base['position'].nunique()}), "
              f"expected (10757, 654)")
    print(f"  G2 PASS: base (10757, 654) -- same frame as Group G")

    bounds = {int(k): (int(a), int(b)) for k, (a, b) in
              REGION_BOUNDS.items()}
    if bounds != {1: (2, 147), 2: (148, 294), 3: (295, 474),
                  4: (475, 656)}:
        gfail(f"G1 FAIL: REGION_BOUNDS = {bounds}")
    spans = sorted(bounds.values())
    if any(spans[i][1] >= spans[i + 1][0] for i in range(3)):
        gfail(f"G1 FAIL: region bounds overlap: {bounds}")

    def reg(p):
        for k, (a, b) in bounds.items():
            if a <= p <= b:
                return k
        return 0

    base["region"] = base["position"].map(reg)
    unmapped = int((base["region"] == 0).sum())
    if unmapped:
        gfail(f"G1 FAIL: {unmapped} base rows outside all region bounds")
    npos = base.groupby("region")["position"].nunique().to_dict()
    print(f"  G1 PASS: bounds == REGION_BOUNDS, disjoint; 0 unmapped; "
          f"positions per region {npos} (sum {sum(npos.values())})")

    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")[
        ["hgvs", "w.fitness"]].rename(columns={"hgvs": "hgvs_pro"})
    n_before = len(base)
    base = base.merge(raw, on="hgvs_pro", how="left")
    if len(base) != n_before:
        gfail(f"G3 FAIL: w.fitness join changed row count "
              f"{n_before} -> {len(base)} (duplicate hgvs_pro in raw?)")
    if base["w.fitness"].isna().any():
        gfail(f"G3 FAIL: {int(base['w.fitness'].isna().sum())} base rows "
              f"missing w.fitness")
    print(f"  G3 PASS: published w.fitness joins base with 0 missing")

    se = t35[["hgvs_pro", "se_e_b", "own_e_b", "type"]]
    n_before = len(base)
    base = base.merge(se[["hgvs_pro", "se_e_b"]], on="hgvs_pro", how="left")
    if len(base) != n_before:
        gfail(f"G3 FAIL: se_e_b join changed row count {n_before} -> "
              f"{len(base)} (duplicate hgvs_pro in task35?)")
    if base["se_e_b"].isna().any():
        gfail(f"G3 FAIL: {int(base['se_e_b'].isna().sum())} base rows "
              f"missing se_e_b")

    syn = t35[(t35["type"] == "synonymous") & t35["own_e_b"].notna()].copy()
    syn = syn.rename(columns={"own_e_b": "value"})
    syn["region"] = syn["position"].map(reg)
    per = syn.groupby("region").size().to_dict()
    if len(syn) < 100 or any(per.get(r, 0) < 50 for r in (1, 2, 3, 4)):
        gfail(f"G4 FAIL: synonymous finite rows total={len(syn)} per-region "
              f"{per} (need >=100 total, >=50 per region)")
    print(f"  G4 PASS: synonymous axis {len(syn)} rows "
          f"({len(syn)} positions, 1:1), per region {per}")

    base["value_se"] = base["se_e_b"]
    base["value_fit"] = base["w.fitness"]
    syn["value_var"] = syn["value"]

    # ---- per-region summaries --------------------------------------------
    banner("H1a -- PER-REGION DISTRIBUTIONS (mean [95% position-cluster CI])",
           "-")
    axes = [
        ("per-variant SE (se_e_b)", base, "value_se", "mean"),
        ("WT-arm fitness (w.fitness)", base, "value_fit", "mean"),
        ("synonymous own_e.b VARIANCE", syn, "value_var", "var"),
    ]
    rows, contrasts = [], []
    for name, df, col, stat in axes:
        print(f"\n  {name}:")
        for r in (1, 2, 3, 4):
            d = df[df["region"] == r]
            point = d[col].mean() if stat == "mean" else d[col].var(ddof=1)
            lo, hi = cluster_ci_stat(d, col, stat, N_BOOT, SEED)
            print(f"    R{r}: n={len(d):5d} pos={d['position'].nunique():4d} "
                  f"mean={d[col].mean():+.6f} median={d[col].median():+.6f} "
                  f"{'var' if stat == 'var' else 'mean'}="
                  f"{point:.6f} [{lo:.6f}, {hi:.6f}]")
            rows.append(dict(axis=name, region=r, n=len(d),
                             npos=int(d["position"].nunique()),
                             mean=float(d[col].mean()),
                             median=float(d[col].median()),
                             stat_point=point, ci_lo=lo, ci_hi=hi,
                             stat=stat))
        # region 4 vs pooled 1-3
        d, lo, hi = cluster_diff_ci(df, col, stat, N_BOOT, SEED)
        excl0 = not (lo <= 0 <= hi)
        contrasts.append(dict(axis=name, diff=d, lo=lo, hi=hi,
                              r4_differs=excl0))
        print(f"    R4 - R(1-3): {d:+.6f} [{lo:+.6f}, {hi:+.6f}] -> "
              f"{'CI excludes 0' if excl0 else 'CI includes 0'}")
        # 4-region Kruskal-Wallis on position-level aggregates (mean axis)
        if stat == "mean":
            pm = df.groupby(["region", "position"])[col].mean().reset_index()
            groups = [pm.loc[pm["region"] == r, col].to_numpy()
                      for r in (1, 2, 3, 4)]
            try:
                h, p = kruskal(*groups)
                print(f"    Kruskal-Wallis across 4 regions "
                      f"(position-level means): H={h:.3f}, p={p:.4g}")
            except ValueError as e:
                print(f"    Kruskal-Wallis not computable: {e}")

    pd.DataFrame(rows).to_csv(OUT, index=False)

    # ---- H1b verdict -------------------------------------------------------
    banner("H1b -- VERDICT (pre-registered rule: R4-vs-rest CI excludes 0)",
           "-")
    differing = [c for c in contrasts if c["r4_differs"]]
    for c in contrasts:
        print(f"  {c['axis']:32s} R4-R(1-3) {c['diff']:+.6f} "
              f"[{c['lo']:+.6f}, {c['hi']:+.6f}] -> "
              f"{'DIFFERS' if c['r4_differs'] else 'no'}")
    if differing:
        names = ", ".join(c["axis"] for c in differing)
        print(f"  VERDICT: region 4 differs systematically on: {names} "
              f"(CI excludes 0). Per the pre-registered rule this is "
              f"flagged as the LEADING CANDIDATE explanation for region "
              f"4's anomalous findings (the depth reversal, the "
              f"-237/+010 anchor pattern -- anomalies quoted from the "
              f"task doc, not re-derived here): a mutagenesis library or "
              f"batch effect, not necessarily biology. RECOMMENDATION: "
              f"region fixed effects become the DEFAULT treatment in any "
              f"future analysis, rather than a sensitivity check.")
    else:
        print("  VERDICT: no tested axis shows region 4 differing "
              "systematically (every R4-vs-rest CI includes 0). On the "
              "axes measurable here, region 4 does NOT differ from the "
              "other regions; note read depth was NOT available, so a "
              "depth-only batch effect would remain invisible to this "
              "diagnostic.")

    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. Read depth unavailable (3 axes tested, not 4): a")
    print("     library/batch effect on depth alone is untested.")
    print("  2. Region = position range: axes compare disjoint position")
    print("     sets; position-composition differences (buried/exposed")
    print("     mix etc.) are part of what is measured, not separable.")
    print("  3. Synonymous variance: ~128-157 positions/region -> CI")
    print("     widths are what they are; do not over-read.")
    print("  4. w.fitness is the atlas's published WT-arm fit (not")
    print("     re-derived); se_e_b is scripts/35's known-se WLS value.")
    print("  5. Three axes, no multiplicity correction -- diagnostic,")
    print("     not confirmatory.")
    print(f"\nWrote {OUT}")
    print(f"SCRIPT 116 DONE ({time.time() - T0:.1f}s)")
