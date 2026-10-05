"""Script 174 (Phase 4 session 4a, Task A8d) -- Module L model-ladder
analysis: frozen MODEL_LADDER_PREREG_v1 section 2 (design) and section 3
(outcome words), with gates G-L0, G-L4 and G-L5.

PRE-REGISTERED: this docstring was written before the first run of this
script, when NO ladder score existed for 150M or 35M
(data/processed/phase4/ladder/{150M,35M} were empty), so the only model
column computable now is the cached 650M one.  Binding text:
MODEL_LADDER_PREREG_v1.md (sha256
eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3, 26 lines),
frozen sections 2, 3 and 4.  NO torch, esm or thermompnn is imported here
(planning rule 1): this is an analysis script and it reads only cached CSV
scores.

RESAMPLING UNITS (planning rule 7, printed at the top of every run):
  * INSIDE one background (rho_A222V, its partial): POSITION CLUSTERS over
    that background's own rows.
  * ACROSS backgrounds (the gradient, the shift confound, the across-model
    agreement of rho_b): BACKGROUNDS, each rho_b held fixed within a draw.
  Never rows.  Every bootstrap passes identity, a draw-by-draw comparison
  against a slow obvious reference on identical pre-drawn ids (1e-12), and the
  Phase 1 CI reproduction.

DECISIONS, pre-registered here before the first run (printed at startup):

LD-AN1 Inputs are sha-pinned: the ladder pre-registration, the D1 rho table,
        the stored 3D distance table, the 96-background roster, the cached
        WT-score file and the cached AV_220 rows.  Any mismatch -> exit 3.
LD-AN2 Frame = the 455 held-out positions H, minus each background's own
        position (frozen section 2).  Rows = the 7,526 H rows carrying both
        delta_esm and own_e.b; every background's statistic uses its own row
        subset and the analysis-set size is printed per background class.
LD-AN3 Per-model delta: delta_b = score_b - THAT model's own wild-type-arm
        score for the same (position, mut_aa).  For 650M both come from the
        Phase 2 caches (script 173's G-L2(b) showed the 650M wild-type arm
        reproduces esm2_wt_scores.csv to 1.776e-15); for 150M/35M from
        data/processed/phase4/ladder/<model>/{bg_*.csv, wt_H.csv}.  The
        wild-type arm is NEVER treated as a 98th background.
LD-AN4 ADDED cross-checks (stricter, never looser): the 650M rho_b computed
        here must equal the D1 table's rho_H for all 96 backgrounds (<1e-8)
        and A222V's must equal the frozen -0.090021683 (<1e-9); A222V's own
        position must not appear in its own rows.  These tie module L to the
        same inputs module N used, so a discrepancy would be caught here
        rather than read as biology.
LD-AN5 A model column is reported only if EVERY background passes the
        >=95%-of-eligible-H-positions coverage rule script 173 gates
        (G-L3(c)); an incomplete model prints its coverage table and is
        reported PENDING with no numbers -- never a partial column.
LD-AN6 Frozen section 2's five quantities per model, each with its own
        resampling unit: (i) rho_A222V on H with a position-cluster
        percentile CI; (ii) p_spec_H(neg) and p_spec_H(abs) against N = 78
        (arms V u G) through p3c.p_spec, the project's canonical form;
        (iii) the partial rho_H controlling THAT MODEL'S S_W with a
        position-cluster percentile CI (the frozen text names no CI for it;
        one is supplied and labelled as such); (iv) the gradient
        Spearman(rho_b, d3) over the 67 resolved nulls with a
        background-level percentile CI; (v) the shift confound
        Spearman(rho_b, mean|delta_b|) over the 96 backgrounds with a
        background-level percentile CI.  The word is p4c.word_ladder -- the
        frozen section 3 function -- called with the anchor CI and
        p_spec_H(neg).  All CIs of a given model column use N_BOOT draws
        (frozen production value 10,000 = --mode full).
LD-AN7 Cross-model agreement (frozen section 2's last clause), reported only
        when both columns exist: per background, the Spearman between that
        background's 650M delta vector and its own-model delta vector on the
        COMMON H rows, summarised as median and range over the backgrounds;
        and the Spearman ACROSS backgrounds between rho_b under 650M and
        rho_b under the smaller model.
LD-AN8 G-L4 planted tests on synthetic scores, all run through the SAME
        analysis core as the real data (never a parallel code path).  Plants
        are built on the real H rows and the real own_e.b with delta planted.
        Arms, seeds and pre-registered criteria:
        (A1) signal, default_rng(101): A222V's delta = -0.8*z(own_e.b) +
             0.4*noise, every other background's delta = pure noise at N_BOOT
             draws -> the word must be MODEL-REPLICATES (frozen section 3).
        (A2) gradient, default_rng(102): for the 67 resolved nulls
             delta_b = -(0.3 + 1.2*z(d3_b))*z(own_e.b) + 0.3*noise at a fixed
             10,000 draws -> the gradient CI must exclude zero in the
             NEGATIVE direction.
        (A3) shift confound, default_rng(103): a planted per-background
             magnitude s_b drives both |delta_b| and rho_b's sign, delta_b =
             -(0.3 + 1.2*s_b)*z(own_e.b) + 0.3*noise at a fixed 10,000 draws
             -> the confound CI must exclude zero (negative: bigger shift,
             more negative rho_b, the Phase 1 direction).
        (A4) null, default_rng(1000): delta independent of own_e.b for all
             backgrounds -> the word must be MODEL-DOES-NOT-REPLICATE in at
             least 85 of 100 draws, i.e. a fire rate <= 0.15 (the project's
             existing null-arm bound, A6 G-D2 precedent).  Each plant's CI
             uses a PINNED N_NULL_CI = 1,000 position-cluster draws so the
             fire rate does not move with N_BOOT; a 1,000-draw CI is wide
             enough to produce a word, and the arm is a mechanics check, not
             an estimate.  A4 evaluates only the anchor CI and p_spec (the
             gradient and confound are skipped in this arm for runtime; they
             are exercised by A2/A3).
        (A5) cross-model, default_rng(105)/default_rng(106): one plant whose
             two "models" share identical delta vectors (per-background and
             across-background agreement 1.0 to <1e-9) and one with
             independent vectors (both agreement statistics below 0.15).
        Seeds are pinned per arm and are NEVER re-seeked after seeing a result
        (AGENTS 0); a failure is a failure.
LD-AN9 G-L5 reference gate: (i) identity -- with ids = arange (every cluster,
        or every background, exactly once) each statistic equals its own point
        estimate to <1e-12; (ii) draw-by-draw -- the anchor's position-cluster
        draws equal p3c.reference_boot on identical pre-drawn ids to <1e-12
        over N_REF = 500 draws, this script's own cluster bootstrap (used for
        the partial) equals the imported corrected routine to <1e-12 on the
        same ids, and the gradient's background-level draws equal a slow
        pandas-rank rebuild to <1e-12; (iii) the Phase 1 CI
        [-0.1173334458953319, -0.05951138449511738] reproduces to <1e-9 per
        endpoint at a fixed 10,000 draws in BOTH modes (A6 G-DEC7 precedent),
        computed from the canonical cached construction (pdg's a222v_rows),
        NOT from this script's H-frame vectors.
LD-AN10 Modes: --mode smoke defaults N_BOOT to 300, --mode full to 10,000; the
        N_BOOT environment variable always wins.  Frozen section 2 pins
        production CIs at 10,000, so only a full-mode run's numbers and words
        are final; every smoke number is printed marked PROVISIONAL.  The
        planted arms A2/A3 and the Phase 1 gate are fixed at 10,000 in both
        modes.
LD-AN11 This script writes NO score file and never modifies the ladder
        directories; .tmp files are ignored exactly as script 173's
        completion rule ignores them.

LIMITATIONS (also printed at the end of every run):
  * A ladder word is about the SAME data (this protein, this 97-background
    roster) scored at other model sizes.  It is not an independent
    replication of the anchor's existence -- that is what module N tests.
  * The 650M column is not out-of-sample: its rows were scored in Phase 2 and
    already analysed.  Only the 150M and 35M columns are new data.
  * Deltas are per-model WT-referenced, so their scale differs between
    models; every frozen ladder statistic is a rank statistic so the scale
    difference does not enter them, but raw delta magnitudes must never be
    compared across models.
  * G-L4's arms are mechanics checks on synthetic scores: they show the
    analysis detects what it should detect, not that biology is present
    (AGENTS 6).
  * A CI that excludes zero is not by itself a finding; every quantity is
    printed with its magnitude and, for the planted arms, its null-planted
    counterpart.

Usage:
  venv/bin/python3 scripts/174_ladder_analysis.py --mode smoke
  venv/bin/python3 scripts/174_ladder_analysis.py --mode full
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

N_BOOT_ENV = os.environ.get("N_BOOT")
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase2_diag as pdg            # noqa: E402
from scripts.lib import phase3_common as p3c          # noqa: E402
from scripts.lib import phase4_common as p4c          # noqa: E402

PREREG = (ROOT / "docs/tasks/phase4-strengthening/prereg/"
          "MODEL_LADDER_PREREG_v1.md")
PREREG_SHA = "eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3"
D1 = ROOT / "data/processed/phase2_diagnostics/background_rho_table.csv"
D1_SHA = "e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796"
STORED3 = ROOT / "data/processed/phase2_diagnostics/background_3d_distance.csv"
STORED3_SHA = "69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de"
ROSTER96 = ROOT / "data/processed/phase2_arm_roster.csv"
ROSTER96_SHA = "9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b"
WT_CACHE = ROOT / "data/processed/esm2_wt_scores.csv"
WT_CACHE_SHA = "e4d3af3d444a0d0a35e71422e44fe3bfc3338ffa7df77e05552a8a0d6871581c"
AV220_CACHE = ROOT / "data/processed/phase2/bg_AV_220.csv"
AV220_SHA = "2dc13f8073aec0f0147819e038e7488e0306ae100f25b0afdb88539afb9f752e"
A222V_650 = ROOT / "data/processed/esm2_a222v_bg_scores.csv"
PHASE2 = ROOT / "data/processed/phase2"
LADDER = ROOT / "data/processed/phase4/ladder"

ANCHOR = "A222V"
T_A222V_H = -0.090021683
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.05951138449511738
COV_MIN = 0.95
N_NULL_CI = 1000
N_NULL_DRAWS = 100
NULL_FIRE_MAX = 0.15
N_REF = 500
P1_N = 10000
Z = None                      # z-scored own_e.b, set in main()

t0 = time.time()
gates = []


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def gate(name, val, detail=""):
    """True -> PASS, False -> FAIL, None -> PENDING."""
    if val is None:
        tag, stored = "PENDING", None
    else:
        stored = bool(val)
        tag = "PASS" if stored else "FAIL"
    gates.append((name, stored))
    print(f"  [{tag}] {name}" + (f": {detail}" if detail else ""), flush=True)


def cluster_rows(clusters):
    """Rows grouped by cluster in FIRST-APPEARANCE order -- the index space
    p3c.draw_ids draws in.  Returns a list of row-index arrays."""
    order, seen = [], {}
    for c in clusters:
        if c not in seen:
            seen[c] = len(order)
            order.append(c)
    rows = [[] for _ in order]
    for i, c in enumerate(clusters):
        rows[seen[c]].append(i)
    return [np.asarray(r, dtype=np.int64) for r in rows]


def cluster_boot_stat(x, y, controls, rows_by_cluster, ids, stat):
    """This script's own position-cluster bootstrap for an arbitrary
    statistic, driven by PRE-DRAWN ids.  Gated against the imported corrected
    routine in G-L5(ii-a2)."""
    out = np.empty(len(ids), dtype=float)
    for i, ix in enumerate(ids):
        sel = np.concatenate([rows_by_cluster[c] for c in ix])
        if stat == "spearman":
            out[i] = p3c.spearman(x[sel], y[sel])
        else:
            out[i] = p4c.partial_spearman(x[sel], y[sel],
                                          [c[sel] for c in controls])
    return out


def main():
    global Z
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    n_boot = int(N_BOOT_ENV) if N_BOOT_ENV else (300 if args.mode == "smoke"
                                                 else 10000)
    provisional = (args.mode == "smoke" or n_boot != 10000)
    tag_word = " [PROVISIONAL - smoke]" if provisional else ""

    banner("174 -- Module L model-ladder analysis (frozen section 2 + words)")
    print(f"  mode={args.mode} N_BOOT={n_boot} "
          f"(env N_BOOT={'set' if N_BOOT_ENV else 'unset'}) SEED={SEED}")
    print("  RESAMPLING UNITS: position clusters INSIDE one background; "
          "backgrounds ACROSS backgrounds (gradient, shift confound, "
          "across-model rho agreement).  Never rows.")
    print("  Frozen section 2 pins production CIs at 10,000 draws"
          + (f"; this run uses N_BOOT={n_boot} -> every number and word "
             "below is PROVISIONAL" if provisional else " -> production"))
    print("\nPRE-REGISTERED DECISIONS (full text in the docstring):")
    for k, v in [
        ("LD-AN1", "inputs sha-pinned; mismatch -> exit 3."),
        ("LD-AN2", "frame H (455) minus each background's own position; "
                   "7,526 H rows; per-background subsets printed."),
        ("LD-AN3", "delta_b = score_b - THAT model's own wild-type arm; the "
                   "WT arm is never a 98th background."),
        ("LD-AN4", "ADDED: 650M rho_b == D1 (96, <1e-8), A222V == frozen "
                   "-0.090021683 (<1e-9), own position absent."),
        ("LD-AN5", "a model column needs every background at >=95% coverage, "
                   "else PENDING with no numbers."),
        ("LD-AN6", "the five frozen quantities with their own resampling "
                   "units; word = p4c.word_ladder(anchor CI, p_spec_H(neg))."),
        ("LD-AN7", "cross-model agreement: per-background delta-vector "
                   "Spearman on common H rows (median + range) and the "
                   "across-background rho_b Spearman."),
        ("LD-AN8", "G-L4 arms A1-A5 through the SAME core; seeds 101/102/"
                   "103/1000/105+106 pinned; null arm fire rate <= 0.15 with "
                   "a pinned 1,000-draw CI."),
        ("LD-AN9", "G-L5 identity, draw-by-draw vs slow references (500 "
                   "draws) incl. this script's own cluster bootstrap, Phase "
                   "1 CI at fixed 10,000 from the canonical construction."),
        ("LD-AN10", "smoke -> PROVISIONAL; full -> final; a smoke gate "
                    "failure stops the run."),
        ("LD-AN11", "no score file written; ladder dirs read-only; .tmp "
                    "ignored."),
    ]:
        print(f"  {k}: {v}")

    # ------------------------------------------------------------- inputs --
    banner("G-L0 / INPUT PINS", "-")
    for nm, path, want in (("ladder prereg", PREREG, PREREG_SHA),
                           ("D1 rho table", D1, D1_SHA),
                           ("stored 3D distance", STORED3, STORED3_SHA),
                           ("96-background roster", ROSTER96, ROSTER96_SHA),
                           ("cached WT scores", WT_CACHE, WT_CACHE_SHA),
                           ("cached AV_220 rows", AV220_CACHE, AV220_SHA)):
        gate(f"G-L0 {nm} sha256", sha256(path) == want, sha256(path)[:16])

    # ------------------------------------------------- frame, rows, meta --
    spec = importlib.util.spec_from_file_location(
        "s125_phase2_analysis", str(ROOT / "scripts/125_phase2_analysis.py"))
    s125 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s125)
    H = sorted(int(p) for p in s125.holdout(s125.build_frame()))
    Hset = set(H)

    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    frame = atlas.dropna(subset=["delta_esm", "own_e_b"])
    h = frame[frame.position.isin(H)].reset_index(drop=True)
    own_eb = h.own_e_b.to_numpy(float)
    h_pos = h.position.to_numpy(int)
    h_keys = list(zip(h.position.to_numpy(int), h.mut_aa.to_numpy(str)))
    gate("LD-AN2 frame H = 455 positions / 7,526 rows",
         len(H) == 455 and len(h) == 7526, f"{len(H)} / {len(h)}")
    Z = (own_eb - own_eb.mean()) / own_eb.std()

    r96 = pd.read_csv(ROSTER96)
    own_of = {ANCHOR: 222}
    arm_of = {}
    for x in r96.itertuples():
        own_of[x.bg_id] = int(x.position)
        arm_of[x.bg_id] = x.arm
    nulls78 = [b for b in own_of if b != ANCHOR and arm_of[b] in ("V", "G")]
    gate("N = 78 null backgrounds (arms V u G)", len(nulls78) == 78,
         f"{len(nulls78)} of {len(own_of) - 1}; arms "
         f"{r96.arm.value_counts().to_dict()}")

    stored = pd.read_csv(STORED3)
    resolved = stored[stored.resolved & (stored.position != 222)]
    d3_of = dict(zip(resolved.bg_id.astype(str), resolved.d3_CA.to_numpy(float)))
    gate("67 resolved existing nulls carry a d3", len(d3_of) == 67,
         str(len(d3_of)))

    wt = pd.read_csv(WT_CACHE)
    wt650 = {(int(r.position), r.mut_aa): float(r.esm2_score)
             for r in wt.itertuples()}
    miss = [k for k in h_keys if k not in wt650]
    gate("every H row has a cached 650M wild-type score", not miss,
         f"{len(miss)} missing of {len(h_keys)}")

    bg_all = [ANCHOR] + [b for b in own_of if b != ANCHOR]

    def deltas_650m():
        out = {}
        for bg in bg_all:
            if bg == ANCHOR:
                df = pd.read_csv(A222V_650)
                sc = {(int(r.position), r.mut_aa):
                      float(r.esm2_score_a222v_bg) for r in df.itertuples()}
            else:
                df = pd.read_csv(PHASE2 / f"bg_{bg}.csv")
                sc = {(int(r.position), r.mut_aa): float(r.score)
                      for r in df.itertuples()}
            out[bg] = np.array([sc[k] - wt650[k] if k in sc else np.nan
                                for k in h_keys], dtype=float)
        return out

    def deltas_ladder(model):
        mdir = LADDER / model
        wt_path = mdir / "wt_H.csv"
        if not wt_path.exists():
            return None, None, f"no {model} wild-type arm (wt_H.csv absent)"
        wtdf = pd.read_csv(wt_path)
        wmap = {(int(r.position), r.mut_aa): float(r.score)
                for r in wtdf.itertuples()}
        out, short = {}, []
        for bg in bg_all:
            f = mdir / f"bg_{bg}.csv"
            if not f.exists():
                short.append(f"{bg} absent")
                continue
            df = pd.read_csv(f)
            got = len({int(p) for p in df.position.unique() if int(p) in Hset})
            exp = len([p for p in H if p != own_of[bg]])
            if got < COV_MIN * exp:
                short.append(f"{bg} {got}/{exp} positions")
                continue
            sc = {(int(r.position), r.mut_aa): float(r.delta)
                  for r in df.itertuples()}
            out[bg] = np.array([sc[k] if k in sc else np.nan
                                for k in h_keys], dtype=float)
        if short:
            return None, None, (f"{len(short)} background(s) below the "
                                f"{COV_MIN:.0%} coverage rule: "
                                + "; ".join(short[:4]))
        sw = np.array([wmap[k] for k in h_keys], dtype=float)
        return out, sw, None

    # ---------------------------------------------------------- the core --
    def analyse(deltas, sw, n_local, want_gradient=True):
        """Frozen section 2's quantities for ONE model-like column.  The real
        data and every planted arm go through this same function."""
        mask = {bg: np.isfinite(deltas[bg]) & (h_pos != own_of[bg])
                for bg in own_of}
        rhos = {bg: float(p3c.spearman(deltas[bg][mask[bg]],
                                       own_eb[mask[bg]])) for bg in own_of}
        rho_A = rhos[ANCHOR]
        mA = mask[ANCHOR]
        rbc = cluster_rows(h_pos[mA])
        ids, _labels = p3c.draw_ids(h_pos[mA], n_local, SEED)
        a_draws = cluster_boot_stat(deltas[ANCHOR][mA], own_eb[mA], [],
                                    rbc, ids, "spearman")
        ci_A = p3c.pct_ci(a_draws)
        p_neg, k_neg, n78 = p3c.p_spec(rho_A, [rhos[b] for b in nulls78],
                                       mode="neg")
        p_abs, k_abs, _ = p3c.p_spec(rho_A, [rhos[b] for b in nulls78],
                                     mode="abs")
        sw_m = sw[mA]
        pt = p4c.partial_spearman(deltas[ANCHOR][mA], own_eb[mA], [sw_m])
        pt_draws = cluster_boot_stat(deltas[ANCHOR][mA], own_eb[mA], [sw_m],
                                     rbc, ids, "partial")
        ci_pt = p3c.pct_ci(pt_draws)
        out = dict(rhos=rhos, mask=mask, rho_A=rho_A, ci_A=ci_A, ids=ids,
                   rbc=rbc, p_neg=p_neg, k_neg=k_neg, p_abs=p_abs, k_abs=k_abs,
                   n78=n78, partial=pt, ci_pt=ci_pt)
        if want_gradient:
            g67 = [b for b in nulls78 if b in d3_of]
            r67 = np.array([rhos[b] for b in g67])
            d367 = np.array([d3_of[b] for b in g67])
            grad = float(p3c.spearman(r67, d367))
            gd, _ = p3c.background_boot(r67, d367, n_boot=n_local, seed=SEED,
                                        stat=p3c.spearman)
            b96 = [b for b in own_of if b != ANCHOR]
            r96v = np.array([rhos[b] for b in b96])
            mag = np.array([np.nanmean(np.abs(deltas[b][mask[b]]))
                            for b in b96])
            conf = float(p3c.spearman(r96v, mag))
            cd, _ = p3c.background_boot(r96v, mag, n_boot=n_local, seed=SEED,
                                        stat=p3c.spearman)
            out.update(g67=g67, r67=r67, d367=d367, grad=grad,
                       ci_grad=p3c.pct_ci(gd), b96=b96, r96v=r96v, mag=mag,
                       conf=conf, ci_conf=p3c.pct_ci(cd))
        out["word"] = p4c.word_ladder(ci_A[0], ci_A[1], p_neg)
        return out

    def cross(d650_, dm_):
        """Frozen section 2's last clause: per-background delta-vector
        Spearman on common H rows, and rho_b across backgrounds."""
        per_bg, r650b, rmb = {}, [], []
        for bg in own_of:
            m = (np.isfinite(d650_[bg]) & np.isfinite(dm_[bg])
                 & (h_pos != own_of[bg]))
            if m.sum() < 3:
                continue
            per_bg[bg] = float(p3c.spearman(d650_[bg][m], dm_[bg][m]))
            r650b.append(float(p3c.spearman(d650_[bg][m], own_eb[m])))
            rmb.append(float(p3c.spearman(dm_[bg][m], own_eb[m])))
        vals = np.array(list(per_bg.values()))
        return dict(per_bg=per_bg, median=float(np.median(vals)),
                    lo=float(vals.min()), hi=float(vals.max()),
                    n=len(vals), across=float(p3c.spearman(r650b, rmb)))

    # --------------------------------------------------- LD-AN4 crosscheck --
    banner("LD-AN4 -- the 650M column against D1 and the frozen anchor", "-")
    d650 = deltas_650m()
    sw650 = np.array([wt650[k] for k in h_keys], dtype=float)
    r650 = {b: float(p3c.spearman(d650[b][np.isfinite(d650[b])
                                         & (h_pos != own_of[b])],
                                  own_eb[np.isfinite(d650[b])
                                         & (h_pos != own_of[b])]))
            for b in bg_all}
    d1 = pd.read_csv(D1).set_index("bg_id")
    diffs = [abs(r650[b] - float(d1.loc[b, "rho_H"])) for b in bg_all
             if b in d1.index]
    gate("LD-AN4 650M rho_H recomputed == D1 for all 96 backgrounds (<1e-8)",
         len(diffs) == 96 and max(diffs) < 1e-8,
         f"max|diff| = {max(diffs):.3e} over {len(diffs)}")
    gate("LD-AN4 A222V rho_H == the frozen -0.090021683 (<1e-9)",
         abs(r650[ANCHOR] - T_A222V_H) < 1e-9,
         f"got {r650[ANCHOR]!r} |diff| = {abs(r650[ANCHOR] - T_A222V_H):.3e}")
    gate("LD-AN4 A222V's own position 222 is absent from its own rows",
         not bool(np.isfinite(d650[ANCHOR])[h_pos == 222].any()),
         f"finite A222V rows at 222: "
         f"{int(np.isfinite(d650[ANCHOR])[h_pos == 222].sum())}")

    # ------------------------------------------------------ model columns --
    banner("MODEL COLUMNS (frozen section 2)", "-")
    gate("LD-AN5 650M column available", True,
         f"97 backgrounds from the Phase 2 caches + the cached WT arm; "
         f"{len(h)} H rows, own position excluded per background")
    cols = {"650M": (d650, sw650)}
    for model in ("150M", "35M"):
        dm, swm, why = deltas_ladder(model)
        if dm is None:
            gate(f"LD-AN5 {model} column available", None,
                 f"PENDING: {why} (night B scoring stage)")
            continue
        cols[model] = (dm, swm)
        gate(f"LD-AN5 {model} column available", True,
             f"97 backgrounds + wild-type arm, every background at "
             f">= {COV_MIN:.0%} coverage")

    results = {}
    for model, (dl, sw) in cols.items():
        print(f"\n--- model {model}, N_BOOT={n_boot}"
              + ("  [PROVISIONAL]" if provisional else "") + " ---")
        res = analyse(dl, sw, n_boot)
        results[model] = res
        nrows = [int(m.sum()) for m in res["mask"].values()]
        print(f"  analysis set: {int(res['mask'][ANCHOR].sum())} H rows for "
              f"{ANCHOR} (of {len(h)}; own position 222 excluded); per "
              f"background {min(nrows)}-{max(nrows)} rows")
        print(f"  (i)   rho_{ANCHOR} on H = {res['rho_A']:+.9f}  CI "
              f"[{res['ci_A'][0]:+.6f}, {res['ci_A'][1]:+.6f}] "
              f"({res['ci_A'][2]} finite draws, position clusters)")
        print(f"  (ii)  p_spec_H(neg) = {res['p_neg']:.6f} "
              f"({res['k_neg']}/{res['n78']});  p_spec_H(abs) = "
              f"{res['p_abs']:.6f} ({res['k_abs']}/{res['n78']})")
        print(f"  (iii) partial rho_H | this model's S_W = {res['partial']:+.6f}"
              f"  CI [{res['ci_pt'][0]:+.6f}, {res['ci_pt'][1]:+.6f}]  "
              f"(frozen text names no CI; position-cluster, supplied)")
        print(f"  (iv)  gradient Spearman(rho_b, d3) over "
              f"{len(res['g67'])} resolved nulls = {res['grad']:+.6f}  CI "
              f"[{res['ci_grad'][0]:+.6f}, {res['ci_grad'][1]:+.6f}] "
              f"(background-level)")
        print(f"  (v)   shift confound Spearman(rho_b, mean|delta_b|) over "
              f"{len(res['b96'])} backgrounds = {res['conf']:+.6f}  CI "
              f"[{res['ci_conf'][0]:+.6f}, {res['ci_conf'][1]:+.6f}] "
              f"(background-level)")
        print(f"  WORD ({model}): {res['word']}{tag_word}   [frozen section 3: "
              f"MODEL-REPLICATES iff the CI lies below zero AND "
              f"p_spec_H(neg) <= 0.10]")

    # -------------------------------------------------- cross-model (L-AN7)
    banner("CROSS-MODEL AGREEMENT (frozen section 2, last clause)", "-")
    for model in ("150M", "35M"):
        if model not in cols:
            gate(f"LD-AN7 cross-model agreement 650M vs {model}", None,
                 f"PENDING: no {model} column yet")
            continue
        cr = cross(d650, cols[model][0])
        print(f"  650M vs {model}: per-background delta-vector Spearman on "
              f"common H rows -- median {cr['median']:+.6f}, range "
              f"[{cr['lo']:+.6f}, {cr['hi']:+.6f}] over {cr['n']} "
              f"backgrounds; Spearman across the {cr['n']} backgrounds "
              f"between rho_b: {cr['across']:+.6f}")
        gate(f"LD-AN7 cross-model agreement 650M vs {model} computed", True,
             f"median {cr['median']:+.4f}, across-rho {cr['across']:+.4f}, "
             f"n = {cr['n']}")

    # ------------------------------------------------------------- G-L4 ----
    banner("G-L4 (HARD) -- PLANTED SIGNAL AND NULL ON SYNTHETIC SCORES", "-")
    t_g4 = time.time()

    # A1 signal: A222V negative, everyone else pure noise
    rng1 = np.random.default_rng(101)
    a1 = {bg: (-0.8 * Z + rng1.standard_normal(len(h))) if bg == ANCHOR
          else rng1.standard_normal(len(h)) for bg in own_of}
    r1 = analyse(a1, sw650, n_boot, want_gradient=False)
    gate("G-L4 A1 planted signal returns MODEL-REPLICATES",
         r1["word"] == "MODEL-REPLICATES",
         f"rho_A {r1['rho_A']:+.4f} CI [{r1['ci_A'][0]:+.4f}, "
         f"{r1['ci_A'][1]:+.4f}], p_spec_H(neg) {r1['p_neg']:.4f} "
         f"({r1['k_neg']}/{r1['n78']}) -> {r1['word']}")

    # A2 gradient: |rho_b| grows with d3 among the 67 resolved nulls
    vals = np.array(list(d3_of.values()))
    zd3 = {b: (v - vals.mean()) / vals.std() for b, v in d3_of.items()}
    rng2 = np.random.default_rng(102)
    a2 = {bg: (-(0.3 + 1.2 * zd3[bg]) * Z
               + 0.3 * rng2.standard_normal(len(h))) if bg in zd3
          else (-0.3 * Z + 0.3 * rng2.standard_normal(len(h)))
          for bg in own_of}
    r2 = analyse(a2, sw650, 10000)
    gate("G-L4 A2 planted gradient: its CI excludes zero in the NEGATIVE "
         "direction", r2["ci_grad"][1] < 0.0,
         f"gradient {r2['grad']:+.4f} CI [{r2['ci_grad'][0]:+.4f}, "
         f"{r2['ci_grad'][1]:+.4f}] over {len(r2['g67'])} nulls")

    # A3 shift confound: planted magnitude drives |delta_b| and rho_b's sign
    rng3 = np.random.default_rng(103)
    s3 = rng3.uniform(0.0, 1.0, len(own_of))
    a3 = {bg: (-(0.3 + 1.2 * s3[i]) * Z + 0.3 * rng3.standard_normal(len(h)))
          for i, bg in enumerate(own_of)}
    r3 = analyse(a3, sw650, 10000)
    gate("G-L4 A3 planted shift confound: its CI excludes zero (negative)",
         r3["ci_conf"][1] < 0.0,
         f"confound {r3['conf']:+.4f} CI [{r3['ci_conf'][0]:+.4f}, "
         f"{r3['ci_conf'][1]:+.4f}] over {len(r3['b96'])} backgrounds")

    # A4 null: delta independent of own_e.b; fire rate over 100 draws
    fires, seen = 0, {}
    rng4 = np.random.default_rng(1000)
    for _ in range(N_NULL_DRAWS):
        plant = {bg: rng4.standard_normal(len(h)) for bg in own_of}
        rr = analyse(plant, sw650, N_NULL_CI, want_gradient=False)
        seen[rr["word"]] = seen.get(rr["word"], 0) + 1
        if rr["word"] != "MODEL-DOES-NOT-REPLICATE":
            fires += 1
    rate = fires / N_NULL_DRAWS
    gate(f"G-L4 A4 planted null: fire rate <= {NULL_FIRE_MAX} over "
         f"{N_NULL_DRAWS} draws (per-plant CI pinned at {N_NULL_CI})",
         rate <= NULL_FIRE_MAX, f"{fires}/{N_NULL_DRAWS} = {rate:.3f}; words "
                                f"seen {seen}")

    # A5 cross-model: identical vs independent delta vectors
    rng5 = np.random.default_rng(105)
    base = {bg: rng5.standard_normal(len(h)) for bg in own_of}
    c_id = cross(base, dict(base))
    rng6 = np.random.default_rng(106)
    indep = {bg: rng6.standard_normal(len(h)) for bg in own_of}
    c_in = cross(base, indep)
    gate("G-L4 A5 identical-model plant: per-background and across-background "
         "agreement are 1.0 (<1e-9 from 1)",
         abs(c_id["median"] - 1.0) < 1e-9 and abs(c_id["across"] - 1.0) < 1e-9,
         f"median {c_id['median']!r}, across {c_id['across']!r}, n = {c_id['n']}")
    gate("G-L4 A5 independent-model plant: both agreement statistics below "
         "0.15 in absolute value",
         abs(c_in["median"]) < 0.15 and abs(c_in["across"]) < 0.15,
         f"median {c_in['median']:+.4f}, across {c_in['across']:+.4f}")
    print(f"  G-L4 wall {time.time() - t_g4:.0f}s")

    # ------------------------------------------------------------- G-L5 ----
    banner(f"G-L5 (HARD) -- identity, draw-by-draw reference, Phase 1 CI "
           f"(fixed {P1_N})", "-")
    real = results["650M"]
    mA = real["mask"][ANCHOR]
    xA, yA, cA = d650[ANCHOR][mA], own_eb[mA], h_pos[mA]

    gate("G-L5(i) identity: every position once == the anchor point estimate "
         "(<1e-12)",
         abs(float(p3c.spearman(xA, yA)) - real["rho_A"]) < 1e-12,
         f"|diff| = {abs(float(p3c.spearman(xA, yA)) - real['rho_A']):.3e}")
    ids_ref, _lab_ref = p3c.draw_ids(cA, N_REF, SEED)
    mine_ref = cluster_boot_stat(xA, yA, [], real["rbc"], ids_ref, "spearman")
    lib_ref = p3c.pos_cluster_boot_from_ids(xA, yA, cA, ids_ref)
    slow_ref = p3c.reference_boot(xA, yA, cA, ids_ref)
    d_lib = float(np.nanmax(np.abs(np.nan_to_num(mine_ref)
                                   - np.nan_to_num(lib_ref))))
    d_slow = float(np.nanmax(np.abs(np.nan_to_num(mine_ref)
                                    - np.nan_to_num(slow_ref))))
    gate(f"G-L5(ii-a) anchor draws == the slow reference draw by draw over "
         f"{N_REF} draws (<1e-12)", d_slow < 1e-12,
         f"max|diff| = {d_slow:.3e}")
    gate(f"G-L5(ii-a2) this script's own cluster bootstrap == the imported "
         f"corrected routine, draw by draw over {N_REF} draws (<1e-12)",
         d_lib < 1e-12,
         f"max|diff| = {d_lib:.3e} (same ids, two independent implementations "
         f"of the cluster expansion)")

    ones = np.arange(len(real["g67"]))
    gate("G-L5(i) identity: every background once == the gradient point "
         "estimate (<1e-12)",
         abs(float(p3c.spearman(real["r67"][ones], real["d367"][ones]))
             - real["grad"]) < 1e-12,
         f"|diff| = {abs(float(p3c.spearman(real['r67'][ones], real['d367'][ones])) - real['grad']):.3e}")
    rng_g = np.random.default_rng(SEED)
    d_grad = 0.0
    for _ in range(N_REF):
        ix = rng_g.integers(0, len(real["g67"]), len(real["g67"]))
        fast = float(p3c.spearman(real["r67"][ix], real["d367"][ix]))
        slow = float(pd.Series(real["r67"][ix]).rank(method="average")
                     .corr(pd.Series(real["d367"][ix]).rank(method="average")))
        d_grad = max(d_grad, abs(fast - slow))
    gate(f"G-L5(ii-b) gradient draws == a slow pandas-rank rebuild over "
         f"{N_REF} draws (<1e-12)", d_grad < 1e-12, f"max|diff| = {d_grad:.3e}")

    _, Aobj = pdg.build(verbose=False)
    ar = Aobj.a222v_rows
    p1 = p3c.pos_cluster_boot(ar.delta.to_numpy(float),
                             ar.own_e_b.to_numpy(float),
                             ar.position.to_numpy(), n_boot=P1_N, seed=SEED)
    lo, hi, nf = p3c.pct_ci(p1)
    gate("G-L5(iii) Phase 1 CI reproduces (each endpoint < 1e-9)",
         abs(lo - T_CI_LO) < 1e-9 and abs(hi - T_CI_HI) < 1e-9,
         f"lo {lo!r} (|diff| {abs(lo - T_CI_LO):.3e}), hi {hi!r} "
         f"(|diff| {abs(hi - T_CI_HI):.3e}), {nf} finite draws at {P1_N}, "
         f"from pdg's a222v_rows (the canonical construction)")

    # ---------------------------------------------------------- summary ----
    banner("SUMMARY")
    n_pass = sum(1 for _, v in gates if v is True)
    n_fail = sum(1 for _, v in gates if v is False)
    n_pend = sum(1 for _, v in gates if v is None)
    torch_in = "torch" in sys.modules
    print(f"  {n_pass} PASS, {n_fail} FAIL, {n_pend} PENDING of {len(gates)} "
          f"checks.")
    print(f"  torch in sys.modules: {torch_in} (must be False; rule 1)")
    if torch_in:
        n_fail += 1
    print("\nLIMITATIONS (printed per AGENTS 6; full list in the docstring):")
    print("    * a ladder word is about the SAME data scored at other model "
          "sizes; it is not an independent replication of the anchor's "
          "existence (module N tests that).")
    print("    * the 650M column is NOT out-of-sample (Phase 2 rows, already "
          "analysed); only 150M/35M are new data.")
    print("    * deltas are per-model WT-referenced: comparable in rank, "
          "never in scale.")
    print("    * G-L4's planted arms are mechanics checks on synthetic "
          "scores, not evidence about biology.")
    print("    * a CI excluding zero is not a finding on its own; every "
          "quantity is printed with its planted counterpart.")
    print("\nA8d RESULT: " + ("GATE FAIL -- exit 3" if n_fail
                              else "GATE PASS -- exit 0"))
    print(f"  elapsed {time.time() - t0:.1f}s")
    if n_fail:
        sys.exit(3)


if __name__ == "__main__":
    main()