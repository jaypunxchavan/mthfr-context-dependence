"""
Script 48: Group E review tasks
  E1a -- reframe script 36's CI-only two-trait gate with effect sizes.
  E1b -- does own-vs-published e.b disagreement step at DOMAIN boundaries
         but not at the mutagenesis-REGION boundaries used everywhere else
         in this repo?

WHY
---
REVIEW_TRIAGE E1: script 36's decision gate is "CI excludes zero". On
n=11,113 rows / 654 positions almost any nonzero mean clears that. The
review asks (a) whether the domain disagreement gradient is large enough
to matter relative to the residual-sd / e.b.-sd baseline, and (b) whether
the disagreement profile steps specifically at the DOMAIN boundaries or
also at the region boundaries that cut every other analysis here.

PART A (E1a) -- PRE-REGISTERED DESIGN (fixed before running)
------------------------------------------------------------
1. Rebuild script 36's analysis set with its exact code path (phase5 ->
   merge own_context_metrics -> structural features -> dropna f_bar_wt/
   f_bar_a222v -> rank_resid / eb_disagreement / region).
2. GATE (sys.exit(1) on failure): every group mean for stages
   domain_rank_resid / region_rank_resid / disagreement_domain in
   data/processed/task36_two_trait_diagnostic.csv must be reproduced from
   the rebuild to |diff| <= 1e-9, and group row-counts must match exactly.
   Group CI diffs vs the reference CSV are printed as information only
   (the reference's N_BOOT is not recorded).
3. Effect size per group = |mean| / sd, all sds ddof=1 over the same
   analysis set:
     rank_resid groups:   sd_row = sd of rank_resid over rows
                          sd_pos = sd of per-position mean rank_resid
     disagreement groups: sd_row, sd_pos, and
                          sd_eb  = sd of own_e_b over rows (the "e.b. sd
                                   baseline" the review names)
   PRIMARY denominator = the LARGEST candidate (smallest effect) -- the
   most conservative reading of the review's ambiguous "residual sd /
   e.b. sd baseline".  Assumption logged here and in the run output.
4. Effect-size floor: PRIMARY 0.10; bands 0.05 (lenient) and 0.25
   (strict) reported as sensitivity.  DISCLOSURE (AGENTS 6): the floor
   was chosen AFTER the review quoted the ~0.03-0.04 vs 0.24 numbers, so
   it is post-hoc; all three bands are printed so the verdict can be read
   under each.
5. The review's "gradient": max - min of the four domain means
   (disagreement primary; rank_resid span reported too), same
   denominators.
6. VERDICT RULE (fixed before running):
   - every group with CI excluding zero (script 36's gate) ALSO has
     es_primary >= 0.10   -> "GATE SURVIVES the effect floor"
   - some but not all     -> "GATE DOWNGRADED (k of m below the floor)";
                             those CIs are statistically real but
                             negligible at this scale
   - none of them         -> "GATE FAILS the effect floor"

PART B (E1b) -- PRE-REGISTERED DESIGN (fixed before running)
------------------------------------------------------------
1. Units: per-position mean eb_disagreement (d_pos), one value per
   position -- position-level throughout (AGENTS 3: no variant-level
   pseudoreplication).
2. Boundary sets:
   REGION = start of each region after the first, from
            scripts.lib.regions.REGION_BOUNDS -> {148, 295, 475}
   DOMAIN = per-residue Domain label changes from
            load_structural_features(), counting only ADJACENT residue
            pairs (a label change across a gap in the reference table is
            not a boundary).
3. Windows (primary w=25): L = [b-w, b-1], R = [b, b+w-1]; step =
   mean(d_pos[R]) - mean(d_pos[L]).  FULL-WINDOW RULE: a boundary is
   testable at a given w only if EVERY residue of both windows is a data
   position; otherwise it is dropped and logged (conservative: fewer
   boundaries, identical window sizes across boundaries).  Sensitivity
   w in {15, 40}, reported but NOT verdict-bearing.
4. Set statistic T = max over testable boundaries of |step|.
5. Nulls (two; the review specified (a) only -- (b) added because a plain
   position permutation destroys spatial autocorrelation in d_pos and can
   be anti-conservative; using max p is the conservative choice):
   a. POSITION PERMUTATION: shuffle d_pos values across positions,
      N_PERM draws (env, default 10000),
      p = (1 + #{T_perm >= T_obs}) / (N_PERM + 1).
   b. CIRCULAR SHIFT: roll the profile over all n-1 nonzero offsets
      (EXACT, no draws), p = (1 + #{k: T_k >= T_obs}) / n.
   SET p FOR THE VERDICT = max(p_perm, p_shift).  Assumption logged.
6. Verdict at alpha=0.05, primary w=25 only:
   DIVERGENCE (domain only) / DIVERGENCE (region only) / CONCORDANCE /
   NEITHER / UNTESTABLE (a set has zero testable boundaries).

CAVEATS (also printed by the script, AGENTS 6)
----------------------------------------------
- Post-hoc floor disclosure as above; denominator ambiguity resolved
  conservatively and logged.
- The circular-shift null treats the chain as circular (it is not); it is
  used only as the conservative tie-breaker of two nulls.
- Overlapping windows (domain boundaries 36 and 48 at w=25) are handled
  by the max statistic, not by multiplicity correction.
- E1b tests ALIGNMENT of a disagreement profile with boundaries; it
  cannot establish that the boundaries cause the disagreement.
- Inherited from script 36: one alternate background only (A222V), so
  rank_resid is a low-power proxy; a null is weak evidence of absence
  (Carlson et al. PNAS 2025 power caveat).
- Effect sizes use in-sample sds; nothing is predicted here, so AGENTS 3's
  cross-fit rule for calibration anchors does not apply -- disclosed
  anyway.

Outputs:
  data/processed/task48_e1a_effect_sizes.csv
  data/processed/task48_e1b_boundary_steps.csv
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scripts.lib.io import load_structural_features
from scripts.lib.features import add_structural_features
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.stats_ext import group_mean_bootstrap

N_BOOT = int(os.environ.get("N_BOOT", 2000))
N_PERM = int(os.environ.get("N_PERM", 10000))
SEED = 0
ALPHA = 0.05
FLOOR_PRIMARY = 0.10
FLOOR_BANDS = (0.05, 0.25)
W_PRIMARY = 25
W_SENS = (15, 40)
GATE_TOL = 1e-9
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

REF_STAGES = ("domain_rank_resid", "region_rank_resid", "disagreement_domain")


def rebuild_task36_set():
    """Script 36's exact code path, same order of operations."""
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    df = add_structural_features(df, load_structural_features())
    df = df.dropna(subset=["f_bar_wt", "f_bar_a222v"]).reset_index(drop=True)
    df["region"] = assign_region(df["position"])
    n = len(df)
    df["rank_resid"] = (df["f_bar_a222v"].rank() - df["f_bar_wt"].rank()) / n
    df["eb_disagreement"] = (df["own_e_b"] - df["GI_folinate_independent"]).abs()
    return df


