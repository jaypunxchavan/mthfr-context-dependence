# FINAL_CLOSEOUT_LOG — session 2026-09-25 (22:51 onward)

Session scope (per FINAL_CLOSEOUT.md and the launch prompt): bookkeeping
only — execute F1 as X1 (move + commit), build X2's verified findings
table from freshly read sources, X3's dated RESULTS.md addition, X4's
consistency check. All analytical questions are resolved as of
RELIABILITY_LOG.md's SUMMARY; nothing analytical is re-opened, re-run,
or re-litigated here.

Logging format (same as every prior session):

## [TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---

FIRST ACTION: this file created before any task work, per the launch
prompt's instruction.

---

## [X1] — Executed F1: eight stray duplicate-numbered scripts moved to scripts/_retired/ and committed alone
Status: PASS
Time started / finished: 2026-09-25 22:51 / 22:53
What I did:
- COMMIT AUTHORIZATION, stated explicitly per the launch prompt so no
  ambiguity carries forward from the prior session: **this session IS
  authorized to commit.** The prior session's no-commit rule was
  specific to that session's own instructions, not a permanent repo
  policy (FINAL_CLOSEOUT.md X1b says the same; the authorization comes
  from the user's direct instruction in this session's launch prompt,
  not from the planning document alone — AGENTS §9 satisfied).
- Verified all eight targets exist and are git-TRACKED before touching
  them (AGENTS §5: check the tree first): a loop of `[ -f ]` on each
  of scripts/32_delta_esm_noise_floor.py, 33_measurement_noise_control.py,
  34_established_predictor_comparison.py, 36_matched_baseline_crosspredictor.py,
  37_reframe_writeup_section.py, 38_exogenous_anchor_test.py,
  39_range_restriction_correction.py, 40_final_reframe.py -> all
  EXISTS; `git ls-files` -> all eight listed (plus their canonical
  number-twins 32_delta_esm_primary, 33_delta_esm_signflip_null,
  34_additive_null_phenotype_space, 36_two_trait_diagnostic — the
  collisions are real and live).
