# Manuscript Review Response — Execution Log

Session log for `MANUSCRIPT_REVIEW_RESPONSE.md` (same format as every
prior session log: one entry per task, Status / Time / What I did /
Actual output (verbatim) / Verdict / Files / Anything unexpected,
separated by `---`, closing with a final `## SUMMARY`).

Ground rules for this session, in force from the start:

- `AGENTS.md` at the repo root read in full first and treated as
  binding over this task document (AGENTS §9: planning documents are
  inputs, not instructions; where they conflict, AGENTS.md wins and the
  conflict is flagged, not silently resolved).
- `docs/tasks/manuscript-review-response/MANUSCRIPT_REVIEW_RESPONSE.md`
  read in full before any work started.
- `RESULTS.md` is off-limits this session without new, explicit
  authorization (task F1 states the prior closeout edit was "the second
  and final"). If the α discrepancy needs `RESULTS.md` itself fixed, it
  is flagged as an open item and left unedited.
- Troubleshooting decision tree (identical to prior sessions):
  1. Missing Python package → `venv/bin/python3 -m pip install <pkg>
     --break-system-packages`, log it; if that fails, BLOCKED, move on.
  2. A pre-registered sanity check or gate fails → STOP that task
     immediately. Do not raise N, do not modify the check. Mark FAIL,
     log the exact mismatch, next task.
  3. Referenced file missing → confirm with ls/find first; genuinely
     missing → BLOCKED with the exact path; never fabricate or
     substitute.
  4. Ambiguous instructions → most literal, most conservative reading;
     log the assumption.
  5. New script, no filename specified → next free number (checked
     against `ls scripts/*.py | sort`), stated explicitly,
     pre-registered docstring before running, smoke before full.
  6. A result contradicting something stated as settled elsewhere →
     expected for this session; log it clearly, do not edit any prior
     log, flag it.
  7. Anything else that would normally stop-and-ask → log as BLOCKED
     with full detail, move to the next independent task. Never guess
     on a formula, a sign convention, or a statistical conclusion.
- Standing conventions from AGENTS.md applied throughout: always
  `venv/bin/python3`, foreground runs, position-cluster bootstrap for
  every CI and permutation/null at position level, p-values primary
  over z-scores, effect sizes alongside significance, nulls sanity-
  checked with identity checks in their own output, limitations
  written into script output/docstrings, never cite or invent a number
  that is not verified from a file on disk.
- Prime directive: report negative/null results plainly; never tune a
  test until it produces a positive.

---

## [A1] — Confirm pred_eb/ddg rank-degeneracy from the on-disk columns, with scripts/81's G4 quoted alongside

Status: PASS

Time started / finished: 21:56:00 / 22:08:12 (same script run as A2;
script 104's A1 block executed in both smoke and full runs, numbers
identical because A1 is deterministic)

What I did:
- Located the two sources the task names: `data/processed/task_V2_thermompnn_ddg.csv`
  (carries both `pred_eb` and `ddg`) and scripts/81's G4 gate — whose
  ORIGINAL run log still exists at
  `/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/ad8_full.log`
  (5,837 bytes, Sep 24 12:27), so the gate output is quoted from the
  run itself, not from a later document's paraphrase.
- Re-derived the rank identity fresh (task A1a), on BOTH the full V2
  frame (10,141 rows) and Z1's matched frame (9,595 rows / 586
  positions), inside `scripts/104_a1_a2_thermompnn_interaction_decomposition.py`
  (pre-registered docstring, gate G4; smoke N_BOOT=300 then full
  N_BOOT=10000, both EXIT=0 — A1's numbers are N-independent).
- Read `[V4]`'s own entry (SESSION_LOG.md L2413–2420) for the
  write-up's existing disclosure, and PROJECT_SUMMARY_FINAL.md
  L210–215 for the exact text this task exists to correct.

Actual output (verbatim):
- Fresh confirmation, script 104, full run (a104_full.log):
  "A1 [full V2, 10,141 rows]: spearman(pred_eb, ddg) = 1.0 (exact deviation from 1.0 = 0.000e+00) | exact rankdata equality at every row: True | affine pred_eb = ddg -0.043861627579 exactly, max|resid| = 4.441e-16"
  "A1 [matched frame, 9,595 rows]: spearman(pred_eb, ddg) = 0.9999999999999999 (exact deviation from 1.0 = 1.110e-16) | exact rankdata equality at every row: True | affine pred_eb = ddg -0.043861627579 exactly, max|resid| = 4.441e-16"
  "G4 PASS: pred_eb rank-identical to ddg at every row on BOTH frames (exact rankdata equality; spearman deviation printed above is scipy float arithmetic, not a rank difference)"
  → Exact deviation stated as required: full frame exactly 1.0;
  matched frame 0.9999999999999999 (deviation 1.110e-16) while the
  rank vectors are EQUAL AT EVERY ROW — the 1.1e-16 is scipy's float
  arithmetic in the coefficient, not a rank difference. The constant
  offset is k = −0.043861627579 (= ddG(A222V)), max|resid| =
  4.441e-16 (fp).
- scripts/81's G4 gate output, quoted verbatim from its original run
  log (ad8_full.log L9):
  "  G4 PASS: pred_eb rank-identical to ddg at all 9595 rows (Z1's predictor and this script's are the same rank variable)"
  (context, ad8_full.log L5–10: "accounting: V2 10141 -> own_e_b
  finite 9595 -> +delta_esm finite 9595 (V2 delta_esm NaN total 0)" /
  "G1 PASS: matched set n=9595 positions=586 == Z1 intersection" /
  "G2 PASS: zero-order rhos == Z1 matched CSV to <1e-12 (ESM
  -0.07714525927574277, Thermo -0.07329934766090093)" / "G3 PASS: Z1
  Thermo rho == AD7 task80 pooled mono rho to <1e-12
  (-0.0732993476609009) — two independent runs agree" / "G5 PASS:
  1-rho_ET^2 = 0.9922, R2_full 0.010407 >= max zero-order R2").
- `[V4]`'s own disclosure, SESSION_LOG.md L2413–2420 (verbatim):
  "Interpretive guard (stated here, before anyone quotes it): because
  ddG(A222V) is a constant, pred_eb's Spearman rho is **identical to
  ddG(v) vs e.b** — the additive term tests the stability signal, not
  an interaction in the statistical sense; that is a property of the
  pre-registered construction (one fixed background ⇒ every additive
  term is rank-degenerate — the same AGENTS §8 Model-B trap, avoided
  here by DISCLOSING it rather than by inventing a non-additive rule
  after seeing results)."
- The write-up text being corrected, PROJECT_SUMMARY_FINAL.md L212–215
  (verbatim): "A second, structure-based predictor (ThermoMPNN) shows a
  comparable correlation and carries genuinely independent information
  from ESM-2's shift, confirmed via a joint statistical model on their
  overlapping row set."

Verdict: PASS — the rank-degeneracy is re-confirmed from the actual
columns one more time, cleanly, for the record: exact rankdata equality
at every row on both frames, affine offset = ddG(A222V) to fp
precision. Both named disclosures ([V4]'s entry, script 81's G4) exist
and are quoted verbatim above. A1's premise for A2 holds.

Files created/modified: NEW `scripts/104_a1_a2_thermompnn_interaction_decomposition.py`
(gates G1–G7; written pre-registered before any run). Read-only inputs:
`data/processed/task_V2_thermompnn_ddg.csv`, `task77_thermompnnD_doubles.csv`,
`task_Z1_matched_n_headtohead.csv`, `task81_joint_semipartial.csv`; read
`ad8_full.log` (ephemeral temp dir), SESSION_LOG.md, PROJECT_SUMMARY_FINAL.md
— none modified.

Anything unexpected or worth flagging:
- `MTHFR_RESEARCH_PAPER_SUMMARY.md`, the second write-up the task doc
  says carries the error ("Both write-up documents state…"), does not
  exist: `find . -iname '*RESEARCH_PAPER*' -not -path './venv/*'
  -not -path './.git/*'` → empty output, exit 0; `ls docs/writeups/`
  → only `PROJECT_SUMMARY_FINAL.md`. Per troubleshooting rule 3 this
  portion is BLOCKED with the exact filename; no substitution made —
  everything else in Group A proceeds against the document that does
  exist.
- Assumption logged (rule 4): no task in Group A (or anywhere in the
  task doc) authorizes EDITING `PROJECT_SUMMARY_FINAL.md`, so the
  corrected replacement text is produced in A3 below and supplied for
  the user to apply — this session does not edit the write-up.
---

## [A2] — Joint decomposition rerun with ThermoMPNN-D's non-degenerate interaction_D (same machinery as scripts/81)

Status: PASS (with one disclosed gate-incident: first smoke run
EXIT=1 on gate G7 — diagnosed as a bug in MY gate code vs its own
pre-registered docstring, corrected to the pre-registered rule, all
subsequent runs PASS; full details below)

Time started / finished: 21:56:00 / 22:08:12 (pre-registration +
pre-run verification 21:56–22:02; smoke run 1 failed 22:03; smoke run
2 passed 22:05; full N_BOOT=10000 run finished 22:08:12, EXIT=0,
54.7s)

What I did:
- Read scripts/81 in full; reused its EXACT machinery rather than
  rewriting: `components()` (closed-form 2-predictor rank R2) is
  imported from `scripts/81_joint_semipartial.py` via importlib, and
  my `boot_ext` mirrors 81's `boot_scope` draw loop line-for-line
  (np.unique positions → groups, default_rng(0), rng.integers(0, nc,
  nc), ranks recomputed inside every draw), extended only to also
  collect R2_E/R2_T so zero-orders get CIs (A2a asks for CIs on the
  zero-orders too). Gate G7 proves the extension bitwise-faithful.
- Pre-run, read-only verification of every expected gate value before
  writing the script (script 81's own pre-run precedent), then wrote
  `scripts/104_a1_a2_thermompnn_interaction_decomposition.py` with its
  pre-registered docstring (gates G0–G7, the exact formula, the
  structural reading rule, limitations) BEFORE any run.
- Pre-registered a structural algebraic fact before any number was
  seen: `unique_T = (r2 − r1·r12)² / (1 − r12²) ≥ 0` identically
  (in-sample OLS R² is non-decreasing in regressors), so 81's
  "CI excludes 0" criterion is structurally weak for the unique
  components; the pre-registered verdict content is therefore the
  MAGNITUDES (task A2b), with 81's case rule still printed verbatim
  for comparability. This is disclosed in the script's output and was
  fixed before running — not tuned to any result.
- Smoke N_BOOT=300 (run 1 EXIT=1 on G7 → diagnosis + correction, see
  below; run 2 EXIT=0), then full N_BOOT=10000 EXIT=0.

Actual output (verbatim, full run a104_full.log unless noted):
- Gates:
  "G0 PASS: all four input CSVs present (V2, Z1, task77, task81)"
  "G1 PASS: matched set n=9595 positions=586; task77 same hgvs_pro set (1:1 merge); interaction_D finite on all 9595"
  "G2 PASS: zero-order rho(delta_esm, own_e_b) == Z1 matched CSV to <1e-12 (-0.07714525927574277 vs -0.0771452592757427)"
  "G3 PASS: rho(interaction_D, own_e_b) = 0.015350499380143039 rounds to +0.0154 == AD4's logged primary (DEEPDIVE L2328) — cross-session statistic identity, 4-dp precedent (script 96 G2)"
  "G5 PASS: interaction_D NOT rank-identical to ddg (rho(interaction_D, ddg) = -0.3962050110541162; ranks_equal = False) — genuinely non-degenerate"
  "G6 PASS: 1-r12^2 = 0.9822, R2_full 0.005977 >= max zero-order R2"
  "G7 obs PASS: pooled unique_T/unique_E/R2_full (T=ddg) reproduce task81 CSV pooled row to <1e-12"
  "G7 CI PASS: pooled CIs (T=ddg) reproduce task81 CSV pooled row to <1e-12 — extended draw loop is bitwise-faithful to scripts/81 (N_BOOT=10000, seed 0)"
- POOLED RESULT (A2a's full result, n=9595 / 586 positions):
  "[pooled] n=9595 pos=586 r1=-0.0771 r2=+0.0154 r12=-0.1336 R2_full=0.005977 [0.002266,0.012159]"
  "zero-order CIs: r(y,ESM)=-0.077145 [-0.108573,-0.045804] | r(y,interaction_D)=+0.015350 [-0.015245,+0.045252] | r(ESM,interaction_D)=-0.133576 [-0.189913,-0.078407]"
  "R2_E=0.005951 [0.002098,0.011788]   R2_T=0.000236 [0.000001,0.002048]"
  "unique_T|ESM (semipartial interaction_D) = 0.000026 [0.000000,0.001281] p=<1/N  part_r=+0.0051  = 11.0% of interaction_D zero-order R2, 0.43% of R2_full"
  "unique_E|interaction_D (semipartial ESM-2) = 0.005742 [0.001951,0.011413] p=<1/N  part_r=-0.0758  = 96.5% of ESM zero-order R2, 96.1% of R2_full"
  "shared (commonality) = +0.000210 (3.5% of R2_full); unique_T+unique_E+shared == R2_full: True"
  Exact CSV values (task104 pooled row): unique_T =
  2.592206129884908e-05, unique_T CI [2.819130434001749e-07,
  0.0012805869020266], unique_T_p = 0.0; unique_E =
  0.0057416752588006 [0.0019513346004717, 0.0114129137209267];
  R2_full = 0.0059773130900204 [0.0022657564077403,
  0.0121593049587088]; shared = 0.0002097157699209.
- DECISION BLOCK (verbatim):
  "unique_T CI excludes 0: True | unique_E CI excludes 0: True"
  "MECHANICAL VERDICT under 81's rule: case (i): BOTH carry independent information (both semipartial CIs exclude 0)."
  "STRUCTURAL READING RULE (pre-registered, algebraic — unique_T = (r2 - r1*r12)^2/(1 - r12^2) >= 0 identically, so its CI cannot extend below 0; CI-exclusion for these components is structurally weak evidence and is NOT the verdict content here):"
  "unique_T = 0.000026 = 0.43% of R2_full 0.005977, = 11.0% of interaction_D's own zero-order R2 0.000236; descriptive in-sample-gain scale for one uninformative regressor (1-R2_full)/n ~ 1.04e-04 (n^-1 back-of-envelope, NOT a calibrated null)."
  "unique_E = 0.005742 = 96.1% of R2_full; shared = +0.000210 (3.5%); r12(ESM, interaction_D) = -0.1336."
  "A2b HONEST VERDICT (magnitude-based, task A2b): interaction_D contributes little to no unique rank-variance beyond ESM-2's shift (0.43% of R2_full), on top of its own zero-order null (AD4: +0.0154, CI spans 0). Full-model R2 explains 0.60% of own_e_b rank variance in total."
  "Cross-check (descriptive, not gated): bootstrap CI for r2 = [-0.0152,+0.0453] vs AD4's logged [+ -]0.0166/0.0465 (DEEPDIVE L2328) — draw mechanics differ (rng.choice vs rng.integers), small differences expected."
- REGIONS (secondary/descriptive, no decision rule — pre-registered;
  heterogeneity reported because it exists): region1 r(y,interaction_D)
  = +0.118520 [+0.061708, +0.174831] (unique_T 38.28% of R2_full);
  region2 = −0.076474 [−0.138062, −0.017321] (unique_T 66.00% of
  R2_full); region3 = +0.013909 [−0.045612, +0.071917] (unique_T
  0.10% of R2_full); region4 = +0.033255 [−0.019891, +0.086427]
  (unique_T 99.66% of R2_full; region4's ESM zero-order r1 = −0.0020,
  matching [AD8]'s region-4 pattern).
- Script footer: "SCRIPT 104 DONE  (54.7s)  A1: rank identity
  CONFIRMED | A2 mechanical case: case (i): BOTH carry independent
  information (both semipartial CIs exclude 0)". LIMITATIONS block
  printed with results (7 numbered items, AGENTS §6) is in the log
  file itself.
- GATE INCIDENT, fully disclosed (troubleshooting rule 2 as applied):
  first smoke run (N_BOOT=300) printed
  "*** G7 FAIL: pooled obs (T=ddg) does not reproduce task81's pooled
  row to <1e-12 — this script's components call differs from AD8's.
  Stop." → EXIT=1. I stopped and diagnosed rather than raising N or
  changing the rule: recomputing all nine obs values showed they match
  the task81 CSV to ≤ 8.847e-17 (e.g. R2_full computed
  0.010406889250823588 vs CSV 0.0104068892508235, diff 8.847e-17) —
  the failure was that my CODE implemented the obs check as ALSO
  comparing lo/hi CI columns, which at N_BOOT=300 legitimately differ
  from the CSV's N_BOOT=10000 CIs. The pre-registered docstring rule
  is "obs-always, CI-only-when N_BOOT==10000 (smoke prints DEFERRED)";
  the code was corrected to obey that pre-registered rule (rule itself
  unchanged — the correction is recorded in the script's own source as
  a disclosed note). Smoke run 2 then passed; the full run's G7 CI
  check passed at <1e-12, confirming no machinery deviation existed.
  No threshold, N, or rule was altered to force a pass.

Verdict: PASS — the corrected decomposition, reported exactly as
computed: on the same matched frame and same machinery as [AD8]
(bitwise-faithful by G7), swapping the constant-offset pred_eb for
interaction_D changes the picture from "both independent" to:
interaction_D's zero-order with own e.b is AD4's null (+0.015350
[−0.015245, +0.045252], spanning 0), and its unique contribution in
the joint model is 2.59e-05 = 0.43% of R2_full (11.0% of its own
zero-order R2), with the full model explaining 0.60% of own_e_b rank
variance. ESM-2's shift keeps 96.1% of R2_full. The task's expected
outcome (little or no unique variance for ThermoMPNN-D) is what the
numbers show; the framing was not adjusted in either direction. Note
the mechanical case-(i) label fires as the pre-registered structural
analysis predicted — see "unexpected" below.

Files created/modified: NEW `scripts/104_a1_a2_thermompnn_interaction_decomposition.py`;
NEW `data/processed/task104_joint_decomposition_interactionD.csv` (5
scope rows: pooled + regions 1–4). Read-only inputs: task_V2, Z1,
task77, task81 CSVs. Ephemeral run log a104_full.log (temp dir). No
existing script, lib module, prior log, or result CSV modified.

Anything unexpected or worth flagging:
- **Structural finding that contradicts a settled prior verdict (rule
  6: logged here, prior logs NOT edited, flagged):** scripts/81/[AD8]'s
  pre-registered decision rule ("semipartial CI excludes 0 ⇒ carries
  independent information") cannot meaningfully fail — unique_T and
  unique_E are perfect squares over a positive denominator
  (`unique_T = (r2 − r1·r12)²/(1 − r12²) ≥ 0`), so their percentile
  CIs never extend below 0 for ANY predictor. [AD8]'s own output
  already shows it: its p printed `<1/N` (zero of 10,000 draws ≤ 0),
  and script 104's run reproduces p = 0.0 for both components. AD8's
  headline "BOTH carry independent information (case i)" is therefore
  a structurally near-guaranteed label whose evidential content was
  its magnitudes (unique_T 42.8% of R2_full then), not the CI
  exclusion. This strengthens, not weakens, the write-up correction:
  the write-up cited that case-(i) verdict as confirmation. Flagged
  for the user; DEEPDIVE_LOG and PROJECT_SUMMARY_FINAL are untouched.
- Region1 (CI excludes 0, +0.119) vs region2 (−0.076): interaction_D's
  zero-order with own e.b is regionally heterogeneous while pooling to
  a null. Descriptive only, no decision rule attached (pre-registered),
  no multiplicity claim made — flagged so a later task does not
  promote it to a finding without a pre-registered test.
- The r2 CI cross-check landed close but not identical to AD4's
  (−0.0152/+0.0453 vs −0.0166/+0.0465) — expected draw-mechanics
  difference (rng.choice vs rng.integers), printed as descriptive, not
  gated, as pre-registered.
---

## [A3] — Corrected severity-baseline framing: ThermoMPNN raw ddG(v) as a severity predictor (quote-ready paragraph + table row)

Status: PASS (deliverable is the text below; per rule 4's logged
assumption, no write-up file was edited — no task authorizes one)

Time started / finished: 22:08:30 / 22:16:00

What I did:
- Pulled the existing severity-baseline table's exact rows from its
  source CSV (`data/processed/task_AB2_proteingym_model_comparison.csv`,
  read fresh — 96 model rows, every row carries `own_n = 10757`,
  `own_n_positions = 654`), plus the one shift row in that same table
  (`REF_delta_ESM_our_run`).
- Pulled ThermoMPNN's row values from `[V4]`'s entry (SESSION_LOG
  L2406: rho + CI + p + n) and the full-precision value from Z1's CSV
  as quoted in ad8_full.log G2/G3 (`-0.07329934766090093`), plus V4's
  n-reconciliation (SESSION_LOG L2409–2412).
- Verified the sign-orientation statement against a labeled
  pre-registered source (AGENTS §5) instead of assuming: script 77's
  docstring L124–127, and the convention-pinning at
  DISATTENUATION_LOG L187 / L210.

Actual output (verbatim sources feeding the deliverable):
- AB2 CSV rows read fresh (own target, signed, position-cluster
  bootstrap N=10,000): Site_Independent own_rho 0.063966
  [0.037646, 0.090564] p=0.0; ESM1v_single 0.067808
  [0.040928, 0.095568] p=0.0; GEMME 0.075770 [0.049144, 0.102862]
  p=0.0; ESM2_650M 0.085391 [0.058861, 0.112294] p=0.0; and the
  table's own shift row REF_delta_ESM_our_run −0.088118
  [−0.117333, −0.059511]; all own_n=10757, own_n_positions=654.
- `[V4]` SESSION_LOG L2406: "V4 primary: pred_eb vs own e.b
  rho=-0.0733 CI=[-0.1021,-0.0437] p=<0.0001 n=9595"; full precision
  −0.07329934766090093 (ad8_full.log G2: "Thermo
  -0.07329934766090093"; G3: "(-0.0732993476609009) — two independent
  runs agree"); V4's n-reconciliation L2409–2412: "10,141 matched rows
  − 546 without own e.b = 9,595 (global own-e.b missingness is
  587/11,344 = 5.17%; 546/10,141 = 5.38% among matched — a 0.2 pp
  difference, arithmetic closes, no unexplained rows)".
- Sign orientation, script 77 L124–127 (pre-registered): "EXPECTED
  SIGN: NEGATIVE - interaction_D is in stability units (positive =
  more destabilizing than additive) while own_e_b is fitness-scale
  epistasis; the project's own additive reference has this orientation
  (AA4: ThermoMPNN signed rho -0.0733 vs own_e_b)."
- Convention pin, DISATTENUATION_LOG L187: "the severity-baseline
  table (Site_Independent, GEMME, ESM2_650M, … all positive) correlates
  **raw WT-background scores** against e.b; the headline −0.088
  correlates the **delta/shift** against the same e.b vector. … their
  signs are never compared without naming the statistic." (L210's
  four-part naming rule: predictor statistic, target, signed vs
  absolute, n.)

Deliverable A3a — quote-ready paragraph (corrected framing):

> **Correction to the prior write-up (not a new finding).** ThermoMPNN's
> raw single-mutant stability score ddG(v) correlates with own e.b at
> ρ = −0.0733 [−0.1021, −0.0437], p < 0.0001, n = 9,595 / 586
> positions — a WT-background **stability-severity** statistic on
> ThermoMPNN's own maximal frame (V2 = 10,141 joined rows − 546
> without own e.b; the 59 atlas positions without chain-A coordinates
> are structurally absent), and it belongs in the severity-baseline
> table alongside Site_Independent (+0.064), ESM1v_single (+0.068),
> GEMME (+0.076), and ESM2_650M (+0.085) — all on that table's frame
> of n = 10,757 / 654 — **as a severity predictor, not as an
> interaction comparator.** The prior write-up's statement that
> ThermoMPNN "carries genuinely independent information from ESM-2's
> shift, confirmed via a joint statistical model"
> (PROJECT_SUMMARY_FINAL.md L212–215) was an error: that model's Thermo
> side was pred_eb = ddG(v) + ddG(A222V), a single constant added to
> every row, rank-identical to ddG(v) itself — disclosed already in
> [V4]'s own entry and in scripts/81's gate G4, and re-confirmed
> exactly (rankdata equality at every row) by scripts/104. ThermoMPNN's
> magnitude is comparable to the table's rows; its sign is opposite
> theirs because its units are stability (positive = more
> destabilizing, script 77's pre-registered orientation) while the
> ProteinGym rows are likelihood-scale — per the project's convention
> pin, signs are never compared without naming the statistic. This
> reclassification is a correction of an error in the prior write-up,
> not a new finding: every quantity in this paragraph was already
> computed and logged before this session ([V4], 2026-09-23; Z1; AD8).

Optional add-on sentence (this session's new corrected joint model,
labeled as such if quoted):
> With the genuinely non-degenerate interaction_D in that same joint
> model, ThermoMPNN-D's unique contribution is 0.43% of R²_full
> (2.59e-05; scripts/104, A2) — i.e. the corrected decomposition shows
> essentially no independent interaction information.

Deliverable A3a — table row, Block-B style (source column as in
DISATTENUATION_LOG's Block B):

| # | predictor (statistic named) | own e.b, signed (own target) | frame | source |
|---|---|---|---|---|
| B-new | ThermoMPNN **raw ddG(v)** (WT-background stability severity; NOT an interaction term; rank-identical to pred_eb) | **−0.07329934766090093** [−0.1021, −0.0437], p < 0.0001 | n = 9,595 (586) — ThermoMPNN's own maximal frame; table's ProteinGym rows are n = 10,757 (654); frames differ, do not read the rows as same-n | V4: SESSION_LOG L2406 (CI/p/n, 4-dp); full precision: Z1 CSV via ad8_full.log G2/G3; rank identity: scripts/104 A1 |

Verdict: PASS — corrected framing produced and grounded line-by-line:
ThermoMPNN raw ddG(v) is reclassified to the severity-baseline table
(comparable magnitude to Site_Independent…ESM2_650M, opposite sign
convention, frame caveat stated), the paragraph states plainly that
this is a correction of a prior write-up error and not a new finding,
and the sign statement is sourced to a pre-registered orientation
(script 77) plus the project's own convention pin (L187/L210) rather
than assumed.

Files created/modified: nothing modified (text deliverable lives in
this log entry). Read-only: `data/processed/task_AB2_proteingym_model_comparison.csv`,
SESSION_LOG.md, DISATTENUATION_LOG.md, scripts/77 docstring,
PROJECT_SUMMARY_FINAL.md, ad8_full.log.

Anything unexpected or worth flagging:
- The severity table itself already contains the project's own shift
  row (`REF_delta_ESM_our_run`, −0.088118) — useful anchor: the
  corrected story is "one shift row + severity rows incl. ThermoMPNN",
  and A3's row would sit with the severity rows, not the shift row.
- The user (or a later authorized session) still has to APPLY this
  correction to PROJECT_SUMMARY_FINAL.md L210–215; the file currently
  still contains the erroneous sentence (verified fresh this session).
---

## [D1] — The five input quantities (r_XX, r_YY, r_XY, Var(X), Var(Y)) re-derived from the five ESM-1v checkpoints' own score CSVs

Status: PASS (all gates G0–G4)

Time started / finished: 22:16:00 / 22:31:53 (same script execution as
D2 — `scripts/105_d1_d2_difference_score_reliability.py`; smoke
N_BOOT=300 then full N_BOOT=10000, both EXIT=0; D1 quantities are
N-independent)

What I did:
- Located the single consistent source the task mandates: the five
  checkpoint CSVs `data/processed/task_AC4_esm1v_member{1..5}_scores.csv`
  (12,446 rows each; `wt_logodds` = X, `av_logodds` = Y,
  `delta` = Y − X), joined to the analysis base exactly as scripts/89
  (R4 discipline): `task32_analysis_table.csv` dropna(own_e_b,
  GI_folinate_independent, delta_esm) → 10,757 / 654, left-merge each
  member on (position, mut_aa) validate 1:1.
- Wrote script 105 with its pre-registered docstring (gates G0–G5,
  the exact Lord formula, both scale constructions, aggregation rules,
  limitations) BEFORE any run; smoke then full.
- Re-derived every quantity fresh from these CSVs — nothing reused
  from prior contexts (r_XX's 0.8826 gate, r_YY and r_XY fresh;
  0.999636's provenance re-confirmed, not borrowed).

Actual output (verbatim, d105_full.log / identical in smoke):
- G1 accounting + join:
  "G1 base: task32 11344 -> dropna(own_e_b, GI, delta_esm) 10757 rows
  / 654 positions (== 10757/654) | member CSVs have 12446 rows each ->
  1689 rows outside the analysis base (task32's set filtering,
  accounted, not dropped silently)"
  "G1 PASS: R4 join — all 5 members cover the base exactly (10757
  rows / 654 positions, 1:1, wt_aa labels match)"
- G4 (sign convention pinned against the files, AGENTS §5):
  "G4 PASS: all 5 members: delta == av_logodds - wt_logodds on all
  12446 rows (max|diff| < 1e-9) — D = Y - X sign convention pinned
  against the files"
- **r_XX** (WT arms, median of 10 pairwise Spearman) — GATE:
  "r_XX (WT arms, 10 pairwise Spearman): min=0.859689 median=0.882637
  max=0.890106"
  "all 10: [0.859689, 0.8672, 0.872961, 0.875035, 0.882602, 0.882672,
  0.886683, 0.886791, 0.889719, 0.890106]"
  "G2 PASS: r_XX median == 0.882637 (6 dp) — reproduces AC4d/R7's
  existing 0.8826 figure (CALIBRATION_LOG L439; script 97 G4's
  0.8826369)" — reproduces EXACTLY the prior min/median/max triple.
- **r_YY** (A222V arms, same procedure — FRESH):
  "r_YY (A222V arms, 10 pairwise Spearman — FRESH): min=0.859840
  median=0.882150 max=0.890123"
  "all 10: [0.85984, 0.867054, 0.871908, 0.873918, 0.881912, 0.882388,
  0.885802, 0.885815, 0.888311, 0.890123]"
  → r_YY ≈ r_XX (0.882150 vs 0.882637): the two arms are almost
  equally unreliable across checkpoints.
- **r_XY** (per-checkpoint within-model Spearman(X,Y) — FRESH, then
  range + median as required):
  "checkpoint 1: spearman=0.9993872509298699 pearson=0.999346667036114"
  "checkpoint 2: spearman=0.9994196890689375 pearson=0.999405084638616"
  "checkpoint 3: spearman=0.9992668139016031 pearson=0.99918029377409"
  "checkpoint 4: spearman=0.9992208479893161 pearson=0.999072331222566"
  "checkpoint 5: spearman=0.9995565569761303 pearson=0.9995699602636872"
  "range [0.9992208479893161, 0.9995565569761303]
  median=0.9993872509298699  (formula uses the median)"
  Provenance re-confirmed (task D1a): "of the previously-cited
  0.999636: re-confirmed as C1d (OVERNIGHT_LOG L455-465) = ESM-2's
  Spearman(esm2_score_a222v_bg, esm2_score) n=10,757 — a different
  model, NOT one of these five checkpoints; re-derived here instead of
  reused". (Read directly: OVERNIGHT_LOG L461–462 "C1d DIRECT:
  S(v|A222V) vs S(v|WT) / Spearman = 0.999636 (n=10757)".)
- **Var(X), Var(Y)** (per checkpoint + averages, both scales, no
  Var(X)=Var(Y) assumption anywhere):
  "checkpoint 1: raw VarX=17.954970 VarY=17.773687 (d=-0.181283) |
  rank VarX=9642754.000000 VarY=9642754.000000 (d=+0.000000)"
  (ck2 raw d=−0.248553, ck3 −0.118307, ck4 −0.261023, ck5 −0.179640;
  rank d ≤ 4.6e-05 everywhere)
  "averages: raw VarX=17.726776 VarY=17.529015 | rank
  VarX=9642753.999991 VarY=9642753.999981"
  "Var(X) vs Var(Y) statement: on the RAW scale they differ by
  1.1156% of mean Var(X); on the RANK scale by 0.000000% (ties only —
  ranks of n values without ties have identical variance by
  construction). Var(X) = Var(Y) is NOT assumed anywhere in the
  formula (full expression used, no simplification)."
- G3 (the D2d comparator re-derived live):
  "G3 PASS: observed delta agreement (median of 10 pairwise Spearman
  on delta, same base/convention) == 0.084365 (6 dp), full precision
  0.08436481140085886 — re-derived live, not taken on faith. Its CI
  [+0.052159, +0.122589] is QUOTED from T5a/T4a (DISATTENUATION_LOG
  L346 / PROJECT_SUMMARY_FINAL L81), NOT recomputed here."

Verdict: PASS — all five quantities defined and re-derived from one
consistent source (the five checkpoints' CSVs on the project base),
with the mandated 0.8826 reproduction as a passing gate (exact
min/median/max match), r_YY/r_XY fresh, Var(X)/Var(Y) reported
per-checkpoint and averaged on both scales with an explicit
Var(X)≈Var(Y) statement, and 0.999636's provenance pinned to C1d/ESM-2
rather than reused. Interpretation assumption logged (rule 4): the
formula's inputs are computed in two pre-registered consistent
constructions — R (rank scale, primary: satisfies all three mandated
Spearman r's AND D2a's identity simultaneously) and W (raw Var +
Pearson, the classical Lord instantiation) — the mixed scale is
deliberately not used because its identity gate fails by algebra
(Spearman-vs-Pearson gap 4.06e-05 printed as information); both
constructions reported regardless of outcome.

Files created/modified: NEW `scripts/105_d1_d2_difference_score_reliability.py`;
NEW `data/processed/task105_difference_score_reliability.csv` (86 tidy
rows). Read-only: task32_analysis_table.csv, the five member CSVs,
CALIBRATION_LOG.md, OVERNIGHT_LOG.md, DISATTENUATION_LOG.md,
PROJECT_SUMMARY_FINAL.md. Nothing existing modified.

Anything unexpected or worth flagging:
- The previously-cited 0.999636 turns out to be ESM-2's within-model
  arm correlation (C1d), while these five ESM-1v checkpoints give
  0.99922–0.99956 (median 0.99939) — close but not the same number;
  anyone quoting "0.9996" as if it were an ESM-1v figure would be off.
  Logged, not corrected anywhere (no write-up cites it that way yet).
- On the rank scale Var(X) and Var(Y) are identical to ~1e-11
  (construction R), i.e. the task's "would a simplified formula have
  been valid" answer is: on ranks yes (ties only), on raw scores no
  (1.1% mean difference) — full formula used regardless.
---

## [D2] — Lord's difference-score reliability formula: point prediction, identity gates, bootstrap, prediction-vs-observation

Status: PASS (gates G5 + D2a identities all hold; D2b's prediction is
OUTSIDE [0,1] as the task anticipated — reported exactly as computed,
never clipped; one disclosed print-bug fix in an informational line,
details below)

Time started / finished: 22:16:00 / 22:31:53 (same script executions
as D1: smoke N_BOOT=300 EXIT=0, then full N_BOOT=10000 EXIT=0 in
75.6s, foreground)

What I did:
- Implemented the task's formula verbatim in `lord()` (no
  simplification, no Var(X)=Var(Y) shortcut): numerator
  r_XX·VarX + r_YY·VarY − 2·r_XY·√(VarX·VarY), denominator
  VarX + VarY − 2·r_XY·√(VarX·VarY).
- G5/D2a: identity check Var(D) == VarX+VarY−2·r_XY·√(VarX·VarY)
  per checkpoint, per construction, tolerance fixed pre-run at
  relative 1e-12 ("numerical precision" at these magnitudes).
- D2b: point prediction with aggregated inputs exactly as D1a
  specifies (medians for r's, means for Vars), both constructions,
  full precision printed, out-of-range reported with the task's
  pre-provided ill-conditioning diagnostic, plus a labeled
  per-checkpoint-r_XY sensitivity line.
- D2c: position-cluster bootstrap (654 clusters, seed 0, N_BOOT env;
  ALL five inputs recomputed in every draw — re-derivation null,
  ranks recomputed per draw), summarizing finite draws' percentiles,
  min/max, fraction negative, fraction in [0,1]. No winsorization.
- D2d: side-by-side prediction vs observation with plain verdict.

Actual output (verbatim, d105_full.log):
- G5/D2a identities:
  "checkpoint 1: R(rank) rel-dev=9.390e-14 | W(raw) rel-dev=4.535e-15
  OK" / ck2 2.810e-13 | 2.064e-14 / ck3 8.426e-14 | 4.471e-14 /
  ck4 3.837e-14 | 3.351e-14 / ck5 1.789e-13 | 1.414e-14
  "G5 PASS: D2a identities hold to numerical precision (rel < 1e-12)
  on BOTH constructions for all 5 checkpoints — denominator
  trustworthy."
  "information: Spearman r_XY median 0.9993872509298699 vs Pearson
  r_XY median 0.999346667036114 — the gap 4.058e-05 is why a mixed
  scale (Spearman r + raw Var) cannot satisfy this identity and is
  not used as a prediction (pre-registered rule)."
  "information: aggregate-inputs (median r_XY, mean Var's)
  denominator=11817.177094 vs mean Var(D_rank)=12145.400177
  rel-dev=2.702e-02 (median-vs-per-checkpoint residual; exact identity
  is the per-checkpoint statement above)"
- **D2b point predictions (the headline, OUTSIDE [0,1], unclipped):**
  "[R (PRIMARY, rank scale)]
     inputs: r_XX=0.8826369680851056 r_YY=0.8821503142468713
     r_XY=0.9993872509298699 VarX=9642753.999990705
     VarY=9642753.999981407
     numerator  = -2256281.1970469505
     denominator= 11817.177093967795   (== Var(Y-X);
     1 - r_XY = 6.127491e-04)
     reliability(D) = -190.9323334249339   -> OUTSIDE [0,1]"
  "[W (secondary, raw+Pearson)]
     inputs: r_XX=0.88008478166905 r_YY=0.8795826572713766
     r_XY=0.999346667036114 VarX=17.726776378131035
     VarY=17.529015098411556
     numerator  = -4.212919611872362
     denominator= 0.02358806661578683   (== Var(Y-X);
     1 - r_XY = 6.533330e-04)
     reliability(D) = -178.60385424945227   -> OUTSIDE [0,1]"
  Both followed by the pre-provided diagnostic: "the formula is
  numerically ill-conditioned specifically because r_XY is very close
  to 1 — the denominator Var(X)+Var(Y)-2*r_XY*sqrt(Var(X)*Var(Y)) =
  Var(Y-X) collapses toward zero when the two arms are nearly
  rank-identical... Reported exactly as computed; NOT clipped".
  Sensitivity (each checkpoint's own r_XY, construction R):
  "-190.93, -201.66, -159.40, -149.94, -264.21" — every variant far
  outside [0,1].
- **D2c bootstrap (N_BOOT=10000, seed 0):**
  "[R PRIMARY (rank scale)] n_draws=10000 finite=10000 nan=0 inf=0"
  "percentiles of finite draws: p2.5=-301.758 p25=-231.479
  p50=-198.498 p75=-170.835 p97.5=-130.314"
  "min=-384.404 max=-96.1341 | fraction negative=1.0000 | fraction
  in [0,1]=0.0000"
  "[W secondary (raw+Pearson)] n_draws=10000 finite=10000 nan=0
  inf=0"
  "percentiles of finite draws: p2.5=-293.847 p25=-222.565
  p50=-189.681 p75=-162.157 p97.5=-122.169"
  "min=-373.536 max=-89.9166 | fraction negative=1.0000 | fraction
  in [0,1]=0.0000"
- **D2d prediction vs observation:**
  "[R PRIMARY] forward prediction = -190.9323334249339 (OUTSIDE
  [0,1]); bootstrap interval [p2.5=-301.758, p97.5=-130.314] (100.0%
  of draws negative, 0.0% in [0,1])"
  "observed delta reliability = 0.08436481140085886 (re-derived, G3)
  with quoted CI [0.052159, 0.122589] (T5a/T4a)"
  "observed value inside the prediction's bootstrap interval: False"
  "verdict: INCONSISTENT — prediction outside [0,1], observed outside
  the prediction's empirical interval"
  "[W secondary] forward prediction = -178.60385424945227 (OUTSIDE
  [0,1]); bootstrap interval [p2.5=-293.847, p97.5=-122.169] (100.0%
  of draws negative, 0.0% in [0,1]) ... verdict: INCONSISTENT ..."
- Footer: "SCRIPT 105 DONE (75.6s) r_XX=0.882637 | r_YY=0.882150 |
  r_XY(med)=0.999387251 | pred_R=-190.9323334249339 |
  observed=0.084365"; 6-item LIMITATIONS block printed with results
  (shared-error assumption violation first).
- DISCLOSED incidents (no gate, threshold, N, or rule changed):
  (a) Informational-line print bug: smoke run 1's
  "aggregate-inputs ... vs mean Var(D_rank)" line computed the formula
  NUMERATOR instead of the DENOMINATOR (its label), yielding a
  meaningless rel-dev 1.868e+02. Fixed to the denominator before the
  full run (now rel-dev 2.702e-02, a legitimate median-vs-per-
  checkpoint residual); the fix is recorded in the script source as a
  disclosed note. G5's per-checkpoint gates passed before and after.
  This was a labeled-information correctness fix, not a check
  modification — flagged here so the record shows both versions.
  (b) Cosmetic: a numpy scalar printing as `np.float64(...)` wrapped
  in float() in the same edit.

Verdict: PASS — the task's anticipated scenario is what the data
gives, reported exactly: **the classical forward prediction of the
difference score's reliability is ≈ −191 (rank/mandated-Spearman
construction) and ≈ −179 (raw/Pearson construction), both far OUTSIDE
[0,1], while the actually observed cross-checkpoint delta agreement is
+0.084365 [+0.052159, +0.122589]** — INCONSISTENT on both
constructions. D2c's answer to "is it fair to quote a single
predicted number?": the bootstrap is not sign-unstable — 10,000/10,000
draws negative, 0% in [0,1] for both constructions — so the negative
prediction is robust, not a fluke of inputs; but the magnitude is
inherently ill-conditioned (denominator ≈ 1.2e4 against a numerator ≈
−2.3e6 on the rank scale; 1−r_XY ≈ 6e-04), so quoting the specific
value −190.9 as if it were meaningful precision would be wrong; the
reportable content is: sign negative, magnitude ≫1, inconsistent with
observation. Mechanistically (printed as limitation 1, not repaired):
the classical formula assumes uncorrelated errors in X and Y, but
both arms come from the same checkpoint on the same rows — shared
checkpoint noise makes r_XY (0.9994) ≫ r_XX/r_YY (0.88), which is
exactly the condition that drives the numerator negative; the formula
is being asked a question its assumptions do not cover, and it says
so by returning −191 rather than a plausible-looking 0.08.

Files created/modified: NEW `scripts/105_d1_d2_difference_score_reliability.py`
(2 disclosed post-smoke edits to an informational print + cosmetic);
NEW `data/processed/task105_difference_score_reliability.csv`.
Read-only inputs as in D1. No existing script/lib/log/result modified.

Anything unexpected or worth flagging:
- Both constructions (rank and raw) land at nearly the same absurd
  magnitude (−191 vs −179), so the pre-registered scale-sensitivity
  concern did not change the qualitative verdict — reported as such,
  both shown side by side anyway.
- The bootstrap never once crossed into [0,1] (0.0000) — the task's
  "numerically ill-conditioning" explanation is confirmed by the
  draws themselves, not just the point value.
- D2c's distribution is wide in absolute terms (p2.5 −301.8 to
  p97.5 −130.3) — a ~2.3x spread — so while the SIGN is certain, any
  single quoted magnitude carries that much resampling uncertainty
  on top of the conditioning problem.
---

## [C1] — Shift-side mechanism-only null: what a zero-interaction generative mechanism mechanically produces for the shift statistic

Status: PASS (all gates G0–G3, V1–V4, I1; zero planted interaction
VERIFIED before the statistic was computed, as the task requires).
The C1d verdict fires the pre-registered SMALL branch: −0.088 is an
order of magnitude below the mechanical reference — and opposite in
sign.

Time started / finished: 22:33:00 / 22:52:30 (script 106 written
~22:45, smoke N_BOOT=300 EXIT=0, two cosmetic post-smoke edits at
22:51:51, full N_BOOT=10000 EXIT=0 in 27.9s, foreground)

What I did:
- **C1a (read before writing):** read script 101 (Y2) in full first —
  its generative approach (real f_bar pool from
  task32_analysis_table.csv, `f_wt = median(f_bar_wt)`, iid pairs via
  `rng.choice`, multiplicative TRUE model, no interaction, identity
  check, position-cluster convention where applicable) — plus
  `scripts/lib/own_context.py` in full (the real own_e_b path:
  `expected(c) = sm(c)·a222v_line(c) [+ correction]`,
  `e_b = wls_line(resid, m_se, CONCS, valid)[0]`, >2-missing → NA),
  `stats_ext.rebuild_interaction_fit` (returns `w`, `i222` = the
  p.Ala222Val row, `M_se`, `correction`), and
  `stats.position_cluster_bootstrap` (re-derivation per draw,
  sign-crossing two-sided p). Only then wrote
  `scripts/106_c1_mechanism_only_null_shift.py` with a fully
  pre-registered docstring (**C1e**): frame, generative model, the
  two-draw design, V1–V4 thresholds, bootstrap, and the exact
  three-way verdict rule were all fixed before the first run.
- **C1b design:** for each of the 10,757 frame rows, `f(v|WT)` and
  `f(v|A222V)` = two SEPARATE `rng.choice` draws (seed 0) from the
  SAME pool of 11,344 real f_bar values — identical model, no shared
  noise, no term referencing both draws; arms share ONLY the
  severity-to-fitness map. Zero-planted-interaction VERIFICATION
  ordered before the statistic: V1 empirical arm independence (gate
  |Spearman| < 0.05, pre-registered ~5.2σ rationale), V2 structural
  (background = ONE global constant line, printed), V3 construction
  identity (gate < 1e-9), V4 NaN accounting (gate == 0). Any V-fail
  ⇒ exit(1), no threshold change.
- **C1c construction:** `shift_sim = f_av − f_wt` (mirrors delta_esm
  exactly); e.b-analog through the REAL `own_context.fit_interaction`
  code path with the pipeline's fixed parts reused real (CONCS, real
  per-point `M_se`, validity/NA logic, the real global A222V line
  b_A/r_A, the real two-pass correction (cb, cr)) and only the two
  variant-level arms simulated; Y2's noise structure (no
  per-concentration term — disclosed consequence: the WLS intercept
  reduces analytically to `f_av − b_A·f_wt − cb(f_wt)`, which V3
  verifies). Statistic = Spearman via the standard
  position_cluster_bootstrap (654 clusters, N_BOOT env, seed 0),
  with identity check I1 (bootstrap observed == direct _spearman).
