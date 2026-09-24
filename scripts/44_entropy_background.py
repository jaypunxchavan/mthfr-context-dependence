"""
Task B1c (review-triage): per-position entropy of ESM-2's output
distribution, WT background vs A222V background.

WHY
---
B1a/B1b found the delta_ESM <-> e.b correlation survives controlling for
S(v|WT) and w.fitness, but the sharper "generic flattening" version of the
confound lives at the distribution level: if merely PRESENTING the V222
residue makes ESM-2's masked-position distribution flatter (higher entropy)
everywhere, then delta_ESM could be a generic consequence of distribution
flattening rather than anything epistasis-specific. This computes, for each
position, the entropy of the masked-position amino-acid distribution on
BOTH backgrounds and compares them pairwise.

PRE-REGISTERED DECISION RULE (fixed before running; AGENTS.md §6):
  * Primary statistic: mean paired dH = H(A222V bg) - H(WT bg) over the
    sampled positions, with a position-bootstrap CI (positions are the
    sampling unit; AGENTS.md §3).
  * "Generic flattening supported" iff mean dH > 0 AND the 95% CI excludes
    0. Effect size (mean dH relative to mean H_WT) reported alongside —
    a CI excluding 0 alone is not a finding at any n (AGENTS.md §3).
  * Entropy primary = 20 amino acids, renormalized (nats). Full-vocab
    entropy reported as a secondary column, not used for the verdict.
  * Position 222 is force-included: masking position 222 gives an IDENTICAL
    input in both backgrounds, so dH at position 222 must be exactly 0.
    This is the built-in identity check (AGENTS.md §4); failure => exit(1).

RUN RESOLUTION:
  N_POS env var (default 656 = all positions). Timed on this machine:
  ~0.53 s/forward on MPS, so full 656x2 = ~11.5-12 min > the 10-minute
  budget -> tonight's run uses N_POS=500 (random positions, SEED fixed),
  which is a REDUCED-RESOLUTION run and should be rerun at N_POS=656 later.
  Batch size 16 (timed: no speedup over batch 1 for this model on MPS,
  kept for throughput only).

LIMITATION: only one alternate background exists; dH is a paired property
of positions, not of variants, so no variant-level inference is made.
"""
import sys, os, time, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import torch
import esm
from scripts.lib.sequence import load_sequence, verify_sequence
from scripts.lib.esm_scoring import get_device

N_POS = int(os.environ.get("N_POS", 656))
N_BOOT = int(os.environ.get("N_BOOT", 10000))
BATCH = int(os.environ.get("BATCH", 16))
SEED = 0
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
AA = list("ACDEFGHIKLMNPQRSTVWY")


def entropy_batch(model, alphabet, bc, seqs, positions, device):
    """Entropy of masked-position distribution for each (seq, pos).
    Returns (H20, Hfull) in nats. positions are 1-indexed."""
    masked = [s[:p - 1] + "<mask>" + s[p:] for s, p in zip(seqs, positions)]
    _, _, toks = bc([("q", m) for m in masked])
    toks = toks.to(device)
    with torch.no_grad():
        out = model(toks, repr_layers=[], return_contacts=False)
    lp = torch.log_softmax(out["logits"], dim=-1)          # (B, L, V)
    tok_pos = np.array(positions)                           # token index == 1-based pos
    sel = lp[torch.arange(len(positions)), tok_pos, :]      # (B, V)
    p_full = sel.exp()
    H_full = -(p_full * sel).sum(dim=1)
    aa_idx = torch.tensor([alphabet.get_idx(a) for a in AA])
    pa = p_full[:, aa_idx]
    pa = pa / pa.sum(dim=1, keepdim=True)
    lpa = torch.log(pa.clamp_min(1e-30))
    H20 = -(pa * lpa).sum(dim=1)
    if device.type == "mps":
        torch.mps.synchronize()
    return H20.cpu().numpy(), H_full.cpu().numpy()


