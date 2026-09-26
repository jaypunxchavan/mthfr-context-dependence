"""
Task B1 (reliability-and-decompositions): Mundlak decomposition of the
ThermoMPNN/ESM-2 sign flip, and the FE-granularity x control-set 2x2.

PRE-REGISTRATION (written before any number below existed; AGENTS s0/s6)

THE FLIP UNDER TEST (AD5's logged results, DEEPDIVE_LOG L2532-2539):
  SPEC A (task-literal: f_bar + POSITION FE): ddg coef -0.1042,
      delta_esm coef -0.0483  (both negative, both SURVIVE)
  SPEC B (script-24-literal: f_bar_a222v+grantham+blosum62+rsa +
      DOMAIN FE): ddg coef +0.0790, delta_esm coef +0.0353 (positive)
  The two specs varied FE granularity AND control set AT ONCE, so the
  sign flip cannot be attributed. B1c's 2x2 separates the two factors.

FRAME (frozen, script 78's construction reused verbatim):
  V2 table task_V2_thermompnn_ddg.csv (10,141 rows) LEFT-MERGED to
  phase5_analysis_table.csv on hgvs_pro (f_bar, f_bar_a222v, f_bar_wt),
  grantham/blosum62 via scripts.lib.features.add_substitution_features,
  rsa+domain via add_structural_features(load_structural_features()).

GATES (failure => print, sys.exit(1); no threshold raising, no retry):
  G1 frame identity: analysis rows (own_e_b non-null) must be exactly
     9,595 / 586 positions AND rho(ddg, own_e_b) must equal -0.0733
     within 5e-4 (AD5's own identity gate, same tolerances).
  G2 design checks: every 2x2 regression goes through script 78's
     run_spec, which enforces exact rank == k, finite coef/SE/p, cluster
     count == position count -- imported as THE SINGLE IMPLEMENTATION
     (importlib of scripts/78, not a copy), so machinery identity with
     AD5 is structural.
  G3 reproduction anchor: cells T+P and 24+D are BY CONSTRUCTION
     identical designs to AD5's SPEC A and SPEC B (see below); their
     focal coefs for ddg and delta_esm must match task78_thermompnn_
     controls.csv to < 1e-8 or the run stops.

B1a / B1b -- MUNDLAK (literal task spec, no additions):
  For x in {ddg (B1a), delta_esm (B1b)} on the 9,595-row frame:
      x_within_i    = x_i - mean(x | position_i)
      x_between_i   = mean(x | position_i)
      own_e_b_i = b0 + b_within * x_within_i + b_between * x_between_i
                  + e_i,  cluster-robust SEs by position (statsmodels
                  cov_type="cluster").
  PRE-REGISTERED: components enter UNSCALED (both in x's own units, so
  b_within and b_between are directly comparable and the difference
  test is scale-invariant); no other controls are added (the task's
  specification is complete as written -- most-literal reading).
  Report: b_within with cluster-robust 95% CI, b_between with its CI,
  and the DIRECT test b_within - b_between with
  SE_diff = sqrt(V_ww + V_bb - 2 V_wb) from the cluster-robust
  covariance, two-sided normal p (statsmodels' cluster inference is
  normal-based; same convention here). "Differ" declared at
  alpha = 0.05. Exact-decomposition sanity: max|x_within +
  x_between - x| < 1e-12, else stop.

B1c -- THE 2x2 (always all 4 cells x both signed focals = 8
  regressions, nothing chosen after seeing results):
    cell   controls (continuous)                                   FE
    T+P    f_bar                                                   position
    T+D    f_bar, rsa                                              domain
    24+P   f_bar_a222v, grantham, blosum62                         position
    24+D   f_bar_a222v, grantham, blosum62, rsa                    domain
  rsa handling (DISCLOSURE, not a new choice): rsa is a per-position
  constant (V4 confirmed this session: 0 positions with >1 RSA across
  11,902 variants), hence EXACTLY collinear with position FE -- script
  78's documented SPEC A amendment dropped it under position FE for
  that reason and G2's exact rank check would fail otherwise. rsa is
  therefore present in both domain-FE cells and absent from both
  position-FE cells, with the same note AD5 printed.
  Machinery: script 78's run_spec verbatim (z-score continuous inside
  the frame, z-score y, dummy FE drop_first, cluster-robust by
  position, survival = focal CI excludes 0) -- reported for context,
  but B1's verdicts below do NOT depend on the survival rule.

FLIP-ATTRIBUTION RULE (fixed here, before running):
  For each focal, let s_TP, s_TD, s_24P, s_24D be the four coef signs.
    FE-GRANULARITY-DRIVEN  iff  s_TP != s_TD AND s_24P != s_24D
                                AND s_TP == s_24P AND s_TD == s_24D
    CONTROL-SET-DRIVEN     iff  s_TP != s_24P AND s_TD != s_24D
                                AND s_TP == s_TD AND s_24P == s_24D
    otherwise              ->  NOT SEPARABLE into one factor
  (checkerboard across FE levels vs across control sets.) Both focals
  get their own verdict; they are not pooled.

B1d -- statement required by the task (V4-confirmed premise): SPEC B's
  structural controls (rsa, domain) are per-position constants, i.e. by
  construction BETWEEN-position quantities; this is the prior for where
  the flip lives. The script prints the fact and the observed 2x2
  pattern side by side; the consistency judgment is written in the log.

LIMITATIONS (printed with results, AGENTS s6):
  - OLS on z-scored levels is a linear partial association; the -0.0733
    headline is rank-based.
  - Cluster-robust SEs assume independent clusters (positions), the
    house assumption.
  - The Mundlak between coefficient is identified across 586 clusters;
    its SE is a cluster-level quantity.
  - The 2x2 attributes the sign change to a DESIGN FACTOR (which
    specification choice coincides with it), not to a causal mechanism.
  - No bootstrap/permutation exists by design here: inference is the
    specified cluster-robust CI, so there is no N to reduce.

Output: data/processed/task93_b1_mundlak_2x2.csv
Run: venv/bin/python3 scripts/93_b1_mundlak_and_2x2.py
"""

