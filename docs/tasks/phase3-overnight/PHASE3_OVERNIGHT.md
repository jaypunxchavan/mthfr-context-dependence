# PHASE 3 overnight - GB1 regime map, RBD replication, multidms / global-epistasis target

**Written:** 2026-10-01 (Claude, planning) | **Executors:** OpenCode (sessions 3a and 3b), a detached driver (the night)
**Doc lives at:** `docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md`
**Logs:** `docs/tasks/phase3-overnight/PHASE3A_BUILD_LOG.md` (session 3a), `docs/tasks/phase3-overnight/PHASE3B_MORNING_LOG.md` (session 3b)
**Frozen pre-registrations (extracted in A1):** `docs/tasks/phase3-overnight/prereg/`
**Scripts:** next free numbers. Diagnostics IV used up to 152, so expect **153 and up**. Verify with
`ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` before creating anything. New shared code goes in
**new** files `scripts/lib/phase3_common.py` and `scripts/lib/phase3_guards.py`; do not modify any existing script or library.

---

## 0. What this is, what it folds in, and why it is three phases and not one

"All three" means the three items of the original Phase 3 plan, plus one addition that the plan needs to be doable:

| Module | What it is | Needs the GPU (MPS)? | Where it runs |
|---|---|---|---|
| **G** | GB1 regime map: the ESM-2 background-shift statistic across 400 fixed backgrounds, using Olson's full double-mutant matrix. **v2 pre-registration resolves the three open items from Phase 3a.** | yes, about 22,000 forward passes | night, stage S1 |
| **R** | Starr et al. 2022 RBD replication: the same design (background-shift statistic vs measured epistatic shift, placebo backgrounds) for the two single-substitution backgrounds N501Y (Alpha) and E484K (Eta) | yes, roughly 20,000 passes | night, stage S2 |
| **M** | (M1) a **monotone global-epistasis-aware target** for MTHFR, rebuilt from the cached data; (M2) **multidms** fitted on the RBD data, with an audit of whether MTHFR's own data can support it at all | M1 no; M2 no (CPU, separate environment) | M1 in session 3a (minutes); M2 night, stage S4 |

**Not in this run:** the ESM-2 model-size ladder. Re-scoring 96 MTHFR backgrounds at one model size took more than nine hours at 650M,
every further size is another long job, and 3B does not fit this machine. It is not required to finish Phase 3 and is better scoped
separately.

**Why the overnight job is a detached driver and not an OpenCode session.** Phase 2 showed that an unattended multi-hour job survives
only when it is (i) resumable with atomic writes, (ii) launched once under a lock, (iii) free of competing memory consumers, and
(iv) kept off battery. It also showed that an agent session left open for hours is itself one of those consumers. So:

- **Session 3a (OpenCode, supervised, a few hours):** acquire and verify data, freeze three pre-registrations, build and gate every
  script, run the cheap modules, time everything, build the driver, stop at `READY-TO-LAUNCH`. It does **not** launch the night.
- **The night (detached driver, Arnav launches it by hand, OpenCode closed):** scoring, then analysis, then multidms.
- **Session 3b (OpenCode, next morning):** verify, re-run gates, review the staged outputs, correct any prose that contradicts a table, summarize.

**Hard facts about this machine that the design respects:** the disk was at 92% (17 GiB free); swap was pinned near 4 GB when two large
jobs overlapped; the battery died once during a run; a duplicate launch ran for five hours unnoticed. Hence the guards in section 1 and A7.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **Model scoring is allowed only in scripts whose job is scoring, and in gate G-1' (A4d).** Every other script (analysis, M1, audits,
   the driver) must not import torch, esm or thermompnn. Never download model weights; the ESM-2 650M weights come from the local hub cache.
2. **Three pre-registrations are frozen before any data is touched** (A1), by byte-exact extraction with a sha256 gate. Nothing in them may
   change after A1. If a premise in a frozen block proves wrong, log it, stop that module, and propose a new versioned file; never edit.
3. **Every analysis script gets its pre-registration (construction, gates, decision rule) written in its docstring before its first run.**
   Smoke first (small N), then full. Time the full run; do not guess.
4. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold, raise N, or re-run until it passes.
   A script exits with code **3** on a failed gate (the driver never retries code 3).
5. **The bootstrap gate is a reference gate, not an identity gate.** Diagnostics IV found that a position-cluster bootstrap passed
   "every cluster once reproduces the point estimate" while drawing one row per cluster instead of all of them, giving CIs 2.7x too wide.
   Every bootstrap routine used here must (i) pass identity, (ii) agree **draw by draw to 1e-12** with an obvious slow reference
   implementation on identical pre-drawn cluster ids, and (iii) reproduce Phase 1's published MTHFR CI
   **[-0.1173334458953319, -0.0595113844951173]** on the MTHFR anchor rows. Import `pos_cluster_boot_corrected` from
   `scripts/lib/phase2_diag4.py`; do not use script 144's routine.
6. **Resampling units are not interchangeable.** A statistic computed inside one background (a target's rho on a row subset, a
   background's own rho_b CI): resample **position clusters**. A statistic across backgrounds (a covariate's Spearman, a distribution's
   mean): resample **backgrounds** with each rho_b held fixed. State the unit in every docstring.
7. **Prose must match the table above it.** Before finalizing each log entry, re-read every comparative sentence (more/less, higher/lower,
   inside/outside, "per position", "largest") against the printed numbers immediately above it. Four earlier logs drifted from their own
   tables; the table governs.
8. **Protected, never edited:** `RESULTS.md`, `docs/tasks/results-log/MTHFR_RESULTS_LOG.md`, `docs/writeups/PROJECT_SUMMARY_FINAL.md`,
   `AGENTS.md`, `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`, `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` (v1; v2 is a
   new file), **every earlier log** (all of `PHASE1*`, `PHASE2*`, `PHASE3A_LOG.md`, `INTERFACE_LOG.md`, the Diagnostics I-IV logs and corrections
   files), every earlier script (numbered 152 or lower), `scripts/lib/phase2_diag*.py`, and **this planning doc**. If this doc is wrong, say so in
   the log; do not edit it. If an instruction conflicts with a protected-path rule, log `BLOCKED` and stop that item; do not proceed and flag it afterwards.
