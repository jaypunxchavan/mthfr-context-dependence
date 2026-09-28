"""
Script 112 (task C1, Group C) -- reconcile the severity-partial
discrepancy: why the plain LINEAR partial and the existing SPLINE
partial of delta_ESM <-> own_e.b controlling WT-background severity
disagree (review section 1.3).  PRE-REGISTERED: this docstring was
written before the first run; every formula, cell, gate, and reporting
rule below was fixed before any number produced here was seen.

Task: docs/tasks/phase1-corrections-diagnostics/
      PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md, Group C, task C1 (C1a-C1c).

GATING CHECK (C1a, done FIRST, before any recomputation -- per task):
  The two prior figures and the spline's severity control are traced to
  their producing source, scripts/43_flattening_partial.py, and the
  following source substrings are ASSERTED present at runtime (they are
  printed as evidence):
    (a) 'for z in ["esm2_score", "base_functionality", "f_bar_wt"]'
        -> the "Raw correlations" block prints, ON ONE LINE, both
           rho(delta, esm2_score) = -0.3238   AND
           rho(own_e_b, esm2_score) = +0.0854
        => the two prior figures (-0.324, +0.0854) come from the SAME
           severity column: esm2_score.
    (b) the partial configs are
        '["esm2_score", "base_functionality"]' and
        '["esm2_score", "f_bar_wt"]'
        => the originally-reported 94-97%-retained spline result
           controls the SAME variable, esm2_score, as its severity
           covariate.
  VERDICT EXPECTED FROM THE SOURCE (branch 1 of C1b applies): SAME
  column, and it is delta_ESM's own project-native severity variable --
  phase5_analysis_table.csv's esm2_score = S(v|WT), the direct partner
  of delta_esm = esm2_score_a222v_bg - esm2_score.  No ProteinGym-
  sourced column exists in or is used from this table (the full column
  list is printed).  MTHFR_REVIEW_DOCUMENT.md is NOT in the repo, so
  the review's 1.3 text itself cannot be read -- the task doc's
  self-contained description governs (disclosed).

C1a FORMULA (verbatim from the task doc, no substitution):
    rho_DE.S = [rho_DE - rho_DS * rho_ES] / sqrt((1 - rho_DS^2) * (1 - rho_ES^2))
  with delta_ESM's project-native severity column esm2_score for BOTH
  rho_DS and rho_ES.  All three inputs are recomputed here at full
  precision from script 43's own analysis base and gated against the
  record's 4-dp printed values.

C1b (columns match -> first branch): RECOMPUTE the existing spline
  partial by loading script 43 itself (importlib) and calling ITS
  exact estimator functions -- not a reimplementation -- and confirm
  the record's points and ratios.  Cells, all pre-registered, none
  selected after results (own_e_b is C1's target variable; the two
  GI cells reproduce the record's full 94-114% range):
    R1  spline, own_e_b,   [esm2_score, base_functionality]   record -0.0828 / 0.940
    R2  spline, own_e_b,   [esm2_score, f_bar_wt]             record -0.0853 / 0.968
    R3  spline, GI_e_b,    [esm2_score, base_functionality]   record -0.0786 / 1.111
    R4  spline, GI_e_b,    [esm2_score, f_bar_wt]             record -0.0803 / 1.136
    D1  spline, own_e_b,   [esm2_score] only                  DIAGNOSTIC (covariate-count control)
    L1  LINEAR, own_e_b,   severity only (task formula)       PRIMARY C1a (expect ~73%)
    L2  LINEAR, own_e_b,   severity + base_functionality      DIAGNOSTIC (2-covariate extension)
    L3  LINEAR, own_e_b,   severity + f_bar_wt                DIAGNOSTIC (2-covariate extension)
  L2/L3 use the standard two-covariate linear partial obtained by
  matrix inversion of the Spearman correlation matrix (the textbook
  extension of the task's 1-covariate formula -- labeled as such, not
  presented as the task's formula).  The 2x2 comparison
  (form x covariate-set) RESOLVES the discrepancy: D1 vs L1 isolates
  functional form at severity-only; R1 vs L2 isolates it at
  severity+w.fitness; D1 vs R1 and L1 vs L2 isolate the covariate
  count.  Retention ratio for every cell = |partial| / |raw rho|
  (own raw = rho(delta, own_e_b), gated at -0.08811806424891734).

INFERENCE: R1-R4 and D1 carry script 43's own position-cluster
  bootstrap CIs (nuisance refit inside every draw, seed 0, N_BOOT env
  default 10000 to match the record's full run).  L1 additionally gets
  a position-cluster bootstrap CI computed here (all three rhos
  re-derived fresh per draw; same convention) so the 73%-vs-94%
  comparison carries uncertainty.  L2/L3 are diagnostic points WITHOUT
  CIs (pre-registered; disclosed in output).

GATES (failure -> print exact mismatch, sys.exit(1); no retries, no
threshold changes):
  G1 analysis base reproduces script 43's: n=10,757 / 654 positions.
  G2 rho(delta, own_e_b) on this base == -0.08811806424891734
     (abs tol 1e-9) -- reconciles script 43's base with the headline
     task32 value (two-source check, AGENTS sec 5).
  G3 rho(delta, esm2_score) rounds to -0.3238 AND
     rho(own_e_b, esm2_score) rounds to +0.0854 (the record's 4 dp,
     OVERNIGHT_LOG B1a raw-correlations block).
  G4 script 43's source contains the two asserted substrings (C1a
     column-identity evidence).
  G5 R1-R4 point partials and ratios reproduce the record exactly at
     its printed precision (round-4 for points, round-3 for ratios):
     -0.0828/0.940, -0.0853/0.968, -0.0786/1.111, -0.0803/1.136.
     (Reproduction of the record's own numbers is a UNIT TEST of
     implementation consistency -- AGENTS sec 6 -- not independent
     evidence.)

C1c REPORTING RULES (pre-registered):
  * "Corrected retention percentage" is stated plainly from the printed
    cells: if G5 passes, the 94-97% figure is NOT an error and is
    restated with its precise definition (spline, ranks, TWO covariates
    = severity + w.fitness, nuisance refit per draw); the linear
    severity-only retention (L1) is stated alongside as the figure it
    was compared against, and the decomposition (L1/D1/R1/L2) states
    which factor -- functional form or covariate count -- accounts for
    the gap, whichever way it falls.
  * "Update any internal note that cited the original 94-97% figure":
    the script PRINTS a file:line inventory of every doc citing it
    (tier 1: the retention phrases; tier 2: the raw ratio numbers).
    Binding conflict flagged up front: this session's rules forbid
    editing prior-session logs and RESULTS.md, and if every citer is a
    prior-session log, the "update" cannot be executed -- AGENTS sec 9
    (this file wins, flag the conflict) -> the corrections are
    delivered as flagged replacement text in PHASE1_LOG.md instead.

LIMITATIONS (printed with the output, AGENTS sec 6):
  - MTHFR_REVIEW_DOCUMENT.md absent from the repo: section 1.3's exact
    wording cannot be verified; the task doc's description is used.
  - The record's "spline/cross-fit" wording: script 43 is NOT k-fold
    cross-fit -- it refits the spline nuisance model INSIDE every
    bootstrap draw.  Stated; the recomputation targets exactly that
    existing estimator.
  - The spline controls smooth nonlinearity only (df=4 on ranks).
  - All partials are rank-based (Spearman semantics); the linear cells
    are linear partials OF RANKS.
  - Reproducing the record's four cells validates the code, not the
    claim (reproduction is not replication).

Usage:
  N_BOOT=200   venv/bin/python3 scripts/112_c1_severity_partial_reconciliation.py  # smoke
  N_BOOT=10000 venv/bin/python3 scripts/112_c1_severity_partial_reconciliation.py  # full
"""

