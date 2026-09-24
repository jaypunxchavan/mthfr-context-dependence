"""
Script 59: J4a (FDR-based epistatic threshold) + J4b (is 3.76 constant?).
Pre-registration: OVERNIGHT_LOG.md J3a entry (2026-09-22), fixed before
this script was written or run. Decision bands below are pre-registered;
do not change them after seeing results.

J4a -- FDR-based SE threshold replacing the flat 3.76x fix
---------------------------------------------------------
Empirical null = synonymous z_e_b (variants encoding an identical protein
cannot have real epistasis -- script 35's own logic).
  FDR_hat(c) = synonymous pass rate(c) / missense pass rate(c),
  c grid 1.00..10.00 step 0.01 (|z_e_b| > c).
  PRE-REGISTERED: c* = smallest c with FDR_hat <= 0.05 AND all larger
  grid points also <= 0.05.
    BANDS vs the flat 3.76x (|z|>3.76): c* in [3.01, 4.51] (+/-20%)
    -> 3.76-CONFIRMED; c* > 4.51 -> 3.76-TOO-PERMISSIVE;
       c* < 3.01 -> 3.76-TOO-STRICT.
  Also reported: FDR_hat(3.76), pass counts at c* and at 3.76, median
  |own_e_b| among missense passers at both (effect sizes), position-
  cluster bootstrap CI on FDR_hat at c* (N_BOOT=2000; synonymous and
  missense clusters resampled independently).
  Logged interpretation choices (ambiguity -> most conservative reading):
  - No pi0 factor: the raw rate ratio is used. Storey-style FDR would
    multiply by pi0 <= 1, i.e. be SMALLER; the raw ratio therefore cannot
    understate FDR relative to standard estimates (conservative for
    declaring discoveries).
  - Tail condition ("all larger grid points") is evaluated only over grid
    points with >= 1 missense discovery: where zero missense pass, FDR is
    undefined (no discovery, no false-discovery burden). Those points are
    excluded from the condition and printed. syn_pass=0 with missense
    pass >= 1 is a valid FDR = 0.
  - If NO grid point satisfies the pre-registered rule, that IS the
    outcome: report "no sustained c found in [1,10]" plus the descriptive
    first crossing and FDR(3.76); do not substitute a different rule.

J4b -- is the 3.76 ratio constant across regions and fitness levels?
--------------------------------------------------------------------
Stratum ratio = sd(syn own_e_b, ddof=1) / median(syn se_e_b) -- EXACTLY
script 35's definition (pooled value 3.758647782830226 must reproduce
within 1e-6 or the script exits 1).
  Strata: mutagenesis region (region column, assigned by script 35 via
  scripts.lib.regions.assign_region) x fitness terciles of w.fitness
  (edges computed on the missense analysis set; synonymous rows inherit
  the stratum of their OWN w.fitness; syn rows with missing w.fitness
  excluded from terciles, printed).
  PRE-REGISTERED: 3.76 CONSTANT-ENOUGH iff every stratum ratio in
  [1.88, 5.64] (i.e. +/-50% of 3.7586, computed exactly as
  3.758647782830226*0.5 and *1.5) AND max/min <= 2; else NEEDS-TO-VARY.
  Per-stratum syn n printed; strata with syn n < 50 flagged
  "(underpowered)". Position-cluster bootstrap CI per ratio (N_BOOT=2000).

LIMITATIONS (printed by the script itself, AGENTS 6):
- FDR_hat treats the synonymous tail as exchangeable with the missense
  NULL tail; missense and synonymous SE distributions can differ (syn
  variants are often UTR-adjacent/spliced differently), so the ratio is
  an estimate, not an identity.
- With ~570 synonymous rows the bootstrap CI on FDR_hat(c*) is wide; the
  point estimate and its CI are both reported (AGENTS 3: effect size
  alongside significance).
- Per-stratum synonymous counts are small; the +/-50% bands are wide by
  design and small-n strata are flagged rather than hidden.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"
POOLED_RATIO = 3.758647782830226      # task35_summary.csv, gate below
GRID = np.round(np.arange(1.00, 10.0001, 0.01), 2)
FDR_TARGET = 0.05
C_FLAT = 3.76


def ratio_of(syn_sub):
    """Stratum ratio, EXACTLY script 35's definition."""
    if len(syn_sub) < 2:
        return np.nan
    return float(syn_sub["own_e_b"].std(ddof=1) / syn_sub["se_e_b"].median())


