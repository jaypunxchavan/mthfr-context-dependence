# PHASE 2 diagnostics III - execution log

**Doc:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III.md`
**Executor:** OpenCode
**Session constraints:** cached-data only. No model scoring. No `torch`, `esm`, or `thermompnn` import.
**Correction file:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS.md`

Tasks in order: D12, D13, D14, D15, D16.

**Target-vs-recomputation rule in force:** every expected value in the planning doc is Claude's own
recomputation, not a fact. Each is recomputed independently and printed beside the target. On disagreement the
doc is wrong: the item stops, both numbers are reported, and no agreement is forced.

**Wording rule in force:** GENERIC / BEATS / INDETERMINATE are not used as labels for any result computed here.
Adjusted `p_spec` is compared to the frozen numeric thresholds (0.05 full, 0.10 H) and described only as "at or
below" or "above" those.

---
## [D12] - Append-only corrections to Diagnostics II (hard gate first, no new science)
Status: PASS
Time started / finished: 2026-09-30 (D12-G1 gate 0.7 s; smoke at N_BOOT=200 1.2 s; full at N_BOOT=10000 SEED=0 **18.8 s wall, timed not guessed**; single deterministic run per configuration)

What I did:
1. Created this log file first, before anything else, per instruction.
2. Read `AGENTS.md` (222 lines) and `PHASE2_DIAGNOSTICS_III.md` (371 lines) in full.
3. Surveyed real state: `ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` -> highest existing is **139**, confirming **140** is the next free number. Read `scripts/lib/phase2_diag.py` (245 lines), `scripts/137_phase2_diag2_shift_adjusted.py` (451 lines), `scripts/138_phase2_diag2_joint.py` (447 lines) and `scripts/139_phase2_diag2_3d.py` (784 lines) in full, and `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md` (999 lines) **read only**.
4. Located every K-item search string with `grep -n` at run time inside the script (never a line number taken from the task doc or from memory), and read scripts 138/139 **as text** with real line numbers for the verbatim code quotes.
5. Wrote `scripts/140_phase2_diag3_corrections.py` with the pre-registered docstring **before its first run**.
6. Ran **D12-G1 (HARD) first**, before any correction was written. PASS 26/26. Session continued.
7. Recomputed K1-K6, printed recomputed beside every target, and **wrote `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` from inside the script** so every number in a corrected statement is interpolated from a computed variable.

Actual output (verbatim, from `PHASE2_DIAG3_D12_FULL_OUTPUT.txt`):

```
==============================================================================
D12 -- APPEND-ONLY CORRECTIONS TO THE DIAGNOSTICS II LOG (script 140)
==============================================================================
SCOPE: corrections only.  No new science, nothing selected, nothing frozen redefined.
NO torch / esm / thermompnn / Biopython import in this file.  scripts 138 and 139 are READ AS TEXT for the verbatim code quotes.
RESAMPLING UNIT: BACKGROUND for K1's two partial-correlation bootstrap CIs (N_BOOT=10000, SEED=0, per-background values held FIXED).  K2/K3/K4 do NO resampling -- deterministic fits and exact rank counts.
WORDING: GENERIC / BEATS / INDETERMINATE are not used as labels here.  Adjusted p_spec is compared to the frozen NUMERIC thresholds 0.05 (full) and 0.10 (H) and called only 'at or below' or 'above'.

------------------------------------------------------------------------------
GATE D12-G1 (HARD) -- reproduce every row before correcting anything
------------------------------------------------------------------------------
  [PASS] D12-G1.1 D1 table sha256: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796 vs e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796 (match)
  [PASS] D12-G1.2 3D table sha256: 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de vs 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de (match)
    A222V rho (full, re-derived)                               recomputed =     -0.088118064   target =     -0.088118064   |diff| = 2.489e-10   AGREE
    A222V rho (H, re-derived)                                  recomputed =     -0.090021683   target =     -0.090021683   |diff| = 3.340e-11   AGREE
    p_spec (full)                                              recomputed =      0.025316456   target =      0.025316456   |diff| = 0.000e+00   AGREE
    p_spec (full) beaters                                      recomputed =                  ['G_P254F']   target =                  ['G_P254F']   AGREE
    p_spec (H)                                                 recomputed =      0.050632911   target =      0.050632911   |diff| = 0.000e+00   AGREE
    p_spec (H) beaters                                         recomputed = ['AV_195', 'AV_220', 'G_P254F']   target = ['AV_195', 'AV_220', 'G_P254F']   AGREE
    D9 primary r_A (full)                                      recomputed =     -0.066424633   target =     -0.066425000   |diff| = 3.674e-07   AGREE
    D9 primary k (full)                                        recomputed =                        ['2']   target =                        ['2']   AGREE
    D9 primary beaters (full)                                  recomputed =          ['AV_220', 'AV_85']   target =          ['AV_220', 'AV_85']   AGREE
    D9 primary r_A (H)                                         recomputed =     -0.068691937   target =     -0.068692000   |diff| = 6.262e-08   AGREE
    D9 primary k (H)                                           recomputed =                        ['2']   target =                        ['2']   AGREE
    D9 primary beaters (H)                                     recomputed =          ['AV_220', 'AV_85']   target =          ['AV_220', 'AV_85']   AGREE
    D10a joint primary r_A (full)                              recomputed =      0.045226926   target =      0.045227000   |diff| = 7.356e-08   AGREE
    D10a joint primary k (full)                                recomputed =                       ['69']   target =                       ['69']   AGREE
    D10a joint primary r_A (H)                                 recomputed =      0.047030107   target =      0.047030000   |diff| = 1.071e-07   AGREE
    D10a joint primary k (H)                                   recomputed =                       ['70']   target =                       ['70']   AGREE
    D11.2 Spearman(rho, d3_CA) n=67 (full)                     recomputed =      0.731577372   target =      0.731577372   |diff| = 1.899e-10   AGREE
    D11.2 Spearman(rho, dist_seq) n=67 (full)                  recomputed =      0.713293691   target =      0.713293691   |diff| = 4.604e-11   AGREE
    D11.2 Spearman(rho, d3_CA) n=67 (H)                        recomputed =      0.713319366   target =      0.713319366   |diff| = 3.985e-10   AGREE
    D11.2 Spearman(rho, dist_seq) n=67 (H)                     recomputed =      0.695234865   target =      0.695235000   |diff| = 1.349e-07   AGREE
    D11.4 3D-log r_A (full)                                    recomputed =      0.093681340   target =      0.093681000   |diff| = 3.397e-07   AGREE
    D11.4 3D-log k (full)                                      recomputed =                       ['67']   target =                       ['67']   AGREE
    D11.4 3D-log r_A (H)                                       recomputed =      0.098714560   target =      0.098715000   |diff| = 4.397e-07   AGREE
    D11.4 3D-log k (H)                                         recomputed =                       ['67']   target =                       ['67']   AGREE

  2/2 sha256 checks PASS, 0 FAIL
  24/24 numeric gate rows AGREE with the task doc's targets, 0 DISAGREE
  GATE PASS: every row of the D12-G1 table reproduces.  Corrections may now be written.
```

**K1 - D10c's two partial correlations are label-swapped. CONFIRMED, with the source:**

```
  OLD TEXT, located with grep -n in the Diagnostics II log (line numbers are the REAL ones, from the file):
    line 550: >>>     PARTIAL  Spearman(rho, dist | mean|delta|) = -0.146323470
    line 558: >>>     PARTIAL  Spearman(rho, dist | mean|delta|) = -0.161717649
    line 552: >>>     PARTIAL  Spearman(rho, mean|delta| | dist) = +0.629666674
    line 560: >>>     PARTIAL  Spearman(rho, mean|delta| | dist) = +0.603747329

  THE BUG, IN scripts/138_phase2_diag2_joint.py, verbatim (file and real line numbers):
    scripts/138_phase2_diag2_joint.py:374
       374:     def partial(x, y, z):
       375:         rxy = float(spearmanr(x, y).statistic)
       376:         rxz = float(spearmanr(x, z).statistic)
       377:         ryz = float(spearmanr(y, z).statistic)
       378:         den = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
       379:         return (rxy - rxz * ryz) / den, rxy, rxz, ryz
    ... and the two call sites, verbatim:
    scripts/138_phase2_diag2_joint.py:388
       388:         obs, rxy, rxm, rmd = partial(x, m, d)      # rho ~ dist | mean|delta|
    scripts/138_phase2_diag2_joint.py:389
       389:         obs2, rxy2, rxd, ryd = partial(x, d, m)    # rho ~ mean|delta| | dist
    ... and the two print sites, verbatim:
    scripts/138_phase2_diag2_joint.py:404
       404:         print(f"    PARTIAL  Spearman(rho, dist | mean|delta|) = {obs:+.9f}")
    scripts/138_phase2_diag2_joint.py:408
       408:         print(f"    PARTIAL  Spearman(rho, mean|delta| | dist) = {obs2:+.9f}")
    READING: `partial(x, y, z)` returns the partial of x and y GIVEN z.
    `partial(x, m, d)` (x=rho, m=mean|delta|, d=dist) is the partial of rho and mean|delta| GIVEN dist  ->  rho ~ shift | dist.
    It is stored in `obs` and printed on line 404 under the label 'PARTIAL Spearman(rho, dist | mean|delta|)'.
    `partial(x, d, m)` is the partial of rho and dist GIVEN mean|delta|  ->  rho ~ dist | shift.
    It is stored in `obs2` and printed on line 408 under the label 'PARTIAL Spearman(rho, mean|delta| | dist)'.
    -> THE TWO PRINT LABELS ARE TRANSPOSED.  THE VALUES ARE RIGHT; the LABELS are wrong.
    The PAIRWISE line (138:401-403) is CORRECTLY labelled -- it prints spearmanr(x, m), spearmanr(x, d), spearmanr(m, d), which
    are rho~shift, rho~dist and shift~dist.  Only the two PARTIAL labels are affected.

  RECOMPUTED BOTH PARTIALS TWO INDEPENDENT WAYS (n = 78 nulls, both views):
    (a) standard three-pairwise-Spearman formula
    (b) rank-transform + OLS residualisation on [1, rank(z)], Pearson of residuals

    [full]  n = 78
      pairwise Spearman(rho, mean|delta|)  = -0.407276268
      pairwise Spearman(rho, dist)         = +0.696831550
      pairwise Spearman(mean|delta|, dist)  = -0.449969334
      rho ~ DIST  | mean|delta|   (a) formula   = +0.629666674
                              (b) rank-resid  = +0.629666674   |a-b| = 2.220e-16
                              bootstrap 95% CI (a) = [+0.472642, +0.742385] (10000 draws)  EXCLUDES ZERO
                              bootstrap 95% CI (b) = [+0.468468, +0.741477] (10000 draws)  EXCLUDES ZERO
      rho ~ SHIFT | dist          (a) formula   = -0.146323470
                              (b) rank-resid  = -0.146323470   |a-b| = 5.551e-17
                              bootstrap 95% CI (a) = [-0.404796, +0.107532] (10000 draws)  INCLUDES ZERO
                              bootstrap 95% CI (b) = [-0.400560, +0.104714] (10000 draws)  INCLUDES ZERO

    [H]  n = 78
      pairwise Spearman(rho, mean|delta|)  = -0.404595405
      pairwise Spearman(rho, dist)         = +0.673992906
      pairwise Spearman(mean|delta|, dist)  = -0.441230960
      rho ~ DIST  | mean|delta|   (a) formula   = +0.603747329
                              (b) rank-resid  = +0.603747329   |a-b| = 1.110e-16
                              bootstrap 95% CI (a) = [+0.452424, +0.720011] (10000 draws)  EXCLUDES ZERO
                              bootstrap 95% CI (b) = [+0.449441, +0.720082] (10000 draws)  EXCLUDES ZERO
      rho ~ SHIFT | dist          (a) formula   = -0.161717649
                              (b) rank-resid  = -0.161717649   |a-b| = 2.776e-17
                              bootstrap 95% CI (a) = [-0.416825, +0.083508] (10000 draws)  INCLUDES ZERO
                              bootstrap 95% CI (b) = [-0.419251, +0.079345] (10000 draws)  INCLUDES ZERO

  RECOMPUTED vs TARGET (point estimates are the gate):
    K1 rho ~ dist | shift, formula (full)                      recomputed =        +0.629667   target =        +0.629667   |diff| = 3.261e-07   AGREE
    K1 rho ~ shift | dist, formula (full)                      recomputed =        -0.146323   target =        -0.146323   |diff| = 4.703e-07   AGREE
    K1 rho ~ dist | shift, formula (H)                         recomputed =        +0.603747   target =        +0.603747   |diff| = 3.294e-07   AGREE
    K1 rho ~ shift | dist, formula (H)                         recomputed =        -0.161718   target =        -0.161718   |diff| = 3.514e-07   AGREE
    (rank-residualisation agrees with the formula to 2.2e-16 on every value)
      [full] rho ~ dist | shift   CI (a) = [+0.472642, +0.742385]   target [+0.472642, +0.742385]
      [full] rho ~ shift | dist  CI (a) = [-0.404796, +0.107532]   target [-0.401778, +0.106788]
      [H]   rho ~ dist | shift   CI (a) = [+0.452424, +0.720011]   target [+0.451631, +0.719109]
      [H]   rho ~ shift | dist  CI (a) = [-0.416825, +0.083508]   target [-0.416825, +0.083508]

  D11.4's PARTIALS WITH d3_CA -- were THEY labelled correctly?
    scripts/139_phase2_diag2_3d.py:719
       719:         p1, _ = partial(x, g, m)      # rho vs d3_CA, given mean|delta|
    scripts/139_phase2_diag2_3d.py:720
       720:         p2, _ = partial(x, m, g)      # rho vs mean|delta|, given d3_CA
    scripts/139_phase2_diag2_3d.py:735
       735:         print(f"      PARTIAL Spearman(rho, d3_CA | mean|delta|) = {p1:+.9f}")
    scripts/139_phase2_diag2_3d.py:739
       739:         print(f"      PARTIAL Spearman(rho, mean|delta| | d3_CA) = {p2:+.9f}")
    READING: script 139 stores partial(x, g, m) in p1 and prints it as 'rho, d3_CA | mean|delta|', and partial(x, m, g) in p2
    and prints it as 'rho, mean|delta| | d3_CA'.  Both MATCH.  D11.4's labels are CORRECT.
      [full] rho ~ d3_CA | mean|delta| : (a) +0.651428  (b) +0.651428
      [full] rho ~ mean|delta| | d3_CA : (a) -0.108073  (b) -0.108073
      [H]   rho ~ d3_CA | mean|delta| : (a) +0.627446  (b) +0.627446
      [H]   rho ~ mean|delta| | d3_CA : (a) -0.123827  (b) -0.123827
    (all four AGREE with the doc's targets)
```

**K2 - D10b ran on the wrong residual vector. CONFIRMED at source; the old counts reproduce exactly.**

