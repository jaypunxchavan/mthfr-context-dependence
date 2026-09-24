"""
Task A1b (review-triage): rerun script 33's sign-flip re-derivation null at
POSITION-BLOCK granularity, and compare against the finer granularities.

WHY THIS EXISTS
---------------
AGENTS.md §3/§4: any permutation or null must be at POSITION level, not
variant level, or the pseudoreplication already fixed in the CIs is
reintroduced into the p-values (~11,113 variants sit in ~655 positions;
up to 19 substitutions share a residue and their e.b estimates are
correlated). Script 33's null flips residuals at (variant x condition)
CELL granularity -- rng.choice(size=Rs.shape) with Rs.shape == (n, 4) --
which is FINER than variant-level, i.e. strictly narrower than the
house convention allows. The same cell-level flip appears in scripts
21, 24, 26 and 28. The review flagged this specifically as a threat to
the "~0% artifact" claim in log 5.3.

GRANULARITIES COMPARED (all at the same N_PERM, same statistic)
---------------------------------------------------------------
  1. cell       one Rademacher sign per (variant, condition) -- script 33's null
  2. variant    one sign per variant, shared by its 4 conditions
  3. position   one sign per residue position, shared by all its variants
                and all conditions -- the house convention

PRE-REGISTERED DECISION RULE (stated before running, per AGENTS.md §6)
-----------------------------------------------------------------------
Primary statistic: observed signed Spearman(delta_ESM, own_e_b) on the
n=10,757 analysis set (identical to script 33's).
The headline "~0% artifact / p < 1/N_PERM" claim for the SIGNED null is
judged SURVIVES iff the POSITION-level null (a) centres on zero and
(b) p_position < 0.05. If the position-level p exceeds 0.05, the correct
report is that 5.3's significance does not survive position-block
granularity. No retuning of any kind is permitted after seeing results.

Null type: re-derivation (residuals are sign-flipped and e.b is refit on
every draw), not association -- same as script 33.

SANITY CHECKS (AGENTS.md §4 -- failure => sys.exit(1), do not raise N):
  * all-+1 flips reproduce own_e_b exactly (max|diff| < 1e-6)
  * all--1 flips give exactly -own_e_b (cell, variant and position layouts)

LIMITATIONS, STATED UP FRONT:
  * A sign-flip null on a signed variable centres on zero by construction;
    it rules out the e.b-construction artifact, not confounding (AGENTS.md §4).
  * p is bounded by 1/N_PERM and is the primary claim; no z-scores reported.
  * N_PERM comes from the environment (default 10000); reduced-N runs must
    be labelled REDUCED-RESOLUTION by the caller in the log.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman
from scripts.lib.stats_ext import rebuild_interaction_fit

N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"


def pstr(p, n):
    return f"<{1.0 / n:.4f}" if p == 0 else f"{p:.4f}"


def run_null(rng, pred, Rs, Ss, Vs, signs_fn, n_perm, label, rows):
    """Re-derivation sign-flip null at whatever granularity signs_fn draws."""
    obs = _spearman(pred[np.isfinite(pred)], own_eb[np.isfinite(pred)])
    null = np.empty(n_perm)
    for p in range(n_perm):
        signs = signs_fn(rng)
        eb_p, _, _ = wls_line(Rs * signs, Ss, CONCS, Vs)
        g = np.isfinite(eb_p) & np.isfinite(pred)
        null[p] = _spearman(pred[g], eb_p[g])
    pv = float((np.abs(null) >= abs(obs)).mean())
    excess = obs - null.mean()
    frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
    centred = abs(null.mean()) < 3 * null.std() / np.sqrt(n_perm)
    print(f"  [{label}]")
    print(f"    observed={obs:+.4f}  null mean={null.mean():+.4f} "
          f"sd={null.std():.4f}  p={pstr(pv, n_perm)}")
    print(f"    excess over null={excess:+.4f}  "
          f"({100 * frac:.1f}% of the raw value is structural artifact)")
    print(f"    null-centring check: mean {'IS' if centred else 'is NOT'} "
          f"consistent with zero (3 SE)")
    print(f"    -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'} at p<0.05")
    rows.append({"granularity": label, "observed": obs,
                 "null_mean": float(null.mean()), "null_sd": float(null.std()),
                 "excess_over_null": excess, "frac_artifact": frac,
                 "p": pv, "n_perm": n_perm, "survives": pv < 0.05,
                 "null_centred": bool(centred)})
    return null


if __name__ == "__main__":
    rng = np.random.default_rng(SEED)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse = fit["e2"], fit["M_se"]

    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left").dropna(
        subset=["delta_esm", "own_e_b"]).reset_index(drop=True)
    print(f"Analysis set: {len(df)} variants, {df['position'].nunique()} positions")

    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in df["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    # position -> row-index layout for position-block signs
    pos_codes, pos_uniques = pd.factorize(df["position"])
    n_pos = len(pos_uniques)

    own_eb = df["own_e_b"].to_numpy()
    dv = df["delta_esm"].to_numpy()

    def layout_cell(sign_matrix):
        return sign_matrix

    def layout_variant(row_signs):
        return np.repeat(np.asarray(row_signs, float)[:, None], Rs.shape[1], axis=1)

    def layout_position(pos_signs):
        return np.repeat(np.asarray(pos_signs, float)[pos_codes][:, None],
                         Rs.shape[1], axis=1)

    print("\n" + "=" * 74)
    print("SANITY CHECKS (test the test before trusting it) -- AGENTS.md §4")
    print("=" * 74)
    ones_cell = np.ones_like(Rs)
    ones_var = layout_variant(np.ones(len(Rs)))
    ones_pos = layout_position(np.ones(n_pos))
    neg_cell = -ones_cell
    neg_var = -ones_var
    neg_pos = -ones_pos
    ok = np.isfinite(own_eb)
    checks = {}
    for lbl, signs, expect in [
        ("cell      all+1 == own_e_b", ones_cell, own_eb),
        ("cell      all-1 == -own_e_b", neg_cell, -own_eb),
        ("variant   all+1 == own_e_b", ones_var, own_eb),
        ("variant   all-1 == -own_e_b", neg_var, -own_eb),
        ("position  all+1 == own_e_b", ones_pos, own_eb),
        ("position  all-1 == -own_e_b", neg_pos, -own_eb),
    ]:
        got, _, _ = wls_line(Rs * signs, Ss, CONCS, Vs)
        g = np.isfinite(got) & ok
        d = np.abs(got[g] - expect[g]).max()
        checks[lbl] = d
        print(f"  {lbl:32s} max|diff| = {d:.3e}")
    if any((not np.isfinite(d)) or d > 1e-6 for d in checks.values()):
        print("  *** SANITY CHECK FAILED -- do not proceed. sys.exit(1) ***")
        sys.exit(1)
    print("  all checks passed.")

    print("\n" + "=" * 74)
    print(f"SIGN-FLIP RE-DERIVATION NULL AT THREE GRANULARITIES ({N_PERM} draws each)")
    print("=" * 74)
    rows = []

    def signs_cell(r):
        return r.choice([-1.0, 1.0], size=Rs.shape)

    def signs_variant(r):
        return np.repeat(r.choice([-1.0, 1.0], size=(len(Rs), 1)), Rs.shape[1], axis=1)

    def signs_position(r):
        draw = r.choice([-1.0, 1.0], size=n_pos)
        return np.repeat(draw[pos_codes][:, None], Rs.shape[1], axis=1)

    for lbl, fn in [("cell (script 33's null)", signs_cell),
                    ("variant", signs_variant),
                    ("position (house convention)", signs_position)]:
        run_null(rng, dv, Rs, Ss, Vs, fn, N_PERM, lbl, rows)

    ref = pd.read_csv(PROC / "task33_delta_esm_nulls.csv")
    ref_row = ref[(ref["null"] == "signflip") &
                  (ref["variant"] == "signed delta_ESM vs signed e_b")].iloc[0]
    print("\n  Reference -- script 33 on-disk cell-level null (N_PERM=10000):")
    print(f"    null mean={ref_row['null_mean']:+.6f} sd={ref_row['null_sd']:.6f} "
          f"p={ref_row['p']} (this run's cell-level row should agree in scale)")

    out = PROC / "task42_position_block_null.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved to {out}")
    print("\nRe-derivation null (not association). p bounded by 1/N_PERM; p is the")
    print("primary claim, no z reported. Sign-flip null on a signed variable")
    print("centres on zero by construction -- it rules out the e.b-construction")
    print("artifact, not confounding (AGENTS.md §4).")