9. **Do not commit, stage, or push.** Arnav commits.
10. `venv/bin/python3` always for the main environment. A small missing package: `venv/bin/python3 -m pip install <pkg> --break-system-packages`,
    log it. **jax / multidms go in a separate environment** (A6) and never into `venv/`.
11. **Wording.** The frozen MTHFR outcome words (GENERIC / BEATS / INDETERMINATE) are never used for any result here. Each module has its own
    pre-registered outcome words (listed in its frozen block); use exactly those and nothing stronger. **No result from one system may be
    described as confirming or undermining a result from another.** Cross-system statements need their own pre-registration.
    Compare any `p_spec` only to its stated numeric thresholds and say "at or below" or "above".
12. **Matched controls and flags** (where a statistic is compared with a random-deletion range): print the value, the range, both one-sided
    fractions, and the distance to the nearest bound; flag INSIDE, OUTSIDE, or MARGINAL (outside but within 0.002 of a bound, or a one-sided
    fraction in [0.01, 0.05]). Never build a conclusion on a MARGINAL flag.
13. **One heavy process at a time.** Never run two scoring jobs, or a scoring job and a fit, concurrently. Never run anything else heavy while the
    detached driver is alive. Every long job is resumable (per-background atomic write, skip completed) and runs under a lock.
14. **Expected values in this doc are Claude's recomputations or planning figures, not facts.** Recompute each independently and print it next to the
    target. A mismatch means the doc is wrong: STOP that item, report both numbers, do not force agreement.
15. Verbatim output in every entry; full output to `docs/tasks/phase3-overnight/PHASE3_<TASK>_FULL_OUTPUT.txt`.
16. **Context budget.** Session 3a is long. After each module (M1, G, R, M2, driver) append its log entry immediately. If context runs low, finish the
    current entry, write `docs/tasks/phase3-overnight/STATE.md` (done / in progress / next, with the last script number used), and stop. Arnav will paste a
    continuation prompt. Re-read your own log before continuing; do not trust memory.

## S1. Logging instructions

Create `PHASE3A_BUILD_LOG.md` first with this template; append one entry per task **immediately** after it finishes:

```
## [TASK ID] - [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

---

# PART A - SESSION 3a: build, validate, stage (supervised; ends at READY-TO-LAUNCH)

## Task A0 - Preflight (HARD stops: if any fails, STOP and tell Arnav what to fix)

Run and log verbatim:

- `date`; `pmset -g batt` (**must show AC Power and charge >= 50%**); `pmset -g therm`; `sysctl vm.swapusage`
  (**used < 2.0 GB**); `memory_pressure | head -20` (system-wide free memory **>= 35%**); `df -h .` (**free >= 8 GiB**; the disk was at 92% earlier;
  if lower, STOP and list what could be cleared, delete nothing); `ps aux | grep -E "124_phase2|launch_phase|phase3_driver|opencode" | grep -v grep`
  (report everything; **no scorer, launcher or driver may be alive**; the interactive OpenCode window and its `opencode serve --service` daemon are
  expected in this session, but report their RSS).
- `venv/bin/python3 --version`; whether `torch` imports with MPS available (this session only, for A4d / smokes); presence of the local ESM-2 650M cache
  (do not load it here). **Note the Python version.** It has been 3.14; jax and multidms may not support it, which matters for A6.
- `git log -1 --format='%H %cI' -- docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md` must print a hash (**gate A0-G1: this doc is committed**; the commit is the
  pre-registrations' timestamp) and `git status --short -- docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md` must be empty. If not, STOP: "commit the doc first."

## Task A1 - Freeze the three pre-registrations (BEFORE any data is read or downloaded)

Extract each block with **exactly** these line-anchored commands (a looser pattern would match the instructions and leak text). Then `wc -l`, confirm the
output contains no `FROZEN` string, and verify the sha256 against the value in the table. **Gate A1-G1 (HARD, per block):** hash must match. If it does not,
STOP that block, report both hashes, do not re-extract until it matches, and do not edit anything to force it.

```
mkdir -p docs/tasks/phase3-overnight/prereg
awk '/^<<<GB1V2_FROZEN_BEGIN>>>$/{f=1;next} /^<<<GB1V2_FROZEN_END>>>$/{f=0} f' docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md > docs/tasks/phase3-overnight/prereg/GB1_REGIME_PREREG_v2.md
awk '/^<<<RBD_FROZEN_BEGIN>>>$/{f=1;next} /^<<<RBD_FROZEN_END>>>$/{f=0} f' docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md > docs/tasks/phase3-overnight/prereg/RBD_REPLICATION_PREREG_v1.md
awk '/^<<<GE_FROZEN_BEGIN>>>$/{f=1;next} /^<<<GE_FROZEN_END>>>$/{f=0} f' docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md > docs/tasks/phase3-overnight/prereg/MTHFR_GE_TARGET_PREREG_v1.md
```

| file | lines | sha256 |
|---|---|---|
| `GB1_REGIME_PREREG_v2.md` | 76 | `b3c82d589afc2889f60ad8626dcb24d0496f77303d0696b52db700129fd1357e` |
| `RBD_REPLICATION_PREREG_v1.md` | 56 | `8965450a524e883b02ef2c970178cd242709bed1c55bd5e6ed573c1e2c2671a7` |
| `MTHFR_GE_TARGET_PREREG_v1.md` | 47 | `73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c` |

Also verify the v1 GB1 file is untouched: the frozen v1 block (73 lines) has sha256 `b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613`; check
`docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` against it. Record `git log -1` for the doc as the freeze timestamp.

## Task A2 - Shared library, regression gate, and the bootstrap reference gate (no model)

Write `scripts/lib/phase3_common.py` (generic, dataset-agnostic: arrays in, numbers out) containing: Spearman with average ranks; the **corrected position-cluster
bootstrap** (import `pos_cluster_boot_corrected` from `scripts/lib/phase2_diag4.py` if importable without torch; otherwise transcribe verbatim under a `QUOTED SOURCE`
comment with file and line numbers and gate it); the slow reference implementation (concatenate each sampled cluster's row indices; `scipy.stats.spearmanr`); a
background-level bootstrap; a label-permutation p; `p_spec(rho_target, rho_nulls, mode)` with `mode` in {`neg`, `pos`, `abs`} (`neg`: `(1 + #{rho_b <= rho_T})/(1 + n)`;
`abs`: `(1 + #{|rho_b| >= |rho_T|})/(1 + n)`); a leave-one-out OLS residual (as Diagnostics II D9); a Spearman gradient against a distance covariate.
Pre-register the docstring first.

