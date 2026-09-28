# PHASE 2 — Execution doc for the frozen full-frame placebo pre-registration (v1)

**Written:** 2026-09-28 (Claude, planning) · **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase2-full-frame-placebo/PHASE2_EXECUTION.md`
**Binding text:** `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md` (frozen, sha256
`420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`). **This doc only implements it.**
If anything here conflicts with the pre-registration, **the pre-registration wins**; log the conflict,
do not resolve it silently.
**Log to write:** `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (both sessions append to it;
never edit an earlier entry).
**Scripts:** next free numbers; Phase 1b used 120–122, so expect **123, 124, 125** — verify with
`ls scripts/*.py | tail` first.

---

## 0. Structure: two sessions, one human gate

- **Session 2a (this session's first half):** verify integrity, build the roster, build and test the
  scoring script and the analysis script, write the launch script. **OpenCode does NOT launch the
  overnight run.** It ends at status `READY-TO-LAUNCH`. Arnav reads the log, then launches by hand.
- **Human gate:** Arnav runs `bash scripts/launch_phase2.sh` (≈ 9–11 h, detached).
- **Session 2b (a later session, after all 96 background files exist):** run the pre-registered analysis
  and report the verdict verbatim.

Model scoring is allowed **only** in `scripts/124_*` (and the G1 reproduction check, which uses the same
code path). Nothing else in either session may import torch/esm.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **Position-cluster bootstrap only.** `N_BOOT=300` smoke, then `N_BOOT=10000` full, `SEED=0`.
   Docstring pre-registration written **before** each script's first run.
2. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold, edit a
   reference value, raise N and retry, or re-run until a gate passes.
3. **Protected files — never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
   `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, `PHASE2_PREREG.md`, and every earlier log
   (`PHASE1_LOG.md`, `PHASE1B_LOG.md`, all others). Corrections are flagged in place in `PHASE2_LOG.md`.
4. **Do not commit or push.** Arnav commits after review.
5. `venv/bin/python3` always. Missing small package: `venv/bin/python3 -m pip install <pkg> --break-system-packages`,
   log it; if it fails, `BLOCKED`. **Never** download model weights: if
   `esm.pretrained.esm2_t33_650M_UR50D()` tries to download (no local cache), STOP and log `BLOCKED`.
6. **Nothing in the pre-registration may change.** Arms, statistic, decision rule, constants, gates and
   wording rule are frozen. Anything in §2 below is an *implementation pin* that resolves an ambiguity
   without changing a rule; each pin must be logged as used.
7. **No result-peeking edits.** The scoring and analysis scripts are written and their docstrings
   pre-registered before the overnight run starts; they are not edited after any Phase 2 score exists.
   If a bug is found later, log it, fix it in a new numbered script, and report both.
8. Verbatim output in every log entry; full run output saved to
   `docs/tasks/phase2-full-frame-placebo/PHASE2_<TASK>_FULL_OUTPUT.txt`.
9. If a premise in this doc is wrong (Phase 1 found the "common 120-position subset" premise wrong;
   Phase 1b corrected its own Ala-position claim), say so plainly and handle it transparently.

## 2. Implementation pins (resolve ambiguity; change no rule)

- **PIN-1 (Arm G draw).** `rng = numpy.random.default_rng(0)`; `pool = sorted frame positions`
  (654 positions; 222 is not in the frame). `pos = rng.choice(pool, size=40, replace=False)`.
  Then, for each position in the order drawn: `mut = rng.choice(sorted 19 one-letter residues excluding
  the wild-type residue at that position)`. WT residue from `data/raw/P42898.fasta`, residue *p* =
  FASTA index *p*−1 (mapping verified in Phase 1b P1/Q3). Write the roster to disk before any scoring.
- **PIN-2 (duplicates).** If an Arm G entry has the same position **and** mutant as an Arm V entry, keep
  both roster rows as drawn (literal reading of the frozen rule), score both, and disclose the collision.
- **PIN-3 (arms).** Arm S = 18 backgrounds `A222_X` (X not in {A, V}); Arm V = A→V at the 38 non-222
  alanine positions in the frame (Q3 count 38; the >60 cap rule does not trigger; all 38 used);
  Arm G = 40 as PIN-1. Total 96. bg_ids: `A222_<X>`, `AV_<pos>`, `G_<wt><pos><mut>`.
  A222V itself is **not rescored**: its full-frame arm is cached (`delta_esm` in
  `task32_analysis_table.csv`; `merged_wt_a222v_scores.csv` = 12,426 rows).
- **PIN-4 (scoring).** Use `scripts/lib/esm_scoring.py::get_position_logprobs` and `get_device()` exactly as
  scripts 63/69/82 do: ESM-2 `esm2_t33_650M_UR50D`, eval mode, `torch.no_grad`, **one unbatched forward
  pass per (background, position)**, masked-marginal, all 19 non-wild-type substitutions from that pass.
  Do not reimplement the scoring function and do not batch (batching may change numerics and would
  jeopardise G-B).
- **PIN-5 (positions scored).** Every frame position except the background's own position (target ==
  background rows are never used, per frozen G-C). Arm S: 654 positions; Arms V/G: 653.
- **PIN-6 (background sequence).** WT sequence from `scripts/lib/sequence.load_sequence` with the single
  substitution applied; assert the residue at the background position equals the roster WT residue.
- **PIN-7 (usable rows, delta).** Reuse script 109/121's construction: usable rows are the rows of the
  10,757-row frame with non-null `own_e_b`; `delta_b(v) = score_b(v) − esm2_score(v)` joined on
  (position, mut_aa). Read the exact column names from scripts 109/121 and the tables; do not guess.
- **PIN-8 (regions, secondary analysis only).** R1: 2–147, R2: 148–294, R3: 295–474, R4: 475–656.
- **PIN-9 (bootstrap speed).** A naive `scipy.stats.spearmanr` loop over 97 backgrounds × 10,000 draws
  on ~10,757 rows may take 30+ min. You **may** use exact weighted mid-ranks (resample weights = position
  multiplicities) **iff** it is gated against `scipy.stats.spearmanr` on explicit resampled arrays for
  ≥ 5 draws (max |diff| < 1e-12) in the script's own output. Otherwise use the naive loop.
- **PIN-10 (seeds).** `SEED=0`, separate rng streams per bootstrap and per permutation, printed.

## S1. Logging instructions

Create `PHASE2_LOG.md` first with this template; append one entry per task **immediately** after it
finishes:

```
## [TASK ID] — [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

---

# SESSION 2a — build, test, stage (no overnight run)

**Task S0 — Integrity gates (no model)**
- **G-0a** `shasum -a 256 docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md` equals
  `420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`. Else STOP.
- **G-0b** The file is committed: `git log -1 --format='%H %cI' -- docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md`
  prints a hash, and `git status --short` shows it unmodified. If it prints nothing, STOP `BLOCKED`
  ("commit PHASE2_PREREG.md first"): the commit is the pre-registration's timestamp.
- **G-0c** `venv/bin/python3 -c "import torch, esm; print(torch.__version__, torch.backends.mps.is_available())"`;
  log device. If MPS is unavailable, log projected CPU time and mark `BLOCKED` (do not proceed to scoring).
- **G-0d** ≥ 2 GB free disk; log `df -h .`.

**Task R1 — Arm roster (script 123, no torch)**
Pre-register in the docstring, then build `data/processed/phase2_arm_roster.csv` with columns
`bg_id, arm, position, wt_aa, mut_aa` for all 96 backgrounds per PINs 1–3. Report: arm counts (18/38/40),
the 40 drawn (position, wt, mut), any PIN-2 collision, and **`shasum -a 256` of the roster file**.
Gates: arm counts; every `wt_aa` equals the FASTA residue; no position is 222; Arm V positions equal Q3's
list of 38; Arm G positions distinct. This file is written **before** any scoring exists.

**Task R2 — INFORMATIONAL pre-flight (cached only; changes nothing)**
From `task32_analysis_table.csv` (`delta_esm`, `own_e_b`): A222V's Spearman ρ over (i) the full frame
(must reproduce −0.088118 to 1e-6: this is also frozen gate G-A) and (ii) the held-out set H (455 positions,
7,526 usable variants; H = frame positions not in the AE or W frames, from script 122) and (iii) the
held-in positions (3,231 variants). Print all three. Label the entry `INFORMATIONAL: no arm, rule, or
constant may change on the basis of these values; reported so Arnav can decide whether to run.`
Do not compute any placebo quantity in R2.

**Task G1 — Pre-launch reproduction check (frozen gate G-B; uses the model)**
Re-score **three** already-cached backgrounds at their cached 120-position AE grid — the first Arm S row,
the first Arm V row and the last Arm V row of the roster — with the same code path as PIN-4, writing to
`data/processed/phase2_scratch/` only. Compare every (position, mut_aa) score to the cached `task82_ae_raw.csv`
values (read the cached score column name from script 82). **Gate: max |diff| < 1e-6 for each of the three.**
About 360 passes ≈ 3–4 min. If any exceeds 1e-6: **STOP, `FAIL`, do not proceed to G2–G4**, report the
three max diffs and the device. Do not loosen 1e-6.

**Task G2 — Scoring script + smoke/resume test (script 124)**
Write `scripts/124_phase2_score_backgrounds.py` (docstring pre-registered first) implementing PINs 4–6:
reads the roster, scores every background in roster order, writes **one file per background**
`data/processed/phase2/bg_<bg_id>.csv` (`bg_id, position, mut_aa, score`) **atomically** (write `.tmp`, then
rename) only after all positions of that background are done; appends `bg_id, n_positions, n_rows, seconds,
device` to `data/processed/phase2/manifest.csv`; **skips** any background whose complete file already
exists with the expected row count (positions × 19); prints per-background time and a running ETA; logs and
exits nonzero on any exception (never continues past a half-written file). CLI flags: `--only <bg_id>`,
`--limit-positions N`, `--out-dir DIR` (so tests never touch the real output directory).
Test in `data/processed/phase2_scratch/`: (a) `--only` one background with `--limit-positions 5`; (b) run
again and confirm it skips; (c) leave a fake `.tmp` file and confirm it is ignored and overwritten;
(d) confirm the row count is exactly 5 × 19. Log all outputs verbatim.

**Task G3 — Analysis script + validation on cached data (script 125, no torch)**
Write `scripts/125_phase2_analysis.py` (docstring pre-registered first) implementing frozen sections 2, 4,
5, 6 exactly: ρ_b per background on the full frame and on H (recomputed on H rows only for A222V and every
background); position-cluster bootstrap CIs (clusters = frame positions; H: H positions); `p_spec` on full
and H; the outcome word per frozen §5 (GENERIC / A222V BEATS NON-SITE BACKGROUNDS / INDETERMINATE); D_site
with bootstrap CI and 10,000-shuffle label permutation; the within-site Grantham gradient T (CI,
leave-one-out range, minimum detectable |T| ≈ 2.8 × SE, outcome word SUPPORTED / REVERSED / NOT RESOLVED);
secondary region-demeaned analysis (PIN-8) and per-arm tables; frozen gates G-A, G-C, G-D, G-E. Two input
modes: `--mode phase2` (reads `data/processed/phase2/`) and `--mode cached-ae` (builds the same structures
from `task82_ae_raw.csv` for the V group). Validate `--mode cached-ae` at `N_BOOT=300`:
deterministic quantities must reproduce Phase 1b P4's V-group to 1e-9: n=38, mean ρ_b = −0.010138068,
p_spec = 0.025641026 (0 of 38 at or below A222V's −0.104321773), and P2's D = −0.045070706 (n=18 vs 38).
If PIN-9's weighted-rank method is used, print its gate vs `scipy.stats.spearmanr`.
Do **not** run `--mode phase2`; no Phase 2 scores exist yet.

**Task G4 — Launch script (do not run it)**
Write `scripts/launch_phase2.sh`: from the repo root, `nohup` runs `venv/bin/python3
scripts/124_phase2_score_backgrounds.py` in a loop of up to 5 attempts (30 s sleep between; a nonzero exit
retries; completed backgrounds are skipped), appending stdout/stderr to
`data/processed/phase2/run.log`, writing the PID to `data/processed/phase2/run.pid`, and wrapping with
`caffeinate -ims -w <pid>` so the Mac stays awake on AC power. Add a `--dry-run` that only prints what it
would run. Test `--dry-run` only. In the log, record verbatim: how to monitor
(`tail -f`, `ls data/processed/phase2/bg_*.csv | wc -l`), how to resume after an interruption (rerun the
same launch script), how to stop (`kill $(cat data/processed/phase2/run.pid)`), and the projected finish
(96 backgrounds; 62,706 passes = 18×654 + 78×653, versus Q1's 62,784 before each V/G background's own
position is skipped, at the recorded 511–647 ms/pass ≈ 8.9–11.3 h; also state the measured G1
seconds-per-pass from this session). **Do not launch.**

## S2a. SUMMARY mandated for session 2a

Append `## SUMMARY (2a)` in this order: (1) status `READY-TO-LAUNCH` or `BLOCKED` and why; (2) R2's three
informational ρ values, verbatim; (3) G1's three max |diff| values; (4) roster sha256, the 40 Arm G draws,
any PIN-2 collision; (5) every gate: name, PASS/FAIL, value; (6) measured seconds-per-pass and the
projected finish; (7) the exact launch, monitor, resume and stop commands; (8) every PIN used and any
deviation; (9) the single entry Arnav should read first, with its line number. **Then stop.** Do not poll,
sleep-wait, or start scoring.

---

# SESSION 2b — analysis (only after all 96 background files exist)

**Task A1 — Completion and coverage.** Confirm 96 files in `data/processed/phase2/`, each with the expected
row count; read `manifest.csv`; **G-E:** every background scored ≥ 95% of the 654 frame positions (report
the minimum). Confirm nothing in the scoring or analysis scripts changed since 2a (`git status`/`shasum`
against the values logged in 2a). If a script changed, flag it prominently.

**Task A2 — Full analysis.** Run `scripts/125_phase2_analysis.py --mode phase2` at `N_BOOT=300` (smoke),
then `N_BOOT=10000 SEED=0` **detached** (`nohup ... > data/processed/phase2/analysis_run.log &`; poll with
`tail`; the foreground harness kills jobs near 55–65 min). Save the verbatim full output. Gates G-A, G-C,
G-D, G-E must all pass; a failed gate stops the run and is reported as failed.

**Task A3 — Extended reproduction check (descriptive).** Compare freshly scored values to the cached
`task82_ae_raw.csv` for **all** Arm S and Arm V backgrounds on the 120 AE grid positions; report the number
of backgrounds with max |diff| < 1e-6 and the largest max |diff|. No decision rests on this.

**Task A4 — Verdict, verbatim.** Report the outcome word exactly as the frozen rule yields it, with
`p_spec(full)`, `p_spec(H)`, the number of null placebos at or below A222V's ρ in each, the placebo
distribution summary (mean, median, range, per arm), `D_site` (CI, permutation p) and the gradient `T`
(CI, leave-one-out range, minimum detectable |T|, outcome word). State the frozen wording rule: **only
"A222V BEATS NON-SITE BACKGROUNDS" may be written up as supporting background-specificity; GENERIC and
INDETERMINATE get equal prominence.** If the outcome is borderline (a `p_spec` within 0.01 of a threshold),
say so; do not round it toward either pole.

## S2b. SUMMARY mandated for session 2b

`## SUMMARY (2b)` in this order: (1) **READ THIS FIRST** — the outcome word and both `p_spec` values with
the counts behind them; (2) the placebo distributions per arm and where A222V sits (signed rank) in the
full frame and in H; (3) `D_site`; (4) the gradient `T`; (5) region-demeaned secondary result; (6) every
gate, PASS/FAIL, value; (7) A3's reproduction counts; (8) a plain statement of what this changes about the
central claim, stated so that a GENERIC or INDETERMINATE outcome reads with the same prominence as a
positive one; (9) the single entry Arnav should read first, with its line number.

---

## What these sessions are NOT

- Not a change to the pre-registration: `PHASE2_PREREG.md` is never edited; a v2 would be a new file.
- Not permission to touch `RESULTS.md` (the α = 0.05 vs 0.01 fix still needs Arnav's fresh, explicit sign-off).
- Not Phase 3 and not the ESM-2 size ladder.
