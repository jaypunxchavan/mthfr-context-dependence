# Detection Floor, Apples-to-Apples Control, and Mechanism Deep-Dive

Source: external evaluator review of `MTHFR_RESULTS_LOG_PART2.md` (read
against Part I and the proposal). This review is sharper and more
technical than prior rounds and identifies real weaknesses in claims this
project has been treating as settled. Read the full review before starting
— this doc organizes its items into executable groups but does not
reproduce every sentence of reasoning; the original review has that.

**The evaluator's own top-3 picks for this session, stated explicitly, and
honored in the execution order below:** read the Group C-H digest, run all
five ESM-1v seeds, build a project-own detection floor. Do these three
regardless of what else gets attempted.

**Explicitly OUT OF SCOPE for unattended execution:** Group AG at the
bottom of this doc lists the review's framing/presentation/strategy
questions (the one-sentence claim, which figures to use, outreach to
authors, the "second system" choice, the AI-use disclosure). These are
judgment calls for the user, not analysis tasks. Do not attempt them
tonight — read Group AG once at the end so it's visible, then stop.

---

## Group AA — An apples-to-apples positive control, and a project-own detection floor

This is the evaluator's single highest-priority item: I1 validated a
different statistic (association-null, doesn't center on zero) than the
one that actually produced the project's headline finding (sign-flip null,
centers on zero). These are not the same instrument.

**Task AA1 — Transplant the MTHFR estimator onto GB1**
- AA1a. Using GB1's full 20^4 combinatorial landscape (already on disk),
  define a fixed background at one site (e.g. V54→ some alternate letter)
  the same way A222V is fixed in MTHFR. Compute a measured e.b analog from
  the single-mutant and double-mutant arms of the OTHER three sites,
  using the same construction logic as `own_context.py` (weighted
  least-squares residual from a multiplicative no-interaction
  expectation) adapted to GB1's design — document every adaptation
  explicitly, this is not a copy-paste.
- AA1b. Compute a GB1-analog `delta_ESM` the same way script 12 does for
  MTHFR (ESM-2 score with vs without the fixed background substitution).
- AA1c. Run the IDENTICAL signed sign-flip pipeline (script 33's code
  path, reused not rewritten) on this GB1-transplanted pair. Report
  whether the null centers on zero (the actual test of whether THIS
  instrument, not a different one, has power).

**Task AA2 — Characterize the unit of analysis and effective n**
- AA2a. State explicitly what the clustering unit is in this transplanted
  design (site? genotype? something else), and report the effective
  number of independent units the sign-flip null test is actually run
  over. If it's on the order of ~20-30 units, say so plainly rather than
  letting a p-value imply more precision than that supports.

**Task AA3 — Investigate why the four-site I1 null didn't center on zero**
- AA3a. The null mean moved from +0.3880 (3-site) to +0.2476 (4-site) —
  a large shift from one added site. Before treating the four-site PASS
  as clean, characterize what structural feature of the ASSOCIATION null
  (not the sign-flip null used elsewhere) produces a nonzero center at
  all. Compare the null construction used in scripts 49/65 against the
  sign-flip construction used in script 33/AA1c — are they the same kind
  of null? If not, that is itself the answer to why I1 doesn't
  generalize as evidence for the MTHFR pipeline's specific test.

**Task AA4 — Build a detection floor for MTHFR's own design (highest-value item in this group)**
- AA4a. Using MTHFR's actual n, position clustering structure, and
  measured per-condition noise, simulate a predictor with a KNOWN,
  injected partial correlation to e.b (start with several magnitudes,
  e.g. rho_true in {0.05, 0.10, 0.15, 0.20, 0.25}).
- AA4b. Run each simulated predictor through the EXACT same pipeline used
  for the real delta_ESM-vs-e.b test (position-cluster bootstrap,
  sign-flip null, same N_BOOT/N_PERM). Determine the smallest rho_true
  detected at ~80% power across repeated draws at each magnitude.
