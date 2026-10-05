# STATE_FOR_LAUNCH.md — Phase 4 nights (session 4a wrote this; NOTHING HAS BEEN LAUNCHED)

**Written:** 2026-10-04, session 4a, Task A9. **Status: READY-TO-LAUNCH. Not launched.**
Every number here comes from a timing smoke or a measured gate recorded in
`PHASE4A_BUILD_LOG.md`; nothing is estimated from another script.

**Read this file before every night.** Arnav launches by hand; the driver runs
detached under a lock; this session is closed during the nights.

---

## 1. Staged files, one `path sha256 <hash>` per line

The integrity pass (SA3 / SB6) verifies every line below against the file on
disk and exits 3 on any mismatch, so **if a line does not match, do not launch.**

### Scripts the nights run

```
scripts/170_neigh_roster.py sha256 a9516951e05b9a2cc5a2ba804c2db81b43b0c56bf2afd12473ac00f058e2e597
scripts/171_neigh_score.py sha256 e904951d327030cbc843c3eefdd818ef6a5c4e7d46448c8031fe03051c4cf2a7
scripts/172_neigh_analysis.py sha256 0534a301ee3377c78bf2b4d7f63ee0d621a535b8174ca78d1e99a1bd179079f4
scripts/173_ladder_score.py sha256 12f2f140fc212ab3b0e23a1bc74e8f8bc51155e7e82951d7faa5cb1f0f6eabb8
scripts/174_ladder_analysis.py sha256 b638d3c6e8abbaed894858593af8ffdb51395e1e3d7f42a9db39adbfa4b5f3b6
scripts/phase4_driver.py sha256 8696a31198f7aca095d89ecd23e41b1796d84e2f55b4bdafc47b57e2aefcfc59
scripts/launch_phase4_overnight.sh sha256 17952d380660ed4e05adc07919a80e587fae2f32d80da2e4d9afd045a4b3875b
```

### Session-4a scripts already run (kept for the record; not re-run by the nights)

```
scripts/lib/phase4_common.py sha256 8cb58d9d65825e24beb11ab72fc6f5d20883291709dba189ccf3c4c6225d5527
scripts/165_phase4_common_gate.py sha256 ab0ac6cedf61e3d05eca83142d8e88a92a32c06102abc73e7038c32884fbcdfa
scripts/166_sign_convention.py sha256 88ddd211ec85de3160009fdd71c0828d887b85cde477d450082290b481f4d984
scripts/167_mech_anchor.py sha256 122d95ff58a5c1e5bfe7e91e4a59349c5c6d2ab6cb720b77a20ef77c2a410c13
scripts/168_utility.py sha256 3e8819ba25bafae1215fbb6e3fbdc056584f49da48605f48b438c6516c669173
scripts/169_gb1_locality.py sha256 af2f6fd87592af59043da2a744bb81edb8f19e0189c7269625bc7d193b3d8f63
scripts/175_phase4_driver_tests.py sha256 59f023d03b9ebb0c645bcf8c82d973062e6470406a0c550036d404018b16f494
```

### Libraries (reused unchanged; the integrity pass checks them too)

```
scripts/lib/phase3_guards.py sha256 9daed884c57c4a1267e6e3ce3d59c48ecef36153abe5476e71fbcd7474899737
```

### Frozen pre-registrations and Arnav's three amendments (must never change)

```
docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md sha256 8d27467542f4620572cf382b6f01d693d8734b7345bddd039fdbb083be1cf39b
docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md sha256 744e68ce3b565b1b2060d662f322d7d3f53923d9bb6ff45de5156f3f445f9531
docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md sha256 10c547c9e0c158cca6a9f158deefc31fe5b728539aba2909b897d199c85795a8
docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md sha256 167847a97aca32b9ed7f71e28ca2840e1c53dea43c2941ae8b70c8805448359e
docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md sha256 f56134f7642321693e70e9d63875d157eca40a1f210dea828cd61630524df58a
docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md sha256 b636a4d193efa16ed36e7d7feeb5a357c99cd5f202437bf100a55b80f822b55a
docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_3.md sha256 266feb5549ec50d4fd21c0447de2ba83c8a33e72d50be547a5e1f1cf72cc5a42
docs/tasks/phase4-strengthening/prereg/MODEL_LADDER_PREREG_v1.md sha256 eafe37a85c902c2b48dcb6e561f1569f727850fb26cfaeb6fec25c2e18cd9db3
```

### Frozen roster the night scores against (hash-gated by script 171 before the model loads)

