"""A1+A2 — manuscript-review-response Group A (task doc
docs/tasks/manuscript-review-response/MANUSCRIPT_REVIEW_RESPONSE.md,
Group A). PRE-REGISTERED: this docstring was written before the first
run of this script; no number produced by it was seen before these
rules were fixed.

WHY THIS SCRIPT EXISTS (the write-up error being corrected):
  PROJECT_SUMMARY_FINAL.md L212-215 claims ThermoMPNN "shows a
  comparable correlation and carries genuinely independent information
  from ESM-2's shift, confirmed via a joint statistical model" — i.e.
  scripts/81 / [AD8]'s semipartial decomposition of pred_eb. But
  pred_eb = ddG(v) + ddG(A222V) adds a single constant to every row
  (scripts/68's pre-registered ADDITIVE choice), so pred_eb is
  rank-identical to raw single-mutant ddG — a stability-SEVERITY score,
  not an interaction term. This was already disclosed in [V4]'s own
  entry (SESSION_LOG.md L2413-2420: "because ddG(A222V) is a constant,
  pred_eb's Spearman rho is identical to ddG(v) vs e.b") and in
  scripts/81's gate G4. Group A confirms that degeneracy from the
  on-disk columns (A1), then reruns the SAME joint decomposition with
  ThermoMPNN-D's genuinely non-degenerate native double-mutant term
  interaction_D (A2), then produces corrected severity-baseline framing
  (A3, written up in the session log — no computation here).

A1 (fresh confirmation, actual on-disk columns only):
  From data/processed/task_V2_thermompnn_ddg.csv compute, on BOTH the
  full frame (10,141 rows) and the matched frame (own_e_b finite x
  delta_esm finite): Spearman(pred_eb, ddg) with the EXACT deviation
  from 1.0 printed whatever it is, exact rank-vector equality
  (rankdata equality at every row), and the affine fit
  pred_eb = ddg + k (k = mean(pred_eb - ddg), max|resid|).
  scripts/81's own G4 gate output is quoted alongside in the session
  log from its original run log (ad8_full.log), not re-run here.

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G0 input existence: V2, Z1, task77, task81 CSVs all present, else
     STOP with the exact missing path (never substitute).
  G1 frame identity: matched frame n==9595 and positions==586 (Z1's
     logged intersection); task77's own matched rows are the SAME
     hgvs_pro set (validate 1:1 merge); interaction_D finite on every
     matched row (accounting printed at each step, AGENTS sec 5).
  G2 zero-order identity: spearman(delta_esm, own_e_b) == Z1's
     matched_intersection ESM rho to < 1e-12, read FROM the CSV.
  G3 cross-session statistic identity: spearman(interaction_D,
     own_e_b) must round to +0.0154 at 4 dp — AD4's logged primary
     (DEEPDIVE_LOG.md L2328: "+0.0154 [-0.0166, +0.0465] p_boot=0.3406
     n=9595 clusters=586") — the same 4-dp cross-check precedent as
     script 96's G2 ("reproduces AD4's rho ... within 4 dp"). Exact
     full-precision value printed alongside the gate.
  G4 A1 premise: pred_eb rank-identical to ddg at EVERY row on BOTH
     frames (exact rankdata equality — NOT spearman==1.0, which can
     differ by fp noise; the exact spearman deviation is printed as
     information). Fail => A1's premise is broken; STOP.
  G5 comparator non-degeneracy: interaction_D's ranks differ from
     ddg's at >= 1 row on the matched frame (it must not be another
     constant-offset stand-in); exact rho(interaction_D, ddg) printed.
  G6 closed-form validity (A2 model): 1 - r12^2 > 1e-6 and
     R2_full >= max(R2_E, R2_T) - 1e-9.
  G7 extension fidelity vs scripts/81: re-run the extended bootstrap
     with T = ddg (AD8's exact configuration) on the matched frame and
     require pooled obs of unique_T, unique_E, R2_full to reproduce
     data/processed/task81_joint_semipartial.csv's pooled row to
     < 1e-12; additionally require its three CIs to < 1e-12 WHEN
     N_BOOT == 10000 (the CSV was made with N_BOOT=10000 seed 0; in
     smoke the CI check prints DEFERRED and only obs is compared —
     pre-registered, not a post-hoc skip). FAIL => this script's draw
     loop deviates from scripts/81's convention; STOP.

MACHINERY (reuse, not rewrite — AGENTS sec 2/7):
  components() is imported from scripts/81_joint_semipartial.py via
  importlib (its exact closed-form 2-predictor rank R2). The bootstrap
  draw loop (boot_ext) mirrors 81's boot_scope exactly — np.unique
  positions -> groups, default_rng(0), rng.integers(0, nc, nc),
  duplicate positions concatenated as their rows, ALL ranks recomputed
  inside every draw (re-derivation, not relabeling) — but collects two
  extra keys (R2_E, R2_T) so zero-orders get CIs too (task A2a asks
  for CIs on the zero-order correlations as well). G7 verifies this
  extension is bitwise-faithful to 81's saved outputs before any A2
  number is used.

STATISTICS (A2: y = own_e_b, E = delta_esm, T = interaction_D; pooled
  primary, regions 1-4 secondary/descriptive with no decision rule —
  same split as scripts/81):
  ranks (average ranks = Spearman scale); zero-orders r1=corr(y,E),
  r2=corr(y,T), r12=corr(E,T);
  R2_full = (r1^2 + r2^2 - 2 r1 r2 r12)/(1 - r12^2)  (exact OLS R2 on
  ranks); unique_T = R2_full - R2_E; unique_E = R2_full - R2_T;
  shared = R2_E + R2_T - R2_full.
  Position-cluster bootstrap, N_BOOT env default 10000, seed 0,
  percentile CIs, two-sided p = 2*min(frac<=0, frac>=0) bounded at 1,
  NaN draws excluded and counted (printed if any).

PRE-REGISTERED STRUCTURAL FACT AND READING RULE (stated before any
  number of this script was seen; purely algebraic, not data-dependent):
  unique_T = (r2 - r1*r12)^2 / (1 - r12^2) >= 0 IDENTICALLY (and
  unique_E likewise) — in-sample OLS R2 is non-decreasing in regressors.
  Therefore the percentile CI of a unique component can never extend
  meaningfully below 0, and "CI excludes 0" for these components is
  structurally weak evidence: it can fire for an arbitrary predictor.
  [AD8]'s own output already exhibits this — its p printed "<1/N"
  (p = 0, zero of 10,000 draws <= 0). Hence:
  (1) scripts/81's case (i)/(ii)/(iii) rule is applied VERBATIM and
      printed (comparability with AD8), and
  (2) the pre-registered verdict content is MAGNITUDE-based: unique_T
      as a fraction of R2_full and of its own zero-order R2_T, plus a
      printed descriptive scale reference for a single uninformative
      regressor's expected in-sample R2 gain, (1 - R2_full)/n — a
      back-of-envelope n^-1 scale, explicitly NOT a calibrated null (a
      permutation baseline for unique_T was not requested by Group A
      and is not run here). This reading rule is disclosed as
      pre-registered algebra, not tuned to any observed result.
  Report exactly what the numbers show; do not adjust the framing
  (task A2b).

CROSS-CHECK (descriptive, not a gate): this script's bootstrap CI for
  r2 = rho(interaction_D, own_e_b) is printed next to AD4's logged
  [+ -]0.0166/0.0465 CI. Draw mechanics differ slightly between
  scripts.lib.stats.position_cluster_bootstrap (rng.choice) and this
  script's 81-convention loop (rng.integers), so a small difference is
  expected and reported, not gated.

LIMITATIONS (printed with results, AGENTS sec 6): rank-based/additive;
  "independent" = unique rank-variance on this frame, not causal;
  matched frame is Z1's (ESM loses 1,162 rows vs its own 10,757
  analysis set); outcome own_e_b for both directions; interaction_D's
  own zero-order result vs own_e_b is AD4's null (+0.0154, CI spans
  0); region rows secondary/descriptive; p bounded by 1/N_BOOT; the
  structural reading rule above.

SMOKE: N_BOOT=300 (G7 CI check DEFERRED by design), then full
  N_BOOT=10000. Both read from env per project convention.
OUTPUT: data/processed/task104_joint_decomposition_interactionD.csv
  (5 scope rows: pooled + regions 1-4, obs + CIs + p). Existing
  scripts, lib modules, and result CSVs untouched (read-only inputs).
  Next free script number after this: 105.
"""
import importlib.util
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROC = ROOT / "data" / "processed"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
Z1_PATH = PROC / "task_Z1_matched_n_headtohead.csv"
T77_PATH = PROC / "task77_thermompnnD_doubles.csv"
A81_PATH = PROC / "task81_joint_semipartial.csv"
OUT = PROC / "task104_joint_decomposition_interactionD.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
T0 = time.time()

