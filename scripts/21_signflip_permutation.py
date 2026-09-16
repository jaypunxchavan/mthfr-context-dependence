"""
Task 1: Re-derivation null for e_b (folinate-INDEPENDENT genetic interaction).

WHY A NEW MECHANISM WAS NEEDED
The e_r test (script 20, NULL 1) permutes a variant's four measurements
across concentration slots. That destroys a trend, which is what e_r is.
But e_b is a constant OFFSET, and the mean of a set is invariant to how
you relabel which concentration each value belongs to -- so no within-
variant reordering can ever null e_b. A different kind of randomness is
required.

A REJECTED DESIGN, RECORDED SO IT IS NOT RETRIED
An earlier proposal was to pair variant v's no-interaction expectation
against a DIFFERENT variant's observed A222V-background measurements.
That is miscalibrated, not merely weak. expected(v) already encodes how
functional v is overall -- absorbing that main effect is the entire point
of the multiplicative model. Pairing across variants differences two
unrelated baseline severities, producing large "apparent interaction"
even when true e_b is exactly zero for both. Such a test would reject the
null almost regardless of ground truth, while looking rigorous.

THE MECHANISM USED: within-variant sign flips (Rademacher permutation)
Under the null, a variant's per-point residuals are symmetric noise about
zero, so flipping the sign of any residual yields an equally plausible
value. For each iteration, multiply each residual by an independent
random +/-1, keep concentration labels fixed, refit, and recompute the
population-level correlation with ESM-2 error.

This stays inside one variant's own data -- never importing another
variant's baseline -- which is the same discipline that made the e_r test
valid. Sign flips rather than relabelling, because a mean needs a
different randomization than a trend.

RESOLUTION: 4 points give only 2^4 = 16 sign patterns per variant, coarse
for any single variant. The claim here is population-level (does the
correlation across ~10,000 variants survive), and flipping every variant
independently within each iteration gives effectively continuous
resolution at that level.

P-VALUES APPLY TO own_e_b, not the published e.b. The validation
correlation is printed alongside so the reader can judge transfer.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np, pandas as pd
from scipy.stats import spearmanr
from scripts.lib.own_context import (fit_single_arm, fit_interaction, wls_line,
                                     interpolate_correction, CONCS, LOGL_CUTOFF,
                                     WT_SCORE_COLS, WT_SE_COLS, MT_SCORE_COLS, MT_SE_COLS)
from scripts.lib.stats import _spearman

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    d = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    W = d[WT_SCORE_COLS].to_numpy(float); Wse = d[WT_SE_COLS].to_numpy(float)
    M = d[MT_SCORE_COLS].to_numpy(float); Mse = d[MT_SE_COLS].to_numpy(float)

    w = fit_single_arm(W, Wse); w_mean = np.nanmean(W, axis=1)
    i222 = int(np.where(d["hgvs"].to_numpy() == "p.Ala222Val")[0][0])
    a_f, a_r = w["fitness"][i222], w["remediation"][i222]
    e1 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean, a_f, a_r)
    keep = (w["logl"] > LOGL_CUTOFF) & (e1["logl"] > LOGL_CUTOFF)
    cb = interpolate_correction(w["fitness"][keep], e1["e_b"][keep])
    cr = interpolate_correction(w["fitness"][keep], e1["e_r"][keep])
    e2 = fit_interaction(M, Mse, w["fitness"], w["remediation"], w["post"], w_mean,
                         a_f, a_r, correction=(cb, cr))
    R, S, V = e2["resid"], Mse, e2["valid"]

    print("=" * 72)
    print("SANITY CHECKS (test the test before trusting it)")
    print("=" * 72)
    eb_plus, _, _ = wls_line(R * 1.0, S, CONCS, V)
    eb_minus, _, _ = wls_line(R * -1.0, S, CONCS, V)
    ok = np.isfinite(e2["e_b"]) & np.isfinite(eb_plus)
    print(f"  all-+1 flips reproduce real e_b exactly: max|diff|="
          f"{np.abs(e2['e_b'][ok]-eb_plus[ok]).max():.3e}")
    print(f"  all--1 flips give exactly -e_b:          max|diff|="
          f"{np.abs(e2['e_b'][ok]+eb_minus[ok]).max():.3e}")

    print("\n" + "=" * 72)
    print("SYNONYMOUS CONTROL (assumption-free empirical zero)")
    print("=" * 72)
    print("  Synonymous variants encode the identical protein sequence, so they")
    print("  CANNOT have real epistasis. Their e_b distribution is the noise floor,")
    print("  requiring no symmetric-noise assumption at all.")
    ctrl = []
    for lbl, msk in [("synonymous (true zero)", d["type"].to_numpy() == "synonymous"),
                     ("nonsense", d["type"].to_numpy() == "nonsense"),
                     ("missense", d["type"].to_numpy() == "substitution")]:
        v = e2["e_b"][msk]; v = v[np.isfinite(v)]
        print(f"  {lbl:24s} n={len(v):5d} mean={v.mean():+.4f} sd={v.std():.4f} "
              f"median|e_b|={np.median(np.abs(v)):.4f} p95|e_b|={np.percentile(np.abs(v),95):.4f}")
        ctrl.append({"group": lbl, "n": len(v), "mean": v.mean(), "sd": v.std(),
                     "median_abs": np.median(np.abs(v)),
                     "p95_abs": np.percentile(np.abs(v), 95)})
    pd.DataFrame(ctrl).to_csv(PROC / "task1_synonymous_control.csv", index=False)

    syn = e2["e_b"][d["type"].to_numpy() == "synonymous"]
    syn_p95 = np.percentile(np.abs(syn[np.isfinite(syn)]), 95)

    ph3 = pd.read_csv(PROC / "phase3_analysis_table.csv")[
        ["hgvs_pro", "position", "central_error_rank", "central_error_cal"]]
    mis = pd.DataFrame({"hgvs_pro": d["hgvs"], "type": d["type"],
                        "own_e_b": e2["e_b"], "pub_e_b": d["e.b"]})
    mis = mis[mis["type"] == "substitution"].merge(ph3, on="hgvs_pro", how="inner")
    row_of = {h: i for i, h in enumerate(d["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in mis["hgvs_pro"]])
    ok2 = mis["own_e_b"].notna() & mis["pub_e_b"].notna()
    print(f"\n  validation own_e_b vs published e.b: rho="
          f"{spearmanr(mis.loc[ok2,'own_e_b'], mis.loc[ok2,'pub_e_b']).statistic:.4f}")
    print(f"  missense variants exceeding the synonymous 95th pct (|e_b|>{syn_p95:.3f}): "
          f"{(mis['own_e_b'].abs() > syn_p95).sum()} / {mis['own_e_b'].notna().sum()}")

    print("\n" + "=" * 72)
    print(f"SIGN-FLIP PERMUTATION TEST ({N_PERM} iterations, seed={SEED})")
    print("=" * 72)
    Rs, Ss, Vs = R[src], S[src], V[src]
    rows = []
    for err in ["central_error_rank", "central_error_cal"]:
        errv = mis[err].to_numpy()
        good = np.isfinite(mis["own_e_b"].to_numpy()) & np.isfinite(errv)
        obs = _spearman(np.abs(mis["own_e_b"].to_numpy()[good]), errv[good])
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            signs = rng.choice([-1.0, 1.0], size=Rs.shape)
            eb_p, _, _ = wls_line(Rs * signs, Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(errv)
            null[p] = _spearman(np.abs(eb_p[g]), errv[g])
        pv = (np.abs(null) >= abs(obs)).mean()
        excess = obs - null.mean()
        frac_artifact = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
        print(f"  {err}")
        print(f"    observed rho={obs:+.4f}   null mean={null.mean():+.4f} "
              f"sd={null.std():.4f}   p={pstr(pv)}")
        print(f"    -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'} the re-derivation null")
        print(f"    EFFECT SIZE: the null does NOT centre on zero, so the raw rho")
        print(f"    overstates the real effect. Excess over null = {excess:+.4f}")
        print(f"    ({100*frac_artifact:.0f}% of the raw correlation is structural artifact).")
        rows.append({"error_metric": err, "observed_rho": obs,
                     "null_mean": null.mean(), "null_sd": null.std(),
                     "excess_over_null": excess, "frac_artifact": frac_artifact,
                     "p_perm": pv, "survives": pv < 0.05, "n_perm": N_PERM})

    pd.DataFrame(rows).to_csv(PROC / "task1_signflip_results.csv", index=False)
    print(f"\nSaved to {PROC}")
