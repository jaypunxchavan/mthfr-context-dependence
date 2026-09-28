# PHASE 2 — Full-frame placebo-background test: pre-registration v1

Frozen 2026-09-27, before any Phase 2 scoring. Authors: Arnav (PI), Claude (planning).

## 1. Question

Over the full 654-position frame, is the ESM-2 background-shift anchor for A222V (ρ = −0.088118,
delta_ESM vs own_e_b) distinguishable from what arbitrary single-substitution backgrounds
produce against the same target?

## 2. Statistic

For each background b: delta_b(v) = S(v | b) − S(v | WT). ρ_b = Spearman(delta_b, own_e_b), where
own_e_b is A222V's own measured e.b (the anchor's target), over all usable variants in the
10,757-row frame, excluding rows whose target position equals the background's position.
A222V's own ρ must reproduce the anchor (gate G-A).

## 3. Arms (fixed before scoring; all fitness-blind)

- **Arm S (same-site):** the 18 substitutions A222X, X not in {A, V}.
- **Arm V (same-substitution):** A→V at every alanine position other than 222 present in the
  frame. If the number of such positions exceeds 60, use a seed-0 random sample of 40
  (`numpy.random.default_rng(0).choice(sorted_positions, 40, replace=False)`). This condition
  is decided by the position count alone.
- **Arm G (generic):** 40 backgrounds, each a single substitution at a distinct frame position
  other than 222, position drawn uniformly and mutant amino acid uniformly among the 19
  non-wild-type residues, using `default_rng(0)`; drawn and written to disk before any scoring.

**Null set N = Arm V ∪ Arm G.** Arm S shares A222V's site and is **not** a null; it is reported
as a separate comparison arm.

## 4. Inference

Position-cluster bootstrap (positions as clusters, all variants with multiplicity),
N_BOOT = 10000, seed 0, for all ρ_b confidence intervals.
One-sided empirical p (direction pre-stated negative, as for the anchor):
**p_spec = (1 + #{b in N : ρ_b ≤ ρ_A222V}) / (1 + |N|)**, computed on
(a) the full frame and (b) the held-out set H = frame positions not in the Phase 1 F1 AE or W
frames (ρ recomputed on H rows only, for A222V and every background). H was never used in F1
and is the out-of-sample evaluation of the hypothesis raised by F1's post-hoc AE1/AE2
decomposition.

## 5. Decision rule (constants are judgment constants, fixed now)

- **GENERIC:** p_spec(full) > 0.10.
- **A222V BEATS NON-SITE BACKGROUNDS:** p_spec(full) ≤ 0.05 **and** p_spec(H) ≤ 0.10.
- **INDETERMINATE:** everything else, including full and H disagreeing.

Wording rule: only the second outcome may be written up as supporting background-specificity of
the anchor. GENERIC and INDETERMINATE must be reported with equal prominence in every write-up.

Reported irrespective of the outcome above:
- **Site contrast:** D_site = mean ρ_b(Arm S) − mean ρ_b(N), with position-cluster bootstrap 95%
  CI and a label-permutation p (10,000 shuffles). Interpretation: D_site < 0 means a shared site
  tracks A222V's e.b beyond arbitrary backgrounds; that is compatible with a real site-specific
  effect and is not evidence of substitution-specificity.
- **Within-site gradient:** T = Spearman(ρ_b, Grantham distance(X, V)) over Arm S, position-cluster
  bootstrap 95% CI, leave-one-out range, and the minimum detectable |T| ≈ 2.8 × bootstrap SE.
  SUPPORTED iff CI lower bound > 0 and T > 0 in every leave-one-out fit; REVERSED iff CI upper
  bound < 0; otherwise NOT RESOLVED, reported as "n = 18 cannot resolve this," never as "flat."

## 6. Secondary (non-decision) analyses

The same analysis after residualizing delta_b and own_e_b on region indicators (Phase 1 H1 found
region 4 differs systematically); and per-arm summary tables (n, mean, median, range).

## 7. Gates (a failed gate stops the run; thresholds are never loosened)

- **G-A:** A222V's ρ over the full frame reproduces −0.088118 to 1e-6.
- **G-B:** for at least three backgrounds already cached in `task82_ae_raw.csv`, freshly scored
  values on the cached positions reproduce the cached scores to 1e-6 (same model, same settings).
- **G-C:** no row with target position equal to background position enters any ρ_b.
- **G-D:** bootstrap identity (every cluster once reproduces the point estimate to 1e-12).
- **G-E:** each background scores at least 95% of the frame's positions.

## 8. Execution

Detached (`nohup`), one output file per background, resumable; the foreground harness kills
jobs at roughly 55–65 minutes. Smoke run first (N_BOOT = 300), then full.

## 9. Disclosure

The AE1/AE2 split that motivates this test was observed in Phase 1 after F1 was run (POST-HOC).
Confirmatory weight therefore rests on this frozen rule and on the held-out set H, not on the
Phase 1 numbers. Any deviation from this document must be disclosed in the log and, if it
changes a rule or constant, requires a new versioned pre-registration (v2), never an edit to v1.
