# MTHFR Context-Dependence Project — Full Results Log

Purpose of this document: every result the project has produced, in the
order they were found, stated plainly as FOR the hypothesis, AGAINST it, or
NEUTRAL/METHODOLOGICAL. Written to be pasted into a new chat to generate
follow-up questions and next steps — not a polished write-up.

**The hypothesis under test:** does ESM-2 (a protein language model) fail to
predict fitness specifically for variants whose effect depends on genetic
background (real epistasis with the A222V background mutation), as measured
by the MTHFR deep mutational scanning atlas (Weile et al. 2021)?

**One-sentence status as of the last completed script:** the project has NOT
found evidence that ESM-2 uses background information well. It has found
increasingly clean evidence in the OPPOSITE direction — ESM-2 gets slightly
but reliably WORSE when given real background information, specifically
where real interaction is strongest — but one major metric disagreement
(rank vs. absolute error) is still unresolved and blocks a clean final
statement.

---

## Part 1 — Foundational results (Week 1, before any null-testing)

### 1.1 The original "flagship" finding — SUPERSEDED, do not cite as-is
Splitting variants into three interaction-strength buckets (low/mid/high,
by `|e.b|` tercile) gave ESM-2 correlations of **0.53 / 0.35 / 0.17** against
real A222V-background fitness. This was treated as the headline result for
weeks. **It has since been shown to rest on a stratifier that is itself
mostly measurement artifact (see 2.1) and a comparison (Model B vs Model C)
that was mathematically incapable of detecting what it claimed to detect
(see 1.2).** Do not present this number without both caveats attached.

### 1.2 Model B is rank-degenerate with Model A — METHODOLOGICAL, against naive framing
Model B (ESM-2 WT score + constant for "having seen" A222V) is mathematically
identical in rank order to Model A (ESM-2 WT score alone), because adding a
constant cannot change rank order. This was caught, not missed — but it means
the original "B vs C" comparison the whole Phase 5 framing was built on could
never have shown anything under rank correlation. This forced everything
downstream onto either (a) a different comparison entirely, or (b) a
scale-sensitive metric (MAE) instead of rank. Both paths were eventually
taken (see Part 4).

### 1.3 Three context classes tested, one survived preliminary screening
- `folinate_response` (environment-dependent context) — **DROPPED**, does not
  survive multivariable controls (fitness, Grantham, BLOSUM62, RSA, domain).
- `GI_folinate_dependent` (e.r) — **DROPPED**, fails its own re-derivation
  null outright (see 2.2). This is the cleanest kill in the project.
- `GI_folinate_independent` (e.b) — the one result that nominally survived
  Task 1's null, but see 2.1 for how much of it was real.

---

## Part 2 — Null-testing the original e.b/e.r results (Task 1)

### 2.1 Sign-flip re-derivation null for e.b — AGAINST, but not a total kill
| Error metric | Observed rho | Null mean | Excess over null | % of raw value that is artifact |
|---|---|---|---|---|
| rank-based | +0.1199 | +0.0977 | +0.0222 | 81% |
| calibrated | -0.1297 | -0.1015 | -0.0282 | 78% |

The null does NOT centre on zero. Most of the raw correlation is structural
artifact of how the interaction statistic itself is built (it is, by
construction, a residual relative to the wild-type arm — see 4.1 for why
that structure is unavoidable). The association technically survives (p <
0.05) but the real effect is roughly a fifth of the headline number.

### 2.2 Sign-flip re-derivation null for e.r — AGAINST, clean kill
e.r (folinate-DEPENDENT interaction) fails its re-derivation null outright.
This context class is dropped entirely and should be treated as a clean,
reportable negative result in its own right — it is the least ambiguous
finding in the whole project, in either direction.

### 2.3 Synonymous-variant empirical zero — METHODOLOGICAL, validates the approach
Synonymous variants (identical protein sequence, cannot have real epistasis)
give e.b spread that serves as a noise floor: mean +0.0217, sd 0.145. Real
missense e.b spread (sd 0.241) is meaningfully larger, which is reassuring —
there IS a real signal above pure noise somewhere in e.b, even if 2.1 shows
most of any single correlation built from it is artifact.

