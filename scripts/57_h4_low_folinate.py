"""
Task H4 (review-triage): does 6.3's high-stratum result hold at LOW
FOLINATE specifically? [item 30]

H4a: Does 6.3's high-stratum result hold specifically at low folinate
(where A222V's phenotype is most expressed), or is it diluted by
averaging across all four conditions?

WHAT 6.3 WAS (script 34 / MTHFR_RESULTS_LOG 6.3)
-------------------------------------------------
Pooled phenotype target (f_bar_a222v = exact mean of the four per-
condition A222V-arm scores, verified to 2.2e-16): cross-fitted isotonic
pred_C (ESM-2, A222V background) vs the multiplicative no-interaction
null pred_mult (cross-fitted model_A -> f_bar_wt, times A, where A =
A222V's own WT-arm fitness). Strata = pd.qcut(|e.b|, 3). HIGH stratum:
MAE(ESM-2) - MAE(null) = +0.002409, CI [+0.001551, +0.003208], n=3,586
-- ESM-2 reliably WORSE than assuming no interaction.

PRE-REGISTERED DESIGN (stated before running -- AGENTS.md §6)
--------------------------------------------------------------
GATE (sanity, exit 1 on failure, no retry): rebuild script 34's pooled
machinery exactly (same crossfit calls, same seeds, same stratum
construction) and reproduce the on-disk task34_additive_null.csv
gi_high row: observed diff to |delta| <= 1e-6 always (deterministic);
both CI endpoints additionally checked to 1e-6 when N_BOOT == 2000 (the
on-disk run's draw count -- CIs are seed-stable but NOT draw-count-
stable; at smoke N_BOOT the CI check is deferred and SAYS SO, while the
observed-value check still gates).

Per-condition extension (the whole point of H4), for c in
{12, 25, 100, 200}:
  target_c  = m{c}.score        (measured A222V-arm fitness at c)
  w_hat_c   = crossfit(model_A -> w{c}.score)     (position-held-out)
  A_c       = w{c}.score of p.Ala222Val, read from PHASE3 (phase5 has no
              A222V row; same source script 34 used for pooled A;
              exit 1 if missing)
  pred_A_c  = crossfit(model_A -> target_c)
  pred_C_c  = crossfit(model_C -> target_c)
  null_c    = pred_mult_c = w_hat_c * A_c          (multiplicative, per c)
  Rows: pooled-6.3 analysis set (so the stratum definition and the
  comparison population stay identical to 6.3) INTERSECTED with
  non-null w{c} and m{c}; every drop printed (AGENTS §5).
  Statistic: paired MAE difference, pred_C_c vs pred_mult_c
  (= MAE(ESM-2) - MAE(null); positive = ESM-2 worse), position-cluster
  bootstrap, per stratum.

PRIMARY test (single, pre-registered): HIGH stratum at condition 12
(lowest folinate).
  HOLDS-AT-LOW-FOLINATE iff its CI excludes 0 on the POSITIVE side
  (replicating 6.3's direction at low folinate).
  REVERSED iff CI excludes 0 negative.
  NOT-CONFIRMED-AT-LOW-FOLINATE otherwise (incl. CI crossing 0).
Conditions 25/100/200 and the low/mid strata are REPORTED as the
dilution context (labeled descriptive; no retuning from them).

Scale check (stated, not assumed): f_bar_a222v is EXACTLY mean(m12,
m25, m100, m200) and f_bar_wt exactly mean(w12..w200) over rows with
all four present (verified during design, max|diff| <= 4.4e-16), so
per-condition targets/nulls live on the same scale as the pooled ones.

Env: N_BOOT (default 2000). Smoke with 50-100.
Output: data/processed/task57_h4_per_condition.csv
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import crossfit_isotonic_by_position
from scripts.lib.stats_ext import paired_metric_difference_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
CONDS = [12, 25, 100, 200]


def build_pool():
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    n0 = len(df)
    df = df.dropna(subset=["model_A", "model_C", "target",
                           "f_bar_wt"]).reset_index(drop=True)
    print(f"phase5 rows {n0} -> pooled 6.3 set {len(df)} "
          f"(dropna model_A/model_C/target/f_bar_wt: -{n0 - len(df)})")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    p3 = pd.read_csv(PROC / "phase3_analysis_table.csv")
    a_row = p3[p3["hgvs_pro"] == "p.Ala222Val"]
    if len(a_row) == 0 or a_row["f_bar_wt"].isna().all():
        print("*** p.Ala222Val / f_bar_wt missing in phase3. sys.exit(1)")
        sys.exit(1)
    A = float(a_row["f_bar_wt"].dropna().iloc[0])
    df["pred_A"] = crossfit_isotonic_by_position(df, "position", "model_A",
                                                 "target", n_folds=5,
                                                 seed=SEED)
    w_hat = crossfit_isotonic_by_position(df, "position", "model_A",
                                          "f_bar_wt", n_folds=5, seed=SEED)
    df["pred_C"] = crossfit_isotonic_by_position(df, "position", "model_C",
                                                 "target", n_folds=5,
                                                 seed=SEED)
    df["w_hat"] = w_hat
    df["pred_mult"] = df["w_hat"] * A
    d = df.dropna(subset=["pred_A", "pred_C", "pred_mult", "target"]).copy()
    s = d.dropna(subset=["abs_gi"]).copy()
    s["stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    return d, s, A, p3, a_row


def gate_pooled(s):
    ref = pd.read_csv(PROC / "task34_additive_null.csv")
    ref_row = ref[(ref["stage"] == "stratified_mae") &
                  (ref["predictor"] == "gi_high")].iloc[0]
    hi = s[s["stratum"] == "high"]
    r = paired_metric_difference_bootstrap(hi, "position", "pred_mult",
                                           "pred_C", "target",
                                           metric="mae", n_boot=N_BOOT,
                                           seed=SEED)
    d_obs = abs(r["observed_diff"] - ref_row["diff"])
    d_lo = abs(r["ci_lo"] - ref_row["ci_lo"])
    d_hi = abs(r["ci_hi"] - ref_row["ci_hi"])
    # observed_diff is deterministic (independent of N_BOOT); CI endpoints
    # are only expected to reproduce bit-stable at the on-disk run's
    # N_BOOT=2000 with the same seed, so CI checking is conditional.
    check_ci = (N_BOOT == 2000)
    ok = d_obs <= 1e-6 and ((d_lo <= 1e-6 and d_hi <= 1e-6) or not check_ci)
    ci_note = (f"max|delta| obs/lo/hi = {d_obs:.2e}/{d_lo:.2e}/{d_hi:.2e} "
               f"(tol 1e-6)" if check_ci else
               f"max|delta| obs = {d_obs:.2e} (tol 1e-6); CI check deferred "
               f"-- smoke N_BOOT={N_BOOT} != 2000")
    print(f"GATE rebuild of 6.3 pooled HIGH: "
          f"derived diff={r['observed_diff']:+.6f} "
          f"CI=[{r['ci_lo']:+.6f},{r['ci_hi']:+.6f}] n={r['n_rows']}")
    print(f"        on-disk task34:           diff={ref_row['diff']:+.6f} "
          f"CI=[{ref_row['ci_lo']:+.6f},{ref_row['ci_hi']:+.6f}] "
          f"n={int(ref_row['n'])}")
    print(f"        {ci_note} -> {'OK' if ok else 'FAIL'}")
    if not ok:
        print("*** GATE FAILED -- rebuild does not reproduce 6.3. sys.exit(1)")
        sys.exit(1)
    return r


if __name__ == "__main__":
    d, s, A, p3, a_row = build_pool()
    print(f"pooled analysis set for strata: {len(s)} rows; "
          f"stratum counts: {s['stratum'].value_counts().to_dict()}")
    print("\n" + "=" * 74)
    print("H4: 6.3 machinery re-run per folinate condition")
    print("=" * 74)
    gate_pooled(s)

    rows = []
    primary = None
    for c in CONDS:
        wc, mc = f"w{c}.score", f"m{c}.score"
        a_val = a_row[wc]
        if len(a_val) == 0 or a_val.isna().all():
            print(f"*** A_c for condition {c} missing in phase3. sys.exit(1)")
            sys.exit(1)
        A_c = float(a_val.dropna().iloc[0])
        n_before = len(s)
        f = s.dropna(subset=[wc, mc]).copy()
        n_drop = n_before - len(f)
        f["pred_A_c"] = crossfit_isotonic_by_position(f, "position", "model_A",
                                                      mc, n_folds=5, seed=SEED)
        f["pred_C_c"] = crossfit_isotonic_by_position(f, "position", "model_C",
                                                      mc, n_folds=5, seed=SEED)
        w_hat_c = crossfit_isotonic_by_position(f, "position", "model_A", wc,
                                                n_folds=5, seed=SEED)
        f["pred_mult_c"] = np.asarray(w_hat_c) * A_c
        f = f.dropna(subset=["pred_A_c", "pred_C_c", "pred_mult_c"])
        print(f"\n  condition {c:>3d} ug/ml: A_c={A_c:.4f}  "
              f"rows kept={len(f)} (dropped {n_drop} missing {wc}/{mc}; "
              f"positions={f['position'].nunique()})")
        for lvl in ["low", "mid", "high"]:
            sub = f[f["stratum"] == lvl]
            if sub["position"].nunique() < 15:
                print(f"    {lvl:4s} SKIPPED ({sub['position'].nunique()} positions)")
                continue
            r = paired_metric_difference_bootstrap(sub, "position",
                                                   "pred_mult_c", "pred_C_c",
                                                   mc, metric="mae",
                                                   n_boot=N_BOOT, seed=SEED)
            v = ("ESM-2 WORSE (CI>0)" if r["ci_lo"] > 0 else
                 "ESM-2 BETTER (CI<0)" if r["ci_hi"] < 0 else
                 "crosses 0")
            print(f"    {lvl:4s} (n={len(sub):5d}) "
                  f"MAE(null)={r['metric_a']:.4f} MAE(ESM-2)={r['metric_b']:.4f} "
                  f"diff={r['observed_diff']:+.5f} "
                  f"CI=[{r['ci_lo']:+.5f},{r['ci_hi']:+.5f}]  -> {v}")
            rows.append({"condition": c, "stratum": lvl,
                         "mae_null": r["metric_a"], "mae_esm": r["metric_b"],
                         "diff": r["observed_diff"], "ci_lo": r["ci_lo"],
                         "ci_hi": r["ci_hi"], "n": r["n_rows"],
                         "n_pos": r["n_clusters"], "verdict": v})
            if c == 12 and lvl == "high":
                primary = r

    print("\n" + "=" * 74)
    print("PRE-REGISTERED PRIMARY: HIGH stratum at condition 12 (lowest folinate)")
    print("=" * 74)
    if primary is None:
        print("*** primary cell not computed. sys.exit(1)")
        sys.exit(1)
    if primary["ci_lo"] > 0:
        verdict = "HOLDS-AT-LOW-FOLINATE (ESM-2 worse than null, CI>0)"
    elif primary["ci_hi"] < 0:
        verdict = "REVERSED (ESM-2 better than null at condition 12)"
    else:
        verdict = "NOT-CONFIRMED-AT-LOW-FOLINATE (CI crosses 0)"
    print(f"  diff={primary['observed_diff']:+.5f} "
          f"CI=[{primary['ci_lo']:+.5f},{primary['ci_hi']:+.5f}] "
          f"n={primary['n_rows']} pos={primary['n_clusters']}")
    print(f"  VERDICT: {verdict}")

    out = PROC / "task57_h4_per_condition.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved {out}")
    print("\nLIMITATIONS (script is the record, AGENTS §6): ONE pre-registered")
    print("primary cell (high@12); the other 11 cells are descriptive")
    print("dilution context and must not be read as independent tests")
    print("(no multiple-testing correction claimed for them). Per-condition")
    print("rows are a SUBSET of 6.3's set (condition missingness); drops")
    print("printed. Stratum labels transferred from the pooled 6.3 qcut so")
    print("'high' means exactly what it meant in 6.3. Position-cluster")
    print("bootstrap CIs (AGENTS §3); effect sizes reported with all of them.")
