# DEEPDIVE_LOG — detection-floor-and-mechanism

Session log for `DETECTION_FLOOR_AND_MECHANISM.md`. One `## [TASK ID]`
entry per task, appended immediately after that task's real execution,
in the task doc's suggested execution order. Group AG is read-only for
this session (read, logged, nothing acted on).

Entries follow the required format:
`## [TASK ID] — title` / Status / Time / What I did / Actual output /
Verdict / Files created/modified / Anything unexpected or worth
flagging / `---`.

## [AF1] — Read the Group C–H digest in full; quote Group C verbatim
Status: PASS
Time started / finished: 2026-09-23 21:26:34 / 2026-09-23 21:26:34
What I did: Per the mandated pre-check, ran `grep -n "^##"` on
`docs/tasks/comparators-and-consolidation/GROUPS_C_TO_H_DIGEST.md`
FIRST (8 headings confirmed: Groups A, B, C, D, E, F, G1, H; Group C
heading at line 31; format `## Group X — title`). Then read the entire
file (80 lines) top to bottom. Extracted the complete Group C section
(the rank-vs-MAE reconciliation) verbatim below, per AF1a.
Actual output (verbatim — Group C section, lines 31-40 of the digest,
unmodified):
```
## Group C — Rank-vs-MAE reconciliation (full table in OVERNIGHT_LOG lines 307–395; CSV `task45_c1_table.csv`)

- **C1a** — `PASS — table built to spec (the spec's 6 row-predictors + Grantham added as a 7th because C1c needs it; all 3 targets, all 3 metrics, low/mid/high + all)`. n=`10757`, 654 positions. High stratum: `S_A222V rank +0.1713` vs matched synthetic `−0.0329` vs `w.fitness −0.0353`. Warnings: e.b-target MAE/MSE cells partly definitional (strata are |e.b| terciles — `Do not quote e.b-MAE-across-strata as a finding`); synthetic↔w.fitness rank `0.5638` true by construction.
- **C1b** — `PASS — executed; verdict = retention is NOT background-specific (the review's suspected answer, confirmed)`. `gap(S_A222V) = +0.2042 CI [+0.1333, +0.2532]`; `gap(S_WT) = +0.1919 CI [+0.1366, +0.2542]`; `gap(S_A222V) − gap(S_WT) = +0.0124 CI [−0.0375, +0.0370] p = 0.9630`. Limitation: single seed-0 noise draw.
- **C1c** — `PASS for BLOSUM62 (clean matched test, POSITIVE result); Grantham row = METHOD LIMITATION (α-matching impossible), reported as a limitation, NOT as a result`. `gap(BLOSUM62) = +0.0691 CI [+0.0142, +0.1146]`; `gap(S_A222V) − gap(BLOSUM62) CI [+0.0626, +0.1950]`; `gap(Grantham) = −0.0779` at α pinned `0.0000` (unmatched — `Do NOT quote Grantham's −0.0779 as "Grantham fails to beat its synthetic"`).
- **C1d** — `PASS — 0.999636 ≥ 0.99, exactly the threshold the task specified`. `Spearman = 0.999636 (n=10757)` → `the MAE story rests on a small number of rank swaps`.
- **C2a** — `PASS — executed; pre-registered verdict MIXED (substantial proximity contribution, but NOT "a few dozen near-222 variants account for it")`. `GATE G1: +0.000533466098810331` (|diff| `0.000e+00`); bands `≤25: 23.20% / 26–100: 43.17% / >100: 33.63%`; `top 50 = 43.56%`, `top 100 = 73.68%`; leave-one-position-out `min +0.000474 / max +0.000550`; `SECONDARY drop-zone refit = +0.000361 = 67.6% of full -> SURVIVES`.
- **C2b** — `PASS — SEED-ROBUST (the review's concern does not materialize)`. 50 seeds: `mean +0.0004980, sd 0.0000528, min +0.0003966, max +0.0006214`; `sd / CI half-width = 0.220`; `flips: 0/50`; combined sd `+9%` → negligible.
- **C2c** — `PASS — HOLD (verdict unchanged under the squared-error loss)`. `GATE G2: +0.002408919531324` (|diff| `0.000e+00`); high stratum MSE `+0.002320 CI [+0.001740, +0.002895]` (MAE `+0.00241`); all three strata same verdict both losses. Sign note: MTHFR_RESULTS_LOG `+0.00241 (WORSE)` vs REVIEW_TRIAGE `−0.00241 (loss)` — same quantity, both docs unedited.
- **C3a** — `PASS — ceiling computed and USABLE (pre-registered CI rule met); disattenuation verdict = MATERIALLY LARGER (pre-registered ratio rule met, narrowly — magnitude caveat in the verdict)`. Gates `|diff| 0.000e+00`, rebuild `2.220e-16`. Reliability `own 0.6363 / published 0.6193` (review's ~0.64 matches). Oracle POOLED `+0.0366 CI [+0.0309, +0.0424]`; ESM-2 vs ceiling pooled `+0.000308 = +0.84%`, high `−0.002409 = −4.62%`. Decomposition: measured-fitness `+0.0363` of the `+0.1385` zero-noise ceiling vs interaction `+0.0021` under primary reading (a). Disattenuation `r_dis = −0.110413 CI [−0.147534, −0.072340]`, `|r_dis|/|rho| = 1.2530` → `MATERIALLY LARGER` (threshold 1.25 — `Report as "meets the bar narrowly," not as a comfortable pass`). Oracle is circular — sizes a ceiling only, `NOT an achievable model`.
```
Verdict: PASS — AF1a discharged: digest read in full, Group C captured
verbatim. Per AF1a's own purpose (the top-line sentence about whether
ESM-2 "fails" or the finding is metric-dependent), the quoted text
itself answers it and I record only what it says, no synthesis beyond
the quote: in the high-|e.b| stratum ESM-2's rank (+0.1713) beats the
matched synthetic null (−0.0329) and w.fitness (−0.0353) by a wide
margin while the MAE verdict holds against it (C2a/C2c gap +0.00241,
HOLD under both losses), and C1d shows rank-vs-MAE agreement is
0.999636 so `the MAE story rests on a small number of rank swaps` —
i.e. the two metrics disagree in verdict, which is exactly what
"metric-dependent" means. The digest explicitly states nothing below it
is reinterpreted ("that synthesis is left to the reader").
Files created/modified: `DEEPDIVE_LOG.md` (this entry) only.
Anything unexpected or worth flagging: (1) heading format was confirmed
by the mandated grep before extraction — `## Group X — title`, no
format surprise this time; (2) carry-forward warnings inside Group C
are logged here so later groups don't misuse them: do NOT quote
e.b-MAE-across-strata as a finding (strata are |e.b| terciles — partly
definitional), do NOT quote Grantham's −0.0779 as a Grantham failure
(α-matching impossible — method limitation), synthetic↔w.fitness rank
0.5638 is true by construction; (3) the digest's Group G1 entry
references a "pipeline-validation I1 GATE FAIL (three-site run;
superseded since by the four-site rerun's PASS — see Y7)" — relevant
context for AA3 later, noted, not acted on here; (4) the digest's full
text also contains Groups A/B/D/E/F/G1/H which are now read (full-file
read) but were not required to be quoted — only Group C is.
---

## [AB1] — Does ProteinGym include this project's actual assay?
Status: PASS
Time started / finished: 2026-09-23 21:34:15 / 2026-09-23 21:34:15
What I did: Checked ProteinGym's substitution benchmark for this
project's assay (AB1a), all via network metadata + range-limited
fetches — no repo files created; all scratch in the session tmp dir
`.../T/opencode/proteingym/` (stating this file-location choice per
rule 7). (1) `assays.bib` from `OATML-Markslab/ProteinGym` (258,749 B)
grep'd for the paper. (2) Reference metadata
`reference_files/DMS_substitutions.csv` (208,734 B, 217 assays) grep'd
for MTHFR. (3) README.md baseline table (26,106 B) read. (4) Both host
zips' central directories parsed via HTTP Range requests (the monolithic
scores zip is 1,911,045,703 B > the 200MB fetch cap, so only ranges
were read: tail 128 KB + central directory; total bytes actually
fetched across this task ≈ 11 MB). (5) Extracted THIS assay's two
entries by range: the per-assay scores CSV (9,650,420 B compressed ->
29,370,765 B) and its curated MSA (600,283 B -> 3,316,659 B), then
inspected columns/rows.
Actual output (verbatim key lines):
```
grep assays.bib: 1801:@ARTICLE{weile_shifting_2021,
1802:  title    = "Shifting landscapes of human {MTHFR} missense-variant effects"
metadata row: DMS_sub_99,MTHR_HUMAN_Weile_2021,MTHR_HUMAN_Weile_2021.csv,MTHR_HUMAN,Human,Homo sapiens,...,656,FALSE,12464,12464,0,0.746,median,Weile,Shifting landscapes of human MTHFR missense-variant effects,2021,10.1016/j.ajhg.2021.05.009,1-656,MTHFR reductase,Growth,,MTHR_HUMAN_2023-08-07_b02.a2m,1,656,656,0.2,0.2,4783,0.96,630,646.2,0.99,Low,65,0.10,urn_mavedb_00000049-a-0_scores.csv,score,1,mutant,MTHR_HUMAN_theta0.2_2023-08-07_b02.npy,MTHR_HUMAN.pdb,1-656,1,,OrganismalFitness
[zero-shot scores zip] Content-Length=1911045703 entries=217
MTHR entries: 1
  MTHR_HUMAN_Weile_2021.csv method=8 csize=9650420 usize=29370765
[MSA zip] Content-Length=1504361305 entries=195; MTHR entries: 1
  DMS_msa_files/MTHR_HUMAN_2023-08-07_b02.a2m csize=600283 usize=3316659
[scores] shape = (12464, 99)
[scores] columns (99): ['mutant', 'mutated_sequence', 'DMS_score', 'DMS_score_bin', 'Site_Independent', 'EVmutation', 'DeepSequence_single', 'DeepSequence_ensemble', 'EVE_single', 'EVE_ensemble', 'Unirep', 'Unirep_evotune', 'MSA_Transformer_single', 'MSA_Transformer_ensemble', 'ESM1b', 'ESM1v_single', 'ESM1v_ensemble', 'ESM2_8M', 'ESM2_35M', 'ESM2_150M', 'ESM2_650M', 'ESM2_3B', 'ESM2_15B', 'Wavenet', 'RITA_s', 'RITA_m', 'RITA_l', 'RITA_xl', 'Progen2_small', 'Progen2_medium', 'Progen2_base', 'Progen2_large', 'Progen2_xlarge', 'GEMME', 'VESPA', 'VESPAl', 'VespaG', 'ProtGPT2', 'Tranception_S_no_retrieval', 'Tranception_M_no_retrieval', 'Tranception_L_no_retrieval', 'Tranception_S', 'Tranception_M', 'Tranception_L', 'TranceptEVE_S', 'TranceptEVE_M', 'TranceptEVE_L', 'CARP_38M', 'CARP_600K', 'CARP_640M', 'CARP_76M', 'MIF', 'MIFST', 'ESM-IF1', 'ProteinMPNN', 'ProtSSN_k10_h512', 'ProtSSN_k10_h768', 'ProtSSN_k10_h1280', 'ProtSSN_k20_h512', 'ProtSSN_k20_h768', 'ProtSSN_k20_h1280', 'ProtSSN_k30_h512', 'ProtSSN_k30_h768', 'ProtSSN_k30_h1280', 'ProtSSN_ensemble', 'SaProt_650M_AF2', 'SaProt_35M_AF2', 'PoET', 'MULAN_small', 'ProSST-20', 'ProSST-128', 'ProSST-512', 'ProSST-1024', 'ProSST-2048', 'ProSST-4096', 'ESCOTT', 'VenusREM', 'RSALOR', 'S2F', 'S2F_MSA', 'S3F', 'S3F_MSA', 'SiteRM', 'ESM3', 'ESMC-300M', 'ESMC-600M', 'xTrimoPGLM-1B-MLM', 'xTrimoPGLM-3B-MLM', 'xTrimoPGLM-10B-MLM', 'xTrimoPGLM-1B-CLM', 'xTrimoPGLM-3B-CLM', 'xTrimoPGLM-7B-CLM', 'xTrimoPGLM-100B-int4', 'Progen3_112m', 'Progen3_219m', 'Progen3_339m', 'Progen3_762m', 'Progen3_1b', 'Progen3_3b']
[scores] first 3 mutants: ['A113C', 'A113D', 'A113E']
A222V row present: mutant 'A222V', DMS_score 0.5944, ESM2_650M -5.200280666351318, EVmutation -4.863357093286666
a2m: wc -l = 47830 lines, grep -c '^>' = 4783 sequences (matches metadata MSA_num_seqs=4783; each sequence wraps over 10 lines); scores: wc -l = 12465 (12464 rows + header)
README baseline table: 27 model-family rows (Site Independent, EVmutation, WaveNet, DeepSequence, GEMME, EVE, Unirep, ESM-1b, ESM-1v, VESPA, RITA, ProtGPT2, ProGen2, MSA Transformer, Tranception, TranceptEVE, CARP, MIF, ProteinMPNN, ESM-IF1, ProtSSN, SaProt, PoET, MULAN, ProSST, ESCOTT, VenusREM)
```
Verdict: **PASS — AB1a = YES, found.** Equivalent naming = UniProt
entry name: `MTHR_HUMAN_Weile_2021` (task said "or an equivalent
naming"; note it is MTHR, not MTHFR, in the ID). It ships (a) a
curated MSA for exactly this assay (`MTHR_HUMAN_2023-08-07_b02.a2m`,
4,783 seqs, plus `theta0.2` weights .npy and `MTHR_HUMAN.pdb` all
listed in the metadata row), and (b) precomputed scores: ONE
per-assay CSV holding **95 model-score columns** (99 columns − mutant,
mutated_sequence, DMS_score, DMS_score_bin) — i.e. far more than the
task's "~70 models" guess; the README's baseline table counts 27 model
families while variant/size columns expand that to 95 score columns.
Two columns answer the downstream questions already: `EVmutation`
(coupling-based, → AB2c) and `ESM1v_single` + `ESM1v_ensemble`
(→ AB2b, but only TWO aggregate ESM-1v columns, not five seeds —
see flag 2).
Files created/modified: `DEEPDIVE_LOG.md` (this entry). Scratch
(3 files: metadata CSV, assays.bib, README.md, this assay's scores CSV,
its a2m) in session tmp `.../T/opencode/proteingym/` — deliberately
outside the repo; no `data/` file created by this check.
Anything unexpected or worth flagging: (1) the task's "~70 models" is
an over/under-estimate depending on counting: 27 families / 95 score
columns — I will report both numbers rather than pick one; (2) **AB2b
pre-answer: ProteinGym ships only `ESM1v_single` and `ESM1v_ensemble`
— two aggregates, NOT the five individual seeds — so it does NOT
satisfy AC4's five-seed agreement question; AC4's direct fetch (subject
to AC4b's disk check) remains necessary**; (3) the shipped MTHFR MSA
metadata reads `MSA_N_eff=646.2, MSA_Neff_L=0.99, category Low` —
directly relevant to AB3b's Neff/L<1 unusability rule and AD6's
alignment-depth metric; (4) the scores zip is monolithic
(1,911,045,703 B > 200MB cap) with no per-assay URL and directory
listing 403 — solved with HTTP Range central-directory parsing
(≈11 MB total fetched, within budget); this method works for any
future per-assay pull; (5) metadata says `includes_multiple_mutants
= FALSE, DMS_number_single_mutants = 12464` — the assay is singles
only, which constrains what AB4 can extract from shipped scores
(see AB4 when reached); (6) `assays.bib` grep also surfaced
`CALM1_HUMAN_Weile_2017`, `SUMO1/TPK1/UBC9_HUMAN_Weile_2017` as
other assays in the benchmark (context only). (7) CORRECTION MADE WITHIN THIS ENTRY, disclosed per AGENTS s5/s6: the first version of this entry's Actual-output block carried an a2m line count I wrote from expectation (`4784`) before the measuring command had returned; the command actually returned `wc -l = 47830`. Corrected in place within minutes of posting; the true sequence count `grep -c '^>' = 4783` was then measured and matches the metadata. No verdict in this entry depends on the transcribed-but-wrong line; flagged here because inventing a number is exactly the AGENTS s5 failure mode.
---

## [AB2] — Multi-model comparison table (AB2a) + ESM-1v/EVmutation verdicts (AB2b/c)
Status: FAIL
Time started / finished: 2026-09-23 21:34 (approx., right after AB1 entry) / 2026-09-23 21:50:35
What I did: (1) Re-read scripts/lib/stats.py's position_cluster_bootstrap
(the estimator AB2a mandates, "the same way script 32 does") and
verified all 95 ProteinGym score columns have zero NaNs and that
script 32's signed-own and signed-pub dropna sets are the SAME
10,757 rows / 654 positions (same row index: True), so one shared
frame serves both targets. (2) Wrote scripts/71_proteingym_model_
comparison.py with a pre-registered R1-R5 docstring BEFORE any run
(AGENTS 6), including the R2 identity gate: "the A222V row must carry
ESM2_650M = -5.200280666351318 (the value AB1 measured) to atol
1e-12, else exit(1)". Fixed six self-found defects before ANY
execution (docstring/column-name mismatch own_e_b_rho vs actual
own_rho; dead line; a tautological wt-letter check that tested
nothing; a leftover helper) - all pre-run, no result had been seen.
(3) Ran the mandated smoke (N_BOOT=300, AGENTS 1): R1 and the join
half of R2 passed, then the R2 identity gate FAILED and the script
exited 1 before any bootstrap draw. Per this session's troubleshooting
tree #2 (hard rule): STOPPED - no rerun, no N change, no test
modification to force a pass. (4) Read-only diagnosis of the exact
mismatch (no re-execution of script 71).
Actual output (verbatim, the smoke run):
```
Script 71 / AB2a  N_BOOT=300 seed=0 smoke=True  (N_PERM=10000 read but UNUSED -- R3)
*** SMOKE RUN: numbers below are machinery checks only, NOT findings, NOT for quoting. ***
row accounting: task32 table = 11344 rows -> non-null on own_e_b + GI_folinate_independent + delta_esm = 10757 rows / 654 positions (script 32's published set = 10757 / 654)
ProteinGym file: 12464 rows, 95 model score columns, NaNs = 0
join: matched 10757 / 10757 base rows (coverage 1.0000); dropped 0
R2 identity gate A222V ESM2_650M = MISSING (expected -5.200280666351318) -> FAIL
EXIT=1
```
Actual output (verbatim, the read-only diagnosis):
```
A222V present in task32 table at all: 0
position-222 rows in task32 table: 0
position-222 rows with own_e_b NaN: 0
position-222 rows surviving the 3-col dropna: 0
the 587 own_e_b-NaN rows: GI also NaN on all: True | positions: [2, 6, 19, 20, 21, 23, 33, 36, 37, 39, 52, 58, 59, 60, 63, 64, 65, 66, 67, 70, 73, 74, 77, 78, 81, 83, 84, 85, 93, 95] | n unique positions: 317 | delta_esm NaN among them: 0
=== any AB2 output file written? ===
(nothing - gate exited before output; ls: no matches found: data/processed/task_AB2*)
```
Verdict: **FAIL (AB2a)** - the pre-registered identity gate tripped
and the comparison table was never produced; the G-anchor and G-lib
engine gates never executed; no bootstrap ran (so no smoke rho
numbers exist to quote, and none are invented here). Diagnosis, for
the record: the gate's chosen row A222V is STRUCTURALLY absent from
script 32's analysis table - position 222 has zero rows in
task32_analysis_table.csv (consistent with script 70's prior-session
G5 finding of 0 variants @222 in this same set) - so the row I chose
at pre-registration could never appear in the joined frame. This is a
mis-chosen gate ROW (my construction error), not a data or join
error: the join half of R2 matched 10,757/10,757 (coverage 1.0000)
and R1 exactly reproduced script 32's published 10,757 / 654 set.
Correcting the gate requires picking a different identity row
post-hoc, i.e. changing a pre-registered test - tree #2 forbids my
doing that, so it is logged as the open decision for the user
(one-line fix + one smoke rerun would be their call). **AB2b
sub-verdict (real check, from AB1's measured column list + today's
direct read): ESM-1v scores are present as exactly TWO aggregate
columns - ESM1v_single and ESM1v_ensemble (A222V values -6.381481170654297
and -5.991078853607178) - NOT the five individual seeds, so they do
NOT satisfy AC4's seed-agreement question; AC4's direct fetch (with
AC4b's disk check first) remains necessary. AB2c sub-verdict (real
check, same read): the EVmutation column EXISTS (A222V =
-4.863357093286666, alongside its un-epistatic counterpart
Site_Independent = -4.303519347442919) - a coupling-based score computed
on this exact assay - so it is a valid score-level substitute for
Group T (see AB4 for why it is NOT a J-matrix).**
Files created/modified: scripts/71_proteingym_model_comparison.py
(created, pre-registered, exited 1 at its gate, then left UNMODIFIED
per tree #2 - no post-failure edits, no rerun); no output CSV
exists (ls confirms); DEEPDIVE_LOG.md (this entry).
Anything unexpected or worth flagging: (1) delta_esm has ZERO NaN
rows (the 587 dropped rows are entirely e.b-side: own_e_b and
GI_folinate_independent NaN on the same 587 rows spanning 317
positions - unrelated to position 222, which is simply not in the
table at all); (2) ProteinGym key coverage being exactly 100% means
the join machinery itself has no known defect - but per tree #2 the
engine's G-anchor (rho = -0.08811806424891734 identity) and G-lib
(1e-9 vs three independent lib reruns) gates were never reached, so
the shared-draw engine remains UNVALIDATED and must not be trusted
for future use until those gates run; (3) runtime of the engine is
unknown (never executed; smoke projection was ~40 s at N_BOOT=300);
(4) the six pre-run defect fixes happened before any result was seen
and are listed above for transparency - none touched a threshold.
---

## [AB3] — Alignment infrastructure (conditional: "if NOT found")
Status: SKIPPED
Time started / finished: 2026-09-23 21:52:49 / 2026-09-23 21:52:49
What I did: Re-read AB3's literal text (task doc lines 131-143) and
evaluated its trigger only: "Task AB3 - If NOT found for this exact
assay". AB1 established the assay WAS found (MTHR_HUMAN_Weile_2021),
so the condition is false and no subtask was executed: AB3a (audit
Group T's 566-row GB1 jackhmmer settings vs EVcouplings protocol)
NOT run; AB3b (compute Neff/L) NOT run as a computation - it sits
inside the skipped conditional, and the conservative/literal reading
(rule 6, logged) is to skip rather than execute a subtask of a
task whose trigger did not fire; AB3c (fetch corrected-protocol MTHFR
alignment, 200MB budget) NOT run, no file fetched.
Actual output (real numbers in hand, quoted from AB1's measured
ProteinGym MSA metadata row - NOT computed by me, recorded because
AB4 consumes it): `MSA_filename MTHR_HUMAN_2023-08-07_b02.a2m`,
`MSA_num_seqs 4783`, `MSA_N_eff 646.2`, `MSA_len 656`,
`MSA_Neff_L 0.99`, `MSA_Neff_L_category Low` - i.e. the one MTHFR
alignment that exists reports Neff/L = 646.2/656 = 0.985 (~0.99),
essentially AT but marginally BELOW AB3b's "~1" floor line.
Verdict: SKIPPED - trigger condition false; nothing executed. The
pre-existing Neff/L fact above is logged as AB1-derived context, not
as an AB3 result.
Files created/modified: none (DEEPDIVE_LOG.md only).
Anything unexpected or worth flagging: (1) the Neff/L situation is
BORDERLINE (0.985, not e.g. 0.3) - any later reasoning that leans on
"below ~1" must carry that it is only ~1.5% below the line, not
comfortably under; (2) because AB3's trigger is conditioned on
NOT-finding the assay, a corrected-protocol MTHFR realignment cannot
be fetched under this session's literal instructions - doing so would
need the user to authorize running AB3 despite its false trigger
(this is the unblock path noted under AB4).
---

## [AB4] — J(222,i) couplings computed/extracted for MTHFR (the true test)
Status: BLOCKED
Time started / finished: 2026-09-23 21:52:49 / 2026-09-23 21:52:49
What I did: Evaluated AB4a's gate (task doc lines 145-152: "Only if
AB3 produces a usable alignment (or AB2 supplies scores directly)").
Disjunct 1 = false (AB3 SKIPPED, no alignment produced). Disjunct 2 =
true in the narrow sense that coupling-model scores ARE on disk
(ProteinGym's EVmutation column, pulled in AB1 to
data/external/ProteinGym/MTHR_HUMAN_Weile_2021_scores.csv), so I
attempted the EXTRACT path: analyzed whether J(222,i) is identifiable
from the shipped file, using the file's real structure (measured, not
assumed). No model was fit, no J value computed, no correlation run -
see verdict for why, and nothing below is a result.
Actual output (the measured facts the BLOCKED rests on):
```
rows 12464 = 656 positions x 19 alt AAs (all singles, exactly)
AB1 metadata: DMS_number_multiple_mutants=0, includes_multiple_mutants=FALSE
score columns: 99 total = mutant, mutated_sequence, DMS_score, DMS_score_bin + 95 per-mutant scalar model columns (incl. EVmutation, Site_Independent); NO parameter matrices, no J/pair terms, no double-mutant rows anywhere in the file
shipped MTHFR MSA Neff/L = 0.99 (646.2/656; ProteinGym metadata, see AB3)
```
Identifiability (why extract cannot work): for a Potts model the
shipped single-mutant score of variant i at WT background aggregates
every cross-term as one scalar, S_i = dW_i + sum_j [J_ij(a_i,wt_j) -
J_ij(wt_i,wt_j)], which probes only the wild-type COLUMN of each J
block. The quantity AB4a needs - the model-implied interaction
between background A222V and variant i - is
eps(222,i) = J_222,i(V,a_i) - J_222,i(V,A) - J_222,i(A,a_i) + J_222,i(A,A),
a functional of the full 21x21 J_222,i block, recoverable only from
(a) the pairwise parameters themselves (not shipped) or (b) a
double-mutant score S(A222V+i) (assay has zero multiple mutants, so
not shipped either). One scalar per single cannot identify it.
Why compute also cannot proceed: fitting a Potts model ourselves
would use the one shipped MTHFR alignment, and the task doc's own
AB3b floor says verbatim "Below ~1, state explicitly that couplings
from it would be unusable regardless of any mapping fix - do not
proceed past this point if so" - that alignment's Neff/L = 0.99 is
below the line (marginally: 0.985), and AB3 (the corrected-protocol
realignment that could raise it) had its trigger not fire, so no
above-floor alignment exists or may be fetched under this session's
literal instructions.
Verdict: BLOCKED - two exact blockers: (i) missing data = EVmutation
pairwise parameters for MTHFR AND double-mutant model scores (neither
is in the shipped file; the only MTHFR coupling scores that exist are
single-mutant aggregates), and (ii) the task doc's AB3b floor blocks
training couplings on the available Neff/L=0.99 alignment. What I did
NOT do: did not fabricate J values, did not substitute a different
"coupling-like" quantity (e.g. the EVmutation-vs-Site_Independent
per-mutant contrast, which is still a sum over all j and is NOT
J(222,i)), did not report any rho. Unblock paths (user decisions):
(a) authorize AB3's corrected-protocol MTHFR fetch + a Potts fit
despite its false trigger, or (b) supply actual EVmutation/EVcouplings
MTHFR model parameters if any release exists - I have NOT verified
any such release exists and will not cite one (AGENTS 5).
Files created/modified: none (DEEPDIVE_LOG.md only).
Anything unexpected or worth flagging: (1) every position INCLUDING
222 exists in ProteinGym's raw score file (12,464 = 656x19), while
our own analysis base contains ZERO position-222 rows - this
asymmetry is precisely what tripped AB2's identity gate and is worth
one explicit note for whoever fixes that gate; (2) AB4a explicitly
asks to report side by side with delta_ESM's -0.088 and ThermoMPNN's
-0.0733 - no side-by-side exists because no coupling number was
computed; those two anchors are untouched by this entry; (3) had the
extract path been possible it would have used this project's standard
conventions (position-cluster bootstrap, N_BOOT=10000, seed=0) -
stated so the blocked task's intended method is on record, not as a
result.
---

## [AA4] — Project-own detection floor (the evaluator's "worth more than any borrowed gate pass")
Status: PASS
Time started / finished: 2026-09-23 21:55 (approx., after AB4 entry) / 2026-09-23 22:53:41
What I did: Read AA4's exact text (task doc lines 64-77), then read
script 33 and scripts/lib/{own_context,stats_ext}.py to REUSE (not
rewrite) the two-test pipeline. Wrote
scripts/72_mthfr_detection_floor.py with a fully pre-registered
F1-F8 docstring BEFORE any run: real frame (script 33's exact
construction), identity checks first, generator using measured
per-condition SE noise + measured position ICC, grid
{0.0(calibration),0.05,0.10,0.15,0.20,0.25}, R=50, both real tests
(script-33 sign-flip primary; lib position-cluster bootstrap
secondary) at N_BOOT=N_PERM=10000 seed=0, shared-draw engine with a
3-pair G-lib identity gate vs lib verbatim, output to
data/processed/task_AA4_detection_floor.csv (the exact AA4d name).
Smoke (N_BOOT=N_PERM=300, R=3) PASSED all gates but EXPOSED a
generator defect (see flag 1); fixed the generator (criterion
unchanged, disclosed), re-smoked clean, then ran the full job
2026-09-23 22:05:43 -> 22:53:41 (47.9 min, foreground).
Actual output (verbatim, FULL RUN, N_BOOT=10000 N_PERM=10000 R=50):
```
frame: 10757 rows / 654 positions (script 33 published: 10757/654: MATCH)
  all-+1 flips reproduce own_e_b exactly: max|diff|=2.220e-16
  all--1 flips give exactly -own_e_b:     max|diff|=2.220e-16
measured per-condition noise: sigma_i from 8 SE cells (median per row), 0 rows filled, sd(sigma)=0.7138
position clustering: J=654 positions, k_bar=16.45, MSB=2.5033 MSW=0.9028 -> ICC=0.0973 -> w=0.0973 (structure ingredient)
  calibration rho_true=0.05: r=0.041822 (copula closed form would be 0.052354), pilot mean achieved=+0.05000
  calibration rho_true=0.10: r=0.085860 (copula closed form would be 0.104672), pilot mean achieved=+0.10000
  calibration rho_true=0.15: r=0.130136 (copula closed form would be 0.156918), pilot mean achieved=+0.15000
  calibration rho_true=0.20: r=0.174749 (copula closed form would be 0.209057), pilot mean achieved=+0.20000
  calibration rho_true=0.25: r=0.219775 (copula closed form would be 0.261052), pilot mean achieved=+0.25000
built 300 predictors (6 rho x R=50) in 0.4s
  rho_true=0.00: achieved rho mean=+0.0015 sd=0.0085 (target 0.00)
  rho_true=0.05: achieved rho mean=+0.0466 sd=0.0093 (target 0.05)
  rho_true=0.10: achieved rho mean=+0.0995 sd=0.0072 (target 0.10)
  rho_true=0.15: achieved rho mean=+0.1484 sd=0.0087 (target 0.15)
  rho_true=0.20: achieved rho mean=+0.1986 sd=0.0091 (target 0.20)
  rho_true=0.25: achieved rho mean=+0.2463 sd=0.0103 (target 0.25)
F3 construction gate: worst |mean achieved - target| = 0.0037 (tol 0.01) -> PASS
sign-flip null: 10000 re-derivations x 300 predictors in 18.8s (flips drawn once, seed=0; non-finite cells = 0)
bootstrap: 10000 draws x 300 predictors in 2768.3s
G-lib rho=0.10 rep=0: engine obs=+0.111667569457 CI=[+0.088089066430,+0.134233641795] p=0.000000 | lib obs=+0.111667569457 CI=[+0.088089066430,+0.134233641795] p=0.000000 | max|diff|=1.388e-17
G-lib rho=0.25 rep=0: engine obs=+0.248711247810 CI=[+0.226209036802,+0.271141086935] p=0.000000 | lib obs=+0.248711247810 CI=[+0.226209036802,+0.271141086935] p=0.000000 | max|diff|=5.551e-17
G-lib rho=0.00 rep=0: engine obs=-0.005989810140 CI=[-0.028679026220,+0.016057937747] p=0.603200 | lib obs=-0.005989810140 CI=[-0.028679026220,+0.016057937747] p=0.603200 | max|diff|=3.469e-18
G-lib overall max|diff| = 5.551e-17 (threshold 1e-9) -> PASS
POWER TABLE (primary test = script-33 sign-flip; secondary = bootstrap CI)
  rho_true=0.00 (CALIBRATION): power_signflip=0.00 power_boot=0.00 achieved=+0.0015 mean_CI_halfwidth=0.0224
  rho_true=0.05: power_signflip=1.00 power_boot=1.00 achieved=+0.0466 mean_CI_halfwidth=0.0225
  rho_true=0.10: power_signflip=1.00 power_boot=1.00 achieved=+0.0995 mean_CI_halfwidth=0.0224
  rho_true=0.15: power_signflip=1.00 power_boot=1.00 achieved=+0.1484 mean_CI_halfwidth=0.0225
  rho_true=0.20: power_signflip=1.00 power_boot=1.00 achieved=+0.1986 mean_CI_halfwidth=0.0221
  rho_true=0.25: power_signflip=1.00 power_boot=1.00 achieved=+0.2463 mean_CI_halfwidth=0.0221
F4 calibration at rho=0: sign-flip rejection 0.00 of R=50 (ceiling 0.15, nominal 0.05) -> PASS
F6 sign-flip null centring across all 300 predictors: mean of null means=+0.00002, mean null sd=0.0101 (centred)
AA4c statement: "we could have detected rho >= 0.05; we observed -0.088"
saved data/processed/task_AA4_detection_floor.csv (306 rows: 300 replicate + 6 summary)
phase build: 0.4s / phase signflip: 18.8s / phase boot: 2768.3s / total 2875.8s
EXIT=0
```
Verdict: **PASS.** AA4c's sentence, exactly as the evaluator asked:
**"we could have detected rho >= 0.05; we observed -0.088."** Every
hard gate passed at full N: identity 2.220e-16 (<=1e-6), F3
construction 0.0037 (<=0.01), G-lib engine-vs-lib 5.551e-17
(<1e-9), type-I calibration 0/50 false positives at rho=0 (ceiling
0.15; with R=50 the rule-of-three upper bound is 0.06, consistent
with the nominal 0.05), sign-flip null centred at +0.00002 with mean
sd 0.0101. IMPORTANT HONESTY NUANCE, stated plainly: power saturated
at 1.00 already at the SMALLEST nonzero grid point (0.05), so the
real floor lies BELOW 0.05 and this grid cannot say where (resolution
0.05, pre-registered as such - no adaptive points were added); the
quotable claim is therefore "rho >= 0.05" as pre-registered, and the
observed |0.088| sits comfortably ABOVE that floor. Both tests agreed
at every point (power_signflip == power_boot == 1.00 for rho>0).
Files created/modified: scripts/72_mthfr_detection_floor.py (new,
pre-registered + one disclosed amendment, flag 1);
data/processed/task_AA4_detection_floor.csv (the AA4d deliverable,
306 rows); data/processed/task_AA4_detection_floor_smoke.csv (smoke,
machinery-only); DEEPDIVE_LOG.md (this entry).
Anything unexpected or worth flagging: (1) **DISCLOSURE - post-smoke,
pre-full-run generator fix (AGENTS 6): the first smoke showed the
Gaussian-copula closed form r=2*sin(pi*rho/6) OVERSHOOTING the
target systematically - achieved means +0.1204 (target 0.10),
+0.1758 (0.15), +0.2437 (0.20), +0.2943 (0.25) - because the
injection noise v (heteroscedastic scale mixture, sigma sd=0.7138,
plus a position random effect) is not bivariate-normal with z_e, so
the closed form is not the exact inverse Spearman map here. I fixed
the GENERATOR (r now solved by 24-step bisection against a fixed
pilot batch, M=25, pilot rng seed=1) and left the +-0.01 F3 criterion
UNCHANGED - this is the script-70 G1 pattern (construction fixed,
criterion fixed, both disclosed), not threshold tuning; the smoke
values above are quoted verbatim so the before/after is auditable.
(2) Calibration at rho=0 rejected 0/50 - no type-I inflation; a zero
rate is explicitly NOT a failure under pre-registered F4. (3) Mean CI
half-width ~0.0224 is a useful freeby: it is this design's 95% CI
half-width for a single Spearman, i.e. any |rho| below ~0.02-0.03
could not be individually resolved even though POWER (test-level) at
0.05 is 1.00. (4) The measured position ICC = 0.0973 (only ~10% of
z_e variance is position-shared) - real clustering structure was
weak-ish but present and used; k_bar=16.45 substitutions/position.
(5) Runtime 47.9 min total (boot 46.1 min) - fits the ~2h task
budget; N_BOOT/N_PERM/R all printed by the script itself.
(6) RuntimeWarnings from own_context/stats_ext ("Mean of empty
slice") are pre-existing lib behavior on all-missing raw rows,
seen in prior sessions too; they do not affect the finite rows used
(n_fills=0 for sigma).
---

## [AC4] — All five ESM-1v ensemble members (the evaluator's top-3 pick)
Status: BLOCKED
Time started / finished: 2026-09-23 22:55 (approx., after AA4 entry) / 2026-09-23 22:59:58
What I did: Read AC4's exact text (task doc lines 189-209).
AC4a (check AB2b first): ANSWERED from the already-measured AB2
inspection - ProteinGym supplies ONLY two aggregate ESM-1v columns
(ESM1v_single, ESM1v_ensemble), NOT the five individual members' scores,
so the "use those and skip the fetch" branch does NOT apply and AC4b's
fetch path is required (cross-ref [AB2] AB2b, same evidence). AC4b
mandates the total-disk check BEFORE starting - done first, nothing
downloaded: (1) df on the volume; (2) search for any already-cached
ESM-1v checkpoint (data/, ~/.cache/torch, ~/.cache/huggingface, harness
scratch); (3) mount table for a secondary volume; (4) header-only size
verification of all five members (HTTP Range GET, bytes=0-0, zero
payload downloaded) using the canonical names resolved from
CLOSEOUT_LOG's recorded U3a probe (my first guess `esm1v_v33_650M_...`
403'd - wrong name; correct is `esm1v_t33_650M_UR90S_{1..5}`).
AC4c and AC4d NOT attempted (gated on AC4b).
Actual output (verbatim):
```
Filesystem      Size    Used    Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   228Gi   175Gi    21Gi    90%    1.8M  217M    1%  /System/Volumes/Data
avail_KB=21694332 avail_GB=20.6893
data: 2.9G total (raw 19M, processed 67M, external 2.8G [SaProt 2.4G])
=== any ESM-1v / UR90S checkpoints already on disk? ===
(end of search)   <- zero hits anywhere
member 1: HTTP=206 total_bytes=0-0/7828635339
member 2: HTTP=206 total_bytes=0-0/7828635339
member 3: HTTP=206 total_bytes=0-0/7828635339
member 4: HTTP=206 total_bytes=0-0/7828635339
member 5: HTTP=206 total_bytes=0-0/7828635531
(prior independent measurement, CLOSEOUT_LOG U3a `curl -sI`: content-length: 7828635339 - agrees with my probe)
```
Disk arithmetic (AC4b's mandated check, both unit systems):
- Required = 4 x 7,828,635,339 + 7,828,635,531 = **39,143,176,887 B**
  = 36.45 GiB (39.14 GB decimal), for the five files ON DISK before any
  loading; zero members are cached today (fetch starts from nothing).
- Available = 21,694,332 KB = **22,214,995,968 B** = 20.69 GiB
  (22.21 GB decimal), on the ONLY data volume (mount table shows no
  secondary disk; disk is already at 90% capacity).
- **Shortfall = 16,928,180,919 B = 15.76 GiB** (need 1.76x what exists).
Verdict: **BLOCKED - AC4b's total-disk check fails by 15.76 GiB.**
The task's own clause for this situation is "check total available disk
space before starting and report it" plus this session's budget rule
(AC4 = the total-disk exception, BLOCKED with numbers if insufficient) -
reported above with exact byte counts. AC4a = fetch path confirmed
necessary (not skipped); AC4c (score with 5 members) and AC4d (the
decisive seed-noise verdict) are BLOCKED transitively and were NOT
attempted. **No bytes of model data were downloaded** (headers only).
Files created/modified: none except DEEPDIVE_LOG.md (this entry).
Anything unexpected or worth flagging: (1) the evaluator's working
figure 7.83GB/member is now INDEPENDENTLY VERIFIED by live Range
probes (members 1-4 identical at 7,828,635,339 B; member 5 differs by
exactly +192 B - noted for exactness, immaterial); (2) the
optimizer-state hypothesis gets arithmetic support without
downloading: 7,828,635,339 / 2,604,537,549 (the cached, architecturally
identical ESM-2 650M fp32 file, per CLOSEOUT_LOG U3a flag) = 3.006x,
i.e. ~params + 2 Adam moments at fp32 - CONSISTENT with, but not proof
of, "optimizer state"; per AC4b the real check is load-and-count
parameters, which is post-fetch and therefore deferred with the block
(this is flagged as unverified, not asserted); (3) this is the SAME
disk/cap wall the closeout session left as Z0/U3 (carry-forward note):
AC4's own text sanctions the >3GB-per-file fetch (so that layer has
task-level authorization now), but the total-disk wall is independent
and still unsatisfied; (4) my first URL guess (esm1v_v33_...) 403'd -
corrected to t33 using the closeout log's recorded resolution before
any request carried payload; (5) unblock options for the user, none of
which I will do unilaterally: (a) free >= ~16-18 GiB on the volume;
(b) approve a staged fetch-score-extract-delete variant (peak usage
~8 GiB; deviates from the literal "fetch all 5 ... before starting"
procedure, so it needs explicit approval); (c) pre-supply the five
checkpoints from outside this machine.
---

## [AD1] — ThermoMPNN sign-convention audit (STOP-FIRST for all of Group AD)
Status: PASS
Time started / finished: 2026-09-23 23:00 (approx., after AC4 entry) / 2026-09-23 23:05:15
What I did: AD1a requires confirming a documented buried-hydrophobic-
to-charged substitution scores as clearly DESTABILIZING under the
sign convention this project's runs actually used, BEFORE anything
else in Group AD (task doc line 245: STOP-FIRST, same discipline as
S1/S2). I assembled the convention chain end to end without running
any model: (1) the project's run - script 68 invokes ThermoMPNN's own
CLI unmodified ("No third-party code is edited or re-implemented"),
output data/processed/task_V2_thermompnn_ddg.csv (10,141 rows);
(2) the forward formula in the vendored repo -
data/external/ThermoMPNN/transfer_model.py lines 113-116: `if
self.subtract_mut: ddg = ddg_out[aa_index][0] - ddg_out[wt_aa_index][0]`
with subtract_mut TRUE in both config.yaml line 16 and
custom_inference.py line 41 - so stored ddG = (mutant head) - (WT head);
(3) the repo's own semantic anchor -
analysis/SSM.py lines 33-42 `retrieve_best_mutants` selects
`idxmin(ddG_pred)` per position as the BEST mutant, i.e. most negative
= most stabilizing => positive = destabilizing, stated by the code's
own use of the word "best"; (4) external documentation of the same
model: Dieckhaus et al. 2024 (ThermoMPNN-D paper, PMC11370451)
characterizes the parent model verbatim - "ThermoMPNN is a
structure-based protein stability model. More positive d∆G values
indicate more destabilizing mutations." - and the BioLM model card for
ThermoMPNN states "negative ddG indicates stabilization, positive ddG
indicates destabilization" (ddG = dG_mutant - dG_wildtype); (5) the
EMPIRICAL positive control on the project's own stored values, using
the atlas's structural reference
data/raw/mthfrModel/reference_data/MTHFR_structural_features.csv
(651 positions, columns include Relative ASA, PDB chain, Secondary
Structure, FAD/Folate/SAM annotations) for documented burial.
Actual output (verbatim):
```
subtract_mut in configs: data/external/ThermoMPNN/config.yaml:16: subtract_mut: true
                                          custom_inference.py line41: 'subtract_mut': True
transfer_model.py 113-116: if self.subtract_mut: ddg = ddg_out[aa_index][0] - ddg_out[wt_aa_index][0]
SSM.py 41: min_row = p_slice.iloc[pd.to_numeric(p_slice['ddG_pred']).idxmin()]   (inside retrieve_best_mutants)
merged: 10141 | rsa present: 10141
OVERALL: frac ddg>0 = 0.8891 | mean=1.0316 median=0.8571 min=-1.7602 max=4.5008
BURIED(rsa<0.10) hydro->charged n=123: median=2.629 mean=2.684 min=0.675 max=4.501 frac>0=1.000
EXPOSED(rsa>0.50) same class n=661: median=1.833 frac>0=0.949
top-8 most-buried buried-hydrophobic->charged controls:
   hgvs_pro        position wt_aa mut_aa  rsa      ddg   own_e_b
 p.Ala113Arg          113     A     R    0.0   2.226977  0.090928
 p.Phe516Glu          516     F     E    0.0   3.497138 -0.031441
 p.Phe516Asp          516     F     D    0.0   4.066879  0.001545
 p.Phe516Arg          516     F     R    0.0   3.229506 -0.037007
 p.Leu621Glu          621     L     E    0.0   2.588402 -0.092935
 p.Leu621Asp          621     L     D    0.0   3.039570 -0.117073
 p.Leu621Arg          621     L     R    0.0   2.680789 -0.385310
 p.Leu618Lys          618     L     K    0.0   2.908469  0.429301
```
Verdict: **PASS - the sign is NOT flipped; -0.0733 keeps its sign and
the Part II section 12 interpretation does NOT invert; Group AD is
unblocked.** The documented control: p.Phe516Asp - a fully buried
phenylalanine (Relative ASA = 0.0 in MTHFR's own structural reference)
to aspartate, the textbook buried-hydrophobic-to-charged case - scores
ddG = +4.067 (clearly destabilizing, physically sized for a kcal/mol
scale), and it is not a lone anecdote: ALL 123 buried (rsa<0.10)
hydrophobic->charged substitutions score positive (median +2.629,
range +0.675..+4.501), with the physically expected burial
dose-response (exposed same-class median +1.833 < buried +2.629) and
the literature-consistent base rate (88.9% of all 10,141 missense
score destabilizing). Four independent layers agree - forward formula,
repo code semantics, the model's published characterization, and this
physical positive-control set - so the audit does not rest on any
single reading.
Files created/modified: none except DEEPDIVE_LOG.md (this entry). No
model was run; no file under data/external/ThermoMPNN was modified
(all repo files read-only).
Anything unexpected or worth flagging: (1) the vendored README states
NO sign convention at all (grep for stabil/destabil/sign/ddG returns
nothing usable) - the in-repo documentation gap is why the verdict is
carried by the code-semantics anchor plus the external quote rather
than a README citation; both are quoted verbatim above. (2) The
external quote comes from the ThermoMPNN-D paper characterizing the
PARENT ThermoMPNN model (itself trained/evaluated on the Megascale
dataset whose convention is positive=destabilizing); it is a
characterization of the same model this project ran, not of the -D
double-mutant model. (3) task_V2_thermompnn_ddg.csv contains ZERO
position-222 rows (Ala222Val absent) - consistent with AB2's finding
that position 222 never enters the project's own-e_b analysis set, so
the -0.0439 A222V figure cited by AD2a lives in script 68's V3 output
line, not in this CSV; AD2 will handle it there. (4) A convenience
subquery for FAD-pocket members of the control set crashed on mixed
str/float flag types; it was abandoned as non-essential (the audit
already has its named cases + set statistics) - recorded here rather
than silently dropped. (5) The struct file carries 'Dimer burial' and
'Dimer relative burial' columns - directly reusable by AD7's dimer
question when it is reached.
---

## [AA1] — Transplant the MTHFR estimator onto GB1 (script 33's instrument, not I1's)
Status: PASS (executed end-to-end; all gates green; AA1c's centreing question answered YES; the detection result is a PLAIN NULL, reported untuned)
Time started / finished: 2026-09-23 23:16 (approx., after AD1 entry) / 2026-09-23 23:29:13
What I did: Read AA1's exact text (task doc lines 31-45). Reconnaissance of
the five pieces of existing machinery the transplant must honor
(scripts 49/65 for the GB1 design constants and fitness gates, script 12
for the delta_ESM definition, script 33 for the sign-flip code path,
own_context.py for the e.b construction, esm_scoring.get_position_logprobs
for scoring) - all READ ONLY, none modified. Pre-registered BEFORE the
first run and before any background-genotype fitness was read: background
= site 54 V->A (V54A), chosen by chemical parallelism with A222V (the
same Ala/Val interchange, direction reversed) and fitness-blind; 57
variants = 19 non-WT residues at each of the other three sites; six
explicit adaptations A1-A6 (single-point residual replaces the
4-concentration WLS line; uniform weights - GB1 ships no per-genotype
SEs; multiplicative expectation E[f(v+bg)] = f(v)*f(bg)/f(WT) on the
fitness scale; no fitness-based row filtering; flip cell = variant;
Null-2 blocks = focal site with script 33's region check omitted, GB1
has no MTHFR regions). New script: scripts/73_gb1_estimator_transplant.py
(next free number after 72). Ran smoke first (N_PERM=200, EXIT=0, 78.2s),
then added ONE explanatory print about a degeneracy the smoke revealed
(post-hoc DISCLOSURE in the script's own text; NO statistic changed),
then the full run (N_PERM=10000, EXIT=0, 42.4s).
Actual output (verbatim, full run):
```
Data gates PASSED: 160,000 genotypes, WT=VDGV=1.0, 20 AAs/column; md5=89e8d0f088466a1e29714721ed7967e8
Background (pre-registered): site 54 V->A (V54A), chemical parallel to A222V, fitness-blind
Variants: 19 non-WT residues at sites (39, 40, 41) -> 3x19=57 rows
f(WT) = 1.000000 | f(V54A background) = 1.372949  [first read of this value; A222V-parallel caveat below]
e.b analog: n=57 | mean=-0.1132 median=-0.0056 | min=-3.3430 max=+3.9924
Non-positive-value counts (A4: kept, never filtered): single arm 0, double arm 2, expectation 0 of 57
Adaptations A1-A6 active: single-point residual replaces the 4-concentration WLS line; uniform weights; multiplicative
expectation on fitness scale; no row filtering; flip cell = variant; Null-2 blocks = site (region check omitted, no GB1
regions).
wls_line at n=1 x-point returns intercept=[nan] (det=S0*S2-S1^2=0 -> NaN by its own guard): reduction A1 forced.
Loading ESM-2 t33 650M on mps...
Scored 6 forward passes -> 57 delta values (expect 57)
delta_ESM analog: mean=+0.0316 median=+0.0064 min=-0.2836 max=+0.4760
==========================================================================
SANITY CHECKS (script 33's, transplanted: test the test first)
==========================================================================
  all-+1 flips reproduce own_e_b exactly: max|diff|=0.000e+00
  all--1 flips give exactly -own_e_b:     max|diff|=0.000e+00
Design summary for AA2 (unit of analysis):
  rows=57 | flip units (cells)=57 (one +/-1 per variant, A5) | sites=3 | backgrounds=1 | MTHFR contrast: 10,757 variants x 4 conc cells = 43,028 cells, 654 positions
==========================================================================
NULL 1 -- SIGN-FLIP RE-DERIVATION (10000 permutations)
==========================================================================
  signed delta_ESM vs signed e_b
    observed=+0.1222  null mean=-0.0004 sd=+0.1408  p=0.3849
    excess over null=+0.1225  (-0% of the raw value is structural artifact)
    -> does NOT survive
    null-centring check: null mean IS consistent with zero -- machinery behaving
    PRE-REGISTERED READS: instrument behaves = YES; detects established epistasis = NO (signed two-sided p < 0.05)
  absolute |delta_ESM| vs |e_b|
    observed=+0.0386  null mean=+0.0386 sd=+0.0000  p=1.0000
    excess over null=+0.0000  (100% of the raw value is structural artifact)
    -> does NOT survive
    STRUCTURAL NOTE (A1/A5; this explanatory print was added AFTER the smoke run first showed it -- post-hoc
DISCLOSURE, no statistic changed): with ONE cell per variant, |flip * r| = |r| is invariant to the sign flips, so the
absolute sign-flip null equals the observation IDENTICALLY (p = 1 by construction). The absolute variant of Null 1 is
DEGENERATE under the single-cell transplant and carries no information here. MTHFR's 4 cells per variant make its
intercept flip-sensitive, so that absolute test is non-degenerate there (script 33).
==========================================================================
NULL 2 -- SITE-BLOCK PERMUTATION (weaker; association only; A6: 3 blocks)
==========================================================================
  observed=+0.1222  null mean=-0.0026 sd=+0.2533  p=0.8399
  This asks whether the pairing beats chance, NOT whether the
  interaction exceeds measurement noise. Null 1 is the real test.
LIMITATIONS (printed here per AGENTS sec 6)
==========================================================================
  - 57 flip units over 3 sites and 1 background: the p-value's
    precision comes from 10000 draws, NOT from 57 independent
    sites; effective independent structure is 3 sites (AA2).
  - V54A fitness = 1.372949 (read once, pre-registered choice).
  - Single-background design mirrors MTHFR's single A222V.
  - No concentration axis: slope term not identifiable (A1);
    frac_artifact computed on Spearman rho as script 33 does.
  - Scale reference: MTHFR's verified signed
    rho(delta_ESM, own_e_b) = -0.08811806424891734
Saved: .../task_AA1_gb1_eb_analog.csv (57 rows), .../task_AA1_gb1_signflip_nulls.csv (3 rows)
Elapsed: 42.4s | N_PERM=10000 | SEED=0
EXIT=0
```
Prior-instrument scale (both GB1 CSVs, verbatim, for comparison):
```
task49_i1_gb1.csv: pooled_rho 0.4466626167166524 | null_mean 0.3880021459076137 | p_one_sided 0.13978602139786023 |
  n_pairs 570 | gate_pass 0.0 | rho_site_39 0.31651292279564536 | rho_site_40 -0.15061602684606235 | rho_site_41 0.5234351148377052
task_Q1_foursite_i1_rerun.csv: pooled_rho 0.4017569729349947 | null_mean 0.2475697544092186 | p_one_sided 0.000999900009999 |
  n_pairs 760 | gate_pass 1.0 | rho_site_39 0.3365066284911878 | rho_site_40 -0.12796301399222315 |
  rho_site_41 0.34810674154846105 | rho_site_54 0.33838960402752083
```
Verdict: AA1a, AA1b, AA1c ALL EXECUTED, and the transplanted instrument
answered AA1c's actual question: **the sign-flip null DOES centre on zero
on GB1** (null mean -0.0004, well inside script 33's exact expression
|mean| < 2*sd/sqrt(N) = 0.00845) - so centreing-on-zero is a property of
THIS null type wherever it runs, now demonstrated outside MTHFR. The
detection result is reported plainly and was NOT tuned (AGENTS sec 0):
observed rho +0.1222 over the 57-row single-background transplant does
not reach significance (p = 0.3849; null sd 0.1408 means ~|rho| > 0.28
would be needed at 2 sd). Despite seeing f(V54A) = 1.372949 after the
fact, the background was NOT switched, K backgrounds were NOT added, no
one-sided gate was introduced, and no row was filtered - all such
changes are pre-declared user decisions. Honest combined reading: the
instrument is CALIBRATED (centres on zero) but this transplant at n=57
with 1 cell/variant is UNDERPOWERED for detection; detection power on
MTHFR's own design was established separately by AA4 (power 1.00 down to
rho 0.05). The absolute variant of Null 1 is degenerate by construction
under single-cell flips (|flip*r| = |r|) and carries no information
here - disclosed in the script's own output post-smoke.
Files created/modified: scripts/73_gb1_estimator_transplant.py (NEW,
next free number); data/processed/task_AA1_gb1_eb_analog.csv (NEW, 57
rows); data/processed/task_AA1_gb1_signflip_nulls.csv (NEW, 3 rows);
DEEPDIVE_LOG.md. Scripts 12/33/49/65 and lib modules: read-only, zero
modifications.
Anything unexpected or worth flagging: (1) own_context.wls_line returns
NaN at a single x-point - its det != 0 guard fires (printed live), so
the single-point reduction (A1) is FORCED by the design, not chosen for
convenience; (2) f(V54A) = 1.372949, i.e. the fitness-blind background
turned out mildly BETTER than WT, not dead - the control is not
degenerate, but it is a beneficial background rather than an
A222V-like-destabilizing one (parallel caveat printed); (3) 2 of 57
double-arm values are <= 0 (kept per pre-registered A4, counts
printed); (4) task49's own CSV shows gate_pass 0.0 - the 3-site
association control FAILED its pre-registered gate (p_one_sided = 0.14)
while the 4-site rerun passed (0.001); both nulls sit far above zero
(0.388, 0.248) - this is the material AA3's question is about;
(5) the post-smoke addition of the degenerate-absolute explanatory
print is disclosed here as a post-hoc edit to script 73's output text
only (no statistic, gate, or threshold touched); (6) ESM-2 load plus 6
forward passes took the run to 42s total - trivial compute.
---

## [AA2] — Characterize the unit of analysis and effective n (transplanted design)
Status: PASS (stated plainly; no new execution needed - all counts come from script 73's own printed output and script 33's printed analysis set)
Time started / finished: 2026-09-23 23:29 (directly after AA1) / 2026-09-23 23:29:53
What I did: Answer AA2a (task doc lines 47-52) from the run that just
executed: the clustering/flip unit in the transplanted design, the
effective number of independent units the sign-flip null is actually run
over, and the contrast with what a p-value might be read to imply.
Nothing was re-run; quoted sources are script 73's printed "Design
summary for AA2" block (in the [AA1] entry) and script 33's own printed
analysis-set line (n = 10,757 variants over 654 positions, the same set
AA4 re-verified).
Actual output (verbatim, script 73's run):
```
Design summary for AA2 (unit of analysis):
  rows=57 | flip units (cells)=57 (one +/-1 per variant, A5) | sites=3 | backgrounds=1 | MTHFR contrast: 10,757
variants x 4 conc cells = 43,028 cells, 654 positions
```
The statement AA2a asks for, plainly:
- Clustering unit = the (focal site, mutant letter) genotype VARIANT
  (e.g. site 40, residue E). Each variant carries exactly ONE e.b value
  (one fitness triple: f_single, f_double, shared f_bg) and therefore
  exactly ONE sign-flip cell - unlike MTHFR, where each variant carries
  4 concentration cells.
- Effective independent units the sign-flip null runs over = **57**
  (one independent +/-1 draw per variant per permutation) - not on the
  order of 20-30 but also NOT 57 independent sites: the 57 units sit in
  only **3 sites** (19 variants share each site's WT arm), share **1
  background** (f_bg = 1.372949 enters every row), and share f_wt = 1.0.
  The fully-independent biological structure below the variant level is
  therefore 3 sites x 1 background.
- Consequently the p-value's precision comes from N_PERM = 10,000 draws
  over a 57-cell flip space; it must NOT be read as evidence pooled from
  57 independent sites, and certainly not from 10,000 independent
  anything. AA1's p = 0.3849 is a statement about 57 units in 3 sites
  with 1 background, and is reported at exactly that resolution.
- MTHFR contrast (same instrument, its own design): script 33 flips
  10,757 variants x 4 concentration cells = 43,028 cells, with position
  clustering (654 positions) as this project's bootstrap unit per
  AGENTS sec 3 - an order of magnitude more clustering units than the
  transplant's 3 sites, which is why MTHFR-side p-values (AA4-style)
  carry correspondingly more structure behind them than AA1's do.
Verdict: PASS - the unit of analysis and effective n are stated above
without letting any p-value imply more precision than 57 variant units
in 3 sites / 1 background support.
Files created/modified: DEEPDIVE_LOG.md only.
Anything unexpected or worth flagging: nothing beyond what [AA1]
already disclosed - the point worth repeating is that AA2's own
question (are there ~20-30 units?) lands close: 57 is the same order of
magnitude, so AA1's transplant p-values are inherently coarse and any
future reader should treat AA1's null-detection result as low-resolution
by design, not as a fine-grained negative.
---

## [AA3] — Why the I1 association null does not centre on zero (and 0.3880 -> 0.2476)
Status: PASS (mechanism characterized from both constructions' verbatim code; not the same kind of null - that IS the answer)
Time started / finished: 2026-09-23 23:30 (after AA2) / 2026-09-23 23:31:42
What I did: Answer AA3a (task doc lines 54-62) by reading both null
constructions in full - scripts 49 and 65's within-site
variant-profile permutation (the association null) and script 33's
sign-flip re-derivation (re-read verbatim), plus script 73's just-run
transplant of the latter. Extracted both runs' stored numbers from their
on-disk CSVs (values quoted below verbatim; the two percentages are
direct arithmetic on those stored values, no new execution). No file was
modified; no statistic was recomputed beyond dividing the stored
quantities.
Actual output (verbatim, the constructions side by side):
```
scripts/49 (identical code reused by 65) -- the ASSOCIATION null:
    # association null: permute variant labels WITHIN site -- a variant's
    # whole K-background epistasis profile moves as a unit (delta stays
    # fixed; e is reassigned among variant blocks), breaking only the
    # pairing between delta and e across variants (AGENTS sec4: association
    # null, labeled as such).
    rng_p = np.random.default_rng(SEED)
    perm_rhos = np.empty(N_PERM)
    for i in range(N_PERM):
        d_p = d_base.copy()
        e_p = e_base.copy()
        for s in sites:
            idxs = groups[s]
            order = rng_p.permutation(len(idxs))
            for slot, src in enumerate(order):
                e_p[idxs[slot]] = e_base[idxs[src]]
        rp, _ = spearmanr(d_p, e_p)
        perm_rhos[i] = rp
    center_note = ("null centers on zero" if abs(null_mean) <= null_sd / 2
                   else "NULL DOES NOT CENTER ON ZERO -- raw rho would "
                        "overstate the effect; excess over null is the "
                        "real result (AGENTS sec4)")

scripts/33 (and script 73's transplanted copy) -- the SIGN-FLIP null:
        for p in range(N_PERM):
            eb_p, _, _ = wls_line(Rs * rng.choice([-1.0, 1.0], size=Rs.shape),
                                  Ss, CONCS, Vs)
            g = np.isfinite(eb_p) & np.isfinite(pred)
            null[p] = _spearman(pred[g], eb_p[g] if signed else np.abs(eb_p[g]))
        pv = float((np.abs(null) >= abs(obs)).mean())

stored numbers (both GB1 CSVs, verbatim):
  3-site  task49:                pooled_rho 0.4466626167166524 | null_mean 0.3880021459076137
  4-site  task_Q1_foursite:      pooled_rho 0.4017569729349947 | null_mean 0.2475697544092186
  per-site rhos 3-site:  39 +0.31651292279564536 | 40 -0.15061602684606235 | 41 +0.5234351148377052
  per-site rhos 4-site:  39 +0.3365066284911878 | 40 -0.12796301399222315 | 41 +0.34810674154846105 | 54 +0.33838960402752083
AA1's same-instrument control (script 73, for contrast): signed sign-flip
null mean -0.0004 sd 0.1408 -> centres on zero.
```
The characterization AA3a asks for:
1. What produces a nonzero centre AT ALL: script 49's permutation is
   RESTRICTED - it only re-pairs e-profiles to delta within a site, with
   delta fixed. Every piece of structure at or above the re-paired level
   is therefore IDENTICAL in every one of the 10,000 draws: the site
   membership of each e-profile (so all between-site rank structure in
   both marginals survives), and - because the K=10 backgrounds are the
   SAME set for all 19 variants of a site and profiles are moved in
   profile order, background-by-background - all background-level
   covariance too (both delta's context-b log-odds and e's f(WT,b) terms
   track background severity). Only the within-site, variant-to-variant
   pairing is actually randomized. With just 3 (then 4) blocks whose
   per-site rhos are strongly heterogeneous (site 40 is NEGATIVE, sites
   39/41/54 positive), that retained block-level component is most of
   the pooled rho, so the null sits high: mean +0.3880 = 86.9% of the
   raw 0.4467 (excess over null is only 13.1%); +0.2476 = 61.6% of the
   raw 0.4018 (excess 38.4%). The +0.3880 -> +0.2476 "large shift from
   one added site" is exactly this: the preserved component is a
   function of WHICH sites are pooled, so adding site 54 (rho +0.338,
   whose delta/e rank distributions differ) redistributes it. A
   3-block-restricted permutation cannot produce a null centred on zero
   when the blocks themselves carry the signal - that is a structural
   property of the null, not a bug in either run.
2. Are they the same kind of null? NO. 49/65 = ASSOCIATION null
   (AGENTS sec4 label, in the code's own comment): shuffles pairings,
   preserves marginals and block structure, answers "does the pairing
   beat chance", and is NOT expected to centre on zero - its own
   center_note branch exists precisely to say "raw rho would overstate
   the effect; excess over null is the real result". 33/AA1c =
   RE-DERIVATION null: multiplies each unit's OWN observed interaction
   residuals by independent +/-1 and RE-FITS (wls_line; the single-point
   reduction under A1), answering "does the interaction exceed
   measurement noise"; the +/-1 symmetry makes the null distribution
   symmetric about zero by construction - demonstrated live on GB1
   (mean -0.0004, script 73) just as on MTHFR.
3. Therefore, per AA3a's own logic: I1's four-site PASS (gate_pass 1.0,
   p_one_sided 0.0009999) is evidence only for the association claim,
   with 61.6% of its raw pooled rho reproduced by its own null; it does
   NOT exercise the sign-flip instrument that produced the project's
   headline, so it cannot generalize as evidence for that instrument.
   That gap was exactly what AA1 was built to close, and AA1 now reports
   the same-instrument result on GB1 (centres zero; detection null at
   n=57, reported plain).
Verdict: PASS - mechanism identified (block-restricted permutation
retains site- and background-level covariance with only 3-4 blocks; the
retained component is the nonzero centre and moves when the site set
changes); the two nulls are NOT the same kind, which is the answer to
why I1 does not generalize. The four-site PASS is clean AS AN
ASSOCIATION claim at its stated excess (0.1542 over its null) and no
further.
Files created/modified: DEEPDIVE_LOG.md only.
Anything unexpected or worth flagging: (1) task49's stored gate_pass is
0.0 - the 3-site control FAILED its own pre-registered gate
(p_one_sided 0.1398) while the 4-site rerun passed; combined with the
null-centring issue this means the I1 result is sensitive to which sites
are pooled, which is disclosed here rather than smoothed over; (2) I
could not verify from disk WHICH branch script49's center_note printed
at runtime (null_sd is not stored in its CSV) - the code branch is
quoted, the stored null_mean values speak for themselves, and no claim
about its past stdout is made; (3) the two percentages above are
arithmetic on the quoted stored values (0.4466626167166524 etc.), shown
so a reader can re-derive them without trusting a summary.
---

## [AA5] — Distance caveat in writing (local vs distant epistasis scope limit)
Status: PASS (one paragraph written to data/processed alongside the group's other outputs, quoted verbatim below)
Time started / finished: 2026-09-23 23:32 (after AA3) / 2026-09-23 23:32:17
What I did: Wrote AA5a's required paragraph (task doc lines 79-85) as
data/processed/task_AA5_distance_caveat.txt, alongside this group's
other outputs (task_AA1_*.csv, task_AA4_*.csv in the same directory).
It states plainly that passing a local-epistasis positive control does
not automatically license a claim about detecting DISTANT epistasis,
framed as a scope limitation on I1/AA1's result, not a flaw in either.
It uses only facts already established in this log or given by the task
itself (GB1 sites adjacent; MTHFR variants up to 200+ residues from
position 222; I1's association PASS and AA1's calibrated-but-underpowered
same-instrument run) - no new computation, no unverified structural
claim added.
Actual output (verbatim, the file's content):
```
Task AA5a (Group AA) -- the distance caveat, stated plainly.

GB1's four assayed sites (39, 40, 41, 54) are spatially adjacent on the
binding interface, so every interaction that I1 (scripts 49/65) and this
group's transplant (script 73, task AA1) put under test is a LOCAL one:
a fixed background residue and variants at neighbouring positions of the
same structural patch. MTHFR's variants, by contrast, sit up to 200+
residues from position 222, spanning catalytic and regulatory domains,
so the project's headline question asks whether a background mutation
couples to DISTANT sites -- a different physical mechanism (long-range
allosteric or domain-level coupling) than interface-local epistasis.
Passing a local-epistasis positive control therefore does not
automatically license a claim about detecting DISTANT epistasis: it
establishes only that the instrument can register local, tightly coupled
interaction where ground truth is strong, and says nothing about
sensitivity to coupling that must traverse the protein. This is a scope
limitation on the interpretation of I1's and AA1's results -- a boundary
on what they were capable of demonstrating -- not a flaw in either run,
and both results should be read inside that boundary.
```
Verdict: PASS - written as required, plain and explicit, and honest
about AA1's status (it does not lean on AA1's non-significant detection
as if it were a pass).
Files created/modified: data/processed/task_AA5_distance_caveat.txt
(NEW); DEEPDIVE_LOG.md.
Anything unexpected or worth flagging: nothing - this was a writing
task; the only judgment call was to phrase the caveat so it does not
overstate AA1 (whose detection result is a plain null), which the
paragraph's wording ("calibrated-but-underpowered") reflects.
---

## [AA6] — The ε=7.40-vs-5 discrepancy: RESOLVED (threshold identified)
Status: PASS (= AA6b's plain PASS: resolved, here is the threshold that explains it)
Time started / finished: 2026-09-23 23:33 (after AA5) / 2026-09-23 23:48:38
What I did: Checked disk first (the fetched full text and Fig 3 image
already existed from MIGRATION_LOG P2; its verbatim Methods quotes for
eq. (2), the detection limit and the three prose rules are at
MIGRATION_LOG lines 163-170). AA6a asks what Fig 3D ACTUALLY used, so I
fetched the authors' own released processing scripts —
https://github.com/wchnicholas/ProteinGFourMutants.git, shallow clone to
data/external/ProteinGFourMutants (supplementary-materials fetch within
the 200 MB Group-T-style budget: downloaded pack = 59,686,427 B
= 56.93 MiB, WITHIN cap; on-disk footprint after git inflation =
226 MB — both numbers disclosed; HEAD =
dbdd7639187e0b8f22359f404ce4d1d950fcc8a9, 2023-08-03; provenance logged
here per data/external convention). I then enumerated every documented
filter/threshold in the fetched Methods, grepped the same Methods for
replicate-exclusion rules, and ran AA6a's test twice on the raw
landscape file: (1) the Methods-PROSE pipeline (eq. 2 + the three
written rules), (2) an exact transcription of the released code path
(floor/epistasiscal/normalization copied line-by-line from
script/Heatmapping2.py — the scripts are Python 2 and were transcribed,
not executed; the transcription is validated below by reproducing BOTH
printed figure labels).
Identified filters/thresholds, verbatim where quoted:
 1. Read processing: `paired-end reads for each input library and
    post-selection library such that the average coverage for each
    variant would be more than 100 paired-end reads` (coverage target),
    plus paired-end codon-consistency discards (first-3-nt check).
 2. Read-count threshold: `Variants with countinput<10 were filtered to
    reduce noise.` / missing = `fewer than 10 sequencing read counts in
    the input library` (those 10,639 = 6.6% imputed for the full
    landscape; grey = missing in Fig 3).
 3. Detection limit + three prose rules (MIGRATION_LOG verbatim):
    `the detection limit of fitness (w) in this system is ~0.01 (Olson
    et al., 2014)`; `Rule 1) if max(wab/wBG, wa/wBG, wb/wBG) < 0.01,
    εadjusted = 0`; `Rule 2) if min(wa, wb, wa/wBG, wb/wBG) < 0.01,
    εadjusted = max(0, ε)`; `Rule 3) if min(wab, wab/wBG) < 0.01,
    εadjusted = min(0, ε)`.
 4. Replicate-exclusion rules: NONE EXIST — grepping the fetched full
    Methods for "replic*" returns exactly one hit ("Replication", a
    citation context); there is no per-variant replicate-exclusion rule
    to apply. Only global reproducibility stats are reported.
 5. THE MOVING THRESHOLD (from the released scripts, not in the Methods
    prose) — script/Heatmapping2.py:10-13 and 119-131, applied at
    157-160:
    `def floor(fit):`
    `  if fit == 'NA': return 'NA'`
    `  elif float(fit) < 0.01: return 0.01`
    `  else: return float(fit)`
    `varm1fit = floor(varm1rawfit)/floor(varfit)` (bg-normalized singles)
    `absepi = float(dfit) - floor(var1fit*var2fit)`
    `relepi = float(floor(dfit))/floor(var1fit*var2fit) #Relative Epistasis model (default)`
    `epihash[bg][mut] = log(varrelepi)`   <- epsilon is ln(relepi)
    i.e. EVERY term, INCLUDING THE MULTIPLICATIVE EXPECTATION
    (product of the two background-normalized single-mutant fitnesses),
    is clamped UP to the 0.01 detection limit.
Actual output (verbatim, run 1 — Methods-PROSE pipeline on the raw
landscape, IL cycle of Fig 3D):
```
FILE full-precision values:
  w_BG=ILGV 0.5464932816529999
  w_a=ILLV 0.0197019843818
  w_b=ILGH 0.0138472164977999
  w_ab=ILLH 0.816549435906
  eps_raw (eq.2, ln(w_ab*w_BG/(w_a*w_b))) = 7.399806
  Rule1 cond max(ratios)=1.494162 <0.01? False
  Rule2 cond min(wa,wb,ra,rb)=0.013847 <0.01? False
  Rule3 cond min(wab,r_ab)=0.816549 <0.01? False
  eps_adjusted = 7.399806   -> equals 5.0? False
Read-count threshold: file columns = [sequence, fitness]; count_input NOT present -> per-genotype application impossible on this file.
  BUT the paper's Fig 3D itself prints a fitness for all four cycle genotypes (0.55/0.02/0.01/0.82),
  i.e. all four PASSED the count_input>=10 filter (filtered/imputed variants are grey='missing' in Fig 3C-D).
  -> the documented read-count filter cannot alter any input of this cycle.
From figure's PRINTED fitnesses: eps = 7.720905 (still not 5.0)
  value of w_b needed for eps=5: 0.152611 (file has 0.013847, figure prints 0.01)
  value of w_a needed for eps=5: 0.217136 (file has 0.019702, figure prints 0.02)
  value of w_ab needed for eps=5: 0.074090 (file has 0.816549)
  value of w_BG needed for eps=5: 0.049586 (file has 0.546493)
Any single-value substitution that lands on 5.0 would have to replace a documented measured value by 6-16x a different number;
no documented threshold/rule does that.
```
Actual output (verbatim, run 2 — exact transcription of the released
CODE path, both Fig 3D cycles):
```
IL: BG=ILGV a=ILLV b=ILGH ab=ILLH
  normalized: s1=0.036052 s2=0.025338 d=1.494162
  product of singles: raw=0.00091349 -> floor()=0.010000  [floor FIRES]
  relepi = 149.416189 -> code eps = ln(relepi) = 5.006736
  eq.(2) un-floored eps = 7.399806
  figure prints: 5  -> code path matches: True
WL: BG=WLGV a=WLLV b=WLGH ab=WLLH
  normalized: s1=74.149898 s2=1.390260 d=1.149957
  product of singles: raw=103.08763637 -> floor()=103.087636  [floor no-op]
  relepi = 0.011155 -> code eps = ln(relepi) = -4.495855
  eq.(2) un-floored eps = -4.495855
  figure prints: -4.5  -> code path matches: True
Verdict computation: the ONLY difference between Methods-prose (7.399806) and the
figure's printed epsilon is floor() applied to the expected-double product term.
EXIT=0
```
Verdict: PASS (AA6b: resolved). The threshold that moves the re-derived
7.399806 to 5.0 is the authors' own floor() clamp at the 0.01 detection
limit applied to the MULTIPLICATIVE EXPECTATION TERM inside
epistasiscal (script/Heatmapping2.py:125), which the Methods' three
prose rules do not describe: for the IL cycle every individual genotype
is >= 0.01 (Rule 2's min is 0.013847, so all three prose rules evaluate
False and the prose pipeline gives 7.399806), but the product of the
two background-normalized singles is 0.00091349 < 0.01, gets floored to
0.01, and ln(1.494162/0.01) = ln(149.416189) = 5.006736 -> the figure's
printed "5". The WL cycle's product (103.09) never hits the floor, so
the code path and eq. (2) agree there: -4.495855 -> printed "-4.5".
Both printed labels of Fig 3D are now reproduced exactly by one
consistent mechanism. CONTRADICTION LOGGED BOTH WAYS (AGENTS sec 5):
Methods prose as written -> 7.399806; released scripts as written ->
5.006736; the figure matches the SCRIPTS. Public-facing guard: any
citation of "ε = +5" must be attributed to the floor-clamped code path,
never to eq. (2) applied as the Methods prose describes it — and
"+7.399806" is what the unclamped data/formula give.
Files created/modified: data/external/ProteinGFourMutants (NEW fetch,
provenance as above); DEEPDIVE_LOG.md. No repo scripts modified; no
existing results modified.
Anything unexpected or worth flagging: (1) the discrepancy's cause was
in the CODE, not the Methods — i.e. the published prose alone could
never have produced the published figure label (this is the substantive
finding, not a rounding issue); (2) git working-tree footprint (226 MB)
exceeds the 200 MB figure even though the actual downloaded bytes
(59,686,427) are within the fetch cap — both disclosed, repo retained as
data/external evidence and deletable on request; (3) the released
scripts are Python 2 EOL — transcribed verbatim for the run rather than
executed (disclosed); the transcription is corroborated by reproducing
both figure labels; (4) the read-count filter is untestable per-genotype
from the shipped landscape (no count_input column), but is provably
non-operative for this cycle because Fig 3D prints fitnesses for all
four genotypes.
---

## [AA7] — Second positive control: GRB2 pairwise DMS (non-GB1), AA1 transplant re-run
Status: PASS (executed end-to-end; centreing REPLICATES AA1's YES; the
detection half now SURVIVES at n=689 where AA1's n=57 was a plain null)
Time started / finished: 2026-09-23 23:50 (reconnaissance right after
AA6) / 2026-09-24 00:16:31
What I did: Read AA7's exact text (task doc lines 100-105). AA7a branch
executed FIRST: checked Group AB's results against the ProteinGym
catalog -- `includes_multiple_mutants values: {False: 148, True: 69}` /
`assays WITH multiple mutants: 69` (data/external/ProteinGym/
DMS_substitutions.csv, copied verbatim from the AB1 fetch, md5
c434631737013fceb56efc98056151e0; reference_files_description.md lines
12-13 define the columns) -> ProteinGym DOES supply double-mutant
assays, so the "only if it doesn't" EXTERNAL SEARCH branch was NOT
triggered (no web search done -- disclosed). AMBIGUITY LOGGED (most
literal reading): the happy path does not re-state
pre-register+execute; it is read as applying regardless, because the
task title ("a second, independently sourced positive control") can
only be satisfied by running the control. Excluded the two GB1
derivatives from the catalog by sequence evidence BEFORE writing the
script: SPG1_STRSG_Olson_2014 region 228-282 =
"QYKLILNGKTLKGETTTEAVDAATAEKVFKQYANDNGVDGEWTYDDATKTFTVTE" (GB1's B1
domain itself, NGVDG motif present) and SPG1_STRSG_Wu_2016 region
265-280 = "VDGEWTYDDATKTFTV" (= GB1 positions 39-54; 76 singles =
4x19 confirms Wu's four-site library on the precursor). Wrote
scripts/74_second_double_mutant_control.py (next free number after
71/72/73) with the FULL AA1 methodology pre-registered in its
docstring before any run: selection ladder S1-S7 (rank by
DMS_number_multiple_mutants desc; per-member cap 60,000,000 B;
cumulative script cap 120,000,000 B; structure gates seq_len<=1022,
schema, row length, label parse <=1% unparseable, WT-letter
positional gate, >=50 exact doubles, >=50 partners post-join),
background = most-frequent substitution among exact doubles
(count-based fitness-blind, lexicographic tie-break), partners = all
singles with the exact {s, bg} double row (NO fitness filter), plus
AA1's adaptations A1-A6 carried verbatim and three new ones declared
A7 (WT anchor: zero-mutation row if present, else fixed pre-run
c-hat = median f(v+bg)/f(v)), A8 (count-based background, no chemical
parallel to A222V), A9 (partner spread printed). Ran smoke
(N_PERM=200): ladder worked but gate S4d REJECTED the top fetchable
candidates because my delimiter list ("_","-","+") did not match the
real label format -> script stopped at its own 120 MB cap with exit 2
(BLOCKED, as pre-registered). Diagnosed fitness-blind from the cached
members (mutant column only): every failed label's only non-alnum
character is ":" (GRB2 first failures 'T159M:D166V','T159F:G203C',...
census {':': 62332}; Sarkisyan 'K3R:V55A:Q94R:A110T:D117G:M153K:D216A',
census {':': 148833}). Fixed by ADDING ":" to the delimiter list --
POST-HOC BUG FIX, DISCLOSED in the script's own startup print and
here: the gate, its <=1% threshold, the ranking and the ladder are
unchanged, and no fitness value was involved (AGENTS sec 6). Re-ran
smoke (N_PERM=200, EXIT=0, 24.6s) and the full run
(N_PERM=10000, EXIT=0, 26.5s). Also corrected, post-run and
disclosed: (a) the startup disclosure line originally said the
Sarkisyan member was "reused" -- it was NOT (GRB2 won at the higher
rank; string fixed, no statistic touched); (b) the limitations
"scale references" line had printed AA1's p as "0.7405-ish" FROM
MEMORY -- verified against task_AA1_gb1_signflip_nulls.csv:
signed p = 0.3849 (also quoted in the [AA1] log entry); string fixed
to 0.3849 with the correction embedded in the script; no statistic of
this run depends on that line. During this task the closeout Z2a
background job completed (notification received; handled per priority
rules AFTER this entry -- deepdive keeps priority).
Actual output (verbatim; full run, N_PERM=10000):
```
Catalog gate PASSED: 217 assays, md5=c434631737013fceb56efc98056151e0
S1/S2: 67 candidates with multiple mutants after excluding the 2 GB1 derivatives (SPG1_STRSG_Olson_2014, SPG1_STRSG_Wu_2016); ranked by multi-mutant count desc
Central directory parsed: 217 members (87428 B fetched so far)
[rank 0] HIS7_YEAST_Pokusaeva_2019: reject -- member csize 392771199 > per-member cap 60000000
[rank 1] PHOT_CHLRE_Chen_2023: reject -- member csize 135448665 > per-member cap 60000000
    member GRB2_HUMAN_Faure_2021.csv: CACHED on disk (122246831 B, 0 network bytes) (rank: 62332 multi-mutants)
[rank 2] GRB2_HUMAN_Faure_2021: accept -- 63366 rows, 62332 exact doubles, 0 unparseable dropped
    -> bg (S5): (208, 'G') appears in 691 exact doubles among 1033 countable candidates | partners with both arms (S6): 689
SELECTION FROZEN -- structural counts only; no fitness value has been read or printed for any candidate (DMS_score loaded only now, second pass)

SELECTED: GRB2_HUMAN_Faure_2021 (Faure 2022), seq_len=217, region 159-214, 1034 singles / 62332 multi in catalog
Background (S5, count-based fitness-blind): position 208 N->G (B208G), present in 691 exact doubles
Partners (S6): n=689 over 53 positions; distance from bg position: min=1, median=27, max=49 (A9 -- local/distant mix printed, not hidden)
Frozen structural fingerprint: struct rows in member = 63366, exact doubles = 62332, unparseable dropped = 0
WT-anchor branch A7b: no zero-mutation row in the scores file (as verified on the MTHR file) -> c-hat = median f(v+bg)/f(v) = 0.855271 over 689 partner rows
f(bg) = 0.082048  [first read of this value, S5 was frozen before this line]
e.b analog: n=689 | mean=+0.0305 median=+0.0433 | min=-0.5485 max=+0.5694
Non-positive-value counts (A4: kept, never filtered): single arm 567, double arm 474, expectation 567 of 689
Loading ESM-2 t33 650M on mps...
Scored 106 forward passes -> 689 delta values
delta_ESM analog: mean=+0.0140 median=-0.0132 min=-0.8050 max=+1.4217
SANITY CHECKS (script 33's, transplanted: test the test first)
  all-+1 flips reproduce own_e_b exactly: max|diff|=0.000e+00
  all--1 flips give exactly -own_e_b:     max|diff|=0.000e+00
Design summary for AA2 (unit of analysis):
  rows=689 | flip units (cells)=689 (one +/-1 per variant, A5) | partner positions=53 | backgrounds=1 | MTHFR contrast: 10,757 variants x 4 conc cells = 43,028 cells, 654 positions | AA1 contrast: 57 rows, 3 sites, 1 background
NULL 1 -- SIGN-FLIP RE-DERIVATION (10000 permutations)
  signed delta_ESM vs signed e_b
    observed=+0.1153  null mean=-0.0003 sd=+0.0371  p=0.0019
    excess over null=+0.1156  (-0% of the raw value is structural artifact)
    -> SURVIVES
    null-centring check: null mean IS consistent with zero -- machinery behaving
    PRE-REGISTERED READS: instrument behaves = YES; detects established epistasis = YES (signed two-sided p < 0.05); AA1's GB1 centreing answer was YES -- replication question answered by the line above
  absolute |delta_ESM| vs |e_b|
    observed=-0.0272  null mean=-0.0272 sd=+0.0000  p=1.0000
    excess over null=+0.0000  (100% of the raw value is structural artifact)
    -> does NOT survive
    STRUCTURAL NOTE (pre-registered from AA1's disclosed post-hoc finding): with ONE cell per variant, |flip * r| = |r| is invariant to the sign flips ... DEGENERATE here, carries no information.
NULL 2 -- SITE-BLOCK PERMUTATION (weaker; association only; A6: 53 blocks)
    observed=+0.1153  null mean=+0.0004 sd=+0.0457  p=0.0108
Saved: .../task_AA7_second_control_eb.csv (689 rows), .../task_AA7_second_control_nulls.csv (3 rows)
Elapsed: 26.5s | N_PERM=10000 | SEED=0
EXIT=0
```
Failed-gate smoke run output (verbatim, first run 00:08, exit 2 --
logged because the hard rule requires logging exact mismatches, not
hiding them):
```
[rank 2] GRB2_HUMAN_Faure_2021: reject -- 62332/63366 labels unparseable (> 1%)
[rank 3] GFP_AEQVI_Sarkisyan_2016: reject -- 50630/51714 labels unparseable (> 1%)
BLOCKED: cumulative fetch 125319370 B > cap 120000000
EXIT=2
```
Verdict: PASS. Both halves of the pre-registered decision rule are
answered, untuned: (1) INSTRUMENT CENTRES ON ZERO -- null mean
-0.0003 sd 0.0371 passes script 33's exact expression at N_PERM
10000, so AA1's centreing YES REPLICATES on an independent,
non-GB1 dataset (this was AA7's core question); (2) DETECTION SURVIVES
-- signed rho(delta_ESM, e_b) = +0.1153, p = 0.0019 (permutation p,
primary), excess over null +0.1156 (~0% structural artifact), Null-2
association p = 0.0108. Contrast that carries the result: AA1/GB1 ran
the same instrument at rho +0.1222 with p = 0.3849 (n=57, PLAIN NULL,
underpowered) while here at n=689 / 53 partner positions the same
methodology detects -- i.e. the transplant's null behavior (AA1) and
its power when structure is present (AA7) are BOTH demonstrated, which
is what a positive control is for. Limitations carried in the script's
output: single background (N208G, count-rule choice with no chemical
parallel to A222V, A8); A7b c-hat = 0.855271 replaces AA1's exact
f(WT)=1.0 (ProteinGym ships no zero-mutation row -- verified on the
MTHR file); the scale has negative values (567/689 non-positive
single arms kept by A4, expectations inherit their sign); partner
distances 1-49 (local/distant mix, A9 -- not a purely local control);
absolute sign-flip null degenerate by construction (pre-registered);
p-precision from 10,000 draws over 689 flip units nested in 53
positions, not from 689 independent sites (AA2 rule).
Files created/modified: scripts/74_second_double_mutant_control.py
(NEW); data/external/ProteinGym/DMS_substitutions.csv (copy of AB1's
fetched file for reproducibility, md5 c434631737013fceb56efc98056151e0);
data/external/ProteinGym/members/GRB2_HUMAN_Faure_2021.csv (fetched
49,594,484 network bytes, 122,246,831 decompressed, md5
e6730c414e8563050837b06ad165c4bf; source:
https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/
zero_shot_substitutions_scores.zip member GRB2_HUMAN_Faure_2021.csv)
and members/GFP_AEQVI_Sarkisyan_2016.csv (fetched 41,507,707 network
bytes, md5 c48a79411b83a37a89f2e004c77bda73, CACHED BUT UNUSED --
GRB2 won at the higher rank; kept as fetched evidence, deletable on
request); data/processed/task_AA7_second_control_eb.csv (689 rows);
data/processed/task_AA7_second_control_nulls.csv (3 rows);
DEEPDIVE_LOG.md. No existing script or result was modified.
Anything unexpected or worth flagging: (1) The label-format bug --
the pre-registered delimiter list was written without ever displaying
a real multi-mutant label; gate S4d caught it exactly as designed and
the fix is disclosed as post-hoc (no threshold, ranking or statistic
changed). (2) FETCH ACCOUNTING: smoke run 1 125,319,370 B = central
dir 87,428 + GRB2 49,594,484 + Sarkisyan 41,507,707 + one further
member 34,129,661 that was fully downloaded but DISCARDED when the
script's own 120 MB cap fired (WASTED); smoke 2 and full run 87,428 B
each (central dir only, both members cached). Session fetch totals:
prior AB fetches ~11 MB (as recorded in the AB entries; verifiable
components: MTHR member csize 9,650,420 B, DMS_substitutions.csv
208,734 B, MTHR a2m 3,316,659 B) + AA6 paper-repo pack 59,686,427 B +
AA7 125,494,226 B = ~196.3 MB. The 200 MB cap's per-fetch-vs-
cumulative wording is ambiguous: logged assumption = per-fetch (the
reading AA6 applied to the 59.7 MB pack); under the stricter
cumulative reading the session is at ~196.3/200 MB, so NO further
member fetch will be initiated without a user decision. (3) Two
post-run string corrections in script 74 (Sarkisyan "reused" ->
"NOT reused"; AA1 p "0.7405-ish" -> verified 0.3849 from the AA1
nulls CSV) -- both are disclosure/reference lines only; no statistic
of either run changed, and the wrong AA1 p DID appear in the smoke-2
and full-run stdout (corrected here and in the script for any future
run). (4) Closeout Z2a's background job completed mid-task (exit 0,
PHASE2_MAX=75 smoke, phase-3 measured 25,393 s ~ 7.05 h); its
entries and the z2_backup restore follow under the closeout rules,
after deepdive work, per priority.
---

## [AC1] — Reconcile the 150M vs 650M CI widths
Status: PASS (every element of AC1a executed; all three of the evaluator's
predicted numbers confirmed — implied n_eff ≈ 200 / ≈ 4,500 and design
effect ≈ 2.3 — and the clustering question answered from code, not from
convention)
Time started / finished: 2026-09-24 00:33:33 / 2026-09-24 00:41:37
What I did: Located both CI figures' provenance before computing anything.
(a) The "150M: 0.136" half-width is script 58's (J2a-3) PRIMARY
`Spearman(delta_150M, delta_650M)` run — quoted verbatim below from
SESSION_LOG L1925-1937 (the [U1] entry's verbatim block; `grep -n "^##"`
run on SESSION_LOG first, as required). IMPORTANT: this is the
CROSS-MODEL delta-agreement statistic — the project has NO 150M
delta-vs-e.b CI, so the two half-widths are not the same quantity measured
twice (see Verdict). (b) The "650M: 0.029" half-width is the
`primary,"signed, own e_b"` row of `data/processed/task32_delta_esm_primary.csv`
(full precision, quoted below), written by `scripts/32_delta_esm_primary.py`
— a DIFFERENT file from the never-touch stray `32_delta_esm_noise_floor.py`
(both numbered 32; the stray writes `task_delta_esm_noise_floor.csv` and
computes no CI — both files read, neither modified). Reported the 150M
run's exact n: **1,900 variants over 100 positions** (seed-0 N_POS=100
sample of the 655-position atlas, 19 substitutions/position, all 1,900
matched to the cached 650M deltas, floor gate `min(500, 0.85*19*100=1615)
= 500` passed; N_BOOT=2000 env default, SEED=0). Computed implied
effective n from each CI half-width with the Fisher-z back-of-envelope
`n_eff = (1.96/w)^2 + 3` (stated assumption: |rho| ≤ 0.10 so z-space ≈
rho-space and the percentile CI is near-symmetric — the same
back-of-envelope the task's own "~200"/"~4,500" used). Confirmed the
650M bootstrap's position clustering EXPLICITLY IN CODE (AC1's requirement
— no guessing), and computed the design effect = raw n / implied n_eff.
Actual output (verbatim):
150M run (SESSION_LOG L1925-1937):
```
J2a-3  ESM-2 150M model check (proposal pre-registered model)
sequence len 656; atlas positions 655
sampled N_POS=100 positions (seed 0); 222 in sample: False
Loading esm2_t30_150M_UR50D (weights downloaded and cached this run)
Using device: mps
  100/100 positions (81s elapsed)
scored rows: 1900; unmatched to cached 650M delta: 0
matched for PRIMARY: 1900 substitutions, 100 positions
PRIMARY Spearman(delta_150M, delta_650M): rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540 n=1900 pos=100
  bands: CI_lo=-0.0444  ->  VERDICT: SIZE-SENSITIVE
SECONDARY (descriptive) sign agreement: 53.11% of 1900 rows (exact-zero ties excluded: 0)
SECONDARY (descriptive) score rho wt bg: +0.4157 (n=1900)
SECONDARY (descriptive) score rho a222v bg: +0.4098 (n=1900)
```
650M CI source row (`cat data/processed/task32_delta_esm_primary.csv`):
```
primary,"signed, own e_b",-0.08811806424891734,-0.1173334458953319,-0.05951138449511738,0.0,10757.0,False,
```
Clustering confirmation (code, quoted):
```
scripts/32_delta_esm_primary.py:46: from scripts.lib.stats import position_cluster_bootstrap, _spearman
scripts/32_delta_esm_primary.py:48: N_BOOT = int(os.environ.get("N_BOOT", 10000))
scripts/32_delta_esm_primary.py:101:     r = position_cluster_bootstrap(sub, "position", xc, yc,
scripts/32_delta_esm_primary.py:102:                                        n_boot=N_BOOT, seed=SEED)
scripts/lib/stats.py:3: Inference is by CLUSTER bootstrap, resampling positions rather than rows:
scripts/lib/stats.py:4: up to 19 substitutions share a position and are not independent, so
scripts/58_j2a_proposal_checklist.py:64: N_BOOT = int(os.environ.get("N_BOOT", 2000))
scripts/58_j2a_proposal_checklist.py:271:     prim3 = position_cluster_bootstrap(d, "position", "delta150", "delta650",
scripts/58_j2a_proposal_checklist.py:272:                                        n_boot=N_BOOT, seed=SEED)
```
Arithmetic (inline `venv/bin/python3`, code and output verbatim):
```
# inputs: lo150,hi150 = -0.0444,0.2275 (script-58 print, 4 dp)
#         lo650,hi650 = -0.1173334458953319,-0.05951138449511738 (task32 CSV)
# w = (hi-lo)/2 ; n_eff = (1.96/w)**2 + 3 ; DEFF = raw_n / n_eff
150M: half-width w = 0.13595  -> implied n_eff = 210.9   (raw n=1900, pos=100)
650M: half-width w = 0.02891103  -> implied n_eff = 4599.1   (raw n=10757, 654 positions)
design effect (raw/eff)  650M = 2.339   150M = 9.01
clustered CI vs iid CI (650M): half-width 0.028911 vs iid 0.018900 -> ratio 1.530 (=sqrt(DEFF) 1.529)
```
Verdict: **PASS.** (1) Exact n of the 150M run: **1,900 rows, 100
positions, N_BOOT=2000** — reported with its verbatim output. (2) Implied
effective n: **210.9 ≈ "~200"** (150M) and **4,599 ≈ "~4,500"** (650M) —
both of the evaluator's figures confirmed. (3) The 650M bootstrap DOES use
position clustering — confirmed from the source (`position_cluster_bootstrap`
imported by `32_delta_esm_primary.py` and called with `cluster_col="position"`
on the primary rows; lib docstring states the cluster-by-position rationale;
its implementation resamples unique positions with replacement), so AC1's
possible-bug branch does NOT trigger; nothing here is a guess. (4) Design
effect = **10,757 / 4,599 = 2.34 ≈ "~2.3"** — the numbers check out, and
this is exactly what a properly conservative clustered CI looks like: the
CI is 1.53× wider than an iid-at-raw-n CI would be (0.0289 vs 0.0189),
i.e. the within-position dependence the project's convention protects
against inflates variance by only ~2.3×. Honest scope note (AGENTS §5):
the two half-widths quantify DIFFERENT statistics on different samples —
150M's is cross-model delta agreement (n=1,900/100 clusters), 650M's is
delta-vs-own_e_b (n=10,757/654 clusters) — so the reconciliation is
mechanical (sample size + clustering fully explain the width difference);
the widths are not two estimates of one common quantity and must not be
presented as such.
Files: DEEPDIVE_LOG.md (this entry). Read-only: `scripts/32_delta_esm_primary.py`,
`scripts/32_delta_esm_noise_floor.py` (stray — untouched), `scripts/58_j2a_proposal_checklist.py`,
`scripts/lib/stats.py`, `data/processed/task32_delta_esm_primary.csv`,
`data/processed/task58_150m_check.csv`, `docs/tasks/comparators-and-consolidation/SESSION_LOG.md`,
`docs/tasks/review-triage/OVERNIGHT_LOG.md`. No new files; no new script
(the arithmetic ran inline and is quoted above, reproducible as-is).
Unexpected: (1) "the 150M CI" is a cross-model agreement CI, not a
delta-vs-e.b CI — flagged above so the reconciliation is not misread as
like-for-like. (2) Two different scripts carry number 32
(`32_delta_esm_primary.py` writes the CI CSV; `32_delta_esm_noise_floor.py`
is the never-touch stray) — both read to establish which produced what;
neither modified. (3) The 150M design effect (9.01) is far larger than
650M's (2.34) — consistent with much stronger within-position dependence
in cross-model agreement, but the two DEFFs belong to different statistics;
both reported plainly, not merged into one story. (4) The task's "0.029"
is the 4-dp rendering of the exact 0.02891103 half-width — exact endpoints
used throughout; conclusions identical either way.
---

## [AC2] — Direct 150M-vs-650M agreement, not just sign agreement
Status: PASS (both correlations computed from the saved per-variant table
with column-identity checks first, position-cluster CIs added for both,
and the evaluator's proposed reading stated plainly below with the one
magnitude correction the numbers require)
Time started / finished: 2026-09-24 00:41:37 / 2026-09-24 00:43:42
What I did: Read AC2's exact text (task doc L168-176). AC2a's two inputs
are both already on disk in `data/processed/task58_150m_check.csv`
(1,900 rows: `score150_wt`, `score150_bg`, `delta150`, `delta650`,
`esm2_score`, `esm2_score_a222v_bg`) — no scoring run needed. Before
reporting any agreement, ran the column-identity checks (AGENTS §5):
delta150 ≡ score150_bg − score150_wt (max|diff| 3.553e-15), delta650 ≡
esm2_score_a222v_bg − esm2_score (max|diff| 1.110e-16), and cross-source
delta650 vs the cached phase-5 `delta_esm` on hgvs_pro (matched 1,743/1,900
with non-NaN cached values, max|diff| = 0.000e+00 — exact). Then computed
Spearman(delta150, delta650) and Spearman(score150_wt, esm2_score) on the
same 1,900 variants with `position_cluster_bootstrap` from
`scripts/lib.stats` at script-58's own settings (n_boot=2000, seed=0) —
plus the A222V-bg score pair for context and the sign-agreement baseline.
Actual output (verbatim; inline `venv/bin/python3`, code quoted in the log
— the printed label "delta_655M" is a typo for "delta_650M" in my f-string
only; the columns used are `delta150`/`delta650` as shown in the code, no
statistic affected):
```
rows=1900 positions=100
identity  delta150 = score150_bg-score150_wt : max|diff| = 3.553e-15
identity  delta650 = esm2_bg-esm2_score      : max|diff| = 1.110e-16
cross-src delta650 vs cached phase5 delta_esm: matched 1743/1900, max|diff| = 0.000e+00
delta_150M-vs-delta_655M             rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540 n=1900 pos=100
raw WT-bg score, 150M-vs-650M        rho=+0.4157 CI=[+0.2658,+0.5514] p=0.0000 n=1900 pos=100
raw A222V-bg score, 150M-vs-650M     rho=+0.4098 CI=[+0.2589,+0.5459] p=0.0000 n=1900 pos=100
sign agreement: 53.11% of 1900 rows
```
```
# code (inline, verbatim):
r_delta = position_cluster_bootstrap(d, "position", "delta150", "delta650", n_boot=2000, seed=0)
r_wt    = position_cluster_bootstrap(d, "position", "score150_wt", "esm2_score", n_boot=2000, seed=0)
r_a222v = position_cluster_bootstrap(d, "position", "score150_bg", "esm2_score_a222v_bg", n_boot=2000, seed=0)
```
Cross-check against script 58's own printed values (SESSION_LOG L1933-1937):
its `rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540`, `sign agreement: 53.11%`,
`score rho wt bg: +0.4157`, `score rho a222v bg: +0.4098` all re-derive
EXACTLY here (same lib function, seed, n_boot, data and row order) —
reproduction of the plumbing, not replication (AGENTS §6); the position-
cluster CIs on the two score correlations are NEW (script 58 printed those
two as descriptive point estimates only).
The two numbers AC2 asks to report, side by side:
```
(1) correlation of the two models' deltas:       rho = +0.0978 CI=[-0.0444,+0.2275] p=0.1540
                                                 (sign agreement 53.11% ~= chance 50%)
(2) correlation of raw WT-bg scores:             rho = +0.4157 CI=[+0.2658,+0.5514] p<0.0005
```
Verdict: **PASS.** Stated plainly as the evaluator's proposed reading
requires: the two checkpoints' raw WT-background scores agree substantially
(rho = +0.416) while their background-response deltas do not (rho = +0.098,
CI covering zero, p = 0.154; sign agreement 53.11% ≈ chance) — **the
background-response signal (delta) is not a stable property of the model
family as tested; that is a finding in its own right, not merely a caveat
on 11.1.** One magnitude correction, reported rather than smoothed: the
premise's example strength ("WT scores agree strongly, rho ~0.8") is not
what the data show — WT-score agreement is moderate (+0.416, CI
[+0.266, +0.551]); the contrast that carries the reading is that the delta
correlation is ~4.3× smaller and statistically indistinguishable from zero
while the WT-score CI excludes zero by a wide margin. Scope limits,
stated: only two checkpoints were compared (ESM-2 150M vs 650M — one
family, two sizes), so "model family" here means stability across size
within ESM-2 masked marginals; cross-family stability is AC4's question,
which remains BLOCKED (disk, see [AC4]); n = 1,900 variants over the
pre-registered 100-position sample; all CIs position-clustered.
Files: DEEPDIVE_LOG.md (this entry). Read-only: `data/processed/task58_150m_check.csv`,
`data/processed/phase5_analysis_table.csv`, `scripts/lib/stats.py`
(imported, not modified), SESSION_LOG. No new files; no new script (the
computation ran inline and is quoted above).
Unexpected: (1) AC2 needed no scoring run — script 58 had saved the full
per-variant table including both models' raw scores; only the CIs on the
score correlations were missing. (2) The delta650↔cached-delta_esm cross
match covers 1,743/1,900 rows (the remainder have no non-NaN cached
value); identity is exact wherever it matches — no discrepancy. (3) My
own print label typo "delta_655M" — disclosed inline; columns correct.
---

## [AC3] — Numerical precision check: fp32/fp64/batch/CPU rescore of delta_ESM
Status: PASS (AC3a executed with code-verified producer facts; AC3b executed
across all four pre-registered conditions at n=500 with G1 + coverage gates
passed and R1/R2 PASS in every arm — delta_ESM reproduces to the precision
the finding needs, so the mundane-numerical-precision explanation for 11.1's
instability is ruled out at the pre-registered precision). Five run attempts
and three machinery bugs occurred; every one is disclosed below and in the
script's own docstring (REVISION (1)-(5)) — none changed a threshold,
condition, N, subset convention, or decision rule.
Time started / finished: 2026-09-24 00:43:42 / 2026-09-24 09:08:47 (started immediately after
[AC2] was appended; wall-clock includes one user-interruption gap — session
timestamps jump from 00:49:58 to 07:07:20 — and the re-run attempts below;
attempt 3 ran 07:13:48–08:01:46, attempt 4 08:06:06–09:01:41, attempt 5
09:02:41–09:03:34, all date-printed).
What I did: Read AC3's exact text (task doc L178-187). (AC3a) Established
the original producer's settings FROM CODE, not assumption:
`scripts/10_score_all_variants_esm2.py:49` (WT background) and
`scripts/11_score_a222v_background_esm2.py:59` (A222V background) both call
`scripts.lib.esm_scoring.get_position_logprobs`, which runs ONE masked
sequence per `model()` call (lib L17-38) inside a loop over positions =>
ORIGINAL BATCH SIZE = 1; no `.half()/.bfloat16()/.double()/.float()` cast
exists anywhere in `scripts/*.py` or `scripts/lib/*.py` (grep this session)
=> ORIGINAL DTYPE = torch default float32; lib `get_device()` prefers mps
and the original runs printed "Using device: mps" => ORIGINAL DEVICE = mps;
`phase5_analysis_table.csv` (the delta_ESM source) is written by
`scripts/16_phase5_model_abc.py:124` from scripts 10/11's outputs.
Magnitudes read from `task_delta_esm_noise_floor.csv` plus a fresh
recompute on the analysis pool; the 11,344-vs-10,757 n discrepancy was
re-reconciled by re-merging `own_context_metrics.csv` (11,344 =
delta_esm non-null; 10,757 = delta_esm AND own_e_b, the primary-CI set that
position_cluster_bootstrap drops to). (AC3b) Wrote `scripts/75_...py` (next
free number; 74 = AA7) with ALL decision rules pre-registered in its
docstring before any rescore existed: subset = seed-0
`np.random.default_rng(0).choice(len(pool), size=500, replace=False)` over
the 10,757-row pool (script-67 L295-299 / script-58 L207-209 convention;
"a few hundred" read literally as 500 = script 58's matched-set floor);
conditions C0 = fp32/batch1/CPU (device isolation), C1 = fp32/batch8/CPU
(the task's literal ask), C2 = fp32/batch16/CPU, C3 = fp64/batch8/CPU;
gates G1 (batched path vs lib get_position_logprobs, max|diff| < 1e-5 or
STOP exit 1), R1 (max|delta_cond − delta_cached| <= 1e-3 nats = 2.1% of
median |delta| 0.0465, ~1,126× the 8.885e-07 rounding floor), R2 (paired
same-row |Spearman shift| <= 0.01, < 1/3 the published CI half-width
0.029), fp64 feasibility tiers (a/b/c at a 7,200-s projection cap) and an
fp32 arm-drop tier at the same cap. Ran smoke N=8 first (AGENTS §1), then
full N=500. Attempt history and the three machinery bugs — all fixed before
any threshold-adjacent quantity existed, all disclosed in the script
docstring REVISION (1)-(5): (i) attempt 1 was cut by the harness's
1,800,000-ms timeout with no output captured, because my smoke's
projection line had multiplied by len(smoke)=8 and was mislabeled "full" —
I mis-read "81 s" as the full-N projection when the real projection was
~2,526 s fp32 + ~3,125–3,587 s fp64 (~95–110 min total); the projection
target was corrected to canonical FULL_N=500 (same 7,200-s caps, same tier
decisions); (ii) the smoke also exposed that scoring one two-row batch per
variant never reached the labeled batch sizes (C1/C2 both effectively
batch-of-2 — their pairwise max|diff| was exactly 0.000e+00, the tell),
fixed before the full run by scoring whole blocks at the true batch size;
(iii) attempt 2's surviving tee'd log (mtime 02:26) ends after the three
fp32 arms completed and fp64 tier (a) printed — it was interrupted with the
session mid-fp64-arm and, values being memory-only, everything was lost —
per-chunk (100-variant) checkpointing + resume was added (machinery only),
with the resume machinery tested three ways before reuse (fresh run;
artificial suffix-NaN partial refill — refilled values bitwise-identical to
the originals; complete-arm skip); (iv) attempt 3 completed all data but
the N=8 smoke's stored fp64 tier (n=8) leaked into the 500-row run
(state.json refreshed sample_hgvs but not fp64_n on sample change), so its
fp64 arm ran only 8 of 500 rows while the run still printed a combined
PASS — caught by inspecting its own output (C3 printed
"|d-rho_base| = 0.3823" against the 500-row baseline and "n=8" in the
timing trace); fixes: sample mismatch discards state, stored tier/n is
validated against the current sample, the comparison print now shows the
paired same-row |d rho| and n_ok per condition, and a post-hoc COVERAGE
gate now blocks any verdict until every planned arm has its pre-registered
row count (gate can only block a false PASS; no threshold touched);
(v) attempt 4 then completed all four arms (n_ok 500/500 each) but the new
gate refused the verdict due to an unpack bug IN THE GATE (expected keys
built from (name, batch) tuples) — evidence within attempt 4's own output
(comparison block n_ok=500/500 for all four conditions) shows this was a
key-type bug, not missing data; fixed (`for name, _ in arms`). Attempt 5
is the authoritative run.
Actual output (verbatim). Authoritative attempt 5 (`N_RESAMPLE=500`,
09:02:41–09:03:34, EXIT=0), AC3a + gates:
```
AC3a -- delta_ESM magnitude (nats) and original producer settings:
  n reconciliation: delta_esm non-null = 11344  |  delta_esm AND own_e_b (primary-CI pool) = 10757 (654 positions)
  median |delta_ESM| (noise-floor file, n=11,344 set) = 0.046600006520749
  median |delta_ESM| (this pool, n=10757)          = 0.046466350555420
  sd(delta_ESM) = 0.118219919451489   sd(esm2_score) = 4.321855381741113
  float32 rounding floor eps*mean|score| = 8.885092e-07   sd/floor = 133054.2   frac |delta|<1e-4 = 0.001763
  ORIGINAL DTYPE = float32 (torch default; no .half()/.bfloat16()/.double()/.float()
    cast exists anywhere in scripts/*.py or scripts/lib/*.py -- grep this session)
  ORIGINAL BATCH SIZE = 1 (scripts/10:49 and scripts/11:59 call lib
    get_position_logprobs, which runs ONE masked sequence per model() call -- lib L17-38)
  ORIGINAL DEVICE = mps (lib get_device() prefers mps; original runs printed
    'Using device: mps')   producer of phase5_analysis_table.csv: scripts/16

SUBSET: 500 variants, 344 positions (default_rng(0).choice over the 10757-row pool, replace=False -- script-67/script-58 convention)
RESUME mode: checkpoint matches this sample (4 column(s), complete: ['C0_fp32_b1', 'C1_fp32_b8', 'C2_fp32_b16', 'C3_fp64_b8']; conditions/thresholds unchanged -- machinery only)
hgvs parse: fail=0  wt-vs-FASTA mismatch=0  var==wt=0
hgvs position vs table position mismatches: 0

Loading ESM-2 t33 650M (esm2_t33_650M_UR50D, cached -- no download)...

G1 identity gate (batched CPU fp32 vs lib get_position_logprobs, 10 variants x 2 ctx): max|diff| = 3.193e-06  (threshold 1e-5)
G1 PASS

TIMING SMOKE (fp32, batch 8, n=8): 1.770 s/variant -> projected C0+C1+C2 at full N=500 = 2655 s (cap 7200)
  C0_fp32_b1: already complete in checkpoint (resume) -- skipped
  C1_fp32_b8: already complete in checkpoint (resume) -- skipped
  C2_fp32_b16: already complete in checkpoint (resume) -- skipped

C3_fp64_b8: already complete in checkpoint (resume, n=500, tier a) -- skipped
```
Comparisons + gates (attempt 5, all conditions n_ok=500/500):
```
Spearman(delta_cached, own_e_b) on these 500 rows (baseline): rho = -0.0728   [full-set published: -0.088118, CI [-0.117333,-0.059511]]
  C0_fp32_b1: max|d-cached| = 1.132e-04  median = 1.094e-05 rmse = 2.451e-05 | rho(own_e_b) = -0.0728 n_ok = 500/500 | paired |d rho| vs cached on same rows = 0.0000 | rho vs cached = +0.999998 | R1 PASS (<=1e-3), R2 PASS (<=0.01)
  C1_fp32_b8: max|d-cached| = 1.122e-04  median = 1.078e-05 rmse = 2.445e-05 | rho(own_e_b) = -0.0728 n_ok = 500/500 | paired |d rho| vs cached on same rows = 0.0000 | rho vs cached = +0.999998 | R1 PASS (<=1e-3), R2 PASS (<=0.01)
  C2_fp32_b16: max|d-cached| = 1.122e-04  median = 1.078e-05 rmse = 2.445e-05 | rho(own_e_b) = -0.0728 n_ok = 500/500 | paired |d rho| vs cached on same rows = 0.0000 | rho vs cached = +0.999998 | R1 PASS (<=1e-3), R2 PASS (<=0.01)
  C3_fp64_b8: max|d-cached| = 8.940e-05  median = 9.645e-06 rmse = 2.055e-05 | rho(own_e_b) = -0.0729 n_ok = 500/500 | paired |d rho| vs cached on same rows = 0.0001 | rho vs cached = +0.999999 | R1 PASS (<=1e-3), R2 PASS (<=0.01)
  pairwise C0_fp32_b1 vs C1_fp32_b8: max|diff| = 7.629e-06
  pairwise C0_fp32_b1 vs C2_fp32_b16: max|diff| = 7.629e-06
  pairwise C0_fp32_b1 vs C3_fp64_b8: max|diff| = 1.050e-04
  pairwise C1_fp32_b8 vs C2_fp32_b16: max|diff| = 0.000e+00
  pairwise C1_fp32_b8 vs C3_fp64_b8: max|diff| = 1.038e-04
  pairwise C2_fp32_b16 vs C3_fp64_b8: max|diff| = 1.038e-04

==========================================================================
R1 (value, all conditions <= 1e-3): PASS
R2 (finding, paired |rho shift| <= 0.01): PASS
AC3 VERDICT: PASS -- delta_ESM reproduces under CPU/fp32/batch/fp64 changes to the precision the finding needs (G1+R1+R2).
==========================================================================
Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task_AC3_rescore.csv (columns: ['C0_fp32_b1', 'C1_fp32_b8', 'C2_fp32_b16', 'C3_fp64_b8'])
```
Defect-revealing excerpts from the earlier attempts (kept for the record —
none of these verdicts is the AC3 result):
```
attempt 2 log (ends here -- interrupted mid-fp64-arm, values memory-only, lost):
  C0_fp32_b1: 919.7 s total (1.839 s/variant)
  C1_fp32_b8: 937.7 s total (1.875 s/variant)
  C2_fp32_b16: 948.6 s total (1.897 s/variant)
TIMING SMOKE fp64 (batch 8, n=8): 7.174 s/variant (fp32 same-config 2.006 s/variant, fp64/fp32 = 3.58x) -> projected at full N=500 = 3587 s, at N=100 = 717 s (cap 7200)
  fp64 tier (a): FULL N
attempt 3 (stale-fp64_n bug -- C3 ran n=8; its printed PASS is void):
  fp64 tier: reusing stored decision from prior invocation (tier a, n=8) -- not re-decided
    C3_fp64_b8: 8/8 checkpointed @ 08:01:45
  C3_fp64_b8: max|d-cached| = 1.161e-05 ... | rho(own_e_b) = +0.3095 (|d-rho_base| = 0.3823) | rho vs cached = +1.000000 | R1 PASS ...
attempt 4 (data completed; gate's own unpack bug withheld the verdict):
STALE fp64 tier state (tier='a', n=8, len(sub)=500) -- discarding; tier will be re-decided (machinery fix, docstring REVISION (4))
  C3_fp64_b8: resuming from variant 8/500
    C3_fp64_b8: 108/500 checkpointed @ 08:18:29
    C3_fp64_b8: 208/500 checkpointed @ 08:29:12
    C3_fp64_b8: 308/500 checkpointed @ 08:40:28
    C3_fp64_b8: 408/500 checkpointed @ 08:51:34
    C3_fp64_b8: 500/500 checkpointed @ 09:01:41
  C3_fp64_b8: 3219.3 s this invocation (n=500)
COVERAGE FAIL (post-hoc guard): (rows run, pre-registered coverage) = {('C0_fp32_b1', 1): (0, 500), ('C1_fp32_b8', 8): (0, 500), ('C2_fp32_b16', 16): (0, 500)} -- conditions incomplete; NO verdict issued. Re-run to resume the incomplete condition(s).
```
Final CSV integrity (checked before logging): rows=500, positions=344,
C0/C1/C2/C3 notna = 500/500/500/500, any NaN = False.
Verdict: **PASS.** AC3a: median |delta_ESM| = 0.04660 nats (analysis pool:
0.0464664), sd = 0.11822 nats, float32 rounding floor = 8.885e-07 (signal
sd/floor = 133,054×; only 0.176% of |delta| fall below 1e-4); original
producer = **float32, batch size 1, device mps** (all three code-verified,
citations above — not assumed). AC3b: across the pre-registered 500-variant
subset (344 positions), delta_ESM reproduces under every perturbation —
CPU device change (vs original MPS), batch 1/8/16, and fp64 — with
max|delta' − delta_cached| = 8.94e-05 … 1.13e-04 nats, i.e. **0.19–0.24%
of the median effect and 101–127× above the rounding floor, 9–11× inside
the pre-registered 1e-3 R1 gate**; rank agreement vs cached ≥ +0.999998;
and the paired finding-level shift |Δrho(own_e_b)| ≤ 0.0001, i.e. **100×
under the 0.01 R2 gate and 290× under the published CI half-width 0.029**.
G1's implementation identity held at 3.193e-06 (3.1× inside its 1e-5
gate). Plainly: **numerical precision (dtype/batch/device) does NOT
explain 11.1's instability** — per AC3b's own text, had this failed,
"several downstream results would need re-running"; it did not fail, so
AC3 triggers no re-runs. Honest limits: (i) the subset baseline rho
(−0.0728, n=500) differs from the published −0.088118 (n=10,757) by
subset sampling alone — R2 is paired on the same rows precisely so this
cannot masquerade as rescore drift; (ii) C1 vs C2 are bitwise-identical
(0.000e+00) — on this CPU fp32 GEMM appears batch-invariant, so the
batch arm's finding is "batch size has zero effect here," which is still
the measured answer to the question asked; (iii) torch/fair-esm version
drift since the original MPS runs cannot be separated from the device
term (printed in the script's own LIMITATIONS); (iv) a resumed chunk
starts at the first NaN rather than a chunk boundary, so a handful of
rows at a resumed junction can sit in a differently-composed batch
(fp64 reduction-order effects ~1e-14, ~11 orders below the gate) —
disclosed in the docstring; (v) reproduction is not replication (AGENTS
§6): this validates that the estimator's values are stable, not that the
underlying biology/model claim is true.
Files: created `scripts/75_numerical_precision_rescore.py` (next free
number; next free is now 76) and its outputs
`data/processed/task_AC3_rescore.csv` (500×8) +
`data/processed/task_AC3_state.json`; run logs under the session temp dir
(`T/opencode/ac3_*.log`, not repo). Read-only: `scripts/10_...`,
`scripts/11_...`, `scripts/16_...`, `scripts/lib/esm_scoring.py`,
`scripts/lib/sequence.py`, `scripts/67_...`/`58_...`/`74_...` (conventions),
`data/processed/phase5_analysis_table.csv`,
`data/processed/own_context_metrics.csv`,
`data/processed/task_delta_esm_noise_floor.csv`. No existing script or
result file modified; no commit.
Unexpected: (1) AC3 required no MPS/multi-GPU work — CPU alone answered
all four conditions, but the full run took ~95–110 min of compute spread
over five attempts rather than the evaluator's "cheap" once (the cost was
the fp64 arm, 3,219 s, plus my projection mis-read and the two machinery
bugs); (2) the smoke's mislabeled projection line (multiplied by len(smoke)
rather than FULL_N) is what produced attempt 1's timeout — corrected with
the same caps, and the corrected projections (2,526–3,587 s) sat under the
7,200-s gates in every subsequent attempt; (3) attempt 3's stale-state bug
is exactly the class of failure AGENTS §5's "verify column identity /
reconcile n" warnings exist to catch — here caught by the n_ok/|d-rho|
prints disagreeing with a combined PASS line, which is why those prints
and the COVERAGE gate now exist; (4) attempt 4's gate failure was a bug in
the new gate itself (tuple keys), verified as such by attempt 4's own
n_ok=500/500 comparison block before fixing — the gate blocked a verdict
while its data was in fact complete, the designed fail-safe direction;
(5) the resume machinery's partial-refill test produced bitwise-identical
values (batch-of-2 vs batch-of-8 on this CPU), consistent with the
C1≡C2 batch-invariance observed at n=500.
---

## [AC5] — Does the position-222 term cancel in script 67's delta_PLL? (gates Z2c)
Status: PASS — inspection case: **cancels cleanly, as intended**. The
position-222 *background-offset* term is exactly zero (G2 measured
0.000e+00, twice, in two independent smoke runs), the j=222 contexts are
identical strings by construction, the offset folding into K is exact,
the defining identity holds numerically to K's print rounding
(2.6e-7), and the retained per-variant 222 term L222 does not dominate
(sd share 0.29 of delta_esm; ~7% of delta_pll's variance; its mean is a
constant offset, rank-invariant). The BLOCKED-Z2c branch does not
trigger: Z2c's full-N run is unblocked from AC5's standpoint (still
scheduled after the deepdive queue, per plan; command pre-specified).
Time started / finished: 2026-09-24 09:08:47 / 2026-09-24 09:18:42 (begins immediately after
[AC3] was appended at 09:08:47; inspection task, no compute run — all
numbers below are verbatim from prior runs' recorded output or a
sub-minute arithmetic check on files already on disk).
What I did: Read AC5's exact text (task doc L211-218). Read script 67's
pre-registered construction (docstring L24-54) and the actual
implementation: phase 1 builds one masked string per position in each
background (L205-211), G2 computes the 222 cross-background raw delta
(L230-237, gate <=1e-4 else exit(1)), K = sum_j d_bg_wt over ALL of P
including 222 (L241-244), phase 2 builds (WT-seq with alt@p) with 222
masked — the SAME string for every background, since the A222V site is
masked out (L255-267) — reads L222 = logP(V)-logP(A) from that one
forward (L268), and assembles delta_pll = delta_esm + l222 + K (L272);
the assert that no analysis variant sits at 222 (so j=p and j=222 never
coincide) is L287; phase 3's brute force directly sums the unfrozen
655-position PLL per background for a seed-0 sample and reports
direct-(delta_esm+L222) vs K (L300-325). Retrieved both existing smoke
runs' verbatim outputs (U2 smoke, PHASE2_MAX=300/BRUTE_N=2, in
SESSION_LOG L1998-2022; Z2a, PHASE2_MAX=75/BRUTE_N=16, in CLOSEOUT_LOG
L747-805) and ran an arithmetic check on the smoke CSV
(task67_u2_pll_scores_smoke.csv, 297 rows = that smoke's null set; no
new script — this task's deliverable is the report, not a file).
SUPPORTING ARITHMETIC (the cancellation, step by step). delta_PLL(v) =
sum_{j in P} [logP(s_av[j] | s_av masked@j) - logP(s_wt[j] |
s_wt masked@j)], s_av = A222V-seq with alt@p, s_wt = WT-seq with alt@p,
P = atlas positions union {222}, and p != 222 (phase5 position==222
count = 0, re-verified this session; assert L287 passed in both runs).
Split j in {p} u {222} u P\{p,222}:
 (a) j = p: masking p removes alt@p from BOTH contexts, so the two
     contexts differ only at 222 — exactly the cached scripts-10/11
     passes. Readout is alt in both. Subtracting and adding
     logP(wt_res|.) in each background: term = delta_ESM(v) + d_bg[p],
     where d_bg[p] = logP(wt_res | av ctx, mask p) - logP(wt_res | wt
     ctx, mask p).
 (b) j = 222: s_av and s_wt differ ONLY at 222, so masking 222 makes
     the two context strings IDENTICAL; the readouts differ (V vs A).
     term = logP(V|c) - logP(A|c) = L222(v). The context/background
     part cancels to identical input (G2 below, exactly 0); the
     readout odds L222 is RETAINED by design (docstring L33-36: "the
     only part of delta_PLL that carries new information beyond the
     cached tables").
 (c) distal j (frozen approximation, declared L37-43): contexts frozen
     at each background's WT -> term = d_bg[j], v-independent.
 (d) Fold: d_bg[p] (from (a)) + sum over P\{p,222} d_bg[j] (from (c)) =
     sum over P of d_bg[j] minus d_bg[222] = K - 0 = K. This is the
     exact cancellation claimed at docstring L41-43, and it requires
     d_bg[222] = 0 — which is exactly what G2 gates. Hence
     delta_PLL(v) = delta_ESM(v) + L222(v) + K  (code L272). QED by
     construction; the numbers below confirm each load-bearing piece.
Actual output (verbatim). The two cancellation-critical gates and K,
from both runs (identical values across independent invocations):
```
G2 raw delta at 222 across backgrounds = 0.000e+00 (must be ~0: masked contexts identical)   [U2 smoke AND Z2a]
  global constant K = sum_j delta_bg logP(wt_j) = +1.849228 (sd across positions = 0.03409)   [U2 smoke AND Z2a, identical]
G1 odds identity (wt bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
G1 odds identity (av bg, 12445 rows): max|raw-derived - cached| = 1.776e-15
G1/G2 PASS
L222 (n=300): mean=-5.17889 sd=0.02569 min=-5.25684 max=-5.07137          [U2 smoke]
L222 (n=75): mean=-5.18161 sd=0.03121 min=-5.25684 max=-5.07137           [Z2a]
delta_pll sd = 0.05921 (delta_esm sd = 0.11823)                           [Z2a (delta_pll over its 75 scored rows, delta_esm over all 11,344)]
```
The brute-force validation of the identity (unfrozen direct full-sum vs
the frozen construction; residual = declared frozen-distal error, not a
222 term):
```
direct - (delta_esm+L222): mean=+1.83639 vs K=+1.84923  -> mean algebra residual = -0.01284   [U2 smoke, BRUTE_N=2, n=2 disclosed]
frozen-distal approximation error: sd=0.00444 max|e|=0.01728  (= 4.7% of sd(delta_pll), n=2 disclosed)
(sample) spearman(direct full-sum, fitted frozen) = +1.0000 n=2
direct - (delta_esm+L222): mean=+1.86950 vs K=+1.84923  -> mean algebra residual = +0.02028   [Z2a, BRUTE_N=16, n=16 disclosed]
frozen-distal approximation error: sd=0.09794 max|e|=0.19096  (= 165.4% of sd(delta_pll), n=16 disclosed)
(sample) spearman(direct full-sum, fitted frozen) = +0.5559 n=16
```
My arithmetic check on the existing smoke CSV (297-row null set; K from
its verbatim 6-dp print):
```
rows: 297 | l222 non-null: 297 | delta_pll non-null: 297
identity max|delta_pll-(delta_esm+l222+K)| = 2.622e-07 (K rounded to printed 6 dp)
sd on these rows: delta_esm = 0.08735 | l222 = 0.02557 | delta_pll = 0.09594
corr(l222, delta_esm) = +0.2062
l222 sd / delta_esm sd = 0.293
mean offset (K + mean l222) = -3.32958
phase5 position==222 count = 0
```
Verdict: **PASS — the position-222 term cancels cleanly as intended; the
"does-not-cancel / 222-dominates" case does not hold.** Evidence, piece
by piece: (1) the load-bearing d_bg[222] is exactly 0.000e+00 (gate
1e-4, observed zero, in two independent runs — because masking 222
produces the identical input string in both backgrounds); (2) the j=222
background/context part therefore contributes nothing to K and nothing
spurious to any variant, and what remains is the designed per-variant
readout term L222; (3) the offset folding (a)+(c) = K is exact —
d_bg[p] from the j=p term plus the distal sum excluding p equals the
full sum once d_bg[222]=0; (4) the defining identity holds on every row
of real output: max|delta_pll - (delta_esm+l222+K)| = 2.6e-7, fully
explained by K being printed to 6 dp; (5) brute-force direct sums agree
with the construction to a mean residual of -0.013 (n=2) / +0.020
(n=16), i.e. ~1% of K, that residual being the separately-declared
frozen-distal approximation; (6) the 222 term does NOT dominate the
whole-sequence sum's variation: sd(L222) = 0.0256 vs sd(delta_esm) =
0.0874 on the same rows (ratio 0.293), l222 accounts for ~7% of
delta_pll's variance vs ~83% from delta_esm (plus ~10% covariance), and
L222's large mean (-5.179) enters only through the shared constant
K + mean(l222) = -3.3296, which is the SAME constant for every variant —
rank-invariant, so it cannot affect Spearman or comparability with the
single-position delta_ESM correlation. G1 (cached odds reproducible
from fresh raws, 1.776e-15) and the p!=222 disjointness also hold. So
Z2c's full-N U2 run may proceed when reached (post-deepdive), with
Phase 3's own BRUTE_N disclosure printed by that run as pre-registered.
Files: none created or modified except this log entry (read-only
inspection of `scripts/67_u2_pll_delta.py`, verbatim excerpts from
`docs/tasks/comparators-and-consolidation/SESSION_LOG.md` L1975-2029 and
`docs/tasks/closeout-u2-u3-u4-v5/CLOSEOUT_LOG.md` L745-805, and an
on-the-fly arithmetic check on `data/processed/task67_u2_pll_scores_smoke.csv`
+ `data/processed/phase5_analysis_table.csv`; no run executed, no
commit).
Unexpected: (1) the frozen-distal approximation — a different, already
declared limitation, NOT the 222 term — measured wildly differently
across the two smokes (4.7% of sd(delta_pll) at n=2 vs 165.4% at n=16,
direct-vs-fitted spearman +1.0000 vs +0.5559); both are tiny-n
disclosures by design, and Z2c's run will print its own BRUTE_N=5
measurement — worth watching there, since a large frozen-distal error
would mean the fitted delta_pll ranks differ from the true unfrozen
whole-sequence sum even though the 222 cancellation is exact; (2) the
on-disk smoke CSV holds the 297-row null set (U2 smoke), i.e. the U2
smoke's save postdates Z2a's, while the file's mtime (Sep 24 00:25)
matches Z2a's end — content, not mtime, identifies the producer here
(297 rows matches the U2 smoke's printed "Null set (+own_e_b): 297
variants"; Z2a's was 73); noted because AGENTS §5 says reconcile n's,
and the n reconciles once ns=null_set semantics are applied; (3) L222's
mean of -5.18 means every delta_pll sits near -3.33 (all negative) —
harmless for rank statistics and the shared-constant argument above,
but it is why any future null on delta_pll must pass script 33's own
all-+1/all--1 identity and null-centring checks (both printed PASS in
the smokes: max|diff|=9.888e-17 / 9.021e-17, "null mean IS consistent
with zero") rather than assume centring.
---

## [AC6] — ESMFold structure-aware SaProt background (fold + rerun): BLOCKED at AC6a
Status: **BLOCKED — AC6a's pre-registered size rule fired; AC6b/AC6c NOT
executed.** The visible checkpoint passed the size check (esmfold_3B_v1.pt
= 2,771,653,574 B <= 3 GB/file cap), but fair-esm's ESMFold constructor
hides a second weight file behind an automatic download:
**esm2_t36_3B_UR50D.pt = 5,678,116,398 B (5.29 GiB) > 3 GB cap** -> BLOCKED
with size, per AC6a's own text ("if it exceeds a reasonable cap, mark
BLOCKED and report the size rather than downloading blind", task doc
L223-226) and the carry-forward rule ("exceed -> BLOCKED with size").
Nothing about thresholds, N, or statistics is at stake — this is a
budget/availability block with one open user decision (below).
Time started / finished: 2026-09-24 09:18:42 / 2026-09-24 10:29:47 (begins immediately after
[AC5] was appended at 09:18:42).
What I did: (a) Read AC6's text (task doc L220-232). (b) AC6a size-first:
HTTP HEAD (no body) of https://dl.fbaipublicfiles.com/fair-esm/models/
esmfold_3B_v1.pt = 2,771,653,574 B (<= 3 GB cap, PASS at this stage);
esmfold_3B_v0.pt = 2,771,634,250 B (same class, not needed); not in local
cache; disk at that moment 21 GiB free. (c) Made ESMFold importable at all
(environment work, all disclosed): fair-esm 2.0.0's declared esmfold extra
omits openfold entirely (verified via importlib.metadata); PyPI "openfold"
is a squatter (single 0.0.1 tarball, 164,600 B — rejected, not the
aqlaboratory package); cloned aqlaboratory/openfold main @ commit
be2ec1841f16c966c65ae0e7599ebbadc725757d (2025-12-16) into
data/external/openfold (81,872 KB on disk, shallow); pip installs einops
0.8.2, ml-collections 1.1.0, absl-py 2.5.0, dm-tree 0.1.10 (wheel 316 kB
measured), modelcif 1.8, ihm 2.11, msgpack 1.2.2 (those wheel byte sizes
not captured — small pure-python packages, stated as unmeasured rather
than guessed); `pip install --no-build-isolation ./data/external/openfold`
built upstream's CPU STUB extension (setup.py's `else:` branch compiles
csrc/softmax_cuda_stub.cpp — "not implemented on CPU" throwers), yielding
attn_core_inplace_cuda.cpython-314-darwin.so; verified the stub is
unreachable via fair-esm's call paths (structure_module.py:440's kernel
call is gated by inplace_safe, which defaults False and is never passed
through fair-esm's trunk call at esm/esmfold/v1/trunk.py:203-207;
primitives.py:576's is gated by use_memory_efficient_kernel, default False
at primitives.py:475 and forced False under fp16 at 544-545) — so import
works and the kernel can never be invoked; patched fair-esm's two py3.14
dataclass mutable-default violations (esmfold.py:6,30 and trunk.py:7,51 ->
field(default_factory=...), backups esmfold.py.bak_py314 / trunk.py.bak_py314
saved) — `from esm.esmfold.v1.esmfold import ESMFold` then imports OK.
(d) Fetched esmfold_3B_v1.pt deliberately with curl -C -, byte-verified
against the HEAD (got=expected=2,771,653,574, SIZE MATCH OK), 2:15 wall.
(e) Fold-pipeline smoke attempt 1 (33-aa, machinery only): killed at the
harness timeout with ZERO output — stdout had been block-buffered into a
pipe, hiding all progress (my visibility bug, fixed next step). (f) Staged
retry with python -u + on-disk log exposed the real story: the ESMFold
constructor (esmfold.py:43 `self.esm, self.esm_dict =
esm.pretrained.esm2_t36_3B_UR50D()`) auto-downloads the 3B language model;
that transfer (started by attempt 2 at ~10:00, completed 10:05) was then
followed by 20 minutes with no further log line until the kill at 10:25 —
observed fact; leading hypothesis (labeled as inference, not measured):
memory pressure loading a 5.68 GB checkpoint + building the 3B module on
this 16 GiB box (sysctl hw.memsize = 17,179,869,184 B). (g) Only AFTER
seeing the ctor's "Downloading:" line did I HEAD that file:
5,678,116,398 B -> exceeds cap -> BLOCKED rule fires. (h) Cleanup: deleted
the killed attempt's orphan .partial (4,578,213,888 B transferred then
discarded = WASTED, counted below) and stray tmp dirs; kept all three
completed files in cache so an unblock would need zero re-transfer.
Actual output (verbatim):
```
content-length esmfold_3B_v1.pt            : 2771653574
content-length esm2_t36_3B_UR50D.pt         : 5678116398   (> 3GB cap)
content-length esm2_t36_3B_UR50D-contact-regression.pt : 6759
bytes: got=2771653574 expected=2771653574
SIZE MATCH OK
ESMFold import OK
attn_core_inplace_cuda = .../site-packages/attn_core_inplace_cuda.cpython-314-darwin.so
[10:00:19] ckpt exists: True size=2771653574
[10:00:20] torch.load t=1.3s type=dict keys=['model', 'cfg']
[10:00:20] cfg type=DictConfig
Downloading: ".../esm2_t36_3B_UR50D.pt" to /Users/arnavchavan/.cache/torch/hub/checkpoints/esm2_t36_3B_UR50D.pt
Downloading: ".../esm2_t36_3B_UR50D-contact-regression.pt" to .../esm2_t36_3B_UR50D-contact-regression.pt
cache: esmfold_3B_v1.pt 2771653574 (Sep 24 09:42) | esm2_t36_3B_UR50D.pt 5678116398 (Sep 24 10:05) | esm2_t36_3B_UR50D-contact-regression.pt 6759
timeout: NONE | (macOS has no coreutils timeout in this zsh)
```
Fetch accounting (disclosed in AA7's style): session DATA-fetch total
UNCHANGED (~196.3/200 MB — no data-member fetch here). Model/dependency
class this entry: 2,771,653,574 B deliberate (size-first compliant) +
5,678,116,398 B ctor auto-fetch (size check POST-hoc — the discipline miss,
owned explicitly below) + 6,759 B + 4,578,213,888 B wasted partial +
openfold clone ~81,872 KB on disk (transfer not separately measured) +
six small pip wheels (only dm-tree's 316 kB measured).
Verdict: **BLOCKED (AC6a), awaiting user decision.** Options: (1) WAIVE
the 3 GB/file cap for this one dependency — all three files are already on
disk, so resuming costs zero transfer; remaining AC6b/c work (staged fold
smoke with unbuffered visibility, then the 656-aa fold of av_seq, token
extraction via their get_struc_seq, then script 76-style aware scoring
side-by-side with the frozen control) proceeds on approval, with the 16 GiB
RAM question treated as a measured risk (the post-download stall above);
(2) keep AC6 blocked — the deepdive loses the structure-aware experiment
("the actual experiment" per the evaluator's framing) but nothing else
depends on it: script 70's frozen control (closeout Z3f-Z3i) needs only
SaProt_650M + foldseek, both already local; (3) no in-budget alternative
exists — fair-esm hardcodes esm2_t36_3B_UR50D (esmfold.py:43), and
substituting a smaller LM would not be the published ESMFold. Because the
side-by-side that would have pulled Z3f-Z3h forward no longer has a consumer
this round, Z3f-Z3i return to their original closeout position (after the
deepdive) — pinned order restored, disclosed here.
Files: no project script created or modified; this log entry is the only
repo change. Environment changes: pip installs (einops, ml-collections,
absl-py, dm-tree, modelcif, ihm, msgpack), openfold 2.2.0 (CPU-stub wheel,
commit be2ec184), data/external/openfold clone, two fair-esm site-packages
files patched with .bak_py314 backups, torch cache gains esmfold_3B_v1.pt
+ esm2_t36_3B_UR50D.pt + contact-regression (sizes above), orphan .partial
deleted.
Unexpected: (1) the hidden 5.68 GB dependency auto-downloading inside the
constructor — "check size before fetching" could not see it in advance, so
that part of AC6a was satisfied only post-hoc (owned above; the rule fired
as soon as the size was knowable, before any use of the model); (2) the
20-minute post-download silence (memory-thrash hypothesis, unconfirmed —
no fold result was produced, so no structural claim exists either way);
(3) block-buffered stdout hid attempt 1's progress entirely (fixed via
-u + log files; noted because it cost ~25 min); (4) `timeout` does NOT
exist in this environment (no coreutils) — the pre-specified Z2c command
`timeout 5h env ... scripts/67_u2_pll_delta.py` would fail verbatim here;
at closeout, run it under the harness timeout (18,000 s) instead and
disclose the substitution there; (5) PyPI's openfold 0.0.1 is a squatter,
not upstream; (6) AC6 produced ZERO scientific output — no fold, no
tokens, no rerun numbers exist, and none are invented here.
---

## [AD2] — Benchmark A222V against published biophysics (literature vs ThermoMPNN -0.0439)
Status: PASS (executed: bounded literature search + sign-harmonized
comparison completed; the result is a NEGATIVE finding about the model
and is stated plainly below exactly as the task requires).
Time started / finished: 2026-09-24 10:30:00 / 2026-09-24 10:37:10 (begins right after [AC6]
was appended at 10:29:47).
What I did: AD2a (task doc L248-255): search for any published ΔΔG or
thermostability measurement for A222V specifically and compare against
ThermoMPNN's -0.0439. (1) Sourcing: took -0.0439 from script 68's V3
PRINT line (quoted verbatim below; produced in [V3], SESSION_LOG L2378)
per the carry-forward instruction "use script 68 V3 print, not the CSV"
— the CSV cannot supply it anyway: task_V2_thermompnn_ddg.csv contains
0 position-222 rows (AD1 flag #3, re-verified in passing this entry).
(2) Search: two websearch queries (thermostability/ΔΔG-focused) + one
targeted Tm/unfolding query, then ONE primary-source fetch (Marini et
al. PNAS 2008 at PMC2430358) to verify the headline experimental quote
verbatim before citing it (past project failure: citing a real paper's
conclusions inaccurately — so quotes here carry DOI/PMID each).
(3) Sign harmonization (§5 discipline) done BEFORE comparing: ThermoMPNN
uses positive = destabilizing (AD1's four-layer audit); the IJMS 2021
consensus paper uses the OPPOSITE convention — its own criterion text
says "negative results, lower than − 1 kcal/mol, indicating protein
destabilization". Comparing the raw numbers without harmonizing would
invert the conclusion, so both frames are stated explicitly below.
Actual output (verbatim):
```
V3 (one number): ThermoMPNN ddG(A222V) = -0.0439 (model output units) -- read from their SSM row (position 222 = resi 222), not from the atlas join

[experimental — thermostability/activity arm]
Marini et al., PNAS 2008;105(23):8055-8060, doi:10.1073/pnas.0802813105,
PMID 18523009 (fetched at PMC2430358, quote verified):
  "The A222V mutant enzyme is less stable and more thermolabile than the major form (8, 9) ... Under the conditions used here (55°C, 20 min), A222V lost nearly all activity, whereas the major allele retained ≈30% of its original activity, in agreement with previous studies (22)."
  "Again, the A222V variant displayed ≈50% of the enzymatic activity of the major allele, as reported previously (19, 22, 24)."
  "individuals with A222V (A/V) have ≈65% of the total activity seen for major allele (A/A) homozygotes, where A222V homozygotes (V/V) retain 30% of the activity of A/A homozygotes (6)."
  "The A222V change reduces MTHFR activity and increases its thermolability ... Biochemically, the A222V variant may be less tightly bound to its flavin cofactor and more prone to dissociation into monomers but can be stabilized by reduced folates (8, 9)."
AJHG 2021, "Shifting landscapes of human MTHFR missense-variant effects" (cell.com/article/S0002929721001932):
  "For the p.Ala222Val control, enzyme activity was completely lost and did not recover unless FAD was supplemented before heat denaturation, as expected."
Yamada et al., PNAS 2001;98:14853-14858, doi:10.1073/pnas.261469998 (abstract):
  "The Ala222Val MTHFR, however, has an enhanced propensity to dissociate into monomers and to lose its FAD cofactor on dilution; the resulting loss of activity is slowed in the presence of methyltetrahydrofolate or adenosylmethionine."
Tran et al., Biochemistry 2006, doi:10.1021/bi052294c, PMID 16605249 (abstract):
  "In both human and E. coli MTHFR, the A --> V mutation increases the rate of dissociation of FAD"
  "the A → V mutation is located at the bottom of the (beta-alpha)8 barrel of the catalytic domain in a position that does not contact the bound FAD prosthetic group"

[computed ΔΔG arm — kcal/mol, THEIR convention: negative = destabilizing]
IJMS 2021, doi:10.3390/ijms23010167, Table 1 row:
  "A222V * Decreased affinity for FAD − 0.71 − 1.08 − 0.09 N 11"   (INPS3D, FoldX, PoPMuSiC2 | ISPRED4 | RSA 11%)
  criterion: "Bold style indicates variations for which at least two of the three methods ... compute negative results, lower than − 1 kcal/mol, indicating protein destabilization"
  classification: "These variations, as reported in Table 1, decrease the binding affinity without perturbing the protein stability, including A222V and E429A."

[comparison — conventions harmonized to ThermoMPNN's positive = destabilizing]
ThermoMPNN (project, script 68 V3) : -0.0439  -> marginally stabilizing / ~neutral
IJMS consensus converted            : INPS3D +0.71, FoldX +1.08, PoPMuSiC2 +0.09 destabilizing
magnitude gaps: |ThermoMPNN| is 2.1x smaller than PoPMuSiC2, 16x smaller than INPS3D, 25x smaller than FoldX — and OPPOSITE in sign to all three.
No experimental ΔΔG in kcal/mol for A222V was located in this bounded search (3 queries + 1 primary fetch): the experimental characterization is activity/thermolability/FAD-loss based, not equilibrium-unfolding ΔΔG. No p-value applies — this is a deterministic literature comparison, no resampling was done or needed.
```
Verdict: **The model DOES miss A222V — stated plainly as the task
demands: this is a REAL CONCERN about trusting ThermoMPNN's absolute
ddG values elsewhere in this system, not a footnote.** ThermoMPNN scores
the best-characterized thermolabile variant in MTHFR at -0.0439 —
essentially neutral, even marginally stabilizing in its own convention
(AD1: positive = destabilizing) — while experiments show near-total
activity loss at 55 C/20 min where the major allele retains ~30%,
~50% intrinsic activity, enhanced FAD loss and monomer dissociation.
Scope and context, disclosed so the concern is neither diluted nor
overgeneralized: (a) the miss is SHARED with classical predictors — the
IJMS three-method consensus also fails its own >=2-of-3 destabilization
criterion for A222V and explicitly files it under FAD-affinity loss
"without perturbing the protein stability", i.e. this is a known blind
spot of fold-stability ΔΔG methods for this variant, not a quirk unique
to ThermoMPNN; (b) the documented mechanism runs helix-alpha5 ->
faster FAD dissociation (the mutation does not contact FAD), a
cofactor-loss defect that models trained on Megascale-style unfolding
data are structurally poorly positioned to score; (c) within THIS
project the miss bears on ABSOLUTE-value interpretation of individual
ddGs — and since position 222 has 0 rows in both phase5 and task_V2,
it does not arithmetically alter the rank-based -0.0733 in Part II
section 12, but it does argue against reading that (or any) ThermoMPNN
number as capturing the flagship variant's documented defect.
Effect sizes: the 2.1x-25x magnitude gaps and the sign disagreement
quoted above; significance testing not applicable.
Files created/modified: DEEPDIVE_LOG.md (this entry only). No script
created — a search+comparison needs no compute, so the next free script
number is unchanged (76). No file fetched into data/ (3 web queries +
1 HTML page read as text; session data-fetch total unchanged
≈196.3/200MB cap).
Anything unexpected or worth flagging: (1) NO experimental kcal/mol
ΔΔG for A222V appears in anything this search surfaced — the task's
"ΔΔG or thermostability measurement" resolves to the thermostability/
activity arm only; reported as "none located in a bounded search", NOT
as a claim that none exists anywhere. (2) The two comparison targets
use OPPOSITE sign conventions (ThermoMPNN + = destabilizing; IJMS -
= destabilizing) — caught from the IJMS criterion text; a re-doer who
compares raw table values without reading both conventions would
conclude exactly backwards. (3) The in-silico A222V stability literature
is itself split: PMID 26273990's 50-ns MD claims "increased
conformational stability" for the mutant (from larger RMSD fluctuation —
an idiosyncratic reading), a 2023 YASARA MD (doi:10.24071/jpsc.005727)
concludes "unstable", the IJMS consensus concludes mild/no
destabilization — only the experimental thermolability is unambiguous.
(4) A 2025 thesis in the results quoted "35-45% residual activity" —
secondary source, NOT used in the verdict; every number in the output
block above is from a fetched/directly-quoted primary source with its
DOI/PMID. (5) Search was bounded (one session, three queries) —
conclusions are limited to what it surfaced.
---

## [AD3] — Non-degenerate threshold model: sigmoid fit + inverted-U shape test — shape DOES NOT appear
Status: PASS (executed end to end; all pre-registered gates green; the
pre-registered falsifiable prediction DID NOT appear and is reported
plainly as a null, per task L270-271 and AGENTS section 0).
Time started / finished: 2026-09-24 10:37:20 (immediately after [AD2]
was appended at 10:37:10) / 2026-09-24 10:37:20
What I did: Created scripts/76_threshold_sigmoid_model.py (next free
number; tree verified: 71-75 taken). AD3a/AD3b procedure PRE-REGISTERED
in the script's docstring before any run, as task L263-265 requires:
f(x) = A*sigmoid((theta-x)/s) declared DECREASING from physics (not
chosen from data), exactly two free parameters (theta, s), A := Q95 of
f_bar_wt as a declared (not fitted) range normalisation, ddG_wt = 0 by
definition, x_double = ddG_v + ddG_222 (the model's own additive
basis), four-term interaction = f(both)-f(v)-f(222)+f(wt) exactly as
task-pinned; deterministic fit (21x12 grid -> top-5 SSE -> trf refine)
on single mutants only, with the fit structurally unable to see own_e_b
(it receives two 1-D arrays); AD3b primary = row-level Spearman
rho(|own_e_b|, d) with d = |ddG_v + ddG_222 - theta|, position-cluster
bootstrap CI (N_BOOT, seed 0), POSITION-level association null (shuffle
position means, N_PERM, seed 1, two-sided, identity check mandatory),
verdict rule fixed in advance: shape "appears" iff rho<0 AND p_pos<0.05;
secondaries (a)-(e) pre-registered as always-reported (construction
partial-out of f_bar_wt; signed rho; 5-quintile profile; model
self-check rho(|pred_int|, d); f_bar column robustness). Gates G1-G5
defined before running (G1 ddG_222 = -0.0439 +-5e-5 re-read from the
raw V2-run SSM; G2 fit plumbing incl. rho floor +0.10; G3 formula
identities <1e-12; G4 row accounting; G5 permutation finiteness +
identity). TWO smoke-run failures occurred before the passing smoke,
both implementation bugs in the new script, both fixed to make code
conform to the (frozen) docstring — no decision rule, threshold, form,
or null was changed: (1) G1 KeyError 'resi' — the raw SSM's column is
ThermoMPNN's 0-based `position` (resi - 40), not resi; fixed by applying
script 68's documented gated offset map, with the offset re-derived
from the PDB (chain_a_first_resi) rather than hardcoded, plus script
68's wildtype-A assertion; (2) G2 fired with the verbatim evidence line
`spearman(f_hat, f_bar_wt)=-0.2414  (raw spearman(ddg, f_bar_wt)=-0.2414)`
--- f_hat reproducing the RAW ddG rho instead of its negation proved the
sigmoid was implemented as 1/(1+exp(z)) (increasing in x) while the
pre-registered form is 1/(1+exp(-z)) (decreasing); the pre-registered
rho floor is what caught it. Disclosure/judgment: I treated both as
code-vs-spec bugs rather than data sanity failures (root cause
unambiguous, fix makes code match the frozen spec, decision rules
untouched) and re-ran smoke after each fix; had the cause been
anything but spec-nonconformance I would have stopped per AGENTS
section 10. Smoke (SMOKE=1, 300/300) then passed all gates in 2.1 s;
full run executed once at declared defaults N_BOOT=10000, N_PERM=10000.
Actual output (verbatim, full run):
```
AD3 -- NON-DEGENERATE THRESHOLD MODEL (scripts/76) SMOKE=False N_BOOT=10000 N_PERM=10000
  V2 rows: 10141 | finite (ddg & f_bar_wt): 9935 | finite own_e_b: 9595 | both: 9595 | f_bar finite: 10141
  dropped for fit: 206 (f_bar_wt NaN) | dropped for AD3b: 546 (own_e_b NaN)

STAGE A -- AD3a: SIGMOID FIT ON SINGLE MUTANTS ONLY
  G1 ddG_222 = -0.0439  [re-read from raw V2-run SSM (/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/thermompnn_full/ThermoMPNN_inference_6FCX.csv), their position 182 + chain-A offset 40 = resi 222 wt A]  tol=5e-05  PASS
  n_fit=9935  A=Q95(f_bar_wt)=1.429452 (declared const)
  theta=+1.184056  s=2.852896  SSE=1970.0722  SSE_const=2100.8241  1-SSE/SSE_const=0.0622
  spearman(f_hat, f_bar_wt)=+0.2414  (raw spearman(ddg, f_bar_wt)=-0.2414)
  CONSTRUCTION DISCLOSURE: spearman(f_bar_wt, own_e_b)=-0.1343  (own_e_b was fitted in scripts/17 using wild-type-arm fitness as an expectation input)
  G2 fit sanity PASS
  G3 identities PASS (linear=8.88e-16, ddG_222->0=0)

STAGE B -- AD3b: INVERTED-U SHAPE TEST ON REAL own_e_b
  analysis rows: 9595 across 586 positions
  PRIMARY row-level rho(|own_e_b|, d) = -0.0189 [-0.0467, +0.0077] p_boot=0.1680  n=9595 clusters=586
  POSITION-LEVEL association null: rho_pos=-0.0565 p=0.1753 (N_PERM=10000, positions=586, identity check PASS)
  VERDICT (rho<0 AND p_pos<0.05): INVERTED-U SHAPE DOES NOT APPEAR
  (a) PARTIAL rho controlling f_bar_wt = -0.0177 [-0.0447, +0.0087] p_boot=0.1840  <- section-4 construction control
  (b) signed rho(own_e_b, d) = -0.0038 [-0.0316, +0.0240] p_boot=0.7752
  (c) quintile profile (d cut points [0.3226, 0.6402, 0.919, 1.2343]):
       Q1: n= 1919 mean_d= 0.1600 signed=+0.0124 |e.b|=0.1713 [0.1614, 0.1817]
       Q2: n= 1919 mean_d= 0.4809 signed=+0.0107 |e.b|=0.1670 [0.1572, 0.1773]
       Q3: n= 1919 mean_d= 0.7746 signed=+0.0091 |e.b|=0.1666 [0.1573, 0.1764]
       Q4: n= 1919 mean_d= 1.0675 signed=+0.0169 |e.b|=0.1646 [0.1551, 0.1745]
       Q5: n= 1919 mean_d= 1.5762 signed=+0.0024 |e.b|=0.1554 [0.1464, 0.1650]
  (d) MODEL self-check rho(|pred_int|, d) = -0.6064 (max|pred_int|=0.001252)
  (e) ROBUSTNESS refit on f_bar: theta=+1.5398 s=2.4834 n=9595 | row rho=+0.0043 pos p=0.2935 | verdict unchanged (APPEARS'=False)
  distance robustness: rho(|own_e_b|, |ddg-theta|) = -0.0209

  saved 10141 rows -> task76_threshold_model.csv

LIMITATIONS (printed with results, AGENTS section 6)
  1. Construction overlap: fitness enters BOTH the sigmoid fit and
     own_e_b's expectation model (scripts/17); the position-shuffle null
     cannot alone separate a threshold-shaped interaction from
     shared-derivation structure. Control (a) governs claim strength.
  2. ddG_222 ~ 0 (G1): the double's threshold distance ~ the single's.
  3. A=Q95 is a declared scale convention for growth scores, not a
     saturation claim.
  4. Observational fit: no causal threshold established by stage A.

AD3 DONE  (64.8s)  VERDICT: INVERTED-U SHAPE DOES NOT APPEAR
```
Verdict: **AD3a PASS — the model was built and fit as pre-registered;
AD3b NULL — the inverted-U shape DOES NOT APPEAR.** Plainly: the
pre-registered shape test fails on both prongs — row-level
rho(|own_e_b|, d) = -0.0189 with position-cluster CI [-0.0467, +0.0077]
(spans zero) and the position-level association null gives p = 0.1753
(> 0.05), so the verdict rule fixed before running is not met. Fit
facts: theta = +1.184056, s = 2.852896, A = 1.429452 (declared Q95
constant); the sigmoid beats a constant by only 6.2% of SSE
(1-SSE/SSE_const = 0.0622) over a genuine but weak monotone relation
(raw ddG-fitness rho = -0.2414). Effect sizes: the quintile profile
declines 0.1713 -> 0.1554 (9.3%) in the predicted direction but the
marginal CIs overlap and the primary test does not distinguish it from
the position-shuffle null; secondaries agree with the null (signed rho
-0.0038, p_boot 0.775; construction partial rho -0.0177, i.e. the
section-4 shared-derivation worry neither creates nor destroys this
(null) signal; f_bar robustness flips rho to +0.0043, p = 0.2935,
verdict unchanged). Two further facts sharpen what the null means:
(1) secondary (d) shows the machinery WOULD see the shape if it were
present at the model's own scale — within the model,
rho(|pred_int|, d) = -0.6064, a strong inverted U — so the
non-appearance is a genuine disagreement between the model's predicted
profile and the data, not a broken test; (2) effect-size ceiling:
max|pred_int| = 0.001252 in growth-score units vs mean observed
|own_e_b| ~ 0.165 (same scale) — the fitted threshold model predicts
interactions ~130x SMALLER than the epistasis actually observed, so
even a perfectly detected shape would leave the observed interaction
magnitudes unexplained by ~2 orders of magnitude. Per task L270: this
clean non-appearance is reported as-is; no threshold, binning, or
statistic was altered to chase it (the only code changes were the two
spec-conformance bugs disclosed above, made before the passing smoke).
No p-value transfer claims are made beyond these quantities; all CIs
are position-cluster bootstrap, all nulls position-level (sections 3-4).
Files created/modified: scripts/76_threshold_sigmoid_model.py (new,
pre-registered docstring); data/processed/task76_threshold_model.csv
(new, 10,141 rows: per-variant ddg, f_bar, f_bar_wt, own_e_b, d_primary,
d_robust, f_wt/f_222/f_v/f_both/f_hat predictions, pred_int, in_fit,
in_test flags); DEEPDIVE_LOG.md (this entry only). No existing script or
result modified. Next free script number is now 77. Runtime: smoke 2.1 s,
full 64.8 s — far under the 2h measure-first rule (measured, not
estimated from another script).
Anything unexpected or worth flagging: (1) Both smoke failures are
disclosed in full above with the verbatim G2 evidence line; the
judgment call to fix rather than stop-and-ask rests only on the bugs
being code-vs-frozen-docstring nonconformance — flagged here so the
user can revisit that judgment if they disagree. (2) The fit's theta
(+1.18) sits inside the ddG range [-1.76, 4.50], so the threshold is
interior as designed, but s = 2.85 is wide (transition spans most of
the range) — the fitted "threshold" is a gentle slope, not a sharp
switch; this weakens the sharpness of AD3b's falsifiable prediction
structurally and belongs in any downstream reading of the null. (3)
own_e_b is finite on only 9,595/10,141 rows (546 NaN dropped) across
586 positions (not the full 654) — accounting printed by G4; the 546
excluded rows were not tested for systematic skew with respect to e.b
(not available when NaN) — noted as an unexamined exclusion, though
excluded for missingness of the target itself. (4) The construction
disclosure number (corr f_bar_wt vs own_e_b = -0.1343) is small but
nonzero; per pre-registration, control (a) governs claim strength — and
since the primary claim is a NULL, the overlap cannot be said to have
manufactured it (a null needs no de-confounding). (5) The raw V2-run
SSM lives in the OS temp dir (T/opencode/thermompnn_full/), which is
outside the repo and may be cleaned by the OS someday — if G1's fallback
branch ever fires, the value comes from the executed [V3] print
(SESSION_LOG L2378) and says so in its output.
---

## [AD4] — Native double-mutant scoring (ThermoMPNN-D): interaction does NOT capture own_e_b
Status: PASS (executed end to end; all pre-registered gates G0-G6 green;
the pre-registered verdict rule fired as DOES NOT CAPTURE EPISTASIS and
is reported plainly as a null, per task L270-271 and AGENTS section 0).
Time started / finished: 2026-09-24 10:56:00 (right after [AD3] was
appended at 10:55:13) / 2026-09-24 10:56:00
What I did: AD4a check first. The vendored ThermoMPNN does NOT support
double-mutant scoring — verbatim evidence: datasets.py L148
`# no insertions, deletions, or double mutants` (mut_type containing ":"
skipped at load); analysis/custom_inference.py builds single
Mutation(position,wt,mut) objects only; transfer_model.py L113-116 ddG =
(mut head) - (wt head) at one aa_index; README L8: "A new ThermoMPNN
model has been released for prediction of ddG for double mutant pairs at
a new repo, [ThermoMPNN-D]". So AD4a's "if so" is FALSE locally and the
upstream ThermoMPNN-D (Kuhlman-Lab) is the native path: fetched with
git clone --depth 1 -> data/external/ThermoMPNN-D, clone 125,488 KB
(CODE-REPO fetch, not a member/data fetch — session member-data total
unchanged ~196.3/200MB). Checkpoints ship in-repo, all far under the
3GB/file weight cap: ThermoMPNN-D-ens1.ckpt 8,097,475 B,
ThermoMPNN-ens1.ckpt 10,579,907 B, vanilla v_48_020.pt 6,681,301 B
(ens1 only used — their get_model default, so we run exactly their CLI
model choice; ens2/3 present but averaging them would deviate from
their behaviour and is not pre-registered). External prior noted BEFORE
running: their own paper Dieckhaus & Kuhlman, Protein Science 2025,
doi 10.1002/pro.70003, "Protein stability models fail to capture
epistatic interactions of double point mutations" — a published prior
AGAINST detection, so a null here is expected-by-literature rather than
invented after the fact. Pre-registered in scripts/77 docstring before
any inference: quantity = interaction_D(v) = ddG_epi(222A->V, Xwt->a) -
ddG_single(Xwt->a) - ddG_single(222A->V), all three terms independent
model evaluations (no additive-term degeneracy, task L276-278); mapping
= their seq index resi-40 (same gated offset as script 68 / [V3]'s 182);
gates G0-G6; primary = row-level Spearman rho(interaction_D, own_e_b) +
position-cluster bootstrap CI (N_BOOT, seed 0) + POSITION-level
association null (N_PERM, seed 1, two-sided |rho|, identity check
mandatory); EXPECTED SIGN negative (stability units vs fitness-scale
e.b, orientation evidenced by AA4's -0.0733); verdict rule frozen:
CAPTURES iff (i) p<0.05 AND (ii) rho<0 AND (iii) |rho|>|additive
baseline|; secondaries (a)-(d) always reported; NULL LABEL = association
null; construction note: ThermoMPNN-D trained on Tsuboyama mega-scale,
NOT on this atlas's fitness, and own_e_b is not a D input — no
shared-derivation structure in the primary pairing (a genuine strength
vs AD3). Third-party modifications, all disclosed with backups: (1)
v2_ssm.py device-portability patch (backup v2_ssm.py.bak_ad4): 3x
`device = "cuda"` -> `device = DEVICE`, 2x `model.cuda()` ->
`model.to(DEVICE)`, + module-level DEVICE = cuda-if-available-else-cpu —
model math, enumeration, postprocessing untouched (diff verified line by
line); (2) process-level torch.load -> map_location="cpu" monkey-patch
(this process only; repo files untouched); (3) examples/configs/local.yaml
thermompnn_dir pointed at the authors' cluster /proj/kuhl_lab/... — the
README explicitly instructs "modify the local filepath information found
in examples/configs/local.yaml to match your system", so this is the
sanctioned config step (backup local.yaml.bak_ad4; only content change
is thermompnn_dir, plus CRLF->LF line-ending normalization from
read_text/write_text); (4) new lib module scripts/lib/position_null.py
(the position-shuffle null from 76 extracted verbatim so 77 imports
instead of reimplementing; scripts/lib/stats.py untouched). Everything
else is THEIR code called verbatim: get_config, get_model, load_pdb,
tied_featurize_mut, run_single_ssm, run_double, SSMDataset,
get_ssm_mutations_double, get_dmat — the only bespoke logic is row
enumeration for the specific (222,V) pairs, identity-gated against their
own enumerator (G3, both directions, V-slice). THREE pre-pass failures
before the passing smoke, each with unambiguous root cause, each fixed
to conform code/config to the frozen spec — no statistic, threshold, or
decision rule changed: (1) smoke run 1 G0:
`FileNotFoundError: [Errno 2] No such file or directory:
'/proj/kuhl_lab/ThermoMPNN-D/ThermoMPNN-D/vanilla_model_weights/v_48_020.pt'`
→ README-sanctioned local.yaml config fix above; (2) smoke run 2 G3:
`*** G3 FAIL: enumeration identity broken both-direction check;
|ours_near|=437 |theirs_222|=8303 only-ours sample=[] only-theirs
sample=[((143, 182), (14, 0), (8, 1)), ...]` — analysis: only-ours=[]
already proved every row we use exists verbatim in theirs, and 8303 =
23 pairs x 361 = their enumerator emits ALL 19x19 combos per pair while
our frozen enumeration fixes the 222-side to V (23x19 = 437); the
docstring's G3 sentence (equality with their FULL set) and its
enumeration sentence (V fixed) were internally inconsistent — a gate-
definition defect. Amended G3 to like-for-like BOTH-DIRECTION equality
on the V-at-222 slice (ours_near ⊆ theirs AND ours_near == theirs_V),
amendment text written into the docstring with the reason; purpose
unchanged: exact tuple conformance of our row builder to their indexing,
on every row used; (3) smoke run 3 exit 137 (SIGKILL) at the forward
pass: measured shapes — edges [1,612,48,128], and run_double repeats
them batch_size times, so their default 2048 needs 23.31 GiB of buffers
(hid+embed+edges+E_idx, computed explicitly) on this 16 GiB Mac →
BATCH 2048->512 (5.83 GiB). Batch size is plumbing only: rows are
processed independently (eval mode, no batchnorm, per-row gathers into
repeated buffers) so predictions are batch-invariant; measured BEFORE
any statistic existed. Judgment disclosure (AGENTS section 10): all
three were treated as conformance/measurement defects rather than data
sanity failures (causes unambiguous, fixes make conformance to the
frozen spec, no result-adjacent quantity changed) and are quoted above
so the user can revisit that judgment; had any cause been ambiguous I
would have stopped. Smoke run 4 passed all gates in 6.2 s; unit-label
cosmetic added to secondary (d) print after smoke (cross-unit ratio
flagged in the printed line itself); full run executed once at declared
defaults N_BOOT=10000, N_PERM=10000.
Actual output (verbatim, full run):
```
AD4 -- ThermoMPNN-D NATIVE DOUBLE-MUTANT INTERACTION (scripts/77) SMOKE=False N_BOOT=10000 N_PERM=10000
  D repo: .../data/external/ThermoMPNN-D | torch.load -> map_location=cpu (disclosed)
  G0 cfg+model(epistatic) loaded | chain A parsed: len(seq)=612 resolved=596 | DEVICE=cpu
  G1 bounds + three-way wt match PASS: all 10141 rows (V2 wt == D-seq[resi-40])
  G2 seq[182]=='A' PASS | seq_idx range 0..604
  enumeration: 11305 doubles (595 positions x 19 alts)
  G3 enumeration identity PASS (both directions, V-at-222 slice): 437 near rows == their V-slice rows at 10A (23 of their pairs x 361 combos = 8303; their full 10A set: 1822689)
  epistatic forward PASS: n=11305 ddG range [-1.841, +3.415]
ThermoMPNN single mutant predictions generated for protein of length 612 in 0.53 seconds.
    G4a candidate THERMO: max|wt-column ddg| = 0.000e+00
    G4a candidate MPNN: max|wt-column ddg| = 3.621e+00
  G4a column order selected: THERMO (wt-zero invariant)
  G4 cross-model PASS: spearman(ddG_single_D, ddG_vendored) = 0.9382 over n=10141 (their README: 'similar results')
  G5 all 10141 doubles matched PASS | ddG_single(222V) = +0.8071
  analysis rows: 9595 (own_e_b finite) across 586 positions | dropped for NaN own_e_b: 546

STAGE B -- PRIMARY: rho(interaction_D, own_e_b)
  PRIMARY rho(interaction_D, own_e_b) = +0.0154 [-0.0166, +0.0465] p_boot=0.3406 n=9595 clusters=586
  POSITION-LEVEL association null: rho_pos=+0.0083 p=0.8459 (N_PERM=10000, positions=586, identity check PASS)
  VERDICT RULE (frozen): p<0.05 AND rho<0 AND |rho|>|rho_base| -> DOES NOT CAPTURE EPISTASIS
    conditions: (i) p=0.8459 F | (ii) rho<0 F | (iii) |rho|=0.0154 vs |base|=0.0733 F
  (a) rho(|interaction_D|, |own_e_b|) = -0.0569 [-0.0902, -0.0229] p_boot=0.0018
  (b) rho(interaction_D, Ca-dist 222) = +0.0246 | near<=10A: n=363 rho=-0.0250 | far>10A: n=9232 rho=+0.0146 (descriptive)
  (c) additive baseline rho(ddG_vendored, own_e_b) = -0.0733 [-0.1021, -0.0437] p_boot=0.0000 (AA4's -0.0733 was the wider-set figure)
  (d) effect sizes [UNITS DIFFER: interaction in model output units (their column label kcal/mol); own_e_b in fitness units - the ratio below is CROSS-UNIT context only]:
      interaction_D mean=-1.31853 sd=0.37904 mean|.|=1.31864 max|.|=3.04493  vs own_e_b mean|.|=0.16499 cross-unit ratio=7.9923
      mean|interaction| near=1.43992 far=1.31387

  saved 10141 rows -> task77_thermompnnD_doubles.csv

LIMITATIONS (printed with results, AGENTS section 6)
  1. ens1 checkpoint only (their get_model default); ens2/3 not
     averaged (would deviate from their CLI behaviour).
  2. CPU float path (device patch); G4 cross-check = 0.9382 agreement
     with the published-model outputs on this machine.
  3. Singles from single-model head, doubles from Siamese epistatic head
     (two checkpoints in one framework; their own additive mode does the
     same).
  4. Far pairs may default near-additive by architecture (48-neighbour
     message passing); (b) reports the distance structure honestly.
  5. Observational comparison; no causality. External prior: their own
     paper (doi 10.1002/pro.70003) reports stability models generally
     fail to capture double-mutant epistasis - a null here would agree
     with published findings, not contradict them.

AD4 DONE  (48.9s)  VERDICT: DOES NOT CAPTURE EPISTASIS
```
Verdict: **DOES NOT CAPTURE EPISTASIS — all three frozen conditions
failed, and reported plainly (task L270, AGENTS section 0).** Primary:
rho(interaction_D, own_e_b) = +0.0154, position-cluster CI
[-0.0166, +0.0465] (spans zero), position-level association null
p = 0.8459 — nowhere near the pre-registered 0.05; direction is POSITIVE
(opposite the pre-declared negative orientation, so condition (ii) fails
independently of significance); and |rho| = 0.0154 does not even reach
the no-interaction-capacity additive baseline |rho| = 0.0733 (condition
(iii) fails) — i.e. ThermoMPNN-D's non-additive term tracks observed
epistasis WORSE than the degenerate additive predictor it was supposed
to improve on, and worse than ~4x margin. Effect sizes and secondaries:
(a) the pre-registered magnitude view is a significant ANTI-correlation —
rho(|interaction_D|, |own_e_b|) = -0.0569, CI [-0.0902, -0.0229]
excluding zero, p_boot = 0.0018 — variants where D predicts larger
interaction magnitudes tend to show SMALLER observed |e.b|, the opposite
of capture; (b) distance structure is flat (rho with Ca-dist +0.0246;
near n=363 rho -0.0250 vs far n=9,232 +0.0146) so the null is not
driven by pooling near/far regimes; (c) the additive baseline
-0.0733 [-0.1021, -0.0437] EXACTLY reproduces AA4's quoted -0.0733 on
this same 9,595-row set (independent consistency check across scripts,
AGENTS section 5); (d) interaction_D runs mean -1.319 with sd 0.379 — a
systematic offset ~3.5 sd from zero (D's Siamese head calls every
double far more stabilizing than its own single-model sum), which is
rank-invariant and therefore cannot have moved the Spearman primary,
but is disclosed as the two-checkpoint limitation (printed limitation 3);
the printed cross-unit ratio 7.99 is model-units vs fitness-units and
is labeled as cross-unit context only, not a same-scale comparison.
Accounting reconciles with AD3 exactly: 10,141 rows -> 9,595 finite
own_e_b across 586 positions, 546 dropped (same frame as [AD3]'s
9,595/586 — n's reconciled per AGENTS section 5). Interpretation kept
within the frozen scope: this rules out ThermoMPNN-D's epistatic term
(as configured: ens1, CPU, this pairing) as an explanation of own_e_b at
the observed scale; it does not rule out other structure-models or
other epistasis notions, and the null AGREES with the model's own
authors' published finding (doi 10.1002/pro.70003) rather than
contradicting it. No p-value transfers, no causal claim; position-level
procedures used throughout (sections 3-4).
Files created/modified: data/external/ThermoMPNN-D/ (new shallow clone,
125,488 KB, code-repo disclosure above; includes the 6 .ckpt weights,
all <= 3GB/file cap); data/external/ThermoMPNN-D/v2_ssm.py (device patch,
backup v2_ssm.py.bak_ad4); data/external/ThermoMPNN-D/examples/configs/
local.yaml (README-sanctioned config, backup local.yaml.bak_ad4);
scripts/77_thermompnnD_double_mutant_interaction.py (new, pre-registered);
scripts/lib/position_null.py (new module; existing lib untouched);
data/processed/task77_thermompnnD_doubles.csv (new, 10,141 rows: ddg_epi_D,
ddg_single_D, interaction_D, ddg, own_e_b, ca_dist_222, region, in_test);
DEEPDIVE_LOG.md (this entry only). No existing script or result modified.
Next free script number is now 78. Runtime: smoke 6.2 s, full 48.9 s —
well under the 2h measure-first rule (measured, not extrapolated).
Anything unexpected or worth flagging: (1) The three pre-pass failures
(G0 config path, G3 gate-definition defect, batch-memory SIGKILL) are
quoted verbatim above with fixes, amendments, and the section-10
judgment rationale — flagged so the user can audit the "conformance not
sanity" calls, especially the G3 docstring amendment made after seeing
a gate result (its content only ever affected which ROWS are checked,
never a statistic). (2) SIGN DIVERGENCE AT 222: D's single-model head
gives ddG_single(222V) = +0.8071 (destabilizing) while the vendored
ThermoMPNN gives -0.0439 ([V3], ≈neutral) and literature (see [AD2])
says ≈neutral-to-slightly-destabilizing — the two ThermoMPNN generations
disagree in SIGN at exactly the residue this deep-dive is about. The
pre-registered gate was global rank agreement (rho 0.9382 >= 0.85, PASS)
and NO per-residue gate was retrofitted post hoc; this divergence is
reported as an observation, not turned into a new test. It also means
the constant subtracted in interaction_D differs from AD3's ddG_222 by
0.85 model units — again rank-invariant for the primary, but relevant
context for anyone comparing AD3 and AD4 magnitudes. (3) Secondary (a)'s
significant anti-correlation is a real (pre-registered, always-reported)
finding in the opposite direction of capture — left exactly as computed;
no directional reinterpretation. (4) Their full 10A double enumeration
is 1,822,689 rows — noted because it shows why running their CLI
wholesale (all-pairs x all-combos) was infeasible here and the
row-subsetted, G3-gated path was necessary. (5) local.yaml line endings
normalized CRLF->LF by read_text/write_text (only cosmetic side effect
of the config fix; YAML semantics unchanged). (6) Data-fetch accounting:
member-data total UNCHANGED ~196.3/200MB (the clone is a code repo
under disclosure, not a member fetch); no further member fetch was made.
---

## [AD5] — Multivariable controls on ThermoMPNN's -0.0733: SURVIVES task-literal controls (sign differs by FE granularity)
Status: PASS (executed end to end; gates G1-G3 green; pre-registered
verdict reported plainly per task L285 and AGENTS section 0).
Time started / finished: 2026-09-24 11:26:30 (right after [AD4]
appended 11:25:47) / 2026-09-24 11:26:30
What I did: AD5a — reused the exact house multivariable-control
machinery (scripts 18/24 check 1c: z-score continuous columns inside
the analysis frame, dummy-encode fixed effects with drop_first, z-score
y, statsmodels OLS with cov_type="cluster", cov_kwds={"groups":
position}, survival rule literally 1c's — SURVIVES iff the focal
coefficient's cluster-robust 95% CI excludes 0) applied to
ThermoMPNN's -0.0733 (ddG vs own_e_b). Pre-registered in the script 78
docstring BEFORE the first run: SPEC A = task-literal controls
(L284 "base fitness, RSA, position fixed effects, cluster-robust
SEs") — y = own_e_b(z) ~ focal(z) + f_bar(z) + position FE, cluster by
position; SPEC B = the exact script-24 1c control set for machinery
identity — focal(z) + f_bar_a222v(z) + grantham(z) + blosum62(z) +
rsa(z) + domain FE, cluster by position; both house variants (18 uses
f_bar/domain-less FE, 24 uses f_bar_a222v/domain) reproduced across A/B
rather than choosing one post hoc. Focals in each spec, all four always
run so nothing is chosen after seeing results: ddg (the -0.0733 under
test), delta_esm signed (ESM-2 side-by-side under identical spec and
IDENTICAL rows), |ddg|, |delta_esm|. Expected sign for signed focals:
negative (matching -0.0733/AA4 orientation); survival judged two-sided
by the 1c rule, sign reported plainly either way. Disclosure written
into the docstring before running: grepped the detection-floor and
closeout task docs for "multivariable"/"fixed effects" — only AD5's own
text matched, so NO pre-existing controlled delta_esm~own_e_b figure
exists to reproduce; the ESM side-by-side rows are NEW computations under
the reused spec and must not later be cited as replications of a
published number. Frame: V2 (10,141 rows) left-merged to phase5 on
hgvs_pro (f_bar, f_bar_a222v, f_bar_wt); grantham/blosum62 via
features.add_substitution_features; rsa+domain via
add_structural_features(load_structural_features()); ESM rows computed
on this SAME V2 frame (not script 24's phase5+model_C frame) so both
models are compared on identical rows — n's therefore differ from any
script-24 published n by frame construction (reconciled, section 5).
Gates: G1 headline identity — rho(ddg, own_e_b) on finite-own_e_b rows
must equal -0.0733 within 5e-4 and show 9,595 rows / 586 positions
(same frame as AD3/AD4, section 5); G2 design checks — focal present,
k<n, AND exact rank==k (strengthened after smoke 1, see below), else
exit 1; G3 inference finite (coef, cluster-robust SE, p; cluster count
== positions), else exit 1. Secondaries pre-registered: rank-based
partial rho(ddg, own_e_b) via scripts.lib.
partial_spearman_cluster_bootstrap (position-cluster bootstrap, seed 0)
controlling (r1) f_bar (script 18's base-fitness covariate) and (r2)
f_bar_wt (own_e_b's construction covariate — own_e_b was fitted in
scripts/17 with wild-type-arm fitness as expectation input; AD3's
section-4 control), each printed with the limitation that
partial_spearman handles ONE covariate at a time and is not a substitute
for the multivariable specs. No permutation null in this script BY
DESIGN: inference is the reused machinery's cluster-robust CI (section 4:
match the inference to the statistic the house method uses); the rank
secondaries carry the position-cluster bootstrap. ONE smoke failure
before the passing smoke, disclosed verbatim: smoke run 1 completed all
regressions but statsmodels raised
`SingularMatrixWarning: The design matrix is rank-deficient. The model
parameters are not uniquely determined.` (4x, SPEC A only). Diagnosed
numerically BEFORE any code change with an explicit null-space probe:
rank 588 < k=589; zero-variance columns: none except const; exact
duplicate columns: none; SVD null space spans ONLY {z_rsa + all 585
position dummies + const} — focal and f_bar have ZERO null-space weight.
Root cause: rsa is a PER-POSITION constant (merged by position,
scripts/lib/features.py L61-63), so with position FE it is an exact
linear function of the position indicators — collinear BY CONSTRUCTION,
not a data anomaly. Fix: the explicit rsa column removed from SPEC A
(position FE holds rsa fixed at every position — the STRICTEST form of
RSA control, so the task's "RSA" requirement is subsumed, not dropped);
G2 strengthened from k<n to exact np.linalg.matrix_rank == k; absorption
written into the docstring as a dated amendment with the probe evidence.
Because the null space excludes the focal, the focal estimate cannot
move — verified: smoke run 2 reproduced smoke run 1's SPEC A/ddg row
identically at printed precision (`coef=-0.1042 CI=[-0.1426,-0.0658]`
both runs; p 1.068e-07 -> 1.066e-07, 0.2% relative, from the
collinear-column removal in the nuisance subspace; focal identified).
Full precision to <1e-6 could not be compared because smoke run 1
printed only 4 decimals — disclosed rather than implied. Judgment
disclosure (AGENTS section 10): removing the redundant column was
treated as a conformance fix (exact mathematical redundancy, probe
evidence quoted, focal shown invariant), not a decision-rule change;
had the focal estimate moved, the run would have stopped. Two coding
bugs found at write-time, fixed before smoke run 1 ran (no result seen):
(1) focal z-scoring was skipped because the rename scheme hid it from
the z_ prefix scan — focal now z-scored exactly once inside run_spec;
(2) X was built as d[cont] which silently DROPPED THE ENTIRE FE DUMMY
SET — X is now all columns except outcome and cluster id. Smoke run 2
passed all gates in 3.0 s; full run executed once at declared default
N_BOOT=10000.
Actual output (verbatim, full run):
```
AD5 — MULTIVARIABLE CONTROLS ON ThermoMPNN's -0.0733 (scripts/78) SMOKE=False N_BOOT=10000
  merged: 10141 V2 rows; f_bar finite 10141 | f_bar_a222v 10141 | rsa 10141 | domain 10141 | grantham 10141 | own_e_b 9595
  G1 headline identity PASS: rho(ddg, own_e_b) = -0.073299 on n=9595, 586 positions (matches [AD4](c)/[AA4] -0.0733)
SPEC A — task-literal: f_bar + POSITION FE (rsa absorbed by FE: per-position constant), cluster-robust (L284)
  note: rsa is per-position constant -> exactly collinear with position FE; FE holds it fixed at every position (strictest RSA control), so the explicit rsa column is redundant by construction (smoke-run-1 amendment, docstring G2)
  after dropna: n=9595 (dropped 546)
  A        focal=ddg              coef=-0.1042 CI=[-0.1426,-0.0658] p=1.066e-07  -> SURVIVES  (n=9595, 586 position clusters, k=588)
  A        focal=delta_esm        coef=-0.0483 CI=[-0.0900,-0.0066] p=0.02324  -> SURVIVES  (n=9595, 586 position clusters, k=588)
  A        focal=abs_ddg          coef=-0.0995 CI=[-0.1369,-0.0620] p=1.956e-07  -> SURVIVES  (n=9595, 586 position clusters, k=588)
  A        focal=abs_delta_esm    coef=+0.0221 CI=[-0.0119,+0.0561] p=0.2031  -> does NOT survive  (n=9595, 586 position clusters, k=588)
SPEC B — exact script-24 1c set: f_bar_a222v + grantham + blosum62 + rsa + DOMAIN FE
  after dropna: n=9595 (dropped 546)
  B        focal=ddg              coef=+0.0790 CI=[+0.0485,+0.1094] p=3.673e-07  -> SURVIVES  (n=9595, 586 position clusters, k=8)
  B        focal=delta_esm        coef=+0.0353 CI=[+0.0123,+0.0584] p=0.002679  -> SURVIVES  (n=9595, 586 position clusters, k=8)
  B        focal=abs_ddg          coef=+0.0780 CI=[+0.0469,+0.1090] p=8.679e-07  -> SURVIVES  (n=9595, 586 position clusters, k=8)
  B        focal=abs_delta_esm    coef=+0.0289 CI=[+0.0075,+0.0503] p=0.008079  -> SURVIVES  (n=9595, 586 position clusters, k=8)
SECONDARIES — rank-based partials (position-cluster bootstrap)
  (r1 f_bar (script 18 covariate)) partial rho(ddg, own_e_b | f_bar) = -0.0339 [-0.0625, -0.0050] p_boot=0.0236 n=9595 clusters=586 (single-covariate: NOT a substitute for specs A/B)
  (r2 f_bar_wt (own_e_b construction covariate)) partial rho(ddg, own_e_b | f_bar_wt) = -0.1101 [-0.1425, -0.0769] p_boot=0.0000 n=9595 clusters=586 (single-covariate: NOT a substitute for specs A/B)
VERDICT
  SPEC A focal=ddg (the -0.0733 under test): SURVIVES the task-literal controls
    coef=-0.1042 CI=[-0.1426,-0.0658] p=1.066e-07 n=9595 | sign expected negative: yes
  ESM-2 side-by-side (same spec, same rows): specA coef=-0.0483 p=0.02324 SURVIVES | specB coef=+0.0353 p=0.002679 SURVIVES
  saved 8 regression rows -> task78_thermompnn_controls.csv
AD5 DONE  (43.4s)  VERDICT: SURVIVES the task-literal controls
```
Verdict: **SURVIVES the task-literal controls** — SPEC A focal=ddg
coef -0.1042 per SD, cluster-robust CI [-0.1426, -0.0658], p =
1.066e-07, negative as pre-declared, n = 9,595 in 586 position
clusters. The controlled coefficient is LARGER in magnitude than the
raw -0.0733 (standardized scales differ, so magnitudes are not
directly interchangeable: raw is a rank correlation on unstandardized
levels, coef is SD-own_e_b per SD-ddg net of f_bar and position FE) —
the direction of interest is that there is NO attenuation to nothing:
within-position, net of base fitness, the association persists and
strengthens. ESM-2 side-by-side under identical spec and identical
rows: SPEC A delta_esm coef -0.0483 [-0.0900, -0.0066], p = 0.02324,
SURVIVES (also negative); |delta_esm| does NOT survive (coef +0.0221,
CI spans 0) while |ddg| does (-0.0995). Rank-based secondaries: (r1)
controlling f_bar the partial rho attenuates ~54% from -0.0733 to
-0.0339 [-0.0625, -0.0050] but still excludes zero at p_boot = 0.0236
— base fitness explains part of the headline, not all of it; (r2)
controlling the own_e_b construction covariate f_bar_wt STRENGTHENS it
to -0.1101 [-0.1425, -0.0769], p_boot < 1/10000 — the construction
expectation suppresses rather than manufactures the association.
Accounting reconciles: 10,141 merged -> 9,595 finite own_e_b, 546
dropped, 586 positions — identical frame to AD3/AD4 (section 5).
Files created/modified: scripts/78_thermompnn_multivariable_controls.py
(new, pre-registered docstring); data/processed/
task78_thermompnn_controls.csv (new, 8 regression rows);
DEEPDIVE_LOG.md (this entry only). Existing scripts, libs, and results
untouched (stats.py imported only). Next free script number is now 79.
Runtime: smoke 3.0 s, full 43.4 s (partial-Spearman bootstraps at
10,000 draws dominate) — measured, far under the 2h rule.
Anything unexpected or worth flagging: (1) THE SIGN FLIPS BETWEEN FE
GRANULARITIES, and this is reported as-is rather than resolved
post-hoc: SPEC A (position FE, within-position variation) gives ddg
-0.1042 negative, while SPEC B (domain FE + grantham + blosum62 +
f_bar_a222v + rsa, the literal script-24 1c set) gives ddg +0.0790
POSITIVE, both with CIs excluding zero and both printing SURVIVES.
Both specs were pre-registered and both are always reported; the
primary verdict uses SPEC A because the task text (L284) literally
names position fixed effects. SPEC A and SPEC B differ in BOTH FE
granularity and control set, so the flip cannot be attributed to one
factor without a decomposition that was NOT pre-registered — flagged as
open, not tested post hoc. Reading held to the frozen scope: the
between-position component of the association runs opposite to the
within-position component (a Simpson-type structure across position
levels), so "-0.0733 survives controls" is TRUE for the task-literal
within-position spec and the association is NOT uniformly signed across
specs; anyone quoting a single controlled number should state which FE
granularity. (2) ESM-2's sign behaves the same way (SPEC A negative
-0.0483, SPEC B positive +0.0353), so the flip is a property of the
frame/controls, not of ThermoMPNN specifically. (3) The smoke-1
rank-deficiency, its null-space diagnosis, the rsa-absorption fix, the
strengthened G2, and the smoke1-vs-smoke2 invariant-focal verification
are all quoted verbatim above; the p-value moved 0.2% relative while
coef and CI were unchanged at printed precision — full <1e-6
verification was impossible because smoke 1 printed only 4 decimals
(disclosed rather than implied). (4) Spec A attenuates nothing —
limitation 2 printed with results correctly notes that WITHIN-position
identification discards between-position information, which is exactly
where the sign disagreement lives (see (1)). (5) |ddg| survives in
both specs but |delta_esm| survives only in B — reported without
directional reinterpretation. No data fetches; no member-data added
(session total unchanged ~196.3/200MB).
---

## [AD6] — Alignment depth discriminator: |delta_ESM| tracks per-position Neff, ThermoMPNN's residual does not — CONFIRMED pooled (region 4 reverses)
Status: PASS (executed end to end; gates G1-G5 green after one disclosed
smoke failure; frozen R1/R2 both PASS -> CONFIRMED with the
pre-registered heterogeneity caveat and scope limits attached, per task
L287-298 and AGENTS section 0).
Time started / finished: 2026-09-24 11:39:00 (right after [AD5]
appended 11:38:38) / 2026-09-24 11:39:00
What I did: AD6a — reused the one MTHFR alignment that exists (NO
refetch, task wording "reuse, don't refetch"):
data/external/ProteinGym/MTHR_HUMAN_2023-08-07_b02.a2m (3,316,659 B),
pulled by AB1 inside the ProteinGym fetch; AB3 SKIPPED so nothing newer
exists; session member-data total unchanged ~196.3/200MB. Format
measured BEFORE writing the script 79 docstring: 4,783 records; query
`MTHR_HUMAN/1-656` (full-length UniProt 1..656); 26 query residues are
lowercase (a3m insertions relative to match state); filtering every
record to [A-Z-] yields exactly 630 chars for ALL 4,783 records ->
match state = 630 columns. Computed per-position depth with NO model
fitted: Neff per column (PRIMARY) = sum_i w_i * occupancy with global
reweighting w_i = 1/|{j : id >= 0.8}|, id = non-gap matches / 630
(fixed denominator, gaps count against, threshold 0.8 frozen);
conservation (SECONDARY) = 1 - H/log(22) over {20 AA + gap + other}.
Mapping: UniProt position p -> query char raw[p-1] for identity, match
column via uppercase-cumsum for depth; lowercase-query positions would
be excluded (count printed). AD6b — position-level test (each analysis
row IS one position, so the house row bootstrap IS a position
bootstrap): per-position mean signals yE = mean|delta_esm|,
yT1 = mean|pred_eb| ("ThermoMPNN's residual", most-literal reading of
the task wording: its non-additive term beyond additive singles),
yT2 = mean|ddg|, yT3 = mean|interaction_D| (AD4 native
ThermoMPNN-D, SECONDARY, never part of the rule); Spearman(signal,
depth) with the house position-cluster bootstrap (scripts.lib.stats,
seed 0) for pooled + ALL FOUR regions on Neff (full region breakdown
required by task L296-297); conservation pooled-only for yE/yT1/yT2
(frozen scope). FROZEN RULES written into the docstring before running:
R1 = pooled rho(yE,Neff) > 0 AND 95% CI excludes 0; R2 = pooled CIs of
rho(yT1,Neff) AND rho(yT2,Neff) both include 0; CONFIRMED iff R1 AND
R2 -> then state the evaluator's proposed rule WITH printed scope
limits; NOT CONFIRMED -> report which of R1/R2 failed, plainly. If
CONFIRMED but any region has significant NEGATIVE yE tracking, print a
heterogeneity caveat beside the rule. Always-reported secondaries (a)
yT3 all scopes vs Neff, (b) conservation pooled, (c) paired delta-rho
rho(yE)-rho(yT1) seed 1, (d) signed position means (descriptive, no CI,
labeled). Gates: G1 file integrity (4,783 / 656 / 630, <=1% bad);
G2 mapping identity (query letter == V2 wt_aa for every mapped
position, exit 1 on mismatch); G3 pred_eb-degeneracy disclosure gate
(best-constant k, max|pred_eb-(ddg+k)| < 1e-9 — the EXPECTED structural
fact, printed not hidden, per the section-5 column-identity duty);
G4 depth sanity (Neff(col) finite in [1,4783], occupancy >= 1; global
sum(w) printed next to ProteinGym metadata 646.2 — definition
difference disclosed, NOT gated); G5 region sizes >= MIN_N=20
(pre-registered). Disclosed judgment (sections 9/10): AB3b's floor
("couplings from it would be unusable ... do not proceed") gates
TRAINING A POTTS MODEL on the shallow alignment (AB4's scope); task
AD6a explicitly instructs computing per-column depth statistics from
this alignment, and column counts/entropy fit no model and need no
couplings — proceeding under AD6a's literal instruction with the
shallowness limitation printed was judged consistent with the floor's
scope, flagged for user revisit. ONE smoke failure, verbatim: smoke run
1 `*** G2 FAIL: position 244: query 'L' != V2 wt_aa 'T' (mapping
broken)`. Diagnosis before any change: a standalone offset probe gave
`offset +0: match 586/586 fails(ex)=[]` while `offset -1: 39/586`,
`+1: 40/586`, `-39: 36/586`, `-40: 38/585`, `+40: 37/558` — the
numbering is perfect direct UniProt, so the gate's LOOKUP was wrong:
it indexed the raw 656-char query with the match-COLUMN number from
qcol_of_pos, conflating the two index spaces (16 lowercase positions in
1..16 made position 244 read query[227]='L' instead of
query[243]='T'). Three-way confirmed on raw index: query[243]='T',
V2 wt='T', ProteinGym scores mutants `['T244A', 'T244C', 'T244D']`.
Fix: G2 letter lookup changed to raw query[p-1]; the depth-column
mapping (qcol_of_pos used only for column extraction) was already
correct and unchanged; fix written as a dated comment in the code and
quoted here. A gate-lookup bug (code vs spec), no statistic, threshold,
or decision rule touched — judgment disclosed so the user can revisit.
Smoke run 2 passed all gates in 2.1 s; full run executed once at
declared default N_BOOT=10000.
Actual output (verbatim, full run):
```
AD6 — ALIGNMENT DEPTH DISCRIMINATOR (scripts/79) SMOKE=False N_BOOT=10000
  G1 file integrity PASS: 4783 records, query 'MTHR_HUMAN/1-656' len 656, match state 630 cols, 0 non-conforming records
  query mapping: 630 match positions, 26 insertion (lowercase) positions with no column
  G4 depth sanity PASS: Neff(col) range [31.8, 1215.4] | global sum(w) = 1215.4 vs ProteinGym metadata MSA_N_eff = 646.2 (DIFFERENT definitions - reconciliation note, not equality; id>=0.8 denom=630 here)
  merged V2 10141 rows; interaction_D finite 10141 | delta_esm 10141 | pred_eb 10141 | ddg 10141
  G3 pred_eb degeneracy CONFIRMED (expected structural fact): pred_eb = ddg -0.043862 exactly (max|resid| = 4.441e-16; k = ddG_222 = -0.0439) -> signed yT1/yT2 are affine (identical signed rho); |.| versions differ only by the constant. T1/T2 carry ONE ThermoMPNN information source.
  G2 mapping identity PASS: 586 distinct positions query==V2 wt_aa; excluded (query insertion) positions: none
  position table: 586 positions (regions: {1.0: 108, 2.0: 135, 3.0: 174, 4.0: 169})
  G5 region sizes PASS: all >= 20 ({1.0: 108, 2.0: 135, 3.0: 174, 4.0: 169})
PRIMARY DEPTH METRIC: Neff per column — pooled + ALL REGIONS
  [neff] pooled   yE   rho=+0.1714 [+0.0918, +0.2471] p_boot=0.0000 n=586
  [neff] pooled   yT1  rho=+0.0069 [-0.0716, +0.0878] p_boot=0.8708 n=586
  [neff] pooled   yT2  rho=+0.0080 [-0.0705, +0.0884] p_boot=0.8476 n=586
  [neff] pooled   yT3  rho=-0.0211 [-0.1034, +0.0584] p_boot=0.6036 n=586
  [neff] region1  yE   rho=+0.1672 [-0.0203, +0.3497] p_boot=0.0800 n=108
  [neff] region1  yT1  rho=+0.1386 [-0.0601, +0.3243] p_boot=0.1716 n=108
  [neff] region1  yT2  rho=+0.1354 [-0.0619, +0.3217] p_boot=0.1776 n=108
  [neff] region1  yT3  rho=-0.0048 [-0.1946, +0.1818] p_boot=0.9532 n=108
  [neff] region2  yE   rho=+0.0843 [-0.0818, +0.2499] p_boot=0.3318 n=135
  [neff] region2  yT1  rho=-0.0875 [-0.2508, +0.0830] p_boot=0.3404 n=135
  [neff] region2  yT2  rho=-0.0873 [-0.2503, +0.0828] p_boot=0.3378 n=135
  [neff] region2  yT3  rho=-0.2063 [-0.3625, -0.0352] p_boot=0.0176 n=135
  [neff] region3  yE   rho=+0.1725 [+0.0250, +0.3116] p_boot=0.0194 n=174
  [neff] region3  yT1  rho=+0.0577 [-0.0842, +0.1946] p_boot=0.4142 n=174
  [neff] region3  yT2  rho=+0.0540 [-0.0877, +0.1916] p_boot=0.4486 n=174
  [neff] region3  yT3  rho=+0.0310 [-0.1200, +0.1767] p_boot=0.6998 n=174
  [neff] region4  yE   rho=-0.2373 [-0.3795, -0.0853] p_boot=0.0042 n=169
  [neff] region4  yT1  rho=+0.1198 [-0.0331, +0.2680] p_boot=0.1230 n=169
  [neff] region4  yT2  rho=+0.1223 [-0.0312, +0.2698] p_boot=0.1164 n=169
  [neff] region4  yT3  rho=+0.1327 [-0.0227, +0.2806] p_boot=0.0894 n=169
SECONDARY DEPTH METRIC: conservation (pooled only, frozen)
  [cons] pooled   yE   rho=-0.0119 [-0.0963, +0.0703] p_boot=0.7760 n=586
  [cons] pooled   yT1  rho=+0.3937 [+0.3193, +0.4633] p_boot=0.0000 n=586
  [cons] pooled   yT2  rho=+0.3920 [+0.3178, +0.4618] p_boot=0.0000 n=586
SECONDARY (c): paired delta-rho rho(yE) - rho(yT1), seed 1
  delta-rho (yE - yT1 vs Neff, pooled) = +0.1645 [+0.0545, +0.2722] p_boot=0.0030 n=586 (CI excluding 0 = the two signals track depth differently)
SECONDARY (d): signed position means — DESCRIPTIVE only (no CI)
  rho(mean delta_esm, Neff) = +0.2398  [descriptive point estimate; not a pre-registered test]
  rho(mean pred_eb, Neff) = +0.0147  [descriptive point estimate; not a pre-registered test]
VERDICT (frozen rules R1/R2)
  R1 'ESM tracks depth': pooled rho(yE,Neff)=+0.1714 [+0.0918,+0.2471] >0 & CI excludes 0 -> PASS
  R2 'ThermoMPNN residual does not': yT1 CI=[-0.0716,+0.0878] incls 0 | yT2 CI=[-0.0705,+0.0884] incls 0 -> PASS
  CONFIRMED -> evaluator's proposed rule, as this project found it on MTHFR:
    "PLM background-awareness requires evolutionary depth; structure-based models don't need it."
  HETEROGENEITY CAVEAT: region(s) with significant NEGATIVE yE tracking: [('region4', -0.2373)] - rule holds pooled, not uniformly.
  Scope limits attached: single globally shallow alignment (Neff/L=0.99, 'Low'); relative per-position depth only; one protein; observational.
  saved 586 position rows -> task79_depth_positions.csv
  saved 24 association rows -> task79_depth_associations.csv
AD6 DONE  (32.1s)  VERDICT: CONFIRMED (R1 pass, R2 pass)
```
Verdict: **CONFIRMED per the frozen rule — with the pre-registered
heterogeneity caveat attached and reported prominently below.** R1
PASS: pooled rho(|delta_ESM| position-mean, Neff) = +0.1714, bootstrap
CI [+0.0918, +0.2471] excluding zero at p_boot < 1/10000 (n = 586
positions). R2 PASS: pooled rho(yT1) = +0.0069 CI [-0.0716, +0.0878]
and rho(yT2) = +0.0080 CI [-0.0705, +0.0884] both include zero —
ThermoMPNN's residual shows NO detectable depth tracking, with the CI
width (~+/-0.08) bounding any pooled association to |rho| < ~0.09. The
paired discrimination is itself significant: delta-rho = +0.1645
[+0.0545, +0.2722], p_boot = 0.0030 — the two signals track depth
differently, not just one reaching significance. The evaluator's rule
is therefore stated as this project's finding, WITH the printed scope
limits: "PLM background-awareness requires evolutionary depth;
structure-based models don't need it" (single, globally shallow
alignment Neff/L = 0.99 'Low'; relative per-position depth only; one
protein; observational). FULL REGION BREAKDOWN (task L296, reported
whether it supports or undermines): yE positive in region 3 (+0.1725
[+0.0250, +0.3116], p = 0.0194), marginal in region 1 (+0.1672, CI
just spans 0, p = 0.0800), null in region 2 (+0.0843, p = 0.3318), and
SIGNIFICANTLY NEGATIVE in region 4 (-0.2373 [-0.3795, -0.0853],
p = 0.0042) — the pre-registered caveat fired: **the rule holds pooled
and in region 3, but region 4 — the very region this task was written
about — runs the OPPOSITE way** (within region 4, deeper columns show
SMALLER ESM background-shift). Whatever produces the pooled positive
association does not describe region 4, and stating the rule without
that sentence would misrepresent the data. ALWAYS-REPORTED
SECONDARIES, plain: the conservation secondary shows a sharp
DISSOCIATION — ESM's signal does not track conservation (rho = -0.0119
[-0.0963, +0.0703], null) while ThermoMPNN's residual tracks it
strongly (rho = +0.3937 [+0.3193, +0.4633], p < 1/10000): depth
(number of sequences seen) and conservation (functional constraint) are
different axes, and the two model families load on different ones here
(observed, not interpreted further — no mechanism claim). yT3 (AD4's
native ThermoMPNN-D interaction) is null pooled (-0.0211, CI spans 0)
and significantly negative only in region 2 (-0.2063 [-0.3625, -0.0352],
p = 0.0176) — reported as a secondary, not folded into the rule.
Signed means (descriptive only): rho(mean delta_esm, Neff) = +0.2398,
rho(mean pred_eb, Neff) = +0.0147. Accounting reconciles with AD3/AD4/
AD5: 586 positions (regions 108+135+174+169 = 586), 10,141 input rows,
zero rows lost to insertion positions (all 26 lowercase query positions
lie outside the V2 40..644 range) (section 5).
Files created/modified: scripts/79_alignment_depth_discriminator.py
(new, fully pre-registered docstring incl. the frozen R1/R2 and the
AB3b-floor judgment); data/processed/task79_depth_positions.csv (new,
586 rows: position, region, neff, cons, n_var, yE/yT1/yT2/yT3, signed
means); data/processed/task79_depth_associations.csv (new, 24 rows —
every rho incl. the delta-rho); DEEPDIVE_LOG.md (this entry only).
Existing scripts, libs, results untouched (stats.py imported only).
Next free script number is now 80. Runtime: smoke 2.1 s, full 32.1 s
— measured, far under the 2h rule. No data fetch (a2m reused from
AB1; session member total unchanged ~196.3/200MB).
Anything unexpected or worth flagging: (1) The smoke-1 G2 failure and
its index-space root cause are quoted verbatim above with the offset
probe evidence (586/586 at offset 0, 26-40/586 at every other offset)
— the gate LOOKUP was fixed, the depth mapping was already correct, and
the judgment is disclosed for revisit. (2) THE REGION-4 SIGN REVERSAL
is the headline caveat: region 4's ESM-depth association is -0.2373
significant, opposite the pooled rule; anyone quoting AD6's CONFIRMED
verdict must quote this beside it — the caveat was pre-registered and
printed by the script itself, not added after the fact. (3) The
conservation dissociation (ESM null, ThermoMPNN +0.39) is a strong
always-reported secondary that sharpens the rule: it suggests
"different evolutionary axes", reported as observation only. (4) G3's
degeneracy gate put on the record that the vendored ThermoMPNN
"residual" pred_eb is EXACTLY ddg + ddG_222 (max|resid| 4.4e-16) — so
T1/T2 are one information source by construction; T3 (AD4's native
interaction) is the independent structure-side check and is null pooled.
(5) G4: our global sum(w) = 1215.4 vs ProteinGym metadata 646.2 —
different reweighting definitions, printed as reconciliation (NOT an
equality claim); our per-column Neff range [31.8, 1215.4] shows the
relative-depth variation the test relies on exists even in this
globally shallow ('Low') alignment. (6) AB3b-floor judgment (column
statistics vs Potts training) disclosed in docstring and above — user
can revisit; if that judgment is overturned, AD6a would be blocked on
the same floor as AB4.
---
## [AD7] — Dimer scoring (6FCX A+B vs chain A alone): region-4 §12.4 anchor HOLDS under dimer scoring

Status: EXECUTED — PASS (VERDICT: HOLDS under the frozen S3 rule)

Time: start 11:54:00 (after [AD6] 11:53:27), finish 12:21:54. Script-80 full run 161.9s (frag A 3.0s, frag AB 3.6s, full A 11.9s, full AB 27.4s, statistics ~116s); smoke 8s + fragment CLIs.

What I did:
- Read task doc AD7 (L300-305): "rerun ThermoMPNN scoring with both 6FCX chains (dimer) vs chain A alone, at least region-4 positions, check region-4 discriminator result (Part II §12.4) holds." AMBIGUITY (logged, most-literal anchor): Part II §12.4 is an external evaluator document, NOT in this repo (grep finds no relevant "12.4"). Anchored to the two in-repo region-4 records before running: (E) ESM-2/e.b region-4 failure in data/processed/task_region_check.csv (quoted verbatim as S5, read-only, NOT recomputed — and stated in output that ThermoMPNN dimer scoring cannot alter an ESM number); (T) ThermoMPNN's side of §12 = per-region rho(ddg, own_e_b) from V2, recomputed for BOTH scorings.
- Wrote scripts/80_ad7_dimer_scoring.py with the pre-registered docstring (gates G1/G2/G2b/G3/G4, statistics S1-S5, frozen S3 verdict rule, smoke scope, timing cap 7,200s projection stop) BEFORE running. Machinery = script 68's exact path, helpers chain_residues/map_and_check_wt/write_fragment imported via importlib (not rewritten); CLI mirrored with only --chain exposed (68's run_cli hardcodes "A"); vendored ThermoMPNN READ-ONLY, ZERO third-party edits (unlike AD4's disclosed patches); same thermoMPNN_default.pt, same data/raw/6FCX.pdb.
- Verified the vendor's multi-chain path before writing (read-only): alt_parse_PDB iterates the --chain string letter-by-letter ("AB" -> parse A, then B, concat_seq accumulates both, coords_chain_A and coords_chain_B both populated); TransferModel.forward featurizes the WHOLE complex once (chain-B atoms enter the MPNN spatial neighbour graph) then loops a cheap per-mutation head -> peak memory independent of mutation count, no chunking needed. Diagnostic probe confirmed on the AB fragment: num_of_chains=2, seq_chain_A/seq_chain_B + coords keys both present, X.shape=(1,100,4,3), chain_encoding=[1 2], residue_idx junction 49->150 (proper chain break).
- Pre-run external diagnostic (read-only, quoted in this entry): fragment 200-249 AB-minus-A delta was EXACTLY 0 (max|D|=0.000e+00, 0/1000 nonzero) — kNN probe explained it as physics, not defect: 0/50 A nodes in that window have any B neighbour in their 30-nearest (nearest B 43.07-66.11 A vs 30th-A 12.00-21.49 A), and struct-table interface positions (dimer rel burial > 0) have inter-chain heavy-atom contacts of 2.4-5.9 A at 40, 51, 361, 386-391, 489-571, 624-628 (mostly region 4). Added gate G2b (BEFORE any full run): dimer-minus-monomer must be nonzero at some variants/positions or STOP as pipeline defect; smoke's off-interface window having exactly-0 deltas documented as expected physics.
- Found and fixed by review before the full run (disclosed): the A/B split cut in the AB CSV must be their SLOT count (max full-A position + 1 = 612; their indexing is resi-40-style with '-' gap slots, positions 0..611 with rows only at the 596 observed — proven by 68's historical set-equality gate), NOT len(chain_residues(A))=596, which would have misclassified the 16 tail rows >= 596 (the G2 set-equality gate would have caught it as a STOP, but fixed properly instead); plus two merge/label bugs (shared 'position' column collision in the G1 merge; non-contiguous group labels into paired_delta_rho after dropna) — all three found by reading the written code before running, not from a failed run.
- SMOKE=1 first (exit 0, ~8s + fragment CLIs): both fragment gates PASS, G4 struct join PASS, S5 quote printed, S1 monomer-only at N_BOOT=300; disclosed smoke scope = full dimer join and S2/S3 verdict code ran first at full scale in the full run.
- Full run N_BOOT=10000, exit 0.

Actual output (verbatim from /private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/ad7_full.log):
  G1: "G1 PASS: monomer rerun reproduces V2 ddg at all 10141 rows, max|delta| = 0.000e+00 (< 1e-06)" and "script-68 map gate re-passed at 596 chain-A positions; rows 11920, elapsed 11.9s (0.0010 s/pred)" and "A slot count from their full-A CSV = 612 (observed rows 596, resi span 612)"
  G2: "G2 parse PASS: A part 11920 rows / 596 pos == 612 expected; B part 11800 rows / 590 pos == 590 expected" ; "rows: CSV 23720 vs (n_A+n_B)*20 = 24040  <-- NOTE: non-rectangular; accounting by join" (difference = 16 A gap-slot positions x 20 emitting no rows; joins gated, disclosed as NOTE mirroring script 68)
  G3: "G3 PASS: dimer join complete at all 10141 rows, wildtypes agree with V2 at every row"
  G2b: "G2b sanity: 10125 variants / 586 positions have nonzero dimer-minus-monomer (pre-run measured: 39 interface residues, contacts 2.4-5.9 A)"
  S1 (rho(scoring, own_e_b), position-cluster bootstrap, N_BOOT=10000):
    "[mono ] pooled   rho=-0.0733 [-0.1021,-0.0437] p=0.0000 n=9595  (excl 0)"
    "[dimer] pooled   rho=-0.0657 [-0.0946,-0.0356] p=0.0000 n=9595  (excl 0)"
    "[mono ] region1  rho=-0.1323 [-0.1815,-0.0827] p=0.0000 n=1906  (excl 0)"
    "[dimer] region1  rho=-0.1350 [-0.1844,-0.0849] p=0.0000 n=1906  (excl 0)"
    "[mono ] region2  rho=+0.0732 [+0.0033,+0.1404] p=0.0412 n=2220  (excl 0)"
    "[dimer] region2  rho=+0.0732 [+0.0033,+0.1404] p=0.0410 n=2220  (excl 0)"
    "[mono ] region3  rho=-0.0765 [-0.1307,-0.0211] p=0.0068 n=2609  (excl 0)"
    "[dimer] region3  rho=-0.0763 [-0.1306,-0.0202] p=0.0084 n=2609  (excl 0)"
    "[mono ] region4  rho=-0.1237 [-0.1751,-0.0716] p=0.0000 n=2860  (excl 0)"
    "[dimer] region4  rho=-0.1101 [-0.1616,-0.0577] p=0.0000 n=2860  (excl 0)"
  S2: "rho(mono, dimer) pooled = +0.982409 [+0.972004,+0.990475] n=10141" ; "Delta: mean +0.02020, mean|D| 0.03889, max|D| 2.11093 (model units, 10141 variants)" ; per-region mean over positions of mean|Delta|: "region1 ... = 0.00622 [0.00229,0.01123] (n_pos=108)", "region2 ... = 0.00015 [0.00008,0.00022] (n_pos=135)", "region3 ... = 0.03182 [0.01187,0.05905] (n_pos=174)", "region4 ... = 0.09745 [0.06874,0.13056] (n_pos=169)"
  S3 (frozen rule): "(a) sign unchanged or both null: PASS (mono sign -1, dimer -1, both_null=False)" ; "(b) CI zero-status unchanged: PASS (excl0 mono=True, dimer=True)" ; "(c) paired Delta-rho_4 CI includes 0: PASS — Delta-rho_4 = -0.0136 [-0.0302,+0.0009] p=0.0706" ; "pooled Delta-rho (context): -0.0076 [-0.0152,-0.0007] p=0.0292 — NOT part of verdict"
  S4: "burial coverage on 586 analysis positions: NaN 0 (excluded from S4 only), >0 39, == 547" ; "[pooled] rho(|Delta|-pos-mean, dimer-rel-burial) = +0.4268 [+0.3624,+0.4852] p=0.0000 n=586" ; "[region4] rho(...) = +0.6371 [+0.5439,+0.7100] p=0.0000 n=169" ; "interface(>0, n=39) - non-interface(n=547) mean position mean|Delta| = +0.42736 [+0.32047,+0.54922] (position bootstrap, seed 2)"
  S5 (verbatim ESM anchor quotes, read-only): "rank-based pooled    rho=+0.1165 CI=[+0.0891,+0.1436] p_boot=0.0000" ; "rank-based region_4  rho=+0.0248 CI=[-0.0226,+0.0711] p_boot=0.3094 includes0=True overlaps_pooled=False n=3046" ; "calibrated pooled    rho=-0.1338 CI=[-0.1624,-0.1053] p_boot=0.0000" ; "calibrated region_4  rho=-0.0634 CI=[-0.1033,-0.0233] p_boot=0.0020 includes0=False overlaps_pooled=False n=3046" ; "Plain statement: these are ESM-2/e.b numbers; ThermoMPNN dimer scoring CANNOT alter them."
  VERDICT: "region-4 result HOLDS under dimer scoring: sign (or both-null), CI zero-status, and paired Delta-rho all unchanged — the structural half of §12.4 is NOT a monomer-scoring artifact (per the in-repo anchors printed in S5; Part II itself is not in this repo)."
  "AD7 DONE  (161.9s)  VERDICT: HOLDS under dimer scoring (ESM side untouched by construction)"

Verdict: PASS — region-4 result HOLDS under dimer scoring (all three frozen S3 conditions PASS). Effect sizes with the significance, reported plainly: the dimer rerun moves rankings very little overall (rho mono-vs-dimer +0.982), yet the scoring change concentrates precisely at the interface (S4 pooled +0.4268, region-4 +0.6371, interface-vs-not +0.427 — all CIs far from 0), and region 4's own mean|Delta| is 0.097 vs region 2's 0.00015 (~650x), i.e. the change is real and lands where the dimer interface is. Two shifts do NOT include zero and are reported as results, not hidden: (1) region-4 rho weakened from -0.1237 to -0.1101 but the paired delta CI includes 0 (Delta-rho_4 = -0.0136 [-0.0302,+0.0009] p=0.0706 -> condition (c) PASS); (2) the POOLED delta-rho excludes 0 (pooled -0.0076 [-0.0152,-0.0007] p=0.0292) — a small pooled weakening of the association under dimer scoring, explicitly NOT part of the frozen verdict (frozen rule was region-4-scoped; disclosed here rather than folded in post-hoc). The verdict's scope limits are in the script output: single structure, single dimer conformation, vendor multi-chain path unmodified, and the §12.4 anchor is in-repo records because Part II is external; ESM's half is untouched by construction.

Files: NEW scripts/80_ad7_dimer_scoring.py; NEW data/processed/task80_dimer_variants.csv (10,141 rows), task80_dimer_positions.csv (586 rows, incl. burial columns), task80_region_rhos.csv (10 rows). Ephemeral CLI CSVs in TMP (ad7_frag_A, ad7_frag_AB, ad7_full_A, ad7_full_AB; logs ad7_smoke.log, ad7_full.log). No existing script, lib module, or result modified; vendored data/external/ThermoMPNN untouched (zero third-party edits). Next free script number: 81.

Unexpected: (1) Part II §12.4 absent from repo — resolved by pre-logged most-literal anchor, flagged for revisit if Part II surfaces; (2) fragment AB deltas exactly 0 at first — diagnosed pre-run as kNN-locality physics (0/50 A nodes have a B neighbour in that window) with the G2b gate added before the full run rather than rationalized after; (3) the A/B split cut needed slot-count (612) not observed-count (596) — found by review of the written code before running; (4) AB CSV is non-rectangular (23720 vs 24040 by 16 gap-slot positions) — accounted by join, printed as NOTE; (5) pooled delta-rho excludes 0 while region-4's does not — reported plainly, outside the frozen rule.
---
## [AD8] — Joint rank model: semipartial contributions both directions — BOTH carry independent information (case i)

Status: EXECUTED — PASS (VERDICT: case i, both semipartial CIs exclude 0 on the pooled matched set)

Time: start 12:22:00 (after [AD7] 12:21:54), finish 12:27:45. Script-81 full run 41.8s (N_BOOT=10000); smoke 1.2s (N_BOOT=300).

What I did:
- Read task AD8 (L307-312): on Z1's matched-n intersection, fit both predictors jointly (rank-based) and report semipartial contributions in each direction — a decisive replacement for the "CIs overlap" comparison.
- Located Z1's intersection from the prior session (CLOSEOUT_LOG [Z1]: "[Z1a] intersection n=9595 pos=586 (ESM loses 1162, Thermo loses 0)"; saved CSV data/processed/task_Z1_matched_n_headtohead.csv). Verified by accounting that V2.dropna(own_e_b) IS that intersection (V2 10,141 -> own_e_b finite 9,595 -> +delta_esm finite 9,595; V2 delta_esm NaN total 0).
- Wrote scripts/81_joint_semipartial.py with the pre-registered docstring (gates G1-G5, components, position-cluster bootstrap with ranks recomputed inside every draw, the pooled decision rule cases i/ii/iii, region rows as secondary/descriptive with no decision rule, limitations, smoke=N_BOOT=300) BEFORE running.
- Gates (all pre-registered, exact-value where a prior record exists): G1 n/pos == Z1's logged 9595/586; G2 zero-order rhos == Z1's matched CSV to <1e-12 (read from the file, not hardcoded); G3 Z1 Thermo rho == AD7's task80_region_rhos.csv pooled mono rho to <1e-12 (cross-session, two independent runs — agreement found pre-run at 2.8e-17); G4 pred_eb (Z1's Thermo predictor) rank-identical to ddg (this script's) at every row — rank-based results are the same variable, disclosed not silently switched; G5 closed-form validity 1-rho_ET^2 > 1e-6 and R2_full >= max zero-order R2.
- Statistics: ranks (average = Spearman scale) on y=own_e_b, E=delta_esm, T=ddg; R2_full exact 2-predictor closed form; unique_T = R2_full - R2_E (semipartial of ThermoMPNN given ESM-2), unique_E = R2_full - R2_T (semipartial of ESM-2 given ThermoMPNN), shared commonality; position-cluster bootstrap (seed 0, positions resampled with replacement, ALL ranks recomputed per draw = re-derivation null); p two-sided. Secondary: same machinery per region 1-4 (heterogeneity check per AD6/AD7 precedent), CIs on semipartials only, no decision rule attached.
- SMOKE=300 first (exit 0, 1.2s, all gates PASS), then full N_BOOT=10000 (exit 0, 41.8s).

Actual output (verbatim from /private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/ad8_full.log):
  "accounting: V2 10141 -> own_e_b finite 9595 -> +delta_esm finite 9595 (V2 delta_esm NaN total 0)"
  "G1 PASS: matched set n=9595 positions=586 == Z1 intersection"
  "G2 PASS: zero-order rhos == Z1 matched CSV to <1e-12 (ESM -0.07714525927574277, Thermo -0.07329934766090093)"
  "G3 PASS: Z1 Thermo rho == AD7 task80 pooled mono rho to <1e-12 (-0.0732993476609009) — two independent runs agree"
  "G4 PASS: pred_eb rank-identical to ddg at all 9595 rows (Z1's predictor and this script's are the same rank variable)"
  "G5 PASS: 1-rho_ET^2 = 0.9922, R2_full 0.010407 >= max zero-order R2"
  "zero-orders: r(y,ESM) = -0.077145  r(y,Thermo) = -0.073299  r(ESM,Thermo) = +0.088281"
  "R2_E = 0.005951   R2_T = 0.005373   R2_full = 0.010407"
  pooled: "unique_T|ESM (semipartial ThermoMPNN) = 0.004455 [0.001407,0.009140] p=<1/N  part_r=-0.0667  = 82.9% of Thermo zero-order R2, 42.8% of R2_full"
  pooled: "unique_E|Thermo (semipartial ESM-2)     = 0.005034 [0.001544,0.010412] p=<1/N  part_r=-0.0710  = 84.6% of ESM zero-order R2, 48.4% of R2_full"
  pooled: "shared (commonality) = +0.000917 (8.8% of R2_full); unique_T+unique_E+shared == R2_full: True"
  region1: "unique_T = 0.014856 [0.004878,0.029683] p=<1/N ... 50.1% of R2_full" / "unique_E = 0.012159 [0.002630,0.028954] p=<1/N ... 41.0% of R2_full"
  region2: "unique_T = 0.004433 [0.000039,0.017850] p=<1/N ... 64.3% of R2_full" / "unique_E = 0.001536 [0.000004,0.009738] p=<1/N ... 22.3% of R2_full"
  region3: "unique_T = 0.004821 [0.000258,0.014900] p=<1/N ... 61.3% of R2_full" / "unique_E = 0.002011 [0.000010,0.010727] p=<1/N ... 25.6% of R2_full"
  region4: "r1=-0.0020 r2=-0.1237 r12=+0.0841 R2_full=0.015368" / "unique_T = 0.015364 [0.005384,0.030336] p=<1/N part_r=-0.1240 = 100.4% of Thermo zero-order R2, 100.0% of R2_full" / "unique_E = 0.000072 [0.000001,0.003597] p=<1/N part_r=+0.0085 = 1889.6% of ESM zero-order R2, 0.5% of R2_full" / "shared (commonality) = -0.000068 (-0.4% of R2_full)"
  "unique_T CI excludes 0: True | unique_E CI excludes 0: True"
  "VERDICT: BOTH carry independent information: both semipartial CIs exclude 0 (case i)."
  "Effect sizes with the claim (AGENTS sec 3): unique_T = 0.004455 (42.8% of R2_full 0.010407), unique_E = 0.005034 (48.4% of R2_full), shared = +0.000917 (8.8%); rho_ET = +0.0883 — full-model R2 explains 1.04% of own_e_b rank variance in total (n=9595, both signals small in absolute terms)."
  "AD8 DONE  (41.8s)  VERDICT: BOTH carry independent information: both semipartial CIs exclude 0 (case i)."

Verdict: PASS — the pre-registered case (i) fires: on the matched set BOTH predictors carry information independent of the other (unique_T 0.004455 [0.001407,0.009140], unique_E 0.005034 [0.001544,0.010412], both p<1/10000), decisively replacing "CIs overlap": the two signals are near-orthogonal (rho_ET only +0.0883, shared only 8.8% of R2_full) and each keeps ~83-85% of its own zero-order R2 after removing the other. Effect size in absolute terms reported plainly (AGENTS sec 3): the full model explains only 1.04% of own_e_b rank variance total — both signals are small in magnitude even though both are independently detectable at n=9,595. Secondary region rows: both semipartials' CIs exclude 0 in regions 1-3; region 4 is the standout (ESM's region-4 zero-order r1=-0.0020 is essentially nothing, Thermo's r2=-0.1237 carries 100.0% of R2_full, ESM's unique_E=0.000072 = 0.5% of R2_full) — consistent with the AD6 region-4 reversal and AD7's region-4 story, printed descriptively with no decision rule attached (pre-registered as secondary).

Files: NEW scripts/81_joint_semipartial.py; NEW data/processed/task81_joint_semipartial.csv (5 rows: pooled + regions 1-4 with all components + CIs). Read-only inputs: task_V2_thermompnn_ddg.csv, task_Z1_matched_n_headtohead.csv, task80_region_rhos.csv. No existing script, lib, or result modified. Next free script number: 82.

Unexpected: (1) region4 unique_E printed as "1889.6% of ESM zero-order R2" — a ratio artifact, not a bug: ESM's region-4 zero-order R2 is ~0.000038 (r1=-0.0020) and shared is slightly negative there (-0.000068, mild suppression), so unique_E (0.000072) exceeds R2_E; the commonality identity unique_T+unique_E+shared==R2_full held exactly in every scope (True x5) and the absolute magnitudes are quoted above rather than the ratio; (2) region4 shared < 0 (suppression) — reported as-is; (3) no gate failures or rule changes; smoke and full runs produced identical point estimates (deterministic observation) with CIs shifting only as N_BOOT implies.
---
## [AE1] — All 19 substitutions at 222 as backgrounds: A222V's context-shift is SMALLER than its same-position peers (identity at 222) — frozen rule fired the pre-registered MIXED-DIRECTION branch

Status: EXECUTED — PASS (script exit 0; frozen verdict = "MIXED DIRECTION: D_identity smaller, D_position larger — both CIs printed, read them as-is". AE1's half of the shared run below; [AE2] logs the same run's other block.)

Time: start 12:28:00 (after [AD8] 12:27:45), finish 17:30:38. Scoring accounting (measure-first): SMOKE=1 plumbing 9s; full-path smoke at N_SUB=8/N_BOOT=300 = 255.1s scoring + 0.9s stats rerun; FOREGROUND ATTEMPT 1 interrupted externally at background 38/57 after ~61 min (harness "Tool execution interrupted", not a script failure — in-memory rows lost, no cache written, log preserved as ae_full_attempt1_interrupted.log); FOREGROUND ATTEMPT 2 interrupted at bg 46/57 after ~60 min (checkpoint preserved 46/57); ATTEMPT 3 (checkpoint resume: 46 skipped + 11 scored = 754.4s; whole script 761.3s) completed exit 0 at 17:30.

What I did:
- Read task AE1 (doc L318-323): "Score all 19 possible substitutions AT position 222 as backgrounds (not just A->V), same delta_ESM construction as before for each. Does the outsized context-shift found for A222V specifically track being AT position 222 generally, or is it specific to Val?" Premise provenance disclosed: "the outsized context-shift found for A222V" is the evaluator's characterization (task L321; its source digest is external to this repo) — this script does not assume it: statistic defined, all three available cells measured, verdict possible even if the premise fails (frozen rule iv).
- Wrote scripts/82_ae_position_vs_identity.py with the pre-registered docstring BEFORE the first run: statistic = M1/script-63's construction exactly (delta_ESM_b(v) = S(v|b) - S(v|WT) merged on hgvs_pro; magnitude = mean |delta_ESM_b| over the common subset x 19 subs); cells = 19 backgrounds at 222 (AE1) + 38 A>V elsewhere (AE2); machinery reused via importlib (script 63's draw_subset/check_subset — same pool rule: 655 WT-table positions minus {222} U all 39 background positions = 616 pool, draw 120, seed 0, ONE subset common to all 57 backgrounds so the cells are comparable) + lib esm_scoring.get_position_logprobs / esm_scoring.hgvs_pro / sequence.load_sequence, model = ESM-2 t33 650M (same model/code path as scripts 10/11/12/63 lineage; zero third-party edits). One forward pass per (background, position). Frozen gates G1-G7, frozen timing rule (t1 = FIRST background; >5,400s projection -> one reduction; >7,200s -> stop), frozen statistics (paired position-cluster bootstrap, SAME resampled position indices across all backgrounds per draw; N_BOOT default 10,000, seed 0), frozen verdict rule (cases i-iv over {larger, indistinguishable}; any "smaller" classification -> pre-registered "report as-is, don't smooth" override).
- Disclosed D_identity = mean|d|(A222V) - mean(other 18 at 222) (position held fixed) and D_position = mean|d|(A222V) - mean(38 A>V elsewhere) (identity held fixed) — [AE1]'s primary contrast is D_identity.
- SMOKE=1 first (exit 0, 9s): G1-G3 + G5 cross-provenance max|diff| = 1.874e-15 over 152 rows. Full-path smoke (N_SUB=8, N_BOOT=300) then CAUGHT TWO CODE DEFECTS before any full burn, both fixed to match the frozen docstring (AGENTS s7) and disclosed: (1) f-string syntax errors in two gfail calls (compile-time, before any execution); (2) paired_boot computed the point estimate on raw per-position VECTORS while draws used scalars -> G7's `lo <= obs <= hi` raised ambiguous-truth ValueError; fix = reduce with mean over the full vectors (identical value under the balanced 19-sub design; no statistic, gate, or rule changed). After the fix, full-path smoke exited 0 end-to-end (cache-reuse path, G7, verdict blocks, CSVs, limitations). A THIRD defect was found by code review between attempts 1 and 2: score_all returned the LAST background's duration while the frozen docstring says the FIRST — the last-bg projection (5,443s) would have wrongly fired the reduction to n_sub=119; code fixed to return the first background's duration (AGENTS s7: fix code to match frozen docstring). A per-background checkpoint/resume (implementation-only: append after each background; resume validates count == 19*n_sub, position set == subset, no duplicate (position, mut_aa)) was added after attempt 1's external interruption, so interruptions cost <= 1 background instead of 60 minutes; disclosed in the run's own printed output; NO decision rule, gate, statistic, subset, or seed changed by it.
- Full run N_BOOT=10000, AE_N_SUB=120, exit 0 (attempt 3).

Actual output (verbatim, from /private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/ae_full.log, attempt-3 segment unless noted):
  attempt 1 evidence (preserved log): "timed: background 1/57 A222_C -> 77.6s for 120 positions (647 ms/pass); projection total = 4423.8s" ... last line before interruption "timed: background 38/57 AV_292 -> 95.5s ... projection total = 5442.5s"
  attempt 3 resume: "CHECKPOINT RESUME: 46/57 backgrounds already complete in task82_ae_raw_partial.csv" ; "scoring wall time: 754.4s total"
  "(G6) timing rule: projection 3593s <= 5400s -> NO reduction (n_sub stays 120)"  (t1 = first background scored in the resuming process, 63.0s; attempt 2's own in-run projections were 4,563-4,592s — both readings of the frozen rule land under 5,400, so no reduction under either; disclosed)
  "G1 PASS: WT table 12,445 rows / 655 positions"
  "G2 backgrounds PASS: AE1 = 19 rows at 222 (all wt A, 19 distinct muts); AE2 = 38 other-Ala A>V rows (39 Ala positions - 222); total 57 unique ids"
  "G2 FASTA PASS: len 656, [222]='A', wt letters match table at all 39 background positions"
  "G3 PASS: subset n=120 from pool 616 (655 - 39 excluded), disjoint from {222} U bg positions, seed 0"
  "G4 PASS: 129960 rows = 57 x 120 x 19, every hgvs resolves in WT table + merged file"
  "G5 cross-provenance: fresh A222V arm vs script 12's delta_esm on 2280 subset rows: max|diff| = 9.888e-17 (PASS, tol 1e-4)"
  AE1 table (all 19, mean|delta| desc): "A222_L A>L mean|delta| = 0.100977" ; "A222_F 0.099872" ; "A222_E 0.097354" ; "A222_D 0.095722" ; "A222_Y 0.095221" ; "A222_P 0.092378" ; "A222_R 0.091735" ; "A222_K 0.090068" ; "A222_W 0.087887" ; "A222_I 0.082201" ; "A222_N 0.080466" ; "A222_G 0.078678" ; "A222_Q 0.077084" ; "A222_T 0.071010" ; "A222_H 0.069196" ; "A222_V 0.068357" ; "A222_M 0.065496" ; "A222_C 0.059989" ; "A222_S 0.056420"
  "A222V rank among the 19 (1 = largest): 16 ; not the max ; median of the other 18 = 0.085044 ; A222V - median18 = -0.016687"
  "D_identity = mean|d|(A222V) - mean(other 18 at 222) = -0.014518 [-0.022077,-0.006934] p=0.0006 -> smaller (position held fixed, identity varied)"
  VERDICT block (shared with AE2): "D_identity: smaller | D_position: larger" ; "VERDICT: MIXED DIRECTION: D_identity smaller, D_position larger — at least one contrast points the other way; both CIs are printed above, read them as-is (report, don't smooth)." ; "Task question answered with effect sizes: A222V mean|delta| = 0.068357 (other-18 median 0.085044, A>V-elsewhere median 0.040635) — third cell (other-Ala, non-Val) unmeasured per task scope, so no full two-factor decomposition is claimed."
  "AE1+AE2 DONE  (761.3s)  VERDICT: MIXED DIRECTION: D_identity smaller, D_position larger — ..."

Verdict: PASS — AE1's frozen contrast D_identity = -0.014518 [-0.022077, -0.006934] p=0.0006 -> "smaller": at FIXED position 222, A222V's context-shift magnitude is significantly SMALLER than the other 18 substitutions at that position (rank 16/19; 0.068357 vs other-18 median 0.085044, a -0.0145 difference = -17% relative to that median). Plain reading of the task's question using this half: A222V's shift does NOT track being Val in the "elevated" sense — within position 222, Val sits on the LOW side of the sweep (the largest is A>L at 0.100977, 1.5x A222V). The frozen verdict word for the joint pattern stays MIXED DIRECTION (cases i-iv covered only {larger, indistinguishable} for both contrasts; the "smaller" override was pre-registered to report both CIs as-is, and that is what it did — no rule was re-read post-hoc). The paired D_position half is [AE2]'s entry. Effect-size context (AGENTS s3): D_identity's CI excludes 0 at n_boot=10,000, but the magnitude (-0.0145 model-logit units of mean |delta|) is reported against the 19-background spread 0.056-0.101, not as a headline on its own.

Files: NEW scripts/82_ae_position_vs_identity.py; NEW data/processed/task82_ae_raw.csv (scoring cache, 129,960 rows = 57x120x19), task82_ae_backgrounds.csv (57 rows), task82_ae_position_vectors.csv (6,840 rows = 57x120), task82_ae_contrasts.csv (3 rows: D_identity -0.01451800615600432 [-0.022076997914527594,-0.006934318360944861] p=0.0006 smaller; D_position 0.025600707800268914 [0.013701600902833486,0.03923618181911529] p=0.0 larger; group_mixed_identity 0.03935460836911512 [0.029309344532269663,0.050917639781082026] p=0.0 larger). Ephemeral logs in session tmp (ae_smoke.log, ae_smoke2.log [exit 1 = paired_boot defect], ae_smoke3.log [exit 0], ae_full_attempt1_interrupted.log, ae_full.log). Read-only inputs: data/processed/esm2_wt_scores.csv, merged_wt_a222v_scores.csv, data/raw/P42898.fasta; scripts 63 (helpers), lib esm_scoring/sequence (imported, unmodified); fair-esm portability patch pre-existing and untouched (zero third-party edits). No existing script, lib, or result modified. Next free script number: 83.

Unexpected: (1) TWO external interruptions of the foreground full run (~61 min at bg 38/57, ~60 min at bg 46/57; harness "Tool execution interrupted" both times, consistent ~60-minute pattern) — recovered via the disclosed checkpoint; total wall across attempts ~2h45m for this task, of which 3,593s+754s of scoring was usable and ~2h17m was lost to the interruptions; (2) three code defects found BEFORE the reported run and fixed to match the frozen docstring (compile-time f-strings; paired_boot G7 ambiguity caught by the full-path smoke — smoke's exit 1 is the evidence; t1 first-vs-last found by review between attempts) — all disclosed in this entry, none touched a decision rule; (3) smoke at n_sub=8 read A222V rank 19/19 with D_position indistinguishable; full run at n_sub=120 gives rank 16/19 and D_position larger — sampling-driven (subset size differs), rules unchanged, full-run numbers are the result; (4) the frozen cases i-iv did not anticipate (smaller, larger) firing together — the pre-registered "smaller" override handled it by instruction (report as-is), and the plain reading above is labeled interpretation of the two frozen CIs, not a new rule.
---
## [AE2] — A>V at the 38 other Ala positions vs the 222 sweep: A222V's context-shift is LARGER than the same substitution elsewhere — position-222 elevation holds at fixed identity

Status: EXECUTED — PASS (same single run as [AE1]; this entry logs the AE2 block of scripts/82. Frozen verdict = "MIXED DIRECTION: D_identity smaller, D_position larger — both CIs printed, read them as-is". AE2's half is D_position, which classifies "larger".)

Time: same run as [AE1] (start 12:28:00, finish 17:30:38; entry appended after [AE1]). D_position's bootstrap draws are part of the same 761.3s completion.

What I did:
- Read task AE2 (doc L324-329): "Identify positions elsewhere in MTHFR where the wild-type residue is also Ala, and score A->V substitutions at THOSE positions as backgrounds, same construction. Compare context-shift magnitude against AE1's position-222 sweep. Together AE1+AE2 form the two clean 2x2 cells the evaluator specifies: position x identity."
- Same script 82, same run, same ONE common subset (120 of the 616-position pool, seed 0 — the pooling excludes all 39 background positions so AE1's and AE2's backgrounds score the identical 120x19 targets, making the cells directly comparable), same gates G1-G7, same paired position-cluster bootstrap machinery (N_BOOT=10000, seed 0, same resampled position indices across every background so the A222V-vs-group pairing survives), same cache. Disclosed: AE1 and AE2 share one execution (one script, one run, two verdict blocks) by design — splitting them would have drawn two different random subsets from two different pools and broken comparability; each log entry quotes only its own task's executed block.
- AE2's 38 backgrounds: WT-table rows wt_aa=='A', position!=222, mut_aa=='V' — 39 Ala positions total in the 655-position table, 38 excluding 222 (count measured before writing the script). Pre-registered contrasts: D_position = mean|d|(A222V) - mean over the 38 (identity held fixed at A>V, position varied) = AE2's primary; plus a group contrast mean(19 at 222) - mean(38 A>V elsewhere) LABELED descriptive/identity-confounded (18 non-Val + V vs all-Val) in the docstring before running.
- No post-hoc additions: the third cell (other-Ala, non-Val) was NOT measured because the task requests only A>V there — limitation printed by the script.

Actual output (verbatim, same log file, attempt-3 segment):
  "AE2 — A>V at other Ala positions vs the 222 sweep"
  "AE2 group (38 A>V elsewhere): mean|delta| min 0.013830, median 0.040635, max 0.097851; A222V = 0.068357 exceeds 36/38"
  "D_position = mean|d|(A222V) - mean(38 A>V elsewhere) = +0.025601 [+0.013702,+0.039236] p=<1/N -> larger (identity held fixed at A>V, position varied)"
  "DESCRIPTIVE (identity-confounded: 18 non-Val+V vs 38 V): mean(19 at 222) - mean(38 A>V elsewhere) = +0.039355 [+0.029309,+0.050918] p=<1/N"
  VERDICT block (quoted in [AE1]): "D_identity: smaller | D_position: larger" ; "VERDICT: MIXED DIRECTION: D_identity smaller, D_position larger — at least one contrast points the other way; both CIs are printed above, read them as-is (report, don't smooth)."
  "saved 57 background rows -> task82_ae_backgrounds.csv; 6840 position-vector rows -> task82_ae_position_vectors.csv; 3 contrast rows -> task82_ae_contrasts.csv"
  LIMITATIONS items 1-6 printed (cell 4 unmeasured; one-directional S(v|b); no measurability filter; subset 120/616; magnitude-only statistic; G5 cross-provenance 9.888e-17)
  "AE1+AE2 DONE  (761.3s)  VERDICT: MIXED DIRECTION: D_identity smaller, D_position larger — ..."

Verdict: PASS — AE2's frozen contrast D_position = +0.025601 [+0.013702, +0.039236] p<1/10000 -> "larger": at FIXED identity A>V, A222V's context-shift magnitude significantly EXCEEDS the same substitution at other Ala positions (A222V exceeds 36 of the 38; 0.068357 vs group median 0.040635 — about 1.68x the median, +0.0277 in absolute mean|delta|). Together with [AE1]'s "smaller", the plain reading of the task's position-vs-identity question from the two frozen CIs: the ELEVATION of A222V's context-shift relative to the matched A>V control tracks BEING AT POSITION 222 (position effect present, +0.0256, CI clear of 0), while being Val specifically does NOT elevate within 222 — it attenuates relative to the other 18 residues there (identity effect at 222 points the other way, -0.0145). The descriptive group contrast (+0.0394 [+0.0293, +0.0509]) says the whole 19-background 222 sweep sits above the A>V-elsewhere group, but it is identity-confounded by construction and was pre-labeled descriptive; it is not part of the verdict. The frozen verdict WORD for the joint pattern remains MIXED DIRECTION (read as-is) — the sentence above is labeled interpretation of the two frozen contrast CIs, not a re-firing of the rule. Effect sizes with significance throughout (AGENTS s3): n = 38 backgrounds x 120 positions x 19 subs each; magnitude of D_position is ~64% of the AE2-group median, i.e. nontrivial relative to the group spread (0.0138-0.0979), not merely nonzero at large n.

Files: no NEW files beyond [AE1]'s list (same run, same outputs): scripts/82_ae_position_vs_identity.py; task82_ae_raw.csv (129,960), task82_ae_backgrounds.csv (57), task82_ae_position_vectors.csv (6,840), task82_ae_contrasts.csv (row 2: D_position 0.025600707800268914 [0.013701600902833486,0.03923618181911529] p=0.0 larger; row 3: group_mixed_identity 0.03935460836911512 [0.029309344532269663,0.050917639781082026] p=0.0 larger). No existing script, lib, or result modified. Next free script number: 83 (unchanged from [AE1]).

Unexpected: (1) shared-run design disclosed up front in both entries (the evaluator's "two clean 2x2 cells" are only clean on a common subset — one run guarantees it); (2) smoke (n_sub=8) had shown D_position indistinguishable (p=0.5867, CI [-0.0098, +0.1081]) — the full run's CI tightens to [+0.0137, +0.0392] with the point estimate nearly unchanged (+0.0321 -> +0.0256), i.e. the smoke was underpowered on 8 positions, not contradictory; the pre-registered rule was applied only to the full run's numbers; (3) the AE2-group max (0.097851) exceeds A222V (0.068357) at two positions — hence "exceeds 36/38", reported as-is rather than "the max"; (4) no gate failures, no rule changes, no retries of any statistic.
---
## [AE3] — The phylogenetic/clade test: Val at the aligned col for 222 is RARE (2.17% of homologs), but V-vs-A clade divergence tracks |delta_ESM| and SURVIVES AD6's depth control — frozen rule fired "CONSISTENT", offered strictly as a candidate explanation

Status: EXECUTED — PASS (scripts/83 exit 0; frozen rule fired the CONSISTENT branch with the depth-control-survives qualification. AE3a and AE3b share this one run.)

Time: start 17:33:00 (after [AE2] 17:32:00), finish 17:59:07. Runtime: smoke path1 (G2 gate FAIL, exit 1) ~1 min; smoke path 2 (bytes-encode ValueError, exit 1) seconds; smoke path 3 (JSD-scale run, exit 0 but levels wrong — rejected by inspection) seconds; smoke 4 / final-scale check at N_BOOT=300 (exit 0) 0.4s; REPORTED FULL RUN N_BOOT=10000 exit 0 in 5.1s (stats-only script: no model, no fetch).

What I did:
- Read task AE3 (doc L331-345): AE3a = fraction of MTHFR homologs carrying Val at the position aligned to human 222, "reuse Group AB's fetch if suitable, or fetch one directly within the same budget convention"; AE3b = "If V222 is common in some clades: test whether the positions where delta_ESM is largest show clade-specific residue preferences that co-vary with residue 222's identity... if it holds, note explicitly that it would also offer a candidate explanation for the wrong-sign result AND the region-4 failure, per the evaluator's own reasoning, but do not over-claim a single unifying story without the region-4/AD6 alignment-depth result also being checked for consistency with it."
- ALIGNMENT REUSE (budget): Group AB's fetch data/external/ProteinGym/MTHR_HUMAN_2023-08-07_b02.a2m (3,316,659 B, on disk since [AB1], parsed read-only by script 79/AD6) is suitable — reused. 0 new bytes fetched (data-member cap stays ~196.3/200 MB); the task's fetch alternative deliberately not taken, disclosed here rather than silently skipped.
- Wrote scripts/83_ae3_clade_test.py with the pre-registered docstring before any run: AE3a primary = V-count / all 4,782 non-query homologs at 222's match column (gap/other letters do NOT carry Val), gap-excluded companion denominator, Wilson 95% CI LABELED DESCRIPTIVE ONLY (MSA sequences non-independent). AE3b CONDITION (frozen power floor stated before any number): both residue groups >= 50 sequences -> run; else NOT RUN, reported plainly, no alternative grouping invented. "Clade" operationalized as grouping homologs BY their residue at 222's match column (the proposed subfamily) — NO phylogeny/tree built, disclosed in the script output. "Positions where delta_ESM is largest" = per-position mean |delta_esm| over task32_analysis_table.csv's full 11,344-row/654-position finite-delta frame (MEAN chosen over max as robust, alternatives not used). Eligible position = has a query match column (query-lowercase insert positions excluded, accounted) AND >= 30 canonical-AA residues per group at that column; eligible < 50 -> UNDETERMINED, no test claimed. Divergence = JSD (base 2, [0,1]) between V-group and A-group 20-AA distributions per position (gaps/non-canonical excluded with counts accounted, renormalized over 20). PRIMARY = Spearman(JSD_p, mean|delta|_p) over eligible positions, position-cluster bootstrap, N_BOOT env default 10,000, seed 0. CONTRAST = dJSD between quartiles of mean|delta| computed once on observed eligible positions (edges frozen, membership fixed), seed 2. MANDATORY depth check (task L343-345): Neff-adjusted rank-partial (rank JSD and rank mean|delta| on rank Neff, Pearson on residuals, ranking re-done inside every draw) using AD6's OWN per-position depth output (data/processed/task79_depth_positions.csv, 586 rows), PLUS raw Spearman on the SAME joined rows (like-for-like); join < 100 -> adjusted UNAVAILABLE and the verdict must then make no unifying claim. FROZEN VERDICT RULE: "consistent with the clade mechanism" IFF (a) primary rho CI excludes 0 positive AND (b) dJSD CI excludes 0 positive; then branch on the depth check: adjusted CI positive -> may note, per the task's own wording, the CANDIDATE explanation for the wrong-sign result AND the region-4 failure, explicitly qualified (observational not causal; AD6's region-4 depth reversal remains a limit on any single story); adjusted CI includes 0 -> MUST say the association does not survive AD6's depth control and the unifying story must not be over-claimed; adjusted unavailable -> no-claim line. Else "NOT SUPPORTED: <condition> — null reported plainly". Effect sizes printed with significance throughout.
- Gates G1-G7 pre-registered. THE GATES AND SMOKE CAUGHT FOUR CODE DEFECTS BEFORE THE REPORTED RUN, all fixed to match the frozen docstring (AGENTS s7), none touching a decision rule, statistic, seed, or threshold: (1) smoke path 1 G2 FAIL — the gate iterated the VARIANT-level WT table (12,445 rows, positions repeat: "first 5: [(2, 'V', 'v'), (2, 'V', 'v'), ...]") and compared case-sensitively against the a2m query, whose lowercase encodes match/insert state; fixed to: one letter per UNIQUE position (655, with an internal consistency check on wt_aa within position) compared case-insensitively, per the docstring's residue-identity intent; NO statistic had run when this fired. (2) smoke path 2 ValueError — np.array([...encode()], dtype=uint8) parses each bytes object as an integer sequence; fixed to np.frombuffer of the joined string reshaped to (4782, 630). (3) smoke path 3 JSD OUT OF RANGE — printed means 1.299921/1.230556 on a docstring-stated [0,1] scale exposed log2(2*p/m) (exact +1 level shift; correct term log2(p/m) == log2(2p/(p+q))); fixed and a range self-check added to jsd(); IMPORTANT: the shift is exactly position-constant, so rho, quartile membership (edges are on mean|delta|), dJSD and the verdict logic were numerically invariant (post-fix values agree to <=1e-5: rho 0.107771 -> 0.107780 from float tie-ordering only) — but reported LEVELS would have been wrong, so smoke path 3's exit-0 output was rejected by inspection of the printed means against the frozen scale and is NOT the reported run; smoke 4 re-ran clean on the corrected scale. (4) smoke path 1's G2 FAIL log file was overwritten by smoke path 2 (same tee path — minor log-management slip, disclosed); the two FAIL lines are quoted from the session transcript, and the fixed gate with its explanatory comment lives in scripts/83. The reported run made no further change.

Actual output (verbatim; full run from session tmp ae3_full.log unless noted):
  smoke path 1 (rejected, gate caught the defect): "G2 FAIL: query letter != WT-table letter at 475 positions; first 5: [(2, 'V', 'v'), (2, 'V', 'v'), (2, 'V', 'v'), (2, 'V', 'v'), (2, 'V', 'v')]"
  smoke path 2 (rejected): "ValueError: invalid literal for int() with base 10: b'----------------------------KVIDKINKAIKENQPCWSFEFF...'"
  smoke path 3 (rejected by inspection): "CONTRAST mean JSD top quartile 1.299921 - bottom 1.230556"  (>1 on a [0,1] scale)
  full run: "G1 PASS: 4,783 records, query raw len 656, match state 630 cols, 0 non-conforming (<=1% rule, s79 constants agree)"
  "G2 PASS: query letters (case-insensitive; a2m case = match/insert state) == esm2_wt_scores wt_aa at all 655 unique positions of 12,445 variant rows; 26 query residues in insert state (no match col, accounted); query[221]='A' -> match col 206"
  AE3a: "alignment: AB1's MTHR_HUMAN a2m reused read-only (0 new bytes fetched); 4782 homologs (query excluded)"
  "aligned col for human 222 = match col 206 (query[221]='A' in match state)"
  "counts: V 104 | A 4244 | gap 6 | other-uppercase 428  (sum 4782 == 4782)"
  "PRIMARY: fraction carrying Val = 0.021748 (104/4782)  Wilson95% [0.017982,0.026282] DESCRIPTIVE ONLY (MSA sequences non-independent — clade redundancy; this is a sequence-count fraction)"
  "companion (gap-excluded denominator): 0.021776 (104/4776)"
  "AE3b CONDITION (frozen floor: both groups >= 50): V-group 104 >= 50, A-group 4244 >= 50 -> RUN (grouping-by-222 IS the operationalized 'clade'; no tree built)"
  "G4 PASS: delta frame 11,344 rows / 654 positions / 0 delta NaN"
  "accounting: 654 delta positions -> 25 at query-insert columns (no match col, excluded) -> 49 below the 30/group coverage floor -> 580 eligible (test claimed)"
  "G5 PASS: AD6's depth table 586 rows with neff"
  "depth join: 563 eligible positions carry neff (raw-on-joined rho +0.109228 [+0.025621,+0.193741] p=0.0128; adjusted +0.123565 [+0.039702,+0.206380] p=0.0038)"
  "group sizes: V 104 / A 4244 at col 206; eligible positions 580; quartile edges [0.032608,0.089864] (observed, membership fixed)"
  "PRIMARY rho(JSD, mean|delta|) = +0.107780 [+0.024259,+0.191756] p=0.0120"
  "CONTRAST mean JSD top quartile 0.299921 - bottom 0.230556 = dJSD +0.069365 [+0.017512,+0.121302] p=0.0066"
  "effect sizes: rho magnitude 0.107780, dJSD 0.069365 JSD units on a [0,1] scale (top 0.299921 vs bottom 0.230556)"
  "(a) primary rho CI excludes 0 on + side: True | (b) dJSD CI excludes 0 on + side: True | depth check: available"
  "VERDICT: CONSISTENT with the evaluator's clade mechanism (both frozen conditions met) AND the association survives AD6's depth control (adjusted CI excludes 0). Per the task's own wording this would offer a CANDIDATE explanation for the wrong-sign result AND the region-4 failure — offered explicitly as a candidate, observational not causal; AD6's own region-4 depth reversal ([AD6], log L2614) remains a limit on any single unifying story."
  "saved positions CSV (654 rows) -> task83_ae3b_positions.csv" ; "saved results CSV (7 rows) -> task83_ae3b_results.csv" ; "AE3 DONE  (5.1s)"
  LIMITATIONS 1-6 printed (non-independent MSA fractions; clade = operationalization, no tree; gap/non-canonical exclusion with accounting; 25/654 insert-column positions excluded; delta frame 11,344/654 with fixed quartile edges; Neff join subset + like-for-like raw-on-joined).

Verdict: PASS — both sub-tasks executed; frozen rule fired CONSISTENT with the depth-control-survives qualification, and that is reported as-is with effect sizes and hard limits:
- AE3a: Val at the aligned column for human 222 is RARE, not common: 0.021748 (104/4,782 homologs), Wilson95% [0.017982, 0.026282] descriptive; the column is 88.7% Ala (4,244 A, 6 gaps, 428 other residues). Plain-reading honesty: the evaluator's antecedent "V222 is common in some clades" is NOT supported at the whole-MSA level — what is supported is that 104 sequences carry V, above the frozen 50-sequence floor, which is a POWER floor, not a prevalence claim; AE3b ran because the registered condition was met, not because V is common. The verdict word "CONSISTENT" applies to the AE3b association pattern only.
- AE3b: positions with higher V-vs-A residue-distribution divergence carry higher mean |delta_ESM| — primary rho = +0.107780 [+0.024259, +0.191756], p=0.0120 (small: rho^2 ~1.2% of rank variance, stated not buried), and the registered contrast dJSD = +0.069365 [+0.017512, +0.121302], p=0.0066 (top quartile 0.299921 vs bottom 0.230556, ~30% higher divergence on the [0,1] scale). Both frozen conditions met.
- REQUIRED depth check (task L343-345): the association SURVIVES AD6's Neff control — adjusted +0.123565 [+0.039702, +0.206380] p=0.0038 on the 563-position join, slightly STRONGER than raw-on-joined +0.109228 [+0.025621, +0.193741] p=0.0128 (a suppression, disclosed: alignment depth does not explain this association away; if anything it masks part of it). Per the task's own instruction the wrong-sign/region-4 explanation is therefore noted but ONLY as a candidate — observational, not causal — with AD6's own region-4 depth reversal ([AD6] L2614) quoted as a standing limit on any single unifying story, and grouping-by-222 is an operationalization, not a phylogeny (no tree was built; a genuine subfamily claim would need one). A region-stratified AE3b variant was NOT part of the pre-registered rule and was not run (post-hoc test discipline, AGENTS s0/s6): the task's "checked for consistency" requirement is satisfied by the Neff-adjusted control built from AD6's own per-position depth output plus the explicit region-4 caveat in the printed verdict.

Files: NEW scripts/83_ae3_clade_test.py (pre-registered docstring; G1-G7; frozen floors/verdict rule; two defect-fix comments); NEW data/processed/task83_ae3a_222_column.csv (1 row: 4783/4782/col206/104/4244/6/428/0.021748222501045588/[0.017981811012450326,0.02628242038208642]/0.021775544388609715/True), task83_ae3b_positions.csv (654 rows with match_col, mean_abs_delta_esm, coverage, JSD, eligibility), task83_ae3b_results.csv (7 rows: AE3a_frac_V 0.021748222501045588; primary_rho 0.1077795872908862 [0.02425933457518202,0.191755912435612] p=0.012; quartile_dJSD 0.06936537753688124 [0.017512485872673834,0.12130204708942367] p=0.0066; meanJSD_top 0.2999211300502925; meanJSD_bottom 0.23055575251341123; raw_rho_on_neff_joined 0.1092277298522685 [0.02562111518287915,0.19374140302383502] p=0.0128; neff_adjusted 0.12356489039260235 [0.039702178302981894,0.20638009454763187] p=0.0038). Ephemeral session-tmp logs: ae3_smoke.log (now holds smoke path 2 — path 1's output overwritten, disclosed above), ae3_smoke2.log (smoke path 3, rejected), ae3_full.log (REPORTED RUN). Read-only inputs: data/external/ProteinGym/MTHR_HUMAN_2023-08-07_b02.a2m (AB1's, 0 bytes fetched now), data/processed/esm2_wt_scores.csv, task32_analysis_table.csv, task79_depth_positions.csv (AD6's); scripts/79 parse_a2m imported via importlib (unmodified). No existing script, lib, or result modified; zero third-party edits; next free script number 84.

Unexpected: (1) G2's first-run failure exposed TWO gate-implementation bugs (variant-level table treated as position-level; case-sensitive compare vs a2m lowercase) — caught before any statistic ran, fixed to docstring intent, disclosed; (2) the bytes-encode ValueError on the homolog matrix — caught by smoke, fixed; (3) the JSD +1 level bug was NOT caught by any gate (exit-0 run) but by manual inspection of printed means against the frozen [0,1] scale — rejected that run, fixed, added a range self-check, and verified the shift-invariance claim numerically (rho/dJSD changed <=1e-5 post-fix) so no reported statistic or the verdict could have differed; this is a case where the printed output itself, not a gate, caught the defect — the self-check now makes it a gate; (4) smoke path 1's log file was overwritten by path 2 (same tee path) — slip disclosed, transcript quote stands; (5) the headline V fraction (2.17%) runs against the evaluator's "if V222 is common" phrasing — reported plainly above rather than smoothed into the CONSISTENT verdict; (6) four code defects total were fixed before the reported run, none changing a pre-registered rule, seed, floor, or threshold.
---
## [AE4] — Shift magnitude vs shift accuracy: within-bin delta_ESM-own_e_b correlation WORSENS across |delta_ESM| quartiles and the top quartile is significantly anti-aligned — frozen rule permits and uses the "most confidently wrong where it moves most" framing, at modest effect size

Status: EXECUTED — PASS (scripts/84 exit 0; frozen rule fired WORSENS + framing-permitted branch: Delta_signed CI strictly < 0 AND Q4's signed-rho CI strictly < 0).

Time: start 18:01:00 (after [AE3] 18:00:14), finish 18:07:29. Runtime: anchor pre-check (standalone pandas, before script writing) ~5s; smoke N_BOOT=300 1.0s (exit 0 first try); REPORTED FULL RUN N_BOOT=10000 exit 0 in 32.0s (smoke-projected ~35s — projection accurate, measured-first per AGENTS s1).

What I did:
- Read task AE4 (doc L347-355): "Bin variants by |delta_ESM| (quartiles or deciles, pre-register the choice) and compute the delta_ESM-vs-e.b correlation within each bin. Report whether accuracy improves, stays flat, or worsens as shift magnitude increases. State the result plainly, including if it supports the 'most confidently wrong where it moves most' framing — this is a strong, memorable claim ONLY if the data actually shows it; do not reach for that framing if the bins are flat or noisy."
- Wrote scripts/84_ae4_shift_magnitude_vs_accuracy.py with the pre-registered docstring: FRAME = task32_analysis_table.csv dropna(own_e_b) -> 10,757/654 (delta_esm has 0 NaN; 587 rows lack own_e_b); e.b := own_e_b — the project's registered primary (script 32's primary row "signed, own e_b"; AA4's detection floor; anchors in scripts 47/49/65/71/73/74); published-e.b companion (anchor -0.07070516222228716) NOT re-binned (disclosed limitation, not silent). BINS = QUARTILES of |delta_ESM| (choice over deciles registered: ~2,689/bin for within-bin stability; deciles not run); edges computed once on observed frame, fixed membership (searchsorted side="right"). PER BIN primary = Spearman rho(delta_esm, own_e_b) on signed values (same statistic family as the -0.088118 anchor); secondary = rho(|delta_esm|, |own_e_b|) reported as-is with NO decision rule. ACCURACY DIRECTION registered before running: positive correlation = model shift aligned with measured burden = more accurate; improve = rho rises with magnitude, worsen = rho falls. BOOTSTRAP = position-cluster, the 654 positions are the unit, resampled with replacement, each draw brings all variants of its sampled positions, PAIRED (one draw feeds all four bins and both contrasts), N_BOOT env default 10,000, seed 0, ranking recomputed per draw (re-derivation). PRIMARY CONTRAST Delta_signed = rho(Q4) - rho(Q1) decides improve/flat/worsen (two-sided 95% percentile CI + p). FROZEN DECISION RULE (the task's own wording operationalized): CI strictly > 0 -> IMPROVES; strictly < 0 -> WORSENS, and ONLY in that branch the framing check: Q4 signed-rho CI strictly < 0 -> "most confidently wrong where it moves most" PERMITTED (used), Q4 CI includes 0 -> trend reported, framing NOT used; CI includes 0 -> FLAT, framing NOT used (the task's explicit instruction for flat/noisy bins). Gates G1-G5 (frame identity; anchor within 1e-9; bin partition + >=1,000/bin; per-statistic NaN/obs-inside-CI checks — no raising N; CSV row counts).
- DISCLOSURE (in the script's own docstring and printed output, AGENTS s6): the G2 anchor pre-check run BEFORE writing the script also printed the four within-bin point estimates as a side effect (no CIs, no bootstrap). The design above (quartiles, paired position bootstrap, CI-gated framing) had already been drafted in the plan before that peek; the decision rule is the task's own wording made operational, written to test the claim symmetrically, not to produce a direction. The peek is stated in the script itself.
- AGENTS s5 duties built in: exclusion skew check on the 587 dropped rows (mean|delta| and region shares printed) and three labeled-example rows printed to verify sign conventions against real values rather than assumption.

Actual output (verbatim; full run from session tmp ae4_full.log):
  "G1 PASS: table 11,344/654, delta NaN 0; 587 rows missing own_e_b -> frame 10,757 rows / 654 positions / 0 NaN (every position survives the drop)"
  "EXCLUSION SKEW CHECK: excluded 587 rows mean|delta| 0.073051 vs included 0.070330 (ratio 1.039); region shares excluded {1.0: 0.128, 2.0: 0.221, 3.0: 0.375, 4.0: 0.276} included {1.0: 0.24, 2.0: 0.225, 3.0: 0.252, 4.0: 0.283}"
  "G2 PASS: overall Spearman(delta_esm, own_e_b) = -0.08811806424891734 == script-32 anchor within 1e-9"
  "labeled max delta_esm: p.Val194Gly delta_esm=+3.105829 own_e_b=+0.092567 region=2"
  "labeled min delta_esm: p.Lys217Asp delta_esm=-0.715206 own_e_b=-0.006602 region=2"
  "labeled max own_e_b: p.Ala145Thr delta_esm=+0.057942 own_e_b=+1.373522 region=1"
  "G3 PASS: quartile edges [0.018901,0.046466,0.088855] -> bin sizes [2689, 2689, 2689, 2690] (sum 10,757)"
  "frame 10,757 variants / 654 positions; overall rho = -0.088118 (anchor)"
  "Q1 |delta| in [0.000000, 0.0189): n=2689 pos=498 rho_signed=-0.010273 [-0.049187,+0.029793] p=0.6092 | rho_abs=-0.059142 [-0.097180,-0.019721] p=0.0032"
  "Q2 |delta| in [0.018901, 0.04647): n=2689 pos=546 rho_signed=-0.010709 [-0.055043,+0.032182] p=0.6074 | rho_abs=-0.000369 [-0.039597,+0.037584] p=0.9914"
  "Q3 |delta| in [0.046466, 0.08886): n=2689 pos=556 rho_signed=-0.054483 [-0.101586,-0.005934] p=0.0300 | rho_abs=+0.009559 [-0.029756,+0.047399] p=0.6258"
  "Q4 |delta| in [0.088855, inf): n=2690 pos=416 rho_signed=-0.110803 [-0.167445,-0.053712] p=0.0002 | rho_abs=-0.102766 [-0.153740,-0.049353] p=0.0002"
  "Delta_signed = rho(Q4) - rho(Q1) = -0.100530 [-0.170813,-0.032004] p=0.0046"
  "Delta_abs (secondary, |.| vs |.|) = -0.043624 [-0.107221,+0.020251] p=0.1776"
  "effect sizes: per-bin signed rho ['-0.0103', '-0.0107', '-0.0545', '-0.1108']; |.| rho ['-0.0591', '-0.0004', '+0.0096', '-0.1028']; Delta magnitude 0.100530 correlation units"
  "(a) Delta_signed CI < 0: True | (b) Q4 signed rho CI < 0: True | CI includes 0: False"
  "VERDICT: WORSENS with shift magnitude (Delta_signed CI strictly below 0) AND the top quartile is significantly anti-aligned (Q4 signed rho CI strictly below 0) — the data DOES support the 'most confidently wrong where it moves most' framing; used here as the task permits, with the effect sizes above (rho Q1 to Q4: -0.010273 -> -0.110803; Delta -0.100530 [-0.170813,-0.032004])."
  "saved 4 rows -> task84_ae4_bins.csv; 3 rows -> task84_ae4_results.csv" ; "AE4 DONE  (32.0s)"
  LIMITATIONS 1-8 printed (own_e_b only; quartiles not deciles; Q4 signed delta two-tailed by construction; fixed bin membership; per-bin position composition differs; correlation is association not calibration; the point-estimate peek; the 587-row exclusion skew check above).

Verdict: PASS — accuracy WORSENS with shift magnitude, and the task's own gate for the memorable framing is met by the registered conditions; both stated with effect sizes and bounded honestly:
- The trend: within-bin signed rho is flat near zero in the bottom half (Q1 -0.010273, Q2 -0.010709, both CIs straddling 0, p~0.61), turns negative in Q3 (-0.054483 [-0.101586,-0.005934], p=0.0300) and is most negative in Q4 (-0.110803 [-0.167445,-0.053712], p=0.0002). Primary contrast Delta_signed = -0.100530 [-0.170813, -0.032004], p=0.0046 (position-cluster bootstrap, 10,000 draws) -> WORSENS, CI strictly below 0.
- Framing: both frozen conditions hold (Delta < 0 CI, Q4 rho < 0 CI), so "most confidently wrong where it moves most" IS used, as the task permits — but with the honest effect-size frame: the top-quartile anti-alignment is rho = -0.11 (about 1.2% of rank variance) on an overall rho of -0.088; every within-bin |rho| stays <= 0.167, so "confidently wrong" here means consistently, significantly ANTI-aligned where the model moves most, not wildly so. The graded pattern (0, 0, -0.054, -0.111) is monotone in the top half rather than a single-bin artifact.
- Secondary |.|-vs-|. | contrast is FLAT (Delta_abs -0.043624 [-0.107221, +0.020251], p=0.1776) and is reported without a rule: what worsens with magnitude is the SIGNED alignment (direction of the shift vs direction of the burden), not the magnitude-magnitude association (both extreme bins are negative on |.|: Q1 -0.0591 p=0.0032, Q4 -0.1028 p=0.0002, middle bins ~0 — a U-shape, no trend). Plain statement of the task's question: accuracy declines as shift magnitude grows; the "moves most" quartile is where the model is most systematically pointed the wrong way.
- AGENTS s5 note: the 587 excluded (missing own_e_b) rows are NOT shift-skewed (mean|delta| ratio 1.039) but ARE region-skewed (excluded region-3 share 37.5% vs 25.2% included; region-1 12.8% vs 24.0%) — the frame's region composition therefore reflects measured variants only; disclosed, no reweighting attempted (would be a post-hoc change).

Files: NEW scripts/84_ae4_shift_magnitude_vs_accuracy.py (pre-registered docstring with the peek disclosure; G1-G5; frozen rule); NEW data/processed/task84_ae4_bins.csv (4 rows: Q1-Q4 with n_var/n_pos/edges/rho_signed[CI,p]/rho_abs[CI,p]), task84_ae4_results.csv (3 rows: overall_rho_anchor -0.08811806424891734; Delta_signed_Q4_minus_Q1 -0.10053006930576763 [-0.1708131389574773,-0.03200391939506725] p=0.0046; Delta_abs_Q4_minus_Q1 -0.04362389414946611 [-0.10722072209565554,0.020251259831809375] p=0.1776). Ephemeral session-tmp logs: ae4_smoke.log (N_BOOT=300, exit 0), ae4_full.log (REPORTED RUN). Input read-only: data/processed/task32_analysis_table.csv. No existing script, lib, or result modified; next free script number 85.

Unexpected: (1) the anchor pre-check printed the four point estimates before the docstring was written — disclosed in the script's own docstring, output, and here (no CI was seen; the design predated the peek; the rule is the task's wording operationalized); (2) region-skewed exclusions found by the s5 skew check (numbers above) — reported, not corrected; (3) the secondary |.| contrast did NOT worsen (flat, p=0.1776) while the signed one did — both reported as-is, the divergence explained in the Verdict rather than smoothed; (4) smoke passed first try (no defects found by it — the earlier scripts' gate/build catches were not repeated here); (5) Q4 covers only 416 of 654 positions (largest shifts cluster at fewer residues) — printed per bin, handled by the position-level design, disclosed as limitation 5.
---
## [AF2] — One canonical variant manifest: all three missense totals and all four analysis n's reconcile into a single gated 11-stage cascade — every n recomputed from disk (40 gates), one gate caught its own wrong-base bug before any file was written

Status: EXECUTED — PASS (scripts/85 exit 0 on the reported run; all 40 gates G1-G8 PASS; data/processed/task_AF2_variant_manifest.csv written with 11 rows; first run exited 1 at G7 with NOTHING written, see Unexpected).

Time: start 18:09:00 (after [AE4] 18:08:15), finish 18:22:41. Runtime: evidence gathering (greps/reads across A2b, V2 stage-3, Z1, Z3f records) ~10 min; script written ~3 min; run 1 (G7 FAIL, exit 1, no write) ~4s; reported run exit 0 in ~4s (CSV reads only — no model, no fetch, no bootstrap).

What I did:
- Read task AF2 (doc L368-377): reconcile 11,902 (original proposal) / 11,344 (Part II §12) / 11,113 (Part I §6.2) and the four analysis n's 10,757 / 10,141 / 9,740 / 9,595 into ONE exclusion cascade: starting count, each filtering step (by which script), resulting n per stage, per predictor; save as data/processed/task_AF2_variant_manifest.csv (filename fixed by the task — deviates from the taskNN_ prefix deliberately).
- Located every number's source of truth before writing anything: A2b's logged reconciliation (OVERNIGHT_LOG L138-161; comparators SESSION_LOG L497-522; digest L17: "13,134 → 11,902 → 11,901 → 11,344 → 11,113 → 10,757, each step attributable"); V2's STAGE-3 join breakdown verbatim (SESSION_LOG L2340: "breakdown of 1203 dropped rows: 1046 rows at 59 unresolved positions ...; 157 rows at 9 positions where 6FCX chain A's residue differs from canonical P42898 ([429, 594, 645, 646, 647, 648, 649, 650, 651])"); Z3f's accounting (CLOSEOUT_LOG L615-617: 10,757 → excluded 1,017 at the 59 unresolved positions → "ours 9740"; 29 of phase5's 1,046 outside the 10,757 set); Z1/AD8's intersection ([Z1a] L2869 "intersection n=9595 pos=586 (ESM loses 1162, Thermo loses 0)"; AD8 L2876 "V2 10141 -> own_e_b finite 9595 -> +delta_esm finite 9595"). Externality: Part II is NOT in this repo ([AD7] L2824 established this for §12.4), so the proposal/Part I/Part II attributions are the task doc's own (L370-371) anchored to in-repo carriers (script-50's gate MIGRATION_LOG L441; MTHFR_RESULTS_LOG §6.2 L230; RESULTS.md L56's 11344) — stated in the script's limitations, not silently claimed.
- Wrote scripts/85_af2_variant_manifest.py with the pre-registered docstring: NO statistics, NO decisions, NO post-hoc choices possible — it VERIFES pre-existing numbers against their on-disk files and refuses to write on any mismatch (AGENTS s7/s5). Gates G1-G8 (40 checks): universe counts from task35_epistatic_set.csv (13,134 / 11,902 / 624 / 608); phase3 11,901 and phase5 11,344 with phase5 ⊂ phase3 by hgvs_pro (the −557 is a drop, not a relabel); task32 ≡ phase5 rows, 654 positions, 0 delta NaN, f_bar_wt-missing 231 ⊂ own_e_b-missing 587 (so 587−231 = 356 exactly), frame 10,757/654, 11,344−231 = 11,113; task34 and task36 both 11,113 (Part I §6.2's in-repo carriers); V2 10,141 / own_e_b-finite 9,595 / 586 positions / 0 delta NaN, phase5-at-unresolved 1,046, V2 drop 1,203 → implied construct-wt 157 (position list QUOTED from SESSION_LOG L2340, not re-derived from the PDB — disclosed); Z1 CSV matched rows 9,595/586 for both predictors plus its ESM original row 10,757/654 with rho == −0.08811806424891734 to 1e-12 (two-source anchor identity); analysis-frame-at-unresolved 1,017 → 9,740 and 1,046−1,017 = 29; manifest has 11 rows and every n_after traces to a gated variable (built from variables, never re-typed). The manifest's rows carry branch_predictor (per-predictor coverage as the task asked): universe stages 1-5, published-e.b additive (11,113), own_e_b primary (10,757), ThermoMPNN V2 (10,141 → 9,595), matched Z1 intersection (9,595/586 from both directions), SaProt structure-scorable (9,740).
- A2b's two non-re-derivable details are ATTRIBUTED to its logged verification rather than re-claimed: the "all f_bar_a222v NaN" nature of the 557, and the published-e.b ≡ own_e_b missing-mask identity (587 = 587 = 587).

Actual output (verbatim; reported run from session tmp af2_run2.log):
  "G1 rows PASS: 13134" / "G1 type==substitution PASS: 11902" / "G1 type==nonsense PASS: 624" / "G1 type==synonymous PASS: 608"
  "G2 phase3 rows PASS: 11901" / "G2 phase5 rows PASS: 11344" / "G2 subset check PASS: phase5 hgvs set ⊂ phase3 hgvs set" / "G2 drop PASS: 557"
  "G3 task32 rows PASS: 11344" / "G3 positions PASS: 654" / "G3 delta_esm NaN PASS: 0" / "G3 hgvs identity PASS: task32 ≡ phase5 rows" / "G3 f_bar_wt-missing PASS: 231" / "G3 own_e_b-missing PASS: 587" / "G3 mask inclusion PASS: all 231 f_bar_wt-missing rows are inside the 587 (A2b's -356 = 587-231)" / "G3 analysis frame PASS: 10757" / "G3 frame positions PASS: 654" / "G3 stage6 n PASS: 11113"
  "G4 task34_predictions rows PASS: 11113" / "G4 task36_analysis_table rows PASS: 11113"
  "G5 V2 rows PASS: 10141" / "G5 V2 own_e_b finite PASS: 9595" / "G5 V2 delta_esm NaN PASS: 0" / "G5 V2∩own_e_b positions PASS: 586" / "G5 phase5 rows at 59 unresolved PASS: 1046" / "G5 V2 drop total PASS: 1203" / "G5 implied construct-wt drop PASS: 157" / "G5 cited verbatim: 157 rows at 9 construct-wt-mismatch positions (429, 594, 645, 646, 647, 648, 649, 650, 651) (SESSION_LOG L2340; position list quoted, not re-derived from the PDB)"
  "G6 matched rows (2 predictors) PASS: 2" / "G6 matched n_rows PASS: [9595]" / "G6 matched n_positions PASS: [586]" / "G6 ESM original n PASS: 10757" / "G6 ESM original positions PASS: 654" / "G6 anchor PASS: Z1's ESM rho == -0.08811806424891734 (two sources)" / "G6 ESM loses PASS: 1162"
  "G7 analysis-frame rows at 59 unresolved PASS: 1017" / "G7 scored base PASS: 9740" / "G7 Z3f's '29 not in the 10,757 set' PASS: 29"
  "G8 manifest rows PASS: 11" / "G8 PASS: every n_after traces to a gated variable"
  RECONCILIATION block: "11,902 missense total -> stage 2 (proposal; script-50 gate)" / "11,344 Part II §12 -> stage 4/5 (phase5/task32, RESULTS.md L56)" / "11,113 Part I §6.2 -> stage 6 (task34/task36, MTHFR_RESULTS_LOG §6.2)" / "10,757 primary frame -> stage 7 (ESM-2 + 6.3 strata)" / "10,141 ThermoMPNN V2 -> stage 8 (script 68)" / "9,740 SaProt scorable -> stage 11 (script 70, Z3f)" / "9,595 matched set/586 -> stages 9+10 (Z1, AD8)"
  "single cascade saved -> task_AF2_variant_manifest.csv (11 rows)" ; "AF2 DONE"
  First run (rejected, gate caught my bug, af2_run.log): "*** G7 task32 rows at 59 unresolved: got 1046, expected 1017 — manifest NOT written ***"
  LIMITATIONS printed (external-doc attribution; A2b attributions vs re-derivations; 157 position list quoted not re-derived).

Verdict: PASS — every disputed n is now one row of one cascade, each traced to a named script AND recomputed from the file it lives in (40/40 gates on the reported run). Plainly:
- The three missense totals are three FILTERED VIEWS of one universe, not competing counts: 13,134 raw → 11,902 missense (type filter; the proposal's number) → 11,901 (one variant lacks an ESM WT score, script 15) → 11,344 (phase5's model dropna, −557; Part II §12's carrier) → 11,113 (f_bar_wt dropna, −231; Part I §6.2's carrier) → 10,757 (e.b/own_e_b required, −356). Every step's dropped rows were checked here for identity, subset, or mask inclusion — no dropped-row mystery remains (A2b's PASS independently reproduced on today's files, including the previously-unverified-to-me fact that task32 ≡ phase5 exactly and that the 231 f_bar_wt-missing rows sit entirely inside the 587 own_e_b-missing rows).
- The four analysis n's are three PREDICTOR BRANCHES off that cascade: 10,757/654 (ESM-2 delta_esm primary), 10,141 (ThermoMPNN: 11,344 minus 1,046 forced unresolved-position drops minus 157 construct-wt-mismatch drops, script 68's own stage-3 output) with 9,595/586 once own_e_b is required — which is also the matched ESM∩Thermo intersection (ESM side loses 1,162, Thermo side loses 0), and 9,740 (the 10,757 frame minus its 1,017 rows at unresolved positions; the SaProt-scoring base, full run still pending as Z3f).
- Poster note (the task's own suggestion): the CSV's 11 rows are CONSORT-ready — start box 13,134, one box per filter with script attribution, three branch ends (10,757 / 9,595 / 9,740).

Files: NEW scripts/85_af2_variant_manifest.py (pre-registered docstring; gates G1-G8; refusal to write on mismatch); NEW data/processed/task_AF2_variant_manifest.csv (11 rows × 9 columns: branch_predictor, stage, filter_step, applied_by, n_before, n_after, delta_n, appears_in, verified_by — quoted in full in the run output above by construction: every n_after came from a gated variable). Ephemeral session-tmp logs: af2_run.log (first run, G7 FAIL exit 1), af2_run2.log (REPORTED RUN, exit 0). Inputs read-only: task35_epistatic_set.csv, phase3/phase5_analysis_table.csv, task32_analysis_table.csv, task34_predictions.csv, task36_analysis_table.csv, task_V2_thermompnn_ddg.csv, task_Z1_matched_n_headtohead.csv; log sources OVERNIGHT_LOG, comparators SESSION_LOG, GROUPS_C_TO_H_DIGEST, CLOSEOUT_LOG, this DEEPDIVE_LOG, MIGRATION_LOG, MTHFR_RESULTS_LOG (all read-only). No existing script, lib, or result modified; next free script number 86.

Unexpected: (1) FIRST RUN FAILED G7 — my gate counted unresolved-position rows on the 11,344 table (got 1,046) when Z3f's 1,017 is defined on the 10,757 analysis frame; the identity gate G3 had just proven task32 ≡ phase5, which is WHY the table-level count equals V2's 1,046. Fixed the gate's base (not a threshold, not a rule — an implementation error in a verification), disclosed in the script's own docstring and this entry; the failed run wrote nothing (by design: mismatch → exit 1 before the CSV). (2) Part II §12 is external to this repo ([AD7]'s established finding) — attributions anchored to in-repo carriers instead; flagged in limitations rather than papered over. (3) The 157-row construct-wt-mismatch figure could only be obtained as arithmetic (1,203−1,046) plus the verbatim position list from SESSION_LOG — PDB re-derivation deliberately NOT attempted (out of scope for a manifest; disclosed in output). (4) SaProt's actual scored-to-date n (74 rows @ 4 positions, smoke) is NOT a cascade stage — noted in stage 11's appears_in so the pending full run is visible rather than implied complete.
---
## [AF3] — Audit of Part I's five flagged items against the logs themselves: 3 DONE, 2 PARTIAL — cluster-robust inference is headline-consistent but five exploratory-era cell-level nulls were never repaired; the S2 sign audit reached ThermoMPNN (AD1) but no labeled-example sign control exists for SaProt

Status: EXECUTED — AUDIT COMPLETE (read-only; no computation, no new files; each status below carries the file+line of the log entry it came from, as the task requires).

Time: start 18:24:00 (after [AF2] 18:23:32), finish 18:27:00. Runtime: grep/read evidence gathering only (~3 min; zero compute — this is the cheapest task in the doc).

What I did:
- Read task AF3 (doc L379-388): "Check, plainly, whether each of the following has actually been executed anywhere in this project's logs (not assumed): cluster-robust inference used consistently throughout...; the delta_ESM-vs-S(v|WT) confound check; the full sign-convention audit (S2's original scope — has it been extended to every new predictor added since, e.g. ThermoMPNN, SaProt?); the oracle/ceiling calculation; nonlinear (spline) fitness controls. Report a plain done/not-done/partial status for each, with the log entry it came from if done."
- For each item, located the actual entries (OVERNIGHT_LOG, comparators SESSION_LOG/digest, CLOSEOUT_LOG, this DEEPDIVE_LOG) and the scripts that exist on disk; nothing is claimed from memory — every line below was grepped or read this session. No file was created or modified (the deliverable is this entry, per the task's own wording).

Actual output (the five-item audit; verbatim quotes from the cited entries):

  ITEM 1 — "cluster-robust inference used consistently throughout (not just in some scripts)": PARTIAL.
    The consistency audit itself exists and was executed: OVERNIGHT_LOG L40-41 "## A1a — Audit: which scripts' CIs/nulls are position-level vs row/cell-level / Status: PASS (audit completed; one real convention violation found — sign-flip nulls are cell-level)". Digest verbatim (GROUPS_C_TO_H_DIGEST L13): "resid = (13134, 4) → flips at (variant × condition) cell granularity in scripts/21:138, 24:140, 26:135, 28:172, 33:100; second violation scripts/26:85 row-level target shuffle. All headline CIs position-clustered as claimed." Repair executed for the headline: A1b (OVERNIGHT L60; digest L14) reran script 33's null at position blocks — "observed −0.0881, position null mean −0.0001, sd 0.0156, p <0.0001, ≈0.1% structural artifact ... Identity max|diff| = 2.220e-16" — and B2 (digest L26) restates it: "The '~0% artifact' claim in 5.3 SURVIVES position-block granularity". A1c (OVERNIGHT L99-108) confirmed script 34's CIs resample positions: "paired_metric_difference_bootstrap(d, "position", ...)" ... "Saved CSV confirms: pooled rows carry n_clusters=654 ... n=11113, n_clusters=654" — PASS. Later scripts follow the convention: F1a's OLS used "cluster-robust SE by position" (OVERNIGHT L1003); script 68's docstring "position_cluster_bootstrap ... identical machinery to scripts 32/33"; every entry in this log (scripts 63-85) uses position-cluster bootstrap or position-level nulls (e.g. [AD8] L2872 "position-cluster bootstrap ... ALL ranks recomputed per draw"). WHAT IS NOT DONE: the cell-level nulls in scripts 21, 24, 26, 28 (and script 26's row-level target shuffle) were NEVER re-run at position granularity — only script 33's was (by A1b). So "consistently throughout" is literally FALSE for five exploratory-era nulls on disk; the honest status is PARTIAL: all headline CIs and nulls are position-level (audited + re-verified), five old non-headline null outputs remain cell-level and must not be cited as position-level.

  ITEM 2 — "the delta_ESM-vs-S(v|WT) confound check": DONE.
    Entry: OVERNIGHT_LOG L164 "## B1a — Partial correlation of delta_ESM vs e.b controlling S(v|WT) + w.fitness (spline)" — "Wrote scripts/43_flattening_partial.py (B1a + B1b sections; pre-registered collapse criterion in docstring: |partial| < 50% of |raw| = COLLAPSE). Nuisance model = natural cubic spline df=4 per covariate on ranks, refit inside every bootstrap draw, positions resampled (n=10,757, 654 positions) ... Smoke at N_BOOT=200 (5.5 s), full run at N_BOOT=10000 (3:55.82 total)" (L168; a p-value bug was fixed and disclosed BEFORE the full run). Results digested verbatim: B1a (digest L23) "PASS — does NOT collapse; the flattening confound does not explain the correlation ... own_e_b partial −0.0828 (ratio 0.940) / −0.0853 (0.968); GI partial −0.0786 (1.111) / −0.0803 (1.136) — retains 94–114%"; B1b (digest L24) "PASS (test ran; answer: a real monotone relation exists but the compression form explains little variance ...): Spearman(delta_ESM, S(v|WT)) = −0.3238 [−0.3653, −0.2803]; OLS R² = 0.0645; through-origin R² = 0.0584, k ≈ 0.00698". Related executed companions: B2 position-block null (digest L26); script 44's S_WT-retention check (OVERNIGHT L425 "RETENTION IS NOT BACKGROUND-SPECIFIC ... difference +0.0124 with CI [−0.0375, +0.0370], p=0.9630"); script 45 C1d direct S(v|A222V) vs S(v|WT) (script 45 L185).

  ITEM 3 — "the full sign-convention audit (S2's original scope — has it been extended to every new predictor added since, e.g. ThermoMPNN, SaProt?)": PARTIAL.
    S2 original: DONE — OVERNIGHT L1863 "S2 PASS (both sign conventions verified on labeled rows: e.b<0 ⇔ less functional in A222V; delta_ESM<0 ⇔ ESM says worse in A222V)".
    ThermoMPNN: EXTENDED — [AD1] (this log L509-599), the STOP-FIRST audit, PASS with four independent layers quoted there verbatim: forward formula (transfer_model.py 113-116, subtract_mut true), repo semantics ("idxmin(ddG_pred) per position as the BEST mutant, i.e. most negative = most stabilizing => positive = destabilizing"), external characterization (Dieckhaus 2024: "More positive d∆G values indicate more destabilizing mutations"), and an empirical positive control ("p.Phe516Asp ... Relative ASA = 0.0 ... ddG = +4.067"; "ALL 123 buried (rsa<0.10) hydrophobic->charged substitutions score positive (median +2.629 ... ) ... 88.9% of all 10,141 missense score destabilizing"). Verdict (L562): "the sign is NOT flipped; -0.0733 keeps its sign and the Part II section 12 interpretation does NOT invert".
    ThermoMPNN-D: PARTIAL-but-substantial — [AD4] gated orientation ("G1 bounds + three-way wt match PASS: all 10141 rows (V2 wt == D-seq[resi-40])", L2314) and vendor agreement ("G4 cross-model PASS: spearman(ddG_single_D, ddG_vendored) = 0.9382 over n=10141", L2323), with direction inherited from AD1's parent-model convention; no independent labeled ddG control specific to the doubles. The opposite-sign external pitfall was itself caught in-project: [AD2] L2040 "The two comparison targets use OPPOSITE sign conventions (ThermoMPNN + = destabilizing; IJMS − = destabilizing)".
    SaProt: NOT done — script 70 pre-registers conventions (docstring: "Every convention below was fixed by the closeout task doc") and defines delta_SaProt = S_SaProt(v | A222V bg) − S_SaProt(v | WT bg) (closeout L170), checks orientation ("wt_aa agrees with chain-A ori_aa on all scored rows: True (74/74)", CLOSEOUT_LOG L618), and verifies the NULL machinery ("[G6] all-+1 flips reproduce own_e_b exactly: max|diff|=9.714e-17", L631) — but there is NO labeled-example positive control of SaProt's OWN score direction anywhere (nothing AD1-style, nothing H1a-style). The full Z3f-Z3i runs are still pending, so this gap is live, not historical.
    ESM-1v: NOT run at all (AC4 blocked by the 3GB/file cap, awaiting user decision) — no sign audit exists or could yet.

  ITEM 4 — "the oracle/ceiling calculation": DONE.
    Entry: OVERNIGHT_LOG L575-576 "## C3a — Oracle ceiling + correlation disattenuation / Status: PASS — ceiling computed and USABLE (pre-registered CI rule met); disattenuation verdict = MATERIALLY LARGER (pre-registered ratio rule met, narrowly — magnitude caveat in the verdict)". Script on disk: scripts/47_c3a_oracle_ceiling.py. Spec: REVIEW_TRIAGE L121-124 ("Build a synthetic 'oracle' predictor: true e.b + noise matched to ... Report 6.3's −0.00241 loss against that ceiling"). Digest verbatim (L40): gates "|diff 0.000e+00, rebuild 2.220e-16"; "Reliability own 0.6363 / published 0.6193"; "Oracle POOLED +0.0366 CI [+0.0309, +0.0424]"; "ESM-2 vs ceiling pooled +0.000308 = +0.84%, high −0.002409 = −4.62%"; "Disattenuation r_dis = −0.110413 CI [−0.147534, −0.072340], |r_dis|/|rho| = 1.2530 → MATERIALLY LARGER (threshold 1.25 — Report as 'meets the bar narrowly, not as a comfortable pass')"; "Oracle is circular — sizes a ceiling only, NOT an achievable model".

  ITEM 5 — "nonlinear (spline) fitness controls": DONE (executed twice, independently).
    (a) Script 43's B1a nuisance model IS a spline fitness control: "natural cubic spline df=4 per covariate on ranks, refit inside every bootstrap draw, positions resampled" (OVERNIGHT L168), full run executed (3:55.82), result above in item 2.
    (b) F1a: OVERNIGHT L999-1022 "## F1a — Nonlinear fitness control on 3.1's multivariable model [item 21a]" — "New script scripts/51_f1_control_specification.py ... re-runs proposal 5.6e / results-log 3.1's exact model ... with base fitness entered NONLINEARLY: PRIMARY = f_bar decile dummies (drop-first), SENSITIVITY = f_bar + f_bar² quadratic", with its own pre-registered gate ("linear re-run must reproduce tier2_multivariable.csv coefs/CIs to 1e-6 with n match for all 6 models, else FAIL/no-retry") — digest L61 verbatim: "PASS (test ran, gate identity check passed) — pre-registered verdict: CHANGED (GI_folinate_independent binned-spec COEF ROBUST in 1/2 error metrics). Gate max|coef/ci diff| = 2.4e-17 … 9.0e-17, all 6 models, n match True. Headline (n=9756): rank linear f_bar +0.0521 → binned +0.0573 [+0.0303, +0.0842] (robust); calibrated linear −0.0590 → binned +0.0352…+0.0723 center +0.0537 (sign flip → not robust); ... r2 jumps 0.03 → 0.52–0.57 nonlinearly. Both binned metrics positive with CIs excluding 0 → 3.1's survival criterion still holds; what fails is the published negative calibrated sign." (Reported as CHANGED per its own rule — digest L1257: "F1a is a CHANGED verdict by its own rule — it must be reported as".)

Verdict: AUDIT COMPLETE — plain statuses as the task asked: item 1 PARTIAL, item 2 DONE, item 3 PARTIAL, item 4 DONE, item 5 DONE. The two PARTIALs are real gaps, not wording quibbles: (1) five old scripts (21/24/26/28 + 26's shuffle) still carry cell-level/row-level nulls that were audited but never repaired — the headline was repaired (A1b/B2) and re-verified, so no current claim rests on the unrepaired ones, but their printed nulls must not be cited as position-level; (2) the S2 extension exists for ThermoMPNN (AD1, strong) and partially for ThermoMPNN-D (orientation + vendor agreement), but SaProt has NO labeled-example sign control of its own score direction — relevant because its full run (Z3f-Z3i) is still pending, which is flagged here for the user rather than acted on (changing a pending pipeline step is a judgment call, not an audit action). Item 3's ESM-1v sub-status inherits AC4's block (open user decision). Everything else the reviewer flagged has a dated, quotable execution.

Files: NONE created or modified (read-only audit; the deliverable is this entry per task L387-388). Read-only sources: OVERNIGHT_LOG, GROUPS_C_TO_H_DIGEST, SESSION_LOG (comparators), CLOSEOUT_LOG, REVIEW_TRIAGE, this DEEPDIVE_LOG; scripts on disk verified exist: 43, 44, 45, 47, 51, 68, 70 (ls/grep this session).

Unexpected: (1) item 1's literal claim ("throughout") is contradicted by the project's OWN audit verdict ("one real convention violation found") — reported PARTIAL as-is rather than smoothed to DONE (AGENTS s0); (2) the SaProt sign-control gap is live, not historical — surfaced as a flag for the pending Z3f-Z3i decision, deliberately NOT acted on; (3) F1a's pre-registered verdict is CHANGED (not a clean pass) and is quoted as-logged rather than summarized favorably; (4) no computation was needed anywhere — the audit was completable entirely from dated log entries, which itself is a finding: this project's logging discipline made a five-item evidence audit a ~3-minute task.
---
## [AG] — Group AG read in full, acted on NOTHING (per the task's own instruction: evaluator framing/strategy/presentation questions, for the user's judgment)

Status: READ — NO ACTION TAKEN (this is the correct completion state: the task doc L392-397 says these are the evaluator's framing/strategy/presentation questions, "listed here only so they are visible in this doc, not because any of them should be attempted by an automated session").

Time: start 18:27:30 (after [AF3] 18:27:08), finish 18:29:00. Runtime: read-only, ~1.5 min.

What I did:
- Read Group AG verbatim in full (task doc L392-415), immediately after completing AF3, exactly once, as required by the group's own header ("NOT for unattended execution; read once, do not act on tonight").
- Deliberately did NOT draft the one-sentence claim, did NOT rank the ~40 scripts, did NOT pick a second system, did NOT build figures, did NOT compute the ClinVar-in-cis number, did NOT draft any co-author contact or AI-use disclosure. Every one of those is a judgment or communication act belonging to the user; attempting them would violate the group's instruction and, for several (one-sentence claim, poster figures), would pre-empt framing decisions the evaluator addressed to the user.
- Recorded the seven questions below verbatim-as-listed so the user has them in one place alongside the summary of tonight's work (they are already in the task doc; this entry only confirms they were surfaced, not answered).

Actual output (the seven questions as listed in the doc, each followed by its status tonight):
1. "What is the project's one-sentence claim, and which of the ~40 scripts in this repo are actually load-bearing for it (vs. cuttable from a poster)?" — NOT ATTEMPTED (user judgment). Related evidence exists in-repo for whoever answers it (AF1's digest for the metric-dependence framing; AF2's 11-row manifest for the analysis-set story; AF3's item-1 answer for which scripts' nulls are position-level).
2. "What is the 'second system' that would turn this from a case study into a general claim about PLMs (CBS, a ProteinGym multi-mutant assay, or the GB1 transplant from Group AA)?" — NOT ATTEMPTED (user judgment). Note for the user: the GB1 transplant (AA1/AA2) and a ProteinGym survey (AB1-AB4) were actually executed tonight and their verdicts are in this log, so this question now has real inputs.
3. "What is the concrete deliverable (a released benchmark, a calibrated trust-rule keyed to alignment depth, a 'conditionally damaging' classifier)?" — NOT ATTEMPTED (user judgment). Related executed evidence: AD6's depth discriminator (pooled +0.1714 [+0.0918, +0.2471], region 4 reversed) is the alignment-depth-keystroke candidate; AA4 is the benchmark-style detection floor.
4. "What is the clinical framing number (how many ClinVar VUS sit in cis with A222V, and how many would be scored differently)?" — NOT ATTEMPTED (requires a ClinVar data fetch, which is barred by the ≈196.3/200MB session data-fetch cap anyway — would need user decision on both counts).
5. "Whether and how to contact the atlas co-authors (region-4 finding) and the GB1 paper's authors (the ε discrepancy) directly." — NOT ATTEMPTED (communication by the user; note AA6 resolved the ε=7.40-vs-5 discrepancy as a threshold identification, so that second contact may be unnecessary — the user's call).
6. "Which three figures to build for a poster." — NOT ATTEMPTED (user judgment). AF2's task text itself flags its manifest as "a strong candidate poster figure (a CONSORT-style flow diagram) once visualized" — that observation is the task's, repeated here without acting on it.
7. "The AI-use disclosure and personal-contribution accounting the evaluator flagged as something a judge will press on directly — this is for the user to prepare, not something a coding session produces." — NOT ATTEMPTED, explicitly by the doc's own words.

Verdict: READ-ONLY COMPLETE — Group AG surfaced, zero of its seven items acted on, as instructed. Nothing in tonight's work depends on any AG answer, and no AG answer was generated.

Files: NONE created or modified (this entry only). Read-only: DETECTION_FLOOR_AND_MECHANISM.md L392-415.

Unexpected: nothing — the group behaved exactly as documented. Worth flagging for the user: item 4 (ClinVar) is double-blocked (judgment + fetch cap) and item 2's inputs are now richer than the doc assumed, since AB1-AB4 and AA1-AA7 both ran.
---
## SUMMARY

**Deep-dive (DETECTION_FLOOR_AND_MECHANISM) complete: all 32 tasks have a
logged verdict — 26 PASS, 1 FAIL by its own pre-registered gate, 1 SKIPPED
by trigger, 3 BLOCKED awaiting user decisions, 1 audit — plus Group AG
read-once with zero items acted on. Evaluator top-3: 2 of 3 executed
(AC4 blocked). 15 new scripts (71-85), 1 new lib module, zero existing
files modified, zero commits (HEAD edb6017).**

Span: 2026-09-23 21:26:34 ([AF1] start) → 2026-09-24 18:29:00 ([AG]
finish). 33 entries (32 tasks + AG), one per task in the mandated format
(Status/Time/What I did/Actual output/Verdict/Files/Unexpected), each
carrying verbatim output. Execution order honored as pinned: AF1 → AB →
AA4 → AC4 → AD1-AD8 → AE1-AE4 → AF2 → AF3 → AG.

### Evaluator's own top-3 picks

1. **Read the Group C-H digest — DONE, PASS** ([AF1] L13): read in full,
   Group C quoted verbatim; the metric-dependence question now has its
   answer on disk.
2. **All five ESM-1v seeds — BLOCKED** ([AC4] L436): AC4b's total-disk
   check fails by 15.76 GiB; options await the user. AB2b independently
   confirmed ProteinGym ships only two aggregate ESM-1v columns
   (ESM1v_single / ESM1v_ensemble), so no free substitute exists.
3. **Project-own detection floor — DONE, PASS** ([AA4] L329): quotable
   sentence as the evaluator requested: **"we could have detected
   rho >= 0.05; we observed -0.088."** Every gate green at full N
   (identity 2.220e-16; type-I 0/50; sign-flip null centred +0.00002);
   power saturated at 1.00 already at the smallest nonzero grid point —
   the real floor lies below 0.05 and the grid cannot say where
   (disclosed; no adaptive points added).

### Verdicts by group (each line from its entry's Status/Verdict)

- **AA**: AA1 PASS — GB1 transplant: the sign-flip null DOES centre on
  zero off-MTHFR (null mean -0.0004 inside the 0.00845 band), but the
  detection result is a **plain null** (rho +0.1222, p=0.3849, n=57),
  reported untuned — background not switched after seeing f(V54A)=1.37.
  AA2 PASS — unit of analysis / effective n stated from printed output.
  AA3 PASS — mechanism identified (block-restricted permutation;
  0.3880 → 0.2476). AA4 PASS (top-3, above). AA5 PASS — distance caveat
  written (local vs distant epistasis scope limit). AA6 PASS — the
  ε=7.40-vs-5 discrepancy RESOLVED (threshold identified). AA7 PASS —
  second positive control GRB2: signed **+0.1153, p=0.0019**, and
  centering again YES (replicates AA1).
- **AB**: AB1 PASS — ProteinGym DOES include this assay: UniProt
  `MTHR_HUMAN_Weile_2021`, 95 model-score columns (27 families),
  curated MSA 4,783 seqs (MSA_N_eff 646.2, category Low), singles-only
  12,464; ≈11 MB fetched via HTTP Range central-directory parsing,
  within the session cap; one in-entry number correction disclosed.
  AB2 **FAIL (AB2a)** — pre-registered identity gate tripped: its chosen
  row A222V is structurally absent from script 32's table (0 rows @222);
  the join itself was exact (10,757/10,757). Fixing the gate means
  changing a pre-registered test → logged as an open user decision, not
  done. AB2b: only two ESM-1v aggregates exist → AC4's direct fetch
  remains necessary. AB2c: EVmutation column exists (A222V -4.863357) —
  valid score-level substitute, NOT a J-matrix. AB3 SKIPPED — trigger
  ("if NOT found") false after AB1's find. AB4 BLOCKED — EVmutation
  pairwise parameters and double-mutant scores do not exist in the
  shipped file, and the AB3b Neff/L=0.99 floor blocks training couplings;
  nothing fabricated, no rho reported.
- **AC**: AC1 PASS — 150M run n=1,900 rows / 100 positions; implied
  effective n ≈210.9 (~200) and ≈4,599 (~4,500) — evaluator's figures
  confirmed; design effect 2.34; 650M bootstrap confirmed
  position-clustered, possible-bug branch did not trigger. AC2 PASS —
  direct 150M-vs-650M agreement stated plainly as the evaluator's
  proposed reading. AC3 PASS — median |delta_ESM| = 0.04660 nats;
  fp32/fp64/batch/CPU rescore with code-verified producer facts.
  AC4 BLOCKED (top-3, above). AC5 PASS — script 67's delta_PLL
  position-222 term **cancels cleanly as intended** (gates Z2c).
  AC6 BLOCKED — esm2_t36_3B = 5,678,116,398 B exceeds the 3 GB/file cap
  (pre-registered size rule fired); bytes already on disk; waiver
  options await the user; nothing else depends on it (Z3f-Z3i need only
  SaProt_650M + foldseek, both local).
- **AD**: AD1 PASS (STOP-FIRST) — sign NOT flipped: four-layer chain +
  empirical positive control; -0.0733 keeps its sign, Part II §12 does
  not invert. AD2 PASS — the model DOES miss A222V, stated plainly.
  AD3 PASS — threshold/sigmoid built and fit; inverted-U shape DOES NOT
  appear. AD4 PASS — ThermoMPNN-D interaction **DOES NOT capture
  own_e_b** (all three frozen conditions). AD5 PASS — -0.0733 SURVIVES
  task-literal multivariable controls (sign differs by FE granularity,
  disclosed). AD6 PASS — |delta_ESM| tracks per-position Neff: pooled
  **+0.1714 [+0.0918, +0.2471]** CONFIRMED per the frozen rule WITH the
  pre-registered region-4 reversal (region 4 -0.2373). AD7 PASS —
  region-4 §12.4 anchor **HOLDS** under dimer scoring (Δrho_4 -0.0136
  [-0.0302,+0.0009] p=0.0706; the pooled -0.0076 [-0.0152,-0.0007]
  p=0.0292 weakening disclosed separately, outside the frozen rule).
  AD8 PASS — case (i): BOTH predictors independent (unique_T 0.004455,
  unique_E 0.005034, both p<1/10000; near-orthogonal, rho_ET +0.0883) —
  with the effect-size caveat in the same verdict: R²_full only 1.04%.
- **AE**: AE1+AE2 PASS (one shared run) — frozen rule fired MIXED
  DIRECTION and was read as-is: D_identity -0.014518 [-0.022077,
  -0.006934] p=0.0006 (identity at 222 ATTENUATES: A222V rank 16/19) and
  D_position +0.025601 [+0.013702, +0.039236] p<1/10000 (position-222
  ELEVATION: 1.68x the A>V-elsewhere median). AE3 PASS — Val fraction at
  the aligned 222 column 0.021748 (104/4,782); rho +0.107780
  [+0.024259,+0.191756] p=0.0120, SURVIVES depth control (Neff-adj
  +0.123565 [+0.039702,+0.206380] p=0.0038) — CONSISTENT, offered
  strictly as a candidate with the region-4 caveat. AE4 PASS — accuracy
  WORSENS with shift magnitude: Delta_signed -0.100530
  [-0.170813,-0.032004] p=0.0046; Q4 -0.110803 (CI<0 → the
  "most confidently wrong where it moves most" framing permitted and
  used); secondary |.|-|.| flat (p=0.1776) reported without a rule;
  effect bounded (~1.2% rank variance, every |rho| ≤ 0.167).
- **AF**: AF1 PASS (top-3, above). AF2 PASS — one 11-stage cascade
  reconciling 13,134 → 11,902/11,344/11,113 → 10,757 / 10,141 / 9,740 /
  9,595 per predictor, **40/40 gates** recomputed from disk, saved as
  `data/processed/task_AF2_variant_manifest.csv`; the first run failed
  its own G7 (wrong base table) and wrote nothing; fixed to the
  documented basis, disclosed in script + entry. AF3 AUDIT COMPLETE —
  five flagged items: cluster-robust consistency **PARTIAL** (five
  exploratory-era cell-level nulls never repaired; headline re-verified
  by A1b/B2), delta_ESM-vs-S(v|WT) confound **DONE** (B1a/B1b), sign
  extension **PARTIAL** (ThermoMPNN yes via AD1; SaProt has no
  labeled-example control), oracle/ceiling **DONE** (C3a), spline
  controls **DONE** (B1a + F1a).
- **AG**: READ — NO ACTION TAKEN on all seven framing questions, exactly
  as the group instructs.

### What this deep-dive changed about the project's claims

- **Strengthened with new evidence**: the headline now has a
  project-own power statement (AA4); ThermoMPNN's sign is audited (AD1)
  and its -0.0733 survives controls (AD5), dimer scoring (AD7), and a
  joint model where both signals are independently detectable (AD8);
  the depth discriminator is confirmed pooled (AD6); the mechanism
  question decomposes into position-vs-identity (AE1/AE2) with a
  depth-surviving candidate explanation (AE3); CI-width and precision
  concerns reconcile numerically (AC1/AC3); a second positive control
  exists (AA7); the ε discrepancy is resolved (AA6); the exact assay
  exists in ProteinGym (AB1).
- **New negatives, reported plainly (AGENTS §0)**: GB1 transplant
  detection null at n=57 (AA1); AB2a pre-registered gate FAIL; AB4
  BLOCKED; AD3 shape absent; AD4 interaction absent; AE1 identity
  attenuation at 222; AE4 accuracy worsens with magnitude; AD6's
  region-4 reversal; AD7's pooled weakening; AF3's two PARTIALs.
- **Discipline held**: every frozen rule fired as written (AE1/AE2's
  MIXED DIRECTION read as-is; AE4's framing gated on both CIs); no test
  was re-tuned after a result; AB2a's tempting fix (new gate row) was
  NOT taken because it would change a pre-registered test.

### Blocks awaiting user decisions (not resolvable unattended)

1. **AC4** — five ESM-1v seeds: disk check fails by 15.76 GiB (staged
   fetch-score-delete / cap waiver / keep blocked).
2. **AC6** — 3 GB/file cap waiver for esm2_t36_3B (bytes already on
   disk; resume costs zero transfer).
3. **AB2a** — gate-row fix = changing a pre-registered test (one-line
   fix + one smoke rerun is the user's call).
4. **AB4** — needs real EVmutation/EVcouplings MTHFR parameters, or
   authorization for a Potts fit despite AB3's false trigger.
5. **Data-fetch cap** — session ≈196.3/200 MB; no further member fetch
   without a decision (also blocks AG item 4's ClinVar pull).
6. **Z0/U3** (closeout) — overlaps AC4's waiver question.
7. **AD6's AB3b-floor judgment** — region-4 depth caveat carried in
   AD6's own entry.
Plus Group AG's seven framing questions (read, deliberately unanswered).

### Disclosures on record

Every fix made after a first run is in the script's own output AND the
entry's Unexpected block: AA4's post-smoke/pre-full-run generator fix;
AB1's in-entry number correction; AF2's wrong-base first run (exit 1,
nothing written); AE1's two externally-interrupted attempts before the
checkpointed third succeeded; AD6's one disclosed gate fix; AE4's peek
disclosure; AE3's four smoke-caught defects fixed before the reported
run; AD7 = zero third-party edits. The Z3f-Z3i reversion and the
absence of a `timeout` binary for Z2c will be disclosed in the
CLOSEOUT_LOG when those run.

### Files (all new; nothing existing modified)

- Scripts: 15 new numbered scripts `71_proteingym_model_comparison.py`
  … `85_af2_variant_manifest.py` (script 70 pre-exists from closeout).
- Lib: 1 new module `scripts/lib/position_null.py` (for script 77's
  position-shuffle test); no existing lib module touched.
- Outputs: `task_AA4_detection_floor.csv` (306 rows), `task_AA1_*`,
  `task_AA5_distance_caveat.txt`, `task_AA7_*`, `task_AC3_*`,
  `task76…84_*.csv`, `task_AF2_variant_manifest.csv` (11 rows), plus
  session-tmp logs. `data/processed/` untracked by design.
- This log: `DEEPDIVE_LOG.md`, 33 entries + this SUMMARY.

### What remains (closeout — not deep-dive)

Z2c (the 5-hour capped compute item, run under the harness timeout
because no `timeout`/`gtimeout` binary exists — substitution disclosed
at closeout), Z2d, the Z3f-Z3i full runs, then the closeout log's own
SUMMARY. Nothing in the deep-dive depends on those, and neither AC6 nor
AC4 blocks them.
