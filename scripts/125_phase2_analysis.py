"""Script 125 (Phase 2 session 2a, task G3) -- the pre-registered
Phase 2 analysis (frozen PHASE2_PREREG.md sections 2, 4, 5, 6, 7).

PRE-REGISTERED: this docstring was written before the first run of this
script (PHASE2_EXECUTION.md, Task G3).  Per execution-doc rule 7 it is
NOT edited after any Phase 2 score exists; session 2a validates only
--mode cached-ae (no Phase 2 scores exist yet).  NO torch/esm import
anywhere (cached CSVs only).

TWO INPUT MODES (--mode required, no default):
  --mode phase2    reads data/processed/phase2/bg_<bg_id>.csv (schema
                   bg_id, position, mut_aa, score -- execution doc G2)
                   for all 96 roster backgrounds + A222V's cached arm
                   (delta_esm, PIN-3).  This is THE pre-registered
                   analysis.  NOT RUN IN SESSION 2a (no scores exist).
  --mode cached-ae validation mode: builds the same structures from
                   task82_ae_raw.csv, line-for-line the construction of
                   script 121 (which P1/G2 gated against the raw caches
                   at max|diff| 9.714e-17): join esm2_wt_scores on
                   (position, mut_aa) -> delta = score_bg - esm2_score;
                   A222_V relabelled __A222V__ and never a placebo;
                   merge own_context_metrics on hgvs_pro; own_e_b
                   non-null; drop rows whose target position equals the
                   background's own position (G6, expected 0 on the
                   grid).  Arm G does not exist here, so the null set
                   degenerates to N = Arm V and the held-out set H
                   intersects the grid in 0 positions (H excludes the
                   AE frame by definition) -- both facts are printed,
                   and the frozen section 5 OUTCOME WORD IS NOT
                   COMPUTED IN THIS MODE (it needs p_spec(H) and N =
                   V u G; cached-ae is validation only and must never
                   be quoted as the pre-registered result).

STATISTIC (frozen section 2, both modes): delta_b(v) = S(v|b) -
S(v|WT); rho_b = Spearman(delta_b, own_e_b) over usable variants of the
10,757-row frame (non-null own_e_b), EXCLUDING rows whose target
position equals the background's position (frozen G-C).  S(v|WT) is the
frame's own esm2_score column (joined on (position, mut_aa)); A222V's
arm is its cached delta_esm (its rho over the full frame must reproduce
the anchor -- gate G-A).  The p_spec threshold is ALWAYS A222V's rho
computed on the SAME rows as the rho_b it is compared against
(full-frame -> -0.088118; cached-ae grid -> -0.104321773).

INFERENCE (frozen section 4): position-cluster bootstrap (positions as
clusters, all variants with multiplicity), N_BOOT draws (env, default
10000), SEED (env, default 0), 95% percentile CIs for all rho_b.
p_spec = (1 + #{b in N : rho_b <= rho_A222V}) / (1 + |N|) computed on
(a) the full frame and (b) the held-out H = frame positions not in the
Phase 1 F1 AE or W frames (rho recomputed on H rows only, for A222V and
every background; H re-derived from task82_ae_raw.csv /
task69_w2_bg_raw.csv position sets exactly as script 122 did).

BOOTSTRAP IMPLEMENTATION (PIN-9 resolved): the NAIVE loop --
scipy.stats.spearmanr on explicit resampled row indices, identical
machinery to script 121's seed+0 loop.  PIN-9's weighted mid-rank
acceleration is deliberately NOT used (the pin's default: "otherwise
use the naive loop"); no weighted-rank gate is therefore needed.
Estimated full-run cost is printed from the measured per-draw timing.
NaN draws (constant vector in any recomputed rho) are dropped and
counted (121's convention).

PRE-REGISTERED RNG STREAMS (PIN-10, printed with every run):
  SEED+0 primary full-frame position-cluster draws (serve rho CIs,
          D_site CI and T CI -- one shared loop, 121's precedent);
  SEED+1 primary H position-cluster draws;
  SEED+2 D_site label permutation;
  SEED+3 secondary (region-demeaned) full-frame draws;
  SEED+4 secondary H draws.

DECISION (frozen section 5), printed verbatim with both p_spec values:
  GENERIC                              iff p_spec(full) > 0.10
  A222V BEATS NON-SITE BACKGROUNDS     iff p_spec(full) <= 0.05 AND
                                        p_spec(H) <= 0.10
  INDETERMINATE                        otherwise.
  Wording rule printed: only the second outcome may be written up as
  supporting background-specificity; GENERIC and INDETERMINATE get
  equal prominence.

REPORTED IRRESPECTIVE OF THE OUTCOME (frozen section 5):
  D_site = mean rho_b(Arm S) - mean rho_b(N), position-cluster
    bootstrap 95% CI (from the SEED+0 draws) and a label-permutation p
    with 10,000 shuffles (N_PERM env; smoke 300).  AMBIGUITY RESOLVED
    AND LOGGED: frozen section 5 states the shuffle count but not the
    sidedness; the most literal conservative reading is used --
    TWO-SIDED on |D|, following Phase 1b script 121's exact precedent
    for the same contrast ("two-sided p = (1 + #{|D_perm| >= |D_obs|}) /
    (1 + N_PERM)").  The labels are shuffled over the arm backgrounds
    with n(S) kept fixed (18), A222V excluded from the shuffle (it is
    neither S nor N).
  T = Spearman(rho_b, Grantham(X, V)) over Arm S (Grantham from
    scripts/lib.features.grantham, the source P1's Grantham gate
    passed), position-cluster bootstrap 95% CI, leave-one-out range
    (point rhos, 18 fits), minimum detectable |T| approx 2.8 x
    bootstrap SE; SUPPORTED iff CI lower bound > 0 AND T > 0 in every
    leave-one-out fit; REVERSED iff CI upper bound < 0; otherwise NOT
    RESOLVED, reported as "n = 18 cannot resolve this," never as
    "flat".  NO label permutation for T: frozen section 5 includes
    none (Phase 1b's exploratory T permutation is not part of this
    pre-registration).

SECONDARY (frozen section 6, non-decision): the same quantities after
residualizing delta_b and own_e_b on region indicators (PIN-8 regions:
R1 2-147, R2 148-294, R3 295-474, R4 475-656; cross-checked against
task32's own region column in this script's output).  IMPLEMENTATION
CHOICE (printed): residualization = subtracting the region mean
computed over the SAME rows used for that rho_b (within-region
demeaning, the Frisch-Waugh equivalent for indicators).  Secondary
p_spec/D_site/T are printed explicitly labelled NON-DECISION.  Per-arm
summary tables (n, mean, median, range) for every arm, primary and
secondary, full frame and H.

GATES (frozen section 7; failure -> "GATE FAIL: ..." + exit 1; no
loosening, no retry):
  G-A  A222V's rho over the full frame reproduces -0.088118 to 1e-6.
  G-C  no row with target position equal to background position enters
       any rho_b (asserted on every background's analysis rows).
  G-D  bootstrap identity: every cluster exactly once reproduces the
       point estimate to 1e-12 (checked before any random draw).
  G-E  each background scores >= 95% of the frame's positions
       (654 x 0.95 = 621.3 -> >= 622 positions; gated in --mode
       phase2; in --mode cached-ae the analogue (all 120 grid
       positions per cached background) is printed and gated too).
  INPUT gates (121's G-121.x style, implementation sanity only):
       roster 96 unique bg_ids; cached-ae: task109_placebo_rhos.csv
       point-rho identity < 1e-9, paired frame (identical row sets,
       printed vs Phase 1's 1932); own_e_b from task32_analysis_table
       must equal own_context_metrics' own_e_b on every frame row (the
       two modes must share one y-vector -- AGENTS 5); PIN-8 regions
       must equal task32's region column on every row; grantham
       importable and finite; task32 frame 10,757 rows / 654
       positions; H = 455 positions / 7,526 rows (script 122's
       recorded values).
  VALIDATION targets (--mode cached-ae, gated to 1e-9; these reproduce
       Phase 1b P4's V-group and P2's D on deterministic quantities):
       n(V) = 38; mean rho_b(V) = -0.010138068;
       p_spec = 0.025641026 (0 of 38 at or below A222V's
       -0.104321773 on this frame); D = -0.045070706 (n=18 vs 38).

DISCLOSURE (frozen section 9, printed): the AE1/AE2 split that
motivates this test was observed in Phase 1 AFTER F1 was run
(POST-HOC); confirmatory weight rests on this frozen rule and on H.

Usage:
  N_BOOT=300   N_PERM=300  venv/bin/python3 scripts/125_phase2_analysis.py --mode cached-ae  # validation smoke
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/125_phase2_analysis.py --mode cached-ae  # validation full
  N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/125_phase2_analysis.py --mode phase2    # SESSION 2b only

LIMITATIONS (AGENTS 6, printed with the output): own_e_b is the same
measured vector for every background, so the rho_b are mutually
correlated (shared y); the position-cluster bootstrap resamples
positions and recomputes rhos from raw scores, which propagates that
structure.  p_spec is bounded below by 1/(1+|N|) and is an empirical
rank count, not a tail model.  Cached-ae reproduces Phase 1b numbers
(REPRODUCTION IS NOT REPLICATION, AGENTS 6).  Secondary analyses are
non-decision by frozen section 6.
"""

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))       # project convention (scripts 82/110/...)

