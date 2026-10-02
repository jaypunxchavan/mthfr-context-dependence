# PHASE 4 - strengthening: sign, mechanism, utility, locality, neighbour arm, model ladder

**Written:** 2026-10-02 (Claude, planning) | **Executors:** OpenCode (sessions 4a and 4b), a detached driver (the nights)
**Doc lives at:** `docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md`
**Logs:** `docs/tasks/phase4-strengthening/PHASE4A_BUILD_LOG.md` (session 4a), `docs/tasks/phase4-strengthening/PHASE4B_MORNING_LOG.md` (session 4b)
**Frozen pre-registrations (extracted in A1):** `docs/tasks/phase4-strengthening/prereg/`
**Scripts:** next free numbers. Phase 3 used up to 164, so expect **165 and up**. Verify with
`ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` before creating anything. New shared code goes in **new** files
`scripts/lib/phase4_common.py`; do not modify any existing script or library.

---

## 0. What this is, and what "8/10 across the board" means

Two outside reviews and Claude's own re-read of the logs agree on what holds the project at about 6/10: the central question (is A222V's
signal tied to **position 222** or to the **region around it**) was never answered with data built to answer it; the **sign** of the anchor was
never explained; what the correlation **measures** (regression to the mean through the baseline ESM-2 score, measurement noise, between-position
structure) is partly untested; there is no **detection limit** for the pipeline; nothing shows the shift scores are **useful** for anything; and
generality rests on thin evidence. Rigor is already near its ceiling. This phase spends effort where the score is lost.

| Dimension | Now | Modules that move it | What counts toward an 8 |
|---|---|---|---|
| Answers the original question | 5 | **N** (neighbour arm), **M-5** | Each module reports a frozen outcome word (or UNDERPOWERED with the reason); the position-versus-region question has a word from new data |
| Strength of the finding | 4-5 | **M** (mechanism), **N** | We know how much of the anchor is artifact (M-1, M-3) and where it lives (M-5), with a stated detection limit (M-4) and rank stability (M-6) |
| Replication and generality | 4 | **G** (GB1 locality), **L** (model ladder) | The pattern is tested across ESM-2 sizes and in GB1's 400 backgrounds with the same framework |
| Importance and novelty | 5 | **S**, **U** (utility), write-up | A defensible answer to "what does a background shift measure, and does conditioning help?" with an explicit, correct sign statement |
| Rigor and honesty | 9 | all | Keep the standard: frozen blocks, gates, independent recomputation, corrections |
| Reproducibility | 7 | **C5** | An outside person can rebuild every headline number from a fresh clone |

**The honesty clause.** An 8 does not require a positive result. Every module reports its frozen word whichever way it falls, with equal prominence. The
three cached-data modules (M, U, G) use quantities for which related numbers were already seen, so they are **not** out-of-sample; the out-of-sample evidence
in this phase is only the neighbour arm (N) and the model ladder (L). Do not write conclusions in advance; the words decide.

**Why two OpenCode sessions and detached nights.** Same reasons as Phase 3: a long agent session is itself a memory consumer, so scoring runs in a detached
driver under a lock with guards, and a second short session verifies it. The Phase 3 driver ran clean (5 of 5 stages, 22 tests, no retries), and its guards are reused.

**Not in this phase:** ESM-2 3B (does not fit this machine), fine-tuning, new proteins, more placebo backgrounds, the Grantham gradient (n = 18 cannot resolve it), and
the multidms attempt on MTHFR (inapplicable: no multi-mutant rows).

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **Model scoring is allowed only** in the neighbour-arm and ladder scoring scripts, in their gates, and in their timing smokes. Every other script (S, M, U, G, all
   analyses, the driver) must not import torch, esm or thermompnn.
2. **Network use is limited to:** MaveDB and the paper's supplement (U-2); RCSB for GB1 PDB 1PGA (GB1D G-3, optional); and the two ESM-2 checkpoints named in A8 under the
   authorisation there. Nothing else. Record URL, HTTP status, bytes and sha256 for every download. Abort a download that would leave under 5 GiB free.
3. **Five pre-registrations are frozen before any data is touched** (A1) by byte-exact extraction with a sha256 gate. Nothing in them may change after A1. If a premise in a
   frozen block proves wrong, log it, stop that module, and propose a new versioned file; never edit.
4. **Every script's docstring carries its pre-registration (construction, gates, outcome words) before its first run.** Smoke first, then full. Time the full run.
5. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold, raise N, or re-run until it passes. A script exits with code **3** on a failed gate
   (the driver never retries code 3).
