"""D1+D2 — difference-score reliability from the five ESM-1v checkpoints
(task doc `MANUSCRIPT_REVIEW_RESPONSE.md`, Group D). PRE-REGISTERED:
this docstring was written before the first run of this script; every
gate, formula, aggregation, and reporting rule below was fixed before
any number produced here was seen.

WHY (task background, restated so the record is self-contained):
  The observed reliability of the ESM-1v arm DIFFERENCE
  delta = score(A222V bg) - score(WT bg) across checkpoints is very low
  (median pairwise cross-checkpoint Spearman on deltas = 0.084365,
  T5a/T4a). Classical test theory's difference-score reliability
  (Lord 1956), applied to the two arms themselves, can be computed
  FORWARD from the arms' reliabilities and their inter-correlation:

      reliability(D) = [r_XX*Var(X) + r_YY*Var(Y)
                        - 2*r_XY*sqrt(Var(X)*Var(Y))]
                       ------------------------------------------------
                       [Var(X) + Var(Y) - 2*r_XY*sqrt(Var(X)*Var(Y))]

  with X = a checkpoint's raw WT-background score, Y = the same
  checkpoint's raw A222V-background score, D = Y - X. This forward
  value is then compared (D2d) to the actually observed delta
  reliability (0.0844) as a model-prediction-vs-observation check.
  The task doc explicitly anticipates the result may fall outside
  [0,1] and instructs: report it exactly as computed with the
  ill-conditioning diagnostic (denominator -> 0 as r_XY -> 1); NEVER
  clip.

DATA (one consistent source, per D1a — no mixing of prior contexts):
  Five ESM-1v checkpoint score CSVs
  data/processed/task_AC4_esm1v_member{1..5}_scores.csv (12,446 rows
  each; columns position, wt_aa, mut_aa, wt_logodds = X, av_logodds =
  Y, delta = Y - X), joined to the project's analysis base exactly as
  scripts/89 (N4/R4) did: base = task32_analysis_table.csv dropna on
  (own_e_b, GI_folinate_independent, delta_esm) -> expect 10,757 rows /
  654 positions; left-merge each member on (position, mut_aa),
  validate 1:1, require 0 unmatched and identical wt_aa labels.

THE FIVE INPUT QUANTITIES (D1a — all re-derived here, from these CSVs,
  on this base):
  r_XX = cross-checkpoint agreement on X: median of the 10 pairwise
         Spearman correlations across the 5 checkpoints. GATE: must
         reproduce the existing 0.8826 figure (6 dp: 0.882637;
         CALIBRATION_LOG L439 "AC4d printed median 0.882637", min
         0.859689 / max 0.890106; also script 97's gate "G4 WT =
         0.8826369 (tol 1e-6)"). Reproduction is a gate, as the task
         requires.
  r_YY = same procedure on Y (av_logodds) — FRESH, likely never
         isolated before; min/median/max reported.
  r_XY = per-checkpoint within-model Spearman(X_i, Y_i), 5 values;
         range and median reported. NOT reused from the previously
         cited 0.999636: that figure's provenance is re-confirmed here
         as C1d (OVERNIGHT_LOG L455-465) = ESM-2's
         Spearman(esm2_score_a222v_bg, esm2_score), n=10,757 — a
         different model, not one of these five checkpoints.
  Var(X), Var(Y) = per-checkpoint variances + their averages; stated
         explicitly per scale (see construction rules below) —
         Var(X) = Var(Y) is NOT assumed anywhere.

SCALE / CONSISTENCY RULE (assumption, most-literal reading, logged
  per troubleshooting rule 4 — decided BEFORE running):
  D1a mandates all three r's as Spearman. The D2a identity
  Var(D) = Var(X)+Var(Y) - 2*r_XY*sqrt(Var(X)*Var(Y)) holds exactly
  (fp) only when the Var's and r_XY live on the SAME scale, i.e. when
  r_XY is the Pearson correlation of the very variables whose
  variances are used. With r_XY mandated Spearman, that consistent
  scale is the RANK scale (Pearson on average ranks = Spearman).
  Therefore TWO constructions are computed, BOTH pre-registered, BOTH
  reported regardless of outcome (no selection after seeing results):
  * CONSTRUCTION R (PRIMARY): all five quantities on ranks — r_XX,
    r_YY as the mandated Spearman medians, r_XY = median of the 5
    within-checkpoint Spearmans, Var = variance of average ranks
    (per checkpoint, then averaged across checkpoints). The D2a
    identity is exact here by construction of the same-scale rule.
  * CONSTRUCTION W (SECONDARY, classical Lord instantiation): raw-score
    variances + Pearson correlations throughout (the historical
    test-theory reading of the formula). Its D2a identity is likewise
    exact per checkpoint with Pearson r_XY.
  The mixed scale (Spearman r + raw Var) is NOT computed as a
  prediction, because its own identity gate would fail by algebra;
  the raw-vs-rank gap (Pearson r_XY vs Spearman r_XY) is printed as
  information so the reader can see how far apart the two consistent
  constructions are.

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G0 inputs exist: task32 CSV + all 5 member CSVs (missing => STOP
     with the exact path).
  G1 base + join: base == 10,757 rows / 654 positions; every member
     joins 1:1 with 0 unmatched and identical wt_aa labels (script
     89's R4 discipline). Row accounting printed: 12,446 member rows
     -> 10,757 on base (the 1,689 difference is task32's analysis-set
     filtering, printed, not silently dropped).
  G2 r_XX reproduction: round(median of 10 pairwise Spearman on X,
     6) == 0.882637, else STOP (task-mandated gate).
  G3 observed-delta reproduction: round(median of the 10 pairwise
     Spearman on the checkpoints' delta columns, 6) == 0.084365
     (R7/T5a convention, same join) — this re-derived value IS the
     "observed delta reliability 0.0844" that D2d compares against;
     if it disagrees with the prior figure, the comparison has no
     ground -> STOP (two sources disagree, AGENTS sec 10).
     (Its CI [+0.052159, +0.122589] is QUOTED from T5a/T4a —
     DISATTENUATION_LOG L346 / PROJECT_SUMMARY_FINAL L81 — and not
     recomputed here; disclosed in output.)
  G4 member CSV internal integrity: max|delta - (av_logodds -
     wt_logodds)| < 1e-9 on all 12,446 rows of each member (pins the
     sign convention of D = Y - X against the file itself — AGENTS
     sec 5 sign-verification rule).
  G5 D2a identity, per checkpoint, BOTH constructions: relative
     deviation |Var(D_i) - (VarX_i + VarY_i - 2*r_XY_i*sqrt(VarX_i*
     VarY_i))| / max(1, |Var(D_i)|) < 1e-12 (fp64 "numerical
     precision" at these magnitudes — tolerance fixed here, pre-run).
     Fail => that construction's denominator cannot be trusted ->
     STOP. (An aggregate-inputs deviation using the cross-checkpoint
     medians/means is printed as INFORMATION — the exact identity is
     a per-checkpoint statement.)

D2b (point prediction): the formula verbatim, inputs aggregated
  exactly as D1a specifies: r_XX = the median (G2 value), r_YY = the
  median, r_XY = the median across the 5 checkpoints, Var(X) = mean
  over checkpoints, Var(Y) = mean over checkpoints. Computed for
  construction R (primary) and W (secondary). Both printed with full
  numerator, denominator, and inputs at full precision; if outside
  [0,1] or negative, printed exactly as computed with the
  pre-registered ill-conditioning diagnostic (never clipped). A
  descriptive sensitivity line also prints the formula with each
  checkpoint's own r_XY (median Var's held fixed) — labeled
  descriptive, no decision attached.

D2c (bootstrap, project-standard position-cluster):
  Resample the 654 positions with replacement (default_rng seed 0),
  concatenate the drawn positions' rows (duplicates included as their
  rows, as in scripts/81), and RECOMPUTE ALL FIVE INPUTS fresh inside
  every draw (re-derivation null, not relabeling): the two 10-pair
  Spearman medians (r_XX, r_YY — Pearson of per-column average ranks),
  the 5-value r_XY median, the Var means, and both constructions'
  predictions. N_BOOT from env (default 10000; smoke 300), seed 0.
  Report the empirical distribution of the predicted reliability for
  both constructions: n draws, non-finite counts (nan/inf), fraction
  negative, fraction in [0,1], percentiles [2.5, 25, 50, 75, 97.5] of
  finite draws, min, max — no clipping of extreme values (the
  heavy-tail IS the answer to whether a single predicted number is
  fair to quote).

D2d (comparison): state plainly, side by side — the forward
  prediction (point + bootstrap interval), the observed delta
  reliability (G3 re-derived full-precision value + quoted CI), and
  whether the prediction is inside [0,1] and whether the observed
  value falls inside the prediction's bootstrap interval; verdict
  sentence "consistent" or "inconsistent" written from those two
  facts only.

LIMITATIONS (printed with results, AGENTS sec 6):
  1. Classical difference-score reliability assumes X and Y's errors
     are uncorrelated; here X and Y come from the SAME checkpoint on
     the SAME rows, so checkpoint-specific noise is shared between
     arms by construction. That violation is exactly what pushes
     r_XY (~0.999+) far above r_XX (~0.88) and can drive the
     numerator negative — reported as computed, not repaired.
  2. r_XX/r_YY are cross-checkpoint agreement (parallel-forms flavor,
     5 forms) standing in for reliability in the classical formula.
  3. Primary numbers are rank-scale (construction R); construction W
     (raw/Pearson) reported alongside; the two can differ by orders
     of magnitude in the ratio because the denominator is a near-
     cancellation — this scale sensitivity is itself a headline of
     D2d's "fair to quote a single number?" question.
  4. Observed comparator 0.084365 is the median of 10 pairwise delta
     Spearmans on the same base (re-derived, gated G3); its CI is
     quoted from T5a/T4a, not recomputed here.
  5. Bootstrap draws can produce near-zero denominators; extreme /
     negative predictions are counted and reported, not winsorized.
  6. n = 10,757 / 654 (task32 analysis base); five checkpoints as
     shipped in the AC4 member CSVs (12,446 rows each before the base
     join).

SMOKE: N_BOOT=300 (gates + point + machinery), then full N_BOOT=10000.
OUTPUT: data/processed/task105_difference_score_reliability.csv (tidy
  long table: section/key/value/note). Existing scripts/CSVs untouched.
  Next free script number after this: 106.
"""
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.lib.stats import _spearman  # noqa: E402  (same fn as scripts/89)

