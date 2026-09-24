"""AE4 — Does shift magnitude predict shift accuracy? (task doc L347-355)
PRE-REGISTERED: this docstring was written before any bootstrap ran.

Task: "Bin variants by |delta_ESM| (quartiles or deciles, pre-register the
choice) and compute the delta_ESM-vs-e.b correlation within each bin.
Report whether accuracy improves, stays flat, or worsens as shift
magnitude increases. State the result plainly, including if it supports
the 'most confidently wrong where it moves most' framing — this is a
strong, memorable claim ONLY if the data actually shows it; do not reach
for that framing if the bins are flat or noisy."

DISCLOSURE (AGENTS s6): the anchor gate below (G2) was verified in a
pre-check BEFORE this docstring was written — that pre-check printed the
four within-bin point estimates as a side effect (no CIs, no bootstrap).
The design below (quartiles, paired position-cluster bootstrap, CI-gated
framing) had already been drafted before that peek; the decision rule is
the direct operationalization of the task's own wording above (improve /
flat / worsen decided by the top-vs-bottom CI; framing permitted ONLY
under a significant-worsening + significant-negative-top-bin condition),
i.e. written to test the task's claim, not to produce a direction. The
peek is stated here in the script itself per AGENTS s6.

FROZEN DESIGN
- FRAME: data/processed/task32_analysis_table.csv, drop rows with
  missing own_e_b (delta_esm has no NaN). e.b := own_e_b — the project's
  registered primary e.b (script 32's primary row "signed, own e_b";
  AA4's detection-floor statistic; scripts 47/49/65/71/73/74 anchor on
  the same value). The published-e.b variant (anchor -0.07070516222228716)
  is NOT re-binned here (disclosed limitation, not a silent skip).
- BINS: QUARTILES of |delta_ESM| (choice over deciles pre-registered:
  ~2,689 variants/bin keeps within-bin rho estimates stable; deciles are
  NOT run). Edges = 25/50/75 percentiles computed ONCE on the observed
  frame (fixed membership, not recomputed per draw); a value equal to an
  edge goes to the higher bin (searchsorted side="right").
- PER BIN (primary): Spearman rho(delta_esm, own_e_b) — signed values,
  the same statistic family as the -0.088118 anchor. Secondary: Spearman
  rho(|delta_esm|, |own_e_b|), reported as-is, NO decision rule.
- ACCURACY DIRECTION (stated before running): positive correlation =
  model shift aligned with measured burden = more accurate; higher
  (more positive) within-bin rho = better accuracy. Improve = rho rises
  with magnitude; worsen = rho falls.
- BOOTSTRAP: position-cluster (the 654 positions are the unit;
  resampled with replacement; each draw's 654 sampled positions bring
  ALL their variants), paired — one draw feeds all four bins and both
  contrasts so the top-vs-bottom comparison is within-draw. N_BOOT env
  default 10,000, seed 0. Per-draw ranking recomputed (re-derivation).
- CONTRASTS: Delta_signed = rho_signed(Q4) - rho_signed(Q1) decides
  improve/flat/worsen (two-sided 95% percentile CI + two-sided p).
  Delta_abs = rho_abs(Q4) - rho_abs(Q1) reported as secondary.
- FROZEN DECISION RULE (task's own wording operationalized):
    Delta_signed CI strictly > 0            -> "IMPROVES with magnitude"
    Delta_signed CI strictly < 0            -> "WORSENS with magnitude"
      AND ONLY THEN, framing check:
        Q4's within-bin signed rho CI strictly < 0
            -> "most confidently wrong where it moves most" framing is
               PERMITTED (used), reported with effect sizes.
        Q4 CI includes 0
            -> trend reported as worsens; framing NOT used (task: only
               if the data actually shows it).
    Delta_signed CI includes 0              -> "FLAT: no detectable
      trend" — framing NOT used (task's explicit instruction).
  Effect sizes (bin rhos, Delta magnitude, n variants, n positions) are
  printed alongside every significance statement (AGENTS s3).

GATES (failure => print, sys.exit(1); no retry, no rule change):
  G1 frame: table 11,344 rows / 654 positions / 0 delta NaN; 587
     missing own_e_b; analysis frame 10,757 rows / 654 positions /
     0 NaN in either column. EXCLUSION SKEW CHECK printed (AGENTS s5):
     mean|delta_esm| and region shares of the 587 excluded vs included.
  G2 anchor: overall Spearman(delta_esm, own_e_b) on the frame equals
     -0.08811806424891734 within 1e-9 (script 32 saved; two-source
     identity). Disagree -> STOP.
  G3 bins: the four bins partition the frame exactly (sizes sum to
     10,757), each >= 1,000 variants, edges strictly increasing.
  G4 bootstrap sanity: every per-draw statistic finite (NaN draws
     excluded and counted; >50% NaN -> fail), draw count == N_BOOT,
     every reported point estimate inside its own 95% CI (else
     resampling broken -> fail; do not raise N).
  G5 CSV accounting: bins CSV == 4 rows; results CSV == 3 rows.

SMOKE: N_BOOT=300 (full path minus draw count), measure runtime and
extrapolate before the full run (AGENTS s1; if projection > 30 min,
stop and reassess instead of burning the time). Full: N_BOOT=10000.

OUTPUTS: data/processed/task84_ae4_bins.csv (4 rows),
task84_ae4_results.csv (3 rows: anchor, Delta_signed, Delta_abs).
No existing script/lib/result modified. Next free script number: 85.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
T32 = ROOT / "data" / "processed" / "task32_analysis_table.csv"
OUT_BINS = ROOT / "data" / "processed" / "task84_ae4_bins.csv"
OUT_RES = ROOT / "data" / "processed" / "task84_ae4_results.csv"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
ANCHOR_RHO = -0.08811806424891734   # script 32 primary "signed, own e_b"
ANCHOR_TOL = 1e-9
MIN_BIN = 1000
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def pfmt(p):
    return "<1/N" if p == 0 else f"{p:.4f}"


def boot_checks(label, draws, obs, lo, hi, n_nan):
    if n_nan > 0:
        print(f"  ({label}: {n_nan} NaN draws excluded)")
    if draws.size < 0.5 * N_BOOT:
        gfail(f"G4 FAIL ({label}): >50% NaN draws — statistic broken")
    if not np.isfinite(obs):
        gfail(f"G4 FAIL ({label}): point estimate non-finite")
    if not (lo <= obs <= hi):
        gfail(f"G4 FAIL ({label}): obs {obs:.6f} outside own 95% CI "
              f"[{lo:.6f},{hi:.6f}] — resampling broken (not raising N)")


if __name__ == "__main__":
    banner(f"AE4 — |delta_ESM| quartiles vs delta_ESM-own_e_b accuracy "
           f"(scripts/84)  N_BOOT={N_BOOT} seed={SEED}")

    # ---------------- frame + gates --------------------------------------
    full = pd.read_csv(T32)
    if len(full) != 11344 or full["position"].nunique() != 654 \
            or int(full["delta_esm"].isna().sum()) != 0:
        gfail(f"G1 FAIL: table {len(full)} rows / "
              f"{full['position'].nunique()} positions / "
              f"{int(full['delta_esm'].isna().sum())} delta NaN != "
              f"11,344 / 654 / 0")
    n_excl = int(full["own_e_b"].isna().sum())
    frame = full.dropna(subset=["own_e_b"]).reset_index(drop=True)
    if len(frame) != 10757 or frame["position"].nunique() != 654 \
            or int(frame["own_e_b"].isna().sum()) != 0:
        gfail(f"G1 FAIL: frame {len(frame)} rows / "
              f"{frame['position'].nunique()} positions / "
              f"{int(frame['own_e_b'].isna().sum())} own_e_b NaN != "
              f"10,757 / 654 / 0 (table missing-own_e_b rows = "
              f"{n_excl})")
    print(f"  G1 PASS: table 11,344/654, delta NaN 0; {n_excl} rows "
          f"missing own_e_b -> frame 10,757 rows / 654 positions / "
          f"0 NaN (every position survives the drop)")
    # exclusion skew check (AGENTS s5): do the dropped rows differ?
    excl = full[full["own_e_b"].isna()]
    inc_mad = float(frame["delta_esm"].abs().mean())
    ex_mad = float(excl["delta_esm"].abs().mean())
    print(f"  EXCLUSION SKEW CHECK: excluded {n_excl} rows mean|delta| "
          f"{ex_mad:.6f} vs included {inc_mad:.6f} "
          f"(ratio {ex_mad / inc_mad:.3f}); region shares excluded "
          f"{(excl['region'].value_counts(normalize=True).sort_index().round(3).to_dict())} "
          f"included "
          f"{(frame['region'].value_counts(normalize=True).sort_index().round(3).to_dict())}")

    r_all = float(spearmanr(frame["delta_esm"], frame["own_e_b"]).statistic)
    if abs(r_all - ANCHOR_RHO) > ANCHOR_TOL:
        gfail(f"G2 FAIL: recomputed rho {r_all!r} != anchor "
              f"{ANCHOR_RHO!r} (two sources disagree)")
    print(f"  G2 PASS: overall Spearman(delta_esm, own_e_b) = "
          f"{r_all!r} == script-32 anchor within 1e-9")

    # labeled-example print (AGENTS s5 — sign conventions, not assumed)
    i_hi = int(frame["delta_esm"].idxmax())
    i_lo = int(frame["delta_esm"].idxmin())
    i_eb = int(frame["own_e_b"].idxmax())
    for tag, i in (("max delta_esm", i_hi), ("min delta_esm", i_lo),
                   ("max own_e_b", i_eb)):
        r = frame.loc[i]
        print(f"  labeled {tag}: {r.hgvs_pro} delta_esm="
              f"{r.delta_esm:+.6f} own_e_b={r.own_e_b:+.6f} "
              f"region={int(r.region)}")

    # ---------------- quartile bins --------------------------------------
    absd = frame["delta_esm"].abs().to_numpy()
    edges = np.percentile(absd, [25, 50, 75])
    if not (edges[0] < edges[1] < edges[2]):
        gfail(f"G3 FAIL: non-increasing edges {edges}")
    bidx = np.searchsorted(edges, absd, side="right")
    sizes = [int((bidx == k).sum()) for k in range(4)]
    if sum(sizes) != 10757 or min(sizes) < MIN_BIN:
        gfail(f"G3 FAIL: bins {sizes} do not partition 10,757 or a bin "
              f"below {MIN_BIN}")
    print(f"  G3 PASS: quartile edges [{edges[0]:.6f},{edges[1]:.6f},"
          f"{edges[2]:.6f}] -> bin sizes {sizes} (sum 10,757)")

    delta = frame["delta_esm"].to_numpy()
    ebb = frame["own_e_b"].to_numpy()
    abs_ebb = np.abs(ebb)
    n_pos = 654
    pos_vals = frame["position"].to_numpy()
    uniq = np.sort(np.unique(pos_vals))
    if len(uniq) != n_pos:
        gfail(f"G1 FAIL: {len(uniq)} unique positions != 654")
    rows_per_pos = [np.flatnonzero(pos_vals == p) for p in uniq]

    def rhos_for(rows):
        out = np.empty(8)
        for k in range(4):
            rk = rows[bidx[rows] == k]
            out[k] = float(spearmanr(delta[rk], ebb[rk]).statistic)
            out[4 + k] = float(spearmanr(np.abs(delta[rk]),
                                         abs_ebb[rk]).statistic)
        return out

    obs_all = rhos_for(np.arange(len(frame)))
    if not np.all(np.isfinite(obs_all)):
        gfail("G4 FAIL: non-finite observed within-bin rho")
    rho_s = obs_all[:4]
    rho_a = obs_all[4:]

    rng = np.random.default_rng(SEED)
    draws = np.empty((N_BOOT, 8))
    for b in range(N_BOOT):
        sel = rng.integers(0, n_pos, n_pos)
        rows = np.concatenate([rows_per_pos[i] for i in sel])
        draws[b] = rhos_for(rows)
    n_nan = int((~np.isfinite(draws)).sum())
    finite = np.isfinite(draws).all(axis=1)
    d = draws[finite]

    lo_s, hi_s = np.percentile(d[:, :4], [2.5, 97.5], axis=0)
    lo_a, hi_a = np.percentile(d[:, 4:], [2.5, 97.5], axis=0)
    for k in range(4):
        p_s = min(2.0 * min((d[:, k] <= 0).mean(),
                            (d[:, k] >= 0).mean()), 1.0)
        p_a = min(2.0 * min((d[:, 4 + k] <= 0).mean(),
                            (d[:, 4 + k] >= 0).mean()), 1.0)
        boot_checks(f"Q{k + 1} signed", d[:, k], rho_s[k],
                    lo_s[k], hi_s[k], n_nan)
        boot_checks(f"Q{k + 1} abs", d[:, 4 + k], rho_a[k],
                    lo_a[k], hi_a[k], n_nan)

    d_sig = d[:, 3] - d[:, 0]
    d_abs = d[:, 7] - d[:, 4]
    ds_lo, ds_hi = np.percentile(d_sig, [2.5, 97.5])
    da_lo, da_hi = np.percentile(d_abs, [2.5, 97.5])
    ds_p = min(2.0 * min((d_sig <= 0).mean(), (d_sig >= 0).mean()), 1.0)
    da_p = min(2.0 * min((d_abs <= 0).mean(), (d_abs >= 0).mean()), 1.0)
    ds_obs = float(rho_s[3] - rho_s[0])
    da_obs = float(rho_a[3] - rho_a[0])
    boot_checks("Delta_signed", d_sig, ds_obs, ds_lo, ds_hi, n_nan)
    boot_checks("Delta_abs", d_abs, da_obs, da_lo, da_hi, n_nan)
    if finite.sum() != N_BOOT:
        print(f"  (draw rows with any NaN excluded: {N_BOOT - finite.sum()})")

    # ---------------- report ---------------------------------------------
    banner("AE4a — within-bin accuracy (Spearman delta_ESM vs own_e_b) "
           "by |delta_ESM| quartile")
    print(f"  frame 10,757 variants / 654 positions; overall rho = "
          f"{r_all:+.6f} (anchor)")
    p_s_arr = np.empty(4)
    p_a_arr = np.empty(4)
    for k in range(4):
        p_s_arr[k] = min(2.0 * min((d[:, k] <= 0).mean(),
                                   (d[:, k] >= 0).mean()), 1.0)
        p_a_arr[k] = min(2.0 * min((d[:, 4 + k] <= 0).mean(),
                                   (d[:, 4 + k] >= 0).mean()), 1.0)
    bins_rows = []
    for k in range(4):
        sub = frame[bidx == k]
        lo_e = edges[k - 1] if k > 0 else 0.0
        hi_e = edges[k] if k < 3 else float("inf")
        print(f"  Q{k + 1} |delta| in [{lo_e:.6f}, {hi_e:.4g}): "
              f"n={len(sub)} pos={sub['position'].nunique()} "
              f"rho_signed={rho_s[k]:+.6f} [{lo_s[k]:+.6f},"
              f"{hi_s[k]:+.6f}] p={pfmt(p_s_arr[k])} | rho_abs="
              f"{rho_a[k]:+.6f} [{lo_a[k]:+.6f},{hi_a[k]:+.6f}] "
              f"p={pfmt(p_a_arr[k])}")
        bins_rows.append(dict(
            bin=f"Q{k + 1}", n_var=len(sub),
            n_pos=int(sub["position"].nunique()),
            edge_lo=lo_e, edge_hi=hi_e,
            rho_signed=rho_s[k], ci_lo=lo_s[k], ci_hi=hi_s[k],
            p_signed=p_s_arr[k],
            rho_abs=rho_a[k], abs_ci_lo=lo_a[k], abs_ci_hi=hi_a[k],
            p_abs=p_a_arr[k]))
    banner("CONTRASTS (paired position bootstrap, seed 0)")
    print(f"  Delta_signed = rho(Q4) - rho(Q1) = {ds_obs:+.6f} "
          f"[{ds_lo:+.6f},{ds_hi:+.6f}] p={pfmt(ds_p)}")
    print(f"  Delta_abs (secondary, |.| vs |.|) = {da_obs:+.6f} "
          f"[{da_lo:+.6f},{da_hi:+.6f}] p={pfmt(da_p)}")
    print(f"  effect sizes: per-bin signed rho "
          f"{[f'{r:+.4f}' for r in rho_s]}; |.| rho "
          f"{[f'{r:+.4f}' for r in rho_a]}; Delta magnitude "
          f"{abs(ds_obs):.6f} correlation units")

    # ---------------- frozen verdict -------------------------------------
    banner("VERDICT (frozen rule; stated before any bootstrap ran)")
    if ds_hi < 0:
        if hi_s[3] < 0:
            verdict = (
                "WORSENS with shift magnitude (Delta_signed CI strictly "
                "below 0) AND the top quartile is significantly "
                "anti-aligned (Q4 signed rho CI strictly below 0) — the "
                "data DOES support the 'most confidently wrong where it "
                "moves most' framing; used here as the task permits, "
                "with the effect sizes above (rho Q1 to Q4: "
                f"{rho_s[0]:+.6f} -> {rho_s[3]:+.6f}; Delta "
                f"{ds_obs:+.6f} [{ds_lo:+.6f},{ds_hi:+.6f}]).")
        else:
            verdict = (
                "WORSENS with shift magnitude (Delta_signed CI strictly "
                "below 0), BUT Q4's within-bin rho CI includes 0 — trend "
                "reported as-is; the 'most confidently wrong' framing is "
                "NOT used (task: only if the data actually shows it).")
    elif ds_lo > 0:
        verdict = (
            "IMPROVES with shift magnitude (Delta_signed CI strictly "
            "above 0): within-bin accuracy rises from Q1 to Q4; framing "
            "not applicable. Effect sizes above.")
    else:
        verdict = (
            "FLAT: Delta_signed CI includes 0 — no detectable trend in "
            "within-bin accuracy as shift magnitude grows; the 'most "
            "confidently wrong where it moves most' framing is NOT used "
            "(task's explicit instruction for flat or noisy bins).")
    print(f"  (a) Delta_signed CI < 0: {ds_hi < 0} | (b) Q4 signed rho "
          f"CI < 0: {hi_s[3] < 0} | CI includes 0: {ds_lo <= 0 <= ds_hi}")
    print(f"  VERDICT: {verdict}")

    # ---------------- outputs + limitations -------------------------------
    pd.DataFrame(bins_rows).to_csv(OUT_BINS, index=False)
    pd.DataFrame([
        dict(statistic="overall_rho_anchor", value=r_all,
             ci_lo=np.nan, ci_hi=np.nan, p_boot=np.nan,
             note="== script-32 -0.08811806424891734 (G2)"),
        dict(statistic="Delta_signed_Q4_minus_Q1", value=ds_obs,
             ci_lo=ds_lo, ci_hi=ds_hi, p_boot=ds_p,
             note="primary: decides improve/flat/worsen"),
        dict(statistic="Delta_abs_Q4_minus_Q1", value=da_obs,
             ci_lo=da_lo, ci_hi=da_hi, p_boot=da_p,
             note="secondary |.| vs |.|, no decision rule"),
    ]).to_csv(OUT_RES, index=False)
    print(f"\n  saved 4 rows -> {OUT_BINS.name}; 3 rows -> "
          f"{OUT_RES.name}")
    banner("LIMITATIONS (printed with results, AGENTS s6)", "-")
    print(f"""  1. e.b = own_e_b (registered primary); the published-e.b
     companion (anchor -0.07070516222228716) was NOT re-binned — one e.b
     definition, not a robustness sweep.
  2. Quartiles (not deciles) pre-registered for within-bin stability;
     deciles not run.
  3. Q4's signed delta_esm is two-tailed by construction (|d| >= q75),
     so its signed within-bin rho spans both tails; the |.|-vs-|.|
     secondary complements it.
  4. Bin membership fixed by observed edges (not recomputed per draw);
     resampling unit is the position (654), paired across bins.
  5. Position composition differs by bin (Q4 covers fewer positions than
     Q1 — printed per bin); draws may include positions absent from a
     bin.
  6. Correlation is association, not calibration: 'accuracy' here is
     defined (frozen) as alignment between model shift and measured
     burden, positive = better.
  7. The anchor pre-check before this script was written printed the
     four point estimates (no CIs) — disclosed in the module docstring;
     the rule is the task's own wording operationalized.
  8. The {n_excl} rows excluded for missing own_e_b are reported with a
     skew check in G1 output above (AGENTS s5).""")
    print(f"\nAE4 DONE  ({time.time() - T0:.1f}s)  VERDICT: {verdict}")
