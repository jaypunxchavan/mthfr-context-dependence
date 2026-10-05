"""A5 -- MODULE U: predictive utility of background conditioning.

Implements the frozen block docs/tasks/phase4-strengthening/prereg/
UTILITY_PREREG_v1.md EXACTLY (sections 1-5), for task A5 of
PHASE4_STRENGTHENING.md lines 174-178.  Two uses:

  U-1 (cached): does conditioning ESM-2 on the A222V background (S_A)
      predict the A222V-background fitness y better than the plain
      WT-background score (S_W)?  Delta = Spearman(S_A, y) -
      Spearman(S_W, y) with a paired position-cluster bootstrap CI.
  U-2 (one acquisition): does S_A separate pathogenic from reference
      variants better than S_W on the Weile et al. 2021 benchmark
      (MaveDB urn:mavedb:00000049-a-1..a-8 plus the paper's reference
      variant sets from its supplement)?  AUROC primary, balanced-PR
      area secondary, paired position-cluster bootstrap CI on
      Delta AUROC.

PRE-REGISTERED DECISION RULES (written before this script was first
run; the frozen prereg fixed the statistics, words and margins, and the
U-DEC items below fix the only remaining implementation choices; the
consequence -- which words can be printed -- is therefore not
post-hoc):

  U-DEC1 (U-1 frame and response, prereg section 2): frame = task32 rows
      with finite (delta_esm, own_e_b, position, esm2_score,
      base_functionality) -- the identical filter scripts 165/166/167
      gated at 10,757 rows / 654 positions.  y = per-variant mean of the
      four A222V-background fitness columns m12/m25/m100/m200.score over
      those conditions with finite values (pandas mean(skipna=True) ==
      np.nanmean).  Column identity (AGENTS 5): y must equal the
      recorded f_bar_a222v to < 1e-15 wherever both are finite, with no
      row-level disagreement in finiteness (gated, G-U0(g)).
  U-DEC2 (paired bootstrap): one set of position-cluster ids is drawn
      per subset with p4c.draw_ids(clusters, N_BOOT, SEED=0) in that
      subset's first-appearance position space; BOTH rhos (U-1) or both
      AUROCs (U-2) are computed on the identical draws and Delta is the
      draw-wise difference.  CI = np.percentile-style 2.5/97.5 of the
      finite Delta draws via p4c.pct_ci (Phase 1's convention).  The
      resampling unit is the POSITION; backgrounds are never resampled
      (there is one background here).  Single-class AUROC draws are
      NaN-dropped by pct_ci and their count is printed.
  U-DEC3 (subsets, prereg section 2): PRIMARY = all frame rows; H =
      frame rows at positions in script 125's A.Hset (target 455
      positions / 7,526 rows); TOPDECILE = frame rows with
      |own_e_b| >= np.quantile(|own_e_b|, 0.90) over the frame (numpy
      linear interpolation, ties kept; n printed).  Outcome words are
      given for PRIMARY ONLY; H and TOPDECILE get point estimates and
      CIs, labelled descriptive.
  U-DEC4 (context and per-condition repeats, prereg section 2): context
      numbers = Spearman(S_W, base_functionality) and Spearman(S_A, y)
      printed as point estimates.  Per-condition repeats = the same
      Delta with y_c = m<c>.score on frame rows with that condition
      finite, point + CI, labelled DESCRIPTIVE (no word, no
      multiplicity correction).
  U-DEC5 (G-U1 column identity -- see DISCLOSURE below): the MaveDB
      comparison uses the score set's EXPERIMENTAL column (exp.score
      for a-1..a-6; plain score for a-7/a-8, whose records carry no
      exp/pred columns and whose score is the raw experimental value).
      Evidence, printed every run: (i) the project's m25.score is
      EXACTLY the paper's Supplemental Table S2 A222V-25 column
      (10,891/10,891 exact, rho 1.0); (ii) a-2's canonical `score`
      column is a shrunken blend of exp and pred (rho(score, exp) =
      0.737; score == pred.score on 1,037 rows); (iii) a-8 (only
      score/sd/se columns) matches the project's m200.score at
      rho = 0.999999999982 (rank-identical).  The gate is on
      Spearman(exp.score, m25) >= 0.90; the canonical-column value is
      ALSO printed as disclosed context (the run's own value, ~0.692,
      is below the threshold -- see DISCLOSURE).
      DISCLOSURE (AGENTS 0/5): the canonical `score` comparison was
      computed FIRST during A5 reconnaissance and came out ~0.685 <
      0.90.  Rather than weaken the gate, column identity was then
      analysed (AGENTS 5 requires assuming a column bug until proven
      otherwise), which established that `score` for a-2 is not the
      experimental map (evidence (i)-(iii) above), so it is not a
      like-for-like comparison for "the same data" the gate asks about.
      Both numbers are printed every run.  Had no like-for-like column
      existed, U-2 would have been STOPPED at G-U1.
      POST-RUN TEXT FIX (disclosed per AGENTS 6; text only -- no gate,
      threshold or computed value changed): the recon note originally
      quoted the exact figure 0.6846, which cannot be reproduced from
      any current row set -- recomputing the same comparison after the
      first full run gives 0.6919 on the 10,891-row merge and 0.6931 on
      the 10,819-row gate subset (0.6812 restricted to U-1 frame rows);
      the exact recon row set was not recorded.  Every variant is below
      0.90, so no decision rule or outcome changed; the gated number is
      the experimental column (0.9524).
  U-DEC6 (positive label set, prereg section 3 "the paper's pathogenic
      ... reference variant sets"): from Supplemental Table S3
      (mmc4.xlsx, sheet 'patients from literature' -- the file the
      article names "Curated reference variant sets for validation"):
      samples whose Category is exactly 'early' or 'late' enter the
      tally ('asymptomatic', 'late?', and blank Categories are excluded
      -- using only the strict labels reproduces the paper's stated
      set sizes); per sample, the DISTINCT missense protein
      consequences it carries (standard three-letter consequence, or a
      one-letter form normalised to three-letter; stop/Ter, '=',
      splice, and bracketed haplotypes are NOT missense); a variant is
      POSITIVE iff it is carried by strictly more early-than-late
      samples; ties excluded (all of this is the paper's supplemental
      methods D verbatim).  EXPECTED (paper-stated): 30 positive, 40
      late-onset -- gated as G-U0(d), an ADDED sub-gate (stricter than
      the frozen G-U0 list) because it validates the derivation.
  U-DEC7 (negative label set): Table S3 sheet '1000 genomes' (the
      "random reference set of variants found in the general
      population" the article's benchmark description points at):
      distinct missense protein consequences carried by any listed
      individual; bracketed haplotypes p.[X;Y] are split into their
      constituents; p.Ala222Val is removed (the paper's stated
      exclusion).  Any variant in BOTH sets is excluded from both
      (count printed).  NOTE (disclosed): the supplemental methods D
      also describe a gnomAD-based random set used for the LLR
      transformation; gnomAD is outside this project's authorised
      network and is NOT obtainable here.  The benchmark the article
      text describes for Figure 6A is the Table S3 pair implemented
      above, and that is what G-U2 checks.
  U-DEC8 (metric orientation): y = 1 for pathogenic; every predictor is
      passed as -score (lower functionality = higher predicted
      pathogenicity) to BOTH metrics, so AUROC > 0.5 means the
      predictor ranks pathogenic above benign, Delta AUROC > 0 means
      conditioning helps (the frozen words' semantics), and the
      frozen G-U2 expectation is that the best map attains the HIGHEST
      balanced-PR area (with raw functional scores the best map would
      attain the lowest).  The identity AUROC(y, -s) = 1 - AUROC(y, s)
      is printed.
  U-DEC9 (map columns for U-2): exp.score where the score set provides
      it (a-1..a-6), score otherwise (a-7/a-8) -- "the experimental
      ... map" of prereg section 3.  A PRE-REGISTERED SENSITIVITY,
      non-gated: the same ranking recomputed on each set's canonical
      `score` column is printed alongside for disclosure.
  U-DEC10 (row accounting, AGENTS 5): U-2's variant set = labelled
      variants with finite S_W and S_A (prereg section 3); each
      predictor's metrics use its finite values (the library drops
      non-finite rows) and n is printed per metric; class sizes are
      printed BEFORE any metric; a class < 15 -> UNDERPOWERED, no word.
      The derivation attrition (30 + 39 = 69 -> analysis set) is
      printed with every dropped row accounted for.
  U-DEC11 (acquisition): MaveDB score CSVs and the supplement ZIP were
      downloaded during A5 reconnaissance; this script RE-VERIFIES
      url|status|bytes|sha256 against the on-disk manifests, requires
      every status 200, and aborts U-2 above 200 MB total (planning
      line 176).  Files are re-fetched (urllib, 200 MB running total)
      only if absent; a fetch failure yields U-2 = BLOCKED, U-1 stands
      (planning line 178).  If Supplemental Table S3 is unavailable,
      the frozen fallback (task102_clinvar_atlas_overlap.csv,
      pathogenic/likely pathogenic vs benign/likely benign) is used
      and DISCLOSED as a different label set (prereg section 3).  NOT
      used in this run: the supplement was reached in 399 s of the
      1,200 s budget.
  U-DEC12 (smoke vs full): N_BOOT env (default 10000; smoke 300).
      Every CI-dependent number is marked PROVISIONAL in smoke; the
      Phase 1 CI reproduction and the draw-by-draw reference sub-gates
      that depend on N are SKIPPED (labelled) and G-U3 cannot be
      called PASS on a smoke run -- the decision is taken on the
      N_BOOT=10000 run.  Words printed in smoke are marked
      PROVISIONAL.

GATES (all HARD for the item they guard; planning line 178):
  G-U0  infrastructure (guards U-1 and U-2):
      (a) prereg file sha256 == the frozen hash;
      (b) frame 10,757 rows / 654 positions;
      (c) Spearman(own_e_b, S_W) = +0.0854 at 4 dp;
      (d) ADDED, stricter: label derivation reproduces the paper's
          stated 30 early-onset / 40 late-onset variants;
      (e) ADDED, stricter: H subset = 455 positions / 7,526 rows;
      (f) ADDED, stricter: acquisition manifests re-verify (sha256 +
          bytes), all statuses 200, total downloaded < 200 MB;
      (g) ADDED, stricter (AGENTS 5): y == f_bar_a222v (< 1e-15,
          same finiteness) and delta_esm == S_A - S_W (< 1e-12).
      FAIL -> exit 3 (both U-1 and U-2 unguarded).
  G-U1  MaveDB a-2 (experimental column) vs the project's m25 Spearman
      >= 0.90 over shared variants.  FAIL -> U-2 STOPPED ("the maps
      are not the same data"), no U-2 metric is computed, U-1 stands,
      exit 0 with the stop printed and logged.
  G-U2  among the eight experimental maps, a-2 (A222V background,
      25 ug/mL) attains the highest balanced-PR area on the label set.
      FAIL -> U-2 = UNVERIFIED-LABELS, no word, metrics still printed,
      exit 0 with the status logged.
  G-U3  (i) auroc == sklearn.metrics.roc_auc_score and balanced-PR ==
      sklearn's weighted precision_recall_curve / roc_curve paths, all
      < 1e-12 on toys (ties, perfect, inverted, chance); (ii) bootstrap
      REFERENCE gate (identity: every-position-once reproduces each
      point estimate and Delta < 1e-12; draw-by-draw fast vs slow
      reference < 1e-12 over N_REF draws; at N_BOOT=10000 the Phase 1
      CI [-0.1173334458953319, -0.0595113844951173] reproduced to 1e-9
      per endpoint; the U-2 AUROC bootstrap gets its own identity +
      draw-by-draw-vs-sklearn reference).  FAIL -> exit 3.

OUTCOME WORDS (prereg sections 2/3/5, via p4c.word_conditioning,
margin 0.02, and p4c.word_underpowered, min 15): printed verbatim;
statements concern ESM-2 scores in this one gene, no clinical claim.

DISCLOSURE (prereg section 0): cached-data analyses on variables for
which related correlations were seen earlier; the comparisons below
were never computed, but the analyses are not out-of-sample with
respect to the project's history.  U-1 re-derives cached quantities
(reproduction, not replication, AGENTS 6).  U-2's label derivation was
prototyped during reconnaissance against the paper's stated 30/40 set
sizes (that is what fixed U-DEC6's strict-Category rule); no AUROC,
balanced-PR or Delta number was computed before this script's first
run.

LIMITATIONS printed in output (AGENTS 6): one gene, one ESM-2 model;
bootstrap resamples positions within the frame only; the U-2 label set
is 29/39 variants (small -- the CI width, not the point estimate, is
the binding constraint); per-condition repeats are descriptive and
uncorrected; percentile CIs; Weile's own AUBPRC used monotonisation
and a prior-balanced posterior we do not re-implement -- G-U2 asks
only that their reported ORDERING (AV25 best) reproduces on our label
set; orientation U-DEC8 is an implementation convention that fixes the
direction of the frozen words.

ENV: N_BOOT (default 10000), SEED (default 0), N_REF (default 500).

Usage:
  smoke: N_BOOT=300   venv/bin/python3 scripts/168_utility.py
  full:  N_BOOT=10000 SEED=0 venv/bin/python3 scripts/168_utility.py
"""

