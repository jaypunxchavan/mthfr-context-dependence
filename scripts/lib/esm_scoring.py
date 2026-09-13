"""ESM-2 masked-marginal scoring -- the core reusable scoring function."""
import torch
from scripts.lib.validate import AA3TO1

AA1TO3 = {v: k for k, v in AA3TO1.items()}
AA_LIST = list("ACDEFGHIKLMNPQRSTVWY")


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_position_logprobs(model, alphabet, batch_converter, sequence, position_1idx, device):
    """One forward pass at position_1idx. Returns dict of {amino_acid: score}
    for all 19 non-wildtype substitutions (masked-marginal log-odds vs WT)."""
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


def hgvs_pro(wt_aa_1letter, position, mut_aa_1letter):
    """e.g. ('A', 113, 'R') -> 'p.Ala113Arg' -- matches the atlas's own format."""
    return f"p.{AA1TO3[wt_aa_1letter]}{position}{AA1TO3[mut_aa_1letter]}"
