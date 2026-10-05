# PHASE4B_MORNING_LOG — session 4b (verify, interpret, reproduce)

Template per PHASE4_STRENGTHENING.md §S1. Entries appended immediately after each task finishes.

## [SESSION HEADER] - session 4b opened
Status: IN PROGRESS
Time started: see C0 for the exact `date` output
What I did: Re-read `AGENTS.md` in full (222 lines); `docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md` Part C (lines 234-244) and, earlier in this session, the whole doc including the five frozen appendices; the five extracted pre-registrations plus Amendments 1, 2 and 3 (all eight sha256 re-verified unchanged in C0); `docs/tasks/phase4-strengthening/STATE_FOR_LAUNCH.md`; and the whole of `PHASE4A_BUILD_LOG.md` (1,666 lines). Created this log before any other task.
Verdict: proceeding to C0.
Files created/modified: docs/tasks/phase4-strengthening/PHASE4B_MORNING_LOG.md
Anything unexpected or worth flagging: **Night A ran; nights B and C did not.** See C0.
---
---

## [C0] - State and integrity after the nights - PASS, with two nights NOT RUN (reported)

Status: PASS for every check C0 asks for; **nights B and C were never launched** and that is
reported here in full, because it changes which words exist.
Time started / finished: Sun Oct 4 13:24:33 EDT 2026 / Sun Oct 4 13:40 EDT 2026
What I did: read every driver state file that exists and the driver/stage logs; confirmed
nothing is alive; counted `bg_*.csv` per frame and per model against the rosters as a SET
equality; deduped the manifest into a NEW file (the original untouched); verified every
manifest sha256 against the file on disk; verified all 24 `path sha256` lines in
`STATE_FOR_LAUNCH.md` with my own parser AND through the driver's integrity parser; and, per
this task's instruction, ran `scripts/174_ladder_analysis.py --mode full` myself because Night C
was not run.

Actual output (verbatim where it matters):

`date`, `pmset -g batt`, `sysctl vm.swapusage`, `memory_pressure`
```
Sun Oct  4 13:24:33 EDT 2026
Now drawing from 'AC Power'
 -InternalBattery-0 (id=22020195)	100%; charged; 0:00 remaining present: true
vm.swapusage: total = 3072.00M  used = 1580.31M  free = 1491.69M  (encrypted)
System-wide memory free percentage: 55%
```

**Nothing is alive** (a driver, scorer, analysis or launcher would all show here):
```
ps aux | grep -E "phase4_driver|171_neigh_score|173_ladder_score|launch_phase4|172_neigh|174_ladder" | grep -v grep
  none (no driver, scorer, analysis or launcher running)
```

### 1. Which nights ran

- `data/processed/phase4/driver_state_phase4A.json` **exists**; `...phase4B.json` and
  `...phase4C.json` **do not exist**. Night A ran on 2026-10-04 03:44:57 -> 08:22:39 EDT.
  **Nights B and C were never launched** (no state file, no log, no lock record, no ladder
  output directory).
- `driver_state_phase4A.json` (verbatim): `"status": "finished"`, `"plan": "A"`,
  `"driver_pid": 12056`, and **all three stages `completed` with `exit_code: 0` and
  `attempts: 1`** - SA1 03:44:57->08:07:10 (262.2 min), SA2 08:07:10->08:22:39 (15.5 min),
  SA3 08:22:39->08:22:39. `current_stage: null`.
- Driver log: guards PASSED before every stage with REAL readings (SA1: AC ON, battery 80%,
  swap 0.31 GB, free memory 59%, disk 19.81 GiB; SA3: AC ON, battery 99%, swap 1.82 GB, free
  memory 66%, disk 17.74 GiB), precheck OK, and the closing line
  `DRIVER FINISHED: SA1=completed, SA2=completed, SA3=completed`.
- **Budget used vs budgeted:** SA1 **262.2 of 330 min** (the A7d projection was 304 min, so the
  night ran 14% faster than projected), SA2 15.5 of 23, SA3 0.0 of 10. Night A total
  **277.7 of 363 budgeted minutes**.
- The night's own SA3 integrity pass printed `INTEGRITY: RESULT PASS (31 findings)` with 24
  `sha256: MATCH` lines. One line is self-referential and harmless:
  `driver_state_phase4A.json present; stage statuses: SA1=completed, SA2=completed,
  SA3=running` -- the integrity stage reads the state file while it is itself running.

### 2. Set equality per frame and per model (C0)

| directory | bg files | roster expects | verdict |
|---|---|---|---|
| `neigh/` (H frame, SA1) | **50** | 50 | **SET EQUAL** (no extras, none missing) |
| `neigh_nonH/` (nonH, SB4) | directory absent | 50 | never run (night C) |
| `ladder/150M/` (SB1) | directory absent | 97 | never run (night B) |
| `ladder/35M/` (SB2) | directory absent | 97 | never run (night B) |
| `ladder/650M/` | 0 | 97 | **EMPTY BY DESIGN, not a defect** |

The last row needs stating plainly because a naive count calls it a mismatch: the frozen
ladder design says the 650M column is **cached** (Phase 2 rows), so nothing is ever scored
into `ladder/650M/`; that directory exists only because the A8b gate run created it. Script
174 reads the Phase 2 caches instead, which is why the 650M column still computes. The 96
Phase 2 `bg_*.csv` files live in `data/processed/phase2/`.

### 3. Manifest dedupe into a NEW file

`data/processed/phase4/neigh/manifest.csv` has **50 rows** (one per background; columns
`bg_id,frame,n_positions,n_rows,seconds,device,sha256`) and **zero duplicate `bg_id` rows** --
the night ran SA1 on its first attempt, so nothing was rescored. The dedupe therefore removed
nothing, and I say so rather than implying it fixed a duplicate: I wrote
**`data/processed/phase4/neigh/manifest_deduped_4b.csv`** (50 unique rows, sorted by `bg_id`,
last-write-wins rule) and left the original untouched. The other three manifests in the tree
are **scratch** artifacts from the A7d/A8c timing smokes (`neigh_scratch/timing/`,
`ladder_scratch/timing150/`, `ladder_scratch/timing35/`), not night outputs; they hold 3 rows
each and were not modified.

### 4. Every manifest sha256 against the file on disk, and the night's timing

- **50 of 50 match, 0 mismatches.** Every neighbour score file on disk is byte-for-byte the
  file the night recorded.
- Per background: min 271.6 s, median 306.4 s, max 313.9 s; **total 254.1 min** of scoring.
- `n_positions` per background: {454, 455} -- 455 when the background's own position is not
  in H, 454 when it is, exactly as the frozen protocol requires.
- Frames: `{H}` only. Device: `{mps}` only.
- **Free reproduction check (not requested, but it fell out and it is strong):** the three
  backgrounds the A7d timing smoke scored on Oct 3 at ~16:11 are **byte-identical** to the
  night's files ~12 hours later in a different process -
  `N_214_LV faee2d60683f88c4`, `N_46_RL 679e348c66882620`, `N_182_IV 5eb3ad64c3072a4e`, all
  three MATCH. Same code, same checkpoint, same device, identical bytes.

### 5. sha256 of every staged script, pre-registration and amendment

Parsed `STATE_FOR_LAUNCH.md` myself (any line with a 64-hex digest and a path token) and
compared against the files:
```
  24 'path sha256 <hash>' lines parsed
  verified: 24 unchanged, 0 CHANGED, 0 missing
    night scripts (170-174, driver, launcher)     13
    session-4a scripts (165-169, tests, lib)       6
    reused guards library                          1
    frozen pre-registrations + amendments           8
    frozen neighbour roster                        1
```
The driver's own integrity parser gives the same answer independently: 24 `MATCH`, 0
`MISMATCH`, `RESULT PASS`. The five frozen pre-registrations and Arnav's three amendments are
among the 24 and are unchanged. **Nothing staged in this session has drifted.**

### 6. Night C's stage run by me (C0's explicit instruction)

`N_BOOT=10000 SEED=0 venv/bin/python3 scripts/174_ladder_analysis.py --mode full` ->
`PHASE4B_C0_LADDER_ANALYSIS_OUTPUT.txt`, **exit 0, 26 PASS / 0 FAIL / 4 PENDING**. CPU only
(script 174 imports no torch; it printed `torch in sys.modules: False`).

- The **650M column reproduces session 4a's A8d numbers digit for digit**: rho_A222V on H
  -0.090021683 CI [-0.122385, -0.056046]; p_spec_H(neg) 0.050633 (3/78), p_spec_H(abs)
  0.050633 (3/78); partial given S_W -0.067209 CI [-0.099734, -0.033553]; gradient +0.713319
  CI [+0.566655, +0.808932]; shift confound -0.612697 CI [-0.732776, -0.456234];
  **WORD (650M): MODEL-REPLICATES**.
- **150M and 35M are PENDING: `no 150M wild-type arm (wt_H.csv absent)` / same for 35M**, and
  both cross-model agreements are PENDING for the same reason.

### 7. Which words are therefore still PENDING

| module | word | status |
|---|---|---|
| N | section 5 position-versus-region | **PRESENT: REGION-LIKE** (p_NB(neg) 0.127660 = (1+5)/(1+46), \|NB\| = 46) |
| N | section 6 distance separation | **PRESENT: NEITHER-RESOLVED** (flexible statistic; both CIs include zero) |
| N | full-frame secondary (frozen: secondary, **no word**) | PENDING - needs SB4/SB5 (night C) |
| L | 650M MODEL-REPLICATES | **PRESENT** |
| L | **150M word** | **PENDING - night B never ran, no 150M scores exist** |
| L | **35M word** | **PENDING - night B never ran, no 35M scores exist** |
| L | cross-model agreement (both directions, all four numbers) | **PENDING - needs a second model column** |
| S, M, U, G | all their words | PRESENT from session 4a (cached modules) |

**Two frozen words of module L and the four cross-model agreement numbers cannot be produced,
because the data that would produce them were never scored.** No amount of analysis can
substitute for them; they need night B (SB1, SB2) and then night C's SB3.

