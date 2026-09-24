"""
Task H3 (review-triage): rescue/suppressor variant enrichment [item 29].

H3a: Does ESM-2 fail symmetrically on "worse in A222V" and "better in
A222V" (rescue/suppressor) variants, or does delta_ESM enrich for the
rescue variants at all? These are the most biologically interesting
variants in the dataset and haven't been examined separately.

SIGN CONVENTIONS (verified in S2, not assumed -- log entries S2):
  e.b < 0  <=> measured LESS functional in A222V than no-interaction
             expectation (verified against fitModels.R source + labeled
             rows: p.Leu529Pro, p.Pro627Met, p.Ala145Thr).
  e.b > 0  <=> RESCUE: measured BETTER in A222V than expected.
  delta_ESM < 0 <=> ESM-2 says v is worse in the A222V background.
  Therefore "ESM-2 agrees" <=> sign(delta_ESM) == sign(e.b).

PRE-REGISTERED DESIGN (stated before running -- AGENTS.md §6)
--------------------------------------------------------------
Population: phase5, non-null delta_esm AND GI_folinate_independent
(n=10,757 / 654 positions, the established set). Groups by sign of e.b
(rescue = e.b > 0, worse = e.b < 0).

PRIMARY statistics, each position-cluster bootstrapped (N_BOOT):
  T1  mean(delta_ESM) in rescue vs in worse, and the difference
      (rescue - worse).
  T2  agreement rates:
        r_res  = P(delta_ESM > 0 | e.b > 0)      [ESM agrees it rescues]
        r_wor  = P(delta_ESM < 0 | e.b < 0)      [ESM agrees it worsens]
      each CI vs the 0.5 chance line; asymmetry = r_res - r_wor with CI.
  T3  AUC of delta_ESM for the class e.b > 0 (0.5 = no rank enrichment),
      CI.

SECONDARY (labeled): the same three on the atlas-significant subset
GI_indep_post > 0.95 (S2's convention; GI_indep_post verified equal to
the raw atlas e.post.b column to <1e-12 or sys.exit(1)).

Pre-registered verdicts:
  ENRICHMENT-FOR-RESCUE iff T3's CI excludes 0.5 -- state direction.
  else NO-RANK-ENRICHMENT.
  SYMMETRIC-FAILURE iff BOTH agreement-rate CIs include 0.5 AND the
  asymmetry CI includes 0; ASYMMETRIC-FAILURE otherwise (asymmetry CI
  excludes 0 -- ESM-2 fails one class more than the other).
  Base-rate enrichment descriptor (descriptive, not a gate):
  among delta_ESM > 0 variants, fraction with e.b > 0 vs the population
  base rate of e.b > 0.

Null/CI conventions: position-cluster bootstrap throughout (AGENTS §3).
No permutation p-values claimed; effect sizes + CIs are the report.

Limitations stated up front:
  * e.b's sign split includes variants whose own interaction estimate is
    noise-level (the significant-subset secondary addresses this);
    results are reported for BOTH so the noise-inclusion sensitivity is
    visible.
  * Mean-comparison T1 mixes scale assumptions; T2/T3 are rank/shape
    based and carry the main weight.

Env: N_BOOT (default 2000). Smoke with 50-100.
Output: data/processed/task56_h3_rescue.csv
"""
import sys, os, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

N_BOOT = int(os.environ.get("N_BOOT", 2000))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "mthfrModel"
POST_CUT = 0.95


def cluster_boot(df, stat_fn, n_boot, seed):
    """Generic position-cluster bootstrap of stat_fn(df_sample) -> dict."""
    d = df.reset_index(drop=True)
    idx_map = {p: d.index[d["position"] == p].to_numpy()
               for p in d["position"].unique()}
    keys = np.array(list(idx_map.keys()))
    rng = np.random.default_rng(seed)
    obs = stat_fn(d)
    draws = {k: np.empty(n_boot) for k in obs}
    for i in range(n_boot):
        draw = rng.choice(keys, size=len(keys), replace=True)
        idx = np.concatenate([idx_map[p] for p in draw])
        s = stat_fn(d.iloc[idx])
        for k in obs:
            draws[k][i] = s[k]
    out = {}
    for k in obs:
        lo, hi = np.percentile(draws[k], [2.5, 97.5])
        out[k] = {"obs": obs[k], "ci_lo": lo, "ci_hi": hi}
    out["_n_rows"] = len(d)
    out["_n_pos"] = d["position"].nunique()
    return out


