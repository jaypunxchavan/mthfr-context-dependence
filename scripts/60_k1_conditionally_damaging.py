"""
Script 60: K1a — conditionally damaging variants and the ESM-2 flag
fraction. Pre-registration: OVERNIGHT_LOG.md J3a entry (2026-09-22),
fixed before this script was written or run. Decision rules below are
pre-registered; do not change them after seeing results.

QUESTION (REVIEW_TRIAGE item 40): Of variants that cross a functional
threshold ONLY in the A222V background ("conditionally damaging"), what
fraction does ESM-2 flag as damaging, and does supplying the A222V
sequence change that fraction?

SET DEFINITION (pre-registered):
- Analysis set: atlas substitutions with both fitness arms non-null
  (expected ~10,757, printed), position 222 excluded a priori (undefined
  in the cis-with-A222V arm; count printed).
- Per-arm normalized fitness: f = (fitness - mean_nonsense_arm) /
  (mean_synonymous_arm - mean_nonsense_arm), anchors computed WITHIN arm
  from that arm's own synonymous/nonsense rows (standard DMS two-point
  normalization; removes the arm-wide A222V shift BY CONSTRUCTION -- the
  set therefore captures VARIANT-SPECIFIC in-cis harm, not A222V's global
  hypomorphism; disclosed in output).
- CONDITIONALLY DAMAGING (PRIMARY): f_WT >= 0.5 AND f_A222V < 0.5.
  Sensitivity bands 0.3 / 0.7 reported, labeled sensitivity only.

ESM FLAG (pre-registered): masked-marginal log-odds of the mutant vs the
background's own residue. PRIMARY: score < 0 (model disfavours the
mutant). Bands < -1, < -2 reported.

PRIMARY STATISTIC (pre-registered): delta_frac = frac_flagged(bg scoring)
- frac_flagged(WT scoring) among conditionally damaging variants,
position-cluster bootstrap, N_BOOT=2000 (same draws for both fractions).
VERDICT: FLAG-FRACTION-CHANGED iff CI excludes 0 AND |delta_frac| >= 0.05
(5-point effect-size floor, E1a precedent); else NOT-MEANINGFULLY-CHANGED.
Report: both fractions with CIs, set size (flag n < 100 as underpowered),
all-missense baseline fractions at the primary thresholds (descriptive).

LIMITATIONS (printed by the script itself, AGENTS 6):
- Fitness arms w/m are treated as WT-background / A222V-background;
  a sign sanity check (Spearman(m.fitness - w.fitness, own_e_b) must be
  positive) gates the run -- if the arm interpretation were backwards
  this correlation would be strongly negative and the script exits 1.
- The ESM flag threshold (log-odds < 0) is a modelling convention, not a
  validated pathogenicity cutoff; bands < -1 / < -2 show sensitivity.
- Rarity ("roughly a third of rare variants in cis with A222V") cannot be
  assessed here -- the atlas has no allele-frequency data. No claim about
  rare variants is made by this script.
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"
FIT_CUTS = [0.5, 0.3, 0.7]      # primary 0.5, sensitivity 0.3/0.7
SCORE_CUTS = [0.0, -1.0, -2.0]  # primary 0.0, bands -1/-2
EFFECT_FLOOR = 0.05


def flag_fracs_boot(df, n_boot, seed=0):
    """Paired flag fractions (WT bg, A222V bg) and their difference,
    position-cluster bootstrapped. df carries columns flag_wt, flag_bg,
    position."""
    pos = df["position"].to_numpy()
    fw = df["flag_wt"].to_numpy(dtype=float)
    fb = df["flag_bg"].to_numpy(dtype=float)
    uniq = np.unique(pos)
    idx_by = {c: np.flatnonzero(pos == c) for c in uniq}
    rng = np.random.default_rng(seed)
    dw = np.empty(n_boot)
    db = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        dw[b] = fw[i].mean()
        db[b] = fb[i].mean()
    dd = db - dw
    ci = lambda a: (float(np.percentile(a, 2.5)),
                    float(np.percentile(a, 97.5)))
    p = min(2 * min((dd <= 0).mean(), (dd >= 0).mean()), 1.0)
    w_lo, w_hi = ci(dw)
    b_lo, b_hi = ci(db)
    d_lo, d_hi = ci(dd)
    return {"frac_wt": float(fw.mean()), "frac_wt_ci": (w_lo, w_hi),
            "frac_bg": float(fb.mean()), "frac_bg_ci": (b_lo, b_hi),
            "delta": float(fb.mean() - fw.mean()),
            "delta_ci": (d_lo, d_hi), "p_boot": float(p)}


if __name__ == "__main__":
    print(f"Script 60 — K1a | N_BOOT={N_BOOT} SEED={SEED}")
    raw_p = RAW / "results" / "folate_response_model5.csv"
    merged_p = PROC / "merged_wt_a222v_scores.csv"
    own_p = PROC / "own_context_metrics.csv"
    for p in [raw_p, merged_p, own_p]:
        if not p.exists():
            print(f"GATE FAIL: missing {p}")
            sys.exit(1)

    raw = pd.read_csv(raw_p)
    print(f"raw rows {len(raw)}; columns include w.fitness="
          f"{'w.fitness' in raw.columns} m.fitness={'m.fitness' in raw.columns}")

    # ---- GATE: arm-direction sign sanity (S2-style labeled check) ----
    own = pd.read_csv(own_p)[["hgvs_pro", "own_e_b"]]
    chk = raw[["hgvs", "w.fitness", "m.fitness"]].rename(
        columns={"hgvs": "hgvs_pro"}).merge(own, on="hgvs_pro", how="inner")
    chk = chk.dropna()
    from scripts.lib.stats import _spearman
    rho_sign = _spearman((chk["m.fitness"] - chk["w.fitness"]).to_numpy(),
                         chk["own_e_b"].to_numpy())
    print(f"GATE arm-direction sanity: Spearman(m.fitness - w.fitness, "
          f"own_e_b) = {rho_sign:+.4f} on n={len(chk)} "
          f"(must be positive: own_e_b<0 <=> worse in A222V)")
    if not rho_sign > 0:
        print("GATE FAIL: arm interpretation contradicts S2's verified sign "
              "convention -- stopping per AGENTS 5/10")
        sys.exit(1)

    # ---- analysis set ----
    subs = raw[(raw["type"] == "substitution") &
               raw["w.fitness"].notna() & raw["m.fitness"].notna()].copy()
    # smoke-stage fix (disclosed): raw carries the residue position as
    # "start"; the bootstrap cluster column must exist before the loops.
    subs["position"] = subs["start"]
    n_222 = int((subs["start"] == 222).sum())
    subs = subs[subs["start"] != 222]
    print(f"eligible substitutions (both arms non-null): {len(subs) + n_222} "
          f"; position 222 excluded a priori: {n_222} -> set "
          f"{len(subs)}")
    if not 10000 <= len(subs) <= 11500:
        print(f"GATE FAIL: analysis set {len(subs)} outside expected band")
        sys.exit(1)

    # ---- per-arm anchors ----
    anchors = {}
    for arm in ["w.fitness", "m.fitness"]:
        syn_m = raw.loc[raw["type"] == "synonymous", arm].dropna().mean()
        non_m = raw.loc[raw["type"] == "nonsense", arm].dropna().mean()
        n_syn = int(raw.loc[raw["type"] == "synonymous", arm].notna().sum())
        n_non = int(raw.loc[raw["type"] == "nonsense", arm].notna().sum())
        if not non_m < syn_m:
            print(f"GATE FAIL: anchor order broken for {arm}: nonsense "
                  f"{non_m:.4f} >= synonymous {syn_m:.4f}")
            sys.exit(1)
        anchors[arm] = (syn_m, non_m)
        print(f"anchors {arm}: synonymous mean {syn_m:.4f} (n={n_syn}), "
              f"nonsense mean {non_m:.4f} (n={n_non})")

    (syn_w, non_w) = anchors["w.fitness"]
    (syn_m2, non_m2) = anchors["m.fitness"]
    subs["f_w"] = (subs["w.fitness"] - non_w) / (syn_w - non_w)
    subs["f_m"] = (subs["m.fitness"] - non_m2) / (syn_m2 - non_m2)

    # ---- ESM scores ----
    merged = pd.read_csv(merged_p)[
        ["hgvs_pro", "esm2_score", "esm2_score_a222v_bg", "delta_esm"]]
    bothm = merged.dropna()
    ident = (bothm["esm2_score_a222v_bg"] - bothm["esm2_score"] -
             bothm["delta_esm"]).abs().max()
    print(f"GATE merged delta identity: max|bg-wt-delta| = {ident:.3e} "
          f"(tol 1e-9)")
    if not ident < 1e-9:
        print("GATE FAIL: delta_esm identity broken")
        sys.exit(1)

    d = subs.merge(merged, left_on="hgvs", right_on="hgvs_pro", how="left")
    n_no_esm = int(d["esm2_score"].isna().sum() +
                   d["esm2_score_a222v_bg"].isna().sum())
    d = d.dropna(subset=["esm2_score", "esm2_score_a222v_bg"])
    print(f"after ESM merge: {len(d)} rows "
          f"({(len(subs) + n_222 - n_222) - len(d)} dropped for missing "
          f"scores); flag checks use {n_no_esm} missing score entries "
          f"counted before dropna")

    rows = []
    for fit_cut in FIT_CUTS:
        cd = d[(d["f_w"] >= fit_cut) & (d["f_m"] < fit_cut)]
        lbl_fit = f"f_cut={fit_cut}" + (" (PRIMARY)" if fit_cut == 0.5 else
                                        " (sensitivity)")
        if fit_cut == 0.5 and len(cd) < 100:
            print(f"NOTE: primary conditionally-damaging set n={len(cd)} "
                  f"< 100 -> UNDERPOWERED flag (pre-registered)")
        for sc in SCORE_CUTS:
            df = cd.copy()
            df["flag_wt"] = df["esm2_score"] < sc
            df["flag_bg"] = df["esm2_score_a222v_bg"] < sc
            if len(df) == 0 or df["position"].nunique() < 2:
                print(f"  {lbl_fit} score<{sc:g}: EMPTY/UNUSABLE "
                      f"(n={len(df)})")
                rows.append({"fit_cut": fit_cut, "score_cut": sc,
                             "n": len(df), "frac_wt": np.nan,
                             "frac_bg": np.nan, "delta": np.nan,
                             "ci_lo": np.nan, "ci_hi": np.nan,
                             "p_boot": np.nan, "primary": fit_cut == 0.5
                             and sc == 0.0})
                continue
            r = flag_fracs_boot(df, N_BOOT, SEED)
            primary = (fit_cut == 0.5 and sc == 0.0)
            if primary:
                fires = (not (r["delta_ci"][0] < 0 < r["delta_ci"][1]) and
                         abs(r["delta"]) >= EFFECT_FLOOR)
                verdict = ("FLAG-FRACTION-CHANGED" if fires
                           else "NOT-MEANINGFULLY-CHANGED")
            tag = "PRIMARY" if primary else "sensitivity"
            print(f"  {lbl_fit:<24} score<{sc:<4g} n={len(df):<5} "
                  f"frac_WT={r['frac_wt']:.4f} "
                  f"CI=[{r['frac_wt_ci'][0]:.4f},{r['frac_wt_ci'][1]:.4f}]  "
                  f"frac_BG={r['frac_bg']:.4f} "
                  f"CI=[{r['frac_bg_ci'][0]:.4f},{r['frac_bg_ci'][1]:.4f}]  "
                  f"delta={r['delta']:+.4f} "
                  f"CI=[{r['delta_ci'][0]:+.4f},{r['delta_ci'][1]:+.4f}] "
                  f"p={r['p_boot']:.4f}  [{tag}]")
            rows.append({"fit_cut": fit_cut, "score_cut": sc, "n": len(df),
                         "frac_wt": r["frac_wt"], "frac_bg": r["frac_bg"],
                         "delta": r["delta"], "ci_lo": r["delta_ci"][0],
                         "ci_hi": r["delta_ci"][1], "p_boot": r["p_boot"],
                         "primary": primary})
            if primary:
                print(f"    -> position={df['position'].nunique()} "
                      f"VERDICT: {verdict}")

    # ---- all-missense baseline at primary thresholds (descriptive) ----
    base = d.copy()
    base["flag_wt"] = base["esm2_score"] < 0.0
    base["flag_bg"] = base["esm2_score_a222v_bg"] < 0.0
    rb = flag_fracs_boot(base, N_BOOT, SEED)
    print(f"\nBASELINE all-missense (score<0): frac_WT={rb['frac_wt']:.4f} "
          f"frac_BG={rb['frac_bg']:.4f} delta={rb['delta']:+.4f} "
          f"CI=[{rb['delta_ci'][0]:+.4f},{rb['delta_ci'][1]:+.4f}] "
          f"n={len(base)} (descriptive, no decision attached)")

    out = PROC / "task60_k1_conditionally_damaging.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved {out}")
    print("\nLIMITATIONS: w/m arms treated as WT/A222V backgrounds (gated "
          "by positive Spearman(m-w, own_e_b)); score<0 is a convention not "
          "a validated cutoff (bands printed); per-arm syn anchoring removes "
          "A222V's global shift by construction (variant-specific harm only);"
          " no allele-frequency data -> no rare-variant claim.")