**Gate A2-G1 (HARD) - regression on MTHFR through the generic API.** Applied to the MTHFR cached inputs (`data/processed/phase2_diagnostics/background_rho_table.csv`,
sha256 `e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796`; `data/processed/task32_analysis_table.csv`; the 96 `bg_*.csv`), the generic functions must reproduce, to
1e-9 on 9-dp values and 2e-6 on 6-dp values: A222V rho -0.088118064 (full) / -0.090021683 (H); `p_spec` (`neg`) 2/79 with beaters `{G_P254F}` (full) and 4/79 with
`{AV_195, AV_220, G_P254F}` (H); the D9 primary shift-adjusted residual `r_A` -0.066425 (full) / -0.068692 (H) with k = 2; Spearman(rho_b, mean|delta|) over the 96 backgrounds
-0.614188823 (full) / -0.612696690 (H); and the corrected CI for the unrestricted anchor **[-0.1173334458953319, -0.0595113844951173]**. If the generic library cannot
reproduce these, it is not trusted for GB1 or RBD: STOP A4-A5.

**Gate A2-G2 (HARD) - reference bootstrap:** draw-by-draw agreement to 1e-12 between the corrected routine and the slow reference on (i) the MTHFR anchor rows and (ii) a restricted
row set (positions removed), using identical pre-drawn cluster ids.

## Task A3 - Module M1: MTHFR monotone global-epistasis target (cached data; runs fully in this session)

Implement `MTHFR_GE_TARGET_PREREG_v1.md` exactly (script 153 or next free). Read `rebuild_interaction_fit` and the weighted aggregation of per-condition residuals, **quote
them verbatim** with file and line numbers, and make the per-condition expectation the only pluggable component. Gates G-M1 to G-M5 of the frozen block, all hard.
Smoke at `N_BOOT=300`, then full at `N_BOOT=10000`, `SEED=0`; time the full run. Report every quantity (a)-(f) of the frozen block for GE-ISO (primary), GE-SIG and GE-LIN-CF, side by side,
with the frozen outcome word for each and an explicit sentence when the three disagree. Print the fitted monotone functions (breakpoints / parameters) so the reader can see the shape.
**Do not interpret beyond the pre-registered words.** This is a result in its own right; it does not wait for the night.

## Task A4 - Module G: GB1 regime map (build, gate, time; no overnight scoring here)

Implement `GB1_REGIME_PREREG_v2.md` exactly.