import importlib.util
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm, spearmanr

from scripts.lib.io import load_structural_features
from scripts.lib.features import add_substitution_features, \
    add_structural_features

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
PH5_PATH = PROC / "phase5_analysis_table.csv"
T78 = PROC / "task78_thermompnn_controls.csv"
EXPECTED_N, EXPECTED_POS = 9595, 586
HEADLINE_RHO, TOL = -0.0733, 5e-4
FOCALS = ["ddg", "delta_esm"]


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


# ---- script 78's run_spec: THE single implementation (not a copy) ----
_s78 = importlib.util.spec_from_file_location(
    "ad5_controls", ROOT / "scripts" / "78_thermompnn_multivariable_controls.py")
_m78 = importlib.util.module_from_spec(_s78)
_s78.loader.exec_module(_m78)
run_spec = _m78.run_spec


def mundlak(d, xcol):
    """Own_e_b on (x - xbar_pos) + xbar_pos, cluster-robust by position.
    Returns coefs, CIs, and the direct within-vs-between difference test."""
    x = d[xcol].to_numpy(dtype=float)
    xb = d.groupby("position")[xcol].transform("mean").to_numpy()
    xw = x - xb
    dec = float(np.max(np.abs(xw + xb - x)))
    if dec >= 1e-12:
        gfail(f"mundlak({xcol}): decomposition |diff|={dec:.3e} >= 1e-12")
    X = sm.add_constant(pd.DataFrame({"within": xw, "between": xb}))
    m = sm.OLS(d["own_e_b"].to_numpy(dtype=float), X).fit(
        cov_type="cluster", cov_kwds={"groups": d["position"].to_numpy()})
    bw, bb = float(m.params["within"]), float(m.params["between"])
    sew, seb = float(m.bse["within"]), float(m.bse["between"])
    V = m.cov_params()
    vww, vbb, vwb = (float(V.loc["within", "within"]),
                     float(V.loc["between", "between"]),
                     float(V.loc["within", "between"]))
    se_diff = float(np.sqrt(vww + vbb - 2 * vwb))
    diff = bw - bb
    z = diff / se_diff
    p = 2.0 * (1.0 - norm.cdf(abs(z)))
    return {
        "x": xcol, "n": len(d), "n_positions": int(d["position"].nunique()),
        "within": bw, "within_lo": bw - 1.96 * sew, "within_hi": bw + 1.96 * sew,
        "between": bb, "between_lo": bb - 1.96 * seb,
        "between_hi": bb + 1.96 * seb,
        "diff": diff, "diff_se": se_diff,
        "diff_lo": diff - 1.96 * se_diff, "diff_hi": diff + 1.96 * se_diff,
        "diff_p": p, "differ": bool(p < 0.05), "decomp_max": dec,
    }


