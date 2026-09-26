"""
Script 33: does measurement noise explain the accuracy-degradation finding?

Reviews 1 and 3 raised a live alternative: |e.b| is a residual estimated
from noisy measurements, so measurement noise in the A222V arm could
inflate |e.b| AND inflate apparent prediction error simultaneously for
ANY predictor -- meaning "high interaction" partly just means "high
measurement noise," which every predictor should struggle with regardless
of what it knows.

RESULT: the diagnostic confirms the concern was worth raising -- A222V-arm
measurement SE genuinely correlates with |e.b| (rho=+0.231, CI clear of
zero), and mean SE rises measurably across interaction strata (0.094 ->
0.140). But abs_gi survives controlling for this directly, essentially
unchanged (rank +0.182->+0.182; calibrated +0.245->+0.235), and restricting
to the high-precision half only modestly flattens the degradation slope
(-0.357 -> -0.298, a ~16% reduction, not a collapse to zero). Noise is a
real, quantified contributor. It is not the explanation.
"""
import sys, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.io import load_derived_maps, load_structural_features
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.stats import crossfit_isotonic_by_position, position_cluster_bootstrap, _spearman

MT_SE = ["m12.se", "m25.se", "m100.se", "m200.se"]
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def run(df, ec, cols):
    d = df.dropna(subset=cols + [ec, "domain", "position"]).copy()
    for c in cols:
        sd = d[c].std(); d[c] = (d[c] - d[c].mean()) / (sd if sd > 0 else 1)
    X = sm.add_constant(pd.concat([d[cols], pd.get_dummies(d["domain"], prefix="dom",
                                   drop_first=True, dtype=float)], axis=1))
    y = (d[ec] - d[ec].mean()) / d[ec].std()
    m = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": d["position"]})
    b, se = m.params["abs_gi"], m.bse["abs_gi"]
    return b, b - 1.96*se, b + 1.96*se, len(d)


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df = add_substitution_features(df)
    df = add_structural_features(df, load_structural_features())
    der = load_derived_maps()
    df = df.merge(pd.DataFrame({"hgvs_pro": der["hgvs"], **{c: der[c] for c in MT_SE}}),
                  on="hgvs_pro", how="left")
    df["m_se"] = df[MT_SE].mean(axis=1, skipna=True)
    df = df.dropna(subset=["model_C", "target"]).copy()
    df["err_rank"] = (df["model_C"].rank() - df["target"].rank()).abs()
    df["err_cal"] = (df["target"] - crossfit_isotonic_by_position(
        df, "position", "model_C", "target", n_folds=5, seed=0)).abs()

    print("=" * 74)
    print("DIAGNOSTIC: does measurement noise track interaction strength?")
    print("=" * 74)
    d = df.dropna(subset=["abs_gi", "m_se"])
    r = position_cluster_bootstrap(d, "position", "m_se", "abs_gi", n_boot=2000, seed=0)
    print(f"  rho(A222V-arm SE, |e.b|) = {r['observed_rho']:+.4f} "
          f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}]  n={r['n_rows']}")
    d2 = d.copy(); d2["st"] = pd.qcut(d2["abs_gi"], 3, labels=["low", "mid", "high"])
    for lvl in ["low", "mid", "high"]:
        s = d2[d2.st == lvl]
        print(f"    {lvl:4s} mean SE={s['m_se'].mean():.4f}  n={len(s)}")

    print("\n" + "=" * 74)
    print("DOES abs_gi SURVIVE CONTROLLING FOR MEASUREMENT NOISE?")
    print("=" * 74)
    BASE = ["abs_gi", "grantham", "blosum62", "rsa"]
    rows = []
    for ec, lbl in [("err_rank", "rank-based"), ("err_cal", "calibrated")]:
        for name, cols in [("structural covars only", BASE), ("+ m_se", BASE + ["m_se"])]:
            b, lo, hi, n = run(df, ec, cols)
            surv = not (lo < 0 < hi)
            print(f"  {lbl:11s} {name:24s} coef={b:+.4f} CI=[{lo:+.4f},{hi:+.4f}] "
                  f"{'SURVIVES' if surv else 'FAILS'} n={n}")
            rows.append({"error_metric": lbl, "spec": name, "coef": b,
                        "ci_lo": lo, "ci_hi": hi, "survives": surv, "n": n})

    print("\n" + "=" * 74)
    print("HIGH-PRECISION SUBSET: does the degradation slope flatten?")
    print("=" * 74)
    thr = df["m_se"].quantile(0.5)
    for name, sub in [("all variants", df), (f"precise half (SE<{thr:.3f})", df[df.m_se < thr])]:
        s = sub.dropna(subset=["abs_gi", "model_C", "target"]).copy()
        s["st"] = pd.qcut(s["abs_gi"], 3, labels=False)
        rh = [_spearman(s[s.st == i]["model_C"], s[s.st == i]["target"]) for i in range(3)]
        print(f"  {name:26s} {rh[0]:+.4f} -> {rh[1]:+.4f} -> {rh[2]:+.4f}  "
              f"drop={rh[2]-rh[0]:+.4f}  n={len(s)}")
        rows.append({"error_metric": "n/a", "spec": name, "coef": rh[2]-rh[0],
                    "ci_lo": None, "ci_hi": None, "survives": None, "n": len(s)})

    pd.DataFrame(rows).to_csv(PROC / "task_measurement_noise_control.csv", index=False)
    print(f"\nSaved to task_measurement_noise_control.csv")