def stats_for(sub):
    eb = sub["GI_folinate_independent"].to_numpy()
    dv = sub["delta_esm"].to_numpy()
    resc, wor = eb > 0, eb < 0
    mean_r = float(dv[resc].mean()) if resc.any() else np.nan
    mean_w = float(dv[wor].mean()) if wor.any() else np.nan
    r_res = float((dv[resc] > 0).mean()) if resc.any() else np.nan
    r_wor = float((dv[wor] < 0).mean()) if wor.any() else np.nan
    auc = float(roc_auc_score((eb > 0).astype(int), dv)) if len(np.unique(eb > 0)) == 2 else np.nan
    return {"mean_delta_rescue": mean_r,
            "mean_delta_worse": mean_w,
            "mean_diff": mean_r - mean_w,
            "agree_rescue": r_res,
            "agree_worse": r_wor,
            "asymmetry": r_res - r_wor,
            "auc": auc}


def report(label, sub, n_boot, seed, rows):
    print(f"\n  [{label}]  n={len(sub)} rows, "
          f"{sub['position'].nunique()} positions; "
          f"rescue(e.b>0)={int((sub['GI_folinate_independent'] > 0).sum())} "
          f"worse(e.b<0)={int((sub['GI_folinate_independent'] < 0).sum())}")
    b = cluster_boot(sub, stats_for, n_boot, seed)
    m_r, m_w = b["mean_delta_rescue"], b["mean_delta_worse"]
    m_d = b["mean_diff"]
    print(f"    mean delta     rescue={m_r['obs']:+.5f} "
          f"CI=[{m_r['ci_lo']:+.5f},{m_r['ci_hi']:+.5f}]   "
          f"worse={m_w['obs']:+.5f} CI=[{m_w['ci_lo']:+.5f},{m_w['ci_hi']:+.5f}]")
    print(f"    mean diff      {m_d['obs']:+.5f} "
          f"CI=[{m_d['ci_lo']:+.5f},{m_d['ci_hi']:+.5f}]  (rescue - worse)")
    a_r, a_w, asym = b["agree_rescue"], b["agree_worse"], b["asymmetry"]
    inc_r = a_r["ci_lo"] <= 0.5 <= a_r["ci_hi"]
    inc_w = a_w["ci_lo"] <= 0.5 <= a_w["ci_hi"]
    print(f"    agree rescue   {a_r['obs']:+.4f} "
          f"CI=[{a_r['ci_lo']:+.4f},{a_r['ci_hi']:+.4f}]  "
          f"vs 0.5: {'INCLUDES' if inc_r else 'EXCLUDES'}")
    print(f"    agree worse    {a_w['obs']:+.4f} "
          f"CI=[{a_w['ci_lo']:+.4f},{a_w['ci_hi']:+.4f}]  "
          f"vs 0.5: {'INCLUDES' if inc_w else 'EXCLUDES'}")
    inc_as = asym["ci_lo"] <= 0.5 - 0.5 <= asym["ci_hi"]
    print(f"    asymmetry      {asym['obs']:+.4f} "
          f"CI=[{asym['ci_lo']:+.4f},{asym['ci_hi']:+.4f}]  "
          f"vs 0: {'INCLUDES' if inc_as else 'EXCLUDES'}")
    auc = b["auc"]
    inc_auc = auc["ci_lo"] <= 0.5 <= auc["ci_hi"]
    enrich = ("ENRICHMENT-FOR-RESCUE (CI excludes 0.5, direction: "
              + ("delta higher for rescue)" if auc["obs"] > 0.5 else
                 "delta LOWER for rescue, i.e. inverted)")) \
        if not inc_auc else "NO-RANK-ENRICHMENT"
    print(f"    AUC(delta->e.b>0) {auc['obs']:.4f} "
          f"CI=[{auc['ci_lo']:.4f},{auc['ci_hi']:.4f}]  -> {enrich}")
    sym = (inc_r and inc_w and inc_as)
    print(f"    failure shape: {'SYMMETRIC-FAILURE' if sym else 'ASYMMETRIC-FAILURE'}"
          f"  (both rate CIs include 0.5 AND asymmetry CI includes 0: {sym})")
    # descriptive base-rate enrichment
    dv = sub["delta_esm"].to_numpy()
    eb = sub["GI_folinate_independent"].to_numpy()
    base = float((eb > 0).mean())
    pos = dv > 0
    frac = float((eb[pos] > 0).mean()) if pos.any() else np.nan
    print(f"    descriptor     base rate e.b>0 = {base:.4f}; among "
          f"delta_ESM>0 (n={int(pos.sum())}): e.b>0 = {frac:.4f}")
    for k, v in b.items():
        if k.startswith("_"):
            continue
        rows.append({"subset": label, "stat": k, "value": v["obs"],
                     "ci_lo": v["ci_lo"], "ci_hi": v["ci_hi"],
                     "n": len(sub)})
    rows.append({"subset": label, "stat": "base_rate_rescue", "value": base})
    rows.append({"subset": label, "stat": "rescue_given_delta_pos",
                 "value": frac})
    return b