```
  OLD TEXT (real line numbers, from grep -n):
    line 529: >>> D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals
    line 224: >>>   k=10 nearest (full): # at or below =  1 of 10  -> rank fraction 2/11 = 0.1818
    line 532: >>>   k=10 nearest (full):  # at or below =  8 of 10  ->  rank fraction (1 + 8)/(1 + 10) = 0.8182   at or below: AV_195, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
    line 225: >>>   k=10 nearest (   H): # at or below =  3 of 10  -> rank fraction 4/11 = 0.3636
    line 533: >>>   k=10 nearest (   H):  # at or below =  9 of 10  ->  rank fraction (1 + 9)/(1 + 10) = 0.9091   at or below: AV_195, AV_209, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
    line 226: >>>   k=20 nearest (full): # at or below =  1 of 20  -> rank fraction 2/21 = 0.0952
    line 534: >>>   k=20 nearest (full):  # at or below = 18 of 20  ->  rank fraction (1 + 18)/(1 + 20) = 0.9048   at or below: AV_145, AV_155, AV_175, AV_195, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V
    line 227: >>>   k=20 nearest (   H): # at or below =  3 of 20  -> rank fraction 4/21 = 0.1905
    line 535: >>>   k=20 nearest (   H):  # at or below = 19 of 20  ->  rank fraction (1 + 19)/(1 + 20) = 0.9524   at or below: AV_145, AV_155, AV_175, AV_195, AV_209, AV_220, AV_233, AV_242, AV_292, AV_293, AV_302, AV_311, G_E168S, G_E279K, G_G317Q, G_I192T, G_L178T, G_P254F, G_Y197V
    line 583: >>> **D10b - the neighbourhood rank fractions are worse than D0's raw-rho version.** A222V sits at rank fraction 0.818 (full) and 0.909 (H) among the 10 nearest, against 0.182 / 0.364 on raw rho. Rank fractions, not tests.

  (i) WHICH RESIDUAL VECTOR DID SCRIPT 138's D10b ACTUALLY USE? Verbatim source:
    scripts/138_phase2_diag2_joint.py:270
       270:     VARIANTS = [
    scripts/138_phase2_diag2_joint.py:271
       271:         ("PRIMARY  log1p(dist)", ["mean|delta|", "log1p(dist)"],
    ...
    scripts/138_phase2_diag2_joint.py:322
       322:             if name.startswith("PRIMARY"):
       323:                 resid_primary[view] = (dict(r), r_A)
    ...
    scripts/138_phase2_diag2_joint.py:333
       333:     banner("D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals",
    scripts/138_phase2_diag2_joint.py:337
       337:     near_by_dist = sorted(N_ids, key=lambda b: (DIST[b], b))
    scripts/138_phase2_diag2_joint.py:342
       342:             r, r_A = resid_primary[view]
    scripts/138_phase2_diag2_joint.py:343
       343:             k = int(sum(1 for b in sub if r[b] <= r_A))
    READING: `resid_primary[view]` is assigned ONLY inside the D10a loop, under the guard `if name.startswith("PRIMARY")`.  VARIANTS[0]
    is named "PRIMARY  log1p(dist)" -- the JOINT log1p(dist_seq) model, NOT D9's shift-only model.  D10b then reads
    `r, r_A = resid_primary[view]` at line 342.
    -> D10b RAN ON THE D10a PRIMARY JOINT log1p(dist_seq) RESIDUALS, while its banner (line 333) and its prose call them "D9's PRIMARY
       residuals".  The LABEL IS WRONG; the counts are arithmetically correct for the vector actually used.

  (ii) REPRODUCE THE OLD COUNTS AND NAME THE VECTOR THAT PRODUCES THEM:
    ON D10a PRIMARY log1p(dist) residuals, full, k=10: # at or below = 8 of 10  ->  rank fraction (1 + 8)/(1 + 10) = 0.8182
      at or below: AV_195, AV_220, AV_233, AV_242, G_I192T, G_L178T, G_P254F, G_Y197V
    ON D10a PRIMARY log1p(dist) residuals, full, k=20: # at or below = 18 of 20  ->  rank fraction (1 + 18)/(1 + 20) = 0.9048
    ON D10a PRIMARY log1p(dist) residuals, H, k=10: # at or below = 9 of 10  ->  rank fraction (1 + 9)/(1 + 10) = 0.9091
    ON D10a PRIMARY log1p(dist) residuals, H, k=20: # at or below = 19 of 20  ->  rank fraction (1 + 19)/(1 + 20) = 0.9524
    (all four counts AND all four name lists reproduce the old log exactly)

  (iii) RECOMPUTE D10b ON D9's PRIMARY RESIDUALS, as pre-registered.  *** RANK FRACTIONS, NOT TESTS. ***
    ON D9's PRIMARY residuals, full, k=10: # at or below = 1 of 10  ->  rank fraction (1 + 1)/(1 + 10) = 0.1818   at or below: AV_220
    ON D9's PRIMARY residuals, full, k=20: # at or below = 1 of 20  ->  rank fraction (1 + 1)/(1 + 20) = 0.0952   at or below: AV_220
    ON D9's PRIMARY residuals, H, k=10: # at or below = 1 of 10  ->  rank fraction (1 + 1)/(1 + 10) = 0.1818   at or below: AV_220
    ON D9's PRIMARY residuals, H, k=20: # at or below = 1 of 20  ->  rank fraction (1 + 1)/(1 + 20) = 0.0952   at or below: AV_220
    (raw-rho version, for the withdrawn comparison, recomputed here on the same neighbourhoods)
      raw rho, full, k=10: # at or below = 1 of 10 -> rank fraction 0.1818
      raw rho, full, k=20: # at or below = 1 of 20 -> rank fraction 0.0952
      raw rho, H, k=10: # at or below = 3 of 10 -> rank fraction 0.3636
      raw rho, H, k=20: # at or below = 3 of 20 -> rank fraction 0.1905
```

**K3 - "not an extrapolation artifact". The log-form predictions DO lie below every observed null.**

```
  OLD TEXT:
    line 856: >>> `r_A` flips from -0.066 to +0.045 and A222V's rank moves from 3/79 to 70/79. The clamped variant does not rescue it, and
    A222V's leverage (hat 0.383) is *inside* the null range (max 0.442), so this is not an extrapolation artifact.

  MOST NEGATIVE OBSERVED NULL rho (a real measurement, not a prediction):
    [full] G_P254F = -0.096244
    [H] G_P254F = -0.101954
    (both AGREE with the doc's targets -0.096244 / -0.101954, G_P254F)

                               variant  view            fit n   predicted rho at A222V         r_A  most neg OBSERVED null
             shift-only (LOO fit on N)  full           N (78)                -0.021693   -0.066425               -0.096244
                     + linear dist_seq  full           N (78)                -0.054407   -0.033711               -0.096244
           + log1p(dist_seq), dist = 0  full           N (78)                -0.133345   +0.045227               -0.096244
   + log1p(dist_seq), clamped dist = 2  full           N (78)                -0.107121   +0.019003               -0.096244
                + log1p(d3_CA), d3 = 0  full  resolved N (67)                -0.181799   +0.093681               -0.096244
             shift-only (LOO fit on N)     H           N (78)                -0.021330   -0.068692               -0.101954
                     + linear dist_seq     H           N (78)                -0.054074   -0.035948               -0.101954
           + log1p(dist_seq), dist = 0     H           N (78)                -0.137052   +0.047030               -0.101954
   + log1p(dist_seq), clamped dist = 2     H           N (78)                -0.110092   +0.020070               -0.101954
                + log1p(d3_CA), d3 = 0     H  resolved N (67)                -0.188736   +0.098715               -0.101954

  RECOMPUTED vs TARGET (full frame).  The task doc states these K3 targets to 4 DECIMAL PLACES.  The 2e-6 tolerance belongs to the
  D12-G1 table and is NOT reused here and NOT loosened; both comparisons are printed for every target.
    K3 predicted rho, shift-only (LOO fit on N)
      recomputed (6 dp)          = -0.021693
      target as printed          = -0.0217  (the task doc gives this target to 4 dp)
      |recomputed - target|      = 6.568e-06   vs the D12-G1 2e-6 tolerance -> *** DISAGREE at 2e-6 ***
      round(recomputed, 4) = -0.0217  -> MATCHES the target to every digit the target prints
    K3 predicted rho, + linear dist_seq
      recomputed (6 dp)          = -0.054407   target -0.0544   |diff| = 7.367e-06 -> DISAGREE at 2e-6   round(.,4) = -0.0544 MATCH
    K3 predicted rho, + log1p(dist_seq), dist = 0
      recomputed (6 dp)          = -0.133345   target -0.1333   |diff| = 4.499e-05 -> DISAGREE at 2e-6   round(.,4) = -0.1333 MATCH
    K3 predicted rho, + log1p(dist_seq), clamped dist = 2
      recomputed (6 dp)          = -0.107121   target -0.1071   |diff| = 2.087e-05 -> DISAGREE at 2e-6   round(.,4) = -0.1071 MATCH
    K3 predicted rho, + log1p(d3_CA), d3 = 0
      recomputed (6 dp)          = -0.181799   target -0.1818   |diff| = 5.960e-07 -> AGREE at 2e-6   round(.,4) = -0.1818 MATCH
    K3 targets matching to every digit the target prints (4 dp): 5/5
    K3 targets agreeing at the 2e-6 tolerance: 1/5
    *** REPORTED, NOT FORCED: the task doc's K3 targets are rounded to 4 dp; the recomputed values agree with them digit
    for digit, and the raw differences (all below 5e-5) are an artefact of that rounding, not a value mismatch. ***
```

**K4 - form dependence, all four values reproduce:**

```
    [full]    linear dist: k =  9 of 78, p_spec_adj = 0.126582 -> ABOVE 0.05;  A222V signed rank = 10/79;  r_A = -0.033711
    [full]    log1p(dist): k = 69 of 78, p_spec_adj = 0.886076 -> ABOVE 0.05;  A222V signed rank = 70/79;  r_A = +0.045227
    [H]    linear dist: k = 10 of 78, p_spec_adj = 0.139241 -> ABOVE 0.1;  A222V signed rank = 11/79;  r_A = -0.035948
    [H]    log1p(dist): k = 70 of 78, p_spec_adj = 0.898734 -> ABOVE 0.1;  A222V signed rank = 71/79;  r_A = +0.047030
    ratio of the two full-frame p_spec_adj values = 7.000x
```

**K5 / K6 - real line numbers, quoted:**

```
  grep -n 'partialled the' -> [927]
    line 927: >>> - **Against "position-222-specific.** rho_b tracks distance from 222 with a large, region-robust gradient (Spearman
    +0.697 within N on sequence distance, +0.732 on 3D distance - the latter is *not* explained by sequence proximity). All three
    backgrounds that fall at or below A222V's residual lie at 3D ranks 2, 4 and 9. Once distance is in the model, A222V's residual
    turns **positive** (`p_spec_adj` 0.886 with sequence distance, 1.000 with 3D distance) and every background in the resolved null
    set lies beyond it. Holding mean|delta| fixed, the distance association survives (-0.146 -> CI includes zero only after shift is
    partialled the *other* way; the partial with shift held fixed is +0.651) while the shift association does not (-0.108, CI includes zero).

  grep -n 'point opposite ways' -> [597]
    line 597: >>> 3. **D10c's answer and D10a's answer point opposite ways, and both are reported.** D10c says the distance axis, not the
    shift axis, carries the association once the other is held fixed. D10a says that *adding* a distance term destroys A222V's adjusted
    standing. These are consistent - the distance gradient is strong and A222V sits at its extreme end (dist = 0) - but the framing
    differs and neither is suppressed.

  grep -n 'D10c - distance, not shift, carries the association' -> [585]
    line 585: >>> **D10c - distance, not shift, carries the association.** Holding mean|delta| fixed, `Spearman(rho, dist | mean|delta|) =
    -0.146` (full) and `-0.162` (H), **both CIs include zero**. Holding distance fixed, `Spearman(rho, mean|delta| | dist) = +0.630`
    (full) and `+0.604` (H), **both CIs exclude zero**. This is the reverse of D4's reading.

  grep -n 'D10c reverses the sign of the shift partial' -> [596]
    line 596: >>> 2. **D10c reverses the sign of the shift partial relative to the raw pairwise.** Pairwise `Spearman(rho, mean|delta|)`
    within N is **-0.407**, but the partial controlling for distance is **+0.630**. That sign flip is not a bug: `Spearman(mean|delta|,
    dist)` is **-0.450**, i.e. distant backgrounds are the *low-shift* ones, so conditioning on distance induces a negative relationship
    between the two covariates that flips the residualised association. Anyone reading the partial alone would be misled about direction.

  grep -n 'Background-level bootstrap CI only, 10,000 draws, SEED=0. **No permutation p is computed, by design**' -> [872]
    line 872: >>> Background-level bootstrap CI only, 10,000 draws, SEED=0. **No permutation p is computed, by design**: a partial
    correlation is a function of three correlations, and shuffling one variable leaves the conditioning variable unpermuted, so a naive
    shuffle is not a valid null. Note the sign flip - pairwise `Spearman(rho, mean|delta|)` is **-0.407** but the partial controlling
    for distance is **+0.630**, because `Spearman(mean|delta|, dist) = -0.450`.
```

Corrections file written:

```
  wrote docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS.md  (266 lines)
  sha256 = 8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176
```

Verdict: **PASS.**
- **D12-G1 (HARD): PASS 26/26** (2 sha256 rows + 24 numeric rows), before any correction was written.
- **K1 CONFIRMED.** Script 138's two partial-correlation *labels* are transposed at lines 404 and 408. `+0.629667` is `rho ~ dist | shift`; `-0.146323` is `rho ~ shift | dist`. Recomputed two independent ways (pairwise formula and rank-residualisation) to 2.2e-16. CIs reproduce within Monte-Carlo error. Consequence: the log's "sign flip" (lines 596, 872) and its "reverse of D4's reading" (line 585) **do not exist** - the shift partial keeps the raw sign (-0.407 -> -0.146). **D11.4's partials were labelled correctly** and are unchanged (+0.651428 / -0.108073 full; +0.627446 / -0.123827 H).
- **K2 CONFIRMED, and worse than the task doc said.** D10b did not merely mislabel its input: `resid_primary` is bound at script 138 line 322-323 under the guard `name.startswith("PRIMARY")`, which matches `VARIANTS[0] = "PRIMARY  log1p(dist)"`, the **D10a joint log1p(dist_seq)** model. D10b therefore ran on the joint-model residuals. The old counts (8/9/18/19) and all four name lists reproduce exactly on that vector. On **D9's primary residuals**, as pre-registered, the counts are **1, 1, 1, 1** (`AV_220` only) with rank fractions 0.1818 / 0.0952. The claim "worse than D0's raw-rho version" is **withdrawn**.
- **K3 CONFIRMED.** Predicted rho at A222V's covariates is below the most negative **observed** null rho (`G_P254F`, -0.096244 full / -0.101954 H) for the log1p(dist_seq) form at dist=0 (-0.133345), the clamped form (-0.107121) and the log1p(d3_CA) form (-0.181799). Only linear-in-sequence-distance (-0.054407) and shift-only (-0.021693) leave A222V more extreme than predicted.
- **K3 TARGET PRECISION - DISAGREEMENT REPORTED, NOT FORCED.** The task doc states the K3 targets to 4 decimal places. Four of the five differ from the recomputed values by more than the D12-G1 table's 2e-6 tolerance (raw differences 5.96e-07 to 4.50e-05), and all five match the target to every digit the target prints. **No tolerance was loosened and no value was tuned.** Both comparisons are printed side by side in the script's output and in the corrections file. My reading (rule 4, most conservative): the doc's K3 *values* are right and only its precision is coarse; the substantive conclusion does not turn on the fourth decimal place.
- **K4 CONFIRMED.** All four values reproduce; the two full-frame `p_spec_adj` values differ by a factor of **7.000**. All four are above the frozen numeric thresholds.
- **K5/K6 done.** Lines 585, 596, 597, 872 and 927 quoted verbatim with real line numbers; void parts named.

Files created/modified:
- `scripts/140_phase2_diag3_corrections.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` (new, 266 lines, sha256 `8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176`).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D12_FULL_OUTPUT.txt` (new, 385 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- **Not modified:** `PHASE2_DIAGNOSTICS_II_LOG.md` (mtime still Sep 29 22:45; sha256 `2297a2d924792a2d2d78053d4bdb1ca504c348540b9673c33e03ee77c3181279`), `PHASE2_DIAGNOSTICS_LOG.md` (sha256 `8209875d714b0e2b2428b6eee26500f0218b777a14a2af31b84d735ae57cd6fc`, unchanged from the value Diagnostics II itself recorded), `PHASE2_LOG.md`, `PHASE2_PREREG.md`, `AGENTS.md`, `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`, `GB1_REGIME_PREREG.md`, `scripts/137*`, `scripts/138*`, `scripts/139*`, `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **K1's mechanism is a one-line label swap, not a numerical error.** Every D10c *value* in the Diagnostics II log is correct; only the two print labels at script 138 lines 404 and 408 are transposed. The swap propagated into the narrative (lines 585, 596, 597, 872, 927), which is why the log's prose contradicted its own table. This is the same class of failure as Diagnostics II's D0 C2 and C7: **a log whose prose drifts from the code that produced it.**
2. **K2's diagnosis in the task doc was right in substance but understated.** The doc said the counts "contradict D9's printed residuals" and suspected the D10a joint residuals. That suspicion is exactly right, and the counts reproduce to the digit on that vector - including all four name lists, which the doc did not ask for.
3. **`grep -n` on `"k=10 nearest (full):"` also hits D0's section at real lines 224-227.** Those four lines are Diagnostics II's D0/C7 quote of the **raw-rho** neighbourhood rank fractions (1/10 and 3/10), not D10b's. Recomputed here and matching exactly (0.1818/0.3636/0.0952/0.1905). The D10b lines are 532-535. Recorded so nobody reads 224-227 as a second D10b.
4. **D0's C7 raw-rho fractions (1 full / 3 H at k=10) and D10b's claimed D9-residual fractions (8 / 9) differ mostly because they are different statistics on different vectors**, not because D10b "lost" something. On D9's primary residuals the full-frame k=10 count is 1, which equals the raw-rho count; the H count drops from 3 (raw) to 1 (shift-adjusted).
5. **A222V is only barely more extreme than predicted under linear distance** (-0.054407 predicted vs -0.096244 observed), so the K3 conclusion - that only the linear form leaves A222V more extreme than predicted - rests on a fairly small margin. Stated, not smoothed over.
6. **Three of my own script's first-run crashes were caught before any result was reported**, all presentation-layer: a 4-tuple where `boot_partial` needed a scalar, a local name `pf` shadowing the new scalar wrapper by assignment rather than definition, and a `{:d}` format applied to a float. The gate and all D12-G1 numbers were identical across every run. Re-run rather than hand-patching the output file.

## [D13] - A222V against its same-site comparators (Arm S), directly
Status: PASS
Time started / finished: 2026-09-30 (0.7 s wall - deterministic, no resampling; N_BOOT/N_PERM not read by this script)

What I did:
1. Created the **new** shared module `scripts/lib/phase2_diag3.py` (D13-D16 helpers, plus script 139's verbatim transcription of script 126's float64 PDB parse, needed by D15). `scripts/lib/phase2_diag.py` was **not** modified. No torch/esm/thermompnn/Biopython import.
2. Wrote `scripts/141_phase2_diag3_samesite.py` with the pre-registered docstring **before its first run**: n = 19, rank fractions only, no p-values, D13.2 designated primary in advance, the all-96 fit as a disclosed in-sample sensitivity, the resampling unit (none), and the limits.
3. Ran it. All 8 doc targets reproduced.

Actual output (verbatim, from `PHASE2_DIAG3_D13_FULL_OUTPUT.txt`):

