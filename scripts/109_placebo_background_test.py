"""
Script 109 (task F1) -- placebo-background test: do the cached background
substitutions' shift statistics correlate with A222V's own measured
own_e.b?  PRE-REGISTERED: this docstring was written before any run of
this script; no correlation statistic below had been computed when the
rules here were fixed (only F1a cache-coverage plumbing was inspected,
as the task requires).

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group F, task F1 (F1a-F1e).
      Group F is the single most decisive item in this session.

CACHE INVENTORY (measured from the real files BEFORE this docstring was
written -- F1a; the task doc's "~87 backgrounds on a common ~120-position
subset" is verified, and is only half right):
  * data/processed/task82_ae_raw.csv   : 129,960 rows = 57 backgrounds x
    120 positions x 19 substitutions (AE1: 19 A>X at position 222, AE2:
    38 A>V at other Ala positions).  No hgvs_pro column -> joined to
    data/processed/esm2_wt_scores.csv on (position, mut_aa): 0 nulls.
  * data/processed/task69_w2_bg_raw.csv : 68,400 rows = 30 decile-stratified
    backgrounds x 120 positions x 19 substitutions (W-series, script 69),
    hgvs_pro present.
  * backgrounds total = 57 + 30 = 87 -> the doc's "roughly 87" is exact.
  * POSITION OVERLAP between the two caches = 41 positions ONLY.  W's 120
    == M1's subset (script 63) exactly; AE drew its own 120.  => there is
    NO single common ~120-position frame across all 87 backgrounds; the
    doc's "common subset" premise is wrong on this point.  Three frames
    are therefore analysed (below).
  * A222V is bg_id A222_V in the AE cache (1 of the 57).  The M1 cache's
    8 backgrounds (script 63) exist but are NOT among the two sources the
    task names (57+30=87 matches) -- not used; disclosed.

FRAMES (pre-registered):
  * AE   : 56 non-A222V AE backgrounds on AE's 120 positions.  A222V
           reference = the cache's own A222_V arm, SAME rows.
  * W    : 30 W backgrounds on W's 120 positions.  A222V reference =
           atlas delta (merged_wt_a222v_scores.csv) on the SAME rows.
  * COMMON (sensitivity): all 86 placebos + A222V on the 41 positions
           both caches share -- identical rows for every background.
  Within a frame the usable (position, mut_aa) grid is a property of the
  variant alone (own_e_b coverage), so every background's rho -- placebo
  AND A222V -- is computed on identical rows: the comparison is exactly
  paired.

STATISTIC (F1b): for each background b, on its frame,
    delta_b(v) = S(v|b) - S(v|WT) = score_bg - esm2_score (same hgvs_pro)
    rho_b      = Spearman(delta_b, own_e_b) over rows with both non-null.
  A222V's reference uses the identical construction on the same rows.
  delta source: score_bg column of the cache; WT = esm2_score of
  data/processed/esm2_wt_scores.csv.

BOOTSTRAP (position-cluster, the project convention): resample the frame's
K usable positions with replacement, keep ALL usable variants of each
sampled position with multiplicity, recompute Spearman; percentile 95% CI.
N_BOOT from env (default 10000), SEED from env (default 0).  rng streams:
seed+0 = A222V reference CIs, seed+1 = placebo CIs, seed+2 = the
across-background mean CI.  Order: frames AE, W, COMMON; backgrounds in
sorted bg_id order -> bit-reproducible.  NaN draws (constant vector) are
counted and dropped (n_nan reported).
IDENTITY CHECK: concatenating every position cluster exactly once must
reproduce the point estimate to <1e-12 (max|diff|); failure -> exit 1.

DECISION RULE (F1d -- fixed here before running; applied per frame):
  Let P   = the placebo signed rhos on the frame (primary frames) or
            |rho| where stated, R = A222V's signed rho on the SAME rows,
            C = 95% background-level bootstrap CI (10000 draws, rng
            stream seed+2) for mean(P).
  Branch 1 ("strong support that the anchor is background-specific")
      iff C contains 0 AND |R| > max_{b in P} |rho_b|.
  Branch 2 ("placebos match A222V's magnitude")
      iff NOT Branch 1 AND |R| <= max|rho_b| AND median|rho_b| >= 0.5*|R|.
  Branch 3 ("dispersed, A222V inside but not extreme -> inconclusive")
      otherwise.
  The 0.5 factor is a pre-registered judgment constant, not tuned to any
  result.  Branches are decided per frame; if the two primary frames
  disagree, BOTH are reported as-is -- no averaging, no rounding toward
  either pole.  If a frame's outcome falls in a gap of the task's own
  three-branch wording (e.g. A222V beyond every placebo but the center CI
  excludes 0), the numbers are reported plainly and the straddle is
  disclosed rather than forced into a branch.
  ALSO reported (descriptive, not part of the rule): A222V's rank and
  percentile among placebos on signed rho and on |rho|; how many placebos'
  own CIs exclude 0; mean/median/sd/q25/q75/min/max of P; mean|delta|
  per background as scale context; and the canonical full-frame anchor
  -0.08811806424891734 as CONTEXT ONLY (10,757 rows / 654 positions --
  its spread is not comparable to a 120- or 41-position subset).

GATES (failure -> print the exact mismatch, exit 1; no retries, no
threshold changes):
  G1  cache shapes: AE 129,960 rows/57 bg/120 pos, W 68,400/30/120,
      AE∩W = 41 positions.
  G2  AE cache A222_V arm delta vs atlas delta_esm: max|diff| < 1e-9.
  G3  atlas delta_esm == esm2_score_a222v_bg - esm2_score: max|diff| < 1e-9.
  G4  coverage floor per background (own_e_b usable rows / positions).
      Floors: primary frames >= 1500 usable variants and >= 100 usable
      positions per background; COMMON >= 500 variants and >= 35
      positions.  (Floors set AFTER F1a coverage inspection -- ~1932 and
      ~1971 usable variants per background observed -- and BEFORE any rho
      was computed; disclosed as such.)  If a floor fails: STOP, print
      the real coverage (F1e), exit 1 -- do not stretch a thin result.
  G5  bootstrap identity check (above).
  G6  rows whose target position == that background's own position
      (delta there is a double-mutant effect, not a context shift): those
      rows are dropped for that background only, count disclosed; if any
      occur, per-background row counts are printed.

LIMITATIONS (printed with the output, AGENTS 6):
  * Cached data only; no new model runs (F1e).
  * Placebos differ from A222V in background identity and (for W) in
    background severity.  A null result here rules out "ANY cached
    background reproduces A222V's correlation"; it cannot exclude a
    severity-matched confound -- that test is not available on cache.
  * own_e_b is the SAME measured vector for every background, so the 86
    placebo rhos are mutually correlated (shared y).  The across-background
    sd and the background-bootstrap mean CI are descriptive of this set of
    backgrounds; they are not iid sampling quantities.
  * A222V's reference rows here are subsets of the full-frame anchor's
    rows; -0.0881 is context, not the same estimator on the same data.

Usage:
  N_BOOT=300   venv/bin/python3 scripts/109_placebo_background_test.py   # smoke
  N_BOOT=10000 venv/bin/python3 scripts/109_placebo_background_test.py   # full
"""

