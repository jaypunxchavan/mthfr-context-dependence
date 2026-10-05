# PHASE4A_BUILD_LOG — session 4a (build, run cached modules, stage the nights)

Template per PHASE4_STRENGTHENING.md §S1. Entries appended immediately after each task finishes.

## [SESSION HEADER] - session 4a opened
Status: IN PROGRESS
Time started: see A0 for exact `date` output
What I did: Read AGENTS.md in full (222 lines). Read docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md in full (475 lines, every section including the five frozen appendices A-E between the MECH/UTIL/GB1D/NEIGH/LADDER FROZEN BEGIN/END markers). Created this log before any other task.
Verdict: proceeding to A0 preflight.
Files created/modified: docs/tasks/phase4-strengthening/PHASE4A_BUILD_LOG.md
Anything unexpected or worth flagging: none yet.
---

## [A0] - Preflight hard stops
Status: FAIL (one hard stop: AC power; gate A0-G1 itself PASSES)
Time started / finished: Fri Oct 2 19:44:29 EDT 2026 / Fri Oct 2 19:46 EDT 2026
What I did: Ran every preflight command from Task A0 verbatim and compared each against its stated threshold.

Actual output (real numbers and quoted source text, not a paraphrase):

`date`
```
Fri Oct  2 19:44:29 EDT 2026
```

`pmset -g batt`
```
Now drawing from 'Battery Power'
 -InternalBattery-0 (id=22544483)	74%; discharging; (no estimate) present: true
```
Threshold: **AC Power, charge >= 50%**. Charge 74% >= 50% -> PASS. Source line reads `Now drawing from 'Battery Power'` and `discharging` -> **AC POWER: FAIL**.

`sysctl vm.swapusage`
```
vm.swapusage: total = 2048.00M  used = 998.81M  free = 1049.19M  (encrypted)
```
Threshold: used < 2.0 GB. 998.81M used -> PASS.

`memory_pressure | head -20` (plus tail, for the percentage)
```
The system has 17179869184 (1048576 pages with a page size of 16384).
Stats:
Pages free: 10835
...
System-wide memory free percentage: 44%
```
Threshold: free >= 35%. 44% -> PASS.

`df -h .`
```
Filesystem      Size    Used    Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   228Gi   183Gi    19Gi    91%    1.8M  196M    1%   /System/Volumes/Data
```
Threshold: free >= 8 GiB. 19Gi -> PASS.

`ps aux | grep -E "phase3_driver|phase4_driver|124_phase2|launch_phase|opencode" | grep -v grep`
```
arnavchavan       2675  10.7  2.2 445686032 371232   ??  Ss   Wed11PM  35:56.98 /opt/homebrew/Cellar/opencode-v2/2.0.12/bin/opencode serve --service
arnavchavan      43052   8.1  1.7 445552432 288112 s000  S+    7:43PM   0:03.10 opencode
arnavchavan      27714   6.4  1.2 445562784 208112 s001  S+   11:57PM  22:14.35 opencode
```
No scorer, launcher or driver alive: a targeted `ps aux | grep -E "phase3_driver|phase4_driver|124_phase2|launch_phase" | grep -v grep` returned `no scorer/launcher/driver alive` -> PASS. OpenCode windows: three opencode processes (PID 2675 `opencode serve --service` RSS 371232 KB at 19:44, re-read 249616 KB at 19:46; PID 43052 RSS 288112 KB; PID 27714 RSS 208112 KB) -> this session's window plus two others, expected, not a stop.

`venv/bin/python3 --version`
```
Python 3.14.3
```
-> PASS.

torch imports with MPS (this session only):
```
torch 2.14.0
mps available: True
mps built: True
```
-> PASS.

local ESM-2 650M checkpoint present (not loaded):
```
-rw-r--r--@ 1 arnavchavan  staff   3687 Sep 11 01:34 esm2_t33_650M_UR50D-contact-regression.pt
-rw-r--r--@ 1 arnavchavan  staff 2604537549 Sep 11 01:34 esm2_t33_650M_UR50D.pt
```
-> PASS. (Also present, relevant later: `esm2_t30_150M_UR50D.pt` 592774773 bytes; `esm2_t12_35M_UR50D.pt` NOT present.)

**Gate A0-G1** (planning doc committed and clean):
```
git log -1 --format='%H %cI' -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md
856d2f60c9d614fce7f6c5564107d72c95d73334 2026-10-02T19:43:49-04:00
git status --short -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md
(empty)
```
Hash printed, status empty -> **A0-G1 PASS**.

Logged without stopping:
- `data/processed/DATA_SHA256_MANIFEST.txt` exists: `-rw-r--r-- 1 arnavchavan staff 72579 Oct 2 15:28 data/processed/DATA_SHA256_MANIFEST.txt`
- Phase 3 scripts tracked: `git ls-files scripts/153_m1_ge_target.py scripts/164_rbd_roster.py` -> `scripts/153_m1_ge_target.py` and `scripts/164_rbd_roster.py` both listed.

Verdict: **FAIL — hard stop on AC power.** The Mac is on battery (`Now drawing from 'Battery Power'`, `74%; discharging`). Every other check passes (swap 998.81M < 2.0 GB, free memory 44% >= 35%, free disk 19Gi >= 8 GiB, no scorer/launcher/driver alive, Python 3.14.3, torch+MPS OK, 650M checkpoint present, gate A0-G1 PASS). Per Task A0 I STOP here and do not begin A1.
Files created/modified: docs/tasks/phase4-strengthening/PHASE4A_BUILD_LOG.md
Anything unexpected or worth flagging: the working tree has unrelated modified/untracked files (`.gitignore`, `README.md`, `requirements.txt` modified; `PROVENANCE.md` and various `data/processed/` files untracked) — none of them the planning doc, so A0-G1 is unaffected. Two extra `opencode` windows besides this session are open (PIDs 43052, 27714).
---

## [A0-rerun] - Preflight re-run from scratch (continuation of session 4a)
Status: PASS (every hard check passes; gate A0-G1 PASS) -> proceeding to A1
Time started / finished: Fri Oct 2 20:41:13 EDT 2026 / Fri Oct 2 20:41:27 EDT 2026
What I did: Re-ran Task A0 from scratch exactly as PHASE4_STRENGTHENING.md specifies, every command verbatim, and compared each reading against its stated threshold. The earlier [A0] entry is left untouched; this entry supersedes it only in that A0 now passes.

Actual output (real numbers and quoted source text, not a paraphrase):

`date`
```
Fri Oct  2 20:41:13 EDT 2026
```

`pmset -g batt`
```
Now drawing from 'AC Power'
 -InternalBattery-0 (id=22544483)	68%; charging; 1:47 remaining present: true
```
Threshold: **AC Power, charge >= 50%**. `Now drawing from 'AC Power'`, `68%`, `charging` -> **PASS** (the hard check that failed the first time).

`sysctl vm.swapusage`
```
vm.swapusage: total = 2048.00M  used = 990.81M  free = 1057.19M  (encrypted)
```
Threshold: used < 2.0 GB. 990.81M used -> PASS.

`memory_pressure | head -20`
```
The system has 17179869184 (1048576 pages with a page size of 16384).

Stats: 
Pages free: 3415 
Pages purgeable: 9530 
Pages purged: 10908869 

Swap I/O:
Swapins: 86218 
Swapouts: 180230 

Page Q counts:
Pages active: 252160 
Pages inactive: 249991 
Pages speculative: 825 
Pages throttled: 0 
Pages wired down: 167055 

Compressor Stats:
Pages used by compressor: 334351 
```
`memory_pressure | tail -3` (for the percentage)
```
Pageouts: 238738 

System-wide memory free percentage: 50%
```
Threshold: free >= 35%. 50% -> PASS.

`df -h .`
```
Filesystem      Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   228Gi   183Gi    19Gi    91%    1.8M  196M    1%   /System/Volumes/Data
```
Threshold: free >= 8 GiB. 19Gi -> PASS.

`ps aux | grep -E "phase3_driver|phase4_driver|124_phase2|launch_phase|opencode" | grep -v grep`
```
arnavchavan       2675  14.9  2.4 445580944 410336   ??  Ss   Wed11PM  37:00.62 /opt/homebrew/Cellar/opencode-v2/2.0.12/bin/opencode serve --service
arnavchavan      44003  12.2  1.9 445550816 313952 s001  R+    8:40PM   0:03.11 opencode
```
Targeted re-check `ps aux | grep -E "phase3_driver|phase4_driver|124_phase2|launch_phase" | grep -v grep`:
```
no scorer/launcher/driver alive
```
No scorer, launcher or driver alive -> PASS. OpenCode: two opencode processes — PID 2675 `opencode serve --service` RSS 410336 KB (this session's service), PID 44003 `opencode` RSS 313952 KB (this session's window). Only one OpenCode window is running now (the second window from the first [A0] entry, PID 27714, is gone).

`venv/bin/python3 --version`
```
Python 3.14.3
```
-> PASS.

torch imports with MPS (this session only):
```
torch 2.14.0
mps available: True
mps built: True
```
-> PASS.

local ESM-2 650M checkpoint present (not loaded):
```
-rw-r--r--@ 1 arnavchavan  staff        3687 Sep 11 01:34 /Users/arnavchavan/.cache/torch/hub/checkpoints/esm2_t33_650M_UR50D-contact-regression.pt
-rw-r--r--@ 1 arnavchavan  staff  2604537549 Sep 11 01:34 /Users/arnavchavan/.cache/torch/hub/checkpoints/esm2_t33_650M_UR50D.pt
```
-> PASS (present, not loaded here).