```
==============================================================================
D13 -- A222V AGAINST ITS SAME-SITE COMPARATORS (Arm S), DIRECTLY (script 141)
==============================================================================
SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as a label.
*** RANK FRACTIONS ONLY (n = 19).  NO p-VALUES, NO NULL DISTRIBUTION, NO SIGNIFICANCE CLAIM. ***
RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  N_BOOT / N_PERM are not read by this script.

  background_rho_table.csv sha256 = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  MATCH (required e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796)
  background_3d_distance.csv sha256 = 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
  MATCH

  Arm S (all at position 222, substitution != A and != V): 18 = ['A222_C', 'A222_D', 'A222_E', 'A222_F', 'A222_G',
  'A222_H', 'A222_I', 'A222_K', 'A222_L', 'A222_M', 'A222_N', 'A222_P', 'A222_Q', 'A222_R', 'A222_S', 'A222_T', 'A222_W', 'A222_Y']
  All Arm S positions are 222: [222], all dist_222 = [0]
  A222V is in neither Arm S nor N and is out of sample for every fit below.
  Arm S d3_CA = [0.0] A (it is position 222)

------------------------------------------------------------------------------
D13.1 -- RAW rho: A222V WITHIN Arm S u {A222V}  (n = 19)
------------------------------------------------------------------------------

  [full]  A222V rho = -0.088118064
    rank      bg_id  position  dist_222    d3_CA  mean|delta|            rho  <= A222V?
       1     A222_C       222         0    0.000     0.068111   -0.093529969  YES
       2     A222_T       222         0    0.000     0.078027   -0.085890371  no
       3     A222_D       222         0    0.000     0.104093   -0.081657235  no
       4     A222_N       222         0    0.000     0.088948   -0.076712110  no
       5     A222_F       222         0    0.000     0.103369   -0.076109024  no
       6     A222_E       222         0    0.000     0.104842   -0.072118749  no
       7     A222_I       222         0    0.000     0.085258   -0.069322876  no
       8     A222_S       222         0    0.000     0.066545   -0.068299813  no
       9     A222_Y       222         0    0.000     0.096628   -0.064967616  no
      10     A222_P       222         0    0.000     0.098881   -0.064488894  no
      11     A222_Q       222         0    0.000     0.083930   -0.061575739  no
      12     A222_W       222         0    0.000     0.092244   -0.057926447  no
      13     A222_H       222         0    0.000     0.077272   -0.053981871  no
      14     A222_L       222         0    0.000     0.105150   -0.053895221  no
      15     A222_R       222         0    0.000     0.097354   -0.053242246  no
      16     A222_G       222         0    0.000     0.087211   -0.047518529  no
      17     A222_M       222         0    0.000     0.071537   -0.045990178  no
      18     A222_K       222         0    0.000     0.094122   -0.045641128  no
    A222V  rho = -0.088118064   mean|delta| = 0.070330   dist_222 = 0   d3_CA = 0.000
    Arm S members at or below A222V: k = 1 of 18  -> A222_C
    A222V signed rank within S u {A222V} = 2/19   rank fraction (1 + 1)/(1 + 18) = 0.1053
    *** RANK FRACTION OVER n = 19.  NOT A TEST. ***

  [H]  A222V rho = -0.090021683
    (18 rows, same structure)
       1     A222_C       222         0    0.000     0.067910   -0.090964259  YES
       2     A222_D       222         0    0.000     0.106383   -0.086809350  no
      ...
      18     A222_M       222         0    0.000     0.071665   -0.048929841  no
    A222V  rho = -0.090021683   mean|delta| = 0.069403   dist_222 = 0   d3_CA = 0.000
    Arm S members at or below A222V: k = 1 of 18  -> A222_C
    A222V signed rank within S u {A222V} = 2/19   rank fraction (1 + 1)/(1 + 18) = 0.1053
    *** RANK FRACTION OVER n = 19.  NOT A TEST. ***

  RECOMPUTED vs TARGET (A222_C, from Diagnostics II's D0 C2 output):
    D13.1 A222_C raw rho (full)                          recomputed = -0.093530   target = -0.093530   |diff| = 3.118e-08   AGREE
    D13.1 A222V raw rho (full)                           recomputed = -0.088118   target = -0.088118   |diff| = 6.425e-08   AGREE
    D13.1 A222_C raw rho (H)                             recomputed = -0.090964   target = -0.090964   |diff| = 2.593e-07   AGREE
    D13.1 A222V raw rho (H)                              recomputed = -0.090022   target = -0.090022   |diff| = 3.170e-07   AGREE
    No target is given for how many OTHER Arm S members are at or below; the counts above are the recomputation and stand on their own.

------------------------------------------------------------------------------
D13.2 -- SHIFT-ADJUSTED RESIDUAL, EXCHANGEABLE CONSTRUCTION (PRIMARY)
------------------------------------------------------------------------------
  PRIMARY: OLS rho ~ a + c*mean|delta| fitted on ALL 78 NULLS (the D9 fit).
  A222V and all 18 Arm S members are OUT OF SAMPLE from that same fit, so A222V and Arm S are exchangeable with each other.
  SENSITIVITY, REPORTED NOT SELECTED: D4's all-96 fit (Arm S IN sample; A222V out of sample).
  *** RANK FRACTIONS OVER n = 19.  NOT TESTS. ***

  === [full] ===
                             variant         r_A       slope   intercept  n_fit  Arm S in sample?
         PRIMARY  D9 fit on 78 nulls   -0.066425   -0.726287   +0.029386     78  no
    rank      bg_id            rho  mean|delta|     residual  <= r_A?
       1     A222_C   -0.093529969     0.068111    -0.073448  YES
       2     A222_T   -0.085890371     0.078027    -0.058607  no
       3     A222_S   -0.068299813     0.066545    -0.049356  no
       4     A222_N   -0.076712110     0.088948    -0.041496  no
       5     A222_I   -0.069322876     0.085258    -0.036787  no
       6     A222_D   -0.081657235     0.104093    -0.035442  no
       7     A222_F   -0.076109024     0.103369    -0.030420  no
       8     A222_Q   -0.061575739     0.083930    -0.030005  no
       9     A222_H   -0.053981871     0.077272    -0.027246  no
      10     A222_E   -0.072118749     0.104842    -0.025360  no
      11     A222_Y   -0.064967616     0.096628    -0.024174  no
      12     A222_M   -0.045990178     0.071537    -0.023420  no
      13     A222_P   -0.064488894     0.098881    -0.022059  no
      14     A222_W   -0.057926447     0.092244    -0.020317  no
      15     A222_G   -0.047518529     0.087211    -0.013564  no
      16     A222_R   -0.053242246     0.097354    -0.011922  no
      17     A222_L   -0.053895221     0.105150    -0.006913  no
      18     A222_K   -0.045641128     0.094122    -0.006668  no
    A222V  rho = -0.088118064  mean|delta| = 0.070330  predicted = -0.021693  r_A = -0.066425
    Arm S at or below A222V: k = 1 of 18  -> A222_C
    A222V rank fraction within S u {A222V} = (1 + 1)/(1 + 18) = 0.1053   *** RANK FRACTION, NOT A TEST ***
          SENSITIVITY  D4 all-96 fit   -0.059133   -0.896326   +0.034053     96  YES -- disclosed
       1     A222_C   -0.093529969     0.068111    -0.066534  YES
       2     A222_T   -0.085890371     0.078027    -0.050006  no
      ...
      18     A222_L   -0.053895221     0.105150    +0.006300  no
    Arm S at or below A222V: k = 1 of 18  -> A222_C
    A222V rank fraction within S u {A222V} = (1 + 1)/(1 + 18) = 0.1053   *** RANK FRACTION, NOT A TEST ***

  (H view, same structure: PRIMARY r_A = -0.068692, slope -0.774750, intercept +0.032440, n_fit 78, k = 1 -> A222_C,
   residual -0.070791; all-96 r_A = -0.061058, slope -0.964705, intercept +0.037990, n_fit 96, k = 1 -> A222_C,
   residual -0.063441)

  RECOMPUTED vs TARGET (A222_C on the ALL-96 residual, from D0 C2):
    D13.2 A222_C all-96 residual (full)                  recomputed = -0.066534   target = -0.066534   |diff| = 2.987e-07   AGREE
    D13.2 A222V all-96 residual (full)                   recomputed = -0.059133   target = -0.059133   |diff| = 3.139e-07   AGREE
    D13.2 A222_C all-96 residual (H)                     recomputed = -0.063441   target = -0.063441   |diff| = 2.067e-07   AGREE
    D13.2 A222V all-96 residual (H)                      recomputed = -0.061058   target = -0.061058   |diff| = 3.935e-07   AGREE

------------------------------------------------------------------------------
D13 HEAD-TO-HEAD (rank fractions; n = 19; none is a test)
------------------------------------------------------------------------------
   view                                      statistic  k of 18  rank frac  Arm S at or below A222V
   full                                        raw rho        1     0.1053  A222_C
   full     shift-adj. residual (PRIMARY, 78-null fit)        1     0.1053  A222_C
   full  shift-adj. residual (all-96 fit, SENSITIVITY)        1     0.1053  A222_C
      H                                        raw rho        1     0.1053  A222_C
      H     shift-adj. residual (PRIMARY, 78-null fit)        1     0.1053  A222_C
      H  shift-adj. residual (all-96 fit, SENSITIVITY)        1     0.1053  A222_C

  effect size, stated alongside the rank fraction (AGENTS 3):
    [full] Arm S raw rho: mean = -0.065159, median = -0.064728, min = -0.093530, max = -0.045641, sd = 0.014048;  A222V = -0.088118
    [full] Arm S primary residual: mean = -0.029845, median = -0.026303, min = -0.073448, max = -0.006668, sd = 0.017533;  A222V r_A = -0.066425
    [H] Arm S raw rho: mean = -0.070181, median = -0.068991, min = -0.090964, max = -0.048930, sd = 0.012563;  A222V = -0.090022
    [H] Arm S primary residual: mean = -0.033105, median = -0.033896, min = -0.070791, max = -0.008424, sd = 0.015453;  A222V r_A = -0.068692
    *** RAW rho: A222V is the 2nd most negative of the 19 on the full frame and the 2nd most negative on H; it sits INSIDE
    the Arm S raw-rho range [-0.093530, -0.045641] (full), not outside it.  Exactly one Arm S member (A222_C) is more negative
    than A222V.  The rank fraction is the result; the range statement is context and is not a test. ***

------------------------------------------------------------------------------
D13.3 -- WHAT THIS CAN AND CANNOT SAY
------------------------------------------------------------------------------
  CAN: within position 222, replacing the alanine with valine changes rho_b relative to the other 18 substitutions at that same site, on this measure, at n = 19.  This is a substitution-specificity statement WITHIN the site.
  CANNOT: separate 'the residue' from 'the region around 222'.  Every member of this comparison is at position 222 and at d3_CA = 0, so the comparison carries no information about proximity at all.
  CANNOT: speak to a monotonic Grantham gradient over these 18.  The Grantham gradient over the same 18 was NOT RESOLVED (Phase 1b P3, Phase 2 A4), so no claim about substitution property is made here.
  CANNOT: be a test.  n = 19, all 18 comparators share a site, and no null distribution exists for this comparison.  These are rank fractions.
  CANNOT: replace the frozen p_spec.  The frozen comparison is A222V against the 78 nulls and is untouched by this task.
  CAVEAT: mean|delta| and rho_b are both functions of the SAME delta_b, so D13.2 is a partial control of shift MAGNITUDE and not an independent one; it is blind to shift sign pattern and to heteroscedasticity.

  RECOMPUTED vs TARGET: 8/8 AGREE, 0 DISAGREE
```

Verdict: **PASS.** All 8 doc targets reproduced to < 4.4e-7.

- **D13.1 raw rho: exactly ONE Arm S member is at or below A222V on both views - `A222_C`.** A222V is 2nd most negative of 19; rank fraction **0.1053** on both frames.
- **D13.2 primary (out-of-sample on the 78-null fit): still exactly one, `A222_C`** (residual -0.073448 full, -0.070791 H vs r_A -0.066425 / -0.068692). Rank fraction **0.1053** on both frames.
- **D13.2 all-96 sensitivity (Arm S in sample, disclosed): still one, `A222_C`** (residual -0.066534 / -0.063441 vs r_A -0.059133 / -0.061058). Rank fraction **0.1053**.
- The answer is the same on raw rho, on the exchangeable shift-adjusted residual, and on the in-sample all-96 residual, on both views. **No variant selected; all three reported.**
- Effect size, per AGENTS §3: A222V's raw rho is 0.0230 below the Arm S mean (-0.088118 vs -0.065159, full) against an Arm S sd of 0.0140; its primary residual is 0.0366 below the Arm S residual mean (-0.066425 vs -0.029845) against an Arm S residual sd of 0.0175.
- **These are rank fractions at n = 19, not tests.** No p-value, no CI, no permutation was computed.

Files created/modified:
- `scripts/lib/phase2_diag3.py` (new, shared helpers for D13-D16; script 139's PDB parse transcribed verbatim for D15's use).
- `scripts/141_phase2_diag3_samesite.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D13_FULL_OUTPUT.txt` (new, 223 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- Nothing protected, no earlier log, no earlier script, and not `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **The answer is completely stable across all three constructions.** A222V beating all but one of the 18 same-site comparators does not depend on whether the comparison is raw, shift-adjusted out-of-sample, or shift-adjusted with Arm S in sample. That is a stronger statement than the doc asked for, and it is the opposite direction from D10b's (withdrawn) claim that adjustment made A222V look worse within its own neighbourhood.
2. **The single exception is `A222_C`, and it is a large one on raw rho.** A222_C's rho is -0.093530 against A222V's -0.088118, a gap of 0.0054; A222_T, the next-most-negative, is -0.085890, a gap of 0.0022 the other way. So A222V and A222_C are effectively tied at the top of the site and the third member is clearly behind. On the primary shift-adjusted residual the ordering changes: A222_C -0.073448, A222_T -0.058607, **A222_S -0.049356**. After removing the shift-magnitude component, the *next* member at the site is `A222_S` (serine), not `A222_T`.
3. **`A222_S` is the low-shift member of Arm S** (mean|delta| 0.066545, the lowest of the 18 on both frames) and its raw rho (-0.068300) sits mid-pack (rank 8 of 18). The shift adjustment therefore lifts it in the residual ordering. This is the same mechanism Diagnostics II flagged for `AV_85` in the null set (small mean|delta|, large negative residual), and it is a reminder that a shift-adjusted residual at a leverage corner of the covariate range is partly mechanical. Disclosed, not corrected.
4. **A222V is INSIDE the Arm S raw-rho range, not outside it.** Only one of 18 same-site comparators is more extreme. That is a much weaker same-site statement than the frozen 1-of-78 result against the null set, and it is reported as the rank fraction it is.
5. Two of my own first-run crashes were presentation/scope errors in a brand-new script, both caught before any result was reported: the primary fit's residual dict covered only the 78 nulls so Arm S lookups raised `KeyError` (fixed by scoring every Arm S member out of sample from the same fit, which is also what the exchangeability argument requires), and a leftover placeholder line. Re-run rather than hand-patching the output.

## [D14] - Model-free gradient bins by 3D distance, including Arm S at 0 A
Status: PASS (D14.3 figure SKIPPED - matplotlib not importable, not installed, per the doc's rule 9)
Time started / finished: 2026-09-30 (smoke at N_BOOT=500 then full at N_BOOT=10000 SEED=0; 0.9 s wall - timed, not guessed)

What I did:
1. Wrote `scripts/142_phase2_diag3_bins.py` with the pre-registered docstring **before its first run**: bins fixed now and not tuned, the 11 unresolved backgrounds named and excluded and never imputed, the background-level resampling unit for D14.1 only, D14.2 labelled POST-HOC, and the figure's optional status.
2. Verified both input sha256s (3D table and rho table) before any bin was computed.
3. Smoke at `N_BOOT=500`, then full at `N_BOOT=10000 SEED=0`.

Actual output (verbatim, from `PHASE2_DIAG3_D14_FULL_OUTPUT.txt`):

```
==============================================================================
D14 -- MODEL-FREE GRADIENT BINS BY 3D DISTANCE, INCLUDING Arm S AT 0 A (script 142)
==============================================================================
SCOPE: descriptive.  Nothing frozen is redefined.  No outcome word is used as a label.
NO FITTED FUNCTIONAL FORM APPEARS ANYWHERE IN THIS SCRIPT.  Bins are fixed in advance and are NOT tuned.
RESAMPLING UNIT: BACKGROUND, and only for D14.1's difference-of-means CI (N_BOOT=10000, SEED=0, per-
background rho_b held FIXED, the two disjoint groups resampled INDEPENDENTLY).  D14.0 and D14.2 do NO resampling.

  background_3d_distance.csv sha256 = 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
  MATCH
  background_rho_table.csv sha256 = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  MATCH

  RESOLUTION ACCOUNTING -- nothing imputed, ever:
    96 backgrounds; 11 unresolved, EXCLUDED from every bin and listed by name:
      ['AV_19', 'AV_396', 'AV_5', 'AV_655', 'G_E168S', 'G_E16V', 'G_K27I', 'G_N12P', 'G_N3K', 'G_P395F', 'G_S23A']
    of those, in the null set N: [same 11]  (11 of 11)
    resolved backgrounds = 85  (Arm S 18, resolved V 34, resolved G 33)
    resolved null set = 67 of 78

