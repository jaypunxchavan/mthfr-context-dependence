# CALIBRATION_LOG.md — session log for docs/tasks/calibration-and-publication-readiness/

Session: external-review feedback response, 2026-09-25. Group N is the
single highest-priority item. This file is append-only: one entry per
task, in completion order, in the exact format given by the session
prompt. Never write an entry without having actually run the check and
read its real output first.

(Entry format — binding for this file:

## [TASK ID] — [one-line title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
---
)

## [N1] — Retrieve Nambiar et al. 2025's exact calibration functional form (Eqn. 2) or their released code
Status: PASS — EXACT EQUATION RECOVERED (their actual equation, not a reconstruction)
Time started / finished: 2026-09-25 18:23 / 18:25
What I did:
- Searched bioRxiv for the paper (DOI 10.1101/2025.09.14.676130, "Protein
  Language Models Capture Structural and Functional Epistasis in a Zero-Shot
  Setting", Nambiar, Littlefield, Cuellar, Khorana, Maslov; posted Sept 17,
  2025) and read the full text, including all of section 4 Methods.
- Searched GitHub for the paper title / authors; the paper's own full text
  names its code repository, and the paper's Data/Code availability line
  (full text line 355) reads verbatim: "The code and data to reproduce these
  results are available at https://github.com/maslov-group/Epistasis".
- Fetched the repo's src/NonlinearTransform/ directory listing (5 MATLAB
  files: nonlinear_fit_RRM.m, nonlinear_fit_TEM1.m, nonlinear_fit_YAP1.m,
  nonlinear_fit_reuse_phi1_TEM1.m, nonlinear_fit_reuse_phi1_YAP1.m) and then
  the raw source of nonlinear_fit_TEM1.m.
- Also confirmed there is no supplementary-media file linked from the full
  text (only an in-text reference to "Supplementary Table 2" of fitted
  parameter values, which is not needed — we fit our own parameters).
Actual output (quoted source text, verbatim):

1) Their released code, https://raw.githubusercontent.com/maslov-group/
Epistasis/main/src/NonlinearTransform/nonlinear_fit_TEM1.m (key lines):
```matlab
%fix a=1, keep same b and c from single mutation fitting
%fit on 20% data, correlation on 80% data
data=readtable("20_llm_tem1_esm2_650.csv");
data1=readtable("20_esm2_650_unique_single_mutations_TEM1.csv");
data_test = readtable("80_llm_tem1_esm2_650.csv");
...
ft = fittype('-1.*log(1+exp(-b.*(x+c)))','dependent',{'y'},'independent',{'x'},'coefficients',{'b','c'});
fo = fitoptions( 'Method', 'NonlinearLeastSquares', 'Lower', [0, 0, 0]);

f = fit(data1.llm_single_mut,data1.expt_single_mut,ft,fo);
f.b
f.c
...
f = fit(cat(1,data.mut21,data.mut12), cat(1,log_exp_double_exp_mut1_,log_exp_double_exp_mut2_),ft,fo);
...
%calculate LLM predicted epistasis
total_epistasis = 0.5*(mut1_prime+mut21_prime+mut2_prime+mut12_prime)-(mut1_prime+mut2_prime);
...
[R,p] = corrcoef(total_epistasis, data_test.expt_epistasis);
```

2) Their Methods section, verbatim (full-text lines 311-327):
```text
We convert relative log-likelihood (RLL) scores from the PLM into model-derived
fitness values using the monotone nonlinearity specified in Eq. (2), where we
fit the parameters (b, c) by nonlinear least squares.

For each protein, we define the calibration subset by a 20% uniform random
sample of the double-mutant entries. The remaining 80% of double mutants are
held out and used only for downstream evaluation of PLM-derived epistasis and
all figures/tables that report generalization. To fit the single-mutant curve,
we take the set of single substitutions that appear as constituents of the
double mutants in the 20% calibration subset.

[Single-mutant curve] We fit one instance of Eq. (2) to unique single mutants
by regressing experimental single-mutant fitness (on the log scale) against
PLM RLLs ... using a 20% fitting subset. This yields parameters (b1, c1) and
a mapping phi1 ... a global curve for single mutants.

[Conditional (background) curve] Separately, we fit a second instance of
Eq. (2) to conditional targets derived from double-mutant measurements using
the same 20% fitting subset. For each pair (A, B), we form the
background-adjusted log-fitness contrasts [log f_AB - log f_A, log f_AB -
log f_B] and regress them on the corresponding conditional PLM scores
log f_A|B and log f_B|A, respectively. This produces parameters (b2, c2) and
a mapping phi2 ...

[Epistasis Calculation, their Eqn. 4] the two path totals
P_A->B = phi1(log f_A) + phi2(log f_B|A) and
P_B->A = phi1(log f_B) + phi2(log f_A|B)
are averaged symmetrically, and the additive expectation
phi1(log f_A) + phi1(log f_B) is subtracted.
```

