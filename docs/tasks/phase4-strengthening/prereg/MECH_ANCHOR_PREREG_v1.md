# MTHFR anchor: mechanism-matched analyses - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Authors: Arnav (PI), Claude (planning).

## 0. What this is, and what it is not

These analyses use cached data and quantities already seen in earlier exploratory work (the anchor, the shift-magnitude confound, the Phase 1 partial correlations). The constructions and outcome words below are fixed before the specific new quantities are computed, but the analyses are NOT
independent of what was already seen; the out-of-sample evidence in this programme comes only from the neighbour-arm and model-ladder pre-registrations. Nothing here changes the frozen Phase 2 verdict.

## 1. Convention and question

own_e.b is positive when a variant is fitter in the A222V background than the project's expectation from the WT-background map. delta = S_A - S_W (S_A: the ESM-2 score with A222V present; S_W: the WT-background ESM-2 score) is positive when ESM-2 scores a variant as more tolerated with A222V present.
The anchor rho = Spearman(delta, own_e.b) = -0.088118 (n = 10,757 variants, 654 positions) is negative: the model's shift runs OPPOSITE to the measured shift. Phase 1 measured rho(delta, S_W) = -0.3238 and rho(own_e.b, S_W) = +0.0854 and a linear partial correlation controlling S_W of -0.0641
(72.8% retained). This pre-registration asks (i) how much of the anchor and of its placebo separation survives removal of the channels through S_W and the base functionality, (ii) how much a zero-epistasis world with the same measurement noise and the same data pipeline would produce,
(iii) what true correlation the pipeline could detect, (iv) whether the anchor lives between positions or within them, and (v) how stable the frozen placebo test is to resampling positions.

## 2. Common definitions

Rows, frames and views are exactly script 125's construction (frame: 10,757 rows / 654 positions; held-out view H: 455 positions / 7,526 rows; each background's rows exclude its own position). Backgrounds: A222V and the 96 Phase 2 backgrounds (Arm V 38, Arm G 40, Arm S 18); the null set N = V u G (78).
rho_b = Spearman(delta_b, own_e.b) over a background's rows. p_spec(neg) = (1 + #{b in N: stat_b <= stat_A222V}) / (1 + 78); p_spec(abs) uses |stat|. Position-cluster bootstrap for statistics computed inside one background; background-level bootstrap across backgrounds; N_BOOT 10,000 and SEED 0 unless stated.
Every bootstrap routine passes identity, draw-by-draw reference (1e-12) and Phase 1 CI reproduction gates.

## 3. Analyses