- AA4c. Report the result as the evaluator specified: "we could have
  detected rho >= X; we observed -0.088." This converts the project's
  central negative result from absence-of-evidence to evidence-of-absence
  and is worth more than any borrowed comparator's gate pass.
- AA4d. Save to `data/processed/task_AA4_detection_floor.csv`.

**Task AA5 — State the distance caveat explicitly, in writing**
- AA5a. GB1's four sites are spatially adjacent; MTHFR's variants sit up
  to 200+ residues from position 222. Write one paragraph, saved
  alongside this group's other outputs, stating plainly that passing a
  local-epistasis positive control does not automatically license a
  claim about detecting DISTANT epistasis — this is a scope limitation on
  I1/AA1's result, not a flaw in either.

**Task AA6 — Resolve or explicitly fail to resolve the ε=7.40-vs-5 discrepancy**
- AA6a. Before this discrepancy is presented publicly anywhere: identify
  the exact variant filters, replicate-exclusion rules, and read-count
  thresholds Wu et al. 2016's Figure 3D actually used (check the paper's
  Methods and any supplementary files already fetched, or fetch
  supplementary materials if not yet on disk, within the existing 200MB
  Group-T-style budget). Test whether ANY documented threshold, applied
  to the raw landscape file, moves the re-derived 7.399806 to 5.0.
- AA6b. State a plain PASS (resolved, here's the threshold that explains
  it) or FAIL (not resolved with available sources) — per the
  evaluator's instruction, do not let this ship in any public-facing
  material without one of those two answers.

**Task AA7 — A second, independently sourced positive control (only if Group AB below doesn't supply one)**
- AA7a. Check Group AB's results FIRST (ProteinGym may supply this for
  free). Only if it doesn't: search for a second double-mutant DMS
  dataset distinct from GB1, pre-register the exact same
  transplant-and-test methodology as AA1 BEFORE running it on the new
  dataset, and execute.

---

## Group AB — Check ProteinGym before doing anything else expensive (may unblock T, AC4, and part of AD/AE for free)

**Task AB1 — Does ProteinGym include this project's actual assay?**
- AB1a. Check whether ProteinGym's substitution benchmark includes
  `MTHFR_HUMAN_Weile_2021` (or an equivalent naming), and whether it ships
  curated MSAs and precomputed scores for its ~70 models (EVmutation, EVE,
  GEMME, TranceptEVE, MSA Transformer, an ESM-1v ensemble, among others)
  for that assay specifically.

**Task AB2 — If found: pull the multi-model comparison for free**
- AB2a. If precomputed scores exist for this assay, correlate EACH
  available model's scores against measured e.b the same way script 32
  does for ESM-2's delta_ESM. Build one comparison table across every
  model ProteinGym provides.
- AB2b. If ProteinGym's ESM-1v scores are present, this satisfies Group
  AC's five-seed requirement (AC4) without a 39GB fetch — check for this
  specifically and cross-reference before attempting AC4's direct fetch.
- AB2c. If ProteinGym ships an EVmutation/coupling-based score, this may
  satisfy Group T's original goal directly — report it as a valid
  substitute for the failed Group T MSA-based attempt (not a redo of T,
  a different, better-sourced route to the same question).

**Task AB3 — If NOT found for this exact assay: get the alignment infrastructure right for a direct MTHFR attempt**
- AB3a. Check what jackhmmer settings produced Group T's 566-row GB1
  alignment against EVcouplings' standard protocol (bitscore threshold
  ~0.3-0.5 bits/residue against UniRef90, 5 iterations, column coverage +
  gap filters, ~80% identity reweighting). Identify what differed.
- AB3b. Compute Neff/L for whatever alignment was actually used. Below
  ~1, state explicitly that couplings from it would be unusable
  regardless of any mapping fix — do not proceed past this point if so.
