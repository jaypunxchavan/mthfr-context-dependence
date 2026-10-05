# GB1 locality of model shifts versus measured epistasis - pre-registration v1

Frozen 2026-10-02, before any quantity below is computed. Uses the 400 scored backgrounds of the GB1 regime map (v2). The Phase 3 results for those backgrounds have been seen; these are new quantities computed from the same scores.

## 1. Question

In GB1 every background has its own measured epistasis e_b and ESM-2 shift delta_b. Do the model's shifts decay with sequence separation from the background (a local perturbation), does the measured epistasis decay in the same way, and does the per-background correlation rho_b depend on separation?

## 2. Quantities (primary threshold: Input Count >= 25; all rows as in script 155; separation s = |pos(b) - pos(v)| in residues)

G-1 Per background: lambda_model,b = Spearman(|delta_b(v)|, s); lambda_data,b = Spearman(|e_b(v)|, s); d_b = lambda_model,b - lambda_data,b. Across the 400 backgrounds: the mean, SD and fraction negative of each, and a background-level bootstrap CI (10,000 draws, SEED 0) for the mean of each.
G-2 Separation strata: near s in 1-5, mid 6-15, far 16-54. Per background and stratum with at least 50 partners: rho_b,stratum = Spearman(delta_b, e_b). Across backgrounds per stratum: the mean with a background-level bootstrap CI; and the paired difference near - far with its CI.
G-3 (secondary) If a GB1 structure (RCSB PDB 1PGA, chain A, Calpha atoms) can be obtained and its numbering verified against the assayed sequence, repeat G-1 and G-2 with the Calpha distance in place of s, using strata < 8, 8-14 and > 14 Angstrom; otherwise skip and say why.

## 3. Outcome words (numeric)

MODEL-DECAYS iff the CI of the mean lambda_model lies entirely below zero. DATA-DECAYS iff the CI of the mean lambda_data lies entirely below zero. LOCALITY-DIFFERS iff the CI of the mean d_b excludes zero. SEPARATION-MATTERS iff the CI of the mean paired difference (near - far) excludes zero; SEPARATION-NOT-RESOLVED otherwise, reported as "n cannot resolve this", never as "no relationship".

## 4. Gates

G-D0 the prereg hash; the partner table reproduces script 155's 410,271 rows and its 400 rho_b values (max |diff| < 1e-12 on 10 sampled backgrounds) and the primary mean -0.009125. G-D1 no partner at a background's own position enters. G-D2 planted decay on synthetic scores: with |delta| built to decay with s plus noise the mean lambda_model is negative with its CI below zero; with |delta| independent of s it is not
(fire rate <= 0.15 over 100 draws). G-D3 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 5. Wording

This characterises the statistic in GB1 only; no sentence reads for or against any MTHFR or RBD result.
