"""
Script 40: final corrected framing incorporating the exogenous-anchor test
(38) and the range-restriction correction (39).

Rewrites the accuracy-degradation section of RESULTS.md again, superseding
script 37's framing. This is not a contradiction of 37 -- 37 correctly
established that ESM-2 is indistinguishable from conventional predictors.
This script goes one step further and asks whether ANY of them show a
real excess once the one WT-arm-derived ingredient (w.fitness) is removed
from the confound anchor entirely. It does not.
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
    L = ["## Accuracy-degradation finding — final corrected framing "
         "(supersedes script 37's framing)\n"]
    L.append("**Adds the exogenous-anchor test and the range-restriction correction. "
             "This is the deepest test of the circularity concern raised across three "
             "rounds of external review, and it resolves the question.**\n")

    rr = load("task_range_restriction_summary.csv")
    ex = load("task_exogenous_anchor_test.csv")

    L.append("### Range restriction — ruled out\n")
    L.append("Stratifying by |e.b| restricts the target's variance within each stratum, "
             "which could mechanically produce a Spearman-correlation decline independent "
             "of anything about circularity. Formal Thorndike-style correction (an "
             "approximation when applied to Spearman rather than Pearson correlations, "
             "stated explicitly) found SD ratios close to 1.0 across strata (1.02, 1.13, "
             "0.97), and correction made the apparent degradation slightly *larger*, not "
             "smaller, for every predictor tested. Range restriction is not the "
             "explanation.\n")
    if rr is not None:
        L.append("| Predictor | Raw drop | Corrected drop |")
        L.append("|---|---|---|")
        for _, r in rr.iterrows():
            L.append(f"| {r.label} | {r.raw_drop:+.4f} | {r.corrected_drop:+.4f} |")
        L.append("")

    L.append("### The exogenous-anchor test — the decisive result\n")
    L.append("Every confound control before this point (placebos, matched-strength "
             "synthetic, richer anchor, cross-predictor matched baseline) included "
             "`w.fitness` as an anchor ingredient — itself derived from this assay's "
             "wild-type arm. Rebuilding the anchor from Grantham, BLOSUM62, RSA, and "
             "domain **with `w.fitness` removed entirely**, and rerunning the matched-"
             "strength gap for ESM-2 and four conventional predictors:\n")
    if ex is not None:
        L.append("| Predictor | Gap WITH w.fitness | Gap WITHOUT w.fitness |")
        L.append("|---|---|---|")
        for _, r in ex.iterrows():
            w = f"{r.gap_with_wf_mean:+.4f} [{r.gap_with_wf_lo:+.4f},{r.gap_with_wf_hi:+.4f}]"
            n = f"{r.gap_no_wf_mean:+.4f} [{r.gap_no_wf_lo:+.4f},{r.gap_no_wf_hi:+.4f}]"
            L.append(f"| {r.label} | {w} | {n} |")
        L.append("")
    L.append("**No predictor's excess survives without `w.fitness` in the anchor.** "
             "Every one of five CIs crosses zero, several with negative means. The "
             "'genuine excess beyond confounds' result reported in scripts 30/31/36 was "
             "entirely dependent on including a WT-arm-derived quantity in the confound "
             "anchor — which is exactly the deepest form of circularity raised across "
             "three review rounds.\n")

    L.append("### Corrected conclusion, final\n")
    L.append("The accuracy-degradation pattern is real as a description of the data: "
             "predictors lose correlation with true fitness as measured genetic "
             "interaction strengthens. But every attempt to establish that ESM-2 (or any "
             "sequence-based predictor) retains information beyond this assay's own "
             "wild-type-arm measurements has failed once tested rigorously. **The most "
             "defensible standing conclusion for this project is the negative "
             "methodological one**: `e.r` is almost entirely a mathematical artifact of "
             "how the interaction statistic is constructed (confirmed, script 20/21's "
             "sign-flip null), `e.b` is real but heavily artifact-laden (77-82% per the "
             "sign-flip null), and the accuracy-degradation pattern built on top of these "
             "measures does not support a claim about ESM-2 or protein language models "
             "specifically — it reduces to a property of how well any WT-arm-informed "
             "signal predicts an A222V-arm-derived target, which is close to tautological "
             "once seen clearly. The project's real, defensible contribution is the "
             "re-derivation and confound-control framework itself, and what it revealed "
             "about the limits of interaction-residual stratification as an analysis "
             "method for this kind of atlas.\n")

    text = "\n".join(L)
    results_path = ROOT / "RESULTS.md"
    existing = results_path.read_text() if results_path.exists() else ""
    marker = "## Accuracy-degradation finding"
    idx = existing.find(marker)
    if idx != -1:
        pre = existing[:idx]
        rest = existing[idx:]
        next_idx = rest.find("\n## ", 1)
        post = rest[next_idx:] if next_idx != -1 else ""
        existing = pre + text + post
    else:
        existing = existing + "\n" + text
    results_path.write_text(existing)
    print(f"RESULTS.md updated with final corrected framing ({len(text)} chars)")
