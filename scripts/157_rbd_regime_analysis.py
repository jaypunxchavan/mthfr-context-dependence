#!/usr/bin/env python3
"""scripts/157_rbd_regime_analysis.py -- Module M2 (RBD) analysis + gates + G-SYN.

PRE-REGISTRATION (this docstring was written BEFORE the first run of this
script; no RBD model score outside data/processed/phase3/rbd_smoke/ existed
when it was written; it is not edited after any real score exists)
================================================================================
TASK.  docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md A5g: "Analysis script
(scripts/157_..., no torch) and planted-signal test G-SYN exactly as A4f/A4g,
using the real e_T."  Binding rules: frozen
docs/tasks/phase3-overnight/prereg/RBD_REPLICATION_PREREG_v1.md (sha256
8965450a...c2671a7, verified in A1).  NO TORCH, NO ESM (gate G-157-2).

DECISIONS (R1-R16)
------------------
R1 INPUTS AND PINS.  e_T.csv (A5c, sha256 14f76c83...), roster_v1.csv (A5d,
   sha256 70a6305d...), and the three acquired data files with their A5a
   acquisition sha256s; 6M0J.pdb is an OPTIONAL secondary input (R10): if it
   is absent its sha pin is skipped; if it is present and its sha is wrong,
   G-157-1 FAILS (a corrupted file on disk is a real problem).  Score
   out-dir: --mode smoke -> data/processed/phase3/rbd_smoke/ ; --mode full
   -> data/processed/phase3/rbd/ (overridable with --out-dir).
R2 VARIANT SET.  For (target T, phenotype p in {bind, expr}, mask m in
   {ge1, ge3, ge5}): the rows of e_T with use_<p>_<m> and a non-missing
   e_<p>.  PRIMARY = ge3 (frozen s2); ge1/ge5 are SENSITIVITIES - computed
   and printed for the section-5 quantities, never chosen among, never
   decisive.  T's own site must be absent from e_T (frozen s2: "Target site
   excluded from the variant set for everyone"); re-checked here -> G-157-5.
   Every filtering step prints its row count (AGENTS 5).
R3 DELTA.  delta_b(v) = S(v|b) - S(v|Wuhan arm) joined on (site, mut_aa).
   ONE shared subtraction helper serves BOTH the file path and G-SYN, so the
   planted-signal test exercises the same code.  delta is phenotype-
   independent: computed once per background over the target's master row
   list, then subset by mask.  Join gaps (a frame row with no score on
   either side after b's own site is excluded) must be exactly 0 ->
   G-157-4.
R4 RHO.  rho_b^T = Spearman(delta_b, e_T) over the variant set minus rows
   at b's own site (frozen s3).  Computed for EVERY roster background that
   has a complete file, for both targets and all six (p, m) frames; n
   printed per row of the rho table.
R5 P-VALUES AND COMPLETENESS.  p_abs/p_neg/p_pos = p3c.p_spec(rho_T,
   {rho_b : b in N_T}, mode) -- the frozen s5 formula (source quoted at run
   time).  This requires the COMPLETE null set: every b in N_T scored and
   G-R4-clean, and T's own file present.  If anything is missing the script
   prints "stage incomplete (k/|N_T|)" and emits NO outcome word for that
   target - the frozen block defines no partial-null rule and none is
   invented.  In --mode full, missing roster files are gate G-157-3 FAIL
   (exit 3); in smoke, incompleteness of the null sets is expected by
   construction and is printed as such.  p_spec_adj (R9) obeys the same
   completeness rule.
R6 OUTCOME WORDS.  Frozen s5 thresholds: RBD-REPRODUCES iff p_abs <= 0.05;
   RBD-DOES-NOT-REPRODUCE iff p_abs > 0.10; RBD-INCONCLUSIVE otherwise.
   outcome_word() asserts its return is in that closed set of three; both
   targets are reported side by side; NO multiplicity adjustment (frozen s5,
   stated in the output); sensitivities never decide; nothing this script
   prints is ever compared across MTHFR/GB1/RBD (no cross-system claim).
R7 SECONDARY SCOPE (frozen s6).  6a-6e and 6h run at the PRIMARY mask for
   BOTH phenotypes (6g = the expression run; 6f is A5c's record, R13);
   section-5 quantities additionally run at ge1/ge5 as sensitivities.
R8 6a.  Position-cluster bootstrap of rho_T's own row set: clusters = site,
   n_boot = N_BOOT (env, default 10000), seed = SEED (env, default 0), via
   p3c.pos_cluster_boot; CI = p3c.pct_ci; draw count, NaN count and cluster
   count printed.  Never row-level.
R9 6b.  shift_b = mean|delta_b| on the same rows used for rho_b.
   Spearman(rho_b, shift_b) across ALL scored backgrounds with a
   BACKGROUND-level bootstrap CI (p3c.background_boot, N_BOOT, SEED) -
   the resampling unit is the background, never positions, never variants.
   p_spec_adj: y = rho_b, x = shift_b over scored backgrounds INCLUDING T;
   resid = p3c.loo_ols_residuals; p_spec_adj = p_spec(resid_T, {resid_b :
   b in N_T}, "abs") primary, with neg/pos printed beside it.
R10 6c.  Locality over N_T U S_T: sequence distance |site_b - site_T| is
   always available; 3D CA distance from 6M0J chain E when BOTH sites have
   a CA, with numbering verified AT RUN TIME (every chain-E residue inside
   331-531 must equal the Wuhan reference; at least 95% of the 201 sites
   must be present, else the structure is refused and sequence distance
   only is used, disclosed).  Missing pairs are reported, never imputed.
   Spearman(rho_b, distance) + background-level CI for each distance type.
   Descriptive: no outcome word attaches to 6c.
R11 6d.  T's rank within S_T U {T}: primary = rank of |rho_T| among the
   |rho_b| (average ties, 1-based), fraction = rank / (1 + |S_T|); the
   signed-rank fraction prints beside it.  A rank fraction, not a test.
R12 6e.  Split-half: the unique variant sites are shuffled by
   default_rng(SEED) and split floor/ceil into two halves; p_abs is
   recomputed on each half under the same completeness rule (R5).
   Stability descriptor only: its p_abs values are never used to re-derive
   the outcome word and are never compared with alpha to decide anything.
R13 6f.  Measurement reliability was computed in A5c (scripts/163) and its
   record is PHASE3_A5c_FULL_OUTPUT.txt; e_T.csv carries no per-library
   columns, so this script prints a pointer with a file-existence check and
   does NOT recompute it.  Disclosed (frozen 6f asks only that it be
   reported alongside).
R14 6h.  If A6's product data/processed/phase3/multidms/e_T_MD.csv exists it
   is printed next to the primary; otherwise "unavailable (A6 pending)".
   It can never replace the primary (frozen s6h).
   IMPLEMENTATION NOTE (post-hoc code fix after the A5g runs, closing an
   implementation-vs-R7 gap; no rule/threshold/seed change): 6h now computes
   per (T, phenotype) at the PRIMARY mask coverage n_matched/n_frame,
   rho_T^MD = Spearman(delta_T, effect) and profile_rho = Spearman(effect,
   e_phenotype) on matched rows: secondary only, NO outcome word.
R15 G-SYN (frozen s7).  Synthetic SCORE sets built from the REAL e_T, run
   through the same score -> subtract_scores -> rho -> p_spec ->
   outcome_word path, with the real roster's N_T membership:
   - signal (rng seed 0): delta_T = e_T + N(0, 0.1*sd(e_T)); every other
     member of N_T U {T} = N(0, sd(e_T)).  RNG draws in a fixed order:
     synthetic WT-arm scores, then T's noise, then null backgrounds in
     sorted id order.  GATE (i): p_abs <= 0.05 AND the emitted word ==
     RBD-REPRODUCES, for BOTH targets.  (Expected floor: 1/(1+|N_T|).)
   - null (N_SYN_NULL draws, rng seed 1000+i): every member including T =
     N(0, sd(e_T)).  GATE (ii) per target: fraction of draws with
     p_abs <= 0.05 <= 0.15 AND median p_abs > 0.05 AND NaN draws == 0.
     100 draws because a single synthetic-noise draw is not a number
     (AGENTS 3); a FAIL is never re-rolled - it stops the task.
   - primary frame only (bind, ge3); disclosed.
R16 MODES/ENV.  --mode {smoke,full} (default smoke) picks the out-dir
   unless --out-dir is given; N_BOOT (10000), N_REF (2000 - the draw-by-
   draw gate's draw count, the same value GB1's G-3(ii) used),
   N_SYN_NULL (100), SEED (0) are read from the environment and every
   non-default value is printed.  --inputs-only runs G-157-1, G-157-5,
   G-R1, G-R2, G-R4, G-157-4 and stops before any resampling.

GATES (each printed as ">>> name: PASS/FAIL value = ... note = ...")
-------------------------------------------------------------------
G-157-1 input pins: sha256 of e_T.csv, roster_v1.csv, wildtype_sequence.fasta,
       RBD_sites.csv, final_variant_scores.csv (+ 6M0J.pdb when present).
G-157-5 e_T excludes T's own site: 0 rows at 501 for N501Y, 0 rows at 484
       for E484K (frozen s2, re-derived here).
G-R1   (frozen s7) N501Y's reference differs from Wuhan-Hu-1 by exactly
       (501, N->Y) and E484K's by exactly (484, E->K), computed from the
       data's own wildtype column and compared with the frozen constants.
G-R2   (frozen s7) every row of final_variant_scores.csv has wildtype ==
       the sequence residue at its site, where the reference for a label is
       Wuhan + that label's PRE-REGISTERED background mutations (constants
       carried from scripts/162's docstring R4, verified in A5b: Wuhan {},
       Beta {417 K->N, 484 E->K, 501 N->Y}, Delta {452 L->R, 478 T->K},
       E484K {484 E->K}, N501Y {501 N->Y}).  Per-target references are used
       because G-R1 shows the backgrounds differ from Wuhan at exactly
       those sites; the count of rows that would mismatch the WUHAN
       reference is printed for the record.
G-R3   (frozen s7) the three bootstrap gates, re-run on REAL RBD rows:
       (i) identity: every cluster drawn exactly once reproduces the point
           estimate to < 1e-12 (every scored background, both targets,
           primary frame);
       (ii) draw-by-draw: corrected routine vs p3c.reference_boot on
           identical pre-drawn cluster ids (N_REF draws, seed 0) for the
           FIRST THREE completed backgrounds in roster order, both targets,
           max|diff| < 1e-12;
       (iii) Phase 1 CI reproduction at FIXED n_boot=10000, seed 0 on the
           MTHFR A222V anchor rows: both endpoints within 1e-9 of the
           frozen T_CI_LO/T_CI_HI (constants in scripts/159 lines 140-141,
           quoted at run time; re-verified 40/40 in A2).
G-R4   (frozen s7) every scored file covers >= 95% of the construct's 201
       sites, carries the right bg_id / 16-hex sequence digest / shape
       (own site absent, site == position+330, no duplicate triples), and
       wt_arm.csv is present and complete (201 sites x 19 mutants, Wuhan
       digest).
G-157-4 delta join: zero frame rows missing either side of the
       subtraction after b's own site is excluded (both targets, every
       scored file, full master row list).
G-157-3 stage completeness (full mode only): all 100 roster files present
       and G-R4-clean.  Not a gate in smoke mode (by construction).
G-SYN(i)/(ii): as in R15.
G-157-2 torch and esm are NOT in sys.modules when the script exits.

OUTPUTS.  rho_b_<mode>.csv (one row per target x frame x scored background)
and analysis_results_<mode>.json in the mode's out-dir; everything else is
printed -- the printed output is the record, and limitations() is printed at
exit as well as stated above.

COMMANDS (run from the repo root)
---------------------------------
    scripts/157_rbd_regime_analysis.py --inputs-only          # pins/gates
    scripts/157_rbd_regime_analysis.py --mode smoke           # rehearsal
    N_BOOT=10000 scripts/157_rbd_regime_analysis.py --mode full  # the night
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))                    # scripts.lib imports (as 154/155/161)
from scripts.lib import phase3_common as p3c     # noqa: E402

# ---- paths ---------------------------------------------------------------
ET_CSV    = ROOT / "data" / "processed" / "phase3" / "rbd" / "e_T.csv"
ROSTER    = ROOT / "data" / "processed" / "phase3" / "rbd" / "roster_v1.csv"
OUT_REAL  = ROOT / "data" / "processed" / "phase3" / "rbd"
OUT_SMOKE = ROOT / "data" / "processed" / "phase3" / "rbd_smoke"
EXT       = ROOT / "data" / "external" / "rbd_starr2022"
FASTA     = EXT / "wildtype_sequence.fasta"
SITES_CSV = EXT / "RBD_sites.csv"
FVAR      = EXT / "final_variant_scores.csv"
PDB       = ROOT / "data" / "external" / "rbd_structures" / "6M0J.pdb"
MD_CSV    = ROOT / "data" / "processed" / "phase3" / "multidms" / "e_T_MD.csv"
A5C_OUT   = ROOT / "docs" / "tasks" / "phase3-overnight" / "PHASE3_A5c_FULL_OUTPUT.txt"
PREREG159 = ROOT / "scripts" / "159_phase3_common_gate.py"
P3C        = ROOT / "scripts" / "lib" / "phase3_common.py"

# ---- pinned sha256 (A5a acquisition log / A5c / A5d; re-derived on every run)
SHAS = {
    ET_CSV:    "14f76c83714e74b757509403560685071d61bccf920f97d71f686cd772e257fd",
    ROSTER:    "70a6305d24b753655e92f10f413115381a84721998300440b5d48f8eec87b2fb",
    FASTA:     "2a49a444e9d002c82c40d3b5e4a3bc5e4a152c00f5817428803b4368c21c15fb",
    SITES_CSV: "a35adf4dc5e6bff78ed64dc9daca12580cfe6f891e52c6016e0ffaf6702c5ca3",
    FVAR:      "c0678e8560e745479a896bc56c4744b75e64f1cfd8666fe0715f0855d652ef97",
}
PDB_SHA = "51f27a495c0c12fa87f459a2510a9268d4d48a34b63ba3e5db5ae7c672a26af5"

# ---- frozen / pre-registered constants ------------------------------------
TARGETS      = ["N501Y", "E484K"]                 # frozen s5: both, side by side
TARGET_SITE  = {"N501Y": 501, "E484K": 484}
TARGET_SUB   = {"N501Y": (501, "N", "Y"), "E484K": (484, "E", "K")}
REF_MUTS = {                                      # scripts/162 docstring R4 (A5b)
    "Wuhan-Hu-1": {},
    "Beta":       {417: ("K", "N"), 484: ("E", "K"), 501: ("N", "Y")},
    "Delta":      {452: ("L", "R"), 478: ("T", "K")},
    "E484K":      {484: ("E", "K")},
    "N501Y":      {501: ("N", "Y")},
}
PHENOS   = ["bind", "expr"]                        # R7 (6g = the expr run)
MASKS    = ["ge1", "ge3", "ge5"]                   # primary ge3 (frozen s2)
PRIMARY  = "ge3"
N_SITES  = 201
SITE0    = 331
FLOOR_COV = 0.95                                   # frozen G-R4
T_CI_LO, T_CI_HI = -0.1173334458953319, -0.05951138449511738
G3III_N  = 10000
TOL_12, TOL_9 = 1e-12, 1e-9
ALPHA_ABS, ALPHA_NONE = 0.05, 0.10                 # frozen s5
WORDS = ("RBD-REPRODUCES", "RBD-INCONCLUSIVE", "RBD-DOES-NOT-REPRODUCE")

N_BOOT     = int(os.environ.get("N_BOOT", "10000"))
N_REF      = int(os.environ.get("N_REF", "2000"))
N_SYN_NULL = int(os.environ.get("N_SYN_NULL", "100"))
SEED       = int(os.environ.get("SEED", "0"))

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}", flush=True)


def rule(t=""):
    print("\n" + "=" * 76)
    if t:
        print(t)
        print("=" * 76)


def note(t):
    print(f"  {t}", flush=True)


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    """Print path relative to the repo root when possible, else absolute."""
    try:
        return str(Path(p).relative_to(ROOT))
    except ValueError:
        return str(Path(p))


def quote(path, a, b, label):
    lines = Path(path).read_text().splitlines()
    print(f"  QUOTED SOURCE: {label} ({path}, lines {a}-{b}):")
    for i in range(a - 1, min(b, len(lines))):
        print(f"    {i + 1:4d}| {lines[i]}")


def outcome_word(p_abs):
    """Frozen s5 thresholds.  Asserts the closed set of three words (R6)."""
    p = float(p_abs)
    if not np.isfinite(p):
        raise ValueError(f"p_abs not finite: {p!r} -- completeness rule R5 "
                         "should have withheld the word")
    w = ("RBD-REPRODUCES" if p <= ALPHA_ABS else
         "RBD-DOES-NOT-REPRODUCE" if p > ALPHA_NONE else "RBD-INCONCLUSIVE")
    assert w in WORDS, f"outcome word outside the frozen set: {w!r}"
    return w


def subtract_scores(score_arr, wt_arr):
    """R3: THE single subtraction used by the file path AND by G-SYN."""
    return np.asarray(score_arr, dtype=float) - np.asarray(wt_arr, dtype=float)


def limitations():
    print("\nLIMITATIONS (printed, not only written down):")
    for t in [
        "two targets, two looks, NO multiplicity adjustment (frozen s5 says "
        "so explicitly)",
        "an outcome word is emitted only when the target's whole null set "
        "N_T and T's own file are scored and G-R4-clean; otherwise the "
        "status is 'stage incomplete' and no word exists (R5)",
        "rho_b is a rank correlation over ~3.3k variant rows nested in ~200 "
        "site clusters; resampling is by site (6a) and by background "
        "(6b/6c), never by variant row",
        "G-SYN validates the MECHANICS of the pipeline on planted data; it "
        "says nothing about this dataset's power",
        "6b/6c/6d/6e are descriptive: none of them carries an outcome word "
        "and none can change the s5 decision",
        "6f is A5c's record (pointer printed, not recomputed - e_T has no "
        "per-library columns)",
        "6h awaits A6's multidms product; when absent it prints "
        "'unavailable (A6 pending)' and never substitutes anything",
        "smoke mode withholds real-data outcome words BY DESIGN because its "
        "out-dir does not contain the full roster",
        "sensitivity masks (n_bc >= 1, >= 5) are computed and printed but "
        "are never selected among and never decide (frozen s2)",
    ]:
        print(f"  - {t}")


# ==========================================================================
# 1. reference + roster sequences (S1 semantics, re-derived here)
# ==========================================================================
def load_reference():
    sites = pd.read_csv(SITES_CSV).set_index("site").amino_acid.to_dict()
    missing = [p for p in range(SITE0, SITE0 + N_SITES) if p not in sites]
    if missing:
        raise SystemExit(f"RBD_sites.csv missing sites {missing[:5]}")
    ref = "".join(sites[p] for p in range(SITE0, SITE0 + N_SITES))
    nt = "".join(l.strip() for l in FASTA.read_text().splitlines()
                 if not l.startswith(">"))
    note(f"reference: {N_SITES} sites {SITE0}-{SITE0 + N_SITES - 1} from "
         f"RBD_sites.csv; fasta {len(nt)} nt "
         f"(content three-way gated in A5b/G-156-1 this session; here its "
         f"sha256 is pinned)")
    if len(ref) != N_SITES:
        raise SystemExit(f"reference length {len(ref)} != {N_SITES}")
    return sites, ref


def seq_digest(s):
    """16-hex sha256 of the 201-aa sequence actually scored (S4 semantics)."""
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def bg_sequence(row, ref):
    s = list(ref)
    i = int(row.site) - SITE0
    if s[i] != row.wt_aa:
        raise SystemExit(f"roster wt_aa mismatch at site {row.site}: "
                         f"reference has {s[i]}, roster says {row.wt_aa}")
    s[i] = row.mutant
    return "".join(s)


# ==========================================================================
# 2. variant frames (R2) -- master row list per target, mask subsets
# ==========================================================================
def load_frames(et):
    """masters[T] = (pos, mut) over ALL of T's e_T rows (3,800).
    frames[(T, ph, mk)] = dict(idx, e) selecting the masked rows."""
    masters, frames, excl = {}, {}, {}
    for T in TARGETS:
        sub = et[et.target == T].reset_index(drop=True)
        masters[T] = (sub.position.to_numpy(int), sub.mutant.to_numpy(str))
        excl[T] = int((sub.position == TARGET_SITE[T]).sum())
        note(f"target {T}: {len(sub)} master rows "
             f"(sites {sub.position.min()}-{sub.position.max()}), "
             f"rows at T's own site {excl[T]} (must be 0)")
        for ph in PHENOS:
            for mk in MASKS:
                m = sub[f"use_{ph}_{mk}"].to_numpy(bool)
                nn = sub[f"e_{ph}"].notna().to_numpy()
                sel = m & nn
                frames[(T, ph, mk)] = dict(
                    idx=np.flatnonzero(sel),
                    e=sub.loc[sel, f"e_{ph}"].to_numpy(float))
                note(f"  frame {T}/{ph}/{mk}: mask {int(m.sum())} rows, "
                     f"non-missing e -> {int(sel.sum())} rows "
                     f"(dropped {int(m.sum()) - int(sel.sum())})")
    return masters, frames, excl


# ==========================================================================
# 3. score files + G-R4 (frozen s7) + R3 deltas
# ==========================================================================
def load_scores(out_dir, roster, ref):
    """Returns (wt_map, files, cov, issues, wt_rows)."""
    out_dir = Path(out_dir)
    issues = []
    wt_path = out_dir / "wt_arm.csv"
    if not wt_path.exists():
        return None, {}, {}, [f"wt_arm.csv missing in {out_dir}"], None
    wt = pd.read_csv(wt_path)
    exp_digest = seq_digest(ref)
    wt_ok = (len(wt) == N_SITES * 19
             and not wt.duplicated(["site", "position", "mut_aa"]).any()
             and sorted(wt.position.unique()) == list(range(1, N_SITES + 1))
             and set(wt.sequence.astype(str)) == {exp_digest}
             and set(wt.bg_id.astype(str)) == {"WT"}
             and (wt.site.to_numpy() == wt.position.to_numpy() + 330).all())
    if not wt_ok:
        issues.append(f"wt_arm shape/digest wrong: rows {len(wt)}, "
                      f"digests {sorted(set(wt.sequence.astype(str)))} != "
                      f"[{exp_digest}]")
    wt_map = {(int(r.site), r.mut_aa): float(r.score) for r in wt.itertuples()}

    files, cov = {}, {}
    for row in roster.itertuples():
        bid = row.background_id
        p = out_dir / f"bg_{bid}.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        c = df.position.nunique() / N_SITES
        cov[bid] = c
        ok = (c >= FLOOR_COV
              and set(df.bg_id.astype(str)) == {bid}
              and set(df.sequence.astype(str)) == {seq_digest(bg_sequence(row, ref))}
              and not df.duplicated(["site", "position", "mut_aa"]).any()
              and (df.site.to_numpy() == df.position.to_numpy() + 330).all()
              and (df.site.to_numpy() != int(row.site)).all())
        if ok:
            files[bid] = df
        else:
            issues.append(f"{bid}: coverage {c:.4f} / shape-digest-own-site "
                          f"check {ok}")
    return wt_map, files, cov, issues, len(wt)


def delta_masters(files, wt_map, masters):
    """R3: score and WT arrays aligned to each target's master rows,
    subtracted through subtract_scores().  NaN marks a missing side."""
    out = {}
    for bid, df in files.items():
        smap = {(int(r.site), r.mut_aa): float(r.score) for r in df.itertuples()}
        for T, (pos, muts) in masters.items():
            score = np.array([smap.get((int(p), m), np.nan)
                              for p, m in zip(pos, muts)])
            wtv = np.array([wt_map.get((int(p), m), np.nan)
                            for p, m in zip(pos, muts)])
            out[(bid, T)] = subtract_scores(score, wtv)
    return out


def join_gaps(files, dm, roster_site, masters):
    """R3/G-157-4: rows with a NaN delta after b's own site is excluded."""
    bad = []
    for (bid, T), d in dm.items():
        pos = masters[T][0]
        keep = pos != roster_site[bid]
        n_gap = int(np.isnan(d[keep]).sum())
        if n_gap:
            bad.append((bid, T, n_gap))
    return bad


