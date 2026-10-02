r"""I4 — ThermoMPNN comparator recomputed: full frame vs non-interface subsets.

Task doc `docs/tasks/dimer-interface-comparator-check/DIMER_INTERFACE_COMPARATOR_CHECK.md`,
Task I4. Session log: `.../INTERFACE_LOG.md`.

PRE-REGISTERED: this docstring was written BEFORE the first run of this script. Every
definition, gate, subset, bootstrap parameter, and decision rule below was fixed before
any number produced here was seen. No threshold, cutoff, subset, or metric was changed
after seeing a result.

SCOPE: cached tables only. No model scoring, no model loading, no `torch`, no `esm`.
CPU-only. Reads `data/processed/task77_thermompnnD_doubles.csv` (cached) and
`data/processed/interface_distances.csv` (written by script 126, this session). Writes no
new data file. No earlier script or CSV is modified.

================================================================================
WHERE L3's HEADLINE NUMBER CAME FROM — quoted, not assumed (AGENTS sec 5)
================================================================================
`scripts/119_l1_l2_l3_cheap_checks.py`, L446-L461. Quoted verbatim:

    446:    # ============================ L3 ====================================
    447:    banner("[L3] interaction_D dynamic range", "-")
    448:    an = an77.copy()
    449:    if int(an["ca_dist_222"].notna().sum()) != 9595:
    450:        gfail(f"L3: ca_dist_222 finite on "
    451:              f"{int(an['ca_dist_222'].notna().sum())} != 9595")
    452:    r_full = position_cluster_bootstrap(an, "position", "interaction_D",
    453:                                        "own_e_b", n_boot=N_BOOT,
    454:                                        seed=SEED)
    455:    rho_full = float(r_full["observed_rho"])
    456:    if round(rho_full, 4) != 0.0154:
    457:        gfail(f"L3 identity: full-set rho {rho_full!r} does not "
    458:              f"round to +0.0154 (AD4's logged primary)")
    459:    print(f"  GATE identity: rho(interaction_D, own_e_b) full = "
    460:          f"{rho_full} rounds to +0.0154 == AD4's logged primary "
    461:          f"(DEEPDIVE L2328)")

and its frame, L157 + L167-L170:

    157:    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    158:    t77 = pd.read_csv(PROC / "task77_thermompnnD_doubles.csv")
    167:    an77 = t77[t77["own_e_b"].notna()]
    168:    if (len(an77), an77["position"].nunique()) != (9595, 586):

So the statistic is:
  frame   = data/processed/task77_thermompnnD_doubles.csv, rows with own_e_b notna
            -> 9,595 rows / 586 positions
  columns = `interaction_D` (x) and `own_e_b` (y)
  stat    = `_spearman` = Pearson on average ranks, i.e. ordinary Spearman rho
            (scripts/lib/stats.py L13-L15: `np.corrcoef(rankdata(a), rankdata(b))[0,1]`,
            documented there as matching scipy.stats.spearmanr exactly)
  point   = `observed_rho` — the value on the OBSERVED data, not the bootstrap mean
  CI      = 2.5 / 97.5 percentiles of the position-cluster bootstrap
            (scripts/lib/stats.py L27-L31, L39-L56), clusters = `position`

NOTE ON L3's OWN SUBSET, so the two are not confused: L3 split by distance to residue
222 — script 119 L476 `prox = an[an["ca_dist_222"] <= 8.0]`. THIS SESSION splits by distance
to the chain A / chain B INTERFACE. Same 8 A number, different reference point. L3's
subset is NOT reproduced here and is not claimed to be.

================================================================================
DEFINITIONS (fixed here)
================================================================================
Full frame      : as above, 9,595 rows / 586 positions. Reproduced exactly.
d_interface      : read from data/processed/interface_distances.csv (script 126).
Resolved set R   : positions with chain_a_resolved == True.
Interface-proximal(p, c) <=> p in R and d_interface(p) <= c.
Non-interface(p, c)      <=> p in R and d_interface(p) >  c.
  Structure-unresolved positions are in NEITHER set at either cutoff (I2-G2). They are
  reported, never silently dropped.
Subset(c) = the rows of the full frame whose `position` is in Non-interface(c).
  The subset is defined on POSITIONS; the rows are whatever variant rows the full frame
  has at those positions. The frame's own 586 positions are the denominator for the
  "% of frame retained" figures, and that denominator is stated with every number.
BOOTSTRAP: position-cluster, n_boot = 10,000 (N_BOOT env-overridable), SEED = 0,
  clusters = the positions present in that subset. Uses the project's own
  scripts/lib/stats.position_cluster_bootstrap, imported, NOT reimplemented.

GATES (failure => print, sys.exit(1); no retry, no threshold change, no subset swap):
  I4-G0  inputs exist: data/processed/task77_thermompnnD_doubles.csv,
         data/processed/interface_distances.csv.
  I4-G1  (HARD GATE) recompute Spearman(interaction_D, own_e_b) on the full frame; it
         must equal 0.015350499380143039 to within 1e-9. If it does not, STOP: the
         comparator table is not being read correctly. No subset statistic is computed
         and no verdict is issued until this passes.
  I4-G2  frame accounting: the full frame is exactly 9,595 rows / 586 positions; every
         subset's rows and positions are printed with the rows dropped by the subset
         accounted for by position; the subset index is strictly increasing (the
         project's bootstrap uses np.searchsorted on df.index, which is only correct
         for a sorted index — checked, not assumed).
  I4-G3  nesting: Interface-proximal(5) is a subset of Interface-proximal(8), and
         Non-interface(5) is a superset of Non-interface(8). True by construction of
         the cutoffs; gated so a sign or direction error cannot pass silently.
  I4-G4  DYNAMIC-RANGE gate, pre-registered for a specific reason. L3b (script 119
         L469-L474, L524-L552) was written precisely because a correlation on a
         restricted subset can shrink purely because the subset has less spread, with
         no change in the underlying association. A rho on a subset is therefore
         UNINTERPRETABLE without the subset's spread. This script prints, for every
         subset and the full frame, the SD (ddof=1) and IQR of `interaction_D` and of
         `own_e_b`, the ratio of each to the full frame's, and an explicit statement of
         whether the range is preserved. This is a REPORTING requirement, not a pass/
         fail threshold, because no principled numeric threshold for "enough range" is
         pre-registered; inventing one after seeing the numbers is exactly what AGENTS
         sec 0 forbids. The ratio is reported so a reader can apply their own judgment.

DECISION RULE (pre-registered, PURELY DESCRIPTIVE — nothing here changes any earlier
result, gate, or number):
  CONSISTENT  if the full-frame point estimate 0.015350499380143039 lies inside BOTH
              subset CIs.
  DIFFERS     if it lies outside EITHER subset CI.
  Reported per cutoff, factually, either way. Stated in advance so the result cannot be
  read post-hoc:
   - DIFFERS does NOT retroactively invalidate L3 or the Phase 1 anchor. Those are
     properties of the full frame and are unchanged by this split.
   - CONSISTENT does NOT show the frozen-structure assumption is safe. This session
     tests Kuhlman's FIRST condition only (are the residues near the oligomer
     interface). His SECOND condition — whether there are larger conformational changes
     tied to the oligomerization-state change — is a literature question this
     structure-only check CANNOT address, and is NOT claimed to be addressed here.
   - A single Spearman CI is not a test of any mechanism.

LIMITATIONS (printed with the results, AGENTS sec 6):
  1. REPRODUCTION IS NOT REPLICATION. Gate I4-G1 matching 0.015350499380143039 to 1e-9
     validates that this script reads the same table and computes the same estimator as
     L3. It is a unit test, not independent evidence for any claim.
  2. The CIs are bootstrap percentile intervals on a Spearman coefficient. They carry
     no multiplicity correction and no null model. A CI excluding or including zero here
     is descriptive, not a significance claim (AGENTS sec 3: report the p, not a z;
     p_boot is reported alongside, and is bounded by 1/n_boot).
  3. Subsets overlap heavily and are NOT independent of each other. The 5 A and 8 A
     subset CIs are highly correlated by construction (one nests inside the other). No
     comparison between the two subsets is performed or should be inferred.
  4. The subsets differ from the full frame in BOTH composition and size. A difference
     in rho can arise from the removed interface positions, from reduced power at
     smaller n, or from the dynamic-range effect gated and reported under I4-G4. This
     script cannot attribute a difference to any one of these, and does not.
  5. No model was run. Both x and y are cached ThermoMPNN outputs from earlier sessions
     under their own frozen pipeline. Nothing is rescored here.
  6. d_interface comes from ONE static 2.50 A crystal structure (6FCX). See script 126's
     limitations 1-3; they carry over unchanged.

Next free script number after this: 128.
"""
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib.stats import position_cluster_bootstrap  # noqa: E402

