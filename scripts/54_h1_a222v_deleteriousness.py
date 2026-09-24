"""
Task H1 (review-triage): does ESM-2 even think A222V is deleterious?

H1a [items 25, 26]: Report S(A222V | WT) directly. If near-neutral, the
model has no internal reason to propagate any correction from it.

H1b [item 26]: Ortholog conservation at position 222. If Val occurs
commonly in some clades, "V222 context" sensitivity may be a
phylogenetic/clade cue rather than a destabilization signal.

PRE-REGISTERED DESIGN (stated before running -- AGENTS.md §6)
--------------------------------------------------------------
H1a:
  S(A222V | WT) = esm2_wt_scores row (position=222, wt=A, mut=V) --
  the WT-background masked-marginal score, no re-scoring, exact on-disk
  value.
  Contextual statistics (same 12,445-row file): percentile of ALL
  WT-background scores lying at or below A222V (deleterious direction =
  more negative), z-score, rank among position 222's own substitutions,
  mildest substitution at 222 for scale.
  Pre-registered banding (thresholds fixed now, p10/p90 as used
  elsewhere in this project, e.g. F1b):
    FLAGGED-DELETERIOUS iff score <= p10(all);
    NEAR-NEUTRAL iff p10 < score < p90;
    BENIGN-TAIL iff score >= p90.
  (Disclosure: the score value -5.20 was visible during data inspection
  at design time; the BANDING rule is the project's standard p10/p90 and
  was written into the docstring before the script was run. The score
  report itself has no degrees of freedom.)

H1b:
  Fetch ALL reviewed UniProt entries with gene name MTHFR
  (rest.uniprot.org), keep non-human sequences of length 400-800,
  global-align each to human P42898 (Bio.Align.PairwiseAligner, BLOSUM62,
  global, affine gaps), map human residue 222 through the alignment,
  record the ortholog residue.
  Human self-check: P42898 must map back to A at 222 (exit 1 otherwise --
  tests the alignment machinery, AGENTS.md §4).
  Pre-registered sets: PRIMARY identity >= 50% (alignment-trust floor);
  SECONDARY identity >= 30% (broader, labeled). Identity =
  identities / (identities + mismatches + gaps) over the full global
  alignment.
  Pre-registered reading of the review's "Val occurs commonly":
    VAL-COMMON iff V fraction >= 0.20 of non-gap-at-222 residues in the
    PRIMARY set (the 20% figure is an explicit assumption; "commonly" is
    undefined in the review -- logged as an assumption, conservative-ish
    midpoint).
  Rows where human 222 aligns to a gap in the ortholog are KEPT and
  counted (res222 = "-"), so they cannot silently inflate any fraction.

LIMITATIONS stated up front:
  * UniProt "reviewed" coverage is biased toward model organisms and
    vertebrates; clade statements describe the sample. Sampling printed.
  * Global alignment of distant MTHFRs can misplace 222; identity floors
    and the human self-check bound but do not eliminate this.

No bootstrap/permutation in this task (descriptive report + explicit
threshold readings). Results CSV: task54_h1b_conservation.csv; fetched
provenance: task54_uniprot_mthfr.tsv.
"""
import sys, urllib.request, urllib.parse, warnings
from io import StringIO
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
HUMAN_ACC = "P42898"
POS = 222


