"""
Script 38: matched-strength gap with an anchor EXOGENOUS to the WT arm.

Every confound control before this one -- placebos (29), matched-strength
synthetic (30), richer anchor (31), cross-predictor matched baseline (36)
-- includes w.fitness as an ingredient, which is itself derived from THIS
assay's wild-type arm. A reviewer correctly flagged that this means even
the "fair" tests share a common WT-informed anchor, so none of them can
fully rule out the construction-artifact concern.

This rebuilds the richer anchor with w.fitness REMOVED entirely -- kept:
Grantham, BLOSUM62, RSA, domain, none of which have any structural
connection to this assay's WT arm. Run for ESM-2 and all four conventional
predictors (PROVEAN, SIFT, PolyPhen-2 x2), matching the exact machinery
of scripts 31/36.

METHODOLOGICAL NOTE, found while building this: a SINGLE point-estimate
gap (one synthetic noise draw) is not a stable, reproducible number on its
own -- confirmed directly: identical alpha, identical anchor, but a
different upstream row order changed a gap from +0.079 to +0.045, purely
because synthetic noise is assigned positionally. Only the full bootstrap
distribution (many draws, resampled by position, alpha refit each time)
is trustworthy. This script reports bootstrap means and CIs as the primary
number; point estimates from a single draw are NOT reported as standalone
results anywhere in this project going forward.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.io import load_insilico_predictors, load_derived_maps, load_structural_features
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


def bootstrap_gap(df, col, anchor_col, positions, idx_by_pos, n_boot, seed):
    """Returns array of n_boot gap values, position-resampled, alpha refit each time."""
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(positions, size=len(positions), replace=True)
        rows = np.concatenate([idx_by_pos[p] for p in drawn])
        bs = df.iloc[rows].reset_index(drop=True)
        dd2 = bs.dropna(subset=[col, "abs_gi", "target", anchor_col]).copy()
        dd2["anchor_z"] = zscore(dd2[anchor_col])
        cuts = np.quantile(dd2["abs_gi"], [1 / 3, 2 / 3])
        dd2["_stratum"] = np.digitize(dd2["abs_gi"], cuts)
        dd2["_low"] = dd2["_stratum"] == 0
        real = strat_rho(dd2, col)
        alpha = fit_alpha(dd2, real[0], rng)
        dd2["_syn"] = make_synth(alpha, dd2["anchor_z"].to_numpy(), rng)
        out[b] = real[2] - strat_rho(dd2, "_syn")[2]
    return out


if __name__ == "__main__":
    d = pd.read_csv(PROC / "phase5_analysis_table.csv")
    d["abs_gi"] = d["GI_folinate_independent"].abs()
    ins = load_insilico_predictors()
    d = d.merge(ins.rename(columns={"pos": "position", "ref": "wt_aa", "alt": "mut_aa"}),
               on=["position", "wt_aa", "mut_aa"], how="left")
    der = load_derived_maps()
    d = d.merge(pd.DataFrame({"hgvs_pro": der["hgvs"], "w.fitness": der["w.fitness"]}),
               on="hgvs_pro", how="left")
    d["pp2div_flip"] = -d["pp2div"]; d["pp2var_flip"] = -d["pp2var"]
    d = add_substitution_features(d)
    d = add_structural_features(d, load_structural_features())
    d["domain"] = d["domain"].fillna("unassigned")
    d["region"] = assign_region(d["position"])

    d["anchor_with_wf"] = crossfit_ols_anchor(d, "position", "target",
        ["w.fitness", "grantham", "blosum62", "rsa"], "domain", seed=SEED)
    d["anchor_no_wf"] = crossfit_ols_anchor(d, "position", "target",
        ["grantham", "blosum62", "rsa"], "domain", seed=SEED)

    for c in ["anchor_with_wf", "anchor_no_wf"]:
        s = d.dropna(subset=[c, "target"])
        print(f"{c}: rho with target = {_spearman(s[c], s['target']):+.4f}  n={len(s)}")

    d_full = d.dropna(subset=["model_C", "abs_gi", "target"]).reset_index(drop=True)
    positions = d_full["position"].unique()
    idx_by_pos = {p: d_full.index[d_full["position"] == p].to_numpy() for p in positions}

    PREDS = [("model_C", "ESM-2"), ("provean", "PROVEAN"), ("sift", "SIFT"),
             ("pp2div_flip", "PolyPhen-2 HumDiv"), ("pp2var_flip", "PolyPhen-2 HumVar")]

    print(f"\n{'='*88}\nBOOTSTRAPPED GAP: WITH vs WITHOUT w.fitness ({N_BOOT} draws each)\n{'='*88}")
    rows = []
    for col, lbl in PREDS:
        b_with = bootstrap_gap(d_full, col, "anchor_with_wf", positions, idx_by_pos, N_BOOT, SEED)
        b_no = bootstrap_gap(d_full, col, "anchor_no_wf", positions, idx_by_pos, N_BOOT, SEED + 1)
        lo_w, hi_w = np.nanpercentile(b_with, [2.5, 97.5])
        lo_n, hi_n = np.nanpercentile(b_no, [2.5, 97.5])
        surv_w = "SURVIVES" if lo_w > 0 else ("BELOW ZERO" if hi_w < 0 else "crosses 0")
        surv_n = "SURVIVES" if lo_n > 0 else ("BELOW ZERO" if hi_n < 0 else "crosses 0")
        print(f"  {lbl:20s} WITH w.fitness:    mean={b_with.mean():+.4f} CI=[{lo_w:+.4f},{hi_w:+.4f}] {surv_w}")
        print(f"  {' '*20} WITHOUT w.fitness: mean={b_no.mean():+.4f} CI=[{lo_n:+.4f},{hi_n:+.4f}] {surv_n}")
        rows.append({"predictor": col, "label": lbl,
                    "gap_with_wf_mean": b_with.mean(), "gap_with_wf_lo": lo_w, "gap_with_wf_hi": hi_w,
                    "gap_no_wf_mean": b_no.mean(), "gap_no_wf_lo": lo_n, "gap_no_wf_hi": hi_n,
                    "survives_with_wf": lo_w > 0, "survives_no_wf": lo_n > 0})

    out = pd.DataFrame(rows)
    out.to_csv(PROC / "task_exogenous_anchor_test.csv", index=False)
    print(f"\n{'='*88}")
    if out["survives_no_wf"].any():
        print("At least one predictor's excess survives WITHOUT w.fitness in the anchor --")
        print("the earlier result is not purely an artifact of the WT-arm-derived ingredient.")
    else:
        print("NO predictor's excess survives once w.fitness is removed from the anchor.")
        print("The earlier 'genuine excess' results were entirely dependent on including a")
        print("WT-arm-derived quantity in the confound anchor -- the deepest form of the")
        print("circularity concern is confirmed.")
    print("="*88)
    print(f"\nSaved to task_exogenous_anchor_test.csv")