import importlib.util
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROC = ROOT / "data" / "processed"
S43_PATH = ROOT / "scripts" / "43_flattening_partial.py"
OUT = PROC / "task112_severity_partial.csv"
DOCS = ROOT / "docs"

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
RAW_OWN = -0.08811806424891734
REC = {  # record's printed precision (OVERNIGHT_LOG B1a / GROUPS digest)
    "rho_ds": -0.3238, "rho_es": 0.0854,
    "R1": (-0.0828, 0.940), "R2": (-0.0853, 0.968),
    "R3": (-0.0786, 1.111), "R4": (-0.0803, 1.136),
}
ASSERT_SUBSTRINGS = [
    'for z in ["esm2_score", "base_functionality", "f_bar_wt"]',
    '["esm2_score", "base_functionality"]',
    '["esm2_score", "f_bar_wt"]',
]
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def linear_partial_1cov(r_de, r_ds, r_es):
    """The task's exact formula."""
    den = math.sqrt((1.0 - r_ds ** 2) * (1.0 - r_es ** 2))
    return (r_de - r_ds * r_es) / den


def linear_partial_2cov(r_xy, r_xz1, r_xz2, r_yz1, r_yz2, r_z1z2):
    """Standard two-covariate linear partial via matrix inversion of the
    Spearman correlation matrix (textbook extension; labeled diagnostic)."""
    rzz = np.array([[1.0, r_z1z2], [r_z1z2, 1.0]])
    if abs(np.linalg.det(rzz)) < 1e-12:
        return float("nan")
    inv = np.linalg.inv(rzz)
    xz = np.array([r_xz1, r_xz2])
    zy = np.array([r_yz1, r_yz2])
    num = r_xy - xz @ inv @ zy
    dx2 = 1.0 - xz @ inv @ xz
    dy2 = 1.0 - zy @ inv @ zy
    if dx2 <= 0 or dy2 <= 0:
        return float("nan")
    return num / (math.sqrt(dx2) * math.sqrt(dy2))


