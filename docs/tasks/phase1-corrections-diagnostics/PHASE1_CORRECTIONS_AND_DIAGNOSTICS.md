# Phase 1 — Corrections, the Placebo Test, and Cheap Diagnostics

Source: two independent adversarial reviews of `MTHFR_REVIEW_DOCUMENT.md`,
synthesized and cross-checked. This is the first of three staged
sessions. Everything here uses data already on disk or already cached
from prior sessions — no new model scoring beyond what a handful of
already-cached background substitutions require. Nothing here should
take more than an afternoon in aggregate; if any single task looks like
it needs new heavy compute, stop and flag it rather than improvising a
workaround.

**This session is long by task count, not by runtime.** Eighteen
sub-tasks across nine groups. Use the log itself as your checkpoint —
if you lose context partway through, re-read what you've already
written before continuing, the same way prior sessions have recovered
from compaction.

---

## Group A — Fix the disattenuation arithmetic (§3.3)

**Task A1 — Compute the self-consistent, within-family disattenuated value**
- A1a. The current write-up divides ESM-2's numerator (−0.0881) by
  ESM-1v's reliability (0.0844) — a ratio of two quantities measured on
  different models. Compute the self-consistent version instead: take
  the five ESM-1v checkpoints' own mean anchor (−0.0156) and disattenuate
  it using ESM-1v's own reliability (0.0844) and the target's reliability
  (0.6363). Report both the delta-only and fully-corrected versions.
- A1b. Report the 95% CI on the five-checkpoint mean (n=5, sd=0.0211) and
  propagate it through the same disattenuation formula, so the
  within-family corrected value has its own honest interval, not just a
  point estimate.
- A1c. State plainly, side by side: ESM-2's raw, uncorrected anchor
  (−0.0881) versus ESM-1v's within-family corrected value. If ESM-2's raw
  value already exceeds ESM-1v's ceiling, say so explicitly — that is a
  genuinely different, and more defensible, framing than the withdrawn
  cross-model ratio.

---

## Group B — Give the anchor an instance-inclusive interval

**Task B1 — Two-component variance decomposition**
- B1a. Compute Var_instance from the five ESM-1v checkpoint anchors
  (sample variance, n=5) and Var_cluster from the position-cluster
  bootstrap SE already on record for the headline anchor. Combine them
  (sum of variances, independence assumed and stated as an assumption)
  into an instance-inclusive SE.
- B1b. Report the resulting instance-inclusive interval around the
  ESM-1v five-checkpoint mean (−0.0156), and separately note what the
  same combined SE would imply if centered on ESM-2's single-checkpoint
  value, with an explicit caveat that ESM-2 has only one checkpoint so
  this second framing is illustrative, not a real interval.
- B1c. State plainly whether the instance-inclusive interval around the
  ESM-1v mean excludes or includes zero.

---

## Group C — Reconcile the severity-partial discrepancy (§1.3)

**Task C1 — Resolve why the linear partial and the spline partial disagree**
- C1a. Compute the plain linear partial correlation of delta_ESM and
  own_e.b controlling for WT-background severity, using the exact
  formula: ρ_DE·S = [ρ_DE − ρ_DS·ρ_ES] / √[(1−ρ_DS²)(1−ρ_ES²)]. Use
  delta_ESM's own project-native severity column (not a ProteinGym
  column) for both ρ_DS and ρ_ES, and confirm this is the same
  variable used to compute the originally-reported 94–97%-retained
  spline result. State explicitly whether the two prior figures
  (−0.324 and +0.0854) came from the same severity column or different
  ones — this is the first thing to check, before recomputing anything.
- C1b. If the columns match, recompute the existing spline/cross-fit
  partial and confirm whether it truly retains 94–97% or whether that
  number was itself an error. If the columns don't match, recompute
  both the linear and spline partials using one consistent severity
  column and report both fresh.
- C1c. State the corrected retention percentage plainly, whichever it
  turns out to be, and update any internal note that cited the
  original 94–97% figure.

---

## Group D — Derive ρ_E via the correlated-error formula (replaces the −191 headline)

**Task D1 — Solve for the error correlation, using the exact formula below**

