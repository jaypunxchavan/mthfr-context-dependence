"""
Script 89 (Task N4): does the N2 calibration change AC4's seed-instability
finding?

PRE-REGISTERED (written before running; rule fixed here — AGENTS s0/s6)

N4a — the five ESM-1v member score CSVs (NOT weights) must exist:
  data/processed/task_AC4_esm1v_member{1..5}_scores.csv, columns
  position, wt_aa, mut_aa, wt_logodds, av_logodds, delta. Missing file ->
  proceed with what exists and log exactly which are missing; row-count
  mismatch or join failure -> exit 1 (script 86's R4 discipline).

N4b — apply the SAME calibration, fit ONCE (task doc: "do not refit
  per-seed, since Nambiar's own protocol fits the calibration once and
  applies it broadly"):
      delta_cal_m{k} = phi2(av_logodds) - phi1(wt_logodds)
  with phi1/phi2 = script 87's fitted parameters (loaded, never refit)
  and phi = script 87's function (single implementation). NOTE/DISCLOSURE:
  these curves were fit on ESM-2's score range; the script prints the
  fraction of each member's score range lying outside the ESM-2
  calibration x-range so any out-of-domain application is visible, not
  hidden. This is the task's explicit instruction; no alternative
  scaling was tried.

N4c — replicate AC4d's raw-score machinery on the calibrated scores,
  exactly (script 86's summ section, quoted):
  - analysis base: task32_analysis_table.csv dropna(own_e_b,
    GI_folinate_independent, delta_esm) == 10,757 rows / 654 positions
    (gated, as script 86 gates it);
  - join each member on ["position","mut_aa"], validate 1:1, wt_aa
    label match, zero unmatched (script 86's R4, verbatim);
  - R6-analogue: per-member position-cluster-bootstrap rho of
    delta_cal_m{k} vs own_e_b (primary) and GI (secondary), N_BOOT, SEED=0;
  - AC2a's convention ("Compute the correlation between delta_150M and
    delta_650M across the same variants (not just what fraction agree in
    sign)"): pairwise member Spearman on the CALIBRATED deltas (10 pairs,
    min/median/max) — the cross-member agreement proper;
  - the five correlations themselves (AC4c: "cross-member agreement on
    the delta-vs-e.b correlations themselves"): signs, mean/sd/min/max,
    CIs excluding zero — R7c-analogue;
  - RAW references recomputed in this same script from the same files
    (pairwise on raw delta and raw wt; per-member raw rhos also
    cross-checked against task_AC4_esm1v_summary.csv).
  CHECK C1 (monotone identity): pairwise Spearman of phi1(wt_logodds)
  across members must equal pairwise Spearman of raw wt_logodds to
  |diff| < 1e-12 (phi1 is strictly increasing, so ranks cannot change).
  Failure -> exit 1. This doubles as a machinery test.

N4d — VERDICT RULE, fixed before running:
  Calibration "IMPROVES cross-seed agreement" iff BOTH:
    (i)  median pairwise member Spearman on CALIBRATED deltas >= 2x the
         median on RAW deltas (raw median recomputed here; AC4d printed
         0.084365), AND
    (ii) all five calibrated delta-vs-own_e_b rhos share ONE sign
         (raw AC4d state: 4 negative / 1 positive = mixed =
         SEED-NOISE branch).
  Otherwise NOT IMPROVED (unchanged or worse), stated plainly as
  evidence that the instability is not a calibration-scale artifact.
  Both components print regardless of outcome; no threshold is tuned
  after seeing results. Effect sizes print alongside significance.

LIMITATIONS printed with results: ESM-1v vs ESM-2 score-scale mismatch
quantified (above), calibration fit for ESM-2 not ESM-1v (per the task's
fit-once instruction), and Spearman-based agreement (rank) only.
"""
import sys, os, warnings, importlib.util
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.stats import position_cluster_bootstrap, _spearman

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

_spec = importlib.util.spec_from_file_location(
    "n2_calibration", ROOT / "scripts" / "87_n2_calibration_fit.py")
_n2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_n2)
phi = _n2.phi