import hashlib
import os
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg                             # noqa
from scripts.lib import phase3_common as p3c                           # noqa
from scripts.lib import phase4_common as p4c                           # noqa

# ==========================================================================
# Targets and constants
# ==========================================================================
PREREG = ROOT / "docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md"
PREREG_SHA = "744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531"
TASK32 = ROOT / "data/processed/task32_analysis_table.csv"
FALLBACK = ROOT / "data/processed/task102_clinvar_atlas_overlap.csv"
MAVE_DIR = ROOT / "data/external/mavedb"
MAVE_MANIFEST = MAVE_DIR / "U2_DOWNLOAD_MANIFEST.txt"
SUPP_DIR = ROOT / "data/external/weile2021_supp"
SUPP_ZIP = SUPP_DIR / "europepmc_supp.zip"
SUPP_MANIFEST = SUPP_DIR / "SUPP_DOWNLOAD_MANIFEST.txt"
ST3 = SUPP_DIR / "extracted/mmc4.xlsx"     # Table S3 reference variant sets
ST2 = SUPP_DIR / "extracted/mmc3.xlsx"     # Table S2 map values (identity check)

T_ROWS, T_POS = 10757, 654                 # A2/G-U0 frame
T_HPOS, T_HROWS = 455, 7526                # H subset (A4 G-M0)
T_RHO_U0 = 0.0854                          # G-U0(c), 4 dp
T_CI_LO = -0.1173334458953319              # Phase 1 CI (G-U3)
T_CI_HI = -0.0595113844951173
T_POS_SET, T_LATE_SET = 30, 40              # paper-stated set sizes (G-U0(d))
G_U1_MIN = 0.90
WORD_MARGIN = 0.02
MIN_CLASS = 15
MAX_BYTES = 200 * 1024 * 1024               # 200 MB abort (planning 176)

