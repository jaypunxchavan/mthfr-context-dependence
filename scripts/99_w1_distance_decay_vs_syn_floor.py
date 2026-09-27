"""
Script 99 (task W1 of DISATTENUATION_AND_LEDGER.md, Group W):

  Does |own_e_b| decay with distance from residue 222, or is the apparent
  decay indistinguishable from the synonymous noise floor? Plus the
  distance-stratified version of the primary correlation the task asks
  for as a sensitivity check.

PRE-REGISTERED (this docstring written before any run; AGENTS 6)
------------------------------------------------------------------
FRAMES (all reused, not rewritten):
  analysis = data/processed/task32_analysis_table.csv dropna(own_e_b,
             GI_folinate_independent, delta_esm) -> 10757 rows / 654
             positions (script 32's frozen set, gate G1).
  syn      = data/raw/mthfrModel/results/folate_response_model5.csv with
             own_e_b rebuilt via scripts.lib.stats_ext.rebuild_
             interaction_fit, rows type=="synonymous" (script 47
             L130-146 / script 98 convention) -> 570 rows (gate G4).
  dist_222 = task32's own column; verified against |position - 222|
             on every row (gate G3). Syn rows get |start - 222|.

DISTANCE BANDS (fixed here before running, from the project's known
<=25 locality split): B1 = dist <= 25; B2 = 26..100; B3 = > 100.

STATISTICS (Spearman throughout, house convention; position-cluster
bootstrap via scripts.lib.stats.position_cluster_bootstrap, N_BOOT
from env default 10000, seed 0):
  W1a1  rho(|own_e_b|, dist_222) on analysis rows  + 95% CI
  W1a2  rho(|own_e_b|, dist_222) on syn rows        + 95% CI   <- floor
  W1a3  mean/sd |own_e_b| per band, analysis vs syn (descriptive curve)
  W1b   rho(delta_esm, own_e_b) within each band    + 95% CI + n
        (the distance-stratified primary; pooled value gated in G2)
  W1c   rho(|delta_esm|, dist_222) on analysis rows + 95% CI
        (context: the known negative |delta_ESM|-vs-distance finding,
         printed here so the interaction the task names is on record)

VERDICT RULE (stated before running): the decay is reported as real
structure only if W1a1's 95% CI excludes 0; how it compares to the
floor is stated from W1a1 vs W1a2 side by side (a syn CI that also
excludes zero does NOT get explained away -- it is printed and
disclosed as an equally real floor-side gradient). No band or
threshold is chosen after seeing results.

LIMITATIONS printed with the output (AGENTS 6): syn n=570 across its
own positions gives a wide CI -- wide is informative, it brackets the
floor; bands are unbalanced by construction (distance is a position
property); W1c is context, not a new claim.

Run: N_BOOT=300 venv/bin/python3 scripts/99_w1_distance_decay_vs_syn_floor.py
Full: N_BOOT=10000 (foreground)
Output: data/processed/task_W1_distance_stratified.csv
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import _spearman, position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit

PROC = Path("data/processed")
RAW = Path("data/raw/mthfrModel")

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = N_BOOT <= 500

RHO_PUB = -0.08811806424891734
SYN_N_PUB = 570
BANDS = [("B1 dist<=25", -1, 25), ("B2 dist 26-100", 25, 100),
         ("B3 dist>100", 100, 10**9)]


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def boot_ci(df, x, y, label):
    r = position_cluster_bootstrap(df, "position", x, y,
                                   n_boot=N_BOOT, seed=SEED)
    log(f"  {label}: rho={r['observed_rho']:+.6f}  "
        f"CI=[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}]  "
        f"p_boot={r['p_boot']:.4f}  n={r['n_rows']} "
        f"positions={r['n_clusters']}")
    return r


def main():
    log(f"script 99 | N_BOOT={N_BOOT} seed={SEED} "
        f"started {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # ---------------- frames -------------------------------------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(
        subset=["own_e_b", "GI_folinate_independent", "delta_esm"]
    ).copy()
    log(f"G1 base frame: {len(base)} rows / {base['position'].nunique()} "
        f"positions (expect 10757 / 654)")
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail("G1 FAILED: base frame differs from script 32's frozen set")

    obs = _spearman(base["delta_esm"].to_numpy(),
                    base["own_e_b"].to_numpy())
    log(f"G2 pooled primary rho: {obs!r} (want {RHO_PUB!r})")
    if abs(obs - RHO_PUB) > 1e-9:
        gfail("G2 FAILED: pooled headline rho not reproduced")

    dchk = np.abs(t32["dist_222"].to_numpy(int)
                  - np.abs(t32["position"].to_numpy(int) - 222)).max()
    log(f"G3 dist_222 == |position-222| on all {len(t32)} rows: "
        f"max|diff|={dchk}")
    if dchk != 0:
        gfail("G3 FAILED: dist_222 column is not |position-222|")

    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    syn = pd.DataFrame({"position": raw["start"].to_numpy(int),
                        "type": raw["type"].to_numpy(),
                        "own_e_b": fit["e2"]["e_b"]})
    syn = syn[(syn["type"] == "synonymous")].dropna(subset=["own_e_b"])
    syn["dist_222"] = np.abs(syn["position"].to_numpy(int) - 222)
    log(f"G4 syn frame: {len(syn)} rows (want {SYN_N_PUB}), "
        f"positions={syn['position'].nunique()}, "
        f"var={np.var(syn['own_e_b'], ddof=1):.5f} (script 98: 0.02111)")
    if len(syn) != SYN_N_PUB:
        gfail("G4 FAILED: syn row count differs from script 98's G5")

    base["abs_own"] = base["own_e_b"].abs()
    syn["abs_own"] = syn["own_e_b"].abs()
    base["abs_delta"] = base["delta_esm"].abs()

    rows = []

    # ---------------- W1a ----------------------------------------------
    log("\n==== W1a: |own_e_b| vs distance, analysis vs syn floor ====")
    r_ana = boot_ci(base, "abs_own", "dist_222", "W1a1 analysis")
    r_syn = boot_ci(syn, "abs_own", "dist_222", "W1a2 syn (floor)")
    rows += [
        {"task": "W1a1", "stat": "rho(|own_e_b|, dist)_analysis",
         "value": r_ana["observed_rho"], "ci_lo": r_ana["ci_lo"],
         "ci_hi": r_ana["ci_hi"], "p_boot": r_ana["p_boot"],
         "n": r_ana["n_rows"], "n_pos": r_ana["n_clusters"]},
        {"task": "W1a2", "stat": "rho(|own_e_b|, dist)_syn",
         "value": r_syn["observed_rho"], "ci_lo": r_syn["ci_lo"],
         "ci_hi": r_syn["ci_hi"], "p_boot": r_syn["p_boot"],
         "n": r_syn["n_rows"], "n_pos": r_syn["n_clusters"]},
    ]

    log("  W1a3 distance curve (mean|own_e_b| per band, analysis vs syn):")
    log("    band              ana_n ana_pos ana_mean ana_sd | "
        "syn_n syn_pos syn_mean syn_sd")
    for lbl, lo, hi in BANDS:
        a = base[(base["dist_222"] > lo) & (base["dist_222"] <= hi)]
        s = syn[(syn["dist_222"] > lo) & (syn["dist_222"] <= hi)]
        log(f"    {lbl:<15} {len(a):>5} {a['position'].nunique():>7} "
            f"{a['abs_own'].mean():>8.4f} {a['abs_own'].std():>7.4f} | "
            f"{len(s):>5} {s['position'].nunique():>7} "
            f"{s['abs_own'].mean() if len(s) else float('nan'):>8.4f} "
            f"{s['abs_own'].std() if len(s) else float('nan'):>7.4f}")
        rows.append({"task": "W1a3", "stat": f"mean|own_e_b| {lbl}",
                     "value": a["abs_own"].mean(), "ci_lo": np.nan,
                     "ci_hi": np.nan, "p_boot": np.nan,
                     "n": len(a), "n_pos": a["position"].nunique()})

    # ---------------- W1b ----------------------------------------------
    log("\n==== W1b: distance-stratified primary (delta_esm vs own_e_b) ====")
    for lbl, lo, hi in BANDS:
        b = base[(base["dist_222"] > lo) & (base["dist_222"] <= hi)]
        r = boot_ci(b, "delta_esm", "own_e_b", f"W1b {lbl}")
        rows.append({"task": "W1b", "stat": f"rho(delta, own) {lbl}",
                     "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "p_boot": r["p_boot"],
                     "n": r["n_rows"], "n_pos": r["n_clusters"]})

    # ---------------- W1c ----------------------------------------------
    log("\n==== W1c: context — |delta_esm| vs distance (known negative) ====")
    r_c = boot_ci(base, "abs_delta", "dist_222", "W1c |delta_esm|,dist")
    rows.append({"task": "W1c", "stat": "rho(|delta_esm|, dist)",
                 "value": r_c["observed_rho"], "ci_lo": r_c["ci_lo"],
                 "ci_hi": r_c["ci_hi"], "p_boot": r_c["p_boot"],
                 "n": r_c["n_rows"], "n_pos": r_c["n_clusters"]})

    # ---------------- verdict ------------------------------------------
    log("\n==== W1 VERDICT (rule pre-registered in docstring) ====")
    ana_excl0 = r_ana["ci_hi"] < 0 or r_ana["ci_lo"] > 0
    syn_excl0 = r_syn["ci_hi"] < 0 or r_syn["ci_lo"] > 0
    log(f"  analysis rho(|own_e_b|,dist) = {r_ana['observed_rho']:+.6f} "
        f"CI [{r_ana['ci_lo']:+.6f}, {r_ana['ci_hi']:+.6f}] -> "
        f"{'EXCLUDES' if ana_excl0 else 'includes'} 0")
    log(f"  syn      rho(|own_e_b|,dist) = {r_syn['observed_rho']:+.6f} "
        f"CI [{r_syn['ci_lo']:+.6f}, {r_syn['ci_hi']:+.6f}] -> "
        f"{'EXCLUDES' if syn_excl0 else 'includes'} 0 (the floor)")
    if ana_excl0 and not syn_excl0:
        log("  -> |e.b| decays with distance beyond the syn noise floor.")
    elif ana_excl0 and syn_excl0:
        log("  -> BOTH sides show a distance gradient: the floor itself "
            "has distance structure; the analysis-side decay cannot be "
            "called pure signal without the two magnitudes compared "
            "(printed above; compare |rho| ana vs syn directly).")
    elif not ana_excl0:
        log("  -> analysis-side |e.b| does NOT show a CI-excluding-zero "
            "distance gradient. Stated plainly: no decay claim.")
    log("  LIMITATION: syn CI is wide (570 rows across its positions); "
        "bands unbalanced by construction; W1c is context only.")

    out = PROC / "task_W1_distance_stratified.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"\nSaved: {out}  ({len(rows)} rows)")
    log(f"finished {time.strftime('%Y-%m-%d %H:%M:%S')}"
        + ("  [SMOKE - not quotable]" if SMOKE else "  [FULL RUN]"))


if __name__ == "__main__":
    main()