Verdict: **PASS (C0), with the two unrun nights reported as the finding.** Nothing protected,
earlier, staged or frozen was edited; nothing was staged, committed or pushed; the driver was
not launched. Proceeding to C1.
Files created/modified: docs/tasks/phase4-strengthening/PHASE4B_MORNING_LOG.md (new),
data/processed/phase4/neigh/manifest_deduped_4b.csv (new; the original manifest untouched),
docs/tasks/phase4-strengthening/PHASE4B_C0_LADDER_ANALYSIS_OUTPUT.txt (new).
Anything unexpected or worth flagging: nights B and C were never launched. Everything module N
needs exists and is internally consistent; module L is half-done by construction (650M only).

---

## [C1] - Re-gate on the real outputs - PASS (every gate passes; rescoring is bit-exact)

Status: PASS
Time started / finished: Sun Oct 4 13:42:49 EDT 2026 / Sun Oct 4 17:28 EDT 2026
What I did: (a) snapshotted every real output directory (counts, newest mtimes, and a
sha256 over the whole (name, mtime, size) listing) BEFORE touching anything; (b) re-ran the
cheap gates on the real outputs - script 165 (the A2 gates), script 166, and script 172 at
the night's exact settings; (c) verified coverage and own-position exclusion directly from
the night's raw files; (d) under the authorisation in this task (scratch-only, read-only with
respect to real outputs; machine idle, free memory 55% > 35%, on AC) rescored 3
never-rescored neighbour backgrounds on H, one per cell, and 2 backgrounds per ladder model
into NEW scratch directories, and compared to the night's files at 1e-6; (e) re-snapshotted
the real directories AFTER and diffed.

### 1. Cheap gates, re-run on the real outputs

| gate | result |
|---|---|
| **script 165 (the A2 gates)** `scripts/lib/phase4_common.py` | **70/70 PASS, 0 FAIL, `GATE PASS`**, exit 0. Identity, reference-gated draw-by-draw, Phase 1 CI, whole-placebo, all word functions' boundary cases (e.g. `word_neighbour`: \\|NB\\| 30 & p<=0.05 -> POSITION-SPECIFIC, \\|NB\\| 29 -> UNDERPOWERED; `word_distance`: a CI *touching* zero does not exclude it; `word_ladder`: 0.10 exactly meets). |
| **script 166 (sign convention)** | **49 checks PASS, 0 FAIL**, exit 0. Its own printed limitation: "RBD direction word UNAVAILABLE locally" - consistent with C3's rule not to describe RBD direction. |
| **script 172 `--mode full`** on the night's real outputs, `N_BOOT=10000 SEED=0` | **33 PASS / 0 FAIL / 0 PENDING**, `GATE PASS`, exit 0, 15.6 min (13:45:00 -> 14:00:34). |

The 172 rerun reproduces the night's SA2 output **value for value**:
```
  p_NB(neg) 0.127660   p_NB(abs) 0.893617   rho_A222V -0.090021683   |NB| 46
  WORD: REGION-LIKE
  PRIMARY flexible-control partial rho_b ~ d3  | spline(dseq): +0.192294 CI [-0.018716, +0.379290]
  PRIMARY flexible-control partial rho_b ~ dseq | spline(d3) : -0.053758 CI [-0.276061, +0.167518]
  SECONDARY linear: +0.341487 CI [+0.158986, +0.502389] -> word 3D-LOCAL; +0.054166 CI [-0.132667, +0.248374]
  WORD: NEITHER-RESOLVED (Amendment 3 item 5, first branch - every planted criterion passed)
  planted confusion matrix: 3D-only truth -> BOTH-LOCAL or worse 0.030; sequence-only truth
    -> 3D-LOCAL or worse 0.010; no signal -> any word 0.070
  cell means: C1 n=13 -0.027997 CI [-0.047893,-0.008961]; C2 n=16 -0.035857 CI [-0.051698,-0.019456];
    C5 n=17 -0.058180 CI [-0.070122,-0.046009]
```
Six headline keys and every section-6 line compared programmatically: **6 identical, 0
different**; the section-6 block, both WORD lines and all cell means are character-for-character
equal. The bootstrap reference gates (G-N4 planted rates, G-N5 identity/reference/Phase 1 CI)
are inside this run and passed.

### 2. Coverage and own-position exclusion, checked directly from the night's raw files

Not via any staged script - I read all 50 `bg_*.csv` myself:
```
  50 bg files vs 50 roster backgrounds
  union of positions across the 50 files: 455    intersection: 424
  distinct own positions among the 50: 50
  rows-per-file distribution: {8645: 19, 8626: 31}
  own-position exclusion + row-count problems: 0 (none)
  distinct header rows across all 50 files: {('bg_id','position','mut_aa','score','delta')}
```
So H = **455** positions; the 31 backgrounds whose own position lies in H carry 454 rows and
the 19 whose own position lies outside H carry 455 - exactly the frozen requirement. Every
file has the same five columns and no duplicate positions.

### 3. Rescoring into NEW scratch directories

**Neighbour arm, 3 backgrounds on H, one per cell of the frozen null set NB.** Chosen as the
first never-rescored background of each cell in `score_order`: **`N_215_KQ` (C1), `N_152_NP`
(C2), `N_183_RM` (C5)** - the three cells Amendment 1 puts in NB. The three A7d smoke
backgrounds were excluded, as instructed. C3 is a fourth cell among the new backgrounds and
was **not** rescored: NB is C1+C2+C5 plus the six existing d3<=12 nulls, so C3 is outside the
headline null set. Out dir: `data/processed/phase4/c1_rescore_scratch/neigh/`.

| background | cell | rows | max abs diff, score | max abs diff, delta | bytes identical to the night's file |
|---|---|---|---|---|---|
| `N_215_KQ` | C1 | 8626 | **0.000e+00** | **0.000e+00** | **True** |
| `N_152_NP` | C2 | 8645 | **0.000e+00** | **0.000e+00** | **True** |
| `N_183_RM` | C5 | 8626 | **0.000e+00** | **0.000e+00** | **True** |

Not merely inside 1e-6: the files are **byte-for-byte identical** to the night's, scored in a
different process ~10 hours later. Gate cost disclosed as pre-registered (NS-DEC7): `--only`
takes a single id, so each invocation re-ran G-N2 (908 passes) - 514.5 s, 593.4 s, 606.8 s -
which is outside the A7d projection formula, as declared. All three exited 0 with G-N2 PASS.

**Ladder, 2 backgrounds per model** (`--limit-backgrounds 2` -> the first two in roster order,
`A222V` and `A222_C`, plus that model's WT arm), each into
`data/processed/phase4/c1_rescore_scratch/ladder_<model>/`.

| model | compared against | result |
|---|---|---|
| **650M** | `data/processed/esm2_a222v_bg_scores.csv` (A222V arm, the file script 174 reads) | max abs diff **0.000e+00** over 8645 rows, 0 unmatched |
| **650M** | `data/processed/phase2/bg_A222_C.csv` (the Phase 2 cache) | max abs diff, score **0.000e+00** over the 8645 H rows (the cache holds 12426 = 654 positions x 19) |
| **650M** | `data/processed/esm2_wt_scores.csv` (WT cache) | max abs diff **0.000e+00**, 0 unmatched |
| **150M** | A8c gate-run files in `ladder_scratch/timing150/` | `bg_A222V`, `bg_A222_C`, `wt_H` all **byte identical** |
| **35M** | A8c gate-run files in `ladder_scratch/timing35/` | `bg_A222V`, `bg_A222_C`, `wt_H` all **byte identical** |

**Stated honestly, because it changes what this proves:** for 150M and 35M **there are no
night files to compare against** - night B never ran. The comparison above is against the
files the A8c *gate run* wrote on Oct 3, so it demonstrates that scoring is deterministic and
reproducible across processes; it does **not** reproduce a night result, and it says nothing
about whether night B would have succeeded. For 650M the comparison is against the Phase 2
caches, which is the strongest reference available and is exactly the column module L's only
word rests on.

Two further internal checks, both exact (`0.000e+00`): `delta == score - WT score` for all
three models over 8645 rows, and each model's WT arm differs from the 650M cache by 16.43
(150M) / 16.62 (35M) while its per-background scores differ from the 650M scores by 16.48 /
16.69 - i.e. the smaller models really are scored separately and each delta uses its own
model's WT arm. A mixed WT source would have silently changed every delta.

Timings observed (s/pass): 650M 0.654-0.684, 150M 0.221-0.227, 35M 0.072 - consistent with
A8c's 0.2414 / 0.0762 medians; the 650M leg is new timing information (27 min for the WT arm
plus 2 backgrounds plus its gates).

### 4. Proof the real output directories were not written

BEFORE (`PHASE4B_C1_REALDIR_SNAPSHOT_BEFORE.txt`) vs AFTER
(`PHASE4B_C1_REALDIR_SNAPSHOT_AFTER.txt`), diffed line by line:
```
DIR data/processed/phase4/neigh    bg_*.csv 50  ALL 55  newest bg mtime 2026-10-04T08:07:10
                                   (name,mtime,size) listing sha 5d74f3fa7d9042020...
DIR data/processed/phase4/ladder/650M  bg 0  ALL 0  listing sha e3b0c44298fc1c14...
DIR data/processed/phase4/ladder/150M  ABSENT
DIR data/processed/phase4/ladder/35M   ABSENT
DIR data/processed/phase4/neigh_nonH   ABSENT
DIR data/processed/phase2              bg 96  ALL 101  newest bg mtime 2026-09-29T12:38:44
                                       listing sha 82ed844ad444ba37...
diff -> IDENTICAL in every line
  50 night files re-hashed after all C1 work: 0 changed (none)
```
Every count, every newest mtime and both listing hashes are unchanged, and all 50 night score
files still match their manifest sha256 after three hours of rescoring. Nothing was written
outside `data/processed/phase4/c1_rescore_scratch/`.

### 5. Limitations, printed here as they must be

- The rescore is a **sample**: 3 of 50 neighbour backgrounds and 2 of 97 per ladder model. The
  other 47 neighbour files rest on the night's own G-N2 gate plus the byte-identity of the
  three A7d files, not on a fresh rescore.
