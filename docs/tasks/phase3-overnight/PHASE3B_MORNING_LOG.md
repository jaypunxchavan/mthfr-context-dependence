# PHASE3B_MORNING_LOG — session 3b (verification and analysis review)

Template per PHASE3_OVERNIGHT.md §S1 (same as session 3a). Entries appended immediately after each task finishes.
Tasks in order: C0, C1, C2, C3, C4, then SUMMARY (3b) in the order of section S2.

## [SESSION HEADER] - session 3b opened
Status: IN PROGRESS
Time started: see C0's `date` output
What I did: Read AGENTS.md in full (binding); read `docs/tasks/phase3-overnight/PHASE3_OVERNIGHT.md` (Part C lines 254-276, section S2 lines 265-275, plus the three frozen appendices for context); read the three extracted pre-registrations in `prereg/` in full; read `STATE_FOR_LAUNCH.md` in full; read `PHASE3A_BUILD_LOG.md` in full (1,797 lines). Created this log before any task. No protected path, earlier log, earlier script, library, planning doc or frozen prereg will be edited; nothing will be committed, staged or pushed; no scoring will be launched.
Verdict: proceeding to C0.
Files created/modified: docs/tasks/phase3-overnight/PHASE3B_MORNING_LOG.md
Anything unexpected or worth flagging: none yet.
---
## [C0] - State and integrity of the overnight run
Status: PASS (all stages completed; 0 script-hash mismatches; 0 prereg mismatches; 0 duplicates; 0 stages timed out / skipped / failed)
Time started: Fri Oct 1 23:59:20 EDT 2026 / finished: Fri Oct 2 00:06 EDT 2026
What I did: Read `driver_state.json` and `driver.log` in full; confirmed no driver, launcher or scorer process is alive; counted `bg_*.csv` per module against the rosters (by set equality, not just counts); deduplicated every manifest into a NEW file (`manifest_dedup_c0.csv`, originals untouched); re-derived the sha256 of every staged script in `STATE_FOR_LAUNCH.md` section 1 with `venv/bin/python3` + hashlib; re-derived the three frozen pre-registration hashes plus the protected GB1 v1 file; grepped every `driver_stage_S*.log` for timeout / skip / failure evidence.

Actual output (real numbers, verbatim where quoted):

```
$ date
Thu Oct  1 23:59:20 EDT 2026

$ ps aux | grep -E "124_phase2|launch_phase|phase3_driver|154_gb1|156_rbd|155_gb1|157_rbd|158_multidms|esm" | grep -v grep
(no output; grep exit 1)

$ ls data/processed/phase3/.driver.lock ; ls data/processed/phase3/driver.pid
ls: data/processed/phase3/.driver.lock: No such file or directory
ls: data/processed/phase3/driver.pid: No such file or directory
```

**driver_state.json (verbatim structure):** `status: finished`, `started 2026-10-01T21:34:04-04:00`, `finished 2026-10-01T23:23:47-04:00`, `driver_pid 25771`, `current_stage: null`. Per stage:

| stage | start | end | status | steps (exit code, attempts) |
|---|---|---|---|---|
| S1 GB1 scoring | 21:34:04 | 21:56:52 | completed | score400_assayed exit 0 x1; score_first20_project exit 0 x1 |
| S2 RBD scoring | 21:56:52 | 23:16:59 | completed | gate_gr5 exit 0 x1; score100_rbd exit 0 x1 |
| S3 analyses | 23:16:59 | 23:22:27 | completed | gb1_analysis exit 0 x1; rbd_analysis exit 0 x1 |
| S4 multidms | 23:22:27 | 23:23:47 | completed | multidms_full exit 0 x1 |
| S5 integrity | 23:23:47 | 23:23:47 | completed | integrity exit 0 x1 |

Durations vs budget: S1 1,368 s of 6,000 (22.8%); S2 4,807 s of 9,000 (53.4%); S3 328 s of 4,500 (7.3%); S4 80 s of 7,200 (1.1%); S5 <1 s of 300. Total wall 109 min 15 s of the 450-min cap.

**driver.log tail (verbatim):** `2026-10-01T23:23:47-04:00 DRIVER FINISHED: S1=completed, S2=completed, S3=completed, S4=completed, S5=completed` followed by `LIMITATIONS: exit 0 means the run finished, not that every stage succeeded -- read driver_state.json; guard readings are point-in-time; UNGUARDED checks prove nothing.` (driver_state.json read above: all completed). Every stage guard line reads `GUARDS PASS (all readings within spec thresholds)`; no guard skip, no `--force`, no UNGUARDED, no retry line (`attempt 1/3` and `attempt 1/1` on every step, `attempts: 1` in state).

**File counts vs rosters (set equality, recomputed without any staged script):**

```
GB1  roster: 400 bg_*.csv files: 400 set_equal: True
GB1P roster-first20: 20 bg_*.csv files: 20 set_equal: True   (the 20 = first 20 of the draw order)
RBD  roster: 100 bg_*.csv files: 100 set_equal: True
```

Plus `wt_arm.csv` present in `gb1/`, `gb1_project/` and `rbd/`. No `.tmp` / stray partial file anywhere under `data/processed/phase3`.

**Manifest dedupe (new files; originals never overwritten):** `gb1/manifest.csv` 401 rows (400 bg + 1 wt_arm), `gb1_project/manifest.csv` 21 rows, `rbd/manifest.csv` 101 rows (100 bg + 1 wt_arm). Full-row duplicate count = 0, duplicate first-column (file id) count = 0 in all three. Deduped copies written to `gb1/manifest_dedup_c0.csv`, `gb1_project/manifest_dedup_c0.csv`, `rbd/manifest_dedup_c0.csv` — each **byte_identical=True** to its original, i.e. the dedupe was a no-op: the night wrote no duplicate manifest line.

**Staged-script sha256 vs STATE_FOR_LAUNCH.md (re-derived independently):**

```
OK scripts/153_m1_ge_target.py            e9fd90aff973be1c03dcfa15c80298f5cd54df4dbf5775a41de1839adf0b5133
OK scripts/154_gb1_score_backgrounds.py   d861660bc2e53e22853b127d9a0139aa644fc27de91c2ee67a8b9bd3eb6df7c6
OK scripts/155_gb1_regime_analysis.py     0b3874d23031f37b5ebab9c6cfa2d983a308ee7f03b20a072d925b156db83eae
OK scripts/156_rbd_score_backgrounds.py   e9dec44aebd7e96f646c092c1ad7463b72360728373150a2979793611769a837
OK scripts/157_rbd_regime_analysis.py     7ec495111116a43742f038ffc075fadd4f193b5ca0e203169f9e904af8106ce3
OK scripts/158_multidms_rbd.py            c7044836f080937504c1b822b4c009dce8ca8631bbde0428f787040dbf0fae15
OK scripts/phase3_driver.py               07b7f1898e81141a8c55b37f795c89da8860a84f1f50ab0528971ab075d4a8cd
OK scripts/lib/phase3_guards.py           9daed884c57c4a1267e6e3ce3d59c48ecef36153abe5476e71fbcd7474899737
OK scripts/test_phase3_driver.py          346d1f640fb4343070af6d58ad96d510d6ba8fd8190702e3e38742b5f9c739b0
OK scripts/159_phase3_common_gate.py      c0888438576f6ea2196b6565bdee9b3bc61aa0d5fc9b0b01aa02ba232cfffa48
OK scripts/160_gb1_phase3_inputs_roster.py 2bdc68dfcde259e7361a736f5be911f489098800fd0fe8018583c80ffb94d84e
OK scripts/161_gb1_gate_g1prime.py        12ae46007496e17c290375fcc1328aaeca0aac4aeabfb6821c5c65ad7677a485
OK scripts/162_rbd_inputs_gate.py         76abc21b0453122e3f1bede2c76c4f34f5369246e4ead7ee9061d507f8f167ff
OK scripts/163_rbd_targets.py             353bfe6e8d5793a1c03ad4ee6fcbda1f6c7b303940ec063db10aadebd629a81e
OK scripts/164_rbd_roster.py              fa45236751deff16dfd900e77e1538d58ae3ae9fe62ddca77c72a558133e0351
OK scripts/launch_phase3_overnight.sh     6c988597f08e7733d9d5ea81d6fa1ecd7f16383ba06a30d69e9ae122912bbfb9
TOTAL 16 files, mismatches = 0
```

