"""
Task C1 (review-triage): one reconciliation table + three targeted tests
behind the unresolved rank-vs-MAE tension (log 4.5 vs 6.3).

C1a  One table: rows = predictors {S_WT, S_A222V, delta_ESM, matched
     synthetic, BLOSUM62, Grantham, w.fitness} x columns =
     {A222V fitness, e.b, w.fitness} x {rank, MAE, MSE} x {all/low/mid/high}.
C1b  Does S(v|WT) (no background supplied) retain as much HIGH-stratum rank
     signal over its matched synthetic as S(v|A222V) does? If yes, 4.5's
     "retention" is not about background information at all.
C1c  Do trivial WT-independent predictors (BLOSUM62, Grantham) also beat
     their matched synthetics in the high stratum? If yes, script 30 was
     measuring noise-sharing with w.fitness, not epistasis detection.
C1d  Direct rank correlation S(v|A222V) vs S(v|WT).

PRE-REGISTERED DECISION RULES (fixed before running; AGENTS.md §6):
  * Analysis set: phase5 rows with everything non-null (published e.b,
    own_e_b, delta_esm, esm2_score, esm2_score_a222v_bg,
    base_functionality, f_bar_a222v, grantham, blosum62) — expected
    10,757; the actual n is printed and any mismatch is a red flag.
  * Strata for the TABLE: pd.qcut |e.b| terciles (identical to script 34 /
    log 6.3). Strata for the GAP TESTS: script 30's quantile-digitize
    (identical to script 30) — each test mirrors the script it reconciles.
  * rank = Spearman; MAE/MSE = evaluated after cross-fit ISOTONIC
    calibration pred->target (position-held-out, 5 folds, house
    crossfit_isotonic_by_position). Rank alone is structurally blind to
    no-interaction models (AGENTS.md §8) — that is why MAE/MSE exist here.
  * Matched synthetic = script 30's exact construction:
    alpha*z(w.fitness) + sqrt(1-alpha^2)*N(0,1), bisection-matched to THAT
    predictor's own low-stratum rho vs the A222V-fitness target, seed 0.
    For the table, one canonical synthetic matched to S_A222V (script 30's
    original) is used in every cell.
  * Gap tests: high-stratum rho(pred) − rho(syn_pred), position bootstrap,
    alpha REFIT inside every draw (script 30 pattern), all four predictors
    computed on the SAME draws (paired). N_BOOT from env, default 1000.
  * C1b verdict: CI of (gap_C − gap_A) includes 0 => "S_WT retains as much
    as S_A222V" (retention not background-specific).
  * C1c verdict: gap_blosum or gap_grantham CI > 0 => trivial predictors
    also beat their matched synthetics (script 30's 'beat' is generic).

LIMITATIONS: synthetic noise is a single seed-0 draw per evaluation —
the bootstrap resamples positions but keeps the noise draw fixed (same
limitation script 30 has; stated, not hidden). Isotonic MAE is evaluated
on cross-fit predictions, so calibration error is included (conservative).
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import _spearman, crossfit_isotonic_by_position
from scripts.lib.features import add_substitution_features

N_BOOT = int(os.environ.get("N_BOOT", 1000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - np.nanmean(x)) / np.nanstd(x)


def strat_rho(d, pred, gi_col="abs_gi", target_col="target", n=3):
    """Script 30's exact stratum machinery (quantile digitize inside the call)."""
    s = d.dropna(subset=[pred, gi_col, target_col])
    cuts = np.quantile(s[gi_col], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s[gi_col], cuts)
    return [_spearman(s[pred].to_numpy()[k == i], s[target_col].to_numpy()[k == i])
            for i in range(n)]


def make_synthetic(alpha, anchor_z, rng):
    noise = rng.standard_normal(len(anchor_z))
    return alpha * anchor_z + np.sqrt(max(1 - alpha ** 2, 0.0)) * noise