# ---- reuse scripts/81's exact component machinery (import, not rewrite)
_spec = importlib.util.spec_from_file_location(
    "s81_for_104", ROOT / "scripts" / "81_joint_semipartial.py")
_s81 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s81)
components = _s81.components  # closed-form 2-predictor rank R2 (AD8's)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def pfmt(p):
    return "<1/N" if p == 0 else f"{p:.4f}"


def boot_ext(E, T, y, pos, n_boot, seed):
    """Position-cluster bootstrap mirroring scripts/81's boot_scope
    exactly (same grouping, same rng stream, ranks recomputed in every
    draw), extended to also collect R2_E/R2_T so zero-orders get CIs.
    G7 proves this extension reproduces 81's saved pooled row."""
    rng = np.random.default_rng(seed)
    uniq, inverse = np.unique(pos, return_inverse=True)
    groups = [np.flatnonzero(inverse == k) for k in range(len(uniq))]
    nc = len(groups)
    obs = components(E, T, y, np.arange(len(y)))
    keys = ("r1", "r2", "r12", "R2_E", "R2_T", "R2_full",
            "unique_T", "unique_E", "shared")
    draws = {k: np.full(n_boot, np.nan) for k in keys}
    for b in range(n_boot):
        pick = rng.integers(0, nc, nc)
        idx = np.concatenate([groups[k] for k in pick])
        c = components(E, T, y, idx)
        for k in keys:
            draws[k][b] = c[k]
    out = {"obs": obs, "n_nan": 0, "ci": {}, "p": {}}
    for k in keys:
        d = draws[k]
        nan = ~np.isfinite(d)
        out["n_nan"] = max(out["n_nan"], int(nan.sum()))
        d = d[~nan]
        lo, hi = np.percentile(d, [2.5, 97.5])
        out["ci"][k] = (float(obs[k]), float(lo), float(hi))
        if k in ("unique_T", "unique_E"):
            p = min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0)
            out["p"][k] = float(p)
    return out