**Gate A0-G1** (planning doc committed and clean; the commit is the pre-registrations' timestamp):
```
git log -1 --format='%H %cI' -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md
856d2f60c9d614fce7f6c5564107d72c95d73334 2026-10-02T19:43:49-04:00
git status --short -- docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md
(no output)
```
Hash printed, status empty -> **A0-G1 PASS**.

Logged without stopping:
- `data/processed/DATA_SHA256_MANIFEST.txt` exists: `-rw-r--r--  1 arnavchavan  staff  72579 Oct  2 15:28 data/processed/DATA_SHA256_MANIFEST.txt`
- Phase 3 scripts tracked: `git ls-files scripts/153_m1_ge_target.py scripts/164_rbd_roster.py` ->
```
scripts/153_m1_ge_target.py
scripts/164_rbd_roster.py
```

Also listed for A8 (cache inventory, no load): `esm2_t30_150M_UR50D.pt` 592774773 bytes and `esm2_t30_150M_UR50D-contact-regression.pt` present; `esm2_t12_35M_UR50D.pt` **NOT present** (authorised download in A8); `esm2_t36_3B_UR50D.pt` and `esmfold_3B_v1.pt` present but not used.

Verdict: **PASS — every hard check of Task A0 passes.** AC Power 68% charging (the check that failed before), swap 990.81M < 2.0 GB, free memory 50% >= 35%, free disk 19Gi >= 8 GiB, no scorer/launcher/driver alive, Python 3.14.3, torch 2.14.0 with MPS available, 650M checkpoint present, gate A0-G1 PASS. Continuing with A1.
Files created/modified: docs/tasks/phase4-strengthening/PHASE4A_BUILD_LOG.md (this entry appended only; no earlier entry edited).
Anything unexpected or worth flagging: `esm2_t12_35M_UR50D.pt` is missing from the cache, so A8 will need the one authorised download; the working tree still has unrelated modified/untracked files (none of them the planning doc, so A0-G1 is unaffected).
---

## [A1] - Freeze the five pre-registrations
Status: PASS (gate A1-G1 PASS for all five blocks; Phase 3 preregs untouched)
Time started / finished: Fri Oct 2 20:42 EDT 2026 / Fri Oct 2 20:43 EDT 2026
What I did: Before any data was read or downloaded, extracted each frozen block byte-exactly with the five line-anchored awk commands given in the doc (no other pattern), then `wc -l`, a check for any `FROZEN` string inside the extracted files, and `shasum -a 256` against the doc's table. Also re-hashed the three Phase 3 frozen pre-registrations.

Actual output:

`wc -l docs/tasks/phase4-strengthening/prereg/*.md`
```
      26 docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md
      56 docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md
      26 docs/tasks/phase4-strengthening/prereg/MODEL_LADDER_PREREG_v1.md
      42 docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md
      32 docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md
     182 total
```
Line counts match the table (56 / 32 / 26 / 42 / 26).

`grep -c FROZEN` over the five files: `0` in every file (no marker text inside any block).

`shasum -a 256 docs/tasks/phase4-strengthening/prereg/*.md`
```
8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b  docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md
744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531  docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md
10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8  docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md
167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e  docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md
eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3  docs/tasks/phase4-strengthening/prereg/MODEL_LADDER_PREREG_v1.md
```
**Gate A1-G1: all five hashes match the doc's table exactly -> PASS.** Expected vs observed are identical for every block; nothing re-extracted, nothing edited.

Phase 3 frozen files untouched:
```
b3c82d589afc2889f60ad8626dcb24d0496f77303d0696b52db700129fd1357e  docs/tasks/phase3-overnight/prereg/GB1_REGIME_PREREG_v2.md
8965450a524e883b02ef2c970178cd242709bed1c55bd5e6ed573c1e2c2671a7  docs/tasks/phase3-overnight/prereg/RBD_REPLICATION_PREREG_v1.md
73faaa6d6b28b144f7562864a325b37225a0048085618282aebb7f22afeb542c  docs/tasks/phase3-overnight/prereg/MTHFR_GE_TARGET_PREREG_v1.md
```
All three match the values in the doc.

Verdict: PASS. The five pre-registrations are now frozen on disk before any data was touched.
Files created/modified: docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md, UTILITY_PREREG_v1.md, GB1_LOCALITY_PREREG_v1.md, NEIGHBOUR_ARM_PREREG_v1.md, MODEL_LADDER_PREREG_v1.md (all new); log entry appended.
Anything unexpected or worth flagging: none.
---
## [A2] - scripts/lib/phase4_common.py + its gate (script 165)
Status: PASS (full run: 70/70 checks PASS, 0 FAIL, exit 0; smoke: 68/69 with only the intentional CI SKIP)
Time started / finished: Fri Oct 2 20:55 EDT 2026 / Fri Oct 2 21:06 EDT 2026
What I did: Wrote `scripts/lib/phase4_common.py` (the A2 shared library: all ten required function groups plus re-exports from phase3_common / phase2_diag4 / stats_ext, with the pre-registered interpretation decisions I1-I8 in its docstring) and `scripts/165_phase4_common_gate.py` (A2-G1 / A2-G2 / A2-G3, pre-registered docstring). Smoke ran first at N_BOOT=300; four defects were found and fixed there, all disclosed below and in the gate's own docstring; then the full run at N_BOOT=10000 SEED=0, redirected to `docs/tasks/phase4-strengthening/PHASE4_A2_FULL_OUTPUT.txt`.

**Smoke-phase fixes (AGENTS 6 disclosure; all made before any Phase 4 number existed, none moved a threshold toward passing):**
1. `own_eb_from_arrays` indexed `rebuild_interaction_fit(raw)["e_b"]` -- KeyError. The project's own convention (scripts 17/33/47) is `fit["e2"]["e_b"]`. Fixed to that.
2. The whole-placebo fast AND reference paths ranked arrays containing the per-background NaNs: scipy's `rankdata` propagates a single NaN through the whole rank vector (verified: `rankdata([1, nan, 3, 4])` -> four NaNs) and `spearmanr` returns NaN outright, so every rho was NaN and the identity gate failed (`p_spec 0.2 target 1.0`, `k 0 target 4`, `rho_A nan`). Both paths now mask to each background's finite rows (`_rho_masked`), which is what "rho_b over a background's rows" means when each background's rows exclude its own position. The reference masks identically, so the draw-by-draw comparison still tests the arithmetic, not the mask.
3. `simulate_rho` used ONE array for both the m NOISE SD and the SE COLUMN the pipeline weights by. Frozen G-M4 says "every noise term zero ... the pipeline returns the recorded own_e.b"; scripts 106 (line 340) and 17 feed the RECORDED Mse into the fit, so zeroing the weights would not return the recorded own_e.b (it produced NaN instead: se=0 in the WLS). Split off `m_noise` (default `m_se`, so frozen M-3's `N(0, m_se_ic^2)` is unchanged); G-M4 passes `m_noise=zeros` with `m_se` left recorded. This is a decision recorded in `zero_epistasis_draw`'s docstring, made on the smoke run.
4. Two of THIS GATE's own toy expectations were wrong against the frozen text and were corrected **to the frozen text**: (a) NEIGH section 2 defines C1 as `d3 <= 12 AND dseq <= 20` (the doc line 411) -- my toy had asserted `dseq 40 -> C1`, which the library correctly refused; (b) a CI touching zero (0.0, 0.05) does NOT exclude zero, the same convention as M-1 (`_excludes_zero` is `lo > 0 or hi < 0`) -- my toy had asserted it does. Both toys now probe the frozen boundary (20 / 20.000001 / 40 / 40.000001) and the touch-zero case explicitly.

Smoke after the fixes: `68/69 checks PASS, 1 FAIL (1 of the FAILs are smoke SKIPS)` -- only the intentional N_BOOT!=10000 CI SKIP, exit 0.

Full run (foreground, `N_BOOT=10000 SEED=0 venv/bin/python3 scripts/165_phase4_common_gate.py > docs/tasks/phase4-strengthening/PHASE4_A2_FULL_OUTPUT.txt 2>&1`), exit 0, 51.4s.

Actual output (verbatim, from PHASE4_A2_FULL_OUTPUT.txt, 190 lines, sha256 `f18ffce333df6cadb1007c73a7b26cbcd8fc48feddfb1e7982e678fbcd6cada2`):

```
==============================================================================
A2 -- GATES FOR scripts/lib/phase4_common.py (script 165)
==============================================================================
N_BOOT = 10000   SEED = 0   N_REF = 500   N_REF_PRE = 20
RESAMPLING UNIT in this script: POSITION CLUSTERS (the anchor statistic is inside one background).  No background-level resampling here.
DECISION RULE (pre-registered): any A2-G1/A2-G2/A2-G3 sub-gate FAIL -> phase4_common is not trusted for M, U, G, N, L; exit 3.  Thresholds are never loosened; N is never raised.
NO torch / esm / thermompnn is imported here (rule 1).

------------------------------------------------------------------------------
GATE A2-G1 -- script 159 rerun UNCHANGED (HARD)
------------------------------------------------------------------------------
  running: N_BOOT=10000 SEED=0 /Users/arnavchavan/Desktop/mthfr-context-dependence/venv/bin/python3 159_phase3_common_gate.py
  ---- subprocess tail (verbatim) ----
    [PASS] A2-G2(i) identity, (ii) ANCHOR ROWS: every-cluster-once corrected -0.08811806424891734, reference -0.08811806424891734, point -0.08811806424891734; max|diff| = 0.000e+00 (gate < 1e-12)
    [PASS] A2-G2(ii/iii) draw-by-draw, (ii) ANCHOR ROWS: 500 draws, max|corrected - reference| = 0.000e+00 (gate < 1e-12)
    [PASS] A2-G2(i) identity, (iii) RESTRICTED (positions removed): every-cluster-once corrected -0.0810084432806544, reference -0.0810084432806544, point -0.0810084432806544; max|diff| = 0.000e+00 (gate < 1e-12)
    [PASS] A2-G2(ii/iii) draw-by-draw, (iii) RESTRICTED (positions removed): 500 draws, max|corrected - reference| = 0.000e+00 (gate < 1e-12)
    40/40 checks PASS, 0 FAIL (0 of the FAILs are smoke SKIPS).
  LIMITATIONS (printed, per AGENTS 6): this gate REPRODUCES cached Phase 1/2 numbers through the new generic API -- it validates the library code (reproduction is not replication, AGENTS 6), it is not independent evidence for any claim, and it produces no new inference.  The bootstrap it exercises resamples POSITION CLUSTERS only.  The corrected routine is imported from scripts/lib/phase2_diag4.py (unmodified); script 144's routine is never used.  A smoke run (N_BOOT != 10000) cannot PASS A2-G1 because sub-gate (k) is skipped.
  GATE PASS -- A2-G1 and A2-G2 both pass; the generic library is trusted for the M1/GB1/RBD analyses per the planning doc's Task A2 decision rule.
  Elapsed 32.9s
  ---- end subprocess ----
  [PASS] A2-G1 script 159 prints 40/40 PASS: returncode 0; found '40 checks PASS, 0 FAIL' = True (target: the line '40/40 checks PASS, 0 FAIL', exit 0)

------------------------------------------------------------------------------
GATE A2-G2 -- cached MTHFR numbers through phase4_common (HARD)
------------------------------------------------------------------------------
  [PASS] A2-G2(a) rho table sha256: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796  (target e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796)
  [pdg.build] 0.8s -- script 125's cached construction, imported (AGENTS 2), not reimplemented
  [PASS] A2-G2 rows / positions (target 10,757 / 654): got 10757 rows / 654 positions; target 10757 / 654
  [PASS] A2-G2(b) A222V rho full (task32 via p4c.spearman): got -0.08811806424891734 target -0.088118064 |diff| = 2.489e-10 (gate < 1e-09)
  [PASS] A2-G2(b) A222V rho full (script 125 rows via p4c.spearman): got -0.08811806424891734 target -0.088118064 |diff| = 2.489e-10 (gate < 1e-09)
  [PASS] A2-G2(b) the two sources agree with each other: |diff| 0.000e+00 (AGENTS 5 column identity)
  [PASS] A2-G2(c) H positions (target 455): got 455 target 455 (7526 anchor rows on H)
  [PASS] A2-G2(c) A222V rho H: got -0.09002168303339808 target -0.090021683 |diff| = 3.340e-11 (gate < 1e-09)
  [PASS] A2-G2(c) A222V rho H (pdg.point_rhos_H cross-check): got -0.09002168303339808 target -0.090021683 |diff| = 3.340e-11 (gate < 1e-09)
  [PASS] A2-G2(d) p_spec(neg) full: p = (1+1)/(1+78) = 0.02531645569620253 target 0.02531645569620253 (2/79); k = 1 target 1; beaters ['G_P254F'] target ['G_P254F']
  [PASS] A2-G2(e) p_spec(neg) H: p = (1+3)/(1+78) = 0.05063291139240506 target 0.05063291139240506 (4/79); k = 3 target 3; beaters ['AV_195', 'AV_220', 'G_P254F'] target ['AV_195', 'AV_220', 'G_P254F']
  [PASS] A2-G2(f) rho(delta, S_W): got -0.32376573717755663 target -0.32376573717755663 |diff| = 0.000e+00 (gate < 1e-12)
  [PASS] A2-G2(g) rho(own_e.b, S_W): got 0.085391652432165 target 0.085391652432165 |diff| = 0.000e+00 (gate < 1e-12)
  [PASS] A2-G2(h) partial rho controlling S_W (p4c.partial_spearman): got -0.06414804421216103 target -0.06414804421216103 |diff| = 0.000e+00 (gate < 1e-12)
  [PASS] A2-G2(h) retention |partial|/|raw| (3 dp): got 0.728 target 0.728 |diff| = 0.000e+00 (gate < 1e-15)
       retention full precision = 0.7279783635618071
  [PASS] A2-G2(i) two-covariate partial (4 dp): got -0.0829 target -0.0829 |diff| = 0.000e+00 (gate < 1e-15)
       full precision = -0.08289332817238883 (Phase 1 L2 printed -0.0829)

------------------------------------------------------------------------------
A2-G2 REFERENCE BOOTSTRAP on the real anchor rows (PHASE4 rule 6)
------------------------------------------------------------------------------
  [PASS] rule 6 identity: every position once == point estimate: every-once -0.08811806424891734 point -0.08811806424891734 |diff| 0.000e+00 (gate < 1e-12)
  [PASS] rule 6 draw-by-draw reference (500 draws): max|corrected - reference| = 0.000e+00 (gate < 1e-12)
  [PASS] rule 6 Phase 1 CI lo: got -0.1173334458953319 target -0.1173334458953319 |diff| = 0.000e+00 (gate < 1e-09)
  [PASS] rule 6 Phase 1 CI hi: got -0.05951138449511738 target -0.0595113844951173 |diff| = 7.633e-17 (gate < 1e-09)
       (10000 finite draws, N_BOOT=10000, SEED=0; the routine is phase2_diag4's, imported)
```

A2-G3 (50 toy sub-gates) -- every one PASS. The gate table's decisive lines, verbatim:

```
  [PASS] A2-G3 re-exports are the imported objects: p4c.spearman/p_spec/pos_cluster_boot/reference_boot are phase3_common's objects; p4c.pos_cluster_boot_corrected is phase2_diag4's object (script 144's routine is never importable from this path)
  [PASS] A2-G3 harness == the project's rebuild_interaction_fit: max|diff| 0.000e+00 (gate < 1e-12); own_eb_from_arrays must be the unmodified pipeline, not a re-derivation
  [PASS] A2-G3 G-M4 simulation identity (zero noise, E = observed m): simulate_rho -0.07692307692307693 direct -0.07692307692307693 |diff| 0.000e+00 (gate < 1e-12)
  [PASS] A2-G3 whole_placebo IDENTITY (every position once == observed, frozen G-M7): p_spec 1.0 target 1.0; k 4 target 4; rho_A 0.21930937279774487 target 0.21930937279774487
  [PASS] A2-G3 whole_placebo DRAW-BY-DRAW reference (20 draws): max|new - reference|: rho_A 0.000e+00, rho_N 0.000e+00, k 0.0, p_spec 0.000e+00 (gate < 1e-12; the reference rebuilds position -> rows with flatnonzero and calls scipy per background)
  [PASS] A2-G3 whole_placebo DETERMINISM (same seed): rho_A identical True, k identical True
  [PASS] A2-G3 partial == closed form (1 control): library 0.6897973159953645 closed form np.float64(0.6897973159953646) |diff| 1.110e-16 (gate < 1e-12)
  [PASS] A2-G3 partial == closed form (2 controls, matrix inversion): library 0.6934320177009149 closed form 0.6934320177009148 |diff| 1.110e-16 (gate < 1e-12)
  [PASS] A2-G3 decomposition PLANTED PURE-BETWEEN: rho_between 1.0 target 1.0; rho_within 0.0 target 0.0
  [PASS] A2-G3 decomposition PLANTED PURE-WITHIN: rho_within 1.0 target 1.0; rho_between 0.0 target 0.0
  [PASS] A2-G3 cell_labels C1/C2 dseq boundary (frozen NEIGH section 2: C1 is dseq <= 20, C2 is dseq > 40): got ['C1', '', '', 'C2', ''] target ['C1', '', '', 'C2', '']
  [PASS] A2-G3 balanced_pr_curve coordinates == sklearn's weighted precision_recall_curve (recall 1..end): max|diff| recall 0.000e+00, balanced precision 1.110e-16 (gate < 1e-12)
  [PASS] A2-G3 balanced_pr coordinates == sklearn's roc_curve path (second independent sklearn path): max|diff| 0.000e+00 (gate < 1e-12); chance level 0.5 = 0.5
  [PASS] A2-G3 min_detectable_effect interpolation (I5): neg 0.09375 pos 0.09375 headline 0.09375 target 0.09375
  [PASS] A2-G3 word_distance (NEIGH section 6): ... and a CI TOUCHING zero (0.0, 0.05) does NOT exclude it, same convention as M-1 -- _excludes_zero is lo > 0 or hi < 0
```
(all five frozen word blocks, every boundary case incl. p = 0.05 and 0.10 exactly, |NB| = 30 vs 29, and the AUROC/balanced-PR sklearn cross-checks are in the full output file)

Final lines, verbatim:
```
  70/70 checks PASS, 0 FAIL (0 of the FAILs are smoke SKIPS).

LIMITATIONS (printed, per AGENTS 6): A2-G2 REPRODUCES cached Phase 1/2 numbers through the new library -- it validates the library code (reproduction is not replication), it is not independent evidence for any claim, and it produces no new inference.  A2-G3's toys fix the arithmetic, not the biology.  Every bootstrap exercised here resamples POSITION CLUSTERS; the corrected routine is phase2_diag4's, imported unmodified; script 144's routine is never used.  A smoke run (N_BOOT != 10000) cannot PASS A2.

GATE PASS -- A2-G1, A2-G2 and A2-G3 all pass; phase4_common is trusted for the Phase 4 analyses per Task A2's decision rule.
Elapsed 51.4s
```

Every expected value printed beside its target matched; nothing was forced into agreement. The Phase 1 CI reproduced exactly (`lo` diff 0.000e+00, `hi` diff 7.633e-17 < 1e-9).

Verdict: **PASS.** `phase4_common` is trusted for Modules M, U, G, N, L per Task A2's decision rule.
Files created/modified: `scripts/lib/phase4_common.py` (new), `scripts/165_phase4_common_gate.py` (new), `docs/tasks/phase4-strengthening/PHASE4_A2_FULL_OUTPUT.txt` (new), log entry appended. No existing script or library modified; no `git add`/commit.
Anything unexpected or worth flagging:
- **Script-numbering deviation (disclosed):** the doc's Task A4 parenthetical says "scripts 165 and next" for the MECH block, but A2 came first and took 165 for the gate above. MECH scripts therefore start at **166**. The numbering rule ("next free number") was followed; only the parenthetical's label is off by one.
- **Open interpretation for A4 / M-3 (`sw_i`):** frozen M-3 says `sw_i` is "the per-variant WT-background standard error **if the project's data carries one**; if it does not, `sw_i = 0` (PRIMARY) and a sensitivity uses `sw_i` = the median m_se". It is not yet decided whether the atlas's raw `w12.se ... w200.se` columns count as "the per-variant WT-background standard error" in the sense M-3 means (they are per-condition WT-arm SEs from the fit, not a per-variant WT-background fitness SE). This must be decided and stated in M's own output BEFORE M is run; if they do not qualify, PRIMARY is `sw_i = 0` with the median-`m_se` sensitivity. Not resolved here.
---
## [A3] - Module S: the sign convention note (script 166)
Status: PASS (single run: 49/49 checks PASS, 0 FAIL, exit 0; no resampling, no model, no network -- N_BOOT is deliberately not read, so there is no smoke/full split for this script)
Time started / finished: Fri Oct 2 21:06 EDT 2026 / Fri Oct 2 21:33 EDT 2026
What I did: wrote `scripts/166_sign_convention.py` with a pre-registered docstring (the S-1..S-5 decision rules, the example-selection rule and the limitations were stated before the first run; on the first mismatch the script prints the computed value beside the target, prints the summary and exits 1 -- nothing was tuned toward agreement), then ran it to a record file. It (S-1) quotes how own_e.b and delta are defined with file **and line number**, printing the code line found at the cited line beside the planning document's expectation and asserting the quoted tokens are on that line; (S-2) computes the worked example from the data with row accounting at every filter; (S-3) prints the descriptive 2x2 and recomputes the two Phase 1 C1 Spearmans four independent ways against the doc's targets; (S-4) quotes the GB1 and RBD sign conventions and states for each whether a positive value means fitter/tighter than expected, reporting UNAVAILABLE rather than inferring where no local document says so; (S-5) writes `SIGN_CONVENTION.md` and re-reads it, parsing every number back out to compare with an independent pandas/numpy recomputation.

Actual output: `docs/tasks/phase4-strengthening/PHASE4_A3_OUTPUT.txt` (454 lines, sha256 `9ff1fac51dd93221edac822462466d0242edb0ad2266a48728e911d6dc7dc21a`). Final lines, verbatim:
```
A3 SUMMARY: 49 checks PASS, 0 FAIL  (ALL CHECKS PASSED)
elapsed 0.3s
```

S-1 -- 14 quote checks, each printing code beside expectation, e.g.:
```
    scripts/lib/own_context.py:163
      code | resid = np.where(valid, m_score - expected, np.nan)
      doc  | the residual subtracts the expectation from the observed A222V-arm score
  PASS  S-1i the residual is m_score - expected
    scripts/lib/own_context.py:165
      code | e_b, e_r, df = wls_line(resid, m_se, concs, valid)
      doc  | own_e.b = wls_line(resid, m_se, concs, valid)'s intercept
    docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md:36
      code | One-sided empirical p (direction pre-stated negative, as for the anchor):
  PASS  S-1n the tail registered in PHASE2_PREREG.md is negative (read only)
```
The other eleven cover `rebuild_interaction_fit` (stats_ext 63/84/87), `wls_line` (own_context 48/49/64), `fit_interaction`'s multiplicative expectation (148/157), both independent definitions of delta (scripts 45:97 and 12:29) and its printed meaning `S(v|A222V) - S(v|WT)` (12:30).

S-2 -- worked example (computed, not typed):
```
  PASS  S-2a analysis set = 10,757 rows at 654 positions (planning 143)
  median se_e_b = 0.062873954434773; strictly below: 5,378; exactly at the median: 1 (excluded by 'below the median')
  PASS  S-2e rebuilt own_e.b == recorded own_e_b (identity)   max|diff| = 2.220e-16 over 10,757 rows (tolerance 1e-12)
  PASS  S-2f independent numpy closed-form intercept == recorded own_e_b   max|diff| = 7.094e-14 over 10,757 rows (w*x*x here vs w*(x**2) in wls_line: summation-order only)
  PASS  S-2g independent SE == recorded se_e_b (library path too)   closed-form max|diff| = 1.275e-13, library max|diff| = 2.220e-16 over 10,757 rows
  PASS  S-2h stored delta == S_A - S_W recomputed (identity)   max|diff| = 2.220e-16
  PASS  S-2d no zero-valued sign is silently grouped (delta, own_e.b)   delta == 0: 0; own_e.b == 0: 0 (so the 2x2 has no zero cell)
```
The six variants (3 most positive / 3 most negative own_e.b inside se_e_b < median), with every field the task lists printed per variant -- position, wt/mut, S_W, S_A, delta, base functionality, the four observed A222V-arm scores, the four expectations, the four residuals, own_e.b and its se (recorded beside the independent closed form):
```
    p.Arg134Gly  position 134  R -> G   own_e.b = 0.8636330028276065   se_e.b = 0.0387464462219277
    p.Asp100Met  position 100  D -> M   own_e.b = 0.840923163611355    se_e.b = 0.062828666636335
    p.Thr129Ser  position 129  T -> S   own_e.b = 0.8114199904645375   se_e.b = 0.04203245058859071
    p.Asn118Pro  position 118  N -> P   own_e.b = -0.7243006804322979  se_e.b = 0.0493686762635291
    p.Phe60Ala   position 60   F -> A   own_e.b = -0.7100191685367429  se_e.b = 0.0443483912273545
    p.Lys27Ile   position 27   K -> I   own_e.b = -0.6998409599000717  se_e.b = 0.0486859594907699
```
(one plain sentence per variant follows each block in the record file, built from the computed signs only; e.g. p.Asn118Pro: "delta is positive ... own_e.b is negative ... the model's shift and the measured interaction point in OPPOSITE directions").

S-3 -- descriptive 2x2 (numbers only; no interval, no p-value, one dataset):
```
  PANEL overall (analysis set)   n = 10,757
    rows = own_e.b < 0   n =  5,524   mean(delta) = +0.040691443
    rows = own_e.b > 0   n =  5,233   mean(delta) = +0.024508573
    rows = delta < 0     n =  3,787   mean(own_e.b) = +0.033116770
    rows = delta > 0     n =  6,970   mean(own_e.b) = +0.003779363
  PANEL tertile T1 lowest S_W  n = 3,586   mean(delta): own_e.b<0 +0.069856083 / own_e.b>0 +0.060545678
  PANEL tertile T2 middle S_W  n = 3,585   mean(delta): own_e.b<0 +0.042277475 / own_e.b>0 +0.028561900
  PANEL tertile T3 highest S_W n = 3,586   mean(delta): own_e.b<0 +0.001739282 / own_e.b>0 -0.007075489
```
Every panel's two partitions account for all of its rows (gates S-3a/S-3c; tertile bin sizes 3,586 / 3,585 / 3,586). The three rhos, four routes each (project `spearman`, `scipy.stats.spearmanr`, `pandas.corr(method='spearman')`, numpy-only average-rank Pearson), against the doc's targets:
```
    project spearman / scipy / pandas / numpy rho(delta, S_W)   = -0.32376573717755663  (4 of 4 identical; TARGET -0.32376573717755663, 4 dp task target -0.3238)  |diff| 0.000e+00
    project spearman / scipy / pandas = 0.085391652432165, numpy = 0.08539165243216501  (TARGET 0.085391652432165, 4 dp 0.0854)  spread 1.388e-17
    rho(delta, own_e.b) = -0.08811806424891734 (all four)  TARGET -0.088118064 (planning 144/314, 9 dp)  worst deviation 2.489e-10 < 1e-09
```

S-4 -- cross-system sign statements (quoted, never inferred):
```
    MTHFR atlas own_e.b: POSITIVE = observed ABOVE the multiplicative expectation -> better than expected.  Quoted: own_context.py lines 148/157/163/165.
    GB1 e_b: POSITIVE = measured double-arm fitness ABOVE the multiplicative expectation of the two singles (155:21, 155:394, 73:58, 128:135) on the selection-enrichment scale (155:24) -> fitter than expected.
      files under scripts/ and docs/ containing the literal phrase 'fitter than expected': 2 -> ['scripts/166_sign_convention.py', 'docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md']
      (that search is not a quotation: of the hits, one is this task's own instruction line in PHASE4_STRENGTHENING.md and one is this script's search code -- neither states a sign convention.  The GB1 direction above therefore rests on the quoted formulas.)
    RBD e_T / delta_bind: ARITHMETIC (quoted) = positive means the mutation's value ABOVE the wild-type row's / Wuhan's value (163:31, 163:35, 163:47, README:22).
      DIRECTION WORD ('stronger' / 'tighter' / 'weaker'): UNAVAILABLE locally.
  PASS  S-4n RBD direction word is UNAVAILABLE because the repository's column descriptions are genuinely absent from disk
        absent: data/external/rbd_starr2022/data/README.md, data/external/rbd_starr2022/results/summary/summary.md
```
`bc_binding.csv`'s own header (`"library",...,"log10Ka"`) and script 158:29 (`bind = bc_binding.csv / log10Ka`) are quoted too; the file inventory of `data/external/rbd_starr2022/` is printed in the record file (11 files, neither description among them).

S-5 -- `SIGN_CONVENTION.md`, 32 lines (limit 40), sha256 `dc856a016197b12da3a9fbf8c74dcbf93bedccb89f5a45e0e8fed097f856d4d8`. Eleven numbers were written from one source and re-derived from another; the script then re-read the file and parsed each `label = value` back out:
```
    n_rows = 10757 / n_positions = 654 / rho(delta, own_e_b) = -0.08811806424891734 / rho(delta, S_W) = -0.32376573717755663 / rho(own_e_b, S_W) = 0.085391652432165
    example p.Asn118Pro: position = 118, S_W = -14.296979989856482, S_A = -14.25630108639598, delta = 0.0406789034605008, own_e_b = -0.7243006804322979, se_e_b = 0.0493686762635291
  PASS  S-5c every number parsed back out of the note equals its independent recomputation   11 labels, each matched exactly once
  PASS  S-5d SIGN_CONVENTION.md is at most forty lines   32 lines written
```
The note's sign sentence (the text modules must quote per planning line 241) reads: *delta = S(v|A222V) - S(v|WT) ... positive delta means the model scores the substitution as MORE favourable in the A222V background ...; own_e_b = observed A222V-arm score minus the multiplicative no-interaction expectation, taken as its concentration-weighted intercept ...; A NEGATIVE rho means the model's background shift runs OPPOSITE to the measured shift ... direction only; no magnitude, mechanism or causal claim follows from the sign.*

Verdict: **PASS.** `SIGN_CONVENTION.md` is frozen-by-generation for later modules; the sign sentence above is the text C3 must restate wherever a rho is discussed.
Files created/modified: `scripts/166_sign_convention.py` (new), `docs/tasks/phase4-strengthening/SIGN_CONVENTION.md` (new), `docs/tasks/phase4-strengthening/PHASE4_A3_OUTPUT.txt` (new), `docs/tasks/phase4-strengthening/PHASE4_A3_ATTEMPT1_FAIL_OUTPUT.txt` (new, the failed first attempt), log entry appended. No existing script, library, planning document or Phase 2 preregistration modified (PHASE2_PREREG.md and the planning doc were only read); no `git add`/commit.
Anything unexpected or worth flagging:
- **Script numbering (supersedes A2's forward note):** A3 took **166**, so the MECH block of Task A4 starts at **167** -- not the "166" the A2 entry forecast. The doc's A4 parenthetical ("scripts 165 and next") is now off by two; the "next free number" rule was followed each time.
- **First attempt failed on a bug (disclosed, output retained):** run 1 died with `AttributeError: 'Series' object has no attribute 'eb_cf'` because the closed-form columns had been merged into the analysis frame but not into the six-variant worked-example frame. Fixed before any passing run; the failed output is kept as `PHASE4_A3_ATTEMPT1_FAIL_OUTPUT.txt` rather than overwritten. Two later passes changed only explanatory print statements (a clarification that the two "fitter than expected" phrase hits are the task's own instruction line and this script's search code, and the wording of the RBD-absence reason); no gate, target or number changed in any of them -- every passing run printed `49 checks PASS, 0 FAIL`. The record file above is from the final script version (`scripts/166_sign_convention.py` sha256 `88ddd211ec85de3160009fdd71c0828d887b85cde477d450082290b481f4d984`).
- **RBD direction word is UNAVAILABLE locally -- open question, needs a decision:** the repository's own column descriptions (`data/README.md`, `results/summary/summary.md`) were never fetched, and fetching them is not authorised in Phase 4 (only `esm2_t12_35M_UR50D` is). Worse, the local wording is internally inconsistent: `bc_binding.csv`'s header and script 158:29 say `log10Ka`, while the frozen RBD block quoted at 163:11 says `log10 KD` -- inverse relationships -- so no direction word ("stronger"/"tighter") is asserted for RBD. This does not block A4 (Module M is MTHFR-only) but it does block any cross-system direction claim for RBD. Escalate rather than infer; the script's own check S-4n fails loudly if either description ever appears on disk.
- **Descriptive only:** the S-3 panels are cross-sectional summaries of one dataset with no resampling and no p-value; the tertile-3 sign flip in `mean(delta)` (+0.001739282 vs -0.007075489) is reported as a number, not as a finding, and the note says so ("direction alone, on one dataset, with no interval attached").
- **No smoke run exists for A3** (nothing is resampled or bootstrapped, so `N_BOOT` is not read and could not change the result); the single recorded run is the run.
---

## [A4] - Module M: the mechanism-matched analyses (script 167)
Status: PASS (smoke: 63/64 checks PASS, the only FAIL the intentional G-M3(iii) smoke SKIP, exit 0; full run: **65/65 checks PASS, 0 FAIL**, exit 0)
Time started / finished: Fri Oct 2 22:26 EDT 2026 (first smoke attempt) / Fri Oct 2 22:50 EDT 2026 (full run, 1202.4 s)
What I did: wrote `scripts/167_mech_anchor.py` (1,772 lines) implementing the frozen `prereg/MECH_ANCHOR_PREREG_v1.md` block (M-1..M-6, gates G-M0..G-M7) plus two EXTRA gates stricter than the frozen text (G-XFOLD, G-ALIGN). The docstring was written before the first run and carries the nine pre-registered interpretation decisions **M-DEC1..M-DEC9** and the report-set decisions, all printed in the output *before the first M draw exists*. Cached data only: no torch / esm / thermompnn imported, no model scored, no network. Everything reusable is imported, never re-derived (`pdg.build`/`pdg.rho_table`/`pdg.usable_rows` = script 125's cached construction, `p3d` D3 loader, `p3c` Phase 1/3 statistics, `p4c` = the A2 library); the only new machinery is the position-cluster draw loop for a CUSTOM statistic and its slow scipy reference, kept in this script (AGENTS 7: `scripts/lib/*` untouched). Frozen sources are quoted **verbatim from disk at runtime** with file and line number (`stats_ext` 63-88, `own_context` 48-66 and 143-187, and `SIGN_CONVENTION.md` 6-15, the sign sentence), and the whole 56-line frozen block is re-printed at startup after its sha256/line-count gate.

Actual output: `docs/tasks/phase4-strengthening/PHASE4_A4_FULL_OUTPUT.txt` (1,171 lines, sha256 `d95426bdabbba94da1bbc35a8605c6927f51302641cb27cc12d3deb0ce9c77be`). Final lines, verbatim:
```
  Elapsed 1202.4s

GATE PASS -- G-M0..G-M7 plus G-XFOLD and G-ALIGN all pass; the frozen outcome words above are the result of this block.
```
Smoke record: `PHASE4_A4_SMOKE_OUTPUT.txt` (sha256 `c10aa3b5e5de5a363bddd120a14b6eaaeac423d0a2e233da5f89b9e06e3a9908`, 101.0 s, `N_BOOT=300 N_SIM=100 N_PLANT=100 N_PERM=100 N_STAB=100 N_REF=100`); every word it printed was marked PROVISIONAL and G-M3(iii) printed SKIPPED, as pre-registered. Script sha256 `122d95ff58a5c1e5bfe7e91e4a59349c5c6d2ab6cb720b77a20ef77c2a410c13`.

Gates -- all 65 hard checks, every target recomputed independently and printed beside the frozen value (never forced to agree). Highlights:
```
  [PASS] G-M0 prereg sha256 8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b, 56 lines; rho table e397a442...63796; 3D table 69914df9...312de; 6FCX.pdb 95133130...48fbf; script 153 e9fd90af...b5133; m1_own_e_b_ge.csv 0dd63b4a...44523; m1_fitted_expectations.csv e353330d...d9915
  [PASS] G-M0 structure: 96 backgrounds, |N| = 78, arms G40/V38/S18; frame 10,757 rows / 654 positions, H = 455 positions / 7,526 rows; 67 resolved nulls; D3 loader reproduces stored d3_CA max|diff| = 4.965e-07 (gate < 1e-6)
  [PASS] G-XFOLD fold vector / position / hgvs identical to script 153's saved table; aggregate(E_iso) vs saved own_e_b_ge_iso max|diff| = 2.220e-16 over 11,865 finite rows, 0 NaN disagreements; all 20 isotonic transition lists max|diff| = 2.220e-16
  [PASS] G-ALIGN 96 backgrounds re-joined: position mismatches 0, own_e_b diff 0, delta diff 0, rho_full/rho_H diff 1.388e-17; the 97 x 10,757 delta matrix reproduces every cached rho_b to 1.388e-17 and row 0 == the frame's delta exactly
  [PASS] G-M1 rho_A222V = -0.08811806424891734 (target -0.088118064, |diff| 2.489e-10) from two independent columns agreeing 0.000e+00; H = -0.09002168303339808 (target -0.090021683); p_spec(neg) full = 2/79 = 0.02531645569620253 beaters ['G_P254F']; H = 4/79 = 0.05063291139240506 beaters ['AV_195','AV_220','G_P254F'] -- all exact
  [PASS] G-M2 partial controlling S_W = -0.06414804421216103 (|diff| 0.000e+00); two-covariate partial = -0.0829 at 4 dp (full precision -0.08289332817238883)
  [PASS] G-M3(i) identity x4 (anchor, partial, stratified, both decomposition components) each < 1e-12; G-M3(ii) draw-by-draw vs independent references: partial 1.4e-16, two-covariate 1.9e-16, stratified 2.8e-17, decomposition < 1e-12, imported bootstrap vs reference_boot < 1e-12, whole-placebo vs slow reference rho_A 1.4e-17 / rho_N 2.8e-17 / k exact on both views (N_REF = 500, placebo capped at 50 draws, disclosed)
  [PASS] G-M3(iii) Phase 1 CI lo -0.1173334458953319 |diff| 0.000e+00, hi -0.05951138449511738 |diff| 7.633e-17 (gate < 1e-9, N_BOOT = 10000, the imported corrected routine)
  [PASS] G-M4 zero-noise pipeline returns recorded own_e.b: 10,757 rows, max|diff| = 2.220e-16, 0 rows > 1e-12, 0 recorded rows missing; every M-3 (3 runs x 1000 draws) and M-4 (9 x 200 draws) draw kept exactly 10,757 rows
  [PASS] G-M5 planting response: 8/8 adjacent pairs non-decreasing within 2 combined SEs (M-DEC6's pre-registered rule)
  [PASS] G-M6 toy gates: stratified 1.0 / 0.5 / dropped-stratum-renormalised, decomposition planted pure-between 1.0/0.0 and pure-within 0.0/1.0, min_rows exclusion 6 of 7 -- library and scipy reference agree everywhere
  [PASS] G-M7 every-position-once: rho_A full -0.088118064 / k = 1 / p = 2/79 and H -0.090021683 / k = 3 / p = 4/79 with the named beaters
```
Analysis-set accounting printed in the output (AGENTS 5): raw fit frame 13,134 rows / 655 positions -> task32 analysis table 11,344 rows (own_e_b finite 10,757) -> anchor frame 10,757 rows / 654 positions; H 7,526 / 455; off-frame raw rows 2,377; deciles of S_W cut once over the frame, row counts [1076 x7, 1075 x3] sum 10,757; resolved frame positions 595 of 654 (59 unresolved -> eleventh bin), rows per d3 bin [961, 1019, 1003, 946, 885, 969, 1027, 1017, 970, 943, 1017].

**Frozen outcome words (full run; these are the result of this block):**
- **M-1 = PARTIAL-SURVIVES** -- primary control S_W, full-frame partial -0.064148044, position-cluster CI **[-0.093576, -0.035309]** (retained 0.727978 of the raw anchor), p_spec(neg) full 0.025316 (2/79), H 0.037975 (3/79). H view -0.067208910 CI [-0.099734, -0.033553]. Secondary control (S_W + base functionality) -0.082893328 CI [-0.115227, -0.050705], retained 0.940708, p_spec(neg) 0.025316 both views -- reported with **no word** (frozen). p_spec(abs) = 0.189873 (primary, both views); p_spec_adj (LOO OLS on mean|delta_b|) = 0.037975, k = 2/78, beaters ['AV_220','AV_85'].
- **M-3 = EXCESS-OVER-ARTIFACT** -- PRIMARY (GE-ISO, sw_i = 0): 1,000 draws, mean **+0.027069**, SD 0.007896, band [+0.012014, +0.042006], fraction <= -0.088118 = 0.0000; observed -0.088118 sits below the 2.5th percentile. Sensitivity A (E_c^lin): mean +0.000164, band [-0.016636, +0.018346]. Sensitivity B (sw_i = median m_se = 0.0809333031092933): mean +0.021297, band [+0.005599, +0.037307]. Both sensitivities reported with numbers and **no word**.
- **M-5 = WITHIN-CARRIED** -- full frame: rho_within = -0.028237316, CI **[-0.049826, -0.006662]**, p_spec(neg) 0.025316 (2/79, beaters ['AV_242']); rho_between = -0.177458126, CI **[-0.235913, -0.119746]**, p_spec(neg) 0.050633 (4/79 -- misses the <= 0.05 clause, which is what makes the word WITHIN-CARRIED rather than BOTH-CARRY). H view: within -0.035545269 CI [-0.061418, -0.010468] p = 0.037975; between -0.169522069 CI [-0.234391, -0.102037] p = 0.075949. Qualifying positions 652/654 (full), 453/455 (H). Surrogate nulls (re-labelling, no word): **S1** (within position) mean -0.067354, 95% range [-0.076189, -0.058614], fraction of -0.088118 = +0.7644; **S2** (within d3 group) mean -0.040113, range [-0.057561, -0.022281], fraction = +0.4552.
- **M-6 = MODERATE (both views)** -- full: P(p_spec <= 0.05) = **0.5760** (k distribution k=0:377, k=1:467, k=2:308, ... k=20:1 over 2,000 draws); H: P(p_spec <= 0.10) = **0.7720**. Frozen z printed as ILLUSTRATIVE SCALE CONTEXT ONLY (AGENTS 3): observed -1.8788 full, CI [-2.4116, -1.1868]; -1.7850 H, CI [-2.3273, -1.0520].
- **No word anywhere else, as registered:** M-2 (stratified: full -0.059956192 CI [-0.089115, -0.031457] p = 1/79 = 0.012658; H -0.064594698 CI [-0.096119, -0.031608] p = 3/79 = 0.037975), M-4 (MDE |r0| at 80% power = 0.03994845 on both sides, attenuation slope +0.832651, intercept +0.012097, r0=0 band q_lo -0.005532 / q_hi +0.029970), the M-3 sensitivities and the M-1 secondary control.

Resampling units (printed at the top of the output, PHASE4 rule 7): every CI in this module resamples POSITION clusters (654 / 455 positions, never 10,757 rows); M-6 resamples positions and re-derives all 79 rho_b each draw (a re-derivation null); backgrounds are never resampled here -- p_spec is an exact rank count over the 78 fixed nulls; S1/S2 and M-3/M-4 are re-labelling / simulation loops reported as distributions, not CIs. Bootstrap p-values are the primary claim; the frozen z is labelled illustrative only; effect sizes are printed beside every significance claim.

Verdict: **PASS.** A4/Module M is complete: 65/65 with all frozen anchors reproduced to their tolerances and the six frozen words above. Next is A5 (Module U, MaveDB `urn:mavedb:00000049`, separately authorised).
Files created/modified: `scripts/167_mech_anchor.py` (new), `PHASE4_A4_FULL_OUTPUT.txt` (new), `PHASE4_A4_SMOKE_OUTPUT.txt` (new), log entry appended. No existing script, library (`scripts/lib/*`), planning document, frozen pre-registration or PHASE2_PREREG.md modified (all only read); no `git add`/commit/push (status still shows only the pre-existing `.gitignore` / `README.md` / `requirements.txt` edits).
Anything unexpected or worth flagging:
- **Two genuine bugs fixed before the first passing run; no gate, threshold or frozen constant was touched.** (1) Leftover scratch from drafting was still in the file (two dead `if False` expressions, a stray `Δ` identifier, a lambda defined before the decile array it closes over) and the whole-placebo reference drew its position ids in the 654-position index space for *both* views, which would have raised IndexError on the 455-position H view -- fixed by drawing ids per view in that view's own `np.unique` space. (2) The first smoke attempt died after M-3 with `TypeError: simulation_run() missing 1 required positional argument: 'delta_raw'` -- the M-4 call omitted `HGVS`. Fixed and the smoke rerun clean. **Disclosure:** unlike A3, no separate fail file was kept -- the rerun overwrote `PHASE4_A4_SMOKE_OUTPUT.txt`, so the traceback of that first attempt exists only in this entry (it is reproduced verbatim above).
- **The M-3 null does NOT centre on zero (AGENTS 4), and the script says so every run.** PRIMARY mean = +0.027069 with mean/(sd/sqrt(n)) = 108; S1 = -0.067354 (447.6 SEs from zero) and S2 = -0.040113 (140.9 SEs). A positively-offset M-3 null and a negative S1/S2 null both mean the raw statistic overstates nothing by themselves: the excess over the null is the result. Reported plainly; nothing was re-centred or re-thresholded after seeing it.
- **M-6 lands in MODERATE, not STABLE** (0.5760 / 0.7720 against the 0.80 boundary): the frozen placebo test's per-draw p_spec clears its threshold in only ~58% (full) / ~77% (H) of position bootstraps. That is the frozen word, reported as printed; it is neither tuned up nor re-characterised.
- **M-DEC3 is a disclosed wrapper-level deviation:** `p4c.simulate_rho` cannot run on the real data (NaN delta off-frame versus a non-NaN-dropping `spearman`; a frame+reference-only rebuild misses the recorded own_e.b by up to 3.3e-1; `p.Ala222Val` is absent from task32), so the script runs simulate_rho's own loop in its exact rng order, calling `zero_epistasis_draw` / `own_eb_from_arrays` unmodified and masking to rows where both delta_real and own_e.b^sim are finite. No frozen constant, library function or rng stream changed.
- **Runtime cost:** full run 1,202 s (dominated by M-5's two 10,000-draw decomposition CIs at ~30 ms/draw and M-6's two 2,000-draw whole-placebo bootstraps at ~70-110 ms/draw); smoke 101 s. The whole-placebo *reference* is capped at `min(N_REF, 50)` draws for runtime and this cap is printed in its own gate line and in the docstring.
- **Script numbering:** MECH/A4 occupies **167**, as A3's entry already forecast (the planning doc's "scripts 165 and next" parenthetical is off by two).
---

## [A5] - Module U: predictive utility (script 168)
Status: **PASS** for U-1 (frozen word CONDITIONING-HURTS); U-2 reported **UNVERIFIED-LABELS, no word**, by the pre-registered G-U2 fallback (smoke: 20/22 checks PASS, the two FAILs being the intentional G-U3 smoke SKIP and the substantive G-U2 FAIL, exit 0; final full run: **22/23 checks PASS, 1 FAIL (G-U2)**, exit 0)
Time started / finished: Fri Oct 2 23:29 EDT 2026 (first smoke) / Fri Oct 2 23:39 EDT 2026 (final full run, 193.9 s; smoke 11.0 s)
What I did: wrote `scripts/168_utility.py` implementing the frozen `prereg/UTILITY_PREREG_v1.md` block (sha256 `744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531`, 32 lines, gated) exactly: U-1 (cached), U-2 (acquired labels + MaveDB maps), gates G-U0..G-U3. The docstring was written before the first run and carries the twelve pre-registered decisions **U-DEC1..U-DEC12**, printed at startup before any metric exists; class sizes are printed before any metric (prereg S3). Reuse only, never re-derivation (AGENTS 2): `p4c` for spearman/auroc/balanced-PR/word_conditioning/pct_ci/draw_ids/pos_cluster_boot/reference_boot, the task32 analysis table for the frame, `pdg.build` for the cached construction, openpyxl for the supplement's Tables S2/S3. No torch; no `scripts/lib/*` edits; the four sub-gates G-U0(d)-(g) are ADDED, stricter than the frozen text, disclosed as such in their own labels.

Acquisition (U-DEC11, all provenance in manifests): `POST https://api.mavedb.org/api/v1/score-sets/search {"text":"MTHFR"}` found `urn:mavedb:00000049-a-1..a-8` (4 folinate concentrations x WT/A222V backgrounds); each `GET .../score-sets/<urn>/scores` returned HTTP 200, 10,226,397 bytes total; `data/external/mavedb/U2_DOWNLOAD_MANIFEST.txt` records url|status|bytes|sha256 per line (a first shell loop assigned `$i_scores` empty and overwrote a filename, so all eight were re-downloaded with `${i}`; shas identical both times -- disclosed). Supplement: PMC direct bin links returned 1,816-byte JavaScript interstitials (stub files deleted, disclosed); the Europe PMC REST endpoint `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8322931/supplementaryFiles` succeeded at 399 s of the 1,200 s budget -- 38,784,725 bytes, sha256 `941fe85477d6c73f7dc06316c8bbe3f6e5444ddb0c40cad588c24499cc5b6187`; mmc1..mmc6 extracted (mmc3 = Table S2 for the identity check, mmc4 = Table S3 labels); `data/external/weile2021_supp/SUPP_DOWNLOAD_MANIFEST.txt` has per-file shas. The frozen fallback label set (`task102_clinvar_atlas_overlap.csv`) was NOT needed and NOT used. Both manifests are re-verified at the start of every run (G-U0(f)): 9 records, all 200, 49,011,122 bytes = 49.0 MB < 200 MB abort threshold.

Labels (U-DEC6/7) and attrition (printed before any metric): from mmc4.xlsx sheet 'patients from literature', Category exactly 'early' gives **30** positives (target 30, G-U0(d) PASS), 'late' gives **40** (target 40, PASS), per-sample distinct missense, stop gained excluded even when type=='missense', one-letter normalized; negatives are the 1000-Genomes sheet's missense, brackets split, A222V itself discarded; overlap between sets 0. ATTRITION: 69 labelled -> 68 present in task32 (missing: p.Trp339Gly) -> 68 with finite S_W and S_A (U-DEC10). **CLASS SIZES: pathogenic 29, benign 39** (min 29 >= 15; not UNDERPOWERED).

Gates -- all hard for the item they guard, every target recomputed independently and printed beside the frozen value:
```
  [PASS] G-U0(a) prereg sha256 744e68ce...9531, 32 lines
  [PASS] G-U0(b) frame 10,757 rows / 654 positions (task32 11,344; 587 dropped, y finite on all)
  [PASS] G-U0(c) Spearman(own_e_b, S_W) = 0.0854 vs target 0.0854, |diff| 0.000e+00
  [PASS] G-U0(d) set sizes 30 / 40 (ADDED)   [PASS] G-U0(e) H 455 positions / 7,526 rows (ADDED)
  [PASS] G-U0(f) manifests re-verify, all 200, 49.0 MB < 200 MB (ADDED)
  [PASS] G-U0(g) y == f_bar_a222v max|diff| 2.220e-16 (< 1e-15); delta_esm == S_A - S_W 2.220e-16 (< 1e-12) (ADDED)
  [PASS] G-U1 rho(exp.score, m25) = 0.952371770556546 over 10,819 shared variants (gate >= 0.90)
         [disclosed context] canonical `score`: rho = 0.6919167110350621 over 10,891 -- below, NOT the gate (U-DEC5)
         evidence i: project m25 == paper Table S2 A222V-25, 10,891/10,891 exact, rho 1.0
         evidence ii: a-2 rho(score, exp.score) = 0.737104307; score == pred.score on 1,037 rows (blend)
         evidence iii: a-8 (score only) vs project m200 rho = 0.9999999999819985 (rank-identical)
  [PASS] G-U3(i) 7 toy checks vs scikit-learn (AUROC w/ ties, perfect, inverted; balanced-PR curve/AUC/
         2nd path; chance toy) -- max|diff| <= 1.110e-16, all < 1e-12
  [PASS] G-U3(ii) identity: every position once reproduces rho_A/rho_W/Delta, max|diff| 5.551e-17
  [PASS] G-U3(ii) draw-by-draw paired bootstrap vs reference_boot, 500 draws: max|diff| 0.000e+00 on
         all three statistics (3.0 s)
  [PASS] G-U3(ii) Phase 1 CI lo -0.1173334458953319 |diff| 0.000e+00, hi -0.05951138449511738
         |diff| 7.633e-17 (gate < 1e-9, N_BOOT=10000, 15.2 s)
  [PASS] G-U3(ii) U-2 AUROC bootstrap draw-by-draw vs sklearn, 500 draws: max|diff| 1.110e-16 (both)
  [PASS] G-U3(ii) U-2 every-position-once reproduces both AUROCs exactly
  [FAIL] G-U2 a-2 does NOT attain the highest balanced-PR area: a-2 0.6645257581748936 vs best other
         a-6 0.7968920548030036 (a-2 ranks 8th of 8; full ranking printed)
```

**Frozen outcome words (full run; these are the result of this block):**
- **U-1 PRIMARY = CONDITIONING-HURTS** -- Delta = Spearman(S_A, y) - Spearman(S_W, y) = **-0.003397796074143755**, position-cluster CI95 **[-0.004488253530713755, -0.0023350383831684295]** (10,000/10,000 finite draws, SEED 0, word margin 0.02). Components: rho(S_A, y) = 0.36502342954860856, rho(S_W, y) = 0.3684212256227523 (context rho(S_W, base functionality) = 0.32803277256740376). Effect size beside significance: Delta is -0.0034 against component rhos of ~0.365, i.e. conditioning on the A222V background costs ~0.9% of the WT-background correlation -- small in magnitude, but negative in every one of the 10,000 draws.
- **U-2 = UNVERIFIED-LABELS, no word** -- G-U2 failed (pre-registered fallback, prereg line 28). Metrics are still reported in full: S_W AUROC 0.823165 / balPR 0.777803 (n=68); S_A AUROC 0.816976 / balPR 0.765473 (n=68); Delta AUROC = **-0.006189213085764811**, paired position-cluster CI95 [-0.021462658497809133, 0.0043300449550450135] -- the CI spans zero, reported as a number with no word (the word slot is empty because G-U2 failed, not because of this CI). Map table: n ranges 63-68 of 68 per map (U-DEC10); non-gated canonical-column sensitivity ranks best = a-6 (0.760203), a-2 (0.612497) -- same ordering conclusion.
- **No word anywhere else, as registered:** H subset (descriptive) Delta -0.003421469023321466 CI [-0.004793221601291767, -0.002173112311275384]; TOP |own_e_b| decile (cut 0.4040203526705994 -> 1,076 rows / 422 positions) Delta -0.0015226472851924966 CI [-0.002999395189130719, -7.857963560724469e-05]; per-condition descriptive repeats (U-DEC4, no multiplicity correction) all strictly negative and consistent with the primary: m12 -0.0033968104390297293 CI [-0.00450781613921524, -0.002326257927633789], m25 -0.003387127723297134 CI [-0.004497880563982747, -0.002320379334816386], m100 -0.003395316392855119 CI [-0.0045083823316761, -0.0023288692493284163], m200 -0.003430973513863067 CI [-0.004547678842604127, -0.0023543369108673822].

Resampling units (printed at the top of the output): every CI resamples POSITION clusters (654 / 455 / 422 / 654 positions, never rows); one draw_ids set per subset is shared by both predictors so the Delta is paired; backgrounds are never resampled (one background, U-DEC2); CIs are percentile 2.5/97.5 via `p4c.pct_ci`; U-2's Delta-AUROC bootstrap uses the same paired position draws with single-class draws dropped and counted (0 in both runs). Label-set metrics are point estimates with per-metric finite n; effect sizes printed beside every significance claim (AGENTS 3).

Verdict: **PASS.** A5/Module U is complete as pre-registered: U-1's frozen word CONDITIONING-HURTS stands on a fully gated reference bootstrap; U-2 comes out UNVERIFIED-LABELS -- a negative reproduction result (the paper's Fig 6A ordering, AV25 best, does not reproduce on their own label set under our balanced-PR computation), reported plainly with all eight maps' numbers, and nothing was tuned toward or away from it. Next is A6 (Module G, GB1 locality, script 169).
Files created/modified: `scripts/168_utility.py` (new, sha256 `3e8819ba25bafae1215fbb6e3fbdc056584f49da48605f48b438c6516c669173`), `docs/tasks/phase4-strengthening/PHASE4_A5_FULL_OUTPUT.txt` (new, 183 lines, sha256 `079c58f0f7f50787a912f7945b6ee48c3cee065d555082567fb37fd0febca967`), `docs/tasks/phase4-strengthening/PHASE4_A5_SMOKE_OUTPUT.txt` (new, 181 lines, sha256 `36df48a6388399a3aeb56963dae04d53befdba27d5a1251c19f5060469c195f2`), `data/external/mavedb/` (8 score CSVs + `U2_DOWNLOAD_MANIFEST.txt`), `data/external/weile2021_supp/` (zip + extracted/mmc1..mmc6 + `SUPP_DOWNLOAD_MANIFEST.txt`), log entry appended. No existing script, library (`scripts/lib/*`), planning document, frozen pre-registration or PHASE2_PREREG.md modified (all only read); no `git add`/commit/push (status still shows only the pre-existing `.gitignore` / `README.md` / `requirements.txt` edits plus untracked new files).
Anything unexpected or worth flagging:
- **POST-RUN TEXT-ONLY FIX (disclosed in the script's own output per AGENTS 6).** The first full run (sha256 `020f58a4eddce08bcb72e8a99937057ea542cc88044aad86ce55852d42ab2789`, now superseded -- regenerated in place, not appended) quoted the recon-time canonical-column figure as exactly 0.6846 in its disclosure line. Post-run reconciliation could NOT reproduce 0.6846 from any current row set: the same comparison gives 0.6919167110350621 on the 10,891-row merge, 0.693100 on the 10,819-row gate subset, 0.681157 restricted to U-1 frame rows -- the recon's exact row set was not recorded. The docstring and the disclosure line were changed to state this; **text only -- no gate, threshold, decision or computed value changed**, confirmed by the rerun: Delta, G-U1's 0.9524, the Phase 1 CI and every other gated number are digit-for-digit identical to the superseded run. Smoke and full were both rerun after the patch.
- **G-U2's FAIL is robust to the column choice and was left alone.** a-2 ranks last of eight on the gated experimental columns and the non-gated canonical sensitivity gives the same ordering (both printed). Coverage differs across maps (n 63-68 of 68); a like-for-like intersection re-ranking would be a post-hoc subset change (AGENTS 0) and was deliberately NOT run. The pre-registered fallback -- UNVERIFIED-LABELS, no word, exit 0 -- is the result; nothing was re-metriced or re-thresholded after seeing it.
- **U-DEC5 stands as disclosed:** the canonical-column comparison (below 0.90) was seen first during recon; the column choice follows AGENTS 5's column-identity analysis (m25 is byte-identical to the paper's Table S2 column; a-2's `score` is a shrunken exp/pred blend -- not a like-for-like map). Both numbers are printed every run; had no like-for-like column existed, U-2 would have been STOPPED at G-U1.
- **No runtime bugs in either run:** the first smoke and first full run both completed end-to-end with only the two designed FAILs (smoke SKIP + G-U2); the only edit after the first full run was the disclosure text above. Unlike A3/A4, no failure output needed preserving.
- **Outputs' location:** A5's two output files were first written at the repo root (as the smoke command dictates) and then moved to `docs/tasks/phase4-strengthening/` to sit with A2-A4's outputs; contents and shas unchanged.
- **Runtime:** smoke 11.0 s (N_BOOT=300), full 193.9 s (N_BOOT=10000 SEED=0, dominated by the 10,000-draw reference-gate CI reproduction at 15.2 s and the eight U-1 bootstrap subsets). Script numbering: Utility/A5 occupies **168**, as forecast by A3/A4's entries (the planning doc's parenthetical remains off by two).
---
## [A6] - Module G: GB1 locality (script 169)
Status: **PASS** -- full run **31/31 checks PASS, 0 FAIL**, exit 0 (smoke: 31/31 PASS, exit 0; two earlier smoke attempts crashed and are disclosed below)
Time started / finished: Fri Oct 2 2026 (script written + first compile attempts) / Sat Oct 3 08:05 EDT 2026 (final full run, 27.4 s; final smoke 26.7 s)
What I did: wrote `scripts/169_gb1_locality.py` implementing the frozen `prereg/GB1_LOCALITY_PREREG_v1.md` block (sha256 `10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8`, 26 lines, gated) exactly: G-D0..G-D3 reference/mechanics gates, G-1 (decay of |delta| and |e_b| with separation s), G-2 (signed rho_b within separation strata + paired near-far), G-3 (optional C-alpha distance repeat). The docstring carries the eight pre-registered decisions **G-DEC1..G-DEC8**, printed at startup before any statistic exists. AGENTS 2 reuse only: script 155's partner table and delta build are EXECUTED VERBATIM from quoted line ranges (346-417, 431-455) in a dict copy of globals seeded with 155's constants, with the transcript's own gates (F_B,wt pin, partner structure, G-4 coverage) re-run and marked `[155 transcript]`; `load_scores`/`SHAS` imported from script 155; all bootstrapping via `p3c.background_boot` / `p3c.pct_ci` (never rows, never positions -- resampling unit is the 400 backgrounds, one pre-drawn ids set per sample size shared by every statistic of that size so the paired difference is paired). No torch/esm anywhere (extra gate confirms). Script numbering: A6 = **169** (the planning doc's parenthetical is off by two; disclosed in session header).

Pre-registered (G-DEC7) and observed: every gate decides in both modes -- no smoke skips; G-D3(iii) runs at its fixed 10,000 draws even in smoke; any FAIL -> exit 3; thresholds never loosened; N never raised to pass a gate.

Gates -- all hard for the item they guard, every target recomputed independently and printed beside the frozen value:
```
  [PASS] G-D0 prereg sha256 10c547c9...95a8, 26 lines
  [PASS] G-D0 input sha256 x5 (olson doubles 89f8e394..., olson singles 0b2e865e...,
         gb1_background_roster ee2e7872..., roster_v2 edc259d4..., sequences f0d1d2d5...)
  [PASS] G-D0 partner table rows: 410,271 (script 155 printed 410,271)
  [PASS] G-D0 rho_b reproduces stored table on 10 sampled backgrounds: max|diff| 8.327e-17 (tol 1e-12)
  [PASS] G-D0 primary mean rho_b == -0.009125: stored -0.009125049245666152, recomputed
         -0.009125049245666152 (target -0.009125 +/- 1e-06 at 6 dp)
  [PASS] G-155-2 F_B,wt pin [155 transcript]: max|diff| 4.441e-16 over 1,045 singles (tol 1e-12)
  [PASS] partner-table structure [155 transcript]: rows with v_pos == pos: 0
  [PASS] G-4 coverage >= 95% of 54 eligible positions [155 transcript]: completed 400, failures 0
  [PASS] delta-build coverage gate [155 transcript] (all complete)
  [reconcile] n vs stored n_partners_t25: max|diff| = 0 over 400 backgrounds
  [PASS] G-D1 own-position partners in the analysis rows: 0 rows
  [PASS] G-D2 decay arm: CI = [-0.993134, -0.992555] entirely below zero
  [PASS] G-D2 null arm fire rate 0.020 <= 0.15 over the frozen 100 draws (smoke: 0.040)
  [PASS] G-D3(i) identity: every unit once == point estimate, |diff| 0.000e+00, for all
         7 statistics (lambda_model, lambda_data, d_b, near, mid, far, paired)
  [PASS] G-D3(ii) draw-by-draw vs background_boot max|diff| 0.000e+00 over 10,000 draws AND
         vs slow reference 0.000e+00 over 500 draws, for all 7 statistics (tol 1e-12)
  [PASS] G-D3(iii) Phase 1 CI reproduces: |diff| lo = 0.000e+00, hi = 0.000e+00
         (target [-0.1173334458953319, -0.05951138449511738], tol 1e-9, 10,000 draws)
  [PASS] [extra] no torch/esm/thermompnn imported: True
```

**Frozen outcome words (full run; these are the result of this block):**
- **G-1 MODEL-DECAYS FIRES** -- mean lambda_model = **-0.271233756**, SD(ddof=0) 0.132617417, fraction negative 0.9650, background-bootstrap CI95 **[-0.284302974, -0.257821930]** (10,000/10,000 finite draws, SEED 0).
- **G-1 DATA-DECAYS does not fire** -- mean lambda_data = +0.036680324, SD 0.108869710, fraction negative 0.3775, CI95 [+0.025947267, +0.047664307]; the CI does not lie entirely below zero (it is entirely above zero -- printed as-is, the frozen word is "does not fire").
- **G-1 LOCALITY-DIFFERS FIRES** -- mean d_b = **-0.307914080**, SD 0.155916580, fraction negative 0.9650, CI95 **[-0.323182052, -0.292525237]**. Effect size beside significance: the model's |delta| correlates with separation about 0.30 Spearman units more negatively than the measured epistasis does, against a lambda_data mean of only +0.037 -- the gap is an order of magnitude larger than the data-side trend it is subtracted from.
- **G-2 SEPARATION-MATTERS** -- signed rho_b,stratum (SIGNED delta vs signed e_b, as frozen; not interchangeable with G-1's absolute values): near s 1-5 = -0.022121012 CI [-0.040277659, -0.003976346] (400/400 backgrounds, 70,747 partner rows); mid s 6-15 = -0.010881286 CI [-0.024698533, +0.002299449] (400/400, 120,303 rows, spans zero); far s 16-54 = +0.000268630 CI [-0.012552017, +0.012707822] (399/400, 202,018 rows, spans zero); **paired near - far = -0.022238860**, SD 0.214089446, CI95 **[-0.043104841, -0.001032463]** over the 399 backgrounds with both strata -- excludes zero. The stratum means themselves are not individually decisive outside "near"; the claim rests on the paired difference, which is what the prereg froze.
- **G-3 SKIPPED (pre-registered G-DEC8 fallback), by the book** -- 1PGA downloaded and verified (provenance below); chain A's C-alpha sequence is 56 residues vs ASSAYED 56, with exactly **1 differing position: pos 2, PDB T / assayed Q**, so neither the 56-mer nor the positions-2..56 55-mer yields a unique contiguous, resnum-contiguous match. G-DEC8 says: else one-line skip. No numbering was guessed, no offset was assumed, and no distance analysis was run.

Acquisition (G-3, authorized as the optional RCSB item): `https://files.rcsb.org/download/1PGA.pdb` status=200, 59,049 bytes, sha256 `908f8dbf3bb7567f36eec4683eb8cfab5ac0c011dfee1b9c940cab7f482bc841`, saved `data/external/rcsb/1PGA.pdb`; the >= 5 GiB free-disk check ran before the fetch (planning rule 2), url/status/bytes/sha256 printed by the script itself, and a fetch failure would have skipped G-3 alone. Re-fetched identically on each run (same sha both times).

Resampling units (printed at the top of the output): backgrounds (the 400 units), never positions, never rows; one ids set per sample size pre-drawn in `background_boot`'s own loop order from default_rng(SEED) and shared across all statistics of that size; CIs are percentile 2.5/97.5 via `p3c.pct_ci`. This module's unit is backgrounds rather than positions because the statistic is defined per background by construction (G-DEC5).

Verdict: **PASS.** A6/Module G is complete as pre-registered. The substantive result is a split one and is reported as such: the MODEL's implied epistasis decays with partner separation while the MEASURED epistasis does not (LOCALITY-DIFFERS fires, d_b CI excludes zero), and the model-data agreement rho_b is significantly more negative among close partners than among distant ones (SEPARATION-MATTERS) -- but the absolute signed correlations are small (near -0.022), the mid stratum's CI spans zero, and DATA-DECAYS does not fire. Nothing was tuned; G-3 took its registered skip path instead of a guessed numbering.
Files created/modified: `scripts/169_gb1_locality.py` (new, sha256 `af2f6fd87592af59043da2a744bb81edb8f19e0189c7269625bc7d193b3d8f63`), `docs/tasks/phase4-strengthening/PHASE4_A6_FULL_OUTPUT.txt` (new, 323 lines, sha256 `057670ae21b86cceeb5e7e90e04dad5743d911af9982fdf6a5a9b9a48d3071d1`), `PHASE4_A6_SMOKE_OUTPUT.txt` (new, 324 lines, sha256 `fce817213f5d1c8ed59ea28869a70c5a42f0b39a2f742c045476ca03736fdd44`), `data/external/rcsb/1PGA.pdb` (new, 59,049 bytes), log entry appended. No existing script, library (`scripts/lib/*`), planning document, frozen pre-registration or PHASE2_PREREG.md modified (all only read); no `git add`/commit/push (status still shows only the pre-existing `.gitignore` / `README.md` / `requirements.txt` edits plus untracked new files).
Anything unexpected or worth flagging:
- **Two failed smoke attempts, disclosed (A4-style).** Attempt 1 died on an IndentationError in the gate-table f-strings (line breaks inside implicitly-continued strings); attempt 2 ran cleanly through G-D0..G-2 and then crashed at G-3 with `NameError: name 'ASSAYED' is not defined` -- ASSAYED existed only inside the transcript's `env` dict and was never bound in the scope that runs G-DEC8. **Post-hoc runtime fix, disclosed in the script's own output** (`[POST-HOC FIX, DISCLOSED] ASSAYED bound from transcript env ...`): `ASSAYED` is now read out of `env` after the transcript executes -- the same object (`S155.ASSAYED`, already sha-pinned by G-D0); no gate, threshold, number or decision rule changed. Final smoke and the full run were both executed after this fix.
- **Second post-hoc addition, informational only:** after the final smoke showed G-3 skipping with an unexplained reason, a one-line `numbering diagnostic` was added that prints the exact divergence (chain A vs ASSAYED position-by-position) so the skip is auditable. It prints information and changes no gate, threshold, or path; the G-DEC8 skip text is unchanged.
- **G-3's skip is a real sequence difference, not a download or parsing problem.** 1PGA chain A residue 2 is Thr where the assayed construct has Gln; both pre-registered matching forms therefore fail by construction. Substituting a different PDB, shifting the offset, or dropping the match requirement would all be post-hoc -- none was done (AGENTS 0/8).
- **G-D2's two arms use different seeds by design** (decay arm default_rng(3), null arm default_rng(1000), G-DEC6); the null fire rate differs between modes (0.040 smoke at 300 draws vs 0.020 full at 10,000) because CI width depends on N_BOOT -- both are far under the 0.15 gate, and neither number is an estimate (mechanics check only, disclosed in the output).
- **Smoke vs full:** every gate number that does not depend on N_BOOT is identical between the final smoke and the full run (identity checks 0.000e+00, Phase 1 CI endpoints 0.000e+00 in both, since G-D3(iii) runs at fixed 10,000 draws in both modes per G-DEC7). Words in the smoke are marked PROVISIONAL; the words above are from the full run only.
- **Runtime:** smoke 26.7 s (N_BOOT=300, N_REF=500), full 27.4 s (N_BOOT=10000, N_REF=500, SEED=0) -- the fixed 10,000-draw Phase 1 CI gate dominates and runs in both modes, so the two runs cost about the same. Downloads: 1PGA only (59 KB).
---

---

## [A7a-A7b] - Module N neighbour arm: geometry, cells and the frozen roster (scripts/170_neigh_roster.py) - PASS

**Date:** 2026-10-03 (session 4a). **Status: PASS** - smoke 18/18 checks, full run 19/19 checks, exit 0.

### ARNAV'S AMENDMENT 1 (received during A7 build, before any draw or score, fitness-blind)

Verbatim decision, recorded here in full as instructed; saved UNEDITED as
`docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md`
**sha256 `f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a`** (9 lines).
`NEIGHBOUR_ARM_PREREG_v1.md` was NOT edited - v1 sha256 before and after the amendment is
`167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e` (gated at startup by G-N0).

> ARNAV'S DECISION (made before any draw or score; fitness-blind). Record it verbatim in the A7b log entry AND save it, unedited, as docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md, then log its sha256. Do NOT edit NEIGHBOUR_ARM_PREREG_v1.md.
>
> Amendment 1 to NEIGHBOUR_ARM_PREREG_v1 (supersedes only the items named):
> 1. Alanine-first (section 3) applies only to eligible alanine positions in C1 and C2 whose (position, V) pair is NOT already among the 96 existing backgrounds. First VERIFY and print, for every eligible alanine in C1 and C2, whether (position, V) exists in data/processed/phase2_arm_roster.csv. Where it exists (expected for all, because Arm V covers the alanines), the step is skipped for that position.
> 2. Every eligible position in C1 and C2 receives exactly one new background (the caps exceed the eligible counts, so all are used). The mutant is drawn with numpy.random.default_rng(0) from the alphabetically sorted one-letter codes of the non-wild-type residues EXCLUDING any residue whose (position, residue) pair already exists among the 96 existing backgrounds or A222V; draw in ascending position order, C1 first and then C2, one draw per position from the continuing stream. A position that already hosts an existing background stays eligible with a different residue and is flagged second_at_position in the roster.
> 3. New cell C5 (near in 3D, middle in sequence): d3 <= 12 and 20 < dseq <= 40, same rules as 1 and 2, cap 16 (all eligible if fewer). This closes the gap between C1 and C2. NB (section 5) is redefined as the new backgrounds in C1, C2 and C5 plus the six existing nulls with d3 <= 12.
> 4. Sensitivity (no word): p_NB recomputed after collapsing NB to one value per position (the mean rho_b of the backgrounds at that position), because second_at_position backgrounds are not independent. Report it beside the primary p_NB.
> 5. The A9 coverage rule for the neighbour-arm analysis (SA2 and SB5) is replaced by: run iff the complete NB (every member with >= 95% of its eligible H positions) has at least 30 members; otherwise log SKIPPED. The UNDERPOWERED rule (|NB| < 30) is unchanged.
> 6. Everything else in NEIGHBOUR_ARM_PREREG_v1 stands: the gates, the words, the thresholds, the scoring protocol. Print the counts (eligible per cell, new backgrounds per cell, |NB|) BEFORE the draw, and write and hash the roster BEFORE any scoring.

End of verbatim amendment. Conflict it resolved: frozen section 3's "every eligible alanine in
C1/C2 receives A->V" collided with "no (position, mutant) pair among the 96 is reused" - the only
eligible C1/C2 alanines are 220, 155, 175 and all three (position, V) pairs exist as AV_220,
AV_155, AV_175. Amendment item 1 supersedes the alanine-first rule for those positions.
**Flag (AGENTS 9):** the amendment's item 5 also replaces the A9 SA2/SB5 coverage rule in
`PHASE4_STRENGTHENING.md` lines 217-218; that planning doc is protected and was NOT edited - the
conflict is flagged here and will be applied per the amendment when A9 is built.

### What this run did

- **Script:** `scripts/170_neigh_roster.py` **sha256
  `a9516951e05b9a2cc5a2ba804c2db81b43b0c56bf2afd12473ac00f058e2e597`** (next-free-number rule:
  A6 took 169; A7 needs three scripts - 170 roster/geometry, 171 score, 172 analysis - so A8
  shifts to 173/174; disclosed here because the planning doc's "scripts/17x" parenthetical does
  not pin a count).
- **Pre-registered before first run (N-DEC1..N-DEC9 in the script docstring, printed at
  startup):** both prereg hashes pinned; script 139's `parse_pdb_float64` imported torch-free;
  cells = `p4c.cell_labels` (A2-gated thresholds, frozen section 2) + C5 as a gap-cell override
  (d3 <= 12), so the A2-gated function is NOT modified; alanine-first verification per amendment
  item 1; single `default_rng(0)` draw stream with cell order C1 -> C2 -> C5 -> C3; roster schema
  + bg_id format + round-robin score order; NB definition per amendment item 3; expected passes
  = 455 - 1[own in H].
- **Gates (hard, exit 3):** G-N0 - both prereg/amendment/stored-d3 hashes, frame = 654, loader
  reproduces stored d3 for the 67 resolved nulls to 1e-6 (this run: max|diff| 4.97e-07 vs the
  6-decimal stored file), cell counts printed before the draw, no torch anywhere in the process.
  G-N1 - roster written + sha256 sidecar + re-read before any scoring; unique bg_ids; no
  duplicate (position, mutant); no pair among the 97 banned; per-cell counts = pre-draw counts;
  second_at_position flags correct; round-robin balance at every prefix; the six NB nulls all
  resolved with d3 <= 12; H = 455; and (from the full run) a re-run reproduces the frozen roster
  byte-identically.

### Numbers printed BEFORE the draw (amendment item 6)

- Eligible per cell: C1 12, C2 13, C5 15, C3 24, C4 450, gap 81; total 595 frame positions
  resolved in 6FCX chain A minus 222; **40 positions with d3 <= 12** (planning figure "roughly
  40-60", met at the floor).
- New backgrounds per cell: C1 12, C2 13, C5 15, C3 10 = **50 total**.
- **|NB| = 40 new (C1+C2+C5) + 6 existing nulls = 46 >= 30** - not underpowered by construction
  (amendment item 5's coverage rule still applies after scoring).
- **Alanine-first verification (amendment item 1):** four eligible alanines, all skipped -
  C1 position 220, C2 position 155, C2 position 175, C5 position 195 - each (position, V)
  EXISTS among the 96 (AV_220/AV_155/AV_175/AV_195). No A->V assignment was made.
- Six NB nulls verified against geometry: G_I192T 5.058, AV_220 6.480, AV_155 8.639,
  AV_195 10.150, G_L178T 10.313, AV_175 10.537 (all <= 12, all resolved).
- Expected passes: roster 22,719 (454 or 455 per background), NB 20,900.
- second_at_position flagged on 7 of 50 new backgrounds (positions already hosting an existing
  background; amendment item 2 - they stay eligible with a non-banned residue).

### Outputs

- `data/processed/phase4/neigh/roster_v1.csv` - 50 rows, **sha256
  `675a24f1963878568e65b6d630e25e9ce649627c3f02ab0d5e65ec438f2d85d6`** (sidecar
  `roster_v1.sha256`); written and hashed BEFORE any scoring.
- `data/processed/phase4/neigh/eligible_cells_v1.csv` - 595 rows, sha256
  `db86399b8858e890fd11cb2c3e7debd2857f66f33eea7d87c769862b8408ba22` (written before the draw).
- `docs/tasks/phase4-strengthening/PHASE4_A7_ROSTER_FULL_OUTPUT.txt` - full run record, 107
  lines, sha256 `a99fd93a128d440187b89dec80f16e0161e0b45b4b6bf5c208edf6f12b6aacd8`
  (19/19 PASS). Smoke: N_BOOT=300 run, 18/18 PASS (the 19th check - byte-identity on re-run -
  only fires once a roster exists); identical numbers in both.
- Runtime: 0.1 s per run (no bootstrap, no model scoring; N_BOOT/SEED printed, unused - the draw
  seed is fixed at 0 by the amendment).

### Disclosed interpretations / limitations (also in the script's printed output)

- **Stream order C1 -> C2 -> C5 -> C3 and `rng.integers`-indexed draws are this script's
  interpretation** of Amendment 1: the amendment pins "C1 first and then C2" and gives C5 "the
  same rules as 1 and 2" (so C5 follows C2), but does not state C3's place in the stream (C3 is
  unamended and is drawn last). The allowed-set indexing is the literal reading of "drawn ...
  from the alphabetically sorted one-letter codes ... EXCLUDING" banned residues.
- The roster freezes WHICH backgrounds are scored, not their scores; nothing fitness- or
  rho-related enters any decision here (fitness-blind by construction).
- d3 is a CA-CA distance in the 2.50 A 6FCX chain A structure; "resolved" means a chain-A
  Calpha exists at that residue number.

---

## [A7c-A7d] - Module N neighbour-arm scorer, gate G-N2 and the timing projection (scripts/171_neigh_score.py) - PASS

**Date:** 2026-10-03 (session 4a). **Status: PASS** - G-N2 (a)(b)(c) all PASS, A7d projection WITHIN budget, exit 0. **No roster background has been scored for real yet** - the night run (SA1) owns that; this entry covers the gate run and a 3-background timing smoke into scratch only.

### What this run did

- **Script:** `scripts/171_neigh_score.py` **sha256
  `e904951d327030cbc843c3eefdd818ef6a5c4e7d46448c8031fe03051c4cf2a7`** (second of the three
  A7 scripts; numbering disclosed in the A7a/A7b entry).
- **Pre-registered before first run (NS-DEC1..NS-DEC7 in the docstring, printed at startup):**
  no-download pre-check of the local torch.hub cache (missing checkpoint -> exit 3, never a
  download); frames H=455 / nonH=199 with script 124's `expected_positions` imported; output
  contract `bg_id, position, mut_aa, score, delta` (delta vs the Phase 2 WT cache, join asserted
  complete); script 124's `file_is_complete` skip logic imported and its atomic-write pattern
  quoted with a QUOTED SOURCE reference; G-N2 runs before any roster scoring on every invocation
  that has something to score, always into `data/processed/phase4/neigh_scratch/`; roster sha
  must match its G-N1 sidecar before the model loads; median s/pass x 22,719 x 1.25 vs 330 min
  with the G-N2 cost disclosed outside the formula.
- **G-N2 (HARD, exit 3) results:**
  - (a) AV_220 rescored on H reproduces its cached rows: 8,626 rows (454 positions x 19),
    **max|d score| 1.776e-15, max|d delta| 1.776e-15** (gate 1e-6) -> PASS. The cached rows
    were produced by the same library function on the same device (mps) in Phase 2; the
    agreement is float64-exact, which also confirms the delta join is correct.
  - (b) same background scored twice in one run: **max|d score| 0.000e+00, max|d delta|
    0.000e+00** (gate: exactly 0.0) -> PASS. MPS forward passes are bit-reproducible here;
    the exact-zero reading of "identical" (disclosed NS-DEC4b) held.
  - (c) wild-type residue's log-odds at H position 2 (V): **0.0**, alphabet token round-trip
    True, `get_position_logprobs` returns 19 entries excluding the WT residue -> PASS.
  - Gate cost: 908 passes (2 x 454), 546 s, scratch only.
- **A7d timing smoke:** 3 roster backgrounds (round-robin prefix: N_214_LV/C1, N_46_RL/C2,
  N_182_IV/C5) scored on H into `data/processed/phase4/neigh_scratch/timing/`:
  279.1 s / 292.4 s / 297.4 s for 455/455/454 positions = **median 0.643 s/pass**
  (0.613, 0.643, 0.655).
- **Projection (fixed formula): (22,719 roster H passes x 0.643 s/pass) x 1.25 = 304 min vs
  the 330-minute budget -> WITHIN budget.** G-N2's own 908 passes add ~12 min at this rate,
  inside the 1.25 slack (disclosed NS-DEC7). The roster is NOT shrunk; if a later measurement
  exceeds 330 the A9 stage rule applies.

### Bug fixed before any roster score existed (disclosed)

- **Attempt 1 of the timing smoke exited 1** on `AttributeError: 'Alphabet' object has no
  attribute 'all_tokens'` (the G-N2(c) token round-trip check used a wrong attribute name;
  the canonical inverse of `get_idx` is `get_tok`). The crash happened inside G-N2, BEFORE any
  roster background was scored - no roster file, no manifest row existed at the time. Fixed in
  place (one line) and re-run; this is a pre-first-score code fix, not a post-hoc change to any
  result. Record kept as `PHASE4_A7_TIMING_SMOKE_ATTEMPT1_FAIL_OUTPUT.txt` (sha256
  `72c503617630279d0fa4dc897ad1bf9d97669513969106a1e1caca154bcfc37d`), per the A3 precedent.
- Note from attempt 1: G-N2 (a) and (b) had already PASSED in that run with the same numbers -
  the failure was purely the attribute name in check (c).

### Outputs

- `docs/tasks/phase4-strengthening/PHASE4_A7_TIMING_SMOKE_OUTPUT.txt` - full record, 54 lines,
  sha256 `73b5fca7e845a3b451f09d7ae8fdeb850ca677ec5d2c6cd8ff858a87cf593a24` (exit 0).
- Scratch: `neigh_scratch/gate_n2_av220_run1.csv` + `run2.csv` (457,674 B each),
  `neigh_scratch/timing/bg_N_214_LV.csv`, `bg_N_46_RL.csv`, `bg_N_182_IV.csv` + `manifest.csv`.
  Nothing was written to `data/processed/phase4/neigh/` (the real output dir) in this entry.
- Wall: 1,422 s (~24 min) for the whole invocation (G-N2 9.1 min + 14.5 min scoring).

---

## [A7e] - Module N analysis script: G-N4 FAILS on its fixed pre-registered seed - BLOCKED, STOPPED TO ASK (scripts/172_neigh_analysis.py)

**Date:** 2026-10-03 (session 4a). **Status: BLOCKED** - smoke run exited 3:
25 PASS, 1 PENDING (G-N3, expected: no new scores exist yet), **1 FAIL (G-N4's
3D-signal arm)**. Per AGENTS 10 and the script's own N-AN10 ("if one fails, that
is a genuine gate failure -> exit 3, stop, ask -- never a re-seek of the seed"),
no full run was attempted and NO parameter was changed. The full run would not
help: G-N4 is fixed at 10,000 draws in both modes (N-AN9/N-AN10), so it
reproduces this result exactly - this is not an N question.

### What ran

- **Script:** `scripts/172_neigh_analysis.py` **sha256
  `366fd6a329ccddfc60464260a88aba2f0079ecfe552d663f11f57770a0715124`** (third of the
  three A7 scripts; no torch, asserted at exit: False).
- **Record:** `PHASE4_A7_ANALYSIS_SMOKE_OUTPUT.txt`, 116 lines, sha256
  `03011482df128c92f977e0b05269ee99835ec18f440481e88ceca3df5ef056f4`
  (`N_BOOT=300 SEED=0 venv/bin/python3 scripts/172_neigh_analysis.py --mode smoke`, exit 3,
  319 s). Words/numbers marked PROVISIONAL in the record per N-AN11.
- **Pre-first-run fixes (disclosed):** before the first execution, the draft's G-N5(i)
  identity block was corrected - two contrast checks were tautologies (`x - x`, which could
  never fail) and the cell-mean identity used a 1-draw random draw instead of `arange`; they
  now compare `stat(arange)` against the directly computed point estimate. No result existed
  when these were fixed.

### What PASSED (25 checks)

- **N-CHK0** all six input hashes (both preregs, roster, cells, D1, stored 3d) match.
- **N-CHK2** A222V canonical rho_H = -0.09002168303339808 vs frozen -0.090021683
  (|diff| 3.34e-11); independent recomputation matches canonical to 0.000e+00 over 7,526
  H rows; **all 96 D1 rho_H values == recomputation from cached rows, max|diff| 4.96e-10**
  (gate 1e-8); same-site rank **2/19** by both signed and |rho| (frozen 2/19).
- **N-CHK3** roster 50/40; 67 resolved existing nulls; existing-null cells
  `{C1:1, C2:3, C3:3, C4:51, C5:2, gap:7}` with C5 exactly `AV_195, G_I192T` (the C5 split
  was verified against the data before first run: the 7 gap members all have d3 15.7-18.65);
  roster cell == geometry cell for all 50; Pool P = 117 = 50 + 67.
- **G-N3** PENDING (0/50 new backgrounds scored; 0 short files) - correct pre-night.
- **G-N4's other two arms:** sequence plant -> **SEQUENCE-LOCAL**; noise fire rate
  **0.070 <= 0.15** (7/100).
- **G-N5 all five checks exact:** identity 0.000e+00; cell-mean draws == `background_boot`
  0.000e+00 (same seed construction); partial draws == slow closed-form reference
  max|diff| **1.86e-15** over both arms x 10,000 draws, 0 NaN mismatches; contrast draws ==
  plain-Python rebuild 0.000e+00; **Phase 1 CI reproduced to 0.000e+00 on both endpoints**
  at fixed 10,000 draws.
- Sections 5/6/full-frame printed SKIPPED/PENDING per amendments 4/5 (correct: no scores).

### The failure, diagnosed (no tuning applied)

- **Gate:** `G-N4 3D plant returns 3D-LOCAL`. The plant `rho = 1.0*z(d3) + 0.4*eps`
  (eps = `default_rng(3)`, shared across both signal arms, N-AN10) gave d3 CI
  **[+0.5254, +0.7978]** (correct arm, fires) but dseq CI **[+0.0612, +0.4562]** - the
  wrong arm's CI also excludes zero, so the word was **BOTH-LOCAL, not 3D-LOCAL**.
- **Not a code bug.** Independently recomputed outside the script: point partials for
  seed 3 are matched 0.6864, wrong 0.2670 (consistent with the printed CIs). The
  machinery itself passed every other check above.
- **Not structural to the plant design either - it is an unlucky fixed seed on hard
  geometry.** Over 300 random eps seeds, the d3-plant's WRONG arm has mean **0.0651**,
  sd **0.0904**; seed 3's 0.2670 sits at **+2.24 sd**. (The +0.065 offset is a small
  structural bias: expected rank of `z(d3)+0.4*eps` is a nonlinear monotone function of
  d3, whose curvature residual correlates 0.065 with `resid(dseq | d3)` on this pool -
  driven by the pool's high `spearman(d3, dseq) = 0.776`.) With the observed CI
  half-width (~0.20), roughly **7-8% of seeds would fail this gate**; seed 3 is one of
  them. The matched arm is robust (mean 0.754, sd 0.040 - it always fires).
- **Nothing was re-run, re-seeded, re-thresholded or re-designed.** Changing the seed,
  the noise scale, or the wrong-arm criterion now - after seeing which result each
  produces - would be exactly the post-hoc tuning AGENTS 0/1 forbids. It is Arnav's call.

### Blocked until Arnav decides

A7e (and therefore anything downstream of it in A7/A9) waits for a decision - most
cleanly a **Amendment 2** in the same format as Amendment 1, naming exactly what
supersedes (plant seed and/or noise scale and/or the wrong-arm requirement, or an
explicit acceptance of BOTH-LOCAL for the d3 plant as a known property of this
geometry). Amendment 1 and v1 remain untouched (hashes gated PASS in this run).

### AMENDMENT 2 (issued after the seed-3 failure, before any real neighbour-arm score exists)

Verbatim decision, recorded here in full as instructed; saved UNEDITED as
`docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md`
**sha256 `b636a4d193efa16ed36e7d7feeb5a357c99cd5f202437bf100a55b80f822b55a`** (8 lines).
Neither v1 nor Amendment 1 was edited - `NEIGHBOUR_ARM_PREREG_v1.md` sha256
`167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e` and
`NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md` sha256
`f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a` before and after
(all three are hash-gated PASS in the run below).

> ARNAV'S DECISION (made before any real neighbour-arm score exists). Record it verbatim in the A7e log entry AND save it, unedited, as docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md, then log its sha256. Do NOT edit v1 or Amendment 1.
> Amendment 2 to NEIGHBOUR_ARM_PREREG_v1 (supersedes only the plant criteria of G-N4):
> 1. G-N4's plant checks are evaluated as RATES over 100 pre-listed seeds (0..99; the failing seed 3 is INCLUDED, not skipped), not on a single seed. For each plant (3D-only, sequence-only, none) report the confusion matrix of the four words (3D-LOCAL, SEQUENCE-LOCAL, BOTH-LOCAL, NEITHER-RESOLVED).
> 2. Criteria, in the rate form of the same requirements: the correct word is returned for the 3D-only plant and for the sequence-only plant in at least 80% of seeds; the wrong-arm partial excludes zero in at most 15% of seeds (v1's own fire-rate bound); the none-plant returns NEITHER-RESOLVED in at least 85% of seeds. The thresholds 0.80 and 0.15 were set without reference to any seed's outcome.
> 3. Disclosure: quote in the log the single seed that failed, the diagnosis (pool spearman(d3, dseq) = 0.776; the wrong-arm fire rate across seeds of about 7-8%, near the nominal CI rate), and that this amendment was made after seeing them.
> 4. The real section 6 result is always printed together with the planted confusion matrix, so a BOTH-LOCAL word can be read against its measured false-attribution rate when the truth is 3D-only.
> 5. If the correct-word rate for either single-arm plant is below 80%, section 6 returns NO WORD (all numbers still reported) and section 5, the position-versus-region test, is unaffected.
> Everything else in v1 and Amendment 1 stands. Do not change any seed, noise scale or threshold other than as written here.

End of verbatim amendment. **Amendment 2 was made after seeing the failing seed-3 result
and its diagnosis** (0.776 collinearity; ~7-8% wrong-arm fire rate across seeds), exactly as
item 3 requires be disclosed. Both preregs remain hash-pinned and unmodified.

---

## [A7e, attempt 2 under Amendment 2] - G-N4 FAILS AGAIN, now structurally: the sequence channel cannot be separated from the 3D channel - BLOCKED, STOPPED TO ASK

**Date:** 2026-10-03 (session 4a). **Status: BLOCKED** - smoke run exited 3:
28 PASS, 1 PENDING (G-N3, correct pre-night), **2 FAIL**, both in G-N4's sequence-only
plant. Section 6 would return **NO WORD** under Amendment 2 item 5 even once scores
exist; section 5 (position vs region) is unaffected. No seed, noise scale, threshold or
statistic was changed by me.

### What ran

- `scripts/172_neigh_analysis.py`, **sha256 `7f4beb53f3be551d568f26eea9c67e6df70d07942eee91e9fcd95baf307a0db5`**; run as `N_BOOT=300 SEED=0 ... --mode smoke`, record
  `PHASE4_A7_ANALYSIS_SMOKE_OUTPUT.txt`, 131 lines, sha256
  `ae950f6e3dec8e4f0e259926576b808d236cc99caff86e14383b6b8e2f20d607` (G-N4 wall 864 s; total
  ~15 min).
- Amendment 2 implemented as pre-registered in **N-AN14** (docstring, printed at startup):
  100 pre-listed seeds 0..99 x 3 plants, eps shared across the three plants within a seed,
  plant construction, noise scale 0.4, CI stream and 10,000 fixed draws all unchanged;
  G-N5's mechanics vector left exactly as first pre-registered (the seed-3 3D-only plant),
  so no already-passing gate was re-selected. Amendment 2's hash is gated in N-CHK0.
- **Bug found and fixed before this run, disclosed:** the first implementation of the new
  wrong-arm check always read the *dseq* column, which for the sequence-only plant is its
  MATCHED arm - it would have failed that gate spuriously. Caught by a 3-seed, 200-draw
  sanity check before the long run; fixed so each plant's wrong arm is its own other
  feature (dseq for 3D-only, d3 for sequence-only).

### Planted results (the confusion matrix Amendment 2 item 1 asks for)

| plant (truth) | 3D-LOCAL | SEQUENCE-LOCAL | BOTH-LOCAL | NEITHER-RESOLVED |
|---|---|---|---|---|
| 3D-only | **93** | 0 | 7 | 0 |
| sequence-only | 0 | **67** | 33 | 0 |
| none | 3 | 1 | 0 | **96** |

- 3D-only: correct word **0.930** (gate >= 0.80 PASS); wrong-arm (dseq|d3) fires **0.070**
  (gate <= 0.15 PASS).
- sequence-only: correct word **0.670** (gate >= 0.80 **FAIL**); wrong-arm (d3|dseq) fires
  **0.330** (gate <= 0.15 **FAIL**) - 33 of 100 seeds come back BOTH-LOCAL.
- none: NEITHER-RESOLVED **0.960** (gate >= 0.85 PASS); 4/100 fire any word.
- Seed 3 (the seed that failed the single-seed form, now included per item 1) is one of the
  seven 3D-only BOTH-LOCAL outcomes.
- Everything else still passes: all six input hashes plus Amendment 2's; frame/H rows;
  A222V anchors (3.34e-11, 0.000e+00); D1 recomputation max|diff| 4.96e-10 over 96;
  same-site rank 2/19; cell/Pool composition; **G-N5 all five checks exact** (identity,
  background_boot draw-by-draw, slow closed-form reference max|diff| 1.86e-15, contrast
  rebuild, Phase 1 CI 0.000e+00 both endpoints); torch never imported.

### Diagnosis: this is a real property of the frozen statistic on this geometry, not a seed and not a bug

Point partials over the same 100 seeds (no bootstrap, ~1 s):

| quantity | mean | sd | min | max |
|---|---|---|---|---|
| 3D-only plant, WRONG arm (dseq given d3) | **+0.058** | 0.088 | -0.101 | +0.288 |
| 3D-only plant, matched (d3 given dseq) | +0.760 | 0.036 | +0.659 | +0.835 |
| sequence-only plant, WRONG arm (d3 given dseq) | **+0.160** | 0.089 | -0.029 | +0.337 |
| sequence-only plant, matched (dseq given d3) | +0.678 | 0.056 | +0.537 | +0.780 |
| none plant, d3 given dseq | +0.008 | 0.089 | -0.171 | +0.219 |

- **The sequence-only plant's wrong arm carries a systematic +0.16 offset in essentially
  every seed** (only 1 of 100 falls below -0.03), while the pure-noise plant is unbiased
  (+0.008). So the machinery does not invent signal from noise; the leakage appears only
  when the *other* feature carries the signal.
- Mechanism: with rho = z(dseq) + 0.4*eps, rank(rho) differs from rank(dseq) by a term
  whose expectation over eps is a **deterministic nonlinear function of dseq** (the
  expected-rank curvature). With the pool's `spearman(d3, dseq) = 0.776`, that curvature
  correlates +0.16 with `resid(d3 | dseq)`. The same effect in the other direction is only
  +0.058, so the leakage is strongly asymmetric.
- Consequences, stated plainly: (i) on this Pool P (n = 117), a genuinely
  sequence-driven signal is reported as BOTH-LOCAL about a third of the time; (ii) a real
  BOTH-LOCAL word cannot be distinguished from a sequence-driven signal at the word level -
  only the sign/size of the two partials can; (iii) **neither more bootstrap draws nor
  more backgrounds fixes it** - it is a bias in the population statistic, not a CI-width or
  sampling artifact, and Pool P's composition is frozen; (iv) under Amendment 2 item 5,
  section 6 must print **NO WORD** with all numbers intact, and section 5 is unaffected.
- This is the planted gate doing its job: it detected that the frozen section 6 word is not
  reliable in the sequence direction **before** any real score exists, rather than after.

### Blocked pending Arnav's decision

A7e stays at exit 3. A third amendment would be needed to change anything, and every
available route is a design choice, not a bug fix: accept the measurement and run section 6
as NO WORD with the confusion matrix printed beside it (Amendment 2 item 5 as written);
keep the gate hard-failed and leave A7/A9 blocked; or change the frozen statistic (e.g. a
collinearity-aware or null-calibrated partial, or a permutation null in place of the
bootstrap CI) - which would need its own pre-registration and re-gating. Nothing was
tuned toward a pass.

### AMENDMENT 3 (issued after the Amendment-2 plant results; disclosed as such)

Verbatim decision, recorded here in full as instructed; saved UNEDITED as
`docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_3.md`
**sha256 `266feb5549ec50d4fd21c0447de2ba83c8a33e72d50be547a5e1f1cf72cc5a42`** (8 lines).
None of the three earlier preregs was edited - v1 `167847a9...4359e`, Amendment 1
`f56134f7...df58a`, Amendment 2 `b636a4d1...2b55a` before and after (all hash-gated PASS in
the run below).

> ARNAV'S DECISION (made before any real neighbour-arm score exists; made AFTER seeing the Amendment 2 plant results, which is disclosed here). Record it verbatim in the A7e log entry AND save it, unedited, as docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_3.md, then log its sha256. Do NOT edit v1, Amendment 1 or Amendment 2.
> Amendment 3 to NEIGHBOUR_ARM_PREREG_v1 (supersedes only the section 6 partial-correlation statistic and G-N4's gating of it):
> 1. Diagnosis accepted: the leakage is residual confounding from a linear-on-ranks control. E[rank(rho) | other distance] is a smooth nonlinear function of the RAW other distance because the pool's distances are skewed and collinear (spearman(d3, dseq) = 0.776), so a linear control leaves curvature that correlates with the other distance's residual.
> 2. New statistic for section 6 (replaces the linear rank-residual partial): flexible-control partial Spearman. For the d3 partial: regress rank(rho_b) on a natural cubic spline basis of RAW dseq (4 degrees of freedom, interior knots at the 25th, 50th and 75th percentiles of dseq over the pool) by OLS; regress rank(d3) on the same basis; the partial is the Pearson correlation of the two residual vectors. The dseq partial is the mirror image (spline basis of RAW d3, 4 degrees of freedom). The background-level bootstrap CIs (10,000 draws, SEED 0) are unchanged and recompute the spline fits per resample.
> 3. The same four words and the same rule (CI excludes zero versus includes zero) apply; the cell means and the C2-C4 and C3-C4 contrasts are unchanged.
> 4. G-N4 is re-run on the new statistic over the same 100 seeds (0..99) with Amendment 2's criteria unchanged: correct word in at least 80% of seeds for each single-arm plant; wrong-arm CI excludes zero in at most 15% of seeds; none-plant returns NEITHER-RESOLVED in at least 85% of seeds. No seed, noise scale or threshold changes. One implementation exactly as written; no further tuning.
> 5. Pre-committed fallback, no further amendment needed: if the new statistic meets every criterion, section 6 words are produced by it, with the planted confusion matrix printed beside them. If it fails ANY criterion, section 6 returns NO WORD (all numbers still reported, planted confusion matrix printed), exactly as Amendment 2 item 5, and the earlier linear statistic is reported as a labelled secondary only. Either way, record G-N4's measured status honestly (PASS or FAIL per the criteria) with the mechanical consequence, mark A7e complete, and proceed to A8 and A9.
> 6. Section 5 (position versus region) and all other gates are unaffected.

End of verbatim amendment.

---

## [A7e, attempt 3 under Amendment 3] - G-N4 PASSES on the flexible-control statistic - A7e COMPLETE

**Date:** 2026-10-03 (session 4a). **Status: COMPLETE (GATE PASS, exit 0)** - 32 PASS, 0 FAIL,
1 PENDING (G-N3: 0/50 new backgrounds scored, correct before the night's scoring).
Per Amendment 3 item 5, section 6 therefore takes the **first branch**: on real data its
words will be produced by the flexible-control statistic with the planted confusion matrix
printed beside them, and A8/A9 proceed.

- **Script:** `scripts/172_neigh_analysis.py` sha256
  `0534a301ee3377c78bf2b4d7f63ee0d621a535b8174ca78d1e99a1bd179079f4`.
- **Record:** `PHASE4_A7_ANALYSIS_FULL_OUTPUT.txt`, 139 lines, sha256
  `94d49cd5bd08032613866fda51bc13d306c37087afbdc6521bcc13207c1993a3`, run
  `N_BOOT=10000 SEED=0 venv/bin/python3 scripts/172_neigh_analysis.py --mode full`,
  923.6 s (G-N4 893 s). The Amendment-2 record (`PHASE4_A7_ANALYSIS_SMOKE_OUTPUT.txt`,
  sha256 `ae950f6e3dec8e4f0e259926576b808d236cc99caff86e14383b6b8e2f20d607`) is preserved
  and is where the linear statistic's confusion matrix lives.

### Implementation, pre-registered as N-AN15 before the run

- **Flexible-control partial Spearman** exactly as Amendment 3 item 2 writes it: average
  ranks (scipy `rankdata("average")`, identical to `p4c._rank`); `rank(rho)` and
  `rank(feature)` each regressed by OLS on a natural cubic spline basis of the **RAW** other
  distance; partial = Pearson correlation of the two residual vectors; d3 partial controls
  dseq, dseq partial controls d3. NaN semantics mirror `p4c.partial_spearman`.
- **Knots** are the pool's 25th/50th/75th percentiles of that raw distance, computed ONCE
  from the full 117-background pool and held fixed (a resample's values always lie inside the
  pool's range, so the fixed boundary knots are always valid); the spline FITS and the ranks
  are recomputed on every resample, as Amendment 3 requires. Printed in the record:
  d3 knots `[3.805, 10.161, 20.112, 36.759, 76.194]`, dseq knots `[1.0, 26.0, 67.0, 163.0,
  428.0]` (boundary knots at the pool's min/max).
- **Parametrisation DISCLOSURE (the one ambiguity in Amendment 3):** its parenthetical pins
  both "4 degrees of freedom" and three interior knots, and in the standard natural-spline
  family m interior knots give m+1 basis functions (patsy's own `cr(df=4)` uses only TWO
  interior knots), so the two cannot both hold in one parametrisation. The three named knots
  were treated as operative - they are the explicit, unambiguous part - and the basis is
  patsy's canonical `cr(x, knots=[q25,q50,q75])`: **five** spline columns, rank 5, condition
  4.614 (d3 control) and 4.220 (dseq control). patsy is far too slow to call inside a
  6-million-draw loop, so the basis is computed by a numpy replication of patsy's
  `mgcv_cubic_splines` construction and **gated against patsy itself** (N-CHK4: max|diff|
  **0.000e+00** over three probes - pool dseq, pool d3, a random lognormal).
- **Two extra self-checks pre-registered** for the new statistic (stricter, never looser):
  G-N5(iv) flex identity (max|diff| 0.000e+00) and G-N5(v) flex draws vs a slow QR-based OLS
  rebuild (max|diff| **5.83e-16**, both arms, all 10,000 draws, 0 NaN mismatches).
- G-N5's mechanics vector is unchanged from the first pre-registration (the seed-3 3D-only
  plant), so no already-passing gate was re-selected; the linear statistic is kept and
  reported as a labelled secondary in section 6; cell means and the C2-C4/C3-C4 contrasts are
  untouched.
- **Smoke discipline:** no reduced-draw smoke of the production configuration was run,
  because every bootstrap count in this script is pre-registered as FIXED at 10,000
  (N-AN9/N-AN11) and the only `N_BOOT`-dependent quantity - section 6's CIs - is PENDING
  pre-night, so a smoke would be byte-identical to the full run apart from the banner. A
  mechanical smoke WAS run first through a throwaway wrapper that overrode the module's
  `GATE_N`/`PLANT_SEEDS`/`P1_N` to 200/3/200 to exercise every code path end to end; it
  produced no reported number (its only FAIL was the Phase 1 CI, expected at 200 draws) and
  the wrapper is not a supported invocation.

### Planted results on the flexible statistic (Amendment 3 item 4, criteria unchanged)

| plant (truth) | 3D-LOCAL | SEQ-LOCAL | BOTH-LOCAL | NEITHER | correct-word rate | wrong-arm fire rate |
|---|---|---|---|---|---|---|
| 3D-only | **97** | 0 | 3 | 0 | **0.970** (gate >= 0.80) | **0.030** (gate <= 0.15) |
| sequence-only | 0 | **99** | 1 | 0 | **0.990** (gate >= 0.80) | **0.010** (gate <= 0.15) |
| none | 3 | 4 | 0 | **93** | - | NEITHER-RESOLVED **0.930** (gate >= 0.85) |

- **All five G-N4 criteria PASS.** Seed 3 remains included and still misclassifies the 3D-only
  plant as BOTH-LOCAL (Amendment 2 item 1: included, never skipped).
- **Honest side effect, disclosed:** the none-plant's NEITHER-RESOLVED rate *fell* from
  0.960 (linear statistic, Amendment-2 run) to **0.930** - the flexible control is slightly
  more willing to call a word when there is nothing there (7/100 vs 4/100 seeds fire). It
  passes the frozen 0.85 bound, but the fix for the sequence channel cost a little
  specificity, and both numbers are on record.
- The linear statistic's confusion matrix was **not** recomputed (Amendment 3 item 4 re-runs
  G-N4 on the new statistic only); it stays in the Amendment-2 record, and the script prints
  a pointer to it in place of a second 15-minute loop.
- Everything else unchanged and still exact: all seven input hashes (v1, Amendments 1-3,
  roster, cells, D1, stored 3d); frame/H/H-rows 654/455/7526; A222V anchors (3.34e-11 and
  0.000e+00); **D1 recomputation max|diff| 4.96e-10 over all 96**; same-site rank **2/19**;
  cell and Pool-P composition; G-N5(i)-(iii) exact (Phase 1 CI **0.000e+00** both endpoints);
  torch never imported.
- Section 5 printed SKIPPED (complete NB 6/46 < 30, Amendment 1 item 5) and section 6
  PENDING (Pool P 67/117) - both correct pre-night; their machinery is now ready for the
  night's SA1/SA2.

### What the planted gate actually bought

The whole three-attempt arc is a real result about the frozen design, not a code problem:
with a linear-on-ranks control the two distance channels were **not separable** on this pool
(spearman(d3, dseq) = 0.776) - a sequence-driven signal was called BOTH-LOCAL in 33% of
seeds - and the flexible control removes that leakage (1%) while leaving the 3D channel
intact (97/100). Section 6's word can now be produced by the flexible statistic, but it
should still be read beside the printed confusion matrix: when the truth is 3D-only, the word
would be BOTH-LOCAL or worse **3.0%** of the time, and with no signal at all **7.0%** of the
time. A8 and A9 proceed next per Amendment 3 item 5.

---

## [A8a] - Module L checkpoints: cache survey + the one authorised download - PASS

**Date:** 2026-10-03 (session 4a). **Status: PASS** - both required checkpoints present and
verified to load with the network unreachable. `PHASE4_A8_DOWNLOAD_PROVENANCE.txt`,
61 lines, sha256 `42afd5c5d505314d3034589a5e3ec94361d2f5949c79f48d23bdfcb23f674dd3`.

### Cache survey (before any download)

- Present and usable as-is (no download): `esm2_t33_650M_UR50D.pt` 2,604,537,549 B (+ its
  contact-regression), `esm2_t30_150M_UR50D.pt` 592,774,773 B (+ its contact-regression).
  Also present but **not used** by module L and untouched: `esm2_t36_3B_UR50D.pt`.
- Missing: **`esm2_t12_35M_UR50D`** - the single authorised download.
- Free disk before: **20.66 GiB** (requirement >= 5 GiB).

### The authorised download (A8a's exact scope: only these two files)

Both URLs HEAD-verified first, then fetched into the standard torch hub cache
(`~/.cache/torch/hub/checkpoints/`). Nothing else was requested.

| file | URL | HTTP | bytes | sha256 |
|---|---|---|---|---|
| esm2_t12_35M_UR50D.pt | `https://dl.fbaipublicfiles.com/fair-esm/models/esm2_t12_35M_UR50D.pt` | 200 | 134,095,705 | `7f21e80e61d16a71735163ef555d3009afb0c98da74c48e29df08606973cc55e` |
| esm2_t12_35M_UR50D-contact-regression.pt | `https://dl.fbaipublicfiles.com/fair-esm/regression/esm2_t12_35M_UR50D-contact-regression.pt` | 200 | 1,959 | `16641e05d830d0ce863dd152dbb8c2f3ddfa3c3ec2a66080152c8abad01d8585` |

- Free disk after: **20.54 GiB** (requirement >= 5 GiB met).
- The contact-regression file is required: `esm.pretrained._has_regression_weights` is True
  for every ESM-2 model, and the loader fetches it from the `fair-esm/regression/`
  directory (not `models/`).

### Verification and G-L1 parameter counts

With **every socket blocked** (so any network use raises), the package's own hub loaders -
which consult the cache first - load all three checkpoints: **650M 651,043,254 parameters
(33 layers, dim 1280), 150M 148,140,154 (30 layers, dim 640), 35M 33,501,394 (12 layers,
dim 480)**. The cache is therefore complete; module L is not BLOCKED.

### Disclosed incident - an unintended re-download of the same two files

My first attempt to prove "loading does not download" set `torch.hub`'s directory to an
empty scratch dir. That removes the cache **hit**, so the loader treated the checkpoints as
missing and downloaded `esm2_t12_35M_UR50D.pt` and `esm2_t30_150M_UR50D.pt` plus their two
regression files into that scratch directory (706 MB). No other model, URL or destination
was involved; the intended cache copies were not overwritten, and I re-verified their
sha256s **unchanged** after the incident (values in the table above). The scratch dir was
deleted at once and free disk returned to 20.54 GiB. The verification was then redone
correctly (sockets blocked, cache hit), as recorded above. Cause of the mistake: the test
manipulated the very thing it was trying to verify instead of blocking the network.

### Operational finding for script 173 (no library edit)

`esm.pretrained.load_model_and_alphabet_local(path)` **fails** on these checkpoints under
the installed torch: 2.6+ defaults `torch.load(weights_only=True)` and the files contain an
`argparse.Namespace`. The hub path (`esm.pretrained.esm2_*_UR50D`) works because
`torch.hub.load_state_dict_from_url` still passes `weights_only=False`, and it hits the local
cache first. `scripts/lib/esm_scoring.py` is NOT edited (AGENTS 7): script 173 must load
through the package's `pretrained.*` entry points and must never call the local loader.

Next: A8b (`scripts/173_ladder_score.py`, `--model {650M,150M,35M}`, gates G-L1..G-L3),
then A8c timing smoke, then A8d analysis (script 174, G-L4/G-L5).

---

## [STATE-VERIFY] - Continuation of session 4a: state verified before resuming at A8b - PASS

**Date:** 2026-10-03 (session 4a, continuation). **Status: PASS** - every continuation
precondition holds. No earlier entry was edited; nothing was re-run; no result was changed.
Re-read in full before resuming: `AGENTS.md` (222 lines),
`docs/tasks/phase4-strengthening/PHASE4_STRENGTHENING.md` (475 lines including the five
frozen appendices A-E), `STATE.md`, and this log (1,156 lines at that point).

### 1. Entries that exist (expected: A0 through A7e and A8a PASS)

`grep -n "^## \["` on this log returns, in order: SESSION HEADER, **[A0]**, **[A0-rerun]**,
**[A1]**, **[A2]**, **[A3]**, **[A4]**, **[A5]**, **[A6]**, **[A7a-A7b]**, **[A7c-A7d]**,
**[A7e]**, **[A7e, attempt 2 under Amendment 2]**, **[A7e, attempt 3 under Amendment 3]**,
**[A8a]**. A0's first pass is the FAIL (AC power) that A0-rerun superseded; both are retained.
Statuses as logged: A0-rerun PASS, A1 PASS, A2 PASS, A3 PASS, A4 PASS, A5 PASS (U-2
UNVERIFIED-LABELS by its pre-registered fallback), A6 PASS, A7a/A7b PASS, A7c/A7d PASS, A7e
COMPLETE after three attempts (two BLOCKED, both logged verbatim), A8a PASS. Nothing is
missing and nothing is duplicated.

### 2. Five pre-registrations plus Amendments 1, 2, 3 - all hashes unchanged

| file | lines | sha256 now | expected (doc table / logged) | match |
|---|---|---|---|---|
| MECH_ANCHOR_PREREG_v1.md | 56 | `8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b` | doc table | yes |
| UTILITY_PREREG_v1.md | 32 | `744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531` | doc table | yes |
| GB1_LOCALITY_PREREG_v1.md | 26 | `10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8` | doc table | yes |
| NEIGHBOUR_ARM_PREREG_v1.md | 42 | `167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e` | doc table | yes |
| MODEL_LADDER_PREREG_v1.md | 26 | `eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3` | doc table | yes |
| NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md | 9 | `f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a` | A7a/A7b entry | yes |
| NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md | 8 | `b636a4d193efa16ed36e7d7feeb5a357c99cd5f202437bf100a55b80f822b55a` | A7e-2 entry | yes |
| NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_3.md | 8 | `266feb5549ec50d4fd21c0447de2ba83c8a33e72d50be547a5e1f1cf72cc5a42` | A7e-3 entry | yes |

Line counts match the doc's table (56 / 32 / 26 / 42 / 26). The three amendments are Arnav's
saved-verbatim decisions; the frozen blocks and all three amendments are unmodified.

### 3. Roster from A7b unchanged

```
675a24f1963878568e65b6d630e25e9ce649627c3f02ab0d5e65ec438f2d85d6  data/processed/phase4/neigh/roster_v1.csv
sidecar roster_v1.sha256: 675a24f1963878568e65b6d630e25e9ce649627c3f02ab0d5e65ec438f2d85d6
51 lines (50 backgrounds + header)
```
Matches the A7a/A7b entry exactly, so the frozen roster the night will score against is
byte-identical to the one hashed before any scoring.

### 4. No real neighbour-arm or ladder score output exists

- `data/processed/phase4/neigh/` contains ONLY `roster_v1.csv`, `roster_v1.sha256`,
  `eligible_cells_v1.csv` - **0** `bg_*.csv` files (the real output dir is untouched).
- `data/processed/phase4/neigh_nonH/` - absent (night B, SB4 owns it).
- `data/processed/phase4/ladder/` - absent (no ladder score has ever been produced).
- `data/processed/phase4/neigh_scratch/` holds only the A7c/A7d timing and G-N2 artifacts
  (`gate_n2_av220_run1.csv`, `run2.csv`, `timing/bg_N_214_LV.csv`, `bg_N_46_RL.csv`,
  `bg_N_182_IV.csv`, `timing/manifest.csv`) - scratch by construction, never read by the
  analyses.
So the out-of-sample modules N and L are still genuinely out of sample.

### 5. The three cached checkpoints, hashed now, against A8a

| checkpoint | sha256 now | sha256 logged in A8a | match |
|---|---|---|---|
| `esm2_t12_35M_UR50D.pt` | `7f21e80e61d16a71735163ef555d3009afb0c98da74c48e29df08606973cc55e` | `7f21e80e61d16a71735163ef555d3009afb0c98da74c48e29df08606973cc55e` (downloaded) | yes |
| `esm2_t12_35M_UR50D-contact-regression.pt` | `16641e05d830d0ce863dd152dbb8c2f3ddfa3c3ec2a66080152c8abad01d8585` | `16641e05d830d0ce863dd152dbb8c2f3ddfa3c3ec2a66080152c8abad01d8585` (downloaded) | yes |
| `esm2_t33_650M_UR50D.pt` (650M, cached since Sep 11) | `ea9d0522b335a8778dea6535a65301f10208dece28cd5865482b0b1fc446168c` | not hashed by A8a (pre-existing cache file; A8a logged size 2,604,537,549 B) | first hash recorded now |
| `esm2_t30_150M_UR50D.pt` (150M, cached, never downloaded) | `881c7176cf198ef8dec26a3c375d40eb58d0c33df95c22562ca6cc6d3f812c62` | not hashed by A8a (pre-existing cache file; A8a logged size 592,774,773 B) | first hash recorded now |

The two files A8a downloaded are byte-identical to what its entry logged, so the disclosed
re-download incident did not touch the intended cache copies. **Disclosure:** A8a recorded
sizes for the two pre-existing checkpoints but not their sha256; the two values above are
recorded here for the first time and are what `STATE_FOR_LAUNCH.md` will pin.

### 6. Power and swap (the two conditions the doc requires before heavy work)

```
$ pmset -g batt
Now drawing from 'AC Power'
 -InternalBattery-0 (id=22020195)	80%; AC attached; not charging present: true

$ sysctl vm.swapusage
vm.swapusage: total = 0.00M  used = 0.00M  free = 0.00M  (encrypted)
```
AC Power: **PASS** (80%). Swap used **0.00M** - the machine has been restarted since A0/A0-rerun
(the battery id is now 22020195, not 22544483), so the swap condition is in its best state
and the nights' precondition ("if swap was above 2 GB since the last reboot, restart first")
is satisfied with nothing to do.

### 7. Repository state

`git log -1` = `856d2f60c9d614fce7f6c5564107d72c95d73334 2026-10-02T19:43:49-04:00` (unchanged;
I have committed nothing). `git status --short` shows only the pre-existing `.gitignore`,
`README.md`, `requirements.txt` modifications and untracked data/scripts - nothing staged by
me. The planning doc is clean against git (A0-G1 still PASS), and `scripts/lib/*`,
`PHASE2_PREREG.md` and every earlier log are untouched.

Verdict: **PASS - resume at A8b** (`scripts/173_ladder_score.py`, gates G-L1..G-L3), then A8c
timing smoke, A8d analysis (script 174, G-L4/G-L5), then A9 exactly as the doc specifies.

---

## [A8b-A8c] - Module L ladder scorer, gates G-L1/G-L2/G-L3 and the timing smokes (scripts/173_ladder_score.py) - PASS

**Date:** 2026-10-03 (session 4a). **Status: PASS** - the 650M gate run exits 0 with G-L2 and
all three G-L3 sub-gates PASS; both timing smokes exit 0. **No ladder score exists in any real
output directory**: `data/processed/phase4/ladder/{650M,150M,35M}` contain 0 files each
(three empty directories were created by the pre-scan `mkdir`); everything written went to
`data/processed/phase4/ladder_scratch/`. Module L's out-of-sample status is intact.

- **Script:** `scripts/173_ladder_score.py` **sha256
  `12f2f140fc212ab3b0e23a1bc74e8f8bc51155e7e82951d7faa5cb1f0f6eabb8`**.
- **Pre-registered before the first run (LD-DEC1..LD-DEC12 in the docstring, printed at
  startup):** hub entry points only (`esm.pretrained.esm2_*`) because
  `load_model_and_alphabet_local` is broken under torch >= 2.6 (A8a), with
  `scripts/lib/esm_scoring.py` untouched; cache pre-check before the loader, a missing
  checkpoint is exit 3 and never a download; roster = A222V + the 96, frame = H minus own
  position; delta against **this model's own** wild-type arm; output layout and 124's
  imported skip logic with its atomic-write pattern quoted (124 lines 235-264); G-L1/G-L2/G-L3
  exactly as the frozen ladder states, plus ONE added stricter sub-check; `--gate-only` runs
  the gates and writes nothing; timing printed beside the doc's pass count with no budget
  applied (A9 sets budgets); N_BOOT/SEED printed and unused.
- **Input pins (G-L0, all PASS):** `MODEL_LADDER_PREREG_v1.md` `eafe37a8...db3`,
  `phase2_arm_roster.csv` `9b31721a...9445b`, `phase2/bg_AV_220.csv` `2dc13f80...752e`,
  `esm2_wt_scores.csv` `e4d3af3d...1581c`.

### Roster and pass counts (the doc's figure recomputed, rule 16)

- 97 unique backgrounds (A222V + the 96: arms G40/V38/S18), **A222V is NOT among the 96**,
  **0 duplicate (position, mutant) pairs**.
- **Exact total = 44,533 passes** = 44,078 background passes + 455 wild-type passes. The
  planning doc's formula `97 x 455 + 455 = 44,590` **overstates by exactly 57**: 57 of the 97
  backgrounds have their own position inside H, so each gets 454 rather than 455. (A222V's own
  position 222 is NOT in H, so it gets all 455.) Both numbers are printed by the script on
  every run; the exact one is used for the projections.

### G-L1 / G-L2 / G-L3 results (650M gate run, 953.6 s)

```
[PASS] LD-DEC2 cache pre-check: both checkpoint files present
[PASS] G-L1 650M parameter count == the A8a-measured 651,043,254: got 651,043,254 (|diff| 0)
[PASS] G-L1 650M layers / embed_dim match the A8a measurement: 33 layers, embed_dim 1280
[PASS] G-L2 AV_220 on H reproduces the cached rows (score AND delta) to 1e-06:
       8,626 rows, max|d score| 1.776e-15, max|d delta| 1.776e-15
       (A7c's G-N2 measured 1.776e-15 for this same comparison on this device)
[PASS] G-L2(b) ADDED, stricter: this run's 650M wild-type arm reproduces the cached
       esm2_wt_scores.csv to 1e-06: 8,645 rows, max|d score| 1.776e-15
[PASS] G-L3(a) AV_220 scored twice is identical to 1e-06 (reuses G-L2's two runs): max|d| 0.000e+00
[PASS] G-L3(b) the wild-type residue's log-odds is exactly 0 at H position 2 (V): 0.0;
       alphabet round-trip True; 19 entries excluding wt True
[PENDING] G-L3(c) coverage: PENDING: 0/97 backgrounds scored for 650M yet
```
G-L2's agreement is float64-exact and **equal to the value A7c measured independently**
through a different script - the two agree digit for digit. G-L2(b) is not in the frozen
text; it is added because that wild-type arm is the delta reference for every background of
the model (stricter, never looser, disclosed as ADDED).

### A8c timing smokes (the doc said "measure, do not assume")

| model | median s/pass | per-bg | full-ladder projection (44,533 x s x 1.25) | speed vs 650M |
|---|---|---|---|---|
| 650M (A7d/A8b measured) | 0.643 - 0.688 | 0.613 / 0.643 / 0.655 | 603 min at 0.643 (not a night stage: 650M is cached) | 1x |
| **150M** | **0.2414** | 0.2410 / 0.2414 / 0.2436 | **224 min** | **2.7x faster** |
| **35M** | **0.0762** | 0.0762 / 0.0762 / 0.0763 | **71 min** | **8.4x faster** |

- Each smoke scored the wild-type arm on H plus the first 3 roster backgrounds (A222V,
  A222_C, A222_D) into scratch; per-model wild-type arms measured 0.2416 and 0.0766 s/pass,
  consistent with the background rate.
- Both measured ratios land inside the planning doc's guesses (150M "about 2-4x", 35M "about
  8-15x") - reported as a check of the guess, not as an input.
- **A9 consequence, stated now:** SB1 (150M) projects 224 min and SB2 (35M) 71 min at the
  1.25 factor, i.e. 295 min of the 450-minute night-B ceiling before the nonH neighbour
  scoring (SB4) and the analysis stages. A9 must apply the overflow rule explicitly.

### Three bugs of mine, all fixed BEFORE any ladder score was written (AGENTS 6 disclosure)

1. **`AttributeError: 'DataFrame' object has no attribute 'delta_new'`** - G-L2 compared the
   raw scorer output against the cached rows without first attaching this model's delta, so
   the merge suffixes did not exist. Fixed by attaching the delta to both gate runs.
2. **G-L2 then printed FAIL with max|diff| = 2.983** - **this was my error, not a finding**:
   the gate hardcoded `wt_seq[:221] + "V"`, which builds **A222V**, while the cached file is
   **AV_220 = A220Val at position 220**. Scoring A222V and comparing it with A220V's cached
   rows cannot agree. The own position is now read from the roster and never hardcoded
   (`assert wt_seq[own-1] == wt_aa` is printed in the roster gate). A separate
   `AttributeError` on the WT-arm merge (columns `score` vs `esm2_score` do not overlap, so no
   `_new`/`_cache` suffixes exist) was fixed in the same pass.
3. **`ERROR: the wild-type arm has no score for 8,645 keys ... Exit 3`** on the 150M smoke -
   for models other than 650M the wild-type arm is scored in the *write* section, and
   `wt_map` was never populated from it, so the delta join aborted. The script's own
   completeness check caught it exactly as designed (exit 3, no background file published).
   Fixed by populating `wt_map` from the freshly scored arm.

**Also fixed, a misleading printed number:** the first 150M smoke projected the
*3-background* pass count (1,820 x s x 1.25 = "9 min") instead of the full roster's 44,533,
because `--limit-backgrounds` truncated the roster the projection was computed from. A9 needs
the full-stage number, so the projection is now always computed on the full roster and the
run says when it covered only a prefix. The superseded run is kept as
`PHASE4_A8C_TIMING_150M_ATTEMPT1_DEFECT_OUTPUT.txt`; no gate, threshold or decision changed,
only the printed projection.

### Records

- `PHASE4_A8B_GATE_OUTPUT.txt` (56 lines, sha256 `d682b1c32ba380187dd30c4b325c0ca239b92a8a18f19865d7a85c97396762b4`) - the 650M gate run, exit 0.
- `PHASE4_A8B_GATE_ATTEMPT1_FAIL_OUTPUT.txt` (sha256 `306518674d33d1bc1749a7d5a911eff78f8e243252c91647aba6670a0ca1ce71`) - the first attempt, which stopped on the delta-column bug.
- `PHASE4_A8C_TIMING_150M_OUTPUT.txt` (71 lines, sha256 `9abb25fdfb70c8a09ebbf0997da04b049b00fb7492a6cb4f0816763ab26d6cd8`) and `PHASE4_A8C_TIMING_35M_OUTPUT.txt` (71 lines, sha256 `a8396fb1b04031df00174e2d48de6ffdf8d272ce3da3259bc5e9a766efebc487`), both exit 0.
- `PHASE4_A8C_TIMING_150M_ATTEMPT1_DEFECT_OUTPUT.txt` (sha256 `e9adfaa05c20b45fb094071fd1913ec6d0d22fb6648e6a9b8eb75cd81df78026`) - the superseded projection.
- Scratch only: `ladder_scratch/gate_g_l2_650M_av220_run1.csv` + `run2.csv`,
  `timing150/{wt_H,bg_A222V,bg_A222_C,bg_A222_D}.csv` + manifest,
  `timing35/{...}` + manifest, and an empty `gateonly35/`.
- One heavy process at a time throughout (rule 15): the 35M gate-only mechanical check, the
  650M gate run and each smoke ran alone in the foreground.

Verdict: **PASS.** Module L's scorer is built and gated; the ladder is projected at 224 min
(150M) and 71 min (35M). Next: A8d (`scripts/174_ladder_analysis.py`, no torch, frozen
section 2, gates G-L4 and G-L5).

---

## [A8d] - Module L ladder analysis: the cached 650M column, gates G-L4 and G-L5 (scripts/174_ladder_analysis.py) - PASS

**Date:** 2026-10-04 (session 4a). **Status: PASS** - smoke 26 PASS / 0 FAIL / 4 PENDING,
full run **26 PASS / 0 FAIL / 4 PENDING**, exit 0 both. The four PENDING are the 150M and 35M
columns and the two cross-model agreements, which need the night's SB1/SB2 scores; they are
correct pre-night states, not skips. **No score file was written and the ladder directories
are still empty** (`ladder/{650M,150M,35M}` = 0 files each), so module L remains out of sample.
`torch in sys.modules: False` (rule 1).

- **Script:** `scripts/174_ladder_analysis.py` **sha256
  `b638d3c6e8abbaed894858593af8ffdb51395e1e3d7f42a9db39adbfa4b5f3b6`** (no torch anywhere).
- **Pre-registered before the first run (LD-AN1..LD-AN11, printed at startup):** inputs
  sha-pinned; frame H minus own position; delta against **that model's own** wild-type arm and
  the WT arm never counted as a background; a model column requires every background at >=95%
  coverage or it is PENDING with no numbers; the five frozen quantities each with its own
  resampling unit (position clusters inside a background, backgrounds across backgrounds); the
  word from `p4c.word_ladder`; cross-model agreement on common H rows; G-L4's five planted arms
  with seeds 101/102/103/1000/105+106 pinned and the null arm's per-plant CI pinned at 1,000
  draws so its fire rate cannot move with N_BOOT; G-L5's identity / draw-by-draw / Phase 1 CI.

### The 650M column (the only one computable today) - frozen section 2, full run

| frozen quantity | value | CI / count | unit |
|---|---|---|---|
| (i) rho_A222V on H | **-0.090021683** | **[-0.122385, -0.056046]** (10,000 draws) | position clusters |
| (ii) p_spec_H(neg) | **0.050633** (3/78) | p_spec_H(abs) 0.050633 (3/78) | exact rank count |
| (iii) partial rho_H given this model's S_W | **-0.067209** | [-0.099734, -0.033553] | position clusters |
| (iv) gradient Spearman(rho_b, d3), 67 resolved nulls | **+0.713319** | [+0.566655, +0.808932] | backgrounds |
| (v) shift confound Spearman(rho_b, mean\|delta_b\|), 96 backgrounds | **-0.612697** | [-0.732776, -0.456234] | backgrounds |

- **WORD (650M): MODEL-REPLICATES** (CI lies below zero AND p_spec_H(neg) = 0.0506 <= 0.10).
- **Consistency worth recording:** quantity (iii) reproduces A4's Module-M H-view partial
  (-0.067208910, CI [-0.099734, -0.033553]) to every printed digit from an independent path --
  different script, different bootstrap plumbing. Quantity (i) reproduces the frozen anchor
  -0.090021683 to 3.34e-11, and the ADDED LD-AN4 check confirms all 96 background rho_H values
  equal the D1 table to **max|diff| 4.956e-10**. Module L is reading exactly the inputs module
  N reads.
- **Both gradient/confound CIs exclude zero and are large** (0.71 and -0.61). They are
  reported as numbers with their units and no word -- frozen section 3 defines a word only for
  the anchor's CI and p_spec. Reading: rho_b is *less* negative the further a null sits from
  residue 222 (a locality gradient), and *more* negative the larger that background's mean
  |delta| is (the Phase 1 shift-magnitude confound, still fully present at 650M).

### Gates

- **G-L0** all six input hashes PASS.
- **G-L4 (HARD), all five planted arms PASS** (`G-L4 wall 362 s`):
  - A1 signal -> **MODEL-REPLICATES** (rho_A -0.5666, CI [-0.5880, -0.5446], p_spec 0.0127 = 0/78);
  - A2 gradient -> gradient **-0.9997**, CI [-1.0000, -0.9982], excludes zero negatively;
  - A3 shift confound -> confound **-0.9991**, CI [-0.9994, -0.9971], excludes zero;
  - A4 null -> fire rate **0.020** (2/100) <= 0.15; words seen {MODEL-DOES-NOT-REPLICATE: 98, MODEL-REPLICATES: 2};
  - A5 identical-model -> per-background median **1.0**, across-background **0.9999999999999999** (1 ulp from 1); independent-model -> median +0.0004, across +0.0865, both < 0.15.
  - **Disclosure:** A2 and A3 are near-saturated plants (-0.9997, -0.9991), so they show the
    machinery responds in the planted direction but say nothing about sensitivity at realistic
    effect sizes. A4's two MODEL-REPLICATES draws are the expected ~5%-tail behaviour of a
    1,000-draw percentile CI and are reported, not explained away.
- **G-L5 (HARD), all six checks PASS:** identity 0.000e+00 (anchor and gradient); anchor draws
  vs `p3c.reference_boot` max|diff| **2.776e-17** over 500 draws; **this script's own cluster
  bootstrap vs the imported corrected routine 2.776e-17** on the same ids (two independent
  implementations of the cluster expansion); gradient draws vs a slow pandas-rank rebuild
  0.000e+00 over 500 draws; **Phase 1 CI reproduced to 0.000e+00 on both endpoints** at fixed
  10,000 draws, computed from `pdg`'s canonical `a222v_rows` (not from this script's H-frame
  vectors -- an earlier draft did the latter and would have failed by construction).

### Bug found and fixed before any score existed (disclosed)

`p3c.draw_ids` returns the tuple `(ids, labels)`, not the array; two smoke attempts crashed
with `TypeError: only integer scalar arrays can be converted to a scalar index` when the tuple
was indexed as an array (once in `analyse`, once in the G-L5 block). Both were the same
mistake, both were fixed before any number was reported. **Unlike A3/A4/A8b I did not keep the
two failed outputs as separate files -- they were overwritten by the successful smoke**, so
the tracebacks exist only in this entry (both are the three-line `cluster_boot_stat` failure
shown above in the session transcript). No gate, threshold or number changed.

### Records

- `PHASE4_A8D_ANALYSIS_FULL_OUTPUT.txt` (103 lines, sha256
  `3bafec0241baa9f580a68bfc2757492d83dfeac5c00f191edbd626c10270441e`), full run, 408.8 s.
- `PHASE4_A8D_ANALYSIS_SMOKE_OUTPUT.txt` (103 lines, sha256
  `703b9206ec088762866abe61023306ee5b646f589476a48c39c97fa24508a433`), `--mode smoke`
  (N_BOOT=300), 357.0 s, every number marked PROVISIONAL. The G-N5-style gates that do not
  depend on N_BOOT are identical in both; the model-column CIs are the production values in
  the full run only.

Verdict: **PASS.** Module L's analysis is built and gated, and the 650M column is computed
(MODEL-REPLICATES). The 150M/35M columns and both cross-model agreements will fill in at
night B, stage SB3. Next: A9 (driver, lock, tests, STATE_FOR_LAUNCH.md), stopping at
READY-TO-LAUNCH.

---

## [A9] - Orchestration: the Phase 4 driver, the stronger lock, three plans, 19 tests, STATE_FOR_LAUNCH.md - PASS (READY-TO-LAUNCH, nothing launched)

**Date:** 2026-10-04 (session 4a). **Status: PASS.** New files: `scripts/phase4_driver.py`
(sha256 `8696a31198f7aca095d89ecd23e41b1796d84e2f55b4bdafc47b57e2aefcfc59`),
`scripts/launch_phase4_overnight.sh` (`17952d380660ed4e05adc07919a80e587fae2f32d80da2e4d9afd045a4b3875b`),
`scripts/175_phase4_driver_tests.py` (`59f023d03b9ebb0c645bcf8c82d973062e6470406a0c550036d404018b16f494`),
`docs/tasks/phase4-strengthening/STATE_FOR_LAUNCH.md` (232 lines, sha256
`44954eecd9ca0648ec1257fb3ac622adbf6f8a187e3139a6dcbc63c42045d9f8`).
**Nothing was launched and no real scorer has run under the driver.**
`scripts/lib/phase3_guards.py` is IMPORTED AND USED **UNCHANGED** (sha256
`9daed884c57c4a1267e6e3ce3d59c48ecef36153abe5476e71fbcd7474899737`, verified by the integrity
pass); `scripts/phase3_driver.py` was read as the design template and NOT modified. Phase 3's
driver takes a JSON plan FILE rather than a named plan, so it is not plan-configurable in A9's
sense and a new driver file was written, as the spec allows.

### 1. The Phase 3 flake: what allowed a second start

Phase 3's lock was `mkdir {home}/.driver.lock` (atomic) **then** write `driver.pid` **inside**
it (`phase3_driver.py` 407-441). Those are two steps, and the window between them is the bug:

```
driver 1:  mkdir() succeeds  ->  .driver.lock exists, driver.pid does NOT
driver 2:  mkdir() raises FileExistsError
           -> int(pidf.read_text()) raises -> pid = None
           -> "pid is None" is treated as a STALE lock
           -> shutil.rmtree(lock) DELETES DRIVER 1'S LOCK
           -> retry -> mkdir() succeeds -> DRIVER 2 STARTS
```
=> two drivers, one home, no error raised anywhere. "driver.pid missing" is
indistinguishable from "a live driver created this lock a millisecond ago and has
not written its pid yet", so the stale-lock branch fires on a brand-new lock. The
window is sub-millisecond, which is exactly why `test_double_start_second_refuses`
failed once and the root cause was never found. Two secondary windows in the same
code: `_pid_alive()` is true for ANY live process with that PID (after PID reuse a
stale lock refuses forever, unexplainably), and `rmtree` in both the stale branch
and `release_lock` is unconditional, so a slow driver's exit can delete a live
peer's lock.

### 2. The replacement lock, and the 50-of-50 demonstrations

**Authoritative: `fcntl.flock(LOCK_EX | LOCK_NB)` on `data/processed/phase4/.driver.lockfile`.**
The kernel arbitrates: it either fails immediately (refuse, deterministically) or
succeeds (take it, atomically) -- there is no read-then-write step in between, and
the kernel releases a flock when the holder dies, so a **stale lock is impossible**.
Two layers sit on top, as the spec asks: a **PID liveness check** on the file's
contents (catches the pathological both-hold-it case), and the original **atomic
`mkdir` marker** as a second layer, which is removed on release and, if found while
the flock was free, is declared stale with a printed message and removed.

- **T1, sequential double-start: 50 of 50 refusals.** Driver A is proven running (its
  stub wrote a ready marker, so the lock is held), then B is launched 50 times; every
  launch exits **2** with `REFUSING TO START`. After A is terminated the lock reads
  free.
- **T2, the Phase 3 case specifically -- 50 SIMULTANEOUS starts of A and B on one
  home:** in **50 of 50 rounds exactly one ran and exactly one refused**; the winner
  reached its stage in 50/50 rounds; **rounds with neither refusing (two drivers on
  one home): 0**; unclassifiable: 0. The coin flip (A won 25, B won 25 in the final
  run) shows neither side has a systematic advantage -- the kernel, not a race,
  decides. This is a race sample, not a proof of impossibility, and is labelled as
  such in the test output.

### 3. Plans, budgets and the night split

Per-stage budget = 1.5 x the projection from the timing smokes, except SA1 which the
plan caps at 330 min. Projections (measured, not inherited): SA1 22,719 passes x 0.643
s x 1.25 = 304 min; SA2 15.4 min; SB1 44,533 x 0.2414 x 1.25 = 224 min; SB2 44,533 x
0.0762 x 1.25 = 71 min; SB3 ~10 min; SB4 ~145 min; SB5 15.4 min; integrity 1 min.

| night | stages | budgets | total |
|---|---|---|---|
| **A** | SA1 neighbour scoring H, SA2 neighbour analysis, SA3 integrity | 330 + 23 + 10 | **363 min** |
| **B** | SB1 ladder 150M, SB2 ladder 35M | 336 + 107 | **443 min** |
| **C** | SB3 ladder analysis, SB4 neighbour nonH, SB5 neighbour secondary analysis, SB6 integrity | 15 + 218 + 23 + 10 | **266 min** |

**The move, stated as the spec requires:** all six night-B budgets total 709 min,
over the 450-min ceiling. Dropping in reverse priority (SB6, SB5, SB4, SB3) leaves
SB1 + SB2 = 443 min, so **SB3, SB4, SB5 and SB6 move to a night C plan**. Nothing was
shrunk to avoid this: no roster, no coverage rule and no threshold was touched, and
SB1's budget stays 1.5 x 224 even though its projection is 224, because the multiplier
is fixed.

### 4. Coverage rule (Amendment 1 item 5) and the Amendment 3 statistic

SA2/SB5 run the neighbour analysis **iff the COMPLETE NB has >= 30 members**, a member
being complete at >= 95% of its eligible H positions (own position excluded), NB =
the 40 new C1/C2/C5 backgrounds plus the six existing nulls. Below 30 the step is
logged and skipped; the UNDERPOWERED rule inside the analysis is unchanged.
**Flag (AGENTS 9):** this **supersedes the planning doc's ">= 24 of the C1 + C2
backgrounds"** (doc lines 217-218). The planning doc is protected and was NOT edited.
The driver runs script 172, which implements Amendment 3's flexible-control partial
and prints the planted confusion matrix beside section 6's word.

### 5. Everything else, as in Phase 3

Guards before every stage via the unchanged `phase3_guards.evaluate_guards` (AC +
charge >= 30%, swap < 3.0 GB, free memory >= 25% with the spec's 10/30-minute wait
windows, disk >= 5 GiB with no window); the launcher refuses below **35%** free memory
and when a lock is held; up to 3 attempts on a nonzero exit other than 3; **exit 3
never retried**; gate steps never retried; timeouts not retried (TERM to the child
process group, grace, SIGKILL); atomic state + heartbeat + per-plan logs and state
files (`driver_state_phase4{A,B,C}.json`); TERM/INT forwarding with exit 143 and lock
release; `--dry-run` that creates nothing; resume that skips completed steps; one
shared lock across all three plans.

### 6. Tests: 19 of 19 PASS (`PHASE4_A9_DRIVER_TESTS_OUTPUT.txt`, sha256 `ca111194792653fd583a8d6cb1f7fbee92cfaa7cec7d0f36231123d6cde7d61a`)

All in an isolated temp directory with stub stages; no real output, checkpoint or
scorer touched. T1 double-start 50/50 + lock free after TERM; T2 simultaneous 50/50
with zero double-runs; T3 stale marker + dead PID cleared with a printed message;
T4a-d SIGTERM -> exit 143, state `terminated`, lock free, TERM forwarded to the child
group (a child that IGNORES TERM was used, so the SIGKILL path is the one exercised);
T5 timeout kills the stage and the driver continues; T6a exit 1 retried to exactly 3
attempts, T6b exit 3 attempted exactly once (stage `gate_failed`); T7 all five guards
fail-and-skip with `PHASE3_FAKE_*` readings and all-good readings run the stage; T8
`--dry-run` for A, B and C prints the plan and creates nothing; T9 resume skips the
completed stage; T10 the coverage rule both ways (6 complete -> skipped;
6 + 24 = 30 -> runs).

**Two bugs in my own test script, found and fixed before the final run (disclosed):**
T2 read `returncode` before `communicate()` (so it could be `None`) and then sorted
`None` against `int`; and its win-counting logic classified every round wrongly while
still reporting PASS, which would have been a meaningless number. Both were fixed and
T2 re-run with an honest metric (50/50, A 25 / B 25). I would rather report a fixed
test than a passing one that measures nothing.

### 7. STATE_FOR_LAUNCH.md

232 lines: every staged file as one `path sha256 <hash>` line (7 night scripts, 7
session scripts, the reused guards library, the 5 frozen pre-registrations, the 3
amendments, the frozen roster); expected durations against budgets; the night-split
arithmetic; exact launch / monitor / stop / resume commands per plan; a ready-to-paste
`git add` naming every new file by explicit path; and the limitations. **The integrity
pass was run against it and verified all 24 listed files: 24 MATCH, RESULT PASS.**

### 8. Deviations and open items

- **Three nights, not two** (the plan's own overflow rule) -- stated in
  STATE_FOR_LAUNCH.md section 3.
- **The coverage rule is Amendment 1's, not the doc's** -- flagged above; the doc is
  protected and unedited.
- **`--plan-file` was added to the driver** (the same hook Phase 3 used for its tests) so
  the suite can inject stub stages; the built-in plans are unaffected.
- **The integrity pass's `STATE_FOR_LAUNCH.md` parser** accepts any line carrying a
  64-hex digest and a path token; the format is now fixed by A9 ("path sha256 <hash>"),
  and it was verified to parse all 24 lines.
- **`scripts/lib/phase3_guards.py`'s own `CONFLICT_PATTERN` is Phase 3's**; the Phase 4
  pattern (`phase4_driver|171_neigh_score|173_ladder_score`) is passed as an argument,
  which the unchanged function accepts -- no library edit.
- **Nothing has been run end-to-end under the driver.** The scorers' gates were each
  verified individually in A7c/A8b, and the driver is verified with stubs.

---

## [S-A SUMMARY] - session 4a, end of Part A (READY-TO-LAUNCH)

**Read first: this file's A7e attempt-3 entry, `PHASE4A_BUILD_LOG.md` line 1002** -- it is
where the neighbour arm's section 6 statistic changed (Amendment 3's flexible-control
partial) and where G-N4's five planted criteria are recorded with their rates.

**Module status**

| module | status | note |
|---|---|---|
| S (sign convention) | **DONE** | `SIGN_CONVENTION.md`, 32 lines, every number independently re-derived |
| M (mechanism) | **DONE** | script 167, 65/65 checks |
| U (utility) | **DONE** | script 168; U-1 has a word, U-2 UNVERIFIED-LABELS by its pre-registered fallback |
| G (GB1 locality) | **DONE** | script 169, 31/31; G-3 SKIPPED per G-DEC8 (1PGA numbering unverified) |
| N (neighbour arm) | **STAGED, SCORES PENDING NIGHT A** | roster frozen; scorer, timing and analysis all gated (G-N2 PASS at 1.776e-15; G-N4/G-N5 PASS under Amendment 3) |
| L (model ladder) | **STAGED, SCORES PENDING NIGHT B** | both authorised checkpoints downloaded and verified; 650M column computed (MODEL-REPLICATES); 150M/35M columns PENDING |

**Frozen words produced so far (numbers as logged)**

- M-1 **PARTIAL-SURVIVES** (partial -0.064148044, CI [-0.093576, -0.035309]; p_spec 2/79 full, 3/79 H)
- M-3 **EXCESS-OVER-ARTIFACT** (observed -0.088118 below the null's 2.5th percentile +0.012014; the null centres POSITIVE at +0.027069)
- M-5 **WITHIN-CARRIED** (within CI [-0.049826, -0.006662], p 2/79; between CI [-0.235913, -0.119746], p 4/79)
- M-6 **MODERATE** both views (P = 0.5760 full, 0.7720 H)
- U-1 **CONDITIONING-HURTS** (Delta -0.003398, CI [-0.004488, -0.002335])
- U-2 **UNVERIFIED-LABELS, no word** (G-U2 failed; Delta AUROC -0.006189, CI [-0.021463, +0.004330])
- G-1 **MODEL-DECAYS FIRES** (-0.271234, CI [-0.284303, -0.257822]); **DATA-DECAYS does not fire** (+0.036680); **LOCALITY-DIFFERS FIRES** (-0.307914, CI [-0.323182, -0.292525])
- G-2 **SEPARATION-MATTERS** (paired near-far -0.022239, CI [-0.043105, -0.001032], 399 backgrounds)
- G-3 **SKIPPED** (1PGA chain A residue 2 = T vs assayed Q; no numbering guessed)
- L (650M column only) **MODEL-REPLICATES** (rho_A222V -0.090021683, CI [-0.122385, -0.056046]; p_spec_H(neg) 0.050633 = 3/78); gradient +0.713319 CI [+0.566655, +0.808932]; shift confound -0.612697 CI [-0.732776, -0.456234]
- **No word yet for N** -- every N word needs night's SA1/SA2.

**Gates, with their values**

- A2: A2-G1 40/40, A2-G2 all anchors exact (Phase 1 CI 0.000e+00 / 7.6e-17), A2-G3 50 toys PASS; Phase 1 CI reproduced
- A7: G-N0 loader 4.97e-07; G-N1 roster `675a24f1…85d6` (50 backgrounds, |NB| = 46); **G-N2 (a) 1.776e-15, (b) 0.000e+00, (c) 0.0; G-N3 PENDING (no scores); G-N4 all five PASS (0.970 / 0.990 correct; 0.030 / 0.010 wrong-arm; 0.930 NEITHER); G-N5 identity 0.000e+00, references 1.86e-15 and 5.83e-16, Phase 1 CI 0.000e+00**
- A8: **G-L1 parameter counts exact (651,043,254 / 148,140,154 / 33,501,394); G-L2 AV_220 1.776e-15 score and delta, plus the ADDED G-L2(b) WT arm 1.776e-15; G-L3(a) 0.000e+00, (b) 0.0, (c) PENDING; G-L4 all five planted arms PASS (A1 MODEL-REPLICATES, A2 -0.9997, A3 -0.9991, A4 fire 0.020, A5 1.0 / +0.0004); G-L5 identity 0.000e+00, references 2.776e-17 and 0.000e+00, Phase 1 CI 0.000e+00**
- A9: 19/19 driver tests PASS, including **double-start 50/50** and **simultaneous 50/50 with zero double-runs**; integrity pass 24/24 sha256 MATCH.

**Projected nights:** A 363 min, B 443 min, C 266 min (all <= 450).

**Deviations, in one place:** three nights instead of two (the plan's overflow rule);
Amendment 1's coverage rule instead of the doc's; Amendment 3's flexible statistic;
three pre-first-run bugs fixed in script 173 and two in script 174 (all disclosed in
their entries); one unintended re-download of two already-authorised files in A8a
(deleted, cache copies verified unchanged); no stage has ever run under the driver.

**Status: READY-TO-LAUNCH. Nothing has been launched.** Next session: after the
nights, `PHASE4B_MORNING_LOG.md` (Part C).
