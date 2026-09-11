"""Step 2: Verify the reference sequence. Logic lives in lib/sequence.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lib.sequence import load_sequence, verify_sequence

if __name__ == "__main__":
    fasta_path = Path(__file__).resolve().parents[1] / "data" / "raw" / "P42898.fasta"
    seq = load_sequence(fasta_path)
    verify_sequence(seq)