- **A4a Inputs.** Verify sha256 of `data/external/gb1_olson2014/gb1_olson2014_doubles.csv` (`89f8e394125d743b5db4bc455a64c59dc6d85f3f1d994f6de51af90f47cc4769`, 535,917 rows),
  `gb1_olson2014_singles.csv` (`0b2e865e007d606d885d1e8df9f4548a85e4ceeedbff8ab860db7469d65dbfc3`, 1,045 rows), `data/external/GB1_fitness_landscape.txt`
  (`7c9aedcf44416ba8c3a442f041d0b53f8981f8a0bcaaf86afd8ebb8088ec0ad2`) and `data/processed/gb1_background_roster.csv`. Build the **assayed sequence** (the project's 2GB1 constant with position 2 = Q)
  and the **project sequence** (T at position 2) and confirm they differ at exactly position 2 and that every single-mutant WT residue in the data matches the assayed sequence at its position (gate **G-5**).
- **A4b Roster.** Draw the 400 per frozen block A4 (`default_rng(0).choice`), write `data/processed/phase3/gb1/roster_v2.csv` and its sha256 **before any scoring**; record the first 20 of the draw order as the
  two-sequence subset. Report n_partners per background at thresholds 23, 25 (primary), 28 and unfiltered, and confirm all 400 clear the 100-partner floor.
- **A4c Scoring script** (`scripts/154_...`), modeled on `scripts/124_phase2_score_backgrounds.py` (read it; reuse its atomic-write and skip logic): `scripts/lib/esm_scoring.py::get_position_logprobs` and
  `get_device()`, ESM-2 650M, **one unbatched forward pass per (background, position)**, masked-marginal, all 19 substitutions from the pass; per-background file `data/processed/phase3/gb1/bg_<id>.csv`
  written atomically (`.tmp` then rename) only when all 54 positions are done; manifest append; skip completed files; flags `--only`, `--limit-positions`, `--out-dir`, `--sequence {assayed,project}`; the WT arm
  (55 passes per sequence) computed once into its own file. Exit 3 on any failed gate.
- **A4d Gate G-1' (HARD, uses the model, scratch directory only).** Rescore the V54A background and the WT arm at positions 39, 40, 41 on the **project** sequence; all 57 variants' delta must reproduce script 73's cached
  `delta_esm` to 1e-6 and the control rho must re-derive as **+0.12218045112781956** (to 1e-9). Then score V54A on the assayed sequence and report that rho and the difference (not a gate).
- **A4e Timing smoke.** Fully score 3 roster backgrounds plus the assayed WT arm; report median seconds per pass and project the full stage: `(400 x 54 + 55) passes x s/pass x 1.25`. Compare with the **100-minute stage budget**.
  If the projection exceeds the budget, **do not shrink the roster**; record it. The stage will run to its budget in roster order and the analysis rule A8 of the frozen block applies.
- **A4f Analysis script** (`scripts/155_...`, no torch): per-background partner sets (primary t = 25, plus sensitivities), `e_b` by the project's GB1 construction (quote script 73 / the Phase 3a T3 code), rho_b with corrected position-cluster CI
  (`N_BOOT = 2000`), the distribution summary with background-level bootstrap CI, the four pre-registered covariate tests with background-level bootstrap CI and 10,000-shuffle permutation p, the sensitivities and the two-sequence comparison,
  the frozen outcome words only. Modes `--mode smoke` and `--mode full`.
- **A4g Planted-signal test (HARD gate G-SYN).** Run the whole analysis pipeline on a **synthetic** score set built from the real partner sets and `e_b`: (i) `delta_b = e_b + noise` (known positive signal) must give a distribution flagged OFF-CENTER with a positive mean and
  every covariate test computed; (ii) `delta_b` = a fixed random permutation of values must give CENTERED. If either fails, the analysis cannot be trusted: STOP and fix before the night.

## Task A5 - Module R: Starr et al. 2022 RBD replication (acquire, verify, build, gate, time)

Implement `RBD_REPLICATION_PREREG_v1.md` exactly. This module depends on the network; if acquisition fails, log `BLOCKED` with the verbatim error and **skip R and the RBD part of M2**, never substitute another dataset or a mirror without logging it.

- **A5a Acquisition.** The source is the authors' public repository `jbloomlab/SARS-CoV-2-RBD_DMS_variants` (Starr et al., *Science* 377:420-424, doi:10.1126/science.abo7896). List the repository tree through the GitHub contents API,
  identify the **single-mutation effects table** and the **per-variant (barcode-level) tables** and any per-library columns, and download **only the files needed**, recording URL, HTTP status, bytes and sha256 for each.
  **Abort the download and log `BLOCKED` if the needed files exceed 1.5 GB total** (the disk is tight). Record the repository commit hash. Files go to `data/external/rbd_starr2022/` (gitignored).
- **A5b Data dictionary.** Quote the table headers verbatim; list the backgrounds present; confirm Wuhan-Hu-1, Alpha and Eta are present; report per-background mutation counts and the barcode-count columns' distributions. Determine from the repository's own reference sequences
  that Alpha differs from Wuhan-Hu-1 in the RBD by exactly N501Y and Eta by exactly E484K (**gate G-R1**). Extract the Wuhan-Hu-1 RBD sequence and site numbering used by the data (**gate G-R2**: every row's WT residue equals the sequence residue at its site).
- **A5c Targets.** Build `e_T^bind` and `e_T^expr` for T in {N501Y, E484K} per the frozen block (barcode-count filter `n_bc >= 3` in both backgrounds; sensitivities `>= 1` and `>= 5`); report retained variant counts; per-library reliability of `e_T` if per-library columns exist.
- **A5d Roster.** Draw the arms per the frozen block with `default_rng(0)`, write `data/processed/phase3/rbd/roster_v1.csv` and its sha256 before any scoring, in the **interleaved order** the block specifies. Report counts per arm and the expected number of passes.
- **A5e Scoring script** (`scripts/156_...`): same design as A4c on the RBD sequence; WT arm over all construct sites; per-background atomic files `data/processed/phase3/rbd/bg_<id>.csv`.
  **Gate G-R5 (HARD, model):** scoring the same background twice gives identical values (1e-6), and the masked-marginal log-odds of the WT residue is 0 at every scored position.
- **A5f Timing smoke.** Fully score the two targets and one arm-S background; report s/pass and project the stage against the **150-minute budget**.
- **A5g Analysis script** (`scripts/157_...`, no torch) and **planted-signal test G-SYN** exactly as A4f/A4g, using the real `e_T`.

## Task A6 - Module M2: multidms (feasibility audit, isolated environment, smoke fit; best-effort, time-boxed to 75 minutes)

multidms (Haddox, Galloway, Dadonaite, Bloom, Matsen, DeWitt; bioRxiv doi:10.1101/2023.07.31.551037) fits a shared global-epistasis nonlinearity across conditions from **multi-mutant** variants. **This module may be `BLOCKED` and that is an acceptable outcome**; the monotone target in M1 already addresses the same question for MTHFR.

- **A6a Audit (no install).** (i) MTHFR atlas variant composition: how many variants carry 1, 2, 3+ amino-acid substitutions in the data the project uses. Claude's expectation, stated so it can fail: the atlas rows are single-substitution allele effects, in which case a global nonlinearity is **not identifiable** from them
  (each variant's two phenotypes can be fit exactly by two free parameters). Apply the frozen rule: multidms is attempted on MTHFR only if >= 5,000 variants carry >= 2 substitutions. (ii) RBD per-variant tables: substitutions per variant and variants per background; the multi-mutant count decides feasibility there.
- **A6b Environment.** Check what Python versions are available (`python3.12`, `python3.13`, `uv`, `brew list`). multidms pins a jax stack that may not support Python 3.14. Build a **separate** environment `venv_multidms` with a supported interpreter and pinned versions (record every version). Never touch `venv/`. If no supported interpreter can be had in the time box, log `BLOCKED`, skip.
- **A6c Smoke fit.** Following the package's own documentation, fit on a ~5% variant subsample for a few iterations; record seconds per iteration and a projected full-fit time against the **120-minute stage budget**; record held-out predictive correlation.
- **A6d Script** (`scripts/158_...`) that fits the Wuhan / Alpha / Eta conditions, writes the shift parameters for N501Y and E484K as `e_T^MD`, a convergence report and held-out correlations, under a hard internal wall-clock cap. Used only as a **secondary** target in the RBD analysis, only if the held-out correlation criterion in the RBD frozen block is met.

## Task A7 - Orchestration: driver, launcher, guards, dry-run (end at READY-TO-LAUNCH)

Build and **test** (isolated temp directory with stub stages; never touch real outputs):

- `scripts/lib/phase3_guards.py` and `scripts/phase3_driver.py` (Python: it needs real timeouts, signal handling and per-stage retry), `scripts/launch_phase3_overnight.sh` (bash: lock, guards, `nohup`, `caffeinate`).
- **Lock.** `mkdir data/processed/phase3/.driver.lock` (atomic) plus `driver.pid`. The launcher **refuses to start** if the lock exists and its PID is alive, and clears a stale lock with a message. It also refuses if any process matching `phase3_driver|124_phase2` is alive. (Six overlapping launches happened once; this is the fix.)
- **Guards before every stage** (override only with `--force`, logged): AC power and charge >= 30% (wait up to 10 minutes, then skip the stage and log), swap used < 3.0 GB and free memory >= 25% (wait up to 30 minutes in 5-minute steps, then skip the stage and log), disk free >= 5 GiB. If `pmset`, `memory_pressure` or `sysctl` is missing, log and continue unguarded.
  The launcher additionally refuses to launch below 35% free memory and prints what to quit (the OpenCode window, browsers, Spotify, Claude, ChatGPT).
- **Stages, in order, each with a wall-clock budget, a retry rule (up to 2 retries on a non-gate crash after 30 s; never on exit code 3), and an independent failure policy:**

  | stage | what | budget | depends on |
  |---|---|---|---|
  | S1 | GB1 scoring (`154`), then the two-sequence subset | 100 min | A4 gates |
  | S2 | RBD scoring (`156`) | 150 min | A5 gates |
  | S3 | analyses: GB1 (`155 --mode full`), RBD (`157 --mode full`) | 75 min | S1 / S2 outputs (each runs only if its scoring reached the coverage rule; otherwise logged and skipped) |
  | S4 | multidms on RBD (`158`), in `venv_multidms` | 120 min | A6 gates |
  | S5 | integrity pass: file counts, manifests, sha256 of every staged script vs `STATE_FOR_LAUNCH.md`, final `driver_state.json` | 5 min | none |

  A stage that times out, is skipped, or hits a gate failure is logged and the driver **continues to the next stage**. Total cap about 7.5 hours.
- **State and heartbeat.** `data/processed/phase3/driver_state.json` (stage, start, last update, status per stage) and `driver.log`, both updated at every transition and every 60 seconds during a stage.
- **Tests (all hard):** start twice (second refuses); stale lock; `kill $(cat driver.pid)` forwards TERM to the child and removes the lock; stage timeout kills the child; retry on a crash, no retry on exit 3; each guard with simulated bad readings (use environment-variable overrides such as `PHASE3_FAKE_BATT`, `PHASE3_FAKE_SWAP`, `PHASE3_FAKE_MEM`); `--dry-run` prints the full plan and runs nothing.
  Disclose every deviation from this section.
- **Write `docs/tasks/phase3-overnight/STATE_FOR_LAUNCH.md`:** every staged script with sha256, the expected duration per stage from the timing smokes, the exact launch / monitor / stop / resume commands, and anything Arnav must know. **Do not launch the real run.**
- **S-A SUMMARY.** Status `READY-TO-LAUNCH` or `BLOCKED` per module and why; M1's result (it is complete); every gate with value; the projected night; the single entry to read first with its line number. Then **STOP**. Do not poll, sleep-wait, or start scoring.

---

# PART B - THE NIGHT (Arnav launches by hand; OpenCode closed)

Before launching: plugged in and **charging**, lid open (or the machine set not to sleep on power), Low Power Mode off, everything heavy quit (OpenCode window, browsers, Spotify, Claude, ChatGPT). The launcher enforces the memory floor. Launch once with
`bash scripts/launch_phase3_overnight.sh`. It prints the PID, the monitor command (`tail -n 5 data/processed/phase3/driver.log`) and the stop command. Do not `tail -f`. Do not open OpenCode. Do not run anything else heavy. If it is interrupted, `bash scripts/launch_phase3_overnight.sh` resumes (completed
backgrounds are skipped).

---

# PART C - SESSION 3b (next morning; OpenCode; verification and analysis review)

Use `PHASE3B_MORNING_LOG.md`, same template. Tasks in order:

- **C0 State and integrity.** Read `driver_state.json` and `driver.log`; confirm no driver or scorer is still alive; count `bg_*.csv` per module against the rosters; dedupe any manifest (keep the row nearest the file's mtime; do not overwrite the original); verify every staged script's sha256 against `STATE_FOR_LAUNCH.md` (**flag any change prominently**); verify the three prereg hashes. Record any stage that timed out, was skipped, or failed.
- **C1 Re-gate.** Re-run, on the real outputs, the cheap gates: coverage (each background >= 95% of its eligible positions), the G-B-style reproduction of three completed backgrounds per module against a fresh rescoring **only if** the machine is idle and the memory floor holds, the bootstrap reference gate, G-2 (no own-position rows), G-5. A failed gate means that module's results are reported as failed, not interpreted.
- **C2 Verify the staged analyses.** Independently recompute a sample of headline numbers from the raw per-background files (not by calling the staged script): at least 10 per-background rho_b per module, each covariate Spearman, `p_spec_abs` for both RBD targets. Any disagreement stops that module.
- **C3 Interpret within the frozen words.** Per module, in order of the frozen blocks' own definitions. Where two sensitivities disagree, say so plainly.
- **C4 Corrections.** Append-only, in this log, for any staged-output sentence that contradicts its table.
- **S-B SUMMARY**, in the order of section S2 below.

## S2. Mandated SUMMARY (session 3b)

1. **READ THIS FIRST:** which stages completed, timed out, were skipped, or failed, and the evidence.
2. **M1** (from session 3a, re-verified): GE-ISO / GE-SIG / GE-LIN-CF outcome words, rho^GE with CI, the shrinkage, `p_spec^GE` full and H, the gradient, in one table.
3. **G:** the rho_b distribution and its CENTERED / OFF-CENTER word; each of the four covariates with its word, CI and permutation p; the three threshold sensitivities; the two-sequence comparison; backgrounds completed.
4. **R:** per target (N501Y, E484K): rho_T with corrected CI, `p_spec_abs`, `p_spec_neg`, `p_spec_pos`, the outcome word; the shift-adjusted and locality results; Arm S rank fraction; split-half stability; the expression-phenotype sensitivity; the multidms target if available.
5. **M2:** audit result, environment, convergence, held-out correlations, and whether the multidms target was used.
6. Every gate, PASS/FAIL, value.
7. A plain two-sided statement **per module** (no cross-module claim).
8. Confirmation that no protected file, earlier log, earlier script or library was edited; nothing was committed; torch/esm were imported only where rule 1 allows.
9. The single most important entry to read first, with its line number.

---

## What this is NOT

- Not a change to any frozen Phase 2 result, and not a revision of `PHASE2_PREREG.md` or of GB1 v1 (v2 is a new file).
- Not the ESM-2 size ladder.
- Not a statement about MTHFR from GB1 or RBD results, in either direction.
- Not permission to touch `RESULTS.md`; the alpha discrepancy still needs Arnav's explicit sign-off.

---

## Appendix A - FROZEN: GB1 regime map, pre-registration v2

<<<GB1V2_FROZEN_BEGIN>>>
# GB1 regime map - pre-registration v2

Frozen 2026-10-01, before any GB1 scoring. Supersedes v1 (frozen block sha256 b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613).
Authors: Arnav (PI), Claude (planning). This file is self-contained. It carries v1's question, statistic, decision rules and disclosure forward
and amends v1's roster, resampling units, gates and execution, and fixes the three items v1 left open (read-depth qualification, the scored
sequence, passes per background). The amendments were fixed after Phase 3a (acquisition) and before any GB1 delta value existed.

## 1. Question

Across many fixed single-mutant backgrounds in one protein with a complete double-mutant matrix, how does the ESM-2 background-shift statistic behave
as a function of regime? This is a characterisation of the statistic, not a test of any MTHFR result, and its interpretation does not depend on any MTHFR outcome.

## 2. Statistic

For each background b (a GB1 single mutant) and each qualifying partner variant v measured in combination with b:
delta_b(v) = S(v | b) - S(v | WT), S = ESM-2 650M masked-marginal log-odds against the wild-type residue, one unbatched forward pass per (background, position).
e_b(v) = the measured genetic-interaction term for the pair (b, v), by the same construction the project's existing GB1 transplant code uses (script 73, as reproduced
in Phase 3a T3). rho_b = Spearman(delta_b, e_b) over b's qualifying partners, excluding any partner at b's own position.

## 3. Amendments and resolved items

A1 Partner qualification ("high-confidence"). The publisher's file has no confidence column; the only confidence signal is the read depth `Input Count`. A double mutant
qualifies iff Input Count >= 25 (PRIMARY). Sensitivities, all reported, none selected: >= 23, >= 28, and unfiltered. Rationale: the integer thresholds 23 through 28 are exactly
those whose retained double-mutant count lies inside the paper's stated 509,693-517,278 range (Phase 3a T2-G1); 25 is the midpoint, fixed without reference to any score.
v1's floor of 100 qualifying partners is retained but is inert (every one of the 1,045 singles clears it under every threshold).

A2 Scored sequence. The sequence actually assayed: the project's 2GB1 constant with position 2 = Q (the documented template change T228Q). The wild-type arm is one masked-marginal pass at each of
the 55 assayed positions 2..56 under this sequence, computed once. Each background receives 54 passes (the 55 positions minus its own). No pass at position 1, which is never a target.

A3 Gate G-1 replaced. v1's G-1 (reproduce the recorded V54A control rho = +0.122 from the whole-domain matrix) cannot be met: that control came from the four-site library. G-1' (hard): rescoring the V54A
background and the wild-type arm at positions 39, 40, 41 on the PROJECT sequence (T at position 2) reproduces script 73's cached delta_esm for all 57 variants to 1e-6, and the control rho
re-derives as +0.12218045112781956 (to 1e-9). This proves the machinery independent of the sequence choice. V54A on the assayed sequence is reported, not gated.

A4 Roster. All 1,045 single mutants qualify under every threshold. 400 are drawn with numpy.random.default_rng(0).choice(sorted_ids, 400, replace=False), sorted_ids = the single-mutant ids sorted
lexicographically by (position, mutant). Scoring order is the draw order, so any completed prefix is a random subsample. The roster is written to disk and hashed before scoring. No fitness-based or
severity-based selection at any point.

A5 Resampling units (corrects v1 section 4, which conflated them). rho_b's own 95% CI: position-cluster bootstrap (clusters = partner positions; every variant at a drawn position comes with it,
with multiplicity), N_BOOT = 2000, SEED = 0, a descriptive interval. Every statistic ACROSS backgrounds (the distribution's mean; each covariate's Spearman): background-level bootstrap (backgrounds
resampled with replacement, each rho_b held fixed), N_BOOT = 10000, SEED = 0; permutation p from 10,000 shuffles of the covariate across backgrounds.

A6 Gate G-3 strengthened. The bootstrap routine must (i) reproduce its point estimate with every cluster once, AND (ii) agree draw by draw to 1e-12 with an obvious slow reference implementation on
three real backgrounds using identical pre-drawn cluster ids, AND (iii) reproduce Phase 1's published MTHFR CI [-0.1173334458953319, -0.0595113844951173] on the MTHFR anchor rows. The identity gate
alone cannot detect a cluster-to-row mapping error.

A7 Sensitivities (reported, none selected): partner thresholds 23 and 28 and unfiltered (recompute every rho_b and the four covariate tests); and the first 20 backgrounds in roster order scored on BOTH
sequences (assayed and project), reporting the Spearman between the two rho_b vectors and max |delta rho_b|.

A8 Coverage and partial completion. G-4 retained: each background scores at least 95% of its eligible positions. The analysis requires at least 200 completed backgrounds in roster order; with fewer, the
distribution is reported but the covariate tests are labelled UNDERPOWERED and not interpreted.

## 4. Primary analysis

The distribution of rho_b across the completed roster: n, mean, median, SD, range, and the fraction with rho_b < 0. Pre-registered regime covariates, each tested against rho_b by Spearman:
(a) mean sequence separation |pos(b) - pos(v)| over b's qualifying partners; (b) the background's own measured single-mutant fitness; (c) n_partners; (d) the SD of e_b over b's partners.

## 5. Decision rules (constants fixed now)

- Per covariate: ASSOCIATED iff the background-level bootstrap CI of its Spearman excludes 0; NOT RESOLVED otherwise. NOT RESOLVED is reported as "n cannot resolve this", never as "no relationship".
- Distribution centering: CENTERED iff the background-level bootstrap CI of the mean rho_b includes 0; OFF-CENTER otherwise. If OFF-CENTER, that is a property of the statistic in this system and is
  reported with equal prominence either way.
- Wording rule: no result from this map may be described as confirming, supporting or undermining any MTHFR result. The systems, backgrounds and measurement platforms differ.

## 6. Gates (a failed gate stops the run; thresholds are never loosened)

G-1' (A3); G-2 no partner at a background's own position enters any rho_b; G-3 (A6); G-4 and A8; G-5 the sequence used for scoring (assayed) matches the sequence the fitness data implies at every
position 2..56; G-SYN the analysis pipeline recovers a planted signal and a planted null on synthetic scores built from the real partner sets and e_b.

## 7. Execution

Detached, resumable, one output file per background, in roster order, under a lock, only after Phase 2's scoring has completed (done). Timing measured in a smoke run, not assumed.

## 8. Disclosure

The MTHFR anchor motivated building this map, but the map's rules and covariates were fixed before any GB1 score existed and do not reference any MTHFR value (the only MTHFR numbers cited are the
bootstrap-gate reproduction targets in A6). Any deviation must be disclosed in the log and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v2.
<<<GB1V2_FROZEN_END>>>

