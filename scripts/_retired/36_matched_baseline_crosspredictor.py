"""
Script 36: matched-baseline cross-predictor comparison -- the decisive test.

Script 34's raw comparison found ESM-2 degrades more than PROVEAN/SIFT/
PolyPhen-2 HumDiv in absolute terms. A review correctly identified this as
repeating the exact baseline-mismatch problem scripts 30-31 solved for the
placebo comparison: ESM-2 starts at a higher raw correlation (+0.53) than
the conventional predictors (+0.37-0.42), so it mechanically has more room
to fall. An absolute-drop comparison across unequal starting points is not
directly interpretable, and the same fix that worked for the placebo case
applies here -- build a matched-strength synthetic for EACH predictor
independently (same richer anchor as script 31: position-cross-fit OLS on
w.fitness + grantham + blosum62 + rsa + domain), compare each predictor's
own gap over its own matched-strength synthetic, not raw degradation.

RESULT: once matched, ESM-2's gap (+0.077) is nearly identical to
PolyPhen-2 HumDiv's (+0.076), and the position-cluster-bootstrapped
differences (alpha refit inside every resample) are ALL indistinguishable
from zero -- PROVEAN, SIFT, PolyPhen-2 HumDiv, PolyPhen-2 HumVar. The raw
degradation comparison in script 34 was a baseline-mismatch artifact, not
a real ESM-2-specific effect. This is the test that decides the question
script 34 could not: ESM-2's genuine excess over a rich confound anchor is
real (script 31, CI [+0.022,+0.125]) but is NOT distinguishable from what
conventional sequence-based predictors show under the identical test.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.io import load_insilico_predictors, load_derived_maps, WT_COND_COLS, load_structural_features
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.regions import assign_region
from scripts.lib.stats import _spearman

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def zscore(x):
    x = np.asarray(x, dtype=float)
    return (x - np.nanmean(x)) / np.nanstd(x)


def crossfit_ols_anchor(df, position_col, target_col, cont_cols, cat_col, n_folds=5, seed=0):
    dd = df[[position_col, target_col, cat_col] + cont_cols].dropna()
    rng = np.random.default_rng(seed)
    folds = np.array_split(rng.permutation(dd[position_col].unique()), n_folds)
    preds = pd.Series(np.nan, index=df.index, dtype=float)
    for fold in folds:
        test_mask = dd[position_col].isin(fold)
        train, test = dd[~test_mask], dd[test_mask]
        if len(train) == 0 or len(test) == 0:
            continue
        dum_tr = pd.get_dummies(train[cat_col], prefix="dom", drop_first=True, dtype=float)
        dum_te = pd.get_dummies(test[cat_col], prefix="dom", drop_first=True, dtype=float)
        dum_te = dum_te.reindex(columns=dum_tr.columns, fill_value=0.0)
        X_tr = sm.add_constant(pd.concat([train[cont_cols], dum_tr], axis=1))
        X_te = sm.add_constant(pd.concat([test[cont_cols], dum_te], axis=1), has_constant="add")
        X_te = X_te.reindex(columns=X_tr.columns, fill_value=0.0)
        m = sm.OLS(train[target_col], X_tr).fit()
        preds.loc[test.index] = m.predict(X_te).to_numpy()
    return preds


def strat_rho(dd, pred, n=3):
    s = dd.dropna(subset=[pred, "abs_gi", "target"])
    cuts = np.quantile(s["abs_gi"], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s["abs_gi"], cuts)
    return [_spearman(s[pred].to_numpy()[k == i], s["target"].to_numpy()[k == i]) for i in range(n)]


def make_synth(alpha, anchor_z, rng):
    noise = rng.standard_normal(len(anchor_z))
    return alpha * anchor_z + np.sqrt(max(1 - alpha ** 2, 0.0)) * noise


def fit_alpha(dd, target_low, rng, iters=20):
    lo, hi, mid = 0.0, 1.0, 0.5
    for _ in range(iters):
        mid = (lo + hi) / 2
        syn = make_synth(mid, dd["anchor_z"].to_numpy(), rng)
        r = _spearman(syn[dd["_low"].to_numpy()], dd.loc[dd["_low"], "target"].to_numpy())
        lo, hi = (mid, hi) if r < target_low else (lo, mid)
    return mid


def gap_for(dd, col, rng):
    dd2 = dd.dropna(subset=[col, "abs_gi", "target", "anchor_z"]).copy()
    cuts = np.quantile(dd2["abs_gi"], [1 / 3, 2 / 3])
    dd2["_stratum"] = np.digitize(dd2["abs_gi"], cuts)
    dd2["_low"] = dd2["_stratum"] == 0
    real = strat_rho(dd2, col)
    alpha = fit_alpha(dd2, real[0], rng)
    dd2["_syn"] = make_synth(alpha, dd2["anchor_z"].to_numpy(), rng)
    return real[2] - strat_rho(dd2, "_syn")[2], alpha, real, strat_rho(dd2, "_syn")[2]


if __name__ == "__main__":
    d = pd.read_csv(PROC / "phase5_analysis_table.csv")
    d["abs_gi"] = d["GI_folinate_independent"].abs()
    ins = load_insilico_predictors()
    d = d.merge(ins.rename(columns={"pos": "position", "ref": "wt_aa", "alt": "mut_aa"}),
               on=["position", "wt_aa", "mut_aa"], how="left")
    der = load_derived_maps()
    d = d.merge(pd.DataFrame({"hgvs_pro": der["hgvs"], "placebo_wfitness": der["w.fitness"]}),
               on="hgvs_pro", how="left")
    d["pp2div_flip"] = -d["pp2div"]; d["pp2var_flip"] = -d["pp2var"]
    d = add_substitution_features(d)
    d = add_structural_features(d, load_structural_features())
    d["region"] = assign_region(d["position"])
    d["w.fitness"] = d["placebo_wfitness"]

    d["anchor_raw"] = crossfit_ols_anchor(d, "position", "target",
                                          ["w.fitness", "grantham", "blosum62", "rsa"],
                                          "domain", n_folds=5, seed=SEED)
    d["anchor_z"] = zscore(d["anchor_raw"])
    print(f"n with anchor: {d['anchor_raw'].notna().sum()}")

    PREDS = [("model_C", "ESM-2 (A222V bg)"), ("provean", "PROVEAN"), ("sift", "SIFT"),
             ("pp2div_flip", "PolyPhen-2 HumDiv"), ("pp2var_flip", "PolyPhen-2 HumVar")]

    rng = np.random.default_rng(SEED)
    print("\n" + "=" * 84)
    print("MATCHED-BASELINE GAP PER PREDICTOR (point estimates)")
    print("=" * 84)
    point_rows = []
    for col, lbl in PREDS:
        gap, alpha, real, syn_high = gap_for(d, col, rng)
        print(f"  {lbl:20s} real_low={real[0]:+.4f} real_high={real[2]:+.4f} "
              f"alpha={alpha:.3f} synth_high={syn_high:+.4f}  GAP={gap:+.4f}")
        point_rows.append({"predictor": col, "label": lbl, "real_low": real[0],
                          "real_high": real[2], "alpha": alpha, "synth_high": syn_high, "gap": gap})
    pd.DataFrame(point_rows).to_csv(PROC / "task_matched_baseline_gaps.csv", index=False)

    d_full = d.dropna(subset=["model_C", "abs_gi", "target", "anchor_z"]).reset_index(drop=True)
    positions = d_full["position"].unique()
    idx_by_pos = {p: d_full.index[d_full["position"] == p].to_numpy() for p in positions}

    print(f"\n" + "=" * 84)
    print(f"BOOTSTRAPPED GAP DIFFERENCES vs ESM-2 ({N_BOOT} draws, alpha refit each time)")
    print("=" * 84)
    diff_rows = []
    for col, lbl in [("provean", "PROVEAN"), ("sift", "SIFT"),
                     ("pp2div_flip", "PolyPhen-2 HumDiv"), ("pp2var_flip", "PolyPhen-2 HumVar")]:
        point = gap_for(d_full, "model_C", rng)[0] - gap_for(d_full, col, rng)[0]
        boot = np.empty(N_BOOT)
        for b in range(N_BOOT):
            drawn = rng.choice(positions, size=len(positions), replace=True)
            rows = np.concatenate([idx_by_pos[p] for p in drawn])
            bs = d_full.iloc[rows].reset_index(drop=True)
            boot[b] = gap_for(bs, "model_C", rng)[0] - gap_for(bs, col, rng)[0]
        lo, hi = np.nanpercentile(boot, [2.5, 97.5])
        v = "ESM-2 gap LARGER" if lo > 0 else ("ESM-2 gap SMALLER" if hi < 0 else "INDISTINGUISHABLE")
        print(f"  ESM-2 gap minus {lbl:20s} diff={point:+.4f}  CI=[{lo:+.4f},{hi:+.4f}]  -> {v}")
        diff_rows.append({"predictor": col, "label": lbl, "point_diff": point,
                         "ci_lo": lo, "ci_hi": hi, "verdict": v})

    pd.DataFrame(diff_rows).to_csv(PROC / "task_matched_baseline_crosspredictor.csv", index=False)
    print(f"\n{'='*84}")
    all_indist = all(r["verdict"] == "INDISTINGUISHABLE" for r in diff_rows)
    if all_indist:
        print("VERDICT: ESM-2's matched-baseline excess is NOT distinguishable from any of the")
        print("four conventional predictors tested. The raw-degradation comparison in script 34")
        print("was a baseline-mismatch artifact. ESM-2's real, small excess over the richer")
        print("confound anchor (script 31) is shared with conventional sequence-based")
        print("predictors, not specific to protein language models.")
    print("=" * 84)
    print(f"\nSaved to task_matched_baseline_crosspredictor.csv")
