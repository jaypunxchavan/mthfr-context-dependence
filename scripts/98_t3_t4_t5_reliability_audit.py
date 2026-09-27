#!/usr/bin/env python3
"""
Script 98 (disattenuation-and-ledger: tasks T3 + T4 + T5): the
reliability-audit bootstrap -- an empirical CI on the disattenuated
estimate, the pooled-vs-position-controlled reliability decomposition,
and the WT-base-score-vs-delta agreement comparison.

PRE-REGISTRATION (written before any number below existed; AGENTS s0/s6)

WHY THIS SCRIPT EXISTS
----------------------
A2's disattenuation (scripts/91) divides the headline rho by a
reliability that is itself estimated from the same finite data (the
median of the 10 pairwise ESM-1v member correlations on delta).  T3 asks
for the CI you get when BOTH the numerator and that denominator are
re-estimated inside every bootstrap draw.  T4 asks whether the
denominator was computed pooled (inflatable by shared positional
structure) or with position held fixed.  T5 asks for the base-score
agreement beside the delta agreement, same convention, same frame --
a comparison that needs no disattenuation at all.

FRAME (frozen)
--------------
base  = data/processed/task32_analysis_table.csv dropna(own_e_b,
        GI_folinate_independent, delta_esm) -> must be 10,757 rows /
        654 positions (script 86's exact R4 base, L458-461).
members = data/processed/task_AC4_esm1v_member{1..5}_scores.csv merged
        left onto base on [position, mut_aa], validate="1:1" (script 86
        L483-495 convention; any missing match or wt_aa mismatch = exit).
syn   = data/raw/mthfrModel/results/folate_response_model5.csv with
        own_e_b rebuilt via scripts.lib.stats_ext.rebuild_interaction_fit,
        rows with type == "synonymous" (script 47 L130-146 convention).

GATES (failure => print, sys.exit(1); NO threshold raising, NO retry)
----------------------------------------------------------------------
G1 frame            : (10757 rows, 654 positions)
G2 headline rho     : _spearman(delta_esm, own_e_b) ==
                      -0.08811806424891734 (tol 1e-9)
G3 rel_delta pooled : median of the 10 pairwise member Spearman on
                      `delta` == 0.084365 (tol 1e-6; published 6 dp)
G4 WT pooled        : median of the 10 pairwise member Spearman on
                      `wt_logodds` == 0.882637 (tol 1e-6)
G5 rel_own          : 1 - var(syn own_e_b, ddof=1)/var(own_e_b, ddof=1)
                      == 0.6363 (tol 5e-4; published 4 dp)
G6 derived points   : delta-only = rho/sqrt(rel_delta) == -0.303378 and
                      fully = rho/sqrt(rel_delta*rel_own) == -0.380323
                      (tol 1e-5 each)
G7 AC2 frame+rho    : task58_150m_check.csv matched frame is
                      (1900 rows, 100 positions) and
                      _spearman(delta150, delta650) == 0.0978
                      (tol 5e-4; AC2 published 4 dp)

THE BOOTSTRAP (T3; N_BOOT env, default 10000; seed 0)
------------------------------------------------------
One draw = sample the 654 positions with replacement; the draw's rows =
concatenation of every analysis row at each drawn position (a position
drawn twice contributes its rows twice -- the standard cluster
bootstrap, and exactly the resampling unit scripts/lib/stats.py
position_cluster_bootstrap uses, L51-52: rng.choice(clusters,
size=len(clusters), replace=True)).  Synonymous rows travel with their
positions the same way.  Inside EVERY draw, recompute from scratch:

    rho_b    = _spearman(delta_esm, own_e_b)                (numerator)
    rel_b    = median of the 10 pairwise member Spearman on
               delta, POOLED across the draw's rows           (T3/T4)
    relW_b   = the same 10-pair median after subtracting each
               member's per-position mean                    (T4)
    relB_b   = median of the 10 pairwise member Spearman across
               the draw's per-position means                 (T4)
    relOwn_b = 1 - var(syn own_e_b in draw)/var(own_e_b in draw)
    wt_b     = median of the 10 pairwise member Spearman on
               wt_logodds, pooled (script 86 R7b's convention; T5)

then form the disattenuated statistics fresh in that same draw:

    delta-only_b = rho_b / sqrt(rel_b)
    fully_b      = rho_b / sqrt(rel_b * relOwn_b)

Report = percentile 2.5/97.5 empirical CI (+ median) for every
quantity.  Draws whose denominator <= 0 are COUNTED AND REPORTED and
excluded from the disattenuation CI (never silently dropped); if >1%
of draws are non-positive the script prints a loud warning that the
disattenuation is unstable in its tails.

Demeaning note (pre-registered): because a cluster draw brings ALL rows
of a position, the per-position mean inside a draw equals the
per-position mean on the full frame; the within-position residual
arrays are therefore computed once on the full frame and merely sliced
per draw.  Between-position means are likewise full-frame per-position
means, indexed by the drawn positions (with multiplicity).

T4's side-by-side (reported together; neither chosen post-hoc):
  pooled (A2's quantity) | within-position | between-position,
each with its bootstrap CI.  AC2's 150M-vs-650M pair on
task58_150m_check.csv gets the same pooled/within treatment with its
own 100-position cluster bootstrap (its pooled CI is printed beside
AC2's published CI [-0.0444, +0.2275] as a reproduction check).

T5's side-by-side: WT-base agreement (pooled median-of-10, gated
0.882637) vs delta agreement (gated 0.084365) -- same convention, same
frame, same draws.  Standalone result; depends on no disattenuation.

DISCLOSURES (printed in this script's output, per AGENTS s6)
-------------------------------------------------------------
1. This CI quantifies sampling variability of the ratio under position
   resampling.  It does NOT license transferring either reliability to
   ESM-2 (task T1's separate documented finding: ESM-2 is not a member
   of the ESM-1v seed family -- different corpus, architecture, run).
2. rel_own's in-draw recompute resamples synonymous rows by position,
   so syn and analysis variances share the draw; this differs from
   A2's point computation only through resampling (gated by G5).
3. within-position = subtract the frame's own per-position means
   (fixed-effect style); it removes ALL between-position structure,
   including the real distance-to-222 gradient, so it isolates
   within-residue agreement specifically -- it is not "the correct
   number", it is the isolated quantity the review asked for.
4. AC2 uses one checkpoint pair over 100 positions; its CIs are coarse.

Run: N_BOOT=300  venv/bin/python3 scripts/98_t3_t4_t5_reliability_audit.py   (smoke)
      N_BOOT=10000 venv/bin/python3 scripts/98_t3_t4_t5_reliability_audit.py (full)
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from scripts.lib.stats import _spearman
from scripts.lib.stats_ext import rebuild_interaction_fit

PROC = Path("data/processed")
RAW = Path("data/raw/mthfrModel")

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
SMOKE = N_BOOT <= 500

RHO_PUB = -0.08811806424891734
REL_D_PUB = 0.084365
WT_PUB = 0.882637
REL_OWN_PUB = 0.6363
DIS_PUB = -0.303378
DIS_FULL_PUB = -0.380323
AC2_RHO_PUB = 0.0978
AC2_CI_PUB = (-0.0444, 0.2275)

t_start = time.time()


def log(msg):
    print(msg, flush=True)


def gate(name, got, want, tol):
    ok = abs(float(got) - float(want)) <= tol
    log(f"GATE {name}: got {got!r} want {want!r} tol {tol} -> "
        f"{'OK' if ok else 'FAILED'}")
    if not ok:
        sys.exit(1)


def pct(a, lo=2.5, hi=97.5):
    a = np.asarray(a, dtype=float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return (np.nan, np.nan, np.nan)
    return (float(np.percentile(a, lo)), float(np.median(a)),
            float(np.percentile(a, hi)))


def main():
    if SMOKE:
        log("*** SMOKE RUN (N_BOOT <= 500): machinery checks only, "
            "NOT findings, NOT for quoting. ***")
    log(f"script 98 | N_BOOT={N_BOOT} seed={SEED} "
        f"started {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # ---------------- frame + members (script 86 conventions) -------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(
        subset=["own_e_b", "GI_folinate_independent", "delta_esm"]
    ).copy()
    n_rows, n_pos = len(base), base["position"].nunique()
    log(f"G1a base frame: {n_rows} rows / {n_pos} positions "
        f"(expect 10757 / 654)")
    if (n_rows, n_pos) != (10757, 654):
        log("G1 FAILED: base frame differs from script 32's published set")
        sys.exit(1)

    for k in range(1, 6):
        p = PROC / f"task_AC4_esm1v_member{k}_scores.csv"
        if not p.exists():
            log(f"G1 FAILED: missing {p}")
            sys.exit(1)
        m = pd.read_csv(p)
        j = base.merge(
            m[["position", "wt_aa", "mut_aa", "wt_logodds", "delta"]],
            on=["position", "mut_aa"], how="left", validate="1:1",
            suffixes=("", f"_m{k}"))
        if j["delta"].isna().any():
            log(f"G1 FAILED: member {k} unmatched rows present")
            sys.exit(1)
        if not (j["wt_aa"] == j[f"wt_aa_m{k}"]).all():
            log(f"G1 FAILED: member {k} wt_aa mismatch")
            sys.exit(1)
        base[f"delta_m{k}"] = j["delta"].to_numpy()
        base[f"wt_m{k}"] = j["wt_logodds"].to_numpy()
    base = base.reset_index(drop=True)
    log("G1 PASS: frame + 5-member join exact (R4 convention)")

    cols = ["delta_esm", "own_e_b"] + [f"delta_m{k}" for k in range(1, 6)] \
        + [f"wt_m{k}" for k in range(1, 6)]
    arr = {c: base[c].to_numpy(float) for c in cols}

    # ---------------- gates G2-G6 ------------------------------------------
    rho_full = float(_spearman(arr["delta_esm"], arr["own_e_b"]))
    gate("G2 headline rho", rho_full, RHO_PUB, 1e-9)

    def pair_median(getter):
        vals = []
        for k in range(1, 6):
            for l in range(k + 1, 6):
                vals.append(_spearman(getter(k), getter(l)))
        return float(np.median(vals)), vals

    rel_d_full, _ = pair_median(lambda k: arr[f"delta_m{k}"])
    gate("G3 rel_delta pooled (median of 10 pairs)", rel_d_full, REL_D_PUB,
         1e-6)
    wt_full, _ = pair_median(lambda k: arr[f"wt_m{k}"])
    gate("G4 WT pooled (median of 10 pairs)", wt_full, WT_PUB, 1e-6)

    # syn own_e_b (script 47's rebuild path)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    syn = pd.DataFrame({"position": raw["start"].to_numpy(int),
                        "type": raw["type"].to_numpy(),
                        "own_e_b": fit["e2"]["e_b"]})
    syn = syn[(syn["type"] == "synonymous")].dropna(subset=["own_e_b"])
    ana_var = float(np.var(arr["own_e_b"], ddof=1))
    syn_var = float(np.var(syn["own_e_b"].to_numpy(float), ddof=1))
    rel_own_full = 1.0 - syn_var / ana_var
    gate("G5 rel_own (1 - var(syn)/var(ana))", rel_own_full, REL_OWN_PUB,
         5e-4)
    log(f"      (syn rows n={len(syn)}, var={syn_var:.5f}; "
        f"analysis var={ana_var:.5f})")

    dis_full = rho_full / np.sqrt(rel_d_full)
    gate("G6 delta-only disattenuated point", dis_full, DIS_PUB, 1e-5)
    dis_full2 = rho_full / np.sqrt(rel_d_full * rel_own_full)
    gate("G6 fully disattenuated point", dis_full2, DIS_FULL_PUB, 1e-5)

    # ---------------- AC2 frame + pooled rho (G7) ---------------------------
    ac2 = pd.read_csv(PROC / "task58_150m_check.csv").dropna(
        subset=["delta150", "delta650"]).reset_index(drop=True)
    a_rows, a_pos = len(ac2), ac2["position"].nunique()
    if (a_rows, a_pos) != (1900, 100):
        log(f"G7 FAILED: AC2 frame {a_rows}/{a_pos} != 1900/100")
        sys.exit(1)
    ac2_rho = float(_spearman(ac2["delta150"].to_numpy(float),
                               ac2["delta650"].to_numpy(float)))
    gate("G7 AC2 pooled rho", ac2_rho, AC2_RHO_PUB, 5e-4)
    log("ALL GATES GREEN -- proceeding to the bootstrap\n")

    # ---------------- index machinery --------------------------------------
    rng = np.random.default_rng(SEED)
    positions = np.sort(base["position"].unique())
    n_cl = len(positions)
    idx_by_pos = {int(p): np.asarray(ix, dtype=int)
                  for p, ix in base.groupby("position").indices.items()}
    syn_idx_by_pos = {}
    syn_pos = syn["position"].to_numpy(int)
    syn_own = syn["own_e_b"].to_numpy(float)
    for i, p in enumerate(syn_pos):
        syn_idx_by_pos.setdefault(int(p), []).append(i)
    syn_idx_by_pos = {p: np.asarray(ix, dtype=int)
                      for p, ix in syn_idx_by_pos.items()}

    # within-position residual arrays (equal to in-draw demeaning; see
    # pre-registration note above)
    within = {}
    pm = base.groupby("position")[cols].mean()
    for c in [f"delta_m{k}" for k in range(1, 6)]:
        within[c] = (arr[c] - pm[c].reindex(base["position"]).to_numpy())
    # between-position means in position order
    pm_arr = {c: pm[c].reindex(positions).to_numpy()
              for c in [f"delta_m{k}" for k in range(1, 6)]}

    def pair_median_local(a, di):
        vals = []
        for k in range(1, 6):
            for l in range(k + 1, 6):
                vals.append(_spearman(a[f"wt_m{k}"][di], a[f"wt_m{l}"][di]))
        return float(np.median(vals)), vals

    # full-frame point values for the T4 decomposition
    wv, bv = [], []
    for k in range(1, 6):
        for l in range(k + 1, 6):
            wv.append(_spearman(within[f"delta_m{k}"],
                                within[f"delta_m{l}"]))
            bv.append(_spearman(pm_arr[f"delta_m{k}"],
                                pm_arr[f"delta_m{l}"]))
    within_point, between_point = float(np.median(wv)), float(np.median(bv))

    # ---------------- the bootstrap loop ------------------------------------
    log(f"bootstrap: {N_BOOT} draws of {n_cl} positions "
        f"(each draw ~41 Spearman computations) ...")
    B = {k: np.empty(N_BOOT) for k in
         ["rho", "rel_pool", "rel_within", "rel_between", "rel_own",
          "wt_pool", "dis_delta", "dis_full"]}
    nonpos_d = nonpos_f = 0

    for b in range(N_BOOT):
        drawn = rng.choice(positions, size=n_cl, replace=True)
        di = np.concatenate([idx_by_pos[int(p)] for p in drawn])

        rho_b = float(_spearman(arr["delta_esm"][di], arr["own_e_b"][di]))
        B["rho"][b] = rho_b

        def med(getter_arr):
            vals = []
            for k in range(1, 6):
                for l in range(k + 1, 6):
                    vals.append(_spearman(getter_arr(k)[di],
                                          getter_arr(l)[di]))
            return float(np.median(vals))

        rel_b = med(lambda k: arr[f"delta_m{k}"])
        B["rel_pool"][b] = rel_b

        drawn_pos_i = np.searchsorted(positions, drawn)
        wvals = []
        bvals = []
        for k in range(1, 6):
            for l in range(k + 1, 6):
                wvals.append(_spearman(within[f"delta_m{k}"][di],
                                        within[f"delta_m{l}"][di]))
                bvals.append(_spearman(pm_arr[f"delta_m{k}"][drawn_pos_i],
                                        pm_arr[f"delta_m{l}"][drawn_pos_i]))
        B["rel_within"][b] = float(np.median(wvals))
        B["rel_between"][b] = float(np.median(bvals))

        # rel_own in-draw
        si = [syn_idx_by_pos[int(p)] for p in drawn if int(p) in syn_idx_by_pos]
        si = np.concatenate(si) if si else np.empty(0, dtype=int)
        if len(si) >= 2:
            v_syn = float(np.var(syn_own[si], ddof=1))
            B["rel_own"][b] = 1.0 - v_syn / float(
                np.var(arr["own_e_b"][di], ddof=1))
        else:
            B["rel_own"][b] = np.nan

        wt_b, _ = pair_median_local(arr, di)
        B["wt_pool"][b] = wt_b

        if rel_b > 0:
            B["dis_delta"][b] = rho_b / np.sqrt(rel_b)
        else:
            B["dis_delta"][b] = np.nan
            nonpos_d += 1
        if rel_b > 0 and np.isfinite(B["rel_own"][b]) and B["rel_own"][b] > 0:
            B["dis_full"][b] = rho_b / np.sqrt(rel_b * B["rel_own"][b])
        else:
            B["dis_full"][b] = np.nan
            nonpos_f += 1

        if (b + 1) % max(1, N_BOOT // 10) == 0:
            log(f"  {b + 1}/{N_BOOT} draws "
                f"({time.time() - t_start:.0f}s elapsed)")

    # ---------------- AC2 own cluster bootstrap (100 positions) -------------
    a_pos_arr = np.sort(ac2["position"].unique())
    a_idx = {int(p): np.asarray(ix, dtype=int)
             for p, ix in ac2.groupby("position").indices.items()}
    a_pool = np.empty(N_BOOT)
    a_within = np.empty(N_BOOT)
    ac2_d = ac2["delta150"].to_numpy(float)
    ac2_e = ac2["delta650"].to_numpy(float)
    ac2_pos = ac2["position"].to_numpy(int)
    ac2_pm = ac2.groupby("position")[["delta150", "delta650"]].mean()
    ac2_w150 = ac2_d - ac2_pm["delta150"].reindex(ac2_pos).to_numpy()
    ac2_w650 = ac2_e - ac2_pm["delta650"].reindex(ac2_pos).to_numpy()
    for b in range(N_BOOT):
        d2 = rng.choice(a_pos_arr, size=len(a_pos_arr), replace=True)
        ii = np.concatenate([a_idx[int(p)] for p in d2])
        a_pool[b] = _spearman(ac2_d[ii], ac2_e[ii])
        a_within[b] = _spearman(ac2_w150[ii], ac2_w650[ii])
    ac2_within_point = float(_spearman(
        ac2_d - ac2_pm["delta150"].reindex(ac2_pos).to_numpy(),
        ac2_e - ac2_pm["delta650"].reindex(ac2_pos).to_numpy()))

    # ---------------- report -------------------------------------------------
    rows = []

    def report(name, task, point, draws=None, pub=None):
        if draws is None:
            lo = med = hi = np.nan
        else:
            lo, med, hi = pct(draws)
        pub_s = "" if pub is None else f"  published={pub}"
        log(f"{task}  {name}: point={point:+.6f}  "
            f"CI=[{lo:+.6f}, {med:+.6f}, {hi:+.6f}] (pct 2.5/50/97.5)"
            f"{pub_s}")
        rows.append({"task": task, "quantity": name, "point": point,
                     "ci_lo": lo, "ci_med": med, "ci_hi": hi,
                     "published": "" if pub is None else pub,
                     "n_boot": N_BOOT,
                     "n_nonpos_denominator": ""})

    log("\n==== T3: disattenuated estimate with in-draw reliability "
        "(the CI the review asked for) ====")
    report("disattenuated delta-only = rho/sqrt(rel_delta)", "T3",
           dis_full, B["dis_delta"], pub=DIS_PUB)
    report("disattenuated fully = rho/sqrt(rel_delta*rel_own)", "T3",
           dis_full2, B["dis_full"], pub=DIS_FULL_PUB)
    report("headline rho (in-draw)", "T3", rho_full, B["rho"], pub=RHO_PUB)
    report("rel_delta pooled (in-draw)", "T3", rel_d_full, B["rel_pool"],
           pub=REL_D_PUB)
    report("rel_own (in-draw)", "T3", rel_own_full, B["rel_own"],
           pub=REL_OWN_PUB)
    frac_d = nonpos_d / N_BOOT
    frac_f = nonpos_f / N_BOOT
    log(f"non-positive denominators: delta-only {nonpos_d}/{N_BOOT} "
        f"({frac_d:.2%}), fully {nonpos_f}/{N_BOOT} ({frac_f:.2%}) "
        f"-- excluded from the CIs above, reported not hidden")
    if frac_d > 0.01 or frac_f > 0.01:
        log("WARNING: >1% of draws had a non-positive denominator -- the "
            "disattenuation is unstable in its tails; report the CI with "
            "that caveat.")

    log("\n==== T4: pooled vs position-controlled reliability, side by "
        "side (inflated vs isolated) ====")
    report("rel_delta POOLED (A2's quantity)", "T4", rel_d_full,
           B["rel_pool"], pub=REL_D_PUB)
    report("rel_delta WITHIN-position (position demeaned)", "T4",
           within_point, B["rel_within"])
    report("rel_delta BETWEEN-position (position means)", "T4",
           between_point, B["rel_between"])
    log(f"T4  AC2 150M-vs-650M pooled: point={ac2_rho:+.6f} "
        f"CI=[{pct(a_pool)[0]:+.6f}, {pct(a_pool)[2]:+.6f}] "
        f"published CI=[{AC2_CI_PUB[0]:+.4f}, {AC2_CI_PUB[1]:+.4f}] "
        f"n=1900 pos=100")
    log(f"T4  AC2 150M-vs-650M WITHIN-position: point={ac2_within_point:+.6f} "
        f"CI=[{pct(a_within)[0]:+.6f}, {pct(a_within)[2]:+.6f}]")
    rows.append({"task": "T4", "quantity": "AC2 pooled",
                 "point": ac2_rho, "ci_lo": pct(a_pool)[0], "ci_med": pct(a_pool)[1],
                 "ci_hi": pct(a_pool)[2], "published": AC2_RHO_PUB,
                 "n_boot": N_BOOT, "n_nonpos_denominator": ""})
    rows.append({"task": "T4", "quantity": "AC2 within-position",
                 "point": ac2_within_point, "ci_lo": pct(a_within)[0],
                 "ci_med": pct(a_within)[1], "ci_hi": pct(a_within)[2],
                 "published": "", "n_boot": N_BOOT,
                 "n_nonpos_denominator": ""})

    log("\n==== T5: the money figure -- WT-base vs delta agreement, same "
        "five checkpoints, no disattenuation involved ====")
    report("cross-member agreement on RAW WT scores (median of 10)", "T5",
           wt_full, B["wt_pool"], pub=WT_PUB)
    report("cross-member agreement on DELTAS (median of 10)", "T5",
           rel_d_full, B["rel_pool"], pub=REL_D_PUB)
    log(f"T5 ratio WT/delta (point): {wt_full / rel_d_full:.2f}x")

    log("\nDISCLOSURES (script 98's own limitations):")
    log("1. This CI is sampling variability of the ratio under position "
        "resampling; it does NOT license transferring either reliability "
        "to ESM-2 (T1: ESM-2 is outside the ESM-1v seed family).")
    log("2. rel_own's in-draw variance shares the position draw with the "
        "analysis rows (syn rows travel with their positions).")
    log("3. within-position removes ALL between-position structure "
        "(including the real distance-to-222 gradient); it isolates "
        "within-residue agreement, it is not 'the correct number'.")
    log("4. AC2 has one checkpoint pair over 100 positions -- coarse CI.")

    out = PROC / ("task_T3T4T5_reliability_audit_smoke.csv" if SMOKE
                  else "task_T3T4T5_reliability_audit.csv")
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"\n[saved] {out}")
    log(f"done in {time.time() - t_start:.1f}s "
        f"({time.strftime('%Y-%m-%d %H:%M:%S')})")


if __name__ == "__main__":
    main()
