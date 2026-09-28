#!/usr/bin/env python3
"""Script 119 -- Group L (tasks L1, L2, L3) of
docs/tasks/phase1-corrections-diagnostics/PHASE1_CORRECTIONS_AND_DIAGNOSTICS.md.

L4 (GRB2 provenance) is read-only and needs no script; it is logged
directly in PHASE1_LOG.md with quoted evidence.

PRE-REGISTRATION (written before the first run of this script; every
rule below executes exactly as written; any change made after a run is
disclosed in this docstring AND in the printed output -- AGENTS 6).

--------------------------------------------------------------------------
L1 -- Confirm position-222 rows are excluded
--------------------------------------------------------------------------
  Frame: base = task32_analysis_table.csv dropna on own_e_b,
  GI_folinate_independent, delta_esm (the 10,757-row analysis table).
  RULE: L1 PASS iff base has EXACTLY 0 rows with position == 222 AND
  task77's analysis set (finite own_e_b) has 0 rows at position 222.
  If any exist: print the count and the task's correction-needed flag
  verbatim in meaning (rank statistics and the distance analysis --
  where such rows sit at distance zero -- must not be trusted).
  Mechanics reported as DATA, no decision attached: esm_scoring.py
  returns log-odds vs THE SEQUENCE'S OWN residue at the scored
  position (`wt_aa = sequence[idx0]`; score = logP(X) - wt_score), so
  at position 222 the two arms' stored scores differ by an exact
  constant (av - wt = logP(A) - logP(V), std < 1e-12) even though the
  masked inputs are identical by construction (script 11 builds the
  A222V sequence as wt_seq[:221] + "V" + wt_seq[222:] -- identical
  apart from residue 222 -- and the scorer masks the scored position);
  script 11 deliberately writes hgvs=None at 222
  (`if pos != 222 else None`), so merged_wt_a222v (hgvs join) carries
  654 positions and 222 never enters a downstream table.  All source
  facts are asserted by READING the source files at run time; no
  model re-scoring (no heavy model work in this session).

--------------------------------------------------------------------------
L2 -- ThermoMPNN-D sign-convention audit
--------------------------------------------------------------------------
  L2a identification (pre-registered grid, fixed order): AD1's audit
  (DEEPDIVE_LOG [AD1] L509-599) did not record its amino-acid sets,
  so the sets are IDENTIFIED by exact reproduction of AD1's published
  numbers.  hydro candidates in order: H1 {A,V,I,L,M,F,W,Y};
  H2 = H1+{C}; H3 = H1+{G}; H4 = H1+{C,G}; H5 = H1+{T};
  H6 = H1+{C,T}; H7 = H1+{C,G,T}.  charged candidates: C1 {D,E,K,R};
  C2 = C1+{H}.  14 pairs, H-major.  A pair IDENTIFIES iff:
  n(Relative ASA < 0.10 & wt in H & mut in C) == 123,
  n(Relative ASA > 0.50 & same class) == 661, AND the five published
  buried statistics match at their printed precision (median 2.629,
  mean 2.684, min 0.675, max 4.501, frac>0 1.000; |diff| <= 5.1e-4).
  First identifying pair in grid order wins; ALL 14 size pairs are
  printed; a size-match whose stats fail is printed as such.  No
  pair identifies -> GATE FAIL with the table; L2a is NOT computed
  (stop per the troubleshooting tree -- no invented definition).
  The identification matches AD1's PREVIOUSLY PUBLISHED numbers only;
  no ThermoMPNN-D quantity enters it (reproducing a prior audit is a
  unit test of plumbing, not independent evidence -- AGENTS 6).
  Further identity gates (AD1 verbatim): frame == 10,141 rows; rsa
  present == 10,141; OVERALL frac ddg>0 = 0.8891, mean 1.0316,
  median 0.8571, min -1.7602, max 4.5008 (|diff| <= 5.1e-5);
  exposed(rsa>0.50) median 1.833, frac>0 0.949; the top-8 control
  rows' ddg to 1e-6 with Relative ASA == 0.0; task77 ddg == task_V2
  ddg to 0.0 on the hgvs join (one frame, two columns).
  L2a result: the SAME 123 rows, stats of ddg_single_D (n, frac>0,
  median, mean, min, max, sign counts) plus the top-8 with the D-head
  value added.  CONVENTION RULE: frac>0 >= 0.95 -> SAME convention
  (positive = destabilizing in both heads); frac>0 <= 0.05 ->
  FLIPPED in the D head; otherwise MIXED (reported as-is, no forced
  reading).
  L2b: the A222V numbers are RETRIEVED, not re-derived -- position
  222 has 0 rows in task_V2/task77 (gated in L1), so -0.0439 comes
  from DEEPDIVE_LOG [AD2] G1 (script 68's V3 output, raw SSM re-read)
  and +0.8071 from DEEPDIVE_LOG [AD4] G5 (line 2324).  VERDICT RULE:
  SAME -> the A222V disagreement is REAL (two model generations,
  same sign convention); FLIPPED -> sign-convention artifact (the
  heads agree in meaning: raw -0.0439 ~neutral/stabilizing vs D's
  flipped +0.8071 also meaning stabilizing); MIXED -> both readings
  reported, unresolved by this audit.

--------------------------------------------------------------------------
L3 -- interaction_D dynamic-range check
--------------------------------------------------------------------------
  Frame gate: task77 finite own_e_b -> (9,595 rows, 586 positions);
  ca_dist_222 finite on all 9,595.
  Identity gate: Spearman(interaction_D, own_e_b) on the full set
  must round to +0.0154 at 4 dp (AD4's logged primary, DEEPDIVE
  L2328); its CI/p are printed next to AD4's logged
  [-0.0166, +0.0465] p 0.3406 for comparison, NOT gated (CI
  endpoints depend on N_BOOT).
  Report SD (ddof=1) and IQR (q25/q75, linear) on the full set and
  on the proximal subset ca_dist_222 <= 8.0 (n always printed; n <
  30 -> subset bootstrap CI skipped and said so, per the task's "if
  a sufficient number exist").
  Ratios r_SD = SD_full/SD_prox, r_IQR = IQR_full/IQR_prox.
  LABEL RULE (pre-run convention, not derived): r_SD <= 0.5 ->
  COLLAPSES; 0.5 < r_SD < 1 -> REDUCED; r_SD >= 1 -> NOT REDUCED.
  Floor-effect probe (task-motivated, decided before running): the
  same cluster bootstrap on the proximal subset; whether its CI
  excludes 0 is reported.  L3b statement follows this rule set:
    COLLAPSES + proximal CI excludes 0 -> floor effect SUPPORTED;
        caveat recommended wherever the null is cited.
    COLLAPSES + proximal CI includes 0 -> range compression is real
        but the null persists at proximal range -> floor effect NOT
        supported by this probe; both facts stated.
    REDUCED  -> state ratios + proximal CI; caveat partial.
    NOT REDUCED -> not a floor-effect candidate by this measure.

LIMITATIONS (also printed by the script, AGENTS 6): the proximal
subset is a subset of the full set (not independent); the 0.5
collapse threshold is a pre-run convention; the A222V values are
retrieved from DEEPDIVE_LOG, not re-derived here (position 222 has
0 rows, gated); the AD1 reproduction validates plumbing only
(reproduction is not replication); the AA sets are identified from
a prior audit's printed numbers because AD1 never recorded them.

Environment: N_BOOT (default 10000), SEED=0, venv foreground only.
"""