- AB3c. If Neff/L looks usable, fetch a properly-parameterized MTHFR
  alignment directly (not GB1 — the evaluator is explicit that validating
  on GB1's alignment doesn't answer the MTHFR question) using the
  corrected protocol, within the same 200MB-per-fetch budget convention
  used throughout this project.

**Task AB4 — The real head-to-head: J(222,i) couplings computed directly for MTHFR**
- AB4a. Only if AB3 produces a usable alignment (or AB2 supplies scores
  directly): compute or extract coupling terms between position 222 and
  every other scored position, correlate the implied interaction against
  measured e.b, same statistical conventions as everywhere else in this
  project. Report side by side with delta_ESM's -0.088 and ThermoMPNN's
  -0.0733. This is the comparison the evaluator calls the true test —
  treat it as such, not as a footnote to Group T.

---

## Group AC — Model robustness, done properly this time

**Task AC1 — Reconcile the 150M vs 650M CI widths**
- AC1a. Report the exact n the 150M run used. Compute implied effective
  n from each CI half-width (150M: 0.136 → ~200; 650M: 0.029 → ~4,500
  against a raw n of 10,757). If the 650M bootstrap uses position
  clustering (it should, per this project's own convention), confirm
  that explicitly and report the resulting design effect (~2.3 if the
  numbers check out) as exactly what a properly conservative clustered
  CI should look like. If it does NOT use clustering, the CI is
  unexplained — flag this as a possible bug, do not guess.

**Task AC2 — Direct 150M-vs-650M agreement, not just sign agreement**
- AC2a. Compute the correlation between delta_150M and delta_650M across
  the same variants (not just what fraction agree in sign). Separately
  compute the correlation between the two models' raw WT scores. Report
  both. If WT scores agree strongly (e.g. rho ~0.8) while the deltas do
  not (e.g. rho near 0), state this plainly as the evaluator's proposed
  reading: the background-response signal is not a stable property of
  the model family, which is itself a finding, not merely a caveat on
  11.1.

**Task AC3 — Numerical precision check (cheap, potentially decisive)**
- AC3a. Report delta_ESM's typical magnitude in nats, and the dtype and
  batch size that originally produced it.
- AC3b. Rescore a few hundred variants (reuse whatever subset convention
  is already established) in fp32 (and fp64 if feasible), at a different
  batch size, and on CPU instead of the original device. Check whether
  delta_ESM reproduces to the precision the finding actually needs. If it
  does NOT reproduce, this is a more mundane and more urgent explanation
  for 11.1's instability than model-family disagreement, and several
  downstream results would need re-running — say so plainly if found.

**Task AC4 — All five ESM-1v seeds (the evaluator's own top-3 pick)**
- AC4a. Check AB2b first — if ProteinGym already supplies all five
  members' scores, use those and skip the fetch entirely.
- AC4b. If not available that way: fetch all 5 ESM-1v ensemble members
  (not just member 1 as previously planned), same size-verification
  discipline as before (confirm the 7.83GB-per-member figure by loading
  and counting parameters — optimizer state in the checkpoint is the
  most likely explanation per the evaluator, verify rather than assume).
  This is a substantial fetch (5x the single-member budget) — check
  total available disk space before starting and report it.
- AC4c. Score MTHFR with each of the 5 members, same procedure as
  650M/150M. Compute delta_ESM-vs-e.b for each of the 5, AND the
  cross-member agreement on WT scores vs cross-member agreement on the
  delta-vs-e.b correlations themselves.
- AC4d. State the decisive verdict plainly: if the five members agree
  tightly on WT scores but scatter across zero (some positive, some
  negative) on their delta-vs-e.b correlation, that is strong evidence
  the "epistasis signal" reported elsewhere in this project is seed
  noise rather than a stable model property. If they agree in direction
  too, that's evidence for a real, reproducible signal. Either answer is
  valuable — report whichever the data shows.

**Task AC5 — Fix and verify the PLL construction before running it at full scale**
- AC5a. Before committing to U2's full run: confirm explicitly whether
  the position-222 term cancels in the delta_PLL construction as
  intended. If it does not cancel cleanly, the 222 term could dominate
  the whole-sequence sum and break comparability with the single-position
  masked-marginal delta_ESM. Inspect the actual construction in script
  67 and report which case holds, with the supporting arithmetic shown,
  before trusting any full-N run's output.

**Task AC6 — SaProt without the frozen-structure assumption (the real experiment, not just the control)**
- AC6a. Check whether ESMFold (lighter-weight, no MSA required, unlike
  AlphaFold) is available within a reasonable budget (check size before
  fetching — likely a few GB, apply the same 3GB-class cap discipline
  used for other models; if it exceeds a reasonable cap, mark BLOCKED and
  report the size rather than downloading blind).
- AC6b. If available: fold the A222V-background sequence and extract ITS
  OWN 3Di structure tokens (rather than reusing WT's tokens, which is
  what the already-completed frozen-structure run does).
- AC6c. Rerun SaProt's delta_SaProt-vs-e.b test using this
  structure-aware background instead of the frozen one. Report side by
  side with the frozen-structure result. The evaluator's framing: frozen
  is the control, this is the actual experiment.

---

## Group AD — ThermoMPNN: audit the sign, then build a non-degenerate model

**Task AD1 — Sign-convention audit (do this before anything else in this group)**
- AD1a. Verify ThermoMPNN's sign convention on a known positive control:
  identify a documented buried-hydrophobic-to-charged substitution
  (either in MTHFR's own structure or a standard benchmark case) and
  confirm it scores as clearly destabilizing under whatever sign
  convention this project's existing runs used. If the sign is flipped,
  -0.0733 becomes +0.0733 and the interpretation in Part II §12 inverts
  — treat this as a STOP-FIRST check for this entire group, same
  discipline as the project's earlier S1/S2 checks.

**Task AD2 — Benchmark against A222V's known biophysics**
- AD2a. A222V's thermolability and FAD-cofactor loss are well-documented
  in the MTHFR literature. Search for any published ΔΔG or thermostability
  measurement for A222V specifically and compare against ThermoMPNN's
  -0.0439 (near-neutral) prediction. If the model misses the
  best-characterized destabilizing variant in this entire system, state
  this plainly as a real concern about trusting it elsewhere, not as a
  footnote.

**Task AD3 — Build the non-degenerate threshold model**
- AD3a. Pre-register the exact functional form BEFORE fitting anything:
  `predicted fitness = f(dG_wt + ddG_v + ddG_222)`, f a sigmoid;
  `predicted interaction = f(both) - f(v) - f(222) + f(wt)`. Fit the
  sigmoid's two free parameters using ONLY the (ddG, fitness) relationship
  from single mutants — never tuned against the interaction term itself
  or against e.b. Document the exact fitting procedure in the new
  script's docstring before running, per this project's standing
  pre-registration discipline.
- AD3b. Test the model's sharp, falsifiable prediction: interaction
  should be largest for variants whose ddG sits near the threshold and
  vanish at both extremes (an inverted U). Bin real e.b by predicted-ddG
  distance from the fitted threshold and check whether this shape
  appears. Report plainly whether it does or doesn't — a clean
  non-appearance is as informative as a clean appearance.

**Task AD4 — Check for native double-mutant scoring**
- AD4a. Check whether ThermoMPNN supports direct double-mutant ΔΔG
  scoring. If so, compute `ddG(v + A222V) - ddG(v) - ddG(A222V)` directly
  as a non-degenerate predicted interaction with no additive-term
  degeneracy at all, and correlate against e.b the same way as
  everywhere else. This would be a cleaner result than AD3's fitted
  model if available — prefer it if both are feasible.

**Task AD5 — Confound-control the ThermoMPNN result the same way ESM-2's was controlled**
- AD5a. Reuse the exact multivariable-control machinery already built for
  ESM-2 (scripts 18/24's method: base fitness, RSA, position fixed
  effects, cluster-robust SEs) and apply it to ThermoMPNN's -0.0733.
  Report whether it survives the same controls.

**Task AD6 — Region 4: alignment depth as the discriminator, not an MTHFR quirk**
- AD6a. Using whatever MTHFR alignment Group AB produces (reuse, don't
  refetch), compute a per-position depth/conservation metric (Neff per
  column, or per-position entropy).
- AD6b. Test whether ESM-2's background-shift signal (|delta_ESM|)
  tracks this depth metric while ThermoMPNN's residual does not,
  region by region. If confirmed, state the evaluator's proposed
  general rule explicitly: PLM background-awareness requires
  evolutionary depth; structure-based models don't need it. This would
  be the single most transferable claim in the project if it holds —
  treat it with commensurate care (full region breakdown, CIs, not just
  a pooled number).

**Task AD7 — Does the region-4 result survive dimer scoring?**
- AD7a. 6FCX chain A alone treats MTHFR as a monomer; region 4 is the
  dimerization domain. Rerun ThermoMPNN's structural scoring against the
  biological dimer assembly (both chains) rather than chain A alone, at
  least for region-4 positions, and check whether the region-4
  discriminator result (Part II §12.4) holds up.

**Task AD8 — Joint model test: is ThermoMPNN's signal additive to ESM-2's?**
- AD8a. On the matched-n row set (reuse Z1's intersection from the prior
  session), fit both predictors jointly (rank-based) and report
  semipartial contributions in each direction — a real test of whether
  the two carry independent information, replacing the current "CIs
  overlap" comparison with something decisive.

---

## Group AE — Sharpening the H1a reversal (the mechanism question)

**Task AE1 — Isolate position vs residue identity: all 19 backgrounds at 222**
- AE1a. Score all 19 possible substitutions AT position 222 as
  backgrounds (not just A→V), same delta_ESM construction as before for
  each. Does the outsized context-shift found for A222V specifically
  track being AT position 222 generally, or is it specific to Val?

**Task AE2 — The matched control: A→V at other positions**
- AE2a. Identify positions elsewhere in MTHFR where the wild-type residue
  is also Ala, and score A→V substitutions at THOSE positions as
  backgrounds, same construction. Compare context-shift magnitude against
  AE1's position-222 sweep. Together AE1+AE2 form the two clean 2x2 cells
  the evaluator specifies: position x identity.

**Task AE3 — The phylogenetic/clade hypothesis**
- AE3a. Using an MTHFR ortholog alignment (reuse Group AB's fetch if
  suitable, or fetch one directly within the same budget convention),
  determine what fraction of MTHFR homologs carry Val at the position
  aligned to human residue 222.
- AE3b. If V222 is common in some clades: test whether the positions
  where delta_ESM is largest show clade-specific residue preferences that
  co-vary with residue 222's identity across the alignment. This is the
  evaluator's proposed unifying mechanism (a phylogenetic subfamily
  reassignment effect, not a biophysical one) — if it holds, note
  explicitly that it would also offer a candidate explanation for the
  wrong-sign result AND the region-4 failure, per the evaluator's own
  reasoning, but do not over-claim a single unifying story without the
  region-4/AD6 alignment-depth result also being checked for consistency
  with it.

**Task AE4 — Does shift magnitude predict shift accuracy?**
- AE4a. Bin variants by `|delta_ESM|` (quartiles or deciles, pre-register
  the choice) and compute the delta_ESM-vs-e.b correlation within each
  bin. Report whether accuracy improves, stays flat, or worsens as shift
  magnitude increases. State the result plainly, including if it supports
  the "most confidently wrong where it moves most" framing — this is a
  strong, memorable claim ONLY if the data actually shows it; do not
  reach for that framing if the bins are flat or noisy.

---

## Group AF — Bookkeeping (read the digest FIRST, before any other group)

**Task AF1 — Read the Group C-H digest (do this before anything else this session)**
- AF1a. Locate and read
  `docs/tasks/comparators-and-consolidation/GROUPS_C_TO_H_DIGEST.md` in
  full. Quote its Group C section (the rank-vs-MAE reconciliation)
  verbatim in this session's log. This has been outstanding across
  multiple sessions and determines the project's top-line sentence about
  whether ESM-2 "fails" or the finding is metric-dependent.

**Task AF2 — One canonical variant manifest**
- AF2a. Reconcile the three different missense totals appearing across
  this project's documents (11,902 in the original proposal; 11,344 used
  in Part II §12; 11,113 used in Part I §6.2) and the four different
  analysis n's (10,757 / 10,141 / 9,740 / 9,595) into a single exclusion
  cascade: starting count, each filtering step applied (by which
  script), and the resulting n at each stage, per predictor. Save as
  `data/processed/task_AF2_variant_manifest.csv` — this is both a rigor
  fix and, per the evaluator, a strong candidate poster figure (a
  CONSORT-style flow diagram) once visualized.

**Task AF3 — Audit which of Part I's flagged items were actually run**
- AF3a. Check, plainly, whether each of the following has actually been
  executed anywhere in this project's logs (not assumed): cluster-robust
  inference used consistently throughout (not just in some scripts);
  the delta_ESM-vs-S(v|WT) confound check; the full sign-convention
  audit (S2's original scope — has it been extended to every new
  predictor added since, e.g. ThermoMPNN, SaProt?); the oracle/ceiling
  calculation; nonlinear (spline) fitness controls. Report a plain
  done/not-done/partial status for each, with the log entry it came
  from if done.

---

## Group AG — NOT for unattended execution; read once, do not act on tonight

These are the evaluator's framing, strategy, and presentation questions.
They require the user's own judgment and are listed here only so they are
visible in this doc, not because any of them should be attempted by an
automated session:

- What is the project's one-sentence claim, and which of the ~40 scripts
  in this repo are actually load-bearing for it (vs. cuttable from a
  poster)?
- What is the "second system" that would turn this from a case study into
  a general claim about PLMs (CBS, a ProteinGym multi-mutant assay, or
  the GB1 transplant from Group AA)?
- What is the concrete deliverable (a released benchmark, a calibrated
  trust-rule keyed to alignment depth, a "conditionally damaging"
  classifier)?
- What is the clinical framing number (how many ClinVar VUS sit in cis
  with A222V, and how many would be scored differently)?
- Whether and how to contact the atlas co-authors (region-4 finding) and
  the GB1 paper's authors (the ε discrepancy) directly.
- Which three figures to build for a poster.
- The AI-use disclosure and personal-contribution accounting the
  evaluator flagged as something a judge will press on directly — this is
  for the user to prepare, not something a coding session produces.

---

## Suggested execution order

1. **AF1 (the digest) — literally first, unconditionally.** The
   evaluator's own instruction, repeated here because it matters: this
   determines the project's top-line sentence and has been outstanding
   too long.
2. **AB (ProteinGym check) — second.** It may supply AC4's five ESM-1v
   seeds and part of Group AD/AE's alignment needs for free, and it's
   cheap to check before committing to expensive fetches elsewhere.
3. **AA4 (detection floor) and AC4 (five ESM-1v seeds)** — the
   evaluator's other two top-3 picks. Run these next regardless of what
   Group AB finds, since AA4 doesn't depend on it at all and AC4 only
   partially does.
4. **AD1 (ThermoMPNN sign audit) — before trusting AD2-AD8 or anything
   in Part II §12 that cites ThermoMPNN.** This is a STOP-FIRST check for
   its whole group, same discipline as this project's earlier S1/S2.
5. Everything else in Groups AA, AC, AD, AE — independent of each other,
   run in whatever order the environment's resources allow. Respect every
   budget and gate stated in each task.
6. **AF2, AF3** — do these whenever a heavy compute task elsewhere is
   running or blocked; they're mechanical and don't need to wait.
7. **AG — read once at the very end, act on nothing.**