def print_scope(tag, n, npos, res):
    o, ci = res["obs"], res["ci"]
    rf, uT, uE = ci["R2_full"], ci["unique_T"], ci["unique_E"]
    part_T = np.sign(o["beta_T"]) * np.sqrt(max(o["unique_T"], 0))
    part_E = np.sign(o["beta_E"]) * np.sqrt(max(o["unique_E"], 0))
    print(f"\n  [{tag}] n={n} pos={npos} r1={o['r1']:+.4f} "
          f"r2={o['r2']:+.4f} r12={o['r12']:+.4f} "
          f"R2_full={rf[0]:.6f} [{rf[1]:.6f},{rf[2]:.6f}]"
          + ("" if res["n_nan"] == 0
             else f"  (NaN draws excluded: {res['n_nan']})"))
    print(f"    zero-order CIs: r(y,ESM)={ci['r1'][0]:+.6f} "
          f"[{ci['r1'][1]:+.6f},{ci['r1'][2]:+.6f}] | "
          f"r(y,interaction_D)={ci['r2'][0]:+.6f} "
          f"[{ci['r2'][1]:+.6f},{ci['r2'][2]:+.6f}] | "
          f"r(ESM,interaction_D)={ci['r12'][0]:+.6f} "
          f"[{ci['r12'][1]:+.6f},{ci['r12'][2]:+.6f}]")
    print(f"    R2_E={ci['R2_E'][0]:.6f} [{ci['R2_E'][1]:.6f},{ci['R2_E'][2]:.6f}]"
          f"   R2_T={ci['R2_T'][0]:.6f} [{ci['R2_T'][1]:.6f},{ci['R2_T'][2]:.6f}]")
    print(f"    unique_T|ESM (semipartial interaction_D) = {uT[0]:.6f} "
          f"[{uT[1]:.6f},{uT[2]:.6f}] p={pfmt(res['p']['unique_T'])}  "
          f"part_r={part_T:+.4f}  = {uT[0]/o['R2_T']*100:.1f}% of "
          f"interaction_D zero-order R2, {uT[0]/rf[0]*100:.2f}% of R2_full")
    print(f"    unique_E|interaction_D (semipartial ESM-2) = "
          f"{uE[0]:.6f} [{uE[1]:.6f},{uE[2]:.6f}] "
          f"p={pfmt(res['p']['unique_E'])}  part_r={part_E:+.4f}  "
          f"= {uE[0]/o['R2_E']*100:.1f}% of ESM zero-order R2, "
          f"{uE[0]/rf[0]*100:.1f}% of R2_full")
    print(f"    shared (commonality) = {o['shared']:+.6f} "
          f"({o['shared']/rf[0]*100:.1f}% of R2_full); "
          f"unique_T+unique_E+shared == R2_full: "
          f"{abs(uT[0] + uE[0] + o['shared'] - rf[0]) < 1e-9}")


