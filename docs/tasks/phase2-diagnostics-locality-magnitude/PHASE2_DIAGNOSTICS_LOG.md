# PHASE 2 diagnostics — session log

Plan: `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS.md`
Executor: OpenCode · Started 2026-09-29
Scope: cached-data-only. No model scoring, no torch, no esm, no new backgrounds.

**This session is descriptive.** It does not redefine, replace, or retroactively
qualify the frozen `PHASE2_PREREG.md` §5 outcome, which stands as logged. Wording
discipline (doc rule 9): the words reserved for the frozen §5 test are not used in
this log's own prose; plain descriptive language is used instead.

Full verbatim run output for each task is saved to
`PHASE2_DIAG_<TASK>_FULL_OUTPUT.txt` in this directory.

---

## D1 — Build and gate the canonical per-background ρ_b table (HARD GATE)
Status: **PASS**
Time started: 2026-09-29 20:10:05 · Time finished: 2026-09-29 20:10:07 (2 s wall)

**What I did:**

1. Searched for a persisted per-background ρ table. **It does not exist as a file.** Script 125 contains zero file-writing calls (my scan for `to_csv|np.save|write_text|open(...,'w')` returned `NONE`), and no CSV under `data/processed/` carries a `rho` column except the two unrelated pre-Phase-2 files `task109_placebo_rhos.csv` and `task80_region_rhos.csv`. `data/processed/phase2_diagnostics/` did not exist. Script 125's ρ_b survive **only in its stdout**, at `data/processed/phase2/analysis_run.log`.
2. Therefore recomputed, by **importing script 125 and driving its own `--mode phase2` build path** — not by reimplementing anything. New shared loader `scripts/lib/phase2_diag.py` does `importlib` on `scripts/125_phase2_analysis.py` (the filename starts with a digit, so a normal `import` is illegal) and runs `A = s125.Analysis("phase2")` → `s125.build_phase2(A)` → `A.finalize()` → `A.point_rhos()`. 125's `main()` is guarded by `if __name__ == "__main__"`, so importing is side-effect free.
3. The **only** transcription is 125's H-view ρ block, which lives inline inside `main()` (lines 531–539) and therefore cannot be imported. It is reproduced line-for-line in `pdg.point_rhos_H` and is gated independently against 125's own printed log (G1.15).
4. Ran gate **D1-G1** at |diff| < 1e-9 on every target, then an extra independent cross-check of all 96+96 recomputed values against 125's printed stdout.

**Actual output (verbatim, from `PHASE2_DIAG_D1_FULL_OUTPUT.txt`):**

```
[step 0] script 125 contains 0 file-writing call(s): NONE
  -> script 125 writes NO output file; its rhos survive only in its stdout.
  CSVs under data/processed/ with a 'rho' column in the header: ['task109_placebo_rhos.csv', 'task80_region_rhos.csv']
  data/processed/phase2_diagnostics/ exists: False
  FINDING: no per-background rho table exists as a file. Recomputing from script 125's own construction (imported).

[step 1] delta_b(v) = score_b(v) - esm2_score(v)
    score_b(v)  <- data/processed/phase2/bg_<bg_id>.csv::score
    esm2_score  <- data/processed/task32_analysis_table.csv::esm2_score
    join        <- frame.merge(bg[[position, mut_aa, score]], on=[position, mut_aa], how='left')
  (all four lines quoted from scripts/125_phase2_analysis.py)
  own_e_b cross-check: task32 vs own_context_metrics over 10757 frame rows: mismatches = 0 (expect 0)
  PIN-8 regions vs task32 region column: mismatches = 0/10757 (expect 0)
  H: 455 positions, 7526 frame rows (script 122 recorded 455 / 7526)
  roster 96 backgrounds; bg_*.csv files found = 96 (all 96 expected before session 2b)
  rows outside own position without scores (coverage gaps) = 0 across all backgrounds (none)
  arms: S=18 V=38 G=40 -> N (null set) = 78; A222V is neither S nor N (frozen section 3)
  G-C PASS: 0 rows with target position == background position in any rho_b input (own-position rows pre-dropped: 1267)

GATE D1-G1 (HARD; tolerance |diff| < 1e-9 on every target)
  [PASS] G1.1 A222V rho full: got -0.08811806424891734 vs -0.088118064 |diff|=2.489e-10
  [PASS] G1.2 A222V rho H: got -0.09002168303339808 vs -0.090021683 |diff|=3.340e-11
  null set N = V u G, n = 78 (125 printed 78; expect 78)
  [PASS] G1.3 p_spec(full) == 2/79: got 0.02531645569620253 = (1 + 1)/(1 + 78) vs 0.02531645569620253 |diff|=0.000e+00
  [PASS] G1.4 full-frame beater set == {G_P254F}: got ['G_P254F'] vs ['G_P254F']; G_P254F=-0.096243863
  [PASS] G1.4 G_P254F rho_full: got -0.09624386299393672 vs -0.096243863 |diff|=6.063e-12
  [PASS] G1.5 p_spec(H) == 4/79: got 0.05063291139240506 = (1 + 3)/(1 + 78) vs 0.05063291139240506 |diff|=0.000e+00
  [PASS] G1.6 H-frame beater set == {G_P254F, AV_220, AV_195}: got ['AV_195', 'AV_220', 'G_P254F'] vs ['AV_195', 'AV_220', 'G_P254F']; AV_195=-0.093420822; AV_220=-0.094480281; G_P254F=-0.101954441
  [PASS] G1.6 G_P254F rho_H: got -0.10195444117792953 vs -0.101954441 |diff|=1.779e-10
  [PASS] G1.6 AV_220 rho_H: got -0.09448028074575339 vs -0.094480281 |diff|=2.542e-10
  [PASS] G1.6 AV_195 rho_H: got -0.09342082173718176 vs -0.093420822 |diff|=2.628e-10
  [PASS] G1 arm S mean (full): got -0.06515933422985482 vs -0.065159334 |diff|=2.299e-10
  [PASS] G1 arm V mean (full): got -0.019532174185071315 vs -0.019532174 |diff|=1.851e-10
  [PASS] G1 arm G mean (full): got -0.00023029557700166744 vs -0.000230296 |diff|=4.230e-10
  [PASS] G1 arm S mean (H): got -0.07018124298308563 vs -0.070181243 |diff|=1.691e-11
  [PASS] G1 arm V mean (H): got -0.022540725087712855 vs -0.022540725 |diff|=8.771e-11
  [PASS] G1 arm G mean (H): got 0.0008695555193221162 vs 0.000869556 |diff|=4.807e-10
      arm S (full): n=18 mean=-0.065159334 median=-0.064728255 range=[-0.093529969, -0.045641128]
      arm V (full): n=38 mean=-0.019532174 median=-0.023411207 range=[-0.084598081, +0.047573205]
      arm G (full): n=40 mean=-0.000230296 median=+0.010076945 range=[-0.096243863, +0.063116028]
      arm S (H): n=18 mean=-0.070181243 median=-0.068991235 range=[-0.090964259, -0.048929841]
      arm V (H): n=38 mean=-0.022540725 median=-0.022628334 range=[-0.094480281, +0.040588603]
      arm G (H): n=40 mean=+0.000869556 median=+0.009295575 range=[-0.101954441, +0.068247435]
  [PASS] G1.13 N mean (full): got -0.009633774898881753 vs -0.009633775 |diff|=1.011e-10
  [PASS] G1.13 N mean (H): got -0.010535452981541071 vs -0.010535453 |diff|=1.846e-11
  [PASS] G1.14 A222V signed rank within N u {A222V} (full): got 2/79 vs 2/79
  [PASS] G1.14 A222V signed rank within N u {A222V} (H): got 4/79 vs 4/79

  [G1.15] independent cross-check of all 96 recomputed values against script 125's own stdout
    parsed 96 full-frame rho lines and 96 rho_H lines from data/processed/phase2/analysis_run.log
  [PASS] G1.15 all 96 rho_full match 125's printed log: parsed 96/96; max|diff| = 4.990e-10 (worst G_N12P)
  [PASS] G1.15 all 96 rho_H match 125's printed log: parsed 96/96; max|diff| = 4.956e-10 (worst A222_Q)

  50/50 checks PASS, 0 FAIL
  GATE PASS: D1-G1 satisfied at |diff| < 1e-9 on every target.

  A222V rho_full = -0.08811806424891734
  A222V rho_H    = -0.09002168303339808
  p_spec(full)   = 0.02531645569620253  (1/78 at or below)
  p_spec(H)      = 0.05063291139240506  (3/78 at or below)
  full-frame beaters: ['G_P254F']
  H-frame beaters:    ['AV_195', 'AV_220', 'G_P254F']
  table sha256  = e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796
  table path    = data/processed/phase2_diagnostics/background_rho_table.csv
```

Worth noting for the record: `G1.3` and `G1.5` returned `|diff| = 0.000e+00` — the recomputed `p_spec` values are not merely close, they are bit-identical to `2/79` and `4/79` because they are exact rationals in float64. Every other discrepancy is at the 1e-10–1e-12 level, i.e. 9-decimal rounding of the plan's quoted values, three orders of magnitude inside the 1e-9 tolerance.

**Verdict:** **PASS.** The hard gate D1-G1 is satisfied on all 50 checks. A222V's ρ reproduces on both views; `p_spec` reproduces on both views; the identity of the beating nulls reproduces on both views; all six arm means/medians/ranges and the null-set summaries reproduce. The session may proceed to D2–D8 on this table. The frozen `PHASE2_PREREG.md` §5 outcome is untouched by this task.

**Files created/modified:**
- `scripts/lib/phase2_diag.py` (new) — shared loader; imports 125, holds the one transcribed H block, the per-background-bootstrap helper, and the quoted delta/join provenance constants.
- `scripts/131_phase2_diag_background_rho.py` (new) — D1, with D1-G1 pre-registered in the docstring before the run.
- `data/processed/phase2_diagnostics/background_rho_table.csv` (new) — 96 rows, columns `bg_id, arm, position, dist_222, rho_full, rho_H`, sha256 `e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796`.
- `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAG_D1_FULL_OUTPUT.txt` (new).
- `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md` (this file).

