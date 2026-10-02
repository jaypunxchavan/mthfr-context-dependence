#!/usr/bin/env python3
"""Script 164 (Phase 3a session 3a, task A5d) -- the frozen RBD roster,
drawn and hashed before any RBD score exists.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Task A5d under the frozen
prereg/RBD_REPLICATION_PREREG_v1.md section 4 ("Backgrounds"), quoted
verbatim:

  (4) "For each target T: Arm S_T = the 18 other substitutions at T's
      site (not the wild type, not T's own substitution). Arm V_T = T's
      substitution type (N to Y for N501Y; E to K for E484K) at every
      other site of the construct with the same wild-type residue; if
      more than 60, a seed-0 sample of 40. Arm G (shared by both
      targets) = 40 backgrounds, each a single substitution at a
      distinct site, drawn with numpy.random.default_rng(0), site
      uniform among the construct's sites excluding 484 and 501, mutant
      uniform among the 19 non-wild-type residues. The null set for T is
      N_T = V_T u G; the OTHER target's background is excluded from N_T.
      The two target backgrounds are scored. The roster is written and
      hashed before scoring, and ordered by interleaving the arms
      round-robin so that any completed prefix is balanced."

NO MODEL IS LOADED.  No torch, no esm, no network, nothing scored.

INPUTS (recomputed independently and printed beside every target; a
mismatch is a STOP, never a rewrite of the target):
  data/external/rbd_starr2022/RBD_sites.csv             201 sites, 331..531
  data/external/rbd_starr2022/wildtype_sequence.fasta   603 nt -> 201 aa
  data/external/rbd_starr2022/final_variant_scores.csv  Wuhan wildtype column
  output: data/processed/phase3/rbd/roster_v1.csv (+ its sha256)

PRE-REGISTERED DECISIONS (fixed in this docstring before the first run):
  D1  "The construct's sites" = the 201 contiguous sites 331..531 of
      RBD_sites.csv (established in A5b, gate G-R2).  Verified at run
      time three independent ways (G-164-1): (a) every site's
      `amino_acid` equals the Wuhan-Hu-1 `wildtype` column of
      final_variant_scores.csv; (b) translating wildtype_sequence.fasta
      (603 nt, 201 codons, no in-frame stop) equals both; (c) every site
      carries all 20 letters as mutants in the data, so all 19
      non-wild-type residues exist at every site.
  D2  Arm V sampling branch: candidate sites are counted first; the
      frozen "if more than 60, a seed-0 sample of 40" applies only above
      60.  The sampling branch is implemented as a FRESH
      numpy.random.default_rng(0) for that arm doing
      .choice(sorted_sites, 40, replace=False), arm order = draw order.
      Which branch was taken is printed either way; if keep-all was
      taken, the sampling code is not exercised (stated as such, not
      silently skipped).
  D3  Arm G draw, from a FRESH numpy.random.default_rng(0) for the G
      draw: sites = sorted(the 199 construct sites excluding 484 and
      501); rng.choice(sites, 40, replace=False) -- uniform over
      40-subsets and the only reading of "distinct site" that yields
      exactly that; then, in draw order, mutant = sorted(the 19
      non-wild-type residues at that site)[rng.integers(19)].  The whole
      draw is rebuilt a second time from a fresh seed-0 RNG inside the
      run and must be identical (G-164-4).
  D4  Within-arm order before interleaving: TARGET in frozen order
      (N501Y, E484K); S_T ascending mutant letter (all one site); V_T
      ascending site (keep-all branch); G in draw order.
  D5  Physical deduplication: the roster carries ONE row per distinct
      (site, mutant), because that is one scoring unit.  If the G draw
      lands on a substitution already in a V arm, the row keeps the
      earlier arm's id (cycle order puts V before G) and its `arms`
      column records both memberships.  Both numbers are printed: G
      drawn (frozen: 40) and G's roster rows after unification.  Null
      sets are set unions, so |N_T| is computed from the union and never
      by adding arm sizes together.
  D6  Round-robin interleave over the fixed arm cycle
      [TARGET, S_N501Y, S_E484K, V_N501Y, V_E484K, G], taking one entry
      per non-exhausted arm per pass over disjoint arm lists (D5
      resolved before interleaving).  The balanced-prefix property is
      gated (G-164-7).  Roster order decides only the order in which
      independent per-background scores are produced; no statistic is
      computed here, so order cannot affect any result.
  D7  Null-set membership flags: in_null_N501Y = V_N501Y u G,
      in_null_E484K = V_E484K u G; targets and S arms belong to neither;
      the other target's background is excluded from N_T (checked, not
      assumed).
  D8  The Wuhan-Hu-1 reference is NOT a roster row: script 156 scores it
      as the WT arm over all 201 construct sites (frozen 3 needs
      S(v | Wuhan) at every site).  Each roster background is scored at
      201 - 1 = 200 positions -- the background's own site excluded, the
      A4c design carried over -- so expected coverage is 200/201 =
      99.50%, above G-R4's 95% floor.  Expected passes are printed.
  D9  roster_v1.csv is written and re-read inside this run, and the
      script asserts that data/processed/phase3/rbd/ holds no bg_*.csv
      and no wt_arm.csv at run time: the roster is hashed strictly
      before any scoring exists.

GATES (a failed gate prints FAIL and exits 3; thresholds are never
loosened, N is never raised):
  G-164-1  reference chain (D1): three derivations agree, 0 mismatches.
  G-164-2  arm S_T: exactly 18 per target (frozen "the 18 other
           substitutions"), all at T's site, mutant != Wuhan residue,
           mutant != T's own substitution, every mutant present in the
           data for that site.
  G-164-3  arm V_T: every site's Wuhan residue equals T's wild-type
           residue, the substitution equals T's (N->Y / E->K), site !=
           T's own site, count == candidate count, branch reported.
  G-164-4  arm G: 40 entries, 40 distinct sites, no 484 and no 501,
           mutant != Wuhan residue at that site, second fresh seed-0
           draw identical.
  G-164-5  null sets: the roster's in_null_T flags equal V_T u G exactly;
           no target and no S arm in any N_T; the OTHER target's
           background not in N_T.
  G-164-6  roster integrity: one row per (site, mutant), unique ids,
           wt_aa == Wuhan residue at that site, every (site, mutant)
           exists in the data, required columns present, whole roster
           rebuilt from scratch and identical.
  G-164-7  balanced prefix: at every prefix, the counts of the
           not-yet-exhausted arms differ by <= 1.
  G-164-8  roster written, hashed, re-read (sha256 stable), nothing
           scored yet, pass arithmetic printed.

LIMITATIONS (AGENTS 6, printed at the end of every run):
  * this script draws and hashes; it computes no statistic, no p-value
    and no outcome word of any frozen block.
  * roster order is a fairness device for a stage that its budget may cut
    short; it is not a statistical property and confers no benefit.
  * counts are of backgrounds (rows), not of independent positions; the
    position-cluster machinery that needs that distinction is A5g's.
  * the arm sizes are set by the frozen block and by the reference
    sequence; nothing here is chosen after seeing any score (no score
    exists).
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
ROSTER = OUT_DIR / "roster_v1.csv"

ALPHABET = sorted("ACDEFGHIKLMNPQRSTVWY")
SITES = list(range(331, 532))                 # D1: 201 construct sites
TARGETS = ["N501Y", "E484K"]                  # frozen order
T_SITE = {"N501Y": 501, "E484K": 484}
T_SUB = {"N501Y": ("N", "Y"), "E484K": ("E", "K")}
G_EXCLUDE = (484, 501)                        # frozen 4
N_G = 40                                      # frozen 4
V_THRESHOLD, V_SAMPLE_N = 60, 40              # frozen 4 ("more than 60")
SEED = 0
CYCLE = ["TARGET", "S_N501Y", "S_E484K", "V_N501Y", "V_E484K", "G"]   # D6
WT_PASSES = 201                               # D8: WT arm, all construct sites
BG_PASSES = 200                               # D8: 201 - own site
G_R4_FLOOR = 0.95                             # frozen 7

CODON_TABLE = {}
for _i, _b in enumerate("TCAG"):
    for _j, _c in enumerate("TCAG"):
        for _k, _d in enumerate("TCAG"):
            CODON_TABLE[_b + _c + _d] = (
                "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVV"
                "AAAADDEEGGGG")[_i * 16 + _j * 4 + _k]

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}")


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def translate_fasta(path):
    txt = "".join(l.strip() for l in path.read_text().splitlines()
                  if not l.startswith(">"))
    assert len(txt) % 3 == 0, len(txt)
    prot = "".join(CODON_TABLE[txt[i:i + 3].upper()]
                   for i in range(0, len(txt), 3))
    return txt, prot


def build_arms(seq, verbose=True):
    """Build the six raw arms (D2-D4).  Returns (raw_arms, meta)."""
    raw, meta = {}, {}

    # TARGET (frozen: "The two target backgrounds are scored")
    raw["TARGET"] = [dict(id=f"TGT_{t}", site=T_SITE[t], wt=seq[T_SITE[t]],
                          mut=T_SUB[t][1]) for t in TARGETS]

    for t in TARGETS:
        site, (wt0, sub) = T_SITE[t], T_SUB[t]

        # Arm S_T: the 18 other substitutions at T's site
        muts = [m for m in ALPHABET if m not in (wt0, sub)]
        raw[f"S_{t}"] = [dict(id=f"S{site}{m}", site=site, wt=seq[site],
                              mut=m) for m in sorted(muts)]

        # Arm V_T: T's substitution at every other site with same WT residue
        cand = sorted(p for p in SITES if seq[p] == wt0 and p != site)
        if len(cand) > V_THRESHOLD:
            rng = np.random.default_rng(SEED)          # fresh per arm (D2)
            chosen = [int(p) for p in rng.choice(np.array(cand),
                                                 size=V_SAMPLE_N,
                                                 replace=False)]
            branch = (f"candidates {len(cand)} > {V_THRESHOLD} -> seed-0 "
                      f"sample of {V_SAMPLE_N}, draw order kept")
        else:
            chosen = list(cand)
            branch = (f"candidates {len(cand)} <= {V_THRESHOLD} -> "
                      f"keep-all (the seed-0 sampling branch of D2 was "
                      f"NOT taken)")
        raw[f"V_{t}"] = [dict(id=f"V{p}{sub}", site=p, wt=seq[p], mut=sub)
                         for p in chosen]
        meta[f"V_{t}"] = dict(candidates=len(cand), chosen=len(chosen),
                              branch=branch, cand_sites=cand)

    # Arm G (D3)
    cand_sites = sorted(p for p in SITES if p not in G_EXCLUDE)

    def draw_g():
        rng = np.random.default_rng(SEED)              # fresh for G (D3)
        sites = [int(p) for p in rng.choice(np.array(cand_sites),
                                            size=N_G, replace=False)]
        out = []
        for p in sites:
            muts = sorted(m for m in ALPHABET if m != seq[p])
            m = muts[int(rng.integers(0, 19))]
            out.append(dict(id=f"G{p}{m}", site=p, wt=seq[p], mut=m))
        return out

    g1 = draw_g()
    g2 = draw_g()
    raw["G"] = g1
    meta["G"] = dict(candidates=len(cand_sites), d1=g1, d2=g2)
    return raw, meta


def interleave(raw):
    """D5 (unification) + D6 (round-robin over disjoint arm lists)."""
    members = {}                      # (site, mut) -> [arm, ...] in CYCLE order
    for arm in CYCLE:
        for e in raw[arm]:
            members.setdefault((e["site"], e["mut"]), []).append(arm)
    primary = {k: v[0] for k, v in members.items()}
    lists = {a: [e for e in raw[a] if primary[(e["site"], e["mut"])] == a]
             for a in CYCLE}
    rows, ptr = [], {a: 0 for a in CYCLE}
    while True:
        added = False
        for a in CYCLE:
            if ptr[a] < len(lists[a]):
                e = lists[a][ptr[a]]
                ptr[a] += 1
                added = True
                rows.append((a, e))
        if not added:
            break
    return rows, members, primary, lists


def make_frame(rows, members, seq, nset):
    recs = []
    for i, (arm, e) in enumerate(rows, start=1):
        key = (e["site"], e["mut"])
        arms = members[key]
        if arms[0] == "TARGET":
            tgt = e["id"].replace("TGT_", "")
        elif arms[0] == "G":
            tgt = "shared"
        elif arms[0] in ("S_N501Y", "V_N501Y"):
            tgt = "N501Y"
        else:
            tgt = "E484K"
        recs.append({
            "roster_order": i,
            "background_id": e["id"],
            "arm": arms[0],
            "arms": ";".join(arms),
            "site": e["site"],
            "wt_aa": seq[e["site"]],
            "mutant": e["mut"],
            "target_assoc": tgt,
            "is_target": arms[0] == "TARGET",
            "in_null_N501Y": key in nset["N501Y"],
            "in_null_E484K": key in nset["E484K"],
            "n_scored_positions": BG_PASSES,
        })
    return pd.DataFrame(recs)


def main():
    t0 = time.time()
    print("PHASE 3a Task A5d -- RBD roster (frozen "
          "RBD_REPLICATION_PREREG_v1.md section 4)")
    print("No torch/esm/no model.  Nothing is scored: the roster is "
          "written and hashed before any score exists (frozen 4).")

    # ---- reference chain (D1) --------------------------------------------
    rule("REFERENCE CHAIN -- the construct's sites and residues (D1)")
    sites = pd.read_csv(EXT / "RBD_sites.csv")
    scores = pd.read_csv(EXT / "final_variant_scores.csv",
                         usecols=["target", "position", "wildtype", "mutant"])
    _, prot = translate_fasta(EXT / "wildtype_sequence.fasta")
    wu = (scores[scores["target"] == "Wuhan-Hu-1"]
          .drop_duplicates("position").sort_values("position"))
    data_seq = dict(zip(wu.position, wu.wildtype))
    rbd_seq = dict(zip(sites.site, sites.amino_acid))
    fasta_seq = {s: prot[i] for i, s in enumerate(SITES)}

    mm_a = [(p, rbd_seq.get(p), data_seq.get(p)) for p in SITES
            if rbd_seq.get(p) != data_seq.get(p)]
    mm_b = [(p, fasta_seq.get(p), rbd_seq.get(p)) for p in SITES
            if fasta_seq.get(p) != rbd_seq.get(p)]
    alph = scores[scores["target"] == "Wuhan-Hu-1"].groupby(
        "position").mutant.apply(lambda s: sorted(s))
    bad_alph = [p for p in SITES if list(alph[p]) != ALPHABET]
    print(f"  RBD_sites.csv: {len(sites)} rows, sites "
          f"{sites.site.min()}..{sites.site.max()}, contiguous "
          f"{list(sites.site) == SITES}")
    print(f"  wildtype_sequence.fasta: {len(prot)} aa (603 nt / 3), "
          f"in-frame stops {prot.count('*')}")
    print(f"  data Wuhan wildtype: {len(data_seq)} sites")
    print(f"  derivation (i) RBD_sites vs data: {len(mm_a)} mismatches")
    print(f"  derivation (ii) fasta translation vs RBD_sites: "
          f"{len(mm_b)} mismatches")
    print(f"  derivation (iii) sites lacking the full 20-letter mutant "
          f"set: {len(bad_alph)}")
    seq = rbd_seq
    gate("G-164-1 reference chain: three derivations of the construct "
         "agree", "PASS" if not (mm_a or mm_b or bad_alph) else "FAIL",
         f"201 sites 331..531, mismatches {len(mm_a)}/{len(mm_b)}, "
         f"sites missing an alphabet {len(bad_alph)}",
         "RBD_sites == data == translated fasta")
    if mm_a or mm_b or bad_alph:
        sys.exit(3)

    # ---- arms (D2-D4) -----------------------------------------------------
    rule("ARMS (frozen 4) -- drawn, never chosen; counts printed")
    raw, meta = build_arms(seq)
    for a in CYCLE:
        print(f"  {a:<11} drawn {len(raw[a]):>3}")
    for t in TARGETS:
        m = meta[f"V_{t}"]
        print(f"  V_{t} branch: {m['branch']}")
    print(f"  G candidate sites: {meta['G']['candidates']} (201 - 484 - 501)")

    ok_s = all(len(raw[f"S_{t}"]) == 18 for t in TARGETS)
    s_detail = []
    for t in TARGETS:
        site, (wt0, sub) = T_SITE[t], T_SUB[t]
        ents = raw[f"S_{t}"]
        good = (all(e["site"] == site for e in ents)
                and all(e["mut"] != wt0 for e in ents)
                and all(e["mut"] != sub for e in ents)
                and all(e["mut"] in ALPHABET for e in ents)
                and all(e["mut"] in set(alph[site]) for e in ents))
        s_detail.append(f"{t}: n={len(ents)} site={site} all_valid={good}")
        ok_s &= good and len(ents) == 18
    gate("G-164-2 arm S_T = the 18 other substitutions at T's site",
         "PASS" if ok_s else "FAIL", "; ".join(s_detail),
         "frozen: not the wild type, not T's own substitution")

    ok_v = True
    v_detail = []
    for t in TARGETS:
        wt0, sub = T_SUB[t]
        m = meta[f"V_{t}"]
        good = (m["chosen"] == m["candidates"]
                and all(e["wt"] == wt0 and e["mut"] == sub
                        and e["site"] != T_SITE[t] for e in raw[f"V_{t}"]))
        ok_v &= good
        v_detail.append(f"{t}: {m['chosen']}/{m['candidates']} valid={good}")
    gate("G-164-3 arm V_T = T's substitution at other same-WT-residue sites",
         "PASS" if ok_v else "FAIL", "; ".join(v_detail),
         "candidates are counted, not sampled, below the frozen threshold "
         "of 60; branch printed above")

    g1, g2 = meta["G"]["d1"], meta["G"]["d2"]
    g_ok = (len(g1) == N_G
            and len({e["site"] for e in g1}) == N_G
            and all(e["site"] not in G_EXCLUDE for e in g1)
            and all(e["mut"] != e["wt"] for e in g1)
            and all(e["mut"] in ALPHABET for e in g1)
            and g1 == g2)
    gate("G-164-4 arm G: 40 backgrounds, distinct sites, seed-0 reproducible",
         "PASS" if g_ok else "FAIL",
         f"{len(g1)} entries, {len({e['site'] for e in g1})} distinct sites, "
         f"excluded sites present "
         f"{sorted({e['site'] for e in g1} & set(G_EXCLUDE))}, "
         f"second fresh default_rng(0) draw identical = {g1 == g2}",
         "site uniform over 199, mutant uniform over 19 (D3)")

    # ---- null sets (D7) + unification (D5) -------------------------------
    rule("NULL SETS N_T = V_T u G (frozen 4) and roster unification (D5)")
    Gset = {(e["site"], e["mut"]) for e in raw["G"]}
    Vset = {t: {(e["site"], e["mut"]) for e in raw[f"V_{t}"]} for t in TARGETS}
    Nset = {t: Vset[t] | Gset for t in TARGETS}
    rows, members, primary, lists = interleave(raw)
    overlap = {t: sorted(Vset[t] & Gset) for t in TARGETS}
    for t in TARGETS:
        other = [x for x in TARGETS if x != t][0]
        print(f"  N_{t}: |V_{t}| = {len(Vset[t])}, |G| = {len(Gset)}, "
              f"|V_T & G| = {len(overlap[t])} -> |N_{t}| = "
              f"{len(Nset[t])} (set union, never a sum of arm sizes)")
        if overlap[t]:
            print(f"      overlap with G (D5: row keeps the V id, "
                  f"arms records both): {overlap[t]}")
        print(f"      other target's background "
              f"({other} at {T_SITE[other]}{T_SUB[other][1]}) in "
              f"N_{t}: {(T_SITE[other], T_SUB[other][1]) in Nset[t]}")

    # membership flags on the frame are checked against the frozen union
    null_ok = True
    for t in TARGETS:
        other = [x for x in TARGETS if x != t][0]
        null_ok &= not ((T_SITE[other], T_SUB[other][1]) in Nset[t])
        null_ok &= not any((T_SITE[x], T_SUB[x][1]) in Nset[t]
                           for x in TARGETS)
        for tt in TARGETS:
            s_keys = {(e["site"], e["mut"]) for e in raw[f"S_{tt}"]}
            null_ok &= not (s_keys & Nset[t])
    gate("G-164-5 null sets: N_T == V_T u G, targets and S arms excluded, "
         "other target's background excluded",
         "PASS" if null_ok else "FAIL",
         "; ".join(f"|N_{t}|={len(Nset[t])}" for t in TARGETS),
         "checked as set identities, not assumed")

    # ---- frame (D6) -------------------------------------------------------
    df = make_frame(rows, members, seq, Nset)
    rule("ROSTER (written at the end of this run, D9) -- first 12 rows")
    print(df.head(12).to_string(index=False))

    # ---- G-164-6 integrity ------------------------------------------------
    data_pairs = set(zip(scores.position, scores.mutant))
    keys = list(zip(df.site, df.mutant))
    rebuilt = make_frame(*interleave(raw)[:2], seq, Nset)
    cols_ok = list(df.columns) == [
        "roster_order", "background_id", "arm", "arms", "site", "wt_aa",
        "mutant", "target_assoc", "is_target", "in_null_N501Y",
        "in_null_E484K", "n_scored_positions"]
    i6 = (len(keys) == len(set(keys))
          and df.background_id.is_unique
          and (df.wt_aa.values == df.site.map(seq).values).all()
          and set(keys) <= data_pairs
          and cols_ok
          and df.equals(rebuilt))
    gate("G-164-6 roster integrity (unique rows/ids, residues, data "
         "membership, rebuild)",
         "PASS" if i6 else "FAIL",
         f"{len(df)} rows, {len(set(keys))} unique (site, mutant), "
         f"{df.background_id.nunique()} unique ids, wt_aa mismatches "
         f"{int((df.wt_aa.values != df.site.map(seq).values).sum())}, "
         f"pairs absent from the data {len(set(keys) - data_pairs)}, "
         f"columns ok {cols_ok}, rebuild identical {df.equals(rebuilt)}",
         "one row per physical background (D5)")

    # ---- G-164-7 balanced prefix -----------------------------------------
    totals = df.arm.value_counts().to_dict()
    counts = {a: 0 for a in CYCLE}
    worst = 0
    bad_k = None
    for k, a in enumerate(df.arm, start=1):
        counts[a] += 1
        active = [x for x in CYCLE if counts[x] < totals.get(x, 0)]
        if len(active) >= 2:
            spread = max(counts[x] for x in active) - min(
                counts[x] for x in active)
            if spread > worst:
                worst = spread
            if spread > 1 and bad_k is None:
                bad_k = k
    gate("G-164-7 balanced prefix: counts of not-yet-exhausted arms differ "
         "by <= 1 at every prefix",
         "PASS" if bad_k is None else "FAIL",
         f"max spread observed {worst} over {len(df)} positions "
         f"(first violation at prefix {bad_k})",
         "round-robin over the fixed cycle "
         + " > ".join(CYCLE))

    # ---- counts per arm, null sizes, expected passes ----------------------
    rule("COUNTS PER ARM AND EXPECTED PASSES (A5d report)")
    print(f"  {'arm':<11} {'drawn':>6} {'roster rows':>12}")
    for a in CYCLE:
        print(f"  {a:<11} {len(raw[a]):>6} {int((df.arm == a).sum()):>12}")
    print(f"  {'TOTAL':<11} {sum(len(raw[a]) for a in CYCLE):>6} "
          f"{len(df):>12}   "
          f"(memberships {sum(len(raw[a]) for a in CYCLE)} - "
          f"unified duplicates "
          f"{sum(len(raw[a]) for a in CYCLE) - len(df)})")
    for t in TARGETS:
        print(f"  |N_{t}| = {len(Nset[t])} "
              f"(V {len(Vset[t])} u G {len(Gset)}; "
              f"overlap {len(Vset[t] & Gset)})")
    n_bg = len(df)
    total_passes = WT_PASSES + BG_PASSES * n_bg
    print(f"  WT arm passes: {WT_PASSES} (all construct sites, D8)")
    print(f"  background passes: {n_bg} backgrounds x {BG_PASSES} "
          f"(201 sites - own site) = {BG_PASSES * n_bg}")
    print(f"  EXPECTED PASSES for the stage: {total_passes}")
    print(f"  expected site coverage per background: "
          f"{BG_PASSES}/201 = {BG_PASSES / 201:.2%} vs G-R4 floor "
          f"{G_R4_FLOOR:.0%}")

    # ---- G-164-8 write, hash, re-read, nothing scored ---------------------
    rule("WRITE + HASH BEFORE ANY SCORING (frozen 4, D9)")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    strays = sorted([p.name for p in OUT_DIR.glob("bg_*.csv")]
                    + [p.name for p in OUT_DIR.glob("wt_arm*.csv")])
    df.to_csv(ROSTER, index=False)
    h1 = hashlib.sha256(ROSTER.read_bytes()).hexdigest()
    back = pd.read_csv(ROSTER)
    h2 = hashlib.sha256(ROSTER.read_bytes()).hexdigest()
    print(f"  wrote {ROSTER.relative_to(ROOT)}: {len(back)} rows, "
          f"sha256 {h1}")
    print(f"  re-read: {len(back)} rows, sha256 {h2} "
          f"(stable = {h1 == h2}); pre-existing score files: {strays}")
    print(f"  expected passes written into the record: {total_passes}")
    ok8 = (h1 == h2 and not strays and len(back) == n_bg
           and back.equals(df))
    gate("G-164-8 roster written, hashed, re-read; nothing scored yet",
         "PASS" if ok8 else "FAIL",
         f"sha256 stable {h1 == h2}, stray score files {len(strays)}, "
         f"rows in == rows out {len(back) == n_bg}, frame identical "
         f"{back.equals(df)}",
         "hashed strictly before any scoring exists")

    # ---- summary ----------------------------------------------------------
    rule("SUMMARY -- A5d")
    n_pass = 0
    for name, verdict, value, note in GATES:
        print(f"  [{verdict}] {name}: {value}  {note}")
        n_pass += verdict == "PASS"
    ok = n_pass == len(GATES)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS -> "
          f"{'A5d PASSES' if ok else 'A5d FAILS'}")
    print(f"  roster_v1.csv sha256 {h1}")
    print("\n  LIMITATIONS (AGENTS 6):")
    print("    * draws and hashes only: no statistic, no p-value and no "
          "outcome word of any frozen block")
    print("    * roster order is a fairness device for a budgeted stage, "
          "not a statistical property")
    print("    * rows are backgrounds, not independent positions; "
          "position clustering is A5g's")
    print("    * arm sizes come from the frozen block and the reference "
          "sequence; no score existed when they were fixed")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    if not ok:
        sys.exit(3)


if __name__ == "__main__":
    main()