import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.lib.stats import position_cluster_bootstrap

PROC = ROOT / "data" / "processed"
RAW_REF = ROOT / "data" / "raw" / "mthfrModel" / "reference_data"
N_BOOT = int(os.environ.get("N_BOOT", "10000"))
SEED = 0
T0 = time.time()


def gfail(msg):
    print(f"GATE FAIL: {msg}")
    sys.exit(1)


def banner(txt, ch="="):
    print("\n" + ch * 74)
    print(txt)
    print(ch * 74, flush=True)


def main():
    banner("L1/L2/L3 -- cheap verification checks (scripts/119)  "
           f"N_BOOT={N_BOOT} seed={SEED}")
    print("  L4 (GRB2 provenance) is read-only: logged directly in "
          "PHASE1_LOG.md, no script.")

    t32 = pd.read_csv(PROC / "task32_analysis_table.csv")
    t77 = pd.read_csv(PROC / "task77_thermompnnD_doubles.csv")

    # ============================ L1 ====================================
    banner("[L1] position-222 exclusion from the analysis tables", "-")
    base = t32.dropna(subset=["own_e_b", "GI_folinate_independent",
                              "delta_esm"])
    if (len(base), base["position"].nunique()) != (10757, 654):
        gfail(f"L1 frame: base is ({len(base)}, "
              f"{base['position'].nunique()}) != (10757, 654)")
    an77 = t77[t77["own_e_b"].notna()]
    if (len(an77), an77["position"].nunique()) != (9595, 586):
        gfail(f"L1 frame: task77 analysis set is ({len(an77)}, "
              f"{an77['position'].nunique()}) != (9595, 586)")
    n222_base = int((base["position"] == 222).sum())
    n222_t77 = int((t77["position"] == 222).sum())
    n222_an = int((an77["position"] == 222).sum())
    print(f"  frames: base (10757, 654) OK; task77 analysis "
          f"(9595, 586) OK")
    print(f"  rows at position 222: base = {n222_base}, "
          f"task77 all = {n222_t77}, task77 analysis = {n222_an}")
    if (n222_base, n222_t77, n222_an) != (0, 0, 0):
        print("  *** CORRECTION NEEDED (task L1a wording): "
              f"{n222_base} position-222 row(s) exist in the "
              "analysis table -- rank statistics and the distance "
              "analysis (such rows sit at distance zero) must not "
              "be trusted until they are excluded. ***")
        gfail(f"L1 FAIL: position-222 rows exist (base "
              f"{n222_base}, task77 {n222_t77}/{n222_an})")

    # -- mechanics as data (source-asserted, no re-scoring) -------------
    wt = pd.read_csv(PROC / "esm2_wt_scores.csv")
    av = pd.read_csv(PROC / "esm2_a222v_bg_scores.csv")
    if (len(wt), wt["position"].nunique()) != (12445, 655):
        gfail(f"arm wt: ({len(wt)}, {wt['position'].nunique()}) != "
              f"(12445, 655)")
    if (len(av), av["position"].nunique()) != (12445, 655):
        gfail(f"arm av: ({len(av)}, {av['position'].nunique()}) != "
              f"(12445, 655)")
    if 222 not in set(wt["position"]) or 222 not in set(av["position"]):
        gfail("L1: position 222 missing from an arm file")
    w222 = wt[wt["position"] == 222]
    a222 = av[av["position"] == 222]
    if (len(w222), len(a222)) != (19, 19):
        gfail(f"L1 arm rows at 222: wt {len(w222)} av {len(a222)} "
              f"!= 19/19")
    j222 = w222.merge(a222, on=["position", "mut_aa"])
    if len(j222) != 18:
        gfail(f"L1: {len(j222)} common (position,mut_aa) at 222 != 18")
    off = j222["esm2_score_a222v_bg"] - j222["esm2_score"]
    if float(off.std()) >= 1e-12:
        gfail(f"L1: 222 arm offset not constant, std {off.std():.3e}")
    const = float(off.mean())
    if int(a222["hgvs_pro"].isna().sum()) != 19:
        gfail("L1: av@222 hgvs not all null (expected script 11's "
              "deliberate None)")
    if int(w222["hgvs_pro"].isna().sum()) != 0:
        gfail("L1: wt@222 hgvs has nulls")
    mg = pd.read_csv(PROC / "merged_wt_a222v_scores.csv")
    if (mg["position_wt"].nunique() != 654
            or 222 in set(mg["position_wt"])):
        gfail(f"L1: merged has {mg['position_wt'].nunique()} "
              f"positions, 222 present = "
              f"{222 in set(mg['position_wt'])}")
    s11 = (ROOT / "scripts" /
           "11_score_a222v_background_esm2.py").read_text()
    for lit in ("if pos != 222 else None",
                'wt_seq[:221] + "V" + wt_seq[222:]'):
        if lit not in s11:
            gfail(f"L1: script 11 source literal not found: {lit!r}")
    ses = (ROOT / "scripts" / "lib" / "esm_scoring.py").read_text()
    for lit in ("wt_aa = sequence[idx0]", "- wt_score"):
        if lit not in ses:
            gfail(f"L1: esm_scoring source literal not found: {lit!r}")
    print("  L1 PASS: zero position-222 rows in every analysis "
          "table; no correction flag triggered.")
    print(f"    upstream mechanics (DATA, no rule attached):")
    print(f"      arm files 12,445 rows / 655 positions each "
          f"(both include 222); common mutants at 222 = 18")
    print(f"      av - wt at 222 = EXACT constant {const!r} "
          f"(std {float(off.std()):.1e}) = logP(A) - logP(V) of the "
          f"masked position: esm_scoring returns log-odds vs the "
          f"sequence's own residue (`wt_aa = sequence[idx0]`, "
          f"`log_probs[aa].item() - wt_score`), wt arm ref = A, "
          f"A222V arm ref = V, on identical masked inputs "
          f"(sequences differ only at 222: "
          f"`wt_seq[:221] + 'V' + wt_seq[222:]`)")
    print(f"      implied P(A|mask@222)/P(V|mask@222) = "
          f"exp({const:.6f}) = {float(np.exp(const)):.1f}")
    print(f"      script 11 `hgvs_pro ... if pos != 222 else None` "
          f"-> merged (hgvs join) = 654 positions -> 222 never "
          f"reaches task32/task77/any table")

    # ============================ L2 ====================================
    banner("[L2] ThermoMPNN-D sign-convention audit", "-")
    tv2 = pd.read_csv(PROC / "task_V2_thermompnn_ddg.csv")
    if len(tv2) != 10141:
        gfail(f"task_V2 rows {len(tv2)} != 10141")
    jj = tv2.merge(t77, on="hgvs_pro", suffixes=("_v2", "_77"))
    if len(jj) != 10141:
        gfail(f"task_V2 x task77 join {len(jj)} != 10141")
    dmax = float((jj["ddg_v2"] - jj["ddg_77"]).abs().max())
    if dmax != 0.0:
        gfail(f"frame equivalence: task77 ddg != task_V2 ddg, "
              f"max|diff| = {dmax}")
    print(f"  GATE frame: task77 ddg == task_V2 ddg exactly on all "
          f"10,141 hgvs (max|diff| = {dmax}) -- one frame, two "
          f"columns")

    sf = pd.read_csv(RAW_REF / "MTHFR_structural_features.csv")
    if (len(sf), sf["Position"].nunique()) != (651, 651):
        gfail(f"structural: ({len(sf)}, {sf['Position'].nunique()}) "
              f"!= (651, 651)")
    m = t77.merge(sf[["Position", "Relative ASA"]],
                  left_on="position", right_on="Position", how="left")
    if len(m) != 10141:
        gfail(f"rsa join changed row count: {len(m)} != 10141")
    n_rsa = int(m["Relative ASA"].notna().sum())
    if n_rsa != 10141:
        gfail(f"rsa present {n_rsa} != AD1's 10141")
    rsa = m["Relative ASA"]

    ov = dict(frac=float((m["ddg"] > 0).mean()),
              mean=float(m["ddg"].mean()),
              median=float(m["ddg"].median()),
              min=float(m["ddg"].min()),
              max=float(m["ddg"].max()))
    tgt_ov = dict(frac=0.8891, mean=1.0316, median=0.8571,
                  min=-1.7602, max=4.5008)
    for k, v in tgt_ov.items():
        if abs(ov[k] - v) > 5.1e-5:
            gfail(f"OVERALL {k}: {ov[k]!r} != AD1's {v} (4dp)")
    print(f"  GATE identity vs AD1's printed line: merged {len(m)} | "
          f"rsa present {n_rsa} | OVERALL frac>0 {ov['frac']:.4f} "
          f"mean {ov['mean']:.4f} median {ov['median']:.4f} "
          f"min {ov['min']:.4f} max {ov['max']:.4f}")

    HYDROS = [("H1", set("AVILMFWY")),
              ("H2", set("AVILMFWYC")),
              ("H3", set("AVILMFWYG")),
              ("H4", set("AVILMFWYCG")),
              ("H5", set("AVILMFWYT")),
              ("H6", set("AVILMFWYCT")),
              ("H7", set("AVILMFWYCGT"))]
    CHARGED = [("C1", set("DEKR")), ("C2", set("DEKRH"))]
    wt_s = m["wt_aa"]
    mut_s = m["mut_aa"]
    found = None
    print("  identification grid (pre-registered order): "
          "n_buried(rsa<0.10) / n_exposed(rsa>0.50)")
    for hn, H in HYDROS:
        for cn, C in CHARGED:
            cls = wt_s.isin(H) & mut_s.isin(C)
            nb = int(((rsa < 0.10) & cls).sum())
            ne = int(((rsa > 0.50) & cls).sum())
            tag = ""
            if (nb, ne) == (123, 661):
                sub = m[cls & (rsa < 0.10)]
                st = dict(median=float(sub["ddg"].median()),
                          mean=float(sub["ddg"].mean()),
                          min=float(sub["ddg"].min()),
                          max=float(sub["ddg"].max()),
                          frac=float((sub["ddg"] > 0).mean()))
                tgt = dict(median=2.629, mean=2.684, min=0.675,
                           max=4.501, frac=1.000)
                ok = all(abs(st[k] - tgt[k]) <= 5.1e-4
                         for k in tgt)
                if ok and found is None:
                    found = (hn, cn, H, C, sub, st)
                    tag = "  <= IDENTIFIES (sizes + stats match AD1)"
                elif not ok:
                    tag = ("  size match, stats mismatch: "
                           + " ".join(f"{k}={st[k]:.6f}"
                                      for k in tgt))
            print(f"    {hn}x{cn}  n_buried={nb:4d}  "
                  f"n_exposed={ne:4d}{tag}")
    if found is None:
        gfail("L2a IDENTIFICATION FAILED: no (hydro, charged) "
              "candidate reproduced AD1's n=123 / n=661 with all "
              "five published statistics -- L2a NOT computed "
              "(stopped per pre-registration; no definition invented)")
    hn, cn, H, C, sub, st = found
    print(f"  L2a IDENTIFIED: hydro={hn} {{{''.join(sorted(H))}}} "
          f"charged={cn} {{{''.join(sorted(C))}}} (first match in "
          f"grid order)")
    print(f"    buried(rsa<0.10) hydro->charged n={len(sub)}: "
          f"median={st['median']:.3f} mean={st['mean']:.3f} "
          f"min={st['min']:.3f} max={st['max']:.3f} "
          f"frac>0={st['frac']:.3f}  == AD1's printed line")
    expo = m[(wt_s.isin(H) & mut_s.isin(C)) & (rsa > 0.50)]
    if len(expo) != 661:
        gfail(f"exposed class n {len(expo)} != 661")
    if (abs(float(expo["ddg"].median()) - 1.833) > 5.1e-4
            or abs(float((expo["ddg"] > 0).mean()) - 0.949) > 5.1e-4):
        gfail(f"exposed stats: median "
              f"{float(expo['ddg'].median()):.6f} frac "
              f"{float((expo['ddg'] > 0).mean()):.6f} != AD1's "
              f"1.833 / 0.949")
    print(f"    EXPOSED(rsa>0.50) same class n={len(expo)}: "
          f"median={expo['ddg'].median():.3f} "
          f"frac>0={(expo['ddg'] > 0).mean():.3f} == AD1 "
          f"(n=661, 1.833, 0.949)")

    TOP8 = [("p.Ala113Arg", 2.226977), ("p.Phe516Glu", 3.497138),
            ("p.Phe516Asp", 4.066879), ("p.Phe516Arg", 3.229506),
            ("p.Leu621Glu", 2.588402), ("p.Leu621Asp", 3.039570),
            ("p.Leu621Arg", 2.680789), ("p.Leu618Lys", 2.908469)]
    if sub["hgvs_pro"].duplicated().any():
        gfail("L2a: duplicate hgvs in the identified set")
    idx8 = sub.set_index("hgvs_pro")
    for h, v in TOP8:
        if h not in idx8.index:
            gfail(f"top-8 control {h} not in the identified set")
        r = idx8.loc[h]
        if abs(float(r["ddg"]) - v) > 1e-6:
            gfail(f"top-8 {h}: ddg {r['ddg']!r} vs AD1 {v} (1e-6)")
        if float(r["Relative ASA"]) != 0.0:
            gfail(f"top-8 {h}: rsa {r['Relative ASA']} != 0.0")
    print("  GATE top-8: all 8 control rows present with AD1's ddg "
          "(tol 1e-6) and rsa 0.0")

    dcol = sub["ddg_single_D"]
    if not np.isfinite(dcol.to_numpy(dtype=float)).all():
        gfail("L2a: non-finite ddg_single_D in the 123-row audit set")
    frac_d = float((dcol > 0).mean())
    n_pos_d = int((dcol > 0).sum())
    n_neg_d = int((dcol < 0).sum())
    print("  [L2a RESULT] ThermoMPNN-D single-mutant head on the "
          "IDENTICAL 123 rows:")
    print(f"    n={len(sub)} frac>0={frac_d:.3f} "
          f"median={float(dcol.median()):.3f} "
          f"mean={float(dcol.mean()):.3f} "
          f"min={float(dcol.min()):.3f} max={float(dcol.max()):.3f} "
          f"| positive={n_pos_d} negative={n_neg_d} "
          f"zero={len(sub) - n_pos_d - n_neg_d}")
    print("    raw ThermoMPNN (AD1):      n=123 frac>0=1.000 "
          "median=2.629 mean=2.684 min=0.675 max=4.501")
    if frac_d >= 0.95:
        conv = "SAME"
    elif frac_d <= 0.05:
        conv = "FLIPPED"
    else:
        conv = "MIXED"
    print(f"    convention rule (pre-registered): frac>0 "
          f"{frac_d:.3f} -> {conv}")
    print("    top-8 controls with the D-head value added:")
    for h, v in TOP8:
        r = idx8.loc[h]
        print(f"      {h:14s} raw ddg {v:+.6f}   ddg_single_D "
              f"{float(r['ddg_single_D']):+.6f}")

    n222_t77 = int((t77["position"] == 222).sum())
    print(f"  [L2b] A222V values are RETRIEVED, not re-derived "
          f"(position 222 has {n222_t77} rows in task_V2/task77 -- "
          f"gated in L1):")
    print("    raw ThermoMPNN  ddG(A222V) = -0.0439   source: "
          "DEEPDIVE_LOG [AD2] G1 -- script 68's V3 output, raw SSM "
          "re-read (position 182 + chain-A offset 40 = resi 222)")
    print("    ThermoMPNN-D    ddG_single(222V) = +0.8071  source: "
          "DEEPDIVE_LOG [AD4] G5 (DEEPDIVE L2324)")
    if conv == "SAME":
        verdict = (f"REAL DISAGREEMENT between the two model "
                   f"generations: both heads use positive = "
                   f"destabilizing (the D head passes the identical "
                   f"123-sub audit with frac>0 = {frac_d:.3f} vs the "
                   f"raw head's 1.000), so -0.0439 (~neutral) vs "
                   f"+0.8071 (destabilizing) is a genuine "
                   f"disagreement in predicted effect, not a "
                   f"sign-convention artifact.")
    elif conv == "FLIPPED":
        verdict = (f"SIGN-CONVENTION ARTIFACT: the D head scores "
                   f"the known-destabilizing audit set "
                   f"predominantly negative (frac>0 = {frac_d:.3f}), "
                   f"i.e. its sign is flipped relative to the "
                   f"vendored model. Read in meaning: raw -0.0439 = "
                   f"~neutral; D's +0.8071 on a flipped scale also "
                   f"= destabilizing ... the two heads agree in "
                   f"direction once each is read on its own "
                   f"convention.")
    else:
        verdict = (f"UNRESOLVED by this audit: the D head's 123-sub "
                   f"audit is neither uniform positive (1.000) nor "
                   f"uniform negative (frac>0 = {frac_d:.3f}) -> "
                   f"MIXED. Both readings reported as-is: under a "
                   f"same-convention reading the A222V signs truly "
                   f"disagree; under a flipped reading they agree. "
                   f"No forced conclusion.")
    print(f"  [L2b VERDICT (pre-registered rule)]: {verdict}")

    # ============================ L3 ====================================
    banner("[L3] interaction_D dynamic range", "-")
    an = an77.copy()
    if int(an["ca_dist_222"].notna().sum()) != 9595:
        gfail(f"L3: ca_dist_222 finite on "
              f"{int(an['ca_dist_222'].notna().sum())} != 9595")
    r_full = position_cluster_bootstrap(an, "position", "interaction_D",
                                        "own_e_b", n_boot=N_BOOT,
                                        seed=SEED)
    rho_full = float(r_full["observed_rho"])
    if round(rho_full, 4) != 0.0154:
        gfail(f"L3 identity: full-set rho {rho_full!r} does not "
              f"round to +0.0154 (AD4's logged primary)")
    print(f"  GATE identity: rho(interaction_D, own_e_b) full = "
          f"{rho_full} rounds to +0.0154 == AD4's logged primary "
          f"(DEEPDIVE L2328)")
    print(f"    this run: CI [{r_full['ci_lo']}, {r_full['ci_hi']}] "
          f"p_boot={r_full['p_boot']} (n {r_full['n_rows']}, "
          f"clusters {r_full['n_clusters']})")
    print("    AD4 logged: [-0.0166, +0.0465] p_boot 0.3406 "
          "n=9595 clusters=586 -- printed for comparison, not "
          "gated (CI endpoints depend on N_BOOT)")

    sd_full = float(an["interaction_D"].std(ddof=1))
    q25f = float(an["interaction_D"].quantile(0.25))
    q75f = float(an["interaction_D"].quantile(0.75))
    iqr_full = q75f - q25f
    print(f"  full set (9,595): SD {sd_full:.6f}  IQR {iqr_full:.6f} "
          f"(q25 {q25f:.6f}, q75 {q75f:.6f})")

    prox = an[an["ca_dist_222"] <= 8.0]
    n_prox = len(prox)
    print(f"  proximal subset (ca_dist_222 <= 8.0): n = {n_prox} rows "
          f"across {prox['position'].nunique()} positions "
          f"(distal complement n = {9595 - n_prox})")
    if n_prox < 10:
        print("  proximal n < 10 -> descriptive stats skipped; "
              "reporting what is available: full-set SD/IQR above "
              "and proximal n only (task wording).")
        r_SD = r_IQR = float("nan")
        r_prox = None
        label = "INSUFFICIENT N"
    else:
        sd_p = float(prox["interaction_D"].std(ddof=1))
        q25p = float(prox["interaction_D"].quantile(0.25))
        q75p = float(prox["interaction_D"].quantile(0.75))
        iqr_p = q75p - q25p
        r_SD = sd_full / sd_p
        r_IQR = iqr_full / iqr_p
        print(f"  proximal stats: SD {sd_p:.6f}  IQR {iqr_p:.6f} "
              f"(q25 {q25p:.6f}, q75 {q75p:.6f})")
        print(f"  ratios full/prox: SD {r_SD:.6f}  "
              f"IQR {r_IQR:.6f}")
        label = ("COLLAPSES" if r_SD <= 0.5 else
                 "REDUCED" if r_SD < 1.0 else "NOT REDUCED")
        print(f"  LABEL (pre-registered rule r_SD <= 0.5 -> "
              f"COLLAPSES; <1 -> REDUCED; >=1 -> NOT REDUCED): "
              f"{label}")
        if n_prox >= 30:
            r_prox = position_cluster_bootstrap(
                prox, "position", "interaction_D", "own_e_b",
                n_boot=N_BOOT, seed=SEED)
            print(f"  floor-effect probe (pre-registered, "
                  f"task-motivated): proximal rho = "
                  f"{float(r_prox['observed_rho'])} CI "
                  f"[{r_prox['ci_lo']}, {r_prox['ci_hi']}] "
                  f"p_boot={r_prox['p_boot']} (n "
                  f"{r_prox['n_rows']}, clusters "
                  f"{r_prox['n_clusters']})")
        else:
            r_prox = None
            print(f"  proximal n = {n_prox} < 30 -> subset "
                  f"bootstrap CI skipped and said so (pre-"
                  f"registered).")

    if label == "COLLAPSES" and r_prox is not None:
        excl = bool(r_prox["ci_lo"] > 0 or r_prox["ci_hi"] < 0)
        if excl:
            s = (f"L3b: dynamic range COLLAPSES on the full set "
                 f"(SD ratio {r_SD:.3f}) AND the proximal-subset CI "
                 f"excludes 0 -> the existing null (+0.0154) may be "
                 f"a FLOOR EFFECT; add the task's caveat wherever "
                 f"that null is cited (DEEPDIVE L2328, script 104's "
                 f"output, REVIEW_RESPONSE L43).")
        else:
            s = (f"L3b: dynamic range COLLAPSES (SD ratio "
                 f"{r_SD:.3f}) but the proximal-subset null "
                 f"PERSISTS (CI includes 0) -> range compression is "
                 f"real, yet the floor-effect reading is NOT "
                 f"supported by this probe; both facts stated "
                 f"wherever the null is cited.")
    elif label == "COLLAPSES":
        s = (f"L3b: COLLAPSES (SD ratio {r_SD:.3f}) but the "
             f"proximal CI was not computed (n < 30) -> floor "
             f"effect unresolved by this probe; report ratios + n.")
    elif label == "REDUCED":
        extra = ""
        if r_prox is not None:
            extra = (f" proximal rho CI "
                     f"[{r_prox['ci_lo']}, {r_prox['ci_hi']}]"
                     f"{' excludes 0' if (r_prox['ci_lo'] > 0 or r_prox['ci_hi'] < 0) else ' includes 0'}.")
        s = (f"L3b: range is REDUCED but does not collapse "
             f"(SD ratio {r_SD:.3f}, IQR ratio {r_IQR:.3f}) -> "
             f"floor-effect caveat is partial, not affirmative;"
             f"{extra}")
    elif label == "NOT REDUCED":
        s = (f"L3b: NOT a floor-effect candidate by this measure -- "
             f"the full set's spread is not smaller than the "
             f"proximal subset's (SD ratio {r_SD:.3f}, IQR ratio "
             f"{r_IQR:.3f}); the null at +0.0154 stands as a "
             f"genuine null on this test.")
    else:
        s = "L3b: insufficient proximal n; no range verdict."
    print(f"  {s}")

    banner("LIMITATIONS (printed per AGENTS 6)")
    print("  1. L1's 'identical masked inputs' claim is asserted "
          "from source (script 11's sequence construction + "
          "esm_scoring's masking), not by re-scoring -- no model "
          "runs this session.")
    print("  2. The 123-row audit reproduction is a UNIT TEST of "
          "plumbing against AD1's published numbers, not "
          "independent evidence (AGENTS 6). AD1 never recorded "
          "its amino-acid sets; they are identified here by exact "
          "reproduction, disclosed as such.")
    print("  3. A222V's two values are RETRIEVED from DEEPDIVE_LOG "
          "(position 222 has 0 rows in both tables, gated in L1) "
          "-- not re-derived.")
    print("  4. L3's proximal subset is a subset of the full set "
          "(not independent); the 0.5 collapse threshold is a "
          "pre-run convention, not a derived quantity.")
    print("  5. L2b's verdict depends wholly on the audit outcome; "
          "the thresholds (0.95 / 0.05) leave a MIXED middle "
          "that is reported, not forced.")
    print(f"\nDone in {time.time() - T0:.1f}s.")


if __name__ == "__main__":
    main()