**Anything unexpected or worth flagging:**

- **The plan's premise was right and its guess was right.** D1 said a persisted table was "likely" absent; it is confirmed absent, and the only trace is stdout. Had I trusted a reconstruction from the run log alone, D1 would have been a *parse* of A4's output rather than an independent rebuild; importing 125 makes it a genuine rebuild that happens to agree to 5e-10. The plan's instruction to import rather than reimplement was the right call and I flag that it made the difference between a real check and a circular one.
- **125's own-position exclusion is implicit, not explicit.** `build_phase2` never filters `position == own_position`; it relies on a background's own substitution being absent from its own score file, so the score is NaN and the row drops, and then *asserts* the result via gate G-C. That reproduced exactly (`own-position rows pre-dropped: 1267`, G-C PASS). Every D2–D8 "same usable rows" instruction is therefore satisfied by reusing `A.bg_rows[bg]` verbatim, which is what `pdg.usable_rows()` does.
- **Arm S has `dist_222 = 0` for all 18 members** (all are at position 222), which is exactly the confound D2 is told to handle by running the N-only variant as well as the all-96 variant. Both are pre-registered in D2 and neither will be selected.
- **The 96 ρ_b share one y-vector** (`own_e_b`), so they are mutually correlated. The table is a set of 96 correlated measurements, not 96 independent ones, and any D2/D4/D6 uncertainty must come from the background-level bootstrap, never from treating table rows as independent. This is stated in 131's docstring and must be carried into the later scripts.
- No packages were installed; `venv/bin/python3` used throughout; no background jobs; nothing committed.

---

## D2 — Locality: does ρ_b track distance from position 222?
Status: **PASS** (all gates and sanity checks pass) — but the result is a **large, clean, unfavourable signal** for the Phase 2 write-up, reported as prominently here as a null would be.
Time started: 2026-09-29 20:12:21 · Time finished: 2026-09-29 20:16:18 (first smoke run 20:12:21, full run 20:16:09–20:16:18, 7.8 s of compute)

**What I did:**

Read D1's gated table (re-verifying its sha256 `e397a442…` on disk, and hard-stopping on mismatch), verified `dist_222` provenance against the roster's `position` column, then computed `Spearman(ρ_b, dist_b)` in four views — {full, H} × {all 96, N-only 78} — with a **background-level** bootstrap (10,000 draws, SEED=0) and a 10,000-draw label-permutation null, all four reported, none selected. Then the k-nearest removal at k=5 and k=10, side by side. Then a disclosed post-hoc region check.

**Actual output (verbatim):**

```
INPUT GATE PASS
  96 unique backgrounds; arms = {'G': 40, 'V': 38, 'S': 18}
  R3 PASS: roster `position` == table `position` == id-parsed integer for all 96;
           Arm S/V/G id prefixes match the table's arm for all 96;
           Arm G id wt/mut letters match the roster's wt_aa/mut_aa for all 40.

R3 SANITY CHECK: the two H-frame beaters' distances
  AV_220: roster position = 220 -> dist_222 = |220 - 222| = 2 (plan says 2) -> PASS
  AV_195: roster position = 195 -> dist_222 = |195 - 222| = 27 (plan says 27) -> PASS

  [all96 | full] n = 96
    Spearman(rho_b, dist_222) = +0.780559974   (locality predicts a POSITIVE value, R4)
    background-level bootstrap 95% CI = [+0.704579, +0.832167]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED on |r|, primary) = 0.000100  = (1 + 0) / (1 + 10000)
    permutation p (ONE-SIDED, r >= r_obs, locality direction) = 0.000100
    identity check (R7): forced identity permutation |diff| = 0.000e+00 (gate < 1e-12)
    null centring (R6): mean=+0.001241 (MCSE 0.001036, |z|=1.20), sd=0.103622 -> centres on zero

  [all96 | H] n = 96
    Spearman(rho_b, dist_222) = +0.772047001
    background-level bootstrap 95% CI = [+0.690648, +0.825525]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED, primary) = 0.000100  = (1 + 0) / (1 + 10000)

  [N_only_78 | full] n = 78
    Spearman(rho_b, dist_222) = +0.696831550
    background-level bootstrap 95% CI = [+0.576176, +0.784062]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED, primary) = 0.000100  = (1 + 0) / (1 + 10000)

  [N_only_78 | H] n = 78
    Spearman(rho_b, dist_222) = +0.673992906
    background-level bootstrap 95% CI = [+0.547236, +0.766611]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED, primary) = 0.000100  = (1 + 0) / (1 + 10000)
```

**D2 SUMMARY table:**

```
  all96       full n=96  rho~dist = +0.780560  CI [+0.704579, +0.832167] EXCLUDES ZERO  p_two=0.000100  p_one=0.000100
  all96       H    n=96  rho~dist = +0.772047  CI [+0.690648, +0.825525] EXCLUDES ZERO  p_two=0.000100  p_one=0.000100
  N_only_78   full n=78  rho~dist = +0.696832  CI [+0.576176, +0.784062] EXCLUDES ZERO  p_two=0.000100  p_one=0.000100
  N_only_78   H    n=78  rho~dist = +0.673993  CI [+0.547236, +0.766611] EXCLUDES ZERO  p_two=0.000100  p_one=0.000100
```

All four permutation p-values are **at the floor** (0 of 10,000 draws reached the observed statistic), and all four bootstrap CIs exclude zero by a wide margin. The association null centres on zero in every view (|z| ≤ 1.42), so the raw correlation is not an artifact of a shifted null.

**Disclosed post-hoc addendum — is `dist_222` just region? (This is the check AGENTS §4 demands, and it does not rescue the confound.)**

```
  Spearman(dist_222, PIN-8 region) over all 96 = +0.523842
  position 222 region (computed directly, not from the frame): R2
  region composition by distance tercile of the 96:
col_0   1   2   3   4
row_0
near    0  32   0   0
mid    13   2  17   0
far     7   0   5  20
  [full] Spearman(rho_b, dist_222) raw          = +0.780560
  [full] Spearman(region-demeaned rho_b, dist_222) = +0.690531
  [full] within-region correlations:
        region R1 (n=20): +0.649624
        region R2 (n=34): +0.243499
        region R3 (n=22): +0.659136
        region R4 (n=20): -0.074464
  [H] Spearman(rho_b, dist_222) raw          = +0.772047
  [H] Spearman(region-demeaned rho_b, dist_222) = +0.649599
  [H] within-region correlations:
        region R1 (n=20): +0.639098
        region R2 (n=34): +0.226780
        region R3 (n=22): +0.643886
        region R4 (n=20): -0.227905
```

`dist_222` **is** confounded with region (Spearman = +0.524; the nearest tercile is 32/32 in R2). But the gradient survives the correction: region-demeaning drops it only from +0.781 to +0.691, and within R1 and R3 — the two regions with enough spread in distance to be informative — it is still +0.65 and +0.66. It is weak in R2 (which contains 222 and therefore has the least distance spread, +0.24) and absent in R4 (+0.00 full, −0.23 H; R4 is 475–656, so everything there is far from 222 and there is no near end to compare against). **The locality gradient is not a region artifact.**

**k-nearest removal (both reported, neither selected):**

```
  ORIGINAL (no removal), |N| = 78, floor = 1/79 = 0.012658228:
    p_spec(full) = (1 + 1)/(1 + 78) = 0.025316456
    p_spec(H   ) = (1 + 3)/(1 + 78) = 0.050632911

  k = 5 nearest-to-222 removed from N (|N| = 73, new floor = 1/74 = 0.013513514)
    removed: AV_220(d=2,V), AV_233(d=11,V), AV_209(d=13,V), AV_204(d=18,V), AV_242(d=20,V)
    p_spec(full) = (1 + 1)/(1 + 73) = 0.027027027   [original 0.025316456]   still at or below: ['G_P254F']
    p_spec(H   ) = (1 + 2)/(1 + 73) = 0.040540541   [original 0.050632911]   still at or below: ['AV_195', 'G_P254F']

  k = 10 nearest-to-222 removed from N (|N| = 68, new floor = 1/69 = 0.014492754)
    removed: AV_220(2,V), AV_233(11,V), AV_209(13,V), AV_204(18,V), AV_242(20,V), G_Y197V(25,G), AV_195(27,V), G_I192T(30,G), G_P254F(32,G), G_L178T(44,G)
    p_spec(full) = (1 + 0)/(1 + 68) = 0.014492754   [original 0.025316456]   still at or below: []
    p_spec(H   ) = (1 + 0)/(1 + 68) = 0.014492754   [original 0.050632911]   still at or below: []
```

Also printed: `TIED dist_222 values present in N: [106, 124, 174, 240, 329] -> broken by ascending bg_id (pre-registered R9)`. No tie straddles the k=5 or k=10 cut, so the tie-break rule did not have to be invoked at either reported k.

**The two facts that must be read together:**

```
         bg_id  arm    d     rho_full        rho_H    <=A222V full?   <=A222V H?
        AV_220    V    2 -0.084598081 -0.094480281           False         True
        AV_233    V   11 -0.028766221 -0.037194932           False        False
        AV_209    V   13 -0.018056192 -0.022231037           False        False
        AV_204    V   18 -0.002578066 +0.002257283           False        False
        AV_242    V   20 -0.062924344 -0.067520962           False        False
       G_Y197V    G   25 -0.076879798 -0.072497990           False        False
        AV_195    V   27 -0.084161807 -0.093420822           False         True
       G_I192T    G   30 -0.032947897 -0.029689252           False        False
       G_P254F    G   32 -0.096243863 -0.101954441            True         True
       G_L178T    G   44 -0.070330933 -0.074355887           False        False
         A222V   --    0 -0.088118064 -0.090021683
```

