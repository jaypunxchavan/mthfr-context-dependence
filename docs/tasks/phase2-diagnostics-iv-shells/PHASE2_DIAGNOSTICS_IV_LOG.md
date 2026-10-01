# PHASE 2 Diagnostics IV - execution log

Session: cached-data-only (no model scoring; no torch/esm/thermompnn imports).
Executor: OpenCode. Planning doc: `PHASE2_DIAGNOSTICS_IV.md` (read in full before start).

Template used for every entry (as mandated):

```
## [TASK ID] - [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---
```

Entries are appended immediately after each task finishes, in order: D18, D19, D20, D21, D22.

---

## D18 - Bootstrap reproduction gate, and corrected CIs for A222V's rho
Status: FAIL at D18-G3 (the routine under test), with the pre-registered D18.4 remediation executed and its gates
PASS; D18-G1 (session-wide) PASS, so the session continues to D19-D21.
Time started / finished: 2026-09-30 ~18:46 (full run) / 2026-09-30 18:51 (full run ended, 302.0s wall).
What I did:
1. Pre-registered `scripts/148_phase2_diag4_bootstrap_gate.py` (docstring written before the first run) and
   `scripts/lib/phase2_diag4.py` (verbatim transcriptions of script 144's nested functions under `QUOTED SOURCE`
   comments with file:line, plus new `retained_parts`, `pos_cluster_boot_corrected`, `reference_boot`,
   `ids_translation`, `flag11`). Smoke first: `N_BOOT=200 N_DRAW=20`, G1 36/36 (the six matched-deletion rows SKIP
   at smoke), G3 already FAIL on all five row sets.
2. Full run: `N_BOOT=10000 N_DRAW=200 SEED=0 venv/bin/python3 scripts/148_phase2_diag4_bootstrap_gate.py >
   docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D18_FULL_OUTPUT.txt`. First full attempt crashed at D18.3
   with `ValueError: not enough values to unpack (expected 4, got 3)` from my own line `lo, hi, _, _ =
   p3.pdg.pct_ci(draws)` -- `pct_ci` (`scripts/lib/phase2_diag.py:238-245`) returns 3 values. Fixed the unpack at
   script 148 lines 529 and 683 (2 places); no gate, threshold, seed or N was touched. Second full run EXIT=0.
3. An amendment I had drafted for the task doc claiming a `ci_n_boot` data-location mismatch was checked against
   the data and found **wrong**: `task32_delta_esm_primary.csv` has no bootstrap-count column (header:
   `stage,quantity,value,ci_lo,ci_hi,p,n,ci_includes_zero,overlaps_pooled`), no `scripts/31_*.py` exists, and
   Phase 1's `N_BOOT` for this CI is 10000 (`scripts/32_delta_esm_primary.py:48-49`), equal to script 148's default.
   The draft was removed and replaced in `PHASE2_DIAGNOSTICS_IV.md` with a verification note recording the clean
   check. Mandate 14 applied; nothing in the gate changed.
Actual output (real numbers and quoted source text, not a paraphrase):
**D18-G1 (HARD, session-wide), all 42 rows PASS -- recomputed value beside the doc's target:**
```
[PASS] D18-G1 sha256 background_rho_table.csv: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
[PASS] D18-G1 sha256 background_3d_distance.csv: 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
[PASS] D18-G1 sha256 PHASE2_DIAGNOSTICS_II_CORRECTIONS.md: 8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176
[PASS] D18-G1 sha256 PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md: c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d
[PASS] D18-G1 A222V rho re-derived (full): got -0.08811806424891734 vs target -0.088118064 |diff| = 2.489e-10 (gate < 1e-09)
[PASS] D18-G1 A222V rho re-derived (H): got -0.09002168303339808 vs target -0.090021683 |diff| = 3.340e-11 (gate < 1e-09)
[PASS] D18-G1 frozen p_spec k/n (full): k = 1, n = 78, p = (1+k)/(1+n) = 0.025316456  [the doc writes this as 2/79]
[PASS] D18-G1 frozen p_spec k/n (H): k = 3, n = 78, p = (1+k)/(1+n) = 0.050632911  [the doc writes this as 4/79]
[PASS] D18-G1 k_R (full, R=10): got 23 vs target 23
[PASS] D18-G1 k_R (full, R=20): got 121 vs target 121
[PASS] D18-G1 k_R (full, R=30): got 247 vs target 247
[PASS] D18-G1 k_R (H, R=10): got 13 vs target 13
[PASS] D18-G1 k_R (H, R=20): got 86 vs target 86
[PASS] D18-G1 k_R (H, R=30): got 172 vs target 172
[PASS] D18-G1 S1 gradient n=67 (full, R=10): got 0.6894542553502687 vs target 0.689454255 |diff| = 3.503e-10 (gate < 1e-09)
[PASS] D18-G1 S1 gradient n=67 (full, R=20): got 0.6620971766258761 vs target 0.662097177 |diff| = 3.741e-10 (gate < 1e-09)
[PASS] D18-G1 S1 gradient n=67 (full, R=30): got 0.40067843966871375 vs target 0.40067844 |diff| = 3.313e-10 (gate < 1e-09)
[PASS] D18-G1 matched-deletion gradient range (full, R=10): got [+0.680406565, +0.706900130] vs target [+0.680407, +0.706900] |diff| = 4.350e-07 / 1.298e-07 (gate < 2e-06)
[PASS] D18-G1 matched-deletion gradient range (full, R=20): got [+0.663147261, +0.723050983] vs target [+0.663147, +0.723051] |diff| = 2.614e-07 / 1.712e-08 (gate < 2e-06)
[PASS] D18-G1 matched-deletion gradient range (full, R=30): got [+0.615026439, +0.731210217] vs target [+0.615026, +0.731210] |diff| = 4.393e-07 / 2.166e-07 (gate < 2e-06)
[PASS] D18-G1 matched-deletion gradient range (H, R=10): got [+0.675493864, +0.702835977] vs target [+0.675494, +0.702836] |diff| = 1.358e-07 / 2.261e-08 (gate < 2e-06)
[PASS] D18-G1 matched-deletion gradient range (H, R=20): got [+0.642046793, +0.720171605] vs target [+0.642047, +0.720172] |diff| = 2.075e-07 / 3.945e-07 (gate < 2e-06)
[PASS] D18-G1 matched-deletion gradient range (H, R=30): got [+0.602546643, +0.726412751] vs target [+0.602547, +0.726413] |diff| = 3.572e-07 / 2.492e-07 (gate < 2e-06)
  D18-G1 SUMMARY: 42/42 checks PASS, 0 FAIL
  GATE PASS: D18-G1 satisfied.  D15's machinery reproduces, so the deletion routine may be used for new statistics (D19-D21).
```
(The other G1 rows -- the twelve S1 rho/gradient/p_spec cells -- are in the full output at
`PHASE2_DIAG4_D18_FULL_OUTPUT.txt:26-77`; all PASS at 1e-9 / 2e-6.)

**D18.0, verbatim quotes with line numbers:**
```
docs/tasks/phase1-corrections-diagnostics/PHASE1_LOG.md:383:   G2 PASS: headline row reproduced exactly (-0.0881180642489173, CI [-0.1173334458953319, -0.0595113844951173])
scripts/111_a1_b1_within_family_disattenuation.py:221:     print(f"  G2 PASS: headline row reproduced exactly "
  {P1_CSV.name}, row (primary,'signed, own e_b'): value = -0.0881180642489173, ci_lo = -0.1173334458953319, ci_hi = -0.0595113844951173, n = 10757
```
The bootstrap behind it is `scripts/lib/stats.py` lines 34-56 (printed verbatim in the full output): a cluster is one
residue position; each draw samples `len(clusters)` cluster labels with replacement from a `np.random.default_rng(0)`
stream; the drawn clusters' row indices are concatenated with multiplicity and rho recomputed on that resample.
`N_BOOT`/seed from `scripts/32_delta_esm_primary.py:48-49` (`N_BOOT = int(os.environ.get("N_BOOT", 10000))`,
`SEED = 0`), call at `:102`.

**D18-G2 (HARD for D18) -- Phase 1's own routine, imported unmodified:**
```
  Phase 1 routine: observed = -0.08811806424891734, CI = [np.float64(-0.1173334458953319), np.float64(-0.05951138449511738)], median n/a, n_rows = 10757, n_clusters = 654, p_boot = 0.0
  published CI (task32 CSV)          = [-0.1173334458953319, -0.0595113844951173], point = -0.0881180642489173
  [PASS] D18-G2 Phase 1 routine reproduces the published CI (1e-9): |diff| lo = 0.000e+00, hi = 7.633e-17, point = 4.163e-17 (gate < 1e-9)
```
Exact-stream version applied (not the Monte-Carlo fallback): the seed and code are recoverable, and the agreement
is at the 1e-16 level.

**D18.2 -- script 144's routine (transcribed), same rows:**
```
   row set                                 point       p2.5        p50      p97.5         SE  centre-pt      width    nk rows/draw
  (i) UNRESTRICTED (same rows as Phase 1) -0.088118064  -0.120939  -0.042333  +0.035496   0.039598  +0.045397   0.156435   654       654
  (ii) R = 0 resolved rows (full)  -0.076685523  -0.109464  -0.029645  +0.051530   0.040967  +0.047719   0.160993   595       595
  (iii) S1 R = 10 (full)           -0.079237139  -0.112073  -0.028585  +0.053240   0.042205  +0.049821   0.165313   572       572
  (iii) S1 R = 20 (full)           -0.065947891  -0.105245  -0.013324  +0.077592   0.046330  +0.052121   0.182837   474       474
  (iii) S1 R = 30 (full)           -0.027360127  -0.125006  -0.019606  +0.087795   0.054359  +0.008755   0.212801   348       348
  D18.1 (Phase 1) on the SAME rows:  point -0.088118064, CI [-0.117333, -0.059511], width 0.057822
  script 144 on the SAME rows:       point -0.088118064, CI [-0.120939, +0.035496], width 0.156435;  width ratio = 2.71x, centre - point = +0.045397
```
Same point estimate (both concatenate every cluster once), but 2.71x the width and a centre displaced +0.0454
from the point on the very rows where Phase 1's CI is [-0.117333, -0.059511]. `rows/draw` is what script 144's
routine actually evaluates: exactly nk rows per draw, one per sampled cluster occurrence.

**Transcription fidelity gate (rule 15) -- 16 CIs replayed against D15's printed output:**
```
  [PASS] D18 transcription of pos_cluster_boot vs all 16 CIs in D15's printed output: max|diff| over 16 CIs = 4.571e-07 (gate < 2e-06); cluster counts all matched
```
The transcription is faithful; the defect is in script 144 itself, not in my copy of it.
Pre-drawn-variant fidelity (3c), all five row sets: `max|diff| over 200 draws = 0.000e+00 (required EXACTLY 0)`.

**D18-G3 (HARD for D18) -- FAILED on all five row sets:**
```
  [FAIL] D18-G3 first 200 draws agree to 1e-12 ((i) UNRESTRICTED (same rows as Phase 1)): max|diff| = 1.415e-01; draw 0 uses 10712 rows in the reference vs exactly 654 rows in script 144's routine (retained clusters = 654, retained rows = 10757)
  [FAIL] D18-G3 first 200 draws agree to 1e-12 ((ii) R = 0 resolved rows (full)): max|diff| = 1.680e-01; draw 0 uses 9632 rows in the reference vs exactly 595 rows in script 144's routine (retained clusters = 595, retained rows = 9740)
  [FAIL] D18-G3 first 200 draws agree to 1e-12 ((iii) S1 R = 10 (full)): max|diff| = 1.836e-01; draw 0 uses 9340 rows in the reference vs exactly 572 rows in script 144's routine (retained clusters = 572, retained rows = 9377)
  [FAIL] D18-G3 first 200 draws agree to 1e-12 ((iii) S1 R = 20 (full)): max|diff| = 1.665e-01; draw 0 uses 7804 rows in the reference vs exactly 474 rows in script 144's routine (retained clusters = 474, retained rows = 7742)
  [FAIL] D18-G3 first 200 draws agree to 1e-12 ((iii) S1 R = 30 (full)): max|diff| = 1.452e-01; draw 0 uses 5741 rows in the reference vs exactly 348 rows in script 144's routine (retained clusters = 348, retained rows = 5701)
  D18-G3 result: DISAGREE on: (i) UNRESTRICTED (same rows as Phase 1), (ii) R = 0 resolved rows (full), (iii) S1 R = 10 (full), (iii) S1 R = 20 (full), (iii) S1 R = 30 (full)
```
No threshold was loosened and N was not raised. The failure is a property of the statistic, not of precision:
the reference draws ~9,000-10,700 rows per draw while script 144's routine draws exactly nk (348-654).

**D18.4 -- the defect, quoted verbatim (QUOTED SOURCE, read at run time from script 144):**
```
scripts/144_phase2_diag3_farvariants.py:458:     def pos_cluster_boot(view, keep, n_boot, rng):
scripts/144_phase2_diag3_farvariants.py:459:         """POSITION-CLUSTER bootstrap: whole retained target positions are
scripts/144_phase2_diag3_farvariants.py:460:         resampled with replacement; all their rows come with them."""
scripts/144_phase2_diag3_farvariants.py:465:         kept_sizes = sizes[keep]
scripts/144_phase2_diag3_farvariants.py:466:         kept_base = base[keep]
scripts/144_phase2_diag3_farvariants.py:469:         for i in range(n_boot):
scripts/144_phase2_diag3_farvariants.py:470:             cnt = np.bincount(rng.integers(0, nk, nk), minlength=nk)
scripts/144_phase2_diag3_farvariants.py:471:             m = int(cnt.sum())
scripts/144_phase2_diag3_farvariants.py:472:             rep = np.repeat(np.arange(nk), cnt)
scripts/144_phase2_diag3_farvariants.py:473:             cum = np.concatenate([[0], np.cumsum(cnt)])
scripts/144_phase2_diag3_farvariants.py:474:             j = np.arange(m) - np.repeat(cum[:-1], cnt)
scripts/144_phase2_diag3_farvariants.py:477:             idx = np.repeat(kept_base, cnt)[rep] + j
scripts/144_phase2_diag3_farvariants.py:478:             draws[i] = rho_of(d[idx], y[idx])
```
What is wrong: `j` (line 474) is the OCCURRENCE index within a draw slot (0,1,2,...), not the row offset within that
cluster's rows. So `idx = np.repeat(kept_base, cnt)[rep] + j` (line 477) addresses `kept_base[s'] +
occurrence-index` -- a cluster drawn cnt[s] times contributes rows `base+0 .. base+cnt[s]-1`, ONE row per
occurrence, instead of ALL `sizes[s]` rows. Every draw therefore evaluates exactly nk rows (348-654) rather than the
sampled clusters' full complement (5,701-10,757), and the rows it does take are the FIRST rows of each cluster, not
the whole cluster. The point-estimate identity gate cannot see this: it only ever concatenates every cluster once
(line 486), a path that never uses `cnt` or `j`. Script 144 was NOT edited.
FIX: `scripts/lib/phase2_diag4.py pos_cluster_boot_corrected` -- each drawn cluster contributes ALL of its rows,
concatenated in draw order, as `scripts/lib/stats.py:51-53` does.

**D18-G4a (corrected vs reference, same pre-drawn ids) -- PASS, all five, `max|diff| = 0.000e+00` (gate < 1e-12).**
**D18-G4b (corrected vs Phase 1's published CI) -- PASS:**
```
  [PASS] D18-G4b corrected routine reproduces Phase 1's published CI (1e-9): corrected CI [-0.1173334458953319, -0.05951138449511738] vs published [-0.1173334458953319, -0.0595113844951173]; |diff| 0.000e+00 / 7.633e-17 (gate < 1e-9)
```
The corrected routine is bit-for-bit Phase 1's estimator on this data: same cluster order (first appearance in row
order), same integer stream.

**D18.5 -- the twelve corrected CIs (N_BOOT=10000, SEED=0, fresh rng per cell):**
```
   view cell                point      CI lo      CI hi     median        SE    ctr-pt     width  excl0   nk               old D15 CI    old w
   full S1 R = 0     -0.076685523  -0.107547  -0.045843  -0.076636  0.015764 -0.000010  0.061703   True  595 [-0.110517, +0.052946] 0.163463
   full S1 R = 10    -0.079237139  -0.110958  -0.047323  -0.079252  0.016225 +0.000097  0.063634   True  572 [-0.108943, +0.053475] 0.162418
   full S1 R = 20    -0.065947891  -0.100593  -0.030938  -0.065740  0.017816 +0.000182  0.069655   True  474 [-0.106446, +0.077385] 0.183831
   full S1 R = 30    -0.027360127  -0.067875  +0.012911  -0.027644  0.020565 -0.000122  0.080787  False  348 [-0.126369, +0.088052] 0.214421
   full SEQ Rs = 25  -0.081584044  -0.113697  -0.049861  -0.081229  0.016036 -0.000194  0.063836   True  545 [-0.115971, +0.055396] 0.171367
   full SEQ Rs = 50  -0.072880941  -0.106218  -0.039834  -0.073001  0.017053 -0.000145  0.066384   True  495 [-0.107525, +0.069562] 0.177087
      H S1 R = 0     -0.080432398  -0.114432  -0.046209  -0.080330  0.017346 +0.000112  0.068223   True  418 [-0.136966, +0.050697] 0.187663
      H S1 R = 10    -0.082101889  -0.116434  -0.046886  -0.081962  0.017986 +0.000442  0.069547   True  405 [-0.133307, +0.060709] 0.194016
      H S1 R = 20    -0.063596629  -0.102800  -0.025367  -0.063631  0.019787 -0.000487  0.077433   True  332 [-0.131090, +0.087967] 0.219057
      H S1 R = 30    -0.024367374  -0.071605  +0.023131  -0.024694  0.024286 +0.000130  0.094736  False  246 [-0.145818, +0.109530] 0.255348
      H SEQ Rs = 25  -0.087875866  -0.123753  -0.052020  -0.087586  0.018138 -0.000011  0.071733   True  393 [-0.144621, +0.054462] 0.199083
      H SEQ Rs = 50  -0.077360307  -0.114467  -0.039157  -0.076704  0.019291 +0.000548  0.075311   True  350 [-0.135943, +0.073553] 0.209496
  corrected CIs excluding zero: 10/12;  old D15 CIs excluding zero: 0/12