```
data/processed/phase4/neigh/roster_v1.csv sha256 675a24f1963878568e65b6d630e25e9ce649627c3f02ab0d5e65ec438f2d85d6
```

---

## 2. Expected durations against the budgets

Projections come from the timing smokes (median s/pass measured on 3
backgrounds, plus the wild-type arm), multiplied by the exact pass counts and by
the plan's 1.25 factor. Per-stage budget = 1.5 x projection, except SA1 which the
plan caps at 330 minutes.

| stage | what runs | projection (measured) | budget (cap) |
|---|---|---|---|
| SA1 | script 171, 50 backgrounds on H, 650M | 22,719 passes x 0.643 s x 1.25 = **304 min** | **330 min** (1.5x would be 456, capped) |
| SA2 | script 172 neighbour analysis (Amendment 3) | 15.4 min (923.6 s measured) | **23 min** |
| SA3 | integrity pass | ~1 min | **10 min** |
| SB1 | script 173, 97 backgrounds + WT arm, 150M | 44,533 passes x 0.2414 s x 1.25 = **224 min** | **336 min** |
| SB2 | script 173, same, 35M | 44,533 passes x 0.0762 s x 1.25 = **71 min** | **107 min** |
| SB3 | script 174 ladder analysis (2 new columns + cross-model) | ~10 min | **15 min** |
| SB4 | script 171, 50 backgrounds on nonH, 650M | ~9,930 + 908 gate passes x 0.643 s x 1.25 = **145 min** | **218 min** |
| SB5 | script 172 again (full-frame secondary) | 15.4 min | **23 min** |
| SB6 | integrity pass | ~1 min | **10 min** |

Gate overhead is disclosed and NOT inside the projection formulas the plan fixes:
script 171 re-runs G-N2 (908 passes, ~9 min at 650M) on every invocation that
has something to score, and script 173's G-L3(a) costs 910 passes (~3.7 min at
150M). Both sit inside the 1.25/1.5 slack.

---

## 3. THE NIGHT SPLIT (three nights, not two) — and why

The six night-B stages' budgets total **709 minutes**, above the 450-minute
per-night ceiling. Dropping stages in **reverse priority** (SB6, SB5, SB4, SB3)
leaves SB1 + SB2 = **443 min**, which fits. **SB3, SB4, SB5 and SB6 therefore
move to night C** (15 + 218 + 23 + 10 = **266 min**, which fits).

- **Night A** — SA1, SA2, SA3 = 363 min
- **Night B** — SB1, SB2 = 443 min
- **Night C** — SB3, SB4, SB5, SB6 = 266 min

This is the plan's own overflow rule, applied in the stated order. It was **not**
avoided by shrinking a roster, a coverage rule or a threshold: SB1's budget is
1.5 x 224 even though the projection is 224, because the multiplier is fixed.

---

## 4. Launch / monitor / stop / resume

Before **each** night: plugged in and **charging**, lid open, Low Power Mode off,
everything heavy quit — and **if swap was above 2 GB at any point since the last
reboot, restart the Mac first** (swap is not released by closing apps). The
launcher refuses below 35% free memory, without AC power, with swap >= 3 GB, with
free memory below the floor, with disk under 5 GiB, or when a driver lock is held.

```bash
cd /Users/arnavchavan/Desktop/mthfr-context-dependence

# dry run first (prints the whole plan, creates nothing, runs nothing):
bash scripts/launch_phase4_overnight.sh --plan A --dry-run

# night A (or B, or C) -- LAUNCH ONCE:
bash scripts/launch_phase4_overnight.sh --plan A

# monitor (light check; do NOT tail -f, do not reopen OpenCode):
tail -n 5 data/processed/phase4/driver_phase4A.log
cat data/processed/phase4/driver_state_phase4A.json

# stop (if you must):
kill <PID printed by the launcher>          # or: pkill -f phase4_driver

# resume (same command; completed steps are skipped, nothing is rescored):
bash scripts/launch_phase4_overnight.sh --plan A
```

Per-night files (all under `data/processed/phase4/`):

| file | plan A | plan B | plan C |
|---|---|---|---|
| state | `driver_state_phase4A.json` | `driver_state_phase4B.json` | `driver_state_phase4C.json` |
| log | `driver_phase4A.log` | `driver_phase4B.log` | `driver_phase4C.log` |
| stage output | `driver_phase4A_stage_SA*.log` | `driver_phase4B_stage_SB*.log` | `driver_phase4C_stage_SB*.log` |
| nohup | `driver_phase4A_nohup.log` | ... | ... |

One lock serves all three plans (`data/processed/phase4/.driver.lockfile`, an
`fcntl.flock`), so two plans can never run at once.

