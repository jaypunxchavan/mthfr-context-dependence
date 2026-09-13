"""
Step 10 (Week 2 start): Score every atlas position with ESM-2, WT background.

One forward pass per position (not per variant) -- ~655 passes covering
all 19 substitutions each, matching the efficiency the proposal assumes
in section 5.1. Caches the full table to data/processed/esm2_wt_scores.csv
so this never needs to run twice.
"""
import sys
import time
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import esm
import pandas as pd

from scripts.lib.sequence import load_sequence
from scripts.lib.io import load_primary_maps
from scripts.lib.esm_scoring import get_position_logprobs, hgvs_pro, get_device

if __name__ == "__main__":
    device = get_device()
    print(f"Using device: {device}")

    fasta_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "P42898.fasta"
    seq = load_sequence(fasta_path)

    maps = load_primary_maps()
    atlas_variants = set(maps["hgvs_pro"].unique())

    positions = sorted({
        int(m.group(1))
        for h in atlas_variants
        for m in [re.match(r"p\.[A-Za-z]{3}(\d+)", str(h))] if m
    })
    print(f"Scoring {len(positions)} positions...")

    print("Loading ESM-2 650M...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    rows = []
    t_start = time.time()
    for i, pos in enumerate(positions):
        wt_aa = seq[pos - 1]
        scores = get_position_logprobs(model, alphabet, batch_converter, seq, pos, device)
        for mut_aa, score in scores.items():
            rows.append({
                "position": pos,
                "wt_aa": wt_aa,
                "mut_aa": mut_aa,
                "hgvs_pro": hgvs_pro(wt_aa, pos, mut_aa),
                "esm2_score": score,
            })
        if (i + 1) % 100 == 0 or (i + 1) == len(positions):
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed
            remaining = (len(positions) - (i + 1)) / rate
            print(f"  {i+1}/{len(positions)} positions "
                  f"({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining)")

    scored = pd.DataFrame(rows)
    print(f"\nTotal scored variants: {len(scored)}")

    matched = scored["hgvs_pro"].isin(atlas_variants).sum()
    print(f"Matched to atlas hgvs_pro naming: {matched} / {len(scored)} "
          f"({100*matched/len(scored):.1f}%)")
    if matched / len(scored) < 0.95:
        print("WARNING: match rate below 95% -- check hgvs_pro string format "
              "against the atlas's actual naming before trusting this table.")

    out_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "esm2_wt_scores.csv"
    scored.to_csv(out_path, index=False)
    print(f"\nSaved to {out_path}")