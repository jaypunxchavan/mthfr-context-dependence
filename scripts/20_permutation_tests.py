"""
Subtask B4-B5: Randomization tests (proposal 5.6f).

Two hypotheses need two different nulls. Stating each in words first,
because "shuffle the condition labels" silently picks one and would
quietly test the wrong thing for e_b.

NULL 1 -- for e_r (folinate-DEPENDENT interaction)
  "The deviation from the no-interaction expectation carries no real
   concentration trend."
  Shuffle: within each variant, permute the four (residual, se) PAIRS
  across concentration slots. Permuting the pair jointly leaves
  sum(w*y) and sum(w) unchanged, so the weighted mean residual -- and
  hence e_b -- is preserved exactly, while any concentration trend is
  destroyed. This targets e_r specifically, which is the point.
  Requires re-deriving e_r on every shuffle: the reason own_context.py
  exists at all.

NULL 2 -- for e_b (folinate-INDEPENDENT interaction)
  e_b is a constant offset, so permuting concentration slots leaves it
  untouched and cannot null it. Instead this permutes the context values
  across POSITION blocks, breaking the variant-to-error pairing while
  preserving within-position structure.
  This is an ASSOCIATION-level permutation test, not a re-derivation null:
  it asks whether error and context are paired more strongly than chance,
  not whether the interaction itself exceeds measurement noise. Weaker,
  and labelled as such rather than presented as equivalent to NULL 1.

Permutation is at POSITION level throughout -- pseudoreplication fixed in
the confidence intervals would otherwise be reintroduced in the p-values.

P-VALUES APPLY TO own_e_b / own_e_r, not the published values. The
validation correlation against the published metrics is printed alongside
so the reader can judge how far the result transfers.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scipy.stats import spearmanr
from scripts.lib.own_context import (fit_single_arm, fit_interaction, wls_line,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS, MT_SCORE_COLS, MT_SE_COLS)
from scripts.lib.stats import _spearman

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    d = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    W = d[WT_SCORE_COLS].to_numpy(float); Wse = d[WT_SE_COLS].to_numpy(float)
    M = d[MT_SCORE_COLS].to_numpy(float); Mse = d[MT_SE_COLS].to_numpy(float)

    w = fit_single_arm(W, Wse)
    w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(d["hgvs"].to_numpy() == "p.Ala222Val")[0][0])
    e1 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                         w["fitness"][i222], w["remediation"][i222])
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1["e_r"][keep])
    e2 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                         w["fitness"][i222], w["remediation"][i222], correction=(cb, cr))

    base = pd.DataFrame({"hgvs_pro": d["hgvs"], "type": d["type"],
                         "own_e_b": e2["e_b"], "own_e_r": e2["e_r"],
                         "pub_e_b": d["e.b"], "pub_e_r": d["e.r"]})
    resid, m_se, valid = e2["resid"], Mse, e2["valid"]

    ph3 = pd.read_csv(PROC / "phase3_analysis_table.csv")[
        ["hgvs_pro", "position", "central_error_rank", "central_error_cal"]]
    merged = base[base["type"] == "substitution"].merge(ph3, on="hgvs_pro", how="inner")
    idx = merged.index.to_numpy()
    row_of = {h: i for i, h in enumerate(d["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in merged["hgvs_pro"]])

    for c in ["own_e_b", "own_e_r"]:
        ok = merged[c].notna() & merged["pub_" + c[4:]].notna()
        print(f"validation {c} vs published: rho="
              f"{spearmanr(merged.loc[ok,c], merged.loc[ok,'pub_'+c[4:]]).statistic:.4f}")

    print(f"\n{'='*72}\nNULL 1: e_r  (re-derivation null, {N_PERM} permutations)\n{'='*72}")
    R, S, V = resid[src], m_se[src], valid[src]
    for err in ["central_error_rank", "central_error_cal"]:
        sub = merged[[err]].copy(); sub["ctx"] = merged["own_e_r"].abs()
        good = sub["ctx"].notna() & sub[err].notna()
        obs = _spearman(sub.loc[good, "ctx"], sub.loc[good, err])
        errv = sub[err].to_numpy()
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            order = np.argsort(rng.random(R.shape), axis=1)
            _, er_p, _ = wls_line(np.take_along_axis(R, order, 1),
                                  np.take_along_axis(S, order, 1), CONCS,
                                  np.take_along_axis(V, order, 1))
            g = np.isfinite(er_p) & np.isfinite(errv)
            null[p] = _spearman(np.abs(er_p[g]), errv[g])
        pv = (np.abs(null) >= abs(obs)).mean()
        print(f"  {err}: observed rho={obs:+.4f}  null mean={null.mean():+.4f} "
              f"sd={null.std():.4f}  p={pstr(pv)}")

    print(f"\n{'='*72}\nNULL 2: e_b  (association-level null -- weaker, see docstring)\n{'='*72}")
    for err in ["central_error_rank", "central_error_cal"]:
        sub = merged[["position", err]].copy(); sub["ctx"] = merged["own_e_b"].abs()
        sub = sub.dropna()
        obs = _spearman(sub["ctx"], sub[err])
        blocks = [g["ctx"].to_numpy() for _, g in sub.groupby("position")]
        errv = np.concatenate([g[err].to_numpy() for _, g in sub.groupby("position")])
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            null[p] = _spearman(np.concatenate([blocks[i] for i in
                                rng.permutation(len(blocks))]), errv)
        pv = (np.abs(null) >= abs(obs)).mean()
        print(f"  {err}: observed rho={obs:+.4f}  null mean={null.mean():+.4f} "
              f"sd={null.std():.4f}  p={pstr(pv)}")

    merged.to_csv(PROC / "tier2_permutation_inputs.csv", index=False)
    print(f"\nSaved inputs to {PROC / 'tier2_permutation_inputs.csv'}")
