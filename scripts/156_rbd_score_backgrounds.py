#!/usr/bin/env python3
"""Script 156 (Phase 3a session 3a, task A5e) -- RBD background scorer,
including HARD gate G-R5.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Task A5e under the frozen
prereg/RBD_REPLICATION_PREREG_v1.md sections 2, 3, 6 and 7, quoted
verbatim where they bind this script:

  (2) "S = ESM-2 650M masked-marginal log-odds against the wild-type
      residue, one unbatched forward pass per (background, site), over
      the RBD construct's sites."
  (6) "G-R4 each background scores at least 95% of the construct's
      eligible sites.  G-R5 scoring the same background twice gives
      identical values (1e-6) and the wild-type residue's log-odds is 0
      at every scored site."
  (7) the roster "is written and hashed before scoring" (done in A5d,
      sha256 70a6305d24b753655e92f10f413115381a84721998300440b5d48f8eec87b2fb).

Same design as A4c (scripts/154), ported to the RBD sequence: atomic
one-file-per-background writes, resume-by-skip, manifest, own site
excluded from a background's own passes, WT arm over every construct
site.  Session 3a runs only G-R5 (--g-r5) and the A5f timing smoke
(scratch out-dir); the full 100-background stage is run by the A7 driver
overnight, not here.

MACHINERY, SHARED NOT REIMPLEMENTED: scoring goes through
scripts/lib/esm_scoring.py::get_position_logprobs + get_device exactly
as scripts 73/124/154 -- ESM-2 esm2_t33_650M_UR50D, eval mode, one
UNBATCHED forward pass per (background, position), all 19 non-wild-type
substitutions from that pass.  The checkpoint is CHECKED for existence
and byte size before loading and the script exits 3 if it is missing
(never downloads).

PRE-REGISTERED DECISIONS (fixed here before the first run):
  S1  The scored sequence is the 201-aa RBD construct itself:
      wildtype_sequence.fasta (603 nt -> 201 codons, no in-frame stop),
      gated at run time against RBD_sites.csv and against the data's
      Wuhan wildtype column (three-way, G-156-1).  Construct position
      i (1-based) = site SITE0 + i - 1 with SITE0 = 331, so the file's
      `position` (what the model masked) and `site` (the data's own
      numbering, what e_T is keyed by) are both carried.  No flanking
      context is added: the frozen block says "over the RBD construct's
      sites" and the data's reference is exactly these 201 residues.
  S2  Passes: WT arm = all 201 construct positions; background b = the
      201 positions EXCLUDING b's own site (the A4c design carried over
      and pre-registered in script 164's D8) -> 200 passes per
      background, coverage 200/201 = 99.50% against G-R4's 95% floor.
      A background's own site never appears in its own file.
  S3  G-R5 is a MODE of this script (--g-r5), run once in this session
      and re-run by the A7 driver before the stage.  It checks, on the
      reference at all 201 positions and on one full roster background
      at all 200 of its positions (both sequence contexts the stage
      uses):
        (a) determinism -- the same background scored twice, every
            (position, mut_aa) value compared: max|diff| <= 1e-6;
        (b) the wild-type residue's log-odds == 0 at every scored
            position, computed by an INDEPENDENT inline re-derivation
            (mask, forward pass, log_softmax, subtract that position's
            own wild-type log-prob) which must also reproduce the
            library's 19 values to 1e-6.  The zero itself is an
            arithmetic identity once (b)'s cross-check holds -- the
            library source line is quoted in the output so the identity
            is visible rather than asserted.
        Both sequence contexts share the property that the background's
        own site is never scored, so at every scored position the
        background residue EQUALS the reference residue: "the wild-type
        residue" is unambiguous there (asserted, not assumed).
  S4  The `sequence` column carries a 16-hex sha256 DIGEST of the
      201-aa sequence actually scored (WT arm: the reference).  A4c
      stored a sequence label because two sequences shared one roster;
      here every background has its own sequence and the skip gate must
      catch a file written for a different background or a different
      reference, so the column is keyed to the sequence bytes.  Full
      sequences are reconstructible from the reference + roster row
      (printed by this script).
  S5  One out-dir, default data/processed/phase3/rbd (the same directory
      as roster_v1.csv and e_T.csv, which are input to the analysis
      stage, not to this one).  Scratch out-dirs are used by the A5f
      timing smoke so the real directory holds no score until the
      driver runs it.

OUTPUT CONTRACT (one file per background, written ONLY after all its
positions are done, ATOMICALLY):
  rows in memory -> <out-dir>/.bg_<bg_id>.csv.tmp -> os.replace() ->
  <out-dir>/bg_<bg_id>.csv (WT arm: wt_arm.csv).
  Columns: bg_id, sequence, site, position, mut_aa, score.
  Integrity asserted BEFORE the rename (G-156-4): rows == 19 x
  n_positions, unique (site, position, mut_aa), position set == the
  expected one (own site absent for backgrounds, all 201 for the WT
  arm), bg_id as expected, sequence digest as expected, and every
  scored position's residue equal between background and reference (S3).
  After each published file: append file, kind, bg_id, sequence,
  n_positions, n_rows, seconds, median_pass_s, device to
  <out-dir>/manifest.csv (header if new; skipped files append nothing).
  Any exception: current .tmp removed, traceback + ERROR printed,
  exit 1 (never continues past a half-written file).

SKIP/RESUME (frozen 7): a final file counts as done only if it exists
with the expected row count, expected position set, no duplicates,
expected bg_id AND expected sequence digest.  A .tmp NEVER counts.
Because the roster order is the frozen interleaved order (script 164,
D6), any completed prefix of an interrupted stage is arm-balanced.

CLI:
  --only BG_ID       score/skip just that roster id (repeatable)
  --limit-positions N  first N expected positions (sorted); row
                     expectation becomes N x 19; a file written with
                     this flag is INCOMPLETE for a later full run and
                     will be re-scored then -- by design; test/timing use
  --out-dir DIR      default data/processed/phase3/rbd
  --limit-roster N   only the first N roster rows in roster order
  --wt-arm-only      score/skip only the WT arm
  --inputs-only      run the input gates (G-156-1/2/3/6) and exit
                     without loading the model -- pre-flight check
  --g-r5 [BG_ID]     run HARD gate G-R5 (default background TGT_N501Y,
                     roster row 1) and exit; writes nothing

GATES (failed gate -> message + exit 3; thresholds never loosened):
  G-156-1 reference: three file sha256 pins (fasta, RBD_sites.csv,
          final_variant_scores.csv), 201 codons with no in-frame stop,
          and three-way residue agreement over all 201 sites.
  G-156-2 roster: sha256 pin 70a6305d..., 100 rows / 100 unique ids,
          site in 331..531, wt_aa == reference residue at that site,
          mut != wt, every (site, mut) present in the data, every
          n_scored_positions == 200 (S2).
  G-156-3 local ESM-2 650M checkpoint exists with the pinned byte size
          (never downloads).
  G-156-4 per-file integrity before the atomic rename (see contract) +
          background-sequence asserts (S1/PIN-6 pattern: wt asserted
          before substitution, mut asserted after).
  G-156-5 G-R4 echo: coverage = positions scored / 201 >= 0.95 for
          every file written or skipped in this run (frozen floor).
  G-156-6 out-dir consistency: no bg_<id>.csv for an id outside the
          roster, manifest header matches when present.
  G-R5a  determinism: max|diff| between two independent scorings of the
          same background <= 1e-6 (frozen tolerance, never widened).
  G-R5b  wild-type residue log-odds == 0 at every scored position of
          the reference (201) and of the gate background (200), with
          the independent re-derivation matching the library to 1e-6.

CONVENTION: N_BOOT / SEED are read nowhere -- this script performs no
bootstrap, no permutation and no randomness of its own; the only draw
was the roster (script 164, seed 0).
"""

