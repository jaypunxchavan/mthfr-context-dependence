"""Script 172 (Phase 4 session 4a, Task A7e) -- Module N neighbour-arm
analysis: frozen sections 5 and 6, plus gates G-N3/G-N4/G-N5.

PRE-REGISTERED: this docstring was written before the first run of this
script, when NO Module N background had been scored for real (only the
A7d timing smoke in scratch existed, which this script never reads).
Binding texts: NEIGHBOUR_ARM_PREREG_v1.md (sha256
167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e) +
NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md (sha256
f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a) +
NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md (sha256
b636a4d193efa16ed36e7d7feeb5a357c99cd5f202437bf100a55b80f822b55a;
Amendment 2 SUPERSEDES only the plant criteria of G-N4 -- see N-AN14).
NO TORCH, no model, no scoring anywhere in this script (asserted before
exit).

DECISIONS, pre-registered here before the first run (printed at startup):

N-AN1  Inputs are sha-pinned: roster_v1.csv (675a24f1...f2d85d6),
       eligible_cells_v1.csv (db86399b...08ba22), D1 background_rho_table
       (e397a442...863796), stored 3d distance (69914df9...31312de), both
       pre-registration files.  Any mismatch -> exit 3.
N-AN2  Existing nulls' H-frame rho_b are READ from the D1 table (all 96,
       including frozen section 5's six) and checked against an
       independent recomputation from the cached phase2 bg_*.csv rows:
       merge the file's rows onto the H frame rows by (position,
       mut_aa), delta = score - cached WT esm2_score, rho =
       Spearman(delta, own_e_b), own position excluded.  Gate: max |D1 -
       recomputed| < 1e-8 over all 96 (D1 was written at 9 decimals).
       This validates the identical function that computes the NEW
       backgrounds' rho_b.
N-AN3  A222V's H rho comes from the canonical builder
       (phase2_diag.rho_table, the same construction script 131 gated at
       1e-9) and is gated against the frozen -0.090021683 (|diff| <
       1e-9); it is ALSO recomputed independently from
       esm2_a222v_bg_scores.csv and gated against the canonical value.
       The same-site rank (frozen section 5: "A222V among the 18 Arm S,
       2/19") is computed from D1's 18 arm-S rho_H plus A222V and gated
       at exactly rank 2 of 19, by both the signed and absolute
       rankings (all 19 values are negative, so they agree).
N-AN4  New-background rho_b uses the N-AN2 function on
       data/processed/phase4/neigh/bg_<id>.csv (their delta column, built
       by script 171 against the same WT cache).  Scratch files from A7d
       (neigh_scratch/) are NEVER read.
N-AN5  G-N3 coverage: for each of the 50 new backgrounds, scored
       positions / |H - {own}| >= 0.95.  A missing file = PENDING (the
       night has not run); a present file below 95% = FAIL -> exit 3
       (script 171 only publishes complete files, so a present-but-short
       file means something broke).
N-AN6  Section 5 runs iff the COMPLETE NB (amendment item 5) has >= 30
       members; otherwise the script logs SKIPPED and computes nothing.
       The NB set for the statistics = complete members of the 46 (40
       new C1/C2/C5 + the six existing d3<=12 nulls); the word comes
       from p4c.word_neighbour with n = that complete count.  The
       sensitivity (amendment item 4) recomputes p_NB after collapsing
       NB to one value per position (mean rho_b at that position) and is
       reported BESIDE the primary with NO word.
N-AN7  Section 6 runs iff ALL 50 new backgrounds are complete (Pool P =
       50 new + 67 resolved existing = 117; an incomplete pool changes
       the estimand, so no partial-pool numbers are ever printed).
       Cell membership is the frozen section 2 definitions + amendment
       item 3's C5, applied to every P member's (d3, dseq); the frozen
       statistics are the C1, C2, C3, C4 means and the C2-C4 / C3-C4
       contrasts; a C5 mean is printed as a DISCLOSED EXTRA (frozen
       section 6 does not list it and no word depends on it).
N-AN8  Bootstrap design (frozen: "background-level ... 10,000, SEED 0"):
       PARTIALS use ONE joint Pool-P ids matrix drawn as
       default_rng(SEED), one rng.integers(0, 117, 117) per draw -- this
       stream is the production stream for every partial CI in the
       script, and gates G-N4/G-N5 always use the first 10,000 draws of
       it in BOTH modes (A6 G-DEC7 precedent).  CELL MEANS use per-cell
       ids streams with seeds SEED + cell ordinal (C1..C5 = 0..4), which
       is exactly p3c.background_boot's construction, cross-checked draw
       by draw against it; CONTRASTS are the difference of the two
       cells' own draws (independent within-cell resampling).  Section
       6's own CIs use N_BOOT draws of the same streams (frozen
       production value 10000 = --mode full; 300 = --mode smoke,
       PROVISIONAL).  CIs are p3c.pct_ci (percentile 2.5/97.5 over
       finite draws).  Pool P order = [50 new in score_order] + [67
       existing by bg_id ascending].
N-AN9  G-N5 (fixed 10,000 draws in BOTH modes): (i) identity -- every
       statistic on ids = arange(n) equals its own point estimate to <
       1e-12; (ii) draw-by-draw -- cell-mean draws equal
       p3c.background_boot's draws to < 1e-12 (same seed), partial draws
       equal a slow closed-form reference built from three
       scipy.stats.spearmanr values per draw to < 1e-12 (both arms, all
       draws, NaN pairs must match), contrast draws equal a plain-Python
       rebuild to < 1e-12; (iii) Phase 1 CI reproduction:
       pos_cluster_boot on the a222v_rows anchor at fixed 10,000 draws
       reproduces [-0.1173334458953319, -0.05951138449511738] to < 1e-9
       per endpoint.  G-N5's (i)/(ii) run on the G-N4 3D-signal plant
       vector (fitness-blind, fixed seed) so the mechanics are exercised
       before any score exists, and the identity check runs AGAIN on the
       real rho vector when Pool P is complete (both print; identical
       code).
N-AN10 G-N4 (fixed 10,000 draws in BOTH modes) on the REAL geometry of
       Pool P: features z-scored over P; signal plants rho = 1.0*z +
       0.4*eps with eps = default_rng(3) shared by both arms (so the
       arms differ only in the feature); noise plant rho = eps alone,
       100 draws from default_rng(1000).  Every plant's CI uses the
       N-AN8 partial stream (seed SEED).  Gates: word(3D plant) =
       3D-LOCAL; word(seq plant) = SEQUENCE-LOCAL; noise fire rate
       (word != NEITHER-RESOLVED) <= 0.15 over the 100 draws.  The two
       signal arms are single fixed draws (A6 G-DEC2 precedent); if one
       fails, that is a genuine gate failure -> exit 3, stop, ask --
       never a re-seek of the seed.
       **SUPERSEDED IN PART by Amendment 2 / N-AN14 below**: the single
       fixed seed 3 (and the seed-1000 noise draw) is replaced by the
       100-seed rate evaluation; the plant construction itself (z-feature
       + 0.4*eps, eps shared between the two single-arm plants, CIs on
       the N-AN8 stream, 10,000 fixed draws) is UNCHANGED, as are the
       seeds' noise scale and every other G-N4 element.
N-AN11 Modes: --mode smoke sets the default N_BOOT to 300, --mode full
       to 10000; the N_BOOT environment variable always wins (session
       convention).  Frozen section 6 pins production CIs at 10,000, so
       only a full-mode run's numbers and words are final; every smoke
       number and word is printed marked PROVISIONAL.  G-N4/G-N5/Phase
       1 draw counts are fixed at 10,000 in both modes, so a smoke gate
       failure is a real failure: stop, never raise N and retry.
N-AN12 The full-frame (secondary, no word) version runs only if every
       NB member also has a complete nonH file in
       data/processed/phase4/neigh_nonH/ (script 171's frame-separated
       output dir); otherwise PENDING.  Existing nulls' full-frame rho
       comes from D1's rho_full column.
N-AN13 No torch: 'torch' in sys.modules is checked before exit (torch is
       never imported here; script 139/125/pdg/131-free imports in this
       chain are all torch-free).
N-AN14 (Amendment 2, Arnav, issued after the seed-3 failure and before
       any real neighbour-arm score exists -- disclosed in the log) G-N4
       is evaluated as RATES over the 100 PRE-LISTED seeds 0..99 (seed 3
       included, never skipped).  For seed s, eps = default_rng(s) is
       shared by the three plants, so the three plants at one seed differ
       only in the feature: 3D-only = z(d3) + 0.4*eps, sequence-only =
       z(dseq) + 0.4*eps, none = eps alone.  The noise scale (0.4), the
       N-AN8 CI stream and the fixed 10,000 draw count are unchanged.
       For each plant the confusion distribution over the four words
       (3D-LOCAL, SEQUENCE-LOCAL, BOTH-LOCAL, NEITHER-RESOLVED) is
       printed, plus the 3x4 matrix (plant x predicted word).  Criteria
       (Arnav's, set without reference to any seed's outcome): correct
       word in >= 80% of seeds for EACH single-arm plant; the wrong-arm
       partial's CI excluding zero in <= 15% of seeds for EACH single-arm
       plant; NEITHER-RESOLVED in >= 85% of seeds for the none plant.
       Any breach -> exit 3.  Item 4: the real section 6 word is ALWAYS
       printed together with this confusion matrix, so a BOTH-LOCAL word
       on real data can be read against the measured false-attribution
       rate when the truth is 3D-only.  Item 5: if either correct-word
       rate is below 80%, section 6 prints NO WORD (every number still
       printed) and section 5 is unaffected.  G-N5's mechanics vector
       stays exactly as first pre-registered (the 3D-only plant at seed
       3, which is one of the 100 pre-listed seeds) so no already-passing
       gate is re-selected.
N-AN15 (Amendment 3, Arnav, issued after the Amendment-2 plant results --
       disclosed in the log) The section 6 partial-correlation statistic is
       the FLEXIBLE-CONTROL partial Spearman and the earlier
       linear-rank-control partial becomes a labelled secondary only.
       Definition, exactly as written in Amendment 3 item 2: for the d3
       partial, regress rank(rho_b) on a natural cubic spline basis of RAW
       dseq by OLS, regress rank(d3) on the SAME basis, and take the
       Pearson correlation of the two residual vectors; the dseq partial
       is the mirror image (spline basis of RAW d3).  Average ranks are
       scipy rankdata("average"), identical to p4c._rank.  The knots are the
       25th/50th/75th percentiles of that RAW distance over the POOL
       (n = 117), computed ONCE from the full pool and held fixed; the
       spline FITS (and the ranks) are recomputed on every bootstrap
       resample, as Amendment 3 requires.  A resample's control values are
       always inside the pool's [min, max], so the fixed boundary knots are
       always valid.  NaN handling mirrors p4c.partial_spearman: NaN if
       n < 3, if the basis is rank-deficient on the draw, or if either
       residual is constant.  Parametrisation DISCLOSURE: in the standard
       natural-cubic-spline family, m interior knots give m+1 basis
       functions (patsy's cr(df=4) uses only TWO interior knots), so
       Amendment 3's "4 degrees of freedom" and its three named interior
       knots cannot both hold under one parametrisation; the three named
       knots are treated as operative (they are the explicit, unambiguous
       part of the text) and the basis is patsy's canonical
       cr(x, knots=[q25,q50,q75]) -- five spline columns, full rank 5,
       condition number printed.  The basis is computed by a fast numpy
       replication of patsy's mgcv_cubic_splines construction, GATED at
       startup against patsy itself (max|diff| < 1e-10) on both pool
       distances and on random probes; patsy is too slow to call inside a
       6-million-draw loop.  G-N4 is re-run on this statistic over the
       same 100 seeds with Amendment 2's criteria unchanged (N-AN14).
       Amendment 3 item 5's fallback is implemented literally: if every
       criterion passes, the flexible statistic produces section 6's
       word with the planted confusion matrix printed beside it; if ANY
       criterion fails, section 6 prints NO WORD with all numbers and the
       matrix, and the linear statistic is printed as a labelled
       secondary.  G-N4's status is reported honestly either way, A7e is
       then complete, and A8/A9 proceed.  Section 5 and every other gate
       are untouched.  Two ADDITIONAL self-checks are pre-registered here
       for the new statistic (they can only make the gate stricter, never
       looser): flex identity (stat(arange) == point, < 1e-12) and flex
       draw-by-draw against a slow QR-based OLS rebuild (< 1e-12, both
       arms, all draws.

GATES (hard for the item they guard; any FAIL -> exit 3):
  input hashes (N-AN1); N-CHK D1 recomputation (N-AN2), A222V anchors
  (N-AN3), roster-cell vs geometry-cell and Pool-P composition; G-N3
  (N-AN5, PENDING until the night's scoring exists); G-N5 (N-AN9); G-N4
  (N-AN10 as superseded by Amendments 2 and 3 -- the rates over seeds
  0..99 on the flexible-control statistic, N-AN14 + N-AN15); the spline
  basis is gated against patsy (N-AN15).

NOTE ON G-N4 AND A7e COMPLETION: Amendment 3 item 5 is pre-committed --
G-N4's PASS/FAIL status is recorded honestly either way, the mechanical
consequence for section 6 is applied (flexible-statistic word, or NO WORD
with the linear statistic as a labelled secondary), A7e is then COMPLETE,
and A8/A9 proceed regardless of that status.  Only a failure of the OTHER
gates (N-CHK*, G-N3, G-N5) blocks the run with exit 3.

LIMITATIONS (also printed at the end):
  * p_NB is a rank-exact count over the sampled neighbourhood of ONE
    protein; POSITION-SPECIFIC/REGION-LIKE say nothing beyond it
    (frozen section 8).
  * NB members are not independent (second_at_position; amendment item
    4's collapsed sensitivity is reported for exactly that reason, and
    it carries no word).
  * d3 is a CA-CA distance in a crystal structure; cells are thresholded
    definitions, so conclusions near thresholds inherit that
    discreteness.
  * The D1 cross-check and G-N2 are same-pipeline regression tests, not
    independent evidence (AGENTS 6).
  * Cell CIs are marginal (not multiplicity-adjusted); they are
    descriptive companions to the two pre-registered words.

Usage:
  venv/bin/python3 scripts/172_neigh_analysis.py --mode smoke
  venv/bin/python3 scripts/172_neigh_analysis.py --mode full
"""