PROC = ROOT / "data" / "processed"
T32_PATH = PROC / "task32_analysis_table.csv"
MEMBER_PATHS = {k: PROC / f"task_AC4_esm1v_member{k}_scores.csv"
                for k in range(1, 6)}
OUT = PROC / "task105_difference_score_reliability.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
T0 = time.time()

K_RXX_TARGET = 0.882637    # AC4d/R7 printed median, CALIBRATION_LOG L439
K_DELT_TARGET = 0.084365   # R7/T5a printed median, observed delta agreement
K_IDENTITY_REL_TOL = 1e-12  # fp64 "numerical precision", fixed pre-run

DIAGNOSTIC = (
    "DIAGNOSTIC (pre-provided by the task doc): the formula is "
    "numerically ill-conditioned specifically because r_XY is very "
    "close to 1 — the denominator Var(X)+Var(Y)-2*r_XY*sqrt(Var(X)*"
    "Var(Y)) = Var(Y-X) collapses toward zero when the two arms are "
    "nearly rank-identical, so tiny input differences are amplified "
    "by orders of magnitude in the ratio. Reported exactly as "
    "computed; NOT clipped (task D2b)."
)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def lord(rxx, ryy, rxy, vx, vy):
    """The task's formula verbatim (no simplification, no Vx==Vy
    assumption): returns (numerator, denominator, prediction)."""
    cross = rxy * math.sqrt(vx * vy)
    num = rxx * vx + ryy * vy - 2.0 * cross
    den = vx + vy - 2.0 * cross
    pred = num / den if den != 0.0 else float("nan")
    return num, den, pred