- Rescoring two files per model cannot detect a defect that only affects a particular
  background; it tests determinism, not completeness.
- **Process disclosure:** my first attempt at the ladder rescore (all three models in one
  call) was interrupted by a tool abort partway through the 150M gates. I checked before
  restarting: no scorer process alive, `ladder_150M/` empty, no partial files, and the 650M
  leg had not yet started. I then ran one model per call. Nothing was corrupted and no real
  directory was involved.
- AGENTS 6: re-implementing or re-running an estimator reproduces the code's behaviour; it is
  not independent evidence for any biological claim.

Verdict: **PASS (C1).** All cheap gates pass on the real outputs, script 172 reproduces the
night value-for-value, every rescored file is bit-exact against its reference, and the real
directories are provably untouched.
Files created/modified: `docs/tasks/phase4-strengthening/PHASE4B_C1_REALDIR_SNAPSHOT_BEFORE.txt`,
`..._AFTER.txt`, `PHASE4B_C1_SCRIPT165_OUTPUT.txt`, `PHASE4B_C1_SCRIPT166_OUTPUT.txt`,
`PHASE4B_C1_SCRIPT172_OUTPUT.txt`, `PHASE4B_C1_RESCORE_NEIGH.txt`,
`PHASE4B_C1_RESCORE_LADDER.txt` (all new, in the task folder);
`data/processed/phase4/c1_rescore_scratch/` (new scratch: 3 neighbour files + 3 ladder dirs).
Nothing protected, earlier, staged or frozen was edited. Nothing staged, committed or pushed.
Anything unexpected or worth flagging: the 150M/35M reference for the rescore is the A8c gate
run, not a night - see §3. Proceeding to C2.

---

## [C2] - Independent recomputation of every module - PASS with findings (39 of 40 gated numbers identical)

Status: PASS for the recomputation task; **five findings**, two of which are real
disagreements or unreconciled conventions that are reported rather than fixed, and three of
which are NOT-COMPUTABLE with the reason (one of them a gate I set and that failed).
Time started / finished: Sun Oct 4 17:27 EDT 2026 / Sun Oct 4 18:21 EDT 2026
What I did: wrote `scripts/176_phase4b_independent_recompute.py` and recomputed, from the raw
data files only, every headline number of modules S, M, U, G, N and L **without calling any
staged Phase-4 script** (not 166-175, not the driver) and **without importing
`scripts/lib/phase4_common.py`** - Spearman, the rank-partial, the position-cluster bootstrap,
AUROC and balanced precision are all re-implemented in that file from numpy/scipy. H is
derived from the RULE (frame positions in neither the F1 AE nor the F1 W frame), giving
455 positions / 7,526 rows from the raw inputs. Output:
`docs/tasks/phase4-strengthening/PHASE4B_C2_RECOMPUTE_OUTPUT.txt` (production run,
`N_BOOT=10000 SEED=0 N_STAB=2000`, 10m57s, exit 0).

**Headline: `comparisons gated: 40; identical: 39; DISAGREEMENTS: 1`.**

### 1. What reproduced exactly (selection; the full list is in the output file)

| module | quantity | mine | staged | diff |
|---|---|---|---|---|
| S | Spearman(delta, S_W) / Spearman(own_e.b, S_W) | -0.3238 / +0.0854 | same | 0.000e+00 |
| N | p_NB(neg) = (1+5)/47 | 0.1276595744680851 | same | **0.000e+00** |
| N | count of NB members at or below rho_A222V | 5 | 5 | exact |
| N | cell means C1 / C2 / C5 (n = 13/16/17) | -0.027997074 / -0.035856852 / -0.058179765 | -0.027997 / -0.035857 / -0.058180 | 7e-8 / 1e-7 / 2e-7 (6-dp targets) |
| N | contrast C2 - C4 | -0.036890449 | -0.036890 | 4.5e-7 (6 dp) |
| N | Amendment 3 partials (flexible) | +0.19229403 / -0.05375753 | +0.192294 / -0.053758 | 3e-8 / 5e-7 (6 dp) |
| N | pool P composition | 117 = 50 new + 67 nulls; cells C1 13, C2 16, C3 13, C4 51, C5 17, gap 7 | identical | exact |
| L | rho_A222V on H (650M) | -0.09002168303339808 | -0.090021683 | 3.3e-11 |
| L | p_spec_H(neg) = (1+3)/79 and p_spec_H(abs) | 0.050633 / 0.050633 | same | **0.000e+00** |
| L | beaters | AV_195, AV_220, G_P254F | same | exact |
| L | gradient Spearman(rho_b, d3), n = 67 | +0.713319 | +0.713319 | **0.000e+00** |
| L | shift confound Spearman(rho_b, mean abs delta), n = 96 | -0.612697 | -0.612697 | **0.000e+00** |
| M | rho_A222V full frame | **-0.08811806424891734** | -0.088118064 | 2.5e-10 |
| M | partial given S_W (full) | **-0.06414804421216103** | -0.064148044 | 2.1e-10 |
| M | partial given S_W (H) | -0.06720891007058159 | -0.067208910 | 7.1e-11 |
| M | p_spec(neg) full / H | 2/79 / 4/79, same beaters | same | exact |
| M | rho_between / rho_within | -0.177458126 / -0.028237316 | same | **0.000e+00** |
| M | **M-6 stability, 2,000 draws, full frame** | **P(p_spec<=0.05) = 0.5760**, k = 0:377, 1:467, 2:308, 3:202, 4:170 ... | 0.5760, k = 0:377, 1:467, 2:308 ... | **identical** |
| M | M-6 stability, H | 0.7795 (2,000 draws) | 0.7720 | 0.0075 = 0.8 SE of a 2,000-draw probability |
| U | Spearman(S_A,y) / Spearman(S_W,y) / Delta | 0.3650234295486086 / 0.3684212256227523 / **-0.0033977960741436997** | same to 16 dp | 5.6e-17 |
| N, L, U | frozen words | REGION-LIKE, NEITHER-RESOLVED, MODEL-REPLICATES, CONDITIONING-HURTS | identical | - |

CIs are reported **beside** the staged ones, never gated (C2-DEC2: my draw ids differ by
construction). Selected pairs: M-1 partial full, mine [-0.093, -0.036] (10,000 draws) vs staged
[-0.093576, -0.035309]; Amendment 3 d3 partial, mine [-0.025768, +0.380381] vs staged
[-0.018716, +0.379290]; U-1 Delta, mine [-0.004529104, -0.002339321] vs staged
[-0.004488253530713755, -0.0023350383831684295]. Every one of these excludes zero in the same
direction as its staged counterpart, and no CI I computed changes a word's side of a boundary.

### 2. FINDING 1 - the anchor rho is sensitive at 1e-8 to which delta column is used

The frozen G-M1/G-M2 targets are reproduced **exactly** by the frame's own `delta_esm` column
(-0.08811806424891734 and -0.06414804421216103). Computing the same delta as
`esm2_score_a222v_bg - esm2_score` - algebraically the same quantity, and what I used first -
gives -0.08811808948323244 instead, a difference of **2.5e-8**. Cause measured, not guessed:
the two columns differ by up to 2.2e-16 per value, and the frame carries **180 adjacent
`own_e.b` values within 1e-12**, so two ranks flip. On the H view the same mechanism acts
through the CSV float parser: pandas' default parser and `round_trip` differ by up to
3.55e-15 per delta, which flips **4 of 7,526 ranks** and moves rho_A222V by **8.8e-9**; the
default parse is bit-identical to the task32 columns, i.e. to the canonical cached
construction. Across all 78 null rho_b the parser moves rho by at most 1.4e-7 and changes
`p_spec_H(neg)`'s k by **0**. **No p-value, count, CI or word is affected at any level that
matters** - but the project's headline anchor is not reproducible to better than ~1e-8 without
saying which column and which parser were used. Disclosed as C2-DEC8 and printed in every run.

### 3. FINDING 2 - the two staged modules use OPPOSITE tails for the same "abs" p-value

- `scripts/172_neigh_analysis.py` line 475: `rank_abs = 1 + sum(1 for v in arm_s.rho_H if abs(v) > abs(rho_a_H))`
  -> `p_NB(abs) = (1+41)/47 = 0.8936170212765957`, which I reproduce **exactly**.
- `scripts/lib/phase3_common.py` `p_spec(..., mode="abs")` counts `abs(rho_b) >= abs(rho_T)`
  -> `p_spec_H(abs) = (1+3)/79 = 0.050633`, which I also reproduce **exactly**.