def script36_groups(df):
    """Same group iteration and <10-position skip as script 36."""
    groups = []
    for dom, sub in df.groupby("domain"):          # NaN domain dropped by groupby
        if sub["position"].nunique() >= 10:
            groups.append(("domain_rank_resid", str(dom), sub, "rank_resid"))
    for rg in sorted(REGION_BOUNDS):
        sub = df[df["region"] == rg]
        if sub["position"].nunique() >= 10:
            groups.append(("region_rank_resid", f"region_{rg}", sub, "rank_resid"))
    for dom, sub in df.groupby("domain"):
        if sub["position"].nunique() >= 10:
            groups.append(("disagreement_domain", str(dom), sub, "eb_disagreement"))
    return groups


def part_a(df):
    print("=" * 74)
    print("E1a  SCRIPT 36'S GATE, WITH AN EFFECT-SIZE FLOOR")
    print("=" * 74)

    # ---- row accounting (AGENTS 5: every dropped row accounted for) ----
    n_all = len(df)
    n_domnull = int(df["domain"].isna().sum())
    dis = df.dropna(subset=["eb_disagreement"])
    n_dis_domnull = int(dis["domain"].isna().sum())
    print(f"Analysis set: {n_all} rows, {df['position'].nunique()} positions "
          f"(script 36's set)")
    print(f"Rows with domain label NULL: {n_domnull} (rank_resid set) -- "
          f"dropped by groupby in BOTH script 36 and this script")
    print(f"Disagreement set: {len(dis)} rows, of which {n_dis_domnull} "
          f"domain-NULL (dropped from disagreement_domain groups)")

    # ---- gate against script 36's saved output ----
    ref = pd.read_csv(PROC / "task36_two_trait_diagnostic.csv")
    ref = ref[ref.stage.isin(REF_STAGES)]
    exp = {}
    for r in ref.itertuples(index=False):
        excl = (None if r.stage == "disagreement_domain"
                else bool(r.excludes_zero))
        exp[(r.stage, r.group)] = (r.mean, r.ci_lo, r.ci_hi, int(r.n), excl)

    print(f"\nGATE: reproduce reference means to <={GATE_TOL} and n exactly "
          f"(N_BOOT={N_BOOT} for recomputed CIs)")
    results, failed, ci_diffs = [], False, []
    for stage, grp, sub, value in script36_groups(df):
        r = group_mean_bootstrap(sub, "position", value,
                                 n_boot=N_BOOT, seed=SEED)
        key = (stage, grp)
        if key not in exp:
            print(f"  MISSING in reference: {key}")
            failed = True
            continue
        m_ref, lo_ref, hi_ref, n_ref, excl_ref = exp[key]
        d_mean = abs(r["mean"] - m_ref)
        ok = d_mean <= GATE_TOL and r["n_rows"] == n_ref
        ci_diff = max(abs(r["ci_lo"] - lo_ref), abs(r["ci_hi"] - hi_ref))
        ci_diffs.append(ci_diff)
        if not ok:
            failed = True
        print(f"  {stage:22s} {grp:12s} mean_diff={d_mean:.3e} "
              f"n {r['n_rows']}=={n_ref} ci_diff={ci_diff:.3e} "
              f"{'OK' if ok else '<-- GATE FAIL'}")
        results.append({"stage": stage, "group": grp, **r,
                        "excludes_zero_ref": excl_ref})
    if failed:
        print("GATE FAILED: rebuild does not reproduce script 36. "
              "Stopping (AGENTS: sanity-check failure = FAIL, no retry).")
        sys.exit(1)
    print(f"GATE PASSED. Max CI diff vs reference (informational, "
          f"reference N_BOOT unrecorded): {max(ci_diffs):.3e}")

    # ---- effect-size denominators (all ddof=1, same set) ----
    sd_rr = {"sd_row": float(df["rank_resid"].std(ddof=1)),
             "sd_pos": float(df.groupby("position")["rank_resid"]
                             .mean().std(ddof=1))}
    sd_dis = {"sd_row": float(dis["eb_disagreement"].std(ddof=1)),
              "sd_pos": float(dis.groupby("position")["eb_disagreement"]
                              .mean().std(ddof=1)),
              "sd_eb": float(df["own_e_b"].dropna().std(ddof=1))}
    print(f"\nDenominators: rank_resid {sd_rr} | disagreement {sd_dis}")
    print("PRIMARY denominator per group = LARGEST candidate (conservative "
          "reading of 'residual sd / e.b. sd' -- assumption logged).")

    out_rows = []
    print("\n  stage                  group        mean      CI-gate   "
          "es_row  es_pos  es_eb  es_PRIM  >=0.05 >=0.10 >=0.25")
    for res in results:
        cand = sd_rr if res["stage"] != "disagreement_domain" else sd_dis
        es = {k: abs(res["mean"]) / v for k, v in cand.items()}
        denom_name = max(cand, key=cand.get)
        es_p = es[denom_name]
        excl = res["excludes_zero_ref"]
        cg = "EXCL0" if excl else ("crosses" if excl is False else "n/a")
        print(f"  {res['stage']:22s} {res['group']:12s} {res['mean']:+.5f}  "
              f"{cg:9s} {es.get('sd_row', float('nan')):6.3f} "
              f"{es.get('sd_pos', float('nan')):6.3f} "
              f"{es.get('sd_eb', float('nan')):6.3f}  {es_p:6.3f}   "
              f"{'Y' if es_p >= 0.05 else 'N':5s} "
              f"{'Y' if es_p >= 0.10 else 'N':5s} "
              f"{'Y' if es_p >= 0.25 else 'N':5s}")
        out_rows.append({"stage": res["stage"], "group": res["group"],
                         "mean": res["mean"], "ci_lo": res["ci_lo"],
                         "ci_hi": res["ci_hi"], "n": res["n_rows"],
                         "excludes_zero_ref": excl,
                         "es_sd_row": es.get("sd_row", np.nan),
                         "es_sd_pos": es.get("sd_pos", np.nan),
                         "es_sd_eb": es.get("sd_eb", np.nan),
                         "es_primary": es_p, "denom_primary": denom_name,
                         "passes_0.05": es_p >= 0.05,
                         "passes_0.10": es_p >= 0.10,
                         "passes_0.25": es_p >= 0.25})

    # ---- the review's gradient: spread of domain means ----
    print("\n  GRADIENT (max - min of the four domain means):")
    for stage, pool in (("disagreement_domain", sd_dis),
                        ("domain_rank_resid", sd_rr)):
        ms = [r["mean"] for r in out_rows if r["stage"] == stage]
        span = max(ms) - min(ms)
        ratios = {k: span / v for k, v in pool.items()}
        print(f"    {stage:22s} span={span:.5f}  ratios=" +
              " ".join(f"{k}={v:.3f}" for k, v in ratios.items()))
        out_rows.append({"stage": "gradient", "group": stage, "mean": span,
                         "ci_lo": np.nan, "ci_hi": np.nan, "n": np.nan,
                         "excludes_zero_ref": None,
                         "es_sd_row": ratios.get("sd_row", np.nan),
                         "es_sd_pos": ratios.get("sd_pos", np.nan),
                         "es_sd_eb": ratios.get("sd_eb", np.nan),
                         "es_primary": min(ratios.values()),
                         "denom_primary": max(pool, key=pool.get),
                         "passes_0.05": min(ratios.values()) >= 0.05,
                         "passes_0.10": min(ratios.values()) >= 0.10,
                         "passes_0.25": min(ratios.values()) >= 0.25})

    # ---- verdict (pre-registered rule) ----
    flagged = [r for r in out_rows if r["stage"] != "gradient"
               and r["excludes_zero_ref"] is True]
    print("\nVERDICT (rule fixed in the docstring before running):")
    if not flagged:
        verdict = "NO GROUP PASSED script 36's CI gate to begin with"
    else:
        below = [r for r in flagged if r["es_primary"] < FLOOR_PRIMARY]
        if not below:
            verdict = (f"GATE SURVIVES the effect floor "
                       f"({len(flagged)} of {len(flagged)} CI-passing "
                       f"groups have es >= {FLOOR_PRIMARY})")
        elif len(below) == len(flagged):
            verdict = (f"GATE FAILS the effect floor (all {len(flagged)} "
                       f"CI-passing groups below {FLOOR_PRIMARY})")
        else:
            verdict = (f"GATE DOWNGRADED: {len(below)} of {len(flagged)} "
                       f"CI-passing groups below the {FLOOR_PRIMARY} floor: "
                       + ", ".join(f"{r['stage']}/{r['group']} "
                                   f"({r['es_primary']:.3f})"
                                   for r in below))
        band = ", ".join(
            f"floor {f}: {sum(r['es_primary'] >= f for r in flagged)}"
            f"/{len(flagged)} pass"
            for f in FLOOR_BANDS + (FLOOR_PRIMARY,))
        verdict += f"  [bands: {band}]"
    print(f"  {verdict}")

    out = PROC / "task48_e1a_effect_sizes.csv"
    pd.DataFrame(out_rows).to_csv(out, index=False)
    print(f"\nSaved to {out}")
    return verdict


