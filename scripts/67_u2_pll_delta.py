"""
Script 67 (task U2a/U2b): whole-sequence pseudo-log-likelihood delta as an
alternative to the single-position delta_ESM, then the same sign-flip null.

PRE-REGISTRATION (written before the first run; do not change after seeing
results -- any later change must be disclosed in SESSION_LOG as post-hoc).

WHAT IS BEING TESTED
--------------------
I3 asks whether the negative finding is specific to ESM-2's masked-marginal
scoring recipe. This script swaps the recipe, not the model: the existing
endpoint scores ONLY the variant's own position

    delta_ESM(v)  = logodds(alt@p | A222V bg) - logodds(alt@p | WT bg)
                    [esm2_a222v_bg esm2_score - esm2_wt esm2_score,
                     script 12 line 29; odds = logP(a|mask p) - logP(wt|mask p)]

and this script scores a pseudo-likelihood (PL) of the whole variant
sequence in each background:

    PLL(x)  = sum_{j in P} logP(x_j | x with j masked)      (PL definition)
    delta_PLL(v) = PLL(A222V-seq with alt@p) - PLL(WT-seq with alt@p)

CONSTRUCTION (the subset/evaluation rules, fixed now):
  * P = every atlas position in the cached tables PLUS position 222 (the
    A222V site belongs in any interaction-relevant sequence sum; no atlas
    variant sits AT 222, verified: phase5 position==222 count = 0).
  * j = p   : exact -- masking p removes p from context; the two contexts
              differ only at 222, exactly the cached scripts-10/11 passes.
  * j = 222 : exact -- masking 222 makes both backgrounds' contexts the
              SAME string (WT-seq with alt@p), one fresh forward pass per
              variant reads both required residues V (A222V term) and A
              (WT term).  This per-variant term is
                  L222(v) = logP(V | mask222, ctx_alt) - logP(A | mask222, ctx_alt)
              and is the only part of delta_PLL that carries new information
              beyond the cached tables.
  * j elsewhere: context-frozen at each background's wild-type sequence --
              the SAME approximation every cached masked-marginal pipeline
              in this repo already makes (scripts 10/11 scored pure
              backgrounds, never variant contexts).  These terms are
              v-independent under freezing, and summing them algebraically
              gives a GLOBAL constant K (position offsets cancel exactly
              between the j=p term and the sum's exclusion of p):

                  delta_PLL(v) = delta_ESM(v) + L222(v) + K      (derived)

              K does not affect Spearman; it is still computed and printed
              so the absolute PLL values are on the record.
  * What freezing DROPS: the effect of alt@p on distal masked positions
    (a true whole-sequence context effect, ~1 pass/variant/position --
    14M+ forward passes, infeasible).  It is QUANTIFIED on a random
    sample (BRUTE_N variants, seed 0) by computing the un-frozen
    full 655-position sum directly and measuring the per-variant
    discrepancy; reported as a limitation with its actual size.

DECISION RULES (pre-registered):
  * Primary reported rho: Spearman(delta_PLL, own_e_b), position-cluster
    bootstrap CI, N_BOOT draws -- the exact machinery of scripts 32/33.
  * Sensitivity line (no separate claim): the strict {p, 222}-subset PL
    (delta_esm + delta_bg_raw(wt_p) + L222) -- differs from primary by a
    position-level offset only.
  * U2b null = script 33's code path, unchanged: same lib functions
    (wls_line/CONCS, rebuild_interaction_fit, _spearman), same sanity
    checks (all-+1 must reproduce own_e_b to 1e-6 or exit 1), same
    Null 1 sign-flip (signed + absolute arms), Null 2 position-block
    permutation, region arm.  Predicated on delta_PLL in place of
    delta_ESM.  Script 33 = scripts/33_delta_esm_signflip_null.py (one of
    two files numbered 33 in this repo; the other,
    33_measurement_noise_control.py, contains no sign-flip null -- task
    resolution assumption logged in SESSION_LOG).
  * Gates that exit(1): G1 cached-odds identity (raw-derived odds vs both
    cached CSVs, max|diff| <= 1e-4); G2 raw delta at 222 across
    backgrounds ~ 0 (masked contexts identical, <= 1e-4); G3 script 33's
    +/-1 sign-flip identity (<= 1e-6).  The brute-force frozen-context
    comparison is a DISCLOSURE, not a gate (it measures a declared
    approximation, not correctness of what this script computes).

LIMITATIONS (printed by the run itself): frozen distal context (size
reported); one-directional interaction (same as script 32's -- the atlas
measures variants IN the A222V background only, no symmetrisation); p
values apply to own_e_b and transfer to published e.b only as far as the
two agree (script 17); no new download (650M weights already cached).

Outputs: data/processed/task67_u2_pll_scores.csv,
         data/processed/task67_u2_results.csv
Env: N_BOOT (default 10000), N_PERM (default 10000), BRUTE_N (default 16),
     BATCH (default 16), PHASE2_MAX (default 0 = all variants; SMOKE-ONLY
     knob to cap L222 scoring for the reduced-N machinery smoke — the
     resulting rows carry NaN delta_pll and every printed statistic is
     labelled with its reduced n; never use a nonzero value for a reported
     result).
     Smoke first: N_BOOT=300 N_PERM=300 BRUTE_N=2 PHASE2_MAX=300.
Runtime note (added before ANY result existed, after a timed benchmark on
this machine — disclosed in SESSION_LOG): fresh masked forwards run at
0.587 s/seq at BATCH=16 (batches >16 thrash MPS memory and get slower),
so the FULL-N run needs >= 13 + 111 + 26 + 15 ~= 165 min, above this
session's ~2h-per-task cap; the full run is therefore BLOCKED for this
session and only the reduced-N smoke executes.
"""
import sys, os, time, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch

from scripts.lib.sequence import load_sequence
from scripts.lib.esm_scoring import AA_LIST, get_device
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats import _spearman, position_cluster_bootstrap
from scripts.lib.stats_ext import rebuild_interaction_fit
from scripts.lib.regions import assign_region, REGION_BOUNDS

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
BRUTE_N = int(os.environ.get("BRUTE_N", 16))
BATCH = int(os.environ.get("BATCH", 16))
PHASE2_MAX = int(os.environ.get("PHASE2_MAX", 0))  # smoke-only cap, 0 = all
SEED = 0
POS_222 = 222
ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "mthfrModel"
T0 = time.time()


def pstr(p, n=1):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


def el(tag):
    print(f"  [{tag} t={time.time()-T0:6.0f}s]", flush=True)


def aa_indices(alphabet):
    return {aa: alphabet.get_idx(aa) for aa in AA_LIST}


def batched_raw_logprobs(model, bc, seq_targets, aa_idx, device, batch):
    """seq_targets: list of (masked_seq_string, target_idx0).
    Returns (len, 20) float64 raw log-probs for AA_LIST order.
    Halves the batch on CUDA/MPS OOM and retries."""
    out = np.empty((len(seq_targets), len(AA_LIST)), dtype=np.float64)
    order = [aa_idx[a] for a in AA_LIST]
    i, b = 0, batch
    while i < len(seq_targets):
        chunk = seq_targets[i:i + b]
        try:
            _, _, tokens = bc([("v", s) for s, _ in chunk])
            tokens = tokens.to(device)
            with torch.no_grad():
                logits = model(tokens, repr_layers=[], return_contacts=False)["logits"]
            tg = torch.tensor([t + 1 for _, t in chunk])  # +1 for BOS
            lp = torch.log_softmax(logits[torch.arange(len(chunk)), tg], dim=-1)
            out[i:i + b] = lp[:, order].cpu().numpy()
            i += b
        except RuntimeError as e:
            if b == 1:
                raise
            print(f"    batch OOM at b={b} ({str(e)[:80]}) -> halving", flush=True)
            b = max(1, b // 2)
    return out


if __name__ == "__main__":
    import esm
    device = get_device()
    print(f"Using device: {device}; BATCH={BATCH} N_BOOT={N_BOOT} "
          f"N_PERM={N_PERM} BRUTE_N={BRUTE_N} PHASE2_MAX={PHASE2_MAX or 'all'} "
          f"SEED={SEED}")

    seq = load_sequence(ROOT / "data" / "raw" / "P42898.fasta")
    av_seq = seq[:POS_222 - 1] + "V" + seq[POS_222:]
    assert seq[POS_222 - 1] == "A", f"residue 222 is {seq[POS_222-1]}, not A"

    wt_tab = pd.read_csv(PROC / "esm2_wt_scores.csv")
    av_tab = pd.read_csv(PROC / "esm2_a222v_bg_scores.csv")
    positions = sorted(set(wt_tab["position"]) | {POS_222})
    print(f"P (PLL sum set): {len(positions)} positions incl. 222")

    # ---- analysis set: script 32/33's exact join ---------------------------
    df = pd.read_csv(PROC / "phase5_analysis_table.csv")
    own = pd.read_csv(PROC / "own_context_metrics.csv")[["hgvs_pro", "own_e_b"]]
    df = df.merge(own, on="hgvs_pro", how="left").dropna(subset=["delta_esm"])
    df = df.reset_index(drop=True)
    print(f"Analysis set (delta_esm): {len(df)} variants, "
          f"{df['position'].nunique()} positions")
    print("\nLoading ESM-2 650M (already cached -- no new download)...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()
    ai = aa_indices(alphabet)                      # ESM vocab indices (logits)
    col = {aa: i for i, aa in enumerate(AA_LIST)}  # column indices (20-wide out)
    el("model-loaded")

    # ---- Phase 1: raw logP at every position, both backgrounds (2 passes
    #      per position) -> odds-identity gate G1 + global constant K -------
    print("\n" + "=" * 74)
    print("PHASE 1 -- raw masked log-probs, both backgrounds "
          f"({2*len(positions)} forward passes)")
    print("=" * 74)
    st_wt, st_av = [], []
    for p in positions:
        st_wt.append((seq[:p-1] + "<mask>" + seq[p:], p - 1))
        st_av.append((av_seq[:p-1] + "<mask>" + av_seq[p:], p - 1))
    raw_wt = batched_raw_logprobs(model, bc, st_wt, ai, device, BATCH)
    raw_av = batched_raw_logprobs(model, bc, st_av, ai, device, BATCH)
    pos_idx = {p: i for i, p in enumerate(positions)}

    def odds_gate(tab, raws, seqs, label):
        errs = []
        for _, r in tab.iterrows():
            p = int(r["position"])
            if p not in pos_idx:
                continue
            ref = seqs[p - 1]
            o = (raws[pos_idx[p], col[r["mut_aa"]]]
                 - raws[pos_idx[p], col[ref]])
            errs.append(abs(o - r["esm2_score" + ("_a222v_bg" if label == "av" else "")]))
        m = max(errs)
        print(f"  G1 odds identity ({label} bg, {len(errs)} rows): "
              f"max|raw-derived - cached| = {m:.3e}")
        return m

    g1 = max(odds_gate(wt_tab, raw_wt, seq, "wt"),
             odds_gate(av_tab, raw_av, av_seq, "av"))
    d_bg_wt222 = (raw_av[pos_idx[POS_222], col[seq[POS_222 - 1]]]
                  - raw_wt[pos_idx[POS_222], col[seq[POS_222 - 1]]])
    print(f"  G2 raw delta at 222 across backgrounds = {d_bg_wt222:.3e} "
          "(must be ~0: masked contexts identical)")
    if g1 > 1e-4 or abs(d_bg_wt222) > 1e-4:
        print("*** GATE FAIL -- cached odds not reproducible from fresh raws. "
              "Stop. ***")
        sys.exit(1)
    print("  G1/G2 PASS")

    # global constant K = sum_j [raw_av(wt_j) - raw_wt(wt_j)]  (v-independent)
    d_bg_wt = np.array([raw_av[pos_idx[p], col[seq[p - 1]]]
                        - raw_wt[pos_idx[p], col[seq[p - 1]]]
                        for p in positions])
    K = float(d_bg_wt.sum())
    print(f"  global constant K = sum_j delta_bg logP(wt_j) = {K:+.6f} "
          f"(sd across positions = {d_bg_wt.std():.5f})")
    el("phase1-done")

    # ---- Phase 2: L222 for every analysis-set variant (masked @222 with
    #      alt@p in context; one pass each, reads V and A) -------------------
    print("\n" + "=" * 74)
    print(f"PHASE 2 -- L222 term, {len(df)} variants "
          "(mask @222, variant substitution in context)")
    print("=" * 74)
    seqs222 = []
    n2 = PHASE2_MAX if PHASE2_MAX > 0 else len(df)
    score_df = df.iloc[:n2]
    if n2 < len(df):
        print(f"  PHASE2_MAX={n2} (SMOKE ONLY -- "
              f"{len(df)-n2} rows keep NaN delta_pll; reduced-n outputs "
              "are machinery checks, NOT results)")
    for _, r in score_df.iterrows():
        p, alt = int(r["position"]), r["mut_aa"]
        s = seq[:p-1] + alt + seq[p:]          # WT-seq + alt@p
        m222 = s[:POS_222 - 1] + "<mask>" + s[POS_222:]
        seqs222.append((m222, POS_222 - 1))
    raw222 = batched_raw_logprobs(model, bc, seqs222, ai, device, BATCH)
    l222 = raw222[:, col["V"]] - raw222[:, col["A"]]
    l222_full = pd.Series(np.nan, index=df.index)
    l222_full.iloc[:n2] = l222
    df["l222"] = l222_full
    df["delta_pll"] = df["delta_esm"] + df["l222"] + K   # whole-seq primary
    # strict {p,222}-subset PL: only the two variant-bearing positions,
    # no distal sum -- differs from primary by (Delta_bg logP(wt_p) - K),
    # a position-level offset.
    d_bg_p = np.array([d_bg_wt[pos_idx[int(p_)]] for p_ in df["position"]])
    df["delta_pll_subset"] = df["delta_esm"] + df["l222"] + d_bg_p
    print(f"  L222 (n={n2}): mean={np.nanmean(l222_full):+.5f} "
          f"sd={np.nanstd(l222_full):.5f} "
          f"min={np.nanmin(l222_full):+.5f} max={np.nanmax(l222_full):+.5f}")
    print(f"  delta_pll sd = {np.nanstd(df['delta_pll']):.5f} "
          f"(delta_esm sd = {df['delta_esm'].std():.5f})")

    null_set = df.dropna(subset=["own_e_b", "delta_pll"]).reset_index(drop=True)
    print(f"Null set (+own_e_b): {len(null_set)} variants, "
          f"{null_set['position'].nunique()} positions")
    assert (null_set["position"] != POS_222).all(), "variant at position 222"
    el("phase2-done")

    # ---- Phase 3: brute-force disclosure -- direct full sum, no freezing --
    print("\n" + "=" * 74)
    print(f"PHASE 3 -- direct un-frozen full-sum check on {BRUTE_N} variants "
          f"(seed {SEED}, {(BRUTE_N*2*len(positions))} forward passes)")
    print("=" * 74)
    rng = np.random.default_rng(SEED)
    sample = df.dropna(subset=["delta_pll"])
    sample = sample.iloc[rng.choice(len(sample),
                                    size=min(BRUTE_N, len(sample)),
                                    replace=False)]
    diffs = []
    for _, r in sample.iterrows():
        p, alt, dpll_fit = (int(r["position"]), r["mut_aa"],
                            r["delta_esm"] + r["l222"])
        pll = {}
        for tag, base in [("wt", seq), ("av", av_seq)]:
            s_alt = base[:p-1] + alt + base[p:]
            st = [(s_alt[:j-1] + "<mask>" + s_alt[j:], j - 1)
                  for j in positions]
            rr = batched_raw_logprobs(model, bc, st, ai, device, BATCH)
            res = np.array([col[s_alt[j - 1]] for j in positions])
            pll[tag] = float(rr[np.arange(len(positions)), res].sum())
        direct = pll["av"] - pll["wt"]
        diffs.append(direct - dpll_fit)   # = K + frozen-distal error
    diffs = np.array(diffs)
    err = diffs - K                       # frozen-distal error alone
    print(f"  direct - (delta_esm+L222): mean={diffs.mean():+.5f} "
          f"vs K={K:+.5f}  -> mean algebra residual = {diffs.mean()-K:+.5f}")
    print(f"  frozen-distal approximation error: sd={err.std():.5f} "
          f"max|e|={np.abs(err).max():.5f}  "
          f"(= {100*err.std()/np.nanstd(df['delta_pll']):.1f}% of sd(delta_pll), "
          f"n={len(sample)} disclosed)")
    direct_vals = (sample["delta_esm"] + sample["l222"]).to_numpy() + diffs
    fitted_vals = (sample["delta_esm"] + sample["l222"]).to_numpy() + K
    print(f"  (sample) spearman(direct full-sum, fitted frozen) = "
          f"{_spearman(direct_vals, fitted_vals):+.4f} n={len(sample)}")
    el("phase3-done")

    # ---- Phase 4: correlations, side by side with the original ------------
    print("\n" + "=" * 74)
    print(f"PHASE 4 -- PRIMARY correlations (position-cluster bootstrap, "
          f"N_BOOT={N_BOOT})")
    print("=" * 74)
    orig = pd.read_csv(PROC / "task32_delta_esm_primary.csv")
    o = orig[orig["stage"] == "primary"].set_index("quantity")["value"]
    print(f"  ORIGINAL delta_ESM (full n, script 32): own e.b rho="
          f"{o['signed, own e_b']:+.6f} | published e.b rho="
          f"{o['signed, published e.b']:+.6f}")
    if PHASE2_MAX:
        print("  *** PHASE2_MAX set: the rows below are reduced-n machinery "
              "checks, NOT results (see SESSION_LOG). ***")
    res_rows = []
    for xc, yc, lbl in [("delta_pll", "own_e_b", "PLL, signed, own e_b"),
                        ("delta_pll", "GI_folinate_independent",
                         "PLL, signed, published e.b"),
                        ("delta_pll_subset", "own_e_b",
                         "PLL({p,222}-subset), own e_b"),
                        ("delta_esm", "own_e_b",
                         "ORIGINAL delta_ESM, own e_b (rerun here)")]:
        sub = df.dropna(subset=[xc, yc])
        r = position_cluster_bootstrap(sub, "position", xc, yc,
                                       n_boot=N_BOOT, seed=SEED)
        print(f"  {lbl:44s} rho={r['observed_rho']:+.6f} "
              f"CI=[{r['ci_lo']:+.6f},{r['ci_hi']:+.6f}] "
              f"p={pstr(r['p_boot'], N_BOOT)} n={r['n_rows']}"
              f"{'  (crosses 0)' if r['ci_lo'] < 0 < r['ci_hi'] else ''}")
        res_rows.append({"stage": "primary", "quantity": lbl,
                         "rho": r["observed_rho"], "ci_lo": r["ci_lo"],
                         "ci_hi": r["ci_hi"], "p_boot": r["p_boot"],
                         "n": r["n_rows"]})
    el("phase4-done")

    # ---- Phase 5 (U2b): script 33's null code path on delta_pll -----------
    print("\n" + "=" * 74)
    print(f"PHASE 5 (U2b) -- SIGN-FLIP RE-DERIVATION NULL ({N_PERM} perms), "
          "script-33 machinery unchanged")
    print("=" * 74)
    ns = null_set.copy().reset_index(drop=True)
    ns["region"] = assign_region(ns["position"])
    rngn = np.random.default_rng(SEED)
    raw_fit = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw_fit)
    e2, Mse = fit["e2"], fit["M_se"]
    row_of = {h: i for i, h in enumerate(raw_fit["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in ns["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    own_eb = ns["own_e_b"].to_numpy()
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    dplus = np.abs(chk_p[ok] - own_eb[ok]).max()
    dminus = np.abs(chk_m[ok] + own_eb[ok]).max()
    print(f"  all-+1 flips reproduce own_e_b exactly: max|diff|={dplus:.3e}")
    print(f"  all--1 flips give exactly -own_e_b:     max|diff|={dminus:.3e}")
    if dplus > 1e-6:
        print("  *** SANITY CHECK FAILED (G3) -- row alignment wrong. Stop. ***")
        sys.exit(1)

    dv = ns["delta_pll"].to_numpy()
    adv = np.abs(dv)
    orig_null = pd.read_csv(PROC / "task33_delta_esm_nulls.csv")
    for pred, lbl, signed in [(dv, "signed delta_PLL vs signed e_b", True),
                              (adv, "absolute |delta_PLL| vs |e_b|", False)]:
        obs = _spearman(pred, own_eb if signed else np.abs(own_eb))
        null = np.empty(N_PERM)
        for p_i in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rngn.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(pred)
            null[p_i] = _spearman(pred[g], eb_p[g] if signed else np.abs(eb_p[g]))
        pv = float((np.abs(null) >= abs(obs)).mean())
        excess = obs - null.mean()
        frac = 1 - abs(excess) / abs(obs) if obs != 0 else np.nan
        print(f"  {lbl}")
        print(f"    observed={obs:+.4f}  null mean={null.mean():+.4f} "
              f"sd={null.std():.4f}  p={pstr(pv, N_PERM)}")
        print(f"    excess over null={excess:+.4f}  "
              f"({100*frac:.0f}% of the raw value is structural artifact)")
        print(f"    -> {'SURVIVES' if pv < 0.05 else 'does NOT survive'}")
        if signed:
            centred = abs(null.mean()) < 2 * null.std() / np.sqrt(N_PERM) * 3
            print(f"    null-centring check: null mean {'IS' if centred else 'is NOT'} "
                  f"consistent with zero -- "
                  f"{'machinery behaving' if centred else 'INVESTIGATE'}")
            ov = orig_null[(orig_null["null"] == "signflip") &
                           orig_null["variant"].str.contains("signed delta_ESM")]
            if len(ov):
                print(f"    ORIGINAL delta_ESM side-by-side: "
                      f"observed={ov.iloc[0]['observed']:+.4f} "
                      f"null mean={ov.iloc[0]['null_mean']:+.4f} "
                      f"p={ov.iloc[0]['p']:.4f}")
        res_rows.append({"stage": "null1_signflip", "quantity": lbl,
                         "observed": obs, "null_mean": float(null.mean()),
                         "null_sd": float(null.std()), "excess": excess,
                         "frac_artifact": frac, "p": pv, "n_perm": N_PERM,
                         "survives": pv < 0.05})

    print("\n  NULL 2 -- POSITION-BLOCK PERMUTATION (weaker; association only)")
    sub = ns[["position", "delta_pll", "own_e_b"]].dropna()
    blocks = [g["delta_pll"].to_numpy() for _, g in sub.groupby("position")]
    ebv = np.concatenate([g["own_e_b"].to_numpy()
                          for _, g in sub.groupby("position")])
    obs2 = _spearman(np.concatenate(blocks), ebv)
    null2 = np.empty(N_PERM)
    for p_i in range(N_PERM):
        null2[p_i] = _spearman(
            np.concatenate([blocks[i] for i in rngn.permutation(len(blocks))]),
            ebv)
    pv2 = float((np.abs(null2) >= abs(obs2)).mean())
    print(f"    observed={obs2:+.4f}  null mean={null2.mean():+.4f} "
          f"sd={null2.std():.4f}  p={pstr(pv2, N_PERM)}")
    res_rows.append({"stage": "null2_position_block", "quantity": "signed",
                     "observed": obs2, "null_mean": float(null2.mean()),
                     "null_sd": float(null2.std()), "p": pv2,
                     "n_perm": N_PERM, "survives": pv2 < 0.05})

    print("\n  REGION CHECK (sign-flip null, per region; script-33 parity)")
    n_reg = max(200, N_PERM // 10)
    for rg in sorted(REGION_BOUNDS):
        m = (ns["region"] == rg).to_numpy()
        if ns.loc[m, "position"].nunique() < 15:
            print(f"    region {rg}: SKIPPED "
                  f"({ns.loc[m, 'position'].nunique()} positions)")
            continue
        obs_r = _spearman(dv[m], own_eb[m])
        nr = np.empty(n_reg)
        for p_i in range(n_reg):
            eb_p, _, _ = wls_line(Rs[m] * rngn.choice([-1.0, 1.0],
                                                      size=Rs[m].shape),
                                  Ss[m], CONCS, Vs[m])
            g = np.isfinite(eb_p) & np.isfinite(dv[m])
            nr[p_i] = _spearman(dv[m][g], eb_p[g])
        pvr = float((np.abs(nr) >= abs(obs_r)).mean())
        lo, hi = REGION_BOUNDS[rg]
        print(f"    region {rg} ({lo}-{hi}) observed={obs_r:+.4f} "
              f"null mean={nr.mean():+.4f} excess={obs_r-nr.mean():+.4f} "
              f"p={pstr(pvr, n_reg)}")
        res_rows.append({"stage": "null_signflip_region",
                         "quantity": f"region_{rg}", "observed": obs_r,
                         "null_mean": float(nr.mean()),
                         "null_sd": float(nr.std()),
                         "excess": obs_r - nr.mean(), "p": pvr,
                         "n_perm": n_reg, "survives": pvr < 0.05})

    # ---- save --------------------------------------------------------------
    cols = ["hgvs_pro", "position", "mut_aa", "delta_esm", "l222",
            "delta_pll", "delta_pll_subset"]
    cols = [c for c in cols if c in ns.columns]
    out1 = PROC / ("task67_u2_pll_scores_smoke.csv" if PHASE2_MAX
                   else "task67_u2_pll_scores.csv")
    ns[cols].to_csv(out1, index=False)
    out2 = PROC / ("task67_u2_results_smoke.csv" if PHASE2_MAX
                   else "task67_u2_results.csv")
    pd.DataFrame(res_rows).to_csv(out2, index=False)
    print(f"\nSaved to {out1}\nSaved to {out2}")
    print("\nLIMITATIONS (stated here, not only in a writeup):")
    print("  * Distal context is frozen at each background's WT sequence;")
    print(f"    the dropped term has sd={err.std():.5f} max={np.abs(err).max():.5f}")
    print(f"    on the n={len(sample)} brute-force sample above.")
    print("  * One-directional: the atlas measures v in the A222V background")
    print("    only (no symmetrisation) -- same caveat as script 32.")
    print("  * P-values apply to own_e_b; transfer to published e.b only as")
    print("    far as the two agree (script 17).")
    print(f"  * Total runtime {time.time()-T0:.0f}s.")
