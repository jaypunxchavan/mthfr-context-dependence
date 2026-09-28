# PHASE 1b — Placebo follow-up: same-site vs same-substitution probe, and Phase 2 pre-registration

**Written:** 2026-09-27 (Claude, planning) · **Executor:** OpenCode
**Repo:** `~/Desktop/mthfr-context-dependence` · **Doc lives at:** `docs/tasks/phase1b-placebo-followup/PHASE1B_PLACEBO_FOLLOWUP.md`
**Log to write:** `docs/tasks/phase1b-placebo-followup/PHASE1B_LOG.md`
**Scripts:** next free numbers. Phase 1 used 109–119, so expect **120, 121, 122** — verify with `ls scripts/ | tail -20` before creating anything.

---

## 0. Why this session exists (read first)

Phase 1's F1 placebo-background test returned a verdict *between* branch 2 and branch 3
(AE = branch 3, W = branch 2, COMMON = branch 2). Verified numbers from `PHASE1_LOG.md`
that this session builds on (all are reproduction gates below — do not retype from memory,
recompute and compare):

| Quantity | Value |
|---|---|
| Full-frame anchor ρ (delta_ESM vs own_e_b, 10,757 variants / 654 positions) | −0.088118 |
| AE frame: A222V ρ | −0.104322, CI [−0.166932, −0.041325] |
| AE frame: 56 placebos, mean ρ_b | −0.024625 |
| AE1 = 18 backgrounds A222X (X ∉ {A, V}), **same site as A222V**, mean ρ_b | −0.055209 |
| AE2 = 38 backgrounds A→V at other alanine positions, **same substitution as A222V**, mean ρ_b | −0.010138 |
| W frame: A222V ρ / COMMON frame: A222V ρ | −0.072547 / −0.104044 |

**The observation motivating this doc:** the AE1 "placebos" are not real placebos. They share
A222V's *site*, while AE2 shares its *substitution*. F1's AE placebo mean was pulled negative
mostly by AE1. That decomposition was made **after** seeing F1 (it is labelled POST-HOC in
`PHASE1_LOG.md`), so everything in Part A below is **exploratory / hypothesis-generating**.
It cannot upgrade or replace the F1d verdict, and it must never be cited as confirmatory.
The confirmatory version is Phase 2 (Part B), whose design is frozen in Appendix A **before**
any Phase 2 scoring is run.

**Two parts:**
- **Part A (P1–P4): runs now, cached data only.** Position-cluster bootstrap analyses of
  the already-computed per-background ρ_b values.
- **Part B (Q1–Q4): design work only.** Audit feasibility/cost of a full-frame placebo run and
  freeze its pre-registration. **Nothing in Part B scores any model.**

---

## 1. Rules (inherited from `AGENTS.md` — that file governs; this section restates the ones that bite here)

1. **No new model scoring, no forward passes, no downloading model weights, in this session.**
   Cached CSVs only. Do not import `torch`/`esm` in any script written this session.
2. **Position-cluster bootstrap only** (resample positions with all their variants, with
   multiplicity). Never row-level. `N_BOOT=300` smoke run first, then `N_BOOT=10000` full,
   `SEED=0`. Every non-trivial analysis: construction + gates + decision rule written in the
   script's **docstring before its first run**.
3. **A failed gate means STOP that task and log it `BLOCKED` or `FAIL`.** Never loosen a
   threshold, edit a reference value, or re-run until it passes. Continue to independent tasks.
4. **Protected files — do not edit, do not "fix"**: `RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
   `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, and **every prior session's log including
   `PHASE1_LOG.md`**. If a correction to a prior log seems needed, flag it *in place in the new
   log* (`PHASE1B_LOG.md`) only.
5. **Do not commit, do not push.** Arnav commits after Claude reviews.
6. Python is always `venv/bin/python3`, never bare `python3`. Do not `pip install` anything;
   if a package is missing, log the dependent sub-task `SKIPPED` with the import error verbatim.