ANCHOR = -0.088118                  # frozen G-A target, tolerance 1e-6
GRID_A222V = -0.104321773           # cached-ae validation threshold (execution doc)
VAL_MEAN_V = -0.010138068
VAL_P_SPEC = 0.025641026
VAL_D = -0.045070706
PIN8 = [(2, 147, 1), (148, 294, 2), (295, 474, 3), (475, 656, 4)]

t0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def pin8_region(p):
    for lo, hi, r in PIN8:
        if lo <= p <= hi:
            return r
    return None


def pct(a):
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return (float("nan"), float("nan"), 0)
    lo, hi = np.percentile(a, [2.5, 97.5])
    return float(lo), float(hi), len(a)


def outcome_word(p_full, p_h):
    """Frozen section 5, verbatim logic."""
    if p_full > 0.10:
        return "GENERIC"
    if p_full <= 0.05 and p_h <= 0.10:
        return "A222V BEATS NON-SITE BACKGROUNDS"
    return "INDETERMINATE"


def build_frame():
    """The 10,757-row usable frame (PIN-7) + anchors, both modes."""
    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    frame = atlas.dropna(subset=["delta_esm", "own_e_b"]).copy()
    if len(frame) != 10757 or frame.position.nunique() != 654:
        gfail(f"frame rows={len(frame)} positions="
              f"{frame.position.nunique()} (expect 10757/654)")
    # own_e_b must be ONE y-vector across the two sources (AGENTS 5)
    own = pd.read_csv(ROOT / "data/processed/own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    m = frame[["hgvs_pro", "own_e_b"]].merge(own, on="hgvs_pro",
                                             how="left",
                                             suffixes=("_t32", "_own"))
    bad = int((m.own_e_b_t32 != m.own_e_b_own).sum())
    print(f"  own_e_b cross-check: task32 vs own_context_metrics over "
          f"{len(m)} frame rows: mismatches = {bad} (expect 0)")
    if bad:
        gfail(f"own_e_b source disagreement on {bad} rows")
    # PIN-8 vs task32 region
    pin = frame.position.map(pin8_region)
    bad_r = int((pin.astype(float) != frame.region).sum())
    print(f"  PIN-8 regions vs task32 region column: mismatches = "
          f"{bad_r}/{len(frame)} (expect 0)")
    if bad_r or pin.isna().any():
        gfail(f"PIN-8/region mismatch rows={bad_r}")
    return frame


def holdout(frame):
    """H = frame positions not in the F1 AE or W frames (script 122)."""
    ae = pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv",
                     usecols=["position"])
    w = pd.read_csv(ROOT / "data/processed/task69_w2_bg_raw.csv",
                    usecols=["position"])
    fset = set(frame.position.unique())
    H = sorted(fset - (set(ae.position.unique())
                       | set(w.position.unique())))
    n_h = int(frame.position.isin(H).sum())
    print(f"  H: {len(H)} positions, {n_h} frame rows (script 122 "
          f"recorded 455 / 7526)")
    if len(H) != 455 or n_h != 7526:
        gfail(f"H = {len(H)} positions / {n_h} rows (expect 455/7526)")
    return H