def identity_rel(vd, vx, vy, r):
    rhs = vx + vy - 2.0 * r * math.sqrt(vx * vy)
    return abs(vd - rhs) / max(1.0, abs(vd)), rhs


def summarize(preds, label):
    a = np.asarray(preds, dtype=float)
    fin = np.isfinite(a)
    f = a[fin]
    nan = int(np.isnan(a).sum())
    inf = int(np.isinf(a).sum())
    if len(f):
        p2_5, p25, p50, p75, p97_5 = np.percentile(
            f, [2.5, 25, 50, 75, 97.5])
        frac_neg = float((f < 0).mean())
        frac_01 = float(((f >= 0) & (f <= 1)).mean())
        mn, mx = float(f.min()), float(f.max())
    else:
        p2_5 = p25 = p50 = p75 = p97_5 = mn = mx = float("nan")
        frac_neg = frac_01 = float("nan")
    print(f"  [{label}] n_draws={len(a)} finite={int(fin.sum())} "
          f"nan={nan} inf={inf}")
    print(f"    percentiles of finite draws: p2.5={p2_5:.6g} "
          f"p25={p25:.6g} p50={p50:.6g} p75={p75:.6g} "
          f"p97.5={p97_5:.6g}")
    print(f"    min={mn:.6g} max={mx:.6g} | fraction negative="
          f"{frac_neg:.4f} | fraction in [0,1]={frac_01:.4f}")
    return {"n": len(a), "finite": int(fin.sum()), "nan": nan,
            "inf": inf, "p2_5": p2_5, "p25": p25, "p50": p50,
            "p75": p75, "p97_5": p97_5, "min": mn, "max": mx,
            "frac_neg": frac_neg, "frac_01": frac_01}


