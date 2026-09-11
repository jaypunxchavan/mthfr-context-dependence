"""Reference sequence fetching and verification.

Fetch P42898-1 directly from UniProt (rest.uniprot.org/uniprotkb/P42898.fasta)
or NCBI RefSeq NM_005957.5 -- NOT from a PDB structure page, which can carry
construct-specific substitutions.
"""
from Bio import SeqIO

def load_sequence(fasta_path):
    record = next(SeqIO.parse(fasta_path, "fasta"))
    return str(record.seq)

def verify_sequence(seq):
    """Checks: length 656, residue 222 == Ala. Raises AssertionError on failure.

    An off-by-one here silently produces a plausible-looking wrong result
    downstream -- do not skip this.
    """
    assert len(seq) == 656, f"Expected length 656, got {len(seq)}"
    assert seq[221] == "A", f"Expected Ala at position 222, got {seq[221]}"
    print("Length check passed: 656")
    print("Position 222 check passed: Ala")
    return True