import argparse
import hashlib
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))          # scripts.lib imports (same as 154/155/161)
EXT = ROOT / "data" / "external" / "rbd_starr2022"
ROSTER_PATH = ROOT / "data" / "processed" / "phase3" / "rbd" / "roster_v1.csv"
DEFAULT_OUT = ROOT / "data" / "processed" / "phase3" / "rbd"

FASTA_SHA = ("2a49a444e9d002c82c40d3b5e4a3bc5e4a152c00f5817428803b4368c21c15fb")
RBD_SITES_SHA = ("a35adf4dc5e6bff78ed64dc9daca12580cfe6f891e52c6016e0ffaf6702c5ca3")
SCORES_SHA = ("c0678e8560e745479a896bc56c4744b75e64f1cfd8666fe0715f0855d652ef97")
ROSTER_SHA = ("70a6305d24b753655e92f10f413115381a84721998300440b5d48f8eec87b2fb")
CKPT = (Path.home() / ".cache" / "torch" / "hub" / "checkpoints"
        / "esm2_t33_650M_UR50D.pt")
CKPT_BYTES = 2_604_537_549

SITE0 = 331                 # site of construct position 1 (S1)
N_SITES = 201
ALPHABET = sorted("ACDEFGHIKLMNPQRSTVWY")
WT_ID = "WT"
G_R4_FLOOR = 0.95           # frozen 6
TOL_G_R5 = 1e-6             # frozen 6 (never widened)
DEFAULT_G_R5_BG = "TGT_N501Y"

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