def inputs_on(idx, X, Y):
    """Recompute all five input quantities on the given rows.
    X, Y: (5, n) arrays, one row per checkpoint."""
    xd = X[:, idx]
    yd = Y[:, idx]
    rx = rankdata(xd, axis=1)
    ry = rankdata(yd, axis=1)
    # one 10x10 correlation matrix on ranks gives every Spearman
    C = np.corrcoef(np.vstack([rx, ry]))
    iu = np.triu_indices(5, 1)
    rxx = float(np.median(C[:5, :5][iu]))
    ryy = float(np.median(C[5:, 5:][iu]))
    rxy = float(np.median(np.diag(C[:5, 5:])))
    vx_rank = float(np.mean(np.var(rx, axis=1, ddof=0)))
    vy_rank = float(np.mean(np.var(ry, axis=1, ddof=0)))
    # construction W: raw Pearson + raw variances (same structure)
    Cr = np.corrcoef(np.vstack([xd, yd]))
    rxx_w = float(np.median(Cr[:5, :5][iu]))
    ryy_w = float(np.median(Cr[5:, 5:][iu]))
    rxy_w = float(np.median(np.diag(Cr[:5, 5:])))
    vx_raw = float(np.mean(np.var(xd, axis=1, ddof=0)))
    vy_raw = float(np.mean(np.var(yd, axis=1, ddof=0)))
    return dict(rxx=rxx, ryy=ryy, rxy=rxy, vx=vx_rank, vy=vy_rank,
                rxx_w=rxx_w, ryy_w=ryy_w, rxy_w=rxy_w,
                vx_w=vx_raw, vy_w=vy_raw)


