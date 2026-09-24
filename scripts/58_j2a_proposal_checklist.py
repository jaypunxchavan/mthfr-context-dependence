"""
Script 58: J2a items 3 and 5. Pre-registration: OVERNIGHT_LOG.md J3a entry
(2026-09-22), fixed before this script was written or run. Do not change
the decision bands below after seeing results.

J2a-3 -- ESM-2 150M model check
-------------------------------
The proposal pre-registered the 150M model; the project ran
esm2_t33_650M_UR50D (scripts 10/11) with NO deviation note anywhere in the
repo (grep-verified, logged in J2a). This check scores a random subset of
positions with esm2_t30_150M_UR50D using the project's own masked-marginal
plumbing (scripts.lib.esm_scoring.get_position_logprobs, identical to
scripts 10/11) in BOTH backgrounds, and compares per-substitution deltas
against the cached 650M deltas.

  PRE-REGISTERED (J3a): N_POS=100 positions (seed 0) of the atlas set;
  PRIMARY = Spearman(delta_150M, delta_650M), position-cluster bootstrap,
  N_BOOT=2000.
    VERDICT BANDS:  CI_lo > 0.90            -> ROBUST-TO-MODEL-SIZE
                    0.75 < CI_lo <= 0.90    -> PARTIAL-ROBUSTNESS
                    CI_lo <= 0.75           -> SIZE-SENSITIVE
  Secondary (descriptive, no decision attached): sign agreement of delta
  (exact-zero ties excluded and counted); score-level rho 150 vs 650 per
  background.
  If the 150M weights cannot be fetched/run: outcome = DEVIATION NOTE with
  the exact error, no substitute model.

J2a-5 -- extrinsic-intrinsic correlation (limitation 7)
------------------------------------------------------
Proposal document is absent from the repo (J1a), so the logged conservative
reading applies: EXTRINSIC = published folinate_response (context_metrics),
INTRINSIC = own_e_b (own_context_metrics).

  PRE-REGISTERED (J3a): PRIMARY = Spearman(folinate_response, own_e_b) on
  the missense set, position-cluster bootstrap N_BOOT=2000.
  SECONDARY = partial version controlling w.fitness (rank-residual method,
  re-derived inside every bootstrap draw), same resampling.
    VERDICT BANDS: |rho_primary| >= 0.10 AND CI excludes 0
                    -> STRANDS-NOT-INDEPENDENT (limitation-7 concern
                       supported)
                    otherwise -> INDEPENDENCE-NOT-REJECTED
  Effect size reported either way (AGENTS 3).

LIMITATIONS (printed by the script itself, AGENTS 6):
- The 150M check is a subset check, not a full pipeline re-run; positions
  are sampled at random (seed 0). It tests checkpoint-size sensitivity of
  delta_ESM, not every downstream number.
- Reproducing the cached 650M deltas from their source CSVs is a join unit
  test, not independent evidence (AGENTS 6).
- The limitation-7 column mapping is a logged conservative reading, not
  recovered from the (absent) proposal document.
- Partial correlation controls w.fitness linearly in rank space; F1a showed
  the fitness relationship is nonlinear, so the partial is a coarse
  adjustment, not a fully flexible control. Stated, not hidden.
"""
import sys, os, time, re, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

N_BOOT = int(os.environ.get("N_BOOT", 2000))
N_POS = int(os.environ.get("N_POS", 100))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def partial_spearman_cluster_boot(df, cluster_col, x_col, y_col, z_col,
                                  n_boot, seed=0):
    """Partial Spearman of x,y | z with position-cluster bootstrap.
    Uses the house closed-form _partial_spearman (ranks internally),
    re-derived inside every draw. p_boot follows house _summarize:
    min(2 * min(P(boot<=0), P(boot>=0)), 1).

    Smoke-stage fix (disclosed): the first version computed p as the
    fraction of draws within |obs| of zero, which is not a p-value and
    disagreed with its own CI; replaced before any full run. The
    pre-registered decision bands (J3a) were never affected -- they key
    off the CI and the point estimate only."""
    from scripts.lib.stats import _partial_spearman
    d = df[[cluster_col, x_col, y_col, z_col]].dropna().reset_index(drop=True)
    x = d[x_col].to_numpy()
    y = d[y_col].to_numpy()
    z = d[z_col].to_numpy()

    obs = _partial_spearman(x, y, z)
    clusters = d[cluster_col].to_numpy()
    uniq = np.unique(clusters)
    idx_by = {c: np.flatnonzero(clusters == c) for c in uniq}
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for b in range(n_boot):
        drawn = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([idx_by[c] for c in drawn])
        boot[b] = _partial_spearman(x[i], y[i], z[i])
    boot = boot[~np.isnan(boot)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p = min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0)
    return {"observed": obs, "ci_lo": float(lo), "ci_hi": float(hi),
            "p_boot": float(p), "n_rows": len(d), "n_clusters": len(uniq)}