The NEIGHBOUR pre-registration says "p_NB(neg) = (1 + #{b in NB: rho_b <= rho_A222V}) / (1 + |NB|);
p_NB(abs) uses |rho|" - read literally, "uses |rho|" means the same formula with |rho|
substituted, i.e. the `<=` tail, which is what 172 does. The MECH/LADDER `>=` tail is the
opposite of that literal reading. **No frozen word uses either value** (the section-5 word uses
`p_NB(neg)`; the ladder word uses `p_spec_H(neg)`; M-1's word uses `p_spec(neg)`), so no
conclusion in this phase depends on the choice. Flagged for C4; deliberately NOT reconciled
here, and not tuned.

### 4. FINDING 3 - M-2's stratified rho: one unresolved disagreement (no word attached)

`stratified rho (full frame)`: mine **-0.059988177**, staged **-0.059956192**, difference
3.198e-05. My decile row counts are exactly the staged accounting ([1076 x7, 1075 x3] =
10,757) once I use an exact equal-count rank split rather than a percentile cut, and the
difference survives that fix. Most likely cause is the same near-tie mechanism as Finding 1
acting inside the deciles, but **I did not measure it and am not claiming it**. M-2 is a
registered sensitivity with **no word**; M-1, M-5 and M-6 are unaffected and reproduce exactly.
Per C2-DEC1 this stays a reported disagreement.

### 5. NOT-COMPUTABLE, with reasons (never estimated)

- **M-3 / M-4 (the zero-epistasis simulation null and the planting curve): the requested
  200-draw re-draw was NOT delivered, because my generator failed the identity gate I set for
  it.** I rebuilt `E_c^iso` (4 conditions x 5 folds, weights 1/m_se^2, folds = permutation of
  the sorted raw positions under `default_rng(0)`) from the raw table and fed it to the
  project's own `scripts/lib/own_context.wls_line` unmodified, as the frozen block requires.
  With **no noise at all** the result must reproduce the project's recorded
  `own_e_b_ge_iso`; it does not:
  `max|diff| = 4.544e-02 over 11,865 rows (gate < 1e-12)`. The remaining difference is the
  project's "second-pass valid mask", which is not recoverable from the saved tables. A null
  distribution from a generator that cannot reproduce the recorded `own_e.b` would be a number
  I cannot stand behind, so **no M-3 or M-4 number is reported by me**, and the staged values
  (mean +0.027069, band [+0.012014, +0.042006], word EXCESS-OVER-ARTIFACT; MDE |r0| 0.03994845)
  stand unverified by C2.
- **Module G (GB1 locality): G-1's lambda_model / lambda_data / d_b and G-2's strata means
  and paired difference are NOT-COMPUTABLE.** They need script 155's per-(background, partner)
  table of `abs(delta_b(v))`, `abs(e_b(v))` and separation s, which is built from the Olson
  doubles and is **not cached anywhere on disk**; rebuilding it is a transcription of 155, not
  an independent recomputation, and C2's rule is not to call staged code. What I could verify:
  the cached 400-background rho table's mean is **-0.009125049245666152**, which is the frozen
  G-D0 target -0.009125 exactly (0.000e+00).
- **Module L's 150M and 35M columns and both cross-model agreements**: the scores do not
  exist (night B never ran). Reported, not estimated.
- **U-2's AUROC / balanced-PR metrics**: the staged run used the Weile et al. supplement
  labels, and G-U2 FAILED, so U-2 is wordless; the fallback label file on disk is a different
  label set, so U-2 is NOT-COMPUTABLE from it.

### 6. Errors I found in MY OWN first pass, disclosed (C2-DEC10)

Five, none of them a tuned threshold: (1) the `abs` tail, initially `<=` in module L - my error,
the staged convention is `>=`; (2) the pool-P membership: I first used all 85 resolved
backgrounds instead of the 67 resolved **nulls**, which broke the cell means and both partials;
(3) I omitted Amendment 1's **new C5 cell** (d3<=12, 20<dseq<=40), which put 2 nulls in "gap"
and made pool P 107 instead of 117; (4) the two score files were parsed with different float
parsers, producing a third spurious rho value; (5) a shape bug in my `partial_spearman`
control handling. Each was found by a count or pool-size mismatch against the staged
accounting, fixed, and re-verified - not by nudging a number toward the staged one.

**POST-HOC DISCLOSURE (AGENTS 0, 6):** `C2-DEC9` was added after I saw rounded-target
mismatches at the 1e-7 level: where a staged value is only PRINTED to six decimals (cell means,
the Amendment 3 partials, the M-2 target), agreement is judged at 5e-7, half a unit of the last
printed digit, with the full-precision difference printed in the same line. Values the staged
scripts print in full precision keep the 1e-9 gate. It is recorded in the script's docstring,
in its startup banner and here. **Disclosure of my own basis error (C2-DEC11):** my first
Amendment 3 statistic used a hand-written numpy natural cubic basis and gave +0.214063 /
-0.048437 against the staged +0.192294 / -0.053758, because that basis is a *different column
space*, not a reparameterisation of the specified one. I replaced it with patsy's own `cr()` -
the function Amendment 3 names, and a third-party library, not project code - which reproduces
the staged values exactly. I did not tune the hand-written basis toward the answer.

### 7. Limitations, printed in the script's own output

Re-implementing estimators on cached data validates code against code; it is **not
independent evidence for any biological claim** (AGENTS 6). Bootstrap CIs are two independent
estimates and are not expected to match digit for digit. The M-3/M-4 generator is a
re-implementation that failed its identity gate, so nothing from it is reported. Module G's
statistics and U-2's metrics are NOT-COMPUTABLE here. The 200-draw simulation re-draw asked for
by this task **was not achieved**, and the M-4 planting curve at three grid points with it.

Verdict: **PASS (C2)** for what was computable - 39 of 40 gated numbers identical, including
every frozen word of modules N, L, S and U and the whole of M-1, M-5 and M-6 - with Findings
1-3 and five NOT-COMPUTABLE items reported rather than smoothed over.
Files created/modified: `scripts/176_phase4b_independent_recompute.py` (new),
`docs/tasks/phase4-strengthening/PHASE4B_C2_RECOMPUTE_OUTPUT.txt` (new), log entry appended.
Nothing protected, earlier, staged or frozen was edited; nothing staged, committed or pushed.
Anything unexpected or worth flagging: the `abs`-tail inconsistency between two staged modules
(Finding 2) is a real defect in the project's reporting conventions even though no word depends
on it - it goes to C4. Proceeding to C3.

---

## [C3] - Interpretation inside the frozen words - one plain two-sided statement per module

Status: DONE
Time started / finished: Sun Oct 4 18:24 EDT 2026 / Sun Oct 4 18:40 EDT 2026
What I did: read each module's frozen outcome word and stated, in both directions, what the
printed numbers do and do not support. No cross-module sentence appears below; no p_spec is
compared with anything but its own stated threshold; no result is described as confirming or
undermining another module's, or any GB1 / RBD / Phase 3 result. Rule 14's flags (INSIDE /
OUTSIDE / MARGINAL) are printed wherever a statistic is compared with a bound or a random-draw
range, and **no conclusion below is built on a MARGINAL flag**. The sign sentence is quoted
verbatim from `SIGN_CONVENTION.md` at every rho.

**THE SIGN SENTENCE (verbatim, quoted wherever a rho is discussed):**
> delta = S(v|A222V) - S(v|WT): positive delta means the model scores the substitution as MORE
> favourable in the A222V background than in the wild-type background. own_e_b = observed
> A222V-arm score minus the multiplicative no-interaction expectation, taken as its
> concentration-weighted intercept: positive own_e_b means observed BETTER than the
> expectation, negative own_e_b means observed WORSE than the expectation. A NEGATIVE rho means
> the model's background shift runs OPPOSITE to the measured shift: substitutions the model
> makes look better under A222V are, on average, the ones whose measured interaction residual
> is lower -- direction only; no magnitude, mechanism or causal claim follows from the sign.

### MODULE S - the sign convention (no outcome word; this module only fixes vocabulary)

Two-sided statement: the convention is fixed and stated once, with a computed worked example
(p.Asn118Pro: delta +0.0407 positive, own_e.b -0.7243 negative), and it is the same convention
the other modules read. The anchor correlation is **negative** (full frame -0.08811806424891734,
H view -0.09002168303339808), which under the sign sentence means the model's background shift
runs **opposite** the measured shift - never that it agrees with it. Its magnitude is small:
|rho| is under 0.1 in both views. For scale within this module only, Spearman(delta, S_W) =
-0.3238 and Spearman(own_e.b, S_W) = +0.0854, so delta carries most of its rank association
with S_W rather than with the measured residual. C2 reproduced all three of these numbers
exactly. **No RBD direction is described anywhere in this entry** (the RBD direction word is
unverified locally, per script 166's own printed limitation).

### MODULE M - mechanism-matched analyses

**M-1 = PARTIAL-SURVIVES.** Two-sided statement: controlling for S_W the negative association
shrinks but does not disappear - partial -0.06414804421216103, position-cluster CI
[-0.093576, -0.035309] excludes zero in the negative direction, retaining 0.727978 of the raw
anchor's magnitude; p_spec(neg) = 2/79 = 0.0253 on the full frame, which is **at or below** the
frozen 0.05 clause, and 4/79 = 0.0506 on H, which is **at or below** the frozen 0.10 clause. So
the word survives in the frozen sense on both views, and the honest counterweight is that the
retained fraction is about 73%: roughly a quarter of the raw association is attributable to the
S_W channel. The secondary two-covariate control gives -0.0829 (retained 0.940708) and carries
**no word** as registered. C2 reproduced the partial and both p_spec counts exactly.

**M-2 (registered sensitivity, no word).** Stratified -0.059988177 against a raw -0.088118064;
the stratification by S_W decile removes about a third of the magnitude. C2 could not reconcile
this figure with the staged -0.059956192 (3.198e-05 apart, C2 Finding 3) and the difference is
reported, not resolved. **No word attaches, so nothing turns on it.**

**M-3 = EXCESS-OVER-ARTIFACT** (staged word; **C2 could not verify it** - see below). Two-sided
statement, with its assumptions stated as required: under a zero-epistasis world run through
the project's own pipeline, the anchor's magnitude sits **below** the null's 2.5th percentile,
so the observed association is not what that world produces on its own. The assumptions this
rests on are: (i) **sw_i = 0** - the data carries no per-variant WT-background standard error,
so the WT side of the simulation is treated as noise-free, which is an assumption and not a
measurement; (ii) the null's only structure is a monotone nonlinear relation - a cross-fitted
isotonic expectation of WT fitness - plus the recorded measurement noise, with no
background-specific epistasis by construction; (iii) **the null does not centre on zero**
(mean +0.027069, SD 0.007896), so the result is the *excess over the null*, and the raw
statistic is not itself the claim; a positively-offset null means the raw -0.088 is not by
itself evidence of anything. The two sensitivities (linear generating relation; median m_se as
sw) are reported with numbers and carry no word. **C2's independent 200-draw re-draw of this
null was NOT delivered: my rebuilt generator failed its identity gate at max|diff| = 4.544e-02
against the project's recorded own_e.b, so this word stands on the staged run alone.**

**M-4 (no word).** Minimum detectable |r0| at 80% power 0.03994845 either side of zero,
attenuation slope +0.832651: a planted true correlation would have to be about 0.04 before this
design sees it half the time. **C2 could not verify the planting curve.**

**M-5 = WITHIN-CARRIED — and the two components tell different stories, so both are stated.**
Full frame: **rho_within = -0.028237316**, CI [-0.049826, -0.006662] excludes zero in the
negative direction, p_spec(neg) 2/79 = 0.0253, **at or below** the 0.05 clause. **rho_between =
-0.177458126**, CI [-0.235913, -0.119746] also excludes zero, but its p_spec(neg) is 4/79 =
0.0506, which is **above** the 0.05 clause by 0.000633 - a distance of 0.0006 to the bound, so
under rule 14 this p_spec is **MARGINAL**, and no conclusion is built on that flag. The
counterweight, stated plainly because it matters: **the between-position component is about 6.3
times larger in magnitude than the within-position component** (-0.177 vs -0.028). The word
WITHIN-CARRIED therefore reflects which component clears *both* frozen clauses, not which is
bigger. Surrogate retention: S1 (own_e.b permuted within each position) mean -0.067354, 95%
range [-0.076189, -0.058614], which is **+0.7644 of -0.088118**; S2 (within 3D-distance bins)
mean -0.040113, range [-0.057561, -0.022281], **+0.4552 of -0.088118**. Read with the sign
sentence: both surrogates retain a large share of the anchor's magnitude, and neither centres
on zero. C2 reproduced both components exactly (0.000e+00).

**M-6 = MODERATE (both views).** The frozen placebo test clears its own threshold in only part
of the position resamples: **P(p_spec <= 0.05) = 0.5760 on the full frame** and
**P(p_spec <= 0.10) = 0.7795 on H** in C2's independent 2,000-draw whole-placebo (staged:
0.5760 and 0.7720 - the full-frame figure and its whole k-distribution are identical to mine;
the H figure differs by 0.0075, which is 0.8 standard errors of a 2,000-draw probability). Both
sit **above the 0.50 fragility bound and below the 0.80 stability bound**, which is what MODERATE
means, and both are 0.076 / 0.021 away from a boundary respectively - the H figure is
**MARGINAL** against the 0.80 bound under rule 14 and no conclusion is built on it. The frozen z
is printed as illustrative scale context only and is not a claim.

### MODULE U - predictive utility

**U-1 = CONDITIONING-HURTS - and the equivalence margin says something different, so both are
stated.** Delta = Spearman(S_A, y) - Spearman(S_W, y) = **-0.003397796074143755**, paired
position-cluster CI [-0.004488253530713755, -0.0023350383831684295] (C2's independent 10,000-draw
CI: [-0.004529104, -0.002339321]) lies **entirely below zero**, which is the frozen HURTS
criterion, and it is below zero in every one of the 10,000 draws. **The same interval lies
entirely inside the block's own (-0.02, +0.02) equivalence margin**, which is the frozen
EQUIVALENT criterion. Both facts are printed here and neither is suppressed: the word is HURTS
because that is the criterion the block applies first, and a reader who applies the margin
instead would say the two scores are practically indistinguishable. Magnitude, beside the
significance: the components are rho(S_A, y) = 0.36502342954860856 and rho(S_W, y) =
0.3684212256227523, so conditioning costs about 0.9% of the wild-type-background correlation -
small. The frozen word is reported on a difference that is statistically clean and practically
tiny, and that is the honest summary.

**U-2 = UNVERIFIED-LABELS, no word.** The gate that would have licensed a word failed, so the
word slot is empty; the metrics are still printed as numbers (S_W AUROC 0.823165 / balanced-PR
0.777803; S_A AUROC 0.816976 / balanced-PR 0.765473; Delta AUROC -0.006189213085764811 with a
paired CI [-0.021462658497809133, 0.0043300449550450135] that spans zero). **No claim of any
kind is made here about clinical usefulness, diagnostic value, or what these numbers imply for
patients.** Statements in this module concern ESM-2 scores in this one gene. C2 could not
recompute U-2's metrics because the staged run used the supplement's label set and G-U2 failed.

### MODULE G - GB1 locality (this module characterises GB1 only)

**G-1: MODEL-DECAYS fires; DATA-DECAYS does not fire; LOCALITY-DIFFERS fires.** Two-sided
statement: the model's |delta| decays with sequence separation from the background
(mean lambda_model -0.271233756, background-bootstrap CI [-0.284302974, -0.257821930] lying
entirely below zero, 96.5% of backgrounds negative), the measured |e_b| does **not** decay in
that sense (mean +0.036680324, CI [+0.025947267, +0.047664307] lying entirely **above** zero,
37.75% negative), and the difference between them is large and its CI excludes zero (mean d_b
-0.307914080, CI [-0.323182052, -0.292525237]). Counterweight: these are rank correlations of
magnitudes with separation in one dataset, and the data-side trend is not merely absent but
slightly positive. **G-2 = SEPARATION-MATTERS**: the paired near-minus-far difference is
-0.022238860 with CI [-0.043104841, -0.001032463] excluding zero over the 399 backgrounds with
both strata - and the honest counterweight is that the individual strata are small and mostly
unresolved: near -0.022121012 (CI excludes zero), mid -0.010881286 (CI spans zero), far
+0.000268630 (CI spans zero). The claim rests on the paired difference, which is what the
pre-registration froze. **G-3 was SKIPPED** by its registered fallback (1PGA chain A's C-alpha
sequence differs from the assayed 56-mer at position 2, so no numbering could be verified and
none was guessed). C2 could **not** independently recompute G-1's or G-2's statistics (the
partner table is not cached and rebuilding it would be a transcription, not a recomputation);
it did verify the cached 400-background mean rho_b = -0.009125049245666152 against the frozen
G-D0 target -0.009125 exactly. Per rule 13 and the frozen block, no sentence here reads for or
against any MTHFR or RBD result, and **no RBD direction is described**.

### MODULE N - neighbour arm (the out-of-sample test)

**Section 5 = REGION-LIKE.** Two-sided statement: A222V's correlation is **not** extreme relative
to backgrounds sampled from its own neighbourhood - p_NB(neg) = 6/47 = 0.1276595744680851, which
is **above** the frozen 0.10 boundary by 0.0277, i.e. **OUTSIDE** (not marginal) - with |NB| =
46, above the frozen 30-member floor. Under the sign sentence the anchor rho is negative, so what
is being compared is the *magnitude and direction* of a negative association: the negative
association at residue 222 is typical of the region around it, not peculiar to it. Two
counterweights, both stated: (i) the position-collapsed sensitivity gives **0.097561**, which
falls **inside** the UNRESOLVED band (0.05 < p <= 0.10), 0.0024 below the 0.10 bound - outside
MARGINAL by 0.0004 and therefore, per rule 14, not a MARGINAL flag, but close enough that the
sensitivity and the primary word do not agree; (ii) the five NB members at or below the anchor
are N_252_IL, N_191_DR, AV_220, N_195_AT, AV_195 - i.e. the set that does beat it is not empty.
**Section 6 = NEITHER-RESOLVED**, and the Amendment 3 planted confusion matrix is printed beside
it as required:
```
planted confusion matrix this word must be read against (seeds 0..99, real pool-P geometry):
  if the truth were 3D-only,     the word would be BOTH-LOCAL (or worse) 0.030 of the time
  if the truth were sequence-only, the word would be 3D-LOCAL (or worse) 0.010 of the time
  with no signal at all,          any word at all            0.070 of the time
measured: d3 partial  +0.192294 CI [-0.018716, +0.379290]  (includes zero)
          dseq partial -0.053758 CI [-0.276061, +0.167518]  (includes zero)
```
Two-sided statement of section 6: neither distance channel is separable from the other here -
both intervals include zero, so the data do not attribute the locality gradient to 3D distance,
to sequence distance, or to both. Counterweight worth stating because it cuts the other way: the
**superseded linear** control would have produced 3D-LOCAL (+0.341487, CI [+0.158986,
+0.502389]), so the choice of control flexibility, frozen in Amendment 3 before these scores
existed, is what makes this word NEITHER-RESOLVED rather than 3D-LOCAL; that is disclosed, not
hidden. Cell means move monotonically with 3D proximity (C5 -0.0582, C2 -0.0359, C1 -0.0280,
C3 -0.0170, C4 +0.0006) while the C2-minus-C4 contrast's CI excludes zero
([-0.056108, -0.017307]) and the C3-minus-C4 one does not. **No conclusion is built on any
MARGINAL flag in this module.**

### MODULE L - model ladder

**650M = MODEL-REPLICATES.** Two-sided statement: with the wild-type-background score partialled
out, the partial stays negative with its CI entirely below zero ([-0.099734, -0.033553]) and
p_spec_H(neg) = 4/79 = 0.050633, **at or below** the frozen 0.10 threshold - so on this model the
association is not an artefact of the WT-background score. Counterweight: the partial is smaller
than the raw (-0.0672 against -0.0900, about 75% retained), and this is one model. **The 150M
and 35M words DO NOT EXIST** - night B never ran, so those columns and both cross-model
agreements are pending, not negative. No word of any kind is issued for them.

### Cross-module discipline, stated for the record

No sentence above compares two modules, and no module's result is described as confirming or
undermining another's. The three pending items (L's 150M and 35M words, and the cross-model
agreements) are the only frozen words in this phase that no data exists for; the full-frame
neighbour-arm secondary (which the frozen block gives **no word**) is likewise unrun.