if __name__ == "__main__":
    banner(f"D1+D2 — difference-score reliability from the five ESM-1v "
           f"checkpoints (scripts/105)  N_BOOT={N_BOOT} seed={SEED}")

    # ---- G0: inputs -------------------------------------------------
    for p in [T32_PATH, *MEMBER_PATHS.values()]:
        if not p.exists():
            gfail(f"G0 FAIL: {p} missing — input not found. Stop.")
    print("  G0 PASS: task32_analysis_table.csv + all 5 member CSVs "
          "present")

    # ---- G4: member CSV integrity (sign convention pinned) ----------
    memb = {}
    for k, p in MEMBER_PATHS.items():
        d = pd.read_csv(p)
        gap = float(np.abs(d["delta"] - (d["av_logodds"]
                                         - d["wt_logodds"])).max())
        if gap >= 1e-9:
            gfail(f"G4 FAIL: member {k} delta != av - wt "
                  f"(max|diff| = {gap:.3e}). Stop.")
        memb[k] = d
    print(f"  G4 PASS: all 5 members: delta == av_logodds - "
          f"wt_logodds on all {len(d)} rows (max|diff| < 1e-9) — "
          f"D = Y - X sign convention pinned against the files "
          f"(AGENTS sec 5)")

    # ---- G1: base + join --------------------------------------------
    t32 = pd.read_csv(T32_PATH)
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G1 FAIL: base n={len(base)} "
              f"pos={base['position'].nunique()}, expected 10757/654. "
              f"Stop.")
    print(f"  G1 base: task32 {len(t32)} -> dropna(own_e_b, GI, "
          f"delta_esm) {len(base)} rows / "
          f"{base['position'].nunique()} positions (== 10757/654) | "
          f"member CSVs have {len(d)} rows each -> "
          f"{len(d) - len(base)} rows outside the analysis base "
          f"(task32's set filtering, accounted, not dropped silently)")
    joined = {}
    for k, md in memb.items():
        j = base.merge(md[["position", "wt_aa", "mut_aa", "wt_logodds",
                           "av_logodds", "delta"]],
                       on=["position", "mut_aa"], how="left",
                       validate="1:1")
        miss = int(j["wt_logodds"].isna().sum())
        if miss:
            gfail(f"G1 FAIL: member {k} left {miss} base rows "
                  f"unmatched — exit (R4). Stop.")
        if not (j["wt_aa_x"] == j["wt_aa_y"]).all():
            gfail(f"G1 FAIL: member {k} wt_aa label mismatch vs base. "
                  f"Stop.")
        joined[k] = j
    print(f"  G1 PASS: R4 join — all 5 members cover the base exactly "
          f"({len(joined[1])} rows / "
          f"{joined[1]['position'].nunique()} positions, 1:1, "
          f"wt_aa labels match)")

    # stack arrays: X[k], Y[k], delta[k] over base rows
    ks = sorted(joined)
    X = np.vstack([joined[k]["wt_logodds"].to_numpy() for k in ks])
    Y = np.vstack([joined[k]["av_logodds"].to_numpy() for k in ks])
    Dl = np.vstack([joined[k]["delta"].to_numpy() for k in ks])
    pos = joined[1]["position"].to_numpy()
    n_rows, n_pos = X.shape[1], len(np.unique(pos))

    # ---- D1: the five quantities ------------------------------------
    banner("D1 — THE FIVE INPUT QUANTITIES (re-derived from the five "
           "checkpoint CSVs on the base)", "-")
    iu = np.triu_indices(5, 1)
    pair_xx = [float(_spearman(X[i], X[j])) for i, j in zip(*iu)]
    pair_yy = [float(_spearman(Y[i], Y[j])) for i, j in zip(*iu)]
    pair_d = [float(_spearman(Dl[i], Dl[j])) for i, j in zip(*iu)]
    rxx = float(np.median(pair_xx))
    ryy = float(np.median(pair_yy))
    delta_med = float(np.median(pair_d))
    print(f"  accounting: 5 checkpoints x {n_rows} base rows x "
          f"{n_pos} positions (X = wt_logodds, Y = av_logodds, "
          f"delta = Y - X)")
    print(f"  r_XX (WT arms, 10 pairwise Spearman): "
          f"min={min(pair_xx):.6f} median={rxx:.6f} "
          f"max={max(pair_xx):.6f}")
    print(f"    all 10: {[round(v, 6) for v in sorted(pair_xx)]}")
    if round(rxx, 6) != K_RXX_TARGET:
        gfail(f"G2 FAIL: r_XX median {rxx!r} does not reproduce "
              f"{K_RXX_TARGET} (6 dp). Stop.")
    print(f"  G2 PASS: r_XX median == {K_RXX_TARGET} (6 dp) — "
          f"reproduces AC4d/R7's existing 0.8826 figure "
          f"(CALIBRATION_LOG L439; script 97 G4's 0.8826369)")
    print(f"  r_YY (A222V arms, 10 pairwise Spearman — FRESH): "
          f"min={min(pair_yy):.6f} median={ryy:.6f} "
          f"max={max(pair_yy):.6f}")
    print(f"    all 10: {[round(v, 6) for v in sorted(pair_yy)]}")
    rxy_i = [float(_spearman(X[i], Y[i])) for i in range(5)]
    rxy = float(np.median(rxy_i))
    rxy_p_i = [float(np.corrcoef(X[i], Y[i])[0, 1]) for i in range(5)]
    print(f"  r_XY (per-checkpoint within-model Spearman(X,Y), FRESH, "
          f"n={n_rows} each):")
    for i in range(5):
        print(f"    checkpoint {i+1}: spearman={rxy_i[i]!r}  "
              f"pearson={rxy_p_i[i]!r}")
    print(f"    range [{min(rxy_i)!r}, {max(rxy_i)!r}]  "
          f"median={rxy!r}  (formula uses the median)")
    print("    provenance of the previously-cited 0.999636: re-"
          "confirmed as C1d (OVERNIGHT_LOG L455-465) = ESM-2's "
          "Spearman(esm2_score_a222v_bg, esm2_score) n=10,757 — a "
          "different model, NOT one of these five checkpoints; "
          "re-derived here instead of reused, per task D1a.")
    print("  Var(X)/Var(Y) per checkpoint (raw score scale | rank "
          "scale), ddof=0:")
    vx_r, vy_r, vx_w, vy_w = [], [], [], []
    for i in range(5):
        vxi_r = float(np.var(rankdata(X[i]), ddof=0))
        vyi_r = float(np.var(rankdata(Y[i]), ddof=0))
        vxi_w = float(np.var(X[i], ddof=0))
        vyi_w = float(np.var(Y[i], ddof=0))
        vx_r.append(vxi_r); vy_r.append(vyi_r)
        vx_w.append(vxi_w); vy_w.append(vyi_w)
        print(f"    checkpoint {i+1}: raw VarX={vxi_w:.6f} "
              f"VarY={vyi_w:.6f} (d={(vyi_w - vxi_w):+.6f}) | rank "
              f"VarX={vxi_r:.6f} VarY={vyi_r:.6f} "
              f"(d={(vyi_r - vxi_r):+.6f})")
    print(f"    averages: raw VarX={np.mean(vx_w):.6f} "
          f"VarY={np.mean(vy_w):.6f} | rank VarX={np.mean(vx_r):.6f} "
          f"VarY={np.mean(vy_r):.6f}")
    raw_diff_pct = 100 * abs(np.mean(vy_w) - np.mean(vx_w)) / np.mean(vx_w)
    rank_diff_pct = 100 * abs(np.mean(vy_r) - np.mean(vx_r)) / np.mean(vx_r)
    print(f"    Var(X) vs Var(Y) statement: on the RAW scale they "
          f"differ by {raw_diff_pct:.4f}% of mean Var(X); on the RANK "
          f"scale by {rank_diff_pct:.6f}% (ties only — ranks of n "
          f"values without ties have identical variance by "
          f"construction). Var(X) = Var(Y) is NOT assumed anywhere in "
          f"the formula (full expression used, no simplification).")
    # G3: observed delta agreement re-derived
    if round(delta_med, 6) != K_DELT_TARGET:
        gfail(f"G3 FAIL: observed delta-pair median {delta_med!r} does "
              f"not reproduce {K_DELT_TARGET} (6 dp) — the D2d "
              f"comparator has no ground. Stop.")
    print(f"  G3 PASS: observed delta agreement (median of 10 pairwise "
          f"Spearman on delta, same base/convention) == "
          f"{K_DELT_TARGET} (6 dp), full precision {delta_med!r} — "
          f"re-derived live, not taken on faith. Its CI "
          f"[+0.052159, +0.122589] is QUOTED from T5a/T4a "
          f"(DISATTENUATION_LOG L346 / PROJECT_SUMMARY_FINAL L81), "
          f"NOT recomputed here.")

    # ---- G5: D2a identities, both constructions, per checkpoint -----
    banner("G5 / D2a — IDENTITY CHECKS (Var(D) == VarX+VarY-2*r_XY*"
           "sqrt(VarX*VarY)), per checkpoint, both constructions)", "-")
    for i in range(5):
        xr, yr = rankdata(X[i]), rankdata(Y[i])
        vd_r = float(np.var(yr - xr, ddof=0))
        rel_r, rhs_r = identity_rel(vd_r, float(np.var(xr, ddof=0)),
                                    float(np.var(yr, ddof=0)),
                                    float(np.corrcoef(xr, yr)[0, 1]))
        vd_w = float(np.var(Y[i] - X[i], ddof=0))
        rel_w, rhs_w = identity_rel(vd_w, float(np.var(X[i], ddof=0)),
                                    float(np.var(Y[i], ddof=0)),
                                    float(np.corrcoef(X[i], Y[i])[0, 1]))
        if rel_r >= K_IDENTITY_REL_TOL or rel_w >= K_IDENTITY_REL_TOL:
            gfail(f"G5 FAIL: checkpoint {i+1} identity rel-dev "
                  f"R={rel_r:.3e} W={rel_w:.3e} >= "
                  f"{K_IDENTITY_REL_TOL:.0e}. Stop.")
        print(f"  checkpoint {i+1}: R(rank) rel-dev={rel_r:.3e} | "
              f"W(raw) rel-dev={rel_w:.3e}  OK")
    # informational: mixed-scale gap the consistent readings avoid
    print(f"  information: Spearman r_XY median {rxy!r} vs Pearson "
          f"r_XY median {float(np.median(rxy_p_i))!r} — the gap "
          f"{abs(rxy - float(np.median(rxy_p_i))):.3e} is why a mixed "
          f"scale (Spearman r + raw Var) cannot satisfy this identity "
          f"and is not used as a prediction (pre-registered rule).")
    # informational: aggregate-inputs deviation (medians/means).
    # NOTE (disclosed): smoke run 1 printed the FORMULA NUMERATOR here
    # by mistake (label promised the denominator); corrected to the
    # denominator before the full run. Informational only — G5's
    # per-checkpoint identity gates passed before and after; no gate,
    # threshold, or rule changed.
    agg_den = (float(np.mean(vx_r)) + float(np.mean(vy_r))
               - 2.0 * rxy * math.sqrt(float(np.mean(vx_r))
                                       * float(np.mean(vy_r))))
    agg_vd = float(np.mean([np.var(rankdata(Y[i]) - rankdata(X[i]),
                                   ddof=0) for i in range(5)]))
    print(f"  information: aggregate-inputs (median r_XY, mean Var's) "
          f"denominator={agg_den:.6f} vs mean Var(D_rank)="
          f"{agg_vd:.6f} rel-dev="
          f"{abs(agg_den - agg_vd) / max(1.0, agg_vd):.3e} (median-vs-"
          f"per-checkpoint residual; exact identity is the "
          f"per-checkpoint statement above)")
    print("  G5 PASS: D2a identities hold to numerical precision "
          f"(rel < {K_IDENTITY_REL_TOL:.0e}) on BOTH constructions for "
          "all 5 checkpoints — denominator trustworthy.")

    # ---- D2b: point predictions -------------------------------------
    banner("D2b — POINT PREDICTION (formula verbatim, no Vx=Vy "
           "simplification, no clipping)", "-")
    points = {}
    for label, rxx_i, ryy_i, rxy_i_v, vx_i, vy_i in (
            ("R (PRIMARY, rank scale)", rxx, ryy, rxy,
             float(np.mean(vx_r)), float(np.mean(vy_r))),
            ("W (secondary, raw+Pearson)", float(np.median(
                [np.corrcoef(X[a], X[b])[0, 1]
                 for a, b in zip(*iu)])), float(np.median(
                [np.corrcoef(Y[a], Y[b])[0, 1]
                 for a, b in zip(*iu)])), float(np.median(rxy_p_i)),
             float(np.mean(vx_w)), float(np.mean(vy_w)))):
        num, den, pred = lord(rxx_i, ryy_i, rxy_i_v, vx_i, vy_i)
        points[label] = dict(rxx=rxx_i, ryy=ryy_i, rxy=rxy_i_v,
                             vx=vx_i, vy=vy_i, num=num, den=den,
                             pred=pred)
        print(f"  [{label}]")
        print(f"    inputs: r_XX={rxx_i!r} r_YY={ryy_i!r} "
              f"r_XY={rxy_i_v!r} VarX={vx_i!r} VarY={vy_i!r}")
        print(f"    numerator  = {num!r}")
        print(f"    denominator= {den!r}   (== Var(Y-X); "
              f"1 - r_XY = {1 - rxy_i_v:.6e})")
        print(f"    reliability(D) = {pred!r}   -> "
              f"{'IN [0,1]' if 0 <= pred <= 1 else 'OUTSIDE [0,1]'}")
        if not (0 <= pred <= 1):
            print(f"    {DIAGNOSTIC}")
    # descriptive sensitivity: each checkpoint's own r_XY
    print("  descriptive sensitivity (each checkpoint's own r_XY, "
          "median Var's held fixed, construction R):")
    for i in range(5):
        _, _, p_i = lord(rxx, ryy, rxy_i[i],
                         float(np.mean(vx_r)), float(np.mean(vy_r)))
        print(f"    checkpoint {i+1} r_XY={rxy_i[i]!r} -> {p_i!r}")

    # ---- D2c: position-cluster bootstrap ----------------------------
    banner(f"D2c — POSITION-CLUSTER BOOTSTRAP (N_BOOT={N_BOOT}, seed "
           f"{SEED}; ALL FIVE inputs recomputed in every draw)", "-")
    uniq, inverse = np.unique(pos, return_inverse=True)
    groups = [np.flatnonzero(inverse == u) for u in range(len(uniq))]
    nc = len(groups)
    rng = np.random.default_rng(SEED)
    preds_r = np.full(N_BOOT, np.nan)
    preds_w = np.full(N_BOOT, np.nan)
    t_b = time.time()
    for b in range(N_BOOT):
        pick = rng.integers(0, nc, nc)
        idx = np.concatenate([groups[g] for g in pick])
        inp = inputs_on(idx, X, Y)
        _, _, preds_r[b] = lord(inp["rxx"], inp["ryy"], inp["rxy"],
                                inp["vx"], inp["vy"])
        _, _, preds_w[b] = lord(inp["rxx_w"], inp["ryy_w"],
                                inp["rxy_w"], inp["vx_w"], inp["vy_w"])
        if b == 0:
            print(f"    (one draw ≈ {time.time() - t_b:.3f}s; full "
                  f"~{(time.time() - t_b) * N_BOOT:.0f}s)")
    s_r = summarize(preds_r, "R PRIMARY (rank scale)")
    s_w = summarize(preds_w, "W secondary (raw+Pearson)")

    # ---- D2d: prediction vs observation ------------------------------
    banner("D2d — PREDICTION vs OBSERVATION", "-")
    obs, obs_lo, obs_hi = delta_med, 0.052159, 0.122589
    for label, s in (("R PRIMARY", s_r), ("W secondary", s_w)):
        p = points["R (PRIMARY, rank scale)" if label.startswith("R")
                   else "W (secondary, raw+Pearson)"]["pred"]
        in01 = 0 <= p <= 1
        obs_in_ci = s["p2_5"] <= obs <= s["p97_5"]
        print(f"  [{label}] forward prediction = {p!r} "
              f"({'in' if in01 else 'OUTSIDE'} [0,1]); bootstrap "
              f"interval [p2.5={s['p2_5']:.6g}, p97.5={s['p97_5']:.6g}] "
              f"({s['frac_neg'] * 100:.1f}% of draws negative, "
              f"{s['frac_01'] * 100:.1f}% in [0,1])")
        print(f"    observed delta reliability = {obs!r} "
              f"(re-derived, G3) with quoted CI [{obs_lo}, {obs_hi}] "
              f"(T5a/T4a)")
        print(f"    observed value inside the prediction's bootstrap "
              f"interval: {obs_in_ci}")
        verdict = ("CONSISTENT" if (in01 and obs_in_ci)
                   else "INCONSISTENT")
        print(f"    verdict: {verdict} — prediction "
              f"{'inside' if in01 else 'outside'} [0,1], observed "
              f"{'inside' if obs_in_ci else 'outside'} the prediction's "
              f"empirical interval")

    # ---- save tidy CSV ----------------------------------------------
    rows = []
    def add(section, key, value, note=""):
        rows.append(dict(section=section, key=key, value=value,
                         note=note))
    for i in range(5):
        add("d1_checkpoint", f"ck{i+1}_varx_raw", vx_w[i])
        add("d1_checkpoint", f"ck{i+1}_vary_raw", vy_w[i])
        add("d1_checkpoint", f"ck{i+1}_varx_rank", vx_r[i])
        add("d1_checkpoint", f"ck{i+1}_vary_rank", vy_r[i])
        add("d1_checkpoint", f"ck{i+1}_rxy_spearman", rxy_i[i])
        add("d1_checkpoint", f"ck{i+1}_rxy_pearson", rxy_p_i[i])
    add("d1", "r_xx_median", rxx, "G2 gate == 0.882637")
    add("d1", "r_xx_min", min(pair_xx))
    add("d1", "r_xx_max", max(pair_xx))
    add("d1", "r_yy_median", ryy, "fresh")
    add("d1", "r_yy_min", min(pair_yy))
    add("d1", "r_yy_max", max(pair_yy))
    add("d1", "r_xy_median", rxy, "formula input")
    add("d1", "r_xy_min", min(rxy_i))
    add("d1", "r_xy_max", max(rxy_i))
    add("d1", "varx_raw_mean", float(np.mean(vx_w)))
    add("d1", "vary_raw_mean", float(np.mean(vy_w)))
    add("d1", "varx_rank_mean", float(np.mean(vx_r)))
    add("d1", "vary_rank_mean", float(np.mean(vy_r)))
    add("d1", "observed_delta_median", delta_med,
        "G3 gate == 0.084365; CI [+0.052159,+0.122589] quoted T5a/T4a")
    for label, dd in points.items():
        for key in ("rxx", "ryy", "rxy", "vx", "vy", "num", "den",
                    "pred"):
            add("d2b_point", f"{label}::{key}", dd[key])
    for label, s in (("R", s_r), ("W", s_w)):
        for key, v in s.items():
            add("d2c_boot", f"{label}::{key}", v)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\n  saved {len(rows)} rows -> {OUT.name}")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. Classical difference-score reliability assumes uncorrelated
     errors in X and Y; here both arms come from the SAME checkpoint
     on the SAME rows, so checkpoint-specific noise is SHARED between
     arms by construction — r_XY (~0.999+) >> r_XX (~0.88) is the
     signature of that violation and is exactly what can drive the
     numerator negative. Reported as computed, not repaired.
  2. r_XX/r_YY are cross-checkpoint agreement (parallel-forms flavor,
     5 forms) standing in for reliability in Lord's formula.
  3. Two consistent constructions pre-registered and both reported
     (R = rank/mandated-Spearman, primary; W = raw/Pearson,
     secondary); their ratio-form predictions can differ by orders of
     magnitude because the denominator is a near-cancellation. Scale
     sensitivity is part of D2c/D2d's "is one number fair to quote?"
     question, not a discrepancy to hide.
  4. Observed comparator: 0.084365 re-derived live (G3-gated); its CI
     [+0.052159, +0.122589] quoted from T5a/T4a, not recomputed.
  5. Bootstrap = position-cluster re-derivation (654 clusters, seed 0,
     ranks recomputed per draw); extreme/negative predictions counted
     and reported, never winsorized; p-values are not the point of
     D2c — stability of the prediction is.
  6. n = 10,757 / 654 (task32 analysis base); member CSVs carry
     12,446 rows each — {len(d) - len(base)} rows fall outside the
     analysis base and are excluded by the join (accounted in G1).{os.linesep}"""
    )
    print(f"\nSCRIPT 105 DONE  ({time.time() - T0:.1f}s)  "
          f"r_XX={rxx:.6f} | r_YY={ryy:.6f} | r_XY(med)={rxy:.9f} | "
          f"pred_R={points['R (PRIMARY, rank scale)']['pred']!r} | "
          f"observed={delta_med:.6f}")
