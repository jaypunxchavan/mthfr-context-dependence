# Review Triage — Tasks & Subtasks

Source: independent review of `MTHFR_RESULTS_LOG.md`, run in a fresh chat
with no prior context. Original item numbers from that review are kept in
brackets throughout for traceability back to the source document.

Two items below are flagged **STOP-FIRST** — cheap checks that, if they come
back badly, invalidate conclusions the log currently treats as settled.
Do these before anything else, including before reading the rest of this
triage in detail.

---

## STOP-FIRST — five-minute checks that could overturn a headline

### S1. Own vs. published e.b — possible column duplication bug [item 9]
Script 32 reported **identical** correlations to three decimals for
"signed, published e.b" and "signed, own e_b" (both -0.088x). Section 7
of the log separately claims own/published e.b *disagree* in the
mid-range. Both cannot be true as described. Check whether script 33 (or
32) accidentally read the same column twice under two different names.
**If this is a real bug, it doesn't just weaken 5.3 — it means the
"validates against published" framing used throughout the project may be
silently checking a column against itself in at least one place.**

### S2. Sign convention audit [item 8]
Confirm, explicitly, on real rows: does the atlas's own "significantly
less functional in A222V" label correspond to e.b < 0? Does delta_ESM's
sign convention mean "ESM-2 thinks it's worse in A222V" in the same
direction? One flipped sign turns "ESM-2 moves the wrong way" into
"ESM-2 moves the right way, weakly." This has been assumed, never
verified against a labeled example.

**If S1 or S2 comes back bad, stop and fix before running anything else in
this document — several groups below build on 5.2/5.3 being correct as
described.**

---

## Group A — Inference validity (cuts across almost every result)

**Task A1 — Confirm position-clustered inference was actually used everywhere it's claimed** [items 7, 14]
- A1a. Audit which scripts' CIs are position-cluster-bootstrapped (the
  project's stated house convention) vs. row-level. Script 33's sign-flip
  null specifically: was it per-variant or per-position-block? The log's
  proximity result (ρ=-0.298) shows both delta_ESM and e.b are strongly
  position-structured, so a variant-level flip may be too narrow.
- A1b. Rerun 33's null with position-block flips if it was variant-level,
  compare.
- A1c. Confirm 34's bootstrap CIs (6.2/6.3) were built by resampling
  positions, not variants. State explicitly in the script's output.

**Task A2 — Accounting for excluded/missing rows** [item 18]
- A2a. High stratum = 3,586 vs. expected ~3,704 for an even tercile of
  11,113. Where did the other rows go? Check for a systematic
  fitness/region skew in what got dropped before stratification, not just
  a rounding artifact.
- A2b. Separately: why 11,113 of the full missense set (the log elsewhere
  cites 10,757–11,344 across different scripts, inconsistently) — reconcile
  which n is the actual analysis set per script and why they differ.

---

## Group B — delta_ESM validity (attacks 5.2/5.3 directly)

**Task B1 — Rule out the "flattening" confound** [items 5, 6]
- B1a. Partial correlation of delta_ESM vs. e.b, controlling for S(v|WT)
  and w.fitness (nonlinearly — spline or binned, not linear). If the
  partial correlation collapses, the "opposite direction" story is really
  "both variables track deleteriousness independently."
- B1b. Test whether delta_ESM ≈ -k·S(v|WT) (compression toward zero when
  V222 is in the sequence). Plot delta_ESM against S(v|WT) directly.
- B1c. Per-position entropy of ESM-2's output distribution, WT vs. A222V
  background. If entropy rises with V222 present, that's a generic
  distribution-flattening effect, not epistasis-specific.

**Task B2 — Redo the null at the right granularity** [item 7, ties to A1a]
- B2a. Already covered by A1a/A1b — listed here for visibility since it
  specifically threatens the "~0% artifact" claim in 5.3.

**Task B3 — Correct the "~0% artifact" framing regardless of B1's outcome** [item 5.3's own framing]
- B3a. Note in the writeup: a sign-flip null on a signed variable centers
  on zero by construction. It rules out the e.b-construction artifact
  specifically (the same failure mode that killed 77-82% of everything
  else). It does NOT rule out confounding (B1) or rule in "real epistasis."
  Rewrite 5.3's language before it goes into any external-facing doc.

