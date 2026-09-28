"""
Script 113 (task E1, Group E) -- fix the 150M/650M frame mismatch
(review 1.5): recompute the five ESM-1v checkpoints' pairwise agreement
ON THE MATCHED 100-POSITION SUBSET used by the pre-registered
150M-vs-650M comparison, and report all three readings side by side.

PRE-REGISTERED: this docstring was written before the first run; every
frame, statistic, gate, threshold, and reporting rule below was fixed
before any number produced here was seen (AGENTS sec 6).

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group E, task E1 (E1a-E1c).

E1a -- THE EXACT 100-POSITION SUBSET (identified, not assumed):
  the unique positions in data/processed/task58_150m_check.csv, the
  output of script 58's pre-registered J2a-3 run (N_POS=100, seed 0,
  sampled from the primary-maps atlas position set -- script 58
  L207-210).  The CSV is the authority (it is the set actually
  scored), not a re-derivation of the sampling.

E1a -- AGREEMENT STATISTIC (exactly script 86 R7 / script 98 T5a's
  procedure, quoted from the record): join the five members'
  task_AC4_esm1v_member{k}_scores.csv onto script 32's analysis base
  (task32 dropna(own_e_b, GI_folinate_independent, delta_esm) =
  10,757 rows / 654 positions -- gated), compute all 10 pairwise
  Spearmans per column set, take the MEDIAN of the 10.  Two column
  sets: RAW wt_logodds (WT-background raw scores) and DELTA =
  av_logodds - wt_logodds.  Computed twice: on the FULL 654-position
  frame (record reproduction) and on the matched 100-position subset
  (the new quantity E1 asks for).

  CI convention (script 98's, as described in DISATTENUATION_LOG T3a/
  T5a): position-cluster bootstrap -- resample the frame's positions
  with replacement, recompute all 10 pair Spearmans and their median
  fresh inside every draw, percentile 2.5/97.5, seed 0, N_BOOT from
  environment (default 10000; smoke at 300).

E1b -- SIDE BY SIDE, all three together:
  1. ESM-1v agreement, full 654-position frame (raw + delta)
  2. ESM-1v agreement, matched 100-position subset (raw + delta)
  3. The 150M/650M comparison's own values, recomputed from the same
     task58 CSV: PRIMARY Spearman(delta_150M, delta_650M) with
     position-cluster bootstrap (script 58's own
     position_cluster_bootstrap call), the two raw score-level rhos
     (150 vs 650 per background), and delta sign agreement.

E1c -- DECISION RULE, pre-stated (both observations printed regardless;
  the label never replaces the numbers):
  "drops substantially" is defined before running as an absolute drop
  of MORE THAN 0.05 in the agreement between the full frame and the
  matched subset (applied separately to the raw agreement -- the
  record's 0.88 quantity -- and to the delta agreement); <= 0.05 =
  "holds near" its full-frame value.  The E1c conclusion then follows
  mechanically from which label applies, and the cross-model contrast
  on the SAME 100 positions (ESM-1v vs 150M/650M, raw and delta) is
  printed next to it.  The task's two readings map onto:
    subset agreement DROPS    -> the 150M/650M non-replication is much
                                 less alarming than currently written
    subset agreement HOLDS    -> the scale non-replication claim is
                                 strengthened
  Reported whichever is actually true; no other reading is offered.

GATES (failure -> print the exact mismatch, sys.exit(1); no retries,
  no threshold changes):
  G1  task58 CSV = 1,900 rows / exactly 100 unique positions;
      joined member frame on the analysis base = (10,757, 654) with
      zero missing member values.
  G2  FULL-frame points reproduce the record (T5a):
      raw median rounds to 0.882637, delta median rounds to 0.084365
      (6 dp -- deterministic, exact reproduction expected).
  G3  150M/650M recomputation reproduces its record (OVERNIGHT J2a-3
      / script 98 G7): PRIMARY rho rounds to 0.0978 (abs tol 5e-4
      against 0.0977638), raw score rhos round to 0.4157 / 0.4098
      (4 dp), sign agreement rounds to 53.11% (2 dp), n=1900/100.
  G4  every one of the 100 sampled positions is reported with its
      analysis-base row count; positions with zero rows are printed
      (not silently dropped) -- the subset frame's actual n and
      position count are printed either way.

  NOT hard-gated (disclosed): the bootstrap CIs themselves.  They are
  stochastic summaries; at N_BOOT=10000/seed 0 they should sit near
  the record's T5a/T4a intervals ([+0.869559,+0.891790] raw,
  [+0.052159,+0.122589] delta, [+0.039090,+0.226736]-scale for
  150/650), and the comparison is printed, but Monte-Carlo variation
  is not treated as a gate failure.

LIMITATIONS (printed with the output, AGENTS sec 6):
  - The matched subset is ONE seed-0 draw of 100 positions; results
    are frame-specific, not a distribution over subsets (stated, per
    AGENTS sec 3 on single synthetic draws).
  - The 150M model exists ONLY on these 100 positions; there is no
    full-frame 150M number to compare against (that would be new
    model scoring, barred this session).
  - Agreement here is pooled (row-level statistic, position
    clustering only in the CI) -- the record's own convention; T4a's
    within-position decomposition exists for the full frame and is
    quoted in the log, not recomputed here.
  - Reproducing the record's full-frame points (G2) is a UNIT TEST of
    implementation consistency, not independent evidence (AGENTS 6).

Usage:
  N_BOOT=300   venv/bin/python3 scripts/113_e1_matched_frame_agreement.py  # smoke
  N_BOOT=10000 venv/bin/python3 scripts/113_e1_matched_frame_agreement.py  # full
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib.stats import _spearman, position_cluster_bootstrap

PROC = ROOT / "data" / "processed"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
DROP_THRESHOLD = 0.05  # E1c pre-registered "substantial" drop (absolute)
OUT = PROC / "task113_matched_frame_agreement.csv"
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def med10(pairs_vals):
    a = np.asarray(pairs_vals, float)
    return float(np.median(a)), float(a.min()), float(a.max())


def boot_medians(pos_arr, cols, n_boot, seed):
    """Resample positions with replacement; recompute both medians-of-10
    fresh per draw (script 98's convention). Returns dict of percentiles."""
    rng = np.random.default_rng(seed)
    uniq = np.unique(pos_arr)
    idx_by = {c: np.flatnonzero(pos_arr == c) for c in uniq}
    raw_d = np.empty(n_boot)
    dl_d = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        rv, dv = [], []
        for k in range(5):
            for l in range(k + 1, 5):
                rv.append(_spearman(cols[k][i], cols[l][i]))
                dv.append(_spearman(cols[5 + k][i], cols[5 + l][i]))
        raw_d[b] = np.median(rv)
        dl_d[b] = np.median(dv)
    return (dict(raw_lo=float(np.percentile(raw_d, 2.5)),
                 raw_hi=float(np.percentile(raw_d, 97.5)),
                 dl_lo=float(np.percentile(dl_d, 2.5)),
                 dl_hi=float(np.percentile(dl_d, 97.5))))


if __name__ == "__main__":
    banner("E1 -- matched-frame ESM-1v agreement vs the 150M/650M "
           f"comparison (scripts/113)  N_BOOT={N_BOOT} seed={SEED}")

    # ---- G1: frames ------------------------------------------------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"G1 FAIL: analysis base = ({len(base)}, "
              f"{base['position'].nunique()}), expected (10757, 654)")

    mcols = {}
    for k in range(1, 6):
        mm = pd.read_csv(PROC / f"task_AC4_esm1v_member{k}_scores.csv")
        mm = mm[["position", "wt_aa", "mut_aa", "wt_logodds",
                 "av_logodds"]].copy()
        mm["delta_k"] = mm["av_logodds"] - mm["wt_logodds"]
        base = base.merge(mm[["position", "wt_aa", "mut_aa", "wt_logodds",
                              "delta_k"]].rename(
            columns={"wt_logodds": f"wt{k}", "delta_k": f"dl{k}"}),
            on=["position", "wt_aa", "mut_aa"], how="left")
    miss = sum(base[f"wt{k}"].isna().sum() + base[f"dl{k}"].isna().sum()
               for k in range(1, 6))
    if (len(base), base["position"].nunique(), miss) != (10757, 654, 0):
        gfail(f"G1 FAIL: joined frame = ({len(base)}, "
              f"{base['position'].nunique()}), missing member values {miss}")

    t58 = pd.read_csv(PROC / "task58_150m_check.csv")
    sample = sorted(t58["position"].unique().tolist())
    if (len(t58), len(sample)) != (1900, 100):
        gfail(f"G1 FAIL: task58 CSV = ({len(t58)} rows, "
              f"{len(sample)} positions), expected (1900, 100)")
    print(f"  G1 PASS: base (10757, 654), 5 members joined with 0 missing; "
          f"task58 CSV (1900 rows, 100 positions)")

    # subset frame + per-position row counts (G4 reporting)
    base["in_subset"] = base["position"].isin(sample)
    sub = base[base["in_subset"]].copy()
    rowcounts = base.groupby("position").size()
    empty = [p for p in sample if p not in set(base["position"])]
    print(f"  G4 subset frame: {len(sub)} rows / "
          f"{sub['position'].nunique()} of the 100 sampled positions "
          f"present in the analysis base; positions with zero rows: "
          f"{empty if empty else 'none'}")

    # ---- agreement on both frames ---------------------------------------
    def frame_cols(df):
        return ([df[f"wt{k}"].to_numpy() for k in range(1, 6)],
                [df[f"dl{k}"].to_numpy() for k in range(1, 6)])

    results = {}
    for label, df in [("FULL (654 pos)", base), ("MATCHED (100 pos)", sub)]:
        wc, dc = frame_cols(df)
        raw_m, raw_min, raw_max = med10(
            [_spearman(wc[k], wc[l]) for k in range(5)
             for l in range(k + 1, 5)])
        dl_m, dl_min, dl_max = med10(
            [_spearman(dc[k], dc[l]) for k in range(5)
             for l in range(k + 1, 5)])
        pos = df["position"].to_numpy()
        ci = boot_medians(pos, wc + dc, N_BOOT, SEED)
        results[label] = dict(raw=raw_m, raw_min=raw_min, raw_max=raw_max,
                              dl=dl_m, dl_min=dl_min, dl_max=dl_max, ci=ci,
                              n=len(df), npos=int(df["position"].nunique()))

    full, m100 = results["FULL (654 pos)"], results["MATCHED (100 pos)"]

    # ---- G2 record reproduction -----------------------------------------
    if round(full["raw"], 6) != 0.882637:
        gfail(f"G2 FAIL: full-frame RAW median {full['raw']!r} != 0.882637")
    if round(full["dl"], 6) != 0.084365:
        gfail(f"G2 FAIL: full-frame DELTA median {full['dl']!r} != 0.084365")
    print(f"  G2 PASS: full-frame raw {full['raw']:.6f} and delta "
          f"{full['dl']:.6f} reproduce the record (T5a) at 6 dp")

    # ---- 150M/650M own values (G3) ---------------------------------------
    pb = position_cluster_bootstrap(t58, "position", "delta150", "delta650",
                                    N_BOOT, SEED)
    rho_150_650 = float(pb["observed_rho"])
    raw_wt = float(_spearman(t58["score150_wt"], t58["esm2_score"]))
    raw_av = float(_spearman(t58["score150_bg"],
                             t58["esm2_score_a222v_bg"]))
    s150 = np.sign(t58["delta150"].to_numpy())
    s650 = np.sign(t58["delta650"].to_numpy())
    nz = (s150 != 0) & (s650 != 0)
    sign_agree = float((s150[nz] == s650[nz]).mean() * 100.0)
    if abs(rho_150_650 - 0.0977638) > 5e-4:
        gfail(f"G3 FAIL: PRIMARY rho {rho_150_650!r} vs 0.0977638")
    if (round(raw_wt, 4), round(raw_av, 4), round(sign_agree, 2)) != \
            (0.4157, 0.4098, 53.11):
        gfail(f"G3 FAIL: raw rhos ({raw_wt!r}, {raw_av!r}) sign "
              f"{sign_agree!r} vs (0.4157, 0.4098, 53.11)")
    print(f"  G3 PASS: 150M/650M recomputed -- PRIMARY {rho_150_650:+.4f} "
          f"CI=[{pb['ci_lo']:+.4f},{pb['ci_hi']:+.4f}] "
          f"p={pb['p_boot']:.4f}, raw wt {raw_wt:+.4f}, raw av "
          f"{raw_av:+.4f}, sign {sign_agree:.2f}% (all match record)")

    # ---- E1b side-by-side --------------------------------------------------
    banner("E1b -- ALL THREE READINGS SIDE BY SIDE", "-")
    hdr = (f"  {'frame':28s} {'n rows':>7s} {'pos':>4s} "
           f"{'RAW median-of-10':>34s}   {'DELTA median-of-10':>34s}")
    print(hdr)
    for label, r in [("ESM-1v full frame", full),
                     ("ESM-1v matched subset", m100)]:
        ci = r["ci"]
        print(f"  {label:28s} {r['n']:7d} {r['npos']:4d} "
              f"{r['raw']:+.6f} [{ci['raw_lo']:+.6f},{ci['raw_hi']:+.6f}]"
              f"   {r['dl']:+.6f} [{ci['dl_lo']:+.6f},{ci['dl_hi']:+.6f}]")
    print(f"  {'ESM-1v full (record T5a)':28s} {full['n']:7d} "
          f"{full['npos']:4d} {'+0.882637 [+0.869559,+0.891790]':>34s}"
          f"   {'+0.084365 [+0.052159,+0.122589]':>34s}")
    print(f"  {'150M/650M (same 100 pos)':28s} {len(t58):7d} "
          f"{len(sample):4d} "
          f"{'wt %+.4f / av %+.4f (per background)' % (raw_wt, raw_av):>34s}"
          f"   {rho_150_650:+.4f} [{pb['ci_lo']:+.4f},{pb['ci_hi']:+.4f}]"
          f"  sign {sign_agree:.2f}%")

    # ---- E1c pre-registered decision --------------------------------------
    banner("E1c -- WHICH READING THE RESULT SUPPORTS", "-")
    raw_drop = full["raw"] - m100["raw"]
    dl_drop = full["dl"] - m100["dl"]
    raw_label = ("DROPS SUBSTANTIALLY" if raw_drop > DROP_THRESHOLD
                 else "HOLDS NEAR its full-frame value")
    dl_label = ("DROPS SUBSTANTIALLY" if dl_drop > DROP_THRESHOLD
                else "HOLDS NEAR its full-frame value")
    print(f"  raw  : full {full['raw']:+.6f} -> subset {m100['raw']:+.6f} "
          f"(change {m100['raw'] - full['raw']:+.6f}; threshold "
          f"-{DROP_THRESHOLD:.2f}) -> {raw_label}")
    print(f"  delta: full {full['dl']:+.6f} -> subset {m100['dl']:+.6f} "
          f"(change {m100['dl'] - full['dl']:+.6f}; threshold "
          f"-{DROP_THRESHOLD:.2f}) -> {dl_label}")
    print(f"  on the SAME 100 positions: ESM-1v raw {m100['raw']:+.6f} vs "
          f"150M/650M raw {raw_wt:+.4f}/{raw_av:+.4f}; ESM-1v delta "
          f"{m100['dl']:+.6f} vs 150M/650M delta {rho_150_650:+.4f}")
    if raw_drop > DROP_THRESHOLD or dl_drop > DROP_THRESHOLD:
        print("  VERDICT (pre-registered mapping): ESM-1v's agreement ALSO "
              "drops on the matched subset -> the 150M/650M scale "
              "non-replication is MUCH LESS ALARMING than currently "
              "written (frame/subset restricted agreement is weaker for "
              "everyone).")
    else:
        print("  VERDICT (pre-registered mapping): ESM-1v's agreement "
              "HOLDS near its full-frame value on the matched subset -> "
              "the scale non-replication claim is STRENGTHENED (the "
              "150M/650M collapse is not a property of this frame).")

    pd.DataFrame([
        dict(frame=k, n=r["n"], n_pos=r["npos"],
             raw_median=r["raw"], raw_lo=r["ci"]["raw_lo"],
             raw_hi=r["ci"]["raw_hi"], delta_median=r["dl"],
             delta_lo=r["ci"]["dl_lo"], delta_hi=r["ci"]["dl_hi"])
        for k, r in results.items()] + [
        dict(frame="150M/650M delta", n=len(t58), n_pos=len(sample),
             raw_median=rho_150_650, raw_lo=pb["ci_lo"],
             raw_hi=pb["ci_hi"], delta_median=np.nan, delta_lo=np.nan,
             delta_hi=np.nan),
        dict(frame="150M/650M raw wt / av / sign%", n=len(t58),
             n_pos=len(sample), raw_median=raw_wt, raw_lo=np.nan,
             raw_hi=np.nan, delta_median=raw_av, delta_lo=np.nan,
             delta_hi=np.nan),
    ]).to_csv(OUT, index=False)

    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. The matched subset is ONE seed-0 draw of 100 positions:")
    print("     frame-specific, not a distribution over subsets.")
    print("  2. 150M exists only on these 100 positions (no full-frame")
    print("     150M number; new model scoring is barred this session).")
    print("  3. Statistics are pooled; position clustering enters only")
    print("     the CIs (the record's own convention; T4a's")
    print("     within-position decomposition is quoted, not redone).")
    print("  4. G2/G3 reproductions are unit tests, not evidence.")
    print(f"\nWrote {OUT}")
    print(f"SCRIPT 113 DONE ({time.time() - T0:.1f}s)")