3) The paper's Results text describing Eqn. 2's shape (full-text line 167),
verbatim: "we fit a nonlinear curve of the form [equation image] where b1 and
c1 are fit parameters ... This function captures the linear dependence at low
values of x < −c1 and the plateau starting for x > c1."

Verdict:
- N1a: the exact equation AND the released code were both found in one
  genuine search (bioRxiv full text + GitHub, repo named by the paper itself).
- The calibration function is, verbatim from their code:
  **phi(x) = −log(1 + exp(−b·(x + c)))**, two free parameters (b, c), fit by
  nonlinear least squares with lower bounds 0 (their fitoptions
  'Lower',[0,0,0] carries a spurious third entry, consistent with the
  header comment "%fix a=1" — an early version evidently had a third
  amplitude parameter a, since fixed to 1; the shipped fittype has exactly
  coefficients {b, c}).
- Properties check against the paper's own description: as x → +∞,
  phi → 0 (plateau for x > c ✓); as x → −∞, phi ≈ b·(x+c) (linear for
  x < −c ✓); strictly monotone increasing for b > 0 ✓. This is a negative
  softplus — i.e. the exact functional family the task doc's N1b fallback
  anticipated, but it is THEIR actual Eqn. 2, not a reconstruction. Any
  write-up may say "we applied Nambiar et al.'s exact calibration function"
  with the citation above. The N1b reconstruction path is NOT used.
- Also recovered at no extra cost: their exact epistasis definition (their
  Eqn. 4) and their exact 20%/80% calibration/held-out protocol — both needed
  later by N3b and N2a respectively.
Files created/modified: none (read-only search). This log entry only.
Anything unexpected or worth flagging:
- Their Eqn. 4 and 20/80 split are recoverable from the same code file, so
  N3b and N2a can follow their exact protocol rather than an approximation.
- Their MATLAB fitoptions 'Lower',[0,0,0] has 3 entries for a 2-coefficient
  fittype (leftover from the fixed-a version); our Python implementation will
  use lower bounds [0, 0] for (b, c), which is the only consistent reading.
- The repo also hosts their data on a Google Drive link (README "Data"
  section); not needed for our test — we fit on MTHFR's own measurements.
---