6. **The bootstrap gate is a reference gate, not an identity gate** (Diagnostics IV's script 144 defect). Every bootstrap routine must pass identity, agree draw by draw to 1e-12
   with a slow obvious reference on identical pre-drawn cluster ids, and reproduce Phase 1's CI **[-0.1173334458953319, -0.0595113844951173]**. Import
   `pos_cluster_boot_corrected` from `scripts/lib/phase2_diag4.py`; never script 144's routine.
7. **Resampling units are not interchangeable.** Inside one background (an anchor, a component, a partial correlation): resample **position clusters**. Across backgrounds (a
   gradient, a cell mean, a distribution): resample **backgrounds** with each rho_b held fixed. The M-6 bootstrap resamples positions and recomputes the whole placebo test. State the
   unit in every docstring.
8. **Prose must match the table above it.** Before finalizing each entry, re-read every comparative sentence (more/less, higher/lower, inside/outside, "carries", "per position")
   against the printed numbers immediately above it. Five earlier logs drifted from their own tables; the table governs.
9. **The sign sentence is fixed** once the convention note exists (A3): own_e.b is positive when a variant is fitter in the A222V background than expected; delta is positive when ESM-2
   scores a variant as more tolerated with A222V present; a negative rho means the model's shift runs **opposite** to the measured shift. Never write "agrees with", "lines up with" or
   "tracks" for a negative rho.
10. **Protected, never edited:** `RESULTS.md`, `docs/tasks/results-log/MTHFR_RESULTS_LOG.md`, `docs/writeups/PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`,
    `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`, every GB1 / RBD / GE pre-registration under `docs/tasks/phase3*`, **every earlier log and corrections file**
    (`PHASE1*`, `PHASE2*`, `PHASE3*`, `INTERFACE_LOG.md`, Diagnostics I-IV logs, `PHASE3B_MORNING_LOG.md`), every earlier script (numbered 164 or lower), `scripts/lib/phase2_diag*.py`,
    `scripts/lib/phase3_common.py`, `scripts/lib/phase3_guards.py`, `scripts/phase3_driver.py`, and **this planning doc**. If an instruction conflicts with a protected-path rule, log `BLOCKED`
    and stop that item **before** acting; never proceed and flag it afterwards.
11. **Do not commit, stage, or push.** Arnav commits.
12. `venv/bin/python3` always (never `venv_multidms`, which stays untouched). A small missing package: `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it.
13. **Wording.** The frozen MTHFR verdict words (GENERIC / BEATS / INDETERMINATE) and the Phase 3 words are never reused for results here. Each frozen block has its own outcome words; use exactly those and
    nothing stronger. No result from one module may be described as confirming or undermining another module's, or any GB1 / RBD / Phase 3 result. Compare a `p_spec` only to its stated thresholds and
    say "at or below" or "above".
14. **Matched controls and flags:** where a statistic is compared with a random-draw range, print the value, the range, both one-sided fractions and the distance to the nearest bound; flag INSIDE, OUTSIDE or
    MARGINAL (outside but within 0.002 of a bound, or a one-sided fraction in [0.01, 0.05]); never build a conclusion on a MARGINAL flag.
15. **One heavy process at a time.** Never run two scoring jobs, or a scoring job and a long CPU analysis, concurrently. Every long job is resumable (per-background atomic write, skip completed) and runs under a lock.
16. **Expected values in this doc are Claude's recomputations or planning figures, not facts.** Recompute each independently and print it beside the target. A mismatch means the doc is wrong: STOP that item, report
    both numbers, do not force agreement.
17. Verbatim output in every entry; full output to `docs/tasks/phase4-strengthening/PHASE4_<TASK>_FULL_OUTPUT.txt`.
18. **Context budget.** After each module append its log entry immediately. If context runs low, finish the current entry, write `docs/tasks/phase4-strengthening/STATE.md` (done / in progress / next, last script number used)
    and stop; Arnav will paste a continuation prompt. Re-read your own log before continuing.
19. **A read of a CSV written by one script and compared with another must use `float_precision="round_trip"`** (the default pandas parser perturbed values by 1 ULP and moved a Spearman by 8e-06 in Phase 3's recompute).

## S1. Logging instructions

Create `PHASE4A_BUILD_LOG.md` first with this template; append one entry per task **immediately** after it finishes:

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

# PART A - SESSION 4a: build, run the cached modules, stage the nights (supervised; ends at READY-TO-LAUNCH)

## Task A0 - Preflight (HARD stops: if any fails, STOP and tell Arnav what to fix)

Run and log verbatim: `date`; `pmset -g batt` (**AC Power, charge >= 50%**); `sysctl vm.swapusage` (**used < 2.0 GB**; if higher, STOP: "restart the Mac; swap is not released by closing apps"); `memory_pressure | head -20`
(**free >= 35%**); `df -h .` (**free >= 8 GiB**); `ps aux | grep -E "phase3_driver|phase4_driver|124_phase2|launch_phase|opencode" | grep -v grep` (no scorer, launcher or driver alive; report the OpenCode window and
`opencode serve` RSS); `venv/bin/python3 --version`; torch imports with MPS (this session only); the local ESM-2 650M checkpoint is present (do not load it here); `git log -1 --format='%H %cI' -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md`
prints a hash and `git status --short -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md` is empty (**gate A0-G1: this doc is committed; the commit is the pre-registrations' timestamp**).
Also log, without stopping: whether `data/processed/DATA_SHA256_MANIFEST.txt` exists and whether Phase 3's scripts and logs are tracked (`git ls-files scripts/153_m1_ge_target.py scripts/164_rbd_roster.py`).

## Task A1 - Freeze the five pre-registrations (BEFORE any data is read or downloaded)

Extract each block with **exactly** these line-anchored commands (a looser pattern would match the instructions), then `wc -l`, confirm no `FROZEN` string, and verify sha256 against the table.
**Gate A1-G1 (HARD, per block):** the hash must match. If it does not, STOP that block, report both hashes, never re-extract to force a match, never edit anything.

```
mkdir -p docs/tasks/phase4-strengthening/prereg
awk '/^<<<MECH_FROZEN_BEGIN>>>$/{f=1;next} /^<<<MECH_FROZEN_END>>>$/{f=0} f' docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md > docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md
awk '/^<<<UTIL_FROZEN_BEGIN>>>$/{f=1;next} /^<<<UTIL_FROZEN_END>>>$/{f=0} f' docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md > docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md
awk '/^<<<GB1D_FROZEN_BEGIN>>>$/{f=1;next} /^<<<GB1D_FROZEN_END>>>$/{f=0} f' docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md > docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md
awk '/^<<<NEIGH_FROZEN_BEGIN>>>$/{f=1;next} /^<<<NEIGH_FROZEN_END>>>$/{f=0} f' docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md > docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md
awk '/^<<<LADDER_FROZEN_BEGIN>>>$/{f=1;next} /^<<<LADDER_FROZEN_END>>>$/{f=0} f' docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md > docs/tasks/phase4-strengthening/prereg/MODEL_LADDER_PREREG_v1.md
```

| file | lines | sha256 |
|---|---|---|
| `MECH_ANCHOR_PREREG_v1.md` | 56 | `8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b` |
| `UTILITY_PREREG_v1.md` | 32 | `744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531` |
| `GB1_LOCALITY_PREREG_v1.md` | 26 | `10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8` |
| `NEIGHBOUR_ARM_PREREG_v1.md` | 42 | `167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e` |
| `MODEL_LADDER_PREREG_v1.md` | 26 | `eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3` |

Also verify the Phase 3 frozen files are untouched: `docs/tasks/phase3-overnight/prereg/GB1_REGIME_PREREG_v2.md` b3c82d589afc2889f60ad8626dcb24d0496f77303d0696b52db700129fd1357e,
`RBD_REPLICATION_PREREG_v1.md` 8965450a524e883b02ef2c970178cd242709bed1c55bd5e6ed573c1e2c2671a7, `MTHFR_GE_TARGET_PREREG_v1.md` 73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c.

## Task A2 - Shared library and regression gates (no model)

Write `scripts/lib/phase4_common.py` (dataset-agnostic arrays in, numbers out): average-rank partial Spearman by OLS residualisation on ranks (any number of controls); decile-stratified Spearman; between/within-position
decomposition; within-position and within-bin permutation; the zero-epistasis simulation harness that wraps the project's unmodified own_e.b pipeline with a pluggable noise model and planting; the planting power curve and
minimum-detectable-effect interpolation; the whole-placebo-test position bootstrap; 2x2 geometry helpers; AUROC and balanced-PR area; and the outcome-word functions of each frozen block exactly as written. Import corrected-bootstrap and
`phase3_common` functions rather than re-deriving them. Pre-register the docstring first.

**Gate A2-G1 (HARD):** re-run `scripts/159_phase3_common_gate.py` unchanged: it must still print **40/40 PASS**. **Gate A2-G2 (HARD):** through the new library, reproduce to the stated tolerances: the rho table sha256
`e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796`; A222V rho -0.088118064 (full) / -0.090021683 (H); p_spec(neg) 2/79 `{G_P254F}` and 4/79 `{AV_195, AV_220, G_P254F}`; the linear partial controlling
the baseline ESM-2 score **-0.06414804421216103** (1e-12; Phase 1 C1: rho(delta, S_W) -0.32376573717755663, rho(own_e.b, S_W) +0.085391652432165, 72.8% retained); the two-covariate linear partial **-0.0829** (4 dp, Phase 1 L2).
**Gate A2-G3 (HARD):** toy-data gates for every new function with hand-fixed expectations (a planted pure-between and a planted pure-within structure are recovered by the decomposition; partial correlation equals the closed-form
formula; AUROC and balanced-PR agree with scikit-learn to 1e-12).

## Task A3 - Module S: the sign convention note (cached; no model)

Goal: state the sign convention once, correctly, with a worked example, before anything else is written about the anchor.

- **S-1 Quote, with file and line numbers:** how own_e.b is built (`rebuild_interaction_fit` in `scripts/lib/stats_ext.py`, `wls_line` and `fit_interaction` in `scripts/lib/own_context.py`: the residual `m_score - expected` and
  its weighted intercept), how delta is defined (`esm2_score_a222v_bg - esm2_score`), and the direction of the tail registered in `PHASE2_PREREG.md` (read only).
- **S-2 Worked example (computed, not typed):** among variants with `se_e_b` below the median and finite delta and baseline score, print the 3 with the most positive and the 3 with the most negative own_e.b: position, wild type, mutant,
  S_W, S_A, delta, base functionality, the observed A222V-background fitness per condition, the expectation, the residual, own_e.b and its standard error. Add one plain sentence per variant built from the computed signs.
- **S-3 Descriptive 2x2:** counts and means of delta by sign of own_e.b and the reverse, overall and within tertiles of S_W; also Spearman(delta, S_W) and Spearman(own_e.b, S_W) (targets -0.3238 and +0.0854).
- **S-4 Across systems:** quote from the data's own documentation or the scripts the sign convention of e_b in GB1 (script 155 / Phase 3a T3: the interaction term and which direction is "fitter than expected") and of e_T in RBD (the repository's column description for
  `bind` and `expr`, and the direction of "stronger"/"weaker"); state for each whether a positive value means fitter/tighter than expected. Quote; do not infer.
- **S-5 Write `docs/tasks/phase4-strengthening/SIGN_CONVENTION.md`** (at most 40 lines): the convention sentence, the worked example, and what a negative rho means in words. Every number in the note is re-derived by an independent recomputation (pandas/numpy only) and printed beside it.
  Do not interpret beyond the sign.

## Task A4 - Module M: mechanism-matched analyses (cached; run to completion in this session)

Implement `MECH_ANCHOR_PREREG_v1.md` exactly (scripts 165 and next). Quote `rebuild_interaction_fit` and the aggregation verbatim; the simulation must call the project's **unmodified** pipeline (scripts 153's wiring is the template: its identity gate G-M1(c) shows
how the rebuild is fed). Gates G-M0 to G-M7 of the frozen block, all hard. Smoke at reduced draws (N_BOOT 300, simulation 100, stability 100), then full; time each. Report M-1 to M-6 with every number the block lists and each frozen word, side by side with the
original values, plus:

- the planting power curve as a printed table (r0, mean observed rho, power) and the minimum detectable |r0| at 80% power;
- the null-versus-observed placement for M-3 (primary and both sensitivities);
- for M-5, a table of A222V's two components, their CIs, the S1/S2 retained fractions, and each component's p_spec on both views.
Do not interpret beyond the frozen words.

## Task A5 - Module U: predictive utility (cached + one acquisition)

Implement `UTILITY_PREREG_v1.md` exactly. **U-1** is cached. **U-2** needs data: from MaveDB (`urn:mavedb:00000049`, Weile et al. 2021, AJHG 108:1283-1300; eight experimental maps) via its public API, list the score sets, download only the scores (abort above 200 MB total) and
record URL, status, bytes and sha256; obtain the paper's pathogenic and random reference variant sets from its supplement (PMC8322931) if reachable within 20 minutes; otherwise use the fallback in the frozen block (the project's `task102_clinvar_atlas_overlap.csv`) and **disclose it as a different label set**.
Report class sizes before any metric. If either class has fewer than 15 variants: UNDERPOWERED, no word. Gates G-U0 to G-U3, all hard for the item they guard. If the network fails, log `BLOCKED` for U-2 only (U-1 stands) and do not substitute another dataset.

## Task A6 - Module G: GB1 locality (cached; run to completion in this session)

Implement `GB1_LOCALITY_PREREG_v1.md` exactly, importing script 155's partner-table construction (or transcribing it verbatim under a `QUOTED SOURCE` comment with line numbers, gated against its printed 410,271 rows). Gates G-D0 to G-D3. G-3 (structure) is optional: attempt PDB 1PGA chain A
from RCSB only after the primary analyses are logged, verify numbering against the assayed 56-mer, and skip with a one-line reason if it cannot be verified. Report G-1 and G-2 with every number and each frozen word.

## Task A7 - Module N: neighbour arm (build, gate, time; scoring is for the night)

Implement `NEIGHBOUR_ARM_PREREG_v1.md` exactly.

- **A7a Geometry and cells.** Reuse the Diagnostics II script 139 structure loader (import if `main()` is guarded and torch-free; else transcribe verbatim with a `QUOTED SOURCE` comment). Print the eligible-position count per cell **before any draw**
  (planning figure: roughly 40 to 60 positions within 12 A; C3 may be small or empty). Gate G-N0: the loader reproduces the stored d3 for the 67 resolved existing nulls to 1e-6.
- **A7b Roster.** Draw per frozen section 3, write `data/processed/phase4/neigh/roster_v1.csv` and its sha256 **before any scoring**, with the round-robin scoring order; report new backgrounds per cell, the size of NB (new C1 and C2 plus the six existing nulls) and
  the expected passes (about 455 per background). If |NB| < 30 is already certain, say so now.
- **A7c Scoring script** (`scripts/17x_neigh_score.py`). Read `scripts/124_phase2_score_backgrounds.py` and reuse its atomic-write and skip logic and, if it can be imported, its scoring function; otherwise use `scripts/lib/esm_scoring.py::get_position_logprobs` and `get_device()` directly:
  one unbatched forward pass per (background, position), masked-marginal, all 19 substitutions from the pass, ESM-2 650M, delta against the cached WT-background score. Flags: `--frame {H,nonH}`, `--only`, `--out-dir`, `--limit-roster`. Per-background files
  `data/processed/phase4/neigh/bg_<id>.csv`, written atomically only when every position is done; manifest append; exit 3 on a failed gate. **Gate G-N2 (HARD, model, scratch directory only):** rescoring AV_220 on H reproduces its cached rows, including delta, to 1e-6; the same background scored twice is identical; the wild-type residue's log-odds is 0.
- **A7d Timing smoke.** Score 3 roster backgrounds on H into a scratch directory; report median seconds per pass and project the full stage: `(backgrounds x passes) x s/pass x 1.25`; compare with the **330-minute** budget. Do not shrink the roster; if the projection exceeds the budget, record it and apply the stage rule in A9.
- **A7e Analysis script** (`scripts/17x_neigh_analysis.py`, no torch): frozen sections 5 and 6, reading existing nulls' H-frame rho_b from the D1 table and checking it against a recomputation from the cached rows. Modes smoke/full. **Gate G-N4 (HARD):** planted tests on the real geometry
  (3D-only, sequence-only, none).

## Task A8 - Module L: model ladder (build, gate, time; scoring is for the night)

Implement `MODEL_LADDER_PREREG_v1.md` exactly.

- **A8a Checkpoints.** List the local torch hub cache. **Authorisation (Arnav, this doc):** if `esm2_t30_150M_UR50D` and/or `esm2_t12_35M_UR50D` are missing, download only those two (and their `-contact-regression` files if the loader requires them) from the official `dl.fbaipublicfiles.com/fair-esm/models/` location
  used by the `facebookresearch/esm` repository, into the standard cache; verify the URL with a HEAD request first, record bytes and sha256, require free disk >= 5 GiB afterwards, and never download any other model. If this cannot be done, log `BLOCKED` for module L and continue.
- **A8b Scorer** (`scripts/17x_ladder_score.py`). Same protocol as A7c with `--model {650M,150M,35M}`; read `scripts/lib/esm_scoring.py` first and, if its loader is fixed to 650M, load the other checkpoint through the same package loader and pass it to the same masked-marginal function; do not edit the library. Outputs under
  `data/processed/phase4/ladder/<model>/`. **Gates G-L1 to G-L3 (HARD):** parameter count printed; the 650M path through this scorer reproduces cached AV_220 on H to 1e-6; per model determinism and wild-type-zero.
- **A8c Timing smoke.** Per smaller model: the WT arm on H plus 3 backgrounds; report s/pass and project `(97 x 455 + 455)` passes x 1.25 against the budget in A9 (planning guess: 150M about 2-4x faster than 650M, 35M about 8-15x faster; **measure, do not assume**).
- **A8d Analysis script** (`scripts/17x_ladder_analysis.py`, no torch): frozen section 2, reading the cached 650M rows for the same H rows. **Gate G-L4 (HARD):** planted signal/null on synthetic scores.

## Task A9 - Orchestration: Phase 4 driver, two plans, a stronger lock, tests (end at READY-TO-LAUNCH)

Reuse, do not edit, `scripts/lib/phase3_guards.py` and the Phase 3 driver's design (read `scripts/phase3_driver.py` and `STATE_FOR_LAUNCH.md` in `docs/tasks/phase3-overnight/` first). If the Phase 3 driver is plan-configurable, use that; otherwise write `scripts/phase4_driver.py` and
`scripts/launch_phase4_overnight.sh` as new files with `--plan A|B`, separate state files (`driver_state_phase4A.json`, `driver_state_phase4B.json`) and logs.

- **The Phase 3 flake.** Phase 3's `test_double_start_second_refuses` failed once, root cause never found. Before anything else: read the lock code, state what could allow a second start, and **replace the lock with an `fcntl.flock` on a lock file plus a PID liveness check** (the atomic `mkdir` lock may stay as a second layer). Demonstrate the double-start refusal **50 of 50** times in a loop (isolated temp dir, stub stage).
- **Plan A (night A):** SA1 neighbour-arm scoring on H (`--frame H`); SA2 neighbour-arm analysis (runs only if >= 24 of the C1 + C2 backgrounds are complete, each with >= 95% of its eligible H positions; otherwise logged and skipped); SA3 integrity pass.
- **Plan B (night B), in this priority order:** SB1 ladder 150M scoring; SB2 ladder 35M scoring; SB3 ladder analysis; SB4 neighbour-arm secondary scoring (`--frame nonH`, the same backgrounds, completing the full 654-position frame); SB5 neighbour-arm secondary analysis; SB6 integrity.
  Per-stage budgets = 1.5 x the projection from the timing smokes (never above 330 minutes for SA1); **the per-night total never exceeds 450 minutes; stages that do not fit are moved, in reverse priority, to a night C plan** and the move is stated in `STATE_FOR_LAUNCH.md`.
- Guards before every stage, retry rule, state and heartbeat, TERM forwarding, timeout kill, `--dry-run`, wait-then-skip policy: as in Phase 3 (AC power and charge >= 30%; swap < 3.0 GB; free memory >= 25%; disk >= 5 GiB; up to 3 attempts on a non-gate crash, never on exit 3). The launcher refuses below 35% free memory and when a lock is held.
- **Tests (all hard, isolated temp directory, stub stages, never real outputs):** double-start 50/50; stale lock; TERM forwarding and lock removal; timeout; retry versus exit 3; each guard with simulated readings (`PHASE3_FAKE_*` equivalents); `--dry-run` for both plans; resume skips completed stages; coverage-rule skip. Disclose every deviation.
- **Write `docs/tasks/phase4-strengthening/STATE_FOR_LAUNCH.md`:** every staged script with sha256 (one `path sha256 <hash>` per line), expected durations from the timing smokes against the budgets, the exact launch / monitor / stop / resume commands for each plan, and **a ready-to-paste `git add` command listing every new file by explicit path**. **Do not launch.**
- **S-A SUMMARY:** status per module (S, M, U, G done; N, L staged or BLOCKED and why); every frozen word produced so far (M, U, G) with its numbers; every gate with value; projected nights; deviations; the single entry to read first with its line number. Then **STOP**. Do not poll, sleep-wait or start scoring.

---

# PART B - THE NIGHTS (Arnav launches by hand; OpenCode closed)

Before each night: plugged in and **charging**, lid open, Low Power Mode off, everything heavy quit, and if swap was above 2 GB at any point since the last reboot, **restart the Mac first** (swap is not released by closing apps). Launch **once**:
`bash scripts/launch_phase4_overnight.sh --plan A` (night A), then, after a light morning check of `driver_state_phase4A.json`, `--plan B` the next evening. Do not `tail -f`, do not open OpenCode. If interrupted, re-run the same launch command (completed backgrounds are skipped).

---

# PART C - SESSION 4b (after both nights; OpenCode; verification, interpretation, reproduction package)

Use `PHASE4B_MORNING_LOG.md`, same template. Tasks in order:

- **C0 State and integrity.** Read both state files and logs; confirm nothing is alive; count `bg_*.csv` per frame and model against the roster (set equality); dedupe manifests into NEW files; verify the sha256 of every staged script against `STATE_FOR_LAUNCH.md` (flag any change) and of all five pre-registrations.
- **C1 Re-gate.** Rerun the cheap gates on real outputs (coverage, own-position exclusion, bootstrap reference gate, the A2 gates). If idle and memory allows: rescore 3 never-re-scored new backgrounds on H (one per cell) and 2 backgrounds per ladder model into scratch directories and compare to the night's files at 1e-6, and prove the real output directories were not written (counts and newest mtimes before and after).
- **C2 Independent recompute** of headline numbers for **every** module (S, M, U, G, N, L) from raw files, **without** calling the staged analysis scripts: all per-background rho_b, every outcome-word input, the planting curve at three grid points, the simulation null's percentiles from a re-drawn sample of 200, and the AUROC differences. Any disagreement stops that module and is reported with both numbers.
- **C3 Interpretation within the frozen words**, per module, with a plain two-sided statement each (no cross-module statements; no pre-written conclusions). State the sign sentence from `SIGN_CONVENTION.md` wherever a rho is discussed.
- **C4 Corrections**, append-only, for any staged-output sentence that contradicts its table.
- **C5 Reproduction package (time-boxed to 90 minutes).** Pin the environment (`pip freeze` for `venv`, kept in `reproduce/requirements.lock`); regenerate `data/processed/DATA_SHA256_MANIFEST.txt`; write `reproduce/REPRODUCE.md` and `reproduce/rebuild_headlines.sh`, which rebuilds the headline numbers of every phase from the cached files and prints a PASS/FAIL table against the values in the logs; **test it in a fresh clone** under `/tmp` with the data restored from the backup archive (Arnav provides its path in the prompt), and record the result. The data stay out of git.
- **S-B SUMMARY** in the order: (1) READ FIRST: which stages completed, timed out, were skipped or failed; (2) S: the sign note; (3) M: every frozen word and number; (4) U; (5) G; (6) N: the position-versus-region word, the distance-separation word, the cell table; (7) L: per-model words and the cross-model agreement numbers; (8) every gate; (9) a plain two-sided statement per module; (10) confirmation nothing protected, earlier or staged was edited, nothing committed, torch only where rule 1 allows; (11) the single most important entry with its line number.

---

# PART D - not for OpenCode (Claude and Arnav, after 4b)

- **Write-up (Claude):** results, limitations and the correction history, in the frozen words, with the sign sentence, citing the corrections files rather than superseded text, and positioned against Nambiar et al. 2025 (bioRxiv 2025.09.14.676130) and the 2026 "Beyond additivity" preprint.
- **Questions for experts (Arnav sends, Claude drafts):** Dr. Nambiar (the preprint's first author; whether a single-background calibration is a valid use of the transformation, and how the preprint treats the regression-to-the-mean channel), the atlas authors (replicate-level data to measure the target's reliability), Dr. Kuhlman (conformational change on dimer dissociation).
- **Archive:** tag the commit that contains the frozen blocks; optionally register the analysis plan on OSF with the five hashes; deposit the reproduction package with a DOI.

## What this phase is NOT

- Not a change to the frozen Phase 2 verdict or to any Phase 3 result or pre-registration.
- Not a source of conclusions written in advance. The frozen words decide.
- Not permission to touch `RESULTS.md`; the alpha discrepancy still needs Arnav's explicit sign-off.

---

## Appendix A - FROZEN: mechanism-matched analyses of the MTHFR anchor

<<<MECH_FROZEN_BEGIN>>>
# MTHFR anchor: mechanism-matched analyses - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Authors: Arnav (PI), Claude (planning).

## 0. What this is, and what it is not

These analyses use cached data and quantities already seen in earlier exploratory work (the anchor, the shift-magnitude confound, the Phase 1 partial correlations). The constructions and outcome words below are fixed before the specific new quantities are computed, but the analyses are NOT
independent of what was already seen; the out-of-sample evidence in this programme comes only from the neighbour-arm and model-ladder pre-registrations. Nothing here changes the frozen Phase 2 verdict.

## 1. Convention and question

own_e.b is positive when a variant is fitter in the A222V background than the project's expectation from the WT-background map. delta = S_A - S_W (S_A: the ESM-2 score with A222V present; S_W: the WT-background ESM-2 score) is positive when ESM-2 scores a variant as more tolerated with A222V present.
The anchor rho = Spearman(delta, own_e.b) = -0.088118 (n = 10,757 variants, 654 positions) is negative: the model's shift runs OPPOSITE to the measured shift. Phase 1 measured rho(delta, S_W) = -0.3238 and rho(own_e.b, S_W) = +0.0854 and a linear partial correlation controlling S_W of -0.0641
(72.8% retained). This pre-registration asks (i) how much of the anchor and of its placebo separation survives removal of the channels through S_W and the base functionality, (ii) how much a zero-epistasis world with the same measurement noise and the same data pipeline would produce,
(iii) what true correlation the pipeline could detect, (iv) whether the anchor lives between positions or within them, and (v) how stable the frozen placebo test is to resampling positions.

## 2. Common definitions

Rows, frames and views are exactly script 125's construction (frame: 10,757 rows / 654 positions; held-out view H: 455 positions / 7,526 rows; each background's rows exclude its own position). Backgrounds: A222V and the 96 Phase 2 backgrounds (Arm V 38, Arm G 40, Arm S 18); the null set N = V u G (78).
rho_b = Spearman(delta_b, own_e.b) over a background's rows. p_spec(neg) = (1 + #{b in N: stat_b <= stat_A222V}) / (1 + 78); p_spec(abs) uses |stat|. Position-cluster bootstrap for statistics computed inside one background; background-level bootstrap across backgrounds; N_BOOT 10,000 and SEED 0 unless stated.
Every bootstrap routine passes identity, draw-by-draw reference (1e-12) and Phase 1 CI reproduction gates.

## 3. Analyses

M-1 Partial-correlation placebo test. PRIMARY control: S_W. SECONDARY control: S_W and the base functionality (the second covariate of Phase 1's R1 and L2). The partial Spearman is the Pearson correlation of the OLS residuals of the average ranks of delta_b and own_e.b on the average ranks of the controls, over a background's rows.
Report, for A222V and every background, the partial rho_b; the A222V partial with a position-cluster bootstrap CI; p_spec(neg) and p_spec(abs) on the full frame and on H; the shift-adjusted p_spec_adj on the partial rho_b (leave-one-out OLS on mean|delta_b|, as Diagnostics II D9); and the retained fraction (partial / raw).
Outcome words (primary control, A222V partial): PARTIAL-SURVIVES iff the CI excludes zero in the negative direction AND p_spec(neg) <= 0.05 (full) AND <= 0.10 (H). PARTIAL-WEAKENS iff the CI excludes zero in the negative direction but a p_spec condition fails. PARTIAL-DOES-NOT-SURVIVE iff the CI includes zero or the sign reverses.

M-2 Stratified correlation (sensitivity; no word). Rows are cut into deciles of S_W (equal-count over the frame); the stratified rho is the weighted mean (weights = rows in the decile) of the within-decile Spearman. Report for A222V (position-cluster bootstrap CI) and p_spec(neg) on the full frame and on H using the stratified rho_b.

M-3 Zero-epistasis simulation null (A222V only). Per draw r = 1..1000 (SEED 0): w*_i = w_i (the WT-background fitness exactly as script 153 defines it, used as the proxy truth); w^sim_i = w_i + N(0, sw_i^2), where sw_i is the per-variant WT-background standard error if the project's data carries one; if it does not, sw_i = 0 (PRIMARY) and a sensitivity uses
sw_i = the median m_se over the frame; m^sim_ic = E_c^iso(w*_i) + N(0, m_se_ic^2), with E_c^iso the cross-fitted isotonic expectation of script 153 (GE-ISO). By construction there is no background-specific epistasis, only a monotone nonlinear relation plus noise. The project's own unmodified pipeline (linear expectation, weighted aggregation across conditions) rebuilds
own_e.b^sim from (w^sim, m^sim); rho^sim_r = Spearman(delta_real, own_e.b^sim_r) over the frame rows. Sensitivity: the generating relation linear (E_c^lin). Report the mean, SD, 2.5th and 97.5th percentiles of rho^sim, the fraction of draws at or below -0.088118, and mean(rho^sim) / (-0.088118).
Outcome words: EXCESS-OVER-ARTIFACT iff -0.088118 is at or below the 2.5th percentile of the primary simulation; CONSISTENT-WITH-ARTIFACT otherwise. The sensitivities are reported with no word.

M-4 Detection limit by planting. As M-3 (primary generating relation) plus a planted term e_plant_i = s_e (r0 z_i + sqrt(1 - r0^2) u_i) added to m^sim_ic for every condition, where s_e = the SD of the recorded own_e.b, z_i = the standardised rank-normal score of delta_real(i), u_i ~ N(0,1) independent, and r0 in {-0.30, -0.20, -0.10, -0.05, 0, +0.05, +0.10, +0.20, +0.30} is the planted true correlation; 200 draws per r0.
Report the mean observed rho and power(r0) = the fraction of draws beyond the 2.5th / 97.5th percentile of the r0 = 0 simulation (lower tail for r0 < 0, upper for r0 > 0); the minimum detectable |r0| at 80% power (linear interpolation; "above the grid" if none reaches it); and the attenuation slope (mean observed rho against r0 over the grid). No word.

M-5 Between- and within-position decomposition. Positions with at least 5 rows in the view qualify. rho_between = Spearman across qualifying positions of the mean delta against the mean own_e.b. rho_within = the mean over qualifying positions of the within-position Spearman, weights = rows in the position, undefined positions skipped.
Report both for A222V (position-cluster bootstrap CI, both components recomputed per resample) and for every background; p_spec(neg) per component on the full frame and on H. Surrogate nulls (1,000 draws each, SEED 0): S1 permutes own_e.b among rows within each position (keeps position-level structure); S2 permutes own_e.b among rows within each of 10 equal-count bins of 3D distance to residue 222 over the resolved positions, unresolved positions forming an eleventh bin
(keeps only the regional profile). Report the anchor under S1 and S2 as mean, 95% range and as a fraction of -0.088118.
Outcome words (full frame, A222V): WITHIN-CARRIED iff rho_within's CI excludes zero in the negative direction AND its p_spec(neg) <= 0.05 AND the between component does not meet both conditions. BETWEEN-CARRIED iff the reverse. BOTH-CARRY iff both meet both conditions. NEITHER-CARRIES otherwise.

M-6 Stability of the frozen placebo test. Position-cluster bootstrap of the whole test: per draw resample positions with replacement (frame: 654; H: 455), recompute rho_A222V and all 78 null rho_b on the resampled rows, and p_spec(neg) and k = #{b in N: rho_b <= rho_A222V}; 2,000 draws (SEED 0) per view. Report the distribution of k, P(p_spec <= 0.05) on the full frame, P(p_spec <= 0.10) on H,
and the standardised effect z = (rho_A222V - mean rho_N) / SD rho_N with its bootstrap CI.
Outcome words, per view: STABLE iff the probability is >= 0.80; FRAGILE iff it is < 0.50; MODERATE otherwise.

## 4. Gates (hard; a failed gate stops that analysis and nothing is loosened)

G-M0 the prereg hash, the rho table sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796 and the 3D table sha256 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de. G-M1 A222V rho -0.088118064 (full) / -0.090021683 (H); p_spec 2/79 and 4/79 with the named beaters.
G-M2 the Phase 1 partials reproduce: the linear S_W-only partial -0.06414804421216103 (1e-12) and the two-covariate linear partial -0.0829 (4 dp). G-M3 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction. G-M4 simulation identity: with every noise term zero and E_c replaced by the observed m, the pipeline returns the recorded own_e.b (1e-12).
G-M5 planting response: the mean observed rho is non-decreasing in r0 across the grid up to Monte-Carlo error (a more negative planted correlation must produce a more negative observed rho; under the convention in section 1 an agreeing model would give a positive rho). G-M6 toy gates for the stratified statistic and the decomposition. G-M7 the stability bootstrap with every position exactly once returns the observed p_spec and k.

## 5. Wording and disclosure

The negative anchor is described only as the model's shift running opposite to the measured shift, never as agreement. No result here may be described as confirming or undermining a GB1, RBD, neighbour-arm or model-ladder result. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
<<<MECH_FROZEN_END>>>

---

## Appendix B - FROZEN: predictive utility of background conditioning

<<<UTIL_FROZEN_BEGIN>>>
# Predictive utility of background conditioning - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Authors: Arnav (PI), Claude (planning).

## 0. Disclosure

Cached-data analyses on variables for which related correlations were seen earlier; the comparisons below were never computed, but the analyses are not out-of-sample with respect to the project's history.

## 1. Question

Does conditioning ESM-2 on the A222V background (S_A) predict anything better than the plain WT-background score (S_W)? Two uses: (U-1) predicting A222V-background fitness; (U-2) separating pathogenic from reference variants using the benchmark of Weile et al. 2021.

## 2. U-1

Rows: the 10,757-row frame. Response y: the per-variant mean of the A222V-background fitness (m_score) over the four folinate conditions with finite values; descriptive repeats for each condition and on H. Predictors: S_A and S_W. Statistic: Delta = Spearman(S_A, y) - Spearman(S_W, y) on identical rows with a paired position-cluster bootstrap CI (10,000 draws, SEED 0).
Subsets: all rows (PRIMARY), H rows, and the rows in the top decile of |own_e.b|. Context rows: Spearman(S_W, base functionality) and Spearman(S_A, y).
Outcome words (PRIMARY): CONDITIONING-HELPS iff the CI lies entirely above zero; CONDITIONING-HURTS iff it lies entirely below zero; EQUIVALENT iff it lies inside (-0.02, +0.02); INCONCLUSIVE otherwise.

## 3. U-2

Data: the eight experimental maps and the reference variant sets of Weile et al. 2021 (MaveDB urn:mavedb:00000049 and the paper's supplement). If the pathogenic reference set cannot be obtained, the fallback is the project's ClinVar overlap file (pathogenic or likely pathogenic versus benign or likely benign), disclosed as a different label set. Variants: those with a label and finite S_W and S_A.
Predictors: S_W, S_A and, as positive controls, the experimental A222V-background map at 25 ug/mL folinate and the WT-background map at the lowest folinate. Metrics: AUROC (PRIMARY) and the area under the balanced precision-recall curve (balanced precision = TPR / (TPR + FPR)); paired position-cluster bootstrap CIs (10,000 draws) on Delta AUROC = AUROC(S_A) - AUROC(S_W).
Outcome words (PRIMARY, Delta AUROC): as U-1 with the same margin of 0.02. UNDERPOWERED iff either class has fewer than 15 variants; then no word is given and the CI is reported.

## 4. Gates

G-U0 the prereg hash; frame rows 10,757 / 654; Spearman(own_e.b, S_W) = +0.0854 reproduces (4 dp). G-U1 the MaveDB A222V-background 25 ug/mL scores correlate with the project's own A222V-background fitness for that condition at Spearman >= 0.90 over shared variants (otherwise the maps are not the same data: stop U-2).
G-U2 among the experimental maps the A222V-background 25 ug/mL map attains the highest area under the balanced precision-recall curve on the label set (the ordering Weile et al. report); if not, U-2 is reported UNVERIFIED-LABELS with no word. G-U3 the AUROC and balanced-PR implementations agree with scikit-learn on toy data (1e-12) and the bootstrap passes the reference gate.

## 5. Wording

Statements concern ESM-2 scores in this one gene; there is no claim about clinical use.
<<<UTIL_FROZEN_END>>>

---

## Appendix C - FROZEN: GB1 locality of model shifts versus measured epistasis

<<<GB1D_FROZEN_BEGIN>>>
# GB1 locality of model shifts versus measured epistasis - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Uses the 400 scored backgrounds of the GB1 regime map (v2). The Phase 3 results for those backgrounds have been seen; these are new quantities computed from the same scores.

## 1. Question

In GB1 every background has its own measured epistasis e_b and ESM-2 shift delta_b. Do the model's shifts decay with sequence separation from the background (a local perturbation), does the measured epistasis decay in the same way, and does the per-background correlation rho_b depend on separation?

## 2. Quantities (primary threshold: Input Count >= 25; all rows as in script 155; separation s = |pos(b) - pos(v)| in residues)

G-1 Per background: lambda_model,b = Spearman(|delta_b(v)|, s); lambda_data,b = Spearman(|e_b(v)|, s); d_b = lambda_model,b - lambda_data,b. Across the 400 backgrounds: the mean, SD and fraction negative of each, and a background-level bootstrap CI (10,000 draws, SEED 0) for the mean of each.
G-2 Separation strata: near s in 1-5, mid 6-15, far 16-54. Per background and stratum with at least 50 partners: rho_b,stratum = Spearman(delta_b, e_b). Across backgrounds per stratum: the mean with a background-level bootstrap CI; and the paired difference near - far with its CI.
G-3 (secondary) If a GB1 structure (RCSB PDB 1PGA, chain A, Calpha atoms) can be obtained and its numbering verified against the assayed sequence, repeat G-1 and G-2 with the Calpha distance in place of s, using strata < 8, 8-14 and > 14 Angstrom; otherwise skip and say why.

## 3. Outcome words (numeric)

MODEL-DECAYS iff the CI of the mean lambda_model lies entirely below zero. DATA-DECAYS iff the CI of the mean lambda_data lies entirely below zero. LOCALITY-DIFFERS iff the CI of the mean d_b excludes zero. SEPARATION-MATTERS iff the CI of the mean paired difference (near - far) excludes zero; SEPARATION-NOT-RESOLVED otherwise, reported as "n cannot resolve this", never as "no relationship".

## 4. Gates

G-D0 the prereg hash; the partner table reproduces script 155's 410,271 rows and its 400 rho_b values (max |diff| < 1e-12 on 10 sampled backgrounds) and the primary mean -0.009125. G-D1 no partner at a background's own position enters. G-D2 planted decay on synthetic scores: with |delta| built to decay with s plus noise the mean lambda_model is negative with its CI below zero; with |delta| independent of s it is not
(fire rate <= 0.15 over 100 draws). G-D3 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 5. Wording

This characterises the statistic in GB1 only; no sentence reads for or against any MTHFR or RBD result.
<<<GB1D_FROZEN_END>>>

---

## Appendix D - FROZEN: position versus region, the neighbour arm

<<<NEIGH_FROZEN_BEGIN>>>
# Position versus region: neighbour arm - pre-registration v1

Frozen 2026-10-02, before any new background is selected or scored. Authors: Arnav (PI), Claude (planning). This is NEW data and an out-of-sample test.

## 1. Question

A222V's background shift correlates with its measured epistasis (rho = -0.0900 on the held-out frame H) more strongly than most placebo backgrounds, but backgrounds at nearby positions behave similarly, and sequence distance and 3D distance to residue 222 are collinear. Is A222V's rho extreme relative to backgrounds at spatially nearby positions (position-specific), or typical of its neighbourhood (region-like)?
And is the locality gradient carried by 3D distance, by sequence distance, or by both?

## 2. Geometry

From PDB 6FCX chain A (the loader of Diagnostics II script 139): d3(p) = Calpha-Calpha distance from residue p to residue 222; dseq(p) = |p - 222|. Eligible positions: frame positions that are resolved in 6FCX chain A, other than 222. Cells: C1 near-near (d3 <= 12 and dseq <= 20); C2 3D-near and sequence-far (d3 <= 12 and dseq > 40);
C3 sequence-near and 3D-far (d3 > 18 and dseq <= 25); C4 far-far (d3 > 20 and dseq > 40), represented by the existing nulls, nothing new scored there.

## 3. Backgrounds (fixed before scoring, fitness-blind)

All eligible positions per cell are listed with their cell membership before any draw. New backgrounds are single substitutions. Alanine first: every eligible alanine in C1 and C2 receives A->V (the substitution type of A222V). Remaining slots are filled by positions drawn with numpy.random.default_rng(0) from the cell's eligible positions not already used, each with a mutant drawn uniformly from the 19 non-wild-type residues from the same generator.
Caps on new backgrounds: C1 16, C2 28, C3 10 (all eligible positions if fewer). No (position, mutant) pair already among the 96 existing backgrounds or A222V is reused. The roster (cell, position, mutant, d3, dseq, with the scoring order interleaved round-robin across cells so that any completed prefix is balanced) is written and hashed before scoring.

## 4. Scoring

ESM-2 650M, masked-marginal, one unbatched forward pass per (background, position). PRIMARY frame: the 455 held-out positions H, minus the background's own position; delta uses the cached WT-background ESM-2 score. SECONDARY frame: the remaining 199 non-H positions, scored in a later stage so that the full 654-position frame completes.

## 5. Primary test and words

The neighbourhood null set NB = the new backgrounds in C1 and C2 plus the existing nulls with d3 <= 12 (six: G_I192T, AV_220, AV_155, AV_195, G_L178T, AV_175). rho_b is Spearman(delta_b, own_e.b) over a background's rows on H (A222V: -0.090021683). p_NB(neg) = (1 + #{b in NB: rho_b <= rho_A222V}) / (1 + |NB|); p_NB(abs) uses |rho|.
POSITION-SPECIFIC iff |NB| >= 30 AND p_NB(neg) <= 0.05. REGION-LIKE iff |NB| >= 30 AND p_NB(neg) > 0.10. UNRESOLVED iff |NB| >= 30 and 0.05 < p_NB(neg) <= 0.10. UNDERPOWERED iff |NB| < 30 (no interpretation). The same-site rank (A222V among the 18 Arm S, 2/19) is reported beside it. The full-frame version is computed when the secondary frame completes (secondary; no word).

## 6. Separating the two distances

Pool P = all new backgrounds plus the existing nulls with a resolved d3 (67); rho_b on H. The partial Spearman of rho_b with d3 controlling dseq, and with dseq controlling d3, each with a background-level bootstrap CI (10,000, SEED 0). Cell means of rho_b with CIs for C1, C2, C3 and C4 (the existing nulls with d3 > 20 and dseq > 40), and the contrasts C2 - C4 (3D-near, sequence-far versus far-far)
and C3 - C4 (sequence-near, 3D-far versus far-far) by background-level bootstrap.
3D-LOCAL iff the d3 partial's CI excludes zero and the dseq partial's CI includes zero. SEQUENCE-LOCAL iff the reverse. BOTH-LOCAL iff both exclude zero. NEITHER-RESOLVED iff both include zero.

## 7. Gates

G-N0 the prereg hash; the geometry loader reproduces the stored d3 for the 67 resolved existing nulls (max |diff| < 1e-6) and the cell counts are printed before the draw. G-N1 the roster is written, hashed and re-read before any scoring; no duplicate pairs; counts per cell. G-N2 the new scorer reproduces the cached rows of an existing background (AV_220) on H to 1e-6 including delta; scoring the same background twice is identical (1e-6); the wild-type residue's log-odds is 0.
G-N3 each new background scores at least 95% of its eligible H positions. G-N4 planted gates on the analysis, on the real geometry: synthetic rho_b = a + b d3 + noise returns 3D-LOCAL, = a + b dseq + noise returns SEQUENCE-LOCAL, = noise returns NEITHER-RESOLVED (fire rate <= 0.15 over 100 draws). G-N5 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 8. Wording and disclosure

POSITION-SPECIFIC and REGION-LIKE describe A222V relative to the sampled neighbourhood in this protein only. A222V's own measured epistasis is the only target and all backgrounds are scored against it, as in Phase 2. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
<<<NEIGH_FROZEN_END>>>

---

## Appendix E - FROZEN: ESM-2 model ladder

<<<LADDER_FROZEN_BEGIN>>>
# Model ladder for the background-shift test - pre-registration v1

Frozen 2026-10-02, before any ladder score exists. The ESM-2 650M results are cached. New data: ESM-2 150M and ESM-2 35M.

## 1. Question

Do the anchor, its placebo separation and its locality gradient appear with other ESM-2 sizes, and do the models agree with one another about the background shifts themselves?

## 2. Design

For each model in {150M, 35M}: score A222V and the 96 Phase 2 backgrounds (the same roster) on the 455 held-out positions H (minus each background's own position), plus the wild-type arm on H, with the same masked-marginal protocol as the 650M scoring.
Per model, and for the cached 650M on the same H rows: A222V rho_H = Spearman(delta, own_e.b) with a position-cluster bootstrap CI; p_spec_H (neg and abs) against N (78); the partial rho_H controlling that model's S_W; the gradient Spearman(rho_b, d3) over the 67 resolved nulls (background-level CI); the shift confound Spearman(rho_b, mean|delta_b|) over the 96 backgrounds; and cross-model agreement:
for each background the Spearman between its delta vector under 650M and under the smaller model on common H rows (report the median and range over the 97 backgrounds), and the Spearman across the 97 backgrounds between rho_b under the two models.

## 3. Outcome words (per model; numeric)

MODEL-REPLICATES iff the CI of rho_A222V on H lies below zero AND p_spec_H(neg) <= 0.10. MODEL-DOES-NOT-REPLICATE iff the CI includes zero or the sign reverses. MODEL-PARTIAL otherwise.

## 4. Gates

G-L0 the prereg hash. G-L1 the checkpoint loads from the local cache (or the authorised download verifies) and reports its parameter count. G-L2 the 650M path through the new scorer reproduces a cached background (AV_220) on H to 1e-6. G-L3 per model: scoring a background twice is identical (1e-6), the wild-type residue's log-odds is 0, and each background scores at least 95% of its eligible H positions.
G-L4 the analysis passes a planted signal and planted null test on synthetic scores. G-L5 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 5. Wording

Statements concern these ESM-2 sizes in this gene; models of other families are not covered.
<<<LADDER_FROZEN_END>>>