---

## Appendix B - FROZEN: Starr et al. 2022 RBD replication, pre-registration v1

<<<RBD_FROZEN_BEGIN>>>
# RBD replication of the background-shift design - pre-registration v1

Frozen 2026-10-01, before any RBD data is downloaded or scored. Authors: Arnav (PI), Claude (planning).

## 1. Question

In MTHFR, the ESM-2 background-shift statistic for the single-substitution background A222V correlated with A222V's measured epistatic shift, and that correlation was more extreme than for arbitrary
placebo backgrounds. Does the same design, applied to the two genuine single-substitution backgrounds in the Starr et al. 2022 SARS-CoV-2 RBD deep mutational scans (Alpha = N501Y, Eta = E484K, each against Wuhan-Hu-1),
produce a target correlation that is extreme relative to placebo backgrounds? This replicates the DESIGN, not any MTHFR number, and makes no claim about MTHFR.

## 2. Data

Starr et al., Science 377:420-424 (doi:10.1126/science.abo7896); the authors' public repository jbloomlab/SARS-CoV-2-RBD_DMS_variants. File and column names are recorded in the implementation log, not guessed here.
Phenotype PRIMARY: ACE2 binding (the per-mutation effect on log10 KD as the authors define it). SECONDARY: expression. A mutation is usable for a target T only if it is measured in both T and Wuhan-Hu-1 with barcode
count n_bc >= 3 in each (sensitivities n_bc >= 1 and >= 5, reported, none selected). Target site excluded from the variant set for everyone.