def rho_of(dm_row, frame, master_pos, exclude_site):
    """R4: Spearman(delta_b, e_T) over frame rows not at exclude_site."""
    idx = frame["idx"]
    keep = master_pos[idx] != exclude_site
    sub = idx[keep]
    d = dm_row[sub]
    e = frame["e"][keep]
    if np.isnan(d).any():
        raise ValueError(f"unexpected join gap inside rho ({int(np.isnan(d).sum())}"
                         " rows) -- G-157-4 should have failed first")
    return float(p3c.spearman(d, e)), len(d), d, e, master_pos[sub]


def pvals(rho_t, nulls):
    """R5: the frozen s5 triplet via phase3_common.p_spec."""
    p_abs, k_abs, n = p3c.p_spec(rho_t, nulls, "abs")
    p_neg, k_neg, _ = p3c.p_spec(rho_t, nulls, "neg")
    p_pos, k_pos, _ = p3c.p_spec(rho_t, nulls, "pos")
    return dict(p_abs=float(p_abs), k_abs=int(k_abs),
                p_neg=float(p_neg), k_neg=int(k_neg),
                p_pos=float(p_pos), k_pos=int(k_pos),
                n_null=int(n), rho_target=float(rho_t))


def null_members(roster, T):
    return list(roster.loc[roster[f"in_null_{T}"].astype(bool),
                           "background_id"])


