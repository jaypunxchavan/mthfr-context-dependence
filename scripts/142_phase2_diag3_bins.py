"""Script 142 -- Phase 2 diagnostics III, Task D14: MODEL-FREE GRADIENT BINS by
3D distance, INCLUDING Arm S AT 0 A.  No fitted functional form anywhere.

WHY
---
D10a's answers range from p_spec_adj 0.13 (linear distance) to 0.89
(log1p(distance)) to 1.00 (3D distance) because each extrapolates a fitted form
to distance 0, a point no null occupies.  This task shows the raw picture with
NO fitted form at all: rho_b is simply summarised inside fixed distance bins,
with Arm S occupying the distance-0 bin.

SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as
a label for any result computed here.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN.  BINS ARE FIXED NOW AND
ARE NOT TUNED
--------------------------------------------------------------------------
Distance axis: `d3_CA` from data/processed/phase2_diagnostics/
background_3d_distance.csv, whose sha256 is checked before anything else.

BINS, fixed in advance:
    {exactly 0}            -> Arm S (all 18 are at position 222, d3_CA = 0)
    (0, 12]
    (12, 20]
    (20, 30]
    (30, 45]
    (45, inf)

BackgrounRESOLUTION: the 11 backgrounds with `resolved` false get NO distance,
are LISTED BY NAME, and are EXCLUDED from every bin.  They are NEVER imputed
and never silently dropped.  Chain A resolves residues 40..651 with internal
gaps 161-171 and 392-396, so positions 2-39, 161-171, 392-396 and 652-656 have
no chain-A coordinates; all 11 unresolved backgrounds sit in one of those.

D14.0 BIN TABLE.  Per bin and per view: n by arm; mean / median / min / max of
  rho_b; mean of mean|delta_b| (so the shift covariate is VISIBLE in every
  bin, because the bins are not matched for it); and A222V's own rho printed as
  the reference line.  Arm S is reported in its own row AND as a separate arm
  breakdown, because "at 0 A" is the entire point of this task.

D14.1 DISCONTINUITY CHECK.  Difference of means
      mean(rho, Arm S) - mean(rho, resolved nulls in (0, 12])
  with an INDEPENDENT-GROUPS BACKGROUND-LEVEL bootstrap 95% CI (10,000 draws,
  SEED=0): the two groups are disjoint sets of backgrounds, so each is
  resampled separately with replacement and the difference recomputed.  The
  (0, 12] bin is labelled **n = 6 AND UNSTABLE** everywhere it is used.  All
  six members are listed by name with their d3_CA.
  *** THIS IS A DESCRIPTIVE COMPARISON OF TWO SMALL SAMPLES.  It is NOT a
  test of a discontinuity and no p-value is computed. ***

D14.2 POST-HOC TARGET CHECK.  Reproduce the task doc's calculation from its D2
  table: mean rho of the 10 sequence-nearest nulls against the Arm S mean, both
  views.  LABELLED POST-HOC IN THE OUTPUT AND IN EVERY TABLE THAT USES IT: it
  was computed after seeing the data.  Targets: -0.0557 (full) / -0.0591 (H)
  against Arm S -0.0652 (full) / -0.0702 (H).

D14.3 FIGURE.  If matplotlib imports, save
  data/processed/phase2_diagnostics/rho_vs_d3.png.  ELSE LOG SKIPPED AND DO NOT
  INSTALL IT (the task doc rule 9).  The check is performed and the result is
  printed either way.

RESAMPLING UNIT
---------------
BACKGROUND, and ONLY for D14.1's difference-of-means CI: each group is a set of
backgrounds, so the only thing a bootstrap can legitimately resample is WHICH
BACKGROUNDS WERE DRAWN, and each background's already-computed rho_b is held
FIXED within a draw.  The two groups are resampled INDEPENDENTLY because they
are disjoint background sets.  N_BOOT = 10,000, SEED = 0.
D14.0 and D14.2 perform NO RESAMPLING: deterministic summaries and exact
counts.  No position-within-background bootstrap is used anywhere, because no
statistic here is computed inside one background.

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result
computed here.  No adjusted p_spec is computed in this task, so the frozen
numeric thresholds are not invoked; every quantity is a bin summary or a
difference of bin means.

LIMITS (AGENTS 6; AGENTS 3 on effect size)
------------------------------------------
* The bins are FIXED in advance and are not tuned, but they are still bins:
  results inside a bin depend on where its edges fall.  The bin n's are printed
  at every use so a reader can see the small ones.
* The (0, 12] bin has n = 6 nulls and is labelled unstable everywhere.
* The bins are NOT matched for mean|delta|.  Mean|delta| is printed in every
  bin precisely so the reader can see that a distance-bin difference and a
  shift difference are confounded in this picture.
* rho_b for 96 backgrounds share one y-vector (own_e_b) and are mutually
  correlated.  Nothing here models that.
* d3_CA is a CA-CA distance in ONE 2.50 A crystal structure of the DIMER; a
  CA-CA distance is not a contact, side chains and alternate conformations are
  not modelled, and 11 unresolved backgrounds are excluded and never imputed.
* D14.2 is POST-HOC and is labelled as such.

Usage:
  N_BOOT=10000 SEED=0 venv/bin/python3 scripts/142_phase2_diag3_bins.py
"""

