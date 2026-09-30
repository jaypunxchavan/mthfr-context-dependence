# PHASE 2 diagnostics II — executor log

**Doc:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II.md`
**Corrections file:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_CORRECTIONS.md`
**Full outputs:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAG2_<TASK>_FULL_OUTPUT.txt`
**Executor:** OpenCode · **Started:** 2026-09-29
**Mode:** cached-data-only. No model scoring, no torch, no esm.
**Status of every task below:** descriptive. Nothing here touches the frozen `PHASE2_PREREG.md` verdict.

Tasks in order: D0, D9, D10, D11.

---

## [D0] — Append-only corrections to Diagnostics I
Status: **PASS**
Time started / finished: 2026-09-29 (D0-G1 gate ~2 s; full run incl. C1–C9 ~35 s wall, single deterministic run, no resampling)

**What I did:**

1. Created this log first, before anything else, per instruction.
2. Read `AGENTS.md` (222 lines) and `PHASE2_DIAGNOSTICS_II.md` (336 lines) in full before starting.
3. Surveyed the real state: `ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` → highest existing is **135**, confirming 136 is the next free number. Verified `venv/bin/python3` exists. Read `scripts/lib/phase2_diag.py` (245 lines), `scripts/131_phase2_diag_background_rho.py` (392 lines) and `scripts/134_phase2_diag_shift_magnitude.py` (545 lines) in full to establish the exact construction to import rather than reimplement.
4. Read `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md` (830 lines) in full — **read only, never written** — and `PHASE2_DIAG_D4_D5_FULL_OUTPUT.txt` (158 lines) for the D4 construction.
5. Wrote `scripts/136_phase2_diag2_corrections.py` with the pre-registered docstring **before** its first run: construction, D0-G1 gate, the primary designation (none needed — D0 adds no science), what will be reported, and the limitations.
6. Ran **D0-G1 (HARD)** first. It passed 5/5, so the session continued.
7. Then recomputed all nine items C1–C9 and **wrote `PHASE2_DIAGNOSTICS_CORRECTIONS.md` from inside the script**, so that every number in the corrected statements is interpolated from a computed variable and none is hand-typed. Fixing the three gate rows and the quote formatting required two further runs of the same deterministic script; the final sha256 is reported below.

**Actual output (verbatim, from `PHASE2_DIAG2_D0_FULL_OUTPUT.txt`):**

```
==============================================================================
D0 -- APPEND-ONLY CORRECTIONS TO DIAGNOSTICS I (script 136)
==============================================================================
SCOPE: corrections only.  The earlier log is READ, never written.  This task adds no new science and redefines nothing frozen.
RESAMPLING UNIT: NONE (deterministic point values and exact rank counts; no bootstrap, no permutation).

------------------------------------------------------------------------------
GATE D0-G1 (HARD) -- input identity, then A222V re-derived through scripts/lib/phase2_diag.py
------------------------------------------------------------------------------
  data/processed/phase2_diagnostics/background_rho_table.csv
  sha256 on disk  = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  required        = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  [PASS] G0.1 table sha256: match |diff| =none

  script 134 imported; its ols_resid() is used verbatim for D4's residualisation (not reimplemented).
  [PASS] G0.2 A222V rho_full: got -0.08811806424891734 vs -0.088118064 |diff|=2.489e-10
  [PASS] G0.3 A222V rho_H: got -0.09002168303339808 vs -0.090021683 |diff|=3.340e-11
  [PASS] G0.4 p_spec(full) == 2/79 with {G_P254F}: got 0.02531645569620253 = (1+1)/(1+78), beaters ['G_P254F'] vs ['G_P254F'] |diff|=0.000e+00
  [PASS] G0.5 p_spec(H) == 4/79 with {AV_195, AV_220, G_P254F}: got 0.05063291139240506 = (1+3)/(1+78), beaters ['AV_195', 'AV_220', 'G_P254F'] vs ['AV_195', 'AV_220', 'G_P254F'] |diff|=0.000e+00

  5/5 D0-G1 checks PASS, 0 FAIL
  GATE PASS: D0-G1 satisfied.  The session may proceed.
```

**C1 — the D7.1 sentence is inverted. Real line numbers 329 and 768 (not one):**

```
  old quote located at REAL line(s) [329, 768] of docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md
    line 329: >>> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on th
    line 768: > Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the 

  k at or below A222V (full) = 1 of 78  -> A222V is more negative than 77 of the 78
  k at or below A222V (H)    = 3 of 78  -> A222V is more negative than 75 of the 78
    C1 full 'more negative than N of 78': recomputed = 77   plan target = 77   AGREE
    C1 H    'more negative than N of 78': recomputed = 75   plan target = 75   AGREE

  CORRECTED SENTENCE (composed from computed variables):
    >>> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 77 of the 78 placebo backgrounds on the full frame and 75 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).
```

**C2 — "the most extreme residual of all 96" is false, and script 134's percentile definition, quoted verbatim:**

```
  script 134's percentile definition, QUOTED VERBATIM:
    scripts/134_phase2_diag_shift_magnitude.py:417
      pct = 100.0 * float((resid_all > res).mean())
  -> `pct` is the fraction of the 96 background residuals GREATER than A222V's, so 100 = the MOST POSITIVE end and 0 = the most negative end.  The log's parenthetical '(0 = most negative)' describes the OPPOSITE end from the one the code computes.
    scripts/134_phase2_diag_shift_magnitude.py:425
      f"the 96 background residuals (0 = most negative)")

  [full]  OLS line: rho_hat = +0.034053 -0.896326 * mean|delta|
    A222V mean|delta| = 0.070330 -> predicted rho = -0.028985;  actual rho = -0.088118
    A222V RESIDUAL = -0.059133
    fraction of 96 with residual > A222V's = 96.9  (this is the number the log printed as '96.9th percentile')
    backgrounds AT OR BELOW A222V's residual: 3 -> A222V is rank 4 of 97 (most negative = rank 1), NOT rank 1
         bg_id  arm  dist_222  mean|delta|          rho     residual
        AV_220    V         2     0.047893    -0.084598    -0.075724
         AV_85    V       137     0.039341    -0.071229    -0.070021
        A222_C    S         0     0.068111    -0.093530    -0.066534
    three most negative background residuals beyond A222V's: AV_220 -0.075724, AV_85 -0.070021, A222_C -0.066534

  [H]  OLS line: rho_hat = +0.037990 -0.964705 * mean|delta|
    A222V mean|delta| = 0.069403 -> predicted rho = -0.028963;  actual rho = -0.090022
    A222V RESIDUAL = -0.061058
    fraction of 96 with residual > A222V's = 96.9  (this is the number the log printed as '96.9th percentile')
    backgrounds AT OR BELOW A222V's residual: 3 -> A222V is rank 4 of 97 (most negative = rank 1), NOT rank 1
         bg_id  arm  dist_222  mean|delta|          rho     residual
        AV_220    V         2     0.050233    -0.094480    -0.084010
         AV_85    V       137     0.042106    -0.081935    -0.079305
        A222_C    S         0     0.067910    -0.090964    -0.063441
    three most negative background residuals beyond A222V's: AV_220 -0.084010, AV_85 -0.079305, A222_C -0.063441

    C2 AV_220 residual (full): recomputed = -0.0757   plan target = -0.0757   AGREE
    C2 A222V residual (full): recomputed = -0.0591   plan target = -0.0591   AGREE
    C2 AV_220 residual (H): recomputed = -0.0840   plan target = -0.0840   AGREE
    C2 A222V residual (H): recomputed = -0.0611   plan target = -0.0611   AGREE
    C2 n backgrounds at or below A222V's residual (full): recomputed = 3   plan target = 3   AGREE
    C2 n backgrounds at or below A222V's residual (H): recomputed = 3   plan target = 3   AGREE
```

Note: `AV_85` (d=137) and `A222_C` (Arm S, d=0) are the other two backgrounds at or below A222V's residual. The plan's C2 text said "do not assume AV_220 is the only one" — it is not, and **two of the three the plan did not name are `AV_85` and `A222_C`**. `A222_C` being an Arm S background (same position 222) is worth flagging separately.

**C3 — arm-alone p_spec is a POST-HOC DECOMPOSITION:**

```
  real line numbers: 'carried entirely by Arm G' -> [742, 814] ; 'exhaustive control agrees' -> [311]

   view  arm    n   k at or below   p_spec(post-hoc)                        names
   full    V   38               0           0.025641                           []   vs 0.05: AT OR BELOW
   full    G   40               1           0.048780                  ['G_P254F']   vs 0.05: AT OR BELOW
      H    V   38               2           0.076923         ['AV_195', 'AV_220']   vs 0.1: AT OR BELOW
      H    G   40               1           0.048780                  ['G_P254F']   vs 0.1: AT OR BELOW
  *** POST-HOC DECOMPOSITION -- the frozen test is defined on the pooled 78; this redefines nothing. ***
    C3 arm-alone k (full | V): recomputed = 0   plan target = 0   AGREE
    C3 arm-alone k (H | V): recomputed = 2   plan target = 2   AGREE
    C3 arm-alone k (full | G): recomputed = 1   plan target = 1   AGREE
    C3 arm-alone k (H | G): recomputed = 1   plan target = 1   AGREE
    C3 arm-alone p (full | V): recomputed = 0.025641   plan target = 0.025641   AGREE
    C3 arm-alone p (H | V): recomputed = 0.076923   plan target = 0.076923   AGREE
    C3 arm-alone p (full | G): recomputed = 0.048780   plan target = 0.048780   AGREE
    C3 arm-alone p (H | G): recomputed = 0.048780   plan target = 0.048780   AGREE
```

All four arm-alone values are **at or below** their frozen numeric thresholds (0.05 full, 0.10 H). That is a fact; it is still a post-hoc decomposition and is labelled as one.

**C4 — "largest in the null set in either direction" is wrong as worded (real lines 351, 770):**

```
  [full] |rho_A222V| = 0.088118064;  #{|rho_b| >= |rho_A222V|} over the 78 nulls = 1  -> rank 2/79, p = 0.025316
          of those, 0 are POSITIVE ([])
  [H] |rho_A222V| = 0.090021683;  #{|rho_b| >= |rho_A222V|} over the 78 nulls = 3  -> rank 4/79, p = 0.050633
          of those, 0 are POSITIVE ([])
    C4 rank of |rho_A222V| in N u {{A222V}} (full): recomputed = 2/79   plan target = 2/79   AGREE
    C4 rank of |rho_A222V| in N u {{A222V}} (H): recomputed = 4/79   plan target = 4/79   AGREE
