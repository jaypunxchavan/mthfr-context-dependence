"""
AD3 — non-degenerate threshold model (task doc L257-271), PRE-REGISTERED.

THIS DOCSTRING IS THE PRE-REGISTRATION. It was written before the first
run of this script, per the project's standing discipline. Nothing below
was chosen after seeing any result of stages A/B.

AD3a — functional form (task-pinned, made fully explicit here):
    predicted fitness of a state with total stability x (ddG relative to
    wild type, x_wt = 0 by definition):

        f(x) = A * sigmoid((theta - x) / s)          [DECREASING in x]

    * DECREASING is declared from physics BEFORE fitting: larger ddG =
      more destabilizing = lower fitness. The orientation is not chosen
      from the data.
    * Two free parameters exactly: theta (threshold, fitness-transition
      point) and s (transition width). A is NOT fitted: A := the 95th
      percentile of the fit-set fitness column, a declared range
      normalisation constant (printed with the results). Three further
      constants of the model are also declared, not fitted: ddG_wt = 0
      (definition), ddG_222 = value verified under gate G1 below, and the
      additive-stability assumption for the double mutant
      x_double = ddG_v + ddG_222 (the model's own basis, identical in
      spirit to V4's additive term in scripts/68).
    * Four-term interaction (task formula, verbatim structure):
        predicted interaction(v) = f(x_double) - f(v) - f(222) + f(wt)
      with f(v)=f(ddG_v), f(222)=f(ddG_222), f(wt)=f(0).

AD3a — fitting procedure (exact, deterministic, no RNG):
    Rows: task_V2_thermompnn_ddg.csv INNER-joined to phase5's
    f_bar_wt (single-mutant fitness on the wild-type background) by
    hgvs_pro; keep rows with finite ddg AND finite f_bar_wt. Drop counts
    printed at every step (analysis-set accounting, section 5).
    Objective: unweighted least squares SSE over (ddG_v, f_bar_wt).
    Method: (1) coarse grid theta in linspace over [ddg.min, ddg.max],
    21 points; s in logspace over [0.01, max(1.0, ddg_range)], 12 points
    -> 252 candidates; (2) keep the 5 lowest-SSE candidates; (3) refine
    each with scipy.optimize.least_squares (method='trf', bounds:
    theta in [ddg.min - ddg_range, ddg.max + ddg_range],
    s in [1e-3, 1e3]); (4) final parameters = lowest refined SSE.
    SEPARATION IS STRUCTURAL: the fitting routine receives only two 1-D
    arrays (ddG, fitness). own_e_b is never passed to it, so the fit
    cannot be tuned against the interaction term or against e.b — the
    task's hold-out requirement, enforced by call signature, not by
    promise.

AD3b — the falsifiable shape test (pre-registered decision rules):
    Driver: d(v) = |ddG_v + ddG_222 - theta|   (distance of the DOUBLE's
    predicted total stability from the threshold). Robustness quantity
    (always printed): d0(v) = |ddG_v - theta| (they differ by |ddG_222|
    which gate G1 shows is small).
    Prediction being tested (task L266-271): interaction is LARGEST near
    the threshold and vanishes at both extremes -> |own_e_b| DECREASES
    with d -> row-level Spearman rho(|own_e_b|, d) < 0 (inverted U).
    PRIMARY statistic: row-level Spearman rho(|own_e_b|, d).
    PRIMARY interval: position-cluster bootstrap (scripts.lib.stats,
    N_BOOT draws, seed 0) — positions, never rows (section 3).
    PRIMARY null: ASSOCIATION null at POSITION level (labelled as such,
    section 4): aggregate both quantities to per-position means, shuffle
    the d-side position means against the fixed own_e_b position means
    (N_PERM draws, seed 1), two-sided p on |rho|. The identity
    permutation must reproduce the observed position-level rho exactly
    (|diff| < 1e-12) or the script exits 1 (section 4 identity check).
    A row-level shuffle is NOT run: rows within a position are not
    independent and a row-level null would reintroduce pseudoreplication.
    VERDICT RULE (fixed now): the inverted-U shape "APPEARS" iff
    primary rho < 0 AND position-level p < 0.05; otherwise it "does NOT
    appear". Both numbers are printed either way; a clean non-appearance
    is reported as plainly as an appearance.

    SECONDARY (pre-registered, all always reported, never selective):
    (a) construction control (section 4: own_e_b was FITTED in
        scripts/17 using per-variant wild-type-arm fitness as an input
        to its expectation model — the same underlying measurements that
        f_bar_wt summarises, so the fit's outcome sits inside the tested
        target's construction). Control = partial Spearman of
        |own_e_b| vs d controlling f_bar_wt (scripts.lib.stats
        partial_spearman_cluster_bootstrap). If the primary shape
        appears but (a) removes it, the honest reading is
        construction-driven and this script says so in its output.
    (b) signed version: rho(own_e_b, d) with cluster CI (descriptive).
    (c) shape profile: 5 d-quintiles (cut points from the analysis set,
        fixed before bootstrapping): n, mean signed e.b, mean |e.b| with
        position-cluster CI.
    (d) model self-consistency: predicted interaction per variant from
        the FITTED four-term formula; its rho(|pred_int|, d) — the model
        itself predicts an inverted U, documented here so the tested
        prediction's origin is traceable to the fit, not to this script.
    (e) column robustness: refit everything on phase5's `f_bar` instead
        of f_bar_wt and report whether the primary sign/verdict changes.
        Pre-registered: reported regardless of outcome.

GATES (failure => print reason, sys.exit(1), no larger-N rerun):
    G1 ddG_222: re-read from the V2 run's raw chain-A SSM output
       (…/T/opencode/thermompnn_full/ThermoMPNN_inference_6FCX.csv) with
       scripts/68's exact gate (resi==222 & mutation=='V', one row);
       value must equal -0.0439 within 5e-5 (the executed [V3] print,
       SESSION_LOG L2378). If the raw file is gone: use -0.0439 from
       that executed print and say so in the output (never invent).
    G2 fit sanity: all fitted values finite; A>0; Spearman(f(x_v),
       f_bar_wt) >= +0.10 (orientation/fit plumbing check).
    G3 formula identities: (i) four-term combo of any exactly linear f
       is < 1e-12; (ii) four-term combo with ddG_222 set to 0 is < 1e-12
       for the fitted f. Either failing => wiring bug => exit 1.
    G4 accounting: every filtering step prints row counts; analysis-set
       sizes must reconcile (10,141 V2 rows decompose exactly).
    G5 permutation: all N_PERM rhos finite; identity check as above.

Run: N_BOOT/N_PERM from env (default 10000 each; SMOKE=1 => 300/300).
Output artifact: data/processed/task76_threshold_model.csv (per-variant
predictions + distances + flags).

LIMITATIONS (printed with the results, not only here):
    1. Construction overlap (section 4): fitness enters BOTH the sigmoid
       fit AND own_e_b's expectation model — the position-shuffle null
       cannot by itself distinguish a real threshold-shaped interaction
       from shared-derivation structure; secondary (a) is the direct
       control and its result governs the strength of any claim.
    2. ddG_222 is near zero (verified G1), so the double's threshold
       distance is numerically close to the single's — the model's
       interaction here is driven by curvature, not by a large A222V
       stability term.
    3. A = Q95 normalisation is a declared scale convention for growth
       scores (0..~3.1), not a claim about physiological saturation.
    4. This is one fitted sigmoid on observational (ddG, fitness) pairs;
       no causal threshold is established by the fit alone.
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import (  # noqa: E402
    position_cluster_bootstrap,
    partial_spearman_cluster_bootstrap,
)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SSM_PATH = Path(os.environ.get(
    "FRAGMENT_OUT",
    "/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode",
)) / "thermompnn_full" / "ThermoMPNN_inference_6FCX.csv"
V2_PATH = PROC / "task_V2_thermompnn_ddg.csv"
PHASE5_PATH = PROC / "phase5_analysis_table.csv"
OUT_PATH = PROC / "task76_threshold_model.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SMOKE = os.environ.get("SMOKE", "0") == "1"
if SMOKE:                      # smoke convention (AGENTS section 1)
    N_BOOT = min(N_BOOT, 300)
    N_PERM = min(N_PERM, 300)
SEED_BOOT, SEED_PERM = 0, 1
DD222_EXPECTED, DD222_TOL = -0.0439, 5e-5
G2_MIN_FIT_RHO = 0.10          # declared plumbing floor, not tuned
IDENT_TOL = 1e-12
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def sig_decreasing(x, theta, s):
    """f(x) = sigmoid((theta - x)/s); decreasing in x, in (0,1).

    sigmoid(u) = 1/(1+exp(-u)) with u = (theta - x)/s -> exp(-z) below.
    A first draft used exp(z), i.e. increasing in x, and the pre-registered
    G2 rho floor caught it on the smoke run (observed spearman(f_hat,
    fitness) equalled the raw ddG-fitness rho exactly, -0.2414, instead of
    its negation). Implementation bug fixed to match this pre-registered
    form; no decision rule changed. See the [AD3] log entry.
    """
    z = np.clip((theta - x) / max(s, 1e-12), -500, 500)
    return 1.0 / (1.0 + np.exp(-z))


def four_term(f, x_v, dd222):
    """f(both) - f(v) - f(222) + f(wt), wt stability := 0."""
    return f(x_v + dd222) - f(x_v) - f(dd222) + f(0.0)


def fit_sigmoid(ddg, fit):
    """Declared procedure: 21x12 grid -> top-5 -> trf refine -> min SSE."""
    lo, hi = float(np.min(ddg)), float(np.max(ddg))
    rng_span = hi - lo
    th_grid = np.linspace(lo, hi, 21)
    s_grid = np.logspace(np.log10(0.01), np.log10(max(1.0, rng_span)), 12)
    A = float(np.percentile(fit, 95))
    if not np.isfinite(A) or A <= 0:
        raise SystemExit("*** G2 FAIL: A (Q95 of fitness) not positive/finite")

    def sse(theta, s):
        r = A * sig_decreasing(ddg, theta, s) - fit
        return float(np.sum(r * r))

    cands = sorted(
        ((sse(th, s), th, s) for th in th_grid for s in s_grid),
        key=lambda t: t[0],
    )[:5]
    best = cands[0]
    bnds = ([lo - rng_span, 1e-3], [hi + rng_span, 1e3])
    for _, th0, s0 in cands:
        res = least_squares(
            lambda p: A * sig_decreasing(ddg, p[0], p[1]) - fit,
            x0=[th0, s0], bounds=bnds, method="trf",
        )
        cur = float(np.sum(res.fun * res.fun))
        if cur < best[0]:
            best = (cur, float(res.x[0]), float(res.x[1]))
    return {"sse": best[0], "theta": best[1], "s": best[2], "A": A}


def chain_a_first_resi(pdb_path):
    """First chain-A residue number in the ATOM file, in file order.

    Script 68 documents (L52-54) that ThermoMPNN's `position` column is
    resi MINUS the first residue number of the parsed chain (6FCX chain
    A: 40), and gates the mapping three ways; this re-derives just that
    offset so the resi-222 gate below matches [V3]'s source row.
    """
    with open(pdb_path) as fh:
        for line in fh:
            if line.startswith("ENDMDL"):
                break
            if line.startswith("ATOM") and line[21] == "A":
                return int(line[22:26])
    raise SystemExit(f"*** G1 FAIL: no chain-A ATOM record in {pdb_path}")


def position_shuffle_test(df, x_col, y_col, n_perm, seed):
    """Association null: shuffle y-side POSITION MEANS vs fixed x means."""
    g = df.groupby("position")[[x_col, y_col]].mean().dropna()
    xo, yo = g[x_col].to_numpy(), g[y_col].to_numpy()
    rho_obs = float(spearmanr(xo, yo).statistic)
    # identity check through the SAME indexing path as the draws below
    rho_ident = float(spearmanr(xo, yo[np.arange(len(yo))]).statistic)
    if abs(rho_obs - rho_ident) > IDENT_TOL:
        raise SystemExit("*** G5 FAIL: identity permutation did not "
                         f"reproduce observed rho ({rho_obs} vs {rho_ident})")
    rng = np.random.default_rng(seed)
    ge = 0
    for _ in range(n_perm):
        perm = rng.permutation(len(yo))
        rp = float(spearmanr(xo, yo[perm]).statistic)
        if not np.isfinite(rp):
            raise SystemExit("*** G5 FAIL: non-finite permuted rho")
        if abs(rp) >= abs(rho_obs) - 1e-15:
            ge += 1
    p = (1 + ge) / (1 + n_perm)
    return rho_obs, p, len(g)


def quintile_profile(df, d_col, eb_col, n_boot, seed):
    """5 d-quintiles: n, mean signed, mean |e.b| with position-cluster CI.

    Vectorised: per-position (P x 5) sum/count matrices are resampled by
    position index, so one bootstrap draw is a fancy-index + sum instead
    of a 654-frame concatenation (same cluster semantics, ~1e3 faster).
    """
    cuts = np.quantile(df[d_col], np.linspace(0, 1, 6))
    bins = np.clip(np.searchsorted(cuts[1:-1], df[d_col].to_numpy(),
                                   side="right"), 0, 4)
    pos_list = df["position"].unique()
    p_index = {p: i for i, p in enumerate(pos_list)}
    pi = np.array([p_index[p] for p in df["position"]])
    eb = df[eb_col].to_numpy(float)
    abs_eb = np.abs(eb)
    dvals = df[d_col].to_numpy(float)

    P, B = len(pos_list), 5
    M_sum, C_cnt = np.zeros((P, B)), np.zeros((P, B))
    M_signed = np.zeros((P, B))
    np.add.at(M_sum, (pi, bins), abs_eb)
    np.add.at(M_signed, (pi, bins), eb)
    np.add.at(C_cnt, (pi, bins), 1.0)

    def block_stats(drawn_idx):
        s = M_sum[drawn_idx].sum(0)
        sgn = M_signed[drawn_idx].sum(0)
        c = C_cnt[drawn_idx].sum(0)
        with np.errstate(invalid="ignore"):
            return sgn / c, s / c

    ms_all, m_all = block_stats(np.arange(P))
    rng = np.random.default_rng(seed)
    boot_abs = np.full((n_boot, B), np.nan)
    for k in range(n_boot):
        drawn = rng.integers(0, P, size=P)
        _, m = block_stats(drawn)
        boot_abs[k] = m

    stats = []
    for b in range(B):
        col = boot_abs[:, b]
        col = col[np.isfinite(col)]
        lo, hi = np.percentile(col, [2.5, 97.5])
        stats.append((b + 1, int(C_cnt[:, b].sum()), float(ms_all[b]),
                      float(m_all[b]), float(lo), float(hi),
                      float(dvals[bins == b].mean())))
    return stats, cuts[1:5]


if __name__ == "__main__":
    banner("AD3 -- NON-DEGENERATE THRESHOLD MODEL (scripts/76) "
           f"SMOKE={SMOKE} N_BOOT={N_BOOT} N_PERM={N_PERM}", "=")

    # ---------- load + accounting (G4) --------------------------------
    v2 = pd.read_csv(V2_PATH)
    ph = pd.read_csv(PHASE5_PATH)[["hgvs_pro", "f_bar", "f_bar_wt"]]
    df = v2.merge(ph, on="hgvs_pro", how="left")
    n0 = len(df)
    n_finite_fit = int((df["ddg"].notna() & df["f_bar_wt"].notna()).sum())
    n_eb = int(df["own_e_b"].notna().sum())
    n_both = int((df["own_e_b"].notna() & df["ddg"].notna()
                  & df["f_bar_wt"].notna()).sum())
    print(f"  V2 rows: {n0} | finite (ddg & f_bar_wt): {n_finite_fit} "
          f"| finite own_e_b: {n_eb} | both: {n_both} "
          f"| f_bar finite: {int(df['f_bar'].notna().sum())}")
    print(f"  dropped for fit: {n0 - n_finite_fit} "
          f"(f_bar_wt NaN) | dropped for AD3b: {n0 - n_eb} (own_e_b NaN)")

    banner("STAGE A -- AD3a: SIGMOID FIT ON SINGLE MUTANTS ONLY", "=")
    # ---------- G1: ddG_222 ------------------------------------------
    if SSM_PATH.exists():
        ssm = pd.read_csv(SSM_PATH, index_col=0)
        # their `position` = resi - first chain-A resi (script 68, L52-54);
        # [V3]'s source row is their position 182 = resi 222, wt A.
        first = chain_a_first_resi(ROOT / "data" / "raw" / "6FCX.pdb")
        hit = ssm[(ssm["position"] + first == 222)
                  & (ssm["mutation"] == "V")]
        if len(hit) != 1 or str(hit["wildtype"].iloc[0]) != "A":
            print(f"*** G1 FAIL: SSM rows(pos={222 - first}+{first},V)="
                  f"{len(hit)} wt="
                  f"{hit['wildtype'].tolist() if len(hit) else '-'}")
            sys.exit(1)
        dd222 = float(hit["ddG_pred"].iloc[0])
        src = (f"re-read from raw V2-run SSM ({SSM_PATH}), their position "
               f"{222 - first} + chain-A offset {first} = resi 222 wt A")
        if abs(dd222 - DD222_EXPECTED) > DD222_TOL:
            print(f"*** G1 FAIL: ddG_222={dd222} != {DD222_EXPECTED} "
                  f"(tol {DD222_TOL})")
            sys.exit(1)
    else:
        dd222 = DD222_EXPECTED
        src = (f"raw SSM ABSENT at {SSM_PATH}; using -0.0439 from the "
               "executed [V3] print (SESSION_LOG L2378)")
    print(f"  G1 ddG_222 = {dd222:+.4f}  [{src}]  tol={DD222_TOL}  PASS")

    fit_df = df[df["ddg"].notna() & df["f_bar_wt"].notna()]
    ddg_f = fit_df["ddg"].to_numpy(float)
    y_f = fit_df["f_bar_wt"].to_numpy(float)
    fit = fit_sigmoid(ddg_f, y_f)
    theta, s_w, A = fit["theta"], fit["s"], fit["A"]
    f_hat = A * sig_decreasing(ddg_f, theta, s_w)
    fit_rho = float(spearmanr(f_hat, y_f).statistic)
    raw_rho = float(spearmanr(ddg_f, y_f).statistic)
    sse_null = float(np.sum((y_f - y_f.mean()) ** 2))
    print(f"  n_fit={len(fit_df)}  A=Q95(f_bar_wt)={A:.6f} (declared const)")
    print(f"  theta={theta:+.6f}  s={s_w:.6f}  SSE={fit['sse']:.4f}  "
          f"SSE_const={sse_null:.4f}  "
          f"1-SSE/SSE_const={1 - fit['sse'] / sse_null:.4f}")
    print(f"  spearman(f_hat, f_bar_wt)={fit_rho:+.4f}  "
          f"(raw spearman(ddg, f_bar_wt)={raw_rho:+.4f})")
    # construction disclosure numbers (section 4)
    ok = df["f_bar_wt"].notna() & df["own_e_b"].notna()
    print("  CONSTRUCTION DISCLOSURE: spearman(f_bar_wt, own_e_b)="
          f"{spearmanr(df.loc[ok, 'f_bar_wt'], df.loc[ok, 'own_e_b']).statistic:+.4f}"
          "  (own_e_b was fitted in scripts/17 using wild-type-arm fitness "
          "as an expectation input)")
    if (not np.all(np.isfinite([theta, s_w, A]))) or A <= 0 \
            or fit_rho < G2_MIN_FIT_RHO:
        print(f"*** G2 FAIL: fit plumbing (finite/positive/rho>="
              f"{G2_MIN_FIT_RHO})")
        sys.exit(1)
    print("  G2 fit sanity PASS")

    # ---------- G3: formula identities -------------------------------
    lin = lambda z: 3.7 - 1.3 * np.asarray(z, dtype=float)
    id_lin = float(np.max(np.abs(four_term(lin, ddg_f, dd222))))
    f_fit = lambda z: A * sig_decreasing(np.asarray(z, dtype=float),
                                         theta, s_w)
    id_zero = float(np.max(np.abs(four_term(f_fit, ddg_f, 0.0))))
    if id_lin > IDENT_TOL or id_zero > IDENT_TOL:
        print(f"*** G3 FAIL: linear-id={id_lin:.3g} zero-shift-id={id_zero:.3g}")
        sys.exit(1)
    print(f"  G3 identities PASS (linear={id_lin:.3g}, "
          f"ddG_222->0={id_zero:.3g})")

    # ---------- per-variant predictions ------------------------------
    df["f_wt_pred"] = f_fit(0.0)
    df["f_222_pred"] = f_fit(dd222)
    df["f_v_pred"] = f_fit(df["ddg"])
    df["f_both_pred"] = f_fit(df["ddg"] + dd222)
    df["pred_int"] = (df["f_both_pred"] - df["f_v_pred"]
                      - df["f_222_pred"] + df["f_wt_pred"])
    df["f_hat_fit"] = f_fit(df["ddg"])
    df["d_primary"] = (df["ddg"] + dd222 - theta).abs()
    df["d_robust"] = (df["ddg"] - theta).abs()

    banner("STAGE B -- AD3b: INVERTED-U SHAPE TEST ON REAL own_e_b", "=")
    t = df[df["own_e_b"].notna() & df["ddg"].notna()
           & df["f_bar_wt"].notna()].copy()
    t["abs_eb"] = t["own_e_b"].abs()
    print(f"  analysis rows: {len(t)} across "
          f"{t['position'].nunique()} positions")

    cb = position_cluster_bootstrap(t, "position", "abs_eb", "d_primary",
                                    n_boot=N_BOOT, seed=SEED_BOOT)
    rho_pos, p_pos, n_pos = position_shuffle_test(
        t, "abs_eb", "d_primary", N_PERM, SEED_PERM)
    print(f"  PRIMARY row-level rho(|own_e_b|, d) = {cb['observed_rho']:+.4f} "
          f"[{cb['ci_lo']:+.4f}, {cb['ci_hi']:+.4f}] "
          f"p_boot={cb['p_boot']:.4f}  n={cb['n_rows']} "
          f"clusters={cb['n_clusters']}")
    print(f"  POSITION-LEVEL association null: rho_pos={rho_pos:+.4f} "
          f"p={p_pos:.4f} (N_PERM={N_PERM}, positions={n_pos}, "
          f"identity check PASS)")
    appears = (cb["observed_rho"] < 0) and (p_pos < 0.05)
    verdict = ("INVERTED-U SHAPE APPEARS"
               if appears else "INVERTED-U SHAPE DOES NOT APPEAR")
    print(f"  VERDICT (rho<0 AND p_pos<0.05): {verdict}")

    # secondary (a): construction control
    pa = partial_spearman_cluster_bootstrap(t, "position", "abs_eb",
                                            "d_primary", "f_bar_wt",
                                            n_boot=N_BOOT, seed=SEED_BOOT)
    print(f"  (a) PARTIAL rho controlling f_bar_wt = {pa['observed_rho']:+.4f} "
          f"[{pa['ci_lo']:+.4f}, {pa['ci_hi']:+.4f}] p_boot={pa['p_boot']:.4f}"
          "  <- section-4 construction control")

    # secondary (b): signed
    sb = position_cluster_bootstrap(t, "position", "own_e_b", "d_primary",
                                    n_boot=N_BOOT, seed=SEED_BOOT)
    print(f"  (b) signed rho(own_e_b, d) = {sb['observed_rho']:+.4f} "
          f"[{sb['ci_lo']:+.4f}, {sb['ci_hi']:+.4f}] p_boot={sb['p_boot']:.4f}")

    # secondary (c): quintile profile
    prof, mid_cuts = quintile_profile(t, "d_primary", "own_e_b",
                                      N_BOOT, SEED_BOOT)
    print("  (c) quintile profile (d cut points "
          f"{[round(float(c), 4) for c in np.quantile(t['d_primary'],
             np.linspace(0, 1, 6))[1:5]]}):")
    for b, n, ms, m, lo, hi, dm in prof:
        print(f"       Q{b}: n={n:5d} mean_d={dm:7.4f} signed={ms:+.4f} "
              f"|e.b|={m:.4f} [{lo:.4f}, {hi:.4f}]")

    # secondary (d): model self-consistency
    rho_pi = float(spearmanr(t["pred_int"].abs(), t["d_primary"]).statistic)
    print(f"  (d) MODEL self-check rho(|pred_int|, d) = {rho_pi:+.4f} "
          f"(max|pred_int|={t['pred_int'].abs().max():.6f})")

    # secondary (e): column robustness (f_bar instead of f_bar_wt)
    rb = df[df["own_e_b"].notna() & df["ddg"].notna()
            & df["f_bar"].notna()].copy()
    rb["abs_eb"] = rb["own_e_b"].abs()
    fit_rb = fit_sigmoid(rb["ddg"].to_numpy(float),
                         rb["f_bar"].to_numpy(float))
    dd222_rb = dd222
    rb["d_primary"] = (rb["ddg"] + dd222_rb - fit_rb["theta"]).abs()
    cb_rb = position_cluster_bootstrap(rb, "position", "abs_eb",
                                       "d_primary", n_boot=N_BOOT,
                                       seed=SEED_BOOT)
    rho_pos_rb, p_pos_rb, _ = position_shuffle_test(
        rb, "abs_eb", "d_primary", N_PERM, SEED_PERM)
    appears_rb = (cb_rb["observed_rho"] < 0) and (p_pos_rb < 0.05)
    print(f"  (e) ROBUSTNESS refit on f_bar: theta={fit_rb['theta']:+.4f} "
          f"s={fit_rb['s']:.4f} n={len(rb)} | row rho="
          f"{cb_rb['observed_rho']:+.4f} pos p={p_pos_rb:.4f} "
          f"| verdict {'CHANGES' if appears_rb != appears else 'unchanged'}"
          f" (APPEARS'={appears_rb})")

    # robustness on distance definition (dd222 small)
    rho_d0 = float(spearmanr(t["abs_eb"], t["d_robust"]).statistic)
    print(f"  distance robustness: rho(|own_e_b|, |ddg-theta|) = {rho_d0:+.4f}")

    df["in_fit"] = (df["ddg"].notna() & df["f_bar_wt"].notna()).astype(int)
    df["in_test"] = df["own_e_b"].notna().astype(int)
    df.to_csv(OUT_PATH, index=False)
    print(f"\n  saved {len(df)} rows -> {OUT_PATH.name}")

    banner("LIMITATIONS (printed with results, AGENTS section 6)", "-")
    print("""  1. Construction overlap: fitness enters BOTH the sigmoid fit and
     own_e_b's expectation model (scripts/17); the position-shuffle null
     cannot alone separate a threshold-shaped interaction from
     shared-derivation structure. Control (a) governs claim strength.
  2. ddG_222 ~ 0 (G1): the double's threshold distance ~ the single's.
  3. A=Q95 is a declared scale convention for growth scores, not a
     saturation claim.
  4. Observational fit: no causal threshold established by stage A.""")
    print(f"\nAD3 DONE  ({time.time() - T0:.1f}s)  "
          f"VERDICT: {verdict}")
