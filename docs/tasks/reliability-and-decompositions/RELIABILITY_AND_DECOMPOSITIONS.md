# Reliability Reframing and Mechanistic Decompositions

Source: an external analysis that read Nambiar et al. 2025 end to end,
cloned their released code, and worked through this project's full log
history. Independently verified against the primary source before this
doc was written: the exact calibration equation (φ1(x) = −log(1 +
exp(−b1(x+c1))), confirmed word-for-word from the paper's own PDF text
layer) and every one of Supplementary Table 2's nine correlation values
(TEM-1 0.0918→0.1169→0.3748, YAP1 0.1770→0.2364→0.3444, RRM
0.1333→0.1508→0.2633 — all confirmed exact). The disattenuation
arithmetic was independently recomputed and matches. This analysis has
earned real trust — but Group V below still verifies the handful of
claims about THIS repo's own state that haven't been independently
checked yet, before anything downstream treats them as settled.

**The headline reframe this analysis offers, stated plainly up front:**
the project's small effect size may not mean "ESM-2 lacks the
information" — it may mean "a single checkpoint's background-sensitivity
signal has low test-retest reliability (~0.084–0.098 across two
independent measurements), which mechanically caps any achievable
correlation at roughly 0.29, and once disattenuated for that unreliability
the effect sits inside Nambiar's own calibrated range." This is a
genuinely different, more defensible, and more interesting claim than
either "the effect is real" or "the effect is noise" — it's a claim about
measurement precision, and it is checkable.

---

## Group V — Verify the repo-specific claims before trusting them downstream

**Task V1 — Confirm E3 (AB2a-FIX) is actually closed**
- V1a. Read the actual log entry for AB2a-FIX (not a summary of it).
  Confirm: the anchor swap to H354R, the gate `|diff| = 0.000e+00`, the
  692-second runtime, and that `task_AB2_proteingym_model_comparison.csv`
  exists on disk with 96 model rows. Quote the real entry verbatim. If
  any of these don't match, say so plainly — do not assume the external
  analysis's summary is correct without checking.

**Task V2 — Confirm the severity-baseline numbers**
- V2a. From `task_AB2_proteingym_model_comparison.csv` (once V1 confirms
  it exists), pull the actual correlation values for Site_Independent,
  ESM1v_single, GEMME, DeepSequence, EVmutation, ESM2_650M, and
  ESM2_150M against own_e_b. Confirm or correct the claimed values
  (+0.064, +0.068, +0.076, +0.076, +0.077, +0.085, +0.162 respectively).

**Task V3 — Confirm script 53 exists and what it actually does**
- V3a. `ls scripts/53*.py` and read it. Confirm it is a global-vs-specific
  epistasis control, as claimed, and confirm what its own logged result
  says. This is being cited as the project's existing differentiation
  from Nambiar's headline — verify it actually says what it's claimed to
  say before that framing goes anywhere.

**Task V4 — Confirm the AD5 RSA-per-position-constant fact**
- V4a. Re-read `[AD5]`'s own entry and confirm: is RSA genuinely a
  per-position constant (i.e., does every variant at a given position
  share the same RSA value)? This is load-bearing for Task B1 below — if
  it's wrong, the Mundlak decomposition's predicted answer changes.

---

## Group A — Reliability reframing (do this first; it's the cheapest, highest-value thing in this doc)

**Task A1 — The five-member ensemble-mean delta run (never computed)**
- A1a. Load all five ESM-1v members' saved score CSVs (confirm they
  still exist — see Group Q in the prior task doc if this hasn't been
  checked). Compute the simple mean of delta across the five members,
  per variant. No GPU, no model load — this is arithmetic on existing
  columns.
- A1b. Correlate this ensemble-mean delta against own_e_b, same
  conventions as every other headline number (position-cluster
  bootstrap, sign-flip null). Report the real result next to the
  Spearman-Brown-predicted value (~−0.030) — state plainly whether the
  prediction holds.