## [N2] — Fit Nambiar's two-stage calibration on MTHFR's own data with a real 20/80 split (script 87)
Status: PASS — all gates pass, rc=0, fit quality reported
Time started / finished: 2026-09-25 18:31 / 18:32
What I did:
- Inspected the analysis frame first (data/processed/task32_analysis_table.csv,
  11,344 rows / 654 positions) to pin down every column used: measured WT-bg
  fitness = f_bar_wt = mean(w12,w25,w100,w200).score (script 15 line 63),
  measured A222V-bg fitness = f_bar_a222v = mean(m12,m25,m100,m200).score
  (line 64), raw scores esm2_score / esm2_score_a222v_bg. Condition columns
  confirmed from scripts/lib/io.py: WT_COND_COLS = ["w12.score", "w25.score",
  "w100.score", "w200.score"], A222V_COND_COLS = ["m12.score", "m25.score",
  "m100.score", "m200.score"]. f_bar_wt range [0, 3.095192] — a LINEAR
  activity scale, so Nambiar's convention requires a natural-log transform
  (their Methods: "if a dataset reported fitness on a log scale, we used
  those values as provided; otherwise, we applied a log transform").
- Wrote scripts/87_n2_calibration_fit.py with the full pre-registration in
  its docstring BEFORE running (functional form, structural adaptation,
  split rule, targets, fit method, the four gates, exclusion accounting).
- Split (N2a): BY POSITION, seed 0. Documented conflict: the task doc says
  "20% random calibration subset of MTHFR variants", AGENTS.md §3 requires
  calibration anchors cross-fit BY POSITION never by variant, and AGENTS §9
  says AGENTS wins — so the split unit is position (the more conservative
  reading; within-position substitutions never straddle the split). Rule
  implemented verbatim: rng=np.random.default_rng(0) over sorted unique
  positions, first ceil(0.2*654)=131 positions = calibration.
- Fit (N2b/N2c) with scipy curve_fit on calibration rows only, bounds
  [0,0]→[inf,inf] on (b,c), the exact Nambiar form
  phi(x) = -log(1+exp(-b*(x+c))) via stable -logaddexp(0,-b*(x+c)).
- Pre-registered sensitivity arm (declared in the docstring before running,
  NOT post-hoc): phi2-contrast with Nambiar's ACTUAL phi2 target from their
  Methods 4.2, y = ln(f_bar_a222v) - ln(f_bar_wt), because the task doc's
  literal N2c target (raw A222V-bg fitness) differs from theirs; both are
  reported, the primary follows the task doc literally.
Actual output (verbatim, key lines):
```
G1  SPLIT INTEGRITY (20% calibration / 80% held-out, seed 0, BY POSITION)
  seed=0  rule=ceil(0.2*654) positions -> calibration
  calibration: 131 positions / 2279 rows
  held-out   : 523 positions / 9065 rows
  position overlap           : 0 PASS
  hgvs_pro row overlap       : 0 PASS
  seed-0 re-derivation match : PASS
EXCLUSION ACCOUNTING (dropped rows, AGENTS s3)
  phi1 fit eligibility (f_bar_wt): kept=10448 dropped=896 (NaN=231, <=0=665)
    kept    n=10448 positions= 654 mean esm2_score=-7.137 mean delta_esm=+0.0302 | regions 1.0:23%,2.0:23%,3.0:25%,4.0:29%
    dropped n=  896 positions= 355 mean esm2_score=-9.644 mean delta_esm=+0.0609 | regions 1.0:27%,2.0:21%,3.0:34%,4.0:18%
  phi2 fit eligibility (f_bar_a222v): kept=10615 dropped=729 (NaN=0, <=0=729)
    kept    n=10615 positions= 654 mean esm2_score=-7.123 mean delta_esm=+0.0302 | regions 1.0:23%,2.0:23%,3.0:24%,4.0:30%
    dropped n=  729 positions= 281 mean esm2_score=-10.418 mean delta_esm=+0.0681 | regions 1.0:24%,2.0:20%,3.0:46%,4.0:9%
  [PRIMARY ] phi1_wt              ln(f_bar_wt) ~ esm2_score
           b=0.262004  c=11.017485   n_cal=2115  n_held=8333
           calibration: R2=0.1100 RMSE=0.9044 Spearman(pred,obs)=+0.2961
           held-out   : R2=0.1102 RMSE=0.9623 Spearman(pred,obs)=+0.3013   (diagnostic only)
  [PRIMARY ] phi2_a222v           ln(f_bar_a222v) ~ esm2_score_a222v_bg
           b=0.143945  c=3.953698   n_cal=2171  n_held=8444
           calibration: R2=0.1234 RMSE=0.9489 Spearman(pred,obs)=+0.3234
           held-out   : R2=0.1159 RMSE=1.0445 Spearman(pred,obs)=+0.3214   (diagnostic only)
  [SENSITIV] phi2_contrast_sens   ln(f_bar_a222v)-ln(f_bar_wt) ~ esm2_score_a222v_bg
           b=0.020688  c=23.512049   n_cal=2039  n_held=7916
           calibration: R2=0.0016 RMSE=0.9353 Spearman(pred,obs)=+0.0316
           held-out   : R2=0.0025 RMSE=0.9521 Spearman(pred,obs)=+0.0698   (diagnostic only)
G2  SIGN SANITY ... phi1_wt Spearman(esm2_score, y1) = +0.2961 PASS
                   phi2_a222v Spearman(esm2_score_a222v_bg, y2) = +0.3234 PASS
G3/G4 ... phi1_wt b>0 & c>=0 & finite PASS; strictly increasing PASS
          phi2_a222v b>0 & c>=0 & finite PASS; strictly increasing PASS
N2d held-out binned tables printed (10 equal-count bins); residuals vs the
fitted curve are mostly within ±0.26 in log-fitness units and both curves
show Nambiar's own shape: linear at low x, flattening toward 0 at high x.
    fraction of held-out targets > 0 (outside phi's (-inf,0) range):
      phi1: 35.2%    phi2: 2.0%
Saved params to .../data/processed/task87_calibration_params.csv
ALL GATES PASS (G1 split integrity, G2 sign sanity, G3 fit validity,
G4 monotonicity).
EXIT_CODE=0
```
Verdict: PASS. The exact Nambiar Eqn. 2 was fit on 131 calibration
positions (2,279 rows), evaluated only as a diagnostic on 523 held-out
positions (9,065 rows). Both primary curves are monotone, sign-sane, and
reproduce the paper's Fig-2 qualitative shape (linear low-x, plateau
high-x). Fit quality is moderate (held-out R² = 0.1102 / 0.1159) —
honest, and now on record before N3 touches it.
Files created/modified:
- scripts/87_n2_calibration_fit.py (new; the only new script)
- data/processed/task87_calibration_params.csv (3 rows: phi1_wt,
  phi2_a222v primary; phi2_contrast_sens sensitivity)
- data/processed/task87_calibration_split.csv (11,344 rows: hgvs_pro,
  position, split — reused verbatim by scripts 88/89)
Anything unexpected or worth flagging:
- EXCLUSION SKEW, disclosed per AGENTS §3: dropped rows (fitness <= 0 or
  NaN) are NOT a random 8% — they score markedly worse on ESM-2
  (mean esm2_score -9.644 vs -7.137 kept for phi1; -10.418 vs -7.123 for
  phi2), carry larger delta_esm (0.061 vs 0.030), and over-represent region
  3 (34% vs 25% kept; 46% vs 30% for phi2). Null variants with undefined
  log fitness are exactly the low-scoring tail, so the φ curves describe
  the positive-fitness subpopulation (92% of rows); this is unavoidable
  for a log target and is now on the record. N3's evaluation rows are NOT
  restricted by this (own_e_b/GI exist regardless of fitness > 0) — only
  the fitting used positive-fitness rows.
