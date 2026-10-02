# MTHFR global-epistasis-aware target - pre-registration v1

Frozen 2026-10-01, before the alternative target is computed. Authors: Arnav (PI), Claude (planning).

## 1. Question

The anchor is rho = Spearman(delta_ESM, own_e.b) = -0.088118 over 10,757 variants at 654 positions. own_e.b is the 1/m_se^2-weighted WLS intercept, across conditions c in {12, 25, 100, 200}, of residuals r_c = m_score_c - expected_c from the project's two-pass
interaction fit, where the expectation is a LINEAR function of the WT-background fitness w. If the relation between the two backgrounds' maps is monotone but nonlinear (global epistasis, for example floor and ceiling effects), a linear expectation leaves residuals that depend on a variant's severity and
can be mistaken for background-specific epistasis. This asks whether the anchor and its placebo separation survive when own_e.b is rebuilt against a monotone expectation. It changes no frozen Phase 2 result; it re-targets the anchor.

## 2. Construction

2.1 Reuse the project's own construction (rebuild_interaction_fit and the weighted aggregation of per-condition residuals) unchanged except for one pluggable component, the per-condition expectation E_c(v) as a function of w(v). The code is quoted in the log.
2.2 Identity: with the project's own linear expectation plugged in, the rebuild reproduces the recorded own_e.b for all 10,757 rows to 1e-12.
2.3 PRIMARY (GE-ISO): E_c is the isotonic (non-decreasing) regression of m_score_c on w, weights 1/m_se^2, fitted by 5-fold cross-fitting with folds defined by POSITION (positions permuted with a seed-0 generator, fold = rank mod 5); a variant's expectation comes from the fit that excluded its position.
2.4 SENSITIVITY (GE-SIG): E_c is a four-parameter logistic a + b / (1 + exp(-k (w - m))), weighted least squares, same folds.
2.5 SENSITIVITY (GE-LIN-CF): the project's own linear expectation, cross-fitted with the same folds, so that any change can be attributed to monotonicity and not to cross-fitting.
2.6 r_c^GE = m_score_c - E_c(w); own_e.b^GE = the project's aggregation of r_c^GE across conditions.

## 3. Quantities reported (for GE-ISO, GE-SIG and GE-LIN-CF, side by side)

(a) Spearman(own_e.b^GE, own_e.b) over the 10,757 rows.
(b) rho^GE = Spearman(delta_ESM, own_e.b^GE) with a corrected position-cluster bootstrap CI (clusters = positions; 10,000 draws; seed 0), next to -0.088118, and the shrinkage 1 - rho^GE / rho.
(c) All 96 Phase 2 backgrounds' rho_b^GE (cached delta_b; the same row construction and own-position exclusion as script 125) and the frozen-construction p_spec^GE = (1 + #{b in N : rho_b^GE <= rho^GE}) / (1 + |N|), N = Arm V u Arm G (78), on the full frame and on the held-out set H (455 positions), with the at-or-below nulls named.
(d) The shift-adjusted p_spec_adj^GE (leave-one-out OLS on mean|delta_b|, as Diagnostics II D9).
(e) A222V's rank within Arm S u {A222V} on rho_b^GE (a rank fraction, n = 19, not a test).
(f) Spearman(rho_b^GE, d3_b) across the 67 resolved nulls with a background-level bootstrap CI, next to +0.7316.

## 4. Outcome words (numeric, fixed now; none is a frozen Phase 2 verdict word)

GE-SURVIVES: the CI of rho^GE (GE-ISO) excludes zero in the negative direction AND p_spec^GE(full) <= 0.05 AND p_spec^GE(H) <= 0.10.
GE-WEAKENS: the CI excludes zero in the negative direction but at least one p_spec^GE condition fails.
GE-DOES-NOT-SURVIVE: the CI includes zero or the sign reverses.
The primary governs; the two sensitivities are reported with the same words, and any disagreement is stated plainly.

## 5. Gates (hard)

G-M1 identity (2.2). G-M2 each fitted monotone expectation is non-decreasing in w on a grid. G-M3 the bootstrap passes the identity, draw-by-draw reference and Phase 1 CI reproduction gates. G-M4 the Phase 2 reproduction rows: A222V rho -0.088118064 (full) / -0.090021683 (H); frozen p_spec 2/79 and 4/79; the rho table sha256 e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796.
G-M5 fold integrity: every position in exactly one fold, every variant predicted by a fit that excluded its position.

## 6. multidms on MTHFR

multidms identifies a global nonlinearity only from multi-mutant variants. It is attempted on the MTHFR data only if the audit finds at least 5,000 variants carrying two or more amino-acid substitutions. Otherwise the monotone expectation of section 2 is the global-epistasis-aware refit for MTHFR, and multidms is confined to the RBD data.

## 7. Wording and disclosure

No result here may be described as confirming or undermining a GB1 or RBD result. The construction was fixed before the alternative target was computed. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
