# Predictive utility of background conditioning - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Authors: Arnav (PI), Claude (planning).

## 0. Disclosure

Cached-data analyses on variables for which related correlations were seen earlier; the comparisons below were never computed, but the analyses are not out-of-sample with respect to the project's history.

## 1. Question

Does conditioning ESM-2 on the A222V background (S_A) predict anything better than the plain WT-background score (S_W)? Two uses: (U-1) predicting A222V-background fitness; (U-2) separating pathogenic from reference variants using the benchmark of Weile et al. 2021.

## 2. U-1

Rows: the 10,757-row frame. Response y: the per-variant mean of the A222V-background fitness (m_score) over the four folinate conditions with finite values; descriptive repeats for each condition and on H. Predictors: S_A and S_W. Statistic: Delta = Spearman(S_A, y) - Spearman(S_W, y) on identical rows with a paired position-cluster bootstrap CI (10,000 draws, SEED 0).
Subsets: all rows (PRIMARY), H rows, and the rows in the top decile of |own_e.b|. Context rows: Spearman(S_W, base functionality) and Spearman(S_A, y).
Outcome words (PRIMARY): CONDITIONING-HELPS iff the CI lies entirely above zero; CONDITIONING-HURTS iff it lies entirely below zero; EQUIVALENT iff it lies inside (-0.02, +0.02); INCONCLUSIVE otherwise.

## 3. U-2

Data: the eight experimental maps and the reference variant sets of Weile et al. 2021 (MaveDB urn:mavedb:00000049 and the paper's supplement). If the pathogenic reference set cannot be obtained, the fallback is the project's ClinVar overlap file (pathogenic or likely pathogenic versus benign or likely benign), disclosed as a different label set. Variants: those with a label and finite S_W and S_A.
Predictors: S_W, S_A and, as positive controls, the experimental A222V-background map at 25 ug/mL folinate and the WT-background map at the lowest folinate. Metrics: AUROC (PRIMARY) and the area under the balanced precision-recall curve (balanced precision = TPR / (TPR + FPR)); paired position-cluster bootstrap CIs (10,000 draws) on Delta AUROC = AUROC(S_A) - AUROC(S_W).
Outcome words (PRIMARY, Delta AUROC): as U-1 with the same margin of 0.02. UNDERPOWERED iff either class has fewer than 15 variants; then no word is given and the CI is reported.

## 4. Gates

G-U0 the prereg hash; frame rows 10,757 / 654; Spearman(own_e.b, S_W) = +0.0854 reproduces (4 dp). G-U1 the MaveDB A222V-background 25 ug/mL scores correlate with the project's own A222V-background fitness for that condition at Spearman >= 0.90 over shared variants (otherwise the maps are not the same data: stop U-2).
G-U2 among the experimental maps the A222V-background 25 ug/mL map attains the highest area under the balanced precision-recall curve on the label set (the ordering Weile et al. report); if not, U-2 is reported UNVERIFIED-LABELS with no word. G-U3 the AUROC and balanced-PR implementations agree with scikit-learn on toy data (1e-12) and the bootstrap passes the reference gate.

## 5. Wording

Statements concern ESM-2 scores in this one gene; there is no claim about clinical use.
