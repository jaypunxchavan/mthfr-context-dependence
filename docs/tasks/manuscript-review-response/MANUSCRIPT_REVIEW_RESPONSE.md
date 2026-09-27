# Manuscript Review Response — Critical Fixes and New Analysis

Source: a full manuscript-level review of `PROJECT_SUMMARY_FINAL.md` and
`MTHFR_RESEARCH_PAPER_SUMMARY.md`. This review found one critical error
that must be fixed before anything else, several major issues requiring
new (not previously computed) analysis, and a set of verification and
packaging items. Given the stakes, every statistically delicate task
below states its exact formula and gates in full — do not substitute an
approximate or remembered version of any formula given here.

---

## Group A — CRITICAL: the ThermoMPNN interaction claim (fix this first, before anything else)

**The error.** Both write-up documents state that ESM-2 and ThermoMPNN
"carry genuinely independent information from each other," based on a
joint semipartial decomposition of `pred_eb = ddG(v) + ddG(A222V))`
against `delta_esm`. This is wrong. `ddG(A222V)` is a single constant
added to every row (`scripts/68`'s pre-registered "ADDITIVE" choice), so
`pred_eb` is rank-identical to raw single-mutant `ddG(v)` alone — this
was already disclosed explicitly in `[V4]`'s own entry and in
`scripts/81`'s gate G4. The −0.0733 correlation is a
**stability-severity** correlation, not an interaction correlation, and
the "8.8% shared variance, both independent" framing is invalid because
one side of that decomposition is a severity score wearing an interaction
term's name.

**Task A1 — Confirm the rank-degeneracy one more time, cleanly, for the record**
- A1a. Re-derive, from the actual `pred_eb` and `ddg` columns already on
  disk, that `pred_eb` and `ddg` are rank-identical (Spearman = 1.0 to
  numerical precision, or state the exact deviation if any exists).
  Quote the exact gate output from `scripts/81` G4 verbatim alongside
  this fresh confirmation.

**Task A2 — Rerun the joint decomposition using a genuinely non-degenerate structural comparator**
- A2a. Repeat the joint semipartial decomposition (same closed-form
  two-predictor R² method, same position-cluster bootstrap convention as
  the original `scripts/81`) using ThermoMPNN-D's native, non-degenerate
  double-mutant `interaction_D` term in place of `pred_eb`. Report the
  full result: zero-order correlations, R²_full, unique/shared variance
  components, with CIs.
- A2b. State the honest verdict plainly. Given `interaction_D`'s own
  prior result was a clean null (ρ = +0.0154, CI spanning zero), the
  expected outcome is that ThermoMPNN-D contributes little or no unique
  variance in the joint model — report whatever the actual numbers show,
  do not adjust the framing to make the comparison sound more
  informative than it is.

**Task A3 — Reframe ThermoMPNN's raw ddG correctly as a severity baseline**
- A3a. Produce one clean, quote-ready paragraph and table row placing
  ThermoMPNN's raw `ddg(v)` correlation with e.b (ρ = −0.0733) alongside
  the existing severity-baseline table (Site_Independent, GEMME, etc.) —
  as a severity predictor, not an interaction comparator. State plainly
  that this reclassification is a correction of an error in the prior
  write-up, not a new finding.

---

## Group B — Surface two already-computed results that were dropped from Results (no new computation)

**Task B1 — Compile clean, source-cited blocks for both omitted results**
- B1a. The 150M-vs-650M delta-agreement result (ρ = +0.0978, CI
  [−0.0444, +0.2275], p = 0.154, 53.1% sign agreement, n = 1,900 rows /
  100 positions) — pull the exact source lines and assemble one
  citation-ready paragraph stating plainly that this is a
  non-replication of the shift statistic across model scale, with a
  sign agreement indistinguishable from chance.
- B1b. The five-seed ensemble-mean result (ρ = −0.0285, CI, p = 0.048)
  — pull the exact source lines and assemble one citation-ready
  paragraph, explicitly carrying forward the existing "marginal, must
  not be quoted as a strong result" caveat from its own log entry.

---

## Group C — New analysis: a mechanism-only null for the shift statistic itself

This is a genuinely new analysis, not a write-up fix. The existing Y2
simulation (script 101) shows what a *severity-only* predictor with zero
interaction capacity mechanically produces against measured e.b
(ρ ≈ +0.590). No equivalent reference point exists for what the
*shift* statistic (delta_ESM) would mechanically produce under an
identical no-interaction generative mechanism — which is the number
actually needed to interpret whether −0.088 is large or small relative
to what pure severity-scale structure alone would produce for a shift
statistic specifically.

**Task C1 — Build the shift-side mechanism-only null**
- C1a. Read script 101 (Y2) in full before writing anything new. Reuse
  its exact generative approach: the real MTHFR fitness distribution
  (`f_bar`), a monotone severity-to-fitness relationship, and no
  interaction term of any kind.
- C1b. Extend this to the two-background case: simulate `f(v | WT)` and
  `f(v | A222V)` as two independent draws from the identical
  severity-driven generative model (same monotone map, same noise
  structure as Y2's single-background version) — critically, with NO
  interaction term connecting them, so any correlation between the
  resulting simulated shift and simulated e.b-analog is purely a
  mechanical artifact of the measurement construction, not a planted
  effect.
- C1c. From these simulated values, construct a simulated shift
  (`f(v|A222V) − f(v|WT)`, mirroring `delta_esm`'s definition exactly)
  and a simulated e.b-analog using the SAME weighted-least-squares
  `own_context.py` construction used for the real own_e.b, then compute
  their Spearman correlation using the project's standard position-
  cluster bootstrap convention.
- C1d. Report the resulting |ρ| this mechanism alone produces, with a
  CI, directly alongside the real observed −0.088. State plainly
  whether −0.088 is large, comparable to, or small relative to this
  mechanical reference point — this is the missing piece needed to
  interpret the anchor honestly, the same way Y2 already does for the
  severity baseline.
- C1e. Pre-register this entire construction in the new script's
  docstring before running anything, per standing project convention.

---

## Group D — New analysis: the classical difference-score reliability prediction (specify and verify carefully)

**Background, stated precisely so the correct formula is used.** For a
difference score D = X − Y, where X and Y each have their own
reliability (r_XX, r_YY — here, cross-checkpoint agreement) and are
correlated with each other at r_XY, classical test theory (Lord 1956)
gives:

```
reliability(D) = [r_XX·Var(X) + r_YY·Var(Y) − 2·r_XY·sqrt(Var(X)·Var(Y))]
                 ------------------------------------------------------
                 [Var(X) + Var(Y) − 2·r_XY·sqrt(Var(X)·Var(Y))]
```

This follows directly from decomposing X = Tx + Ex, Y = Ty + Ey under the
classical assumption that measurement errors are uncorrelated with true
scores and with each other, then taking Var(true difference) /
Var(observed difference). **Do not use a simplified version that assumes
Var(X) = Var(Y) unless that assumption is verified against the real data
first** — an incorrect simplification here would produce a wrong number
confidently.

**Task D1 — Define every input quantity precisely, from one consistent source**
- D1a. All five quantities below must be computed from the SAME
  underlying per-checkpoint raw score data (the five ESM-1v checkpoints'
  saved score CSVs), not mixed from different prior contexts:
  - X = each checkpoint's raw wild-type-background score.
  - Y = each checkpoint's raw A222V-background score.
  - r_XX = cross-checkpoint agreement on X (median of the 10 pairwise
    Spearman correlations across the five checkpoints — this should
    reproduce the existing 0.8826 figure; treat that reproduction as a
    gate, not an assumption).
  - r_YY = cross-checkpoint agreement on Y, computed by the identical
    procedure. **This has likely never been isolated separately before
    (only the WT-background version was previously reported) — compute
    it fresh.**
  - r_XY = the correlation between X and Y. Compute this SEPARATELY for
    each of the five checkpoints (each checkpoint's own within-model
    Spearman(X, Y)), then report the range and the median across
    checkpoints — do not simply reuse the previously-cited 0.999636
    without re-deriving it in this exact construction, since that
    number's precise provenance (which checkpoint, which exact row set)
    needs to be re-confirmed for internal consistency with X and Y as
    defined here.
  - Var(X), Var(Y): compute per-checkpoint, then report both the
    per-checkpoint values and their average. State explicitly whether
    Var(X) ≈ Var(Y) or whether they differ meaningfully — this directly
    determines whether a simplified formula would have been valid.

**Task D2 — Compute the formula, with gates, and report the raw result honestly**
- D2a. Implement the exact formula above (not a simplified version).
  Gate: verify the identity Var(D) [computed directly from the real
  simulated-or-real D = Y − X data] equals Var(X) + Var(Y) − 2·r_XY·
  sqrt(Var(X)·Var(Y)) to numerical precision, as an internal consistency
  check before trusting the reliability formula's denominator.
- D2b. Compute the point prediction. **If the result falls outside
  [0, 1], or is negative, report this exactly as computed — do not
  adjust, clip, or silently treat it as an error.** A result outside the
  normal range here is likely itself informative: it would indicate the
  formula is numerically ill-conditioned specifically because r_XY is
  very close to 1 (the denominator collapses toward zero, and the
  prediction becomes extremely sensitive to small imprecision in the
  input correlations) — which is itself a meaningful, reportable
  finding about *why* difference scores built from two near-identical,
  imperfectly-reliable quantities are fragile, not a computational
  mistake to be hidden.
- D2c. As a robustness companion, also compute this via a full
  position-cluster bootstrap: resample positions, recompute r_XX, r_YY,
  r_XY, Var(X), Var(Y), and the resulting predicted reliability fresh
  within every draw, and report the empirical distribution of the
  predicted reliability (not just a single point estimate) — this
  reveals whether the point prediction is itself wildly unstable across
  resamples, which is directly relevant to whether it's fair to quote a
  single predicted number at all.
- D2d. Compare the formula's prediction (with its own uncertainty, from
  D2c) against the actually observed delta reliability (0.0844). State
  plainly whether the classical formula's prediction is consistent with
  the observed value, and report both numbers together — this is the
  citable psychometric-framing result the review specifically asked for.

---

## Group E — Precision fixes for the Nambiar characterization and the long-range distance claim

**Task E1 — Restate Nambiar et al.'s finding precisely**
- E1a. Write a corrected paragraph stating precisely what their paper
  shows: a QUALITATIVE comparison (visual heatmap pattern matching to
  structural contact maps, plus a top-20-pairs circular interaction-graph
  analysis) across three proteins (TEM-1, YAP1, Pab1 RRM2), showing raw
  epistasis resembling contact maps and calibrated epistasis
  reorganizing around functional/catalytic hubs described as "long-range
  functional couplings." Explicitly state this is NOT a quantitative
  distance-stratified accuracy table — no such analysis exists in their
  paper.
- E1b. Separately and explicitly label this project's own claim — that
  their calibration's benefit "structurally requires" a many-background,
  two-path measurement design a single fixed background cannot supply —
  as this project's own hypothesis extending their finding, not
  something they state or test themselves.

**Task E2 — Recompute the long-range distance figure on the biological dimer**
- E2a. MTHFR is an obligate homodimer; the existing 96.22%
  beyond-contact-distance figure was computed on chain A alone (a
  catalytic-domain monomer construct, missing 59 atlas positions). Reuse
  the already-scored dimer coordinates from the AD7 dimer-scoring session
  (`task80_dimer_variants.csv` / `task80_dimer_positions.csv`) rather
  than rescoring from scratch.
- E2b. For each variant position, compute the minimum Cα–Cα distance to
  EITHER copy of residue 222 across both chains (accounting for the
  dimer's two-fold symmetry — a variant could plausibly sit close to
  position 222 through the opposite subunit even if far from it within
  its own chain). Report the resulting long-range percentage under this
  dimer-aware definition, directly alongside the original monomer-only
  96.22% figure.
- E2c. Report the exact count of atlas positions with no coordinates at
  all under each definition (monomer vs. dimer), since these may differ.

---

## Group F — Multiplicity correction: resolve the α discrepancy and state the honest test count

**Task F1 — Resolve the α = 0.01 vs. α = 0.05 discrepancy**
- F1a. Read `RESULTS.md`'s multiplicity-correction line and
  `scripts/97`'s actual implementation directly. Determine which is
  correct (what α the script actually used, versus what the write-up
  claims). Fix `scripts/97` or its own log entry if the discrepancy is
  there. **Do NOT hand-edit `RESULTS.md` again without new, explicit
  authorization from the user** — the prior closeout session's edit was
  explicitly stated as "the second and final authorized hand-edit."
  If `RESULTS.md` itself is the file that needs correcting, flag this
  plainly as an open item requiring the user's explicit go-ahead, do not
  edit it automatically.

**Task F2 — State the honest total test count**
- F2a. Re-read `OVERNIGHT_LOG.md`'s own estimate ("on the order of
  100–200 individually reported inferential numbers across 61 scripts,"
  "no formal project-wide multiplicity correction has been claimed
  anywhere") and confirm this citation is accurate by quoting the exact
  line. Produce one clean, honest paragraph for the write-up's
  limitations section stating this count plainly, and stating that the
  five-to-eight-member Holm correction addresses only a narrow,
  pre-registered confirmatory family, not the project's full set of
  computed inferential quantities.

---

## Group G — Positive-control precision, and two citation checks

**Task G1 — Build the estimator-differences table**
- G1a. Produce a small, clear table comparing the MTHFR primary
  estimator against the GB1 transplant and the GRB2 transplant on:
  weighting scheme (4-condition WLS with measured SEs vs. uniform
  weights), wild-type anchor (measured vs. `c-hat` median-ratio proxy
  where no zero-mutation row exists), sign-flip granularity, whether the
  absolute-arm null is degenerate under single-cell flips, and the
  approximate sequence-distance regime of the assayed variant pairs
  (local/dense for GRB2 vs. long-range/single-background for MTHFR).
  State plainly, using this table, that the controls establish correct
  null-centering and (for GRB2) genuine detection capability in a
  short-range, multi-partner regime — and that no control in this
  project establishes detection validity specifically for a single,
  distant, fixed background, which is a limitation of the design.

**Task G2 — Verify the GRB2 citation year**
- G2a. Check ProteinGym's own metadata for the `GRB2_HUMAN_Faure`
  dataset directly (not from memory or a prior log's possibly-
  inconsistent citation) and report the correct publication year.

**Task G3 — Verify and properly frame the region-boundary provenance**
- G3a. Locate the exact existing provenance record for the mutagenesis
  region boundaries (`lib/regions.py`'s documented chain of
  communication) and draft correct acknowledgment text citing it as a
  personal communication. Note explicitly that using this in any public
  write-up requires the original source's permission, which has not
  been confirmed — flag this as needing the user's follow-up, do not
  assume permission.

---

## Group H — Reproducibility packaging

**Task H1 — Commit the essential derived tables needed to verify the headline results**
- H1a. Add a narrow, explicit exception to `.gitignore` (same pattern
  already used for the `data/external/` fix earlier in this project) for
  specifically: the primary ~10,757-row analysis frame (delta_esm,
  own_e_b, esm2_score, position, region columns), the five ESM-1v member
  score CSVs, the ProteinGym comparison table, and the ThermoMPNN output
  table. Do not un-gitignore the full `data/processed/` directory — scope
  this narrowly to the files that actually back the headline claims.

**Task H2 — Fix requirements.txt**
- H2a. Uncomment `torch` and `fair-esm`; add `transformers` and
  `huggingface_hub`, all with version numbers pinned to what is actually
  installed in the working `venv` (check directly with `pip freeze`, do
  not guess versions).

**Task H3 — Draft a LICENSE recommendation (do not choose unilaterally)**
- H3a. Draft a short recommendation (a permissive license such as MIT is
  a reasonable default for a student research repository) but do not add
  the file — this is the user's decision to make, flag it as open.

**Task H4 — Add a minimal run-all path for the headline results specifically**
- H4a. Write a short script or README section listing, in order, the
  handful of scripts that reproduce the project's actual headline claims
  (not an exhaustive run-all for all 100+ scripts) — scope this to what
  a reader would need to verify the results reported in the manuscript.

**Task H5 — Compile external-data provenance into one place**
- H5a. Pull the existing provenance records (source URL, fetch date,
  checksum where logged) for every external dataset already fetched
  during this project (GB1, GRB2, ProteinGym, ThermoMPNN weights,
  SaProt) from wherever they currently live scattered across various log
  files, and compile them into one new, clean `PROVENANCE.md`.

**Task H6 — NOT for this session**
- Archival DOI registration (e.g., via Zenodo) requires the user's own
  GitHub and Zenodo account linkage and cannot be done by this session.
  Flag it as a human action item in the final log, do not attempt it.

---

## Suggested execution order

1. **Group A first, unconditionally** — this is the critical correctness
   fix and nothing else in the write-up should be trusted until it's
   done.
2. **Group D next** — the most statistically delicate task in this doc;
   do it early, while attention is freshest, and follow every gate
   specified above exactly.
3. **Group C** — the other genuinely new analysis; independent of D, can
   run in parallel.
4. **Groups B, E, F, G** — verification and precision fixes, independent
   of each other, any order.
5. **Group H** — packaging, do last, since it's least time-sensitive and
   partly blocked on open questions (LICENSE choice, α reconciliation)
   flagged elsewhere in this doc.

Every task in this document either corrects a specific, named error or
computes something genuinely new and previously absent. Nothing here
should be treated as already resolved by any prior session — this
review is responding to what the write-up currently says, not to the
underlying logs, several of which already disagree with the write-up in
exactly the ways this doc corrects.
