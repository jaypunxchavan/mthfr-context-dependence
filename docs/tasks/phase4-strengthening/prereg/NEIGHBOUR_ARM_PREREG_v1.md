# Position versus region: neighbour arm - pre-registration v1

Frozen 2026-10-02, before any new background is selected or scored. Authors: Arnav (PI), Claude (planning). This is NEW data and an out-of-sample test.

## 1. Question

A222V's background shift correlates with its measured epistasis (rho = -0.0900 on the held-out frame H) more strongly than most placebo backgrounds, but backgrounds at nearby positions behave similarly, and sequence distance and 3D distance to residue 222 are collinear. Is A222V's rho extreme relative to backgrounds at spatially nearby positions (position-specific), or typical of its neighbourhood (region-like)?
And is the locality gradient carried by 3D distance, by sequence distance, or by both?

## 2. Geometry

From PDB 6FCX chain A (the loader of Diagnostics II script 139): d3(p) = Calpha-Calpha distance from residue p to residue 222; dseq(p) = |p - 222|. Eligible positions: frame positions that are resolved in 6FCX chain A, other than 222. Cells: C1 near-near (d3 <= 12 and dseq <= 20); C2 3D-near and sequence-far (d3 <= 12 and dseq > 40);
C3 sequence-near and 3D-far (d3 > 18 and dseq <= 25); C4 far-far (d3 > 20 and dseq > 40), represented by the existing nulls, nothing new scored there.

## 3. Backgrounds (fixed before scoring, fitness-blind)

All eligible positions per cell are listed with their cell membership before any draw. New backgrounds are single substitutions. Alanine first: every eligible alanine in C1 and C2 receives A->V (the substitution type of A222V). Remaining slots are filled by positions drawn with numpy.random.default_rng(0) from the cell's eligible positions not already used, each with a mutant drawn uniformly from the 19 non-wild-type residues from the same generator.
Caps on new backgrounds: C1 16, C2 28, C3 10 (all eligible positions if fewer). No (position, mutant) pair already among the 96 existing backgrounds or A222V is reused. The roster (cell, position, mutant, d3, dseq, with the scoring order interleaved round-robin across cells so that any completed prefix is balanced) is written and hashed before scoring.

## 4. Scoring

ESM-2 650M, masked-marginal, one unbatched forward pass per (background, position). PRIMARY frame: the 455 held-out positions H, minus the background's own position; delta uses the cached WT-background ESM-2 score. SECONDARY frame: the remaining 199 non-H positions, scored in a later stage so that the full 654-position frame completes.

## 5. Primary test and words

The neighbourhood null set NB = the new backgrounds in C1 and C2 plus the existing nulls with d3 <= 12 (six: G_I192T, AV_220, AV_155, AV_195, G_L178T, AV_175). rho_b is Spearman(delta_b, own_e.b) over a background's rows on H (A222V: -0.090021683). p_NB(neg) = (1 + #{b in NB: rho_b <= rho_A222V}) / (1 + |NB|); p_NB(abs) uses |rho|.
POSITION-SPECIFIC iff |NB| >= 30 AND p_NB(neg) <= 0.05. REGION-LIKE iff |NB| >= 30 AND p_NB(neg) > 0.10. UNRESOLVED iff |NB| >= 30 and 0.05 < p_NB(neg) <= 0.10. UNDERPOWERED iff |NB| < 30 (no interpretation). The same-site rank (A222V among the 18 Arm S, 2/19) is reported beside it. The full-frame version is computed when the secondary frame completes (secondary; no word).

## 6. Separating the two distances

Pool P = all new backgrounds plus the existing nulls with a resolved d3 (67); rho_b on H. The partial Spearman of rho_b with d3 controlling dseq, and with dseq controlling d3, each with a background-level bootstrap CI (10,000, SEED 0). Cell means of rho_b with CIs for C1, C2, C3 and C4 (the existing nulls with d3 > 20 and dseq > 40), and the contrasts C2 - C4 (3D-near, sequence-far versus far-far)
and C3 - C4 (sequence-near, 3D-far versus far-far) by background-level bootstrap.
3D-LOCAL iff the d3 partial's CI excludes zero and the dseq partial's CI includes zero. SEQUENCE-LOCAL iff the reverse. BOTH-LOCAL iff both exclude zero. NEITHER-RESOLVED iff both include zero.

## 7. Gates

G-N0 the prereg hash; the geometry loader reproduces the stored d3 for the 67 resolved existing nulls (max |diff| < 1e-6) and the cell counts are printed before the draw. G-N1 the roster is written, hashed and re-read before any scoring; no duplicate pairs; counts per cell. G-N2 the new scorer reproduces the cached rows of an existing background (AV_220) on H to 1e-6 including delta; scoring the same background twice is identical (1e-6); the wild-type residue's log-odds is 0.
G-N3 each new background scores at least 95% of its eligible H positions. G-N4 planted gates on the analysis, on the real geometry: synthetic rho_b = a + b d3 + noise returns 3D-LOCAL, = a + b dseq + noise returns SEQUENCE-LOCAL, = noise returns NEITHER-RESOLVED (fire rate <= 0.15 over 100 draws). G-N5 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 8. Wording and disclosure

POSITION-SPECIFIC and REGION-LIKE describe A222V relative to the sampled neighbourhood in this protein only. A222V's own measured epistasis is the only target and all backgrounds are scored against it, as in Phase 2. Any deviation is disclosed and, if it changes a rule or constant, requires a new versioned pre-registration, never an edit to v1.
