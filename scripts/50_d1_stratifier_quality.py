"""
Script 50 (Group D — stratifier quality / winner's-curse risk): D1a, D1b, D1c.

WHAT THE REVIEW ASKED (REVIEW_TRIAGE items 15-17)
--------------------------------------------------
D1a. Is the high-|e.b| stratum enriched for high-SE variants? (Ties
     directly to script 35's known SE miscalibration.)
D1b. Rerun 6.3's stratification using an empirical-Bayes shrunken e.b
     instead of raw e.b; does the high-stratum verdict change?
D1c. Add a nonsense-variant noise floor alongside the synonymous floor:
     nonsense variants are dead in both backgrounds so true e.b ~ 0 — a
     second noise-floor check at the OPPOSITE end of the fitness range
     from synonymous variants, which may be heteroscedastic.

PRE-REGISTERED DECISION RULES (fixed here before any run — AGENTS §6)
----------------------------------------------------------------------
D1a PRIMARY: strata = pd.qcut(|GI_folinate_independent|, 3) on the exact
  6.3 set (n=10,757; same rows and rule as script 46's C2c). Statistic
  D = mean(SE | high) - mean(SE | low). CI = position-cluster bootstrap,
  stratum labels FIXED within draws (matching C2c's convention; script
  34's older bootstrap re-quantiled inside draws — not used here).
  Verdict: ENRICHED iff CI_lo > 0; DEPLETED iff CI_hi < 0; else
  NOT DETECTED. Effect size (ratio mean_SE_high / mean_SE_low) printed
  alongside every verdict (AGENTS §3). Secondary, descriptive only:
  Spearman(|GI|, SE) with position-cluster CI, and the share of the
  top-SE tercile falling in each stratum (1/3 each under no enrichment).
  Sensitivity, NOT verdict-bearing: repeat on |own_e_b| strata (own vs
  published stratifier switch is ~82% agreement — quantified, not hidden).

D1b GATES FIRST (each exit 1, no retry): script-34 set n == 11,113;
  G1 pooled MAE diff == PUBLISHED_POOLED (1e-9, proves the local build
  mirror of script 46); identity checks — MAE and MSE bootstrap helpers
  with pred_a == pred_b must give observed_diff exactly 0 (1e-12); s-set
  (dropna abs_gi) n == 10,757 with complete SE join; G2 arm-1 high-stratum
  MAE diff == PUBLISHED_HIGH (1e-9, proves the stratification + verdict
  machinery reproduces 6.3 exactly).
  Three arms, same rows, same preds, only the stratifier variable varies:
    arm1 = |GI_folinate_independent|  (the original 6.3 — gated by G2)
    arm2 = |own_e_b|                  (own-vs-published switch control)
    arm3 = |EB-shrunk own_e_b|        (the task: shrink factor
           tau^2 / (tau^2 + se_e_b^2), tau^2 = var_ddof1(own_e_b) -
           mean(se_e_b^2) on the s-set, method of moments; if tau^2 <= 0
           -> verdict EB-DEGENERATE (legitimate empirical outcome, not a
           crash), arms 1-2 still run). Shrinkage uses ONLY own_e_b and
           its analytic SE — never the target — so it cannot leak into
           the cross-fitted predictions; strata only decide grouping.
  Per arm: high-stratum MAE (stats_ext.paired_metric_difference_bootstrap)
  and MSE (local mirror of script 46's helper, proven faithful by G1/G2)
  diff + position-cluster CI; all three strata printed; membership
  agreement arm1<->arm2 and arm2<->arm3; mean SE of each arm's high
  stratum (ties directly back to D1a).
  Verdict on arm3's MAE CI (6.3's own verdict was MAE-based):
    UNCHANGED-HOLD iff CI_lo > 0 (ESM-2 still worse than the null);
    REVERSED iff CI_hi < 0; DOWNGRADED iff CI crosses 0.
  MSE verdict printed alongside (C2c's variant of the rule).

D1c PRIMARY: R = sd(e.b | nonsense) / sd(e.b | synonymous) on the N2
  flag table (11,865 rows = script 35's own_e_b+se_e_b-complete subset;
  counts gated 10,757 substitution / 538 nonsense / 570 synonymous; the
  full script-35 table behind se_e_b is separately gated at its original
  13,134 / 11,902 / 624 / 608). CI = position-cluster bootstrap over the
  pooled syn+nonsense positions (both types' rows travel with position).
  Verdict: HIGHER iff CI_lo > 1; LOWER iff CI_hi < 1; else NOT DETECTED
  (explicitly NOT proof of equality). Secondary floor comparison:
  cut23 = the 2/3-quantile of |own_e_b| on substitution rows (the entry
  bar into the high tercile that6.3 actually uses) divided by
  sd(nonsense); independent position-cluster bootstrap of numerator and
  denominator; verdict FLOOR CLEARED iff CI_lo > 2 (high-stratum entry
  bar sits at least 2 dead-end-noise SDs above zero), NOT CLEARED iff
  CI_hi < 2, else INCONCLUSIVE. Plus epistatic_ecdf (N2's nonparametric
  flag) pass rate per type as
  a cross-check against script 35's published FPR table.

WHY THE 6.3 SET CONTAINS NO NONSENSE (printed as a gate, not discovered
mid-run): phase5's model_C/target exist only for missense rows, so the
stratified6.3 set is substitution-only by construction; D1c's floor is
therefore computed in e.b space on the N2 flag table (= script 35's
own_e_b+se_e_b-complete subset, se_e_b joined raw), which covers all
three variant types.

LIMITATIONS (also printed by the script, AGENTS §6)
----------------------------------------------------
- D1a: SE(e_b) and e.b come from the SAME WLS fit; the association asked
  for is the winner's-curse signature, not a causal claim. Analytic SEs
  are themselves miscalibrated (script 35's empirical/analytic ratio,
  recomputed here), so absolute SE levels understate noise — enrichment
  statistics are relative and inherit that scale error.
- D1b: EB prior is a single global Gaussian variance (method of moments),
  not covariate-dependent; strata labels are fixed within bootstrap draws
  (C2c convention); arm2-vs-arm1 agreement quantifies the own-vs-published
  switch so arm3-vs-arm2 isolates shrinkage alone.
- D1c: synonymous and nonsense sit at OPPOSITE fitness-range ends from the
  missense strata — that is the point of the check, and also why the
  floor comparison is not apples-to-apples with missense noise; the floor
  lives in e.b space only (no ESM scores exist for nonsense rows).
- Settings printed at the end: N_BOOT, SEED.

Outputs: data/processed/task50_d1a_se_enrichment.csv (+ _stats.csv),
         data/processed/task50_d1b_eb_restrat.csv (+ _agreement.csv),
         data/processed/task50_d1c_nonsense_floor.csv
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from scripts.lib.stats import crossfit_isotonic_by_position
from scripts.lib.stats_ext import paired_metric_difference_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

PUBLISHED_POOLED = 0.0005334660988103312      # script 34 saved (6.2) — G1
PUBLISHED_HIGH = 0.0024089195313244105         # script 34 saved (6.3) — G2


def fail(msg):
    print(f"*** {msg} — STOP (no retry, no tweak) ***")
    sys.exit(1)


def _mse(a, y):
    return float(np.mean((np.asarray(a, float) - np.asarray(y, float)) ** 2))


def paired_mse_bootstrap(df, cluster_col, pred_a, pred_b, target_col,
                         n_boot, seed=0):
    """Local mirror of script 46's MSE bootstrap (stats_ext._METRICS has
    no 'mse'; shared lib not rewritten, AGENTS §7). Faithfulness of the
    surrounding machinery is proven by gates G1/G2, not by trust."""
    d = df[[cluster_col, pred_a, pred_b, target_col]].dropna().reset_index(drop=True)
    clusters = d[cluster_col].unique()
    idx_by = {c: d.index[d[cluster_col] == c].to_numpy() for c in clusters}
    a, b, y = (d[pred_a].to_numpy(), d[pred_b].to_numpy(), d[target_col].to_numpy())
    observed = _mse(b, y) - _mse(a, y)
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for i in range(n_boot):
        drawn = rng.choice(clusters, size=len(clusters), replace=True)
        j = np.concatenate([idx_by[c] for c in drawn])
        boot[i] = _mse(b[j], y[j]) - _mse(a[j], y[j])
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return {"observed_diff": observed, "ci_lo": float(lo), "ci_hi": float(hi),
            "metric_a": _mse(a, y), "metric_b": _mse(b, y),
            "n_rows": len(d), "n_clusters": len(clusters),
            "boot_mean": float(np.nanmean(boot)),
            "n_valid": int(np.sum(~np.isnan(boot)))}


def build_set():
    """Exactly script 46's build_script34_set (mirror), seed 0."""
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = df.dropna(subset=["model_A", "model_C", "target", "f_bar_wt"]).reset_index(drop=True)
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df["pred_A"] = crossfit_isotonic_by_position(df, "position", "model_A",
                                                  "target", n_folds=5, seed=SEED)
    df["pred_C"] = crossfit_isotonic_by_position(df, "position", "model_C",
                                                  "target", n_folds=5, seed=SEED)
    w_hat = crossfit_isotonic_by_position(df, "position", "model_A",
                                           "f_bar_wt", n_folds=5, seed=SEED)
    p3 = pd.read_csv(PROC / "phase3_analysis_table.csv")
    A = float(p3[p3["hgvs_pro"] == "p.Ala222Val"]["f_bar_wt"].dropna().iloc[0])
    df["pred_mult"] = w_hat * A
    d = df.dropna(subset=["pred_A", "pred_C", "pred_mult", "target"]).copy()
    return d


