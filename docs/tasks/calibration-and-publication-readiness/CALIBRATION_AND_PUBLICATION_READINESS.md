# Calibration Test, Precise Statistics, and Publication-Readiness Items

Source: external skeptical review of the pitch document, cross-checked against
the primary literature. The review's single highest-value, most concrete,
most actionable finding: **Nambiar et al. 2025 (bioRxiv 10.1101/2025.09.14.676130,
"Protein Language Models Capture Structural and Functional Epistasis in a
Zero-Shot Setting") report that raw, uncalibrated ESM-2 log-likelihood scores
give Pearson r ≈ 0.09–0.18 against real measured epistasis across three
proteins — and this project's own raw ρ ≈ −0.08 to −0.09 sits suspiciously
close to that same "uncalibrated" range.** Nambiar's paper shows that applying
a specific two-stage nonlinear calibration to the same raw scores raises their
correlation to r ≈ 0.26–0.38. This project has never applied an analogous
calibration. That is a live, specific, checkable alternative explanation for
why this project's effect looks small and doesn't track real interaction
well, and it must be tested — honestly, in either direction — before any
claim about "ESM-2 lacks the relevant information" stands as currently
written.

**This is also, not coincidentally, the exact paper this project's own
future-directions section already named as its eventual replication target.**
That target has now arrived earlier than planned, in the more useful form of
"apply their calibration to our own data first," which is cheaper, faster,
and more directly decisive than a full external replication would have been.

---

## Group N — The calibration test (highest priority, do this first)

**Task N1 — Retrieve the exact calibration functional form**
- N1a. Check bioRxiv for supplementary materials (a Methods PDF, supplementary
  tables) and check for a released code repository (search GitHub for the
  paper's authors — Ananthan Nambiar, Sergei Maslov, UIUC Bioengineering —
  and for the paper's own title/DOI). The paper's Methods describes the
  transformation as: monotone, two free parameters (b, c), fit by nonlinear
  least squares, "linear dependence at low values of x < −c" and "plateau
  starting for x > c." If the exact closed-form equation (their Eqn. 2) or
  code is found, use it exactly, cited.
- N1b. If neither the exact equation nor code can be found: construct the
  simplest monotone two-parameter function matching that qualitative
  description exactly — a softplus-based saturating curve is the natural fit
  (linear for very negative input, asymptotically flat for large positive
  input, exactly two free parameters). State the exact functional form
  chosen in the script's docstring BEFORE any fitting, and disclose plainly,
  in both the docstring and the eventual log entry, that this is a
  reconstruction from the paper's qualitative description, not a copy of
  their actual equation — this distinction must never be blurred in any
  later write-up.

**Task N2 — Fit the two-stage calibration on MTHFR's own data, following Nambiar's exact protocol**
- N2a. Adapt Nambiar's calibration-subset protocol to MTHFR's single-background
  design (Nambiar's datasets have many different background mutations;
  MTHFR has one fixed background, A222V, applied to many variants — this
  structural difference must be stated explicitly, not silently assumed
  away): draw a 20% random calibration subset of MTHFR variants (seed 0,
  documented), hold out the remaining 80% for all downstream evaluation.
  This mirrors Nambiar's own calibration/held-out split discipline exactly,
  and is essential — fitting and testing on the same rows would be exactly
  the circularity problem this project's whole methodology exists to avoid.
- N2b. Fit φ1 (the single-mutant/wild-type-background curve): regress real
  measured WT-background fitness (log scale, matching Nambiar's convention)
  against raw ESM-2 relative log-likelihood scores, using only the 20%
  calibration subset's WT-background values.
- N2c. Fit φ2 (the conditional/background curve): regress real measured
  A222V-background fitness (log scale) against raw ESM-2 relative
  log-likelihood scores computed in the A222V background, using only the
  20% calibration subset.
- N2d. Report both fits' parameters, fit quality, and a plot-equivalent
  description (binned means vs. fitted curve, the same diagnostic Nambiar's
  own Figure 2 uses) so the calibration itself can be sanity-checked before
  it's used for anything.

**Task N3 — Recompute the headline correlation on calibrated scores, held-out only**
- N3a. Using ONLY the 80% held-out set (never the calibration subset),
  recompute the project's primary statistic (signed correlation between
  ESM-2's background-induced shift and real measured epistasis) using the
  φ1/φ2-CALIBRATED scores instead of raw log-likelihoods. Same sign-flip
  re-derivation null, same position-cluster bootstrap, same reporting
  conventions as every other headline number in this project.
- N3b. Separately, ALSO compute Nambiar's own epistasis definition exactly
  as they define it (their symmetrized two-path average, Eqn. 4 in their
  Methods) directly on MTHFR's real single- and background-fitness data,
  using the calibrated scores — this is the most literal possible
  replication of their exact method on this project's data, distinct from
  (and complementary to) N3a's use of this project's own e.b construction.
  Report both. If they disagree, report the disagreement plainly rather
  than picking the more favorable one.
- N3c. Report the raw-vs-calibrated comparison directly and honestly,
  exactly as Nambiar's own Figure 3d does: raw correlation, calibrated
  correlation, side by side, on the same held-out rows.
- N3d. State the plain verdict: does calibration change the magnitude,
  significance, or interpretation of the finding? If it moves the
  correlation meaningfully closer to Nambiar's reported calibrated range
  (~0.26–0.38 in magnitude, allowing for the sign difference already
  established in this project — their datasets and epistasis sign
  convention differ from MTHFR's, so compare magnitudes and directional
  consistency with own_e_b's established sign, not a literal number match),
  that is a major finding requiring the whole project's interpretation to be
  revised. If it does not move materially, that is equally important and
  argues against the calibration-gap explanation for this project's small
  effect size.

**Task N4 — Does calibration change AC4's seed-instability finding?**
- N4a. Locate the five ESM-1v seed members' saved score outputs from AC4
  (the score CSVs, not the deleted model weights — confirm these still
  exist on disk before doing anything else; if any are missing, note which
  and proceed with what's available). Do NOT re-fetch any model weights for
  this task.
- N4b. Apply the SAME calibration (φ1/φ2, fit once on MTHFR's own 20%
  calibration subset per N2 — do not refit per-seed, since Nambiar's own
  protocol fits the calibration once and applies it broadly) to each of the
  five members' raw scores.
- N4c. Recompute each member's calibrated delta-vs-e.b correlation, and
  recompute cross-member agreement (both the sign-agreement check and the
  correlation-of-correlations check from AC2's convention) on the CALIBRATED
  scores, exactly as AC4d did on raw scores.
- N4d. State plainly: does calibration improve cross-seed agreement
  (evidence that raw-scale noise was inflating apparent instability) or
  leave it unchanged/worse (evidence the instability is not a
  calibration-scale artifact)? Either answer is a real, useful finding —
  do not reach for the more convenient one.

---

## Group O — Precise statistic definition (cheap, do alongside Group N)

**Task O1 — One unambiguous, code-verified statement of the exact quantity being correlated**
- O1a. The review flagged real ambiguity: is the project's headline statistic
  a correlation between raw ESM-2 scores and raw fitness, or between
  background-INDUCED SHIFTS in each? Resolve this with a single paragraph,
  verified against the actual code (script 32 and script 33, quoted
  verbatim), stating precisely: what delta_ESM is (a score computed in
  which background(s), combined how), what own_e_b is (constructed how,
  from which raw quantities), and confirming they are shift-vs-shift
  quantities, not raw-vs-raw — or correcting the record if they are not.
  This is a documentation and verification task, not a new analysis.

---

## Group P — Multiplicity accounting across the whole project

**Task P1 — Compile every major pre-registered headline-adjacent p-value into one table**
- P1a. Walk every log file across this project (OVERNIGHT_LOG, the
  comparators SESSION_LOG, CLOSEOUT_LOG, DEEPDIVE_LOG, this doc's own
  eventual log) and extract every p-value that was treated as a headline
  or near-headline result — not every exploratory secondary, but every
  number that has appeared or could plausibly appear in a write-up's main
  claims. Build one flat table: test name, p-value, source entry.
- P1b. Apply Holm-Bonferroni correction across that full set (the same
  method already used and cited in the COPD project — real continuity,
  worth noting in any write-up) and report which findings survive at a
  family-wise α = 0.05.
- P1c. State plainly which of the project's currently-claimed "real" results
  survive this correction and which do not. This may change how confidently
  several Tier 1/2 findings from the pitch summary can be stated.

---

## Group Q — The clinical stakes number

**Task Q1 — How many real variants would this actually affect?**
- Q1a. Fetch ClinVar data for MTHFR (gene symbol MTHFR, or by the same
  UniProt/RefSeq identifiers already established in this project) —
  variants classified as VUS (variant of uncertain significance) or with
  conflicting interpretations. Standard ClinVar API/FTP access, within the
  same data-fetch budget discipline as every other fetch in this project.
- Q1b. Cross-reference against the atlas's own missense variant set (the
  canonical manifest from AF2) to identify which ClinVar VUS correspond to
  variants this project has actual measured or predicted data for.
- Q1c. Compute the concrete number the review and the pitch document's own
  future-directions section both flagged as missing: how many of these VUS
  would be scored meaningfully differently under background-aware
  (A222V-conditioned) vs. background-naive prediction — using whatever
  practical threshold for "meaningfully differently" seems defensible
  (e.g., a sign flip, or a shift larger than the project's own established
  detection floor), stated explicitly and pre-registered before computing
  the number.
- Q1d. Report this as a single, clearly-stated number with its exact
  definition attached — this is the concrete "so what" the review
  specifically asked for.

---

## Group R — NOT for this session (explicitly excluded)

The review's citation/differentiation recommendation (explicitly and
accurately distinguishing this project from Nambiar et al. 2025, the 2022
NeurIPS rescue-mutation paper, and the 2026 CSHL population-scale paper in
any eventual write-up) is a writing and framing task, not an analysis task.
Do not draft citation text or a differentiation paragraph in this session —
that belongs with the user, informed by whatever Group N's results actually
show, since how the project is differentiated depends heavily on whether the
calibration test moves the headline finding or not.

---

## Suggested execution order

1. **Group N (N1 → N2 → N3 → N4) first, uninterrupted.** This is the
   single highest-value test in this entire task doc and determines how
   several other things should even be interpreted.
2. **Group O** — quick, do it once Group N's results are in hand, since the
   precise-statistic writeup should describe whatever construction N3
   actually used.
3. **Group P and Group Q** — independent of each other and of Group N,
   can run whenever convenient, including alongside Group N if resources
   allow.
4. **Group R** — do not attempt.

If Group N's calibration test shows the effect moves substantially toward
Nambiar's calibrated range, stop and flag this prominently at the top of the
log's SUMMARY — this would be the most important finding of the session and
should not be buried under Groups O/P/Q's more routine bookkeeping work.