import hashlib
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))

# BINS, fixed now, not tuned.
BINS = [
    ("{exactly 0}  (Arm S)", 0.0, 0.0, True),        # inclusive lower & upper
    ("(0, 12]", 0.0, 12.0, False),
    ("(12, 20]", 12.0, 20.0, False),
    ("(20, 30]", 20.0, 30.0, False),
    ("(30, 45]", 30.0, 45.0, False),
    ("(45, inf)", 45.0, float("inf"), False),
]

# D14.2 post-hoc targets, quoted from the task doc.
TGT_SEQ10 = {"full": -0.0557, "H": -0.0591}
TGT_ARM_S = {"full": -0.0652, "H": -0.0702}

checks = []
t0 = time.time()


def agree(label, got, target, tol=5e-5):
    ok = abs(float(got) - float(target)) < tol
    checks.append((label, ok))
    print(f"    {label:<50s} recomputed = {float(got):+.6f}   "
          f"target = {float(target):+.6f}   "
          f"|diff| = {abs(float(got) - float(target)):.3e}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


def which_bin(d, first_bin_is_zero):
    if first_bin_is_zero and d == 0.0:
        return BINS[0][0]
    for nm, lo, hi, _ in BINS:
        if (d > lo or lo == 0.0 and first_bin_is_zero) and d <= hi:
            return nm
    return None


def main():
    p3.banner("D14 -- MODEL-FREE GRADIENT BINS BY 3D DISTANCE, INCLUDING "
              "Arm S AT 0 A (script 142)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word "
          "is used as a label.")
    print("NO FITTED FUNCTIONAL FORM APPEARS ANYWHERE IN THIS SCRIPT.  Bins "
          "are fixed in advance and are NOT tuned.")
    print("RESAMPLING UNIT: BACKGROUND, and only for D14.1's "
          f"difference-of-means CI (N_BOOT={N_BOOT}, SEED={SEED}, per-"
          "background rho_b held FIXED, the two disjoint groups resampled "
          "INDEPENDENTLY).  D14.0 and D14.2 do NO resampling.")

    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    print(f"\n  background_3d_distance.csv sha256 = {sha3}")
    print(f"  {'MATCH' if sha3 == p3.D3_SHA else '*** MISMATCH ***'} "
          f"(required {p3.D3_SHA})")
    assert sha3 == p3.D3_SHA, "3D table sha256 mismatch -- STOP D14"
    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    print(f"  background_rho_table.csv sha256 = {sha1}")
    print(f"  {'MATCH' if sha1 == p3.RHO_TABLE_SHA else '*** MISMATCH ***'}")
    assert sha1 == p3.RHO_TABLE_SHA, "rho table sha256 mismatch -- STOP D14"

    st = p3.build()
    bgs, S_ids, N_ids, resN = st["bgs"], st["S_ids"], st["N_ids"], st["resN"]
    RHO, RHO_A, mad, mad_a, df3 = (st["RHO"], st["RHO_A"], st["mad"],
                                   st["mad_a"], st["df3"])
    unres = sorted(b for b in bgs if not bool(df3.loc[b, "resolved"]))
    res = [b for b in bgs if b not in unres]
    print(f"\n  RESOLUTION ACCOUNTING -- nothing imputed, ever:")
    print(f"    96 backgrounds; {len(unres)} unresolved, EXCLUDED from every "
          f"bin and listed by name:")
    print(f"      {unres}")
    print(f"    of those, in the null set N: "
          f"{[b for b in unres if b in N_ids]}  ({len([b for b in unres if b in N_ids])} of {len(unres)})")
    print(f"    resolved backgrounds = {len(res)}  (Arm S {len(S_ids)}, "
          f"resolved V {len([b for b in res if st['ARM'][b] == 'V'])}, "
          f"resolved G {len([b for b in res if st['ARM'][b] == 'G'])})")
    print(f"    resolved null set = {len(resN)} of {len(N_ids)}")

    # ---------------------------------------------------------------- D14.0
    p3.banner("D14.0 -- BIN TABLE (no fitted form; bins fixed in advance)",
              "-")
    binof = {b: which_bin(float(df3.loc[b, "d3_CA"]), b in S_ids)
             for b in res}
    assert all(v is not None for v in binof.values()), "a resolved bg fell in no bin"
    for view in p3.VIEWS:
        print(f"\n  === [{view}] ===  (A222V rho = {RHO_A[view]:+.9f}, "
              f"mean|delta| = {mad_a[view]:.6f}, d3_CA = 0.000 A -- the "
              f"REFERENCE LINE)")
        print(f"  {'bin (d3_CA)':>18s} {'n':>4s} {'S':>3s} {'V':>3s} {'G':>3s} "
              f"{'mean rho':>11s} {'median':>11s} {'min':>11s} {'max':>11s} "
              f"{'mean|delta|':>12s}")
        for nm, lo, hi, _ in BINS:
            sub = [b for b in res if binof[b] == nm]
            if not sub:
                print(f"  {nm:>18s} {0:>4d} {'-':>3s} {'-':>3s} {'-':>3s} "
                      f"{'(empty bin)':>11s}")
                continue
            v = np.array([RHO[view][b] for b in sub], float)
            m = np.array([mad[view][b] for b in sub], float)
            ns = sum(1 for b in sub if st["ARM"][b] == "S")
            nv = sum(1 for b in sub if st["ARM"][b] == "V")
            ng = sum(1 for b in sub if st["ARM"][b] == "G")
            unstable = " *** n=6, UNSTABLE ***" if (nm == "(0, 12]" and
                                                    len(sub) == 6) else ""
            print(f"  {nm:>18s} {len(sub):>4d} {ns:>3d} {nv:>3d} {ng:>3d} "
                  f"{v.mean():>+11.6f} {np.median(v):>+11.6f} "
                  f"{v.min():>+11.6f} {v.max():>+11.6f} {m.mean():>12.6f}"
                  f"{unstable}")
        nulls_only = [b for b in N_ids if b in res]
        print(f"\n  same bins, NULL SET ONLY (the D11/D15 denominator, "
              f"n = {len(nulls_only)} resolved):")
        print(f"  {'bin (d3_CA)':>18s} {'n':>4s} {'mean rho':>11s} "
              f"{'median':>11s} {'min':>11s} {'max':>11s} {'mean|delta|':>12s}")
        for nm, lo, hi, _ in BINS:
            sub = [b for b in nulls_only if binof[b] == nm]
            if not sub:
                print(f"  {nm:>18s} {0:>4d} {'(empty bin)':>11s}")
                continue
            v = np.array([RHO[view][b] for b in sub], float)
            m = np.array([mad[view][b] for b in sub], float)
            print(f"  {nm:>18s} {len(sub):>4d} {v.mean():>+11.6f} "
                  f"{np.median(v):>+11.6f} {v.min():>+11.6f} {v.max():>+11.6f} "
                  f"{m.mean():>12.6f}")
        print(f"\n  full membership of each bin, by name:")
        for nm, lo, hi, _ in BINS:
            sub = sorted([b for b in res if binof[b] == nm])
            print(f"    {nm:>18s} n={len(sub):>3d}: "
                  + (", ".join(f"{b}({st['ARM'][b]},{float(df3.loc[b, 'd3_CA']):.2f})"
                               for b in sub) if sub else "EMPTY"))
        print(f"    d3_CA over the {len(res)} resolved backgrounds: min = "
              f"{min(float(df3.loc[b, 'd3_CA']) for b in res):.3f}, median = "
              f"{np.median([float(df3.loc[b, 'd3_CA']) for b in res]):.3f}, "
              f"max = {max(float(df3.loc[b, 'd3_CA']) for b in res):.3f} A")

    # ---------------------------------------------------------------- D14.1
    p3.banner("D14.1 -- DISCONTINUITY CHECK AT THE 0 A BIN EDGE", "-")
    print("  Difference of means:  mean(rho, Arm S)  -  mean(rho, resolved "
          "nulls in (0, 12])")
    print("  INDEPENDENT-GROUPS BACKGROUND-LEVEL bootstrap 95% CI, "
          f"N_BOOT={N_BOOT}, SEED={SEED}.")
    print("  RESAMPLING UNIT: BACKGROUND.  The two groups are DISJOINT sets of "
          "backgrounds, so each is resampled with replacement independently "
          "and the difference recomputed.  Each background's rho_b is held "
          "FIXED within a draw; nothing is re-derived.")
    print("  *** DESCRIPTIVE COMPARISON OF TWO SMALL SAMPLES.  The (0, 12] "
          "bin is n = 6 AND UNSTABLE.  NO p-VALUE IS COMPUTED. ***")
    near = sorted([b for b in resN if 0.0 < float(df3.loc[b, "d3_CA"]) <= 12.0],
                  key=lambda b: float(df3.loc[b, "d3_CA"]))
    print(f"\n  the (0, 12] resolved-NULL bin, all {len(near)} members:")
    print(f"    {'bg_id':>10s} {'arm':>4s} {'d3_CA':>9s} {'dist_seq':>9s} "
          f"{'mean|delta|':>12s} {'rho (full)':>13s} {'rho (H)':>13s}")
    for b in near:
        print(f"    {b:>10s} {st['ARM'][b]:>4s} {float(df3.loc[b, 'd3_CA']):>9.3f} "
              f"{st['DIST'][b]:>9d} {mad['full'][b]:>12.6f} "
              f"{RHO['full'][b]:>+13.9f} {RHO['H'][b]:>+13.9f}")
    print(f"    d3_CA span = {float(df3.loc[near[0], 'd3_CA']):.3f} to "
          f"{float(df3.loc[near[-1], 'd3_CA']):.3f} A")
    d141 = {}
    for view in p3.VIEWS:
        a = np.array([RHO[view][b] for b in S_ids], float)
        c = np.array([RHO[view][b] for b in near], float)
        diff = float(a.mean() - c.mean())
        rng = np.random.default_rng(SEED)
        draws = np.empty(N_BOOT, float)
        for i in range(N_BOOT):
            ia = rng.integers(0, len(a), len(a))
            ic = rng.integers(0, len(c), len(c))
            draws[i] = a[ia].mean() - c[ic].mean()
        lo, hi, v = p3.pdg.pct_ci(draws)
        d141[view] = dict(a=a, c=c, diff=diff, lo=lo, hi=hi, v=v)
        print(f"\n    [{view}]  mean(rho, Arm S, n={len(a)}) = {a.mean():+.6f}"
              f"   mean(rho, (0,12] nulls, n={len(c)}) = {c.mean():+.6f}")
        print(f"    [{view}]  DIFFERENCE OF MEANS = {diff:+.6f}")
        print(f"    [{view}]  background-level bootstrap 95% CI = "
              f"[{lo:+.6f}, {hi:+.6f}] ({v} usable draws)   "
              f"{'EXCLUDES ZERO' if (lo > 0 or hi < 0) else 'INCLUDES ZERO'}")
        print(f"    [{view}]  *** The (0, 12] bin has n = {len(c)} and is "
              f"labelled UNSTABLE.  This is a description of two small "
              f"samples, not a test of a discontinuity. ***")

    # ---------------------------------------------------------------- D14.2
    p3.banner("D14.2 -- POST-HOC TARGET CHECK", "-")
    print("  *** POST-HOC: this comparison was computed AFTER seeing the data. "
          "It is reproduced here as a check on the task doc's arithmetic and "
          "is labelled POST-HOC wherever it appears. ***")
    seq10 = sorted(N_ids, key=lambda b: (st["DIST"][b], b))[:10]
    print(f"\n  the 10 sequence-nearest nulls (dist_222 ascending, ties by "
          f"ascending bg_id): {seq10}")
    d142 = {}
    for view in p3.VIEWS:
        t = np.array([RHO[view][b] for b in seq10], float)
        s = np.array([RHO[view][b] for b in S_ids], float)
        d142[view] = (t.mean(), s.mean())
        print(f"\n    [{view}]  POST-HOC mean rho of the 10 sequence-nearest "
              f"nulls = {t.mean():+.6f}")
        print(f"    [{view}]  POST-HOC mean rho of Arm S (n = {len(s)}) = "
              f"{s.mean():+.6f}")
        print(f"    [{view}]  POST-HOC difference (Arm S - seq-10 nearest) = "
              f"{s.mean() - t.mean():+.6f}")
    print("\n  RECOMPUTED vs TARGET:")
    for view in p3.VIEWS:
        agree(f"D14.2 mean rho, 10 sequence-nearest nulls ({view})",
              d142[view][0], TGT_SEQ10[view])
    for view in p3.VIEWS:
        agree(f"D14.2 mean rho, Arm S ({view})", d142[view][1], TGT_ARM_S[view])

    # ---------------------------------------------------------------- D14.3
    p3.banner("D14.3 -- FIGURE", "-")
    try:
        import matplotlib                                        # noqa: F401
        HAVE_MPL = True
        MPL_ERR = ""
    except Exception as exc:                                    # noqa: BLE001
        HAVE_MPL = False
        MPL_ERR = f"{type(exc).__name__}: {exc}"
    if HAVE_MPL:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        col = {"S": "tab:orange", "V": "tab:blue", "G": "tab:green"}
        fig, ax = plt.subplots(figsize=(7, 5))
        for arm in ("S", "V", "G"):
            sub = [b for b in res if st["ARM"][b] == arm]
            ax.scatter([float(df3.loc[b, "d3_CA"]) for b in sub],
                       [RHO["full"][b] for b in sub], s=26, label=f"arm {arm}",
                       color=col[arm], alpha=0.85)
        ax.axhline(RHO_A["full"], color="k", ls="--",
                   label=f"A222V rho = {RHO_A['full']:.4f}")
        for b in ("AV_220", "AV_195", "G_P254F"):
            ax.annotate(b, (float(df3.loc[b, "d3_CA"]), RHO["full"][b]),
                        textcoords="offset points", xytext=(4, 4), fontsize=7)
        ax.annotate("A222C", (0.0, RHO["full"]["A222_C"]),
                    textcoords="offset points", xytext=(4, -10), fontsize=7)
        ax.set_xlabel("d3_CA (A), chain-A CA-CA to residue 222")
        ax.set_ylabel("rho_b (full frame)")
        ax.set_title("rho_b vs 3D distance to 222; 11 unresolved excluded, "
                     "never imputed")
        ax.legend(fontsize=8)
        fig.tight_layout()
        out = ROOT / "data/processed/phase2_diagnostics/rho_vs_d3.png"
        fig.savefig(out, dpi=150)
        print(f"  matplotlib imported; wrote {out.relative_to(ROOT)} "
              f"({out.stat().st_size} bytes)")
        print(f"  sha256 = {hashlib.sha256(out.read_bytes()).hexdigest()}")
        print("  *** FIGURE PRODUCED.  A figure is a picture of the numbers "
              "printed above, not evidence of anything on its own. ***")
    else:
        print(f"  *** SKIPPED: matplotlib is not importable "
              f"({MPL_ERR}).")
        print("  Per the task doc rule 9 it is NOT installed.  "
              "data/processed/phase2_diagnostics/rho_vs_d3.png was NOT "
              "written.")
        print("  Every number the figure would have shown is in the D14.0 "
              "bin table above; no result depends on the figure.")

    n_dis = sum(1 for _, ok in checks if not ok)
    print(f"\n  RECOMPUTED vs TARGET: {len(checks) - n_dis}/{len(checks)} "
          f"AGREE, {n_dis} DISAGREE")

    print("\nD14 LIMITATIONS (printed, not only in the docstring):  THE BINS "
          "ARE FIXED IN ADVANCE AND NOT TUNED, BUT THEY ARE STILL BINS, so a "
          "result inside a bin depends on where its edges fall; every bin n is "
          "printed at every use.  The (0, 12] bin has n = 6 and is labelled "
          "UNSTABLE everywhere.  THE BINS ARE NOT MATCHED FOR mean|delta| -- "
          "mean|delta| is printed in every bin precisely so the reader can "
          "see that a distance-bin difference and a shift difference are "
          "confounded in this picture.  D14.1 IS A DESCRIPTIVE COMPARISON OF "
          "TWO SMALL SAMPLES AND NOT A TEST; no p-value is computed for it.  "
          "D14.2 IS POST-HOC AND IS LABELLED SO.  11 unresolved backgrounds "
          "are excluded from every bin, listed by name, and NEVER imputed.  "
          "rho_b for the 96 backgrounds share one y-vector and are mutually "
          "correlated; nothing here models that.  NOTHING FROZEN IS REDEFINED "
          "AND NO OUTCOME WORD LABELS ANY RESULT HERE.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