def cluster_boot_ratio(syn_sub, n_boot, seed=0):
    """Position-cluster bootstrap CI for the stratum ratio."""
    pos = syn_sub["position"].to_numpy()
    eb = syn_sub["own_e_b"].to_numpy()
    se = syn_sub["se_e_b"].to_numpy()
    uniq = np.unique(pos)
    idx_by = {c: np.flatnonzero(pos == c) for c in uniq}
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        out[b] = np.std(eb[i], ddof=1) / np.median(se[i])
    out = out[~np.isnan(out)]
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi)


if __name__ == "__main__":
    print(f"Script 59 — J4a + J4b | N_BOOT={N_BOOT} SEED={SEED}")
    f_path = PROC / "task35_epistatic_set.csv"
    if not f_path.exists():
        print(f"GATE FAIL: missing {f_path}")
        sys.exit(1)

    tab = pd.read_csv(f_path)
    ok = tab["se_e_b"].notna() & tab["own_e_b"].notna()
    syn = tab[(tab["type"] == "synonymous") & ok].copy()
    mis = tab[(tab["type"] == "substitution") & ok].copy()
    print(f"rows {len(tab)}; synonymous ok {len(syn)}; missense ok {len(mis)}")
    if not (len(syn) >= 500 and len(mis) >= 10000):
        print("GATE FAIL: analysis set smaller than expected")
        sys.exit(1)

    # GATE: pooled ratio reproduces script 35's sanity number exactly
    pooled = ratio_of(syn)
    d_pooled = abs(pooled - POOLED_RATIO)
    print(f"GATE pooled syn ratio: {pooled:.12f} "
          f"(target {POOLED_RATIO}, |diff| = {d_pooled:.3e}, tol 1e-6)")
    if not d_pooled < 1e-6:
        print("GATE FAIL: pooled ratio does not reproduce task35 value")
        sys.exit(1)

    # column identity: z_e_b == own_e_b / se_e_b
    zchk = (tab.loc[ok, "z_e_b"] -
            tab.loc[ok, "own_e_b"] / tab.loc[ok, "se_e_b"]).abs().max()
    print(f"GATE z identity: max|z - own/se| = {zchk:.3e} (tol 1e-9)")
    if not zchk < 1e-9:
        print("GATE FAIL: z_e_b column inconsistent")
        sys.exit(1)

    # ==================== J4a ====================
    print("\n" + "=" * 74)
    print("J4a  FDR-BASED THRESHOLD (synonymous empirical null)")
    print("=" * 74)
    syn_z = syn["z_e_b"].abs().to_numpy()
    mis_z = mis["z_e_b"].abs().to_numpy()
    n_syn, n_mis = len(syn_z), len(mis_z)
    syn_pass = np.array([(syn_z > c).sum() for c in GRID])
    mis_pass = np.array([(mis_z > c).sum() for c in GRID])
    with np.errstate(invalid="ignore", divide="ignore"):
        fdr = (syn_pass / n_syn) / (mis_pass / n_mis)
    has_disc = mis_pass >= 1
    fdr_eval = np.where(has_disc, fdr, np.nan)

    # pre-registered tail condition over points with >= 1 missense discovery
    tail_max = np.full(len(GRID), np.nan)
    running = np.nan
    for i in range(len(GRID) - 1, -1, -1):
        v = fdr_eval[i]
        if not np.isnan(v):
            running = v if np.isnan(running) else max(running, v)
        tail_max[i] = running
    satisfy = ~np.isnan(tail_max) & (tail_max <= FDR_TARGET)
    c_star = float(GRID[satisfy][0]) if satisfy.any() else None
    n_nodisc = int((~has_disc).sum())

    i_flat = int(np.argmin(np.abs(GRID - C_FLAT)))
    print(f"grid {GRID[0]:.2f}-{GRID[-1]:.2f} step 0.01; "
          f"points with 0 missense discoveries (excluded from tail "
          f"condition): {n_nodisc}")
    for c in [2.0, 2.5, 3.0, 3.5, C_FLAT, 4.5, 5.0]:
        i = int(np.argmin(np.abs(GRID - c)))
        if has_disc[i]:
            print(f"  FDR_hat({GRID[i]:>4.2f}) = {fdr[i]:.4f}   "
                  f"syn {syn_pass[i]}/{n_syn}  mis {mis_pass[i]}/{n_mis}")
        else:
            print(f"  FDR_hat({GRID[i]:>4.2f}) = undefined (0 missense "
                  f"passes)")

    if c_star is None:
        verdict = "NO-SUSTAINED-C-IN-GRID"
        print(f"\nPRE-REGISTERED c*: none in [1,10] satisfies "
              f"FDR<={FDR_TARGET} sustained to the grid end -> "
              f"VERDICT: {verdict}")
        first_cross = (float(GRID[(fdr_eval <= FDR_TARGET) & has_disc][0])
                       if ((fdr_eval <= FDR_TARGET) & has_disc).any() else None)
        if first_cross is not None:
            print(f"  (descriptive only, NOT the pre-registered c*): "
                  f"first grid point with FDR_hat <= 0.05 = "
                  f"{first_cross:.2f}")
    else:
        if 3.01 <= c_star <= 4.51:
            verdict = "3.76-CONFIRMED"
        elif c_star > 4.51:
            verdict = "3.76-TOO-PERMISSIVE"
        else:
            verdict = "3.76-TOO-STRICT"
        print(f"\nPRE-REGISTERED c* = {c_star:.2f}  ->  VERDICT: {verdict}")

    # FDR at c* with position-cluster bootstrap CI (pre-registered)
    def fdr_at(c):
        sp = int((syn_z > c).sum())
        mp = int((mis_z > c).sum())
        if mp == 0:
            return np.nan, sp, mp
        return (sp / n_syn) / (mp / n_mis), sp, mp

    if c_star is not None:
        point_fdr, sp_star, mp_star = fdr_at(c_star)
        ps = pd.DataFrame({"position": syn["position"],
                           "pass": (syn_z > c_star).astype(int)})
        pm = pd.DataFrame({"position": mis["position"],
                           "pass": (mis_z > c_star).astype(int)})
        cs, cm = ps["position"].unique(), pm["position"].unique()
        gs = {c: ps.loc[ps["position"] == c, "pass"].to_numpy() for c in cs}
        gm = {c: pm.loc[pm["position"] == c, "pass"].to_numpy() for c in cm}
        rng = np.random.default_rng(SEED)
        boot = np.empty(N_BOOT)
        for b in range(N_BOOT):
            ds = rng.choice(cs, size=len(cs), replace=True)
            dm = rng.choice(cm, size=len(cm), replace=True)
            rs = np.concatenate([gs[c] for c in ds]).sum()
            rm = np.concatenate([gm[c] for c in dm]).sum()
            boot[b] = (rs / n_syn) / (rm / n_mis) if rm > 0 else np.nan
        boot = boot[~np.isnan(boot)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print(f"FDR_hat(c*) point estimate = {point_fdr:.4f}  "
              f"CI=[{lo:.4f},{hi:.4f}]  (syn {sp_star}/{n_syn}, "
              f"mis {mp_star}/{n_mis}; cluster bootstrap N_BOOT={N_BOOT})")
    else:
        point_fdr, sp_star, mp_star, lo, hi = np.nan, 0, 0, np.nan, np.nan

    # FDR at the flat 3.76 + effect sizes (pre-registered reporting)
    f_flat, sp_flat, mp_flat = fdr_at(C_FLAT)
    print(f"FDR_hat({C_FLAT}) = {f_flat:.4f}  (syn {sp_flat}/{n_syn}, "
          f"mis {mp_flat}/{n_mis})")
    for lbl, c in [("c*", c_star if c_star is not None else np.nan),
                   (f"{C_FLAT}", C_FLAT)]:
        if np.isnan(c):
            continue
        sub = mis[mis["z_e_b"].abs() > c]
        print(f"  missense passers at {lbl} (|z|>{c:.2f}): {len(sub)} "
              f"({100*len(sub)/n_mis:.1f}%)  median |own_e_b| = "
              f"{sub['own_e_b'].abs().median():.4f}  "
              f"median se = {sub['se_e_b'].median():.4f}")
    if c_star is not None and not np.isnan(f_flat) and mp_flat > 0:
        print(f"  count change vs flat 3.76: "
              f"{mp_star - mp_flat:+d} missense "
              f"({100*(mp_star - mp_flat)/n_mis:+.1f} pp)")

    j4a_rows = [
        {"quantity": "pooled_ratio", "value": pooled},
        {"quantity": "c_star", "value": c_star if c_star else np.nan},
        {"quantity": "verdict", "value": verdict},
        {"quantity": "fdr_at_cstar", "value": point_fdr},
        {"quantity": "fdr_at_cstar_ci_lo", "value": lo},
        {"quantity": "fdr_at_cstar_ci_hi", "value": hi},
        {"quantity": f"fdr_at_{C_FLAT}", "value": f_flat},
        {"quantity": "syn_pass_at_cstar", "value": sp_star},
        {"quantity": "mis_pass_at_cstar", "value": mp_star},
        {"quantity": f"syn_pass_at_{C_FLAT}", "value": sp_flat},
        {"quantity": f"mis_pass_at_{C_FLAT}", "value": mp_flat},
        {"quantity": "n_syn", "value": n_syn},
        {"quantity": "n_mis", "value": n_mis},
    ]

    # ==================== J4b ====================
    print("\n" + "=" * 74)
    print("J4b  IS THE 3.76 RATIO CONSTANT ACROSS REGIONS / FITNESS?")
    print("=" * 74)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    wf = raw[["hgvs", "w.fitness"]].rename(columns={"hgvs": "hgvs_pro"})
    tab_ok = tab[ok].merge(wf, on="hgvs_pro", how="left")
    syn_all = tab_ok[tab_ok["type"] == "synonymous"].copy()
    mis_all = tab_ok[tab_ok["type"] == "substitution"].copy()
    print(f"syn with region: {syn_all['region'].notna().sum()}; "
          f"syn with w.fitness: {syn_all['w.fitness'].notna().sum()}")

    lo_band, hi_band = POOLED_RATIO * 0.5, POOLED_RATIO * 1.5
    strata_rows = []

    # -- regions
    print(f"\n  {'stratum':>22}  {'n_syn':>6}  {'ratio':>7}  "
          f"{'CI':>21}  flags")
    for r in sorted(syn_all["region"].dropna().unique()):
        sub = syn_all[syn_all["region"] == r]
        ratio = ratio_of(sub)
        ci_lo, ci_hi = cluster_boot_ratio(sub, N_BOOT, SEED) if len(sub) >= 20 \
            else (np.nan, np.nan)
        flags = []
        if len(sub) < 50:
            flags.append("(underpowered: n<50)")
        if not (np.isnan(ratio) or lo_band <= ratio <= hi_band):
            flags.append("OUTSIDE +/-50%")
        print(f"  {'region ' + str(int(r)):>22}  {len(sub):>6}  "
              f"{ratio:>7.3f}  [{ci_lo:>8.3f},{ci_hi:>8.3f}]  "
              f"{' '.join(flags)}")
        strata_rows.append({"stratum_type": "region", "stratum": int(r),
                            "n_syn": len(sub), "ratio": ratio,
                            "ci_lo": ci_lo, "ci_hi": ci_hi,
                            "flag": " ".join(flags)})

    # -- fitness terciles (edges on the missense analysis set)
    mis_fit = mis_all.dropna(subset=["w.fitness"]).copy()
    edges = mis_fit["w.fitness"].quantile([1/3, 2/3]).to_numpy()
    print(f"\n  fitness tercile edges (missense analysis set "
          f"n={len(mis_fit)}): {edges.round(4).tolist()}")
    labels = ["low", "mid", "high"]
    mis_fit["terc"] = pd.cut(mis_fit["w.fitness"],
                             [-np.inf, edges[0], edges[1], np.inf],
                             labels=labels)
    terc_counts = mis_fit.groupby("terc", observed=True).size()
    print(f"  missense tercile counts: {terc_counts.to_dict()}")
    syn_fit = syn_all.dropna(subset=["w.fitness"]).copy()
    syn_fit["stratum"] = pd.cut(syn_fit["w.fitness"],
                                [-np.inf, edges[0], edges[1], np.inf],
                                labels=labels)
    for lab in labels:
        sub = syn_fit[syn_fit["stratum"] == lab]
        ratio = ratio_of(sub)
        ci_lo, ci_hi = cluster_boot_ratio(sub, N_BOOT, SEED) if len(sub) >= 20 \
            else (np.nan, np.nan)
        flags = []
        if len(sub) < 50:
            flags.append("(underpowered: n<50)")
        if not (np.isnan(ratio) or lo_band <= ratio <= hi_band):
            flags.append("OUTSIDE +/-50%")
        print(f"  {'fit_' + lab:>22}  {len(sub):>6}  {ratio:>7.3f}  "
              f"[{ci_lo:>8.3f},{ci_hi:>8.3f}]  {' '.join(flags)}")
        strata_rows.append({"stratum_type": "fitness_tercile",
                            "stratum": lab, "n_syn": len(sub),
                            "ratio": ratio, "ci_lo": ci_lo, "ci_hi": ci_hi,
                            "flag": " ".join(flags)})

    sdf = pd.DataFrame(strata_rows)
    ratios = sdf["ratio"].dropna()
    any_out = bool(((ratios < lo_band) | (ratios > hi_band)).any())
    spread = float(ratios.max() / ratios.min()) if len(ratios) else np.nan
    spread_ok = spread <= 2.0
    verdict_b = ("CONSTANT-ENOUGH" if (not any_out and spread_ok)
                 else "NEEDS-TO-VARY")
    print(f"\nbands: [{lo_band:.3f}, {hi_band:.3f}] (+/-50% of "
          f"{POOLED_RATIO:.4f}); max/min ratio = {spread:.2f} (<=2 required)")
    print(f"PRE-REGISTERED J4b VERDICT: {verdict_b}  "
          f"(any stratum outside band: {any_out}; max/min>2: "
          f"{not spread_ok})")
    under = sdf[sdf["flag"].str.contains("underpowered")]
    if len(under):
        print(f"underpowered strata (syn n<50): "
              f"{under[['stratum_type', 'stratum', 'n_syn']].to_dict('records')}")

    pd.DataFrame(j4a_rows).to_csv(PROC / "task59_j4a_fdr.csv", index=False)
    sdf.to_csv(PROC / "task59_j4b_ratios.csv", index=False)
    print(f"\nSaved {PROC / 'task59_j4a_fdr.csv'} and "
          f"{PROC / 'task59_j4b_ratios.csv'}")
    print("\nLIMITATIONS: syn-tail-as-null assumes exchangeable SE "
          "structures; ~570 syn rows give wide bootstrap CIs (reported); "
          "small-n strata flagged; ddof=1 and median-SE exactly as "
          "script 35.")