def cluster_boot(df, stat_fn, n_boot, seed=0):
    """Position-cluster bootstrap of an arbitrary statistic on df
    (df must contain a 'position' column; stat_fn(sub-df) -> float).
    Local: one helper serves D1a's mean-diff and Spearman statistics."""
    d = df.reset_index(drop=True)
    pos = d["position"].to_numpy()
    uniq = np.unique(pos)
    idx_by = {p: np.flatnonzero(pos == p) for p in uniq}
    rng = np.random.default_rng(seed)
    out = np.full(n_boot, np.nan)
    for i in range(n_boot):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        j = np.concatenate([idx_by[p] for p in drawn])
        out[i] = stat_fn(d.iloc[j])
    lo, hi = np.nanpercentile(out, [2.5, 97.5])
    return {"value": float(stat_fn(d)), "ci_lo": float(lo), "ci_hi": float(hi),
            "boot_mean": float(np.nanmean(out)),
            "n_valid": int(np.sum(~np.isnan(out))), "n_clusters": len(uniq)}


if __name__ == "__main__":
    # ======================= GATES (D1b section) =========================
    d = build_set()
    print("=" * 74)
    print("GATES — build mirror + replication of 6.2/6.3 (exit 1 on failure)")
    print("=" * 74)
    print(f"script-34 set n = {len(d)} (expected 11,113), "
          f"{d['position'].nunique()} positions")
    if len(d) != 11113:
        fail(f"n = {len(d)} != 11,113")
    pooled = float(np.mean(np.abs(d["pred_C"] - d["target"])) -
                   np.mean(np.abs(d["pred_A"] - d["target"])))
    g1 = abs(pooled - PUBLISHED_POOLED)
    print(f"G1: pooled MAE diff = {pooled:+.18f} "
          f"(published {PUBLISHED_POOLED:+.18f}, |diff| = {g1:.3e})")
    if g1 > 1e-9:
        fail("G1 FAILED — cannot reproduce 6.2")
    # identity checks: equal-valued DISTINCT columns through both helpers
    # (passing the same column name twice makes df[[a,b]] duplicate it and
    # the lib crashes on shape (n,2) — a construction artifact, disclosed)
    d["pred_C_alias"] = d["pred_C"]
    ident_mae = paired_metric_difference_bootstrap(d, "position", "pred_C",
                                                   "pred_C_alias", "target",
                                                   metric="mae", n_boot=10,
                                                   seed=SEED)["observed_diff"]
    ident_mse = paired_mse_bootstrap(d, "position", "pred_C", "pred_C_alias",
                                     "target", n_boot=10, seed=SEED)["observed_diff"]
    print(f"identity: MAE helper a==b -> {ident_mae:.3e}; "
          f"MSE helper a==b -> {ident_mse:.3e}")
    if abs(ident_mae) > 1e-12 or abs(ident_mse) > 1e-12:
        fail("identity check failed — helpers do not return 0 for identical arms")

    # MIGRATED (task S2, 2026-09-22; supersedes the R2 single-file attempt): TWO-FILE design — base+flag from task_N2_nonparametric_epistatic_set.csv (flag column epistatic_ecdf, confirmed by its 16.6%/5.1% rates), se_e_b joined in separately from the retired task35_epistatic_set.csv on hgvs_pro (unique in both files; position NOT unique), used strictly as a raw continuous covariate, never re-thresholded; t35's epistatic_N* flags are never read (script 35's DEPRECATED header, task N1a).
    n2 = pd.read_csv(PROC / "task_N2_nonparametric_epistatic_set.csv")
    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")   # se_e_b + type source ONLY (raw continuous; no flag column from this file is used)
    counts = n2["type"].value_counts().to_dict()
    print(f"N2 table (flag+base): {len(n2)} rows, types {counts}")
    if len(n2) != 11865 or counts.get("substitution") != 10757 \
            or counts.get("nonsense") != 538 or counts.get("synonymous") != 570:
        fail(f"N2 counts unexpected: {len(n2)} {counts}")
    counts35 = t35["type"].value_counts().to_dict()
    print(f"retired t35 table (se_e_b source): {len(t35)} rows, types {counts35}")
    if len(t35) != 13134 or counts35.get("substitution") != 11902 \
            or counts35.get("nonsense") != 624 or counts35.get("synonymous") != 608:
        fail(f"task35 counts unexpected: {len(t35)} {counts35}")
    # the S2a join (key = hgvs_pro, unique in both): flag table + raw continuous se_e_b
    ep = n2.merge(t35[["hgvs_pro", "se_e_b"]], on="hgvs_pro", how="left")

    d = d.merge(t35[["hgvs_pro", "se_e_b", "type"]], on="hgvs_pro", how="left")
    s = d.dropna(subset=["abs_gi"]).reset_index(drop=True)
    print(f"s-set (dropna abs_gi): n = {len(s)} (expected 10,757); "
          f"SE join complete: {int(s['se_e_b'].notna().sum())}")
    if len(s) != 10757:
        fail(f"s-set n = {len(s)} != 10,757")
    if s["se_e_b"].notna().sum() != 10757:
        fail("SE join incomplete on the s-set")
    if (s["type"] != "substitution").any():
        fail("6.3 set is not substitution-only — D1c premise broken")
    print("6.3 set contains no nonsense/synonymous rows (missense-only by "
          "construction) — D1c uses the N2 flag table (= script 35's "
          "complete-case subset) instead.")

    # ======================= D1a: SE enrichment ==========================
    print("\n" + "=" * 74)
    print("D1a  IS THE HIGH-|e.b| STRATUM ENRICHED FOR HIGH-SE VARIANTS?")
    print("=" * 74)
    s["stratum_gi"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    s["se_top_tercile"] = s["se_e_b"] >= s["se_e_b"].quantile(2 / 3)
    print(f"strata (pd.qcut |GI| terciles, FIXED labels in draws — C2c rule):")
    d1a_rows = []
    means = {}
    for lvl in ["low", "mid", "high"]:
        sub = s[s["stratum_gi"] == lvl]
        means[lvl] = float(sub["se_e_b"].mean())
        share = float(sub["se_top_tercile"].mean())
        print(f"  {lvl:4s} n={len(sub):5d}  mean SE={means[lvl]:.4f}  "
              f"median SE={sub['se_e_b'].median():.4f}  "
              f"share in top-SE tercile={share:.3f} (1/3 = no enrichment)")
        d1a_rows.append({"stratifier": "GI_abs", "stratum": lvl, "n": len(sub),
                         "mean_se": means[lvl],
                         "median_se": float(sub["se_e_b"].median()),
                         "share_top_se_tercile": share})

    def _diff(sub):
        hi = sub.loc[sub["stratum_gi"] == "high", "se_e_b"]
        lo = sub.loc[sub["stratum_gi"] == "low", "se_e_b"]
        return float(hi.mean() - lo.mean())

    r_diff = cluster_boot(s, _diff, N_BOOT, seed=SEED)
    ratio = means["high"] / means["low"]
    print(f"\nPRIMARY D = mean(SE|high) - mean(SE|low) = {r_diff['value']:+.4f}  "
          f"CI=[{r_diff['ci_lo']:+.4f}, {r_diff['ci_hi']:+.4f}]  "
          f"({r_diff['n_valid']}/{N_BOOT} valid, {r_diff['n_clusters']} positions)")
    print(f"effect size: mean_SE_high / mean_SE_low = {ratio:.3f} "
          f"(+{100*(ratio-1):.1f}%)  [AGENTS §3]")
    verdict_d1a = ("ENRICHED" if r_diff["ci_lo"] > 0 else
                   "DEPLETED" if r_diff["ci_hi"] < 0 else "NOT DETECTED")
    print(f"D1a VERDICT (pre-registered rule): {verdict_d1a}")

    def _rho(sub):
        r = spearmanr(sub["abs_gi"], sub["se_e_b"]).statistic
        return float(r)

    r_rho = cluster_boot(s, _rho, N_BOOT, seed=SEED)
    print(f"\nsecondary Spearman(|GI|, SE) = {r_rho['value']:+.4f}  "
          f"CI=[{r_rho['ci_lo']:+.4f}, {r_rho['ci_hi']:+.4f}]  "
          f"(descriptive; same WLS fit feeds both — see limitations)")
    stat_rows = [
        {"stratifier": "GI_abs", "label": "PRIMARY_diff_high_low",
         "value": r_diff["value"], "ci_lo": r_diff["ci_lo"],
         "ci_hi": r_diff["ci_hi"], "verdict": verdict_d1a},
        {"stratifier": "GI_abs", "label": "effect_size_ratio_high_over_low",
         "value": ratio, "ci_lo": np.nan, "ci_hi": np.nan, "verdict": ""},
        {"stratifier": "GI_abs", "label": "secondary_spearman_absGI_vs_se",
         "value": r_rho["value"], "ci_lo": r_rho["ci_lo"],
         "ci_hi": r_rho["ci_hi"], "verdict": "descriptive"},
    ]

    # sensitivity (NOT verdict-bearing): own_e_b stratifier
    s["abs_own"] = s["own_e_b"].abs()
    s["stratum_own"] = pd.qcut(s["abs_own"], 3, labels=["low", "mid", "high"])
    agree = float((s["stratum_gi"].astype(str) == s["stratum_own"].astype(str)).mean())
    def _diff_own(sub):
        hi = sub.loc[sub["stratum_own"] == "high", "se_e_b"]
        lo = sub.loc[sub["stratum_own"] == "low", "se_e_b"]
        return float(hi.mean() - lo.mean())
    r_diff_own = cluster_boot(s, _diff_own, N_BOOT, seed=SEED)
    print(f"\nsensitivity (|own_e_b| strata): D = {r_diff_own['value']:+.4f}  "
          f"CI=[{r_diff_own['ci_lo']:+.4f}, {r_diff_own['ci_hi']:+.4f}];  "
          f"stratum agreement own vs GI = {agree:.3f} (the ~82% from design checks)")
    sens_verdict = ("ENRICHED" if r_diff_own["ci_lo"] > 0 else
                    "DEPLETED" if r_diff_own["ci_hi"] < 0 else "NOT DETECTED")
    print(f"sensitivity verdict: {sens_verdict} (not verdict-bearing)")
    for lvl in ["low", "mid", "high"]:
        sub = s[s["stratum_own"] == lvl]
        d1a_rows.append({"stratifier": "own_abs_sensitivity", "stratum": lvl,
                         "n": len(sub), "mean_se": float(sub["se_e_b"].mean()),
                         "median_se": float(sub["se_e_b"].median()),
                         "share_top_se_tercile": float(sub["se_top_tercile"].mean())})
    stat_rows += [
        {"stratifier": "own_abs_sensitivity", "label": "PRIMARY_diff_high_low",
         "value": r_diff_own["value"], "ci_lo": r_diff_own["ci_lo"],
         "ci_hi": r_diff_own["ci_hi"], "verdict": f"{sens_verdict} (not verdict-bearing)"},
        {"stratifier": "own_abs_sensitivity", "label": "stratum_agreement_vs_GI",
         "value": agree, "ci_lo": np.nan, "ci_hi": np.nan, "verdict": ""},
    ]
    pd.DataFrame(d1a_rows).to_csv(PROC / "task50_d1a_se_enrichment.csv", index=False)
    pd.DataFrame(stat_rows).to_csv(PROC / "task50_d1a_se_enrichment_stats.csv",
                                   index=False)
    print(f"Saved {PROC / 'task50_d1a_se_enrichment.csv'} + _stats.csv")

    # ======================= D1b: EB re-stratification ===================
    print("\n" + "=" * 74)
    print("D1b  6.3 UNDER AN EMPIRICAL-BAYES SHRUNKEN e.b STRATIFIER")
    print("=" * 74)
    # G2 first: arm1 must reproduce 6.3 exactly
    s["stratum_a1"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    hi1 = s[s["stratum_a1"] == "high"]
    g2 = paired_metric_difference_bootstrap(hi1, "position", "pred_mult",
                                            "pred_C", "target", metric="mae",
                                            n_boot=10, seed=SEED)["observed_diff"]
    g2err = abs(g2 - PUBLISHED_HIGH)
    print(f"G2: arm-1 high-stratum MAE diff = {g2:+.15f} "
          f"(6.3 = {PUBLISHED_HIGH:+.15f}, |diff| = {g2err:.3e})")
    if g2err > 1e-9:
        fail("G2 FAILED — cannot reproduce 6.3's high-stratum verdict base")

    var_own = float(s["own_e_b"].var(ddof=1))
    mean_se2 = float((s["se_e_b"] ** 2).mean())
    tau2 = var_own - mean_se2
    print(f"\nEB prior (method of moments): var(own_e_b) = {var_own:.6f} - "
          f"mean(se^2) = {mean_se2:.6f}  ->  tau^2 = {tau2:.6f}")
    eb_degenerate = tau2 <= 0
    if eb_degenerate:
        print("tau^2 <= 0 — EB-DEGENERATE (noise explains all variance); "
              "arm3 skipped as pre-registered, arms 1-2 still run.")
        s["eb_shrunk"] = 0.0
    else:
        s["eb_shrunk"] = s["own_e_b"] * (tau2 / (tau2 + s["se_e_b"] ** 2))
        shrink_diag = tau2 / (tau2 + s["se_e_b"] ** 2)
        print(f"shrink factor: min={shrink_diag.min():.3f} "
              f"median={shrink_diag.median():.3f} max={shrink_diag.max():.3f}; "
              f"spearman(raw, shrunk) = "
              f"{spearmanr(s['own_e_b'], s['eb_shrunk']).statistic:.4f}")

    s["abs_own"] = s["own_e_b"].abs()
    s["abs_eb"] = s["eb_shrunk"].abs()
    arms = [("arm1_raw_GI", "abs_gi"), ("arm2_raw_own", "abs_own"),
            ("arm3_eb_shrunk", "abs_eb")]
    d1b_rows = []
    arm_strata = {}
    arm_high_verdict = {}
    for aname, col in arms:
        if aname == "arm3_eb_shrunk" and eb_degenerate:
            continue
        s[f"str_{aname}"] = pd.qcut(s[col], 3, labels=["low", "mid", "high"])
        arm_strata[aname] = s[f"str_{aname}"].astype(str)
        print(f"\n--- {aname} (stratifier: {col}) ---")
        for lvl in ["low", "mid", "high"]:
            sub = s[s[f"str_{aname}"] == lvl]
            r_mae = paired_metric_difference_bootstrap(sub, "position", "pred_mult",
                                                       "pred_C", "target",
                                                       metric="mae", n_boot=N_BOOT,
                                                       seed=SEED)
            r_mse = paired_mse_bootstrap(sub, "position", "pred_mult", "pred_C",
                                         "target", n_boot=N_BOOT, seed=SEED)
            mean_se = float(sub["se_e_b"].mean())
            print(f"  {lvl:4s} (n={r_mae['n_rows']:5d}, {r_mae['n_clusters']} pos, "
                  f"mean SE={mean_se:.4f})  "
                  f"MAE diff={r_mae['observed_diff']:+.6f} "
                  f"CI=[{r_mae['ci_lo']:+.6f},{r_mae['ci_hi']:+.6f}]  "
                  f"MSE diff={r_mse['observed_diff']:+.6f} "
                  f"CI=[{r_mse['ci_lo']:+.6f},{r_mse['ci_hi']:+.6f}]")
            d1b_rows.append({"arm": aname, "stratum": lvl,
                             "n": r_mae["n_rows"], "n_pos": r_mae["n_clusters"],
                             "mean_se": mean_se,
                             "mae_diff": r_mae["observed_diff"],
                             "mae_ci_lo": r_mae["ci_lo"], "mae_ci_hi": r_mae["ci_hi"],
                             "mse_diff": r_mse["observed_diff"],
                             "mse_ci_lo": r_mse["ci_lo"], "mse_ci_hi": r_mse["ci_hi"]})
            if lvl == "high":
                v_mae = ("HOLD (CI_lo>0: ESM-2 worse)" if r_mae["ci_lo"] > 0 else
                         "REVERSED (CI_hi<0)" if r_mae["ci_hi"] < 0 else
                         "INCONCLUSIVE (CI crosses 0)")
                v_mse = ("HOLD (CI_lo>0)" if r_mse["ci_lo"] > 0 else
                         "REVERSED (CI_hi<0)" if r_mse["ci_hi"] < 0 else
                         "INCONCLUSIVE (CI crosses 0)")
                arm_high_verdict[aname] = (v_mae, v_mse)
                print(f"       high-stratum verdict: MAE {v_mae} | MSE {v_mse}")

    print("\nstratum membership agreement (fraction of rows in same tercile):")
    if "arm3_eb_shrunk" in arm_strata:
        pairs = [("arm1 vs arm2 (own-vs-published switch)", "arm1_raw_GI", "arm2_raw_own"),
                 ("arm2 vs arm3 (shrinkage alone)", "arm2_raw_own", "arm3_eb_shrunk"),
                 ("arm1 vs arm3 (total change vs 6.3)", "arm1_raw_GI", "arm3_eb_shrunk")]
    else:
        pairs = [("arm1 vs arm2 (own-vs-published switch)", "arm1_raw_GI", "arm2_raw_own")]
    agree_rows = []
    for lbl, a, b in pairs:
        agr = float((arm_strata[a] == arm_strata[b]).mean())
        hi_a = set(s.index[arm_strata[a] == "high"])
        hi_b = set(s.index[arm_strata[b] == "high"])
        moved = len(hi_a ^ hi_b)
        print(f"  {lbl}: {agr:.3f}  (rows entering/leaving the high stratum: {moved})")
        agree_rows.append({"comparison": lbl, "agreement": agr, "high_sym_diff": moved})

    v1 = arm_high_verdict["arm1_raw_GI"][0]
    v2 = arm_high_verdict["arm2_raw_own"][0]
    print(f"\narm1 high-stratum MAE verdict (gated replication of 6.3): {v1}")
    print(f"arm2 high-stratum MAE verdict (own_e_b switch control):   {v2}")
    if "arm3_eb_shrunk" in arm_high_verdict:
        v3_mae, v3_mse = arm_high_verdict["arm3_eb_shrunk"]
        lo_ok = v3_mae.startswith("HOLD")
        rev = v3_mae.startswith("REVERSED")
        d1b_verdict = ("UNCHANGED-HOLD" if lo_ok else
                       "REVERSED" if rev else "DOWNGRADED")
        print(f"arm3 high-stratum MAE verdict (EB-shrunken):            {v3_mae}")
        print(f"arm3 high-stratum MSE verdict:                           {v3_mse}")
        print(f"\nD1b VERDICT (pre-registered, arm3 MAE CI): {d1b_verdict} "
              f"— 6.3's high-stratum verdict is {v1.split(' (')[0]} on arm1")
    else:
        d1b_verdict = "EB-DEGENERATE"
        print(f"\nD1b VERDICT: EB-DEGENERATE (tau^2 <= 0); no shrunken re-stratification possible")
    pd.DataFrame(d1b_rows).to_csv(PROC / "task50_d1b_eb_restrat.csv", index=False)
    pd.DataFrame(agree_rows).to_csv(PROC / "task50_d1b_eb_agreement.csv", index=False)
    print(f"Saved {PROC / 'task50_d1b_eb_restrat.csv'} + _agreement.csv")

    # ======================= D1c: nonsense noise floor ===================
    print("\n" + "=" * 74)
    print("D1c  NONSENSE NOISE FLOOR (opposite fitness end from synonymous)")
    print("=" * 74)
    t = ep.dropna(subset=["own_e_b", "se_e_b"]).copy()
    # N2 rows + raw se_e_b join; dropna drops 0 rows (se non-null on all
    # 11,865 N2 rows — verified) => same 11,865-row set as before S2.
    t["abs_eb"] = t["own_e_b"].abs()
    d1c_rows = []
    for typ, lbl in [("synonymous", "synonymous"), ("nonsense", "nonsense"),
                     ("substitution", "missense (reference)")]:
        sub = t[t["type"] == typ]
        sd = float(sub["own_e_b"].std(ddof=1))
        med_se = float(sub["se_e_b"].median())
        p95 = float(sub["abs_eb"].quantile(0.95))
        ep2 = float(sub["epistatic_ecdf"].mean())
        print(f"  {lbl:22s} n={len(sub):5d}  sd(e.b)={sd:.4f}  "
              f"median SE={med_se:.4f}  p95|e.b|={p95:.4f}  "
              f"calib sd/medianSE={sd/med_se:.2f}  "
              f"epistatic_ecdf pass={100*ep2:.1f}%")
        for q, v in [(f"{typ}_n", len(sub)), (f"{typ}_sd_eb", sd),
                     (f"{typ}_median_se", med_se), (f"{typ}_p95_abs_eb", p95),
                     (f"{typ}_calib_sd_over_se", sd / med_se),
                     (f"{typ}_epistatic_ecdf_frac", ep2)]:
            d1c_rows.append({"quantity": q, "value": v,
                             "ci_lo": np.nan, "ci_hi": np.nan, "verdict": ""})

    syn = t[t["type"] == "synonymous"]
    nons = t[t["type"] == "nonsense"]
    mis = t[t["type"] == "substitution"]

    pos_pool = np.unique(np.concatenate([syn["position"].to_numpy(),
                                         nons["position"].to_numpy()]))
    syn_pos, syn_eb = syn["position"].to_numpy(), syn["own_e_b"].to_numpy()
    nons_pos, nons_eb = nons["position"].to_numpy(), nons["own_e_b"].to_numpy()
    syn_by = {p: syn_eb[syn_pos == p] for p in np.unique(syn_pos)}
    nons_by = {p: nons_eb[nons_pos == p] for p in np.unique(nons_pos)}
    rng_c = np.random.default_rng(SEED)
    ratios = np.full(N_BOOT, np.nan)
    for i in range(N_BOOT):
        drawn = rng_c.choice(pos_pool, size=len(pos_pool), replace=True)
        se_ = np.concatenate([syn_by[p] for p in drawn if p in syn_by])
        ne_ = np.concatenate([nons_by[p] for p in drawn if p in nons_by])
        if len(se_) > 1 and len(ne_) > 1:
            ratios[i] = np.std(ne_, ddof=1) / np.std(se_, ddof=1)
    R = float(np.std(nons_eb, ddof=1) / np.std(syn_eb, ddof=1))
    r_lo, r_hi = np.nanpercentile(ratios, [2.5, 97.5])
    v_R = ("HIGHER (nonsense noise > synonymous)" if r_lo > 1 else
           "LOWER (nonsense noise < synonymous)" if r_hi < 1 else
           "NOT DETECTED (CI crosses 1 — not proof of equality)")
    print(f"\nPRIMARY R = sd(e.b|nonsense)/sd(e.b|synonymous) = {R:.3f}  "
          f"CI=[{r_lo:.3f}, {r_hi:.3f}]  "
          f"({int(np.sum(~np.isnan(ratios)))}/{N_BOOT} valid)")
    print(f"D1c HETEROSCEDASTICITY VERDICT (pre-registered): {v_R}")

    cut23 = float(mis["abs_eb"].quantile(2 / 3))
    mis_pos = mis["position"].to_numpy()
    mis_eb = mis["abs_eb"].to_numpy()
    mis_by = {p: mis_eb[mis_pos == p] for p in np.unique(mis_pos)}
    # denominator must be sd of SIGNED nonsense e.b (the pre-registered
    # statistic); the smoke run caught an abs/signed mismatch here — the
    # bootstrap CI excluded its own point estimate. Fixed before the full run.
    rng_f = np.random.default_rng(SEED)
    rcuts = np.full(N_BOOT, np.nan)
    uniq_mis = np.unique(mis_pos)
    for i in range(N_BOOT):
        dm = rng_f.choice(uniq_mis, size=len(uniq_mis), replace=True)
        dn = rng_f.choice(pos_pool, size=len(pos_pool), replace=True)
        cm = np.concatenate([mis_by[p] for p in dm])
        nn = np.concatenate([nons_by[p] for p in dn if p in nons_by])
        if len(cm) > 1 and len(nn) > 1:
            rcuts[i] = np.quantile(cm, 2 / 3) / np.std(nn, ddof=1)
    R_cut = cut23 / float(np.std(nons_eb, ddof=1))
    c_lo, c_hi = np.nanpercentile(rcuts, [2.5, 97.5])
    v_cut = ("FLOOR CLEARED (CI_lo > 2)" if c_lo > 2 else
             "NOT CLEARED (CI_hi < 2)" if c_hi < 2 else "INCONCLUSIVE")
    print(f"\nSECONDARY floor comparison: cut23(|own_e_b|, missense) = {cut23:.4f} / "
          f"sd(nonsense) = {float(np.std(nons_eb, ddof=1)):.4f}  ->  ratio {R_cut:.3f}  "
          f"CI=[{c_lo:.3f}, {c_hi:.3f}]")
    print(f"D1c FLOOR VERDICT (pre-registered): {v_cut}")
    print("  (syn/nonsense sit at opposite fitness ends from the missense "
          "strata — see limitations; ratio < 1 would mean the entry bar into")
    print("   6.3's 'high interaction' tercile is smaller than dead-end noise "
          "spread at the floor of the fitness range.)")

    d1c_rows += [
        {"quantity": "R_sd_nonsense_over_syn", "value": R,
         "ci_lo": float(r_lo), "ci_hi": float(r_hi), "verdict": v_R},
        {"quantity": "cut23_missense", "value": cut23,
         "ci_lo": np.nan, "ci_hi": np.nan, "verdict": ""},
        {"quantity": "R_cut23_over_sd_nonsense", "value": R_cut,
         "ci_lo": float(c_lo), "ci_hi": float(c_hi), "verdict": v_cut},
    ]
    pd.DataFrame(d1c_rows).to_csv(PROC / "task50_d1c_nonsense_floor.csv", index=False)
    print(f"Saved {PROC / 'task50_d1c_nonsense_floor.csv'}")

    # ======================= limitations (AGENTS §6) =====================
    print("\n" + "=" * 74)
    print("LIMITATIONS (printed by the script itself)")
    print("=" * 74)
    print("  - D1a: SE(e_b) and e.b come from the SAME WLS fit — the")
    print("    association is the winner's-curse signature, not causal.")
    print("    Analytic SEs are themselves miscalibrated (script 35's")
    print("    empirical/analytic ratio), so absolute SE levels understate")
    print("    noise; enrichment statistics are RELATIVE and inherit that.")
    print("  - D1b: EB prior = single global Gaussian tau^2 (method of")
    print("    moments), not covariate-dependent; shrinkage uses own_e_b +")
    print("    SE only, never the target (no leakage into cross-fit preds);")
    print("    stratum labels FIXED within bootstrap draws (C2c convention);")
    print("    arm2-vs-arm1 agreement isolates the own-vs-published switch.")
    print("  - D1c: synonymous/nonsense sit at OPPOSITE fitness-range ends")
    print("    from the missense strata — the point of the check AND the")
    print("    reason the floor ratio is not apples-to-apples with missense")
    print("    noise; floor lives in e.b space only (no ESM scores exist for")
    print("    nonsense rows); INCONCLUSIVE/NOT DETECTED = absence of")
    print("    evidence, not evidence of equality.")
    print(f"  - Settings: N_BOOT={N_BOOT}, SEED={SEED}.")
    print("\nDone.")