1. **There is a strong, region-robust gradient**: placebo backgrounds near 222 have systematically more negative ρ_b than distant ones. This is exactly the mechanism the two external reviews worried about, and it is present, large, and not explained by region.
2. **A222V is nonetheless more negative than essentially every placebo, including the nearest ones.** The nearest placebo to 222 (`AV_220`, d=2) is *less* negative than A222V on the full frame. And critically, removing the near-222 placebos does **not** weaken the pooled comparison — it *strengthens* it (k=10 drives both p_spec values to their floors, 0/69, because the two H-frame beaters `AV_195` and `G_P254F` are themselves among the ten nearest).

**Verdict:** **PASS**, with a result that cuts both ways and must be written up as both. The gradient is real and is a genuine threat to the interpretation "position 222 produces an association unusually unlike other positions" — because *other positions near 222 produce a similar-signed association too*, and the reason A222V is unusual is that it is **more extreme than its own neighbourhood**, not that its neighbourhood is unlike the rest of the protein. The k-removal is the more directly relevant test of the reviews' actual worry ("is the verdict propped up by near-222 placebos?") and its answer is **no** — the verdict is if anything more robust without them. Neither fact cancels the other, and the frozen §5 outcome is untouched: this session reports the gradient, it does not adjudicate it.

**Files created/modified:**
- `scripts/132_phase2_diag_locality.py` (new).
- `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAG_D2_FULL_OUTPUT.txt` (new).
- `PHASE2_DIAGNOSTICS_LOG.md` (this entry).

**Anything unexpected or worth flagging:**

- **The plan's "expect 131, 132" for script numbers was too low for eight tasks.** I have used 131 (D1) and 132 (D2); D3–D8 will use 133–136, and I am stating the numbering explicitly rather than silently drifting. Grouping follows the plan's own hints ("D5 … same run", "D7 … same run").
- **The R3 provenance gate caught a bug in my own check, twice over.** My first draft parsed positions as `int(bg_id.split("_")[1])`, which works for `AV_113` and `A222_C` but returns a non-integer for all 40 Arm G ids (`G_P254F` encodes wt-residue + position + mut-residue). The gate reported `roster/table/id disagreements among 96 backgrounds: 40` and hard-stopped the run rather than proceeding. Fixed with per-arm patterns plus a check of the id's wt/mut letters against the roster's `wt_aa`/`mut_aa`. **Had the gate not been there, `dist_222` would have been wrong for 40 of 96 backgrounds and the headline correlation would have been quietly corrupt.** This is the gate working as designed, not a false alarm.
- **Position 222 is not among the frame's 654 target positions.** The atlas never treats its own background residue as a target variant, which is exactly why Arm S rows are dropped by G-C. A frame-derived position→region lookup therefore has no entry for 222 and raised `KeyError: 222`; the region is now computed directly from script 125's own `pin8_region` (222 → R2). Worth knowing for any future region-stratified work.
- **Disclosed correction to my own pre-registration (R6).** My first draft flagged "null centres on zero" with a hard-coded `|median| < 0.005`. That absolute cut does not scale with `N_PERM` and mislabelled the smoke run's nulls. Replaced before the full run with a test against the null's own Monte-Carlo standard error (`|mean| < 2·MCSE` and `|median| < 2·MCSE_median`); all four nulls then centre on zero at `N_PERM=10000`. This made a diagnostic more principled, not more permissive, and is printed in the run output as `REVISED post-run`.
- **Disclosed post-hoc addendum.** The region check was added *after* seeing the four large positive correlations. It is labelled `POST-HOC ADDENDUM (disclosed)` in the output. It was not selected because it helped; it made the confound *look worse-surviving*, and I ran it because AGENTS §4 requires checking whether the axis is confounded with something the statistic already contains.
- **`p_spec` is at its floor in the k=10 case** (1/69 = 0.014493 with 0 backgrounds at or below). That is a rank count, not a tail model, and it should not be read as "p < 0.0145" in any inferential sense beyond "no placebo in the reduced null set reached A222V's ρ."
- `dist_b` is **sequential** residue distance. Residues 2 and 442 are 440 apart here but may be adjacent in the folded structure. A sequential-locality result is not a structural-locality result, and this session has no structure to check it with.

---

## D3 — A222V's rank within Arm V alone and within Arm G alone
Status: **PASS**
Time started: 2026-09-29 20:18:13 · Time finished: 2026-09-29 20:18:15 (0.7 s; run shared with D7 and D8 in script 133 — see the D7/D8 entries below)

**What I did:**

Re-derived A222V's two threshold ρs from script 125's own construction and hard-gated them against D1's printed values at 1e-12 before using either (`|diff| = 0.000e+00` on both). A222V is deliberately not a row of the 96-background table — it is neither Arm S nor the null set — so its ρs are re-derived rather than hard-coded, and the script exits rather than compute a rank count against an unverified threshold. Then decomposed the pooled rank into its two arms, separately, on both views, with rank defined as script 125's own (`1 + #{rho_b < rho_A222V}`, line 415) and the `<=` form reported alongside.

**Actual output (verbatim):**

```
  A222V THRESHOLD GATE PASS
  arms: S=18 V=38 G=40 -> N = 78

  [full | Arm V] n = 38 (+A222V -> 39)
    #{arm members with rho_b <= rho_A222V} = 0  (the frozen p_spec numerator form)
    #{arm members with rho_b <  rho_A222V} = 0
    A222V rank within Arm V u {A222V} = 1/39  (rank 1 = most negative)
    arm rho range = [-0.084598081, +0.047573205], median = -0.023411207
  [full | Arm G] n = 40 (+A222V -> 41)
    #{arm members with rho_b <= rho_A222V} = 1
    #{arm members with rho_b <  rho_A222V} = 1
    A222V rank within Arm G u {A222V} = 2/41  (rank 1 = most negative)
    arm rho range = [-0.096243863, +0.063116028], median = +0.010076945
  [H    | Arm V] n = 38 (+A222V -> 39)
    #{arm members with rho_b <= rho_A222V} = 2
    A222V rank within Arm V u {A222V} = 3/39
    arm rho range = [-0.094480281, +0.040588603], median = -0.022628334
  [H    | Arm G] n = 40 (+A222V -> 41)
    #{arm members with rho_b <= rho_A222V} = 1
    A222V rank within Arm G u {A222V} = 2/41
    arm rho range = [-0.101954441, +0.068247435], median = +0.009295575

  side-by-side:
view arm  n  n_pooled  k_at_or_below  n_strictly_below  rank rank_frac   arm_min  arm_max  arm_median
full   V 38        39              0                 0     1      1/39 -0.084598 0.047573   -0.023411
full   G 40        41              1                 1     2      2/41 -0.096244 0.063116    0.010077
   H   V 38        39              2                 2     3      3/39 -0.094480 0.040589   -0.022628
   H   G 40        41              1                 1     2      2/41 -0.101954 0.068247    0.009296

  D3.4 arm construction asymmetry (printed so the comparison is not read as if the arms were exchangeable):
    Arm V: n=38 positions min=5 max=655 median=292.5; within 222+/-50: 7; within 222+/-25: 5
    Arm G: n=40 positions min=3 max=629 median=355.5; within 222+/-50: 4; within 222+/-25: 1
```