def target_bg_id(roster, T):
    """The roster background_id of target T (e.g. N501Y -> TGT_N501Y).
    Derived from the roster, never hard-coded, and triple-checked: one
    TARGET-arm row at T's site whose mutant equals T's substitution."""
    m = roster.loc[(roster.arm.astype(str) == "TARGET")
                   & (roster.site.astype(int) == TARGET_SITE[T])]
    if len(m) != 1:
        raise SystemExit(f"target {T}: expected 1 TARGET-arm row at site "
                         f"{TARGET_SITE[T]}, found {len(m)}")
    row = m.iloc[0]
    if str(row.mutant) != TARGET_SUB[T][2]:
        raise SystemExit(f"target {T}: roster mutant {row.mutant} != "
                         f"{TARGET_SUB[T][2]}")
    return str(row.background_id)


def arm_members(roster, T, kind):
    """kind: 'S' -> the S_T arm, 'nullS' -> N_T U S_T."""
    arms = roster.arm.astype(str)
    if kind == "S":
        return list(roster.loc[arms == f"S_{T}", "background_id"])
    return list(roster.loc[(roster[f"in_null_{T}"].astype(bool))
                           | (arms == f"S_{T}"), "background_id"])


# ==========================================================================
# 4. reference-sequence gates G-R1 / G-R2 (frozen s7)
# ==========================================================================
def check_reference_gates(fvar):
    sites = pd.read_csv(SITES_CSV).set_index("site").amino_acid.to_dict()
    wuhan = "".join(sites[p] for p in range(SITE0, SITE0 + N_SITES))

    # G-R1: per-target reference vs Wuhan, from the data's own wildtype col
    g1_vals, g1_ok = [], True
    for T in TARGETS:
        sub = fvar[fvar.target == T]
        diffs = {}
        for r in sub.itertuples():
            p = int(r.position)
            if p in diffs:
                assert diffs[p] == r.wildtype, (T, p, diffs[p], r.wildtype)
            diffs[p] = r.wildtype
        observed = sorted((p, wuhan[p - SITE0], w) for p, w in diffs.items()
                          if w != wuhan[p - SITE0])
        expected = [TARGET_SUB[T]]
        ok = observed == expected
        g1_ok &= ok
        g1_vals.append(f"{T}: {observed} vs frozen {expected} -> {ok}")
    print("  G-R1 per-target reference differences vs Wuhan-Hu-1:")
    for v in g1_vals:
        note(v)

    # G-R2: every row's wildtype == its label's pre-registered reference
    bad_rows, wuhan_rows = [], 0
    for lab, muts in REF_MUTS.items():
        sub = fvar[fvar.target == lab]
        if sub.empty:
            bad_rows.append(f"label {lab} absent from final_variant_scores")
            continue
        for r in sub.itertuples():
            p = int(r.position)
            exp = dict((q, a) for q, (a, b) in muts.items()).get(
                p, wuhan[p - SITE0])
            # muts maps site -> (from, to); reference residue = 'to' if
            # the label mutates that site, else the Wuhan residue
            if p in muts:
                exp = muts[p][1]
            if r.wildtype != exp:
                bad_rows.append((lab, p, r.wildtype, exp))
            if lab != "Wuhan-Hu-1" and r.wildtype != wuhan[p - SITE0]:
                wuhan_rows += 1
    note(f"rows whose wildtype differs from the WUHAN sequence: "
         f"{wuhan_rows} (expected: the background-substitution sites of the "
         f"non-Wuhan labels)")
    return g1_ok, bad_rows, len(fvar), wuhan_rows