Background, stated precisely so this is implemented correctly the first
time. Extending Lord's model to allow correlated measurement errors
(Williams & Zimmerman 1977; independently re-derived and confirmed this
session's planning phase from the same true-score decomposition used for
Lord's original formula) gives:

```
reliability(D) = [Num_Lord + 2·ρ_E·√((1−r_XX)(1−r_YY)·Var(X)·Var(Y))] / Var(D)

where:
  Num_Lord = r_XX·Var(X) + r_YY·Var(Y) − 2·r_XY·√(Var(X)·Var(Y))
  Var(D)   = Var(X) + Var(Y) − 2·r_XY·√(Var(X)·Var(Y))    [measured directly from D = Y−X data]
```

Solving for ρ_E given an observed reliability(D):

```
ρ_E = [observed_reliability · Var(D) − Num_Lord] / [2·√((1−r_XX)(1−r_YY)·Var(X)·Var(Y))]
```

- D1a. Using the exact same five input quantities already computed in
  the prior session's D1 entry (r_XX=0.882637, r_YY=0.882150,
  r_XY=0.999387 [median], Var(X) and Var(Y) per the rank-scale primary
  construction already on record), solve for ρ_E using the formula
  above, with the observed reliability(D) = 0.084365 (the real,
  re-derived cross-checkpoint delta agreement).
- D1b. Gate: verify that plugging the solved ρ_E back into the forward
  formula reproduces 0.084365 to numerical precision. This is an
  algebraic identity check, not independent validation — state that
  plainly in the output, exactly as the task doc that specified this
  formula intends.
- D1c. Report ρ_E with a bootstrap interval: resample positions, recompute
  all five inputs and ρ_E fresh within each draw (same position-cluster
  convention as every other bootstrap in this project), report the
  resulting distribution's percentiles.
- D1d. Write one clean, quote-ready sentence stating the result plainly:
  what fraction of each checkpoint's idiosyncratic deviation is shared
  between the wild-type and A222V backgrounds, and what fraction is not.
  This sentence, not the −191 figure, becomes the primary quotable number
  for this section going forward. Retain the −191 calculation in the
  record as a labeled illustration of why the naive independent-error
  formula fails, not as a headline number.

---

## Group E — Fix the 150M/650M frame mismatch (§1.5)

**Task E1 — Recompute ESM-1v agreement on the matched 100-position subset**
- E1a. Identify the exact 100-position subset used for the pre-registered
  150M-vs-650M comparison. Recompute the five ESM-1v checkpoints'
  pairwise agreement (both raw-score and delta versions, same median-of-10
  convention) restricted to that same 100-position subset.
- E1b. Report both frames side by side: ESM-1v agreement on the full
  654-position frame versus on the matched 100-position subset, and the
  150M/650M comparison's own value, all three together.
- E1c. State plainly which reading the result supports: if ESM-1v's
  agreement also drops substantially on the 100-position subset, the
  150M/650M scale non-replication is much less alarming than currently
  written. If ESM-1v's agreement holds near 0.88 even on the restricted
  subset, the scale non-replication claim is strengthened. Report
  whichever is actually true.

---

## Group F — The placebo-background test (the single most decisive item in this session)

**Task F1 — Correlate cached background substitutions against A222V's own measured e.b**
- F1a. Locate the cached delta scores from the AE1/AE2 position-vs-identity
  analysis and the SESS W-series background sweep (roughly 87 background
  substitutions already scored on a common ~120-position subset — confirm
  the exact count and position overlap from the actual cached files
  before proceeding, do not assume the number from this doc).
- F1b. For each cached background substitution b (excluding A222V itself),
  compute ρ(delta_ESM computed with background b, A222V's own measured
  own_e.b) — i.e., treat b as a placebo stand-in for A222V and ask whether
  its shift statistic correlates with the real, measured A222V interaction
  data. Use the same position-cluster bootstrap convention throughout.
- F1c. Report the full distribution of these placebo correlations (mean,
  sd, range, and where A222V's own real correlation sits relative to
  that distribution — percentile or exact rank).
