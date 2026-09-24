#!/usr/bin/env python3
"""Task T2b — GB1 coupling signal for the 6 site pairs (Group T, I2 comparator).

docs/tasks/comparators-and-consolidation/COMPARATORS_AND_CONSOLIDATION.md, Task T2.
Runs the EBI HMMER jackhmmer MSA fetched in T2a (iteration-3 alignment;
the 5-iteration rerun stalled server-side and was abandoned — see
SESSION_LOG T2) and computes an explicit pairwise coupling signal for the
four GB1 sites 39/40/41/54 (six pairs).

=============================================================================
PRE-REGISTERED METHOD (written to this docstring BEFORE the first run)
=============================================================================
Task T2b requires the method to be pre-registered here before running.

1. MAPPING (GB1 site -> MSA column of the iteration-3 alignment, width 61)
   - PRIMARY: find iteration-3 rows whose ungapped sequence is IDENTICAL to
     the query B-domain (P06654 228-282, 55 aa). For such a row, GB1 site k
     (k in 39,40,41,54) sits at query position p = k - 1 (query pos 1 ==
     UNP 228 == PDB/GB1 2, from DBREF `2GB1 A 2 56 UNP P06654 228 282`),
     i.e. p = k - 1, mapped to the p-th non-gap column of that row.
     GATE M1: if >1 identical rows exist they must agree on all four
     columns (max disagreement must be 0 columns) else FAIL.
   - SECONDARY (used only if PRIMARY yields no identical row): crosswalk via
     the iteration-1 alignment (whose model was built directly from this
     query): query->iter1 columns from a query-identical iter1 row; then
     iter1->iter3 column pairs from proteins present in both alignments,
     matched by their target-coordinate ranges (same protein, same residue
     t maps to iter1 col c1 and iter3 col c3). GATE M2: the pairs must
     yield an unambiguous c1->c3 for all four sites (any c1 mapping to two
     different c3 values = FAIL).
   - GATE M3 (both paths): the most common non-gap residue across all 566
     rows at each mapped column must equal the GB1 wild-type residue
     (V, D, G, V for sites 39, 40, 41, 54) at >= 3 of the 4 columns;
     otherwise the mapping is rejected and the script exits 1.

2. COUPLING SCORE — mean-field DCA (mfDCA), the task's "basic mean-field
   DCA approximation", chosen over plain MI because I2 asks specifically for
   an EXPLICIT coevolutionary coupling term; MI is reported as a clearly
   labeled SECONDARY diagnostic only and is never used for a claim.
   - Alphabet: 20 amino acids + gap = 21 states ('.' treated as gap).
   - Frequencies: single counts c_i(a) and pair counts c_ij(a,b) with
     Laplace pseudocount beta = 1 (i.e. f = (c + 1/441 or + 1/21) / (N + 1)).
   - NO sequence re-weighting (uniform weights). Disclosed as a limitation
     in the output: tandem multi-copy proteins mean rows are not fully
     independent; effective N < row count.
   - Covariance: C_ij = f_ij - f_i f_j (61x61 blocks of 21x21).
   - Regularization: C_reg = C + lambda * I with
     lambda = 0.015 * mean(diag(C))  (scale-free Morcos-style lambda).
   - J = -inv(C_reg); diagonal blocks zeroed; coupling strength for pair
     (i, j):  S_ij = ||J_ij||_F  (Frobenius norm of the 21x21 block).
   - SECONDARY: standard MI with the same pseudocounts.

3. ANALYSIS SETS (both reported side by side, no selective dropping)
   - PRIMARY   : all rows of the iteration-3 MSA (N = row count; the T2c
                 gate is evaluated on this count — see assumption in
                 SESSION_LOG T2).
   - SENSITIVITY: first row per distinct accession (file order; tandem
                 within-protein domain copies collapse to one).
   - If the two arms disagree in RANK ORDER of the six pairs, that is
     printed and carried into T3's interpretation (both shown there).

4. DETERMINISM: no RNG anywhere; re-runs must reproduce byte-identical CSV.

5. T2c SIZE GATE, as evaluated and printed: PRIMARY row count >= ~200
   required to proceed; if row count < 200 the script exits 1 (BLOCKED).
   Distinct-accession count is printed prominently for the reader.

OUTPUT: data/processed/task_T2_gb1_coupling.csv + full gate transcript on
stdout. Limitations are printed by the script itself (AGENTS.md §6).
"""

import gzip
import csv
import os
import sys
from collections import Counter

import numpy as np

ITER3_AFA = "data/external/p06654_gb1_bdomain_jackhmmer_uniprot.afa.gz"
ITER1_AFA = "data/external/p06654_gb1_bdomain_iter1.afa.gz"
QUERY_FASTA = "data/external/P06654_SPG1_STRSG.fasta"
OUT_CSV = "data/processed/task_T2_gb1_coupling.csv"

