"""Script 155 (Phase 3a session 3a, task A4f + A4g) -- GB1 regime-map
analysis: rho_b, distribution, covariate tests, sensitivities, two-sequence
comparison, gates G-3/G-4/A8 and G-SYN.  NO TORCH, NO ESM.

PRE-REGISTERED: this docstring was written before the first run of this
script.  It implements PHASE3_OVERNIGHT.md Tasks A4f/A4g under the frozen
prereg/GB1_REGIME_PREREG_v2.md (sha256 b3c82d589afc2889f60ad8626dcb24d0496
f77303d0696b52db700129fd1357e), sections 2-6 verbatim:

  STATISTIC (section 2).  For each background b (a GB1 single mutant) and
  each qualifying partner variant v measured in combination with b:
      delta_b(v) = S(v | b) - S(v | WT)
        S = ESM-2 650M masked-marginal log-odds against the wild-type
        residue; delta here = bg file score - wt_arm file score on the
        join key (position, mut_aa).  The two files are script 154's own
        output; delta is NOT recomputed from the model.
      e_b(v) = the measured genetic-interaction term by the same
        construction the project's GB1 transplant code uses (script 73,
        quoted at run time from scripts/73 lines 196-231, and script
        128's Phase 3a T3 reimplementation, lines 131-136, also quoted):
            e_b = f_vb - f_v * f_bg / f_wt
        On the Olson whole-domain data (W scale, f_wt = 1 by
        construction):
            W_x     = (sel_count / input_count) / F_B,wt
            f_bg    = the background's own single-mutant W (roster)
            f_v     = the partner single's W (singles)
            f_vb    = the double's W (that double row's own counts)
      rho_b = Spearman(delta_b, e_b) over b's qualifying partners,
        EXCLUDING any partner at b's own position (frozen G-2; the
        doubles matrix has pos1 != pos2 in every row -- structural, also
        re-checked here).

  QUALIFICATION (A1).  A double mutant qualifies iff Input Count >= 25
  (PRIMARY); sensitivities reported, none selected: >= 23, >= 28, and
  unfiltered.  The 100-partner floor (A1) is retained: a background with
  fewer than 100 qualifying partners is excluded from rho_b and counted
  (inert: every roster background clears it under every threshold; the
  count is printed).

  RESAMPLING UNITS (A5).  rho_b's own 95% CI: POSITION-CLUSTER bootstrap
  (clusters = partner positions; every variant at a drawn position comes
  with it, with multiplicity), N_BOOT_RB = 2000, SEED = 0, descriptive --
  computed for the PRIMARY threshold only (disclosure F3).  Every
  statistic ACROSS backgrounds (the distribution's mean; each covariate's
  Spearman): BACKGROUND-level bootstrap (backgrounds resampled with
  replacement, each rho_b held fixed), N_BOOT = 10000, SEED = 0;
  permutation p from 10,000 shuffles of the covariate across backgrounds
  (phase3_common.label_permutation_p(rho_b, covariate) -- y = the
  covariate is what is shuffled -- mode "abs", two-sided; disclosed as
  F4).  N_BOOT, N_BOOT_RB, N_PERM, SEED are read from the environment
  (project convention) with the frozen values as defaults; smoke runs
  lower them (AGENTS 1), which changes only Monte-Carlo error, never a
  rule or threshold.

  DISTRIBUTION (section 4): n, mean, median, SD, range, fraction rho_b < 0.
  SD is ddof=0 (numpy's default population SD over the completed set;
  disclosed as F5).  Centering: background-level bootstrap CI of the mean
  rho_b (N_BOOT draws, seed 0) -> CENTERED iff the CI includes 0, else
  OFF-CENTER (section 5).

  FOUR PRE-REGISTERED COVARIATES (section 4), each tested against rho_b by
  Spearman across backgrounds, each with a background-level bootstrap CI
  and a 10,000-shuffle permutation p:
    (a) mean sequence separation |pos(b) - pos(v)| over b's qualifying
        partners;
    (b) the background's own measured single-mutant fitness (W);
    (c) n_partners (the qualifying count actually used for rho_b);
    (d) the SD (ddof=0, disclosed F5) of e_b over b's partners.
  Each covariate's rows are the SAME partner rows rho_b used; when score
  coverage is complete (the expected case, G-4) that is exactly the
  qualifying set (F2).  Outcome words, frozen section 5: ASSOCIATED iff
  the background-level bootstrap CI excludes 0; NOT RESOLVED otherwise,
  reported as "n cannot resolve this" and never as "no relationship".

  SENSITIVITIES (A7): thresholds 23, 28, unfiltered -- every rho_b and
  the four covariate tests recomputed, all reported, none selected.

  TWO-SEQUENCE COMPARISON (A7): the first 20 backgrounds in roster order,
  scored on BOTH sequences (assayed = out-dir default; project = the
  project out-dir), reporting the Spearman between the two rho_b vectors
  and max |delta rho_b|.  Availability is reported truthfully: if the
  project-sequence files are not on disk yet (they are scored by the
  stage), the comparison prints "unavailable, N of 20 pairs present"
  rather than any number (F6; a shortfall is reported, not gated).

GATES (hard; failed gate -> FAIL + exit 3; thresholds never loosened):
  G-155-1  input sha256: doubles 89f8e394...47cc4769,
           singles 0b2e865e...65dbfc3, Phase 3a roster ee2e7872...e79aae4,
           roster_v2 edc259d4...b7dbe4e, sequences.csv f0d1d2d5...2ca25f.
  G-155-2  F_B,wt pin: recomputing every single's W from its own counts
           with F_B,wt = 3041819/1759616 (script 129 line 118, quoted at
           run time) reproduces the roster's stored fitness column to
           < 1e-12.
  G-3(i)   identity: the corrected position-cluster bootstrap with every
           cluster drawn exactly once reproduces each background's rho_b
           point estimate to < 1e-12.
  G-3(ii)  draw-by-draw: corrected routine vs the slow reference
           (phase3_common.reference_boot), identical pre-drawn cluster
           ids (seed 0, N_BOOT_RB draws), on the FIRST THREE completed
           backgrounds in roster order, max|diff| < 1e-12 draw by draw.
  G-3(iii) Phase 1 CI reproduction, ALWAYS at N=10000 fixed (the
           published interval is a 10,000-draw quantity; frozen target)
           on the MTHFR anchor rows (scripts/lib/phase2_diag.py build,
           same construction scripts/159 used):
           lo = -0.1173334458953319 and hi = -0.05951138449511738, each
           endpoint < 1e-9.  The frozen prereg line is printed at run
           time so the target's provenance is in the output.
  G-4      every completed background scores >= 95% of its 54 eligible
           positions (else FAIL).
  A8       >= 200 completed backgrounds (in roster order) required to
           interpret the covariate tests; with fewer, every covariate
           outcome is the word UNDERPOWERED and is not interpreted (the
           tests are still computed and printed).  The distribution and
           its centering word are still reported (frozen A8 text).
  G-SYN(i)  planted signal: delta_b = e_b + noise (within-background sd
           of e_b, drawn default_rng(1) over backgrounds in roster order)
           -> mean rho_b > 0 AND its background-level CI excludes 0
           (OFF-CENTER), with all four covariate tests COMPUTED and
           printed.
  G-SYN(ii) planted null: the SAME synthetic delta values permuted within
           each background (fixed default_rng(2) stream, roster order)
           -> the background-level CI of the mean INCLUDES 0 (CENTERED).
           If either G-SYN arm fails the analysis cannot be trusted: the
           run exits 3 and the night must not start.
  G-155-99 torch/esm are NOT imported by this script (checked in
           sys.modules at the end; must be absent).

  G-SYN scope (F7): synthetic sets are built for ALL 400 roster
  backgrounds from their real partner sets and real e_b -- partner sets
  need no scores -- so the planted tests run even before the stage
  scores.  G-SYN does not recompute per-background position-cluster CIs
  (they are not part of G-SYN's decisions); disclosed.

MODES: `--mode smoke` (default out-dir = the A4e smoke dir, caller lowers
N_*) and `--mode full` (default out-dir = the real stage dir; frozen
defaults N_BOOT=10000, N_BOOT_RB=2000, N_PERM=10000).  The mode changes
ONLY the default out-dir and the printed label -- no rule, threshold or
statistic differs between modes (F8).  This session runs smoke; the full
run of the real data is the A7 driver's job overnight, not here.

OUTPUTS: stdout is the record (tee'd by the caller);
  data/processed/phase3/gb1/gb1_rho_b_<mode>.csv -- per-background rho_b,
  CI (primary), covariates, partner counts, for session 3b re-verification.

LIMITATIONS (AGENTS 3, 4, 6; printed by the script itself):
  * The permutation p is an ASSOCIATION null, not a re-derivation null
    (phase3_common's own label); the ASSOCIATED/NOT RESOLVED decision
    uses the background-level CI, as frozen.
  * background_boot treats backgrounds as independent draws; all rho_b
    within one threshold share the same WT arm (disclosed, not modelled).
  * W values are read-depth-derived counts under the disclosed proxy of
    frozen A1; W can be 0 (a zero-count double), which is kept, never
    filtered; counts of non-positive W are printed.
  * rho_b's per-background CI is descriptive (frozen A5), not a test.
  * Wording: only the frozen block's outcome words are printed (CENTERED /
    OFF-CENTER / ASSOCIATED / NOT RESOLVED / UNDERPOWERED); no result here
    may be described as confirming, supporting or undermining any MTHFR
    result (frozen section 5) -- the systems, backgrounds and measurement
    platforms differ.

Usage:
  N_BOOT=300 N_BOOT_RB=300 N_PERM=300 venv/bin/python3 \\
      scripts/155_gb1_regime_analysis.py --mode smoke
"""

