# PHASE 2 diagnostics IV - where does the signal live?

**Written:** 2026-09-30 (Claude, planning) | **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV.md`
**Log to write:** `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV_LOG.md`
**Corrections file to write:** `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md`
**Scripts:** next free numbers. Diagnostics III used 140-147, so expect **148 and up**. Verify with
`ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` before creating anything. Shared helpers go in a
**new** file `scripts/lib/phase2_diag4.py`. Do not modify `scripts/lib/phase2_diag.py`, `scripts/lib/phase2_diag3.py`,
or any script numbered 147 or lower (script 144 is superseded code for D15; it is read, never edited).

---

## 0. Why this session exists

Diagnostics III established that the anchor is regional and that its cross-background gradient depends on
target variants within about 30 A of residue 222 (the gradient falls 43% on the full frame and 65% on H at R = 30 A,
far outside the matched-deletion range). Claude's read of the log against its own printed numbers found four things
to fix before anything is written up:

1. **A222V's position-cluster confidence intervals look like an artifact.** D15 reports CIs that include zero in
   all twelve restricted variants. They are 2.8x wider than Phase 1's CI for essentially the same statistic
   ([-0.1105, +0.0529] at R = 0, resolved rows, against Phase 1's [-0.1173, -0.0595] on all rows) and their centres sit
   0.037 to 0.052 above the point estimate in six of eight cells, where Phase 1's centre is within 0.0003 of its
   point estimate. A valid bootstrap is centred near its point estimate. The gate in the Diagnostics III doc
   (every cluster once reproduces the point estimate) is permutation-invariant, so it cannot detect a cluster-to-row
   mapping error. **That was a gap in the planning doc, not in OpenCode's execution.** D18 closes it with a
   reproduction gate against Phase 1 and a draw-by-draw reference implementation.
2. **The matched-deletion control was reported only for the gradient.** The Diagnostics III doc asked for A222V's rho and
   `p_spec` too. Without them, "A222V's own association is roughly halved by removing near-222 variants" is not
   attributable to the removed positions. D19 supplies them.
3. **The location of the signal is only bracketed.** R = 10 changes nothing, R = 20 is marginal, R = 30 collapses
   the gradient, so most of the loss falls between 20 and 30 A. A shell decomposition (D20) locates it, with matched
   controls for shell size.
4. **"Tracks 3D distance, not sequence distance" rests on unmatched counts.** D21 compares removal orderings at
   equal k.

**Nothing here touches the frozen `PHASE2_PREREG.md` verdict.** Every task is descriptive. The session also appends
corrections (D22) to statements in the Diagnostics III log that its own tables contradict.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No model scoring. Do not import torch, esm, or thermompnn.** Everything needed is on disk.
2. **Expected values in this doc are Claude's recomputations, not facts.** Recompute each independently and print it
   beside its target. A mismatch means **the doc is wrong**: STOP that item, report both numbers, do not force
   agreement.
3. **Hard reproduction gate first (D18-G1).** If it fails, STOP the whole session.
4. **Resampling units.** One number per background correlated against another per background: resample
   **backgrounds** (10,000 draws, `SEED=0`, rho_b held fixed). A statistic computed inside one background (A222V's rho
   on a row subset): resample **target positions** (position clusters). The matched-deletion controls recompute
   everything on a deleted position set and do not resample inside a draw. State the unit in every docstring.
5. **Pre-register in each script's docstring before its first run:** construction, primary designation, gates, what
   will be reported. Smoke run first, then full. Time the full run; do not guess.
6. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold or raise N to chase a result.
7. **Protected, never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md` (at `docs/tasks/results-log/`),
   `PROJECT_SUMMARY_FINAL.md` (at `docs/writeups/`), `AGENTS.md`, `PHASE2_PREREG.md`,
   `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md`, and **every earlier log** (including
   `PHASE2_DIAGNOSTICS_III_LOG.md`). Corrections live only in this session's log and corrections file. Do not touch
   `docs/tasks/phase3a-gb1-acquisition/` or `docs/tasks/phase3b-gb1-regime-map/`.