## 3. Quantities

e_T(v) = x_T(v) - x_Wuhan(v) for T in {N501Y, E484K}, over single substitutions v at sites other than T's site.
delta_b(v) = S(v | b) - S(v | Wuhan-Hu-1 RBD), S = ESM-2 650M masked-marginal log-odds against the wild-type residue, one unbatched forward pass per (background, site), over the RBD construct's sites.
rho_b^T = Spearman(delta_b, e_T) over variants v at sites other than b's own site and T's site.

## 4. Backgrounds (fixed before scoring, fitness-blind)

For each target T: Arm S_T = the 18 other substitutions at T's site (not the wild type, not T's own substitution). Arm V_T = T's substitution type (N to Y for N501Y; E to K for E484K) at every other site of the
construct with the same wild-type residue; if more than 60, a seed-0 sample of 40. Arm G (shared by both targets) = 40 backgrounds, each a single substitution at a distinct site, drawn with
numpy.random.default_rng(0), site uniform among the construct's sites excluding 484 and 501, mutant uniform among the 19 non-wild-type residues. The null set for T is N_T = V_T u G; the OTHER target's background is excluded from N_T.
The two target backgrounds are scored. The roster is written and hashed before scoring, and ordered by interleaving the arms round-robin so that any completed prefix is balanced.