# ==========================================================================
# 5. G-SYN (R15): synthetic score sets built from the real e_T
# ==========================================================================
def g_syn_signal(frame, master_pos, null_ids, bg_sites, T):
    """Planted alignment: T's synthetic delta tracks e_T, others are noise."""
    rng = np.random.default_rng(0)
    e = frame["e"]
    fpos = master_pos[frame["idx"]]            # frame-length site array
    sd = float(np.std(e))
    wt_syn = rng.normal(0.0, 1.0, len(e))            # synthetic WT-arm scores
    syn_t = e + rng.normal(0.0, 0.1 * sd, len(e))    # planted signal for T
    score_t = subtract_scores(wt_syn + syn_t, wt_syn)
    rho_t = float(p3c.spearman(score_t, e))          # T's site is not in frame
    rhos = []
    for bid in sorted(null_ids):
        syn = rng.normal(0.0, sd, len(e))
        score = subtract_scores(wt_syn + syn, wt_syn)
        keep = fpos != bg_sites[bid]
        rhos.append(float(p3c.spearman(score[keep], e[keep])))
    return rho_t, rhos


def g_syn_null(frame, master_pos, null_ids, bg_sites, T, draw):
    """All members (incl. T) are noise: no alignment with e_T anywhere."""
    rng = np.random.default_rng(1000 + draw)
    e = frame["e"]
    fpos = master_pos[frame["idx"]]            # frame-length site array
    sd = float(np.std(e))
    wt_syn = rng.normal(0.0, 1.0, len(e))
    score_t = subtract_scores(wt_syn + rng.normal(0.0, sd, len(e)), wt_syn)
    keep_t = fpos != TARGET_SITE[T]            # all-True: frame excludes it
    rho_t = float(p3c.spearman(score_t[keep_t], e[keep_t]))
    rhos = []
    for bid in sorted(null_ids):
        score = subtract_scores(wt_syn + rng.normal(0.0, sd, len(e)), wt_syn)
        keep = fpos != bg_sites[bid]
        rhos.append(float(p3c.spearman(score[keep], e[keep])))
    return rho_t, rhos


def run_g_syn(roster, masters, frames):
    rule("G-SYN -- PLANTED SIGNAL AND PLANTED NULL ON SYNTHETIC SCORES "
         "BUILT FROM THE REAL e_T (frozen s7)")
    note(f"primary frame only (bind, {PRIMARY}); rng seed 0 (signal), "
         f"1000+i (null draws); N_SYN_NULL={N_SYN_NULL}; the same "
         f"subtract_scores/rho/p_spec/outcome_word path as the real data")
    bg_sites = dict(zip(roster.background_id, roster.site.astype(int)))
    out = {}
    for T in TARGETS:
        frame = frames[(T, "bind", PRIMARY)]
        pos = masters[T][0]
        null_ids = null_members(roster, T)
        floor = 1.0 / (1.0 + len(null_ids))

        rho_t, rhos = g_syn_signal(frame, pos, null_ids, bg_sites, T)
        p = pvals(rho_t, rhos)
        w = outcome_word(p["p_abs"])
        out[T] = dict(signal=dict(rho_target=rho_t,
                                  max_abs_null=float(np.max(np.abs(rhos))),
                                  n_null=len(rhos), expected_floor=floor, w=w,
                                  **{k: p[k] for k in
                                     ("p_abs", "k_abs", "p_neg", "p_pos")}))
        note(f"  {T} signal: rho_T = {rho_t:.4f} vs max|rho_null| = "
             f"{float(np.max(np.abs(rhos))):.4f} over {len(rhos)} nulls")
        note(f"  {T} signal: p_abs = {p['p_abs']:.4f} "
             f"(= k {p['k_abs']} + 1 / {p['n_null'] + 1}; mathematical "
             f"floor {floor:.4f}), word = {w}")

        draws = []
        for i in range(N_SYN_NULL):
            rho_tn, rhosn = g_syn_null(frame, pos, null_ids, bg_sites, T, i)
            pn = pvals(rho_tn, rhosn)
            draws.append(pn["p_abs"])
        arr = np.array(draws, dtype=float)
        n_nan = int(np.isnan(arr).sum())
        fires = int(np.nansum(arr <= ALPHA_ABS)) if n_nan < arr.size else -1
        frac = fires / max(1, arr.size - n_nan)
        med = float(np.nanmedian(arr)) if n_nan < arr.size else float("nan")
        out[T]["null"] = dict(n_draws=int(arr.size), n_nan=n_nan,
                              fires=fires, frac=frac, median=med,
                              p_min=float(np.nanmin(arr)),
                              p_max=float(np.nanmax(arr)),
                              p_abs_draws=[float(x) for x in arr])
        note(f"  {T} null: {arr.size} draws, p_abs min/median/max = "
             f"{out[T]['null']['p_min']:.4f}/{med:.4f}/"
             f"{out[T]['null']['p_max']:.4f}, draws with p_abs <= 0.05: "
             f"{fires} ({frac:.3f})")
    return out


# ==========================================================================
# 6. structure (R10): 6M0J chain E, numbering verified at run time
# ==========================================================================
THREE2ONE = dict(ALA="A", ARG="R", ASN="N", ASP="D", CYS="C", GLN="Q",
                 GLU="E", GLY="G", HIS="H", ILE="I", LEU="L", LYS="K",
                 MET="M", PHE="F", PRO="P", SER="S", THR="T", TRP="W",
                 TYR="Y", VAL="V", MSE="M")