7. Every number in the log must be **verbatim output**, not paraphrased. Save each script's full
   run output to `docs/tasks/phase1b-placebo-followup/PHASE1B_<TASK>_FULL_OUTPUT.txt`.
8. The sign-flip re-derivation null has a limited interpretation (see `AGENTS.md`); it is not
   used in this session. Do not introduce it.
9. Disclose, in the entry, any deviation from this doc — even ones you think are harmless.
   Prior sessions found that the *task doc's own premises* were sometimes wrong (F1 found the
   "common ~120-position subset" did not exist). If a premise here is wrong, **say so in the
   log, handle it transparently, and do not paper over it.**

---

## S1. Logging instructions

Create `PHASE1B_LOG.md` **first**, containing this template, then append one entry per task
**immediately after that task finishes** (do not reconstruct from memory at the end):

```
## [TASK ID] — [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (verbatim, not paraphrased):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

After all tasks, append `## SUMMARY` (see S2).

## S2. Mandated SUMMARY contents

In this order: (1) **READ THIS FIRST** — P3's primary gradient result and outcome, verbatim
numbers; (2) P2 site-vs-substitution contrast, verbatim; (3) P4 descriptive numbers;
(4) Q1 cost table and whether a full-frame run needs detached execution;
(5) Q2 held-out-position counts; (6) Q3 arm sizes and whether the subset rule triggered;
(7) Q4 sha256 of the frozen text and confirmation it is byte-identical to Appendix A;
(8) every gate: name, PASS/FAIL, value; (9) a plain statement of what this session changes
about the central claim — **"nothing" is an acceptable and expected answer**; (10) the single
most important entry for Claude to read first, with its line number in the log.

---

# PART A — Cached-data probe (EXPLORATORY, post-hoc-motivated)

**Inputs (all must exist; verify in P1):**
`data/processed/task109_placebo_rhos.csv` (175 rows), `data/processed/task82_ae_raw.csv`
(129,960 rows = 57 backgrounds × 120 positions × 19 subs), `data/processed/esm2_wt_scores.csv`,
the atlas table holding `own_e_b`, and **`scripts/109_placebo_background_test.py`** (reuse its
loading, join, usable-row, and ρ code — import it if importable, otherwise replicate
line-for-line and gate the replica against the CSV as G2 requires).

**Task P1 — Inventory, provenance, and reproduction gates** (script 120)

Read-only. Establish, from the real files:
- (a) The list of the 57 AE `bg_id`s: confirm **AE1 = 18 A222X placebos** (X ∉ {A, V}) plus
  `A222_V`, and **AE2 = 38 A→V at other positions**. For every AE2 background record
  position and confirm the wild-type residue there is Ala. Log any that are not.
- (b) **Selection provenance:** read the scripts that generated `task82_ae_raw.csv` (script 82)
  and `task69_w2_bg_raw.csv` (script 69). Quote, verbatim, the rule that chose the AE2 positions
  and the 30 W-series backgrounds (e.g. decile, random, fitness-based?). If either selection rule
  used anything fitness-related, flag it prominently: it bears on how AE2/W can be used as nulls.
- (c) Reproduction gates, all against recorded values:
  - **G1** `task109_placebo_rhos.csv` has 175 rows; AE-frame rows = 57.
  - **G2** Recompute ρ_b from raw for all 57 AE backgrounds; max |diff| vs the CSV < 1e-9.
  - **G3** A222V AE ρ = −0.104322 (to 1e-6); AE1 mean = −0.055209 (n=18); AE2 mean = −0.010138
    (n=38) (each to 1e-6).
  - **G4** Full-frame anchor ρ = −0.088118 reproduces from the atlas table (to 1e-6).
- (d) Grantham gate for later use: locate the Grantham implementation in `scripts/lib/`
  (`grep -rn -i grantham scripts/lib`). Verify against published Grantham (1974) values:
  A–V 64, I–V 29, L–V 32, L–I 5, F–Y 22, C–W 215; symmetric; zero diagonal. If absent or any
  value fails: **P3's primary metric is BLOCKED — log it, do not improvise a replacement.**
  (Earlier in this project a Grantham implementation had constants inside the square root.)

