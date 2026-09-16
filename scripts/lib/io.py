"""Shared data-loading functions -- used by both scripts/ and notebooks/."""
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parents[2] / "data" / "raw" / "mthfrModel"

CONDITIONS = {
    "WT12": ("WT", 12.5), "WT25": ("WT", 25), "WT100": ("WT", 100), "WT200": ("WT", 200),
    "V12": ("V", 12.5), "V25": ("V", 25), "V100": ("V", 100), "V200": ("V", 200),
}

# Column names in folate_response_model5.csv for the eight measured conditions.
# w* = WT background, m* = p.Ala222Val ("mutant") background.
CONDITION_COLS = [
    "w12.score", "w25.score", "w100.score", "w200.score",
    "m12.score", "m25.score", "m100.score", "m200.score",
]
WT_COND_COLS = ["w12.score", "w25.score", "w100.score", "w200.score"]
A222V_COND_COLS = ["m12.score", "m25.score", "m100.score", "m200.score"]


def load_primary_maps():
    """Load and merge the eight primary maps into one long-format table."""
    frames = []
    for fname, (background, conc) in CONDITIONS.items():
        df = pd.read_csv(RAW / "map_data" / f"{fname}.csv")
        df["background"] = background
        df["folinate_ugml"] = conc
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_derived_maps(missense_only=True):
    """Load per-variant derived model fits (folate_response_model5.csv).

    Contains BOTH the four derived context measures AND all eight raw
    condition scores (verified identical to map_data/*.csv, diff = 0.0).

    missense_only=True (the default) drops synonymous ('=') and nonsense
    ('Ter') entries. Those are calibration anchors for the atlas's own
    rescaling, not measurements of missense effect, and pooling them into
    downstream analyses has caused real errors twice in this project
    (see audit_log.md). Pass missense_only=False only if you specifically
    need the controls.

    Key columns:
      w.fitness      -> base functionality (WT background, low folinate)
      w.remediation  -> folinate response      (environment-dependent context)
      e.b            -> folinate-independent GI (sequence-encoded context)
      e.r            -> folinate-dependent GI   (both)
      start          -> amino acid position
    """
    df = pd.read_csv(RAW / "results" / "folate_response_model5.csv")
    if missense_only:
        df = df[df["type"] == "substitution"].copy()
    return df


def load_structural_features():
    """Per-position structural covariates.

    Domain categories: Catalytic / Regulatory / Ser-Rich / (unassigned).
    There is no "Linker" category.
    """
    return pd.read_csv(RAW / "reference_data" / "MTHFR_structural_features.csv")


def load_insilico_predictors():
    """PolyPhen-2 / SIFT / PROVEAN predictions, keyed by (pos, ref, alt)."""
    return pd.read_csv(RAW / "reference_data" / "insilico.csv")


def load_pathogenicity_llrs():
    """The atlas's own pathogenicity LLR (25ug/mL reference condition)."""
    return pd.read_csv(RAW / "results" / "m25LLRs.csv")