```
Identity gate (every cluster once reproduces the point estimate, 1e-12): PASS on all twelve cells, `|diff| = 0.000e+00`,
cluster counts equal to D15's on all twelve (595/572/474/348/545/495 and 418/405/332/246/393/350). No cell's
|centre - point| exceeds 0.01 (largest is +0.000548, H / SEQ Rs = 50).

**Gate table (verbatim tail of the full output):**
```
  D18 gates: 67/72 PASS, 5 FAIL

Elapsed 302.0s
```
The five FAILs are the five D18-G3 rows. All 20 D18-G1 rows, D18-G2, the 16-CI transcription gate, the five
pre-drawn-variant rows, the five G4a rows, G4b and the twelve D18.5 identity rows PASS.
Verdict:
- **D18-G1 (session-wide): PASS 42/42.** The session continues; the deletion routine may be used for D19-D21.
- **D18-G2: PASS**, exact-stream version (|diff| <= 7.6e-17 on the CI, 4.2e-17 on the point).
- **D18-G3: FAIL on all five row sets.** Script 144's `pos_cluster_boot` is not a position-cluster bootstrap: it
  takes one row per sampled cluster occurrence instead of the cluster's rows. No threshold was loosened; N was not
  raised.
- **D18-G4a: PASS** (corrected == reference, 0.0 on all five). **D18-G4b: PASS** (corrected reproduces Phase 1's
  published CI to 7.6e-17). The twelve-cell identity gate: PASS.
- **D18.5 result:** with the corrected routine 10/12 CIs exclude zero; D15's CIs excluded zero in 0/12. Every
  corrected CI is 0.35-0.39x the width of the D15 CI it replaces. The corrected R = 30 cells (full and H) include
  zero; all other ten exclude it. The D15 CIs printed in Diagnostics III are not usable as uncertainty statements
  and are superseded by these twelve.
- D18 as a task is logged **FAIL at G3** (rule 6: a failed gate is reported as FAIL, not worked around), with the
  pre-registered D18.4 remediation carried out and its own gates PASS.
Files created/modified:
- `scripts/148_phase2_diag4_bootstrap_gate.py` (new; created, smoke-tested, full-run; two `pct_ci` unpack fixes
  after the first full attempt crashed)
- `scripts/lib/phase2_diag4.py` (new)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D18_FULL_OUTPUT.txt` (new, full output)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV.md` (amended: a wrong draft amendment removed, a
  verification note in its place -- mandate 14)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV_LOG.md` (this entry)
Anything unexpected or worth flagging:
1. The task doc's D18-G3 is described as "HARD for D18" while D18.4 pre-registers the branch "if anything fails:
   find the defect, fix it in a new function". Both were followed: G3 is logged FAIL, and the D18.4 branch ran.
   The gate table reads 67/72 with exactly the five G3 rows failing. Flagging the tension rather than resolving it
   silently (AGENTS 9).
2. The identity gates are printed under the label `D18.5 identity, every cluster once (...)` in the gate table
   rather than "D18-G4c"; they are the same twelve-cell identity check the docstring pre-registers as G4c. Naming
   only -- no criterion changed.
3. My own first full attempt failed on a tuple-unpack bug in script 148, not on data. The fix changed no gate,
   threshold, seed or N, and the failing run's output was overwritten by the successful one; the crash text is
   recorded above.
4. `p_spec` in the G1 table is written as 2/79 and 4/79 in the task doc; the computed value is
   (1+k)/(1+n) = 2/79 = 0.025316456 and 4/79 = 0.050632911. Same numbers, different notation; both agree.
---

## D19 - Matched-deletion ranges for A222V's rho, k and p_spec
Status: PASS
Time started / finished: 2026-09-30 ~18:58 (smoke) / 2026-09-30 ~19:07 (full run ended, 88.3s wall).
What I did:
1. Pre-registered `scripts/149_phase2_diag4_md_rho_pspec.py` (docstring written before the first run): null model
   (re-derivation, no resampling inside a draw), draw generation transcribed from script 144's control loop lines
   705-724 (fresh `np.random.default_rng(SEED)` per (view, R), `rg.choice(univ, size=k_R, replace=False)`), gates
   D19-G1/G2/G3, and what is reported.
2. **Reproduction gate found in the data:** script 144 already printed rho and `p_spec` matched-deletion blocks in
   D15's full output; the Diagnostics III *log* reported only the gradient's. Those printed values are read at run
   time from `PHASE2_DIAG3_D15_FULL_OUTPUT.txt` and used as D19-G1's targets (mean, sd, 2.5/97.5, both fractions,
   for rho, k, `p_spec` **and** the gradient as a draw-identity cross-check), instead of being retyped.
3. Smoke `N_DRAW=20` EXIT=0 (G1 SKIPped, G2/G3 4/4 PASS). One bug of mine found at smoke: the summary-table loop
   passed the whole accumulator dict to `flag11` instead of the draw array (`TypeError: float() argument must be a
   string or a real number, not 'dict'`); fixed to `acc_all[(view, R)][kk]` -- a one-line indexing fix, no gate,
   threshold, seed or N touched. Full run `N_DRAW=200 SEED=0` EXIT=0.
Actual output (real numbers and quoted source text, not a paraphrase):
**D19-G2 (doc-target), the R = 0 resolved baselines:**
```
  [PASS] D19-G2 R=0 resolved baseline (full): recomputed -0.07668552269189256 vs doc target -0.076685523 |diff| = 3.081e-10 (gate < 1e-09)
  [PASS] D19-G2 R=0 resolved baseline (H): recomputed -0.0804323977038959 vs doc target -0.080432398 |diff| = 2.961e-10 (gate < 1e-09)
```
**S1 statistics and the nulls at or below A222V (named, as the doc asks):**
```
  full R = 10: k_R = 23 positions removed from a universe of 595;  A222V rho = -0.079237139;  k (n=78) = 2;  p_spec = 0.037974684;  gradient n=67 = +0.689454255
        nulls at or below A222V in this S1 case (n=78): ['AV_220', 'G_P254F']
  full R = 20: k_R = 121 positions removed from a universe of 595;  A222V rho = -0.065947891;  k (n=78) = 2;  p_spec = 0.037974684;  gradient n=67 = +0.662097177
        nulls at or below A222V in this S1 case (n=78): ['AV_220', 'G_P254F']
  full R = 30: k_R = 247 positions removed from a universe of 595;  A222V rho = -0.027360127;  k (n=78) = 4;  p_spec = 0.063291139;  gradient n=67 = +0.400678440
        nulls at or below A222V in this S1 case (n=78): ['AV_145', 'AV_220', 'G_L318F', 'G_P254F']
     H R = 10: k_R = 13 positions removed from a universe of 418;  A222V rho = -0.082101889;  k (n=78) = 2;  p_spec = 0.037974684;  gradient n=67 = +0.686580864
        nulls at or below A222V in this S1 case (n=78): ['AV_220', 'G_P254F']
     H R = 20: k_R = 86 positions removed from a universe of 418;  A222V rho = -0.063596629;  k (n=78) = 3;  p_spec = 0.050632911;  gradient n=67 = +0.640347202
        nulls at or below A222V in this S1 case (n=78): ['AV_220', 'G_L318F', 'G_P254F']
     H R = 30: k_R = 172 positions removed from a universe of 418;  A222V rho = -0.024367374;  k (n=78) = 7;  p_spec = 0.101265823;  gradient n=67 = +0.241344907
        nulls at or below A222V in this S1 case (n=78): ['AV_145', 'AV_220', 'AV_328', 'AV_650', 'G_G317Q', 'G_L318F', 'G_P254F']
```
**Does thinning alone move A222V's rho?** (random-deletion mean beside the R = 0 baseline)
```
   view    R   k_R    R=0 baseline     random mean         shift     S1 (real)   S1 - random mean
   full   10    23    -0.076685523    -0.076620772  +0.000064750  -0.079237139       -0.002616367
   full   20   121    -0.076685523    -0.076253257  +0.000432266  -0.065947891       +0.010305366
   full   30   247    -0.076685523    -0.075062605  +0.001622917  -0.027360127       +0.047702478
      H   10    13    -0.080432398    -0.080517203  -0.000084806  -0.082101889       -0.001584686
      H   20    86    -0.080432398    -0.080928195  -0.000495797  -0.063596629       +0.017331566
      H   30   172    -0.080432398    -0.078787588  +0.001644810  -0.024367374       +0.054420214
```
Read: random thinning shifts A222V's rho by at most +0.00164 (H, 172 positions), while the real R = 30 deletion
moves it by +0.0477 (full) and +0.0544 (H) — i.e. the S1 move is ~29x (full) and ~33x (H) the mean thinning shift.
Thinning alone does not account for it; what accounts for it is *which* positions.

**D19-G1 (HARD) — reproduction of D15's printed matched-deletion values, 24 gates, all PASS.** Representative rows
(the pattern is identical across all six cells x four statistics):
```
  [PASS] D19-G1 matched-deletion A222V rho (full, R=30) reproduces D15's printed value: worst is mean: got -0.07506260545985426 vs D15 -0.075062605 |diff| = 4.599e-10 (gate < 5e-05); all six: mean 4.60e-10, sd 4.14e-10, lo 2.74e-10, hi 2.48e-12, frac_le 0.00e+00, frac_ge 0.00e+00
  [PASS] D19-G1 matched-deletion p_spec, 78 nulls (H, R=30) reproduces D15's printed value: (all six components < 5e-10)
  [PASS] D19-G1 matched-deletion gradient Spearman(rho_b,d3_b), resolved nulls n=67 (full, R=10) reproduces D15's printed value: worst is mean: got 0.6932023347683551 vs D15 0.693202335 |diff| = 2.316e-10 (gate < 5e-05)
```
The gradient row is the draw-identity cross-check: reproducing D15's gradient range means this loop drew the same
deletions D15 drew, so the new rho / `p_spec` ranges are on D15's own draws.

**THE SUMMARY TABLE (rule 11: value, range, both fractions, distance to nearest bound, flag):**
```
   view    R   k_R      stat       S1 value       range lo       range hi     f<=     f>=        dist      flag
   full   10    23       rho   -0.079237139   -0.083258800   -0.069624333  0.2350  0.7650 0.004021661    INSIDE
   full   10    23         k   +2.000000000   +0.975000000   +2.000000000  0.9950  0.8450 0.000000000    INSIDE
   full   10    23    p_spec   +0.037974684   +0.025000000   +0.037974684  0.9950  0.8450 0.000000000    INSIDE
   full   20   121       rho   -0.065947891   -0.091007274   -0.062448598  0.9200  0.0800 0.003499293    INSIDE
   full   20   121         k   +2.000000000   +0.000000000   +4.025000000  0.7950  0.6200 2.000000000    INSIDE
   full   20   121    p_spec   +0.037974684   +0.012658228   +0.063607595  0.7950  0.6200 0.025316456    INSIDE
   full   30   247       rho   -0.027360127   -0.098275992   -0.047691236  1.0000  0.0000 0.020331109   OUTSIDE
   full   30   247         k   +4.000000000   +0.000000000  +10.025000000  0.7700  0.3000 4.000000000    INSIDE
   full   30   247    p_spec   +0.063291139   +0.012658228   +0.139556962  0.7700  0.3000 0.050632911    INSIDE
      H   10    13       rho   -0.082101889   -0.086499760   -0.073431733  0.3200  0.6800 0.004397871    INSIDE
      H   10    13         k   +2.000000000   +1.975000000   +4.000000000  0.7500  0.9750 0.025000000    INSIDE
      H   10    13    p_spec   +0.037974684   +0.037658228   +0.063291139  0.7500  0.9750 0.000316456    INSIDE
      H   20    86       rho   -0.063596629   -0.096713499   -0.064444959  0.9750  0.0250 0.000848330  MARGINAL
      H   20    86         k   +3.000000000   +0.000000000   +7.000000000  0.6900  0.5150 3.000000000    INSIDE
      H   20    86    p_spec   +0.050632911   +0.012658228   +0.101265823  0.6900  0.5150 0.037974684    INSIDE
      H   30   172       rho   -0.024367374   -0.104682320   -0.054086245  1.0000  0.0000 0.029718871   OUTSIDE
      H   30   172         k   +7.000000000   +0.000000000  +12.000000000  0.8850  0.1650 5.000000000    INSIDE
      H   30   172    p_spec   +0.101265823   +0.012658228   +0.164556962  0.8850  0.1650 0.063291139    INSIDE
```
Counts over the six cells: `rho: INSIDE 3, OUTSIDE 2, MARGINAL 1`; `k: INSIDE 6, OUTSIDE 0, MARGINAL 0`;
`p_spec: INSIDE 6, OUTSIDE 0, MARGINAL 0`.

**`p_spec` against the frozen numeric thresholds only (rule 10, no outcome words):**
```
    full R = 10: p_spec = 0.037974684 vs threshold 0.05 -> at or below the threshold
    full R = 20: p_spec = 0.037974684 vs threshold 0.05 -> at or below the threshold
    full R = 30: p_spec = 0.063291139 vs threshold 0.05 -> above the threshold
       H R = 10: p_spec = 0.037974684 vs threshold 0.1 -> at or below the threshold
       H R = 20: p_spec = 0.050632911 vs threshold 0.1 -> at or below the threshold
       H R = 30: p_spec = 0.101265823 vs threshold 0.1 -> above the threshold
```

**THE R = 30 FALL — the attribution check and the flag.** The task doc asked me to quote D15's claim "in its own
terms" as *"A222V's rho falls 64% (full) and 70% (H) at R = 30"*. That sentence does not exist in Diagnostics III's
log (grep for `falls 64` / `64% (full)` over `docs/` and `scripts/` returns only the task doc itself,
`PHASE2_DIAGNOSTICS_IV.md:192`). What D15 actually wrote, verbatim:
```
  docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md:833: ... **A222V's own negative association is halved by removing target variants within 30 A of 222.**
  docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md:1248: ... **A222V's own negative association is roughly halved by removing target variants within 30 A of 222.**
```
The 64% / 70% figures are a recomputation, not D15's words. Recomputed here as `fall = 1 - rho(R30)/rho(R0)`:
```
  [PASS] D19-G3 fall at R=30 (full) vs the doc's 64%: recomputed 64.3217%  = 1 - (-0.027360127)/(-0.076685523) vs doc target 64%  |diff| = 0.3217 percentage points (gate < 0.5 = rounding); the doc rounds 64.32% to 64%
  [PASS] D19-G3 fall at R=30 (H) vs the doc's 70%: recomputed 69.7045%  = 1 - (-0.024367374)/(-0.080432398) vs doc target 70%  |diff| = 0.2955 percentage points (gate < 0.5 = rounding); the doc rounds 69.70% to 70%
  --- full, R = 30 (k_R = 247) ---
    S1 fall                          = +0.643216525 (64.3217% of the association's magnitude lost)
    random-deletion fall mean        = +0.021163281   sd = 0.175346481
    random-deletion fall 2.5/97.5    = [-0.281545568, +0.378093357]
    fraction at or below S1 fall     = 1.0000;  at or above = 0.0000
    distance to nearest bound        = 0.265123168   (on the FALL scale, 0.002 threshold)
    FLAG on the fall scale (rule 11) : OUTSIDE
    FLAG on the rho scale  (rule 11) : OUTSIDE  [S1 rho -0.027360127 vs range [-0.098275992, -0.047691236]; frac at/below 1.0000, at/above 0.0000; distance to nearest bound 0.020331109]
    the two scales must agree ...: AGREE
    transform identity check: max|fall_i - (1 - rho_i/rho(R0))| = 0.000e+00
  --- H, R = 30 (k_R = 172) ---
    S1 fall                          = +0.697045289 (69.7045% of the association's magnitude lost)
    random-deletion fall mean        = +0.020449597   sd = 0.163212487
    random-deletion fall 2.5/97.5    = [-0.301494454, +0.327556473]
    fraction at or below S1 fall     = 1.0000;  at or above = 0.0000
    distance to nearest bound        = 0.369488815   (on the FALL scale, 0.002 threshold)
    FLAG on the fall scale (rule 11) : OUTSIDE
    FLAG on the rho scale  (rule 11) : OUTSIDE  [S1 rho -0.024367374 vs range [-0.104682320, -0.054086245]; frac at/below 1.0000, at/above 0.0000; distance to nearest bound 0.029718871]
    the two scales must agree ...: AGREE
```
**Answer to the doc's question:** the 64% (full) and 70% (H) fall is **OUTSIDE** what deleting 247 (172) random
positions produces, on both views, with 0 of 200 random deletions producing a fall as large (frac at or above =
0.0000) and both scales (fall and rho) giving the same flag.

