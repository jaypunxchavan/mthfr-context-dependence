# RBD replication of the background-shift design - pre-registration v1

Frozen 2026-10-01, before any RBD data is downloaded or scored. Authors: Arnav (PI), Claude (planning).

## 1. Question

In MTHFR, the ESM-2 background-shift statistic for the single-substitution background A222V correlated with A222V's measured epistatic shift, and that correlation was more extreme than for arbitrary
placebo backgrounds. Does the same design, applied to the two genuine single-substitution backgrounds in the Starr et al. 2022 SARS-CoV-2 RBD deep mutational scans (Alpha = N501Y, Eta = E484K, each against Wuhan-Hu-1),
produce a target correlation that is extreme relative to placebo backgrounds? This replicates the DESIGN, not any MTHFR number, and makes no claim about MTHFR.

## 2. Data

Starr et al., Science 377:420-424 (doi:10.1126/science.abo7896); the authors' public repository jbloomlab/SARS-CoV-2-RBD_DMS_variants. File and column names are recorded in the implementation log, not guessed here.
Phenotype PRIMARY: ACE2 binding (the per-mutation effect on log10 KD as the authors define it). SECONDARY: expression. A mutation is usable for a target T only if it is measured in both T and Wuhan-Hu-1 with barcode
count n_bc >= 3 in each (sensitivities n_bc >= 1 and >= 5, reported, none selected). Target site excluded from the variant set for everyone.

## 3. Quantities

e_T(v) = x_T(v) - x_Wuhan(v) for T in {N501Y, E484K}, over single substitutions v at sites other than T's site.
delta_b(v) = S(v | b) - S(v | Wuhan-Hu-1 RBD), S = ESM-2 650M masked-marginal log-odds against the wild-type residue, one unbatched forward pass per (background, site), over the RBD construct's sites.
rho_b^T = Spearman(delta_b, e_T) over variants v at sites other than b's own site and T's site.

## 4. Backgrounds (fixed before scoring, fitness-blind)

For each target T: Arm S_T = the 18 other substitutions at T's site (not the wild type, not T's own substitution). Arm V_T = T's substitution type (N to Y for N501Y; E to K for E484K) at every other site of the
construct with the same wild-type residue; if more than 60, a seed-0 sample of 40. Arm G (shared by both targets) = 40 backgrounds, each a single substitution at a distinct site, drawn with
numpy.random.default_rng(0), site uniform among the construct's sites excluding 484 and 501, mutant uniform among the 19 non-wild-type residues. The null set for T is N_T = V_T u G; the OTHER target's background is excluded from N_T.
The two target backgrounds are scored. The roster is written and hashed before scoring, and ordered by interleaving the arms round-robin so that any completed prefix is balanced.

## 5. Primary test and outcome words (numeric, fixed now)

p_abs(T) = (1 + #{b in N_T : |rho_b^T| >= |rho_T^T|}) / (1 + |N_T|). Direction is not assumed (the MTHFR sign is not carried over). Also reported: p_neg (rho_b <= rho_T) and p_pos (rho_b >= rho_T).
RBD-REPRODUCES for T iff p_abs(T) <= 0.05. RBD-DOES-NOT-REPRODUCE iff p_abs(T) > 0.10. RBD-INCONCLUSIVE otherwise. Two targets are two looks; both are reported with no multiplicity adjustment and that is stated.

## 6. Secondary analyses (descriptive; none changes the outcome words)

(a) rho_T^T with a corrected position-cluster bootstrap CI (clusters = sites; 10,000 draws; seed 0). (b) The shift-magnitude confound: Spearman(rho_b, mean|delta_b|) across all backgrounds (background-level bootstrap) and a leave-one-out
OLS shift-adjusted p_spec_adj. (c) Locality: Spearman(rho_b, |site_b - site_T|) across N_T u S_T, and the same with 3D distance if a structure of the RBD is obtainable (PDB 6M0J, RBD chain) with numbering verified against the sequence; otherwise sequence distance only.
(d) T's rank within S_T u {T} (a rank fraction, not a test). (e) Split-half stability: sites split in two halves by seed 0; p_abs recomputed on each half. (f) Measurement reliability of e_T: correlation between per-library estimates if per-library columns exist.
(g) The expression-phenotype version of every quantity. (h) The multidms target e_T^MD, used only if its held-out predictive Pearson correlation is >= 0.5 for each of the Wuhan, Alpha and Eta conditions (a judgment constant fixed now); reported next to the primary, never replacing it.

## 6b. multidms

multidms (bioRxiv doi:10.1101/2023.07.31.551037) identifies a shared global nonlinearity only from multi-mutant variants. It is fitted on the RBD per-variant data for the Wuhan, Alpha and Eta conditions in a separate environment, under a wall-clock cap. Failure to install, to converge, or to meet
the held-out criterion is an acceptable outcome and is reported as such.

## 7. Gates (a failed gate stops the module; thresholds are never loosened)

G-R1 Alpha differs from Wuhan-Hu-1 in the RBD by exactly N501Y and Eta by exactly E484K in the data's own reference sequences. G-R2 every data row's wild-type residue equals the sequence residue at its site. G-R3 the bootstrap routine passes the identity, draw-by-draw reference
and Phase 1 CI reproduction gates. G-R4 each background scores at least 95% of the construct's eligible sites. G-R5 scoring the same background twice gives identical values (1e-6) and the wild-type residue's log-odds is 0 at every scored site. G-SYN the analysis pipeline recovers a
planted signal and a planted null on synthetic scores built from the real e_T.

## 8. Wording and disclosure

No RBD result may be described as confirming, supporting or undermining any MTHFR or GB1 result; the systems, backgrounds, phenotypes and platforms differ. The design was fixed before any RBD datum was downloaded. Any deviation is disclosed and, if it changes a rule or constant,
requires a new versioned pre-registration, never an edit to v1.