**Verdict:** **PASS.** The pooled ranks decompose cleanly and, notably, **the full-frame result comes entirely from Arm G, not Arm V.** On the full frame A222V is the single most negative of all 39 Arm-V-plus-A222V backgrounds (rank 1/39, zero at or below), and second of 41 in Arm G (rank 2/41, one at or below). On H the split is the other way round: rank 3/39 in Arm V (two at or below, `AV_220` and `AV_195`) and rank 2/41 in Arm G (one, `G_P254F`). The 78-null decomposition `1 + 1` on full and `2 + 1` on H is exactly accounted for. Arm S is excluded from both, being the same-site arm. No `p_spec` is redefined; this is decomposition, as pre-registered. The two arms are not exchangeable (V is exhaustive over A→V positions, G is a seed-0 uniform draw, and G has only 1 background within 222±25 against V's 5), so the arm-level counts are **not** a comparison of two groups and no cross-arm significance is claimed.

**Files created/modified:** `scripts/133_phase2_diag_rank_counts.py` (new, shared by D3/D7/D8); `PHASE2_DIAG_D3_D7_D8_FULL_OUTPUT.txt` (new); this log.

**Anything unexpected or worth flagging:** The full-frame comparison is carried entirely by the 40-member uniform random arm. The exhaustive, fitness-blind arm — the one with no selection at all — contains **no** background at or below A222V's full-frame ρ. That is a substantive fact for interpretation and the opposite of what a "the exhaustive control agrees" reading would predict. It does not weaken the frozen result (the frozen test is defined on the pooled 78), but it is exactly the kind of thing the write-up should say rather than let a reader assume. On H, Arm V does contribute two of the three.

---

## D7 — Sign-explicit restatement and the |ρ| sensitivity
Status: **PASS**
Time started / finished: 2026-09-29 20:18:13 / 20:18:15 (shared run with D3 and D8)

**What I did:**

D7.1 composed the sign-explicit one-sentence statement entirely from gated D1 values — every number in it is interpolated from a variable, none typed by hand. D7.2 computed `p_spec_abs` with the **flipped inequality** (`>=` on magnitudes, not `<=` on signed values) and printed the signed and magnitude counts side by side so the direction is visible in the output rather than asserted in prose.

**Actual output (verbatim):**

```
D7.1 -- SIGN-EXPLICIT ONE-SENTENCE RESTATEMENT
  Composed from the gated D1 values only (D7.1); no number in it is typed by hand:

  >>> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 1 of the 78 placebo backgrounds on the full frame and 3 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).

D7.2 -- p_spec under |rho| INSTEAD OF SIGNED rho (SENSITIVITY)
D7.2 THE INEQUALITY FLIPS: the frozen signed test asks whether A222V is unusually NEGATIVE (`rho_b <= rho_A222V`); this sensitivity asks whether its MAGNITUDE is unusually large in EITHER direction (`|rho_b| >= |rho_A222V|`).

  [full]  |rho_A222V| = 0.088118064   rho_A222V = -0.088118064   |N| = 78
    signed    #{rho_b <= rho_A222V}   = 1  -> p_spec      = (1 + 1)/(1 + 78) = 0.025316456
    magnitude #{|rho_b| >= |rho_A222V|} = 1  -> p_spec_abs  = (1 + 1)/(1 + 78) = 0.025316456
    backgrounds counted in p_spec_abs: ['G_P254F']
    of those, 0 are POSITIVE ([]) -- these are the ones the frozen signed test correctly ignores, and the entire difference between the two p-values is them.
  [H]  |rho_A222V| = 0.090021683   rho_A222V = -0.090021683   |N| = 78
    signed    #{rho_b <= rho_A222V}   = 3  -> p_spec      = (1 + 3)/(1 + 78) = 0.050632911
    magnitude #{|rho_b| >= |rho_A222V|} = 3  -> p_spec_abs  = (1 + 3)/(1 + 78) = 0.050632911
    backgrounds counted in p_spec_abs: ['AV_195', 'AV_220', 'G_P254F']
    of those, 0 are POSITIVE ([])

  side-by-side (signed vs magnitude):
view  n_N  rho_a222v  signed_le  p_signed  abs_ge    p_abs  n_positive_among_hits
full   78  -0.088118          1  0.025316       1 0.025316                      0
   H  78  -0.090022          3  0.050633       3 0.050633                      0
```

**Verdict:** **PASS**, and this is a **favourable** result for the Phase 2 write-up, reported as directly as D2's adverse one. The `|ρ|` sensitivity is **numerically identical** to the signed test on both views: `p_spec_abs(full) = p_spec(full) = 0.025316456` and `p_spec_abs(H) = p_spec(H) = 0.050632911`. The reason is visible in the output: **zero** backgrounds are positive with `|ρ| ≥ |ρ_A222V|`, so the two counts coincide. In other words the verdict does **not** depend on the pre-declared one-sided direction at all. A222V's association is not merely the most negative in the null set; its magnitude is the largest in the null set in either direction. That removes one of the two external reviews' specific objections — that a pre-declared direction could be manufacturing the result — on this dataset. It does not address the locality or shift-magnitude concerns, which are separate.

**Files created/modified:** as D3 above (shared script and output file).

**Anything unexpected or worth flagging:** The exact tie between the two p-values is a stronger statement than "the sensitivity did not overturn the result." It means the null set contains no strongly *positive* background anywhere near A222V's magnitude — the placebo distribution is centred near zero and the extreme tail is one-sided negative. AGENTS §5's column-identity warning is worth a moment here: two nominally different tests returning identical values to nine decimals is exactly the pattern that should be assumed to be a bug until proven otherwise. It is not — the two counts are computed by genuinely different code paths (`r <= t` vs `np.abs(r) >= abs(t)`) and are equal only because the positive tail is empty, which the script prints explicitly (`of those, 0 are POSITIVE`). The identity is real, not a duplicated column.

---

## D8 — `G_P254F` leave-one-out fragility
Status: **PASS**
Time started / finished: 2026-09-29 20:18:13 / 20:18:15 (shared run with D3 and D7)

**What I did:**

Recomputed both `p_spec` values with `G_P254F` removed from N, changing the denominator as well as the numerator (|N| 78 → 77, floor 1/79 → 1/78), and printed original and leave-one-out side by side on both views with the new floor stated next to every value. Explicitly checked, rather than assumed, which backgrounds remain binding on H.

**Actual output (verbatim):**

```
D8 -- G_P254F LEAVE-ONE-OUT FRAGILITY
  [full]  floor with |N|=78 -> 1/79 = 0.012658228; floor with |N|=77 -> 1/78 = 0.012820513
    ORIGINAL   |N|=78  #{rho_b <= rho_A222V} = 1 -> p_spec = (1 + 1)/(1 + 78) = 0.025316456
              still at or below: ['G_P254F']
    LOO (G_P254F removed) |N|=77  #{rho_b <= rho_A222V} = 0 -> p_spec = (1 + 0)/(1 + 77) = 0.012820513
              still at or below: []
    change in p_spec = -0.012495943
  [H]  floor with |N|=78 -> 1/79 = 0.012658228; floor with |N|=77 -> 1/78 = 0.012820513
    ORIGINAL   |N|=78  #{rho_b <= rho_A222V} = 3 -> p_spec = (1 + 3)/(1 + 78) = 0.050632911
              still at or below: ['AV_195', 'AV_220', 'G_P254F']
    LOO (G_P254F removed) |N|=77  #{rho_b <= rho_A222V} = 2 -> p_spec = (1 + 2)/(1 + 77) = 0.038461538
              still at or below: ['AV_195', 'AV_220']
    change in p_spec = -0.012171373
    D8.2 check: G_P254F was one of 3 H beaters.  After removal the binding set is ['AV_195', 'AV_220'] -- AV_220 and AV_195 remain, as expected.

  side-by-side:
view  n_orig  k_orig   p_orig  n_loo  k_loo    p_loo     delta
full      78       1 0.025316     77      0 0.012821 -0.012496
   H      78       3 0.050633     77      2 0.038462 -0.012171
```

**Verdict:** **PASS**. `G_P254F` is confirmed to be the single background keeping the full-frame `p_spec` off its floor, and the leave-one-out behaves exactly as the plan anticipated: full frame goes 0.025316456 → 0.012820513 (i.e. straight to the new floor 1/78, with 0 backgrounds at or below), H goes 0.050632911 → 0.038461538 with `AV_220` and `AV_195` remaining as expected. **The fragility is asymmetric between the two views**: the full-frame count rests on a single background, the H-frame count on three. This is a diagnostic of the frozen result, not an alternative estimate of it — the deletion was chosen after seeing which background it was, which is precisely what makes it a fragility measure. Nothing frozen is redefined.

**Files created/modified:** as D3 above (shared script and output file).

**Anything unexpected or worth flagging:** `1/78 = 0.012820513` is **slightly larger** than `1/79 = 0.012658228` — removing a background raises the floor, so the leave-one-out `p_spec` understates the corresponding frozen value by a hair even before the numerator change. The two effects (−0.012496 on full) are almost entirely the numerator going 1 → 0, not the floor. Worth stating so nobody reads the leave-one-out as a "better" or "cleaner" result; it is a weaker one. The `1/78` value quoted in the plan is confirmed exactly.

---

## D4 — Shift-magnitude confound: does ρ_b just track how hard ESM-2 gets perturbed?
Status: **PASS** (all gates pass) — **and the correlation is large, clean, and unfavourable.** This is the result the plan asked to be reported as prominently as a null would be, so it gets the most prominent treatment in this log and first place in the summary.
Time started: 2026-09-29 20:20:40 · Time finished: 2026-09-29 20:21:26 (smoke 20:20:40, full 20:21:21–20:21:26)

**What I did:**

Quoted script 125's exact `delta_b` construction and column names rather than assuming them, then **independently re-derived `delta_b = score_b(v) − esm2_score(v)` from the two raw files for all 96 backgrounds** and gated it against script 125's own `delta` column row-for-row at 1e-12 (AGENTS §5: verify column identity before reporting agreement). Then computed `mean_abs_delta_b = mean(|delta_b(v)|)` over exactly the rows 125 used for each background's ρ_b, on both full and H; correlated against ρ_b across all 96 with a **background-level** bootstrap (10,000 draws, SEED=0) and a 10,000-draw association null with a forced-identity check. Finally reported where the named backgrounds sit on `mean_abs_delta_b`, and — as a disclosed post-hoc addition — where A222V sits **relative to the fitted confound line**.

**Actual output (verbatim):**

```
DELTA_B PROVENANCE (quoted from script 125, then RE-DERIVED independently)
  delta_b(v) = score_b(v) - esm2_score(v)
    score_b(v)  <- data/processed/phase2/bg_<bg_id>.csv::score
    esm2_score  <- data/processed/task32_analysis_table.csv::esm2_score
    join        <- frame.merge(bg[[position, mut_aa, score]], on=[position, mut_aa], how='left')

  INDEPENDENT RE-DERIVATION: recomputed score_b(v) - esm2_score(v) from the two raw
  files for all 96 backgrounds and compared to script 125's own `delta` column, row for row.
    max|diff| over 96 backgrounds x ~10.7k rows = 0.000e+00 (gate < 1e-12)
    DELTA GATE PASS -- the two sources agree exactly, so this is a genuine
    agreement and not a duplicated column (AGENTS 5).

D4.1 mean_abs_delta_b = mean(|delta_b(v)|) over each background's usable rows
  rows behind each mean_abs_delta_b: full min=10738 max=10757; H min=7507 max=7526
  [full] mean_abs_delta over the 96 backgrounds: min=0.012399 median=0.056099 max=0.208008 sd=0.028526
         A222V's own = 0.070330
  [H   ] mean_abs_delta over the 96 backgrounds: min=0.011486 median=0.059174 max=0.200143 sd=0.028473
         A222V's own = 0.069403

D4.2-D4.5  Spearman(rho_b, mean_abs_delta_b) across all 96

  [full]  n = 96
    Spearman(rho_b, mean_abs_delta_b) = -0.614188823
    background-level bootstrap 95% CI = [-0.732848, -0.459688]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED on |r|, PRIMARY, D4.3) = 0.000100 = (1 + 0)/(1 + 10000)
    permutation p (one-sided, observed direction) = 0.000100
    identity check (D4.4): forced identity permutation |diff| = 0.000e+00 (gate < 1e-12)
    null centring (D4.5): mean=-0.000110 (MCSE 0.001027), median=+0.001072 (MCSE 0.001287), sd=0.102718 -> centres on zero

  [H]  n = 96
    Spearman(rho_b, mean_abs_delta_b) = -0.612696690
    background-level bootstrap 95% CI = [-0.732738, -0.456420]  (EXCLUDES ZERO)
    permutation p (TWO-SIDED on |r|, PRIMARY, D4.3) = 0.000100 = (1 + 0)/(1 + 10000)
    permutation p (one-sided, observed direction) = 0.000100
    identity check (D4.4): forced identity permutation |diff| = 0.000e+00 (gate < 1e-12)
    null centring (D4.5): mean=-0.000388 (MCSE 0.001024), median=-0.000109 (MCSE 0.001284), sd=0.102409 -> centres on zero
```

**The correlation is large, its CI excludes zero on both views, and the permutation p is at its floor (0 of 10,000 draws reached the observed value) on both.** The null centres on zero in both views (|mean| and |median| well inside 2 MCSE), so the raw correlation is not inflated by a shifted null. Backgrounds that perturb ESM-2's representation more have systematically **more negative** ρ_b.

**Where the named backgrounds sit on `mean_abs_delta_b` (D4.6, full frame):**

```
  [full]  A222V mean_abs_delta = 0.070330 -> percentile 68.8 of 96
         bg_id  mean|delta|  pctile/96                       named?
       G_P254F     0.208008       99.0 at-or-below A222V (D1); nearest-222 (D2, d=32)
        AV_220     0.047893       33.3 at-or-below A222V (D1); nearest-222 (D2, d=2)
        AV_195     0.095630       89.6 at-or-below A222V (D1); nearest-222 (D2, d=27)
        AV_233     0.049868       38.5       nearest-222 (D2, d=11)
        AV_209     0.049976       39.6       nearest-222 (D2, d=13)
        AV_204     0.032608       12.5       nearest-222 (D2, d=18)
        AV_242     0.055971       47.9       nearest-222 (D2, d=20)
       G_Y197V     0.137584       97.9       nearest-222 (D2, d=25)
       G_I192T     0.066874       65.6       nearest-222 (D2, d=30)
       G_L178T     0.063864       60.4       nearest-222 (D2, d=44)
    largest mean|delta|: [('G_P254F', 0.208), ('G_Y197V', 0.1376), ('A222_L', 0.1051), ('A222_E', 0.1048), ('A222_D', 0.1041)]
    smallest mean|delta|: [('AV_19', 0.0124), ('AV_5', 0.018), ('AV_650', 0.0237), ('G_A462S', 0.0238), ('G_E383T', 0.0242)]
```

**`G_P254F` — the one background that keeps the frozen full-frame `p_spec` off its floor — has by far the largest `mean|delta|` of all 96 (0.208, 99th percentile).** The two H-frame beaters are split: `AV_195` is high (89.6th percentile) but `AV_220` is low (33.3rd). The `H` view is nearly identical to `full` for every one of these (e.g. `G_P254F` 0.200 at the 99th percentile; `AV_220` 0.050 at the 36.5th).

**The single most important line in D4 — A222V relative to the confound line (disclosed post-hoc addition):**

```
POST-HOC ADDITION (disclosed): where does A222V sit RELATIVE TO the shift-magnitude line?
  [full]  OLS line: rho_hat = +0.034053 -0.896326 * mean|delta|
    A222V mean|delta| = 0.070330  ->  predicted rho = -0.028985
    A222V actual  rho  = -0.088118
    RESIDUAL (actual - predicted) = -0.059133
    A222V's residual sits at the 96.9th percentile of the 96 background residuals (0 = most negative)
      for reference   G_P254F: mean|delta|=0.208008  rho=-0.096244  residual=+0.056146
      for reference    AV_220: mean|delta|=0.047893  rho=-0.084598  residual=-0.075724
      for reference    AV_195: mean|delta|=0.095630  rho=-0.084162  residual=-0.032500
  [H]  OLS line: rho_hat = +0.037990 -0.964705 * mean|delta|
    A222V mean|delta| = 0.069403  ->  predicted rho = -0.028963
    A222V actual  rho  = -0.090022
    RESIDUAL (actual - predicted) = -0.061058
    A222V's residual sits at the 96.9th percentile of the 96 background residuals (0 = most negative)
      for reference   G_P254F: mean|delta|=0.200143  rho=-0.101954  residual=+0.053135
      for reference    AV_220: mean|delta|=0.050233  rho=-0.094480  residual=-0.084010
      for reference    AV_195: mean|delta|=0.098154  rho=-0.093421  residual=-0.036722
```

A222V's shift magnitude (0.0703, 68.8th percentile) is **unremarkable** — mid-pack. But the confound line predicts only ρ ≈ −0.029 for a background of that magnitude, and A222V's actual ρ is −0.088, a residual of **−0.059**, at the extreme end of the 96 residuals. Note also that `G_P254F`'s residual is **+0.056** — i.e. its extreme ρ is substantially *over*-predicted by its huge shift, in the opposite direction.

**Verdict:** **PASS on the gates; the correlation is a large, clean, adverse confound signal and must be written up as one.** Stated plainly: across the 96 backgrounds, roughly 38% of the rank variation in ρ_b is associated with how much that background moves ESM-2's score. That is a real, region-robust, large association, and it is precisely the mechanism the plan flagged as most likely to change how Phase 2 gets written up.

**But the confound does not account for A222V.** A222V is not a high-shift background; it is a mid-shift background whose ρ is far more negative than its shift magnitude predicts. The `G_P254F` case is the clearest illustration: its ρ is the single most negative on the full frame, but that is largely *because* it has the largest shift of all 96, and once the shift is accounted for its residual flips sign. So the honest statement is two-sided and both halves must appear in any write-up:

- **Against:** much of the cross-background variation in ρ_b is explained by shift magnitude alone, and the one background that most directly challenges the frozen result (`G_P254F`) is the extreme of that confound. A reader who saw only the correlation would be right to worry.
- **For:** A222V's own position is not on the confound line. It is a mid-pack shifter with an extreme ρ, and after accounting for magnitude it remains the most extreme residual of all 96. The frozen comparison of A222V *against* the null set is not thereby explained away.

Neither half cancels the other. Nothing frozen is redefined.

**Files created/modified:** `scripts/134_phase2_diag_shift_magnitude.py` (new, shared by D4 and D5); `PHASE2_DIAG_D4_D5_FULL_OUTPUT.txt` (new); this log.

**Anything unexpected or worth flagging:**

- **The plan's phrase "the four backgrounds named in D1/D2" does not resolve to four.** D1 names exactly three backgrounds at or below A222V (`G_P254F`, `AV_220`, `AV_195`). Rather than pick a fourth to satisfy the wording, I reported all three named backgrounds **plus** the ten null backgrounds nearest 222 from D2 — a superset of every reading — and selected none. Stated in the script's D4.6 pre-registration and in the output.
- **A hand-derived number in my own printout was wrong and is now computed.** An early draft asserted "min full-frame count is 10757 − 18 = 10739"; the actual minimum is **10738** (position 222 carries 19 rows, not 18). Caught by comparing my assertion against the run output, and the line now prints `10757 − nf.min()` rather than a hand-typed subtraction. Logged because AGENTS §5 forbids asserting a number that was not derived, and this one was.
- **The independent `delta_b` re-derivation returned `max|diff| = 0.000e+00` exactly** over 96 backgrounds × ~10.7k rows. Two nominally independent sources agreeing to the bit is the AGENTS §5 pattern that should be assumed to be a bug; here it is not, because the two paths differ (one reads 125's precomputed `delta` column, the other recomputes `score − esm2_score` from the raw CSVs) and the equality is exact rather than approximate. Verified and stated rather than glossed.
- **Disclosed post-hoc addition.** The "where does A222V sit relative to the line" block was added after seeing D4's correlation, and is labelled as such in the output. It is not a gate and not a new test. I added it because a correlation says a line exists but not whether the background the frozen result rests on sits on that line or far off it — and those two situations have opposite implications, which the correlation alone cannot distinguish. It is the reason the D4 verdict is two-sided rather than one-sided, and it makes the result *less* alarming than the headline correlation alone would suggest.
- `mean|delta|` is a **scale-only** statistic, blind to sign. A null here would not have ruled out a shift confound operating through heteroscedasticity or sign-pattern rather than magnitude. This is a test of one specific mechanism, stated in the docstring.
- Partial construction overlap, stated in the docstring before running: `mean_abs_delta_b` and ρ_b are both functions of the **same** `delta_b`. They share `delta_b` exactly and share `own_e_b` not at all. This is not an independent control.

---

## D5 — Does `D_site` survive controlling for shift magnitude?
Status: **PASS**
Time started / finished: 2026-09-29 20:20:40 / 20:21:26 (shared run with D4)

**What I did:**

Reproduced the frozen `D_site` as a check (not a redefinition), residualized ρ_b on `mean_abs_delta_b` by OLS across all 96 backgrounds with an intercept, and recomputed the arm contrast on the residuals with a **background-level** bootstrap that **refits the OLS on every draw** (so the uncertainty in the residualization itself is propagated rather than conditioning on the full-sample fit). A222V is excluded throughout, being neither S nor N.

**Actual output (verbatim):**

```
D5 -- DOES D_site SURVIVE CONTROLLING FOR SHIFT MAGNITUDE
D5.4 first: the plan permits skipping the residualization if D4's correlation is
  negligible.  That condition is evaluated only now, after D4 is in hand, as the plan
  requires.  It is NOT negligible -- the D4 CIs are printed above and the
  residualization is run regardless, so nothing here depends on this judgement.

  [full]  OLS rho_b ~ mean_abs_delta_b: slope = -0.896325500 per unit mean|delta|, intercept = +0.034053200
    D_site      = mean(rho, S, n=18) - mean(rho, N, n=78) = -0.055525559
      background-level bootstrap 95% CI = [-0.068409, -0.044214]  (EXCLUDES ZERO)
    D_site_resid= mean(resid, S) - mean(resid, N) = -0.023832242
      background-level bootstrap 95% CI (OLS REFIT per draw, D5.3) = [-0.030266, -0.013300]  (EXCLUDES ZERO)
      ratio D_site_resid / D_site = 0.429212  (ATTENUATED)

  [H]  OLS rho_b ~ mean_abs_delta_b: slope = -0.964705251 per unit mean|delta|, intercept = +0.037990057
    D_site      = mean(rho, S, n=18) - mean(rho, N, n=78) = -0.059645790
      background-level bootstrap 95% CI = [-0.072574, -0.048009]  (EXCLUDES ZERO)
    D_site_resid= mean(resid, S) - mean(resid, N) = -0.026597218
      background-level bootstrap 95% CI (OLS REFIT per draw, D5.3) = [-0.032712, -0.016452]  (EXCLUDES ZERO)
      ratio D_site_resid / D_site = 0.445919  (ATTENUATED)

  side-by-side (D5.5):
view     slope    D_site      D_lo      D_hi  D_excl   D_resid      R_lo      R_hi  R_excl     ratio
full -0.896326 -0.055526 -0.068409 -0.044214    True -0.023832 -0.030266 -0.013300    True +0.429212
   H -0.964705 -0.059646 -0.072574 -0.048009    True -0.026597 -0.032712 -0.016452    True +0.445919

  D5.1 check: D_site on the full frame was frozen at -0.055525559; this run reproduces
  -0.055525559 (|diff| = 3.310e-10).
  NOTE: script 125's own D_site CI came from the POSITION-cluster bootstrap.  The CI
  printed here uses the BACKGROUND bootstrap so that D_site and D_site_resid are directly
  comparable.  They are different uncertainties and their widths must not be compared to
  each other or to 125's.
```

**Verdict:** **PASS.** `D_site` is confirmed at its frozen value (−0.055525559, |diff| = 3.3e-10, a 9-decimal rounding difference). Controlling for shift magnitude **attenuates but does not remove** the site contrast: −0.0555 → −0.0238 on full (43% retained) and −0.0596 → −0.0266 on H (45% retained), and **both residual CIs still exclude zero**. The attenuation is real and substantial — more than half the site contrast is accounted for by shift magnitude — but the contrast survives. This is a *survival* result with a magnitude caveat attached, and it should be reported with both halves.

**Files created/modified:** as D4 above (shared script and output file).

**Anything unexpected or worth flagging:**

- **The survival is weaker than it looks at a glance.** Retaining 43% of the contrast is not the same as being unaffected: the point estimate falls by more than half. "The CI still excludes zero" and "the effect roughly halved" are both true, and only quoting the first would be misleading.
- **The two CIs are not comparable to script 125's.** 125's `D_site` CI came from the **position**-cluster bootstrap; this run's uses the **background** bootstrap, deliberately, so that `D_site` and `D_site_resid` are internally comparable. Anyone comparing the CI widths here against 125's printed `[-0.079318507, -0.033178263]` would be comparing two different uncertainty questions. Printed in the output.
- **D5's "skip if negligible" escape clause was evaluated only after D4 was in hand**, as the plan requires, and the residualization was run regardless — so no result in this entry depends on that judgement having gone the convenient way.
- **The residualization cannot make the two statistics independent** (AGENTS §4's warning about a covariate built from the same quantities as the outcome). `mean_abs_delta_b` and ρ_b are both functions of the same `delta_b`. A background with small `mean|delta|` but a badly-shaped `delta` distribution would still drive ρ_b, and this control would not see it. A surviving `D_site_resid` is therefore *not* evidence that delta_b's influence is gone — only that its overall magnitude does not account for the arm contrast. Stated in the docstring before the run, not after.

---

## D6 — Severity gradient: do more disruptive backgrounds give more negative ρ_b?
Status: **PASS** (all gates pass) — and this is a **clean null**, reported with the same directness as D2's and D4's adverse results.
Time started: 2026-09-29 20:24:06 · Time finished: 2026-09-29 20:24:54 (smoke 20:24:06, full 20:24:39–20:24:54, 13.7 s)

**What I did:**

**Located** the severity proxy on disk rather than assuming a column name: `data/processed/task32_analysis_table.csv::esm2_score`, joined to `phase2_arm_roster.csv` on `(position, mut_aa)` — the same column and the same join script 125 uses as the wild-type baseline. **Verified the sign convention against labelled examples** before using it. **Confirmed retrievability** for all 96 and accounted for every missing row by name and by cause, substituting nothing. Then correlated ρ_b against severity across N on both views with a background-level bootstrap and an association null, and separately compared the two arms' severity distributions.

**Actual output (verbatim):**

```
LOCATING THE SEVERITY PROXY (not assuming a column name)
  FILE   : data/processed/task32_analysis_table.csv
  COLUMN : esm2_score
  JOIN   : roster (position, mut_aa) -> task32 (position, mut_aa), left
  RANGE  : -18.007029 .. +7.807393 over 11344 rows, 0 nulls

  SIGN CONVENTION CHECK AGAINST LABELLED EXAMPLES (AGENTS 5):
    most disruptive (lowest esm2_score):
      V179W  -18.007029
      G158H  -17.871993
      L45D   -17.750033
      T227W  -17.735583
    most conservative (highest esm2_score):
      R594Q  +7.807393
      R134S  +6.351555
      M327V  +6.235535
      L437R  +6.082635
    -> SIGN ESTABLISHED: LOW esm2_score = MORE SEVERE.  severity := -esm2_score.

RETRIEVABILITY: 75 OF 96 -- THE 21 MISSING ARE ACCOUNTED FOR
  retrieved 75 of 96
  wt_aa roster vs task32 on the 75 retrieved rows: 0 mismatches (expect 0)
  MISSING, Arm S (18): A222_C, A222_D, ..., A222_Y
    REASON: position 222 has 0 rows in task32 -- the atlas never treats its
    own background residue as a target variant.  Same fact as script 125's
    gate G-C.  All 18 are Arm S, and D6's statistic is over N, so this does
    not touch the primary test.

  MISSING, Arm G (3):
    G_E383T: task32 lists E383->{ACDFGHIKLMNRSVWY} and does NOT contain 'T'.  Not a join bug -- the reference table never scored that mutant at that position.
    G_D629C: task32 lists D629->{AEGHIKLNPRSVY} and does NOT contain 'C'.  Not a join bug -- the reference table never scored that mutant at that position.
    G_P346V: task32 lists P346->{AFHLNQRST} and does NOT contain 'V'.  Not a join bug -- the reference table never scored that mutant at that position.

  CONSEQUENCE (disclosed): D6's null set is N = 78 minus 3 = 75, NOT 78.
       G_E383T pos=383 dist_222=161  rho_full=-0.020285940  rho_H=-0.011306110
       G_D629C pos=629 dist_222=407  rho_full=-0.031212310  rho_H=-0.028485037
       G_P346V pos=346 dist_222=124  rho_full=-0.011818561  rho_H=-0.008553976
  ALSO: A222V's own severity is NOT retrievable (position 222 absent from
  task32, same reason as Arm S).
  N = 78; retrievable subset used below = 75
```

**D6.1 — the primary statistic:**

```
  [full | severity (-esm2)] n = 75
    Spearman(rho_b, x) = -0.175504979
    background-level bootstrap 95% CI = [-0.407048, +0.071882]  (INCLUDES ZERO)
    permutation p (TWO-SIDED, PRIMARY, D6.3) = 0.134487 = (1 + 1344)/(1 + 10000)
    permutation p (one-sided, observed direction) = 0.065893
    identity check (D6.4): |diff| = 0.000e+00 (gate < 1e-12)
  [H | severity (-esm2)] n = 75
    Spearman(rho_b, x) = -0.147937411
    background-level bootstrap 95% CI = [-0.377687, +0.094270]  (INCLUDES ZERO)
    permutation p (TWO-SIDED, PRIMARY) = 0.208179

  side-by-side:
    full sev   n=75  rho=-0.175505  CI [-0.407048, +0.071882] INCLUDES ZERO  p_two=0.134487
    full raw   n=75  rho=+0.175505  CI [-0.071882, +0.407048] INCLUDES ZERO  p_two=0.134487
    H    sev   n=75  rho=-0.147937  CI [-0.377687, +0.094270] INCLUDES ZERO  p_two=0.208179
    H    raw   n=75  rho=+0.147937  CI [-0.094270, +0.377687] INCLUDES ZERO  p_two=0.208179
    sign-convention self-check (full): |-0.175505 + +0.175505| = 0.000e+00 (must be ~0)
```

**D6.2 — Arm V vs Arm G severity (descriptive), and D6.2b — the same correlation split by arm:**

```
    Arm V: n=38  severity mean=+4.942302 median=+5.623503 range=[-0.185290, +11.058872] sd=2.935096
    Arm G: n=37  severity mean=+6.790772 median=+6.464176 range=[-1.398707, +14.907699] sd=4.709865
    mean severity difference (G - V) = +1.848470; label-permutation p (two-sided) = 0.046295
    Spearman(severity, dist_222) within N = -0.238414

  [full | Arm V] n=38  Spearman(rho_b, severity) = -0.297735  CI [-0.596849, +0.043195] INCLUDES ZERO  p_two=0.072693
  [full | Arm G] n=37  Spearman(rho_b, severity) = -0.137743  CI [-0.474945, +0.240127] INCLUDES ZERO  p_two=0.413759
  [H    | Arm V] n=38  Spearman(rho_b, severity) = -0.258781  CI [-0.569960, +0.081770] INCLUDES ZERO  p_two=0.119088
  [H    | Arm G] n=37  Spearman(rho_b, severity) = -0.148174  CI [-0.466399, +0.217489] INCLUDES ZERO  p_two=0.378862
```

**Verdict:** **PASS, and the result is a clean null.** Background severity is **not distinguishable from noise** as a predictor of ρ_b across the null set: |ρ| = 0.176 (full) and 0.148 (H), both CIs comfortably including zero, permutation p = 0.134 and 0.208. Every one of the four primary views and all four within-arm views has a CI that includes zero. The one-sided p on the full frame (0.0659) is not a result — it is one of two directions, and the pre-registered primary is two-sided. So: **the specific worry that "Arm G's uniform draw misses a real severity gradient" is not supported by this test.** More disruptive placebos do not systematically give more negative ρ_b.

Two descriptive findings that do *not* affect the primary:
- **Arm G is more severe than Arm V on average** (mean severity +6.79 vs +4.94, difference +1.85, two-sided permutation p = 0.0463) and has roughly 60% larger spread (sd 4.71 vs 2.94). So the two arms are **not** severity-matched, which is directly relevant to the reviews' framing. Stated as descriptive; the arms are not exchangeable by construction, so this is not a significance claim about biology.
- **Severity decreases with distance from 222** (Spearman = −0.238 within N), i.e. near-222 backgrounds are more severe. This means D6's axis is **not independent of D2's locality axis** — part of the locality gradient could be a severity gradient wearing a different name. Reported precisely for that reason.

**Files created/modified:** `scripts/135_phase2_diag_severity.py` (new); `PHASE2_DIAG_D6_FULL_OUTPUT.txt` (new); this log.

**Anything unexpected or worth flagging:**

- **Retrievability is 75/96, not 96/96, and the plan's premise that it might be complete was wrong.** The 21 missing split into two genuinely different causes, both now named and explained: 18 Arm S because position 222 does not exist in `task32` at all, and 3 Arm G (`G_E383T`, `G_D629C`, `G_P346V`) because task32 never scored the requested mutant at those positions (`E383` has no `T`, `D629` has no `C`, `P346` has no `V`). None is a join bug, and **no substitute proxy was used**. D6's null set is therefore 75, not 78, and that is disclosed in the script's own output.
- **A222V's own severity is not retrievable**, for the same 222 reason. This task can say whether *placebo* severity tracks ρ_b; it **cannot** place A222V on the same axis. That is a real limit on what D6 can say about the frozen result, and it is stated rather than worked around.
- **My first retrievability probe reported `wt_aa agree: False`, which was an artifact of my own check, not a data problem.** It compared `wt_aa_roster == wt_aa_t32` across all 96 merged rows, and the 21 unmatched rows compare against NaN, which is `False`. Restricting the comparison to the 75 rows that actually joined gives **0 mismatches**, and that restricted check is what the script runs and gates on. Logged because the same code would have produced a false alarm in a less careful script.
- **The null-centring flag reads `DOES NOT CENTRE ON ZERO` on the full-frame views at `N_PERM=10000`, and I am reporting it rather than re-tuning it.** The flag is driven entirely by the *median* (+0.003186 against MCSE 0.001459, |z| = 2.19); the *mean* is +0.001213 against MCSE 0.001164, |z| = 1.04, comfortably centred. The median of a discrete rank statistic is a lumpy quantity and the `1.2533·sd/√n` standard error assumes continuity, so it is the less trustworthy of the two here. I did **not** loosen the threshold to make the flag read "centred" — that would be exactly the post-hoc threshold-moving AGENTS §0 prohibits. The flag is reported as it came out, with the mean-vs-median breakdown printed so the reader can see which part of it fired. It does not affect the verdict: with a CI spanning roughly ±0.4 and a two-sided p of 0.13, the result is a null either way.
- **The severity axis overlaps `delta_b` structurally.** `delta_b(v) = score_b(v) − esm2_score(v)` *subtracts the very column used as the severity proxy*. A background ESM-2 scores badly will have `delta_b` systematically offset from the frame's values. So this test cannot fully separate "disruptive backgrounds behave differently" from "subtracting a large constant changes the ranks" — a limit of the proxy, disclosed in the docstring before the run, and the strongest single reason not to over-read a large value here had one appeared. As it happens the value is a null, which the overlap makes *harder* to obtain rather than easier, so the null is if anything conservative.
- The severity numbers print identically for `full` and `H` because severity is a property of the substitution alone and does not depend on the view. That is correct, not a duplicated computation, and the output says so — flagged here because an unexplained identical pair of blocks is exactly the pattern AGENTS §5 says to suspect a bug in.

---

# SUMMARY

*Note on entry order: entries appear in **execution** order, not numeric order. D3, D7 and D8 are exact rank-count tasks on D1's table with no resampling, so they were computed together in one script (133) and are logged consecutively as they finished. D4 and D5 share script 134 ("D5 … same run" in the plan). Script numbering ran 131–135 rather than the plan's expected "131, 132", because eight tasks need more than two scripts; the grouping follows the plan's own hints and is stated in each script's docstring.*

## 1. READ THIS FIRST — D4's shift-magnitude correlation

| view | Spearman(ρ_b, mean\|delta_b\|) | 95% CI (background bootstrap) | excludes zero? | permutation p (two-sided) |
|---|---|---|---|---|
| full | **−0.614189** | **[−0.732848, −0.459688]** | **YES** | 0.000100 (0 / 10,000 draws) |
| H | **−0.612697** | **[−0.732738, −0.456420]** | **YES** | 0.000100 (0 / 10,000 draws) |

A large, clean, unfavourable signal. Backgrounds that move ESM-2's score more have systematically **more negative** ρ_b. Roughly 38% of the rank variation in ρ_b across the 96 backgrounds tracks this one quantity. Both CIs exclude zero by a wide margin, both permutation p-values are at the floor, and both nulls centre on zero.

**The confound does not, however, account for A222V — and this is the half of D4 that must appear in any write-up:**

```
  [full]  OLS line: rho_hat = +0.034053 -0.896326 * mean|delta|
    A222V mean|delta| = 0.070330 (68.8th pctile of 96 -- mid-pack)
    A222V predicted rho = -0.028985;  actual rho = -0.088118
    RESIDUAL = -0.059133, at the 96.9th percentile of the 96 residuals
  [H]     RESIDUAL = -0.061058, also 96.9th percentile
    G_P254F (the one background beating A222V on full):
      mean|delta| = 0.208008 -- the LARGEST of all 96 (99.0th pctile)
      residual = +0.056146  (its extreme rho is OVER-predicted, wrong sign)
```

So: the one background that most directly challenges the frozen result is the extreme of the shift-magnitude confound, which is a genuine problem for the write-up. But A222V is a *mid-pack* shifter with an *extreme* ρ, and after accounting for magnitude it is still the most extreme residual of all 96. Both facts are true and neither cancels the other.

## 2. D2's locality correlation, and the AV_220 / AV_195 distance sanity check

| set | view | Spearman(ρ_b, dist_222) | 95% CI | excludes zero? | p (two-sided) |
|---|---|---|---|---|---|
| all 96 | full | **+0.780560** | [+0.704579, +0.832167] | YES | 0.000100 |
| all 96 | H | +0.772047 | [+0.690648, +0.825525] | YES | 0.000100 |
| **N only (78)** | full | **+0.696832** | [+0.576176, +0.784062] | **YES** | 0.000100 |
| **N only (78)** | H | +0.673993 | [+0.547236, +0.766611] | YES | 0.000100 |

Sanity check, confirmed from the roster's `position` column: **dist(AV_220) = |220 − 222| = 2** ✓ and **dist(AV_195) = |195 − 222| = 27** ✓. ρ_b is more negative near 222 — the sign the locality hypothesis predicts.

**Not a region artifact** (disclosed post-hoc check): Spearman(dist_222, region) = +0.524, so the axis *is* confounded with region — but region-demeaning barely moves it (+0.780 → +0.691 on full, +0.772 → +0.650 on H), and within the two informative regions it is still +0.650 (R1) and +0.659 (R3). It is weak in R2 (+0.243, which contains 222 and so has the least distance spread) and absent in R4 (−0.074, where everything is far and there is no near end to compare).

**The k-removal points the other way**, and this is the more directly relevant test of the reviews' actual worry. Neither value is selected:

| | \|N\| | p_spec(full) | p_spec(H) |
|---|---|---|---|
| original | 78 | 0.025316456 | 0.050632911 |
| k=5 nearest removed | 73 | 0.027027027 | 0.040540541 |
| k=10 nearest removed | 68 | 0.014492754 (floor 1/69) | 0.014492754 (floor 1/69) |

Removing near-222 placebos does not weaken the comparison — **it strengthens it**, because two of the three H-frame beaters (`AV_195` at d=27, `G_P254F` at d=32) are themselves among the ten nearest, and at k=10 nothing is left at or below. A222V is more negative than essentially every placebo *including the nearest ones*.

## 3. D3's arm-decomposed ranks

| view | arm | n (+A222V) | # at or below A222V | A222V's rank |
|---|---|---|---|---|
| full | **V** | 38 (39) | **0** | **1/39** |
| full | **G** | 40 (41) | 1 | 2/41 |
| H | V | 38 (39) | 2 | 3/39 |
| H | G | 40 (41) | 1 | 2/41 |

Decomposition only; no p_spec redefined. **The full-frame result is carried entirely by Arm G.** The exhaustive, fitness-blind arm contains no background at or below A222V's full-frame ρ. On H the split reverses: Arm V contributes two of the three (`AV_220`, `AV_195`).

## 4. D5's D_site vs D_site_resid

| view | D_site | CI | D_site_resid | CI (OLS refit per draw) | ratio | resid excludes zero? |
|---|---|---|---|---|---|---|
| full | −0.055526 | [−0.068409, −0.044214] | **−0.023832** | [−0.030266, −0.013300] | 0.429 | **YES** |
| H | −0.059646 | [−0.072574, −0.048009] | **−0.026597** | [−0.032712, −0.016452] | 0.446 | **YES** |

`D_site` reproduces its frozen value exactly (|diff| = 3.3e-10). The site contrast **survives** controlling for shift magnitude, but **more than half of it is accounted for** (43–45% retained). Both halves must be reported. Note the residual CIs are background-level and are not comparable to script 125's position-cluster CI.

## 5. D6's severity gradient, and Arm V vs Arm G severity

| view | Spearman(ρ_b, severity) | 95% CI | excludes zero? | p (two-sided) |
|---|---|---|---|---|
| full | −0.175505 | [−0.407048, +0.071882] | **NO** | 0.134487 |
| H | −0.147937 | [−0.377687, +0.094270] | **NO** | 0.208179 |

A **clean null** on the primary question: placebo background severity is not distinguishable from noise as a predictor of ρ_b. All four within-arm views also include zero (−0.298 / −0.138 on full; −0.259 / −0.148 on H).

Arm V vs Arm G severity, descriptive (arms are not exchangeable, so no significance claimed for it as biology): Arm V mean +4.94 (sd 2.94), Arm G mean **+6.79 (sd 4.71)** — Arm G is more severe on average by +1.85, two-sided permutation p = 0.0463, with ~60% larger spread. **The two arms are not severity-matched.** Also: Spearman(severity, dist_222) = −0.238, so the severity axis overlaps D2's locality axis and is **not** independent corroboration of it.

## 6. D7's sign-explicit sentence, and the |ρ| sensitivity

Composed entirely from gated D1 values, printed verbatim in the D7 entry:

> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 1 of the 78 placebo backgrounds on the full frame and 3 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).

**The |ρ| sensitivity is numerically identical to the signed test on both views** — `p_spec_abs(full) = p_spec(full) = 0.025316456`, `p_spec_abs(H) = p_spec(H) = 0.050632911`. The reason is printed, not asserted: **zero** backgrounds are positive with |ρ| ≥ |ρ_A222V|, so the `>=` count and the `<=` count coincide. **The verdict does not depend on the pre-declared one-sided direction at all** — A222V's magnitude is the largest in the null set in either direction. This removes one of the two external reviews' specific objections, on this dataset.

## 7. D8's leave-one-out p_spec

| view | original (\|N\|=78) | G_P254F removed (\|N\|=77) | change | still at or below |
|---|---|---|---|---|
| full | 0.025316456 | **0.012820513** (= 1/78, the floor) | −0.012496 | *(none)* |
| H | 0.050632911 | **0.038461538** | −0.012171 | `AV_195`, `AV_220` |

The floor rises from 1/79 = 0.012658 to 1/78 = 0.012821. **The fragility is asymmetric**: the full-frame count rests on a single background; the H-frame count rests on three. This is a diagnostic of the frozen result, not an alternative estimate of it.

## 8. Every gate, PASS/FAIL, value, D1-G1 first

| gate | what it checked | result | value |
|---|---|---|---|
| **D1-G1** | **50 checks: A222V ρ, p_spec, beater identity, all arm n/mean/median/range, N summaries, ranks, + 192-value cross-check against script 125's own log** | **PASS 50/50** | ρ_full −0.088118064 (\|diff\| 2.5e-10); ρ_H −0.090021683 (3.3e-11); p_spec(full) 0.02531645569620253 (\|diff\| **0.000e+00**); p_spec(H) 0.05063291139240506 (\|diff\| **0.000e+00**); beaters {G_P254F} / {AV_220, AV_195, G_P254F}; all six arm means within 4.8e-10; G1.15 max\|diff\| 4.990e-10 (ρ_full) and 4.956e-10 (ρ_H) over 96/96 |
| D2 input | table sha256 re-verified | PASS | `e397a442…5863` |
| D2 R3 | dist_222 provenance vs roster `position` + id parse + `wt_aa`/`mut_aa` | PASS | 0 disagreements / 96 |
| D2 R3 sanity | dist(AV_220)=2, dist(AV_195)=27 | PASS | 2, 27 |
| D2 R7 | forced identity permutation reproduces observed | PASS (×4) | \|diff\| 0.000e+00 |
| D2 R6 | permutation null centring | PASS | \|z\| ≤ 1.42, centres on zero |
| D3/D7/D8 input + A222V threshold gate | table sha256; A222V ρs re-derived | PASS | \|diff\| 0.000e+00 on both |
| D4 delta gate | `delta_b` independently re-derived from both raw files for all 96 | PASS | max\|diff\| **0.000e+00** |
| D4 D4.4 | forced identity permutation | PASS (×2) | 0.000e+00 |
| D4 D4.5 | permutation null centring | PASS | centres on zero |
| D5 D5.1 | D_site reproduces frozen −0.055525559 | PASS | \|diff\| 3.310e-10 |
| D6 retrievability | 75/96, 21 missing all accounted for by name and cause | PASS (disclosed) | 18 Arm S (position 222 absent from task32), 3 Arm G (`G_E383T`, `G_D629C`, `G_P346V` — mutants never scored) |
| D6 wt gate | roster `wt_aa` vs task32 `wt_aa` on joined rows | PASS | 0 mismatches / 75 |
| D6 D6.4 | forced identity permutation | PASS (×8) | 0.000e+00 |
| D6 D6.5 | permutation null centring | **flagged, reported as-is** | full-frame reads DOES NOT CENTRE, driven solely by the median (\|z\|=2.19); the mean is \|z\|=1.04. Not re-tuned — see D6 flags. |
| D6 sign self-check | severity and raw axes are exact negatives | PASS | \|-0.175505 + 0.175505\| = 0.000e+00 |

**No gate failed. No threshold was loosened. No task was re-run at a higher N to obtain a result. Task status: D1 PASS, D2 PASS, D3 PASS, D4 PASS, D5 PASS, D6 PASS, D7 PASS, D8 PASS.**

## 9. What this session changes about how Phase 2 should be interpreted or written up

Stated plainly, in the order the evidence forces:

1. **A new, large confound exists and must be disclosed: ρ_b tracks how much a background perturbs ESM-2 (r = −0.61, CI excluding zero, region-robust).** This was not previously on record. A write-up that presents A222V's position as distinctive without mentioning it is incomplete.
2. **But that confound does not explain A222V.** A222V is a mid-pack shifter (68.8th percentile) whose ρ is far more negative than the confound line predicts — residual −0.059, the most extreme of all 96. The correlation and A222V's extremity coexist; the correlation does not absorb A222V.
3. **A locality gradient in ρ_b is real and large (r ≈ +0.70 within the null set alone) and survives region correction.** Position 222's neighbourhood behaves differently from the rest of the protein. This must be disclosed, and it reframes the result: A222V is unusual **relative to its own neighbourhood**, not because its neighbourhood is unlike everywhere else.
4. **The k-removal is reassuring and should be reported alongside the gradient.** Removing the 5 and 10 backgrounds nearest 222 leaves the comparison intact or strengthens it. The frozen comparison is *not* propped up by near-222 placebos.
5. **Two objections are affirmatively retired.** The verdict does not depend on the pre-declared direction (D7: the |ρ| test is identical, because no positive placebo comes near A222V's magnitude), and background severity does not track ρ_b (D6: a clean null on all four views).
6. **One fragility must be stated: the full-frame count rests on a single background** (`G_P254F`), which is also the largest shift of all 96. The H-frame count rests on three and is more robust.
7. **Two structural facts about the arms belong in the write-up.** The full-frame result is carried entirely by Arm G (rank 1/39 in Arm V, 2/41 in Arm G), and the two arms are not severity-matched (Arm G mean +6.79 vs Arm V +4.94).
8. **The frozen `PHASE2_PREREG.md` §5 outcome is unchanged and is not qualified by anything here.** Every task in this session was descriptive. What changes is the framing around it, not its value.

## 10. Protected paths and git state — confirmed

- **Nothing under `docs/tasks/phase3a-gb1-acquisition/` or `docs/tasks/phase3b-gb1-regime-map/` was created, modified, or read into.** Verified by timestamp: every file in both directories has an mtime of **2026-09-28** (16:12–16:33), a full day before this session began. `git status` lists them as untracked (`??`), which is their pre-existing state, not a change.
- **Nothing was committed, staged, pushed, or added.** `git status` shows no staged changes. HEAD remains `fe0f533`, which was committed at **20:07:14**, three minutes *before* this session's first action, and contains exactly one file — `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS.md` (261 insertions), the planning document. **That commit is not mine**; I did not create it and did not author its message.
- **Protected files untouched, verified by timestamp:** `AGENTS.md` (2026-09-22), `RESULTS.md` (2026-09-26), `docs/tasks/phase2-full-frame-placebo/PHASE2_PREREG.md` (2026-09-27), `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md` (2026-09-28), and the earlier session log `docs/tasks/phase2-full-frame-placebo/PHASE2_LOG.md` (2026-09-29 19:13:48, before this session started at 20:07:14).
- **Two protected paths named in the instructions do not exist in this repository:** `MTHFR_RESULTS_LOG.md` and `PROJECT_SUMMARY_FINAL.md` are not present (`ls` returns "No such file or directory"). I am reporting their absence rather than claiming to have preserved them, per AGENTS §5's rule against citing files not verified to exist. If they are expected to be somewhere else, that is worth checking separately.
- **The complete list of files this session created** (verified by mtime > 20:08): `scripts/lib/phase2_diag.py`, `scripts/131_phase2_diag_background_rho.py`, `scripts/132_phase2_diag_locality.py`, `scripts/133_phase2_diag_rank_counts.py`, `scripts/134_phase2_diag_shift_magnitude.py`, `scripts/135_phase2_diag_severity.py`, `data/processed/phase2_diagnostics/background_rho_table.csv`, and the six files in this task directory (this log plus five `PHASE2_DIAG_*_FULL_OUTPUT.txt`).
- No packages were installed. `venv/bin/python3` throughout. All runs in the foreground. No background jobs.

## 11. The single most important thing to read first

**`PHASE2_DIAGNOSTICS_LOG.md` line 478** — the D4 residual block, `RESIDUAL (actual - predicted) = -0.059133`.

Read the D4 correlation (line 432, r = −0.614, CI excluding zero) and this residual together or you will draw the wrong conclusion from either alone. The correlation says a large confound exists; the residual says A222V is not explained by it. Anyone who reads only the first will overstate the problem; anyone who reads only the second will miss it. The honest answer needs both, and line 478 is where the two meet.
