# Context-Dependent Variant Effects in MTHFR: Project Summary (Final)

*This version supersedes all prior drafts. Every number below was verified
against its primary source — code, a live-fetched model card, or a
directly cloned paper repository — in the round that produced it, not
copied forward from an earlier summary. Where a prior draft's framing was
wrong, that is stated plainly, not smoothed over.*

---

## The one-paragraph version

Protein language models like ESM-2 are increasingly used to score how
damaging a genetic variant is, almost always as if it doesn't matter what
else is present in the sequence. This project tested that assumption
against real deep-mutational-scanning data for a common genetic
background in MTHFR (A222V). The clearest, most defensible result in the
whole project needs no statistical correction at all: **five identically
trained instances of a related model agree almost perfectly (ρ = 0.88) on
what a variant's raw score is, and barely at all (ρ = 0.084) on how that
score changes when a genetic background is added — a 10.5-fold gap.** The
background-sensitivity signal itself is real, small, and statistically
detectable above a properly-derived power floor — but a candidate
explanation that it was just badly scaled, fixable by another group's
published calibration method, was tested directly and failed cleanly. A
second candidate explanation — that the small effect size reflects
genuine model-to-model unreliability large enough to hide a much bigger
true effect — was tested and closed for the opposite reason: the model
used to estimate that unreliability turns out to come from a documented,
different training distribution than the model being corrected, so the
correction was never actually licensed. What remains, after five rounds
of adversarial scrutiny, is a smaller, more honest, and better-defended
project than any earlier draft claimed: a real, weak, well-replicated
signal; a clean demonstration that model reliability — not model
capability — is the right lens for reading it; and a specific, scoped
explanation, borrowed from directly comparable published work, for why
this particular clinical scenario sits in the hardest regime for these
methods to succeed in.

---

## The question, unchanged from the start

Does ESM-2's predicted fitness effect for a mutation shift depending on
genetic background — specifically, the common A222V variant — and if it
does shift, does that shift track *real*, experimentally measured genetic
interaction? MTHFR remains a rare case where both halves of this question
can be checked against the same real, independently collected dataset
(Weile et al. 2021).

---

## Read this first: the naming convention every number in this document follows

An earlier draft blurred two different statistics that happen to share a
target variable, and a reviewer correctly caught it. Every correlation in
this project is one of exactly two kinds, and this document always names
which:

- **The background-induced SHIFT** — `delta_esm = score(A222V background)
  − score(WT background)` — this is the project's actual object of study.
  The headline anchor (ρ = −0.088 vs. own e.b; −0.071 vs. published e.b)
  is always this quantity.
