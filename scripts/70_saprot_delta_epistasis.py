"""
Script 70 (tasks Z3e/Z3f/Z3g/Z3h): SaProt structure-aware masked-marginal
delta between the A222V and WT backgrounds, correlated with e.b.

PRE-REGISTRATION (written before the first run; do not change after
seeing results -- any later change must be disclosed in CLOSEOUT_LOG as
post-hoc). Every convention below was fixed by the closeout task doc or
by an already-settled project decision before this file existed.

Z3e -- FROZEN-STRUCTURE CONVENTION (stated explicitly here, per task):
  Both scoring passes (WT background and A222V background) reuse the
  SAME 3Di structure tokens from chain A of 6FCX; only the amino-acid
  channel changes, at residue 222 only (A->V). The backbone/fold is
  assumed effectively unchanged by a single substitution. This is
  standard SaProt DMS practice (noted as "first contact" in this repo
  by U4a's entry) and it is an ASSUMPTION, not a measured fact: no
  re-folding is done, no 3Di token differs between backgrounds. The
  assumption would matter only if A222V materially rearranged the
  local fold; nothing in this script tests that.

SCORE DEFINITION (Z3d's verified reuse path -- their code, not ours):
  S is exactly SaProt's own `predict_pos_mut` arithmetic
  (data/external/SaProt/code/model/saprot/saprot_foldseek_mutation_model.py
  line 316), transcribed line-for-line, loaded through their own
  `utils.esm_loader.load_esm_saprot` on `SaProt_650M_PDB.pt`:
    - fused sequence = chain-A residue i -> "AA" + lowercase-3Di
      (their combined_seq, produced by their get_struc_seq);
    - mask site = "#" + the site's OWN 3Di letter (structure channel
      stays visible at the masked site);
    - read model row `pos` (BOS shift: fused residue i sits at row i);
    - S(bg, p, alt) = log( sum_{s in 21 struc} P(alt+s) /
                            sum_{s in 21 struc} P(ori+s) ),
      i.e. AA marginalized over all 21 struc states (their block slice
      [st : st+len(foldseek_struc_vocab)]). Verified empirically in
      Z3d: block order, mask tokens, self-logodds == 0, probs sum 1.
  Only adaptation: batching, and running it on both backgrounds.

  delta_SaProt(v) = S(A222V bg, p_v, alt_v) - S(WT bg, p_v, alt_v)
  (same construction as script 12/32's delta_ESM).

SCORING SET (Z3f, decisions 1+2 already settled):
  - chain A only; the 59 unresolved atlas positions (positions 2-39,
    161-171, 392-396, 652-656 -- no chain-A coordinates) are EXCLUDED,
    never imputed. Scoring covers all 596 resolved residues; variant
    rows at unresolved positions are dropped and COUNTED, then compared
    against V2/ThermoMPNN's own exclusion (1,046 rows at the same 59
    positions) -- a mismatch is reported and explained, not assumed
    away (Z3f's explicit instruction).
  - Analysis set for statistics follows script 32's convention exactly:
    task32_analysis_table.csv rows with delta_esm & own_e_b non-null
    (n=10,757, 654 positions), then minus the unresolved-position rows.

STATISTICS (Z3g, script 32/33 conventions reused, not reinvented):
  - correlate delta_SaProt against own_e_b AND published e.b
    (= GI_folinate_independent; script 32 line 91's own mapping of
    "published e.b"), signed primary + absolute secondary (script 32's
    four PAIRS), position_cluster_bootstrap, N_BOOT=10000, seed=0;
  - sign-flip re-derivation null through script 33's code path:
    SAME imports (wls_line, CONCS, rebuild_interaction_fit, _spearman,
    assign_region, REGION_BOUNDS), loop structure copied
    line-for-line, including script 33's +/-1 identity checks (exit 1
    on failure), Null-2 position-block arm, and its region arm
    (script 67's established precedent for "reuse the code path");
  - Z3h: same four-region check as script 32d (per-region
    position-cluster CI, overlap-vs-pooled flag, >=15-position gate).

PRE-RUN GATES (fail -> sys.exit(1), no retry-with-more-N):
  G1  their get_struc_seq(6FCX, chain A) == the Z3c token file
      (re-derives Z3c through their own pipeline);
  G2  block order: idx(aa+struc[0])+k == idx(aa+struc[k]) for all 441;
  G3  batched forward == single forward on the same masked input
      (max |logit diff| < 1e-3; fp32/MPS tolerance -- the CPU smoke
      typically lands below 1e-5);
  G4  self-logodds (ori vs ori) exactly 0.0 on a sampled position;
  G5  no atlas variant sits at position 222 (script 67 verified the
      same on phase5; re-verified here because the background swap
      assumes it);
  G6  script 33's +/-1 wls identity checks (stats stage);
  G7  excluded-position accounting: the 59 unresolved positions are
      exactly positions 2-39/161-171/392-396/652-656, and V2's
      exclusion reproduces 1,046 rows (report any divergence).

ENV: N_BOOT, N_PERM (both default 10000), STAGE=score|stats|all,
     SMOKE=1 (CPU, first 4 positions, N_BOOT/N_PERM capped at 300,
     outputs suffixed _smoke), BATCH (default 16), SEED=0 fixed.
Smoke before full (AGENTS s1). Device: CPU under SMOKE, MPS otherwise
(this run is scheduled around Z2a/Z2c -- GPU contention would corrupt
a timing measurement -- decided in CLOSEOUT_LOG, not here).
Outputs: data/processed/task_Z3f_saprot_scores.csv[._smoke],
         data/processed/task_Z3g_saprot_delta.csv[._smoke],
         data/processed/task_Z3g_saprot_summary.csv[._smoke].
Limitations are printed by the script itself (AGENTS s6).
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "data" / "external" / "SaProt" / "code"))

from scripts.lib.stats import position_cluster_bootstrap, _spearman
from scripts.lib.regions import assign_region, REGION_BOUNDS
from scripts.lib.own_context import wls_line, CONCS
from scripts.lib.stats_ext import rebuild_interaction_fit
from utils.esm_loader import load_esm_saprot
from utils.constants import foldseek_seq_vocab, foldseek_struc_vocab, aa_list

N_BOOT = int(os.environ.get("N_BOOT", 10000))
N_PERM = int(os.environ.get("N_PERM", 10000))
STAGE = os.environ.get("STAGE", "all")
SMOKE = os.environ.get("SMOKE", "0") == "1"
BATCH = int(os.environ.get("BATCH", 16))
SEED = 0
PROC = REPO / "data" / "processed"
RAW = REPO / "data" / "raw" / "mthfrModel"
CODE = REPO / "data" / "external" / "SaProt" / "code"
FSBIN = str(REPO / "data" / "external" / "foldseek" / "foldseek" / "bin" / "foldseek")
SUFFIX = "_smoke" if SMOKE else ""
N_BOOT = min(N_BOOT, 300) if SMOKE else N_BOOT
N_PERM = min(N_PERM, 300) if SMOKE else N_PERM
SCORES = PROC / f"task_Z3f_saprot_scores{SUFFIX}.csv"
DELTAS = PROC / f"task_Z3g_saprot_delta{SUFFIX}.csv"
SUMMARY = PROC / f"task_Z3g_saprot_summary{SUFFIX}.csv"


def pstr(p, n):
    return f"<{1.0/n:.4f}" if p == 0 else f"{p:.4f}"


def load_chain_tokens():
    z3c = pd.read_csv(PROC / "task_Z3c_6fcx_chainA_3di.csv")
    return z3c["res_num"].tolist(), [a + d.lower() for a, d in zip(z3c["aa"], z3c["di3"])]


def stage_score(device):
    t0 = time.time()
    sys.path.insert(0, str(CODE))
    from utils.foldseek_util import get_struc_seq

    resnums, pairs = load_chain_tokens()
    L = len(pairs)
    print(f"[score] chain-A fused length {L} residues {resnums[0]}..{resnums[-1]}")

    # G1 -- their own get_struc_seq must reproduce the Z3c tokens
    got = get_struc_seq(FSBIN, str(REPO / "data/raw/6FCX.pdb"), ["A"], plddt_mask=False)
    their_seq, their_struc, _ = got["A"]
    mine_aa = "".join(p[0] for p in pairs)
    mine_di3 = "".join(p[1] for p in pairs)
    # case note: fused pairs store 3Di lowercased (their combined_seq
    # convention) while get_struc_seq's struc channel is uppercase --
    # fold their dump to lowercase before the exact-equality compare
    # (criteria unchanged: exact token-for-token equality; verified
    # case-sensitively against the raw Z3c column during diagnosis)
    g1 = their_seq == mine_aa and their_struc.lower() == mine_di3
    print(f"[G1] their get_struc_seq == Z3c tokens: {g1}")
    if not g1:
        print("G1 FAILED -- token pipelines disagree. Stop.")
        sys.exit(1)

    model, alphabet = load_esm_saprot(str(REPO / "data/external/SaProt/SaProt_650M_PDB.pt"))
    model.eval()
    model = model.to(device)

    # G2 -- block order (their slice assumption, in THIS alphabet)
    bad = [1 for aa in foldseek_seq_vocab
           if any(alphabet.get_idx(aa + foldseek_struc_vocab[k])
                  != alphabet.get_idx(aa + foldseek_struc_vocab[0]) + k
                  for k in range(len(foldseek_struc_vocab)))]
    print(f"[G2] AA blocks consecutive from aa+struc[0]: {not bad}")
    if bad:
        print("G2 FAILED. Stop.")
        sys.exit(1)
    st0 = {aa: alphabet.get_idx(aa + foldseek_struc_vocab[0]) for aa in foldseek_seq_vocab}

    # backgrounds: identical except residue 222's AA channel (frozen 3Di)
    i222 = resnums.index(222)
    assert pairs[i222][0] == "A", f"residue 222 is {pairs[i222][0]}, expected A (U4a verified ALA)"
    av_pairs = list(pairs)
    av_pairs[i222] = "V" + pairs[i222][1]
    print(f"[bg] A222V swaps fused token {pairs[i222]} -> {av_pairs[i222]} "
          f"at index {i222}; all other {L-1} tokens identical (frozen structure)")

    npos = 4 if SMOKE else L
    pos_list = list(range(1, npos + 1))

    def masked_ids(base_pairs, pos1):
        m = list(base_pairs)
        m[pos1 - 1] = "#" + m[pos1 - 1][1]
        return [alphabet.cls_idx] + [alphabet.get_idx(p) for p in m] + [alphabet.eos_idx]

    def forward_rows(id_rows):
        with torch.no_grad():
            logits = model(torch.tensor(id_rows, device=device))["logits"]
        return logits

    # G3 -- batched == single
    ids_one = masked_ids(pairs, 1)
    lg_one = forward_rows([ids_one])
    lg_bat = forward_rows([masked_ids(pairs, p) for p in pos_list[:min(4, npos)]])
    g3 = float((lg_one[0, 1] - lg_bat[0, 1]).abs().max())
    print(f"[G3] batched vs single forward, max|diff| = {g3:.2e} (limit 1e-3): {g3 < 1e-3}")
    if g3 >= 1e-3:
        print("G3 FAILED. Stop.")
        sys.exit(1)

    # G4 -- self-logodds exactly 0
    p1 = 1
    lg = forward_rows([masked_ids(pairs, p1)])
    probs = lg.softmax(dim=-1)[0, p1]
    ori = pairs[p1 - 1][0]
    s_ = torch.log(probs[st0[ori]: st0[ori] + 21].sum() / probs[st0[ori]: st0[ori] + 21].sum())
    g4 = s_.item()
    print(f"[G4] self-logodds at fused pos {p1} (residue {resnums[p1-1]}, {ori}) = {g4!r}: {g4 == 0.0}")
    if g4 != 0.0:
        print("G4 FAILED. Stop.")
        sys.exit(1)

    rows = []
    t_sc = time.time()
    for bg_name, bg_pairs in (("wt", pairs), ("av", av_pairs)):
        for b0 in range(0, len(pos_list), BATCH):
            batch_pos = pos_list[b0:b0 + BATCH]
            id_rows = [masked_ids(bg_pairs, p) for p in batch_pos]
            logits = forward_rows(id_rows)
            for j, pos1 in enumerate(batch_pos):
                probs = logits.softmax(dim=-1)[j, pos1]
                ori = bg_pairs[pos1 - 1][0]
                ori_p = probs[st0[ori]: st0[ori] + 21].sum()
                for aa in aa_list:
                    mut_p = probs[st0[aa]: st0[aa] + 21].sum()
                    rows.append({"bg": bg_name, "fused_pos": pos1,
                                 "res_num": resnums[pos1 - 1], "ori_aa": ori,
                                 "mut_aa": aa,
                                 "logodds": torch.log(mut_p / ori_p).item()})
        print(f"[score] {bg_name} background done "
              f"({time.time() - t_sc:.0f}s elapsed)", flush=True)
    df = pd.DataFrame(rows)
    wide = df.pivot_table(index=["res_num", "ori_aa", "mut_aa"],
                          columns="bg", values="logodds").reset_index()
    wide.columns.name = None
    wide = wide.rename(columns={"wt": "wt_logodds", "av": "av_logodds"})
    wide.to_csv(SCORES, index=False)
    print(f"[score] saved {SCORES} ({len(wide)} rows = {npos} positions x 20 alts; "
          f"smoke-limited={SMOKE})")
    print(f"[score] stage wall-clock {time.time() - t0:.0f}s on device={device}")
    return wide


def stage_stats():
    t0 = time.time()
    wide = pd.read_csv(SCORES)
    resnums, pairs = load_chain_tokens()
    resolved = set(resnums)

    # G5 -- no variant sits at 222
    raw_df = pd.read_csv(PROC / "task32_analysis_table.csv")
    full = raw_df.dropna(subset=["delta_esm", "own_e_b"]).copy()
    g5 = (full["position"] == 222).sum()
    print(f"[G5] variants at position 222 in analysis set: {g5} (expect 0): {g5 == 0}")
    if g5:
        print("G5 FAILED. Stop.")
        sys.exit(1)

    # G7 -- unresolved-position accounting (59 positions; V2's 1,046)
    unresolved = sorted(set(range(2, 657)) - resolved)
    expect_runs = (list(range(2, 40)) + list(range(161, 172))
                   + list(range(392, 397)) + list(range(652, 657)))
    g7_runs = unresolved == expect_runs
    v2 = pd.read_csv(PROC / "task_V2_thermompnn_ddg.csv")
    v2_excl = int(v2["position"].isin(unresolved).sum())
    p5 = pd.read_csv(PROC / "phase5_analysis_table.csv")
    p5_excl = int(p5["position"].isin(unresolved).sum())
    print(f"[G7] unresolved atlas positions: {len(unresolved)} "
          f"== 59 and == 2-39/161-171/392-396/652-656: {g7_runs and len(unresolved) == 59}")
    print(f"[G7] phase5 base (n={len(p5)}) rows at those positions: {p5_excl} "
          f"(V2's own figure: 1,046) -> {'MATCH' if p5_excl == 1046 else 'DIVERGENCE'}")
    print(f"[G7] task_V2 rows present at those positions: {v2_excl} (expect 0: V2 "
          f"dropped them at construction -- structure-based scoring cannot cover "
          f"unresolved residues)")
    if not (g7_runs and len(unresolved) == 59):
        print("G7 FAILED (unexpected unresolved set). Stop.")
        sys.exit(1)

    full["excluded_unresolved"] = full["position"].isin(unresolved)
    n_excl = int(full["excluded_unresolved"].sum())
    df = full[~full["excluded_unresolved"]].copy()
    if SMOKE:
        keep = sorted(wide["res_num"].unique().tolist())
        df = df[df["position"].isin(keep)].copy()
        print(f"[SMOKE] stats restricted to the {len(keep)} scored positions "
              f"{keep} (smoke scores only the first 4 residues)")
    ori_map = wide.drop_duplicates("res_num").set_index("res_num")["ori_aa"]
    wt_ok = int((df["wt_aa"] == df["position"].map(ori_map)).sum())
    print(f"[Z3f] analysis set {len(full)} -> excluded at 59 unresolved positions: "
          f"{n_excl} rows; scored set {len(df)} ({df['position'].nunique()} positions)")
    print(f"[Z3f] reconciliation vs V2's 1,046: that figure = phase5 rows at the "
          f"same 59 positions (measured here: {p5_excl}); ours ({n_excl}) = the "
          f"subset of those inside script 32's pre-registered 10,757-row set after "
          f"delta_esm/own_e_b filtering ({p5_excl - n_excl} of the 1,046 are not "
          f"in it); task_V2 itself holds {v2_excl} unresolved rows -- dropped at "
          f"its construction. Same 59 positions, three bases, all consistent.")
    print(f"[Z3f] scored set vs ThermoMPNN's coverage: ours {len(full) - n_excl} "
          f"vs task_V2 {len(v2)} rows ({int(v2['own_e_b'].notna().sum())} with "
          f"own_e_b) -- bases differ by design (script 32 = ESM-2+e.b filters; "
          f"V2 = ddG+structure filters), so an exact match is NOT expected and "
          f"is not asserted.")
    print(f"[Z3f] wt_aa agrees with chain-A ori_aa on all scored rows: "
          f"{wt_ok == len(df)} ({wt_ok}/{len(df)})")
    if wt_ok != len(df):
        print("wt_aa/ori_aa identity FAILED. Stop.")
        sys.exit(1)

    # join delta_SaProt
    m = df.merge(wide, left_on=["position", "mut_aa"],
                 right_on=["res_num", "mut_aa"], how="left", validate="many_to_one")
    miss = int(m["wt_logodds"].isna().sum())
    print(f"[Z3g] join miss (mut_aa not among scored alts at that residue): {miss}")
    if miss:
        print("join misses present. Stop.")
        sys.exit(1)
    m["delta_saprot"] = m["av_logodds"] - m["wt_logodds"]
    m["region"] = assign_region(m["position"])
    m_out = m[["hgvs_pro", "position", "wt_aa", "mut_aa", "region",
               "wt_logodds", "av_logodds", "delta_saprot", "own_e_b",
               "GI_folinate_independent"]].rename(
        columns={"GI_folinate_independent": "pub_e_b"})
    m_out.to_csv(DELTAS, index=False)

    m["pub_e_b"] = m["GI_folinate_independent"]  # script 32 line 91's mapping
    rows = []
    PAIRS_ = [("delta_saprot", "own_e_b", "signed, own e_b"),
              ("delta_saprot", "pub_e_b", "signed, published e.b"),
              ("abs_saprot", "abs_own", "absolute, own e_b"),
              ("abs_saprot", "abs_pub", "absolute, published e.b")]
    m["abs_saprot"] = m["delta_saprot"].abs()
    m["abs_own"] = m["own_e_b"].abs()
    m["abs_pub"] = m["GI_folinate_independent"].abs()
    print("\n" + "=" * 74)
    print(f"Z3g  PRIMARY -- delta_SaProt vs e.b  (N_BOOT={N_BOOT}, seed={SEED})")
    print("=" * 74)
    for x, y, lbl in PAIRS_:
        r = position_cluster_bootstrap(m, "position", x, y, n_boot=N_BOOT, seed=SEED)
        print(f"  {lbl}: rho={r['observed_rho']:+.4f} "
              f"CI=[{r['ci_lo']:+.4f},{r['ci_hi']:+.4f}] p={pstr(r['p_boot'], N_BOOT)} "
              f"n={r['n_rows']} pos={r['n_clusters']}")
        rows.append({"stage": "primary", "quantity": lbl,
                     "value": r["observed_rho"], "ci_lo": r["ci_lo"],
                     "ci_hi": r["ci_hi"], "p": r["p_boot"],
                     "n": r["n_rows"],
                     "ci_includes_zero": bool(r["ci_lo"] <= 0 <= r["ci_hi"])})
    # comparison anchor
    print(f"  [anchor] script 32's single-position delta_ESM signed own e_b = "
          f"-0.0881 (n=10,757); our n = {len(m)} after unresolved exclusions")

    # ---- script 33's sign-flip code path (same imports, same loop) ----
    rng = np.random.default_rng(SEED)
    raw = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    fit = rebuild_interaction_fit(raw)
    e2, Mse = fit["e2"], fit["M_se"]
    row_of = {h: i for i, h in enumerate(raw["hgvs"].to_numpy())}
    src = np.array([row_of[h] for h in m["hgvs_pro"]])
    Rs, Ss, Vs = e2["resid"][src], Mse[src], e2["valid"][src]

    print("\n" + "=" * 74)
    print("SANITY CHECKS (script 33's +/-1 identity checks -- test the test)")
    print("=" * 74)
    chk_p, _, _ = wls_line(Rs * 1.0, Ss, CONCS, Vs)
    chk_m, _, _ = wls_line(Rs * -1.0, Ss, CONCS, Vs)
    own_eb = m["own_e_b"].to_numpy()
    ok = np.isfinite(chk_p) & np.isfinite(own_eb)
    d1 = float(np.abs(chk_p[ok] - own_eb[ok]).max())
    d2 = float(np.abs(chk_m[ok] + own_eb[ok]).max())
    print(f"  [G6] all-+1 flips reproduce own_e_b exactly: max|diff|={d1:.3e}")
    print(f"  [G6] all--1 flips give exactly -own_e_b:     max|diff|={d2:.3e}")
    if d1 > 1e-6:
        print("  *** G6 FAILED -- row alignment wrong. Stop. ***")
        sys.exit(1)

    dv = m["delta_saprot"].to_numpy()
    adv = np.abs(dv)
    print("\n" + "=" * 74)
    print(f"NULL 1 -- SIGN-FLIP RE-DERIVATION ({N_PERM} permutations; script 33's path)")
    print("=" * 74)
    for pred, lbl, signed in [(dv, "signed delta_SaProt vs signed e_b", True),
                              (adv, "absolute |delta_SaProt| vs |e_b|", False)]:
        obs = _spearman(pred, own_eb if signed else np.abs(own_eb))
        null = np.empty(N_PERM)
        for p in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(pred)
            null[p] = _spearman(pred[g], eb_p[g] if signed else np.abs(eb_p[g]))
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
                  f"consistent with zero -- {'machinery behaving' if centred else 'INVESTIGATE'}")
        rows.append({"null": "signflip", "variant": lbl, "observed": obs,
                     "null_mean": float(null.mean()), "null_sd": float(null.std()),
                     "excess_over_null": excess, "frac_artifact": frac,
                     "p": pv, "n_perm": N_PERM, "survives": pv < 0.05})

    print("\n" + "=" * 74)
    print(f"NULL 2 -- POSITION-BLOCK PERMUTATION ({N_PERM}; weaker; association only)")
    print("=" * 74)
    sub = m[["position", "delta_saprot", "own_e_b"]].dropna()
    blocks = [g["delta_saprot"].to_numpy() for _, g in sub.groupby("position")]
    ebv = np.concatenate([g["own_e_b"].to_numpy() for _, g in sub.groupby("position")])
    obs2 = _spearman(np.concatenate(blocks), ebv)
    null2 = np.empty(N_PERM)
    for p in range(N_PERM):
        null2[p] = _spearman(
            np.concatenate([blocks[i] for i in rng.permutation(len(blocks))]), ebv)
    pv2 = float((np.abs(null2) >= abs(obs2)).mean())
    print(f"  observed={obs2:+.4f}  null mean={null2.mean():+.4f} "
          f"sd={null2.std():.4f}  p={pstr(pv2, N_PERM)}")
    print("  This asks whether the pairing beats chance, NOT whether the")
    print("  interaction exceeds measurement noise. Null 1 is the real test.")
    rows.append({"null": "position_block", "variant": "signed", "observed": obs2,
                 "null_mean": float(null2.mean()), "null_sd": float(null2.std()),
                 "p": pv2, "n_perm": N_PERM, "survives": pv2 < 0.05})

    # ---- Z3h: script 32d's four-region check (bootstrap CIs) ----
    print("\n" + "=" * 74)
    print("Z3h  REGION CHECK (script 32d convention)")
    print("=" * 74)
    pooled = position_cluster_bootstrap(m, "position", "delta_saprot", "own_e_b",
                                        n_boot=N_BOOT, seed=SEED)
    print(f"  pooled rho={pooled['observed_rho']:+.4f} "
          f"CI=[{pooled['ci_lo']:+.4f},{pooled['ci_hi']:+.4f}] n={pooled['n_rows']}")
    for rg in sorted(REGION_BOUNDS):
        sub_r = m[m["region"] == rg]
        if sub_r["position"].nunique() < 15:
            print(f"    region {rg} SKIPPED ({sub_r['position'].nunique()} positions)")
            continue
        res = position_cluster_bootstrap(sub_r, "position", "delta_saprot", "own_e_b",
                                         n_boot=N_BOOT, seed=SEED)
        ov = not (res["ci_hi"] < pooled["ci_lo"] or res["ci_lo"] > pooled["ci_hi"])
        lo, hi = REGION_BOUNDS[rg]
        print(f"    region {rg} ({lo}-{hi}) rho={res['observed_rho']:+.4f} "
              f"CI=[{res['ci_lo']:+.4f},{res['ci_hi']:+.4f}] p={pstr(res['p_boot'], N_BOOT)} "
              f"n={res['n_rows']} pos={res['n_clusters']}"
              f"{'' if ov else '  <-- does NOT overlap pooled'}")
        rows.append({"stage": "region", "quantity": f"region_{rg}",
                     "value": res["observed_rho"], "ci_lo": res["ci_lo"],
                     "ci_hi": res["ci_hi"], "p": res["p_boot"],
                     "n": res["n_rows"], "overlaps_pooled": ov})

    out = pd.DataFrame(rows)
    out.to_csv(SUMMARY, index=False)
    print(f"\n[saved] {DELTAS.name} + {SUMMARY.name} "
          f"(rows: primary=4, nulls, regions)")
    print("P-values apply to own_e_b (primary). Transfer to the published e.b only")
    print("as far as the two agree (script 17 prints that correlation).")
    print("LIMITATIONS (printed here per AGENTS s6): frozen-structure assumption")
    print("(Z3e docstring) is untested by this script; chain-A-only tokens exclude")
    print("the 59 unresolved positions (never imputed); reproduction of script 33's")
    print("path is a unit test of consistency, not independent evidence.")
    print(f"[stats] stage wall-clock {time.time() - t0:.0f}s")


if __name__ == "__main__":
    print(f"script 70 | STAGE={STAGE} SMOKE={SMOKE} N_BOOT={N_BOOT} N_PERM={N_PERM} "
          f"SEED={SEED} BATCH={BATCH}")
    if STAGE not in ("score", "stats", "all"):
        print(f"unknown STAGE={STAGE}"); sys.exit(2)
    if SMOKE:
        dev = torch.device("cpu")
    else:
        dev = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    print(f"device={dev}")
    t0 = time.time()
    if STAGE in ("score", "all"):
        stage_score(dev)
    if STAGE in ("stats", "all"):
        stage_stats()
    print(f"[total] {time.time()-t0:.0f}s")