Verdict: **DONE (C3).** Every frozen word is interpreted inside its own criterion, each with a
plain two-sided statement, with the effect sizes and the counterweights beside it, and with
MARGINAL flags flagged and not leaned on.
Files created/modified: log entry appended only.
Proceeding to C4.

---

## [C4] - Corrections, append-only - 2 corrections and 1 clarification, no staged file edited

Status: DONE
Time started / finished: Sun Oct 4 18:42 EDT 2026 / Sun Oct 4 18:50 EDT 2026
What I did: compared the sentences the staged outputs print against the tables and the files
those sentences describe, and recorded every mismatch **here, append-only**. Per rule 10 and
AGENTS 7 no staged script, no staged output file, no earlier log and no frozen block was
edited; these corrections live only in this log.

### CORRECTION 1 - script 174 misstates where 97 of its 650M backgrounds come from

The sentence printed by `scripts/174_ladder_analysis.py` (line 49 of
`PHASE4B_C0_LADDER_ANALYSIS_OUTPUT.txt`, also in the A8d output):
> `[PASS] LD-AN5 650M column available: 97 backgrounds from the Phase 2 caches + the cached WT arm`

**What is actually on disk:** `data/processed/phase2/` holds **96** `bg_*.csv` files, and
**A222V is not one of them**. The 97th background's rows come from a different file,
`data/processed/esm2_a222v_bg_scores.csv` (the script's own `A222V_650` constant, line 178).
**So: the number 97 is correct, the code is correct, and the sentence is wrong about the
provenance of one member.** This also explains C0's otherwise puzzling set-equality result -
`ladder/650M/` contains 0 files while the column has 97 members, because that directory is
never written to by design.

*Correction as it should read:* "97 backgrounds: 96 from the Phase 2 caches plus A222V from
`data/processed/esm2_a222v_bg_scores.csv`, and the cached WT arm; 7,526 H rows, own position
excluded per background." **Effect on any number or word: none.** C2 independently built the
same 97-member column (96 file-derived deltas + the A222V arm) and reproduced the ladder's
rho, p_spec, gradient and confound exactly.

### CORRECTION 2 - the "abs" p-value uses OPPOSITE tails in two staged modules, and neither label says so

- `scripts/172_neigh_analysis.py` line 475 computes `p_NB(abs)` with the tail
  `abs(rho_b) > abs(rho_A222V)`, giving **(1+41)/47 = 0.8936170212765957** (C2 reproduces this
  exactly).
- `scripts/lib/phase3_common.py`'s `p_spec(..., mode="abs")` counts `abs(rho_b) >= abs(rho_T)`,
  giving `p_spec_H(abs) = (1+3)/79 = 0.050633` in script 174's column and in script 167's
  (C2 reproduces this exactly too).

Both printed values are internally correct, but the two quantities carry the same name and are
**not the same statistic**: a reader comparing module N's 0.8936 with module L's 0.0506 as "the
same p-value" would be wrong, and neither printout states which tail it used. The
NEIGHBOUR_ARM pre-registration line reads "p_NB(neg) = (1 + #{b in NB: rho_b <= rho_A222V}) /
(1 + |NB|); p_NB(abs) uses |rho|" - read literally that is the `<=` tail, i.e. what 172 does.

*Correction:* both printouts should state the tail explicitly, e.g. `p_NB(abs) = 0.8936
(|rho_b| <= |rho_A222V|)` and `p_spec_H(abs) = 0.0506 (|rho_b| >= |rho_A222V|)`. **Effect on any
word: none** - the section-5 word uses `p_NB(neg)`, the ladder word uses `p_spec_H(neg)`, and
M-1's word uses `p_spec(neg)`; no frozen word reads either "abs" value. Recorded rather than
reconciled, because choosing one convention project-wide would be a post-hoc decision about a
frozen quantity (AGENTS 0/3).

### CLARIFICATION 3 - not an error, but the next write-up must say which delta column it quotes

The anchor is reproducible only to about 1e-8 unless the delta column is named. C2's numbers:
full-frame rho = **-0.08811806424891734** from the frame's own `delta_esm` column (this is the
frozen G-M1 target) and **-0.08811808948323244** from recomputing the same quantity as
`esm2_score_a222v_bg - esm2_score` on the same rows - a 2.5e-8 difference caused by two rank
flips among the frame's 180 `own_e.b` values that lie within 1e-12 of their neighbour. On the H
view the same mechanism acts through the CSV float parser (4 of 7,526 ranks, 8.8e-9), which is
the effect rule 19 was written about. Every staged number is correct for the column it used;
the recommendation is only that a write-up state the column. **No correction to any staged
output is required.**

