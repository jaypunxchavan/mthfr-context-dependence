"""Script 121 (Phase 1b, tasks P2 + P3 + P4) -- same-site vs
same-substitution contrast, similarity-to-valine gradient, and the
non-site placebo descriptive block.  ALL THREE TASKS ARE EXPLORATORY /
POST-HOC: motivated by F1's AE1/AE2 decomposition, which was observed
AFTER F1 was run.  PRE-REGISTERED: this docstring was written before the
first run of this script (PHASE1B_PLACEBO_FOLLOWUP.md, Part A).

NO MODEL SCORING: cached CSVs only; this script never imports torch/esm.

SHARED CONSTRUCTION (replicated line-for-line from scripts/109's AE
frame, whose point rhos were gated against the raw caches by P1/G2 at
max|diff| 9.714e-17):
  task82_ae_raw.csv joined to esm2_wt_scores.csv on (position, mut_aa);
  delta = score_bg - esm2_score; the cache arm 'A222_V' is relabelled
  '__A222V__' and is never a placebo; merged with own_context_metrics on
  hgvs_pro; own_e_b non-null kept; G6 drop of rows whose target position
  equals that background's own position (expected 0 on the AE grid).
  Groups: S = 18 site placebos 'A222_X' (X not in {A, V}); V = 38
  'AV_<pos>' substitution placebos.  A222V enters only for rank
  reporting.  rho_b = Spearman(delta, own_e_b) per background.

PRE-REGISTERED GATES (failure -> `GATE FAIL: ...` + exit 1; no retry,
no threshold change):
  G-121.1 input shapes: task109 CSV 175 rows; AE frame 57 rows;
          S=18, V=38, disjoint, union 56; all 57 backgrounds share the
          IDENTICAL (position, hgvs_pro) row set (paired frame; the
          per-background row count is printed, Phase 1 recorded 1932).
  G-121.2 point-rho identity: the 56 recomputed point rhos match
          task109_placebo_rhos.csv to max|diff| < 1e-9.
  G-121.3 bootstrap identity: one draw using every position cluster
          exactly once reproduces all 56 point rhos to max|diff| <
          1e-12 (checked before any random draw is taken).
  G-121.4 P3 inputs: grantham() importable and all 18 d_b finite.

BOOTSTRAP (position-cluster, project convention): clusters = the 120 AE
positions (sorted); each draw samples 120 positions with replacement
and keeps ALL usable variants of each sampled position with
multiplicity, recomputing rho_b from the resampled rows (mid-rank
handling of duplicated rows is scipy's spearmanr default).  N_BOOT from
env (default 10000), SEED from env (default 0).  PRE-REGISTERED RNG
STREAMS: seed+0 = the single position-cluster draw loop serving BOTH P2
and P3 (P3's rhos are the S-subset of the same draws -- deliberate, one
loop, no re-draw); seed+1 = P2 label permutation; seed+2 = P3 label
permutation; seed+4 = P4 background bootstrap (V group first, then the
W group from the same stream, in that fixed order).  NaN draws (constant
vector in any recomputed rho, or NaN T) are dropped and counted
(n_nan printed; if any are dropped the CI uses the non-NaN draws).
N_PERM from env (default 10000; smoke uses 300), mirroring the N_BOOT
convention.

P2 -- SAME-SITE vs SAME-SUBSTITUTION CONTRAST (EXPLORATORY)
  Statistic: D = mean rho_b(S) - mean rho_b(V) (point rhos).
  Inference:
    (i)  position-cluster bootstrap over the 120 AE positions: each
         draw recomputes all 56 rho_b on the resampled rows, then the
         two group means, then D; 95% percentile CI (2.5, 97.5);
    (ii) label permutation: 10,000 shuffles assigning 18 S-labels to
         the 56 backgrounds (point rhos), two-sided
         p = (1 + #{|D_perm| >= |D_obs|}) / (1 + N_PERM).
  Reported without testing: A222V's rho on this frame and its signed
  rank within S u {A222V} (n=19) and within V u {A222V} (n=39);
  rank 1 = most negative (rank = #{rho < rho_A222V} + 1, scripts/109
  convention).
  DECISION RULE (fixed now): "SITE EFFECT PRESENT" iff the bootstrap CI
  of D excludes 0 (hi < 0 or lo > 0); otherwise "NOT DISTINGUISHABLE".
  Either outcome is logged as exploratory.
  INTERPRETATION GUARD, printed verbatim with the result: "A222V
  shares the site with S and the substitution with V. D < 0 means
  shared site tracks A222V's e.b more than a shared substitution does.
  That is compatible with a real site-specific effect; it is NOT
  evidence of a generic artifact and NOT evidence of A222V-specificity."

P3 -- SIMILARITY-TO-VALINE GRADIENT WITHIN S (EXPLORATORY)
  d_b = Grantham distance between X and V (scripts/lib/features.py,
  gated by P1's Grantham gate; PRIMARY METRIC, fixed now).
  T = Spearman(rho_b, d_b) over the 18.
  PREDICTION (fixed now): more V-like (small d) -> more negative rho_b
  -> T > 0.
  Inference:
    * position-cluster bootstrap, SAME seed+0 draw loop as P2; each
      draw recomputes the 18 rho_b then T; 95% percentile CI;
    * bootstrap SE = ddof=1 std of the T draws; minimum detectable
      |T| = 2.8 x SE, stated because n=18 is small;
    * label permutation: N_PERM shuffles of d_b across the 18 (point
      rhos), two-sided p = (1 + #{|T_perm| >= |T_obs|}) / (1 + N_PERM);
    * leave-one-out range: T recomputed 18 times, each dropping one
      background (point rhos over the remaining 17).
  DECISION RULE (fixed now): SUPPORTED iff CI lower bound > 0 AND
  T > 0 in ALL 18 leave-one-out fits; REVERSED iff CI upper bound < 0;
  otherwise NOT RESOLVED.  NOT RESOLVED must be reported as "n=18
  cannot resolve this," never as "the gradient is flat" -- both strings
  are printed with the verdict so the wording cannot be paraphrased.
  Reported: the 18-row table sorted by d_b (X, d_b, rho_b, bootstrap CI
  from this run, recorded Phase 1 CI from the CSV).
  SECONDARY, DESCRIPTIVE ONLY (no decision rests on them; all reported,
  never selected among): BLOSUM62(V, X) via
  Bio.Align.substitution_matrices -- if the import raises ImportError
  the line prints `BLOSUM62: SKIPPED (ImportError: <verbatim message>)`
  and nothing is installed; and |dKD| with the task's Kyte-Doolittle
  table (A 1.8, R -4.5, N -3.5, D -3.5, C 2.5, Q -3.5, E -3.5, G -0.4,
  H -3.2, I 4.5, L 3.8, K -3.9, M 1.9, F 2.8, P -1.6, S -0.8, T -0.7,
  W -0.9, Y -1.3, V 4.2).  Each secondary gets the same T-style
  Spearman with the same seed+0 draws.  DIRECTION CONVENTION (fixed
  now, printed): Grantham and |dKD| are DISTANCES (gradient predicts
  T > 0); BLOSUM62 is a SIMILARITY (gradient predicts T < 0).

P4 -- NON-SITE PLACEBOS ONLY (DESCRIPTIVE; REPLACES NOTHING)
  Groups: V group = 'AV_*' in the AE frame; W group = the 30 W-series
  backgrounds in the W frame (frame == 'W', bg_id != '__A222V__').
  For each group report exactly what F1 reported: n, mean rho_b and
  background-bootstrap 95% CI (resample the n point rhos with
  replacement, N_BOOT draws, stream seed+4, V then W), median, range,
  A222V's signed rank in group u {A222V} (frame-matched A222V rho:
  AE-frame for V, W-frame for W), and the empirical one-sided
  p_spec = (1 + #{b : rho_b <= rho_A222V}) / (1 + n).
  F1's recorded values (task109_distribution_summary.csv) are printed
  side by side: the W group is F1's W placebos exactly, so n, mean,
  median, range and rank must match F1 bit-for-bit (a mismatch would be
  a bug and is reported plainly); the W CI is a FRESH bootstrap with
  this script's stream and is expected to differ slightly from F1's --
  both are printed.  F1's AE-frame record covers all 56 placebos, not
  the 38 of V; it is printed as context and labelled different-set.
  NO DECISION RULE.  The line printed with the block, verbatim:
  `POST-HOC, DESCRIPTIVE; does not replace F1d; may not be cited as
  support for background-specificity.`

LIMITATIONS (printed with the output, AGENTS 6):
  * Everything in P2/P3/P4 is exploratory and post-hoc-motivated; none
    of it can upgrade or replace F1d, and none of it is confirmatory.
  * own_e_b is the same measured vector for every background, so the 56
    rho_b are mutually correlated (shared y); group means and their
    background-bootstrap CIs describe this set of backgrounds and are
    not iid sampling quantities.  The P2/P3 bootstrap resamples
    POSITIONS and recomputes rhos from raw scores, which propagates
    this shared-y structure correctly; the P4 background bootstrap
    (F1's convention, mandated by the task) does not -- it is
    descriptive, matching F1's reported quantity.
  * A222V's rank and rho are reported, never tested.
  * Cached scores only; no new model runs; no torch/esm import.

Usage (session convention):
  N_BOOT=300  N_PERM=300  venv/bin/python3 scripts/121_ae_placebo_probe.py   # smoke
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/121_ae_placebo_probe.py # full
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

KD = {"A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5,
      "E": -3.5, "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9,
      "M": 1.9, "F": 2.8, "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9,
      "Y": -1.3, "V": 4.2}

t0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


if __name__ == "__main__":
    banner(f"Phase 1b P2+P3+P4 -- cached-data probe (script 121)  "
           f"N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}", "=")

    # ---------------------------------------------------------- build ----
    wt = pd.read_csv(ROOT / "data/processed/esm2_wt_scores.csv")
    ae_raw = pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv")
    own = pd.read_csv(ROOT / "data/processed/own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    rec = pd.read_csv(ROOT / "data/processed/task109_placebo_rhos.csv")

    aej = ae_raw.merge(
        wt[["position", "mut_aa", "hgvs_pro", "esm2_score"]],
        on=["position", "mut_aa"], how="left")
    if aej[["hgvs_pro", "esm2_score"]].isna().any().any():
        gfail("G-121.1 join produced nulls")
    aej["delta"] = aej.score_bg - aej.esm2_score

    parts = []
    for b in sorted(aej.bg_id.unique()):
        if b == "A222_V":
            continue
        sub = aej[aej.bg_id == b][["position", "hgvs_pro", "delta"]].copy()
        sub["bg_id"] = b
        parts.append(sub)
    av = aej[aej.bg_id == "A222_V"][["position", "hgvs_pro", "delta"]].copy()
    av["bg_id"] = "__A222V__"
    parts.append(av)
    lng = pd.concat(parts, ignore_index=True).merge(
        own, on="hgvs_pro", how="left")
    lng = lng[lng.own_e_b.notna()].copy()
    # G6: target position == background position (expected 0 on AE grid)
    dropped = 0
    keep = []
    for b in sorted(lng.bg_id.unique()):
        p = (222 if b.startswith("A222_") else
             int(b.split("_")[1]) if b.startswith("AV_") else None)
        sub = lng[lng.bg_id == b]
        if p is None:
            keep.append(sub)
            continue
        hit = sub.position == p
        dropped += int(hit.sum())
        keep.append(sub[~hit])
    lng = pd.concat(keep, ignore_index=True)

    S_IDS = sorted(b for b in lng.bg_id.unique() if b.startswith("A222_"))
    V_IDS = sorted(b for b in lng.bg_id.unique() if b.startswith("AV_"))
    A222V_ID = "__A222V__"

    print("[G-121.1] input shapes")
    print(f"  task109 CSV rows = {len(rec)} (expect 175); AE frame rows = "
          f"{int((rec.frame == 'AE').sum())} (expect 57)")
    print(f"  S (A222_X, X not in {{A,V}}) = {len(S_IDS)} (expect 18); "
          f"V (AV_*) = {len(V_IDS)} (expect 38); "
          f"disjoint={set(S_IDS).isdisjoint(V_IDS)}; "
          f"union = {len(S_IDS) + len(V_IDS)} (expect 56)")
    print(f"  G6 rows dropped (target pos == bg pos) = {dropped}")
    if len(rec) != 175 or int((rec.frame == "AE").sum()) != 57:
        gfail("G-121.1 task109 shape")
    if len(S_IDS) != 18 or len(V_IDS) != 38:
        gfail(f"G-121.1 group sizes S={len(S_IDS)} V={len(V_IDS)}")
    # paired frame: identical (position, hgvs_pro) sets across backgrounds
    sets = {b: frozenset(zip(g.position, g.hgvs_pro))
            for b, g in lng.groupby("bg_id")}
    n_rows = {b: len(s) for b, s in sets.items()}
    first = next(iter(sets.values()))
    all_same = all(s == first for s in sets.values())
    print(f"  rows per background: min={min(n_rows.values())} "
          f"max={max(n_rows.values())} (Phase 1 recorded 1932); "
          f"identical (position, hgvs_pro) sets across all "
          f"{len(sets)} backgrounds: {all_same}")
    if not all_same:
        gfail("G-121.1 backgrounds do not share identical row sets")
    print("  G-121.1 PASS")

    # point rhos on the shared grid (sorted row order for every bg)
    order = lng.sort_values(["bg_id", "position", "hgvs_pro"]).copy()
    bgs = sorted(order.bg_id.unique())
    rows = {b: order[order.bg_id == b] for b in bgs}
    y = rows[bgs[0]].own_e_b.to_numpy(float)
    X = {b: rows[b].delta.to_numpy(float) for b in bgs}
    pos_codes, uniq = pd.factorize(rows[bgs[0]].position, sort=True)
    k = len(uniq)
    for b in bgs[1:]:
        if not (rows[b].position.to_numpy() == rows[bgs[0]].position.to_numpy()
                ).all():
            gfail(f"G-121.1 row misalignment for {b}")
    point = {b: float(spearmanr(X[b], y).statistic) for b in bgs}

    print("[G-121.2] point rhos vs task109_placebo_rhos.csv")
    rec_ae = rec[rec.frame == "AE"].set_index("bg_id")
    diffs = {b: abs(point[b] - float(rec_ae.loc[b, "rho"])) for b in bgs}
    dmax = max(diffs.values())
    print(f"  max|diff| over {len(diffs)} backgrounds = {dmax:.3e} "
          f"(gate < 1e-9)")
    if dmax >= 1e-9:
        gfail(f"G-121.2 max|diff| = {dmax}")
    print("  G-121.2 PASS")

    # ------------------------------------------------------ bootstrap -----
    clusters = [np.flatnonzero(pos_codes == p) for p in range(k)]
    ident = np.concatenate(clusters)
    if not np.all(np.sort(ident) == np.arange(len(y))):
        gfail("G-121.3 index identity failed")
    id_pts = {b: float(spearmanr(X[b][ident], y[ident]).statistic)
              for b in bgs}
    idmax = max(abs(id_pts[b] - point[b]) for b in bgs)
    print(f"[G-121.3] bootstrap identity: every cluster exactly once -> "
          f"max|diff| vs point rhos = {idmax:.3e} (gate < 1e-12)")
    if idmax >= 1e-12:
        gfail(f"G-121.3 max|diff| = {idmax}")
    print("  G-121.3 PASS")

    rng0 = np.random.default_rng(SEED + 0)   # P2+P3 position-cluster draws
    rho_draws = np.empty((N_BOOT, len(bgs)))
    n_nan = 0
    for i in range(N_BOOT):
        draw = rng0.integers(0, k, k)
        idx = np.concatenate([clusters[d] for d in draw])
        for j, b in enumerate(bgs):
            rho_draws[i, j] = spearmanr(X[b][idx], y[idx]).statistic
        if np.isnan(rho_draws[i]).any():
            n_nan += 1
    print(f"  position-cluster draws: {N_BOOT} x {len(bgs)} rho recomputed "
          f"on resampled rows (stream SEED+0); draws with any NaN = {n_nan}")
    jS = [bgs.index(b) for b in S_IDS]
    jV = [bgs.index(b) for b in V_IDS]

    # --------------------------------------------------------------- P2 ---
    banner("P2 -- SAME-SITE (S, n=18) vs SAME-SUBSTITUTION (V, n=38) "
           "CONTRAST  [EXPLORATORY]", "-")
    rS = np.array([point[b] for b in S_IDS])
    rV = np.array([point[b] for b in V_IDS])
    D_obs = float(rS.mean() - rV.mean())
    print(f"  mean rho_b(S) = {rS.mean():+.9f} (n={len(rS)})")
    print(f"  mean rho_b(V) = {rV.mean():+.9f} (n={len(rV)})")
    print(f"  D = mean(S) - mean(V) = {D_obs:+.9f}")

    d_draws = (rho_draws[:, jS].mean(axis=1)
               - rho_draws[:, jV].mean(axis=1))
    d_valid = d_draws[~np.isnan(d_draws)]
    lo, hi = np.percentile(d_valid, [2.5, 97.5])
    print(f"  bootstrap (position-cluster, {N_BOOT} draws, SEED+0): "
          f"D CI 95% = [{lo:+.9f}, {hi:+.9f}] "
          f"(valid draws {len(d_valid)}/{N_BOOT}, NaN dropped {N_BOOT - len(d_valid)})")
    print(f"  bootstrap sd(D) = {d_valid.std(ddof=1):.9f}")

    rng1 = np.random.default_rng(SEED + 1)
    allrho = np.array([point[b] for b in bgs])
    ge = 0
    for _ in range(N_PERM):
        perm = rng1.permutation(len(bgs))
        lab = np.zeros(len(bgs), dtype=bool)
        lab[perm[:len(S_IDS)]] = True
        dp = float(allrho[lab].mean() - allrho[~lab].mean())
        if abs(dp) >= abs(D_obs):
            ge += 1
    p_perm = (1 + ge) / (1 + N_PERM)
    print(f"  label permutation ({N_PERM} shuffles of S/V labels over the 56, "
          f"two-sided, SEED+1): p = (1 + {ge}) / (1 + {N_PERM}) = {p_perm:.6f}")
    print(f"  label check: each shuffle keeps n(S)=18, n(V)=38 "
          f"(mechanical: lab.sum()==18 by construction)")

    rA = point[A222V_ID]
    rs = np.array([point[b] for b in S_IDS + [A222V_ID]])
    rv = np.array([point[b] for b in V_IDS + [A222V_ID]])
    rank_S = int((rs < rA).sum() + 1)
    rank_V = int((rv < rA).sum() + 1)
    print(f"  A222V rho (AE frame) = {rA:+.9f}; signed rank within "
          f"S u {{A222V}} (n={len(rs)}) = {rank_S}; within "
          f"V u {{A222V}} (n={len(rv)}) = {rank_V} "
          f"(rank 1 = most negative; reported, NOT tested)")

    verdict = ("SITE EFFECT PRESENT" if (hi < 0 or lo > 0)
               else "NOT DISTINGUISHABLE")
    print(f"  P2 RULE (pre-registered): CI excludes 0 -> {verdict}")
    print("  P2 IS EXPLORATORY either way.")
    print('  INTERPRETATION GUARD (verbatim from the task doc): "A222V '
          'shares the site with S and the substitution with V. D < 0 '
          'means shared site tracks A222V\'s e.b more than a shared '
          'substitution does. That is compatible with a real '
          'site-specific effect; it is NOT evidence of a generic '
          'artifact and NOT evidence of A222V-specificity."')

    # --------------------------------------------------------------- P3 ---
    banner("P3 -- SIMILARITY-TO-VALINE GRADIENT WITHIN S  [EXPLORATORY]", "-")
    try:
        from scripts.lib.features import grantham
    except Exception as e:                                    # pragma: no cover
        gfail(f"G-121.4 grantham import failed: {e!r}")
    xs = [b.split("_")[1] for b in S_IDS]
    d_b = np.array([float(grantham(x, "V")) for x in xs])
    if not np.all(np.isfinite(d_b)):
        gfail(f"G-121.4 non-finite d_b: {d_b}")
    print(f"  [G-121.4] grantham import OK; 18 finite d_b "
          f"(range [{d_b.min():.1f}, {d_b.max():.1f}]) -> PASS")
    rS18 = np.array([point[b] for b in S_IDS])
    T_obs = float(spearmanr(rS18, d_b).statistic)
    print(f"  d_b = Grantham(X, V) for X in the 18 A222X (PRIMARY metric, "
          f"fixed in the pre-registration)")
    print(f"  T = Spearman(rho_b, d_b) over the 18 = {T_obs:+.9f} "
          f"(prediction if the anchor tracks A222V-like structure: "
          f"more V-like -> more negative rho_b -> T > 0)")

    rho18 = rho_draws[:, jS]
    T_G = np.array([spearmanr(rho18[i], d_b).statistic
                    for i in range(N_BOOT)])
    T_Gv = T_G[~np.isnan(T_G)]
    g_lo, g_hi = np.percentile(T_Gv, [2.5, 97.5])
    se_G = float(T_Gv.std(ddof=1))
    print(f"  bootstrap T (same SEED+0 draws as P2): 95% CI = "
          f"[{g_lo:+.9f}, {g_hi:+.9f}] (valid {len(T_Gv)}/{N_BOOT}, "
          f"NaN dropped {N_BOOT - len(T_Gv)})")
    print(f"  bootstrap SE(T) = {se_G:.9f} -> minimum detectable |T| "
          f"approx 2.8 x SE = {2.8 * se_G:.9f}  (n=18 is small; stated "
          f"as the task requires)")

    rng2 = np.random.default_rng(SEED + 2)
    ge3 = 0
    for _ in range(N_PERM):
        dp = rng2.permutation(d_b)
        Tp = float(spearmanr(rS18, dp).statistic)
        if abs(Tp) >= abs(T_obs):
            ge3 += 1
    p3 = (1 + ge3) / (1 + N_PERM)
    print(f"  label permutation ({N_PERM} shuffles of d_b across the 18, "
          f"two-sided, SEED+2): p = (1 + {ge3}) / (1 + {N_PERM}) = {p3:.6f}")

    loo = []
    for i in range(18):
        m = np.arange(18) != i
        loo.append((xs[i], float(spearmanr(rS18[m], d_b[m]).statistic)))
    loo_T = np.array([t for _, t in loo])
    print(f"  leave-one-out range of T: [{loo_T.min():+.9f}, "
          f"{loo_T.max():+.9f}] (n=18 fits; T > 0 in "
          f"{int((loo_T > 0).sum())}/18)")
    for x, t in loo:
        print(f"    drop {x}: T = {t:+.9f}")

    csv_ci = rec_ae.loc[S_IDS]
    order_idx = np.argsort(d_b)
    print("  18-row table sorted by d_b (X, d_b, rho_b, this-run bootstrap "
          "CI, Phase 1 recorded CI):")
    for i in order_idx:
        bj = jS[i]
        bd = rho18[:, bj]
        bd = bd[~np.isnan(bd)]
        blo, bhi = np.percentile(bd, [2.5, 97.5])
        row = csv_ci.loc[S_IDS[i]]
        print(f"    X={xs[i]}  d_b={d_b[i]:6.1f}  rho_b={point[S_IDS[i]]:+.9f}  "
              f"CI_this=[{blo:+.6f},{bhi:+.6f}]  "
              f"CI_phase1=[{row.ci_lo:+.6f},{row.ci_hi:+.6f}]")

    if g_lo > 0 and np.all(loo_T > 0):
        p3_verdict = "SUPPORTED"
    elif g_hi < 0:
        p3_verdict = "REVERSED"
    else:
        p3_verdict = "NOT RESOLVED"
    print(f"  P3 RULE (pre-registered): CI lower bound > 0 ({g_lo > 0}) AND "
          f"T > 0 in all 18 LOO ({bool(np.all(loo_T > 0))}); CI upper bound "
          f"< 0 ({g_hi < 0}) -> {p3_verdict}")
    if p3_verdict == "NOT RESOLVED":
        print('  REQUIRED WORDING for NOT RESOLVED: "n=18 cannot resolve '
              'this," never "the gradient is flat".')
    elif p3_verdict == "SUPPORTED":
        print('  SUPPORTED: the within-site gradient is supported on '
              'exploratory data (still post-hoc; Phase 2 restates it '
              'pre-registered).')
    else:
        print(f'  REVERSED: T CI excludes 0 on the negative side.')

    # secondary, descriptive only
    print("  SECONDARY (descriptive only; no decision rests on these; all "
          "reported, never selected among):")
    try:
        from Bio.Align import substitution_matrices
        m62 = substitution_matrices.load("BLOSUM62")
        d_bl = np.array([float(m62["V", x]) for x in xs])
        T_B = np.array([spearmanr(rho18[i], d_bl).statistic
                        for i in range(N_BOOT)])
        Tb_v = T_B[~np.isnan(T_B)]
        blo, bhi = np.percentile(Tb_v, [2.5, 97.5])
        T_B_obs = float(spearmanr(rS18, d_bl).statistic)
        print(f"    BLOSUM62(V, X): SIMILARITY metric (gradient predicts "
              f"T < 0); T = {T_B_obs:+.9f}, bootstrap CI "
              f"[{blo:+.9f}, {bhi:+.9f}]")
    except ImportError as e:
        print(f"    BLOSUM62: SKIPPED (ImportError: {e}) -- nothing "
              f"installed (task rule)")
    d_kd = np.array([abs(KD["V"] - KD[x]) for x in xs])
    T_K = np.array([spearmanr(rho18[i], d_kd).statistic
                    for i in range(N_BOOT)])
    Tk_v = T_K[~np.isnan(T_K)]
    klo, khi = np.percentile(Tk_v, [2.5, 97.5])
    T_K_obs = float(spearmanr(rS18, d_kd).statistic)
    print(f"    |dKD| (Kyte-Doolittle): DISTANCE metric (gradient predicts "
          f"T > 0); T = {T_K_obs:+.9f}, bootstrap CI "
          f"[{klo:+.9f}, {khi:+.9f}]")

    # --------------------------------------------------------------- P4 ---
    banner("P4 -- NON-SITE PLACEBOS ONLY  [POST-HOC, DESCRIPTIVE]", "-")
    summ = pd.read_csv(ROOT / "data/processed/task109_distribution_summary.csv")
    w_rec = summ[summ.frame == "W"].iloc[0]
    rng4 = np.random.default_rng(SEED + 4)

    def p4_block(label, r, a222v_rho):
        n = len(r)
        boots = np.empty(N_BOOT)
        for i in range(N_BOOT):
            boots[i] = rng4.choice(r, size=n, replace=True).mean()
        blo, bhi = np.percentile(boots, [2.5, 97.5])
        n_le = int((r <= a222v_rho).sum())
        p_spec = (1 + n_le) / (1 + n)
        rank = int((r < a222v_rho).sum() + 1)
        print(f"  [{label}] n={n} mean={r.mean():+.9f} "
              f"background-bootstrap 95% CI=[{blo:+.9f},{bhi:+.9f}] "
              f"(N_BOOT={N_BOOT}, stream SEED+4) median={np.median(r):+.9f} "
              f"range=[{r.min():+.9f},{r.max():+.9f}]")
        print(f"    A222V rho (frame-matched) = {a222v_rho:+.9f}; signed "
              f"rank in group u {{A222V}} = {rank}/{n + 1} (rank 1 = most "
              f"negative); #{{b : rho_b <= rho_A222V}} = {n_le}; "
              f"p_spec = (1 + {n_le}) / (1 + {n}) = {p_spec:.9f}")
        return dict(n=n, mean=float(r.mean()), med=float(np.median(r)),
                    mn=float(r.min()), mx=float(r.max()), rank=rank,
                    blo=blo, bhi=bhi)

    r_v = np.array([point[b] for b in sorted(V_IDS)])
    res_v = p4_block("V (AE2, AE frame)", r_v, point[A222V_ID])
    w_df = rec[(rec.frame == "W") & (~rec.is_a222v)].sort_values("bg_id")
    r_w = w_df.rho.to_numpy(float)
    w_rho = float(rec[(rec.frame == "W") & rec.is_a222v].rho.iloc[0])
    res_w = p4_block("W (W frame)", r_w, w_rho)

    print("  F1 recorded (task109_distribution_summary.csv) side by side:")
    print(f"    [W] F1: n={int(w_rec.n_placebos)} mean={w_rec['mean']:+.9f} "
          f"median={w_rec['median']:+.9f} range=[{w_rec['min']:+.9f},"
          f"{w_rec['max']:+.9f}] rank_signed={int(w_rec.rank_signed)} "
          f"mean CI=[{w_rec.mean_ci_lo:+.9f},{w_rec.mean_ci_hi:+.9f}]")
    det_match = (res_w["n"] == int(w_rec.n_placebos)
                 and abs(res_w["mean"] - float(w_rec["mean"])) < 1e-15
                 and abs(res_w["med"] - float(w_rec["median"])) < 1e-15
                 and abs(res_w["mn"] - float(w_rec["min"])) < 1e-15
                 and abs(res_w["mx"] - float(w_rec["max"])) < 1e-15
                 and res_w["rank"] == int(w_rec.rank_signed))
    print(f"    [W] deterministic quantities identical to F1 "
          f"(n/mean/median/range/rank): {det_match} "
          f"(must be True; a False would be a bug -- reported plainly)")
    print(f"    [W] CI comparison: this run [{res_w['blo']:+.9f},"
          f"{res_w['bhi']:+.9f}] vs F1 [{w_rec.mean_ci_lo:+.9f},"
          f"{w_rec.mean_ci_hi:+.9f}] -- fresh bootstrap stream, small "
          f"differences expected")
    ae_rec = summ[summ.frame == "AE"].iloc[0]
    print(f"    [AE-frame F1 record = ALL 56 placebos, a DIFFERENT set "
          f"than V's 38, context only]: n={int(ae_rec.n_placebos)} "
          f"mean={ae_rec['mean']:+.9f} mean CI=[{ae_rec.mean_ci_lo:+.9f},"
          f"{ae_rec.mean_ci_hi:+.9f}]")
    print("  POST-HOC, DESCRIPTIVE; does not replace F1d; may not be cited "
          "as support for background-specificity.")
    print("  No decision rule for P4 (none pre-registered; none applied).")

    # -------------------------------------------------------- wrap-up -----
    banner("SCRIPT 121 SUMMARY", "-")
    print(f"  P2: D = {D_obs:+.9f}, CI [{lo:+.9f}, {hi:+.9f}], "
          f"perm p = {p_perm:.6f} -> {verdict} (EXPLORATORY)")
    print(f"  P3: T = {T_obs:+.9f}, CI [{g_lo:+.9f}, {g_hi:+.9f}], "
          f"perm p = {p3:.6f}, LOO range [{loo_T.min():+.9f}, "
          f"{loo_T.max():+.9f}] -> {p3_verdict} (EXPLORATORY)")
    print(f"  P4: V n={res_v['n']} mean={res_v['mean']:+.9f}; "
          f"W n={res_w['n']} mean={res_w['mean']:+.9f} "
          f"(POST-HOC, DESCRIPTIVE)")
    print("\nLIMITATIONS (AGENTS 6):")
    print("  * all of P2/P3/P4 is post-hoc-motivated and EXPLORATORY; it")
    print("    cannot upgrade or replace F1d and is not confirmatory.")
    print("  * shared y (own_e_b) across backgrounds: group-mean background")
    print("    bootstraps describe this set of backgrounds (not iid);")
    print("    P2/P3 position-cluster draws recompute rhos from raw scores.")
    print("  * cached scores only; no model scoring; no torch/esm import.")
    print(f"Elapsed {time.time() - t0:.1f}s")