- **C1d:** re-derived the real anchor live (G2, gated 1e-9 against
  the canonical −0.08811806424891734, three prior sources agreeing:
  CALIBRATION_LOG L290 / CLOSEOUT_LOG L1228 / DEEPDIVE_LOG L3019),
  computed BOTH CIs fresh with the same convention, and applied the
  pre-registered three-way magnitude rule (BELOW ⇒ SMALL, INSIDE ⇒
  COMPARABLE, ABOVE ⇒ LARGE), printing the sign contrast as its own
  observation.

Actual output (verbatim, c106_full.log):
- Gates:
  "G0 PASS: all 4 inputs present"
  "G1 PASS: script-33 frame = 10757 rows / 654 positions; all
  hgvs_pro map to raw fit rows"
  "G2 PASS: real anchor reproduced live: rho(delta_esm, own_e_b) =
  -0.08811806424891734 == -0.08811806424891734 (tol 1e-9; task
  quotes -0.088 at 4 dp)"
  "G3 PASS: f_bar pool n=11344 range=[0.0000, 1.9354] non-negative;
  f_wt (median f_bar_wt)=0.8177 printed for Y2 context"
- **Zero planted interaction (verified BEFORE the statistic):**
  "generator: two SEPARATE rng.choice calls over the same pool; no
  term references both draws; arms share ONLY the
  severity-to-fitness map (pool of 11344 real f_bar values, Y2's
  generative base)"
  "mean/median: f_wt 0.598375/0.650647 | f_av 0.595509/0.649672
  (identical-model sanity)"
  "V1 Spearman(f_wt, f_av) = -0.003307496960482229 (gate: |rho| <
  0.05)" → "V1 PASS: arms independent — no planted interaction"
  "V2 structural: background enters ONLY via ONE GLOBAL constant
  line — p.Ala222Val row index 3010, b_A=0.46891682222397274,
  r_A=0.0016033484529922113; no per-variant background array exists
  in the generator (shared constant = main effect, not interaction)
  — PASS"
  "V4 accounting: eb_analog finite = 10757/10757" → "V4 PASS"
  "V3 identity: max|eb_analog - (f_av - b_A*f_wt - cb(f_wt))| =
  2.850e-14 (gate < 1e-09)" → "V3 PASS: the real wls_line path
  reproduces the analytic intercept exactly — eb_analog = f_av -
  0.468917*f_wt - cb(f_wt), i.e. the mechanical coupling between
  shift and e.b-analog is fully characterized"
  (5 example rows printed: e.g. "row 0: f_wt=0.577247
  f_av=0.672677 shift=+0.095430 eb_analog=+0.436181
  analytic=+0.436181")
- **Statistics (both position-cluster, N_BOOT=10000, seed 0):**
  "I1 PASS: bootstrap observed == direct Spearman
  (0.9366244249321943), identity check inside the null's own output"
  "[MECHANISM-ONLY (sim shift vs sim e.b)] rho=0.9366244249321943
  CI [0.933389201160778, 0.9396189771832062] p_boot=<1.0e-04
  (n=10757, 654 positions)"
  "[REAL anchor (delta_esm vs own_e_b)] rho=-0.08811806424891734
  CI [-0.1173334458953319, -0.05951138449511738] p_boot=<1.0e-04
  (n=10757, 654 positions)"
  "descriptive sensitivity (correction=None, point estimate only,
  no decision): rho=0.9334164059518051"
