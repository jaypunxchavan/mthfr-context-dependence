# Model ladder for the background-shift test - pre-registration v1

Frozen 2026-10-02, before any ladder score exists. The ESM-2 650M results are cached. New data: ESM-2 150M and ESM-2 35M.

## 1. Question

Do the anchor, its placebo separation and its locality gradient appear with other ESM-2 sizes, and do the models agree with one another about the background shifts themselves?

## 2. Design

For each model in {150M, 35M}: score A222V and the 96 Phase 2 backgrounds (the same roster) on the 455 held-out positions H (minus each background's own position), plus the wild-type arm on H, with the same masked-marginal protocol as the 650M scoring.
Per model, and for the cached 650M on the same H rows: A222V rho_H = Spearman(delta, own_e.b) with a position-cluster bootstrap CI; p_spec_H (neg and abs) against N (78); the partial rho_H controlling that model's S_W; the gradient Spearman(rho_b, d3) over the 67 resolved nulls (background-level CI); the shift confound Spearman(rho_b, mean|delta_b|) over the 96 backgrounds; and cross-model agreement:
for each background the Spearman between its delta vector under 650M and under the smaller model on common H rows (report the median and range over the 97 backgrounds), and the Spearman across the 97 backgrounds between rho_b under the two models.

## 3. Outcome words (per model; numeric)

MODEL-REPLICATES iff the CI of rho_A222V on H lies below zero AND p_spec_H(neg) <= 0.10. MODEL-DOES-NOT-REPLICATE iff the CI includes zero or the sign reverses. MODEL-PARTIAL otherwise.

## 4. Gates

G-L0 the prereg hash. G-L1 the checkpoint loads from the local cache (or the authorised download verifies) and reports its parameter count. G-L2 the 650M path through the new scorer reproduces a cached background (AV_220) on H to 1e-6. G-L3 per model: scoring a background twice is identical (1e-6), the wild-type residue's log-odds is 0, and each background scores at least 95% of its eligible H positions.
G-L4 the analysis passes a planted signal and planted null test on synthetic scores. G-L5 bootstrap identity, draw-by-draw reference and Phase 1 CI reproduction.

## 5. Wording

Statements concern these ESM-2 sizes in this gene; models of other families are not covered.