**Task P2 — Same-site vs same-substitution contrast** (script 121; EXPLORATORY)

*Pre-register in the docstring before running.* Groups in the AE frame: S = AE1 (n=18),
V = AE2 (n=38). Statistic: D = mean ρ_b(S) − mean ρ_b(V).
- Inference: (i) position-cluster bootstrap over the 120 AE positions — each draw recomputes
  all 56 ρ_b on the resampled rows, then the group means, then D; 95% percentile CI.
  (ii) label-permutation p (10,000 shuffles of S/V labels across the 56 backgrounds), two-sided.
- Also report, without testing: A222V's ρ and its rank within S∪{A222V} and within V∪{A222V}.
- **Rule (exploratory):** "SITE EFFECT PRESENT" iff the bootstrap CI of D excludes 0;
  otherwise "NOT DISTINGUISHABLE". Either outcome is logged as exploratory.
- Interpretation guard, to be printed by the script: *A222V shares the site with S and the
  substitution with V. D < 0 means shared site tracks A222V's e.b more than a shared
  substitution does. That is compatible with a real site-specific effect; it is NOT evidence
  of a generic artifact and NOT evidence of A222V-specificity.*

**Task P3 — Similarity-to-valine gradient within S** (script 121; EXPLORATORY)

*Pre-register in the docstring before running.* For the 18 S backgrounds (A222X), let d_b =
Grantham distance between X and V (**primary metric; fixed now**). Statistic:
T = Spearman(ρ_b, d_b) over the 18. Prediction if the anchor tracks A222V-like structure:
more V-like (small d) → more negative ρ_b → **T > 0**.
- Inference: position-cluster bootstrap (AE positions), each draw recomputes all 18 ρ_b then T;
  95% percentile CI. Also: label-permutation p (10,000), leave-one-out range of T (drop each of
  the 18 in turn), and the bootstrap SE with **minimum detectable |T| ≈ 2.8 × SE** stated, since
  n=18 is small.
- **Rule:** SUPPORTED iff CI lower bound > 0 **and** T > 0 in all 18 leave-one-out fits;
  REVERSED iff CI upper bound < 0; else **NOT RESOLVED**. NOT RESOLVED must be reported as
  "n=18 cannot resolve this," never as "the gradient is flat."
- Print the 18-row table sorted by d_b: X, d_b, ρ_b, CI.
- **Secondary, descriptive only (no decision rests on these):** BLOSUM62(V, X) via
  `Bio.Align.substitution_matrices` (SKIPPED if not importable — no install), and |ΔKD| with
  Kyte–Doolittle: A 1.8, R −4.5, N −3.5, D −3.5, C 2.5, Q −3.5, E −3.5, G −0.4, H −3.2, I 4.5,
  L 3.8, K −3.9, M 1.9, F 2.8, P −1.6, S −0.8, T −0.7, W −0.9, Y −1.3, V 4.2. Compute the same
  T-style Spearman with the same bootstrap. Do not pick whichever metric "works".

**Task P4 — Non-site placebos only (DESCRIPTIVE; replaces nothing)** (script 121)