import argparse
import hashlib
import importlib.util
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

N_BOOT_ENV = os.environ.get("N_BOOT")
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase4_common as p4c          # noqa: E402
from scripts.lib import phase3_common as p3c          # noqa: E402
from scripts.lib import phase2_diag as pdg            # noqa: E402

PREREG = ROOT / "docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md"
PREREG_SHA = "167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e"
AMEND = ROOT / ("docs/tasks/phase4-strengthening/prereg/"
                "NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md")
AMEND_SHA = "f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a"
AMEND2 = ROOT / ("docs/tasks/phase4-strengthening/prereg/"
                 "NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md")
AMEND2_SHA = "b636a4d193efa16ed36e7d7feeb5a357c99cd5f202437bf100a55b80f822b55a"
ROSTER = ROOT / "data/processed/phase4/neigh/roster_v1.csv"
ROSTER_SHA = "675a24f1963878568e65b6d630e25e9ce649627c3f02ab0d5e65ec438f2d85d6"
CELLS = ROOT / "data/processed/phase4/neigh/eligible_cells_v1.csv"
CELLS_SHA = "db86399b8858e890fd11cb2c3e7debd2857f66f33eea7d87c769862b8408ba22"
D1 = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
D1_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
STORED3 = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
STORED3_SHA = "69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de"
WT_CACHE = ROOT / "data/processed/esm2_wt_scores.csv"
A222V_BG = ROOT / "data/processed/esm2_a222v_bg_scores.csv"
NEIGH_DIR = ROOT / "data/processed/phase4/neigh"
NEIGH_NONH = ROOT / "data/processed/phase4/neigh_nonH"
ATLAS = ROOT / "data/processed/task32_analysis_table.csv"

T_A222V_H = -0.090021683
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.05951138449511738
SIX_NULLS = ["G_I192T", "AV_220", "AV_155", "AV_195", "G_L178T", "AV_175"]
AMENDED_CELLS = ("C1", "C2", "C5")
CELLS_FOR_STATS = ("C1", "C2", "C3", "C4")
CELL_ALL = ("C1", "C2", "C5", "C3", "C4")
CELL_ORD = {"C1": 0, "C2": 1, "C3": 2, "C4": 3, "C5": 4}
GATE_N = 10000          # G-N4/G-N5: fixed in both modes (A6 G-DEC7)
P1_N = 10000            # Phase 1 CI gate: fixed (A6 G-DEC7)
NOISE_DRAWS = 100
PLANT_SEED = 3           # G-N5's mechanics vector only (N-AN14)
PLANT_SEEDS = tuple(range(100))   # Amendment 2: pre-listed 0..99
NOISE_SD = 0.4
WORDS4 = ("3D-LOCAL", "SEQUENCE-LOCAL", "BOTH-LOCAL", "NEITHER-RESOLVED")
CORRECT_MIN = 0.80       # Amendment 2 item 2 (per single-arm plant)
WRONG_MAX = 0.15         # wrong-arm CI-excludes-zero rate (v1's own bound)
NONE_MIN = 0.85          # none-plant NEITHER-RESOLVED rate
SPLINE_Q = (25.0, 50.0, 75.0)    # Amendment 3 item 2 interior knots
PATSY_TOL = 1e-10        # fast-basis vs patsy equivalence gate