### Checked and found consistent (no correction needed)

- The neighbour arm's position-collapsed sensitivity: staged "position-collapsed NB = 40
  positions, p_NB(neg) = 0.097561 (6 second_at_position merges)"; C2 recomputed 40 distinct
  positions, k = 3, p = 4/41 = **0.0975609756** - the same value.
- Pool accounting: staged "50 new + 67 existing, cells C1 13, C2 16, C5 17, C3 13, C4 51" against
  C2's independent count of **117 = 50 + 67** with exactly those cell counts, and the existing
  nulls' own cells {C1 1, C2 3, C3 3, C4 51, C5 2, gap 7} reproduced exactly.
- The ladder's "over 96 backgrounds" confound and "over 67 resolved nulls" gradient: C2 counted
  n = 96 and n = 67 from the files.
- M-5's "qualifying positions 652/654": C2 counted 652.

Verdict: **DONE (C4).** Two real corrections, both about sentences rather than numbers, and
one clarification; no staged output, script, log or frozen block was modified, and no word in
this phase changes.
Proceeding to C5.

---

## [C5] - Reproduction package - built, PASSES on the working tree, FAILS from a fresh clone (both recorded)

Status: DONE (package complete). The fresh-clone test **failed**, for two reasons that are
outside the package's control, and both are recorded rather than worked around.
Time started / finished: Sun Oct 4 18:52 EDT 2026 / Sun Oct 4 20:05 EDT 2026 (inside the
90-minute box)
What I did: pinned the environment; regenerated the data manifest; wrote the package; ran it
here; ran it in a fresh clone under `/tmp` with the data restored from Arnav's archive.

### 1. Arnav's data archive - confirmed present, and incomplete for this purpose

```
-rw-r--r--  30126816 Oct  2 15:28 /Users/arnavchavan/Desktop/mthfr_data_backup.tgz
sha256 225106698afa8bd82a6ac080a2ecb82f3856186e70fc1658a79ff5afe9c42d50
702 entries; top-level content: data/processed/phase2/ (102), data/processed/phase2_diagnostics/ (3),
data/processed/phase3/ (12 + gb1 408 + rbd 108 + other scratch dirs)
  data/external entries: 0        phase4 entries: 0
```
Exactly as the task states: **the Phase 4 outputs and the `data/external` downloads are NOT in
it and must be added.** Checking all 19 inputs the headline numbers need:
```
  12 of 19 required inputs are ABSENT from ~/Desktop/mthfr_data_backup.tgz
present: task32_analysis_table.csv, phase2_diagnostics/{background_3d_distance,background_rho_table}.csv,
         phase2/ (96 bg files), phase3/m1_own_e_b_ge.csv, phase3/m1_fitted_expectations.csv, phase3/gb1/
absent:  esm2_wt_scores.csv, esm2_a222v_bg_scores.csv, task82_ae_raw.csv, task69_w2_bg_raw.csv,
         data/raw/mthfrModel/results/folate_response_model5.csv, data/raw/6FCX.pdb,
         phase4/neigh/roster_v1.csv, phase4/neigh/ (50 score files), phase4/neigh/manifest.csv,
         data/external/mavedb/, data/external/weile2021_supp/, data/external/rcsb/1PGA.pdb
```
The two worst absences are `task82_ae_raw.csv` and `task69_w2_bg_raw.csv`: those two files are
what **define the held-out frame H**, so without them *every* module stops before computing
anything.

### 2. The package

- `reproduce/requirements.lock` - `pip freeze` of `venv`, **92 packages**. Environment as run:
  Python **3.14.3**, macOS-26.5.1-arm64, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, sklearn 1.9.1,
  patsy 1.0.3.
- `data/processed/DATA_SHA256_MANIFEST.txt` - **regenerated**, 1,955 files with sha256 and size
  (260 KB), covering `data/processed/` and `data/external/`.
- `reproduce/required_inputs.tsv` - the 19 inputs and what each is for.
- `reproduce/headline_expectations.tsv` - 27 expected headline values, each with **where it is
  recorded** (which log, which entry).
- `reproduce/rebuild_headlines.sh` - steps: environment -> inputs -> independent recompute ->
  modules N and L -> module S -> (M, U, G off by default). Every value is extracted with a
  `sed` capture group and compared to the expectation; **the script never edits an expectation**,
  and says so at the failure branch (AGENTS 0). `--quick` reduces draws; `--only=` selects steps.
- `reproduce/REPRODUCE.md` - how to run it, what it checks, and the two test results below.

### 3. Test on the working tree - RESULT: PASS

`bash reproduce/rebuild_headlines.sh --quick --only=inputs,indep,S,N,L`:
```
  [ok] 19/19 required inputs present
  [PASS] venv/bin/python3 present: 3.14.3 ; pip freeze matches requirements.lock exactly
  [PASS] independent recompute: 1 disagreement, all of it the ONE documented exception
         (M-2 stratified rho, 3.198e-05, unresolved; [C2] Finding 3)
  [PASS] N / rho_A222V on H = -0.090021683      [PASS] N / p_NB(neg) = 0.127660
  [PASS] N / count at or below = 5              [PASS] N / section-5 word = REGION-LIKE
  [PASS] N / d3 flexible partial = +0.192294    [PASS] N / dseq flexible partial = -0.053758
  [PASS] N / section-6 word = NEITHER-RESOLVED  [PASS] N / cell mean C2 = -0.035857
  [PASS] L / 650M rho_A222V on H = -0.090021683 [PASS] L / 650M p_spec_H(neg) = 0.050633
  [PASS] L / 650M gradient = +0.713319           [PASS] L / 650M confound = -0.612697
  [PASS] L / 650M word = MODEL-REPLICATES        [PASS] S / checks PASS = 49
  checks failed: 0
RESULT: PASS -- every requested check reproduced its logged value.
```

### 4. Test in a fresh clone under /tmp - RESULT: FAIL, for two reasons, both recorded

```
STEP 1  git clone . /tmp/phase4_repro_test        clone HEAD: 24fe0e9
        scripts 1[6-7]* present: 7 of 12 (the seven are the OLDER 16/160-164 scripts)
        reproduce/ present: NO
STEP 2  tar -xzf ~/Desktop/mthfr_data_backup.tgz  -> 691 files restored
STEP 3  bash reproduce/rebuild_headlines.sh
        -> reproduce/rebuild_headlines.sh DOES NOT EXIST in the clone
```

