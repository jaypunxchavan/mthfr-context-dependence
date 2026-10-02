"""
Script 100 (tasks X1 + X2 of DISATTENUATION_AND_LEDGER.md, Group X):

X1 — a plain continuous regression of per-position ESM-2 shift magnitude
(yE) vs alignment depth (Neff), and the analogous ThermoMPNN residual
(yT1), on the SAME per-position data already computed for the
alignment-depth discriminator (data/processed/task79_depth_positions.
csv, 586 positions), with position-level inference, plus the decile-
binned shape and the leverage check the earlier version omitted.

X2 — compare the atlas's four mutagenesis-region boundaries against
MTHFR's actual functional domain boundaries and test whether the
depth-tracking effect breaks at domain edges or region edges.

PRE-REGISTERED (this docstring written before any run; AGENTS 6)
------------------------------------------------------------------
FRAME: task79_depth_positions.csv exactly as on disk (586 rows, one row
per position; columns position, region, neff, cons, n_var, yE, yT1,
yT2, yT3, sE, sT1). Gate G1: 586 unique positions, neff finite within
[1, 4783] (script 79's measured Neff bounds). Gate G2: pooled
Spearman rho(yE, neff) reproduces AD6's published +0.1714 within 5e-4
(DEEPDIVE [AD6] L2731) — if G2 fails, STOP.

INFERENCE (house convention, unit = position; each row IS one
position, so the position-cluster bootstrap here degenerates to the
row bootstrap over 586 units — stated, not hidden):
  - continuous: OLS slope of y on neff (raw scale, intercept included;
    the "plain continuous regression" as worded) + 95% percentile
    bootstrap CI over positions; and Spearman rho + 95% position-
    bootstrap CI (house statistic) for each of yE and yT1.
  - decile-binned shape: neff deciles (pd.qcut 10, ties dropped),
    mean yE and mean yT1 per decile + bootstrap CI of each mean.
    Edges computed once on the full frame and FROZEN for the draws.
  - LEVERAGE CHECK: drop the 124 highest-Neff positions, defined as
    neff > max(neff among region-4 positions) — the same cut B2c used
    (RELIABILITY_LOG L836: "POOLED-in-region4-range: n=462", i.e. 124
    excluded). Pre-registered expectation: kept n = 462. If the actual
    count differs from 462 it is printed and DISCLOSED, not adjusted.
    Recompute slope + rho (yE and yT1) with CIs on the kept set and
    report with/without side by side. N_BOOT env (default 10000),
    seed 0.

X2 BOUNDARIES (fixed before running):
  region edges: 147|148, 294|295, 474|475 (scripts/lib/regions.py,
    REGION_BOUNDS {1:(2,147), 2:(148,294), 3:(295,474), 4:(475,656)},
    provenance: primer file via 2nd author, Sept 2026).
  domain edges: Pfam PF02219 MTHFR catalytic 48-337; PF21895 MTHFR_C
    SAM-binding regulatory 344-644 — both ranges fetched live from the
    InterPro API v110.0 on 2026-09-26 (entry pfam/PF02219 and
    pfam/PF21895, protein P42898). Domain edge = 337|344 (6-residue
    linker 338-343).
  coincidence criterion (pre-stated): an edge pair "coincides" iff the
    two boundaries are within 5 residues of each other.
  BREAK TEST: for each candidate boundary b in {147, 294, 337, 474}:
    rho(yE, neff) on positions <= b and on positions > b (for the
    domain edge: <=337 vs >=344, dropping the 338-343 linker, count
    printed), each with a position-bootstrap 95% CI. The boundary at
    which the sign/CI pattern actually changes is where the effect
    breaks. Reported for all four regardless of outcome; no boundary
    is chosen post hoc.

LIMITATIONS printed with output: yE and yT1 are per-position means of
variant-level quantities (no variant-level n here); decile CIs treat
positions as iid (they are, by construction of this frame); the
leverage cut is a Neff cut, not a region cut — region 4 overlaps it
partly (printed); break-test sides have very unbalanced n (printed).

Run: N_BOOT=300 venv/bin/python3 scripts/100_x1_x2_depth_regression_domains.py
Full: N_BOOT=10000 (foreground)
Output: data/processed/task100_x1_depth_regression.csv,
        data/processed/task100_x2_boundary_break.csv
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import _spearman, position_cluster_bootstrap
from scripts.lib.regions import REGION_BOUNDS

PROC = Path("data/processed")

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = N_BOOT <= 500

AD6_RHO = 0.1714
DOMAINS = {"PF02219 catalytic (48-337)": (48, 337),
           "PF21895 regulatory SAM-binding (344-644)": (344, 644)}
REGION_EDGES = [147, 294, 474]     # left side ends; edge pairs x|x+1
BREAK_B = [147, 294, 337, 474]
COINCIDE_TOL = 5                   # residues, pre-stated


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def slope(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    vx = x.var()
    if vx == 0 or len(x) < 3:
        return np.nan
    return float(np.cov(x, y, ddof=0)[0, 1] / vx)


def boot_stat(df, fn, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    a = df.to_numpy()
    nrow = len(a)
    vals = np.empty(n)
    for i in range(n):
        vals[i] = fn(a[rng.integers(0, nrow, nrow)])
    return vals


def summarize(label, df, xcol, ycol, rows, task):
    x, y = df[xcol].to_numpy(float), df[ycol].to_numpy(float)
    b = slope(x, y)
    # bootstrap the slope on the NAMED columns only (pos/region being
    # columns 0/1 of the full frame made the first smoke run's CI garbage)
    xy = df[[xcol, ycol]]
    rb = boot_stat(xy, lambda a: slope(a[:, 0], a[:, 1]))
    lo, hi = np.nanpercentile(rb, [2.5, 97.5])
    r = position_cluster_bootstrap(df, "position", ycol, xcol,
                                   n_boot=N_BOOT, seed=SEED)
    log(f"  {label}: slope={b:+.6e} CI=[{lo:+.6e}, {hi:+.6e}] | "
        f"rho={r['observed_rho']:+.6f} CI=[{r['ci_lo']:+.6f}, "
        f"{r['ci_hi']:+.6f}] p={r['p_boot']:.4f} n={r['n_rows']}")
    rows.append({"task": task, "set": label, "stat": "slope",
                 "value": b, "ci_lo": lo, "ci_hi": hi,
                 "n": r["n_rows"]})
    rows.append({"task": task, "set": label, "stat": "rho",
                 "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                 "ci_hi": r["ci_hi"], "p_boot": r["p_boot"],
                 "n": r["n_rows"]})
    return b, r


def main():
    log(f"script 100 | N_BOOT={N_BOOT} seed={SEED} "
        f"started {time.strftime('%Y-%m-%d %H:%M:%S')}")
    d = pd.read_csv(PROC / "task79_depth_positions.csv")
    n = len(d)
    log(f"G1 frame: {n} rows, positions unique="
        f"{d['position'].is_unique}, neff finite={np.isfinite(d.neff).all()} "
        f"in [{d.neff.min():.1f}, {d.neff.max():.1f}] (bounds [1, 4783])")
    if n != 586 or not d["position"].is_unique:
        gfail("G1 FAILED: frame is not the published 586 positions")
    if not (np.isfinite(d.neff).all() and d.neff.min() >= 1
            and d.neff.max() <= 4783):
        gfail("G1 FAILED: neff outside script 79's measured bounds")

    g2 = _spearman(d["yE"].to_numpy(), d["neff"].to_numpy())
    log(f"G2 pooled rho(yE, neff) = {g2:+.6f} (AD6 published +0.1714, "
        f"tol 5e-4)")
    if abs(g2 - AD6_RHO) > 5e-4:
        gfail("G2 FAILED: AD6's pooled depth result not reproduced")

    rows = []

    # ================= X1 =================
    log("\n==== X1 continuous regression: yE and yT1 vs neff "
        "(raw-scale slope + Spearman, position bootstrap) ====")
    summarize("all 586 positions", d, "neff", "yE", rows, "X1")
    summarize("all 586 positions", d, "neff", "yT1", rows, "X1")

    log("\n  X1 decile-binned shape (frozen decile edges, mean per decile):")
    try:
        d["dec"] = pd.qcut(d["neff"], 10, duplicates="drop")
    except ValueError as e:
        gfail(f"decile cut failed: {e}")
    log("    dec  neff_range            n   mean_yE  CI_yE_lo CI_yE_hi"
        "   mean_yT1 CI_lo  CI_hi")
    for k, grp in d.groupby("dec", observed=True):
        rng = np.random.default_rng(SEED)
        a = grp[["yE", "yT1"]].to_numpy()
        bs = np.array([a[rng.integers(0, len(a), len(a))].mean(axis=0)
                       for _ in range(N_BOOT)])
        lo_e, hi_e = np.percentile(bs[:, 0], [2.5, 97.5])
        lo_t, hi_t = np.percentile(bs[:, 1], [2.5, 97.5])
        iv = str(k)
        log(f"    {iv:<22} {len(grp):>4}  {grp.yE.mean():>8.4f} "
            f"{lo_e:>8.4f} {hi_e:>8.4f}   {grp.yT1.mean():>8.4f} "
            f"{lo_t:>6.4f} {hi_t:>6.4f}")
        rows.append({"task": "X1dec", "set": iv, "stat": "mean_yE",
                     "value": grp.yE.mean(), "ci_lo": lo_e,
                     "ci_hi": hi_e, "n": len(grp)})
        rows.append({"task": "X1dec", "set": iv, "stat": "mean_yT1",
                     "value": grp.yT1.mean(), "ci_lo": lo_t,
                     "ci_hi": hi_t, "n": len(grp)})

    r4max = float(d.loc[d["region"] == 4, "neff"].max())
    keep = d[d["neff"] <= r4max].copy()
    drop = d[d["neff"] > r4max]
    log(f"\n  X1 LEVERAGE CUT (pre-registered: neff <= region-4 max):")
    log(f"    region-4 max neff = {r4max:.1f}; kept n={len(keep)}, "
        f"dropped n={len(drop)} (B2c expectation: kept 462 / dropped 124)"
        + ("" if (len(keep), len(drop)) == (462, 124)
           else "  <-- DIFFERS FROM 462/124: DISCLOSED, not adjusted"))
    log("  X1 with/without the 124 highest-Neff positions, side by side:")
    summarize(f"without top-{len(drop)} (n={len(keep)})", keep,
              "neff", "yE", rows, "X1lev")
    summarize(f"without top-{len(drop)} (n={len(keep)})", keep,
              "neff", "yT1", rows, "X1lev")

    # ================= X2 =================
    log("\n==== X2 region edges vs domain edges ====")
    log("  region edges (scripts/lib/regions.py): "
        + ", ".join(f"{e}|{e+1}" for e in REGION_EDGES))
    log("  domain edge (InterPro API v110.0, fetched 2026-09-26): "
        "337|344 (PF02219 48-337 / PF21895 344-644; linker 338-343)")
    gaps = [abs(337 - e) for e in REGION_EDGES] + \
           [abs(344 - (e + 1)) for e in REGION_EDGES]
    gmin = min(gaps)
    log(f"  distance domain edge -> nearest region edge: {gmin} residues "
        f"(pre-stated coincidence tolerance {COINCIDE_TOL}) -> "
        f"{'COINCIDE' if gmin <= COINCIDE_TOL else 'DO NOT COINCIDE'}")

    log("\n  break test: rho(yE, neff) on each side of each boundary:")
    x2rows = []
    for b in BREAK_B:
        lo_side = d[d["position"] <= b]
        if b == 337:
            hi_side = d[d["position"] >= 344]
            gap = d[(d["position"] > 337) & (d["position"] < 344)]
            extra = f" (linker 338-343 dropped: n={len(gap)})"
        else:
            hi_side = d[d["position"] > b]
            extra = ""
        for lbl, sub in [(f"pos<= {b}", lo_side),
                         (f"pos>= {b+1 if b != 337 else 344}", hi_side)]:
            r = position_cluster_bootstrap(sub, "position", "yE", "neff",
                                           n_boot=N_BOOT, seed=SEED)
            log(f"    b={b:>3} {lbl:<12}: rho={r['observed_rho']:+.6f} "
                f"CI=[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}] "
                f"p={r['p_boot']:.4f} n={r['n_rows']}"
                + (extra if lbl.startswith(f"pos>= {b+1}") or b == 337
                   else ""))
            x2rows.append({"boundary": b, "side": lbl,
                           "rho": r["observed_rho"],
                           "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"],
                           "p_boot": r["p_boot"], "n": r["n_rows"]})

    # ADJUDICATION: the pre-registered four boundaries flip sign at BOTH
    # 337|344 (domain) and 474|475 (region 4). Which boundary does what
    # can only be read off the segments BETWEEN consecutive pre-registered
    # boundaries -- computed here as one systematic set (all segments
    # between {147, 294, 337, 474}), not cherry-picked.
    SEGMENTS = [("2-147", -1, 147), ("148-294", 148, 294),
                ("295-337", 295, 337), ("344-474", 344, 474),
                ("475-656", 475, 999)]
    for lbl, lo, hi in SEGMENTS:
        seg = d[(d["position"] >= lo) & (d["position"] <= hi)]
        if len(seg) < 5:
            continue
        rseg = position_cluster_bootstrap(seg, "position", "yE", "neff",
                                          n_boot=N_BOOT, seed=SEED)
        log(f"\n  SEGMENT {lbl}: rho={rseg['observed_rho']:+.6f} "
            f"CI=[{rseg['ci_lo']:+.6f}, {rseg['ci_hi']:+.6f}] "
            f"p={rseg['p_boot']:.4f} n={rseg['n_rows']}")
        x2rows.append({"boundary": f"seg{lbl}", "side": "between",
                       "rho": rseg["observed_rho"],
                       "ci_lo": rseg["ci_lo"], "ci_hi": rseg["ci_hi"],
                       "p_boot": rseg["p_boot"], "n": rseg["n_rows"]})

    log("\n  X2 VERDICT (rule pre-registered: report where the sign/CI "
        "pattern changes):")
    pos_pos = [x for x in x2rows
               if x["ci_lo"] > 0]      # CI strictly positive
    neg_sides = [x for x in x2rows if x["ci_hi"] < 0]
    for x in x2rows:
        tag = ("positive" if x["ci_lo"] > 0 else
               "negative" if x["ci_hi"] < 0 else "includes 0")
        log(f"    b={x['boundary']} {x['side']:<12}: {tag}")
    log("  (stated from the four boundaries as computed; no boundary "
        "chosen post hoc)")

    out1 = PROC / "task100_x1_depth_regression.csv"
    pd.DataFrame(rows).to_csv(out1, index=False)
    out2 = PROC / "task100_x2_boundary_break.csv"
    pd.DataFrame(x2rows).to_csv(out2, index=False)
    log(f"\nSaved: {out1} ({len(rows)} rows), {out2} ({len(x2rows)} rows)")
    log(f"finished {time.strftime('%Y-%m-%d %H:%M:%S')}"
        + ("  [SMOKE - not quotable]" if SMOKE else "  [FULL RUN]"))


if __name__ == "__main__":
    main()