import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
OUTDIR = "data/processed"
CANONICAL_ANCHOR = -0.08811806424891734  # full-frame context value

FLOOR = {  # G4, pre-registered (see docstring)
    "AE": (1500, 100),
    "W": (1500, 100),
    "COMMON": (500, 35),
}

t0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


# ---------------------------------------------------------------- load ----
wt = pd.read_csv("data/processed/esm2_wt_scores.csv")
ae = pd.read_csv("data/processed/task82_ae_raw.csv")
w = pd.read_csv("data/processed/task69_w2_bg_raw.csv")
mg = pd.read_csv("data/processed/merged_wt_a222v_scores.csv")
own = pd.read_csv("data/processed/own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]

print("=" * 78)
print("Script 109 -- F1 placebo-background test "
      f"(N_BOOT={N_BOOT}, SEED={SEED})")
print("=" * 78)

# ------------------------------------------------------------- G1: shape ---
pos_ae, pos_w = set(ae.position.unique()), set(w.position.unique())
inter = pos_ae & pos_w
print("\n[F1a] CACHE COVERAGE (measured from the files):")
print(f"  task82_ae_raw.csv   : {len(ae)} rows, {ae.bg_id.nunique()} backgrounds, "
      f"{len(pos_ae)} positions")
print(f"  task69_w2_bg_raw.csv: {len(w)} rows, {w.bg_id.nunique()} backgrounds, "
      f"{len(pos_w)} positions")
print(f"  backgrounds total   : {ae.bg_id.nunique() + w.bg_id.nunique()} "
      "(task doc said '~roughly 87')")
print(f"  position overlap AE n W = {len(inter)} "
      "(task doc assumed a common ~120 -- NOT the case)")
if not (len(ae) == 129960 and ae.bg_id.nunique() == 57 and len(pos_ae) == 120):
    gfail(f"G1 AE shape: rows={len(ae)} bg={ae.bg_id.nunique()} pos={len(pos_ae)}")
if not (len(w) == 68400 and w.bg_id.nunique() == 30 and len(pos_w) == 120):
    gfail(f"G1 W shape: rows={len(w)} bg={w.bg_id.nunique()} pos={len(pos_w)}")
if len(inter) != 41:
    gfail(f"G1 position overlap = {len(inter)}, expected 41")
print("  G1 PASS")

# ------------------------------------------------- join keys + WT scores ---
aej = ae.merge(wt[["position", "mut_aa", "hgvs_pro", "esm2_score"]],
               on=["position", "mut_aa"], how="left")
if aej.hgvs_pro.isna().any() or aej.esm2_score.isna().any():
    gfail(f"G1b AE join nulls: hgvs={aej.hgvs_pro.isna().sum()} "
          f"score={aej.esm2_score.isna().sum()}")
aej["delta"] = aej["score_bg"] - aej["esm2_score"]
wj = w.merge(wt[["hgvs_pro", "esm2_score"]], on="hgvs_pro", how="left")
if wj.esm2_score.isna().any():
    gfail(f"G1b W WT-score nulls = {wj.esm2_score.isna().sum()}")
wj["delta"] = wj["score_bg"] - wj["esm2_score"]

# -------------------------------------------- G2/G3: A222V cross-provenance -
av = aej[aej.bg_id == "A222_V"]
mg_check = mg.dropna(subset=["delta_esm", "esm2_score_a222v_bg"]).copy()
mg_check["calc"] = mg_check["esm2_score_a222v_bg"] - mg_check["esm2_score"]
d3 = float(np.max(np.abs(mg_check["delta_esm"] - mg_check["calc"])))
mm = av.merge(mg[["hgvs_pro", "delta_esm"]], on="hgvs_pro", how="left")
d2 = float(np.max(np.abs(mm["delta"] - mm["delta_esm"])))
print(f"\n[G2] AE-cache A222_V arm vs atlas delta_esm: max|diff| = {d2:.3e} "
      f"on {mm['delta_esm'].notna().sum()} rows")
print(f"[G3] atlas delta_esm vs esm2_score_a222v_bg - esm2_score: "
      f"max|diff| = {d3:.3e}")
if d2 >= 1e-9:
    gfail(f"G2 max|diff| = {d2}")
if d3 >= 1e-9:
    gfail(f"G3 max|diff| = {d3}")
print("  G2, G3 PASS")

# --------------------------------------------------------------- frames -----
a222v_cache = av[["hgvs_pro", "position", "delta"]].copy()      # AE reference
atlas = mg[["hgvs_pro", "position_a222v_bg", "delta_esm"]].rename(
    columns={"position_a222v_bg": "position", "delta_esm": "delta"})[
    ["hgvs_pro", "position", "delta"]]


def build_frame(name, placebos_df, a222v_df, positions):
    """Return one tidy long frame: bg_id, position, hgvs_pro, delta, own_e_b.

    A222V appears as bg_id '__A222V__' so it flows through the identical
    code path as every placebo.
    """
    parts = []
    for b in sorted(placebos_df.bg_id.unique()):
        if b == "A222_V":
            # F1b: A222V itself is NEVER a placebo; it enters only as the
            # __A222V__ reference below (same cache arm, same rows).
            continue
        sub = placebos_df[placebos_df.bg_id == b].copy()
        sub = sub[sub.position.isin(positions)]
        sub["bg_id"] = b
        parts.append(sub[["bg_id", "position", "hgvs_pro", "delta"]])
    a = a222v_df[a222v_df.position.isin(positions)].copy()
    a["bg_id"] = "__A222V__"
    parts.append(a[["bg_id", "position", "hgvs_pro", "delta"]])
    long = pd.concat(parts, ignore_index=True).merge(own, on="hgvs_pro", how="left")
    long = long[long.own_e_b.notna()].copy()
    # G6: drop rows where target position == that background's own position
    bgpos = {}
    for b in sorted(placebos_df.bg_id.unique()):
        m = b.split("_")[-1]
        # AE backgrounds: A222_X (pos 222) or AV_<pos>; W: e.g. D1A_V179W (pos 179)
        if b.startswith("A222_"):
            bgpos[b] = 222
        elif b.startswith("AV_"):
            bgpos[b] = int(b.split("_")[1])
        else:
            digits = "".join(ch for ch in m if ch.isdigit())
            bgpos[b] = int(digits)
    dropped = 0
    keep = []
    for b in sorted(long.bg_id.unique()):
        if b == "__A222V__":
            keep.append(long[long.bg_id == b])
            continue
        p = bgpos[b]
        mask = long.bg_id == b
        hit = mask & (long.position == p)
        n = int(hit.sum())
        if n:
            dropped += n
            print(f"  [G6] {name}: {b} target-position==bg-position {p}: "
                  f"dropped {n} rows")
        keep.append(long[~hit & mask])
    long = pd.concat(keep, ignore_index=True)
    print(f"  [{name}] usable rows total = {len(long)}, "
          f"backgrounds = {long.bg_id.nunique()}, G6 dropped = {dropped}")
    return long


print("\n[frames]")
ae_long = build_frame("AE", aej, a222v_cache, pos_ae)
w_long = build_frame("W", wj, atlas, pos_w)
common_long = build_frame("COMMON", pd.concat([aej, wj], ignore_index=True),
                          a222v_cache, inter)

# ------------------------------------------------------ G4 coverage floor ---
for nm, lng in [("AE", ae_long), ("W", w_long), ("COMMON", common_long)]:
    g = lng.groupby("bg_id")
    rows_per = g.size()
    pos_per = g.position.nunique()
    f_rows, f_pos = FLOOR[nm]
    print(f"  [{nm}] usable variants per background: min={rows_per.min()} "
          f"max={rows_per.max()} | positions: min={pos_per.min()} "
          f"max={pos_per.max()}")
    if rows_per.min() < f_rows or pos_per.min() < f_pos:
        gfail(f"G4 {nm}: min rows={rows_per.min()} (floor {f_rows}), "
              f"min positions={pos_per.min()} (floor {f_pos}) -- real "
              "coverage too thin; report as F1e rather than stretch")
print("  G4 PASS")


# ------------------------------------------------------------ bootstrap -----
def rho_of(idx, x, y):
    r = spearmanr(x[idx], y[idx]).statistic
    return r


def cluster_boot(x, y, pos_codes, k, n_boot, rng):
    """Position-cluster bootstrap: resample k position clusters with
    replacement, keep all variants of each sampled cluster."""
    clusters = [np.flatnonzero(pos_codes == p) for p in range(k)]
    # G5 identity: every cluster exactly once, in order -> point estimate
    ident = np.concatenate(clusters)
    assert np.all(np.sort(ident) == np.arange(len(x))), "G5 index identity"
    out = np.empty(n_boot)
    n_nan = 0
    for i in range(n_boot):
        draw = rng.integers(0, k, k)
        idx = np.concatenate([clusters[d] for d in draw])
        v = rho_of(idx, x, y)
        if np.isnan(v):
            n_nan += 1
        out[i] = v
    return out, n_nan, rho_of(np.arange(len(x)), x, y)


def run_cell(lng, bg, n_boot, rng):
    sub = lng[lng.bg_id == bg]
    x = sub.delta.to_numpy(float)
    y = sub.own_e_b.to_numpy(float)
    pos_codes, uniq = pd.factorize(sub.position, sort=True)
    k = len(uniq)
    draws, n_nan, rho = cluster_boot(x, y, pos_codes, k, n_boot, rng)
    lo, hi = np.nanpercentile(draws, [2.5, 97.5])
    return dict(rho=rho, ci_lo=lo, ci_hi=hi, n_rows=len(sub), n_clusters=k,
                n_nan=n_nan, mean_abs_delta=float(np.mean(np.abs(x))))


rng_a = np.random.default_rng(SEED + 0)   # A222V references
rng_p = np.random.default_rng(SEED + 1)   # placebo CIs
rng_m = np.random.default_rng(SEED + 2)   # across-background mean CI

results = []
summary = []
branch_by_frame = {}

for nm, lng in [("AE", ae_long), ("W", w_long), ("COMMON", common_long)]:
    print(f"\n[run] frame {nm}: {lng.bg_id.nunique()} backgrounds, "
          f"{N_BOOT} bootstrap draws each ...")
    bgs = sorted(lng.bg_id.unique())
    for b in bgs:
        is_a = b == "__A222V__"
        cell = run_cell(lng, b, N_BOOT, rng_a if is_a else rng_p)
        cell.update(frame=nm, bg_id=b, is_a222v=is_a)
        results.append(cell)
        tag = "A222V" if is_a else b
        print(f"    {tag:12s} rho={cell['rho']:+.6f} "
              f"CI[{cell['ci_lo']:+.6f},{cell['ci_hi']:+.6f}] "
              f"n={cell['n_rows']} k={cell['n_clusters']} "
              f"nan={cell['n_nan']} mean|d|={cell['mean_abs_delta']:.4f}")

    df = pd.DataFrame([r for r in results if r["frame"] == nm])
    pl = df[~df.is_a222v]
    a = df[df.is_a222v].iloc[0]
    P = pl.rho.to_numpy()
    R = float(a.rho)
    # across-background mean CI (background-level resample, rng stream +2)
    boots = np.empty(2000 if N_BOOT < 1000 else 10000)
    for i in range(len(boots)):
        boots[i] = rng_m.choice(P, size=len(P), replace=True).mean()
    mlo, mhi = np.percentile(boots, [2.5, 97.5])
    n_excl = int(((pl.ci_lo > 0) | (pl.ci_hi < 0)).sum())
    absP, absR = np.abs(P), abs(R)
    rank_signed = int((P < R).sum() + 1)          # 1 = more negative than all
    rank_abs = int((absP > absR).sum() + 1)       # 1 = largest magnitude
    pct_abs = float((absP <= absR).mean() * 100.0)
    # F1d pre-registered branches
    center0 = (mlo <= 0.0 <= mhi)
    if center0 and absR > absP.max():
        branch = 1
    elif absR <= absP.max() and np.median(absP) >= 0.5 * absR:
        branch = 2
    else:
        branch = 3
    branch_by_frame[nm] = branch
    summary.append(dict(
        frame=nm, n_placebos=len(P), mean=P.mean(), sd=P.std(ddof=1),
        median=np.median(P), q25=np.percentile(P, 25),
        q75=np.percentile(P, 75), min=P.min(), max=P.max(),
        mean_ci_lo=mlo, mean_ci_hi=mhi, center_contains_0=bool(center0),
        a222v_rho=R, a222v_ci_lo=a.ci_lo, a222v_ci_hi=a.ci_hi,
        rank_signed=rank_signed, rank_abs=rank_abs, pct_abs=pct_abs,
        n_placebo_ci_excl_0=n_excl, median_abs_P=float(np.median(absP)),
        max_abs_P=float(absP.max()), branch=branch,
        full_frame_anchor=CANONICAL_ANCHOR))
    print(f"  [{nm}] placebos n={len(P)} mean={P.mean():+.6f} "
          f"sd={P.std(ddof=1):.6f} median={np.median(P):+.6f} "
          f"range[{P.min():+.6f},{P.max():+.6f}]")
    print(f"  [{nm}] mean CI (background bootstrap) = [{mlo:+.6f},{mhi:+.6f}] "
          f"contains 0: {center0}")
    print(f"  [{nm}] A222V rho={R:+.6f} CI[{a.ci_lo:+.6f},{a.ci_hi:+.6f}] "
          f"| rank signed={rank_signed}/{len(P)+1} rank|rho|={rank_abs}/"
          f"{len(P)+1} percentile|rho|={pct_abs:.1f}")
    print(f"  [{nm}] placebos with own CI excluding 0: {n_excl}/{len(P)} "
          f"| median|rho_b|={np.median(absP):.6f} max|rho_b|={absP.max():.6f}")
    print(f"  [{nm}] >> F1d pre-registered branch = {branch} "
          f"({ {1: 'strong support', 2: 'matches magnitude', 3: 'inconclusive'}[branch] })")

res = pd.DataFrame(results)
summ = pd.DataFrame(summary)
res.to_csv(f"{OUTDIR}/task109_placebo_rhos.csv", index=False)
summ.to_csv(f"{OUTDIR}/task109_distribution_summary.csv", index=False)

# ------------------------------------------------------------- F1d verdict --
print("\n" + "=" * 78)
print("F1d VERDICT (pre-registered rule, per frame)")
print("=" * 78)
for s in summ.itertuples():
    print(f"  {s.frame:7s} -> branch {s.branch} "
          f"| placebos mean {s.mean:+.6f} CI[{s.mean_ci_lo:+.6f},"
          f"{s.mean_ci_hi:+.6f}] | A222V {s.a222v_rho:+.6f} "
          f"CI[{s.a222v_ci_lo:+.6f},{s.a222v_ci_hi:+.6f}] "
          f"| rank|r| {s.rank_abs}/{s.n_placebos + 1}")
if branch_by_frame.get("AE") == branch_by_frame.get("W"):
    print(f"  PRIMARY FRAMES AGREE: branch {branch_by_frame['AE']}")
else:
    print(f"  PRIMARY FRAMES DISAGREE: AE=branch {branch_by_frame['AE']}, "
          f"W=branch {branch_by_frame['W']} -- reported as-is, not averaged")
print(f"  CONTEXT (different frame, not comparable spread): full-frame "
      f"anchor rho = {CANONICAL_ANCHOR}")

print("\nLIMITATIONS (AGENTS 6):")
print("  * cached scores only; no new model runs.")
print("  * placebos are not severity-matched to A222V (W backgrounds are "
      "decile-stratified, AE are position/identity cells); a null here "
      "rules out 'any cached background' but not a severity-matched confound.")
print("  * own_e_b is the same measured y for all backgrounds -> placebo "
      "rhos are mutually correlated; sd and mean-CI describe this set of "
      "backgrounds, they are not iid sampling quantities.")
print("  * per-frame A222V reference rows are a subset of the full-frame "
      "anchor's rows; -0.088118 is context only.")
print(f"\nWrote {OUTDIR}/task109_placebo_rhos.csv ({len(res)} rows), "
      f"{OUTDIR}/task109_distribution_summary.csv ({len(summ)} rows)")
print(f"Elapsed {time.time() - t0:.1f}s")
