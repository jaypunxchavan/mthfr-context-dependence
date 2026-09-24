"""
AD5 — confound-control ThermoMPNN's -0.0733 with the ESM-2 machinery
(task doc L281-285), PRE-REGISTERED. This docstring was written before
the first run.

QUESTION (frozen): does the ThermoMPNN-vs-own_e_b association
(rho = -0.0733, headline from [AA4], independently reproduced in [AD4]
secondary (c) as -0.0733 [-0.1021, -0.0437], n=9,595) survive the same
multivariable controls that were built for ESM-2 (scripts 18 and 24:
base fitness, RSA, fixed effects, cluster-robust SEs by position)?

MACHINERY REUSED VERBATIM (not re-derived): scripts/
18_multivariable_controls.py and scripts/24_accuracy_degradation_
gauntlet.py check 1c — z-score all continuous columns inside the
analysis frame (d[c] = (d[c]-mean)/sd), dummy-encode the categorical
fixed effects with drop_first, z-score y, statsmodels OLS with
cov_type="cluster", cov_kwds={"groups": position}, survival rule
exactly 1c's: SURVIVES iff the focal coefficient's cluster-robust
95% CI (b +- 1.96 SE) excludes 0. Standardized focal coefficients are
comparable across focals (SD outcome per SD predictor).

PRE-REGISTERED SPECS (both always run, both always reported):
  SPEC A — task-literal controls (L284: "base fitness, RSA, position
    fixed effects, cluster-robust SEs"):
      y = own_e_b (z) ~ focal (z) + f_bar (z) + position FE,
      cluster-robust by position. RSA is NOT listed explicitly because
      it is exactly absorbed by position FE [AMENDED after smoke run 1:
      with rsa in the design, statsmodels raised SingularMatrixWarning,
      rank 588 < 589; diagnosed numerically before any fix — the null
      space of the design spans ONLY {z_rsa + position dummies + const}
      (focal and f_bar have zero null-space weight), because rsa is a
      PER-POSITION constant merged by position (scripts/lib/features.py
      L61-63) and is therefore an exact linear function of the position
      indicators. Position FE is the strictest form of RSA control
      (it holds rsa fixed at every position, not just linearly), so the
      explicit rsa column is redundant BY CONSTRUCTION and was removed;
      G2 was strengthened from k<n to an exact rank==k check. The focal
      estimate cannot move (focal absent from the null space); smoke run
      2 must reproduce smoke run 1's focal coefs to <1e-6 or the run
      stops — verification quoted in the log entry. No threshold,
      direction, or survival rule changed.]
  SPEC B — the exact script-24 check-1c control set (its literal cont
    list), for machinery identity with the ESM-2 work:
      y = own_e_b (z) ~ focal (z) + f_bar_a222v (z) + grantham (z) +
      blosum62 (z) + rsa (z) + domain FE, cluster-robust by position.
      (script 18 used f_bar rather than f_bar_a222v and domain FE; the
      two house specs differ in base-fitness column and FE granularity —
      both house variants are reproduced here across A/B rather than
      choosing one post hoc.)
FOCALS in each spec (always all four, so nothing is chosen after seeing
  results): (i) ddg = ThermoMPNN signed ddG — THE -0.0733 UNDER TEST;
  (ii) delta_esm signed — ESM-2 side-by-side under identical spec and
  identical rows; (iii) |ddg|; (iv) |delta_esm| (magnitude framing,
  mirroring 1c/18's abs focal). Note: no pre-existing controlled ESM-2
  number for delta_esm~own_e_b was found in the task docs (grepped
  detection-floor + closeout docs for "multivariable"/"fixed effects" —
  only AD5's own text matched), so rows (ii)/(iv) are NEW side-by-side
  computations under the reused spec, not reproductions of a published
  figure; disclosed here so they are not later cited as replications.
EXPECTED SIGN for signed focals: negative (matching -0.0733 and AA4's
  -0.088 orientation). Survival itself is judged two-sided by the 1c
  rule (CI excludes 0), sign reported plainly either way.

FRAME (frozen): V2 table (10,141 rows; ddg, own_e_b, delta_esm, region,
  position) LEFT-MERGED to phase5 on hgvs_pro for f_bar, f_bar_a222v;
  grantham/blosum62 via scripts.lib.features.add_substitution_features;
  rsa + domain via add_structural_features(load_structural_features()).
  ESM-2 rows use this SAME V2 frame (not script 24's phase5+model_C
  frame) so both models are compared on identical rows — the n's will
  therefore not match script 24's published n's; reconciled here by
  construction (AGENTS section 5).

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 headline identity: rho(ddg, own_e_b) on finite-own_e_b rows must
     equal -0.0733 within 5e-4 (4dp rounding of the [AD4](c)/[AA4]
     figure); frames must show 9,595 rows / 586 positions (same frame
     as [AD3]/[AD4] — n's reconciled, AGENTS section 5).
  G2 design checks per regression: focal column present,
     X.shape[1] < n, AND exact rank == k (np.linalg.matrix_rank);
     else exit 1. [G2 was k<n only at smoke run 1, which let a
     rank-deficiency through as a warning; strengthened to exact rank
     after diagnosing the SPEC A rsa/position-FE collinearity — see
     SPEC A amendment note. Do not weaken.]
  G3 inference finite: focal coef, cluster-robust SE, p all finite and
     cluster count == positions in that spec's frame; else exit 1.
ACCOUNTING: every spec prints n dropped at each non-NA filter.

SECONDARIES (frozen, always reported): rank-based complement via
  scripts.lib.partial_spearman_cluster_bootstrap (position-cluster
  bootstrap, seed 0): partial rho(ddg, own_e_b) controlling (r1) f_bar
  — script 18's base-fitness covariate; (r2) f_bar_wt — the own_e_b
  construction covariate (own_e_b was fitted in scripts/17 with
  wild-type-arm fitness as expectation input; AD3's section-4 control).
  Limitation printed with them: partial_spearman handles ONE covariate
  at a time, so (r1)/(r2) are not substitutes for the multivariable
  specs; they exist to reconnect the standardized-OLS answer to the
  rank-based headline.

ENV: N_BOOT default 10,000 (partial-Spearman bootstraps); SMOKE=1 =>
  300. OUTPUT: data/processed/task78_thermompnn_controls.csv (every
  regression row). NULL LABEL: no permutation here by design — inference
  is the reused machinery's cluster-robust CI (section 4: match the
  null/inference to the statistic the house method uses); the rank
  secondaries carry the position-cluster bootstrap.

LIMITATIONS (printed with results, section 6):
  1. OLS on z-scored levels is a linear partial association; the -0.0733
     headline is rank-based — the partial-Spearman secondaries bridge
     the two scales but control one covariate each.
  2. Position FE (spec A) identifies the focal effect only from WITHIN-
     position variation; that is stricter than the between-position
     information the raw rho also uses, so a spec-A attenuation is not
     by itself evidence of confounding — spec B (domain FE) retains
     between-position variation at coarser granularity.
  3. Cluster-robust SEs assume independent clusters (positions) — the
     house assumption, unchanged from 18/24.
  4. This tests association of ThermoMPNN's single-mutant ddG with
     own_e_b (the -0.0733 quantity), NOT [AD4]'s double-mutant
     interaction (which is a different, separately-null result).
"""
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import spearmanr