import argparse
import hashlib
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib import phase3_common as p3c                # noqa: E402

EXT = ROOT / "data" / "external" / "gb1_olson2014"
DOUBLES = EXT / "gb1_olson2014_doubles.csv"
SINGLES = EXT / "gb1_olson2014_singles.csv"
ROSTER_FULL = ROOT / "data" / "processed" / "gb1_background_roster.csv"
ROSTER2 = ROOT / "data" / "processed" / "phase3" / "gb1" / "roster_v2.csv"
SEQS_CSV = ROOT / "data" / "processed" / "phase3" / "gb1" / "sequences.csv"
SCRIPT73 = ROOT / "scripts" / "73_gb1_estimator_transplant.py"
SCRIPT128 = ROOT / "scripts" / "128_gb1_olson_verify_and_transplant_repro.py"
SCRIPT129 = ROOT / "scripts" / "129_gb1_background_roster.py"
OUT_RESULTS = ROOT / "data" / "processed" / "phase3" / "gb1"

SHAS = {
    DOUBLES: "89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769",
    SINGLES: "0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3",
    ROSTER_FULL: "ee2e7872c19530978f5e64fd3344c6a7597be025dcddb84bd50ac9230e79aae4",
    ROSTER2: "edc259d460691c244ba293bc9e3e8675e11e2ce27638cf5cd88796524b7dbe4e",
    SEQS_CSV: "f0d1d2d5b1376113568b17a04f5c9dfd9661517415c630e1d63a89b7032ca25f",
}
ASSAYED = "MQYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"
PROJECT = "MTYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE"