---

## Part 3 — Robustness checks on the surviving e.b result

### 3.1 Multivariable controls — MIXED
Controlling for base fitness, Grantham distance, BLOSUM62, RSA, and domain
with cluster-robust SEs by position: `GI_folinate_independent` survives in
both error metrics (rank: +0.0521, calibrated: -0.0590, both CIs exclude
zero). `folinate_response` does not survive in either. This is consistent
with 1.3/2.1 — e.b has *something* real in it, just much less than its raw
correlation implies.

### 3.2 Region-stratified check — AGAINST uniformity, informative
Using region boundaries obtained directly from the atlas's co-authors:
region 4 (475-656, most of the regulatory domain) does **not** overlap the
pooled estimate in either error metric, and crosses zero entirely in the
rank-based one. The e.b result is not uniformly distributed across the
protein. Later shown (Part 7) to plausibly reflect a real two-latent-trait
structure rather than noise.

### 3.3 Precision filtering — MIXED
5 of 18 subset tests (restricting to high-confidence variants by measurement
precision) have a CI crossing zero. Some but not all of the association
survives when noisy variants are excluded.

---

## Part 4 — The accuracy-degradation finding, full gauntlet (initially: "the strongest result in the project")

### 4.1 Why this needed the same scrutiny as everything else — METHODOLOGICAL, important
`e.b` is, by construction, the residual of the A222V arm from an expectation
built entirely out of the WT arm. ANY WT-informed predictor (ESM-2 included)
will mechanically appear to degrade across `|e.b|` strata — not because it
fails at epistasis, but because high `|e.b|` selects variants whose target
deviates from what the WT arm implies. This is the single most important
structural fact discovered in the project and it undermines almost every
naive stratified comparison run before it was identified.

### 4.2 First pass through the full gauntlet — appeared to survive, was later reframed
At the time, this looked like the strongest result in the project:
multivariable controls made the effect LARGER not smaller (unlike every
other claim), both error metrics agreed in sign, and the sign-flip null
excess was proportionally larger than e.b's. **This framing is now
superseded by Part 6 below — the "strongest result" label no longer applies
in its original positive sense.**

### 4.3 Region 2 sign reversal — RESOLVED as a calibration artifact, in favor of the finding
Region 2 reversed sign under the calibrated metric only. Traced to pooled
calibration mixing fitness ranges across structurally different regions
(region 2 is 100% catalytic domain, lowest mean fitness of any region).
Fitting calibration separately within each region removed the reversal, and
strengthened the pooled correlation (+0.090 → +0.191). This was a genuine
methodological fix, disclosed as chosen after seeing which region reversed
(a post-hoc fix, stated as such, not hidden).