**Task A2 — Formalize the reliability/attenuation framing as a proper, gated result**
- A2a. Pre-register the disattenuation formula in a new script's
  docstring before computing anything: observed correlation divided by
  the square root of (delta's reliability × own_e_b's reliability),
  using AC4's cross-member delta agreement (0.084) and C3a's own_e_b
  reliability (0.6363) as the two reliability inputs — cite both sources
  by their exact log entries.
- A2b. Compute and report: the attenuation ceiling (√0.084 ≈ 0.29), the
  disattenuated anchor correcting only for delta's reliability (≈−0.303),
  and the fully disattenuated anchor correcting for both (≈−0.380).
  State explicitly, as a limitation printed alongside the number, that
  this borrows ESM-1v's cross-seed reliability as a proxy for ESM-2's
  own (unmeasurable, since no ESM-2 seed replicates exist — see A3
  below) — this is an assumption, not a measurement, and must be labeled
  as such every time this number is quoted.
- A2c. Report where ESM-2's actual −0.088 sits relative to the five
  ESM-1v members' own distribution (mean, sd, and the resulting z-score
  or SD-distance) as an additional, complementary piece of context.

**Task A3 — Correct scope: this is an ESM-1v-seed finding, not an ESM-2-seed finding**
- A3a. Write one clear paragraph, checked against what's actually
  knowable about Meta's release process: ESM-2 was released as one
  checkpoint per parameter size (no published seed replicates), while
  ESM-1v's five members are genuine seed replicates of one architecture.
  State plainly that AC4's finding is scoped to ESM-1v specifically, and
  that treating ESM-1v as a seed-proxy for ESM-2 is an assumption (used
  in A2's disattenuation), not an established fact. This corrects any
  prior framing that treated AC4 as directly testing "ESM-2's" seed
  stability.

**Task A4 — Run N3 and N4 from the prior calibration task doc (never executed)**
- A4a. Confirm from `CALIBRATION_LOG.md` that N1 and N2 have real log
  entries but N3 does not, and that N4 was never reached. If this
  matches, proceed; if the state is different, log what's actually true
  and adjust.
- A4b. Run N3 (the calibrated headline correlation on the held-out 80%)
  as originally specified. Before treating any result as final, check
  the algebraic prediction from this analysis: because Δφ = φ2 − φ1 is
  non-monotone and the severity term dominates the shift term in this
  construction, N3 is predicted to show near-zero correlation between
  delta_cal and delta_esm and to fail to recover a strong calibrated
  correlation. Report the actual result regardless of which way the
  prediction points — this is a real algebraic prediction worth testing
  explicitly, not assuming.
- A4c. Run N4 (calibration applied to the five ESM-1v members) WITH THE
  FOLLOWING TRAP EXPLICITLY GUARDED AGAINST, pre-registered before
  running: calibration adds a shared, seed-INDEPENDENT severity term
  (φ1's contribution) to every member's calibrated delta. This means
  cross-member agreement on delta_cal will rise for a purely mechanical
  reason — the members start agreeing more because they now share a
  common additive component, not because the underlying interaction
  signal became more stable. The valid test is cross-member agreement on
  the SHIFT component specifically (the φ2′(x)·d term, isolated from the
  Δφ(x) severity term), not on raw delta_cal. Pre-register this
  distinction in the script's docstring before running, and report BOTH
  quantities side by side so the mechanical-inflation trap is visible in
  the output, not hidden.

---

## Group B — Four mechanistic decompositions

**Task B1 — Mundlak decomposition of the ThermoMPNN/ESM-2 sign flip**
- B1a. On the existing 9,595-row matched frame, fit a Mundlak
  specification: regress own_e_b on (ddg − mean_ddg_by_position) [the
  within-position component] and mean_ddg_by_position [the
  between-position component] simultaneously, cluster-robust SEs by
  position. Report both coefficients, their CIs, and whether they differ
  from each other (a direct test, not just eyeballing two separate specs).
- B1b. Repeat the identical decomposition for ESM-2's delta_esm — the
  sign flip happens for both predictors, not just ThermoMPNN, so both
  need the same treatment.
- B1c. Run the full 2×2 (FE granularity: position vs. domain) × (control
  set: task-literal vs. script-24-literal) to separate which factor
  actually drives the flip, rather than the two original specs which
  varied both at once.
- B1d. If V4 confirmed RSA is a per-position constant, state explicitly
  that SPEC B's entire "structural" control is, by construction, a
  between-position quantity — this is the strong prior for where the
  flip lives, and B1a-c's results should be checked against it directly.

**Task B2 — Is the region-4 depth reversal composition or a real effect?**
- B2a. Using `task79_depth_positions.csv` (already on disk, no new
  compute): compute Spearman(Neff, conservation) pooled and separately
  within each of the four regions. If the Neff-conservation relationship
  itself differs in region 4 versus the other regions, that's evidence
  the reversal is a compositional artifact rather than a true region-4
  depth effect.
- B2b. Compute the partial correlation of yE (mean |delta_ESM|) against
  Neff, controlling for conservation, both pooled and specifically within
  region 4. Compare against the raw (non-partial) region-4 result already
  on record.
- B2c. Report Neff's range and distribution specifically within region 4
  (only 169 positions) — check whether range restriction, combined with
  a genuinely nonlinear underlying relationship, could produce a sign
  reversal in a small, range-restricted subset even if the true
  relationship doesn't actually reverse.

**Task B3 — Does AE3's clade signal survive proper controls, or is it generic heterogeneity?**
- B3a. Size-matched null: repeatedly draw 104 random sequences from the
  full 4,348-sequence V+A set (matching the real V-group's size exactly),
  recompute per-position JSD against the remaining sequences each time,
  and build a null distribution. Test whether the actual V-group's
  JSD-vs-|delta_esm| correlation exceeds this null — this directly
  addresses the known upward bias of JSD between unequal-sized groups,
  which is worse at high-entropy columns.
- B3b. Placebo test: identify several other alignment columns with a
  comparable minority-residue fraction to position 222's ~2% (not
  necessarily the same residue identity — comparable rarity is what
  matters for this control). Repeat AE3b's exact grouping-and-JSD
  procedure at those columns. If a similar-magnitude positive correlation
  with |delta_ESM| appears at arbitrary columns with comparable rarity,
  the finding is generic per-position distributional heterogeneity, not
  something specific to position 222 — reuse script 29's existing
  placebo-predictor convention for this, don't build a new one.
- B3c. State the honest verdict plainly: if B3a/B3b both hold up, the
  candidate explanation should be restated as "ESM-2's background-shift
  is larger at positions with more sequence heterogeneity in general,"
  not as anything specific to A222V's biology or clade structure.

**Task B4 — De-bias AD4's interaction term and re-test**
- B4a. AD4's ThermoMPNN-D interaction term has a large, mostly
  distance-independent offset (mean −1.319, far-pairs and near-pairs
  both cluster near this same value) — for genuinely non-contacting
  residue pairs, a real physical interaction should be close to zero, so
  this offset looks like a comparator-calibration artifact, not signal.
  Regress `interaction_D` on Cα distance to 222 (`ca_dist_222`, already
  in `task77_thermompnnD_doubles.csv`), take the residuals, and re-test
  the residualized interaction term against own_e_b with the same
  conventions as AD4's original test.
- B4b. State the verdict plainly: if the de-biased residual still shows
  no relationship with own_e_b, AD4's null is confirmed as real, not an
  artifact of the offset. If a real relationship emerges after
  de-biasing, AD4's original null needs to be restated as a
  comparator-calibration failure, not a genuine absence of signal.
- B4c. Report the actual proportion of the 9,595-row frame that sits
  beyond 10 Å from position 222 (claimed: 9,232/9,595, ~96%) and state
  this plainly as a standalone fact: MTHFR/A222V is overwhelmingly a
  long-range system. Connect this explicitly to Nambiar's own Section
  2.4 finding (raw, uncalibrated PLM epistasis tracks structural contact
  proximity; only their calibrated epistasis reveals long-range
  functional coupling) — if true, this is a real, unifying explanation
  tying B1/B2/B4/A2 together: this project's comparators (both ESM-2's
  raw scores and ThermoMPNN's stability term) may be instruments better
  suited to short-range structural coupling than to the long-range
  regime MTHFR/A222V actually sits in.

---

## Group C — Bookkeeping and closure items

**Task C1 — Finalize the precise-statistic definition with correct attribution**
- C1a. Confirm and finalize: `delta_esm = esm2_score_a222v_bg -
  esm2_score` (defined in scripts 12 and 45, not 32/33 — those scripts
  consume the already-defined columns, they don't define them). Confirm
  `own_e_b`'s construction in `lib/own_context.py`: a per-variant WLS fit
  with weights 1/se², and e_b as the deviation of the A222V-arm fit from
  a MULTIPLICATIVE expectation built from the WT-arm fit — this is why
  f_bar_wt is a construction covariate, not an independent predictor.
  Write the final, corrected version of the precise-statistic paragraph
  with this attribution fixed.

**Task C2 — Run the multiplicity correction with a narrowly pre-registered family**
- C2a. Define the family BEFORE computing anything (an unbounded family
  makes any correction close to meaningless in either direction):
  pre-registered headline tests only. A reasonable starting family, to
  be finalized and stated explicitly in the script's docstring:
  AD1 (sign audit), AD6 pooled depth result, AD6's conservation
  dissociation, AB2a's severity-baseline gate, and the core −0.088
  anchor itself. Note explicitly that AE3b (p=0.012), AD6 region-3
  (p=0.0194), and AD5's SPEC A delta_esm result (p=0.023) sit close to
  the boundary and are worth flagging as "at real risk" under
  correction, even if not part of the core pre-registered family.
- C2b. Apply Holm-Bonferroni (the same method already cited in the COPD
  project) across the defined family. Report which survive at
  family-wise α = 0.05 and which do not.

**Task C3 — Deprecate the five old cell-level-null scripts**
- C3a. Add a DEPRECATED header to scripts 21, 24, 26, and 28 (and note
  script 26's row-level shuffle specifically), matching the exact
  convention already used for script 35's deprecation header. Ten
  minutes, closes this permanently — no re-run needed.

**Task C4 — Do NOT attempt SaProt's sign audit yet**
- C4a. Confirm this is still correctly blocked behind Z3g-h/E4 (no
  SaProt correlation exists yet to protect). If Z3g-h has since
  resolved, note that the 123 buried hydrophobic→charged substitutions
  already used for ThermoMPNN's AD1 audit are a ready-made labeled
  positive-control set for SaProt too, and this can be run using the
  same four-layer recipe once unblocked — but do not attempt it in this
  session unless Z3g-h has genuinely resolved.

---

## Group F — Repo hygiene

**Task F1 — Retire the stray duplicate-numbered scripts**
- F1a. Move (do not delete) `scripts/32_delta_esm_noise_floor.py`,
  `33_measurement_noise_control.py`, `34_established_predictor_comparison.py`,
  `36_matched_baseline_crosspredictor.py`, `37_reframe_writeup_section.py`,
  `38_exogenous_anchor_test.py`, `39_range_restriction_correction.py`, and
  `40_final_reframe.py` into a new `scripts/_retired/` directory. This
  preserves provenance while permanently eliminating the number
  collision with the real, canonical scripts of the same numbers. One
  commit.

---

## Suggested execution order

1. **Group V first, always.** Nothing in Groups A–C should be trusted or
   built upon until the specific repo-state claims it depends on are
   independently confirmed.
2. **Group A next** — the ensemble-mean run (A1) is the single cheapest,
   highest-value action in this entire document. A2's disattenuation
   framing and A3's scope correction should follow immediately after,
   since they depend on A1's real numbers. A4 (running N3/N4) is
   important but can proceed in parallel with Group B if convenient.
3. **Group B** — all four decompositions run on existing CSVs, no GPU,
   independent of each other, can run in any order or in parallel.
4. **Group C and Group F** — cheap bookkeeping, do whenever convenient,
   including interleaved with Groups A/B.

Nothing in this entire document requires a GPU or a new model load. Every
task either verifies an existing claim or computes something from data
already on disk. This should be a fast session relative to prior ones.