FLOOR = 100                 # frozen A1 floor (retained, expected inert)
PRIMARY_T = 25              # frozen A1 primary
SENS_T = [23, 28, None]     # sensitivities: 23, 28, unfiltered (None)
N_A8 = 200                  # frozen A8 completed-backgrounds floor
T_CI_LO = -0.1173334458953319
T_CI_HI = -0.05951138449511738
G3III_N = 10000             # frozen A6 target is a 10,000-draw interval
TOL_12 = 1e-12
TOL_9 = 1e-9
FIRST20 = 20                # frozen A7 two-sequence subset size
WT_IN, WT_SEL = 1759616, 3041819     # script 129 line 118, quoted at run
POSITIONS = list(range(2, 57))
ELIGIBLE_PER_BG = 54

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
N_BOOT_RB = int(os.environ.get("N_BOOT_RB", "2000"))
N_PERM = int(os.environ.get("N_PERM", "10000"))
SEED = int(os.environ.get("SEED", "0"))

GATES = []


def gate(name, verdict, value, note=""):
    GATES.append((name, verdict, value, note))
    print(f"  >>> {name}: {verdict}   value = {value}   {note}", flush=True)


def rule(t=""):
    print("\n" + "=" * 76)
    if(t):
        print(t)
        print("=" * 76)


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def quote(path, a, b, label):
    lines = Path(path).read_text().splitlines()
    print(f"  QUOTED SOURCE: {label} ({path}, lines {a}-{b}):")
    for i in range(a - 1, min(b, len(lines))):
        print(f"    {i + 1:4d}| {lines[i]}")


def centering_word(draws):
    lo, hi, nf = p3c.pct_ci(draws)
    includes_zero = (not np.isnan(lo)) and lo <= 0.0 <= hi
    word = "CENTERED" if includes_zero else "OFF-CENTER"
    return lo, hi, nf, word


def covariate_word(rho_k, lo, hi, n_bg):
    if n_bg < N_A8:
        return "UNDERPOWERED"
    excludes = (not np.isnan(lo)) and (lo > 0.0 or hi < 0.0)
    return "ASSOCIATED" if excludes else "NOT RESOLVED"


def summary_stats(rho):
    rho = np.asarray(rho, dtype=float)
    return dict(n=int(rho.size), mean=float(np.mean(rho)),
                median=float(np.median(rho)), sd=float(np.std(rho)),
                lo=float(np.min(rho)), hi=float(np.max(rho)),
                frac_neg=float(np.mean(rho < 0)))


