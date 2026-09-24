"""
Script 34: does ESM-2 degrade differently from PROVEAN/SIFT/PolyPhen-2?

Review 2 proposed extending the script-29 placebo logic to established,
independent sequence-based predictors already loaded in script 07's
insilico.csv: if they show the same excess over placebos that ESM-2 does,
the pattern belongs to "any sequence-based predictor," not to ESM-2
specifically.

RAW result (unmatched baselines): ESM-2 degrades MORE than PROVEAN, SIFT,
and PolyPhen-2 HumDiv in absolute terms, with CIs excluding zero.

THIS RAW COMPARISON IS NOT TRUSTWORTHY ON ITS OWN. A follow-up review
correctly identified that it repeats the exact baseline-mismatch problem
scripts 30-31 were built to solve for the placebo comparison: ESM-2 starts
from a higher raw correlation (+0.53) than the other predictors (+0.37-
0.42), so it mechanically has more room to fall, and an absolute-drop
comparison across unequal starting points isn't directly interpretable.
The correct, matched-baseline version of this comparison is script 36 --
read that result together with this one, not this one alone.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scripts.lib.io import load_insilico_predictors, load_derived_maps, WT_COND_COLS
from scripts.lib.stats import _spearman

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
N_BOOT = 1000


def strat(d, p, n=3):
    s = d.dropna(subset=[p, "abs_gi", "target"])
    cuts = np.quantile(s["abs_gi"], np.linspace(0, 1, n + 1)[1:-1])
    k = np.digitize(s["abs_gi"], cuts)
    return [_spearman(s[p].to_numpy()[k == i], s["target"].to_numpy()[k == i]) for i in range(n)]


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    ins = load_insilico_predictors()
    df = df.merge(ins.rename(columns={"pos": "position", "ref": "wt_aa", "alt": "mut_aa"}),
                  on=["position", "wt_aa", "mut_aa"], how="left")
    der = load_derived_maps()
    df = df.merge(pd.DataFrame({"hgvs_pro": der["hgvs"], "placebo_wfitness": der["w.fitness"],
                                "placebo_wt_mean": der[WT_COND_COLS].mean(axis=1, skipna=True)}),
                  on="hgvs_pro", how="left")
    df["pp2div_flip"] = -df["pp2div"]
    df["pp2var_flip"] = -df["pp2var"]

    print("=" * 78)
    print("SIGN CHECK (PROVEAN/SIFT: lower=more damaging; PolyPhen-2: higher=more")
    print("damaging -- flipped PolyPhen-2 so all predictors run the same direction)")
    print("=" * 78)
    for c in ["model_C", "provean", "sift", "pp2div", "pp2var"]:
        s = df.dropna(subset=[c])
        print(f"  {c:16s} raw rho with target = {_spearman(s[c], s['target']):+.4f}")

    PREDS = [("model_C", "ESM-2 (A222V bg)  [claim]"), ("model_A", "ESM-2 (WT bg)"),
             ("provean", "PROVEAN"), ("sift", "SIFT"),
             ("pp2div_flip", "PolyPhen-2 HumDiv (flipped)"),
             ("pp2var_flip", "PolyPhen-2 HumVar (flipped)"),
             ("placebo_wt_mean", "PLACEBO: WT-arm mean"),
             ("placebo_wfitness", "PLACEBO: atlas w.fitness")]

    print("\n" + "=" * 78)
    print("RAW (unmatched-baseline) STRATIFIED rho BY |e.b| TERCILE")
    print("=" * 78)
    rows = []
    for c, l in PREDS:
        r = strat(df, c); drop = r[2] - r[0]
        pct = 100 * (1 - r[2] / r[0]) if r[0] != 0 else np.nan
        print(f"  {l:30s} {r[0]:+.4f} -> {r[1]:+.4f} -> {r[2]:+.4f}   drop={drop:+.4f} ({pct:5.0f}%)")
        rows.append({"predictor": c, "label": l, "low": r[0], "mid": r[1], "high": r[2],
                    "drop": drop, "pct_drop": pct})

    print("\n" + "=" * 78)
    print(f"ESM-2's RAW degradation vs each established predictor "
          f"(position bootstrap, {N_BOOT}) -- SEE CAVEAT IN DOCSTRING")
    print("=" * 78)
    rng = np.random.default_rng(0)
    base = df.dropna(subset=["model_C", "abs_gi", "target"]).reset_index(drop=True)
    diff_rows = []
    for comp, lbl in [("provean", "PROVEAN"), ("sift", "SIFT"),
                      ("pp2div_flip", "PolyPhen-2 HumDiv"), ("pp2var_flip", "PolyPhen-2 HumVar")]:
        sub = base.dropna(subset=[comp]).reset_index(drop=True)
        rbp = {p: sub.index[sub["position"] == p].to_numpy() for p in sub["position"].unique()}
        cl = np.array(list(rbp.keys()))
        point = (strat(sub, "model_C")[2] - strat(sub, "model_C")[0]) - \
                (strat(sub, comp)[2] - strat(sub, comp)[0])
        boot = np.empty(N_BOOT)
        for b in range(N_BOOT):
            idx = np.concatenate([rbp[c] for c in rng.choice(cl, size=len(cl), replace=True)])
            bs = sub.iloc[idx]
            boot[b] = (strat(bs, "model_C")[2] - strat(bs, "model_C")[0]) - \
                      (strat(bs, comp)[2] - strat(bs, comp)[0])
        lo, hi = np.nanpercentile(boot, [2.5, 97.5])
        v = "ESM-2 degrades MORE" if hi < 0 else "ESM-2 degrades LESS" if lo > 0 else "INDISTINGUISHABLE"
        print(f"  vs {lbl:22s} diff={point:+.4f} CI=[{lo:+.4f},{hi:+.4f}]  -> {v} (raw, unmatched)")
        diff_rows.append({"predictor": comp, "label": lbl, "raw_diff": point,
                          "ci_lo": lo, "ci_hi": hi, "verdict_raw": v})

    pd.DataFrame(rows).to_csv(PROC / "task_established_predictor_strat.csv", index=False)
    pd.DataFrame(diff_rows).to_csv(PROC / "task_established_predictor_diff_raw.csv", index=False)
    print(f"\nSaved. RAW comparison only -- see script 36 for the matched-baseline version.")