**Reason 1 - the commit does not contain the code.** `git show --stat HEAD` on `24fe0e9`
("Phase 4: staged scripts, amendments, build log and cached-module results
(READY-TO-LAUNCH)", Arnav, 2026-10-04 02:54) lists **23 files, all of them
`PHASE4_A*_OUTPUT.txt` run logs** - 5,245 insertions and nothing else. Not one of
`scripts/165`..`scripts/175`, not the amendments, not `PHASE4A_BUILD_LOG.md`, not
`STATE_FOR_LAUNCH.md`. This is the exact failure AGENTS 5 and AGENTS 7 name ("commit messages
claiming files that were never staged"), and it is reported here as a finding, not as a
Phase-4 result. I did not amend, revert or re-commit anything (rule 11).

**Reason 2 - the data are incomplete.** With the uncommitted working tree overlaid by `rsync`
and `venv` symlinked in place of `pip install -r requirements.lock` (both substitutions
disclosed in `REPRODUCE.md`), the script ran and reported `[MISS]` on **12 of 19** inputs,
then every module stopped at the first missing file:
```
  MODULE S/N/L/M/U STOPPED: FileNotFoundError: data/processed/task82_ae_raw.csv
  MODULE G STOPPED: the partner table cannot be rebuilt independently
  scripts/172 exit 1 ; scripts/174 exit 1 ; scripts/166 exit 1
  every headline pattern "not found in the output"
```
So from a fresh clone plus the archive, **no Phase-4 headline number can be rebuilt**, and the
package says exactly which files would fix that (`REPRODUCE.md`, final section).

### 5. Honest summary of what C5 delivered and did not

Delivered: a pinned environment, a 1,955-file data manifest, an input inventory, a 27-value
expectation table with provenance, a rebuild script with a PASS/FAIL table, a README, and a
working-tree run that **passes every check**. Not delivered: a reproduction from a fresh clone,
for the two external reasons above - the archive lacks 12 inputs (including the two files that
define H), and commit `24fe0e9` does not contain the scripts the message claims. Both are
Arnav's to fix (extend the archive; commit the staged files).

Verdict: **DONE (C5), with the fresh-clone test recorded as FAIL and its two causes named.**
Files created/modified: `reproduce/{REPRODUCE.md,requirements.lock,required_inputs.tsv,
headline_expectations.tsv,rebuild_headlines.sh}`, `reproduce/runs/*` (run logs),
`data/processed/DATA_SHA256_MANIFEST.txt` (regenerated), `/tmp/phase4_repro_test` (throwaway
test tree, outside the repo). Nothing protected, earlier, staged or frozen was edited; nothing
staged, committed or pushed; the driver was not launched.
Proceeding to the S-B SUMMARY for session 4b.

---

# S-B SUMMARY - session 4b (C0..C5), Sun Oct 4 2026

## 1. READ FIRST - which stages completed, were skipped, or failed

| item | outcome |
|---|---|
| **Night A (plan A: SA1 scoring, SA2 analysis, SA3 integrity)** | **COMPLETED**, 2026-10-04 03:44:57 -> 08:22:39 EDT. SA1 262.2 min (budget 330; the A7d projection was 304, so 14% faster), SA2 15.5 of 23, SA3 instant. All three exit 0, attempt 1, guards passed with real readings before each stage. **277.7 of 363 budgeted minutes.** 50 neighbour backgrounds scored; all 50 files match their manifest sha256; the three A7d smoke files are byte-identical to the night's. |
| **Night B (SB1 150M, SB2 35M scoring)** | **NEVER LAUNCHED.** No `driver_state_phase4B.json`, no log, no `ladder/150M/` or `ladder/35M/` directory. |
| **Night C (SB3 ladder analysis, SB4/SB5 nonH frame)** | **NEVER LAUNCHED.** No state file, no log, no `neigh_nonH/`. Its SB3 stage was run by me on the CPU instead, per C0's instruction. |
| C0 state and integrity | PASS (with the two unrun nights reported as the finding) |
| C1 re-gate on the real outputs | PASS - 165: 70/70 `GATE PASS`; 166: 49 checks; 172: 33 PASS / 0 FAIL / 0 PENDING, reproducing the night value-for-value; every rescored file bit-exact; real directories provably untouched |
| C2 independent recomputation | PASS with findings - **39 of 40 gated numbers identical**; 1 disagreement (M-2, no word); 5 items NOT-COMPUTABLE |
| C3 interpretation | DONE |
| C4 corrections | DONE - 2 corrections, 1 clarification, append-only |
| C5 reproduction package | DONE - working tree **PASS**; fresh clone **FAIL** (archive missing 12 inputs; commit `24fe0e9` lacks the scripts) |
| Timed out | nothing |
| Failed gates | one, and it was mine: C2's identity gate for the M-3/M-4 simulation generator (`max|diff| = 4.544e-02`, gate 1e-12), which is why that re-draw is NOT-COMPUTABLE |

**Two frozen words do not exist and cannot be produced without night B: module L's 150M and
35M words, plus both cross-model agreements.** The neighbour arm's full-frame secondary also
remains unrun, and the frozen block gives it **no word**.

## 2. MODULE S - the sign note (no outcome word)

The convention is fixed in `SIGN_CONVENTION.md` with a computed worked example
(p.Asn118Pro: delta +0.0407, own_e.b -0.7243). Anchor numbers: **10,757 rows / 654 positions**,
**rho(delta, own_e.b) = -0.08811806424891734** (full), **-0.09002168303339808** (H),
**rho(delta, S_W) = -0.32376573717755663**, **rho(own_e.b, S_W) = +0.085391652432165**.
C2 reproduced the two rounded values exactly (0.000e+00). A negative rho means the model's shift
runs **opposite** the measured shift - direction only. No RBD direction is stated anywhere.

## 3. MODULE M - every frozen word and number

- **M-1 = PARTIAL-SURVIVES.** partial | S_W **-0.06414804421216103**, CI [-0.093576, -0.035309],
  retained **0.727978**; p_spec(neg) **2/79 = 0.0253** (full, at or below 0.05), **4/79 = 0.0506**
  (H, at or below 0.10); H partial -0.067208910 CI [-0.099734, -0.033553]; secondary
  two-covariate -0.0829, retained 0.940708, **no word**; p_spec(abs) 0.189873; p_spec_adj
  0.037975 (2/78).
- **M-2 (no word).** stratified **-0.059988177** by C2 vs **-0.059956192** staged (3.198e-05
  apart, unresolved); H -0.064660110.
- **M-3 = EXCESS-OVER-ARTIFACT** (staged only; **C2 could not verify**). 1,000 draws, mean
  **+0.027069**, SD 0.007896, band [+0.012014, +0.042006], fraction at or below -0.088118 =
  **0.0000**. The null does **not** centre on zero. Assumptions: sw_i = 0 (no per-variant WT SE
  exists), a cross-fitted isotonic monotone relation as the only structure, and the excess over
  the null - not the raw statistic - is the claim.
- **M-4 (no word).** MDE |r0| at 80% power **0.03994845**; attenuation slope +0.832651.
- **M-5 = WITHIN-CARRIED.** within **-0.028237316**, CI [-0.049826, -0.006662], p_spec(neg)
  2/79 = 0.0253; between **-0.177458126**, CI [-0.235913, -0.119746], p_spec(neg) 4/79 = 0.0506 -
  **above** 0.05 by 0.000633 (MARGINAL under rule 14, not leaned on). **The between component is
  ~6.3x larger in magnitude than the within one**; the word follows which component clears *both*
  clauses. Surrogate retention: S1 +0.7644, S2 +0.4552 of -0.088118; H view within -0.035545269,
  between -0.169522069; qualifying positions 652/654.
- **M-6 = MODERATE (both views).** **P(p_spec<=0.05) = 0.5760** full, **0.7795** H by C2's
  independent 2,000-draw whole-placebo (staged 0.5760 / 0.7720; the full-frame figure and its
  entire k-distribution are identical to mine). Both above 0.50, below 0.80; the H figure is
  MARGINAL against 0.80 and no conclusion rests on it. Frozen z: illustrative only.

## 4. MODULE U

- **U-1 = CONDITIONING-HURTS.** **Delta = -0.003397796074143755**, CI
  [-0.004488253530713755, -0.0023350383831684295] (C2's independent 10,000-draw CI:
  [-0.004529104, -0.002339321]) **entirely below zero in all 10,000 draws** - **and entirely
  inside the block's own (-0.02, +0.02) equivalence margin**, so the same interval also meets the
  EQUIVALENT criterion. Both are stated; the word is HURTS because that is the first criterion
  the block applies. Components: rho(S_A,y) = 0.36502342954860856, rho(S_W,y) = 0.3684212256227523,
  so the cost is ~0.9% of the WT-background correlation - small.
- **U-2 = UNVERIFIED-LABELS, no word** (G-U2 failed). Metrics as numbers only: S_W AUROC
  0.823165 / balPR 0.777803, S_A 0.816976 / 0.765473, Delta AUROC **-0.006189213085764811**, CI
  [-0.021462658497809133, 0.0043300449550450135] spanning zero. **No claim of clinical usefulness,
  diagnostic value, or patient implication is made or implied.**

## 5. MODULE G

- **G-1: MODEL-DECAYS fires** (mean lambda_model **-0.271233756**, CI [-0.284302974, -0.257821930],
  96.5% negative); **DATA-DECAYS does not fire** (**+0.036680324**, CI [+0.025947267, +0.047664307]
  entirely *above* zero, 37.75% negative); **LOCALITY-DIFFERS fires** (mean d_b **-0.307914080**,
  CI [-0.323182052, -0.292525237]).
- **G-2 = SEPARATION-MATTERS.** paired near - far **-0.022238860**, CI [-0.043104841,
  -0.001032463] over 399 backgrounds; near -0.022121012 (CI excludes zero), mid -0.010881286
  (spans zero), far +0.000268630 (spans zero).
- **G-3 SKIPPED** by its registered fallback (1PGA chain A differs from the assayed 56-mer at
  position 2; no numbering guessed).
- C2 verified the frozen G-D0 mean rho_b **-0.009125049245666152** exactly, but could **not**
  recompute G-1's or G-2's statistics (script 155's partner table is not cached).

## 6. MODULE N - position versus region, distance separation, cells

- **Section 5 word = REGION-LIKE.** p_NB(neg) = (1+5)/47 = **0.1276595744680851**, **above** the
  0.10 boundary by 0.0277 (**OUTSIDE**, not marginal); |NB| = 46, above the 30-member floor.
  Position-collapsed sensitivity **0.097561** (40 positions), which falls **inside** the
  UNRESOLVED band, 0.0024 below the boundary - outside MARGINAL by 0.0004, and stated because it
  does not agree with the primary word. The five members at or below the anchor: N_252_IL,
  N_191_DR, AV_220, N_195_AT, AV_195.
- **Section 6 word = NEITHER-RESOLVED**, with the Amendment 3 planted confusion matrix printed
  beside it: truth 3D-only -> BOTH-LOCAL or worse **0.030**; sequence-only -> 3D-LOCAL or worse
  **0.010**; no signal -> any word **0.070**. Measured: d3 partial **+0.192294** CI [-0.018716,
  +0.379290]; dseq partial **-0.053758** CI [-0.276061, +0.167518] - both include zero. The
  superseded linear control would have said 3D-LOCAL (+0.341487 CI [+0.158986, +0.502389]); that
  the word depends on the control's flexibility, frozen in Amendment 3 before these scores
  existed, is disclosed rather than hidden.
- **Cell table** (pool P = 117 = 50 new + 67 resolved nulls; cells C1 13, C2 16, C3 13, C4 51,
  C5 17, gap 7): C1 **-0.027997**, C2 **-0.035857**, C5 **-0.058180**, C3 -0.017, C4 +0.001;
  **C2 - C4 = -0.036890**, CI [-0.056108, -0.017307] excludes zero; C3 - C4 CI includes zero.

## 7. MODULE L - per-model words and cross-model agreement

- **650M = MODEL-REPLICATES.** rho_A222V on H **-0.09002168303339808**; partial | S_W
  **-0.06720891007058159**, CI [-0.099734, -0.033553]; p_spec_H(neg) **4/79 = 0.050633** (at or
  below 0.10); gradient Spearman(rho_b, d3) over 67 resolved nulls **+0.713319**, CI [+0.566655,
  +0.808932]; shift confound over 96 backgrounds **-0.612697**, CI [-0.732776, -0.456234].
- **150M: NO WORD - night B never ran. 35M: NO WORD - night B never ran.**
- **Cross-model agreement 650M vs 150M: NOT-COMPUTABLE. 650M vs 35M: NOT-COMPUTABLE.** Both
  require a second model column, which does not exist. No value is estimated for them.

## 8. Every gate run this session

| gate | result |
|---|---|
| night's own SA3 integrity pass | `RESULT: PASS (31 findings)`, 24 `sha256: MATCH` (its `SA3=running` line is self-referential and harmless) |
| script 165 (A2 library gates) | **70/70 PASS, 0 FAIL, `GATE PASS`** |
| script 166 (sign convention) | **49 checks PASS, 0 FAIL** |
| script 172 re-run on the night's outputs | **33 PASS / 0 FAIL / 0 PENDING**, identical values |
| script 174 re-run by me (C0's instruction) | **26 PASS / 0 FAIL / 4 PENDING**; 650M column reproduces A8d digit-for-digit |
| manifest sha256 vs disk (50 files) | **50/50 match** |
| C1 rescoring vs references (3 neighbour + 2 per ladder model + 3 WT arms) | **0.000e+00 on every comparison**; byte-identical where a reference existed |
| real-output before/after snapshots | **identical in every line**, incl. both listing hashes |
| C2's 40 gated comparisons | **39 identical, 1 disagreement (M-2, no word), 0 threshold loosened** |
| C2's M-3/M-4 identity gate | **FAILED (4.544e-02 vs 1e-12)** -> both reported NOT-COMPUTABLE, no number invented |
| rebuild_headlines.sh, working tree | **RESULT: PASS, 0 checks failed** |
| rebuild_headlines.sh, fresh clone + archive | **RESULT: FAIL** - 12/19 inputs missing; commit `24fe0e9` lacks the scripts |

## 9. A plain two-sided statement per module

- **S** - the convention is fixed and quotable; the anchor correlation is negative, so the
  model's shift runs opposite the measured shift, and it is small (|rho| < 0.1). Direction only.
- **M** - the negative association survives controlling for S_W with 73% of its magnitude kept,
  and it is more than a zero-epistasis world produces on its own (word unverified by C2); the
  larger of the two decomposition components is the one that misses its p-threshold by 0.0006;
  the placebo test clears its own bar in only 58%/78% of position resamples.
- **U** - conditioning on the A222V background costs a tiny but perfectly consistent amount of
  rank correlation (about 0.9% of ~0.37), which the frozen word calls HURTS and the block's own
  equivalence margin calls equivalent; both readings are on the table.
- **G** - in GB1 the model's shifts decay with separation while the measured epistasis does not,
  and model-data agreement is more negative among close partners - but the absolute correlations
  are small (near -0.022), the mid stratum is unresolved, and one of the three G-1 words does not
  fire.
- **N** - A222V's association is typical of its neighbourhood rather than peculiar to its
  position (REGION-LIKE, |NB| = 46), and the locality gradient cannot be attributed to either
  distance channel separately (NEITHER-RESOLVED) - though the position-collapsed sensitivity
  lands in the UNRESOLVED band and the superseded linear control would have named 3D-LOCAL.
- **L** - on the one model that exists, the association is not an artefact of the WT-background
  score (MODEL-REPLICATES), with the partial at ~75% of the raw; the other two models are
  unmeasured, not negative.

## 10. Discipline confirmations

- **Nothing protected, earlier, staged or frozen was edited.** No edit to `RESULTS.md`, the
  results log, the final write-up, `AGENTS.md`, any earlier log, any script numbered 164 or
  lower, `scripts/lib/phase2_diag*.py`, `scripts/lib/phase3_common.py`,
  `scripts/lib/phase3_guards.py`, `scripts/phase3_driver.py`, the planning document, or any of
  the five pre-registrations and three amendments. Verified in C0: all 24 hashes in
  `STATE_FOR_LAUNCH.md` unchanged, 0 changed, 0 missing, confirmed by my own parser and by the
  driver's.
- **Nothing staged, committed or pushed.** (Finding: commit `24fe0e9`'s message overstates its
  contents - see C5. Not touched.)
- **torch only where rule 1 allows.** Model scoring ran only in script 171 and script 173 and
  their gates, all into scratch directories; scripts 165, 166, 172, 174 and 176 import no torch,
  esm or thermompnn (172 and 174 print `torch in sys.modules: False`; 165 and 166 print their own
  no-torch gates). The real `data/processed/phase4/neigh/` and `ladder/` directories were not
  written by anything in this session - proved by before/after snapshots.
- **Every real output still matches its manifest**: 50/50 night files re-hashed after three hours
  of rescoring, 0 changed.
- **No threshold was loosened to make a result pass.** The one post-hoc addition (C2-DEC9, a
  5e-7 tolerance for 6-dp printed targets) is labelled post-hoc in the script, in its banner and
  in the log; five errors in my own C2 first pass are disclosed rather than quietly fixed.

## 11. The single most important entry

**`## [C2]` at line 322 of this log** - the independent recomputation. It re-derived every
headline number of modules S, M, U, N and L from the raw files without calling a single staged
Phase-4 script, reproduced **39 of 40** gated values (including every frozen word of N, L, S and
U, the whole of M-1, M-5 and M-6 - M-6's full-frame stability probability and its entire
k-distribution identical), and surfaced the three findings a reader needs: the anchor is
reproducible only to ~1e-8 unless the delta column is named; the two staged modules use opposite
tails for the same "abs" p-value; and M-3/M-4 are the one thing this session could not verify.

Session 4b verdict: **the phase's headline claim survives independent recomputation; two of its
frozen words do not exist because nights B and C were never run; the reproduction package works
here but not from a fresh clone.**

---

## [C5-ADDENDUM] - the one tracked file this session modified, and exactly how

Status: DONE (disclosure, append-only)

`data/processed/DATA_SHA256_MANIFEST.txt` is a **tracked** file, so C5's instruction to
regenerate it is the one place where this session changed a file git already tracks. Reported
here in full rather than left for Arnav to discover in `git status`:

- **Format preserved.** My first pass emitted `sha256  size  path`; the committed file is
  `sha256  path`. I noticed, compared against `git show HEAD:...`, and **regenerated in the
  committed 2-column format** so future diffs of this manifest stay meaningful.
- **Coverage is a strict superset, verified line by line.** Committed: **688** paths, spanning
  only `data/processed/phase2`, `phase2_diagnostics` and `phase3`. Mine: **1,955** paths.
  `in HEAD but MISSING from mine: 0`. Newly covered: **1,267** paths - the **95**
  `data/processed/phase4/**` files (roster, the 50 neighbour scores, manifests, driver state and
  logs) and the `data/external/**` downloads (MaveDB maps, the Weile et al. supplement, 1PGA and
  the other reference sets), none of which the committed manifest listed.
- **No value changed.** `shared paths with a CHANGED sha256: 0` - every one of the 688 committed
  entries still hashes to the value recorded there, so no data file has changed since that
  manifest was written.
- **Nothing parses it.** `grep -rl DATA_SHA256_MANIFEST scripts/ docs/ *.md` finds only prose
  mentions (the planning doc, the 4a build log, this log, `STATE.md`) - no code reads it, so the
  format restoration carries no functional risk.

The other three modified tracked files (`.gitignore`, `README.md`, `requirements.txt`) were
already modified before this session began and were not touched by it. **Nothing was staged,
committed or pushed.**

Verdict: **DONE.** One tracked file regenerated as instructed, format preserved, coverage
extended, zero values altered.