- Nambiar's ACTUAL phi2 target (background-adjusted contrast) essentially
  does not fit on MTHFR: R² = 0.0016 (calibration), rho = +0.0316. The
  task doc's literal target fits fine (R² = 0.1234). This is a real
  divergence between their protocol and this data, found by the
  pre-registered sensitivity arm, not buried.
- 35.2% of held-out phi1 targets (ln f_bar_wt) are > 0, above phi's
  (-inf, 0) ceiling — the single largest structural limit on phi1's fit
  quality here, printed by the script itself.
- p.Ala222Val (needed for N3b's experimental additive baseline) exists in
  phase3_analysis_table.csv with f_bar_wt = 0.6073921694038995 (absent
  from phase5, which excludes position 222). Note: this constant cancels
  out of every Spearman correlation anyway; it will be used only to state
  epsilon_e exactly as Nambiar define it.
---

## [N3] — Headline recomputed on calibrated scores, held-out only (script 88): NOT MATERIAL toward Nambiar's band
Status: PASS — pre-registered verdict NOT MATERIAL (a real negative result for the calibration-gap explanation)
Time started / finished: 2026-09-25 18:34 / 18:41
What I did:
- Wrote scripts/88_n3_calibrated_headline.py with the full
  pre-registration (quantities, split gate, frames, nulls, and the N3d
  verdict rule M1/M2) in its docstring before running. phi is loaded
  from script 87 itself (single implementation of the equation); the
  parameters come from task87_calibration_params.csv, fit once — never
  refit here.
- ATTEMPT HISTORY (all runs disclosed):
  1. Smoke: N_BOOT=300 N_PERM=300, rc=0, 4.97s wall. Used only for
     runtime extrapolation (→ ~3 min full) and gate debugging. Smoke
     numbers are NOT quoted in any verdict below.
  2. After the smoke I added two things, disclosed in the docstring and
     in the output as post-smoke additions, on structural grounds and
     NOT in response to any smoke result: (a) N3b-LITERAL — Nambiar's
     Eqn. 4 actually fits their phi2 with the CONTRAST target (Methods
     4.2), which is N2's sensitivity arm, so N3b must report both phi2
     semantics ("if they disagree, report the disagreement plainly");
     (b) the delta_cal composition diagnostic.
  3. Full run #1: N_BOOT=10000 N_PERM=10000, rc=0, 2m20s.
  4. Independent AGENTS §5 verification of the diagnostic (separate
     script, labeled rows, scipy not the project's _spearman) — all
     values reproduced exactly (see Unexpected).
  5. After seeing the composition diagnostic I added the POST-HOC
     single-curve arm (disclosed as post-hoc in docstring and output,
     printed AFTER the pre-registered verdict, explicitly excluded from
     M1/M2 so it cannot move the verdict).
  6. Final full run #2 (canonical output below): N_BOOT=10000,
     N_PERM=10000, rc=0, 2m48s.
Actual output (verbatim, canonical run):
```
G0  SPLIT RE-DERIVATION AND LEAKAGE CHECK (before any computation)
  seed=0  calibration positions=131 rows=2279 | held-out positions=523 rows=9065
  re-derived split == task87_calibration_split.csv : PASS
  calibration/held-out row overlap in evaluation set: 0 PASS
  calibration loaded (fit once on calibration rows, script 87):
    phi1: b=0.262004 c=11.017485  (target ln(f_bar_wt) ~ esm2_score)
    phi2: b=0.143945 c=3.953698  (target ln(f_bar_a222v) ~ esm2_score_a222v_bg)
    phi2-contrast (their actual Eqn. 4 target): b=0.020688 c=23.512049  (calibration R2=0.0016 — poor fit, disclosed)
G0b  raw anchor reproduction: rho=-0.08811806424891734 vs established -0.08811806424891734
     |diff|=0.000e+00  PASS
FRAMES  E1 (pair A) = 8584 rows / 523 positions
        E2 (pair B) = 7719 rows / 522 positions (dropped from E1: 865 with fitness <= 0)
  eps_e = ln(f_bar_a222v) - ln(f_bar_wt) - ln(f_A222V), f_A222V = p.Ala222Val f_bar_wt = 0.6073921694038995
  construction cross-reference (expected positive):
    Spearman(eps_e, own_e_b) = +0.8021
    Spearman(eps_e, GI_e.b)  = +0.7999
SIGN-FLIP IDENTITY CHECKS:
  all-+1 flips reproduce own_e_b exactly: max|diff|=2.220e-16
  all--1 flips give exactly -own_e_b:     max|diff|=2.220e-16

N3a  PRIMARY: y = own_e_b (E1, sign-flip re-derivation null, N_PERM=10000)
  raw         delta_esm vs own_e_b
    rho=-0.0902  CI95=[-0.1229,-0.0575]  n=8584
    sign-flip re-derivation null: null mean=+0.0000 sd=0.0107 excess=-0.0903  p=<0.0001  -> SURVIVES
    null-centring: null mean IS consistent with zero
  calibrated  delta_cal vs own_e_b
    rho=+0.0339  CI95=[+0.0044,+0.0634]  n=8584
    sign-flip re-derivation null: null mean=-0.0003 sd=0.0110 excess=+0.0342  p=0.0033  -> SURVIVES
    null-centring: null mean IS consistent with zero

N3a-sec  y = GI_folinate_independent (position-block permutation, weaker null)
  raw         delta_esm vs GI e.b  rho=-0.0734  CI=[-0.1039,-0.0432]  block-perm p=<0.0001  boot p=<0.0001
  calibrated  delta_cal vs GI e.b  rho=+0.0269  CI=[-0.0012,+0.0547] (crosses 0)  block-perm p=0.0426  boot p=0.0592

N3b  NAMBIAR EQN. 4 (one-path reduction), y = eps_e (their Eqn. 3); E2; n=7719
  raw (E_raw)              vs eps_e  rho=-0.0850  CI=[-0.1170,-0.0528]  block-perm p=<0.0001
  N3b-LEVEL (phi2 level)   vs eps_e  rho=+0.0559  CI=[+0.0280,+0.0833]  block-perm p=<0.0001
  N3b-LITERAL (their phi2) vs eps_e  rho=-0.0749  CI=[-0.1067,-0.0426]  block-perm p=<0.0001

N3c  RAW vs CALIBRATED, side by side, SAME held-out rows
  pair         arm                            rho                  CI95   p_null   p_boot      n
  A_own_e_b    raw                         -0.0902 [-0.1229,-0.0575]   0.0000   0.0000   8584
  A_own_e_b    calibrated                  +0.0339 [+0.0044,+0.0634]   0.0033   0.0256   8584
  A_gi_eb      raw                         -0.0734 [-0.1039,-0.0432]   0.0000   0.0000   8584
  A_gi_eb      calibrated                  +0.0269 [-0.0012,+0.0547]   0.0426   0.0592   8584
  B_eps_e      raw (E_raw)                 -0.0850 [-0.1170,-0.0528]   0.0000   0.0000   7719
  B_eps_e      N3b-LEVEL (phi2 level)      +0.0559 [+0.0280,+0.0833]   0.0000   0.0000   7719
  B_eps_e      N3b-LITERAL (their phi2)    -0.0749 [-0.1067,-0.0426]   0.0000   0.0000   7719
  full-data raw reference (all 10757 rows): rho(delta_esm, own_e_b) = -0.088118  (reproduced, G0b)

DIAGNOSTIC  delta_cal composition (post-smoke addition, disclosed)
  Spearman(delta_cal, delta_esm               ) = -0.0307   (E1, held-out)
  Spearman(delta_cal, esm2_score              ) = +0.4139   (E1, held-out)
  Spearman(delta_cal, esm2_score_a222v_bg     ) = +0.4186   (E1, held-out)
  spread sd(delta_esm)=0.12257  sd(delta_cal)=0.08975  ratio=0.732

N3d  VERDICT (rule fixed in the docstring before running)
  raw    rho=-0.0902  CI=[-0.1229,-0.0575] p_null=<0.0001
  cal    rho=+0.0339  CI=[+0.0044,+0.0634] p_null=0.0033
  M1 |rho_cal| >= 0.26 (Nambiar calibrated band floor): NOT MET
  M2 |rho_cal| >= 2*|rho_raw| on same rows:            NOT MET
  *** SIGN CHANGE raw -> calibrated: flagged prominently ***
  -> NOT MATERIAL toward Nambiar's calibrated range (~0.26-0.38 in magnitude).

POST-HOC SENSITIVITY (disclosed — NOT part of the verdict above)
  delta_same = phi1(s_av) - phi1(s_wt): both scores through ONE curve
  post-hoc   delta_same vs own_e_b
    rho=-0.0878  CI95=[-0.1208,-0.0555]  n=8584
    sign-flip re-derivation null: null mean=-0.0000 sd=0.0106 excess=-0.0878  p=<0.0001  -> SURVIVES
    Spearman(delta_same, delta_esm) = +0.9548 (structure check)
SCRIPT 88 COMPLETE — rc=0.
```
Verdict: NOT MATERIAL — the calibration-gap explanation for this
project's small effect size is not supported, in EVERY construction
computed:
- pre-registered two-curve Nambiar-mapped shift: |rho| collapses
  0.0902 → 0.0339 and flips sign (both criteria M1/M2 fail);
- Nambiar's own epistasis with their actual contrast-phi2 (their most
  faithful replication): -0.0850 raw → -0.0749 calibrated — sign kept,
  magnitude slightly SMALLER, nowhere near 0.26-0.38;
- post-hoc single-curve calibrated shift (disclosed): -0.0878 vs raw
  -0.0902 — essentially unchanged (rank-equivalent to raw, +0.955).
The task doc's own instruction: "If it does not move materially, that is
equally important and argues against the calibration-gap explanation for
this project's small effect size." That is the result.
Files created/modified:
- scripts/88_n3_calibrated_headline.py (new)
- data/processed/task88_n3_results.csv (7 rows + meta: pair/arm/rho/
  CI/p_null/null-type/p_boot/n)
- run logs: /private/var/folders/tv/.../T/opencode/n3_full.log (run #1),
  n3_full2.log (canonical run #2)
Anything unexpected or worth flagging:
- SIGN FLIP under the two-curve construction (raw -0.0902 → cal
  +0.0339), and the composition diagnostic explains WHY: delta_cal is
  essentially no longer a shift (Spearman with delta_esm = -0.0307,
  verified independently against labeled rows: p.Val194Gly has
  delta_esm=+3.1058 but delta_cal=-0.3575). With b1=0.262004 ≠
  b2=0.143945 the difference phi2(s_av)-phi1(s_wt) is dominated by the
  curve mismatch (each score's level), not by the induced shift. This is
  a structural property of Nambiar's phi1/phi2 split on this data, found
  and disclosed — not a bug (independent re-computation reproduced every
  diagnostic value exactly: -0.0307 / +0.4139 / +0.4186, n=8584,
  sd's 0.12257/0.08975, rho +0.0339).
- The two phi2 semantics DISAGREE ON SIGN for N3b (+0.0559 level vs
  -0.0749 literal-contrast), reported plainly per the task doc; neither
  approaches Nambiar's band. The task doc's N2c (level target) and N3b
  ("exactly as they define it", whose phi2 target is the contrast) are
  genuinely in tension; both arms are in the results CSV.
- N3b-LITERAL's phi2 is nearly flat (b=0.020688, calibration R²=0.0016):
  Nambiar's contrast curve does not transfer to MTHFR at all, which by
  itself limits how far their exact protocol can be replicated here.
- own_e_b vs eps_e rank agreement +0.8021 (two independent measures of
  the same interaction) — direction checks passed, so pair A and pair B
  are comparable as intended.
- E2 lost 865 rows (fitness <= 0) relative to E1; exclusions accounted
  and printed by the script.
- The calibrated arm IS statistically nonzero (own_e_b pair: p=0.0033
  re-derivation, CI excludes 0) but tiny (+0.0339): significance ≠
  magnitude (AGENTS §3), stated here so the small positive number is not
  later mistaken for a "rescued" effect.
---

## [N4] — Does calibration change AC4's seed-instability finding? (script 89): YES — pre-registered rule fires IMPROVED
Status: PASS — both N4d conditions MET; mechanism caveat carried from N3
Time started / finished: 2026-09-25 18:43 / 18:46
What I did:
- N4a verified first: all five data/processed/task_AC4_esm1v_member{1..5}
  _scores.csv exist on disk (the staged plan deleted weights, not scores —
  confirmed rather than assumed), 12,446 rows each, columns
  [position, wt_aa, mut_aa, wt_logodds, av_logodds, delta].
- Wrote scripts/89_n4_calibration_on_seed_members.py with the N4d verdict
  rule pre-registered in its docstring BEFORE running:
    IMPROVED iff BOTH (i) calibrated delta-pair median >= 2x raw median
    AND (ii) all five calibrated delta-vs-own_e_b rhos share one sign.
- Replicated AC4d's raw machinery exactly (script 86's summ): analysis
  base gated to (10,757 rows, 654 positions); per-member join on
  [position, mut_aa], validate 1:1, wt_aa label check, zero unmatched;
  per-member position-cluster-bootstrap rhos (own_e_b primary, GI
  secondary); AC2a-convention pairwise member agreement (10 pairs); the
  five-correlations summary (AC4c).
- N4b honored: phi1/phi2 loaded from task87_calibration_params.csv, fit
  once — never refit per member. delta_cal_m = phi2(av_logodds) -
  phi1(wt_logodds).
- Attempt history: smoke N_BOOT=300 rc=0 (5.8s; machinery only) -> full
  run N_BOOT=10000 rc=0 (2m24s, canonical numbers below).
Actual output (verbatim, canonical run):
```
5/5 member CSVs present, all 12446 rows.
analysis base from task32: 10757 rows / 654 positions (expect 10757 / 654)
phi1 b=0.262004 c=11.017485; phi2 b=0.143945 c=3.953698 (loaded ... NOT refit, N4b)
ESM-2 calibration x-ranges: WT [-18.007, 7.807]  A222V [-17.808, 7.588]
R4 join: all 5 members cover the base exactly (10757 rows / 654 positions)
  member 1 score range: wt [-19.020, +6.604] ... outside ESM-2 x-range: wt 0.1% / av 0.1%
  member 2 ... 0.2% / 0.2%;  member 3 ... 0.0% / 0.0%;  member 4 ... 0.1% / 0.1%;  member 5 ... 0.2% / 0.2%
C1  MONOTONE IDENTITY ... max|diff| = 0.000e+00 PASS
R7 (AC2a convention, 10 pairs) member-pair Spearman:
  RAW    delta: min=0.003314 median=0.084365 max=0.162631
  RAW    wt   : min=0.859689 median=0.882637 max=0.890106  (AC4d printed median 0.882637)
  CALIB  delta: min=0.525389 median=0.655966 max=0.734686
  raw delta-pair median recomputed = 0.084365 (AC4d printed 0.084365)

N4c  PER-MEMBER (N_BOOT=10000, SEED=0)
  member 1 primary: raw rho=-0.020573 CI=[-0.048467,+0.006286] p=0.1400  |  CAL rho=+0.049720 CI=[+0.022765,+0.077339] p=0.0002
  member 2 primary: raw rho=-0.040820 CI=[-0.069623,-0.011940] p=0.0046  |  CAL rho=+0.020070 CI=[-0.005565,+0.045313] p=0.1302
  member 3 primary: raw rho=+0.013434 CI=[-0.014563,+0.041385] p=0.3444  |  CAL rho=+0.056799 CI=[+0.028528,+0.084683] p=0.0000
  member 4 primary: raw rho=-0.026572 CI=[-0.053779,+0.000264] p=0.0524  |  CAL rho=+0.039788 CI=[+0.011784,+0.067863] p=0.0060
  member 5 primary: raw rho=-0.003409 CI=[-0.031214,+0.024562] p=0.8194  |  CAL rho=+0.027469 CI=[+0.001748,+0.053542] p=0.0372
  (secondary GI rows also printed: CAL +0.045638/+0.015829/+0.050040/+0.032631/+0.024855)

R7c the five delta-vs-own-e.b rhos:
  RAW       : ['-0.020573', '-0.040820', '+0.013434', '-0.026572', '-0.003409']
  CALIBRATED: ['+0.049720', '+0.020070', '+0.056799', '+0.039788', '+0.027469']
  raw       : mean=-0.015588 sd=0.021052 signs 1 pos / 4 neg
  calibrated: mean=+0.038769 sd=0.015194 min=+0.020070 max=+0.056799; CIs excluding zero: 4/5; signs 5 pos / 0 neg

N4d  VERDICT (rule fixed in the docstring before running)
  (i) delta-pair median: raw=0.084365 cal=0.655966 (need cal >= 2x raw = 0.168730): MET
  (ii) all five calibrated rhos one sign: MET (5 pos / 0 neg)
  -> IMPROVED: calibration improves cross-seed agreement (raw-scale noise was inflating apparent instability).
SCRIPT 89 COMPLETE — rc=0.
```
Verdict (N4d, one sentence + mechanism): YES — calibration improves
cross-seed agreement by the pre-registered rule: members' deltas go from
median pair rho 0.084365 (essentially no agreement) to 0.655966 on the
calibrated scale, and the five delta-vs-own_e_b correlations go from
mixed signs (1 pos / 4 neg, AC4's SEED-NOISE branch) to 5/5 positive
(4/5 CIs exclude zero at N_BOOT=10000). MECHANISM CAVEAT, carried
honestly from N3's verified diagnostic: delta_cal is dominated by
score-LEVEL common mode (for ESM-2, Spearman(delta_cal, delta_esm) =
-0.0307 while levels agree across members at median 0.883), so part of
the improved agreement is inherited from WT-score agreement rather than
proving the SHIFT became seed-stable. Both facts stated; neither
swallowed.
Files created/modified:
- scripts/89_n4_calibration_on_seed_members.py (new)
- data/processed/task89_n4_results.csv (20 rows: 5 members x 2 targets x
  raw/calibrated with CIs/p)
- run log: /private/var/folders/tv/.../T/opencode/n4_full.log
Anything unexpected or worth flagging:
- RAW references reproduced EXACTLY: delta-pair median 0.084365 and
  wt-pair median 0.882637 both match AC4d's printed values to 6
  decimals — the raw arm is a verified match, so the raw-vs-calibrated
  contrast is apples-to-apples.
- ESM-1v's score scale sits inside ESM-2's calibration x-range for
  99.8-100% of rows (out-of-domain <=0.2% per member) — the fit-once
  application is not extrapolating materially; disclosed in-script.
- The calibrated members' rhos (+0.020 to +0.057) bracket N3's ESM-2
  calibrated value (+0.0339): all six model instances give a small
  POSITIVE calibrated association with own_e_b, while their raw values
  scatter around zero/negative. Consistent sign family across ESM-2 and
  all five ESM-1v members — worth quoting together in any write-up.
- member 2's calibrated primary CI still crosses zero (p=0.1302): 4/5
  not 5/5 exclude zero — reported exactly, not rounded up.
- N4 did NOT touch any AC4 output file; raw CIs are quoted from
  task_AC4_esm1v_summary.csv (AC4's own run), not recomputed.
---

## [O1] — Code-verified statement of the exact quantity being correlated: shift-vs-shift (documentation/verification)
Status: PASS — record CONFIRMED, no correction needed; the headline is shift-vs-shift, not raw-vs-raw
Time started / finished: 2026-09-25 18:46 / 18:49
What I did:
- O1a only (documentation task, no new analysis): read the actual code
  that builds both sides of the headline correlation — scripts 32, 16,
  17, 33, and scripts/lib/own_context.py — and quoted every load-bearing
  line verbatim rather than paraphrasing from memory.
Actual output (verbatim quotes from the code, in the order the
construction happens):

**THE PARAGRAPH (the deliverable):** The project's headline statistic is
a Spearman correlation between two background-induced SHIFTS —
shift-vs-shift, not raw-vs-raw. On the model side, delta_ESM is the
difference of two ESM-2 relative log-likelihoods for the SAME variant
computed in the two backgrounds: script 32's docstring states it
"delta_ESM(v) = S(v | A222V background) - S(v | WT background)" and
calls it "ESM-2's OWN predicted interaction term: the change in the
model's assessment of v caused by supplying the A222V background…
interaction-vs-interaction"; script 16 builds it literally as
`df["model_A"] = df["esm2_score"]`,
`df["model_C"] = df["esm2_score_a222v_bg"]`,
`df["delta_esm"] = df["model_C"] - df["model_A"]`, so only the
difference (the shift) enters the correlation — no raw ESM-2 score is a
variable of the pair. On the measured side, own_e_b is not a raw fitness
level either: scripts/lib/own_context.py's fit_interaction docstring
defines it as "the deviation of the A222V-background arm from the
multiplicative no-interaction expectation", computing
`expected(c) = sm * a222v_line` ("single_mutant_term(c) *
(b_A222V + c*r_A222V) [+ correction]"), then
`resid = np.where(valid, m_score - expected, np.nan)` and
`e_b, e_r, df = wls_line(resid, m_se, concs, valid)`, where wls_line is
"weighted least squares of y ~ 1 + x, weights 1/se^2 … Returns
(intercept, slope, df)" — i.e. own_e_b is the concentration-independent
INTERCEPT of the weighted line through the four per-concentration
residuals (m12/m25/m100/m200 measured A222V-background condition scores
minus the no-interaction expectation), a signed offset of observed
double-mutant fitness from expectation. Script 17 writes it
(`own_e_b = e2["e_b"]`, two-pass with the fitness-dependent bias
correction) to own_context_metrics.csv; script 32 merges it and runs
`PAIRS = [("delta_esm", "GI_folinate_independent", "signed, published
e.b"), ("delta_esm", "own_e_b", "signed, own e_b"), …]` through
`position_cluster_bootstrap(sub, "position", xc, yc, …)`. Script 33 does
not redefine either quantity — it re-derives the outcome under the null:
"multiply each variant's per-concentration residuals by independent
random +/-1, refit, and recompute the population correlation.
Everything stays inside one variant's own data -- no cross-variant
pairing", guarded by the identity gate
`if np.abs(chk_p[ok] - own_eb[ok]).max() > 1e-6: "*** SANITY CHECK FAILED
-- row alignment is wrong. Stop here. ***"`. Both variables are signed;
both are shifts (a model-side score difference; a measured-side
fitness offset from a multiplicative expectation built partly from raw
quantities — constructed FROM raw condition scores, but itself a
residual/offset, not a raw level). The record is therefore correct as
stated: the review's "raw scores vs raw fitness" reading is not what the
code does. One addition from this session: script 88's calibrated arm
inherits the same shift-vs-shift structure —
delta_cal = phi2(esm2_score_a222v_bg) − phi1(esm2_score) — but with
N3's verified caveat that under two differently-fitted curves the
difference is dominated by score-level common mode (Spearman with
delta_esm = −0.0307), so any write-up describing N3 must say
"calibrated score difference", not "calibrated shift", without that
qualifier.

Verdict: CONFIRMED shift-vs-shift; no correction to the record needed.
The one wording caveat that DOES apply is the N3 delta_cal qualifier in
the paragraph above (disclosed there and in the N3 entry).
Files created/modified:
- None (read-only verification). Files read: scripts/32_delta_esm_primary.py
  (docstring L12-21, PAIRS L91-95, bootstrap L101), scripts/16_phase5_model_abc.py
  (L49-52), scripts/17_build_own_context.py (L43-48, L80-88),
  scripts/33_delta_esm_signflip_null.py (docstring L4-9, identity gate L75-85,
  null loop L94-101), scripts/lib/own_context.py (wls_line L48-66,
  fit_interaction L143-187).
Anything unexpected or worth flagging:
- Nothing contradicted the documented construction. The only nuance is
  the one already flagged: own_e_b is an offset FROM an expectation that
  contains the p.Ala222Val reference line (script 17 prints: "this
  single reference line enters EVERY variant's expectation… shifts the
  location of the e_b distribution but not rank order, and every
  downstream test here is rank-based") — common-mode, rank-invariant,
  and irrelevant to a Spearman correlation, but stated here so the
  construction description is complete.
---
