"""Shared data-loading functions -- used by both scripts/ and notebooks/."""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parents[2] / "data" / "raw" / "mthfrModel"

CONDITIONS = {
    "WT12": ("WT", 12.5), "WT25": ("WT", 25), "WT100": ("WT", 100), "WT200": ("WT", 200),
    "V12": ("V", 12.5), "V25": ("V", 25), "V100": ("V", 100), "V200": ("V", 200),
}

def load_primary_maps():
    """Load and merge the eight primary maps into one long-format table."""
    frames = []
    for fname, (background, conc) in CONDITIONS.items():
        df = pd.read_csv(RAW / "map_data" / f"{fname}.csv")
        df["background"] = background
        df["folinate_ugml"] = conc
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

def load_derived_maps():
    """Load per-variant derived context metrics (folate_response_model5.csv).

    Key columns -- see config/audit_log.md for the full mapping:
      w.remediation          -> folinate_response      (extrinsic context)
      e.b, e.lod.b, e.post.b -> GI_folinate_independent (intrinsic context)
      e.r, e.lod.r, e.post.r -> GI_folinate_dependent   (both)
    """
    return pd.read_csv(RAW / "results" / "folate_response_model5.csv")

def load_structural_features():
    """Load per-position structural covariates.

    Domain categories are Catalytic / Regulatory / Ser-Rich / (unassigned).
    There is no "Linker" category.
    """
    return pd.read_csv(RAW / "reference_data" / "MTHFR_structural_features.csv")

def load_insilico_predictors():
    """Load PolyPhen-2 / SIFT / PROVEAN predictions, keyed by (pos, ref, alt)."""
    return pd.read_csv(RAW / "reference_data" / "insilico.csv")

def load_pathogenicity_llrs():
    """Load the atlas's own pathogenicity LLR (25ug/mL reference condition)."""
    return pd.read_csv(RAW / "results" / "m25LLRs.csv")