if __name__ == "__main__":
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    df = df.dropna(subset=["delta_esm", "GI_folinate_independent"]).copy()
    print(f"Analysis set: {len(df)} variants, "
          f"{df['position'].nunique()} positions")

    # GATE: GI_indep_post == raw atlas e.post.b (NaN patterns included --
    # 5 analysis rows have NaN in BOTH columns; an earlier draft gate only
    # counted jointly non-null rows and mis-fired. Smoke-stage gate bug,
    # fixed before any H3 statistic ran -- disclosed in the log.)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv",
                      usecols=["hgvs", "e.post.b"]).rename(
                          columns={"hgvs": "hgvs_pro"})
    m = df.merge(raw, on="hgvs_pro", how="left")
    if len(m) != len(df):
        print("*** merge changed row count. sys.exit(1)")
        sys.exit(1)
    both_nan = int((m["GI_indep_post"].isna() & m["e.post.b"].isna()).sum())
    one_sided = int((m["GI_indep_post"].isna() ^ m["e.post.b"].isna()).sum())
    g = m.dropna(subset=["GI_indep_post", "e.post.b"])
    dmax = float((g["GI_indep_post"] - g["e.post.b"]).abs().max())
    print(f"GATE GI_indep_post == raw e.post.b: jointly non-null={len(g)}, "
          f"NaN in both={both_nan}, one-sided NaN={one_sided}, "
          f"max|diff|={dmax:.2e} (tol 1e-12) -> "
          f"{'OK' if dmax <= 1e-12 and one_sided == 0 else 'FAIL'}")
    if not (dmax <= 1e-12 and one_sided == 0):
        print("*** GATE FAILED -- column identity unproven. sys.exit(1)")
        sys.exit(1)

    rows = []
    print("\n" + "=" * 74)
    print("H3a: rescue vs worse-in-A222V, ESM-2's failure shape")
    print("=" * 74)
    report("PRIMARY (all, n=10757)", df, N_BOOT, SEED, rows)

    sig = df[df["GI_indep_post"] > POST_CUT]
    report(f"SECONDARY (e.post.b > {POST_CUT})", sig, N_BOOT, SEED + 1, rows)

    out = PROC / "task56_h3_rescue.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved {out}")
    print("\nLIMITATIONS (script is the record, AGENTS §6): groups are split")
    print("on the SIGN of a noisy estimate (primary includes noise-level")
    print("interactions; the e.post.b>0.95 secondary shows the sensitivity).")
    print("Position-cluster bootstrap CIs throughout (AGENTS §3); no")
    print("permutation p-values claimed. Sign conventions verified in S2")
    print("against atlas source and labeled rows, not assumed.")