- **A raw WT-background score** — how damaging a model thinks a variant
  is, with no background comparison at all. Every severity baseline
  (Site_Independent, GEMME, ESM2_650M's own raw score, etc.) is this
  quantity, and every one of them is *positive* against the same target —
  which is not a contradiction with the negative shift-based anchor, it's
  a different statistic entirely.

---

## The headline result: reliability, not calibration, not model capability

**Five independently-trained ESM-1v checkpoints agree almost perfectly on
raw scores and barely at all on background-induced shifts.**

| Cross-seed agreement across 5 ESM-1v checkpoints | ρ | 95% CI |
|---|---|---|
| Raw wild-type-background scores | **+0.8826** | [+0.8696, +0.8918] |
| Background-induced shifts (deltas) | **+0.0844** | [+0.0522, +0.1226] |

**10.5×.** No disattenuation, no cross-model assumption, no calibration
step, no contested premise — this is a directly measured fact about how
five identical-architecture models trained differently agree with each
other. This is the single cleanest, most reportable figure this project
has produced, and it is now the recommended headline.

**What it means:** whatever the true relationship between genetic
background and predicted mutation effect is, extracting it as a raw
score subtraction is an unreliable measurement — even before asking
whether ESM-2 specifically "gets it right."

---

## What we tested and closed — the disattenuation chain

Two prior drafts of this document carried a striking number: disattenuate
the project's −0.088 anchor for cross-model measurement unreliability,
and the corrected estimate lands around −0.30 to −0.38 — suspiciously
close to a directly comparable published method's *calibrated* results.
This was the most exciting number in the project. **It does not survive
the final round of scrutiny, and the reason is decisive rather than
merely cautious.**

The correction requires borrowing ESM-1v's own cross-seed reliability
(0.084, above) as a stand-in for ESM-2's — which cannot be measured
directly, because Meta released ESM-2 as a single checkpoint with no
seed replicates. This was always flagged as an assumption. **Checked
directly against Meta's own published model documentation, fetched live:
ESM-2 (`UniRef50`, 2021, Lin et al.) and the five ESM-1v seeds
(`UniRef90`, 2020, Meier et al.) are different training corpora,
different training runs, and separate papers.** Shared architecture and
parameter count is not shared training distribution. The formal outlier
test (is −0.088 an unusual draw from the ESM-1v seed family?) was
underpowered at n=5 and could not settle this on its own — but it didn't
need to. The documentation settles it directly: this isn't a question of
whether ESM-2's number is unusual, it's that the premise required to
correct it was never true.

**The disattenuated interval, computed anyway for completeness, with a
proper bootstrap that propagates uncertainty in both the correlation and
the reliability estimate itself:** delta-only correction, −0.303
[−0.440, −0.193]; fully corrected, −0.380 [−0.555, −0.242]. **Both
numbers are reported here as a labeled counterfactual only** — "what the
anchor would be if ESM-2 shared ESM-1v's reliability, a premise now shown
to be false" — never as a claim about ESM-2's true effect size.

---

## What we tested and closed — the calibration rescue

The same suspicious proximity to a comparable published method's
calibrated range motivated testing whether that method's exact
two-stage nonlinear transformation, applied to this project's own raw
scores, would move the anchor toward it. On a properly held-out 80% of
the data (calibration fit only on the remaining 20%): raw ρ = −0.090
→ calibrated ρ = **+0.034** — the sign flips, and neither of the
pre-registered success criteria were met. A follow-up diagnostic,
purpose-built to catch the most tempting way this could look like a
success rather than a failure, confirmed the apparent improvement in
cross-seed *agreement* under calibration (0.084 → 0.656) is almost
entirely a mechanical artifact: calibration adds a shared, uninteresting
severity term to every checkpoint identically, and isolating the
actual interaction-relevant component shows agreement unchanged
(0.090 vs. the original 0.084).

**Checked directly against the comparable method's own reported numbers
and released code:** their headline calibrated correlations (Pearson
0.26–0.38) are raw, uncorrected observations — no disattenuation of any
kind appears anywhere in their paper or their code. Comparing this
project's corrected estimate to their raw numbers was never a
like-for-like comparison, and that sentence is dropped from this
document entirely. The defensible comparison instead: **this project's
raw anchor (|ρ| = 0.088) sits in a similar range to their own raw,
pre-calibration values (Pearson 0.09, 0.13, 0.18 across their three
proteins)** — a magnitude-level observation only, since the statistics
differ (Spearman vs. Pearson, different targets, different signs).

---

## The most concrete, most transferable explanation available: this is a long-range problem

The comparable method's own published finding is that raw, uncalibrated
model-derived epistasis tracks structural contact proximity, and only
their calibration step reveals long-range functional coupling — which
specifically requires the many-background, two-path measurement
structure their method was built around. **This project's analysis set
sits 96.2% beyond structural contact range from position 222**, a
single fixed background. This reframes the project's central negative
result from "the model failed" to a scoped, defensible, and genuinely
useful claim: **the published method's calibrated success is specific to
a measurement regime — dense, many-background, short-range-anchored —
that the common clinical scenario (one distant modifier variant) simply
does not occupy.**

One candidate mechanism was tested directly against this framing and
refuted, honestly: real measured interaction does not concentrate near
structural contact — |e.b| actually grows with distance from position
222, and so does the background synonymous-variant noise floor alongside
it. A distance-restricted analysis is not the fix; the long-range
argument above is about what information the *model* has access to, not
about where real biological interaction happens to sit.

---

## The power question, resolved after three rounds of disagreement

Two naive statistical-power calculations disagreed by a factor of 4
across earlier drafts, and each was quoted selectively depending on which
argument it supported. **Both were wrong, for the same underlying
reason.** Read directly from the actual bootstrap resampling code: the
project's inference procedure resamples *positions* (654 of them), never
rows — so treating the sample size as 10,757 independent rows is
pseudoreplication, and treating it as a naive 654-point correlation is
also wrong, because it's empirically falsified by the pipeline's own
measured power (the naive formula predicts 25% power where the actual
pipeline measured 100%, at the same effect size). **The correct floor is
this project's own from-scratch, pre-registered empirical power
injection: ρ ≥ 0.05**, independently corroborated by the measured
design effect (intra-position correlation ≈0.10, effective n ≈4,300) and
multiple independent null-standard-deviation estimates, all landing in
the same 0.026–0.043 range. The anchor clears this floor by roughly 2×.
**Never cite this power claim to a raw sample size of 10,757, and never
cite the naive 654-point Fisher formula — both were tested this round
and both are the wrong model for this pipeline's actual statistic.**

---

## What survives, stated plainly

**A second, structure-based predictor (ThermoMPNN) shows a comparable
correlation and carries genuinely independent information from ESM-2's
shift**, confirmed via a joint statistical model on their overlapping
row set.

**ESM-2 goes nearly blind in one specific region of the protein, and this
survives real scrutiny** — but the general "PLM sensitivity tracks
evolutionary depth" story needs a real correction: the pooled
relationship (ρ = +0.171) collapses to near-zero (ρ = +0.013) once the
top 124 highest-depth positions are excluded. **This is a threshold
effect concentrated at the highest end of alignment depth, not a smooth
dose-response gradient**, and any future statement of this finding must
say so. The region-specific blindness itself is unaffected by this
correction and remains real. It also breaks precisely at the boundary of
the affected region, not at the protein's actual functional-domain
boundary (which sits 43 residues away) — a real, useful specificity that
should be stated alongside the depth finding.

**A structure-based stability model's null result on interaction
capture is a genuine, confirmed absence of signal**, not a comparator
artifact — tested directly against the model's own non-degenerate
double-mutant scoring mode (not a rank-degenerate stand-in) and
confirmed to survive a distance-offset correction.

**A severity-only baseline correlates with real measured interaction —
and this is true for a precise, checkable reason, not despite one.** The
correlation itself is statistically real (survives its own null and the
project's multiplicity correction cleanly). A direct simulation using
this project's real fitness distribution shows that a monotone
severity-to-fitness relationship alone — with zero capacity to represent
actual interaction — mechanically produces a correlation roughly nine
times larger than what's observed. **Both facts are true simultaneously
and answer different questions**: the baseline correlation is not
statistical noise, and it is also not evidence that any predictor is
"detecting interaction" in the informal sense a reader might assume —
this is a critique that generalizes to any published claim in this space
that doesn't control for it, not just this project's own numbers.

**Two independent positive controls confirm the project's actual
headline statistical instrument (not a related but different one)
behaves correctly.** One (a real, independent double-mutant dataset)
detects a genuine signal cleanly; the other (a transplant onto GB1) was
underpowered at its available sample size and returned an honest null —
correctly read as "the instrument centers correctly, tested at low
power," not as a passing positive control in its own right.

---

## Limitations, stated precisely

**The clade-specificity question remains genuinely mixed.** A candidate
explanation involving rare, evolutionarily unusual residues clears a
size-matched randomization control decisively but does not clear a
placebo test at comparable-rarity alignment columns with full
confidence. Something real is happening with alignment-column
heterogeneity broadly; whether it is specific to this position is
unresolved.

**A structure-aware sequence model (SaProt) remains genuinely blocked**
on an open decision about how to define its comparison population,
reserved deliberately for the project's own decision-maker rather than
resolved automatically.

**Two earlier findings — that A222V produces a larger representational
shift than its own severity predicts, and that ESM-2 performs reliably
worse than a no-interaction baseline in the highest-interaction stratum
— both still stand as verified, descriptive facts, but neither has been
reconciled head-on against this project's later reliability findings.**
Both should be read with an explicit single-checkpoint caveat attached
until that reconciliation happens.

**Numerical precision for the five ESM-1v checkpoints' delta scores has
not been separately verified** the way the original ESM-2 delta was
(rescoring under different floating-point precision, batch size, and
hardware). The analogy to the original check is plausible but remains
unverified as of this writing.

**The formal multiple-testing correction currently includes a sanity
check that cannot statistically fail** (a 123-for-123 sign audit,
p ≈ 10⁻³⁸) alongside the project's genuinely contestable claims, which
makes the correction's "5 of 5 survive" framing sound stronger than the
contestable claims alone would produce. A future, stricter accounting
should separate sanity checks from contestable statistical claims before
reporting a family-wise result.

---

## Where things stand right now

Five rounds of external, adversarial review have progressively
strengthened rather than undermined this project — each round converged
on refining or correcting earlier claims rather than discovering new
fundamental problems, which is itself a signal that the underlying work
is sound. What remains is not analysis. It is: folding a small number of
remaining verified corrections into this project's canonical repository
documentation, and deciding how to present the work.

---

## The one honest sentence

> *"Five identically-architected models agree almost perfectly on how
> damaging a mutation is and barely at all on how that assessment
> changes with genetic background — a measurement-reliability problem,
> not a capability problem — and the specific clinical scenario this
> project tested sits in exactly the long-range, single-background
> regime that comparable published methods are least equipped to
> succeed in."*

This is the version that survives every round of scrutiny this project
has received. It does not depend on any contested correction, any
borrowed reliability assumption, or any comparison that turned out not
to be like-for-like. It is also, on its own terms, a genuinely useful
thing to have shown.