- **C1d comparison:**
  "mechanism-only |rho| = 0.9366244249321943, 95% CI on |rho|
  [0.933389201160778, 0.9396189771832062]"
  "real observed |rho| = 0.08811806424891734 (task quotes -0.088;
  canonical -0.08811806424891734)"
  "SIGN observation: mechanism rho = +0.936624 (+pos), real rho =
  -0.088118 (-neg) — sign contrast reported as its own result, not
  folded into the magnitude verdict"
  "VERDICT: −0.088 is SMALL relative to the mechanical reference
  point — the observed |−0.088| sits BELOW the mechanism-only CI"
  "context: Y2's sibling reference (severity predictor vs e.b) =
  +0.590, quoted from the task doc's own Y2 summary — not
  recomputed here"
- "SCRIPT 106 DONE (27.9s) mech_rho=+0.936624 [+0.933389,
  +0.939619] | real=-0.088118 | verdict: SMALL relative to the
  mechanical reference point — the observed |−0.088| sits BELOW the
  mechanism-only CI"
- An 8-item LIMITATIONS block printed with results; items 1–2 quoted
  verbatim: "Zero planted interaction (V1-V2, gated) guarantees the
  SIM has none; it does not prove the real -0.088 is free of
  interaction. This script says what mechanism ALONE can produce." /
  "Shift and e.b-analog share the SAME two arm draws by design —
  that shared-driver structure is the construction under test. In
  reality delta_ESM (ESM scores) and own_e_b (folinate measurements)
  are different channels sharing only true variant biology, so this
  reference is an upper-bound-style stress test of shared-driver
  coupling, not a like-for-like null of the two real pipelines."
- DISCLOSED post-smoke edits (cosmetic only; no gate, threshold, N,
  or rule changed): (a) a `warnings.filterwarnings("ignore",
  message="Mean of empty slice")` for the REAL pipeline's pre-existing
  nanmean warnings on all-NaN rows (same code path scripts 101/33
  emit; noted in-script as cosmetic), (b) two `float()` wrappings so
  CIs print as plain floats instead of `np.float64(...)`. Gates
  identical before and after; smoke output already showed every gate
  passing.

