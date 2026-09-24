"""
Task C3a (review-triage): oracle ceiling for the MAE comparison, and the
correlation disattenuation asked for alongside it.

PART 1 — ORACLE CEILING
  Synthetic oracle predictor of target (f_bar_a222v):
      implied(v) = f_bar_wt(v) * A      multiplicative no-interaction built
                                        from MEASURED quantities (A read
                                        from phase3 exactly as script 34)
      oracle(v)  = implied(v) + e.b(v) + eps,  eps ~ N(0, sigma^2)
  sigma matched to the SYNONYMOUS-DERIVED reliability of e.b, computed
  from data (never assumed):
      rel = 1 - var(e.b | synonymous) / var(e.b | analysis set)
  Two readings of "+noise matched to reliability 0.64" exist; the
  instruction is ambiguous, so BOTH are computed and labeled (AGENTS.md
  protocol: conservative reading + log the assumption):
      (a) PRIMARY, the literal algebra: knowledge = signal + noise with
          rel = var(signal)/var(knowledge)
          -> sigma^2 = var(e.b) * (1/rel - 1)
      (b) SENSITIVITY, classical measurement error:
          observed = truth + noise with rel = var(truth)/var(observed)
          -> sigma^2 = var(e.b) * (1 - rel)
      plus the ZERO-NOISE reference (implied + e.b, no eps).
  10 noise draws (seeds 0..9), mean/sd of MAE reported. The PRIMARY
  oracle's improvement over the multiplicative null (pred_mult) gets a
  position-bootstrap CI (N_BOOT env, seed 0), POOLED and in 6.3's HIGH
  stratum (qcut |e.b| terciles, the exact 6.3 rows).
  6.3's ESM-2 diff is reported against that ceiling, taken from script
  34's saved CSV (task34_additive_null.csv): pooled
  -0.00030834734510909456, high +0.0024089195313244105 (sign convention:
  MAE(ESM-2) - MAE(null); positive = ESM-2 worse. MTHFR_RESULTS_LOG 6.3
  prints +0.00241 "ESM-2 WORSE"; REVIEW_TRIAGE C3a calls the same number
  "-0.00241 loss" — both phrasings printed once, neither document edited).
  PRE-REGISTERED: the ceiling is usable as a reference only if the
  PRIMARY oracle's pooled improvement CI excludes 0; otherwise report "no
  measurable ceiling exists" (a null result) and skip all fraction claims.

  CIRCULARITY DISCLOSURE (printed by the script, not buried): e.b is
  fitted from the same measurements that define target, so
  implied + e.b is an IN-SAMPLE reconstruction. The oracle sizes HOW MUCH
  MAE improvement exists between the null and near-perfect
  reconstruction; it is not an achievable model and must never be quoted
  as one.

PART 2 — DISATTENUATION
  GATE G3: Spearman(delta_esm, own_e_b) on n=10,757 must equal script
  32's saved -0.08811806424891734 to <=1e-9.
  GATE G4: Spearman(delta_esm, GI_folinate_independent) must equal
  -0.07070516222228716 to <=1e-9.
  GATE G5: rebuilt own_e_b (rebuild_interaction_fit, script 35's
  pattern) must match own_context_metrics.csv to <=1e-9 on mergeable
  rows (column identity, AGENTS.md §5).
  r_dis = rho / sqrt(rel); reliability of delta_esm = 1 (deterministic
  model output — assumption printed). Joint position bootstrap (N_BOOT):
  each draw resamples positions from the UNION of analysis-set and
  synonymous positions and recomputes rho AND rel, so the CI covers both
  sources of uncertainty. Synonymous rows are rebuilt from raw (the CSV
  contains substitution rows only).
  PRE-REGISTERED verdict: "materially larger" iff |r_dis|/|rho| >= 1.25
  (the ratio rel=0.64 itself implies; fixed in advance regardless of what
  rel computes to) AND the disattenuated CI excludes 0; else
  "not material".

LIMITATIONS: point rho is row-level (identical to script 32 / log 5.2);
only the CI is position-clustered. The oracle CI uses the seed-0 noise
draw (10-draw mean printed alongside). The classical reading (b) assumes
measurement error uncorrelated with delta_esm. Reliability treats
synonymous e.b spread as pure noise (the atlas's own control, log 2.3).
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import crossfit_isotonic_by_position, _spearman
from scripts.lib.stats_ext import (paired_metric_difference_bootstrap,
                                   rebuild_interaction_fit)

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
N_NOISE = 10
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"

R_OWN_PUBLISHED = -0.08811806424891734     # script 32 saved (5.2, own e.b)
R_PUB_PUBLISHED = -0.07070516222228716      # script 32 saved (5.2, published e.b)
ESM_VS_NULL_POOLED = -0.00030834734510909456   # script 34 saved (6.2 row 1)
ESM_VS_NULL_HIGH = 0.0024089195313244105       # script 34 saved (6.3)


def gate(name, got, want, tol=1e-9):
    ok = abs(got - want) <= tol
    print(f"GATE {name}: got {got:+.15f} (published {want:+.15f}, "
          f"|diff| = {abs(got - want):.3e}) -> {'OK' if ok else 'FAILED'}")
    if not ok:
        print(f"GATE {name} FAILED — cannot reproduce the published value. STOP.")
        sys.exit(1)


if __name__ == "__main__":
    # ---- analysis set (script 34's, minus nothing new) --------------------
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    base = df.dropna(subset=["model_A", "model_C", "target", "f_bar_wt"]).reset_index(drop=True)
    p3 = pd.read_csv(PROC / "phase3_analysis_table.csv")
    A = float(p3[p3["hgvs_pro"] == "p.Ala222Val"]["f_bar_wt"].dropna().iloc[0])
    print(f"Analysis set: {len(base)} variants, {base['position'].nunique()} positions "
          f"(script 34's set; expected 11,113)   A = {A:.4f}")
    if len(base) != 11113:
        print("*** n != 11,113 — investigate before quoting anything below ***")

    w_hat = crossfit_isotonic_by_position(base, "position", "model_A", "f_bar_wt",
                                          n_folds=5, seed=SEED)
    base["pred_mult"] = w_hat * A
    base["implied"] = base["f_bar_wt"] * A

    # ---- gates G3/G4/G5: disattenuation inputs ----------------------------
    ana = base.dropna(subset=["delta_esm", "own_e_b", "GI_folinate_independent"]).copy()
    print(f"\ndisattenuation analysis rows: {len(ana)} (expected 10,757)")
    r_own = float(_spearman(ana["delta_esm"].to_numpy(), ana["own_e_b"].to_numpy()))
    r_pub = float(_spearman(ana["delta_esm"].to_numpy(),
                            ana["GI_folinate_independent"].to_numpy()))
    gate("G3 (rho own_e_b)", r_own, R_OWN_PUBLISHED)
    gate("G4 (rho published e.b)", r_pub, R_PUB_PUBLISHED)

    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    syn_own = pd.DataFrame({"position": raw["start"], "type": raw["type"],
                            "own_e_b": fit["e2"]["e_b"],
                            "pub_e_b": raw["e.b"]})
    # G5: rebuilt own_e_b vs the CSV on mergeable rows (identity check, §5)
    rebuild_all = pd.DataFrame({"hgvs_pro": raw["hgvs"],
                                "own_eb_rebuilt": fit["e2"]["e_b"]}).dropna()
    m5 = rebuild_all.merge(own, on="hgvs_pro", how="inner").dropna()
    g5 = float((m5["own_eb_rebuilt"] - m5["own_e_b"]).abs().max())
    print(f"GATE G5 (rebuilt vs CSV own_e_b): n={len(m5)}, max|diff| = {g5:.3e} "
          f"-> {'OK' if g5 <= 1e-9 else 'FAILED'}")
    if g5 > 1e-9:
        sys.exit(1)

    # ---- reliabilities, computed from data -------------------------------
    syn = syn_own[syn_own["type"] == "synonymous"].dropna(subset=["own_e_b"])
    syn_pub = raw.loc[raw["type"] == "synonymous", "e.b"].dropna()
    ana = ana.reset_index(drop=True)   # positional index for the bootstrap maps below
    rel_own = float(1 - syn["own_e_b"].var() / ana["own_e_b"].var())
    rel_pub = float(1 - syn_pub.var() / ana["GI_folinate_independent"].var())
    print(f"\nreliability, own e.b     : 1 - var(syn {syn['own_e_b'].var():.5f}, "
          f"n={len(syn)}) / var(analysis {ana['own_e_b'].var():.5f}) = {rel_own:.4f}")
    print(f"reliability, published e.b: 1 - var(syn {syn_pub.var():.5f}, "
          f"n={len(syn_pub)}) / var(analysis {ana['GI_folinate_independent'].var():.5f}) "
          f"= {rel_pub:.4f}")
    print(f"review's assumed ~0.64 -> own flavor {rel_own:.3f} "
          f"({'MATCHES' if abs(rel_own - 0.64) < 0.01 else 'differs from'}); "
          f"published flavor {rel_pub:.3f} (logged for the record)")
    print(f"synonymous own e.b: n={len(syn)}, mean={syn['own_e_b'].mean():+.4f}, "
          f"sd={syn['own_e_b'].std():.4f}  [log 2.3 says mean +0.0217, sd 0.145]")

    # =================== PART 1: oracle ceiling ============================
    print("\n" + "=" * 74)
    print("C3a-1  ORACLE CEILING (position bootstrap, N_BOOT=%d)" % N_BOOT)
    print("=" * 74)
    print("CIRCULARITY, stated up front: e.b is fitted from the same")
    print("measurements that define target, so implied+e.b is an IN-SAMPLE")
    print("reconstruction. The oracle SIZES THE CEILING (how much MAE gain")
    print("exists between the null and near-perfect reconstruction); it is")
    print("NOT an achievable model and must not be quoted as one.")
    # scale diagnostics (why the decomposition is coherent at all)
    for col, lbl in [("GI_folinate_independent", "published"), ("own_e_b", "own")]:
        m = base[["implied", "target", col]].dropna()
        sl, ic = np.polyfit(m[col], m["target"] - m["implied"], 1)
        print(f"  target-implied ~ {lbl:9s} e.b: slope={sl:+.4f} intercept={ic:+.4f} "
              f"pearson={np.corrcoef(m[col], m['target'] - m['implied'])[0,1]:+.4f} "
              f"n={len(m)}")
    mae_null_all = float(np.abs(base.loc[base["pred_mult"].notna() &
                                         base["target"].notna(), "pred_mult"] -
                                base.loc[base["pred_mult"].notna() &
                                         base["target"].notna(), "target"]).mean())
    print(f"  MAE(implied) alone          = {np.abs(base['implied'] - base['target']).mean():.4f}")
    print(f"  MAE(multiplicative null)    = {mae_null_all:.4f}   [calibrated w_hat x A]")

    def oracle_column(flavor_col, rel, reading, seed=SEED):
        eb = base[flavor_col].to_numpy(dtype=float)
        var = np.nanvar(eb)
        sig = np.sqrt(var * (1 / rel - 1)) if reading == "a" else (
              np.sqrt(var * (1 - rel)) if reading == "b" else 0.0)
        rng = np.random.default_rng(seed)
        eps = np.where(np.isfinite(eb), rng.normal(0, sig, len(eb)), np.nan)
        return base["implied"].to_numpy() + eb + eps, sig

    variants = []
    for flavor_col, flavor_lbl, rel in [
            ("GI_folinate_independent", "published", rel_pub),
            ("own_e_b", "own", rel_own)]:
        zn, _ = oracle_column(flavor_col, rel, "0")
        v = zn[np.isfinite(zn)]
        variants.append({"flavor": flavor_lbl, "reading": "zero-noise",
                         "sigma": 0.0,
                         "mae_mean": float(np.abs(v - base.loc[np.isfinite(zn), "target"]).mean()),
                         "mae_sd": 0.0})
        for reading, lbl in [("a", "primary (a): var_e*(1/rel-1)"),
                             ("b", "sensitivity (b): var_e*(1-rel)")]:
            maes, sig = [], None
            for s in range(N_NOISE):
                col, sig = oracle_column(flavor_col, rel, reading, seed=s)
                m = np.isfinite(col)
                maes.append(float(np.abs(col[m] - base.loc[m, "target"]).mean()))
            variants.append({"flavor": flavor_lbl, "reading": lbl, "sigma": float(sig),
                             "mae_mean": float(np.mean(maes)),
                             "mae_sd": float(np.std(maes, ddof=1))})
    print(f"\n{'flavor':10s} {'reading':34s} {'sigma':>7s} {'MAE_mean':>9s} {'MAE_sd':>8s} "
          f"{'improve_pooled':>15s}")
    for v in variants:
        print(f"{v['flavor']:10s} {v['reading']:34s} {v['sigma']:7.4f} "
              f"{v['mae_mean']:9.4f} {v['mae_sd']:8.4f} "
              f"{mae_null_all - v['mae_mean']:+15.4f}")

    # primary oracle column (published flavor, reading a, seed 0) + CIs
    prim, _ = oracle_column("GI_folinate_independent", rel_pub, "a", seed=SEED)
    base["oracle"] = prim
    r_pool = paired_metric_difference_bootstrap(base.dropna(subset=["oracle"]),
                                                "position", "pred_mult", "oracle",
                                                "target", metric="mae",
                                                n_boot=N_BOOT, seed=SEED)
    impr_pool = -r_pool["observed_diff"]
    impr_lo, impr_hi = -r_pool["ci_hi"], -r_pool["ci_lo"]
    print(f"\nPRIMARY oracle (published, reading a), POOLED n={r_pool['n_rows']}: "
          f"improvement over null = {impr_pool:+.4f} "
          f"CI=[{impr_lo:+.4f},{impr_hi:+.4f}] "
          f"-> ceiling {'USABLE (CI excludes 0)' if impr_lo > 0 or impr_hi < 0 else 'NOT measurable (CI includes 0)'}")
    ceiling_usable = (impr_lo > 0) or (impr_hi < 0)
    if not ceiling_usable:
        print("PRE-REGISTERED RULE: no measurable ceiling exists — fraction claims skipped.")
        sys.exit(0)

    s = base.dropna(subset=["abs_gi", "oracle"]).copy()
    s["stratum"] = pd.qcut(s["abs_gi"], 3, labels=["low", "mid", "high"])
    hi = s[s["stratum"] == "high"]
    r_hi = paired_metric_difference_bootstrap(hi, "position", "pred_mult", "oracle",
                                              "target", metric="mae",
                                              n_boot=N_BOOT, seed=SEED)
    ceiling_high = -r_hi["observed_diff"]
    print(f"PRIMARY oracle, HIGH stratum (n={r_hi['n_rows']}, "
          f"{r_hi['n_clusters']} positions): improvement over null = "
          f"{ceiling_high:+.4f} CI=[{-r_hi['ci_hi']:+.4f},{-r_hi['ci_lo']:+.4f}]")

    print(f"\n6.3/6.2 ESM-2 vs null AGAINST that ceiling "
          f"(improvement = -diff; positive = ESM-2 better):")
    print(f"  pooled : ESM-2 improvement = {-ESM_VS_NULL_POOLED:+.6f} "
          f"= {-ESM_VS_NULL_POOLED / impr_pool * 100:+.2f}% of ceiling "
          f"{impr_pool:+.4f}   [saved task34 row: diff {ESM_VS_NULL_POOLED:+.9f}]")
    print(f"  high   : ESM-2 improvement = {-ESM_VS_NULL_HIGH:+.6f} "
          f"= {-ESM_VS_NULL_HIGH / ceiling_high * 100:+.2f}% of ceiling "
          f"{ceiling_high:+.4f}   [saved: diff {ESM_VS_NULL_HIGH:+.9f}; "
          f"MTHFR_RESULTS_LOG 6.3 prints '+0.00241 ESM-2 WORSE', "
          f"REVIEW_TRIAGE calls it '-0.00241 loss' — same number]")

    # =================== PART 2: disattenuation ============================
    print("\n" + "=" * 74)
    print(f"C3a-2  DISATTENUATION of rho(delta_ESM, e.b) "
          f"(joint position bootstrap, N_BOOT={N_BOOT})")
    print("=" * 74)
    ana2 = ana[["position", "delta_esm", "own_e_b"]].copy()
    syn2 = syn_own[syn_own["type"] == "synonymous"][["position", "own_e_b"]].dropna().reset_index(drop=True)
    pos_ana = ana2["position"].unique()
    pos_syn = syn2["position"].unique()
    union = np.union1d(pos_ana, pos_syn)
    ia = {p: ana2.index[ana2["position"] == p].to_numpy() for p in pos_ana}
    isyn = {p: syn2.index[syn2["position"] == p].to_numpy() for p in pos_syn}
    ea = ana2["own_e_b"].to_numpy()
    de = ana2["delta_esm"].to_numpy()
    es = syn2["own_e_b"].to_numpy()

    def disattenuate(idx_a, idx_s):
        r = _spearman(de[idx_a], ea[idx_a])
        va, vs = np.var(ea[idx_a]), np.var(es[idx_s]) if len(idx_s) else np.nan
        rel = 1 - vs / va if va > 0 and np.isfinite(vs) else np.nan
        return (r / np.sqrt(rel)) if (np.isfinite(rel) and rel > 0) else np.nan, r, rel

    i0a = np.arange(len(ana2))
    i0s = np.arange(len(syn2))
    d0, r0, rel0 = disattenuate(i0a, i0s)
    rng = np.random.default_rng(SEED)
    draws = np.empty(N_BOOT)
    rel_draws = np.empty(N_BOOT)
    for b in range(N_BOOT):
        drawn = rng.choice(union, size=len(union), replace=True)
        ja = np.concatenate([ia[p] for p in drawn if p in ia]) if any(p in ia for p in drawn) else np.array([], int)
        js = np.concatenate([isyn[p] for p in drawn if p in isyn]) if any(p in isyn for p in drawn) else np.array([], int)
        if len(ja) < 10 or len(js) < 2:
            draws[b] = np.nan
            rel_draws[b] = np.nan
            continue
        draws[b], _, rel_draws[b] = disattenuate(ja, js)
    n_valid = int(np.isfinite(draws).sum())
    lo, hi_ = np.nanpercentile(draws, [2.5, 97.5])
    ratio = abs(d0) / abs(r0)
    materially = ratio >= 1.25 and not (lo <= 0 <= hi_)
    print(f"point (row-level): rho_own = {r0:+.12f}  (gate-checked vs script 32)")
    print(f"reliability own e.b (point) = {rel0:.4f}   [per-draw rel: "
          f"mean {np.nanmean(rel_draws):.4f}, sd {np.nanstd(rel_draws, ddof=1):.4f}]")
    print(f"r_dis = rho / sqrt(rel) = {d0:+.6f}   (reliability of delta_esm assumed 1: "
          f"deterministic model output)")
    print(f"CI ({n_valid}/{N_BOOT} valid draws): [{lo:+.6f}, {hi_:+.6f}]")
    print(f"|r_dis|/|rho| = {ratio:.4f}   [pre-registered 'materially larger' "
          f"threshold 1.25 = ratio implied by rel=0.64, fixed in advance]")
    print(f"VERDICT: {'MATERIALLY LARGER (ratio >= 1.25 AND CI excludes 0)' if materially else 'NOT MATERIAL (fails ratio >= 1.25 or CI includes 0)'}")
    print(f"published-flavor point for the record: r_dis_pub = "
          f"{r_pub / np.sqrt(rel_pub):+.6f} (rho {r_pub:+.6f}, rel {rel_pub:.4f}; "
          f"no CI — own flavor is the task's −0.088)")

    # ---- save ---------------------------------------------------------------
    o1 = PROC / "task47_c3a_oracle.csv"
    pd.DataFrame(variants).assign(
        ceiling_pooled=impr_pool, ceiling_pooled_ci_lo=impr_lo,
        ceiling_pooled_ci_hi=impr_hi, ceiling_high=ceiling_high,
        esm_improvement_pooled=-ESM_VS_NULL_POOLED,
        esm_improvement_high=-ESM_VS_NULL_HIGH).to_csv(o1, index=False)
    o2 = PROC / "task47_c3a_disattenuation.csv"
    pd.DataFrame([{"rho_own": r0, "rho_pub": r_pub, "rel_own": rel_own,
                   "rel_pub": rel_pub, "r_dis_own": d0, "ci_lo": float(lo),
                   "ci_hi": float(hi_), "ratio": ratio,
                   "materially_larger": bool(materially),
                   "n_valid_draws": n_valid}]).to_csv(o2, index=False)
    print(f"\nSaved {o1.name} and {o2.name}")

    print("\nLIMITATIONS (also in the docstring): oracle is in-sample")
    print("reconstruction (circularity disclosed above); its CI uses the")
    print("seed-0 noise draw (10-draw mean/sd printed above). Point rho is")
    print("row-level like script 32; only the CI is position-clustered.")
    print("delta_esm reliability assumed 1. Reading (b) assumes measurement")
    print("error uncorrelated with delta_esm. Reliability treats synonymous")
    print("e.b spread as pure noise (log 2.3's own control).")
