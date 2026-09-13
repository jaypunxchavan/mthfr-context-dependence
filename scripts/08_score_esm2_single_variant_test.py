"""
Step 8: Single-variant ESM-2 test.

Score p.Ala222Val end to end with masked-marginal scoring before scaling
to ~12,000 variants. Position 222 is a good first check because the
answer is checkable by hand: A222V is a documented hypomorphic (damaging)
variant, so wild-type Ala should score substantially more likely than
Val at that position. If the sign comes out backwards, something in the
masking or indexing is wrong -- stop and debug before scoring anything else.
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
import esm
from scripts.lib.sequence import load_sequence

WT_POS = 222   # 1-indexed
WT_AA = "A"
MUT_AA = "V"


def masked_marginal_score(model, alphabet, batch_converter, sequence, position_1idx, wt_aa, mut_aa, device):
    idx0 = position_1idx - 1
    assert sequence[idx0] == wt_aa, f"Expected {wt_aa} at position {position_1idx}, found {sequence[idx0]}"

    masked_seq = sequence[:idx0] + "<mask>" + sequence[idx0 + 1:]
    _, _, tokens = batch_converter([("query", masked_seq)])
    tokens = tokens.to(device)

    with torch.no_grad():
        out = model(tokens, repr_layers=[], return_contacts=False)
        logits = out["logits"]

    token_pos = idx0 + 1  # +1 for the BOS token batch_converter prepends
    log_probs = torch.log_softmax(logits[0, token_pos], dim=-1)

    wt_tok = alphabet.get_idx(wt_aa)
    mut_tok = alphabet.get_idx(mut_aa)
    return (log_probs[mut_tok] - log_probs[wt_tok]).item()


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
    print(f"Loaded sequence, length {len(seq)}")

    print("Loading ESM-2 650M (downloads ~2.5GB on first run -- may take a while)...")
    t0 = time.time()
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    model.eval()
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()
    print(f"Model ready in {time.time() - t0:.1f}s")

    print("\nScoring p.Ala222Val (masked-marginal)...")
    t0 = time.time()
    score = masked_marginal_score(model, alphabet, batch_converter, seq, WT_POS, WT_AA, MUT_AA, device)
    elapsed = time.time() - t0

    print(f"Score (log P(Val) - log P(Ala)) at position 222: {score:.4f}")
    print(f"Time for this single scoring pass: {elapsed:.2f}s")
    print()
    if score < 0:
        print("Sign check PASSED: negative, as expected -- Val predicted less likely")
        print("than Ala at this position, consistent with A222V being hypomorphic.")
    else:
        print("Sign check FAILED: positive -- Val predicted MORE likely than Ala.")
        print("Do not proceed to scaling. Check masking/indexing logic first.")