M-1 Partial-correlation placebo test. PRIMARY control: S_W. SECONDARY control: S_W and the base functionality (the second covariate of Phase 1's R1 and L2). The partial Spearman is the Pearson correlation of the OLS residuals of the average ranks of delta_b and own_e.b on the average ranks of the controls, over a background's rows.
Report, for A222V and every background, the partial rho_b; the A222V partial with a position-cluster bootstrap CI; p_spec(neg) and p_spec(abs) on the full frame and on H; the shift-adjusted p_spec_adj on the partial rho_b (leave-one-out OLS on mean|delta_b|, as Diagnostics II D9); and the retained fraction (partial / raw).
Outcome words (primary control, A222V partial): PARTIAL-SURVIVES iff the CI excludes zero in the negative direction AND p_spec(neg) <= 0.05 (full) AND <= 0.10 (H). PARTIAL-WEAKENS iff the CI excludes zero in the negative direction but a p_spec condition fails. PARTIAL-DOES-NOT-SURVIVE iff the CI includes zero or the sign reverses.

M-2 Stratified correlation (sensitivity; no word). Rows are cut into deciles of S_W (equal-count over the frame); the stratified rho is the weighted mean (weights = rows in the decile) of the within-decile Spearman. Report for A222V (position-cluster bootstrap CI) and p_spec(neg) on the full frame and on H using the stratified rho_b.

M-3 Zero-epistasis simulation null (A222V only). Per draw r = 1..1000 (SEED 0): w*_i = w_i (the WT-background fitness exactly as script 153 defines it, used as the proxy truth); w^sim_i = w_i + N(0, sw_i^2), where sw_i is the per-variant WT-background standard error if the project's data carries one; if it does not, sw_i = 0 (PRIMARY) and a sensitivity uses
sw_i = the median m_se over the frame; m^sim_ic = E_c^iso(w*_i) + N(0, m_se_ic^2), with E_c^iso the cross-fitted isotonic expectation of script 153 (GE-ISO). By construction there is no background-specific epistasis, only a monotone nonlinear relation plus noise. The project's own unmodified pipeline (linear expectation, weighted aggregation across conditions) rebuilds
own_e.b^sim from (w^sim, m^sim); rho^sim_r = Spearman(delta_real, own_e.b^sim_r) over the frame rows. Sensitivity: the generating relation linear (E_c^lin). Report the mean, SD, 2.5th and 97.5th percentiles of rho^sim, the fraction of draws at or below -0.088118, and mean(rho^sim) / (-0.088118).
Outcome words: EXCESS-OVER-ARTIFACT iff -0.088118 is at or below the 2.5th percentile of the primary simulation; CONSISTENT-WITH-ARTIFACT otherwise. The sensitivities are reported with no word.

M-4 Detection limit by planting. As M-3 (primary generating relation) plus a planted term e_plant_i = s_e (r0 z_i + sqrt(1 - r0^2) u_i) added to m^sim_ic for every condition, where s_e = the SD of the recorded own_e.b, z_i = the standardised rank-normal score of delta_real(i), u_i ~ N(0,1) independent, and r0 in {-0.30, -0.20, -0.10, -0.05, 0, +0.05, +0.10, +0.20, +0.30} is the planted true correlation; 200 draws per r0.
Report the mean observed rho and power(r0) = the fraction of draws beyond the 2.5th / 97.5th percentile of the r0 = 0 simulation (lower tail for r0 < 0, upper for r0 > 0); the minimum detectable |r0| at 80% power (linear interpolation; "above the grid" if none reaches it); and the attenuation slope (mean observed rho against r0 over the grid). No word.

M-5 Between- and within-position decomposition. Positions with at least 5 rows in the view qualify. rho_between = Spearman across qualifying positions of the mean delta against the mean own_e.b. rho_within = the mean over qualifying positions of the within-position Spearman, weights = rows in the position, undefined positions skipped.
Report both for A222V (position-cluster bootstrap CI, both components recomputed per resample) and for every background; p_spec(neg) per component on the full frame and on H. Surrogate nulls (1,000 draws each, SEED 0): S1 permutes own_e.b among rows within each position (keeps position-level structure); S2 permutes own_e.b among rows within each of 10 equal-count bins of 3D distance to residue 222 over the resolved positions, unresolved positions forming an eleventh bin
(keeps only the regional profile). Report the anchor under S1 and S2 as mean, 95% range and as a fraction of -0.088118.
Outcome words (full frame, A222V): WITHIN-CARRIED iff rho_within's CI excludes zero in the negative direction AND its p_spec(neg) <= 0.05 AND the between component does not meet both conditions. BETWEEN-CARRIED iff the reverse. BOTH-CARRY iff both meet both conditions. NEITHER-CARRIES otherwise.

M-6 Stability of the frozen placebo test. Position-cluster bootstrap of the whole test: per draw resample positions with replacement (frame: 654; H: 455), recompute rho_A222V and all 78 null rho_b on the resampled rows, and p_spec(neg) and k = #{b in N: rho_b <= rho_A222V}; 2,000 draws (SEED 0) per view. Report the distribution of k, P(p_spec <= 0.05) on the full frame, P(p_spec <= 0.10) on H,
and the standardised effect z = (rho_A222V - mean rho_N) / SD rho_N with its bootstrap CI.
Outcome words, per view: STABLE iff the probability is >= 0.80; FRAGILE iff it is < 0.50; MODERATE otherwise.

## 4. Gates (hard; a failed gate stops that analysis and nothing is loosened)

G-M0 the prereg hash, the rho table sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796 and the 3D table sha256 69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de. G-M1 A222V rho -0.088118064 (full) / -0.090021683 (H); p_spec 2/79 and 4/79 with the named beaters.
G-M2 the Phase 1 partials reproduce: the linear S_W-only partial -0.06414804421216103 (1e-12) and the two-covariate linear partial -0.0829 (4 dp). G-M3 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction. G-M4 simulation identity: with every noise term zero and E_c replaced by the observed m, the pipeline returns the recorded own_e.b (1e-12).
G-M5 planting response: the mean observed rho is non-decreasing in r0 across the grid up to Monte-Carlo error (a more negative planted correlation must produce a more negative observed rho; under the convention in section 1 an agreeing model would give a positive rho). G-M6 toy gates for the stratified statistic and the decomposition. G-M7 the stability bootstrap with every position exactly once returns the observed p_spec and k.

## 5. Wording and disclosure

The negative anchor is described only as the model's shift running opposite to the measured shift, never as agreement. No result here may be described as confirming or undermining a GB1, RBD, neighbour-arm or model-ladder result. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