Restrict to placebos that do **not** share A222V's site: V (AE2) in the AE frame; the W-series in
the W frame. For each, report exactly what F1 reported: n, mean ρ_b and background-bootstrap 95%
CI, median, range, A222V's signed rank, and the empirical one-sided
**p_spec = (1 + #{b : ρ_b ≤ ρ_A222V}) / (1 + n)** (this is the same quantity Phase 2 will use).
**No decision rule.** Label the entry `POST-HOC, DESCRIPTIVE; does not replace F1d; may not be cited
as support for background-specificity.` Its purpose is to stop the AE1 contamination from
being silently carried into a write-up.

---

# PART B — Phase 2 design audit and frozen pre-registration (NO SCORING)

**Task Q1 — Feasibility and cost audit** (read-only; inline commands allowed, log them verbatim;
if you write a script it must not import torch/esm)

Read the scripts that produced the cached scores (scripts 63, 69, 82 and whatever they call).
Report, with file/line quotes: (a) ESM-2 model size/checkpoint used; (b) scoring method
(masked-marginal at each position? wt-marginal? how many forward passes per
(background, position)); (c) device and any recorded runtime or timing (log lines, timestamps,
file mtimes — cite the source; if no timing exists, write `NOT AVAILABLE`, **do not run a model
to measure it**); (d) computed table: passes per background for the full 654-position frame,
and total passes for candidate arm sizes 18 (S) + N_V + 40 (G) — see Q3 for N_V; (e) whether
projected wall time exceeds the ~55–65 min foreground limit (→ needs detached/`nohup` execution).

**Task Q2 — Held-out positions** (script 122 or inline)

Compute, from the real files: the set of positions in the 654-position analysis frame; the set
in the AE frame (120) and the W frame (120); the **held-out set H = frame positions not in AE ∪ W**.
Report |H| and the number of usable variants in H. Confirm 222 is excluded from every set as a
target position (L1 established this for the analysis table — cite it).

**Task Q3 — Arm roster counts (enumerate only, choose nothing)**

From the wild-type sequence in the repo: count alanine positions ≠ 222 that lie in the
654-position frame (= N_V). Report N_V, and whether N_V > 60. Do not select any backgrounds.
Selection rules are frozen in Appendix A.

**Task Q4 — Freeze the pre-registration**

Extract the Appendix A frozen block into `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`
(`mkdir -p` the directory) using **exactly** this line-anchored command (a looser
`sed '/FROZEN_BEGIN/,...'` pattern would also match this paragraph and leak text):

```
awk '/^<<<FROZEN_BEGIN>>>$/{f=1;next} /^<<<FROZEN_END>>>$/{f=0} f' \
  docs/tasks/phase1b-placebo-followup/PHASE1B_PLACEBO_FOLLOWUP.md \
  > docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
```

Then: confirm the output is 86 lines and contains no `FROZEN` string; record
`shasum -a 256` of the file in the log. **Gate G-Q4:** the hash must equal
`420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`. If it does not, STOP,
log `FAIL`, and report both hashes — do not re-extract until it matches or edit anything to
force a match. Confirm **no** scoring was launched. **Do not edit the frozen text.** If Q1–Q3 reveal that the design is infeasible or a premise is wrong, log that
fact plainly and stop; Claude and Arnav decide any change in a *new* versioned file — never by
editing v1 after Q4.

**Task R1 — Housekeeping (read-only)**

`git status --short` and `git diff --stat` to list every file this session created or changed.
Confirm no protected file appears. Do not `git add`.

---

## Appendix A — FROZEN text for `PHASE2_PREREG.md`

<<<FROZEN_BEGIN>>>
# PHASE 2 — Full-frame placebo-background test: pre-registration v1

Frozen 2026-09-27, before any Phase 2 scoring. Authors: Arnav (PI), Claude (planning).

## 1. Question

Over the full 654-position frame, is the ESM-2 background-shift anchor for A222V (ρ = −0.088118,
delta_ESM vs own_e_b) distinguishable from what arbitrary single-substitution backgrounds
produce against the same target?

## 2. Statistic

For each background b: delta_b(v) = S(v | b) − S(v | WT). ρ_b = Spearman(delta_b, own_e_b), where
own_e_b is A222V's own measured e.b (the anchor's target), over all usable variants in the
10,757-row frame, excluding rows whose target position equals the background's position.
A222V's own ρ must reproduce the anchor (gate G-A).

## 3. Arms (fixed before scoring; all fitness-blind)

- **Arm S (same-site):** the 18 substitutions A222X, X not in {A, V}.
- **Arm V (same-substitution):** A→V at every alanine position other than 222 present in the
  frame. If the number of such positions exceeds 60, use a seed-0 random sample of 40
  (`numpy.random.default_rng(0).choice(sorted_positions, 40, replace=False)`). This condition
  is decided by the position count alone.
