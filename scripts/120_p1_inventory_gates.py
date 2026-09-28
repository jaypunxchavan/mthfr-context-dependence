"""Script 120 (Phase 1b, task P1) -- inventory, provenance, and
reproduction gates. READ-ONLY over the real files; writes nothing.
PRE-REGISTERED: this docstring was written before the first run of this
script (PHASE1B_PLACEBO_FOLLOWUP.md, Part A, task P1).

SCOPE (no new inference):
  P1 computes no bootstrap and no new statistic beyond re-deriving
  recorded values.  N_BOOT/SEED are read per the session convention but
  are UNUSED: there is nothing stochastic in P1, so the mandated
  N_BOOT=300 smoke run and N_BOOT=10000 full run produce identical output
  apart from the banner label; both are executed anyway (disclosed).

PRE-REGISTERED CHECKS (thresholds fixed by the task doc; a failed gate
prints `GATE FAIL: ...` and exits 1 -> P1 is logged FAIL/BLOCKED; no
retry, no threshold change, no reference value edited):

  ROSTER (task P1(a)): parse the 57 AE-frame bg_ids from
    task109_placebo_rhos.csv (frame == 'AE'): '__A222V__' -> target
    (position 222); 'A222_X' -> site placebo (gate: X not in {A, V});
    'AV_<p>' -> AE2 (position p).  Gate: 18 site placebos + 1 target +
    38 AE2 = 57; all 38 AV positions distinct and none is 222; for all
    38 AE2 backgrounds the WT residue (esm2_wt_scores.csv wt_aa at that
    position) is 'A' -- any non-Ala is printed and fails the gate.
    Cross-check (informational, task allows "either source"): the
    wild-type FASTA data/raw/P42898.fasta with mapping fasta[p-1] == wt
    at position p; agreement over ALL 12,445 rows of esm2_wt_scores.csv
    is printed (12445/12445 expected; if the global mapping disagreed,
    the FASTA check would be reported as unavailable rather than used to
    fail the roster -- the table wt_aa is the primary source).

  PROVENANCE (task P1(b)): the selection rules are read from
    scripts/82_ae_position_vs_identity.py (lines 24-47, 68-75, 226-228)
    and scripts/69_w_decile_background_rescore.py (lines 23-50) at
    RUNTIME and printed verbatim with line numbers -- never retyped.
    Pre-registered flag rule (mechanical, so it cannot be omitted by
    judgment): scan each quoted rule for the keywords
    `esm2_score`, `fitness`, `severity`, `damaging`, `decile`, `own_e`
    (case-insensitive).  Any hit prints a prominent FLAG for that
    selection, with this pre-registered reading: the W-series rule is
    score-based if and only if its own text says so -- the flag states
    that the 30 backgrounds were chosen by deciles of the MODEL's own
    severity column (esm2_score, i.e. ESM-2's WT-background log-prob
    severity), NOT by measured fitness (own_e_b) and NOT by rho_b; it
    bears on how W may be used as a null (severity-stratified by
    design).  No hit prints "no score/fitness keyword in the quoted
    rule" for that script.

  G1  task109_placebo_rhos.csv has exactly 175 rows; exactly 57 rows
      with frame == 'AE'.

  G2  Recompute rho_b for all 57 AE backgrounds from the raw caches --
      a line-for-line replication of scripts/109's AE-frame code:
      task82_ae_raw.csv joined to esm2_wt_scores.csv on
      (position, mut_aa) (0 nulls), delta = score_bg - esm2_score,
      backgrounds 'A222_*' and 'AV_*' kept, cache 'A222_V' re-labelled
      '__A222V__' (never a placebo), merged with own_context_metrics.csv
      on hgvs_pro, own_e_b non-null kept, G6 drop of rows whose target
      position equals that background's own position (count printed),
      Spearman(delta, own_e_b) per background.  Gate: max |diff| vs the
      CSV's AE-frame rho < 1e-9 across all 57.

  G3  Recorded-value comparisons from the task doc's Phase 1 table,
      each gated within 1e-6 (the doc quotes 6 dp -> rounding error at
      most 5e-7):
        A222V AE rho vs -0.104322 (from the frame=='AE', is_a222v row);
        AE1 mean over exactly n=18 rows (frame 'AE', bg_id A222_*) vs
          -0.055209 (both the value and n=18 are gated);
        AE2 mean over exactly n=38 rows (frame 'AE', bg_id AV_*) vs
          -0.010138 (value and n=38 gated).
      REPORTED, NOT gated (the task doc's G3 names only the three
      values above): W-frame A222V rho vs -0.072547, COMMON-frame
      A222V rho vs -0.104044, AE 56-placebo mean vs -0.024625 --
      printed side by side with the doc values.

  G4  Full-frame anchor: Spearman(delta_esm, own_e_b) on
      data/processed/task32_analysis_table.csv after dropna on both
      columns must equal -0.088118 within 1e-6; the full-precision
      recorded value -0.08811806424891734, the row count (expected
      10,757) and the distinct-position count (expected 654) are also
      printed (the task doc's table states all three).

  GRANTHAM GATE (task P1(d)): run the literal command
    grep -rn -i grantham scripts/lib
    (subprocess, cwd=repo root; output printed verbatim; grep exit != 0
    -> absent -> P3's primary metric BLOCKED, printed, no replacement
    improvised).  Implementation used: scripts/lib/features.py grantham.
    Verify published Grantham (1974) values A-V 64, I-V 29, L-V 32,
    L-I 5, F-Y 22, C-W 215, each within 1.0 of published; symmetry
    |g(a,b) - g(b,a)| < 1e-12 for all 20x20 ordered pairs; zero diagonal
    g(a,a) == 0.0 for all 20.
    TOLERANCE PRE-REGISTRATION (before running): the published table is
    integer-rounded and features.py's own docstring documents "max
    deviation 0.87 (the published table is integer-rounded)" against ten
    published values, so agreement at the table's precision is |diff| <=
    1.0.  This tolerance was set from that documented verification
    BEFORE this script's first run; the six pairs were additionally
    hand-checked against the published formula while writing this
    docstring (deterministic evaluations of published constants, not
    analysis results) to confirm 1.0 characterizes integer-rounding
    rather than implementation error.  A wrong implementation -- e.g.
    this project's earlier one, with the constants inside the square
    root -- misses by far more than 1.0.  If absent or any value fails:
    P3's primary metric is BLOCKED (printed as such).

LIMITATIONS (printed with the output, AGENTS 6):
  * read-only reproduction of recorded values; cached files only; no
    model scoring, no torch/esm import, no new inference in P1.
  * P1's gates re-derive Phase 1 numbers from Phase 1's own outputs and
    raw caches -- reproduction of the code path, not independent
    replication of the science (AGENTS 6).
  * P2/P3/P4 remain exploratory regardless of P1's outcome.

Usage (session convention; both runs executed, identical apart from the
banner label, as disclosed above):
  N_BOOT=300   venv/bin/python3 scripts/120_p1_inventory_gates.py   # smoke
  N_BOOT=10000 venv/bin/python3 scripts/120_p1_inventory_gates.py   # full
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = int(os.environ.get("SEED", "0"))
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DOC_TABLE = {
    "a222v_ae": -0.104322,
    "ae_placebos_mean": -0.024625,
    "ae1_mean": -0.055209,
    "ae2_mean": -0.010138,
    "a222v_w": -0.072547,
    "a222v_common": -0.104044,
}
ANCHOR_DOC = -0.088118
ANCHOR_FULL = -0.08811806424891734
TOL_1E6 = 1e-6
GRANTHAM_PUB = {"A-V": 64, "I-V": 29, "L-V": 32, "L-I": 5, "F-Y": 22, "C-W": 215}
GRANTHAM_TOL = 1.0          # pre-registered, see docstring
KEYWORDS = ["esm2_score", "fitness", "severity", "damaging", "decile", "own_e"]

t0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def quote_lines(path, lo, hi, label):
    """Print lines lo..hi (1-based, inclusive) of path verbatim, numbered."""
    src = (ROOT / path).read_text().splitlines()
    print(f"  --- {label}: {path} lines {lo}-{hi} (verbatim) ---")
    for i in range(lo, min(hi, len(src)) + 1):
        print(f"  {i:4d}: {src[i - 1]}")
    return [src[i - 1] for i in range(lo, min(hi, len(src)) + 1)]


def keyword_scan(label, lines_with_nums):
    """Mechanical pre-registered scan; returns hit dict."""
    hits = {}
    for ln, text in lines_with_nums:
        low = text.lower()
        for kw in KEYWORDS:
            if kw.lower() in low:
                hits.setdefault(kw, []).append(ln)
    if hits:
        print(f"  !! FLAG (P1b): selection rule for {label} contains "
              f"score/fitness keywords: {hits}")
        print("     Pre-registered reading: the rule is score-based iff its "
              "own text says so (above). The W-series rule is chosen by "
              "deciles of the MODEL's own severity column (esm2_score, "
              "ESM-2's WT-background log-prob severity), NOT by measured "
              "fitness (own_e_b) and NOT by rho_b. It bears on how the "
              "group may be used as a null: severity-stratified by design.")
    else:
        print(f"  No score/fitness keyword in the quoted rule for {label} "
              f"(mechanical scan of {len(lines_with_nums)} lines over "
              f"{KEYWORDS}).")
    return hits


if __name__ == "__main__":
    banner("P1 -- inventory, provenance, reproduction gates (script 120)  "
           f"N_BOOT={N_BOOT} SEED={SEED} (no bootstrap: deterministic)")

    # ---------------------------------------------------------- roster ----
    banner("P1(a) ROSTER of the 57 AE backgrounds", "-")
    rec = pd.read_csv(ROOT / "data/processed/task109_placebo_rhos.csv")
    ae = rec[rec.frame == "AE"].copy()
    site, ae2, target = [], [], []
    for b in sorted(ae.bg_id):
        if b == "__A222V__":
            target.append(b)
        elif b.startswith("A222_"):
            site.append(b)
        elif b.startswith("AV_"):
            ae2.append(b)
        else:
            gfail(f"roster: unclassifiable bg_id {b!r}")
    print(f"  site placebos (A222_X, X not in {{A,V}}): n={len(site)}")
    print(f"  target A222V (__A222V__): n={len(target)}")
    print(f"  AE2 (AV_<pos>): n={len(ae2)}")
    if len(site) != 18 or len(target) != 1 or len(ae2) != 38 or len(ae) != 57:
        gfail(f"roster sizes: site={len(site)} target={len(target)} "
              f"AE2={len(ae2)} AE_rows={len(ae)}")
    bad_suffix = [b for b in site if b.split("_")[1] in ("A", "V")]
    if bad_suffix:
        gfail(f"roster: site placebo with X in {{A,V}}: {bad_suffix}")
    av_pos = [int(b.split("_")[1]) for b in ae2]
    if len(set(av_pos)) != 38 or 222 in av_pos:
        gfail(f"roster: AV positions distinct={len(set(av_pos))} "
              f"contains_222={222 in av_pos}")

    wt = pd.read_csv(ROOT / "data/processed/esm2_wt_scores.csv")
    wt_by_pos = wt.groupby("position").wt_aa.first().to_dict()
    seq = "".join(l.strip() for l in
                  open(ROOT / "data/raw/P42898.fasta") if not l.startswith(">"))
    agree_all = int(sum(seq[int(p) - 1] == w for p, w in
                        wt.groupby("position").wt_aa.first().items()))
    print(f"  FASTA cross-check: fasta[p-1] == table wt_aa for "
          f"{agree_all}/{wt.position.nunique()} positions "
          f"({len(wt)} rows, positions {wt.position.min()}.."
          f"{wt.position.max()}, FASTA length {len(seq)})")

    print(f"  {'bg_id':12s} {'pos':>5s} {'wt':>3s} {'FASTA':>5s}  class")
    non_ala = []
    for b in site + ["__A222V__"] + ae2:
        p = 222 if not b.startswith("AV_") else int(b.split("_")[1])
        w = wt_by_pos.get(p, "?")
        f = seq[p - 1]
        cls = ("AE1" if b.startswith("A222_") else
               "TARGET" if b == "__A222V__" else "AE2")
        print(f"  {b:12s} {p:5d} {w:>3s} {f:>5s}  {cls}")
        if cls == "AE2" and w != "A":
            non_ala.append((b, p, w))
    if non_ala:
        gfail(f"P1(a): AE2 backgrounds whose WT residue is not Ala: {non_ala}")
    print(f"  P1(a) PASS: 38/38 AE2 positions have WT residue Ala "
          f"(esm2_wt_scores.csv; FASTA mapping "
          f"{'confirmed' if agree_all == wt.position.nunique() else 'UNAVAILABLE'}")

    # ------------------------------------------------------ provenance ----
    banner("P1(b) SELECTION PROVENANCE (verbatim quotes, read at runtime)", "-")
    q82a = quote_lines("scripts/82_ae_position_vs_identity.py", 24, 47,
                       "AE selection: AE1/AE2 definitions + subset rule + scoring")
    q82b = quote_lines("scripts/82_ae_position_vs_identity.py", 68, 75,
                       "script 82 gates (FASTA/shape provenance)")
    q82c = quote_lines("scripts/82_ae_position_vs_identity.py", 226, 228,
                       "script 82 bg_id construction")
    q69 = quote_lines("scripts/69_w_decile_background_rescore.py", 23, 50,
                      "W-series selection rule (W1)")
    num = lambda lines, lo: [(lo + i, s) for i, s in enumerate(lines)]
    hits_ae = keyword_scan("the AE grid/AE2 rule (script 82)",
                           num(q82a, 24) + num(q82b, 68) + num(q82c, 226))
    hits_w = keyword_scan("the W-series rule (script 69)", num(q69, 23))

    # -------------------------------------------------------------- G1 ----
    banner("P1(c) REPRODUCTION GATES", "-")
    n_rows, n_ae = len(rec), len(ae)
    print(f"  [G1] task109_placebo_rhos.csv rows={n_rows} (expect 175), "
          f"frame==AE rows={n_ae} (expect 57)")
    if n_rows != 175 or n_ae != 57:
        gfail(f"G1: rows={n_rows} AE rows={n_ae}")
    print("  G1 PASS")

    # -------------------------------------------------------------- G2 ----
    own = pd.read_csv(ROOT / "data/processed/own_context_metrics.csv")[
        ["hgvs_pro", "own_e_b"]]
    aej = wt[["position", "mut_aa", "hgvs_pro", "esm2_score"]].pipe(
        lambda d: pd.read_csv(ROOT / "data/processed/task82_ae_raw.csv")
        .merge(d, on=["position", "mut_aa"], how="left"))
    n_null = int(aej[["hgvs_pro", "esm2_score"]].isna().sum().sum())
    if n_null:
        gfail(f"G2 join nulls={n_null}")
    aej["delta"] = aej.score_bg - aej.esm2_score
    av = aej[aej.bg_id == "A222_V"]
    parts = []
    for b in sorted(aej.bg_id.unique()):
        if b == "A222_V":
            continue
        sub = aej[aej.bg_id == b][["position", "hgvs_pro", "delta"]].copy()
        sub["bg_id"] = b
        parts.append(sub)
    a = av[["position", "hgvs_pro", "delta"]].copy()
    a["bg_id"] = "__A222V__"
    parts.append(a)
    lng = pd.concat(parts, ignore_index=True).merge(own, on="hgvs_pro", how="left")
    n_before = len(lng)
    lng = lng[lng.own_e_b.notna()].copy()
    # G6: drop rows whose target position equals this background's position
    dropped = 0
    keep = []
    for b in sorted(lng.bg_id.unique()):
        p = 222 if b.startswith("A222_") else (
            int(b.split("_")[1]) if b.startswith("AV_") else None)
        sub = lng[lng.bg_id == b]
        if p is None:
            keep.append(sub)
            continue
        hit = sub.position == p
        dropped += int(hit.sum())
        if hit.any():
            print(f"    [G6] {b}: dropped {int(hit.sum())} rows at position {p}")
        keep.append(sub[~hit])
    lng = pd.concat(keep, ignore_index=True)
    print(f"  [G2] recompute from raw: rows {n_before} -> own_e_b non-null "
          f"{lng.own_e_b.notna().sum()} -> after G6 drops ({dropped}) "
          f"{len(lng)}; backgrounds={lng.bg_id.nunique()}")
    diffs, per_bg = [], []
    ae_csv = ae.set_index("bg_id")
    for b in sorted(lng.bg_id.unique()):
        sub = lng[lng.bg_id == b]
        r = float(spearmanr(sub.delta, sub.own_e_b).statistic)
        rc = float(ae_csv.loc[b, "rho"])
        diffs.append(abs(r - rc))
        per_bg.append((b, r, rc, abs(r - rc)))
    for b, r, rc, d in per_bg:
        print(f"    {b:12s} rho_recomp={r:+.15f} rho_csv={rc:+.15f} "
              f"|diff|={d:.3e}")
    dmax = max(diffs)
    print(f"  [G2] max|diff| over {len(diffs)} AE backgrounds = {dmax:.3e} "
          f"(gate < 1e-9)")
    if dmax >= 1e-9:
        gfail(f"G2 max|diff| = {dmax}")
    print("  G2 PASS")

    # -------------------------------------------------------------- G3 ----
    def close(val, doc, tol=TOL_1E6):
        return abs(val - doc) < tol

    r_a222v_ae = float(ae[ae.is_a222v].rho.iloc[0])
    m_ae1 = float(ae[ae.bg_id.str.startswith("A222_")].rho.mean())
    m_ae2 = float(ae[ae.bg_id.str.startswith("AV_")].rho.mean())
    n_ae1 = int(ae.bg_id.str.startswith("A222_").sum())
    n_ae2 = int(ae.bg_id.str.startswith("AV_").sum())
    print(f"  [G3] A222V AE rho = {r_a222v_ae:+.12f} vs doc "
          f"{DOC_TABLE['a222v_ae']} (diff "
          f"{abs(r_a222v_ae - DOC_TABLE['a222v_ae']):.3e})")
    print(f"  [G3] AE1 mean = {m_ae1:+.12f} (n={n_ae1}, doc n=18) vs doc "
          f"{DOC_TABLE['ae1_mean']} (diff "
          f"{abs(m_ae1 - DOC_TABLE['ae1_mean']):.3e})")
    print(f"  [G3] AE2 mean = {m_ae2:+.12f} (n={n_ae2}, doc n=38) vs doc "
          f"{DOC_TABLE['ae2_mean']} (diff "
          f"{abs(m_ae2 - DOC_TABLE['ae2_mean']):.3e})")
    if not close(r_a222v_ae, DOC_TABLE["a222v_ae"]):
        gfail(f"G3 A222V AE rho diff = "
              f"{abs(r_a222v_ae - DOC_TABLE['a222v_ae'])}")
    if n_ae1 != 18 or not close(m_ae1, DOC_TABLE["ae1_mean"]):
        gfail(f"G3 AE1: n={n_ae1} diff="
              f"{abs(m_ae1 - DOC_TABLE['ae1_mean'])}")
    if n_ae2 != 38 or not close(m_ae2, DOC_TABLE["ae2_mean"]):
        gfail(f"G3 AE2: n={n_ae2} diff="
              f"{abs(m_ae2 - DOC_TABLE['ae2_mean'])}")
    print("  G3 PASS")
    # informational (not gated -- the task's G3 names only the three above)
    r_w = float(rec[(rec.frame == "W") & rec.is_a222v].rho.iloc[0])
    r_c = float(rec[(rec.frame == "COMMON") & rec.is_a222v].rho.iloc[0])
    m_pl = float(ae[~ae.is_a222v].rho.mean())
    n_pl = int((~ae.is_a222v).sum())
    print("  [reported, NOT gated -- task G3 lists only the three values "
          "above]:")
    print(f"    W  A222V rho = {r_w:+.9f} vs doc {DOC_TABLE['a222v_w']} "
          f"(diff {abs(r_w - DOC_TABLE['a222v_w']):.3e})")
    print(f"    COMMON A222V rho = {r_c:+.9f} vs doc "
          f"{DOC_TABLE['a222v_common']} (diff "
          f"{abs(r_c - DOC_TABLE['a222v_common']):.3e})")
    print(f"    AE 56-placebo mean = {m_pl:+.9f} (n={n_pl}) vs doc "
          f"{DOC_TABLE['ae_placebos_mean']} (diff "
          f"{abs(m_pl - DOC_TABLE['ae_placebos_mean']):.3e})")

    # -------------------------------------------------------------- G4 ----
    atlas = pd.read_csv(ROOT / "data/processed/task32_analysis_table.csv")
    use = atlas.dropna(subset=["delta_esm", "own_e_b"])
    r_anchor = float(spearmanr(use.delta_esm, use.own_e_b).statistic)
    print(f"  [G4] anchor rho = {r_anchor:.17f} | doc {ANCHOR_DOC} "
          f"(diff {abs(r_anchor - ANCHOR_DOC):.3e}) | full precision record "
          f"{ANCHOR_FULL} (diff {abs(r_anchor - ANCHOR_FULL):.3e})")
    print(f"  [G4] rows={len(use)} (doc table: 10,757), positions="
          f"{use.position.nunique()} (doc table: 654)")
    if abs(r_anchor - ANCHOR_DOC) >= TOL_1E6:
        gfail(f"G4 anchor diff = {abs(r_anchor - ANCHOR_DOC)}")
    if len(use) != 10757 or use.position.nunique() != 654:
        print(f"  [G4] NOTE: frame shape differs from the doc table "
              f"(rows={len(use)}, positions={use.position.nunique()}) -- "
              f"reported, not gated (G4 gates rho only)")
    print("  G4 PASS")

    # -------------------------------------------------------- Grantham ----
    banner("P1(d) GRANTHAM GATE (literal grep, then value checks)", "-")
    g = subprocess.run(["grep", "-rn", "-i", "grantham", "scripts/lib"],
                       cwd=str(ROOT), capture_output=True, text=True)
    print(g.stdout, end="")
    if g.stderr:
        print(g.stderr, end="")
    if g.returncode != 0:
        print("GRANTHAM ABSENT from scripts/lib -> P3's primary metric is "
              "BLOCKED. No replacement metric is improvised.")
        sys.exit(1)
    from scripts.lib.features import grantham
    print(f"  implementation: scripts/lib/features.py::grantham "
          f"(loaded OK); tolerance |value - published| <= {GRANTHAM_TOL} "
          f"(pre-registered; see docstring)")
    g_fail = []
    for pair, pub in GRANTHAM_PUB.items():
        a1, b1 = pair.split("-")
        v = float(grantham(a1, b1))
        d = abs(v - pub)
        ok = d <= GRANTHAM_TOL
        print(f"    {pair}: computed {v:.4f} vs published {pub} "
              f"|diff|={d:.4f} -> {'PASS' if ok else 'FAIL'}")
        if not ok:
            g_fail.append(f"{pair} computed {v:.4f} vs {pub}")
    aas = sorted("ARNDCQEGHILKMFPSTWY")
    sym_max = max(abs(float(grantham(a1, b1)) - float(grantham(b1, a1)))
                  for a1 in aas for b1 in aas)
    diag_max = max(abs(float(grantham(a1, a1))) for a1 in aas)
    print(f"    symmetry: max|g(a,b)-g(b,a)| over 20x20 = {sym_max:.3e} "
          f"(gate < 1e-12) -> {'PASS' if sym_max < 1e-12 else 'FAIL'}")
    print(f"    zero diagonal: max|g(a,a)| over 20 = {diag_max:.3e} "
          f"(gate == 0.0) -> {'PASS' if diag_max == 0.0 else 'FAIL'}")
    if sym_max >= 1e-12:
        g_fail.append(f"symmetry {sym_max}")
    if diag_max != 0.0:
        g_fail.append(f"diagonal {diag_max}")
    if g_fail:
        print("GRANTHAM GATE FAIL -> P3's primary metric is BLOCKED. "
              f"Failing checks: {g_fail}. No replacement metric is "
              "improvised.")
        sys.exit(1)
    print("  GRANTHAM GATE PASS: P3's primary metric (Grantham) is usable.")

    # -------------------------------------------------------- wrap-up -----
    banner("P1 SUMMARY", "-")
    print("  G1 PASS  G2 PASS (max|diff| {:.3e})  G3 PASS  G4 PASS  "
          "GRANTHAM GATE PASS".format(dmax))
    print(f"  AE roster: {len(site)} site placebos + A222V + {len(ae2)} "
          f"AE2 = {len(site) + len(ae2) + 1}")
    print("  fitness-relatedness: "
          f"AE rule keyword hits={hits_ae or 'none'}; "
          f"W rule keyword hits={hits_w or 'none'} "
          f"-> {'FLAG: W selection is score-based (see above)' if hits_w else 'no score-based selection found'}")
    print("\nLIMITATIONS (AGENTS 6):")
    print("  * read-only reproduction of recorded values from Phase 1's own")
    print("    outputs and raw caches: validates the code path, is not")
    print("    independent replication of the science.")
    print("  * cached files only; no model scoring; no torch/esm import.")
    print("  * P2/P3/P4 remain exploratory regardless of these gates.")
    print(f"Elapsed {time.time() - t0:.1f}s")
