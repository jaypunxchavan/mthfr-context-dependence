"""Script 163 (Phase 3a session 3a, task A5c) -- build the RBD targets
e_T^bind and e_T^expr for T in {N501Y, E484K} exactly as the frozen block
requires, with the barcode-count filter, its two sensitivities and the
per-library reliability of e_T.  No torch, no esm, no network.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Task A5c under the frozen
prereg/RBD_REPLICATION_PREREG_v1.md sections 2, 3 and 6(f), quoted
verbatim:

  (2) "Phenotype PRIMARY: ACE2 binding (the per-mutation effect on log10 KD
      as the authors define it).  SECONDARY: expression.  A mutation is
      usable for a target T only if it is measured in both T and
      Wuhan-Hu-1 with barcode count n_bc >= 3 in each (sensitivities
      n_bc >= 1 and >= 5, reported, none selected).  Target site excluded
      from the variant set for everyone."
  (3) "e_T(v) = x_T(v) - x_Wuhan(v) for T in {N501Y, E484K}, over single
      substitutions v at sites other than T's site."
  (6f)"Measurement reliability of e_T: correlation between per-library
      estimates if per-library columns exist."

COLUMN SEMANTICS, VERIFIED BEFORE WRITING THIS SCRIPT (AGENTS 5: verify
against a labeled example, never by assumption).  The verification is
re-run inside this script as gates G-163-1..4, so the script fails rather
than silently using a misread column:

  G-163-1  `bind` is the NaN-ignored mean of `bind_rep1..3`, and `expr`
           the NaN-ignored mean of `expr_rep1..2` (agreement to <= 1e-5,
           the table's 5-decimal rounding).
  G-163-2  `delta_bind` is the authors' own per-library construction:
           mean over libraries of (rep - that target's wild-type row's
           rep).  Agreement to <= 1e-5.  It is NOT `bind - WT_bind`: those
           differ by up to ~0.14 log10 KD on rows missing some library,
           because the two averages run over different library sets.
  G-163-3  every wild-type row has delta_bind = delta_expr = 0 exactly.
  G-163-4  the per-library columns map to the barcode table's libraries as
           bind_rep1=pool1A, bind_rep2=pool2A, bind_rep3=pool1B (and
           expr_rep1/2 to pool1/pool2), checked by recomputing each
           (library, target) wild-type mean log10Ka from bc_binding.csv /
           bc_expression.csv and matching it to the wild-type row's
           per-library value (<= 1e-5).

DECISIONS (pre-registered here, before the first run):

  C1  x_T is the authors' own per-mutation effect column -- `delta_bind`
      for the primary phenotype, `delta_expr` for the secondary -- so
      e_T(v) = delta_T(v) - delta_Wuhan(v).  This is what "the
      per-mutation effect ... as the authors define it" names, and G-163-2
      pins that definition to code-level arithmetic.  The alternative
      construction (bind_T - bind_W) minus its own wild-type offset is
      computed and printed ONLY as a disclosed difference, never used.
  C2  Variant set: rows with mutant != wildtype (the wild-type rows are
      not mutations) at sites other than T's own site -- site 501 for
      T=N501Y, site 484 for T=E484K -- per frozen 3.  The other target's
      site stays in: frozen 3 excludes only T's site from e_T (it is
      excluded later, per background, in rho_b).  Rows dropped by this
      rule are counted and printed (account for every dropped row).
  C3  Usability masks, computed for BOTH phenotypes at all three
      thresholds and reported side by side: measured in both backgrounds
      (the effect column is non-NaN in T and in Wuhan-Hu-1 -- which is
      exactly n_bc > 0 in that background) AND n_bc >= thr in each.
      thr = 3 is the frozen primary; thr = 1 and thr = 5 are the frozen
      sensitivities, "reported, none selected".  No threshold is chosen
      from a result here.
  C4  Reliability (frozen 6f): for each library L that exists on both
      sides, build e_T^L(v) = [rep_L(T, v) - rep_L(T, WT)] - [rep_L(W, v)
      - rep_L(W, WT)] and report every pairwise Pearson and Spearman
      correlation between the per-library estimates over the variants
      where BOTH members of the pair are non-NaN (n printed).  This is
      descriptive; it gates nothing and changes no mask.
  C5  Output: data/processed/phase3/rbd/e_T.csv -- one row per (T, variant)
      passing C2, with the effect columns, the three masks per phenotype,
      n_bc in each background, and the site/label columns A5d needs.  Its
      sha256 is printed.  Nothing is written outside that file.

GATES: G-163-1..4 above (column semantics; a failure exits 3 -- it means
the columns are not what this script assumes), plus internal consistency
G-163-5 the (position, mutant) variant sets of T and Wuhan-Hu-1 are
identical before masking, G-163-6 mask nesting ge5 subset of ge3 subset
of ge1 for both phenotypes, G-163-7 no NaN inside any mask, G-163-8 both
targets retain a non-empty primary (thr=3) variant set for both
phenotypes.  These are implementation checks, not the frozen G-R gates;
the frozen G-R3/G-R4/G-R5 belong to scripts 157/156 and are not claimed
here.

POST-HOC AMENDMENT (added after run 1 exited 3; disclosed per AGENTS 0
and 6 -- the pre-registered text above is left exactly as written):

  Run 1 of this script failed G-163-2 against the pre-registered
  TOL = 1e-5: measured max|delta - mean_over_libs(rep - own_WT_rep)| =
  1.0000000001411657e-05, i.e. 1.41e-15 above the threshold in absolute
  terms (relative excess 1.4e-10), with 499 of 23,638 rows over 1e-5,
  99.99th percentile
  1.000000000137759e-05, median 3.33e-06 (worst row: E484K, delta_expr,
  position 524, mutant G: stored -0.10229 vs recomputed
  -0.1022799999999986).  Cause, established from the storage format
  rather than assumed: the table stores 5 decimals, so recomputing the
  identity from rounded `rep` and rounded `WT_rep` values (differencing
  two 5-decimal numbers: up to 1e-5) and comparing with the rounded
  `delta` column (its own rounding: up to 5e-6) can only agree to about
  1.5e-5.  The pre-registered threshold sat at exactly that scale.  The
  other three semantics gates passed on the same run (G-163-1 6.67e-06,
  G-163-3 exactly 0, G-163-4 4.58e-06).

  DECISION (made only after seeing run 1, therefore POST-HOC, and
  disclosed here, in the script's printed output and in the build log):
  G-163-2 is additionally checked against TOL_ROUND = 1.5e-5, a bound
  derived analytically from the table's 5-decimal storage and NOT fitted
  to the observed value (observed 1.0000000001e-5; any deviation above
  1.5e-5 still fails).  The pre-registered TOL = 1e-5 is left untouched
  and its verdict is still printed on every run -- it reads FAIL.  No
  other threshold, no frozen prereg gate and no decision rule changes.
  Consequently: A5c's PASS rests on a post-hoc tolerance for one
  internal semantics check, and the summary block says so in as many
  words.  Run 1's output is preserved as PHASE3_A5c_RUN1_FAIL_OUTPUT.txt.

Usage:
  venv/bin/python3 scripts/163_rbd_targets.py

LIMITATIONS (AGENTS section 6, printed by the script itself): no test
statistic, no p-value and no outcome word of any frozen block is computed
here -- this script builds data and reports counts and reliabilities only;
the two targets are two looks with no multiplicity adjustment (frozen 5),
stated here as a standing fact; per-library reliability uses the same
library on both sides of e_T and is descriptive, not an error model;
barcodes are the unit of n_bc, and a variant's barcode count says nothing
about independence of positions (the position-cluster machinery in A5g
handles that).
"""

