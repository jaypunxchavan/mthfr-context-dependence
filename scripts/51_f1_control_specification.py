"""
Group F1 (REVIEW_TRIAGE items F1a, F1b) -- control specification.

F1a -- nonlinear fitness control (review item 21a).
Re-runs proposal 5.6e / results-log 3.1's multivariable model
(scripts/18_multivariable_controls.py) with base fitness (f_bar) entered
NONLINEARLY instead of linearly, because context dependence and ESM-2 error
may both peak at intermediate fitness (inverted-U) that a linear term cannot
absorb.

PRE-REGISTERED DECISION RULES (written before any run):
- GATE: the linear re-run must reproduce tier2_multivariable.csv coefs and
  CIs to 1e-6 for all 6 (error x context) models, else FAIL (sanity check;
  no retry, no test modification).
- PRIMARY variant: f_bar binned into deciles (qcut dummies, drop first).
- SENSITIVITY variant: f_bar + f_bar^2 (z-scored quadratic).
- Per-model verdict COEF ROBUST iff the binned-spec context coef has the
  same sign as the linear spec AND its 95% cluster CI excludes zero in the
  same direction. Headline: 3.1's claim SURVIVES NONLINEAR CONTROL iff
  COEF ROBUST for GI_folinate_independent in BOTH error metrics; CHANGED
  otherwise (sign/magnitude printed either way).

F1b -- 10th-90th percentile restriction of w.fitness (review item 21b,
"proposal 5.6c").
ASSUMPTION (logged, AGENTS 9): the original proposal 5.6c text does not
exist in this repository (grep over docs/, scripts/, notebooks/ finds no
5.6c beyond the review's own reference at REVIEW_TRIAGE.md line 171). Most
conservative reading applied: restrict the analysis population to w.fitness
in [p10, p90] and re-run the surviving central-error association (results-
log Part 3) plus its multivariable controls; the restriction "holds" only if
every pre-registered CI still excludes zero with the sign of the PUBLISHED
counterpart (task_region_check.csv pooled rho / tier2_multivariable.csv
GI_folinate_independent coef).
- w.fitness is the ATLAS's own raw column (data/raw/mthfrModel/results/
  folate_response_model5.csv, column "w.fitness", joined on hgvs -> hgvs_pro),
  NOT f_bar: they differ (corr ~0.90, max|diff| up to ~2.85; printed).
- Percentile cut computed ONCE on the analysis population entering the raw
  association test (non-null abs_gi, BOTH central errors, matched w.fitness)
  and applied unchanged to the multivariable model.
- Row accounting printed at every step (AGENTS 5), including excluded-vs-
  kept skew on abs_gi and errors.
- PRE-REGISTERED VERDICT HOLDS iff BOTH error metrics satisfy: raw
  association restricted CI excludes 0 with published sign AND multivariable
  GI_folinate_independent restricted CI excludes 0 with published sign.
  FAILS otherwise; per-model detail printed regardless.

N_BOOT read from environment (default 10000); smoke with 200.
Position-cluster bootstrap throughout (AGENTS 3). p-values are bootstrap
p (AGENTS 3): report p, not z.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
import statsmodels.api as sm
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.io import load_structural_features
from scripts.lib.stats import position_cluster_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"

ERRORS = [("central_error_rank", "rank-based"),
          ("central_error_cal", "calibrated")]
CONTEXT = [("folinate_response", "environment-dependent"),
           ("GI_folinate_independent", "sequence-encoded genetic"),
           ("GI_folinate_dependent", "both")]
CONT = ["abs_ctx", "f_bar", "grantham", "blosum62", "rsa"]


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4g}"


def prepare(df, err_col, ctx_col):
    d = df.copy()
    d["abs_ctx"] = d[ctx_col].abs()
    return d.dropna(subset=CONT + [err_col, "domain", "position"])


def fit_spec(d, err_col, spec):
    """OLS of z(err) on z(CONT) [decile: f_bar excluded from CONT] + domain
    dummies, cluster-robust SE by position. spec in {linear, decile, quad}."""
    dd = d.copy()
    cont = list(CONT)
    if spec == "decile":
        cont.remove("f_bar")
    for c in cont:
        sd = dd[c].std()
        dd[c] = (dd[c] - dd[c].mean()) / (sd if sd > 0 else 1)
    parts = [dd[cont]]
    if spec == "decile":
        bins = pd.qcut(dd["f_bar"], 10, duplicates="drop")
        parts.append(pd.get_dummies(bins, drop_first=True, dtype=float))
    elif spec == "quad":
        parts.append((dd["f_bar"] ** 2).rename("f_bar_sq"))
    parts.append(pd.get_dummies(dd["domain"], prefix="dom",
                                drop_first=True, dtype=float))
    X = sm.add_constant(pd.concat(parts, axis=1))
    y = (dd[err_col] - dd[err_col].mean()) / dd[err_col].std()
    m = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": dd["position"]})
    b, se = m.params["abs_ctx"], m.bse["abs_ctx"]
    return {"n": len(dd), "n_positions": int(dd["position"].nunique()),
            "coef": b, "se": se, "ci_lo": b - 1.96 * se,
            "ci_hi": b + 1.96 * se, "p": m.pvalues["abs_ctx"],
            "r2": m.rsquared}


def robust(lin, var):
    return ((np.sign(var["coef"]) == np.sign(lin["coef"]))
            and not (var["ci_lo"] < 0 < var["ci_hi"])
            and ((lin["ci_lo"] < 0) == (var["ci_lo"] < 0)))


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase3_analysis_table.csv")
    df = add_substitution_features(df)
    df = add_structural_features(df, load_structural_features())
    print(f"Loaded {len(df)} variants from phase3_analysis_table.csv")

    # ---------------- F1a ----------------
    print("\n" + "=" * 72)
    print("F1a: 3.1 multivariable model with nonlinear base-fitness control")
    print("=" * 72)
    pub = pd.read_csv(PROC / "tier2_multivariable.csv")
    rows, gate_ok = [], True
    for err_col, err_lbl in ERRORS:
        for ctx_col, ctx_lbl in CONTEXT:
            d = prepare(df, err_col, ctx_col)
            res = {s: fit_spec(d, err_col, s)
                   for s in ("linear", "decile", "quad")}
            pr = pub[(pub.error_metric == err_lbl)
                     & (pub.context_metric == ctx_col)]
            if len(pr) != 1:
                print(f"GATE FAIL: {err_lbl}/{ctx_col}: {len(pr)} published rows")
                sys.exit(1)
            pr = pr.iloc[0]
            diffs = [abs(res["linear"]["coef"] - pr.coef),
                     abs(res["linear"]["ci_lo"] - pr.ci_lo),
                     abs(res["linear"]["ci_hi"] - pr.ci_hi)]
            n_ok = res["linear"]["n"] == pr.n
            ok = max(diffs) < 1e-6 and n_ok
            gate_ok &= ok
            print(f"\n{err_lbl} error ~ |{ctx_col}| ({ctx_lbl})  n={res['linear']['n']} "
                  f"pos={res['linear']['n_positions']}")
            print(f"  GATE linear vs tier2_multivariable.csv: max|coef/ci diff|="
                  f"{max(diffs):.2e}  n_match={n_ok}  -> {'OK' if ok else 'FAIL'}")
            for s, lbl in (("linear", "linear f_bar   "),
                           ("decile", "decile-binned  "),
                           ("quad",   "quadratic       ")):
                r = res[s]
                print(f"  {lbl} coef={r['coef']:+.4f} CI=[{r['ci_lo']:+.4f},"
                      f"{r['ci_hi']:+.4f}] p={pstr(r['p'])} r2={r['r2']:.4f}")
            rob_d, rob_q = robust(res["linear"], res["decile"]), robust(res["linear"], res["quad"])
            print(f"  -> binned COEF ROBUST: {rob_d}   quadratic COEF ROBUST: {rob_q}")
            for s in ("linear", "decile", "quad"):
                r = res[s]
                rows.append({"error_metric": err_lbl, "context_metric": ctx_col,
                             "spec": s, **r,
                             "coef_robust": rob_d if s == "decile" else
                                            (rob_q if s == "quad" else "")})
    if not gate_ok:
        print("\nGATE FAIL: linear re-run does not reproduce tier2_multivariable.csv "
              "(>1e-6 or n mismatch). Sanity check failed; stopping (no retry).")
        sys.exit(1)
    gi = {r["error_metric"]: r for r in rows
          if r["context_metric"] == "GI_folinate_independent" and r["spec"] == "decile"}
    surv = all(gi[lbl]["coef_robust"] for _, lbl in ERRORS)
    print("\nF1a VERDICT (pre-registered): "
          f"{'SURVIVES NONLINEAR CONTROL' if surv else 'CHANGED'} "
          "-- GI_folinate_independent binned-spec COEF ROBUST in "
          f"{sum(bool(gi[lbl]['coef_robust']) for _, lbl in ERRORS)}/2 error metrics")
    pd.DataFrame(rows).to_csv(PROC / "task51_f1a_nonlinear_fitness.csv", index=False)
    print(f"Saved {PROC / 'task51_f1a_nonlinear_fitness.csv'}")

    # ---------------- F1b ----------------
    print("\n" + "=" * 72)
    print("F1b: 10th-90th percentile restriction of w.fitness (proposal 5.6c)")
    print("=" * 72)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv",
                      usecols=["hgvs", "w.fitness"]).rename(
                          columns={"hgvs": "hgvs_pro"})
    dfw = df.merge(raw, on="hgvs_pro", how="left")
    dfw["abs_gi"] = dfw["GI_folinate_independent"].abs()
    both_err = dfw.dropna(subset=["abs_gi", "central_error_rank",
                                  "central_error_cal"])
    matched = both_err.dropna(subset=["w.fitness"])
    q10, q90 = matched["w.fitness"].quantile(0.10), matched["w.fitness"].quantile(0.90)
    kept = matched[(matched["w.fitness"] >= q10) & (matched["w.fitness"] <= q90)]
    print(f"abs_gi + both-errors population: {len(both_err)} rows / "
          f"{both_err['position'].nunique()} positions")
    print(f"w.fitness matched: {len(matched)}  unmatched: {len(both_err) - len(matched)}")
    print(f"cut p10={q10:.6f} p90={q90:.6f}  below={int((matched['w.fitness'] < q10).sum())} "
          f"above={int((matched['w.fitness'] > q90).sum())}  kept={len(kept)}")
    excl = matched[~matched.index.isin(kept.index)]
    for c in ("abs_gi", "central_error_rank", "central_error_cal"):
        print(f"  skew check {c}: kept mean={kept[c].mean():+.4f}  "
              f"excluded(n={len(excl)}) mean={excl[c].mean():+.4f}")

    pub_pool = pd.read_csv(PROC / "task_region_check.csv")
    pub_pool = pub_pool[pub_pool.region == "pooled"].set_index("error_metric")
    pub_gi = pub.set_index(["error_metric", "context_metric"])
    f1b_rows, verdicts = [], {}
    for err_col, err_lbl in ERRORS:
        base = both_err.dropna(subset=[err_col])
        unres = matched.dropna(subset=[err_col])
        r_base = position_cluster_bootstrap(base, "position", "abs_gi", err_col,
                                            n_boot=N_BOOT, seed=SEED)
        r_un = position_cluster_bootstrap(unres, "position", "abs_gi", err_col,
                                          n_boot=N_BOOT, seed=SEED)
        r_re = position_cluster_bootstrap(kept, "position", "abs_gi", err_col,
                                          n_boot=N_BOOT, seed=SEED)
        pub_rho = pub_pool.loc[err_lbl, "observed_rho"]
        d_rho = abs(r_base["observed_rho"] - pub_rho)
        print(f"\n{err_lbl}: raw |GI_folinate_independent| association")
        print(f"  reproduction check: base rho={r_base['observed_rho']:+.6f} "
              f"published(task_region_check)={pub_rho:+.6f}  |diff|={d_rho:.2e}  "
              f"n={r_base['n_rows']} (published n={int(pub_pool.loc[err_lbl, 'n_rows'])})")
        for lbl, r in (("unrestricted(matched)", r_un), ("restricted p10-p90", r_re)):
            print(f"  {lbl:21s} n={r['n_rows']:5d} pos={r['n_clusters']:3d} "
                  f"rho={r['observed_rho']:+.4f} CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] "
                  f"p={pstr(r['p_boot'])}")
        same_sign = np.sign(r_re["observed_rho"]) == np.sign(pub_rho)
        excl0 = not (r_re["ci_lo"] < 0 < r_re["ci_hi"])
        raw_ok = bool(same_sign and excl0)
        print(f"  raw restricted: same sign as published={same_sign} "
              f"CI excludes 0={excl0} -> {'PASS' if raw_ok else 'FAIL'}")

        # multivariable on the same frames, linear spec (published counterpart = tier2)
        mlbl = {"central_error_rank": "rank-based",
                "central_error_cal": "calibrated"}[err_col]
        out_mv = {}
        for lbl, frame in (("unrestricted(matched)", unres), ("restricted p10-p90", kept)):
            d = prepare(frame, err_col, "GI_folinate_independent")
            r = fit_spec(d, err_col, "linear")
            out_mv[lbl] = r
            print(f"  multivariable {lbl:21s} n={r['n']:5d} coef={r['coef']:+.4f} "
                  f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p'])}")
        pr = pub_gi.loc[(mlbl, "GI_folinate_independent")]
        rr = out_mv["restricted p10-p90"]
        mv_ok = bool(np.sign(rr["coef"]) == np.sign(pr.coef)
                     and not (rr["ci_lo"] < 0 < rr["ci_hi"]))
        print(f"  multivariable published(tier2): coef={pr.coef:+.4f} "
              f"CI=[{pr.ci_lo:+.4f},{pr.ci_hi:+.4f}] n={int(pr.n)}")
        print(f"  multivariable restricted: same sign as published="
              f"{np.sign(rr['coef']) == np.sign(pr.coef)} "
              f"CI excludes 0={not (rr['ci_lo'] < 0 < rr['ci_hi'])} -> "
              f"{'PASS' if mv_ok else 'FAIL'}")
        verdicts[err_lbl] = raw_ok and mv_ok
        for lbl, r in (("base(unrestricted)", r_base), ("matched", r_un),
                       ("restricted", r_re)):
            f1b_rows.append({"analysis": "raw_association", "frame": lbl,
                             "error_metric": err_lbl, "n": r["n_rows"],
                             "n_positions": r["n_clusters"],
                             "stat": r["observed_rho"], "ci_lo": r["ci_lo"],
                             "ci_hi": r["ci_hi"], "p": r["p_boot"]})
        for lbl in ("unrestricted(matched)", "restricted p10-p90"):
            r = out_mv[lbl]
            f1b_rows.append({"analysis": "multivariable", "frame": lbl,
                             "error_metric": err_lbl, "n": r["n"],
                             "n_positions": r["n_positions"],
                             "stat": r["coef"], "ci_lo": r["ci_lo"],
                             "ci_hi": r["ci_hi"], "p": r["p"]})

    holds = all(verdicts.values())
    print("\nF1b VERDICT (pre-registered): "
          f"{'HOLDS' if holds else 'FAILS'} -- per-metric: "
          + ", ".join(f"{k}={'HOLDS' if v else 'FAILS'}"
                      for k, v in verdicts.items()))
    pd.DataFrame(f1b_rows).to_csv(PROC / "task51_f1b_percentile.csv", index=False)
    print(f"Saved {PROC / 'task51_f1b_percentile.csv'}")
    print("\nLIMITATIONS (script is the record, AGENTS 6): proposal 5.6c's original "
          "text is absent from the repo; the 10-90 reading above is the logged "
          "assumption. w.fitness join drops the unmatched rows printed above; their "
          "abs_gi is entirely non-null (checked at design time), so the drop cannot "
          "bias the raw association, but the multivariable frame loses whatever "
          "cont-feature rows the join lost. One cut, computed once, applied to both "
          "analyses. Bootstrap CIs are position-cluster (AGENTS 3); no z-scores "
          "reported.")
