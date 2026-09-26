# Disattenuation Validity, Master Ledger, and the Clustering Question

Source: a fourth-round external review, sharper than the prior three. Its
own priority order, stated explicitly: the ensemble test (already run —
see Group T below), the base-vs-delta reliability contrast, and the
clustering/effective-n question that has now been asked across three
separate rounds without a definitive answer. This doc treats those as
first priority, alongside a real structural problem the review identified
in how the project's own disattenuation logic was applied.

**Two things are already confirmed and do not need re-checking:**
the ensemble-mean run (item 85 in the review) already exists —
`[A1]` in `RELIABILITY_LOG.md`, ρ = −0.028508, matching the
Spearman-Brown prediction of ≈−0.030. And a direct full-text search of
Nambiar et al. 2025's complete paper (main text, methods, and
supplementary — one continuous PDF, confirmed) found zero mentions of a
severity-only or site-independent baseline control anywhere.

---

## Group S — The master ledger (do this first; several other tasks depend on it)

**Task S1 — One table, every number, every convention, verified fresh from disk**
- S1a. Build one table covering every correlation quoted anywhere in
  v3 or the underlying logs: predictor, target (own_e_b vs published
  e.b), statistic type (raw wild-type-background score vs delta/shift),
  signed vs absolute, n, ρ, CI, null mean, exact source file + line.
  Every value read fresh from its source CSV/log at the time this runs —
  do not copy from any prior summary, including this document's own
  characterization of what the numbers probably mean.
- S1b. Using this table, resolve the apparent contradiction directly:
  confirm that the severity-baseline table (Site_Independent, GEMME,
  ESM2_650M, etc., all reported positive) correlates RAW wild-type-
  background scores against e.b, while the project's headline −0.088 is
  delta_esm (the background-induced SHIFT) against e.b — two different
  statistics sharing a target variable, not the same statistic with
  contradictory signs. State this plainly, with the exact confirming
  evidence (column names, computation code) quoted. If this
  characterization turns out to be wrong once checked against the real
  code, say so — do not assume the explanation is correct just because
  it's the obvious one.
- S1c. Rewrite the specific v3 sentences this affects so they cannot be
  misread again: name which statistic each claim refers to, every time.

**Task S2 — The master claims ledger (every claim, every round, current status)**
- S2a. Compile every substantive claim made across this project's full
  history — the original results log's Parts 1 through 14, the deep-dive
  round, the calibration round, and the reliability round — into one
  ledger: claim, current status (confirmed / superseded / contradicted /
  never followed up), and a pointer to whatever superseded or resolved
  it if applicable.
- S2b. Specifically surface and resolve three items the current write-up
  silently dropped, each as its own ledger row:
  - The original Part II finding that A222V produces a LARGER
    representational shift than its own severity predicts (the "H1a
    reversal"). State whether the reliability framing supersedes this,
    contradicts it, or simply sits alongside it unaddressed — do not
    leave this unstated.
  - The rank-vs-MAE digest (`GROUPS_C_TO_H_DIGEST.md`'s Group C section)
    — read it now if it has genuinely never been read in full, or quote
    its actual verbatim finding if it was already read but never
    reported. This was flagged early in the project as determining the
    top-line sentence and needs its actual content on record, not just
    a note that it was checked.
  - The original additive-null MAE result (ESM-2 performing reliably
    WORSE than a no-interaction baseline in the high-interaction
    stratum) — state explicitly whether this is superseded by the
    reliability framing, still stands alongside it, or was ever directly
    reconciled with it.
- S2c. Fix the v3 sentence "all analytical questions this project set
  out to answer are resolved" — it is directly contradicted three
  paragraphs later by SaProt being blocked and the clade question being
  open. Replace with an accurate statement of exactly what is resolved
  and what genuinely remains open.

---

## Group T — Is the disattenuation valid? (highest scientific priority)

**Task T1 — Is ESM-2 an outlier relative to the ESM-1v seed distribution, or a different distribution entirely?**
- T1a. Compute exactly where ESM-2's −0.088118 sits relative to the five
  ESM-1v members' empirical distribution (mean, sd, range, and ESM-2's
  position relative to that range — not just a z-score, which assumes
  normality with n=5; report the raw rank/percentile too).
- T1b. State plainly, checked against what's actually documented about
  each model's training (Meta's own model cards/papers, not assumption):
  do ESM-2 and ESM-1v share enough of a training relationship (corpus,
  objective, architecture) to be treated as comparable draws from a
  common distribution, or are they different enough that borrowing one's
  reliability for the other isn't a licensed move at all? This is a
  factual question with a checkable answer, not a judgment call to
  hedge on.
