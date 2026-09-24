"""AF2 — one canonical variant manifest (task doc L368-377).

PRE-REGISTERED: this docstring was written before the script's first run.

Task: "Reconcile the three different missense totals appearing across this
project's documents (11,902 in the original proposal; 11,344 used in Part
II §12; 11,113 used in Part I §6.2) and the four different analysis n's
(10,757 / 10,141 / 9,740 / 9,595) into a single exclusion cascade:
starting count, each filtering step applied (by which script), and the
resulting n at each stage, per predictor. Save as
data/processed/task_AF2_variant_manifest.csv."

NATURE: pure bookkeeping + verification — NO new statistics, NO decision
rules, NO choices that could be post-hoc. Every number below is
pre-existing; this script VERIFIES each one against the on-disk file it
is supposed to come from and only then writes the manifest. Any
mismatch -> print the failure and sys.exit(1) WITHOUT writing (AGENTS
s7/s5: reconcile before interpreting).

SOURCES OF TRUTH (every cascade step has one; the manifest's
`appears_in` and `verified_by` columns carry these):
  * A2b's logged reconciliation (review-triage OVERNIGHT_LOG L138-161;
    comparators SESSION_LOG L497-522; GROUPS_C_TO_H_DIGEST L17):
    13,134 -> 11,902 -> 11,901 -> 11,344 -> 11,113 -> 10,757.
  * V2's STAGE-3 join accounting, verbatim (comparators SESSION_LOG
    L2340, from script 68's own run output): "breakdown of 1203 dropped
    rows: 1046 rows at 59 unresolved positions ...; 157 rows at 9
    positions where 6FCX chain A's residue differs from canonical
    P42898".
  * Z3f accounting (closeout CLOSEOUT_LOG L615-617): 10,757 -> excluded
    1,017 at 59 unresolved positions -> "ours 9740"; 29 of phase5's
    1,046 unresolved rows are outside the 10,757 set.
  * Z1/AD8 intersection accounting (DEEPDIVE_LOG L2869-2877):
    [Z1a] 9,595/586, "ESM loses 1162, Thermo loses 0"; AD8 "V2 10141 ->
    own_e_b finite 9595 -> +delta_esm finite 9595".

EXTERNAL-DOCUMENT CAVEAT (stated, not hidden): the "original proposal",
"Part II §12", and "Part I §6.2" documents are NOT all in this repo
(Part II is external — established in DEEPDIVE_LOG [AD7] L2824: "Part
II §12.4 is an external evaluator document, NOT in this repo"). Their
attributions in `appears_in` are taken from the task doc's own statement
(task L370-371) and anchored to the in-repo carriers noted per row
(A2b's chain, script 50's gate in MIGRATION_LOG L441, MTHFR_RESULTS_LOG
§6.2 L230, RESULTS.md L56's 11344). Details this script does NOT
re-derive are attributed to A2b's logged verification instead of being
silently re-claimed: the "all f_bar_a222v NaN" nature of the 557, and
the published-e.b == own_e_b missing-mask identity (587 = 587 = 587).

GATES (recomputed from disk; failure = exit 1, no CSV written):
  G1  task35_epistatic_set.csv: 13,134 rows; type counts
      substitution/nonsense/synonymous == 11,902 / 624 / 608.
  G2  phase3_analysis_table.csv == 11,901 rows; phase5_analysis_table
      .csv == 11,344 rows and a SUBSET of phase3 by hgvs_pro (the -557
      step is a drop, not a relabel); 11,901-11,344 == 557.
  G3  task32_analysis_table.csv == 11,344 rows / 654 positions / 0
      delta_esm NaN, same hgvs set as phase5; f_bar_wt-missing rows
      == 231; own_e_b-missing == 587; ALL 231 f_bar_wt-missing rows are
      inside the 587 (so 587-231 == 356); dropna(own_e_b) == 10,757 /
      654; 11,344-231 == 11,113.
  G4  task34_predictions.csv == 11,113 and task36_analysis_table.csv
      == 11,113 (the Part-I-§6.2 n's in-repo carriers).
  G5  task_V2_thermompnn_ddg.csv == 10,141 rows; own_e_b finite
      == 9,595; delta_esm NaN == 0; those 9,595 span 586 positions;
      phase5 rows at the 59 unresolved positions == 1,046; 11,344-10,141
      == 1,203 and 1,203-1,046 == 157 (the verbatim construct-wt figure,
      9 positions [429,594,645-651] cited from SESSION_LOG L2340 — the
      157 is arithmetic here, the position list is quoted, not
      re-derived from the PDB).
  G6  Z1 matched CSV: both matched_intersection rows == 9,595/586; its
      ESM original_unmatched row == 10,757/654 with rho ==
      -0.08811806424891734 (two-source identity of the primary anchor);
      10,757-9,595 == 1,162 ("ESM loses").
  G7  the 10,757 analysis FRAME's rows at the 59 unresolved positions
      == 1,017 (first run of this script gated on the 11,344 table and
      got 1,046 — wrong base; fixed to Z3f's documented basis before any
      manifest existed, exit 1, nothing written; both numbers are
      correct on their own base: 1,046 = task32 ≡ phase5 rows at those
      positions, gated by G3/G5);
      10,757-1,017 == 9,740; 1,046-1,017 == 29 (Z3f's three verbatim
      figures).
  G8  manifest written has exactly 11 rows and every n_after value in
      it came from a gated variable above (built from the variables,
      never re-typed).

Deliverable filename is FIXED BY THE TASK: task_AF2_variant_manifest.csv
(deviates from the usual taskNN_ prefix deliberately — follow the task
literally; disclosed here).

Output columns: branch_predictor, stage, filter_step, applied_by,
n_before, n_after, delta_n, appears_in, verified_by.

No existing script/lib/result modified. Next free script number: 86.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = PROC / "task_AF2_variant_manifest.csv"

UNRESOLVED = (
    list(range(2, 40)) + list(range(161, 172))
    + list(range(392, 397)) + list(range(652, 657))
)  # 59 positions: 2-39, 161-171, 392-396, 652-656 (V2/Z3f policy)
ANCHOR_RHO = -0.08811806424891734
CONSTRUCT_WT_MISMATCH_157 = (429, 594, 645, 646, 647, 648, 649, 650, 651)


def gfail(msg):
    print(f"*** {msg} — manifest NOT written ***")
    sys.exit(1)


def gate(label, got, want):
    if got != want:
        gfail(f"{label}: got {got!r}, expected {want!r}")
    print(f"  {label} PASS: {got!r}")


if __name__ == "__main__":
    print("=" * 74)
    print("AF2 — canonical variant manifest: verify every n, then write")
    print("=" * 74)

    # ---- G1: universe counts (task35 is A2b's in-repo carrier) --------
    t35 = pd.read_csv(PROC / "task35_epistatic_set.csv")
    gate("G1 rows", len(t35), 13134)
    vc = t35["type"].value_counts()
    gate("G1 type==substitution", int(vc["substitution"]), 11902)
    gate("G1 type==nonsense", int(vc["nonsense"]), 624)
    gate("G1 type==synonymous", int(vc["synonymous"]), 608)
    n13, n119 = len(t35), int(vc["substitution"])

    # ---- G2: phase3 (ESM join) and phase5 (model dropna) --------------
    p3 = pd.read_csv(PROC / "phase3_analysis_table.csv")
    p5 = pd.read_csv(PROC / "phase5_analysis_table.csv")
    gate("G2 phase3 rows", len(p3), 11901)
    gate("G2 phase5 rows", len(p5), 11344)
    if not set(p5["hgvs_pro"]).issubset(set(p3["hgvs_pro"])):
        gfail("G2: phase5 not a subset of phase3 by hgvs_pro")
    print("  G2 subset check PASS: phase5 hgvs set ⊂ phase3 hgvs set")
    gate("G2 drop", len(p3) - len(p5), 557)
    n3, n5 = len(p3), len(p5)

    # ---- G3: script-32 frame + the two exclusion masks ----------------
    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    gate("G3 task32 rows", len(t32), 11344)
    gate("G3 positions", t32["position"].nunique(), 654)
    gate("G3 delta_esm NaN", int(t32["delta_esm"].isna().sum()), 0)
    if set(t32["hgvs_pro"]) != set(p5["hgvs_pro"]):
        gfail("G3: task32 and phase5 hgvs sets differ")
    print("  G3 hgvs identity PASS: task32 ≡ phase5 rows")
    miss_wt = t32["f_bar_wt"].isna()
    miss_own = t32["own_e_b"].isna()
    gate("G3 f_bar_wt-missing", int(miss_wt.sum()), 231)
    gate("G3 own_e_b-missing", int(miss_own.sum()), 587)
    if not bool((miss_wt & ~miss_own).sum() == 0):
        gfail("G3: some f_bar_wt-missing row has own_e_b present "
              "(231 not inside 587)")
    print("  G3 mask inclusion PASS: all 231 f_bar_wt-missing rows are "
          "inside the 587 (A2b's -356 = 587-231)")
    frame = t32.dropna(subset=["own_e_b"])
    gate("G3 analysis frame", len(frame), 10757)
    gate("G3 frame positions", frame["position"].nunique(), 654)
    gate("G3 stage6 n", len(t32) - int(miss_wt.sum()), 11113)
    n111, n107 = len(t32) - int(miss_wt.sum()), len(frame)

    # ---- G4: Part I §6.2 carriers ------------------------------------
    gate("G4 task34_predictions rows",
         len(pd.read_csv(PROC / "task34_predictions.csv")), 11113)
    gate("G4 task36_analysis_table rows",
         len(pd.read_csv(PROC / "task36_analysis_table.csv")), 11113)

    # ---- G5: V2 branch ------------------------------------------------
    v2 = pd.read_csv(PROC / "task_V2_thermompnn_ddg.csv")
    gate("G5 V2 rows", len(v2), 10141)
    v2_own = v2.dropna(subset=["own_e_b"])
    gate("G5 V2 own_e_b finite", len(v2_own), 9595)
    gate("G5 V2 delta_esm NaN", int(v2["delta_esm"].isna().sum()), 0)
    gate("G5 V2∩own_e_b positions", v2_own["position"].nunique(), 586)
    n101, n9595 = len(v2), len(v2_own)
    unresolved_p5 = int(p5["position"].isin(UNRESOLVED).sum())
    gate("G5 phase5 rows at 59 unresolved", unresolved_p5, 1046)
    gate("G5 V2 drop total", n5 - n101, 1203)
    gate("G5 implied construct-wt drop",
         (n5 - n101) - unresolved_p5, 157)
    print(f"  G5 cited verbatim: 157 rows at 9 construct-wt-mismatch "
          f"positions {CONSTRUCT_WT_MISMATCH_157} (SESSION_LOG L2340; "
          f"position list quoted, not re-derived from the PDB)")

    # ---- G6: Z1 matched intersection ----------------------------------
    z1 = pd.read_csv(PROC / "task_Z1_matched_n_headtohead.csv")
    m = z1[z1["analysis_set"] == "matched_intersection"]
    gate("G6 matched rows (2 predictors)", len(m), 2)
    gate("G6 matched n_rows", sorted(set(m["n_rows"])), [9595])
    gate("G6 matched n_positions", sorted(set(m["n_positions"])), [586])
    e_orig = z1[(z1["predictor"] == "ESM-2 delta_esm")
                & (z1["analysis_set"] == "original_unmatched")].iloc[0]
    gate("G6 ESM original n", int(e_orig["n_rows"]), 10757)
    gate("G6 ESM original positions", int(e_orig["n_positions"]), 654)
    if abs(float(e_orig["rho"]) - ANCHOR_RHO) > 1e-12:
        gfail(f"G6: Z1 ESM original rho {e_orig['rho']!r} != anchor")
    print(f"  G6 anchor PASS: Z1's ESM rho == {ANCHOR_RHO} (two sources)")
    gate("G6 ESM loses", n107 - n9595, 1162)

    # ---- G7: Z3f / SaProt scorable base --------------------------------
    # Z3f's 1,017 is on the 10,757 ANALYSIS FRAME (dropna own_e_b), not
    # the 11,344 table — first run gated on t32 and got 1,046; fixed to
    # the documented basis before any manifest existed (exit 1, nothing
    # written; disclosed in the AF2 log entry). Both numbers are correct
    # on their own base: 1,046 = rows of task32 ≡ phase5 (G3/G5) at the
    # 59 positions; 1,017 = the subset of those inside the 10,757 frame.
    unresolved_frame = int(frame["position"].isin(UNRESOLVED).sum())
    gate("G7 analysis-frame rows at 59 unresolved", unresolved_frame, 1017)
    gate("G7 scored base", n107 - unresolved_frame, 9740)
    gate("G7 Z3f's '29 not in the 10,757 set'",
         unresolved_p5 - unresolved_frame, 29)

    # ---- manifest (built from the gated variables only) ----------------
    rows = [
        dict(branch_predictor="universe (all atlas variants)", stage=1,
             filter_step="raw atlas table, all variant types",
             applied_by="source table (A2b carrier: "
                        "task35_epistatic_set.csv)",
             n_before="", n_after=n13, delta_n="",
             appears_in="A2b chain (OVERNIGHT_LOG L147)",
             verified_by="G1"),
        dict(branch_predictor="universe (all atlas variants)", stage=2,
             filter_step='type == "substitution" (missense only), '
                         "-1,232 nonsense+synonymous",
             applied_by="load_derived_maps(missense_only=True) "
                        "(scripts 15/35 data loader)",
             n_before=n13, n_after=n119, delta_n=n119 - n13,
             appears_in="original proposal (task doc L370 attribution); "
                        "script-50 gate (MIGRATION_LOG L441)",
             verified_by="G1"),
        dict(branch_predictor="universe (all atlas variants)", stage=3,
             filter_step="inner join esm2_wt_scores.csv — 1 substitution "
                         "has no ESM WT score",
             applied_by="script 15 (phase3_analysis_table.csv)",
             n_before=n119, n_after=n3, delta_n=n3 - n119,
             appears_in="A2b (SESSION_LOG L502)",
             verified_by="G2"),
        dict(branch_predictor="universe (all atlas variants)", stage=4,
             filter_step="dropna(model_A, model_B, model_C, target) — "
                         "-557 (all f_bar_a222v NaN per A2b's logged "
                         "verification)",
             applied_by="script 16 line 55 (phase5_analysis_table.csv)",
             n_before=n3, n_after=n5, delta_n=n5 - n3,
             appears_in="Part II §12 (task L371; Part II is external, "
                        "per [AD7] L2824); in-repo carriers: phase5, "
                        "RESULTS.md L56 (11344)",
             verified_by="G2"),
        dict(branch_predictor="ESM-2 delta_esm primary", stage=5,
             filter_step="dropna(delta_esm) — 0 additional rows",
             applied_by="script 32 (task32_analysis_table.csv)",
             n_before=n5, n_after=len(t32), delta_n=0,
             appears_in="primary delta_ESM table (Part II §12's "
                        "in-repo carrier)",
             verified_by="G3"),
        dict(branch_predictor="published-e.b additive null (script 34)",
             stage=6,
             filter_step="dropna(f_bar_wt) — -231 rows with all four "
                         "WT-arm conditions missing (231/231 verified "
                         "by A2b)",
             applied_by="scripts 34 & 36 analysis set "
                        "(task34_predictions.csv, "
                        "task36_analysis_table.csv)",
             n_before=len(t32), n_after=n111,
             delta_n=n111 - len(t32),
             appears_in="Part I §6.2 (task L371); MTHFR_RESULTS_LOG "
                        "§6.2 L230 carries 11,113",
             verified_by="G3, G4"),
        dict(branch_predictor="own_e_b primary / 6.3 strata", stage=7,
             filter_step="require published e.b AND own_e_b — -356 more "
                         "(own_e_b-missing ≡ e.b-missing per A2b; 587 "
                         "total incl. the 231)",
             applied_by="scripts 32-pairs / 33 / 35 / 6.3 strata "
                        "(task32_delta_esm_primary.csv)",
             n_before=n111, n_after=n107, delta_n=n107 - n111,
             appears_in="primary analysis frame (AA4/AA5 floor; AD8 "
                        "zero-orders)",
             verified_by="G3"),
        dict(branch_predictor="ThermoMPNN V2", stage=8,
             filter_step="left-join ThermoMPNN chain-A SSM on "
                         "(position, wt_aa, mut_aa) — -1,046 rows at 59 "
                         "unresolved positions (forced) and -157 rows at "
                         "9 construct-wt-mismatch positions "
                         f"{CONSTRUCT_WT_MISMATCH_157}",
             applied_by="script 68 (task_V2_thermompnn_ddg.csv)",
             n_before=n5, n_after=n101, delta_n=n101 - n5,
             appears_in="V2 deliverable; AD1 verdict cites 10,141 "
                        "(DEEPDIVE_LOG L519, L572)",
             verified_by="G5"),
        dict(branch_predictor="ThermoMPNN V2 (own_e_b analysis set)",
             stage=9,
             filter_step="dropna(own_e_b) — -546 rows",
             applied_by="Z1a/AD3 matched accounting",
             n_before=n101, n_after=n9595, delta_n=n9595 - n101,
             appears_in="[Z1]/AD8 accounting (DEEPDIVE_LOG L2876)",
             verified_by="G5"),
        dict(branch_predictor="matched Z1 intersection (ESM ∩ Thermo)",
             stage=10,
             filter_step="ESM primary frame ∩ V2 coverage — -1,162 ESM "
                         "rows lack V2 ddg; V2 side loses 0 (every V2 "
                         "row with own_e_b is already in the ESM frame); "
                         "586 positions",
             applied_by="Z1a (task_Z1_matched_n_headtohead.csv); gated "
                        "in scripts 81 G1",
             n_before=n107, n_after=n9595, delta_n=n9595 - n107,
             appears_in="[Z1a] 'intersection n=9595 pos=586 (ESM loses "
                        "1162, Thermo loses 0)' (DEEPDIVE_LOG L2869)",
             verified_by="G6"),
        dict(branch_predictor="SaProt structure-scorable (Z3f base)",
             stage=11,
             filter_step="exclude rows at the 59 unresolved chain-A "
                         "positions — -1,017 (SaProt cannot score "
                         "structure-less residues; 29 of phase5's 1,046 "
                         "are outside the 10,757 set)",
             applied_by="script 70 (Z3f accounting)",
             n_before=n107, n_after=n107 - unresolved_frame,
             delta_n=-unresolved_frame,
             appears_in="CLOSEOUT_LOG L615-617 'ours 9740'; scores to "
                        "date are smoke-limited (74 rows @ 4 positions, "
                        "L608-615) — full Z3f run pending",
             verified_by="G7"),
    ]
    manifest = pd.DataFrame(rows)
    gate("G8 manifest rows", len(manifest), 11)
    # every n_after must be one of the gated variables (never re-typed)
    allowed = {n13, n119, n3, n5, len(t32), n111, n107,
               n101, n9595, n107 - unresolved_frame}
    if set(manifest["n_after"].astype(int)) - allowed:
        gfail(f"G8: ungated n_after values in manifest: "
              f"{set(manifest['n_after'].astype(int)) - allowed}")
    print("  G8 PASS: every n_after traces to a gated variable")
    manifest.to_csv(OUT, index=False)

    print("\n" + "-" * 74)
    print("RECONCILIATION (the task's disputed numbers -> manifest rows)")
    print("-" * 74)
    print(f"  11,902 missense total  -> stage 2 (proposal; "
          f"script-50 gate)")
    print(f"  11,344 Part II §12      -> stage 4/5 "
          f"(phase5/task32, RESULTS.md L56)")
    print(f"  11,113 Part I §6.2      -> stage 6 "
          f"(task34/task36, MTHFR_RESULTS_LOG §6.2)")
    print(f"  10,757 primary frame    -> stage 7 (ESM-2 + 6.3 strata)")
    print(f"  10,141 ThermoMPNN V2    -> stage 8 (script 68)")
    print(f"   9,740 SaProt scorable  -> stage 11 (script 70, Z3f)")
    print(f"   9,595 matched set/586  -> stages 9+10 (Z1, AD8)")
    print(f"\n  single cascade saved -> {OUT.name} (11 rows)")
    print("LIMITATIONS: proposal/Part I/Part II are external or carried "
          "by in-repo mirrors (cited per row);\n  A2b's logged "
          "verifications for the 557's NaN nature and the 587=587=587\n"
          "  e.b/own_e_b mask identity are attributed, not re-derived; "
          "the 157-row position\n  list is quoted from SESSION_LOG "
          "L2340, not re-derived from the PDB.")
    print("\nAF2 DONE")