def load_structure(ref):
    """Returns (ca: {site: xyz}, stats) or (None, reason)."""
    if not PDB.exists():
        return None, "6M0J.pdb absent -> sequence distance only (R10)"
    if sha256_of(PDB) != PDB_SHA:
        return None, ("6M0J.pdb sha256 mismatch -> sequence distance only "
                      "(R10)")
    chains = {}
    for line in PDB.read_text().splitlines():
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            ch = line[21]
            rn = int(line[22:26])
            chains.setdefault(ch, {})[rn] = (
                (float(line[30:38]), float(line[38:46]), float(line[46:54])),
                THREE2ONE.get(line[17:20].strip(), "X"))
    best, best_cov = None, -1
    for ch, d in chains.items():
        cov = sum(1 for p in range(SITE0, SITE0 + N_SITES)
                  if p in d and d[p][1] == ref[p - SITE0])
        if cov > best_cov:
            best, best_cov = ch, cov
    d = chains[best]
    present = [p for p in range(SITE0, SITE0 + N_SITES) if p in d]
    mism = [(p, d[p][1], ref[p - SITE0]) for p in present
            if d[p][1] != ref[p - SITE0]]
    if mism or best_cov < int(FLOOR_COV * N_SITES):
        return None, (f"numbering verification FAILED on chain {best}: "
                      f"{len(mism)} mismatches, coverage {best_cov}/201 -> "
                      f"sequence distance only (R10)")
    ca = {p: np.array(d[p][0]) for p in present}
    return ca, (f"chain {best}: {len(ca)}/201 sites with CA, "
                f"0 mismatches vs the Wuhan reference (numbering verified)")


# ==========================================================================
# 7. secondary analyses 6a-6h (R7-R14)
# ==========================================================================
def ci_word(lo, hi):
    if np.isnan(lo):
        return "CI unavailable"
    return "excludes 0" if (lo > 0 or hi < 0) else "includes 0"


def run_secondaries(roster, masters, frames, dm, files, results, ca):
    """6a-6e at the PRIMARY mask for both phenotypes; 6f/6h pointers.
    Returns a serialisable dict."""
    roster_site = dict(zip(roster.background_id, roster.site.astype(int)))
    sec = {}
    for ph in PHENOS:
        for T in TARGETS:
            frame = frames[(T, ph, PRIMARY)]
            pos = masters[T][0]
            tb = target_bg_id(roster, T)     # e.g. N501Y -> TGT_N501Y
            rec = {}
            null_ids = null_members(roster, T)
            s_ids = arm_members(roster, T, "S")
            complete = (results[(T, ph, PRIMARY)].get("complete", False))

            # ---- per-background rho + shift on the primary frame --------
            per_bg = {}
            for bid in files:
                r, n, d, e, pos_sub = rho_of(dm[(bid, T)], frame, pos,
                                             roster_site[bid])
                per_bg[bid] = dict(rho=r, n=n,
                                   shift=float(np.mean(np.abs(d))),
                                   site=roster_site[bid])

            # ---- 6a: position-cluster bootstrap CI of rho_T -------------
            if tb in per_bg:
                idx = frame["idx"]
                dd = dm[(tb, T)][idx]
                ee = frame["e"]
                cl = pos[idx]
                okk = ~np.isnan(dd)
                draws = p3c.pos_cluster_boot(dd[okk], ee[okk], cl[okk],
                                             n_boot=N_BOOT, seed=SEED)
                lo, hi, n_fin = p3c.pct_ci(draws)
                rec["6a"] = dict(rho=per_bg[tb]["rho"], n=int(okk.sum()),
                                 n_clusters=int(len(np.unique(cl[okk]))),
                                 n_draws=int(len(draws)), n_finite=int(n_fin),
                                 ci_lo=float(lo), ci_hi=float(hi))
                note(f"  6a {T}/{ph}: rho_T = {per_bg[tb]['rho']:.4f}, "
                     f"position-cluster CI [{lo:.4f}, {hi:.4f}] "
                     f"({ci_word(lo, hi)}) over {int(okk.sum())} rows in "
                     f"{int(len(np.unique(cl[okk])))} site clusters, "
                     f"{len(draws)} draws ({n_fin} finite)")
            else:
                note(f"  6a {T}/{ph}: T's own score file missing -> "
                     f"rho_T CI not computed")

            # ---- 6b: shift-magnitude confound ---------------------------
            ids_all = [b for b in files]        # T included iff T scored
            rho_v = np.array([per_bg[b]["rho"] for b in ids_all])
            shift_v = np.array([per_bg[b]["shift"] for b in ids_all])
            if len(ids_all) >= 3:
                rho_s = float(p3c.spearman(rho_v, shift_v))
                bdraws, bnan = p3c.background_boot(rho_v, shift_v,
                                                   n_boot=N_BOOT, seed=SEED,
                                                   stat=p3c.spearman)
                lo, hi, nf = p3c.pct_ci(bdraws)
                rec["6b"] = dict(n_backgrounds=len(ids_all), rho=rho_s,
                                 ci_lo=float(lo), ci_hi=float(hi),
                                 n_nan=int(bnan))
                note(f"  6b {T}/{ph}: Spearman(rho_b, mean|delta_b|) = "
                     f"{rho_s:.4f}, background-level CI [{lo:.4f}, {hi:.4f}] "
                     f"({ci_word(lo, hi)}), n = {len(ids_all)} backgrounds "
                     f"(resampling unit = background)")
                if complete:
                    resid = p3c.loo_ols_residuals(rho_v, shift_v)
                    i_t = ids_all.index(tb)
                    null_resid = [float(resid[ids_all.index(b)])
                                  for b in null_ids]
                    pa = pvals(float(resid[i_t]), null_resid)
                    rec["6b"]["p_spec_adj"] = {k: pa[k] for k in
                                               ("p_abs", "p_neg", "p_pos",
                                                "k_abs", "n_null")}
                    note(f"  6b {T}/{ph} p_spec_adj (leave-one-out OLS "
                         f"shift-adjusted): p_abs = {pa['p_abs']:.4f} "
                         f"(neg {pa['p_neg']:.4f} / pos {pa['p_pos']:.4f}); "
                         f"descriptive, not a decision")
                else:
                    note(f"  6b {T}/{ph} p_spec_adj: withheld -- "
                         f"stage incomplete (R5)")
            else:
                note(f"  6b {T}/{ph}: only {len(ids_all)} backgrounds "
                     f"scored (>= 3 needed for a correlation) -> not "
                     f"computed")

            # ---- 6c: locality over N_T U S_T ----------------------------
            subset = [b for b in (null_ids + s_ids) if b in per_bg]
            if len(subset) >= 3:
                rho_b = np.array([per_bg[b]["rho"] for b in subset])
                dist_seq = np.array([abs(per_bg[b]["site"] - TARGET_SITE[T])
                                     for b in subset], dtype=float)
                r_seq = float(p3c.spearman(rho_b, dist_seq))
                d1, _ = p3c.background_boot(rho_b, dist_seq, n_boot=N_BOOT,
                                            seed=SEED, stat=p3c.spearman)
                lo1, hi1, _ = p3c.pct_ci(d1)
                rec["6c"] = dict(n=len(subset), rho_seq=r_seq,
                                 ci_lo_seq=float(lo1), ci_hi_seq=float(hi1))
                note(f"  6c {T}/{ph}: Spearman(rho_b, |site_b - site_T|) = "
                     f"{r_seq:.4f}, CI [{lo1:.4f}, {hi1:.4f}] "
                     f"({ci_word(lo1, hi1)}), n = {len(subset)} of "
                     f"{len(null_ids) + len(s_ids)} (N_T U S_T)")
                if ca is not None:
                    pairs = [(b, per_bg[b]["site"]) for b in subset
                             if per_bg[b]["site"] in ca and TARGET_SITE[T] in ca]
                    dropped = len(subset) - len(pairs)
                    if len(pairs) >= 3:
                        d3 = np.array([float(np.linalg.norm(
                            ca[s] - ca[TARGET_SITE[T]])) for _, s in pairs])
                        r3 = float(p3c.spearman(
                            np.array([per_bg[b]["rho"] for b, _ in pairs]), d3))
                        d2, _ = p3c.background_boot(
                            np.array([per_bg[b]["rho"] for b, _ in pairs]), d3,
                            n_boot=N_BOOT, seed=SEED, stat=p3c.spearman)
                        lo2, hi2, _ = p3c.pct_ci(d2)
                        rec["6c"].update(n_3d=len(pairs), rho_3d=r3,
                                         ci_lo_3d=float(lo2),
                                         ci_hi_3d=float(hi2))
                        note(f"  6c {T}/{ph} 3D: Spearman(rho_b, CA dist) = "
                             f"{r3:.4f}, CI [{lo2:.4f}, {hi2:.4f}] "
                             f"({ci_word(lo2, hi2)}), n = {len(pairs)} "
                             f"({dropped} dropped for missing CA, never "
                             f"imputed)")
                    else:
                        note(f"  6c {T}/{ph} 3D: only {len(pairs)} pairs "
                             f"have both CAs -> not computed")
                else:
                    note(f"  6c {T}/{ph} 3D: structure unavailable -> "
                         f"sequence distance only (R10)")
            else:
                note(f"  6c {T}/{ph}: only {len(subset)} of "
                     f"{len(null_ids) + len(s_ids)} (N_T U S_T) members "
                     f"scored in this mode -> not computed")

            # ---- 6d: T's rank within S_T U {T} --------------------------
            n_s_total = int((roster.arm.astype(str) == f"S_{T}").sum())
            ids_s = [b for b in (s_ids + [tb]) if b in per_bg]
            n_s_scored = sum(1 for b in s_ids if b in per_bg)
            if tb in ids_s and len(ids_s) >= 2:
                abs_v = pd.Series({b: abs(per_bg[b]["rho"]) for b in ids_s})
                sg_v = pd.Series({b: per_bg[b]["rho"] for b in ids_s})
                r_abs = float(abs_v.rank(ascending=False,
                                         method="average")[tb])
                r_sgn = float(sg_v.rank(ascending=False,
                                        method="average")[tb])
                rec["6d"] = dict(n=len(ids_s), rank_abs=r_abs,
                                 frac_abs=r_abs / len(ids_s),
                                 rank_signed=r_sgn,
                                 frac_signed=r_sgn / len(ids_s),
                                 n_s_scored=n_s_scored, n_s_total=n_s_total)
                note(f"  6d {T}/{ph}: |rho_T| rank {r_abs:g} within "
                     f"S_T U {{T}} (n = {len(ids_s)}; {n_s_scored}/"
                     f"{n_s_total} S members scored in this mode), fraction "
                     f"{r_abs / len(ids_s):.3f} -- a rank fraction, not a "
                     f"test; signed rank {r_sgn:g}")
            else:
                note(f"  6d {T}/{ph}: only {len(ids_s)} of S_T U {{T}} "
                     f"members scored in this mode -> rank not computed")

            # ---- 6e: split-half stability --------------------------------
            if complete:
                sites_all = np.unique(pos)
                rng = np.random.default_rng(SEED)
                perm = rng.permutation(sites_all)
                half = len(perm) // 2
                halves = {"h1": set(perm[:half].tolist()),
                          "h2": set(perm[half:].tolist())}
                rec["6e"] = {}
                for hname, hs in halves.items():
                    rhos_h = {}
                    for bid in list(files) + [tb]:
                        r_h = rho_on_sites(dm[(bid, T)], frame, pos, hs,
                                           roster_site[bid])
                        if r_h is not None:
                            rhos_h[bid] = r_h
                    have_all = set(null_ids) <= set(rhos_h)
                    if tb in rhos_h and have_all:
                        ph_ = pvals(rhos_h[tb],
                                    [rhos_h[b] for b in null_ids])
                        rec_h = dict(p_abs=ph_["p_abs"],
                                     word=outcome_word(ph_["p_abs"]),
                                     n_sites=len(hs))
                        note(f"  6e {T}/{ph} {hname}: {len(hs)} sites, "
                             f"p_abs = {ph_['p_abs']:.4f}, word = "
                             f"{rec_h['word']} (stability descriptor only, "
                             f"never a decision)")
                    else:
                        rec_h = dict(p_abs=None, n_sites=len(hs),
                                     missing_null=len(set(null_ids)
                                                      - set(rhos_h)))
                        note(f"  6e {T}/{ph} {hname}: incomplete -> not "
                             f"computed")
                    rec["6e"][hname] = rec_h
            else:
                note(f"  6e {T}/{ph}: withheld -- stage incomplete (R5)")

            sec[f"{T}/{ph}"] = rec

    # ---- 6f pointer + 6h pointer ----------------------------------------
    sec["6f"] = dict(record=str(A5C_OUT.name), exists=A5C_OUT.exists(),
                     note="reliability computed in A5c (scripts/163); e_T "
                          "has no per-library columns, not recomputed here")
    note(f"  6f: A5c's record {A5C_OUT.name} "
         f"{'present' if A5C_OUT.exists() else 'MISSING'} (pointer only, "
         f"R13)")
    sec["6h"] = dict(available=MD_CSV.exists(),
                     path=str(MD_CSV.relative_to(ROOT)))
    if MD_CSV.exists():
        md = pd.read_csv(MD_CSV)
        note(f"  6h: multidms product present: {md.shape} at "
             f"{MD_CSV.relative_to(ROOT)} -- printed next to the primary "
             f"(never replacing it)")
        sec["6h"]["rows"] = md.shape[0]
        note("  6h implementation note: post-hoc code fix after the A5g "
             "runs (R14 extension) -- coverage / rho_T^MD / profile "
             "Spearman on matched PRIMARY-mask rows, both phenotypes, "
             "secondary only, NO outcome word, no rule/threshold/seed "
             "change")
        # Per (T, ph) at the PRIMARY mask, joined on (site, mutant) per
        # scripts/158's D10 contract.  Secondary only: never an outcome
        # word (the frozen block defines none for 6h), never a decision.
        sec["6h"]["combos"] = {}
        for ph in PHENOS:
            for T in TARGETS:
                frame = frames[(T, ph, PRIMARY)]
                pos = masters[T][0]
                muts = masters[T][1]
                idx = frame["idx"]
                tb = target_bg_id(roster, T)     # e.g. N501Y -> TGT_N501Y
                keep = pos[idx] != roster_site[tb]      # mirrors rho_of
                sub = md[(md.target == T) & (md.phenotype == ph)]
                eff_map = {(int(s), str(m)): float(v) for s, m, v in
                           zip(sub.site, sub.mutant, sub.effect)}
                keys = [(int(p), str(m)) for p, m in
                        zip(pos[idx][keep], muts[idx][keep])]
                hit = np.array([k in eff_map for k in keys], dtype=bool)
                n_frame, n_match = len(keys), int(hit.sum())
                ent = dict(n_frame=n_frame, n_matched=n_match)
                if (tb, T) not in dm:
                    note(f"  6h {T}/{ph}: coverage {n_match}/{n_frame}, "
                         f"delta_T unavailable (T's own score file "
                         f"missing) -> rho_T^MD not computed (secondary; "
                         f"never replaces the primary)")
                elif n_match < 3:
                    note(f"  6h {T}/{ph}: coverage {n_match}/{n_frame} "
                         f"matched (< 3) -> not computed (secondary; "
                         f"never replaces the primary)")
                else:
                    sel = np.flatnonzero(hit)
                    d = dm[(tb, T)][idx[keep][sel]]      # delta_T, R3
                    n_nan = int(np.isnan(d).sum())
                    if n_nan:
                        ent["nan_delta"] = n_nan
                        note(f"  6h {T}/{ph}: coverage {n_match}/{n_frame}, "
                             f"{n_nan} matched rows with NaN delta -> not "
                             f"computed (secondary; G-157-4 should have "
                             f"failed first)")
                    else:
                        eff = np.array([eff_map[keys[j]] for j in sel])
                        e_ph = frame["e"][keep][sel]     # measured e_{ph}
                        rho_md = float(p3c.spearman(d, eff))
                        prof = float(p3c.spearman(eff, e_ph))
                        ent.update(rho_T_MD=rho_md, profile_rho=prof)
                        note(f"  6h {T}/{ph}: coverage {n_match}/{n_frame}, "
                             f"rho_T^MD = {rho_md:.4f}, profile_rho = "
                             f"{prof:.4f} (secondary; never replaces the "
                             f"primary)")
                sec["6h"]["combos"][f"{T}/{ph}"] = ent
    else:
        note("  6h: unavailable (A6 pending) -- nothing substituted (R14)")
    return sec