**Gate table:**
```
  D19 gates: 28/28 PASS, 0 FAIL

Elapsed 88.3s
```
Verdict: **PASS.**
- D19-G1 PASS (24/24): rho, k, `p_spec` and gradient matched-deletion values reproduce D15's printed numbers to
  < 5e-9 against a 1e-9 tolerance on 9-dp values and 5e-5 on 4-dp fractions; worst component over all 24 gates was
  4.95e-10. D19's draws are D15's draws.
- D19-G2 PASS (2/2): both R = 0 baselines reproduce the doc's targets to 3.1e-10.
- D19-G3 PASS (2/2): 64.3217% and 69.7045% vs the doc's 64% / 70% (both within rounding).
- **Substantive results:** (a) A222V's rho is **OUTSIDE** the matched-deletion range at R = 30 on both views
  (distances to the nearest bound 0.0203 and 0.0297, frac at or above 0.0000) and **INSIDE** at R = 10 on both
  views; H at R = 20 is **MARGINAL** — outside by 0.00085, within the 0.002 distance rule *and* with frac at or
  above = 0.0250, i.e. both MARGINAL criteria fire, and the full view at R = 20 is INSIDE (dist 0.0035). So the
  "outside" story for A222V's own rho is an R = 30 story, on both views, plus one marginal H cell at R = 20.
  (b) `k` and `p_spec` are **INSIDE** the matched-deletion range in **all six** cells — A222V's rank among the 78
  nulls moves no more than deleting the same number of random positions moves it. That includes R = 30, where
  `p_spec` is *above* the frozen threshold (0.0633 vs 0.05 full; 0.1013 vs 0.10 H) while still being INSIDE the
  matched-deletion range: the threshold comparison and the matched-deletion flag are different questions and
  answer differently here, and both are reported as printed.
  (c) Random thinning shifts A222V's rho by at most 0.00164 while the real R = 30 deletion moves it 0.0477 / 0.0544.