t0 = time.time()
gates = []


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gate(name, val, detail=""):
    """val: True -> PASS, False -> FAIL, None -> PENDING."""
    if val is None:
        tag, stored = "PENDING", None
    else:
        stored = bool(val)
        tag = "PASS" if stored else "FAIL"
    gates.append((name, stored))
    print(f"  [{tag}] {name}" + (f": {detail}" if detail else ""), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    n_boot = int(N_BOOT_ENV) if N_BOOT_ENV else (300 if args.mode == "smoke"
                                                 else 10000)
    provisional = (args.mode == "smoke" or n_boot != 10000)
    word_tag = " [PROVISIONAL - smoke]" if provisional else ""

    banner("172 -- Module N neighbour-arm analysis (frozen sections 5+6)")
    print(f"  mode={args.mode} N_BOOT={n_boot} "
          f"(env N_BOOT={'set' if N_BOOT_ENV else 'unset'}) SEED={SEED}")
    print(f"  Frozen section 6 pins production CIs at 10,000 draws. "
          f"Section 6 uses N_BOOT={n_boot} here; G-N4/G-N5/Phase-1 are "
          "fixed at 10,000 in BOTH modes."
          + ("  -> every number and word below is PROVISIONAL"
             if provisional else "  -> production values"))
    print("\nPRE-REGISTERED DECISIONS (full text in the docstring):")
    for k, v in [
        ("N-AN1", "inputs sha-pinned (roster, cells, D1, stored d3, both "
                  "preregs); mismatch -> exit 3."),
        ("N-AN2", "existing nulls' rho_H READ from D1, checked against "
                  "recomputation from cached rows (<1e-8 over 96)."),
        ("N-AN3", "A222V rho_H canonical + independent, frozen "
                  "-0.090021683 (<1e-9); same-site rank gated 2/19."),
        ("N-AN4", "new rho_b from neigh/bg_<id>.csv with the same "
                  "validated function; scratch never read."),
        ("N-AN5", "G-N3: coverage >= 95% of eligible H; missing file = "
                  "PENDING, short file = FAIL."),
        ("N-AN6", "section 5 runs iff complete NB >= 30 (amendment 5), "
                  "else SKIPPED; position-collapse sensitivity beside "
                  "the primary, no word (amendment 4)."),
        ("N-AN7", "section 6 runs iff all 50 new complete; cells by "
                  "frozen section 2 + C5; C5 mean is a disclosed extra."),
        ("N-AN8", "partials: joint-P ids default_rng(SEED) (10,000 fixed "
                  "for gates); cell means: per-cell seeds SEED+ord == "
                  "background_boot; contrasts: difference of cell "
                  "draws; section 6 CIs at N_BOOT."),
        ("N-AN9", "G-N5 identity / draw-by-draw (slow references) / "
                  "Phase 1 CI, all fixed 10,000 both modes."),
        ("N-AN10", "G-N4 plants on real geometry: z-feature + 0.4*eps "
                   "(eps seed 3 shared), noise seed 1000 x100 draws, "
                   "fire <= 0.15; fixed seed, never re-seeked."),
        ("N-AN11", "smoke N_BOOT=300 -> PROVISIONAL; full -> final; "
                   "smoke gate failure stops the run."),
        ("N-AN12", "full-frame secondary needs neigh_nonH/ files; else "
                   "PENDING (no word)."),
        ("N-AN13", "torch never imported; checked before exit."),
        ("N-AN15", "AMENDMENT 3: section 6's partial is now the "
                   "FLEXIBLE-CONTROL partial (rank(rho) and rank(feature) "
                   "on a natural cubic spline basis of the RAW other "
                   "distance, knots = pool 25/50/75 percentiles, refit per "
                   "resample); the linear partial is a labelled secondary; "
                   "G-N4 re-run on the flexible statistic with Amendment 2's "
                   "criteria unchanged; fast basis gated against patsy at "
                   "1e-10; item 5's fallback applied literally (word or NO "
                   "WORD + secondary), A7e then COMPLETE either way."),
        ("N-AN14", "AMENDMENT 2: G-N4 as RATES over pre-listed seeds "
                   "0..99 (seed 3 included) x 3 plants, confusion "
                   "matrix printed; correct word >= 80% per single-arm "
                   "plant, wrong-arm fire <= 15%, none-plant "
                   "NEITHER-RESOLVED >= 85%; section 6 word printed "
                   "with the matrix and becomes NO WORD if either "
                   "correct-word rate < 80%; G-N5 mechanics vector "
                   "unchanged (seed-3 plant)."),
    ]:
        print(f"  {k}: {v}")

    # ------------------------------------------------------------ hashes --
    banner("N-CHK0 -- INPUT HASHES (N-AN1)", "-")
    for nm, path, want in (("prereg v1", PREREG, PREREG_SHA),
                           ("Amendment 1", AMEND, AMEND_SHA),
                           ("Amendment 2", AMEND2, AMEND2_SHA),
                           ("roster_v1", ROSTER, ROSTER_SHA),
                           ("eligible_cells_v1", CELLS, CELLS_SHA),
                           ("D1 rho table", D1, D1_SHA),
                           ("stored 3d distance", STORED3, STORED3_SHA)):
        got = sha256(path)
        gate(f"N-CHK0 {nm} sha256", got == want, f"{got[:16]}...")

    # --------------------------------------------------- frame, H, rows ---
    atlas = pd.read_csv(ATLAS)
    frame_rows = atlas.dropna(subset=["delta_esm", "own_e_b"])
    frame = sorted(int(p) for p in frame_rows.position.unique())
    spec = importlib.util.spec_from_file_location(
        "s125_phase2_analysis", ROOT / "scripts/125_phase2_analysis.py")
    s125 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s125)
    H = sorted(int(p) for p in s125.holdout(s125.build_frame()))
    h_rows = frame_rows[frame_rows.position.isin(H)][
        ["position", "mut_aa", "own_e_b"]]
    gate("N-CHK1 frame 654 / H 455 / H rows 7526",
         len(frame) == 654 and len(H) == 455 and len(h_rows) == 7526,
         f"{len(frame)} / {len(H)} / {len(h_rows)}")

    wt = pd.read_csv(WT_CACHE)
    wt_map = {(int(r.position), r.mut_aa): float(r.esm2_score)
              for r in wt.itertuples()}

    def rho_of(sub, own, label=""):
        """N-AN2/N-AN4: Spearman(delta, own_e_b) over H frame rows."""
        m = h_rows[h_rows.position != int(own)].merge(
            sub, on=["position", "mut_aa"])
        if "delta" not in m.columns:
            d = []
            for p, mu, s in zip(m.position, m.mut_aa, m.score):
                key = (int(p), mu)
                if key not in wt_map:
                    raise SystemExit(f"ERROR: WT cache missing {key} "
                                     f"({label})")
                d.append(float(s) - wt_map[key])
            m = m.assign(delta=d)
        return (float(p3c.spearman(m.delta.to_numpy(float),
                                   m.own_e_b.to_numpy(float))), len(m))

    # --------------------------------- canonical builder, A222V, D1 ------
    banner("N-CHK2 -- D1 CROSS-CHECK, A222V ANCHORS, SAME-SITE RANK", "-")
    _, A = pdg.build(verbose=False)
    _, point_h, rho_a_H = pdg.rho_table(A)
    gate("N-CHK2 A222V canonical rho_H vs frozen -0.090021683",
         abs(rho_a_H - T_A222V_H) < 1e-9,
         f"got {rho_a_H!r} |diff|={abs(rho_a_H - T_A222V_H):.3e}")

    av = pd.read_csv(A222V_BG)
    av_sub = av[["position", "mut_aa"]].assign(
        score=av.esm2_score_a222v_bg)
    rho_a_mine, n_av = rho_of(av_sub, 222, "A222V")
    gate("N-CHK2 A222V independent rho_H vs canonical",
         abs(rho_a_mine - rho_a_H) < 1e-9,
         f"got {rho_a_mine!r} |diff|={abs(rho_a_mine - rho_a_H):.3e} "
         f"over {n_av} rows")

    d1 = pd.read_csv(D1)
    gate("N-CHK2 D1 has 96 unique backgrounds",
         len(d1) == 96 and d1.bg_id.nunique() == 96, str(len(d1)))
    diffs, err = [], None
    for r in d1.itertuples():
        try:
            rho_m, _ = rho_of(
                pd.read_csv(ROOT / f"data/processed/phase2/bg_{r.bg_id}.csv"),
                r.position, r.bg_id)
        except Exception as e:                       # missing file etc.
            err = f"{r.bg_id}: {e}"
            break
        diffs.append(abs(rho_m - float(r.rho_H)))
    dmax = max(diffs) if diffs else float("inf")
    gate("N-CHK2 all 96 D1 rho_H == recomputation from cached rows "
         "(<1e-8)", err is None and dmax < 1e-8,
         err or f"max|diff| = {dmax:.3e} over {len(diffs)}")
    dmax_pdg = max(abs(float(r.rho_H) - float(point_h[r.bg_id]))
                   for r in d1.itertuples())
    print(f"  (informational) max|D1 - canonical builder| = {dmax_pdg:.3e}")

    arm_s = d1[d1.arm == "S"]
    rank_signed = 1 + sum(1 for v in arm_s.rho_H if v < rho_a_H)
    rank_abs = 1 + sum(1 for v in arm_s.rho_H if abs(v) > abs(rho_a_H))
    all_neg = all(v < 0 for v in list(arm_s.rho_H) + [rho_a_H])
    gate("N-CHK2 same-site rank of A222V among the 18 Arm S == 2/19",
         rank_signed == 2 and rank_abs == 2 and len(arm_s) == 18,
         f"signed {rank_signed}/19, |rho| {rank_abs}/19, "
         f"n(arm S)={len(arm_s)}, all-negative={all_neg}")

    # ------------------------------------------------------------ geometry --
    banner("N-CHK3 -- POOL P, CELLS, COVERAGE (G-N3)", "-")
    roster = pd.read_csv(ROSTER)
    gate("N-CHK3 roster = 50 unique, 40 in C1/C2/C5",
         len(roster) == 50 and roster.bg_id.nunique() == 50
         and int(roster.cell.isin(AMENDED_CELLS).sum()) == 40,
         f"{len(roster)} rows, "
         f"{int(roster.cell.isin(AMENDED_CELLS).sum())} in C1/C2/C5")

    stored = pd.read_csv(STORED3)
    ex = stored[stored.resolved & (stored.position != 222)].copy()
    gate("N-CHK3 67 resolved existing nulls (non-222)", len(ex) == 67,
         str(len(ex)))
    ex_d3 = ex.d3_CA.to_numpy(float)
    ex_ds = ex.dist_seq.to_numpy(float)
    lab = np.asarray(p4c.cell_labels(ex_d3, ex_ds), dtype=object)
    lab = np.where((lab == "") & (ex_d3 <= 12.0), "C5", lab)
    ex["cell"] = [str(x) for x in lab]
    cc = ex.cell.value_counts().to_dict()
    gate("N-CHK3 existing-null cells {C1:1, C2:3, C3:3, C4:51, C5:2, "
         "gap:7}", cc.get("C1") == 1 and cc.get("C2") == 3
         and cc.get("C3") == 3 and cc.get("C4") == 51
         and cc.get("C5") == 2 and cc.get("") == 7, str(cc))
    c5_set = set(ex.loc[ex.cell == "C5", "bg_id"])
    gate("N-CHK3 C5 existing members are exactly AV_195 + G_I192T",
         c5_set == {"AV_195", "G_I192T"}, str(sorted(c5_set)))

    # roster cell must equal geometry cell (frozen section 2 + C5)
    mismatch = []
    for r in roster.itertuples():
        d3r, dsr = float(r.d3), float(r.dseq)
        lab1 = str(np.asarray(p4c.cell_labels([d3r], [dsr]),
                              dtype=object)[0])
        if lab1 == "" and d3r <= 12.0:
            lab1 = "C5"
        if lab1 != r.cell:
            mismatch.append(f"{r.bg_id}: roster {r.cell} != {lab1}")
    gate("N-CHK3 roster cell == geometry cell for all 50",
         not mismatch, "; ".join(mismatch) if mismatch else
         "all 50 match frozen section 2 + C5 definitions")

    p_new = roster.sort_values("score_order")[
        ["bg_id", "cell", "position", "d3", "dseq"]].assign(source="new")
    p_ex = ex[["bg_id", "cell", "position"]].copy()
    p_ex["d3"] = ex_d3
    p_ex["dseq"] = ex_ds
    p_ex["source"] = "existing"
    pool = pd.concat([p_new, p_ex[p_new.columns]], ignore_index=True)
    gate("N-CHK3 Pool P = 117 = 50 new + 67 existing",
         len(pool) == 117 and int((pool.source == "new").sum()) == 50
         and int((pool.source == "existing").sum()) == 67,
         f"{len(pool)} rows")
    print("  Pool P cells: " + ", ".join(
        f"{c} {int((pool.cell == c).sum())}" for c in CELL_ALL))

    # ---------------------------------------------------- coverage / G-N3 --
    hset = set(H)
    cov = []
    for r in roster.itertuples():
        exp = [p for p in H if p != int(r.position)]
        f = NEIGH_DIR / f"bg_{r.bg_id}.csv"
        if not f.exists():
            cov.append((r.bg_id, r.cell, None, len(exp)))
            continue
        got = len({int(p) for p in pd.read_csv(f).position.unique()
                   if int(p) in hset})
        cov.append((r.bg_id, r.cell, got / len(exp), len(exp)))
    n_missing = sum(1 for _, _, c, _ in cov if c is None)
    n_short = sum(1 for _, _, c, _ in cov if c is not None and c < 0.95)
    n_complete = sum(1 for _, _, c, _ in cov if c is not None and c >= 0.95)
    if n_short:
        gate("G-N3 every scored new background >= 95% of eligible H",
             False, f"{n_short} present but short")
    elif n_missing == len(cov):
        gate("G-N3 every scored new background >= 95% of eligible H",
             None, "PENDING: 0/50 new backgrounds scored (the night has "
                   "not run); 0 short files")
    else:
        gate("G-N3 every scored new background >= 95% of eligible H",
             n_short == 0,
             f"{n_complete} complete, {n_missing} not yet scored, "
             f"{n_short} short")
    for c in AMENDED_CELLS + ("C3",):
        ncc = sum(1 for b, cc2, v, _ in cov if cc2 == c
                  and v is not None and v >= 0.95)
        ntt = sum(1 for _, cc2, _, _ in cov if cc2 == c)
        print(f"    {c}: complete {ncc}/{ntt}")

    complete_nb = 6 + sum(1 for _, c, v, _ in cov
                          if c in AMENDED_CELLS and v is not None
                          and v >= 0.95)
    print(f"  complete NB members (amendment item 5): {complete_nb}/46 "
          f"(six existing + {complete_nb - 6}/40 new C1/C2/C5)")
    print(f"  Pool P complete: {117 - n_missing - n_short}/117 "
          f"(new complete {n_complete}/50)")

    # ------------------------------------------------------------ vectors --
    d3P = pool.d3.to_numpy(float)
    dsP = pool.dseq.to_numpy(float)
    cellsP = pool.cell.to_numpy(str)
    nP = len(pool)

    def z(x):
        x = np.asarray(x, dtype=float)
        return (x - x.mean()) / x.std()

    zd, zs = z(d3P), z(dsP)

    def make_ids(n, n_boot, seed):
        rng = np.random.default_rng(seed)
        ids = np.empty((n_boot, n), dtype=np.int64)
        for i in range(n_boot):
            ids[i] = rng.integers(0, n, n)
        return ids

    def partial_arm(rho, ids, which, slow=False):
        out = np.empty(len(ids), dtype=float)
        for i, idx in enumerate(ids):
            a = rho[idx]
            b, c = (d3P[idx], dsP[idx]) if which == "d3" else (dsP[idx],
                                                               d3P[idx])
            if not slow:
                out[i] = p4c.partial_spearman(a, b, [c])
            else:
                r_xy = spearmanr(a, b).statistic
                r_xz = spearmanr(a, c).statistic
                r_yz = spearmanr(b, c).statistic
                den = np.sqrt((1 - r_xz ** 2) * (1 - r_yz ** 2))
                out[i] = ((r_xy - r_xz * r_yz) / den if den > 0
                          else float("nan"))
        return out

    def cell_mean_draws(vals, seed, n_boot):
        ids = make_ids(len(vals), n_boot, seed)
        return np.array([float(vals[ix].mean()) for ix in ids])

    def cell_mean_point(vals):
        return float(vals.mean()) if len(vals) else float("nan")

    # pool-level statistics keyed by row index (for the identity gate:
    # stat(arange) must equal the point estimate computed directly)
    def cell_mean_pool(rho, idx, cell):
        v = rho[idx][cellsP[idx] == cell]
        return float(v.mean()) if v.size else float("nan")

    def contrast_pool(rho, idx, ca, cb):
        return (cell_mean_pool(rho, idx, ca) - cell_mean_pool(rho, idx, cb))

    # ------------------------------------- Amendment 3 flexible control ----
    # Natural cubic regression spline basis (Wood, GAM p.146) exactly as
    # patsy.mgcv_cubic_splines builds it, replicated in numpy for speed and
    # GATED against patsy itself below.  Knots = [min, q25, q50, q75, max] of
    # the RAW control distance over the pool -> five basis columns.
    def natural_f(knots):
        from scipy.linalg import solve_banded
        h = np.diff(knots)
        diag = (h[:-1] + h[1:]) / 3.0
        ul = h[1:-1] / 6.0
        banded_b = np.array([np.r_[0.0, ul], diag, np.r_[ul, 0.0]])
        d = np.zeros((knots.size - 2, knots.size))
        for i in range(knots.size - 2):
            d[i, i] = 1.0 / h[i]
            d[i, i + 2] = 1.0 / h[i + 1]
            d[i, i + 1] = -d[i, i] - d[i, i + 2]
        fm = solve_banded((1, 1), banded_b, d)
        return np.vstack([np.zeros(knots.size), fm, np.zeros(knots.size)])

    def cr_basis(x, knots, f):
        n = knots.size
        x = np.asarray(x, dtype=float)
        lb = np.searchsorted(knots, x) - 1
        lb[lb == -1] = 0
        lb[lb == n - 1] = n - 2
        h = np.diff(knots)
        hj = h[lb]
        xj1_x = knots[lb + 1] - x
        x_xj = x - knots[lb]
        ajm = xj1_x / hj
        ajp = x_xj / hj
        cjm_3 = xj1_x * xj1_x * xj1_x / (6.0 * hj)
        cjm_3[x > np.max(knots)] = 0.0
        cjm = cjm_3 - hj * xj1_x / 6.0
        cjp_3 = x_xj * x_xj * x_xj / (6.0 * hj)
        cjp_3[x < np.min(knots)] = 0.0
        cjp = cjp_3 - hj * x_xj / 6.0
        j1 = lb + 1
        I = np.eye(n)
        return (ajm[:, None] * I[lb, :] + ajp[:, None] * I[j1, :]
                + cjm[:, None] * f[lb, :] + cjp[:, None] * f[j1, :])

    KNOTS = {k: np.array([v.min()] + list(np.percentile(v, SPLINE_Q))
                        + [v.max()]) for k, v in (("d3", d3P), ("dseq", dsP))}
    F_MAP = {k: natural_f(KNOTS[k]) for k in KNOTS}

    # N-CHK4: the fast basis must equal patsy's own cr() basis
    import patsy
    dmax_patsy = 0.0
    probes = [("dseq", dsP), ("d3", d3P),
              ("probe", np.random.default_rng(20261003).lognormal(
                  size=nP) * 30.0)]
    for nm, v in probes:
        k = nm if nm in KNOTS else "dseq"
        kn = KNOTS[k] if nm in KNOTS else np.array(
            [v.min()] + list(np.percentile(v, SPLINE_Q)) + [v.max()])
        mine = cr_basis(v, kn, natural_f(kn))
        ref = np.asarray(patsy.dmatrix("cr(x, knots=q)",
                                       {"x": v, "q": list(kn[1:-1])}))[:, 1:]
        dmax_patsy = max(dmax_patsy, float(np.max(np.abs(mine - ref))))
    gate("N-CHK4 fast spline basis == patsy cr(x, knots=...) non-intercept "
         f"columns (<{PATSY_TOL:g})", dmax_patsy < PATSY_TOL,
         f"max|diff| = {dmax_patsy:.3e} over {len(probes)} probes "
         f"(pool dseq, pool d3, random lognormal)")
    for k in ("d3", "dseq"):
        B = cr_basis((dsP if k == "dseq" else d3P), KNOTS[k], F_MAP[k])
        print(f"  spline basis for the RAW {k} control: knots "
              f"{np.round(KNOTS[k], 3).tolist()}, basis {B.shape[1]} "
              f"columns, rank {np.linalg.matrix_rank(B)}, "
              f"cond {np.linalg.cond(B):.3f} "
              "(Amendment 3's three named knots are operative; '4 df' and "
              "three knots cannot both hold in the standard "
              "parametrisation -- disclosed N-AN15)")

    def flex_partial(rho, feat, ctrl, which, slow=False):
        """Amendment 3 item 2: flexible-control partial Spearman."""
        x = np.asarray(rho, dtype=float)
        y = np.asarray(feat, dtype=float)
        if x.size < 3:
            return float("nan")
        rx = rankdata(x, method="average")
        ry = rankdata(y, method="average")
        B = cr_basis(ctrl, KNOTS[which], F_MAP[which])
        if np.linalg.matrix_rank(B) < B.shape[1]:
            return float("nan")
        if slow:                       # different OLS path for G-N5
            Q, _ = np.linalg.qr(B)
            ex = rx - Q @ (Q.T @ rx)
            ey = ry - Q @ (Q.T @ ry)
        else:
            ex = rx - B @ np.linalg.lstsq(B, rx, rcond=None)[0]
            ey = ry - B @ np.linalg.lstsq(B, ry, rcond=None)[0]
        if ex.std() == 0.0 or ey.std() == 0.0:
            return float("nan")
        return float(np.corrcoef(ex, ey)[0, 1])

    def flex_arm(rho, ids, which, slow=False):
        out = np.empty(len(ids), dtype=float)
        for i, idx in enumerate(ids):
            if which == "d3":           # control = raw dseq
                out[i] = flex_partial(rho[idx], d3P[idx], dsP[idx], "dseq",
                                      slow=slow)
            else:                       # control = raw d3
                out[i] = flex_partial(rho[idx], dsP[idx], d3P[idx], "d3",
                                      slow=slow)
        return out

    # ------------------------------------------------------- plants (G-N4) --
    banner("G-N4 (HARD, AMENDMENTS 2+3) -- PLANTED SIGNAL/NULL RATES OVER "
           f"PRE-LISTED SEEDS {PLANT_SEEDS[0]}..{PLANT_SEEDS[-1]} ON THE "
           f"REAL POOL-P GEOMETRY, FLEXIBLE-CONTROL STATISTIC "
           f"(fixed {GATE_N} draws, eps shared across plants within a seed)",
           "-")
    pids = make_ids(nP, GATE_N, SEED)     # N-AN8 production partial stream

    def ci_of(rho, which):
        """PRIMARY statistic (Amendment 3): flexible-control partial."""
        return p3c.pct_ci(flex_arm(rho, pids, which))

    def ci_of_linear(rho, which):
        """LINEAR rank-control partial -- labelled secondary only."""
        return p3c.pct_ci(partial_arm(rho, pids, which))

    def plant_words(rho, wrong_arm):
        """(word, wrong_arm_excludes_zero) for one plant rho.

        wrong_arm is the OTHER feature: "dseq" for the 3D-only plant,
        "d3" for the sequence-only plant (Amendment 2 item 2 is about the
        wrong arm of that plant, not a fixed column)."""
        a, b = ci_of(rho, "d3"), ci_of(rho, "dseq")
        w = p4c.word_distance(a[:2], b[:2])
        wc = b if wrong_arm == "dseq" else a
        return w, p4c._excludes_zero(wc[0], wc[1])

    t_g4 = time.time()
    counts = {pl: {w: 0 for w in WORDS4}
              for pl in ("3D-only", "sequence-only", "none")}
    wrong_fires = {"3D-only": 0, "sequence-only": 0}
    failing_seeds = []
    seed3_line = ""
    for s in PLANT_SEEDS:
        eps_s = np.random.default_rng(s).standard_normal(nP)
        for pl, rho, w_arm in (
                ("3D-only", zd + NOISE_SD * eps_s, "dseq"),
                ("sequence-only", zs + NOISE_SD * eps_s, "d3"),
                ("none", eps_s, "dseq")):
            w, wrong_fire = plant_words(rho, w_arm)
            counts[pl][w] += 1
            if pl == "3D-only" and wrong_fire:
                wrong_fires["3D-only"] += 1
            if pl == "sequence-only" and wrong_fire:
                wrong_fires["sequence-only"] += 1
            if s == PLANT_SEED and pl == "3D-only":
                seed3_line = (f"seed {s} (the seed that failed the "
                              f"single-seed form): word {w}, "
                              f"wrong-arm CI excludes zero = {wrong_fire}")
            if ((pl == "3D-only" and w != "3D-LOCAL")
                    or (pl == "sequence-only" and w != "SEQUENCE-LOCAL")
                    or (pl == "none" and w != "NEITHER-RESOLVED")):
                failing_seeds.append(f"{pl}@seed{s}={w}")

    n_seed = len(PLANT_SEEDS)
    print("  confusion matrix: rows = plant (ground truth), columns = word "
          "returned by word_distance; cells = seeds out of "
          f"{n_seed}")
    print("    plant              " + "".join(f"{w:>18s}" for w in WORDS4))
    for pl in ("3D-only", "sequence-only", "none"):
        print(f"    {pl:<18s}" + "".join(f"{counts[pl][w]:>18d}"
                                        for w in WORDS4))
    print("  rates:")
    rate_3d = counts["3D-only"]["3D-LOCAL"] / n_seed
    rate_seq = counts["sequence-only"]["SEQUENCE-LOCAL"] / n_seed
    rate_none = counts["none"]["NEITHER-RESOLVED"] / n_seed
    rate_w3 = wrong_fires["3D-only"] / n_seed
    rate_ws = wrong_fires["sequence-only"] / n_seed
    print(f"    3D-only       correct word (3D-LOCAL)      {rate_3d:.3f} "
          f"(gate >= {CORRECT_MIN})")
    print(f"    sequence-only correct word (SEQUENCE-LOCAL) {rate_seq:.3f} "
          f"(gate >= {CORRECT_MIN})")
    print(f"    3D-only       wrong arm (dseq CI excl 0)   {rate_w3:.3f} "
          f"(gate <= {WRONG_MAX})")
    print(f"    sequence-only wrong arm (d3 CI excl 0)    {rate_ws:.3f} "
          f"(gate <= {WRONG_MAX})")
    print(f"    none          NEITHER-RESOLVED            {rate_none:.3f} "
          f"(gate >= {NONE_MIN}); any word fired "
          f"{n_seed - counts['none']['NEITHER-RESOLVED']}/{n_seed}")
    print(f"    false-attribution rate when truth is 3D-only (BOTH-LOCAL or "
          f"SEQUENCE-LOCAL returned): "
          f"{(counts['3D-only']['BOTH-LOCAL'] + counts['3D-only']['SEQUENCE-LOCAL']) / n_seed:.3f}")
    print(f"    seeds not returning the planted word: "
          f"{len(failing_seeds)} -> {failing_seeds[:12]}"
          f"{' ...' if len(failing_seeds) > 12 else ''}")
    print(f"  {seed3_line}")
    print(f"  (the linear rank-control statistic's confusion matrix for the "
          f"same 100 seeds is recorded in "
          f"PHASE4_A7_ANALYSIS_SMOKE_OUTPUT.txt from the Amendment-2 run; "
          f"it is NOT recomputed here -- Amendment 3 item 4 re-runs G-N4 on "
          f"the new statistic only)")
    print(f"  G-N4 wall {time.time() - t_g4:.0f}s")

    gate("G-N4 3D-only plant: correct word in >= 80% of 100 seeds",
         rate_3d >= CORRECT_MIN, f"{rate_3d:.3f} "
         f"({counts['3D-only']['3D-LOCAL']}/{n_seed})")
    gate("G-N4 sequence-only plant: correct word in >= 80% of 100 seeds",
         rate_seq >= CORRECT_MIN, f"{rate_seq:.3f} "
         f"({counts['sequence-only']['SEQUENCE-LOCAL']}/{n_seed})")
    gate("G-N4 3D-only plant: wrong-arm CI excludes zero in <= 15% of seeds",
         rate_w3 <= WRONG_MAX, f"{rate_w3:.3f} ({wrong_fires['3D-only']}/"
         f"{n_seed})")
    gate("G-N4 sequence-only plant: wrong-arm CI excludes zero in <= 15% of "
         "seeds", rate_ws <= WRONG_MAX,
         f"{rate_ws:.3f} ({wrong_fires['sequence-only']}/{n_seed})")
    gate("G-N4 none plant: NEITHER-RESOLVED in >= 85% of 100 seeds",
         rate_none >= NONE_MIN, f"{rate_none:.3f} "
         f"({counts['none']['NEITHER-RESOLVED']}/{n_seed})")
    sec6_word_allowed = (rate_3d >= CORRECT_MIN) and (rate_seq >= CORRECT_MIN)
    planted = dict(counts=counts, rate_3d=rate_3d, rate_seq=rate_seq,
                   rate_none=rate_none, rate_w3=rate_w3, rate_ws=rate_ws,
                   n_seed=n_seed,
                   false_attr=(counts["3D-only"]["BOTH-LOCAL"]
                               + counts["3D-only"]["SEQUENCE-LOCAL"])
                   / n_seed,
                   word_allowed=sec6_word_allowed)

    # ------------------------------------------------------------ G-N5 -----
    banner(f"G-N5 (HARD) -- identity, draw-by-draw reference, Phase 1 CI "
           f"(fixed {GATE_N})", "-")
    # G-N5's mechanics vector: the 3D-only plant at pre-listed seed 3,
    # exactly as first pre-registered (N-AN9/N-AN14 -- unchanged, not
    # re-selected).
    mech_rho = zd + NOISE_SD * np.random.default_rng(
        PLANT_SEED).standard_normal(nP)
    ar = np.arange(nP)

    id_pd3 = abs(p4c.partial_spearman(mech_rho[ar], d3P[ar], [dsP[ar]])
                 - p4c.partial_spearman(mech_rho, d3P, [dsP]))
    id_pds = abs(p4c.partial_spearman(mech_rho[ar], dsP[ar], [d3P[ar]])
                 - p4c.partial_spearman(mech_rho, dsP, [d3P]))
    id_cells = 0.0
    for c in CELL_ALL:
        id_cells = max(id_cells,
                       abs(cell_mean_pool(mech_rho, ar, c)
                           - cell_mean_point(mech_rho[cellsP == c])))
    id_c24 = abs(contrast_pool(mech_rho, ar, "C2", "C4")
                 - (cell_mean_point(mech_rho[cellsP == "C2"])
                    - cell_mean_point(mech_rho[cellsP == "C4"])))
    id_c34 = abs(contrast_pool(mech_rho, ar, "C3", "C4")
                 - (cell_mean_point(mech_rho[cellsP == "C3"])
                    - cell_mean_point(mech_rho[cellsP == "C4"])))
    id_max = max(id_pd3, id_pds, id_cells, id_c24, id_c34)
    gate("G-N5(i) identity: stat(arange) == point estimate (<1e-12)",
         id_max < 1e-12, f"max|diff| = {id_max:.3e}")

    # (ii-a) cell-mean draws vs p3c.background_boot, same seed per cell
    dmax_bg = 0.0
    for c in CELL_ALL:
        vals = mech_rho[cellsP == c]
        mine = cell_mean_draws(vals, SEED + CELL_ORD[c], GATE_N)
        ref, _ = p3c.background_boot(vals, n_boot=GATE_N,
                                     seed=SEED + CELL_ORD[c])
        dmax_bg = max(dmax_bg, float(np.nanmax(np.abs(mine - ref))))
    gate("G-N5(ii-a) cell-mean draws == background_boot draw by draw "
         "(<1e-12)", dmax_bg < 1e-12, f"max|diff| = {dmax_bg:.3e}")

    # (ii-b) partial draws vs slow closed-form reference
    dmax_part, bad = 0.0, 0
    for which in ("d3", "dseq"):
        f = partial_arm(mech_rho, pids, which)
        s = partial_arm(mech_rho, pids, which, slow=True)
        both_nan = np.isnan(f) & np.isnan(s)
        bad += int((np.isnan(f) ^ np.isnan(s)).sum())
        dmax_part = max(dmax_part,
                        float(np.nanmax(np.abs(np.where(both_nan, 0.0,
                                                        np.abs(f - s))))))
    gate("G-N5(ii-b) partial draws == slow closed-form reference "
         "(<1e-12, both arms, all draws)",
         dmax_part < 1e-12 and bad == 0,
         f"max|diff| = {dmax_part:.3e}, nan mismatches = {bad}")

    # (ii-c) contrast draws vs plain-Python rebuild
    c2v, c4v = mech_rho[cellsP == "C2"], mech_rho[cellsP == "C4"]
    ids_c2 = make_ids(len(c2v), GATE_N, SEED + CELL_ORD["C2"])
    ids_c4 = make_ids(len(c4v), GATE_N, SEED + CELL_ORD["C4"])
    fast = np.array([float(c2v[ix].mean()) for ix in ids_c2]) - \
        np.array([float(c4v[ix].mean()) for ix in ids_c4])
    slow = np.array([float(np.mean([c2v[j] for j in ix]))
                     - float(np.mean([c4v[j] for j in iy]))
                     for ix, iy in zip(ids_c2, ids_c4)])
    dmax_c24 = float(np.nanmax(np.abs(fast - slow)))
    gate("G-N5(ii-c) contrast draws == plain-Python rebuild (<1e-12)",
         dmax_c24 < 1e-12, f"max|diff| = {dmax_c24:.3e}")

    # (iii) Phase 1 CI reproduction (fixed 10,000)
    ar1 = A.a222v_rows
    draws_p1 = p3c.pos_cluster_boot(ar1.delta.to_numpy(float),
                                    ar1.own_e_b.to_numpy(float),
                                    ar1.position.to_numpy(),
                                    n_boot=P1_N, seed=SEED)
    lo, hi, nf = p3c.pct_ci(draws_p1)
    d_lo, d_hi = abs(lo - T_CI_LO), abs(hi - T_CI_HI)
    print(f"  Phase 1 CI: lo {lo!r} vs {T_CI_LO!r} (|diff| {d_lo:.3e}), "
          f"hi {hi!r} vs {T_CI_HI!r} (|diff| {d_hi:.3e}), {nf} finite")
    gate("G-N5(iii) Phase 1 CI reproduces (each endpoint < 1e-9)",
         d_lo < 1e-9 and d_hi < 1e-9, f"lo {d_lo:.3e}, hi {d_hi:.3e}")

    # N-AN15: two ADDITIONAL checks for the Amendment-3 flexible statistic
    id_flex = 0.0
    for which in ("d3", "dseq"):
        f_ar = flex_arm(mech_rho, ar.reshape(1, -1), which)[0]
        f_pt = (flex_partial(mech_rho, d3P, dsP, "dseq") if which == "d3"
                else flex_partial(mech_rho, dsP, d3P, "d3"))
        id_flex = max(id_flex, abs(f_ar - f_pt))
    gate("G-N5(iv) FLEX identity: stat(arange) == point estimate (<1e-12)",
         id_flex < 1e-12, f"max|diff| = {id_flex:.3e}")
    dmax_flex, bad_flex = 0.0, 0
    for which in ("d3", "dseq"):
        f = flex_arm(mech_rho, pids, which)
        s = flex_arm(mech_rho, pids, which, slow=True)
        both_nan = np.isnan(f) & np.isnan(s)
        bad_flex += int((np.isnan(f) ^ np.isnan(s)).sum())
        dmax_flex = max(dmax_flex,
                        float(np.nanmax(np.abs(np.where(both_nan, 0.0,
                                                        f - s)))))
    gate("G-N5(v) FLEX draws == slow QR-based OLS rebuild (<1e-12, both "
         "arms, all draws)",
         dmax_flex < 1e-12 and bad_flex == 0,
         f"max|diff| = {dmax_flex:.3e}, nan mismatches = {bad_flex}")

    # --------------------------------------------------------- section 5 --
    banner("SECTION 5 -- PRIMARY TEST (frozen) + AMENDMENT 4 SENSITIVITY",
           "-")
    six_d1 = d1.set_index("bg_id")
    ex_cell = dict(zip(ex.bg_id.astype(str), ex.cell))
    nb_new = roster[roster.cell.isin(AMENDED_CELLS)]
    nb_rows = []
    for b in SIX_NULLS:
        nb_rows.append(dict(bg_id=b, cell=ex_cell.get(b, "?"),
                            source="existing",
                            rho_H=float(six_d1.loc[b, "rho_H"]),
                            complete=True,
                            position=int(six_d1.loc[b, "position"])))
    complete_ids = {b for b, _, v, _ in cov if v is not None and v >= 0.95}
    for r in nb_new.itertuples():
        f = NEIGH_DIR / f"bg_{r.bg_id}.csv"
        if r.bg_id in complete_ids:
            rho, _ = rho_of(pd.read_csv(f), r.position, r.bg_id)
            comp = True
        else:
            rho, comp = float("nan"), False
        nb_rows.append(dict(bg_id=r.bg_id, cell=r.cell, source="new",
                            rho_H=rho, complete=comp,
                            position=int(r.position)))
    nb = pd.DataFrame(nb_rows)
    nb_c = nb[nb.complete].copy()

    if len(nb_c) < 30:
        print(f"  SKIPPED per amendment item 5: complete NB = "
              f"{len(nb_c)}/46 (< 30).  No p_NB, no word.")
        print(f"  (coverage: {n_complete}/50 new backgrounds scored; six "
              "existing always complete)")
    else:
        rho_a = rho_a_H
        k_neg = int((nb_c.rho_H <= rho_a).sum())
        k_abs = int((nb_c.rho_H.abs() <= abs(rho_a)).sum())
        p_neg = (1 + k_neg) / (1 + len(nb_c))
        p_abs = (1 + k_abs) / (1 + len(nb_c))
        w = p4c.word_neighbour(p_neg, len(nb_c))
        print("  NB (complete) rho_H values:")
        for r in nb_c.sort_values("rho_H").itertuples():
            print(f"    {r.bg_id:10s} cell {r.cell:3s} pos {r.position:4d} "
                  f"{r.rho_H:+.6f}")
        print(f"  |NB| = {len(nb_c)} (frozen UNDERPOWERED iff < 30)")
        print(f"  rho_A222V = {rho_a:+.9f} (frozen {T_A222V_H})")
        print(f"  p_NB(neg) = {p_neg:.6f}  (1 + {k_neg})/(1 + {len(nb_c)}); "
              f"p_NB(abs) = {p_abs:.6f}  (1 + {k_abs})/(1 + {len(nb_c)})")
        print(f"  WORD: {w}{word_tag}")
        print(f"  same-site rank: A222V {rank_signed}/19 (frozen 2/19)")
        coll = nb_c.groupby("position").rho_H.mean()
        p_coll = (1 + int((coll <= rho_a).sum())) / (1 + len(coll))
        print(f"  SENSITIVITY (amendment 4, NO word): position-collapsed "
              f"NB = {len(coll)} positions, p_NB(neg) = {p_coll:.6f} "
              f"(primary {p_neg:.6f}; {len(nb_c) - len(coll)} "
              "second_at_position merges)")
        if provisional:
            print("  NOTE: smoke run -- the numbers and word above are "
                  "PROVISIONAL; only a --mode full run is final.")

    # --------------------------------------------------------- section 6 --
    banner("SECTION 6 -- DISTANCES (frozen) ON POOL P", "-")
    n_pool_done = 117 - n_missing - n_short
    if n_pool_done < 117:
        print(f"  PENDING: Pool P incomplete ({n_pool_done}/117; new "
              f"{n_complete}/50 scored).  The partials/cells/contrasts "
              "are defined on the COMPLETE pool only (N-AN7) -- no "
              "numbers printed.")
    else:
        rhoP = []
        for r in pool.itertuples():
            if r.source == "new":
                rho, _ = rho_of(pd.read_csv(NEIGH_DIR / f"bg_{r.bg_id}.csv"),
                                r.position, r.bg_id)
            else:
                rho = float(six_d1.loc[r.bg_id, "rho_H"])
            rhoP.append(rho)
        rhoP = np.asarray(rhoP, dtype=float)

        # G-N5(i) repeated on the REAL vector
        id_real = 0.0
        for which in ("d3", "dseq"):
            f_ar = partial_arm(rhoP, ar.reshape(1, -1), which)[0]
            f_all = (p4c.partial_spearman(rhoP, d3P, [dsP])
                     if which == "d3" else
                     p4c.partial_spearman(rhoP, dsP, [d3P]))
            id_real = max(id_real, abs(f_ar - f_all))
        print(f"  G-N5(i) on the real rho vector: max|diff| = "
              f"{id_real:.3e} (<1e-12)")

        sec_ids = make_ids(nP, n_boot, SEED)
        # PRIMARY (Amendment 3): flexible-control partial
        draws_f3 = flex_arm(rhoP, sec_ids, "d3")
        draws_fs = flex_arm(rhoP, sec_ids, "dseq")
        ci_f3, ci_fs = p3c.pct_ci(draws_f3), p3c.pct_ci(draws_fs)
        pt_f3 = flex_partial(rhoP, d3P, dsP, "dseq")
        pt_fs = flex_partial(rhoP, dsP, d3P, "d3")
        # SECONDARY (labelled): the superseded linear rank-control partial
        draws_l3 = partial_arm(rhoP, sec_ids, "d3")
        draws_ls = partial_arm(rhoP, sec_ids, "dseq")
        ci_l3, ci_ls = p3c.pct_ci(draws_l3), p3c.pct_ci(draws_ls)
        pt_l3 = p4c.partial_spearman(rhoP, d3P, [dsP])
        pt_ls = p4c.partial_spearman(rhoP, dsP, [d3P])
        w6 = p4c.word_distance((ci_f3[0], ci_f3[1]), (ci_fs[0], ci_fs[1]))
        w6_lin = p4c.word_distance((ci_l3[0], ci_l3[1]),
                                   (ci_ls[0], ci_ls[1]))
        print(f"  N_BOOT={n_boot} for section 6 CIs"
              + (" (PROVISIONAL)" if provisional else " (production)"))
        print("  PRIMARY -- flexible-control partial (Amendment 3):")
        print(f"    partial rho_b ~ d3  | spline(dseq): {pt_f3:+.6f} CI "
              f"[{ci_f3[0]:+.6f}, {ci_f3[1]:+.6f}] ({ci_f3[2]} finite)")
        print(f"    partial rho_b ~ dseq | spline(d3) : {pt_fs:+.6f} CI "
              f"[{ci_fs[0]:+.6f}, {ci_fs[1]:+.6f}] ({ci_fs[2]} finite)")
        print("  SECONDARY -- linear rank-control partial (superseded; "
              "labelled secondary per Amendment 3 item 5, NOT the word "
              "source):")
        print(f"    partial rho_b ~ d3 | dseq  : {pt_l3:+.6f} CI "
              f"[{ci_l3[0]:+.6f}, {ci_l3[1]:+.6f}] -> word {w6_lin}")
        print(f"    partial rho_b ~ dseq | d3  : {pt_ls:+.6f} CI "
              f"[{ci_ls[0]:+.6f}, {ci_ls[1]:+.6f}]")
        if sec6_word_allowed:
            print(f"  WORD: {w6}{word_tag} (flexible-control statistic; "
                  f"Amendment 3 item 5, first branch -- every planted "
                  f"criterion passed)")
        else:
            print(f"  WORD: NO WORD{word_tag} -- Amendment 3 item 5, "
                  f"second branch: at least one planted criterion failed "
                  f"(3D-only correct-word rate {planted['rate_3d']:.3f}, "
                  f"sequence-only {planted['rate_seq']:.3f}); the raw "
                  f"flexible-statistic word would be {w6} and is reported "
                  f"WITHOUT interpretation.  All numbers above are still "
                  f"printed; section 5 is unaffected.")
        # Amendment 2 item 4: the real word always travels with the planted
        # confusion matrix, so a BOTH-LOCAL word can be read against its
        # measured false-attribution rate when the truth is 3D-only.
        print("  planted confusion matrix this word must be read against "
              f"(seeds 0..{planted['n_seed'] - 1}):")
        print("    plant              " + "".join(f"{w:>18s}"
                                                 for w in WORDS4))
        for pl in ("3D-only", "sequence-only", "none"):
            print(f"    {pl:<18s}" + "".join(
                f"{planted['counts'][pl][w]:>18d}" for w in WORDS4))
        print(f"    read: if the truth were 3D-only, the word would be "
              f"BOTH-LOCAL (or worse) {planted['false_attr']:.3f} of the "
              f"time; if the truth were sequence-only, the word would be "
              f"3D-LOCAL (or worse) "
              f"{(planted['counts']['sequence-only']['3D-LOCAL'] + planted['counts']['sequence-only']['BOTH-LOCAL']) / planted['n_seed']:.3f}"
              f"; with no signal, any word "
              f"{1 - planted['rate_none']:.3f} of the time.")

        print("  cell means of rho_b (background-level bootstrap CI):")
        for c in CELL_ALL:
            vals = rhoP[cellsP == c]
            draws = cell_mean_draws(vals, SEED + CELL_ORD[c], n_boot)
            lo_c, hi_c, nfc = p3c.pct_ci(draws)
            extra = "  (DISCLOSED EXTRA: not in frozen section 6)" \
                if c == "C5" else ""
            print(f"    {c}: n={len(vals)} mean={cell_mean_point(vals):+.6f} "
                  f"CI [{lo_c:+.6f}, {hi_c:+.6f}] ({nfc} finite){extra}")
        for name, ca, cb in (("C2-C4", "C2", "C4"), ("C3-C4", "C3", "C4")):
            va, vb = rhoP[cellsP == ca], rhoP[cellsP == cb]
            ia = make_ids(len(va), n_boot, SEED + CELL_ORD[ca])
            ib = make_ids(len(vb), n_boot, SEED + CELL_ORD[cb])
            draws = np.array([float(va[x].mean()) - float(vb[y].mean())
                              for x, y in zip(ia, ib)])
            lo_c, hi_c, nfc = p3c.pct_ci(draws)
            print(f"    {name}: {cell_mean_point(va) - cell_mean_point(vb):+.6f} "
                  f"CI [{lo_c:+.6f}, {hi_c:+.6f}] ({nfc} finite)")

    # --------------------------------------------------- full frame (sec) --
    banner("FULL-FRAME SECONDARY (frozen section 5: secondary, no word)",
           "-")
    nb_new_ids = list(nb[nb.source == "new"].bg_id)
    nonh_ok = sum(1 for b in nb_new_ids
                  if (NEIGH_NONH / f"bg_{b}.csv").exists())
    if nonh_ok == len(nb_new_ids):
        full_new = []
        for b, pos in zip(nb_new_ids, nb[nb.source == "new"].position):
            df_h = pd.read_csv(NEIGH_DIR / f"bg_{b}.csv")
            df_n = pd.read_csv(NEIGH_NONH / f"bg_{b}.csv")
            sub = pd.concat([df_h[["position", "mut_aa", "delta"]],
                             df_n[["position", "mut_aa", "delta"]]],
                            ignore_index=True)
            m = frame_rows[["position", "mut_aa", "own_e_b"]].merge(
                sub, on=["position", "mut_aa"])
            full_new.append(float(p3c.spearman(m.delta.to_numpy(float),
                                               m.own_e_b.to_numpy(float))))
        six_full = [float(six_d1.loc[b, "rho_full"]) for b in SIX_NULLS]
        allv = full_new + six_full
        p_full = (1 + sum(1 for v in allv if v <= rho_a_H)) / (1 + len(allv))
        print(f"  full-frame p_NB(neg) = {p_full:.6f} over {len(allv)} "
              "(SECONDARY, no word)")
    else:
        print(f"  PENDING: {nonh_ok}/{len(nb_new_ids)} NB new backgrounds "
              "have nonH files in "
              "data/processed/phase4/neigh_nonH/ (night B, SB4)")

    # ------------------------------------------------------------ summary --
    banner("SUMMARY")
    n_pass = sum(1 for _, v in gates if v is True)
    n_fail = sum(1 for _, v in gates if v is False)
    n_pend = sum(1 for _, v in gates if v is None)
    torch_in = "torch" in sys.modules
    print(f"  {n_pass} PASS, {n_fail} FAIL, {n_pend} PENDING "
          f"of {len(gates)} checks.")
    print(f"  N-AN13: torch in sys.modules after this run: {torch_in} "
          "(must be False)")
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the docstring):")
    print("    * words describe A222V vs this protein's sampled "
          "neighbourhood only (frozen section 8).")
    print("    * NB members are not independent (second_at_position) -> "
          "amendment 4 sensitivity reported without a word.")
    print("    * D1 cross-checks are same-pipeline regression tests, not "
          "independent evidence.")
    print("    * cell CIs are marginal, not multiplicity-adjusted.")
    print("    * d3 is a CA-CA distance in a crystal structure; cell "
          "thresholds are discrete definitions.")
    print("    * Amendment 3's parenthetical pins both '4 degrees of "
          "freedom' and three interior knots, which cannot both hold in the "
          "standard natural-spline parametrisation (m interior knots give "
          "m+1 basis functions); the three named knots were treated as "
          "operative and the basis is patsy's canonical cr with those knots "
          "(five columns, gated against patsy above) -- disclosed.")
    failed = n_fail + (1 if torch_in else 0)
    print(f"\nA7e RESULT: " + ("GATE FAIL -- exit 3" if failed else
                               "GATE PASS -- exit 0"))
    print(f"  elapsed {time.time() - t0:.1f}s")
    if failed:
        sys.exit(3)


if __name__ == "__main__":
    main()
