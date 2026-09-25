"""
Script 88 (Task N3): recompute the headline correlation on phi1/phi2-
CALIBRATED scores, using ONLY the 80% held-out set.

PRE-REGISTERED (written before running; decision rules fixed here, AGENTS s0/s6)

WHAT IS BEING TESTED
--------------------
Nambiar et al. 2025 report raw PLM scores at Pearson r ~ 0.09-0.18 against
measured epistasis and ~0.26-0.38 after their Eqn. 2 calibration. This
project's raw anchor (Spearman, delta_ESM vs own_e_b, all rows) is
-0.088118. The calibration-gap explanation predicts that applying phi1/phi2
should move this project's statistic materially toward Nambiar's calibrated
band. This script tests exactly that, on held-out rows only.

QUANTITIES (all derived below and printed)
------------------------------------------
  phi1, phi2 : parameters from data/processed/task87_calibration_params.csv
               (fit ONCE on the 20% calibration subset by script 87 — never
               refit here, per Nambiar's protocol). The phi FUNCTION is
               loaded from script 87 itself, so exactly one implementation
               of the equation exists in this project.
  delta_cal  = phi2(esm2_score_a222v_bg) - phi1(esm2_score)
               the background-induced shift on the CALIBRATED scale —
               N3a's x-variable. (Nambiar's phi2 maps conditional RLLs to
               background-specific fitness; phi1 maps WT-background RLLs.)
  delta_raw  = delta_esm = esm2_score_a222v_bg - esm2_score (script 32)
  own_e_b    = the project's own measured interaction (WLS residual
               intercept, scripts/lib/own_context.py) — N3a's primary y.
               Chosen as primary because the sign-flip re-derivation null
               (script 33) is defined on own_e_b and the established anchor
               (Z2d/AC4: -0.088118) is the own_e_b pair. The published
               GI_folinate_independent (e.b) is reported alongside as
               secondary with the weaker null only — script 33's own note:
               "P-values apply to own_e_b."
  eps_e(v)   = Nambiar's experimental epistasis (their Eqn. 3) on MTHFR:
               ln f(v,A222V) - ln f(v,WT) - ln f(A222V)
             = ln(f_bar_a222v) - ln(f_bar_wt) - ln(f_A222V),
               with f_A222V read at runtime from
               phase3_analysis_table.csv, p.Ala222Val, f_bar_wt (asserted
               single row, > 0). Rows with non-positive fitness drop (log
               undefined) and are counted. The additive constant
               -ln(f_A222V) cancels in every rank statistic; it is kept so
               the quantity equals their definition exactly.
  eps_m(v)   = Nambiar's MODEL epistasis (their Eqn. 4) reduced to the one
               direction this dataset has. Their Eqn. 4:
                 eps = 0.5*(P_A->B + P_B->A) - (phi1(A) + phi1(B))
                 P_A->B = phi1(A) + phi2(B|A),  P_B->A = phi1(B) + phi2(A|B)
               Set A = variant v, B = A222V. Path B->A needs phi2(v|A222V)
               = phi2(esm2_score_a222v_bg), available. Path A->B needs
               phi2(A222V|v) — A222V scored in EACH variant's background —
               which was never scored; script 32's docstring already
               discloses this one-directional limitation ("the atlas
               measures variants in the A222V background, never A222V in
               each variant's background"). Taking the available path minus
               the additive expectation, phi1(A222V) cancels:
                 eps_m = P_B->A - (phi1(v) + phi1(A222V))
                       = phi1(A222V) + phi2(s_av) - phi1(s_wt) - phi1(A222V)
                       = phi2(s_av) - phi1(s_wt)  =  delta_cal.
               So N3b's model side IS delta_cal; N3b differs from N3a only
               in its y (eps_e, Nambiar's definition). This identity is a
               derivation, printed, not a coincidence. The raw-scale
               analogue of the same reduction is s_av - s_wt = delta_esm
               (their E_raw one-path), which makes N3c's raw-vs-calibrated
               pair for N3b exact.

  WHICH phi2: their Eqn. 4's phi2 is fit with THEIR ACTUAL TARGET, the
  background-adjusted contrast (Methods 4.2; their code targets
  log f_AB - log f_mut). That is N2's pre-registered sensitivity arm
  (b=0.020688, c=23.512049), which fits MTHFR poorly (R2=0.0016). The task
  doc's N2c instead defines the PRIMARY phi2 with the level target. The
  cancellation above is independent of the target — only the fitted
  parameters differ — so BOTH arms are computed and reported (task doc:
  "if they disagree, report the disagreement plainly rather than picking
  the more favorable one"):
    - N3b-LITERAL  x = phi2_contrast(s_av) - phi1(s_wt)  (their actual
      phi2 semantics — the most literal replication of their method)
    - N3b-LEVEL    x = phi2_level(s_av) - phi1(s_wt) = delta_cal
      (the phi2 N2c's primary definition produced; same x as N3a)
  DISCLOSURE: pairing the contrast arm with N3b was added AFTER the smoke
  run, on semantic grounds (which phi2 target their Eqn. 4 actually uses),
  NOT in response to any observed smoke result; no pre-registered gate,
  frame, null or verdict rule changed by adding it.

  DIAGNOSTIC (added with the same disclosure): Spearman(delta_cal,
  delta_esm / esm2_score / esm2_score_a222v_bg) and the two spreads, to
  state how much of delta_cal is still the shift versus how much is the
  phi1-vs-phi2 curve mismatch (b1=0.262 vs b2=0.144). Interpretation
  context for N3d; it does not alter the verdict rule.

  POST-HOC SENSITIVITY (explicitly post-hoc, disclosed per AGENTS s0/s6):
  after the composition diagnostic showed the pre-registered delta_cal is
  essentially not a shift (Spearman with delta_esm near zero), a
  single-curve shift delta_same = phi1(s_av) - phi1(s_wt) — both scores
  through ONE curve — is computed against own_e_b on E1 with the same
  nulls. It is printed AFTER the pre-registered verdict, is NOT part of
  M1/M2, and cannot change the verdict either way. Whatever it shows is
  reported as-is.

SPLIT GATE (N2a's named gate, repeated here before anything is computed)
-----------------------------------------------------------------------
  G0: re-derive the split from seed 0 by position (np.random.
  default_rng(0).permutation(sorted positions), first ceil(0.2*654)=131
  positions calibration); assert it reproduces
  task87_calibration_split.csv exactly; assert ZERO held-out evaluation row
  is a calibration row (0 position overlap, 0 row overlap). Failure -> exit 1.
  G0b: the full-data raw anchor must reproduce the established value
  rho(delta_esm, own_e_b) = -0.08811806424891734 on all 10,757 rows
  (tolerance 1e-9); failure -> exit 1 (frame or column-identity error,
  AGENTS s5).

FRAMES (pre-registered)
  E1 = held_out rows with delta_esm & own_e_b & GI finite     (pair A)
  E2 = E1 rows additionally with f_bar_wt > 0 & f_bar_a222v > 0 (pair B)
  Size gates: E1 >= 5000 rows and >= 400 positions; E2 >= 4000 rows.
  Raw and calibrated arms of every pair use the SAME rows (N3c).

NULLS (chosen to match each statistic, AGENTS s4)
  Pair A primary (own_e_b): SIGN-FLIP RE-DERIVATION null exactly as script
    33 — flip +/-1 on each variant's per-concentration residuals, refit
    own_e_b, recompute rho, N_PERM times. Mandatory identity checks on this
    frame: all-+1 reproduces own_e_b (max|diff| < 1e-6), all-(-1) gives its
    exact negation; failure -> exit 1 (AGENTS s4). Null centring checked
    and printed; p_null is the primary claim for this pair (script 33:
    "Null 1 is the real test"), p_boot from the position-cluster bootstrap
    reported alongside; effect sizes printed with every significance.
  Pair A secondary (GI) and Pair B (eps_e): POSITION-BLOCK PERMUTATION
    null, script 33's Null-2 implementation (shuffle position-block order
    of x against y), labelled the weaker association null. The
    re-derivation null does not apply to GI or eps_e: neither is built
    from the WLS residual machinery, so no measurement-noise
    re-derivation exists for them. This limitation is printed.

REPORTING (N3c/N3d decision rule — fixed before running)
  Every number: rho, 95% position-cluster-bootstrap CI, p_null, p_boot, n,
  on the same held-out rows; plus the full-data raw reference.
  VERDICT RULE for N3d, pre-registered:
    "MATERIAL MOVEMENT toward Nambiar's calibrated band" iff
      (M1) |rho_cal(own_e_b)| >= 0.26  (bottom of their calibrated range),
    or (M2) |rho_cal(own_e_b)| >= 2 * |rho_raw(own_e_b)| on the same rows.
    Otherwise NOT MATERIAL. A sign change vs the raw arm is flagged
    prominently regardless. Magnitudes, not literal number-matches, are
    compared (task doc: sign conventions differ across datasets).

LIMITATIONS printed with results: one background/one path (above), phi's
(-inf, 0) range ceiling, Spearman here vs Nambiar's Pearson, and the fact
that the 80% held out held out only from CALIBRATING — the raw statistic
was known on all rows before this script (not a fresh holdout for the raw
arm; AGENTS s8). N_BOOT/N_PERM from environment (smoke first).
"""
import sys, os, math, warnings, importlib.util
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman, position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit
from scripts.lib.regions import assign_region

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
CAL_FRAC = 0.2
ANCHOR_FULL_RAW = -0.08811806424891734   # Z2d/AC4 anchor, delta_ESM vs own_e_b
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"