- `k` and `p_spec` are one statistic at two scales (`p_spec = (1+k)/79`); their agreeing flags are printed as two
  views of one quantity, not two pieces of evidence (stated in the script's own output).
- **No threshold was loosened and N was not raised.** No frozen outcome word appears anywhere in the script or its
  output; `p_spec` is compared only to 0.05 / 0.10 with "at or below" / "above".
Files created/modified:
- `scripts/149_phase2_diag4_md_rho_pspec.py` (new; created, smoke-tested, full-run; one indexing fix after smoke)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D19_FULL_OUTPUT.txt` (new, full output)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV_LOG.md` (this entry)
Anything unexpected or worth flagging:
1. **The doc's quoted D15 claim does not exist in D15's log.** "A222V's rho falls 64% (full) and 70% (H) at R = 30"
   appears only in the task doc itself. D15 wrote "halved" / "roughly halved" (`PHASE2_DIAGNOSTICS_III_LOG.md`
   lines 833 and 1248). Both the recomputation (64.3217% / 69.7045%, agreeing with the doc's rounding) and D15's
   actual wording are printed in the script's output. D15's "roughly halved" understates its own printed numbers
   (the fall is larger than 50%). Mandate 2 (expected values are recomputations, not facts) applied to an
   attribution, not just a number.
2. **The ranges were never reported at log level.** Script 144 printed rho and `p_spec` matched-deletion blocks;
   the Diagnostics III log reported only the gradient's range (line 772 and the summary table at line 1232). The
   claim in this task's "Why" — that the log reported ranges only for the gradient — is confirmed by that check.
   Note this means D19's rho/`p_spec` ranges are a *re-presentation of already-computed D15 numbers under the
   rule-11 reporting requirement*, not new computation; the new content is the flags, the distances, the
   thinning-vs-S1 table and the fall-scale analysis.
3. The H R = 20 rho cell is MARGINAL under **both** of rule 11's criteria simultaneously (dist 0.000848 < 0.002 and
   frac at or above 0.0250 in [0.01, 0.05]); full R = 20 is INSIDE. Reporting both views as required: the two views
   disagree at R = 20 for A222V's rho, and neither cell is a clean OUTSIDE.
---

## D20 - Shell decomposition, with matched controls for shell size
Status: PASS
Time started / finished: 2026-09-30 ~19:12 (script 150 written) / smoke ~19:19-19:20 / full run finished
2026-09-30 19:26:17 (213.8s wall, measured — smoke 22.0s at N_DRAW=20/N_BOOT=200).
What I did:
1. Pre-registered `scripts/150_phase2_diag4_shells.py` (docstring before the first run): the five fixed shells
   (0,10] (10,20] (20,30] (30,45] (45,inf) on `d3_222(p)` over each view's resolved universe; REMOVE-ONE-SHELL and
   KEEP-ONLY-SHELL per shell per view; size-matched controls (N_DRAW=200, smoke 20, SEED=0, fresh
   `default_rng(SEED)` per (view, shell, variant-type) block, script 144's control construction); gate D20-G1;
   what is reported (rho point, gradient n=67 with background-level CI at N_BOOT=10000, p_spec n=78, each beside
   its own matched range with rule 11's four numbers); the summary definitions ("most damaging removal" = largest
   gradient drop from R = 0; "best preserves alone" = largest retained fraction of the R = 0 gradient) computed
   from the same arrays as the tables; resampling units; limits.
2. All machinery came from the existing `scripts/lib/phase2_diag4.py` (imported, never modified):
   `keep_from_removed`, `stats`, `grad_boot`, `flag11`, `build_view_state`. D15's printed S1 table and k_R geometry
   are parsed at run time from `PHASE2_DIAG3_D15_FULL_OUTPUT.txt` (never retyped) as the gate targets.
3. Run history (three attempts, all before any shell statistic existed):
   - attempt 1 crashed at my `KR.match()` regex (no `^\s+` anchor → `KeyError: 10` while deriving k_R targets);
     fixed the pattern only.
   - attempt 2 (smoke) **failed G1** on p_spec only: recomputed 0.0379746835443038 vs D15's printed 0.037975,
     |diff| 3.165e-07 > my uniform 1e-9. rho and gradient matched to < 4e-10. Cause: D15's table prints p_spec with
     **6 decimals** (script 144 line 783, `f"{s['p_n78']:>13.6f}"`), so 1e-9 is unachievable for it by ANY
     implementation. Corrected the p_spec tolerance to 5e-7 (the 6-dp half-ulp) and disclosed it in the script's
     own output and docstring (printed at output line 68). The run had stopped at G1 in 1.3s — **no shell
     statistic had been computed when this was changed.**
   - attempt 3 (smoke): 21/21 PASS, EXIT=0, 22.0s. Then, still before the full run, I added two deterministic
     G1b checks (REMOVE shell (0,10] alone must reproduce D15's printed R = 10 row — it *is* D15's R = 10 removal
     set since min d3_222 = 3.805 > 0), pre-registered in the docstring. Variant computations unchanged.
   - Full run `N_DRAW=200 N_BOOT=10000 SEED=0` EXIT=0, 23/23 gates PASS.
Actual output (real numbers and quoted source text, not a paraphrase). Full file:
`docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D20_FULL_OUTPUT.txt` (815 lines).

**Shell counts vs their doc targets (rule 2: recomputed independently, printed beside the target; output lines
47-59):**
```
  SHELL COUNTS vs THEIR TARGETS (rule 2 -- the doc's values are recomputations, not facts):
  [PASS] D20-G1c full shell (0,10] count vs doc target 23: recomputed from d3_222 = 23;  D15 k_R-derived = 23;  doc target = 23  (MISMATCH would mean the doc is wrong -- both numbers printed above)
  [PASS] D20-G1c full shell (10,20] count vs doc target 98: recomputed from d3_222 = 98;  D15 k_R-derived = 98;  doc target = 98  (MISMATCH would mean the doc is wrong -- both numbers printed above)
  [PASS] D20-G1c full shell (20,30] count vs doc target 126: recomputed from d3_222 = 126;  D15 k_R-derived = 126;  doc target = 126  (MISMATCH would mean the doc is wrong -- both numbers printed above)
  [PASS] D20-G1c H shell (0,10] count vs D15 k_R difference: recomputed = 13 vs D15 k_R-derived = 13 (exact integer equality)
  [PASS] D20-G1c H shell (10,20] count vs D15 k_R difference: recomputed = 73 vs D15 k_R-derived = 73 (exact integer equality)
  [PASS] D20-G1c H shell (20,30] count vs D15 k_R difference: recomputed = 86 vs D15 k_R-derived = 86 (exact integer equality)
  The two large shells have no doc target; REPORTED:
    full: (30,45] = 145, (45,inf) = 203  (no target exists -- reported as is)
    H: (30,45] = 100, (45,inf) = 146  (no target exists -- reported as is)
```
All doc targets matched exactly; no doc mismatch to report. Universe partition gates: full 23+98+126+145+203 =
595 = resolved; H 13+73+86+100+146 = 418 = resolved; all pairwise intersections empty (lines 39, 44).

**D20-G1 (HARD) — the tolerance disclosure and the gates (lines 68, 79-84, 800-813):**
```
  TOLERANCES: compared against D15's PRINTED rows, each quantity is gated at its own print precision -- rho and gradient 9-dp prints -> 1e-9; p_spec is a 6-dp print (script 144 line 783) -> 5e-7.  DISCLOSURE: the first smoke run used a uniform 1e-9, which a 6-dp print cannot satisfy for ANY implementation; corrected to print precision before the full run, with no shell statistic seen (G1 runs first).
  [PASS] D20-G1a zero-deletion == R = 0 baseline (full): keep arrays identical = True (required True); max|diff| over rho_A222V, both gradients and both k's = 0.000e+00 (required EXACTLY 0)
  [PASS] D20-G1a R = 0 baseline reproduces D15's printed row (full): worst is p_spec n=78: recomputed 0.0379746835443038 vs D15 printed 0.037975 |diff| = 3.165e-07 (gate < 5e-07 = that quantity's print precision); all: rho 3.08e-10 (tol 1e-09), gradient n=67 6.39e-11 (tol 1e-09), p_spec n=78 3.16e-07 (tol 5e-07)
  [PASS] D20-G1b union keep-mask == R = 30 keep-mask (full): boolean arrays identical = True (required EXACTLY True); union count = 247, R = 30 count = 247
  [PASS] D20-G1b union removal reproduces D15's printed R = 30 row (full): worst is p_spec n=78: recomputed 0.06329113924050633 vs D15 printed 0.063291 |diff| = 1.392e-07 (gate < 5e-07 = that quantity's print precision); all: rho 2.55e-10 (tol 1e-09), gradient n=67 3.31e-10 (tol 1e-09), p_spec n=78 1.39e-07 (tol 5e-07)
  [PASS] D20-G1b union removal reproduces the DOC target (A222V rho, full): recomputed -0.02736012725503149  vs  doc target -0.027360127  |diff| = 2.550e-10 (gate < 1e-09)
  [PASS] D20-G1b union removal reproduces the DOC target (gradient n=67, full): recomputed 0.40067843966871375  vs  doc target 0.40067844  |diff| = 3.313e-10 (gate < 1e-09)
  [PASS] D20-G1b union keep-mask == R = 30 keep-mask (H): boolean arrays identical = True (required EXACTLY True); union count = 172, R = 30 count = 172
  [PASS] D20-G1b union removal reproduces D15's printed R = 30 row (H): ... all: rho 1.63e-10 (tol 1e-09), gradient n=67 2.37e-10 (tol 1e-09), p_spec n=78 1.77e-07 (tol 5e-07)
  [PASS] D20-G1b REMOVE shell (0,10] reproduces D15's printed R = 10 row (full): ... all: rho 3.88e-10 (tol 1e-09), gradient n=67 3.50e-10 (tol 1e-09), p_spec n=78 3.16e-07 (tol 5e-07)
  [PASS] D20-G1b REMOVE shell (0,10] reproduces D15's printed R = 10 row (H): ... all: rho 1.21e-10 (tol 1e-09), gradient n=67 1.49e-10 (tol 1e-09), p_spec n=78 3.16e-07 (tol 5e-07)

  D20 gates: 23/23 PASS, 0 FAIL
```
The doc's two expected values were recomputed independently and printed beside them (rule 2): rho
-0.02736012725503149 vs -0.027360127 (2.55e-10), gradient +0.40067843966871375 vs +0.40067844 (3.31e-10) — both
match; no doc error to report.

**Representative per-variant block — the headline cell, full REMOVE (45,inf) (lines 330-357):**
```
  === [full] REMOVE-ONE-SHELL shell (45,inf): k_s = 203 positions (removed), 392 of 595 resolved positions kept ===
    rows retained: A222V = 6358;  across the 96 backgrounds min = 6339, median = 6358, max = 6358;  positions kept = 392
    A222V rho (point; no cluster CI run here, D18.5 holds the CIs) = -0.082001025
    gradient Spearman(rho_b, d3_b) on resolved nulls n = 67: +0.561648209  BACKGROUND-level bootstrap 95% CI = [+0.359744, +0.718860] (10000 usable, 0 nan, 10000 draws, SEED=0)  EXCLUDES ZERO
    gradient on all resolved backgrounds n = 85 (context only, no CI -- the task specifies n = 67): +0.713231377
    p_spec (n = 78 nulls, frozen direction rho_b <= rho_A222V): k = 0, p_spec = 0.012658228   at or below: NONE   -> at or below the frozen numeric threshold 0.05 (full)
    --- matched control (DELETING 203 random positions per draw from the 595-position resolved universe; N_DRAW = 200, SEED = 0; no resampling inside a draw) ---
    A222V rho
      variant value                  = -0.082001025
      matched-control mean           = -0.077120417   sd = 0.011077151
      matched-control 2.5 / 97.5 pct = [-0.099124366, -0.056445478]
      fraction of draws at or below  = 0.3100;  at or above = 0.6900
      distance to nearest bound      = 0.017123341   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): INSIDE
    gradient n=67
      variant value                  = +0.561648209
      matched-control mean           = +0.684646214   sd = 0.024882748
      matched-control 2.5 / 97.5 pct = [+0.632717749, +0.727086701]
      fraction of draws at or below  = 0.0000;  at or above = 1.0000
      distance to nearest bound      = 0.071069540   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): OUTSIDE
    p_spec n=78
      variant value                  = +0.012658228
      matched-control mean           = +0.039746835   sd = 0.026830858
      matched-control 2.5 / 97.5 pct = [+0.012658228, +0.114240506]
      fraction of draws at or below  = 0.1700;  at or above = 1.0000
      distance to nearest bound      = 0.000000000   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): INSIDE
```

**The best-preserve cell, full KEEP (30,45] (lines 301-321, gradient part):**
```
    gradient Spearman(rho_b, d3_b) on resolved nulls n = 67: +0.339539060  BACKGROUND-level bootstrap 95% CI = [+0.107945, +0.542137] (10000 usable, 0 nan, 10000 draws, SEED=0)  EXCLUDES ZERO
    --- matched control (RETAINING a random 145-position subset per draw of the 595-position resolved universe; N_DRAW = 200, SEED = 0; no resampling inside a draw) ---
    gradient n=67
      variant value                  = +0.339539060
      matched-control mean           = +0.624545944   sd = 0.069796268
      matched-control 2.5 / 97.5 pct = [+0.465522798, +0.740299811]
      fraction of draws at or below  = 0.0000;  at or above = 1.0000
      distance to nearest bound      = 0.125983737   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): OUTSIDE
```

**The MARGINAL cells (both criteria fire for each), H REMOVE (10,20] (lines 446-466):**
```
    A222V rho
      variant value                  = -0.065071860
      matched-control mean           = -0.080531184   sd = 0.007529568
      matched-control 2.5 / 97.5 pct = [-0.094858647, -0.066379839]
      fraction of draws at or below  = 0.9850;  at or above = 0.0150
      distance to nearest bound      = 0.001307979   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): MARGINAL
    gradient n=67
      variant value                  = +0.645056370
      matched-control mean           = +0.682302604   sd = 0.018009997
      matched-control 2.5 / 97.5 pct = [+0.646044598, +0.712329143]
      fraction of draws at or below  = 0.0250;  at or above = 0.9750
      distance to nearest bound      = 0.000988227   (MARGINAL distance threshold 0.002)
      -> FLAG (rule 11): MARGINAL
```

**SUMMARY TABLE A — the GRADIENT (n = 67), output lines 681-692:**
```
   view     shell   k_s      R0 grad    REMOVE grad         drop   drop %      flag     KEEP grad  frac of R0      flag
   full    (0,10]    23 +0.698473511   +0.689454255 +0.009019256    1.29%    INSIDE  -0.084984536     -0.1217    INSIDE
   full   (10,20]    98 +0.698473511   +0.663793276 +0.034680235    4.97%    INSIDE  -0.288556321     -0.4131   OUTSIDE
   full   (20,30]   126 +0.698473511   +0.681612292 +0.016861219    2.41%    INSIDE  +0.182639928      0.2615   OUTSIDE
   full   (30,45]   145 +0.698473511   +0.767255313 -0.068781802   -9.85%   OUTSIDE  +0.339539060      0.4861   OUTSIDE
   full  (45,inf)   203 +0.698473511   +0.561648209 +0.136825302   19.59%   OUTSIDE  +0.058265988      0.0834   OUTSIDE
      H    (0,10]    13 +0.688316871   +0.686580864 +0.001736007    0.25%    INSIDE  +0.068761848      0.0999    INSIDE
      H   (10,20]    73 +0.688316871   +0.645056370 +0.043260501    6.28%  MARGINAL  -0.287139579     -0.4172   OUTSIDE
      H   (20,30]    86 +0.688316871   +0.667385015 +0.020931857    3.04%    INSIDE  +0.137324154      0.1995   OUTSIDE
      H   (30,45]   100 +0.688316871   +0.728723935 -0.040407064   -5.87%   OUTSIDE  +0.295560212      0.4294   OUTSIDE
      H  (45,inf)   146 +0.688316871   +0.566317470 +0.121999401   17.72%   OUTSIDE  -0.058285942     -0.0847   OUTSIDE
  drop = R0 - REMOVE (positive = gradient fell);  drop % = drop relative to that view's R = 0 gradient;  frac of R0 = KEEP / R0 (fraction of the baseline gradient retained).
```

**SUMMARY TABLE B — A222V's RHO, output lines 697-708:**
```
   view     shell   k_s        R0 rho    REMOVE rho       change  |chg| %R0      flag      KEEP rho  frac of R0      flag
   full    (0,10]    23  -0.076685523  -0.079237139 -0.002551617     -3.33%    INSIDE  +0.129216559     -1.6850  MARGINAL
   full   (10,20]    98  -0.076685523  -0.066536360 +0.010149163     13.23%    INSIDE  +0.004812725     -0.0628   OUTSIDE
   full   (20,30]   126  -0.076685523  -0.061991680 +0.014693842     19.16%    INSIDE  -0.118108396      1.5402    INSIDE
   full   (30,45]   145  -0.076685523  -0.076655422 +0.000030101      0.04%    INSIDE  -0.076330478      0.9954    INSIDE
   full  (45,inf)   203  -0.076685523  -0.082001025 -0.005315502     -6.93%    INSIDE  +0.012893786     -0.1681   OUTSIDE
      H    (0,10]    13  -0.080432398  -0.082101889 -0.001669491     -2.08%    INSIDE  +0.109952243     -1.3670  MARGINAL
      H   (10,20]    73  -0.080432398  -0.065071860 +0.015360538     19.10%  MARGINAL  +0.006162621     -0.0766  MARGINAL
      H   (20,30]    86  -0.080432398  -0.067160511 +0.013271886     16.50%    INSIDE  -0.114275722      1.4208    INSIDE
      H   (30,45]   100  -0.080432398  -0.076244032 +0.004188365      5.21%    INSIDE  -0.083150869      1.0338    INSIDE
      H  (45,inf)   146  -0.080432398  -0.094766180 -0.014333782    -17.82%    INSIDE  +0.018337201     -0.2280   OUTSIDE
```

**SUMMARY TABLE C — p_spec (n = 78) vs the frozen numeric thresholds (rule 10), lines 713-732 (verbatim):**
```
    full REMOVE shell    (0,10]: p_spec = 0.037974684 (k = 2) -> at or below the threshold 0.05   flag vs its own size-matched range: INSIDE
    full KEEP   shell    (0,10]: p_spec = 1.000000000 (k = 78) -> above the threshold 0.05   flag vs its own size-matched range: OUTSIDE
    full REMOVE shell   (10,20]: p_spec = 0.037974684 (k = 2) -> at or below the threshold 0.05   flag vs its own size-matched range: INSIDE
    full KEEP   shell   (10,20]: p_spec = 0.632911392 (k = 49) -> above the threshold 0.05   flag vs its own size-matched range: OUTSIDE
    full REMOVE shell   (20,30]: p_spec = 0.050632911 (k = 3) -> above the threshold 0.05   flag vs its own size-matched range: INSIDE
    full KEEP   shell   (20,30]: p_spec = 0.037974684 (k = 2) -> at or below the threshold 0.05   flag vs its own size-matched range: INSIDE
    full REMOVE shell   (30,45]: p_spec = 0.088607595 (k = 6) -> above the threshold 0.05   flag vs its own size-matched range: MARGINAL
    full KEEP   shell   (30,45]: p_spec = 0.063291139 (k = 4) -> above the threshold 0.05   flag vs its own size-matched range: INSIDE
    full REMOVE shell  (45,inf): p_spec = 0.012658228 (k = 0) -> at or below the threshold 0.05   flag vs its own size-matched range: INSIDE
    full KEEP   shell  (45,inf): p_spec = 0.721518987 (k = 56) -> above the threshold 0.05   flag vs its own size-matched range: OUTSIDE
       H REMOVE shell    (0,10]: p_spec = 0.037974684 (k = 2) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H KEEP   shell    (0,10]: p_spec = 0.949367089 (k = 74) -> above the threshold 0.1   flag vs its own size-matched range: INSIDE
       H REMOVE shell   (10,20]: p_spec = 0.050632911 (k = 3) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H KEEP   shell   (10,20]: p_spec = 0.658227848 (k = 51) -> above the threshold 0.1   flag vs its own size-matched range: MARGINAL
       H REMOVE shell   (20,30]: p_spec = 0.063291139 (k = 4) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H KEEP   shell   (20,30]: p_spec = 0.025316456 (k = 1) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H REMOVE shell   (30,45]: p_spec = 0.151898734 (k = 11) -> above the threshold 0.1   flag vs its own size-matched range: OUTSIDE
       H KEEP   shell   (30,45]: p_spec = 0.037974684 (k = 2) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H REMOVE shell  (45,inf): p_spec = 0.012658228 (k = 0) -> at or below the threshold 0.1   flag vs its own size-matched range: INSIDE
       H KEEP   shell  (45,inf): p_spec = 0.822784810 (k = 64) -> above the threshold 0.1   flag vs its own size-matched range: OUTSIDE
```

**THE ANSWER (computed from the tables above, lines 739-769):**
```
  --- full view (R = 0 gradient +0.698473511, R = 0 rho -0.076685523) ---
    gradient drop by shell (REMOVE, descending): (45,inf) +0.136825, (10,20] +0.034680, (20,30] +0.016861, (0,10] +0.009019, (30,45] -0.068782
    MOST DAMAGING REMOVAL = shell (45,inf) (k = 203): gradient +0.698473511 -> +0.561648209 (drop +0.136825302, 19.59% of R0), flag OUTSIDE
    next = shell (10,20] (drop +0.034680235, flag INSIDE)
    separation check (rule 11, own ranges): the top two REMOVE gradient ranges are [+0.632717749, +0.727086701] and [+0.659378929, +0.720370648] -> OVERLAP: their ordering is NOT separated by their own matched ranges
    rho attenuation by shell (REMOVE, descending): (20,30] +0.014694, (10,20] +0.010149, (30,45] +0.000030, (0,10] -0.002552, (45,inf) -0.005316
    the rho ordering says most damaging = shell (20,30] -> DIFFERS with the gradient ordering
    retained fraction of R = 0 gradient by shell (KEEP-ONLY, descending): (30,45] 0.4861, (20,30] 0.2615, (45,inf) 0.0834, (0,10] -0.1217, (10,20] -0.4131
    BEST PRESERVES ALONE = shell (30,45] (k = 145): gradient +0.339539060 = 48.61% of R0, flag OUTSIDE
    next = shell (20,30] (fraction 0.2615, flag OUTSIDE)
    separation check: the top two KEEP gradient ranges are [+0.465522798, +0.740299811] and [+0.452590542, +0.724480695] -> OVERLAP: their ordering is NOT separated by their own matched ranges
    rho fraction (KEEP / R0) by shell: (0,10] -1.6850, (10,20] -0.0628, (20,30] 1.5402, (30,45] 0.9954, (45,inf) -0.1681   (above 1.0000 = magnitude exceeds baseline)
    rho ordering of KEEP preservation says best = shell (20,30] -> DIFFERS with the gradient ordering

  --- H view (R = 0 gradient +0.688316871, R = 0 rho -0.080432398) ---
    gradient drop by shell (REMOVE, descending): (45,inf) +0.121999, (10,20] +0.043261, (20,30] +0.020932, (0,10] +0.001736, (30,45] -0.040407
    MOST DAMAGING REMOVAL = shell (45,inf) (k = 146): gradient +0.688316871 -> +0.566317470 (drop +0.121999401, 17.72% of R0), flag OUTSIDE
    next = shell (10,20] (drop +0.043260501, flag MARGINAL)
    separation check (rule 11, own ranges): the top two REMOVE gradient ranges are [+0.612122119, +0.723096877] and [+0.646044598, +0.712329143] -> OVERLAP: their ordering is NOT separated by their own matched ranges
    rho attenuation by shell (REMOVE, descending): (10,20] +0.015361, (20,30] +0.013272, (30,45] +0.004188, (0,10] -0.001669, (45,inf) -0.014334
    the rho ordering says most damaging = shell (10,20] -> DIFFERS with the gradient ordering
    retained fraction of R = 0 gradient by shell (KEEP-ONLY, descending): (30,45] 0.4294, (20,30] 0.1995, (0,10] 0.0999, (45,inf) -0.0847, (10,20] -0.4172
    BEST PRESERVES ALONE = shell (30,45] (k = 100): gradient +0.295560212 = 42.94% of R0, flag OUTSIDE
    next = shell (20,30] (fraction 0.1995, flag OUTSIDE)
    separation check: the top two KEEP gradient ranges are [+0.428702983, +0.720871995] and [+0.358043500, +0.719287140] -> OVERLAP: their ordering is NOT separated by their own matched ranges
    rho fraction (KEEP / R0) by shell: (0,10] -1.3670, (10,20] -0.0766, (20,30] 1.4208, (30,45] 1.0338, (45,inf) -0.2280   (above 1.0000 = magnitude exceeds baseline)
    rho ordering of KEEP preservation says best = shell (20,30] -> DIFFERS with the gradient ordering

  BETWEEN THE TWO VIEWS:
    most damaging removal: full = (45,inf), H = (45,inf) -> the SAME shell in both views
    best preserving alone: full = (30,45], H = (30,45] -> the SAME shell in both views
```

**LIMITS STATED WITH THE RESULT (lines 774-784, verbatim):**
```
  * SHELLS DIFFER IN SIZE, so every effect above is compared ONLY with its own size-matched control, never across shells: the tables report each variant against the range from deleting/retaining the SAME NUMBER of random positions.
  * The (30,45] and (45,inf) shells are LARGE: full (30,45] = 145, (45,inf) = 203, H (30,45] = 100, (45,inf) = 146.
  * KEEP-ONLY of a SMALL shell leaves few rows per background and a noisy rho_b:
      full (0,10] keeps 344-363 rows per background (A222V 363 rows, 23 positions)
      H (0,10] keeps 202-220 rows per background (A222V 220 rows, 13 positions)
  * p_spec under a variant compares DIFFERENTLY-THINNED row sets (each background has its own usable rows), exactly as in D15: disclosed, not corrected.
  * A222V's rho here has NO bootstrap CI by construction of this task; D18.5 holds the session's corrected CIs.  The matched range answers only 'is this what the same NUMBER of random positions does?', not 'is it nonzero'.
  * d3_222 is a CA-CA distance in ONE 2.50 A crystal structure of the dimer; a CA-CA distance is not a contact.
  * Unresolved positions and their rows are dropped and counted (printed per view above), never imputed.
  * Rank fractions over small n are rank fractions, not tests (rule 10).  p_spec is compared only to the frozen numeric thresholds 0.05 (full) / 0.10 (H).
  * The matched-deletion spread is a RE-DERIVATION null over 200 draws; the smallest one-sided fraction it can resolve is 0.0050.
```

Verdict: **PASS.** D20-G1 PASS (23/23, all deterministic; doc targets matched: shell counts 23/98/126 exact, rho
-0.027360127 to 2.55e-10, gradient +0.400678440 to 3.31e-10). Substantive answer, stated at each shell's own
size-matched control (never across shells):
1. **No single shell reproduces D15's R = 30 collapse.** The R = 30 union (first three shells, gated above)
   drops the gradient by 0.2978 = 42.64% (full) and 0.4470 = 64.94% (H) from the R = 0 baselines of
   +0.698473511 / +0.688316871 (union values = D15's printed R = 30 row, lines 646/654 of D15's output; full
   also gated at doc targets above). The largest SINGLE-shell drop is (45,inf): 19.59% (full) / 17.72% (H),
   flagged OUTSIDE. The first three shells alone are small: (0,10] 1.29% INSIDE, (10,20] 4.97% INSIDE,
   (20,30] 2.41% INSIDE on full; 0.25% INSIDE, 6.28% MARGINAL, 3.04% INSIDE on H.
2. **Gradient and rho orderings disagree** in both views (printed "DIFFERS"): by gradient the most damaging single
   shell is (45,inf) on both views; by rho attenuation it is (20,30] (full) and (10,20] (H). And **no REMOVE cell's
   rho is OUTSIDE**: 9 of 10 rho REMOVE flags are INSIDE, the tenth (H (10,20]) is MARGINAL (dist 0.001308,
   frac at or above 0.0150 — both MARGINAL criteria fire).
3. **Removing (30,45] RAISES the gradient** above baseline on both views (full +0.6985 -> +0.7673, H
   +0.6883 -> +0.7287), flagged OUTSIDE on both.
4. **Best single-shell sufficiency is (30,45] on both views** (48.61% / 42.94% of the R = 0 gradient retained),
   but its flag is OUTSIDE *below* its own size-matched range (full observed +0.3395 vs
   [+0.4655, +0.7403]; H +0.2956 vs [+0.4287, +0.7209]): retaining 145 (100) RANDOM positions preserves
   more gradient than retaining that shell.
5. **Both answers are the same in both views**, but in all four separation checks the top two shells' own matched
   ranges OVERLAP, so the ordering *within* the top two is not separated by their own controls — stated as such
   in the output, not as a clean ranking.
6. **Post-hoc observation (NOT pre-registered, arithmetic on Table A + D15's R = 30 row):** the individual drops of
   the first three shells sum to 0.0606 (full) / 0.0659 (H), versus the union's 0.2978 / 0.4470 — i.e. the union
   effect is ~4.9x (full) and ~6.8x (H) the sum of its parts. The R = 30 collapse is strongly non-additive, so
   "the signal lives within 30 A" cannot be attributed to any one of the first three shells.
7. Rule 11 flags for p_spec are reported beside the threshold comparison as separate questions (Table C): e.g.
   full REMOVE (30,45] has p_spec 0.088608, above the 0.05 threshold, and MARGINAL against its own range;
   full REMOVE (45,inf) has p_spec 0.012658, at or below 0.05, INSIDE.
- **No threshold was loosened and N was not raised.** The one tolerance change (1e-9 -> 5e-7 on p_spec only) was a
  print-precision correction made at smoke before any shell statistic existed, disclosed in the script's output.
  No frozen outcome word appears anywhere; `p_spec` is compared only to 0.05 / 0.10 with "at or below" / "above".
- All limits above are printed by the script itself, not only here.
Files created/modified:
- `scripts/150_phase2_diag4_shells.py` (new; created, three run attempts as disclosed, full run)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D20_FULL_OUTPUT.txt` (new, full output, 815 lines)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV_LOG.md` (this entry)
- NOT modified: `scripts/lib/phase2_diag4.py` and all other libs (used as-is), no protected file, nothing
  staged/committed/pushed (`git status` checked: only pre-existing modifications, none mine beyond this task's
  new files).
Anything unexpected or worth flagging:
1. **The most damaging single-shell removal is the FARTHEST shell (45,inf), not a near-222 shell.** This is not a
   contradiction of D15: D15's R = 30 removed the first three shells *together* (gated here as their union), and
   each near shell alone is INSIDE or MARGINAL against its own control. The far shell's removal is OUTSIDE its
   control on both views (frac at or below 0.0000 for the gradient), while (30,45]'s removal pushes the gradient
   *up* and is also OUTSIDE. Report both facts; neither was pre-expected in the doc.
2. **The top-two overlap caveat**: "most damaging = (45,inf)" and "best preserves = (30,45]" are answers under the
   pre-registered definitions, but their margins over the runner-up are NOT separated by their own matched ranges
   (all four separation checks overlap). Do not write these up as clean rankings.
3. The p_spec tolerance issue (attempt 2 above) was a gate-calibration defect of mine, not a data problem — rho and
   gradient passed 1e-9 on the same run. Disclosed in output line 68 and in the docstring's GATES section.
4. KEEP-ONLY sign flips: (0,10] and (10,20] KEEP produce NEGATIVE gradients on both views (e.g. H (10,20]
   -0.287139579, background-level CI [-0.481982, -0.060343], excluding zero below) and rho flips positive
   (full (0,10] KEEP rho +0.129216559). For small-shell KEEP this is exactly the "few rows, noisy rho_b" limit
   the doc asked to state (344-363 rows full / 202-220 H per background).
---

## D21 - Equal-k ordering test: sequence, 3D, or random?
Status: PASS
Time started / finished: 2026-09-30 evening — `scripts/151_phase2_diag4_equal_k.py` written and pre-registered in
its docstring before the first run; smoke runs measured 14.3s (attempt 2) and 14.8s (attempt 3); full run
attempt 2 measured 118.1s wall (the script's own `Elapsed 117.8s`, output line 785); this entry written
2026-09-30 20:11.
What I did:
1. Pre-registered `scripts/151_phase2_diag4_equal_k.py` (docstring before first run): universe = resolved
   positions (doc targets 595 full / 418 H); four k slots per view — `k_seq(25)`, `k_seq(50)`, `k_R(20)`,
   `k_R(30)` — full-frame doc targets 50/100/121/247, H computed; SEQ-k = k smallest |p − 222| ties by
   ascending position; 3D-k = k smallest `d3_222` ties ascending; RANDOM-k = N_DRAW=200, SEED=0, a fresh
   `default_rng(SEED)` per (view, k) block (script 144's control construction, lines 717-721). BOTH SEQ-k and
   3D-k are computed at EVERY slot's k (so the cross-method set is reported even where D15 has no counterpart).
   Reported per slot: overlap (count + Jaccard); A222V's rho (POINT — no bootstrap CI here; D18.5 holds this
   session's CIs), gradient n=67, p_spec n=78, each beside its OWN RANDOM-k 2.5/97.5 range with rule 11's
   numbers (value, range, both one-sided fractions, distance to nearest bound) and INSIDE/OUTSIDE/MARGINAL flag;
   p_spec compared only to the frozen numeric thresholds 0.05 (full) / 0.10 (H) with "at or below"/"above"
   (rule 10). Gates G1a-G1h pre-registered as HARD (task doc rule 6: any failure stops D21).
2. Determination required by the doc (lines 245-247), read from script 144 BEFORE any run: line 572 keeps
   `resolved & ~np.isin(POSV, rm)` — D15's sequence sensitivities DID drop unresolved-position rows, so D15's
   printed SEQ values are on the RESOLVED universe and under the doc's conditional they ARE identity gates
   (D21-G1e). This also reconciles D15's "positions retained = 495" for Rs = 50: 495 = 595 − 100 (resolved),
   not 654 − 100 = 554 (frame); the reconciliation is printed at run time (line 92).
3. All shared machinery imported from `scripts/lib/phase2_diag4.py` (used as-is, never modified this session).
   D15's S1 table, k_R geometry, matched-deletion gradient lines and four SEQ blocks are parsed AT RUN TIME
   from `PHASE2_DIAG3_D15_FULL_OUTPUT.txt` (never retyped) — output line 17: 8 table rows, 8 matched-deletion
   lines, 4 SEQ blocks.
4. Run history (five attempts; all disclosed per AGENTS 6):
   - smoke attempt 1 (0.8s): FAILED 4 G1c checks. I had written the 3D comparison mask as
     `resolved & (d3 <= R)` — the REMOVED set, which keeps 121 — instead of D15's keep mask (keeps 474).
     Fixed the EXPRESSION only (the gate's rule, mask identity vs script 144's construction, unchanged);
     no statistic and no control draw had been computed. Disclosed in the docstring's G1c.
   - smoke attempt 2: 33/33 PASS, 14.3s.
   - full attempt 1 (N_DRAW=200, 118.1s): **EXIT=1** — `KeyError: ('full', 20)` at the G1g gate. Cause: my
     `MD` pattern expected the header "(n=200):" but D15 prints "(n=200 draws):", so 0 matched-deletion lines
     parsed (attempt-1 output line 17) and the gate crashed on `MD15[(view, R)]` BEFORE evaluating any G1g
     check and BEFORE the gate tally. This was a REGEX DEFECT IN MY SCRIPT, not a disagreement between two
     sources. The crashed run's own output already showed the four recomputed RANDOM-k gradient ranges equal
     D15's printed matched-deletion ranges exactly (attempt-1 output lines 180/186/204/210 vs D15 lines
     645/647/653/655: `[+0.663147261, +0.723050983]`, `[+0.615026439, +0.731210217]`,
     `[+0.642046793, +0.720171605]`, `[+0.602546643, +0.726412751]`) — the stream identity the gate tests held;
     only the pattern was wrong. Fix: the word " draws" added to the pattern, plus an 8/8/4 parse-count guard
     so a future parse miss fails with a clear "[PARSER FAIL] ... defect in this script's parsers ... NOT a
     data disagreement" instead of a KeyError. NO threshold, tolerance or decision rule was changed. Disclosed
     in the docstring's G1g. CAVEAT: attempt 1's output was overwritten by attempt 2 at the same path (one
     full-output file per task); its content is quoted here from the session record, not from disk.
   - smoke attempt 3 (post-fix): 33/33 PASS, EXIT=0, 14.8s.
   - full attempt 2: **EXIT=0, 118.1s wall, 37/37 gates PASS**.
Actual output (real numbers and quoted source text, not a paraphrase). Full file:
`docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D21_FULL_OUTPUT.txt` (785 lines).

**Geometry and k counts vs the doc's targets (rule 2: recomputed independently, printed beside the target;
lines 85-121):**
```
  [full] frame positions = 654;  RESOLVED universe = 595;  unresolved = 59;  min |p - 222| among resolved = 1;  min d3_222 = 3.805 A;  NaN in d3_222 = 0
  [full] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM EVERY SET AND FROM THE BASELINE, NEVER IMPUTED: A222V 1017 of 10757 rows; per background min = 998, max = 1017 ***
  [full] recomputed k: SEQ-window Rs = 25 -> k = 50, SEQ-window Rs = 50 -> k = 100, 3D R = 20 A -> k = 121, 3D R = 30 A -> k = 247
  [PASS] D21-G1b full SEQ-window Rs = 25 count vs doc target 50: recomputed = 50;  doc target 50;  D15 printed retained 545 -> 595 - 545 = 50;  -> PASS (exact integer equality vs doc and D15)
  [PASS] D21-G1b full SEQ-window Rs = 50 count vs doc target 100: recomputed = 100;  doc target 100;  D15 printed retained 495 -> 595 - 495 = 100;  -> PASS (exact integer equality vs doc and D15)
  [PASS] D21-G1b full 3D R = 20 A count vs doc target 121: recomputed = 121;  doc target 121;  D15 printed k_R = 121;  -> PASS (exact integer equality vs doc and D15)
  [PASS] D21-G1b full 3D R = 30 A count vs doc target 247: recomputed = 247;  doc target 247;  D15 printed k_R = 247;  -> PASS (exact integer equality vs doc and D15)
  [full] 495 RECONCILIATION (doc line 237): D15 printed positions retained for Rs = 50 = 495;  recomputed here = resolved(595) - k_seq(50)(100) = 495;  frame-based arithmetic = 654 - 100 = 554 (NOT 495).  The retained count is over the RESOLVED universe.
  [PASS] D21-G1a full resolved universe == doc target 595 and == D15's R = 0 retained: recomputed = 595;  doc target (line 234) = 595;  D15 printed retained at R = 0 = 595 (exact integer equality)
  [H] frame positions = 455;  RESOLVED universe = 418;  unresolved = 37;  min |p - 222| among resolved = 2;  min d3_222 = 5.058 A;  NaN in d3_222 = 0
  [H] recomputed k: SEQ-window Rs = 25 -> k = 25, SEQ-window Rs = 50 -> k = 68, 3D R = 20 A -> k = 86, 3D R = 30 A -> k = 172
  [PASS] D21-G1a H resolved universe == doc target 418 and == D15's R = 0 retained: recomputed = 418;  doc target (line 234) = 418;  D15 printed retained at R = 0 = 418 (exact integer equality)
  Count/set gates: 19/19 PASS, 0 FAIL
```
All four full-frame doc targets matched exactly (50/100/121/247) and all eight k values were confirmed
independently against D15's own prints; H had no doc target ("H: compute") and its k's derive from D15's
printed retained counts (418 − 393 = 25, 418 − 350 = 68) and k_R (86, 172).

**D21-G1 (HARD) — tolerances and the gates (lines 126, 127-156, 212-220):**
```
  TOLERANCES: each quantity is gated at the source's own print precision -- rho and gradient are 9-decimal prints (script 144 lines 779/781) -> 5e-10 half-ulp; p_spec is a 6-decimal print (line 783) -> 5e-7; '0 difference' additionally means the keep MASKS are identical arrays (G1c above).
  [PASS] D21-G1f zero-deletion == baseline (full): keep arrays identical = True (required True); max|diff| over rho_A222V, gradient n=67 and both k's = 0.000e+00 (required EXACTLY 0)
  [PASS] D21-G1f baseline reproduces D15's printed R = 0 row (full): worst is p_spec n=78: recomputed 0.0379746835443038 vs D15 printed 0.037975 |diff| = 3.165e-07 (gate < 5e-07 = that quantity's print precision); all: rho 3.08e-10 (tol 5e-10), gradient n=67 6.39e-11 (tol 5e-10), p_spec n=78 3.16e-07 (tol 5e-07)
  [PASS] D21-G1d 3D-k at k_R(20) reproduces D15's S1 R = 20 row (full) -- task doc line 244 HARD identity: worst is p_spec n=78: recomputed 0.0379746835443038 vs D15 printed 0.037975 |diff| = 3.165e-07; all: rho 4.59e-10 (tol 5e-10), gradient n=67 3.74e-10 (tol 5e-10), p_spec n=78 3.16e-07 (tol 5e-07), k_R count 0.00e+00 (tol 0)
  [PASS] D21-G1d 3D-k at k_R(30) reproduces D15's S1 R = 30 row (full) -- task doc line 244 HARD identity: worst is p_spec n=78 ... |diff| = 1.392e-07; all: rho 2.55e-10, gradient n=67 3.31e-10, p_spec 1.39e-07, k_R count 0.00e+00
  [PASS] D21-G1e SEQ-k at k_seq(25) reproduces D15's printed SEQ Rs = 25 row (full): worst is gradient n=67: recomputed 0.6953606705963813 vs D15 printed 0.695360671 |diff| = 4.036e-10; all: rho 1.79e-10 (tol 5e-10), gradient n=67 4.04e-10 (tol 5e-10), p_spec k 0.00e+00 (tol 0), positions retained 0.00e+00 (tol 0)
  [PASS] D21-G1e SEQ-k at k_seq(50) reproduces D15's printed SEQ Rs = 50 row (full): worst is gradient n=67 ... |diff| = 2.756e-10 ...
  [PASS] D21-G1d 3D-k at k_R(20) reproduces D15's S1 R = 20 row (H) ... worst is p_spec n=78 ... |diff| = 8.861e-08; all: rho 4.57e-10, gradient 4.36e-10, p_spec 8.86e-08, k_R 0.00e+00
  [PASS] D21-G1d 3D-k at k_R(30) reproduces D15's S1 R = 30 row (H) ... worst is p_spec n=78 ... |diff| = 1.772e-07; all: rho 1.63e-10, gradient 2.37e-10, p_spec 1.77e-07, k_R 0.00e+00
  [PASS] D21-G1e SEQ-k at k_seq(25) reproduces D15's printed SEQ Rs = 25 row (H): worst is gradient n=67 ... |diff| = 8.353e-11 ...
  [PASS] D21-G1e SEQ-k at k_seq(50) reproduces D15's printed SEQ Rs = 50 row (H): worst is gradient n=67 ... |diff| = 1.331e-10 ...
  [PASS] D21-G1f zero-deletion == baseline (H): keep arrays identical = True (required True); max|diff| ... = 0.000e+00 (required EXACTLY 0)
  [PASS] D21-G1f baseline reproduces D15's printed R = 0 row (H): ... all: rho 2.96e-10 (tol 5e-10), gradient n=67 3.33e-10 (tol 5e-10), p_spec n=78 3.16e-07 (tol 5e-07)
  [PASS] D21-G1h every RANDOM draw keeps exactly len(universe) - k positions (all blocks): all draw keep-counts equal universe - k = True (required True); full/seq25: 545-545 of expected 545;  full/seq50: 495-495 of expected 495;  full/R20: 474-474 of expected 474;  full/R30: 348-348 of expected 348;  H/seq25: 393-393 of expected 393;  H/seq50: 350-350 of expected 350;  H/R20: 332-332 of expected 332;  H/R30: 246-246 of expected 246
  [PASS] D21-G1h first draw of every block reproduces from a fresh default_rng(SEED): max|diff| over all blocks = 0.000e+00 (required EXACTLY 0)
  [PASS] D21-G1g RANDOM-121 reproduces D15's printed matched-deletion gradient line (R = 20, full) -- same seed, same stream: worst is range lo: recomputed np.float64(0.6631472614310338) vs D15 printed 0.663147261 |diff| = 4.310e-10; all: range lo 4.31e-10 (tol 5e-10), range hi 1.16e-10 (tol 5e-10), frac at or below 0.00e+00 (tol 5e-05), frac at or above 0.00e+00 (tol 5e-05), n draws 0.00e+00 (tol 0)
  [PASS] D21-G1g RANDOM-247 reproduces D15's printed matched-deletion gradient line (R = 30, full) ... worst range hi |diff| = 3.524e-10; fracs 0.00e+00 both
  [PASS] D21-G1g RANDOM-86 reproduces D15's printed matched-deletion gradient line (R = 20, H) ... worst range lo |diff| = 4.946e-10; fracs 0.00e+00 both
  [PASS] D21-G1g RANDOM-172 reproduces D15's printed matched-deletion gradient line (R = 30, H) ... worst range hi |diff| = 1.819e-10; fracs 0.00e+00 both

  Gates before the analysis: 37/37 PASS, 0 FAIL
  GATE PASS so far: D21-G1 satisfied.  The equal-k analysis may be reported.
```
(The eight G1c set-identity checks all printed `keep arrays identical = True (required EXACTLY True)` — lines
95-98 and 112-115 — and the G1d/G1e rows above confirm that at the identity slots BOTH methods reproduce
D15's printed values within print precision; the four G1g rows confirm the RANDOM-k blocks at k_R(20)/k_R(30)
ARE D15's matched-deletion stream, ranges AND both fractions exact to 4-decimal print precision.)

**Representative RANDOM-k control block — full RANDOM-121 (lines 177-181):**
```
  === [full] RANDOM-121 (3D R = 20 A): k = 121 deleted per draw from the 595-position resolved universe; N_DRAW = 200, SEED = 0 ===
    kept positions per draw: min = 474, max = 474 (expected 474);  first-draw determinism |diff| = 0.000e+00
    RANDOM-k A222V rho: mean = -0.076253257, sd = 0.007281463, min = -0.099971859, max = -0.058567063, 2.5/97.5 pct = [-0.091007274, -0.062448598]
    RANDOM-k gradient n=67: mean = +0.690973760, sd = 0.016380035, min = +0.654474708, max = +0.734251222, 2.5/97.5 pct = [+0.663147261, +0.723050983]
    RANDOM-k p_spec n=78: mean = +0.036455696, sd = 0.017563610, min = +0.012658228, max = +0.139240506, 2.5/97.5 pct = [+0.012658228, +0.063607595]
```
The gradient range `[+0.663147261, +0.723050983]` is D15's printed matched-deletion range for full R = 20
(D15 output line 645) — gate G1g, line 214.

**Overlap of SEQ-k and 3D-k (the doc's first required report; slot headers lines 227, 282, 337, 392, 447,
502, 557, 612):**
```
  view    k    intersection   union   Jaccard   positions differing
  full    50      13           87     0.1494    74
  full   100      61          139     0.4388    78
  full   121      69          173     0.3988   104
  full   247     196          298     0.6577   102
  H       25       6           44     0.1364    38
  H       68      43           93     0.4624    50
  H       86      49          123     0.3984    74
  H      172     134          210     0.6381    76
```
(computed verbatim from the OVERLAP lines: e.g. line 393 `OVERLAP: |SEQ-247 intersect 3D-247| = 196
positions;  union = 298;  Jaccard = 0.6577  (the two sets differ in 102 positions)`.)

**THE ANSWER AT EQUAL k (lines 670-728, verbatim):**
```
  Pre-registered definitions (docstring): gradient drop = baseline gradient - set gradient (positive = fell); rho attenuation = set rho - baseline rho (rho_0 < 0; positive = magnitude lost).  '3D-k MORE DESTRUCTIVE' requires BOTH larger for 3D-k; disagreement prints DISAGREE with both pairs.  Gradient verdict: 3D OUTSIDE + SEQ INSIDE -> SUPPORTED at this k; both INSIDE -> UNSUPPORTED at this k (claim WITHDRAWN at this k); anything else is printed with its exact flags.
  D15's original comparison was UNEQUAL-k (SEQ Rs = 50, k = 100 vs 3D R = 30, k = 247 -- task doc line 231): the equal-k versions are the seq50 slot and the R30 slot below.

  --- full view (baseline gradient +0.698473511, baseline rho -0.076685523; k values: seq25 = 50, seq50 = 100, R20 = 121, R30 = 247) ---
    [SEQ-window Rs = 25, k = 50]  overlap = 13, Jaccard = 0.1494
      gradient drop   : SEQ-k +0.003112840,  3D-k +0.008979348
      rho attenuation : SEQ-k -0.004898521,  3D-k +0.002250306
      MORE DESTRUCTIVE: 3D-k IS MORE DESTRUCTIVE THAN SEQ-k (both metrics)
      flags vs RANDOM-50: gradient SEQ = INSIDE, 3D = INSIDE;  rho SEQ = INSIDE, 3D = INSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: UNSUPPORTED at this k: BOTH SEQ-k and 3D-k are INSIDE the RANDOM-k range on the gradient -> the '3D not sequence' claim is WITHDRAWN at this k
    [SEQ-window Rs = 50, k = 100]  overlap = 61, Jaccard = 0.4388
      gradient drop   : SEQ-k +0.017539659,  3D-k +0.022707772
      rho attenuation : SEQ-k +0.003804582,  3D-k +0.007048330
      MORE DESTRUCTIVE: 3D-k IS MORE DESTRUCTIVE THAN SEQ-k (both metrics)
      flags vs RANDOM-100: gradient SEQ = INSIDE, 3D = INSIDE;  rho SEQ = INSIDE, 3D = INSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: UNSUPPORTED at this k: BOTH SEQ-k and 3D-k are INSIDE the RANDOM-k range on the gradient -> the '3D not sequence' claim is WITHDRAWN at this k
    [3D R = 20 A, k = 121]  overlap = 69, Jaccard = 0.3988
      gradient drop   : SEQ-k +0.022388506,  3D-k +0.036376334
      rho attenuation : SEQ-k +0.011906626,  3D-k +0.010737632
      MORE DESTRUCTIVE: DISAGREE: gradient drop SEQ +0.022389 vs 3D +0.036376 -> 3D; rho attenuation SEQ +0.011907 vs 3D +0.010738 -> SEQ
      flags vs RANDOM-121: gradient SEQ = INSIDE, 3D = MARGINAL;  rho SEQ = INSIDE, 3D = INSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: NOT decidable by the pre-registered rule at this k: gradient flags are SEQ = INSIDE, 3D = MARGINAL -- reported with those exact flags, no stronger word
    [3D R = 30 A, k = 247]  overlap = 196, Jaccard = 0.6577
      gradient drop   : SEQ-k +0.323615684,  3D-k +0.297795071
      rho attenuation : SEQ-k +0.058252020,  3D-k +0.049325395
      MORE DESTRUCTIVE: 3D-k IS LESS DESTRUCTIVE THAN SEQ-k (both metrics)
      flags vs RANDOM-247: gradient SEQ = OUTSIDE, 3D = OUTSIDE;  rho SEQ = OUTSIDE, 3D = OUTSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: NOT decidable by the pre-registered rule at this k: gradient flags are SEQ = OUTSIDE, 3D = OUTSIDE -- reported with those exact flags, no stronger word

  --- H view (baseline gradient +0.688316871, baseline rho -0.080432398; k values: seq25 = 25, seq50 = 68, R20 = 86, R30 = 172) ---
    [SEQ-window Rs = 25, k = 25]  overlap = 6, Jaccard = 0.1364
      gradient drop   : SEQ-k -0.000897935,  3D-k +0.003930959
      rho attenuation : SEQ-k -0.007443468,  3D-k -0.001140505
      MORE DESTRUCTIVE: 3D-k IS MORE DESTRUCTIVE THAN SEQ-k (both metrics)
      flags vs RANDOM-25: gradient SEQ = INSIDE, 3D = INSIDE;  rho SEQ = INSIDE, 3D = INSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: UNSUPPORTED at this k: BOTH SEQ-k and 3D-k are INSIDE the RANDOM-k range on the gradient -> the '3D not sequence' claim is WITHDRAWN at this k
    [SEQ-window Rs = 50, k = 68]  overlap = 43, Jaccard = 0.4624
      gradient drop   : SEQ-k +0.038271974,  3D-k +0.030829093
      rho attenuation : SEQ-k +0.003072091,  3D-k +0.013587086
      MORE DESTRUCTIVE: DISAGREE: gradient drop SEQ +0.038272 vs 3D +0.030829 -> SEQ; rho attenuation SEQ +0.003072 vs 3D +0.013587 -> 3D
      flags vs RANDOM-68: gradient SEQ = MARGINAL, 3D = INSIDE;  rho SEQ = INSIDE, 3D = INSIDE;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: NOT decidable by the pre-registered rule at this k: gradient flags are SEQ = MARGINAL, 3D = INSIDE -- reported with those exact flags, no stronger word
    [3D R = 20 A, k = 86]  overlap = 49, Jaccard = 0.3984
      gradient drop   : SEQ-k +0.050424025,  3D-k +0.047969670
      rho attenuation : SEQ-k +0.013054771,  3D-k +0.016835769
      MORE DESTRUCTIVE: DISAGREE: gradient drop SEQ +0.050424 vs 3D +0.047970 -> SEQ; rho attenuation SEQ +0.013055 vs 3D +0.016836 -> 3D
      flags vs RANDOM-86: gradient SEQ = MARGINAL, 3D = MARGINAL;  rho SEQ = INSIDE, 3D = MARGINAL;  p_spec SEQ = INSIDE, 3D = INSIDE
      GRADIENT VERDICT: NOT decidable by the pre-registered rule at this k: gradient flags are SEQ = MARGINAL, 3D = MARGINAL -- reported with those exact flags, no stronger word
    [3D R = 30 A, k = 172]  overlap = 134, Jaccard = 0.6381
      gradient drop   : SEQ-k +0.381582361,  3D-k +0.446971965
      rho attenuation : SEQ-k +0.066042253,  3D-k +0.056065024
      MORE DESTRUCTIVE: DISAGREE: gradient drop SEQ +0.381582 vs 3D +0.446972 -> 3D; rho attenuation SEQ +0.066042 vs 3D +0.056065 -> SEQ
      flags vs RANDOM-172: gradient SEQ = OUTSIDE, 3D = OUTSIDE;  rho SEQ = OUTSIDE, 3D = OUTSIDE;  p_spec SEQ = MARGINAL, 3D = INSIDE
      GRADIENT VERDICT: NOT decidable by the pre-registered rule at this k: gradient flags are SEQ = OUTSIDE, 3D = OUTSIDE -- reported with those exact flags, no stronger word

  OVERALL AT EQUAL k (per construction slot; the two views' k values differ because their universes differ):
    full: SUPPORTED at slots NONE;  WITHDRAWN (both inside) at slots seq25, seq50;  other flags at slots R20, R30
    H: SUPPORTED at slots NONE;  WITHDRAWN (both inside) at slots seq25;  other flags at slots seq50, R20, R30
    both views give the SAME verdict at every slot: NO
```

**LIMITS STATED WITH THE RESULT (lines 733-740, verbatim):**
```
  * COMPARISONS ARE WITHIN A VIEW AT EQUAL k only: SEQ-k and 3D-k are deleted at the SAME k, each judged against ITS OWN RANDOM-k range.  The two views have different universes, so their k values differ (full: 50, 100, 121, 247; H: 25, 68, 86, 172).
  * SEQ-k and 3D-k OVERLAP (printed at every k above); any difference between their effects comes only from the positions in the union-minus-intersection part.
  * |p - 222| is a RESIDUE-INDEX distance, not a structural distance; d3_222 is a CA-CA distance in ONE 2.50 A crystal structure of the dimer; a CA-CA distance is not a contact.
  * p_spec under a deletion compares DIFFERENTLY-THINNED row sets (each background has its own usable rows), exactly as in D15: disclosed, not corrected.
  * Unresolved positions and their rows are dropped and counted (printed in the geometry section), never imputed.
  * No bootstrap CI is computed in this script: the matched range answers 'is this what the same NUMBER of random positions does?', not 'is it nonzero'.  D18.5 holds this session's corrected CIs.
  * Rank fractions over small n are rank fractions, not tests (rule 10).  p_spec is compared only to the frozen numeric thresholds 0.05 (full) / 0.10 (H).
  * The RANDOM-k spread is a RE-DERIVATION null over 200 draws; the smallest one-sided fraction it can resolve is 0.0050.
```

Verdict: **PASS.** D21-G1 PASS (37/37: 19 count/set + 12 reproduction + 2 null-identity + 4 stream-identity).
All doc targets matched (universe 595/418; k 50/100/121/247 and 25/68/86/172; 495 reconciliation). The
substantive answer to "3D, not sequence?" at equal k, per the pre-registered rules:
1. **SUPPORTED (3D OUTSIDE while SEQ INSIDE) at ZERO of eight slots.** The claim is never supported at equal k.
2. **WITHDRAWN (both INSIDE the RANDOM-k range) at three slots**: full seq25 (k=50), full seq50 (k=100),
   H seq25 (k=25). At k=100 — the equal-k re-do of D15's sequence arm — deleting 100 sequence-nearest
   positions does no distinguishable damage relative to deleting 100 random ones, and neither does deleting
   the 100 nearest in 3D.
3. **At the largest k both sets are OUTSIDE, and on full the SEQUENCE set is MORE destructive on BOTH
   metrics**: at k=247, SEQ drop +0.323615684 vs 3D +0.297795071, SEQ rho attenuation +0.058252020 vs 3D
   +0.049325395 (line 693-695: "3D-k IS LESS DESTRUCTIVE THAN SEQ-k (both metrics)"); SEQ-247's gradient
   +0.374857827 sits below its own range's lower bound with frac at or below 0.0000 (line 410), i.e. deleting
   247 sequence-nearest positions is at least as destructive as deleting 247 3D-nearest ones. D15's
   "tracks 3D distance" conclusion came from exactly this comparison at UNEQUAL counts (100 SEQ vs 247 3D,
   task doc line 231); at equal k it does not survive as a 3D-specific statement.
4. **The remaining five slots are flagged, not adjudicated** (pre-registered rule: no stronger word than the
   flags): full R20 (SEQ INSIDE, 3D MARGINAL), H seq50 (SEQ MARGINAL, 3D INSIDE), H R20 (both MARGINAL),
   full R30 and H R30 (both OUTSIDE). The gradient-vs-rho metrics DISAGREE at four of these five slots
   (lines 689, 709, 715, 721).
5. **The views do not agree on every slot** (line 728: "the two views give the SAME verdict at every slot:
   NO") — full has two WITHDRAWN slots, H one.
6. p_spec vs the frozen numeric thresholds only (rule 10): full all "at or below 0.05" except SEQ-247
   (0.088607595) and 3D-247 (0.063291139), both "above"; H all "at or below 0.10" except SEQ-172
   (0.177215190) and 3D-172 (0.101265823), both "above". Rule-11 flags for p_spec: INSIDE everywhere except
   H SEQ-172 = MARGINAL (value 0.177215190, range [+0.012658228, +0.164556962], dist 0.012658228,
   frac at or below 0.9950 — line 639).
- **No threshold was loosened and N was not raised.** The two defects fixed mid-session (G1c mask expression,
  MD regex) were gate/parser defects, fixed before any gated statistic was seen, disclosed in the script's
  own docstring and here. No frozen outcome word appears anywhere; `p_spec` is compared only to 0.05/0.10
  with "at or below"/"above". All limits above are printed by the script itself, not only here.
Files created/modified:
- `scripts/151_phase2_diag4_equal_k.py` (new; pre-registered docstring, five run attempts as disclosed)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D21_FULL_OUTPUT.txt` (new, full output, 785 lines;
  holds attempt 2 — attempt 1's crashed output was overwritten at this path, disclosed above)
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAGNOSTICS_IV_LOG.md` (this entry)
- NOT modified: `scripts/lib/phase2_diag4.py` and all other libs (used as-is), no protected file, no earlier
  log or script ≤147, nothing staged/committed/pushed (`git status` checked: only pre-existing modifications
  plus this session's new untracked files).
Anything unexpected or worth flagging:
1. **The headline caveat is the count confound D21 was built to test — and it cuts against D15.** D15 compared
   100 removed sequence positions against 247 removed 3D positions. At equal k the only slot where BOTH
   deletions are attributable (OUTSIDE) shows the SEQUENCE deletion more destructive on both metrics (full
   k=247), and the three small-k slots where D15's R=0-adjacent deletions were mild come out INSIDE for both
   methods. State this two-sidedly: the equal-k data do not support "3D, not sequence" at any k, and at the
   largest k they point the other way on full. The overlap also grows with k (Jaccard 0.15 -> 0.66 full),
   so at k=247 the two methods share 196 of 298 union positions — much of the large-k comparison involves
   nearly the same deleted set, which is printed, not hidden.
2. **Rule 11 refines two of D15's printed flags.** D15 printed "OUTSIDE" for the R = 20 gradient on both
   views (D15 lines 645/653); under session rule 11 the SAME numbers are MARGINAL on both counts — full:
   dist 0.001050085 < 0.002 AND frac at or below 0.0150 in [0.01, 0.05] (lines 381-382); H: dist 0.001699591 AND
   frac 0.0250 (lines 601-602). This is a stricter flag definition (introduced in D19), not a numeric
   disagreement: the ranges and fractions reproduce D15's exactly (G1g).
3. **Recurring identical p_spec values are the discrete ladder of 78 nulls, not a column-identity bug**
   (AGENTS 5): every printed p_spec equals (k+1)/79 to within the 9-dp print (checked: k=0 -> 0.012658228,
   k=1 -> 0.025316456, k=2 -> 0.037974684, ..., k=13 -> 0.177215190, all |diff| < 5e-10), so the same k under
   different sets prints the same value by construction; rho and gradient DO differ across sets (e.g. full
   k=100: SEQ rho -0.072880941 vs 3D -0.069637193, gradient +0.680933852 vs +0.675765739).
4. The two G1g-gated ranges that reproduce D15's matched-deletion lines are the SAME stream D19 reproduced
   (same seed, same universe, same k), so D15's control and this session's RANDOM-k blocks are interchangeable
   at k_R(20)/k_R(30) — which is what makes the equal-k comparison against D15's printed OUTSIDE flags valid.
---

## D22 - Corrections to the Diagnostics III log (append-only; write LAST)
Status: PASS - 85/85 D22 gates PASS, 0 FAIL; every gate ran BEFORE any byte was written; WRITE 1 (the corrections
file) and WRITE 2 (the single append-only addition to the III log, last) both completed; a fourth run confirmed the
append is idempotent.
Time started / finished: first attempt not separately timed (the pre-run defect fixes preceded it); canonical run
finished 2026-09-30 21:03:49 (mtime of `PHASE2_DIAG4_D22_FULL_OUTPUT.txt` and of the III log), idempotency re-run
finished 21:04:15; script 152's last edit 21:03:31. This task parses text only - `Elapsed 0.0s` (output line 405) is
real; no resampling runs here.
What I did:
1. Doc D22 (`PHASE2_DIAGNOSTICS_IV.md` lines 255-288): locate each old sentence by searching the III log **at run
   time** (the log is read-only for this purpose; line numbers given anywhere else are not trusted), quote it
   verbatim with its REAL line number, put the recomputed fact beside it, write the corrected statement from
   computed variables (no hand-typed numbers), end every section with "Cite this, not the old sentence.", write
   `PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md` and report its sha256, with the log addition as the LAST write.
2. Pre-registered in the docstring of `scripts/152_phase2_diag4_corrections.py` **before the first run**: the K11-K16
   search strings (including the extra K11 string `all twelve`, which the doc does not list, because III log lines
   1319 and 1368 both carry the claim); rule 11 verbatim (INSIDE; MARGINAL = outside but distance <= 0.002 from a
   bound OR a one-sided fraction in [0.01, 0.05]; OUTSIDE otherwise) with the requirement to print value, range,
   BOTH fractions and distance to the nearest bound; every doc target and its tolerance; the K11 branch rule
   (D18-G2 + D18-G1 + D18-G3 decide which branch applies); the full gate list; and the limitation that
   `flag11_printed()` re-derives rule 11 from D15's/D19's printed summaries rather than from raw draws.
3. Stdlib only - `ast`, `hashlib`, `re`, `sys`, `time`, `pathlib` (script 152 lines 179-184). No numpy/pandas, no
   torch/esm/thermompnn, no model scoring, no bootstrap/permutation (`N_BOOT`/`N_PERM` are never read by this
   script).
4. Design: gates first (`gfail()` -> `sys.exit(1)` before any write); the six sections are built ONCE and shared by
   stdout, the corrections file and the log append, so the three cannot drift apart; WRITE 2 is marker-guarded on
   `[D22-APPEND]`, verifies the pre-append bytes are an exact PREFIX of the post-append file, and prints both
   sha256 values.
5. Before the first analysis run I did a read-only dry parse (a throwaway script outside the repo,
   `/private/var/folders/tv/c79722px07l2bv90zk3slkmc0000gn/T/opencode/tmp_d22_drycheck.py`, which parses and never
   writes). Defects it and attempt 1 exposed, all fixed before any write: an always-false comparison clause; two
   multi-line f-string SyntaxErrors; `D18_ROW` requiring signs on unsigned SE/width columns (0 rows parsed);
   `D15_K172` matching both the full 247 and H 172 blocks (restricted to `=== full, R = 30 A`); a sub-gate reading
   the IV log instead of the D18 output; a gate requiring `len(d15c)==6` when that block has 8 rows; a gate
   requiring exactly five `[FAIL]` lines when D18 prints ten (5 gate-table + 5 summary - it now requires all five
   row-set labels); a row parser searching the wrong file. Sub-gates added BEFORE the first run and documented in
   the docstring: G2k, G4 (D21 R30 all-OUTSIDE; D21 R20 3D=MARGINAL), G5g, G6g, G7h.
6. Run history - four runs, all disclosed:
   - **Attempt 1** - EXIT=1, 82 of 84 gates PASS; G2b/G2c FAIL because my row parser searched the wrong file. No
     write occurred (gates run first). **That output was overwritten by attempt 3 and is not on disk**; the 82/84
     figure is recorded here only, which is why it is cited nowhere else.
   - **Attempt 2** - EXIT=0, 84/84 gates PASS; both writes performed (corrections sha
     `2b096343e1c95abb63bf033d6609c8af29c7867d7cf75d943e8a0d8761b468f8`; III log 1368 -> 1561). Output preserved as
     `PHASE2_DIAG4_D22_FULL_OUTPUT_RUN2.txt`. Then **rolled back** before the canonical run: K16's corrected
     statement printed only `frac<= 0.0250` for the H R = 20 cell - the non-discriminating tail - where the
     pre-registration requires BOTH fractions. The III log was restored to its 1368 pre-append lines and its
     sha256 re-verified byte-identical to the pre-append sha `39d6ea6889580d75466edd017d9565a6311d6c0e3912fe910460b06a51d1c7b4`;
     run-2's corrections file was deleted. The change made afterwards was **prose only** (print both fractions);
     no gate, threshold, target, tolerance or number changed. Disclosed as a post-hoc correction to statement text,
     made before the canonical write (AGENTS §6).
   - **Attempt 3** - canonical: EXIT=0, **85/85 gates PASS**, both writes; output
     `PHASE2_DIAG4_D22_FULL_OUTPUT.txt` (405 lines).
   - **Attempt 4** - idempotency re-run: `marker [D22-APPEND]: ALREADY PRESENT` (line 9),
     `SKIPPED: marker [D22-APPEND] already present in the log (idempotent re-run).  No bytes written.` (line 308),
     85/85 again (gates-first verdict at line 100, gate summary `D22 gates: 85/85 PASS, 0 FAIL.` at line 399 of that file); III log sha unchanged (`8f41f1fe...`) and corrections sha unchanged (`612c4565...`).
     Output `PHASE2_DIAG4_D22_IDEMPOTENCY_CHECK.txt`.

Actual output (real numbers; line numbers are of the canonical `PHASE2_DIAG4_D22_FULL_OUTPUT.txt`, 405 lines):

- **Gates before either write:** lines 11-100, ending `85/85 D22 gates PASS.  The corrections may be written.`
  (line 100); gate table lines 30-100 and 314-402; final `D22 gates: 85/85 PASS, 0 FAIL.` (line 402). Selected rows:
  - G2f line 35 `corrected CIs excluding zero: 10/12`; G2g line 36 `old D15 CIs excluding zero: 0/12`; G2h line 37
    cluster counts `[595, 572, 474, 348, 545, 495, 418, 405, 332, 246, 393, 350]`; G2i line 38 (D18's output and the
    IV log's quote of it both read 10/12 and 0/12); G2j line 39 (G1 42/42, G2 PASS, G3 FAILED, ten `[FAIL]` lines
    covering all five row sets); G2k line 40 (published CI `[-0.1173334458953319, -0.0595113844951173]` reproduced
    with `|diff|` lo = 0.000e+00, hi = 7.633e-17).
  - G3 rule-11 re-derivation, lines 48-55: all eight D15 cells recompute to the pre-registered flag, each with
    value, range, BOTH fractions and distance printed - e.g. full R = 20 `+0.662097177` vs
    `[+0.663147261, +0.723050983]`, `frac<= 0.0150, frac>= 0.9850`, distance `0.001050084` -> **MARGINAL**; H R = 20
    `+0.640347202` vs `[+0.642046793, +0.720171605]`, `frac<= 0.0250`, distance `0.001699591` -> **MARGINAL**;
    R = 30 **OUTSIDE** on both (distances 0.214347999 / 0.361201736, `frac<= 0.0000`); R = 10 **INSIDE** both;
    R = 0 **INSIDE** (degenerate range, distance 0.000000000).
  - Doc targets recomputed beside the doc: K12's six at lines 42-47, K13's six at lines 57-62, K15's five at lines
    81-84 and line 87 (`P(rank 2nd or better of 19) = 0.105263158` vs doc 0.105), K16's two falls at lines 90 and 92
    (64.3217 / 69.7045 vs doc 64 / 70) - all within their pre-registered tolerances.
  - G4 line 63 (595 resolved and 495 SEQ-retained cross-gate D18.5's cluster counts), line 64 (script 144's SEQ
    removal definition located at line 569, resolved-universe removal at 572), lines 65-66 (D21's seq50 and R30
    drops equal K13's to 1e-12), line 67 (D21 SUPPORTED at slots NONE on both views; same verdict at every slot:
    NO), line 68 (D21 R = 30: gradient AND rho, SEQ-k and 3D-k, all OUTSIDE vs RANDOM-247), line 69 (D21 R = 20:
    3D gradient MARGINAL on both views; full rho INSIDE, H rho MARGINAL).
  - G5g line 76: both OUTSIDE-flagged shells sit BELOW their own matched range - REMOVE (45,inf) value
    `+0.561648209` < lo `+0.632717749` (H `+0.566317470` < `+0.612122119`); KEEP (30,45] `+0.339539060` <
    `+0.465522798` (H `+0.295560212` < `+0.428702983`).
  - G6e line 85 (recomputed predicted/residual max `|diff|` = 8.212e-07, gate < 5e-6), G6f line 86 (rank 2/19 in all
    8 model-view cells), G6g line 88 (A222V's shift rank **3 of 19** on both views - interior, neither 1st nor
    19th; site shifts 0.066545-0.105150 full, 0.067910-0.107653 H, A222V 0.070330 / 0.069403).
  - G7a line 89 and G7b line 91 (falls recompute from D15's printed rhos: 0.643216530 vs D19's 0.643216525, and
    0.697045288 vs 0.697045289); G7f line 398 (6/6 of D19's rho values equal D15's, max `|diff|` = 0.000e+00);
    G7h line 400 (rule-11 flag re-derived from value, range, BOTH fractions and distance for all six cells - H
    R=10 INSIDE, H R=20 MARGINAL, H R=30 OUTSIDE, full R=10 INSIDE, full R=20 INSIDE, full R=30 OUTSIDE - all equal
    to D19's printed flags).
- **The six corrections**, each ending "Cite this, not the old sentence." Old text at REAL pre-append III-log line
  numbers: K11 lines 1250, 834, 1319, 1368; K12 lines 829, 1366, 1245; K13 lines 832, 1243; K14 lines 1368, 1317,
  1310; K15 lines 1077, 1284, 1315; K16 lines 1248, 1314, 833 (full verbatim quotes printed at output lines
  106-117, 146-153, 176-181, 212-221, 241-252, 276-283). Corrected statements at output lines **138 (K11), 168 (K12),
  201 (K13), 233 (K14), 268 (K15), 295 (K16)**; the mandated citation line follows at 140/170/206/235/270/297.
- **Writes:** lines 300-303 WRITE 1 - `PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md`, 218 lines, **sha256
  `612c4565378a4c41d35e4bc203b9b3182dc43b457243b8232de0271f8bb69d23`** (re-verified afterwards with
  `shasum -a 256`); lines 305-311 WRITE 2 (LAST) - `appended 195 lines (marker [D22-APPEND])`,
  `lines: 1368 -> 1562; pre-append bytes are a prefix of the post-append file: True`, pre-append sha
  `39d6ea6889580d75466edd017d9565a6311d6c0e3912fe910460b06a51d1c7b4`, post-append sha
  `8f41f1fee66178e9f6ff2dc2cd3a7bfce9325dab2e0ed5c145074775eb0a20f1`. In the III log the append header is line 1372
  (`## [D22-APPEND] ...`), the AGENTS-vs-D22 tension line 1375, the corrections sha line 1376, `85/85 D22 gates
  PASS` line 1377. `git diff --numstat` on that file reports `194 0` (insertions only, 0 deletions).
- **Limitations printed with the run (output line 404):** K11 replaces CIs withdrawn by D18's own failed gate, not
  by re-judgement here; K12's rule-11 flags come from D15's printed percentiles and fractions with rule 11 applied
  verbatim (the raw draws are not re-derived in this script - D21's G1g already gated those printed summaries to
  <= 4.95e-10 on bounds and exactly on fractions); K13 compares both native unequal-k windows and D21's equal-k
  slots and says which is which; K14 is a category error about which axis the design manipulates, and the
  4.9x / 6.8x non-additivity it cites is D20's own POST-HOC observation; K15 counts comparisons, not values - every
  rank in the old sentences reproduces exactly; no pre-existing line of any file was edited; no torch/esm/
  thermompnn import; nothing frozen redefined; no outcome-word label used.
Verdict: PASS. Six corrected statements were written twice (standalone corrections file, then the one authorized
append), each computed from parsed variables, each ending with the mandated citation line; the append is
marker-guarded and prefix-verified; the AGENTS-vs-D22 tension is flagged inside the append itself.
Files created/modified:
- `scripts/152_phase2_diag4_corrections.py` (NEW; next free number after 151; stdlib only).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md` (NEW; 218 lines; sha256
  above).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (MODIFIED by the one authorized
  append-only, write-LAST addition: 1368 -> 1562 lines, 194 insertions / 0 deletions, prefix-verified).
- `docs/tasks/phase2-diagnostics-iv-shells/PHASE2_DIAG4_D22_FULL_OUTPUT.txt` (canonical), `..._D22_FULL_OUTPUT_RUN2.txt`,
  `..._D22_IDEMPOTENCY_CHECK.txt` (NEW).
- This log: this entry, then the mandated `## SUMMARY`.
Anything unexpected or worth flagging:
1. **AGENTS.md vs D22.** AGENTS §7 protects earlier logs; D22 mandates one append-only, write-LAST addition to the
   III log. Flagged rather than silently resolved: here, in the append header (III log line 1375), and in script
   152's docstring. No other earlier log was touched.
2. **Two line counts for the same append.** The script prints `appended 195 lines`; `wc -l` and
   `git diff --numstat` both say 194 (1368 -> 1562). The script counts list elements including a trailing empty
   element. Both numbers are reported; the file's actual growth is 194.
3. **Idempotency is content-level, not mtime-level.** Only WRITE 2 is marker-guarded; WRITE 1 rewrites the
   corrections file on every run (attempt 4 rewrote it byte-identically, sha unchanged, but its mtime changed).
4. `flag11_printed()` re-derives rule 11 from printed summaries (values, ranges, fractions, distances), not from
   raw draws; disclosed in the docstring and in output line 404.
5. Attempt 1's output no longer exists (overwritten) and attempt 2 was rolled back after a sha-verified restore.
   Both are recorded above so the run count is not hidden behind a single clean file.
6. Attempt 2's K16 fix was prose-only and post-hoc; it changed no number, gate or threshold (AGENTS §6).
7. `Elapsed 0.0s` is genuine: no resampling runs in this task.
---

## SUMMARY

### 1. READ THIS FIRST - D18

**Did D15's bootstrap reproduce Phase 1's CI? Phase 1's own CI: YES - D18-G2 PASS, exact-stream version applied
(not the Monte-Carlo fallback), `|diff|` lo = 0.000e+00, hi = 7.633e-17, point = 4.163e-17 (gate < 1e-9), IV log
line 93. D15's position-cluster CIs: NO - D18-G3 FAILED on all five row sets, so D15's twelve CIs are WITHDRAWN and
replaced by D18.5's corrected CIs.**

What was wrong (quoted source, IV log lines 132-154): in `scripts/144_phase2_diag3_farvariants.py`, `j` (line 474)
is the OCCURRENCE index within a draw slot (0,1,2,...), not the row offset within that cluster's rows, so
`idx = np.repeat(kept_base, cnt)[rep] + j` (line 477) gives ONE row per cluster occurrence instead of ALL of that
cluster's rows. Every draw therefore evaluates exactly nk rows (348-654) instead of the sampled clusters' full
complement (5,701-10,757). Evidence: `max|diff|` = 1.415e-01 (unrestricted), 1.680e-01, 1.836e-01, 1.665e-01,
1.452e-01 across the five row sets, and `draw 0 uses 10712 rows in the reference vs exactly 654 rows in script
144's routine` (IV log lines 122-126). The point-estimate identity gate cannot see it (line 486 never touches
`cnt`/`j`), which is how it survived Diagnostics III. The transcription is faithful (16 CIs replayed,
`max|diff|` = 4.571e-07 < 2e-06) and the pre-drawn variant matches the verbatim transcription exactly
(`0.000e+00`), so the defect is in script 144 itself. Script 144 was NOT edited; the fix is
`scripts/lib/phase2_diag4.py pos_cluster_boot_corrected`, which matches the reference (`max|diff| = 0.000e+00`,
gate < 1e-12) and reproduces Phase 1's published CI (0.000e+00 / 7.633e-17).

**The twelve corrected CIs (N_BOOT=10000, SEED=0, fresh rng per cell) beside the old ones** (parsed from D18's
output; quoted table at D22 output lines 123-136):

| cell | corrected CI | excludes zero | old D15 CI | old excluded zero |
|---|---|---|---|---|
| full S1 R = 0 | [-0.107547, -0.045843] | yes | [-0.110517, +0.052946] | no |
| full S1 R = 10 | [-0.110958, -0.047323] | yes | [-0.108943, +0.053475] | no |
| full S1 R = 20 | [-0.100593, -0.030938] | yes | [-0.106446, +0.077385] | no |
| full S1 R = 30 | [-0.067875, +0.012911] | **no** | [-0.126369, +0.088052] | no |
| full SEQ Rs = 25 | [-0.113697, -0.049861] | yes | [-0.115971, +0.055396] | no |
| full SEQ Rs = 50 | [-0.106218, -0.039834] | yes | [-0.107525, +0.069562] | no |
| H S1 R = 0 | [-0.114432, -0.046209] | yes | [-0.136966, +0.050697] | no |
| H S1 R = 10 | [-0.116434, -0.046886] | yes | [-0.133307, +0.060709] | no |
| H S1 R = 20 | [-0.102800, -0.025367] | yes | [-0.131090, +0.087967] | no |
| H S1 R = 30 | [-0.071605, +0.023131] | **no** | [-0.145818, +0.109530] | no |
| H SEQ Rs = 25 | [-0.123753, -0.052020] | yes | [-0.144621, +0.054462] | no |
| H SEQ Rs = 50 | [-0.114467, -0.039157] | yes | [-0.135943, +0.073553] | no |

Counts: **corrected 10/12 exclude zero, old 0/12** (D22 output lines 35-36; D22's G2i gate at output line 38
independently re-reads D18's output line 275 and the IV log's quote of it at line 181, and requires both to read
10/12 and 0/12). Corrected widths are 0.35-0.39x the old ones. Only full S1 R = 30 and
H S1 R = 30 still include zero. Also wrong in the old text: the explanation at III log line 834 - that Phase 1's CI
[-0.1173334458953319, -0.0595113844951173] excluded zero "only because it used a different bootstrap on the full
row set" - is false: on the SAME resolved rows the corrected CI [-0.107547, -0.045843] excludes zero, and D18-G4b
shows the corrected routine reproduces the published CI on the full rows. The R = 0 width difference was the
bootstrap defect, not the row set.

### 2. D19 - A222V's rho and `p_spec` at R = 10, 20, 30, both views, against matched-deletion ranges

(D19 output lines 281-299; rule-11 flags recomputed in D22 output lines 93-98 and 400.)

| view | R | k_R | rho | matched range | frac<= | frac>= | distance | **flag** | p_spec | vs frozen threshold (rule 10) |
|---|---|---|---|---|---|---|---|---|---|---|
| full | 10 | 23 | -0.079237139 | [-0.083258800, -0.069624333] | 0.2350 | 0.7650 | 0.004021661 | **INSIDE** | 0.037974684 | at or below 0.05 |
| full | 20 | 121 | -0.065947891 | [-0.091007274, -0.062448598] | 0.9200 | 0.0800 | 0.003499293 | **INSIDE** | 0.037974684 | at or below 0.05 |
| full | 30 | 247 | -0.027360127 | [-0.098275992, -0.047691236] | 1.0000 | 0.0000 | 0.020331109 | **OUTSIDE** | 0.063291139 | above 0.05 |
| H | 10 | 13 | -0.082101889 | [-0.086499760, -0.073431733] | 0.3200 | 0.6800 | 0.004397871 | **INSIDE** | 0.037974684 | at or below 0.1 |
| H | 20 | 86 | -0.063596629 | [-0.096713499, -0.064444959] | 0.9750 | 0.0250 | 0.000848330 | **MARGINAL** | 0.050632911 | at or below 0.1 |
| H | 30 | 172 | -0.024367374 | [-0.104682320, -0.054086245] | 1.0000 | 0.0000 | 0.029718871 | **OUTSIDE** | 0.101265823 | above 0.1 |

`p_spec` is INSIDE its own matched-deletion range in all 6 cells, and `k` likewise (INSIDE 6/6) - k and p_spec are
one statistic at two scales, so their agreeing flags are NOT two pieces of evidence (D19 output line 314).
Counts over the six cells: **rho INSIDE 3, OUTSIDE 2, MARGINAL 1**; p_spec INSIDE 6. The fall from R = 0 to R = 30
is **64.3217% (full) / 69.7045% (H)** - recomputed from D15's printed rhos and equal to D19's own prints to the
last digit (D22 output lines 89, 91) - i.e. about two-thirds of the magnitude, not "roughly halved".

### 3. D20 - the shell table (gradient, n = 67; each cell against its own size-matched range)

(D20 output lines 681-691; flags are D20's rule-11 labels; `drop %` is relative to that view's R = 0 gradient;
`frac of R0` is KEEP/R0.)

| view | shell | k_s | REMOVE drop | REMOVE flag | KEEP retained | KEEP flag |
|---|---|---|---|---|---|---|
| full | (0,10] | 23 | 1.29% | INSIDE | -0.1217 | INSIDE |
| full | (10,20] | 98 | 4.97% | INSIDE | -0.4131 | OUTSIDE |
| full | (20,30] | 126 | 2.41% | INSIDE | 0.2615 | OUTSIDE |
| full | (30,45] | 145 | -9.85% | OUTSIDE | 0.4861 | **OUTSIDE** |
| full | (45,inf) | 203 | **19.59%** | **OUTSIDE** | 0.0834 | OUTSIDE |
| H | (0,10] | 13 | 0.25% | INSIDE | 0.0999 | INSIDE |
| H | (10,20] | 73 | 6.28% | MARGINAL | -0.4172 | OUTSIDE |
| H | (20,30] | 86 | 3.04% | INSIDE | 0.1995 | OUTSIDE |
| H | (30,45] | 100 | -5.87% | OUTSIDE | 0.4294 | **OUTSIDE** |
| H | (45,inf) | 146 | **17.72%** | **OUTSIDE** | -0.0847 | OUTSIDE |

- **Most damaging removal:** shell (45,inf) on both views - 19.59% (full, k = 203) / 17.72% (H, k = 146), flag
  OUTSIDE on both, and below its own matched range (D22 G5g, line 76: value +0.561648209 < lo +0.632717749; H
  +0.566317470 < +0.612122119).
- **Shell that alone best preserves the signal:** (30,45] - 48.61% (full) / 42.94% (H) of the baseline gradient
  retained - yet itself flagged **OUTSIDE below** its own size-matched range on both views (+0.339539060 <
  +0.465522798; H +0.295560212 < +0.428702983), i.e. it preserves less than deleting the same number of random
  positions.
- **Views agree?** Yes on both cross-view answers (D20 output lines 768-769): most damaging removal = (45,inf) on
  both views, best preserving alone = (30,45] on both views. Gradient and rho, however, DISAGREE in both views
  (D20 output lines 745, 751, 759, 765: rho's most damaging is (20,30] full / (10,20] H and rho's best preserving
  is (20,30] on both), and all four top-two gradient separations OVERLAP their own matched ranges (IV log lines
  606, 612, 620, 626). D22's G5c cross-check of D20 (output line 72) reads `DIFFERS 4, OVERLAP 4, SAME 2`. For **rho**, no single-shell removal is OUTSIDE (all INSIDE except H (10,20] MARGINAL) - the
  anchor's magnitude is not attributable to any one shell's removal. `p_spec` by shell (D20 output 713-732) is
  compared only to the numeric thresholds: e.g. full REMOVE (45,inf) 0.012658228 at or below 0.05, full KEEP
  (45,inf) 0.721518987 above 0.05, H REMOVE (30,45] 0.151898734 above 0.1.
- The R = 30 union effect is **4.9x (full) / 6.8x (H)** the sum of the first three shells' individual drops - a
  **POST-HOC** observation (IV log lines 672-674), so "the signal lives within 30 A" cannot be attributed to any
  one shell.

### 4. D21 - equal-k: SEQ-k vs 3D-k vs RANDOM-k, both views

(D21 output lines 668-728; gradient drop = baseline - set, positive = fell.)

| view | slot (k) | SEQ-k drop | 3D-k drop | which is more destructive | flags vs RANDOM-k (gradient) | verdict |
|---|---|---|---|---|---|---|
| full | seq25 (50) | +0.003112840 | +0.008979348 | 3D (both metrics) | SEQ INSIDE, 3D INSIDE | **WITHDRAWN** |
| full | seq50 (100) | +0.017539659 | +0.022707772 | 3D (both metrics) | SEQ INSIDE, 3D INSIDE | **WITHDRAWN** |
| full | R20 (121) | +0.022388506 | +0.036376334 | DISAGREE (grad 3D, rho SEQ) | SEQ INSIDE, 3D MARGINAL | flagged, not decidable |
| full | R30 (247) | +0.323615684 | +0.297795071 | **SEQ (both metrics)** | SEQ OUTSIDE, 3D OUTSIDE | flagged, not decidable |
| H | seq25 (25) | -0.000897935 | +0.003930959 | 3D (both metrics) | SEQ INSIDE, 3D INSIDE | **WITHDRAWN** |
| H | seq50 (68) | +0.038271974 | +0.030829093 | DISAGREE (grad SEQ, rho 3D) | SEQ MARGINAL, 3D INSIDE | flagged, not decidable |
| H | R20 (86) | +0.050424025 | +0.047969670 | DISAGREE (grad SEQ, rho 3D) | SEQ MARGINAL, 3D MARGINAL | flagged, not decidable |
| H | R30 (172) | +0.381582361 | +0.446971965 | DISAGREE (grad 3D, rho SEQ) | SEQ OUTSIDE, 3D OUTSIDE | flagged, not decidable |

**Answer to "3D, not sequence?":** **SUPPORTED at 0 of 8 slots.** WITHDRAWN (both SEQ-k and 3D-k INSIDE the
RANDOM-k range) at 3 of 8 (full seq25, full seq50, H seq25); the remaining 5 are printed with their exact flags
and are not decidable by the pre-registered rule. rho and p_spec flags are in D21 output lines 678/684/690/696 and
704/710/716/722 (at R30 both views: rho SEQ and 3D both OUTSIDE; p_spec full both INSIDE, H SEQ MARGINAL /
3D INSIDE). **The two views give the same verdict at every slot: NO** - they differ at seq50 (full WITHDRAWN,
H not decidable). At the full R30 slot (k = 247) **SEQ-k is MORE destructive than 3D-k on both metrics**
(+0.323615684 vs +0.297795071 gradient; rho attenuation +0.058252020 vs +0.049325395), the opposite of D15's
unequal-k ordering, which compared k = 100 against k = 247.

### 5. D22 - corrections K11-K16

| K | old text (verbatim fragment) | real line(s), pre-append III log | recomputed fact | corrected statement (output line) |
|---|---|---|---|---|
| K11 | "A222V's position-cluster CI INCLUDES ZERO IN ALL TWELVE VARIANTS ON BOTH VIEWS" / "Twelve out of twelve" | 1250, 834, 1319, 1368 | D18-G3 FAILED on all five row sets -> those CIs are withdrawn; D18.5's corrected CIs exclude zero in **10/12** (widths 0.35-0.39x old); only full/H S1 R = 30 include | corrected CIs replace the withdrawn ones; rho is established (CI excluding zero) at R = 0, 10, 20 and both SEQ windows, still NOT at R = 30; the old "different bootstrap on the full row set" explanation is wrong (**138**) |
| K12 | "The gradient does NOT survive R = 20 A or R = 30 A" / "YES at R = 10, NO at R = 20 and R = 30" | 829, 1366, 1245 | full R = 20 `+0.662097177` vs bound `+0.663147261` (distance 0.001050084 <= 0.002 AND frac<= 0.0150 in [0.01, 0.05]); H `+0.640347202` vs `+0.642046793` (distance 0.001699591, frac<= 0.0250) -> **MARGINAL both**; R = 30 OUTSIDE both; R = 10 INSIDE both | R = 20 is **MARGINAL, not OUTSIDE** (D15 printed OUTSIDE); R = 30 IS the collapse; R = 10 nothing attributable (**168**) |
| K13 | "Removing |p-222| <= 50 in *sequence* is much more destructive per position than removing 30 A in *space*" | 832 (contradicted by 1243) | SEQ Rs = 50 removes **100** positions (595 - 495), drop 0.017539659 = **1.754e-04/pos**; 3D R = 30 removes **247**, drop 0.297795071 = **1.206e-03/pos** -> 3D is **6.87x** more destructive per position | the direction is backwards; total and per-position both say the 3D removal is the destructive one; D21 adds that at equal k the ordering is not stable (**201**, with D21 detail at 204) |
| K14 | "the first measurement in this project that separates ... and it resolves that separation against the long-range reading"; "Cannot be separated" vs "the two effects are separable" | 1368 (both phrases), 1310, 1317 | D15/D20 vary only the **target variants'** distance; the **background's** location is never manipulated or restricted; every same-site comparison is at d3_CA = 0; D21 SUPPORTED 0/8; D20 non-additivity 4.9x/6.8x is POST-HOC (IV log 672) | among target variants the gradient signal is concentrated in the near-222 region in 3D and in the far shell's removal, **and the design cannot say whether that is a property of position 222 itself or of its spatial neighbourhood** (**233**) |
| K15 | "six independent constructions, one answer" / "fifth independent construction to give the same same-site answer" | 1284, 1315, 1077 | all 18 Arm S members: position 222, `dist_222 = 0`, `d3_CA = 0.0` -> every distance term is a constant across all 19; shift coefs 0 / -0.726287 / -0.363298 / -0.418381 / -0.324445 (full), -0.774750 / -0.418766 / -0.464836 / -0.338456 (H); rank **2/19 in all 8 cells** (max&#124;recomputed - printed&#124; = 8.212e-07); 2/19 = **0.105263**; A222V's own shift value ranks **3 of 19** (interior) | **one comparison stable to shift adjustment, not six confirmations**; rank fraction, n = 19, not a test (**268**) |
| K16 | "A222V's own negative association is roughly halved by removing target variants within 30 A of 222" | 1248, 1314, 833 | fall **64.3217% (full) / 69.7045% (H)** (35.68% / 30.30% remains); R = 30 rho **OUTSIDE** its matched range both views (full -0.027360127 vs [-0.098275992, -0.047691236], frac<= 1.0000, distance 0.020331109; H -0.024367374 vs [-0.104682320, -0.054086245], distance 0.029718871); R = 10 INSIDE both; R = 20 full INSIDE, H MARGINAL | "roughly halved" **understates** it: about two-thirds; the fall **IS** attributable at R = 30, **not** at R = 10 nor at R = 20 full (H R = 20 MARGINAL) (**295**) |

Each section ends "Cite this, not the old sentence." (output lines 140/170/206/235/270/297).
**sha256 of `PHASE2_DIAGNOSTICS_III_LOG_CORRECTIONS.md` (218 lines):
`612c4565378a4c41d35e4bc203b9b3182dc43b457243b8232de0271f8bb69d23`.**

### 6. Plain two-sided statement

**Where the signal lives, by shell.** Removing the far shell (45,inf) is the single most damaging removal - the
gradient falls 19.59% (full, k = 203) and 17.72% (H, k = 146) of its R = 0 value, OUTSIDE below its own
size-matched range on both views. The shell that best preserves the signal on its own is (30,45] (48.61% / 42.94%
retained), and it too sits OUTSIDE *below* its own size-matched range - it preserves less than a random deletion of
the same size. Every near shell's individual removal - (0,10], (10,20], (20,30] - is INSIDE its own matched range
(sole exception: H (10,20] MARGINAL on the gradient), so no single near shell does what a same-size random
deletion would not. Removing everything within 30 A (the union of the first three shells) costs 4.9x (full) /
6.8x (H) the sum of the shells' individual drops - a POST-HOC observation (IV log 672-674) - and gradient and rho
orderings differ on 4 of 4 comparison lines with all four top-2 separations overlapping. So the near-30 A effect is
real but not attributable to any one shell.

**Does the anchor persist among distal variants? Partly, and it weakens monotonically.** A222V's rho keeps its sign
and, on the corrected CIs, excludes zero at R = 0, 10, 20 and both sequence windows on both views; only at R = 30
does the CI include zero (full [-0.067875, +0.012911], H [-0.071605, +0.023131]). Its magnitude nevertheless falls
**64.3217% (full) / 69.7045% (H)** between R = 0 and R = 30, and that R = 30 value sits **OUTSIDE** its own
matched-deletion range on both views (distances 0.020331109 / 0.029718871) - beyond what deleting the same 247 /
172 random positions produces. At 10 A the same rho is INSIDE on both views (nothing there is attributable to the
removed positions); at 20 A full is INSIDE and H is MARGINAL. `p_spec` is at or below its frozen threshold through
R = 20 on both views and above it at R = 30 (0.063291139 vs 0.05 full; 0.101265823 vs 0.10 H), and INSIDE its own
matched range in all six cells.

**What this design can and cannot say about position 222 vs its neighbourhood.** It can say where the signal lives
**among target variants**: near 222 in 3D, concentrated in the far shell's removal, and not attributable to any
single near shell. It cannot say whether that is a property of residue 222 itself or of its spatial neighbourhood,
because nothing here ever moves, restricts or controls a **background** - D15 and D20 only choose which target
variants are scored, every same-site comparison sits at exactly d3_CA = 0, and the equal-k test does not rescue the
distinction ("3D, not sequence" is SUPPORTED at 0 of 8 slots). Stated with the same directness whichever way it
falls: **position 222 versus the neighbourhood of 222 is UNDETERMINED by every cached measurement in this
project.** The old III-log sentence claiming this session "resolves that separation against the long-range
reading" is withdrawn (K14).

**What new data would settle what cached data cannot:** **backgrounds placed in the neighbourhood of 222** - same
shift machinery, but background *location* varied rather than target-variant distance - so that background location
is manipulated directly. That requires scoring and a new pre-registration before anything is run; it is explicitly
outside this session's scope (doc lines 314-318).

### 7. Every gate, PASS/FAIL, value - D18-G1 first

1. **D18-G1 (HARD, session-wide): PASS - 42/42 checks, 0 FAIL** (D18 output line 79; full table + GATE PASS at IV
   log lines 46-73), e.g. sha256 of `background_rho_table.csv` `e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796`,
   A222V rho re-derived -0.08811806424891734 vs target -0.088118064 (`|diff|` 2.489e-10 < 1e-09), k_R(full) =
   23/121/247, k_R(H) = 13/86/172, gradient 0.689454255 / 0.662097177 / 0.400678440 all within 1e-09.
2. **D18-G2 (HARD for D18): PASS** - Phase 1's own routine reproduces the published CI, `|diff|` 0.000e+00 /
   7.633e-17 / point 4.163e-17 (gate < 1e-9), IV log line 93; exact-stream version applied and stated (line 95).
3. **D18-G3 (HARD for D18): FAIL - 5 of 5 row sets FAIL** (`max|diff|` 1.415e-01, 1.680e-01, 1.836e-01, 1.665e-01,
   1.452e-01; gate 1e-12), D18 output lines 163-179 and 341-345, IV log lines 120-128. No threshold loosened, N not
   raised.
4. **Transcription-fidelity gate (rule 15): PASS** - 16 CIs replayed, `max|diff|` 4.571e-07 < 2e-06, cluster
   counts matched (IV log 115). **Pre-drawn identity (3c): PASS** - `max|diff|` = 0.000e+00 exactly, all five row
   sets (IV log 118).
5. **D18-G4a: PASS** - corrected vs reference on the same pre-drawn ids, all five, `max|diff| = 0.000e+00`
   (gate < 1e-12), IV log 158. **D18-G4b: PASS** - corrected routine reproduces Phase 1's published CI,
   `|diff|` 0.000e+00 / 7.633e-17 (gate < 1e-9), IV log 161.
6. **D18 overall: 67/72 PASS, 5 FAIL** (the five D18-G3 rows) - D18 output line 365. Identity checks on the
   corrected CIs (`|diff| = 0.000e+00`, gate < 1e-12) pass in all 12 cells (D18 output lines 352-363).
7. **D19: 28/28 PASS, 0 FAIL** (D19 output line 317); D19-G1 (HARD) = 24 reproduction gates PASS (IV log 283);
   D19-G2 doc targets pass; transform identity `max|fall_i - (1 - rho_i/rho(R0))| = 0.000e+00` (output line 276).
8. **D20: 23/23 PASS, 0 FAIL** (D20 output line 813); D20-G1 = 23/23 tolerance checks (line 88).
9. **D21: 37/37 PASS, 0 FAIL** (D21 output line 783); count/set gates 19/19 (line 121); gates before the analysis
   37/37 (line 219).
10. **D22: 85/85 PASS, 0 FAIL** (output line 402; gates-first verdict line 100), run before either write; repeated
    unchanged on the idempotency re-run (idempotency file line 100).

The only FAIL in the whole session is D18-G3 - the routine under test - and its pre-registered remediation's own
gates (G4a/G4b) pass.

### 8. Protection and scope confirmation

- **No protected file edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUM_SUMMARY_FINAL.md`, `AGENTS.md`,
  `PHASE2_PREREG.md`, the GB1 preregistration, `scripts/lib/phase2_diag.py`, `scripts/lib/phase2_diag3.py`,
  `scripts/lib/phase2_diag4.py`, every script numbered <= 147, and `docs/tasks/phase3a-*` / `phase3b-*` are
  untouched.
- **Earlier logs:** the only change to any earlier log is D22's one authorized append-only, write-LAST addition to
  `PHASE2_DIAGNOSTICS_III_LOG.md` (1368 -> 1562 lines, 194 insertions, **0 deletions**, prefix-verified, sha
  39d6ea68... -> 8f41f1fe...), with the AGENTS-vs-D22 tension flagged in the append header (line 1375) and in this
  log. No other earlier log was written.
- **Planning doc:** `PHASE2_DIAGNOSTICS_IV.md` carries only the D18.1 verification note recorded at IV log lines 43
  and 214-215 (a premise check that came back clean, replacing a wrong draft); no gate, target, tolerance or
  decision rule was changed by it.
- **Nothing committed:** no `git add`, `git commit` or `git push` was run; `git status --porcelain` shows no staged
  files. Among tracked files the worktree differs only by the four pre-existing modifications (`.gitignore`,
  `README.md`, `requirements.txt`, and the IV doc's disclosed note) plus the authorized III-log append; the new
  files are untracked (scripts 148-152, the four D18-D21 outputs, the three D22 outputs, this log, the corrections
  file).
- **No torch/esm/thermompnn import occurred:** scripts 148-152 and `scripts/lib/phase2_diag4.py` contain no
  `import torch` / `import esm` / `import thermompnn` / `from ...` line (grep exit 1), and script 152 imports
  stdlib only (`ast, hashlib, re, sys, time, pathlib`, lines 179-184). No model scoring ran in this session;
  `N_BOOT`/`N_PERM` are env-driven everywhere (smoke then full), and D22 itself does no resampling at all.
- **Labelling:** no result was labelled GENERIC, BEATS or INDETERMINATE anywhere; `p_spec` was compared only to
  the numeric 0.05 / 0.10 thresholds and reported as "at or below" or "above".

### 9. The single most important entry to read first

**IV log line 120** - "D18-G3 (HARD for D18) -- FAILED on all five row sets" (with the defect quoted verbatim at
lines 132-154). Everything else in this session follows from it: D15's twelve position-cluster CIs are withdrawn,
the corrections K11-K16 in the Diagnostics III log are required rather than optional, and the corrected values to
read next are the twelve CIs at **IV log line 166**.