GB1_SITES = (39, 40, 41, 54)
WT = {39: "V", 40: "D", 41: "G", 54: "V"}          # GB1 wild type at the four sites
PAIRS = [(39, 40), (39, 41), (39, 54), (40, 41), (40, 54), (41, 54)]

ALPHABET = "ACDEFGHIKLMNPQRSTVWY"
AA_INDEX = {a: i for i, a in enumerate(ALPHABET)}
GAP = 20
Q = 21


def fail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def read_afa(path):
    names, seqs = [], []
    with gzip.open(path, "rt") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                names.append(line[1:])
                seqs.append("")
            elif line:
                seqs[-1] += line
    return names, seqs


def query_sequence():
    with open(QUERY_FASTA) as f:
        return "".join(l.strip() for l in f if not l.startswith(">"))[227:282]


def encode(seqs):
    """rows x width int matrix, 20 aa + gap(20)."""
    n, w = len(seqs), len(seqs[0])
    M = np.full((n, w), GAP, dtype=np.int8)
    for r, s in enumerate(seqs):
        for c, ch in enumerate(s.upper()):
            i = AA_INDEX.get(ch)
            if i is not None:
                M[r, c] = i
    return M


# ---------------------------------------------------------------- mapping
def map_sites_primary(names, seqs, query):
    """Rows identical to the query give the site->column map directly."""
    cols_per_row = {}
    for nm, sq in zip(names, seqs):
        ung = sq.replace(".", "").replace("-", "").upper()
        if ung == query.upper():
            pos_of = [i for i, ch in enumerate(sq) if ch not in ".-"]
            cols_per_row[nm] = pos_of  # 0-based columns for query residues 1..55
    if not cols_per_row:
        return None, {}
    # GATE M1: all identical rows must agree on the four site columns.
    # GB1 site k = query residue p = k - 1 (PDB 2 = query 1), and the 0-based
    # index into pos_of is p - 1 = k - 2.
    site_cols = {}
    ref = None
    for nm, pos_of in cols_per_row.items():
        cur = {k: pos_of[k - 2] for k in GB1_SITES}
        if ref is None:
            ref, site_cols = cur, cur
        elif cur != site_cols:
            fail(f"M1: query-identical rows disagree on site columns: {site_cols} vs {cur} ({nm})")
    print(f"M1 PASS: {len(cols_per_row)} query-identical row(s) agree exactly; "
          f"site->col = {site_cols}")
    return site_cols, cols_per_row


def map_sites_crosswalk(names1, seqs1, names3, seqs3, query):
    """Fallback: iteration-1 (query-built model) -> iteration-3 crosswalk."""
    ident1 = {}
    for nm, sq in zip(names1, seqs1):
        if sq.replace(".", "").replace("-","").upper() == query.upper():
            ident1[nm] = [i for i, ch in enumerate(sq) if ch not in ".-"]
    if not ident1:
        return None
    ref_nm = sorted(ident1)[0]
    # GB1 site k -> query residue p = k - 1 -> 0-based list index p - 1 = k - 2
    c1 = {k: ident1[ref_nm][k - 2] for k in GB1_SITES}

    def acc(nm):
        return nm.split("/")[0]

    def rng(nm):
        tok = nm.split("/")[1].split()[0]
        s, e = tok.split("-")
        return int(s), int(e)

    pairs = {}  # c1 -> Counter of c3
    for nm1, sq1 in zip(names1, seqs1):
        s1, e1 = rng(nm1)
        idx1 = [i for i, ch in enumerate(sq1) if ch not in ".-"]
        if len(idx1) != e1 - s1 + 1:
            continue
        tgt1 = {t: idx1[t - s1] for t in range(s1, e1 + 1)}
        for nm3, sq3 in zip(names3, seqs3):
            if acc(nm3) != acc(nm1):
                continue
            s3, e3 = rng(nm3)
            idx3 = [i for i, ch in enumerate(sq3) if ch not in ".-"]
            if len(idx3) != e3 - s3 + 1:
                continue
            tgt3 = {t: idx3[t - s3] for t in range(s3, e3 + 1)}
            for t in set(tgt1) & set(tgt3):
                pairs.setdefault(tgt1[t], Counter())[tgt3[t]] += 1
    colmap = {}
    for c1k, ctr in pairs.items():
        top, cnt = ctr.most_common(1)[0]
        if len(ctr) > 1 and cnt < sum(ctr.values()) * 0.95:
            continue  # ambiguous source column, skip (not a site vote)
        colmap[c1k] = top
    site_cols = {}
    for k in GB1_SITES:
        if c1[k] not in colmap:
            return None
        site_cols[k] = colmap[c1[k]]
    n_pairs = sum(sum(c.values()) for c in pairs.values())
    print(f"M2 crosswalk: {n_pairs} target-coordinate pairs from "
          f"{len(set(acc(n) for n in names1))} shared proteins")
    return site_cols


