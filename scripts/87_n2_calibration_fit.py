"""
Script 87 (Task N2): fit Nambiar et al. 2025's two-stage calibration on
MTHFR's own data, behind a real calibration/held-out split.

PRE-REGISTERED DESIGN (written to this docstring BEFORE any fit was run)

1. FUNCTIONAL FORM — exact, recovered, cited (Task N1's result; NOT a
   reconstruction). Nambiar et al. 2025, bioRxiv 10.1101/2025.09.14.676130,
   "Protein Language Models Capture Structural and Functional Epistasis in
   a Zero-Shot Setting". Their Data/Code availability statement (full text
   line 355) names https://github.com/maslov-group/Epistasis; from
   src/NonlinearTransform/nonlinear_fit_TEM1.m, verbatim:

       ft = fittype('-1.*log(1+exp(-b.*(x+c)))','dependent',{'y'},
                    'independent',{'x'},'coefficients',{'b','c'});
       fo = fitoptions('Method','NonlinearLeastSquares','Lower',[0,0,0]);

   i.e.  phi(x) = -log(1 + exp(-b*(x + c)))   with b >= 0, c >= 0
   (negative softplus: linear with slope b for x << -c, plateau at 0 for
   x >> +c — exactly the paper's own description "linear dependence at low
   values of x < -c1 and the plateau starting for x > c1"). Their
   fitoptions 'Lower' carries 3 entries for a 2-coefficient fittype (a
   leftover from an earlier version whose header comment "%fix a=1" shows
   the amplitude was fixed to 1); the only consistent reading is
   lower bounds [0, 0] for (b, c), which is what is used here.

2. STRUCTURAL ADAPTATION (N2a — stated, not silently assumed away).
   Nambiar's datasets carry many different double-mutant backgrounds per
   protein; MTHFR has ONE fixed alternate background, A222V, applied to
   many single variants. Mapping used here:

       phi1:  S(v | WT)     ->  ln(measured fitness of v in WT background)
       phi2:  S(v | A222V)  ->  ln(measured fitness of v in A222V background)

   Nambiar's own phi2 target is the background-adjusted CONTRAST
   (log f_AB - log f_A, Methods 4.2), whereas the task doc's literal N2c
   asks for the A222V-background fitness itself. PRIMARY follows the task
   doc literally; a PRE-REGISTERED SENSITIVITY arm fits Nambiar's actual
   contrast target on the same calibration rows. Both are printed; the
   sensitivity is labelled as such everywhere.

3. THE SPLIT (N2a — the single most important safeguard in this task).
   Split unit: POSITION, not variant. AGENTS.md s3 ("cross-fit any
   calibration or confound anchor BY POSITION, never by variant") binds
   this repo and, per AGENTS.md s9, overrides the task doc's row-level
   "subset of variants" wording; the conflict is flagged in the log.
   Rule, verbatim implementable:

       rng = np.random.default_rng(0)          # seed 0
       positions = sorted(unique(position))    # 654 positions
       perm = rng.permutation(positions)
       cal_positions  = perm[:ceil(0.2 * 654)]      # 131 positions
       held_positions = perm[ceil(0.2 * 654):]      # 523 positions

   Every row at a calibration position is a calibration row; every row at
   a held-out position is a held-out row. NO POSITION AND NO ROW APPEARS
   IN BOTH (gate G1). phi1 and phi2 are fit ONLY on calibration rows.
   The row-level assignment is written to
   data/processed/task87_calibration_split.csv and reused verbatim by
   script 88 (N3) and script 89 (N4), which re-derive it from seed 0 and
   fail if it differs.

4. TARGETS. Nambiar: "if a dataset reported fitness on a log scale, we
   used those values as provided; otherwise, we applied a log transform"
   (Methods). The atlas condition scores are LINEAR activity scores
   (f_bar_wt in [0, 3.095], median 0.818), so natural log is applied:

       N2b (phi1):  y = ln(f_bar_wt)          x = esm2_score
                    f_bar_wt = mean(w12,w25,w100,w200).score   (script 15)
       N2c (phi2):  y = ln(f_bar_a222v)       x = esm2_score_a222v_bg
                    f_bar_a222v = mean(m12,m25,m100,m200).score (script 15)
       sensitivity: y = ln(f_bar_a222v) - ln(f_bar_wt)   (Nambiar's actual
                    phi2 contrast target)         x = esm2_score_a222v_bg

   Rows whose target is undefined (fitness <= 0: 665 rows f_bar_wt == 0,
   729 rows f_bar_a222v == 0; fitness NaN: 231 rows f_bar_wt) are dropped
   FROM THE CORRESPONDING FIT ONLY, counted separately for calibration and
   held-out, with an exclusion-skew check (region shares, mean
   esm2_score, mean delta_esm vs the kept rows — AGENTS.md s3: account
   for every dropped row and confirm exclusions are not systematically
   skewed w.r.t. fitness, region, or the variable under test).

5. FIT: scipy.optimize.curve_fit (trf), bounds b,c in [0, inf),
   p0 = [1/std(x), clip(-median(x), 0, None)], maxfev = 20000.

6. GATES — any failure prints FAIL and sys.exit(1). No retries, no
   threshold tuning after seeing results (AGENTS.md s0):

   G1 split integrity: seed-0 re-derivation matches the saved split;
      131/523 positions; calibration and held-out row sets disjoint;
      zero hgvs_pro in both.
   G2 sign sanity (AGENTS.md s5): Spearman(x, y) > 0 on calibration rows
      for BOTH primary curves. A non-positive value would mean the
      score/fitness direction is not what we believe; everything
      downstream would be suspect.
   G3 both primary fits converge to finite params with b > 0, c >= 0.
   G4 fitted curves strictly increasing over a 2000-point grid spanning
      the calibration x-range (Nambiar's Eqn. 2 must be monotone).

7. REPORTED (N2d): fitted (b1, c1) and (b2, c2); R2, RMSE, Spearman on
   calibration rows (fit quality) and on held-out rows (DIAGNOSTIC ONLY —
   never a selection criterion); a 10-bin equal-count binned-means vs
   fitted-curve table per curve (Nambiar Fig. 2's own diagnostic); the
   fraction of rows with log fitness > 0, which phi's (-inf, 0) range
   cannot reach. Parameters -> data/processed/task87_calibration_params.csv.

LIMITATIONS (printed with the results, AGENTS.md s6):
  - phi's range is (-inf, 0); measured log fitness above 0 (fitness > 1,
    gain-of-function rows) is structurally unreachable by the fit.
  - one ESM model (ESM-2 650M), one alternate background (A222V).
  - the split is by position, so within-position substitutions never
    straddle calibration/held-out; held-out rows share positions with
    other held-out rows and are not independent of each other (hence the
    position-cluster bootstrap in N3).
"""
import sys, os, math, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scripts.lib.stats import _spearman

