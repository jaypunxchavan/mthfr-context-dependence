"""
Step 11: Score every position with ESM-2, A222V background.

Same logic as WT scoring (script 10), applied to the sequence with
A222V already substituted in. This is what Phase 5's Model C needs --
the model scoring each position with the genetic background actually
present in the input sequence, not just wild-type.
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
    wt_seq = load_sequence(fasta_path)

    assert wt_seq[221] == "A", f"Expected Ala at 222, found {wt_seq[221]}"
    a222v_seq = wt_seq[:221] + "V" + wt_seq[222:]
    print(f"A222V sequence built: position 222 is now {a222v_seq[221]}")
    print(f"Length unchanged: {len(a222v_seq)} (should be 656)")

    maps = load_primary_maps()
    atlas_variants = set(maps["hgvs_pro"].unique())
    atlas_missense = {v for v in atlas_variants if "=" not in str(v) and "Ter" not in str(v)}

    positions = sorted({
        int(m.group(1))
        for h in atlas_variants
        for m in [re.match(r"p\.[A-Za-z]{3}(\d+)", str(h))] if m
    })
    # Position 222 itself is now WT in this background (Val, not Ala) --
    # score it too, so downstream code can look up "what does A222V
    # background score at its own position" if needed, but the atlas
    # naming for that position refers to the WT-background substitution.
    print(f"Scoring {len(positions)} positions in A222V background...")

    print("Loading ESM-2 650M...")
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    rows = []
    t_start = time.time()
    for i, pos in enumerate(positions):
        wt_aa_in_this_background = a222v_seq[pos - 1]
        scores = get_position_logprobs(model, alphabet, batch_converter, a222v_seq, pos, device)
        for mut_aa, score in scores.items():
            rows.append({
                "position": pos,
                "background_aa_at_this_pos": wt_aa_in_this_background,
                "mut_aa": mut_aa,
                # Name relative to the ORIGINAL wt_seq residue at this position,
                # so it matches atlas hgvs_pro naming (which is always relative
                # to true WT, even in the A222V-background maps).
                "hgvs_pro": hgvs_pro(wt_seq[pos - 1], pos, mut_aa) if pos != 222 else None,
                "esm2_score_a222v_bg": score,
            })
        if (i + 1) % 100 == 0 or (i + 1) == len(positions):
            elapsed = time.time() - t_start
            remaining = (len(positions) - (i + 1)) * elapsed / (i + 1)
            print(f"  {i+1}/{len(positions)} positions "
                  f"({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining)")

    scored = pd.DataFrame(rows)
    print(f"\nTotal scored rows: {len(scored)}")
    out_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "esm2_a222v_bg_scores.csv"
    scored.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")