from scripts.lib.io import load_structural_features
from scripts.lib.features import add_substitution_features, add_structural_features
from scripts.lib.stats import partial_spearman_cluster_bootstrap

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
PH5_PATH = PROC / "phase5_analysis_table.csv"
OUT_PATH = PROC / "task78_thermompnn_controls.csv"

HEADLINE_RHO = -0.0733
HEADLINE_TOL = 5e-4
EXPECTED_N = 9595
EXPECTED_POS = 586

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
if SMOKE:
    N_BOOT = min(N_BOOT, 300)
SEED = 0
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def run_spec(d, focal, spec_name, group_col="position"):
    """1c machinery verbatim: z-score conts + focal inside frame, z-score y,
    FE already encoded by caller in d, cluster-robust OLS by position.

    NOTE on naming: caller passes controls as z_* markers (raw values,
    z-scored exactly once here) and the focal under its bare name (so
    m.params[focal] resolves); dummies are never z-scored."""
    cont = [c for c in d.columns
            if c.startswith("z_") or c == focal]
    for c in cont:
        sd = d[c].std()
        d[c] = (d[c] - d[c].mean()) / (sd if sd > 0 else 1)
    ycol = [c for c in d.columns if c.startswith("zy_")][0]
    d[ycol] = (d[ycol] - d[ycol].mean()) / d[ycol].std()
    # X = everything except outcome and cluster id: z-scored controls,
    # focal, and the fixed-effect dummies (all FE must be in the design)
    X = d.drop(columns=[ycol, group_col]).copy()
    X = sm.add_constant(X)
    m = sm.OLS(d[ycol], X).fit(cov_type="cluster",
                               cov_kwds={"groups": d[group_col]})
    b, se, p = m.params[focal], m.bse[focal], m.pvalues[focal]
    lo, hi = b - 1.96 * se, b + 1.96 * se
    surv = not (lo < 0 < hi)
    n_pos = d[group_col].nunique()
    if not (np.isfinite(b) and np.isfinite(se) and np.isfinite(p)):
        gfail(f"{spec_name}/{focal}: non-finite coef/SE/p")
    if X.shape[1] >= len(d):
        gfail(f"{spec_name}/{focal}: design not full rank "
              f"(k={X.shape[1]} >= n={len(d)})")
    r = np.linalg.matrix_rank(X.to_numpy())
    if r != X.shape[1]:
        gfail(f"{spec_name}/{focal}: RANK DEFICIENT design "
              f"(rank {r} < k={X.shape[1]}) — coefficients would not be "
              f"uniquely determined; fix the collinearity first")
    print(f"  {spec_name:8s} focal={focal:16s} coef={b:+.4f} "
          f"CI=[{lo:+.4f},{hi:+.4f}] p={p:.4g}  -> "
          f"{'SURVIVES' if surv else 'does NOT survive'}  "
          f"(n={len(d)}, {n_pos} position clusters, k={X.shape[1]})")
    return {"spec": spec_name, "focal": focal, "coef": b, "se": se,
            "ci_lo": lo, "ci_hi": hi, "p": p, "survives": bool(surv),
            "n": len(d), "n_positions": int(n_pos)}


