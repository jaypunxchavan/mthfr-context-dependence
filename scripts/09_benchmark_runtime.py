
"""
Step 9: Runtime benchmark + efficient scoring function.

Refactors masked-marginal scoring so ONE forward pass at a masked position
returns log-probabilities for all 20 amino acids at once -- one pass per
POSITION, not one pass per VARIANT. Benchmarks a random sample of the
positions actually present in the atlas, extrapolates total runtime.
"""
import sys
import time
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
import esm
from scripts.lib.sequence import load_sequence
from scripts.lib.io import load_primary_maps

AA_LIST = list("ACDEFGHIKLMNPQRSTVWY")


def get_position_logprobs(model, alphabet, batch_converter, sequence, position_1idx, device):
    """One forward pass at position_1idx. Returns dict of {amino_acid: score}
    for all 19 non-wildtype substitutions, relative to wildtype log-prob."""
    idx0 = position_1idx - 1
    wt_aa = sequence[idx0]

    masked_seq = sequence[:idx0] + "<mask>" + sequence[idx0 + 1:]
    _, _, tokens = batch_converter([("query", masked_seq)])
    tokens = tokens.to(device)

    with torch.no_grad():
        out = model(tokens, repr_layers=[], return_contacts=False)
        logits = out["logits"]

    token_pos = idx0 + 1
    log_probs = torch.log_softmax(logits[0, token_pos], dim=-1)
    wt_score = log_probs[alphabet.get_idx(wt_aa)].item()

    return {
        aa: log_probs[alphabet.get_idx(aa)].item() - wt_score
        for aa in AA_LIST if aa != wt_aa
    }


if __name__ == "__main__":
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    fasta_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "P42898.fasta"
    seq = load_sequence(fasta_path)

    # Real positions needing scoring, pulled from the actual atlas data
    maps = load_primary_maps()
    import re
    positions = set()
    for h in maps["hgvs_pro"].unique():
        m = re.match(r"p\.[A-Za-z]{3}(\d+)", str(h))
        if m:
            positions.add(int(m.group(1)))
    positions = sorted(positions)
    print(f"Distinct positions in atlas data: {len(positions)} "
          f"(range {positions[0]}-{positions[-1]})")

    print("\nLoading ESM-2 650M...")
    t0 = time.time()
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()
    print(f"Model ready in {time.time() - t0:.1f}s")

    n_sample = 30
    sample_positions = random.sample(positions, min(n_sample, len(positions)))

    print(f"\nBenchmarking {len(sample_positions)} random positions...")
    times = []
    for pos in sample_positions:
        t0 = time.time()
        _ = get_position_logprobs(model, alphabet, batch_converter, seq, pos, device)
        times.append(time.time() - t0)

    avg = sum(times) / len(times)
    total_est = avg * len(positions)

    print(f"\nMean time per position: {avg:.3f}s (min {min(times):.3f}s, max {max(times):.3f}s)")
    print(f"Estimated total time for all {len(positions)} positions: "
          f"{total_est:.0f}s ({total_est/60:.1f} min)")
    print()
    if total_est < 3600:
        print(f"Under an hour on {device} -- CPU/MPS overnight concern from the")
        print("proposal doesn't apply here. Fine to just run the full scoring now.")
    else:
        print(f"Over an hour -- consider batching multiple positions per forward")
        print("pass, or running unattended overnight.")