if __name__ == "__main__":
    banner(f"A1+A2 — Group A: pred_eb rank-identity + joint decomposition "
           f"with interaction_D (scripts/104)  N_BOOT={N_BOOT} seed={SEED}")

    # ---- G0: inputs exist ---------------------------------------------
    for p in (V2_PATH, Z1_PATH, T77_PATH, A81_PATH):
        if not p.exists():
            gfail(f"G0 FAIL: {p} missing — input not found. Stop.")
    print("  G0 PASS: all four input CSVs present (V2, Z1, task77, task81)")

    v2 = pd.read_csv(V2_PATH)
    t77 = pd.read_csv(T77_PATH)
    z1 = pd.read_csv(Z1_PATH)
    a81 = pd.read_csv(A81_PATH)

    # ---- A1: fresh pred_eb vs ddg rank identity -----------------------
    banner("A1 — FRESH RANK-IDENTITY CONFIRMATION (pred_eb vs ddg)", "-")
    m = v2.dropna(subset=["own_e_b"]).dropna(subset=["delta_esm"])
    print(f"  accounting: V2 {len(v2)} -> own_e_b finite x delta_esm "
          f"finite {len(m)} (matched positions {m['position'].nunique()})")
    for name, fr in (("full V2, 10,141 rows", v2),
                     ("matched frame, 9,595 rows", m)):
        rho = float(spearmanr(fr["pred_eb"], fr["ddg"]).statistic)
        ranks_eq = bool((rankdata(fr["pred_eb"]) ==
                         rankdata(fr["ddg"])).all())
        k = float((fr["pred_eb"] - fr["ddg"]).mean())
        resid = float(np.abs(fr["pred_eb"] - (fr["ddg"] + k)).max())
        print(f"  A1 [{name}]: spearman(pred_eb, ddg) = {rho!r} "
              f"(exact deviation from 1.0 = {1.0 - rho:.3e}) | exact "
              f"rankdata equality at every row: {ranks_eq} | affine "
              f"pred_eb = ddg {k:+.12f} exactly, max|resid| = {resid:.3e}")
        if not ranks_eq:
            gfail("G4 FAIL: pred_eb and ddg ranks differ — A1 premise "
                  "broken (would contradict [AD8] G4). Stop.")
    print("  G4 PASS: pred_eb rank-identical to ddg at every row on BOTH "
          "frames (exact rankdata equality; spearman deviation printed "
          "above is scipy float arithmetic, not a rank difference)")

    # ---- G1: frame identity ------------------------------------------
    m77 = t77.dropna(subset=["own_e_b"]).dropna(subset=["delta_esm"])
    if (len(m), m["position"].nunique()) != (9595, 586):
        gfail(f"G1 FAIL: matched frame n={len(m)} "
              f"pos={m['position'].nunique()}, Z1 logged 9595/586. Stop.")
    if set(m["hgvs_pro"]) != set(m77["hgvs_pro"]):
        gfail("G1 FAIL: task77's matched rows are not the same hgvs_pro "
              "set as V2's matched frame. Stop.")
    mm = m.merge(t77[["hgvs_pro", "interaction_D"]], on="hgvs_pro",
                 how="left", validate="1:1")
    n_int = int(np.isfinite(mm["interaction_D"]).sum())
    if n_int != len(mm):
        gfail(f"G1 FAIL: interaction_D finite on {n_int}/{len(mm)} "
              f"matched rows. Stop.")
    n, npos = len(mm), mm["position"].nunique()
    print(f"  G1 PASS: matched set n={n} positions={npos}; task77 same "
          f"hgvs_pro set (1:1 merge); interaction_D finite on all {n_int}")

    # ---- G2: zero-order identity vs Z1 --------------------------------
    zm = z1[z1["analysis_set"] == "matched_intersection"]
    z_esm = float(zm.loc[zm["predictor"].str.startswith("ESM"),
                         "rho"].iloc[0])
    y = mm["own_e_b"].to_numpy()
    E = mm["delta_esm"].to_numpy()
    T = mm["interaction_D"].to_numpy()
    r_esm = float(pd.Series(E).corr(pd.Series(y), method="spearman"))
    if abs(r_esm - z_esm) >= 1e-12:
        gfail(f"G2 FAIL: zero-order ESM rho {r_esm!r} != Z1 {z_esm!r}. "
              f"Stop.")
    print(f"  G2 PASS: zero-order rho(delta_esm, own_e_b) == Z1 matched "
          f"CSV to <1e-12 ({r_esm!r} vs {z_esm!r})")

    # ---- G3: cross-session identity of interaction_D's zero-order -----
    r_int = float(pd.Series(T).corr(pd.Series(y), method="spearman"))
    if round(r_int, 4) != 0.0154:
        gfail(f"G3 FAIL: rho(interaction_D, own_e_b) = {r_int!r} does "
              f"not round to +0.0154 (AD4's logged primary). Stop.")
    print(f"  G3 PASS: rho(interaction_D, own_e_b) = {r_int!r} rounds to "
          f"+0.0154 == AD4's logged primary (DEEPDIVE L2328) — "
          f"cross-session statistic identity, 4-dp precedent (script 96 "
          f"G2)")

    # ---- G5: comparator non-degeneracy --------------------------------
    rho_int_ddg = float(spearmanr(mm["interaction_D"],
                                  mm["ddg"]).statistic)
    ranks_same = bool((rankdata(mm["interaction_D"]) ==
                       rankdata(mm["ddg"])).all())
    if ranks_same:
        gfail("G5 FAIL: interaction_D rank-identical to ddg — not a "
              "genuinely non-degenerate comparator. Stop.")
    print(f"  G5 PASS: interaction_D NOT rank-identical to ddg "
          f"(rho(interaction_D, ddg) = {rho_int_ddg!r}; "
          f"ranks_equal = {ranks_same}) — genuinely non-degenerate")

    # ---- G6 + point values for the A2 model ---------------------------
    y_idx = np.arange(n)
    obs = components(E, T, y, y_idx)
    if not (1.0 - obs["r12"] ** 2 > 1e-6):
        gfail(f"G6 FAIL: 1 - r12^2 = {1 - obs['r12']**2:.3e} too small. "
              f"Stop.")
    if obs["R2_full"] < max(obs["R2_E"], obs["R2_T"]) - 1e-9:
        gfail(f"G6 FAIL: R2_full {obs['R2_full']:.6f} < max zero-order "
              f"R2 — algebra broken. Stop.")
    print(f"  G6 PASS: 1-r12^2 = {1 - obs['r12']**2:.4f}, "
          f"R2_full {obs['R2_full']:.6f} >= max zero-order R2")

    # ---- G7: extension fidelity vs scripts/81's saved output ----------
    banner("G7 — EXTENSION FIDELITY vs scripts/81 (T = ddg, AD8 config)",
           "-")
    pr81 = a81[a81["scope"] == "pooled"]
    if len(pr81) != 1:
        gfail(f"G7 FAIL: task81 CSV pooled row count = {len(pr81)}. "
              f"Stop.")
    pr81 = pr81.iloc[0]
    b81 = boot_ext(E, mm["ddg"].to_numpy(), y, mm["position"].to_numpy(),
                   N_BOOT, SEED)
    # NOTE (disclosed): the first smoke run (2026-09-26) failed here
    # because the obs check was CODED to also compare the lo/hi CI
    # columns, which at N_BOOT=300 legitimately differ from the CSV's
    # N_BOOT=10000 CIs. The pre-registered docstring rule is obs-always,
    # CI-only-at-10000; the code now implements exactly that (all nine
    # obs values matched the CSV to <=9e-17 in that failed run).
    _G7_COLS = (("unique_T", ("unique_T", "unique_T_lo", "unique_T_hi")),
                ("unique_E", ("unique_E", "unique_E_lo", "unique_E_hi")),
                ("R2_full", ("R2_full", "R2_full_lo", "R2_full_hi")))
    obs_ok = all(
        abs(b81["ci"][k][0] - float(pr81[cols[0]])) < 1e-12
        for k, cols in _G7_COLS)
    if not obs_ok:
        gfail("G7 FAIL: pooled obs (T=ddg) does not reproduce task81's "
              "pooled row to <1e-12 — this script's components call "
              "differs from AD8's. Stop.")
    print("  G7 obs PASS: pooled unique_T/unique_E/R2_full (T=ddg) "
          "reproduce task81 CSV pooled row to <1e-12")
    if N_BOOT == 10000:
        ci_ok = all(
            abs(b81["ci"][k][i] - float(pr81[col])) < 1e-12
            for k, cols in _G7_COLS
            for i, col in enumerate(cols))
        if not ci_ok:
            gfail("G7 FAIL: bootstrap CIs (T=ddg) do not reproduce "
                  "task81's pooled CIs to <1e-12 — draw loop deviates "
                  "from scripts/81's convention. Stop.")
        print("  G7 CI PASS: pooled CIs (T=ddg) reproduce task81 CSV "
              "pooled row to <1e-12 — extended draw loop is bitwise-"
              "faithful to scripts/81 (N_BOOT=10000, seed 0)")
    else:
        print(f"  G7 CI check DEFERRED (pre-registered: CSV was made at "
              f"N_BOOT=10000; this is the N_BOOT={N_BOOT} smoke — obs "
              f"check above is N-independent)")

    # ---- A2: the real run with interaction_D --------------------------
    banner(f"A2 — JOINT RANK MODEL with interaction_D: pooled primary "
           f"(N_BOOT={N_BOOT}, seed {SEED}; ranks recomputed per draw)",
           "-")
    scopes = [("pooled", mm)] + [
        (f"region{int(r)}", mm[mm["region"] == r])
        for r in sorted(mm["region"].unique())]
    rows, results = [], {}
    t_b = time.time()
    for i, (scope, s) in enumerate(scopes):
        res = boot_ext(s["delta_esm"].to_numpy(),
                       s["interaction_D"].to_numpy(),
                       s["own_e_b"].to_numpy(),
                       s["position"].to_numpy(), N_BOOT, SEED)
        results[scope] = res
        print_scope(scope, len(s), s["position"].nunique(), res)
        o = res["obs"]
        rows.append({
            "scope": scope, "n_rows": len(s),
            "n_positions": s["position"].nunique(),
            "r_yE": o["r1"], "r_yE_lo": res["ci"]["r1"][1],
            "r_yE_hi": res["ci"]["r1"][2],
            "r_yInt": o["r2"], "r_yInt_lo": res["ci"]["r2"][1],
            "r_yInt_hi": res["ci"]["r2"][2],
            "r_EInt": o["r12"], "r_EInt_lo": res["ci"]["r12"][1],
            "r_EInt_hi": res["ci"]["r12"][2],
            "R2_E": o["R2_E"], "R2_T": o["R2_T"],
            "R2_full": res["ci"]["R2_full"][0],
            "R2_full_lo": res["ci"]["R2_full"][1],
            "R2_full_hi": res["ci"]["R2_full"][2],
            "unique_T": res["ci"]["unique_T"][0],
            "unique_T_lo": res["ci"]["unique_T"][1],
            "unique_T_hi": res["ci"]["unique_T"][2],
            "unique_T_p": res["p"]["unique_T"],
            "unique_E": res["ci"]["unique_E"][0],
            "unique_E_lo": res["ci"]["unique_E"][1],
            "unique_E_hi": res["ci"]["unique_E"][2],
            "unique_E_p": res["p"]["unique_E"],
            "shared": o["shared"]})
        if i == 0:
            el = time.time() - t_b
            print(f"    (timing: pooled draw set {el:.1f}s; project all "
                  f"scopes ~{el / (i + 1) * len(scopes):.0f}s)")

    # ---- pre-registered decision + reading rule -----------------------
    pr = results["pooled"]
    uT, uE = pr["ci"]["unique_T"], pr["ci"]["unique_E"]
    T_excl = not (uT[1] <= 0 <= uT[2])
    E_excl = not (uE[1] <= 0 <= uE[2])
    banner("DECISION (scripts/81's rule applied verbatim, pooled scope)",
           "-")
    if T_excl and E_excl:
        mech = ("case (i): BOTH carry independent information (both "
                "semipartial CIs exclude 0)")
    elif T_excl and not E_excl:
        mech = ("case (ii): ONLY interaction_D is independent beyond "
                "ESM-2")
    elif E_excl and not T_excl:
        mech = ("case (ii): ONLY ESM-2 is independent beyond "
                "interaction_D")
    else:
        mech = ("case (iii): neither semipartial excludes 0")
    print(f"  unique_T CI excludes 0: {T_excl} | unique_E CI excludes "
          f"0: {E_excl}")
    print(f"  MECHANICAL VERDICT under 81's rule: {mech}.")
    print("  STRUCTURAL READING RULE (pre-registered, algebraic — "
          "unique_T = (r2 - r1*r12)^2/(1 - r12^2) >= 0 identically, so "
          "its CI cannot extend below 0; CI-exclusion for these "
          "components is structurally weak evidence and is NOT the "
          "verdict content here):")
    o = pr["obs"]
    floor = (1.0 - o["R2_full"]) / n
    print(f"    unique_T = {o['unique_T']:.6f} = "
          f"{o['unique_T'] / o['R2_full'] * 100:.2f}% of R2_full "
          f"{o['R2_full']:.6f}, = {o['unique_T'] / o['R2_T'] * 100:.1f}% "
          f"of interaction_D's own zero-order R2 {o['R2_T']:.6f}; "
          f"descriptive in-sample-gain scale for one uninformative "
          f"regressor (1-R2_full)/n ~ {floor:.2e} (n^-1 back-of-envelope, "
          f"NOT a calibrated null).")
    print(f"    unique_E = {o['unique_E']:.6f} = "
          f"{o['unique_E'] / o['R2_full'] * 100:.1f}% of R2_full; "
          f"shared = {o['shared']:+.6f} "
          f"({o['shared'] / o['R2_full'] * 100:.1f}%); "
          f"r12(ESM, interaction_D) = {o['r12']:+.4f}.")
    print(f"    A2b HONEST VERDICT (magnitude-based, task A2b): "
          f"interaction_D contributes "
          f"{'little to no' if o['unique_T'] / o['R2_full'] < 0.05 else 'some'} "
          f"unique rank-variance beyond ESM-2's shift "
          f"({o['unique_T'] / o['R2_full'] * 100:.2f}% of R2_full), on "
          f"top of its own zero-order null (AD4: +0.0154, CI spans 0). "
          f"Full-model R2 explains {o['R2_full'] * 100:.2f}% of own_e_b "
          f"rank variance in total.")
    # descriptive cross-check vs AD4's logged CI for r2
    print(f"  Cross-check (descriptive, not gated): bootstrap CI for "
          f"r2 = [{pr['ci']['r2'][1]:+.4f},{pr['ci']['r2'][2]:+.4f}] vs "
          f"AD4's logged [+ -]0.0166/0.0465 (DEEPDIVE L2328) — draw "
          f"mechanics differ (rng.choice vs rng.integers), small "
          f"differences expected.")
    print("  Region rows are SECONDARY/descriptive (no decision rule; "
          "heterogeneity noted per AD6/AD7 precedent).")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\n  saved {len(rows)} scope rows -> {OUT.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. Rank-based/additive: "independent" = unique rank-variance on
     this frame, not causal or mechanistic separation.
  2. Matched frame is Z1's: ESM loses 1,162 rows vs its own 10,757
     analysis set; zero-order pinned to Z1's CSV by G2.
  3. Outcome for both directions is own_e_b (same as Z1/V5/AD8).
  4. interaction_D's own zero-order vs own_e_b is AD4's null
     (+0.0154, CI [-0.0166,+0.0465] spans 0), cross-checked by G3.
  5. Unique-component CIs are structurally nonnegative (pre-registered
     reading rule above); p values are position-cluster bootstrap,
     bounded by 1/N_BOOT.
  6. pred_eb vs ddg rank identity (A1/G4) is exact rankdata equality;
     spearman deviations printed are float arithmetic only.{os.linesep}  7. This script's bootstrap CI for r2 vs AD4's is a descriptive
     cross-check (different draw mechanics), not a gate.""")

    print(f"\nSCRIPT 104 DONE  ({time.time() - T0:.1f}s)  "
          f"A1: rank identity CONFIRMED | A2 mechanical case: {mech}")
