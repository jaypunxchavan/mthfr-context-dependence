"""Script 162 (Phase 3a session 3a, task A5b) -- RBD data dictionary plus
the HARD gates G-R1 and G-R2 of the frozen RBD pre-registration.  No torch,
no esm, no network: it reads only the local files acquired in A5a.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Task A5b under the frozen
prereg/RBD_REPLICATION_PREREG_v1.md sections 2 and 7, quoted verbatim:

  "G-R1 Alpha differs from Wuhan-Hu-1 in the RBD by exactly N501Y and Eta
   by exactly E484K in the data's own reference sequences. G-R2 every data
   row's wild-type residue equals the sequence residue at its site."

  (section 2, for the dictionary:) "File and column names are recorded in
   the implementation log, not guessed here."

NAMING, fixed here so it cannot be read post-hoc: the frozen block names
its two targets "Alpha = N501Y" and "Eta = E484K" (prereg line 8).  The
repository never uses those words: its README lists the four backgrounds
as Wuhan-Hu-1 / E484K / N501Y ("found in the B.1.1.7 lineage") /
K417N-E484K-N501Y ("found in the B.1.351 lineage"), and the data column
`target` holds the five labels {'Wuhan-Hu-1', 'E484K', 'N501Y', 'Beta',
'Delta'} where `Beta` is the same background the README calls
K417N-E484K-N501Y.  So, for this module only:

    Alpha  == data label 'N501Y'   (frozen block's target T = N501Y)
    Eta    == data label 'E484K'   (frozen block's target T = E484K)

'Beta' and 'Delta' are present in the data and are reported in the
dictionary; they are not targets T anywhere in the frozen block.

REFERENCE CHAIN (every link fixed here, before the first run; none of it
consults the `wildtype` column of final_variant_scores.csv):

  R1  data/RBD_sites.csv (201 rows, site 331..531 contiguous) column
      `amino_acid` = the repository's own Wuhan-Hu-1 RBD reference.
  R2  data/wildtype_sequence.fasta (603 nt) translated in frame 1 must
      equal R1 exactly (independent second copy of the same reference).
  R3  PacBio_amplicon_Wuhan_Hu_1.gb (1079 bp, GenBank) translated after
      trimming to a whole number of codons must contain R1 as an exact
      substring, and must contain it EXACTLY ONCE; that unique 0-based
      index J fixes the numbering offset used for every amplicon:
      site = (0-based protein index) + (331 - J).  The four amplicons are
      the same construct, so one J serves all of them; each target's
      201-residue window is the amplicon protein sliced at [J, J+201].
  R4  Delta has NO amplicon in this repository (its README says the Delta
      data were "downloaded from" jbloomlab/SARS-CoV-2-RBD_Delta), so the
      Delta window is R1 with the two substitutions this repository's own
      README states for that background -- "Delta background
      (L452R+T478K)" -- applied at 452 and 478.  That sentence is
      asserted to be present in README.md at run time; the substitution
      list is taken from it, not from scanning the data.  If the data
      asserted any additional wild-type difference for Delta, G-R2 fails.

GATES (hard; a failed gate prints FAIL and exits 3; thresholds are the
frozen ones and are never widened; no N is ever raised to pass):

  G-R1  window('N501Y') - window('Wuhan-Hu-1') == exactly one
        substitution, N->Y at site 501;  window('E484K') -
        window('Wuhan-Hu-1') == exactly one substitution, E->K at
        site 484.  (Compared as the exact difference list, so a second
        substitution, a wrong site, or a wrong residue pair fails.)
  G-R2  for EVERY row of final_variant_scores.csv (all 20,100, none
        dropped, none sampled), row['wildtype'] equals the reference
        residue of that row's own target at that row's site; and every
        target covers all 201 sites with the expected 20 rows per
        (target, site).

REPORT-ONLY, never gated (printed for the record): the Beta window's
difference from the Wuhan reference and its agreement with the README's
K417N-E484K-N501Y; the Delta data's own difference list against R1; the
three-way agreement of R1, R2 and R3; input sha256 re-derivations.

DATA DICTIONARY (printed in full): the first line of each acquired table
quoted verbatim (repr(), so quoting is exact); target labels with row
counts; the Alpha/Eta mapping above; per-target row counts and
per-position structure; the barcode-count columns' distributions
(n_bc_bind, n_bc_expr: min/quartiles/max and the fractions at >=1, >=3,
>=5 -- the frozen block's filter and its two sensitivities, counts only,
nothing selected here); n_libs_bind / n_libs_expr ranges; the per-library
columns; and, as context for task A6a only, the distribution of
n_aa_substitutions in the barcode-level table.

DECISIONS (pre-registered here, before the first run):
  D1  Nothing is filtered in A5b: all 20,100 rows are checked by G-R2.
  D2  The script writes no data files.  Its only product is the printed
      record (captured to PHASE3_A5b_FULL_OUTPUT.txt) and the log entry.
  D3  `wildtype_sequence.fasta` is treated as a cross-check of the site
      table (R2), not as the primary reference, because the site table is
      the file the repository's own analysis indexes by `site`.
  D4  If G-R1 or G-R2 fails: print FAIL, exit 3, and stop the R module;
      do not re-derive the reference from the data to make it pass.

Usage:
  venv/bin/python3 scripts/162_rbd_inputs_gate.py

LIMITATIONS (AGENTS section 6, printed by the script itself): this checks
reference/numbering integrity only -- it says nothing about any rho,
e_T or outcome word; the frozen block's outcome words are not computed
here and none of the words reserved for other blocks appear; two targets
are two looks (frozen section 5), stated but not adjusted for, and no
test is run here at all; the Delta reference rests on this repository's
README because no Delta amplicon exists in it (disclosed in R4).
"""

