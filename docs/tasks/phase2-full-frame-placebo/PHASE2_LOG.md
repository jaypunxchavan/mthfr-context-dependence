# PHASE 2 — full-frame placebo test: session log (2a build/test/stage, then 2b analysis)

**Binding text:** `PHASE2_PREREG.md` (frozen, sha256 `420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`).
`PHASE2_EXECUTION.md` only implements it; where they conflict the pre-registration wins and the
conflict is logged. Both sessions append to this log; **never edit an earlier entry.**
Started: 2026-09-28 (session 2a — build, test, stage; **no overnight run launched here**).

Entry format (same as every prior session):

```
## [TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---
```

Entries append below this template, in task order: S0, R1, R2, G1, G2, G3, G4, then
`## SUMMARY (2a)`.

---

## [S0] — Integrity gates: prereg hash, commit timestamp, torch/MPS, disk
Status: PASS
Time started / finished: 2026-09-28 01:07:45 – 01:08:10
What I did:
Read `AGENTS.md`, then `PHASE2_EXECUTION.md` and `PHASE2_PREREG.md` in full (binding text read
before anything ran). Created this log first. Then ran the four S0 gates verbatim, no model:
`shasum -a 256` of the prereg (G-0a); `git log -1 --format='%H %cI' --` the prereg plus
`git status --short --` it (G-0b); the mandated torch/esm import check (G-0c); `df -h .` (G-0d).

Actual output (real numbers and quoted source text, not a paraphrase):

```
2026-09-28 01:07:45
--- G-0a ---
420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2  docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md
--- G-0b ---
f364c95fa2794d37611bf8dfde07feb3fbe17f9b 2026-09-28T01:05:32-04:00
git-log-exit=0
status-exit=0 (empty above = unmodified)
--- G-0c ---
2.14.0 True
G-0c-exit=0
--- G-0d ---
Filesystem      Size    Used    Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s5   228Gi   182Gi    19Gi    91%    1.8M  203M    1%   /System/Volumes/Data
```

Verdict:
- **G-0a PASS:** sha256 = `420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2` (exact match).
- **G-0b PASS:** committed — commit `f364c95fa2794d37611bf8dfde07feb3fbe17f9b`, committer date
  `2026-09-28T01:05:32-04:00` (this is the pre-registration's timestamp); `git status --short`
  for the file prints **nothing** → unmodified. Not BLOCKED; no need to tell Arnav to commit.
- **G-0c PASS:** `torch 2.14.0`, `torch.backends.mps.is_available() = True` → device = **MPS
  available**, so we may proceed to scoring tasks (CPU-time BLOCKED clause does not trigger).
- **G-0d PASS:** 19 GiB free ≥ 2 GB.
All four gates pass → S0 open, R1 may start.

Files created/modified: `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (created, this
entry). No other file touched.
Anything unexpected or worth flagging:
1. The prereg commit landed at **01:05:32**, ~2 minutes before this check — i.e. Arnav
   committed immediately before launching this session, as G-0b requires. The timestamp is
   recorded above for the record.
2. No conflict between the pre-registration and the execution doc found while reading (the
   execution doc's pass count 62,706 = 18×654 + 78×653 checks out arithmetically against
   PIN-5; Q1's earlier 62,784 was the pre-PIN-5 figure that assumed every background scores
   all 654 positions — noted now, quoted properly in G4).

---

## [R1] — Arm roster: PIN-1 draw, 96 backgrounds written to disk before any scoring
Status: PASS
Time started / finished: 2026-09-28 01:08:10 – 01:13:21 (minute-resolution start; S0 finished 01:08:10)
What I did:
Verified script numbering first: `ls scripts/1[0-9][0-9]_*.py` → the highest existing script
was `122_q2_q3_frame_and_arms.py`; `scripts/123*.py`, `124*.py`, `125*.py` → "no matches
found", so 123/124/125 are free. Named this one `scripts/123_phase2_arm_roster.py`. Read
Q3's 38-position list **off disk** from `PHASE1B_Q3_FULL_OUTPUT.txt` (not from memory):
`sorted positions: [np.int64(5), ..., np.int64(655)]`, `N_V = 38`, `Q1 = 38, Q3 = 38 -> AGREE`.
Wrote script 123 with its pre-registered docstring **before the first run** (the docstring
records PINs 1–3 as used, gates R1-G1..R1-G5 with expected values, the row-order and
"no position is 222" assumptions, and the before-any-scoring check). Ran smoke
(`N_BOOT=300`, exit 0) then full (`N_BOOT=10000`, exit 0) — no bootstrap exists here, so the
runs differ only in the banner; both disclosed per convention. Full output saved verbatim to
`PHASE2_R1_FULL_OUTPUT.txt` (144 lines). The Arm G draw followed PIN-1 literally:
`rng = np.random.default_rng(0)`; `pool = np.array(sorted frame positions)` (654, no 222);
`rng.choice(pool, size=40, replace=False)`; then, for each position **in drawn order**,
`rng.choice(sorted 19 one-letter residues excluding the FASTA wild-type residue at that
position)` with residue *p* = FASTA index *p*−1.

Actual output (real numbers and quoted source text, not a paraphrase):

```
  usable rows = 10757 (expect 10757)
  |frame| = 654 (expect 654); 222 in frame = False
  FASTA length = 656; residue p = FASTA index p-1
  wrote data/processed/phase2_arm_roster.csv  (96 rows)
  roster sha256 (computed in-script) = 9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b
  before-any-scoring check: data/processed/phase2/ exists = False, bg_*.csv files = 0 (expect 0)
  counts by arm = {'G': 40, 'V': 38, 'S': 18} (expect S=18, V=38, G=40)
  R1-G1 PASS (18 / 38 / 40, total 96)
  wt_aa == FASTA residue: 96/96 roster rows
  FASTA vs esm2_wt_scores.csv agreement over all 654 frame positions: 654/654
  R1-G2 PASS
  Arm V/G rows at position 222 = 0; 222 in frame = False; A222_V row present = False
  R1-G3 PASS
  Arm V positions == Q3's 38-list: True
  R1-G4 PASS
  Arm G: n = 40, distinct = 40, all in frame = True, 222 among them = False, mut == wt rows = 0
  R1-G5 PASS
  Arm G rows with same position AND mutant as an Arm V row: 0
    none
```

External cross-check of the in-script hash:

```
9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b  data/processed/phase2_arm_roster.csv
```

(identical to the in-script value, and identical after the smoke run and after the full run
→ the roster is deterministic across runs.)

The 40 Arm G draws, **in draw order** (bg_id = `G_<wt><pos><mut>`, exactly as written to disk):

```
G_T549H G_G317Q G_R357M G_H354F G_S494H G_E54R  G_N12P  G_G562M G_L472H G_E168S
G_K27I  G_L408H G_E16V  G_T115G G_L318F G_H613R G_K48P  G_S23A  G_W59C  G_E279K
G_E383T G_A551K G_A462S G_K510H G_P254F G_L178T G_R358V G_D629C G_V574C G_S430P
G_W595H G_M111N G_T521D G_P346V G_N3K   G_Y197V G_I192T G_L526R G_P395F G_K401S
```

Arm S (18, sorted by bg_id): A222_C, A222_D, A222_E, A222_F, A222_G, A222_H, A222_I,
A222_K, A222_L, A222_M, A222_N, A222_P, A222_Q, A222_R, A222_S, A222_T, A222_W, A222_Y
(no A222_A, no A222_V — A222V itself is not rescored, PIN-3).
Arm V (38, sorted by position): 5, 19, 70, 73, 84, 85, 98, 113, 116, 145, 155, 175, 195,
204, 209, 220, 233, 242, 292, 293, 302, 311, 328, 350, 353, 368, 396, 461, 462, 511, 522,
524, 551, 558, 587, 589, 650, 655 — identical to Q3's on-disk list (R1-G4 True).

Verdict: **PASS.** All five gates R1-G1..R1-G5 PASS with the values shown above; every
`wt_aa` equals the FASTA residue (96/96) and the FASTA agrees with `esm2_wt_scores.csv` at
654/654 frame positions (two independent sources for the wild-type sequence). The roster
exists on disk **before any Phase 2 score exists**: `data/processed/phase2/` does not exist
and `bg_*.csv = 0` at write time (frozen §3: "drawn and written to disk before any scoring").
PIN-2 collisions: **0** (reporting only, not a gate; nothing dropped).
**PINs used and logged:** PIN-1 (Arm G draw, `default_rng(0)` — the `SEED` env var does not
touch this draw; printed but unused), PIN-2 (duplicate check run, 0 collisions), PIN-3
(arms/bg_ids/total 96).

Files created/modified:
- `scripts/123_phase2_arm_roster.py` (created; pre-registered docstring written before first run)
- `data/processed/phase2_arm_roster.csv` (created; 96 rows; sha256 `9b31721a…9445b`)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_R1_FULL_OUTPUT.txt` (created; full verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)

Anything unexpected or worth flagging:
1. **Assumption (troubleshooting rule 4, logged in the docstring too):** the execution doc's
   gate wording "no position is 222" *cannot* include Arm S rows — Arm S backgrounds are
   `A222X` by frozen §3/PIN-3, so their roster `position` is 222 by definition. Read
   conservatively as: **no Arm V and no Arm G background at 222, and 222 not in the frame**
   (both verified: 0 rows, `222 in frame = False`), plus no `A222_V` row. A literal reading
   that included Arm S would contradict PIN-3 itself; flagged here rather than silently
   resolved.
2. **Assumption:** row order = Arm S sorted by bg_id → Arm V sorted by position → Arm G in
   draw order. Nothing in the pre-registration fixes row order; this order makes G1's "first
   Arm S row, first Arm V row, last Arm V row of the roster" unambiguous: **A222_C, AV_5,
   AV_655** (to be re-confirmed as cached in `task82_ae_raw.csv` at G1).
3. **PIN-2 disclosure:** two Arm G draws landed on Arm V *positions* (462 → A→S, 551 → A→K)
   but with different mutants, so under PIN-2's exact criterion (same position **and** same
   mutant) there are **0** collisions; both G rows are kept regardless (nothing dropped).
   Externally checked: `shared positions G ∩ V = [462, 551]`.
4. No `torch`/`esm` import anywhere in script 123 (execution doc: model scoring only in
   124/G1). Script 123 was **not edited after its runs**.

---

## [R2] — INFORMATIONAL pre-flight: A222V's own ρ, three views (cached only)
Status: PASS
Time started / finished: 2026-09-28 01:14 – 01:15:35
What I did:
Computed **only** A222V's own Spearman ρ from `task32_analysis_table.csv` columns
(`delta_esm`, `own_e_b`, `dropna` — the same column names scripts 121/122 use; no guessing),
in three views: (i) full frame, (ii) held-out H, (iii) held-in. H re-derived with script 122's
exact construction (`frame − (AE positions ∪ W positions)` from `task82_ae_raw.csv` and
`task69_w2_bg_raw.csv`). No bootstrap (point estimates only), **no placebo quantity computed**
(frozen: placebo ρ_b belongs to the analysis after scoring), no script numbered for R2 (the
execution doc allocates 123/124/125 to R1/G2/G3), so this ran as one inline `venv/bin/python3`
heredoc with output saved verbatim to `PHASE2_R2_FULL_OUTPUT.txt`. Gate G-A was checked inside
the same command with exit 1 on failure.

Actual output (real numbers and quoted source text, not a paraphrase):

```
  frame = 654 positions, usable rows = 10757 (expect 654 / 10757)
  |H| = 455 (expect 455)

(i) FULL FRAME : n = 10757 rows, rho = np.float64(-0.08811806424891734)
    frozen anchor target = -0.088118  |diff| = 6.425e-08
(ii) HELD-OUT H: n = 7526 rows over 455 positions, rho = np.float64(-0.09002168303339808)
(iii) HELD-IN  : n = 3231 rows over 199 positions, rho = np.float64(-0.08368142781814307)

  row accounting: 7526 + 3231 = 10757 (expect 10757)

GATE G-A (frozen): A222V's rho over the full frame reproduces -0.088118 to 1e-6
  count cross-check vs execution doc (654/10757/455/7526/3231): AGREE
  G-A PASS: |np.float64(-0.08811806424891734) - (-0.088118)| = 6.425e-08 < 1e-6

INFORMATIONAL: no arm, rule, or constant may change on the basis of these values; reported so Arnav can decide whether to run.
```

(`R2-EXIT=0`.)

Verdict: **PASS.** Gate **G-A PASS** — full-frame ρ = `−0.08811806424891734`, which is the
frozen anchor to all printed digits (Phase 1b P1 recorded the identical value
`−0.08811806424891734`); |diff| vs the printed anchor `−0.088118` = **6.425e-08 < 1e-6**.
All five count cross-checks AGREE with the execution doc: frame 654, usable 10,757, |H| = 455,
H rows 7,526, held-in rows 3,231 (7,526 + 3,231 = 10,757 closes). No placebo quantity was
computed; nothing here changes any arm, rule or constant — the entry exists so Arnav can
decide whether to run.

**INFORMATIONAL: no arm, rule, or constant may change on the basis of these values; reported
so Arnav can decide whether to run.** The three values, verbatim:
- full frame: `−0.08811806424891734` (n = 10,757)
- held-out H: `−0.09002168303339808` (n = 7,526 over 455 positions)
- held-in: `−0.08368142781814307` (n = 3,231 over 199 positions)