def main():
    log("B1 -- MUNDLAK + FE-GRANULARITY x CONTROL-SET 2x2 (scripts/93)")
    log("pre-registered: unscaled components, alpha=0.05 difference test,"
        " flip-attribution rule fixed in docstring")

    # ---- frame (script 78's construction verbatim) ----
    v2 = pd.read_csv(V2_PATH)
    ph5 = pd.read_csv(PH5_PATH)[["hgvs_pro", "f_bar", "f_bar_a222v",
                                 "f_bar_wt"]]
    df = v2.merge(ph5, on="hgvs_pro", how="left")
    df = add_structural_features(add_substitution_features(df),
                                 load_structural_features())
    base = df[df["own_e_b"].notna()].copy()
    rho_head = float(spearmanr(base["ddg"], base["own_e_b"]).statistic)
    if (len(base), base["position"].nunique()) != (EXPECTED_N, EXPECTED_POS):
        gfail(f"G1 FAIL: frame {len(base)}/"
              f"{base['position'].nunique()} != {EXPECTED_N}/{EXPECTED_POS}")
    if abs(rho_head - HEADLINE_RHO) > TOL:
        gfail(f"G1 FAIL: rho {rho_head:+.6f} != {HEADLINE_RHO} +- {TOL}")
    log(f"G1 frame identity PASS: n={len(base)} / "
        f"{base['position'].nunique()} positions, "
        f"rho(ddg, own_e_b) = {rho_head:+.6f} (AD5 identity, same tol)")
    rho_esm = float(spearmanr(base["delta_esm"], base["own_e_b"]).statistic)
    log(f"  context: rho(delta_esm, own_e_b) on this frame = "
        f"{rho_esm:+.6f} (Z1 matched: -0.0771)")

    # ---- B1a / B1b: Mundlak ----
    log("\n" + "=" * 74)
    log("B1a/B1b  MUNDLAK: own_e_b ~ (x - xbar_pos) + xbar_pos, "
        "cluster-robust by position")
    log("=" * 74)
    mrows = []
    for xcol in FOCALS:
        r = mundlak(base, xcol)
        mrows.append(r)
        log(f"\n  x = {r['x']}   (n={r['n']}, {r['n_positions']} clusters; "
            f"decomposition sanity max|diff| = {r['decomp_max']:.1e})")
        log(f"    b_within  = {r['within']:+.6f} "
            f"CI [{r['within_lo']:+.6f}, {r['within_hi']:+.6f}]")
        log(f"    b_between = {r['between']:+.6f} "
            f"CI [{r['between_lo']:+.6f}, {r['between_hi']:+.6f}]")
        log(f"    DIRECT TEST (within - between): {r['diff']:+.6f} "
            f"SE {r['diff_se']:.6f} CI [{r['diff_lo']:+.6f}, "
            f"{r['diff_hi']:+.6f}] p = {r['diff_p']:.4g} -> "
            f"{'DIFFER at alpha=0.05' if r['differ'] else 'do NOT differ at alpha=0.05'}")

    # ---- B1c: the 2x2 ----
    log("\n" + "=" * 74)
    log("B1c  2x2: FE granularity (position/domain) x control set "
        "(task-literal / script-24-literal); both signed focals")
    log("=" * 74)
    log("  note: rsa is a per-position constant (V4: 0 positions with >1 "
        "RSA / 11,902 variants) -> exactly collinear with position FE; "
        "dropped under position FE per script 78's documented SPEC A "
        "amendment, kept under domain FE (G2 exact-rank enforced)")
    cells = [
        ("T+P", ["f_bar"], "position"),
        ("T+D", ["f_bar", "rsa"], "domain"),
        ("24+P", ["f_bar_a222v", "grantham", "blosum62"], "position"),
        ("24+D", ["f_bar_a222v", "grantham", "blosum62", "rsa"], "domain"),
    ]
    rows = []
    for name, cont, fe_col in cells:
        for f in FOCALS:
            cols = [f, "own_e_b"] + cont + [fe_col, "position"]
            dd = base.dropna(subset=cols).copy()
            if len(dd) != EXPECTED_N:
                gfail(f"{name}/{f}: n={len(dd)} != {EXPECTED_N} -- rows "
                      f"must be identical across all cells")
            fe = pd.get_dummies(dd[fe_col], prefix=fe_col[:3],
                                drop_first=True, dtype=float)
            spec = pd.concat([
                dd[[f] + cont].add_prefix("z_").reset_index(drop=True),
                fe.reset_index(drop=True)], axis=1)
            spec = spec.rename(columns={f"z_{f}": f})
            spec["zy_own_e_b"] = dd["own_e_b"].to_numpy()
            spec["position"] = dd["position"].to_numpy()
            rows.append(run_spec(spec, f, name))

    # ---- G3: reproduction anchor vs AD5's own CSV ----
    t78 = pd.read_csv(T78)
    ok3 = True
    for cell, spec78 in (("T+P", "A"), ("24+D", "B")):
        for f in FOCALS:
            mine = [r for r in rows if r["spec"] == cell and r["focal"] == f]
            ref = t78[(t78["spec"] == spec78) & (t78["focal"] == f)]
            if len(mine) != 1 or len(ref) != 1:
                gfail(f"G3 FAIL: missing rows for {cell}/{f}")
            dref = abs(mine[0]["coef"] - float(ref["coef"].iloc[0]))
            ok3 = ok3 and dref < 1e-8
            log(f"  G3 {cell} focal={f}: coef {mine[0]['coef']:+.10f} vs "
                f"AD5 spec{spec78} {float(ref['coef'].iloc[0]):+.10f} "
                f"(|diff| = {dref:.2e}) -> {'OK' if dref < 1e-8 else 'FAIL'}")
    if not ok3:
        gfail("G3 FAIL -- 2x2 cells do not reproduce AD5's SPEC A/B "
              "designs. STOP.")
    log("  G3 reproduction anchor PASS: T+P == SPEC A, 24+D == SPEC B "
        "to < 1e-8 (machinery identity with AD5)")

    # ---- flip attribution (rule fixed in docstring) ----
    log("\n" + "=" * 74)
    log("B1c  VERDICT (flip-attribution rule fixed before running)")
    log("=" * 74)
    verd = {}
    for f in FOCALS:
        c = {r["spec"]: r for r in rows if r["focal"] == f}
        s = {k: ("+" if c[k]["coef"] > 0 else "-") for k in c}
        log(f"  {f:10s} signs: T+P {s['T+P']}  T+D {s['T+D']}  "
            f"24+P {s['24+P']}  24+D {s['24+D']}   "
            f"(coefs: T+P {c['T+P']['coef']:+.4f}  T+D {c['T+D']['coef']:+.4f}  "
            f"24+P {c['24+P']['coef']:+.4f}  24+D {c['24+D']['coef']:+.4f})")
        fe_driven = (s["T+P"] != s["T+D"] and s["24+P"] != s["24+D"]
                     and s["T+P"] == s["24+P"] and s["T+D"] == s["24+D"])
        ctrl_driven = (s["T+P"] != s["24+P"] and s["T+D"] != s["24+D"]
                       and s["T+P"] == s["T+D"] and s["24+P"] == s["24+D"])
        v = ("FE-GRANULARITY-DRIVEN" if fe_driven else
             "CONTROL-SET-DRIVEN" if ctrl_driven else "NOT SEPARABLE")
        verd[f] = v
        log(f"    -> {v}")

    # ---- B1d statement ----
    log("\n" + "=" * 74)
    log("B1d  PREMISE (V4-confirmed this session) + CONSISTENCY CHECK")
    log("=" * 74)
    log("  Fact: SPEC B's structural controls rsa AND domain are both "
        "per-position constants (V4: every variant at a position shares "
        "one RSA and one domain label) -> the entire structural control "
        "block is a BETWEEN-position quantity by construction. Under "
        "position FE it is fully absorbed; under domain FE only 3 "
        "between-domain indicators remain.")
    log(f"  Observed 2x2: ddg {verd['ddg']}; "
        f"delta_esm {verd['delta_esm']}")
    log("  Mundlak locations: "
        + "; ".join(f"{r['x']}: within {r['within']:+.4f} / "
                    f"between {r['between']:+.4f} "
                    f"({'differ' if r['differ'] else 'not different'})"
                    for r in mrows))

    # ---- save ----
    out = PROC / "task93_b1_mundlak_2x2.csv"
    srows = []
    for r in mrows:
        for part in ("within", "between"):
            srows.append({"group": "mundlak", "spec": r["x"],
                          "focal": part, "coef": r[part],
                          "ci_lo": r[f"{part}_lo"], "ci_hi": r[f"{part}_hi"],
                          "p": np.nan, "n": r["n"],
                          "n_positions": r["n_positions"]})
        srows.append({"group": "mundlak_diff", "spec": r["x"],
                      "focal": "within-minus-between", "coef": r["diff"],
                      "ci_lo": r["diff_lo"], "ci_hi": r["diff_hi"],
                      "p": r["diff_p"], "n": r["n"],
                      "n_positions": r["n_positions"]})
    for r in rows:
        srows.append({"group": "2x2", "spec": r["spec"], "focal": r["focal"],
                      "coef": r["coef"], "ci_lo": r["ci_lo"],
                      "ci_hi": r["ci_hi"], "p": r["p"], "n": r["n"],
                      "n_positions": r["n_positions"]})
    pd.DataFrame(srows).to_csv(out, index=False)
    log(f"\n[saved] {out}")
    log("\nLIMITATIONS: OLS on z-scored levels vs a rank headline; "
        "cluster-robust independence across 586 positions; between coef "
        "identified across clusters; the 2x2 attributes the sign change "
        "to a design factor, not a causal mechanism; rsa dropped under "
        "position FE by documented collinearity (script 78 amendment), "
        "not chosen here; no bootstrap/permutation by design (inference "
        "is the specified cluster-robust CI).")
    log("SCRIPT 93 COMPLETE -- rc=0.")


if __name__ == "__main__":
    main()