def fail(name, value, note=""):
    gate(name, "FAIL", value, note)
    print("\nGATE FAILED: stopping before any score is written.")
    summary()
    sys.exit(3)


def summary():
    n = sum(v == "PASS" for _, v, _, _ in GATES)
    if GATES:
        print(f"\n  GATES so far: {n}/{len(GATES)} PASS")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seq_digest(seq):
    return hashlib.sha256(seq.encode()).hexdigest()[:16]


def load_reference():
    """G-156-1: three pinned hashes and three-way residue agreement."""
    fasta = EXT / "wildtype_sequence.fasta"
    sites_csv = EXT / "RBD_sites.csv"
    scores_csv = EXT / "final_variant_scores.csv"
    got = [sha(fasta), sha(sites_csv), sha(scores_csv)]
    want = [FASTA_SHA, RBD_SITES_SHA, SCORES_SHA]
    for label, g, w in zip(["wildtype_sequence.fasta", "RBD_sites.csv",
                            "final_variant_scores.csv"], got, want):
        print(f"  {label:<26} sha256 {g}  {'MATCH' if g == w else 'MISMATCH'}")
    hash_ok = got == want

    txt = "".join(l.strip() for l in fasta.read_text().splitlines()
                  if not l.startswith(">"))
    prot = "".join(CODON_TABLE[txt[i:i + 3].upper()]
                   for i in range(0, len(txt), 3))
    sites = pd.read_csv(sites_csv)
    sc = pd.read_csv(scores_csv, usecols=["target", "position", "wildtype",
                                          "mutant"])
    wu = sc[sc.target == "Wuhan-Hu-1"].drop_duplicates("position")
    data_seq = dict(zip(wu.position, wu.wildtype))
    rbd_seq = dict(zip(sites.site, sites.amino_acid))
    site_list = list(range(SITE0, SITE0 + N_SITES))
    mm_rbd = [p for p in site_list if rbd_seq.get(p) != data_seq.get(p)]
    mm_fa = [p for p in site_list
             if (prot[site_list.index(p)] if len(prot) >= N_SITES else None)
             != rbd_seq.get(p)]
    alpha = sc[sc.target == "Wuhan-Hu-1"].groupby("position").mutant.apply(
        lambda s: sorted(s))
    bad_alpha = [p for p in site_list if list(alpha[p]) != ALPHABET]
    ref = "".join(rbd_seq[p] for p in site_list)
    print(f"  fasta: {len(txt)} nt -> {len(prot)} codons, in-frame stops "
          f"{prot.count('*')}; RBD_sites rows {len(sites)}; data Wuhan sites "
          f"{len(data_seq)}")
    print(f"  three-way mismatches: RBD_sites vs data {len(mm_rbd)}, "
          f"translated fasta vs RBD_sites {len(mm_fa)}, sites lacking the "
          f"20-letter mutant set {len(bad_alpha)}")
    ok = (hash_ok and len(prot) == N_SITES and "*" not in prot
          and not mm_rbd and not mm_fa and not bad_alpha
          and list(sites.site) == site_list)
    gate("G-156-1 reference: pinned hashes + 201 codons + three-way "
         "residue agreement",
         "PASS" if ok else "FAIL",
         f"hashes {hash_ok}, codons {len(prot)}, stops {prot.count('*')}, "
         f"mismatches {len(mm_rbd)}/{len(mm_fa)}/{len(bad_alpha)}",
         "S1: the 201-aa construct is the scored sequence")
    if not ok:
        summary()
        sys.exit(3)
    data_pairs = set(zip(sc.position, sc.mutant))
    return ref, data_pairs


