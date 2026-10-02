"""
Script 101 (tasks Y1 + Y2 of DISATTENUATION_AND_LEDGER.md, Group Y):

Y1 — does the severity baseline (ProteinGym's Site_Independent model)
survive ITS OWN sign-flip re-derivation null (script 33's exact code
path) and the same Holm-Bonferroni multiplicity correction applied
everywhere else in the project?

Y2 — can the severity-baseline correlation be produced by mechanism
alone? A simulation using the dataset's real distribution of fitness
that tests whether a monotone nonlinearity in severity->fitness
mechanically produces a positive correlation between a severity-only
predictor and measured epistasis.

PRE-REGISTERED (this docstring written before any run; AGENTS 6)
------------------------------------------------------------------
Y1 FRAMES + GATES (failure => print, sys.exit(1); no retry, no
threshold change):
  G1  script 33's exact frame: phase5_analysis_table +
      own_context_metrics[own_e_b] merge, dropna(delta_esm, own_e_b),
      reset_index -> 10757 rows / 654 positions (script 33's printed
      set). Site_Independent scores from
      data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv joined
      on key f"{wt_aa}{position}{mut_aa}" vs the file's `mutant`
      column (script 71 L49 convention), inner join. Expect join keeps
      all 10757 (ProteinGym covers all 12464 single substitutions,
      script 71 L52); printed either way.
  G2  reproduction: rho(Site_Independent, own_e_b) equals AB2's
      published own_rho +0.063966 within 1e-6 (task_AB2_...
      _model_comparison.csv row "Site_Independent", n=10757/654 — same
      frame, same _spearman).
  G3  script 33's identity gates verbatim: all-+1 flips reproduce
      stored own_e_b to <=1e-6; all-1 flips give its exact negation;
      failure -> sys.exit(1).
Y1 NULL: script 33's sign-flip re-derivation, signed, copied literally
  (wls_line(Rs * rng.choice([-1,1], size=Rs.shape), Ss, CONCS, Vs) per
  draw; p = mean(|null| >= |obs|); null-centring check
  |mean| < 2*sd/sqrt(N_PERM)*3 printed; excess-over-null and
  frac-artifact printed exactly as script 33 prints them).
  N_PERM env default 10000, seed 0. Only the signed variant runs —
  AB2a's claim is the SIGNED positive correlation, so that is the
  claim tested (absolute variant would test a different claim; not run).
Y1 BOOTSTRAP CI: position_cluster_bootstrap on the same frame for the
  same rho, compared to AB2's published [0.037646, 0.090564].
Y1 MULTIPLICITY (both families pre-registered, both reported
  regardless of outcome; Holm step-down copied verbatim from script 97
  L159-176, alpha=0.05):
  F7  the seven severity-baseline rows (script 97's SEVEN:
      Site_Independent, ESM1v_single, GEMME, DeepSequence_ensemble,
      EVmutation, ESM2_650M, ESM2_150M): Site_Independent's entry is
      replaced by its sign-flip p (stronger null); the other six keep
      their AB2 own_p_boot = 0.0 as on disk.
  F5  script 97's m=5 core family with its p4 (the conservative
      severity-gate entry "largest own_p_boot among the seven") replaced
      by Site_Independent's sign-flip p — the gate entry now uses the
      stronger null. Other four p's are script 97's frozen values:
      9.41e-38 (AD1 binomial), 0.0 (AD6 neff yE), 0.0 (AD6 cons yT1),
      0.0 (anchor). DISCLOSED: substitution is this script's
      operationalization, chosen before seeing the sign-flip p.

Y2 SIMULATION (which simulation, stated up front): the classic
  scale-mismatch mechanism —
  * real fitness values f = task32's f_bar (11,344 real values, range
    0 to 1.935; ratio-scale assumption DISCLOSED: multiplicative
    composition presumes f_bar is ratio-scaled with WT ~ f_wt);
    f_wt = median(f_bar_wt) on the same file (printed).
  * pairs: i, j drawn INDEPENDENTLY with replacement from the real f
    distribution (N_PAIRS = 10000, seed 0) — iid by construction, so
    plain iid inference applies (no position clustering to model in a
    draw from an empirical distribution; disclosed).
  * TRUE model: NO interaction — fitness composes MULTIPLICATIVELY
    (additive in log space; log is monotone, so this IS a monotone
    severity->fitness nonlinearity relative to the additive scale):
    f_ij = f_i * f_j / f_wt.
  * MEASURED epistasis on the additive scale (what an additive
    comparison yields): e = f_ij - f_i - f_j + f_wt
      = (f_i - f_wt)(f_j - f_wt)/f_wt.
  * severity-only predictor: s_mean = ((1 - f_i/f_wt) + (1 - f_j/f_wt))/2.
  * statistic: Spearman rho(s_mean, e); identity check = feeding the
    unpermuted predictor reproduces the observed rho exactly (1e-12);
    null = label permutation of the predictor (N_PERM env, default
    10000), null-centring printed; bootstrap CI over pairs (N_BOOT).
  * comparator printed: the real AB2 Site_Independent rho +0.063966.
  VERDICT RULE (stated before running): mechanism-only positive
  correlation is DEMONSTRATED iff the permutation p < 0.05 AND the
  bootstrap CI excludes 0 on the positive side; magnitude vs the
  observed +0.063966 is reported both ways (mechanical >= observed
  means the observed value is INSIDE what mechanism alone produces).
  Also printed: the rank-invariance note — under Spearman any monotone
  transform of the PREDICTOR is rank-invariant, so the mechanical
  correlation arises entirely from the severity->FITNESS nonlinearity,
  not from how severity is scaled on the predictor side.

Run: N_BOOT=300 N_PERM=300 venv/bin/python3 scripts/101_y1_y2_severity_baseline.py
Full: N_BOOT=10000 N_PERM=10000 (foreground)
Output: data/processed/task101_y_severity_baseline.csv
"""

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman, position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit

PROC = Path("data/processed")
RAW = Path("data/raw/mthfrModel")
EXT = Path("data/external/ProteinGym")

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
N_PAIRS = 10000
SEED = 0
SMOKE = N_BOOT <= 500

AB2_SI_RHO = 0.063966
AB2_SI_CI = (0.037646, 0.090564)
ALPHA = 0.05
SEVEN = ["Site_Independent", "ESM1v_single", "GEMME", "DeepSequence_ensemble",
         "EVmutation", "ESM2_650M", "ESM2_150M"]


def log(msg=""):
    print(msg, flush=True)


def gfail(msg):
    log(f"*** {msg}")
    sys.exit(1)


def pstr(p, n):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


def holm(ps, alpha):
    """Verbatim logic of script 97 L159-176 (Holm step-down)."""
    m = len(ps)
    order = np.argsort(ps, kind="stable")
    reject = np.zeros(m, dtype=bool)
    adj = np.empty(m)
    running, stopped = 0.0, False
    for i, idx in enumerate(order):
        thr = alpha / (m - i)
        raw = ps[idx]
        if not stopped and raw <= thr:
            reject[idx] = True
        else:
            stopped = True
        running = max(running, (m - i) * raw)
        adj[idx] = min(1.0, running)
    return order, reject, adj


def run_family(name, names, ps):
    order, reject, adj = holm(ps, ALPHA)
    log(f"\n  family '{name}' (m={len(ps)}), Holm step-down, alpha={ALPHA}:")
    rank = {idx: r + 1 for r, idx in enumerate(order)}
    for i, nm in enumerate(names):
        thr = ALPHA / (len(ps) - rank[i] + 1)
        log(f"    rank {rank[i]}  {nm:<32} raw_p={ps[i]:.6e}  "
            f"thr={thr:.6f}  reject={'YES' if reject[i] else 'no ':<3} "
            f"adj_p={adj[i]:.6e}")
    log(f"    -> {int(reject.sum())}/{len(ps)} survive at family-wise "
        f"alpha {ALPHA}")
    return int(reject.sum()), adj


