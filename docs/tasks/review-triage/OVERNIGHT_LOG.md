# Overnight Log — Review Triage Execution

Run date: 2026-09-21 (overnight, autonomous).
Execution order follows REVIEW_TRIAGE.md "Suggested execution order".
Skip list (per user): I2, I3, G2, K2 — log as SKIPPED, do not attempt.

## S1 — Own vs published e.b: possible column duplication bug
Status: PASS (no code bug; but a reporting discrepancy found in the log — flagged, not edited)
Time started / finished: 2026-09-21 22:35 / 2026-09-21 22:42
What I did:
1. Read scripts/32_delta_esm_primary.py and scripts/33_delta_esm_signflip_null.py to see which columns each PAIRS entry reads.
2. Compared `GI_folinate_independent` (published e.b) vs `own_e_b` row-by-row on the merged analysis set.
3. Verified provenance of both columns against the raw atlas file (`data/raw/mthfrModel/results/folate_response_model5.csv`).
4. Reproduced the correlations the log reports (5.2) with row-level Spearman on n=10,757.
5. Checked mid-range disagreement claim (log §7).
Actual output (real numbers, not a paraphrase):
- phase5_analysis_table has 11,344 rows; merged with own_context_metrics: 10,757 rows have both columns non-null.
- Identical rows: 0 of 10,757. max |published − own| = 0.8373417839573668.
- Spearman(published, own) = 0.975227810760996; Pearson = 0.9808443000750426.
- published e.b sd = 0.2553820644772617; own e_b sd = 0.24090735229710575.
- Provenance: published `GI_folinate_independent` == raw file's `e.b` column exactly (max|diff| = 0.0). `own_e_b` == independent re-derivation from raw per-concentration residuals via rebuild_interaction_fit + wls_line (max|diff| = 2.220446049250313e-16). They are two genuinely different computations.
- Reproduced correlations (row-level Spearman, n=10,757):
    delta_ESM vs published e.b: rho = -0.070705
    delta_ESM vs own e_b     : rho = -0.088118
    difference: +0.017413 — they do NOT agree to 3 decimals.
- Saved script-32 output on disk (task32_delta_esm_primary.csv) agrees: "signed, published e.b" = -0.07070516222228716 (CI [-0.09797, -0.04384]); "signed, own e_b" = -0.08811806424891734 (CI [-0.11733, -0.05951]).
- Script 33's null observed = -0.08811806424891734 — exactly the OWN e_b value; its docstring/last line states "P-values apply to own_e_b."
- Mid-range disagreement (log §7 claim): mean |published − own| = 0.02909604173869448 in the mid band (avg e.b in [-0.2, 0.2], n=7,468) vs 0.033880712960664 overall — disagreement is real, confirming the columns are not duplicates.
Verdict:
- NO column-duplication bug in scripts 32/33. The code reads two distinct, independently derived columns.
- DISCREPANCY FOUND (reporting, not code): MTHFR_RESULTS_LOG.md line 173-174 (§5.2) states "ρ = -0.088 (published e.b) and -0.088 (own e.b)". Script 32's actual saved output for published e.b is -0.0707, not -0.088. The log appears to have transcribed the own-e.b value under both labels. Both are still negative (direction of 5.2's conclusion unchanged), but the published-e.b magnitude is 19% smaller than claimed. REVIEW_TRIAGE.md's premise ("script 32 reported identical correlations to three decimals") reflects the log's numbers, not script 32's actual output. Per protocol I did NOT edit MTHFR_RESULTS_LOG.md; flagged here.
- Qualitative agreement with log §7 (own/published genuinely disagree) CONFIRMED.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry only). No scripts or results touched.
Anything unexpected or worth flagging:
- scripts/32_delta_esm_primary.py and 33 have NO git history (`git log -- scripts/32_delta_esm_primary.py` is empty) — they appear untracked/uncommitted. Not investigated further.
- The -0.088 (published) figure in the log is not reproducible from current data under any obvious computation; the only -0.088 on disk belongs to own_e_b.
- Because both signed correlations are negative and similar, S1 does NOT trigger the "confirmed bug / flipped sign" branch: Groups B/C remain runnable pending S2.
---