- **Arm G (generic):** 40 backgrounds, each a single substitution at a distinct frame position
  other than 222, position drawn uniformly and mutant amino acid uniformly among the 19
  non-wild-type residues, using `default_rng(0)`; drawn and written to disk before any scoring.

**Null set N = Arm V ∪ Arm G.** Arm S shares A222V's site and is **not** a null; it is reported
as a separate comparison arm.

## 4. Inference

Position-cluster bootstrap (positions as clusters, all variants with multiplicity),
N_BOOT = 10000, seed 0, for all ρ_b confidence intervals.
One-sided empirical p (direction pre-stated negative, as for the anchor):
**p_spec = (1 + #{b in N : ρ_b ≤ ρ_A222V}) / (1 + |N|)**, computed on
(a) the full frame and (b) the held-out set H = frame positions not in the Phase 1 F1 AE or W
frames (ρ recomputed on H rows only, for A222V and every background). H was never used in F1
and is the out-of-sample evaluation of the hypothesis raised by F1's post-hoc AE1/AE2
decomposition.

## 5. Decision rule (constants are judgment constants, fixed now)

- **GENERIC:** p_spec(full) > 0.10.
- **A222V BEATS NON-SITE BACKGROUNDS:** p_spec(full) ≤ 0.05 **and** p_spec(H) ≤ 0.10.
- **INDETERMINATE:** everything else, including full and H disagreeing.

Wording rule: only the second outcome may be written up as supporting background-specificity of
the anchor. GENERIC and INDETERMINATE must be reported with equal prominence in every write-up.

Reported irrespective of the outcome above:
- **Site contrast:** D_site = mean ρ_b(Arm S) − mean ρ_b(N), with position-cluster bootstrap 95%
  CI and a label-permutation p (10,000 shuffles). Interpretation: D_site < 0 means a shared site
  tracks A222V's e.b beyond arbitrary backgrounds; that is compatible with a real site-specific
  effect and is not evidence of substitution-specificity.
- **Within-site gradient:** T = Spearman(ρ_b, Grantham distance(X, V)) over Arm S, position-cluster
  bootstrap 95% CI, leave-one-out range, and the minimum detectable |T| ≈ 2.8 × bootstrap SE.
  SUPPORTED iff CI lower bound > 0 and T > 0 in every leave-one-out fit; REVERSED iff CI upper
  bound < 0; otherwise NOT RESOLVED, reported as "n = 18 cannot resolve this," never as "flat."

## 6. Secondary (non-decision) analyses

The same analysis after residualizing delta_b and own_e_b on region indicators (Phase 1 H1 found
region 4 differs systematically); and per-arm summary tables (n, mean, median, range).

## 7. Gates (a failed gate stops the run; thresholds are never loosened)

- **G-A:** A222V's ρ over the full frame reproduces −0.088118 to 1e-6.
- **G-B:** for at least three backgrounds already cached in `task82_ae_raw.csv`, freshly scored
  values on the cached positions reproduce the cached scores to 1e-6 (same model, same settings).
- **G-C:** no row with target position equal to background position enters any ρ_b.
- **G-D:** bootstrap identity (every cluster once reproduces the point estimate to 1e-12).
- **G-E:** each background scores at least 95% of the frame's positions.

## 8. Execution

Detached (`nohup`), one output file per background, resumable; the foreground harness kills
jobs at roughly 55–65 minutes. Smoke run first (N_BOOT = 300), then full.

## 9. Disclosure

The AE1/AE2 split that motivates this test was observed in Phase 1 after F1 was run (POST-HOC).
Confirmatory weight therefore rests on this frozen rule and on the held-out set H, not on the
Phase 1 numbers. Any deviation from this document must be disclosed in the log and, if it
changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
<<<FROZEN_END>>>

---

## What this session is NOT

- Not a rescue of F1: F1d's verdict stands as logged.
- Not permission to touch `RESULTS.md` (the α = 0.05 vs 0.01 fix still needs Arnav's explicit,
  fresh authorization).
- Not Phase 2 execution and not Phase 3.