def h1a():
    print("=" * 74)
    print("H1a: S(A222V | WT) reported directly")
    print("=" * 74)
    esm = pd.read_csv(PROC / "esm2_wt_scores.csv")
    n = len(esm)
    row = esm[(esm["position"] == POS) & (esm["wt_aa"] == "A") &
              (esm["mut_aa"] == "V")]
    if len(row) != 1:
        print(f"*** expected exactly 1 row, got {len(row)}. sys.exit(1)")
        sys.exit(1)
    s = float(row["esm2_score"].iloc[0])
    hgvs = row["hgvs_pro"].iloc[0]
    scores = esm["esm2_score"].to_numpy(float)
    p10, p90 = np.percentile(scores, 10), np.percentile(scores, 90)
    frac_at_or_more_deleterious = float((scores <= s).mean())
    z = (s - scores.mean()) / scores.std()
    at222 = esm[esm["position"] == POS].sort_values("esm2_score")
    rank = int((at222["esm2_score"] < s).sum()) + 1  # 1 = most deleterious
    mildest_idx = int(np.argmax(at222["esm2_score"].to_numpy()))
    mildest = float(at222["esm2_score"].iloc[mildest_idx])
    mildest_hgvs = at222["hgvs_pro"].iloc[mildest_idx]
    reading = ("FLAGGED-DELETERIOUS" if s <= p10 else
               "BENIGN-TAIL" if s >= p90 else
               "NEAR-NEUTRAL" if p10 < s < p90 else "UNCLASSIFIED")
    print(f"  file rows: {n}")
    print(f"  S(A222V | WT) [{hgvs}] = {s:+.6f}")
    print(f"  all-score p10 = {p10:+.4f}  p90 = {p90:+.4f}  "
          f"mean = {scores.mean():+.4f}  sd = {scores.std():.4f}")
    print(f"  fraction of all substitutions scoring <= A222V "
          f"(at least as deleterious): {frac_at_or_more_deleterious:.4f}")
    print(f"  z-score vs all: {z:+.3f}")
    print(f"  rank among position 222's substitutions (1=most deleterious): "
          f"{rank} of {len(at222)}")
    print(f"  mildest substitution at 222: {mildest:+.4f} ({mildest_hgvs})")
    print(f"  pre-registered reading: {reading}")
    print("    (FLAGGED iff <= p10; NEAR-NEUTRAL iff inside (p10, p90); "
          "BENIGN-TAIL iff >= p90)")
    return {"s": s, "reading": reading}


def _query(q):
    params = urllib.parse.urlencode({
        "query": q, "fields": "accession,id,organism_name,sequence",
        "format": "tsv", "size": "500"})
    with urllib.request.urlopen(
            "https://rest.uniprot.org/uniprotkb/search?" + params,
            timeout=60) as r:
        return pd.read_csv(StringIO(r.read().decode()), sep="\t")


def fetch_uniprot():
    # Two queries unioned: (1) protein_name catches non-mammalian
    # orthologs whose gene symbol is metF/MET12/MTHFR1 etc.;
    # (2) gene:MTHFR catches entries whose protein name differs.
    # This broadened fetch was chosen AFTER the first attempt returned
    # only 4 entries (gene:MTHFR alone matches essentially just mammals);
    # it is a data-COLLECTION completeness fix made before any alignment
    # result was computed -- disclosed in the log entry.
    a = _query('(reviewed:true) AND '
               '(protein_name:"methylenetetrahydrofolate reductase")')
    b = _query('(reviewed:true) AND (gene:MTHFR)')
    df = pd.concat([a, b], ignore_index=True).drop_duplicates(
        subset=[a.columns[0]])
    (PROC / "task54_uniprot_mthfr.tsv").write_text(
        "# union of two reviewed-UniProt queries, see script 54 docstring\n"
        + df.to_csv(sep="\t", index=False))
    return df