import hashlib
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "external" / "rbd_starr2022"
LOG_JSON = EXT / "acquisition_log.json"
SITES_CSV = EXT / "RBD_sites.csv"
FASTA = EXT / "wildtype_sequence.fasta"
README = EXT / "README.md"
SCORES = EXT / "final_variant_scores.csv"
BC_BIND = EXT / "bc_binding.csv"
BC_EXPR = EXT / "bc_expression.csv"

AMPLICONS = {                      # data label -> GenBank file stem
    "Wuhan-Hu-1": "Wuhan_Hu_1",
    "N501Y": "N501Y",
    "E484K": "E484K",
    "Beta": "B1351",
}
DELTA_MUTS = {452: ("L", "R"), 478: ("T", "K")}   # README "L452R+T478K"
DELTA_QUOTE = "Delta background (L452R+T478K)"
EXPECTED_TARGETS = ["Beta", "Delta", "E484K", "N501Y", "Wuhan-Hu-1"]
ALPHA_IS, ETA_IS = "N501Y", "E484K"               # frozen block, line 8
G_R1_EXPECT = {
    "N501Y": [(501, "N", "Y")],
    "E484K": [(484, "E", "K")],
}
SITE_MIN, SITE_MAX = 331, 531
ROWS_PER_SITE = 20                # 19 mutants + the wild-type row

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}")


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_refs():
    """Return (site_table, fasta_prot, amplicon windows, J). Pre-registered
    reference chain R1-R4; never touches final_variant_scores.csv."""
    import re
    from Bio import SeqIO
    from Bio.Seq import Seq

    sites = pd.read_csv(SITES_CSV)
    site_table = {int(s): a for s, a in zip(sites["site"], sites["amino_acid"])}
    ref = "".join(site_table[s] for s in range(SITE_MIN, SITE_MAX + 1))

    rec = SeqIO.read(str(FASTA), "fasta")
    fs = str(rec.seq)
    fasta_prot = str(Seq(fs[: len(fs) // 3 * 3]).translate())

    prots = {}
    for label, stem in AMPLICONS.items():
        r = SeqIO.read(str(EXT / f"PacBio_amplicon_{stem}.gb"), "genbank")
        s = str(r.seq)
        prots[label] = str(Seq(s[: len(s) // 3 * 3]).translate()), len(s)

    wu_prot = prots["Wuhan-Hu-1"][0]
    hits = [m.start() for m in re.finditer("(?=" + ref + ")", wu_prot)]
    if len(hits) != 1:
        print(f"GATE FAILED: Wuhan amplicon contains the {len(ref)}-residue "
              f"site-table reference {len(hits)} times (need exactly 1)")
        sys.exit(3)
    J = hits[0]
    windows = {lab: p[J:J + len(ref)] for lab, (p, _) in prots.items()}

    # R4: Delta window from the README's own sentence
    readme = README.read_text()
    if DELTA_QUOTE not in readme:
        print(f"GATE FAILED: README.md no longer contains {DELTA_QUOTE!r}; "
              f"the Delta reference cannot be built from the repository's "
              f"own record")
        sys.exit(3)
    d = dict(site_table)
    for pos, (wt, mt) in DELTA_MUTS.items():
        assert d[pos] == wt, (pos, d[pos], wt)
        d[pos] = mt
    windows["Delta"] = "".join(d[s] for s in range(SITE_MIN, SITE_MAX + 1))
    return site_table, fasta_prot, windows, J, prots


def main():
    t0 = time.time()
    print("PHASE 3a Task A5b -- RBD data dictionary + HARD gates G-R1, G-R2 "
          "(frozen RBD_REPLICATION_PREREG_v1.md)")
    print("No torch/esm, no network, no files written; all 20,100 rows "
          "checked (nothing sampled).")

    # ---- 0. input integrity (internal, not a prereg gate) ---------------
    rule("INPUT INTEGRITY -- files on disk vs A5a acquisition_log.json")
    acq = json.loads(LOG_JSON.read_text())
    bad = []
    for e in acq:
        p = ROOT / e["dest"]
        h = sha256(p) if p.exists() else "MISSING"
        b = p.stat().st_size if p.exists() else -1
        ok = (h == e["sha256"] and b == e["bytes"])
        if not ok:
            bad.append(e["dest"])
        print(f"  {'ok ' if ok else 'BAD'} {p.name:<32} bytes={b:>9,} "
              f"sha256={h[:16]}...")
    gate("G-162-1 input files match acquisition log", "PASS" if not bad
         else "FAIL", f"{len(acq) - len(bad)}/{len(acq)} files match",
         f"expected sha/bytes from acquisition_log.json")
    if bad:
        sys.exit(3)

    # ---- 1. data dictionary --------------------------------------------
    rule("DATA DICTIONARY -- headers quoted verbatim (repr, first line)")
    for p in (SCORES, BC_BIND, BC_EXPR, SITES_CSV):
        with open(p) as fh:
            first = fh.readline().rstrip("\n")
        print(f"  {p.name}:\n    {first!r}")

    d = pd.read_csv(SCORES)
    print(f"\n  final_variant_scores.csv: {d.shape[0]} rows x "
          f"{d.shape[1]} columns")
    print(f"  columns: {list(d.columns)}")

    rule("BACKGROUNDS PRESENT -- labels, counts, Alpha/Eta mapping")
    counts = d["target"].value_counts().sort_index()
    print("  target labels in the data (verbatim):")
    for k, v in counts.items():
        print(f"    {k:<14} {v:>6} rows")
    labels = sorted(d["target"].unique())
    gate("G-162-2 target label set is the expected five",
         "PASS" if labels == EXPECTED_TARGETS else "FAIL",
         f"{labels}", f"expected {EXPECTED_TARGETS}")
    present = {w: (w in labels) for w in
               ["Wuhan-Hu-1", ALPHA_IS, ETA_IS]}
    gate("G-162-3 Wuhan-Hu-1, Alpha and Eta are present",
         "PASS" if all(present.values()) else "FAIL",
         f"Wuhan-Hu-1={present['Wuhan-Hu-1']}, "
         f"Alpha=={ALPHA_IS}={present[ALPHA_IS]}, "
         f"Eta=={ETA_IS}={present[ETA_IS]}",
         "frozen block line 8: Alpha = N501Y, Eta = E484K; the repository "
         "never uses those words (README says B.1.1.7 / E484K)")
    if labels != EXPECTED_TARGETS or not all(present.values()):
        sys.exit(3)

    # ---- 2. reference chain --------------------------------------------
    rule("REFERENCE CHAIN R1-R4 (independent of the wildtype column)")
    site_table, fasta_prot, windows, J, prots = load_refs()
    ref = "".join(site_table[s] for s in range(SITE_MIN, SITE_MAX + 1))
    contig = (sorted(site_table) == list(range(SITE_MIN, SITE_MAX + 1)))
    gate("R1 site table contiguous 331..531", "PASS" if contig else "FAIL",
         f"{len(site_table)} sites, {SITE_MIN}..{SITE_MAX}", "")
    agree_f = (fasta_prot == ref)
    gate("R2 wildtype_sequence.fasta translation == site table",
         "PASS" if agree_f else "FAIL",
         f"603 nt -> {len(fasta_prot)} aa, equal={agree_f}",
         "independent second copy of the reference")
    offset0 = SITE_MIN - J            # 0-based: site = idx0 + offset0
    offset1 = SITE_MIN - (J + 1)      # 1-based: site = idx1 + offset1
    print(f"  R3 Wuhan amplicon: {prots['Wuhan-Hu-1'][1]} bp -> protein, "
          f"site-table reference found exactly once at 0-based index J={J}")
    print(f"      numbering: site = (0-based protein index) + {offset0} "
          f"(check: {J} + {offset0} = {J + offset0} == first site "
          f"{SITE_MIN}; 1-based form: site = index + {offset1})")
    for lab in AMPLICONS:
        w = windows[lab]
        diffs = [(SITE_MIN + i, ref[i], w[i]) for i in range(len(ref))
                 if w[i] != ref[i]]
        n_x = w.count("X")
        print(f"      window[{lab:<12}] len {len(w)}, X-residues {n_x}, "
              f"diffs vs Wuhan reference: {diffs}")
    print(f"      window[Delta         ] built from R1 + README "
          f"{DELTA_MUTS} (no amplicon in this repository)")

    # ---- 3. G-R1 --------------------------------------------------------
    rule("G-R1 (hard) -- Alpha = N501Y and Eta = E484K differ from "
         "Wuhan-Hu-1 by EXACTLY that one substitution, in the repository's "
         "own reference sequences")
    g1_ok = True
    for lab, exp in G_R1_EXPECT.items():
        w = windows[lab]
        diffs = [(SITE_MIN + i, ref[i], w[i]) for i in range(len(ref))
                 if w[i] != ref[i]]
        got_ok = (diffs == exp)
        g1_ok &= got_ok
        print(f"  {lab}: differences vs Wuhan-Hu-1 = {diffs}")
        print(f"    frozen expectation                = {exp}")
        gate(f"G-R1 {lab} window differs by exactly "
             f"{'N501Y' if lab == 'N501Y' else 'E484K'}",
             "PASS" if got_ok else "FAIL",
             f"diffs = {diffs}", f"required exactly {exp}")
    gate("G-R1 overall", "PASS" if g1_ok else "FAIL",
         "one substitution each, at 501 (N->Y) and 484 (E->K)",
         "frozen prereg section 7, G-R1")
    if not g1_ok:
        print("\nGATE FAILED (G-R1): stopping the R module; the reference "
              "chain is not rebuilt from the data.")
        sys.exit(3)

    rule("REPORT ONLY (never gated) -- Beta / Delta consistency with the "
         "repository's own README")
    readme = README.read_text()
    print(f"  README quote present: {DELTA_QUOTE!r} = "
          f"{DELTA_QUOTE in readme}")
    for lab, exp in [("Beta", [(417, "K", "N"), (484, "E", "K"),
                               (501, "N", "Y")]),
                     ("Delta", [(452, "L", "R"), (478, "T", "K")])]:
        if lab == "Delta":
            print(f"  Delta: no amplicon in this repository; window built "
                  f"from the README sentence (see R4). Expected data-side "
                  f"difference vs Wuhan reference: {exp}")
            continue
        w = windows[lab]
        diffs = [(SITE_MIN + i, ref[i], w[i]) for i in range(len(ref))
                 if w[i] != ref[i]]
        print(f"  {lab}: window diffs vs Wuhan reference = {diffs}")
        print(f"    README states K417N-E484K-N501Y        = {exp}  "
              f"agrees: {diffs == exp}")
    delta_wt = (d[d["target"] == "Delta"].drop_duplicates("position")
                .set_index("position")["wildtype"].to_dict())
    data_diffs = [(p, ref[p - SITE_MIN], delta_wt[p])
                  for p in sorted(delta_wt)
                  if delta_wt[p] != ref[p - SITE_MIN]]
    print(f"  Delta DATA wildtype vs Wuhan reference = {data_diffs}")
    print(f"    equals the README pair L452R+T478K : "
          f"{data_diffs == [(452, 'L', 'R'), (478, 'T', 'K')]}")

    # ---- 4. G-R2 --------------------------------------------------------
    rule("G-R2 (hard) -- every data row's wild-type residue equals the "
         "sequence residue at its site (all rows, no filtering)")
    d["_ref"] = [windows[t][p - SITE_MIN] if SITE_MIN <= p <= SITE_MAX
                 else None for t, p in zip(d["target"], d["position"])]
    oob = d["_ref"].isna().sum()
    mism = d[d["wildtype"] != d["_ref"]]
    print(f"  rows checked            : {len(d):,} (0 dropped)")
    print(f"  rows outside 331..531   : {oob}")
    print(f"  wildtype != reference   : {len(mism)}")
    if len(mism):
        print(mism[["target", "position", "wildtype", "_ref", "mutation"]]
              .head(20).to_string(index=False))
    per_target = d.groupby("target").size()
    sites_per_target = d.groupby("target")["position"].nunique()
    cells = d.groupby(["target", "position"]).size()
    struct_ok = (all(per_target[t] == len(site_table) * ROWS_PER_SITE
                     for t in EXPECTED_TARGETS)
                 and all(sites_per_target[t] == len(site_table)
                         for t in EXPECTED_TARGETS)
                 and (cells == ROWS_PER_SITE).all())
    recon = (d["wildtype"] + d["position"].astype(str) + d["mutant"]
             == d["mutation"]).all()
    gate("G-162-4 table structure: 5 targets x 201 sites x 20 rows",
         "PASS" if struct_ok else "FAIL",
         f"per-target rows {dict(per_target)}, sites "
         f"{dict(sites_per_target)}, cells all == {ROWS_PER_SITE}: "
         f"{bool((cells == ROWS_PER_SITE).all())}",
         "nothing dropped; 201 wild-type rows per target = 1,005 total")
    gate("G-162-5 mutation == wildtype + position + mutant",
         "PASS" if bool(recon) else "FAIL", f"holds for {len(d):,} rows",
         "internal consistency of the label column")
    gate("G-R2 every row's wildtype equals its target's sequence residue",
         "PASS" if (len(mism) == 0 and oob == 0 and struct_ok) else "FAIL",
         f"mismatches {len(mism)} / {len(d):,} rows, out-of-range {oob}",
         "frozen prereg section 7, G-R2; per-target references (the five "
         "positions 417/452/478/484/501 legitimately carry two residues, "
         "one per background)")
    d.drop(columns=["_ref"], inplace=True)

    # ---- 5. dictionary: counts and barcode-count distributions ----------
    rule("DICTIONARY -- per-background mutation counts")
    for t in EXPECTED_TARGETS:
        sub = d[d["target"] == t]
        n_wt = int((sub["mutant"] == sub["wildtype"]).sum())
        print(f"  {t:<14} rows {len(sub):>5} | distinct sites "
              f"{sub['position'].nunique():>3} | wild-type rows {n_wt:>3} "
              f"| non-wild-type rows {len(sub) - n_wt:>5}")

    rule("DICTIONARY -- barcode-count columns (n_bc_bind / n_bc_expr); "
         "the frozen filter is n_bc >= 3 in BOTH backgrounds, sensitivities "
         ">= 1 and >= 5 (counts only; nothing selected here)")
    for col in ("n_bc_bind", "n_bc_expr"):
        print(f"\n  {col}:")
        g = d.groupby("target")[col]
        desc = g.agg(["count", "min", "median", "max"])
        desc["p25"] = g.quantile(0.25)
        desc["p75"] = g.quantile(0.75)
        for thr in (1, 3, 5):
            desc[f"ge{thr}"] = g.apply(lambda s, t=thr: float((s >= t).mean()))
        print(desc[["count", "min", "p25", "median", "p75", "max",
                    "ge1", "ge3", "ge5"]]
              .to_string(float_format=lambda x: f"{x:,.3f}"))
    both3 = d[(d["n_bc_bind"] >= 3) & (d["n_bc_expr"] >= 3)]
    print(f"\n  rows with n_bc_bind >= 3 AND n_bc_expr >= 3: "
          f"{len(both3):,} / {len(d):,} ({len(both3) / len(d):.1%})  "
          f"[A5c will apply this per target T against Wuhan-Hu-1; this line "
          f"is dictionary context only]")

    rule("DICTIONARY -- n_libs ranges, per-library columns, barcode-level "
         "tables")
    print("  " + d.groupby("target")[["n_libs_bind", "n_libs_expr"]]
          .agg(["min", "max"]).to_string().replace("\n", "\n  "))
    lib_cols = [c for c in d.columns if "_rep" in c]
    print(f"  per-library columns present in final_variant_scores.csv: "
          f"{lib_cols}")
    print("  non-null counts per target for the per-library columns "
          "(A5c reliability input):")
    print("  " + d.groupby("target")[lib_cols].count().to_string())
    bcb = pd.read_csv(BC_BIND)
    bce = pd.read_csv(BC_EXPR)
    print(f"\n  bc_binding.csv    : {len(bcb):,} rows; targets "
          f"{sorted(bcb['target'].unique())}")
    print(f"  bc_expression.csv : {len(bce):,} rows; targets "
          f"{sorted(bce['target'].unique())}")
    print("  n_aa_substitutions distribution in bc_binding.csv "
          "(context for task A6a's multi-mutant audit):")
    print("  " + bcb.groupby(["target", "n_aa_substitutions"]).size()
          .unstack(fill_value=0).to_string())
    print("  variant_class values (verbatim, top 6):")
    print("  " + bcb["variant_class"].value_counts().head(6)
          .to_string())

    # ---- summary --------------------------------------------------------
    rule("SUMMARY -- A5b / G-R1 / G-R2")
    n_pass = 0
    for name, verdict, value, note in GATES:
        print(f"  [{verdict}] {name}: {value}  {note}")
        n_pass += verdict == "PASS"
    ok = n_pass == len(GATES)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS -> "
          f"{'A5b PASSES; G-R1 and G-R2 are green' if ok else 'A5b FAILS'}")
    print("\n  LIMITATIONS (AGENTS 6):")
    print("    * reference/numbering integrity only -- no rho, no e_T, no "
          "outcome word is computed here;")
    print("      no outcome word of any frozen block appears in this "
          "output.")
    print("    * G-R2 checks the wild-type label against sequences derived "
          "from the repository's own files;")
    print("      for Delta that chain ends at the repository's README "
          "(no Delta amplicon exists here),")
    print("      which is disclosed rather than treated as independent "
          "sequence evidence.")
    print("    * the two targets T of the frozen block are two looks with "
          "no multiplicity adjustment")
    print("      (frozen section 5) -- stated here; no test is run in this "
          "script.")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