- F1d. State the verdict plainly, per the three possible outcomes:
  - If placebo correlations center near zero and A222V is a clear
    outlier: this is strong support that the anchor is background-specific,
    not a generic artifact. Report this as the single strongest piece of
    evidence for the anchor in the entire project.
  - If placebo correlations match A222V's magnitude: the anchor is not
    distinguishable from a generic aliasing property of which positions
    the model happens to move scores for. State this plainly — it does
    not mean the project failed, it means the central finding shifts from
    "A222V has an interaction signal" to something about the shift
    statistic's generic behavior, which is itself worth knowing.
  - If results are dispersed with A222V inside the distribution but not
    at an extreme: report this as inconclusive on this specific question,
    consistent with the instance-variance concern from Group B.
- F1e. This test uses only cached, already-scored data — no new model
  runs. If the cache doesn't cover enough positions or backgrounds to make
  this a meaningful test, say so plainly and report what coverage was
  actually available rather than stretching a thin result.

---

## Group G — Precision-stratified anchor

**Task G1 — Does the anchor rise with target precision?**
- G1a. Propagate each variant's per-condition standard errors through
  the WLS-plus-multiplicative-expectation construction (delta method) to
  get an approximate per-variant SE on own_e.b. Stratify into quintiles
  by this SE (most to least precise).
- G1b. Report the anchor (delta_ESM vs own_e.b, same convention) within
  each quintile, with CIs.
- G1c. State the verdict plainly: if |ρ| rises monotonically as precision
  improves, this is direct empirical evidence the anchor is real signal
  attenuated by noise — report this as a positive, affirmative finding
  that does not depend on any disattenuation assumption. If |ρ| is flat
  or falls with precision, say that plainly instead.

---

## Group H — Region batch-effect diagnostic

**Task H1 — Test whether region 4's anomalies are library/batch artifacts**
- H1a. Compare per-region distributions of: read depth (if available),
  per-variant SE, synonymous-variant variance, and WT-arm fitness, across
  all four mutagenesis regions.
- H1b. State plainly whether region 4 (or any region) differs
  systematically on these axes from the others. If it does, note this as
  the leading candidate explanation for region 4's anomalous findings
  (the depth reversal, the −237/+010 anchor pattern) — a mutagenesis
  library or batch effect, not necessarily biology — and recommend region
  fixed effects become the default treatment in any future analysis
  rather than a sensitivity check.

---

## Group I — Per-condition anchors (free internal replication)

**Task I1 — Report the anchor separately for each of the four folinate conditions**
- I1a. Compute delta_ESM vs. e.b separately within each of the four
  folinate concentration conditions (not the pooled WLS residual), same
  bootstrap convention.
- I1b. Report all four, with CIs, and state whether the sign and rough
  magnitude are consistent across conditions or whether they track each
  condition's mean fitness level (which would suggest a measurement-scale
  artifact rather than a stable effect).

---

## Group J — A222V's over-shift result, tested for seed stability