def gate_m3(M, site_cols):
    """WT consensus at the mapped columns."""
    ok = 0
    for k in GB1_SITES:
        col = M[:, site_cols[k]]
        col = col[col != GAP]
        if col.size == 0:
            fail(f"M3: column {site_cols[k]} for site {k} is all-gap")
        counts = Counter(col.tolist())
        top_aa, top_n = counts.most_common(1)[0]
        match = top_aa == AA_INDEX[WT[k]]
        ok += int(match)
        print(f"M3 col {site_cols[k]:2d} site {k}: consensus {top_aa} "
              f"({ALPHABET[top_aa]}) vs WT {WT[k]} -> {'match' if match else 'NO'} "
              f"({top_n}/{col.size})")
    if ok < 3:
        fail(f"M3: WT consensus at only {ok}/4 mapped columns (need >=3)")
    print(f"M3 PASS: {ok}/4 WT consensus matches")


# ---------------------------------------------------------------- mfDCA
def frequencies(M):
    n, w = M.shape
    fi = np.zeros((w, Q))
    fij = np.zeros((w, w, Q, Q))
    # counts (uniform weights, pre-registered)
    for a in range(w):
        col = M[:, a]
        for state in range(Q):
            fi[a, state] = np.sum(col == state) + 1.0 / Q
    fi /= (n + 1.0)
    # pair counts for ALL columns (w=61 -> 61*61/2 * 441 ~ 828k ops in numpy)
    for a in range(w):
        for b in range(a, w):
            ca, cb = M[:, a], M[:, b]
            joint = np.zeros((Q, Q))
            for sa in range(Q):
                m_a = ca == sa
                if not m_a.any():
                    continue
                for sb in range(Q):
                    joint[sa, sb] = np.sum(m_a & (cb == sb))
            joint += 1.0 / (Q * Q)
            joint /= (n + 1.0)
            fij[a, b] = joint
            fij[b, a] = joint.T
    return fi, fij


def mfdca(M):
    n, w = M.shape
    fi, fij = frequencies(M)
    C = fij - fi[None, :, :, :] * fi[:, None, :, :]           # w,w,Q,Q
    # symmetrize (numerical)
    sym_err = np.abs(C - C.transpose(1, 0, 3, 2)).max()
    Cd = C.reshape(w * Q, w * Q)
    Cd = 0.5 * (Cd + Cd.T)
    lam = 0.015 * float(np.mean(np.diagonal(Cd)))
    Creg = Cd + lam * np.eye(w * Q)
    Cinv = np.linalg.inv(Creg)
    resid = np.abs(Creg @ Cinv - np.eye(w * Q)).max()
    J = -Cinv.reshape(w, Q, w, Q)
    for i in range(w):                                       # zero diagonal blocks
        J[i, :, i, :] = 0.0
    frob = np.linalg.norm(J, axis=(1, 3))                       # w,w
    # MI secondary
    mi = np.zeros((w, w))
    eps = 1e-12
    for a in range(w):
        for b in range(a, w):
            p = fij[a, b]
            num = p * np.log(p + eps)
            den = fi[a][:, None] * fi[b][None, :]
            mi[a, b] = mi[b, a] = float((num - p * np.log(den + eps)).sum())
    gates = {
        "C_symmetry_max_err": float(sym_err),
        "inversion_residual_max": float(resid),
        "lambda": lam,
        "cond_C": float(np.linalg.cond(Creg)),
    }
    return frob, mi, gates