def part_b(df):
    print("\n" + "=" * 74)
    print("E1b  DOMAIN vs REGION BOUNDARY STEP TEST on the disagreement profile")
    print("=" * 74)

    d = (df.dropna(subset=["eb_disagreement"])
           .groupby("position")["eb_disagreement"].mean().sort_index())
    P = d.index.to_numpy()
    vals = d.to_numpy()
    idx = {int(p): i for i, p in enumerate(P)}
    n = len(P)
    missing = sorted(set(range(int(P.min()), int(P.max()) + 1))
                     - set(map(int, P)))
    print(f"Per-position disagreement: {n} positions "
          f"({int(P.min())}..{int(P.max())}); positions absent from data: "
          f"{missing}")

    # domain label changes, adjacent residue pairs only
    st = load_structural_features().rename(
        columns={"Position": "position", "Domain": "domain"})
    st["domain"] = st["domain"].fillna("unassigned")
    st = st.sort_values("position")
    pos = st["position"].to_numpy()
    dom = st["domain"].to_numpy()
    dom_b = [int(pos[i]) for i in range(1, len(pos))
             if dom[i] != dom[i - 1] and pos[i] == pos[i - 1] + 1]
    reg_b = [REGION_BOUNDS[r][0] for r in sorted(REGION_BOUNDS)][1:]
    sets = {"DOMAIN": dom_b, "REGION": reg_b}
    print(f"DOMAIN label-change boundaries (adjacent pairs only): {dom_b}")
    print(f"REGION boundaries from scripts/lib/regions.py:        {reg_b}")

    rows, verdict = [], None
    for w in (W_PRIMARY,) + tuple(W_SENS):
        M_rows, meta = [], []
        for set_name, bounds in sets.items():
            for b in bounds:
                L = [idx[p] for p in range(b - w, b) if p in idx]
                R = [idx[p] for p in range(b, b + w) if p in idx]
                if len(L) != w or len(R) != w:
                    rows.append({"w": w, "set": set_name, "boundary": b,
                                 "testable": False, "n_left": len(L),
                                 "n_right": len(R), "step": np.nan,
                                 "p_perm": np.nan, "p_shift": np.nan,
                                 "p_verdict": np.nan})
                    print(f"  w={w} {set_name} boundary {b}: DROPPED "
                          f"(windows need {w} residues, have "
                          f"{len(L)}/{len(R)})")
                    continue
                row = np.zeros(n)
                row[R] = 1.0 / w
                row[L] = -1.0 / w
                M_rows.append(row)
                meta.append((set_name, b))
        if not M_rows:
            print(f"w={w}: NO testable boundaries in either set -- UNTESTABLE")
            continue
        M = np.vstack(M_rows)
        steps_obs = M @ vals
        abs_obs = np.abs(steps_obs)
        sets_idx = {s: [i for i, m in enumerate(meta) if m[0] == s]
                    for s in sets}
        T_obs = {s: (float(abs_obs[sets_idx[s]].max())
                     if sets_idx[s] else np.nan) for s in sets}

        # null a: position permutation (N_PERM draws)
        rng = np.random.default_rng(SEED)
        cnt_b = np.zeros(len(meta))
        cnt_s = {s: 0 for s in sets}
        for _ in range(N_PERM):
            absp = np.abs(M @ rng.permutation(vals))
            cnt_b += (absp >= abs_obs)
            for s in sets:
                if sets_idx[s] and absp[sets_idx[s]].max() >= T_obs[s]:
                    cnt_s[s] += 1
        p_perm_b = (1 + cnt_b) / (N_PERM + 1)
        p_perm_s = {s: (1 + cnt_s[s]) / (N_PERM + 1) for s in sets}

        # null b: circular shift over all n-1 nonzero offsets (exact)
        cntb2 = np.zeros(len(meta))
        cnts2 = {s: 0 for s in sets}
        for k in range(1, n):
            absp = np.abs(M @ np.roll(vals, k))
            cntb2 += (absp >= abs_obs)
            for s in sets:
                if sets_idx[s] and absp[sets_idx[s]].max() >= T_obs[s]:
                    cnts2[s] += 1
        p_shift_b = (1 + cntb2) / n
        p_shift_s = {s: (1 + cnts2[s]) / n for s in sets}

        w_label = ("(PRIMARY)" if w == W_PRIMARY
                   else "(sensitivity, not verdict-bearing)")
        print(f"\n  --- w={w} {w_label} ---")
        for i, (s, b) in enumerate(meta):
            pv = max(p_perm_b[i], p_shift_b[i])
            rows.append({"w": w, "set": s, "boundary": b, "testable": True,
                         "n_left": w, "n_right": w,
                         "step": float(steps_obs[i]),
                         "p_perm": float(p_perm_b[i]),
                         "p_shift": float(p_shift_b[i]),
                         "p_verdict": float(pv)})
            mark = ("  <-- uncorrected p<0.05 under both nulls"
                    if p_perm_b[i] < ALPHA and p_shift_b[i] < ALPHA else "")
            print(f"  {s:6s} b={b:4d}  step={steps_obs[i]:+.5f}  "
                  f"p_perm={p_perm_b[i]:.4f} p_shift={p_shift_b[i]:.4f}"
                  f"{mark}")
        for s in sets:
            if not sets_idx[s]:
                print(f"  {s:6s}: 0 testable boundaries")
                rows.append({"w": w, "set": s, "boundary": "SET_MAX",
                             "testable": False, "n_left": np.nan,
                             "n_right": np.nan, "step": np.nan,
                             "p_perm": np.nan, "p_shift": np.nan,
                             "p_verdict": np.nan})
                continue
            pv = max(p_perm_s[s], p_shift_s[s])
            rows.append({"w": w, "set": s, "boundary": "SET_MAX",
                         "testable": True, "n_left": np.nan,
                         "n_right": np.nan, "step": T_obs[s],
                         "p_perm": p_perm_s[s], "p_shift": p_shift_s[s],
                         "p_verdict": pv})
            print(f"  {s:6s} SET MAX |step|={T_obs[s]:.5f}  "
                  f"p_perm={p_perm_s[s]:.4f} p_shift={p_shift_s[s]:.4f} "
                  f"p_SET=max={pv:.4f}  ({len(sets_idx[s])} boundaries)")

        if w == W_PRIMARY:
            pv = {}
            for s in sets:
                pv[s] = (max(p_perm_s[s], p_shift_s[s])
                         if sets_idx[s] else None)
            if pv["DOMAIN"] is None or pv["REGION"] is None:
                verdict = ("UNTESTABLE (a set has zero testable boundaries "
                           f"at w={W_PRIMARY})")
            else:
                dom_sig = pv["DOMAIN"] < ALPHA
                reg_sig = pv["REGION"] < ALPHA
                if dom_sig and not reg_sig:
                    verdict = ("DIVERGENCE: domain-boundary step found "
                               "(p<0.05), region-boundary step not found")
                elif reg_sig and not dom_sig:
                    verdict = ("DIVERGENCE: region-boundary step found "
                               "(p<0.05), domain-boundary step not found")
                elif dom_sig and reg_sig:
                    verdict = ("CONCORDANCE: both boundary sets show a step "
                               "(p<0.05)")
                else:
                    verdict = ("NEITHER boundary set shows a step (both "
                               f"p>={ALPHA})")
            print(f"\n  VERDICT at w={W_PRIMARY}, alpha={ALPHA}, "
                  f"p_set = max(permutation, circular-shift):")
            print(f"    {verdict}")

    if verdict is None:
        verdict = ("UNTESTABLE (zero testable boundaries at primary "
                   f"w={W_PRIMARY})")
    out = PROC / "task48_e1b_boundary_steps.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved to {out}")
    return verdict