**Task J1 — Does the +0.0212 residual replicate across ESM-1v checkpoints?**
- J1a. Using the same 30-background, 120-position design that produced
  the +0.02121 [+0.00465, +0.03934] result on ESM-2, recompute the
  identical A222V-residual statistic separately for each of the five
  ESM-1v checkpoints (reuse cached background scores where available;
  if any checkpoint lacks the needed background coverage, say so and
  report what's computable).
- J1b. Report all five values with CIs, and state plainly whether the
  result is seed-stable or not. If it is not stable, flag this finding
  as exploratory-only going forward and remove it from any confident
  framing in future write-ups.

---

## Group K — PC1 / global-mode check on the delta matrix

**Task K1 — Is the shift statistic dominated by one global representational mode?**
- K1a. Build the 654×19 delta_ESM matrix (positions × substitutions).
  Run SVD. Report the fraction of variance in PC1 and PC1–PC3.
- K1b. Run the same SVD on the cached placebo-background matrices from
  Group F (as many as coverage allows) and compare PC1's variance
  fraction and, if feasible, its spatial loading pattern relative to
  position 222.
- K1c. Project out PC1 from the real A222V delta matrix and recompute the
  anchor on the residual. Report whether the anchor survives, grows, or
  disappears. Any outcome is reportable — state it plainly.

---

## Group L — Cheap verification and provenance checks

**Task L1 — Confirm position-222 rows are excluded**
- L1a. Under masked-marginal scoring, delta_ESM is identically zero at
  position 222 itself (the WT-background and A222V-background inputs are
  identical once position 222 is masked). Confirm directly from the
  10,757-row analysis table that zero rows exist at position 222. If any
  do exist, report exactly how many and flag this as a correction needed
  before any further analysis trusts the rank statistics or the
  distance analysis (where position-222 rows would sit at distance zero).

**Task L2 — ThermoMPNN-D sign-convention audit**
- L2a. Run the identical 123-substitution buried-hydrophobic-to-charged
  audit already used for ThermoMPNN's raw ΔΔG, on ThermoMPNN-D's
  single-mutant head scores. Report whether it passes the same way
  (should score uniformly destabilizing).
- L2b. State plainly whether the ThermoMPNN-vs-ThermoMPNN-D sign
  disagreement at A222V specifically (−0.0439 vs +0.807) is a real
  disagreement between two models or a sign-convention artifact between
  the two scoring heads.

**Task L3 — interaction_D dynamic-range check**
- L3a. Report the SD and interquartile range of ThermoMPNN-D's
  interaction_D term on the full 9,595-variant analysis set, and
  separately on a proximal-pair subset (pairs within 8 Å, if a
  sufficient number exist in this dataset; if not, report what's
  available and say so).
- L3b. State plainly whether the dynamic range collapses on the full
  (mostly long-range) set relative to a proximal subset — if so, the
  existing null result on interaction_D may be a floor effect rather
  than a genuine null about structure-based interaction prediction, and
  this caveat should be added wherever that null is cited.

**Task L4 — GRB2 provenance check**
- L4a. Confirm exactly what source `scripts/73` / `scripts/74` actually
  pulled for the GRB2 positive control, and what "N208G" refers to in
  that source's own numbering. A full-text search of Faure et al. 2022
  (the paper this project has been citing for GRB2) found zero mentions
  of "N208G" anywhere — confirm whether the GRB2 dataset in use actually
  derives from that paper, from a ProteinGym-specific curation of it
  under different numbering, or from a different source entirely. Report
  plainly whichever is true; do not assume the citation is correct
  without checking.

---

## Group M — Surface the still-missing ClinVar result and fix the α discrepancy

**Task M1 — Quote Z3's actual ClinVar finding, verbatim**
- M1a. This has been requested and marked "completed" in at least one
  prior session's SUMMARY without the actual number ever reaching the
  project's write-up documents. Locate the actual Z3 entry (from the
  true-final-closeout session) and quote its real result verbatim into
  this session's log. If it shows the task never actually produced a
  usable number, say so plainly rather than inventing one.

**Task M2 — Confirm and log the α discrepancy, do not touch RESULTS.md**
- M2a. Re-confirm (already established in a prior session): `scripts/97`
  used and pre-registered α = 0.05; `RESULTS.md` states 0.01. This is a
  known, already-diagnosed error. Log the confirmation again here for
  completeness, but do **not** edit RESULTS.md — that requires the
  user's own explicit new authorization, not a standing instruction in
  this task doc.

---

## What NOT to do this session

Do not attempt the GB1 regime map, the RBD replication, the multidms
refit, the full-frame (all 654 positions) placebo-background scoring, or
the ESM-2 model-size ladder beyond what already exists (150M/650M). Those
are Phase 2 and Phase 3, staged behind this session's results. Do not
touch `RESULTS.md`. Do not re-run anything from the manuscript-review-response
or C1-prime sessions — their results stand as-is.

---

## Suggested execution order

1. **Group F (placebo test) and Group D (ρ_E) first** — these are the two
   most consequential results in this session and should be done with
   full attention while fresh.
2. **Group A, B, C** — the three arithmetic corrections, straightforward
   once the exact input values are confirmed.
3. **Group E, G, H, I, J, K** — independent diagnostics, any order,
   can interleave.
4. **Group L, M** — verification and provenance checks, lowest priority
   but cheap; do whenever convenient.

Append a final `## SUMMARY` with every task's headline result, explicitly
including: Group F's verdict (this is the one to read first), Group D's
final ρ_E sentence, Group A's within-family corrected value, whether
Group B's instance-inclusive interval excludes zero, and a plain
statement of what — if anything — this session changes about the
project's central claim.