def load_roster(ref, data_pairs):
    """G-156-2."""
    h = sha(ROSTER_PATH)
    df = pd.read_csv(ROSTER_PATH)
    checks = {
        "sha256 pin": h == ROSTER_SHA,
        "100 rows": len(df) == 100,
        "unique ids": df.background_id.is_unique,
        "site range": bool(df.site.between(SITE0, SITE0 + N_SITES - 1).all()),
        "wt_aa == reference": bool((df.wt_aa.values
                                    == [ref[p - SITE0] for p in df.site]).all()),
        "mut != wt": bool((df.mutant != df.wt_aa).all()),
        "in data": not (set(zip(df.site, df.mutant)) - data_pairs),
        "n_scored_positions == 200": bool((df.n_scored_positions == 200).all()),
    }
    print(f"  roster_v1.csv sha256 {h}")
    for k, v in checks.items():
        print(f"    {k:<26} {v}")
    ok = all(checks.values())
    gate("G-156-2 roster: pinned hash, structure, residues, data membership",
         "PASS" if ok else "FAIL",
         f"{len(df)} rows, {df.background_id.nunique()} unique ids, all "
         f"checks {ok}", "roster hashed in A5d, before any score")
    if not ok:
        summary()
        sys.exit(3)
    return df


def bg_sequence(ref, row):
    """S1/PIN-6: wt asserted before substitution, mut after."""
    i = int(row.site) - SITE0
    seq = list(ref)
    assert seq[i] == row.wt_aa, (row.background_id, seq[i], row.wt_aa)
    seq[i] = row.mutant
    assert seq[i] != row.wt_aa, row.background_id
    return "".join(seq)


def expected_positions(row_or_none, roster_sites_ok=True):
    """S2: all construct positions except the background's own site."""
    if row_or_none is None:
        return list(range(1, N_SITES + 1))
    own = int(row_or_none.site) - SITE0 + 1
    return [p for p in range(1, N_SITES + 1) if p != own]


