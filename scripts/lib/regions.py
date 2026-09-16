"""
Mutagenesis region boundaries for MTHFR.

Source: personal communication, Nishka Kishore (2nd author, Weile et al.
2021) via Fritz Roth, in response to an emailed query, Sept 2026, forwarding
the actual primer design file (MTHFR_regionalPOPcode_regions.xlsx) from Song
Sun. Not published in the paper, the GitHub repository, or any released
data file -- the prior Tier 2 pass disclosed this as unobtainable.

Cross-validated three ways before use:
  1. Union of the four ranges exactly equals the atlas's position set
     (2-656; position 1, the Met start codon, is absent from both).
  2. Tile counts per region (4,4,5,6) match the paper's stated tile counts
     for R1-R4 exactly.
  3. Residues/tile is 30-37 across all four regions -- a tight, plausible
     band for ~130nt tiles with codon-level mutagenesis.

Primer-level tile boundaries (finer than needed here, kept for provenance):
  R1: 2-36, 37-72, 73-110, 111-147
  R2: 148-182, 183-219, 220-256, 257-294
  R3: 295-332, 333-367, 368-402, 403-439, 440-474
  R4: 475-510, 511-547, 548-583, 584-620, 621-654, 655-656
"""
REGION_BOUNDS = {1: (2, 147), 2: (148, 294), 3: (295, 474), 4: (475, 656)}


def assign_region(position):
    """Vectorized: position (array-like) -> region number (1-4), NaN if out
    of range (only position 1, never mutagenized, should map to NaN)."""
    import numpy as np
    pos = np.asarray(position, dtype=float)
    region = np.full(pos.shape, np.nan)
    for r, (lo, hi) in REGION_BOUNDS.items():
        region[(pos >= lo) & (pos <= hi)] = r
    return region