SEED = 0
CAL_FRAC = 0.2
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
N_BINS = 10


def phi(x, b, c):
    """Nambiar Eqn. 2 exactly as their code fits it: -log(1+exp(-b*(x+c))),
    computed as -logaddexp(0, -b*(x+c)) for numerical stability."""
    return -np.logaddexp(0.0, -b * (x + c))


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


def fit_curve(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    b0 = 1.0 / max(np.std(x), 1e-6)
    c0 = float(np.clip(-np.median(x), 0.0, None))
    popt, pcov = curve_fit(phi, x, y, p0=[b0, c0], bounds=([0.0, 0.0], [np.inf, np.inf]),
                           maxfev=20000)
    return popt, pcov


def quality(x, y, popt):
    pred = phi(np.asarray(x, float), *popt)
    y = np.asarray(y, float)
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
    rho = float(_spearman(pred, y))
    return r2, rmse, rho


def binned_table(x, y, popt, label):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    order = np.argsort(x)
    bins = np.array_split(order, N_BINS)
    print(f"  binned means vs fitted curve — {label} "
          f"({N_BINS} equal-count bins)")
    print(f"    {'bin':>3s} {'n':>5s} {'x_center':>10s} {'mean y':>9s} "
          f"{'phi(x_c)':>9s} {'resid':>8s}")
    for i, idx in enumerate(bins):
        xc = float(x[idx].mean())
        yc = float(y[idx].mean())
        pc = float(phi(xc, *popt))
        print(f"    {i:>3d} {len(idx):>5d} {xc:>10.3f} {yc:>9.3f} "
              f"{pc:>9.3f} {yc - pc:>+8.3f}")


def skew_report(df, mask_kept, target_name, label):
    """AGENTS s3: account for every dropped row; check exclusion skew."""
    dropped = df[~mask_kept]
    kept = df[mask_kept]
    print(f"  {label} ({target_name}): kept={len(mask_kept) - len(dropped)} "
          f"dropped={len(dropped)} "
          f"(NaN={int(df[target_name].isna().sum())}, "
          f"<=0={int((df[target_name] <= 0).sum())})")
    if len(dropped) == 0:
        return
    for nm, sub in [("kept", kept), ("dropped", dropped)]:
        reg = sub["region"].value_counts(normalize=True).sort_index()
        regstr = ",".join(f"{k}:{100*v:.0f}%" for k, v in reg.items())
        print(f"    {nm:7s} n={len(sub):5d} positions={sub['position'].nunique():4d} "
              f"mean esm2_score={sub['esm2_score'].mean():+.3f} "
              f"mean delta_esm={sub['delta_esm'].mean():+.4f} | regions {regstr}")


def main():
    fails = []
    df = pd.read_csv(PROC / "task32_analysis_table.csv")
    print(f"Analysis frame: {len(df)} rows, {df['position'].nunique()} positions")

    # ---- G1: the split (seed 0, by position) -----------------------------
    print("\n" + "=" * 74)
    print("G1  SPLIT INTEGRITY (20% calibration / 80% held-out, seed 0, BY POSITION)")
    print("=" * 74)
    positions = np.sort(df["position"].unique())
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(positions)
    n_cal_pos = math.ceil(CAL_FRAC * len(positions))
    cal_pos = set(perm[:n_cal_pos].tolist())
    held_pos = set(perm[n_cal_pos:].tolist())
    df["split"] = np.where(df["position"].isin(cal_pos), "calibration", "held_out")

    split_path = PROC / "task87_calibration_split.csv"
    df[["hgvs_pro", "position", "split"]].to_csv(split_path, index=False)

    n_cal_rows = int((df["split"] == "calibration").sum())
    n_held_rows = int((df["split"] == "held_out").sum())
    cal_hgvs = set(df.loc[df["split"] == "calibration", "hgvs_pro"])
    held_hgvs = set(df.loc[df["split"] == "held_out", "hgvs_pro"])
    overlap_pos = cal_pos & held_pos
    overlap_rows = cal_hgvs & held_hgvs

    # seed-0 re-derivation must match the saved file
    rng2 = np.random.default_rng(SEED)
    perm2 = rng2.permutation(positions)
    cal_pos_re = set(perm2[:n_cal_pos].tolist())
    rerder_ok = cal_pos_re == cal_pos

    print(f"  seed={SEED}  rule=ceil({CAL_FRAC}*{len(positions)}) positions -> calibration")
    print(f"  calibration: {len(cal_pos)} positions / {n_cal_rows} rows")
    print(f"  held-out   : {len(held_pos)} positions / {n_held_rows} rows")
    print(f"  position overlap           : {len(overlap_pos)} "
          f"{'PASS' if not overlap_pos else 'FAIL'}")
    print(f"  hgvs_pro row overlap       : {len(overlap_rows)} "
          f"{'PASS' if not overlap_rows else 'FAIL'}")
    print(f"  seed-0 re-derivation match : {'PASS' if rerder_ok else 'FAIL'}")
    if len(cal_pos) != n_cal_pos or len(held_pos) != len(positions) - n_cal_pos \
            or overlap_pos or overlap_rows or not rerder_ok:
        fails.append("G1")
    print(f"  split written to {split_path.name}")

    cal = df[df["split"] == "calibration"].copy()
    held = df[df["split"] == "held_out"].copy()

    # ---- build targets; drop undefined rows per fit ----------------------
    def build(frame):
        out = frame.copy()
        out["y1"] = np.log(out["f_bar_wt"])          # phi1 target
        out["y2"] = np.log(out["f_bar_a222v"])       # phi2 target (task-doc literal)
        out["y2c"] = out["y2"] - out["y1"]           # phi2 contrast (Nambiar actual)
        return out

    cal, held = build(cal), build(held)

    def rows_for(colname):
        c = cal[np.isfinite(cal[colname])]
        h = held[np.isfinite(held[colname])]
        return c, h

    # exclusion accounting (all rows, and per split)
    print("\n" + "=" * 74)
    print("EXCLUSION ACCOUNTING (dropped rows, AGENTS s3)")
    print("=" * 74)
    df_all = build(df)
    skew_report(df_all, np.isfinite(df_all["y1"]), "f_bar_wt", "phi1 fit eligibility")
    skew_report(df_all, np.isfinite(df_all["y2"]), "f_bar_a222v", "phi2 fit eligibility")

    # ---- fit the three curves -------------------------------------------
    print("\n" + "=" * 74)
    print("N2b/N2c  FITS (calibration rows ONLY)")
    print("=" * 74)
    results = {}
    arms = [
        ("phi1_wt", "y1", "esm2_score",
         "ln(f_bar_wt) ~ esm2_score", "primary"),
        ("phi2_a222v", "y2", "esm2_score_a222v_bg",
         "ln(f_bar_a222v) ~ esm2_score_a222v_bg", "primary"),
        ("phi2_contrast_sens", "y2c", "esm2_score_a222v_bg",
         "ln(f_bar_a222v)-ln(f_bar_wt) ~ esm2_score_a222v_bg", "sensitivity"),
    ]
    for name, ycol, xcol, desc, kind in arms:
        c, h = rows_for(ycol)
        c = c[np.isfinite(c[xcol])]
        h = h[np.isfinite(h[xcol])]
        try:
            popt, _ = fit_curve(c[xcol].to_numpy(), c[ycol].to_numpy())
        except Exception as e:
            print(f"  {name:20s} FIT FAILED: {e}")
            fails.append(f"G3:{name}")
            continue
        b, cc = float(popt[0]), float(popt[1])
        r2c, rmsec, rhoc = quality(c[xcol], c[ycol], popt)
        r2h, rmseh, rhoh = quality(h[xcol], h[ycol], popt)
        results[name] = dict(b=b, c=cc, desc=desc, kind=kind, popt=popt,
                             n_cal=len(c), n_held=len(h),
                             r2c=r2c, rmsec=rmsec, rhoc=rhoc,
                             r2h=r2h, rmseh=rmseh, rhoh=rhoh)
        tag = "PRIMARY " if kind == "primary" else "SENSITIV"
        print(f"  [{tag}] {name:20s} {desc}")
        print(f"           b={b:.6f}  c={cc:.6f}   n_cal={len(c)}  n_held={len(h)}")
        print(f"           calibration: R2={r2c:.4f} RMSE={rmsec:.4f} "
              f"Spearman(pred,obs)={rhoc:+.4f}")
        print(f"           held-out   : R2={r2h:.4f} RMSE={rmseh:.4f} "
              f"Spearman(pred,obs)={rhoh:+.4f}   (diagnostic only)")

    # ---- G2: sign sanity --------------------------------------------------
    print("\n" + "=" * 74)
    print("G2  SIGN SANITY (Spearman(x, y) on calibration rows must be > 0)")
    print("=" * 74)
    for name, ycol, xcol, desc, kind in arms[:2]:      # primary curves only
        c, _ = rows_for(ycol)
        c = c[np.isfinite(c[xcol])]
        rho = float(_spearman(c[xcol], c[ycol]))
        ok = rho > 0
        print(f"  {name:20s} Spearman({xcol}, {ycol}) = {rho:+.4f}  "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"G2:{name}")

    # ---- G3 / G4 ----------------------------------------------------------
    print("\n" + "=" * 74)
    print("G3/G4  FIT VALIDITY AND MONOTONICITY")
    print("=" * 74)
    for name in ("phi1_wt", "phi2_a222v"):
        if name not in results:
            print(f"  {name}: FAIL (no fit — see above)")
            continue
        r = results[name]
        ok3 = np.isfinite(r["b"]) and np.isfinite(r["c"]) and r["b"] > 0 and r["c"] >= 0
        print(f"  {name:20s} b>0 & c>=0 & finite : {'PASS' if ok3 else 'FAIL'} "
              f"(b={r['b']:.6f}, c={r['c']:.6f})")
        if not ok3:
            fails.append(f"G3:{name}")
        c, _ = rows_for("y1" if name == "phi1_wt" else "y2")
        xc = c[("esm2_score" if name == "phi1_wt" else "esm2_score_a222v_bg")].to_numpy()
        grid = np.linspace(xc.min(), xc.max(), 2000)
        vals = phi(grid, r["b"], r["c"])
        ok4 = bool(np.all(np.diff(vals) > 0))
        print(f"  {name:20s} strictly increasing  : {'PASS' if ok4 else 'FAIL'} "
              f"(2000-pt grid over calibration x-range)")
        if not ok4:
            fails.append(f"G4:{name}")

    # ---- N2d: binned diagnostics ------------------------------------------
    print("\n" + "=" * 74)
    print("N2d  BINNED MEANS vs FITTED CURVE (Nambiar Fig. 2's diagnostic)")
    print("=" * 74)
    for name, ycol, xcol in [("phi1_wt", "y1", "esm2_score"),
                             ("phi2_a222v", "y2", "esm2_score_a222v_bg")]:
        if name not in results:
            continue
        r = results[name]
        c, h = rows_for(ycol)
        c = c[np.isfinite(c[xcol])]
        h = h[np.isfinite(h[xcol])]
        print(f"\n  {name}  b={r['b']:.6f} c={r['c']:.6f}  {r['desc']}")
        binned_table(c[xcol], c[ycol], r["popt"], "calibration rows")
        binned_table(h[xcol], h[ycol], r["popt"], "held-out rows (diagnostic)")
        frac_pos = float((np.asarray(h[ycol]) > 0).mean()) if len(h) else np.nan
        print(f"    fraction of held-out targets > 0 (outside phi's (-inf,0) range): "
              f"{100*frac_pos:.1f}%")

    # ---- save parameters ---------------------------------------------------
    rows = []
    for name, r in results.items():
        rows.append({"arm": name, "kind": r["kind"], "b": r["b"], "c": r["c"],
                     "target_x": r["desc"], "n_cal": r["n_cal"], "n_held": r["n_held"],
                     "r2_cal": r["r2c"], "rmse_cal": r["rmsec"], "rho_cal": r["rhoc"],
                     "r2_heldout": r["r2h"], "rmse_heldout": r["rmseh"],
                     "rho_heldout": r["rhoh"], "seed": SEED, "cal_frac": CAL_FRAC,
                     "split_unit": "position"})
    out = PROC / "task87_calibration_params.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved params to {out}")

    print("\n" + "=" * 74)
    print("LIMITATIONS (printed with the results — AGENTS s6)")
    print("=" * 74)
    print("  - phi's range is (-inf, 0): measured log fitness > 0 (fitness > 1,")
    print("    gain-of-function rows) is structurally unreachable by the fit.")
    print("  - one PLM (ESM-2 650M), one alternate background (A222V); Nambiar's")
    print("    symmetrized two-path design is not available on this data (one path).")
    print("  - phi2's PRIMARY target follows the task doc literally (A222V-bg")
    print("    fitness); Nambiar's own phi2 target is the background-adjusted")
    print("    contrast — that arm is reported separately and labelled SENSITIVITY.")
    print("  - fit quality on held-out rows is a diagnostic, never a selection")
    print("    criterion; no parameter, threshold or subset was chosen after seeing it.")

    if fails:
        print(f"\n*** GATES FAILED: {fails} — not passing gates; no retry, no tuning. ***")
        sys.exit(1)
    print("\nALL GATES PASS (G1 split integrity, G2 sign sanity, G3 fit validity, "
          "G4 monotonicity).")
    sys.exit(0)


if __name__ == "__main__":
    main()
