"""
Task C2 (review-triage): robustness of the MAE differences in logs 6.2/6.3.

C2a  Influence: which variants drive 6.2's +0.00053 (pred_C - pred_A)?
     If a few dozen near-222 variants account for it, the story is local
     (5.4's proximity confound), not "background info hurts" broadly.
C2b  Fold-seed sensitivity: recompute the +0.00053 under 50 different
     position-fold seeds of the cross-fit isotonic calibration. If the
     cross-seed spread is comparable to the published CI width, the result
     is not as clean as one seed suggests.
C2c  Does 6.3's high-stratum verdict hold under MSE instead of MAE?
     Isotonic regression targets the conditional mean (squared-error
     optimal); evaluating it on MAE (median-optimal) is a loss/calibration
     mismatch that could matter at this effect size.

PRE-REGISTERED DECISION RULES (fixed before running; AGENTS.md §6):
  * Replication gates, checked FIRST, exit(1) on failure (AGENTS §4):
      G1: pooled MAE diff (pred_C - pred_A, seed 0, n=11,113) must equal
          script 34's saved +0.0005334660988103312 to |diff| <= 1e-9.
      G2: high-stratum MAE diff (pred_C - pred_mult, seed 0, n=3,586)
          must equal script 34's saved +0.0024089195313244105 to <= 1e-9.
      Internal identity: mean over rows of (|pred_C-y| - |pred_A-y|)
          must equal G1's diff to <= 1e-12.
  * C2a influence measure: c_i = |pred_C - y_i| - |pred_A - y_i| with the
    calibration held fixed at script 34's seed-0 full-data fit (the
    standard decomposition of a mean difference; refitting per subset is
    reported separately as the drop-zone check below).
    Bands by linear distance to residue 222: <=25 (5.4's local zone),
    26-100, >100; position==222 counted separately.
    PRIMARY VERDICT: LOCAL if band(<=25) contributes >= 50% of the signed
    total; BROAD if it contributes <= 20%; MIXED otherwise.
    SECONDARY (corroboration, not the verdict): refit pred_A/pred_C on
    rows with distance > 25 only (seed 0). If the restricted diff stays
    positive and >= 50% of the full diff, the effect survives removal of
    the local zone.
  * C2b: 50 seeds (0..49; seed 0 is the published one). Reference CI half
    width = (0.0007675630167030905 - 0.00028835365805139276)/2 =
    0.00023960487957904891.
    VERDICT: SEED-ROBUST if cross-seed sd <= that half-width AND no seed
    flips sign (diff <= 0); SEED-SENSITIVE if sd > half-width OR >= 5 of
    50 seeds flip; MIXED otherwise.
  * C2c: same qcut |e.b| terciles as 6.3 (script 34's exact rows; strata
    total 10,757 because 356 of the 11,113 lack non-null e.b — the n-chain
    from A2a/A2b). MSE bootstrap mirrors the house MAE bootstrap exactly
    (position clusters, seed 0, percentile CI) but computes
    mean((pred-y)^2); it lives locally because scripts/lib/stats_ext.py's
    _METRICS has no "mse" key and shared lib code must not be rewritten
    (AGENTS §7).
    VERDICT on the HIGH stratum only: HOLD if MSE CI_lo > 0 (ESM-2 still
    worse than the multiplicative null); REVERSED if CI_hi < 0;
    INCONCLUSIVE otherwise. low/mid printed for completeness, no verdict.

LIMITATIONS (stated in the output as well): C2a decomposes a fixed
calibration, so it measures where the realized difference lives, not how
the fit would change if the local zone were absent (that is the secondary
refit). C2b varies only the fold assignment seed; training-set
composition per fold is the thing that varies, which is the intended
target. C2c's MSE and MAE bootstraps are separate resampling runs (same
seed, so the same position draws), not a paired per-draw difference.
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
N_SEEDS = 50
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

PUBLISHED_POOLED = 0.0005334660988103312       # script 34 saved (6.2)
PUBLISHED_HIGH = 0.0024089195313244105          # script 34 saved (6.3)
CI_LO, CI_HI = 0.00028835365805139276, 0.0007675630167030905
CI_HALF = (CI_HI - CI_LO) / 2.0                 # 0.00023960487957904891


def _mse(a, y):
    return float(np.mean((np.asarray(a, float) - np.asarray(y, float)) ** 2))


def paired_mse_bootstrap(df, cluster_col, pred_a, pred_b, target_col,
                         n_boot, seed=0):
    """Same algorithm as stats_ext.paired_metric_difference_bootstrap,
    metric = MSE. Local because shared lib must not be rewritten (§7)."""
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
            "n_rows": len(d), "n_clusters": len(clusters)}


def build_script34_set():
    """Exactly script 34's analysis set and predictors (seed 0)."""
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