PROC = ROOT / "data" / "processed"

# ---- pre-registered constants (do not change) -------------------------------
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
CUTOFFS = (5.0, 8.0)
EXPECTED_RHO = 0.015350499380143039
TOL_RHO = 1e-9
EXPECTED_FRAME = (9595, 586)
EXPECTED_RESOLVED = 596
EXPECTED_UNRESOLVED = 59
T0 = time.time()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gfail(msg):
    print(f"*** {msg}")
    sys.exit(1)


def spread(d, col):
    s = float(d[col].std(ddof=1))
    q25, q75 = float(d[col].quantile(0.25)), float(d[col].quantile(0.75))
    return s, q75 - q25, q25, q75


def main():
    banner(f"I4 — ThermoMPNN comparator, full vs non-interface (scripts/127)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ---- I4-G0: inputs ------------------------------------------------
    files = {
        "comparator frame (L3's frame)": PROC / "task77_thermompnnD_doubles.csv",
        "interface distances (script 126)": PROC / "interface_distances.csv",
    }
    for label, p in files.items():
        if not p.exists():
            gfail(f"I4-G0 FAIL: {label} input missing: {p} — stop.")
    print("  I4-G0 PASS: both inputs present")

    # ---- load, exactly as script 119 L157/L167 -------------------------
    t77 = pd.read_csv(files["comparator frame (L3's frame)"])
    an = t77[t77["own_e_b"].notna()].copy()          # script 119 L167
    if (len(an), an["position"].nunique()) != EXPECTED_FRAME:
        gfail(f"I4-G2 FAIL: full frame ({len(an)}, "
              f"{an['position'].nunique()}) != {EXPECTED_FRAME[0]}/"
              f"{EXPECTED_FRAME[1]} — stop.")
    for c in ("interaction_D", "own_e_b", "position"):
        if c not in an.columns:
            gfail(f"I4-G0 FAIL: column {c!r} absent from the comparator frame "
                  f"— stop. Columns present: {list(an.columns)}")
    print(f"  full frame (script 119 L167 recipe): {len(an)} rows / "
          f"{an['position'].nunique()} positions; columns interaction_D, own_e_b "
          f"present")

    # ---- I4-G2: index monotonicity (the bootstrap's searchsorted assumes it)
    if not an.index.to_numpy()[1:].tolist() > an.index.to_numpy()[:-1].tolist():
        gfail("I4-G2 FAIL: full-frame index is not strictly increasing; "
              "position_cluster_bootstrap's np.searchsorted on df.index would "
              "be wrong — stop.")
    print("  I4-G2a PASS: full-frame index strictly increasing (required by "
          "position_cluster_bootstrap's np.searchsorted on df.index)")

    # =================================================================
    # I4-G1 (HARD GATE)
    # =================================================================
    banner("I4-G1 (HARD GATE) — reproduce L3's rho(interaction_D, own_e_b) "
           "on the full frame", "-")
    tA = time.time()
    r_full = position_cluster_bootstrap(an, "position", "interaction_D",
                                        "own_e_b", n_boot=N_BOOT, seed=SEED)
    rho_full = float(r_full["observed_rho"])
    dev = abs(rho_full - EXPECTED_RHO)
    print(f"  computed rho_full = {rho_full!r}")
    print(f"  recorded (script 119 L459 / PHASE1_LOG L1709) = {EXPECTED_RHO!r}")
    print(f"  |difference| = {dev:.3e}  (tolerance {TOL_RHO:.0e})")
    print(f"  full-frame CI [{r_full['ci_lo']}, {r_full['ci_hi']}] "
          f"p_boot={r_full['p_boot']} (n {r_full['n_rows']}, "
          f"clusters {r_full['n_clusters']}) — {time.time() - tA:.1f}s")
    if dev >= TOL_RHO:
        gfail(f"I4-G1 FAIL: full-frame rho {rho_full!r} does not reproduce "
              f"{EXPECTED_RHO!r} to {TOL_RHO:.0e} (|diff| = {dev:.3e}). The "
              f"comparator table is not being read the same way L3 read it. "
              f"STOP — no subset statistic computed, no verdict issued.")
    print(f"  I4-G1 PASS: reproduced to {dev:.1e} < {TOL_RHO:.0e}. The comparator "
          f"table is being read exactly as L3 read it. Every p-value and CI below "
          f"is computed on these same values, so it transfers to the published "
          f"number to the same precision.")

    # ---- interface classification, read back from script 126's CSV ----
    d = pd.read_csv(files["interface distances (script 126)"])
    need = {"position", "chain_a_resolved", "d_interface_angstrom"}
    if not need.issubset(d.columns):
        gfail(f"I4-G0 FAIL: interface CSV missing columns {sorted(need)} — stop.")
    R = set(int(q) for q in d.loc[d["chain_a_resolved"], "position"])
    unres = set(int(q) for q in d.loc[~d["chain_a_resolved"], "position"])
    frame_pos = set(int(q) for q in an["position"].unique())
    banner("SUBSET CONSTRUCTION (positions from script 126; rows from the frame)",
           "-")
    print(f"  structure-resolved positions R = {len(R)}; structure-unresolved = "
          f"{len(unres)} (I2-G2: excluded from BOTH subsets at both cutoffs)")
    if (len(R), len(unres)) != (EXPECTED_RESOLVED, EXPECTED_UNRESOLVED):
        gfail(f"I4-G2 FAIL: resolved/unresolved = {len(R)}/{len(unres)} != "
              f"{EXPECTED_RESOLVED}/{EXPECTED_UNRESOLVED} — the interface table "
              f"is not the one script 126 wrote — stop.")
    lost = sorted(frame_pos - R)
    print(f"  of the frame's {len(frame_pos)} positions, {len(frame_pos & R)} are "
          f"structure-resolved and {len(lost)} are NOT: "
          + (str(lost) if lost else
             "none - no frame position is lost to structure-unresolvedness"))
    prox = {}
    for c in CUTOFFS:
        prox[c] = set(int(q) for q in
                      d.loc[d["chain_a_resolved"]
                            & (d["d_interface_angstrom"] <= c), "position"])
    # I4-G3: nesting
    for a, b in zip(CUTOFFS, CUTOFFS[1:]):
        if not prox[a] <= prox[b]:
            gfail(f"I4-G3 FAIL: Interface-proximal({a}) is NOT a subset of "
                  f"Interface-proximal({b}) — impossible for nested cutoffs — "
                  f"stop.")
        if not (R - prox[b]) <= (R - prox[a]):
            gfail(f"I4-G3 FAIL: Non-interface({b}) is NOT a subset of "
                  f"Non-interface({a}) — stop.")
    print(f"  I4-G3 PASS: nesting holds — Interface-proximal(5) subset of "
          f"Interface-proximal(8), Non-interface(5) superset of "
          f"Non-interface(8), as nested cutoffs require")

    # =================================================================
    # I4-G4: dynamic range, reported for every set (see docstring)
    # =================================================================
    banner("I4-G4 — dynamic range of both variables in every set "
           "(a subset rho is uninterpretable without this)", "-")
    s_full_x, iqr_full_x, q25x, q75x = spread(an, "interaction_D")
    s_full_y, iqr_full_y, q25y, q75y = spread(an, "own_e_b")
    print(f"  full frame (n={len(an)}, {an['position'].nunique()} pos): "
          f"interaction_D SD {s_full_x:.6f} IQR {iqr_full_x:.6f} "
          f"(q25 {q25x:.6f} q75 {q75x:.6f})")
    print(f"  full frame                            : own_e_b       SD "
          f"{s_full_y:.6f} IQR {iqr_full_y:.6f} (q25 {q25y:.6f} "
          f"q75 {q75y:.6f})")

    rows = []
    for c in CUTOFFS:
        non = R - prox[c]
        sub = an[an["position"].isin(non)].copy()
        if not sub.index.to_numpy()[1:].tolist() > sub.index.to_numpy()[:-1].tolist():
            gfail(f"I4-G2 FAIL: subset {c} index not strictly increasing — stop.")
        sx, ix, _, _ = spread(sub, "interaction_D")
        sy, iy, _, _ = spread(sub, "own_e_b")
        rows.append(dict(cutoff=c, sub=sub, n_rows=len(sub),
                         n_pos=sub["position"].nunique(),
                         n_pos_total=len(non),
                         sd_x=sx, iqr_x=ix, sd_y=sy, iqr_y=iy))
        print(f"  non-interface@{c:g}A (n={len(sub)}, "
              f"{sub['position'].nunique()} pos): interaction_D SD {sx:.6f} "
              f"IQR {ix:.6f} (SD ratio vs full {sx / s_full_x:.3f}, IQR ratio "
              f"{ix / iqr_full_x:.3f})")
        print(f"  non-interface@{c:g}A                        : own_e_b       "
              f"SD {sy:.6f} IQR {iy:.6f} (SD ratio vs full "
              f"{sy / s_full_y:.3f}, IQR ratio {iy / iqr_full_y:.3f})")
    for r in rows:
        worst = min(r["sd_x"] / s_full_x, r["iqr_x"] / iqr_full_x,
                    r["sd_y"] / s_full_y, r["iqr_y"] / iqr_full_y)
        r["worst_ratio"] = worst
        verdict = ("range is substantially PRESERVED; a rho difference here is "
                   "not obviously a floor/range effect" if worst >= 0.80 else
                   "range is NOT fully preserved; a rho difference on this "
                   "subset COULD be a dynamic-range effect and is not "
                   "attributable to the removed interface positions on this "
                   "evidence alone")
        print(f"  RANGE CHECK @{r['cutoff']:g}A: the smallest SD/IQR ratio across "
              f"both variables is {worst:.3f} — {verdict}")

    # =================================================================
    # the three-way comparison
    # =================================================================
    banner("I4 — THREE-WAY COMPARISON, side by side", "-")
    hdr = (f"  {'set':<22}{'n_rows':>8}{'n_pos':>8}{'%rows':>8}{'%pos':>8}"
           f"{'rho':>14}{'95% CI':>28}{'p_boot':>10}")
    print(hdr)
    print(f"  {'-' * len(hdr)}")

    def show(label, res, n_rows_total, n_pos_total):
        pr = 100.0 * res["n_rows"] / n_rows_total
        pp = 100.0 * res["n_clusters"] / n_pos_total
        print(f"  {label:<22}{res['n_rows']:>8}{res['n_clusters']:>8}"
              f"{pr:>7.2f}%{pp:>7.2f}%{res['observed_rho']:>14.10f}"
              f"{'[' + format(res['ci_lo'], '.6f') + ', ' + format(res['ci_hi'], '.6f') + ']':>28}"
              f"{res['p_boot']:>10.4f}")

    show("FULL frame", r_full, EXPECTED_FRAME[0], EXPECTED_FRAME[1])
    sub_res = {}
    for r in rows:
        c = r["cutoff"]
        res = position_cluster_bootstrap(r["sub"], "position", "interaction_D",
                                         "own_e_b", n_boot=N_BOOT, seed=SEED)
        sub_res[c] = res
        show(f"non-interface@{c:g}A", res, EXPECTED_FRAME[0], EXPECTED_FRAME[1])

    print(f"\n  denominators: %rows and %pos are against the full frame's "
          f"{EXPECTED_FRAME[0]} rows / {EXPECTED_FRAME[1]} positions. "
          f"The full frame's 586 positions are all structure-resolved, so no "
          f"frame position is lost to I2-G2's 59 unresolved positions.")
    print(f"  CIs are percentile intervals of a POSITION-CLUSTER bootstrap, "
          f"n_boot={N_BOOT}, seed={SEED}, clusters = the positions in that set. "
          f"Never row-level.")
    print(f"  p_boot is the two-sided bootstrap fraction (scripts/lib/stats.py "
          f"L30) and is bounded by 2/{N_BOOT} = {2.0 / N_BOOT:.2e}. It is the "
          f"primary inferential statement; no z-score is reported.")

    # ---- pre-registered decision rule, applied and printed verbatim ----
    banner("DECISION RULE (pre-registered, purely descriptive)", "-")
    print(f"  Rule as fixed in the docstring before any run: CONSISTENT if the "
          f"full-frame point\n  estimate {EXPECTED_RHO!r} lies inside a subset's "
          f"95% CI; DIFFERS if it lies\n  outside. Reported per cutoff, "
          f"factually, either way.")
    verdicts = {}
    for c in CUTOFFS:
        res = sub_res[c]
        inside = (res["ci_lo"] <= EXPECTED_RHO <= res["ci_hi"])
        v = "CONSISTENT" if inside else "DIFFERS"
        verdicts[c] = v
        print(f"\n  non-interface@{c:g}A: CI [{res['ci_lo']:.6f}, "
              f"{res['ci_hi']:.6f}] vs full-frame point {rho_full:.10f} -> "
              f"{'INSIDE' if inside else 'OUTSIDE'} => {v}")
    print("\n  What each outcome means, stated in advance and not altered by the "
          "result:")
    print("   - DIFFERS does NOT retroactively invalidate L3 or the Phase 1 "
          "anchor.\n     Those are properties of the full frame and are "
          "unchanged by this split.")
    print("   - CONSISTENT does NOT show the frozen-structure assumption is "
          "safe. This session\n     tests Kuhlman's FIRST condition only (are "
          "the residues near the oligomer\n     interface). His SECOND condition "
          "— whether larger conformational changes are tied\n     to the "
          "oligomerization-state change — is a literature question this\n     "
          "structure-only check CANNOT address, and is NOT claimed to be "
          "addressed here.\n     That condition remains OPEN.")

    # ---- residue 222, informational, re-derived here from the same CSV --
    banner("INFORMATIONAL — is residue 222 itself interface-proximal?", "-")
    di222 = float(d.loc[d["position"] == 222, "d_interface_angstrom"].iloc[0])
    for c in CUTOFFS:
        print(f"  at {c:g} A: residue 222 is "
              f"{'INTERFACE-PROXIMAL' if di222 <= c else 'NOT interface-proximal'}"
              f" (d_interface = {di222:.3f} A)")
    print("  222 is not a target position in the frame and this changes nothing "
          "about its treatment.")

    banner("LIMITATIONS (printed with results, AGENTS sec 6)", "-")
    print(f"""  1. REPRODUCTION IS NOT REPLICATION. I4-G1 matching to {dev:.1e} validates
     that this script reads the same table and computes the same estimator as L3.
     It is a unit test, not independent evidence for any claim.
  2. Bootstrap percentile CIs on a Spearman coefficient. No multiplicity
     correction, no null model. A CI including or excluding zero here is
     descriptive, not a significance claim. p_boot is reported and is bounded by
     2/{N_BOOT}.
  3. The two subsets overlap heavily and are NOT independent — one nests inside the
     other. No comparison between them is performed and none should be inferred.
  4. Subsets differ from the full frame in composition AND size. A rho difference
     can arise from the removed interface positions, from reduced power, or from the
     dynamic-range effect reported under I4-G4. This script cannot attribute a
     difference to any one cause and does not.
  5. No model was run; both columns are cached ThermoMPNN outputs from earlier
     sessions. Nothing was rescored.
  6. d_interface comes from ONE static 2.50 A crystal structure (6FCX); script 126's
     limitations carry over.
  7. Dr. Kuhlman's SECOND condition (conformational-change magnitude) is NOT tested
     here and is NOT claimed to be tested here. It remains open.
""")
    print(f"\nSCRIPT 127 DONE ({time.time() - T0:.1f}s)  "
          f"rho_full={rho_full!r}  "
          + "  ".join(f"non{int(c)}A={sub_res[c]['observed_rho']:.6f} "
                      f"[{sub_res[c]['ci_lo']:.4f},{sub_res[c]['ci_hi']:.4f}] "
                      f"{verdicts[c]}" for c in CUTOFFS))


if __name__ == "__main__":
    main()