---

## 5. What each stage does, and what a failure means

| stage | script | if it fails |
|---|---|---|
| SA1 | 171 `--frame H` | exit 3 = a gate failed (G-N2/G-N3): logged, **never retried**, driver continues to SA2, which will then log the coverage skip |
| SA2 | 172 `--mode full` | runs only if the COMPLETE NB has >= 30 members (Amendment 1 item 5); otherwise logged and skipped |
| SA3 | driver `--integrity` | exit 3 = a staged script's sha256 or a ladder file count is wrong: **stop and tell OpenCode** |
| SB1 / SB2 | 173 `--model 150M` / `35M` | per-background atomic writes; a relaunch resumes where it stopped |
| SB3 | 174 `--mode full` | prints the 150M/35M words and both cross-model agreements |
| SB4 | 171 `--frame nonH` | completes the 654-position frame into `neigh_nonH/` |
| SB5 | 172 `--mode full` | the full-frame secondary (no word by design) |
| SB6 | driver `--integrity` | as SA3 |

**A driver exit code of 0 does NOT mean every stage succeeded.** Always read the
state file: `"status": "finished"` plus each stage's `status`.

---

## 6. Ready-to-paste `git add` (every new file, explicit paths)

Nothing has been staged or committed by this session. When you are ready:

```bash
git add \
  scripts/lib/phase4_common.py \
  scripts/165_phase4_common_gate.py \
  scripts/166_sign_convention.py \
  scripts/167_mech_anchor.py \
  scripts/168_utility.py \
  scripts/169_gb1_locality.py \
  scripts/170_neigh_roster.py \
  scripts/171_neigh_score.py \
  scripts/172_neigh_analysis.py \
  scripts/173_ladder_score.py \
  scripts/174_ladder_analysis.py \
  scripts/175_phase4_driver_tests.py \
  scripts/phase4_driver.py \
  scripts/launch_phase4_overnight.sh \
  docs/tasks/phase4-strengthening/prereg/MECH_ANCHOR_PREREG_v1.md \
  docs/tasks/phase4-strengthening/prereg/UTILITY_PREREG_v1.md \
  docs/tasks/phase4-strengthening/prereg/GB1_LOCALITY_PREREG_v1.md \
  docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1.md \
  docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_1.md \
  docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_2.md \
  docs/tasks/phase4-strengthening/prereg/NEIGHBOUR_ARM_PREREG_v1_AMENDMENT_3.md \
  docs/tasks/phase4-strengthening/prereg/MODEL_LADDER_PREREG_v1.md \
  docs/tasks/phase4-strengthening/SIGN_CONVENTION.md \
  docs/tasks/phase4-strengthening/STATE_FOR_LAUNCH.md
```

`data/processed/` stays out of git (it is gitignored by design and is
regenerable). `PROVENANCE.md`, `STATE.md` and the `PHASE4_A*.txt` /
`PHASE4_*_OUTPUT.txt` records can be added at your discretion; they are not in
the list above because they are session records rather than staged code. The
planning doc `PHASE4_STRENGTHENING.md` is deliberately **not** listed: it was
committed before the pre-registrations were extracted (gate A0-G1) and has not
been modified since.

---

## 7. Known limitations and deviations (read before trusting a night)

1. **A fifth file the integrity pass does not check:** `scripts/lib/phase3_guards.py`
   is listed and checked, but it is a PRE-EXISTING Phase 3 file, reused
   unchanged; if it is ever edited, the nights' guard behaviour changes.
2. **The coverage rule is Amendment 1's, not the planning doc's.** The doc says
   ">= 24 of the C1 + C2 backgrounds"; Amendment 1 item 5 replaces it with
   "the COMPLETE NB has >= 30 members". The planning doc is protected and was
   NOT edited; the conflict is flagged in `PHASE4A_BUILD_LOG.md`. The driver
   implements Amendment 1.
3. **Section 6 of the neighbour arm now uses Amendment 3's flexible-control
   partial**, and its word is printed beside the planted confusion matrix.
4. **The 650M ladder column is not out-of-sample** (Phase 2 rows, already
   analysed); only 150M and 35M are new data.
5. **Budgets are caps, not predictions.** A stage killed at its budget has done
   part of its work; every scorer is per-background atomic and resumable.
6. **The lock refuses a second driver; it cannot protect against someone editing
   an output file by hand while a night runs.**
7. **Nothing here has been run end-to-end against real scoring.** The driver's
   19 checks used stub stages in an isolated temp directory. The scorers'
   gates were each verified on their own (A7c/A7d/A8b), but no night has run.