### 4.4 Placebo-predictor control (script 29) — AGAINST the "ESM-2-specific" framing, then partially FOR
Testing whether pure measurement placebos (no model at all — the WT-arm's
own measured mean, and the atlas's own `w.fitness`) degrade the same amount
across `|e.b|` strata as ESM-2 does. If they degrade identically, the
"finding" belongs to how `|e.b|` is constructed, not to ESM-2.
**Result: ESM-2 degraded LESS than the placebos** (real excess, not purely
mechanical) — but this comparison used unmatched starting strengths, so it
could not distinguish "ESM-2 is genuinely more robust" from "ESM-2 is just
a weaker overall predictor of w.fitness, so it has less confound to lose."
Script 30 was built specifically to separate these two explanations.

### 4.5 Matched-confound curve (script 30) — Historically FOR the finding; now in direct tension with Part 6
Built a synthetic predictor matched to ESM-2's LOW-stratum correlation
strength (same starting power, zero real information, built purely from
`w.fitness`). Compared HIGH-stratum performance: **ESM-2 retained MORE
signal than the matched-strength synthetic** — a real, reportable excess on
a RANK-based metric. At the time this was read as evidence the original
epistasis-blindness claim was wrong and ESM-2 had real signal.
**This is the result that Part 6's MAE-based finding now directly
contradicts. Both are real computations; they disagree because they use
different metrics (rank vs. absolute error) on similar but not identical
questions. UNRESOLVED — see "What's next," item 1.**

---

## Part 5 — Promoting delta_ESM to the primary endpoint (structurally cleaner test)

### 5.1 Why this replaced the e.b-based endpoint — METHODOLOGICAL, in favor of rigor
Every prior test regressed an ESM-2 ERROR against a DMS-derived RESIDUAL
(e.b), an outcome shown in 4.1 to be structurally biased toward finding a
relationship. `delta_ESM = S(v | A222V background) − S(v | WT background)`
is ESM-2's OWN predicted interaction, with no error metric, no calibration,
and no w.fitness anywhere in either variable — interaction-vs-interaction,
the same comparison Visani/Verma/DeWitt (2026) use as their diagnostic for
"does this model represent epistasis at all."

### 5.2 Primary correlation, real data — the sign FLIPPED from the synthetic test run, and this is real
On real data: **signed delta_ESM vs signed e.b: ρ = -0.088** (published e.b)
and -0.088 (own e.b), both p < 0.0001. Also tested: absolute version
(ρ = -0.105 to -0.122), and delta_ESM vs e.r (ρ = -0.035, weak but
significant). **The negative sign is the real finding** — ESM-2's implied
interaction moves opposite to the measured interaction, not merely "fails to
detect" it.

### 5.3 Sign-flip null on delta_ESM — the cleanest result in the entire project, AGAINST ESM-2's usefulness but methodologically the strongest evidence yet
| Version | Observed | Null mean | Excess | % artifact |
|---|---|---|---|---|
| signed | -0.0881 | +0.0001 | -0.0882 | **~0%** |
| absolute | -0.1049 | -0.0852 | -0.0198 | 81% |

The signed null centres almost exactly on zero (as it should, mechanically,
since both delta_ESM and e.b are signed) — this is a calibration check on
the test itself, and it passes. **The signed result survives at essentially
0% structural artifact**, the cleanest number the project has produced,
versus 77-82% artifact fractions everywhere else. This is strong evidence
the -0.088 correlation is real, not a construction artifact.

### 5.4 Position-222 proximity confound — AGAINST clean interpretation, real caveat
`|delta_ESM|` vs distance from position 222: ρ = **-0.298** (strong). The
primary correlation flips depending on locality: within 25 residues of 222,
ρ = +0.067 (CI crosses zero, underpowered, n=844); beyond 25 residues,
ρ = -0.075. A meaningful part of the pooled effect may be driven by residues
far from the mutation site, and near the site there may be no reliable
signal at all — just a transformer's local-attention sensitivity to a
nearby literal residue swap rather than anything resembling real epistasis
detection.

### 5.5 Region check on delta_ESM's excess — AGAINST uniformity
Only regions 1 and 3 have sign-flip excess that survives its own null
(p<0.001, p=0.006). Region 2 (p=0.156) and region 4 (p=0.768) do not. The
finding is real and clean where it holds, but holds in roughly half the
protein.

---

## Part 6 — The additive null in phenotype space (script 34) — the most consequential single result, AGAINST the original hypothesis

### 6.1 Why this had never been built before — METHODOLOGICAL gap, now closed
No true no-interaction baseline existed anywhere in the project until this
script. It was structurally blocked: with only ONE fixed alternate
background (A222V), EVERY no-interaction model (additive or multiplicative)
is mathematically rank-degenerate with the raw WT-background score — proven
numerically to 10 decimal places (`rho(pred_mult, target) ==
rho(pred_add, target) == rho(w_hat, target)`, exactly). Rank correlation is
structurally blind to the null. The fix: evaluate on MAE instead.

### 6.2 Headline MAE result — AGAINST the hypothesis, clean and directionally consistent with 5.2/5.3
| Comparison | MAE diff | CI | Verdict |
|---|---|---|---|
| ESM-2(A222V bg) vs multiplicative null | -0.00031 | [-0.00102, +0.00043] | indistinguishable |
| ESM-2(A222V bg) vs additive null | -0.00871 | [-0.01386, -0.00361] | ESM-2 better (weak null, expected) |
| **ESM-2(A222V bg) vs ESM-2(WT bg)** | **+0.00053** | **[+0.00029, +0.00077]** | **ESM-2 WORSE with real background info** |

Giving the model the true mutated sequence instead of just wild-type makes
it *reliably* worse, across all 11,113 variants (CI excludes zero). Small
in absolute terms (~0.2% of baseline MAE ~0.22) but statistically clean.

### 6.3 Stratified by interaction strength — the direct test of the ORIGINAL hypothesis, and it fails
| Stratum | MAE(null) | MAE(ESM-2) | diff | Verdict |
|---|---|---|---|---|
| low | 0.2153 | 0.2121 | -0.00317 | ESM-2 better (CI excludes 0) |
| mid | 0.1930 | 0.1928 | -0.00011 | crosses zero |
| **high** | **0.2481** | **0.2505** | **+0.00241** | **ESM-2 WORSE (CI excludes 0), n=3586** |

This is the direct test of the prediction that founded Phase 5 back in Week
1: "C gains over B specifically among variants with strong measured genetic
interaction." The opposite happened. Where real interaction is strongest,
ESM-2 is *reliably worse* than assuming no interaction exists at all.

### 6.4 The asymmetry in this test favors ESM-2, and it still lost — strengthens 6.2/6.3
The ESM-2 predictors were calibrated directly against the true target; the
null predictors were calibrated against a *different* target (WT fitness)
and then algebraically transformed. That favors ESM-2 by construction. It
still lost in the high stratum. If it had won narrowly, that would be weak
evidence (margin could be the calibration asymmetry). Losing anyway is not
weakened by this — if anything it's a more conservative bar that ESM-2
still failed to clear.

---

## Part 7 — Two-latent-trait diagnostic (script 36) — NEUTRAL/methodological, motivates further work

### 7.1 Motivation — from Carlson, Andrews & Simons (PNAS 2025)
Fitting a single-latent-trait global-epistasis model to a system that
actually has two latent traits (e.g., MTHFR's catalytic domain and
regulatory/AdoMet-binding domain) produces SPURIOUS specific epistasis that
tracks the omitted trait. This is a candidate mechanism for two of the
project's longest-standing open puzzles: the region-4 anomaly (3.2) and the
own_e_b/published-e_b mid-range disagreement (never previously explained).

### 7.2 Result — the decision rule fired, in favor of doing the refit
A decision rule was fixed BEFORE running the script: domain/region means
that exclude zero justify a two-trait refit (MoCHI, bidimensional global
epistasis); if everything centres on zero, drop the hypothesis. **Result:**
domain means exclude zero for Catalytic, Ser-Rich, and unassigned; **region
means exclude zero for all four regions.** The disagreement-vs-mid-range
correlation is ρ=+0.278 (excludes zero), and disagreement is lowest in the
Catalytic domain (0.027) and ~50% higher elsewhere (0.038-0.042) — consistent
with a single global correction curve fit mostly on catalytic-heavy data
misfitting elsewhere. **The gate for the two-trait refit is cleared. The
refit itself has not yet been run.**

### 7.3 Power caveat, stated up front
Only one alternate background (A222V) exists, versus Carlson's method
assuming averaging over many. A null result here would have been weak
evidence of absence; the fact it came back positive anyway (7.2) is more
meaningful than a positive result would be in a well-powered design, but a
future null in the actual MoCHI refit should not be over-read either, given
Carlson's own finding that both their method and MoCHI are underpowered for
negative epistasis among deleterious mutations — which describes most of
MTHFR's variant set.

---

## Part 8 — A currently BROKEN tool: the SE-based epistatic-set threshold (script 35)

### 8.1 What it was meant to do
Replace the arbitrary tercile split (`pd.qcut` into low/mid/high) with a
principled threshold: call a variant "epistatic" only when `|e.b|` exceeds N
times its own analytically-derived standard error (Kolchina et al. 2026's
criterion). SE(e.b) is closed-form here (WLS intercept variance), not
bootstrapped, so this required no new assumption beyond what the atlas's own
model already makes.

### 8.2 Result — the tool does not work as shipped, AGAINST using it downstream
Calibration check: empirical synonymous-variant sd (0.145) vs. median
analytic SE (0.039) → ratio **3.76**. The reported per-condition
measurement-error values are underdispersed by roughly 4x relative to what
the data's own noise floor says.

**Consequence:** at N=2, the missense pass rate (44.8%) and the synonymous
pass rate (44.7%) are statistically indistinguishable. A threshold meant to
flag real interaction is flagging synonymous "controls" — which by
definition cannot have real epistasis — at the same rate as real variants.
**This tool should not be used as a stratifier until the SE miscalibration
is fixed** (likely by inflating SE by the empirically-derived factor, or
recalibrating per region, since the ratio may not be constant across the
protein).

---

## Summary table — every claim, current status, direction

| # | Claim | Status | For / Against / Neutral |
|---|---|---|---|
| 1.1 | Original 3-bucket ESM-2 correlation (0.53/0.35/0.17) | Superseded | Was FOR; now unsupported |
| 1.3 | folinate_response predicts error | DROPPED | Against |
| 1.3 | e.r predicts error | DROPPED, clean | Against |
| 2.1 | e.b predicts error (raw) | Survives but 78-81% artifact | Weakly For |
| 3.1 | e.b survives multivariable controls | Survives | Weakly For |
| 3.2 | e.b result is uniform across protein | Fails (region 4) | Against uniformity |
| 4.4/4.5 | ESM-2 beats matched placebo on rank | Survives (rank metric) | For (rank-based) |
| 5.2/5.3 | delta_ESM vs e.b, signed | Real, ~0% artifact | **Against** ESM-2 (negative direction) |
| 5.4 | delta_ESM driven by 222-proximity | Partial confound | Against clean interpretation |
| 6.2/6.3 | ESM-2 beats additive null on MAE, esp. high stratum | **Fails** | **Against** ESM-2 |
| 7.2 | Two-latent-trait structure exists | Gate cleared | Neutral (motivates more work) |
| 8.2 | SE-threshold epistatic set is well-calibrated | **Fails** | Against using the tool as-is |

**Net read:** the project has moved from an ambiguous positive result (Week
1) through increasingly rigorous null-testing to a real, if modest, negative
finding (ESM-2 does not use background context well, and using it can hurt)
— with one unresolved internal contradiction (rank vs. MAE, item 4.5 vs 6.3)
that determines whether the negative finding is total or partial.

---

## What's next (as previously recommended, unchanged)

1. **Reconcile the rank-vs-MAE disagreement** (script 30's positive rank
   result vs. script 34's negative MAE result). Same stratification, both
   metrics, one output table, so the tension is documented in one place
   instead of scattered across scripts 16/30/34. This determines whether the
   final claim is "ESM-2 fails on strong interaction" (unqualified) or
   "depends which metric you trust" (qualified). **Do this first** — it
   changes how everything else should be written up.

2. **Fix script 35's SE calibration** before using the epistatic-set flag
   anywhere downstream. Either inflate SE by the empirical ~3.76x factor (or
   refit that factor per region, since it may not be constant) and
   re-threshold, or fall back to a rank-based definition that doesn't lean on
   SE's absolute scale.

3. **Run the two-trait MoCHI refit** (bidimensional global epistasis,
   catalytic vs. regulatory domain) now that script 36 cleared the gate for
   it. This could explain the region-4 anomaly and the own/published e.b
   mid-range disagreement with a named, falsifiable mechanism rather than
   leaving both as unexplained caveats.