def score_positions(model, alphabet, bc, seq_str, digest, bg_id, positions,
                    device, include_wt_zero=False):
    """One unbatched forward pass per position (shared library path).

    When include_wt_zero is set, the wild-type residue's own log-odds is
    computed as well (independent inline re-derivation, S3b) and returned
    in `score_wt` for the caller to check.
    """
    from scripts.lib.esm_scoring import get_position_logprobs
    import torch
    rows, pass_s, wt_vals, cross = [], [], [], []
    for p in positions:
        t0 = time.perf_counter()
        scores = get_position_logprobs(model, alphabet, bc, seq_str, p,
                                       device)
        pass_s.append(time.perf_counter() - t0)
        if include_wt_zero:
            idx0 = p - 1
            wt = seq_str[idx0]
            masked = seq_str[:idx0] + "<mask>" + seq_str[idx0 + 1:]
            _, _, tokens = bc([("query", masked)])
            with torch.no_grad():
                out = model(tokens.to(device), repr_layers=[],
                            return_contacts=False)
            lp = torch.log_softmax(out["logits"][0, idx0 + 1], dim=-1)
            wti = alphabet.get_idx(wt)
            wt_vals.append((p, float(lp[wti] - lp[wti])))
            cross.append(max(abs(float(lp[alphabet.get_idx(aa)] - lp[wti])
                                 - sc) for aa, sc in scores.items()))
        for aa, sc in scores.items():
            rows.append(dict(bg_id=bg_id, sequence=digest,
                             site=p + SITE0 - 1, position=p, mut_aa=aa,
                             score=sc))
    extra = (dict(wt_vals=wt_vals, cross=cross) if include_wt_zero else {})
    return rows, pass_s, extra


def check_file(path, bg_id, digest, positions):
    """Skip gate: complete only if everything matches."""
    if not path.exists():
        return False, "absent"
    try:
        d = pd.read_csv(path)
    except Exception as exc:                      # noqa: BLE001
        return False, f"unreadable ({exc})"
    need_cols = ["bg_id", "sequence", "site", "position", "mut_aa", "score"]
    if list(d.columns) != need_cols:
        return False, "columns"
    if len(d) != 19 * len(positions):
        return False, f"rows {len(d)} != {19 * len(positions)}"
    if d.bg_id.nunique() != 1 or d.bg_id.iloc[0] != bg_id:
        return False, "bg_id"
    if d.sequence.nunique() != 1 or d.sequence.iloc[0] != digest:
        return False, "sequence digest"
    if d.duplicated(["site", "position", "mut_aa"]).any():
        return False, "duplicates"
    if sorted(d.position.unique().tolist()) != list(positions):
        return False, "position set"
    per_pos = d.groupby("position").mut_aa.nunique()
    if len(per_pos) != len(positions) or set(per_pos.tolist()) != {19}:
        return False, "mutants per position"
    return True, "complete"


def write_manifest(out_dir, rec):
    mp = out_dir / "manifest.csv"
    hdr = not mp.exists()
    pd.DataFrame([rec]).to_csv(mp, mode="a", header=hdr, index=False)