if __name__ == "__main__":
    banner("C1 -- severity-partial reconciliation (scripts/112)  "
           f"N_BOOT={N_BOOT} seed={SEED}")

    # ---- G4: C1a column-identity evidence from the producing source --
    src = S43_PATH.read_text()
    banner("C1a-GATE FIRST: column-identity check (before recomputing)", "-")
    for s in ASSERT_SUBSTRINGS:
        if s not in src:
            gfail(f"G4 FAIL: script 43 source lacks substring: {s}")
    print("  G4 PASS: script 43 source contains the asserted blocks:")
    for s in ASSERT_SUBSTRINGS:
        print(f"    {s}")
    print("  EVIDENCE (verbatim from scripts/43_flattening_partial.py):")
    print('    for z in ["esm2_score", "base_functionality", "f_bar_wt"]:')
    print('      print(f"    rho(delta, {z:26s}) = ..."'
          ' f"   rho(own_e_b, {z:20s}) = ..." ...)')
    print("    -> -0.324 and +0.0854 are printed on the SAME line of")
    print("       the SAME loop iteration (z = esm2_score).")
    print("  ANSWER (task C1a, stated explicitly): the two prior")
    print("  figures -0.324 (rho(delta, esm2_score)) and +0.0854")
    print("  (rho(own_e_b, esm2_score)) came from the SAME severity")
    print("  column -- esm2_score -- and it is the SAME variable the")
    print("  94-97%-retained spline result controls as its severity")
    print("  covariate.  SAME column; branch 1 of C1b applies.")
    print("  esm2_score is project-native: delta_esm =")
    print("  esm2_score_a222v_bg - esm2_score (its direct partner);")
    print("  no ProteinGym-sourced column is used (full phase5 column")
    print("  list below).")
    ph5_cols = pd.read_csv(PROC / "phase5_analysis_table.csv",
                           nrows=0).columns.tolist()
    print(f"    phase5 columns: {ph5_cols}")
    if "MTHFR_REVIEW_DOCUMENT.md" not in [p.name for p in ROOT.glob("*.md")]:
        print("  NOTE: MTHFR_REVIEW_DOCUMENT.md is NOT in the repo --")
        print("  review 1.3's exact wording unverifiable; the task doc's")
        print("  self-contained description governs (disclosed).")

    # ---- load script 43's OWN estimator (not a reimplementation) ----
    spec = importlib.util.spec_from_file_location("s43", S43_PATH)
    s43 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s43)

    # ---- G1/G2/G3: analysis base + raw rhos --------------------------
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left")
    base = df.dropna(subset=["delta_esm", "own_e_b",
                             "GI_folinate_independent",
                             "esm2_score", "base_functionality"]).copy()
    n, npos = len(base), base["position"].nunique()
    if (n, npos) != (10757, 654):
        gfail(f"G1 FAIL: base n={n} positions={npos}, expected 10757/654")
    print(f"\n  G1 PASS: script 43's base reproduces: {n} variants / "
          f"{npos} positions")

    r_de = float(s43._spearman(base["delta_esm"], base["own_e_b"]))
    if not math.isclose(r_de, RAW_OWN, abs_tol=1e-9):
        gfail(f"G2 FAIL: rho(delta, own_e_b)={r_de!r} vs headline "
              f"{RAW_OWN!r} (two bases disagree -- stop, AGENTS 5)")
    r_ds = float(s43._spearman(base["delta_esm"], base["esm2_score"]))
    r_es = float(s43._spearman(base["own_e_b"], base["esm2_score"]))
    r_gi_raw = float(s43._spearman(base["delta_esm"],
                                   base["GI_folinate_independent"]))
    if round(r_ds, 4) != REC["rho_ds"]:
        gfail(f"G3 FAIL: rho_DS {r_ds!r} != {REC['rho_ds']} (4 dp)")
    if round(r_es, 4) != REC["rho_es"]:
        gfail(f"G3 FAIL: rho_ES {r_es!r} != {REC['rho_es']} (4 dp)")
    print(f"  G2 PASS: rho(delta, own_e_b) = {r_de!r} == headline")
    print(f"  G3 PASS: rho_DS = {r_ds!r} (record -0.3238), "
          f"rho_ES = {r_es!r} (record +0.0854) -- full precision, same"
          f" esm2_score column")

    # ---- L1: the task's linear partial + its bootstrap CI ------------
    l1 = linear_partial_1cov(r_de, r_ds, r_es)
    rng = np.random.default_rng(SEED)
    pos = base["position"].to_numpy()
    uniq = np.unique(pos)
    idx_by = {c: np.flatnonzero(pos == c) for c in uniq}
    xd = base["delta_esm"].to_numpy()
    yd = base["own_e_b"].to_numpy()
    sd = base["esm2_score"].to_numpy()
    l1_boot = np.empty(N_BOOT)
    for b in range(N_BOOT):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        a = float(s43._spearman(xd[i], yd[i]))
        c1 = float(s43._spearman(xd[i], sd[i]))
        c2 = float(s43._spearman(yd[i], sd[i]))
        l1_boot[b] = linear_partial_1cov(a, c1, c2)
    l1_lo, l1_hi = np.nanpercentile(l1_boot, [2.5, 97.5])
    l1_ratio = abs(l1) / abs(r_de)
    banner("C1a -- LINEAR PARTIAL (task's exact formula)", "-")
    print(f"  inputs (full precision, esm2_score):")
    print(f"    rho_DE = {r_de!r}")
    print(f"    rho_DS = {r_ds!r}")
    print(f"    rho_ES = {r_es!r}")
    print(f"  rho_DE.S = [rho_DE - rho_DS*rho_ES] / "
          f"sqrt((1-rho_DS^2)(1-rho_ES^2))")
    print(f"           = {l1!r}")
    print(f"  retention |partial|/|raw| = {l1_ratio:.3f} "
          f"({l1_ratio * 100:.1f}%)")
    print(f"  position-cluster bootstrap CI (rhos re-derived per draw, "
          f"{N_BOOT} draws): [{l1_lo!r}, {l1_hi!r}]")

    # ---- R1-R4 + D1: the EXISTING spline estimator -------------------
    banner("C1b -- RECOMPUTED SPLINE PARTIAL (script 43's own "
           "estimator via importlib)", "-")
    cells = []
    cfg = [("R1", "own_e_b", ["esm2_score", "base_functionality"]),
           ("R2", "own_e_b", ["esm2_score", "f_bar_wt"]),
           ("R3", "GI_folinate_independent",
            ["esm2_score", "base_functionality"]),
           ("R4", "GI_folinate_independent", ["esm2_score", "f_bar_wt"]),
           ("D1", "own_e_b", ["esm2_score"])]
    raw_of = {"own_e_b": r_de, "GI_folinate_independent": r_gi_raw}
    for tag, eb, zcols in cfg:
        res = s43.partial_bootstrap(base, "delta_esm", eb, zcols,
                                    N_BOOT, SEED)
        ratio = abs(res["partial_rho"]) / abs(raw_of[eb])
        cells.append(dict(tag=tag, kind="spline", eb=eb,
                          controls="+".join(zcols),
                          partial=res["partial_rho"], ci_lo=res["ci_lo"],
                          ci_hi=res["ci_hi"], p_boot=res["p_boot"],
                          ratio=ratio, n=res["n_rows"],
                          n_clusters=res["n_clusters"]))
        print(f"  {tag} spline | {eb:26s} | ctrl "
              f"{'+'.join(zcols)}"
              f" -> partial={res['partial_rho']:+.4f} "
              f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}] "
              f"ratio={ratio:.3f} n={res['n_rows']}/{res['n_clusters']}pos")
    # G5 record reproduction
    for tag in ["R1", "R2", "R3", "R4"]:
        cell = next(c for c in cells if c["tag"] == tag)
        rp, rr = REC[tag]
        if round(cell["partial"], 4) != rp or round(cell["ratio"], 3) != rr:
            gfail(f"G5 FAIL: {tag} partial {cell['partial']!r} ratio "
                  f"{cell['ratio']!r} vs record {rp}/{rr}")
    print("  G5 PASS: R1-R4 reproduce the record exactly at its printed "
          "precision (-0.0828/0.940, -0.0853/0.968, -0.0786/1.111, "
          "-0.0803/1.136)")

    # ---- L2/L3 diagnostics (two-covariate linear) ---------------------
    banner("C1b-DIAGNOSTICS -- LINEAR 2-COVARIATE CELLS (matrix-inversion "
           "extension; points only, no CI by pre-registration)", "-")
    vars_ = {"delta": base["delta_esm"].to_numpy(),
             "own": base["own_e_b"].to_numpy(),
             "sev": base["esm2_score"].to_numpy(),
             "bf": base["base_functionality"].to_numpy(),
             "fw": base["f_bar_wt"].to_numpy()}
    R = {}
    keys = list(vars_)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            R[(keys[i], keys[j])] = float(
                s43._spearman(vars_[keys[i]], vars_[keys[j]]))
            R[(keys[j], keys[i])] = R[(keys[i], keys[j])]

    l2 = linear_partial_2cov(R[("delta", "own")], R[("delta", "sev")],
                             R[("delta", "bf")], R[("own", "sev")],
                             R[("own", "bf")], R[("sev", "bf")])
    l3 = linear_partial_2cov(R[("delta", "own")], R[("delta", "sev")],
                             R[("delta", "fw")], R[("own", "sev")],
                             R[("own", "fw")], R[("sev", "fw")])
    for tag, val, ctl in [("L2", l2, "esm2_score+base_functionality"),
                          ("L3", l3, "esm2_score+f_bar_wt")]:
        cells.append(dict(tag=tag, kind="linear", eb="own_e_b",
                          controls=ctl, partial=val, ci_lo=np.nan,
                          ci_hi=np.nan, p_boot=np.nan,
                          ratio=abs(val) / abs(r_de), n=n,
                          n_clusters=npos))
        print(f"  {tag} linear | own_e_b                    | ctrl {ctl}"
              f" -> partial={val:+.4f} ratio={abs(val) / abs(r_de):.3f}"
              f" (point only)")
    cells.append(dict(tag="L1", kind="linear", eb="own_e_b",
                      controls="esm2_score", partial=l1, ci_lo=l1_lo,
                      ci_hi=l1_hi, p_boot=np.nan, ratio=l1_ratio, n=n,
                      n_clusters=npos))

    # ---- resolution decomposition -------------------------------------
    banner("C1 -- RESOLUTION (form x covariate-set decomposition, "
           "own_e_b)", "-")
    d1 = next(c for c in cells if c["tag"] == "D1")
    r1 = next(c for c in cells if c["tag"] == "R1")
    print(f"  L1 linear  sev only        : {l1:+.4f}  ratio "
          f"{l1_ratio:.3f}")
    print(f"  D1 spline  sev only        : {d1['partial']:+.4f}  ratio "
          f"{d1['ratio']:.3f}")
    print(f"  L2 linear  sev+w.fitness   : {l2:+.4f}  ratio "
          f"{abs(l2) / abs(r_de):.3f}")
    print(f"  R1 spline  sev+w.fitness   : {r1['partial']:+.4f}  ratio "
          f"{r1['ratio']:.3f}")
    print(f"  form effect at sev-only      (D1 - L1) = "
          f"{d1['partial'] - l1:+.4f}")
    print(f"  form effect at sev+wfitness  (R1 - L2) = "
          f"{r1['partial'] - l2:+.4f}")
    print(f"  covariate effect, spline     (R1 - D1) = "
          f"{r1['partial'] - d1['partial']:+.4f}")
    print(f"  covariate effect, linear     (L2 - L1) = "
          f"{l2 - l1:+.4f}")

    # ---- C1c: corrected retention + note-citation inventory ------------
    banner("C1c -- CORRECTED RETENTION, STATED PLAINLY", "-")
    print(f"  The 94-97% figure is NOT an error: the existing spline"
          f" partial (ranks, TWO covariates = severity + w.fitness,"
          f" nuisance refit per draw) retains {r1['ratio'] * 100:.1f}%"
          f" (R1) and {next(c for c in cells if c['tag'] == 'R2')['ratio'] * 100:.1f}%"
          f" (R2) of the raw own_e_b correlation -- confirmed by"
          f" re-running script 43's own estimator (G5).")
    print(f"  The plain LINEAR partial with severity only (the task's"
          f" exact formula) retains {l1_ratio * 100:.1f}% (L1).")
    print(f"  Both numbers are correct FOR THEIR OWN CELL; the"
          f" decomposition above states which factor (functional form"
          f" vs covariate count) accounts for the gap -- see cells.")
    tier1, tier2 = [], []
    pats1 = ["94\u201397", "94-97", "retains 94", "retained 94"]
    pats2 = ["0.940", "0.968"]
    for p in sorted(DOCS.rglob("*.md")):
        for ln, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            if any(s in line for s in pats1):
                tier1.append(f"{p.relative_to(ROOT)}:{ln}")
            elif any(s in line for s in pats2):
                tier2.append(f"{p.relative_to(ROOT)}:{ln}")
    print("  NOTE-CITATION INVENTORY (tier 1 = retention phrase):")
    for t in tier1:
        print(f"    {t}")
    print("  tier 2 = raw ratio numbers (weaker signal):")
    for t in tier2:
        print(f"    {t}")
    res_md = ROOT / "RESULTS.md"
    cites = []
    if res_md.exists():
        txt = res_md.read_text()
        cites = [s for s in pats1 + pats2 if s in txt]
    print(f"  RESULTS.md cites any of these: {bool(cites)} {cites} "
          f"(RESULTS.md is OFF-LIMITS this session -- flag only)")
    prior_logs = [t for t in tier1
                  if any(k in t for k in ("OVERNIGHT_LOG", "DEEPDIVE_LOG",
                                          "SESSION_LOG", "GROUPS_C_TO_H",
                                          "CLOSEOUT_LOG", "REVIEW_RESPONSE",
                                          "C1_PRIME_LOG", "PHASE1_LOG"))]
    others = [t for t in tier1 if t not in prior_logs]
    print(f"  PRIOR-SESSION LOGS citing (never editable this session): "
          f"{len(prior_logs)}")
    print(f"  NON-LOG citers needing update if any: {others if others else 'NONE'}")

    # ---- write CSV -----------------------------------------------------
    pd.DataFrame([dict(section="c1a", key="rho_de", value=r_de),
                  dict(section="c1a", key="rho_ds", value=r_ds),
                  dict(section="c1a", key="rho_es", value=r_es),
                  dict(section="c1a", key="linear_partial_L1", value=l1),
                  dict(section="c1a", key="L1_ci_lo", value=l1_lo),
                  dict(section="c1a", key="L1_ci_hi", value=l1_hi),
                  dict(section="c1a", key="L1_ratio", value=l1_ratio)]
                 ).to_csv(OUT, index=False)
    pd.DataFrame(cells).to_csv(OUT.with_name(
        "task112_severity_partial_cells.csv"), index=False)

    banner("LIMITATIONS (AGENTS 6)", "-")
    print("  1. MTHFR_REVIEW_DOCUMENT.md not in repo: section 1.3's")
    print("     wording unverifiable; task doc's description used.")
    print("  2. 'cross-fit' in the task wording: script 43 refits its")
    print("     spline nuisance per bootstrap draw; it is not k-fold")
    print("     cross-fit.  The recomputation targets that estimator.")
    print("  3. Spline controls smooth nonlinearity only (df=4, ranks).")
    print("  4. All partials are rank-based; L2/L3 are diagnostic")
    print("     points without CIs (pre-registered).")
    print("  5. G5 reproduction validates the code, not the claim.")
    print(f"\nWrote {OUT} and task112_severity_partial_cells.csv")
    print(f"SCRIPT 112 DONE ({time.time() - T0:.1f}s)")