## 5. Primary test and outcome words (numeric, fixed now)

p_abs(T) = (1 + #{b in N_T : |rho_b^T| >= |rho_T^T|}) / (1 + |N_T|). Direction is not assumed (the MTHFR sign is not carried over). Also reported: p_neg (rho_b <= rho_T) and p_pos (rho_b >= rho_T).
RBD-REPRODUCES for T iff p_abs(T) <= 0.05. RBD-DOES-NOT-REPRODUCE iff p_abs(T) > 0.10. RBD-INCONCLUSIVE otherwise. Two targets are two looks; both are reported with no multiplicity adjustment and that is stated.

## 6. Secondary analyses (descriptive; none changes the outcome words)

(a) rho_T^T with a corrected position-cluster bootstrap CI (clusters = sites; 10,000 draws; seed 0). (b) The shift-magnitude confound: Spearman(rho_b, mean|delta_b|) across all backgrounds (background-level bootstrap) and a leave-one-out
OLS shift-adjusted p_spec_adj. (c) Locality: Spearman(rho_b, |site_b - site_T|) across N_T u S_T, and the same with 3D distance if a structure of the RBD is obtainable (PDB 6M0J, RBD chain) with numbering verified against the sequence; otherwise sequence distance only.
(d) T's rank within S_T u {T} (a rank fraction, not a test). (e) Split-half stability: sites split in two halves by seed 0; p_abs recomputed on each half. (f) Measurement reliability of e_T: correlation between per-library estimates if per-library columns exist.
(g) The expression-phenotype version of every quantity. (h) The multidms target e_T^MD, used only if its held-out predictive Pearson correlation is >= 0.5 for each of the Wuhan, Alpha and Eta conditions (a judgment constant fixed now); reported next to the primary, never replacing it.

## 6b. multidms

multidms (bioRxiv doi:10.1101/2023.07.31.551037) identifies a shared global nonlinearity only from multi-mutant variants. It is fitted on the RBD per-variant data for the Wuhan, Alpha and Eta conditions in a separate environment, under a wall-clock cap. Failure to install, to converge, or to meet
the held-out criterion is an acceptable outcome and is reported as such.

## 7. Gates (a failed gate stops the module; thresholds are never loosened)

G-R1 Alpha differs from Wuhan-Hu-1 in the RBD by exactly N501Y and Eta by exactly E484K in the data's own reference sequences. G-R2 every data row's wild-type residue equals the sequence residue at its site. G-R3 the bootstrap routine passes the identity, draw-by-draw reference
and Phase 1 CI reproduction gates. G-R4 each background scores at least 95% of the construct's eligible sites. G-R5 scoring the same background twice gives identical values (1e-6) and the wild-type residue's log-odds is 0 at every scored site. G-SYN the analysis pipeline recovers a
planted signal and a planted null on synthetic scores built from the real e_T.

## 8. Wording and disclosure

No RBD result may be described as confirming, supporting or undermining any MTHFR or GB1 result; the systems, backgrounds, phenotypes and platforms differ. The design was fixed before any RBD datum was downloaded. Any deviation is disclosed and, if it changes a rule or constant,
requires a new versioned pre-registration, never an edit to v1.
<<<RBD_FROZEN_END>>>

---

## Appendix C - FROZEN: MTHFR global-epistasis-aware target, pre-registration v1

<<<GE_FROZEN_BEGIN>>>
# MTHFR global-epistasis-aware target - pre-registration v1

Frozen 2026-10-01, before the alternative target is computed. Authors: Arnav (PI), Claude (planning).

## 1. Question

The anchor is rho = Spearman(delta_ESM, own_e.b) = -0.088118 over 10,757 variants at 654 positions. own_e.b is the 1/m_se^2-weighted WLS intercept, across conditions c in {12, 25, 100, 200}, of residuals r_c = m_score_c - expected_c from the project's two-pass
interaction fit, where the expectation is a LINEAR function of the WT-background fitness w. If the relation between the two backgrounds' maps is monotone but nonlinear (global epistasis, for example floor and ceiling effects), a linear expectation leaves residuals that depend on a variant's severity and
can be mistaken for background-specific epistasis. This asks whether the anchor and its placebo separation survive when own_e.b is rebuilt against a monotone expectation. It changes no frozen Phase 2 result; it re-targets the anchor.

## 2. Construction

2.1 Reuse the project's own construction (rebuild_interaction_fit and the weighted aggregation of per-condition residuals) unchanged except for one pluggable component, the per-condition expectation E_c(v) as a function of w(v). The code is quoted in the log.
2.2 Identity: with the project's own linear expectation plugged in, the rebuild reproduces the recorded own_e.b for all 10,757 rows to 1e-12.
2.3 PRIMARY (GE-ISO): E_c is the isotonic (non-decreasing) regression of m_score_c on w, weights 1/m_se^2, fitted by 5-fold cross-fitting with folds defined by POSITION (positions permuted with a seed-0 generator, fold = rank mod 5); a variant's expectation comes from the fit that excluded its position.
2.4 SENSITIVITY (GE-SIG): E_c is a four-parameter logistic a + b / (1 + exp(-k (w - m))), weighted least squares, same folds.
2.5 SENSITIVITY (GE-LIN-CF): the project's own linear expectation, cross-fitted with the same folds, so that any change can be attributed to monotonicity and not to cross-fitting.
2.6 r_c^GE = m_score_c - E_c(w); own_e.b^GE = the project's aggregation of r_c^GE across conditions.

## 3. Quantities reported (for GE-ISO, GE-SIG and GE-LIN-CF, side by side)

(a) Spearman(own_e.b^GE, own_e.b) over the 10,757 rows.
(b) rho^GE = Spearman(delta_ESM, own_e.b^GE) with a corrected position-cluster bootstrap CI (clusters = positions; 10,000 draws; seed 0), next to -0.088118, and the shrinkage 1 - rho^GE / rho.
(c) All 96 Phase 2 backgrounds' rho_b^GE (cached delta_b; the same row construction and own-position exclusion as script 125) and the frozen-construction p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / (1 + |N|), N = Arm V u Arm G (78), on the full frame and on the held-out set H (455 positions), with the at-or-below nulls named.
(d) The shift-adjusted p_spec_adj^GE (leave-one-out OLS on mean|delta_b|, as Diagnostics II D9).
(e) A222V's rank within Arm S u {A222V} on rho_b^GE (a rank fraction, n = 19, not a test).
(f) Spearman(rho_b^GE, d3_b) across the 67 resolved nulls with a background-level bootstrap CI, next to +0.7316.

## 4. Outcome words (numeric, fixed now; none is a frozen Phase 2 verdict word)

GE-SURVIVES: the CI of rho^GE (GE-ISO) excludes zero in the negative direction AND p_spec^GE(full) <= 0.05 AND p_spec^GE(H) <= 0.10.
GE-WEAKENS: the CI excludes zero in the negative direction but at least one p_spec^GE condition fails.
GE-DOES-NOT-SURVIVE: the CI includes zero or the sign reverses.
The primary governs; the two sensitivities are reported with the same words, and any disagreement is stated plainly.

## 5. Gates (hard)

G-M1 identity (2.2). G-M2 each fitted monotone expectation is non-decreasing in w on a grid. G-M3 the bootstrap passes the identity, draw-by-draw reference and Phase 1 CI reproduction gates. G-M4 the Phase 2 reproduction rows: A222V rho -0.088118064 (full) / -0.090021683 (H); frozen p_spec 2/79 and 4/79; the rho table sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796.
G-M5 fold integrity: every position in exactly one fold, every variant predicted by a fit that excluded its position.

## 6. multidms on MTHFR

multidms identifies a global nonlinearity only from multi-mutant variants. It is attempted on the MTHFR data only if the audit finds at least 5,000 variants carrying two or more amino-acid substitutions. Otherwise the monotone expectation of section 2 is the global-epistasis-aware refit for MTHFR, and multidms is confined to the RBD data.

## 7. Wording and disclosure

No result here may be described as confirming or undermining a GB1 or RBD result. The construction was fixed before the alternative target was computed. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
<<<GE_FROZEN_END>>>
