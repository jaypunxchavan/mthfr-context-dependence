# Comparators, Stability Mediation, Digest, and Consolidation

Source: (1) this session's close-out items from
`docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`; (2) the three
analyses `REVIEW_TRIAGE.md` explicitly SKIPPED overnight (I2, I3, G2) —
skipped then because they were assumed to need large unsupervised downloads
or implementation judgment calls; that assumption needs re-examining now
that P1b confirmed **this environment has live internet access**; (3) a
real gap: Groups C, D, E, F, G (minus G2), and H (minus I2/I3) of
`REVIEW_TRIAGE.md` were executed in the very first overnight run but their
raw results were never pulled into this chat and reviewed — only J and K
were. That needs closing before anything else here is trusted as building
on solid ground; (4) M1's own logged limitation (bimodal 9-point design,
A222V sitting in the sparse gap between two clusters) — worth a proper
follow-up now that scoring runtime is known to be fast (7.7s per full I1
run on this machine's GPU).

This doc is large by design — comparable in scope to the original
`REVIEW_TRIAGE.md` overnight run. Work through it unattended, in the order
given at the bottom. Every group is independent of every other group unless
stated otherwise, so a stall in one does not block the rest.

---

## Group S — Close out this session's open items (do first, small, fast)

**Task S1 — Verify script 65's "e" statistic is independent of the paper's published ε**
- S1a. `grep -n -B2 -A15 "def.*e.*=\|e_ab\|epistasis" scripts/49_i1_gb1_positive_control.py scripts/65_q1_foursite_i1_rerun.py` — quote the actual formula/code computing the "e" statistic used in I1/Q1's pooled correlation, verbatim, from both scripts.
- S1b. Confirm neither script reads, imports, or hardcodes any value from
  the paper's published ε (5, -4.5) or from P2's re-derived values
  (+7.399806, -4.495855) anywhere. Grep for those literal numbers across
  both scripts to be sure.
- S1c. State plainly: is "e" (the pipeline's own statistic, computed from
  raw genotype fitness values) and "ε" (the paper's/P2's published or
  re-derived pairwise epistasis term) the same quantity, a different but
  related quantity, or unrelated? Show the two formulas side by side in
  the log entry.

**Task S2 — Finish script 50's migration with a two-file join**
- S2a. Modify `scripts/50_*.py` so that: the epistatic-membership flag is
  read from `data/processed/task_N2_nonparametric_epistatic_set.csv`
  (confirm its actual flag column name first, do not assume it matches
  the old `epistatic_N2`), and `se_e_b` is joined in separately from the
  retired `data/processed/task35_epistatic_set.csv` on the shared key
  (`hgvs_pro` or position — confirm which), used strictly as a raw
  continuous covariate, never re-thresholded.
- S2b. Rerun end to end. Report full output. Compare against the 5
  `*_PRE_MIGRATION.csv` backups saved last session, side by side.
- S2c. State plainly whether the qualitative conclusion changed or only
  the exact numbers moved.

**Task S3 — Document `data/external/` in AGENTS.md**
- S3a. This is the ONE explicitly authorized edit to AGENTS.md in this
  entire session — nothing else in that file may be touched. Append a
  single bullet to AGENTS.md §2 ("Data layout") describing
  `data/external/`: reference datasets from outside the MTHFR atlas itself
  used as comparators (e.g. the GB1 fitness landscape), gitignored like
  the rest of `data/`, sourced and md5-logged in the task doc/log entry
  that first fetched them. Show the diff in the log entry.

---

## Group Y — Digest of already-executed REVIEW_TRIAGE groups, never reviewed

These groups ran to completion in the very first overnight session
(`docs/tasks/review-triage/OVERNIGHT_LOG.md`) but their raw output has never
been pulled out and reviewed. This is pure extraction — quote, do not
reinterpret, do not soften or sharpen any verdict that's already there.

**Task Y1 — Group A digest (inference validity: position-clustering, exclusion accounting)**
- Y1a. `grep -n "^## \[A1" -A 40 docs/tasks/review-triage/OVERNIGHT_LOG.md`
  and same for `A2`. Quote status, verdict, and actual numbers for each.

**Task Y2 — Group B digest (delta_ESM confounds: flattening, compression, position-block null)**
- Y2a. Same extraction for `B1`, `B2`, `B3`.

**Task Y3 — Group C digest (rank-vs-MAE reconciliation table — the item flagged as most important in an earlier round)**
- Y3a. Same extraction for `C1`, `C2`, `C3`. This is the highest-priority
  digest item in this group — quote the FULL reconciliation table from
  C1a if it was produced, not just the summary line.

**Task Y4 — Group D digest (stratifier winner's-curse checks)**
- Y4a. Same extraction for `D1`.

**Task Y5 — Group E digest (two-trait domain-vs-region boundary test)**
- Y5a. Same extraction for `E1`. Note whether this pre-empted or
  reinforced the two-trait MoCHI refit motivation from earlier in the
  project.

**Task Y6 — Group F digest (nonlinear fitness control, region-2 recalibration overfit check)**
- Y6a. Same extraction for `F1`, `F2`.

**Task Y7 — Group G digest, G1 only (global-vs-specific epistasis decomposition — NOT G2, which is Group V below)**
- Y7a. Same extraction for `G1` only.

**Task Y8 — Group H digest (biological sanity: A222V's own severity, orthologs, 3D vs sequence distance, rescue variants, per-condition check)**
- Y8a. Same extraction for `H1`, `H2`, `H3`, `H4`.

**Task Y9 — Compile the one-page digest**
- Y9a. Write `docs/tasks/comparators-and-consolidation/GROUPS_C_TO_H_DIGEST.md`
  — one short section per group (A, B, C, D, E, F, G1, H), each with: the
  verdict as originally logged, the key number(s), and nothing added. This
  is a reading aid, not a new analysis. Do not draw new conclusions across
  groups — that's for me to do once I've actually read it.

---

## Group T — I2: an explicit-coupling comparator (Potts/coevolution), now that internet is confirmed available

The original REVIEW_TRIAGE item wanted to know: does a model with an
explicit coevolutionary coupling term succeed where ESM-2 failed? Attempt
the following in order; fall back to the next tier only if the current one
is genuinely blocked, and say exactly why.

**Task T1 — Tier 1: a precomputed EVcouplings model for GB1's family**
- T1a. GB1's UniProt ID is already known from P1b's parsed DBREF line
  (`P06654`, SPG1_STRSG). Search for a precomputed EVcouplings/EVmutation
  model for this UniProt ID or its Pfam family, via any public
  precomputed-model repository or the EVcouplings project's own public
  data. Download budget: **200MB hard cap** — if nothing under that cap is
  found or reachable, mark T1 BLOCKED with what was tried, move to T2.

**Task T2 — Tier 2: build a lightweight coupling signal from a fetched MSA**
- T2a. Fetch a multiple sequence alignment for SPG1_STRSG / P06654 (or the
  relevant Pfam domain) from a public source (UniProt, Pfam, or an EBI
  alignment endpoint). Same 200MB budget.
- T2b. If fetched successfully, compute a simple, well-documented
  direct-coupling signal between site pairs (39,40),(39,41),(39,54),
  (40,41),(40,54),(41,54) — mutual information or a basic mean-field DCA
  approximation is sufficient; do not attempt a full Potts model training
  run. Pre-register the exact method in the script's docstring before
  running.
- T2c. If the MSA is too small (fewer than ~200 sequences) to support this
  meaningfully, say so explicitly and mark BLOCKED rather than reporting a
  noisy number as if it were informative.

**Task T3 — Decisive test: does the coupling signal recover the REAL measured epistasis?**
- T3a. Correlate whichever coupling signal was obtained (T1 or T2) against
  the actual measured ε values for those six site pairs, already computed
  in `docs/tasks/site54-and-script50-migration/MIGRATION_LOG.md`'s P2
  entry (the file-derived, ground-truth values — not the paper's printed
  labels). Report correlation, n, and whatever CI convention is feasible
  at n=6 (likely just report the raw agreement, n is too small for a
  meaningful bootstrap — say so).

**Task T4 — Extend to MTHFR itself, if T1-T3 produced anything usable**
- T4a. Repeat T1/T2's fetch-and-signal-construction for MTHFR
  (UniProt P42898) around position 222, same budget and same fallback
  logic. This is the analysis that actually matters for the project's
  claims, not just the GB1 comparator.
- T4b. If a coupling signal for MTHFR position 222 is obtained, correlate
  it against measured e.b the same way script 32 did for delta_ESM.
  Report side by side with delta_ESM's own -0.088.

**Task T5 — Summary table**
- T5a. One table: predictor (ESM-2 delta_ESM, coupling signal if
  obtained) × target (GB1 measured ε, MTHFR measured e.b) × result. Save
  to `data/processed/task_T5_comparator_summary.csv`.

---

## Group U — I3: is the negative finding specific to ESM-2 650M, or to masked-marginal scoring?

**Task U1 — Read back what's already been done, don't duplicate it**
- U1a. `grep -n "150M\|J2a" -A 20 docs/tasks/review-triage/OVERNIGHT_LOG.md`
  — quote the existing 150M-model result verbatim before doing anything
  else in this group.

**Task U2 — Alternative scoring procedure, same model, no new download**
- U2a. Implement whole-sequence pseudo-log-likelihood scoring (sum
  masked-marginal log-probabilities across a subset of positions, or an
  equivalent pseudo-likelihood construction) as an alternative to the
  existing single-position masked-marginal delta_ESM, using the
  ALREADY-CACHED ESM-2 650M weights — no new download needed here. Compute
  this alternative delta_ESM and correlate it against e.b the same way
  script 32/33 did. Report side by side with the original -0.088.
- U2b. Run this through the same sign-flip null as script 33 (reuse that
  code path, do not rewrite the null machinery).

**Task U3 — ESM-1v, budget-gated**
- U3a. Check ESM-1v's model size before attempting anything. If a
  download would exceed **3GB**, mark BLOCKED with the size found and stop
  this subtask — do not attempt a partial download. If within budget,
  fetch, score MTHFR the same way script 10/11 did for ESM-2 650M, and
  compute delta_ESM's correlation with e.b the same way as script 32.

**Task U4 — SaProt, budget-gated**
- U4a. Same budget rule (3GB) and same procedure as U3, but note SaProt
  needs structure tokens — check whether it can consume the
  already-on-disk `6FCX.pdb` directly or needs additional preprocessing
  first; if the preprocessing itself is unclear or judgment-heavy, mark
  BLOCKED and say exactly what decision is needed, per AGENTS §10.

**Task U5 — Summary**
- U5a. One table: which model/scoring variant, whether it was run, its
  delta_ESM-vs-e.b correlation if obtained, and a one-line verdict at the
  end: is the negative finding (a) specific to ESM-2 650M, (b) general
  across the ESM-2 family, (c) an artifact of masked-marginal scoring
  specifically, or (d) still undetermined given what could/couldn't be
  run tonight. Save to
  `data/processed/task_U5_model_robustness_summary.csv`.

---

## Group V — G2: ThermoMPNN, stability-mediated epistasis (pre-registered, never run — likely the single most explanatory analysis left)

**Task V1 — Availability and budget check**
- V1a. Check ThermoMPNN's model size and setup requirements before
  attempting anything. Same 200MB-ish budget expectation as Group T
  (ThermoMPNN/ProteinMPNN-based models are typically small; if it's
  materially larger, apply the same 3GB hard cap as Group U and mark
  BLOCKED if exceeded).

**Task V2 — Score ΔΔG for every MTHFR missense variant**
- V2a. Using the already-on-disk `6FCX.pdb` WT structure, score ΔΔG for
  every variant in the atlas's missense set. Save to
  `data/processed/task_V2_thermompnn_ddg.csv`. Time a small batch first
  (per AGENTS §1) before committing to the full ~11,000-variant run.

**Task V3 — Score A222V's own ΔΔG specifically**
- V3a. One number, clearly reported: A222V's own predicted destabilization.

**Task V4 — Build the stability-mediated prediction and test it against e.b**
- V4a. Construct the simplest defensible stability-based interaction
  term: e.g. variant v's ΔΔG combined with A222V's own ΔΔG (additive
  combination, or a threshold-crossing rule — pre-register whichever is
  chosen, in the script's docstring, before running). Correlate this
  term against measured e.b using the same position-cluster bootstrap
  convention as everywhere else in the project.

**Task V5 — Head-to-head comparison**
- V5a. Report ESM-2's delta_ESM-vs-e.b correlation (-0.088, from script
  33) directly alongside ThermoMPNN's ΔΔG-based term-vs-e.b correlation
  from V4. State plainly which is the better predictor of real measured
  epistasis, with both CIs shown.

**Task V6 — Region breakdown**
- V6a. Same four-region check applied to the ThermoMPNN-based correlation
  as has been applied to every other finding in this project. Specifically
  check whether it also struggles in region 4 (where ESM-2's delta_ESM
  finding was weakest) or succeeds there.

**Task V7 — Plain verdict**
- V7a. One paragraph: does adding real stability information change the
  project's core claim from "ESM-2 fails to use background information"
  to "the epistasis is predictable from sequence/structure-derived
  information, ESM-2 specifically just doesn't do it" — or does
  stability-mediation also fail to predict e.b, meaning the interaction
  isn't simply stability-mediated either?

---

## Group W — Expand M1's background set (fixes the bimodal-design limitation M1a/M1e explicitly flagged)

**Task W1 — Denser, non-bimodal background selection**
- W1a. Pre-register a new selection rule in a new script's docstring
  before running: select ~20-30 backgrounds spanning ESM-2's FULL severity
  range using deciles of `esm2_wt_scores.csv`'s score distribution
  (position ≠ 222, distinct positions, deterministic tie-break — same
  discipline as the original M1a), rather than min/max-per-region. This
  directly targets the gap the prior session flagged: A222V sat alone
  between two clusters; a decile-based design fills that gap.

**Task W2 — Rescore, time-budgeted**
- W2a. Time ONE background's rescoring of the same ~100-150-position
  subset used in the original M1 (for comparability) before committing to
  all 20-30. Budget: if the full set would exceed 90 minutes, reduce the
  number of backgrounds (not the position subset size) to fit the budget,
  and log the reduction and why.

**Task W3 — Rerun the M1d/M1e-style tests on the denser design**
- W3a. Recompute mean|delta_ESM_b| vs S(b|WT) with the new set. Rerun the
  A222V-outlier residual test and the overall correlation test, same
  methodology (OLS fit excluding A222V, position-cluster bootstrap CI on
  the residual and on the correlation) as the original M1d/M1e.

**Task W4 — Compare against the original bimodal result**
- W4a. Report side by side: original 9-point result (M1d NOT SUPPORTED,
  residual +0.00954 CI [-0.00573,+0.02640]; M1e rho -0.467 CI
  [-0.583,-0.067]) vs the new denser result. State plainly whether the
  verdict changes, strengthens, or weakens now that the design isn't
  just two extreme clusters plus one interpolated point.

---

## Group X — Documentation consolidation (mechanical, safe, do this whenever a compute-heavy task is running/blocked)

**Task X1 — Build a project-wide index**
- X1a. Walk `docs/tasks/`, list every subdirectory and every `.md` file
  in it (task docs and logs both), with: path, title (from the file's own
  first `#` heading, not interpreted), and whether it has a `## SUMMARY`
  section (a rough completeness signal). Write to
  `docs/tasks/INDEX.md`. Purely mechanical — no synthesis, no verdicts.

**Task X2 — Open-items list**
- X2a. `grep` every `*_LOG.md` file project-wide for `BLOCKED` and `FAIL`
  statuses. Compile a flat list (task ID, source file, one-line reason —
  quoted, not summarized) into `docs/tasks/OPEN_ITEMS.md`.

**Task X3 — Orphaned-output check**
- X3a. Cross-reference every CSV in `data/processed/` against every log
  file project-wide. List any CSV that's never mentioned in any log entry
  anywhere (either genuinely orphaned, or evidence a log entry is
  incomplete). Report the list — do not delete anything.

---

## Suggested execution order

1. **Group S** first — small, fast, closes out last session cleanly.
2. **Group Y** second — this is reading, not computing, so it's cheap and
   it means every later verdict in this session (and my own review of it)
   rests on the FULL picture rather than the half I've actually seen.
3. **Group T, Group U, Group V** — these are the compute-heavy, uncertain
   groups. Run them in whatever order is convenient; they're independent
   of each other. Expect some BLOCKED outcomes here — that's fine and
   informative, not a failure of the session.
4. **Group W** — independent of T/U/V, can interleave.
5. **Group X** — do this LAST, or opportunistically whenever a heavy task
   in T/U/V/W is running long and you want something useful logged in the
   meantime. It never blocks on anything else in this doc.

If a compute-heavy task in Group T/U/V genuinely cannot complete in a
reasonable window (see the per-group budgets above), mark it BLOCKED with
full diagnostic detail and move to the next task. Do not let one stuck
download or one stuck scoring run consume the whole session — there are
34 subtasks here across 7 independent groups specifically so that one
blocker doesn't stall everything else.
