"""
Subtask A: Multivariable model (proposal 5.6e).

Does context dependence still explain ESM-2's central error after
accounting for ordinary variant difficulty -- biochemical severity of the
substitution, burial, and domain -- plus the fitness confound?

Inference uses cluster-robust standard errors by residue position, which
the proposal permits as an alternative to full mixed-effects modelling.
~12,000 variants sit within ~655 positions, so naive OLS standard errors
would be badly overstated.

Continuous predictors are z-scored, so each coefficient is the change in
error per 1 SD of that predictor and coefficients are comparable.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.io import load_structural_features
from scripts.lib.features import add_substitution_features, add_structural_features

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
CONTEXT = [("folinate_response", "environment-dependent"),
           ("GI_folinate_independent", "sequence-encoded genetic"),
           ("GI_folinate_dependent", "both")]
ERRORS = [("central_error_rank", "rank-based"), ("central_error_cal", "calibrated")]

if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase3_analysis_table.csv")
    df = add_substitution_features(df)
    df = add_structural_features(df, load_structural_features())
    print(f"Loaded {len(df)} variants; rsa missing for "
          f"{df['rsa'].isna().sum()} (unresolved in 6FCX, dropped from this model)")
    print(f"Domains: {df['domain'].value_counts(dropna=False).to_dict()}")

    rows = []
    for err_col, err_lbl in ERRORS:
        for ctx_col, ctx_lbl in CONTEXT:
            d = df.copy()
            d["abs_ctx"] = d[ctx_col].abs()
            cont = ["abs_ctx", "f_bar", "grantham", "blosum62", "rsa"]
            d = d.dropna(subset=cont + [err_col, "domain", "position"])
            for c in cont:
                sd = d[c].std()
                d[c] = (d[c] - d[c].mean()) / (sd if sd > 0 else 1)

            X = pd.concat([d[cont],
                           pd.get_dummies(d["domain"], prefix="dom",
                                          drop_first=True, dtype=float)], axis=1)
            X = sm.add_constant(X)
            y = (d[err_col] - d[err_col].mean()) / d[err_col].std()
            m = sm.OLS(y, X).fit(cov_type="cluster",
                                 cov_kwds={"groups": d["position"]})

            b, se = m.params["abs_ctx"], m.bse["abs_ctx"]
            lo, hi = b - 1.96 * se, b + 1.96 * se
            print(f"\n{err_lbl} error ~ |{ctx_col}| ({ctx_lbl})")
            print(f"  n={len(d)}, {d['position'].nunique()} position clusters")
            print(f"  context coef = {b:+.4f} (SD error per SD context)  "
                  f"95% CI=[{lo:+.4f},{hi:+.4f}]  p={m.pvalues['abs_ctx']:.4g}")
            print(f"  -> {'SURVIVES' if not (lo < 0 < hi) else 'does NOT survive'} controls")
            others = {k: round(m.params[k], 4) for k in ["f_bar", "grantham", "blosum62", "rsa"]}
            print(f"  covariates: {others}")
            rows.append({"error_metric": err_lbl, "context_metric": ctx_col,
                         "context_class": ctx_lbl, "n": len(d),
                         "n_positions": d["position"].nunique(), "coef": b, "se": se,
                         "ci_lo": lo, "ci_hi": hi, "p": m.pvalues["abs_ctx"],
                         "survives": not (lo < 0 < hi), "r2": m.rsquared, **others})

    pd.DataFrame(rows).to_csv(PROC / "tier2_multivariable.csv", index=False)
    print(f"\nSaved to {PROC / 'tier2_multivariable.csv'}")
