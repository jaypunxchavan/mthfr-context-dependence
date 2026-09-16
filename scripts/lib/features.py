"""Substitution-difficulty and structural covariates (proposal 5.6e)."""
import numpy as np
import pandas as pd

# Grantham (1974) per-amino-acid composition, polarity, molecular volume.
# D = rho * sqrt(alpha*dc^2 + beta*dp^2 + gamma*dv^2)  -- constants multiply
# the SQUARED differences. Verified against ten published table values,
# max deviation 0.87 (the published table is integer-rounded).
_GRANTHAM = {
    'A': (0.00, 8.1, 31), 'R': (0.65, 10.5, 124), 'N': (1.33, 11.6, 56),
    'D': (1.38, 13.0, 54), 'C': (2.75, 5.5, 55), 'Q': (0.89, 10.5, 85),
    'E': (0.92, 12.3, 83), 'G': (0.74, 9.0, 3), 'H': (0.58, 10.4, 96),
    'I': (0.00, 5.2, 111), 'L': (0.00, 4.9, 111), 'K': (0.33, 11.3, 119),
    'M': (0.00, 5.7, 105), 'F': (0.00, 5.2, 132), 'P': (0.39, 8.0, 32.5),
    'S': (1.42, 9.2, 32), 'T': (0.71, 8.6, 61), 'W': (0.13, 5.4, 170),
    'Y': (0.20, 6.2, 136), 'V': (0.00, 5.9, 84),
}
_ALPHA, _BETA, _GAMMA, _RHO = 1.833, 0.1018, 0.000399, 50.723


def grantham(a, b):
    if a not in _GRANTHAM or b not in _GRANTHAM:
        return np.nan
    (c1, p1, v1), (c2, p2, v2) = _GRANTHAM[a], _GRANTHAM[b]
    return _RHO * np.sqrt(_ALPHA * (c1 - c2) ** 2 + _BETA * (p1 - p2) ** 2
                          + _GAMMA * (v1 - v2) ** 2)


def blosum62(a, b):
    from Bio.Align import substitution_matrices
    m = substitution_matrices.load("BLOSUM62")
    try:
        return float(m[a, b])
    except (KeyError, IndexError):
        return np.nan


def add_substitution_features(df, wt_col="wt_aa", mut_col="mut_aa"):
    from Bio.Align import substitution_matrices
    m = substitution_matrices.load("BLOSUM62")

    def _bl(r):
        try:
            return float(m[r[wt_col], r[mut_col]])
        except (KeyError, IndexError):
            return np.nan

    out = df.copy()
    out["grantham"] = [grantham(a, b) for a, b in zip(out[wt_col], out[mut_col])]
    out["blosum62"] = out.apply(_bl, axis=1)
    return out


def add_structural_features(df, struct, position_col="position"):
    """Merge relative solvent accessibility and domain by residue position.

    Domain categories are Catalytic / Regulatory / Ser-Rich / unassigned --
    there is no "Linker" category despite the proposal text saying so.
    """
    s = struct.rename(columns={"Position": position_col,
                               "Relative ASA": "rsa", "Domain": "domain"})
    s = s[[position_col, "rsa", "domain"]].copy()
    s["domain"] = s["domain"].fillna("unassigned")
    return df.merge(s, on=position_col, how="left")