------------------------------------------------------------------------------
D14.0 -- BIN TABLE (no fitted form; bins fixed in advance)
------------------------------------------------------------------------------

  === [full] ===  (A222V rho = -0.088118064, mean|delta| = 0.070330, d3_CA = 0.000 A -- the REFERENCE LINE)
         bin (d3_CA)    n   S   V   G    mean rho      median         min         max  mean|delta|
  {exactly 0}  (Arm S)   18  18   0   0   -0.065159   -0.064728   -0.093530   -0.045641     0.089085
             (0, 12]    6   0   4   2   -0.064933   -0.070363   -0.084598   -0.032948     0.069361 *** n=6, UNSTABLE ***
            (12, 20]    8   0   3   5   -0.057444   -0.056323   -0.096244   -0.018056     0.096069
            (20, 30]   17   0  10   7   -0.027758   -0.034024   -0.077808   +0.045471     0.056589
            (30, 45]   16   0   8   8   +0.000252   -0.003612   -0.062145   +0.051669     0.046972
           (45, inf)   20   0   9  11   +0.024492   +0.022853   -0.031212   +0.063116     0.045204

  same bins, NULL SET ONLY (the D11/D15 denominator, n = 67 resolved):
         bin (d3_CA)    n    mean rho      median         min         max  mean|delta|
  {exactly 0}  (Arm S)    0 (empty bin)
             (0, 12]    6   -0.064933   -0.070363   -0.084598   -0.032948     0.069361
            (12, 20]    8   -0.057444   -0.056323   -0.096244   -0.018056     0.096069
            (20, 30]   17   -0.027758   -0.034024   -0.077808   +0.045471     0.056589
            (30, 45]   16   +0.000252   -0.003612   -0.062145   +0.051669     0.046972
           (45, inf)   20   +0.024492   +0.022853   -0.031212   +0.063116     0.045204

  (H view, identical bin structure: Arm S mean -0.070181, median -0.068991, min -0.090964, max -0.048930,
   mean|delta| 0.089728; (0,12] -0.073769 / -0.081581 / -0.094480 / -0.029689 / 0.073960;
   (12,20] -0.060151; (20,30] -0.027577; (30,45] +0.002603; (45,inf) +0.022246)

  full membership of each bin, by name (all 85 resolved):
    {exactly 0}  (Arm S) n= 18: A222_C(S,0.00) ... A222_Y(S,0.00)
               (0, 12] n=  6: AV_155(V,8.64), AV_175(V,10.54), AV_195(V,10.15), AV_220(V,6.48), G_I192T(G,5.06), G_L178T(G,10.31)
              (12, 20] n=  8: AV_145, AV_209, AV_242, G_G317Q, G_K48P, G_L318F, G_P254F, G_Y197V
              (20, 30] n= 17: AV_113, AV_116, AV_204, AV_233, AV_302, AV_311, AV_353, AV_84, AV_85, AV_98, G_E54R, G_H354F, G_M111N,
                          G_R357M, G_R358V, G_T115G, G_W59C
             (30, 45] n= 16: AV_292, AV_293, AV_328, AV_350, AV_368, AV_461, AV_70, AV_73, G_E279K, G_E383T, G_G562M, G_K401S,
                          G_L408H, G_P346V, G_S494H, G_V574C
             (45, inf) n= 20: AV_462, AV_511, AV_522, AV_524, AV_551, AV_558, AV_587, AV_589, AV_650, G_A462S, G_A551K, G_D629C,
                          G_H613R, G_K510H, G_L472H, G_L526R, G_S430P, G_T521D, G_T549H, G_W595H
    d3_CA over the 85 resolved backgrounds: min = 0.000, median = 25.098, max = 76.194 A

------------------------------------------------------------------------------
D14.1 -- DISCONTINUITY CHECK AT THE 0 A BIN EDGE
------------------------------------------------------------------------------
  Difference of means:  mean(rho, Arm S)  -  mean(rho, resolved nulls in (0, 12])
  INDEPENDENT-GROUPS BACKGROUND-LEVEL bootstrap 95% CI, N_BOOT=10000, SEED=0.
  RESAMPLING UNIT: BACKGROUND.  The two groups are DISJOINT sets of backgrounds, so each is resampled with replacement
  independently and the difference recomputed.  Each background's rho_b is held FIXED within a draw; nothing is re-derived.
  *** DESCRIPTIVE COMPARISON OF TWO SMALL SAMPLES.  The (0, 12] bin is n = 6 AND UNSTABLE.  NO p-VALUE IS COMPUTED. ***

  the (0, 12] resolved-NULL bin, all 6 members:
         bg_id  arm     d3_CA  dist_seq  mean|delta|    rho (full)       rho (H)
       G_I192T    G     5.058        30     0.066874  -0.032947897  -0.029689252
        AV_220    V     6.480         2     0.047893  -0.084598081  -0.094480281
        AV_155    V     8.639        67     0.081750  -0.070395718  -0.088806375
        AV_195    V    10.150        27     0.095630  -0.084161807  -0.093420822
       G_L178T    G    10.313        44     0.063864  -0.070330933  -0.074355887
        AV_175    V    10.537        47     0.060158  -0.047162207  -0.061862861
    d3_CA span = 5.058 to 10.537 A

    [full]  mean(rho, Arm S, n=18) = -0.065159   mean(rho, (0,12] nulls, n=6) = -0.064933
    [full]  DIFFERENCE OF MEANS = -0.000227
    [full]  background-level bootstrap 95% CI = [-0.017265, +0.015162] (10000 usable draws)   INCLUDES ZERO
    [full]  *** The (0, 12] bin has n = 6 and is labelled UNSTABLE.  This is a description of two small samples, not a test of a discontinuity. ***

    [H]  mean(rho, Arm S, n=18) = -0.070181   mean(rho, (0,12] nulls, n=6) = -0.073769
    [H]  DIFFERENCE OF MEANS = +0.003588
    [H]  background-level bootstrap 95% CI = [-0.016695, +0.020572] (10000 usable draws)   INCLUDES ZERO

------------------------------------------------------------------------------
D14.2 -- POST-HOC TARGET CHECK
------------------------------------------------------------------------------
  *** POST-HOC: this comparison was computed AFTER seeing the data. ***

  the 10 sequence-nearest nulls (dist_222 ascending, ties by ascending bg_id): ['AV_220', 'AV_233', 'AV_209', 'AV_204',
  'AV_242', 'G_Y197V', 'AV_195', 'G_I192T', 'G_P254F', 'G_L178T']

    [full]  POST-HOC mean rho of the 10 sequence-nearest nulls = -0.055749
    [full]  POST-HOC mean rho of Arm S (n = 18) = -0.065159
    [full]  POST-HOC difference (Arm S - seq-10 nearest) = -0.009411
    [H]  POST-HOC mean rho of the 10 sequence-nearest nulls = -0.059109
    [H]  POST-HOC mean rho of Arm S (n = 18) = -0.070181
    [H]  POST-HOC difference (Arm S - seq-10 nearest) = -0.011072

  RECOMPUTED vs TARGET:
    D14.2 mean rho, 10 sequence-nearest nulls (full)   recomputed = -0.055749   target = -0.055700   |diff| = 4.872e-05   AGREE
    D14.2 mean rho, 10 sequence-nearest nulls (H)      recomputed = -0.059109   target = -0.059100   |diff| = 8.832e-06   AGREE
    D14.2 mean rho, Arm S (full)                       recomputed = -0.065159   target = -0.065200   |diff| = 4.067e-05   AGREE
    D14.2 mean rho, Arm S (H)                          recomputed = -0.070181   target = -0.070200   |diff| = 1.876e-05   AGREE

------------------------------------------------------------------------------
D14.3 -- FIGURE
------------------------------------------------------------------------------
  *** SKIPPED: matplotlib is not importable (ModuleNotFoundError: No module named 'matplotlib').
  Per the task doc rule 9 it is NOT installed.  data/processed/phase2_diagnostics/rho_vs_d3.png was NOT written.
  Every number the figure would have shown is in the D14.0 bin table above; no result depends on the figure.

  RECOMPUTED vs TARGET: 4/4 AGREE, 0 DISAGREE
```

Verdict: **PASS** (with D14.3 **SKIPPED**).

- **The 0 A bin has NO DISCONTINUITY.** Arm S mean rho (-0.065159 full, -0.070181 H) and the resolved 3D-nearest-null mean (-0.064933 full, -0.073769 H) differ by **-0.000227** (full) and **+0.003588** (H), both with background-level bootstrap CIs that include zero ([-0.017265, +0.015162] and [-0.016695, +0.020572]). The sign even flips between views. The (0,12] bin is labelled n = 6 and UNSTABLE at every use.
- **The gradient is monotone in bin means over the whole range**: -0.0652 / -0.0649 / -0.0574 / -0.0278 / +0.0003 / +0.0245 (full). Arm S at 0 A is statistically indistinguishable from the 3D-nearest nulls at 5-10.5 A; the rise begins between 12 and 30 A.
- **mean|delta| is NOT monotone in the bins and moves in the opposite direction at the near end**: Arm S 0.0891, (0,12] 0.0694, (12,20] 0.0961, (20,30] 0.0566, (30,45] 0.0470, (45,inf) 0.0452. The near-222 bins are the LOW-shift bins and the far bins are also low, with a peak at (12,20]. The bins are not matched for shift; this is printed in every bin for exactly that reason.
- **D14.2 POST-HOC targets reproduce to < 5e-5**: 10 sequence-nearest nulls -0.055749 / -0.059109; Arm S -0.065159 / -0.070181.
- **D14.3 SKIPPED**: `matplotlib` is not importable in `venv` and was **not** installed. `data/processed/phase2_diagnostics/rho_vs_d3.png` was **not** written. No result depends on the figure.
- The 11 unresolved backgrounds are named, excluded, and never imputed: `AV_19`, `AV_396`, `AV_5`, `AV_655`, `G_E168S`, `G_E16V`, `G_K27I`, `G_N12P`, `G_N3K`, `G_P395F`, `G_S23A`.

Files created/modified:
- `scripts/142_phase2_diag3_bins.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D14_FULL_OUTPUT.txt` (new, 138 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- Nothing protected, no earlier log, no earlier script, not `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **The discontinuity the task doc was looking for is not there, and its absence is the informative part.** D10a/D16 exist because A222V sits at distance 0 where no null sits, so every parametric fit extrapolates. D14 shows that on the raw, model-free picture there is **no step at 0**: the 18 Arm S backgrounds, all at exactly 0 A, sit at the same mean rho as the six 3D-nearest nulls 5-10.5 A away. So the extrapolation in D10a/D16 is an extrapolation of a *fitted functional form* into a region the data are already dense in, not an extrapolation into empty data.
2. **That cuts against the more extreme reading of "spatial-overlap with no long-range content"** and is why I am not going to let D15 be read that way unless its own numbers say so. The bin means are what they are: a smooth gradient, no 0 A cliff.
3. **`G_I192T` is the 3D-nearest background of all (5.06 A) and it has rho -0.033, roughly half the Arm S mean.** It is the one member of the (0,12] bin that is nowhere near the others; the other five range -0.047 to -0.085. The bin mean is therefore dragged toward zero by a single background, and the bin's n = 6 is not the only reason it is unstable.
4. **`(12, 20]` contains the most negative null of all, `G_P254F` (-0.096244), and has the HIGHEST mean|delta| of any bin (0.0961).** So the deepest single negative rho sits in the high-shift, mid-distance bin - a reminder that rho_b's extremes are not confined to the near-222 region.
5. Two first-run crashes, both caught before any result was reported and both trivial: a leftover placeholder `print` in the membership loop, and a missing `t0 = time.time()` that only surfaced on the final `Elapsed` line after every number had already printed. Re-run, not hand-patched.

## [D15] - Far-variant restriction: does the anchor survive without variants near 222? (the mechanism test)
Status: PASS
Time started / finished: 2026-09-30 (state check; script 143 read and SUPERSEDED by 144 - see flag 1; smoke at N_DRAW=20 N_BOOT=300; full at N_DRAW=200 N_BOOT=10000 SEED=0, **176.7 s wall, timed not guessed**)

What I did:
1. **Verified state first**, as instructed. `scripts/140,141,142` and `scripts/lib/phase2_diag3.py` exist. `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` sha256 = `8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176` **MATCHES** the value D12 reported. D1 table sha256 `e397a442...3796` and 3D table sha256 `69914df9...12de` both MATCH. The log already contained D12, D13, D14 and nothing else; those entries were not touched.
2. **Script 143 already existed from the stopped session.** See flag 1 below: it was read, its defect identified, and it was NOT overwritten. I wrote **`scripts/144_phase2_diag3_farvariants.py`** as the superseding script, carrying 143's pre-registered docstring forward with one behavioural fix and one hoist.
3. Wrote the pre-registered docstring before the first run of 144 (carried forward from 143, unchanged in substance): construction, all four radii reported and none selected, S1 primary / S2 sensitivity, both sequence sensitivities, both hard gates, both resampling units stated per statistic, and the limits.
4. Ran **D15-G1 (HARD) first**, then all variants, then **D15-G2 (HARD)**, then the matched-deletion control.

Actual output (verbatim, from `PHASE2_DIAG3_D15_FULL_OUTPUT.txt`):

```
==============================================================================
D15 -- FAR-VARIANT RESTRICTION: DOES THE ANCHOR SURVIVE WITHOUT VARIANTS NEAR 222?  (script 144)
==============================================================================
NO MODEL SCORING.  NO torch / esm / thermompnn / Biopython import anywhere in this file.
  N_DRAW=200 N_BOOT=10000 SEED=0
RESAMPLING UNITS (not interchangeable):
  * A222V's rho on a row subset  -> POSITION CLUSTER (whole retained target positions), identity gate 1e-12.
  * anything ACROSS backgrounds   -> BACKGROUND, per-background rho_b held FIXED.
  * the matched-deletion control  -> NO resampling inside a draw; it is a recomputation on a deleted row set.
  * p_spec and every row count    -> NO resampling.

------------------------------------------------------------------------------
GATE D15-G1 (HARD) -- loader, far fractions, unrestricted baselines, baseline targets
------------------------------------------------------------------------------
  [PASS] D15-G1 rho table sha256: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  [PASS] D15-G1 3D table sha256: 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
  [PASS] D15-G1a loader vs stored ca_dist_222: max|diff| = 7.105e-15 A over 9595 rows (gate < 1e-09); unresolved positions in this frame = 0
  [PASS] D15-G1b monomer far (>10 A): 9232/9595 = 96.2168% (script 107/126: 9232 = 96.22%)
  [PASS] D15-G1b dimer-aware far (>10 A): 9128/9595 = 95.1329% (script 107/126: 9128 = 95.13%)
  [full] frame positions in view = 654, A222V rows = 10757, per-background rows min = 10738, median = 10741, max = 10757
  [H] frame positions in view = 455, A222V rows = 7526, per-background rows min = 7507, median = 7512, max = 7526
  [PASS] D15-G1c all 96 rho_full and rho_H vs background_rho_table.csv: 192 comparisons; max|diff| = 4.990e-10 (gate < 1e-09)
  [PASS] D15-G1c A222V rho (full and H): max|diff| = 0.000e+00 (gate < 1e-09); values -0.088118064 / -0.090021683
  [PASS] D15-G1d unrestricted gradient on resolved N (n=67) (full): got +0.731577372 vs +0.731577372 |diff|=1.899e-10
  [PASS] D15-G1d A222V rho unrestricted (full): got -0.088118064 vs -0.088118064 |diff|=2.489e-10
  [PASS] D15-G1d unrestricted gradient on resolved N (n=67) (H): got +0.713319366 vs +0.713319366 |diff|=3.985e-10
  [PASS] D15-G1d A222V rho unrestricted (H): got -0.090021683 vs -0.090021683 |diff|=3.340e-11

  11/11 D15-G1 checks PASS, 0 FAIL
  GATE PASS: D15-G1 satisfied.  The far-filter analysis may run.

------------------------------------------------------------------------------
GEOMETRY BOOKKEEPING -- what each R removes, and what is dropped for being unresolved
------------------------------------------------------------------------------
  frame positions = 654;  position 222 itself IS NOT a frame target position
  chain A resolves 40..651 with internal gaps 161-171 and 392-396, so positions 2-39, 161-171, 392-396 and
  652-656 have NO chain-A coordinates

  [full] positions in view = 654;  resolved = 595;  UNRESOLVED = 59 (2-39, 161-171, 392-396, 652-656)
  [full] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM EVERY 3D VARIANT INCLUDING R = 0, NEVER IMPUTED:
         A222V 1017 of 10757 rows; per background min = 998, max = 1017
  [full] d3_222(p) over the 595 RESOLVED view positions, percentiles:
           p0=3.805  p1=6.452  p5=10.528  p10=14.500  p25=21.518  p50=34.969  p75=51.913  p90=60.327  p100=81.011   (A)
  [full] frame positions within each R of 222 (resolved only), i.e. what the S1 filter removes:
           R =    0 A: k_R =   0 positions removed, 595 retained  (min d3_222 among retained = 3.805 A)
           R =   10 A: k_R =  23 positions removed, 572 retained  (min d3_222 among retained = 10.029 A)
           R =   20 A: k_R = 121 positions removed, 474 retained  (min d3_222 among retained = 20.098 A)
           R =   30 A: k_R = 247 positions removed, 348 retained  (min d3_222 among retained = 30.091 A)

  [H] positions in view = 455;  resolved = 418;  UNRESOLVED = 37
  [H] *** ROWS AT UNRESOLVED POSITIONS DROPPED FROM EVERY 3D VARIANT INCLUDING R = 0, NEVER IMPUTED:
         A222V 640 of 7526 rows; per background min = 621, max = 640
  [H] d3_222(p) over the 418 RESOLVED view positions, percentiles:
           p0=5.058  p1=6.721  p5=11.350  p10=14.645  p25=21.587  p50=35.289  p75=52.271  p90=60.731  p100=81.011   (A)
  [H] frame positions within each R of 222 (resolved only):
           R =    0 A: k_R =   0 positions removed, 418 retained  (min d3_222 among retained = 5.058 A)
           R =   10 A: k_R =  13 positions removed, 405 retained  (min d3_222 among retained = 10.029 A)
           R =   20 A: k_R =  86 positions removed, 332 retained  (min d3_222 among retained = 20.098 A)
           R =   30 A: k_R = 172 positions removed, 246 retained  (min d3_222 among retained = 30.091 A)
```

**The far-variant restriction table (S1, both views, all four radii) — the headline of this session:**

