"""
Script 33: sign-flip re-derivation null for the delta_ESM endpoint.

Script 32's correlation is not quotable until it has faced the null that
killed e.r and cut the e_b result by ~80%. Same mechanism as script 21:
multiply each variant's per-concentration residuals by independent random
+/-1, refit, and recompute the population correlation. Everything stays
inside one variant's own data -- no cross-variant pairing, which was
rejected as miscalibrated early in the project.

WHAT IS NEW HERE, AND WHY IT MATTERS
------------------------------------
Every previous use of this null correlated |e_b| against an ERROR metric,
so the null could not centre on zero: |.| of a symmetric variable has a
positive mean by construction, and that is precisely the "77-82% structural
artifact" figure. delta_ESM is SIGNED and so is e_b, so the signed version
of this test has a null that SHOULD centre on zero. That is a far stronger
test, and it doubles as a calibration check on the machinery itself:

  * signed null mean ~ 0        -> the null is behaving; the excess is the effect
  * signed null mean far from 0 -> something is wrong with the construction,
                                   and no result from it should be believed

Both signed and absolute versions are run so the two can be compared
directly.

A SECOND, WEAKER NULL is also run: permuting delta_ESM across POSITION
blocks. That one asks whether the pairing is stronger than chance, not
whether the interaction exceeds measurement noise. Reported separately and
labelled as the weaker of the two, exactly as script 20 does.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman
from scripts.lib.stats_ext import rebuild_interaction_fit
from scripts.lib.regions import assign_region, REGION_BOUNDS

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p, n):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse = fit["e2"], fit["M_se"]

    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left").dropna(subset=["delta_esm", "own_e_b"])
    df = df.reset_index(drop=True)
    df["region"] = assign_region(df["position"])
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in df["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    print("\n" + "=" * 74)
    print("SANITY CHECKS (test the test before trusting it)")
    print("=" * 74)
    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    own_eb = df["own_e_b"].to_numpy()
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    print(f"  all-+1 flips reproduce own_e_b exactly: max|diff|="
          f"{np.abs(chk_p[ok] - own_eb[ok]).max():.3e}")
    print(f"  all--1 flips give exactly -own_e_b:     max|diff|="
          f"{np.abs(chk_m[ok] + own_eb[ok]).max():.3e}")
    if np.abs(chk_p[ok] - own_eb[ok]).max() > 1e-6:
        print("  *** SANITY CHECK FAILED -- row alignment is wrong. Stop here. ***")
        sys.exit(1)

    dv = df["delta_esm"].to_numpy()
    adv = np.abs(dv)
    rows = []

    print("\n" + "=" * 74)
    print(f"NULL 1 -- SIGN-FLIP RE-DERIVATION ({N_PERM} permutations)")
    print("=" * 74)
    for pred, lbl, signed in [(dv, "signed delta_ESM vs signed e_b", True),
                              (adv, "absolute |delta_ESM| vs |e_b|", False)]:
        obs = _spearman(pred if signed else pred,
                        own_eb if signed else np.abs(own_eb))
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(pred)
            null[p] = _spearman(pred[g], eb_p[g] if signed else np.abs(eb_p[g]))
        pv = float((np.abs(null) >= abs(obs)).mean())
        excess = obs - null.mean()
        frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
        print(f"  {lbl}")
        print(f"    observed={obs:+.4f}  null mean={null.mean():+.4f} "
              f"sd={null.std():.4f}  p={pstr(pv, N_PERM)}")
        print(f"    excess over null={excess:+.4f}  "
              f"({100*frac:.0f}% of the raw value is structural artifact)")
        print(f"    -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'}")
        if signed:
            centred = abs(null.mean()) < 2 * null.std() / np.sqrt(N_PERM) * 3
            print(f"    null-centring check: null mean {'IS' if centred else 'is NOT'} "
                  f"consistent with zero -- {'machinery behaving' if centred else 'INVESTIGATE'}")
        rows.append({"null": "signflip", "variant": lbl, "observed": obs,
                     "null_mean": float(null.mean()), "null_sd": float(null.std()),
                     "excess_over_null": excess, "frac_artifact": frac,
                     "p": pv, "n_perm": N_PERM, "survives": pv < 0.05})

    print("\n" + "=" * 74)
    print(f"NULL 2 -- POSITION-BLOCK PERMUTATION (weaker; association only)")
    print("=" * 74)
    sub = df[["position", "delta_esm", "own_e_b"]].dropna()
    blocks = [g["delta_esm"].to_numpy() for _, g in sub.groupby("position")]
    ebv = np.concatenate([g["own_e_b"].to_numpy() for _, g in sub.groupby("position")])
    obs2 = _spearman(np.concatenate(blocks), ebv)
    null2 = np.empty(N_PERM)
    for p in range(N_PERM):
        null2[p] = _spearman(
            np.concatenate([blocks[i] for i in rng.permutation(len(blocks))]), ebv)
    pv2 = float((np.abs(null2) >= abs(obs2)).mean())
    print(f"  observed={obs2:+.4f}  null mean={null2.mean():+.4f} "
          f"sd={null2.std():.4f}  p={pstr(pv2, N_PERM)}")
    print("  This asks whether the pairing beats chance, NOT whether the")
    print("  interaction exceeds measurement noise. Null 1 is the real test.")
    rows.append({"null": "position_block", "variant": "signed", "observed": obs2,
                 "null_mean": float(null2.mean()), "null_sd": float(null2.std()),
                 "p": pv2, "n_perm": N_PERM, "survives": pv2 < 0.05})

    print("\n" + "=" * 74)
    print("REGION CHECK ON THE EXCESS (sign-flip null, per region)")
    print("=" * 74)
    n_reg = max(200, N_PERM // 10)
    for rg in sorted(REGION_BOUNDS):
        m = (df["region"] == rg).to_numpy()
        if df.loc[m, "position"].nunique() < 15:
            print(f"  region {rg}: SKIPPED ({df.loc[m,'position'].nunique()} positions)")
            continue
        obs_r = _spearman(dv[m], own_eb[m])
        nr = np.empty(n_reg)
        for p in range(n_reg):
            eb_p, _, _ = wls_line(Rs[m] * rng.choice([-1.0, 1.0], size=Rs[m].shape),
                                  Ss[m], CONCS, Vs[m])
            g = np.isfinite(eb_p) & np.isfinite(dv[m])
            nr[p] = _spearman(dv[m][g], eb_p[g])
        pvr = float((np.abs(nr) >= abs(obs_r)).mean())
        lo, hi = REGION_BOUNDS[rg]
        print(f"  region {rg} ({lo}-{hi}) observed={obs_r:+.4f} "
              f"null mean={nr.mean():+.4f} excess={obs_r-nr.mean():+.4f} "
              f"p={pstr(pvr, n_reg)}")
        rows.append({"null": "signflip_region", "variant": f"region_{rg}",
                     "observed": obs_r, "null_mean": float(nr.mean()),
                     "null_sd": float(nr.std()),
                     "excess_over_null": obs_r - nr.mean(),
                     "p": pvr, "n_perm": n_reg, "survives": pvr < 0.05})

    out = PROC / "task33_delta_esm_nulls.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved to {out}")
    print("\nP-values apply to own_e_b. Transfer to the published e.b only as far")
    print("as the two agree -- script 17 prints that correlation.")