if __name__ == "__main__":
    df = rebuild_task36_set()
    v_a = part_a(df)
    v_b = part_b(df)

    print("\n" + "=" * 74)
    print("LIMITATIONS (AGENTS 6: printed by the script, not just the writeup)")
    print("=" * 74)
    print(f"  E1a verdict: {v_a}")
    print(f"  E1b verdict: {v_b}")
    print("  - Effect floor 0.10 is POST-HOC (chosen after the review quoted")
    print("    the ~0.03-0.04 vs 0.24 numbers); bands 0.05/0.25 printed too.")
    print("  - 'residual sd / e.b. sd baseline' is ambiguous; the LARGEST")
    print("    candidate sd per group is used as primary (smallest effect).")
    print("  - E1b uses TWO nulls and takes max p: the review specified only")
    print("    position permutation; circular shift added because permutation")
    print("    destroys spatial autocorrelation and can be anti-conservative.")
    print("    The circular-shift null treats the chain as circular (it is")
    print("    not); it serves only as the conservative tie-breaker.")
    print("  - E1b tests alignment of a profile with boundaries, not causation.")
    print("  - Overlapping windows (domain 36/48 at w=25) handled by the max")
    print("    statistic, not multiplicity correction.")
    print("  - Inherited power caveat (script 36): one alternate background")
    print("    only; a null result here is weak evidence of absence.")
    print("  - Effect sizes use in-sample sds; nothing is predicted, so the")
    print("    cross-fit rule does not apply -- disclosed anyway.")
    print(f"  - Settings: N_BOOT={N_BOOT}, N_PERM={N_PERM}, SEED={SEED}.")