```
------------------------------------------------------------------------------
D15 FAR-VARIANT RESTRICTION TABLE -- S1, both views, all four radii
------------------------------------------------------------------------------
   view   R (A)   k_R pos    A222V rho         pos-cluster 95% CI  excl 0          gradient n=67                 its 95% CI   p_spec n=78            at or below
   full       0         0 -0.076685523 [-0.110517, +0.052946]   False   +0.698473511  [+0.543521, +0.803731]      0.037975        AV_220, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.698473511, +0.698473511]   -> S1 gradient is INSIDE it;  frac draws at or below S1 = 1.0000, at or above = 1.0000
   full      10        23 -0.079237139 [-0.108943, +0.053475]   False   +0.689454255  [+0.530630, +0.794968]      0.037975        AV_220, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.680406565, +0.706900130]   -> S1 gradient is INSIDE it;  frac draws at or below S1 = 0.2800, at or above = 0.7200
   full      20       121 -0.065947891 [-0.106446, +0.077385]   False   +0.662097177  [+0.518283, +0.763801]      0.037975        AV_220, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.663147261, +0.723050983]   -> S1 gradient is OUTSIDE it;  frac draws at or below S1 = 0.0150, at or above = 0.9850
   full      30       247 -0.027360127 [-0.126369, +0.088052]   False   +0.400678440  [+0.189417, +0.569595]      0.063291 AV_145, AV_220, G_L318F, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.615026439, +0.731210217]   -> S1 gradient is OUTSIDE it;  frac draws at or below S1 = 0.0000, at or above = 1.0000
      H       0         0 -0.080432398 [-0.136966, +0.050697]   False   +0.688316871  [+0.530040, +0.793972]      0.037975        AV_220, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.688316871, +0.688316871]   -> S1 gradient is INSIDE it;  frac draws at or below S1 = 1.0000, at or above = 1.0000
      H      10        13 -0.082101889 [-0.133307, +0.060709]   False   +0.686580864  [+0.526713, +0.797779]      0.037975        AV_220, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.675493864, +0.702835977]   -> S1 gradient is INSIDE it;  frac draws at or below S1 = 0.3750, at or above = 0.6250
      H      20        86 -0.063596629 [-0.131090, +0.087967]   False   +0.640347202  [+0.484996, +0.749546]      0.050633 AV_220, G_L318F, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.642046793, +0.720171605]   -> S1 gradient is OUTSIDE it;  frac draws at or below S1 = 0.0250, at or above = 0.9750
      H      30       172 -0.024367374 [-0.145818, +0.109530]   False   +0.241344907  [-0.006500, +0.461143]      0.101266 AV_145, AV_220, AV_328, AV_650, G_G317Q, G_L318F, G_P254F
        matched-deletion range for the gradient (n=200 draws): [+0.602546643, +0.726412751]   -> S1 gradient is OUTSIDE it;  frac draws at or below S1 = 0.0000, at or above = 1.0000
```

**The sequence sensitivities (S1 only; Rs = 25, 50) — reported, none selected:**

```
  S1 SEQ Rs = 25 [full]: A222V rho = -0.081584044, CI [-0.115971, +0.055396] INCLUDES ZERO; gradient n=67 = +0.695360671 [+0.544574, +0.797086] EXCLUDES ZERO
  S1 SEQ Rs = 50 [full]: A222V rho = -0.072880941, CI [-0.107525, +0.069562] INCLUDES ZERO; gradient n=67 = +0.680933852 [+0.522444, +0.786901] EXCLUDES ZERO
  S1 SEQ Rs = 25 [H]:    A222V rho = -0.087875866, CI [-0.144621, +0.054462] INCLUDES ZERO; gradient n=67 = +0.689214806 [+0.531313, +0.796074] EXCLUDES ZERO
  S1 SEQ Rs = 50 [H]:    A222V rho = -0.077360307, CI [-0.135943, +0.073553] INCLUDES ZERO; gradient n=67 = +0.650044897 [+0.475784, +0.771330] EXCLUDES ZERO
```

**S2 (far from both 222 and the background) — DESCRIPTIVE, no matched control:**

```
  S2 R =  0 A [full]: gradient n=67 = +0.698473511, n=85 = +0.780769661
  S2 R = 10 A [full]: gradient n=67 = +0.689454255, n=85 = +0.772866140
  S2 R = 20 A [full]: gradient n=67 = +0.662097177, n=85 = +0.785737588
  S2 R = 30 A [full]: gradient n=67 = +0.400678440, n=85 = +0.676943908
  S2 R =  0 A [H]:    gradient n=67 = +0.688316871, n=85 = +0.777402074
  S2 R = 10 A [H]:    gradient n=67 = +0.686580864, n=85 = +0.770372359
  S2 R = 20 A [H]:    gradient n=67 = +0.640347202, n=85 = +0.779355863
  S2 R = 30 A [H]:    gradient n=67 = +0.241344907, n=85 = +0.589995363
```

**D15-G2 (HARD) — the deletion function is exact:**

```
  [PASS] D15-G2a zero-deletion == R=0 baseline (full): max|diff| over rho_A222V, both gradients and both k's = 0.000e+00 (required EXACTLY 0)
  [PASS] D15-G2b actual S1 removed set reproduces S1 (full, R = 0): 0 positions removed; max|diff| over all 97 rho and every reported statistic = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (full, R = 10): 23 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (full, R = 20): 121 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (full, R = 30): 247 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2a zero-deletion == R=0 baseline (H): max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (H, R = 0): 0 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (H, R = 10): 13 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (H, R = 20): 86 positions removed; max|diff| = 0.000e+00
  [PASS] D15-G2b actual S1 removed set reproduces S1 (H, R = 30): 172 positions removed; max|diff| = 0.000e+00
```

Verdict: **PASS.** Both hard gates pass. D15-G1 11/11; D15-G2 10/10 at **exactly** 0; position-cluster identity gate `max|diff| = 0.000e+00` across every variant and view.

**DOES THE GRADIENT SURVIVE AMONG DISTAL VARIANTS? YES, AND THE FALL IS ATTRIBUTABLE TO THE REMOVED POSITIONS.**

- **The gradient survives R = 10 A essentially intact.** Full frame: 0.6985 -> 0.6895 (a fall of 0.0090), and the matched-deletion range at R = 10 is **[+0.680407, +0.706900]** - the S1 value sits **INSIDE** it, with 72% of random 23-position deletions giving a gradient *above* the S1 value. H: 0.6883 -> 0.6866, inside [+0.675494, +0.702836], 62.5% above. **Deleting 23 random positions is if anything slightly WORSE for the gradient than deleting the 23 nearest ones, so nothing about R = 10 is attributable to those positions.**
- **The gradient does NOT survive R = 20 A or R = 30 A.** At R = 20 full, the gradient falls to 0.6621 against a matched-deletion range of [+0.663147, +0.723051] - **OUTSIDE** (below), with 98.5% of random 121-position deletions giving a *higher* gradient. At R = 30 full it collapses to 0.4007 against [+0.615026, +0.731210] - far **OUTSIDE**, 100% of draws higher. The H frame is the same story and slightly worse: 0.6403 at R = 20 (outside, 97.5% higher) and 0.2413 at R = 30 (outside, 100% higher; its own bootstrap CI now includes zero, [-0.006500, +0.461143]).
- **So the removal of target variants within 30 A of 222 is what destroys the gradient.** A random deletion of the same number of positions does not reproduce that collapse. That is the mechanism result, and it is adverse to the long-range reading.
- **The S2 sensitivity agrees** at R = 30 (+0.4007 full, +0.2413 H) but is DESCRIPTIVE with no matched control, so it corroborates rather than licenses the attribution.
- **The sequence sensitivities disagree with the 3D ones at the same nominal severity.** Removing |p - 222| <= 50 (495 positions retained, full) leaves the gradient at **+0.680934** with a CI excluding zero, versus +0.4007 for the 3D R = 30 filter. Removing |p-222| <= 50 in *sequence* is much more destructive per position than removing 30 A in *space* (247 positions). **The statistic is tracking 3D distance to 222, not sequence distance to 222.**
- **THE ANCHOR PERSISTS AMONG DISTAL VARIANTS, WEAKENING MONOTONICALLY.** A222V's rho on the retained rows: -0.0767 (R=0) -> -0.0792 (R=10) -> -0.0659 (R=20) -> **-0.0274** (R=30) full; -0.0804 -> -0.0821 -> -0.0636 -> **-0.0244** H. `p_spec` stays at 2/78 = 0.037975 through R = 20 and rises to 4/78 = 0.063291 at R = 30 (full) and 7/78 = 0.101266 (H). **A222V's own negative association is halved by removing target variants within 30 A of 222.**
- **The honest caveat, and it is not small: A222V's position-cluster CI INCLUDES ZERO in EVERY variant on BOTH frames** - at R = 0, at R = 10, at R = 20, at R = 30, and on both sequence sensitivities, on both views. Twelve out of twelve. That is true of the unrestricted baseline too ([-0.110517, +0.052946] at R = 0 resolved; the doc's own quoted Phase 1 CI [-0.117333, -0.059511] excludes zero only because it used a different bootstrap on the full row set). **I am not claiming A222V's own rho is established by this task; I am reporting that whatever signal is there is concentrated near 222 and is not carried by distal variants.** Reported with the same directness as the gradient result.
- Position 222 is **not itself a frame target position**; the nearest resolved frame target is at 3.805 A. k_R = 0 / 23 / 121 / 247 (full) and 0 / 13 / 86 / 172 (H).

Files created/modified:
- `scripts/144_phase2_diag3_farvariants.py` (new, supersedes 143).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D15_FULL_OUTPUT.txt` (new, 688 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- **Not modified:** `scripts/143_phase2_diag3_farvariants.py` (read only), `scripts/140/141/142`, `scripts/lib/phase2_diag.py`, `scripts/lib/phase2_diag3.py`, any earlier log, any protected file. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **Script 143 existed from the stopped session and was never overwritten.** It ran only as far as a `N_DRAW=5 N_BOOT=200` smoke and **crashed before producing any output file**; `PHASE2_DIAG3_D15_FULL_OUTPUT.txt` did not exist when this session resumed, and there is no D15 entry in the log. Its defect was in `pos_cluster_boot`: the cluster-relative offsets `kept_base + j` were used to index `rows_sorted`, which holds indices into the ORIGINAL row arrays, instead of indexing the retained arrays `d`/`y`. On the R = 0 variant that produced `IndexError: index 10075 is out of bounds for axis 0 with size 9740`. **144 is 143 with that one line fixed** (`idx = np.repeat(kept_base, cnt)[rep] + j; draws[i] = rho_of(d[idx], y[idx])`) plus a hoist of the per-background `d3_b` computation out of S2's 96-background loop. **No behavioural change to any statistic.** Both scripts are on disk; 143 is dead code and is disclosed rather than deleted.
2. **Two further indexing bugs in 144's lineage were caught in smoke and are disclosed**: `geo[view]["univ"]` originally held position VALUES where indices into `POSV` were needed, which silently produced `k_R = 22 / 118 / 242` instead of the correct `23 / 121 / 247` and a row of `nan` percentiles; and `sizes` was built with `minlength = number of retained clusters` rather than `npos`. Both were caught before any number was reported, because the correct `k_R` had already been established independently and the two disagreed.
3. **The matched-deletion control earned its keep immediately, and it cuts against the interesting result.** Without it, R = 20 (full) would have looked like a mild attenuation of the gradient and R = 30 like a collapse, with no way to tell that ordinary row thinning does the same thing. With it, R = 20 and R = 30 are *outside* the random-deletion range, so the collapse is real and attributable.
4. **The R = 0 matched-deletion range is degenerate by construction** ([+0.698474, +0.698474], k_R = 0, so every draw is the same row set). It is printed that way rather than hidden, and the INSIDE flag at R = 0 is vacuous. Stated so nobody reads R = 0 as evidence.
5. **`p_spec` under restriction is a comparison of differently-thinned statistics.** A222V's rho and each null's rho_b are computed on each background's own usable rows, so the row sets differ from background to background. This is disclosed in the docstring and in the printed limitations, not corrected.
6. **S2 dropped no background in any view at any radius** - the per-line "backgrounds with NO d3_b" lists are empty. That is because a background only needs *its own* position resolved to define `d3_b`, and all 96 background positions except the 11 named earlier are resolved; the 11 unresolved backgrounds are unresolved *target-frame* positions, which S2's row filter drops for everyone identically. Worth stating because the doc anticipated some backgrounds would drop out and none did.

## [D16] - Adjustment with no fitted functional form and no extrapolation (isotonic)
Status: PASS
Time started / finished: 2026-09-30 (1.2 s wall - deterministic, no resampling; N_BOOT/N_PERM not read by this script)

What I did:
1. Wrote `scripts/145_phase2_diag3_isotonic.py` with the pre-registered docstring **before its first run**: primary designated in advance (D16b on `d3_CA`), all four variants reported with none selected, leave-one-out for nulls and out-of-sample for A222V and Arm S, the `increasing=True` direction justified from the observed sign, the sklearn-then-scipy fallback with no installation, and the limits including D16b's disclosed stage-1 optimism.
2. `sklearn.isotonic.IsotonicRegression(increasing=True, out_of_bounds='clip')` imported; no fallback needed and nothing installed.
3. Ran. Both D16 stage-1 gates against D9's printed PRIMARY reproduce.

Actual output (verbatim, from `PHASE2_DIAG3_D16_FULL_OUTPUT.txt`):

```
ISOTONIC IMPLEMENTATION: sklearn.isotonic.IsotonicRegression(increasing=True, out_of_bounds='clip')
  increasing=True is the OBSERVED direction (rho is more negative near 222), not a free parameter.  out_of_bounds='clip' gives the FLAT extrapolation at the boundary that the task doc requires.

------------------------------------------------------------------------------
HOW MUCH DATA SETS g(0)  (printed before any fit)
------------------------------------------------------------------------------
  d3_CA, resolved nulls: n = 67, minimum distance = 5.058, nulls within 10 A = 3, within 10.5 A = 5, within 12 A = 6, within 20 A = 14
    *** g(0) IS SET BY THE 6 NULL(S) WITHIN 12 A, AT MOST. ***
  dist_seq, all 78 nulls: n = 78, minimum distance = 2.000, nulls within 10 A = 1, within 12 A = 2, within 20 A = 5
    *** g(0) IS SET BY THE 2 NULL(S) WITHIN 12 A, AT MOST. ***

------------------------------------------------------------------------------
D16a -- RAW rho, ISOTONIC ON d3_CA OVER THE RESOLVED NULLS (n = 67)
------------------------------------------------------------------------------

  --- D16a  raw rho ~ g(d3_CA)  [full] ---
    fit on n = 67;  distance range of the fitted support = [5.058, 76.194]
    g(0) = fitted value at the SMALLEST null distance (5.058) = -0.068487   *** FLAT CLIPPED EXTRAPOLATION ***
    fitted STEP FUNCTION g: 14 pooled block(s) over 67 nulls
      block  1: g = -0.068487   nulls with distance in (5.058, 5.058]   n =   1   <-- g(0) IS THIS BLOCK'S VALUE
      block  2: g = -0.068487   nulls with distance in (5.058, 10.313]   n =   4
      block  3: g = -0.067797   nulls with distance in (10.313, 10.537]   n =   1
      block  4: g = -0.067797   nulls with distance in (10.537, 16.280]   n =   3
      block  5: g = -0.054367   nulls with distance in (16.280, 17.648]   n =   1
      block  6: g = -0.054367   nulls with distance in (17.648, 18.650]   n =   3
      block  7: g = -0.044832   nulls with distance in (18.650, 18.862]   n =   1
      block  8: g = -0.044832   nulls with distance in (18.862, 20.331]   n =   3
      block  9: g = -0.025156   nulls with distance in (20.331, 20.626]   n =   1
      block 10: g = -0.025156   nulls with distance in (20.626, 33.766]   n =  19
      block 11: g = -0.002566   nulls with distance in (33.766, 36.759]   n =   1
      block 12: g = -0.002566   nulls with distance in (36.759, 40.571]   n =   4
      block 13: g = +0.027968   nulls with distance in (40.571, 40.814]   n =   1
      block 14: g = +0.027968   nulls with distance in (40.814, 76.194]   n =  24
    *** the near-222 end of g is set by the 6 null(s) within 12 A ***
    A222V r_A = -0.019631
    #{{b in nulls : r_b <= r_A}} = 12 of 67
    p_spec_adj = (1 + 12)/(1 + 67) = 0.191176   -> ABOVE the frozen numeric threshold 0.05
    A222V signed rank within nulls u {{A222V}} = 13/68  (rank 1 = most negative residual)
    D16d  Arm S (n = 18) at or below r_A: k = 1  ->  rank fraction (1 + 1)/(1 + 18) = 0.1053   *** RANK FRACTION, NOT A TEST ***
         1     A222_C    -0.025043      YES
         2     A222_T    -0.017403       no
