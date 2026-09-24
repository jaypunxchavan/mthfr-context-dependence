"""AD8 — Joint model test: is ThermoMPNN's signal additive to ESM-2's?
(task doc L307-312). PRE-REGISTERED: this docstring was written before
the first run.

QUESTION: on the matched-n row set (Z1's intersection from the prior
session), fit both predictors jointly (rank-based) and report
semipartial contributions in each direction — a decisive test of
whether the two carry independent information, replacing the current
"CIs overlap" comparison.

ROW SET (reuse Z1's intersection, per spec): V2 (ThermoMPNN join frame)
x own_e_b finite x delta_esm finite. Expected n=9,595 / 586 positions
(Z1's logged "[Z1a] intersection n=9595 pos=586"). delta_esm has 0 NaN
in V2, so the set is V2.dropna(own_e_b) — accounted and printed at each
step (AGENTS sec 5: account for every dropped row).

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G1 row-set identity: n == 9595 and positions == 586, else STOP (a
     disagreement with Z1's logged intersection is a two-sources-disagree
     situation, AGENTS sec 10).
  G2 zero-order identity vs Z1's saved CSV: spearman(delta_esm, own_e_b)
     must equal Z1's matched_intersection ESM rho and spearman(ddg,
     own_e_b) must equal Z1's matched Thermo rho to < 1e-12, both read
     FROM data/processed/task_Z1_matched_n_headtohead.csv (the file is
     the record; missing file = STOP).
  G3 cross-source: Z1's Thermo rho must also equal AD7's stored pooled
     mono rho in data/processed/task80_region_rhos.csv to < 1e-12 (two
     independent runs, prior session vs this one, same statistic —
     column/statistic identity check per AGENTS sec 5; agreement found
     pre-run at 2.8e-17, gate keeps it honest).
  G4 column identity: Z1's Thermo predictor was pred_eb; this script
     uses ddg. pred_eb is an affine function of ddg (AD6 G3: exact),
     so their RANKS must be identical in this frame (rank equality at
     every row, else STOP). Rank-based results are therefore identical
     for ddg and pred_eb — disclosed rather than silently switched.
  G5 closed-form validity: 1 - rho_ET^2 > 1e-6 (predictors not
     collinear enough to break the 2-predictor R2 formula) and
     R2_full >= max(R2_E, R2_T) - 1e-9 (adding a predictor cannot
     reduce OLS R2), else STOP.

STATISTICS (rank-based throughout, average ranks = Spearman scale;
position-cluster bootstrap, N_BOOT env default 10,000, seed 0 —
ALL ranks recomputed inside every draw (re-derivation null, AGENTS
sec 4), resampling the 586 POSITIONS with replacement, never rows):
  For y = own_e_b, E = delta_esm, T = ddg (all ranked):
    zero-orders r1=corr(y,E), r2=corr(y,T), r12=corr(E,T);
    R2_E=r1^2, R2_T=r2^2;
    R2_full=(r1^2+r2^2-2*r1*r2*r12)/(1-r12^2)  (exact OLS R2 on ranks);
    unique_T ("semipartial of ThermoMPNN given ESM-2") = R2_full-R2_E;
    unique_E ("semipartial of ESM-2 given ThermoMPNN") = R2_full-R2_T;
    shared (commonality) = R2_E+R2_T-R2_full;
    part r's signed by the standardized full-model coefficients
    beta_T=(r2-r1*r12)/(1-r12^2), beta_E=(r1-r2*r12)/(1-r12^2).
  CIs + p_boot (two-sided, 2*min(frac<=0,frac>=0), bounded at 1) for
  unique_T and unique_E; percentile CI for R2_full. NaN draws excluded
  and counted (printed if any).

PRE-REGISTERED DECISION RULE (stated before any number is seen):
  "X carries information independent of the other predictor" iff the
  semipartial CI of X excludes 0 (p_boot < 0.05) on the pooled matched
  set:
    (i)  both exclude 0   -> both carry independent information;
    (ii) only one excludes 0 -> only that one is independent beyond the
         other; the other's apparent signal is shared/mediated;
    (iii) neither         -> the old "CIs overlap" comparison was not
         hiding anything: null, reported plainly either way.
  Effect sizes are ALWAYS printed with the significance: each unique
  contribution as a fraction of its own zero-order R2 and of R2_full,
  plus shared/R2_full, plus rho_ET (AGENTS sec 3: with n>9,000 tiny
  nonzero effects will exclude zero; the magnitude relative to R2_full
  and to zero-order R2 is the result, not the CI alone).

SECONDARY (pre-registered, descriptive — no decision rule attached,
given AD6/AD7's demonstrated region heterogeneity): the same pooled
machinery per region (1-4), printed with CIs. Region scopes are the V2
region column (scripts/lib/regions.py provenance, same as AD1-AD7).

DISCLOSED LIMITATIONS (also printed with results, AGENTS sec 6):
  - Rank-based, additive, linear in ranks; independence here means
    unique rank-variance, not causal or mechanistic separation.
  - The matched frame is Z1's: ESM loses 1,162 rows vs its own
    10,757 analysis set (Z1's documented artifact direction); both
    correlations on this frame are Z1's matched values (G2).
  - pred_eb vs ddg equivalence is rank-identity only (G4); absolute
    scales differ (irrelevant for rank-based fits, relevant if anyone
    re-uses this code on raw values).
  - Outcome is own_e_b for both directions (same outcome Z1/V5 used).
  - Zero-order region rhos for Thermo are in task80_region_rhos.csv;
    region zero-orders printed here are point values without CI
    (secondary scope; CIs here are for the semipartials only).

SMOKE: N_BOOT=300 (env), same code path, prints per-draw timing and
the full-run projection. Full: N_BOOT=10000.

OUTPUTS: data/processed/task81_joint_semipartial.csv (5 rows: pooled +
regions 1-4, all components + CIs). Existing scripts/libs/results
untouched. Next free script number after this: 82.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
Z1_PATH = PROC / "task_Z1_matched_n_headtohead.csv"
AD7_PATH = PROC / "task80_region_rhos.csv"
OUT = PROC / "task81_joint_semipartial.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def pfmt(p):
    return "<1/N" if p == 0 else f"{p:.4f}"


def components(E, T, y, idx):
    """All rank-based joint-model components on rows idx (re-ranked
    inside every bootstrap draw — re-derivation, not relabeling)."""
    ry = rankdata(y[idx])
    re = rankdata(E[idx])
    rt = rankdata(T[idx])
    R = np.corrcoef(np.vstack([ry, re, rt]))
    r1, r2, r12 = R[0, 1], R[0, 2], R[1, 2]
    denom = 1.0 - r12 * r12
    r2e, r2t = r1 * r1, r2 * r2
    r2f = (r2e + r2t - 2.0 * r1 * r2 * r12) / denom
    beta_t = (r2 - r1 * r12) / denom
    beta_e = (r1 - r2 * r12) / denom
    return {"r1": r1, "r2": r2, "r12": r12, "R2_E": r2e, "R2_T": r2t,
            "R2_full": r2f, "unique_T": r2f - r2e, "unique_E": r2f - r2t,
            "shared": r2e + r2t - r2f, "beta_T": beta_t, "beta_E": beta_e}


def boot_scope(E, T, y, pos, n_boot, seed):
    """Position-cluster bootstrap (positions resampled with
    replacement; duplicate positions concatenated as their rows)."""
    rng = np.random.default_rng(seed)
    uniq, inverse = np.unique(pos, return_inverse=True)
    groups = [np.flatnonzero(inverse == k) for k in range(len(uniq))]
    nc = len(groups)
    all_idx = np.arange(len(y))
    obs = components(E, T, y, all_idx)
    keys = ("unique_T", "unique_E", "R2_full")
    draws = {k: np.full(n_boot, np.nan) for k in keys}
    for b in range(n_boot):
        pick = rng.integers(0, nc, nc)
        idx = np.concatenate([groups[k] for k in pick])
        c = components(E, T, y, idx)
        for k in keys:
            draws[k][b] = c[k]
    out = {"obs": obs, "n_nan": 0}
    for k in keys:
        d = draws[k]
        nan = ~np.isfinite(d)
        out["n_nan"] = max(out["n_nan"], int(nan.sum()))
        d = d[~nan]
        lo, hi = np.percentile(d, [2.5, 97.5])
        out[k] = (float(obs[k]), float(lo), float(hi))
        if k in ("unique_T", "unique_E"):
            p = min(2.0 * min((d <= 0).mean(), (d >= 0).mean()), 1.0)
            out[k + "_p"] = float(p)
    return out


if __name__ == "__main__":
    banner(f"AD8 — JOINT RANK MODEL: semipartial contributions both "
           f"directions (scripts/81)  N_BOOT={N_BOOT} seed={SEED}")

    # ---- row set: Z1's intersection -----------------------------------
    v2 = pd.read_csv(V2_PATH)
    n0 = len(v2)
    step1 = v2.dropna(subset=["own_e_b"])
    step2 = step1.dropna(subset=["delta_esm"])
    print(f"  accounting: V2 {n0} -> own_e_b finite {len(step1)} "
          f"-> +delta_esm finite {len(step2)} "
          f"(V2 delta_esm NaN total {int(v2['delta_esm'].isna().sum())})")
    df = step2.copy()
    n, npos = len(df), df["position"].nunique()
    if (n, npos) != (9595, 586):
        gfail(f"G1 FAIL: matched set n={n} pos={npos}, Z1 logged "
              f"n=9595 pos=586 — two sources disagree. Stop.")
    print(f"  G1 PASS: matched set n={n} positions={npos} == Z1 "
          f"intersection")

    # ---- G2: zero-order identity vs Z1's saved CSV --------------------
    if not Z1_PATH.exists():
        gfail(f"G2 FAIL: {Z1_PATH} missing — Z1 record not found. Stop.")
    z1 = pd.read_csv(Z1_PATH)
    zm = z1[z1["analysis_set"] == "matched_intersection"]
    z_esm = float(zm.loc[zm["predictor"].str.startswith("ESM"), "rho"].iloc[0])
    z_thermo = float(zm.loc[zm["predictor"].str.startswith("Thermo"), "rho"].iloc[0])
    y = df["own_e_b"].to_numpy()
    E = df["delta_esm"].to_numpy()
    T = df["ddg"].to_numpy()
    r_esm = float(pd.Series(E).corr(pd.Series(y), method="spearman"))
    r_thermo = float(pd.Series(T).corr(pd.Series(y), method="spearman"))
    if abs(r_esm - z_esm) >= 1e-12 or abs(r_thermo - z_thermo) >= 1e-12:
        gfail(f"G2 FAIL: zero-order rhos disagree with Z1: ESM "
              f"{r_esm!r} vs {z_esm!r}, Thermo {r_thermo!r} vs "
              f"{z_thermo!r}. Stop.")
    print(f"  G2 PASS: zero-order rhos == Z1 matched CSV to <1e-12 "
          f"(ESM {r_esm!r}, Thermo {r_thermo!r})")

    # ---- G3: cross-source Z1 vs AD7 stored pooled rho -----------------
    if not AD7_PATH.exists():
        gfail(f"G3 FAIL: {AD7_PATH} missing — AD7 record not found. Stop.")
    a7 = pd.read_csv(AD7_PATH)
    a7_rho = float(a7[(a7["scoring"] == "mono")
                      & (a7["scope"] == "pooled")]["rho"].iloc[0])
    if abs(a7_rho - z_thermo) >= 1e-12:
        gfail(f"G3 FAIL: AD7 pooled mono rho {a7_rho!r} != Z1 Thermo "
              f"rho {z_thermo!r} — cross-session disagreement. Stop.")
    print(f"  G3 PASS: Z1 Thermo rho == AD7 task80 pooled mono rho to "
          f"<1e-12 ({a7_rho!r}) — two independent runs agree")

    # ---- G4: pred_eb vs ddg rank identity -----------------------------
    rank_eq = (rankdata(df["pred_eb"]) == rankdata(df["ddg"])).all()
    if not rank_eq:
        gfail("G4 FAIL: pred_eb and ddg ranks differ in this frame — "
              "column-identity assumption broken. Stop.")
    print(f"  G4 PASS: pred_eb rank-identical to ddg at all {n} rows "
          f"(Z1's predictor and this script's are the same rank variable)")

    # ---- pooled fit ----------------------------------------------------
    obs = components(E, T, y, np.arange(n))
    if not (1.0 - obs["r12"] ** 2 > 1e-6):
        gfail(f"G5 FAIL: 1 - rho_ET^2 = {1 - obs['r12']**2:.3e} too "
              f"small — closed-form R2 invalid. Stop.")
    if obs["R2_full"] < max(obs["R2_E"], obs["R2_T"]) - 1e-9:
        gfail(f"G5 FAIL: R2_full {obs['R2_full']:.6f} < max(R2_E, R2_T) "
              f"— algebra broken. Stop.")
    print(f"  G5 PASS: 1-rho_ET^2 = {1 - obs['r12']**2:.4f}, "
          f"R2_full {obs['R2_full']:.6f} >= max zero-order R2")

    banner("POOLED FIT (matched set, rank-based)", "-")
    print(f"  zero-orders: r(y,ESM) = {obs['r1']:+.6f}  "
          f"r(y,Thermo) = {obs['r2']:+.6f}  "
          f"r(ESM,Thermo) = {obs['r12']:+.6f}")
    print(f"  R2_E = {obs['R2_E']:.6f}   R2_T = {obs['R2_T']:.6f}   "
          f"R2_full = {obs['R2_full']:.6f}")

    banner(f"POSITION-CLUSTER BOOTSTRAP (N_BOOT={N_BOOT}, seed {SEED}; "
           f"ranks recomputed in every draw)", "-")
    scopes = [("pooled", df)] + [
        (f"region{int(r)}", df[df["region"] == r])
        for r in sorted(df["region"].unique())]
    rows = []
    results = {}
    t_b = time.time()
    for i, (scope, s) in enumerate(scopes):
        res = boot_scope(s["delta_esm"].to_numpy(), s["ddg"].to_numpy(),
                         s["own_e_b"].to_numpy(),
                         s["position"].to_numpy(), N_BOOT, SEED)
        results[scope] = res
        o = res["obs"]
        uT = res["unique_T"]
        uE = res["unique_E"]
        rf = res["R2_full"]
        part_T = np.sign(o["beta_T"]) * np.sqrt(max(o["unique_T"], 0))
        part_E = np.sign(o["beta_E"]) * np.sqrt(max(o["unique_E"], 0))
        print(f"\n  [{scope}] n={len(s)} pos={s['position'].nunique()} "
              f"r1={o['r1']:+.4f} r2={o['r2']:+.4f} "
              f"r12={o['r12']:+.4f} R2_full={rf[0]:.6f} "
              f"[{rf[1]:.6f},{rf[2]:.6f}]"
              + ("" if res["n_nan"] == 0
                 else f"  (NaN draws excluded: {res['n_nan']})"))
        print(f"    unique_T|ESM (semipartial ThermoMPNN) = {uT[0]:.6f} "
              f"[{uT[1]:.6f},{uT[2]:.6f}] p={pfmt(res['unique_T_p'])}  "
              f"part_r={part_T:+.4f}  = {uT[0]/o['R2_T']*100:.1f}% of "
              f"Thermo zero-order R2, {uT[0]/rf[0]*100:.1f}% of R2_full")
        print(f"    unique_E|Thermo (semipartial ESM-2)     = "
              f"{uE[0]:.6f} [{uE[1]:.6f},{uE[2]:.6f}] "
              f"p={pfmt(res['unique_E_p'])}  part_r={part_E:+.4f}  "
              f"= {uE[0]/o['R2_E']*100:.1f}% of ESM zero-order R2, "
              f"{uE[0]/rf[0]*100:.1f}% of R2_full")
        print(f"    shared (commonality) = {o['shared']:+.6f} "
              f"({o['shared']/rf[0]*100:.1f}% of R2_full); "
              f"unique_T+unique_E+shared == R2_full: "
              f"{abs(uT[0] + uE[0] + o['shared'] - rf[0]) < 1e-9}")
        rows.append({"scope": scope, "n_rows": len(s),
                     "n_positions": s["position"].nunique(),
                     "r_yE": o["r1"], "r_yT": o["r2"],
                     "r_ET": o["r12"], "R2_E": o["R2_E"],
                     "R2_T": o["R2_T"], "R2_full": rf[0],
                     "R2_full_lo": rf[1], "R2_full_hi": rf[2],
                     "unique_T": uT[0], "unique_T_lo": uT[1],
                     "unique_T_hi": uT[2],
                     "unique_T_p": res["unique_T_p"],
                     "unique_E": uE[0], "unique_E_lo": uE[1],
                     "unique_E_hi": uE[2], "unique_E_p": res["unique_E_p"],
                     "shared": o["shared"], "part_r_T": part_T,
                     "part_r_E": part_E})
        if i == 0:
            el = time.time() - t_b
            proj = el / (i + 1) * len(scopes)
            print(f"    (timing: pooled draw set {el:.1f}s; project "
                  f"all scopes ~{proj:.0f}s)")

    # ---- pre-registered decision (pooled scope) ------------------------
    pr = results["pooled"]
    T_excl = not (pr["unique_T"][1] <= 0 <= pr["unique_T"][2])
    E_excl = not (pr["unique_E"][1] <= 0 <= pr["unique_E"][2])
    banner("DECISION (pre-registered rule, pooled scope)", "-")
    if T_excl and E_excl:
        verdict = ("BOTH carry independent information: both semipartial "
                   "CIs exclude 0 (case i).")
    elif T_excl and not E_excl:
        verdict = ("ONLY ThermoMPNN is independent beyond ESM-2: its "
                   "semipartial excludes 0, ESM's does not (case ii).")
    elif E_excl and not T_excl:
        verdict = ("ONLY ESM-2 is independent beyond ThermoMPNN: its "
                   "semipartial excludes 0, Thermo's does not (case ii).")
    else:
        verdict = ("NEITHER semipartial excludes 0 (case iii): the old "
                   "'CIs overlap' comparison was not hiding anything — "
                   "null on the matched set, reported plainly.")
    print(f"  unique_T CI excludes 0: {T_excl} | unique_E CI excludes "
          f"0: {E_excl}")
    print(f"  VERDICT: {verdict}")
    print(f"  Effect sizes with the claim (AGENTS sec 3): unique_T = "
          f"{pr['obs']['unique_T']:.6f} ({pr['obs']['unique_T']/pr['obs']['R2_full']*100:.1f}% "
          f"of R2_full {pr['obs']['R2_full']:.6f}), unique_E = "
          f"{pr['obs']['unique_E']:.6f} "
          f"({pr['obs']['unique_E']/pr['obs']['R2_full']*100:.1f}% of "
          f"R2_full), shared = {pr['obs']['shared']:+.6f} "
          f"({pr['obs']['shared']/pr['obs']['R2_full']*100:.1f}%); "
          f"rho_ET = {pr['obs']['r12']:+.4f} — full-model R2 explains "
          f"{pr['obs']['R2_full']*100:.2f}% of own_e_b rank variance "
          f"in total (n={n}, both signals small in absolute terms).")
    print("  Region rows above are SECONDARY/descriptive (no decision "
          "rule attached; heterogeneity noted per AD6/AD7 precedent).")

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\n  saved {len(rows)} scope rows -> {OUT.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. Rank-based/additive: "independent" = unique rank-variance on
     this frame, not causal or mechanistic separation.
  2. Matched frame is Z1's: ESM loses 1,162 rows vs its own 10,757 set
     (Z1's documented artifact direction); zero-orders pinned to Z1's
     CSV by gate (G2) and cross-checked to AD7 (G3).
  3. pred_eb/ddg equivalence is rank-identity only (G4); raw-scale use
     of this code would need the affine relation stated separately.
  4. Outcome for both directions is own_e_b (same as Z1/V5).
  5. Semipartial CIs are the bootstrapped quantities; region zero-order
     rhos printed as points (Thermo's region CIs live in
     task80_region_rhos.csv).{os.linesep}  6. p values are position-cluster bootstrap, bounded by 1/N_BOOT;
     effect sizes reported alongside per project convention.""")

    print(f"\nAD8 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