# single source of truth for the equation: load script 87 (main is guarded)
_spec = importlib.util.spec_from_file_location(
    "n2_calibration", ROOT / "scripts" / "87_n2_calibration_fit.py")
_n2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_n2)
phi = _n2.phi


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


def signflip_null(pred, y, Rs, Ss, Vs, n_perm, seed):
    """Script 33's exact mechanism: flip +/-1 signs of each variant's
    per-concentration residuals, refit own_e_b, recompute rho."""
    rng = np.random.default_rng(seed)
    obs = _spearman(pred, y)
    null = np.empty(n_perm)
    for p in range(n_perm):
        eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                              Ss, CONCS, Vs)
        g = np.isfinite(eb_p) & np.isfinite(pred)
        null[p] = _spearman(pred[g], eb_p[g])
    pv = float((np.abs(null) >= abs(obs)).mean())
    return obs, null, pv


def blockperm_null(x, y, pos, n_perm, seed):
    """Script 33 Null 2: shuffle position-block order of x against y.
    (Blocks have unequal sizes — this is the project's committed
    implementation, labelled the weaker association null.)"""
    rng = np.random.default_rng(seed)
    order = np.argsort(pos, kind="stable")
    xs, ys, ps = x[order], y[order], pos[order]
    cuts = np.flatnonzero(np.diff(ps)) + 1
    blocks = np.split(np.arange(len(xs)), cuts)
    obs = _spearman(xs, ys)
    null = np.empty(n_perm)
    for p in range(n_perm):
        idx = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        null[p] = _spearman(xs[idx], ys)
    pv = float((np.abs(null) >= abs(obs)).mean())
    return obs, null, pv