- T1c. Give the one-sentence answer the review explicitly asked for:
  is ESM-2's number an unusually large draw from the same distribution
  the ESM-1v seeds come from, or evidence it isn't the same distribution
  at all? State which, plainly.

**Task T2 — Does the attenuation model itself hold up, distinct from whether it applies to ESM-2**
- T2a. Retrieve A1's already-run ensemble result and state explicitly:
  this is real evidence the classical-test-theory attenuation model
  describes the ESM-1v seed family's own internal behavior correctly.
  It does NOT, on its own, license applying that model's correction
  factor to a model (ESM-2) outside that seed family — that is T1's
  separate question, not resolved by T2.

**Task T3 — Propagate uncertainty in the reliability estimate itself into the disattenuated CI**
- T3a. Build a proper bootstrap: resample positions with replacement,
  and within each draw recompute BOTH the raw correlation AND whatever
  reliability estimate is being used, then compute the disattenuated
  statistic fresh in that same draw. Report the resulting empirical CI
  on the disattenuated estimate — not just the point estimate. Given
  reliability ≈0.09 is itself estimated from limited data, this interval
  is very likely to be wide; report it honestly, however wide it is.

**Task T4 — Was the reliability estimate itself computed correctly, or does positional structure inflate it?**
- T4a. Check whether AC2's and AC4's cross-checkpoint reliability
  estimates (0.084–0.098) were computed on pooled data or within-position.
  Delta vectors carry real positional structure (e.g. a distance-to-222
  gradient) — if the reliability estimate wasn't computed with position
  held fixed or clustered out, shared positional structure could inflate
  apparent cross-checkpoint agreement without reflecting any shared
  interaction signal. This is the same mechanical-inflation trap the
  calibration test caught, applied to a different quantity — recompute
  the reliability estimate in a way that isolates within-position
  agreement specifically, and report both the original and the
  position-controlled version side by side.

**Task T5 — The money figure: base-score reliability vs delta reliability, same five checkpoints**
- T5a. Compute cross-checkpoint agreement on the five ESM-1v members'
  RAW wild-type-background scores (not deltas), same statistical
  convention as the existing delta-agreement computation. Report this
  number directly alongside the already-known delta agreement
  (~0.084–0.098). This comparison does not depend on disattenuation at
  all and should be treated as a standalone, high-value result — flagged
  by the review as the strongest single figure available.

**Task T6 — Is the comparison to Nambiar's reported numbers even valid?**
- T6a. Check directly (their paper text, and their released code if
  accessible) whether Nambiar et al.'s reported calibrated correlations
  (~0.26–0.38) are themselves disattenuated for any measurement
  unreliability, or are raw observed correlations on their own data.
- T6b. If their numbers are raw (not disattenuated), state plainly that
  comparing this project's disattenuated estimate to their raw numbers
  is not a like-for-like comparison, and either drop the "lands inside
  their range" claim from any future write-up entirely, or reframe it
  explicitly as "our raw anchor sits in a similar range to their raw,
  pre-calibration numbers; we have no comparably-corrected number of
  theirs to compare our corrected estimate against."