def run_g_r5(ref, roster, device, bg_id):
    """G-R5 (frozen 6): determinism + wild-type residue log-odds == 0."""
    import esm
    rule("G-R5 (HARD, model) -- determinism and wild-type log-odds == 0")
    row = roster[roster.background_id == bg_id].iloc[0]
    bg_seq = bg_sequence(ref, row)
    pos_bg = expected_positions(row)
    pos_ref = expected_positions(None)
    print(f"  gate background: {bg_id} (roster order "
          f"{int(row.roster_order)}), {len(pos_bg)} positions; reference "
          f"{len(pos_ref)} positions; device {device}")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    # (a) same background twice, all values compared
    t0 = time.perf_counter()
    rows1, ps1, _ = score_positions(model, alphabet, bc, bg_seq,
                                    seq_digest(bg_seq), bg_id, pos_bg,
                                    device)
    rows2, ps2, _ = score_positions(model, alphabet, bc, bg_seq,
                                    seq_digest(bg_seq), bg_id, pos_bg,
                                    device)
    k1 = {(r["position"], r["mut_aa"]): r["score"] for r in rows1}
    k2 = {(r["position"], r["mut_aa"]): r["score"] for r in rows2}
    same_keys = set(k1) == set(k2)
    dmax = max(abs(k1[k] - k2[k]) for k in k1) if same_keys else float("inf")
    gate("G-R5a scoring the same background twice gives identical values",
         "PASS" if (same_keys and dmax <= TOL_G_R5) else "FAIL",
         f"max|diff| = {dmax:.3e} over {len(k1)} values "
         f"(frozen tolerance {TOL_G_R5:.0e}); keys equal {same_keys}; "
         f"{sum(ps1) / len(ps1):.3f} s/pass",
         "frozen 6, tolerance never widened")

    # (b) wild-type residue log-odds == 0, independent re-derivation
    _, _, ex_ref = score_positions(model, alphabet, bc, ref, seq_digest(ref),
                                   WT_ID, pos_ref, device,
                                   include_wt_zero=True)
    _, _, ex_bg = score_positions(model, alphabet, bc, bg_seq,
                                  seq_digest(bg_seq), bg_id, pos_bg, device,
                                  include_wt_zero=True)
    wt_all = ex_ref["wt_vals"] + ex_bg["wt_vals"]
    cross_all = ex_ref["cross"] + ex_bg["cross"]
    max_wt = max(abs(v) for _, v in wt_all)
    max_cross = max(cross_all)
    gate("G-R5b wild-type residue log-odds == 0 at every scored position",
         "PASS" if (max_wt <= TOL_G_R5 and max_cross <= TOL_G_R5) else "FAIL",
         f"|score_wt| max {max_wt:.3e} over {len(wt_all)} positions "
         f"(reference {len(pos_ref)} + {bg_id} {len(pos_bg)}); independent "
         f"re-derivation vs library max|diff| {max_cross:.3e}",
         "S3: the zero is an identity once the cross-check holds; the "
         "library source line is quoted below")
    src = [l for l in (ROOT / "scripts" / "lib" / "esm_scoring.py")
           .read_text().splitlines() if "wt_score" in l or "aa:" in l]
    print("  quoted from scripts/lib/esm_scoring.py at run time:")
    for l in src:
        print(f"    {l.strip()}")
    print(f"  scored positions where background residue != reference "
          f"residue (must be 0; own site excluded, S2/S3): "
          f"{sum(bg_seq[p - 1] != ref[p - 1] for p in pos_bg)}")
    n_passes = 2 * len(pos_bg) + 2 * (len(pos_ref) + len(pos_bg))
    print(f"  total G-R5 passes: {n_passes} "
          f"(determinism 2 x {len(pos_bg)}; G-R5b library + independent "
          f"2 x {len(pos_ref) + len(pos_bg)}) in "
          f"{time.perf_counter() - t0:.1f}s")
    del model
    return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=[])
    ap.add_argument("--limit-positions", type=int, default=None)
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--limit-roster", type=int, default=None)
    ap.add_argument("--wt-arm-only", action="store_true")
    ap.add_argument("--inputs-only", action="store_true")
    ap.add_argument("--g-r5", nargs="?", const=DEFAULT_G_R5_BG, default=None)
    args = ap.parse_args()

    t0 = time.time()
    print("PHASE 3a Task A5e -- RBD background scorer "
          "(frozen RBD_REPLICATION_PREREG_v1.md sections 2, 3, 6, 7)")
    print("One unbatched masked-marginal pass per (background, position) "
          "via scripts/lib/esm_scoring.py; no batching, no reimplementation.")

    ref, data_pairs = load_reference()
    roster = load_roster(ref, data_pairs)

    if not CKPT.exists() or CKPT.stat().st_size != CKPT_BYTES:
        fail("G-156-3 local ESM-2 650M checkpoint present (never downloads)",
             f"{CKPT} exists={CKPT.exists()} size="
             f"{CKPT.stat().st_size if CKPT.exists() else 0}")
    print(f"  checkpoint {CKPT} ({CKPT.stat().st_size:,} bytes)")
    gate("G-156-3 local ESM-2 650M checkpoint present (never downloads)",
         "PASS", f"{CKPT_BYTES:,} bytes", "weights come from the local cache")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # G-156-6: out-dir consistency
    roster_ids = set(roster.background_id) | {WT_ID}
    strays = sorted(p.stem[3:] for p in out_dir.glob("bg_*.csv")
                    if p.stem[3:] not in roster_ids)
    mp = out_dir / "manifest.csv"
    hdr_ok = True
    if mp.exists():
        want_hdr = ["file", "kind", "bg_id", "sequence", "n_positions",
                    "n_rows", "seconds", "median_pass_s", "device"]
        hdr_ok = list(pd.read_csv(mp, nrows=0).columns) == want_hdr
    gate("G-156-6 out-dir consistency (no foreign background, manifest header)",
         "PASS" if not strays and hdr_ok else "FAIL",
         f"stray bg files {strays}, manifest header ok {hdr_ok}",
         "one roster, one out-dir (S5)")

    if args.inputs_only:
        rule("SUMMARY -- A5e input pre-flight (--inputs-only)")
        n = 0
        for name, v, val, note in GATES:
            print(f"  [{v}] {name}: {val}  {note}")
            n += v == "PASS"
        ok = n == len(GATES)
        verdict = "input pre-flight PASSES" if ok else "input pre-flight FAILS"
        print(f"\n  GATES: {n}/{len(GATES)} PASS -> {verdict}")
        print(f"\n  elapsed {time.time() - t0:.1f}s")
        sys.exit(0 if ok else 3)

    if args.g_r5 is not None:
        from scripts.lib.esm_scoring import get_device
        device = get_device()
        run_g_r5(ref, roster, device, args.g_r5)
        rule("SUMMARY -- A5e / G-R5")
        n = 0
        for name, v, val, note in GATES:
            print(f"  [{v}] {name}: {val}  {note}")
            n += v == "PASS"
        ok = n == len(GATES)
        print(f"\n  GATES: {n}/{len(GATES)} PASS -> "
              f"{'G-R5 PASSES' if ok else 'G-R5 FAILS'}")
        limitations()
        print(f"\n  elapsed {time.time() - t0:.1f}s")
        sys.exit(0 if ok else 3)

    # ---- scoring ---------------------------------------------------------
    import esm
    from scripts.lib.esm_scoring import get_device
    device = get_device()
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()
    print(f"\n  model esm2_t33_650M_UR50D loaded, device {device}")

    jobs = []           # (kind, bg_id, seq, digest, positions, row)
    if not args.only or args.wt_arm_only:
        jobs.append(("wt_arm", WT_ID, ref, seq_digest(ref),
                     expected_positions(None), None))
    for _, row in roster.iterrows():
        if args.limit_roster is not None and int(row.roster_order) > \
                args.limit_roster:
            continue
        if args.only and row.background_id not in args.only:
            continue
        if args.wt_arm_only:
            continue
        seq = bg_sequence(ref, row)
        pos = expected_positions(row)
        if args.limit_positions is not None:
            pos = sorted(pos)[:args.limit_positions]
        jobs.append(("background", row.background_id, seq, seq_digest(seq),
                     pos, row))

    rule(f"SCORING {len(jobs)} job(s) -> {out_dir}")
    n_written = n_skipped = 0
    min_cov = 1.0
    try:
        for kind, bg_id, seq, digest, pos, row in jobs:
            path = out_dir / (f"wt_arm.csv" if kind == "wt_arm"
                              else f"bg_{bg_id}.csv")
            done, why = check_file(path, bg_id, digest, pos)
            if done:
                print(f"  SKIP {bg_id} ({why})")
                n_skipped += 1
                min_cov = min(min_cov, len(pos) / N_SITES)
                continue
            t1 = time.perf_counter()
            rows, pass_s, _ = score_positions(model, alphabet, bc, seq,
                                               digest, bg_id, pos, device)
            # G-156-4 integrity BEFORE the rename
            frame = pd.DataFrame(rows)
            assert len(frame) == 19 * len(pos), (len(frame), 19 * len(pos))
            assert not frame.duplicated(["site", "position", "mut_aa"]).any()
            assert sorted(frame.position.unique().tolist()) == list(pos)
            assert set(frame.bg_id) == {bg_id}
            assert set(frame.sequence) == {digest}
            assert (frame.site.values == frame.position.values +
                    SITE0 - 1).all()
            per_pos = frame.groupby("position").mut_aa.nunique()
            assert set(per_pos) == {19} and len(per_pos) == len(pos), \
                (bg_id, per_pos.value_counts().to_dict())
            if row is not None:
                own = int(row.site)
                assert own not in set(frame.site), (bg_id, own)
                assert all(seq[p - 1] == ref[p - 1] for p in pos), bg_id
            tmp = out_dir / (f".{path.name}.tmp")
            frame.to_csv(tmp, index=False)
            tmp.replace(path)
            cov = len(pos) / N_SITES
            min_cov = min(min_cov, cov)
            med = sorted(pass_s)[len(pass_s) // 2]
            write_manifest(out_dir, dict(
                file=path.name, kind=kind, bg_id=bg_id, sequence=digest,
                n_positions=len(pos), n_rows=len(frame),
                seconds=round(time.perf_counter() - t1, 3),
                median_pass_s=round(med, 5), device=str(device)))
            n_written += 1
            eta = (len(jobs) - n_written - n_skipped) * med * len(pos)
            print(f"  {bg_id:<12} {len(pos):>4} pos, {len(frame):>5} rows, "
                  f"{med * 1000:.1f} ms/pass, {time.perf_counter() - t1:.1f}s "
                  f"-> {path.name} (jobs left "
                  f"{len(jobs) - n_written - n_skipped}, ETA {eta:.0f}s)")
    except Exception:                              # noqa: BLE001
        for p in out_dir.glob(".*.tmp"):
            p.unlink()
        traceback.print_exc()
        print("ERROR: .tmp removed, nothing half-written; exiting 1")
        sys.exit(1)

    gate("G-156-4 per-file integrity before atomic rename",
         "PASS", f"{n_written} file(s) written, {n_skipped} skipped, all "
                 f"asserts held (rows, uniqueness, position set, own site "
                 f"absent, background residue == reference at scored "
                 f"positions)", "S2/PIN-6")
    gate("G-156-5 G-R4 echo: coverage of the construct's sites",
         "PASS" if min_cov >= G_R4_FLOOR else "FAIL",
         f"min coverage {min_cov:.4f} = {min_cov * N_SITES:.1f}/201 vs "
         f"frozen floor {G_R4_FLOOR:.0%}", "200/201 when own site excluded")

    rule("SUMMARY -- A5e")
    n = 0
    for name, v, val, note in GATES:
        print(f"  [{v}] {name}: {val}  {note}")
        n += v == "PASS"
    ok = n == len(GATES)
    print(f"\n  GATES: {n}/{len(GATES)} PASS -> "
          f"{'A5e PASSES' if ok else 'A5e FAILS'}")
    print(f"  written {n_written}, skipped {n_skipped}, out-dir {out_dir}")
    limitations()
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    if not ok:
        sys.exit(3)


def limitations():
    print("\n  LIMITATIONS (AGENTS 6):")
    print("    * scores only: no statistic, no p-value and no outcome "
          "word of any frozen block is computed here")
    print("    * delta_b(v) = S(v|b) - S(v|Wuhan) is script 157's join, "
          "not this script's")
    print("    * G-R5 checks both sequence contexts on one background; "
          "the property is a property of the scoring code path, and the "
          "wild-type zero is an arithmetic identity verified against an "
          "independent re-derivation (S3)")
    print("    * files written under --limit-positions are incomplete by "
          "design and are re-scored by a later full run")


if __name__ == "__main__":
    main()