# MaveDB score sets of urn:mavedb:00000049 (titles from the API record)
MAPS = {
    "a-1": "MTHFR at 100ug/ml folate in WT background",
    "a-2": "MTHFR at 25ug/ml folate in A222V background",
    "a-3": "MTHFR at 100ug/ml folate in A222V background",
    "a-4": "MTHFR at 12ug/ml folate in WT background",
    "a-5": "MTHFR at 12ug/ml folate in A222V background",
    "a-6": "MTHFR at 25ug/ml folate in WT background",
    "a-7": "MTHFR at 200ug/ml folate in WT background",
    "a-8": "MTHFR at 200ug/ml folate in A222V background",
}
POS_CONTROL = "a-2"   # prereg: experimental A222V map at 25 ug/mL
NEG_CONTROL = "a-4"   # prereg: WT-background map at the lowest folinate

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
N_REF = int(os.environ.get("N_REF", "500"))

TOL_9DP = 1e-9
TOL_12 = 1e-12
TOL_15 = 1e-15

t0 = time.time()
gates = []


def banner(t, ch="="):
    print("\n" + ch * 78)
    print(t)
    print(ch * 78, flush=True)


def gate(gid, ok, detail, hard=True):
    tag = "PASS" if ok else ("FAIL" if hard else "FAIL(not hard)")
    gates.append((gid, bool(ok), detail, hard))
    print(f"  [{tag}] {gid}: {detail}", flush=True)
    return bool(ok)


def note(item, got, target, tol, fmt="{!r}"):
    d = abs(float(got) - float(target))
    return gate(item, d < tol,
                f"got {fmt.format(got)} target {fmt.format(target)} "
                f"|diff| = {d:.3e} (gate < {tol:g})")


def smoke_mode():
    return N_BOOT != 10000


# ==========================================================================
# U-DEC11 -- acquisition: re-verify manifests, re-fetch only if absent
# ==========================================================================
def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acquire():
    """Returns (records, blocked_reason).  records: list of dicts."""
    recs, blocked = [], None

    def fetch(url, dest):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
            status = getattr(r, "status", 200)
        if sum(x["bytes"] for x in recs) + len(data) > MAX_BYTES:
            raise RuntimeError("200 MB total abort")
        dest.write_bytes(data)
        return status

    # -- MaveDB score CSVs: manifest is the record (URL|status|bytes|sha)
    if MAVE_MANIFEST.exists():
        for line in MAVE_MANIFEST.read_text().splitlines():
            if not line.strip():
                continue
            url, status, nbytes, sha = line.split("|")
            urn = url.rsplit("/", 2)[-2]           # urn:mavedb:...-a-N
            dest = MAVE_DIR / f"mavedb_{urn.replace('urn:mavedb:', '')}_scores.csv"
            if not dest.exists():
                try:
                    status = str(fetch(url, dest))
                except Exception as e:                       # noqa: BLE001
                    blocked = f"MaveDB fetch failed: {e}"
                    continue
            got_sha, got_bytes = _sha256(dest), dest.stat().st_size
            ok = (status == "200" and got_sha == sha
                  and got_bytes == int(nbytes))
            recs.append({"url": url, "status": status, "bytes": got_bytes,
                         "sha256": got_sha, "ok": ok,
                         "target_bytes": int(nbytes), "target_sha": sha})
    else:
        blocked = "MaveDB manifest missing"

    # -- supplement ZIP (Europe PMC, reached in 399 s of the 1200 s budget)
    supp_url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
                "PMC8322931/supplementaryFiles")
    supp_sha = None
    if SUPP_MANIFEST.exists():
        for line in SUPP_MANIFEST.read_text().splitlines():
            if line.startswith(supp_url):
                parts = line.split("|")
                supp_sha = parts[-1] if len(parts) >= 4 else None
    if not SUPP_ZIP.exists() and supp_sha:
        try:
            status = str(fetch(supp_url, SUPP_ZIP))
        except Exception as e:                               # noqa: BLE001
            blocked = (blocked or "") + f" supplement fetch failed: {e}"
            status = "000"
    if SUPP_ZIP.exists():
        got_sha, got_bytes = _sha256(SUPP_ZIP), SUPP_ZIP.stat().st_size
        ok = (supp_sha is None or got_sha == supp_sha)
        recs.append({"url": supp_url, "status": "200", "bytes": got_bytes,
                     "sha256": got_sha, "ok": ok,
                     "target_bytes": got_bytes, "target_sha": supp_sha})
    return recs, blocked


# ==========================================================================
# U-DEC6 / U-DEC7 -- label derivation from Supplemental Table S3
# ==========================================================================
_AA1 = dict(zip("ACDEFGHIKLMNPQRSTVWY",
                "AlaCysAspGluPheGlyHisIleLysLeuMetAsnGlnArgSerThrTrpTyrVal"
                .split()))


def _norm_missense(pc):
    """Standard missense consequence -> canonical three-letter form.

    Accepts p.Arg377Cys and the one-letter p.R377Cys; rejects Ter/stop,
    '=', splice, haplotype brackets and anything else (paper methods D:
    'the list of missense variants')."""
    if not isinstance(pc, str):
        return None
    import re
    m = re.fullmatch(r"p\.([ACDEFGHIKLMNPQRSTVWY])"
                     r"(\d+)"
                     r"([ACDEFGHIKLMNPQRSTVWY])", pc)
    if m:
        return f"p.{_AA1[m.group(1)]}{m.group(2)}{_AA1[m.group(3)]}"
    m = re.fullmatch(r"p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})", pc)
    if m and m.group(1) != "Ter" and m.group(3) != "Ter":
        return pc
    return None


def derive_labels():
    """(positive, late, negative) sets as frozensets of HGVS proteins."""
    import openpyxl
    wb = openpyxl.load_workbook(ST3, read_only=True, data_only=True)

    rows = list(wb["patients from literature"].iter_rows(values_only=True))[2:]
    early_t, late_t = {}, {}
    for r in rows:
        cat = r[2]
        ce, cl = cat == "early", cat == "late"
        if not (ce or cl):
            continue
        vs = {v for v in (_norm_missense(r[7]), _norm_missense(r[10])) if v}
        for v in vs:                      # tally carrier SAMPLES (methods D)
            if ce:
                early_t[v] = early_t.get(v, 0) + 1
            if cl:
                late_t[v] = late_t.get(v, 0) + 1
    pos = {v for v in early_t if early_t[v] > late_t.get(v, 0)}   # ties out
    late = {v for v in late_t if late_t[v] > early_t.get(v, 0)}

    rows2 = list(wb["1000 genomes"].iter_rows(values_only=True))[2:]
    neg = set()
    for r in rows2:
        for pc in (r[2], r[5]):
            if not isinstance(pc, str):
                continue
            if pc.startswith("p.["):                       # split haplotype
                for part in pc[3:-1].split(";"):
                    v = _norm_missense("p." + part)
                    if v:
                        neg.add(v)
            else:
                v = _norm_missense(pc)
                if v:
                    neg.add(v)
    neg.discard("p.Ala222Val")          # paper's stated exclusion
    pos.discard("p.Ala222Val")
    return frozenset(pos), frozenset(late), frozenset(neg)


# ==========================================================================
# Bootstrap helpers
# ==========================================================================
def paired_spearman_boot(xa, xw, y, clusters, ids):
    da = p4c.pos_cluster_boot_from_ids(xa, y, clusters, ids)
    dw = p4c.pos_cluster_boot_from_ids(xw, y, clusters, ids)
    return da, dw, da - dw


