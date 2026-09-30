"""Script 146 -- Phase 2 diagnostics III, Task D16e: ARM S UNDER THE JOINT
MODELS, EXACT.  (Descriptive.  Rank fractions, not tests.)

WHY
---
D13 compared A222V to Arm S on raw rho and on D9's shift-only residual.  D16
compared A222V to Arm S under an ISOTONIC distance adjustment, which needs no
functional form.  Neither asked what the PARAMETRIC joint models - the ones
Diagnostics II actually published - predict at distance 0, and how the 18 Arm S
backgrounds, which all sit at exactly distance 0, score under them.  Arm S is
the only distance-matched comparison the design has, and these are the models
whose distance term is an extrapolation.  This task scores Arm S under all of
them exactly, out of sample.

SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as
a label for any result computed here.

PRE-REGISTERED IN THIS DOCSTRING BEFORE THE FIRST RUN
----------------------------------------------------
EXACT FULL-PRECISION FITS -- no 6-dp rounding anywhere, and no hand-typed
coefficients.  All four are refitted here from script 125's own rows via
scripts/lib/phase2_diag3.py, using the same OLS design and the same
exchangeability property Diagnostics II used.  *** NULLS GET LEAVE-ONE-OUT
  RESIDUALS AND A222V IS OUT-OF-SAMPLE, EXACTLY AS SCRIPTS 138 AND 139 DO
  (their `loo_variant` / `loo_joint`), BECAUSE THAT IS WHAT THEIR PUBLISHED
  k COUNTS ARE.  ARM S IS THEN SCORED OUT OF SAMPLE FROM THE ALL-NULLS FIT, SO
  ARM S, THE NULLS AND A222V ARE ALL EXCHANGEABLE WITH ONE ANOTHER. ***

  M1  shift-only              : rho ~ a + c*mean|delta|,            fit on the 78 nulls
  M2  + linear dist_seq       : rho ~ a + c1*mean|delta| + c2*dist_seq,   fit on the 78
  M3  + log1p(dist_seq)       : rho ~ a + c1*mean|delta| + c2*log1p(dist_seq), fit on the 78
  M4  + log1p(d3_CA)          : rho ~ a + c1*mean|delta| + c2*log1p(d3_CA),  fit on the
                                67 RESOLVED nulls only (the 11 unresolved nulls have
                                no d3_CA and are NEVER imputed)

For every model, every view:
  * A222V and all 18 Arm S members are scored OUT OF SAMPLE at their own
    covariates.  Arm S and A222V both sit at distance 0 (position 222), so the
    distance covariate is 0 and log1p(0) = 0 for both.
  * predicted rho at distance 0, and residual r = rho - predicted.
  * Arm S mean and sd of the residual; mean PREDICTED vs mean OBSERVED rho at
    d = 0; and A222V's RANK within Arm S u {A222V} on the residual (rank 1 =
    most negative), as a RANK FRACTION over n = 19.  *** NOT A TEST. ***

GATES (HARD-ish, run FIRST; failure stops this task)
--------------------------------------------------
  E1  M1 reproduces D9's PRIMARY exactly: r_A = -0.066425 (full) / -0.068692 (H)
      to 2e-6.
  E2  M3 reproduces D10a's PRIMARY exactly: r_A = +0.045227 (full) / +0.047030
      (H) to 2e-6, k = 69 / 70.
  E3  M4 reproduces D11.4 exactly: r_A = +0.093681 (full) / +0.098715 (H) to
      2e-6, k = 67 / 67.
  E4  M2 reproduces D10a SENSITIVITY (i): r_A = -0.033711 (full) / -0.035948
      (H) to 2e-6.
  E5  both input sha256s match.

SECOND PART, PRE-REGISTERED
---------------------------
  A222V's RAW-RHO rank among ALL RESOLVED BACKGROUNDS within 20 A of 222, i.e.
  Arm S (18, all at 0 A) plus the resolved nulls in (0, 20].  Reported as:
  n backgrounds in the set, the count at or below A222V, the signed rank, and
  the rank fraction (1 + k)/(1 + n).  *** RANK FRACTIONS, NOT TESTS. ***
  This is the one comparison in the whole session where A222V is compared
  against its own site AND the near spatial neighbourhood together, which is
  the comparison the project's actual claim needs and which nothing else here
  provides.

TARGETS TO CONFIRM (the task doc's, which are Claude's own post-hoc
calculations from PRINTED 6-dp values and are therefore approximate by
construction).  Each is recomputed here and printed beside its target; a
mismatch is reported, never forced.  Note the doc's own framing: these are
POST-HOC numbers.
  * A222V rank 2/19 under all four models.
  * Arm S mean residual: M1 -0.0298, M2 -0.0039, M3 +0.0760, M4 +0.1227 (full).
  * log1p(dist_seq) predicts -0.1412 vs observed Arm S mean -0.0652 (overshoot
    -0.076).
  * within 20 A: 32 backgrounds, 2 at or below A222V (full), 4 (H), i.e. rank
    fractions 3/33 and 5/33.

RESAMPLING UNIT
---------------
NONE.  No bootstrap, no permutation.  N_BOOT / N_PERM are not read by this
script.  Every number is a deterministic OLS fit, a deterministic prediction,
or an exact rank count.

WORDING
-------
GENERIC / BEATS / INDETERMINATE are not used as a label for any result
computed here.  No adjusted p_spec threshold is invoked: this task reports
rank fractions and residuals only, and says "at or below" / "above" only for
the exact beater counts it prints as counts.

LIMITS (AGENTS 6)
-----------------
* Arm S is scored out of sample from a fit on NULLS ONLY, so A222V and Arm S
  are exchangeable with each other.  That is the property that makes the
  comparison meaningful and it is preserved in all four models.
* **These four models all contain a distance term evaluated at 0, a point no
  null occupies** (the M1 exception: it has no distance term).  The predicted
  rho at distance 0 is therefore an EXTRAPOLATION of a fitted surface for M2,
  M3 and M4, and D12's K3 correction applies verbatim: a hat value inside the
  null range does not make a point interpolated.  M3 and M4 are expected to
  predict values below every observed null; the overshoot is printed.
* mean|delta| and rho_b are both functions of the same delta_b: a partial
  control, not an independent one.
* n = 19 for every Arm S rank fraction.  These are rank fractions, not tests.
* Arm S shares the site and differs in substitution, so this bears on
  substitution-specificity WITHIN the site and cannot separate "the residue"
  from "the region".

Usage:
  venv/bin/python3 scripts/146_phase2_diag3_arms_joint.py
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag3 as p3           # noqa: E402

t0 = time.time()
gates = []
checks = []

TOL = 2e-6
# task-doc targets (post-hoc, from printed 6-dp values)
TGT_RANK = 2
TGT_MEANS = {"M1": -0.0298, "M2": -0.0039, "M3": 0.0760, "M4": 0.1227}
TGT_PRED_M3 = -0.1412
TGT_OBS_M3 = -0.0652
TGT_N20 = 32
TGT_K20 = {"full": 2, "H": 4}
TGT_FRAC20 = {"full": 3 / 33, "H": 5 / 33}


def gate(gid, ok, detail):
    gates.append((gid, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")


def agree(label, got, target, tol=TOL, fmt="{:+.6f}"):
    ok = abs(float(got) - float(target)) < tol
    checks.append((label, ok))
    print(f"    {label:<54s} recomputed = {fmt.format(float(got)):>12s}   "
          f"target = {fmt.format(float(target)):>12s}   "
          f"|diff| = {abs(float(got) - float(target)):.3e}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


def agree_int(label, got, target):
    ok = int(got) == int(target)
    checks.append((label, ok))
    print(f"    {label:<54s} recomputed = {str(int(got)):>12s}   "
          f"target = {str(int(target)):>12s}   "
          f"{'AGREE' if ok else '*** DISAGREE ***'}")
    return ok


MODELS = [
    ("M1  shift-only", ["mean|delta|"],
     lambda b, v, st: [st["mad"][v][b]],
     lambda v, st: [st["mad_a"][v]], "n78"),
    ("M2  + linear dist_seq", ["mean|delta|", "dist"],
     lambda b, v, st: [st["mad"][v][b], float(st["DIST"][b])],
     lambda v, st: [st["mad_a"][v], 0.0], "n78"),
    ("M3  + log1p(dist_seq)", ["mean|delta|", "log1p(dist_seq)"],
     lambda b, v, st: [st["mad"][v][b], np.log1p(float(st["DIST"][b]))],
     lambda v, st: [st["mad_a"][v], np.log1p(0.0)], "n78"),
    ("M4  + log1p(d3_CA)", ["mean|delta|", "log1p(d3_CA)"],
     lambda b, v, st: [st["mad"][v][b],
                        np.log1p(float(st["df3"].loc[b, "d3_CA"]))],
     lambda v, st: [st["mad_a"][v], np.log1p(0.0)], "n67"),
]


def main():
    p3.banner("D16e -- ARM S UNDER THE JOINT MODELS, EXACT  (script 146)")
    print("SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word "
          "is used as a label.")
    print("*** RANK FRACTIONS, n = 19.  NOT TESTS.  No p-value is computed "
          "anywhere in this task. ***")
    print("NO 6-dp ROUNDING AND NO HAND-TYPED COEFFICIENTS: all four models "
          "are refitted here at full precision from script 125's own rows.")
    print("RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  N_BOOT / "
          "N_PERM are not read by this script.")
    print("*** THE DOC'S TARGETS FOR THIS TASK ARE ITS OWN POST-HOC "
          "CALCULATIONS FROM PRINTED 6-dp VALUES AND ARE THEREFORE "
          "APPROXIMATE BY CONSTRUCTION.  Each is recomputed and printed beside "
          "its target; a mismatch is reported, never forced. ***")

    sha1 = hashlib.sha256(p3.RHO_TABLE.read_bytes()).hexdigest()
    gate("E5 background_rho_table.csv sha256", sha1 == p3.RHO_TABLE_SHA, sha1)
    sha3 = hashlib.sha256(p3.D3_CSV.read_bytes()).hexdigest()
    gate("E5 background_3d_distance.csv sha256", sha3 == p3.D3_SHA, sha3)

    st = p3.build()
    S_ids, N_ids, resN = st["S_ids"], st["N_ids"], st["resN"]
    RHO, RHO_A = st["RHO"], st["RHO_A"]
    df3 = st["df3"]
    print(f"  Arm S {len(S_ids)} (all position 222, dist_seq 0, d3_CA 0); "
          f"nulls {len(N_ids)}; resolved nulls {len(resN)}")

    # ---- gates on the four fits ------------------------------------------
    p3.banner("GATES -- the four models must reproduce the published "
              "Diagnostics II values exactly before Arm S is scored", "-")
    fitted = {}
    for name, cnames, covb, covA, which in MODELS:
        ids = resN if which == "n67" else N_ids
        for view in p3.VIEWS:
            # LEAVE-ONE-OUT for the nulls, out-of-sample for A222V: this is
            # scripts 138/139's exact construction (their `loo_variant` /
            # `loo_joint`), and it is what their published k counts.  The
            # returned `beta` is the fit over ALL of `ids`, which is the fit
            # Arm S is then scored against.
            r_b, r_A, beta = p3.loo_joint(
                view, RHO, RHO_A, ids,
                lambda b, v, _c=covb: np.asarray(_c(b, v, st), float),
                lambda v, _c=covA: np.asarray(_c(v, st), float))
            k = int(sum(1 for b in ids if r_b[b] <= r_A))
            fitted[(name, view)] = dict(beta=beta, r_A=r_A, k=k, ids=ids,
                                        covb=covb, covA=covA, cnames=cnames)
    g_spec = {"M1  shift-only": (-0.066425, -0.068692, 2, 2),
              "M2  + linear dist_seq": (-0.033711, -0.035948, 9, 10),
              "M3  + log1p(dist_seq)": (+0.045227, +0.047030, 69, 70),
              "M4  + log1p(d3_CA)": (+0.093681, +0.098715, 67, 67)}
    gid = {"M1  shift-only": "E1", "M2  + linear dist_seq": "E4",
           "M3  + log1p(dist_seq)": "E2", "M4  + log1p(d3_CA)": "E3"}
    for name, cnames, covb, covA, which in MODELS:
        tf, th, tkf, tkh = g_spec[name]
        for view, tr, tk in (("full", tf, tkf), ("H", th, tkh)):
            f = fitted[(name, view)]
            gate(f"{gid[name]} {name} r_A ({view})",
                 abs(f["r_A"] - tr) < TOL,
                 f"got {f['r_A']:+.9f} vs {tr:+.6f} "
                 f"|diff|={abs(f['r_A'] - tr):.3e}")
            gate(f"{gid[name]} {name} k ({view})", f["k"] == tk,
                 f"got {f['k']} vs {tk}")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    if n_fail:
        print(f"\n*** {n_fail} GATE(S) FAILED -- STOP D16e. ***")
        import sys as _s
        _s.exit(1)
    print(f"\n  {len(gates)}/{len(gates)} E-gates PASS.  Arm S may be scored.")

    # ---- Arm S scored out of sample --------------------------------------
    p3.banner("ARM S AND A222V SCORED OUT OF SAMPLE AT DISTANCE 0, ALL FOUR "
              "MODELS", "-")
    print("  Arm S and A222V are BOTH out of sample from the null-only fit, "
          "so they are exchangeable with each other.")
    print("  *** D12's K3 CORRECTION APPLIES TO M2, M3 AND M4: all three "
          "evaluate a distance term at 0, a point no null occupies, so their "
          "predicted rho is an EXTRAPOLATION of a fitted surface.  M1 has no "
          "distance term and is not an extrapolation. ***")
    res = {}
    for name, cnames, covb, covA, which in MODELS:
        print(f"\n  ================ {name} ================")
        for view in p3.VIEWS:
            f = fitted[(name, view)]
            pred_A = p3.predict(f["beta"], f["covA"](view, st))
            r_A = RHO_A[view] - pred_A
            predS = {b: p3.predict(f["beta"], f["covb"](b, view, st))
                     for b in S_ids}
            rS = {b: RHO[view][b] - predS[b] for b in S_ids}
            obsS = np.array([RHO[view][b] for b in S_ids], float)
            k = int(sum(1 for b in S_ids if rS[b] <= r_A))
            rank = 1 + int(sum(1 for b in S_ids if rS[b] < r_A))
            frac = (1 + k) / (1 + len(S_ids))
            mn = min(resN if which == "n67" else N_ids,
                     key=lambda b: RHO[view][b])
            res[(name, view)] = dict(pred_A=pred_A, r_A=r_A, predS=predS,
                                     rS=rS, k=k, rank=rank, frac=frac,
                                     mean_r=float(np.mean(list(rS.values()))),
                                     sd_r=float(np.std(list(rS.values()),
                                                       ddof=1)),
                                     mean_pred=float(obsS.mean() - np.mean(
                                         list(rS.values()))),
                                     mean_obs=float(obsS.mean()),
                                     minnull=mn,
                                     minnull_rho=float(RHO[view][mn]))
            print(f"\n    [{view}]  OLS rho ~ " + "  ".join(
                f"{c}*{f['beta'][i + 1]:+.6f}" for i, c in enumerate(cnames))
                + f"  intercept {f['beta'][0]:+.6f}   (fit on n = "
                  f"{len(f['ids'])})")
            print(f"    {'bg_id':>10s} {'mean|delta|':>12s} {'rho (obs)':>13s} "
                  f"{'predicted at d=0':>18s} {'residual':>12s} {'<= r_A?':>8s}")
            for b in sorted(S_ids, key=lambda z: rS[z]):
                print(f"    {b:>10s} {st['mad'][view][b]:>12.6f} "
                      f"{RHO[view][b]:>+13.9f} {predS[b]:>+18.6f} "
                      f"{rS[b]:>+12.6f} "
                      f"{'YES' if rS[b] <= r_A else 'no':>8s}")
            print(f"    A222V    {st['mad_a'][view]:>12.6f} "
                  f"{RHO_A[view]:>+13.9f} {pred_A:>+18.6f} {r_A:>+12.6f}   "
                  f"(the residual every Arm S member is compared against)")
            print(f"    ARM S mean residual = {res[(name, view)]['mean_r']:+.6f}"
                  f"   sd = {res[(name, view)]['sd_r']:.6f}")
            print(f"    mean PREDICTED rho at d=0 = "
                  f"{res[(name, view)]['mean_pred']:+.6f}   vs   mean OBSERVED "
                  f"rho at d=0 = {res[(name, view)]['mean_obs']:+.6f}   "
                  f"overshoot (predicted - observed) = "
                  f"{res[(name, view)]['mean_pred'] - res[(name, view)]['mean_obs']:+.6f}")
            print(f"    most negative OBSERVED null rho on this view = "
                  f"{mn} {res[(name, view)]['minnull_rho']:+.6f}"
                  f"   (A222V's predicted rho at d=0 vs that: "
                  f"{pred_A:+.6f} -> "
                  f"{'BELOW every observed null' if pred_A < res[(name, view)]['minnull_rho'] else 'not below every observed null'})")
            print(f"    A222V rank within Arm S u {{A222V}} on the residual = "
                  f"{rank}/{len(S_ids) + 1}   rank fraction = {frac:.4f}   "
                  f"*** RANK FRACTION OVER n = 19, NOT A TEST ***")

    # ---- targets ----------------------------------------------------------
    p3.banner("RECOMPUTED vs TARGET (the doc's targets are POST-HOC and from "
              "printed 6-dp values)", "-")
    print("  Arm S mean residual (full frame):")
    for name, *_ in MODELS:
        agree(f"Arm S mean residual, {name} (full)",
              res[(name, "full")]["mean_r"], TGT_MEANS[name[:2]], 5e-5)
    print("  A222V rank within Arm S u {A222V}:")
    for name, *_ in MODELS:
        for view in p3.VIEWS:
            agree_int(f"A222V rank, {name} ({view})",
                      res[(name, view)]["rank"], TGT_RANK)
    print("  log1p(dist_seq) prediction vs observation at d = 0 (full):")
    agree("M3 mean predicted rho at d=0 (full)",
          res[("M3  + log1p(dist_seq)", "full")]["mean_pred"], TGT_PRED_M3, 5e-5)
    agree("M3 mean observed Arm S rho at d=0 (full)",
          res[("M3  + log1p(dist_seq)", "full")]["mean_obs"], TGT_OBS_M3, 5e-5)
    agree("M3 overshoot, predicted - observed (full)",
          res[("M3  + log1p(dist_seq)", "full")]["mean_pred"]
          - res[("M3  + log1p(dist_seq)", "full")]["mean_obs"],
          TGT_PRED_M3 - TGT_OBS_M3, 5e-5)
    n_dis = sum(1 for _, ok in checks if not ok)
    print(f"    -> {len(checks) - n_dis}/{len(checks)} AGREE, {n_dis} DISAGREE")

    # ---- second part: within 20 A ----------------------------------------
    p3.banner("A222V's RAW-RHO RANK AMONG ALL RESOLVED BACKGROUNDS WITHIN 20 A "
              "OF 222", "-")
    print("  The set = Arm S (18, all at d3_CA = 0) + the resolved NULLS in "
          "(0, 20].  *** RANK FRACTIONS, NOT TESTS. ***")
    d20 = {}
    for view in p3.VIEWS:
        near = sorted([b for b in resN
                       if 0.0 < float(df3.loc[b, "d3_CA"]) <= 20.0],
                      key=lambda b: float(df3.loc[b, "d3_CA"]))
        sub = list(S_ids) + near
        v = np.array([RHO[view][b] for b in sub], float)
        k = int((v <= RHO_A[view]).sum())
        rank = 1 + int((v < RHO_A[view]).sum())
        frac = (1 + k) / (1 + len(sub))
        ao = sorted([b for b in sub if RHO[view][b] <= RHO_A[view]])
        d20[view] = dict(sub=sub, k=k, rank=rank, frac=frac, ao=ao)
        print(f"\n  [{view}]  n backgrounds in the set = {len(sub)} "
              f"(Arm S {len(S_ids)} + resolved nulls in (0, 20] = {len(near)})")
        print(f"  [{view}]  at or below A222V: k = {k}  ->  {', '.join(ao)}")
        print(f"  [{view}]  A222V signed rank = {rank}/{len(sub)}   rank "
              f"fraction (1 + {k})/(1 + {len(sub)}) = {frac:.4f}   "
              f"*** RANK FRACTION, NOT A TEST ***")
        print(f"    the {len(near)} resolved nulls in (0, 20] by d3_CA: "
              + ", ".join(f"{b}({float(df3.loc[b, 'd3_CA']):.2f})" for b in near))
    print("\n  RECOMPUTED vs TARGET (POST-HOC, from printed 6-dp values):")
    for view in p3.VIEWS:
        agree_int(f"n backgrounds within 20 A ({view})",
                  len(d20[view]["sub"]), TGT_N20)
        agree_int(f"n at or below A222V within 20 A ({view})",
                  d20[view]["k"], TGT_K20[view])
        agree(f"rank fraction within 20 A ({view})", d20[view]["frac"],
              TGT_FRAC20[view], 5e-5, "{:.4f}")

    p3.banner("D16e GATE TABLE", "-")
    for gid2, ok, detail in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid2}: {detail}")
    n_fail = sum(1 for _, ok, _ in gates if not ok)
    print(f"\n  E-gates: {'PASS' if not n_fail else 'FAIL'} "
          f"({len(gates) - n_fail}/{len(gates)}).")

    print("\nD16e LIMITATIONS (printed, not only in the docstring):  Arm S "
          "AND A222V ARE SCORED OUT OF SAMPLE FROM A NULL-ONLY FIT, so they "
          "are exchangeable WITH EACH OTHER; that is the property the "
          "comparison relies on and it holds in all four models.  M2, M3 AND "
          "M4 EVALUATE A DISTANCE TERM AT 0, A POINT NO NULL OCCUPIES, SO "
          "THEIR PREDICTED RHO IS AN EXTRAPOLATION OF A FITTED SURFACE -- "
          "D12's K3 CORRECTION APPLIES VERBATIM AND A HAT VALUE INSIDE THE "
          "NULL RANGE DOES NOT MAKE A POINT INTERPOLATED.  M1 HAS NO DISTANCE "
          "TERM AND IS NOT AN EXTRAPOLATION.  mean|delta| AND rho_b ARE BOTH "
          "FUNCTIONS OF THE SAME delta_b: A PARTIAL CONTROL, NOT AN "
          "INDEPENDENT ONE.  EVERY RANK FRACTION HERE IS OVER n = 19 (Arm S) "
          "or n = 33 (within 20 A) AND IS A RANK FRACTION, NOT A TEST; NO "
          "p-VALUE AND NO CI IS COMPUTED.  ARM S SHARES THE SITE AND DIFFERS "
          "IN SUBSTITUTION, SO THIS BEARS ON SUBSTITUTION-SPECIFICITY WITHIN "
          "THE SITE AND CANNOT SEPARATE 'THE RESIDUE' FROM 'THE REGION'.  THE "
          "TASK DOC'S TARGETS FOR THIS TASK ARE ITS OWN POST-HOC CALCULATIONS "
          "FROM PRINTED 6-dp VALUES; MATCHES AT 5e-5 ARE REPORTED AS MATCHES "
          "AND NOTHING WAS TUNED.  NOTHING FROZEN IS REDEFINED.")
    print(f"Elapsed {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
