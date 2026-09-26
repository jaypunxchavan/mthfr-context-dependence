"""
Task A1 (reliability-and-decompositions): the five-member ensemble-mean
delta run -- never computed before this script.

PRE-REGISTRATION (written BEFORE any ensemble result was seen; AGENTS.md
sec 6). Components visible at pre-registration time: the five members'
per-member rhos (task_AC4_esm1v_summary.csv, printed by AC4), AC4's
cross-member delta agreement, and the task doc's given prediction. The
ensemble rho itself had NOT been computed anywhere on disk when this
docstring was written.

WHAT (A1a)
---------
delta_ens(v) = arithmetic mean of the five ESM-1v members' delta columns
for variant v, i.e. delta_ens(v) = (delta_1 + delta_2 + delta_3 +
delta_4 + delta_5)/5, with each delta_k = av_logodds - wt_logodds as
scored by script 86 (data/processed/task_AC4_esm1v_member{1..5}_
scores.csv). Pure arithmetic on existing columns: NO model load, NO GPU.

ANALYSIS SET (identical to AC4's, gates enforce it)
---------------------------------------------------
base = task32_analysis_table.csv dropped to rows with non-null own_e_b,
GI_folinate_independent, delta_esm -> must be 10,757 rows / 654
positions (exit 1 otherwise, same as script 86). Each member joined
left on [position, mut_aa] with validate="1:1"; zero unmatched rows and
exact wt_aa label match required (script 86's R4 gate, copied).

STATISTICS (A1b), pre-registered
--------------------------------
Primary: rho = Spearman(delta_ens, own_e_b).
CI: position-cluster bootstrap (scripts.lib.stats.position_cluster_
bootstrap, cluster = position, N_BOOT draws, seed 0) -- positions, not
rows (AGENTS.md sec 3).
Null: POSITION-level sign-flip ASSOCIATION null on delta_ens
(N_PERM draws, rng seed 2). Identity checks FIRST (AGENTS.md sec 4):
all-+1 must reproduce observed to <1e-12 and all--1 its exact negation,
else sys.exit(1). Null mean and 3-SE centring reported alongside p.

PREDICTION TEST (pre-registered verdict rule, fixed before running)
-------------------------------------------------------------------
The task doc (RELIABILITY_AND_DECOMPOSITIONS.md L70-73) gives the
Spearman-Brown-predicted ensemble value as ~-0.030. That number is
reproducible from components already on disk -- recomputed here as
context, before the ensemble rho exists:

  mean of AC4's five primary rhos = -0.015588096011510361
    (task_AC4_esm1v_summary.csv, target=own_e_b)
  r_bar = AC4's cross-member delta agreement, median of the 10 member
    pairs = 0.084365 (CLOSEOUT_LOG [AC4] R7: "min=0.003314
    median=0.084365 max=0.162631 (10 pairs)"; same value reproduced
    exactly by CALIBRATION_LOG [N4] and script 89's constant)
  Spearman-Brown for k=5 parallel measures:
    rho_ens_pred = mean_single * sqrt(k / (1 + (k-1)*r_bar))
                 = -0.015588096 * sqrt(5 / (1 + 4*0.084365))
                 = -0.0301  (rounds to the doc's ~-0.030)

VERDICT RULE (no retuning after results):
  "the Spearman-Brown prediction HOLDS"  iff
      (a) observed rho < 0, AND
      (b) -0.030 lies inside the 95% position-cluster CI of the
          observed rho.
  Otherwise "the prediction FAILS". Additionally reported, as
  descriptive context (not part of the verdict): whether
  |observed| exceeds the mean |single-member rho| (did averaging
  strengthen the association at all), and the five per-member rhos
  next to the ensemble value.

LIMITATIONS (printed with the result, AGENTS.md sec 6)
------------------------------------------------------
- SCOPE: this is an ESM-1v result. The five members are genuine seed
  replicates of ONE architecture (task doc A3); nothing here measures
  ESM-2 seed stability, and no ESM-2 seed replicates exist.
- The Spearman-Brown formula assumes tau-equivalent parallel measures;
  the five members are different checkpoints, not interchangeable
  forms, so the prediction is a heuristic benchmark, not a theorem.
- r_bar is the MEDIAN of only 10 pairwise correlations.
- Single analysis frame (n=10,757 / 654 positions), inherited from
  script 32; no multiple-comparison claim is made for this single
  pre-registered test.

Run:  SMOKE=1 N_BOOT=500 N_PERM=500 venv/bin/python3 scripts/90_...
      then full: N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/90_...
Output: data/processed/task90_a1_ensemble_mean.csv
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import position_cluster_bootstrap, _spearman

# ---- house env conventions (AGENTS.md sec 1) ----
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = 0
SMOKE = os.environ.get("SMOKE", "") == "1"

REPO = Path(__file__).resolve().parents[1]
PROC = REPO / "data" / "processed"
T32 = PROC / "task32_analysis_table.csv"
MEMBERS = [PROC / f"task_AC4_esm1v_member{k}_scores.csv" for k in range(1, 6)]
SUMMARY = PROC / "task_AC4_esm1v_summary.csv"

# constants cited in the pre-registration (do not re-fit, do not tune)
PREDICTION = -0.030          # task doc L72, Spearman-Brown-predicted value
R_BAR = 0.084365             # AC4 R7 cross-member delta agreement (median)
K = 5


def log(msg=""):
    print(msg, flush=True)


def main():
    tag = "SMOKE=True" if SMOKE else "SMOKE=False"
    log(f"A1 -- FIVE-MEMBER ENSEMBLE-MEAN DELTA vs own_e_b (scripts/90) "
        f"{tag} N_BOOT={N_BOOT} N_PERM={N_PERM}")

    # ---- analysis base (script 86's exact convention) ----
    t32 = pd.read_csv(T32)
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    log(f"analysis base from task32: {len(base)} rows / "
        f"{base['position'].nunique()} positions (expect 10757 / 654)")
    if (len(base), base["position"].nunique()) != (10757, 654):
        log("analysis base differs from script 32's published set -- exit")
        sys.exit(1)

    # ---- load + join the five members (script 86's R4 gate, copied) ----
    joined = []
    ref_rows = None
    for k, p in enumerate(MEMBERS, start=1):
        if not p.exists():
            log(f"missing {p} -- exit")
            sys.exit(1)
        m = pd.read_csv(p)
        if ref_rows is None:
            ref_rows = len(m)
        if len(m) != ref_rows:
            log(f"member {k} has {len(m)} rows != member 1's {ref_rows} -- exit")
            sys.exit(1)
        j = base.merge(m[["position", "wt_aa", "mut_aa", "delta"]],
                       on=["position", "mut_aa"], how="left",
                       suffixes=("", f"_m{k}"), validate="1:1")
        miss = j["delta"].isna().sum()
        if miss:
            log(f"member {k}: {miss} base rows unmatched -- exit (R4)")
            sys.exit(1)
        if not (j["wt_aa"] == j[f"wt_aa_m{k}"]).all():
            log(f"member {k}: wt_aa label mismatch vs base -- exit")
            sys.exit(1)
        joined.append(j["delta"].rename(f"delta_m{k}"))
        log(f"member {k}: joined, {len(j)} rows, mean delta = "
            f"{j['delta'].mean():+.6f}")

    frame = pd.concat([base[["position", "own_e_b"]].reset_index(drop=True)]
                      + [s.reset_index(drop=True) for s in joined], axis=1)
    frame["delta_ens"] = frame[[f"delta_m{k}" for k in range(1, 6)]].mean(axis=1)
    log(f"A1a ensemble built: {len(frame)} rows / "
        f"{frame['position'].nunique()} positions, "
        f"delta_ens mean={frame['delta_ens'].mean():+.6f} "
        f"sd={frame['delta_ens'].std():.6f}")

    # ---- reference: per-member rhos already on disk (AC4) ----
    summ = pd.read_csv(SUMMARY)
    prim = summ[summ["target"] == "primary"].sort_values("member")
    log("\nreference -- AC4's five per-member primary rhos (on disk):")
    for _, r in prim.iterrows():
        log(f"  member {int(r['member'])}: rho={r['observed_rho']:+.6f} "
            f"CI=[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}] p={r['p_report']}")
    mean_single = float(prim["observed_rho"].mean())
    sb = mean_single * np.sqrt(K / (1 + (K - 1) * R_BAR))
    log(f"  mean single-member rho = {mean_single:+.9f}")
    log(f"  Spearman-Brown recompute: {mean_single:+.9f} * "
        f"sqrt({K}/(1+{K-1}*{R_BAR})) = {sb:+.4f} "
        f"(task doc's given prediction: {PREDICTION})")

    # ---- A1b primary: cluster bootstrap CI + p ----
    b = position_cluster_bootstrap(frame, "position", "delta_ens", "own_e_b",
                                   n_boot=N_BOOT, seed=SEED)
    obs = float(b["observed_rho"])
    p_str = (f"<1/{N_BOOT}" if b["p_boot"] == 0 else f"{b['p_boot']:.4f}")
    log(f"\nPRIMARY: rho(delta_ens, own_e_b) = {obs:+.6f} "
        f"CI=[{b['ci_lo']:+.6f}, {b['ci_hi']:+.6f}] p_boot={p_str} "
        f"(position-cluster, N_BOOT={N_BOOT}, seed={SEED})")

    # ---- A1b null: position-level sign flip, identity-checked (sec 4) ----
    pos_codes, _ = pd.factorize(frame["position"])
    n_pos = len(np.unique(pos_codes))
    x = frame["delta_ens"].to_numpy()
    y = frame["own_e_b"].to_numpy()
    ident = _spearman(x * np.ones(n_pos)[pos_codes], y)
    if not abs(ident - obs) < 1e-12:
        log(f"    *** IDENTITY CHECK FAILED: |{ident:.12f} - {obs:.12f}| "
            f">= 1e-12. sys.exit(1)")
        sys.exit(1)
    neg = _spearman(x * (-np.ones(n_pos))[pos_codes], y)
    if not abs(neg + obs) < 1e-12:
        log(f"    *** IDENTITY CHECK FAILED (all -1): |{neg:.12f} + "
            f"{obs:.12f}| >= 1e-12. sys.exit(1)")
        sys.exit(1)
    log(f"    identity: all+1 == obs ({ident:+.12f}), "
        f"all-1 == -obs ({neg:+.12f})  -> OK")
    rng = np.random.default_rng(SEED + 2)
    null = np.empty(N_PERM)
    for i in range(N_PERM):
        s = rng.choice([-1.0, 1.0], size=n_pos)
        null[i] = _spearman(x * s[pos_codes], y)
    p_sf = float((np.abs(null) >= abs(obs)).mean())
    centred = abs(null.mean()) < 3 * null.std() / np.sqrt(N_PERM)
    log(f"    observed={obs:+.6f}  null mean={null.mean():+.4f}  "
        f"sd={null.std():.4f}  p="
        f"{'<' + str(1 / N_PERM) if p_sf == 0 else f'{p_sf:.4f}'}")
    log(f"    null-centring: mean {'IS' if centred else 'is NOT'} "
        f"consistent with zero (3 SE)")

    # ---- pre-registered verdict ----
    holds = (obs < 0) and (b["ci_lo"] <= PREDICTION <= b["ci_hi"])
    mean_abs_single = float(np.abs(prim["observed_rho"]).mean())
    log("\nVERDICT (pre-registered rule, fixed in docstring before running):")
    log(f"  observed rho = {obs:+.6f}, 95% CI = [{b['ci_lo']:+.6f}, "
        f"{b['ci_hi']:+.6f}]")
    log(f"  Spearman-Brown prediction = {PREDICTION:+.3f} "
        f"(recomputed {sb:+.4f} from on-disk components)")
    log(f"  (a) observed < 0: {obs < 0}; (b) prediction inside CI: "
        f"{b['ci_lo'] <= PREDICTION <= b['ci_hi']}")
    log(f"  -> the Spearman-Brown prediction "
        f"{'HOLDS' if holds else 'FAILS'}")
    log(f"  context: |observed|={abs(obs):.6f} vs mean |single-member rho|="
        f"{mean_abs_single:.6f} -> averaging "
        f"{'strengthened' if abs(obs) > mean_abs_single else 'did not strengthen'} "
        f"the association")

    # ---- save ----
    out = PROC / ("task90_a1_ensemble_mean_smoke.csv" if SMOKE
                  else "task90_a1_ensemble_mean.csv")
    rows = [
        {"stat": "spearman_delta_ens_vs_own_e_b", "value": obs,
         "ci_lo": b["ci_lo"], "ci_hi": b["ci_hi"], "p_boot": b["p_boot"]},
        {"stat": "signflip_p", "value": p_sf, "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "signflip_null_mean", "value": null.mean(), "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "sb_prediction_given", "value": PREDICTION, "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "sb_prediction_recomputed", "value": sb, "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "mean_single_member_rho", "value": mean_single,
         "ci_lo": np.nan, "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "prediction_holds", "value": float(holds), "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "n_variants", "value": float(len(frame)), "ci_lo": np.nan,
         "ci_hi": np.nan, "p_boot": np.nan},
        {"stat": "n_positions", "value": float(frame["position"].nunique()),
         "ci_lo": np.nan, "ci_hi": np.nan, "p_boot": np.nan},
    ]
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"[saved] {out}")

    log("\nLIMITATIONS: ESM-1v-seed result only (5 members of ONE "
        "architecture; ESM-2 has no seed replicates) -- A3 scope. "
        "Spearman-Brown assumes tau-equivalent parallel measures; the "
        "members are distinct checkpoints, so the prediction is a "
        "heuristic benchmark. r_bar = median of 10 pairs only. Single "
        "frame, single pre-registered test, no multiplicity claim.")
    if SMOKE:
        log("*** SMOKE RUN: machinery only, NOT findings, NOT for quoting. ***")
    log("A1 DONE")


if __name__ == "__main__":
    main()