if __name__ == "__main__":
    d = build_script34_set()
    print(f"Analysis set: {len(d)} variants, {d['position'].nunique()} positions "
          f"(script 34's set; expected 11,113)")
    if len(d) != 11113:
        print("*** n != 11,113 — investigate before quoting anything below ***")

    # ---- replication gates -------------------------------------------------
    pooled = float(np.mean(np.abs(d["pred_C"] - d["target"])) -
                   np.mean(np.abs(d["pred_A"] - d["target"])))
    g1 = abs(pooled - PUBLISHED_POOLED)
    print(f"GATE G1: pooled MAE diff = {pooled:+.18f} "
          f"(published {PUBLISHED_POOLED:+.18f}, |diff| = {g1:.3e})")
    if g1 > 1e-9:
        print("GATE G1 FAILED — cannot reproduce 6.2. STOP (no retry, no tweak).")
        sys.exit(1)

    # =================== C2a: influence ====================================
    print("\n" + "=" * 74)
    print("C2a  INFLUENCE: which variants drive the +0.00053 (pred_C - pred_A)?")
    print("=" * 74)
    d["c"] = np.abs(d["pred_C"] - d["target"]) - np.abs(d["pred_A"] - d["target"])
    ident = abs(d["c"].mean() - PUBLISHED_POOLED)
    print(f"internal identity: mean(c_i) = {d['c'].mean():+.18f} "
          f"(|diff| = {ident:.3e})")
    if ident > 1e-12:
        print("IDENTITY FAILED — per-row decomposition does not sum to the diff. STOP.")
        sys.exit(1)

    d["dist222"] = (d["position"] - 222).abs()
    d["band"] = np.where(d["dist222"] <= 25, "0-25",
                  np.where(d["dist222"] <= 100, "26-100", ">100"))
    total = d["c"].sum()
    n_at222 = int((d["position"] == 222).sum())
    print(f"variants at position 222 exactly: {n_at222} "
          f"(A222X substitutions; p.Ala222Val itself has no model_C, excluded upstream)")
    print(f"{'band':8s} {'n':>6s} {'sum_c':>10s} {'share%':>8s} {'mean_c':>10s}")
    band_rows = []
    for b in ["0-25", "26-100", ">100"]:
        sub = d[d["band"] == b]
        share = float(sub["c"].sum() / total * 100) if total != 0 else np.nan
        print(f"{b:8s} {len(sub):6d} {sub['c'].sum():+10.4f} {share:8.2f} "
              f"{sub['c'].mean():+10.3e}")
        band_rows.append({"band": b, "n": len(sub), "sum_c": float(sub["c"].sum()),
                          "share_pct": share, "mean_c": float(sub["c"].mean())})
    share25 = float(d.loc[d["dist222"] <= 25, "c"].sum() / total * 100)
    verdict = ("LOCAL (>=50% of signed total within 25 residues)" if share25 >= 50 else
               "BROAD (<=20% within 25 residues)" if share25 <= 20 else
               "MIXED")
    print(f"PRIMARY RULE: share within |pos-222|<=25 = {share25:.2f}%  -> {verdict}")

    print("\ntop 10 variants by signed contribution:")
    top = d.nlargest(10, "c")[["hgvs_pro", "position", "c"]]
    for _, r in top.iterrows():
        print(f"  {r['hgvs_pro']:18s} pos={int(r['position']):4d}  c={r['c']:+.4f}")
    top_rows = []
    for k in [10, 25, 50, 100]:
        tk = d.nlargest(k, "c")
        sh = float(tk["c"].sum() / total * 100)
        nloc = int((tk["dist222"] <= 25).sum())
        frac_rows = float((d["dist222"] <= 25).mean())
        print(f"top {k:3d} contribute {sh:7.2f}% of the signed total; "
              f"{nloc} of them within 25 residues "
              f"(rows overall in that zone: {frac_rows*100:.1f}%)")
        top_rows.append({"top_k": k, "share_pct": sh, "n_within25": nloc,
                         "frac_rows_within25": frac_rows})
    print("expected # within 25 among top-50 under no enrichment: "
          f"{50 * float((d['dist222'] <= 25).mean()):.1f}")

    gsum = d.groupby("position")["c"].sum()
    gnn = d.groupby("position").size()
    loo = (total - gsum) / (len(d) - gnn)
    print(f"leave-one-position-out diff: min={loo.min():+.6f} "
          f"max={loo.max():+.6f} (full={total/len(d):+.6f}) "
          f"-> widest shift from dropping position {int(loo.idxmin())} "
          f"({total/len(d) - loo.min():+.6f})")

    loc = d[d["dist222"] > 25].copy()
    loc["pred_A_r"] = crossfit_isotonic_by_position(loc, "position", "model_A",
                                                    "target", n_folds=5, seed=SEED)
    loc["pred_C_r"] = crossfit_isotonic_by_position(loc, "position", "model_C",
                                                    "target", n_folds=5, seed=SEED)
    diff_r = float(np.mean(np.abs(loc["pred_C_r"] - loc["target"])) -
                   np.mean(np.abs(loc["pred_A_r"] - loc["target"])))
    ratio = diff_r / pooled
    survives = diff_r > 0 and ratio >= 0.5
    print(f"SECONDARY drop-zone refit (rows >25 residues only, n={len(loc)}, "
          f"refitted): diff = {diff_r:+.6f} = {ratio*100:.1f}% of full "
          f"-> {'SURVIVES' if survives else 'does NOT survive'} "
          f"(>=50% and >0 pre-registered as survives)")

    # =================== C2b: fold-seed sensitivity ========================
    print("\n" + "=" * 74)
    print(f"C2b  FOLD-SEED SENSITIVITY: cross-fit isotonic under {N_SEEDS} seeds")
    print("=" * 74)
    diffs = []
    for s in range(N_SEEDS):
        pa = crossfit_isotonic_by_position(d, "position", "model_A", "target",
                                           n_folds=5, seed=s)
        pc = crossfit_isotonic_by_position(d, "position", "model_C", "target",
                                           n_folds=5, seed=s)
        diffs.append(float(np.mean(np.abs(pc - d["target"])) -
                           np.mean(np.abs(pa - d["target"]))))
    diffs = np.array(diffs)
    sd = float(diffs.std(ddof=1))
    flips = int((diffs <= 0).sum())
    print(f"cross-seed diffs: mean={diffs.mean():+.7f} sd={sd:.7f} "
          f"min={diffs.min():+.7f} max={diffs.max():+.7f} "
          f"(seed 0 = published {PUBLISHED_POOLED:+.7f})")
    print(f"published CI half-width = {CI_HALF:.7f}  "
          f"(from [+0.000288, +0.000768])")
    print(f"sd / CI half-width = {sd / CI_HALF:.3f};  seeds flipping sign "
          f"(diff <= 0): {flips}/{N_SEEDS}")
    boot_sd = (CI_HI - CI_LO) / (2 * 1.96)
    print(f"combined sd = sqrt(boot_sd^2 + seed_sd^2) = "
          f"{np.sqrt(boot_sd**2 + sd**2):.7f}  "
          f"(boot_sd alone = {boot_sd:.7f})")
    vb = ("SEED-ROBUST (sd <= CI half-width AND no sign flips)" if
          (sd <= CI_HALF and flips == 0) else
          f"SEED-SENSITIVE (sd > half-width or {flips} flips >= 5)" if
          (sd > CI_HALF or flips >= 5) else "MIXED")
    print(f"VERDICT: {vb}")

    # =================== C2c: MSE instead of MAE ===========================
    print("\n" + "=" * 74)
    print(f"C2c  HIGH-STRATUM VERDICT UNDER MSE (vs MAE), 6.3's exact rows "
          f"({N_BOOT} draws each)")
    print("=" * 74)
    s = d.dropna(subset=["abs_gi"]).copy()
    s["stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    print(f"strata formed on n={len(s)} (11,113 minus {11113 - len(s)} rows "
          f"with null e.b — the A2a/A2b n-chain)")
    c2c_rows = []
    verdict_high = None
    for lvl in ["low", "mid", "high"]:
        sub = s[s["stratum"] == lvl]
        r_mae = paired_metric_difference_bootstrap(sub, "position", "pred_mult",
                                                   "pred_C", "target",
                                                   metric="mae",
                                                   n_boot=N_BOOT, seed=SEED)
        r_mse = paired_mse_bootstrap(sub, "position", "pred_mult", "pred_C",
                                     "target", n_boot=N_BOOT, seed=SEED)
        if lvl == "high":
            g2 = abs(r_mae["observed_diff"] - PUBLISHED_HIGH)
            print(f"GATE G2: high-stratum MAE diff = {r_mae['observed_diff']:+.15f} "
                  f"(published {PUBLISHED_HIGH:+.15f}, |diff| = {g2:.3e})")
            if g2 > 1e-9:
                print("GATE G2 FAILED — cannot reproduce 6.3. STOP.")
                sys.exit(1)
            verdict_high = ("HOLD (MSE CI_lo > 0: ESM-2 still worse than null)"
                            if r_mse["ci_lo"] > 0 else
                            "REVERSED (MSE CI_hi < 0: ESM-2 better than null)"
                            if r_mse["ci_hi"] < 0 else
                            "INCONCLUSIVE (MSE CI crosses 0)")
        print(f"{lvl:4s} (n={r_mae['n_rows']:4d}, {r_mae['n_clusters']} positions) "
              f"MAE: null={r_mae['metric_a']:.4f} esm={r_mae['metric_b']:.4f} "
              f"diff={r_mae['observed_diff']:+.5f} "
              f"CI=[{r_mae['ci_lo']:+.5f},{r_mae['ci_hi']:+.5f}]")
        print(f"{'':21s}MSE: null={r_mse['metric_a']:.5f} esm={r_mse['metric_b']:.5f} "
              f"diff={r_mse['observed_diff']:+.6f} "
              f"CI=[{r_mse['ci_lo']:+.6f},{r_mse['ci_hi']:+.6f}]")
        c2c_rows.append({"stratum": lvl, "n": r_mae["n_rows"],
                         "mae_null": r_mae["metric_a"], "mae_esm": r_mae["metric_b"],
                         "mae_diff": r_mae["observed_diff"],
                         "mae_ci_lo": r_mae["ci_lo"], "mae_ci_hi": r_mae["ci_hi"],
                         "mse_null": r_mse["metric_a"], "mse_esm": r_mse["metric_b"],
                         "mse_diff": r_mse["observed_diff"],
                         "mse_ci_lo": r_mse["ci_lo"], "mse_ci_hi": r_mse["ci_hi"]})
    print(f"HIGH-STRATUM VERDICT UNDER MSE: {verdict_high}")

    # ---- save --------------------------------------------------------------
    out1 = PROC / "task46_c2_influence.csv"
    pd.DataFrame(band_rows).assign(rule_verdict=verdict, share_within25=share25,
                                   secondary_diff=diff_r, secondary_ratio=ratio,
                                   loo_min=float(loo.min()), loo_max=float(loo.max())
                                   ).to_csv(out1, index=False)
    out2 = PROC / "task46_c2_seeds.csv"
    pd.DataFrame({"seed": range(N_SEEDS), "mae_diff": diffs}).to_csv(out2, index=False)
    out3 = PROC / "task46_c2_mse.csv"
    pd.DataFrame(c2c_rows).to_csv(out3, index=False)
    print(f"\nSaved {out1.name}, {out2.name}, {out3.name}")

    print("\nLIMITATIONS (also in the docstring): C2a decomposes a FIXED")
    print("seed-0 calibration (where the realized diff lives, not how the fit")
    print("would change without the local zone — that is the secondary refit).")
    print("C2b varies the fold-assignment seed only. C2c's MAE and MSE use the")
    print("same seed (same position draws) but are separate resampling runs,")
    print("not a paired per-draw difference. Isotonic calibration is")
    print("squared-error optimal by construction, so MSE is the loss it is")
    print("optimized for; MAE is the metric the log reports.")