Files created/modified:
- `docs/tasks/phase2-full-frame-placebo/PHASE2_R2_FULL_OUTPUT.txt` (created; verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- No script created, no data file touched (read-only over the cached CSVs).

Anything unexpected or worth flagging:
1. Purely descriptive (no rule depends on it): the held-out H value `−0.0900` is *more*
   negative than the full-frame anchor `−0.0881`, and the held-in value `−0.0837` is less
   negative. Reported as observed; **no interpretation attached, no arm/rule/constant may
   change because of it** (label above), and the H value is not a placebo quantity — it is
   A222V's own ρ restricted to H rows.
2. Gate G-A is recorded here as PASS for the first time in Phase 2 (frozen §7 lists it as a
   run-time gate too; it will be re-checked by script 125 in session 2b).

---

## [G1] — Frozen gate G-B: three cached backgrounds re-scored with the model (scratch only)
Status: PASS
Time started / finished: 2026-09-28 ~01:16 – 01:29:26 (attempt 1 ~01:16–01:20 crashed on my
own bug before any score existed; attempt 2, the gate run proper, 01:20:51 – 01:24:07;
precision diagnostics 01:24 – 01:29:26)
What I did:
G1 runs as an **inline heredoc, no script number**: the execution doc allocates 123/124/125
to R1/G2/G3 and names no script for R2/G1 (decision logged per troubleshooting rule 4/5;
the pre-registration of this gate is frozen §7 G-B itself, quoted in the run's own output).
Selected the three backgrounds **from the roster file** (first Arm S row, first Arm V row,
last Arm V row) → `['A222_C', 'AV_5', 'AV_655']` (asserted). Loaded the WT sequence via
`scripts.lib.sequence.load_sequence` + `verify_sequence` (PIN-6), cached comparison via
`task82_ae_raw.csv` (score column `score_bg`, read from script 82, not guessed). Device via
`get_device()`; model loaded exactly as script 82 does:
`esm.pretrained.esm2_t33_650M_UR50D()` → `model.eval()` → `.to(device)`; one **unbatched**
`get_position_logprobs` pass per (background, cached grid position) (PIN-4), background
sequence = WT with the single substitution (PIN-6), all 120 cached grid positions per
background, writes **only** to `data/processed/phase2_scratch/`. Weights came from the local
torch.hub cache (verified present first: `esm2_t33_650M_UR50D.pt`, 2,604,537,549 bytes,
Sep 11) — **no download attempted**. Attempt 1 crashed on a bug of mine (disclosed below);
attempt 2 corrected only that self-check and re-ran the unchanged gate.

Actual output (real numbers and quoted source text, not a paraphrase).

**Attempt 1 — crash (verbatim traceback, Python exited nonzero):**

```
  --- A222_C: background A->C at 222; ...
Traceback (most recent call last):
  File "<stdin>", line 61, in <module>
AssertionError: ('A222_C', 'C', 'A')
G1-EXIT=0        <- this "0" was tee's exit status, NOT Python's (see flags)
```

The failing line was my own sanity check
`assert bg_seq[pos - 1] == wt_aa` applied to the **mutated** background sequence — for
A222_C, `bg_seq[221] = 'C'` can never equal the roster's `wt_aa = 'A'`. The assertion fails
for *every possible substitution by construction*, so it tested no data and produced no gate
value (no score was computed; the crash preceded the scoring loop; `phase2_scratch/` was
empty afterwards).

**Attempt 2 — the gate run (verbatim):**

```
G1 -- frozen gate G-B, quoted verbatim from PHASE2_PREREG.md section 7:
  "G-B: for at least three backgrounds already cached in
   task82_ae_raw.csv, freshly scored values on the cached positions
   reproduce the cached scores to 1e-6 (same model, same settings)."
...
DISCLOSURE: attempt 1 crashed on an inverted self-assertion before
any score existed (see the docstring above and the log); corrected
and re-run here -- threshold, inputs and gate unchanged.
...
  roster rows selected: ['A222_C', 'AV_5', 'AV_655'] (expect ['A222_C', 'AV_5', 'AV_655'])
Length check passed: 656
Position 222 check passed: Ala
  cache: task82_ae_raw.csv = 129960 rows, score column 'score_bg'
Using device: mps
Loading ESM-2 650M from the LOCAL torch.hub cache
(~/.cache/torch/hub/checkpoints/esm2_t33_650M_UR50D.pt, 2.6 GB,
 verified present before this run -- no download attempted)...

  --- A222_C: background A->C at 222; WT residue check = A==A True; cached grid = 120 positions, own position in grid = False; cached rows = 2280
      fresh rows = 2280, merged = 2280, max |diff| = 1.776e-15, 63.0s for 120 passes (0.525 s/pass)

  --- AV_5: background A->V at 5; WT residue check = A==A True; cached grid = 120 positions, own position in grid = False; cached rows = 2280
      fresh rows = 2280, merged = 2280, max |diff| = 1.776e-15, 63.7s for 120 passes (0.531 s/pass)

  --- AV_655: background A->V at 655; WT residue check = A==A True; cached grid = 120 positions, own position in grid = False; cached rows = 2280
      fresh rows = 2280, merged = 2280, max |diff| = 1.776e-15, 64.1s for 120 passes (0.534 s/pass)

--------------------------------------------------------------------------
  G-B A222_C: max |diff| = 1.776e-15 -> PASS (< 1e-6)
  G-B AV_5: max |diff| = 1.776e-15 -> PASS (< 1e-6)
  G-B AV_655: max |diff| = 1.776e-15 -> PASS (< 1e-6)
  device = mps; 360 passes in 190.8s = 0.530 s/pass (530 ms/pass)
G1 VERDICT: G-B PASS -- all three backgrounds reproduce the cached scores to < 1e-6; proceed to G2-G4.
Elapsed 194.4s
G1-EXIT=0
```

**Post-hoc precision diagnostics (AGENTS §5 — identical max for all three backgrounds
suspicion; run after the gate, changes no rule):**

```
A222_C vs AV_5 fresh scores identical at same cell: 0 / 2280
A222_C vs AV_655 fresh scores identical at same cell: 0 / 2280
grids equal: True
A222_C len(mg)= 2280 d.max()= 0.0 n(d>0)= 0 n_nan= 0 n(d==0)= 2280
AV_5    len(mg)= 2280 d.max()= 0.0 n(d>0)= 0 n_nan= 0 n(d==0)= 2280
AV_655  len(mg)= 2280 d.max()= 0.0 n(d>0)= 0 n_nan= 0 n(d==0)= 2280
to_csv roundtrip exact: True
writer+parser roundtrip: n_diff = 29049 / 200000, max|d| = 3.552713678800501e-15
parser on %.17g strings: n_diff = 38681 / 200000, max|d| = 3.552713678800501e-15
task82 score range: min -17.77623011590913 max 5.5839773043990135
```

Verdict: **G-B PASS — proceed to G2–G4.** The three mandated max |diff| values versus
`task82_ae_raw.csv`: **A222_C = 1.776e-15, AV_5 = 1.776e-15, AV_655 = 1.776e-15** (all
< 1e-6 by ~9 orders of magnitude); device = **mps**. The two identical maxima are explained,
not hand-waved (diagnostics above): pandas' `read_csv` float parser is not correctly rounded
(29,049/200,000 values round-trip differently; max error 3.55e-15). G1's gate comparison used
exact in-memory floats against the *parsed* cache and therefore absorbed that parse error
(1.776e-15 = one ulp in the [8,16) binade); the read-back comparison parses both files with
the same parser, so identical stored strings cancel and give **exactly 0.0 on 2,280/2,280
cells for each of the three backgrounds** — i.e. as stored, today's fresh scores are
bit-identical to script 82's cached scores. Both measurements are ~9 orders of magnitude
inside the frozen 1e-6 threshold; the threshold was never touched. No duplication: at shared
(position, mut_aa) cells the three fresh files agree at 0/2,280 cells (backgrounds genuinely
differ), and all three grids are the same 120 positions with no background's own position
included (script 82's G3 property, re-verified).

Measured **0.530 s/pass (530 ms/pass)** → 62,706 passes × 0.530 s ≈ 33,200 s ≈ **9.2 h**
projected for the overnight run (inside Q1's 8.9–11.3 h window).

Files created/modified:
- `data/processed/phase2_scratch/A222_C.csv`, `AV_5.csv`, `AV_655.csv` (created; fresh
  scores only — **`data/processed/phase2/` still does not exist**, verified after the run)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_G1_FULL_OUTPUT.txt` (attempt 2's verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry; attempt 1's text lives
  here — see flag 2)

Anything unexpected or worth flagging:
1. **My bug, fixed and disclosed (AGENTS §6):** attempt 1's inverted assertion checked the
   mutated sequence against the WT residue — it could never pass, tested no data, and
   produced no gate value. Corrected to PIN-6's only coherent reading (WT sequence residue at
   the background position == roster `wt_aa`, *before* substituting — the same check script
   82's own G1 gate did: "letter matches the table wt_aa ... at background positions"), plus
   an assertion that the substitution landed (`bg_seq[pos-1] == mut_aa`). The G-B threshold,
   the three backgrounds, the cached comparisons and every input are unchanged; no Phase 2
   score existed when the fix was made (nothing had been scored). This is a self-check bug
   fix, not a gate adjustment — stated here so nobody later mistakes attempt 1 for a gate
   failure.
2. **Attempt 1's output file was overwritten:** attempt 1's `tee` wrote to
   `PHASE2_G1_FULL_OUTPUT.txt`, and attempt 2's `tee` overwrote it (same path). Attempt 1's
   verbatim text (crash included) is preserved in this entry instead. Also: attempt 1's
   recorded `G1-EXIT=0` was **`tee`'s** exit status, not Python's (Python exited nonzero —
   the traceback proves it); attempt 2 captured `${pipestatus[1]}` correctly (real status 0).
3. **AGENTS §5 check performed rather than assumed:** the three identical `1.776e-15` maxima
   triggered a duplication suspicion; investigated and cleared as reported above (no
   duplication; mechanism = read_csv parse imprecision, quantified).
4. No `esm.pretrained` download (weights verified in the local cache first). No file written
   outside `phase2_scratch/` and the two `docs/.../PHASE2_*` files. Protected files untouched
   (`git status` clean for all of them).

---

## [G2] — Scoring script 124 + smoke/resume tests (a)–(d) in scratch
Status: PASS
Time started / finished: 2026-09-28 01:30 – 01:35:13
What I did:
Wrote `scripts/124_phase2_score_backgrounds.py` — the exact filename the execution doc
prescribes — with its pre-registered docstring **before the first run** (the docstring pins
PINs 4/5/6 as implemented, the output contract `bg_id, position, mut_aa, score`, the atomic
`.tmp → os.replace` publish, the skip/resume rule, the manifest schema, ETA semantics,
exception handling, the CLI flags, the in-script checks, the (a)–(d) test plan, and the
no-edit-after-scores-exist rule). Then ran the four mandated tests, all confined to
`data/processed/phase2_scratch/` via `--out-dir`.

Actual output (real numbers and quoted source text, not a paraphrase).

**First test attempt — crash before any score (verbatim):**

```
Traceback (most recent call last):
  File ".../scripts/124_phase2_score_backgrounds.py", line 281, in <module>
    main()
  File ".../scripts/124_phase2_score_backgrounds.py", line 176, in main
    from scripts.lib.sequence import load_sequence, verify_sequence
ModuleNotFoundError: No module named 'scripts'
TEST-A-EXIT=1
```

(both (a) and the immediate (b) repeat failed identically). Cause: running
`venv/bin/python3 scripts/124_*.py` puts `scripts/` on `sys.path`, not the repo root. Fixed
with the project's own established convention — 20+ scripts including 82 use exactly
`sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` (grep verified) — inserted
before any `scripts.lib` import. **No score existed when the fix was made** (the runs died at
import, before the roster was even read), so execution-doc rule 7 ("not edited after any
Phase 2 score exists") is intact; disclosed here per AGENTS §6.

**Test (a) — `--only A222_C --limit-positions 5` (verbatim):**

```
124 -- Phase 2 background scorer  N_BOOT=10000 SEED=0 (both UNUSED: no bootstrap/randomness here)  out_dir=data/processed/phase2_scratch
Length check passed: 656
Position 222 check passed: Ala
  roster rows to process: 1; frame = 654
  skip logic checks FINAL files only; .tmp never counts
  pre-scan: 0 complete, 1 to score
Using device: mps
Loading ESM-2 650M from the local torch.hub cache (never downloads; stops if a download were attempted)...
  scored A222_C: 5 positions, 95 rows in 3.0s (596 ms/pass) | run 1/1, elapsed 0.0m, ETA 0.00h

Done. Scored 1, skipped 0; wall 0.0m; manifest -> data/processed/phase2_scratch/manifest.csv
TEST-A-EXIT=0
```

**Test (b) — repeat, expect skip (verbatim):**

```
  roster rows to process: 1; frame = 654
  skip logic checks FINAL files only; .tmp never counts
  SKIP A222_C: complete file already exists (95 rows expected)
  pre-scan: 1 complete, 0 to score
Nothing to do.
TEST-B-EXIT=0
```

**Test (c) — fake `.bg_AV_5.csv.tmp` left in scratch, then run (verbatim):**

```
--- before (ls shows): .bg_AV_5.csv.tmp (57 bytes, "FAKE STALE TMP CONTENT - MUST BE IGNORED AND OVERWRITTEN")
  pre-scan: 0 complete, 1 to score        <- the fake .tmp was IGNORED (not treated as completion)
  scored AV_5: 5 positions, 95 rows in 2.7s (536 ms/pass) | run 1/1, elapsed 0.0m, ETA 0.00h
TEST-C1-EXIT=0
--- after: .bg_AV_5.csv.tmp gone; bg_AV_5.csv (2763 bytes) present
fake tmp no longer exists (overwritten/published)
```

**Test (c2, extra) — fake `.tmp` while the final file is complete (verbatim):**

```
  SKIP AV_5: complete file already exists (95 rows expected)
  pre-scan: 1 complete, 0 to score
Nothing to do.
TEST-C2-EXIT=0
--- fake tmp untouched? ---
FAKE TMP 2 - SHOULD NOT AFFECT SKIP
cleaned up
```

**Test (d) — row counts exactly 5 × 19 (verbatim):**

```
bg_A222_C.csv rows = 95 (expect 95 = 5x19) | columns = ['bg_id', 'position', 'mut_aa', 'score'] | positions = [2, 3, 4, 5, 6] | dup pairs = 0
bg_AV_5.csv rows = 95 (expect 95 = 5x19) | columns = ['bg_id', 'position', 'mut_aa', 'score'] | positions = [2, 3, 4, 6, 7] | dup pairs = 0
manifest:
 bg_id  n_positions  n_rows  seconds device
A222_C            5      95    2.980    mps
  AV_5            5      95    2.678    mps
--- real out-dir still absent? ---
ls: data/processed/phase2/: No such file or directory
```

Verdict: **PASS.** All four mandated tests behave exactly as specified: (a) writes 95 rows
atomically + manifest row; (b) skips; (c) a stray `.tmp` is ignored by the skip logic and
overwritten by the real write; (d) both test files are exactly 5 × 19 = 95 rows with the
prescribed columns and no duplicate (position, mut_aa) pairs. Bonus evidence in (d):
PIN-5 is visibly working — `AV_5` scores `[2, 3, 4, 6, 7]` (its own position 5 excluded)
while `A222_C` scores `[2, 3, 4, 5, 6]`. The real output directory
`data/processed/phase2/` **still does not exist** — nothing touched the overnight run's
destination. Device recorded in the manifest: `mps`. Small-N pace 596/536 ms/pass, in line
with G1's 530 ms/pass.

Files created/modified:
- `scripts/124_phase2_score_backgrounds.py` (created; pre-registered docstring; one
  post-attempt fix before any score existed, disclosed above)
- `data/processed/phase2_scratch/bg_A222_C.csv`, `bg_AV_5.csv`, `manifest.csv` (test artifacts)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)

Anything unexpected or worth flagging:
1. **Disclosed fix #2 this session** (after G1's attempt 1): the `sys.path` import crash
   above. Both failed attempts produced no score and no file; fix = project convention only,
   applied before any score existed. Script 124 is now treated as frozen for the launch.
2. **Output column naming (flagged for G3):** the execution doc fixes the overnight schema as
   `score` (124 writes `score`), while the cached `task82_ae_raw.csv` uses `score_bg`.
   Followed the doc literally; the analysis script must map between them — noted for G3's
   implementation, no rule affected.
3. **Skip check strengthened (disclosed):** the doc requires "expected row count"; the
   implementation additionally requires the exact position set and no duplicate pairs
   (script 82's checkpoint precedent). Strictly stronger — can only fail earlier, can never
   pass an incomplete file — loosens nothing.
4. The first five frame positions are 2–6 (frame starts at position 2), so
   `--limit-positions 5` exercises position 5 for `AV_5` — the own-position skip shows up
   naturally in the test data (flag (d) output above).

---

## [G3] — Script 125 cached-ae validation: smoke (N_BOOT=300) + full (N_BOOT=10000)
Status: PASS
Time started / finished: 2026-09-28 01:35 (script written) – 02:02:23 (full run done)

What I did:
Wrote `scripts/125_phase2_analysis.py` with its pre-registered docstring (frozen §§2/4/5/6/7
quoted in-script, both input modes, gates G-A/C/D/E + input gates, cached-ae validation
targets to 1e-9, PIN-9 naive loop, PIN-10 stream table) **before its first run**. Then made a
set of pre-run corrections (no output had been produced yet — see flag 1), compiled clean, and
ran only `--mode cached-ae`:

1. Smoke: `N_BOOT=300 N_PERM=300 venv/bin/python3 scripts/125_phase2_analysis.py --mode cached-ae`
   (see flag 2 re: two invocations), recorded run exit 0, 9.5 s.
2. Full: `N_BOOT=10000 N_PERM=10000 venv/bin/python3 scripts/125_phase2_analysis.py --mode cached-ae`,
   **exit 0**, 298.0 s, saved verbatim as `docs/tasks/phase2-full-frame-placebo/PHASE2_G3_FULL_OUTPUT.txt`.
3. **`--mode phase2` was invoked ZERO times this session** (no Phase 2 score exists; execution doc rule).

**Validation targets — verbatim from the full output (execution doc G3, gate 1e-9):**

```
--------------------------------------------------------------------------
VALIDATION TARGETS (execution doc G3; deterministic quantities, gate 1e-9)
--------------------------------------------------------------------------
  n(V) == 38: got 38.0 want 38.0 -> PASS
  mean rho_b(V): computed -0.01013806778206523 vs target -0.010138068 |diff| = 2.179e-10 -> PASS (gate < 1e-9)
  p_spec: computed 0.02564102564102564 vs target 0.025641026 |diff| = 3.590e-10 -> PASS (gate < 1e-9)
  #(rho_b <= rho_A222V) == 0: got 0.0 want 0.0 -> PASS
  D = mean(S) - mean(V): computed -0.04507070645463121 vs target -0.045070706 |diff| = 4.546e-10 -> PASS (gate < 1e-9)
  ALL VALIDATION TARGETS PASS (reproduction of Phase 1b P4/P2 deterministic quantities; REPRODUCTION IS NOT REPLICATION, AGENTS 6)
```

Each computed value, rounded to the 9 decimals the execution doc quotes, is identical to its
target; the ~2–5e-10 residuals are the rounding of the printed target itself, and every one is
well inside the 1e-9 gate.

**Input / frozen gates — verbatim from the full output:**

```
  own_e_b cross-check: task32 vs own_context_metrics over 10757 frame rows: mismatches = 0 (expect 0)
  PIN-8 regions vs task32 region column: mismatches = 0/10757 (expect 0)
  H: 455 positions, 7526 frame rows (script 122 recorded 455 / 7526)
  rho = -0.08811806424891734; target -0.088118 |diff| = 6.425e-08 (gate < 1e-6)
  G-A PASS
  paired frame: rows per background = 1932 (Phase 1 recorded 1932); identical sets across 57 backgrounds: True
  A222V rho on this frame = -0.104321773 (execution doc validation threshold -0.104321773)
  threshold gate: |diff| = 6.529e-11 < 1e-9 PASS
  point-rho identity vs task109_placebo_rhos.csv over 56 backgrounds: max|diff| = 9.714e-17 (gate < 1e-9)
  input gate PASS
  G-C PASS: 0 rows with target position == background position in any rho_b input (own-position rows pre-dropped: 0)
  G-D: identity draw (every cluster once) vs point rho: max|diff| = 0.000e+00 (gate < 1e-12)
  G-D PASS
  min positions covered by any background = 120 (denominator 120; gate >= 114.0)
  G-E PASS
```

**Validation-mode numbers from the full N_BOOT=10000 run (VALIDATION ONLY — never quotable
as the pre-registered result, which requires `--mode phase2` in session 2b):**

- `p_spec` on the AE grid = 0.025641026 (0 of 38 null placebos at or below A222V's
  −0.104321773); `p_spec(H)` = n/a (H ∩ grid = ∅ by construction, printed as such).
- `D_site = mean(S) − mean(N) = -0.045070706`, position-cluster bootstrap 95% CI
  (SEED+0, 10000 draws) = `[-0.107025598, +0.017286053]` (valid 10000), label permutation
  (10000 shuffles, TWO-SIDED on |D|, SEED+2) `p = (1 + 8) / (1 + 10000) = 0.000900`.
- Gradient `T = Spearman(rho_b, Grantham(X, V)) over Arm S (n=18) = -0.182662539`,
  CI `[-0.605779154, +0.364293086]` (valid 10000/10000), LOO `[-0.284313725, -0.056372549]`
  (T > 0 in 0/18), min detectable |T| ≈ 2.8 × SE = 0.719223081 → **NOT RESOLVED** (required
  wording: "n = 18 cannot resolve this," never "flat").
- Runtime: primary pass 147.9 s / 10000 draws (14.8 ms/draw), secondary region-demeaned pass
  148.4 s, total elapsed 298.0 s. Cached-ae is validation machinery only — the phase2-mode
  runtime is governed by G1's measured 530 ms/pass (see G4).

Verdict: **PASS.** Every validation target, input gate, and frozen gate (G-A, G-C, G-D, G-E)
passed at the prescribed thresholds on both the smoke and the full run, single-shot, with no
gate loosened and no retry. Script 125 is now treated as frozen for session 2b (rule: never
edited after any Phase 2 score exists).

Files created/modified:
- `scripts/125_phase2_analysis.py` (created; pre-registered docstring; pre-run corrections
  disclosed in flag 1, all made before any output existed)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_G3_FULL_OUTPUT.txt` (created; full-run verbatim)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)

Anything unexpected or worth flagging:
1. **Pre-run corrections to script 125 before its first run** (no output existed yet;
   disclosed per AGENTS §6): (a) bootstrap cluster list now taken from positions *actually
   present* in the analysis rows — cached-ae analyses the 120-position grid, so drawing over
   all 654 frame positions would have injected empty clusters and distorted the bootstrap
   (`A.clusters_full` set by each mode builder); (b) the secondary "outcome word would be"
   print passed `None` to a comparator for the cached-ae/full-frame-secondary path (would
   raise `TypeError`); moved the word computation to a single guarded place in `main`; (c) the
   primary-H per-arm table's rank line referenced `point_h["__A222V__"]`, which does not
   exist (A222V is the anchor, not an `add_bg` row) — now passes the H-frame `rho_h_a`;
   (d) NaN assertions added after each score join in `build_phase2`; (e) validation targets
   gated early (fail-fast, immediately after the input gates) per the execution doc's
   "GATE FAIL and exit 1, no retry"; (f) two dead-code artifacts removed (an
   `X if False else Y` expression and an unused variable). No constant, threshold, seed,
   arm definition, or decision rule was touched.
2. **Two smoke invocations, one code state:** the first `N_BOOT=300` invocation's terminal
   capture was truncated by the harness before its exit line, so the identical command was
   re-run with output redirected to a file; the recorded run exited 0 and its full 192-line
   output is what was inspected above. No code changed between the two invocations.
3. The D_site permutation sidedness is **not stated in frozen §5**; implemented two-sided on
   |D| following script 121's precedent, printed in the output and disclosed in-script (this
   was pinned pre-run as the coherent reading; it is not a post-result choice — the smoke and
   full runs both used it unchanged).
4. Cached-ae secondary (region-demeaned) p_spec printed 0.076923077 — recorded here only as
   evidence the secondary path executes; it is NON-DECISION (frozen §6) and must never be
   reported as a result.

---

## [G4] — Launch script `scripts/launch_phase2.sh` (--dry-run tested only; NOT launched)
Status: PASS
Time started / finished: 2026-09-28 02:03 – 02:10:14

What I did:
Wrote `scripts/launch_phase2.sh` (the exact filename the execution doc prescribes) with its
behavior docstring, then tested **`--dry-run` only**. The real launch path of this script was
never executed; `data/processed/phase2/` still does not exist (`ls` confirms "No such file or
directory" after every test).

**`bash scripts/launch_phase2.sh --dry-run` — exit 0, verbatim:**

```
DRY RUN -- nothing below this line was executed or created.
repo root: /Users/arnavchavan/Desktop/mthfr-context-dependence

1) mkdir -p data/processed/phase2

2) the detached attempt loop, launched as:
   nohup bash -c '<attempt loop below>' _ \
     'data/processed/phase2/run.log' 'venv/bin/python3' 'scripts/124_phase2_score_backgrounds.py' 5 30 'data/processed/phase2/run.pid' >> 'data/processed/phase2/run.log' 2>&1 &
   with the wrapper PID written to data/processed/phase2/run.pid; attempt loop body:
   -----------------------------------------------------------------
   log="$1"; py="$2"; scorer="$3"; attempts="$4"; nap="$5"; pidf="$6"
   child=""
   on_term() {
     echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) received TERM/INT -- stopping current scorer" >> "$log"
     if [ -n "$child" ]; then kill -TERM "$child" 2>/dev/null; fi
     exit 130
   }
   trap on_term TERM INT QUIT
   i=1
   while [ "$i" -le "$attempts" ]; do
     echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) attempt $i/$attempts started" >> "$log"
     "$py" "$scorer" >> "$log" 2>&1 &
     child=$!
     wait "$child"; rc=$?
     child=""
     echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) attempt $i/$attempts exited rc=$rc" >> "$log"
     if [ "$rc" -eq 0 ]; then
       echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) SUCCESS on attempt $i (scorer exit 0)" >> "$log"
       exit 0
     fi
     if [ "$i" -lt "$attempts" ]; then
       echo "[launcher] nonzero exit -> sleeping ${nap}s before retry" >> "$log"
       sleep "$nap"
     fi
     i=$((i + 1))
   done
   echo "[launcher] $(date +%Y-%m-%dT%H:%M:%S) GAVE UP after $attempts attempts" >> "$log"
   exit 1
   -----------------------------------------------------------------
   (each attempt runs exactly: venv/bin/python3 scripts/124_phase2_score_backgrounds.py, appending to data/processed/phase2/run.log;
    script 124 skips completed backgrounds on every attempt,
    writes scores atomically to data/processed/phase2/bg_<id>.csv + manifest.csv)

3) caffeinate -ims -w $PID &   (keeps the Mac awake on AC until the run ends)

MONITOR:
  tail -f data/processed/phase2/run.log
  ls data/processed/phase2/bg_*.csv | wc -l
RESUME after an interruption: rerun this same launch script --
  bash scripts/launch_phase2.sh
  (attempt 1 skips every background that already has a complete file)
STOP:
  kill $(cat data/processed/phase2/run.pid)
projection: 96 backgrounds; 62,706 passes = 18x654 + 78x653
  (vs Q1's 62,784 = 96x654 before each V/G background's own position is skipped);
  511-647 ms/pass (execution doc record) ~= 8.9-11.3 h;
  measured G1 pace 0.530 s/pass (530 ms) -> 62,706 x 0.530 ~= 9.2 h
DRYRUN-EXIT=0
```

Post-test checks: `bash -n scripts/launch_phase2.sh` → SYNTAX-OK; after the dry run,
`ls data/processed/phase2/` → "No such file or directory" (nothing created).

**The four records the execution doc requires, verbatim (as printed above and as they appear
in the script):**

- How to monitor:
  `tail -f data/processed/phase2/run.log`
  `ls data/processed/phase2/bg_*.csv | wc -l`
- How to resume after an interruption: rerun the same launch script
  `bash scripts/launch_phase2.sh` (attempt 1 skips every completed background via script
  124's own skip/resume logic)
- How to stop: `kill $(cat data/processed/phase2/run.pid)`
- Projected finish: 96 backgrounds; **62,706 passes = 18×654 + 78×653** (versus Q1's 62,784 =
  96×654 before each V/G background's own position is skipped), at the recorded 511–647
  ms/pass ≈ **8.9–11.3 h**; at this session's measured **G1 = 0.530 s/pass (530 ms)** ≈
  **9.2 h** (G2's small-N paces, 596 and 536 ms/pass, are consistent).

**Sandbox test of the attempt-loop wrapper (disclosed; see flag 1 re: a doc conflict):** the
wrapper body was extracted programmatically from `launch_phase2.sh` between its `WRAP_EOF`
markers (28 lines — identical to the dry-run print above) and exercised with stub scorers in
an isolated temp directory. The launch script's real path was never invoked; no real scorer,
no repo path, no `data/processed/phase2/` was touched. Results:

```
TEST A (success on attempt 1):  exit 0;  log: attempt 1/5 started -> exited rc=0 -> SUCCESS on attempt 1
TEST B (fail once, then retry): exit 0;  log: attempt 1/5 exited rc=3 -> "sleeping 1s before retry"
                                        -> attempt 2/5 exited rc=0 -> SUCCESS on attempt 2
TEST C (stop command):          kill of the wrapper PID -> trap fired, log "received TERM/INT --
                                stopping current scorer", wrapper exit 130, scorer child GONE
TEST D (attempts exhausted):    3 attempts all rc=2 -> log "GAVE UP after 3 attempts", exit 1
```

Verdict: **PASS.** Dry-run behaves as specified and creates nothing; the attempt loop,
retry, TERM-forwarding (so the prescribed `kill` really stops scoring), and give-up paths all
behave as specified against stubs.

Files created/modified:
- `scripts/launch_phase2.sh` (created; behavior docstring; never run without `--dry-run`)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)

Anything unexpected or worth flagging:
1. **Doc conflict, flagged not silently resolved (AGENTS §9):** execution doc G4 says "Test
   `--dry-run` only"; AGENTS §7 says "test before handing over ... run end-to-end, then
   clean-room test." AGENTS.md wins per its own precedence rule, so the wrapper was tested
   end-to-end **against stubs in an isolated temp directory** — which does not execute the
   launch path or anything the execution doc was protecting against (the real scoring run).
   Nothing real was launched; disclosed here so the deviation from the literal instruction is
   visible.
2. **zsh caveat for the prescribed monitor command:** this machine's zsh aborts an unmatched
   glob before `ls` runs (`zsh: no matches found`), so `ls data/processed/phase2/bg_*.csv |
   wc -l` will print an error and no 0 when no files exist yet. The command is recorded
   verbatim as the execution doc requires; if run under zsh with zero files, use
   `ls data/processed/phase2/ | grep -c '^bg_'` instead. Under bash/sh the verbatim command
   works (ls errors to stderr, wc prints 0).
3. **`caffeinate -ims -w <pid>` lifetime:** it waits only on the wrapper PID, so it stops
   holding sleep prevention the moment the wrapper exits (success, give-up, or kill) — the
   Mac may sleep again afterwards, which is the correct behavior. `-s` also requires AC
   power, matching the doc's "on AC power" wording.
4. **Stop command is genuinely effective** (tested, TEST C): the wrapper traps TERM/INT/QUIT
   and forwards the signal to the running python child, then exits 130. A bare `kill` on a
   plain loop script would have left the scorer running; the trap is why `run.pid` points at
   the wrapper.
5. The scorer's own ETA/progress lines interleave into `run.log` (script 124 prints
   `run k/96 ... ETA` per pass), so `tail -f` shows progress without any extra plumbing.

---

## SUMMARY (2a)

Session 2a ran 2026-09-28 01:07:45 – 02:13:19 and completed tasks S0, R1, R2, G1, G2, G3, G4.

**(1) Status: READY-TO-LAUNCH.**
All seven session-2a tasks PASS; every gate in (5) passed at its prescribed threshold with no
loosening and no retry. The pre-registration is intact — `PHASE2_PREREG.md` sha256 re-verified
at session end = `420459ac3d78ca4748f58d454eb74afa4dd2c127f56f710eb0e518e8c8d335f2`,
`git status --short` on it empty (unmodified; committed as
`f364c95fa2794d37611bf8dfde07feb3fbe17f9b` at 2026-09-28T01:05:32-04:00). No `git add` /
`commit` / `push` this session; `RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
`PROJECT_SUMMARY_FINAL.md`, `AGENTS.md` untouched. **The overnight run was never launched:**
`data/processed/phase2/` does not exist (verified after every task), `--mode phase2` of script
125 was invoked zero times, and `scripts/launch_phase2.sh` was run with `--dry-run` only.
Nothing blocks launch: torch 2.14.0 / MPS available, 19 GiB free, prereg committed and
unmodified. Launching is Arnav's hand-run after reading this log; session 2a does not poll it.

**(2) R2's three informational ρ values (verbatim, [R2]):**

```
(i) FULL FRAME : n = 10757 rows, rho = np.float64(-0.08811806424891734)
(ii) HELD-OUT H: n = 7526 rows over 455 positions, rho = np.float64(-0.09002168303339808)
(iii) HELD-IN  : n = 3231 rows over 199 positions, rho = np.float64(-0.08368142781814307)
```

INFORMATIONAL label printed with them: "no arm, rule, or constant may change on the basis of
these values; reported so Arnav can decide whether to run."

**(3) G1's three max |diff| values (verbatim, [G1] lines 321–323):**

```
  G-B A222_C: max |diff| = 1.776e-15 -> PASS (< 1e-6)
  G-B AV_5: max |diff| = 1.776e-15 -> PASS (< 1e-6)
  G-B AV_655: max |diff| = 1.776e-15 -> PASS (< 1e-6)
```

**(4) Roster sha256 + 40 Arm G draws + PIN-2 collision:**
- sha256 (identical in-script, external `shasum`, smoke run, full run):
  `9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b`
- The 40 Arm G draws in draw order (verbatim, [R1]):

```
G_T549H G_G317Q G_R357M G_H354F G_S494H G_E54R  G_N12P  G_G562M G_L472H G_E168S
G_K27I  G_L408H G_E16V  G_T115G G_L318F G_H613R G_K48P  G_S23A  G_W59C  G_E279K
G_E383T G_A551K G_A462S G_K510H G_P254F G_L178T G_R358V G_D629C G_V574C G_S430P
G_W595H G_M111N G_T521D G_P346V G_N3K   G_Y197V G_I192T G_L526R G_P395F G_K401S
```

- PIN-2 collision: **0** (criterion = same position AND same mutant). Two Arm G draws share
  *positions* with Arm V — 462 (A→S) and 551 (A→K) — different mutants, so no collision;
  both rows kept, nothing dropped (report-only, not a gate).

**(5) Every gate — name, PASS/FAIL, value:**

*S0 (integrity):*
- G-0a prereg sha256 `420459ac…c8d335f2` — **PASS** (exact match)
- G-0b prereg committed `f364c95fa2794d37611bf8dfde07feb3fbe17f9b` @
  2026-09-28T01:05:32-04:00, `git status` empty — **PASS**
- G-0c torch 2.14.0, `mps.is_available() = True` — **PASS**
- G-0d disk free 19 GiB ≥ 2 GB — **PASS**

*R1 (roster):*
- R1-G1 counts S=18 / V=38 / G=40, total 96 — **PASS**
- R1-G2 `wt_aa` == FASTA residue 96/96; FASTA vs `esm2_wt_scores.csv` 654/654 — **PASS**
- R1-G3 Arm V/G rows at 222 = 0; 222 not in frame; no `A222_V` row — **PASS**
- R1-G4 Arm V positions == Q3's 38-list: True — **PASS**
- R1-G5 Arm G: n = 40, distinct = 40, all in frame, 222 absent, mut == wt rows 0 — **PASS**
- PIN-2 collisions = 0 (report-only) — value 0

*R2 (informational + first G-A):*
- G-A A222V full-frame ρ `−0.08811806424891734` vs anchor `−0.088118`: |diff| = **6.425e-08 < 1e-6 — PASS**
- count cross-check 654 / 10,757 / 455 / 7,526 / 3,231 — **AGREE**

*G1 (frozen model gate):*
- **G-B** A222_C **1.776e-15**, AV_5 **1.776e-15**, AV_655 **1.776e-15** (< 1e-6) — **PASS ×3**
- device = mps; 360 passes in 190.8 s = 0.530 s/pass
- no-duplication diagnostic: identical cells between fresh files 0/2,280 each pair; read-back
  comparison 0.0 on 2,280/2,280 ×3 (parse-error mechanism quantified, 3.55e-15)

*G2 (scorer tests, all exit 0 in scratch):*
- (a) 95 rows (5×19) written atomically + manifest row — **PASS**
- (b) repeat skips ("complete file already exists (95 rows expected)") — **PASS**
- (c) stray `.bg_AV_5.csv.tmp` ignored by skip logic, overwritten by real write — **PASS**
- (d) both test files 95 rows, prescribed columns, no duplicate (position, mut_aa); PIN-5 own-
  position skip visible (`AV_5` scored [2,3,4,6,7]) — **PASS**

*G3 (cached-ae validation, gate 1e-9 on deterministic quantities):*
- grid threshold `−0.104321773`: |diff| = **6.529e-11 < 1e-9 — PASS**
- point-rho identity vs `task109_placebo_rhos.csv` over 56 backgrounds: max|diff| = **9.714e-17 < 1e-9 — PASS**
- paired frame: 1,932 rows/background, identical sets across 57 backgrounds — **True**
- n(V) = 38 — **PASS**
- mean ρ_b(V) `−0.01013806778206523` vs `−0.010138068`: |diff| = **2.179e-10 < 1e-9 — PASS**
- p_spec `0.02564102564102564` vs `0.025641026`: |diff| = **3.590e-10 < 1e-9 — PASS**
- #(ρ_b ≤ ρ_A222V) = 0 of 38 — **PASS**
- D `−0.04507070645463121` vs `−0.045070706`: |diff| = **4.546e-10 < 1e-9 — PASS**
- G-A (re-checked in script 125): 6.425e-08 < 1e-6 — **PASS**
- G-C own-position rows in any ρ_b input: 0 — **PASS**
- G-D identity draw vs point ρ: max|diff| = **0.000e+00 < 1e-12 — PASS**
- G-E min positions covered per background: **120 ≥ 114.0 (95% of 120) — PASS**
- helpers: `own_e_b` mismatch 0/10,757; PIN-8 region mismatch 0/10,757; H = 455 / 7,526

*G4 (launcher):*
- `--dry-run` exit **0**, prints plan, creates nothing (`phase2/` still absent) — **PASS**
- `bash -n scripts/launch_phase2.sh` — **PASS**
- sandbox wrapper tests A (success), B (retry-then-success), C (TERM forwarding stops the
  scorer, exit 130), D (give-up after N attempts, exit 1) — **PASS ×4**

*Pending (by design, session 2b):* gates G-A, G-C, G-D, G-E under `--mode phase2`, plus A1's
file-completeness G-E — not run, no Phase 2 scores exist.

**(6) Measured seconds-per-pass and projected finish:**
- G1 measured: **0.530 s/pass (530 ms/pass)** — 360 passes in 190.8 s, device mps (per
  background: 0.525 / 0.531 / 0.534 s/pass). G2 small-N paces 596 and 536 ms/pass agree.
- Projected finish: **62,706 passes** (= 18×654 + 78×653; vs Q1's 62,784 = 96×654 before the
  own-position skips) × 0.530 s ≈ 33,200 s ≈ **9.2 h**; at the execution doc's recorded
  511–647 ms/pass ≈ **8.9–11.3 h**.

**(7) Exact launch / monitor / resume / stop commands:**

```bash
# launch (from the repo root; hand-run by Arnav AFTER reading this log — session 2a did NOT run this)
bash scripts/launch_phase2.sh
# monitor
tail -f data/processed/phase2/run.log
ls data/processed/phase2/bg_*.csv | wc -l
# resume after an interruption (same script; completed backgrounds are skipped)
bash scripts/launch_phase2.sh
# stop
kill $(cat data/processed/phase2/run.pid)
```

(zsh caveat for the `ls` line, [G4] flag 2: with zero files zsh aborts the unmatched glob;
run it under bash, or use `ls data/processed/phase2/ | grep -c '^bg_'`.)

**(8) Every PIN used this session and any deviation:**
- **PIN-1** (Arm G draw, `default_rng(0)`) — used in R1; no deviation (`SEED` env does not
  touch this draw; printed but unused).
- **PIN-2** (duplicate check) — used in R1; 0 collisions; nothing dropped.
- **PIN-3** (arms/bg_ids/total 96) — used in R1; no deviation.
- **PIN-4** (scoring: `get_position_logprobs` + `get_device`) — used as G1's code path and
  encoded in script 124; no deviation.
- **PIN-5** (every frame position except the background's own) — used in G1 ("own position in
  grid = False") and script 124; no deviation.
- **PIN-6** (background sequence from `load_sequence`) — **used with a disclosed deviation:**
  attempt 1's inverted assertion (`bg_seq[pos-1] == wt_aa`, impossible for any substitution)
  was corrected to PIN-6's only coherent reading (`wt_seq[pos-1] == wt_aa`, script 82's
  precedent) *before any score existed*; threshold/inputs unchanged ([G1] flag 1).
- **PIN-7** (usable rows, delta = score − esm2_score) — used in script 125's builds; no deviation.
- **PIN-8** (regions R1 2–147, R2 148–294, R3 295–474, R4 475–656) — used in script 125;
  gated 0/10,757 mismatches vs `task32.region`; no deviation.
- **PIN-9** (bootstrap speed) — the **naive `spearmanr` loop was used** (weighted mid-rank
  acceleration NOT used), so its "gate vs scipy" requirement is N/A and printed as such.
- **PIN-10** (seeds) — `SEED=0`, separate streams printed (SEED+0 primary, +1 primary H, +2
  D_site permutation, +3 secondary, +4 secondary H); no deviation.
- Other disclosed deviations/assumptions, each in its entry: R1's "no position is 222" gate
  read as no Arm V/G at 222 (Arm S is 222 by definition) + roster row-order assumption; the
  D_site label permutation implemented **two-sided on |D|** (frozen §5 states no sidedness —
  script 121 precedent, logged as an ambiguity resolution); G2's `sys.path` import fix (project
  convention, before any score); G3's pre-run corrections to script 125 (listed in [G3] flag 1)
  and the two-invocation smoke capture; G4's AGENTS §7 vs "test `--dry-run` only" conflict
  (sandbox stub tests, flagged not silently resolved).

**(9) Read first:** `## [G1]` — **line 249** of this log: the frozen G-B gate that unlocked
G2–G4, its three 1.776e-15 values, the quantified parse-error mechanism, the measured
0.530 s/pass, and the one substantive code-bug disclosure of the session.

STOP. Session 2a ends here: no polling, no sleep-wait, no scoring.

---

## [A0] — Manifest deduplication: 158 rows for 96 backgrounds → `manifest_dedup.csv`
Status: PASS
Time started / finished: 2026-09-29 13:0x – 13:2x (session clock; see file mtimes below)
What I did:
Wrote `scripts/130_phase2_dedup_manifest.py` (next free number — 126–129 are taken by other
sessions' dimer-interface/GB1 work, verified with `ls scripts/*.py | sort -n`) with its
selection rule **frozen in the docstring before the first run** (AGENTS §6). The rule, verbatim
from the docstring: *"for each bg_id with more than one manifest row, keep the single row whose
event is closest in time to the mtime of the actual file `bg_<bg_id>.csv` on disk."*
`manifest.csv` is **not** overwritten; the deduplicated table goes to
`data/processed/phase2/manifest_dedup.csv` (sha256 before and after printed).

The rule needs each row's *logged event time*, and `manifest.csv` has no timestamp column, so
the script reconstructs it from sources that are **independent of any file mtime**:
1. `run.log` has one `scored <bg_id>` line per event, printed by script 124 **after** that
   background's `os.replace` and **after** its manifest append (script 124 lines 256 → 270 →
   276). So the order of those lines is the true global publish order across all processes.
2. Each line carries the event's duration and that process's cumulative `elapsed` counter.
3. Each `[launcher] … attempt 1/5 started` line carries a wall-clock timestamp written by the
   shell wrapper at spawn time → `logged_publish_time = launcher_start + elapsed`.
4. Events are grouped into per-process "chains" requiring, within a chain, strictly increasing
   roster index and `|Δelapsed − seconds| ≤ 45 s`. Six chains were recovered and the count
   equals the six launcher attempt-starts; each chain's `n_done_before` (first event's
   `run N/96` − 1) is checked against the roster index it started at.

The mechanism that makes "closest to the file's mtime" *the same event* as "the last writer":
each background's scores live in exactly one file, published by an atomic `os.replace`, so
`os.replace` is last-writer-wins and the file's mtime is the last publisher's publish time.

Actual output (real numbers and quoted source text, not a paraphrase).
Full verbatim output: `docs/tasks/phase2-full-frame-placebo/PHASE2_A0_FULL_OUTPUT.txt` (208 lines).
Header and shape of the data:

```
  manifest.csv sha256 BEFORE: 98edd6fd9f229936f0790924078989b7e094bc4d16e2101b74b04f02ffda7f21
  manifest rows           : 158 (data rows)
  unique bg_id in manifest: 96
  bg_ids with >1 row      : 62
  rows per duplicated bg_id: [2] (expect [2])
  manifest.csv mtime      : 2026-09-29T12:38:44.932175
```

**Correction to the operational account, reported as found (AGENTS §5, never invent a number):**
the manifest has **exactly 158 data rows** for 96 unique `bg_id` (the "~158–159" estimate was
right), and the cause is **not two** scorer processes. `run.log` and the launcher lines show
**six** scorer processes were launched between 2026-09-28T15:40:31 and 2026-09-29T00:33:32, and
they overlapped in pairs: process 2 (16:02:15) ran concurrently with process 3 (20:21:36) and
process 4 (20:57:14); the final pair — process 5 (23:45:09, "Scored 55, skipped 41; wall
766.6m") and process 6 (00:33:32, "Scored 50, skipped 46; wall 725.1m") — both ran to
completion, and process 6 ran 7 minutes *behind* process 5 throughout, so it republished 50
backgrounds that process 5 had already published. Concurrency is also visible in the per-pass
pace: 534–660 ms/pass in the uncontended early hours, 1400–1460 ms/pass once the final pair was
both running (session 2a measured 530 ms/pass on an idle machine). Nothing about this changes
the deduplication; the extra processes are the reason the duplicate count is 62 rather than 50.

The six recovered chains, verbatim from STEP 1:

```
  chain  n_ev  n_done_before  first..last (runk)     elapsed span        launcher attempt start
     0     1              0  A222_C..A222_C (1..1)         5.8..5.8m  2026-09-28T15:40:31
     1    40              1  A222_D..AV_328 (2..41)       5.8..440.0m  2026-09-28T16:02:15
     2     2             28  AV_155..AV_175 (29..30)     13.6..27.4m  2026-09-28T20:21:36
     3    10             31  AV_204..AV_328 (32..41)    14.9..155.8m  2026-09-28T20:57:14
     4    55             41  AV_350..G_K401S (42..96)     9.2..766.6m  2026-09-28T23:45:09
     5    50             46  AV_462..G_K401S (47..96)    15.4..725.1m  2026-09-29T00:33:32
  all chain checks PASS (gap tolerance 45s, roster order, n_done_before)
```

Matching manifest rows to log events — 1-to-1, with one real edge case found and handled:

```
  rows matched 1-to-1                     : 158/158
  |manifest seconds - logged seconds|     : max 0.050s (log prints 1 dp, manifest stores 3 dp)
  rows resolved by logged `seconds`       : 156
  rows where the log's 1 dp print could not separate the two
    events, resolved by global append order: 2
      G_E54R: manifest seconds [806.073, 806.128] vs logged [806.1, 806.1] (spread 0.055s -- a timing measurement only; n_positions, n_rows and device are identical on both rows)
```

Reconstruction validated against the on-disk mtimes (STEP 3). Residual = `mtime(bg) −
logged_publish_time`; a small positive residual (seconds) means that chain's file is the one on
disk, a large one means another chain overwrote it:

```
  chain  n_ev   min[s]   max[s]   mean[s]   n_resid>60s (that chain lost the file)
     0     1      7.6      7.6      7.6                       0
     1    40      3.2    806.5    174.0                      12
     2     2     11.2     11.5     11.3                       0
     3    10      7.7     11.6      9.3                       0
     4    55      6.5    878.3    689.2                      50
     5    50      6.9     12.8      9.7                       0
```

Every chain's small residual is 3–13 s — that is the model-load time between the launcher's
spawn timestamp and the scorer's `t_run0` — and the reconstruction was not fitted to any mtime,
so this is an independent confirmation rather than a tautology. The two large-residual rows
(chain 1: 12 files; chain 4: 50 files) are exactly the files those chains published and a later
chain then overwrote.

**The selection itself (STEP 4), verbatim:**

```
  duplicated bg_ids                        : 62
  kept row  |logged - file mtime|          : max 12.8s  (mean 8.7s)
  dropped row |logged - file mtime|        : min 419.9s  (mean 720.0s)
  smallest margin between the two rows     : 413.0s  (over the 62 duplicated bg_ids)
  duplicated bg_ids whose two rows differ in n_positions / n_rows / device: 0

  CORROBORATION (reported, cannot change the rule's outcome):
    kept row == LAST `scored` line in run.log for the bg_id : 62/62
    kept row == LAST row in manifest.csv append order        : 62/62
```

Per-background table for all 96 backgrounds (bg_id, arm, duplicate count, kept row
`#man_row chain seconds`, its logged publish time, the file's mtime, `|d|`, the dropped row,
its `|d|`, and the margin) is in the full-output file, STEP 5, one line per background. Format
line and the first and last data rows, verbatim:

```
  bg_id     arm  dup  KEPT(man_row,chain,seconds)      logged_publish            file_mtime           |d|s  DROP(man_row,chain,sec)  runner-up|s|  margin|s
G_T549H   G      2  #79 ch5 812.932s             2026-09-29 03:21:26  2026-09-29 03:21:37   11.8  #78 ch4 825.959s               712.8     701.0
...
G_K401S   G      2  #157 ch5 544.674s            2026-09-29 12:38:38  2026-09-29 12:38:44    6.9  #156 ch4 943.469s              419.9     413.0
...
A222_C    S      1  #0 ch0 349.435s              2026-09-28 15:46:19  2026-09-28 15:46:26    7.6  -                               nan       nan
```

(`#N` is the 0-based row index in `manifest.csv`; the 34 single-row backgrounds are shown too,
with `-` in the DROP column because there was no second row to reject. The ellipses stand for
the omitted 94 lines, which are in the full-output file.)

Tally (STEP 5 tail, verbatim):

```
  duplicated bg_ids, by arm: {'G': 40, 'V': 22}
  duplicated bg_ids, by chain that KEPT the file: {2: 2, 3: 10, 5: 50}
  single-row bg_ids (no ambiguity arose): 34
```

Output written, and `manifest.csv` verified untouched (STEP 6 + A0 SUMMARY, verbatim):

```
  wrote data/processed/phase2/manifest_dedup.csv  (96 data rows, 96 unique bg_id)
  columns: ['bg_id', 'n_positions', 'n_rows', 'seconds', 'device', 'n_manifest_rows_for_bg_id', 'kept_event_chain', 'logged_publish_time', 'file_mtime', 'abs_diff_s']
  manifest_dedup.csv sha256: 0dbe78000c8b736c4c3b399fef09880268658019172d3b49724db5ae461750db
  manifest.csv sha256 AFTER : 98edd6fd9f229936f0790924078989b7e094bc4d16e2101b74b04f02ffda7f21
  manifest.csv unchanged    : True
  ...
  scores affected                           : NONE. The 96 bg_*.csv files were never
                                             duplicated in content; only the timing log was.
  coverage values changed by this dedup      : NO
```

`manifest_dedup.csv` carries the original five columns plus five audit columns
(`n_manifest_rows_for_bg_id`, `kept_event_chain`, `logged_publish_time`, `file_mtime`,
`abs_diff_s`) so the provenance of every kept row is in the file itself, not only in this log.

Verdict: **PASS.** 62 of 96 `bg_id` had duplicate rows (every one exactly 2 rows: 158 = 96 + 62).
For each, the kept row is the one whose reconstructed logged event time is closest to the
`bg_<bg_id>.csv` mtime on disk; the kept row is within **12.8 s** of that mtime (mean 8.7 s,
= the model-load offset) while the rejected row is at least **419.9 s** away, so the smallest
margin is **413.0 s** and no selection was anywhere near ambiguous. Two independent
corroborations agree on 62/62: the kept row is the last `scored` line in `run.log` for that
background, and the last row in `manifest.csv` append order. The 62 splits as
**{G: 40, V: 22}** (no Arm S background was ever re-scored — all 18 have a single row) and by
the process that kept the file: chain 2 → 2, chain 3 → 10, chain 5 → 50, chain 0/1/4 → 0.
**The deduplication changes no coverage value**: for all 62 duplicated backgrounds the two rows
are identical in `n_positions`, `n_rows` and `device`; they differ only in the `seconds` timing
measurement, so G-E (which reads `n_positions`) is numerically unaffected by which row is kept.
`manifest.csv` sha256 is byte-identical before and after; `manifest_dedup.csv` is a new file.

Files created/modified:
- `scripts/130_phase2_dedup_manifest.py` (created; selection rule pre-registered in the
  docstring before the first run)
- `data/processed/phase2/manifest_dedup.csv` (created; 96 rows;
  sha256 `0dbe78000c8b736c4c3b399fef09880268658019172d3b49724db5ae461750db`)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A0_FULL_OUTPUT.txt` (created; verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- `data/processed/phase2/manifest.csv` — **read only**; sha256 verified unchanged.
  No `bg_*.csv` touched. No protected file touched. No `git add`/`commit`/`push`.

Anything unexpected or worth flagging:
1. **A0 is not in `PHASE2_EXECUTION.md`.** It was added by Arnav's session-2b instruction. The
   execution doc is silent on manifest duplicates, so nothing in it is contradicted; flagged
   here per AGENTS §9 rather than silently resolved. The pre-registration is untouched: no arm,
   statistic, decision rule, constant or gate changes in this task.
2. **The operational account in the session brief is incomplete.** Two scorer processes is the
   headline, but `run.log` records six overlapping scorer processes (full table above). The
   last pair both ran to completion and duplicated 50 backgrounds; the earlier pairs duplicated
   12 more. Reporting the real number matters because it explains both the 62 duplicates and the
   roughly 2.5× slowdown in per-pass time late in the run.
3. **`G_E54R` is the one background the log's 1-decimal print cannot separate**: both of its
   events printed `806.1s` while the manifest holds 806.073 and 806.128. Handled by the
   pre-registered fallback (global append order) and disclosed above. It changes which of two
   0.055-s-apart *timing* measurements is carried forward; `n_positions`, `n_rows` and `device`
   are identical, so no gate, statistic or coverage number is affected.
4. **Script 130 had five failed runs of its own before the clean one, all before any output was
   accepted and all disclosed (AGENTS §6):** (a) `assign` referenced before initialisation; (b) a
   Python sort tie on `dict` objects (`TypeError`); (c) a `KeyError` from an `id()` mismatch —
   `build_chains` was copying each event dict, so the `id()` used to look up the owning chain
   was not the object's; fixed by keeping the same object. (d) a `ValueError` from taking
   `max()` of the rejected candidates for a single-row background. (e) **A real methodological
   bug worth recording:** the first working version matched manifest rows to log events using the
   manifest's 3-dp `seconds` against the log's 1-dp value, which "broke" the `G_E54R` tie by
   0.001 s — an artefact of the print rounding, not information. It was corrected to match on
   the value the log actually printed, so a genuine tie falls through to the append-order rule.
   No rule, threshold, seed or selection was changed to suit a result; the selection rule was
   fixed before any run and is unchanged. Only presentation code (margin sign, NaN handling,
   table columns) changed afterwards, and it cannot affect which row is kept.
5. **`manifest_dedup.csv` is deterministic**: two consecutive clean runs produced the identical
   sha256 `0dbe7800…50db`.
6. No `torch`/`esm` import in script 130 (execution doc: model scoring only in 124/G1); nothing
   was downloaded; the real score directory was only read.

---

## [A1] — Completion, coverage (frozen G-E), and script integrity since 2a
Status: PASS (with one flagged gap: no 2a hash baseline exists for 123/125)
Time started / finished: 2026-09-29, immediately after A0
What I did:
Ran A1 as an **inline heredoc, no new script number** — the execution doc allocates numbers
123/124/125 to R1/G2/G3 and names none for A1 (same decision and same disclosure as session
2a's R2/G1, PHASE2_LOG troubleshooting rules 4/5). Verbatim output saved to
`PHASE2_A1_FULL_OUTPUT.txt`.

- **File completeness (A1.1):** rather than reimplement the check, I imported script 124's *own*
  `file_is_complete()` and `expected_positions()` by `importlib` and called them on all 96
  files — i.e. the same strengthened criteria the scorer's resume/skip logic used (exact row
  count, exact position set, single `bg_id`, no duplicate `(position, mut_aa)` pairs; a `.tmp`
  never counts). Frame rebuilt from `task32_analysis_table.csv` exactly as scripts 122/123/124 do.
- **Gate G-E (A1.2):** the frozen threshold from `PHASE2_PREREG.md` §7, with the denominator read
  literally as *the frame's 654 positions* (not 653, and not the 120-position cached grid that
  G3's validation mode used).
- **Manifest cross-check (A1.3):** `manifest_dedup.csv` (A0's output, per the session-2b
  instruction) joined against the score files actually on disk.
- **Script integrity (A1.4):** sha256 + mtime of 123/124/125 (+130 and the launcher), compared
  against the first Phase 2 score file's mtime; `git status`; content spot-checks of the frozen
  contracts; and a check that `torch`/`esm` appear only in 124.

Actual output (real numbers and quoted source text, not a paraphrase):

```
  roster bg_ids                 : 96 (unique 96)
  frame (task32 usable rows)    : 654 positions (expect 654); 654*19=12426, 653*19=12407
  usable frame rows             : 10757 (expect 10757)

A1.1
  bg_*.csv files in phase2/     : 96 (expect 96)
  roster bg_ids with no file    : []
  files not in the roster       : []
  other files in phase2/        : []
  ALL complete by script 124's own criteria : 96/96
  files whose row count != expected          : 0
  files with a duplicate (position, mut_aa)  : 0
  distinct column sets                       : ['bg_id,position,mut_aa,score']

  rows/positions by arm (expect S: 654 pos / 12426 rows; V,G: 653 / 12407):
    n_expect_pos      n_rows        n_pos
             min  max    min  max   min  max
arm
G            653  653  12407  12407   653  653
S            654  654  12426  12426   654  654
V            653  653  12407  12407   653  653

A1.2
  frozen threshold 0.95 x 654 = 621.3
  minimum n_positions over the 96 backgrounds : 653 (background AV_5, arm V)
  maximum n_positions                          : 654
  backgrounds below the threshold              : 0
  min coverage as a fraction of the frame      : 0.998471 (653/654)
  (Arm S scores 654/654 = 100.0%; Arms V and G score 653/654 = 0.998471 because
   PIN-5/G-C exclude the background's own position, which is a REQUIRED
   exclusion, not missing coverage.)

  G-E PASS: min n_positions 653 >= 621.3 -> True

A1.3
  manifest.csv      : 158 data rows / 96 unique bg_id
  manifest_dedup.csv: 96 data rows / 96 unique bg_id
  dedup vs roster merge: {'both': 96, 'left_only': 0, 'right_only': 0} (expect both=96)
  rows where dedup n_positions != positions actually in the file : 0
  rows where dedup n_rows      != rows actually in the file       : 0
  dedup device column values  : ['mps'] (expect ['mps'])
```

Script integrity (A1.4), verbatim — **including the gap**:

```
  *** IMPORTANT: session 2a's SUMMARY (2a) records NO sha256 for scripts
      123/124/125.  It records the roster sha256 and the prereg sha256 only.
      So the instructed comparison -- 'against the checksums logged in 2a' --
      HAS NO BASELINE TO COMPARE AGAINST.  Reported, not papered over.
      The available evidence is recorded below instead:

  earliest Phase 2 score file mtime : 2026-09-28T15:46:26.616961
  latest   Phase 2 score file mtime : 2026-09-29T12:38:44.931501

  file                                   mtime                  sha256                                                          hours before first score
  scripts/123_phase2_arm_roster.py       2026-09-28T01:12:47.725483  f16655ad494ea398e67024dddb9382d943d940a4b9955083bbbd92f24a5e9aba     14.56
  scripts/124_phase2_score_backgrounds.py 2026-09-28T01:34:06.995622  8e2175d416d59a5b474f62ec27b5a884b3b44fffe6eabe79aa3f6e9c119d9408     14.21
  scripts/125_phase2_analysis.py         2026-09-28T01:55:36.586725  6c5b82217234b8f4339d7cfebb9fa8dd234592586a57767d17702b9cfe3bf37d     13.85
  scripts/130_phase2_dedup_manifest.py   2026-09-29T17:25:04.427857  0e73d1343de31731dc68aa93bf54216611864c6435c21763b58db3e7c9c19857    -25.64
  scripts/launch_phase2.sh               2026-09-28T02:07:47.534161  69b4053676cfc70763cf09e0cd06a79ea928e48c398d7a79359bfec2a9f03b34     13.64

  => all three Phase 2 scripts (123/124/125) and the launcher have mtimes
     13.6-14.6 h BEFORE the first Phase 2 score existed, i.e. none was
     written after any score -- which is the rule that actually protects
     the result (execution doc rule 7).  mtime is weaker than a hash: a
     file could be edited and its mtime restored.  No evidence of that is
     present, and it is not claimed to be excluded.

  the ONE checksum session 2a did record, re-verified now:
    data/processed/phase2_arm_roster.csv
      now     : 9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b
      in 2a   : 9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b
      MATCH   : True

  git: scripts 123/124/125 and launch_phase2.sh are UNTRACKED (`??`), so
  `git status`/`git diff` give no committed baseline either.  Their checksums
  above are recorded here as the baseline for any future session.

  content spot-checks that the frozen contracts are still in place:
    OK   124 output contract 'bg_id, position, mut_aa, score'
    OK   124 still does atomic os.replace publish
    OK   124 still imports get_position_logprobs (PIN-4)
    OK   124 still skips its own position (PIN-5)
    OK   125 has both --mode phase2 and --mode cached-ae
    OK   125 pre-registered docstring still present
    OK   125 quotes frozen G-A / G-C / G-D / G-E
    OK   125 uses the NAIVE spearmanr loop (PIN-9 acceleration NOT used)

  torch/esm must appear ONLY in 124 (execution doc: model scoring only in 124/G1):
    scripts/123_phase2_arm_roster.py: none
    scripts/125_phase2_analysis.py: none
    scripts/130_phase2_dedup_manifest.py: none
    scripts/124_phase2_score_backgrounds.py: ['import esm', 'esm.pretrained'] (expected)

==========================================================================
A1 VERDICT: file completeness 96/96 PASS | G-E PASS | manifest_dedup vs files agree PASS |
          script integrity: NO 2a HASH BASELINE EXISTS (flagged); mtime and
          content evidence all consistent with 123/124/125 being unmodified.
==========================================================================
```

Verdict: **PASS**, with one gap reported rather than hidden.
- **Completion:** 96/96 `bg_*.csv` files exist, one per roster `bg_id`, no extras, no missing, and
  **all 96 pass script 124's own completeness criteria**. Every file has exactly the expected row
  count (Arm S 12,426 = 654×19; Arms V and G 12,407 = 653×19), the expected position set, and zero
  duplicate `(position, mut_aa)` pairs. Column set is exactly `bg_id,position,mut_aa,score` in
  every file. This independently confirms the user's direct-on-disk verification.
- **G-E: PASS.** Frozen threshold 0.95 × 654 = **621.3**; the **minimum** over the 96 backgrounds
  is **653** (`AV_5`, Arm V); 0 backgrounds below threshold. Minimum coverage = **0.998471
  (653/654)**. Arm S is 654/654 = 100%. The 653/654 for Arms V and G is the *required* PIN-5 /
  G-C exclusion of each background's own position, not missing coverage — the distinction is
  stated here so G-E is not later read as "one position short".
- **Manifest:** `manifest_dedup.csv` has 96 rows for 96 backgrounds, joins 96/96 to the roster,
  and agrees with the score files on disk on `n_positions` and `n_rows` in **0 disagreements**;
  device is `mps` throughout.
- **Script integrity: no evidence of change, but the instructed comparison is impossible.**
  Session 2a's SUMMARY recorded no checksums for 123/124/125, so there is no baseline; this is
  flagged rather than papered over, and the current hashes are recorded as the baseline going
  forward. The available evidence is consistent with all three being untouched: every one has an
  mtime **13.6–14.6 hours before the first Phase 2 score existed** (earliest score
  `2026-09-28T15:46:26`), all frozen contracts are still present in the source, and `torch`/`esm`
  appear only in 124 as the execution doc requires. The one checksum 2a *did* record — the roster
  — re-verifies **exactly** (`9b31721a…9445b`), which is what actually pins the arm definitions
  the analysis depends on. **mtime is weaker than a hash and I do not claim tampering is excluded.**

Files created/modified:
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A1_FULL_OUTPUT.txt` (created; verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- Nothing else. No `bg_*.csv`, no `manifest*.csv`, no script, no protected file modified. No
  `git add`/`commit`/`push`.

Anything unexpected or worth flagging:
1. **The 2a SUMMARY has no hash baseline for 123/124/125** (flagged above). This is a logging gap
   in session 2a, not a finding about the scripts. Recorded checksums for 123, 124, 125, 130 and
   `launch_phase2.sh` appear in the A1.4 table above; a future session can now compare against
   them. Recommend future gated sessions hash their scripts in the session that creates them.
2. **All of 123/124/125 and the launcher are untracked in git** (`??` in `git status`), so there is
   no committed copy to diff against either. Not a problem for this run, but it means a session
   2b script edit would leave no VCS trace — another reason to treat them as frozen.
3. `frame` and `usable rows` re-derived in A1 agree with 2a exactly (654 / 10,757), so the two
   sessions are working from the same frame definition (AGENTS §5: reconcile n across scripts).
4. A1 imported script 124 by file path rather than duplicating its completeness logic, so the
   check that ran is provably the same check the scorer's resume logic ran. This import does not
   execute `main()` and does not touch the model.

---

## [A3] — Extended reproduction check, all Arm S + Arm V on the 120 AE grid (descriptive)
Status: PASS (descriptive; no decision rests on it)
Time started / finished: 2026-09-29, while the A2 full run executed in the background
What I did:
Ran A3 as an inline heredoc, no new script number (execution doc A3 allocates none; same
disclosure as A1 and session 2a's R2/G1). **No model was loaded** — the "freshly scored values"
are the Phase 2 run's own `data/processed/phase2/bg_<bg_id>.csv` files, and the comparison is a
pure CSV join on `(position, mut_aa)`. Fresh column `score` and cached column `score_bg` were
read from disk and from script 82's own `RAW_CACHE` definition, not guessed. All **18 Arm S + 38
Arm V = 56** backgrounds were compared, on all 120 AE grid positions, 2,280 cells each.

Two comparisons are reported because they disagree, and the disagreement is the finding:
1. **Parsed** — both sides through `pandas.read_csv`, i.e. what every downstream analysis sees.
2. **Stored-text** — the literal decimal strings converted to float with exact Python parsing.
   This is the stricter test.

Actual output (real numbers and quoted source text, not a paraphrase).
Full verbatim output: `docs/tasks/phase2-full-frame-placebo/PHASE2_A3_FULL_OUTPUT.txt`.
Data shape and coverage, verbatim:

```
  cache task82_ae_raw.csv : 129960 rows, 57 bg_ids, 120 positions
  AE grid                 : 120 positions (script 82's 120-position grid)
  cached bg_id set == Arm S + Arm V + A222_V : True
  Arm S + Arm V backgrounds compared         : 56

  cached AE cells per background        : [2280] (expect 2280 = 120x19)
  fresh cells on the grid               : [2280]
  cached cells with NO fresh score      : 0 (backgrounds affected: 0)
  backgrounds whose OWN position is in the AE grid: []
  NaNs among compared cells             : 0
  header line, cached : bg_id,position,mut_aa,score_bg
  header line, fresh  : bg_id,position,mut_aa,score
```

The two comparisons, verbatim:

```
  (1) PARSED COMPARISON  (pandas.read_csv on both sides -- what every
      downstream analysis in this project sees):
      backgrounds with max|d| < 1e-6  : 56 / 56
      backgrounds with max|d| >= 1e-6 : 0 / 56
      LARGEST max|d| over all 56      : 0.000000e+00
      cells compared                  : 127680 (= 56 x 2280)
      cells with |d| exactly 0.0      : 127680 / 127680

  (2) STORED-TEXT COMPARISON  (literal decimal strings -> exact Python
      float(); the stricter test.  Non-zero ONLY where the two files were
      serialised with a different number of significant digits:
      cells identical as text         : 110290 / 127680
      cells differing as text         : 17390 / 127680
      LARGEST |d| over all cells     : 1.776357e-15
      by arm: S = 1.776357e-15  V = 1.776357e-15
      backgrounds with max|d|_text < 1e-6 : 56 / 56
      backgrounds with max|d|_text == 0.0 : 11 / 56  (['AV_461', 'AV_462', 'AV_511', 'AV_522', 'AV_524', 'AV_551', 'AV_558', 'AV_587', 'AV_589', 'AV_650', 'AV_655'])
```

The cause, established rather than assumed, with the example cell that exposed it:

```
    cell (bg=A222_C, position=3, mut_aa=F)
      cached string : 0.1476681232452392
      fresh  string : 0.14766812324523926
      cached float  : 0.1476681232452392
      fresh  float  : 0.14766812324523926
      difference    : 5.551e-17 (3.8e-16 relative)
    CAUSE (verified, not assumed): task82_ae_raw.csv mtime is 2026-09-24T17:29:14.685769,
       five days BEFORE the Phase 2 run, and BOTH writers use a plain `to_csv`
       with no float_format (script 82 line 492, script 124 line 254).  The
       difference is therefore the pandas serialiser, not a rounding step in
       either script: the cache was written under an older pandas, and the current
       pandas 3.0.5 emits the shortest round-tripping repr (17 digits for these
       values), which is exactly what the fresh files contain.
    The text difference is a PER-VALUE property, not a per-file or per-process one:
       a cell whose float64 needs <=16 significant digits is byte-identical in both
       files, and only cells needing 17 digits differ.  That is why 11 backgrounds
       show 0 textual differences and 45 show ~380 of 2280.  (An earlier draft of
       this note attributed the split to the scorer chains; that was wrong and is
       withdrawn here -- the numbers above supersede it.)
```

Verdict: **PASS (descriptive).** **All 56 of 56 Arm S + Arm V backgrounds reproduce the cached
`task82_ae_raw.csv` values to better than 1e-6** — in the parsed comparison the largest
`max |diff|` over all 127,680 cells is **exactly 0.000000e+00**, i.e. every cell is bit-identical
as any analysis in this project reads it. Under the stricter stored-text test the largest
discrepancy anywhere is **1.776357e-15** (one ulp of float64), 17,390 of 127,680 cells differ
*as text*, and the cause is verified to be the pandas serialiser (16-significant-digit cache
written 2026-09-24 vs shortest-round-trip repr under pandas 3.0.5 today) — not a difference in
the scores. Every cached cell has a fresh counterpart (**0** missing), no background's own
position lies inside the AE grid (so PIN-5/G-C cost nothing here), and there are no NaNs. This
extends the frozen G-B check from session 2a's three backgrounds to all 56 cached backgrounds,
and it is ~9 orders of magnitude inside the 1e-6 gate. **No decision rests on any of it.**

Files created/modified:
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A3_FULL_OUTPUT.txt` (created; verbatim output)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- Read-only over `data/processed/phase2/bg_*.csv` and `task82_ae_raw.csv`. Nothing else modified.

Anything unexpected or worth flagging:
1. **A3's first two drafts contained claims I had not verified, and both were corrected before
   this entry was written** (AGENTS §5, §6). (a) The first draft reported a read-back string
   comparison that said 17,390 cells differed while simultaneously reporting a parsed difference
   of exactly 0 everywhere — a self-contradiction I resolved rather than reported. (b) The
   corrected draft then printed a note attributing the text differences to the A0 scorer chains
   ("the 11 zero-difference backgrounds are the ones scored early"), which I checked and found
   **false** — those 11 are the *late* ones (`AV_461` … `AV_655`). The real cause is the pandas
   serialiser plus a per-value significant-digit threshold, and it is stated above. Neither
   withdrawn claim affects any number in this entry; the note is corrected in the script and in
   the full-output file, and it is recorded here so nobody later mistakes it for a finding.
2. The 1.78e-15 stored-text figure is **one ulp of float64**, and the relative difference on the
   example cell is 3.8e-16. It is a serialisation artefact, not a numerical disagreement; the
   parsed values are identical. Stating this precisely matters because "17,390 cells differ" on
   its own would overstate the discrepancy by nine orders of magnitude.
3. A3 ran concurrently with the A2 full bootstrap (a pure-CSV job, no model, ~1 min of CPU), so
   it did not materially perturb A2's timing. Flagged for completeness; A2's own runtime is
   reported in the A2 entry.

---

## [A2] — Full pre-registered analysis, `--mode phase2`, N_BOOT=300 smoke then N_BOOT=10000 SEED=0 detached
Status: PASS (all four frozen gates G-A, G-C, G-D, G-E pass; nothing loosened, no retry)
Time started / finished: smoke 2026-09-29 ~17:22 (151.3 s); full run launched 17:26:44,
finished 19:13:44, **Elapsed 5839.4 s = 97.3 min**, detached per frozen §8
What I did:
Ran `scripts/125_phase2_analysis.py --mode phase2` unmodified, exactly as the execution doc A2
prescribes.

1. **Smoke first** (AGENTS §1): `N_BOOT=300 N_PERM=300 SEED=0`, foreground, **exit 0**, 151.3 s.
   Verbatim output: `PHASE2_A2_SMOKE_OUTPUT.txt` (347 lines).
2. **Runtime extrapolated from that smoke run, not inherited from any other script** (AGENTS §1
   names exactly this failure mode): the smoke spent 147.7 s in its four bootstrap passes at 300
   draws, so `N_BOOT=10000` was projected at ~4,923 s ≈ **84 min** — past the 55–65 min
   foreground limit — so the full run was **detached**:
   `N_BOOT=10000 N_PERM=10000 SEED=0 nohup venv/bin/python3 scripts/125_phase2_analysis.py
   --mode phase2 > data/processed/phase2/analysis_run.log 2>&1 &`
   Monitored with `tail -n` only, never `tail -f`.
3. **Full output saved verbatim** to `PHASE2_A2_FULL_OUTPUT.txt` (347 lines) and left in place at
   `data/processed/phase2/analysis_run.log`.
4. The smoke and the full run agree **exactly** on every deterministic quantity (they must — none
   of them depends on N_BOOT): `p_spec(full) = 0.025316456`, `p_spec(H) = 0.050632911`,
   `D_site = -0.055525559`, `T = -0.347781218`. A real cross-check that the mode and the seed were
   reproduced across the two invocations.

Actual output (real numbers and quoted source text, not a paraphrase).

**Frozen gates, verbatim from the full run:**

```
[G-A] A222V's full-frame rho vs the frozen anchor
  rho = -0.08811806424891734; target -0.088118 |diff| = 6.425e-08 (gate < 1e-6)
  G-A PASS
...
  roster 96 backgrounds; bg_*.csv files found = 96 (all 96 expected before session 2b)
  rows outside own position without scores (coverage gaps) = 0 across all backgrounds (none)
  arms: S=18 V=38 G=40 -> N (null set) = 78; A222V is neither S nor N (frozen section 3)
  G-C PASS: 0 rows with target position == background position in any rho_b input (own-position rows pre-dropped: 1267)
...
  G-D: identity draw (every cluster once) vs point rho: max|diff| = 0.000e+00 (gate < 1e-12)
  G-D PASS
...
[G-E] background position coverage
  min positions covered by any background = 653 (denominator 654; gate >= 621.3)
  G-E PASS
```

**Bootstrap passes actually executed (all four, all 10,000 draws, zero NaN draws dropped):**

```
    [SEED+0 full frame] 10000 draws x 96+A222V rho in 2343.8s (234.4 ms/draw); draws with any NaN = 0
    [SEED+1 H]          10000 draws x 96+A222V rho in 976.8s (97.7 ms/draw);  draws with any NaN = 0
    [SEED+3 secondary full frame] 10000 draws x 96+A222V rho in 1504.2s (150.4 ms/draw); draws with any NaN = 0
    [SEED+4 secondary H] 10000 draws x 96+A222V rho in 1010.0s (101.0 ms/draw);  draws with any NaN = 0
```

**Script 125's own final summary block, verbatim:**

```
  mode = phase2; G-A PASS; G-C PASS; G-D PASS; G-E PASS; input gates PASS
  p_spec(full) = 0.025316456; p_spec(H) = 0.050632911
  D_site = -0.055525559, CI [-0.079318507, -0.033178263], perm p = 0.000100
  T = -0.347781218, CI [-0.694530444, +0.137306502], LOO [-0.436274510, -0.225490196], min detectable |T| = 0.616615508 -> NOT RESOLVED
Elapsed 5839.4s
```

Verdict: **PASS.** All four frozen gates pass at their prescribed thresholds, in both the smoke
and the full run, with no threshold loosened, no input substituted and no retry:
- **G-A PASS** — A222V's full-frame ρ = `−0.08811806424891734` vs the frozen anchor `−0.088118`,
  |diff| = **6.425e-08 < 1e-6**. Identical to session 2a's R2 value to every digit.
- **G-C PASS** — **0** rows with target position == background position in any ρ_b input;
  1,267 own-position rows were pre-dropped.
- **G-D PASS** — bootstrap identity draw (every cluster exactly once) vs the point estimate:
  max|diff| = **0.000e+00 < 1e-12**.
- **G-E PASS** — minimum coverage **653** of 654 positions, threshold 621.3.
- Input gates PASS (own_e_b cross-check 0/10,757 mismatches; PIN-8 region cross-check 0/10,757;
  H = 455 positions / 7,526 rows; zero coverage gaps; 96/96 files found).
- The primary result is **`p_spec(full) = 0.025316456` (1 of 78 null placebos at or below A222V)
  and `p_spec(H) = 0.050632911` (3 of 78)**, with `D_site = −0.055525559` (CI
  `[−0.079318507, −0.033178263]`, label-permutation p = 0.000100) and `T = −0.347781218`
  (CI `[−0.694530444, +0.137306502]` → **NOT RESOLVED**). A4 reports and interprets these under
  the frozen wording rule; the numbers are the pre-registered result, unlike the cached-ae numbers
  session 2a recorded.

Files created/modified:
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A2_SMOKE_OUTPUT.txt` (created; smoke verbatim)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A2_FULL_OUTPUT.txt` (created; full-run verbatim)
- `data/processed/phase2/analysis_run.log` (created by the detached run; the same content)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- **No script was modified.** `scripts/125_phase2_analysis.py` sha256 is still
  `6c5b82217234b8f4339d7cfebb9fa8dd234592586a57767d17702b9cfe3bf37d`, unchanged since A1 measured
  it, i.e. the pre-registered docstring version is exactly what produced these numbers. No
  protected file touched. No `git add`/`commit`/`push`.

Anything unexpected or worth flagging:
1. **The runtime projection from the smoke (≈84 min) under-predicted the real run (97.3 min) by
   about 14%.** The per-draw cost was not constant: the first 2,000 full-frame draws ran at
   146 ms/draw, the 2,000–4,000 block at ~580 ms/draw, and the last 6,000 back at ~148 ms/draw. The
   slow block coincides with A3's pure-CSV job and my polling, i.e. with my own session activity,
   not with anything in the analysis. Recorded because AGENTS §1 warns about exactly this, and
   because a future session should expect ~1.5–2 h for this pass on this machine rather than 84
   min. No number in the result depends on the timing.
2. **I did not capture the detached run's exit code.** I launched with `nohup … &` and polled, so
   no `$?` was available afterwards. What *is* established: the process ran to completion, printed
   script 125's full `SCRIPT 125 SUMMARY` block and the final `Elapsed 5839.4s` line, and a
   `grep` over the whole log for `gate fail|error|traceback|assert|FAIL` returns **nothing**. Since
   script 125 calls `sys.exit(1)` immediately on any gate failure and its gates are all printed as
   PASS, a nonzero exit would have aborted the run before the summary block. I state the exit code
   as *not recorded* rather than asserting 0. This is a process gap in how I launched the job, not
   a result problem; the fix is to append `; echo $? > analysis_exit` inside the detached command.
3. **stdout is block-buffered when redirected**, so progress lines arrived in bursts rather than
   live. Monitoring was by `tail -n` on a lagging file plus `ps`. The launch could use
   `python3 -u` to make it live next time.
4. `p_spec` is bounded below by `1/(1+|N|) = 1/79 = 0.012658`, so the smallest attainable
   p_spec(full) is 0.0253 with 1 of 78 at or below. The value is an empirical rank count, not a
   tail model, and it cannot be made smaller by collecting more data — only by a larger null set.
5. The smoke run's `D_site` permutation p (0.003322) and the full run's (0.000100) differ, as
   expected: 300 vs 10,000 shuffles, and the full run hit the floor `(1+0)/(1+10000)`. Reported so
   the smoke number is never mistaken for the pre-registered one.

---

## [A4] — Verdict, verbatim, under the frozen section-5 wording rule
Status: PASS (task complete; the outcome is reported exactly as the frozen rule yields it)
Time started / finished: 2026-09-29, after A2
What I did:
Read the A2 full-run output and re-derived the two `p_spec` counts independently from the
per-background ρ tables printed in that output (parsing the 96 full-frame and 96 H ρ values,
filtering to N = Arm V ∪ Arm G exactly as frozen §3 defines it), then applied frozen §5 literally.
The independent re-derivation is saved verbatim in `PHASE2_A4_CHECKS.txt`. It confirms both
script-125 values to 1e-9 and identifies *which* backgrounds drive each count.

Actual output (real numbers and quoted source text, not a paraphrase).

**1. THE OUTCOME WORD, exactly as frozen §5 yields it:**

```
  GENERIC  iff p_spec(full) > 0.10                      -> False
  BEATS    iff p_spec(full)<=0.05 AND p_spec(H)<=0.10     -> True
  => OUTCOME WORD: A222V BEATS NON-SITE BACKGROUNDS
```

**2. The two p_spec values and the counts behind them** (script output and my independent
re-derivation, which agree):

```
  p_spec(FULL FRAME): threshold = A222V's rho on the same rows = -0.088118064
    #{b in N : rho_b <= rho_A222V} = 1 of |N| = 78
    p_spec(full) = (1 + 1) / (1 + 78) = 0.025316456
  p_spec(HELD-OUT H): threshold = A222V's rho on H rows = -0.090021683
    #{b in N : rho_b <= rho_A222V} = 3 of |N| = 78
    p_spec(H) = (1 + 3) / (1 + 78) = 0.050632911
```

The **1 of 78** on the full frame is `G_P254F` (ρ = −0.096243863, i.e. 0.008125799 below
A222V). The **3 of 78** on H are `G_P254F` (−0.101954441), `AV_220` (−0.094480281) and
`AV_195` (−0.093420822). A222V's signed rank within N ∪ {A222V} is **2 of 79** on the full frame
and **4 of 79** on H.

**3. Placebo distributions per arm, and where A222V sits** (frozen §6 tables, verbatim):

```
  primary, full frame:
    arm S: n=18 mean=-0.065159334 median=-0.064728255 range=[-0.093529969, -0.045641128]
    arm V: n=38 mean=-0.019532174 median=-0.023411207 range=[-0.084598081, +0.047573205]
    arm G: n=40 mean=-0.000230296 median=+0.010076945 range=[-0.096243863, +0.063116028]
    null set N (V u G): n=78 mean=-0.009633775 median=-0.002701665 range=[-0.096243863, +0.063116028]
    A222V rho = -0.088118064; signed rank within N u {A222V} = 2/79 (rank 1 = most negative; reported, not tested)
  primary, held-out H:
    arm S: n=18 mean=-0.070181243 median=-0.068991235 range=[-0.090964259, -0.048929841]
    arm V: n=38 mean=-0.022540725 median=-0.022628334 range=[-0.094480281, +0.040588603]
    arm G: n=40 mean=+0.000869556 median=+0.009295575 range=[-0.101954441, +0.068247435]
    null set N (V u G): n=78 mean=-0.010535453 median=-0.006633288 range=[-0.101954441, +0.068247435]
    A222V rho = -0.090021683; signed rank within N u {A222V} = 4/79 (rank 1 = most negative; reported, not tested)
```

**4. D_site (frozen §5, "reported irrespective of the outcome above"), verbatim:**

```
  mean rho_b(S, n=18) = -0.065159334; mean rho_b(N, n=78) = -0.009633775
  D_site = mean(S) - mean(N) = -0.055525559
  position-cluster bootstrap 95% CI (SEED+0, 10000 draws) = [-0.079318507, -0.033178263] (valid 10000)
  label permutation (10000 shuffles over 96 arm backgrounds, n(S)=18 kept fixed, TWO-SIDED on |D| per script 121's precedent -- sidedness not stated in frozen section 5, logged as an ambiguity resolution, SEED+2): p = (1 + 0) / (1 + 10000) = 0.000100
  Interpretation (frozen): D_site < 0 means a shared site tracks A222V's e.b beyond arbitrary backgrounds; that is compatible with a real site-specific effect and is not evidence of substitution-specificity.
```

**5. Within-site Grantham gradient T (frozen §5), verbatim — note the required wording:**

```
  d_b = Grantham(X, V) via scripts.lib.features.grantham (P1's Grantham gate source); 18 finite values, range [21.5, 191.2]
  T = Spearman(rho_b, d_b) over Arm S (n=18) = -0.347781218
  bootstrap T 95% CI (SEED+0) = [-0.694530444, +0.137306502] (valid 10000/10000)
  bootstrap SE(T) = 0.220219824 -> minimum detectable |T| approx 2.8 x SE = 0.616615508
  leave-one-out range = [-0.436274510, -0.225490196] (T > 0 in 0/18)
  T RULE: CI lower > 0 (False) AND T > 0 in all leave-one-out fits (False); CI upper < 0 (False) -> NOT RESOLVED
  REQUIRED WORDING for NOT RESOLVED: "n = 18 cannot resolve this," never "flat" / "the gradient is flat".
```

**6. Region-demeaned secondary (frozen §6, NON-DECISION), verbatim:**

```
    secondary p_spec(full frame) = (1 + 5) / (1 + 78) = 0.075949367  (threshold A222V resid rho = -0.053781437)
    secondary D_site = -0.033048195, CI [-0.055707372, -0.011201292] (valid 10000)
    A222V rho = -0.053781437; signed rank within N u {A222V} = 6/79
    secondary p_spec(H) = (1 + 5) / (1 + 78) = 0.075949367  (threshold A222V resid rho = -0.052700937)
    secondary D_site = -0.031510979, CI [-0.056732947, -0.006420822] (valid 10000)
    A222V rho = -0.052700937; signed rank within N u {A222V} = 6/79
  secondary outcome word WOULD BE (NON-DECISION; the pre-registered decision uses primary p_spec only): INDETERMINATE
```

**7. Borderline check, verbatim from the independent re-derivation:**

```
BORDERLINE CHECK (execution doc A4: say so if a p_spec is within 0.01 of a threshold).
  p_spec(full) = 0.025316456 vs 0.05: |diff| = 0.024683544  within 0.01? False
  p_spec(full) = 0.025316456 vs 0.1: |diff| = 0.074683544  within 0.01? False
  p_spec(H) = 0.050632911 vs 0.1: |diff| = 0.049367089  within 0.01? False
  p_spec floor 1/(1+|N|) = 1/79 = 0.012658228; p_spec(full) sits 0.012658228 above it,
  p_spec(H) 0.037974684 above it.  Counts cannot go below 1/(1+|N|) at any N_BOOT.
```

Verdict:
**The outcome word is `A222V BEATS NON-SITE BACKGROUNDS`, with `p_spec(full) = 0.025316456`
(1 of 78 null placebos at or below A222V's ρ) and `p_spec(H) = 0.050632911` (3 of 78).**

**THE FROZEN WORDING RULE, restated exactly as the pre-registration states it:** only
**"A222V BEATS NON-SITE BACKGROUNDS"** may be written up as supporting **background-specificity**
of the anchor; **GENERIC and INDETERMINATE must be reported with equal prominence in every
write-up.** The rule that was applied is verbatim from frozen §5: GENERIC iff `p_spec(full) >
0.10`; "A222V BEATS NON-SITE BACKGROUNDS" iff `p_spec(full) ≤ 0.05` **and** `p_spec(H) ≤ 0.10`;
INDETERMINATE otherwise. The data give the second outcome. No threshold was loosened, no
alternative metric or subset was tried, nothing was rounded, and no arm, statistic, decision rule
or constant changed.

**Not borderline.** Neither `p_spec` is within 0.01 of any threshold in the frozen rule: the
closest approach is `p_spec(full)` at 0.0247 from the 0.05 boundary. The result is not being
called from the edge of the rule.

**What this does and does not license.** It licenses one statement: A222V's ESM-2
background-shift anchor is less extreme than all but one of 78 arbitrary single-substitution
backgrounds on the full frame, and less extreme than three of 78 on the held-out set H. That is
background-specificity of the anchor in the sense the pre-registration defines. It is **not** a
claim about substitution-specificity, and the pre-registration says so itself.

**D_site = −0.055525559, 95% CI [−0.079318507, −0.033178263] (excludes 0), label-permutation
p = 0.000100.** Per the frozen text, D_site < 0 means a shared *site* tracks A222V's e.b beyond
arbitrary backgrounds, which is compatible with a real site-specific effect and **is not evidence
of substitution-specificity**.

**The Grantham gradient T = −0.347781218, 95% CI [−0.694530444, +0.137306502], leave-one-out
range [−0.436274510, −0.225490196] (T > 0 in 0/18), minimum detectable |T| = 0.616615508
(2.8 × bootstrap SE 0.220219824), outcome word `NOT RESOLVED`.** The CI crosses 0, so it is
neither SUPPORTED nor REVERSED. In the words the pre-registration requires: **"n = 18 cannot
resolve this"** — the observed |T| of 0.348 is *below* the minimum this design could have
detected (0.617), so this is an absence of resolution, and it is **not** "flat". The point
estimate is negative in all 18 leave-one-out fits, which is a fact about the point estimates
only and does not change `NOT RESOLVED`; the frozen rule is not met in either direction and no
weight is placed on it.

**The region-demeaned secondary is non-decision, and it points the same way as the primary
result but more weakly:** `p_spec = 0.075949367` in both the full frame and H, A222V's signed
rank falls from 2/79 (full) and 4/79 (H) to **6/79** in both, and the outcome word it *would*
produce is **`INDETERMINATE`**. Its `D_site` remains negative with a CI excluding 0
(−0.033048195, CI [−0.055707372, −0.011201292] full frame; −0.031510979, CI [−0.056732947,
−0.006420822] on H). This is reported with the same prominence as the primary: the region-demeaned
view does not reach the pre-registered 0.05 on the full frame.

**A limitation that bounds all of the above, printed by the script itself:** every ρ_b shares the
same outcome variable (`own_e_b`), so the 96 ρ_b are mutually correlated rather than independent
draws. `p_spec` is an empirical rank count bounded below by 1/(1+|N|) = 1/79 = 0.012658 — it is
not a tail model, and no amount of extra data can move it below that floor. The bootstrap does
recompute the ρ_b from raw scores and propagates the correlation into the CIs, but the rank count
itself is a statement about ordering, not about independence.

Files created/modified:
- `docs/tasks/phase2-full-frame-placebo/PHASE2_A4_CHECKS.txt` (created; independent
  re-derivation of the two counts and the borderline check, verbatim)
- `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (this entry)
- No data file, script or protected file modified. No `git add`/`commit`/`push`.

Anything unexpected or worth flagging:
1. **My independent re-derivation script had a real bug on its first run** and I fixed it before
   writing this entry (AGENTS §5, §6): the arm filter was inverted, so it counted Arm S members
   as null placebos. It reported "1 of 78" for H where the script says 3, and listed `A222_C`
   (an Arm S background) as a null. Arm S is explicitly **not** a null in frozen §3. The corrected
   version is what is quoted above and in `PHASE2_A4_CHECKS.txt`; the script's own counts were
   never in doubt, and the correction moved my check *toward* agreement with the script rather than
   away from it. The corrected run also surfaced a useful confirmation: `A222_C` — the most
   negative Arm S background — sits below A222V on both the full frame (−0.093529969) and H
   (−0.090964259), which is exactly why the pre-registration keeps Arm S out of the null set.
2. **`G_P254F` is the single most extreme placebo in both views** (−0.096243863 full, −0.101954441
   on H) and is the background that makes both p_spec values non-trivial. With |N| = 78 fixed by
   the arms, one background carries a lot of weight here. Its identity is fixed by the frozen
   PIN-1 draw and is not re-drawn or dropped.
3. **The reported `p_spec` values are floor-limited.** `p_spec(full) = 0.025316456` is exactly two
   steps above the floor 1/79; had the count been 0, p_spec would have been 0.012658228. The
   value should be read as "1 of 78 at or below", not as a calibrated tail probability.
4. The D_site permutation is **two-sided on |D|**, following script 121's precedent; frozen §5
   does not state sidedness. This was resolved pre-run in session 2a and logged there; it is
   restated here so the p = 0.000100 is not read as one-sided. At `(1+0)/(1+10000)` the p is at
   its floor, so the sidedness choice does not change it.
5. Nothing in this entry was re-run, re-tuned or re-selected after seeing the outcome. The
   `NOT RESOLVED` gradient and the `INDETERMINATE` secondary are reported at the same length and
   prominence as the positive primary outcome word, as the frozen wording rule requires.

---

## SUMMARY (2b)

Session 2b ran 2026-09-29 and completed tasks A0, A1, A2, A3, A4: manifest deduplication,
completion and coverage, the full pre-registered analysis, the extended reproduction check, and
the verbatim verdict. The pre-registration was not touched (`PHASE2_PREREG.md` sha256
`420459ac…c8d335f2`, unmodified). `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`
and `AGENTS.md` were not edited. Scripts 123/124/125 were not edited. No `git add`/`commit`/`push`.
No threshold was loosened anywhere, no gate was retried, and no result was re-tuned after it was
seen.

**(0) A0 — manifest deduplication.**
`data/processed/phase2/manifest.csv` held **158 data rows for 96 unique `bg_id`**: **62 of the 96
backgrounds had duplicate rows, every one exactly 2 rows** (34 had a single row). Root cause, as
found on disk and reported rather than assumed: **six** scorer processes overlapped during the
overnight run (launched 2026-09-28T15:40:31, 16:02:15, 20:21:36, 20:57:14, 23:45:09 and
2026-09-29T00:33:32), not two; the last pair both ran to completion and republished 50
backgrounds, the earlier pairs republished 12 more. Each background's *scores* live in exactly one
file published by an atomic `os.replace`, so **no score was duplicated or altered — only the
timing log was**.

Resolution: for each of the 62, keep the manifest row whose logged event time is closest to the
mtime of `bg_<bg_id>.csv` on disk. Logged event times were reconstructed from sources independent
of any mtime (each `[launcher] … attempt 1/5 started` wall-clock stamp plus that event's logged
`elapsed` counter), after recovering the six per-process event chains from `run.log`. The kept row
was within **12.8 s** of the file's mtime (mean 8.7 s — the model-load offset) while the rejected
row was at least **419.9 s** away; **smallest margin 413.0 s**, so no selection was near
ambiguous. Two independent corroborations agree **62/62**: the kept row is the last `scored` line
in `run.log` for that background, and the last row in `manifest.csv` append order. Duplicates split
as **{G: 40, V: 22}** (no Arm S background was re-scored); the process that kept the file was
chain 2 → 2, chain 3 → 10, chain 5 → 50. **For all 62 the two rows are identical in
`n_positions`, `n_rows` and `device`**, so the deduplication changes **no** coverage value and no
gate; only a timing measurement differs. `manifest.csv` sha256
`98edd6fd9f229936f0790924078989b7e094bc4d16e2101b74b04f02ffda7f21` is byte-identical before and
after — it was **not** overwritten. The deduplicated table is
`data/processed/phase2/manifest_dedup.csv` (96 rows, sha256
`0dbe78000c8b736c4c3b399fef09880268658019172d3b49724db5ae461750db`), and A1's coverage check used
it as instructed.

---

### (1) READ THIS FIRST — the outcome word and both `p_spec` values, with the counts behind them

```
  OUTCOME WORD: A222V BEATS NON-SITE BACKGROUNDS
  p_spec(full) = 0.025316456   = (1 + 1) / (1 + 78)   -- 1 of 78 null placebos at or below
  p_spec(H)    = 0.050632911   = (1 + 3) / (1 + 78)   -- 3 of 78 null placebos at or below
```

Thresholds behind those counts, verbatim from the run:

```
  A222V full-frame rho = -0.088118064  ->  #{b in N : rho_b <= rho_A222V} = 1 of 78:
       G_P254F   rho = -0.096243863   (0.008125799 below A222V)
  A222V H rho        = -0.090021683  ->  #{b in N : rho_b <= rho_A222V} = 3 of 78:
       G_P254F   rho_H = -0.101954441 ; AV_220 rho_H = -0.094480281 ; AV_195 rho_H = -0.093420822
```

Both counts were re-derived independently from the per-background ρ tables in the run's own
output and agree to 1e-9 (`PHASE2_A4_CHECKS.txt`). `N` = Arm V ∪ Arm G (78); Arm S is **not** a
null (frozen §3). **Not borderline:** neither `p_spec` is within 0.01 of any threshold — the
closest approach is `p_spec(full)` at 0.0247 from the 0.05 boundary. `p_spec` is floor-limited at
1/(1+|N|) = 0.012658; `p_spec(full) = 0.025316` is the second-smallest value the rule can return,
so one placebo sitting below A222V is what keeps it off the floor.

**The frozen wording rule, verbatim from the pre-registration:** only **"A222V BEATS
NON-SITE BACKGROUNDS"** may be written up as supporting **background-specificity**; **GENERIC and
INDETERMINATE must be reported with equal prominence in every write-up.** The rule applied was:
GENERIC iff `p_spec(full) > 0.10`; "A222V BEATS NON-SITE BACKGROUNDS" iff `p_spec(full) ≤ 0.05`
**and** `p_spec(H) ≤ 0.10`; INDETERMINATE otherwise. The data give the second outcome. The full
frame and H agree.

### (2) Placebo distributions per arm, and where A222V sits

```
  primary, full frame:
    arm S: n=18 mean=-0.065159334 median=-0.064728255 range=[-0.093529969, -0.045641128]
    arm V: n=38 mean=-0.019532174 median=-0.023411207 range=[-0.084598081, +0.047573205]
    arm G: n=40 mean=-0.000230296 median=+0.010076945 range=[-0.096243863, +0.063116028]
    null set N (V u G): n=78 mean=-0.009633775 median=-0.002701665 range=[-0.096243863, +0.063116028]
    A222V rho = -0.088118064; signed rank within N u {A222V} = 2/79 (rank 1 = most negative)
  primary, held-out H:
    arm S: n=18 mean=-0.070181243 median=-0.068991235 range=[-0.090964259, -0.048929841]
    arm V: n=38 mean=-0.022540725 median=-0.022628334 range=[-0.094480281, +0.040588603]
    arm G: n=40 mean=+0.000869556 median=+0.009295575 range=[-0.101954441, +0.068247435]
    null set N (V u G): n=78 mean=-0.010535453 median=-0.006633288 range=[-0.101954441, +0.068247435]
    A222V rho = -0.090021683; signed rank within N u {A222V} = 4/79 (rank 1 = most negative)
```

A222V is the **2nd most negative of 79** on the full frame and the **4th of 79** on H. Effect
size for context: the null set spans roughly ±0.10, so A222V's anchor sits about one standard
deviation into the negative tail of a broad null distribution — a real but not overwhelming
separation. `G_P254F` is the most extreme placebo in both views. All 96 backgrounds share the
same outcome variable `own_e_b`, so the ρ_b are mutually correlated; `p_spec` is an empirical rank
count, not a tail model, and cannot fall below 1/79 at any sample size.

### (3) D_site (frozen §5, reported irrespective of the outcome)

```
  D_site = mean(S) - mean(N) = -0.055525559
  position-cluster bootstrap 95% CI (SEED+0, 10000 draws) = [-0.079318507, -0.033178263] (valid 10000)
  label permutation (10000 shuffles, n(S)=18 fixed, TWO-SIDED on |D| per script 121's precedent;
    sidedness is NOT stated in frozen section 5, logged as an ambiguity resolution; SEED+2):
    p = (1 + 0) / (1 + 10000) = 0.000100
  Interpretation (frozen, verbatim): D_site < 0 means a shared site tracks A222V's e.b beyond
  arbitrary backgrounds; that is compatible with a real site-specific effect and is not evidence
  of substitution-specificity.
```

### (4) The within-site Grantham gradient T (frozen §5)

```
  d_b = Grantham(X, V) via scripts.lib.features.grantham; 18 finite values, range [21.5, 191.2]
  T = Spearman(rho_b, d_b) over Arm S (n=18) = -0.347781218
  bootstrap T 95% CI (SEED+0) = [-0.694530444, +0.137306502] (valid 10000/10000)
  bootstrap SE(T) = 0.220219824 -> minimum detectable |T| approx 2.8 x SE = 0.616615508
  leave-one-out range = [-0.436274510, -0.225490196] (T > 0 in 0/18)
  OUTCOME WORD: NOT RESOLVED
```

The CI crosses 0, so neither SUPPORTED nor REVERSED is met. In the wording the pre-registration
requires: **"n = 18 cannot resolve this"** — never "flat". The observed |T| = 0.348 is *below* the
minimum this design could detect (0.617), so this is an absence of resolution, not evidence of no
gradient. T is negative in all 18 leave-one-out fits, which describes the point estimates only and
carries no weight under the frozen rule.

### (5) Region-demeaned secondary result (frozen §6, **NON-DECISION**)

```
  secondary p_spec(full frame) = (1 + 5) / (1 + 78) = 0.075949367  (A222V resid rho = -0.053781437)
  secondary D_site = -0.033048195, CI [-0.055707372, -0.011201292] (valid 10000)
  secondary p_spec(H)           = (1 + 5) / (1 + 78) = 0.075949367  (A222V resid rho = -0.052700937)
  secondary D_site = -0.031510979, CI [-0.056732947, -0.006420822] (valid 10000)
  A222V signed rank within N u {A222V} = 6/79 in both views (primary: 2/79 full, 4/79 H)
  secondary outcome word WOULD BE: INDETERMINATE
```

**Stated with the same prominence as the primary result:** after residualizing on region, the
separation weakens to `p_spec = 0.0759` in both views, A222V's rank falls from 2/79 and 4/79 to
6/79, and the word this analysis *would* produce is **INDETERMINATE**. Its `D_site` stays negative
with a CI excluding 0 in both views. This analysis is non-decision under frozen §6 and did not and
does not change the outcome word; it is reported because it is the strongest available evidence
about how much of the primary result is region-driven.

### (6) Every gate — name, PASS/FAIL, value

*Pre-registration integrity (re-verified at session end):*
- Prereg sha256 `420459ac…c8d335f2` — **PASS** (exact match to the frozen value)

*A1 — completion and coverage:*
- 96/96 `bg_*.csv` files present, one per roster `bg_id`, no extras, no missing — **PASS**
- All 96 pass **script 124's own** `file_is_complete()` + `expected_positions()` criteria (imported,
  not reimplemented) — **PASS**
- Row counts exact: Arm S 12,426 = 654×19; Arms V/G 12,407 = 653×19 — **PASS**
- Duplicate `(position, mut_aa)` pairs: 0 — **PASS**
- Column set exactly `bg_id,position,mut_aa,score` in all 96 — **PASS**
- **G-E** (frozen: each background scores ≥ 95% of the frame's positions; 0.95 × 654 = 621.3) —
  **PASS**, minimum **653** (`AV_5`, Arm V), 0 backgrounds below threshold, min coverage
  **0.998471 (653/654)**; Arm S is 654/654. The 653/654 for Arms V/G is the *required* PIN-5/G-C
  own-position exclusion, not missing coverage.
- `manifest_dedup.csv` vs the score files: **0** disagreements in `n_positions` or `n_rows` —
  **PASS**; device `mps` throughout

*A2 — full analysis gates (identical in the N_BOOT=300 smoke and the N_BOOT=10000 full run):*
- **G-A** A222V full-frame ρ `−0.08811806424891734` vs anchor `−0.088118`:
  |diff| = **6.425e-08 < 1e-6 — PASS**
- **G-C** rows with target position == background position in any ρ_b input: **0** (1,267
  pre-dropped) — **PASS**
- **G-D** bootstrap identity draw vs point ρ: max|diff| = **0.000e+00 < 1e-12 — PASS**
- **G-E** min positions covered: **653 ≥ 621.3 — PASS**
- Input gates: own_e_b cross-check **0/10,757** mismatches; PIN-8 region cross-check
  **0/10,757**; H = **455** positions / **7,526** rows (matches script 122); coverage gaps **0**;
  files found **96/96** — **PASS**
- Bootstrap draws with any NaN, all four passes: **0 / 10,000 / 10,000 / 10,000** — **PASS**

*G-B (carried from session 2a, not re-run here; re-scoring is model work outside 2b's scope):*
- A222_C 1.776e-15, AV_5 1.776e-15, AV_655 1.776e-15, all < 1e-6 — **PASS**; extended to all 56
  cached backgrounds in A3 below.

*A0 (new this session, no pre-registered gate — operational):*
- 158 manifest rows for 96 bg_ids; 62 duplicated; smallest selection margin **413.0 s**; kept-row
  |Δ| to file mtime ≤ **12.8 s** — **PASS**; corroborations 62/62 and 62/62
- `manifest.csv` unmodified — **PASS** (sha256 identical before/after)

*Script integrity:*
- Session 2a's SUMMARY records **no** sha256 for 123/124/125, so the instructed hash comparison
  has **no baseline** — flagged, not papered over. Current hashes recorded as the baseline going
  forward: 123 `f16655ad…aeaba`, 124 `8e2175d4…d9408`, 125 `6c5b8221…bf37d`, 130 `0e73d134…c9857`,
  `launch_phase2.sh` `69b40536…3b34`.
- All three Phase 2 scripts and the launcher have mtimes **13.6–14.6 h before the first Phase 2
  score** (earliest score 2026-09-28T15:46:26) — consistent with none having been written after a
  score existed. mtime is weaker than a hash; tampering is not claimed to be excluded.
- The one checksum 2a did record — the roster — re-verifies **exactly**
  (`9b31721a0ad98422c1923f316c76f5e4349deb9bb4b3e5ba46eadd39b1a9445b`) — **PASS**
- `torch`/`esm` appear only in script 124, as the execution doc requires — **PASS**
- All of 123/124/125 and the launcher are **untracked** in git, so there is no committed baseline
  to diff against either — flagged

### (7) A3's reproduction counts (descriptive; no decision rests on them)

Compared all **18 Arm S + 38 Arm V = 56** backgrounds against cached `task82_ae_raw.csv` on the
120-position AE grid, **2,280 cells each, 127,680 cells total** (A222V itself is not in the roster
and was not compared).

```
  (1) PARSED (pandas.read_csv both sides, i.e. what every downstream analysis sees):
      backgrounds with max|d| < 1e-6  : 56 / 56
      LARGEST max|d| over all 56      : 0.000000e+00
      cells with |d| exactly 0.0      : 127680 / 127680
  (2) STORED-TEXT (literal decimal strings, the stricter test):
      cells identical as text         : 110290 / 127680
      cells differing as text         : 17390 / 127680
      LARGEST |d| over all cells      : 1.776357e-15      (one ulp of float64)
      backgrounds with max|d|_text < 1e-6 : 56 / 56
```

**56 of 56 reproduce to better than 1e-6**; the parsed difference is exactly **0.0** everywhere.
The 17,390 textual differences are a **float-serialisation artefact, verified not assumed**:
`task82_ae_raw.csv` (mtime 2026-09-24T17:29:14) was written with 16 significant digits and the
fresh files under the current pandas 3.0.5 with the shortest round-tripping repr; whether a cell
differs as text is a per-value significant-digit property. Cached cells with no fresh counterpart:
**0**. Backgrounds whose own position lies in the AE grid: **0**. NaNs: **0**.

### (8) What this changes about the central claim

Written so that a GENERIC or INDETERMINATE outcome would read with exactly the same prominence as
this one. The rule first, then the word, then what the word licenses and does not.

**The rule (frozen §5, unchanged):** GENERIC iff `p_spec(full) > 0.10`; "A222V BEATS NON-SITE
BACKGROUNDS" iff `p_spec(full) ≤ 0.05` **and** `p_spec(H) ≤ 0.10`; INDETERMINATE otherwise. Only
the second word may be written up as supporting background-specificity.

**The word the data gave: `A222V BEATS NON-SITE BACKGROUNDS`** (`p_spec(full) = 0.025316456`,
1 of 78; `p_spec(H) = 0.050632911`, 3 of 78; rank 2/79 and 4/79).

Had the data given **GENERIC** or **INDETERMINATE**, this section would say so in the same words,
in the same place, with the same length, and the conclusion about the central claim would be the
same conclusion — namely that the pre-registered test did not license writing A222V's anchor up
as background-specific. That is what makes the positive word informative: it was a real
possibility that it would not be earned.

**What it licenses.** One statement, and only that: over the full 654-position frame, A222V's
ESM-2 background-shift anchor (ρ = −0.088118) is more extreme in the negative direction than 77
of 78 arbitrary single-substitution backgrounds, and this survives on the held-out set H, which
was never used to raise the hypothesis. The central claim that the A222V shift is **not a generic
property of perturbing any single residue** — that it is tied to the site — is supported by the
frozen test, on data that were not available to the hypothesis.

**What it does not license, stated as plainly as the part it does:**
- **Not substitution-specificity.** `D_site` is a statement about the *site*: it is negative with
  a CI excluding 0 (−0.055525559, CI [−0.079318507, −0.033178263], permutation p = 0.000100), and
  the pre-registration itself says this "is not evidence of substitution-specificity". The within-
  site Grantham gradient is **NOT RESOLVED** — n = 18 cannot resolve this. So the data say the
  *site* matters and say nothing resolved about whether Val222 specifically matters, or whether
  other substitutions at 222 differ in degree.
- **The margin is modest and the value is floor-limited.** A222V is 2nd of 79; the null set spans
  roughly ±0.10; `p_spec` cannot go below 1/79 = 0.012658 at any sample size, and one placebo
  (`G_P254F`) sitting below A222V is what holds `p_spec(full)` off that floor.
- **The region-demeaned view is weaker and would read INDETERMINATE** (`p_spec = 0.0759` in both
  views, rank 6/79). Non-decision under frozen §6, so it does not alter the word — but it means an
  appreciable share of the primary separation is region-driven, and any write-up that omits it
  would be overstating the result.
- **This is a model-based, fitness-blind, single-model result** on one device (mps), 96 backgrounds
  scored once against a fixed 654-position frame. It is a background-shift comparison, not a
  functional assay, and it says nothing about the clinical or biochemical consequence of the
  variant.
- **The confirmatory weight rests on the frozen rule and on H, not on the Phase 1 numbers** that
  motivated the test (frozen §9, and printed in the run's own output).

**Net:** the central claim is strengthened in one specific, bounded way — A222V's shift is
site-tied rather than generic — and is **not** extended to substitution-specificity or to any
clinical statement. No new result here bears on the α = 0.05 vs 0.01 question, which still needs
Arnav's fresh, explicit sign-off before `RESULTS.md` is touched.

### (9) Read first

**`## [A4]` — line 1580 of this log**: the verbatim verdict — outcome word, both `p_spec` values
with the counts and the identities of the placebos behind them, `D_site`, the gradient `T` with
its `NOT RESOLVED` wording, the region-demeaned secondary, and the borderline check.

Second, **`## [A0]` — line 950**: the operational finding that six scorer processes overlapped
(not two), the deduplication of the 62 duplicated manifest rows, and the evidence that no score
was affected. Read it because it changes the account of how the overnight run behaved, and
because A1's coverage check depends on it.

**Two disclosures about this log's own structure.** (i) The entries appear in the order
**A0, A1, A3, A2, A4**, not A0, A1, A2, A3, A4, because A3 is a pure-CSV comparison that was run
concurrently with A2's 97-minute bootstrap and finished first; entries are appended immediately on
completion, as the log format requires, and no entry was moved or edited to reorder them. (ii)
A0's script, script 130, had five failed runs of its own before the clean one (three coding
errors, one `id()`-identity bug, and one genuine methodological error where a 0.001 s
floating-point rounding artefact was being read as information). All five produced no accepted
output and all are disclosed in [A0] flag 4; the selection rule was frozen before the first run and
was not changed to suit any result. My A4 verification script likewise had an inverted arm filter
on its first run, caught and fixed before [A4] was written (flag 1 there) — it had wrongly counted
Arm S backgrounds as nulls, and correcting it moved the check *toward* agreement with the script.

**A process gap to fix, disclosed:** the detached A2 run's **exit code was not captured** (I
launched with `nohup … &` and polled). What is established: it ran to completion, printed
script 125's full summary block and a final `Elapsed 5839.4s`, and a `grep` of the whole log for
`gate fail|error|traceback|assert|FAIL` returns nothing; since script 125 calls `sys.exit(1)` on
any gate failure and all gates read PASS, a nonzero exit would have aborted before the summary.
The exit code is reported as *not recorded* rather than asserted as 0. Also, the smoke-based
runtime projection (≈84 min) under-predicted the real 97.3 min by ~14%, because per-draw cost was
not constant — the 2,000–4,000 draw block ran ~4× slower while A3 and my polling were active.
Future sessions should budget ~1.5–2 h for this pass on this machine.

**Session 2b ends here.** No re-run, no re-tuning, no threshold change, no commit, no push, and
no edit to any protected file or any earlier log entry.
