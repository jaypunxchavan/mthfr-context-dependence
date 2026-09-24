"""
Script 32: promote delta_ESM to the PRIMARY endpoint.

WHY THIS REPLACES THE OLD PRIMARY
---------------------------------
Every headline result so far regressed an ESM-2 ERROR against a DMS-derived
RESIDUAL (e.b). That outcome was shown to be dominated by the wild-type arm:
remove w.fitness from the confound anchor and every predictor's excess
collapses to a CI crossing zero. The problem is the outcome variable, not
the controls -- so no further control can fix it.

delta_ESM has none of that structure:

    delta_ESM(v) = S(v | A222V background) - S(v | WT background)

It is ESM-2's OWN predicted interaction term: the change in the model's
assessment of v caused by supplying the A222V background. Correlating it
against the measured interaction e.b is interaction-vs-interaction. No error
metric, no isotonic calibration, no w.fitness anywhere in either variable.
This is the only endpoint in the project structurally immune to the
circularity that ate the others.

It is also exactly the test Visani/Verma/DeWitt (2026) run in their Fig. 2:
compare a model's PREDICTED epistatic residual against the MEASURED one. If
the predicted residuals cluster at a constant and carry no correlation with
the measured residuals, the model represents no epistasis at all. That is a
clean negative result, not a failed positive, and it is reported as such.

Model B already established that S(A222V|WT) is a single constant, so
delta_ESM is the whole of ESM-2's implied interaction up to that constant.

LIMITATION, STATED UP FRONT: Nambiar et al. symmetrise over both mutation
orders (v after A222V, and A222V after v). Only one direction exists here --
the atlas measures variants in the A222V background, never A222V in each
variant's background. This endpoint is therefore one-directional, and no
claim about symmetry is made.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats import position_cluster_bootstrap, _spearman

N_BOOT = int(os.environ.get("N_BOOT", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"


def pstr(p):
    return "<0.0001" if p == 0 else f"{p:.4f}"


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b", "own_e_r"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = df.dropna(subset=["delta_esm"]).copy()
    df["abs_delta"] = df["delta_esm"].abs()
    df["abs_gi"] = df["GI_folinate_independent"].abs()
    df["abs_gi_own"] = df["own_e_b"].abs()
    df["region"] = assign_region(df["position"])
    df["dist_222"] = (df["position"] - 222).abs()
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    rows = []

    # ---- 32a: does ESM-2 represent ANY interaction? (DeWitt Fig 2) ----------
    print(f"\n{'='*74}\n32a  DOES ESM-2 REPRESENT ANY INTERACTION AT ALL?\n{'='*74}")
    dv = df["delta_esm"].to_numpy()
    eb = df["GI_folinate_independent"].to_numpy()
    print(f"  delta_ESM      mean={np.nanmean(dv):+.5f}  sd={np.nanstd(dv):.5f}  "
          f"IQR=[{np.nanpercentile(dv,25):+.5f},{np.nanpercentile(dv,75):+.5f}]")
    print(f"  measured e.b   mean={np.nanmean(eb):+.5f}  sd={np.nanstd(eb):.5f}  "
          f"IQR=[{np.nanpercentile(eb,25):+.5f},{np.nanpercentile(eb,75):+.5f}]")
    spread_ratio = np.nanstd(dv) / np.nanstd(eb) if np.nanstd(eb) > 0 else np.nan
    print(f"  spread ratio sd(delta_ESM)/sd(e.b) = {spread_ratio:.4f}")
    print("  DeWitt's read: predicted residuals collapsing to a near-constant with")
    print("  no correlation to the measured residual = the model carries no")
    print("  representation of interaction. Both facts are tested below.")
    rows.append({"stage": "spread", "quantity": "delta_esm", "value": float(np.nanstd(dv))})
    rows.append({"stage": "spread", "quantity": "e_b", "value": float(np.nanstd(eb))})
    rows.append({"stage": "spread", "quantity": "sd_ratio", "value": float(spread_ratio)})

    # ---- 32b: the primary correlation --------------------------------------
    print(f"\n{'='*74}\n32b  PRIMARY: delta_ESM vs measured interaction "
          f"(n_boot={N_BOOT})\n{'='*74}")
    PAIRS = [("delta_esm", "GI_folinate_independent", "signed, published e.b"),
             ("delta_esm", "own_e_b", "signed, own e_b"),
             ("abs_delta", "abs_gi", "absolute, published e.b"),
             ("abs_delta", "abs_gi_own", "absolute, own e_b"),
             ("delta_esm", "GI_folinate_dependent", "signed, published e.r")]
    for xc, yc, lbl in PAIRS:
        sub = df.dropna(subset=[xc, yc])
        if len(sub) < 100:
            print(f"  {lbl:28s} SKIPPED (n={len(sub)})")
            continue
        r = position_cluster_bootstrap(sub, "position", xc, yc,
                                       n_boot=N_BOOT, seed=SEED)
        crosses = r["ci_lo"] < 0 < r["ci_hi"]
        print(f"  {lbl:28s} rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'])} "
              f"n={r['n_rows']}{'  (crosses 0)' if crosses else ''}")
        rows.append({"stage": "primary", "quantity": lbl, "value": r["observed_rho"],
                     "ci_lo": r["ci_lo"], "ci_hi": r["ci_hi"], "p": r["p_boot"],
                     "n": r["n_rows"], "ci_includes_zero": crosses})

    # ---- 32c: is delta_ESM just local sequence context? --------------------
    print(f"\n{'='*74}\n32c  IS delta_ESM JUST PROXIMITY TO POSITION 222?\n{'='*74}")
    print("  A transformer's score at position i shifts when a nearby residue")
    print("  changes, for reasons that have nothing to do with epistasis. If")
    print("  |delta_ESM| is explained by distance from 222, it is attention")
    print("  locality, not a learned interaction.")
    r = position_cluster_bootstrap(df, "position", "abs_delta", "dist_222",
                                   n_boot=N_BOOT, seed=SEED)
    print(f"  |delta_ESM| vs |position-222|: rho={r['observed_rho']:+.4f} "
          f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'])}")
    rows.append({"stage": "locality", "quantity": "abs_delta_vs_dist222",
                 "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                 "ci_hi": r["ci_hi"], "p": r["p_boot"], "n": r["n_rows"]})

    near = df[df["dist_222"] <= 25]
    far = df[df["dist_222"] > 25]
    for lbl, sub in [("within 25 residues of 222", near), ("beyond 25 residues", far)]:
        if sub["position"].nunique() < 15:
            print(f"  {lbl:28s} SKIPPED ({sub['position'].nunique()} positions)")
            continue
        rr = position_cluster_bootstrap(sub, "position", "delta_esm",
                                        "GI_folinate_independent",
                                        n_boot=N_BOOT, seed=SEED)
        print(f"  primary restricted to {lbl:28s} rho={rr['observed_rho']:+.4f} "
              f"CI=[{rr['ci_lo']:+.4f},{rr['ci_hi']:+.4f}] n={rr['n_rows']}")
        rows.append({"stage": "locality_split", "quantity": lbl,
                     "value": rr["observed_rho"], "ci_lo": rr["ci_lo"],
                     "ci_hi": rr["ci_hi"], "p": rr["p_boot"], "n": rr["n_rows"]})

    # ---- 32d: region check --------------------------------------------------
    print(f"\n{'='*74}\n32d  REGION CHECK\n{'='*74}")
    pooled = position_cluster_bootstrap(df.dropna(subset=["GI_folinate_independent"]),
                                        "position", "delta_esm",
                                        "GI_folinate_independent",
                                        n_boot=N_BOOT, seed=SEED)
    print(f"  pooled rho={pooled['observed_rho']:+.4f} "
          f"CI=[{pooled['ci_lo']:+.4f},{pooled['ci_hi']:+.4f}]")
    for rg in sorted(REGION_BOUNDS):
        sub = df[df["region"] == rg].dropna(subset=["GI_folinate_independent"])
        if sub["position"].nunique() < 15:
            print(f"    region {rg} SKIPPED ({sub['position'].nunique()} positions)")
            continue
        res = position_cluster_bootstrap(sub, "position", "delta_esm",
                                         "GI_folinate_independent",
                                         n_boot=N_BOOT, seed=SEED)
        ov = not (res["ci_hi"] < pooled["ci_lo"] or res["ci_lo"] > pooled["ci_hi"])
        lo, hi = REGION_BOUNDS[rg]
        print(f"    region {rg} ({lo}-{hi}) rho={res['observed_rho']:+.4f} "
              f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}]"
              f"{'' if ov else '  <-- does NOT overlap pooled'}")
        rows.append({"stage": "region", "quantity": f"region_{rg}",
                     "value": res["observed_rho"], "ci_lo": res["ci_lo"],
                     "ci_hi": res["ci_hi"], "p": res["p_boot"],
                     "n": res["n_rows"], "overlaps_pooled": ov})

    out = PROC / "task32_delta_esm_primary.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    df.to_csv(PROC / "task32_analysis_table.csv", index=False)
    print(f"\nSaved to {out}")
    print("NOTE: this endpoint has NOT yet been run against a null. Script 33")
    print("does that. Do not quote 32b before 33 has run.")