```

```
  [full] stage 1 check: r_A = -0.066425  (D9's PRIMARY; AGREE, |diff| < 2e-6)
  --- D16b  r^shift ~ g(d3_CA)  [PRIMARY]  [full] ---
    g(0) = -0.047207
    A222V r_A = -0.019217
    p_spec_adj = (1 + 20)/(1 + 67) = 0.308824   -> ABOVE the frozen numeric threshold 0.05
    A222V signed rank within nulls u {{A222V}} = 21/68
    D16d  Arm S at or below r_A: k = 1 -> rank fraction 0.1053   *** RANK FRACTION, NOT A TEST ***
```

**D16 side-by-side (none selected; PRIMARY marked):**

```
                                     variant  view  n nulls        g(0)         r_A    k  p_spec_adj     rank  vs frozen threshold
         D16a  raw rho ~ g(d3_CA)  [resN=67]  full       67   -0.068487   -0.019631   12    0.191176   13/68             ABOVE 0.05
         D16b  r^shift ~ g(d3_CA)  [PRIMARY]  full       67   -0.047207   -0.019217   20    0.308824   21/68             ABOVE 0.05
     D16c-a  raw rho ~ g(dist_seq)  [all 78]  full       78   -0.084598   -0.003520   37    0.481013   38/79             ABOVE 0.05
     D16c-b  r^shift ~ g(dist_seq)  [all 78]  full       78   -0.080278   +0.013854   53    0.683544   54/79             ABOVE 0.05
         D16a  raw rho ~ g(d3_CA)  [resN=67]     H       67   -0.076599   -0.013423   22    0.338235   23/68              ABOVE 0.1
         D16b  r^shift ~ g(d3_CA)  [PRIMARY]     H       67   -0.051076   -0.017616   19    0.294118   20/68              ABOVE 0.1
     D16c-a  raw rho ~ g(dist_seq)  [all 78]     H       78   -0.094480   +0.004459   43    0.556962   44/79              ABOVE 0.1
     D16c-b  r^shift ~ g(dist_seq)  [all 78]     H       78   -0.089189   +0.020497   58    0.746835   59/79              ABOVE 0.1

  RECOMPUTED vs TARGET: 2/2 AGREE, 0 DISAGREE
```

Verdict: **PASS.**

- **PRIMARY D16b: `g(0)` = -0.047207 (full) / -0.051076 (H); `r_A` = -0.019217 / -0.017616; `p_spec_adj` = 0.308824 (full, k = 20 of 67) / 0.294118 (H, k = 19 of 67); signed rank 21/68 and 20/68.** All **above** the frozen numeric thresholds.
- **D16a: `g(0)` = -0.068487 / -0.076599; `r_A` = -0.019631 / -0.013423; `p_spec_adj` = 0.191176 / 0.338235; rank 13/68 and 23/68.** All **above** the frozen thresholds.
- **D16c (sequence-distance sensitivities): 0.481013 / 0.556962 (raw) and 0.683544 / 0.746835 (shift-adj).** All **above**.
- **`g(0)` is set by 6 nulls (3D) or 2 nulls (sequence) within 12 A**, printed before any fit. The doc's "about 6 nulls within 10.5 A" is 6 within 12 A and 5 within 10.5 A; the count is printed so a reader can apply either.
- **The form-dependence spans 0.191 to 0.747 across four models - nearly a four-fold range - and every one is ABOVE the frozen thresholds.** The direction is unanimous and the size is not interpretable.
- **D16d: A222V's same-site rank fraction is 0.1053 (k = 1, `A222_C`) under BOTH D16a and D16b, on BOTH views** - identical to D13's raw and shift-adjusted results. Adding a no-extrapolation distance adjustment does not move A222V within its own site. *** RANK FRACTION, n = 19, NOT A TEST. ***

Files created/modified:
- `scripts/145_phase2_diag3_isotonic.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D16_FULL_OUTPUT.txt` (new, 368 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- Nothing protected, no earlier log, no earlier script, not `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **Isotonic does not rescue the anchor, but it also does not bury it the way a parametric fit does.** Every isotonic `p_spec_adj` (0.19-0.75) sits **above** the frozen thresholds, exactly as the three parametric forms did - but they cluster far below the log1p forms' 0.89-0.90 and the 3D form's 1.00. `r_A` stays negative in 6 of 8 cells (turning positive only in the two sequence-distance two-stage cells, +0.0139 and +0.0205).
2. **`g(0)` is genuinely set by very few points and the step function shows it.** In D16a (full), block 1 holds **one** null (5.058 A) and block 2 four more; `g(0)` = -0.068487 is the mean of a 5-null pooled region. That is a thinner foundation than the parametric fits' apparent smoothness, and it is printed block by block rather than summarised.
3. **The isotonic fit pools 67 nulls into 14 blocks, and 24 of them share the top block.** The near end is fine-grained and the far end is coarse, which is the correct behaviour for this data but means `g` is not a smooth monotone surface anybody should read values off.
4. Six first-run crashes, all caught before any number was reported and all in the wiring rather than the statistics: a dead `fit` closure with unreachable code inside `get_isotonic`; a duplicated and discarded first D16b call passing `None` as Arm S stage-1 values; `blocks` referenced after being replaced by the fitter's own thresholds; a 3-tuple unpack of a 2-tuple `oos`; `p3.verdict(0.0, view)` returning a `(label, threshold)` tuple where a scalar was needed; and a missing `r_A` key in the summary dict. Each was fixed at source and the run repeated; the numbers are identical across the final runs.

## [D16e] - Arm S under the joint models, exact
Status: PASS
Time started / finished: 2026-09-30 (0.9 s wall - deterministic, no resampling; N_BOOT/N_PERM not read by this script)

What I did:
1. Wrote `scripts/146_phase2_diag3_arms_joint.py` with the pre-registered docstring **before its first run**: the four models refitted at full precision (no hand-typed coefficients, no 6-dp rounding), leave-one-out for nulls and out-of-sample for A222V and Arm S so all three are exchangeable, five E-gates on the four published fits, the two-part reporting list, the rank-fractions-not-tests rule, and the limits including the restatement of D12's K3.
2. Ran the E-gates **first**. **They failed on the first attempt (2 of 18) and the task stopped**, as pre-registered.
3. Diagnosed the cause, fixed it at source, and re-ran. Cause was mine, not a data disagreement - see flag 1.

Actual output (verbatim, from `PHASE2_DIAG3_D16E_FULL_OUTPUT.txt`):

```
==============================================================================
D16e -- ARM S UNDER THE JOINT MODELS, EXACT  (script 146)
==============================================================================
*** RANK FRACTIONS, n = 19.  NOT TESTS.  No p-value is computed anywhere in this task. ***
NO 6-dp ROUNDING AND NO HAND-TYPED COEFFICIENTS: all four models are refitted here at full precision from script 125's own rows.
RESAMPLING UNIT: NONE.  No bootstrap, no permutation.  N_BOOT / N_PERM are not read by this script.
*** THE DOC'S TARGETS FOR THIS TASK ARE ITS OWN POST-HOC CALCULATIONS FROM PRINTED 6-dp VALUES AND ARE THEREFORE
APPROXIMATE BY CONSTRUCTION.  Each is recomputed and printed beside its target; a mismatch is reported, never forced. ***
  [PASS] E5 background_rho_table.csv sha256: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  [PASS] E5 background_3d_distance.csv sha256: 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
  Arm S 18 (all position 222, dist_seq 0, d3_CA 0); nulls 78; resolved nulls 67

------------------------------------------------------------------------------
GATES -- the four models must reproduce the published Diagnostics II values exactly before Arm S is scored
------------------------------------------------------------------------------
  [PASS] E1 M1  shift-only r_A (full): got -0.066424633 vs -0.066425 |diff|=3.674e-07
  [PASS] E1 M1  shift-only k (full): got 2 vs 2
  [PASS] E1 M1  shift-only r_A (H): got -0.068691937 vs -0.068692 |diff|=6.262e-08
  [PASS] E1 M1  shift-only k (H): got 2 vs 2
  [PASS] E4 M2  + linear dist_seq r_A (full): got -0.033710698 vs -0.033711 |diff|=3.025e-07
  [PASS] E4 M2  + linear dist_seq k (full): got 9 vs 9
  [PASS] E4 M2  + linear dist_seq r_A (H): got -0.035947854 vs -0.035948 |diff|=1.459e-07
  [PASS] E4 M2  + linear dist_seq k (H): got 10 vs 10
  [PASS] E2 M3  + log1p(dist_seq) r_A (full): got +0.045226926 vs +0.045227 |diff|=7.356e-08
  [PASS] E2 M3  + log1p(dist_seq) k (full): got 69 vs 69
  [PASS] E2 M3  + log1p(dist_seq) r_A (H): got +0.047030107 vs +0.047030 |diff|=1.071e-07
  [PASS] E2 M3  + log1p(dist_seq) k (H): got 70 vs 70
  [PASS] E3 M4  + log1p(d3_CA) r_A (full): got +0.093681340 vs +0.093681 |diff|=3.397e-07
  [PASS] E3 M4  + log1p(d3_CA) k (full): got 67 vs 67
  [PASS] E3 M4  + log1p(d3_CA) r_A (H): got +0.098714560 vs +0.098715 |diff|=4.397e-07
  [PASS] E3 M4  + log1p(d3_CA) k (H): got 67 vs 67

  18/18 E-gates PASS.  Arm S may be scored.
```

**Arm S scored out of sample at distance 0, all four models (full frame):**

```
  ================ M1  shift-only ================
    [full]  OLS rho ~ mean|delta|*-0.726287  intercept +0.029386   (fit on n = 78)
    ARM S mean residual = -0.029845   sd = 0.017533
    mean PREDICTED rho at d=0 = -0.035315   vs   mean OBSERVED rho at d=0 = -0.065159   overshoot = +0.029845
    most negative OBSERVED null rho = G_P254F -0.096244   (A222V's predicted rho at d=0 = -0.021693 -> not below every observed null)
    A222V rank within Arm S u {A222V} = 2/19   rank fraction = 0.1053   *** RANK FRACTION, NOT A TEST ***

  ================ M2  + linear dist_seq ================
    [full]  OLS rho ~ mean|delta|*-0.363298  dist*+0.000215  intercept -0.028857   (fit on n = 78)
    ARM S mean residual = -0.003938   sd = 0.015200
    mean PREDICTED rho at d=0 = -0.061221   vs   mean OBSERVED rho at d=0 = -0.065159   overshoot = +0.003938
    A222V predicted rho at d=0 = -0.054407 -> not below every observed null
    A222V rank = 2/19   rank fraction = 0.1053

  ================ M3  + log1p(dist_seq) ================
    [full]  OLS rho ~ mean|delta|*-0.418381  log1p(dist_seq)*+0.023870  intercept -0.103920   (fit on n = 78)
    ARM S mean residual = +0.076032   sd = 0.015488
    mean PREDICTED rho at d=0 = -0.141192   vs   mean OBSERVED rho at d=0 = -0.065159   overshoot = -0.076032
    A222V predicted rho at d=0 = -0.133345 -> BELOW every observed null
    A222V rank = 2/19   rank fraction = 0.1053

  ================ M4  + log1p(d3_CA) ================
    [full]  OLS rho ~ mean|delta|*-0.324445  log1p(d3_CA)*+0.048009  intercept -0.158981   (fit on n = 67 resolved)
    ARM S mean residual = +0.122725   sd = 0.015013
    mean PREDICTED rho at d=0 = -0.187884   vs   mean OBSERVED rho at d=0 = -0.065159   overshoot = -0.122725
    A222V predicted rho at d=0 = -0.181799 -> BELOW every observed null
    A222V rank = 2/19   rank fraction = 0.1053

  (H frame: ARM S mean residual = -0.033105 / -0.007596 / +0.076318 / +0.125434; A222V rank 2/19 under all four)
```

**Recomputed vs target (all 15 agree):**

```
    ARM S mean residual, M1 (full)     recomputed = -0.029845   target = -0.029800   |diff| = 4.872e-05   AGREE
    ARM S mean residual, M2 (full)     recomputed = -0.003938   target = -0.003900   |diff| = 3.784e-05   AGREE
    ARM S mean residual, M3 (full)     recomputed = +0.076032   target = +0.076000   |diff| = 3.174e-05   AGREE
    ARM S mean residual, M4 (full)     recomputed = +0.122725   target = +0.122700   |diff| = 2.534e-05   AGREE
    A222V rank, M1/M2/M3/M4 (full and H)   recomputed = 2   target = 2   AGREE  (8/8)
    M3 mean predicted rho at d=0 (full)    recomputed = -0.141192   target = -0.141200   |diff| = 8.423e-06   AGREE
    M3 mean observed Arm S rho at d=0 (full) recomputed = -0.065159  target = -0.065200   |diff| = 4.067e-05   AGREE
    M3 overshoot, predicted - observed (full) recomputed = -0.076032  target = -0.076000  |diff| = 3.224e-05   AGREE
    -> 15/15 AGREE, 0 DISAGREE
```

**Second part - A222V's raw-rho rank among all resolved backgrounds within 20 A of 222:**

```
A222V's RAW-RHO RANK AMONG ALL RESOLVED BACKGROUNDS WITHIN 20 A OF 222
------------------------------------------------------------------------------
  The set = Arm S (18, all at d3_CA = 0) + the resolved NULLS in (0, 20].  *** RANK FRACTIONS, NOT TESTS. ***

  [full]  n backgrounds in the set = 32 (Arm S 18 + resolved nulls in (0, 20] = 14)
  [full]  at or below A222V: k = 2  ->  A222_C, G_P254F
  [full]  A222V signed rank = 3/32   rank fraction (1 + 2)/(1 + 32) = 0.0909   *** RANK FRACTION, NOT A TEST ***
    the 14 resolved nulls in (0, 20] by d3_CA: G_I192T(5.06), AV_220(6.48), AV_155(8.64), AV_195(10.15), G_L178T(10.31),
    AV_175(10.54), G_Y197V(15.72), G_K48P(15.88), G_P254F(16.28), G_G317Q(17.65), AV_242(17.90), AV_145(17.95),
    G_L318F(18.65), AV_209(18.86)

  [H]  n backgrounds in the set = 32 (Arm S 18 + resolved nulls in (0, 20] = 14)
  [H]  at or below A222V: k = 4  ->  A222_C, AV_195, AV_220, G_P254F
  [H]  A222V signed rank = 5/32   rank fraction (1 + 4)/(1 + 32) = 0.1515   *** RANK FRACTION, NOT A TEST ***

  RECOMPUTED vs TARGET (POST-HOC, from printed 6-dp values):
    n backgrounds within 20 A (full)                       recomputed =           32   target =           32   AGREE
    n at or below A222V within 20 A (full)                 recomputed =            2   target =            2   AGREE
    rank fraction within 20 A (full)                       recomputed =       0.0909   target =       0.0909   |diff| = 0.000e+00   AGREE
    n backgrounds within 20 A (H)                          recomputed =           32   target =           32   AGREE
    n at or below A222V within 20 A (H)                    recomputed =            4   target =            4   AGREE
    rank fraction within 20 A (H)                          recomputed =       0.1515   target =       0.1515   |diff| = 0.000e+00   AGREE
```

Verdict: **PASS.** 18/18 E-gates; 15/15 doc targets agree (all four 4-dp residuals within 5e-5, all three 4-dp M3 quantities within 5e-5, all eight ranks exact, all six within-20 A targets exact to 0.000e+00).

- **A222V is rank 2 of 19 within Arm S under ALL FOUR models and BOTH views - eight cells, no exceptions.** This is now the fifth independent construction to give the same same-site answer (D13 raw, D13 shift-adjusted, D13 all-96, D16a isotonic, D16b isotonic-shift, M1-M4).
- **The parametric models' overshoot at distance 0 is the K3 correction confirmed on Arm S.** The log1p forms predict the 18 same-site backgrounds at -0.1412 (M3) and -0.1879 (M4) when they are actually at -0.0652: overshoot **-0.0760** and **-0.1227**, both larger in magnitude than the entire observed Arm S spread (sd 0.0155 and 0.0150). A222V's own predicted rho (-0.1333 and -0.1818) lies below every observed null rho (`G_P254F`, -0.0962). **The models do not merely rank A222V differently at distance 0 - they predict the entire distance-0 site at values no background in the dataset occupies.**
- **M2 (linear distance) is the exception and it is the one that behaves**: Arm S mean residual -0.0039, essentially zero against an Arm S sd of 0.0152. Its prediction (-0.0612) is close to the observed -0.0652. **The single model with the least extreme parametric form is the only one that does not mispredict the distance-0 site.**
- **Within 20 A of 222, A222V's rank fraction is 0.0909 (full, 2 of 32) and 0.1515 (H, 4 of 32)** - the same ordinal position as its 2/19 within-site rank, now against site plus spatial neighbourhood together.

Files created/modified:
- `scripts/146_phase2_diag3_arms_joint.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D16E_FULL_OUTPUT.txt` (new, 329 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- Nothing protected, no earlier log, no earlier script, not `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **The E-gates did their job immediately, and the failure was mine, not the data's.** On the first run `M2 k (full)` returned 8 against a target of 9 and `M3 k (full)` returned 72 against 69, and the task stopped as pre-registered. Cause: I computed the nulls' residuals from the single all-N fit, whereas scripts 138/139 compute them **leave-one-out** (`loo_variant` / `loo_joint`). `r_A` was identical either way because A222V is out-of-sample in both, which is why only `k` disagreed. Fixed by using `p3.loo_joint`, which is scripts 138/139's construction verbatim; all four models then reproduced to < 4.4e-7 on `r_A` and exactly on `k`. **Recorded because a hard gate that fails for a reason of mine is still a gate that worked.**
2. **The "overshoot" sign convention is worth stating explicitly**: I report `predicted - observed`, so a NEGATIVE overshoot means the model predicts something MORE negative than reality. M1 +0.0298 and M2 +0.0039 (models too generous) versus M3 -0.0760 and M4 -0.1227 (models far too harsh). The doc's "-0.076 overshoot" is the same convention and agrees.
3. **`G_P254F` is at 16.28 A, so it is inside the 20 A set in the second part** and it is the only non-Arm-S member at or below A222V on the full frame. The nearest null, `G_I192T` at 5.06 A, is not. Stated because "within 20 A" and "at or below A222V" pick out almost disjoint sets of members.

## [D17] - Append-only corrections to this session's own D12-D14 statements
Status: PASS
Time started / finished: 2026-09-30 (0.9 s wall - deterministic, no resampling; N_BOOT/N_PERM not read by this script)

What I did:
1. Wrote `scripts/147_phase2_diag3_corrections3.py` with the pre-registered docstring **before its first run**: the four corrections K7-K10, five gate families, and the limits.
2. Ran the gates **first**. All 12 passed, including G5, which recomputes D14's per-bin `mean|delta|` from script 125's own rows and gates it against D14's own saved output to 2e-6 on all 12 bin-view combinations - so the K9 recomputation is a check, not a copy.
3. Located every old sentence with `grep -n` at run time; real line numbers only.
4. Wrote `PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md` from inside the script. **Earlier entries in this log were not edited.**

Actual output (verbatim, from `PHASE2_DIAG3_D17_FULL_OUTPUT.txt`):

```
  [PASS] G1 background_rho_table.csv sha256: e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  [PASS] G1 background_3d_distance.csv sha256: 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de
  [PASS] G2 A222V rho (full): -0.088118064
  [PASS] G2 A222V rho (H): -0.090021683
  [PASS] G3 D12 linear-dist r_A (full): -0.033710698
  [PASS] G3 D12 linear-dist rank (full): rank 10/79
  [PASS] G3 D12 linear-dist r_A (H): -0.035947854
  [PASS] G3 D12 linear-dist rank (H): rank 11/79
  [PASS] G4 D13 same-site count on raw rho (full): k = 1 of 18
  [PASS] G4 D13 same-site count on raw rho (H): k = 1 of 18
  [PASS] G5 recomputed mean|delta| vs D14 saved output (full, {exactly 0}  (Arm S)): recomputed 0.089085 vs saved 0.089085
  [PASS] G5 recomputed mean|delta| vs D14 saved output (H, {exactly 0}  (Arm S)): recomputed 0.089728 vs saved 0.089728
  ... (all 12 bin-view G5 comparisons PASS)

  12/12 D17 gates PASS.  Corrections may be written.
```

**K7 — D12 flag 5 cites `G_P254F`'s rho as A222V's observed rho:**

```
  OLD TEXT (real line 350):
    line 350: >>> 5. **A222V is only barely more extreme than predicted under linear distance** (-0.054407
    predicted vs -0.096244 observed), so the K3 conclusion - that only the linear form leaves A222V more
    extreme than predicted - rests on a fairly small margin. Stated, not smoothed over.

  THE ERROR: -0.096244 is NOT A222V's observed rho.  It is G_P254F's rho, the most negative observed NULL
  rho.  A222V's own observed rho is:
    A222V rho_full = -0.088118064   A222V rho_H = -0.090021683
    G_P254F rho_full = -0.096243863   G_P254F rho_H = -0.101954441

  RECOMPUTED linear-dist model, full frame:
    OLS coefficients: intercept -0.028857  mean|delta| -0.363298  dist +0.000215
    A222V mean|delta| = 0.070330, dist = 0
    A222V PREDICTED rho at its own covariates = -0.054407
    A222V r_A = -0.033711   k = 9 of 78   signed rank = 10/79
    A222V OBSERVED rho = -0.088118   (this is the number flag 5 needed, not -0.096244)
    -> A222V is 0.033711 MORE NEGATIVE than the linear-dist model predicts, and 0.008126 LESS negative
       than G_P254F, the most negative observed null.
```

**K8 — D14 flag 2's inference does not follow:**

```
  OLD TEXT (real line 683):
    line 683: >>> 2. **That cuts against the more extreme reading of "spatial-overlap with no long-range
    content"** and is why I am not going to let D15 be read that way unless its own numbers say so. The bin
    means are what they are: a smooth gradient, no 0 A cliff.

  WHAT D14 ACTUALLY VARIES: D14 bins BACKGROUNDS by d3_CA -- the location of the perturbed BACKGROUND
  relative to residue 222 -- and summarises rho_b in each bin. D14 does NOT vary, restrict, filter or
  otherwise touch the set of TARGET VARIANTS whose delta_b is correlated against own_e_b. Every D14 bin is
  computed on all usable rows.
  WHAT D15 ACTUALLY VARIES: D15 restricts the TARGET VARIANTS by their own 3D distance to 222
  (d3_222(p) > R) and recomputes the same gradient.
  THESE ARE TWO DIFFERENT AXES. D14's absence of a step at the 0 A bin edge is a statement about the
  BACKGROUND-location axis only. It is silent about the TARGET-VARIANT-distance axis, so it cannot cut
  against anything D15 found.
  AND IT DID NOT, IN FACT: D15 found the gradient collapsing to +0.401 (full) and +0.241 (H) at R = 30 A,
  OUTSIDE the matched-deletion range. The two results are compatible, and both are now on the record.
```

**K9 — D14 flag 3's "the near-222 bins are the LOW-shift bins":**

```
  OLD TEXT (real line 670):
    line 670: >>> - **mean|delta| is NOT monotone in the bins and moves in the opposite direction at the
    near end**: Arm S 0.0891, (0,12] 0.0694, (12,20] 0.0961, (20,30] 0.0566, (30,45] 0.0470, (45,inf]
    0.0452. The near-222 bins are the LOW-shift bins and the far bins are also low, with a peak at (12,20].

  RECOMPUTED per-bin mean|delta| (full frame), gated to 2e-6 against D14's saved output:
   rank (highest first)        bin (d3_CA) mean|delta| (full)  mean|delta| (H)
                      1           (12, 20]           0.096069         0.094655
                      2 {exactly 0}  (Arm S)           0.089085         0.089728
                      3            (0, 12]           0.069361         0.073960
                      4           (20, 30]           0.056589         0.060150
                      5           (30, 45]           0.046972         0.048621
                      6          (45, inf)           0.045204         0.046668

  The Arm S bin's mean|delta| is 0.089085, which is the 2nd HIGHEST of the six bins.
  Bins with LOWER mean|delta| than the Arm S bin: ['(0, 12]', '(20, 30]', '(30, 45]', '(45, inf)'] (n = 4 of 6).
  The (0,12] bin (0.069361) IS the lowest bin, so the phrase is true of the 3D-nearest null bin and FALSE of
  the distance-0 Arm S bin it was used to describe.
  The (12,20] bin (0.096069) is the HIGHEST of all six, so the 'peak at (12,20]' part of the old sentence was right.
```

**K10 — D13 flag 4's scale error:**

```
  OLD TEXT (real line 534):
    line 534: >>> 4. **A222V is INSIDE the Arm S raw-rho range, not outside it.** Only one of 18 same-site
    comparators is more extreme. That is a much weaker same-site statement than the frozen 1-of-78 result
    against the null set, and it is reported as the rank fraction it is.

  RECOMPUTED denominators:
    same-site  : A222V rank 2/19  (1 of 18 Arm S at or below)
    frozen    : A222V rank 2/79  (1 of 78 nulls at or below)
  BOTH ARE ORDINAL POSITION 2.  The old sentence's '1-of-78' is also wrong as written: the frozen p_spec
  denominator is 79 (1 + |N|), and the count is 1 of 78.
```

```
  wrote docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md
  sha256 = c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d
```

Verdict: **PASS.** 12/12 gates. Corrections file sha256 `c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d`.

Files created/modified:
- `scripts/147_phase2_diag3_corrections3.py` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md` (new).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_D17_FULL_OUTPUT.txt` (new, 132 lines).
- `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` (this file).
- **Earlier entries in this log NOT edited.** Nothing protected, no earlier script, not `scripts/lib/phase2_diag.py`. Nothing staged, committed or pushed.

Anything unexpected or worth flagging:
1. **K9 is the one substantive factual error D17 caught, and D14's own printed table already contained the disproof** - the sentence contradicted the numbers printed 10 lines above it in the same entry. That is now the third time in this project's history that a log's prose has drifted from its own table (Diagnostics II D0 C2 and C7, then this session's D12 flag 5 and D14 flags 2-3). The pattern is the finding, not the individual slips.
2. **K8 is the most consequential of the four.** My own D14 flag 2 explicitly pre-committed to not letting D15 be read one way "unless its own numbers say so" - and then D15's numbers said the opposite of what flag 2 implied, while flag 2 had been used to argue against that reading on the wrong axis. Correcting it matters because it changes what the session concluded, not just how a sentence reads.

---

# SUMMARY

## 1. READ THIS FIRST - D15, the far-variant mechanism test

**S1 = keep target variants with `d3_222(p) > R`. Both views, all four radii. `p_spec` on all 78 nulls; gradient on the 67 resolved nulls (the D11.2 denominator).**

| view | R (A) | k_R positions removed | A222V rho | position-cluster 95% CI | excl 0 | gradient n=67 | its own bg-level 95% CI | **matched-deletion 95% range (200 draws)** | **flag** | frac draws at/below S1 | p_spec n=78 | at or below |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 0 | 0 | -0.076686 | [-0.110517, +0.052946] | **no** | +0.698474 | [+0.543521, +0.803731] | [+0.698474, +0.698474] (degenerate) | inside (vacuous) | 1.0000 | 0.037975 | AV_220, G_P254F |
| full | 10 | 23 | -0.079237 | [-0.108943, +0.053475] | **no** | +0.689454 | [+0.530630, +0.794968] | [+0.680407, +0.706900] | **INSIDE** | 0.2800 | 0.037975 | AV_220, G_P254F |
| full | 20 | 121 | -0.065948 | [-0.106446, +0.077385] | **no** | +0.662097 | [+0.518283, +0.763801] | [+0.663147, +0.723051] | **OUTSIDE (below)** | 0.0150 | 0.037975 | AV_220, G_P254F |
| full | 30 | 247 | **-0.027360** | [-0.126369, +0.088052] | **no** | **+0.400678** | [+0.189417, +0.569595] | [+0.615026, +0.731210] | **OUTSIDE (far below)** | 0.0000 | 0.063291 | AV_145, AV_220, G_L318F, G_P254F |
| H | 0 | 0 | -0.080432 | [-0.136966, +0.050697] | **no** | +0.688317 | [+0.530040, +0.793972] | [+0.688317, +0.688317] (degenerate) | inside (vacuous) | 1.0000 | 0.037975 | AV_220, G_P254F |
| H | 10 | 13 | -0.082102 | [-0.133307, +0.060709] | **no** | +0.686581 | [+0.526713, +0.797779] | [+0.675494, +0.702836] | **INSIDE** | 0.3750 | 0.037975 | AV_220, G_P254F |
| H | 20 | 86 | -0.063597 | [-0.131090, +0.087967] | **no** | +0.640347 | [+0.484996, +0.749546] | [+0.642047, +0.720172] | **OUTSIDE (below)** | 0.0250 | 0.050633 | AV_220, G_L318F, G_P254F |
| H | 30 | 172 | **-0.024367** | [-0.145818, +0.109530] | **no** | **+0.241345** | [-0.006500, +0.461143] | [+0.602547, +0.726413] | **OUTSIDE (far below)** | 0.0000 | 0.101266 | AV_145, AV_220, AV_328, AV_650, G_G317Q, G_L318F, G_P254F |

Sequence sensitivities (S1 only, reported, none selected): Rs = 25 leaves the gradient at **+0.695361** (full) / **+0.689215** (H); Rs = 50 leaves it at **+0.680934** / **+0.650045**. Both with CIs excluding zero. **Removing |p-222| <= 50 in sequence (495 positions retained) is far less destructive than removing 30 A in space (247 positions).**

**DOES THE GRADIENT PERSIST AMONG DISTAL VARIANTS? YES at R = 10, NO at R = 20 and R = 30.**
**IS THE FALL ATTRIBUTABLE TO THE REMOVED POSITIONS? YES at R = 20 and R = 30, NO at R = 10.** The matched-deletion control is what makes that statement possible: at R = 20 and R = 30 the S1 gradient sits **outside** the range produced by deleting the *same number of random whole positions*, on both views, with 97.5-100% of random deletions giving a *higher* gradient. At R = 10 it sits **inside**, with 62.5-72% of random deletions giving a *higher* gradient than the real deletion.

**DOES THE ANCHOR PERSIST? Only weakly.** A222V's rho falls monotonically -0.0767 -> -0.0792 -> -0.0659 -> **-0.0274** (full) and -0.0804 -> -0.0821 -> -0.0636 -> **-0.0244** (H); `p_spec` holds at 2/78 = 0.037975 through R = 20 and rises to 0.063291 (full) and 0.101266 (H) at R = 30. **A222V's own negative association is roughly halved by removing target variants within 30 A of 222.**

**THE HONEST CAVEAT, stated as prominently as the result: A222V's position-cluster CI INCLUDES ZERO IN ALL TWELVE VARIANTS ON BOTH VIEWS** - R = 0, 10, 20, 30 and both sequence sensitivities, both frames - and in the unrestricted baseline too. This task does not establish A222V's own rho; it shows that whatever signal exists is concentrated near 222 and is not carried by distal variants.

## 2. D16 and D16e

**D16 (isotonic; PRIMARY = D16b on `d3_CA`; no bootstrap, no permutation):**

| variant | view | n nulls | g(0) | r_A | k | p_spec_adj | rank | vs frozen threshold |
|---|---|---|---|---|---|---|---|---|
| D16a raw rho ~ g(d3_CA) | full | 67 | -0.068487 | -0.019631 | 12 | **0.191176** | 13/68 | above 0.05 |
| **D16b r^shift ~ g(d3_CA) [PRIMARY]** | full | 67 | **-0.047207** | **-0.019217** | 20 | **0.308824** | 21/68 | **above 0.05** |
| D16c-a raw rho ~ g(dist_seq) | full | 78 | -0.084598 | -0.003520 | 37 | 0.481013 | 38/79 | above 0.05 |
| D16c-b r^shift ~ g(dist_seq) | full | 78 | -0.080278 | +0.013854 | 53 | 0.683544 | 54/79 | above 0.05 |
| D16a raw rho ~ g(d3_CA) | H | 67 | -0.076599 | -0.013423 | 22 | 0.338235 | 23/68 | above 0.10 |
| **D16b r^shift ~ g(d3_CA) [PRIMARY]** | H | 67 | **-0.051076** | **-0.017616** | 19 | **0.294118** | 20/68 | **above 0.10** |
| D16c-a raw rho ~ g(dist_seq) | H | 78 | -0.094480 | +0.004459 | 43 | 0.556962 | 44/79 | above 0.10 |
| D16c-b r^shift ~ g(dist_seq) | H | 78 | -0.089189 | +0.020497 | 58 | 0.746835 | 59/79 | above 0.10 |

**D16d same-site rank fraction: 0.1053 (k = 1, `A222_C`) under BOTH D16a and D16b, BOTH views** - *** rank fraction, n = 19, NOT a test ***. `g(0)` is set by the **6 nulls within 12 A** (5 within 10.5 A) for the 3D variants and **2** for the sequence variants; D16a pools 67 nulls into 14 blocks. All eight isotonic cells are **above** the frozen numeric thresholds; the spread is 0.191-0.747.

**D16e (Arm S under the four exact joint models):**

| model | Arm S mean residual (full) | mean predicted rho at d=0 | mean observed rho at d=0 | overshoot | A222V rank in Arm S u {A222V} |
|---|---|---|---|---|---|
| M1 shift-only | **-0.029845** (sd 0.017533) | -0.035315 | -0.065159 | +0.029845 | **2/19** |
| M2 + linear dist_seq | **-0.003938** (sd 0.015200) | -0.061221 | -0.065159 | +0.003938 | **2/19** |
| M3 + log1p(dist_seq) | **+0.076032** (sd 0.015488) | **-0.141192** | -0.065159 | **-0.076032** | **2/19** |
| M4 + log1p(d3_CA) | **+0.122725** (sd 0.015013) | **-0.187884** | -0.065159 | **-0.122725** | **2/19** |

All four Arm S mean residuals and all three M3 quantities match the doc's targets to < 5e-5. **A222V is rank 2/19 under all four models and both views - eight cells, no exception** (*** rank fraction, not a test ***). The log1p forms predict the whole distance-0 site 0.076-0.123 too negative, several times the site's own sd, and predict A222V **below every observed null rho** (`G_P254F`, -0.096244). Only M2, the least extreme form, comes close to the observed site mean (-0.0612 vs -0.0652).

**Within 20 A of 222 (Arm S + the 14 resolved nulls in (0, 20], n = 32): A222V's raw-rho rank fraction is 0.0909 (full, k = 2: `A222_C`, `G_P254F`) and 0.1515 (H, k = 4: `A222_C`, `AV_195`, `AV_220`, `G_P254F`).** All six targets exact to 0.000e+00.

## 3. D13 and D14, one line each

**D13:** A222V is rank **2/19 within Arm S** - one member (`A222_C`) of 18 is at or below it - and that is unchanged under raw rho, D9's exchangeable shift residual, D4's all-96 residual, D16a, D16b and all four joint models, on both views: **six independent constructions, one answer.** *** Rank fractions, n = 19, not tests. *** It cannot separate "the residue" from "the region".

**D14:** no discontinuity at the 0 A bin edge (Arm S mean -0.0652 vs the (0,12] null mean -0.0649, difference **-0.000227**, bg-level CI [-0.017265, +0.015162]; H **+0.003588**, CI [-0.016695, +0.020572]), monotone bin means from -0.0652 to +0.0245, D14.2's POST-HOC targets reproduced to < 5e-5, and **figure SKIPPED - matplotlib not importable and deliberately not installed.**

## 4. D12 (K1-K6) and D17 (K7-K10)

**Corrections file `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` sha256 = `8089890ab84b0da931e3b2ef43a39c8be36babc7d9dd1281a36306c2d37fd176`** (unchanged since D12).
**Corrections file `PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md` sha256 = `c32d0edb2b5f4b416eedccd52ff639da66b5ef346e8749dfeaa0ded125931f2d`.**

Line numbers are REAL, from `grep -n` at run time. "Old text" line numbers refer to `PHASE2_DIAGNOSTICS_II_LOG.md` for K1-K6 and to **this log** for K7-K10.

| # | old text (real line numbers) | recomputed vs target | corrected statement |
|---|---|---|---|
| K1 | "PARTIAL Spearman(rho, dist \| mean\|delta\|) = -0.146323470" (II log 550, 558) and the reverse label (552, 560) | **AGREE** both ways. Formula and rank-residualisation agree to 2.2e-16. True `rho~dist\|shift` = **+0.629667** / +0.603747; true `rho~shift\|dist` = **-0.146323** / -0.161718. CIs [+0.472642,+0.742385] and [-0.404796,+0.107532] (full) | Script 138 lines 404/408 print the two PARTIAL labels transposed; the VALUES are right. **Once shift is held fixed, SHIFT carries the association (-0.146, CI includes zero); once distance is held fixed, DISTANCE does (+0.630, CI excludes zero).** The "sign flip" and "reverse of D4's reading" do not exist - the shift partial keeps the raw sign. D11.4's partials were labelled correctly (+0.651428 / -0.108073 full). |
| K2 | "D10b -- NEIGHBOURHOOD RESTRICTED RANKS on D9's PRIMARY residuals" (II log 529); counts at 532-535; "worse than D0's raw-rho version" (583) | Old counts 8/9/18/19 and all four name lists **reproduce EXACTLY** on the **D10a joint log1p(dist)** residuals. On **D9's primary** residuals: **1/1/1/1, `AV_220` only**, rank fractions 0.1818 / 0.0952 | `resid_primary` is bound at script 138:322-323 under `name.startswith("PRIMARY")`, which matches `VARIANTS[0] = "PRIMARY log1p(dist)"` - **the joint model, not D9's shift-only model**. D10b ran on the wrong vector while its banner and prose called it D9's. **The "worse than raw rho" claim is withdrawn.** |
| K3 | "so this is not an extrapolation artifact" (II log 856) | Predicted rho at A222V's covariates vs most negative **observed null** (`G_P254F`, -0.096244): shift-only -0.021693, +linear dist -0.054407, **+log1p(dist) -0.133345**, clamped -0.107121, **+log1p(d3_CA) -0.181799**. 4 of 5 targets differ from the printed 4-dp target by >2e-6 (max 4.50e-05) while **matching it to every digit it prints (5/5)** | The log-form predictions lie **below every observed null**, so those results extrapolate a fitted surface whatever the hat value is. **A hat value inside the null range does not make a point interpolated.** Only the linear form leaves A222V more extreme than predicted. **Target-precision disagreement reported, not forced** - no tolerance was loosened. |
| K4 | "adding distance destroys the adjusted advantage" (II log 572, 847) | linear dist **10/79, 0.126582** (full), **11/79, 0.139241** (H); log1p(dist) **70/79, 0.886076** (full), **71/79, 0.898734** (H). All AGREE; ratio **7.000x** | All four are **above** the frozen thresholds; the magnitudes differ seven-fold. **No version is a calibrated tail probability**; the direction is the robust part, the size is a property of the chosen form. |
| K5 | "the distance association survives (-0.146 -> CI includes zero only after shift is partialled the *other* way; the partial with shift held fixed is +0.651)" (II log 927) | Garbled: it uses -0.146 as the shift-held-fixed value and +0.651 as the distance-held-fixed one, in the wrong order | Corrected: with shift held fixed the 3D association is **+0.651** (CI excludes zero); with 3D held fixed the shift association is **-0.108** (CI includes zero); same reversal on sequence distance (**+0.630** vs **-0.146**). **Distance, not shift, carries the association once the other is held fixed.** |
| K6 | "D10c's answer and D10a's answer point opposite ways" (II log 597); D10c verdict (585); "sign flip" (596, 872) | All four lines rest on the transposed labels | **VOID:** "this is the reverse of D4's reading"; flag 2's entire "sign flip" explanation; **flag 3 - D10c and D10a actually AGREE after K1** (both say the distance axis carries the association). The D10c *verdict* survives; its supporting arithmetic in the log does not. |
| K7 | "A222V is only barely more extreme than predicted under linear distance (-0.054407 predicted vs -0.096244 observed)" (**this log line 350**) | -0.096244 is **`G_P254F`'s rho, not A222V's**. A222V's own rho = **-0.088118064**; linear-dist `r_A` = **-0.033711**, rank **10/79**; D16e M2 gives rank **2/19** | The margin is against A222V's **own** observation: it is **0.033711 more negative** than the linear model predicts, and 0.008126 short of `G_P254F`. Not "barely". Within its own site under the same model: rank **2/19** - ***rank fraction, not a test***. |
| K8 | "That cuts against the more extreme reading of 'spatial-overlap with no long-range content'" (**this log line 683**) | D14 bins **backgrounds** and never touches the **target-variant** set; D15 varies the **target-variant** axis. Different axes. | **D14's null result on the background-location axis is silent about the target-variant axis and cannot cut against a long-range claim. It did not: D15 found the gradient collapsing at R = 20-30 A, outside the matched-deletion range.** Both results stand. The old sentence imported a conclusion about one axis into a claim about the other. |
| K9 | "The near-222 bins are the LOW-shift bins" (**this log line 670**) | Recomputed per-bin `mean|delta|` (gated to 2e-6 vs D14's saved output, 12/12): (12,20] **0.096069**, **Arm S 0.089085**, (0,12] 0.069361, (20,30] 0.056589, (30,45] 0.046972, (45,inf) 0.045204 | The **Arm S bin is the 2nd HIGHEST of six**, not a low one; only 4 of 6 bins sit below it. The **(0,12]** bin is the lowest, so the phrase is true of the 3D-nearest null bin and **false of the distance-0 Arm S bin it was used to describe**. The "(12,20] peak" part was right. |
| K10 | "That is a much weaker same-site statement than the frozen 1-of-78 result" (**this log line 534**) | same-site **2/19**; frozen **2/79** (1 of 78 nulls; the frozen denominator is 79, not 78) | **Both are ordinal position 2.** The two comparisons answer different questions at different n - 18 same-site substitutions versus 78 backgrounds elsewhere - and neither is "much weaker" as an ordinal claim. What separates them is the **reference set**, not the rank. |

## 5. Plain two-sided statement of which claim the data now support

**"Cannot be separated" - and that is now a measured conclusion rather than an open question, because the two candidate explanations were tested on different axes and only one of them survived its test.**

Stated in the direction the evidence points:

- **Against "tied to position 222 specifically" / for "the region around 222":** the gradient of rho_b against 3D distance is real and large (+0.732 unrestricted), and **removing target variants within 20-30 A of 222 collapses it to +0.400 (full) and +0.241 (H) - outside the matched-deletion range, on both views.** Every distance-aware adjustment puts A222V's `p_spec_adj` **above** the frozen thresholds: isotonic 0.19-0.75, parametric 0.13-1.00. The log1p distance forms **mispredict the entire distance-0 site** (Arm S predicted -0.141 and -0.188 against an observed -0.065, overshoots of 0.076 and 0.123, several times the site's own sd of 0.015) and predict A222V **below every observed null**. A222V's own association is roughly halved by deleting near-222 target variants.
- **For "tied to position 222 specifically":** A222V's own rho sits **below the entire Arm S mean** (-0.088 against -0.065, a gap of 0.023 against a site sd of 0.014) and it is the 2nd most negative of 19 same-site backgrounds in **six independent constructions and eight model-view cells, without a single exception** - raw, shift-adjusted exchangeable, all-96 in-sample, isotonic, isotonic two-stage, and all four exact joint models. **There is no 0 A discontinuity** in the model-free picture: the 18 Arm S backgrounds at exactly 0 A sit at the same mean rho as the six 3D-nearest nulls 5-10.5 A away (difference -0.000227, CI includes zero). Restricting to *distal* target variants at R = 10 A changes the gradient by 0.009 and changes nothing that can be attributed to the removed positions.

**The honest reading, and the one I will not soften:** **the two effects are separable, and they are separable because they live on different axes.** What is tied to **position 222** is A222V's *excess over its own site* - a substitution-specificity statement that is unusually robust to every adjustment tried here. What is tied to **the region around 222, in space** is the *gradient itself*, and that gradient is carried by target variants within about 30 A of 222 rather than by distal ones. The statistic is **not** a pure spatial-overlap effect with no long-range content: at R = 30 A a gradient of +0.40 remains, and D15's H-frame CI there even includes zero. It is **not** purely position-specific either: the neighbourhood of 222 behaves systematically like A222V in both sequence and space.

**What is NOT established:** A222V's own rho under restriction. Its position-cluster CI includes zero in **all twelve** restricted variants on both views. And `p_spec_adj` in every family here is a rank count on leave-one-out residuals of overlapping fits - not a calibrated tail probability and not a decision rule.

## 6. Every gate, PASS/FAIL, value - D12-G1 first

| gate | what it checked | result | value |
|---|---|---|---|
| **D12-G1.1** | D1 table sha256 | **PASS** | `e397a442…3796` |
| **D12-G1.2** | 3D table sha256 | **PASS** | `69914df9…12de` |
| **D12-G1** (24 numeric rows) | every row of the D12-G1 table before any correction | **PASS 26/26** | A222V rho 2.489e-10 / 3.340e-11; `p_spec` 0.000e+00 both beater sets exact; D9 primary 3.674e-07 / 6.262e-08, k = 2/2, beaters exact; D10a joint 7.356e-08 / 1.071e-07, k = 69/70; D11.2 d3_CA 1.899e-10 / 3.985e-10, dist_seq 4.604e-11 / 1.349e-07; D11.4 3.397e-07 / 4.397e-07, k = 67/67 |
| **D15-G1a** | loader vs stored `ca_dist_222`, 9,595 rows | **PASS** | max\|diff\| = **7.105e-15 A** (gate < 1e-9); 0 unresolved in that frame |
| **D15-G1b** | monomer far (>10 A) | **PASS** | **9,232/9,595 = 96.2168%** |
| **D15-G1b** | dimer-aware far (>10 A) | **PASS** | **9,128/9,595 = 95.1329%** |
| **D15-G1c** | all 96 rho_full and rho_H vs the D1 table | **PASS** | 192 comparisons, max\|diff\| = **4.990e-10** (gate < 1e-9) |
| **D15-G1c** | A222V rho, full and H | **PASS** | max\|diff\| = **0.000e+00**; -0.088118064 / -0.090021683 |
| **D15-G1d** | unrestricted gradient, resolved N = 67 | **PASS** | full 1.899e-10, H 3.985e-10 vs +0.731577372 / +0.713319366 |
| **D15-G2a** | deleting ZERO positions reproduces the R = 0 baseline | **PASS x2** | max\|diff\| = **0.000e+00, required exactly 0** |
| **D15-G2b** | actual S1 removed set reproduces S1 | **PASS x8** | 0/23/121/247 positions (full) and 0/13/86/172 (H); max\|diff\| over all 97 rho and every statistic = **0.000e+00** |
| D15 identity | every retained cluster once vs the point estimate | **PASS** | max\|diff\| = **0.000e+00** (gate < 1e-12), every variant and view |
| **D16e E1** | M1 = D9 primary | **PASS x4** | r_A 3.674e-07 / 6.262e-08; k = 2/2 |
| **D16e E4** | M2 = D10a SENS(i) | **PASS x4** | r_A 3.025e-07 / 1.459e-07; k = 9/10 |
| **D16e E2** | M3 = D10a PRIMARY | **PASS x4** | r_A 7.356e-08 / 1.071e-07; k = 69/70 |
| **D16e E3** | M4 = D11.4 | **PASS x4** | r_A 3.397e-07 / 4.397e-07; k = 67/67 |
| **D16e E5** | both input sha256s | **PASS x2** | `e397a442…`, `69914df9…` |
| **D17 G1-G5** | sha256s, A222V rho, linear-dist r_A/rank, D13 counts, per-bin `mean|delta|` vs D14's saved output | **PASS 12/12** | 2e-6 on all 12 bin-view comparisons |
| D13 / D14 / D16 / D16e targets | recomputed vs the doc's targets | **PASS** | D13 8/8 (max 4.412e-07); D14 4/4 (max 4.872e-05); D16 2/2; D16e **15/15** (max 4.872e-05; the six within-20 A targets exact to 0.000e+00) |
| **D12 K3 targets** | 4-dp targets vs a 2e-6 tolerance | **DISAGREEMENT REPORTED, NOT FORCED** | 1/5 at 2e-6; **5/5 match to every digit the target prints**; raw diffs 5.96e-07 to 4.50e-05. **No tolerance loosened.** |
| D16e E-gates, first run | k under the wrong residual construction | **FAIL 2/18 -> STOPPED** | M2 k 8 vs 9, M3 k 72 vs 69; cause was in-sample null residuals where scripts 138/139 use leave-one-out. Fixed at source, all 18 then PASS. |
| D15-G1..G2 first run of script 143 | crashed in `pos_cluster_boot` | **superseded** | `IndexError: index 10075 out of bounds for size 9740`; script **144** is 143 with that one line fixed. Disclosed, 143 left on disk unread-modified. |

**No gate was loosened to obtain a result. No task was re-run at a higher N to chase a result. Task status: D12 PASS, D13 PASS, D14 PASS (figure SKIPPED), D15 PASS, D16 PASS, D16e PASS, D17 PASS.**

## 7. Protected paths, earlier logs, git state, torch/esm - confirmed

- **Nothing protected was edited.** `AGENTS.md` (Sep 22 23:18), `RESULTS.md` (Sep 26 19:37), `PHASE2_PREREG.md` (Sep 27 23:01), `GB1_REGIME_PREREG.md` (Sep 28 16:31), `MTHFR_RESULTS_LOG.md` (Sep 21 20:17), `PROJECT_SUMMARY_FINAL.md` (Sep 26 15:21) - all unchanged.
- **No earlier log was touched.** `PHASE2_DIAGNOSTICS_II_LOG.md` mtime Sep 29 22:45; `PHASE2_DIAGNOSTICS_LOG.md` sha256 `8209875d714b0e2b2428b6eee26500f0218b777a14a2af31b84d735ae57cd6fc`, the value Diagnostics II itself recorded; `PHASE2_LOG.md` Sep 29 19:13.
- **No earlier entry in THIS log was edited.** D12, D13 and D14 were verified present and untouched at the start of this continuation; D17 corrects them by appending, with the old text quoted at its real line number. `grep -n` confirms the four corrected sentences are still physically present at lines 350, 534, 670 and 683.
- **No earlier script was edited**, and **not `scripts/lib/phase2_diag.py`** (Sep 29 20:09, unchanged). Scripts 136-139 untouched. Script 143 read only, disclosed, left on disk.
- **No torch, no esm, no thermompnn, no Biopython was imported anywhere.** Verified two ways: `grep` finds no matching import statement in scripts 144-147 or `scripts/lib/phase2_diag3.py` (the only hits are the words inside docstrings and printed limitations, which is where the prohibition is restated), and a runtime check importing both library modules reports `torch in sys.modules: False`, `esm: False`, `thermompnn: False`.
- **Nothing was staged, committed or pushed by me.** `git status --porcelain` shows only the three pre-existing unstaged modifications (`.gitignore`, `README.md`, `requirements.txt`) plus untracked files. **Disclosure:** HEAD is `accb0ee` "Add Phase 2 diagnostics III: corrections, same-site comparison, far-variant mechanism test", authored by `jaypunxchavan` at **00:12:32 on Sep 30** - the moment this session began. `git show --stat` confirms it contains **exactly one file, the 371-line planning document `PHASE2_DIAGNOSTICS_III.md`, and none of my scripts, logs or outputs**. **That commit is not mine; I did not create it, stage it, or author its message.** All work of this session is untracked.
- **No packages installed.** `venv/bin/python3` throughout. All runs in the foreground. `matplotlib` was found absent and deliberately **not** installed, per the doc's rule 9.

**Files this session created (all untracked):** `scripts/lib/phase2_diag3.py`, `scripts/140_phase2_diag3_corrections.py`, `scripts/141_phase2_diag3_samesite.py`, `scripts/142_phase2_diag3_bins.py`, `scripts/143_phase2_diag3_farvariants.py` (superseded, disclosed), `scripts/144_phase2_diag3_farvariants.py`, `scripts/145_phase2_diag3_isotonic.py`, `scripts/146_phase2_diag3_arms_joint.py`, `scripts/147_phase2_diag3_corrections3.py`, and in `docs/tasks/phase2-diagnostics-iii-mechanism/`: this log, `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md`, `PHASE2_DIAGNOSTICS_II_CORRECTIONS_III.md`, and six `PHASE2_DIAG3_*_FULL_OUTPUT.txt` files.

## 8. The single most important thing to read first

**`docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` line 829** - the D15 verdict bullet:

> **The gradient does NOT survive R = 20 A or R = 30 A.** At R = 20 full, the gradient falls to 0.6621 against a matched-deletion range of [+0.663147, +0.723051] - **OUTSIDE** (below), with 98.5% of random 121-position deletions giving a *higher* gradient. At R = 30 full it collapses to 0.4007 against [+0.615026, +0.731210] - far **OUTSIDE**, 100% of draws higher.

Read it with **line 828** (R = 10 is INSIDE the matched-deletion range, so nothing at R = 10 is attributable to the removed positions), with the CI caveat printed in the D15 verdict (A222V's position-cluster CI includes zero in **all twelve** restricted variants on both views), and with **section 5 above**, which is the only place the two axes are put together. **That single OUTSIDE flag, on both views at two radii, is the session's main result: it is the first measurement in this project that separates "tied to the residue" from "tied to the spatial neighbourhood of the residue", and it resolves that separation against the long-range reading.**