import hashlib
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "external" / "rbd_starr2022"
OUT_DIR = ROOT / "data" / "processed" / "phase3" / "rbd"
OUT_CSV = OUT_DIR / "e_T.csv"

SCORES = EXT / "final_variant_scores.csv"
BC_BIND = EXT / "bc_binding.csv"
BC_EXPR = EXT / "bc_expression.csv"

WUHAN = "Wuhan-Hu-1"
TARGETS = {"N501Y": 501, "E484K": 484}      # T -> T's own site (frozen 3)
PHENOS = {"bind": ("delta_bind", "n_bc_bind", ["bind_rep1", "bind_rep2",
                                               "bind_rep3"], "binding"),
          "expr": ("delta_expr", "n_bc_expr", ["expr_rep1", "expr_rep2"],
                   "expression")}
REP_LIB = {"bind_rep1": "pool1A", "bind_rep2": "pool2A",
           "bind_rep3": "pool1B", "expr_rep1": "pool1", "expr_rep2": "pool2"}
THRESHOLDS = (1, 3, 5)                       # frozen 2: 3 primary, 1/5 sens
TOL = 1e-5             # pre-registered (docstring above) -- NOT changed
TOL_ROUND = 1.5e-5     # POST-HOC AMENDMENT: 1e-5 (differencing two
                       # 5-decimal values) + 5e-6 (delta's own rounding),
                       # derived from the storage format, see docstring

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}")


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def main():
    t0 = time.time()
    print("PHASE 3a Task A5c -- RBD targets e_T^bind / e_T^expr "
          "(frozen RBD_REPLICATION_PREREG_v1.md sections 2, 3, 6f)")
    print("No torch/esm. Primary threshold n_bc >= 3 in BOTH backgrounds; "
          "1 and 5 reported as sensitivities, none selected.")

    d = pd.read_csv(SCORES)
    rule("COLUMN SEMANTICS GATES (verify before use; AGENTS 5)")

    # G-163-1: aggregate == mean of per-library columns
    worst = 0.0
    for phen, (eff, _, reps, _) in PHENOS.items():
        base = "bind" if phen == "bind" else "expr"
        m = d[reps].mean(axis=1, skipna=True)
        worst = max(worst, float(np.nanmax(np.abs(m - d[base]))))
    gate("G-163-1 bind/expr are the NaN-mean of the per-library columns",
         "PASS" if worst <= TOL else "FAIL",
         f"max|diff| = {worst:.2e} over {len(d):,} rows",
         f"tolerance {TOL} (5-decimal table rounding)")

    # G-163-2 / 3: delta == mean over libs of (rep - own WT rep); WT rows 0
    worst_d, worst_wt = 0.0, 0.0
    for t_lab in [WUHAN] + list(TARGETS):
        sub = d[d["target"] == t_lab]
        wrow = sub[sub["mutant"] == sub["wildtype"]]
        for eff, _, reps, _ in PHENOS.values():
            per = pd.DataFrame({c: sub[c] - sub.loc[sub["mutant"] == sub[
                "wildtype"], c].iloc[0] for c in reps})
            worst_d = max(worst_d, float(np.nanmax(np.abs(
                per.mean(axis=1, skipna=True) - sub[eff]))))
            worst_wt = max(worst_wt, float(np.nanmax(np.abs(wrow[eff]))))
    gate("G-163-2 (as pre-registered, tol 1e-5) delta == mean over "
         "libraries of (rep - own wild-type rep)",
         "PASS" if worst_d <= TOL else "FAIL",
         f"max|diff| = {worst_d:.17g}  (threshold {TOL:.0e}; excess "
         f"{max(0.0, worst_d - TOL):.3g} = {max(0.0, (worst_d - TOL) / TOL):.1e} "
         f"relative)", "the authors' own construction")
    gate("G-163-2 (POST-HOC disclosed bound, tol 1.5e-5 from 5-decimal "
         "storage) delta == mean over libraries of (rep - own WT rep)",
         "PASS" if worst_d <= TOL_ROUND else "FAIL",
         f"max|diff| = {worst_d:.17g}  (bound {TOL_ROUND:.1e}; headroom "
         f"{TOL_ROUND - worst_d:.3g})",
         "post-hoc tolerance chosen AFTER run 1 failed; disclosed per "
         "AGENTS 0/6 -- A5c's PASS depends on it")
    gate("G-163-3 every wild-type row has delta = 0 exactly",
         "PASS" if worst_wt == 0.0 else "FAIL",
         f"max|delta| over 1,005 wild-type rows = {worst_wt:.2e}", "")

    # G-163-4: rep columns <-> library names, via the barcode tables
    checks = []
    for bc_path, eff_base, reps in [(BC_BIND, "log10Ka",
                                     ["bind_rep1", "bind_rep2", "bind_rep3"]),
                                    (BC_EXPR, "expression",
                                     ["expr_rep1", "expr_rep2"])]:
        bc = pd.read_csv(bc_path)
        name_map = {"Wuhan-Hu-1": "Wuhan_Hu_1", "Beta": "B1351"}
        wt = bc[bc["variant_class"] == "wildtype"]
        agg = wt.groupby(["library", "target"])[eff_base].mean()
        for t_lab in [WUHAN] + list(TARGETS):
            key = name_map.get(t_lab, t_lab)
            wrow = d[(d["target"] == t_lab) & (d["mutant"] == d["wildtype"])]
            if wrow.empty:
                continue
            wrow = wrow.iloc[0]
            for c in reps:
                lib = REP_LIB[c]
                if (lib, key) not in agg.index:
                    continue
                checks.append(abs(float(agg.loc[(lib, key)]) - float(wrow[c])))
    worst_lib = max(checks) if checks else float("nan")
    n_lib_checks = len(checks)
    gate("G-163-4 per-library columns map to libraries (WT barcode means)",
         "PASS" if worst_lib <= TOL else "FAIL",
         f"max|diff| = {worst_lib:.2e} over {n_lib_checks} (library,target) "
         f"cells", f"rep1=pool1A, rep2=pool2A, rep3=pool1B; tol {TOL}")
    if not (worst <= TOL and worst_d <= TOL_ROUND and worst_wt == 0.0
            and worst_lib <= TOL):
        print("\nGATE FAILED: column semantics differ from what this script "
              "assumes; stopping before anything is built.")
        sys.exit(3)

    # ---- build e_T -------------------------------------------------------
    rule("BUILD e_T (frozen 3): e_T(v) = delta_T(v) - delta_Wuhan(v), "
         "single substitutions, sites other than T's own site")
    frames = []
    alt_stats = []
    for t_lab, t_site in TARGETS.items():
        T = d[(d["target"] == t_lab) & (d["mutant"] != d["wildtype"])
              & (d["position"] != t_site)]
        W = d[(d["target"] == WUHAN) & (d["mutant"] != d["wildtype"])
              & (d["position"] != t_site)]
        n_all = int(((d["target"] == t_lab) & (d["mutant"] != d["wildtype"])
                     & (d["position"] != t_site)).sum())
        dropped = int(((d["target"] == t_lab)
                       & (d["mutant"] != d["wildtype"])
                       & (d["position"] == t_site)).sum())
        print(f"\n  T = {t_lab} (own site {t_site} excluded): "
              f"{n_all:,} candidate rows; {dropped} rows dropped at the "
              f"target site (19 mutants x 1 site); wild-type rows "
              f"excluded by construction")
        key = ["position", "mutant"]
        if set(map(tuple, T[key].values)) != set(map(tuple, W[key].values)):
            gate(f"G-163-5 variant sets identical for {t_lab} and "
                 f"{WUHAN}", "FAIL", "set mismatch", "")
            sys.exit(3)
        gate(f"G-163-5 variant sets identical for {t_lab} and {WUHAN}",
             "PASS", f"{len(T):,} candidates each, same (position, mutant) "
             f"set", "checked before any merge")
        m = T.merge(W, on=key, suffixes=("_T", "_W"), validate="one_to_one")
        assert len(m) == n_all, (len(m), n_all)
        out = pd.DataFrame({
            "target": t_lab,
            "position": m["position"],
            "mutant": m["mutant"],
            "wildtype": m["wildtype_T"],
            "mutation": m["mutation_T"],
        })
        for phen, (eff, nbc, reps, _) in PHENOS.items():
            out[f"e_{phen}"] = m[f"{eff}_T"] - m[f"{eff}_W"]
            out[f"{nbc}_T"] = m[f"{nbc}_T"]
            out[f"{nbc}_W"] = m[f"{nbc}_W"]
            meas = m[f"{eff}_T"].notna() & m[f"{eff}_W"].notna()
            out[f"meas_{phen}"] = meas
            for thr in THRESHOLDS:
                out[f"use_{phen}_ge{thr}"] = (meas
                                              & (m[f"{nbc}_T"] >= thr)
                                              & (m[f"{nbc}_W"] >= thr))
            # disclosed alternative construction (never used): e_T from
            # raw `bind` means minus the ALL-LIBRARY wild-type offset of
            # each side.  Accumulate stats so the printed claim is
            # measured, not asserted (an earlier version of this line
            # claimed the two agree wherever the library sets match;
            # that was wrong and was corrected after checking).
            if phen == "bind":
                wtT = d[(d["target"] == t_lab)
                        & (d["mutant"] == d["wildtype"])]["bind"].iloc[0]
                wtW = d[(d["target"] == WUHAN)
                        & (d["mutant"] == d["wildtype"])]["bind"].iloc[0]
                alt = (m["bind_T"] - wtT) - (m["bind_W"] - wtW)
                c1 = m["delta_bind_T"] - m["delta_bind_W"]
                dd = (alt - c1).abs()
                full = (m[[c + "_T" for c in reps]].notna().all(axis=1)
                        & m[[c + "_W" for c in reps]].notna().all(axis=1))
                defined = alt.notna() & c1.notna()
                alt_stats.append({
                    "target": t_lab,
                    "n": int(defined.sum()),
                    "n_gt": int((dd[defined] > 1e-4).sum()),
                    "max": float(dd[defined].max()),
                    "median": float(dd[defined].median()),
                    "n_full": int((defined & full).sum()),
                    "max_full": (float(dd[defined & full].max())
                                 if bool((defined & full).any())
                                 else float("nan")),
                })
        frames.append(out)
        # per-target counts table
        print(f"  retained (rows with e_bind and e_expr computed): "
              f"{len(out):,}")
        for phen, (_, nbc, _, label) in PHENOS.items():
            for thr in THRESHOLDS:
                n = int(out[f"use_{phen}_ge{thr}"].sum())
                print(f"    {label:<9} n_bc >= {thr} in both : {n:>6,} "
                      f"({n / len(out):.1%})")

    e = pd.concat(frames, ignore_index=True)
    print(f"\n  e_T table: {len(e):,} rows "
          f"({', '.join(f'{t}: {(e.target == t).sum():,}' for t in TARGETS)})")

    # ---- gates on the built table ---------------------------------------
    rule("INTERNAL GATES ON THE BUILT TABLE (implementation checks)")
    nest_ok = True
    for p in PHENOS:
        nest_ok &= bool((~e[f"use_{p}_ge5"] | e[f"use_{p}_ge3"]).all())
        nest_ok &= bool((~e[f"use_{p}_ge3"] | e[f"use_{p}_ge1"]).all())
    gate("G-163-6 mask nesting ge5 subset ge3 subset ge1",
         "PASS" if nest_ok else "FAIL",
         f"holds for both phenotypes: {nest_ok}", "")
    nan_in = 0
    for p in PHENOS:
        nan_in += int(e.loc[e[f"use_{p}_ge3"], f"e_{p}"].isna().sum())
    gate("G-163-7 no NaN inside any primary mask", "PASS" if nan_in == 0
         else "FAIL", f"NaN inside masks = {nan_in}", "")
    n_ok = all(int(((e["target"] == t) & e[f"use_{p}_ge3"]).sum()) > 0
               for p in PHENOS for t in TARGETS)
    gate("G-163-8 both targets retain a non-empty n_bc >= 3 set "
         "(both phenotypes)", "PASS" if n_ok else "FAIL",
         "; ".join(f"{p}: " + ", ".join(
             f"{t}={int(((e['target'] == t) & e[f'use_{p}_ge3']).sum())}"
             for t in TARGETS) for p in PHENOS), "")
    if not (nest_ok and nan_in == 0 and n_ok):
        sys.exit(3)

    # disclosed difference between the two constructions (bind only)
    if alt_stats:
        tot = sum(s["n"] for s in alt_stats)
        tot_gt = sum(s["n_gt"] for s in alt_stats)
        print("\n  DISCLOSED (never used): the alternative e_T built from "
              "raw `bind` means minus the")
        print("  ALL-LIBRARY wild-type offset differs from C1 (the "
              "authors' same-library construction) for any")
        print("  row missing a library, because it pairs a partial-"
              "library variant value with a full-library")
        print("  wild-type value.  Per target:")
        for s in alt_stats:
            print(f"    {s['target']}: {s['n']:,} rows defined; "
                  f"|diff| max {s['max']:.4f}, median {s['median']:.5f} "
                  f"log10 KD; {s['n_gt']:,} rows differ by > 1e-4; "
                  f"{s['n_full']:,} rows measured in all "
                  f"{len(PHENOS['bind'][2])} libraries on both sides, "
                  f"max diff there {s['max_full']:.2e} (storage rounding)")
        print(f"    totals: {tot:,} rows defined, {tot_gt:,} differ by "
              f"> 1e-4 ({tot_gt / tot:.1%}).  C1 is what the frozen block "
              f"uses; this alternative is never used, and no mask, count "
              f"or result in this run depends on it.")

    # ---- asymmetry accounting (every dropped row accounted for) ---------
    rule("ROW ACCOUNTING (AGENTS 5: account for every dropped row)")
    for phen, (eff, nbc, _, label) in PHENOS.items():
        for t_lab in TARGETS:
            T = d[(d["target"] == t_lab) & (d["mutant"] != d["wildtype"])
                  & (d["position"] != TARGETS[t_lab])]
            W = d[(d["target"] == WUHAN) & (d["mutant"] != d["wildtype"])
                  & (d["position"] != TARGETS[t_lab])]
            nT, nW = T[eff].notna().sum(), W[eff].notna().sum()
            nboth = (T[eff].notna().to_numpy()
                     & W[eff].notna().to_numpy()).sum()
            print(f"  {label:<9} {t_lab}: measured in T {nT:,}, in "
                  f"{WUHAN} {nW:,}, in both {int(nboth):,} of "
                  f"{len(T):,} candidates; "
                  f"only-T {int(nT - nboth):,}, only-W {int(nW - nboth):,}")

    # ---- reliability (frozen 6f) ----------------------------------------
    rule("PER-LIBRARY RELIABILITY OF e_T (frozen 6f) -- descriptive, "
         "never gated, never changes a mask")
    rel_rows = []
    for t_lab in TARGETS:
        T = d[(d["target"] == t_lab) & (d["mutant"] != d["wildtype"])
              & (d["position"] != TARGETS[t_lab])]
        W = d[(d["target"] == WUHAN) & (d["mutant"] != d["wildtype"])
              & (d["position"] != TARGETS[t_lab])]
        for phen, (eff, _, reps, label) in PHENOS.items():
            # wild-type rows are excluded from T and W by construction, so
            # take each side's per-library wild-type reference from the
            # full table
            wT = d[(d["target"] == t_lab) & (d["mutant"] == d["wildtype"])]
            wW = d[(d["target"] == WUHAN) & (d["mutant"] == d["wildtype"])]
            # align T and W on (position, mutant) before subtracting:
            # subtracting the two raw frames aligns on their (disjoint)
            # row indexes and yields all-NaN -- that is precisely what
            # run 3 did (PHASE3_A5c_RUN3_REL_ZERO_OUTPUT.txt, all n=0)
            sub = (T[["position", "mutant"] + reps]
                   .merge(W[["position", "mutant"] + reps],
                          on=["position", "mutant"], suffixes=("_T", "_W"),
                          validate="one_to_one"))
            ests = {}
            for c in reps:
                ests[c] = ((sub[f"{c}_T"] - wT[c].iloc[0])
                           - (sub[f"{c}_W"] - wW[c].iloc[0]))
            print(f"\n  T = {t_lab}, {label} phenotype "
                  f"({len(reps)} libraries: "
                  f"{', '.join(f'{c}->{REP_LIB[c]}' for c in reps)}; "
                  f"{len(sub):,} candidate variants):")
            names = list(ests)
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = ests[names[i]], ests[names[j]]
                    both = a.notna() & b.notna()
                    n = int(both.sum())
                    if n < 3:
                        r_p = r_s = float("nan")
                        pnote = "not estimable (n < 3)"
                    else:
                        r_p = float(np.corrcoef(a[both], b[both])[0, 1])
                        r_s = float(pd.Series(a[both]).corr(
                            pd.Series(b[both]), method="spearman"))
                        pnote = ""
                    rel_rows.append({"target": t_lab, "phenotype": phen,
                                     "lib_a": REP_LIB[names[i]],
                                     "lib_b": REP_LIB[names[j]],
                                     "n": n, "pearson": r_p,
                                     "spearman": r_s})
                    print(f"    {REP_LIB[names[i]]:>7} vs "
                          f"{REP_LIB[names[j]]:<7} n={n:>5}  "
                          f"Pearson {r_p:+.4f}  Spearman {r_s:+.4f}  "
                          f"{pnote}")
    rel = pd.DataFrame(rel_rows)
    n_zero = int((rel["n"] == 0).sum())
    print("\n  reliability summary (all pairs, no selection):")
    print(rel.groupby(["target", "phenotype"])[["pearson", "spearman"]]
             .agg(["min", "max", "mean"])
             .to_string(float_format=lambda x: f"{x:+.4f}"))
    print(f"  pairs with n = 0 (would indicate a construction bug): "
          f"{n_zero} of {len(rel)}")
    if n_zero:
        print("  WARNING: reliability pairs with n=0 -- reported as a "
              "defect, not as a result (C4 gates nothing, so this does "
              "not change the exit code; see the build log)")

    # ---- write ----------------------------------------------------------
    rule("OUTPUT")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["target", "position", "mutant", "wildtype", "mutation",
            "e_bind", "e_expr", "n_bc_bind_T", "n_bc_bind_W",
            "n_bc_expr_T", "n_bc_expr_W", "meas_bind", "meas_expr"]
    cols += [f"use_{p}_ge{t}" for p in ("bind", "expr") for t in THRESHOLDS]
    e[cols].to_csv(OUT_CSV, index=False)
    sha = hashlib.sha256(OUT_CSV.read_bytes()).hexdigest()
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}: {len(e):,} rows x "
          f"{len(cols)} cols, sha256 {sha}")

    # ---- summary --------------------------------------------------------
    rule("SUMMARY -- A5c")
    n_pass = 0
    for name, verdict, value, note in GATES:
        print(f"  [{verdict}] {name}: {value}  {note}")
        n_pass += verdict == "PASS"
    # the pre-registered 1e-5 verdict is reported but no longer decides:
    # see the POST-HOC AMENDMENT in the docstring.
    deciding = [g for g in GATES
                if not g[0].startswith("G-163-2 (as pre-registered")]
    ok = all(v == "PASS" for _, v, _, _ in deciding)
    n_dec_pass = sum(v == "PASS" for _, v, _, _ in deciding)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS overall; "
          f"{n_dec_pass}/{len(deciding)} PASS among the deciding checks "
          f"(the pre-registered 1e-5 verdict is reported, not deciding)")
    print(f"  -> {'A5c PASSES' if ok else 'A5c FAILS'}")
    print("\n  LIMITATIONS (AGENTS 6):")
    print("    * POST-HOC: this run passes the G-163-2 semantics check only "
          "under the disclosed")
    print("      1.5e-5 storage-rounding bound added after run 1 failed at "
          "the pre-registered 1e-5")
    print("      (that verdict still prints above as FAIL); no frozen "
          "prereg gate was touched, and")
    print("      A5c's PASS rests on that post-hoc tolerance.")
    print("    * no test, no p-value and no outcome word of any frozen "
          "block is computed here;")
    print("      this script builds data and reports counts and "
          "reliabilities.")
    print("    * two targets are two looks with no multiplicity "
          "adjustment (frozen 5) -- stated,")
    print("      not tested here.")
    print("    * reliability pairs use the same library on both sides of "
          "e_T and are descriptive;")
    print("      they are not an error model and gate nothing.")
    print("    * n_bc counts barcodes, not independent positions; the "
          "position-cluster machinery")
    print("      of the analysis (A5g) is what handles that.")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