---

## Group C — MAE result robustness (attacks 6.2/6.3)

**Task C1 — Reconciliation table** [items 1, 2, 3, 10]
- C1a. Build one table: rows = {S_WT, S_A222V, delta_ESM, matched
  synthetic, BLOSUM62, w.fitness}, columns = {target: A222V fitness, e.b,
  w.fitness} × {metric: rank, MAE, MSE} × {stratum: low/mid/high}.
- C1b. Specifically test: does ESM-2 on the WT sequence alone retain as
  much high-stratum rank signal against the matched synthetic as ESM-2 on
  A222V does? If yes, 4.5's "retention" has nothing to do with background
  info at all — it's independence from WT-arm measurement noise.
- C1c. Test whether trivially WT-independent predictors (raw BLOSUM62,
  Grantham distance) also "beat" the matched synthetic. If so, script 30
  was measuring noise-sharing with w.fitness, not epistasis detection.
- C1d. Rank correlation between S(v|A222V bg) and S(v|WT bg) directly. If
  it's 0.99+, the MAE story in 6.2 is a few hundred rank swaps, not a
  broad pattern.

**Task C2 — Robustness of the MAE difference itself** [items 11, 12, 13]
- C2a. Influence analysis: which variants drive the +0.00053 diff? If a
  few dozen near-222 variants account for it, the story is local
  (consistent with 5.4's proximity confound), not "background info hurts"
  broadly.
- C2b. Fold-seed sensitivity: rerun the cross-fit isotonic calibration
  under ~50 different position-fold seeds. If the MAE diff's CI width is
  comparable to its cross-seed variance, the result isn't as clean as one
  seed suggests.
- C2c. Does the high-stratum verdict hold under MSE instead of MAE?
  Isotonic regression targets the conditional mean (squared-error optimal);
  evaluating it on MAE (median-optimal) is a loss/calibration mismatch that
  could matter given how small these effects are.

**Task C3 — Oracle ceiling** [item 34]
- C3a. Build a synthetic "oracle" predictor: true e.b + noise matched to
  the synonymous-derived reliability (~0.64). Measure its MAE improvement
  over the null. Report 6.3's -0.00241 loss against that ceiling, not in
  isolation. Also report the correlation disattenuation: does -0.088
  become materially larger once corrected for measurement reliability?

---

## Group D — Stratifier quality (winner's-curse risk)

**Task D1 — Is "high interaction" partly just "high noise"?** [items 15, 16, 17]
- D1a. Check whether the high-|e.b| stratum is enriched for high-SE
  variants (ties directly to script 35's known SE miscalibration).
- D1b. Rerun 6.3's stratification using an empirical-Bayes shrunken e.b
  instead of raw e.b. See if the high-stratum verdict changes.
- D1c. Add a nonsense-variant floor alongside the synonymous floor.
  Nonsense variants are dead in both backgrounds, so true e.b ≈ 0 — a
  second noise-floor check at the opposite end of the fitness range from
  synonymous variants, which may have heteroscedastic noise properties.

---

## Group E — Two-trait diagnostic validity (attacks 7.2)

**Task E1 — Domain vs. region confound** [items 19, 20]
- E1a. The decision rule in script 36 fires on statistical significance
  alone at n>10,000 — nearly any nonzero mean will exclude zero at that
  scale. Reframe the gate around effect size (disagreement magnitude
  relative to e.b's SD, currently ~0.03-0.04 vs SD 0.24) rather than
  CI-excludes-zero.
- E1b. **Decisive test**: does the own/published disagreement change at
  DOMAIN boundaries (predicted by the two-trait hypothesis) or at
  MUTAGENESIS-REGION boundaries (predicted by a normalization artifact,
  since regions were independently rescaled by the original atlas
  authors)? Where domain and region boundaries diverge, check which one
  the data actually follows. This is cheap and should run **before** any
  MoCHI refit — it may make the refit unnecessary, or sharpen exactly what
  it needs to control for.

---

## Group F — Control specification

**Task F1 — Nonlinear fitness control** [item 21]
- F1a. Rerun 3.1's multivariable model with a spline (or binned) term for
  base fitness instead of linear — context-dependence and ESM-2 error both
  plausibly peak at intermediate fitness (inverted-U), which a linear term
  can't absorb.
- F1b. Run the pre-registered 10th-90th percentile restriction (proposal
  5.6c) — flagged in the review as specified but never actually run.

**Task F2 — Region-2 recalibration overfit check** [item 22]
- F2a. Confirm the within-region isotonic calibration (4.3) was
  cross-fitted WITHIN region (held-out positions inside that region), not
  just position-held-out globally. Fewer positions per region = more
  overfitting room, and a post-hoc fix that doubled a correlation deserves
  this check before being trusted.

---

## Group G — What "real epistasis" means here

**Task G1 — Global vs. specific epistasis decomposition** [item 23]
- G1a. How much of e.b's variance is explained by a monotone nonlinear
  function of w.fitness alone? If most of it, the atlas's "interaction" is
  substantially global/threshold epistasis — which a single-site masked-
  marginal model was never mechanistically positioned to capture. This
  reframes the fair test as: does ESM-2 predict the SPECIFIC residual left
  after removing global epistasis, not the raw e.b.

**Task G2 — Stability-mediated epistasis (ThermoMPNN)** [item 24]
- G2a. This was pre-registered and never run. If ΔΔG(v) plus A222V's own
  destabilization (crossing some threshold) predicts e.b, the conclusion
  upgrades from "ESM-2 fails" to "the interaction is predictable from
  sequence-derived stability information; ESM-2 specifically doesn't use
  it" — a more interesting and more publishable claim either way.

---

## Group H — Biological sanity checks

**Task H1 — Does ESM-2 even think A222V is deleterious?** [items 25, 26]
- H1a. Report S(A222V | WT) directly. If near-neutral, the model has no
  internal reason to propagate any correction from it.
- H1b. Check ortholog conservation at position 222. If Val occurs commonly
  in some clades, "V222 context" sensitivity may be a phylogenetic/clade
  cue rather than a destabilization signal.

**Task H2 — Sequence vs. structural distance** [items 27, 28]
- H2a. Recompute the proximity confound (5.4) using Cα 3D distance on
  6FCX instead of linear sequence distance, and separately distance to the
  FAD cofactor site. If delta_ESM tracks sequence distance but not 3D
  structure, that confirms attention locality rather than biophysics.
- H2b. Pre-register a focused local test restricted to 3D neighbors of 222
  plus FAD contacts, properly powered with position-clustered inference.
  The one place the pooled result was directionally positive (within 25
  residues, though underpowered) deserves its own clean test rather than
  being folded into the pooled negative result.

**Task H3 — Rescue-variant enrichment** [item 29]
- H3a. Does ESM-2 fail symmetrically on "worse in A222V" and "better in
  A222V" (rescue/suppressor) variants, or does delta_ESM enrich for the
  rescue variants at all? These are the most biologically interesting
  variants in the dataset and haven't been examined separately.

**Task H4 — Per-condition check** [item 30]
- H4a. Does 6.3's high-stratum result hold specifically at low folinate
  (where A222V's phenotype is most expressed), or is it diluted by
  averaging across all four conditions?

---

## Group I — Positive controls and comparators

**Task I1 — Pipeline validation on a known-epistatic dataset** [item 31]
- I1a. Run the delta_ESM pipeline on a dataset with established epistasis
  (a ProteinGym double-mutant set, or GB1). Without this, a negative
  result here can't be distinguished from a pipeline limitation. High
  priority — this is a sunk-cost-free sanity check on the whole approach.

**Task I2 — Explicit-coupling comparator** [item 32]
- I2a. Run an EVmutation/Potts-model coupling term J(i, 222) on the same
  data. If it also fails, the epistasis in this dataset isn't the
  coevolutionary kind ESM-2-style models are built to catch. If it
  succeeds where ESM-2 fails, the failure is specific to ESM-2's
  architecture, not the biology. Most informative single comparator on
  this entire list.

**Task I3 — Model/scoring robustness** [item 33]
- I3a. Check the pre-registered ESM-2 150M model, ESM-1v, a structure-
  aware model (SaProt), and whole-sequence pseudo-log-likelihood instead
  of masked marginals. Confirms whether the result is about ESM-2
  specifically or about masked-marginal scoring generally.

---

## Group J — Pre-registration drift audit

**Task J1 — Reconcile the extrinsic-vs-intrinsic framing** [item 35]
- J1a. The original proposal predicted extrinsic (folinate_response)
  error would exceed intrinsic (e.b) error. The actual result is the
  reverse — folinate_response failed controls, e.b weakly survived. The
  log never states this plainly as a departure from the pre-registered
  prediction. Add it explicitly, with the candidate explanation (per-
  condition calibration may absorb folinate effects as global scaling).

**Task J2 — Audit for un-run pre-registered analyses** [items 36, 37]
- J2a. Checklist against the original proposal: Steiger's test (or its
  replacement, sign-flip nulls — confirm this substitution was
  intentional and documented), the effect-size floor, the 150M model
  check, the context-precision correlation, the extrinsic-intrinsic
  correlation (limitation 7). For each: run it, or write an explicit
  deviation note explaining why not.
- J2b. Confirm and document: the primary metric changed from a
  project-derived β_intrinsic-with-SEs to the atlas's own e.b. Was this
  change ever written down as a deviation, or did it happen implicitly?

**Task J3 — Multiple-testing accounting** [item 38]
- J3a. Rough count of how many statistical tests have been run across the
  ~36 scripts to date. Pre-register the *remaining* analyses (this
  document's contents, once triaged) with effect-size-based decision
  rules fixed in advance, the same way script 36's gate was pre-committed.

**Task J4 — FDR-based SE threshold, replacing the flat 3.76x fix** [item 39]
- J4a. Instead of inflating SE by the empirical 3.76x ratio uniformly, set
  the epistatic-set threshold at a target FDR = (synonymous pass rate) /
  (missense pass rate), using the empirical null directly rather than a
  single global correction factor.
- J4b. Check whether the 3.76 ratio is constant across regions and fitness
  levels, or whether it needs to vary — directly relevant to script 35's
  known miscalibration.

---

## Group K — Practical framing (do last, after the science settles)

**Task K1 — Classification framing** [item 40]
- K1a. Of variants that cross a functional threshold only in the A222V
  background ("conditionally damaging"), what fraction does ESM-2 flag as
  damaging, and does supplying the A222V sequence change that fraction?
  Ties directly back to the original proposal's clinical motivation
  (roughly a third of rare MTHFR variants occur in cis with A222V in
  real patients).

**Task K2 — Lock the one-sentence claim** [item 41]
- K2a. Once Groups A-J are resolved, write the single honest sentence the
  whole project supports (the reviewer's draft: "Supplying the A222V
  background to ESM-2 does not improve, and marginally degrades,
  prediction of background-dependent effects, while independent evidence
  suggests the measured interaction is largely global/stability-
  mediated" — or whatever the data actually ends up saying). Decide this
  BEFORE finishing the writeup, not after, so it's clear which remaining
  analyses are essential vs. optional.

---

## Suggested execution order

1. **STOP-FIRST checks (S1, S2)** — five minutes, could invalidate 5.2/5.3 outright.
2. **Group A (inference validity)** — cheap, affects every CI in the project.
3. **Group B (delta_ESM confounds)** — cheap, directly threatens the cleanest result.
4. **Group C, Task C1 (reconciliation table)** — the central open question from the last round; C2/C3 follow once C1's table exists.
5. **Group E, Task E1b (domain vs. region boundary test)** — cheap, may make the two-trait MoCHI refit unnecessary or sharply focus it.
6. **Group I, Task I1 (pipeline validation on a known-epistatic dataset)** — sunk-cost-free, resolves whether a negative result means anything at all.
7. **Group I, Task I2 (Potts/EVmutation comparator)** — most informative single result on this list; run once I1 confirms the pipeline works.
8. **Group G, Task G2 (ThermoMPNN)** and the deferred **Group D (winner's-curse checks)** — after the above, since they refine rather than overturn.
9. **Group J (pre-registration audit)** and **Group K (framing)** — last, once the science is settled enough to know what actually needs defending.

Groups F and H sit outside the critical path — useful, but nothing in them
threatens a headline result the way A, B, C, and the S1/S2 checks do. Slot
them in opportunistically.
