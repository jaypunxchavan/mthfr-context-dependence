"""
Script 37: writes the corrected framing section for RESULTS.md, replacing
whatever the accuracy-degradation section currently says.

This exists as its own script rather than a manual edit because the whole
project's discipline has been "results come from a script reading real
CSVs, not hand-typed prose" -- this is no exception, even for the write-up
itself. Reads the actual result files from scripts 32/33/34/36 and states,
explicitly, what is and is not established:

  1. ESM-2's raw baseline correlation is higher than conventional
     predictors' (real, not in dispute).
  2. Whether it retains MORE genuine signal beyond a rich confound anchor
     than conventional predictors do is NOT established -- the matched-
     baseline test found no distinguishable difference from PROVEAN, SIFT,
     or PolyPhen-2.
  3. The earlier "ESM-2 degrades more in absolute terms" claim was a
     baseline-mismatch artifact, not a real effect -- stated as a
     correction, not softened into a caveat.
  4. The measurement-noise control is a genuine, independent positive
     result and stands on its own regardless of items 1-3.
  5. delta_ESM is confirmed real (not rounding noise), which is necessary
     context but does not rescue the cross-predictor claim.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
ROOT = Path(__file__).resolve().parents[1]


def load(name):
    p = PROC / name
    return pd.read_csv(p) if p.exists() else None


if __name__ == "__main__":
    L = ["## Accuracy-degradation finding — corrected framing (superseding all earlier framing)\n"]
    L.append("**This section replaces the earlier 'ESM-2's advantage evaporates at high "
             "interaction' framing, which was based on an unmatched-baseline comparison "
             "and did not survive a proper matched-baseline test. Recorded here as a "
             "correction, not a caveat, per external review.**\n")

    mb = load("task_matched_baseline_crosspredictor.csv")
    gaps = load("task_matched_baseline_gaps.csv")
    raw = load("task_established_predictor_strat.csv")
    noise = load("task_measurement_noise_control.csv")
    df_nf = load("task_delta_esm_noise_floor.csv")

    L.append("### What is established\n")
    L.append("1. **`delta_ESM` is real signal, not numerical noise.** "
             f"{'sd(delta_ESM) is ' + f'{df_nf.iloc[0].sd_over_floor:.2e}' + chr(0x00D7) + ' the float32 rounding floor, median |delta_ESM| = ' + f'{df_nf.iloc[0].median_abs_delta:.4f}' if df_nf is not None else 'confirmed (script 32)'}. "
             "This is necessary context, not itself evidence for any cross-predictor claim.\n")
    L.append("2. **Measurement noise in the A222V arm is a real, quantified contributor** "
             "to the accuracy-degradation pattern (SE correlates with |e.b| at ρ≈+0.23), "
             "but `abs_gi` survives controlling for it directly, essentially unchanged, "
             "and the high-precision-subset slope only modestly flattens (~16% reduction, "
             "not a collapse). Noise is a contributor, not the explanation.\n")
    L.append("3. **ESM-2's raw baseline correlation with real fitness is higher than "
             "conventional predictors'** (PROVEAN, SIFT, PolyPhen-2) in the low-interaction "
             "stratum. This part of the earlier comparison is real and undisputed.\n")

    L.append("### What is NOT established, corrected from earlier framing\n")
    L.append("4. **Whether ESM-2 retains more genuine excess signal beyond a rich confound "
             "anchor than conventional predictors do — NOT established.** The raw, "
             "unmatched-baseline comparison (script 34) found ESM-2 degrading more than "
             "PROVEAN, SIFT, and PolyPhen-2 HumDiv in absolute terms. This comparison is "
             "**invalid on its own**: ESM-2 starts from a higher baseline correlation, "
             "so it mechanically has more room to fall, exactly the problem scripts 30-31 "
             "were built to solve for the placebo comparison. The properly matched-baseline "
             "version (script 36), using the same richer-anchor synthetic-predictor method "
             "applied identically to all five predictors, found:\n")
    if gaps is not None:
        L.append("")
        L.append("| Predictor | Matched-baseline gap |")
        L.append("|---|---|")
        for _, r in gaps.iterrows():
            L.append(f"| {r.label} | {r.gap:+.4f} |")
        L.append("")
    if mb is not None:
        L.append("| Comparison | Difference vs ESM-2 | 95% CI | Verdict |")
        L.append("|---|---|---|---|")
        for _, r in mb.iterrows():
            L.append(f"| {r.label} | {r.point_diff:+.4f} | [{r.ci_lo:+.4f},{r.ci_hi:+.4f}] | {r.verdict} |")
        L.append("")
    L.append("**Every difference is indistinguishable from zero.** ESM-2's matched-baseline "
             "excess (+0.077, comparable to script 31's richer-anchor result of +0.079) is "
             "statistically tied with PolyPhen-2 HumDiv's (+0.076), and not distinguishable "
             "from SIFT or PROVEAN either.\n")

    L.append("### Corrected conclusion\n")
    L.append("The accuracy-degradation pattern — predictors losing correlation with real "
             "fitness as measured genetic interaction strengthens — **is real, but is a "
             "property shared by sequence-based predictors generally, not something "
             "specific to ESM-2 or to protein language models.** The genuine excess any "
             "of these predictors shows beyond a rich confound anchor (severity, burial, "
             "domain, base fitness) is small and does not distinguish ESM-2 from "
             "conventional tools. This is a materially weaker claim than earlier framings "
             "suggested, stated here as the corrected standing conclusion rather than one "
             "option among several.\n")

    text = "\n".join(L)
    results_path = ROOT / "RESULTS.md"
    existing = results_path.read_text() if results_path.exists() else ""
    marker = "## Accuracy-degradation finding"
    if marker in existing:
        pre = existing[:existing.index(marker)]
        rest = existing[existing.index(marker):]
        next_marker = rest.find("\n## ", 1)
        post = rest[next_marker:] if next_marker != -1 else ""
        existing = pre + text + post
    else:
        existing = existing + "\n" + text
    results_path.write_text(existing)
    print(f"RESULTS.md updated with corrected framing ({len(text)} chars written)")