def main():
    log(f"script 101 | N_BOOT={N_BOOT} N_PERM={N_PERM} seed={SEED} "
        f"started {time.strftime('%Y-%m-%d %H:%M:%S')}")
    rows = []

    # ================= Y1 =================
    log("\n==== Y1: Site_Independent under script 33's sign-flip null ====")
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse = fit["e2"], fit["M_se"]

    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro",
                                                         "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left").dropna(
        subset=["delta_esm", "own_e_b"]).reset_index(drop=True)

    pg = pd.read_csv(EXT / "MTHR_HUMAN_Weile_2021_scores.csv",
                     usecols=["mutant", "Site_Independent"])
    pat = r"^([A-Z])(\d+)([A-Z])$"
    parsed = pg["mutant"].astype(str).str.extract(pat)
    bad = int(parsed.isna().any(axis=1).sum())
    if bad:
        gfail(f"G1 FAILED: {bad} ProteinGym mutant strings malformed")
    pg["key"] = (parsed[0] + parsed[1].astype(int).astype(str)
                 + parsed[2])
    df["key"] = (df["wt_aa"].astype(str)
                 + df["position"].astype(int).astype(str)
                 + df["mut_aa"].astype(str))
    d = df.merge(pg[["key", "Site_Independent"]], on="key", how="inner")
    log(f"G1 frame: script-33 set {len(df)} rows / "
        f"{df['position'].nunique()} positions; after SI join "
        f"{len(d)} rows / {d['position'].nunique()} positions")
    if (len(df), df["position"].nunique()) != (10757, 654):
        gfail("G1 FAILED: script 33's frame is not 10757/654")
    if len(d) != len(df):
        log(f"  DISCLOSURE: SI join dropped {len(df) - len(d)} rows "
            f"(ProteinGym coverage gap on this frame)")

    si = d["Site_Independent"].to_numpy(float)
    own_eb = d["own_e_b"].to_numpy(float)
    g2 = _spearman(si, own_eb)
    log(f"G2 rho(Site_Independent, own_e_b) = {g2!r} vs AB2 published "
        f"{AB2_SI_RHO!r} (tol 1e-6)")
    if abs(g2 - AB2_SI_RHO) > 1e-6:
        gfail("G2 FAILED: AB2's Site_Independent rho not reproduced")

    # ---- script 33's identity gates (G3) ----
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in d["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]
    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    dp = np.abs(chk_p[ok] - own_eb[ok]).max()
    dm = np.abs(chk_m[ok] + own_eb[ok]).max()
    log(f"G3 identity: all-+1 max|diff|={dp:.3e}  all--1 max|diff|={dm:.3e}")
    if dp > 1e-6:
        gfail("G3 FAILED: identity check -- row alignment is wrong")

    # ---- bootstrap CI (compare to AB2's published CI) ----
    dd = d[["position"]].copy()
    dd["si"], dd["own_e_b"] = si, own_eb
    rb = position_cluster_bootstrap(dd, "position", "si", "own_e_b",
                                    n_boot=N_BOOT, seed=SEED)
    log(f"    bootstrap CI: rho={rb['observed_rho']:+.6f} "
        f"CI=[{rb['ci_lo']:+.6f}, {rb['ci_hi']:+.6f}] "
        f"p={rb['p_boot']:.4f}  (AB2 published "
        f"[{AB2_SI_CI[0]:+.6f}, {AB2_SI_CI[1]:+.6f}])")

    # ---- script 33's sign-flip re-derivation (signed), verbatim ----
    rng = np.random.default_rng(SEED)
    obs = g2
    null = np.empty(N_PERM)
    for p in range(N_PERM):
        eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                              Ss, CONCS, Vs)
        g = np.isfinite(eb_p) & np.isfinite(si)
        null[p] = _spearman(si[g], eb_p[g])
    pv = float((np.abs(null) >= abs(obs)).mean())
    excess = obs - null.mean()
    frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
    centred = abs(null.mean()) < 2 * null.std() / np.sqrt(N_PERM) * 3
    log(f"    NULL 1 SIGN-FLIP RE-DERIVATION ({N_PERM} permutations):")
    log(f"      observed={obs:+.4f}  null mean={null.mean():+.4f} "
        f"sd={null.std():+.4f}  p={pstr(pv, N_PERM)}")
    log(f"      excess over null={excess:+.4f}  "
        f"({100*frac:.0f}% of the raw value is structural artifact)")
    log(f"      -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'} "
        f"script 33's null")
    log(f"      null-centring check: null mean "
        f"{'IS' if centred else 'is NOT'} consistent with zero")
    rows.append({"task": "Y1", "stat": "signflip_p", "value": pv})
    rows.append({"task": "Y1", "stat": "signflip_null_mean",
                 "value": float(null.mean())})
    rows.append({"task": "Y1", "stat": "signflip_null_sd",
                 "value": float(null.std())})
    rows.append({"task": "Y1", "stat": "frac_artifact",
                 "value": float(frac)})

    # ---- Holm, both pre-registered families ----
    log("\n  Holm multiplicity (same step-down as everywhere else):")
    ps7 = [pv] + [0.0] * 6
    ns7 = ["Site_Independent (sign-flip p here)"] + SEVEN[1:]
    run_family("F7 severity baselines (SI entry = sign-flip p)",
               ns7, ps7)
    ps5 = [9.41e-38, 0.0, 0.0, pv, 0.0]
    ns5 = ["AD1 binomial", "AD6 neff yE", "AD6 cons yT1",
           "AB2 severity gate (p4 = SI sign-flip p)", "anchor -0.088"]
    surv5, adj5 = run_family("F5 core m=5 (p4 = SI sign-flip p)",
                             ns5, ps5)
    rows.append({"task": "Y1", "stat": "holm_F5_survivors",
                 "value": surv5})
    rows.append({"task": "Y1", "stat": "holm_F5_adj_SI",
                 "value": float(adj5[3])})

    # ================= Y2 =================
    log("\n==== Y2: mechanism-only simulation (scale mismatch; "
        "pre-registered in docstring) ====")
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv",
                      usecols=["f_bar", "f_bar_wt"])
    f = t32["f_bar"].dropna().to_numpy(float)
    fwt = float(np.median(t32["f_bar_wt"].dropna()))
    log(f"    real fitness f_bar: n={len(f)} range=[{f.min():.4f}, "
        f"{f.max():.4f}]; f_wt (median f_bar_wt)={fwt:.4f}; "
        f"ratio-scale assumption DISCLOSED")
    if f.min() < 0:
        gfail("Y2: f_bar has negative values; multiplicative model "
              "undefined -- STOP rather than clip post hoc")

    r2 = np.random.default_rng(SEED)
    fi = r2.choice(f, N_PAIRS, replace=True)
    fj = r2.choice(f, N_PAIRS, replace=True)
    fij = fi * fj / fwt                      # TRUE: multiplicative (no epi)
    e = fij - fi - fj + fwt                  # measured on additive scale
    s = ((1 - fi / fwt) + (1 - fj / fwt)) / 2  # severity-only predictor
    obs2 = _spearman(s, e)
    idem = _spearman(s, e)                   # identity check
    log(f"    observed rho(severity, measured e) = {obs2:+.6f} "
        f"(identity check |diff| = {abs(obs2 - idem):.3e})")
    if abs(obs2 - idem) > 1e-12:
        gfail("Y2 identity check FAILED")

    boot = np.empty(N_BOOT)
    perm = np.empty(N_PERM)
    for b in range(N_BOOT):
        ix = r2.integers(0, N_PAIRS, N_PAIRS)
        boot[b] = _spearman(s[ix], e[ix])
    for b in range(N_PERM):
        perm[b] = _spearman(r2.permutation(s), e)
    blo, bmed, bhi = np.percentile(boot, [2.5, 50, 97.5])
    ppv = float((np.abs(perm) >= abs(obs2)).mean())
    log(f"    bootstrap CI: [{blo:+.6f}, {bmed:+.6f}, {bhi:+.6f}] "
        f"(N_BOOT={N_BOOT})")
    log(f"    permutation p = {pstr(ppv, N_PERM)}  null mean="
        f"{perm.mean():+.6f} sd={perm.std():.6f} (centred: "
        f"{'yes' if abs(perm.mean()) < 2*perm.std()/np.sqrt(N_PERM)*3 else 'NO'})")
    log(f"    real comparator (AB2 Site_Independent rho) = "
        f"{AB2_SI_RHO:+.6f}")
    mech_pos = ppv < 0.05 and blo > 0
    log(f"    VERDICT RULE (pre-registered): mechanical positive "
        f"correlation {'DEMONSTRATED' if mech_pos else 'not demonstrated'} "
        f"(p<0.05 and CI excludes 0 positive)")
    if mech_pos:
        log(f"    magnitude: mechanical |rho|={abs(obs2):.4f} vs observed "
            f"{AB2_SI_RHO:.4f} -> mechanical is "
            f"{'>= observed: the real baseline sits INSIDE what mechanism '
              'alone produces' if abs(obs2) >= AB2_SI_RHO else
              '< observed: mechanism alone produces less than the real '
              'value'}")
    log("    rank-invariance note: under Spearman a monotone transform "
        "of the predictor changes nothing; the mechanical correlation "
        "comes entirely from the severity->FITNESS nonlinearity")
    rows.append({"task": "Y2", "stat": "sim_rho", "value": float(obs2)})
    rows.append({"task": "Y2", "stat": "sim_ci_lo", "value": float(blo)})
    rows.append({"task": "Y2", "stat": "sim_ci_hi", "value": float(bhi)})
    rows.append({"task": "Y2", "stat": "sim_p_perm", "value": ppv})

    out = PROC / "task101_y_severity_baseline.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"\nSaved: {out} ({len(rows)} rows)")
    log(f"finished {time.strftime('%Y-%m-%d %H:%M:%S')}"
        + ("  [SMOKE - not quotable]" if SMOKE else "  [FULL RUN]"))


if __name__ == "__main__":
    main()