## A1a — Audit: which scripts' CIs/nulls are position-level vs row/cell-level
Status: PASS (audit completed; one real convention violation found — sign-flip nulls are cell-level)
Time started / finished: 2026-09-21 22:44 / 2026-09-21 22:45
What I did:
Grepped every scripts/*.py for its CI/resampling mechanism; read the sign-flip call sites; loaded the interaction-fit residual matrix to establish the exact granularity of the flips.
Actual output (real numbers, not a paraphrase):
- Residual matrix shape: resid = (13134, 4), M_se = (13134, 4) → every `rng.choice([-1,1], size=Rs.shape)` flips AT (variant × condition) CELL granularity — FINER than variant-level, not position-level.
- Cell-level sign flips found in: scripts/21 line 138, scripts/24 line 140, scripts/26 line 135, scripts/28 line 172, scripts/33 line 100. → the sign-flip re-derivation p-values across the project are all sub-variant granularity, violating AGENTS.md §4 ("any permutation or null must also be at position level").
- Script 33's NULL 2 IS position-block, but it is the weaker association null, correctly labeled in the script.
- Script 20: NULL1 re-derivation within-variant (for e.r), NULL2 position-block association; script labels the association one as such. OK.
- Position-cluster CI scripts (house convention respected): 13, 15, 16, 19, 23, 24, 28, 32, 33_measurement_noise_control, 36_two_trait_diagnostic (all via scripts.lib.stats.position_cluster_bootstrap); 29, 30, 34_additive_null, 34_established, 36_matched_baseline, 38 (custom position-resampled bootstraps, verified in code); 18, 24, 28 (cluster-robust SEs by position in statsmodels OLS).
- Row-level item found: scripts/26 line 85 `fake = rng.permutation(df["target"].to_numpy())` — a ROW-level target shuffle for a null_r2 (flagged; not one of the headline CIs but non-conforming).
- scripts/35: no resampling at all (analytic SEs + pass rates); scripts/39: explicitly labeled diagnostic, not inference.
Verdict: All headline CIs are position-clustered as claimed. The gap is exactly what A1 flagged: script 33's sign-flip null is per-(variant, condition), i.e. too narrow. A1b reruns it at position-block granularity.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). No scripts modified.
Anything unexpected or worth flagging:
- The violation is WORSE than the review guessed: not variant-level but (variant × condition) cell-level.
- scripts/26's row-level target permutation is a second, smaller convention violation worth fixing later (not on tonight's critical path).
---

## A1b — Rerun script 33's sign-flip null at position-block granularity
Status: PASS — sanity checks pass at all three granularities; the headline signed result SURVIVES position-block flips
Time started / finished: 2026-09-21 22:45 / 2026-09-21 22:46
What I did:
Wrote scripts/42_position_block_signflip.py (next free number; conventions: venv shebang-less entry with sys.path insert matching sibling scripts, WHY docstring, pre-registered decision rule in docstring, N_PERM from env, identity checks with sys.exit(1), output to data/processed/). Smoke-tested at N_PERM=200 (2.4 s → extrapolated ~100 s full, well under 10 min), then ran full N_PERM=10000 in the foreground (49.96 s total). Three nulls at identical N and seed: cell (script 33's), variant, position.
Actual output (real numbers, not a paraphrase):
```
Analysis set: 10757 variants, 654 positions
SANITY CHECKS (test the test before trusting it) -- AGENTS.md §4
  cell      all+1 == own_e_b       max|diff| = 2.220e-16
  cell      all-1 == -own_e_b      max|diff| = 2.220e-16
  variant   all+1 == own_e_b       max|diff| = 2.220e-16
  variant   all-1 == -own_e_b      max|diff| = 2.220e-16
  position  all+1 == own_e_b       max|diff| = 2.220e-16
  position  all-1 == -own_e_b      max|diff| = 2.220e-16
  all checks passed.
SIGN-FLIP RE-DERIVATION NULL AT THREE GRANULARITIES (10000 draws each)
  [cell (script 33's null)]
    observed=-0.0881  null mean=+0.0001 sd=0.0094  p=<0.0001
    excess over null=-0.0882  (-0.1% of the raw value is structural artifact)
    null-centring check: mean IS consistent with zero (3 SE) -> SURVIVES at p<0.05
  [variant]
    observed=-0.0881  null mean=+0.0001 sd=0.0094  p=<0.0001
    excess over null=-0.0882  (-0.1% ...) -> SURVIVES at p<0.05
  [position (house convention)]
    observed=-0.0881  null mean=-0.0001 sd=0.0156  p=<0.0001
    excess over null=-0.0881  (0.1% of the raw value is structural artifact)
    null-centring check: mean IS consistent with zero (3 SE) -> SURVIVES at p<0.05
```
- CSV (task42_position_block_null.csv): cell null_sd=0.009363847009825512 p=0.0; variant null_sd=0.009396789400773665 p=0.0; position null_sd=0.015605782151827563 p=0.0; all n_perm=10000, all null_centred=True.
- On-disk script-33 reference reproduced: null mean=+0.000067 sd=0.009364 p=0.0 — my cell-level row matches to 4 decimals, validating implementation equivalence.
- Effect of granularity: position-level null sd is 0.0156 vs 0.0094 cell-level (1.66× wider, as expected from 654 independent units instead of 10,757×4), but observed −0.0881 still gives p<0.0001 and ~0.1% artifact.
Verdict: Per the pre-registered rule in the script's docstring, log 5.3's signed-null significance SURVIVES position-block granularity: null centred, p<0.0001, artifact ≈0%. The reviewer's worry (too-narrow null) was legitimate in construction but does not overturn the result.
Files created/modified: scripts/42_position_block_signflip.py (new), data/processed/task42_position_block_null.csv (new). Nothing existing was modified.
Anything unexpected or worth flagging:
- Variant-level and cell-level nulls are nearly identical (sd 0.00940 vs 0.00936); the jump comes only at position level (0.0156).
- This remains a sign-flip null: it rules out the e.b-construction artifact only, NOT confounding (AGENTS.md §4 caveat; ties to B1).
---

## A1c — Confirm script 34's CIs resample positions, not variants
Status: PASS
Time started / finished: 2026-09-21 22:46 / 2026-09-21 22:47
What I did:
Read scripts/34_additive_null_phenotype_space.py CI call sites (lines 141-185) and the bootstrap function it uses (scripts/lib/stats_ext.py paired_metric_difference_bootstrap, lines 102-131); checked the saved CSV.
Actual output (real numbers, not a paraphrase):
- Pooled 6.2 calls: `paired_metric_difference_bootstrap(d, "position", a, b, "target", metric="mae", ...)` — cluster_col="position"; function resamples `drawn = rng.choice(clusters, size=len(clusters), replace=True)` then concatenates whole-cluster row indices → positions, not variants.
- Stratified 6.3 calls: same function with `sub, "position"` (line 173).
- Script output already states it explicitly: `PAIRED DIFFERENCES, cluster-bootstrapped by position (N_BOOT draws)`.
- Saved CSV confirms: pooled rows carry n_clusters=654 (e.g. ESM-2(A222V) vs ESM-2(WT): diff=+0.0005334660988103312, CI=[+0.00028835365805139276, +0.0007675630167030905], n=11113, n_clusters=654).
Verdict: 6.2/6.3 CIs are position-cluster bootstrapped as the house convention requires. No change needed.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 34 NOT modified (its output already states the method).
Anything unexpected or worth flagging:
- Minor cosmetic gap: stratified (6.3) rows in task34_additive_null.csv omit n_clusters, and the stratified section header doesn't restate the cluster method (the preceding header does). Purely an output-recording gap; the resampling itself is by position. Not worth touching a results-producing script for.
---

## A2a — Where did the stratum rows go? (3,586 vs expected ~3,704) + skew check
Status: PASS — fully explained, and the exclusions ARE systematically skewed (not a rounding artifact)
Time started / finished: 2026-09-21 22:47 / 2026-09-21 22:49
What I did:
Reproduced script 34's stratification exactly (pd.qcut on |GI_folinate_independent| of its dropna set); traced every row from phase5 (11,344) to the stratified set (10,757); compared dropped vs kept rows on fitness, region, missing-condition pattern, and delta_ESM.
Actual output (real numbers, not a paraphrase):
- Reproduction: qcut(|e.b|, 3) on the dropna(abs_gi) set gives {'low': 3586, 'high': 3586, 'mid': 3585} — exactly matching the saved task34_additive_null.csv rows (gi_low n=3586, gi_mid n=3585, gi_high n=3586). Sum = 10,757, NOT 11,113.
- Root cause: script 34's strata are terciles of 10,757 (rows with published e.b), while its pooled 6.2 result runs on 11,113. 11,113 − 10,757 = 356 rows have no e.b and never enter stratification. 3,586 ≈ (11,113 − 356)/3; the reviewer's 3,704 expectation = 11,113/3. Arithmetic closes: 3704 − 3586 = 118 ≈ 356/3.
- Skew of the 356 dropped-before-stratification rows (vs the 10,757 kept):
    mean base_functionality: 0.6312 dropped vs 0.7377 kept (−0.107)
    mean f_bar_wt: 0.6132 dropped vs 0.7547 kept (−0.141)
    region %: dropped {1: 12.6, 2: 23.9, 3: 42.4, 4: 21.1} vs kept {1: 24.0, 2: 22.5, 3: 25.2, 4: 28.3} → region 3 overrepresented +17pp, region 1 halved
    missing A222V-arm conditions among dropped: {0: 85, 1: 13, 2: 18, 3: 240} → 240/356 are missing 3 of 4 m-conditions (the atlas's fitModels.R returns e.b=NA when >2 m-points missing)
    mean delta_esm: +0.03316 dropped vs +0.03282 kept (essentially identical — the ESM-side variable is NOT skewed)
    frac base_functionality<0.2: 0.191 dropped vs 0.206 kept (similar lower tail; the shift is in the mean/mid-range)
- Rule check for why e.b is missing: 471/587 e.b-NA rows are explained by (≥3 m-conditions missing OR no WT-arm data) — the fitModels.R NA rule; 116/587 are NOT explained by that simple rule (likely atlas optim/second-round-fit failures; not investigated further tonight).
Verdict: The missing ~118-per-stratum rows are rows the ATLAS could not fit e.b for (A222V-arm data sparsity), and the exclusion is systematically skewed toward LOWER fitness and region 3 (42.4% vs 25.2%). Not a rounding artifact. Since strata define the 6.3 headline test, its stratified set is a systematically different population than the pooled 6.2 set — worth stating in the writeup. delta_ESM itself is not skewed, so the skew acts through e.b-observability, not through the predictor.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). No data/scripts touched.
Anything unexpected or worth flagging:
- 6.2 (pooled, n=11,113) and 6.3 (stratified, n=10,757) run on DIFFERENT row sets — the log does not currently say this.
- 116 of 587 e.b-missing rows are unexplained by the documented NA rule; flagged, not chased.
---

## A2b — Reconcile n across scripts (10,757 / 11,113 / 11,344 / 11,902 / 13,134)
Status: PASS — every published n is reproduced by a specific, explicit filter; no bug found
Time started / finished: 2026-09-21 22:48 / 2026-09-21 22:50
What I did:
Counted rows at every stage of the pipeline (raw atlas → ESM join → phase3 → phase5 → each script's analysis set) and read each script's dropna chain to attribute every step.
Actual output (real numbers, not a paraphrase):
| Stage | n | Filter that gets you there (verified in code) |
|---|---|---|
| raw folate_response_model5.csv | 13,134 | all variant types (substitutions, synonymous, nonsense) |
| type == "substitution" | 11,902 | load_derived_maps(missense_only=True) |
| phase3_analysis_table (script 15) | 11,901 | inner join with esm2_wt_scores.csv — exactly 1 substitution has no ESM WT score |
| phase5_analysis_table (script 16 line 55) | 11,344 | dropna(model_A, model_B, model_C, target): −557 rows all have f_bar_a222v NaN (= zero A222V-arm measurements; 18 of them additionally lack esm2_score_a222v_bg) |
| script 16 model comparison (phase5_model_comparison.csv) | 11,344 | same filter; n_rows column confirms |
| script 32 analysis set / locality rows | 11,344 | dropna(delta_esm) only — task32_analysis_table has 11,344 rows |
| script 34/36 analysis set | 11,113 | + dropna(f_bar_wt): −231 rows have ALL FOUR WT-arm conditions missing (verified: 231/231 have w-cond missing count = 4; all 231 also lack e.b). Reproduced: phase5.dropna(model_A, model_C, target, f_bar_wt) → 11,113 |
| scripts 32-pairs / 33 / 35 / 6.3 strata | 10,757 | + require published e.b AND own_e_b: −356 of the 11,113 (atlas could not fit e.b — see A2a). own_e_b-missing set is IDENTICAL to e.b-missing set (587 = 587 = 587 overlap) |
Cross-checks:
- task34_predictions.csv = 11,113 rows; task36_analysis_table.csv = 11,113; task32_analysis_table.csv = 11,344; task35_summary.csv missense_n = 10,757 — all match their scripts' dropna chains.
- Log citations: 6.2's "11,113" matches scripts 34/36; 5.2/5.3's n=10,757 (implied by CI widths and script 33's print) matches scripts 32-pairs/33; phase5_model_comparison's 11,344 matches script 16. The "inconsistent n" is real but each value is correct FOR ITS SCRIPT's filter.
Verdict: No contradiction, no dropped-row mystery: 13,134 → 11,902 → 11,901 → 11,344 → 11,113 → 10,757, each step attributable. The only substantive caveat is the one A2a quantified: the last step (−356) is fitness/region-skewed, and 6.2 vs 6.3 use different sets.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- CONTRADICTION-vs-log note (troubleshooting #5): no contradiction of a headline number, but the log presents 6.2 and 6.3 as one analysis while they differ by 356 systematically-different rows. Logged both n's; MTHFR_RESULTS_LOG.md NOT edited.
- 1 substitution (of 11,902) has no ESM score — negligible but recorded here for completeness.
---

## B1a — Partial correlation of delta_ESM vs e.b controlling S(v|WT) + w.fitness (spline)
Status: PASS — does NOT collapse; the flattening confound does not explain the correlation
Time started / finished: 2026-09-21 22:50 / 2026-09-21 22:55
What I did:
Wrote scripts/43_flattening_partial.py (B1a + B1b sections; pre-registered collapse criterion in docstring: |partial| < 50% of |raw| = COLLAPSE). Nuisance model = natural cubic spline df=4 per covariate on ranks, refit inside every bootstrap draw, positions resampled (n=10,757, 654 positions). Fixed a p-value bug before the full run (initial smoke used |boot|>=|obs| against the CI distribution, which is meaningless for a bootstrap; replaced with the house convention from stats._summarize, p = 2·min(frac≤0, frac≥0)). Smoke at N_BOOT=200 (5.5 s), full run at N_BOOT=10000 (3:55.82 total, under the 10-min budget).
Actual output (real numbers, not a paraphrase):
```
Raw correlations:
  rho(delta, own_e_b)             = -0.0881
  rho(delta, GI_folinate_independent) = -0.0707
  rho(delta, esm2_score)          = -0.3238   rho(own_e_b, esm2_score)  = +0.0854   rho(pub_e_b, esm2_score) = +0.0699
  rho(delta, base_functionality)  = -0.1877   rho(own_e_b, base_func)   = -0.1471   rho(pub_e_b, base_func)  = -0.2393
  rho(delta, f_bar_wt)            = -0.1886   rho(own_e_b, f_bar_wt)    = -0.1604   rho(pub_e_b, f_bar_wt)   = -0.2513

own_e_b | ctrl esm2_score+base_functionality
  raw rho=-0.0881  partial rho=-0.0828 CI=[-0.1158,-0.0502] p_boot=<0.0001
  |partial|/|raw| = 0.940  -> does NOT collapse (>=50% of raw)
own_e_b | ctrl esm2_score+f_bar_wt
  raw rho=-0.0881  partial rho=-0.0853 CI=[-0.1185,-0.0525] p_boot=<0.0001
  |partial|/|raw| = 0.968  -> does NOT collapse
GI_folinate_independent | ctrl esm2_score+base_functionality
  raw rho=-0.0707  partial rho=-0.0786 CI=[-0.1114,-0.0459] p_boot=<0.0001
  |partial|/|raw| = 1.111  -> does NOT collapse (partial is LARGER than raw)
GI_folinate_independent | ctrl esm2_score+f_bar_wt
  raw rho=-0.0707  partial rho=-0.0803 CI=[-0.1128,-0.0480] p_boot=<0.0001
  |partial|/|raw| = 1.136  -> does NOT collapse
```
- n=10,757, positions=654 in every configuration; boot mean equals observed in all four (healthy bootstrap).
Verdict: Pre-registered criterion NOT met — the partial correlation retains 94-114% of the raw value under nonlinear control of both S(v|WT) and either w.fitness measure. The review's worry ("the story is really both tracking deleteriousness independently") is NOT supported by this test. The negative direction survives controlling for deleteriousness.
Files created/modified: scripts/43_flattening_partial.py (new), data/processed/task43_flattening.csv (new).
Anything unexpected or worth flagging:
- For published e.b the partial is LARGER than raw (ratio 1.11-1.14) — the covariates were masking a bit of the effect, not creating it.
- Part-whole caveat applies (w.fitness sits inside e.b's expectation) — makes NON-collapse the more meaningful direction, which is what we got. Stated in script docstring and output.
- e.b correlates POSITIVELY with S(v|WT) (+0.085): fitter-per-ESM variants have slightly larger e.b; the indirect path through S would induce only ~−0.03 of the −0.088 — consistent with the partial barely moving.
---

## B1b — Compression test: is delta_ESM ≈ −k·S(v|WT)?
Status: PASS (test run; answer: a real monotone relation exists but the compression form explains little variance — it is not the whole story)
Time started / finished: 2026-09-21 22:50 / 2026-09-21 22:55
What I did:
Section B1b of scripts/43_flattening_partial.py: position-cluster bootstrap Spearman of delta_ESM vs S(v|WT); OLS both with and without intercept (the pure compression form predicts a line through the origin); decile means as the requested plot in text form. Same run as B1a.
Actual output (real numbers, not a paraphrase):
```
Spearman(delta_ESM, S(v|WT)): rho=-0.3238 CI=[-0.3653,-0.2803] p=<0.0001 n=10757
OLS delta = -0.01820 + -0.00698 * S   R^2=0.0645
through-origin delta = -0.00514 * S      R^2=0.0584
slope -0.00698 -> k = 0.00698; intercept -0.01820
Decile means (S(v|WT) -> mean delta_ESM):
  d0 n=1076 mean_S=-13.95592 mean_delta=+0.08477
  d1 n=1076 mean_S=-11.99550 mean_delta=+0.05683
  d2 n=1075 mean_S=-10.69969 mean_delta=+0.05798
  d3 n=1076 mean_S= -9.54643 mean_delta=+0.05089
  d4 n=1076 mean_S= -8.36732 mean_delta=+0.03818
  d5 n=1075 mean_S= -7.04192 mean_delta=+0.03235
  d6 n=1076 mean_S= -5.58283 mean_delta=+0.02365
  d7 n=1075 mean_S= -3.94635 mean_delta=+0.00546
  d8 n=1076 mean_S= -2.17669 mean_delta=-0.01061
  d9 n=1076 mean_S= +0.26069 mean_delta=-0.01131
```
Verdict: delta_ESM IS monotonically related to S(v|WT) (rho=−0.324, CI excludes zero, deciles essentially monotone from +0.085 to −0.011) — consistent with SOME compression-toward-zero structure when V222 is supplied. But the linear compression form fits weakly (R²=0.0645; through-origin R²=0.0584), so delta is NOT well described as −k·S alone. Combined with B1a (partial retains 94-114%), the S-relation does not account for the e.b correlation. B1a/B1b do not kill the finding; B1c (entropy) remains to check whether ANY generic flattening exists at the distribution level.
Files created/modified: same as B1a (task43_flattening.csv rows stage=compression/decile).
Anything unexpected or worth flagging:
- The compression slope k≈0.007 is tiny; the more striking B1b number is the rank correlation −0.32 itself, which is mostly about S(v|WT)'s relation to ANY downstream score difference, not a clean k·S law.
---

## B1c — Per-position entropy of ESM-2's output, WT vs A222V background
Status: PASS (REDUCED-RESOLUTION: 500 of 656 positions — see note)
Time started / finished: 2026-09-21 22:56 / 2026-09-21 23:07
What I did:
Wrote scripts/44_entropy_background.py (pre-registered verdict rule in docstring: generic flattening supported iff mean dH>0 AND position-bootstrap CI excludes 0; entropy primary = 20-AA renormalized, nats; position 222 force-included as identity check since masking it gives identical inputs in both backgrounds). Timed 10 forwards first (0.545 s each on MPS → 1,312 forwards ≈ 11.9 min > 10-min budget; batching tested at 8 and 16 — no speedup, MPS-bound). Per troubleshooting rule 4, ran at N_POS=500 (largest fitting ~10 min): 9:52.59 total. Smoke at N_POS=8 first (identity check passed).
Actual output (real numbers, not a paraphrase):
```
*** REDUCED-RESOLUTION RUN: N_POS=500 of 656 positions ***
IDENTITY CHECK: |dH| at position 222 = 0.000e+00 — passed.
n positions = 500
mean H_WT  = 0.78904 nats   mean H_A222V = 0.79103 nats
mean dH    = +0.001992 nats  CI=[-0.000123,+0.004106]  p_boot=0.0678
effect size: mean dH / mean H_WT = +0.00252 (+0.252%)
fraction of positions with dH > 0: 0.5940
sd of dH across positions: 0.024022
-> flattening NOT supported by this test (CI includes 0 or mean <= 0)
[secondary] full-vocab mean dH = +0.001993 nats
```
- Per-position table saved: data/processed/task44_entropy_bg.csv (500 rows: position, H20_wt, H20_a222v, dH20, Hfull_wt, Hfull_a222v).
Verdict: Per the pre-registered rule, GENERIC FLATTENING IS NOT SUPPORTED: the mean entropy shift is +0.002 nats (+0.25% of mean H_WT) with CI [−0.0001, +0.0041] crossing zero (p=0.0678). Direction is weakly positive (59.4% of positions rise) but fails both the CI and the effect-size bar. This is a NULL RESULT and it is reported as such — B1's flattening confound does not explain delta_ESM's behavior at the distribution level either.
Files created/modified: scripts/44_entropy_background.py (new), data/processed/task44_entropy_bg.csv (new).
Anything unexpected or worth flagging:
- REDUCED-RESOLUTION: 500/656 positions. p=0.0678 is close enough to 0.05 that a full 656-position rerun (N_POS=656, ~11.5-12 min, slightly over the 10-min budget) could plausibly tip either way — rerun at full N before quoting externally. The printed output says this too.
- Full-vocab and 20-AA entropies give essentially identical dH (+0.001992 vs +0.001993) — choice of entropy definition is immaterial here.
- Identity check was exact (0.000e+00), so plumbing is sound; the null is a result, not a bug.
---

## B2 — Redo the null at the right granularity (the "~0% artifact" threat)
Status: PASS — executed as A1a/A1b (B2a says "already covered by A1a/A1b"; logged here for visibility per the review's request)
Time started / finished: 2026-09-21 22:45 / 2026-09-21 22:46 (same runs as A1b)
What I did: See A1a (granularity audit: script 33's null was per-(variant×condition), finer than variant) and A1b (position-block rerun, scripts/42_position_block_signflip.py).
Actual output (real numbers, not a paraphrase): position-level sign-flip re-derivation null, N_PERM=10,000: observed=−0.0881, null mean=−0.0001, null sd=0.0156, p=<0.0001, excess=−0.0881, frac_artifact=0.0005687369964375577 (~0.1%), null centred (3 SE check passed). All identity checks max|diff|=2.220e-16.
Verdict: The "~0% artifact" claim in 5.3 SURVIVES position-block granularity — null sd widens 1.66× (0.0094 → 0.0156) but the observed value is far outside it. The claim was built on too-narrow nulls as-shipped, yet the corrected-granularity result is unchanged to one decimal of a percent. B2 does NOT overturn 5.3.
Files created/modified: scripts/42_position_block_signflip.py, data/processed/task42_position_block_null.csv (same as A1b).
Anything unexpected or worth flagging: none beyond A1b.
---

## B3 — Correct the "~0% artifact" framing regardless of B1's outcome
Status: PARTIAL — corrected wording DRAFTED here; not applied (MTHFR_RESULTS_LOG.md is user-owned and was not touched tonight, per instructions)
Time started / finished: 2026-09-21 23:08 / 2026-09-21 23:10
What I did:
Drafted the replacement language the review requires for log 5.3. It cannot be written into MTHFR_RESULTS_LOG.md tonight (explicit user instruction: do not touch it). The draft below is ready to paste after the user reviews it.
Actual output (real numbers, not a paraphrase) — PROPOSED REPLACEMENT FOR 5.3's closing PARAGRAPH:
> The signed null centres almost exactly on zero (as it should, mechanically, since both delta_ESM and e.b are signed) — this is a calibration check on the test itself, and it passes. **A sign-flip null on a signed variable centers on zero by construction; what it rules out is specifically the e.b-construction artifact — the same failure mode that accounted for 77-82% of every earlier result — and nothing more.** It does not rule out confounding (the B1 partial-correlation tests address that separately and the correlation survives them) and is not, on its own, evidence of real epistasis. **Re-run at position-block granularity per AGENTS.md §3/4 (script 42), the signed result survives unchanged: null sd widens from 0.0094 to 0.0156, p < 0.0001 at 10,000 draws, structural artifact ≈ 0.1%.**
Verdict: The required correction is (a) state the sign-flip null's actual scope — rules out the construction artifact, not confounding, not proof of epistasis — and (b) the position-block rerun now backs the number at the correct granularity. Draft fulfills both; application is blocked by ownership instructions.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry) only.
Anything unexpected or worth flagging: MTHFR_RESULTS_LOG.md 5.3 remains unedited by design; also remember S1's separate discrepancy (5.2's "-0.088 (published)" should be −0.071 — both need the user's edit together).
---

## S2 — Sign convention audit (e.b and delta_ESM, on labeled examples)
Status: PASS — no flipped sign found; both conventions verified as assumed
Time started / finished: 2026-09-21 22:42 / 2026-09-21 22:44
What I did:
1. Read the atlas's own `data/raw/mthfrModel/fitModels.R` to get e.b's definition from source (not assumption).
2. Read scripts/16 (delta_esm = model_C − model_A), scripts/10/15 and scripts/lib/esm_scoring.py for the ESM score convention.
3. Verified delta_esm column identity arithmetically on the analysis table.
4. Verified ESM score direction against measured WT fitness (labeled-direction check).
5. Pulled the most extreme labeled rows: strongly negative e.b ("less functional in A222V") and strongly positive e.b ("rescue") and compared raw condition scores.
6. Recomputed the atlas's own multiplicative expectation for three labeled rows and checked sign(residual) == sign(e.b) each time; then an aggregate check on all atlas-significant rows.
Actual output (real numbers, not a paraphrase):
- fitModels.R source: `pred = b + conc*r + expected(conc)`, where `expected` = multiplicative no-interaction expectation from the WT arm × A222V's own WT fitness; b = e.b. So e.b = fitted offset of MEASURED A222V-background score above expectation. e.b < 0 ⇒ less functional in A222V.
- e.post.b (the atlas's own significance label for this) = logistic(e.logl.static − e.logl.null + prior log-odds) = posterior P(e.b model beats null). Prior probability 0.01, per fitModels.R.
- max |delta_esm − (esm2_score_a222v_bg − esm2_score)| = 2.220446049250313e-16 → delta_ESM = C − A exactly.
- esm2_score = masked-marginal log-odds logP(mut) − logP(WT_aa) (scripts/lib/esm_scoring.py). Direction check: Spearman(esm2_score, mean measured WT fitness) = +0.3313033287692243 (n=10,630) → higher score = better per ESM-2. Therefore delta_ESM < 0 ⇒ "ESM-2 thinks v is WORSE when A222V is in the sequence." Same direction semantics as e.b < 0 (measured worse in A222V).
- Labeled negative rows (raw data):
    p.Leu529Pro: e.b=-1.2225, e.post.b=1.0000; expected m12=+1.0693, observed m12=+0.0142 (residual −1.0551) → sign matches e.b.
    p.Pro627Met: e.b=-1.5051, e.post.b=0.0122; expected m12=+1.3922, observed m12=+0.0000 (residual −1.3922) → sign matches.
    p.Ala145Thr (rescue): e.b=+1.3639, e.post.b=1.0000; expected m12=−0.0111, observed m12=+0.9534 (residual +0.9644) → sign matches.
- Aggregate, atlas-significant rows (e.post.b>0.95): n=934 (e.b<0: 388, e.b>0: 546). Among e.b<0 with m12 present (n=378): 91.8% have observed m12 < expected; among e.b>0 (n=546): 72.7% observed > expected at 12.5 µg/ml. (Not 100% at a single concentration because e.b is a joint fit across all four concentrations via b + conc·r plus per-condition noise.)
- Direction of the headline: mean delta_ESM among e.b < −0.5 (n=300) = +0.019241095647448657; among e.b > +0.5 (n=376) = −0.0011307842142606003. ESM-2 moves OPPOSITE to the measured direction on labeled rows: for variants measured much worse in A222V, ESM-2's delta says slightly better. This matches the negative rho in log 5.2/5.3 — the sign is not flipped.
Verdict: PASS. e.b < 0 ⇔ less functional in A222V (verified in atlas source + real rows). delta_ESM < 0 ⇔ ESM-2 says worse in A222V (verified in scoring code + direction check). The observed negative correlation genuinely means "ESM-2 moves the opposite way," not "ESM-2 moves the right way weakly." S1+S2 both pass → Groups B and C are NOT blocked.
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry only).
Anything unexpected or worth flagging:
- ASSUMPTION (protocol #6): the phrase "the atlas's own 'significantly less functional in A222V' label" does not exist as a text column anywhere in the data (grep for "less functional" matches only REVIEW_TRIAGE.md). Most conservative reading: the atlas's own posterior significance call, e.post.b (P(e.b model beats null)), combined with the sign of e.b. I used e.post.b > 0.95 as "significant" and also showed the3-row extreme examples.
- A222V itself: S(A222V|WT) = −5.2003 (script 16's constant) — ESM-2 considers A222V strongly deleterious on the WT background. Relevant later for H1a.
- esm2_score vs WT fitness Spearman is only +0.33; consistent with script 16's model_A rho ≈ 0.363 vs A222V fitness — direction is what matters here, and it is unambiguous.
---

## C1a — Reconciliation table: predictors × targets × metrics × strata
Status: PASS — table built to spec (the spec's 6 row-predictors + Grantham added as a 7th because C1c needs it; all 3 targets, all 3 metrics, low/mid/high + all)
Time started / finished: 2026-09-21 23:09:45 (scripts/45_c1_reconciliation.py authored, decision rules pre-registered in its docstring) / 2026-09-21 23:10:21 (table written by the N_BOOT=2000 run). N_BOOT=50 smoke ran 23:10:03–23:10:07 (~3.5 s) → extrapolated ~90 s → actual 90 s, under the 10-min budget.
What I did:
1. Pre-registered in the docstring (AGENTS §6): analysis set = phase5 rows with published e.b, own_e_b, delta_esm, both ESM scores, base_functionality, f_bar_a222v, grantham, blosum62 all non-null; expected n=10,757, mismatch printed as a red flag. Strata for the TABLE = pd.qcut |e.b| terciles (identical to script 34 / log 6.3); strata for the GAP TESTS (C1b/C1c) = script 30's quantile digitize — each test mirrors the script it reconciles.
2. rank = Spearman; MAE/MSE evaluated after cross-fit isotonic calibration pred→target, position-held-out 5 folds (house `crossfit_isotonic_by_position`) — because AGENTS §8 says rank alone is structurally blind to no-interaction models, so MAE/MSE must exist alongside it.
3. Matched synthetic = script 30's exact recipe: α·z(w.fitness) + sqrt(1−α²)·N(0,1), bisection-matched to S_A222V's own low-stratum rho, seed 0.
4. One script (45) produces all four C1 subtasks; this entry covers its C1a section only.
Actual output (real numbers, not a paraphrase):
```
Analysis set: 10757 variants, 654 positions (expected 10,757 — mismatch would be a red flag)
Canonical matched alpha (to S_A222V low-stratum rho=+0.5283): 0.5811

C1a  RECONCILIATION TABLE (rank=Spearman; MAE/MSE on cross-fit isotonic)

predictor          target         metric          all          low          mid         high
S_WT               A222V_fitness  rank         0.3684       0.5325       0.3521       0.1726
S_WT               A222V_fitness  mae          0.2177       0.2108       0.1923       0.2500
S_WT               A222V_fitness  mse          0.0700       0.0624       0.0550       0.0926
S_WT               e.b            rank         0.0699       0.0999       0.0403       0.0600
S_WT               e.b            mae          0.1770       0.0350       0.1185       0.3774
S_WT               e.b            mse          0.0652       0.0018       0.0158       0.1780
S_WT               w.fitness      rank         0.3280       0.5228       0.3377       0.0841
S_WT               w.fitness      mae          0.3855       0.3710       0.3471       0.4384
S_WT               w.fitness      mse          0.2277       0.1931       0.1836       0.3063
S_A222V            A222V_fitness  rank         0.3650       0.5283       0.3486       0.1713
S_A222V            A222V_fitness  mae          0.2183       0.2120       0.1927       0.2502
S_A222V            A222V_fitness  mse          0.0703       0.0629       0.0552       0.0926
S_A222V            e.b            rank         0.0692       0.0989       0.0401       0.0591
S_A222V            e.b            mae          0.1770       0.0350       0.1186       0.3775
S_A222V            e.b            mse          0.0652       0.0018       0.0159       0.1781
S_A222V            w.fitness      rank         0.3252       0.5188       0.3344       0.0840
S_A222V            w.fitness      mae          0.3865       0.3729       0.3478       0.4389
S_A222V            w.fitness      mse          0.2285       0.1945       0.1843       0.3067
delta_ESM          A222V_fitness  rank        -0.2397      -0.3155      -0.2340      -0.1038
delta_ESM          A222V_fitness  mae          0.2328       0.2386       0.2056       0.2541
delta_ESM          A222V_fitness  mse          0.0767       0.0766       0.0605       0.0930
delta_ESM          e.b            rank        -0.0707      -0.0980      -0.0533      -0.0787
delta_ESM          e.b            mae          0.1772       0.0364       0.1181       0.3770
delta_ESM          e.b            mse          0.0651       0.0020       0.0159       0.1774
delta_ESM          w.fitness      rank        -0.1877      -0.3013      -0.2046       0.0032
delta_ESM          w.fitness      mae          0.4095       0.4193       0.3714       0.4380
delta_ESM          w.fitness      mse          0.2467       0.2349       0.2023       0.3030
matched_synthetic  A222V_fitness  rank         0.3184       0.5185       0.4336      -0.0329
matched_synthetic  A222V_fitness  mae          0.2254       0.2184       0.1877       0.2701
matched_synthetic  A222V_fitness  mse          0.0734       0.0655       0.0518       0.1030
matched_synthetic  e.b            rank        -0.1435       0.0698      -0.0733      -0.3256
matched_synthetic  e.b            mae          0.1791       0.0554       0.1185       0.3634
matched_synthetic  e.b            mse          0.0627       0.0046       0.0177       0.1658
matched_synthetic  w.fitness      rank         0.5638       0.5552       0.5387       0.5656
matched_synthetic  w.fitness      mae          0.3363       0.3457       0.3151       0.3482
matched_synthetic  w.fitness      mse          0.1724       0.1739       0.1497       0.1934
BLOSUM62           A222V_fitness  rank         0.1603       0.2306       0.1699       0.0550
BLOSUM62           A222V_fitness  mae          0.2390       0.2503       0.2087       0.2580
BLOSUM62           A222V_fitness  mse          0.0794       0.0818       0.0615       0.0949
BLOSUM62           e.b            rank         0.0278       0.0471       0.0330       0.0203
BLOSUM62           e.b            mae          0.1774       0.0355       0.1186       0.3783
BLOSUM62           e.b            mse          0.0652       0.0017       0.0156       0.1783
BLOSUM62           w.fitness      rank         0.1443       0.2352       0.1444       0.0290
BLOSUM62           w.fitness      mae          0.4167       0.4354       0.3774       0.4373
BLOSUM62           w.fitness      mse          0.2519       0.2468       0.2057       0.3031
Grantham           A222V_fitness  rank        -0.1107      -0.1506      -0.1160      -0.0400
Grantham           A222V_fitness  mae          0.2414       0.2540       0.2113       0.2587
Grantham           A222V_fitness  mse          0.0805       0.0841       0.0625       0.0949
Grantham           e.b            rank        -0.0156      -0.0426      -0.0170      -0.0147
Grantham           e.b            mae          0.1776       0.0357       0.1187       0.3784
Grantham           e.b            mse          0.0653       0.0018       0.0157       0.1783
Grantham           w.fitness      rank        -0.1021      -0.1558      -0.1011      -0.0247
Grantham           w.fitness      mae          0.4196       0.4418       0.3805       0.4365
Grantham           w.fitness      mse          0.2544       0.2535       0.2079       0.3018
w.fitness          A222V_fitness  rank         0.5687       0.9056       0.8183      -0.0353
w.fitness          A222V_fitness  mae          0.1762       0.1107       0.1239       0.2939
w.fitness          A222V_fitness  mse          0.0528       0.0179       0.0231       0.1174
w.fitness          e.b            rank        -0.2393       0.1677      -0.1007      -0.5690
w.fitness          e.b            mae          0.1746       0.0766       0.1204       0.3267
w.fitness          e.b            mse          0.0552       0.0084       0.0201       0.1371
w.fitness          w.fitness      rank         1.0000       1.0000       1.0000       1.0000
w.fitness          w.fitness      mae          0.0000       0.0000       0.0000       0.0000
w.fitness          w.fitness      mse          0.0000       0.0000       0.0000       0.0000
Saved table to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task45_c1_table.csv
```
Verdict: PASS. n=10,757 and 654 positions exactly as pre-registered — and 654 is the same position count A1b/A1c logged for this analysis set, so there is no n contradiction between tonight's scripts. The table reconciles log 4.5 vs 6.3 in one view: in the high stratum S_A222V rank = +0.1713 while its matched synthetic is −0.0329 and even w.fitness itself is −0.0353 — the high-stratum ESM rank signal is essentially the only positive entry of its kind in that column, which is exactly the tension C2/C3 must now quantify.
Files created/modified: scripts/45_c1_reconciliation.py, data/processed/task45_c1_table.csv, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 45 is uncommitted (no commits requested tonight); results CSVs are gitignored by design.
Anything unexpected or worth flagging:
- The e.b-target MAE/MSE cells are PARTLY DEFINITIONAL: the strata are terciles of |e.b|, i.e. of that very target (low-stratum MAE 0.0350 vs high 0.3774 is largely constructed by the stratification). The rank cells are unaffected. Do not quote e.b-MAE-across-strata as a finding.
- matched_synthetic vs w.fitness rank = 0.5638 is true by construction (the anchor is z(w.fitness)); only the synthetic's A222V-fitness column carries information.
- REVIEW_TRIAGE's C1a spec lists 6 row-predictors; Grantham is a 7th I added for C1c — a superset of spec, not a deviation from it.
---

## C1b — Does S(v|WT) retain as much high-stratum signal over its matched synthetic as S(v|A222V)?
Status: PASS — executed; verdict = retention is NOT background-specific (the review's suspected answer, confirmed)
Time started / finished: 2026-09-21 23:10:20 / 2026-09-21 23:11:50 (single N_BOOT=2000 run, 90 s wall — same run as C1a/C1c/C1d; scripts/45_c1_reconciliation.py)
What I did:
1. gap = rho_high(pred) − rho_high(its OWN matched synthetic). Each predictor's synthetic has α refit to that predictor's own low-stratum rho against the A222V-fitness target (script 30's recipe); all four predictors are evaluated on the SAME bootstrap draws (paired comparison).
2. Position bootstrap, N_BOOT=2,000 (env var): positions resampled with replacement, strata re-digitized and α refit inside every draw.
3. Pre-registered verdict rule in the docstring (AGENTS §6): CI of gap(S_A222V) − gap(S_WT) including 0 ⇒ "S_WT retains as much as S_A222V" ⇒ 4.5's retention is not about background information.
Actual output (real numbers, not a paraphrase):
```
C1b/C1c  HIGH-STRATUM GAP vs MATCHED SYNTHETIC (position bootstrap, alpha refit per draw, 2000 draws)

predictor          low   syn_low   alpha      high  syn_high       gap
S_A222V        +0.5283   +0.5185  0.5811   +0.1713   -0.0329   +0.2042
S_WT           +0.5325   +0.5188  0.5855   +0.1726   -0.0193   +0.1919
BLOSUM62       +0.2306   +0.2429  0.2559   +0.0550   -0.0141   +0.0691
Grantham       -0.1506   -0.0242  0.0000   -0.0400   +0.0380   -0.0779
  200/2000 draws
  ...
  2000/2000 draws

predictor          gap  boot_mean     CI_lo     CI_hi
S_A222V        +0.2042    +0.1936   +0.1333   +0.2532
S_WT           +0.1919    +0.1948   +0.1366   +0.2542
BLOSUM62       +0.0691    +0.0646   +0.0142   +0.1146
Grantham       -0.0779    -0.0381   -0.0841   +0.0111

C1b: gap(S_A222V) - gap(S_WT) = +0.0124 (boot mean -0.0012) CI=[-0.0375,+0.0370] p=0.9630
  -> RETENTION IS NOT BACKGROUND-SPECIFIC (CI includes 0)
```
Verdict: RETENTION IS NOT BACKGROUND-SPECIFIC. S_WT — ESM-2 on the WT sequence alone, no background supplied — retains +0.1919 over its matched synthetic in the high stratum vs S_A222V's +0.2042. The difference is +0.0124 with CI [−0.0375, +0.0370], p=0.9630; the bootstrap mean of the difference is −0.0012 (both estimates ≈ 0). Per the task's own wording: log 4.5's "retention" has nothing to do with background info — it is independence from WT-arm measurement noise. This answers the central open question from the last review round; C2 (MAE robustness) and C3 (oracle ceiling) now run on top of it.
Files created/modified: data/processed/task45_c1_gaps.csv, scripts/45_c1_reconciliation.py (shared with C1a/C1c/C1d), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Synthetic noise is a single seed-0 draw per evaluation; the bootstrap resamples positions and refits α but keeps the noise draw fixed — the same limitation script 30 ships with. Printed in the script's own output and stated here; not hidden.
- Bootstrap health: observed gap(S_A222V) +0.2042 vs boot mean +0.1936, gap(S_WT) +0.1919 vs +0.1948 — means track observed, as they should (AGENTS §4: a healthy bootstrap centres on the observed value).
---

## C1c — Do trivial WT-independent predictors (BLOSUM62, Grantham) also beat their matched synthetics?
Status: PASS for BLOSUM62 (clean matched test, POSITIVE result); Grantham row = METHOD LIMITATION (α-matching impossible), reported as a limitation, NOT as a result
Time started / finished: 2026-09-21 23:10:20 / 2026-09-21 23:11:50 (same N_BOOT=2000 run as C1a/C1b/C1d)
What I did: Same paired gap machinery as C1b, applied to raw BLOSUM62 and Grantham distance (both trivial, WT-independent predictors). Pre-registered verdict rule (docstring): gap CI > 0 ⇒ the trivial predictor also beats its matched synthetic ⇒ script 30's "beat" is at least partly generic (noise-sharing with the w.fitness anchor), not epistasis detection.
Actual output (real numbers, not a paraphrase):
```
predictor          gap  boot_mean     CI_lo     CI_hi
BLOSUM62       +0.0691    +0.0646   +0.0142   +0.1146
Grantham       -0.0779    -0.0381   -0.0841   +0.0111

C1c: gap(BLOSUM62) = +0.0691 CI=[+0.0142,+0.1146] SIG>0 (also beats its synthetic); gap(S_A222V)-gap(BLOSUM62) CI=[+0.0626,+0.1950]
C1c: gap(Grantham) = -0.0779 CI=[-0.0841,+0.0111] not > 0; gap(S_A222V)-gap(Grantham) CI=[+0.1452,+0.3123]
```
Verdict:
- BLOSUM62: matched cleanly (α=0.2559; synthetic low rho +0.2429 vs Grantham-style observed +0.2306) and its gap = +0.0691, CI [+0.0142, +0.1146] → significantly > 0. A trivial WT-independent predictor ALSO beats its matched synthetic in the high stratum. This SUPPORTS the review's suspicion: part of script 30's "beat" is generic noise-sharing with the w.fitness anchor, not epistasis detection.
- Both facts stand side by side: ESM's excess over its synthetic still exceeds BLOSUM62's — gap(S_A222V) − gap(BLOSUM62) CI [+0.0626, +0.1950] excludes 0. So: a real generic component AND a real ESM-specific excess on top of it. Neither fact cancels the other.
- Grantham: α pinned at the bisection floor 0.0000 because Grantham's low-stratum rho (−0.1506) is below anything an α≥0 anchor+noise synthetic can produce (at α=0 the synthetic's low rho is already −0.0242, and any α≥0 only raises it toward the anchor's positive correlation). Its gap −0.0779 CI [−0.0841, +0.0111] is therefore measured against an UNMATCHED synthetic and is not interpretable as a matched test in either direction. This is a method limitation of α-matching when the predictor's low-stratum correlation is negative — recorded as-is, not worked around post-hoc (AGENTS §0: no tuning a test until it behaves).
Files created/modified: data/processed/task45_c1_gaps.csv, scripts/45_c1_reconciliation.py, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Do NOT quote Grantham's −0.0779 as "Grantham fails to beat its synthetic" — the match never happened. If a matched Grantham test is wanted it needs a different null (e.g. a sign-permuted anchor), which would be a NEW pre-registered test, not a post-hoc tweak of this one.
- The BLOSUM62 positive is the load-bearing C1c result and it used a properly matched synthetic; its conclusion about script 30 does not depend on the Grantham row.
---

## C1d — Direct rank correlation S(v|A222V) vs S(v|WT)
Status: PASS — 0.999636 ≥ 0.99, exactly the threshold the task specified
Time started / finished: 2026-09-21 23:10:20 / 2026-09-21 23:11:50 (same run as C1a–C1c; value printed near the start of the run and persisted to task45_c1_misc.csv at 23:11:50)
What I did: Spearman(esm2_score_a222v_bg, esm2_score) over the full analysis set — one line of script 45, no model, no bootstrap needed (it is a descriptive reconciliation number).
Actual output (real numbers, not a paraphrase):
```
C1d  DIRECT: S(v|A222V) vs S(v|WT)
  Spearman = 0.999636  (n=10757)
  -> 0.99+ : the MAE story rests on a small number of rank swaps
```
Verdict: PASS. rho = 0.999636 (n=10,757) → log 6.2's MAE difference (A1c: diff = +0.0005334660988103312, CI [+0.00028835365805139276, +0.0007675630167030905], n=11,113 there vs 10,757 here because script 45 additionally requires grantham/blosum62/f_bar columns — both sizes already reconciled in A2b) rides on a predictor pair that is 0.9996 rank-identical. So 6.2's MAE story is a small number of rank swaps, not a broad pattern — precisely what REVIEW_TRIAGE predicted at the 0.99 threshold. The MAE difference can be simultaneously statistically solid (CI excludes 0) and substantively tiny (rho 0.9996); both should be quoted together, per AGENTS §3 (effect size alongside significance).
Files created/modified: data/processed/task45_c1_misc.csv, scripts/45_c1_reconciliation.py, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging: none beyond the single-seed synthetic limitation recorded under C1b (C1d does not use the synthetic at all).
---

## C2a — Influence: which variants drive 6.2's +0.00053?
Status: PASS — executed; pre-registered verdict MIXED (substantial proximity contribution, but NOT "a few dozen near-222 variants account for it")
Time started / finished: 2026-09-21 23:23:51 (scripts/46_c2_mae_robustness.py authored, rules pre-registered in docstring) / 2026-09-21 23:24:06 (full run finished; N_BOOT=200 smoke 23:23:51–23:23:56 = 2.4 s, full N_BOOT=2000 = 3.2 s — well under budget, run at full N, no reduced resolution)
What I did:
1. Replicated script 34's exact analysis set (n=11,113) and seed-0 position-crossfit isotonic calibrations for pred_A and pred_C, then passed GATE G1 (pooled MAE diff must equal the saved +0.0005334660988103312 to ≤1e-9; failure = exit 1, no retry — AGENTS §4).
2. Per-row influence c_i = |pred_C − y_i| − |pred_A − y_i| with calibration held fixed (pre-registered: standard decomposition of a mean difference), internal identity check |mean(c_i) − published| ≤ 1e-12.
3. Banded by linear distance to residue 222 (≤25 = 5.4's local zone, 26–100, >100). Pre-registered PRIMARY rule: LOCAL if ≤25 band ≥50% of signed total; BROAD if ≤20%; MIXED otherwise. SECONDARY: refit both calibrations on rows >25 only; survives if restricted diff stays ≥50% of full and >0.
4. Top-k contribution shares, leave-one-position-out range, enrichment check on top-50.
Actual output (real numbers, not a paraphrase):
```
Analysis set: 11113 variants, 654 positions (script 34's set; expected 11,113)
GATE G1: pooled MAE diff = +0.000533466098810331 (published +0.000533466098810331, |diff| = 0.000e+00)

C2a  INFLUENCE: which variants drive the +0.00053 (pred_C - pred_A)?
internal identity: mean(c_i) = +0.000533466098810373 (|diff| = 4.218e-17)
variants at position 222 exactly: 0 (A222X substitutions; p.Ala222Val itself has no model_C, excluded upstream)
band          n      sum_c   share%     mean_c
0-25        870    +1.3753    23.20 +1.581e-03
26-100     2546    +2.5593    43.17 +1.005e-03
>100       7697    +1.9937    33.63 +2.590e-04
PRIMARY RULE: share within |pos-222|<=25 = 23.20%  -> MIXED

top 10 variants by signed contribution:
  p.Val194Tyr        pos= 194  c=+0.1271
  p.Val194Arg        pos= 194  c=+0.1080
  p.Val194Gly        pos= 194  c=+0.0872
  p.Val194Ser        pos= 194  c=+0.0854
  p.Val218Gln        pos= 218  c=+0.0746
  p.Val194Asp        pos= 194  c=+0.0701
  p.Thr227Gln        pos= 227  c=+0.0641
  p.Ala195Tyr        pos= 195  c=+0.0635
  p.Val179Asp        pos= 179  c=+0.0635
  p.Gly221Tyr        pos= 221  c=+0.0622
top  10 contribute   13.59% of the signed total; 3 of them within 25 residues (rows overall in that zone: 7.8%)
top  25 contribute   26.53% of the signed total; 6 of them within 25 residues (rows overall in that zone: 7.8%)
top  50 contribute   43.56% of the signed total; 12 of them within 25 residues (rows overall in that zone: 7.8%)
top 100 contribute   73.68% of the signed total; 22 of them within 25 residues (rows overall in that zone: 7.8%)
expected # within 25 among top-50 under no enrichment: 3.9
leave-one-position-out diff: min=+0.000474 max=+0.000550 (full=+0.000533) -> widest shift from dropping position 194 (+0.000059)
SECONDARY drop-zone refit (rows >25 residues only, n=10243, refitted): diff = +0.000361 = 67.6% of full -> SURVIVES (>=50% and >0 pre-registered as survives)
```
Verdict: MIXED, with a clear distance-decay structure. Both halves of the task's question get a real answer:
- The proximity confound (5.4) contributes substantially PER-VARIANT: the ≤25 band is 7.8% of rows but 23.2% of the signed total (per-row mean +1.581e-3 vs +2.59e-4 beyond 100 — a 6.1× monotone decay with distance), and top-50 membership is enriched 3.1× for near-222 positions (12 observed vs 3.9 expected).
- But "a few dozen near-222 variants account for it" is NOT supported: top-25 = 26.5% and top-50 = 43.6% of the total (not a majority); the 26–100 band carries the largest share (43.2%); no single position can flip the sign (leave-one-position-out range [+0.000474, +0.000550], widest shift 11% from position 194); and after fully removing the ≤25 zone AND refitting, the diff is +0.000361 = 67.6% of full (pre-registered SURVIVES criterion).
- So the honest framing for the writeup: the +0.00053 is proximity-ENRICHED (consistent with5.4 as a contributor) but not proximity-DOMINATED; "background info hurts broadly" survives in weakened form — the effect is distributed with a gradient, not local to a few dozen variants.
Files created/modified: scripts/46_c2_mae_robustness.py, data/processed/task46_c2_influence.csv, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 46 uncommitted (no commits requested tonight).
Anything unexpected or worth flagging:
- GATE G1 replicated EXACTLY (|diff| = 0.000e+00) and the internal row-decomposition identity holds to 4.218e-17 —6.2's number is fully reproducible from current code + data.
- 0 variants at position 222 itself in the set (p.Ala222Val has no model_C by script 11's design; other A222X are not in this table) — so "near-222" here means neighbors only, no self-position artifact.
- Shares are of the SIGNED total (pre-registered); all three band sums are positive, so no sign pathology inflates any share.
- The top contributors cluster at positions 194/195/218/221/227 — a mix inside and outside the ≤25 zone, consistent with the gradient reading rather than a single hotspot.
---

## C2b — Fold-seed sensitivity: 50 seeds of the cross-fit isotonic calibration
Status: PASS — SEED-ROBUST (the review's concern does not materialize)
Time started / finished: 2026-09-21 23:23:51 / 2026-09-21 23:24:06 (same run as C2a/C2c; the 50-seed loop is the fixed-cost part of that 3.2 s run)
What I did:
1. Recomputed 6.2's pooled MAE diff (pred_C − pred_A) under 50 different position-fold seeds (0..49; seed 0 is the published one), n_folds=5 fixed, same analysis set — only the fold assignment varies, which is exactly the quantity under test.
2. Pre-registered comparator (docstring): published CI half-width = (0.0007675630167030905 − 0.00028835365805139276)/2 = 0.00023960487957904891. Rule: SEED-ROBUST if cross-seed sd ≤ half-width AND 0 sign flips; SEED-SENSITIVE if sd > half-width OR ≥5/50 flips; else MIXED.
3. Also computed the combined uncertainty sqrt(boot_sd² + seed_sd²) to size how much the published CI would need to widen if fold-seed noise were added in quadrature.
Actual output (real numbers, not a paraphrase):
```
C2b  FOLD-SEED SENSITIVITY: cross-fit isotonic under 50 seeds
cross-seed diffs: mean=+0.0004980 sd=0.0000528 min=+0.0003966 max=+0.0006214 (seed 0 = published +0.0005335)
published CI half-width = 0.0002396  (from [+0.000288, +0.000768])
sd / CI half-width = 0.220;  seeds flipping sign (diff <= 0): 0/50
combined sd = sqrt(boot_sd^2 + seed_sd^2) = 0.0001332  (boot_sd alone = 0.0001222)
VERDICT: SEED-ROBUST (sd <= CI half-width AND no sign flips)
```
Verdict: SEED-ROBUST. Cross-seed sd = 0.0000528, only 0.22× the published CI half-width; all 50 seeds produce a positive diff (range [+0.0003966, +0.0006214], entirely INSIDE the published CI [+0.000288, +0.000768]); 0/50 flip sign. The published seed-0 value (+0.0005335) sits 0.67 sd above the cross-seed mean (+0.0004980) — unremarkable. Adding fold-seed noise in quadrature would inflate the total sd from 0.0001222 to 0.0001332, a 9% increase — negligible. The task's conditional ("if the CI width is comparable to its cross-seed variance, the result isn't as clean as one seed suggests") resolves the other way: 6.2's CI is not materially understated by fold-seed variation, and one seed WAS representative.
Files created/modified: data/processed/task46_c2_seeds.csv, scripts/46_c2_mae_robustness.py (shared with C2a/C2c), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- C2b varies only the fold-assignment seed at n_folds=5; it does not vary fold COUNT or the calibration family (isotonic vs other) — stated in the script's limitations.
- Cross-seed mean (+0.0004980) is slightly below the published point estimate (+0.0005335); both are inside the CI and the difference is 0.67 sd — recorded, not a discrepancy requiring action.
---

## C2c — Does 6.3's high-stratum verdict hold under MSE instead of MAE?
Status: PASS — HOLD (verdict unchanged under the squared-error loss)
Time started / finished: 2026-09-21 23:23:51 / 2026-09-21 23:24:06 (same run as C2a/C2b; 6 bootstrap calls × N_BOOT=2000)
What I did:
1. Rebuilt 6.3's exact strata (script 34's rows: pd.qcut |e.b| terciles; n=10,757 = 11,113 minus the 356 rows with null e.b — the A2a/A2b n-chain, printed in the output) and passed GATE G2 (high-stratum MAE diff must equal the saved +0.0024089195313244105 to ≤1e-9).
2. Computed both MAE (house `paired_metric_difference_bootstrap`, position clusters) and MSE (locally-defined bootstrap with the identical algorithm — local because stats_ext's `_METRICS` has no "mse" key and shared lib must not be rewritten, AGENTS §7) on the same rows with the same seed (same position draws), N_BOOT=2000.
3. Pre-registered verdict on the HIGH stratum only: HOLD if MSE CI_lo > 0; REVERSED if CI_hi < 0; else INCONCLUSIVE. low/mid printed for completeness, no verdict.
Actual output (real numbers, not a paraphrase):
```
C2c  HIGH-STRATUM VERDICT UNDER MSE (vs MAE), 6.3's exact rows (2000 draws each)
strata formed on n=10757 (11,113 minus 356 rows with null e.b — the A2a/A2b n-chain)
low  (n=3586, 638 positions) MAE: null=0.2153 esm=0.2121 diff=-0.00317 CI=[-0.00418,-0.00215]
                     MSE: null=0.06463 esm=0.06269 diff=-0.001936 CI=[-0.002550,-0.001320]
mid  (n=3585, 649 positions) MAE: null=0.1930 esm=0.1928 diff=-0.00011 CI=[-0.00107,+0.00087]
                     MSE: null=0.05501 esm=0.05520 diff=+0.000196 CI=[-0.000286,+0.000719]
GATE G2: high-stratum MAE diff = +0.002408919531324 (published +0.002408919531324, |diff| = 0.000e+00)
high (n=3586, 609 positions) MAE: null=0.2481 esm=0.2505 diff=+0.00241 CI=[+0.00155,+0.00321]
                     MSE: null=0.09047 esm=0.09279 diff=+0.002320 CI=[+0.001740,+0.002895]
HIGH-STRATUM VERDICT UNDER MSE: HOLD (MSE CI_lo > 0: ESM-2 still worse than null)
```
Verdict: HOLD. Under MSE — the loss isotonic regression is actually optimized for — the high-stratum diff is +0.002320 with CI [+0.001740, +0.002895], excluding 0: ESM-2 remains reliably worse than assuming no interaction, and the magnitude is within 4% of the MAE diff (+0.00232 vs +0.00241). All three strata give the same verdict under both losses (low: ESM better, CI excludes 0 under both; mid: crosses 0 under both; high: ESM worse, CI excludes 0 under both). The task's loss/calibration-mismatch concern — evaluating a mean-optimal calibrator on a median-optimal metric — does not change any conclusion; 6.3 survives the MSE re-check intact.
Files created/modified: data/processed/task46_c2_mse.csv, scripts/46_c2_mae_robustness.py (shared with C2a/C2b), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- GATE G2 replicated EXACTLY (|diff| = 0.000e+00) — 6.3's number is reproducible from current code + data.
- Position counts per stratum (638/649/609) exceed neither 654 nor each other suspiciously: rows at one position carry different e.b and can fall in different strata, so positions overlap across strata; every bootstrap resamples clusters WITHIN its own stratum, which stays consistent.
- MAE and MSE bootstraps share seed 0 → identical position draws, but they are separate resampling runs, not a paired per-draw difference (stated in the script's output and limitations).
- Sign phrasing across documents: MTHFR_RESULTS_LOG 6.3 reports +0.00241 ("ESM-2 WORSE"); REVIEW_TRIAGE C3a calls it "−0.00241 loss" (loss phrasing). Same quantity, opposite sign conventions — logged here so both numbers exist in one place; neither document was edited.
---

## C3a — Oracle ceiling + correlation disattenuation
Status: PASS — ceiling computed and USABLE (pre-registered CI rule met); disattenuation verdict = MATERIALLY LARGER (pre-registered ratio rule met, narrowly — magnitude caveat in the verdict)
Time started / finished: 2026-09-21 23:33:48 (scripts/47_c3a_oracle_ceiling.py finalized after pre-run code review) / 2026-09-21 23:34:38 (full N_BOOT=2000 run finished; N_BOOT=200 smoke 23:34:01 = 1.6 s, full = 4.5 s — under budget, run at full N, no reduced resolution)
What I did:
1. Reliability is COMPUTED from data, not assumed (the review's "~0.64" had no in-repo source — traced to log §2.3's own-flavor numbers and rederived): rel = 1 − var(e.b | synonymous) / var(e.b | analysis set), for both e.b flavors. Synonymous rows rebuilt via `rebuild_interaction_fit` (script 35's pattern) because `own_context_metrics.csv` contains substitution rows only; GATE G5 cross-checks the rebuild against the CSV (max|diff| ≤ 1e-9).
2. Oracle = implied (f_bar_wt × A, multiplicative no-interaction on MEASURED quantities) + e.b + ε, ε sized to the computed reliability. The instruction's "+noise matched to reliability 0.64" is ambiguous, so BOTH readings are computed and labeled (protocol: conservative reading + log the assumption): (a) PRIMARY literal algebra σ² = var(e.b)(1/rel − 1); (b) classical measurement-error σ² = var(e.b)(1 − rel); plus the zero-noise reference. 10 noise draws (seeds 0–9), mean/sd reported; CI on the seed-0 draw via the house position bootstrap, pooled and in 6.3's exact high stratum.
3. PRE-REGISTERED (docstring): ceiling usable only if the primary oracle's pooled improvement CI excludes 0, else report "no measurable ceiling" and skip fraction claims.
4. GATES (exit 1 on failure): G3 rho(delta_esm, own_e_b) == −0.08811806424891734; G4 rho(delta_esm, published e.b) == −0.07070516222228716 (both script 32's saved values from S1); G5 rebuild identity.
5. Disattenuation r_dis = rho/√rel with delta_esm reliability = 1 (deterministic model — assumption printed). Joint position bootstrap: each draw resamples positions from the UNION of analysis-set and synonymous positions and recomputes rho AND rel, so the CI covers both uncertainties. PRE-REGISTERED: "materially larger" iff |r_dis|/|rho| ≥ 1.25 (the ratio rel=0.64 implies, fixed in advance) AND the CI excludes 0.
6. Pre-run code review found and fixed three bugs before any run (an index-label-vs-positional mismatch in both bootstrap maps, and one variable reassignment that would have corrupted the CSV's CI column) — AGENTS §5 duty, done before numbers existed, not after.
Actual output (real numbers, not a paraphrase):
```
Analysis set: 11113 variants, 654 positions (script 34's set; expected 11,113)   A = 0.6074

disattenuation analysis rows: 10757 (expected 10,757)
GATE G3 (rho own_e_b): got -0.088118064248917 (published -0.088118064248917, |diff| = 0.000e+00) -> OK
GATE G4 (rho published e.b): got -0.070705162222287 (published -0.070705162222287, |diff| = 0.000e+00) -> OK
GATE G5 (rebuilt vs CSV own_e_b): n=10757, max|diff| = 2.220e-16 -> OK

reliability, own e.b     : 1 - var(syn 0.02111, n=570) / var(analysis 0.05804) = 0.6363
reliability, published e.b: 1 - var(syn 0.02483, n=570) / var(analysis 0.06522) = 0.6193
review's assumed ~0.64 -> own flavor 0.636 (MATCHES); published flavor 0.619 (logged for the record)
synonymous own e.b: n=570, mean=+0.0217, sd=0.1453  [log 2.3 says mean +0.0217, sd 0.145]

C3a-1  ORACLE CEILING (position bootstrap, N_BOOT=2000)
CIRCULARITY, stated up front: e.b is fitted from the same
measurements that define target, so implied+e.b is an IN-SAMPLE
reconstruction. The oracle SIZES THE CEILING (how much MAE gain
exists between the null and near-perfect reconstruction); it is
NOT an achievable model and must not be quoted as one.
  target-implied ~ published e.b: slope=+0.9066 intercept=-0.0239 pearson=+0.9026 n=10757
  target-implied ~ own       e.b: slope=+0.9413 intercept=-0.0215 pearson=+0.8840 n=10757
  MAE(implied) alone          = 0.1847
  MAE(multiplicative null)    = 0.2210   [calibrated w_hat x A]

flavor     reading                              sigma  MAE_mean   MAE_sd  improve_pooled
published  zero-noise                          0.0000    0.0825   0.0000         +0.1385
published  primary (a): var_e*(1/rel-1)        0.2002    0.1826   0.0013         +0.0384
published  sensitivity (b): var_e*(1-rel)      0.1576    0.1531   0.0011         +0.0679
own        zero-noise                          0.0000    0.0855   0.0000         +0.1355
own        primary (a): var_e*(1/rel-1)        0.1821    0.1725   0.0009         +0.0485
own        sensitivity (b): var_e*(1-rel)      0.1453    0.1478   0.0007         +0.0732

PRIMARY oracle (published, reading a), POOLED n=10757: improvement over null = +0.0366 CI=[+0.0309,+0.0424] -> ceiling USABLE (CI excludes 0)
PRIMARY oracle, HIGH stratum (n=3586, 609 positions): improvement over null = +0.0521 CI=[+0.0436,+0.0613]

6.3/6.2 ESM-2 vs null AGAINST that ceiling (improvement = -diff; positive = ESM-2 better):
  pooled : ESM-2 improvement = +0.000308 = +0.84% of ceiling +0.0366   [saved task34 row: diff -0.000308347]
  high   : ESM-2 improvement = -0.002409 = -4.62% of ceiling +0.0521   [saved: diff +0.002408920; MTHFR_RESULTS_LOG 6.3 prints '+0.00241 ESM-2 WORSE', REVIEW_TRIAGE calls it '-0.00241 loss' — same number]

C3a-2  DISATTENUATION of rho(delta_ESM, e.b) (joint position bootstrap, N_BOOT=2000)
point (row-level): rho_own = -0.088118064249  (gate-checked vs script 32)
reliability own e.b (point) = 0.6369   [per-draw rel: mean 0.6368, sd 0.0343]
r_dis = rho / sqrt(rel) = -0.110413   (reliability of delta_esm assumed 1: deterministic model output)
CI (2000/2000 valid draws): [-0.147534, -0.072340]
|r_dis|/|rho| = 1.2530   [pre-registered 'materially larger' threshold 1.25 = ratio implied by rel=0.64, fixed in advance]
VERDICT: MATERIALLY LARGER (ratio >= 1.25 AND CI excludes 0)
published-flavor point for the record: r_dis_pub = -0.089845 (rho -0.070705, rel 0.6193; no CI — own flavor is the task's −0.088)

Saved task47_c3a_oracle.csv and task47_c3a_disattenuation.csv

LIMITATIONS (also in the docstring): oracle is in-sample
reconstruction (circularity disclosed above); its CI uses the
seed-0 noise draw (10-draw mean/sd printed above). Point rho is
row-level like script 32; only the CI is position-clustered.
delta_esm reliability assumed 1. Reading (b) assumes measurement
error uncorrelated with delta_esm. Reliability treats synonymous
e.b spread as pure noise (log 2.3's own control).
```
Verdict:
- CEILING USABLE (pre-registered rule met): a reliability-limited oracle (rel 0.636) beats the multiplicative null by +0.0366 pooled, CI [+0.0309, +0.0424], and by +0.0521 in 6.3's high stratum, CI [+0.0436, +0.0613]. 6.3's loss is now reportable against that reference instead of in isolation: pooled, ESM-2 captures +0.84% of the ceiling (indistinguishable from the null — consistent with 6.2's CI crossing 0); in the HIGH stratum ESM-2 moves the WRONG WAY for −4.62% of the ceiling — it lost 0.00241 MAE while +0.0521 was available. Zero-noise reference: +0.1385 pooled (+0.84% vs −4.6% under the primary oracle are both computed against the primary, reliability-limited ceiling, as pre-registered).
- IMPORTANT DECOMPOSITION (arithmetic on the printed numbers — the ceiling is NOT all interaction knowledge): the oracle also knows MEASURED f_bar_wt where the null knows only ESM's isotonic estimate w_hat. Measured-fitness component = MAE(null) − MAE(implied) = 0.2210 − 0.1847 = +0.0363 of the +0.1385 zero-noise pooled ceiling; interaction adds MAE(implied) − MAE(oracle) = +0.1022 zero-noise, but only +0.0021 under the primary reading (a) — its σ = 0.2002 noise nearly cancels e.b's signal — and +0.0316 under reading (b) (σ = 0.1576). Under the primary reading, the usable ceiling is therefore dominated by measured-fitness knowledge; the interaction-specific slice is small. Both readings printed; the task's literal reading is primary as instructed.
- DISATTENUATION: −0.088118 → −0.110413, CI [−0.147534, −0.072340] (2,000/2,000 valid draws), ratio 1.2530 ≥ 1.25 → MATERIALLY LARGER per the pre-registered rule. State it plainly alongside the effect size (AGENTS §3): the correction buys +25.3% on the magnitude, the CI comfortably excludes 0, and the verdict is stable across both e.b flavors (ratio 1.2530 own / 1.271 published) and both ddof conventions (1.2530 ddof=0 / 1.2535 ddof=1) — but the corrected correlation is still |r| ≈ 0.11, which is weak in absolute terms. Measurement-error correction does not rescue delta_ESM's correlation into a strong one; it moves a weak nonzero effect up by a quarter.
Files created/modified: scripts/47_c3a_oracle_ceiling.py, data/processed/task47_c3a_oracle.csv, data/processed/task47_c3a_disattenuation.csv, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 47 uncommitted (no commits requested tonight).
Anything unexpected or worth flagging:
- The ratio clears the pre-registered bar by 0.0030 (1.2530 vs 1.25). Report as "meets the bar narrowly," not as a comfortable pass. The bar was fixed in the docstring before the run, so this is not a post-hoc threshold — but the narrowness is a fact of the result.
- rel prints twice as 0.6363 (pandas var, ddof=1) and 0.6369 (np.var, ddof=0) — a ddof convention difference between two code paths; immaterial (every verdict above is identical under both), recorded rather than patched post-hoc (changing it after seeing output would be a silent post-hoc edit; AGENTS §0).
- Circularity: the oracle is an in-sample reconstruction (e.b is fitted from the same measurements as target) — the script prints this at the top of its own output; the oracle sizes the ceiling, it is not an achievable model. Never quote it as one.
- MAE(implied) alone (0.1847) already beats the calibrated null (0.2210): the null's w_hat = isotonic(ESM score → f_bar_wt) discards measured-fitness information. Any future comparison of ESM against a "no-interaction using measured quantities" baseline should expect that baseline to be strong even before interaction knowledge enters.
- n chain again consistent: pooled oracle CI n=10,757 (356 null-e.b rows of the 11,113 dropped — A2a/A2b chain), high stratum n=3,586 / 609 positions, identical to 6.3's rows (C2c verified those exact rows this session).
---

## E1a — Reframe script 36's gate around effect size instead of CI-excludes-zero
Status: PASS — gate reproduced EXACTLY (means and CIs), then DOWNGRADED under the pre-registered effect-size floor: 4 of 7 CI-passing groups fall below 0.10; the review's own question (disagreement magnitude vs e.b's SD ~0.24) answered directly — per-domain offsets 0.11-0.17 of e.b. SD, the between-domain GRADIENT only 0.061 of e.b. SD
Time started / finished: 2026-09-21 ≥23:34:38 (script 48 written after C3a's full run; start not separately stamped) / 2026-09-21 23:43:16 (full run verified complete via `date` immediately after). Smoke N_BOOT=200/N_PERM=300 = 0.36 s, extrapolated full ≈ 10×+33× of smoke segments → actual full N_BOOT=2000/N_PERM=10000 = 1.03 s; under the 10-min budget, run at FULL N, not reduced-resolution.
What I did:
1. `scripts/48_e1_effect_size_and_boundaries.py` part A, rebuilding script 36's analysis set through its exact code path (phase5 → merge own_context_metrics → structural features → dropna f_bar_wt/f_bar_a222v → rank_resid / eb_disagreement / region), same group iteration and <10-position skip.
2. GATE (exit 1 on failure): all 12 group means for stages domain_rank_resid / region_rank_resid / disagreement_domain must reproduce `task36_two_trait_diagnostic.csv` to ≤1e-9 with exact n. PASSED — max mean_diff 6.245e-17, every n exact (4980/4849/613/609, 2622/2506/2864/3121, 4816/4713/607/561). CIs also reproduce to ≤9.368e-17 at N_BOOT=2000/seed 0, which additionally proves script 36's own run used N_BOOT=2000 (its N_BOOT was unrecorded; now pinned by CI-level agreement).
3. Effect size = |mean| / sd (ddof=1, same set): rank_resid groups vs {sd_row=0.268631, sd_pos=0.092248}; disagreement groups vs {sd_row=0.037800, sd_pos=0.014058, sd_eb=0.240907}. PRIMARY denominator = LARGEST candidate (conservative reading of the review's ambiguous "relative to e.b's SD" — for the disagreement groups this IS sd_eb=0.2409, i.e. the review's own stated "~0.24"). Floor: PRIMARY 0.10; bands 0.05 and 0.25 printed too.
4. PRE-REGISTERED in the docstring before running: GATE SURVIVES if every CI-passing group also has es ≥ 0.10; DOWNGRADED if some; FAILS if none. DISCLOSURE (AGENTS §6): the 0.10 floor is post-hoc — chosen after the review had already quoted "~0.03-0.04 vs SD 0.24" — so all three bands are reported and the verdict must be read against them.
5. Row accounting (AGENTS §5): 62 domain-NULL rows in the 11,113 rank set, 60 in the 10,757 disagreement set — dropped by `groupby` in BOTH script 36 and script 48, identically; no other rows excluded anywhere (region n sums to exactly 11,113).
Actual output (real numbers, not a paraphrase):
```
==========================================================================
E1a  SCRIPT 36'S GATE, WITH AN EFFECT-SIZE FLOOR
==========================================================================
Analysis set: 11113 rows, 654 positions (script 36's set)
Rows with domain label NULL: 62 (rank_resid set) -- dropped by groupby in BOTH script 36 and this script
Disagreement set: 10757 rows, of which 60 domain-NULL (dropped from disagreement_domain groups)

GATE: reproduce reference means to <=1e-09 and n exactly (N_BOOT=2000 for recomputed CIs)
  domain_rank_resid      Catalytic    mean_diff=5.204e-17 n 4980==4980 ci_diff=9.021e-17 OK
  domain_rank_resid      Regulatory   mean_diff=2.689e-17 n 4849==4849 ci_diff=9.194e-17 OK
  domain_rank_resid      Ser-Rich     mean_diff=2.776e-17 n 613==613 ci_diff=4.163e-17 OK
  domain_rank_resid      unassigned   mean_diff=6.245e-17 n 609==609 ci_diff=8.327e-17 OK
  region_rank_resid      region_1     mean_diff=5.204e-17 n 2622==2622 ci_diff=9.021e-17 OK
  region_rank_resid      region_2     mean_diff=3.469e-18 n 2506==2506 ci_diff=9.368e-17 OK
  region_rank_resid      region_3     mean_diff=2.082e-17 n 2864==2864 ci_diff=8.847e-17 OK
  region_rank_resid      region_4     mean_diff=3.469e-18 n 3121==3121 ci_diff=9.021e-17 OK
  disagreement_domain    Catalytic    mean_diff=3.469e-17 n 4816==4816 ci_diff=9.368e-17 OK
  disagreement_domain    Regulatory   mean_diff=6.939e-18 n 4713==4713 ci_diff=2.082e-17 OK
  disagreement_domain    Ser-Rich     mean_diff=5.551e-17 n 607==607 ci_diff=8.327e-17 OK
  disagreement_domain    unassigned   mean_diff=2.082e-17 n 561==561 ci_diff=6.939e-17 OK
GATE PASSED. Max CI diff vs reference (informational, reference N_BOOT unrecorded): 9.368e-17

Denominators: rank_resid {'sd_row': 0.26863081023568836, 'sd_pos': 0.09224817737643261} | disagreement {'sd_row': 0.03780022862535025, 'sd_pos': 0.014057664901760506, 'sd_eb': 0.24090735229710575}
PRIMARY denominator per group = LARGEST candidate (conservative reading of 'residual sd / e.b. sd' -- assumption logged).

  stage                  group        mean      CI-gate   es_row  es_pos  es_eb  es_PRIM  >=0.05 >=0.10 >=0.25
  domain_rank_resid      Catalytic    -0.02085  EXCL0      0.078  0.226    nan   0.078   Y     N     N    
  domain_rank_resid      Regulatory   +0.00522  crosses    0.019  0.057    nan   0.019   N     N     N    
  domain_rank_resid      Ser-Rich     +0.08894  EXCL0      0.331  0.964    nan   0.331   Y     Y     Y    
  domain_rank_resid      unassigned   +0.03602  EXCL0      0.134  0.390    nan   0.134   Y     Y     N    
  region_rank_resid      region_1     +0.02604  EXCL0      0.097  0.282    nan   0.097   Y     N     N    
  region_rank_resid      region_2     -0.03111  EXCL0      0.116  0.337    nan   0.116   Y     Y     N    
  region_rank_resid      region_3     -0.01670  EXCL0      0.062  0.181    nan   0.062   Y     N     N    
  region_rank_resid      region_4     +0.01843  EXCL0      0.069  0.200    nan   0.069   Y     N     N    
  disagreement_domain    Catalytic    +0.02713  n/a        0.718  1.930  0.113   0.113   Y     Y     N    
  disagreement_domain    Regulatory   +0.03862  n/a        1.022  2.747  0.160   0.160   Y     Y     N    
  disagreement_domain    Ser-Rich     +0.04184  n/a        1.107  2.976  0.174   0.174   Y     Y     N    
  disagreement_domain    unassigned   +0.04154  n/a        1.099  2.955  0.172   0.172   Y     Y     N    

  GRADIENT (max - min of the four domain means):
    disagreement_domain    span=0.01471  ratios=sd_row=0.389 sd_pos=1.046 sd_eb=0.061
    domain_rank_resid      span=0.10978  ratios=sd_row=0.409 sd_pos=1.190

VERDICT (rule fixed in the docstring before running):
  GATE DOWNGRADED: 4 of 7 CI-passing groups below the 0.1 floor: domain_rank_resid/Catalytic (0.078), region_rank_resid/region_1 (0.097), region_rank_resid/region_3 (0.062), region_rank_resid/region_4 (0.069)  [bands: floor 0.05: 7/7 pass, floor 0.25: 1/7 pass, floor 0.1: 3/7 pass]

Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task48_e1a_effect_sizes.csv
```
Verdict:
- Script 36's CI-only gate is DOWNGRADED, as the review predicted. Under the pre-registered 0.10 floor with the conservative (largest-SD) denominator, 4 of the 7 CI-passing groups are below even a lenient bar: Catalytic rank residual 0.078, region_1 0.097, region_3 0.062, region_4 0.069. Only Ser-Rich (0.331), unassigned (0.134) and region_2 (0.116) clear 0.10; only Ser-Rich clears 0.25. Band sensitivity is the honest headline since the floor is post-hoc: 0.05 → 7/7 pass, 0.10 → 3/7 pass, 0.25 → 1/7 pass. The review's claim "nearly any nonzero mean will exclude zero at that scale" is confirmed as the mechanism: those four effects are statistically nonzero (CIs exclude 0) but ≤0.10 of their own residual SD.
- The review's specific numbers, answered on its own baseline: per-domain disagreement means 0.0271 / 0.0386 / 0.0418 / 0.0415 vs sd_eb = 0.2409 → effect sizes 0.113 / 0.160 / 0.174 / 0.172 — each domain's offset from zero is 11-17% of e.b's SD (all clear 0.10, none clear 0.25: real but modest). The GRADIENT the review actually asked about — max−min across domains = 0.01471 — is only 0.061 × e.b. SD (0.389 × disagreement-row SD, 1.046 × disagreement-position SD): the between-domain change in disagreement magnitude is small under the review's own SD baseline, even though every individual domain mean is a moderate fraction of it.
- Practical reading for the pipeline: an effect-size-gated version of script 36 would still fire overall (Ser-Rich, unassigned, region_2 survive at 0.10) but would no longer fire on Catalytic or on three of four regions — exactly the "significance at scale" inflation the review suspected, quantified rather than asserted.
Files created/modified: scripts/48_e1_effect_size_and_boundaries.py, data/processed/task48_e1a_effect_sizes.csv, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 48 uncommitted (no commits requested tonight).
Anything unexpected or worth flagging:
- Pre-full-run code review (after smoke, before any full run) caught and fixed one bug: the GRADIENT rows' es_primary used max(ratio) — i.e. the SMALLEST SD, anti-conservative and inconsistent with the group rows' largest-SD rule — while the printed verdict uses group rows only, so NO verdict changed; fixed to min(ratio) before the full run, disclosed here per AGENTS §6 (a consistency fix chosen after seeing the smoke's printed ratios; it makes that cell MORE conservative, never less).
- The gate's CI-level reproduction (≤9.37e-17) pins script 36's unrecorded N_BOOT at 2000 with seed 0 — recorded here rather than edited anywhere.
- No contradiction with MTHFR_RESULTS_LOG: every script 36 number (36a/36b/36c means) reproduced exactly; the downgrade is a change of DECISION RULE, not of underlying values.
- sd_pos (per-position means) is ~3× smaller than sd_row for rank_resid and ~2.7× for disagreement; using it instead would flip the verdict to nearly-all-pass. The conservative largest-SD choice was pre-registered precisely to avoid that fork — but a reader should know the verdict is denominator-dependent, which is why all three ratios are printed and saved to CSV.
---

## E1b — Decisive test: does the disagreement step at DOMAIN boundaries or REGION boundaries?
Status: PASS — DIVERGENCE (domain-only): at primary w=25 the DOMAIN-boundary set steps (T=0.01540, p_set = 0.0061) and the REGION-boundary set does not (T=0.00652, p_set = 0.5795). The data follows the domain boundaries (two-trait prediction), not the mutagenesis-region cuts (normalization-artifact prediction). Sensitivity: same divergence at w=40 (0.0046 / 0.6957), NOT at w=15 (0.2446 / 0.1468) — divergence is not w-robust, stated in the verdict below.
Time started / finished: same run as E1a (script 48 part B), finished 2026-09-21 23:43:16; N_PERM=10000 (position permutation) + exact circular-shift null over all 653 nonzero offsets; smoke at N_PERM=300 preceded it (0.36 s total script), full script 1.03 s.
What I did:
1. Units: per-position mean |own_e_b − published e.b| — 654 positions (2..656); position 222 absent from the data, consistent with C2a's "0 variants at pos 222". Position-level throughout (AGENTS §3/§4).
2. Boundary sets: DOMAIN = per-residue Domain label changes from `MTHFR_structural_features.csv`, counting only ADJACENT residue pairs → [36, 48, 338, 363, 645]; REGION = start of regions 2-4 from `scripts/lib/regions.py` → [148, 295, 475]. These are the two competing predictions: domain edges (two-trait) vs region cuts (atlas authors rescaled regions independently → normalization artifact).
3. FULL-WINDOW rule, pre-registered: a boundary is testable at w only if EVERY residue of both ±w windows is a data position (conservative: fewer boundaries, identical window sizes). Logged drops: 645 at w=25 (right window 12/25 — protein ends at 656), 645 at w=15 (12/15), 36 and 645 at w=40 (34/40 needs negative residues, 12/40).
4. Statistic per set: T = max over testable boundaries of |mean(d[R]) − mean(d[L])|. TWO nulls — the review specified only (a): (a) position permutation of d across positions, N_PERM=10000 with +1 correction; (b) circular shift over all 653 nonzero offsets (EXACT, preserves the spatial autocorrelation that permutation destroys and can make anti-conservative). p_set = max(p_perm, p_shift) — conservative; the added null and the max-p rule are logged as assumptions (AGENTS §9). Verdict from primary w=25 only; w=15/40 sensitivity, not verdict-bearing.
5. PRE-REGISTERED decision categories in the docstring: DIVERGENCE (domain-only / region-only), CONCORDANCE (both), NEITHER, UNTESTABLE.
Actual output (real numbers, not a paraphrase):
```
==========================================================================
E1b  DOMAIN vs REGION BOUNDARY STEP TEST on the disagreement profile
==========================================================================
Per-position disagreement: 654 positions (2..656); positions absent from data: [222]
DOMAIN label-change boundaries (adjacent pairs only): [36, 48, 338, 363, 645]
REGION boundaries from scripts/lib/regions.py:        [148, 295, 475]
  w=25 DOMAIN boundary 645: DROPPED (windows need 25 residues, have 25/12)

  --- w=25 (PRIMARY) ---
  DOMAIN b=  36  step=-0.00766  p_perm=0.0575 p_shift=0.1850
  DOMAIN b=  48  step=-0.01191  p_perm=0.0036 p_shift=0.0413  <-- uncorrected p<0.05 under both nulls
  DOMAIN b= 338  step=+0.01540  p_perm=0.0004 p_shift=0.0015  <-- uncorrected p<0.05 under both nulls
  DOMAIN b= 363  step=-0.00049  p_perm=0.9059 p_shift=0.9067
  REGION b= 148  step=-0.00652  p_perm=0.1036 p_shift=0.2324
  REGION b= 295  step=-0.00619  p_perm=0.1189 p_shift=0.2584
  REGION b= 475  step=+0.00202  p_perm=0.6068 p_shift=0.6697
  DOMAIN SET MAX |step|=0.01540  p_perm=0.0007 p_shift=0.0061 p_SET=max=0.0061  (4 boundaries)
  REGION SET MAX |step|=0.00652  p_perm=0.2723 p_shift=0.5795 p_SET=max=0.5795  (3 boundaries)

  VERDICT at w=25, alpha=0.05, p_set = max(permutation, circular-shift):
    DIVERGENCE: domain-boundary step found (p<0.05), region-boundary step not found
  w=15 DOMAIN boundary 645: DROPPED (windows need 15 residues, have 15/12)

  --- w=15 (sensitivity, not verdict-bearing) ---
  DOMAIN b=  36  step=-0.00877  p_perm=0.0930 p_shift=0.1468
  DOMAIN b=  48  step=-0.00570  p_perm=0.2609 p_shift=0.3930
  DOMAIN b= 338  step=+0.01098  p_perm=0.0365 p_shift=0.0627
  DOMAIN b= 363  step=-0.00183  p_perm=0.7160 p_shift=0.8150
  REGION b= 148  step=-0.01120  p_perm=0.0290 p_shift=0.0520
  REGION b= 295  step=-0.00238  p_perm=0.6417 p_shift=0.7492
  REGION b= 475  step=-0.00180  p_perm=0.7198 p_shift=0.8226
  DOMAIN SET MAX |step|=0.01098  p_perm=0.1296 p_shift=0.2446 p_SET=max=0.2446  (4 boundaries)
  REGION SET MAX |step|=0.01120  p_perm=0.0835 p_shift=0.1468 p_SET=max=0.1468  (3 boundaries)
  w=40 DOMAIN boundary 36: DROPPED (windows need 40 residues, have 34/40)
  w=40 DOMAIN boundary 645: DROPPED (windows need 40 residues, have 40/12)

  --- w=40 (sensitivity, not verdict-bearing) ---
  DOMAIN b=  48  step=-0.00932  p_perm=0.0039 p_shift=0.1223
  DOMAIN b= 338  step=+0.01521  p_perm=0.0001 p_shift=0.0015  <-- uncorrected p<0.05 under both nulls
  DOMAIN b= 363  step=+0.00366  p_perm=0.2426 p_shift=0.5428
  REGION b= 148  step=-0.00608  p_perm=0.0548 p_shift=0.3180
  REGION b= 295  step=-0.00380  p_perm=0.2323 p_shift=0.5321
  REGION b= 475  step=+0.00146  p_perm=0.6440 p_shift=0.7920
  DOMAIN SET MAX |step|=0.01521  p_perm=0.0001 p_shift=0.0046 p_SET=max=0.0046  (3 boundaries)
  REGION SET MAX |step|=0.00608  p_perm=0.1538 p_shift=0.6957 p_SET=max=0.6957  (3 boundaries)

Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task48_e1b_boundary_steps.csv
```
Verdict:
- DIVERGENCE at the pre-registered primary (w=25, α=0.05, p_set = max of both nulls): DOMAIN set T=0.01540, p_set=0.0061 (steps); REGION set T=0.00652, p_set=0.5795 (no step). The disagreement profile follows the DOMAIN boundaries — the two-trait hypothesis's prediction — and not the mutagenesis-region boundaries, which is what the normalization-artifact explanation predicted. Per the task's framing, this runs BEFORE any MoCHI refit: the refit, if done, should control for domain structure; region-normalization is not where the disagreement lives.
- Where the steps are, exactly: both load-bearing boundaries are the Catalytic-domain edges — entering at b=48 the disagreement DROPS (step −0.01191, p_perm=0.0036 / p_shift=0.0413), leaving at b=338 it RISES (+0.01540, p_perm=0.0004 / p_shift=0.0015), both uncorrected p<0.05 under BOTH nulls. Direction matches 36c independently: Catalytic has the lowest mean disagreement (0.0271) vs 0.039-0.042 elsewhere. The Ser-Rich/Regulatory internal edge b=363 shows nothing (p≈0.91), b=36 is borderline (p_perm=0.0575). No region boundary is even suggestive at w=25 (best uncorrected p_perm=0.1036).
- SENSITIVITY, stated plainly because it tempers the verdict: the divergence reproduces at w=40 (DOMAIN 0.0046 / REGION 0.6957) but NOT at w=15 (DOMAIN 0.2446 / REGION 0.1468 — neither set steps). The primary w=25 and one of two sensitivity widths agree; the narrowest window does not. The finding is real at the pre-registered width and at the wider width, not width-independent.
- Effect sizes alongside significance (AGENTS §3): the load-bearing step is 0.0154 on a disagreement profile whose row-level SD is 0.0378 and whose between-domain span is 0.0147 — the single largest step is about the same size as the entire across-domain gradient, and ~0.4 × the disagreement row SD. Modest in magnitude; decisive only in WHERE it sits (domain vs region).
Files created/modified: data/processed/task48_e1b_boundary_steps.csv, docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry); script shared with E1a (scripts/48_e1_effect_size_and_boundaries.py, uncommitted).
Anything unexpected or worth flagging:
- LIMITATIONS block printed by the same run (shared with the E1a entry; verbatim, E1b-relevant bullets): "- E1b uses TWO nulls and takes max p: the review specified only position permutation; circular shift added because permutation destroys spatial autocorrelation and can be anti-conservative. The circular-shift null treats the chain as circular (it is not); it serves only as the conservative tie-breaker. / - E1b tests alignment of a profile with boundaries, not causation. / - Overlapping windows (domain 36/48 at w=25) handled by the max statistic, not multiplicity correction. / - Inherited power caveat (script 36): one alternate background only; a null result here is weak evidence of absence."
- The set-level DOMAIN result is driven by b=338 under the circular-shift null (p_shift=0.0061) — b=48's p_shift=0.0413 individually is close to the line; the max-statistic set p, not any single boundary, is the claim.
- Boundary 645 (Regulatory→unassigned, near the C-terminus) is untestable at every w tried (only 12 residues to the protein end) — dropped, logged, not silently skipped; it is a domain boundary where no conclusion is drawn.
- w=15's REGION set shows an uncorrected hint at b=148 (p_perm=0.0290) that does NOT survive the shift null (0.0520) or the set max — do not promote it to a finding; recorded so the number exists in one place.
- No contradiction with MTHFR_RESULTS_LOG (nothing in it covers boundary steps); consistent with C1a/E1a's domain-mean ordering (Catalytic lowest disagreement) by construction of the same underlying rows (n=10,757 / 654 positions).
---

## I1 — Pipeline validation on a known-epistatic dataset (GB1 four-site landscape)
Status: PASS as a test run (gates, identity check, null, CI all correct) — but the pre-registered GATE FAILED: pooled rho = +0.4467 > 0 yet one-sided permutation p = 0.1398 >= 0.05, because the within-site permutation null sits at +0.3880 (between-site structure) and the within-site pairing excess (+0.059) does not clear the bar. Per the decision rule fixed in the script's docstring before running: the pipeline does NOT demonstrate sensitivity to established epistasis here, so MTHFR's negative is confounded with pipeline limitation and must be reported as such.
Time started / finished: 2026-09-22 ~03:30 to 04:05:51 (smoke, timeout diagnosis, intermediate timing run, then full run); full run N_BOOT=2000 / N_PERM=10000, script elapsed 10.8 s (11.4 s wall).
What I did:
1. Positive control per REVIEW_TRIAGE item 31: run the delta_ESM pipeline on a dataset with established epistasis. Data: GB1 four-site deep-mutational-scan (Wu/Dai/Olson/Lloyd-Smith/Sun eLife 2016;5:e16965, Zenodo record 5014984) at data/external/GB1_fitness_landscape.txt, md5=89e8d0f088466a1e29714721ed7967e8: 160,000 genotypes, WT VDGV fitness 1.0.
2. Pre-registered design (scripts/49_i1_gb1_positive_control.py docstring): focal sites 39/40/41 only — site 4 DROPPED because the file's WT letter there (V) contradicts authoritative RCSB 2GB1 (T44), unresolved without the paper's numbering; disclosed, not guessed. Sub-landscape = column 4 held at WT "V" -> 8,000 rows. K_BG = 10 fitness-blind alternate backgrounds per focal site (seed 0, no replacement from 399) -> 570 (variant, background) pairs. delta_ESM = S(v|b) − S(v|b0) via scripts/lib/esm_scoring.get_position_logprobs (one forward pass per background), mirroring scripts 10/11/32. Target = double-mutant-cycle epistasis e(v,b) = f(v,b) − f(v,b0) − f(WT,b) + f(WT,b0), all four fitness lookups from the file.
3. Statistics as pre-registered: pooled Spearman rho; within-site variant-label permutation ASSOCIATION null (a variant's whole K-background e-profile moves as a unit, delta fixed), N_PERM=10000, one-sided positive gate primary, two-sided also printed; identity-through-machinery check (exit 1 on failure); cluster bootstrap by (site, variant) = 57 clusters, N_BOOT=2000. Gate PASS iff rho > 0 AND one-sided p < 0.05.
4. Sequence provenance: PDB 2GB1 polymer entity sequence (56-mer), VDG at 39-41 verified, "NGVDG" motif unique in the sequence (both gated, exit 1 otherwise). Every data gate passed (below).
Actual output (real numbers, not a paraphrase):
```
Data gates PASSED:160,000 genotypes, WT=VDGV=1.0, sub-landscape8,000 rows; md5=89e8d0f088466a1e29714721ed7967e8
Sequence: PDB2GB156-mer; focal sites (39, 40, 41) = ('V', 'D', 'G'); site4 dropped (file WT letter V vs 2GB1 T44 — contradiction)

Loading ESM-2 t33 650M on mps...
Scored 33 forward passes; 570 (variant, background) pairs (expected 570)

PRIMARY: pooled Spearman rho(delta_ESM, e) = +0.4467 over n=570 pairs, 3 sites, K=10 backgrounds/site
Identity check: identity order through the block machinery reproduces rho (max|diff| = 0.000e+00) — PASS
NULL (variant-profile permutation within site, N_PERM=10000): mean=+0.3880 sd=0.0532 -> NULL DOES NOT CENTER ON ZERO — raw rho would overstate the effect; excess over null is the real result (AGENTS §4)
  one-sided p (pre-registered, positive) = 0.1398   two-sided p = 0.1398
CI (cluster bootstrap by (site,variant), N_BOOT=2000): [+0.2787, +0.5793]  (2000/2000 valid)
Per-site rho:
  site 39: rho=+0.3165  (n=190)
  site 40: rho=-0.1506  (n=190)
  site 41: rho=+0.5234  (n=190)

I1 GATE: FAIL: pipeline does NOT detect established epistasis at the pre-registered bar — MTHFR's negative is confounded with pipeline limitation
Scale context: MTHFR's verified rho(delta_ESM, e.b) = -0.088118 (S1/script-32, gate-checked in script 47)

Saved to /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task49_i1_gb1.csv  (elapsed 10.8s)

LIMITATIONS (printed by the script):
  - STRONG-epistasis control: passing shows the pipeline is not
    blind; it does NOT prove sensitivity to MTHFR-sized effects.
  - Site4 excluded: file WT letter V vs 2GB1 T44 contradiction,
    unresolved without the paper's numbering (disclosed, not guessed).
  - Background sampling fitness-blind, seed0, K=10 fixed pre-run.
  - Association null (pairing shuffle), not re-derivation: tests
    whether the pairing beats chance — the pipeline claim.
  - CI clusters by (site,variant) —57 clusters; 3 sites too few
    for a site-level bootstrap; per-site rhos reported instead.
  - GB1 fitness = sort-based assay; noise model differs from the
    atlas's. One model (ESM-2650M), as in the main pipeline.
  - Settings: N_BOOT=2000, N_PERM=10000, SEED=0, K_BG=10.
```
Verdict:
- GATE FAIL, reported plainly per AGENTS §0. The pre-registered rule (rho > 0 AND one-sided p < 0.05) is not met: rho = +0.4467 clears the sign half, but p = 0.1398 does not clear the significance half. The decision rule was fixed in the script's docstring before any run; it is not being renegotiated after seeing the result.
- WHY it fails, mechanism stated exactly: the permutation null does NOT center on zero — it sits at +0.3880 (sd 0.0532) because permuting variant labels within site preserves all between-site structure, and most of the pooled +0.4467 is between-site (the three sites differ in both delta_ESM and epistasis distributions). The within-site pairing excess — the thing the pipeline actually claims — is only ~+0.059 over the null, ~1.1 null-sds, hence p ≈ 0.14. Per AGENTS §4 the excess over the null is the real result, and it is not significant.
- Effect size alongside significance (AGENTS §3): the raw pooled rho's cluster-bootstrap CI [+0.2787, +0.5793] excludes zero and is large — but that CI is for the RAW rho, which the non-centered null says is mostly structure, not pairing. Quoting the CI without the null would overstate; both are printed by the same run for exactly this reason.
- Per-site heterogeneity: site 39 +0.3165, site 41 +0.5234 (both positive), site 40 -0.1506 (negative). The control is not uniformly positive across sites even before null-centering.
- Consequence for the project, per the pre-registered decision rule: the pipeline did NOT demonstrate sensitivity to established epistasis in this design, so MTHFR's negative result (rho = -0.088118, printed by the same run for scale) is confounded with pipeline limitation. I1's question — "can a negative here be distinguished from a pipeline limitation?" — resolves to NO at this bar. That weakens any absence-of-epistasis claim built on the same machinery, and it is the single most important item for the morning.
- IMPORTANT LIMIT on how far this cuts (stated because the FAIL could be over-read): the failure is on the WITHIN-SITE pairing half of the signal, in a design with K=10 alternate backgrounds and a sort-based fitness noise model, on one ESM-2 650M scoring pass — not a blanket "ESM sees nothing" result. The raw association with established epistasis is large and its CI excludes zero; what fails is the stricter pairing-specific bar the task pre-registered. A reasonable next diagnostic (NOT run tonight, listed for the morning) is whether the between-site component alone reflects real biology or site-level confounding (e.g. site 40's sign flip).
- Reproducibility note: three resolution settings all agreed — smoke (N_BOOT=200/N_PERM=300) p=0.1329, intermediate (500/2000) p=0.1309, full (2000/10000) p=0.1398 — so the FAIL is not a draw-count artifact. Rho is identical to 4 decimals at every setting (it does not depend on N_BOOT/N_PERM).
Files created/modified: scripts/49_i1_gb1_positive_control.py (new), data/processed/task49_i1_gb1.csv (new), data/external/GB1_fitness_landscape.txt (new, downloaded public data), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Nothing else touched; RESULTS.md / MTHFR_RESULTS_LOG.md / REVIEW_TRIAGE.md untouched. All new files uncommitted (no commits requested tonight).
Anything unexpected or worth flagging:
- Pre-run bug caught and fixed before ANY run (AGENTS §7): the smoke run crashed with `TypeError: 'float' object is not subscriptable` — the loop unpacked `sc_b` as the float value of `s_b.items()` but the code subscripted it as a dict (`sc_b[v]`). Fixed to `sc_b - s_b0[v]` (identical meaning, no result changed — the crash happened before any statistic existed). Recorded because the fix happened after one failed execution; no output was inspected to choose it.
- First full-run attempt timed out at 600 s with ZERO bytes of output (Python block-buffers stdout on a pipe; the kill discarded the buffer, so no partial result was lost or half-read). Diagnosis by timing, not guessing (troubleshooting tree): an intermediate run (N_BOOT=500/N_PERM=2000) completed in 9.6 s and a rerun of the exact full command completed in 10.8 s — the timeout was a transient hang (consistent with the ECONNRESET transport instability seen elsewhere tonight), not a runtime property. The reported numbers are from the successful full run at the pre-registered N_BOOT=2000/N_PERM=10000; resolution was NOT reduced.
- The null's non-centering (+0.3880) is the substantive surprise: a within-site permutation preserving site membership still leaves ~87% of the pooled rho intact (0.388/0.4467). Read together with per-site rhos (two positive, one negative), the pooled signal is mostly between-site structure. This is exactly the artifact class AGENTS §4 warns about, caught by the null the design pre-registered.
- Site-4 letter contradiction (file "V" vs RCSB 2GB1 T44) remains unresolved without the paper's mutagenesis numbering; it is disclosed in the script, the output, and this entry rather than guessed. The analysis ran on sites 39/40/41 only.
- Smoke and full runs both passed the identity check exactly (max|diff| = 0.000e+00) and every data gate; no sanity check failed at any point, so no run was abandoned on a failed check.
- No contradiction with MTHFR_RESULTS_LOG (it contains no GB1 or positive-control results); the MTHFR scale value printed by script 49 (-0.088118) matches S1/script 47's gate value exactly.
---

## D1a — Is the high-|e.b| stratum enriched for high-SE variants? (winner's curse)
Status: PASS — ENRICHED: the high-|e.b| tercile carries 65.4% higher mean SE(e.b) than the low tercile (0.1166 vs 0.0705), position-cluster CI excludes zero, and 47.3% of the high stratum sits in the top-SE tercile vs 24.3% of the low stratum. The review's winner's-curse suspicion is CONFIRMED as a property of the stratifier. Whether it actually explains 6.3's verdict is D1b's question (it does not — see D1b).
Time started / finished: authored ~2026-09-22 04:15-05:00, smoke 05:02 (N_BOOT=200, 2.6 s), full run finished 2026-09-22 07:11 (N_BOOT=2000, 11.6 s wall) — under budget, full resolution, no reduced-N run.
What I did:
1. Script 50 (scripts/50_d1_stratifier_quality.py) implements D1a+D1b+D1c in one run; this entry covers D1a only. Decision rules pre-registered in the docstring before any run.
2. Analysis set = exactly 6.3's rows: script-34 build mirrored (phase5_analysis_table + own_context_metrics join + dropna(model_A, model_C, target, f_bar_wt) = 11,113, then dropna(|GI|) = 10,757), with se_e_b joined from task35_epistatic_set.csv (complete on all 10,757; the join's row-set identity with script 35's valid-SE missense rows was verified separately: symmetric difference = 0).
3. Strata = pd.qcut(|GI_folinate_independent|, 3), labels FIXED within bootstrap draws (script 46's C2c convention — not script 34's re-quantiling). Statistic D = mean(SE|high) − mean(SE|low), position-cluster bootstrap over 654 positions, N_BOOT=2000. Pre-registered verdict: ENRICHED iff CI_lo > 0.
4. Replication gates all exact before any statistic: set n=11,113; G1 pooled MAE = +0.000533466098810331 (|diff| = 0.000e+00 vs published); identity checks on both bootstrap helpers (equal-valued distinct columns) = 0.000e+00; s-set n=10,757 with complete SE join.
Actual output (real numbers, not a paraphrase):
```
strata (pd.qcut |GI| terciles, FIXED labels in draws — C2c rule):
  low  n= 3586  mean SE=0.0705  median SE=0.0562  share in top-SE tercile=0.243 (1/3 = no enrichment)
  mid  n= 3585  mean SE=0.0757  median SE=0.0591  share in top-SE tercile=0.284 (1/3 = no enrichment)
  high n= 3586  mean SE=0.1166  median SE=0.0769  share in top-SE tercile=0.473 (1/3 = no enrichment)

PRIMARY D = mean(SE|high) - mean(SE|low) = +0.0461  CI=[+0.0396, +0.0535]  (2000/2000 valid, 654 positions)
effect size: mean_SE_high / mean_SE_low = 1.654 (+65.4%)  [AGENTS §3]
D1a VERDICT (pre-registered rule): ENRICHED

secondary Spearman(|GI|, SE) = +0.2650  CI=[+0.2406, +0.2901]  (descriptive; same WLS fit feeds both — see limitations)

sensitivity (|own_e_b| strata): D = +0.0436  CI=[+0.0370, +0.0510];  stratum agreement own vs GI = 0.822 (the ~82% from design checks)
sensitivity verdict: ENRICHED (not verdict-bearing)
Saved /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task50_d1a_se_enrichment.csv + _stats.csv
```
Verdict:
- ENRICHED at the pre-registered bar. Effect size alongside significance (AGENTS §3): the difference is +0.0461 analytic SE units, but the interpretable figure is the 1.65× ratio — the high-|e.b| stratum, the one every stratified headline (6.3, script 36, C2c) is read from, is drawn from a measurably noisier population than the low stratum. Under winner's curse this is exactly the pattern expected: selecting on |estimate| preferentially selects high-SE estimates.
- Shape, not just the endpoint: shares of the top-SE tercile rise monotonically 0.243 → 0.284 → 0.473 (nearly half of the high stratum is top-SE-tercile variants), and Spearman(|GI|, SE) = +0.265 [CI +0.241, +0.290]. Median SE tells the same story (0.0562 → 0.0769), so the mean difference is not one outlier stratum.
- Sensitivity (own_e_b as stratifier, not verdict-bearing): same conclusion, D = +0.0436 [+0.0370, +0.0510], stratum agreement with the published stratifier 0.822 — the enrichment is not an artifact of the own-vs-published e.b choice.
- This is a STRATIFIER defect, not yet a VERDICT defect: D1a alone cannot say whether 6.3's high-stratum conclusion depends on the enriched noise — that is the explicit D1b question, run next on the same rows (answer there: UNCHANGED-HOLD).
- Caveat printed by the script itself: SE(e.b) and e.b come from the same WLS fit, so this association is the winner's-curse signature, not a causal claim; and analytic SEs are themselves miscalibrated (script 35's 3.76× empirical/analytic ratio, recomputed in D1c), so absolute SE levels understate noise — the enrichment statistics are RELATIVE and inherit that scale error.
Files created/modified: scripts/50_d1_stratifier_quality.py (new), data/processed/task50_d1a_se_enrichment.csv, data/processed/task50_d1a_se_enrichment_stats.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry). Script 50 uncommitted (no commits requested tonight).
Anything unexpected or worth flagging:
- Pre-run issues fixed BEFORE the full run, disclosed per AGENTS §6: (a) the first smoke crashed because the identity check passed the same column name as both bootstrap arms — pandas duplicated the column and the lib crashed on shape (n,2); fixed by aliasing the identical values into a distinct column (the check never produced a statistic, so nothing was tuned). (b) The D1a CSV's summary rows initially overloaded the stratum columns (CI bounds written into median_se/share columns) — schema split into a separate _stats.csv before the full run so no misleading file was ever produced at full N.
- The 10,757 coincidence: script 35's valid-SE missense rows and the 6.3 s-set are both exactly 10,757 — verified to be the SAME set (hgvs symmetric difference = 0), not two filters happening to collide. This adds one link to A2b's n-chain: the atlas's published-GI nulls and the WLS SE's non-computability drop the same 1,145 missense rows.
- Top-SE-tercile share in the LOW stratum is 0.243, below the 1/3 no-enrichment line — the enrichment is a genuine redistribution toward the high stratum, not uniform slippage.
- No contradiction with MTHFR_RESULTS_LOG (it contains no SE-by-stratum analysis); consistent with script 35's known SE miscalibration (this quantifies its stratifier-facing consequence, which script 35 did not compute).
---

## D1b — Does 6.3's high-stratum verdict survive an empirical-Bayes shrunken e.b stratifier?
Status: PASS — UNCHANGED-HOLD: under EB-shrunken |e.b| terciles the high-stratum MAE diff is +0.001851 with CI [+0.000987, +0.002706] (excludes 0, ESM-2 still worse than the no-interaction null) — 6.3's verdict holds even though shrinkage purges the high stratum of the D1a high-SE enrichment (its mean SE falls from 0.1166 to 0.0788, and the SE gradient INVERTS: the EB-low stratum becomes the noisiest at 0.1045). The winner's-curse enrichment D1a confirmed does not carry 6.3's verdict.
Time started / finished: same run as D1a/D1c (scripts/50_d1_stratifier_quality.py), full run finished 2026-09-22 07:11, N_BOOT=2000 (11.6 s wall total for all three tasks); smoke at N_BOOT=200 preceded it.
What I did:
1. G2 replication gate FIRST: arm1 (the original |GI| stratifier) high-stratum MAE diff must equal 6.3's published +0.0024089195313244105 to 1e-9 — observed |diff| = 0.000e+00. Same rows (10,757), same cross-fitted predictions (pred_C = cross-fit isotonic of model_C on target; pred_mult = w_hat × A from f_bar_wt of p.Ala222Val; seed 0, 5 position folds — script 46's build mirrored exactly), so any verdict change is attributable to the stratifier alone.
2. Three arms, everything else identical: arm1 = |GI_folinate_independent| (original, gated); arm2 = |own_e_b| (own-vs-published switch control); arm3 = |EB-shrunk own_e_b| (the task). EB shrinkage: shrunk = e.b × τ²/(τ²+se²) with τ² = var_ddof1(own_e_b) − mean(se²) = 0.058036 − 0.022146 = 0.035890 (method of moments, single global Gaussian prior). Shrinkage uses own_e_b + its analytic SE ONLY — never the target — so it cannot leak into the cross-fitted predictions; strata only decide grouping.
3. Per arm and stratum: MAE diff (stats_ext.paired_metric_difference_bootstrap) and MSE diff (local mirror of script 46's helper — stats_ext._METRICS has no 'mse', shared lib not rewritten per AGENTS §7), position-cluster bootstrap, CIs. Pre-registered verdict on arm3's MAE CI: UNCHANGED-HOLD / REVERSED / DOWNGRADED. Stratum membership agreement reported pairwise.
Actual output (real numbers, not a paraphrase):
```
G2: arm-1 high-stratum MAE diff = +0.002408919531324 (6.3 = +0.002408919531324, |diff| = 0.000e+00)

EB prior (method of moments): var(own_e_b) = 0.058036 - mean(se^2) = 0.022146  ->  tau^2 = 0.035890
shrink factor: min=0.003 median=0.901 max=0.994; spearman(raw, shrunk) = 0.9861

--- arm1_raw_GI (stratifier: abs_gi) ---
  low  (n= 3586, 638 pos, mean SE=0.0705)  MAE diff=-0.003166 CI=[-0.004181,-0.002154]  MSE diff=-0.001936 CI=[-0.002550,-0.001320]
  mid  (n= 3585, 649 pos, mean SE=0.0757)  MAE diff=-0.000109 CI=[-0.001073,+0.000875]  MSE diff=+0.000196 CI=[-0.000286,+0.000719]
  high (n= 3586, 609 pos, mean SE=0.1166)  MAE diff=+0.002409 CI=[+0.001551,+0.003208]  MSE diff=+0.002320 CI=[+0.001740,+0.002895]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

--- arm2_raw_own (stratifier: abs_own) ---
  low  (n= 3586, 641 pos, mean SE=0.0720)  MAE diff=-0.002727 CI=[-0.003809,-0.001736]  MSE diff=-0.001722 CI=[-0.002307,-0.001159]
  mid  (n= 3585, 648 pos, mean SE=0.0751)  MAE diff=+0.000136 CI=[-0.000734,+0.001044]  MSE diff=+0.000129 CI=[-0.000325,+0.000619]
  high (n= 3586, 616 pos, mean SE=0.1156)  MAE diff=+0.001726 CI=[+0.000753,+0.002595]  MSE diff=+0.002172 CI=[+0.001509,+0.002807]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

--- arm3_eb_shrunk (stratifier: abs_eb) ---
  low  (n= 3586, 647 pos, mean SE=0.1045)  MAE diff=-0.002610 CI=[-0.003632,-0.001575]  MSE diff=-0.001623 CI=[-0.002195,-0.001038]
  mid  (n= 3585, 647 pos, mean SE=0.0795)  MAE diff=-0.000107 CI=[-0.001023,+0.000825]  MSE diff=+0.000003 CI=[-0.000470,+0.000491]
  high (n= 3586, 613 pos, mean SE=0.0788)  MAE diff=+0.001851 CI=[+0.000987,+0.002706]  MSE diff=+0.002199 CI=[+0.001606,+0.002807]
       high-stratum verdict: MAE HOLD (CI_lo>0: ESM-2 worse) | MSE HOLD (CI_lo>0)

stratum membership agreement (fraction of rows in same tercile):
  arm1 vs arm2 (own-vs-published switch): 0.822  (rows entering/leaving the high stratum: 712)
  arm2 vs arm3 (shrinkage alone): 0.893  (rows entering/leaving the high stratum: 724)
  arm1 vs arm3 (total change vs 6.3): 0.781  (rows entering/leaving the high stratum: 1056)

arm1 high-stratum MAE verdict (gated replication of 6.3): HOLD (CI_lo>0: ESM-2 worse)
arm2 high-stratum MAE verdict (own_e_b switch control):   HOLD (CI_lo>0: ESM-2 worse)
arm3 high-stratum MAE verdict (EB-shrunken):            HOLD (CI_lo>0: ESM-2 worse)
arm3 high-stratum MSE verdict:                           HOLD (CI_lo>0)

D1b VERDICT (pre-registered, arm3 MAE CI): UNCHANGED-HOLD — 6.3's high-stratum verdict is HOLD on arm1
Saved /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task50_d1b_eb_restrat.csv + _agreement.csv
```
Verdict:
- UNCHANGED-HOLD at the pre-registered bar. The task's question ("see if the high-stratum verdict changes") resolves: it does NOT. Arm3's high-stratum MAE diff +0.001851 CI [+0.000987, +0.002706] and MSE diff +0.002199 CI [+0.001606, +0.002807] both exclude zero in the ESM-worse direction — same direction, overlapping magnitude as 6.3's original (+0.002409 MAE / +0.002320 MSE).
- The decisive detail tying this to D1a: shrinkage does exactly what the winner's-curse concern predicts mechanically — high-SE estimates shrink most (factor min 0.003), so the high stratum's mean SE drops from 0.1166 to 0.0788 (−32%, now barely above the original low stratum's 0.0705), and the EB strata's SE gradient INVERTS (EB-low = 0.1045 is now the noisiest stratum: heavily-shrunk noisy estimates collapse toward zero and land in the LOW tercile). The 6.3 verdict survives in a high stratum that has been purged of the D1a enrichment. That is the strongest form of "the verdict doesn't ride on the noise."
- Substantial real movement, so the robustness is not cosmetic: 1,056 of 10,757 rows (9.8%) change high-stratum membership between arm1 and arm3 (agreement 0.781); shrinkage alone moves 724 (agreement 0.893 vs arm2). The verdict held through that churn.
- Arm2 (own-vs-published switch control): HOLD as well (+0.001726 [+0.000753, +0.002595]) — the verdict does not depend on which of the two near-identical e.b columns (rho 0.975) defines the strata; agreement 0.822 quantifies the switch, as pre-registered, so arm3-vs-arm2 isolates shrinkage alone.
- Effect size alongside significance (AGENTS §3): arm3's high-stratum MAE diff (+0.001851) is 77% of the original arm1 value (+0.002409) — a modest shrinkage of the effect, not an erosion of it; its CI excludes zero comfortably at full N.
- Independent cross-check that the machinery is right: arm1's MSE CI [+0.001740, +0.002895] reproduces script 46's C2c published MSE CI EXACTLY (same rows, same seed, local MSE helper mirrors 46's), and G2 is 0.000e+00.
- Limits (printed by the script): EB prior is a single global τ² (method of moments), not covariate-dependent; stratum labels fixed within bootstrap draws (C2c convention); a bimodal or heavy-tailed e.b prior could shrink differently — one global variance is the simplest defensible choice and was pre-registered.
Files created/modified: data/processed/task50_d1b_eb_restrat.csv, data/processed/task50_d1b_eb_agreement.csv (new), script shared with D1a/D1c (scripts/50_d1_stratifier_quality.py, uncommitted), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- τ² came out solidly positive (0.035890), so the pre-registered EB-DEGENERATE branch did not trigger; the degenerate contingency remains in the script, untested by data.
- The shrink factor's minimum (0.003) shows some estimates shrink to near nothing — those rows' tercile placement in arm3 is driven by residual tiny values (ties risk in qcut did not materialize: all three strata came out 3,585-3,586 rows at every arm).
- Read D1a and D1b together, not separately: D1a says the old stratifier WAS biased toward noise; D1b says 6.3's conclusion does not depend on that bias. Reporting D1a alone would leave the false impression 6.3 is damaged; reporting D1b alone would hide a real stratifier defect.
- No contradiction with MTHFR_RESULTS_LOG: arm1 reproduces 6.3 exactly (G2 = 0.000e+00; MSE CI matches C2c byte-for-byte), so nothing in the log changes; the EB re-stratification is a new robustness result beside it.
---

## D1c — Nonsense-variant noise floor alongside the synonymous floor
Status: PASS — two pre-registered verdicts: (1) HETEROSCEDASTICITY HIGHER: sd(e.b|nonsense) = 1.184 × sd(e.b|synonymous), CI [1.025, 1.371] excludes 1 — the review's premise (noise differs at the dead end of the fitness range) is confirmed; (2) FLOOR NOT CLEARED: the entry bar into 6.3's high tercile (cut23 = 0.1830) is only 1.064 × the nonsense noise SD, CI [0.948, 1.207] — far below the pre-registered 2-SD bar, and statistically indistinguishable from ONE dead-end-noise SD (CI includes 1.0).
Time started / finished: same run as D1a/D1b (scripts/50_d1_stratifier_quality.py), full run finished 2026-09-22 07:11, N_BOOT=2000 (11.6 s wall for all three).
What I did:
1. Data: script 35's full table (task35_epistatic_set.csv, 13,134 rows — counts gated: 11,902 substitution / 624 nonsense / 608 synonymous), NOT the 6.3 set: phase5's model_C/target exist only for missense rows, so the 6.3 analysis set contains zero nonsense/synonymous by construction (verified by gate — printed as a gate, not discovered mid-run). The floor lives in e.b space, where all three types exist.
2. Row accounting (AGENTS §5): analysis requires own_e_b AND se_e_b non-null → 11,865 of 13,134 rows survive; drops: 1,145 substitution, 38 synonymous, 86 nonsense (rows where the WLS fit could not produce e.b/SE — the same mechanism as A2a's e.b-observability exclusions). The surviving 10,757 missense rows are VERIFIED identical to the 6.3 s-set (hgvs symmetric difference = 0) — one more exact link in A2b's n-chain.
3. Pre-registered statistics: PRIMARY R = sd(e.b|nonsense)/sd(e.b|synonymous), position-cluster bootstrap over the pooled syn+nonsense positions (both types' rows travel with their position); verdict HIGHER iff CI_lo > 1, LOWER iff CI_hi < 1, else NOT DETECTED (explicitly not proof of equality). SECONDARY floor ratio = cut23(|own_e_b| on missense) / sd(nonsense), numerator and denominator each position-cluster-bootstrapped; verdict FLOOR CLEARED iff CI_lo > 2, NOT CLEARED iff CI_hi < 2, else INCONCLUSIVE. Cross-check: epistatic_N2 pass rate per type (script 35's criterion at N=2).
Actual output (real numbers, not a paraphrase):
```
  synonymous             n=  570  sd(e.b)=0.1453  median SE=0.0387  p95|e.b|=0.3088  calib sd/medianSE=3.76  epistatic_N2 pass=44.7%
  nonsense               n=  538  sd(e.b)=0.1720  median SE=0.0780  p95|e.b|=0.4284  calib sd/medianSE=2.21  epistatic_N2 pass=14.5%
  missense (reference)   n=10757  sd(e.b)=0.2409  median SE=0.0629  p95|e.b|=0.5278  calib sd/medianSE=3.83  epistatic_N2 pass=44.8%

PRIMARY R = sd(e.b|nonsense)/sd(e.b|synonymous) = 1.184  CI=[1.025, 1.371]  (2000/2000 valid)
D1c HETEROSCEDASTICITY VERDICT (pre-registered): HIGHER (nonsense noise > synonymous)

SECONDARY floor comparison: cut23(|own_e_b|, missense) = 0.1830 / sd(nonsense) = 0.1720  ->  ratio 1.064  CI=[0.948, 1.207]
D1c FLOOR VERDICT (pre-registered): NOT CLEARED (CI_hi < 2)
Saved /Users/arnavchavan/Desktop/mthfr-context-dependence/data/processed/task50_d1c_nonsense_floor.csv
```
Verdict:
- HIGHER, at the pre-registered bar: the review's premise is right — noise is heteroscedastic across the fitness range. Dead-end (nonsense) e.b spread is 18.4% larger than synonymous spread (0.1720 vs 0.1453), CI [1.025, 1.371] excludes 1. Effect size alongside significance (AGENTS §3): the ratio is the effect; it is modest (1.18×), not an order-of-magnitude difference — a second noise floor, not a different noise regime.
- The floors themselves, side by side (the deliverable): synonymous floor sd = 0.1453 (p95|e.b| = 0.3088), nonsense floor sd = 0.1720 (p95|e.b| = 0.4284). Both are computed at variant types whose TRUE interaction is ≈0, so these are empirical noise magnitudes at opposite ends of the fitness range — no model assumption beyond "dead in both backgrounds" (nonsense) / "identical protein" (synonymous).
- FLOOR NOT CLEARED for6.3's stratifier: the entry bar into the high tercile (cut23 = 0.1830) sits at 1.064 × sd(nonsense), CI [0.948, 1.207] — the CI includes 1.0, meaning the high-tercile entry bar is statistically indistinguishable from ONE dead-end-noise SD, and is nowhere near the pre-registered 2-SD bar. Read with D1b (verdict survives) this constrains interpretation, not verdicts: variants barely into the "high interaction" tercile cannot be distinguished from dead-end noise on magnitude alone — claims about the HIGH stratum as a whole should lean on D1b's shrunken re-stratification, which re-sorts exactly those borderline rows.
- IMPORTANT scope limit, stated because this could be over-read: the floors live at the fitness-range extremes (nonsense ≈ dead, synonymous ≈ WT-like) while the missense strata sit at intermediate fitness — that is the design's point (heteroscedasticity check at the opposite end) AND the reason the ratio is not apples-to-apples with intermediate-fitness noise. The floor comparison bounds interpretation; it does not re-derive missense noise.
- Cross-check worth flagging: the synonymous calibration ratio recomputes to 3.76 (sd/median analytic SE) — EXACTLY the empirical factor J4a/script 35 refer to — while nonsense calibrates at 2.21 and missense at 3.83: the analytic SE's miscalibration is itself type-dependent, which is a direct empirical argument for J4's FDR-per-type approach over one global 3.76× inflation.
- Striking cross-check (recorded, not promoted to a finding): at script 35's N=2 threshold, missense pass rate (44.8%) is essentially identical to the synonymous FPR (44.7%) — i.e., at N=2 the "epistatic set" passes missense at exactly the noise rate, while nonsense passes at only 14.5% (nonsense median SE is 2× synonymous, so fewer pass |z|>2). This is script 35's criterion read at one level (N=2); the full N-level table lives in script 35's own output.
Files created/modified: data/processed/task50_d1c_nonsense_floor.csv (new), script shared with D1a/D1b (scripts/50_d1_stratifier_quality.py, uncommitted), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Smoke run caught a REAL bug before the full run, disclosed per AGENTS §6: the floor-ratio bootstrap's denominator used sd(|nonsense e.b|) (absolute values) while the point estimate used sd(signed e.b) — the CI [1.190, 1.564] excluded its own point estimate 1.064. The pre-registered statistic says "cut23 / sd(nonsense)" (signed), so the code had deviated from the docstring; fixed to signed before the full run. This was a construction bug found by the sanity observation "CI must contain the point estimate," not a result-driven change — no verdict moved (NOT CLEARED both before and after; only the CI numbers changed).
- Dropped-row accounting is asymmetric by type: nonsense loses 13.8% (86/624) to non-computable SE vs synonymous 6.2% (38/608) — the dead-end rows are harder to fit, so the surviving nonsense floor may be slightly SELECTED toward fitter-feasible rows; the floor is therefore (if anything) an UNDERestimate of dead-end noise, which makes NOT CLEARED conservative.
- The 38/86 dropped rows are reported here rather than silently absorbed: every filter step's counts are printed by the script's gated output (13,134 → 11,865 with the per-type breakdown shown above).
- No contradiction with MTHFR_RESULTS_LOG (no nonsense-floor content there); the 3.76 synonymous calibration ratio AGREES with the figure J4a quotes, and the type-dependence (2.21 / 3.76 / 3.83) is new evidence FOR J4b's "does the ratio vary?" question — answered yes, it varies by variant type.
---

## F1a — Nonlinear fitness control on 3.1's multivariable model [item 21a]
Status: PASS (test ran, gate identity check passed) — pre-registered verdict: CHANGED (GI_folinate_independent binned-spec COEF ROBUST in 1/2 error metrics).
Time started / finished: 2026-09-22 09:36:04 → 09:37:40 full run (N_BOOT=10000; F1a itself is OLS, no bootstrap), smoke (N_BOOT=200) immediately before.
What I did:
1. New script `scripts/51_f1_control_specification.py`, section F1a: re-runs proposal 5.6e / results-log 3.1's exact model (`scripts/18_multivariable_controls.py` spec: z-scored [abs_ctx, f_bar, grantham, blosum62, rsa] + domain dummies, OLS, cluster-robust SE by position, z-scored outcome, phase3_analysis_table n=11,901 loaded) with base fitness entered NONLINEARLY: PRIMARY = f_bar decile dummies (drop-first), SENSITIVITY = f_bar + f_bar² quadratic.
2. Pre-registered (in docstring, before any run): GATE = linear re-run must reproduce tier2_multivariable.csv coefs/CIs to 1e-6 with n match for all 6 models, else FAIL/no-retry; per-model COEF ROBUST = binned coef same sign as linear AND 95% cluster CI excludes 0 in same direction; headline SURVIVES NONLINEAR CONTROL iff COEF ROBUST for GI_folinate_independent in BOTH error metrics, else CHANGED.
3. Gate result: all 6 models OK — max|coef/ci diff| = 2.4e-17 … 9.0e-17, n match True (identity check, exact to floating point).
Actual output (real numbers, not a paraphrase):
```
rank-based error ~ |GI_folinate_independent| (sequence-encoded genetic)  n=9756 pos=596
  GATE linear vs tier2_multivariable.csv: max|coef/ci diff|=2.43e-17  n_match=True  -> OK
  linear f_bar    coef=+0.0521 CI=[+0.0245,+0.0797] p=0.0002115 r2=0.0524
  decile-binned   coef=+0.0573 CI=[+0.0303,+0.0842] p=3.168e-05 r2=0.0839
  quadratic        coef=+0.0664 CI=[+0.0391,+0.0936] p=1.883e-06 r2=0.0664
  -> binned COEF ROBUST: True   quadratic COEF ROBUST: True

calibrated error ~ |GI_folinate_independent| (sequence-encoded genetic)  n=9756 pos=596
  GATE linear vs tier2_multivariable.csv: max|coef/ci diff|=6.25e-17  n_match=True  -> OK
  linear f_bar    coef=-0.0590 CI=[-0.0851,-0.0330] p=8.888e-06 r2=0.0315
  decile-binned   coef=+0.0537 CI=[+0.0352,+0.0723] p=1.41e-08 r2=0.5239
  quadratic        coef=+0.0271 CI=[+0.0085,+0.0456] p=0.004191 r2=0.5406
  -> binned COEF ROBUST: False   quadratic COEF ROBUST: False

F1a VERDICT (pre-registered): CHANGED -- GI_folinate_independent binned-spec COEF ROBUST in 1/2 error metrics
Saved .../data/processed/task51_f1a_nonlinear_fitness.csv
```
(other 4 models: rank/folinate_response linear +0.0100 [-0.0097,+0.0297] → decile -0.0011 [-0.0196,+0.0174] not robust; rank/GI_dependent +0.0592 → decile +0.0424 [+0.0162,+0.0686] robust; cal/folinate_response +0.0017 [-0.0224,+0.0259] → decile +0.0307 [+0.0087,+0.0528] linear CI covered 0 → rule False; cal/GI_dependent +0.0542 → decile +0.0539 [+0.0374,+0.0705] robust)
Verdict:
- CHANGED by the pre-registered letter: the calibrated-metric GI_folinate_independent coefficient FLIPS SIGN under both nonlinear specs (linear -0.0590 → binned +0.0537, quadratic +0.0271), so "same sign as linear" fails in 1/2 metrics. The rank metric is robust and even grows (+0.0521 → +0.0573 binned, +0.0664 quadratic).
- Direction of the change matters and is reported, not spun: under correct functional form BOTH metrics are positive and nearly equal (+0.0573 rank / +0.0537 binned-calibrated), CIs exclude 0 in both (p=3.2e-05 / 1.4e-08). 3.1's published survival criterion ("CI excludes zero in both error metrics") therefore still holds under the nonlinear control; what fails is the published NEGATIVE calibrated sign.
- Mechanism visible in the fit itself: r2 for the calibrated-error models jumps 0.03 → 0.52-0.57 when fitness enters nonlinearly (linear 0.0315 → binned 0.5239 for GI_indep). The linear f_bar term was absorbing almost none of the (strongly curved) fitness→calibrated-error relationship, so its coefficient was misspecified. This EMPIRICALLY CONFIRMS the open follow-up already written in script 22/RESULTS.md: "the rank-vs-calibrated sign disagreement in the Phase 3 central-error results was never explained. Pooled calibration across heterogeneous fitness ranges is now a concrete candidate" — the candidate holds up under direct test (the follow-up text predates this test; the binned-vs-quadratic spec pair was pre-registered here before running).
- Effect sizes with significance (AGENTS §3): binned GI_indep coefs +0.0573/+0.0537 SD-error/SD-context — same order as the published +0.0521, not larger; the finding's size is stable, its calibrated sign was the artifact of linear control.
- Observation (not promoted to a claim): cal/folinate_response moves from null (+0.0017, CI covers 0) to significant (+0.0307 [+0.0087,+0.0528]) under binned control — same misspecification absorbing its variance; flagged for whoever owns the 3.1 narrative, no verdict attached here.
Files created/modified: scripts/51_f1_control_specification.py (new, uncommitted), data/processed/task51_f1a_nonlinear_fitness.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Smoke run caught a KeyError (verdict block looked GI coefs up by err_col against a dict keyed by err_lbl) BEFORE F1b ran; fixed and both sections re-run clean (EXIT=0). Disclosed per AGENTS §6 — bug was in presentation code after all model fits; no model or gate was touched by the fix.
- The GATE (exact reproduction of tier2_multivariable.csv) passed to ~1e-17, independently confirming tier2_multivariable.csv corresponds to the current phase3_analysis_table.csv (column-identity/consistency check, AGENTS §5).
- No contradiction with MTHFR_RESULTS_LOG: 3.1's stated numbers (+0.0521 / -0.0590, both CIs exclude 0) reproduce exactly; the new information is what nonlinear control does to them. Nothing in the log is edited (read-only).
---

## F1b — 10th–90th percentile restriction of w.fitness (proposal 5.6c) [item 21b]
Status: PASS — pre-registered verdict: HOLDS (rank-based=HOLDS, calibrated=HOLDS; all 4 CI checks pass).
Time started / finished: same run as F1a (scripts/51_f1_control_specification.py, section F1b), 2026-09-22 09:36:04 → 09:37:40, N_BOOT=10000 (position-cluster bootstrap; 6 bootstraps, whole script 96 s wall).
What I did:
1. AMBIGUITY, logged per AGENTS §9: the original proposal 5.6c text does not exist anywhere in the repo (grep "5.6c"/"percentile" over docs/, scripts/, notebooks/ → only REVIEW_TRIAGE.md line 171 itself). Most conservative reading applied: restrict the analysis population to w.fitness ∈ [p10, p90] and re-run the SURVIVING central-error results of results-log Part 3 — (a) the raw |GI_folinate_independent| → central-error association (both metrics, position-cluster bootstrap) and (b) its multivariable controls (3.1's model, linear spec so the published tier2 row is the counterpart). Pre-registered rule: per metric, HOLDS iff restricted CI excludes 0 with the SIGN OF THE PUBLISHED COUNTERPART (task_region_check.csv pooled rho for raw; tier2_multivariable.csv GI_indep coef for multivariable); headline HOLDS iff both metrics pass both checks.
2. w.fitness = the ATLAS's own raw column (folate_response_model5.csv "w.fitness", joined hgvs→hgvs_pro), NOT f_bar — design-time check: corr(f_bar, w.fitness)=0.90 but max|diff| up to 2.85, so they are not interchangeable; the review says w.fitness, the raw column was used.
3. One cut, computed once on the analysis population (non-null abs_gi + BOTH central errors + matched w.fitness), applied unchanged to both analyses. Row accounting (AGENTS §5) printed at every step.
Actual output (real numbers, not a paraphrase):
```
abs_gi + both-errors population: 10757 rows / 654 positions
w.fitness matched: 10757  unmatched: 0
cut p10=0.000000 p90=1.337150  below=561 above=1076  kept=9120
  skew check abs_gi: kept mean=+0.1619  excluded(n=1637) mean=+0.2613
  skew check central_error_rank: kept mean=+2830.6182  excluded(n=1637) mean=+3621.6518
  skew check central_error_cal: kept mean=+0.2217  excluded(n=1637) mean=+0.3855

rank-based: raw |GI_folinate_independent| association
  reproduction check: base rho=+0.116464 published(task_region_check)=+0.116464  |diff|=2.78e-17  n=10757 (published n=10757)
  unrestricted(matched) n=10757 pos=654 rho=+0.1165 CI=[+0.0891,+0.1436] p=<0.0001
  restricted p10-p90    n= 9120 pos=654 rho=+0.1199 CI=[+0.0901,+0.1485] p=<0.0001
  raw restricted: same sign as published=True CI excludes 0=True -> PASS
  multivariable unrestricted(matched) n= 9756 coef=+0.0521 CI=[+0.0245,+0.0797] p=0.0002115
  multivariable restricted p10-p90    n= 8275 coef=+0.0621 CI=[+0.0312,+0.0929] p=7.992e-05
  multivariable published(tier2): coef=+0.0521 CI=[+0.0245,+0.0797] n=9756
  multivariable restricted: same sign as published=True CI excludes 0=True -> PASS

calibrated: raw |GI_folinate_independent| association
  reproduction check: base rho=-0.133817 published(task_region_check)=-0.133817  |diff|=5.55e-17  n=10757 (published n=10757)
  unrestricted(matched) n=10757 pos=654 rho=-0.1338 CI=[-0.1624,-0.1053] p=<0.0001
  restricted p10-p90    n= 9120 pos=654 rho=-0.1776 CI=[-0.2087,-0.1465] p=<0.0001
  raw restricted: same sign as published=True CI excludes 0=True -> PASS
  multivariable unrestricted(matched) n= 9756 coef=-0.0590 CI=[-0.0851,-0.0330] p=8.888e-06
  multivariable restricted p10-p90    n= 8275 coef=-0.0861 CI=[-0.1150,-0.0571] p=5.77e-09
  multivariable published(tier2): coef=-0.0590 CI=[-0.0851,-0.0330] n=9756
  multivariable restricted: same sign as published=True CI excludes 0=True -> PASS

F1b VERDICT (pre-registered): HOLDS -- per-metric: rank-based=HOLDS, calibrated=HOLDS
Saved .../data/processed/task51_f1b_percentile.csv
```
Verdict:
- HOLDS on all four pre-registered checks. Effect sizes alongside significance (AGENTS §3): the restriction does not attenuate anything — the calibrated association STRENGTHENS (raw rho -0.1338 → -0.1776, ~33% larger; multivariable coef -0.0590 → -0.0861) while rank stays flat-to-slightly-up (+0.1165 → +0.1199; +0.0521 → +0.0621). The result is not an artifact of the fitness-range extremes; removing them makes it bigger on the calibrated metric.
- Reproduction checks pass to machine precision (|diff| ≤ 5.55e-17 vs task_region_check.csv, n identical), so the unrestricted rows are exactly the published analysis set — the restriction is the only thing that changed (single-variable comparison, AGENTS §5 n-reconciliation).
- Skew disclosure (AGENTS §5): the excluded 1,637 rows are NOT random — they carry higher |GI| (0.2613 vs 0.1619) and higher errors (cal 0.3855 vs 0.2217). The cut removes exactly the extreme-deleterious region where both context and error concentrate; that the association survives (and strengthens) under that loss of leverage is the conservative direction of this test.
- Cut detail worth recording: p10 = 0.000000 exactly (atlas w.fitness has a pile-up at/below 0: 561 rows are strictly negative and are the entire "below" group; rows sitting exactly at 0 are kept by ≥p10). p90 = 1.337150, above = 1,076. Kept 9,120 of 10,757 (84.8%); multivariable restricted n = 8,275 of 9,756 (84.8%).
- unmatched = 0 at this stage: design-time probing had found 456 phase3 rows without raw w.fitness, but ALL of them also lack GI_folinate_independent (checked: non-null GI count among unmatched = 0), so they had already exited via the abs_gi dropna — join loss and analysis-set membership are disjoint here. Accounted for, not silently absorbed.
- No contradiction with MTHFR_RESULTS_LOG: unrestricted reproductions match published numbers exactly; the restriction itself was never run before (this is the first execution of 5.6c's test under the logged reading).
Files created/modified: scripts/51_f1_control_specification.py (shared with F1a, uncommitted), data/processed/task51_f1b_percentile.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- The pre-registered reading of "5.6c" is an assumption (text absent). If the intended target was a DIFFERENT surviving result (e.g., the 6.x MAE family), this entry does not cover it; the assumption is logged here so a morning re-read can re-point it without re-running anything else.
- p10 landing exactly at 0.0 means the "10th–90th percentile" phrase, applied literally, functions as "drop negative-fitness rows + drop top decile" — recorded because a reader may expect a nonzero lower cut.
- Full run used N_BOOT=10000 (no resolution reduction needed: timed small-N extrapolation predicted ~82 s for the six bootstraps; actual whole-script wall 96 s).
---

## F2a — Region-2 recalibration overfit check: was 4.3's within-region isotonic cross-fitted WITHIN region? [item 22]
Status: PASS (verdict: CONFIRMED-WITHIN-REGION — all pre-registered gates green)
Time started / finished: 2026-09-22 09:39 / 2026-09-22 09:43
What I did:
1. Pre-registered in scripts/52_f2a_within_region_audit.py docstring: CHECK 1 source audit of `crossfit_isotonic_within_group` (must subset to group BEFORE by_position, and by_position must hold out positions); CHECK 2 identity tests — 2a: within-region predictions bit-identical (<1e-12) to per-region-by-position fits, 2b: within-region ≠ pooled (>1e-6); CHECK 3: re-derive all 8 published 4.3 constants within |delta|≤0.01 plus sign pattern. Verdict CONFIRMED-WITHIN-REGION iff 2a+2b+constants+sign all pass, else DIVERGENT (exit 1).
2. Smoke run (N_BOOT=100) first. CHECK 1 initially FAILed — a bug in my own matcher (see "unexpected" below), fixed before any numeric check ran; re-ran smoke: all checks green.
3. Full run N_BOOT=2000, foreground, 4 s wall (no resolution reduction needed).
4. Also re-confirmed provenance: scanned scripts/ for any writer of task_region2_diagnostic.csv (0 writers), CSV absent on disk, RESULTS.md lacks the table.
Actual output (real numbers, not a paraphrase):
```
Analysis frame: 11344 variants, 654 positions
region counts: {1.0: 2652, 2.0: 2551, 3.0: 2933, 4.0: 3208}
positions per region: {1.0: 146, 2.0: 146, 3.0: 180, 4.0: 182}

CHECK 1: source audit
def crossfit_isotonic_within_group(df, position_col, score_col, target_col,
                                   group_col, n_folds=5, seed=0):
    preds = pd.Series(np.nan, index=df.index, dtype=float)
    for g, sub in df.groupby(group_col):
        if sub[position_col].nunique() < n_folds * 2:
            continue
        preds.loc[sub.index] = crossfit_isotonic_by_position(
            sub, position_col, score_col, target_col, n_folds=n_folds, seed=seed)
    return preds

  -> subsets to group BEFORE calling by_position: True
  -> by_position holds out POSITIONS (train excludes test fold): True

CHECK 2: identity checks
  2a max|within - per-region-by-position| = 0.000e+00  (gate < 1e-12)  -> OK
  2b max|within - pooled-by-position|      = 2.590e-01  (gate > 1e-6)   -> OK

CHECK 3: re-derivation of results-log 4.3 (three calibration schemes)
pooled     x=abs_gi   pooled=+0.0894 regions={1: +0.0867, 2: -0.1172, 3: +0.1893, 4: +0.1154}  <- published target
pooled     x=abs_own  pooled=+0.1483 regions={1: +0.1481, 2: -0.1043, 3: +0.2662, 4: +0.1908}
stratified x=abs_gi   pooled=+0.0891 regions={1: +0.0888, 2: -0.1162, 3: +0.1916, 4: +0.1121}  <- published target
stratified x=abs_own  pooled=+0.1481 regions={1: +0.1496, 2: -0.1041, 3: +0.2682, 4: +0.1885}
within     x=abs_gi   pooled=+0.1897 regions={1: +0.1622, 2: +0.0707, 3: +0.1632, 4: +0.1834}  <- published target
within     x=abs_own  pooled=+0.2494 regions={1: +0.2021, 2: +0.0667, 3: +0.2474, 4: +0.2986}

  published-constant deltas (tolerance |delta| <= 0.01):
    region2_pooled       derived=-0.1172  published=-0.1120  |delta|=0.0052  -> OK
    region2_stratified   derived=-0.1162  published=-0.1120  |delta|=0.0042  -> OK
    pooled_pooled        derived=+0.0894  published=+0.0900  |delta|=0.0006  -> OK
    pooled_within        derived=+0.1897  published=+0.1910  |delta|=0.0013  -> OK
    within_r1            derived=+0.1622  published=+0.1630  |delta|=0.0008  -> OK
    within_r2            derived=+0.0707  published=+0.0750  |delta|=0.0043  -> OK
    within_r3            derived=+0.1632  published=+0.1610  |delta|=0.0022  -> OK
    within_r4            derived=+0.1834  published=+0.1860  |delta|=0.0026  -> OK
  sign pattern (region2 pooled<0, region2 within>0, pooled rises): OK

PROVENANCE: who writes task_region2_diagnostic.csv?
  writers found: 0  -> NONE
  CSV present on disk: False
  RESULTS.md contains the region-2 table: False

F2a VERDICT (pre-registered): CONFIRMED-WITHIN-REGION (identity 2a/2b pass, constants within 0.01: True, sign pattern: True)

within-region pooled rho cluster bootstrap (N_BOOT=2000): rho=+0.1897 CI=[+0.1597,+0.2188] n=10757 pos=654
Saved .../data/processed/task52_f2a_within_region.csv

LIMITATIONS (script is the record, AGENTS 6): the ORIGINAL script that produced task_region2_diagnostic.csv is missing from the repo (no writer exists; CSV absent; RESULTS.md lacks the table because script 22 skips it when the CSV is missing). This audit therefore identifies the mechanism by RE-DERIVATION: the within-group library function reproduces every published constant to <=0.01, which is strong evidence but not a reading of the lost historical code. Nonzero deltas may reflect data drift in phase5_analysis_table.csv since the original run. n_folds=5, seed=0 assumed (the values match; other settings were not searched).
```
Verdict:
- CONFIRMED-WITHIN-REGION. The calibration IS cross-fitted within region: `crossfit_isotonic_within_group` subsets each region before delegating to the position-held-out fitter, so every held-out prediction comes from a model trained only on OTHER POSITIONS OF THE SAME REGION. Identity 2a is exact to 0.000e+00 (within-region predictions are bit-identical to an explicit per-region-by-position refit), and 2b confirms the mechanism is distinguishable from pooled (max diff 0.259 > 1e-6). The overfitting concern in the review ("fewer positions per region = more overfitting room") is therefore live but bounded by the position-holding-out: no held-out variant's own position is in its calibration's training set, within its region or without.
- Effect size alongside significance (AGENTS §3): the audit's own bootstrap — within-region pooled rho = +0.1897, CI [+0.1597, +0.2188], n=10,757 across 654 positions, position-clustered — reproduces the published +0.191 and excludes 0 comfortably.
- All 8 published 4.3 constants reproduced within 0.01 (max |delta| = 0.0052), including the load-bearing ones: region 2 flips sign (pooled −0.1172 → within-region +0.0707; published −0.112 → +0.075) and pooled correlation nearly doubles (+0.0894 → +0.1897; published +0.090 → +0.191).
- Provenance caveat carried from design phase and written into the script's own output: the original producing script for task_region2_diagnostic.csv does not exist anywhere in the repo (0 writers found by scan), the CSV is absent, and RESULTS.md lacks the table because script 22 skips it when the CSV is missing. The mechanism claim rests on re-derivation (library function matches every published constant), not on reading the lost historical code — logged as a limitation, not as BLOCKED, because re-derivation directly answers the review's question ("was it cross-fitted within region?": the only code that exists does exactly that, to 0.000e+00 against an explicit within-region refit).
- No contradiction with MTHFR_RESULTS_LOG 4.3: every constant it prints is reproduced within tolerance.
Files created/modified: scripts/52_f2a_within_region_audit.py (new, uncommitted), data/processed/task52_f2a_within_region.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Smoke-stage bug in my own CHECK 1 (disclosed, AGENTS §7): the subset-first matcher used the same-line literal `"crossfit_isotonic_by_position(sub"` but the audited call is wrapped across two lines, so it reported False and the script exited 1 before any numeric check had run. The printed source in that same output showed subset-first was actually happening. Fixed by whitespace-normalizing both sources before the literal checks (purely mechanical; the printed source remains the ground truth). This is a pre-run smoke fix of a matcher, not a modification of a test to change a result — but it is disclosed because a strict reading of "sanity-check failure = FAIL, no retry" would have caught it; the distinction is that the check was broken, not the data, and no result had been computed yet.
- Nonzero deltas (up to 0.0052) despite bit-identical mechanism: the published numbers were computed at some earlier data state; current phase5_analysis_table.csv drifts them slightly. All within the pre-registered 0.01 tolerance either way.
- n_folds=5, seed=0 are assumed defaults matching the values; other fold/seed settings were not searched (values match, so this is the parsimonious reading).
---

## G1 — Global vs. specific epistasis decomposition: how much of e.b does w.fitness alone explain? [item 23]
Status: PASS (PART 1 verdict: LIMITED-GLOBAL — the "if most of it" premise is NOT met; PART 2 verdict: SURVIVES — ESM-2 predicts the specific residual, and the signal STRENGTHENS)
Time started / finished: 2026-09-22 09:44 / 2026-09-22 09:50
What I did:
1. Pre-registered in scripts/53_g1_global_specific_epistasis.py docstring: PART 1 primary statistic = cross-fitted isotonic R² of e.b on atlas w.fitness (house `crossfit_isotonic_by_position`, n_folds=5, seed=0, held-out POSITIONS), with variance-share bands fixed BEFORE running (≥0.50 MOST-GLOBAL / ≥0.25 SUBSTANTIAL-GLOBAL / else LIMITED-GLOBAL — the conservative reading of the review's "if most of it"); linear R² and in-sample isotonic ceiling reported for context; position-cluster bootstrap CI on the fixed held-out predictions.
2. PART 2 pre-registered: residual = e.b − cross-fitted prediction (out-of-fold); Spearman(delta_ESM, residual) with position-cluster bootstrap CI + POSITION-level sign-flip association null on delta_ESM (N_PERM=10000, identity checks all-+1/all-−1 must reproduce ±observed to <1e-12 or exit 1); paired magnitude difference vs the raw-e.b association on the same rows. Verdict SURVIVES iff p<0.05 AND CI excludes 0; else NOT-DETECTED. No retuning.
3. Smoke (N_BOOT=100/N_PERM=200) surfaced three bugs in my own script, ALL fixed before any full run (disclosed below): wrong-direction ceiling, inverted plain-language label on the paired difference, broken reconciliation lookup.
4. Full run: N_BOOT=2000, N_PERM=10000, 19 s wall, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
phase5 rows: 11344
  non-null e.b + delta_esm: 10757  (dropped 587)
  + matched atlas w.fitness: 10757  (dropped 0)
Analysis set: 10757 variants, 654 positions

PART 1 (G1a): variance in e.b explained by a monotone function of w.fitness
  cross-fitted isotonic R^2 (PRIMARY)  = 0.1535   (out-of-sample)
  linear OLS R^2 (w.fitness, no nonlin) = 0.1079
  in-sample isotonic R^2 (CEILING)      = 0.1651  (optimistic)
  Spearman(w.fitness, e.b)              = -0.2393
  pre-registered band: R^2_cf -> LIMITED-GLOBAL  (>=0.50 MOST / >=0.25 SUBSTANTIAL / else LIMITED)
  cross-fitted R^2 cluster bootstrap (N_BOOT=2000): CI=[0.1317,0.1749]  (positions resampled, predictions fixed)

PART 2: does ESM-2 predict the SPECIFIC residual after global epistasis?
  residual: e.b - crossfit-isotonic(w.fitness); sd(resid)=0.2349 vs sd(e.b)=0.2554 (0.920 of raw scale)
  Spearman(delta_ESM, residual) = -0.1455  CI=[-0.1761,-0.1131]  p_boot=<0.000500  (cluster, N_BOOT=2000)
  Spearman(delta_ESM, raw e.b)   = -0.0707  (same rows, same set)
  reconciliation vs script 32 on-disk: value=-0.070705 n=10757  |diff|=6.94e-17
  paired magnitude difference |resid| - |raw|: +0.0748  CI=[+0.0585,+0.0912]  (both rhos negative in 2000/2000 draws)
    -> removing global epistasis STRENGTHENS the |delta_ESM| signal magnitude

  position-level sign-flip ASSOCIATION null on delta_ESM (10000 draws):
    identity: all+1 == obs (-0.145545737907), all-1 == -obs (+0.145545737907)  -> OK
    observed=-0.1455  null mean=+0.0001  sd=0.0186  p=<0.000100
    null-centring: mean IS consistent with zero (3 SE)
    pre-registered verdict: SURVIVES  (p<0.05: True; CI excludes 0: True)

Saved .../data/processed/task53_g1_global_specific.csv
```
Verdict:
- PART 1 (G1a): LIMITED-GLOBAL. A monotone nonlinear function of w.fitness alone explains 15.35% of e.b's variance out-of-sample (CI [0.1317, 0.1749]; linear-only 0.1079; optimistic in-sample ceiling 0.1651). The review's conditional — "If MOST of it [is explained], the atlas's interaction is substantially global/threshold epistasis" — does NOT trigger: 0.15 is far below even the 0.25 SUBSTANTIAL floor, and the cross-fitted value sits within 0.02 of the in-sample ceiling, so more flexible monotone fitting cannot rescue the premise (the ceiling bounds it). Global epistasis through w.fitness is REAL but is a minority (~15%) of what e.b measures; ~85% is not a monotone function of fitness.
- PART 2 (the fair test): SURVIVES, and in the direction that HELPS ESM-2. After removing the global component, Spearman(delta_ESM, residual) = −0.1455 (CI [−0.1761, −0.1131], position sign-flip p<0.0001, null centered at +0.0001) — versus −0.0707 on raw e.b. The paired magnitude difference is +0.0748 [CI +0.0585, +0.0912], both correlations negative in 2000/2000 draws. Removing global epistasis roughly DOUBLES the delta_ESM association (0.071 → 0.146), i.e. the global component was mostly noise for ESM-2's signal, not its source. Effect-size context (AGENTS §3): even the strengthened association is modest in absolute terms (|rho| ≈ 0.15, ~2% shared rank variance).
- Reconciliation (AGENTS §5): Spearman(delta_ESM, raw e.b) on this set matches script 32's on-disk published-e.b value to |diff| = 6.94e-17 with identical n=10,757 — same analysis set, no silent join loss (w.fitness join dropped 0 of 10,757; the initial 587 dropped are the non-null e.b/delta_esm requirement, identical to the established both-column set).
- Null type labeled (AGENTS §4): ASSOCIATION sign-symmetry randomization at position granularity (e.b and the cross-fitted calibration fixed), not re-derivation. It tests whether the signed pairing beats chance; it centers on zero by construction and does not rule out confounding.
- No contradiction with MTHFR_RESULTS_LOG: nothing there claims an R² figure for e.b~w.fitness (new analysis); the −0.0707 baseline it does contain (via script 32) is reproduced exactly.
Files created/modified: scripts/53_g1_global_specific_epistasis.py (new, uncommitted), data/processed/task53_g1_global_specific.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Three smoke-stage bugs in my own script, all fixed BEFORE the full run and all disclosed (AGENTS §7): (a) the in-sample ceiling used `increasing=True` while the house crossfit uses `increasing="auto"` — with Spearman(w.fitness, e.b) = −0.239 the relation is DECREASING, so the forced-increasing fit was near-flat (R²=0.0135, absurdly below the cross-fitted 0.1535); fixed to `increasing="auto"`, ceiling now 0.1651 ≥ crossfit as required. (b) The paired-difference label compared signed rhos, so both-negative correlations read "WEAKENS" when |rho| had grown; fixed to bootstrap the MAGNITUDE difference directly (sign stability verified: 2000/2000 draws both negative). (c) The script-32 reconciliation printed a missing column ("see CSV"); fixed to read the `quantity == 'signed, published e.b'` row. None of these touched a pre-registered decision rule or changed a verdict — the bands, statistics, and SURVIVES gate were fixed in the docstring before any run.
- The residual sd is 0.920× the raw e.b sd: the global component shrinks e.b's scale by only ~8%, consistent with the LIMITED-GLOBAL R² — the two parts of the script tell the same story independently.
- INTERPRETIVE NOTE for the morning: this refines rather than overturns. The reviewer's framing "if most of it [is global]… reframe the fair test" — the fair test was run anyway, and it comes out in FAVOR of ESM-2 having real (if small) specific signal. Combined with C1/G1, the honest picture is: ESM-2's specific signal exists (rho ≈ −0.15 after deconfounding) but is small, while the pipeline-validation I1 GATE FAIL means it should not be over-interpreted as calibrated epistasis prediction.
---

## H1a — Report S(A222V | WT) directly: does ESM-2 think A222V is deleterious? [items 25, 26]
Status: PASS (verdict: NEAR-NEUTRAL — ESM-2 does not flag A222V as deleterious)
Time started / finished: 2026-09-22 09:56 / 2026-09-22 10:04
What I did:
1. Pre-registered in scripts/54_h1_a222v_deleteriousness.py docstring: S(A222V|WT) = exact on-disk esm2_wt_scores row (position 222, A→V), no re-scoring; contextual stats on the same 12,445-row file; banding rule fixed before running (FLAGGED iff ≤ p10 of all scores; NEAR-NEUTRAL iff inside (p10, p90); BENIGN-TAIL iff ≥ p90 — the p10/p90 convention this project already uses in F1b).
2. Ran the script (both H1 sections; H1b logged as its own entry below).
Actual output (H1a section, real numbers, not a paraphrase):
```
H1a: S(A222V | WT) reported directly
  file rows: 12445
  S(A222V | WT) [p.Ala222Val] = -5.200276
  all-score p10 = -12.8005  p90 = -1.1867  mean = -7.3666  sd = 4.3120
  fraction of all substitutions scoring <= A222V (at least as deleterious): 0.6804
  z-score vs all: +0.502
  rank among position 222's substitutions (1=most deleterious): 16 of 19
  mildest substitution at 222: -1.8606 (p.Ala222Gly)
  pre-registered reading: NEAR-NEUTRAL
    (FLAGGED iff <= p10; NEAR-NEUTRAL iff inside (p10, p90); BENIGN-TAIL iff >= p90)
```
Verdict:
- NEAR-NEUTRAL per the pre-registered rule: S(A222V|WT) = −5.200276 sits inside (p10=−12.80, p90=−1.19); 68.0% of all 12,445 substitutions are at least as deleterious; z = +0.50 (slightly BENIGN of the all-score mean, remember more-negative = worse).
- Effect-size context (AGENTS §3): ESM-2 is not merely "not flagging" A222V — it ranks A222V the 16th most deleterious of the 19 substitutions at position 222 (i.e. 4th mildest). At position 222 ESM-2 sees mostly-benign substitutions across the board (mildest = Gly at −1.86).
- Supports the review's mechanistic reading directly: with the model scoring A222V as near-neutral-to-mildly-benign, "the model has no internal reason to propagate any correction from it" — a clean explanation for why delta_ESM effects must come from literal local context sensitivity rather than from the model representing A222V as a destabilizing event.
- No contradiction with MTHFR_RESULTS_LOG: it contains no claim about ESM-2's score for A222V itself.
Files created/modified: scripts/54_h1_a222v_deleteriousness.py (new, uncommitted, shared with H1b), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Disclosure (AGENTS §6): the score value −5.20 was visible during data inspection at design time; the BANDING rule (project-standard p10/p90) was written into the docstring before the run. The report itself has no degrees of freedom.
- The near-neutral reading is not knife-edge: −5.20 is far from both p10 and p90, so no reasonable alternative threshold (e.g. z-based) flips the band.
---

## H1b — Ortholog conservation at position 222 (phylogenetic/clade-cue alternative) [item 26]
Status: PASS (verdict: VAL-RARE in the sampled orthologs — the clade-cue alternative is NOT supported, with a small-n caveat)
Time started / finished: 2026-09-22 09:56 / 2026-09-22 10:04
What I did:
1. Pre-registered in script 54's docstring: fetch reviewed UniProt MTHFR-family entries (2-query union, see flag below), keep non-human sequences of length 400–800, global-align to human P42898 (BLOSUM62, affine gaps), map human residue 222 through the alignment; human self-check (P42898 must map back to A222, else exit 1); PRIMARY set identity ≥ 50%, SECONDARY ≥ 30%; "Val occurs commonly" read as V fraction ≥ 0.20 in the PRIMARY set (20% is an explicit assumption — "commonly" undefined in the review). Gap-at-222 rows are counted, not dropped.
2. Ran it (part of script 54; first run failed on an alignment-block unpack bug and a too-narrow fetch — both fixed before any conservation result existed; disclosed below).
Actual output (H1b section, real numbers, not a paraphrase):
```
H1b: ortholog conservation at position 222
  UniProt reviewed entries fetched (2-query union): 26 (saved to data/processed/task54_uniprot_mthfr.tsv)
  human self-check: P42898 maps back to A at 222 -> OK
  orthologs kept (length 400-800): 13  (fetched minus human minus out-of-range lengths)
  PRIMARY (identity >= 50%): n=3  V=0.000  A=1.000  -> VAL-RARE
    residue counts: A:3
  SECONDARY (identity >= 30%): n=12  V=0.000  A=0.917  -> VAL-RARE
    residue counts: A:11, G:1
    (pre-registered: VAL-COMMON iff V fraction >= 0.20 of non-gap-at-222 residues)
  saved .../data/processed/task54_h1b_conservation.csv
  LIMITATIONS: reviewed-UniProt sampling is model-organism/vertebrate biased; clade claims describe the sample. Identity floors bound alignment risk but distant orthologs may still misplace 222. Gap-at-222 rows are counted (res222='-'), not silently dropped.
```
Verdict:
- VAL-RARE: zero orthologs in either pre-registered set carry Val at the position corresponding to human 222 (PRIMARY A:3; SECONDARY A:11, G:1). The review's alternative — "if Val occurs commonly in some clades, V222 context sensitivity may be a phylogenetic/clade cue" — is not supported by the sampled orthologs: position 222 is conserved Alanine (91.7% in SECONDARY, 100% in PRIMARY), with one Gly.
- Small-n caveat (AGENTS §3 honesty): the PRIMARY set is only n=3 (vertebrate orthologs that clear 50% identity AND the 400–800 length window); the substantive evidence is the SECONDARY n=12. Even n=12 is modest; the claim written above is scoped to "the sampled orthologs," as the script's own LIMITATIONS block says.
- Human self-check passed: the alignment machinery maps P42898's own 222 back to A — the identity test on the test (AGENTS §4).
- No contradiction with MTHFR_RESULTS_LOG (no ortholog-conservation claim exists there).
Files created/modified: scripts/54_h1_a222v_deleteriousness.py (shared with H1a), data/processed/task54_h1b_conservation.csv, data/processed/task54_uniprot_mthfr.tsv (fetch provenance), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Two smoke-stage fixes, both before any conservation result was computed (disclosed, AGENTS §7): (a) the first UniProt query (gene:MTHFR only) returned just 4 entries — essentially only mammals use that exact symbol — so the fetch was broadened to a 2-query union with a protein-name query (data-COLLECTION completeness, not result-dependent tuning); (b) the alignment-coordinate unpack assumed exactly 2 blocks and real alignments have more (ValueError) — fixed to iterate blocks properly.
- Coverage reality check printed by the script: 26 fetched → 13 kept after the 400–800 length window (bacterial MetF proteins are ~200 aa and drop out; they are also arguably not true orthologs of the FAD-dependent eukaryotic enzyme — the length filter and identity floors both push in the same conservative direction).
---

## H2a — Proximity confound recomputed with Cα 3D distance (6FCX) and FAD distance [item 27]
Status: PASS (verdict: MIXED-INDETERMINATE — delta_ESM tracks 3D almost as strongly as linear distance; neither "attention locality" nor "biophysics" is decisively confirmed)
Time started / finished: 2026-09-22 10:04 / 2026-09-22 10:06
What I did:
1. Pre-registered in scripts/55_h2_structure_distances.py docstring: parse RCSB 6FCX chain A (downloaded once to data/raw/6FCX.pdb; DBREF maps residues 37–644 1:1 to P42898 numbering, FAD = HETATM resi 701 chain A); gates (222 has CA, FAD has heavy atoms); GATE reproduce the published 5.4 linear rho on the full n=10,757 set to |delta|≤0.005; then on identical structure-covered rows compute Spearman(|delta_ESM|, {linear, Cα-3D-to-222, min-heavy-atom-to-FAD}) with position-cluster bootstrap CIs; paired D1 = |rho_lin|−|rho_3D|, D2 = |rho_lin|−|rho_FAD| with cluster-bootstrap CIs; verdict LINEAR-STRONGER iff both D CIs > 0, 3D-RELEVANT iff either CI < 0, else MIXED-INDETERMINATE. Cutoffs none here (distances continuous); H2b holds the pre-registered cutoffs.
2. Full run N_BOOT=2000, 17 s wall, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
6FCX chain A: 589 positions with CA in 37-644; FAD heavy atoms: 53
Analysis set (delta_esm & GI non-null): 10757 variants, 654 positions

H2a: 3D distance (6FCX) vs linear sequence distance
  GATE reproduce published |delta| vs linear dist222: derived=-0.298214 published=-0.298214 |diff|=5.55e-17 (tol 0.005) -> OK
  structure-covered subset: 9633 variants, 588 positions (dropped 1124 variants / 66 positions outside 37-644 or missing CA)
  |delta_ESM| vs linear (restricted rows)  : rho=-0.2752 CI=[-0.3286,-0.2161] n=9633 pos=588
  |delta_ESM| vs C-alpha 3D to 222         : rho=-0.2443 CI=[-0.2982,-0.1820] n=9633 pos=588
  |delta_ESM| vs min heavy-atom dist to FAD: rho=-0.2625 CI=[-0.3172,-0.2016] n=9633 pos=588
  paired D1 = |rho_lin| - |rho_3D| = +0.0309 CI=[-0.0036,+0.0676]
  paired D2 = |rho_lin| - |rho_FAD| = +0.0127 CI=[-0.0187,+0.0449]
  pre-registered H2a verdict: MIXED-INDETERMINATE
Saved .../data/processed/task55_h2_distances.csv
```
Verdict:
- MIXED-INDETERMINATE by the pre-registered rule. Effect sizes alongside significance (AGENTS §3): all three distance metrics track |delta_ESM| about equally strongly on identical rows — linear −0.275, Cα-3D −0.244, FAD −0.263, all CIs excluding 0 by a wide margin. D1's CI [−0.0036, +0.0676] narrowly straddles 0 (linear nominally strongest but not reliably so), D2's comfortably does.
- What this does and does not settle: the review's dichotomy — "if delta_ESM tracks sequence distance but NOT 3D, that confirms attention locality" — does not resolve, because delta_ESM DOES track 3D distance nearly as strongly as linear distance (a drop from −0.275 to −0.244, ~11% relative). The honest reading: sequence distance and 3D distance are themselves strongly correlated in a single-domain protein, so this dataset cannot cleanly separate "the model attends to nearby sequence" from "the effect is structurally local." Neither the confirmation of locality nor the confirmation of biophysics is supported at this resolution.
- Gate hygiene: the published 5.4 linear rho reproduced to 5.55e-17 (same code path, same set), and coverage losses are printed, not hidden (1,124 variants / 66 positions outside the 37–644 structure window — termini and disordered gaps).
- No contradiction with MTHFR_RESULTS_LOG 5.4: its −0.298 is reproduced exactly; the 3D recompute is new analysis.
Files created/modified: scripts/55_h2_structure_distances.py (new, uncommitted, shared with H2b), data/raw/6FCX.pdb (downloaded raw structure, not the read-only mthfrModel copy), data/processed/task55_h2_distances.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Two smoke-stage bugs in my own script, both fixed before any result was interpreted: (a) the published-row lookup matched two CSV rows (both "distance from 222" lines) — tightened to startswith; the script's own exit(1) gate caught it (no result had been computed). (b) My paired-bootstrap helper indexed numpy arrays with original frame labels (IndexError) — fixed with reset_index. The pre-registered statistics, tolerances, and verdict rule were not touched.
- |e.b| itself also increases with distance from 222 in the published table (rho=+0.229) — interaction magnitude is itself spatially structured, worth remembering when reading any of the distance results.
---

## H2b — Focused local test: 3D neighbors of 222 + FAD contacts [item 28]
Status: PASS (pre-registered verdict: INCONCLUSIVE-POWER on the PRIMARY union; the positive local signal replicates in the 3D-neighbors ≤10 Å COMPONENT — CI excludes 0 — but that is a labeled secondary, not the primary claim)
Time started / finished: 2026-09-22 10:04 / 2026-09-22 10:06
What I did:
1. Pre-registered in script 55's docstring: PRIMARY = union(Cα dist to 222 ≤ 10 Å, min heavy-atom dist to FAD ≤ 5 Å) as ONE restricted test (the review words it as one: "3D neighbors of 222 plus FAD contacts"; 5 Å mirrors the project's own MTHFR_structural_alignment.pml convention); components (10 Å only, FAD only) and a 15 Å sensitivity REPORTED, not cherry-picked; reproduction gates on the published linear splits (+0.067 within-25, −0.075 beyond-25, tol 0.005 each, exit 1 on failure); statistic = signed Spearman(delta_ESM, GI_folinate_independent) with position-cluster bootstrap CI; verdict LOCAL-POSITIVE-SURVIVES iff PRIMARY CI excludes 0 positive, NEGATIVE-IN-PRIMARY iff negative, else INCONCLUSIVE-POWER with power context vs the within-25 set.
2. Full run N_BOOT=2000 (part of script 55; same run as H2a).
Actual output (real numbers, not a paraphrase):
```
H2b: focused local test -- 3D neighbors of 222 + FAD contacts
  GATE within-25:  derived=+0.066793 published=+0.067 |diff|=2.07e-04 -> OK
  GATE beyond-25:  derived=-0.075380 published=-0.075 |diff|=3.80e-04 -> OK
  neighborhoods: 3D<=10A: 24 positions; 3D<=15A: 66; FAD<=5A: 29; PRIMARY union: 49
  PRIMARY union (3D<=10A + FAD<=5A)    rho=+0.0507 CI=[-0.0432,+0.1348] n=776 pos=48 p_boot=0.307000
  component: 3D neighbors <=10A        rho=+0.1191 CI=[+0.0066,+0.2166] n=363 pos=23 p_boot=0.042000
  component: FAD contacts <=5A         rho=-0.0574 CI=[-0.1896,+0.0599] n=472 pos=29 p_boot=0.374000
  sensitivity: 3D neighbors <=15A      rho=+0.0495 CI=[-0.0308,+0.1259] n=1051 pos=65 p_boot=0.229000
  gate context: linear within-25       rho=+0.0668 CI=[-0.0289,+0.1506] n=844 pos=50 p_boot=0.177000
  pre-registered H2b verdict: INCONCLUSIVE-POWER
  power context: PRIMARY pos=48 vs within-25 pos=50 (published within-25 underpowered claim rested on n=844 rows / CI crossing 0)
```
Verdict:
- INCONCLUSIVE-POWER on the pre-registered PRIMARY: union rho=+0.0507, CI [−0.0432, +0.1348], n=776 variants / 48 positions. The review's goal — "its own clean test rather than being folded into the pooled negative result" — was achieved procedurally (clustered inference, pre-registered cutoffs, gates passed), but the test does not resolve: the union is essentially the same size as the old within-25 set (48 vs 50 positions), so the power problem the review identified is structural, not fixable by re-cutting the same variants.
- The informative secondary (labeled as such, pre-registered to be reported): the 3D-neighbors ≤10 Å component — the tightest structural neighborhood of 222, n=363 / 23 positions — gives rho=+0.1191, CI [+0.0066, +0.2166], p_boot=0.042. The directionally-positive local signal from5.4 REPLICATES in 3D space, and more strongly than the linear within-25 estimate (+0.067). The FAD-contact component does NOT (rho=−0.0574, CI crosses 0): the local positive effect is about spatial proximity TO RESIDUE 222, not about the cofactor site.
- Discipline note (AGENTS §0): the 10 Å component is NOT the pre-registered primary and its CI excludes 0 only barely (lower bound +0.0066, 23 clusters); two of the five reported sets could show this by chance. The primary claim stays INCONCLUSIVE-POWER; the component is a lead, not a finding.
- Gates reproduced both published5.4 split values to ≤3.8e-04 before testing anything new (sanity, AGENTS §4).
- No contradiction with MTHFR_RESULTS_LOG 5.4: its "+0.067 within-25, CI crosses zero, underpowered" is reproduced exactly (our within-25 CI still crosses zero: [−0.0289, +0.1506]).
Files created/modified: scripts/55_h2_structure_distances.py (shared with H2a), data/processed/task55_h2_distances.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- The union PRIMARY is *smaller* in rows (776) than the linear within-25 set (844) — the structural neighborhoods are tighter than the ±25-residue window despite adding FAD contacts. If a future round wants real power here, it needs a different data source (more backgrounds/structures), not a re-cut; that is a recommendation, not something I changed.
- Position 222's own variants are inside the 10 Å component (dist=0 by definition); removing them would be a post-hoc cut — not done, disclosed instead.
---

## H3a — Rescue/suppressor variants: is ESM-2's failure symmetric, and does delta_ESM enrich for rescue at all? [item 29]
Status: PASS (verdicts: ASYMMETRIC-FAILURE + NO enrichment for rescue — the rank enrichment is significantly INVERTED)
Time started / finished: 2026-09-22 10:07 / 2026-09-22 10:11
What I did:
1. Pre-registered in scripts/56_h3_rescue_enrichment.py docstring: sign conventions imported from S2 (verified against fitModels.R + labeled rows, not assumed); population = phase5 non-null delta_esm + GI_folinate_independent (10,757/654); rescue = e.b>0 vs worse = e.b<0; PRIMARY stats T1 mean-delta difference, T2 agreement rates vs the 0.5 chance line + asymmetry, T3 AUC of delta_ESM for e.b>0 — each position-cluster bootstrapped (N_BOOT=2000); SECONDARY (labeled) repeats on e.post.b>0.95 (S2's convention). Pre-registered: ENRICHMENT verdict fires iff AUC CI excludes 0.5 with direction stated; SYMMETRIC-FAILURE iff both rate CIs include 0.5 AND asymmetry CI includes 0, else ASYMMETRIC-FAILURE. Gate: phase5 GI_indep_post ≡ raw e.post.b (NaN patterns included) to ≤1e-12, else exit 1.
2. Full run N_BOOT=2000, 8 s wall, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
Analysis set: 10757 variants, 654 positions
GATE GI_indep_post == raw e.post.b: jointly non-null=10752, NaN in both=5, one-sided NaN=0, max|diff|=0.00e+00 (tol 1e-12) -> OK

H3a: rescue vs worse-in-A222V, ESM-2's failure shape

  [PRIMARY (all, n=10757)]  n=10757 rows, 654 positions; rescue(e.b>0)=5448 worse(e.b<0)=5309
    mean delta     rescue=+0.02717 CI=[+0.01885,+0.03665]   worse=+0.03861 CI=[+0.03165,+0.04671]
    mean diff      -0.01144 CI=[-0.01705,-0.00519]  (rescue - worse)
    agree rescue   +0.6233 CI=[+0.5932,+0.6533]  vs 0.5: EXCLUDES
    agree worse    +0.3268 CI=[+0.2978,+0.3550]  vs 0.5: EXCLUDES
    asymmetry      +0.2965 CI=[+0.2422,+0.3505]  vs 0: EXCLUDES
    AUC(delta->e.b>0) 0.4525 CI=[0.4374,0.4688]  -> ENRICHMENT-FOR-RESCUE (CI excludes 0.5, direction: delta LOWER for rescue, i.e. inverted)
    failure shape: ASYMMETRIC-FAILURE  (both rate CIs include 0.5 AND asymmetry CI includes 0: False)
    descriptor     base rate e.b>0 = 0.5065; among delta_ESM>0 (n=6970): e.b>0 = 0.4872

  [SECONDARY (e.post.b > 0.95)]  n=4260 rows, 630 positions; rescue(e.b>0)=2680 worse(e.b<0)=1580
    mean delta     rescue=+0.01664 CI=[+0.00883,+0.02466]   worse=+0.03021 CI=[+0.02273,+0.03799]
    mean diff      -0.01357 CI=[-0.02150,-0.00574]  (rescue - worse)
    agree rescue   +0.6022 CI=[+0.5649,+0.6379]  vs 0.5: EXCLUDES
    agree worse    +0.3354 CI=[+0.2975,+0.3716]  vs 0.5: EXCLUDES
    asymmetry      +0.2668 CI=[+0.2048,+0.3283]  vs 0: EXCLUDES
    AUC(delta->e.b>0) 0.4492 CI=[0.4232,0.4736]  -> ENRICHMENT-FOR-RESCUE (CI excludes 0.5, direction: delta LOWER for rescue, i.e. inverted)
    failure shape: ASYMMETRIC-FAILURE  (both rate CIs include 0.5 AND asymmetry CI includes 0: False)
    descriptor     base rate e.b>0 = 0.6291; among delta_ESM>0 (n=2664): e.b>0 = 0.6059

Saved .../data/processed/task56_h3_rescue.csv
```
Verdict:
- ASYMMETRIC-FAILURE (pre-registered rule fired: the asymmetry CI [+0.2422, +0.3505] excludes 0). ESM-2 does NOT fail symmetrically: it "agrees" with the measured direction on 62.3% of rescue variants (CI [+0.593, +0.653], excludes 0.5) but on only 32.7% of worse-in-A222V variants (CI [+0.298, +0.355], excludes 0.5 — i.e. it actively disagrees two-thirds of the time there). The failure concentrates on the deleterious-in-A222V class.
- NO enrichment for rescue — INVERTED (this is the direct answer to "does delta_ESM enrich for the rescue variants at all?"). AUC of delta_ESM for the rescue class = 0.4525, CI [0.4374, 0.4688], entirely below the 0.5 chance line: rescue variants get systematically LOWER delta_ESM than worse variants (means +0.0272 vs +0.0386, difference −0.0114 CI [−0.0171, −0.0052]). The script's literal pre-registered verdict string prints "ENRICHMENT-FOR-RESCUE … direction: delta LOWER for rescue, i.e. inverted" because the pre-registration was written as "fires iff CI excludes 0.5, state direction" — the plain-language reading is ANTI-enrichment: rank-wise, delta_ESM points slightly AWAY from rescue.
- Descriptor agrees: among delta_ESM>0 variants, the rescue fraction is 0.4872 vs a 0.5065 base rate (primary) and 0.6059 vs 0.6291 (significant subset) — no positive enrichment by sign either.
- Noise-sensitivity handled as pre-registered: the atlas-significant subset (e.post.b>0.95, n=4,260) tells the same story on every statistic (rates 0.602/0.335, AUC 0.4492 CI [0.4232, 0.4736]) — the asymmetry is not an artifact of splitting on noise-level e.b.
- Effect sizes alongside significance (AGENTS §3): the mean-delta difference (−0.011) is small relative to delta's own sd (~0.118 from script 32), so the asymmetry is real but modest in magnitude; the rate asymmetry (0.30) is the larger, more interpretable effect.
- Consistency with S2/5.2: S2's direction check used extreme rows (e.b > ±0.5) and found ESM's mean delta near-zero-to-opposite there; here, on ALL rows, both group means are positive because delta_ESM has an overall positive bias (+0.033 population mean) — the two results are compatible (different subsets, different statistics) and both point the same way: ESM's background-response does not track the measured interaction.
- No contradiction with MTHFR_RESULTS_LOG: rescue-class breakdowns never appear there (new analysis).
Files created/modified: scripts/56_h3_rescue_enrichment.py (new, uncommitted), data/processed/task56_h3_rescue.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Smoke-stage GATE bug in my own script (fixed before any H3 statistic ran, disclosed per AGENTS §7): the column-identity gate counted only jointly non-null rows (10,752 of 10,757) and failed the run even though identity was exact. The 5 unmatched rows are NaN in BOTH columns (raw e.post.b has 1,274 NaNs of 13,134 — fits without a posterior); the fixed gate now verifies identity on non-null rows AND zero one-sided NaNs (max|diff| = 0.00e+00, one-sided = 0).
- The pre-registered AUC verdict STRING is direction-ambiguous as written ("ENRICHMENT-FOR-RESCUE … inverted"); the direction is stated in the same line and in this entry's plain reading. Not renamed after the fact — renaming a pre-registered verdict string post-run would be exactly the kind of silent retuning this project forbids.
---

## H4a — Does 6.3's high-stratum failure hold specifically at low folinate? [item 30]
Status: PASS (verdict: HOLDS-AT-LOW-FOLINATE — and, descriptively, it holds at ALL FOUR conditions, so averaging is not diluting it; if anything it grows with folinate)
Time started / finished: 2026-09-22 10:12 / 2026-09-22 10:15
What I did:
1. Pre-registered in scripts/57_h4_low_folinate.py docstring: GATE = rebuild script 34's pooled 6.3 machinery exactly (same crossfit calls, seeds, qcut strata) and reproduce on-disk task34_additive_null.csv's gi_high row — observed diff always (deterministic, tol 1e-6), CI endpoints additionally when N_BOOT==2000 (on-disk draw count; the deferral at smoke N_BOOT prints itself). Per-condition extension for c ∈ {12, 25, 100, 200}: target_c = m{c}.score, w_hat_c = crossfit(model_A → w{c}.score), A_c = w{c}.score(p.Ala222Val) from phase3 (phase5 has no A222V row), null_c = w_hat_c × A_c, all cross-fit by position; rows = 6.3's exact set ∩ condition present (drops printed); stratum labels transferred from the pooled qcut so "high" = 6.3's "high". PRIMARY (single): HIGH stratum at condition 12 → HOLDS iff CI excludes 0 positive; REVERSED iff negative; else NOT-CONFIRMED. Other 11 cells labeled descriptive dilution context, no multiplicity claim.
2. Full run N_BOOT=2000, 3.3 s wall, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
phase5 rows 11344 -> pooled 6.3 set 11113 (dropna model_A/model_C/target/f_bar_wt: -231)
pooled analysis set for strata: 10757 rows; stratum counts: {'low': 3586, 'high': 3586, 'mid': 3585}

GATE rebuild of 6.3 pooled HIGH: derived diff=+0.002409 CI=[+0.001551,+0.003208] n=3586
        on-disk task34:           diff=+0.002409 CI=[+0.001551,+0.003208] n=3586
        max|delta| obs/lo/hi = 1.04e-17/3.66e-17/4.42e-17 (tol 1e-6) -> OK

  condition  12 ug/ml: A_c=0.4176  rows kept=10516 (dropped 241 missing w12.score/m12.score; positions=654)
    low  (n= 3519) MAE(null)=0.1617 MAE(ESM-2)=0.1575 diff=-0.00418 CI=[-0.00527,-0.00309]  -> ESM-2 BETTER (CI<0)
    mid  (n= 3536) MAE(null)=0.1527 MAE(ESM-2)=0.1516 diff=-0.00116 CI=[-0.00215,-0.00021]  -> ESM-2 BETTER (CI<0)
    high (n= 3461) MAE(null)=0.2085 MAE(ESM-2)=0.2108 diff=+0.00227 CI=[+0.00144,+0.00308]  -> ESM-2 WORSE (CI>0)
  condition  25 ug/ml: A_c=0.5643  rows kept=10509 (dropped 248 missing w25.score/m25.score; positions=654)
    low  (n= 3508) MAE(null)=0.2130 MAE(ESM-2)=0.2093 diff=-0.00378 CI=[-0.00485,-0.00272]  -> ESM-2 BETTER (CI<0)
    mid  (n= 3531) MAE(null)=0.1969 MAE(ESM-2)=0.1963 diff=-0.00061 CI=[-0.00158,+0.00030]  -> crosses 0
    high (n= 3470) MAE(null)=0.2744 MAE(ESM-2)=0.2760 diff=+0.00160 CI=[+0.00075,+0.00245]  -> ESM-2 WORSE (CI>0)
  condition 100 ug/ml: A_c=0.6659  rows kept=10540 (dropped 217 missing w100.score/m100.score; positions=654)
    low  (n= 3512) MAE(null)=0.2394 MAE(ESM-2)=0.2353 diff=-0.00410 CI=[-0.00545,-0.00281]  -> ESM-2 BETTER (CI<0)
    mid  (n= 3537) MAE(null)=0.2212 MAE(ESM-2)=0.2210 diff=-0.00024 CI=[-0.00139,+0.00088]  -> crosses 0
    high (n= 3491) MAE(null)=0.2942 MAE(ESM-2)=0.2972 diff=+0.00303 CI=[+0.00200,+0.00409]  -> ESM-2 WORSE (CI>0)
  condition 200 ug/ml: A_c=0.7817  rows kept=10477 (dropped 280 missing w200.score/m200.score; positions=654)
    low  (n= 3502) MAE(null)=0.2706 MAE(ESM-2)=0.2651 diff=-0.00546 CI=[-0.00732,-0.00352]  -> ESM-2 BETTER (CI<0)
    mid  (n= 3520) MAE(null)=0.2314 MAE(ESM-2)=0.2328 diff=+0.00140 CI=[-0.00014,+0.00292]  -> crosses 0
    high (n= 3455) MAE(null)=0.2604 MAE(ESM-2)=0.2655 diff=+0.00510 CI=[+0.00361,+0.00655]  -> ESM-2 WORSE (CI>0)

PRE-REGISTERED PRIMARY: HIGH stratum at condition 12 (lowest folinate)
  diff=+0.00227 CI=[+0.00144,+0.00308] n=3461 pos=601
  VERDICT: HOLDS-AT-LOW-FOLINATE (ESM-2 worse than null, CI>0)

Saved .../data/processed/task57_h4_per_condition.csv
```
Verdict:
- HOLDS-AT-LOW-FOLINATE (pre-registered primary): at the lowest folinate condition (12 µg/ml), the high stratum reproduces 6.3's failure — MAE(ESM-2) − MAE(null) = +0.00227, CI [+0.00144, +0.00308], n=3,461 / 601 positions. The review's dilution worry does NOT apply: 6.3's pooled +0.00241 is not an artifact of averaging.
- Descriptive dilution grid (labeled, not independent tests): the high-stratum failure appears at EVERY condition — 12: +0.00227, 25: +0.00160, 100: +0.00303, 200: +0.00510, all CIs excluding 0 positive. The effect is not concentrated at low folinate; if anything it is LARGEST at 200 µg/ml (descriptive — no pre-registered claim on that contrast). Meanwhile the low stratum shows ESM-2 BETTER at every condition (CIs negative), reproducing6.3's low-stratum row per-condition — the stratum×condition structure is coherent, not noisy.
- Gate quality: the rebuild of 6.3 reproduces the on-disk pooled result bit-stable (obs 1.04e-17, CI endpoints 3.66e-17 / 4.42e-17 at N_BOOT=2000, same seed) — the per-condition extension is provably built on the same machinery (reproduction = unit test of code, not independent evidence; AGENTS §6).
- Accounted drops (AGENTS §5): 11,113 → 10,757 (non-null GI for strata) → per-condition 10,477–10,540 (condition missingness 217–280 rows, ~2.2%); drops are condition-missingness only and stratum proportions stay ~1/3 each.
- Effect sizes alongside significance (AGENTS §3): +0.0016 to +0.0051 against pooled baseline MAE ~0.22–0.30 — i.e. 0.5–2% relative; real but small, consistent with6.2's "~0.2% of baseline MAE" framing.
- No contradiction with MTHFR_RESULTS_LOG 6.3: its pooled numbers are reproduced exactly by the gate; per-condition breakdowns are new.
Files created/modified: scripts/57_h4_low_folinate.py (new, uncommitted), data/processed/task57_h4_per_condition.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- The gate's CI check is conditional on N_BOOT==2000 by construction (CIs are seed-stable but not draw-count-stable); at the smoke run it printed "CI check deferred" rather than failing spuriously — the observed-value check gated in both runs. Disclosed here because a gate that silently relaxes would be exactly the kind of thing this project does not allow; it announces itself in the output.
- Pooled strata n are 3,586/3,585/3,586 (from10,757), while 6.3's published high n=3,586 — matches.
---

## J1a — Reconcile the extrinsic-vs-intrinsic framing: state the departure plainly [item 35]
Status: PASS (departure confirmed and statement drafted below; MTHFR_RESULTS_LOG.md NOT edited per protocol — the statement lives here for the writeup to lift verbatim)
Time started / finished: 2026-09-22 10:27 / 2026-09-22 10:33
What I did:
1. Located the pre-registered prediction as quoted by the review (REVIEW_TRIAGE.md lines 261-266): "The original proposal predicted extrinsic (folinate_response) error would exceed intrinsic (e.b) error. The actual result is the reverse."
2. Searched the repo for the ORIGINAL proposal document itself: glob `**/*proposal*` → no files; grep -ril "extrinsic" over all non-git files → only REVIEW_TRIAGE.md; root *.md = AGENTS.md, README.md, RESULTS.md only; docs/ contains only MTHFR_RESULTS_LOG.md, REVIEW_TRIAGE.md, OVERNIGHT_LOG.md. **The original proposal document is absent from the repo** (exact locations checked: repo root, docs/ recursively, all *.md). Assumption (most conservative reading, logged per protocol): REVIEW_TRIAGE.md's quotation of the prediction is the authoritative statement of what was pre-registered.
3. Collected both strands' final outcomes from MTHFR_RESULTS_LOG.md line references and this log's own runs.
Actual output (real quotes/numbers, not a paraphrase):
- Extrinsic strand outcome — MTHFR_RESULTS_LOG.md lines 45-48: "folinate_response (environment-dependent context) — DROPPED, does not survive multivariable controls (fitness, Grantham, BLOSUM62, RSA, domain)"; "GI_folinate_dependent (e.r) — DROPPED, fails its own re-derivation null outright (see 2.2). This is the cleanest kill in the project." (2.2: "e.r fails its re-derivation null outright... a clean, reportable negative result in its own right").
- Intrinsic strand outcome — log lines 85-88 (3.1): "GI_folinate_independent survives in both error metrics (rank: +0.0521, calibrated: -0.0590, both CIs exclude [zero])"; log 2.1 (lines 56-66): survives the sign-flip null but "the real effect is roughly a fifth of the headline number" (81%/78% artifact); this review's runs: F1b HOLDS (all 4 checks, log entry F1b), G1 PART 2 SURVIVES and STRENGTHENS (Spearman(delta_ESM, global-epistasis residual) = -0.1455 CI [-0.1761, -0.1131], sign-flip p<0.0001, null centered), H4a HOLDS at all four folinate conditions.
Verdict (the explicit departure statement, drafted for the writeup — quoting verbatim):
```
PRE-REGISTERED PREDICTION, NOT MET — STATED AS A DEPARTURE. The original
proposal predicted that error in the extrinsic strand (folinate_response)
would exceed error in the intrinsic strand (atlas e.b): extrinsic context
was expected to carry the real signal, and intrinsic e.b was expected to
fail its controls. The actual result is the reverse, on both sides of the
comparison. The extrinsic strand was killed outright: folinate_response
does not survive multivariable controls, and its folinate-dependent
interaction e.r fails its own re-derivation null — the cleanest negative
result in the project. The intrinsic strand, predicted to fail, weakly
survived: e.b passes multivariable controls, survives the sign-flip
re-derivation null (though ~78-81% of its raw correlation is structural
artifact of its own construction), and retains a significant residual
association after removing global epistasis (rho = -0.1455, 95% CI
[-0.1761, -0.1131], position-clustered bootstrap, sign-flip p < 0.0001)
which strengthens rather than shrinks relative to the raw correlation.
We report this as a departure from the pre-registered prediction rather
than reframing it after the fact.

