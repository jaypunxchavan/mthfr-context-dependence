# PHASE 3a — GB1 regime map: acquisition, machinery validation, frozen pre-registration

**Written:** 2026-09-28 (Claude, planning) · **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase3a-gb1-acquisition/PHASE3A_GB1_ACQUISITION.md`
**Log to write:** `docs/tasks/phase3a-gb1-acquisition/PHASE3A_LOG.md`
**Scripts:** next free numbers. 123–125 (Phase 2) and 126–127 (interface check) are used, so expect
**128, 129** — verify with `ls scripts/*.py | tail` before creating anything.

---

## 0. Why this session exists, and what it deliberately does not do

**The question Phase 3's GB1 arm answers:** the MTHFR anchor is one number from one background
(A222V) in one protein. Olson, Wu & Sun 2014 published a **full pairwise double-mutant matrix** for
GB1 — 509,693–517,278 high-confidence doubles covering all 1,485 position pairs. That means any of
~1,045 single mutants can be treated as a fixed "background" with its real measured partner set,
**using data that already exists**. Computing the shift statistic across ~1,000 backgrounds maps
where it is and isn't well-behaved as a function of regime (distance, background severity, partner
count). One protein, one background gives a number; a thousand backgrounds give a distribution to
locate that number in.

**This is verdict-independent, and that is the point.** The regime map is informative whether Phase 2
returns GENERIC, INDETERMINATE, or A222V BEATS NON-SITE BACKGROUNDS — arguably *most* informative if
the anchor turns out generic, since the map would then characterise the artifact's structure. Nothing
in this doc's interpretation branches on Phase 2's outcome, and nothing here may be written as
supporting or undermining the MTHFR anchor.

**Hard constraints on this session:**
1. **NO MODEL SCORING OF ANY KIND.** Do not import torch or esm. Do not load ESM-2. The MPS device is
   committed to the Phase 2 overnight run, and this machine has already shown severe memory pressure
   (204 MB unused physical memory, 88% swap used) when two large jobs competed. GB1 scoring happens in
   **Phase 3b**, after Phase 2's scoring finishes.
2. **Do not touch `data/processed/phase2/`, `docs/tasks/phase2-full-frame-placebo/`, `run.log`,
   `run.pid`, or `manifest.csv`** — not even to read them. Phase 2 is actively writing there.
3. This session is acquisition, verification, machinery validation on cached data, and a frozen
   pre-registration. Its end state is **READY-TO-SCORE**, not results.

**Prior GB1 work to build on, not duplicate:** the project already ran a GB1 transplant positive
control on a **single fixed background V54A, n=57**, which returned a correctly-centered null,
underpowered: **ρ = +0.122, p = 0.385**. That recorded result is this session's hard reproduction
gate (T3-G1). If the rebuilt machinery cannot reproduce it, the machinery is wrong and nothing
downstream may proceed.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No model scoring, no torch/esm import, no weight loading** (see §0). If any task seems to require
   it, that task is mis-specified: log `BLOCKED` and stop it.
2. **Position-cluster bootstrap** for any inference (clusters = background-partner *positions*, never
   rows). `N_BOOT=300` smoke, then `N_BOOT=10000` full, `SEED=0`. Pre-registration (construction,
   gates, decision rule) in each script's docstring **before** its first run.
3. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold, never edit
   a reference value, never re-run until it passes.
4. **Protected files — never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
   `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, `PHASE2_PREREG.md`, and every earlier log.
5. **Do not commit, do not push.**
6. `venv/bin/python3` always. Missing small package:
   `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it; if it fails, `BLOCKED`.
   Never install torch/esm or download model weights.
7. **Downloads:** T1 may download published supplementary data over the network. Record the exact URL,
   the HTTP status, the byte count, and the **sha256** of every file fetched. If a download fails or a
   URL 404s, log it verbatim and continue to what can be done offline — do not substitute a different
   dataset or a mirror without logging that you did.
8. Verbatim output in every entry; full run output to
   `docs/tasks/phase3a-gb1-acquisition/PHASE3A_<TASK>_FULL_OUTPUT.txt`.
9. If a premise here is wrong, say so plainly. This has happened three times in this project (F1's
   "common 120-position subset", Phase 1b's Ala-position claim, I2's float32 parser) and each time the
   log catching it was worth more than the premise being right.

## S1. Logging instructions

Create `PHASE3A_LOG.md` first with this template; append one entry per task **immediately** after it
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

## Task T1 — Inventory what already exists, then acquire only what's missing

**Check the repo first.** The V54A positive control already ran, so some GB1 data is almost certainly
already on disk. Before downloading anything:
- `grep -rn -il "gb1" scripts/ docs/ data/ --include="*.py" --include="*.md" --include="*.csv" | head -50`
- Identify and **quote** the script that produced the V54A control (the one reporting ρ = +0.122,
  p = 0.385, n = 57) — filename and line numbers — and every data file it reads.
- Report each such file: path, byte size, sha256, row count, and its **column names verbatim**.

**Then, only for what is genuinely missing:** the Olson GB1 full double-mutant matrix
(Olson, Wu & Sun 2014, *Curr Biol* 24:2643–2651, doi:10.1016/j.cub.2014.09.072 — supplementary data).
Record URL, status, bytes, sha256 per §1.7. **Do not download anything you already have.**

Report for the acquired (or already-present) matrix: total rows, how many are singles vs doubles, the
column names verbatim, what the fitness/score column actually is (quote any header or readme), and
whether an error/confidence column exists.

## Task T2 — Verify the matrix against the paper's own published figures (script 128, no torch)

Pre-register in the docstring before running. The paper's claims, to check against the data:
- **Gate T2-G1:** high-confidence doubles fall in **509,693–517,278** (the paper's stated range), out
  of 536,085 possible. Report the actual count and the filter you applied to get it — and quote the
  data's own definition of "high confidence" rather than inventing one. If no such column exists,
  report the raw double count and log that the gate could not be applied as stated (`PARTIAL`).
- **Gate T2-G2:** all **1,485 position pairs** are covered. (GB1's 56 positions give
  C(56,2) = 1,540; the paper says 1,485, so **report the discrepancy explicitly** and determine from
  the data which positions are excluded — do not silently accept either number.)
- **Gate T2-G3:** singles count is ~1,045 of a possible 56 × 19 = 1,064. Report the actual number and
  which singles are missing.
- Report the wild-type GB1 sequence as the data implies it, its length, and whether position numbering
  is 1-based and contiguous.

## Task T3 — Rebuild and validate the transplant machinery (script 128, same run)

**This is the gate that licenses everything else.** Reusing the project's existing transplant code
where it exists (import it if importable; otherwise replicate line-for-line and say so):
- **Gate T3-G1 (HARD):** reproduce the recorded V54A positive control — **ρ = +0.122, p = 0.385,
  n = 57** — from the GB1 data, using the same background (V54A) and the same construction. Match ρ to
  the precision the original recorded it at (report both to full precision, and the absolute
  difference). If it does not reproduce, **STOP. Log `FAIL`. Do not proceed to T4 or T5.** A machinery
  that cannot reproduce the one GB1 result we already have cannot be trusted across a thousand
  backgrounds.
- Report, for V54A: n partners, the partner position list, and the exact definition of the statistic
  as implemented (quote the code).
- **Gate T3-G2:** bootstrap identity — every cluster exactly once reproduces the point estimate to
  1e-12.

## Task T4 — Enumerate the candidate background roster (script 129, no torch, no selection)

Enumerate only; select nothing. For every GB1 single mutant present in the data, report:
`background_id, position, wt_aa, mut_aa, n_partners` (the number of high-confidence doubles in which
it appears), plus the background's own measured single-mutant fitness. Write
`data/processed/gb1_background_roster.csv` and report its sha256.

Report the distribution of `n_partners` (min, quartiles, max) and how many backgrounds have
n_partners ≥ 50, ≥ 100, ≥ 200, ≥ 500. **Do not choose a threshold** — the frozen pre-registration in
Appendix A fixes it. State plainly how many backgrounds would qualify under Appendix A's rule.

## Task T5 — Cost and feasibility audit for Phase 3b's scoring (read-only, no model)

GB1 is a ~56-residue protein versus MTHFR's 656, so per-pass cost will be far lower — but **do not
guess it and do not measure it by running the model.** Instead:
- State the pass arithmetic: for each background, 1 masked-marginal forward pass per scored position
  (PIN-4 convention from Phase 2), positions = GB1 length minus the background's own position.
  Give total passes for the Appendix A roster size found in T4.
- Quote any recorded GB1-scoring timing already in the repo's logs (`grep -rn "ms/pass\|s/pass" docs/`),
  and if the V54A control involved ESM-2 scoring, quote its recorded runtime. If no GB1 timing exists
  anywhere, write **NOT AVAILABLE** and state that Phase 3b must measure it in a smoke run first.
- State explicitly that Phase 3b must not start until Phase 2's scoring has finished, and how to
  verify that (the existence of 96 complete `bg_*.csv` files and a 96-row `manifest.csv`).

## Task T6 — Freeze the pre-registration

Extract the Appendix A block into `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md`
(`mkdir -p` first) using **exactly** this line-anchored command (a looser pattern would also match
this paragraph and leak text):

```
awk '/^<<<GB1_FROZEN_BEGIN>>>$/{f=1;next} /^<<<GB1_FROZEN_END>>>$/{f=0} f' \
  docs/tasks/phase3a-gb1-acquisition/PHASE3A_GB1_ACQUISITION.md \
  > docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md
```

Confirm the output is **73 lines** and contains no `GB1_FROZEN` string, then record
`shasum -a 256` in the log. **Gate T6-G1:** the hash must equal
`b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613`. If it does not, STOP, log
`FAIL`, and report both hashes — do not re-extract until it matches, and do not edit anything to
force a match. Confirm no scoring was launched. **Do not edit the frozen text.** If T1–T5 show the design is
infeasible or a premise is wrong, log that plainly and stop; any change is a new versioned file (v2),
never an edit to v1.

## Task T7 — Housekeeping (read-only)

`git status --short` and `git diff --stat`. Confirm no protected file appears, and confirm
`data/processed/phase2/` and `docs/tasks/phase2-full-frame-placebo/` were neither read nor written by
this session (grep your own scripts for the string `phase2`). Do not `git add`.

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order: (1) **READ THIS FIRST** — T3-G1's V54A reproduction: computed ρ, recorded
ρ = +0.122, absolute difference, PASS/FAIL; (2) T2's three verification gates with actual counts,
including the 1,485-vs-1,540 position-pair discrepancy and its resolution; (3) T1's provenance —
what already existed vs what was downloaded, with URLs and sha256s; (4) T4's roster: total
backgrounds, n_partners distribution, how many qualify under Appendix A; (5) T5's pass arithmetic and
whether GB1 timing is available or NOT AVAILABLE; (6) T6's sha256 and line count; (7) every gate:
name, PASS/FAIL, value; (8) confirmation no model was loaded and nothing under phase2 paths was
touched; (9) a plain statement of what this session establishes — **"nothing about the MTHFR anchor"
is the expected and correct answer**; (10) the single most important entry to read first, with its
line number.

---

## Appendix A — FROZEN text for `GB1_REGIME_PREREG.md`

<<<GB1_FROZEN_BEGIN>>>
# GB1 regime map — pre-registration v1

Frozen 2026-09-28, before any GB1 scoring. Authors: Arnav (PI), Claude (planning).

## 1. Question

Across many fixed single-mutant backgrounds in one protein with a complete double-mutant matrix, how
does the ESM-2 background-shift statistic behave as a function of regime? This maps where the
statistic is and is not well-behaved. It is a characterisation of the statistic, not a test of any
MTHFR result, and its interpretation does not depend on the MTHFR placebo outcome.

## 2. Statistic

For each background b (a GB1 single mutant) and each partner variant v measured in combination with b:
delta_b(v) = S(v | b) − S(v | WT), where S is ESM-2 masked-marginal log-odds vs the wild-type residue,
one unbatched forward pass per (background, position), matching the MTHFR convention.
e_b(v) = the measured genetic-interaction term for the pair (b, v), computed by the same construction
the project's existing GB1 transplant code uses, quoted in the Phase 3a log.
rho_b = Spearman(delta_b, e_b) over b's high-confidence partners, excluding any partner at b's own
position.

## 3. Roster (fixed before scoring)

Every GB1 single mutant with at least **100 high-confidence partners**, capped at **400 backgrounds**.
If more than 400 qualify, take a seed-0 sample: `numpy.random.default_rng(0).choice(sorted_ids, 400,
replace=False)`. The roster is written to disk before any scoring. No fitness-based or
severity-based selection at any point — qualification is by partner count alone.

## 4. Primary analysis

The distribution of rho_b across the roster: n, mean, median, SD, range, and the fraction with
rho_b < 0. Each rho_b carries a position-cluster bootstrap 95% CI (clusters = partner positions,
N_BOOT = 10000, seed 0).

**Pre-registered regime covariates, all fixed now, each tested against rho_b by Spearman with a
position-cluster bootstrap CI and a 10,000-shuffle label-permutation p:**
- (a) mean sequence separation |pos(b) − pos(v)| over b's partners;
- (b) the background's own measured single-mutant fitness;
- (c) n_partners;
- (d) the SD of e_b over b's partners (the dynamic range available to the correlation).

## 5. Decision rules (constants fixed now)

- **Per covariate:** ASSOCIATED iff the bootstrap CI of its Spearman excludes 0; NOT RESOLVED
  otherwise. NOT RESOLVED is reported as "n cannot resolve this," never as "no relationship."
- **Distribution centering:** the rho_b distribution is CENTERED iff the bootstrap CI of its mean
  includes 0; OFF-CENTER otherwise. If OFF-CENTER, that is a property of the statistic in this system
  and must be reported as such, with equal prominence either way.
- **Wording rule:** no result from this map may be described as confirming, supporting, or
  undermining the MTHFR anchor. The systems, backgrounds, and measurement platforms differ. Any
  cross-system statement requires its own pre-registration.

## 6. Gates (a failed gate stops the run; thresholds are never loosened)

- **G-1:** the V54A background's rho_b reproduces the recorded positive-control value (ρ = +0.122)
  to the precision it was recorded at.
- **G-2:** no partner at a background's own position enters any rho_b.
- **G-3:** bootstrap identity — every cluster once reproduces the point estimate to 1e-12.
- **G-4:** each background scores at least 95% of its eligible positions.
- **G-5:** the wild-type GB1 sequence used for scoring matches the sequence the fitness data implies,
  at every position.

## 7. Execution

Detached, resumable, one output file per background, **only after Phase 2's scoring has completed**
(96 complete background files and a 96-row manifest). Smoke run first. Timing measured in the smoke
run, not assumed.

## 8. Disclosure

The MTHFR anchor motivated building this map, but the map's rules and covariates were fixed before any
GB1 score existed and do not reference any MTHFR value. Any deviation must be disclosed in the log and,
if it changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
<<<GB1_FROZEN_END>>>

---

## What this session is NOT

- Not Phase 3b (no GB1 scoring), not the Starr RBD replication, not the multidms refit.
- Not a claim about the MTHFR anchor in either direction.
- Not permission to touch `RESULTS.md`, or anything Phase 2 is writing.