def rho_on_sites(dm_row, frame, master_pos, sites_subset, exclude_site):
    """Rho of one background over the frame's rows that lie in
    sites_subset and not at exclude_site (6e helper).  None if unusable."""
    idx = frame["idx"]
    fpos = master_pos[idx]
    keep = np.isin(fpos, list(sites_subset)) & (fpos != exclude_site)
    if int(keep.sum()) < 3:
        return None
    d = dm_row[idx[keep]]
    e = frame["e"][keep]
    if np.isnan(d).any():
        return None
    return float(p3c.spearman(d, e))


# ==========================================================================
# 8. G-R3: the three bootstrap gates on real RBD rows (frozen s7)
# ==========================================================================
def _rowset(dm_row, frame, master_pos, exclude_site):
    idx = frame["idx"]
    keep = master_pos[idx] != exclude_site
    sub = idx[keep]
    return dm_row[sub], frame["e"][keep], master_pos[sub]


def run_g3(masters, frames, files, dm, roster):
    rule("G-R3 -- BOOTSTRAP GATES ON REAL RBD ROWS (frozen s7)")
    roster_site = dict(zip(roster.background_id, roster.site.astype(int)))
    pos_sets = {T: masters[T][0] for T in TARGETS}

    # (i) identity: every-cluster-once reproduces the point estimate
    worst_i, n_id = 0.0, 0
    for bid in files:
        for T in TARGETS:
            d, e, cl = _rowset(dm[(bid, T)], frames[(T, "bind", PRIMARY)],
                               pos_sets[T], roster_site[bid])
            if np.isnan(d).any():
                continue
            nk = len(np.unique(cl))
            ids = np.arange(nk, dtype=np.int64).reshape(1, nk)
            one = p3c.pos_cluster_boot_from_ids(d, e, cl, ids)[0]
            worst_i = max(worst_i, abs(one - p3c.spearman(d, e)))
            n_id += 1
    gate("G-R3(i) every-cluster-once reproduces rho (all scored "
         "backgrounds x 2 targets)", "PASS" if worst_i < TOL_12 else "FAIL",
         f"max|diff| = {worst_i:.3e} over {n_id} rho computations",
         f"tolerance {TOL_12}")

    # (ii) draw-by-draw vs the slow reference, first three in roster order
    order = roster.sort_values("roster_order").background_id.astype(str)
    first3 = [b for b in order if b in files][:3]
    if len(first3) < 3:
        gate("G-R3(ii) draw-by-draw vs slow reference (3 real "
             "backgrounds)", "FAIL", f"only {len(first3)} scored",
             f"frozen G-R3 requires three (N_REF={N_REF}, seed {SEED})")
    else:
        worst_ii = 0.0
        for bid in first3:
            for T in TARGETS:
                d, e, cl = _rowset(dm[(bid, T)],
                                   frames[(T, "bind", PRIMARY)],
                                   pos_sets[T], roster_site[bid])
                ids, _ = p3c.draw_ids(cl, N_REF, seed=SEED)
                fast = p3c.pos_cluster_boot_from_ids(d, e, cl, ids)
                slow = p3c.reference_boot(d, e, cl, ids)
                dd = float(np.max(np.abs(fast - slow)))
                note(f"  {bid}/{T}: {N_REF} draws, max|corrected - "
                     f"reference| = {dd:.3e}")
                worst_ii = max(worst_ii, dd)
        gate("G-R3(ii) draw-by-draw vs slow reference (3 real "
             "backgrounds x 2 targets)", "PASS" if worst_ii < TOL_12
             else "FAIL", f"max|diff| = {worst_ii:.3e}",
             f"tolerance {TOL_12}")

    # (iii) Phase 1 CI reproduction, fixed N
    rule(f"G-R3(iii) -- PHASE 1 CI REPRODUCTION ON THE MTHFR ANCHOR ROWS "
         f"(fixed N={G3III_N})")
    quote(PREREG159, 140, 145, "frozen Phase 1 CI endpoints (scripts/159)")
    from scripts.lib import phase2_diag as pdg        # noqa: E402
    _, Aobj = pdg.build(verbose=False)
    ar = Aobj.a222v_rows
    draws = p3c.pos_cluster_boot(ar.delta.to_numpy(float),
                                 ar.own_e_b.to_numpy(float),
                                 ar.position.to_numpy(),
                                 n_boot=G3III_N, seed=SEED)
    lo, hi, n_fin = p3c.pct_ci(draws)
    d_lo, d_hi = abs(float(lo) - T_CI_LO), abs(float(hi) - T_CI_HI)
    note(f"  anchor rows {len(ar):,} / {ar.position.nunique()} positions; "
         f"CI [{lo:.12f}, {hi:.12f}] vs frozen [{T_CI_LO}, {T_CI_HI}]")
    gate("G-R3(iii) Phase 1 CI reproduces (each endpoint < 1e-9, all "
         f"{G3III_N} draws finite)",
         "PASS" if (d_lo < TOL_9 and d_hi < TOL_9
                    and n_fin == G3III_N) else "FAIL",
         f"|diff| lo {d_lo:.3e}, hi {d_hi:.3e} ({n_fin} finite of "
         f"{G3III_N} draws)",
         f"tolerance {TOL_9}; the routine under test is the same "
         f"p3c.pos_cluster_boot used for 6a")