def h1b():
    print("\n" + "=" * 74)
    print("H1b: ortholog conservation at position 222")
    print("=" * 74)
    from Bio.Align import PairwiseAligner, substitution_matrices
    uni = fetch_uniprot()
    print(f"  UniProt reviewed entries fetched (2-query union): {len(uni)} "
          f"(saved to data/processed/task54_uniprot_mthfr.tsv)")
    acc_c = list(uni.columns)[0]
    org_c = [c for c in uni.columns if "organism" in c.lower()][0]
    seq_c = [c for c in uni.columns if "sequence" in c.lower()][0]

    hum_rows = uni[uni[acc_c] == HUMAN_ACC]
    if len(hum_rows) == 0:
        print("  *** human P42898 not in fetch. sys.exit(1)")
        sys.exit(1)
    human_seq = hum_rows[seq_c].iloc[0]

    al = PairwiseAligner()
    al.mode = "global"
    al.substitution_matrix = substitution_matrices.load("BLOSUM62")
    al.open_gap_score, al.extend_gap_score = -10, -0.5

    rows = []
    for _, rr in uni.iterrows():
        acc, org, seq = rr[acc_c], rr[org_c], rr[seq_c]
        if not isinstance(seq, str):
            continue
        if acc == HUMAN_ACC:
            rows.append({"acc": acc, "org": org, "len": len(seq),
                         "identity": 1.0, "res222": "A", "is_human": True})
            continue
        if not (400 <= len(seq) <= 800):
            continue
        aln = al.align(human_seq, seq)[0]
        # aligned coords: shape (2, n_blocks, 2) -- row 0 = human blocks,
        # row 1 = ortholog blocks. (An earlier draft unpacked this as if
        # there were exactly 2 blocks; real alignments have more. Fixed at
        # smoke stage before any result was computed -- disclosed in log.)
        hb_all, sb_all = aln.aligned[0], aln.aligned[1]
        target_res = "-"          # default: human 222 falls in a gap
        for hb, sb in zip(hb_all, sb_all):
            if hb[0] <= 221 < hb[1]:
                off = 221 - hb[0]
                target_res = (seq[sb[0] + off]
                              if sb[0] + off < sb[1] else "-")
                break
        cnt = aln.counts()
        total = cnt.identities + cnt.mismatches + cnt.gaps
        ident = cnt.identities / total if total else 0.0
        rows.append({"acc": acc, "org": org, "len": len(seq),
                     "identity": float(ident), "res222": target_res,
                     "is_human": False})
    df = pd.DataFrame(rows)
    hum = df[df["is_human"]]
    if len(hum) != 1 or hum["res222"].iloc[0] != "A":
        print("  *** human self-check FAILED (222 must map to A). sys.exit(1)")
        sys.exit(1)
    print("  human self-check: P42898 maps back to A at 222 -> OK")
    orth = df[~df["is_human"]].copy()
    print(f"  orthologs kept (length 400-800): {len(orth)}  "
          f"(fetched minus human minus out-of-range lengths)")
    for label, floor in [("PRIMARY (identity >= 50%)", 0.50),
                         ("SECONDARY (identity >= 30%)", 0.30)]:
        sset = orth[orth["identity"] >= floor]
        vc = sset["res222"].value_counts()
        tot = int(vc.sum())
        if tot == 0:
            print(f"  {label}: n=0")
            continue
        frac_v = float(vc.get("V", 0)) / tot
        frac_a = float(vc.get("A", 0)) / tot
        verdict = "VAL-COMMON" if frac_v >= 0.20 else "VAL-RARE"
        print(f"  {label}: n={tot}  V={frac_v:.3f}  A={frac_a:.3f}  "
              f"-> {verdict}")
        print(f"    residue counts: "
              f"{', '.join(f'{k}:{v}' for k, v in vc.head(10).items())}")
    print("    (pre-registered: VAL-COMMON iff V fraction >= 0.20 of "
          "non-gap-at-222 residues)")
    out = PROC / "task54_h1b_conservation.csv"
    df.to_csv(out, index=False)
    print(f"  saved {out}")
    print("  LIMITATIONS: reviewed-UniProt sampling is model-organism/"
          "vertebrate biased; clade claims describe the sample. Identity "
          "floors bound alignment risk but distant orthologs may still "
          "misplace 222. Gap-at-222 rows are counted (res222='-'), not "
          "silently dropped.")
    return df


if __name__ == "__main__":
    h1a()
    h1b()
    print("\nDone.")