8. **Do not commit, stage, or push.**
9. `venv/bin/python3` always. If a small package is missing:
   `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it; if that fails, `BLOCKED`. Never torch/esm.
10. **Wording.** Never use the frozen outcome words (GENERIC / BEATS / INDETERMINATE) as a label for any result computed
    here. Compare `p_spec` only to the frozen numeric thresholds (0.05 full, 0.10 H) and say "at or below" or "above".
    Rank fractions over small n are rank fractions, not tests.
11. **Flagging a statistic against a matched-deletion range.** Print the S1 value, the range, the empirical fraction of
    random draws at or below and at or above it, and the distance to the nearest bound. Flag it **INSIDE**,
    **OUTSIDE**, or **MARGINAL** (outside but within 0.002 of a bound, or empirical one-sided fraction between 0.01 and
    0.05). Diagnostics III called a 0.001 shortfall "OUTSIDE" and built a headline on it; do not repeat that.
12. **Prose must match the table above it.** Before finalizing each entry, re-read every comparative sentence (more or
    less, higher or lower, inside or outside, "per position") against the printed numbers immediately above it. This
    project's logs have drifted from their own tables four times; the table governs.
13. Verbatim output in every entry; full output to
    `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_<TASK>_FULL_OUTPUT.txt`.
14. If a premise here is wrong, say so plainly and adapt transparently.
15. **Importing earlier scripts.** Import scripts 125, 137, 138, 139, 144 via `importlib` only if `main()` is guarded, the
    import has no side effects, and it pulls in no torch. Otherwise transcribe the needed function verbatim under a
    `QUOTED SOURCE` comment with file and line numbers, and gate the transcription against the original's printed
    output.

## S1. Logging instructions

Create `PHASE2_DIAGNOSTICS_IV_LOG.md` first with this template; append one entry per task **immediately** after it
finishes:

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

## Task D18 - Bootstrap reproduction gate, and corrected CIs for A222V's rho

### D18-G1 (HARD, session-wide): reproduce Diagnostics III's machinery before anything new

All of these must reproduce (tolerance 1e-9 on 9-dp values, 2e-6 on 6-dp values). The matched-deletion ranges are
deterministic at `SEED=0`, `N_DRAW=200` if the **same generator calls as script 144's control loop** are used: read that
loop, quote it, and use it (import or verbatim transcription). Reproducing the printed ranges is what licenses using the
deletion routine for new statistics.

| quantity | full | H |
|---|---|---|
| D1 rho table sha256 | `e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796` | same |
| 3D table sha256 | `69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de` | same |
| `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` sha256 | `8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176` | same |
| `PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md` sha256 | `c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d` | same |
| A222V rho (re-derived) | -0.088118064 | -0.090021683 |
| frozen `p_spec`, beaters | 2/79 = 0.025316456, `{G_P254F}` | 4/79 = 0.050632911, `{AV_195, AV_220, G_P254F}` |
| k_R (positions removed, resolved universe), R = 10 / 20 / 30 | 23 / 121 / 247 | 13 / 86 / 172 |
| S1 A222V rho, R = 10 / 20 / 30 | -0.079237139 / -0.065947891 / -0.027360127 | -0.082101889 / -0.063596629 / -0.024367374 |
| S1 gradient (n = 67), R = 10 / 20 / 30 | +0.689454255 / +0.662097177 / +0.400678440 | +0.686580864 / +0.640347202 / +0.241344907 |
| S1 `p_spec` (n = 78), R = 10 / 20 / 30 | 0.037975 / 0.037975 / 0.063291 | 0.037975 / 0.050633 / 0.101266 |
| matched-deletion gradient range, R = 10 | [+0.680407, +0.706900] | [+0.675494, +0.702836] |
| matched-deletion gradient range, R = 20 | [+0.663147, +0.723051] | [+0.642047, +0.720172] |
| matched-deletion gradient range, R = 30 | [+0.615026, +0.731210] | [+0.602547, +0.726413] |

If any row fails, STOP the whole session and log `FAIL`.

### D18.0 - what did Phase 1 do?

Locate in `PHASE1_LOG.md` [A1] the line containing `headline row reproduced exactly` and the script that printed it
(`scripts/91_a2_disattenuation.py` and whatever it calls). **Quote verbatim, with file and line numbers:** how clusters
are drawn, what a cluster is, how rho is computed on a resample, `N_BOOT`, and the seed. Phase 1's published CI for the
unrestricted anchor is **[-0.1173334458953319, -0.0595113844951173]** (point -0.0881180642489173).

### D18.1 - reproduce Phase 1's CI

Run **Phase 1's own routine** on A222V's unrestricted rows with its own seed and `N_BOOT`.
**Gate D18-G2 (HARD for D18):** it reproduces the published CI to 1e-9 if the seed and code are recoverable. If the exact
stream cannot be recovered, the gate is Monte-Carlo agreement: both endpoints within 0.003 of the published ones and
the bootstrap median within 0.002 of the point estimate; state which version applied and why.

### D18.2 - run D15's routine on the same rows, and on restricted rows

Run script 144's `pos_cluster_boot` on (i) the same unrestricted rows, (ii) the R = 0 resolved rows, (iii) S1 R = 10, 20,
30 (full view). Print for each: point, 2.5/50/97.5 percentiles, SE, centre-minus-point, width. Compare with D18.1.

### D18.3 - draw-by-draw reference implementation

Write the obvious, slow reference: for a pre-drawn array of sampled position labels `ids`, `idx = np.concatenate([rows_of[p]
for p in ids])`, rho = `scipy.stats.spearmanr(d[idx], y[idx])`. Drive the reference **and** the routine under test
with the **same pre-drawn `ids` arrays** (if the routine samples internally, record its sampled positions). **Gate D18-G3
(HARD for D18):** the first 200 draws agree to 1e-12 on each of (i)-(iii) above. The point-estimate identity gate alone
is insufficient because it is invariant to which rows a cluster contains.

### D18.4 - if anything fails: find the defect, fix it in a new function

Quote the failing lines of script 144, say what is wrong, and write a corrected routine in `scripts/lib/phase2_diag4.py`.
**Do not edit script 144.** Gate the corrected routine against D18.3's reference (1e-12) and against D18.1's Phase 1
reproduction. If nothing fails and D15's routine matches Phase 1 on unrestricted rows, then the R = 0 resolved-row
width needs another explanation: compute Phase 1's routine on the **resolved** rows and show whether it, too, widens.

### D18.5 - recompute all twelve CIs

With the validated routine (`N_BOOT=10000`, `SEED=0`, clusters = retained target positions): S1 R = 0, 10, 20, 30 on
both views (8 cells) and the sequence sensitivities Rs = 25 and 50 on both views (4 cells). Report point, CI, median,
SE, centre-minus-point, width, whether it excludes zero, and the old D15 CI beside it. Flag any cell whose
|centre - point| exceeds 0.01.

---

## Task D19 - Matched-deletion ranges for A222V's rho and `p_spec`

**Why:** the Diagnostics III doc required them and the log reported ranges only for the gradient.

Pre-register in the docstring. For S1 R = 10, 20, 30 on both views, with the gated deletion routine
(`N_DRAW = 200`, smoke at 20, `SEED=0`): for **A222V's rho**, **the number of nulls at or below A222V** (`k`), and
**`p_spec`**, report the S1 value, the random-deletion mean, SD, 2.5th and 97.5th percentiles, the fractions of draws at
or below and at or above the S1 value, the distance to the nearest bound, and the INSIDE/OUTSIDE/MARGINAL flag (rule 11).
Also print the random-deletion mean of A222V's rho beside the R = 0 resolved baseline (full -0.076685523, H -0.080432398)
so the reader sees whether thinning alone moves it. Name the nulls at or below A222V in the S1 case.

Report the claim D15 made, in its own terms: "A222V's rho falls 64% (full) and 70% (H) at R = 30". State whether that
fall is inside or outside what deleting 247 (172) random positions produces.

---

## Task D20 - Shell decomposition, with matched controls for shell size

**Why:** R = 10 changes nothing, R = 20 is marginal, R = 30 collapses the gradient. That brackets where the signal lives
but does not locate it.

Pre-register in the docstring. **Shells** on `d3_222(p)` over the resolved target positions, fixed now, not tuned:
**(0, 10], (10, 20], (20, 30], (30, 45], (45, inf)**. Print the position count in each shell per view (targets from
D15's k_R differences, full frame: 23, 98, 126; report the other two). Two variants per shell and view:
- **REMOVE-ONE-SHELL (necessity):** delete all positions in shell `s`; keep everything else.
- **KEEP-ONLY-SHELL (sufficiency):** retain only positions in shell `s`.
Rows at unresolved positions are dropped from every variant and counted, never imputed (as D15).

**Matched controls (per variant, per view; `N_DRAW = 200`, smoke at 20, `SEED=0`):** REMOVE-ONE-SHELL is matched by deleting
`k_s` random positions from the resolved universe; KEEP-ONLY-SHELL is matched by retaining a random subset of `k_s`
positions. For each variant report A222V's rho, the gradient (n = 67, background-level bootstrap CI for the S1 value,
10,000 draws, `SEED=0`), and `p_spec` (n = 78) with the nulls at or below A222V, each beside its matched range and flag
(rule 11).

**Gate D20-G1 (HARD):** deleting zero positions reproduces the R = 0 baseline exactly, and (as a cross-check of the
machinery) REMOVE-ONE-SHELL applied to the union of shells (0,10] and (10,20] and (20,30] reproduces D15's S1 R = 30
statistics exactly (A222V rho -0.027360127, gradient +0.400678440 full).

**Summary table (printed at the end):** per view, per shell, REMOVE effect on the gradient and on A222V's rho, KEEP-ONLY
retained fraction of the R = 0 gradient and rho, each with its matched flag. State which shell's removal is most
damaging and which shell alone best preserves the signal; say plainly if the answer differs between the two views.

**Limit to state:** shells differ in size, so effects are compared with their own size-matched control, never across shells;
the 30-45 and >45 shells are large, and KEEP-ONLY of a small shell (for example (0,10], about 23 positions) leaves few rows
per background and a noisy rho_b.

---

## Task D21 - Equal-k ordering test: sequence, 3D, or random?

**Why:** Diagnostics III compared removal of 100 sequence-nearest positions with removal of 247 3D-nearest positions
and concluded the statistic "tracks 3D distance." Unequal counts cannot support that.

Pre-register in the docstring. Universe = the **resolved** positions (595 full / 418 H). For each view, for
`k` in {`k_seq(25)`, `k_seq(50)`, `k_R(20)`, `k_R(30)`} (targets, full frame, **if the sequence windows are taken on the
resolved universe: 50, 100, 121, 247**; H: compute; **confirm these counts and the universe by reading script 144**,
because D15 reported "495 positions retained" for the Rs = 50 window, which equals 595 - 100 and not 654 - 100):
- **SEQ-k:** delete the k positions with the smallest |p - 222| (ties by ascending position).
- **3D-k:** delete the k resolved positions with the smallest `d3_222` (ties by ascending position).
- **RANDOM-k:** delete k random positions, 200 draws, `SEED=0`.
Report the overlap of SEQ-k and 3D-k (count and Jaccard), then for each set A222V's rho, the gradient (n = 67) and
`p_spec` (n = 78), with RANDOM-k's range and the rule 11 flag for both SEQ-k and 3D-k.

**Identity gates (HARD):** 3D-k at `k = k_R(20)` and `k = k_R(30)` is exactly D15's S1 R = 20 and R = 30 set, so it must reproduce
D15's S1 A222V rho and gradient exactly (0 difference). First determine, by reading script 144, whether D15's sequence
sensitivities dropped unresolved-position rows. If they did not, D15's printed sequence values are on a different row set
and are not a gate; report the difference and compute SEQ-k on the resolved universe as specified.

**State the answer as a comparison at equal k**, not across different k: at each k, is 3D-k more destructive than
SEQ-k, and is either outside the RANDOM-k range? If SEQ-k and 3D-k are both inside, the "3D not sequence" claim
is unsupported at that k and must be withdrawn.

---

## Task D22 - Corrections to the Diagnostics III log (append-only; write LAST)

Locate each old sentence with `grep -n` in `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md`
(read only; do not trust line numbers given anywhere else), quote it verbatim with its real line number, put the
recomputed fact beside it, and write the corrected statement from computed variables (no hand-typed numbers). Each
ends with "Cite this, not the old sentence." Write `PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md` and report its sha256.

- **K11 - "A222V's position-cluster CI includes zero in all twelve restricted variants."** Search strings:
  `INCLUDES ZERO IN ALL TWELVE`, `Twelve out of twelve`, `whatever signal is there`. Restate per D18: if D15's routine failed
  D18.3 or D18.1, the twelve CIs are withdrawn and replaced by D18.5's; if it passed, say why the R = 0 width differs from
  Phase 1's and what that means. In either case report whether each corrected CI excludes zero.
- **K12 - "The gradient does NOT survive R = 20 A"** and "YES at R = 10, NO at R = 20 and R = 30." Search strings:
  `does NOT survive R = 20`, `NO at R = 20`. Restate with D15's own values: R = 20 gradient 0.662097 against a
  2.5th-percentile bound of 0.663147 (shortfall 0.001; loss from R = 0 of 0.036); H 0.640347 against 0.642047. Apply rule 11
  and label it MARGINAL if it meets it. R = 30 is the collapse.
- **K13 - "much more destructive per position."** Search string: `much more destructive per position`. The D15 SUMMARY states
  the opposite ("far less destructive"), and the numbers agree with the SUMMARY: the Rs = 50 window removes 100 positions
  (595 resolved minus 495 retained) and lowers the gradient by 0.0175 (1.75e-4 per position), against 0.2978 over 247
  positions (12.06e-4 per position) for 3D R = 30. Confirm the 100 from script 144 and correct any per-position figure that
  used a different k. Then state what D21 adds.
- **K14 - axis conflation.** Search strings: `first measurement in this project that separates`, `the two effects are separable`,
  `Cannot be separated`, `resolves that separation against the long-range reading`. D15 varies the **target variants**'
  distance; it does not vary the **background's** location, so it cannot separate "tied to the residue" from "tied to the
  spatial neighbourhood of the residue" (the log's own K8 says the two axes differ). Restate: what D15 and D20 show about where
  the signal lives among target variants, and that position 222 versus its neighbourhood remains undetermined by this
  design. Also note the SUMMARY section 5 opens "cannot be separated" and then says "the two effects are separable."
- **K15 - "six independent constructions" / "fifth independent construction."** Search strings: `independent construction`,
  `six independent`. All 18 Arm S backgrounds share `d3_CA = 0` and `dist_seq = 0`, so every distance term adds the same constant to
  every same-site member and A222V; the ordering within the site can change only through the shift coefficient. List the
  shift coefficient in each construction (raw 0, M1 -0.726, M2 -0.363, M3 -0.418, M4 -0.324) and A222V's shift rank among
  Arm S, and state that "2/19" is one comparison stable to shift adjustment, not six confirmations. Give the plain
  probability that a random member of 19 exchangeable values ranks 2nd or better: 2/19 = 0.105.
- **K16 - "A222V's own negative association is roughly halved by removing target variants within 30 A."** Search strings:
  `roughly halved`, `is halved`. Restate per D19: attributable or not, with the matched range.

---

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order:
1. **READ THIS FIRST - D18.** Did D15's bootstrap reproduce Phase 1's CI? What, if anything, was wrong? The twelve corrected CIs
   with the old ones beside them, and whether each excludes zero.
2. **D19.** A222V's rho and `p_spec` at R = 10, 20, 30 against their matched-deletion ranges, both views, with flags.
3. **D20.** The shell table: which shell's removal is most damaging, which shell alone best preserves the signal, each against its
   size-matched range; whether the views agree.
4. **D21.** Equal-k comparison of SEQ-k, 3D-k and RANDOM-k at each k, both views; the answer to "3D, not sequence?".
5. **D22.** Corrections K11-K16 as a table: old text, real line numbers, recomputed fact, corrected statement; sha256 of the
   corrections file.
6. **Plain two-sided statement**: where the signal lives (by shell), whether the anchor persists among distal variants,
   and what this design can and cannot say about position 222 versus its neighbourhood. Word it with the same directness
   whichever way it falls, and state which new data (backgrounds placed in the neighbourhood of 222) would settle what cached
   data cannot.
7. Every gate, PASS/FAIL, value, D18-G1 first.
8. Confirmation that no protected file, earlier log, earlier script, or shared library was edited; nothing was committed;
   no torch/esm/thermompnn import occurred.
9. The single most important entry to read first, with its line number.

---

## What this session is NOT

- Not a revision of the frozen `PHASE2_PREREG.md` verdict or a new decision rule.
- Not new scoring. The design fix for position 222 versus its neighbourhood (scoring new backgrounds placed in space
  around 222) needs a new pre-registration and is a separate step.
- Not the write-up. That should follow this session and cite the corrections files rather than the superseded
  sentences in the Diagnostics II and III logs.
