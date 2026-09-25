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