class Analysis:
    """One mode's rho machinery: per-background arrays + shared
    position-cluster draws (naive spearmanr loop, script 121 style)."""

    def __init__(self, mode):
        self.mode = mode
        self.frame = build_frame()
        self.Hset = set(holdout(self.frame))
        self.clusters_full = None   # set by the mode builder (see PIN-9 note:
        # the cluster list must be the positions ACTUALLY PRESENT in the
        # analysis rows -- cached-ae analyses the 120-position grid, so
        # drawing over all 654 frame positions would inject empty clusters
        # and distort the bootstrap; this was fixed before the first run)
        # per-bg: dict(bg_id -> DataFrame of analysis rows) and metadata
        self.bg_rows = {}
        self.arm = {}
        self.own_pos = {}
        self.a222v_rows = self.frame[["position", "delta_esm",
                                      "own_e_b", "region"]].rename(
            columns={"delta_esm": "delta"})
        self.drop_own = 0
        self.unexpected_missing = {}

    # ------------------------------------------------------------ build --
    def add_bg(self, bg_id, arm, own, rows, unexpected=0):
        self.bg_rows[bg_id] = rows
        self.arm[bg_id] = arm
        self.own_pos[bg_id] = own
        self.unexpected_missing[bg_id] = unexpected

    def finalize(self):
        self.bgs = sorted(self.bg_rows)
        self.S_IDS = sorted(b for b in self.bgs if self.arm[b] == "S")
        self.V_IDS = sorted(b for b in self.bgs if self.arm[b] == "V")
        self.G_IDS = sorted(b for b in self.bgs if self.arm[b] == "G")
        self.N_IDS = sorted(self.V_IDS + self.G_IDS)
        print(f"  arms: S={len(self.S_IDS)} V={len(self.V_IDS)} "
              f"G={len(self.G_IDS)} -> N (null set) = {len(self.N_IDS)}; "
              f"A222V is neither S nor N (frozen section 3)")
        # G-C: no target==background rows anywhere
        worst = 0
        for b in self.bgs:
            r = self.bg_rows[b]
            n = int((r.position == self.own_pos[b]).sum())
            worst = max(worst, n)
        if worst:
            gfail(f"G-C: {worst} own-position rows present in rho inputs")
        print("  G-C PASS: 0 rows with target position == background "
              "position in any rho_b input "
              f"(own-position rows pre-dropped: {self.drop_own})")

    # ----------------------------------------------------------- rhos ----
    def point_rhos(self):
        """Point rho_b per background + A222V on its own rows."""
        self.point = {}
        for b in self.bgs:
            r = self.bg_rows[b]
            self.point[b] = float(spearmanr(r.delta.to_numpy(float),
                                            r.own_e_b.to_numpy(float)
                                            ).statistic)
        a = self.a222v_rows
        self.rho_a222v = float(spearmanr(a.delta.to_numpy(float),
                                         a.own_e_b.to_numpy(float)
                                         ).statistic)
        return self.point

    def gate_identity(self):
        """G-D: every cluster once reproduces the point estimate."""
        idmax = 0.0
        for b in self.bgs:
            r = self.bg_rows[b]
            codes, uniq = pd.factorize(r.position, sort=True)
            idx = np.concatenate([np.flatnonzero(codes == i)
                                  for i in range(len(uniq))])
            v = float(spearmanr(r.delta.to_numpy(float)[idx],
                                r.own_e_b.to_numpy(float)[idx]
                                ).statistic)
            idmax = max(idmax, abs(v - self.point[b]))
        a = self.a222v_rows
        codes, uniq = pd.factorize(a.position, sort=True)
        idx = np.concatenate([np.flatnonzero(codes == i)
                              for i in range(len(uniq))])
        va = float(spearmanr(a.delta.to_numpy(float)[idx],
                             a.own_e_b.to_numpy(float)[idx]).statistic)
        idmax = max(idmax, abs(va - self.rho_a222v))
        print(f"  G-D: identity draw (every cluster once) vs point "
              f"rho: max|diff| = {idmax:.3e} (gate < 1e-12)")
        if idmax >= 1e-12:
            gfail(f"G-D max|diff| = {idmax}")
        print("  G-D PASS")

    def bootstrap(self, positions, n_boot, rng, label):
        """Naive position-cluster loop over `positions` (PIN-9 default).
        Returns (draws array n_boot x n_bgs, seconds)."""
        positions = list(positions)
        k = len(positions)
        # per-bg row indices per cluster position (missing -> empty)
        cl = []
        for b in self.bgs:
            r = self.bg_rows[b]
            byp = {p: np.flatnonzero(r.position.to_numpy() == p)
                   for p in positions}
            cl.append(byp)
        a_by_p = {p: np.flatnonzero(self.a222v_rows.position.to_numpy()
                                    == p) for p in positions}
        X = {b: self.bg_rows[b].delta.to_numpy(float) for b in self.bgs}
        Y = {b: self.bg_rows[b].own_e_b.to_numpy(float) for b in self.bgs}
        Xa = self.a222v_rows.delta.to_numpy(float)
        Ya = self.a222v_rows.own_e_b.to_numpy(float)
        draws = np.empty((n_boot, len(self.bgs) + 1))
        t_b = time.time()
        for i in range(n_boot):
            d = rng.integers(0, k, k)
            aidx = np.concatenate([a_by_p[positions[j]] for j in d])
            draws[i, len(self.bgs)] = spearmanr(Xa[aidx], Ya[aidx]
                                                ).statistic
            for j, b in enumerate(self.bgs):
                gidx = np.concatenate([cl[j][positions[q]] for q in d])
                draws[i, j] = spearmanr(X[b][gidx], Y[b][gidx]).statistic
            if (i + 1) % max(1, n_boot // 5) == 0:
                print(f"    [{label}] {i + 1}/{n_boot} draws, "
                      f"{time.time() - t_b:.0f}s", flush=True)
        secs = time.time() - t_b
        n_nan = int(np.isnan(draws).any(axis=1).sum())
        print(f"    [{label}] {n_boot} draws x {len(self.bgs)}+A222V "
              f"rho in {secs:.1f}s ({secs / n_boot * 1000:.1f} ms/draw); "
              f"draws with any NaN = {n_nan} (dropped from CIs)")
        return draws, secs

    # ------------------------------------------------- derived blocks ----
    def p_spec(self, ids, rho_a222v, rhos):
        k = int((rhos <= rho_a222v).sum())
        p = (1 + k) / (1 + len(ids))
        return k, p

    def arm_table(self, title, rhos_by_arm, rho_a222v):
        print(f"  {title}")
        for arm in ["S", "V", "G"]:
            ids = getattr(self, f"{arm}_IDS")
            if not ids:
                continue
            v = np.array([rhos_by_arm[b] for b in ids])
            print(f"    arm {arm}: n={len(v)} mean={v.mean():+.9f} "
                  f"median={np.median(v):+.9f} "
                  f"range=[{v.min():+.9f}, {v.max():+.9f}]")
        allv = np.array([rhos_by_arm[b] for b in self.N_IDS])
        print(f"    null set N (V u G): n={len(allv)} "
              f"mean={allv.mean():+.9f} "
              f"median={np.median(allv):+.9f} "
              f"range=[{allv.min():+.9f}, {allv.max():+.9f}]")
        r = np.array([rhos_by_arm[b] for b in self.N_IDS])
        rank = int((r < rho_a222v).sum() + 1)
        print(f"    A222V rho = {rho_a222v:+.9f}; signed rank within "
              f"N u {{A222V}} = {rank}/{len(r) + 1} (rank 1 = most "
              f"negative; reported, not tested)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True,
                    choices=["phase2", "cached-ae"])
    args = ap.parse_args()

    banner(f"PHASE 2 pre-registered analysis (script 125)  mode="
           f"{args.mode}  N_BOOT={N_BOOT} N_PERM={N_PERM} SEED={SEED}")
    print("PRE-REGISTERED: frozen PHASE2_PREREG.md sections 2/4/5/6/7 "
          "(quoted in this script's docstring); this run's mode "
          f"'{args.mode}' selected BEFORE any output was seen.")
    print("DISCLOSURE (frozen section 9): the AE1/AE2 split that "
          "motivates this test was observed in Phase 1 after F1 was run "
          "(POST-HOC); confirmatory weight rests on this frozen rule "
          "and on H.")
    print(f"PIN-10 rng streams: SEED+0 primary full-frame draws; "
          f"SEED+1 primary H draws; SEED+2 D_site permutation; "
          f"SEED+3 secondary full-frame; SEED+4 secondary H "
          f"(SEED={SEED}).")
    print("PIN-9: NAIVE spearmanr loop on explicit resampled indices "
          "(the pin's default); weighted mid-rank acceleration NOT "
          "used.")

    A = Analysis(args.mode)
    frame = A.frame

    # ------------------------------------------------- G-A (both modes) --
    print("\n[G-A] A222V's full-frame rho vs the frozen anchor")
    rho_a_full = float(spearmanr(frame.delta_esm.to_numpy(float),
                                 frame.own_e_b.to_numpy(float)).statistic)
    d_a = abs(rho_a_full - ANCHOR)
    print(f"  rho = {rho_a_full!r}; target {ANCHOR} |diff| = "
          f"{d_a:.3e} (gate < 1e-6)")
    if d_a >= 1e-6:
        gfail(f"G-A |diff| = {d_a}")
    print("  G-A PASS")

    if args.mode == "cached-ae":
        build_cache_ae(A)
    else:
        build_phase2(A)

    A.finalize()
    A.point_rhos()

    print("\n[point rho_b] full analysis set (all backgrounds)")
    for b in A.bgs:
        print(f"  {b:>10s} arm={A.arm[b]}  rho={A.point[b]:+.9f}")
    print(f"  __A222V__  rho={A.rho_a222v:+.9f} "
          f"({'full frame' if args.mode == 'phase2' else 'AE grid rows'})")

    A.gate_identity()

    # ----------------------------------------------------------- G-E ----
    print("\n[G-E] background position coverage")
    covs = []
    for b in A.bgs:
        r = A.bg_rows[b]
        covs.append(r.position.nunique())
    denom = 654 if args.mode == "phase2" else 120
    lo = min(covs)
    need = 0.95 * denom
    print(f"  min positions covered by any background = {lo} "
          f"(denominator {denom}; gate >= {need:.1f})")
    if lo < need:
        gfail(f"G-E min coverage {lo}/{denom}")
    print("  G-E PASS")

    # cached-ae: gate the deterministic validation targets EARLY (fail fast;
    # execution doc G3: any miss -> GATE FAIL + exit 1, no retry)
    if args.mode == "cached-ae":
        pass_validations(A)

    # -------------------------------------------------- primary bootstrap
    banner("PRIMARY ANALYSIS (frozen sections 2 + 4)", "-")
    positions_full = list(A.clusters_full)
    rng0 = np.random.default_rng(SEED + 0)
    draws0, secs0 = A.bootstrap(positions_full, N_BOOT, rng0,
                                "SEED+0 full frame")
    id_full = {b: j for j, b in enumerate(A.bgs)}

    # per-rho CIs
    ci_lo, ci_hi = {}, {}
    for b in A.bgs:
        col = draws0[:, id_full[b]]
        lo_, hi_, nv = pct(col)
        ci_lo[b], ci_hi[b] = lo_, hi_

    # A222V threshold on the SAME rows as the compared rho_b
    rho_thr = A.rho_a222v
    k_full, p_full = A.p_spec(A.N_IDS, rho_thr,
                              np.array([A.point[b] for b in A.N_IDS]))
    pset = ("FULL FRAME" if args.mode == "phase2"
            else "ANALYSIS SET (AE grid rows)")
    print(f"\n  p_spec({pset}): threshold = A222V's rho on the same "
          f"rows = {rho_thr:+.9f}")
    print(f"    #{{b in N : rho_b <= rho_A222V}} = {k_full} of "
          f"|N| = {len(A.N_IDS)}")
    print(f"    p_spec(full) = (1 + {k_full}) / (1 + {len(A.N_IDS)}) "
          f"= {p_full:.9f}")

    # -------------------------------------------------------------- H ----
    p_h = None
    if args.mode == "phase2":
        positions_H = sorted(A.Hset)
        rng1 = np.random.default_rng(SEED + 1)
        draws1, secs1 = A.bootstrap(positions_H, N_BOOT, rng1,
                                    "SEED+1 H")
        # H-row rhos
        point_h = {}
        for b in A.bgs:
            r = A.bg_rows[b]
            rh = r[r.position.isin(A.Hset)]
            point_h[b] = float(spearmanr(rh.delta.to_numpy(float),
                                         rh.own_e_b.to_numpy(float)
                                         ).statistic)
        ah = A.a222v_rows[A.a222v_rows.position.isin(A.Hset)]
        rho_h_a = float(spearmanr(ah.delta.to_numpy(float),
                                  ah.own_e_b.to_numpy(float)).statistic)
        k_h, p_h = A.p_spec(A.N_IDS, rho_h_a,
                            np.array([point_h[b] for b in A.N_IDS]))
        print(f"\n  p_spec(HELD-OUT H): threshold = A222V's rho on H "
              f"rows = {rho_h_a:+.9f}")
        print(f"    #{{b in N : rho_b <= rho_A222V}} = {k_h} of "
          f"|N| = {len(A.N_IDS)}")
        print(f"    p_spec(H) = (1 + {k_h}) / (1 + {len(A.N_IDS)}) "
              f"= {p_h:.9f}")
        print("\n  per-background rho on H (frozen section 4b):")
        for b in A.bgs:
            lo_, hi_, nv = pct(draws1[:, id_full[b]])
            print(f"    {b:>10s} arm={A.arm[b]}  rho_H={point_h[b]:+.9f} "
                  f"CI=[{lo_:+.6f}, {hi_:+.6f}]")
        A.point_h = point_h
    else:
        print("\n  p_spec(H): NOT COMPUTED in --mode cached-ae (H "
              "excludes the AE frame by construction -> 0 grid rows in "
              "H); the frozen section 5 outcome word requires "
              "p_spec(H) and N = V u G and is therefore computed only "
              "in --mode phase2.")

    # ---------------------------------------------------- outcome word ---
    banner("FROZEN SECTION 5 DECISION RULE", "-")
    print('  GENERIC iff p_spec(full) > 0.10;  "A222V BEATS NON-SITE '
          'BACKGROUNDS" iff p_spec(full) <= 0.05 AND p_spec(H) <= 0.10; '
          'INDETERMINATE otherwise.')
    print('  Wording rule: only "A222V BEATS NON-SITE BACKGROUNDS" may '
          'be written up as supporting background-specificity; GENERIC '
          'and INDETERMINATE get equal prominence.')
    if args.mode == "phase2":
        word = outcome_word(p_full, p_h)
        print(f"  OUTCOME WORD: {word}  (p_spec(full)={p_full:.9f}, "
              f"p_spec(H)={p_h:.9f})")
    else:
        print("  OUTCOME WORD: not computed (validation mode -- see "
              "above). This run is NOT the pre-registered result.")

    # ----------------------------------------------------------- D_site --
    banner("D_site (frozen section 5, reported irrespective)", "-")
    rS = np.array([A.point[b] for b in A.S_IDS])
    rN = np.array([A.point[b] for b in A.N_IDS])
    D_obs = float(rS.mean() - rN.mean())
    print(f"  mean rho_b(S, n={len(rS)}) = {rS.mean():+.9f}; "
          f"mean rho_b(N, n={len(rN)}) = {rN.mean():+.9f}")
    print(f"  D_site = mean(S) - mean(N) = {D_obs:+.9f}")
    jS = [id_full[b] for b in A.S_IDS]
    jN = [id_full[b] for b in A.N_IDS]
    d_draws = draws0[:, jS].mean(axis=1) - draws0[:, jN].mean(axis=1)
    lo_d, hi_d, nv_d = pct(d_draws)
    print(f"  position-cluster bootstrap 95% CI (SEED+0, {N_BOOT} "
          f"draws) = [{lo_d:+.9f}, {hi_d:+.9f}] (valid {nv_d})")
    rng2 = np.random.default_rng(SEED + 2)
    allrho = np.array([A.point[b] for b in A.bgs])
    ge = 0
    for _ in range(N_PERM):
        perm = rng2.permutation(len(A.bgs))
        lab = np.zeros(len(A.bgs), dtype=bool)
        lab[perm[:len(A.S_IDS)]] = True
        dp = float(allrho[lab].mean() - allrho[~lab].mean())
        if abs(dp) >= abs(D_obs):
            ge += 1
    p_perm = (1 + ge) / (1 + N_PERM)
    print(f"  label permutation ({N_PERM} shuffles over "
          f"{len(A.bgs)} arm backgrounds, n(S)=18 kept fixed, TWO-SIDED "
          f"on |D| per script 121's precedent -- sidedness not stated in "
          f"frozen section 5, logged as an ambiguity resolution, SEED+2): "
          f"p = (1 + {ge}) / (1 + {N_PERM}) = {p_perm:.6f}")
    print("  Interpretation (frozen): D_site < 0 means a shared site "
          "tracks A222V's e.b beyond arbitrary backgrounds; that is "
          "compatible with a real site-specific effect and is not "
          "evidence of substitution-specificity.")

    # --------------------------------------------------------------- T ---
    banner("WITHIN-SITE GRANTHAM GRADIENT T (frozen section 5)", "-")
    try:
        from scripts.lib.features import grantham
    except Exception as e:
        gfail(f"grantham import failed: {e!r}")
    xs = [b.split("_")[1] for b in A.S_IDS]
    d_b = np.array([float(grantham(x, "V")) for x in xs])
    if not np.all(np.isfinite(d_b)):
        gfail(f"non-finite Grantham distances: {d_b}")
    print(f"  d_b = Grantham(X, V) via scripts.lib.features.grantham "
          f"(P1's Grantham gate source); 18 finite values, range "
          f"[{d_b.min():.1f}, {d_b.max():.1f}]")
    T_obs = float(spearmanr(rS, d_b).statistic)
    print(f"  T = Spearman(rho_b, d_b) over Arm S (n={len(rS)}) = "
          f"{T_obs:+.9f}")
    T_draws = np.array([spearmanr(draws0[i, jS], d_b).statistic
                        for i in range(N_BOOT)])
    g_lo, g_hi, nv_g = pct(T_draws)
    se_T = float(np.nanstd(T_draws, ddof=1))
    print(f"  bootstrap T 95% CI (SEED+0) = [{g_lo:+.9f}, "
          f"{g_hi:+.9f}] (valid {nv_g}/{N_BOOT})")
    print(f"  bootstrap SE(T) = {se_T:.9f} -> minimum detectable |T| "
          f"approx 2.8 x SE = {2.8 * se_T:.9f}")
    loo = []
    for i in range(len(rS)):
        m = np.arange(len(rS)) != i
        loo.append(float(spearmanr(rS[m], d_b[m]).statistic))
    loo = np.array(loo)
    print(f"  leave-one-out range = [{loo.min():+.9f}, "
          f"{loo.max():+.9f}] (T > 0 in {int((loo > 0).sum())}/{len(loo)})")
    if g_lo > 0 and np.all(loo > 0):
        t_word = "SUPPORTED"
    elif g_hi < 0:
        t_word = "REVERSED"
    else:
        t_word = "NOT RESOLVED"
    print(f"  T RULE: CI lower > 0 ({g_lo > 0}) AND T > 0 in all "
          f"leave-one-out fits ({bool(np.all(loo > 0))}); CI upper < 0 "
          f"({g_hi < 0}) -> {t_word}")
    if t_word == "NOT RESOLVED":
        print('  REQUIRED WORDING for NOT RESOLVED: "n = 18 cannot '
              'resolve this," never "flat" / "the gradient is flat".')
    # NO T permutation: frozen section 5 includes none (stated in docstring)

    # ------------------------------------------------------ per-arm tabs -
    banner("PER-ARM SUMMARY TABLES (frozen section 6)", "-")
    A.arm_table("primary, full frame:", {b: A.point[b] for b in A.bgs},
                A.rho_a222v)
    if args.mode == "phase2" and hasattr(A, "point_h"):
        A.arm_table("primary, held-out H:", A.point_h, rho_h_a)
    print(f"  p_spec(full) = {p_full:.9f} ({k_full}/{len(A.N_IDS)} at "
          f"or below A222V)" +
          (f"; p_spec(H) = {p_h:.9f} ({k_h}/{len(A.N_IDS)})"
           if p_h is not None else "; p_spec(H) = n/a (validation mode)"))

    # --------------------------------------------------------- secondary -
    banner("SECONDARY: REGION-DEMEANED (frozen section 6; NON-DECISION)",
           "-")
    print("  residualization = within-region demeaning of delta_b and "
          "own_e_b over the SAME rows as each rho_b (implementation "
          "choice, printed); regions = PIN-8, gated above against "
          "task32.region.")
    sec_p_full = resid(A, draws_stream=SEED + 3, positions=positions_full,
                       label="SEED+3 secondary full frame")
    sec_p_h = None
    if args.mode == "phase2":
        sec_p_h = resid(A, draws_stream=SEED + 4,
                        positions=sorted(A.Hset), label="SEED+4 secondary H",
                        hview=True)
        print("  secondary outcome word WOULD BE (NON-DECISION; the "
              f"pre-registered decision uses primary p_spec only): "
              f"{outcome_word(sec_p_full, sec_p_h)}")
    else:
        print("  secondary outcome word: n/a (validation mode; the "
              "frozen section 5 word is computed only in --mode phase2)")

    # ----------------------------------------------------------- runtime -
    banner("RUNTIME / PROJECTION", "-")
    proj = secs0 / N_BOOT * 10000
    print(f"  measured: {secs0:.1f}s for {N_BOOT} primary full-frame "
          f"draws -> projection for N_BOOT=10000: {proj:.0f}s "
          f"({proj / 60:.1f} min) for this pass"
          + (f"; primary H pass measured {secs1:.1f}s"
             if args.mode == "phase2" else ""))
    print("  naive loop (PIN-9 default); session 2b runs the full "
          "N_BOOT=10000 phase2 mode DETACHED per frozen section 8.")

    banner("SCRIPT 125 SUMMARY", "-")
    print(f"  mode = {args.mode}; G-A PASS; G-C PASS; G-D PASS; "
          f"G-E PASS; input gates PASS")
    print(f"  p_spec(full) = {p_full:.9f}" +
          (f"; p_spec(H) = {p_h:.9f}" if p_h is not None
           else "; p_spec(H) = n/a (validation mode)"))
    print(f"  D_site = {D_obs:+.9f}, CI [{lo_d:+.9f}, {hi_d:+.9f}], "
          f"perm p = {p_perm:.6f}")
    print(f"  T = {T_obs:+.9f}, CI [{g_lo:+.9f}, {g_hi:+.9f}], LOO "
          f"[{loo.min():+.9f}, {loo.max():+.9f}], min detectable |T| "
          f"= {2.8 * se_T:.9f} -> {t_word}")
    print("\nLIMITATIONS (AGENTS 6): shared y (own_e_b) across "
          "backgrounds -> rho_b mutually correlated; position-cluster "
          "bootstrap recomputes rhos from raw scores and propagates "
          "this. p_spec is bounded below by 1/(1+|N|) -- an empirical "
          "rank count, not a tail model. Reproduction of Phase 1b "
          "numbers in cached-ae is REPRODUCTION, NOT REPLICATION. "
          "Secondary analyses are NON-DECISION (frozen section 6). "
          "cached-ae output must never be quoted as the pre-registered "
          "result.")
    print(f"Elapsed {time.time() - t0:.1f}s")


def build_cache_ae(A):
    """Line-for-line script 121 construction (validation mode)."""
    banner("MODE cached-ae -- validation on task82_ae_raw.csv "
           "(VALIDATION ONLY; not the pre-registered result)", "-")
    wt = pd.read_csv(ROOT / "data/processed/esm2_wt_scores.csv")
    ae_raw = pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv")
    own = pd.read_csv(ROOT / "data/processed/own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    rec = pd.read_csv(ROOT / "data/processed/task109_placebo_rhos.csv")
    aej = ae_raw.merge(wt[["position", "mut_aa", "hgvs_pro",
                          "esm2_score"]],
                       on=["position", "mut_aa"], how="left")
    if aej[["hgvs_pro", "esm2_score"]].isna().any().any():
        gfail("cached-ae: join produced nulls")
    aej["delta"] = aej.score_bg - aej.esm2_score

    parts = []
    for b in sorted(aej.bg_id.unique()):
        if b == "A222_V":
            continue
        sub = aej[aej.bg_id == b][["position", "hgvs_pro", "delta"]].copy()
        sub["bg_id"] = b
        parts.append(sub)
    av = aej[aej.bg_id == "A222_V"][["position", "hgvs_pro", "delta"]].copy()
    av["bg_id"] = "__A222V__"
    parts.append(av)
    lng = pd.concat(parts, ignore_index=True).merge(own, on="hgvs_pro",
                                                    how="left")
    lng = lng[lng.own_e_b.notna()].copy()
    # G6: drop rows at the background's own position (expected 0)
    keep = []
    for b in sorted(lng.bg_id.unique()):
        p = (222 if b.startswith("A222_") else
             int(b.split("_")[1]) if b.startswith("AV_") else None)
        sub = lng[lng.bg_id == b]
        if p is None:
            keep.append(sub)
            continue
        hit = sub.position == p
        A.drop_own += int(hit.sum())
        keep.append(sub[~hit])
    lng = pd.concat(keep, ignore_index=True)

    # pair with the frame's region column for the secondary analysis
    reg = A.frame[["position", "region"]].drop_duplicates()
    lng = lng.merge(reg, on="position", how="left")
    # cluster list for the bootstrap = positions PRESENT in these rows
    # (the 120-position grid; see the cluster note in Analysis.__init__)
    A.clusters_full = sorted(lng.position.unique())
    if len(A.clusters_full) != 120:
        gfail(f"cached-ae grid positions = {len(A.clusters_full)} "
              "(expect 120)")

    S_IDS = sorted(b for b in lng.bg_id.unique() if b.startswith("A222_"))
    V_IDS = sorted(b for b in lng.bg_id.unique() if b.startswith("AV_"))
    print(f"  S = {len(S_IDS)} (expect 18); V = {len(V_IDS)} "
          f"(expect 38); A222_V relabelled __A222V__ (never a placebo)")
    if len(S_IDS) != 18 or len(V_IDS) != 38:
        gfail(f"cached-ae group sizes S={len(S_IDS)} V={len(V_IDS)}")
    sets = {b: frozenset(zip(g.position, g.hgvs_pro))
            for b, g in lng.groupby("bg_id")}
    all_same = all(s == next(iter(sets.values())) for s in sets.values())
    n0 = len(next(iter(sets.values())))
    print(f"  paired frame: rows per background = {n0} "
          f"(Phase 1 recorded 1932); identical sets across "
          f"{len(sets)} backgrounds: {all_same}")
    if not all_same:
        gfail("cached-ae: backgrounds do not share identical row sets")

    # A222V's arm in this mode = its own cached delta on the grid rows
    a222 = lng[lng.bg_id == "__A222V__"][["position", "delta", "own_e_b",
                                          "region"]].copy()
    A.a222v_rows = a222

    for b in sorted(lng.bg_id.unique()):
        sub = lng[lng.bg_id == b]
        arm = ("S" if b.startswith("A222_") else
               "V" if b.startswith("AV_") else "ANCHOR")
        if arm == "ANCHOR":
            continue
        A.add_bg(b, arm, 222 if arm == "S" else int(b.split("_")[1]),
                 sub[["position", "delta", "own_e_b", "region"]].copy())

    # A222V's grid rho = the p_spec threshold for this mode
    A.rho_a222v = float(spearmanr(a222.delta.to_numpy(float),
                                  a222.own_e_b.to_numpy(float)).statistic)
    print(f"  A222V rho on this frame = {A.rho_a222v:+.9f} (execution "
          f"doc validation threshold {GRID_A222V})")
    d_thr = abs(A.rho_a222v - GRID_A222V)
    if d_thr >= 1e-9:
        gfail(f"validation threshold rho |diff| = {d_thr} (>= 1e-9)")
    print(f"  threshold gate: |diff| = {d_thr:.3e} < 1e-9 PASS")

    # task109 point-rho identity (121's G-121.2, mirrored)
    rec_ae = rec[rec.frame == "AE"].set_index("bg_id")
    dmax = 0.0
    for b in sorted(A.bg_rows):
        sub = A.bg_rows[b]
        r = float(spearmanr(sub.delta.to_numpy(float),
                            sub.own_e_b.to_numpy(float)).statistic)
        dmax = max(dmax, abs(r - float(rec_ae.loc[b, "rho"])))
    print(f"  point-rho identity vs task109_placebo_rhos.csv over "
          f"{len(A.bg_rows)} backgrounds: max|diff| = {dmax:.3e} "
          f"(gate < 1e-9)")
    if dmax >= 1e-9:
        gfail(f"task109 identity max|diff| = {dmax}")
    print("  input gate PASS")


def build_phase2(A):
    """The confirmatory build (NOT executed in session 2a)."""
    banner("MODE phase2 -- reads data/processed/phase2/ "
           "(SESSION 2b; no Phase 2 score exists during session 2a)",
           "-")
    roster = pd.read_csv(ROOT / "data/processed/phase2_arm_roster.csv")
    if len(roster) != 96 or roster.bg_id.nunique() != 96:
        gfail(f"roster {len(roster)}/{roster.bg_id.nunique()} "
              "(expect 96/96)")
    frame = A.frame
    A.clusters_full = sorted(frame.position.unique())   # 654 frame positions
    n_files = len(list((ROOT / "data/processed/phase2").glob("bg_*.csv")))
    print(f"  roster 96 backgrounds; bg_*.csv files found = {n_files} "
          f"(all 96 expected before session 2b)")
    missing = [b for b in roster.bg_id
               if not (ROOT / "data/processed/phase2"
                       / f"bg_{b}.csv").exists()]
    if missing:
        gfail(f"{len(missing)} roster backgrounds lack a score file "
              f"(first: {missing[:5]})")
    for r in roster.itertuples():
        f = pd.read_csv(ROOT / "data/processed/phase2"
                        / f"bg_{r.bg_id}.csv")
        m = frame.merge(f[["position", "mut_aa", "score"]],
                        on=["position", "mut_aa"], how="left")
        at_own = m.position == int(r.position)
        A.drop_own += int((at_own & m.score.isna()).sum())
        miss = int((m.score.isna() & ~at_own).sum())
        m = m[m.score.notna()].copy()
        m["delta"] = m.score - m.esm2_score
        if m[["delta", "own_e_b", "esm2_score"]].isna().any().any():
            gfail(f"{r.bg_id}: NaN in delta/own_e_b/esm2_score after "
                  "the score join")
        A.add_bg(r.bg_id, r.arm, int(r.position),
                 m[["position", "delta", "own_e_b", "region"]].copy(),
                 unexpected=miss)
    tot_unexp = sum(A.unexpected_missing.values())
    print(f"  rows outside own position without scores (coverage gaps) "
          f"= {tot_unexp} across all backgrounds "
          f"({'gated by G-E' if tot_unexp else 'none'})")
    # A222V's arm is cached (PIN-3): delta_esm on frame rows
    A.a222v_rows = frame[["position", "delta_esm", "own_e_b",
                          "region"]].rename(
        columns={"delta_esm": "delta"})


def resid(A, draws_stream, positions, label, hview=False):
    """Secondary: within-region demeaning, same machinery, NON-DECISION."""
    positions = list(positions)
    src_point = {}
    # build residualized rows in place of copies
    rows_res = {}
    for b in A.bgs:
        r = A.bg_rows[b]
        if hview:
            r = r[r.position.isin(A.Hset)]
        r = r.copy()
        r["delta"] = r.delta - r.groupby("region").delta.transform("mean")
        r["own_e_b"] = r.own_e_b - r.groupby("region").own_e_b.transform(
            "mean")
        rows_res[b] = r
        src_point[b] = float(spearmanr(r.delta.to_numpy(float),
                                       r.own_e_b.to_numpy(float)
                                       ).statistic)
    ar = A.a222v_rows
    if hview:
        ar = ar[ar.position.isin(A.Hset)]
    ar = ar.copy()
    ar["delta"] = ar.delta - ar.groupby("region").delta.transform("mean")
    ar["own_e_b"] = ar.own_e_b - ar.groupby("region").own_e_b.transform(
        "mean")
    rho_a = float(spearmanr(ar.delta.to_numpy(float),
                            ar.own_e_b.to_numpy(float)).statistic)

    # temporary swap into A for the shared bootstrap machinery
    saved_rows, saved_a222v = A.bg_rows, A.a222v_rows
    A.bg_rows, A.a222v_rows = rows_res, ar
    rng = np.random.default_rng(draws_stream)
    draws, secs = A.bootstrap(positions, N_BOOT, rng, label)
    A.bg_rows, A.a222v_rows = saved_rows, saved_a222v

    k, p = A.p_spec(A.N_IDS, rho_a,
                    np.array([src_point[b] for b in A.N_IDS]))
    jS = [A.bgs.index(b) for b in A.S_IDS]
    jN = [A.bgs.index(b) for b in A.N_IDS]
    d_draws = draws[:, jS].mean(axis=1) - draws[:, jN].mean(axis=1)
    lo_d, hi_d, nv = pct(d_draws)
    D_obs = float(np.mean([src_point[b] for b in A.S_IDS])
                  - np.mean([src_point[b] for b in A.N_IDS]))
    tag = "H" if hview else "full frame"
    print(f"  [{label}] on {tag} (NON-DECISION):")
    print(f"    secondary p_spec({tag}) = (1 + {k}) / (1 "
          f"+ {len(A.N_IDS)}) = {p:.9f}  (threshold A222V resid rho "
          f"= {rho_a:+.9f})")
    print(f"    secondary D_site = {D_obs:+.9f}, CI "
          f"[{lo_d:+.9f}, {hi_d:+.9f}] (valid {nv})")
    A.arm_table(f"secondary per-arm table ({tag}, region-demeaned, "
                f"NON-DECISION):", src_point, rho_a)
    return p


def pass_validations(A):
    banner("VALIDATION TARGETS (execution doc G3; deterministic "
           "quantities, gate 1e-9)", "-")
    rV = np.array([A.point[b] for b in A.V_IDS])
    rS = np.array([A.point[b] for b in A.S_IDS])
    n_v = len(rV)
    mean_v = float(rV.mean())
    D = float(rS.mean() - rV.mean())
    thr = A.rho_a222v
    k = int((rV <= thr).sum())
    p = (1 + k) / (1 + n_v)
    checks = [
        ("n(V) == 38", n_v == 38, float(n_v), 38.0, None),
        ("mean rho_b(V)", abs(mean_v - VAL_MEAN_V) < 1e-9,
         mean_v, VAL_MEAN_V, abs(mean_v - VAL_MEAN_V)),
        ("p_spec", abs(p - VAL_P_SPEC) < 1e-9, p, VAL_P_SPEC,
         abs(p - VAL_P_SPEC)),
        ("#(rho_b <= rho_A222V) == 0", k == 0, float(k), 0.0, None),
        ("D = mean(S) - mean(V)", abs(D - VAL_D) < 1e-9, D, VAL_D,
         abs(D - VAL_D)),
    ]
    ok = True
    for name, passed, got, want, diff in checks:
        if diff is None:
            print(f"  {name}: got {got} want {want} -> "
                  f"{'PASS' if passed else 'FAIL'}")
        else:
            print(f"  {name}: computed {got!r} vs target {want!r} "
                  f"|diff| = {diff:.3e} -> "
                  f"{'PASS' if passed else 'FAIL'} (gate < 1e-9)")
        ok &= passed
    if not ok:
        gfail("cached-ae validation target(s) not reproduced to 1e-9")
    print("  ALL VALIDATION TARGETS PASS (reproduction of Phase 1b "
          "P4/P2 deterministic quantities; REPRODUCTION IS NOT "
          "REPLICATION, AGENTS 6)")


if __name__ == "__main__":
    main()