# ==========================================================================
# 9. section 5: rho_b -> p_abs family -> outcome word (frozen s5)
# ==========================================================================
def run_section5(masters, frames, files, dm, roster):
    rule("SECTION 5 -- rho_b, p_abs/p_neg/p_pos AND THE OUTCOME WORD "
         "(frozen s5)")
    quote(P3C, 292, 312, "phase3_common.p_spec -- the frozen formula as "
                         "actually executed")
    roster_site = dict(zip(roster.background_id, roster.site.astype(int)))
    roster_arm = dict(zip(roster.background_id, roster.arm.astype(str)))
    results, rho_rows = {}, []
    for ph in PHENOS:
        for mk in MASKS:
            for T in TARGETS:
                frame = frames[(T, ph, mk)]
                pos = masters[T][0]
                tb = target_bg_id(roster, T)     # e.g. N501Y -> TGT_N501Y
                rhos = {}
                for bid in files:
                    r, n, *_ = rho_of(dm[(bid, T)], frame, pos,
                                      roster_site[bid])
                    rhos[bid] = (r, n)
                    rho_rows.append(dict(
                        target=T, phenotype=ph, mask=mk,
                        is_primary=(mk == PRIMARY), background_id=bid,
                        arm=roster_arm[bid], site=roster_site[bid],
                        rho_b=r, n_variants=n))
                null_ids = null_members(roster, T)
                missing = [b for b in null_ids if b not in files]
                has_t = tb in files
                complete = (not missing) and has_t
                rec = dict(complete=bool(complete), n_null=len(null_ids),
                           n_scored_null=len(null_ids) - len(missing),
                           missing_null=missing, target_file=bool(has_t),
                           target_bg_id=tb)
                if complete:
                    p = pvals(rhos[tb][0], [rhos[b][0] for b in null_ids])
                    w = outcome_word(p["p_abs"])
                    rec.update(p)
                    rec["outcome_word"] = w
                    tag = "" if mk == PRIMARY else \
                        "   [SENSITIVITY, non-deciding]"
                    note(f"  {T} {ph}/{mk}: nulls {p['n_null']}/"
                         f"{len(null_ids)} scored, rho_T = "
                         f"{p['rho_target']:.4f}, p_abs = {p['p_abs']:.4f} "
                         f"(k = {p['k_abs']}), p_neg = {p['p_neg']:.4f}, "
                         f"p_pos = {p['p_pos']:.4f} -> {w}{tag}")
                else:
                    note(f"  {T} {ph}/{mk}: STAGE INCOMPLETE "
                         f"({len(null_ids) - len(missing)}/{len(null_ids)} "
                         f"null members scored"
                         f"{', T file missing' if not has_t else ''}) -> "
                         f"NO outcome word (R5)")
                results[(T, ph, mk)] = rec
    return results, rho_rows


# ==========================================================================
# 10. finalisation: G-157-2, G-157-3, summary, limitations, exit code
# ==========================================================================
def _jdefault(o):
    return o.item() if hasattr(o, "item") else str(o)


def finish(out_dir, mode, t0, present_ids, roster_ids, results, payload,
           inputs_only=False):
    rule("G-157-2 -- THIS SCRIPT NEVER TOUCHES TORCH OR ESM")
    mods = [m for m in ("torch", "esm") if m in sys.modules]
    gate("G-157-2 torch/esm not in sys.modules", "FAIL" if mods else "PASS",
         f"imported: {mods if mods else 'none'}",
         "A5g is analysis-only; the model ran in A5e")

    if mode == "full":
        missing = sorted(set(roster_ids) - set(present_ids))
        gate("G-157-3 stage completeness (full mode): every roster "
             "background scored", "FAIL" if missing else "PASS",
             f"{len(set(roster_ids) & set(present_ids))}/{len(roster_ids)} "
             f"files + wt_arm",
             f"missing: {missing[:5]}" if missing else "complete")
    else:
        note("  G-157-3 not applicable in smoke mode: its out-dir holds a "
             "subset by construction; full mode gates stage completeness")

    if payload is not None:
        payload["gates"] = [[n, v, val, nt] for n, v, val, nt in GATES]
        path = Path(out_dir) / f"analysis_results_{mode}.json"
        path.write_text(json.dumps(payload, indent=1, default=_jdefault)
                        + "\n")
        note(f"wrote {rel(path)}")

    rule(f"SUMMARY -- A5g / RBD analysis (mode {mode})")
    for name, v, val, nt in GATES:
        print(f"  [{v}] {name}: {val}  {nt}")
    n_pass = sum(1 for _, v, _, _ in GATES if v == "PASS")
    ok = n_pass == len(GATES)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS -> "
          f"{'A5g PASSES' if ok else 'A5g FAILS'}")

    if results:
        rule("PRIMARY OUTCOME (frozen s5: binding, n_bc >= 3, both "
             "targets, NO multiplicity adjustment)")
        for T in TARGETS:
            rec = results.get((T, "bind", PRIMARY), {})
            if rec.get("complete"):
                print(f"    {T:<7} p_abs = {rec['p_abs']:.4f}  ->  "
                      f"{rec['outcome_word']}   (rho_T "
                      f"{rec['rho_target']:.4f}, k = {rec['k_abs']} of "
                      f"{rec['n_null']} nulls)")
            else:
                print(f"    {T:<7} stage incomplete "
                      f"({rec.get('n_scored_null', 0)}/"
                      f"{rec.get('n_null', '?')} nulls scored) ->  no "
                      f"outcome word exists for this run")
        note("  sensitivities (n_bc >= 1 / >= 5) and the expression "
             "phenotype were printed above; none of them decides (R2/R7)")
        note("  the two targets are two looks with no multiplicity "
             "adjustment, by the frozen block's own instruction")

    limitations()
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if ok else 3)