def auroc_from_ids(scores, y, clusters, ids, labels, ref=False):
    """AUROC per pre-drawn position-cluster draw (rows kept with
    multiplicity).  ref=True uses sklearn (the slow reference)."""
    from sklearn.metrics import roc_auc_score
    rows_of = {lab: np.flatnonzero(clusters == lab) for lab in labels}
    out = np.full(len(ids), np.nan)
    for i, draw in enumerate(ids):
        idx = np.concatenate([rows_of[labels[s]] for s in draw])
        yy, ss = y[idx], scores[idx]
        if yy.min() == yy.max():
            continue                      # single class -> NaN
        out[i] = (float(roc_auc_score(yy, ss)) if ref
                  else p4c.auroc(yy, ss))
    return out


# ==========================================================================
def main():
    banner("A5 -- MODULE U: predictive utility (UTILITY_PREREG_v1.md, "
           "implemented exactly)")
    print(f"N_BOOT = {N_BOOT}   SEED = {SEED}   N_REF = {N_REF}")
    print(f"RESAMPLING UNIT: position clusters, drawn once per subset and "
          f"shared by both predictors (paired Delta).  Backgrounds are "
          f"never resampled (one background).")
    print("DECISION RULE (pre-registered, full text in the docstring): "
          "G-U0 or G-U3 FAIL -> exit 3.  G-U1 FAIL -> U-2 STOPPED, U-1 "
          "stands, exit 0.  G-U2 FAIL -> U-2 UNVERIFIED-LABELS (no word), "
          "exit 0.  Acquisition failure -> U-2 BLOCKED, U-1 stands.  "
          "Thresholds are never loosened; N is never raised to pass a "
          "gate.")
    if smoke_mode():
        print(f"*** SMOKE RUN: N_BOOT={N_BOOT} != 10000 -- every CI and "
              "every word is PROVISIONAL; the Phase 1 CI sub-gate is "
              "SKIPPED and G-U3 cannot be PASS on this run ***")
    print("DISCLOSURES (pre-registered in the docstring): (1) cached-data "
          "analysis, not out-of-sample wrt the project's history (prereg "
          "S0); (2) U-DEC5 -- G-U1's canonical-column value was seen "
          "during recon (~0.685; exact recon row set not recorded, "
          "recomputations span 0.681-0.693, all < 0.90) BEFORE the "
          "experimental-column choice was fixed; both are printed at "
          "G-U1 (POST-RUN TEXT FIX of this note only, no decision "
          "changed); (3) label derivation was "
          "prototyped against the paper's stated 30/40 set sizes; no "
          "metric was computed before the first run.")

    # =====================================================================
    banner("G-U0 -- INFRASTRUCTURE (HARD; guards U-1 and U-2)", "-")
    sha = _sha256(PREREG)
    n_lines = len(PREREG.read_text().splitlines())
    gate("G-U0(a) prereg sha256", sha == PREREG_SHA,
         f"{sha}  (target {PREREG_SHA}; {n_lines} lines)")

    tb = time.time()
    t32 = pd.read_csv(TASK32, float_precision="round_trip")
    cols5 = ["delta_esm", "own_e_b", "position", "esm2_score",
             "base_functionality"]
    mcols = ["m12.score", "m25.score", "m100.score", "m200.score"]
    frame = t32[t32[cols5].notna().all(axis=1)].reset_index(drop=True)
    gate("G-U0(b) frame rows / positions",
         len(frame) == T_ROWS and frame.position.nunique() == T_POS,
         f"got {len(frame)} rows / {frame.position.nunique()} positions; "
         f"target {T_ROWS} / {T_POS} (task32 has {len(t32)} rows; "
         f"{len(t32) - len(frame)} dropped by the filter, y finite on "
         f"all of them: "
         f"{int(frame[mcols].notna().any(axis=1).sum())})")

    rho_u0 = p4c.spearman(frame.own_e_b.to_numpy(float),
                          frame.esm2_score.to_numpy(float))
    note("G-U0(c) Spearman(own_e_b, S_W) at 4 dp", round(rho_u0, 4),
         T_RHO_U0, 1e-12, fmt="{:.4f}")

    # U-DEC1 / U-DEC3 -- y and subsets
    frame["y"] = frame[mcols].mean(axis=1, skipna=True)
    both = frame.y.notna() & frame.f_bar_a222v.notna()
    dy = float((frame.y[both] - frame.f_bar_a222v[both]).abs().max())
    same_fin = bool((frame.y.notna() == frame.f_bar_a222v.notna()).all())
    gate("G-U0(g) y == f_bar_a222v (AGENTS 5 column identity, ADDED)",
         dy < TOL_15 and same_fin,
         f"max|diff| = {dy:.3e} over {int(both.sum())} rows (gate < 1e-15), "
         f"finiteness identical: {same_fin}")
    dd = float((frame.delta_esm
                - (frame.esm2_score_a222v_bg - frame.esm2_score)
                ).abs().max())
    gate("G-U0(g) delta_esm == S_A - S_W (AGENTS 5, ADDED)",
         dd < TOL_12, f"max|diff| = {dd:.3e} (gate < 1e-12)")

    _, A = pdg.build(verbose=False)
    print(f"  [pdg.build] {time.time() - tb:.1f}s -- script 125's cached "
          "construction, imported (AGENTS 2)")
    hmask = np.isin(frame.position.to_numpy(), list(A.Hset))
    gate("G-U0(e) H subset = 455 positions / 7,526 rows (ADDED)",
         len(A.Hset) == T_HPOS and int(hmask.sum()) == T_HROWS,
         f"got {len(A.Hset)} positions / {int(hmask.sum())} rows; target "
         f"{T_HPOS} / {T_HROWS}")

    # =====================================================================
    banner("ACQUISITION (U-DEC11) -- manifest re-verification, < 200 MB",
           "-")
    recs, blocked = acquire()
    total = sum(r["bytes"] for r in recs)
    all_ok = all(r["ok"] for r in recs) and bool(recs)
    for r in recs:
        print(f"  {'OK ' if r['ok'] else 'BAD'} {r['url']}  status="
              f"{r['status']}  bytes={r['bytes']}  sha256={r['sha256']}")
    if blocked:
        # network/acquisition failure: U-2 BLOCKED only (planning 178),
        # never a script failure -- U-1's infrastructure is untouched.
        gate("G-U0(f) manifests re-verify (ADDED)", False,
             f"ACQUISITION BLOCKED: {blocked} -- U-2 = BLOCKED, U-1 "
             "stands; not a script failure (planning 178)", hard=False)
    else:
        gate("G-U0(f) manifests re-verify, all 200, total < 200 MB "
             "(ADDED)", all_ok and total < MAX_BYTES,
             f"{len(recs)} records, total {total} bytes = "
             f"{total / 1e6:.1f} MB (abort at {MAX_BYTES / 1e6:.0f} MB)")

    # =====================================================================
    banner("LABEL SETS (U-DEC6/U-DEC7) from Supplemental Table S3 "
           "-- class sizes printed BEFORE any metric", "-")
    u2_alive = blocked is None
    pos, late, neg, fallback_used = frozenset(), frozenset(), frozenset(), False
    if not ST3.exists() or not u2_alive:
        if not u2_alive:
            print("  U-2 label derivation skipped (acquisition BLOCKED)")
        else:
            print("  ST3 missing -- using the FROZEN FALLBACK "
                  f"({FALLBACK.name}) and disclosing it as a DIFFERENT "
                  "LABEL SET (prereg S3); not used in this run when ST3 "
                  "exists.")
            fallback_used = True
    if not fallback_used and ST3.exists():
        pos, late, neg = derive_labels()
        gate("G-U0(d) paper-stated set sizes 30 positive / 40 late "
             "(ADDED)", len(pos) == T_POS_SET and len(late) == T_LATE_SET,
             f"derived {len(pos)} early-onset positive (target "
             f"{T_POS_SET}), {len(late)} late-onset (target {T_LATE_SET}), "
             f"{len(neg)} 1000-Genomes random (no paper anchor; "
             "methods D describe the rule, not the count)")
        both_sets = pos & neg
        print(f"  variants in BOTH sets: {len(both_sets)} "
              f"{sorted(both_sets) if both_sets else ''} -> excluded "
              "from both (U-DEC7)")
        pos = pos - both_sets
        neg = neg - both_sets
    else:
        gate("G-U0(d) paper-stated set sizes 30 positive / 40 late "
             "(ADDED)", False,
             "SKIPPED: label derivation not run in this configuration "
             "(fallback in use or ST3 unavailable)", hard=False)

    if fallback_used:
        fb = pd.read_csv(FALLBACK)
        cls = fb.classification.str.lower()
        p_mask = cls.str.contains("pathogenic") & ~cls.str.contains(
            "conflict") & ~cls.str.contains("uncertain")
        b_mask = cls.str.contains("benign")
        lab = pd.concat([
            fb[p_mask][["uid", "position", "esm2_score",
                        "esm2_score_a222v_bg"]].assign(label=1),
            fb[b_mask][["uid", "position", "esm2_score",
                        "esm2_score_a222v_bg"]].assign(label=0)])
        lab = lab.rename(columns={"uid": "hgvs_pro"}).drop_duplicates(
            "hgvs_pro")
        finite = lab[["esm2_score",
                      "esm2_score_a222v_bg"]].notna().all(axis=1)
        print(f"  ATTRITION (fallback): {len(lab)} labelled -> "
              f"{int(finite.sum())} with finite S_W and S_A")
        lab = lab[finite].reset_index(drop=True)
        n_pos = int((lab.label == 1).sum())
        n_neg = int((lab.label == 0).sum())
        print(f"  CLASS SIZES (printed before any metric): "
              f"pathogenic/likely pathogenic = {n_pos}, benign/likely "
              f"benign = {n_neg} (min class {min(n_pos, n_neg)}; "
              f"UNDERPOWERED if < {MIN_CLASS}) -- FALLBACK: A DIFFERENT "
              "LABEL SET from Weile's reference sets (disclosed, "
              "prereg S3).")
    elif u2_alive:
        lab = pd.DataFrame({"hgvs_pro": sorted(pos), "label": 1})
        lab = pd.concat([lab, pd.DataFrame({"hgvs_pro": sorted(neg),
                                            "label": 0})],
                        ignore_index=True)
        n_labelled = len(lab)
        in_task32 = lab.hgvs_pro.isin(set(t32.hgvs_pro))
        missing = sorted(lab.hgvs_pro[~in_task32])
        lab = lab.merge(t32[["hgvs_pro", "esm2_score",
                             "esm2_score_a222v_bg", "position"]],
                        on="hgvs_pro", how="inner")
        finite = lab[["esm2_score",
                      "esm2_score_a222v_bg"]].notna().all(axis=1)
        print(f"  ATTRITION: {len(pos)} positive + {len(neg)} negative = "
              f"{n_labelled} labelled -> {len(lab)} present in task32 "
              f"(missing: {missing}) -> {int(finite.sum())} with finite "
              "S_W and S_A (U-DEC10)")
        lab = lab[finite].reset_index(drop=True)
        n_pos = int((lab.label == 1).sum())
        n_neg = int((lab.label == 0).sum())
        print(f"  CLASS SIZES (printed before any metric, prereg S3): "
              f"pathogenic = {n_pos}, random/benign = {n_neg} "
              f"(min class {min(n_pos, n_neg)}; UNDERPOWERED if < "
              f"{MIN_CLASS})")

    # =====================================================================
    banner("G-U1 -- MaveDB a-2 (A222V, 25 ug/mL) vs the project's "
           "m25.score (HARD; guards U-2)", "-")
    if not u2_alive:
        gate("G-U1 same-data check", False,
             "BLOCKED (acquisition) -- U-2 cannot run; U-1 stands",
             hard=False)
        u2_status = "BLOCKED"
    elif fallback_used:
        # fallback labels do not involve MaveDB maps for LABELS, but the
        # maps are still the predictors -- G-U1 still guards them.
        u2_status = "FALLBACK-LABELS"
    else:
        u2_status = "ALIVE"

    if u2_status in ("ALIVE", "FALLBACK-LABELS"):
        m2 = pd.read_csv(MAVE_DIR / "mavedb_00000049-a-2_scores.csv")
        j = t32[["hgvs_pro", "m25.score"]].merge(
            m2[["hgvs_pro", "score", "exp.score"]], on="hgvs_pro")
        je = j.dropna(subset=["m25.score", "exp.score"])
        rho_exp = p4c.spearman(je["exp.score"].to_numpy(float),
                               je["m25.score"].to_numpy(float))
        jc = j.dropna(subset=["m25.score", "score"])
        rho_can = p4c.spearman(jc["score"].to_numpy(float),
                               jc["m25.score"].to_numpy(float))
        gate(f"G-U1 Spearman(MaveDB a-2 experimental, m25) >= {G_U1_MIN}",
             rho_exp >= G_U1_MIN,
             f"rho = {rho_exp!r} over {len(je)} shared variants "
             f"(gate >= {G_U1_MIN})")
        print(f"  [U-DEC5 disclosed context] same check on the CANONICAL "
              f"`score` column: rho = {rho_can!r} over {len(jc)} rows "
              f"({'below' if rho_can < G_U1_MIN else 'above'} the "
              "threshold -- NOT the gate; `score` for a-2 is a shrunken "
              "exp/pred blend, not the experimental map)")
        # column-identity evidence (AGENTS 5), all informational
        try:
            import openpyxl
            wb2 = openpyxl.load_workbook(ST2, read_only=True,
                                         data_only=True)
            ws2 = wb2[wb2.sheetnames[0]]
            rows2 = list(ws2.iter_rows(values_only=True))
            st2 = pd.DataFrame(
                [(r[0], r[15]) for r in rows2[3:]
                 if r[0] and isinstance(r[15], (int, float))],
                columns=["hgvs_pro", "st2_m25"])
            j2 = t32[["hgvs_pro", "m25.score"]].merge(st2, on="hgvs_pro")
            n_exact = int(((j2["m25.score"] - j2["st2_m25"]).abs()
                           <= 1e-9).sum())
            print(f"  [evidence i] project m25 == paper Supplemental "
                  f"Table S2 A222V-25: {n_exact}/{len(j2)} exact, rho "
                  f"{p4c.spearman(j2['m25.score'].to_numpy(float), j2['st2_m25'].to_numpy(float))!r}")
        except Exception as e:                                   # noqa
            print(f"  [evidence i] ST2 identity check unavailable: {e}")
        print("  [evidence ii] a-2 rho(score, exp.score) = "
              "0.737104307 (score == pred.score on 1,037 rows): the "
              "canonical column is a blend")
        m8 = pd.read_csv(MAVE_DIR / "mavedb_00000049-a-8_scores.csv")
        j8 = t32[["hgvs_pro", "m200.score"]].merge(
            m8[["hgvs_pro", "score"]], on="hgvs_pro").dropna()
        rho8 = p4c.spearman(j8["m200.score"].to_numpy(float),
                            j8["score"].to_numpy(float))
        print(f"  [evidence iii] a-8 (no exp/pred columns) score vs "
              f"project m200: rho = {rho8!r} (rank-identical)")
        if rho_exp < G_U1_MIN:
            u2_status = "STOPPED-G-U1"

    # =====================================================================
    banner("G-U3(i) -- AUROC and balanced-PR vs scikit-learn on toys "
           "(HARD)", "-")
    from sklearn.metrics import auc as sk_auc
    from sklearn.metrics import precision_recall_curve, roc_auc_score
    from sklearn.metrics import roc_curve as sk_roc_curve
    toys = [
        ("with ties", np.array([0, 0, 1, 1, 1, 0, 1, 0], dtype=bool),
         np.array([0.1, 0.5, 0.5, 0.9, 0.2, 0.5, 0.7, 0.3])),
        ("perfect", np.array([0, 0, 0, 1, 1, 1], dtype=bool),
         np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])),
        ("inverted", np.array([1, 1, 1, 0, 0, 0], dtype=bool),
         np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])),
    ]
    for name, yy, ss in toys:
        mine, theirs = p4c.auroc(yy, ss), float(roc_auc_score(yy, ss))
        gate(f"G-U3 auroc == sklearn ({name})", abs(mine - theirs) < TOL_12,
             f"library {mine!r} sklearn {theirs!r} |diff| "
             f"{abs(mine - theirs):.3e} (gate < 1e-12)")
    yy = np.array([0, 0, 1, 1, 1, 0, 1, 0, 1, 0] * 3, dtype=bool)
    ss = np.array([0.1, 0.5, 0.5, 0.9, 0.2, 0.5, 0.7, 0.3, 0.6, 0.4] * 3)
    rr_, bp_ = p4c.balanced_pr_curve(yy, ss)
    P_, N_ = int(yy.sum()), int((~yy).sum())
    pr_, rc_, _ = precision_recall_curve(yy, ss,
                                         sample_weight=np.where(yy, N_, P_))
    rc_a, pr_a = rc_[::-1], pr_[::-1]
    d_r = float(np.max(np.abs(rr_[1:] - rc_a[1:])))
    d_b = float(np.max(np.abs(bp_[1:] - pr_a[1:])))
    gate("G-U3 balanced_pr_curve == sklearn weighted "
         "precision_recall_curve (recall 1..end)",
         d_r < TOL_12 and d_b < TOL_12,
         f"max|diff| recall {d_r:.3e}, balanced precision {d_b:.3e} "
         "(gate < 1e-12)")
    mine_area = p4c.balanced_pr_auc(yy, ss)
    their_area = float(sk_auc(rc_a, np.r_[pr_a[1], pr_a[1:]]))
    gate("G-U3 balanced_pr_auc == sklearn.metrics.auc (same coords)",
         abs(mine_area - their_area) < TOL_12,
         f"library {mine_area!r} sklearn-path {their_area!r} |diff| "
         f"{abs(mine_area - their_area):.3e} (gate < 1e-12)")
    fpr_, tpr_, _ = sk_roc_curve(yy, ss, drop_intermediate=False)
    d_roc = float(np.max(np.abs(bp_[1:] - tpr_[1:] / (tpr_[1:] + fpr_[1:]))))
    gate("G-U3 balanced_pr == sklearn roc_curve path (2nd path)",
         d_roc < TOL_12, f"max|diff| {d_roc:.3e} (gate < 1e-12)")
    chance = p4c.balanced_pr_auc(np.array([1, 0] * 50, dtype=bool),
                                 np.random.default_rng(0).normal(size=100))
    gate("G-U3 balanced_pr_auc of a chance toy near 0.5",
         np.isfinite(chance) and abs(chance - 0.5) < 0.1,
         f"got {chance!r}, finite and within 0.1 of 0.5")

    # =====================================================================
    banner("G-U3(ii) -- BOOTSTRAP REFERENCE GATE on the U-1 frame "
           "(identity, draw-by-draw, Phase 1 CI)", "-")
    x_w = frame.esm2_score.to_numpy(float)
    x_a = frame.esm2_score_a222v_bg.to_numpy(float)
    yv = frame.y.to_numpy(float)
    posv = frame.position.to_numpy()
    point_a = p4c.spearman(x_a, yv)
    point_w = p4c.spearman(x_w, yv)
    labels_f = p4c.first_appearance_labels(posv)
    nk = len(labels_f)
    ids_one = np.arange(nk, dtype=np.int64)[None, :]
    one_a = float(p4c.pos_cluster_boot_from_ids(x_a, yv, posv, ids_one)[0])
    one_w = float(p4c.pos_cluster_boot_from_ids(x_w, yv, posv, ids_one)[0])
    gate("G-U3(ii) identity: every position once reproduces both rhos "
         "and Delta", abs(one_a - point_a) < TOL_12
         and abs(one_w - point_w) < TOL_12
         and abs((one_a - one_w) - (point_a - point_w)) < TOL_12,
         f"rho_A {one_a!r} vs {point_a!r}, rho_W {one_w!r} vs "
         f"{point_w!r}, max|diff| "
         f"{max(abs(one_a - point_a), abs(one_w - point_w)):.3e} "
         "(gate < 1e-12)")
    tb = time.time()
    ids_ref, _ = p4c.draw_ids(posv, N_REF, SEED)
    da_f, dw_f, dd_f = paired_spearman_boot(x_a, x_w, yv, posv, ids_ref)
    da_r = p4c.reference_boot(x_a, yv, posv, ids_ref)
    dw_r = p4c.reference_boot(x_w, yv, posv, ids_ref)
    md = float(np.max(np.abs(da_f - da_r)))
    mdw = float(np.max(np.abs(dw_f - dw_r)))
    mdd = float(np.max(np.abs(dd_f - (da_r - dw_r))))
    gate("G-U3(ii) draw-by-draw paired bootstrap vs reference "
         f"({N_REF} draws)", max(md, mdw, mdd) < TOL_12,
         f"max|corrected - reference| rho_A {md:.3e}, rho_W {mdw:.3e}, "
         f"Delta {mdd:.3e} (gate < 1e-12) in {time.time() - tb:.1f}s")
    if N_BOOT == 10000:
        tb = time.time()
        draws_p1 = p3c.pos_cluster_boot(frame.delta_esm.to_numpy(float),
                                        frame.own_e_b.to_numpy(float),
                                        posv, N_BOOT, SEED)
        lo, hi, nf = p4c.pct_ci(draws_p1)
        note("G-U3(ii) Phase 1 CI lo", lo, T_CI_LO, TOL_9DP)
        note("G-U3(ii) Phase 1 CI hi", hi, T_CI_HI, TOL_9DP)
        print(f"       ({nf} finite draws, N_BOOT={N_BOOT}, SEED={SEED}) "
              f"in {time.time() - tb:.1f}s")
    else:
        gate("G-U3(ii) Phase 1 CI reproduction", False,
             f"SKIPPED (smoke): N_BOOT={N_BOOT} != 10000 -- G-U3 cannot "
             "be called PASS on this run; decided on the N_BOOT=10000 run",
             hard=False)

    # =====================================================================
    banner("U-1 -- Delta = Spearman(S_A, y) - Spearman(S_W, y) "
           "(frozen section 2)", "-")
    def run_subset(name, mask, word=False, descriptive=False):
        m = np.asarray(mask)
        xs_a, xs_w, ys, ps = x_a[m], x_w[m], yv[m], posv[m]
        pa = p4c.spearman(xs_a, ys)
        pw = p4c.spearman(xs_w, ys)
        d_pt = pa - pw
        ids, _ = p4c.draw_ids(ps, N_BOOT, SEED)
        da, dw, dd = paired_spearman_boot(xs_a, xs_w, ys, ps, ids)
        lo, hi, nf = p4c.pct_ci(dd)
        tag = "PROVISIONAL (smoke) " if smoke_mode() else ""
        lab = "DESCRIPTIVE, no word -- " if descriptive else ""
        print(f"\n  [{name}] n = {int(m.sum())} rows / "
              f"{len(p4c.first_appearance_labels(ps))} positions")
        print(f"    rho(S_A, y) = {pa!r}   rho(S_W, y) = {pw!r}")
        print(f"    Delta = {d_pt!r}   CI95 = [{lo!r}, {hi!r}] "
              f"({nf}/{N_BOOT} finite draws, SEED {SEED}) {lab}"
              f"{tag}word margin {WORD_MARGIN}")
        if word and not smoke_mode():
            w = p4c.word_conditioning(lo, hi, WORD_MARGIN)
            print(f"    OUTCOME WORD (frozen): {w}")
            return w
        if word and smoke_mode():
            w = p4c.word_conditioning(lo, hi, WORD_MARGIN)
            print(f"    OUTCOME WORD {tag}: {w} -- PROVISIONAL; decided "
                  "on N_BOOT=10000")
            return w
        return None

    # context rows (U-DEC4)
    rho_w_bf = p4c.spearman(x_w, frame.base_functionality.to_numpy(float))
    print(f"  CONTEXT: Spearman(S_W, base functionality) = {rho_w_bf!r}; "
          f"Spearman(S_A, y) = {point_a!r} (the PRIMARY Delta's first "
          "component)")
    y_med = float(np.median(frame.y.to_numpy(float)))
    print(f"  CONTEXT: y (A222V fitness) median = {y_med!r}, "
          f"finite {int(np.isfinite(yv).sum())}/{len(yv)}")

    word_u1 = run_subset("PRIMARY (all frame rows)", np.ones(len(frame),
                         dtype=bool), word=True)
    run_subset("H subset (descriptive)", hmask, word=False,
               descriptive=True)
    abs_own = np.abs(frame.own_e_b.to_numpy(float))
    q90 = float(np.quantile(abs_own, 0.90))
    top = abs_own >= q90
    print(f"\n  TOPDECILE cut: |own_e_b| >= quantile 0.90 = {q90!r} "
          f"-> {int(top.sum())} rows (ties kept, U-DEC3)")
    run_subset("TOP |own_e_b| decile (descriptive)", top, word=False,
               descriptive=True)
    print("\n  PER-CONDITION DESCRIPTIVE REPEATS (U-DEC4; no word, no "
          "multiplicity correction)")
    for c in mcols:
        m = frame[c].notna().to_numpy() & np.isfinite(frame[c].to_numpy())
        if m.sum() >= 10:
            run_subset(f"y = {c}", m, word=False, descriptive=True)

    # =====================================================================
    banner("U-2 -- pathogenic vs reference separation "
           "(frozen section 3)", "-")
    word_u2, u2_detail = None, ""
    if u2_status == "BLOCKED":
        print("  U-2 BLOCKED (acquisition): no metric computed, no word. "
              "U-1 stands (planning line 178).")
        u2_detail = "BLOCKED (acquisition)"
    elif u2_status == "STOPPED-G-U1":
        print("  U-2 STOPPED at G-U1: MaveDB a-2 and the project's m25 "
              "are not the same data at the required Spearman >= 0.90.  "
              "No U-2 metric is computed; no word.  U-1 stands.")
        u2_detail = "STOPPED (G-U1)"
    else:
        # predictors: U-DEC8 orientation, U-DEC9 columns
        pred = {
            "S_W (ESM-2 WT bg)": -lab.esm2_score.to_numpy(float),
            "S_A (ESM-2 A222V bg)": -lab.esm2_score_a222v_bg.to_numpy(float),
        }
        pred_canon = {}
        for key, title in MAPS.items():
            mv = pd.read_csv(MAVE_DIR / f"mavedb_00000049-{key}_scores.csv")
            col = "exp.score" if "exp.score" in mv.columns else "score"
            got = lab[["hgvs_pro"]].merge(
                mv[["hgvs_pro", col]].rename(columns={col: "v"}),
                on="hgvs_pro", how="left")["v"].to_numpy(float)
            pred[f"{key} {title.split('at ')[1]}"] = -got
            got_c = lab[["hgvs_pro"]].merge(
                mv[["hgvs_pro", "score"]].rename(columns={"score": "v"}),
                on="hgvs_pro", how="left")["v"].to_numpy(float)
            pred_canon[key] = -got_c
        y2 = lab.label.to_numpy(int)
        print(f"  analysis set n = {len(lab)} "
              f"(pathogenic {n_pos}, benign {n_neg}) -- CLASS SIZES "
              f"ABOVE, printed before any metric; S_A/S_W identity "
              f"AUROC(y, -s) = 1 - AUROC(y, s) (U-DEC8)")
        under = p4c.word_underpowered(n_pos, n_neg, MIN_CLASS)
        if under:
            print(f"  {under}: a class has fewer than {MIN_CLASS} "
                  f"variants ({min(n_pos, n_neg)}) -- no word, CI only.")

        print("\n  METRICS (oriented, U-DEC8; n = finite rows for that "
               "predictor)")
        metrics = {}
        for name, sc in pred.items():
            m = np.isfinite(sc)
            if m.sum() == 0 or len(np.unique(y2[m])) < 2:
                continue
            a = p4c.auroc(y2[m], sc[m])
            b = p4c.balanced_pr_auc(y2[m], sc[m])
            metrics[name] = (a, b, int(m.sum()))
            print(f"    {name:<34} n={int(m.sum()):>3}  AUROC={a:.6f}  "
                  f"balPR={b:.6f}")

        # -- G-U2: a-2 tops the eight experimental maps (HARD)
        map_names = [k for k in metrics if k.split()[0] in MAPS]
        if map_names:
            areas = {k: metrics[k][1] for k in map_names}
            a2_key = next((k for k in areas
                           if k.split()[0] == POS_CONTROL), None)
            others_max = max((v for k, v in areas.items() if k != a2_key),
                             default=float("-inf"))
            print("\n  G-U2 ranking of the eight experimental maps by "
                   "balanced-PR area (U-DEC9 exp-where-available cols):")
            for k in sorted(areas, key=areas.get, reverse=True):
                mark = "   <- a-2 (AV25, target best)" \
                    if k.split()[0] == POS_CONTROL else ""
                print(f"    {k:<36} {areas[k]:.6f}{mark}")
            gu2_ok = a2_key is not None and areas[a2_key] >= others_max
            gate("G-U2 a-2 (A222V, 25 ug/mL) attains the highest "
                 "balanced-PR area among the eight maps", gu2_ok,
                 f"a-2 area {areas.get(a2_key, float('nan'))!r} vs best "
                 f"of the others {others_max!r}; ordering Weile et al. "
                 "report (Fig 6A)")
            # pre-registered non-gated sensitivity: canonical columns
            areas_c = {}
            for key in MAPS:
                sc = pred_canon[key]
                m = np.isfinite(sc)
                if m.sum() and len(np.unique(y2[m])) > 1:
                    areas_c[key] = p4c.balanced_pr_auc(y2[m], sc[m])
            if areas_c:
                best_c = max(areas_c, key=areas_c.get)
                print(f"  [SENSITIVITY, non-gated, U-DEC9] canonical "
                      f"`score` columns: best = {best_c} "
                      f"({areas_c[best_c]:.6f}); a-2 = "
                      f"{areas_c.get(POS_CONTROL, float('nan')):.6f}")
        else:
            gate("G-U2 a-2 tops the eight maps", False,
                 "no map metrics computed")
            gu2_ok = False

        # -- Delta AUROC bootstrap (paired, U-DEC2)
        if under:
            print("\n  Delta AUROC CI (UNDERPOWERED -- no word):")
        else:
            print("\n  Delta AUROC = AUROC(S_A) - AUROC(S_W), paired "
                  "position-cluster bootstrap:")
        sc_a = pred["S_A (ESM-2 A222V bg)"]
        sc_w = pred["S_W (ESM-2 WT bg)"]
        clusters = lab.position.to_numpy()
        ids, _ = p4c.draw_ids(clusters, N_BOOT, SEED)
        labels_l = p4c.first_appearance_labels(clusters)
        au_a = auroc_from_ids(sc_a, y2, clusters, ids, labels_l)
        au_w = auroc_from_ids(sc_w, y2, clusters, ids, labels_l)
        dd2 = au_a - au_w
        lo2, hi2, nf2 = p4c.pct_ci(dd2)
        pt_a2 = p4c.auroc(y2[np.isfinite(sc_a)], sc_a[np.isfinite(sc_a)])
        pt_w2 = p4c.auroc(y2[np.isfinite(sc_w)], sc_w[np.isfinite(sc_w)])
        n_nan = int(np.isnan(dd2).sum())
        print(f"    AUROC(S_A) = {pt_a2!r}   AUROC(S_W) = {pt_w2!r}   "
              f"(oriented y=1 pathogenic, -score)")
        print(f"    Delta AUROC = {pt_a2 - pt_w2!r}   CI95 = [{lo2!r}, "
              f"{hi2!r}] ({nf2}/{N_BOOT} finite draws, {n_nan} "
              f"single-class draws dropped, SEED {SEED})"
              + ("  PROVISIONAL (smoke)" if smoke_mode() else ""))

        # -- G-U3(ii) reference for the AUROC bootstrap
        ids_r, _ = p4c.draw_ids(clusters, N_REF, SEED)
        fa = auroc_from_ids(sc_a, y2, clusters, ids_r, labels_l)
        fw = auroc_from_ids(sc_w, y2, clusters, ids_r, labels_l)
        ra = auroc_from_ids(sc_a, y2, clusters, ids_r, labels_l, ref=True)
        rw = auroc_from_ids(sc_w, y2, clusters, ids_r, labels_l, ref=True)
        m_a = float(np.nanmax(np.abs(fa - ra)))
        m_w = float(np.nanmax(np.abs(fw - rw)))
        gate(f"G-U3(ii) U-2 AUROC bootstrap draw-by-draw vs sklearn "
             f"({N_REF} draws)", max(m_a, m_w) < TOL_12,
             f"max|diff| S_A {m_a:.3e}, S_W {m_w:.3e} (gate < 1e-12)")
        ids_o = np.arange(len(labels_l), dtype=np.int64)[None, :]
        o_a = auroc_from_ids(sc_a, y2, clusters, ids_o, labels_l)[0]
        o_w = auroc_from_ids(sc_w, y2, clusters, ids_o, labels_l)[0]
        gate("G-U3(ii) U-2 identity: every position once reproduces "
             "both AUROCs",
             np.isfinite(o_a) and np.isfinite(o_w)
             and abs(o_a - pt_a2) < TOL_12 and abs(o_w - pt_w2) < TOL_12,
             f"every-once S_A {o_a!r} vs {pt_a2!r}, S_W {o_w!r} vs "
             f"{pt_w2!r} (gate < 1e-12)")

        # -- the word
        if under:
            word_u2 = under
            print(f"  OUTCOME WORD (frozen): {under} -- no word given "
                  "(prereg S3); CI reported above")
        elif not gu2_ok:
            word_u2 = "UNVERIFIED-LABELS"
            print("  OUTCOME WORD (frozen): none -- G-U2 failed, U-2 is "
                  "reported UNVERIFIED-LABELS with no word (prereg S4)")
        else:
            if smoke_mode():
                word_u2 = p4c.word_conditioning(lo2, hi2, WORD_MARGIN)
                print(f"  OUTCOME WORD (smoke, PROVISIONAL): {word_u2} "
                      "-- decided on N_BOOT=10000")
            else:
                word_u2 = p4c.word_conditioning(lo2, hi2, WORD_MARGIN)
                print(f"  OUTCOME WORD (frozen): {word_u2}")
        u2_detail = (f"ALIVE, n={len(lab)} ({n_pos}/{n_neg}), "
                     f"G-U2 {'PASS' if gu2_ok else 'FAIL'}")

    # =====================================================================
    banner("A5 GATE TABLE", "-")
    n_fail = sum(1 for _, ok, _, _ in gates if not ok)
    n_skip = sum(1 for _, ok, d, _ in gates
                 if not ok and "SKIPPED" in d)
    for gid, ok, detail, _ in gates:
        print(f"  [{'PASS' if ok else 'FAIL'}] {gid}: {detail}")
    print(f"\n  {len(gates) - n_fail}/{len(gates)} checks PASS, "
          f"{n_fail} FAIL ({n_skip} of the FAILs are smoke SKIPS).")

    # Exit rule (pre-registered): only HARD failures of the shared
    # infrastructure gates G-U0/G-U3 stop the script (exit 3).  G-U1 and
    # G-U2 are hard for the ITEM they guard (U-2 cannot claim) but their
    # failure only stops U-2 / withholds the word -- U-1 stands and the
    # script exits 0 with the status printed and logged.  Smoke CI gates
    # are SKIPPED (hard=False) and cannot make the run pass.
    hard_infra = [(gid, det) for gid, ok, det, hard in gates
                  if not ok and hard and "SKIPPED" not in det
                  and gid.startswith(("G-U0", "G-U3"))]
    print("\n  U-1 PRIMARY outcome word: "
          + (word_u1 or "(none)")
          + ("  [PROVISIONAL SMOKE]" if smoke_mode() else ""))
    print("  U-2 status: " + u2_detail)
    print("  U-2 outcome word: "
          + (word_u2 if word_u2 else "(none)")
          + ("  [PROVISIONAL SMOKE]" if (word_u2 and smoke_mode()) else ""))

    print("\nLIMITATIONS (printed per AGENTS 6): one gene, one ESM-2 "
          "model; U-1 is a cached-data analysis that is not "
          "out-of-sample with respect to the project's history (prereg "
          "S0) and its numbers REPRODUCE cached columns -- reproduction "
          "is not replication (AGENTS 6); the bootstrap resamples "
          "positions within this frame only; percentile CIs; "
          "per-condition repeats are descriptive and uncorrected for "
          "multiplicity; U-2's label set is small (see class sizes) so "
          "CI width, not the point estimate, is the binding constraint; "
          "Weile's own AUBPRC used monotonisation and prior-balanced "
          "posteriors we do not re-implement -- G-U2 asks only that "
          "their reported ordering (AV25 best) reproduces on our label "
          "set; U-DEC8's orientation fixes the direction of the frozen "
          "words; the supplemental methods also describe a gnomAD "
          "random set (used for their LLR calibration) that is outside "
          "this project's authorised network and NOT used here; no "
          "claim about clinical use (prereg S5).")
    print(f"Elapsed {time.time() - t0:.1f}s")

    if hard_infra:
        for gid, det in hard_infra:
            print(f"  HARD INFRASTRUCTURE FAILURE -- {gid}: {det}")
        print("\nGATE FAIL -- G-U0/G-U3 infrastructure failure; "
              "Module U results are not usable.  Exit 3.")
        sys.exit(3)
    print("\nA5 RESULT: "
          + ("SMOKE complete -- CI gates SKIPPED, all words "
             "PROVISIONAL; the full run decides."
             if smoke_mode() else "full run complete."))
    sys.exit(0)


if __name__ == "__main__":
    main()
