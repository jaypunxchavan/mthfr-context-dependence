"""
Task A2 (reliability-and-decompositions): formalize the
reliability/attenuation framing as a proper, GATED result.

PRE-REGISTRATION (written before computing any number below; AGENTS.md
sec 6). Every input below was already on disk in a cited log entry; no
input was chosen after seeing an outcome.

THE FORMULA (task doc A2a)
--------------------------
    r_dis = r_obs / sqrt(rel_delta * rel_own_eb)

(classical attenuation correction: observed correlation divided by the
square root of the product of the two reliabilities).

INPUTS AND THEIR EXACT SOURCE ENTRIES
--------------------------------------
r_obs = -0.08811806424891734
    the frozen headline Spearman(delta_esm, own_e_b), script 32's
    G-anchor value; independently gated at 0.000e+00 in
    OVERNIGHT_LOG ## C3a (L590, "GATE G3 (rho own_e_b): got
    -0.088118064248917 (published -0.088118064248917, |diff| =
    0.000e+00) -> OK"). Recomputed here from
    data/processed/task32_analysis_table.csv as gate G3'.

rel_delta = 0.084365
    AC4's cross-member delta agreement (median of the 10 member-pair
    Spearman correlations on delta scores).
    SOURCE: docs/tasks/closeout-u2-u3-u4-v5/CLOSEOUT_LOG.md entry
    "## [AC4] -- ESM-1v across all five pretrained members ..." at
    L2038, value quoted at L2188: "[AC4] R7 member-pair Spearman on
    delta scores: min=0.003314 median=0.084365 max=0.162631 (10
    pairs)". Recomputed here from the five member CSVs as gate G2'.

rel_own_eb = 0.6363
    own_e_b reliability, computed as 1 - var(synonymous e.b)/var(e.b).
    SOURCE: docs/tasks/review-triage/OVERNIGHT_LOG.md entry
    "## C3a -- Oracle ceiling + correlation disattenuation" at L575,
    value quoted at L594: "reliability, own e.b     : 1 - var(syn
    0.02111, n=570) / var(analysis 0.05804) = 0.6363" (pandas ddof=1
    convention; OVERNIGHT_LOG L651 records the ddof=0 twin 0.6369 --
    "immaterial (every verdict above is identical under both)"). The
    0.6363 value is used as quoted; it is NOT recomputed here (C3a's
    rebuild of synonymous rows is out of scope for this arithmetic --
    cross-referenced, not duplicated).

NUMBERS TO COMPUTE AND REPORT (task doc A2b, expected values from the
doc's own text, printed side by side with the computed values so any
disagreement is visible rather than hidden)
------------------------------------------------------------------------------------------------
1. attenuation ceiling          = sqrt(rel_delta)            (doc: ~0.29)
2. disattenuated anchor, delta only  = r_obs / sqrt(rel_delta)   (doc: ~-0.303)
3. fully disattenuated anchor        = r_obs / sqrt(rel_delta*rel_own_eb) (doc: ~-0.380)
For reconciliation: r_obs / sqrt(rel_own_eb) is C3a's own on-disk
disattenuation (OVERNIGHT_LOG L627+, "r_dis = -0.110413 ..."); it is
printed here only to show the three corrections are mutually
consistent -- it is NOT a new result.

A2c (context, descriptive): where ESM-2's -0.088 sits relative to the
five ESM-1v members' own primary-rho distribution
(task_AC4_esm1v_summary.csv, target=own_e_b): report mean, sd (ddof=1
as primary, ddof=0 also shown), and z = (r_obs - mean)/sd / SD-distance
for both. Label: descriptive context from n=5 draws -- a z computed on
five members is scale context, NOT a p-value or a claim.

GATES (sanity checks -- failure means STOP, not retry; AGENTS.md sec 4)
----------------------------------------------------------------------
G1 provenance: CLOSEOUT_LOG must contain "median=0.084365" AND
    OVERNIGHT_LOG must contain "var(analysis 0.05804) = 0.6363" -- the
    exact quoted substrings from the cited entries. Else exit 1.
G2' delta-agreement re-derivation: median of the 10 pairwise Spearmans
    between members' delta vectors on the joined 10,757-row frame must
    equal 0.084365 within 1e-6. Else exit 1.
G3' headline re-derivation: Spearman(delta_esm, own_e_b) recomputed on
    the frame must equal -0.08811806424891734 within 1e-12. Else exit 1.

LIMITATIONS -- printed alongside every disattenuated number (task doc
A2b, AGENTS.md sec 6). Every time a disattenuated value is quoted:
- PROXY ASSUMPTION: rel_delta = 0.084365 is ESM-1v's cross-SEED delta
  agreement borrowed as a proxy for ESM-2's own delta reliability.
  ESM-2 has no seed replicates (one checkpoint per size), so its own
  reliability is UNMEASURABLE. This is an assumption, not a
  measurement. (Scope correction per task A3.)
- The classical correction assumes independent measurement errors and
  essentially parallel/tau-equivalent measures; neither is tested here.
- rel_own_eb comes from a synonymous-vs-analysis variance ratio with
  n=570 synonymous rows (C3a).
- Disattenuated values are ATTENUATION CONTEXT, not model performance
  numbers; nothing here is a significance test (no bootstrap/permutation
  by design -- these are point identities).

Run: venv/bin/python3 scripts/91_a2_disattenuation.py
(no stochastic draws exist in this script, so there is no N to reduce)
Output: data/processed/task91_a2_disattenuation.csv
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.stats import _spearman

REPO = Path(__file__).resolve().parents[1]
PROC = REPO / "data" / "processed"
DOCS = REPO / "docs" / "tasks"
CLOSEOUT = DOCS / "closeout-u2-u3-u4-v5" / "CLOSEOUT_LOG.md"
OVERNIGHT = DOCS / "review-triage" / "OVERNIGHT_LOG.md"
T32 = PROC / "task32_analysis_table.csv"
SUMMARY = PROC / "task_AC4_esm1v_summary.csv"
MEMBERS = [PROC / f"task_AC4_esm1v_member{k}_scores.csv" for k in range(1, 6)]

# pre-registered constants (values as quoted in the cited log entries)
R_OBS = -0.08811806424891734
REL_DELTA = 0.084365
REL_OWN_EB = 0.6363
DOC_CEILING = 0.29       # doc A2b expected
DOC_DELTA_ONLY = -0.303  # doc A2b expected
DOC_FULL = -0.380        # doc A2b expected


def log(msg=""):
    print(msg, flush=True)


def main():
    log("A2 -- RELIABILITY/ATTENUATION FORMALIZATION (scripts/91)")
    log(f"formula: r_dis = r_obs / sqrt(rel_delta * rel_own_eb)  "
        f"[pre-registered in docstring]")
    log(f"inputs: r_obs={R_OBS} (script 32 G-anchor), "
        f"rel_delta={REL_DELTA} (CLOSEOUT_LOG [AC4] L2188), "
        f"rel_own_eb={REL_OWN_EB} (OVERNIGHT_LOG ## C3a L594)")

    # ---- G1 provenance gate ----
    t_close = CLOSEOUT.read_text()
    t_over = OVERNIGHT.read_text()
    g1a = "median=0.084365" in t_close
    g1b = "var(analysis 0.05804) = 0.6363" in t_over
    log(f"G1 provenance: CLOSEOUT_LOG contains 'median=0.084365': {g1a}; "
        f"OVERNIGHT_LOG contains 'var(analysis 0.05804) = 0.6363': {g1b}")
    if not (g1a and g1b):
        log("G1 FAIL -- cited source text not found where cited. STOP.")
        sys.exit(1)

    # ---- G3' headline re-derivation ----
    t32 = pd.read_csv(T32)
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"]).copy()
    r_got = float(_spearman(base["delta_esm"].to_numpy(),
                            base["own_e_b"].to_numpy()))
    d3 = abs(r_got - R_OBS)
    log(f"G3' headline re-derivation: rho(delta_esm, own_e_b) = {r_got:.15f} "
        f"(expected {R_OBS:.15f}, |diff| = {d3:.3e}) "
        f"-> {'OK' if d3 < 1e-12 else 'FAIL -- STOP'}")
    if d3 >= 1e-12:
        sys.exit(1)

    # ---- G2' delta-agreement re-derivation ----
    deltas = []
    for k, p in enumerate(MEMBERS, start=1):
        m = pd.read_csv(p)
        j = base.merge(m[["position", "mut_aa", "delta"]],
                       on=["position", "mut_aa"], how="left", validate="1:1")
        if j["delta"].isna().any():
            log(f"G2' member {k}: unmatched rows -- FAIL. STOP.")
            sys.exit(1)
        deltas.append(j["delta"].to_numpy())
    pair_rhos = []
    for a in range(5):
        for b in range(a + 1, 5):
            pair_rhos.append(float(_spearman(deltas[a], deltas[b])))
    med = float(np.median(pair_rhos))
    d2 = abs(med - REL_DELTA)
    log(f"G2' delta-agreement re-derivation: median of {len(pair_rhos)} "
        f"pairwise rhos = {med:.6f} (expected {REL_DELTA}, "
        f"|diff| = {d2:.3e}) -> {'OK' if d2 < 1e-6 else 'FAIL -- STOP'}")
    if d2 >= 1e-6:
        sys.exit(1)

    # ---- the three pre-registered numbers ----
    ceiling = float(np.sqrt(REL_DELTA))
    delta_only = R_OBS / ceiling
    full = R_OBS / float(np.sqrt(REL_DELTA * REL_OWN_EB))
    own_only = R_OBS / float(np.sqrt(REL_OWN_EB))  # C3a's on-disk figure

    PROXY = ("PROXY ASSUMPTION (state with every quote): rel_delta is "
             "ESM-1v's cross-SEED agreement borrowed for ESM-2, whose own "
             "delta reliability is unmeasurable (no seed replicates) -- "
             "assumption, not measurement.")
    log("\nA2b RESULTS (computed | doc's expected value):")
    log(f"  1. attenuation ceiling sqrt(rel_delta)          = {ceiling:+.6f}"
        f"  | doc: {DOC_CEILING}")
    log(f"  2. delta-only disattenuated anchor              = {delta_only:+.6f}"
        f"  | doc: {DOC_DELTA_ONLY}")
    log(f"     [{PROXY}]")
    log(f"  3. fully disattenuated anchor (both reliab.)    = {full:+.6f}"
        f"  | doc: {DOC_FULL}")
    log(f"     [{PROXY}]")
    log(f"  reconciliation: r_obs/sqrt(rel_own_eb)          = {own_only:+.6f}"
        f"  (= C3a's on-disk -0.110413; own_e_b-only correction, not new)")

    # ---- A2c: -0.088 vs the five-member distribution ----
    summ = pd.read_csv(SUMMARY)
    prim = summ[summ["target"] == "primary"].sort_values("member")
    rhos = prim["observed_rho"].to_numpy()
    mean5 = float(rhos.mean())
    sd1 = float(rhos.std(ddof=1))   # primary
    sd0 = float(rhos.std(ddof=0))   # shown for transparency
    z1 = (R_OBS - mean5) / sd1
    z0 = (R_OBS - mean5) / sd0
    log("\nA2c CONTEXT: ESM-2's -0.088 vs the five ESM-1v members' own "
        "distribution (descriptive, n=5 -- scale context, not a p-value):")
    log(f"  five member rhos: {', '.join(f'{r:+.6f}' for r in rhos)}")
    log(f"  mean = {mean5:+.6f};  sd(ddof=1) = {sd1:.6f};  "
        f"sd(ddof=0) = {sd0:.6f}")
    log(f"  z = (r_obs - mean)/sd : ddof=1 -> {z1:+.2f} SD;  "
        f"ddof=0 -> {z0:+.2f} SD")
    log(f"  plain statement: ESM-2's {R_OBS:+.6f} sits "
        f"{abs(z1):.2f} sample-SDs BELOW the five-member mean "
        f"({mean5:+.6f})")

    # ---- save ----
    out = PROC / "task91_a2_disattenuation.csv"
    rows = [
        {"stat": "r_obs_frozen_headline", "value": R_OBS, "doc_expected": ""},
        {"stat": "rel_delta_source_AC4", "value": REL_DELTA,
         "doc_expected": "0.084"},
        {"stat": "rel_own_eb_source_C3a", "value": REL_OWN_EB,
         "doc_expected": "0.6363"},
        {"stat": "attenuation_ceiling_sqrt_rel_delta", "value": ceiling,
         "doc_expected": DOC_CEILING},
        {"stat": "disattenuated_delta_only", "value": delta_only,
         "doc_expected": DOC_DELTA_ONLY},
        {"stat": "disattenuated_full_both", "value": full,
         "doc_expected": DOC_FULL},
        {"stat": "reconcile_own_eb_only_C3a", "value": own_only,
         "doc_expected": -0.110413},
        {"stat": "five_member_mean_rho", "value": mean5, "doc_expected": ""},
        {"stat": "five_member_sd_ddof1", "value": sd1, "doc_expected": ""},
        {"stat": "five_member_sd_ddof0", "value": sd0, "doc_expected": ""},
        {"stat": "z_ddof1", "value": z1, "doc_expected": ""},
        {"stat": "z_ddof0", "value": z0, "doc_expected": ""},
    ]
    pd.DataFrame(rows).to_csv(out, index=False)
    log(f"[saved] {out}")
    log("\nLIMITATIONS (repeat with every quote of a disattenuated value):")
    log(f"  - {PROXY}")
    log("  - classical correction assumes independent errors and "
        "parallel measures -- neither tested here.")
    log("  - disattenuated values are attenuation CONTEXT, not model "
        "performance; no significance claim (point identities only).")
    log("A2 DONE")


if __name__ == "__main__":
    main()