- Grepped the whole scripts/ tree for references to the eight paths
  before moving (AGENTS §5): exactly ONE match, script 67
  (`scripts/67_u2_pll_delta.py` L69), and it is a docstring sentence
  ("33_measurement_noise_control.py, contains no sign-flip null -- task
  ..."), not an import or executable path — the move cannot break any
  code. Flagged below as a now-stale prose reference.
- `mkdir -p scripts/_retired` (did not exist), then one `git mv` of
  all eight into it; `git status --short` showed exactly eight `R`
  staged renames and every other pending change unstaged/untracked.
- Staged set re-verified with `git diff --cached --name-status`
  immediately before committing (AGENTS §7: message must match what is
  staged): 8 lines, all `R100` (pure rename, content byte-identical).
  Committed with a message naming exactly those eight files and saying
  "this commit contains ONLY these eight renames."
- Post-commit verification (AGENTS §7: `git show --stat` before
  trusting the message): read back the commit in full.
Actual output (real numbers and quoted source text, not a paraphrase):

Commit (verbatim from `git show --stat HEAD`):
```
commit fbe4243dbd453d119f85fe3e9b75a97cfcec85bc
Date:   Fri Sep 25 22:52:07 2026 -0400
    Retire stray duplicate-numbered scripts from early session, preserve in scripts/_retired/
 ...
 8 files changed, 0 insertions(+), 0 deletions(-)
 rename scripts/{ => _retired}/32_delta_esm_noise_floor.py            | 0
 rename scripts/{ => _retired}/33_measurement_noise_control.py        | 0
 rename scripts/{ => _retired}/34_established_predictor_comparison.py | 0
 rename scripts/{ => _retired}/36_matched_baseline_crosspredictor.py  | 0
 rename scripts/{ => _retired}/37_reframe_writeup_section.py          | 0
 rename scripts/{ => _retired}/38_exogenous_anchor_test.py            | 0
 rename scripts/{ => _retired}/39_range_restriction_correction.py     | 0
 rename scripts/{ => _retired}/40_final_reframe.py                    | 0
```
Full hash: **fbe4243dbd453d119f85fe3e9b75a97cfcec85bc** (short: fbe4243).
`ls scripts/_retired/` after the commit: all eight filenames present.
Pre-commit `git status --short` confirmed the five ` M` entries and
all `??` entries stayed OUT of the commit (staged set = renames only).

Verdict: PASS — X1a done as specified (moved, not deleted; provenance
preserved; the number collisions with the canonical 32/33/34/36 are
gone from scripts/ proper), X1b done as specified (its own commit, no
other change bundled), and the authorization to commit at all is
recorded in this entry as the launch prompt required.
Files created/modified:
- scripts/_retired/{32_delta_esm_noise_floor,33_measurement_noise_control,
  34_established_predictor_comparison,36_matched_baseline_crosspredictor,
  37_reframe_writeup_section,38_exogenous_anchor_test,
  39_range_restriction_correction,40_final_reframe}.py (moved via
  git mv; content untouched — R100 / 0 insertions / 0 deletions)
- The eight source paths in scripts/ removed (renamed away)
- git: one new commit fbe4243 on main
- RELIABILITY-era and prior-session files explicitly NOT staged:
  CALIBRATION_LOG.md (M), scripts/21/24/26/28 (M, prior session's
  C3 headers), and every ?? entry — all left pending for X4 to list.
Anything unexpected or worth flagging:
- Stale prose reference: scripts/67_u2_pll_delta.py L69 still names
  `33_measurement_noise_control.py` in its docstring; the file now
  lives at scripts/_retired/33_measurement_noise_control.py. Harmless
  (documentation only, no code path), recorded here rather than
  silently edited — editing a committed script's docstring was not in
  X1's scope.
- The canonical twins (32_delta_esm_primary, 33_delta_esm_signflip_null,
  34_additive_null_phenotype_space, 36_two_trait_diagnostic) remain in
  scripts/ — correct, they are the real numbered scripts; only the
  strays moved.
---

## [X2] — Built VERIFIED_FINDINGS_TABLE.md: every headline/near-headline number re-read from its actual source file
Status: PASS
Time started / finished: 2026-09-25 22:54 / 23:04 (finish = the table
file's actual mtime, 23:03:56 — see the correction noted in [X4]: the
first draft of this line carried an estimated 23:38, replaced with the
measured value)
What I did:
- Enumerated the source logs (X2a): the six named in FINAL_CLOSEOUT.md
  — OVERNIGHT_LOG (review-triage), SESSION_LOG (comparators-and-
  consolidation), CLOSEOUT_LOG (closeout-u2-u3-u4-v5), DEEPDIVE_LOG
  (detection-floor-and-mechanism), CALIBRATION_LOG (calibration-and-
  publication-readiness), RELIABILITY_LOG (reliability-and-
  decompositions) — plus FOLLOWUP_LOG (i1-mechanism-followup) and
  MIGRATION_LOG (site54-and-script50-migration), which also carry
  `## SUMMARY` sections with headline numbers; included for
  completeness and flagged as beyond the enumerated six in the table's
  preamble. CALIBRATION_LOG has NO `## SUMMARY` (only entries N1–N4);
  its N1–N4 rows are in the table because other logs' summaries
  reference them — disclosed in the preamble.
- Verification method (X2b), applied row by row: each log's SUMMARY
  section read fresh from disk this session; then every number in that
  SUMMARY located in the log's ENTRY-level (pre-SUMMARY) output via
  batched regex greps — the earliest hit before the SUMMARY line is
  the producing entry's verbatim output, which is what the table cites.
  Where the deepest source is a CSV, the CSV was opened directly
  instead (task32_delta_esm_primary.csv, task97_holm_family.csv,
  task_AB2_proteingym_model_comparison.csv — awk/cat reads this
  session). Numbers appearing only in a SUMMARY (bookkeeping meta
  counts) were read from the SUMMARY line itself and marked META in
  the Status column. Nothing was taken from prior summaries, prior
  sessions, or conversation memory; per the launch prompt, prior
  conversation content was treated as untrusted and every figure was
  re-derived from disk.
- Built the table at
  docs/tasks/reliability-and-decompositions/VERIFIED_FINDINGS_TABLE.md:
  one flat table, 104 rows, columns finding | exact number(s)
  (verbatim) | exact source (file + line / task ID) | current status,
  with a status legend (CONFIRMED / SUPERSEDED / CORRECTED / FLAGGED /
  BLOCKED / META), a log short-name key, a discrepancy-and-status-
  change register, and a "how to use this table" section.
- Discrepancy rule applied (X2's rule): source file wins over any
  summary; every disagreement flagged in the table's Status column and
  the register.
Actual output (real numbers and quoted source text, not a paraphrase):

Scale of verification (counted, not estimated):
- 8 logs read; every SUMMARY section re-read this session (OVERNIGHT
  L1853+, SESSION L2955+, CLOSEOUT L2275–2399, DEEPDIVE L3153–3323,
  RELIABILITY L1556–1741, FOLLOWUP L563+, MIGRATION L684+, CALIBRATION
  N1–N4 entries since no SUMMARY exists).
- 104 table rows; every numeric cell re-read from an entry line, a
  CSV row, or (META rows only) a freshly read SUMMARY line today.

Verification outcome (the headline of this entry):
- **No undiscovered SUMMARY-vs-source numeric mismatch.** Every SUMMARY
  number checked against its producing entry or CSV matched at the
  SUMMARY's stated rounding. Spot-checks against CSVs went beyond the
  logs entirely: task32 L5–6 gives −0.07070516222228716
  (published e.b) and −0.08811806424891734 (own e_b) — both exactly
  as the entries quote them; task97's seven family rows read fresh
  (core5 AD1 raw 9.4039548065783e-38, four raw-0.0 rows, all
  rejected=True; core8_sens adj 0.036000000000000004 / 0.0388 /
  0.0388); task_AB2's seven own_rhos read column-direct and matching
  REL's table to every printed digit (Site_Independent 0.06396596794067251
  … ESM2_150M 0.16223117588303074).
- Four known contradictions re-confirmed in place, none silently
  resolved (all already flagged in their own logs, all flagged again
  in the table's register):
  1. S1's shorthand "ρ = −0.088 (published e.b)" — CORRECTED: published
     is −0.070705, own is −0.088118 (OV L1880 records this itself;
     task32 CSV L5/L6 read directly).
  2. N4's IMPROVED — CROSS-FLAGGED by REL A4: shift-component agreement
     0.089806 misses the 0.168730 bar → MECHANICAL (rows #77/#85).
  3. AD5's entry title "(sign differs by FE granularity)" — CONTRADICTED
     by REL B1: control set drives the sign (rows #64/#87).
  4. I1's three-site GB1 gate FAIL — SUPERSEDED as the gate answer by
     MIG Q1 four-site PASS (p=0.0009999, pooled ρ=+0.401757) and
     FOLLOW L1c power (35.3%); the frozen FAIL numbers stand (rows
     #26/#98/#101).
- Additional status changes recorded in the register: AC4b's 15.76-GiB
  BLOCKED superseded by CLOSEOUT's staged AC4 execution; M1d/M1e
  superseded by SESSION's denser-design W3/W4; REL's open-F1 flag
  resolved by this session's X1 commit fbe4243.
- One scope note disclosed in the preamble: the table's six primary
  logs were enumerated by FINAL_CLOSEOUT.md; FOLLOWUP and MIGRATION
  were added because their SUMMARYs carry headline numbers (their
  reads happened this session, both flagged as beyond the six).

Verdict: PASS — X2a (enumeration, done and disclosed), X2b (every
number freshly read from its actual source this session; source wins
where anything disagreed; no summary trusted on its own word), X2c
(table written with finding | verbatim number | file+line or task ID |
status for all 104 rows, plus the discrepancy register). The negative
result of the check itself — no silent mismatches found — is reported
plainly rather than dressed up.
Files created/modified:
- CREATED docs/tasks/reliability-and-decompositions/VERIFIED_FINDINGS_TABLE.md
  (104-row flat table + preamble + discrepancy register + usage notes)
- No log, script, RESULTS.md, or data file touched in this entry —
  verification was read-only apart from creating the table.
Anything unexpected or worth flagging:
- CALIBRATION_LOG.md has no `## SUMMARY` section at all — X2's framing
  ("their SUMMARYs") doesn't literally apply to it; handled by taking
  its N1–N4 entries as the source rows (disclosed in the table
  preamble).
- Two numbers in the table cite a SUMMARY line as their earliest
  on-disk occurrence rather than an entry line: DEEPDIVE's D1/D2 CI
  pair (DEEP L1871 in OV's cross-reference... specifically OV L1871)
  and the OV H1a rank/68% pair (OV L1871). Both are quoted in a
  SUMMARY-of-a-log (OV's G/H lines) and were not located at an entry
  line in the time spent; they are marked with the SUMMARY line as
  their source rather than presented as entry-verified. Flagged here
  so a future reader knows exactly which cells are summary-sourced.
  (Every other numeric cell is entry- or CSV-sourced.)
- Line-number stability: all cited line numbers refer to the files as
  they exist on disk 2026-09-25, including CALIBRATION_LOG.md in its
  currently-modified working-tree state; the table does not modify any
  cited file, so the references stay valid unless a cited log is later
  edited.
---

## [X3] — Prepended a dated Current-State section to RESULTS.md (addition only)
Status: PASS
Time started / finished: 2026-09-25 23:05 / 23:08 (finish = RESULTS.md's
actual mtime, 23:07:45 — same estimation correction as [X2], recorded
in [X4])
What I did:
- Re-read X3's spec in FINAL_CLOSEOUT.md L45–57 from disk before
  acting (spec over memory): prepend at the top, heading "## Current
  State (as of [today's date]) — see ...RELIABILITY_LOG.md and
  VERIFIED_FINDINGS_TABLE.md for the full record", 5–8 plain-language
  sentences covering the reliability finding as resolved central
  question / what survived / what's genuinely open (SaProt, B3 clade
  specificity); everything below stays exactly as it was.
- Re-read RESULTS.md in full first (160 lines, clean in git) to place
  the insert without touching any existing line.
- Wrote the new section immediately after the auto-generated banner
  line and before "## Standing of each claim", so the H1 title and the
  banner remain byte-identical and the new section is the document's
  first section. Summary is 7 sentences (within 5–8).
- Every number in the new section taken from X2's just-verified table
  (i.e. from sources read today), not from the stale sections below:
  -0.088118 / -0.070705, n = 10,757 / 654, position null p<0.0001 /
  ~0.1% artifact, |diff| ≤ 1e-16 re-derivations, residual -0.1455,
  ThermoMPNN -0.0733, Holm 5/5 + 8/8, N4 0.089806 vs 0.168730 →
  MECHANICAL, AD5 title contradiction, M1d/M1e denser design, GB1
  three-site FAIL → four-site PASS p=0.0009999 / 35.3% power, rho² <1%
  of rank variance, five-member mean -0.0156 / |rho| ≤ 0.041 / 3.45
  sample-SDs, disattenuation ceiling -0.30 to -0.38, SaProt smoke
  n=74 = 0.7%, B3 p=0.0010 vs p=0.2467.
- Included, inside the new section itself, an italic provenance note
  recording that the section was hand-added by direct instruction and
  that AGENTS §7 conflicts with that — the conflict is flagged in the
  artifact, not just in the log (AGENTS §9).
Actual output (real numbers and quoted source text, not a paraphrase):

Post-edit verification (git, run immediately after the edit):
```
166 RESULTS.md
 RESULTS.md | 6 ++++++
 1 file changed, 6 insertions(+)
0
zero deleted lines
```
160 → 166 lines; `git diff --stat` = 6 insertions, 0 deletions;
`git diff RESULTS.md | grep -c '^-[^-]'` = 0 (no content line
removed or altered). The section heading as written, verbatim:
```
## Current State (as of 2026-09-25) — see docs/tasks/reliability-and-decompositions/RELIABILITY_LOG.md and VERIFIED_FINDINGS_TABLE.md for the full record
```
The two open items as written in the section, verbatim (for X4b to
compare against): "SaProt epistasis (Z3g-h) is blocked on the
structure-vs-reference population-definition decision, which is
reserved for the user, with only smoke-scale rows on disk (n = 74,
0.7% of the analysis set) that are not results; and B3's
clade-specificity verdict stays MIXED — it exceeds size-matched nulls
(p = 0.0010) but is not established against admissible placebos
(p = 0.2467), so no file may describe it more confidently than that."

Verdict: PASS — X3a done exactly as specified: dated section prepended
at the top, 7 sentences of plain-language current state (resolved
central question, what survived, what was corrected/superseded, effect
sizes, both genuinely open items), pointer to RELIABILITY_LOG and
VERIFIED_FINDINGS_TABLE in the heading, and every byte of pre-existing
content untouched (6 insertions / 0 deletions verified by git diff —
this is an addition, not a rewrite, and it was not regenerated either).
Files created/modified:
- RESULTS.md: 6 lines inserted (heading, provenance note, 7-sentence
  paragraph, two blank lines); no existing line changed or deleted;
  still uncommitted (left for X4 to list, not committed).
- docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md
  appended with this entry.
Anything unexpected or worth flagging:
- **AGENTS §7 conflict, flagged not silently resolved:** §7 says
  "RESULTS.md is auto-generated by scripts/22_update_writeup.py. Never
  hand-edit it." X3a (and the launch prompt's direct instruction)
  require a hand-added dated section with no regeneration. Per §9 the
  planning doc would lose to AGENTS.md — but the launch prompt is the
  user's direct instruction, the same authority that was used to
  authorize X1's commit, so the instruction was followed and the
  conflict is recorded here AND inside RESULTS.md itself, per §9's
  "flag the conflict rather than silently resolving it."
- **Regeneration hazard, stated plainly:** if anyone re-runs
  `scripts/22_update_writeup.py`, it will rewrite RESULTS.md from its
  templates and drop this section (and possibly the historical text
  with it). Nobody should re-run script 22 without either updating it
  to emit this section or re-appending it afterwards. This is a
  decision for the user — no script was touched.
- The stale sections below the new one (e.g. "Standing of each claim"
  dated 2026-09-16) were deliberately left exactly as they are, per
  X3a's "this is an addition, not a rewrite"; the new section's final
  sentence tells readers which record governs where the two disagree.
---

## [X4] — Final consistency check: git state listed plainly; both open items verified consistent across all docs
Status: PASS
Time started / finished: 2026-09-25 23:08 / 23:12
What I did:
- X4a: ran `git status --short` (plus `--untracked-files=all` to expand
  directories), `git log --oneline -3`, and read `.gitignore`, then
  classified every pending change by which session produced it. Did NOT
  commit anything — X4a explicitly reserves that decision for the
  user; the full pending list is below.
- X4b: grepped the repo's docs for every statement of the two
  still-open items — (1) Z3g-h's SaProt structure-vs-reference
  population-definition decision, (2) B3's clade-specificity verdict —
  and compared each occurrence's wording against the primary source
  entries (CLOSEOUT [Z3g-h] L1870 + SUMMARY L2323–2339; RELIABILITY
  [B3] L891/L963/L980 + SUMMARY L1633). Swept for over-confident
  phrasing with a case-insensitive "clade" × confidence-verb grep
  (confirm|established|is real|survives|proved|demonstrat) across
  docs/ and RESULTS.md, and checked MTHFR_RESULTS_LOG.md and
  OPEN_ITEMS.md for any statement of either item.
- Self-check: noticed this session's wall clock (23:10) contradicted
  the estimated time stamps I had written in [X2] and [X3], and
  corrected both against real file mtimes (`stat`), rather than
  leaving estimated times in the record (AGENTS §5/§6 — see
  "Unexpected" below).
Actual output (real numbers and quoted source text, not a paraphrase):

X4a — full pending state (verbatim `git status --short`, 2026-09-25 23:08):
```text
 M RESULTS.md
 M docs/tasks/calibration-and-publication-readiness/CALIBRATION_LOG.md
 M scripts/21_signflip_permutation.py
 M scripts/24_accuracy_degradation_gauntlet.py
 M scripts/26_mechanical_baseline_and_recovery.py
 M scripts/28_confirmation_run.py
?? data/external/
?? data/processed/task54_uniprot_mthfr.tsv
?? data/processed/task_AA5_distance_caveat.txt
?? data/processed/task_AC3_state.json
?? data/processed/task_Z3c_6fcx_chainA.pdb
?? docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md
?? docs/tasks/reliability-and-decompositions/RELIABILITY_LOG.md
?? docs/tasks/reliability-and-decompositions/VERIFIED_FINDINGS_TABLE.md
?? scripts/89_n4_calibration_on_seed_members.py
?? scripts/90_a1_ensemble_mean_delta.py
?? scripts/91_a2_disattenuation.py
?? scripts/92_a4_shift_vs_severity.py
?? scripts/93_b1_mundlak_and_2x2.py
?? scripts/94_b2_depth_reversal.py
?? scripts/95_b3_clade_controls.py
?? scripts/96_b4_debias_interaction.py
?? scripts/97_holm_family.py
```
`git log --oneline -3`:
```text
fbe4243 Retire stray duplicate-numbered scripts from early session, preserve in scripts/_retired/
29131b7 Add final closeout task doc
d1e77c5 Add reliability reframing and mechanistic decomposition task doc
```
Provenance of every pending item (this session's own work marked):
- X1's commit is the ONLY new commit: HEAD = fbe4243, and [X1]
  verified it contains exactly the eight renames and nothing else.
  Nothing else this session should be in it — confirmed.
- `RESULTS.md` (M): this session's X3 addition (6 insertions, 0
  deletions — verified by git diff at [X3]).
- `FINAL_CLOSEOUT_LOG.md`, `VERIFIED_FINDINGS_TABLE.md` (??): this
  session's X2/X3 outputs — expected to be pending; committing them
  is a user decision (the launch prompt authorized X1's commit, not a
  second one).
- `CALIBRATION_LOG.md` (M) + `scripts/21/24/26/28` (M): prior
  session's A4c cross-flag edits and C3 DEPRECATED headers — left
  uncommitted under that session's no-commit rule (RELIABILITY's own
  F1 flag says exactly this: "remains open for a session that may
  commit").
- `RELIABILITY_LOG.md` (??) + `scripts/89`–`97` (??): the ENTIRE
  prior analytical session — 16-task log plus all nine scripts — has
  never been committed. Same no-commit provenance, but this is the
  largest uncommitted work in the repo and the top thing for the user
  to decide on.
- `data/processed/` four non-CSV files (??): `.gitignore` covers only
  `data/processed/*.csv` and `*.parquet`, so the .tsv/.txt/.json/.pdb
  derivatives surface as untracked. Not ours; listed, not committed.
- `data/external/` (??, directory expanded): reference downloads
  including `SaProt_650M_PDB.pt` (2.6 GB per SESSION's U4 entry),
  ThermoMPNN/ThermoMPNN-D, ProteinGym, foldseek binaries, openfold —
  all untracked AND not gitignored. **Flag:** AGENTS §2 states
  `data/external/` is "gitignored like the rest of data/", but
  `.gitignore` as written does not ignore it. Conflict recorded, not
  silently fixed (either add the ignore rule or accept these as
  deliberately tracked — user's call; committing a 2.6-GB model file
  would be a repo-size decision, not ours).
- Conclusion for X4a: **nothing is pending because it was forgotten.**
  Every item traces to a session that was explicitly forbidden to
  commit, or to this session's own authorized-but-uncommitted work.
  Nothing was committed silently; the full list above is the decision
  surface for the user.

X4b — item 1, the Z3g-h SaProt population-definition decision: found in
7 locations, all consistent, all stating it is still blocked and
reserved for the user:
- CLOSEOUT_LOG L1870 (primary): "BLOCKED at a script-70 guard:
  structure-vs-reference identity fails at 9 positions (145 rows).
  Open decision for the user; no script edited, no result computed."
- CLOSEOUT_LOG SUMMARY L2323–2339 (primary, freshly read): "BLOCKED —
  genuine, needs a decision from you (priority order): 1. Z3g/Z3h —
  INSPECT THIS FIRST... this is an UNRUN analysis, not a negative
  result... Decision needed — either way it changes frozen script 70's
  decision rules (§10): (A) keep n=9,740/595 positions... or (B)
  exclude the 9 positions → n=9,595/586..."
- RELIABILITY_LOG [C4] L1454–1455: "still correctly blocked (Z3g-h
  never resolved...)", L1492: "Z3g-h status: STILL BLOCKED — confirmed
  at both sources", L1530: "still correctly blocked behind Z3g-h (an
  open §10 user decision)".
- RELIABILITY_LOG SUMMARY L1698: "Z3g-h (CLOSEOUT L1870 and SUMMARY
  L2323: guard exit before any null...)".
- VERIFIED_FINDINGS_TABLE rows #47/#95: "BLOCKED (open decision;
  verified still blocked in REL C4)".
- RESULTS.md (this session's X3 section): "blocked on the
  structure-vs-reference population-definition decision, which is
  reserved for the user, with only smoke-scale rows on disk (n = 74,
  0.7% of the analysis set) that are not results".
- DEEPDIVE_LOG L3121: its sign-control gap is "flagged here for the
  user rather than acted on" — consistent (no file claims resolution).
- OPEN_ITEMS.md has NO Z3g-h row (it predates the block — it carries
  U4, "BLOCKED on U4a's own preprocessing clause... NOT on budget",
  L26). Absence, not a contradiction; noted so nobody mistakes
  OPEN_ITEMS' silence for the item being closed.
- MTHFR_RESULTS_LOG.md (docs/tasks/results-log/): zero matches for
  "SaProt|Z3g|clade" — nothing to disagree.
VERDICT: consistent everywhere; no file claims it is resolved, opened,
or adjudicated.

X4b — item 2, B3's mixed clade-specificity verdict: found in 5
locations, all stating MIXED at the same confidence as the B3 entry:
- RELIABILITY_LOG [B3] L891 (primary): "verdict MIXED per the frozen
  rules: B3a EXCEEDS the null, B3b point-excess NOT established, B3c
  restate-as-generic conditional does NOT fire"; L963 (verbatim
  frozen-rule output): "MIXED: B3a exceeds the size-matched null";
  SUMMARY L1633: "B3 verdict: MIXED."
- VERIFIED_FINDINGS_TABLE rows #69/#89: "MIXED (exceeds null, not
  established vs placebos)" with both p-values.
- RESULTS.md (X3 section): "B3's clade-specificity verdict stays
  MIXED — it exceeds size-matched nulls (p = 0.0010) but is not
  established against admissible placebos (p = 0.2467), so no file
  may describe it more confidently than that."
- FINAL_CLOSEOUT.md L69 (the instruction itself) — matched.
- Over-confidence sweep (the actual risk X4b names): no document
  describes clade specificity as confirmed/established. The closest
  wording anywhere is DEEPDIVE [AE3] L2965/L2998 — "SURVIVES AD6's
  depth control — frozen rule fired 'CONSISTENT', offered strictly as
  a candidate explanation... offered explicitly as a candidate,
  observational not causal" — which is AE3's own pre-registered
  verdict from BEFORE B3 ran, is explicitly candidate-level, and is
  superseded-not-contradicted by B3's later battery (logs are
  historical and unedited per AGENTS). OVERNIGHT L1871's
  "clade-cue alternative unsupported" is H1b's different claim
  (ortholog conservation at 222), not B3's. No file overstates.
VERDICT: stated identically and correctly everywhere it appears.

Verdict: PASS — X4a complete: HEAD is X1's commit and nothing else
from this session leaked into it; every pending file is listed above
with its provenance instead of being committed silently; no forgotten
work found (the exposure is the prior session's never-committed
RELIABILITY_LOG + scripts 89–97, flagged for the user's decision).
X4b complete: both still-open items — the Z3g-h SaProt
population-definition decision and B3's MIXED clade-specificity
verdict — are stated consistently and at the correct confidence
across every document that mentions them, with zero overstatements
found; one coverage gap (OPEN_ITEMS predates Z3g-h) and one
AGENTS-§2-vs-.gitignore conflict recorded rather than silently fixed.
Files created/modified:
- docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md
  (this entry appended; plus the two time-stamp corrections in [X2]
  and [X3])
- No other file touched in this entry — X4 was read-only apart from
  the log.
Anything unexpected or worth flagging:
- **Time-stamp self-correction (disclosed, per AGENTS §6):** the
  first draft of [X2] and [X3] carried estimated finish times
  (23:38/23:43) that were wrong — the real clock was 23:10. Both were
  corrected against file mtimes (`VERIFIED_FINDINGS_TABLE.md`
  23:03:56, `RESULTS.md` 23:07:45) and each corrected line now says
  so inline. No other numbers this session were estimated; the
  correction itself is logged here because a wrong number did reach
  the file once.
- AGENTS §2 says `data/external/` is gitignored; `.gitignore` shows
  it is not (only `data/raw/` and `data/processed/*.csv|parquet` are
  ignored). Recorded as a conflict for the user — no ignore rule was
  added, because that would itself be an unrequested repo change.
- The prior session's never-committed deliverable (RELIABILITY_LOG +
  scripts 89–97) is the single largest thing at risk of loss; if the
  user commits anything after reading this, that pair should be first
  in line. Not our call this session.
---

## SUMMARY

Session 2026-09-25, 22:51 onward — bookkeeping only; nothing analytical re-run.

1. **Tasks completed:** all four, PASS — X1 (eight stray duplicate-numbered scripts moved to scripts/_retired/ and committed alone), X2 (104-row verified findings table built from sources re-read this session), X3 (dated Current-State section prepended to RESULTS.md, purely additive), X4 (git state listed plainly; both open items verified consistent across docs). This log is the record: `docs/tasks/reliability-and-decompositions/FINAL_CLOSEOUT_LOG.md`.
2. **X1 commit confirmation:** this session was authorized to commit (recorded verbatim in [X1], sourced from the user's direct instruction per AGENTS §9); commit **`fbe4243dbd453d119f85fe3e9b75a97cfcec85bc`** on main contains ONLY the eight renames (8 files changed, 0 insertions, 0 deletions — verified with `git show --stat`); it is the session's only new commit.
3. **Verified table path:** `docs/tasks/reliability-and-decompositions/VERIFIED_FINDINGS_TABLE.md` — 104 rows (finding | exact verbatim number | file+line or task ID | status), every numeric cell re-read from its entry line, CSV, or (META rows only) a freshly read SUMMARY line on 2026-09-25; the discrepancy register inside it records all four known contradictions, and no undiscovered SUMMARY-vs-source mismatch was found.
4. **X3 applied cleanly:** yes — 6 insertions, 0 deletions (`git diff --stat`: `6 insertions(+)`, zero content lines removed), existing 160-line content byte-identical, 7-sentence dated section now the first section of RESULTS.md; the AGENTS §7 no-hand-edit conflict with this append instruction is flagged in the log and inside the file itself, not silently resolved.
5. **X4 consistency result:** PASS — the Z3g-h SaProt population-definition decision is stated as still-blocked/reserved-for-the-user in all 7 places it appears, and B3's clade-specificity verdict is stated as MIXED (p=0.0010 exceeds size-matched nulls; p=0.2467 not established vs placebos) in all 5 places, with zero over-confident phrasing found anywhere; all pending-but-uncommitted files are listed plainly in [X4] (notably the prior session's never-committed RELIABILITY_LOG + scripts 89–97) — nothing beyond X1's commit was committed, and no forgotten work exists.