if __name__ == "__main__":
    t_run = time.time()
    print(f"Script 58 — J2a items 3 & 5 | N_POS={N_POS} N_BOOT={N_BOOT} SEED={SEED}")

    # ================= data gates (house pattern) =================
    for p in [PROC / "merged_wt_a222v_scores.csv", PROC / "context_metrics.csv",
              PROC / "own_context_metrics.csv", RAW / "P42898.fasta",
              RAW / "mthfrModel" / "results" / "folate_response_model5.csv"]:
        if not p.exists():
            print(f"GATE FAIL: missing required file {p}")
            sys.exit(1)

    merged = pd.read_csv(PROC / "merged_wt_a222v_scores.csv")
    both = merged[merged["esm2_score"].notna() &
                  merged["esm2_score_a222v_bg"].notna() &
                  merged["delta_esm"].notna()]
    ident = (both["esm2_score_a222v_bg"] - both["esm2_score"] -
             both["delta_esm"]).abs().max()
    print(f"GATE 1 merged delta identity: max|bg-wt-delta| = {ident:.3e} "
          f"on {len(both)} rows (tol 1e-9)")
    if not ident < 1e-9:
        print("GATE FAIL: delta_esm is not bg - wt in merged CSV")
        sys.exit(1)

    # 650M scores reproduce from their two source CSVs (join unit test)
    wt = pd.read_csv(PROC / "esm2_wt_scores.csv")[["hgvs_pro", "esm2_score"]]
    bg = pd.read_csv(PROC / "esm2_a222v_bg_scores.csv")[
        ["hgvs_pro", "esm2_score_a222v_bg"]].dropna(subset=["hgvs_pro"])
    chk = both.merge(wt, on="hgvs_pro", suffixes=("", "_src")).merge(
        bg, on="hgvs_pro", suffixes=("", "_src"))
    d1 = (chk["esm2_score"] - chk["esm2_score_src"]).abs().max()
    d2 = (chk["esm2_score_a222v_bg"] - chk["esm2_score_a222v_bg_src"]).abs().max()
    print(f"GATE 2 650M join reproduction: max|delta wt| = {d1:.3e}, "
          f"bg = {d2:.3e}, n = {len(chk)} (tol 1e-9)")
    if not (d1 < 1e-9 and d2 < 1e-9 and len(chk) > 10000):
        print("GATE FAIL: cached 650M scores do not reproduce from sources")
        sys.exit(1)

    # ================= J2a-5: extrinsic-intrinsic correlation =========
    print("\n" + "=" * 74)
    print("J2a-5  EXTRINSIC vs INTRINSIC correlation (limitation 7)")
    print("=" * 74)
    from scripts.lib.stats import position_cluster_bootstrap

    ctx = pd.read_csv(PROC / "context_metrics.csv")[
        ["hgvs_pro", "position", "folinate_response"]]
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    raw = pd.read_csv(RAW / "mthfrModel" / "results" / "folate_response_model5.csv")
    wf = raw[["hgvs", "w.fitness"]].rename(columns={"hgvs": "hgvs_pro"})
    d5 = ctx.merge(own, on="hgvs_pro", how="inner").merge(wf, on="hgvs_pro",
                                                          how="left")
    d5 = d5.dropna(subset=["folinate_response", "own_e_b", "position"])
    n_pos5 = d5["position"].nunique()
    print(f"missense rows with both traits: {len(d5)}, positions: {n_pos5}, "
          f"w.fitness present: {d5['w.fitness'].notna().sum()}")
    if not (len(d5) > 8000 and n_pos5 > 500):
        print("GATE FAIL: J2a-5 analysis set unexpectedly small")
        sys.exit(1)

    prim = position_cluster_bootstrap(d5, "position", "folinate_response",
                                      "own_e_b", n_boot=N_BOOT, seed=SEED)
    rho, lo, hi = prim["observed_rho"], prim["ci_lo"], prim["ci_hi"]
    excl0 = not (lo < 0 < hi)
    fires = abs(rho) >= 0.10 and excl0
    verdict5 = "STRANDS-NOT-INDEPENDENT" if fires else "INDEPENDENCE-NOT-REJECTED"
    print(f"PRIMARY Spearman(folinate_response, own_e_b): rho={rho:+.4f} "
          f"CI=[{lo:+.4f},{hi:+.4f}] p={prim['p_boot']:.4f} "
          f"n={prim['n_rows']} pos={prim['n_clusters']}")
    print(f"  bands: |rho|>=0.10 ({abs(rho) >= 0.10}) AND CI excludes 0 "
          f"({excl0})  ->  VERDICT: {verdict5}")

    sec = partial_spearman_cluster_boot(d5, "position", "folinate_response",
                                        "own_e_b", "w.fitness",
                                        n_boot=N_BOOT, seed=SEED)
    print(f"SECONDARY partial | w.fitness (rank-residual): rho={sec['observed']:+.4f} "
          f"CI=[{sec['ci_lo']:+.4f},{sec['ci_hi']:+.4f}] p={sec['p_boot']:.4f} "
          f"n={sec['n_rows']} pos={sec['n_clusters']}  (descriptive co-primary "
          f"context; coarse linear-in-rank control, see docstring)")

    # ================= J2a-3: 150M check ==========================
    print("\n" + "=" * 74)
    print("J2a-3  ESM-2 150M model check (proposal pre-registered model)")
    print("=" * 74)
    from scripts.lib.sequence import load_sequence
    from scripts.lib.io import load_primary_maps
    from scripts.lib.esm_scoring import (get_position_logprobs, hgvs_pro,
                                         get_device)

    seq = load_sequence(RAW / "P42898.fasta")
    assert seq[221] == "A", f"expected A222, found {seq[221]}"
    a222v_seq = seq[:221] + "V" + seq[222:]
    maps = load_primary_maps()
    positions = sorted({
        int(m.group(1))
        for h in set(maps["hgvs_pro"].unique())
        for m in [re.match(r"p\.[A-Za-z]{3}(\d+)", str(h))] if m})
    print(f"sequence len {len(seq)}; atlas positions {len(positions)}")
    if not len(positions) >= 600:
        print("GATE FAIL: position set unexpectedly small")
        sys.exit(1)

    rng = np.random.default_rng(SEED)
    sample = sorted(rng.choice(positions, size=min(N_POS, len(positions)),
                               replace=False).tolist())
    print(f"sampled N_POS={len(sample)} positions (seed {SEED}); "
          f"222 in sample: {222 in sample}")

    try:
        import esm
        print("Loading esm2_t30_150M_UR50D (downloads weights if not cached)...")
        model150, alphabet150 = esm.pretrained.esm2_t30_150M_UR50D()
        model150.eval()
    except Exception as e:
        print("\nDEVIATION NOTE (pre-registered fallback, J3a): the 150M "
              "check could not run.")
        print(f"Exact error: {type(e).__name__}: {e}")
        print("No substitute model used. J2a-3 outcome = DEVIATION-NOTE; "
              "J2a-5 above ran normally.")
        print(f"\nTotal wall: {time.time() - t_run:.1f} s")
        sys.exit(0)

    device = get_device()
    print(f"Using device: {device}")
    model150 = model150.to(device)
    bc150 = alphabet150.get_batch_converter()

    t0 = time.time()
    rows = []
    for i, pos in enumerate(sample):
        s_wt = get_position_logprobs(model150, alphabet150, bc150, seq, pos,
                                     device)
        s_bg = get_position_logprobs(model150, alphabet150, bc150, a222v_seq,
                                     pos, device)
        for mut_aa in s_wt:
            rows.append({
                "position": pos,
                "hgvs_pro": hgvs_pro(seq[pos - 1], pos, mut_aa),
                "score150_wt": s_wt[mut_aa],
                "score150_bg": s_bg.get(mut_aa, np.nan),
                "delta150": (s_bg.get(mut_aa, np.nan) - s_wt[mut_aa])
                            if mut_aa in s_bg else np.nan,
            })
        if (i + 1) % 25 == 0 or (i + 1) == len(sample):
            print(f"  {i+1}/{len(sample)} positions "
                  f"({time.time() - t0:.0f}s elapsed)")
    r150 = pd.DataFrame(rows)

    mrg = r150.merge(merged[["hgvs_pro", "esm2_score", "esm2_score_a222v_bg",
                             "delta_esm"]], on="hgvs_pro", how="left")
    dropped = mrg["delta_esm"].isna().sum()
    print(f"scored rows: {len(r150)}; unmatched to cached 650M delta: "
          f"{dropped} (includes pos 222 naming gap if sampled)")
    d = mrg.dropna(subset=["delta150", "delta_esm"]).copy()
    d = d.rename(columns={"delta_esm": "delta650"})
    print(f"matched for PRIMARY: {len(d)} substitutions, "
          f"{d['position'].nunique()} positions")
    # Smoke-stage fix (disclosed): the matched-set floor must scale with
    # N_POS or the smoke run cannot exercise the full path. Full-run floor
    # stays 500 rows (N_POS=100 -> min(500, 1615) = 500), unchanged intent.
    floor = min(500, int(0.85 * 19 * len(sample)))
    if not len(d) >= floor:
        print(f"GATE FAIL: matched set too small for the pre-registered "
              f"test ({len(d)} < {floor})")
        sys.exit(1)

    prim3 = position_cluster_bootstrap(d, "position", "delta150", "delta650",
                                       n_boot=N_BOOT, seed=SEED)
    rho3, lo3, hi3 = prim3["observed_rho"], prim3["ci_lo"], prim3["ci_hi"]
    if lo3 > 0.90:
        verdict3 = "ROBUST-TO-MODEL-SIZE"
    elif lo3 > 0.75:
        verdict3 = "PARTIAL-ROBUSTNESS"
    else:
        verdict3 = "SIZE-SENSITIVE"
    print(f"PRIMARY Spearman(delta_150M, delta_650M): rho={rho3:+.4f} "
          f"CI=[{lo3:+.4f},{hi3:+.4f}] p={prim3['p_boot']:.4f} "
          f"n={prim3['n_rows']} pos={prim3['n_clusters']}")
    print(f"  bands: CI_lo={lo3:+.4f}  ->  VERDICT: {verdict3}")

    ties = int(((d["delta150"] == 0) | (d["delta650"] == 0)).sum())
    dz = d[(d["delta150"] != 0) & (d["delta650"] != 0)]
    agree = float((np.sign(dz["delta150"]) == np.sign(dz["delta650"])).mean())
    print(f"SECONDARY (descriptive) sign agreement: {100*agree:.2f}% of "
          f"{len(dz)} rows (exact-zero ties excluded: {ties})")
    for lbl, c150, c650 in [("wt bg", "score150_wt", "esm2_score"),
                            ("a222v bg", "score150_bg",
                             "esm2_score_a222v_bg")]:
        sub = d.dropna(subset=[c150, c650])
        from scripts.lib.stats import _spearman
        print(f"SECONDARY (descriptive) score rho {lbl}: "
              f"{_spearman(sub[c150].to_numpy(), sub[c650].to_numpy()):+.4f} "
              f"(n={len(sub)})")

    out = d[["position", "hgvs_pro", "score150_wt", "score150_bg",
             "delta150", "delta650", "esm2_score",
             "esm2_score_a222v_bg"]]
    out.to_csv(PROC / "task58_150m_check.csv", index=False)
    print(f"\nSaved {PROC / 'task58_150m_check.csv'}")
    print("\nLIMITATIONS: subset check (not full pipeline re-run); 650M "
          "reproduction is a join unit test; J2a-5 column mapping is the "
          "logged conservative reading; partial control linear in ranks.")
    print(f"Total wall: {time.time() - t_run:.1f} s")