Verdict: PASS — **the mechanism-only reference for the shift
statistic is |ρ| = 0.9366, 95% CI [0.9334, 0.9396]** (p < 1e-4),
computed with zero planted interaction verified by four gates
BEFORE the statistic was read. Placed against the real anchor
(re-derived live: −0.08811806424891734, CI [−0.1173, −0.0595], fresh
same-convention bootstrap): **−0.088 is SMALL relative to this
mechanical reference point** (observed magnitude sits an order of
magnitude below the mechanism-only CI), per the pre-registered
BELOW/INSIDE/ABOVE rule — the missing piece C1d asked for, in the
same spirit as Y2 (+0.590 vs the baseline's 0.064). The sign
contrast is reported as its own result: the construction's artifact
is strongly POSITIVE while the anchor is negative, so whatever
produces the real −0.088, it is not this construction's artifact
direction. Honest caveats (in the script's output, limitation 2):
the reference forces both statistics to share the same two arm
draws (an upper-bound-style stress test of shared-driver coupling),
so it bounds how large the artifact CAN be under a zero-interaction
mechanism rather than reproducing the real two-channel pipeline;
and a magnitude inside the mechanism's range does not certify the
anchor as artifact — it says the anchor's size requires no
interaction to explain. Post-run note, explicitly NOT a gate: the
analytic form from V3 (two affine functions of the same draws with
k ≈ 0.469 + cb′) predicts a Pearson near (1+k)/(√2·√(1+k²)) ≈ 0.94,
consistent with the observed 0.9366 — a retrospective sanity check,
computed after the run, carrying no pre-registered weight.

Files created/modified: NEW
`scripts/106_c1_mechanism_only_null_shift.py` (pre-registered
docstring + gates; 2 disclosed cosmetic post-smoke edits); NEW
`data/processed/task106_c1_mechanism_null.csv` (19 tidy rows).
Read-only: `data/raw/mthfrModel/results/folate_response_model5.csv`,
`phase5_analysis_table.csv`, `own_context_metrics.csv`,
`task32_analysis_table.csv`, scripts/101 (read in full, C1a),
`scripts/lib/{own_context,stats,stats_ext}.py`. No existing
script/lib/log/result modified.

Anything unexpected or worth flagging:
- The mechanism reference (0.937) is far LARGER than Y2's sibling
  0.590 — because here both statistics are literally affine
  functions of the same two draws (V3's identity makes it exact:
  shift = f_av − f_wt, eb = f_av − 0.469·f_wt − cb(f_wt)). Expected
  from the construction, disclosed as an upper-bound-style reading,
  not hidden.
- The real anchor's fresh CI [−0.1173, −0.0595] excludes zero —
  reported as computed here (not quoted from any prior log).
- The verdict direction is the OPPOSITE framing from what a
  "reassuring small artifact" story would want: the artifact ceiling
  is huge (0.94), so an observed 0.088 is comfortably inside what
  zero-interaction mechanism can produce — exactly the honest
  interpretation C1d requested, and no more: it neither certifies
  nor convicts the anchor, it sizes the mechanism's reach.
---

## [B1] — Two omitted Results-surface compilations: source-cited blocks for the 150M-vs-650M non-replication and the five-seed ensemble mean (no new computation)

Status: PASS (both blocks assembled strictly from on-disk source
lines, each line verified this session; zero computation run, as B1
mandates)

Time started / finished: 22:53:00 / 22:55:20 (compilation/reading
only; no script run)

What I did:
- Located and READ every source line first, verifying each file and
  line number exists before citing it (AGENTS §5): for B1a —
  `docs/tasks/review-triage/OVERNIGHT_LOG.md` L1674–1684 + L1692
  (original run), `docs/tasks/comparators-and-consolidation/SESSION_LOG.md`
  L1933–1937 (script 58's own print, verified directly this session),
  `docs/tasks/detection-floor-and-mechanism/DEEPDIVE_LOG.md` L1403–1411
  + L1427–1447 (independent re-derivation with column-identity checks
  + side-by-side numbers + verdict/scope), and
  `docs/tasks/reliability-and-decompositions/VERIFIED_FINDINGS_TABLE.md`
  L68 (row 21, CONFIRMED / SIZE-SENSITIVE); for B1b —
  `docs/tasks/reliability-and-decompositions/RELIABILITY_LOG.md`
  L322–348 (the [A1] entry's verbatim output + verdict + caveat) and
  L1592–1600 (final summary). Confirmed `scripts/58_j2a_proposal_checklist.py`
  and `scripts/90_a1_ensemble_mean_delta.py` both exist.
- Assembled one citation-ready paragraph per result below, carrying
  B1b's existing caveat verbatim.

Actual source lines (verbatim):
- **B1a** — original run, SESSION_LOG L1933–1937 (identical values
  at OVERNIGHT_LOG L1680–1684):
  "PRIMARY Spearman(delta_150M, delta_650M): rho=+0.0978
  CI=[-0.0444,+0.2275] p=0.1540 n=1900 pos=100"
  "  bands: CI_lo=-0.0444  ->  VERDICT: SIZE-SENSITIVE"
  "SECONDARY (descriptive) sign agreement: 53.11% of 1900 rows
  (exact-zero ties excluded: 0)"
  "SECONDARY (descriptive) score rho wt bg: +0.4157 (n=1900)"
  "SECONDARY (descriptive) score rho a222v bg: +0.4098 (n=1900)"
  DEEPDIVE_LOG L1403–1411 (re-derivation, identity-checked first):
  "rows=1900 positions=100"
  "identity  delta150 = score150_bg-score150_wt : max|diff| =
  3.553e-15"
  "identity  delta650 = esm2_bg-esm2_score      : max|diff| =
  1.110e-16"
  "cross-src delta650 vs cached phase5 delta_esm: matched 1743/1900,
  max|diff| = 0.000e+00"
  "delta_150M-vs-delta_655M  rho=+0.0978 CI=[-0.0444,+0.2275]
  p=0.1540 n=1900 pos=100" (the "655M" is DEEPDIVE's own disclosed
  f-string typo; columns are delta150/delta650)
  "raw WT-bg score, 150M-vs-650M  rho=+0.4157
  CI=[+0.2658,+0.5514] p=0.0000 n=1900 pos=100"
  "raw A222V-bg score, 150M-vs-650M  rho=+0.4098
  CI=[+0.2589,+0.5459] p=0.0000 n=1900 pos=100"
  DEEPDIVE_LOG L1431–1447 verdict, quoted for scope: "the two
  checkpoints' raw WT-background scores agree substantially (rho =
  +0.416) while their background-response deltas do not (rho =
  +0.098, CI covering zero, p = 0.154; sign agreement 53.11% ≈
  chance) — the background-response signal (delta) is not a stable
  property of the model family as tested" ... "only two checkpoints
  were compared (ESM-2 150M vs 650M — one family, two sizes) ...
  n = 1,900 variants over the pre-registered 100-position sample; all
  CIs position-clustered."
- **B1b** — RELIABILITY_LOG L323–334 (verbatim run output):
  "PRIMARY: rho(delta_ens, own_e_b) = −0.028508
  CI=[−0.056495, −0.000239] p_boot=0.0484 (position-cluster,
  N_BOOT=10000, seed=0)"
  "identity: all+1 == obs (−0.028507550626), all-1 == -obs
  (+0.028507550626)  -> OK"
  "observed=−0.028508  null mean=+0.0002  sd=0.0142  p=0.0442"
  "null-centring: mean IS consistent with zero (3 SE)"
  "context: |observed|=0.028508 vs mean |single-member rho|=0.020962
  -> averaging strengthened the association"
  RELIABILITY_LOG L336–348 verdict + THE CAVEAT to carry forward,
  verbatim: "HONEST-READING CAVEAT: both p-values sit just under 0.05
  (bootstrap CI upper bound −0.000239), so this is a marginal
  detection — it supports the reliability-capped-attenuation framing
  (an ensemble of five still lands at only −0.029) but must not be
  quoted as a strong result. Scope: ESM-1v seed replicates only
  (A3); no ESM-2 implication."
  (Pre-registered prediction components, same entry L309–315:
  "mean single-member rho = −0.015588096"; "Spearman-Brown recompute:
  −0.015588096 * sqrt(5/(1+4*0.084365)) = −0.0301 (task doc's given
  prediction: −0.03)" with r_bar = 0.084365 = AC4 R7's median —
  independently re-derived live this session: script 105 G3 printed
  "0.08436481140085886", a verified cross-check of the input.)

### B1a — citation-ready paragraph (150M-vs-650M delta non-replication)

> To test whether the shift statistic replicates across model scale,
> we scored the pre-registered 100-position sample (1,900
> substitutions, seed 0) with ESM-2 150M and compared its
> background-response deltas against the existing ESM-2 650M deltas
> (the project's delta_ESM). The deltas do not replicate across
> scale: Spearman ρ = +0.0978, position-cluster 95% CI
> [−0.0444, +0.2275], p = 0.1540 (n = 1,900 rows / 100 positions),
> and the two checkpoints' delta signs agree on only 53.11% of rows —
> indistinguishable from a coin flip. The raw per-background scores
> agree substantially more (WT-background ρ = +0.4157, CI
> [+0.2658, +0.5514], p < 0.0005; A222V-background ρ = +0.4098, CI
> [+0.2589, +0.5459]), so the failure is specific to the
> background-response difference, not to the models' overall
> rankings: this is a non-replication of the shift statistic across
> model scale — the background-response signal is not a stable
> property of the model family as tested, and delta-based conclusions
> are properties of the 650M checkpoint as measured. Scope: two
> checkpoints, one family, two sizes; all CIs position-clustered
> (DEEPDIVE_LOG [AC2] L1403–1447; original run SESSION_LOG
> L1933–1937 / OVERNIGHT_LOG L1680–1684; VERIFIED_FINDINGS_TABLE row
> 21, CONFIRMED / SIZE-SENSITIVE).

### B1b — citation-ready paragraph (five-seed ensemble mean, caveat carried)

> Averaging the five ESM-1v seed members' deltas per variant
> (ensemble-mean delta; script 90; n = 10,757 / 654 positions) and
> correlating with measured own-context epistasis gives Spearman
> ρ = −0.028508, position-cluster 95% CI [−0.056495, −0.000239],
> p_boot = 0.0484 (N_BOOT = 10,000, seed 0), with a position-level
> sign-flip null p = 0.0442 (null centered on zero; all+1/all−1
> identity checks exact). This matches the pre-registered
> Spearman-Brown prediction of ~−0.030 re-derived from on-disk
> components (mean single-member ρ = −0.015588096; inter-member delta
> agreement r̄ = 0.084365): averaging five seeds strengthens |ρ| from
> the single-member mean 0.020962 to 0.028508 — a real but modest
> gain consistent with reliability-capped attenuation. Per its own
> log entry's standing caveat, this result is MARGINAL and "must not
> be quoted as a strong result": both p-values sit just under 0.05
> (bootstrap CI upper bound −0.000239), so it is a marginal
> detection supporting the reliability-capped-attenuation framing
> (an ensemble of five still lands at only −0.029). Scope: ESM-1v
> seed replicates only; no ESM-2 implication (RELIABILITY_LOG [A1]
> L322–348; summary L1592–1600; scripts/90_a1_ensemble_mean_delta.py;
> data/processed/task90_a1_ensemble_mean.csv).

Verdict: PASS — both omitted results are surfaced as clean,
citation-ready blocks with exact source lines pulled (every cited
line read and existence-verified this session), no computation
performed, B1b's marginality caveat carried verbatim as mandated, and
no file outside this log modified.

Files created/modified: this log entry only. Read-only:
DEEPDIVE_LOG.md, OVERNIGHT_LOG.md, SESSION_LOG.md, RELIABILITY_LOG.md,
VERIFIED_FINDINGS_TABLE.md, MANUSCRIPT_REVIEW_RESPONSE.md,
scripts/{58,90} (existence check).

Anything unexpected or worth flagging:
- All three independent prior sources for B1a (SESSION_LOG,
  OVERNIGHT_LOG, DEEPDIVE_LOG re-derivation) agree digit-for-digit —
  no reconciliation needed (AGENTS §5's agreement check passes).
- DEEPDIVE L1445's "cross-family stability ... remains BLOCKED
  (disk, see [AC4])" is now STALE: AC4 subsequently ran (the five
  ESM-1v member CSVs and R7/AC4d outputs verified this session, e.g.
  script 105's G2/G3). The paragraph deliberately does not repeat the
  stale BLOCKED status; flagging per rule 6 rather than editing that
  prior log.
- The task-doc premise's example strength for WT-score agreement
  ("rho ~0.8") is NOT what the data show (+0.416); DEEPDIVE
  L1437–1441 already flagged this as a magnitude correction, and the
  paragraph uses the measured +0.416 so the block cannot be misread.
- On the 53.11% sign agreement: no source computed a CI for it — the
  "indistinguishable from chance" reading is the sources' own (and
  the row-level count would be anti-conservative anyway because rows
  cluster within 100 positions); the paragraph states the sources'
  reading and does not invent a new test (no new computation per B1).
---

## [E1] — Precise restatement of Nambiar et al.'s finding, with this project's own extension claim labeled as ours (no computation)

Status: PASS (quote-ready correction text delivered in this log; no
file outside this log touched — same rule-4 assumption as Group A: no
task here authorizes editing `PROJECT_SUMMARY_FINAL.md`, so the user
or a later session applies it)

Time started / finished: 22:56:00 / 23:03:30 (reading + verification
of on-disk sources; no script run)

What I did:
- Read the current write-up sentence being corrected
  (`docs/writeups/PROJECT_SUMMARY_FINAL.md` L164–175) and the
  project's own prior characterization machinery:
  `DISATTENUATION_LOG.md` L392–400 (T6a/T6b/T6c — the full-text and
  code scans), `scripts/96_b4_debias_interaction.py` L64–77 (B4c —
  precedent for labeling the characterization as sourced, not
  re-fetched), `MANUSCRIPT_REVIEW_RESPONSE.md` E1a/E1b spec.
- Verified the qualitative-analysis details DIRECTLY against the
  authors' own released repository on disk
  (`data/external/Epistasis/`, cloned for T6c) rather than trusting
  any summary:
  - Three proteins: `Figures/{tem1.pdb, yap1.pdb, rrm2.pdb}` ✓
  - Heatmap-vs-contact-map pattern matching: their
    `Structure_Figures.ipynb` contains the cells labeled "heatmaps
    and contact map" calling `heatmap_and_contact(epi_untrans,
    dist_mat, ...)` AND `heatmap_and_contact(epi_trans, dist_mat,
    ...)` — i.e. both raw and transformed epistasis heatmaps are
    pattern-matched against the distance/contact matrix ✓ (purely
    visual; no accuracy number is computed by that function's usage).
  - Top-20 circular interaction graphs: cells labeled "circular
    epistasis graphs" calling
    `circular_independent(..., top_n_edges=20)` ✓ — the
    "top-20-pairs circular interaction-graph analysis" is literal,
    present in their own figure code.
  - Their abstract, verbatim from `README.md`: "Raw model scores
    align with residue–residue contacts, indicating that PLMs
    internalize structural proximity. Applying a nonlinear
    transformation to bring model outputs onto the experimental
    scale, however, shifts the signal toward functional couplings
    between distant sites."
  - E1a's negative claim checked repo-side: zero hits for
    stratified/distance-binned/accuracy-vs-distance machinery
    anywhere in `src/` or `Figures/` (the only "binned" hits are the
    nonlinear-fit's binned calibration points — a different thing).
    The full-paper reading behind "no such analysis exists in their
    paper" is the task doc's (reviewer's) — cited as such.
  - T6's already-verified precision facts carried forward: their
    "calibration" = the monotone nonlinear transform ϕ1/ϕ2
    (score-to-fitness mapping, "fit the parameters (b,c) by nonlinear
    least squares"), NOT a measurement-error correction — zero
    occurrences of disatten/reliab\*/measurement error/
    correction-for-attenuation in paper OR code (DISATTENUATION_LOG
    L394, L400); their headline numbers are raw observed Pearson
    after that transformation (0.37 TEM1 / 0.34 YAP1 / 0.26 RRM;
    Table S2 stages TEM-1 0.0918/0.1169/0.3748, YAP1
    0.1770/0.2364/0.3444, RRM 0.1333/0.1508/0.2633); T6b already
    DROPPED any "lands inside their range" comparison from future
    write-ups.

### E1a — citation-ready corrected paragraph (what their paper actually shows)

> Nambiar et al. (bioRxiv 2025.09.14.676130) report a **qualitative,
> visual comparison**, not a quantitative distance-stratified
> accuracy analysis, across three proteins (TEM-1, YAP1, and the
> Pab1 RRM2 domain): they plot model-derived epistasis heatmaps and
> compare their visual pattern against the proteins' structural
> contact maps (their own figure code: `heatmap_and_contact` run for
> both untransformed and transformed epistasis against the distance
> matrix), and they additionally extract the top-20 pairs of each
> epistasis matrix into a circular interaction graph
> (`circular_independent(..., top_n_edges=20)`). The finding they
> draw from those visual comparisons is that **raw, untransformed
> model epistasis visually resembles the contact map — structural
> proximity — while their nonlinear-transformed (calibrated)
> epistasis visually reorganizes around functional/catalytic hubs,
> which they describe as functional couplings between distant sites
> ("long-range functional couplings").** Their calibration is a
> monotone score-to-fitness transformation (ϕ1/ϕ2 fitted by
> nonlinear least squares), not a measurement-error correction —
> the paper and code contain no disattenuation of any kind (verified
> full-text and repository scans). **There is no distance-stratified
> accuracy table in their paper** — no binning of correlation or
> accuracy by structural distance, and their released code computes
> none; their quantitative numbers are overall Pearson correlations
> per protein after the transform (0.37 TEM-1, 0.34 YAP1, 0.26 RRM;
> Table S2: untransformed 0.09–0.18 before it). Any reading of their
> result as "calibration improves accuracy specifically at long
> range, measured by distance bin" overstates what is shown.
> (Sources: task doc E1a; authors' repo `data/external/Epistasis/`
> README + `Figures/Structure_Figures.ipynb`, verified this session;
> DISATTENUATION_LOG L392–400 for the transform/disattenuation facts.)

### E1b — the extension claim, explicitly labeled as THIS PROJECT'S

> **This project's own hypothesis (not a Nambiar et al. claim):**
> the benefit their calibration shows in their setting
> *structurally requires* the many-background, two-path measurement
> design their method was built around — a design a single fixed
> background (MTHFR's A222V) cannot supply. Nambiar et al. neither
> state nor test this requirement: their paper contains no analysis
> of what measurement design the calibration's benefit depends on,
> no single-background ablation, and no statement about clinical
> single-background settings. The claim is our extension of their
> finding — motivated by their three-protein, many-background data
> regime and their symmetrized two-path average (Eqn. 4, as noted in
> our N2 task doc), and by our own observation that our analysis set
> sits overwhelmingly beyond contact range of position 222 — and it
> must be presented as our hypothesis, not as a result of theirs.

The current write-up sentence this corrects
(`PROJECT_SUMMARY_FINAL.md` L164–168, quoted for the record, file
itself untouched): "The comparable method's own published finding is
that raw, uncalibrated model-derived epistasis tracks structural
contact proximity, and only their calibration step reveals long-range
functional coupling — which specifically requires the many-background,
two-path measurement structure their method was built around." —
problems: (i) "tracks" overstates a visual pattern match as a
quantitative tracking result; (ii) the "specifically requires"
clause sits inside a sentence describing "their own published
finding," attributing our hypothesis to them. The two paragraphs
above split it correctly.

Verdict: PASS — E1a states precisely what the paper shows (qualitative
heatmap/contact-map pattern matching + top-20 circular graphs, three
proteins, qualitative reorganization language) and explicitly states
this is NOT a quantitative distance-stratified accuracy table (none
exists in the paper; repo-side check found none either); E1b labels
the "structurally requires" claim as this project's own hypothesis
extending their finding. Every factual element either comes from the
task doc's paper reading (cited as such) or was verified against the
authors' own repository files this session.

Files created/modified: this log entry only. Read-only:
PROJECT_SUMMARY_FINAL.md (L164–175, quoted), DISATTENUATION_LOG.md
(L390–403), DISATTENUATION_AND_LEDGER.md (T6, L137–157),
MANUSCRIPT_REVIEW_RESPONSE.md, scripts/96 (L55–96),
data/external/Epistasis/{README.md, Figures/Structure_Figures.ipynb,
Figures/Epistasis_Figures.ipynb, Figures/Nonlinear_Fits-Figures.ipynb}.

Anything unexpected or worth flagging:
- Their repo gave us MORE direct verification than expected: the
  qualitative-only reading is now confirmed from the authors' own
  figure code (heatmap_and_contact + top_n_edges=20), not just from
  a prose summary — so E1a does not rest on trust.
- The one phrase "long-range functional couplings" as an exact quote
  is the task doc's paper reading; their README's own wording is
  "functional couplings between distant sites" — both are carried in
  E1a with their provenance so no misquote can slip in.
- E1's correction is text-only; the 96.2% figure inside that same
  write-up paragraph is E2's business (next entry), which will give
  the dimer-aware number to sit beside it.
---

## [E2] — Long-range distance figure recomputed on the biological dimer: 96.22% monomer → 95.13% dimer-aware; coordinate counts 59 → 54

Status: PASS (all gates G0–G7; the original figure reproduced exactly
before the new definition was applied — G1b max|diff| 7.1e-15, G2
9,232/363 exact)

Time started / finished: 23:04:00 / 23:18:11 (spec + source reading
23:04–23:10, script 107 written 23:10–23:16; first run EXIT=1 on a
one-character typo — `pdb["coords_chain_{ch}"]` missing its f-prefix,
a KeyError raised at line 203 BEFORE any gate ran; fixed immediately
and disclosed here per rule; second run EXIT=0 in 0.3s, no gate,
threshold, definition, or N changed between runs)

What I did:
- **E2a (reuse, no rescoring):** confirmed the original figure's
  exact provenance by reading script 77: `pdb = load_pdb(str(PDB_PATH),
  ["A"])` (script 77 L261) — chain A alone, over `data/raw/6FCX.pdb`,
  with `dmat = get_dmat(pdb)` (C-alpha distance matrix from the
  vendor's `coords_chain_*['CA_chain_*']`), then
  `ca_dist_222 = dmat[p−40, 182]` (L428–431), FIRST_RESI=40. The 59
  positions-without-chain-A-coordinates list confirmed from two prior
  sources (scripts/68 L24; scripts/85 L106: "2-39, 161-171, 392-396,
  652-656") plus the task doc's own E2a statement. Wrote
  `scripts/107_e2_dimer_distance_recompute.py` with a pre-registered
  docstring (definitions, four-pair min PRIMARY, 10.0 Å cutoff, all
  gate thresholds, denominators, and 6-item limitations fixed before
  the run). It uses the SAME vendor parse machinery as both sessions
  (`thermompnn.ssm_utils.load_pdb` from
  data/external/ThermoMPNN-D, called with `["A","B"]`) — no model
  runs, no re-scoring; the AD7 session's task80 CSVs are read for the
  frame cross-check only.
- **Verified the mapping empirically, not by assumption:** G1b
  recomputes d(p_A, 222_A) from the parse and requires it to
  reproduce the STORED `ca_dist_222` column to <1e-6 on all 9,595
  frame rows (it matches to 7.1e-15) — that single check proves the
  position↔residue alignment AND that the original figure was
  chain-A-only. G2 then requires the published counts exactly
  (9,232 far / 363 near). G4 requires the chain-A missing set to
  equal the 59-position list EXACTLY (two independent prior sources).
- **E2b definition (pre-registered):** PRIMARY d_min(p) = min Cα–Cα
  distance over all four available pairings of the variant site's
  copy {chain A, B} × residue 222's copy {chain A, B} — the complete
  two-fold-symmetry accounting (both subunits carry both mutations in
  the biological construct); it can only shrink distances (G5's
  identity: d_min ≤ d_AA everywhere, far(dimer) ⊆ far(monomer)).
  SENSITIVITY = the task's literal reading (variant copy fixed in
  chain A, min over 222's two copies). Cutoff 10.0 Å (the original's).
  Denominator = the original figure's own frozen frame (task77 rows
  with own_e_b finite = 9,595 rows / 586 positions).
- **E2c:** counts over the atlas universe U = {2..656}, 655
  positions, file-verified (phase5's unique positions == U minus
  {222}, 654 exact).

Actual output (verbatim, e107.log):
- Gates:
  "G0 PASS: all 4 inputs present"
  "G1a PASS: chain A resn 40..651 resolved 596/612; chain B resn
  41..648 resolved 590/608; residue 222 = 'A' and resolved in BOTH
  chains"
  "inter-subunit 222(A)-222(B) C-alpha distance: 70.530 A"
  "G3 PASS: atlas universe U = {2..656} = 655 positions file-verified
  (phase5 = U minus {222}, 654 exact)"
  "G4 PASS: monomer missing over U == the 59-position list EXACTLY
  (59 = 38+11+5+5): 2-39, 161-171, 392-396, 652-656 — scripts/68 L24
  + scripts/85 L106 + task E2a all agree"
  "G1b PASS: d_AA reproduces stored ca_dist_222 on all 9595 frame rows
  (max|diff| = 7.105e-15 < 1e-06) — mapping p<->resn p-40 and 'chain
  A alone' both confirmed"
  "G2 PASS: original figure reproduced EXACTLY: far(>10 A) = 9232,
  near = 363, n = 9595, positions = 586 -> 96.2168% = the published
  96.22% (RELIABILITY_LOG L1058)"
  "G5 PASS: identity holds — d_min <= d_AA everywhere (max excess =
  +0.000e+00 <= 0) and far(dimer) rows are a SUBSET of far(monomer)
  rows"
- **E2b (side by side, same denominator):**
  "denominator: the ORIGINAL figure's frozen frame — 9595 variant
  rows / 586 positions (task77 rows with own_e_b finite)"
  "ORIGINAL monomer-only (chain A): far(>10 A) = 9232/9595 =
  96.2168%   [published as 96.22%]"
  "DIMER-AWARE (four-pair min, PRIMARY): far = 9128/9595 = 95.1329%"
  "sensitivity (variant fixed in chain A, min over 222's two copies):
  far = 9232/9595 = 96.2168%"
  "rows pulled INTO contact range through the opposite subunit: 104
  (and 6742 rows have d_min < d_AA at all)"
  "d_min - d_AA quantiles [0/25/50/75/100%]: [-23.9382, -2.1141,
  -0.7100, +0.0000, +0.0000] A  (all <= 0 by construction)"
  "SENS (four-pair vs chain-A-variant min): differ on 6257/9595 rows —
  PRIMARY (four-pair) is the smaller/enveloping one by construction"
  "symmetry diagnostics (descriptive): max|d_AA - d_BB| = 8.0976 A;
  max|d_AB - d_BA| = 7.0438 A over 578 frame positions present in
  both chains"
  "position-level (descriptive): monomer far = 563/586; dimer far =
  557/586"
  "G6 INFO: task80_dimer_positions has 586 positions; frame has 586;
  symmetric difference = EMPTY (identical) — AD7 session scored
  exactly this frame's positions"
- **E2c:**
  "G7 PASS: dimer-missing (54) is a subset of monomer-missing (59) —
  required by construction (A-or-B absent implies A absent)"
  "atlas universe U: 655 positions ({2..656})"
  "monomer (chain A) missing: 59 -> with coordinates 596; list = [2,
  3, ..., 39, 161, ..., 171, 392, ..., 396, 652, ..., 656]" (the
  full 59-position list printed, matching the policy list exactly)
  "chain B missing over U: 65 -> with coordinates 590"
  "DIMER (A or B) missing: 54 -> with coordinates 601; list = [2..39,
  161..171, 652..656]"
  "positions chain B RESCUES that A lacks: 5 -> [392, 393, 394, 395,
  396]"
  "(chain-B window 41..648 is narrower: positions A has but B lacks =
  11 -> [40, 203, 204, 220, 221, 314, 315, 316, 649, 650, 651] —
  reported per limitation 3)"
  "saved 655 position rows -> task107_e2_dimer_distances.csv"
- 6-item LIMITATIONS block printed with results (quoted in the
  script's own output: Cα-only single crystal structure; geometric
  lower envelope; chain-B window narrower; denominators never mixed;
  descriptive census — no resampling/p/CI; read-only inputs).
- "SCRIPT 107 DONE (0.3s) monomer 9232/9595 = 96.2168% | dimer
  9128/9595 = 95.1329% | mono-missing 59 / dimer-missing 54"

Verdict: PASS. **E2b — under the dimer-aware definition the
long-range figure is 9,128/9,595 = 95.13% (vs the original
monomer-only 9,232/9,595 = 96.22%)** — the claim survives the
correction with a −1.09 pp adjustment; 104 variant rows (1.08%) are
pulled into contact range through the opposite subunit, and
position-level the figure moves 563/586 → 557/586. Note the
pre-registered decomposition: the task's literal sensitivity reading
(variant copy fixed in chain A, min over the two 222 copies) is
EXACTLY 96.22% — the other copy of residue 222 alone never pulls a
row in (it sits 70.53 Å from its own copy across the interface);
every one of the 104 flips comes from the variant's own chain-B copy,
i.e. the full two-fold-symmetry accounting is what moves the number.
**E2c — atlas positions with no coordinates: monomer 59 (exactly the
prior 59-list, chain A gives 596/655), dimer 54 (A or B gives
601/655); chain B rescues exactly 392–396**, while B independently
lacks 40/649–651 (narrower window) and 203–204, 220–221, 314–316
(B-side unresolved loops) — A covers those, so the union loses only
the 5. The write-up's "96.2% beyond structural contact range"
(PROJECT_SUMMARY_FINAL L169, quoted, untouched) can now be restated
as ~95% under the dimer-aware definition; quote-ready line for the
user/later session (NOT applied — same rule-4 assumption as A1/E1):
"On the biological dimer (both chains, minimum distance to either
copy of residue 222 across both subunits), 9,128/9,595 = 95.1% of
the analysis frame sits beyond 10 Å contact range from position 222
(chain-A-only monomer figure: 96.2%), and 54 of 655 atlas positions
lack structural coordinates under that definition (monomer-only: 59)."

Files created/modified: NEW `scripts/107_e2_dimer_distance_recompute.py`
(pre-registered docstring; one pre-gate typo fixed and disclosed);
NEW `data/processed/task107_e2_dimer_distances.csv` (655 position
rows × 14 columns). Read-only: data/raw/6FCX.pdb,
task77_thermompnnD_doubles.csv, task80_dimer_positions.csv,
phase5_analysis_table.csv, data/external/ThermoMPNN-D (vendor
`load_pdb`, imported), scripts/77 (read for provenance), scripts/68
L24, scripts/85 L106. Nothing existing overwritten.

Anything unexpected or worth flagging:
- **The four-pair min vs the literal-reading min differ substantially** (6,257/9,595 rows): the crystal's two subunits are NOT
  exact coordinate mirrors (max|d_AA − d_BB| = 8.10 Å, max
  |d_AB − d_BA| = 7.04 Å) — reported as measured, not assumed away;
  the PRIMARY was pre-registered as the envelope (the smaller), so
  this is the conservative direction for a "long-range" claim.
- **The literal reading changes nothing (exactly 96.22%)** — a
  result worth stating plainly: "either copy of 222" while keeping
  the variant in chain A is a no-op here; the correction that
  matters is allowing the variant's chain-B copy. If a reviewer
  expected the first phrasing alone to move the number, it does not.
- Chain B resolves 392–396 which chain A does not (5-position
  rescue), so the two definitions' missing sets genuinely differ —
  exactly why E2c asked (they may differ: 59 vs 54, confirmed).
- G6 showed the AD7 session's position set is IDENTICAL to the
  frame's (586 = 586, empty symmetric difference) — E2a's "reuse"
  cross-check passed cleanly; no rescored material was needed.
---

## [F1] — α discrepancy resolved: script 97 used (and pre-registered) α = 0.05; RESULTS.md's "α_FWER = 0.01" is the erroneous side → OPEN ITEM, not edited

Status: DONE — discrepancy located, root-caused, and the correct
side identified; **RESULTS.md correction flagged as an OPEN ITEM
requiring the user's explicit go-ahead (F1a's own instruction), file
not touched**; script 97 and its own log entry need NO fix

Time started / finished: 23:18:30 / 23:23:27 (reading + one
deterministic diagnostic on script 97's own holm() implementation;
no new inferential result computed — the diagnostic is a
re-application of the pre-registered rule to the already-recorded raw
p-values, purely to determine which α each claim needs)

What I did (F1a):
- Read RESULTS.md's multiplicity-correction line directly (exact
  phrase verified on disk this session): "family-wise Holm (5/5 core
  at α_FWER = 0.01; 8/8 in the m = 8 set)" (RESULTS.md L11).
- Read script 97's actual implementation: `scripts/97_holm_family.py`
  (note: the task doc calls it "scripts/97" — the file on disk is
  `scripts/97_holm_family.py`; verified to exist). Its METHOD
  docstring states the rule verbatim as "Holm-Bonferroni step-down,
  family-wise alpha = 0.05: sort p ascending; threshold at rank i
  (1-based) = alpha / (m - i + 1)", and the constant is
  `ALPHA = 0.05` (L144).
- Read script 97's actual OUTPUT (`data/processed/task97_holm_family.csv`)
  and confirmed the thresholds in the file are Holm-at-0.05: core5
  family thresholds 0.01, 0.0125, 0.016666666666666666, 0.025, 0.05
  (= 0.05/5 … 0.05/1); core8 family thresholds 0.00625 … 0.05
  (= 0.05/8 …). The CSV is therefore α = 0.05's product, not α =
  0.01's.
- Read script 97's OWN log entry: RELIABILITY_LOG.md L1289–L1305
  quotes the run's printed lines "…-> 5/5 survive at family-wise
  alpha 0.05; non-survivors: none" and "…-> 8/8 survive at
  family-wise alpha 0.05", plus "survives at alpha=0.05 (margin
  +0.014000)" for the tightest member. VERIFIED_FINDINGS_TABLE rows
  92/93 likewise say "5/5 survive family-wise α=0.05" and "8/8
  survive" with adj p values matching the CSV.
- Checked for any pre-registration of 0.01 anywhere: grep across
  docs/ for α_FWER / FWER / "family-wise alpha" / Holm+0.01 finds
  only (a) the 0.05 statements above and (b) exactly TWO documents
  asserting 0.01: RESULTS.md L11 and DISATTENUATION_LOG.md L147 (the
  K19 ledger row: "5/5 core survive at α_FWER 0.01; 8/8 at m=8").
  No task doc, no docstring, and no log entry ever pre-registered
  α_FWER = 0.01. PROJECT_SUMMARY_FINAL.md contains ZERO occurrences
  of "Holm" (checked this session) — so the write-up's pointer
  ("corrections and drops are itemized in PROJECT_SUMMARY_FINAL")
  does not itself carry an α claim either way.
- **Determined which is correct by testing what each α yields**,
  using script 97's OWN `holm()` function (imported from the file,
  not reimplemented) on the CSV's recorded raw p-values:

Actual output (verbatim, diagnostic run this session):
```
core5  alpha=0.05: rejected 5/5
core5  alpha=0.01: rejected 5/5
core8_sens  alpha=0.05: rejected 8/8
core8_sens  alpha=0.01: rejected 5/8
core5 raw ps: [0.0, 0.0, 0.0, 0.0, 9.4039548065783e-38]
core8 raw ps: [0.0, 0.0, 0.0, 0.0, 9.4039548065783e-38, 0.012,
  0.0194, 0.0232387273643964]
```

Verdict (the determination F1a asks for):
- **What the script actually used: α = 0.05** (docstring METHOD,
  `ALPHA = 0.05`, CSV thresholds, and the run's own printed log all
  agree — four independent confirmations on disk). Script 97 is
  CORRECT as it stands; no fix to the script or to its log entry is
  warranted, and none was made.
- **What the write-up claims: α_FWER = 0.01** — this is the
  erroneous side. Two distinct problems:
  1. It misstates the run's α (the run used 0.05);
  2. It is internally inconsistent with its own second claim: at
     α_FWER = 0.01 the m = 8 sensitivity family rejects **5/8, not
     8/8** (step-down stops at AE3b raw 0.012 > 0.01/3 = 0.00333…,
     diagnostic above), whereas at the α actually used (0.05) the
     stated 8/8 is true. So the sentence as written cannot be made
     correct by changing only the α in one place: keeping "8/8"
     requires α = 0.05.
  3. Likely origin of the stray "0.01" (stated as an observation,
     not a claim about intent): 0.01 is exactly the m = 5 family's
     FIRST-RANK Holm threshold (0.05/5 = 0.01), the first number in
     the CSV's threshold column for core5.
- **OPEN ITEM (do not edit, F1a's explicit instruction): RESULTS.md
  L11.** The prior session's edit was "the second and final
  authorized hand-edit"; no new authorization exists. When
  authorized, the minimal correct fix is a one-token change —
  "family-wise Holm (5/5 core at α_FWER = **0.05**; 8/8 in the m =
  8 set)" — which makes both claims true and matches the script,
  its log, and the verified-findings table. (The alternative
  direction — keep 0.01 and restate the counts as "5/5 core; 5/8 at
  m=8" — would describe a run that was never executed and is
  therefore NOT the fix; the script ran at 0.05.)
- **SECOND OPEN ITEM (flag only, never edit — prior log):**
  DISATTENUATION_LOG.md L147's K19 row carries the identical
  α_FWER 0.01 error ("5/5 core survive at α_FWER 0.01; 8/8 at m=8").
  Same root cause, same correct value (0.05); same policy: flagged,
  not edited, because it is a prior session's log entry (AGENTS §7;
  log entries are append-only records).

Files created/modified: this log entry only. Read-only: RESULTS.md
(L11 phrase verified verbatim), scripts/97_holm_family.py (L40–180
docstring/ALPHA/holm read; imported read-only for the diagnostic —
its __main__ guard means no side effects on import),
data/processed/task97_holm_family.csv, RELIABILITY_LOG.md
(L1289–1305), VERIFIED_FINDINGS_TABLE.md (rows 92–93),
DISATTENUATION_LOG.md (L147), PROJECT_SUMMARY_FINAL.md (grep:
0 Holm hits), docs/ (grep for any 0.01 pre-registration: none).

Anything unexpected or worth flagging:
- **The α error is load-bearing in the opposite direction from what
  one might assume**: 0.01 is the *stricter-sounding* value, so the
  write-up currently overstates the correction's severity while the
  counts it reports (5/5, 8/8) belong to the *corrected-at-0.05*
  run. The results themselves (5/5, 8/8) are unaffected — they are
  right; only the α label is wrong.
- At α = 0.01 the core family would still be 5/5 (all five raw p's
  ≤ 9.4e-38) — so the core claim is robust to either α; the m = 8
  sensitivity claim is not (5/8 vs 8/8). Any future restatement must
  bind the counts and the α to the same run.
- The task doc's "scripts/97" maps to `scripts/97_holm_family.py`
  on disk (the filename task F1a does not spell out) — recorded here
  so the mapping is not re-guessed.
---

## [F2] — Honest total test count: citation confirmed verbatim, limitations paragraph drafted (no computation)

Status: PASS (citation accuracy confirmed against disk; one
quote-ready limitations paragraph delivered in this log; no file
outside this log touched — rule-4 assumption as with A1/E1)

Time started / finished: 23:23:30 / 23:26:00 (grep + tree count; no
script run)

What I did (F2a):
- Located the cited estimate and read it in full — it is
  OVERNIGHT_LOG.md **L1554** (docs/tasks/review-triage/), one
  paragraph containing BOTH quoted fragments. Verbatim, in relevant
  part:
  > "Rough count reasoning (stated as an estimate, not precision):
  > distinct hypothesis-test call sites ≈ 35 position-cluster
  > bootstraps + 3 paired-rho bootstraps + ~10 non-bootstrap
  > permutation/null tests + ~15 inferential spearmanr/pearsonr ≈
  > **~65 test sites**; reported individually, several sites expand
  > across subsets (script 19 alone prints 18 cluster-bootstrapped
  > CIs; log §3.2 = 8 region tests; D1a = 7; E1a = 7; C1's table ≈
  > 6 rows × 3 targets × 3 metrics × 3 strata ≈ 100+ cells but only
  > ~6 pre-specified contrasts claimed; scripts 24/28/50/53 report
  > per-stratum CIs). Honest range: **on the order of 100-200
  > individually reported inferential numbers across 61 scripts.**
  > No formal project-wide multiplicity correction has been claimed
  > anywhere; protection in-project comes from pre-registered gates
  > (script 36 precedent), position-level nulls (A1a/A1b), and this
  > review's per-task pre-registrations. This count is itself a
  > rough audit figure — reproducible from the grep above."
- **Citation accuracy: CONFIRMED.** Both fragments in the task doc
  match L1554 word-for-word; the only differences are typographic
  normalization in the task doc (en-dash "100–200" vs the log's
  ASCII "100-200", and sentence-initial capitalization of "No" in a
  mid-sentence quotation). The task doc also silently omits the
  log's own qualifier — "this count is itself a rough audit figure"
  — which the paragraph below restores, because quoting the range
  without its own caveat would strengthen the citation beyond what
  the source claims.
- Checked the companion claim against the current tree: the log's
  "61 scripts" was its audit-time figure; `ls scripts/*.py | wc -l`
  today = **103** top-level scripts (verified this session,
  including this response round's 98–107). The order-of-magnitude
  range therefore belongs to its audit moment and the population
  has grown since — stated in the paragraph rather than left to be
  discovered later.
- Cross-checked the Holm scope wording against F1's verified facts
  (script 97: `ALPHA = 0.05`, pre-registered METHOD in its
  docstring; 5-member core family + 8-member sensitivity set; CSV
  thresholds confirm Holm-at-0.05) so this paragraph and F1's open
  item can never be quoted against each other.

### F2a — quote-ready limitations paragraph (for the write-up's limitations section; NOT applied — rule-4)

> **Multiplicity, stated plainly.** This project reports on the
> order of 100–200 individually computed inferential numbers
> (p-values, confidence intervals, null tests) across 61 scripts —
> an explicitly rough, grep-derived audit figure rather than a
> precise census, and one made when the script tree was smaller than
> it is now (103 top-level scripts at this writing). No formal
> project-wide multiplicity correction has been claimed anywhere in
> the project. The only formal family-wise correction is a
> Holm–Bonferroni step-down over a narrow, pre-registered
> confirmatory family (script 97's five-member core family, with an
> eight-member sensitivity set), which ran at family-wise α = 0.05
> and retained 5/5 core and 8/8 sensitivity members. That
> correction addresses those five-to-eight pre-registered claims
> only; **it does not adjust, and is not presented as adjusting,
> the project's full set of computed inferential quantities.**
> Elsewhere the project's protection against false positives rests
> on per-analysis pre-registered decision gates, position-cluster
> bootstrap and position-level nulls (never row-level resampling),
> and documented split-half stability checks — not on any global
> multiplicity adjustment. Readers should therefore treat isolated
> nominal p-values outside the pre-registered family as
> descriptive, uncorrected evidence.

Verdict: PASS — F2a's two required elements delivered: (i) the
citation is confirmed accurate by quoting the exact line (L1554,
both fragments verbatim, with the source's own "rough audit figure"
qualifier restored); (ii) one clean limitations paragraph states the
count plainly and states, in the task's required terms, that the
five-to-eight-member Holm correction addresses only a narrow,
pre-registered confirmatory family and not the project's full set
of computed inferential quantities. The paragraph's α (0.05) and
counts (5/5, 8/8) were bound to the same run per F1's finding — so
the two entries cannot contradict each other.

Files created/modified: this log entry only. Read-only:
OVERNIGHT_LOG.md (L1554 read in full; L1873 J3a line also checked —
it restates the same estimate as "~65 test-call sites / order
100–200 reported inferential numbers across 61 scripts"),
MANUSCRIPT_REVIEW_RESPONSE.md (F2a spec), scripts/97_holm_family.py
+ task97_holm_family.csv (F1, referenced here), tree count via
`ls scripts/*.py | wc -l`.

Anything unexpected or worth flagging:
- OVERNIGHT_LOG L1873 (the round's own PASS summary) independently
  restates the same estimate, so the number is corroborated inside
  its source document — but both restatements share one grep, so
  they are not two independent counts.
- The paragraph deliberately restores the source's hedge ("rough
  audit figure") and adds the tree-growth disclosure: the honest
  framing of a test-count claim is that it is an order-of-magnitude
  floor from a specific moment, not a live census — and nobody has
  re-run the count since (no such recount is authorized or needed
  for F2a; flagged rather than performed).
---

## [G1] — Estimator-differences table: MTHFR vs GB1 transplant vs GRB2 transplant, with the design limitation stated plainly (no computation)

Status: PASS (citation-ready table + plain-language statement
delivered in this log; pure compilation from on-disk sources —
nothing new computed, same rule as B1/E1)

Time started / finished: 23:26:00 / 23:33:00 (source reading; no
script run)

What I did (G1a):
- Read each estimator's actual implementation/record directly:
  - **MTHFR primary:** `scripts/lib/own_context.py` L32–33
    (WT_SCORE_COLS/SE_COLS = the four measured concentration
    conditions w12/w25/w100/w200, each with its own measured SE),
    L143–157 (`fit_interaction`: `expected(c) = single_mutant_term(c)
    × (b_A222V + c·r_A222V)` — the multiplicative no-interaction
    expectation with the MEASURED A222V background line; the
    single-mutant term is the per-variant fitted line when w.post >
    0.5, else the variant's mean WT-background score, "per
    fitModels.R"), and RELIABILITY_LOG L1162–L1166 (WLS with
    w=1/se², closed-form intercept SE of e_b).
  - **GB1 transplant (AA1, scripts/73):** DEEPDIVE_LOG L605–646 —
    six explicit pre-registered adaptations A1–A6: "single-point
    residual replaces the 4-concentration WLS line; uniform weights —
    GB1 ships no per-genotype SEs; multiplicative expectation
    E[f(v+bg)] = f(v)·f(bg)/f(WT) on the fitness scale; no
    fitness-based row filtering; flip cell = variant; Null-2 blocks =
    focal site"; f(WT) = 1.0 measured from GB1's own WT row
    ("WT=VDGV=1.0" gate, L627); 57 variants × 1 flip unit = 57
    cells (L646); background V54A chosen by chemical parallelism,
    fitness-blind (L612–613).
  - **GRB2 transplant (AA2, scripts/74):** DEEPDIVE_LOG L1110–1225 —
    AA1's A1–A6 carried verbatim (→ uniform weights; flip cell =
    variant) plus A7 (WT anchor: zero-mutation row if present, else
    fixed pre-run `c-hat` = median f(v+bg)/f(v)), A8 (count-based
    background, no chemical parallelism), A9 (partner spread
    printed). Output L1162–1176: background B208G (count-rule,
    frozen before fitness read), partners n=689 over 53 positions,
    "distance from bg position: min=1, median=27, max=49",
    "WT-anchor branch A7b: no zero-mutation row in the scores file
    (as verified on the MTHR file) -> c-hat = median f(v+bg)/f(v) =
    0.855271 over 689 partner rows", design line "rows=689 | flip
    units (cells)=689 (one +/-1 per variant, A5) | ... | MTHFR
    contrast: 10,757 variants x 4 conc cells = 43,028 cells, 654
    positions".
  - **Absolute-arm degeneracy:** DISATTENUATION_LOG L428 — "AA1's
    absolute-value sign-flip variant is degenerate under the
    single-cell transplant (|flip × r| = |r| invariant → p=1 by
    construction), disclosed post-hoc in AA1's own entry
    (L655–660). MTHFR's 4-cell design keeps it non-degenerate
    (script 33)." GRB2's run shows the same degeneracy live
    (DEEPDIVE L1184–1188: "observed=-0.0272 null mean=-0.0272
    sd=+0.0000 p=1.0000 ... 100% of the raw value is structural
    artifact ... DEGENERATE here, carries no information",
    pre-registered from AA1's disclosed finding).
  - **Detection/centering outcomes:** GB1 signed rho +0.1222,
    p = 0.3849 (n=57, PLAIN NULL, underpowered) with centering YES
    (DEEPDIVE L1211–1215, AA1's own CSV re-verified per L1143–1145);
    GRB2 signed +0.1153, p = 0.0019 with null mean −0.0003
    (centering replicated) and Null-2 association p = 0.0108
    (L1177–1190, L1204–1215).
  - **Distance regimes:** GRB2 partner distances from the background
    position 1–49 residues (median 27) across 53 positions of a
    217-aa protein (L1163) — the source's own label is "local/distant
    mix, not a purely local control" (L1222); GB1's four-site library
    (sites 39/40/41 vs background site 54 = 13–15 residues apart)
    (L614, L1110); MTHFR = one fixed background (A222V) on a 656-aa
    protein with ~95% of the analysis frame beyond 10 Å from 222
    under the dimer-aware definition (this session's [E2]).

### G1a — the table (quote-ready)

| Dimension | MTHFR primary (this project) | GB1 transplant (AA1, scripts/73) | GRB2 transplant (AA2, scripts/74) |
|---|---|---|---|
| Weighting scheme | 4-condition weighted least squares, w = 1/se², measured per-condition SEs (`own_context.py`; analytic WLS intercept SE of e_b) | Uniform weights — GB1 ships no per-genotype SEs (A2); single-point residual replaces the 4-concentration WLS line (A1, forced: the WLS line returns NaN at n=1 by its own guard) | Uniform weights; single-point residual (A1–A6 carried verbatim from AA1) |
| Wild-type anchor | Measured: four measured WT scores/SEs (w12/w25/w100/w200) and the measured A222V background line (b_A + c·r_A) enter the multiplicative expectation directly | Measured: GB1's own zero-mutation row, f(WT) = VDGV = 1.0 (data gate) | **Proxy:** no zero-mutation row exists → pre-registered c-hat = median f(v+bg)/f(v) = 0.855271 over the 689 partner rows (A7b) |
| Sign-flip granularity | Per-condition cell: 10,757 variants × 4 concentration cells = 43,028 flip units (654 positions) | Per-variant cell: 57 flip units (one ±1 per variant, A5) | Per-variant cell: 689 flip units (one ±1 per variant, A5), nested in 53 positions |
| Absolute-arm null under single-cell flips | **Non-degenerate** (4 cells/variant; script 33's identity checks pass: all-+1 reproduces e.b exactly, all−1 gives its negation) | **Degenerate:** \|flip × r\| = \|r\| invariant → p = 1 by construction; disclosed post-hoc in AA1's own entry, no information carried | **Degenerate, same mechanism** (pre-registered from AA1's disclosure): printed p = 1.0000, "100% of the raw value is structural artifact ... carries no information" |
| Sequence-distance regime of assayed pairs | Long-range, single fixed background: one background (A222V), variants across positions 2–656; ~95% of rows beyond 10 Å from 222 even on the biological dimer ([E2]: 95.13%; monomer figure 96.22%) | Local, dense: 3 adjacent sites (39/40/41) vs background site 54 → all pairs 13–15 residues apart, one background (V54A) | Short-range-to-mid, multi-partner: 689 partners over 53 positions, distance from background site 208 = 1–49 residues (median 27), one background (B208G); source's own label: "local/distant mix, not a purely local control" |
| Null-centering outcome | Centered (signed null mean +0.0001 vs observed −0.0881; sign-flip identity checks exact) | Centering YES (replicated) | Centering YES: null mean −0.0003, sd 0.0371 at N_PERM=10,000 |
| Detection outcome | Observed −0.0881, p < 1e-4 (small but real) | rho +0.1222, p = 0.3849 — NOT detected (n=57, underpowered; reported as the null result it is) | rho +0.1153, p = 0.0019 — DETECTED (Null-2 association p = 0.0108) |

### G1a — the plain statement the table supports (quote-ready)

> The controls establish exactly two things. First, **null
> centering**: the transplanted instrument's sign-flip null centers
> on zero on both GB1 (scripts/73) and GRB2 (scripts/74), with the
> exact identity checks (all-+1 flips reproduce the statistic; all−1
> give its negation) passing in every run. Second, **genuine
> detection capability in a short-range, multi-partner regime**: on
> GRB2 — 689 partner variants across 53 positions at sequence
> distances 1–49 from the background site, the same methodology
> detects established epistasis (signed rho = +0.1153, p = 0.0019)
> while GB1's far smaller n = 57 correctly did not (p = 0.3849).
> **No control in this project establishes detection validity for a
> single, distant, fixed background** — every positive control runs
> either a local library (GB1: sites 39–41 vs 54) or a short-range
> partner set (GRB2: ≤49 residues from the background), whereas the
> MTHFR claim concerns a single fixed background (A222V) measured
> overwhelmingly beyond contact range (~95% of the frame beyond
> 10 Å even on the biological dimer). Demonstrating that the
> estimator centers on zero and can detect nearby, densely sampled
> epistasis does not by itself demonstrate that it detects distant
> single-background epistasis of the kind MTHFR's setting requires.
> This is a limitation of the control design, stated as such.

Verdict: PASS — all six requested dimensions covered with
dimension-by-dimension sources, and the plain statement says what
the controls establish (centering; GRB2 short-range multi-partner
detection) and what they do not (single distant fixed background),
labeling it a design limitation. Two honesty notes embedded in the
table: (i) GRB2's regime is the source's own "local/distant mix,
not a purely local control" rather than the task doc's bare
"local/dense" — the numbers (1–49, median 27 of 217) are given so
the reader can judge; relative to MTHFR's ~95%-beyond-10-Å regime
it is short-range, which is the contrast the statement needs; (ii)
the absolute-arm degeneracy is reported as it occurred — GB1
disclosed post-hoc, GRB2 pre-registered — never smoothed into a
clean design property.

Files created/modified: this log entry only. Read-only:
scripts/lib/own_context.py (L32–33, L143–157),
DEEPDIVE_LOG.md (L605–649, L1110–1233), DISATTENUATION_LOG.md
(L428), RELIABILITY_LOG.md (L1162–1166), MANUSCRIPT_REVIEW_RESPONSE.md
(G1a spec).

Anything unexpected or worth flagging:
- The MTHFR estimator's own documentation cites fitModels.R (the
  paper's own model) for the single-mutant term — the "measured vs
  proxy" contrast in row 2 of the table is therefore about the
  ANCHOR (WT/background line), not about the single-mutant term,
  which in MTHFR's case is itself sometimes the variant's mean
  WT-background score rather than a fitted line (w.post ≤ 0.5
  branch) — the table says this explicitly so "measured" is not
  read as stronger than it is.
- GB1's WT anchor is MEASURED (f(WT)=1.0) — so the c-hat proxy is
  a GRB2-specific substitution (its file ships no zero-mutation
  row), not a property of "the transplants" as a class.
---

## [G2] — GRB2 citation year verified from ProteinGym's own metadata: publication year = 2022; "2021" is part of the dataset ID

Status: PASS (checked the metadata file directly, per G2a; no
citation in the project's write-ups needs changing)

Time started / finished: 23:33:00 / 23:35:00 (direct read of the
catalog CSV; no script run)

What I did (G2a):
- Read `data/external/ProteinGym/DMS_substitutions.csv` (the
  ProteinGym assay catalog this project fetched — the file whose
  md5 c434631737013fceb56efc98056151e0 is gated in scripts/74's
  startup) and located the single GRB2 row directly. Verbatim field
  values from that row:
  - `DMS_id = 'GRB2_HUMAN_Faure_2021'`
  - `DMS_filename = 'GRB2_HUMAN_Faure_2021.csv'`
  - `first_author = 'Faure'`
  - `title = 'Mapping the energetic and allosteric landscapes of
    protein binding domains'`
  - **`year = 2022`**
  - `UniProt_ID = 'GRB2_HUMAN'`, `seq_len = 217`,
    `region_mutated = '159-214'`, `selection_assay = 'Yeast growth'`
- Searched every project .md for prior GRB2/Faure citations (grep
  "Faure"): all six hits are DEEPDIVE_LOG.md's record of this
  session — five are the literal dataset/member string
  `GRB2_HUMAN_Faure_2021`, and the sixth is the session's own
  citation line "SELECTED: GRB2_HUMAN_Faure_2021 (Faure 2022)"
  (DEEPDIVE_LOG L1161).

Actual output: quoted above (field values printed by a direct
pandas read of the catalog row; grep results: 7 matches total —
6 in DEEPDIVE_LOG, 1 in the task doc itself).

Verdict: **the correct publication year is 2022**, per ProteinGym's
own `year` field on the GRB2 row. The "2021" appears only inside
ProteinGym's `DMS_id`/filename convention (`GRB2_HUMAN_Faure_2021`)
— it is part of the dataset identifier, not the publication-year
metadata, and must not be quoted as the paper's year. The project's
one explicit citation already says "(Faure 2022)" (DEEPDIVE_LOG
L1161), so **no project document carries a wrong year** — G2a's
"possibly-inconsistent prior citation" concern does not materialize
on disk; the only inconsistency is the ID-vs-year juxtaposition
inside ProteinGym's own naming, resolved by the metadata field.

Files created/modified: this log entry only. Read-only:
data/external/ProteinGym/DMS_substitutions.csv (GRB2 row read
directly), DEEPDIVE_LOG.md (L1151–1161, L1226–1233 fetch record),
MANUSCRIPT_REVIEW_RESPONSE.md (G2a spec).

Anything unexpected or worth flagging:
- Nothing in the repo records the paper's DOI/journal for this
  entry — if the write-up later needs a full reference (journal,
  DOI), ProteinGym's catalog carries only first author/title/year
  here; pulling the DOI from the publisher would be a new external
  fetch (not needed for G2a, not done).
- The same ID-vs-year pattern likely applies to other ProteinGym
  IDs (e.g. `MTHR_HUMAN_Weile_2021` — a 2021 ID); any future
  citation should read the `year` field per dataset rather than
  parsing the ID.
---

## [G3] — Region-boundary provenance located (lib/regions.py, personal communication) + acknowledgment draft; permission flag: user follow-up REQUIRED

Status: PASS with an open item (provenance record located and quoted;
acknowledgment text drafted; **public-use permission NOT confirmed —
flagged for the user, not assumed**)

Time started / finished: 23:35:00 / 23:38:00 (reading; no script run)

What I did (G3a):
- Located the exact provenance record the task points to:
  `scripts/lib/regions.py` L1–24 (its module docstring IS the chain
  of communication; AGENTS.md §8 independently confirms: "Real
  boundaries were obtained by direct email to a co-author and are
  in scripts/lib/regions.py with full provenance"). Verbatim:
  > "Source: personal communication, Nishka Kishore (2nd author,
  > Weile et al. 2021) via Fritz Roth, in response to an emailed
  > query, Sept 2026, forwarding the actual primer design file
  > (MTHFR_regionalPOPcode_regions.xlsx) from Song Sun. Not
  > published in the paper, the GitHub repository, or any released
  > data file -- the prior Tier 2 pass disclosed this as
  > unobtainable.
  >
  > Cross-validated three ways before use:
  >   1. Union of the four ranges exactly equals the atlas's position
  >      set (2-656; position 1, the Met start codon, is absent from
  >      both).
  >   2. Tile counts per region (4,4,5,6) match the paper's stated
  >      tile counts for R1-R4 exactly.
  >   3. Residues/tile is 30-37 across all four regions -- a tight,
  >      plausible band for ~130nt tiles with codon-level
  >      mutagenesis."
- The boundaries themselves: `REGION_BOUNDS = {1: (2, 147),
  2: (148, 294), 3: (295, 474), 4: (475, 656)}` (regions.py L24),
  with the primer-level tile boundaries kept at L18–22.

### G3a — draft acknowledgment text (quote-ready; NOT to be used until permission is confirmed)

> **Acknowledgment of unpublished data (draft — pending
> permission).** The mutagenesis-region boundaries used in this
> work (R1: 2–147, R2: 148–294, R3: 295–474, R4: 475–656) are not
> published in Weile et al. (2021), its GitHub repository, or any
> released data file; they were provided as a personal
> communication to Nishka Kishore (2nd author, Weile et al. 2021)
> and Fritz Roth in response to an emailed query (September 2026),
> forwarding the original primer-design file
> (MTHFR_regionalPOPcode_regions.xlsx) prepared by Song Sun. Before
> use, the boundaries were cross-validated three ways: the union of
> the four ranges exactly equals the atlas's mutagenized position
> set (2–656); the per-region tile counts (4/4/5/6) match the tile
> counts stated in the paper; and residues per tile (30–37) fall in
> a plausible band for ~130-nucleotide codon-level mutagenesis
> tiles. We thank Nishka Kishore, Song Sun, and Fritz Roth for
> sharing these unpublished boundaries.

### Permission flag (the explicit part G3a requires)

Using this acknowledgment — and, arguably, publishing the boundary
values themselves — **in any public write-up requires the original
source's permission. Permission has NOT been confirmed.** The chain
(Kishore → Roth → this project) was an emailed response to a query;
nothing on disk records consent for onward publication, and the
file's own docstring states the material was "not published" by the
original authors. **Open item for the user:** obtain explicit
permission from Nishka Kishore (and, as courtesy, Song Sun and
Fritz Roth) before any public release of these boundaries or this
acknowledgment text. Do not assume permission; do not treat the
email's having answered our query as consent to republish. This
situation is exactly analogous to the task doc's framing of personal
communication in citations (standard scholarly practice: cite with
permission).

Verdict: PASS — provenance record located and quoted verbatim
(regions.py L1–24, matching AGENTS §8's description), acknowledgment
drafted as a personal communication with the three-way
cross-validation stated, and permission explicitly flagged as NOT
confirmed and requiring user follow-up — not assumed anywhere.

Files created/modified: this log entry only. Read-only:
scripts/lib/regions.py (L1–35), AGENTS.md (§8), 
MANUSCRIPT_REVIEW_RESPONSE.md (G3a spec).

Anything unexpected or worth flagging:
- The record names three people in the chain (Kishore, Roth, Sun).
  The acknowledgment draft names all three; the permission question
  should at minimum reach the person who sent the file (Kishore,
  via Roth) — the user knows the actual channel used.
- The docstring itself notes the prior Tier 2 pass had already
  classified these boundaries "unobtainable" — i.e., the project's
  earlier public-facing tier deliberately did not contain them.
  Any manuscript that now USES them crosses that earlier line, which
  is a second reason the permission check is not a formality.
---

## [H1] — .gitignore narrow exceptions for the four headline tables (edited; verified both directions)

Status: DONE (the one Group H task that authorizes a repo-file edit —
H1a names .gitignore explicitly — plus file identification done by
checking columns/rows on disk, not by guessing)

Time started / finished: 23:36 / 23:39

What I did (H1a):
- Identified the four targets by reading the files themselves, not
  from the task's description alone:
  - **Primary ~10,757-row analysis frame:** scanned every
    `data/processed/*.csv` for a file holding ALL of
    {delta_esm, own_e_b, esm2_score, position, region} — exactly two
    candidates: `task32_analysis_table.csv` (11,344 rows) and
    `task36_analysis_table.csv` (11,113 rows). Distinguished them
    two ways: (i) `dropna(delta_esm, own_e_b)` on task32 = **10,757
    rows, 654 positions** — the exact frame every headline number
    uses; (ii) reader count: 10 scripts read task32 (incl. this
    round's 101/102/105/106) vs 2 scripts reading task36. Verdict:
    `task32_analysis_table.csv` is THE primary frame. (task36
    qualifies on columns too but is the two-diagnostic-table variant.)
  - **Five ESM-1v member score CSVs:**
    `task_AC4_esm1v_member{1..5}_scores.csv` — confirmed as the
    lead-figure source: script 105's G2 reproduced median r_XX =
    0.882637 from these five files this round ([A2]), and scripts
    86/89/90/91/92/98/103/105 all read them.
  - **ProteinGym comparison table:**
    `task_AB2_proteingym_model_comparison.csv` (script 71's output).
  - **ThermoMPNN output table:** `task_V2_thermompnn_ddg.csv` —
    verified as script 68's output (`out = PROC /
    "task_V2_thermompnn_ddg.csv"` at L417 of
    scripts/68_thermompnn_ddg_epistasis.py).
- Checked the current .gitignore (11 lines: `data/processed/*.csv`
  at L6, `data/external/` at L11 — the latter added by commit
  7df1941, the "data/external fix" H1a points at: the pattern is
  plain explicit single-line entries, so the exception is written the
  same way).
- Appended the H1 exception block to `.gitignore` (after the ignore
  rules, so the negations take effect), commented with what each file
  backs. Nothing else in .gitignore changed; the full
  `data/processed/` directory stays ignored.

Actual output (verbatim, the two verification runs):
```
$ git check-ignore -q <file>; echo $?   # definitive test
TRACKABLE:  data/processed/task32_analysis_table.csv
TRACKABLE:  data/processed/task_AC4_esm1v_member3_scores.csv
TRACKABLE:  data/processed/task_AB2_proteingym_model_comparison.csv
TRACKABLE:  data/processed/task_V2_thermompnn_ddg.csv
IGNORED:    data/processed/phase5_analysis_table.csv
IGNORED:    data/processed/task106_c1_mechanism_null.csv
```
```
$ git status --short -- data/processed   # corroborates: excepted
?? data/processed/task32_analysis_table.csv     # files show as untracked
?? data/processed/task_AB2_proteingym_model_comparison.csv   # (would be
?? data/processed/task_AC4_esm1v_member1_scores.csv           #  git add-able)
...
```

Verdict: PASS — the four target items are trackable, controls
(phase5_analysis_table, task106) still ignored, and the exceptions
are narrowly scoped exactly as H1a requires (no full
`data/processed/` un-ignoring). Files are excepted, not committed —
committing is a separate, not-requested action.

Files created/modified: `.gitignore` (H1 exception block appended).
Read-only: scripts/32 (task32 writer, L168), scripts/68 (out path),
data/processed/ column/row scans.

Anything unexpected or worth flagging:
- **Sanity-check wobble, disclosed:** my first ad-hoc check printed
  "STILL IGNORED" for the excepted files. That was an interpretation
  error IN THE CHECK, not in the .gitignore: `git check-ignore -v`
  prints the last matching pattern — here the `!` negation line —
  and exits 0 on any match, so "pattern printed" ≠ "ignored". The
  definitive `-q` test and `git status` both confirm the files are
  NOT ignored. Recorded because AGENTS §5 treats a failed-looking
  sanity check as a stop-and-verify moment; it was verified before
  proceeding.
- `git ls-files data/processed` shows only `.gitkeep` tracked, so
  these four tables were never committed — the exception is what
  makes a future `git add` possible at all.
- **Spec ambiguity, flagged rather than silently resolved:** H1's
  TITLE says "Commit the essential derived tables", but H1a — the
  actual instruction — only specifies adding the `.gitignore`
  exception (and forbids widening it). Read literally, the body asks
  for the exception; a literal `git commit` would additionally
  require staging data files (large, gitignored-by-design per AGENTS
  §2) and the standing rule here is "commit only when asked". So:
  exception added (done), files NOT committed — if a commit of these
  four tables was intended, that is a one-line follow-up
  (`git add` the four paths + commit) for the user to authorize.
---

## [H2] — requirements.txt: torch + fair-esm uncommented, transformers + huggingface_hub added, all four pinned from `pip freeze`

Status: DONE (H2a: versions read from the venv directly, not guessed)

Time started / finished: 23:39 / 23:41

What I did (H2a):
- Ran `venv/bin/pip freeze` and `pip list` and took the versions of
  exactly the four packages H2a names.

Actual output (verbatim, pip freeze):
```
fair-esm==2.0.0
huggingface_hub==1.33.0
torch==2.14.0
torchmetrics==1.9.0
transformers==5.17.0
```
- Replaced the trailing comment block in requirements.txt:
```
# Added later, once you're ready for scoring (large download):
# torch
# fair-esm
```
  with:
```
# Scoring dependencies (H2: uncommented and version-pinned to the venv —
# versions read from `pip freeze`, not guessed):
torch==2.14.0
fair-esm==2.0.0
transformers==5.17.0
huggingface_hub==1.33.0
```

Verdict: PASS — all four packages present with installed versions
pinned; no other line in requirements.txt touched. (torchmetrics
1.9.0 and pytorch-lightning 2.6.6 are also installed but were NOT
added — H2a names four packages, and widening the change would not be
its scope; they remain resolvable as transitive/other requirements as
before.)

Files created/modified: `requirements.txt`.

Anything unexpected or worth flagging:
- The venv also carries `torchmetrics==1.9.0` and
  `pytorch-lightning==2.6.6` as top-level installs; if any script
  imports them directly, a fresh `pip install -r requirements.txt`
  will still resolve them transitively or fail loudly — either way
  this is pre-existing behavior, unchanged by H2.
---

## [H3] — LICENSE recommendation drafted; NOT added (user's decision, flagged open)

Status: DONE (draft delivered in this log only — H3a explicitly says
do not add the file)

Time started / finished: 23:41 / 23:43

What I did (H3a):
- Checked what would actually ship under a license before
  recommending one: third-party material (mthfrModel reference copy,
  ProteinGym/ThermoMPNN(-D)/SaProt/Epistasis/openfold/Pfam checkouts,
  model weights) all lives under gitignored paths (`data/raw/`,
  `data/external/`) and would NOT be part of a public push; the
  committable tree is the project's own scripts/docs/notebooks/config.

### H3a — quote-ready recommendation (NOT applied; open item for the user)

> **License recommendation (draft — no LICENSE file added; this is
> the user's decision, flagged open per H3a).** A permissive license —
> **MIT** — is a reasonable default for this repository: the code and
> write-ups are the project's own work, and everything third-party
> (the mthfrModel reference copy, the ProteinGym / ThermoMPNN /
> SaProt / Epistasis / openfold checkouts, model weights) lives under
> gitignored paths that are not shipped with the repo, so no
> third-party license obligations travel with a public push. MIT is
> short, universally understood, and permits reuse — including by
> reviewers who re-run the analysis. Alternatives worth two minutes of
> thought: **Apache-2.0** if you want an express patent grant
> (slightly heavier); **GPL-3.0** if you want derivative works to
> remain open (stronger copyleft, more friction). Two additions when
> the time comes: (i) if the manuscript text may be reused separately
> from the code, license the write-up content under a CC license
> (e.g., CC-BY-4.0); (ii) add a `CITATION.cff` (or a citation
> section) pointing at the preprint/paper once one exists.

Verdict: PASS — recommendation drafted as instructed; **no LICENSE
file created** (H3a forbids it); choice flagged as an open decision
for the user. Combined with H6 this is one of two "human decides"
items in Group H.

Files created/modified: this log entry only.

Anything unexpected or worth flagging:
- One wrinkle for whoever decides: the repo carries uncommitted work
  from several sessions (see session context) — the license choice
  should be made before the first public push, not after, since
  license terms attach at distribution.
---

## [H4] — Minimal run-all for headline results: README section added (13 scripts, dependency-ordered, existence-verified)

Status: DONE (H4a allows "a short script or README section" — the
README section was chosen: a listing needs no new run-order code that
could itself be wrong; every line maps to an existing script)

Time started / finished: 23:43 / 23:46

What I did (H4a):
- Mapped each RESULTS.md headline number to its producing script by
  grepping `to_csv`/output paths in the scripts themselves, not from
  memory: e.g. `task32_analysis_table.csv` ← scripts/32 (L168);
  `task_AC4_esm1v_member*` ← scripts/86; `task_T3T4T5_reliability_audit`
  ← scripts/98; `task_AB2_proteingym_model_comparison` ← scripts/71;
  `task_V2_thermompnn_ddg` ← scripts/68 (L417); `task33_delta_esm_nulls`
  ← scripts/33; `task_AA4_detection_floor` ← scripts/72;
  `task53_g1_global_specific` ← scripts/53; `task91_a2_disattenuation`
  ← scripts/91; rho = −0.0733 appears in scripts/77/78/93 (the V4
  headline producer is scripts/77, per CLOSEOUT_LOG L198's re-verify).
- Traced the actual dependency chain by reading each script's inputs:
  phase5 ← scripts/16 (L124), own_context_metrics ← scripts/17,
  the 10,757/654 frame ← scripts/32 (needs 16+17), script 91 needs
  task32 (L111) + `task_AC4_esm1v_summary` (L112, from scripts/86),
  script 98 reads task32 + the five AC4 members + task58 (from
  scripts/58), script 97 reads the outputs of scripts 71/78/79/83
  (T_AB2/T_79/T_83/T_78).
- Appended a "## Reproducing the headline results" section to
  `README.md` (after the existing "Pipeline order" section): an
  ordered 11-step list scoped to what verifies RESULTS.md /
  PROJECT_SUMMARY_FINAL.md, with conventions (venv, foreground,
  N_BOOT=10000 + smoke first), the heavy/model steps marked, each
  script's claim + output named, the committed-backing-tables note
  (ties to H1), and a pointer to the review log for scripts 104–107.
- Existence-verified every script named in the section:

Actual output (verbatim, existence check):
```
OK  scripts/32_delta_esm_primary.py
OK  scripts/33_delta_esm_signflip_null.py
OK  scripts/53_g1_global_specific_epistasis.py
OK  scripts/68_thermompnn_ddg_epistasis.py
OK  scripts/77_thermompnnD_double_mutant_interaction.py
OK  scripts/71_proteingym_model_comparison.py
OK  scripts/86_ac4_esm1v_five_members.py
OK  scripts/98_t3_t4_t5_reliability_audit.py
OK  scripts/96_b4_debias_interaction.py
OK  scripts/97_holm_family.py
OK  scripts/72_mthfr_detection_floor.py
OK  scripts/91_a2_disattenuation.py
OK  scripts/107_e2_dimer_distance_recompute.py
```
plus `scripts/58_j2a_proposal_checklist.py`,
`scripts/78_thermompnn_multivariable_controls.py`,
`scripts/79_alignment_depth_discriminator.py`,
`scripts/83_ae3_clade_test.py` (the 97 prerequisites) — all OK.

Verdict: PASS — H4a's scope respected (headline-verifying scripts
only, not an exhaustive run-all); order is dependency-driven; no
script cited that does not exist on disk (AGENTS §5); α stated as
0.05 everywhere (bound to the run per F1, so README and log cannot
contradict each other).

Files created/modified: `README.md` (one section appended; nothing
existing removed or reworded).

Anything unexpected or worth flagging:
- The section documents the DUAL path to verification: check the
  committed headline tables (H1) without re-running models, or run
  the chain. This matters because the model steps (86, 68/77) are
  the only genuinely expensive ones — the statistical claims
  (33, 53, 72, 91, 97) are seconds-to-minutes on the committed
  tables.
- Script 98 silently needs `task58_150m_check.csv` (scripts/58) —
  noted inline in the README rather than left for a reader to hit.
---

## [H5] — PROVENANCE.md created: every external fetch compiled with source/date/checksum + citations

Status: DONE (new file created, exactly as H5a asks; every field
sourced from a log line; missing fields marked "not logged" instead
of guessed)

Time started / finished: 23:44 / 23:47

What I did (H5a):
- Pulled provenance records from where they actually live — scripts
  49/68/74/77 docstrings, DEEPDIVE_LOG (AB1/AA6/AA7/AD entries),
  CLOSEOUT_LOG (Z3a/Z3b), SESSION_LOG (V1/Pfam/EVcouplings),
  OVERNIGHT_LOG, DISATTENUATION_LOG (T6c/Z3), FOLLOWUP/MIGRATION
  chains — and compiled them into a new root file
  `PROVENANCE.md`, structured as: the five task-named datasets
  (GB1, GRB2, ProteinGym, ThermoMPNN weights, SaProt), then every
  other external asset on disk (ClinVar, Epistasis, foldseek,
  Pfam/GB1 alignments, ProteinGFourMutants, openfold, 2GB1, ESM
  weights, mthfrModel, plus the EVmutation NOT-obtained record), then
  notes.
- The five named datasets, verbatim key fields (all cited in the
  file): GB1 — Zenodo 5014984 / eLife 2016;5:e16965, fetched
  2026-09-22, md5 89e8d0f088466a1e29714721ed7967e8. GRB2 —
  ProteinGym v1.3 zero-shot zip member, fetched 2026-09-23→24,
  49,594,484 network B, md5 e6730c414e8563050837b06ad165c4bf.
  ProteinGym — catalog md5 c434631737013fceb56efc98056151e0,
  MTHR scores 29,370,765 B md5 6222922d3c4b69d043dc50b802814c7c
  (with the 7f9ddcc-docstring-slip reconciliation story carried
  verbatim), MSA md5 7f9ddcc0589f5f93821e8c0a3e5bb539, AB1 fetch
  2026-09-23 21:34. ThermoMPNN — Kuhlman-Lab repo metadata 2026-09-23
  (blob sizes enumerated), sparse clone 125 MB, ThermoMPNN-D clone
  125,488 KB 2026-09-24 with its three in-repo checkpoints' byte
  sizes. SaProt — HF URL, fetched 2026-09-23 16:56–17:01,
  2,606,464,143 B, sha256 2f82f3d5aa1df7bb9eee67bf5f5816269a35caff42e520ab593bc05369732346
  verified against HF's LFS x-linked-etag.

Verdict: PASS — H5a's three required fields (source URL, fetch date,
checksum where logged) present for every dataset that has them; the
"not logged" markers (exact GB1 download URL, Pfam source URL, clone
commit hashes, per-file ESM weight URLs/md5s) are stated as absent
rather than reconstructed.

Files created/modified: `PROVENANCE.md` (new, repo root).

Anything unexpected or worth flagging:
- The compilation surfaced one record that is itself a non-event:
  EVmutation/EVcouplings data was chased across six endpoints and
  NEVER OBTAINED (code-only repo, 404s, 502s) — recorded in
  PROVENANCE.md as a not-obtained item so a future reader doesn't
  hunt for a file that was never fetched (SESSION_LOG L1578–1607).
- Two documentation-quality findings land here rather than in a
  separate task: the MTHR scores-CSV md5 slip (script 71's
  docstring, already reconciled with disclosure — carried into
  PROVENANCE.md so the correction lives next to the number) and the
  fact that ESM weights were fetched by libraries with no per-file
  provenance logged — a gap this file names honestly rather than
  papers over.
---

## [H6] — Archival DOI registration: NOT ATTEMPTED — human action item (per H6's own instruction)

Status: NOT ATTEMPTED BY DESIGN — flagged as a human action item,
exactly as the task instructs ("do not attempt it")

Time started / finished: 23:47 / 23:47 (flagging only)

What I did: recorded the flag; performed no network action, no
account action, no Zenodo/GitHub interaction of any kind.

**Human action item (user):** archival DOI registration (e.g., via
Zenodo's GitHub integration) requires the user's own GitHub and
Zenodo account linkage. When ready: enable the Zenodo–GitHub hook for
the repository (or upload a release manually), which mints a
versioned DOI + a concept DOI; then cite it in the manuscript and
`CITATION.cff` (see H3's draft note). Prerequisites before the first
archive-worthy release: decide the LICENSE (H3 open item), commit the
H1/H2/H4/H5 packaging changes, and resolve the open items flagged in
this log (RESULTS.md α correction, region-boundary permission) so
the archived version doesn't ship a known error.

Verdict: correctly NOT attempted; flagged.

Files created/modified: this log entry only.

Anything unexpected or worth flagging:
- Nothing — this is the only Group H task whose completion is
  definitionally outside the session's capability; the flag is the
  deliverable.
---

## SUMMARY

Session: 2026-09-26 21:55:08 → 23:49:44. All 20 tasks of
`MANUSCRIPT_REVIEW_RESPONSE.md` executed and logged above (entries
A1–A3, B1, C1, D1–D2, E1–E2, F1–F2, G1–G3, H1–H6 — 20 entries for
the spec's 20 `**Task**` headers, 1:1), in the doc's own
suggested order.

### Completed vs blocked

**Completed (20/20 entries):** Group A (A1 rank-degeneracy
confirmation, A2 corrected decomposition, A3 severity-baseline
paragraph), Group B (B1: the two omitted Results-surface compilations,
150M non-replication ρ=+0.0978 / sign agreement 53.11% and the
five-seed ensemble mean with its ρ=−0.028508 marginal caveat),
Group C (C1), Group D (D1, D2), Group E (E1, E2), Group F (F1, F2),
Group G (G1, G2, G3), Group H (H1–H6).

**Blocked or open (7 items, none silently resolved):**
1. `MTHFR_RESEARCH_PAPER_SUMMARY.md` does not exist — the task doc's
   "both write-up documents" premise is half-false (A1; `find` empty,
   `docs/writeups/` holds only `PROJECT_SUMMARY_FINAL.md`). Blocked
   with the exact filename, no substitution made.
2. **RESULTS.md L11 α correction → OPEN ITEM (F1).** RESULTS.md is
   off-limits (prior session's "second and final" edit); flag only.
3. **DISATTENUATION_LOG L147 (K19) repeats the same α error → flagged,
   never edited** (prior log, AGENTS §7).
4. Region-boundary **permission not confirmed → user follow-up**
   required before any public use (G3).
5. **LICENSE choice → user decision**; draft delivered, no file added
   (H3).
6. **Zenodo DOI registration → human action item**, not attempted (H6).
7. Rule-4 assumption logged at A1: no task authorizes editing
   `PROJECT_SUMMARY_FINAL.md` or `RESULTS.md`, so every correction in
   this round is **delivered in this log for the user to apply**.

### Group A — corrected decomposition numbers in full

A1 (fresh, script 104): `pred_eb` is rank-identical to `ddg` — full V2
frame (10,141 rows) spearman = 1.0 exactly (deviation 0.000e+00),
matched frame (9,595 rows) 0.9999999999999999 (deviation 1.110e-16 =
scipy float arithmetic, not a rank difference), **exact rankdata
equality at every row both frames**, affine `pred_eb = ddg −
0.043861627579` (= ddG(A222V)) max|resid| = 4.441e-16. scripts/81's G4
quoted from its original run log; [V4]'s guard quoted; the write-up
sentence being corrected (PROJECT_SUMMARY_FINAL L212–215, "carries
genuinely independent information") quoted verbatim, untouched.

A2 (script 104, N_BOOT=10000, n=9,595 / 586 positions, same machinery
as 81, G7 bitwise-faithful <1e-12):
- Zero-orders: ρ(delta_esm, own_e_b) = **−0.077145**
  [−0.108573, −0.045804]; ρ(interaction_D, own_e_b) = **+0.015350**
  [−0.015245, +0.045252] (spans 0 = AD4's null); r12(ESM,
  interaction_D) = **−0.133576** [−0.189913, −0.078407].
- R²_E = 0.005951 [0.002098, 0.011788]; R²_T = 0.000236
  [0.000001, 0.002048]; **R²_full = 0.005977 [0.002266, 0.012159]**.
- **unique_T|ESM = 2.592206129884908e-05**
  [2.819130434001749e-07, 0.0012805869020266], p = 0.0, part_r +0.0051
  = **11.0% of interaction_D's own zero-order R², 0.43% of R²_full**.
- **unique_E|interaction_D = 0.0057416752588006**
  [0.0019513346004717, 0.0114129137209267], part_r −0.0758 = 96.5% of
  ESM's zero-order R², **96.1% of R²_full**.
- shared = 0.0002097157699209 = **3.5% of R²_full**; components sum to
  R²_full exactly. Full model explains **0.60%** of own_e_b rank
  variance in total.
- Mechanical label under 81's rule: case (i) "BOTH carry independent
  information" — but pre-registered as structurally weak (unique_T =
  (r2−r1·r12)²/(1−r12²) ≥ 0 identically ⇒ percentile CI cannot fall
  below 0 for ANY predictor; AD8's p printed <1/N for the same reason).
  Prior AD8 figure was unique_T = **42.8% of R²_full** under the
  degenerate pred_eb; with non-degenerate interaction_D it is **0.43%**.
- Regions (descriptive, no decision rule): region1 +0.118520
  [+0.061708, +0.174831] (unique_T 38.28% of R²_full); region2
  −0.076474 [−0.138062, −0.017321] (66.00%); region3 +0.013909
  [−0.045612, +0.071917] (0.10%); region4 +0.033255
  [−0.019891, +0.086427] (99.66%).
- Disclosed: first smoke EXIT=1 on G7 — my gate code compared CI
  columns at N_BOOT=300 against N_BOOT=10000 CSVs; corrected to the
  pre-registered rule (obs-always, CI-only-at-10000); rule unchanged.
  A3 delivered the corrected severity-baseline paragraph (raw ddG(v)
  as severity predictor, never interaction).

### Group C — mechanism null vs the real −0.088

Script 106, mechanism-only null (what a zero-interaction generative
mechanism mechanically produces for the shift statistic): null
**ρ = +0.9366244249321943**, CI [+0.933389201160778,
+0.9396189771832062], p < 1e-04 — against the real observed
**−0.08811806424891734** (CI [−0.1173334458953319,
−0.05951138449511738]). Verdict **SMALL with a sign contrast**: the
mechanism's mechanical product sits ~+0.94, so the real −0.088 is not
the mechanism's fingerprint — it is a small, sign-opposite residual.
All gates PASS; CSV `data/processed/task106_c1_mechanism_null.csv`.

### Group D — prediction vs observed, inside/outside [0,1]

D1 inputs (re-derived from the five ESM-1v checkpoints' own CSVs, both
constructions): r_XX = 0.8826369680851056, r_YY = 0.8821503142468713,
r_XY = 0.9993872509298699 (median, rank scale), VarX =
9,642,753.999990705, VarY = 9,642,753.999981407; D2a identities hold to
rel < 1e-12 on both constructions × all 5 checkpoints.
D2 (script 105, Lord's formula verbatim, N_BOOT=10000, seed 0):
- **Forward prediction (rank/primary): −190.9323334249339 — OUTSIDE
  [0,1]** (numerator −2,256,281.2 / denominator 11,817.18).
  Secondary (raw/Pearson): **−178.60385424945227 — OUTSIDE [0,1]**.
  Per-checkpoint sensitivity: −190.93, −201.66, −159.40, −149.94,
  −264.21 — every variant outside [0,1].
- Bootstrap: 10,000/10,000 draws negative, **fraction in [0,1] =
  0.0000** both constructions (R: p2.5 −301.758 … p97.5 −130.314).
- **Observed delta reliability = +0.08436481140085886** with CI
  [+0.052159, +0.122589] — **inside the prediction's interval: False**.
- Verdict (verbatim): **INCONSISTENT — prediction outside [0,1],
  observed outside the prediction's empirical interval.** Interpretation
  as printed: sign is certain, magnitude is ill-conditioned (1−r_XY ≈
  6e-04); the classical formula assumes uncorrelated errors, both arms
  share checkpoint noise (r_XY 0.9994 ≫ r_XX/r_YY 0.88) — the formula
  answers "not coverable" by returning −191 rather than a plausible 0.08.

### Group E — Nambiar restatement + dimer recompute

E1 (no computation): Nambiar et al.'s finding is **qualitative —
heatmap-vs-contact-map pattern matching** (`heatmap_and_contact`) plus
**`circular_independent(top_n_edges=20)` circular graphs** on TEM-1/
YAP1/Pab1 RRM2 — **not** a quantitative distance-stratified accuracy
table (none exists in paper or repo). Their calibration = monotone
ϕ1/ϕ2 transform, no disattenuation (DISATTENUATION_LOG L394/L400);
headline Pearson **0.37 / 0.34 / 0.26**. E1b: the "structurally
requires a many-background, two-path design" sentence is labeled **this
project's own hypothesis** (PROJECT_SUMMARY_FINAL L164–168 quoted,
untouched).
E2 (script 107, deterministic census, file-verified gates all green):
**monomer 9,232/9,595 = 96.2168% → dimer-aware four-pair min
9,128/9,595 = 95.1329%**; task's literal sensitivity (variant fixed in
chain A) = 96.2168% exactly (the other 222 copy alone never pulls a row
in — all 104 flips come from the variant's chain-B copy); 104 rows
flip into contact range; position-level 563/586 → 557/586;
**coordinate counts: monomer 59 missing (596 with coords) → dimer 54
missing (601 with coords), chain B rescues exactly 392–396**;
inter-subunit 222–222 = 70.530 Å. One first-run KeyError (missing
f-prefix in a gate) disclosed in [E2]; second run EXIT=0.

### Group F — α discrepancy: resolution + open item

**Resolution: script 97 used (and pre-registered) α_FWER = 0.05** —
four independent on-disk confirmations (docstring METHOD, `ALPHA =
0.05` at L144, CSV thresholds = Holm-at-0.05, RELIABILITY_LOG's own
"5/5 … 0.05" run lines + VERIFIED_FINDINGS rows 92–93). Script is
correct, no fix needed or made. **RESULTS.md L11 says 0.01 → wrong**
("family-wise Holm (5/5 core at α_FWER = 0.01; 8/8 in the m = 8 set)"):
at 0.01 the m=8 family rejects **5/8, not 8/8** (diagnostic on script
97's own holm(): core5 5/5 at both α; core8 8/8 at 0.05, 5/8 at 0.01).
Likely origin noted: 0.01 = 0.05/5, the m=5 first-rank threshold.
**Open item — not edited** (RESULTS.md off-limits); minimal correct fix
when authorized: one token, 0.01 → 0.05. DISATTENUATION_LOG L147 (K19)
carries the identical error — flagged, prior log, never edited.
PROJECT_SUMMARY_FINAL.md contains zero "Holm" occurrences.

### Group G — three verifications

**G1:** estimator-differences table delivered (MTHFR 4-condition WLS
with measured SEs + measured WT/background anchors + 43,028
per-condition flip units, non-degenerate absolute arm vs GB1 uniform
weights, measured f(WT)=1.0, 57 per-variant flips, degenerate absolute
arm vs GRB2 uniform weights, c-hat = 0.855271 median-ratio proxy anchor,
689 per-variant flips, same degeneracy) with the plain statement:
controls establish null-centering and GRB2 short-range multi-partner
detection (ρ=+0.1153, p=0.0019; GB1 correctly null at p=0.3849) —
**no control establishes detection validity for a single distant fixed
background**, a stated design limitation.
**G2:** ProteinGym's own metadata row for `GRB2_HUMAN_Faure_2021`:
**`year = 2022`** — publication year 2022 (Faure 2022); "2021" is part
of the dataset ID only. Project's one citation already says Faure 2022;
no document carries a wrong year.
**G3:** provenance located in `scripts/lib/regions.py` L1–24 (personal
communication, Nishka Kishore via Fritz Roth, Sept 2026, primer file
from Song Sun; three-way cross-validation; bounds R1 2–147, R2 148–294,
R3 295–474, R4 475–656). Acknowledgment draft delivered; **permission
for public use NOT confirmed → user follow-up required, not assumed.**

### Group H — packaging + human action item

H1: `.gitignore` narrow `!` exceptions added and verified both ways
(target four: task32 frame, five AC4 ESM-1v member CSVs, AB2 comparison
table, V2 ThermoMPNN table — all TRACKABLE; controls still IGNORED; full
`data/processed/` stays ignored; nothing committed). H2:
requirements.txt — `torch==2.14.0`, `fair-esm==2.0.0`,
`transformers==5.17.0`, `huggingface_hub==1.33.0` (all from `pip
freeze`). H3: LICENSE recommendation drafted (MIT default rationale +
alternatives), **no file added — user's decision, open**. H4:
README section "Reproducing the headline results" — 11 ordered steps /
13 scripts, all existence-verified, dependency-chained (16→17→32→33…),
heavy steps marked. H5: **`PROVENANCE.md` created** — the five named
datasets (GB1, GRB2, ProteinGym, ThermoMPNN, SaProt) plus every other
external asset, each field cited to its log line, missing fields marked
"not logged". H6: **Zenodo DOI registration NOT attempted — human action
item** (needs the user's GitHub/Zenodo linkage); prerequisites listed
(license decision, commits, open items above).

### The single most important thing to look at first

**The [A2] corrected decomposition** — the write-up's flagship
"ThermoMPNN carries genuinely independent information from ESM-2's
shift" claim. With the non-degenerate predictor, ThermoMPNN-D's
zero-order is a null spanning 0 (+0.0154 [−0.0152, +0.0453]) and its
unique joint contribution is **0.43% of R²_full** (down from 42.8%
under the rank-degenerate pred_eb), while the full model explains
**0.60%** of own_e_b rank variance total — ESM-2 keeps 96.1%. Read
[A1] for why the old number was an artifact (exact rank identity) and
[A2]'s structural note for why the old case-(i) label could not fail.