if __name__ == "__main__":
    reduced = N_POS < 656
    print("=" * 74)
    if reduced:
        print("*** REDUCED-RESOLUTION RUN: N_POS=%d of 656 positions "
              "(full run exceeds the ~10-min budget on this machine; "
              "rerun later with N_POS=656) ***" % N_POS)
    print("B1c  ENTROPY: WT background vs A222V background, per position")
    print("=" * 74)

    wt = load_sequence(Path(__file__).resolve().parents[1] / "data" / "raw" / "P42898.fasta")
    verify_sequence(wt)
    av = wt[:221] + "V" + wt[222:]
    assert av[221] == "V" and len(av) == 656

    rng = np.random.default_rng(SEED)
    if N_POS >= 656:
        positions = np.arange(1, 657)
    else:
        sample = rng.choice(np.arange(1, 657), size=N_POS - 1, replace=False)
        positions = np.sort(np.concatenate([sample, [222]]))   # force identity-check pos
    print(f"Positions: {len(positions)} (position 222 force-included for the "
          f"identity check), batch={BATCH}, N_BOOT={N_BOOT}")

    device = get_device()
    print(f"Loading ESM-2 650M on {device} ...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    bc = alphabet.get_batch_converter()

    H20_wt = np.empty(len(positions)); H20_av = np.empty(len(positions))
    Hf_wt = np.empty(len(positions)); Hf_av = np.empty(len(positions))
    t0 = time.time()
    for b0 in range(0, len(positions), BATCH):
        chunk = positions[b0:b0 + BATCH]
        h, f = entropy_batch(model, alphabet, bc, [wt] * len(chunk), chunk, device)
        H20_wt[b0:b0 + len(chunk)] = h; Hf_wt[b0:b0 + len(chunk)] = f
        h, f = entropy_batch(model, alphabet, bc, [av] * len(chunk), chunk, device)
        H20_av[b0:b0 + len(chunk)] = h; Hf_av[b0:b0 + len(chunk)] = f
        done = min(b0 + BATCH, len(positions))
        el = time.time() - t0
        print(f"  {done}/{len(positions)} positions ({el:.0f}s elapsed, "
              f"~{el / done * (len(positions) - done):.0f}s remaining)")

    dH = H20_av - H20_wt

    # ---- identity check (AGENTS.md §4): position 222 must have dH == 0 ----
    i222 = int(np.flatnonzero(positions == 222)[0])
    d222 = abs(dH[i222])
    print("\n" + "=" * 74)
    print("IDENTITY CHECK (masking position 222 => identical input in both bgs)")
    print("=" * 74)
    print(f"  |dH| at position 222 = {d222:.3e}")
    if d222 > 1e-6:
        print("  *** SANITY CHECK FAILED -- plumbing is wrong. sys.exit(1) ***")
        sys.exit(1)
    print("  passed.")

    # ---- primary: mean paired dH, position bootstrap --------------------
    print("\n" + "=" * 74)
    print("PRIMARY: paired entropy difference dH = H(A222V bg) - H(WT bg)")
    print("=" * 74)
    obs = float(dH.mean())
    rngb = np.random.default_rng(SEED)
    boot = np.empty(N_BOOT)
    for b in range(N_BOOT):
        boot[b] = dH[rngb.integers(0, len(dH), len(dH))].mean()
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p = float(min(2 * min((boot <= 0).mean(), (boot >= 0).mean()), 1.0))
    print(f"  n positions = {len(positions)}")
    print(f"  mean H_WT  = {H20_wt.mean():.5f} nats   mean H_A222V = {H20_av.mean():.5f} nats")
    print(f"  mean dH    = {obs:+.6f} nats  CI=[{lo:+.6f},{hi:+.6f}]  "
          f"p_boot={'0' if p == 0 else f'{p:.4f}'} (house convention)")
    print(f"  effect size: mean dH / mean H_WT = {obs / H20_wt.mean():+.5f} "
          f"({100 * obs / H20_wt.mean():+.3f}%)")
    print(f"  fraction of positions with dH > 0: {(dH > 0).mean():.4f}")
    print(f"  sd of dH across positions: {dH.std():.6f}")
    verdict = ("GENERIC FLATTENING SUPPORTED (mean dH > 0, CI excludes 0)"
               if (obs > 0 and lo > 0) else
               "flattening NOT supported by this test (CI includes 0 or mean <= 0)")
    print(f"  -> {verdict}")
    full_vocab_note = (Hf_av - Hf_wt).mean()
    print(f"  [secondary] full-vocab mean dH = {full_vocab_note:+.6f} nats")

    out = PROC / "task44_entropy_bg.csv"
    pd.DataFrame({"position": positions, "H20_wt": H20_wt, "H20_a222v": H20_av,
                  "dH20": dH, "Hfull_wt": Hf_wt, "Hfull_a222v": Hf_av}).to_csv(out, index=False)
    print(f"\nSaved per-position table to {out}")
    if reduced:
        print("REDUCED-RESOLUTION RUN (N_POS=%d of 656) — rerun at N_POS=656 "
              "before quoting this externally." % len(positions))
    print("Paired-by-position design; bootstrap unit = position (AGENTS.md §3).")