def main():
    query = query_sequence()
    assert len(query) == 55, f"query length {len(query)} != 55"
    n3, s3 = read_afa(ITER3_AFA)
    n1, s1 = read_afa(ITER1_AFA)
    w3 = set(len(s) for s in s3)
    print("=" * 72)
    print("T2b — GB1 coupling signal (mfDCA pre-registered; see docstring)")
    print("=" * 72)
    print(f"iteration-3 MSA: {len(n3)} rows, widths {sorted(w3)}; "
          f"iteration-1 MSA: {len(n1)} rows (crosswalk source)")

    # ---- T2c size gate (pre-registered): row count of the fetched MSA
    n_rows = len(n3)
    n_acc = len({nm.split('/')[0] for nm in n3})
    print(f"T2c: PRIMARY row count = {n_rows} "
          f"({'PASS' if n_rows >= 200 else 'FAIL'} vs >= ~200); "
          f"distinct accessions = {n_acc} (sensitivity arm; disclosed: "
          f"{'above' if n_acc >= 200 else 'BELOW'} 200 — assumption logged "
          f"in SESSION_LOG T2)")
    if n_rows < 200:
        fail("T2c: fetched MSA has fewer than ~200 sequences (row reading)")

    # ---- mapping
    site_cols, _ = map_sites_primary(n3, s3, query)
    used = "primary (query-identical rows in iteration-3 MSA)"
    if site_cols is None:
        print("primary mapping unavailable -> crosswalk fallback")
        site_cols = map_sites_crosswalk(n1, s1, n3, s3, query)
        used = "crosswalk (iteration-1 -> iteration-3 via shared proteins)"
        if site_cols is None:
            fail("M2: crosswalk could not map all four sites")
    M = encode(s3)
    gate_m3(M, site_cols)
    print(f"mapping path: {used}")
    order = sorted(GB1_SITES)
    print("columns:", {k: site_cols[k] for k in order})

    # ---- coupling on PRIMARY set
    frob, mi, gates = mfdca(M)
    print("gates:", {k: (f"{v:.3e}" if isinstance(v, float) else v)
                     for k, v in gates.items()})
    if gates["C_symmetry_max_err"] > 1e-9:
        fail("covariance not symmetric")
    if gates["inversion_residual_max"] > 1e-6:
        fail("inversion residual too large")
    print("identity checks: C symmetry and C_reg @ C_inv = I both within limits")

    # ---- sensitivity arm: first row per accession (pre-registered)
    seen, keep = set(), []
    for i, nm in enumerate(n3):
        a = nm.split("/")[0]
        if a not in seen:
            seen.add(a)
            keep.append(i)
    Md = M[keep]
    print(f"SENSITIVITY arm: {len(keep)} rows (first per accession)")
    frob_d, mi_d, gates_d = mfdca(Md)
    print("sensitivity gates:", {k: (f"{v:.3e}" if isinstance(v, float) else v)
                                 for k, v in gates_d.items()})

    # ---- report the six pairs
    rows = []
    print()
    print(f"{'pair':>10} {'cols':>10} {'S_ij (N=%d)' % n_rows:>14} "
          f"{'S_ij (N=%d)' % len(keep):>14} {'MI (secondary)':>15}")
    for a, b in PAIRS:
        i, j = site_cols[a], site_cols[b]
        rows.append({
            "site1": a, "site2": b, "col1": i, "col2": j,
            "frob_primary": float(frob[i, j]),
            "frob_dedup": float(frob_d[i, j]),
            "mi_secondary": float(mi[i, j]),
        })
        print(f"{a:>4},{b:<5} {i:>4},{j:<5} {frob[i, j]:>14.6f} "
              f"{frob_d[i, j]:>14.6f} {mi[i, j]:>15.6f}")

    rank_p = [p for _, p in sorted(((r["frob_primary"], (r['site1'], r['site2'])) for r in rows), reverse=True)]
    rank_d = [p for _, p in sorted(((r["frob_dedup"], (r['site1'], r['site2'])) for r in rows), reverse=True)]
    if rank_p != rank_d:
        print(f"NOTE: rank order of the six pairs DIFFERS between arms\n"
              f"  primary : {rank_p}\n"
              f"  dedup   : {rank_d}\n"
              f"  (both carried into T3)")
    else:
        print(f"rank order identical across arms: {rank_p}")

    os.makedirs("data/processed", exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {OUT_CSV}")

    # ---- limitations printed by the script itself (AGENTS.md §6)
    print()
    print("LIMITATIONS (printed by design):")
    print(" - MSA = iteration-3 jackhmmer output; the 5-iteration rerun "
          "stalled server-side and was abandoned (see SESSION_LOG T2).")
    print(" - Rows include tandem multi-copy domains from the same protein "
          "(566 rows / 180 distinct accessions): rows are not independent; "
          "no sequence re-weighting was applied (pre-registered); "
          "effective N is smaller than the row count.")
    print(" - Under the distinct-accession reading of T2c (180 < ~200) the "
          "gate is NOT met; results proceed under the row-count reading "
          "(566 >= 200) — the assumption is logged in SESSION_LOG T2 and "
          "the deduplicated arm is reported alongside.")
    print(" - mfDCA at 61 columns x 566 rows is regularized (lambda = "
          f"{gates['lambda']:.4f}); cond(C_reg) = {gates['cond_C']:.3e}.")
    print(" - Coupling magnitudes are NOT significance statements; agreement "
          "with measured epsilon is Task T3 (n = 6 pairs, no meaningful "
          "bootstrap CI possible at n=6).")
    print(" - MI column is a SECONDARY diagnostic only (association, not "
          "direct coupling); no claim rests on it.")


if __name__ == "__main__":
    main()