def fit_alpha(d, target_low_rho, rng, iters=25):
    lo, hi = 0.0, 1.0
    mid = 0.5
    for _ in range(iters):
        mid = (lo + hi) / 2
        syn = make_synthetic(mid, d["anchor_z"].to_numpy(), rng)
        r = _spearman(syn[d["_lowmask"].to_numpy()],
                      d.loc[d["_lowmask"], "target"].to_numpy())
        lo, hi = (mid, hi) if r < target_low_rho else (lo, mid)
    return mid


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = add_substitution_features(df)
    df["delta_esm"] = df["esm2_score_a222v_bg"] - df["esm2_score"]
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    need = ["GI_folinate_independent", "own_e_b", "delta_esm", "esm2_score",
            "esm2_score_a222v_bg", "base_functionality", "target",
            "grantham", "blosum62"]
    d = df.dropna(subset=need).reset_index(drop=True)
    print(f"Analysis set: {len(d)} variants, {d['position'].nunique()} positions "
          f"(expected 10,757 — mismatch would be a red flag)")
    if len(d) != 10757:
        print("*** n != 10,757 — investigate before quoting anything below ***")

    # ---- canonical matched synthetic (script 30's exact recipe) ----------
    cuts = np.quantile(d["abs_gi"], [1 / 3, 2 / 3])
    d["_stratum"] = np.digitize(d["abs_gi"], cuts)
    d["_lowmask"] = d["_stratum"] == 0
    d["anchor_z"] = zscore(d["base_functionality"])
    rng = np.random.default_rng(SEED)
    real_C = strat_rho(d, "esm2_score_a222v_bg")
    alpha_c = fit_alpha(d, real_C[0], rng)
    d["_syn_canonical"] = make_synthetic(alpha_c, d["anchor_z"].to_numpy(), rng)
    print(f"Canonical matched alpha (to S_A222V low-stratum rho={real_C[0]:+.4f}): {alpha_c:.4f}")

    # =================== C1a: the big table =============================
    print("\n" + "=" * 74)
    print("C1a  RECONCILIATION TABLE (rank=Spearman; MAE/MSE on cross-fit isotonic)")
    print("=" * 74)
    preds = [("S_WT", "esm2_score"),
             ("S_A222V", "esm2_score_a222v_bg"),
             ("delta_ESM", "delta_esm"),
             ("matched_synthetic", "_syn_canonical"),
             ("BLOSUM62", "blosum62"),
             ("Grantham", "grantham"),
             ("w.fitness", "base_functionality")]
    targets = [("A222V_fitness", "target"),
               ("e.b", "GI_folinate_independent"),
               ("w.fitness", "base_functionality")]
    d["stratum_lbl"] = pd.qcut(d["abs_gi"], 3, labels=["low", "mid", "high"])
    strata = [("all", d)] + [(lvl, d[d["stratum_lbl"] == lvl])
                             for lvl in ["low", "mid", "high"]]

    cal_cache = {}
    for t_lbl, t_col in targets:
        for p_lbl, p_col in preds:
            if p_col == t_col:
                # identity pair (w.fitness predicting w.fitness): calibrated
                # prediction is the value itself; passing one column name
                # twice would duplicate it and break isotonic's 1-column X.
                cal_cache[(p_col, t_col)] = d[t_col].copy()
                continue
            cal_cache[(p_col, t_col)] = crossfit_isotonic_by_position(
                d, "position", p_col, t_col, n_folds=5, seed=SEED)

    rows = []
    print(f"\n{'predictor':18s} {'target':14s} {'metric':6s} " +
          " ".join(f"{s[0]:>12s}" for s in strata))
    for p_lbl, p_col in preds:
        for t_lbl, t_col in targets:
            cal = cal_cache[(p_col, t_col)]
            cells = {}
            for metric in ["rank", "mae", "mse"]:
                vals = []
                for s_lbl, sub in strata:
                    m = sub[[p_col, t_col]].notna().all(axis=1)
                    idx = sub.index[m]
                    pv = sub.loc[idx, p_col].to_numpy()
                    tv = sub.loc[idx, t_col].to_numpy()
                    if metric == "rank":
                        v = _spearman(pv, tv)
                    else:
                        cv = cal.loc[idx].to_numpy()
                        ok = np.isfinite(cv)
                        v = (np.abs(cv[ok] - tv[ok]).mean() if metric == "mae"
                             else np.mean((cv[ok] - tv[ok]) ** 2))
                    vals.append(v)
                    rows.append({"predictor": p_lbl, "target": t_lbl,
                                 "metric": metric, "stratum": s_lbl, "value": v,
                                 "n": int(m.sum())})
                cells[metric] = vals
            for metric in ["rank", "mae", "mse"]:
                print(f"{p_lbl:18s} {t_lbl:14s} {metric:6s} " +
                      " ".join(f"{v:12.4f}" for v in cells[metric]))
    tbl = PROC / "task45_c1_table.csv"
    pd.DataFrame(rows).to_csv(tbl, index=False)
    print(f"Saved table to {tbl}")

    # =================== C1d: direct rank ===============================
    r_cd = _spearman(d["esm2_score_a222v_bg"], d["esm2_score"])
    print("\n" + "=" * 74)
    print("C1d  DIRECT: S(v|A222V) vs S(v|WT)")
    print("=" * 74)
    print(f"  Spearman = {r_cd:.6f}  (n={len(d)})")
    print(f"  -> {'0.99+ : the MAE story rests on a small number of rank swaps' if r_cd >= 0.99 else 'below 0.99 — rank swaps are substantial'}")

    # =================== C1b/C1c: matched-synthetic gaps ================
    print("\n" + "=" * 74)
    print(f"C1b/C1c  HIGH-STRATUM GAP vs MATCHED SYNTHETIC "
          f"(position bootstrap, alpha refit per draw, {N_BOOT} draws)")
    print("=" * 74)
    gpreds = [("S_A222V", "esm2_score_a222v_bg"),
              ("S_WT", "esm2_score"),
              ("BLOSUM62", "blosum62"),
              ("Grantham", "grantham")]
    rng2 = np.random.default_rng(SEED)
    obs_rho = {l: strat_rho(d, c) for l, c in gpreds}
    obs_alpha, obs_syn_rho, obs_gap = {}, {}, {}
    for l, c in gpreds:
        a = fit_alpha(d, obs_rho[l][0], rng2)
        syn = make_synthetic(a, d["anchor_z"].to_numpy(), rng2)
        # strat_rho needs a column; put syn into a temp column
        d["_syn_tmp"] = syn
        sr = strat_rho(d, "_syn_tmp")
        obs_alpha[l] = a
        obs_syn_rho[l] = sr
        obs_gap[l] = obs_rho[l][2] - sr[2]
    print(f"\n{'predictor':12s} {'low':>9s} {'syn_low':>9s} {'alpha':>7s} "
          f"{'high':>9s} {'syn_high':>9s} {'gap':>9s}")
    for l, _ in gpreds:
        print(f"{l:12s} {obs_rho[l][0]:+9.4f} {obs_syn_rho[l][0]:+9.4f} "
              f"{obs_alpha[l]:7.4f} {obs_rho[l][2]:+9.4f} "
              f"{obs_syn_rho[l][2]:+9.4f} {obs_gap[l]:+9.4f}")

    positions = d["position"].unique()
    idx_by_pos = {p_: d.index[d["position"] == p_].to_numpy() for p_ in positions}
    keys = [l for l, _ in gpreds]
    boot = {l: np.empty(N_BOOT) for l in keys}
    for b in range(N_BOOT):
        drawn = rng2.choice(positions, size=len(positions), replace=True)
        rows_i = np.concatenate([idx_by_pos[p_] for p_ in drawn])
        bs = d.iloc[rows_i].reset_index(drop=True)
        cuts_b = np.quantile(bs["abs_gi"], [1 / 3, 2 / 3])
        bs["_stratum"] = np.digitize(bs["abs_gi"], cuts_b)
        bs["_lowmask"] = bs["_stratum"] == 0
        for l, c in gpreds:
            rr = strat_rho(bs, c)
            a_b = fit_alpha(bs, rr[0], rng2, iters=15)
            bs["_syn_tmp"] = make_synthetic(a_b, bs["anchor_z"].to_numpy(), rng2)
            boot[l][b] = rr[2] - strat_rho(bs, "_syn_tmp")[2]
        if (b + 1) % max(1, N_BOOT // 10) == 0:
            print(f"  {b+1}/{N_BOOT} draws")

    def summ(x):
        lo, hi = np.nanpercentile(x, [2.5, 97.5])
        p = float(min(2 * min((np.nanmean(x <= 0), np.nanmean(x >= 0))), 1.0))
        return float(np.nanmean(x)), float(lo), float(hi), p

    print(f"\n{'predictor':12s} {'gap':>9s} {'boot_mean':>10s} {'CI_lo':>9s} {'CI_hi':>9s}")
    for l in keys:
        gm, lo, hi, _ = summ(boot[l])
        print(f"{l:12s} {obs_gap[l]:+9.4f} {gm:+10.4f} {lo:+9.4f} {hi:+9.4f}")

    dC_A = boot["S_A222V"] - boot["S_WT"]
    m, lo, hi, p = summ(dC_A)
    print(f"\nC1b: gap(S_A222V) - gap(S_WT) = {obs_gap['S_A222V'] - obs_gap['S_WT']:+.4f} "
          f"(boot mean {m:+.4f}) CI=[{lo:+.4f},{hi:+.4f}] p={p:.4f}")
    v_b1 = ("RETENTION IS NOT BACKGROUND-SPECIFIC (CI includes 0)"
            if lo <= 0 <= hi else
            "S_A222V retains MORE than S_WT (CI excludes 0)")
    print(f"  -> {v_b1}")
    for l in ["BLOSUM62", "Grantham"]:
        gm, lo, hi, pv = summ(boot[l])
        dcx = boot[l]
        _, dlo, dhi, dp = summ(boot["S_A222V"] - boot[l])
        print(f"C1c: gap({l}) = {obs_gap[l]:+.4f} CI=[{lo:+.4f},{hi:+.4f}] "
              f"{'SIG>0 (also beats its synthetic)' if lo > 0 else 'not > 0'}; "
              f"gap(S_A222V)-gap({l}) CI=[{dlo:+.4f},{dhi:+.4f}]")

    gap_rows = [{"predictor": l, "alpha": obs_alpha[l],
                 "low_rho": obs_rho[l][0], "syn_low_rho": obs_syn_rho[l][0],
                 "high_rho": obs_rho[l][2], "syn_high_rho": obs_syn_rho[l][2],
                 "gap_high": obs_gap[l],
                 "gap_boot_mean": float(np.nanmean(boot[l])),
                 "gap_ci_lo": float(np.nanpercentile(boot[l], 2.5)),
                 "gap_ci_hi": float(np.nanpercentile(boot[l], 97.5))}
                for l in keys]
    gap_rows.append({"predictor": "C1b_diff_A222V_minus_WT",
                     "gap_high": float(obs_gap["S_A222V"] - obs_gap["S_WT"]),
                     "gap_boot_mean": m, "gap_ci_lo": lo, "gap_ci_hi": hi,
                     "p": p})
    gout = PROC / "task45_c1_gaps.csv"
    pd.DataFrame(gap_rows).to_csv(gout, index=False)
    mout = PROC / "task45_c1_misc.csv"
    pd.DataFrame([{"C1d_rho": r_cd, "n": len(d), "canonical_alpha": alpha_c}]).to_csv(mout, index=False)
    print(f"\nSaved {gout} and {mout}")
    print("\nSingle-seed synthetic noise (same limitation as script 30); bootstrap")
    print("resamples positions and refits alpha but keeps the noise draw fixed.")