def main():
    ap = argparse.ArgumentParser(
        description="A5g: RBD regime analysis + G-SYN (no torch, no esm)")
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--out-dir", default=None,
                    help="override the mode's score out-dir")
    ap.add_argument("--inputs-only", action="store_true",
                    help="G-157-1/5, G-R1, G-R2, G-R4, G-157-4 only")
    args = ap.parse_args()

    out_dir = (Path(args.out_dir).resolve() if args.out_dir else
               (OUT_REAL if args.mode == "full" else OUT_SMOKE))
    t0 = time.time()
    rule(f"A5g -- RBD REGIME ANALYSIS (scripts/157) -- mode '{args.mode}',"
         f" out-dir {rel(out_dir)}")
    nondefault = (N_BOOT != 10000 or N_REF != 2000 or N_SYN_NULL != 100
                  or SEED != 0)
    note(f"env: N_BOOT={N_BOOT} N_REF={N_REF} N_SYN_NULL={N_SYN_NULL} "
         f"SEED={SEED}{'  (NON-DEFAULT)' if nondefault else '  (defaults)'}")
    note("NO torch, NO esm by construction; G-157-2 proves it at exit")

    # ---- G-157-1 input pins ----------------------------------------------
    rule("G-157-1 -- INPUT PINS (sha256 re-derived on this machine)")
    bad = []
    for p, sha in SHAS.items():
        got = sha256_of(p) if p.exists() else "MISSING"
        ok = got == sha
        note(f"  {p.relative_to(ROOT)}: {got} "
             f"{'==' if ok else '!='} pinned {sha}")
        if not ok:
            bad.append(str(p.relative_to(ROOT)))
    if PDB.exists():
        got = sha256_of(PDB)
        ok = got == PDB_SHA
        note(f"  {PDB.relative_to(ROOT)} (optional 6c input): {got} "
             f"{'==' if ok else '!='} pinned {PDB_SHA}")
        if not ok:
            bad.append(str(PDB.relative_to(ROOT)))
    else:
        note(f"  {PDB.relative_to(ROOT)}: absent (optional; 6c falls back "
             f"to sequence distance only, R10)")
    gate("G-157-1 input pins", "FAIL" if bad else "PASS",
         f"{len(SHAS)} required (+1 optional structure) checked, "
         f"{len(bad)} mismatches",
         "; ".join(bad) if bad else "all match their pinned sha256")

    # ---- load + G-157-5 + G-R1/G-R2 --------------------------------------
    sites, ref = load_reference()
    et = pd.read_csv(ET_CSV)
    roster = pd.read_csv(ROSTER)
    note(f"e_T: {len(et)} rows x {len(et.columns)} cols; roster: "
         f"{len(roster)} backgrounds, arms "
         f"{roster.arm.value_counts().to_dict()}")
    masters, frames, excl = load_frames(et)
    g5_ok = all(excl[T] == 0 for T in TARGETS)
    gate("G-157-5 e_T excludes T's own site (frozen s2)",
         "PASS" if g5_ok else "FAIL",
         "; ".join(f"{T}: {excl[T]} rows at site {TARGET_SITE[T]}"
                   for T in TARGETS), "re-derived here (R2)")

    fvar = pd.read_csv(FVAR)
    g1_ok, bad_rows, n_fvar, wuhan_rows = check_reference_gates(fvar)
    gate("G-R1 N501Y and E484K references differ from Wuhan-Hu-1 by "
         "exactly N501Y / E484K (frozen s7)",
         "PASS" if g1_ok else "FAIL",
         f"computed from the data's own wildtype column over "
         f"{n_fvar} rows", "constants frozen in the block")
    gate("G-R2 every data row's wildtype == its label's own reference "
         "(frozen s7)", "PASS" if not bad_rows else "FAIL",
         f"{n_fvar} rows, {len(bad_rows)} mismatches; {wuhan_rows} rows "
         f"differ from the WUHAN sequence (expected: the labels' "
         f"background-substitution sites)",
         str(bad_rows[:3]) if bad_rows else
         "per-target references from scripts/162 docstring R4 (A5b)")

    # ---- G-R4 + G-157-4 ---------------------------------------------------
    rule("G-R4 -- SCORE FILES IN THIS MODE'S OUT-DIR (frozen s7)")
    wt_map, files, cov, issues, wt_rows = load_scores(out_dir, roster, ref)
    if wt_map is None:
        note(f"  WT arm unavailable: {issues[0]}")
    min_cov = min(cov.values()) if cov else float("nan")
    g4_ok = (wt_map is not None and not issues)
    gate("G-R4 every scored file >= 95% of 201 sites, digest/bg_id/shape "
         "clean, WT arm present", "PASS" if g4_ok else "FAIL",
         f"{len(files)}/{len(roster)} roster files, wt_arm "
         f"{'present' if wt_map else 'MISSING'} ({wt_rows} rows), "
         f"min coverage {min_cov:.4f}",
         "; ".join(issues[:3]) if issues else "all scored files clean")

    roster_site = dict(zip(roster.background_id, roster.site.astype(int)))
    dm = delta_masters(files, wt_map, masters) if wt_map else {}
    gaps = (join_gaps(files, dm, roster_site, masters) if wt_map
            else [("no_wt_arm", "-", -1)])
    gate("G-157-4 delta join: zero gaps outside b's own site",
         "PASS" if not gaps else "FAIL",
         f"{len(dm)} (background, target) delta arrays, {len(gaps)} with "
         f"gaps", str(gaps[:3]) if gaps else
         "score side and WT side both present for every frame row")

    if args.inputs_only:
        finish(out_dir, args.mode, t0, list(files),
               list(roster.background_id), None, None, inputs_only=True)

    # ---- G-R3, section 5, structure, 6a-6h, G-SYN ------------------------
    run_g3(masters, frames, files, dm, roster)
    results, rho_rows = run_section5(masters, frames, files, dm, roster)

    rule("SECONDARIES (frozen s6) -- 6a..6e at the primary mask, both "
         "phenotypes; 6f/6h pointers")
    ca, ca_status = load_structure(ref)
    note(f"structure: {ca_status}")
    sec = run_secondaries(roster, masters, frames, dm, files, results, ca)

    gsyn = run_g_syn(roster, masters, frames)
    for T in TARGETS:
        s, nul = gsyn[T]["signal"], gsyn[T]["null"]
        gate(f"G-SYN(i) planted signal recovered for {T} "
             f"(p_abs <= 0.05 and the frozen word)",
             "PASS" if (s["p_abs"] <= ALPHA_ABS
                        and s["w"] == "RBD-REPRODUCES") else "FAIL",
             f"p_abs = {s['p_abs']:.4f}, word = {s['w']}, rho_T = "
             f"{s['rho_target']:.4f} vs max|rho_null| = "
             f"{s['max_abs_null']:.4f}, floor {s['expected_floor']:.4f}",
             f"seed 0; {s['n_null']} null members")
        gate(f"G-SYN(ii) planted null not claimed for {T} "
             f"(<= 15% of draws <= 0.05, median > 0.05, no NaN)",
             "PASS" if (nul["frac"] <= 0.15 and nul["median"] > ALPHA_ABS
                        and nul["n_nan"] == 0) else "FAIL",
             f"{nul['fires']}/{nul['n_draws']} draws <= 0.05 "
             f"(frac {nul['frac']:.3f}), median p_abs "
             f"{nul['median']:.4f}, NaN {nul['n_nan']}",
             "seeds 1000+i; a FAIL is never re-rolled (R15)")

    # ---- outputs ----------------------------------------------------------
    rho_path = out_dir / f"rho_b_{args.mode}.csv"
    pd.DataFrame(rho_rows).to_csv(rho_path, index=False)
    note(f"wrote {rel(rho_path)} "
         f"({len(rho_rows)} rows: target x frame x scored background)")
    payload = dict(
        script="scripts/157_rbd_regime_analysis.py",
        mode=args.mode, out_dir=str(rel(out_dir)),
        env=dict(N_BOOT=N_BOOT, N_REF=N_REF, N_SYN_NULL=N_SYN_NULL,
                 SEED=SEED),
        pins={str(k.relative_to(ROOT)): v for k, v in SHAS.items()},
        structure=ca_status,
        section5={f"{T}/{ph}/{mk}": results[(T, ph, mk)]
                  for ph in PHENOS for mk in MASKS for T in TARGETS},
        outcomes_primary={T: results[(T, "bind", PRIMARY)].get(
            "outcome_word") for T in TARGETS},
        secondaries=sec, g_syn=gsyn,
        rho_table=str(rel(rho_path)),
        gates=[[n, v, val, nt] for n, v, val, nt in GATES],
        elapsed_s=round(time.time() - t0, 1),
    )
    finish(out_dir, args.mode, t0, list(files), list(roster.background_id),
           results, payload)


if __name__ == "__main__":
    main()