def load_scores(out_dir, ros400, wt_expected_label):
    """Read wt_arm + every completed bg file (roster order).  Returns
    (wt_map, completed list of (row, bg_df), coverage issues)."""
    out_dir = Path(out_dir)
    wt_path = out_dir / "wt_arm.csv"
    if not wt_path.exists():
        return None, [], [f"wt_arm.csv missing in {out_dir}"]
    wt = pd.read_csv(wt_path)
    issues = []
    if set(wt["sequence"].astype(str)) != {wt_expected_label}:
        issues.append(f"wt_arm sequence label {set(wt['sequence'])} != "
                      f"{wt_expected_label}")
    if len(wt) != 55 * 19 or wt.duplicated(["position", "mut_aa"]).any() \
            or set(wt["position"].astype(int)) != set(POSITIONS):
        issues.append(f"wt_arm shape wrong: {len(wt)} rows")
    wt_map = {(int(r.position), r.mut_aa): float(r.score)
              for r in wt.itertuples()}

    completed = []
    stray = 0
    known = set(ros400["background_id"])
    for p in sorted(out_dir.glob("bg_*.csv")):
        bid = p.stem[len("bg_"):]
        if bid not in known:
            stray += 1
            continue
        df = pd.read_csv(p)
        completed.append((bid, df))
    order = {b: i for i, b in enumerate(ros400["background_id"])}
    completed.sort(key=lambda t: order[t[0]])
    return wt_map, completed, issues + [f"stray bg files ignored: {stray}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--project-out-dir",
                    default="data/processed/phase3/gb1_project")
    args = ap.parse_args()
    t0 = time.time()

    default_out = ("data/processed/phase3/gb1_smoke" if args.mode == "smoke"
                   else "data/processed/phase3/gb1")
    out_dir = ROOT / (args.out_dir or default_out)
    proj_dir = ROOT / args.project_out_dir

    rule(f"155 -- GB1 REGIME-MAP ANALYSIS  mode={args.mode}  out_dir="
         f"{out_dir.relative_to(ROOT)}")
    print(f"N_BOOT={N_BOOT} (across-background), N_BOOT_RB={N_BOOT_RB} "
          f"(per-background CI), N_PERM={N_PERM}, SEED={SEED}")
    print("NO TORCH, NO ESM: this script imports neither (gate G-155-99 "
          "checks sys.modules at the end).")

    # ---------------- G-155-1 input hashes ------------------------------
    rule("G-155-1 -- INPUT SHA256 (targets printed beside)")
    for p, want in SHAS.items():
        got = sha256_of(p)
        ok = got == want
        print(f"  {p.relative_to(ROOT)}\n    got    {got}\n    target {want}"
              f"   {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            gate("G-155-1 input sha256", "FAIL", got, f"target {want}")
            sys.exit(3)
    gate("G-155-1 input sha256", "PASS", "5/5",
         "doubles, singles, Phase 3a roster, roster_v2, sequences")

    # ---------------- quoted sources ------------------------------------
    rule("QUOTED SOURCES -- e_b construction and F_B,wt (frozen section 2)")
    quote(SCRIPT73, 196, 231, "script 73 e_b construction (f_v/f_vb/"
          "expct/e_b)")
    quote(SCRIPT128, 131, 136, "Phase 3a T3's verbatim reimplementation")
    quote(SCRIPT129, 116, 119, "F_B,wt constants")
    quote(SCRIPT129, 172, 174, "single-mutant W formula")

    # ---------------- data + F_B,wt pin ---------------------------------
    dbl = pd.read_csv(DOUBLES)
    sgl = pd.read_csv(SINGLES)
    ros_full = pd.read_csv(ROSTER_FULL)
    ros400 = pd.read_csv(ROSTER2).sort_values("draw_order").reset_index(
        drop=True)
    seqs = pd.read_csv(SEQS_CSV).set_index("name")["sequence"].to_dict()
    print(f"\n  doubles {len(dbl):,} rows, singles {len(sgl):,} rows, "
          f"roster {len(ros_full):,}, roster_v2 {len(ros400)}")

    F_WT = WT_SEL / WT_IN
    sgl = sgl.copy()
    sgl["W"] = (sgl["sel_count"] / sgl["input_count"]) / F_WT
    chk = sgl[["pos", "mut", "W"]].merge(
        ros_full[["pos", "mut", "background_single_fitness_W"]],
        on=["pos", "mut"], how="inner")
    d_w = float(np.abs(chk["W"] - chk["background_single_fitness_W"]).max())
    gate("G-155-2 F_B,wt pin (recomputed singles W == roster column)",
         "PASS" if d_w < TOL_12 else "FAIL", f"max|diff| = {d_w:.3e} over "
         f"{len(chk):,} singles", f"tolerance {TOL_12}; F_B,wt = "
         f"{WT_SEL}/{WT_IN} = {F_WT:.9f}")
    print(f"  single W: min {sgl['W'].min():.4f}  median "
          f"{sgl['W'].median():.4f}  max {sgl['W'].max():.4f}; "
          f"singles with W <= 0: {int((sgl['W'] <= 0).sum())}")

    # ---------------- long partner table with e_b ------------------------
    rule("PARTNER TABLE -- every double row as (background, partner), "
         "e_b by script 73's construction")
    a = dbl.rename(columns={"pos1": "pos", "mut1": "mut"}).rename(
        columns={"pos2": "v_pos", "mut2": "v_mut"})
    b = dbl.rename(columns={"pos2": "pos", "mut2": "mut"}).rename(
        columns={"pos1": "v_pos", "mut1": "v_mut"})
    keep = ["pos", "mut", "v_pos", "v_mut", "input_count", "sel_count"]
    long = pd.concat([a[keep], b[keep]], ignore_index=True)
    same_pos = int((long["pos"] == long["v_pos"]).sum())
    print(f"  partner occurrences: {len(long):,} = 2 x {len(dbl):,} | "
          f"rows with v_pos == pos: {same_pos} (frozen G-2 structural: "
          f"must be 0)")
    long["W_double"] = (long["sel_count"] / long["input_count"]) / F_WT
    n_nonpos_W = int((long["W_double"] <= 0).sum())
    long = long.merge(sgl[["pos", "mut", "W"]].rename(
        columns={"pos": "v_pos", "mut": "v_mut", "W": "W_v"}),
        on=["v_pos", "v_mut"], how="left")
    long = long.merge(ros_full[["pos", "mut",
                                "background_single_fitness_W"]].rename(
        columns={"pos": "pos", "mut": "mut", "background_single_fitness_W":
                 "W_bg"}), on=["pos", "mut"], how="left")
    miss_v = int(long["W_v"].isna().sum())
    miss_bg = int(long["W_bg"].isna().sum())
    long["e_b"] = long["W_double"] - long["W_v"] * long["W_bg"]  # f_wt = 1
    # partners at their own position are impossible (checked above); the
    # data-derived WT residue check (partner must be a real substitution)
    bad_mut = int((long["v_mut"].to_numpy()
                   == np.array([ASSAYED[int(p) - 1]
                                for p in long["v_pos"]])).sum())
    print(f"  e_b = W_double - W_v * W_bg (f_wt = 1 by W construction)")
    print(f"  partner singles missing W_v: {miss_v} | backgrounds missing "
          f"W_bg: {miss_bg} | double rows with W <= 0: {n_nonpos_W:,} "
          f"(kept, never filtered)")
    print(f"  partner rows whose v_mut equals the WT residue at v_pos: "
          f"{bad_mut} (expected 0; such rows would drop from rho_b with a "
          f"printed count)")
    gate("partner-table structure", "PASS" if (same_pos == 0 and miss_v == 0
                                               and miss_bg == 0) else "FAIL",
         f"same-position {same_pos}, missing W_v {miss_v}, missing W_bg "
         f"{miss_bg}", "all must be 0")

    # restrict to the 400 roster backgrounds (merge keys stay pos/mut;
    # b_pos is an alias of the background's own position, added after)
    r4 = ros400[["background_id", "pos", "mut", "wt_aa"]]
    long = long.merge(r4, on=["pos", "mut"], how="inner")
    long["b_pos"] = long["pos"]
    print(f"  partner rows for the 400 roster backgrounds: {len(long):,}")

    # ---------------- scores --------------------------------------------
    rule("SCORES -- wt_arm + completed background files (script 154's "
         "output, joined on (position, mut_aa))")
    wt_map, completed, issues = load_scores(out_dir, ros400, "assayed")
    for msg in issues:
        print(f"  note: {msg}")
    print(f"  completed backgrounds (roster order): {len(completed)} "
          f"of {len(ros400)}")
    if wt_map is None:
        print("  (no wt_arm file: rho_b cannot be computed on this run; "
              "G-SYN and G-3(iii) still run)")

    # coverage G-4 + delta table
    cov_fail, deltas_all = [], {}
    if wt_map is not None:
        for bid, df in completed:
            npos = int(df["position"].nunique())
            frac = npos / ELIGIBLE_PER_BG
            if frac < 0.95:
                cov_fail.append((bid, npos, frac))
            m = df.merge(pd.DataFrame(
                [(p, v, s) for (p, v), s in wt_map.items()],
                columns=["position", "mut_aa", "score_wt"]),
                on=["position", "mut_aa"], how="left")
            if m["score_wt"].isna().any():
                cov_fail.append((bid, "wt join missing",
                                 float(m["score_wt"].isna().mean())))
            m["delta"] = m["score"] - m["score_wt"]
            if not np.isfinite(m["delta"]).all():
                cov_fail.append((bid, "non-finite delta", None))
            deltas_all[bid] = {(int(r.position), r.mut_aa): float(r.delta)
                                for r in m.itertuples()}
    gate("G-4 every completed background >= 95% of its 54 eligible "
         "positions", "PASS" if (wt_map is not None and not cov_fail)
         else ("FAIL" if wt_map is not None else "FAIL"),
         f"completed {len(completed)}, coverage failures {len(cov_fail)}",
         str(cov_fail[:3]) if cov_fail else "all complete")

    # ---------------- G-3(iii) Phase 1 CI (always N=10000) ---------------
    rule("G-3(iii) -- PHASE 1 CI REPRODUCTION ON THE MTHFR ANCHOR ROWS "
         f"(fixed N={G3III_N})")
    # frozen target provenance: the prereg line itself
    pre = (ROOT / "docs" / "tasks" / "phase3-overnight" / "prereg" /
           "GB1_REGIME_PREREG_v2.md").read_text()
    m = re.search(r"reproduce Phase 1's published MTHFR CI \[([^\]]+)\]",
                  pre)
    print(f"  frozen prereg line target: "
          f"[{m.group(1) if m else 'NOT FOUND'}]")
    tb = time.time()
    from scripts.lib import phase2_diag as pdg
    s125, Aobj = pdg.build(verbose=False)
    ar = Aobj.a222v_rows
    ax = ar.delta.to_numpy(float)
    ay = ar.own_e_b.to_numpy(float)
    draws = p3c.pos_cluster_boot(ax, ay, ar.position.to_numpy(),
                                 n_boot=G3III_N, seed=SEED)
    lo, hi, nf = p3c.pct_ci(draws)
    d_lo, d_hi = abs(lo - T_CI_LO), abs(hi - T_CI_HI)
    print(f"  anchor rows {len(ar):,} / {ar.position.nunique()} positions; "
          f"{G3III_N} draws in {time.time() - tb:.1f}s ({nf} finite)")
    print(f"  lo got {lo!r} target {T_CI_LO!r} |diff| = {d_lo:.3e}")
    print(f"  hi got {hi!r} target {T_CI_HI!r} |diff| = {d_hi:.3e}")
    gate("G-3(iii) Phase 1 CI reproduces (each endpoint < 1e-9)",
         "PASS" if (d_lo < TOL_9 and d_hi < TOL_9) else "FAIL",
         f"|diff| lo = {d_lo:.3e}, hi = {d_hi:.3e}",
         f"tolerance {TOL_9}")

    if wt_map is None or not completed:
        print("\n  (no completed backgrounds with scores: real rho_b "
              "section skipped; G-SYN follows)")

    # ---------------- per-threshold analysis -----------------------------
    results = {}
    bg_rows = []
    if completed:
        n_bg_total = len(completed)
        for t in [PRIMARY_T] + SENS_T:
            tag = ("t25 (PRIMARY)" if t == PRIMARY_T else
                   (f"t{t}" if t is not None else "unfiltered"))
            rule(f"THRESHOLD {tag} -- rho_b distribution and covariates")
            per_bg, excluded_floor, dropped_delta = [], 0, 0
            for bid, _ in completed:
                q = long[long["background_id"] == bid]
                q = q[q["input_count"] >= (0 if t is None else t)]
                if len(q) < FLOOR:
                    excluded_floor += 1
                    continue
                dmap = deltas_all[bid]
                delta = []
                keep_rows = []
                for r in q.itertuples():
                    d = dmap.get((int(r.v_pos), r.v_mut))
                    if d is None:
                        dropped_delta += 1
                        continue
                    delta.append(d)
                    keep_rows.append(r)
                if len(keep_rows) < FLOOR:
                    excluded_floor += 1
                    continue
                eb = np.array([r.e_b for r in keep_rows], dtype=float)
                dl = np.array(delta, dtype=float)
                vpos = np.array([int(r.v_pos) for r in keep_rows])
                rho = p3c.spearman(dl, eb)
                per_bg.append(dict(
                    background_id=bid, rho_b=rho, n=len(keep_rows),
                    mean_abs_dpos=float(np.mean(np.abs(
                        [int(r.b_pos) - int(r.v_pos)
                         for r in keep_rows]))),
                    fit=float(ros400.loc[
                        ros400.background_id == bid,
                        "background_single_fitness_W"].iloc[0]),
                    sd_eb=float(np.std(eb)),
                    clusters=vpos, dl=dl, eb=eb))
            print(f"  completed {n_bg_total} | excluded by {FLOOR}-floor: "
                  f"{excluded_floor} | partner rows dropped for missing "
                  f"delta: {dropped_delta} (roster-order partner sets; "
                  f"rho_b over the rows with both delta and e_b)")
            finite = [p for p in per_bg if np.isfinite(p["rho_b"])]
            rho_arr = np.array([p["rho_b"] for p in finite])
            st = summary_stats(rho_arr)
            print(f"  distribution: n={st['n']}  mean={st['mean']:+.6f}  "
                  f"median={st['median']:+.6f}  sd(ddof=0)={st['sd']:.6f}"
                  f"  range=[{st['lo']:+.6f}, {st['hi']:+.6f}]  "
                  f"frac<0={st['frac_neg']:.4f}")
            # centering
            cd, _ = p3c.background_boot(rho_arr, None, n_boot=N_BOOT,
                                        seed=SEED)
            lo_c, hi_c, nf_c, word = centering_word(cd)
            print(f"  centering: background-level CI of mean rho_b = "
                  f"[{lo_c:+.6f}, {hi_c:+.6f}] ({nf_c} finite of "
                  f"{N_BOOT}) -> {word}")
            if word == "OFF-CENTER":
                print("    (frozen section 5: OFF-CENTER is a property of "
                      "the statistic in this system, reported with equal "
                      "prominence either way)")
            if st["n"] < N_A8:
                print(f"  A8: n = {st['n']} < {N_A8} -- distribution "
                      f"reported; covariate tests labelled UNDERPOWERED "
                      f"and not interpreted")
            # covariates
            covs = [
                ("(a) mean |pos(b)-pos(v)|",
                 np.array([p["mean_abs_dpos"] for p in finite])),
                ("(b) background single fitness W",
                 np.array([p["fit"] for p in finite])),
                ("(c) n_partners", np.array([p["n"] for p in finite],
                                            dtype=float)),
                ("(d) SD of e_b", np.array([p["sd_eb"] for p in finite])),
            ]
            cov_out = []
            for name, cov in covs:
                rk = p3c.spearman(rho_arr, cov)
                bd, _ = p3c.background_boot(rho_arr, cov, n_boot=N_BOOT,
                                            seed=SEED, stat=p3c.spearman)
                lo_k, hi_k, nf_k = p3c.pct_ci(bd)
                pv, k_perm, n_perm = p3c.label_permutation_p(
                    rho_arr, cov, n_perm=N_PERM, seed=SEED, mode="abs")
                w = covariate_word(rk, lo_k, hi_k, st["n"])
                extra = (" (n cannot resolve this)"
                         if w == "NOT RESOLVED" else "")
                print(f"  covariate {name}: rho={rk:+.6f}  "
                      f"CI=[{lo_k:+.6f}, {hi_k:+.6f}]  perm_p="
                      f"{pv:.4f} ({k_perm + 1}/{n_perm + 1}) -> {w}{extra}")
                cov_out.append(dict(cov=name, rho=rk, ci_lo=lo_k,
                                    ci_hi=hi_k, p=pv, word=w))
            results[t] = dict(tag=tag, stats=st, centering=word,
                              ci_mean=[lo_c, hi_c], cov=cov_out,
                              per_bg=[{k: v for k, v in p.items()
                                       if k in ("background_id", "rho_b",
                                                "n", "mean_abs_dpos",
                                                "fit", "sd_eb")}
                                      for p in finite])
            if t == PRIMARY_T:
                for p in finite:
                    bg_rows.append(dict(
                        background_id=p["background_id"], rho_b=p["rho_b"],
                        n_partners_t25=p["n"],
                        mean_abs_dpos=p["mean_abs_dpos"],
                        single_fitness_W=p["fit"], sd_eb=p["sd_eb"],
                        cluster_ci_note="see stdout for CI (primary "
                                        "threshold)"))
                # per-background position-cluster CI (primary only, F3)
                print(f"  per-background position-cluster CIs "
                      f"(N_BOOT_RB={N_BOOT_RB}, seed {SEED}, primary "
                      f"only):")
                for i, p in enumerate(finite):
                    bd = p3c.pos_cluster_boot(p["dl"], p["eb"],
                                              p["clusters"],
                                              n_boot=N_BOOT_RB, seed=SEED)
                    lo_b, hi_b, _ = p3c.pct_ci(bd)
                    bg_rows[i]["ci_lo"] = lo_b
                    bg_rows[i]["ci_hi"] = hi_b
                    if i < 5:
                        print(f"    {p['background_id']}: rho_b="
                              f"{p['rho_b']:+.6f} CI=[{lo_b:+.6f}, "
                              f"{hi_b:+.6f}] n={p['n']}")

    # ---------------- G-3(i) and G-3(ii) on real GB1 rows ---------------
    rule("G-3(i)/(ii) -- BOOTSTRAP GATES ON REAL GB1 BACKGROUNDS")
    if completed:
        worst_i = 0.0
        # rebuild primary per_bg arrays (they were not kept with arrays);
        # recompute the every-cluster-once identity for ALL completed
        # backgrounds under a fresh primary filter
        prim = {}
        for bid, _ in completed:
            q = long[(long["background_id"] == bid)
                     & (long["input_count"] >= PRIMARY_T)]
            dmap = deltas_all[bid]
            rows = [(dmap[(int(r.v_pos), r.v_mut)], r.e_b, int(r.v_pos))
                    for r in q.itertuples()
                    if (int(r.v_pos), r.v_mut) in dmap]
            if len(rows) < FLOOR:
                continue
            dl = np.array([x[0] for x in rows])
            eb = np.array([x[1] for x in rows])
            cl = np.array([x[2] for x in rows])
            prim[bid] = (dl, eb, cl)
        for bid, (dl, eb, cl) in prim.items():
            nk = len(np.unique(cl))
            ids = np.arange(nk, dtype=np.int64).reshape(1, nk)
            one = p3c.pos_cluster_boot_from_ids(dl, eb, cl, ids)[0]
            pt = p3c.spearman(dl, eb)
            worst_i = max(worst_i, abs(one - pt))
        gate("G-3(i) every-cluster-once reproduces rho_b (all completed)",
             "PASS" if worst_i < TOL_12 else "FAIL",
             f"max|diff| = {worst_i:.3e} over {len(prim)} backgrounds",
             f"tolerance {TOL_12}")
        first3 = list(prim.items())[:3]
        if len(first3) < 3:
            gate("G-3(ii) draw-by-draw vs slow reference (3 real "
                 "backgrounds)", "FAIL", f"only {len(first3)} completed",
                 "frozen A6 requires three real backgrounds")
        else:
            worst_ii = 0.0
            for bid, (dl, eb, cl) in first3:
                ids, _ = p3c.draw_ids(cl, N_BOOT_RB, seed=SEED)
                fast = p3c.pos_cluster_boot_from_ids(dl, eb, cl, ids)
                slow = p3c.reference_boot(dl, eb, cl, ids)
                d = float(np.max(np.abs(fast - slow)))
                worst_ii = max(worst_ii, d)
                print(f"  {bid}: {N_BOOT_RB} draws, max|corrected - "
                      f"reference| = {d:.3e}")
            gate("G-3(ii) draw-by-draw vs slow reference (3 real "
                 "backgrounds)", "PASS" if worst_ii < TOL_12 else "FAIL",
                 f"max|diff| = {worst_ii:.3e}",
                 f"tolerance {TOL_12} (frozen A6)")
    else:
        gate("G-3(i) every-cluster-once reproduces rho_b", "FAIL",
             "no completed backgrounds", "")
        gate("G-3(ii) draw-by-draw vs slow reference", "FAIL",
             "no completed backgrounds", "")

    # ---------------- two-sequence comparison (A7) -----------------------
    rule("TWO-SEQUENCE COMPARISON (frozen A7) -- first 20 in roster order")
    first20 = list(ros400["background_id"][:FIRST20])
    pairs, pairs_rho = [], []
    deltas_all_p = {}
    if proj_dir.exists() and (proj_dir / "wt_arm.csv").exists():
        pw_map, pcompleted, pissues = load_scores(proj_dir, ros400,
                                                  "project")
        # project-sequence deltas vs the PROJECT wt arm (decision: the
        # comparison is within-sequence delta = score - own-sequence WT,
        # never across sequences)
        if pw_map is not None:
            for bid, df in pcompleted:
                m = df.merge(pd.DataFrame(
                    [(p, v, s) for (p, v), s in pw_map.items()],
                    columns=["position", "mut_aa", "score_wt"]),
                    on=["position", "mut_aa"], how="left")
                if m["score_wt"].isna().any() or \
                        not np.isfinite(m["score"] - m["score_wt"]).all():
                    continue  # incomplete join: pair simply not available
                deltas_all_p[bid] = {
                    (int(r.position), r.mut_aa): float(r.score - r.score_wt)
                    for r in m.itertuples()}
        ahave = set(deltas_all)
        have_p = set(deltas_all_p)
        pairs = [b for b in first20 if b in ahave and b in have_p]
    print(f"  pairs present on both sequences: {len(pairs)} of {FIRST20} "
          f"{pairs}")
    if len(pairs) >= 3:
        for bid in pairs:
            q = long[(long["background_id"] == bid)
                     & (long["input_count"] >= PRIMARY_T)]
            da, dp = deltas_all[bid], deltas_all_p[bid]
            ea, ra, rp = [], [], []
            for r in q.itertuples():
                key = (int(r.v_pos), r.v_mut)
                if key in da and key in dp:
                    ea.append(r.e_b)
                    ra.append(da[key])
                    rp.append(dp[key])
            if len(ea) >= 3:
                rho_a = p3c.spearman(np.array(ra), np.array(ea))
                rho_p = p3c.spearman(np.array(rp), np.array(ea))
                pairs_rho.append((bid, rho_a, rho_p))
        if len(pairs_rho) >= 3:
            va = np.array([x[1] for x in pairs_rho])
            vp = np.array([x[2] for x in pairs_rho])
            rho_vectors = p3c.spearman(va, vp)
            max_d = float(np.max(np.abs(va - vp)))
            print(f"  Spearman between the two rho_b vectors "
                  f"(n={len(va)}): {rho_vectors:+.6f}")
            print(f"  max |delta rho_b|: {max_d:.6f}")
        else:
            print("  comparison unavailable (fewer than 3 pairs with "
                  "computable rho_b); reported as unavailable, never as "
                  "0")
    else:
        print("  comparison UNAVAILABLE: the project-sequence scores are "
              "produced by the stage (first 20 on both sequences); "
              f"{len(pairs)} of {FIRST20} pairs on disk now.  Not gated; "
              "the stage's analysis run will report the two numbers.")

    # ---------------- G-SYN (A4g) ----------------------------------------
    rule("G-SYN -- PLANTED SIGNAL AND PLANTED NULL ON SYNTHETIC SCORES "
         "(all 400 roster backgrounds; frozen G-SYN)")
    print("  synthetic sets built from the REAL partner sets (primary "
          "t=25) and REAL e_b --\n  no scores involved (decision F7).  "
          "per-background position-cluster CIs are not recomputed on "
          "synthetic arms (disclosed).")
    syn = {}
    for bid in ros400["background_id"]:
        q = long[(long["background_id"] == bid)
                 & (long["input_count"] >= PRIMARY_T)]
        if len(q) < FLOOR:
            continue
        syn[bid] = (np.array(q["e_b"], dtype=float),
                    np.array([int(v) for v in q["v_pos"]]))
    print(f"  backgrounds with >= {FLOOR} qualifying partners: "
          f"{len(syn)} of {len(ros400)}")
    rng1 = np.random.default_rng(1)
    rho_i, rho_ii, eb_list, cov_lists = [], [], [], []
    rng2 = np.random.default_rng(2)
    n_sd_fallback = 0
    cov_a_i, cov_b_i, cov_c_i, cov_d_i = [], [], [], []
    for bid in ros400["background_id"]:
        if bid not in syn:
            continue
        eb, vp = syn[bid]
        sd = float(np.std(eb))
        if sd == 0.0:
            sd = 1.0
            n_sd_fallback += 1
        delta_i = eb + rng1.normal(0.0, sd, size=eb.shape)
        rho_i.append(p3c.spearman(delta_i, eb))
        perm = rng2.permutation(delta_i)
        rho_ii.append(p3c.spearman(perm, eb))
        fit = float(ros400.loc[ros400.background_id == bid,
                               "background_single_fitness_W"].iloc[0])
        cov_a_i.append(float(np.mean(np.abs(
            [int(ros400.loc[ros400.background_id == bid,
                            "pos"].iloc[0]) - int(v) for v in vp]))))
        cov_b_i.append(fit)
        cov_c_i.append(float(len(eb)))
        cov_d_i.append(float(np.std(eb)))
    rho_i = np.array(rho_i)
    rho_ii = np.array(rho_ii)
    print(f"  sd==0 fallbacks: {n_sd_fallback}")
    print(f"  arm (i) delta = e_b + noise: n={len(rho_i)}  mean="
          f"{rho_i.mean():+.6f}")
    cd_i, _ = p3c.background_boot(rho_i, None, n_boot=N_BOOT, seed=SEED)
    lo_i, hi_i, _, word_i = centering_word(cd_i)
    print(f"    background-level CI of mean = [{lo_i:+.6f}, {hi_i:+.6f}] "
          f"-> {word_i}")
    # every covariate test COMPUTED (frozen G-SYN(i)), printed
    for name, cov in [("(a) mean |Δpos|", np.array(cov_a_i)),
                      ("(b) single fitness W", np.array(cov_b_i)),
                      ("(c) n_partners", np.array(cov_c_i)),
                      ("(d) SD of e_b", np.array(cov_d_i))]:
        rk = p3c.spearman(rho_i, cov)
        bd, _ = p3c.background_boot(rho_i, cov, n_boot=N_BOOT, seed=SEED,
                                    stat=p3c.spearman)
        lo_k, hi_k, _ = p3c.pct_ci(bd)
        pv, kp, np_ = p3c.label_permutation_p(rho_i, cov, n_perm=N_PERM,
                                              seed=SEED, mode="abs")
        print(f"    [G-SYN synthetic] covariate {name}: rho={rk:+.6f} "
              f"CI=[{lo_k:+.6f}, {hi_k:+.6f}] perm_p={pv:.4f} "
              f"(computed)")
    gate("G-SYN(i) planted signal: positive mean AND CI excludes 0 "
         "(OFF-CENTER), covariates computed",
         "PASS" if (rho_i.mean() > 0 and word_i == "OFF-CENTER") else
         "FAIL",
         f"mean = {rho_i.mean():+.6f}, CI = [{lo_i:+.6f}, {hi_i:+.6f}] "
         f"-> {word_i}", "delta = e_b + within-background noise")
    print(f"  arm (ii) permuted delta: n={len(rho_ii)}  mean="
          f"{rho_ii.mean():+.6f}")
    cd_ii, _ = p3c.background_boot(rho_ii, None, n_boot=N_BOOT, seed=SEED)
    lo_ii, hi_ii, _, word_ii = centering_word(cd_ii)
    print(f"    background-level CI of mean = [{lo_ii:+.6f}, "
          f"{hi_ii:+.6f}] -> {word_ii}")
    gate("G-SYN(ii) planted null: CI includes 0 (CENTERED)",
         "PASS" if word_ii == "CENTERED" else "FAIL",
         f"mean = {rho_ii.mean():+.6f}, CI = [{lo_ii:+.6f}, "
         f"{hi_ii:+.6f}] -> {word_ii}", "fixed within-background "
         "permutation, default_rng(2)")

    # ---------------- write per-background results -----------------------
    if bg_rows:
        OUT_RESULTS.mkdir(parents=True, exist_ok=True)
        outp = OUT_RESULTS / f"gb1_rho_b_{args.mode}.csv"
        pd.DataFrame(bg_rows).to_csv(outp, index=False)
        print(f"\n  per-background results written: "
              f"{outp.relative_to(ROOT)} ({len(bg_rows)} rows)")
    else:
        print("\n  per-background results: none (no completed "
              "backgrounds with scores)")

    # ---------------- summary -------------------------------------------
    rule(f"SUMMARY -- mode={args.mode}")
    n_pass = 0
    for name, verdict, value, note in GATES:
        print(f"  [{verdict}] {name}: {value}  {note}")
        n_pass += verdict == "PASS"
    if completed:
        print("\n  outcome words printed above (frozen section 5): "
              "CENTERED/OFF-CENTER for the distribution; ASSOCIATED / "
              "NOT RESOLVED / UNDERPOWERED per covariate (A8 floor "
              f"{N_A8}: this run has {len(completed)} completed "
              "backgrounds).")
    not_orch = ("torch" not in sys.modules) and ("esm" not in sys.modules)
    print(f"  torch in sys.modules: {'torch' in sys.modules}; esm: "
          f"{'esm' in sys.modules}")
    gate("G-155-99 analysis runs without torch/esm", "PASS" if not_orch
         else "FAIL", f"torch={'torch' in sys.modules}, "
         f"esm={'esm' in sys.modules}", "A4f must be model-free")
    n_pass = sum(1 for g in GATES if g[1] == "PASS")
    ok = n_pass == len(GATES)
    print(f"\n  GATES: {n_pass}/{len(GATES)} PASS, {len(GATES) - n_pass} "
          f"FAIL -> exit {0 if ok else 3}")
    print("\n  LIMITATIONS (AGENTS 3/4/6, printed by the script itself):")
    print("    * the permutation p is an association null, not a "
          "re-derivation null; the frozen\n      decision uses the "
          "background-level CI.")
    print("    * background_boot treats backgrounds as independent "
          "draws; all rho_b within one\n      threshold share the same "
          "WT arm (disclosed, not modelled).")
    print("    * W values are read-depth-derived (disclosed proxy, "
          "frozen A1); zero-count\n      doubles are kept, never "
          "filtered (counts printed above).")
    print("    * rho_b's per-background CI is descriptive (frozen A5), "
          "not a test.")
    print("    * no result here may be described as confirming, "
          "supporting or undermining any\n      MTHFR result (frozen "
          "section 5): the systems, backgrounds and platforms differ.")
    print(f"\n  elapsed {time.time() - t0:.1f}s")
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