def report(label, obs, ci, p_null, null, p_boot, n, null_name,
           rederivation_primary=True):
    crosses = ci[0] < 0 < ci[1]
    print(f"  {label}")
    print(f"    rho={obs:+.4f}  CI95=[{ci[0]:+.4f},{ci[1]:+.4f}]"
          f"{'  (crosses 0)' if crosses else ''}  n={n}")
    print(f"    {null_name}: null mean={null.mean():+.4f} sd={null.std():.4f} "
          f"excess={obs - null.mean():+.4f}  p={pstr(p_null)}"
          f"  -> {'SURVIVES' if p_null < 0.05 else 'does NOT survive'}")
    if rederivation_primary:
        print(f"    position-cluster bootstrap: p={pstr(p_boot)}  "
              f"(N_BOOT={N_BOOT}; the re-derivation p above is the primary claim)")
    else:
        print(f"    position-cluster bootstrap: p={pstr(p_boot)}  "
              f"(N_BOOT={N_BOOT}; CI/p_boot is the primary claim here — the "
              f"block-perm p above is the weaker association null)")


if __name__ == "__main__":
    df = pd.read_csv(PROC / "task32_analysis_table.csv")
    df["region"] = assign_region(df["position"])

    # ---- G0: split re-derivation + zero calibration leakage ---------------
    print("=" * 74)
    print("G0  SPLIT RE-DERIVATION AND LEAKAGE CHECK (before any computation)")
    print("=" * 74)
    positions = np.sort(df["position"].unique())
    perm = np.random.default_rng(SEED).permutation(positions)
    n_cal_pos = math.ceil(CAL_FRAC * len(positions))
    cal_pos = set(perm[:n_cal_pos].tolist())
    df["split"] = np.where(df["position"].isin(cal_pos), "calibration", "held_out")
    saved = pd.read_csv(PROC / "task87_calibration_split.csv")
    chk = df[["hgvs_pro", "split"]].merge(saved, on="hgvs_pro", suffixes=("", "_saved"))
    same = bool((chk["split"] == chk["split_saved"]).all())
    n_cal = int((df["split"] == "calibration").sum())
    n_held = int((df["split"] == "held_out").sum())
    held_hgvs = set(df.loc[df["split"] == "held_out", "hgvs_pro"])
    cal_hgvs = set(df.loc[df["split"] == "calibration", "hgvs_pro"])
    leak = held_hgvs & cal_hgvs
    print(f"  seed={SEED}  calibration positions={n_cal_pos} rows={n_cal} | "
          f"held-out positions={len(positions) - n_cal_pos} rows={n_held}")
    print(f"  re-derived split == task87_calibration_split.csv : "
          f"{'PASS' if same else 'FAIL'}")
    print(f"  calibration/held-out row overlap in evaluation set: {len(leak)} "
          f"{'PASS' if not leak else 'FAIL'}")
    if not same or leak:
        print("*** G0 FAIL — split is not reproducible or leaks. Stop. ***")
        sys.exit(1)

    # ---- parameters (fit once by 87; never refit here) --------------------
    par = pd.read_csv(PROC / "task87_calibration_params.csv")
    p1 = par[par["arm"] == "phi1_wt"].iloc[0]
    p2 = par[par["arm"] == "phi2_a222v"].iloc[0]
    p2c = par[par["arm"] == "phi2_contrast_sens"].iloc[0]
    b1, c1 = float(p1["b"]), float(p1["c"])
    b2, c2 = float(p2["b"]), float(p2["c"])
    b2c, c2c = float(p2c["b"]), float(p2c["c"])
    print(f"\n  calibration loaded (fit once on calibration rows, script 87):")
    print(f"    phi1: b={b1:.6f} c={c1:.6f}  (target {p1['target_x']})")
    print(f"    phi2: b={b2:.6f} c={c2:.6f}  (target {p2['target_x']})")
    print(f"    phi2-contrast (their actual Eqn. 4 target): b={b2c:.6f} "
          f"c={c2c:.6f}  (calibration R2={float(p2c['r2_cal']):.4f} — poor fit, disclosed)")

    df["delta_cal"] = phi(df["esm2_score_a222v_bg"].to_numpy(), b2, c2) - \
                      phi(df["esm2_score"].to_numpy(), b1, c1)
    df["delta_cal_con"] = phi(df["esm2_score_a222v_bg"].to_numpy(), b2c, c2c) - \
                          phi(df["esm2_score"].to_numpy(), b1, c1)
    df["delta_same"] = phi(df["esm2_score_a222v_bg"].to_numpy(), b1, c1) - \
                       phi(df["esm2_score"].to_numpy(), b1, c1)

    # ---- G0b: full-data raw anchor reproduction ---------------------------
    full = df.dropna(subset=["delta_esm", "own_e_b"])
    anchor = float(_spearman(full["delta_esm"].to_numpy(),
                             full["own_e_b"].to_numpy()))
    ok_anchor = abs(anchor - ANCHOR_FULL_RAW) < 1e-9
    print(f"\nG0b  raw anchor reproduction: rho={anchor!r} vs established "
          f"{ANCHOR_FULL_RAW!r}")
    print(f"     |diff|={abs(anchor - ANCHOR_FULL_RAW):.3e}  "
          f"{'PASS' if ok_anchor else 'FAIL'}")
    if not ok_anchor:
        print("*** G0b FAIL — frame/column identity broken (AGENTS s5). Stop. ***")
        sys.exit(1)

    # ---- frames ------------------------------------------------------------
    e1 = df.dropna(subset=["delta_esm", "own_e_b", "GI_folinate_independent"]).copy()
    e1 = e1[e1["split"] == "held_out"].reset_index(drop=True)
    e2 = e1[(e1["f_bar_wt"] > 0) & (e1["f_bar_a222v"] > 0)].reset_index(drop=True)
    print(f"\nFRAMES  E1 (pair A) = {len(e1)} rows / {e1['position'].nunique()} positions")
    print(f"        E2 (pair B) = {len(e2)} rows / {e2['position'].nunique()} positions "
          f"(dropped from E1: {len(e1) - len(e2)} with fitness <= 0)")
    if len(e1) < 5000 or e1["position"].nunique() < 400 or len(e2) < 4000:
        print("*** FRAME SIZE GATE FAIL — pre-registered minimums not met. Stop. ***")
        sys.exit(1)

    # ---- eps_e (Nambiar Eqn. 3) on MTHFR ---------------------------------
    p3 = pd.read_csv(PROC / "phase3_analysis_table.csv")
    a_row = p3[p3["hgvs_pro"] == "p.Ala222Val"]
    assert len(a_row) == 1 and float(a_row["f_bar_wt"].iloc[0]) > 0, \
        "p.Ala222Val f_bar_wt not found as a single positive row"
    fA = float(a_row["f_bar_wt"].iloc[0])
    e2["eps_e"] = np.log(e2["f_bar_a222v"]) - np.log(e2["f_bar_wt"]) - np.log(fA)
    print(f"\n  eps_e = ln(f_bar_a222v) - ln(f_bar_wt) - ln(f_A222V), "
          f"f_A222V = p.Ala222Val f_bar_wt = {fA!r}")
    print(f"  N3b identity check: eps_m := delta_cal "
          f"(one-path reduction of their Eqn. 4; phi1(A222V) cancels)")

    # cross-construction references (AGENTS s5: verify direction on real rows)
    r_own = float(_spearman(e2["eps_e"].to_numpy(), e2["own_e_b"].to_numpy()))
    r_gi = float(_spearman(e2["eps_e"].to_numpy(), e2["GI_folinate_independent"].to_numpy()))
    print(f"  construction cross-reference (expected positive — two measures "
          f"of the same interaction):")
    print(f"    Spearman(eps_e, own_e_b) = {r_own:+.4f}")
    print(f"    Spearman(eps_e, GI_e.b)  = {r_gi:+.4f}")

    # ---- re-derivation machinery on E1 ------------------------------------
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2m, Mse = fit["e2"], fit["M_se"]
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in e1["hgvs_pro"]])
    Rs, Ss, Vs = e2m["resid"][src], Mse[src], e2m["valid"][src]
    own_eb = e1["own_e_b"].to_numpy()

    print("\n" + "=" * 74)
    print("SIGN-FLIP IDENTITY CHECKS (AGENTS s4 — test the test before trusting it)")
    print("=" * 74)
    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    okf = np.isfinite(chk_p) & np.isfinite(own_eb)
    d_p = float(np.abs(chk_p[okf] - own_eb[okf]).max())
    d_m = float(np.abs(chk_m[okf] + own_eb[okf]).max())
    print(f"  all-+1 flips reproduce own_e_b exactly: max|diff|={d_p:.3e}")
    print(f"  all--1 flips give exactly -own_e_b:     max|diff|={d_m:.3e}")
    if d_p > 1e-6 or d_m > 1e-6:
        print("*** IDENTITY CHECK FAILED — row alignment wrong. Stop. ***")
        sys.exit(1)

    results = []

    def boot(sub, xc, yc):
        r = position_cluster_bootstrap(sub, "position", xc, yc,
                                       n_boot=N_BOOT, seed=SEED)
        return r

    # ---- N3a: own_e_b primary (sign-flip re-derivation) -------------------
    print("\n" + "=" * 74)
    print(f"N3a  PRIMARY: calibrated vs raw shift, y = own_e_b "
          f"(E1, sign-flip re-derivation null, N_PERM={N_PERM})")
    print("=" * 74)
    for xc, kind in [("delta_esm", "raw"), ("delta_cal", "calibrated")]:
        r = boot(e1, xc, "own_e_b")
        obs, null, pv = signflip_null(e1[xc].to_numpy(), own_eb, Rs, Ss, Vs,
                                      N_PERM, SEED)
        centred = abs(null.mean()) < 2 * null.std() / np.sqrt(max(N_PERM, 1)) * 3
        report(f"{kind:11s} {xc} vs own_e_b",
               r["observed_rho"], (r["ci_lo"], r["ci_hi"]), pv, null,
               r["p_boot"], r["n_rows"], "sign-flip re-derivation null")
        print(f"    null-centring: null mean {'IS' if centred else 'is NOT'} "
              f"consistent with zero (script 33 convention)")
        results.append({"pair": "A_own_e_b", "arm": kind, "x": xc,
                        "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                        "ci_hi": r["ci_hi"], "p_null": pv,
                        "null": "signflip_rederivation", "p_boot": r["p_boot"],
                        "n": r["n_rows"]})

    print("\n" + "=" * 74)
    print("N3a-sec  y = GI_folinate_independent (published e.b; "
          "position-block permutation, the weaker null)")
    print("=" * 74)
    for xc, kind in [("delta_esm", "raw"), ("delta_cal", "calibrated")]:
        r = boot(e1, xc, "GI_folinate_independent")
        obs, null, pv = blockperm_null(e1[xc].to_numpy(),
                                       e1["GI_folinate_independent"].to_numpy(),
                                       e1["position"].to_numpy(), N_PERM, SEED)
        report(f"{kind:11s} {xc} vs GI e.b",
               r["observed_rho"], (r["ci_lo"], r["ci_hi"]), pv, null,
               r["p_boot"], r["n_rows"], "position-block permutation null",
               rederivation_primary=False)
        results.append({"pair": "A_gi_eb", "arm": kind, "x": xc,
                        "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                        "ci_hi": r["ci_hi"], "p_null": pv,
                        "null": "position_block_perm", "p_boot": r["p_boot"],
                        "n": r["n_rows"]})

    # ---- N3b: Nambiar's own epistasis (E2) --------------------------------
    print("\n" + "=" * 74)
    print(f"N3b  NAMBIAR EQN. 4 (one-path reduction) on MTHFR: "
          f"y = eps_e (their Eqn. 3); E2; block-perm null")
    print("  x arms: raw (E_raw) | N3b-LEVEL (phi2 level target) | "
          "N3b-LITERAL (their phi2 contrast target)")
    print("=" * 74)
    print("  LIMITATION: the sign-flip re-derivation null does not apply to")
    print("  eps_e (a log-ratio of condition means — no residual-refit")
    print("  structure); block-perm here is the weaker association null only.")
    for xc, kind in [("delta_esm", "raw (E_raw)"),
                     ("delta_cal", "N3b-LEVEL (phi2 level)"),
                     ("delta_cal_con", "N3b-LITERAL (their phi2)")]:
        r = boot(e2, xc, "eps_e")
        obs, null, pv = blockperm_null(e2[xc].to_numpy(),
                                       e2["eps_e"].to_numpy(),
                                       e2["position"].to_numpy(), N_PERM, SEED)
        report(f"{kind:24s} vs eps_e",
               r["observed_rho"], (r["ci_lo"], r["ci_hi"]), pv, null,
               r["p_boot"], r["n_rows"], "position-block permutation null",
               rederivation_primary=False)
        results.append({"pair": "B_eps_e", "arm": kind, "x": xc,
                        "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                        "ci_hi": r["ci_hi"], "p_null": pv,
                        "null": "position_block_perm", "p_boot": r["p_boot"],
                        "n": r["n_rows"]})

    # ---- N3c: raw vs calibrated side by side ------------------------------
    print("\n" + "=" * 74)
    print("N3c  RAW vs CALIBRATED, side by side, SAME held-out rows")
    print("=" * 74)
    print(f"  {'pair':12s} {'arm':11s} {'rho':>9s} {'CI95':>21s} "
          f"{'p_null':>8s} {'p_boot':>8s} {'n':>6s}")
    for row in results:
        print(f"  {row['pair']:12s} {row['arm']:11s} {row['rho']:>+9.4f} "
              f"[{row['ci_lo']:+.4f},{row['ci_hi']:+.4f}] "
              f"{row['p_null']:>8.4f} {row['p_boot']:>8.4f} {row['n']:>6d}")
    print(f"  full-data raw reference (all {len(full)} rows, NOT held out): "
          f"rho(delta_esm, own_e_b) = {anchor:+.6f}  (reproduced, G0b)")

    # ---- diagnostic: what delta_cal is made of (disclosed post-smoke) -----
    print("\n" + "=" * 74)
    print("DIAGNOSTIC  delta_cal composition (post-smoke addition, disclosed)")
    print("=" * 74)
    for c in ["delta_esm", "esm2_score", "esm2_score_a222v_bg"]:
        rr = float(_spearman(e1["delta_cal"].to_numpy(), e1[c].to_numpy()))
        print(f"  Spearman(delta_cal, {c:24s}) = {rr:+.4f}   (E1, held-out)")
    print(f"  spread sd(delta_esm)={e1['delta_esm'].std():.5f}  "
          f"sd(delta_cal)={e1['delta_cal'].std():.5f}  "
          f"ratio={e1['delta_cal'].std()/e1['delta_esm'].std():.3f}")
    print("  With b1=0.262004 != b2=0.143945, delta_cal = phi2(s_av)-phi1(s_wt)")
    print("  carries a curve-mismatch term in addition to the shift; the")
    print("  correlations above quantify how much of it is still the shift.")

    # ---- N3d: verdict per the pre-registered rule -------------------------
    a_raw = next(r for r in results if r["pair"] == "A_own_e_b" and r["arm"] == "raw")
    a_cal = next(r for r in results if r["pair"] == "A_own_e_b" and r["arm"] == "calibrated")
    m1 = abs(a_cal["rho"]) >= 0.26
    m2 = abs(a_cal["rho"]) >= 2 * abs(a_raw["rho"])
    sign_flip = np.sign(a_cal["rho"]) != np.sign(a_raw["rho"])
    print("\n" + "=" * 74)
    print("N3d  VERDICT (rule fixed in this docstring before running)")
    print("=" * 74)
    print(f"  raw    rho={a_raw['rho']:+.4f}  CI=[{a_raw['ci_lo']:+.4f},{a_raw['ci_hi']:+.4f}] "
          f"p_null={pstr(a_raw['p_null'])}")
    print(f"  cal    rho={a_cal['rho']:+.4f}  CI=[{a_cal['ci_lo']:+.4f},{a_cal['ci_hi']:+.4f}] "
          f"p_null={pstr(a_cal['p_null'])}")
    print(f"  M1 |rho_cal| >= 0.26 (Nambiar calibrated band floor): "
          f"{'MET' if m1 else 'NOT MET'}")
    print(f"  M2 |rho_cal| >= 2*|rho_raw| on same rows:            "
          f"{'MET' if m2 else 'NOT MET'}")
    if sign_flip:
        print("  *** SIGN CHANGE raw -> calibrated: flagged prominently ***")
    material = m1 or m2
    print(f"  -> {'MATERIAL MOVEMENT' if material else 'NOT MATERIAL'} "
          f"toward Nambiar's calibrated range (~0.26-0.38 in magnitude).")

    # ---- POST-HOC sensitivity (disclosed; printed after the verdict) ------
    print("\n" + "=" * 74)
    print("POST-HOC SENSITIVITY (disclosed — NOT part of the verdict above)")
    print("=" * 74)
    print("  delta_same = phi1(s_av) - phi1(s_wt): both scores through ONE")
    print("  curve (single-ruler calibrated shift), added after the")
    print("  composition diagnostic showed delta_cal is not a shift.")
    r = boot(e1, "delta_same", "own_e_b")
    obs, null, pv = signflip_null(e1["delta_same"].to_numpy(), own_eb, Rs, Ss, Vs,
                                  N_PERM, SEED)
    report("post-hoc   delta_same vs own_e_b",
           r["observed_rho"], (r["ci_lo"], r["ci_hi"]), pv, null,
           r["p_boot"], r["n_rows"], "sign-flip re-derivation null")
    rhow = float(_spearman(e1["delta_same"].to_numpy(), e1["delta_esm"].to_numpy()))
    print(f"    Spearman(delta_same, delta_esm) = {rhow:+.4f} (structure check)")
    print("    The pre-registered verdict above stands unchanged regardless of")
    print("    this arm's value; M1/M2 were fixed before this arm existed.")

    out = PROC / "task88_n3_results.csv"
    pd.DataFrame(results).to_csv(out, index=False)
    print(f"\nSaved to {out}")

    print("\n" + "=" * 74)
    print("LIMITATIONS (printed with the results — AGENTS s6)")
    print("=" * 74)
    print("  - one background / one direction: their two-path symmetrisation")
    print("    needs S(A222V|v), never scored (script 32 discloses the same).")
    print("  - phi's (-inf,0) ceiling leaves 35.2% of phi1's held-out targets")
    print("    (fitness>1) unreachable; it compresses the calibrated shift.")
    print("  - Spearman here vs Nambiar's Pearson: magnitudes comparable,")
    print("    literal numbers not.")
    print("  - the 80% set was held out from CALIBRATION only; the raw arm's")
    print("    value was knowable on all rows before this script (AGENTS s8: ")
    print("    split-half stability, not a fresh holdout, for the raw number).")
    print("  - N3b's inference rests on the weaker block-perm null (above).")

    print("\nSCRIPT 88 COMPLETE — rc=0.")
    sys.exit(0)
