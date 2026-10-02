# STATE FOR LAUNCH -- Phase 3 overnight pipeline

**Status: READY-TO-LAUNCH. DO NOT LAUNCH FROM THIS DOCUMENT.** It records
the frozen state at the end of session 3a (build). The launch itself is
Arnav's manual step in PART B of `PHASE3_OVERNIGHT.md`; session 3a never
launched, never scored, and never committed anything to git.

Written: 2026-10-01 (session 3a, tasks A0-A7). Read first:
`docs/tasks/phase3-overnight/PHASE3A_BUILD_LOG.md` entry `## [A7]` at
**line 1622** (build record), then `## [A6]` at line 1327 (A6 product) and
`## [A5g-6h]` at line 1560 (the 157 section-6h code fix). Deviations for the
orchestration: `PHASE3_A7_TEST_OUTPUT.txt` D01-D20.

---

## 1. Integrity baseline -- staged scripts and sha256

S5 (the driver's `--integrity` step) and session 3b's C0 verify every line
below against the file on disk. **Any mismatch is a prominent FLAG (exit 3).**
One path + one sha per line (the S5 parser's disclosed format).

**Run tonight by the stages:**

- scripts/153_m1_ge_target.py sha256 e9fd90aff973be1c03dcfa15c80298f5cd54df4dbf5775a41de1839adf0b5133
- scripts/154_gb1_score_backgrounds.py sha256 d861660bc2e53e22853b127d9a0139aa644fc27de91c2ee67a8b9bd3eb6df7c6
- scripts/155_gb1_regime_analysis.py sha256 0b3874d23031f37b5ebab9c6cfa2d983a308ee7f03b20a072d925b156db83eae
- scripts/156_rbd_score_backgrounds.py sha256 e9dec44aebd7e96f646c092c1ad7463b72360728373150a2979793611769a837
- scripts/157_rbd_regime_analysis.py sha256 7ec495111116a43742f038ffc075fadd4f193b5ca0e203169f9e904af8106ce3
- scripts/158_multidms_rbd.py sha256 c7044836f080937504c1b822b4c009dce8ca8631bbde0428f787040dbf0fae15

**Orchestration (A7; 157's sha above is post-6h-fix, disclosed in the log):**

- scripts/phase3_driver.py sha256 07b7f1898e81141a8c55b37f795c89da8860a84f1f50ab0528971ab075d4a8cd
- scripts/lib/phase3_guards.py sha256 9daed884c57c4a1267e6e3ce3d59c48ecef36153abe5476e71fbcd7474899737
- scripts/test_phase3_driver.py sha256 346d1f640fb4343070af6d58ad96d510d6ba8fd8190702e3e38742b5f9c739b0

**Build-stage gates (frozen; not re-run tonight, verified by C0):**

- scripts/159_phase3_common_gate.py sha256 c0888438576f6ea2196b6565bdee9b3bc61aa0d5fc9b0b01aa02ba232cfffa48
- scripts/160_gb1_phase3_inputs_roster.py sha256 2bdc68dfcde259e7361a736f5be911f489098800fd0fe8018583c80ffb94d84e
- scripts/161_gb1_gate_g1prime.py sha256 12ae46007496e17c290375fcc1328aaeca0aac4aeabfb6821c5c65ad7677a485
- scripts/162_rbd_inputs_gate.py sha256 76abc21b0453122e3f1bede2c76c4f34f5369246e4ead7ee9061d507f8f167ff
- scripts/163_rbd_targets.py sha256 353bfe6e8d5793a1c03ad4ee6fcbda1f6c7b303940ec063db10aadebd629a81e
- scripts/164_rbd_roster.py sha256 fa45236751deff16dfd900e77e1538d58ae3ae9fe62ddca77c72a558133e0351

**Launcher (not a .py token; hashed manually):**

- scripts/launch_phase3_overnight.sh sha256 6c988597f08e7733d9d5ea81d6fa1ecd7f16383ba06a30d69e9ae122912bbfb9

Frozen prereg hashes (verify in C0, unchanged by 3a):
`prereg/GB1_REGIME_PREREG_v1.md`, `prereg/RBD_REPLICATION_PREREG_v1.md`
(sha256 `8965450a...c2671a7` as recorded in the A5d entry),
`PHASE2_PREREG.md`.

---

## 2. Stage plan (driver `--dry-run` output, verified RC=0)

Plan `phase3-overnight-production`: **5 stages, budgets total 450 min,
global cap 450 min (7.5 h)**. Guards before every stage: AC power + battery
>= 30% (wait <= 600 s, poll 60 s); swap < 3.0 GB and free memory >= 25%
(wait <= 1800 s in 300 s steps); disk free >= 5 GiB (no wait). Missing
tool -> UNGUARDED (logged). `--force` overrides (logged).

| Stage | Budget | Precheck (A-gates) | Steps |
|---|---|---|---|
| S1 GB1 scoring | 100 min | gb1/sequences.csv, gb1/roster_v2.csv | `venv/bin/python3 scripts/154_gb1_score_backgrounds.py --sequence assayed --out-dir data/processed/phase3/gb1` then `... --sequence project --out-dir data/processed/phase3/gb1_project --limit-roster 20` (the two-sequence subset = first 20 of the draw, doc line 177) |
| S2 RBD scoring | 150 min | rbd/e_T.csv, rbd/roster_v1.csv | GATE step (never retried): `venv/bin/python3 scripts/156_rbd_score_backgrounds.py --g-r5`; then `... scripts/156_rbd_score_backgrounds.py --out-dir data/processed/phase3/rbd` |
| S3 analyses | 75 min | coverage rule per module (runs only if met, else logged + skipped) | `venv/bin/python3 scripts/155_gb1_regime_analysis.py --mode full`; `venv/bin/python3 scripts/157_rbd_regime_analysis.py --mode full` |
| S4 multidms | 120 min | venv_multidms/bin/python exists | `venv_multidms/bin/python scripts/158_multidms_rbd.py --mode full` |
| S5 integrity | 5 min | none | driver self-run `--integrity`: file counts, manifests, sha256 vs this document, final driver_state.json |

Coverage floors (quoted from the scripts, not invented): GB1 every
`roster_v2` background present with >= 95% of its 54 eligible positions
(155 G-4) + wt_arm.csv; RBD every `roster_v1` background >= 95% of 201
construct sites (156 G-R4) + wt_arm.csv.

Retry/timeout policy (dry-run verbatim): `up to 3 attempts per step, 30 s
apart, on nonzero exit != 3; exit 3 = gate failure, NEVER retried; gate
steps never retried; timeouts not retried (TERM, then SIGKILL of the child
process group after 5 s grace)`. A stage that times out, is skipped or hits
a gate failure is logged and the driver **continues** to the next stage.

---

## 3. Expected duration per stage (each from its timing record)

| Stage | Budget | Projection (record) |
|---|---|---|
| S1 | 100 min | **1,407.575 s = 23.46 min** (21,655 passes x 0.0520 s/pass x 1.25) -- `PHASE3_A4e_TIMING_SMOKE_OUTPUT.txt`, re-derived in log [A4e]. Two-sequence subset step: **derived arithmetic, not separately timed**: (20 x 54 + 55) passes x 0.0520 x 1.25 ~ 74 s ~ 1.2 min |
| S2 | 150 min | **4,102.7 s = 68.38 min = 45.6% of budget** -- `PHASE3_A5f_TIMING_SMOKE_OUTPUT.txt` |
| S3 | 75 min | **Unmeasured at full scale (honest unknown):** scoring has never run on full inputs, so 155/157 full modes have no measured runtime. Smoke timings at the frozen full N_BOOT/N_PERM defaults: 155 = 84.9 s (`PHASE3_A4f_FULLN_REHEARSAL_OUTPUT.txt`), 157 = 102.0 s (`PHASE3_A5G_SMOKE_OUTPUT.txt`). Per-background scaling not extrapolated; the 75-min timeout (TERM, no retry, stage logged, driver continues) is the safety |
| S4 | 120 min | **79 s observed full run** (`PHASE3_A6D_FULL_OUTPUT.txt`); smoke projections 0.5-7.5 min -- vast headroom |
| S5 | 5 min | integrity pass ran in 0.2 s in tests (`PHASE3_A7_TEST_OUTPUT.txt`) |

Measured projection total ~94 min + S3 unknown; hard cap 7.5 h.

---

## 4. Commands

- **Dry-run (prints plan, runs nothing):**
  `bash scripts/launch_phase3_overnight.sh --dry-run`
- **Launch (once):**
  `bash scripts/launch_phase3_overnight.sh`
  Prints the PID, the monitor command and the stop command.
- **Monitor:** `tail -n 5 data/processed/phase3/driver.log`
  (**Do not `tail -f`.**) Also: `data/processed/phase3/driver_state.json`
  (stage, start, last update, per-stage status), per-stage child logs
  `data/processed/phase3/driver_stage_<ID>.log`, launcher mirror
  `data/processed/phase3/driver_nohup.log`.
- **Stop:** `kill $(cat data/processed/phase3/.driver.lock/driver.pid)`
  (forwards TERM to the child process group, removes the lock -- tested).
- **Resume (after an interruption):** re-run
  `bash scripts/launch_phase3_overnight.sh`; completed steps/stages are
  skipped from driver_state.json (tested), and 154/156 skip completed
  background files on rerun.

---

## 5. Exit-code and failure semantics

- Child **exit 3 = gate failure**: never retried; the module's results are
  reported as **failed, not interpreted** (session 3b rule).
- Child nonzero **!= 3 = crash**: up to 2 retries, 30 s apart.
- **Timeout**: TERM, then SIGKILL after 5 s grace; no retry; stage logged,
  driver continues.
- **Driver exit 0 = run finished, not "all stages succeeded"** -- always
  read driver_state.json for per-stage status (completed / failed /
  gate_failed / timeout / skipped_guard / skipped_dependency / ...).
- **S5 sha mismatch vs this document** -> prominent FLAG, exit 3, no retry.
  Absent this document -> logged skip. Session 3b C0 re-verifies anyway.

---

## 6. State on disk at launch (verified 2026-10-01)

- `data/processed/phase3/gb1/`: **inputs only** -- `sequences.csv`,
  `roster_v2.csv` (+ a smoke product). No `bg_*.csv`, no `wt_arm.csv` yet:
  S1 creates them, and S3's coverage rule will not pass until it does.
- `data/processed/phase3/gb1_project/`: does not exist yet (S1 step 2).
- `data/processed/phase3/rbd/`: **inputs only** -- `e_T.csv`,
  `roster_v1.csv`. S2 creates `bg_*.csv`, `wt_arm.csv`, `manifest.csv`.
- `data/processed/phase3/multidms/`: **`e_T_MD.csv` and
  `multidms_report.json` ALREADY EXIST** from A6d (the frozen s6h held-out
  criterion was met: r = 0.8324/0.8550/0.8289 bind, 0.8913/0.8795/0.8584
  expr). Stage order is S3 before S4, so tonight's `157 --mode full` reads
  this existing file in section 6h; S4 then re-runs 158 deterministically
  (SEED 0 / SEED_SUB 1 / random_state 0) and rewrites the same product.
- Rehearsal dirs are **not touched by any stage**: `gb1_smoke/`,
  `gb1_scratch/`, `rbd_smoke/`, `rbd_smoke_6hfix/`.
- `driver_state.json`, `driver.log`, `.driver.lock/`: do not exist yet --
  a fresh start (the launcher reports `resume info` for stale locks).
- `m1_*.csv`: M1 complete (outcome GE-SURVIVES); nothing re-runs it.

---

## 7. What Arnav must know (PART B of the planning doc, lines 248-250)

Before launching: plugged in and **charging**, lid open (or the machine set
not to sleep on power), Low Power Mode off, everything heavy quit (OpenCode
window, browsers, Spotify, Claude, ChatGPT). The launcher enforces the
memory floor (refuses below 35% free memory and prints what to quit). It
also refuses a live lock or a conflicting `phase3_driver` process. After
launching: **do not `tail -f`, do not open OpenCode, do not run anything
else heavy.** If interrupted, re-run the launcher to resume.

Operational notes:

- Battery: per-stage guard needs AC power + battery >= 30% (waits up to
  10 min, then skips that stage and logs it). Swap/memory guard waits up to
  30 min in 5-min steps, then skips + logs. Disk needs >= 5 GiB free.
- Scoring (S1/S2) loads ESM-2 650M locally exactly as in phase 2 and the
  A4e/A5e timing smokes; **no network is needed tonight** (A5 acquisition
  is complete: 10 files, 70,406,131 bytes).
- 158 runs only under `venv_multidms` (pandas 2.3.3 pin; never `venv/`);
  everything else under `venv/bin/python3`.
- Do not start a second driver by hand while one runs (the lock refuses);
  do not run heavy jobs alongside the night (guards will skip stages rather
  than run unguarded -- the skip is logged).
- The 7.5-h cap and per-stage budgets mean a slow stage is cut and logged,
  not stretched; resume re-runs it.
- Outcome words for the morning (3b, not tonight): M1 only
  GE-SURVIVES/GE-WEAKENS/GE-DOES-NOT-SURVIVE; GB1 only ASSOCIATED/NOT
  RESOLVED (+ CENTERED/OFF-CENTER per the frozen block); RBD only
  RBD-REPRODUCES/RBD-INCONCLUSIVE/RBD-DOES-NOT-REPRODUCE (+ UNDERPOWERED).
  No cross-module confirmation claims. `e_T_MD.csv` is secondary only --
  reported next to the primary, never replacing it.

---

## 8. Pointers

- Build record: `PHASE3A_BUILD_LOG.md` (24 entries; start at `[A7]`,
  line 1622). Session checkpoint: `STATE.md`.
- Orchestration deviations: `PHASE3_A7_TEST_OUTPUT.txt` (D01-D20).
- A6 product record: `PHASE3_A6D_FULL_OUTPUT.txt`; env freeze:
  `PHASE3_A6B_FREEZE.txt`.
- Session 3b morning template: `PHASE3B_MORNING_LOG.md` (C0 starts by
  verifying this document's sha table).