- T6c. As a secondary, more ambitious check (attempt only if their code
  is genuinely accessible and this doesn't require excessive effort):
  whether the SAME mechanical-inflation pattern this project caught in
  its own calibration test (a shared severity term inflating apparent
  agreement/correlation) could also be present in Nambiar's own reported
  calibrated metric. This would require running their actual code on
  their actual data, not inferring it — if this isn't feasible within a
  reasonable scope, log it as a well-specified idea for the future
  generalization run instead of forcing a rushed attempt now.

---

## Group U — Positive-control estimator audit

**Task U1 — Do the GB1 and GRB2 positive controls test the actual headline estimator?**
- U1a. Read the actual scripts behind AA1 (GB1 transplant) and AA7
  (GRB2) and confirm explicitly: do they use the SAME signed sign-flip
  re-derivation null (script 33's exact code path) that produces the
  project's headline −0.088, or do they validate a different
  association/excess-over-null statistic from earlier in the project's
  history? State this with a direct code citation, not an assumption
  based on prior framing.

---

## Group V — The clustering/effective-n question (asked three times; resolve definitively this round)

**Task V1 — What is the actual clustering unit and effective n behind the detection floor, and does the anchor clear it?**
- V1a. Re-read AA4's actual detection-floor construction directly from
  its script and log entry. State explicitly and unambiguously: what is
  the resampling/clustering unit the position-cluster bootstrap actually
  uses (positions, or something else), and what is the effective sample
  size that implies — not inferred from a CI-width back-calculation, but
  read directly from the bootstrap's own resampling logic.
- V1b. Compute the 80%-power detection floor under BOTH framings
  explicitly, side by side: treating n as ~10,757 rows, and treating n
  as ~654 (or whatever the actual position count is). Report both
  numbers.
- V1c. State plainly which framing is actually correct given how the
  bootstrap is really constructed, and whether the project's own
  −0.088 anchor sits above or below the resulting floor under the
  correct framing. If it sits below its own claimed detection floor,
  say so directly — this would mean the "we had the power to detect
  this" framing needs to be retracted or substantially qualified, not
  softened.

---

## Group W — Distance stratification and stability-model clarification

**Task W1 — Does real interaction concentrate near contact, diluting the pooled correlation?**
- W1a. Test whether |e.b| itself decays with distance from position 222,
  relative to the synonymous-variant noise floor already established
  elsewhere in this project. If real interaction signal is concentrated
  in the minority of variants within structural contact range, report
  a distance-stratified (not just pooled) version of the primary
  delta_esm-vs-e.b correlation as a sensitivity check — note this
  interacts with the already-known finding that |delta_ESM| itself
  correlates negatively with distance from 222.

**Task W2 — Which stability model produced AD4's confirmed null, unambiguously**
- W2a. State in one unambiguous sentence, checked against the actual
  code: was the interaction term that survived Cα-distance de-biasing
  (and was confirmed as a genuine null) ThermoMPNN-D's native,
  non-degenerate double-mutant interaction score, or the rank-degenerate
  additive ddG(v)+ddG(A222V) construction? If it was the degenerate
  version, the "confirmed genuine absence of stability-mediated
  signal" claim needs to be walked back, since a rank-degenerate
  statistic can't test interaction at all by construction.

---

## Group X — Turn the region-4 finding into a continuous, transferable claim

**Task X1 — Dose-response curve instead of a categorical region label**
- X1a. Using the same per-position data already computed for the
  alignment-depth discriminator, run a continuous regression (not a
  region-binned comparison) of per-position ESM-2 background-shift
  magnitude against per-column alignment depth (Neff), position-clustered
  inference, across the whole protein — and the same regression for
  ThermoMPNN's residual. Report the actual slope/curve for each,
  not just a region-level correlation. A monotone relationship for one
  model and a flat one for the other is a general, transferable claim in
  a way a region label cannot be.

**Task X2 — Is the depth effect separable from domain/region boundary confounds?**
- X2a. Check whether the atlas's own region boundaries and MTHFR's actual
  functional domain boundaries (catalytic vs regulatory) coincide exactly
  or diverge at any point. If they diverge, test whether the
  depth-tracking effect breaks at domain edges or at region edges
  specifically — this is the sharper, more diagnostic version of the
  region-4 finding and should be reported alongside the continuous curve
  from X1.

---

## Group Y — Strengthen the severity-baseline critique before it goes anywhere near a write-up

**Task Y1 — Does the severity baseline survive its own scrutiny?**
- Y1a. Test whether Site_Independent's own correlation with e.b (whatever
  S1's ledger confirms as its correct, verified value) survives its own
  sign-flip re-derivation null and the same multiplicity correction
  applied to everything else in this project. If the baseline's own
  correlation is itself mostly structural artifact, the critique's shape
  changes and this must be stated plainly.

**Task Y2 — Can the severity-baseline effect be derived, not just observed?**
- Y2a. Attempt an analytical or simulation-based demonstration that a
  monotone nonlinearity between severity and fitness mechanically
  generates a positive correlation between a severity-only predictor and
  measured epistasis, using this dataset's own real fitness distribution.
  If a clean analytical derivation isn't feasible in reasonable scope,
  a well-specified simulation is an acceptable substitute — state
  explicitly which was done.

**Task Y3 — Check Nambiar's released code, not just their paper text, for a severity-only control**
- Y3a. This project's own paper text search already confirmed zero
  mentions in the full paper (main + methods + supplementary). Check
  their released code repository (already cloned earlier in this
  project, `maslov-group/Epistasis`) for whether any severity-only
  baseline appears there even if undiscussed in the paper itself, before
  any future write-up asserts the control is "missing from" their work
  rather than merely "not discussed in their paper."

---

## Group Z — Bookkeeping, verification, and human-decision items

**Task Z1 — Was the numerical-precision check comprehensive?**
- Z1a. Confirm whether AC3's precision/hardware rescore covered only
  the original ESM-2 delta_esm, or also the five ESM-1v deltas used in
  the reliability analysis. If only the former, state this gap plainly.

**Task Z2 — Honest accounting of total analyses run, not just the pre-registered family**
- Z2a. Compile a count of every distinct statistical test run across this
  project's full history (not just the five-to-eight-member family used
  for the Holm-Bonferroni correction), to contextualize how much of a
  multiple-forking-paths risk exists beyond what the narrow correction
  addresses. Report the count plainly alongside the existing correction,
  without re-running the correction itself on this larger, informal
  count (which would need its own separate pre-registration to mean
  anything rigorous).

**Task Z3 — The ClinVar clinical number (queued once before, never run — this project's own oversight, not a technical block)**
- Z3a. Fetch ClinVar data for MTHFR (VUS and conflicting-interpretation
  variants), cross-reference against the atlas's canonical variant
  manifest, and compute how many would be scored meaningfully
  differently under background-aware vs. background-naive prediction,
  using a pre-registered, explicitly stated threshold for "meaningfully
  differently." Same fetch-budget discipline as every other fetch in
  this project.

**Task Z4 — Draft, do not send, an email to check the severity-baseline question directly with the authors**
- Z4a. Draft a short, respectful email to Nambiar et al. (or the
  appropriate corresponding author) asking directly whether a
  severity-only baseline control was run and simply not reported, or
  genuinely not considered. Save the draft; do NOT send it — sending
  outreach emails is the user's decision, not this session's.

**Task Z5 — NOT for this session**
- The process-transparency and personal-contribution disclosure question
  (item 119 in the source review) is explicitly for the user to handle
  personally, not an analysis task. Do not attempt it.

---

## Suggested execution order

1. **Group S first, always** — nothing else can be trusted or correctly
   interpreted until the sign/target ambiguity is resolved and the
   dropped threads are back on record.
2. **Group T and Group V next, in parallel if convenient** — these are
   the two highest-priority scientific questions, and V in particular
   has been open across three rounds and should not carry into a fourth.
3. **Group U, W, X, Y** — independent of each other, any order.
4. **Group Z** — bookkeeping and the ClinVar fetch, whenever convenient,
   including interleaved with the above.

If Group T concludes that ESM-2 is likely an outlier draw rather than a
representative one, or that ESM-2 and ESM-1v aren't comparable enough to
share a reliability estimate at all, put that at the very top of the
session's SUMMARY — it would mean the disattenuated −0.30 to −0.38
estimate needs to be dropped or heavily requalified in any future
write-up, which is more important than anything else in this document.