CANDIDATE EXPLANATION (one candidate, not a tested mechanism): the
extrinsic trait was measured through per-condition calibration — each
folinate condition is normalized against its own within-condition
statistics before any cross-condition quantity is formed. A genuine
folinate effect expressed as condition-level shifts in the mutant arm is
therefore absorbed as global per-condition scaling and removed by
construction before reaching either reported interaction metric; what
survives calibration is condition-invariant ("intrinsic") structure. This
predicts the observed asymmetry without biology: the preprocessing is
intrinsically more destructive to the extrinsic signal than to the
intrinsic one. Consistent with it, the per-condition check (H4a) found
the headline comparison flat across all four folinate conditions
(high-stratum deficit +0.0016 to +0.0051, all CIs excluding 0) — no
folinate-dependent structure remains in the calibrated endpoint for an
extrinsic effect to live in. This candidate has NOT been directly tested:
no analysis in this log measures how much folinate signal the calibration
absorbs.
```
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry only).
Anything unexpected or worth flagging:
- The original proposal document does not exist in the repo, so the departure statement's "prediction" side rests on REVIEW_TRIAGE.md's quotation, not the primary source. Flagged rather than assumed away.
- The log's own sections never use the words "extrinsic", "intrinsic", "departure", or "prediction" for this contrast (grep confirmed zero hits outside REVIEW_TRIAGE.md) — the review's premise that the log never states it plainly is correct.
---

## J2b — Was the primary-metric change (β_intrinsic → atlas e.b) ever written down as a deviation? [item 37]
Status: PASS (audit complete; answer: IMPLICIT — no deviation note exists anywhere in the repo)
Time started / finished: 2026-09-22 10:33 / 2026-09-22 10:36
What I did:
1. Repo-wide search for the metric switch and for any deviation note: `grep -ril "intrinsic"` (all files, venv/.git noise excluded), `grep -i "beta_intrinsic|β_intrinsic|primary metric"` over *.md, `grep -i "intrinsic|beta"` over scripts/*.py, `grep -i "deviation|β|primary metric|choose one primary"` over MTHFR_RESULTS_LOG.md.
2. Enumerated every documented metric decision in the log to see whether any of them IS this change.
Actual output (real numbers, not a paraphrase):
- `grep -ril "intrinsic" | grep -v REVIEW_TRIAGE | grep -v venv` → **zero project files**. The string "β_intrinsic" / "intrinsic" appears ONLY in REVIEW_TRIAGE.md lines 275-276 (the review itself). Zero hits in scripts/*.py, MTHFR_RESULTS_LOG.md, RESULTS.md, README.md, AGENTS.md, notebooks/ if any.
- `grep -i "deviation"` over MTHFR_RESULTS_LOG.md → no matches. The word "deviation" as a registered concept appears nowhere in the project's own documents (only AGENTS.md's disclosure rules and REVIEW_TRIAGE).
- `grep -i "metric"` over MTHFR_RESULTS_LOG.md → 13 hits, all accounted for: error-metric rank-vs-calibrated discussion (lines 17, 41, 57, 88, 96, 122, 128, 152, 156, 327, 346, 349) and the MAE-instead-of-rank switch of §1.2. The two metric decisions the log DOES document are: (a) e.b over e.r as the surviving context class (1.3, lines 44-51), (b) delta_ESM promoted to primary endpoint (Part 5, line 161). Neither is the β_intrinsic→e.b change.
- grep "β|beta" over scripts/*.py → zero matches (the construct does not exist in current code under any name).
Verdict:
- The change from a project-derived β_intrinsic-with-SEs to the atlas's own e.b happened **IMPLICITLY**. No deviation note exists at any path checked (scripts/, docs/, root *.md including RESULTS.md). Confirmation complete; suggested deviation-note wording for the writeup (drafted here, nothing edited):
```
DEVIATION (primary metric, recorded late): the proposal's primary
intrinsic endpoint was a project-derived beta_intrinsic with standard
errors. The project instead analyzed the atlas's own published e.b
(plus an independent re-derivation, own_e_b). This switch was never
written down as a deviation when it happened — it is being recorded
here, post-hoc, and no rationale for it was documented at the time. The
closest decisions that ARE documented are the e.b-over-e.r choice
(results log 1.3) and the delta_ESM endpoint promotion (results log
Part 5); neither covers this change.
```
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry only).
Anything unexpected or worth flagging:
- A consequence worth the writeup's attention: because β_intrinsic appears nowhere in code or output, no figure in the project can be traced back to the proposal's originally named quantity — the review's characterization of the switch as implicit is confirmed, not merely plausible.
---

## J3a — Rough count of statistical tests to date + pre-registration of the remaining analyses [item 38]
Status: PASS (count below; pre-registration block fixed BEFORE any remaining analysis ran — timestamped here, scripts 58-60 docstrings will quote it)
Time started / finished: 2026-09-22 10:36 / 2026-09-22 10:45
What I did:
1. Counted scripts (`ls scripts/*.py | wc -l`) and pattern-counted test-invoking code across scripts/*.py and scripts/lib/*.py with one grep -hoE | sort | uniq -c.
2. Estimated how many individually reported inferential results those sites expand to (several sites loop over subsets).
3. Drafted effect-size-based decision rules for every analysis still to run under this review (J2a-3, J2a-5, J4a, J4b, K1a) and fixed them here, before running any of them. J2a's evidence-only items (1, 2, 4) involve no new test and were collected earlier; J2a's two new tests (items 3, 5) are deliberately deferred until after this entry, so their rules are pre-registered rather than post-hoc.
Actual output (real numbers, not a paraphrase):
```
scripts/*.py count: 61   (includes the known duplicate numbering: two scripts numbered 36)
Pattern counts across scripts/*.py + scripts/lib/*.py:
  N_PERM                              83   (env-var reads — ~1 run each, not tests)
  p_boot (reported bootstrap p)       45
  permutation (word in code/comments) 39
  position_cluster_bootstrap( call    36   (35 call sites in scripts/ + 1 definition in lib)
  crossfit_isotonic_by_position(      34   (calibration fits — each validated by holdout checks)
  p_perm (reported permutation p)     22
  n_perm                              21
  spearmanr(                          17   (some descriptive, some inferential)
  p_one (reported one-sided p)         5
  paired_rho_difference_bootstrap(     3
  crossfit_isotonic_within_group(      2
  crossfit_isotonic_stratified(        2
  pearsonr(                            1
```
Rough count reasoning (stated as an estimate, not precision): distinct hypothesis-test call sites ≈ 35 position-cluster bootstraps + 3 paired-rho bootstraps + ~10 non-bootstrap permutation/null tests + ~15 inferential spearmanr/pearsonr ≈ **~65 test sites**; reported individually, several sites expand across subsets (script 19 alone prints 18 cluster-bootstrapped CIs; log §3.2 = 8 region tests; D1a = 7; E1a = 7; C1's table ≈ 6 rows × 3 targets × 3 metrics × 3 strata ≈ 100+ cells but only ~6 pre-specified contrasts claimed; scripts 24/28/50/53 report per-stratum CIs). Honest range: **on the order of 100-200 individually reported inferential numbers across 61 scripts.** No formal project-wide multiplicity correction has been claimed anywhere; protection in-project comes from pre-registered gates (script 36 precedent), position-level nulls (A1a/A1b), and this review's per-task pre-registrations. This count is itself a rough audit figure — reproducible from the grep above.
PRE-REGISTRATION BLOCK (fixed 2026-09-22, before scripts 58-60 were run):
```
J2a-3 (ESM-2 150M check, script 58): sample N_POS=100 of the 655 atlas
  positions (seed 0); score all 19 substitutions per position in both
  backgrounds (WT seq, A222V seq) with esm2_t30_150M_UR50D using the
  project's own get_position_logprobs (masked-marginal log-odds vs the
  background's own residue — identical plumbing to scripts 10/11).
  PRIMARY: Spearman(delta_150M, delta_650M) on matched substitutions,
  position-cluster bootstrap N_BOOT=2000. VERDICT BANDS: CI_lo > 0.90
  -> ROBUST-TO-MODEL-SIZE; 0.75 < CI_lo <= 0.90 -> PARTIAL-ROBUSTNESS;
  CI_lo <= 0.75 -> SIZE-SENSITIVE. Secondary (descriptive): per-position
  sign agreement of delta (exact-zero ties excluded, reported).
  If the 150M weights cannot be fetched/run, outcome = DEVIATION NOTE
  with the exact error (task allows run-or-deviation); no substitute
  model may be used.
J2a-5 (extrinsic-intrinsic correlation, limitation 7, script 58):
  PRIMARY: Spearman(folinate_response, own_e_b) on the missense set,
  position-cluster bootstrap N_BOOT=2000. SECONDARY: partial version
  controlling w.fitness (rank-residual method), same resampling.
  VERDICT BANDS: |rho_primary| >= 0.10 AND CI excludes 0 ->
  STRANDS-NOT-INDEPENDENT (limitation-7 concern supported); otherwise
  -> INDEPENDENCE-NOT-REJECTED (report the effect size either way).
  Ambiguity note: the proposal document is absent (J1a); "extrinsic" =
  published folinate_response (context_metrics.csv), "intrinsic" =
  own_e_b (own_context_metrics.csv) — most direct reading of the phrase.
J4a (FDR-based threshold, script 59): empirical null = synonymous z_e_b
  (n with SE computable, printed). FDR_hat(c) = syn pass rate(c) /
  missense pass rate(c), c grid 1.00-10.00 step 0.01. c* = smallest c
  with FDR_hat <= 0.05 AND all larger grid points also <= 0.05.
  VERDICT BANDS vs the flat 3.76x (|z|>3.76): c* in [3.01, 4.51]
  (±20%) -> 3.76-CONFIRMED; c* > 4.51 -> 3.76-TOO-PERMISSIVE;
  c* < 3.01 -> 3.76-TOO-STRICT. Report FDR_hat(3.76), pass counts at
  both, median |own_e_b| among passers (effect size), position-cluster
  bootstrap CI on FDR_hat at c* (N_BOOT=2000). Conservative reading
  (logged): no pi0 factor — the raw rate ratio is used, which cannot
  overstate FDR relative to Storey-style estimates.
J4b (is 3.76 constant?, script 59): stratum ratio = sd(syn own_e_b) /
  median(syn se_e_b) — EXACTLY script 35's definition (3.758647782830226
  must be reproduced as the pooled value; gate within 1e-6). Strata:
  region (assign_region) x fitness terciles of w.fitness (tercile edges
  computed on the analysis set; syn rows inherit their own w.fitness
  stratum). VERDICT RULE: 3.76 CONSTANT-ENOUGH iff every stratum ratio
  in [1.88, 5.64] (±50% of 3.7586) AND max/min <= 2; else NEEDS-TO-VARY.
  Per-stratum syn n printed; strata with syn n < 50 flagged underpowered.
  Position-cluster bootstrap CI per ratio (N_BOOT=2000).
K1a (conditionally damaging classification, script 60): analysis set =
  substitutions with both arms non-null (expected ~10,757, printed),
  position 222 excluded (undefined in cis-with-A222V arm — pre-registered
  exclusion, count printed). Per-arm normalized fitness f = (fitness -
  mean_nonsense_arm) / (mean_synonymous_arm - mean_nonsense_arm), anchors
  computed WITHIN arm from that arm's own syn/nonsense rows (removes the
  arm-wide A222V shift by construction — disclosed in output).
  CONDITIONALLY DAMAGING (PRIMARY): f_WT >= 0.5 AND f_A222V < 0.5
  (sensitivity bands 0.3/0.7 reported, labeled sensitivity only).
  ESM flag (PRIMARY): background score < 0 (masked-marginal log-odds
  disfavoring the mutant vs the background's own residue); bands < -1,
  < -2 reported. PRIMARY STAT: delta_frac = frac_flagged(bg scoring) -
  frac_flagged(WT scoring) among conditionally damaging, position-
  cluster bootstrap N_BOOT=2000. VERDICT: FLAG-FRACTION-CHANGED iff CI
  excludes 0 AND |delta_frac| >= 0.05 (5-point effect-size floor,
  following E1a's precedent); else NOT-MEANINGFULLY-CHANGED. Report both
  fractions with CIs, set size (flag n < 100 as underpowered), and the
  all-missense baseline fractions for context.
```
Files created/modified: docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry only). No analysis in the pre-registration block has been run at this entry's finish time.
Anything unexpected or worth flagging:
- Ordering deviation, disclosed: REVIEW_TRIAGE lists J2 before J3, but J3a's whole purpose is to pre-register remaining analyses; splitting J2 (evidence items done first, test items after J3a) serves the task's intent. J2a's single entry will be written only after all five of its items are complete.
- Two scripts share the number 36 (pre-existing); next free script numbers used tonight: 58, 59, 60.
---

## J2a — Audit for un-run pre-registered analyses: 5-item checklist [item 36]
Status: PASS (all five items resolved: 1 substitution CONFIRMED-documented, 2 floor CONFIRMED-documented-with-disclosure, 3 RUN — verdict SIZE-SENSITIVE, 4 already run by script 19 — CONFIRMED-EXISTING, 5 RUN — verdict INDEPENDENCE-NOT-REJECTED)
Time started / finished: 2026-09-22 10:45 / 2026-09-22 11:06
Ordering note: items 1, 2, 4 are evidence/confirmation only (no new test) and were collected first; items 3 and 5 are new tests and were deliberately deferred until AFTER the J3a pre-registration entry (finished 10:45), so their decision bands were fixed in advance. This entry is written once, after all five items were complete.
What I did:
1. (Item 1 — Steiger substitution) Read scripts/lib/stats.py:85-89, the function that replaced Steiger's test.
2. (Item 2 — effect-size floor) Read scripts/48_e1_effect_size_and_boundaries.py docstring + printed-limitations block.
3. (Item 3 — 150M model check) Confirmed what the project actually ran (scripts 10/11 load esm2_t33_650M_UR50D) and that NO deviation note mentioning 150M exists anywhere (grep -ril "150M" → only REVIEW_TRIAGE.md). Then wrote scripts/58_j2a_proposal_checklist.py per the J3a pre-registration: N_POS=100 random positions (seed 0), both backgrounds, project's own get_position_logprobs, N_BOOT=2000; smoke at N_POS=5/N_BOOT=100, full run at N_POS=100/N_BOOT=2000.
4. (Item 4 — context-precision correlation) Confirmed it was ALREADY run: scripts/19_precision_checks.py ("Subtask C: Precision filtering (proposal 5.6a)") writes data/processed/tier2_precision_checks.csv using position_cluster_bootstrap (line 65), summarized in MTHFR_RESULTS_LOG.md 3.3 ("5 of 18 subset tests ... have a CI crossing zero").
5. (Item 5 — extrinsic-intrinsic correlation, limitation 7) Not run anywhere in the repo (grep for any extrinsic×intrinsic pairing: zero hits outside REVIEW_TRIAGE). Ran it as script 58's second half, per J3a bands, with the logged conservative column mapping (proposal document absent — see J1a).
Actual output (real numbers, not a paraphrase):
Evidence quotes for items 1, 2, 4:
```
stats.py:85-89: "paired_rho_difference_bootstrap(...): Cluster bootstrap for
  rho(x2,y) - rho(x1,y) on the same rows. Compares competing predictors
  against one outcome. Steiger's test is avoided: it assumes bivariate
  normality that rank data violate."  -> substitution INTENTIONAL and
  DOCUMENTED in the library's own docstring. PASS.
script 48 docstring item 4: "Effect-size floor: PRIMARY 0.10; bands 0.05
  (lenient) and 0.25 (strict) reported as sensitivity. DISCLOSURE (AGENTS
  6): the floor was chosen AFTER the review quoted the ~0.03-0.04 vs 0.24
  numbers, so it is post-hoc; all three bands are printed..."
  item 6: "VERDICT RULE (fixed before running)..." and the script prints
  "Effect floor 0.10 is POST-HOC ..." in its own output.
  -> floor DOCUMENTED and pre-fixed relative to script 48's run; its
  post-hoc origin (chosen in response to the review, i.e. after the review
  saw those numbers) is disclosed inside the script itself. PASS.
tier2_precision_checks.csv: 18 rows, ci_includes_zero True in 5 rows
  (rows 2, 10, 11, 15, 16 = GI_*_post>0.95 / precise-half subsets) ->
  log 3.3's "5 of 18" reproduces exactly from disk. PASS (already run).
```
Full-run output of scripts/58 (N_POS=100, N_BOOT=2000, EXIT=0, wall 90.8 s):
```
Script 58 — J2a items 3 & 5 | N_POS=100 N_BOOT=2000 SEED=0
GATE 1 merged delta identity: max|bg-wt-delta| = 2.220e-16 on 12426 rows (tol 1e-9)
GATE 2 650M join reproduction: max|delta wt| = 0.000e+00, bg = 0.000e+00, n = 12426 (tol 1e-9)

==========================================================================
J2a-5  EXTRINSIC vs INTRINSIC correlation (limitation 7)
==========================================================================
missense rows with both traits: 10757, positions: 654, w.fitness present: 10757
PRIMARY Spearman(folinate_response, own_e_b): rho=-0.0057 CI=[-0.0345,+0.0209] p=0.6660 n=10757 pos=654
  bands: |rho|>=0.10 (False) AND CI excludes 0 (False)  ->  VERDICT: INDEPENDENCE-NOT-REJECTED
SECONDARY partial | w.fitness (rank-residual): rho=-0.0964 CI=[-0.1197,-0.0716] p=0.0000 n=10757 pos=654  (descriptive co-primary context; coarse linear-in-rank control, see docstring)

==========================================================================
J2a-3  ESM-2 150M model check (proposal pre-registered model)
==========================================================================
sequence len 656; atlas positions 655
sampled N_POS=100 positions (seed 0); 222 in sample: False
Loading esm2_t30_150M_UR50D (weights downloaded and cached this run)
Using device: mps
  100/100 positions (81s elapsed)
scored rows: 1900; unmatched to cached 650M delta: 0
matched for PRIMARY: 1900 substitutions, 100 positions
PRIMARY Spearman(delta_150M, delta_650M): rho=+0.0978 CI=[-0.0444,+0.2275] p=0.1540 n=1900 pos=100
  bands: CI_lo=-0.0444  ->  VERDICT: SIZE-SENSITIVE
SECONDARY (descriptive) sign agreement: 53.11% of 1900 rows (exact-zero ties excluded: 0)
SECONDARY (descriptive) score rho wt bg: +0.4157 (n=1900)
SECONDARY (descriptive) score rho a222v bg: +0.4098 (n=1900)

Saved .../data/processed/task58_150m_check.csv
Total wall: 90.8 s
```
Verdict:
- Item 1 (Steiger): PASS — substitution intentional and documented in scripts/lib/stats.py docstring (quote above).
- Item 2 (effect-size floor): PASS — documented in script 48's pre-registered docstring with an explicit post-hoc disclosure printed by the script itself. The floor value responds to the review's quoted numbers, i.e. it was chosen after the review saw those magnitudes but BEFORE script 48 ran; both facts are on the record.
- Item 3 (150M check): RUN, verdict **SIZE-SENSITIVE** (pre-registered band: CI_lo = −0.0444 ≤ 0.75). The background-delta quantity this project analyses does NOT replicate across ESM-2 checkpoints: rho(delta_150M, delta_650M) = +0.0978, CI [−0.0444, +0.2275] includes 0, sign agreement 53.11% (coin flip) on 1,900 substitutions at 100 positions. Even raw score-level rank agreement is only +0.42 per background. Plain reading: either 150M is too weak to produce stable deltas (its scores are themselves only rank-aligned at ~0.42), or delta is checkpoint-specific in general; either way conclusions drawn from delta_ESM are NOT demonstrated to be a property of "ESM-2-family masked marginals" — they are properties of the 650M checkpoint as measured. This cuts toward caution on every delta-based claim, and it means the proposal's pre-registered model was never the model that produced the project's numbers (now stated here with a measured consequence).
- Item 4 (context-precision): already run by script 19 (proposal 5.6a), position-cluster bootstrapped, 18 tests, log 3.3's "5 of 18 cross zero" verified exactly against tier2_precision_checks.csv. No deviation note needed; confirmed present.
- Item 5 (extrinsic-intrinsic): RUN, verdict **INDEPENDENCE-NOT-REJECTED**. Raw Spearman(folinate_response, own_e_b) = −0.0057, CI [−0.0345, +0.0209], n=10,757 / 654 positions — nowhere near the 0.10 band and the CI straddles 0. The pre-registered fitness-partial secondary comes in at −0.0964, CI [−0.1197, −0.0716] — just below the 0.10 effect band in magnitude, excluding 0: after removing shared fitness dependence the strands relate WEAKLY negatively, not positively. Either way limitation 7's concern (the two strands are the same signal wearing different clothes) is not supported on the pre-registered primary reading; the partial is disclosed as a small conditional association, coarse linear-in-rank control (F1a showed fitness effects are nonlinear).
- Effect sizes reported alongside significance throughout (AGENTS §3): item 3's rho is ~0.10 with a null-crossing CI (no effect to speak of); item 5's raw rho is ~0 with CI width ±0.03.
- No contradiction with MTHFR_RESULTS_LOG: items 3/5 are new; items 1/2/4 confirm existing documented content (19's rows reproduce 3.3 exactly).
Files created/modified: scripts/58_j2a_proposal_checklist.py (new, uncommitted), data/processed/task58_150m_check.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- Two smoke-stage bugs in my own script 58, both fixed BEFORE the full run and before interpreting any number, disclosed per AGENTS §7: (a) my custom partial-Spearman bootstrap computed p as the fraction of draws within |obs| — not a p-value, and it disagreed with its own CI (p=0.4554 alongside a CI excluding 0); replaced with the house `_partial_spearman` (its docstring: OLS-residual and closed-form versions verified identical) and house `_summarize` p-convention min(2·min(P(boot≤0),P(boot≥0)),1). (b) the matched-set floor was a hard 500 rows, which blocked the N_POS=5 smoke from exercising the full path; made N_POS-scaling with the full-run floor unchanged at 500. Neither fix touched a pre-registered decision band (J3a bands key off CI/point estimate only).
- The 150M weights needed a fresh download (~600 MB, dl.fbaipublicfiles.com) — it succeeded, so the pre-registered DEVIATION-NOTE fallback was not needed; the fallback path exists in the script and prints the exact error if ever hit.
- Position 222 was not drawn in the seed-0 sample, so the known A222V-background hgvs naming gap at 222 (script 11) did not arise; the script accounts for unmatched rows either way (0 here).
---

## J4a — FDR-based SE threshold, replacing the flat 3.76x fix [item 39]
Status: PASS as a test run (verdict: NO-SUSTAINED-C-IN-GRID — the pre-registered edge case fired: NO threshold in [1,10] controls FDR at 5%; FDR at the flat 3.76 itself is 0.93)
Time started / finished: 2026-09-22 11:06 / 2026-09-22 11:11
What I did:
1. Wrote scripts/59_j4_fdr_threshold.py implementing exactly the J3a pre-registration: empirical null = synonymous z_e_b from task35_epistatic_set.csv; FDR_hat(c) = syn pass rate/missense pass rate on grid 1.00-10.00 step 0.01; c* = smallest c with FDR ≤ 0.05 sustained to grid end; bands ±20% around 3.76. Logged interpretation choices in the docstring before running: no π0 factor (raw rate ratio cannot understate FDR vs Storey); tail condition evaluated only where missense discoveries ≥ 1; if no c satisfies the rule, that IS the outcome (no substitute rule).
2. Gates (all passed): pooled syn ratio reproduced from task35_summary.csv to 5.773e-15; z_e_b ≡ own_e_b/se_e_b to 8.171e-14; syn ok 570 / missense ok 10,757 (matches task35's own table).
3. Smoke N_BOOT=200 then full N_BOOT=2000, EXIT=0 both, point estimates identical across runs (deterministic), full run <10 s.
Actual output (real numbers, not a paraphrase):
```
Script 59 — J4a + J4b | N_BOOT=2000 SEED=0
rows 13134; synonymous ok 570; missense ok 10757
GATE pooled syn ratio: 3.758647782830 (target 3.758647782830226, |diff| = 5.773e-15, tol 1e-6)
GATE z identity: max|z - own/se| = 8.171e-14 (tol 1e-9)

J4a  FDR-BASED THRESHOLD (synonymous empirical null)
grid 1.00-10.00 step 0.01; points with 0 missense discoveries (excluded from tail condition): 0
  FDR_hat(2.00) = 0.9980   syn 255/570  mis 4822/10757
  FDR_hat(2.50) = 0.9862   syn 207/570  mis 3961/10757
  FDR_hat(3.00) = 0.9439   syn 162/570  mis 3239/10757
  FDR_hat(3.50) = 0.9148   syn 127/570  mis 2620/10757
  FDR_hat(3.76) = 0.9312   syn 116/570  mis 2351/10757
  FDR_hat(4.50) = 0.9452   syn 88/570   mis 1757/10757
  FDR_hat(5.00) = 0.9926   syn 76/570   mis 1445/10757

PRE-REGISTERED c*: none in [1,10] satisfies FDR<=0.05 sustained to the grid end -> VERDICT: NO-SUSTAINED-C-IN-GRID
FDR_hat(3.76) = 0.9312  (syn 116/570, mis 2351/10757)
  missense passers at 3.76 (|z|>3.76): 2351 (21.9%)  median |own_e_b| = 0.3265  median se = 0.0529

Saved .../data/processed/task59_j4a_fdr.csv (and task59_j4b_ratios.csv)
LIMITATIONS: syn-tail-as-null assumes exchangeable SE structures; ~570 syn rows give wide bootstrap CIs (reported); small-n strata flagged; ddof=1 and median-SE exactly as script 35.
```
Verdict:
- **NO-SUSTAINED-C-IN-GRID** (the pre-registered edge case, anticipated in the docstring before running). The synonymous pass rate tracks the missense pass rate at EVERY cutoff from 2 to 10 (FDR_hat 0.91-1.00): there is no z-threshold in [1,10] where the empirical null would clear 5% FDR. The flat 3.76 rule sits at FDR_hat = 0.9312 — i.e. under this criterion ~93% of the "epistatic" calls at |z|>3.76 are of the magnitude the synonymous null produces freely. The proposed FDR-based replacement therefore does NOT yield a usable threshold; it instead demonstrates that the SE model underlying z_e_b cannot be rescued by any multiple of itself. This is a result, reported plainly, not a test failure (all gates passed; the pre-registered rule executed exactly as written).
- Cross-check against the project's own numbers (reproduction, not new evidence): FDR_hat(2.00) = 255/570 ÷ 4822/10757 reproduces task35_summary.csv's threshold row exactly (44.7% syn FPR vs 44.8% missense pass) — the near-identity of the tails was already visible in script 35's own table; what is new here is reading it as an FDR and applying the pre-registered decision rule.
- Mechanism-consistency (not a separate test): D1a already showed the high-|e.b| stratum is enriched for high-SE variants, so missense |z| does not exceed synonymous |z| even where |e.b| is larger — the error structure tracks the same quantities the threshold divides by. Both classes of z are inflated ~3.76x by the same per-condition SE underestimate.
- Effect sizes alongside significance (AGENTS §3): pass counts and rates at both comparison points are printed above; the pre-registered bootstrap CI on FDR_hat(c*) is not computable because no c* exists (edge case, pre-announced — no post-hoc CI substituted); n_syn=570 implies binomial-scale uncertainty on the 0.9312 on the order of a few points, stated as scale context only, not a computed interval.
- No contradiction with MTHFR_RESULTS_LOG: the log never claims FDR control; script 35's 3.76 was introduced as an empirical inflation factor, and this entry shows it is far from an FDR-controlling threshold — an extension, not a conflict. The 3.76 value itself is reproduced to 5.8e-15.
Files created/modified: scripts/59_j4_fdr_threshold.py (new, uncommitted), data/processed/task59_j4a_fdr.csv (new), data/processed/task59_j4b_ratios.csv (new, J4b's — see that entry), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- The magnitude was not expected: FDR at 3.76 came in at 0.93, not the ~0.05-0.30 range a "3.76 is roughly fine" story would allow. Per AGENTS §0 this is reported as measured; nothing was re-tuned (grid, target, and edge rule all pre-registered in J3a).
- Zero grid points had zero missense discoveries, so the logged zero-discovery handling never triggered; it is recorded for completeness.
- The ±20% bands around 3.76 (3.01-4.51) never came into play because c* does not exist; no band was reinterpreted.
---

## J4b — Is the 3.76 ratio constant across regions and fitness levels? [item 39]
Status: PASS (verdict: NEEDS-TO-VARY — fires on the pre-registered max/min ≤ 2 clause, max/min = 2.03, driven by region; no stratum leaves the ±50% band; fitness-level variation is small)
Time started / finished: 2026-09-22 11:11 / 2026-09-22 11:14
What I did:
1. Same script 59 run (shared machinery with J4a; entries kept separate per task). Stratum ratio = sd(syn own_e_b, ddof=1)/median(syn se_e_b) — exactly script 35's definition; pooled gate passed at |diff| = 5.773e-15.
2. Regions from script 35's own region assignment (all 570 synonymous rows have a region); fitness terciles = edges [0.4928, 1.007] on the 10,757-row missense analysis set, synonymous rows placed by their OWN w.fitness (all 570 have one).
3. Full run N_BOOT=2000 position-cluster bootstrap CIs per stratum, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
J4b  IS THE 3.76 RATIO CONSTANT ACROSS REGIONS / FITNESS?
syn with region: 570; syn with w.fitness: 570

                 stratum   n_syn    ratio                     CI  flags
                region 1     128    5.162  [   4.339,   6.151]
                region 2     131    2.537  [   2.084,   3.002]
                region 3     154    4.036  [   3.494,   4.521]
                region 4     157    2.593  [   2.139,   2.971]

  fitness tercile edges (missense analysis set n=10757): [0.4928, 1.007]
  missense tercile counts: {'low': 3586, 'mid': 3585, 'high': 3586}
                 fit_low      11    3.680  [     nan,     nan]  (underpowered: n<50)
                 fit_mid     282    3.441  [   3.053,   3.826]
                 fit_high    277    3.550  [   3.105,   3.986]

bands: [1.879, 5.638] (+/-50% of 3.7586); max/min ratio = 2.03 (<=2 required)
PRE-REGISTERED J4b VERDICT: NEEDS-TO-VARY  (any stratum outside band: False; max/min>2: True)
underpowered strata (syn n<50): [{'stratum_type': 'fitness_tercile', 'stratum': 'low', 'n_syn': 11}]
```
Verdict:
- **NEEDS-TO-VARY** by the pre-registered rule: every stratum's point estimate is inside the ±50% band [1.879, 5.638], but max/min = 5.162/2.537 = 2.03 > 2, so the spread clause fires. Plain reading: the SE miscalibration factor is NOT constant — it varies about twofold ACROSS REGIONS (region 1 = 5.16 vs region 2 = 2.54, non-overlapping bootstrap CIs [4.34, 6.15] vs [2.08, 3.00]), while FITNESS-level variation is small (mid 3.44 CI [3.05, 3.83] vs high 3.55 CI [3.11, 3.99], heavily overlapping; the low tercile has only 11 synonymous rows and is flagged underpowered with no CI).
- Margin disclosure: the spread clause fired at 2.03 against a 2.00 threshold — a marginal breach. The verdict is reported as the rule dictates (NEEDS-TO-VARY), with the margin stated so a reader can see it is not a wide miss. The regional CIs make the substantive point regardless: region 1's miscalibration is ~1.4× pooled (5.16 vs 3.76), region 2's ~0.68× (2.54 vs 3.76).
- Effect sizes alongside significance (AGENTS §3): the twofold regional spread and per-stratum CIs are the effect; small-n stratum disclosed rather than hidden.
- Direct relevance to script 35's known miscalibration (as the review anticipated): a single global 3.76x SE inflation under-corrects region 1 and over-corrects region 2. Combined with J4a (no z-cutoff controls FDR at any multiplier), the flat correction should not be presented as calibrated.
- No contradiction with MTHFR_RESULTS_LOG: the log reports only the pooled 3.76 (reproduced exactly here); no per-region ratio was ever claimed there.
Files created/modified: data/processed/task59_j4b_ratios.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry); scripts/59_j4_fdr_threshold.py shared with J4a (see that entry).
Anything unexpected or worth flagging:
- Only 11 of 570 synonymous rows fall in the lowest fitness tercile — synonymous variants are nearly all high-fitness, so the "is 3.76 constant across FITNESS levels" question is answerable only for mid/high; the low-tercile cell is reported as underpowered rather than read.
- Region-level synonymous counts (128-157) are modest; the regional spread (2.5-5.2) is larger than the within-stratum CI widths, so the conclusion does not rest on a single noisy cell.
---

## K1a — Conditionally damaging variants: ESM-2 flag fraction, and does the A222V background change it? [item 40]
Status: PASS (pre-registered verdict: NOT-MEANINGFULLY-CHANGED; flag fraction itself is near-saturated ~95% and indistinguishable from the all-missense baseline)
Time started / finished: 2026-09-22 11:14 / 2026-09-22 11:18
What I did:
1. Wrote scripts/60_k1_conditionally_damaging.py per the J3a pre-registration: set = substitutions with both fitness arms non-null, position 222 excluded a priori; per-arm two-point-normalized fitness f = (fitness − nonsense_arm_mean)/(syn_arm_mean − nonsense_arm_mean) with anchors from each arm's own synonymous/nonsense rows; conditionally damaging PRIMARY f_WT ≥ 0.5 AND f_A222V < 0.5 (bands 0.3/0.7); ESM flag PRIMARY score < 0 (bands −1/−2); primary stat = paired flag-fraction difference (bg scoring − WT scoring), position-cluster bootstrap N_BOOT=2000; verdict FLAG-FRACTION-CHANGED iff CI excludes 0 AND |Δ| ≥ 0.05.
2. Gates: arm-direction sign sanity Spearman(m.fitness − w.fitness, own_e_b) = +0.5923 on n=10,757 (positive → the w/m = WT/A222V-background reading is consistent with S2's verified convention; a backwards arm reading would have flipped this sign and exited 1); merged delta identity 2.220e-16; anchors ordered (nonsense < synonymous) in both arms; analysis set 10,757 inside the expected band; ESM merge dropped 0 rows.
3. Smoke N_BOOT=200 (caught a KeyError — see below, fixed before any number was produced), then full N_BOOT=2000, EXIT=0.
Actual output (real numbers, not a paraphrase):
```
Script 60 — K1a | N_BOOT=2000 SEED=0
GATE arm-direction sanity: Spearman(m.fitness - w.fitness, own_e_b) = +0.5923 on n=10757
eligible substitutions (both arms non-null): 10757 ; position 222 excluded a priori: 0 -> set 10757
anchors w.fitness: synonymous mean 0.9958 (n=584), nonsense mean 0.1745 (n=591)
anchors m.fitness: synonymous mean 0.4769 (n=579), nonsense mean 0.0792 (n=553)
GATE merged delta identity: max|bg-wt-delta| = 2.220e-16 (tol 1e-9)
after ESM merge: 10757 rows (0 dropped for missing scores)
  f_cut=0.5 (PRIMARY)      score<0    n=1462  frac_WT=0.9501 CI=[0.9333,0.9657]  frac_BG=0.9487 CI=[0.9310,0.9645]  delta=-0.0014 CI=[-0.0042,+0.0000] p=0.7250  [PRIMARY]
    -> position=522 VERDICT: NOT-MEANINGFULLY-CHANGED
  f_cut=0.5 (PRIMARY)      score<-1   n=1462  frac_WT=0.9077 CI=[0.8830,0.9303]  frac_BG=0.9063 CI=[0.8816,0.9289]  delta=-0.0014 CI=[-0.0042,+0.0007] p=0.4420  [sensitivity]
  f_cut=0.5 (PRIMARY)      score<-2   n=1462  frac_WT=0.8700 CI=[0.8400,0.8985]  frac_BG=0.8707 CI=[0.8401,0.8989]  delta=+0.0007 CI=[-0.0014,+0.0028] p=0.7750  [sensitivity]
  f_cut=0.3 (sensitivity)  score<0    n=1459  frac_WT=0.9637 frac_BG=0.9637 delta=+0.0000 CI=[+0.0000,+0.0000] p=1.0000
  f_cut=0.3 (sensitivity)  score<-1   n=1459  frac_WT=0.9267 frac_BG=0.9273 delta=+0.0007 CI=[+0.0000,+0.0026] p=0.6920
  f_cut=0.3 (sensitivity)  score<-2   n=1459  frac_WT=0.9013 frac_BG=0.9013 delta=+0.0000 CI=[-0.0027,+0.0028] p=1.0000
  f_cut=0.7 (sensitivity)  score<0    n=1540  frac_WT=0.9409 frac_BG=0.9416 delta=+0.0006 CI=[+0.0000,+0.0020] p=0.7220
  f_cut=0.7 (sensitivity)  score<-1   n=1540  frac_WT=0.8948 frac_BG=0.8942 delta=-0.0006 CI=[-0.0031,+0.0013] p=0.7600
  f_cut=0.7 (sensitivity)  score<-2   n=1540  frac_WT=0.8461 frac_BG=0.8468 delta=+0.0006 CI=[-0.0013,+0.0032] p=0.8370

BASELINE all-missense (score<0): frac_WT=0.9527 frac_BG=0.9532 delta=+0.0006 CI=[-0.0004,+0.0015] n=10757 (descriptive)
Saved .../data/processed/task60_k1_conditionally_damaging.csv
```
Verdict:
- Pre-registered PRIMARY: **NOT-MEANINGFULLY-CHANGED**. Among the 1,462 conditionally damaging variants (522 positions — well above the n<100 underpowered flag), supplying the A222V background moves the ESM-2 damaging-flag fraction by Δ = −0.14 percentage points (CI [−0.42, 0.00] pp, p = 0.725) — both the effect-size floor (|Δ| ≥ 0.05 = 5 pp, missed by ~35×) and the CI condition fail. All eight sensitivity cells agree: |Δ| ≤ 0.14 pp with CIs hugging zero.
- Answer to part 1 (what fraction does ESM-2 flag): 95.0% at the primary threshold (CI [93.3, 96.6]), 90.8% at < −1, 87.0% at < −2. BUT the all-missense baseline is 95.3% — the conditionally damaging set is flagged at essentially the same rate as missense variants in general. At these thresholds the flag is near-saturated and does not single out the conditionally damaging class; it carries almost no triage information for this question.
- Answer to part 2 (does the A222V sequence change the fraction): no, not meaningfully — Δ ≈ 0 everywhere (baseline all-missense Δ = +0.06 pp, CI [−0.04, +0.15]).
- Interpretation (stated, not overclaimed): consistent with H1a (ESM-2 rates A222V itself near-neutral, z = +0.502, so it has no internal reason to re-weight the background) and with the project's broader pattern that supplying the background does not help (C-family, 6.3). The clinical motivation gets no discriminative support from ESM-2 flags: the model flags nearly everything, and the background does not move the rate.
- Effect sizes alongside significance (AGENTS §3): fractions, CIs, and the 0.14-pp delta are printed above; the set size and position count are reported.
- Accounted drops (AGENTS §5): 13,134 raw → 10,757 substitutions with both arms (arms non-null; the A222V-defining row at position 222 is among the arm-incomplete rows — n_222 in the both-arm set was 0, so the pre-registered 222 exclusion changed nothing, disclosed) → 10,757 after ESM merge (0 dropped) → 1,462 conditionally damaging at the primary cut (1,459 / 1,540 at the 0.3 / 0.7 bands).
- No contradiction with MTHFR_RESULTS_LOG: the log makes no classification-fraction claim; this is new analysis. The arm-sign gate (+0.5923) independently re-confirms S2's sign convention on 10,757 rows.
Files created/modified: scripts/60_k1_conditionally_damaging.py (new, uncommitted), data/processed/task60_k1_conditionally_damaging.csv (new), docs/tasks/review-triage/OVERNIGHT_LOG.md (this entry).
Anything unexpected or worth flagging:
- First smoke run crashed with KeyError: 'position' (raw carries the residue as "start"; the bootstrap cluster column was never created). Fixed before any statistic was produced — the only numbers that exist are from the passing runs above. Disclosed per AGENTS §7.
- The f_cut=0.3 / score<0 sensitivity cell shows Δ = +0.0000 with CI [0.0000, 0.0000] — flagging is literally identical between backgrounds for those rows at that cut; reported as computed, not smoothed.
- The 0.3 fitness band yields n=1,459 vs 0.5's n=1,462 — nearly the same set: the normalized-fitness distribution of missense is such that the band cuts barely move membership. Noted so the sensitivity grid isn't read as three independent replications.
---

## I2a — EVmutation/Potts comparator [item 32]
Status: SKIPPED — on the user's explicit skip list for this run (header of this log); not attempted.

---

## I3a — Model/scoring robustness (150M / ESM-1v / SaProt / pseudo-likelihood) [item 33]
Status: SKIPPED — on the user's explicit skip list for this run (header of this log); not attempted. Note: J2a item 3's 150M delta check (logged above) is a separate, pre-registered sub-analysis and does NOT substitute for this task.

---

## G2a — ThermoMPNN stability-mediated epistasis [item 24]
Status: SKIPPED — on the user's explicit skip list for this run (header of this log); not attempted.

---

## K2a — Lock the one-sentence claim [item 41]
Status: SKIPPED — on the user's explicit skip list for this run (header of this log); not attempted. Group J is complete, so the inputs this task asks for (settled Groups A-J) now exist; writing the sentence remains deliberately out of scope for this run.

---

## SUMMARY

Run finished: 2026-09-22 11:20. Total entries in this log: **47** — every task and subtask in REVIEW_TRIAGE.md has exactly one entry (verified by matching entry headers against the task list: S1–S2, A1a–A2b, B1a–B3, C1a–C3a, D1a–D1c, E1a–E1b, F1a–F2a, G1, G2a, H1a–H4a, I1–I3a, J1a–J4b, K1a–K2a).

### Tally
- **Executed: 43** (each with pasted script output or verbatim evidence quotes in its own entry).
- **SKIPPED per user instruction: 4** — I2a (Potts/EVmutation), I3a (ESM-1v/SaProt/pseudo-likelihood), G2a (ThermoMPNN), K2a (one-sentence claim). One-line entries each; none attempted.
- **BLOCKED: 0.** No missing-file blocks occurred; the only absent file encountered as evidence was the original proposal document (checked at repo root, docs/ recursively, all *.md — absent), which was handled as a logged conservative reading in J1a/J2a rather than a block, because the prediction it needed is quoted verbatim in REVIEW_TRIAGE.md itself.

### Completed, with headline verdicts (group by group)
- **S:** S1 PASS (no column-duplication bug; log reporting discrepancy flagged), S2 PASS (both sign conventions verified on labeled rows: e.b<0 ⇔ less functional in A222V; delta_ESM<0 ⇔ ESM says worse in A222V).
- **A:** A1a/A1b/A1c PASS (granularity audit; script 33's null re-run at position blocks — conclusion unchanged), A2a PASS (dropped rows reconciled, no systematic skew), A2b PASS (n across scripts reconciled: 10,757/11,113/11,344/11,902/13,134 each traced to a named filter).
- **B:** B1a PASS (confounds do not explain delta's association), B1b PASS (compression ≈ −k·S(v|WT) present), B1c **REDUCED-RESOLUTION** (N_POS=500/656; full run ≈11.5–12 min > budget; entropy flattening inconclusive at that resolution), B2 PASS (covered by A1b), B3 **PARTIAL** (replacement wording for 5.3 drafted inside this log — MTHFR_RESULTS_LOG.md not edited, per protocol).
- **C:** C1a PASS (reconciliation table), C1b PASS (S(v|WT) retains the signal — retention is not background info), C1c PASS with method limitation (BLOSUM62 α=0.2559 load-bearing; Grantham gap UNMATCHED — α pinned at bisection floor), C1d PASS (S(v|A222V) vs S(v|WT) not 0.99+), C2a **MIXED** (influence concentrated but not near-222-only), C2b PASS (SEED-ROBUST across 50 seeds), C2c HOLD (MSE verdict matches MAE), C3a PASS (oracle ceiling usable; disattenuated correlation MATERIALLY LARGER: reliability ≈0.64).
- **D:** D1a **ENRICHED** (D=+0.0461 CI [+0.0396,+0.0535], ratio 1.654 — high-|e.b| IS high-SE-enriched), D1b **UNCHANGED-HOLD** (shrunken stratifier: arm3 +0.001851 CI [+0.000987,+0.002706], mean SE 0.1166→0.0788), D1c **HIGHER but FLOOR NOT CLEARED** (R=1.184 CI [1.025,1.371]; ratio-to-nonsense-floor 1.064 CI [0.948,1.207]).
- **E:** E1a **GATE DOWNGRADED** (4 of 7 effect sizes below the 0.10 floor; floor itself disclosed post-hoc), E1b **DIVERGENCE — domain-only** (steps at domain boundaries; NOT robust at window w=15, disclosed).
- **F:** F1a **CHANGED** (calibrated GI coefficient flips sign: linear −0.0590 → binned +0.0537, quad +0.0271; r² 0.03→0.52), F1b **HOLDS** (10–90th restriction, all 4 checks; p10=0.000000, p90=1.337150, kept 9,120/10,757), F2a **CONFIRMED-WITHIN-REGION** (identity 2a exact 0.000e+00; within-region pooled rho +0.1897 CI [+0.1597,+0.2188]; original producing script for task_region2_diagnostic.csv is MISSING — provenance caveat recorded in-entry).
- **G:** G1 **LIMITED-GLOBAL / SURVIVES** — cross-fitted isotonic R²(e.b~w.fitness)=0.1535 CI [0.1317,0.1749] (below the 0.25 SUBSTANTIAL band); residual test Spearman(delta_ESM, residual)=−0.1455 CI [−0.1761,−0.1131], sign-flip p<0.0001, null centered, magnitude diff +0.0748 CI [+0.0585,+0.0912] (STRENGTHENS vs raw; reconciles with script 32 to |diff|=6.94e-17).
- **H:** H1a **NEAR-NEUTRAL** (S(A222V|WT)=−5.200276, z=+0.502, rank 16/19 at position 222), H1b **VAL-RARE** (PRIMARY n=3 all Ala; SECONDARY n=12 with 11 Ala/1 Gly; V=0 → clade-cue alternative unsupported, small-n caveat), H2a **MIXED-INDETERMINATE** (proximity reproduces −0.298214; Cα-3D −0.2443, FAD −0.2625; neither locality nor biophysics decisively confirmed: D1 CI [−0.0036,+0.0676], D2 CI [−0.0187,+0.0449]), H2b **INCONCLUSIVE-POWER** on the pre-registered union (rho=+0.0507 CI [−0.0432,+0.1348]; labeled secondary 3D-only component +0.1191 CI [+0.0066,+0.2166] = lead, not finding), H3a **ASYMMETRIC-FAILURE + anti-enrichment** (agree-rescue 0.6233 vs agree-worse 0.3268, asymmetry +0.2965 CI [+0.2422,+0.3505]; AUC=0.4525 CI [0.4374,0.4688] below 0.5), H4a **HOLDS-AT-LOW-FOLINATE** (HIGH@12: +0.00227 CI [+0.00144,+0.00308]; positive at all four conditions 12/25/100/200 — not diluted; gate reproduced 6.3 to 1.04e-17).
- **I:** I1 PASS as a valid test run / scientific **GATE FAIL** (see below).
- **J:** J1a PASS (explicit departure statement drafted verbatim in its entry; proposal document absent from repo), J2a PASS (5 items: Steiger substitution documented in stats.py; effect-size floor documented in script 48 with its post-hoc origin disclosed; **150M check RUN → SIZE-SENSITIVE** rho(delta150,delta650)=+0.0978 CI [−0.0444,+0.2275], sign agreement 53.11%; context-precision already run by script 19 — "5 of 18" verified against disk; **extrinsic×intrinsic RUN → INDEPENDENCE-NOT-REJECTED** rho=−0.0057 CI [−0.0345,+0.0209], fitness-partial −0.0964 CI [−0.1197,−0.0716]), J2b PASS (β_intrinsic→e.b switch happened **implicitly** — zero deviation notes anywhere; suggested wording drafted in-entry), J3a PASS (~65 test-call sites / order 100–200 reported inferential numbers across 61 scripts; pre-registration block for all remaining analyses fixed before they ran), J4a PASS (**NO-SUSTAINED-C-IN-GRID**: FDR_hat = 0.91–1.00 at every cutoff 2–10; FDR at flat 3.76 = **0.9312**, syn 116/570 vs missense 2,351/10,757), J4b PASS (**NEEDS-TO-VARY**: region ratios 2.54–5.16, max/min 2.03 > 2; fitness terciles 3.44–3.55 stable; low-fitness tercile n_syn=11 underpowered).
- **K:** K1a PASS (**NOT-MEANINGFULLY-CHANGED**: n=1,462 conditionally damaging, flagged 95.0% WT-scoring vs 94.9% A222V-scoring, Δ=−0.14 pp CI [−0.42, 0.00] pp, p=0.725 — vs all-missense baseline 95.3%, i.e. the flag is near-saturated and the background moves nothing).

### The single most important item for the morning
**I1 — GATE FAIL.** The delta_ESM pipeline run on known-epistatic GB1 data: observed pooled rho +0.4467 looks strong, but the permutation null centers at **+0.3880** (≈87% of the observed value is between-site structure), giving **p_one = 0.1398**, CI [+0.2787, +0.5793], gate_pass=0. The pipeline as it stands cannot demonstrate sensitivity to genuine epistasis even when it is present. Until this is resolved, every negative/weak downstream result (5.2/5.3's ~0.10 correlations, the C-family MAE story, G1's limited residual, the H-family nulls) is ambiguous between "no signal" and "pipeline can't see it" — that framing should govern what the writeup claims. Runner-up flags: J4a (the stratifier's SE model cannot control FDR at any multiple — D1a's enrichment is the mechanism), J2a-3 (delta is not checkpoint-stable — size-sensitive), E1b (domain-vs-region divergence not robust at w=15).

### Contradictions vs MTHFR_RESULTS_LOG.md (both numbers logged; file NOT edited)
1. **§5.2 (S1):** log states "ρ = −0.088 (published e.b)"; script 32's saved output is **−0.070705** (published) — the −0.088118 value belongs to own e.b. Direction of the claim unchanged; published-e.b magnitude 19% smaller than logged. Flagged in entry S1.
2. **S2 vs H1a characterization:** this log's S2 entry called S(A222V|WT) = −5.2003 "strongly deleterious" while using it only for direction checking; H1a's distributional analysis puts it **NEAR-NEUTRAL** (mid-distribution of substitutions at position 222, z=+0.502, 68.04% of substitutions at least as deleterious, p10=−12.80 / p90=−1.19). H1a's distributional reading governs; S2's label was about sign, not magnitude. Both stated here.
3. **Extensions (log never claimed otherwise, recorded as qualification, not conflict):** J4a measures FDR at the log's 3.76 fix as **0.9312** (the log presents 3.76 as an empirical inflation factor and never claims FDR control); J4b shows the pooled 3.7586 varies **2.54–5.16 by region** (the log reports only the pooled value). Also verified-consistent: log 3.3's "5 of 18 subset tests cross zero" reproduces exactly from tier2_precision_checks.csv (5 True of 18).

### Process record
- Scripts 42–60 created during this session's run (58–60 tonight: J2a, J4, K1); result CSVs task42–task60 in data/processed/; data/raw/6FCX.pdb and GB1 inputs downloaded. **All uncommitted; no git commits made.**
- RESULTS.md, MTHFR_RESULTS_LOG.md, REVIEW_TRIAGE.md, AGENTS.md: **git-verified untouched** (`git diff --stat HEAD` empty for all four).
- Every pre-registration: J3a's block (fixed 2026-09-22, before scripts 58–60 ran) governed J2a-3, J2a-5, J4a, J4b, K1a; no decision band was changed after results. Smoke-stage fixes in my own new scripts (58: wrong p-formula + smoke-scaled gate; 60: missing cluster column) were made before any full run and disclosed in their entries; script 59's only pre-smoke edit was cleanup of an awkward expression before it ever executed.
- One deliberate ordering deviation, disclosed in J3a: J2b and J3a were written before J2a so J2a's two new tests ran under pre-registered rules.
- Conventions held throughout: venv/bin/python3 foreground only, N_BOOT/N_PERM env vars, position-cluster resampling, data gates sys.exit(1), outputs to data/processed/, limitations printed by the scripts themselves.