if __name__ == "__main__":
    banner("AD5 — MULTIVARIABLE CONTROLS ON ThermoMPNN's -0.0733 "
           f"(scripts/78) SMOKE={SMOKE} N_BOOT={N_BOOT}")
    v2 = pd.read_csv(V2_PATH)
    ph5 = pd.read_csv(PH5_PATH)[["hgvs_pro", "f_bar", "f_bar_a222v",
                                 "f_bar_wt"]]
    df = v2.merge(ph5, on="hgvs_pro", how="left")
    df = add_structural_features(add_substitution_features(df),
                                 load_structural_features())
    df["abs_ddg"] = df["ddg"].abs()
    df["abs_delta_esm"] = df["delta_esm"].abs()
    print(f"  merged: {len(df)} V2 rows; f_bar finite "
          f"{df['f_bar'].notna().sum()} | f_bar_a222v "
          f"{df['f_bar_a222v'].notna().sum()} | rsa {df['rsa'].notna().sum()} "
          f"| domain {df['domain'].notna().sum()} | grantham "
          f"{df['grantham'].notna().sum()} | own_e_b "
          f"{df['own_e_b'].notna().sum()}")

    # ---- G1: headline identity + frame reconciliation --------------
    base = df[df["own_e_b"].notna()]
    rho_head = float(spearmanr(base["ddg"], base["own_e_b"]).statistic)
    if len(base) != EXPECTED_N or base["position"].nunique() != EXPECTED_POS:
        gfail(f"G1 FAIL: frame {len(base)} rows / "
              f"{base['position'].nunique()} pos != "
              f"{EXPECTED_N}/{EXPECTED_POS}")
    if abs(rho_head - HEADLINE_RHO) > HEADLINE_TOL:
        gfail(f"G1 FAIL: rho {rho_head:+.6f} != {HEADLINE_RHO} "
              f"+-{HEADLINE_TOL}")
    print(f"  G1 headline identity PASS: rho(ddg, own_e_b) = "
          f"{rho_head:+.6f} on n={len(base)}, "
          f"{base['position'].nunique()} positions "
          f"(matches [AD4](c)/[AA4] -0.0733)")

    FOCALS = ["ddg", "delta_esm", "abs_ddg", "abs_delta_esm"]
    rows = []

    banner("SPEC A — task-literal: f_bar + POSITION FE (rsa absorbed by "
           "FE: per-position constant), cluster-robust (L284)", "=")
    print("  note: rsa is per-position constant -> exactly collinear with "
          "position FE; FE holds it fixed at every position (strictest "
          "RSA control), so the explicit rsa column is redundant by "
          "construction (smoke-run-1 amendment, docstring G2)")
    colsA = FOCALS + ["own_e_b", "f_bar", "rsa", "position"]
    dA = df.dropna(subset=colsA).copy()
    print(f"  after dropna: n={len(dA)} (dropped {len(df) - len(dA)})")
    for f in FOCALS:
        dd = dA.copy()
        fe = pd.get_dummies(dd["position"], prefix="pos", drop_first=True,
                            dtype=float)
        spec = pd.concat([
            dd[[f, "f_bar"]].add_prefix("z_").reset_index(drop=True),
            fe.reset_index(drop=True)], axis=1)
        # focal must carry its bare name for coef lookup -> rename
        spec = spec.rename(columns={f"z_{f}": f})
        spec["zy_own_e_b"] = dd["own_e_b"].to_numpy()
        spec["position"] = dd["position"].to_numpy()
        rows.append(run_spec(spec, f, "A"))

    banner("SPEC B — exact script-24 1c set: f_bar_a222v + grantham + "
           "blosum62 + rsa + DOMAIN FE", "=")
    colsB = FOCALS + ["own_e_b", "f_bar_a222v", "grantham", "blosum62",
                      "rsa", "domain", "position"]
    dB = df.dropna(subset=colsB).copy()
    print(f"  after dropna: n={len(dB)} (dropped {len(df) - len(dB)})")
    for f in FOCALS:
        dd = dB.copy()
        fe = pd.get_dummies(dd["domain"], prefix="dom", drop_first=True,
                            dtype=float)
        cont = ["f_bar_a222v", "grantham", "blosum62", "rsa"]
        spec = pd.concat([
            dd[[f] + cont].add_prefix("z_").reset_index(drop=True),
            fe.reset_index(drop=True)], axis=1)
        spec = spec.rename(columns={f"z_{f}": f})
        spec["zy_own_e_b"] = dd["own_e_b"].to_numpy()
        spec["position"] = dd["position"].to_numpy()
        rows.append(run_spec(spec, f, "B"))

    banner("SECONDARIES — rank-based partials (position-cluster "
           "bootstrap)", "=")
    prim = rows[0]
    for label, covar in (("r1 f_bar (script 18 covariate)", "f_bar"),
                         ("r2 f_bar_wt (own_e_b construction covariate)",
                          "f_bar_wt")):
        sub = df[["position", "ddg", "own_e_b", covar]].dropna()
        ps = partial_spearman_cluster_bootstrap(sub, "position", "ddg",
                                                "own_e_b", covar_col=covar,
                                                n_boot=N_BOOT, seed=SEED)
        print(f"  ({label}) partial rho(ddg, own_e_b | {covar}) = "
              f"{ps['observed_rho']:+.4f} [{ps['ci_lo']:+.4f}, "
              f"{ps['ci_hi']:+.4f}] p_boot={ps['p_boot']:.4f} "
              f"n={ps['n_rows']} clusters={ps['n_clusters']} "
              f"(single-covariate: NOT a substitute for specs A/B)")

    banner("VERDICT", "=")
    verdict = ("SURVIVES the task-literal controls"
               if prim["survives"] else
               "does NOT survive the task-literal controls")
    print(f"  SPEC A focal=ddg (the -0.0733 under test): {verdict}")
    print(f"    coef={prim['coef']:+.4f} CI=[{prim['ci_lo']:+.4f},"
          f"{prim['ci_hi']:+.4f}] p={prim['p']:.4g} n={prim['n']} "
          f"| sign expected negative: "
          f"{'yes' if prim['coef'] < 0 else 'NO (reported as-is)'}")
    esm_rows = [r for r in rows if r["focal"] == "delta_esm"]
    print("  ESM-2 side-by-side (same spec, same rows): "
          + " | ".join(f"spec{r['spec']} coef={r['coef']:+.4f} "
                       f"p={r['p']:.4g} "
                       f"{'SURVIVES' if r['survives'] else 'no'}"
                       for r in esm_rows))

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    print(f"\n  saved {len(out)} regression rows -> {OUT_PATH.name}")

    banner("LIMITATIONS (printed with results, AGENTS section 6)", "-")
    print(f"""  1. OLS on z-scored LEVELS is a linear partial association; the
     headline -0.0733 is rank-based - partial-Spearman secondaries
     bridge scales but control one covariate each.
  2. Spec A's position FE identifies the focal effect only from WITHIN-
     position variation (stricter than the raw rho's between-position
     information); attenuation there is not alone proof of confounding.
  3. Cluster-robust SEs assume independent position clusters (house
     assumption from scripts 18/24, unchanged).
  4. This controls the SINGLE-mutant -0.0733 (ddg vs own_e_b); [AD4]'s
     double-mutant interaction null is a separate result.
  5. ESM-2 side-by-side rows are new computations on the V2 frame (no
     prior controlled delta_esm~own_e_b figure exists in the task docs);
     n's differ from script 24's published rows by frame construction.""")
    print(f"\nAD5 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
