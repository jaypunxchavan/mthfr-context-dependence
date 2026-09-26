"""
Task B2 (reliability-and-decompositions): is the region-4 depth
reversal (rho(yE, Neff) = -0.2373 vs pooled +0.1714) composition or a
real effect?

PRE-REGISTRATION (written before any number below existed; AGENTS s0/s6)

INPUT (frozen): data/processed/task79_depth_positions.csv — one row per
position, 586 rows, columns position, region, neff, cons, yE (= mean
|delta_esm| per position), produced by script 79 (never recomputed
here; script 79's own outputs are the anchor).

RECORD VALUES QUOTED AS CONSTANTS (source cited, recomputed as gates):
  pooled  rho(yE, neff) = +0.1714 CI [+0.0918, +0.2471]  (DEEPDIVE_LOG
          L2731, script 79 rule R1)
  region4 rho(yE, neff) = -0.2373 CI [-0.3795, -0.0853]
          p_boot=0.0042 n=169            (DEEPDIVE_LOG L2717)

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 region sizes exactly {1: 108, 2: 135, 3: 174, 4: 169}, total 586
     (script 79's own G5 counts; the task text's "169 positions" for
     region 4 is checked, not assumed).
  G2 recomputed raw rhos must match the record values to 5e-4
     (4-dp rounding tolerance, same convention as scripts 78/93).

B2a — Spearman(Neff, conservation) pooled + within each region, PLUS a
  direct region-4-vs-rest comparison:
    scopes: pooled, region1..region4, and REST (regions 1-3, n=417).
    each rho with position-cluster bootstrap CI (house
    position_cluster_bootstrap, N_BOOT draws, seed 0).
    "DIFFERS" (pre-registered): region-4 rho's 95% CI excludes the
    REST rho (or REST's CI excludes region-4's) — otherwise the
    Neff-conservation relationship does not demonstrably differ and
    composition is NOT indicated by this test.

B2b — partial correlation of yE against Neff controlling for
  conservation, pooled and within region 4, via the house
  partial_spearman_cluster_bootstrap (single covariate, position
  cluster, N_BOOT, seed 0). Compared against the raw values above.
  Verdict (pre-registered):
    region-4 reversal SURVIVES the conservation control iff the
    region-4 partial rho is negative AND its 95% CI excludes 0;
    otherwise the reversal is not robust to controlling conservation
    (reported plainly either way).

B2c — range restriction + nonlinearity check for region 4:
    (1) Neff distribution for pooled / region4 / rest: min, q25,
        median, q75, max, sd; region-4 range width as a fraction of
        the pooled range; fraction of ALL positions whose Neff falls
        inside region 4's observed Neff range (how selective is the
        slice); region 4's median Neff percentile in the pooled
        distribution.
    (2) POOLED-in-region4-range: Spearman(neff, yE) on pooled rows
        restricted to region 4's exact [min, max] Neff interval, with
        position-cluster CI (same machinery).
    (3) Descriptive shape: pooled Neff deciles with mean/median yE per
        decile (no CI, labeled descriptive).
  Verdict (pre-registered):
    "range restriction + nonlinearity COULD produce the reversal"
      iff pooled-in-region-4-range rho < 0 (i.e. the globally positive
      relationship already turns non-positive inside the slice region 4
      occupies — then a negative within-slice correlation can arise
      without any region-specific effect);
    otherwise "NOT explained by the slice alone": the pooled rows in
    the same Neff range stay [sign] while region 4 alone is negative,
    so the reversal is region-specific beyond range restriction.
  Both numbers + the decile table are printed regardless.

LIMITATIONS (printed with results, AGENTS s6):
  - All quantities are position-level (n=586 rows) — no variant-level
    pseudoreplication enters; CIs are position bootstraps.
  - partial_spearman handles ONE covariate (conservation) — it is the
    house single-covariate partial, not a multivariable model.
  - B2c's deciles are descriptive; no CI or test is attached to them.
  - Region boundaries are scripts.lib.regions' provenance (real
    boundaries, not inferred) — region identity is taken as given.

Run:  SMOKE=1 N_BOOT=300 venv/bin/python3 scripts/94_...  (timed)
      full: N_BOOT=10000 venv/bin/python3 scripts/94_...
Output: data/processed/task94_b2_depth_reversal.csv
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import (position_cluster_bootstrap,
                               partial_spearman_cluster_bootstrap,
                               _spearman)

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = os.environ.get("SMOKE", "") == "1"

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
CSV = PROC / "task79_depth_positions.csv"

REC_POOL, REC_R4 = 0.1714, -0.2373     # record values (cited above)
TOL = 5e-4
EXPECT_SIZES = {1: 108, 2: 135, 3: 174, 4: 169}


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def rho_ci(d, x, y):
    b = position_cluster_bootstrap(d, "position", x, y, n_boot=N_BOOT,
                                   seed=SEED)
    return float(b["observed_rho"]), float(b["ci_lo"]), float(b["ci_hi"]), \
        float(b["p_boot"])


def fmt(r, lo, hi, p):
    ps = "<1/N" if p == 0 else f"{p:.4f}"
    return f"rho={r:+.4f} [{lo:+.4f}, {hi:+.4f}] p_boot={ps}"


def main():
    log(f"B2 -- REGION-4 DEPTH REVERSAL: composition vs effect "
        f"(scripts/94) {'SMOKE' if SMOKE else 'FULL'} N_BOOT={N_BOOT}")

    d = pd.read_csv(CSV)
    sizes = {int(k): int(v) for k, v in d.groupby("region")
             .size().to_dict().items()}
    if len(d) != 586 or sizes != EXPECT_SIZES:
        gfail(f"G1 FAIL: rows={len(d)} sizes={sizes} != 586 / "
              f"{EXPECT_SIZES}")
    log(f"G1 region sizes PASS: {sizes}, total {len(d)} "
        f"(task's 'region 4 = 169 positions' confirmed, not assumed)")

    # ---- G2: raw rhos vs record ----
    r_pool, lo_pool, hi_pool, p_pool = rho_ci(d, "neff", "yE")
    r4 = d[d["region"] == 4]
    r_r4, lo_r4, hi_r4, p_r4 = rho_ci(r4, "neff", "yE")
    d_pool = abs(r_pool - REC_POOL)
    d_r4 = abs(r_r4 - REC_R4)
    log(f"G2 raw recomputation: pooled {r_pool:+.4f} vs record "
        f"{REC_POOL:+.4f} (|diff|={d_pool:.2e}); region4 {r_r4:+.4f} vs "
        f"record {REC_R4:+.4f} (|diff|={d_r4:.2e}) -> "
        f"{'OK' if max(d_pool, d_r4) < TOL else 'FAIL'}")
    if max(d_pool, d_r4) >= TOL:
        gfail("G2 FAIL -- recomputed raw rhos disagree with the record")

    # ---- B2a: Neff-conservation, 6 scopes ----
    log("\n" + "=" * 74)
    log("B2a  Spearman(Neff, conservation) pooled + per region + REST")
    log("=" * 74)
    scopes = [("pooled", d)] + [(f"region{int(r)}",
                                 d[d["region"] == r])
                                for r in sorted(d["region"].unique())]
    rest = d[d["region"] != 4]
    scopes.append(("REST(regions1-3)", rest))
    a_rows = []
    a_res = {}
    for name, sub in scopes:
        rr, ll, hh, pp = rho_ci(sub, "neff", "cons")
        a_res[name] = (rr, ll, hh, pp)
        a_rows.append({"section": "B2a", "scope": name, "stat": "neff_cons",
                       "rho": rr, "ci_lo": ll, "ci_hi": hh, "p": pp,
                       "n": len(sub)})
        log(f"  {name:18s} n={len(sub):4d}  {fmt(rr, ll, hh, pp)}")
    rr4, ll4, hh4, _ = a_res["region4"]
    rrst, llst, hhst, _ = a_res["REST(regions1-3)"]
    differs = (rr4 < llst) or (rr4 > hhst) or (rrst < ll4) or (rrst > hh4)
    log(f"  DIFFERS? region4 [{ll4:+.4f},{hh4:+.4f}] vs REST "
        f"[{llst:+.4f},{hhst:+.4f}] -> "
        f"{'DIFFERS (CIs disjoint) -> composition indicated' if differs else 'does NOT demonstrably differ -> composition NOT indicated by this test'}")

    # ---- B2b: partials ----
    log("\n" + "=" * 74)
    log("B2b  partial Spearman(yE, Neff | conservation), pooled + region4")
    log("=" * 74)
    b_rows = []
    part_res = {}
    for name, sub in (("pooled", d), ("region4", r4)):
        b = partial_spearman_cluster_bootstrap(sub, "position", "neff",
                                               "yE", covar_col="cons",
                                               n_boot=N_BOOT, seed=SEED)
        part_res[name] = b
        b_rows.append({"section": "B2b", "scope": name,
                       "stat": "partial_neff_yE_given_cons",
                       "rho": float(b["observed_rho"]),
                       "ci_lo": float(b["ci_lo"]),
                       "ci_hi": float(b["ci_hi"]),
                       "p": float(b["p_boot"]), "n": len(sub)})
        log(f"  {name:8s} partial: " + fmt(float(b["observed_rho"]),
                                            float(b["ci_lo"]),
                                            float(b["ci_hi"]),
                                            float(b["p_boot"])))
    praw_pool, praw_r4 = part_res["pooled"], part_res["region4"]
    log(f"  raw record: pooled {REC_POOL:+.4f} -> partial "
        f"{float(praw_pool['observed_rho']):+.4f} "
        f"(delta {float(praw_pool['observed_rho']) - REC_POOL:+.4f}); "
        f"region4 {REC_R4:+.4f} -> partial "
        f"{float(praw_r4['observed_rho']):+.4f} "
        f"(delta {float(praw_r4['observed_rho']) - REC_R4:+.4f})")
    survives = (float(praw_r4["observed_rho"]) < 0 and
                float(praw_r4["ci_hi"]) < 0)
    log(f"  B2b VERDICT (rule fixed in docstring): region-4 reversal "
        f"{'SURVIVES' if survives else 'does NOT survive'} the "
        f"conservation control (partial rho "
        f"{float(praw_r4['observed_rho']):+.4f}, CI upper "
        f"{float(praw_r4['ci_hi']):+.4f})")

    # ---- B2c: range restriction + nonlinearity ----
    log("\n" + "=" * 74)
    log("B2c  Neff range/distribution in region 4 + slice checks")
    log("=" * 74)

    def dist(sub):
        q = sub["neff"].quantile([0, .25, .5, .75, 1.0])
        return (float(q[0]), float(q[.25]), float(q[.5]), float(q[.75]),
                float(q[1.0]), float(sub["neff"].std()))

    for name, sub in (("pooled", d), ("region4", r4), ("rest", rest)):
        mn, q25, md, q75, mx, sd = dist(sub)
        log(f"  {name:8s} n={len(sub):4d} neff: min={mn:.1f} q25={q25:.1f} "
            f"median={md:.1f} q75={q75:.1f} max={mx:.1f} sd={sd:.1f}")
    pmin, _, pmed, _, pmax, _ = dist(d)
    rmin, _, rmed, _, rmax, _ = dist(r4)
    width_frac = (rmax - rmin) / (pmax - pmin)
    in_range = float(((d["neff"] >= rmin) & (d["neff"] <= rmax)).mean())
    pctile = float((d["neff"] < rmed).mean())
    log(f"  region4 range [{rmin:.1f}, {rmax:.1f}] = {width_frac:.1%} of "
        f"pooled [{pmin:.1f}, {pmax:.1f}] range")
    log(f"  {in_range:.1%} of ALL positions fall inside region 4's Neff "
        f"range (slice selectivity); region-4 median Neff = {pctile:.1%} "
        f"percentile of pooled")

    slice_d = d[(d["neff"] >= rmin) & (d["neff"] <= rmax)]
    rs, ls, hs, ps = rho_ci(slice_d, "neff", "yE")
    c_rows = [{"section": "B2c", "scope": "pooled_in_r4_range",
               "stat": "neff_yE", "rho": rs, "ci_lo": ls, "ci_hi": hs,
               "p": ps, "n": len(slice_d)}]
    log(f"  POOLED-in-region4-range: n={len(slice_d)}  "
        f"{fmt(rs, ls, hs, ps)}")

    dec = pd.qcut(d["neff"], 10, labels=False, duplicates="drop")
    log("  pooled Neff deciles (descriptive): dec_lo dec_hi  n   mean_yE  "
        "median_yE")
    for i in sorted(dec.unique()):
        sub = d[dec == i]
        log(f"    decile {int(i)+1:2d}: {sub['neff'].min():7.1f} "
            f"{sub['neff'].max():7.1f} {len(sub):4d}  "
            f"{sub['yE'].mean():+.5f}  {sub['yE'].median():+.5f}")

    plausible = rs < 0
    if plausible:
        verdict = ("range restriction + nonlinearity COULD produce the "
                   "reversal: even the pooled rows inside region 4's own "
                   "Neff range correlate non-positively with yE")
    else:
        verdict = (f"NOT explained by the slice alone: pooled rows in the "
                   f"same Neff range correlate {rs:+.4f} while region 4 "
                   f"alone is {r_r4:+.4f} -> region-specific beyond range "
                   f"restriction")
    log(f"  B2c VERDICT (rule fixed in docstring): {verdict}")

    # ---- save ----
    out = PROC / ("task94_b2_smoke.csv" if SMOKE
                  else "task94_b2_depth_reversal.csv")
    rows = a_rows + b_rows + c_rows
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"\n[saved] {out}")
    log("\nLIMITATIONS: position-level frame only (n=586); house "
        "single-covariate partial; deciles descriptive without CI; "
        "region identity from scripts.lib.regions provenance; raw "
        "values recomputed here match script 79's record to <5e-4 "
        "(G2), and all comparisons above are the ONLY pre-registered "
        "ones.")
    if SMOKE:
        log("*** SMOKE RUN: machinery only, NOT findings. ***")
    log("SCRIPT 94 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