**No change to any staged script. FLAG check: nothing to flag.** (S5's own run agrees: `INTEGRITY: sha256: MATCH` for all 15 `.py` entries + launcher, `INTEGRITY: RESULT PASS (22 findings)` in `driver_stage_S5.log`.)

**Pre-registration hashes (re-derived):**

```
OK docs/tasks/phase3-overnight/prereg/GB1_REGIME_PREREG_v2.md          b3c82d589afc2889f60ad8626dcb24d0496f77303d0696b52db700129fd1357e
OK docs/tasks/phase3-overnight/prereg/RBD_REPLICATION_PREREG_v1.md     8965450a524e883b02ef2c970178cd242709bed1c55bd5e6ed573c1e2c2671a7
OK docs/tasks/phase3-overnight/prereg/MTHFR_GE_TARGET_PREREG_v1.md     73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c
OK docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md (protected v1) b170bdfff729a017def585047e503a86151ba1e89d2632ae9bc5e8eb9c137613
```

All three frozen pre-registrations unchanged since A1; the protected v1 file unchanged.

**Stages timed out / skipped / failed: NONE.** Evidence: (i) `driver_state.json` every stage `status: completed`, every step `exit_code: 0`, `attempts: 1`; (ii) `driver.log` contains no `timeout`, no `skip`, no `guard skip`, no `retry`, and ends `DRIVER FINISHED: S1=completed ... S5=completed`; (iii) grep of `driver_stage_S1..S5.log` for `fail|timeout|skip|retry|error|traceback|exit 3` returns only benign matches (scorer bookkeeping `published/skipped-this-run`, `0 skipped`, `G-4 ... coverage failures 0`, `GATES: 10/10 PASS, 0 FAIL -> exit 0`, G-SYN PASS lines, and one quoted `raise ValueError` source line inside the RBD analysis's own printed source excerpt); (iv) the S3 dependency/coverage prechecks both passed (`coverage gb1: PASS 400/400 ... min coverage ... 1.000 >= 0.95`; `coverage rbd: PASS 100/100 ... min coverage TGT_N501Y 0.995 >= 0.95`).

Verdict: **C0 PASS.** The night ran clean end to end: 5/5 stages completed on attempt 1, no guard skip, no retry, no timeout, no gate failure, no script drift, no prereg drift, no lost or duplicate output file.
Files created/modified: `docs/tasks/phase3-overnight/PHASE3B_MORNING_LOG.md` (this entry); `data/processed/phase3/{gb1,gb1_project,rbd}/manifest_dedup_c0.csv` (NEW deduped copies; originals untouched). Nothing else; no git operations; no scoring launched.
Anything unexpected or worth flagging: nothing unexpected. One observation for C1: S2 (RBD) took 53.4% of its budget vs the 45.6% projection — still well inside, no action.
---
## [C1] - Cheap gates, then the conditional rescore

Status: **PASS**
Time: 2026-10-02 06:41 – 07:04

**What I did.** (1) Re-ran every cheap per-file gate myself, directly from the
raw per-background files, without invoking the staged analysis scripts.
(2) Re-ran the bootstrap reference gate (script 159) at its own recorded
parameters. (3) Confirmed tonight's own gate lines from the stage logs.
(4) Ran the free (no-model) cross-process check of the smoke runs against the
overnight files. (5) With the conflict resolved in favour of a scratch-only
read-only rescore (user authorization, this session), ran a fresh rescore of
three never-re-scored backgrounds per module into NEW scratch directories,
one model load at a time, with a memory/swap re-check before each load, and
proved the real output directories were untouched before/after.

### 1. Coverage / integrity gates (re-derived from raw files)

```
GB1 coverage (all 400 bg files, own position excluded, floor 0.95 of 54):
  failures = 0; every file has 54 positions x 19 mut_aa = 1026 rows;
  position set = {55} minus own position, exact for all 400.
GB1 G-2 (never score the background's own residue): 0 violations in all 400.
  two-seq subset (roster_v2 sequence == "project"): 20 files, label "project",
  coverage and own-position checks clean.
RBD coverage / G-R4 (all 100 bg files, own site excluded, floor 0.95 of 201):
  failures = 0; min coverage 200/201 = 0.995; 0 own-site violations;
  all files 3800 rows (19 x 200); site == position + 330 for all 38,000 rows;
  wt_arm.csv 3819 rows = 201 sites x 19 + identity rows, 201 unique sites.
G-5 (WT identity): assayed singles complement vs data-derived WT across the
  55 positions (2..56) = 0 mismatches; project arm = exactly [(2, 'Q', 'T')];
  roster wt_aa vs both sources = 0 mismatches.
G-R2 (targets vs reference): vs each target's OWN background reference
  = 0 mismatches of 20,100; RBD_sites.csv vs fasta = 0 mismatches.
  (Cross-check: 140 rows differ from the WUHAN sequence; these are exactly the
  7 known target-background substitutions x 20 rows — Beta 417/484/501,
  Delta 452/478, E484K 484, N501Y 501 — as expected from A5b.)
```

### 2. Bootstrap reference gate (script 159, its own parameters)

Re-ran `N_BOOT=10000 SEED=0 N_REF=500 N_PERM=1000 venv/bin/python3
scripts/159_phase3_common_gate.py`: **40/40 PASS**, exit 0, wall 42.8 s.
Identity check exact; draw-by-draw anchor and restricted max|diff| =
0.000e+00; Phase 1 CI lo reproduced exactly, hi agrees to 7.633e-17.

### 3. Tonight's own gate lines (S3 stage log)

```
script 155: "GATES: 10/10 PASS"  (G-4: 400/400 files, coverage failures 0)
script 157: "GATES: 15/15 PASS"  (G-R4: 100/100, min coverage 0.9950)
```

### 4. Free check (no model): smoke runs vs overnight, tol 1e-6

Same backgrounds scored on this machine in separate processes earlier
(A4e for GB1, A5f for RBD):

```
GB1 gb1_smoke -> gb1:  bg_G4KV 1026 rows, bg_G19EL 1026, bg_G55TL 1026,
  wt_arm 1045 — max|diff| = 0.000e+00 each, 0 rows over 1e-6. AGREE.
RBD rbd_smoke -> rbd:  bg_TGT_N501Y 3800, bg_TGT_E484K 3800, bg_S501A 3800,
  wt_arm 3819 — max|diff| = 0.000e+00 each, 0 rows over 1e-6. AGREE.
```

**The two runs agree exactly (bit-identical across processes).**

### 5. Fresh rescore of backgrounds scored only once (scratch only)

Selection (exact code, disclosed): candidates = roster ids in roster-file
order, excluding the smoke backgrounds (GB1: G4KV, G19EL, G55TL from
roster_v2, 397 candidates; RBD: TGT_N501Y, TGT_E484K, S501A from roster_v1,
97 candidates), then `np.random.default_rng(0).choice(cand, 3,
replace=False)`. For RBD the explicit >=1 G-arm and >=1 V-arm constraint was
enforced by seed-0 rejection sampling: **1 redraw** (the first seed-0 draw
failed the arm constraint). GB1 picks: **G16TC, G22DR, G32QH** (roster
positions 256, 206, 339). RBD picks: **V331Y (V_N501Y arm), V406K (V_E484K
arm), G492H (G arm)** (roster positions 4, 11, 6).

Procedure: staged scorers' own CLIs (their own scoring functions, not a
reimplementation) — `154_gb1_score_backgrounds.py --only <id>` x3 with
`--sequence assayed` (the night's setting) into
`data/processed/phase3/c1_rescore_gb1/`; `156_rbd_score_backgrounds.py
--only V331Y --only V406K --only G492H` into
`data/processed/phase3/c1_rescore_rbd/`. GB1 ran first, then RBD, one model
load at a time, never concurrently. Pre-load checks:

```
before GB1 load: free 67% (>= 35% OK), swap 1118.75M = 1.09 GB (< 3.0 GB OK)
before RBD load: free 59% (>= 35% OK), swap 1278.81M = 1.25 GB (< 3.0 GB OK)
```

RBD scorer's own gates all passed in the scratch run (G-156-1..6, G-156-4
3 files written / 0 skipped, G-156-5 min coverage 0.9950). No SKIPPED needed.

Comparison vs the overnight files, tolerance 1e-6, device from each
manifest:

```
GB1 (device mps, median pass 0.0523 s):  rows fresh vs night   max|diff|    verdict
  G16TC  1026 = 1026 (common 1026)        0.000e+00   AGREE
  G22DR  1026 = 1026 (common 1026)        0.000e+00   AGREE
  G32QH  1026 = 1026 (common 1026)        0.000e+00   AGREE
  wt_arm 1045 = 1045                      0.000e+00   AGREE
RBD (device mps, median pass ~0.16 s):
  V331Y  3800 = 3800 (common 3800)        0.000e+00   AGREE
  V406K  3800 = 3800 (common 3800)        0.000e+00   AGREE
  G492H  3800 = 3800 (common 3800)        0.000e+00   AGREE
0 rows over 1e-6 anywhere. No module FAILS; both remain interpretable in C3.
```

**Proof the real output directories were not written** (recorded before any
rescore and again after the last one):

```
             BEFORE                                              AFTER
gb1          407 entries, newest manifest_dedup_c0.csv 2026-10-02 00:00:52   407 / same / same mtime
gb1_project   23 entries, newest manifest_dedup_c0.csv 2026-10-02 00:00:52    23 / same / same mtime
rbd          107 entries, newest manifest_dedup_c0.csv 2026-10-02 00:00:52   107 / same / same mtime
```

Identical counts, identical newest file, identical mtime. Roster files,
driver files, and the real gb1/ rbd/ gb1_project/ directories were only ever
read. No driver/scorer process alive after the rescore (`ps` grep empty).
No git operations; nothing staged.

Verdict: **C1 PASS.** All cheap gates pass on re-derivation; the reference
bootstrap gate reproduces 40/40 at its own parameters; the smoke runs and the
overnight runs agree to 0.000e+00; the fresh 6-background rescore agrees to
0.000e+00 on every value with the machine above the memory/swap floors at
every model load. Both modules remain interpretable.
Files created/modified: this log entry; NEW scratch dirs
`data/processed/phase3/c1_rescore_gb1/` (3 bg + wt_arm + manifest) and
`data/processed/phase3/c1_rescore_rbd/` (3 bg + manifest). Real output
directories untouched (proven above).
Anything unexpected or worth flagging: the C1 rescore conflicted with the
session's "no scoring" instruction; resolved by explicit user authorization
(scratch-only, read-only w.r.t. real outputs) — the contradiction was in the
prompt, not the reading. One seed-0 rejection redraw was needed for the RBD
arm constraint (disclosed above, not a problem).
---
## [C2] - Independent recompute of headline numbers

Status: **PASS (3/3 modules; 405 checks, 0 disagreements at the frozen
tolerances)**
Time: 2026-10-02 07:05 – 08:14 (script write + reduced-N smoke + full run;
full run wall 100.5 s, exit 0)

**What I did.** Wrote `docs/tasks/phase3-overnight/c2_independent_recompute.py`
and ran it. It does **not** import or invoke scripts 153/155/157. Every
statistic is computed in that file from the raw per-background files:
own Spearman (`scipy rankdata(average)` + `np.corrcoef`, written locally,
cross-checked against `scipy.stats.spearmanr` in the output), own `p_spec`
triplet, own percentile CI, own permutation p, own background bootstrap, own
LOO-OLS. Imports beyond pandas/numpy/scipy: `scripts.lib.phase2_diag` (the
project's own cached Phase-2 row construction — the raw delta_b side of M1)
and, for exactly one thing, `phase3_common.pos_cluster_boot` for M1 (b)'s
bootstrap CI draws (disclosed in the docstring; that machinery is frozen
infrastructure gated 40/40 by A2 and again by C1's 40/40 draw-by-draw
0.000e+00 — what is verified here is that 153 wired the right arrays into
it). Per Part C: >= 10 per-background rho_b per module (GB1 400, RBD 1200,
M1 776 — every row, not a sample), every covariate Spearman (all 4 x all 4
thresholds), `p_spec_abs` for both RBD targets. First disagreement in a
module prints both numbers and stops that module. Tolerances pre-registered
in the script: 1e-12 full-precision, 5.1e-7 at 6 dp, 5.1e-5 at 4 dp,
integers/words/beater-sets exact. No torch, no esm imported (checked at
exit: NONE).

**Reduced-N smoke first (AGENTS 1), and it caught a real bug.** At
N_BOOT=300/N_PERM=300 (expected: only resampling-dependent checks
disagree), module R passed fully (113 checks, no resampling) and G/M1
stopped at their first CI as expected — but M1's **per-background rho
rows**, which involve no resampling, also disagreed (388 of 582 GE rows,
up to 8.142e-06) while OWN rows and every row-construction check were
exactly 0. Diagnosis: **pandas' default `read_csv` float parser is not
round-trip exact** — it perturbed 8,852 of 13,134 values of
`m1_own_e_b_ge.csv` by up to 1 ULP (2.22e-16), which flips near-tie ranks
and moved Spearman rho by up to 8.1e-06 against the staged record. Fixed
**before the full run** by reading every CSV whose floats are compared to
staged values with `float_precision="round_trip"` (recovers exactly what
the staged script wrote: staged rho then reproduced within 5e-17);
score/bg files that staged and this script each parse themselves stay on
the default parser on both sides. **Tolerances unchanged** (1e-12 was and
remains the pre-registered rule); the fix is disclosed in the script's own
docstring. (Disclosed: the first smoke's output file was overwritten by
the post-fix smoke re-run; recorded values above are from the session
transcript.) Two of my own staged-text parses also mis-read the printed
fractions `2/79` / `(1/79)` as k instead of (1+k)/(1+|N|) — my bugs,
caught by the module-stop protocol, fixed; no number changed.

### Module G (GB1 vs staged 155): PASS — 159 checks

```
partner rows 410,271 = staged. All 4 thresholds: completed 400,
below 100-floor 0, dropped for missing delta 0.
t25 (primary) distribution: mean -0.009125, median -0.004175, sd 0.096911,
range [-0.307915, +0.225376], frac<0 0.505 — all at staged's 6 dp / 4 dp.
centering CI t25 [-0.018633, +0.000402] CENTERED (worst CI endpoint diff
across thresholds 3.18e-07, tol 5.1e-07).
covariates (rho, CI, perm p, word), t25 = staged at 6 dp:
  (a) -0.073349 [-0.169842, +0.025742] p=0.1415 NOT RESOLVED
  (b) -0.367726 [-0.451667, -0.278739] p=0.0001 ASSOCIATED
  (c) +0.001294 [-0.096464, +0.099606] p=0.9810 NOT RESOLVED
  (d) -0.344868 [-0.428355, -0.257477] p=0.0001 ASSOCIATED
  (t23/t28/unfiltered likewise, all 16 covariate rows within tolerance;
  perm p compared as (k+1)/(N_PERM+1), matching 155 line 576.)
per-background table (primary): 400 rows x (rho_b, n_partners, mean_abs_dpos,
single_fitness_W, sd_eb) — max|diff| = 0.000e+00 on every field, 0 rows
outside 1e-12.
```

### Module R (RBD vs staged 157): PASS — 113 checks

```
1200 rho rows (100 bg x 2 targets x 2 phenotypes x 3 masks): max|diff| =
0.000e+00, 0 rows outside 1e-12.
All 12 section5 triplets exact to 1e-12 (JSON is full precision), incl.
k/n integers and both outcome words. Primary:
  N501Y bind/ge3: rho_target -0.09049377121986184, n=57, k_abs=1,
    p_abs = 0.034482758620689655 -> RBD-REPRODUCES  (exact, 0.000e+00)
  E484K bind/ge3: rho_target -0.023931167920018745, n=45, k_abs=23,
    p_abs = 0.5217391304347826 -> RBD-DOES-NOT-REPRODUCE (exact, 0.000e+00)
```

### Module M1 (MTHFR GE vs staged 153): PASS — 133 checks

```
row construction vs cached bg_rows: join counts 0, position mismatches 0,
max|delta diff| = 0.000e+00. A222V anchor rho full -0.08811806424891734
= staged repr exactly (0.000e+00).
per-background rho: 776 rows (96 bgs + A222V x 2 views x 4 constructions)
max|diff| = 1.388e-17, 0 rows outside 1e-12.
(a) GE-ISO 0.949814, GE-SIG 0.951543, GE-LIN-CF 0.999740 — all 6 dp.
(b) CIs/shrink/p_boot all within tolerance (worst endpoint diff 4.6e-07
    vs staged's 6 dp); p_boot 0.0000 all four; 10000 finite draws each.
(c) ALL 6 GE rows: staged == the ORIGINAL rho_b null construction
    (threshold, k, beaters, p). Original row: n=78, k_full=1, p=0.025316,
    k_H=3, beaters exact.
(d) all 8 rows (r_A, k, p_adj, beaters) within tolerance.
(e) all 4 rows: (1+1)/19 = 0.105263.
(f) 67 resolved nulls; original +0.731577372 CI [+0.600332, +0.817699];
    GE gradients and CIs within tolerance; 10000 finite draws each.
outcome words: staged counts and words all exact; all three GE-SURVIVES.
```

### C4 flag: staged (c) sentence vs staged (c) numbers (both computed)

The staged output's printed formula and the frozen prereg 3(c) both say
`p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / (1 + 78)`, but script
153's code passes the **original** rho_b nulls into the (c) loop. I
computed (c) **both ways**:

```
row              staged = original-null   rho_b^GE nulls (prereg literal)
GE-ISO full      0.012658 (0/79)          0.037975 (k=2: AV_195, G_P254F)
GE-ISO H         0.012658 (0/79)          0.050633 (k=3)
GE-SIG full      0.012658 (0/79)          0.037975 (k=2)
GE-SIG H         0.012658 (0/79)          0.050633 (k=3)
GE-LIN-CF full   0.025316 (k=1)           0.025316 (identical)
GE-LIN-CF H      0.050633 (k=3)           0.050633 (identical)
```

Staged matches the original-null construction in all 6 rows (that is what
the gated checks compare against — module PASS = the printed numbers are
correctly derived from the code that ran). Under the prereg formula's
literal rho_b^GE nulls, 4 of 6 rows change value — **but no outcome word
changes**: all three remain GE-SURVIVES under both constructions, because
0.037975 <= 0.05 and 0.050633 <= 0.10 both still pass the frozen rule.
Flagged for C4 (printed-formula-vs-computation contradiction, words
robust); not a C2 disagreement.

**Real output directories untouched after C2** (same proof as C1):

```
             before C2                                             after C2
gb1          407 entries, newest manifest_dedup_c0.csv 00:00:52    407 / same / same mtime
gb1_project   23 entries, newest manifest_dedup_c0.csv 00:00:52     23 / same / same mtime
rbd          107 entries, newest manifest_dedup_c0.csv 00:00:52   107 / same / same mtime
```

Verdict: **C2 PASS.** 405 checks across the three modules, zero
disagreements at the pre-registered tolerances; the one real defect found
(smoke) was in my own recompute pipeline, fixed before the full run and
disclosed above. All three modules are interpretable in C3. torch/esm:
NONE.
Files created/modified: this entry; `docs/tasks/phase3-overnight/
c2_independent_recompute.py`; `C2_SMOKE_OUTPUT.txt` (post-fix smoke);
`C2_RECOMPUTE_OUTPUT.txt` (full run, exit 0). Nothing under
`data/processed/**` written (the script's only output is stdout); no git
operations; nothing staged.
Anything unexpected or worth flagging: (1) the parser-precision bug above
— caught only because the smoke was run before the full run; (2) the
staged (c) formula-vs-code contradiction, carried to C4; (3) the C2 script
writes no files into data/processed (verified by the before/after proof).
---
## [C3] - Interpretation within the frozen words

Status: **PASS.** All three modules cleared C0, C1 and C2, so all three
are interpretable (Part C: a failed gate would report that module as
failed, not interpreted).

Rules applied, verbatim from the frozen blocks and planning rule 11:

- Each module is read in its own frozen block's order and uses exactly
  its pre-registered outcome words — GE-SURVIVES / GE-WEAKENS /
  GE-DOES-NOT-SURVIVE (M1 s4); CENTERED / OFF-CENTER and ASSOCIATED /
  NOT RESOLVED / UNDERPOWERED (G s5); RBD-REPRODUCES /
  RBD-DOES-NOT-REPRODUCE / RBD-INCONCLUSIVE (R s5). NOT RESOLVED is
  stated as "n cannot resolve this", never "no relationship" (G s5).
- **No cross-system statement**: nothing here confirms or undermines any
  other system's result (G s1/s5, R s1, rule 11).
- Rule 12 INSIDE/OUTSIDE/MARGINAL: **no matched-control / random-deletion
  range appears in any staged output this session**, so no flag arises.
  Where a value sits near a decision bound I give the distance and build
  no conclusion on it.
- Scope disclosure: C2 independently re-verified every M1 (a)-(f) value
  and word, all four GB1 thresholds' distribution/covariate rows, all 12
  RBD section-5 rows, and every per-background rho row. The RBD section-6
  secondaries, the GB1 two-sequence and G-SYN blocks are descriptive per
  their frozen sections and are read from the staged record — they were
  not in C2's pre-registered recompute scope (Part C named rho_b rows,
  covariate Spearmans, p_spec_abs).

### M1 - MTHFR GE target (frozen s3 in order (a)-(f), then s4 words)

```
(a) Spearman(own_e.b^GE, own_e.b) over 10,757 rows:
    GE-ISO +0.949814   GE-SIG +0.951543   GE-LIN-CF +0.999740

(b) rho^GE and CI, and (c) p_spec^GE, primary and sensitivities:
variant      rho^GE     CI                   p full         p H          word (s4)
GE-ISO (pri) -0.122476 [-0.152648,-0.092189] 0.012658 (1/79) 0.012658 (1/79) GE-SURVIVES
GE-SIG       -0.122780 [-0.152914,-0.092607] 0.012658 (1/79) 0.012658 (1/79) GE-SURVIVES
GE-LIN-CF    -0.087618 [-0.116907,-0.059049] 0.025316 (2/79) 0.050633 (4/79) GE-SURVIVES
original     -0.088118 [-0.117333,-0.059511] 0.025316 (2/79) 0.050633 (4/79) -

shrinkage (b): GE-ISO -0.389909, GE-SIG -0.393355, GE-LIN-CF +0.005675
(d) p_spec_adj: all eight rows at or below 0.05 (seven at 0.037975,
   GE-ISO full at 0.025316)
(e) rank: all four rows (1+1)/19 = 0.105263  (a rank, not a test, D10)
(f) gradient over 67 resolved nulls:
   original  +0.731577 CI [+0.600332, +0.817699]
   GE-ISO    +0.729343 CI [+0.613181, +0.803973]
   GE-SIG    +0.730540 CI [+0.612456, +0.805775]
   GE-LIN-CF +0.732635 CI [+0.602354, +0.817335]
   all four CIs contain the frozen reference +0.7316
```

Interpretation (frozen s4; primary governs): the GE-ISO CI excludes zero
in the negative direction, full p 0.012658 is **at or below 0.05**
(distance to bound 0.037342) and H p 0.012658 is **at or below 0.10**
(distance 0.087342) → **GE-SURVIVES**. Sensitivities: GE-SIG the same
word with the same p's; GE-LIN-CF the same word with a thinner margin
(H p 0.050633 at or below 0.10, 0.049367 from the bound). **No word-level
disagreement among the three** — there is nothing to state under s4's
"any disagreement is stated plainly". Construction sensitivity (computed
both ways in C2, corrected in C4-1): under the literal frozen s3(c)
formula's `rho_b^GE` nulls, GE-ISO and GE-SIG read 0.037975 full /
0.050633 H and GE-LIN-CF is unchanged — **all three words identical under
either construction** (0.037975 at or below 0.05; 0.050633 at or below
0.10). Effect size alongside significance: rho^GE -0.122476 with the two
bounded shapes shrinking it ~39% toward zero, the linear-CF not shrinking
(+0.005675).

### G - GB1 regime map (frozen s5)

Backgrounds completed: **400 of 400** roster backgrounds (gb1 401 files
incl. the WT arm; gb1_project 21 files incl. its WT arm), 0 dropped for
the 100-partner floor (inert per A1), roster partner rows 410,271. The A8
floor of 200 is exceeded, so the covariate tests are interpretable and
**not** labeled UNDERPOWERED.

Distribution (primary threshold t25, Input Count >= 25): mean rho_b =
-0.009125, background-level bootstrap CI [-0.018633, +0.000402] includes
0 → **CENTERED** (median -0.004175, sd 0.096911, range [-0.307915,
+0.225376], frac<0 0.5050).

Covariates (primary t25; ASSOCIATED iff the background-bootstrap CI of
the rho excludes 0; permutation p is the association null, as the
script's own LIMITATIONS block states):

| covariate | rho | CI | perm p | word |
|---|---|---|---|---|
| (a) mean abs position delta | -0.073349 | [-0.169842, +0.025742] | 0.1415 (1415/10001) | NOT RESOLVED |
| (b) single-mutant fitness W | -0.367726 | [-0.451667, -0.278739] | 0.0001 (1/10001) | ASSOCIATED |
| (c) number of partners | +0.001294 | [-0.096464, +0.099606] | 0.9810 (9811/10001) | NOT RESOLVED |
| (d) SD of e_b | -0.344868 | [-0.428355, -0.257477] | 0.0001 (1/10001) | ASSOCIATED |

(b) and (d) are ASSOCIATED — both negative, CIs exclude 0, permutation p
at the 1/10001 floor. (a) and (c) are **NOT RESOLVED: n cannot resolve
this**, never "no relationship".

Threshold sensitivities (t23 >= 23, t28 >= 28, unfiltered): **every word
identical to the primary at every threshold.** All four distributions
CENTERED (CIs t23 [-0.018592, +0.000401], t28 [-0.018622, +0.000392],
unfiltered [-0.018142, +0.000421]); (a) NOT RESOLVED, (b) ASSOCIATED,
(c) NOT RESOLVED, (d) ASSOCIATED in all four columns. **No threshold
sensitivity disagrees.** Values move without moving any word: (c) rho
+0.001294 (t25) → +0.013406 (t23) → +0.062652 (unfiltered); (a) perm p
0.1195–0.1936.

Two-sequence comparison (frozen A7; reported, A7 defines no word): first
20 backgrounds in roster order, 20 of 20 pairs present on both sequences;
Spearman between the two rho_b vectors **+0.836090** (n=20); max
|delta rho_b| 0.172998.

Per rule 11 this module characterizes the statistic in this system; no
sentence here reads against MTHFR or RBD (frozen s1/s5).

### R - RBD design replication (frozen s5 per target, then s6)

Primary frame (ACE2 binding, barcode n_bc >= 3):

| target | rho_T | corrected CI (6a) | p_abs | p_neg | p_pos | word |
|---|---|---|---|---|---|---|
| N501Y | -0.090494 | [-0.157685, -0.022157] excludes 0 | 0.034483 = (1+1)/(1+57) **at or below 0.05** | 0.034483 | 0.982759 | **RBD-REPRODUCES** |
| E484K | -0.023931 | [-0.079024, +0.030238] includes 0 | 0.521739 = (1+23)/(1+45) **above 0.10** | 0.239130 | 0.782609 | **RBD-DOES-NOT-REPRODUCE** |

Two targets are two looks, reported with no multiplicity adjustment
(frozen s5).

Sensitivities (frozen s6: descriptive; none changes the outcome words) —
**disagreements stated plainly:**

- **Barcode mask: N501Y disagrees with itself across masks.** ge3
  (primary) 0.034483 → RBD-REPRODUCES; ge5 0.034483 → RBD-REPRODUCES;
  **ge1 0.068966 → RBD-INCONCLUSIVE** (between 0.05 and 0.10). E484K
  agrees across all three masks: 0.565217 / 0.521739 / 0.434783, all
  → RBD-DOES-NOT-REPRODUCE.
- **Expression phenotype: N501Y disagrees with its own bind result.**
  N501Y/expr ge3 0.568966 → RBD-DOES-NOT-REPRODUCE (all six expr rows
  → RBD-DOES-NOT-REPRODUCE); E484K/expr 0.630435 agrees with its bind
  word.
- **Split-half: N501Y's halves disagree** (stability descriptor, never a
  decision): h1 p_abs 0.0345 → RBD-REPRODUCES, h2 p_abs 0.2931 →
  RBD-DOES-NOT-REPRODUCE. E484K's halves agree (0.6087 / 0.4565, both
  RBD-DOES-NOT-REPRODUCE).
- Shift-adjusted (6b): N501Y p_spec_adj 0.0517 — **above the 0.05 line by
  0.001724** (near-bound; rule 12's MARGINAL flag applies only to
  matched-control ranges, which do not occur here; no conclusion is built
  on it); its shift Spearman(rho_b, mean|delta_b|) 0.0180 CI
  [-0.1902, +0.2172] includes 0. E484K p_spec_adj 0.6087 above 0.10;
  shift rho +0.2065 CI [+0.0144, +0.3895] excludes 0.
- Locality (6c): N501Y rho_b vs sequence distance +0.3073 CI
  [+0.0979, +0.4868] excludes 0 (positive); 3D distance CI
  [-0.0140, +0.4018] includes 0. E484K sequence CI [-0.1425, +0.3993]
  and 3D CI [-0.1791, +0.3509] both include 0. No frozen word.
- Arm S rank fraction (6d; "a rank fraction, not a test"): N501Y
  |rho_T| rank 3 of 19 → fraction 0.158 (signed rank 17); E484K rank
  12 of 19 → fraction 0.632 (signed rank 10).
- multidms target (6h; secondary, **no outcome word**): available —
  e_T_MD.csv (15,198 x 8), S4 criterion MET. Printed next to the
  primary, never replacing it: N501Y bind rho_T^MD -0.0606 (primary
  -0.090494), E484K bind -0.0387 (primary -0.023931); expression
  -0.0969 / -0.0180.

Interpretation within frozen words: **N501Y → RBD-REPRODUCES; E484K →
RBD-DOES-NOT-REPRODUCE** at the primary frame, both with no multiplicity
adjustment. The mask and split-half sensitivities show N501Y is not
uniformly reproducing across looks — stated plainly and, per frozen s6,
changing no outcome word. Per frozen s1 this replicates the DESIGN and
makes no claim about MTHFR.

Files created/modified: this entry only. No staged file edited (C4 below
is append-only, in this log). No git operations.
Anything unexpected or worth flagging: the N501Y mask/split-half
sensitivity disagreements (reported, not failures — they are the data);
the secondary blocks' scope disclosure above.
---
## [C4] - Corrections (append-only)

Part C4: append-only corrections for any staged-output sentence that
contradicts its table. **Nothing staged was edited**; every correction is
recorded here. All four are in the A3/M1 staged output
(`docs/tasks/phase3-overnight/PHASE3_A3_FULL_OUTPUT.txt`). The GB1 and RBD
staged outputs had every comparative sentence re-read against its printed
numbers this session — GB1 (S3 log lines 90-222: counts, perm-p
parentheticals, G-SYN, two-sequence) and RBD (S3 log lines 249-449:
section 5, all secondaries, gates) plus S4 — **no contradiction found**
there. The (d)/(e) literal-reading k values below are session-3b spot
checks of my own (pandas/numpy + `phase2_diag` imports), outside C2's 405
pre-registered checks — disclosed as such.

**C4-1 (main one; no outcome word changes). A3 line 229 prints the frozen
s3(c) formula, `p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / (1 +
78)`, but the six numbers under it (lines 230-235) are computed against
the ORIGINAL `rho_b` nulls.** Evidence: `scripts/153_m1_ge_target.py`
lines 900-901 print the `rho_b^GE` formula, while lines 903 and 785-786
pass `nulls_full = table.loc[N_ids, "rho_full"]` / `nulls_H` — the
original Phase-2 rho table (sha e397a44...). C2 recomputed both
constructions: staged matches the original-null construction in **all six
GE rows exactly**; under the formula as printed, GE-ISO full would read
(1+2)/(1+78) = 0.037975 (beaters AV_195, G_P254F), GE-ISO H 0.050633,
GE-SIG full 0.037975, GE-SIG H 0.050633, and GE-LIN-CF's two rows are
identical either way (0.025316 / 0.050633). The `p_spec^GE(...)` labels
in the words block (A3 lines 266-268) carry the same value-vs-formula
mismatch. **Correction: the printed numbers are correct for the code that
ran; the formula and labels describe the frozen construction the (c) loop
did not use. No outcome word changes under either construction — all
three remain GE-SURVIVES** (0.037975 at or below 0.05 and 0.050633 at or
below 0.10 both satisfy frozen s4). Anyone quoting `p_spec^GE` from the
staged output must state which null set the value came from.

**C4-2. A3 line 248's rendered (e) formula, `(1 + #{b in S : rho_b <=
rho_A}) / 19`, drops the `^GE` superscripts that frozen s3(e) carries
("on rho_b^GE").** The table's GE rows were computed in GE space (C2
verified k=1 against `rho_b^GE` nulls, matching staged). Under the
formula as literally printed (original `rho_b` nulls), GE-ISO and GE-SIG
would each read (1+0)/19 = 0.052632, not the table's (1+1)/19 = 0.105263
(GE-LIN-CF and original coincide either way). Verified this session:
original-null k = 0 / 0 / 1 for GE-ISO / GE-SIG / GE-LIN-CF vs staged
1 / 1 / 1. **Correction: the table follows the frozen definition and is
right; the printed formula's missing superscripts, read literally,
contradict rows 250-251.**

**C4-3. A3 line 238's (d) prose, "leave-one-out OLS of rho_b on
mean|delta_b|", likewise omits `^GE` for the GE rows.** Staged (d) is in
GE space — C2's GE-space recompute matched all eight rows (r_A, k, p_adj,
beaters) exactly, and the original row reproduces under original space
(r_A -0.066425, k = 2, both confirmed this session). Under one literal
reading of the prose (OLS fit on original `rho_b`, target still rho^GE),
GE-ISO's k would be 0 (p 0.012658 vs table 0.025316) and GE-SIG's would
be 0 (0.012658 vs table 0.037975); GE-LIN-CF's k coincides (2) with r_A
differing by 4.2e-05. **Correction: quantity name and table are GE-space
per frozen s3(d); only the method prose lost the superscript.**

**C4-4. A3 line 155's parenthetical is arithmetically impossible as
written: "rows with a rebuild value but NO recorded own_e_b = 1108 (the
raw file's 1232 nonsense/synonymous rows plus substitutions the atlas
never assigned own_e_b to...)" — 1108 < 1232.** Recomputed from
`m1_own_e_b_ge.csv` + the raw file: the 1108 = **570 synonymous + 538
nonsense, zero substitutions**; 124 of the raw file's 1232 ns/syn rows
have no rebuild value; every rebuildable substitution (10,757) has a
recorded own_e_b. Cross-check: 10,757 recorded + 1,108 unrecorded =
11,865 finite identity rows = the count printed at A3 line 153.
**Correction: the count 1108 is right; the parenthetical's "1232 ...
plus substitutions" is wrong — it is the raw file's ns/syn TOTAL printed
as if it were a component of the 1108, plus a category that contributes
0 rows.** The line is informational; no gate or outcome word depends on
it (G-M1(c) compares the recorded rows only).

Consistency checks that found nothing to correct: A3 line 236's
"original ... (frozen, reproduced in G-M4)"; line 254's |diff| =
2.263e-05 against its 5e-05 gate; line 271's "The three agree: all report
GE-SURVIVES" (true, and true under both (c) constructions); the frozen
rule quoted verbatim at line 270 matches prereg s4 word for word.

Files created/modified: this entry only. The staged A3/S3/S4 outputs and
every frozen file remain untouched (append-only as mandated). No git
operations.
Anything unexpected or worth flagging: four sentence-vs-table
contradictions, all in the A3 output, **none of which changes any outcome
word or gate** — but two of them (C4-1, C4-2) change the printed p- and
rank-fractions' apparent meaning if read literally, so the caveats above
must travel with any quotation of those numbers.
---
## [SUMMARY-3B] - Mandated SUMMARY (session 3b, exact S2 order)

### 1. READ THIS FIRST - which stages completed, timed out, were skipped, or failed

**All five overnight stages completed. None timed out, none skipped, none
failed.** Evidence:
- `driver.log` line 154: `DRIVER FINISHED: S1=completed, S2=completed,
  S3=completed, S4=completed, S5=completed` at 2026-10-01T23:23:47
  (line 155: the driver's own caveat that exit 0 means finished, not that
  every stage succeeded - read `driver_state.json`, which C0 read:
  S1..S5 all `completed`).
- C0 (line 14): no driver/scorer process alive; 16 script sha256 + 3
  prereg sha256 match; rosters set-equal 400/20/100; manifests 401/21/101
  with 0 duplicates; **0 `[FAIL]` lines across all five stage logs**.
- Stage gate lines: S1 both runs clean (G-154-1/2/4/5 ok x2; 21,655 +
  1,135 passes; walls 1287.7 s + 78.6 s, within the 100-min budget); S2
  `GATES: 6/6 PASS -> G-R5 PASSES` + `GATES: 6/6 PASS -> A5e PASSES`
  (101 files, min coverage 0.9950); S3 `GATES: 10/10 PASS, 0 FAIL`
  (script 155) + `GATES: 15/15 PASS` (script 157); S4 `GATES: 5/5 PASS`;
  S5 `INTEGRITY: RESULT PASS (22 findings)`.
- Session 3b: **C0 PASS, C1 PASS, C2 PASS** (405 checks, 0 disagreements,
  exit 0), C3 and C4 executed below.

### 2. M1 (session 3a, re-verified by C2 this session - 0.000e+00 on row
construction, max|diff| 1.4e-17 on the 776 per-background rho rows, exact
on (c)'s original-null values)

| variant | outcome word (frozen s4) | rho^GE [position-cluster CI] | shrinkage | p_spec^GE full | p_spec^GE H | gradient (f) [CI] |
|---|---|---|---|---|---|---|
| **GE-ISO (primary)** | **GE-SURVIVES** | -0.122476 [-0.152648, -0.092189] | -0.389909 | 0.012658 (1/79) | 0.012658 (1/79) | +0.729343 [+0.613181, +0.803973] |
| GE-SIG | **GE-SURVIVES** | -0.122780 [-0.152914, -0.092607] | -0.393355 | 0.012658 (1/79) | 0.012658 (1/79) | +0.730540 [+0.612456, +0.805775] |
| GE-LIN-CF | **GE-SURVIVES** | -0.087618 [-0.116907, -0.059049] | +0.005675 | 0.025316 (2/79) | 0.050633 (4/79) | +0.732635 [+0.602354, +0.817335] |
| original (Phase-2 reference) | - | -0.088118 [-0.117333, -0.059511] | - | 0.025316 (2/79) | 0.050633 (4/79) | +0.731577 [+0.600332, +0.817699] |

Gradient CIs all contain the frozen reference +0.7316. **Caveat C4-1:** the
six GE `p_spec^GE` numbers are the original-rho_b-null values (staged
code), while the frozen formula names `rho_b^GE` nulls; under the literal
formula GE-ISO/GE-SIG read 0.037975 full / 0.050633 H and GE-LIN-CF is
unchanged - **all three words identical under either construction**.

### 3. G (GB1 regime map)

- **Distribution:** mean rho_b -0.009125, background-bootstrap CI
  [-0.018633, +0.000402] includes 0 -> **CENTERED** (median -0.004175,
  sd 0.096911, range [-0.307915, +0.225376], frac<0 0.5050; all 400
  backgrounds completed).
- **Four covariates (primary t25):**

| covariate | rho | CI | perm p | word |
|---|---|---|---|---|
| (a) mean abs position delta | -0.073349 | [-0.169842, +0.025742] | 0.1415 (1415/10001) | NOT RESOLVED |
| (b) single-mutant fitness W | -0.367726 | [-0.451667, -0.278739] | 0.0001 (1/10001) | ASSOCIATED |
| (c) number of partners | +0.001294 | [-0.096464, +0.099606] | 0.9810 (9811/10001) | NOT RESOLVED |
| (d) SD of e_b | -0.344868 | [-0.428355, -0.257477] | 0.0001 (1/10001) | ASSOCIATED |

- **Three threshold sensitivities (t23 / t28 / unfiltered): every word
  identical to the primary.** All four thresholds CENTERED (mean CIs
  t23 [-0.018592, +0.000401], t28 [-0.018622, +0.000392], unfiltered
  [-0.018142, +0.000421]); covariate words a NOT RESOLVED, b ASSOCIATED,
  c NOT RESOLVED, d ASSOCIATED in every column; perm p's for ASSOCIATED
  stay at 1/10001 throughout.
- **Two-sequence comparison (A7):** 20 of 20 pairs on both sequences;
  Spearman between rho_b vectors **+0.836090** (n=20); max |delta rho_b|
  0.172998 - reported, A7 defines no word.
- **Backgrounds completed:** gb1 400/400 + WT arm (401 files); two-seq
  subset gb1_project 20/20 + WT arm (21 files); 0 excluded by the
  100-partner floor; roster partner rows 410,271. A8 floor 200 exceeded
  -> never UNDERPOWERED.

### 4. R (RBD replication)

**Per target (primary frame: binding, n_bc >= 3):**

| target | rho_T [corrected CI] | p_abs | p_neg | p_pos | outcome word |
|---|---|---|---|---|---|
| N501Y | -0.090494 [-0.157685, -0.022157] excludes 0 | 0.034483 = (1+1)/(1+57) at or below 0.05 | 0.034483 | 0.982759 | **RBD-REPRODUCES** |
| E484K | -0.023931 [-0.079024, +0.030238] includes 0 | 0.521739 = (1+23)/(1+45) above 0.10 | 0.239130 | 0.782609 | **RBD-DOES-NOT-REPRODUCE** |

Two targets = two looks, no multiplicity adjustment (frozen s5).
**Sensitivities (s6: descriptive, none changes an outcome word):**
- Barcode mask: N501Y ge3/ge5 0.034483 REPRODUCES, **ge1 0.068966
  INCONCLUSIVE (disagreement)**; E484K 0.565217 / 0.521739 / 0.434783 all
  DO-NOT-REPRODUCE.
- **Shift-adjusted (6b):** N501Y p_spec_adj 0.0517 (above the 0.05 line
  by 0.001724; shift rho +0.0180 CI [-0.1902, +0.2172] includes 0);
  E484K 0.6087 (shift rho +0.2065 CI [+0.0144, +0.3895] excludes 0).
- **Locality (6c):** N501Y sequence distance rho +0.3073 CI
  [+0.0979, +0.4868] excludes 0, 3D +0.2040 CI [-0.0140, +0.4018]
  includes 0; E484K sequence CI [-0.1425, +0.3993] and 3D
  [-0.1791, +0.3509] both include 0.
- **Arm S rank fraction (6d):** N501Y 3/19 = 0.158 (signed rank 17/19);
  E484K 12/19 = 0.632 (signed 10/19) - a rank fraction, not a test.
- **Split-half (6e):** N501Y h1 0.0345 REPRODUCES / h2 0.2931
  DOES-NOT-REPRODUCE (**halves disagree**); E484K h1 0.6087 / h2 0.4565
  both DO-NOT.
- **Expression phenotype:** both targets DO-NOT at all three masks
  (N501Y/expr ge3 0.568966 - disagrees with its own bind word; E484K/
  expr ge3 0.630435 - agrees with its bind word).
- **multidms target (available):** rho_T^MD bind N501Y -0.0606 /
  E484K -0.0387; expr -0.0969 / -0.0180 - printed next to the primary,
  never replacing it, no outcome word.

### 5. M2 (multidms secondary)

- **Audit result:** MTHFR arm **NOT APPLICABLE** by the frozen A6a rule
  (0 of 13,134 MTHFR rows carry >= 2 substitutions vs the rule's >= 5,000
  -> multidms never attempted on MTHFR); RBD arm feasible with 68,789
  multi-mutant rows (`PHASE3_A6A_AUDIT_OUTPUT.txt`).
- **Environment:** `venv_multidms`, python 3.14.5; multidms 1.2.0, jax
  0.11.2, numpy 2.5.3, pandas 2.3.3, scipy 1.18.1, sklearn 1.9.1
  (G-A6-1 PASS); 52 pins frozen (G-A6-2 PASS, 2/2 barcode sha256 match).
- **Convergence (disclosed plainly):** both full fits report
  `converged=False` at the frozen fit kwargs (maxiter=500, tol=1e-06,
  warn_unconverged=False) - bind final loss 0.139129 (18.2 s), expr
  final loss 0.081072 (18.3 s), 51 trajectory rows each; the frozen
  criterion is held-out r, not optimizer convergence.
- **Held-out correlations (G-A6-4, criterion r >= 0.5 each):** bind
  0.8324 / 0.8550 / 0.8289 and expr 0.8913 / 0.8795 / 0.8584
  (Wuhan / N501Y / E484K) -> **CRITERION-MET for both phenotypes**;
  G-A6-3 timing PASS (78 s of 7200 s); S4 `GATES: 5/5 PASS`.
- **multidms target used?** **Yes** - S4 wrote `e_T_MD.csv` (15,198 rows)
  and S3's 6h joined it at the primary mask for all four target x
  phenotype combinations, printed beside the primary values as a
  secondary with no outcome word (frozen D10).

### 6. Every gate, PASS/FAIL, value

Overnight stages and session 3b gates verified directly this session;
session 3a build gates transcribed from `PHASE3A_BUILD_LOG.md`'s own
table (line 1753 ff., which its author verified by grep):

| Gate | Result | Value |
|---|---|---|
| A2 phase3_common | PASS | 40/40 checks, 0 FAIL |
| A3 M1 (frozen + gates) | PASS | 40/40 checks; GE-SURVIVES x3 |
| A4a/A4b inputs+roster | PASS | 10/10, exit 0 |
| A4c scorer tests | PASS | harness EXIT=0; deliberate G-154-2 negpath fired SystemExit=3 as designed |
| A4d G-1' hard rescore | PASS | 4/4 |
| A4e timing | PASS | 1,407.575 s = 23.46 min <= 100-min budget |
| A4f 155 full-N rehearsal | PASS | 10/10, 84.9 s |
| A5b acquisition+verify | PASS | 11/11 (G-R1, G-R2) |
| A5c e_T build | PASS with disclosed note | 9/10 overall, **9/9 deciding** (1 non-deciding FAIL at TOL 1e-5; post-hoc TOL_ROUND = 1.5e-5 for G-163-2 only, disclosed) |
| A5d roster | PASS | 8/8 |
| A5e G-R5 (hard) | PASS | 6/6 |
| A5f timing | PASS | 4,102.7 s = 45.6% of 150-min budget |
| A5g inputs / smoke | PASS | 7/7 and 14/14 |
| A5g full-mode negpath | PASS (deliberate) | exit 3, G-157-3 FAIL fired as designed |
| A5g/6h re-run after disclosed fix | PASS | 14/14, no torch |
| A6b environment | PASS | multidms 1.2.0 stack, 52 pins frozen |
| A6c smoke | PASS | 5/5, 76 s |
| A6d full | PASS | 5/5, 79 s; G-A6-4 r values above |
| A7 orchestration tests | PASS | 22/22 + owner re-run 22/22, exit 0 |
| STATE_FOR_LAUNCH sha baseline | PASS | 15/15 pairs OK, 0 mismatches |
| **S1 (154), both runs** | PASS | G-154-1/2/4/5 ok x2; 401 + 21 files; 21,655 + 1,135 passes; walls 1287.7 s / 78.6 s; 0 FAIL lines |
| **S2 (156), both blocks** | PASS | 6/6 G-R5, 6/6 A5e; 101 files; min coverage 0.9950 |
| **S3 (155)** | PASS | GATES: 10/10, 0 FAIL + G-155-99 |
| **S3 (157)** | PASS | GATES: 15/15 (incl. G-SYN planted-signal OFF-CENTER / planted-null CENTERED) |
| **S4 (158)** | PASS | GATES: 5/5 (G-A6-1/2/3/4 x2) |
| **S5 integrity** | PASS | RESULT PASS (22 findings) |
| C0 (this session) | PASS | 16 script + 3 prereg sha256 match; rosters 400/20/100 set-equal; manifests 401/21/101, 0 dups |
| C1 (this session) | PASS | bootstrap ref 40/40 max\|diff\| 0.000e+00; staged gates 10/10 + 15/15; free check 8/8 0.000e+00; fresh rescoring 6 bg + wt arm 0.000e+00 |
| C2 (this session) | PASS | 405 CHECK, 0 DISAGREE, exit 0, no torch/esm |

The only FAILs anywhere were deliberate negpaths (A4c, A5g) and A5c's
disclosed non-deciding 1e-5 miss; **0 `[FAIL]` lines in all five
overnight logs**.

### 7. Plain two-sided statement per module (no cross-module claim)

- **M1:** Within this frame, the GE expectation's correlation with
  delta_ESM is negative with a CI excluding zero and both p's at or below
  their frozen bounds -> GE-SURVIVES under all three constructions; the
  other side: the effect is modest (rho^GE -0.1225, ~39% shrinkage under
  the two bounded shapes, none under GE-LIN-CF), the printed p_spec^GE
  depends on which null set the frozen formula names (0.012658 vs
  0.037975 full - words unchanged), and the frozen word is a decision
  rule's verdict, not a mechanism claim.
- **G:** In this system the background-level rho_b distribution is
  CENTERED (mean CI includes 0), single-mutant fitness W and the SD of
  e_b are ASSOCIATED with it (negative, CIs exclude 0, perm p at the
  1/10001 floor), and mean |delta pos| and partner count are NOT
  RESOLVED; the other side: NOT RESOLVED means n cannot resolve this -
  not evidence of no relationship - the permutation p is an association
  null (beats chance pairing) rather than a re-derivation null, and all
  four words hold identically across the three partner-threshold
  sensitivities.
- **R:** At the primary frame N501Y's rho_T has a corrected CI excluding
  zero with p_abs 0.034483 at or below 0.05 -> RBD-REPRODUCES, while
  E484K's p_abs 0.521739 is above 0.10 -> RBD-DOES-NOT-REPRODUCE; the
  other side: N501Y does not hold under every pre-registered sensitivity
  (ge1 INCONCLUSIVE, split-half h2 does-not-reproduce, shift-adjusted
  0.0517 above the 0.05 line - all descriptive, none changing the
  outcome word), E484K's non-reproduction is stable across masks, halves
  and phenotype, and two targets are two looks with no multiplicity
  adjustment.

### 8. Protected files, commits, torch/esm

- **No protected file, earlier log, earlier script, or library was
  edited.** `git status --porcelain` shows the only tracked modifications
  as `.gitignore`, `README.md`, `requirements.txt` (mtimes 2026-09-26,
  before this session - pre-existing, untouched by me); no protected path
  (RESULTS.md, AGENTS.md, the planning doc, frozen preregs, any PHASE1 /
  PHASE2 / PHASE3A log, scripts <= 152, `scripts/lib/*`) appears as
  modified.
- **This session wrote only:** `PHASE3B_MORNING_LOG.md` (this log),
  `c2_independent_recompute.py`, `C2_SMOKE_OUTPUT.txt`,
  `C2_RECOMPUTE_OUTPUT.txt` (all under `docs/tasks/phase3-overnight/`),
  three `manifest_dedup_c0.csv` files (C0's dedupe; originals untouched),
  C1's scratch rescore directories outside the real output dirs, and
  stdout-only probes. Real output dirs unchanged: gb1 407 / gb1_project
  23 / rbd 107 files at C1 and again after C2 (newest entry the C0
  manifest, 2026-10-02 00:00:52).
- **Nothing was committed, staged, or pushed:** no git add/commit/push
  run; HEAD remains `4e9aed8` ("Phase 3: staged scripts and
  pre-registration extractions (READY-TO-LAUNCH)").
- **torch/esm imported only where rule 1 allows** (scoring scripts and
  gate G-1'); this session ran no scoring against real output dirs -
  C1's fresh rescore of three backgrounds per module ran scoring code in
  NEW scratch directories under explicit user authorization (disclosed
  in [C1], one model load at a time); **C2 imported neither torch nor
  esm (exit check: NONE)**; scripts 153/155/157 were never invoked
  (C2 re-derives independently of them).

### 9. The single most important entry to read first

`## [C4]` at **line 569** - the only entry that changes how the night's
numbers must be quoted: four staged sentence-vs-table contradictions in
the A3 output (C4-1's `p_spec^GE` formula-vs-nulls being the one that
touches headline p-values), **none changing an outcome word or a gate**.
`## [C2]` at line 241 is the verification that licenses everything
interpreted in `## [C3]` at line 395.

---
Session 3b ends here. **C0/C1/C2 PASS; C3 interpreted all three modules
within their frozen words; C4 recorded four append-only corrections;
nothing staged was edited; no git operations; no protected file, earlier
log, earlier script, or library touched.**