RAW_DELTA_PAIR_MEDIAN_AC4D = 0.084365   # AC4d's printed raw value; recomputed below


def log(msg=""):
    print(msg, flush=True)


if __name__ == "__main__":
    # ---- N4a: files exist --------------------------------------------------
    log("=" * 74)
    log("N4a  MEMBER SCORE FILES (weights are deleted; these are outputs)")
    log("=" * 74)
    members = {}
    for k in range(1, 6):
        p = PROC / f"task_AC4_esm1v_member{k}_scores.csv"
        if not p.exists():
            log(f"  member {k}: MISSING at {p} — proceeding with what exists "
                f"(N4a rule), will log exactly which are missing.")
            continue
        m = pd.read_csv(p)
        members[k] = m
        log(f"  member {k}: {p.name} — {len(m)} rows, "
            f"cols={list(m.columns)}")
    if not members:
        log("*** N4a: no member CSVs at all — BLOCKED for this task. ***")
        sys.exit(1)
    ref_rows = len(members[min(members)])
    for k, m in members.items():
        if len(m) != ref_rows:
            log(f"  member {k} rows != member {min(members)} rows ({ref_rows}) — exit")
            sys.exit(1)
    n_members = len(members)
    log(f"  {n_members}/5 member CSVs present, all {ref_rows} rows.")

    # ---- analysis base (script 86's R4 discipline) ------------------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    log(f"\nanalysis base from task32: {len(base)} rows / "
        f"{base['position'].nunique()} positions (expect 10757 / 654)")
    if (len(base), base["position"].nunique()) != (10757, 654):
        log("analysis base differs from script 32's published set — exit")
        sys.exit(1)

    # ---- calibration params (fit once; never refit — N4b) -----------------
    par = pd.read_csv(PROC / "task87_calibration_params.csv")
    b1, c1 = float(par.loc[par.arm == "phi1_wt", "b"].iloc[0]), \
        float(par.loc[par.arm == "phi1_wt", "c"].iloc[0])
    b2, c2 = float(par.loc[par.arm == "phi2_a222v", "b"].iloc[0]), \
        float(par.loc[par.arm == "phi2_a222v", "c"].iloc[0])
    log(f"phi1 b={b1:.6f} c={c1:.6f}; phi2 b={b2:.6f} c={c2:.6f} "
        f"(loaded from task87_calibration_params.csv — NOT refit, N4b)")

    # ESM-2 calibration x-range (for the out-of-domain disclosure)
    e2 = pd.read_csv(PROC / "task32_analysis_table.csv")
    xlo_w, xhi_w = e2["esm2_score"].min(), e2["esm2_score"].max()
    xlo_a, xhi_a = e2["esm2_score_a222v_bg"].min(), e2["esm2_score_a222v_bg"].max()
    log(f"ESM-2 calibration x-ranges: WT [{xlo_w:.3f}, {xhi_w:.3f}]  "
        f"A222V [{xlo_a:.3f}, {xhi_a:.3f}]")

    # ---- join + calibrated deltas ----------------------------------------
    joined = {}
    for k, m in members.items():
        j = base.merge(m[["position", "wt_aa", "mut_aa",
                          "wt_logodds", "av_logodds", "delta"]],
                       on=["position", "mut_aa"], how="left", validate="1:1")
        miss = int(j["delta"].isna().sum())
        if miss:
            log(f"member {k}: {miss} base rows unmatched — exit (R4)")
            sys.exit(1)
        if not (j["wt_aa_x"] == j["wt_aa_y"]).all():
            log(f"member {k}: wt_aa label mismatch vs base — exit")
            sys.exit(1)
        j["delta_cal_m"] = phi(j["av_logodds"].to_numpy(), b2, c2) - \
                           phi(j["wt_logodds"].to_numpy(), b1, c1)
        j["wt_cal_m"] = phi(j["wt_logodds"].to_numpy(), b1, c1)
        joined[k] = j
    log(f"R4 join: all {n_members} members cover the base exactly "
        f"({len(joined[min(joined)])} rows / "
        f"{joined[min(joined)]['position'].nunique()} positions)")

    # out-of-domain disclosure
    for k, j in joined.items():
        fw = float(((j["wt_logodds"] < xlo_w) | (j["wt_logodds"] > xhi_w)).mean())
        fa = float(((j["av_logodds"] < xlo_a) | (j["av_logodds"] > xhi_a)).mean())
        log(f"  member {k} score range: wt [{j['wt_logodds'].min():+.3f}, "
            f"{j['wt_logodds'].max():+.3f}] av [{j['av_logodds'].min():+.3f}, "
            f"{j['av_logodds'].max():+.3f}]  "
            f"outside ESM-2 x-range: wt {100*fw:.1f}% / av {100*fa:.1f}%")

    # ---- C1: monotone identity check --------------------------------------
    def pair_spearman(colfn, ks):
        vals = []
        for i in range(len(ks)):
            for t in range(i + 1, len(ks)):
                vals.append(_spearman(colfn(ks[i]), colfn(ks[t])))
        return np.array(vals)

    ks = sorted(joined)
    raw_wt_pairs = pair_spearman(lambda k: joined[k]["wt_logodds"].to_numpy(), ks)
    cal_wt_pairs = pair_spearman(lambda k: joined[k]["wt_cal_m"].to_numpy(), ks)
    d_wt = float(np.abs(raw_wt_pairs - cal_wt_pairs).max())
    log("\nC1  MONOTONE IDENTITY (phi1 strictly increasing => WT-pair ranks "
        "unchanged): max|diff| = %.3e  %s" % (d_wt, "PASS" if d_wt < 1e-12 else "FAIL"))
    if d_wt >= 1e-12:
        log("*** C1 FAIL — machinery broken. Stop. ***")
        sys.exit(1)

    # ---- raw references ----------------------------------------------------
    raw_dl_pairs = pair_spearman(lambda k: joined[k]["delta"].to_numpy(), ks)
    cal_dl_pairs = pair_spearman(lambda k: joined[k]["delta_cal_m"].to_numpy(), ks)
    log(f"\nR7 (AC2a convention, 10 pairs) member-pair Spearman:")
    log(f"  RAW    delta: min={raw_dl_pairs.min():.6f} "
        f"median={np.median(raw_dl_pairs):.6f} max={raw_dl_pairs.max():.6f}")
    log(f"  RAW    wt   : min={raw_wt_pairs.min():.6f} "
        f"median={np.median(raw_wt_pairs):.6f} max={raw_wt_pairs.max():.6f}  "
        f"(AC4d printed median 0.882637)")
    log(f"  CALIB  delta: min={cal_dl_pairs.min():.6f} "
        f"median={np.median(cal_dl_pairs):.6f} max={cal_dl_pairs.max():.6f}")
    log(f"  raw delta-pair median recomputed = {np.median(raw_dl_pairs):.6f} "
        f"(AC4d printed {RAW_DELTA_PAIR_MEDIAN_AC4D:.6f})")
    raw_med = float(np.median(raw_dl_pairs))
    cal_med = float(np.median(cal_dl_pairs))

    # ---- per-member rhos (R6-analogue, raw and calibrated) ----------------
    raw_ref = pd.read_csv(PROC / "task_AC4_esm1v_summary.csv")
    rows = []
    log("\n" + "=" * 74)
    log(f"N4c  PER-MEMBER delta-vs-e.b rhos (position-cluster bootstrap, "
        f"N_BOOT={N_BOOT}, SEED={SEED})")
    log("=" * 74)
    for k in ks:
        d = joined[k]
        for tgt, label in [("own_e_b", "primary"),
                           ("GI_folinate_independent", "secondary")]:
            rc = position_cluster_bootstrap(d, "position", "delta_cal_m", tgt,
                                            n_boot=N_BOOT, seed=SEED)
            rr = raw_ref[(raw_ref["member"] == k) &
                         (raw_ref["target_col"] == tgt)].iloc[0]
            log(f"  member {k} {label}: raw rho={rr['observed_rho']:+.6f} "
                f"CI=[{rr['ci_lo']:+.6f},{rr['ci_hi']:+.6f}] p={rr['p_boot']:.4f}  |  "
                f"CAL rho={rc['observed_rho']:+.6f} "
                f"CI=[{rc['ci_lo']:+.6f},{rc['ci_hi']:+.6f}] p={rc['p_boot']:.4f}")
            rows.append({"member": k, "target": label, "arm": "calibrated",
                         "rho": rc["observed_rho"], "ci_lo": rc["ci_lo"],
                         "ci_hi": rc["ci_hi"], "p_boot": rc["p_boot"],
                         "n": rc["n_rows"]})
            rows.append({"member": k, "target": label, "arm": "raw",
                         "rho": float(rr["observed_rho"]),
                         "ci_lo": float(rr["ci_lo"]),
                         "ci_hi": float(rr["ci_hi"]),
                         "p_boot": float(rr["p_boot"]), "n": np.nan})

    # ---- R7c: the five rhos themselves ------------------------------------
    prim = [r for r in rows if r["target"] == "primary" and r["arm"] == "calibrated"]
    rhos_c = [r["rho"] for r in prim]
    excl_c = sum(1 for r in prim if r["ci_lo"] > 0 or r["ci_hi"] < 0)
    raw_p = raw_ref[raw_ref["target"] == "primary"].sort_values("member")
    rhos_r = raw_p["observed_rho"].tolist()
    log("\nR7c the five delta-vs-own-e.b rhos:")
    log(f"  RAW       : {[f'{r:+.6f}' for r in rhos_r]}")
    log(f"  CALIBRATED: {[f'{r:+.6f}' for r in rhos_c]}")
    log(f"  raw       : mean={np.mean(rhos_r):+.6f} sd={np.std(rhos_r, ddof=1):.6f} "
        f"signs {sum(r>0 for r in rhos_r)} pos / {sum(r<0 for r in rhos_r)} neg")
    log(f"  calibrated: mean={np.mean(rhos_c):+.6f} sd={np.std(rhos_c, ddof=1):.6f} "
        f"min={min(rhos_c):+.6f} max={max(rhos_c):+.6f}; "
        f"CIs excluding zero: {excl_c}/{len(rhos_c)}; "
        f"signs {sum(r>0 for r in rhos_c)} pos / {sum(r<0 for r in rhos_c)} neg")

    # ---- N4d verdict (rule fixed in this docstring) -----------------------
    same_sign = all(r > 0 for r in rhos_c) or all(r < 0 for r in rhos_c)
    cond_i = cal_med >= 2 * raw_med
    log("\n" + "=" * 74)
    log("N4d  VERDICT (rule fixed in the docstring before running)")
    log("=" * 74)
    log(f"  (i) delta-pair median: raw={raw_med:.6f} cal={cal_med:.6f} "
        f"(need cal >= 2x raw = {2*raw_med:.6f}): "
        f"{'MET' if cond_i else 'NOT MET'}")
    log(f"  (ii) all five calibrated rhos one sign: "
        f"{'MET' if same_sign else 'NOT MET'} "
        f"({sum(r>0 for r in rhos_c)} pos / {sum(r<0 for r in rhos_c)} neg)")
    improved = cond_i and same_sign
    if improved:
        log("  -> IMPROVED: calibration improves cross-seed agreement "
            "(raw-scale noise was inflating apparent instability).")
    else:
        log("  -> NOT IMPROVED: calibration does NOT improve cross-seed "
            "agreement — the instability is not a calibration-scale artifact.")

    out = PROC / "task89_n4_results.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"\nSaved to {out}")

    log("\nLIMITATIONS (printed with the results — AGENTS s6):")
    log("  - phi1/phi2 were fit on ESM-2's scores and applied to ESM-1v's")
    log("    scale per the task's fit-once instruction; out-of-domain")
    log("    fractions are printed above, not hidden.")
    log("  - agreement is rank-based (Spearman); magnitudes not compared.")
    log("  - raw per-member CIs are quoted from task_AC4_esm1v_summary.csv")
    log("    (AC4's run), not recomputed, so raw and calibrated arms use the")
    log("    same rows and bootstrap convention (seed 0).")
    log("\nSCRIPT 89 COMPLETE — rc=0.")
    sys.exit(0)