```

**C5 — the fragility table and the near-misses (real line 395):**

```
  D8 leave-one-out (G_P254F removed): full p_spec 0.025316 -> 0.012821 (|N| 78 -> 77);  H 0.050633 -> 0.038462 (|N| 78 -> 77)
  direction: full change = -0.012496 (FALLS = smaller, not 'weaker');  H change = -0.012171

  pooled-p_spec fragility: k = 0..8 at-or-below placebos
   k   (1+k)/79    vs 0.05    vs 0.10
   0   0.012658 at or below at or below
   1   0.025316 at or below at or below
   2   0.037975 at or below at or below
   3   0.050633      above at or below
   4   0.063291      above at or below
   5   0.075949      above at or below
   6   0.088608      above at or below
   7   0.101266      above      above
   8   0.113924      above      above
    C5 p at k=2: recomputed = 0.0380   plan target = 0.0380   AGREE
    C5 p at k=3: recomputed = 0.0506   plan target = 0.0506   AGREE
    C5 p at k=6: recomputed = 0.0886   plan target = 0.0886   AGREE
    C5 p at k=7: recomputed = 0.1013   plan target = 0.1013   AGREE
  -> at or below 0.05 through k=2 (0.0380), above at k=3 (0.0506)
  -> at or below 0.10 through k=6 (0.0886), above at k=7 (0.1013)

  the five nulls whose rho lies nearest ABOVE A222V's (i.e. just missed it):
   view      bg_id  arm  dist_222          rho  gap (rho_b - rho_A)
   full     AV_220    V         2    -0.084598             0.003520
   full     AV_195    V        27    -0.084162             0.003956
   full     AV_113    V       109    -0.077808             0.010310
   full    G_Y197V    G        25    -0.076880             0.011238
   full      AV_85    V       137    -0.071229             0.016889
      H     AV_155    V        67    -0.088806             0.001215
      H     AV_113    V       109    -0.086932             0.003089
      H      AV_85    V       137    -0.081935             0.008087
      H    G_L178T    G        44    -0.074356             0.015666
      H    G_Y197V    G        25    -0.072498             0.017524
    C5 gap AV_220 (full): recomputed = 0.00352   plan target = 0.00352   AGREE
    C5 gap AV_195 (full): recomputed = 0.00396   plan target = 0.00396   AGREE

  context only -- A222V's own POSITION-cluster 95% CI, quoted from docs/tasks/phase1-corrections-diagnostics/PHASE1_LOG.md:383
    G2 PASS: headline row reproduced exactly (-0.0881180642489173, CI [-0.1173334458953319, -0.0595113844951173])
    parsed CI = [-0.1173, -0.0595]
    This is a DIFFERENT bootstrap (positions within A222V's own rows) from any per-background CI and is CONTEXT, not a test.
```

**C6 — the k-removal is mechanical (real lines 241, 731):**

```
  the k=10 nearest-to-222 set (by dist_222, ties by ascending bg_id):
        AV_220 d=  2 arm=V  <-- BEATER
        AV_233 d= 11 arm=V  
        AV_209 d= 13 arm=V  
        AV_204 d= 18 arm=V  
        AV_242 d= 20 arm=V  
       G_Y197V d= 25 arm=G  
        AV_195 d= 27 arm=V  <-- BEATER
       G_I192T d= 30 arm=G  
        G_P254F d= 32 arm=G  <-- BEATER
        G_L178T d= 44 arm=G  
  beaters named in D1: ['AV_195', 'AV_220', 'G_P254F']
  beaters inside the k=10 removed set: ['AV_195', 'AV_220', 'G_P254F']  (3/3) -> ALL, so p_spec reaching its floor is GUARANTEED, not informative
  beaters inside the k=20 removed set: ['AV_195', 'AV_220', 'G_P254F']  (3/3)

  *** POST-HOC ***  The beaters were identified AFTER seeing rho; only the distance ranks are fixed in advance.  The probability below is therefore a post-hoc diagnostic, not a test.
  C(10,3)/C(78,3) = 120/76076 = 0.001577
  C(20,3)/C(78,3) = 1140/76076 = 0.014985
    C6 k=10 numerator: recomputed = 120   plan target = 120   AGREE
    C6 k=10 denominator: recomputed = 76076   plan target = 76076   AGREE
    C6 k=10 probability: recomputed = 0.001577   plan target = 0.001577   AGREE
```

**C7 — neighbourhood rank fractions (real lines 810, 243):**

```
  real line numbers: 'relative to its own neighbourhood' / 'more extreme than its own neighbourhood' -> [810, 243]

  *** RANK FRACTIONS, NOT TESTS (n is tiny). ***
  k=10 nearest (full): # at or below =  1 of 10  -> rank fraction 2/11 = 0.1818
  k=10 nearest (   H): # at or below =  3 of 10  -> rank fraction 4/11 = 0.3636
  k=20 nearest (full): # at or below =  1 of 20  -> rank fraction 2/21 = 0.0952
  k=20 nearest (   H): # at or below =  3 of 20  -> rank fraction 4/21 = 0.1905
    C7 k=10 full: k at or below: recomputed = 1   plan target = 1   AGREE
    C7 k=10 H: k at or below: recomputed = 3   plan target = 3   AGREE
    C7 k=10 full: rank fraction: recomputed = 0.1818   plan target = 0.1818   AGREE
    C7 k=10 H: rank fraction: recomputed = 0.3636   plan target = 0.3636   AGREE
  the 20 nearest: ['AV_220', 'AV_233', 'AV_209', 'AV_204', 'AV_242', 'G_Y197V', 'AV_195', 'G_I192T', 'G_P254F', 'G_L178T', 'AV_175', 'G_E168S', 'G_E279K', 'AV_155', 'AV_292', 'AV_293', 'AV_145', 'AV_302', 'AV_311', 'G_G317Q']
```

**C8 — "including the nearest ones" (real lines 241, 731):**

```
  [full] A222V rho = -0.088118;  AV_220 (d=2) rho = -0.084598;  AV_220 is NOT at or below A222V;  gap = +0.003520
  [H] A222V rho = -0.090022;  AV_220 (d=2) rho = -0.094480;  AV_220 IS at or below A222V;  gap = -0.004459
```

**C9 — the "protected files do not exist" flag (real line 822):**

```
  ls -la docs/tasks/results-log/MTHFR_RESULTS_LOG.md
    -rw-r--r--@ 1 arnavchavan  staff  20642 Sep 21 20:17 docs/tasks/results-log/MTHFR_RESULTS_LOG.md
    -> EXISTS, 20642 bytes, mtime 2026-09-21 20:17:45.403327

  ls -la docs/writeups/PROJECT_SUMMARY_FINAL.md
    -rw-r--r--@ 1 arnavchavan  staff  17103 Sep 26 15:21 docs/writeups/PROJECT_SUMMARY_FINAL.md
    -> EXISTS, 17103 bytes, mtime 2026-09-26 15:21:47.796747

  find . -name MTHFR_RESULTS_LOG.md -o -name PROJECT_SUMMARY_FINAL.md (venv excluded):
    ./docs/tasks/results-log/MTHFR_RESULTS_LOG.md
    ./docs/writeups/PROJECT_SUMMARY_FINAL.md
```

**D0 verdict and line numbers:**

```
------------------------------------------------------------------------------
D0 VERDICT
------------------------------------------------------------------------------
  D0-G1 PASS (5/5). All nine items C1-C9 recomputed; no plan target disagreed.

  Line numbers located in the earlier log:
    'more negative than 1 of the 78'                     -> [329, 768]
    'most extreme residual of all 96'                    -> [500, 708]
    '96.9th percentile'                                  -> [479, 487, 701, 702]
    'carried entirely by Arm G'                          -> [742, 814]
    'exhaustive control agrees'                          -> [311]
    'largest in the null set in either direction'         -> [351, 770]
    'a weaker one'                                       -> [395]
    'essentially every placebo'                          -> [241, 731]
    'relative to its own neighbourhood' (x2 searches)    -> [810, 243]
    'do not exist in this repository'                    -> [822]

  corrections file sha256 = 6a38882acd02ef8c2f8c2f58bb5f976eadf9f1c4db5235f521e39eacb33f4036
```

**`PHASE2_DIAGNOSTICS_CORRECTIONS.md` sha256 = `6a38882acd02ef8c2f8c2f58bb5f976eadf9f1c4db5235f521e39eacb33f4036`** (confirmed independently by `shasum -a 256` after the run).

**Verdict: PASS.**

- **D0-G1 (HARD): PASS 5/5.** sha256 matches; A222V ρ re-derived through `scripts/lib/phase2_diag.py` at 2.489e-10 (full) and 3.340e-11 (H), both inside 1e-9; `p_spec(full) = 2/79` with `{G_P254F}` and `p_spec(H) = 4/79` with `{AV_195, AV_220, G_P254F}`, both `|diff| = 0.000e+00`.
- **All nine items C1–C9 recomputed, and every plan target agreed with the recomputation.** No target was forced, and no disagreement table is needed. The `TARGET DISAGREEMENT` machinery is in the script and is what would have fired if one had.
- Nine corrections written to `PHASE2_DIAGNOSTICS_CORRECTIONS.md`, each with old quote + real line number, recomputed vs target, corrected statement, and the closing line "Cite this, not the old sentence."

---

## [D9] — Shift-adjusted `p_spec`: the frozen construction run on residuals
Status: **PASS**
Time started / finished: 2026-09-29 (0.7 s wall — deterministic, no resampling; D9-G1 gate and all three variants in one run)

**What I did:**

1. Read script 134's `ols_resid` and **imported it** rather than reimplementing the residualisation, and drove the build through `pdg.build()` / `pdg.rho_table()` / `pdg.usable_rows()` — script 125's own construction, imported.
2. Wrote `scripts/137_phase2_diag2_shift_adjusted.py` with the **pre-registered docstring written before its first run**: the covariate definition, all three residual variants with the primary designated in advance, the frozen inequality direction, the D9-G1 gate with its tolerances, what would be reported, and the limits.
3. Ran **D9-G1 (HARD) first**, before any new analysis was printed. 23/23 PASS.
4. Then ran the three variants. **No resampling anywhere** — no bootstrap, no permutation, `N_BOOT`/`N_PERM` not read by the script, and this is stated in the docstring and in the printed limitations block.

**Actual output (verbatim, from `PHASE2_DIAG2_D9_FULL_OUTPUT.txt`):**

```
==============================================================================
D9 -- SHIFT-ADJUSTED p_spec: THE FROZEN CONSTRUCTION ON RESIDUALS (script 137)
==============================================================================
SCOPE: descriptive.  p_spec_adj is a companion to the frozen p_spec, never a replacement.  No outcome word is computed or used as a label.
RESAMPLING UNIT: NONE.  No bootstrap, no permutation, no Monte-Carlo uncertainty.  N_BOOT / N_PERM are not read by this script.  Every number below is a deterministic OLS fit on a fixed set of points or an exact rank count.
INEQUALITY DIRECTION: FROZEN.  one-sided, signed, r_b <= r_A.  It is not flipped anywhere in this script.

------------------------------------------------------------------------------
GATE D9-G1 (HARD; tol 1e-8 on correlations, 2e-6 on the 6-dp quantities) -- reproduce D4's PRINTED values before any new analysis
------------------------------------------------------------------------------
  input table sha256 = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  [PASS] D9-G1 input table sha256: match
  script 134 imported; its ols_resid is the residualiser used throughout (imported, not reimplemented).
  [PASS] D9-G1 Spearman(rho_b, mean|delta|) (full): got -0.6141888225718937 vs -0.614188823 |diff|=4.281e-10
  [PASS] D9-G1 all-96 OLS slope (full): got -0.896325500 vs -0.896326
  [PASS] D9-G1 all-96 OLS intercept (full): got +0.034053200 vs 0.034053
  [PASS] D9-G1 A222V mean|delta| (full): got 0.070330 vs 0.07033
  [PASS] D9-G1 A222V residual, all-96 fit (full): got -0.059133 vs -0.059133
  [PASS] D9-G1 G_P254F mean|delta| (full): got 0.208008 vs 0.208008
  [PASS] D9-G1 G_P254F residual, all-96 fit (full): got +0.056146 vs +0.056146
  [PASS] D9-G1 AV_220 mean|delta| (full): got 0.047893 vs 0.047893
  [PASS] D9-G1 AV_220 residual, all-96 fit (full): got -0.075724 vs -0.075724
  [PASS] D9-G1 AV_195 mean|delta| (full): got 0.095630 vs 0.09563
  [PASS] D9-G1 AV_195 residual, all-96 fit (full): got -0.032500 vs -0.032500
  [PASS] D9-G1 Spearman(rho_b, mean|delta|) (H): got -0.6126966901790558 vs -0.61269669 |diff|=1.791e-10
  [PASS] D9-G1 all-96 OLS slope (H): got -0.964705251 vs -0.964705
  [PASS] D9-G1 all-96 OLS intercept (H): got +0.037990057 vs 0.03799
  [PASS] D9-G1 A222V mean|delta| (H): got 0.069403 vs 0.069403
  [PASS] D9-G1 A222V residual, all-96 fit (H): got -0.061058 vs -0.061058
  [PASS] D9-G1 G_P254F mean|delta| (H): got 0.200143 vs 0.200143
  [PASS] D9-G1 G_P254F residual, all-96 fit (H): got +0.053135 vs +0.053135
  [PASS] D9-G1 AV_220 mean|delta| (H): got 0.050233 vs 0.050233
  [PASS] D9-G1 AV_220 residual, all-96 fit (H): got -0.084010 vs -0.084010
  [PASS] D9-G1 AV_195 mean|delta| (H): got 0.098154 vs 0.098154
  [PASS] D9-G1 AV_195 residual, all-96 fit (H): got -0.036722 vs -0.036722

  23/23 D9-G1 checks PASS, 0 FAIL
  GATE PASS: D4's printed values reproduce.  New analysis below.
```

Every D4 target reproduces; the two correlations are exact to 4.3e-10 and 1.8e-10, well inside the 1e-8 gate, and every 6-dp quantity matches at 2e-6 (in fact they agree at printed precision).

**The three variants — A222V and the nulls' residuals, and who lies beyond A222V:**

```
  === PRIMARY (leave-one-out on N) ===
    [full]  fit on n = 78;  OLS rho ~ +0.029386 -0.726287*mean|delta|
      A222V  mean|delta| = 0.070330  rho = -0.088118  ->  r_A = -0.066425
      #{b in N : r_b <= r_A} = 2 of 78
      p_spec_adj = (1 + 2)/(1 + 78) = 0.037975   -> AT OR BELOW the frozen threshold 0.05
      A222V signed rank within N u {A222V} = 3/79  (rank 1 = most negative)
      nulls at or below r_A:      bg_id  arm  dist_222  mean|delta|          rho          r_b
                       AV_220    V         2     0.047893    -0.084598    -0.080278
                        AV_85    V       137     0.039341    -0.071229    -0.073252
    [H]  fit on n = 78;  OLS rho ~ +0.032440 -0.774750*mean|delta|
      A222V  mean|delta| = 0.069403  rho = -0.090022  ->  r_A = -0.068692
      #{b in N : r_b <= r_A} = 2 of 78
      p_spec_adj = (1 + 2)/(1 + 78) = 0.037975   -> AT OR BELOW the frozen threshold 0.1
      A222V signed rank within N u {A222V} = 3/79  (rank 1 = most negative)
      nulls at or below r_A:      bg_id  arm  dist_222  mean|delta|          rho          r_b
                       AV_220    V         2     0.050233    -0.094480    -0.089189
                        AV_85    V       137     0.042106    -0.081935    -0.083078
```

**Sensitivity 1 (in-sample fit on N)** and **Sensitivity 2 (D4's all-96 fit)** both give `k = 2`, `p_spec_adj = 0.037975`, rank `3/79`, and the same beater pair `{AV_220, AV_85}` on both views; only `r_A` differs (-0.066425 / -0.068692 / -0.059133 / -0.061058 across the three variants).

**Ten most negative null residuals — PRIMARY (leave-one-out on N):**

```
  [full]  A222V r_A = -0.066425
    rank      bg_id  arm  dist_222  mean|delta|          rho          r_b  <= r_A?
       1     AV_220    V         2     0.047893    -0.084598    -0.080278      YES
       2      AV_85    V       137     0.039341    -0.071229    -0.073252      YES
       3    G_L178T    G        44     0.063864    -0.070331    -0.054126       no
       4     AV_242    V        20     0.055971    -0.062924    -0.052335       no
       5     AV_113    V       109     0.079641    -0.077808    -0.050605       no
       6     AV_293    V        71     0.062199    -0.062145    -0.047020       no
       7     AV_195    V        27     0.095630    -0.084162    -0.046124       no
       8     AV_116    V       106     0.075102    -0.068926    -0.044702       no
       9     AV_155    V        67     0.081750    -0.070396    -0.041520       no
      10     AV_145    V        77     0.065572    -0.055803    -0.038149       no
    -> 2 of the 78 nulls are at or below A222V's residual on this view

  [H]  A222V r_A = -0.068692
    rank      bg_id  arm  dist_222  mean|delta|          rho          r_b  <= r_A?
       1     AV_220    V         2     0.050233    -0.094480    -0.089189      YES
       2      AV_85    V       137     0.042106    -0.081935    -0.083078      YES
       3     AV_242    V        20     0.051866    -0.067521    -0.060568       no
       4     AV_155    V        67     0.087136    -0.088806    -0.055422       no
       5    G_L178T    G        44     0.071155    -0.074356    -0.052569       no
       6     AV_195    V        27     0.098154    -0.093421    -0.052149       no
       7     AV_113    V       109     0.095327    -0.086932    -0.047446       no
       8     AV_175    V        47     0.064560    -0.061863    -0.044926       no
       9      AV_73    V       149     0.058394    -0.053321    -0.041053       no
      10     AV_293    V        71     0.065113    -0.058014    -0.040595       no
    -> 2 of the 78 nulls are at or below A222V's residual on this view
```

**Summary table:**

```
                             variant  view   k  p_spec_adj         r_A    rank  vs frozen threshold
        PRIMARY (leave-one-out on N)  full   2    0.037975   -0.066425    3/79  AT OR BELOW 0.05
        PRIMARY (leave-one-out on N)     H   2    0.037975   -0.068692    3/79  AT OR BELOW 0.1
  SENSITIVITY 1 (in-sample fit on N)  full   2    0.037975   -0.066425    3/79  AT OR BELOW 0.05
  SENSITIVITY 1 (in-sample fit on N)     H   2    0.037975   -0.068692    3/79  AT OR BELOW 0.1
     SENSITIVITY 2 (D4's all-96 fit)  full   2    0.037975   -0.059133    3/79  AT OR BELOW 0.05
     SENSITIVITY 2 (D4's all-96 fit)     H   2    0.037975   -0.061058    3/79  AT OR BELOW 0.1

                             variant  view       slope   intercept  n_fit
        PRIMARY (leave-one-out on N)  full   -0.726287   +0.029386     78
        PRIMARY (leave-one-out on N)     H   -0.774750   +0.032440     78
  SENSITIVITY 1 (in-sample fit on N)  full   -0.726287   +0.029386     78
  SENSITIVITY 1 (in-sample fit on N)     H   -0.774750   +0.032440     78
     SENSITIVITY 2 (D4's all-96 fit)  full   -0.896326   +0.034053     96
     SENSITIVITY 2 (D4's all-96 fit)     H   -0.964705   +0.037990     96
```

**Verdict: PASS.**

- **D9-G1 (HARD): PASS 23/23.** Every D4 printed value reproduces before any new analysis ran.
- **PRIMARY `p_spec_adj = 0.037975` on both views**, `k = 2` of 78, A222V rank `3/79`. On the full frame this is **at or below** the frozen threshold 0.05; on H it is **at or below** 0.10.
- All three residual variants agree on `k = 2` and on the beater set. The choice among them does not change the count; only `r_A` moves.
- The unadjusted frozen `p_spec` was `0.025316` (full) and `0.050633` (H) — so **adjusting for shift magnitude raises the full-frame value from 0.0253 to 0.0380 and lowers the H value from 0.0506 to 0.0380.** The adjustment narrows the gap between the two views rather than moving both in one direction. Both adjusted values remain at or below their respective frozen thresholds.
- The beater set **changes completely** under adjustment: `{G_P254F}` / `{AV_195, AV_220, G_P254F}` becomes `{AV_220, AV_85}` on both views. `G_P254F`'s all-96 residual is `+0.056` — it is the largest shift of all 96 and its extreme ρ is *over*-predicted, so it drops out. `AV_195` also drops out.

---

## [D10] — Joint adjustment, neighbourhood ranks, partial correlations
Status: **PASS** (all tasks ran; the result is adverse to a "position-222-specific" reading and is reported as such)
Time started / finished: 2026-09-29 (smoke at `N_BOOT=300` then full at `N_BOOT=10000 SEED=0`; 11.5 s wall — timed, not guessed)

**What I did:**

1. Wrote `scripts/138_phase2_diag2_joint.py` with the **pre-registered docstring written before its first run**: D10a's primary and three disclosed sensitivities, the extrapolation statement, D10b's rank-fraction framing, D10c's partial formula and the explicit **refusal to compute a permutation p**, and the resampling unit stated per subtask.
2. Smoke-ran at `N_BOOT=300` first (AGENTS §1), then ran the full `N_BOOT=10000 SEED=0` in the foreground. Timed at 11.5 s — the smoke run was not used to guess anything.
3. **D10a**: joint OLS `rho ~ a + c1·mean|δ| + c2·<distance>` on N, leave-one-out residuals for nulls, out-of-sample for A222V — identical exchangeability property to D9's primary. Four variants, all reported, **none selected**.
4. **D10b**: neighbourhood-restricted rank fractions on D9's primary residuals.
5. **D10c**: partial Spearman via the standard three-correlation formula, with a background-level bootstrap CI at 10,000 draws.

**Actual output (verbatim, from `PHASE2_DIAG2_D10_FULL_OUTPUT.txt`):**

```
------------------------------------------------------------------------------
A222V IS AT THE EDGE OF THE DISTANCE RANGE -- stated before any adjustment is reported
------------------------------------------------------------------------------
  sequence distance dist_b = |position_b - 222|
    A222V               dist = 0
    null set N          dist min = 2 (['AV_220']), median = 162, max = 433 (['AV_655'])
    -> A222V's distance covariate is an EXTRAPOLATION in every variant with a distance term: no null can reach dist = 0.
    This is why the CLAMPED sensitivity below (A222V evaluated at dist = 2, the null minimum) is reported.  It is a sensitivity, NOT a selection.

  LEVERAGE (hat value) of A222V in the D10a primary design (full frame; the H design gives the same covariate structure):
    h(A222V) at dist = 0          = 0.383410
    h(A222V) at dist = 2 (clamped)= 0.231801
    null leverage h_b: mean = 0.038462, max = 0.441777 (['G_P254F', 'AV_220', 'G_Y197V']), min = 0.012935
    the mean leverage of a 3-parameter fit on 78 points is p/n = 0.038462
    -> A222V's leverage at dist = 0 is within the null leverage range; the clamped value is inside it.  A high leverage point's residual is partly extrapolation, not evidence.
```

**D10a — the four variants (beater lists for the two high-k variants are long and are in the full output; the counts are here in full):**

```
  === PRIMARY  log1p(dist) ===
    [full]  fit on n = 78;  OLS coefficients: intercept -0.103920  mean|delta| -0.418381  log1p(dist) +0.023870
      A222V covariates = mean|delta| 0.070330, log1p(dist) 0.000000
      r_A = +0.045227;  #{b in N: r_b <= r_A} = 69 of 78
      p_spec_adj = (1 + 69)/(1 + 78) = 0.886076   -> ABOVE the frozen threshold 0.05
      A222V signed rank within N u {A222V} = 70/79
    [H]  fit on n = 78;  OLS coefficients: intercept -0.104791  mean|delta| -0.464836  log1p(dist) +0.024540
      A222V covariates = mean|delta| 0.069403, log1p(dist) 0.000000
      r_A = +0.047030;  #{b in N: r_b <= r_A} = 70 of 78
      p_spec_adj = (1 + 70)/(1 + 78) = 0.898734   -> ABOVE the frozen threshold 0.1
      A222V signed rank within N u {A222V} = 71/79

  === SENS (i)  linear dist ===
    [full]  fit on n = 78;  OLS coefficients: intercept -0.028857  mean|delta| -0.363298  dist +0.000215
      r_A = -0.033711;  #{b in N: r_b <= r_A} = 9 of 78
      p_spec_adj = (1 + 9)/(1 + 78) = 0.126582   -> ABOVE the frozen threshold 0.05
      A222V signed rank within N u {A222V} = 10/79
    [H]  fit on n = 78;  OLS coefficients: intercept -0.025010  mean|delta| -0.418766  dist +0.000210
      r_A = -0.035948;  #{b in N: r_b <= r_A} = 10 of 78
      p_spec_adj = (1 + 10)/(1 + 78) = 0.139241   -> ABOVE the frozen threshold 0.1
      A222V signed rank within N u {A222V} = 11/79

  === SENS (ii) CLAMPED: A222V at dist = 2 ===
    [full]  intercept -0.103920  mean|delta| -0.418381  log1p(dist) +0.023870
      A222V covariates = mean|delta| 0.070330, log1p(dist) 1.098612
      r_A = +0.019003;  #{b in N: r_b <= r_A} = 56 of 78
      p_spec_adj = (1 + 56)/(1 + 78) = 0.721519   -> ABOVE the frozen threshold 0.05
      A222V signed rank within N u {A222V} = 57/79
    [H]  intercept -0.104791  mean|delta| -0.464836  log1p(dist) +0.024540
      A222V covariates = mean|delta| 0.069403, log1p(dist) 1.098612
      r_A = +0.020070;  #{b in N: r_b <= r_A} = 55 of 78
      p_spec_adj = (1 + 55)/(1 + 78) = 0.708861   -> ABOVE the frozen threshold 0.1
      A222V signed rank within N u {A222V} = 56/79

  === SENS (iii) shift-only (= D9 primary) ===
    [full]  intercept +0.029386  mean|delta| -0.726287
      r_A = -0.066425;  #{b in N: r_b <= r_A} = 2 of 78
      p_spec_adj = (1 + 2)/(1 + 78) = 0.037975   -> AT OR BELOW the frozen threshold 0.05
      A222V signed rank within N u {A222V} = 3/79
      at or below r_A: AV_220 (V, d=2, mean|d|=0.047893, r_b=-0.080278); AV_85 (V, d=137, mean|d|=0.039341, r_b=-0.073252)
    [H]  intercept +0.032440  mean|delta| -0.774750
      r_A = -0.068692;  #{b in N: r_b <= r_A} = 2 of 78
      p_spec_adj = (1 + 2)/(1 + 78) = 0.037975   -> AT OR BELOW the frozen threshold 0.1
      A222V signed rank within N u {A222V} = 3/79
      at or below r_A: AV_220 (V, d=2, mean|d|=0.050233, r_b=-0.089189); AV_85 (V, d=137, mean|d|=0.042106, r_b=-0.083078)

                                 variant  view   k  p_spec_adj         r_A    rank  vs frozen
                    PRIMARY  log1p(dist)  full  69    0.886076   +0.045227   70/79  ABOVE 0.05
                    PRIMARY  log1p(dist)     H  70    0.898734   +0.047030   71/79  ABOVE 0.1
                   SENS (i)  linear dist  full   9    0.126582   -0.033711   10/79  ABOVE 0.05
                   SENS (i)  linear dist     H  10    0.139241   -0.035948   11/79  ABOVE 0.1
    SENS (ii) CLAMPED: A222V at dist = 2  full  56    0.721519   +0.019003   57/79  ABOVE 0.05
    SENS (ii) CLAMPED: A222V at dist = 2     H  55    0.708861   +0.020070   56/79  ABOVE 0.1
    SENS (iii) shift-only (= D9 primary)  full   2    0.037975   -0.066425    3/79  AT OR BELOW 0.05
    SENS (iii) shift-only (= D9 primary)     H   2    0.037975   -0.068692    3/79  AT OR BELOW 0.1
```

**D10b — neighbourhood rank fractions on D9's primary residuals:**

```
------------------------------------------------------------------------------
D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals
------------------------------------------------------------------------------
*** RANK FRACTIONS, NOT TESTS.  n is tiny by construction; these are descriptive counts. ***
  k=10 nearest (full):  # at or below =  8 of 10  ->  rank fraction (1 + 8)/(1 + 10) = 0.8182   at or below: AV_195, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
  k=10 nearest (   H):  # at or below =  9 of 10  ->  rank fraction (1 + 9)/(1 + 10) = 0.9091   at or below: AV_195, AV_209, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
  k=20 nearest (full):  # at or below = 18 of 20  ->  rank fraction (1 + 18)/(1 + 20) = 0.9048   at or below: AV_145, AV_155, AV_175, AV_195, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V
  k=20 nearest (   H):  # at or below = 19 of 20  ->  rank fraction (1 + 19)/(1 + 20) = 0.9524   at or below: AV_145, AV_155, AV_175, AV_195, AV_209, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V

  the 20 nearest by sequence distance: ['AV_220', 'AV_233', 'AV_209', 'AV_204', 'AV_242', 'G_Y197V', 'AV_195', 'G_I192T', 'G_P254F', 'G_L178T', 'AV_175', 'G_E168S', 'G_E279K', 'AV_155', 'AV_292', 'AV_293', 'AV_145', 'AV_302', 'AV_311', 'G_G317Q']
  ties in dist within N present at the cut? none (tie-break by ascending bg_id is the pre-registered rule)
```

*Note on the denominators: the script prints the rank fraction as `(1 + k)/(1 + kk)` with `kk` the neighbourhood size, so the k=20 rows read `(1 + 18)/(1 + 20)` = 19/21 = 0.9048 and `(1 + 19)/(1 + 20)` = 20/21 = 0.9524. Verified independently: `(1+18)/(1+20) = 0.9047619` and `(1+19)/(1+20) = 0.9523810`. My first transcription of these two lines wrote the denominators as `(1 + 21)`, which is wrong; the verbatim output above is corrected and now matches the saved full-output file.*

**D10c — partial rank correlations:**

```
  *** NO PERMUTATION p IS COMPUTED, AND NONE MAY BE. ***  A partial correlation is a function of THREE correlations; shuffling ONE variable leaves the conditioning variable unpermuted and the other two correlations are not independent under the shuffle, so the resulting distribution is not a null for the partial statistic.  A naive shuffle is invalid here.  The bootstrap CI below is the whole uncertainty statement.

  [full]  n = 78
    pairwise Spearman(rho, mean|delta|) = -0.407276268   Spearman(rho, dist) = +0.696831550   Spearman(mean|delta|, dist) = -0.449969334
    PARTIAL  Spearman(rho, dist | mean|delta|) = -0.146323470
      background-level bootstrap 95% CI = [-0.401778, +0.106788]  (10000 usable draws)  (INCLUDES ZERO)
    PARTIAL  Spearman(rho, mean|delta| | dist) = +0.629666674
      background-level bootstrap 95% CI = [+0.472642, +0.742385]  (10000 usable draws)  (EXCLUDES ZERO)
    no permutation p is reported for either -- see the reasoning above

  [H]  n = 78
    pairwise Spearman(rho, mean|delta|) = -0.404595405   Spearman(rho, dist) = +0.673992906   Spearman(mean|delta|, dist) = -0.441230960
    PARTIAL  Spearman(rho, dist | mean|delta|) = -0.161717649
      background-level bootstrap 95% CI = [-0.416825, +0.083508]  (10000 usable draws)  (INCLUDES ZERO)
    PARTIAL  Spearman(rho, mean|delta| | dist) = +0.603747329
      background-level bootstrap 95% CI = [+0.451631, +0.719109]  (10000 usable draws)  (EXCLUDES ZERO)
    no permutation p is reported for either -- see the reasoning above

  side-by-side (which axis carries the association once the other is held fixed?):
   view     rho~dist | mean|d|                         CI  excl0       rho~mean|d| | dist                         CI  excl0
   full              -0.146323 [-0.401778, +0.106788]  False                +0.629667 [+0.472642, +0.742385]   True
      H              -0.161718 [-0.416825, +0.083508]  False                +0.603747 [+0.451631, +0.719109]   True
```

**Verdict: PASS.** No gate failed; every quantity computed as pre-registered. The result is adverse and is reported as such.

**D10a — adding distance destroys the adjusted advantage.** The shift-only adjustment (D9's primary) gives `p_spec_adj = 0.037975`, at or below both frozen thresholds. Adding a distance term in **any** of the three forms tested puts it far **above** both thresholds:

| variant | full | vs 0.05 | H | vs 0.10 |
|---|---|---|---|---|
| shift only (D9 primary) | 0.037975 | at or below | 0.037975 | at or below |
| **+ log1p(dist) (primary)** | **0.886076** | **above** | **0.898734** | **above** |
| + linear dist | 0.126582 | above | 0.139241 | above |
| + log1p(dist), A222V clamped to dist=2 | 0.721519 | above | 0.708861 | above |

`r_A` flips sign from **−0.066** (shift-only) to **+0.045** (joint), i.e. once distance is in the model A222V's residual is *positive* — it is less extreme than the line predicts for a background of its shift and its position. A222V's signed rank moves from 3/79 to 70/79.

**D10b — the neighbourhood rank fractions are worse than D0's raw-ρ version.** A222V sits at rank fraction 0.818 (full) and 0.909 (H) among the 10 nearest, against 0.182 / 0.364 on raw ρ. Rank fractions, not tests.

**D10c — distance, not shift, carries the association.** Holding mean|δ| fixed, `Spearman(ρ, dist | mean|δ|) = −0.146` (full) and `−0.162` (H), **both CIs include zero**. Holding distance fixed, `Spearman(ρ, mean|δ| | dist) = +0.630` (full) and `+0.604` (H), **both CIs exclude zero**. This is the reverse of D4's reading.

**Files created/modified:**
- `scripts/138_phase2_diag2_joint.py` (new).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAG2_D10_FULL_OUTPUT.txt` (new, 145 lines).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` (this file).
- No earlier log, no protected file, nothing staged or committed.

**Anything unexpected or worth flagging:**

1. **The plan supplied no expected values for D10a/D10b/D10c**, so there is nothing to disagree with numerically. The D10a result is however far outside what D4 alone would have led anyone to expect, and it is stated plainly rather than softened.
2. **D10c reverses the sign of the shift partial relative to the raw pairwise.** Pairwise `Spearman(ρ, mean|δ|)` within N is **−0.407**, but the partial controlling for distance is **+0.630**. That sign flip is not a bug: `Spearman(mean|δ|, dist)` is **−0.450**, i.e. distant backgrounds are the *low-shift* ones, so conditioning on distance induces a negative relationship between the two covariates that flips the residualised association. Anyone reading the partial alone would be misled about direction. The raw pairwise values are printed beside every partial for exactly this reason.
3. **D10c's answer and D10a's answer point opposite ways, and both are reported.** D10c says the distance axis, not the shift axis, carries the association once the other is held fixed. D10a says that *adding* a distance term destroys A222V's adjusted standing. These are consistent — the distance gradient is strong and A222V sits at its extreme end (dist = 0) — but the framing differs and neither is suppressed.
4. **`log1p(dist)` and linear `dist` disagree wildly** (k = 69 vs k = 9) on the same data. Both are reported, neither selected. The plan pre-registered `log1p` as primary on the argument that the gradient is steep near 222 and flat far away; the data do not obviously support that functional form over the linear one, and I am not re-selecting after seeing the numbers.
5. **The clamped variant does not rescue the joint result** (0.72 / 0.71), so the collapse is not an artifact of the extrapolation at dist = 0. Leverage confirms this: A222V's hat value at dist = 0 is 0.383, **inside** the null leverage range (max 0.442, `G_P254F`), and clamping drops it to 0.232. A222V is not an extreme leverage point.
6. **A bug worth recording.** The `design()` helper defined near the top of the script was never called and was dead code; the real design matrix is built inside `loo_variant`. The first run also failed on a `column_stack` shape mismatch from building covariate columns as 1-D instead of 2-D. Both were caught before any number was reported, and the D10a `shift-only` variant reproduces D9's primary exactly (`r_A = −0.066425 / −0.068692`, `k = 2`, `p_spec_adj = 0.037975`, beaters `{AV_220, AV_85}`) — an independent confirmation that the new machinery agrees with the previous script.
7. **I mis-transcribed two D10b denominators when writing this log entry** (wrote `(1 + 21)` where the output says `(1 + 20)`), caught by checking the saved full-output file, and corrected in place above. Recorded rather than quietly fixed: this is the same class of error D0 exists to correct — a log entry whose prose drifts from the file it claims to quote. The correction was made against the saved verbatim output, not from memory.

---

## [D11] — 3D structural distance to residue 222 (no torch)
Status: **PASS**
Time started / finished: 2026-09-29 (smoke at `N_BOOT=300 N_PERM=300`, then full at `N_BOOT=10000 N_PERM=10000 SEED=0`; 39.9 s wall — timed, not guessed)

**What I did:**

1. **Checked the loader question before writing anything.** The task doc offers script 126's exact float64 parse, or script 107's `load_pdb` "only if it imports without torch or esm". I tested:
   ```
   $ venv/bin/python3 -c "import sys; sys.path.insert(0,'data/external/ThermoMPNN-D');
       import thermompnn.ssm_utils; print('torch in sys.modules:', 'torch' in sys.modules)"
   IMPORT OK
   torch in sys.modules: True
   ```
   `thermompnn.ssm_utils` (L8–L9) imports `thermompnn.train_thermompnn` and `thermompnn.trainer.v2_trainer`, which pull in torch. Script 126 also executes `from thermompnn.ssm_utils import load_pdb` at **module level (line 224)**, so importing 126 itself is forbidden here too.
   **So I transcribed script 126's SOURCE 3 block — its dependency-free float64 fixed-column parse, lines 322–344 — verbatim under a QUOTED SOURCE comment**, the same precedent `scripts/lib/phase2_diag.py` set for script 125's inline H-view block. **No torch, no esm, no Biopython, no thermompnn import appears anywhere in `scripts/139_phase2_diag2_3d.py`.**
2. Wrote `scripts/139_phase2_diag2_3d.py` with the **pre-registered docstring written before its first run**, including both hard gates, the per-subtask resampling unit, the `d3_atom` literal reading, and the reason no permutation p is computed for any partial correlation.
3. Ran both D11-G1 gates first. Both passed. Then ran D11.1–D11.5.

**Actual output (verbatim, from `PHASE2_DIAG2_D11_FULL_OUTPUT.txt`):**

```
------------------------------------------------------------------------------
D11-G1 (HARD GATES) -- (a) numbering mapping, (b) script 107's known figures
------------------------------------------------------------------------------
  background_rho_table.csv sha256 = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796  MATCH

  STRUCTURE READ: data/raw/6FCX.pdb
    max |coordinate| in file = 67.107 A
    chain A: 596 CA-resolved residues, window 40..651
    chain B: 590 CA-resolved residues, window 41..648
    elements present: chain A ['C', 'N', 'O', 'S'], chain B ['C', 'N', 'O', 'S']
    hydrogens in the heavy set: 0 -> 'heavy atoms only' requires no filtering
    chain A internal gaps: ['161-171', '392-396']
    chain B internal gaps: ['161-171', '203-204', '220-221', '314-316']

  frozen frame: task77_thermompnnD_doubles.csv rows with own_e_b finite = 9595 (586 distinct positions)
  [PASS] D11-G1a numbering mapping: |d_AA(p) - stored ca_dist_222|: max|diff| = 7.105e-15 A over 9595 rows (gate < 1e-06); unresolved positions in this frame are 0
  [PASS] D11-G1b monomer far (>10 A): 9232/9595 = 96.2168% (script 107/126: 9232 = 96.22%)
  [PASS] D11-G1b dimer-aware far (>10 A): 9128/9595 = 95.1329% (script 107/126: 9128 = 95.13%)

  3/3 D11-G1 checks PASS, 0 FAIL
  GATE PASS: numbering mapping reproduces to 7.105e-15 A and script 107's known figures reproduce exactly. D11 proceeds.
```

**D11.1 — 3D distances, resolution accounting, and the written table:**

```
  wrote data/processed/phase2_diagnostics/background_3d_distance.csv  (96 rows + header)
  sha256 = 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de

  RESOLUTION ACCOUNTING -- no position is imputed, ever:
    chain A resolves 40..651 with internal gaps 161-171 and 392-396
    so positions 2-39, 161-171, 392-396 and 652-656 have NO chain-A coordinates
    unresolved backgrounds: 11 of 96 -> ['AV_19', 'AV_396', 'AV_5', 'AV_655', 'G_E168S', 'G_E16V', 'G_K27I', 'G_N12P', 'G_N3K', 'G_P395F', 'G_S23A']
    of those, in the NULL SET N: 11 -> ['AV_19', 'AV_396', 'AV_5', 'AV_655', 'G_E168S', 'G_E16V', 'G_K27I', 'G_N12P', 'G_N3K', 'G_P395F', 'G_S23A']
    N = 78; resolved N (the D11 subset) = 67

  d3_CA over the 96: min = 0.000 A, median = 25.098 A, max = 76.194 A
  d3_atom over the 96: min = 0.000 A, median = 23.983 A, max = 71.264 A
```

Table sha256 confirmed independently: `69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de`.

**D11.2 — is locality spatial? Sequence recomputed on the IDENTICAL resolved subset:**

```
                 set  view                       axis    n    Spearman                     95% CI  excl0     p_two
    all96 (resolved)  full           d3_CA  [PRIMARY]   85   +0.793553 [+0.715280, +0.845734]   True  0.000100
    all96 (resolved)  full    dist_seq  [SAME SUBSET]   85   +0.779383 [+0.687504, +0.838500]   True  0.000100
    all96 (resolved)  full    d3_dimer  [SENSITIVITY]   85   +0.788585 [+0.705677, +0.844906]   True  0.000100
    all96 (resolved)  full     d3_atom  [SENSITIVITY]   85   +0.787603 [+0.705733, +0.841206]   True  0.000100
    all96 (resolved)     H           d3_CA  [PRIMARY]   85   +0.791540 [+0.712508, +0.844979]   True  0.000100
    all96 (resolved)     H    dist_seq  [SAME SUBSET]   85   +0.775692 [+0.687297, +0.834959]   True  0.000100
    all96 (resolved)     H    d3_dimer  [SENSITIVITY]   85   +0.785001 [+0.703060, +0.841129]   True  0.000100
    all96 (resolved)     H     d3_atom  [SENSITIVITY]   85   +0.785924 [+0.703020, +0.841078]   True  0.000100
   N_only (resolved)  full           d3_CA  [PRIMARY]   67   +0.731577 [+0.600332, +0.817699]   True  0.000100
   N_only (resolved)  full    dist_seq  [SAME SUBSET]   67   +0.713294 [+0.579689, +0.806713]   True  0.000100
   N_only (resolved)  full    d3_dimer  [SENSITIVITY]   67   +0.724035 [+0.588062, +0.815498]   True  0.000100
   N_only (resolved)  full     d3_atom  [SENSITIVITY]   67   +0.720962 [+0.581481, +0.812259]   True  0.000100
   N_only (resolved)     H           d3_CA  [PRIMARY]   67   +0.713319 [+0.571904, +0.809793]   True  0.000100
   N_only (resolved)     H    dist_seq  [SAME SUBSET]   67   +0.695235 [+0.561403, +0.791078]   True  0.000100
   N_only (resolved)     H    d3_dimer  [SENSITIVITY]   67   +0.702065 [+0.557926, +0.801047]   True  0.000100
   N_only (resolved)     H     d3_atom  [SENSITIVITY]   67   +0.703342 [+0.555247, +0.804826]   True  0.000100

  HEAD TO HEAD on the IDENTICAL resolved N-only subset (n = 67), full frame:
    Spearman(rho, dist_seq) = +0.713293691  CI [+0.579689, +0.806713]  p_two=0.000100
    Spearman(rho, d3_CA)    = +0.731577372  CI [+0.600332, +0.817699]  p_two=0.000100
    -> 3D distance tracks rho at least as well as sequence distance does (d3_CA is 1.026x the sequence coefficient on this subset)
```

All 16 permutation identity checks returned `|diff| = 0.000e+00` and all 16 nulls centre on zero.

**D11.3 — where the beaters sit in space:**

```
       bg_id  arm  dist_seq     d3_CA   d3_dimer   d3_atom   3D rank  note
      AV_220    V         2     6.480      6.480     5.568         2  BEATER (at or below A222V on rho); in the 10 sequence-nearest
     AV_195    V        27    10.150     10.150     8.882         4  BEATER (at or below A222V on rho); in the 10 sequence-nearest
    G_P254F    G        32    16.280     15.927    15.391         9  BEATER (at or below A222V on rho); in the 10 sequence-nearest
     AV_233    V        11    24.487     24.487    23.037        23  in the 10 sequence-nearest
     AV_209    V        13    18.862     18.862    16.574        14  in the 10 sequence-nearest
     AV_204    V        18    20.626     20.626    19.466        18  in the 10 sequence-nearest
     AV_242    V        20    17.903     17.903    16.509        11  in the 10 sequence-nearest
    G_Y197V    G        25    15.722     15.722    13.971         7  in the 10 sequence-nearest
    G_I192T    G        30     5.058      4.948     3.825         1  in the 10 sequence-nearest
    G_L178T    G        44    10.313      9.804     9.023         5  in the 10 sequence-nearest

  the 10 NEAREST nulls BY 3D DISTANCE (d3_CA):
      1.    G_I192T arm=G  d3_CA=  5.058 A  dist_seq= 30  
      2.     AV_220 arm=V  d3_CA=  6.480 A  dist_seq=  2  <-- BEATER
      3.     AV_155 arm=V  d3_CA=  8.639 A  dist_seq= 67  
      4.     AV_195 arm=V  d3_CA= 10.150 A  dist_seq= 27  <-- BEATER
      5.    G_L178T arm=G  d3_CA= 10.313 A  dist_seq= 44  
      6.     AV_175 arm=V  d3_CA= 10.537 A  dist_seq= 47  
      7.    G_Y197V arm=G  d3_CA= 15.722 A  dist_seq= 25  
      8.     G_K48P arm=G  d3_CA= 15.883 A  dist_seq=174  
      9.    G_P254F arm=G  d3_CA= 16.280 A  dist_seq= 32  <-- BEATER
      10.    G_G317Q arm=G  d3_CA= 17.648 A  dist_seq= 95  

  the 3 3D-nearest beater ranks: AV_220 rank 2, AV_195 rank 4, G_P254F rank 9
  the informative question is whether the beaters are also 3D-near, NOT whether removing them lowers p_spec.

  k-nearest-REMOVAL by 3D order -- REPORTED AS MECHANICAL WHERE LABELLED:
    k= 5 (full): |N| = 73, beaters inside removed set = ['AV_220', 'AV_195'] (2/3) -> NOT all beaters removed
           p_spec = (1 + 1)/(1 + 73) = 0.027027
    k= 5 (   H): |N| = 73, beaters inside removed set = ['AV_220', 'AV_195'] (2/3) -> NOT all beaters removed
           p_spec = (1 + 1)/(1 + 73) = 0.027027
    k=10 (full): |N| = 68, beaters inside removed set = ['AV_220', 'AV_195', 'G_P254F'] (3/3) -> MECHANICAL: all beaters removed, p_spec at its floor is guaranteed, not informative
           p_spec = (1 + 0)/(1 + 68) = 0.014493  (floor 1/69 = 0.014493)
    k=10 (   H): |N| = 68, beaters inside removed set = ['AV_220', 'AV_195', 'G_P254F'] (3/3) -> MECHANICAL: all beaters removed, p_spec at its floor is guaranteed, not informative
           p_spec = (1 + 0)/(1 + 68) = 0.014493  (floor 1/69 = 0.014493)
```

**D11.4 — joint adjustment with 3D distance, resolved subset (n = 67):**

```
                axis  view   k  p_spec_adj         r_A     rank  vs frozen
        log1p(d3_CA)  full  67    1.000000   +0.093681   68/68  ABOVE 0.05
        log1p(d3_CA)     H  67    1.000000   +0.098715   68/68  ABOVE 0.1
     log1p(dist_seq)  full  60    0.897059   +0.046847   61/68  ABOVE 0.05
     log1p(dist_seq)     H  60    0.897059   +0.048805   61/68  ABOVE 0.1
         mean|delta|  full   2    0.044118   -0.065387    3/68  AT OR BELOW 0.05
         mean|delta|     H   2    0.044118   -0.067783    3/68  AT OR BELOW 0.1
```

Fitted lines, printed in full:
```
  === log1p(d3_CA) ===
    [full]  OLS rho ~ intercept -0.158981 + mean|delta|*-0.324445   + log1p(d3_CA)*+0.048009
    [H]    OLS rho ~ intercept -0.165246 + mean|delta|*-0.338456   + log1p(d3_CA)*+0.049915
  === log1p(dist_seq) ===
    [full]  OLS rho ~ intercept -0.101820 + mean|delta|*-0.471277   + log1p(dist_seq)*+0.024049
    [H]    OLS rho ~ intercept -0.102523 + mean|delta|*-0.523085   + log1p(dist_seq)*+0.024773
  === shift only ===
    [full]  OLS rho ~ intercept +0.031062 + mean|delta|*-0.764872
    [H]    OLS rho ~ intercept +0.034429 + mean|delta|*-0.816494
```

Partial correlations with `d3_CA` (bootstrap CI only, **no permutation p**):
```
    [full]  n = 67
      pairwise Spearman(rho, mean|delta|) = -0.449437305;  Spearman(rho, d3_CA) = +0.731577372;  Spearman(mean|delta|, d3_CA) = -0.528863614
      PARTIAL Spearman(rho, d3_CA | mean|delta|) = +0.651427677
        background bootstrap 95% CI = [+0.472958, +0.769040] (10000 draws)  (EXCLUDES ZERO)
      PARTIAL Spearman(rho, mean|delta| | d3_CA) = -0.108073357
        background bootstrap 95% CI = [-0.354953, +0.130566] (10000 draws)  (INCLUDES ZERO)

    [H]  n = 67
      pairwise Spearman(rho, mean|delta|) = -0.449796472;  Spearman(rho, d3_CA) = +0.713319366;  Spearman(mean|delta|, d3_CA) = -0.527187469
      PARTIAL Spearman(rho, d3_CA | mean|delta|) = +0.627446210
        background bootstrap 95% CI = [+0.441136, +0.757830] (10000 draws)  (EXCLUDES ZERO)
      PARTIAL Spearman(rho, mean|delta| | d3_CA) = -0.123826727
        background bootstrap 95% CI = [-0.365496, +0.114504] (10000 draws)  (INCLUDES ZERO)
```

**D11.5 — head-to-head, identical denominators:**

```
   view                 adjustment   k    n  p_spec_adj  vs frozen
   full               log1p(d3_CA)  67   67    1.000000  ABOVE 0.05
      H               log1p(d3_CA)  67   67    1.000000  ABOVE 0.1
   full            log1p(dist_seq)  60   67    0.897059  ABOVE 0.05
      H            log1p(dist_seq)  60   67    0.897059  ABOVE 0.1
   full                 shift only   2   67    0.044118  AT OR BELOW 0.05
      H                 shift only   2   67    0.044118  AT OR BELOW 0.1

  denominators: n = 67 in every row above.  The unadjusted frozen p_spec used n = 78 and is NOT in this table because its denominator differs; comparing the two would be comparing different null sets.
```

**Verdict: PASS.** Both hard gates passed (mapping 7.105e-15 A over 9,595 rows; 9,232/9,595 = 96.2168% and 9,128/9,595 = 95.1329% reproduced exactly). All five subtasks ran as pre-registered.

- **D11.2: locality IS spatial.** `Spearman(ρ, d3_CA) = +0.731577` on the resolved N-only subset vs `+0.713294` for sequence distance on the *identical* 67 backgrounds — 3D is 1.026× the sequence coefficient. Same ordering on all four views and all three sensitivity axes.
- **D11.3: all three beaters are 3D-near.** `AV_220` 3D-rank 2 (6.48 Å), `AV_195` 3D-rank 4 (10.15 Å), `G_P254F` 3D-rank 9 (16.28 Å). The 3D-nearest null overall is `G_I192T` at 5.06 Å, which is *not* a beater. The k=10 3D removal removes all three beaters and is labelled mechanical; the k=5 removal removes only two and is not.
- **D11.4/D11.5: with 3D distance in the model, `p_spec_adj = 1.000000` on both views — every one of the 67 resolved nulls lies at or below A222V's residual.** A222V's residual is *positive* (+0.094 / +0.099). Sequence distance gives 0.897059. Shift-only gives 0.044118, at or below both thresholds.
- **D11.4's partials mirror D10c's**: with mean|δ| held fixed, the 3D association is +0.651 (CI excludes zero); with 3D held fixed, the shift association is −0.108 (CI includes zero).

**Files created/modified:**
- `scripts/139_phase2_diag2_3d.py` (new).
- `data/processed/phase2_diagnostics/background_3d_distance.csv` (new, 96 rows, sha256 `69914df9…333312de`).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAG2_D11_FULL_OUTPUT.txt` (new, 332 lines).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` (this file).
- `data/raw/6FCX.pdb` was read only. No earlier log, no protected file, nothing staged or committed.

**Anything unexpected or worth flagging:**

1. **`G_I192T` is the 3D-nearest null (5.06 Å) and it is not a beater** — its ρ_full is only −0.033. The nearest *spatial* background does not reproduce the effect; the nearest backgrounds that do are 2nd, 4th and 9th nearest in space.
2. **11 backgrounds are unresolved, all 11 in the null set** (`AV_19`, `AV_396`, `AV_5`, `AV_655`, `G_E168S`, `G_E16V`, `G_K27I`, `G_N12P`, `G_N3K`, `G_P395F`, `G_S23A`). Resolved N = **67**, not 78. The sequence correlation was recomputed on that identical 67 so the two are comparable; D2's n = 78 figures are not comparable and are not used here.
3. **Two label bugs of my own, both caught and fixed before the saved output was written.** The D11.4 coefficient labels printed `mean|delta|` in place of `log1p(d3_CA)` (a string-splitting error), and — more seriously — the D11.4 partial-correlation *pairwise* header printed `Spearman(rho, mean|delta|) = +0.731577` when +0.731577 is actually `Spearman(rho, d3_CA)`; the shift correlation is −0.449. Both were caught by checking the numbers against D11.2's independently-computed values, fixed in the script, and re-run. The saved full-output file is the corrected version. This is exactly the AGENTS §5 "verify column identity before reporting agreement" pattern firing on my own code.
4. **`p_spec_adj = 1.000000` with `log1p(d3_CA)` is a boundary result, not a well-estimated p.** All 67 resolved nulls fall at or below A222V's residual, so the statistic sits at its ceiling. It says the ordering is fully explained by the covariates, not that the probability of the observed value is 1.
5. **`d3_atom` was read literally** as min over all heavy atoms of residue p vs all heavy atoms of 222 in chain A, which is what the plan's words say. It gives the same correlation as `d3_CA` to three decimals. The interpretation is printed in the output so a reader can check the reading rather than guess it.
6. The chain-A window is 40..651 with 596 CA-resolved residues, and the frame has **zero** unresolved positions — so all 11 unresolved backgrounds are outside 40..651 or inside the 161–171 / 392–396 gaps, exactly as the doc's list predicts (2–39, 161–171, 392–396, 652–656).

---

# SUMMARY

## 1. READ THIS FIRST — D9's shift-adjusted `p_spec_adj`

**PRIMARY construction (leave-one-out on N, designated in advance):**

| view | `r_A` | `#{r_b ≤ r_A}` of 78 | `p_spec_adj` | vs frozen threshold | A222V rank |
|---|---|---|---|---|---|
| full | −0.066425 | 2 | **0.037975** | **at or below** 0.05 | 3/79 |
| H | −0.068692 | 2 | **0.037975** | **at or below** 0.10 | 3/79 |

**The nulls at or below A222V's residual, both views: `AV_220` (Arm V, d=2) and `AV_85` (Arm V, d=137).** Both views, all three variants, same pair.

**The two sensitivities, for side-by-side — none selected:**

| variant | view | `r_A` | k | `p_spec_adj` | vs threshold |
|---|---|---|---|---|---|
| SENSITIVITY 1 (in-sample fit on N) | full | −0.066425 | 2 | 0.037975 | at or below 0.05 |
| SENSITIVITY 1 (in-sample fit on N) | H | −0.068692 | 2 | 0.037975 | at or below 0.10 |
| SENSITIVITY 2 (D4's all-96 fit) | full | −0.059133 | 2 | 0.037975 | at or below 0.05 |
| SENSITIVITY 2 (D4's all-96 fit) | H | −0.061058 | 2 | 0.037975 | at or below 0.10 |

For reference, the **unadjusted** frozen `p_spec` was 0.025316 (full) and 0.050633 (H). Adjusting for shift magnitude moves the full-frame value up (0.0253 → 0.0380) and the H value down (0.0506 → 0.0380); both adjusted values are still at or below their frozen thresholds.

The beater set changes completely under adjustment: `{G_P254F}` / `{AV_195, AV_220, G_P254F}` becomes `{AV_220, AV_85}` on both views.

## 2. D10a / D10b / D10c

**D10a joint adjustment — adding a distance term destroys the adjusted advantage:**

| variant | full | vs 0.05 | H | vs 0.10 |
|---|---|---|---|---|
| shift only (= D9 primary) | 0.037975 | **at or below** | 0.037975 | **at or below** |
| **+ log1p(dist) (primary)** | **0.886076** | above | **0.898734** | above |
| + linear dist (sensitivity) | 0.126582 | above | 0.139241 | above |
| + log1p(dist), A222V clamped to dist=2 (sensitivity) | 0.721519 | above | 0.708861 | above |

`r_A` flips from **−0.066** to **+0.045** and A222V's rank moves from 3/79 to 70/79. The clamped variant does not rescue it, and A222V's leverage (hat 0.383) is *inside* the null range (max 0.442), so this is not an extrapolation artifact.

**D10b neighbourhood rank fractions — rank fractions, NOT tests** (A222V's rank among the k nearest, on D9's primary residuals):

| k | full | H |
|---|---|---|
| 10 | 8/10 → **0.8182** | 9/10 → **0.9091** |
| 20 | 18/20 → **0.9048** | 19/20 → **0.9524** |

**D10c — which axis carries the association once the other is held fixed: DISTANCE, not shift.**

| view | `Spearman(ρ, dist \| mean\|δ\|)` | 95% CI | excludes zero | `Spearman(ρ, mean\|δ\| \| dist)` | 95% CI | excludes zero |
|---|---|---|---|---|---|---|
| full | **−0.146323** | [−0.401778, +0.106788] | **NO** | **+0.629667** | [+0.472642, +0.742385] | **YES** |
| H | −0.161718 | [−0.416825, +0.083508] | **NO** | +0.603747 | [+0.451631, +0.719109] | YES |

Background-level bootstrap CI only, 10,000 draws, SEED=0. **No permutation p is computed, by design**: a partial correlation is a function of three correlations, and shuffling one variable leaves the conditioning variable unpermuted, so a naive shuffle is not a valid null. Note the sign flip — pairwise `Spearman(ρ, mean|δ|)` is **−0.407** but the partial controlling for distance is **+0.630**, because `Spearman(mean|δ|, dist) = −0.450`.

## 3. D11

**Is locality spatial (D11.2)? YES.** On the identical resolved subset (n = 67), full frame: `Spearman(ρ, d3_CA) = +0.731577` vs `Spearman(ρ, dist_seq) = +0.713294` — 3D is 1.026× the sequence coefficient. All 16 views exclude zero at p_two = 0.000100 with identity checks at `0.000e+00` and nulls centred on zero.

**Where the three beaters sit in 3D (D11.3): ALL THREE ARE 3D-NEAR.**

| background | `dist_seq` | `d3_CA` | `d3_dimer` | 3D rank (of 67 resolved nulls) |
|---|---|---|---|---|
| `G_I192T` (not a beater) | 30 | 5.058 | 4.948 | **1** |
| **`AV_220`** (beater) | 2 | 6.480 | 6.480 | **2** |
| **`AV_195`** (beater) | 27 | 10.150 | 10.150 | **4** |
| **`G_P254F`** (beater) | 32 | 16.280 | 15.927 | **9** |

The k=10 3D removal takes all three beaters and is labelled **mechanical**; the k=5 removal takes only two and is not.

**D11.5 head-to-head, identical denominators (n = 67 in every row):**

| view | adjustment | k | n | `p_spec_adj` | vs frozen threshold |
|---|---|---|---|---|---|
| full | **shift only** | 2 | 67 | **0.044118** | **at or below 0.05** |
| full | + log1p(dist_seq) | 60 | 67 | 0.897059 | above 0.05 |
| full | **+ log1p(d3_CA)** | 67 | 67 | **1.000000** | **above 0.05** |
| H | **shift only** | 2 | 67 | **0.044118** | **at or below 0.10** |
| H | + log1p(dist_seq) | 60 | 67 | 0.897059 | above 0.10 |
| H | **+ log1p(d3_CA)** | 67 | 67 | **1.000000** | **above 0.10** |

**No variant is declared "the" answer.** `1.000000` is a boundary value (all 67 nulls at or below A222V's residual), not an estimated probability.

## 4. D0 — table of corrections C1–C9

Corrections file: `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_CORRECTIONS.md`
**sha256 = `6a38882acd02ef8c2f8c2f58bb5f976eadf9f1c4db5235f521e39eacb33f4036`**

| # | old text (real line numbers in `PHASE2_DIAGNOSTICS_LOG.md`) | recomputed | plan target | verdict |
|---|---|---|---|---|
| C1 | "more negative than 1 of the 78 … and 3 of the 78" (329, 768) | **77 of 78** (full), **75 of 78** (H) | 77 / 75 | AGREE — old sentence reported the *at-or-below* count as the *exceeds* count |
| C2 | "the most extreme residual of all 96" (500, 708); "96.9th percentile" (479, 487, 701, 702) | A222V rank **4 of 97**; 3 backgrounds at or below: `AV_220`, `AV_85`, `A222_C` | not rank 1; ~3 beyond | AGREE — and the "(0 = most negative)" parenthetical is on the **opposite end** from the code, which computes `pct = 100.0 * float((resid_all > res).mean())` |
| C3 | "carried entirely by Arm G" (742, 814); "exhaustive control agrees" (311) | Arm V 1/39 = 0.025641 (full), 3/39 = 0.076923 (H); Arm G 2/41 = 0.048780 (both) | same | AGREE — all four at or below their frozen thresholds; "carried entirely by Arm G" **retracted** |
| C4 | "its magnitude is the largest in the null set in either direction" (351, 770) | rank **2/79** (full), **4/79** (H) | 2/79, 4/79 | AGREE — substantive D7 finding stands: 0 positive placebos reach that magnitude |
| C5 | "it is a weaker one" (395) | LOO **falls** 0.0253→0.0128; at or below 0.05 through k=2 (0.0380), above at k=3 (0.0506); at or below 0.10 through k=6 (0.0886), above at k=7 (0.1013); gaps `AV_220` 0.00352, `AV_195` 0.00396 | same | AGREE |
| C6 | "essentially every placebo" (241, 731) | all 3 beaters in the k=10 removed set (3/3); C(10,3)/C(78,3) = 120/76076 = **0.001577**; k=20 → 0.014985 | 0.001577 | AGREE — mechanical, POST-HOC |
| C7 | "A222V is unusual **relative to its own neighbourhood**" (810, 243) | k=10: 1 (full), 3 (H) → **0.1818 / 0.3636**; k=20: **0.0952 / 0.1905** | 0.1818 / 0.3636 | AGREE — rank fractions, NOT tests |
| C8 | "more negative than essentially every placebo, including the nearest ones" (241, 731) | `AV_220` NOT at or below on full (gap +0.003520); **IS** at or below on H (−0.004459) | as described | AGREE — the sentence is true of full, **false of H** |
| C9 | "do not exist in this repository" (822) | **both files EXIST**: `docs/tasks/results-log/MTHFR_RESULTS_LOG.md`, `docs/writeups/PROJECT_SUMMARY_FINAL.md` | both exist | AGREE — the earlier flag was a **wrong-path check** |

**All nine plan targets agreed with the recomputation. No target was forced; the disagreement-detection machinery in script 136 is what would have fired otherwise.**

## 5. Plain two-sided statement of which claim the data now support

**The data cannot separate "tied to position 222" from "tied to the region around 222."** They rule out neither, and they rule out the stronger reading on both sides.

Stated in both directions, because the evidence points both ways:

- **Against "position-222-specific."** ρ_b tracks distance from 222 with a large, region-robust gradient (Spearman +0.697 within N on sequence distance, +0.732 on 3D distance — the latter is *not* explained by sequence proximity). All three backgrounds that fall at or below A222V's residual lie at 3D ranks 2, 4 and 9. Once distance is in the model, A222V's residual turns **positive** (`p_spec_adj` 0.886 with sequence distance, 1.000 with 3D distance) and every background in the resolved null set lies beyond it. Holding mean|δ| fixed, the distance association survives (−0.146 → CI includes zero only after shift is partialled the *other* way; the partial with shift held fixed is +0.651) while the shift association does not (−0.108, CI includes zero).
- **For "position-222-specific."** Before distance is adjusted for, the shift-adjusted comparison is at or below both frozen thresholds (`p_spec_adj` = 0.037975, both views; 0.044118 on the resolved subset). A222V is not explained by shift magnitude. All 18 Arm S backgrounds sit at position 222 and none of them is in the null set, so the design cannot distinguish "the residue" from "the region's first member" on its own.

**Neither reading wins.** The claim that survives intact is the descriptive one Diagnostics I already had: A222V's ρ is more extreme than most placebos, and remains so after controlling for how hard each background perturbs the model — but the neighbourhood it sits in behaves systematically like it, in both sequence and space, and nothing here separates "this position" from "this region's closest member."

## 6. Every gate, PASS/FAIL, value — D0-G1 first

| gate | what it checked | result | value |
|---|---|---|---|
| **D0-G1a** | D1 table sha256 | **PASS** | `e397a442…5863` |
| **D0-G1b** | A222V ρ re-derived through `phase2_diag.py` | **PASS** | −0.088118064 (\|diff\| 2.489e-10); −0.090021683 (\|diff\| 3.340e-11), tol 1e-9 |
| **D0-G1c** | `p_spec(full)` = 2/79, beaters `{G_P254F}` | **PASS** | \|diff\| **0.000e+00** |
| **D0-G1d** | `p_spec(H)` = 4/79, beaters `{AV_195, AV_220, G_P254F}` | **PASS** | \|diff\| **0.000e+00** |
| **D9-G1** | reproduce D4's printed values before any new analysis | **PASS 23/23** | ρ~mean\|δ\| −0.614188823 (\|diff\| 4.281e-10) / −0.612696690 (1.791e-10), tol 1e-8; all 20 six-dp quantities match at tol 2e-6 |
| D9 input | table sha256 | **PASS** | `e397a442…5863` |
| D10 input | table sha256 | **PASS** | `e397a442…5863` |
| **D11-G1a** | numbering mapping: recomputed chain-A CA-CA distance to 222 vs stored `ca_dist_222` | **PASS** | **max\|diff\| = 7.105e-15 Å** over 9,595 rows, gate < 1e-6 |
| **D11-G1b** | monomer far (>10 Å) | **PASS** | **9,232/9,595 = 96.2168%** (script 107: 9,232 = 96.22%) |
| **D11-G1b** | dimer-aware far (>10 Å) | **PASS** | **9,128/9,595 = 95.1329%** (script 107: 9,128 = 95.13%) |
| D11 identity checks | forced identity permutation, every view | **PASS ×16** | \|diff\| = **0.000e+00** |
| D11 null centring | permutation null centring, every view | **PASS ×16** | all centre on zero within 2 MCSE |
| D0 plan targets | 9 items × recomputed vs target | **ALL AGREE** | no disagreement table produced |
| D11 3D table | `background_3d_distance.csv` sha256 | recorded | `69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de` |

**No gate failed. No threshold was loosened. No task was re-run at a higher N to obtain a result. Task status: D0 PASS, D9 PASS, D10 PASS, D11 PASS.**

## 7. Protected paths, earlier logs, git state, torch/esm — confirmed

- **Nothing protected was edited.** Verified by `git status --porcelain` and by mtime: `AGENTS.md` (Sep 22 23:18), `RESULTS.md` (Sep 26 19:37), `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md` (Sep 27 23:01), `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` (Sep 28 16:31) — all unchanged.
- **No earlier log was touched.** `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md` sha256 = `8209875d714b0e2b2428b6eee26500f0218b777a14a2af31b84d735ae57cd6fc`, mtime still **Sep 29 20:27** — before this session began. `PHASE2_LOG.md`, `MTHFR_RESULTS_LOG.md` and `PROJECT_SUMMARY_FINAL.md` were not written. `docs/tasks/phase3a-gb1-acquisition/` and `docs/tasks/phase3b-gb1-regime-map/` were not touched (every file there still has its Sep 28 mtime).
- **Nothing was staged, committed or pushed.** `git log --all -- scripts/136…139` returns **empty** — none of my four scripts is in any commit. HEAD is `bbcfe11` ("Add Phase 2 diagnostics II…"), committed **22:24:08**, which contains exactly one file: the planning document `PHASE2_DIAGNOSTICS_II.md` (336 insertions). **That commit is not mine**; I did not create it and did not author its message. The immediately preceding `620f099` (also 22:24:08) committed the Diagnostics I outputs and scripts 131–135 — likewise not mine, and it records the earlier log "as-is", consistent with this session's append-only corrections rule.
- **No torch and no esm were imported anywhere.** `scripts/139_phase2_diag2_3d.py` deliberately does not import script 126 or script 107, because both execute `from thermompnn.ssm_utils import load_pdb` at module level and that package pulls in torch (verified: `import thermompnn.ssm_utils` → `IMPORT OK`, `'torch' in sys.modules` → `True`). Script 126's dependency-free float64 fixed-column parse was **transcribed verbatim** instead and gated to 7.105e-15 Å against the stored values. No Biopython, no thermompnn.
- **No packages installed.** `venv/bin/python3` throughout. All runs in the foreground. Nothing written outside `docs/tasks/phase2-diagnostics-ii-neighbourhood/`, `scripts/`, and `data/processed/phase2_diagnostics/`.

**Files this session created (all untracked):** `scripts/136_phase2_diag2_corrections.py`, `scripts/137_phase2_diag2_shift_adjusted.py`, `scripts/138_phase2_diag2_joint.py`, `scripts/139_phase2_diag2_3d.py`, `data/processed/phase2_diagnostics/background_3d_distance.csv`, and in `docs/tasks/phase2-diagnostics-ii-neighbourhood/`: this log, `PHASE2_DIAGNOSTICS_CORRECTIONS.md`, and four `PHASE2_DIAG2_*_FULL_OUTPUT.txt` files.

## 8. The single most important thing to read first

**`docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` line 515** — D10a's primary result, `PRIMARY  log1p(dist)  full  69    0.886076   +0.045227   70/79  ABOVE 0.05`.

Read it together with **line 354** (D9's `p_spec_adj = 0.037975`, at or below the frozen threshold) and **line 784** (D11.5's `1.000000` with 3D distance). Those three lines are the whole story of this session: **the frozen comparison holds up against the shift confound and falls apart against the distance gradient.** Anyone quoting only the first will report a result the data no longer supports; anyone quoting only the third will miss that it survives the adjustment that Diagnostics I never ran.

*(Line numbers verified against this file after it was finalised: 354, 515 and 784. An earlier draft of this section cited 295/452/570, which pointed at the wrong lines; corrected against `grep -n` output, not from memory.)*

---

**Anything unexpected or worth flagging:**

1. **`AV_85` (d=137) is a beater under adjustment and appears nowhere in Diagnostics I.** It is the 137-residue-distant second-smallest shifter (`mean|δ|` 0.039, second-lowest of all 96), so the shift line predicts almost nothing for it and its ρ of -0.071 becomes a large negative residual. It was never at or below A222V's raw ρ and so never surfaced before. Its residual (-0.073 full, -0.083 H) is the second most negative in both views.
2. **`AV_220` remains at or below A222V's residual on both views**, and it is the nearest background to 222 (d=2). Its residual is the most negative in both views. So the shift-adjusted comparison is still, in the beater sense, a near-222 background lying beyond A222V — which is the locality concern, not a resolution of it.
3. **The three variants are identical in `k` but not in `r_A`**, and the primary/sensitivity-1 pair share `r_A` exactly because A222V is out-of-sample in both (its residual depends only on the fit on all 78). Only sensitivity 2 (all-96) shifts it. Expected, and printed.
4. **No plan target was supplied for `p_spec_adj` itself** — only the D9-G1 reproduction table — so there is no target to disagree with. The direction of the change relative to the unadjusted `p_spec` is reported above as computed.
5. The leave-one-out residuals are exact but **not exchangeable draws**: they come from 78 overlapping fits on the same 78 points, and a leverage point gets a larger LOO residual mechanically. `AV_85` is exactly that case. This is stated in the docstring and in the printed limitations so `p_spec_adj = 0.038` is not read as a calibrated tail probability.
6. Two of my own script's first-run failures were presentation-layer only (`s134` module called as a function; a `sed` fix for the second occurrence). The gate and all numbers were identical across runs. The saved output file is the complete 184-line stdout, not a hand-edited copy.

---
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_CORRECTIONS.md` (new, sha256 `6a38882a…33f4036`).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAG2_D0_FULL_OUTPUT.txt` (new).
- `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` (this file).
- **Not modified:** `PHASE2_DIAGNOSTICS_LOG.md` (sha256 `8209875d714b0e2b2428b6eee26500f0218b777a14a2af31b84d735ae57cd6fc`, mtime still 2026-09-29 20:27), `PHASE2_LOG.md`, `PHASE2_PREREG.md`, `AGENTS.md`, `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`, `GB1_REGIME_PREREG.md`. Nothing staged, committed or pushed.

**Anything unexpected or worth flagging:**

1. **C2 is worse than the plan says, and two of the three are not the ones anyone would name.** The plan predicted `AV_220` would be more negative than A222V and that "about three backgrounds lie beyond it". True — but the other two are **`AV_85` (d=137, Arm V)** and **`A222_C` (Arm S, d=0)**. `AV_85` is a *distant* background, so "residual extremity" is not confined to the 222 neighbourhood. `A222_C` is an **Arm S** background, i.e. the same position-222 arm, and is not part of the null set N at all — so the corrected sentence's framing ("A222V is rank 4 of 97 among the 96 backgrounds") is about the 96 background set, not the null set. Both the full and H frames give the same three. This is a substantive addition to what the earlier log claimed and should not be lost in the correction.
2. **The "96.9th percentile" is not a small disagreement, it is a wrong-direction label.** Script 134 line 417 computes `pct = 100.0 * float((resid_all > res).mean())` — the fraction of residuals **greater** than A222V's — while line 425 prints "(0 = most negative)". The code's 0 is the most *positive* residual and its 100 is the most *negative*. The parenthetical describes the opposite end. The 96.9 figure itself is right and does imply 3 backgrounds at or below; the parenthetical attached to it is what is wrong.
3. **C3's retraction changes the direction of a summary item, not just its wording.** "The full-frame result is carried entirely by Arm G" (lines 742, 814) is the opposite of what the numbers say: Arm V's full-frame count of 0/38 is rank 1/39, the strongest agreement the design-matched arm can give, and the *only* full-frame exception (`G_P254F`) lies in Arm G. All four arm-alone post-hoc values are at or below their frozen thresholds. A summary item that reads the other way needs replacing, not editing.
4. **C6's probability confirms the mechanical claim, and the k=20 value is reported as a second disclosed value (0.014985) with neither selected.** All three beaters are in both the k=10 and the k=20 removed sets, so `p_spec` reaching its floor is guaranteed by construction at both k.
5. **C7's k=20 numbers are new** (0.0952 full, 0.1905 H, rank fractions 2/21 and 4/21) — the plan supplied no target for them, and they are labelled rank fractions, not tests.
6. **C9: the earlier "protected files do not exist" flag was a wrong-path check.** Both files exist at the paths Phase 3a's T7 recorded. Diagnostics I looked for them at the repository root. Neither file was read into or modified.
7. **Two of my own script's first-run crashes were caught before any result was reported**, and both were in the *presentation* layer, not the computation: a Python scoping bug in the C2 verbatim-quote locator, and a 2-tuple/3-tuple arity mismatch when writing the C1 table. The gate had already passed and the C1–C9 numbers were identical across all three runs. I re-ran rather than hand-patching the output file, and the final sha256 is the one above. Recorded because a corrected output file is exactly the kind of thing that should never be hand-edited.
8. No packages installed. `venv/bin/python3` throughout. Foreground only. Nothing committed.

---
