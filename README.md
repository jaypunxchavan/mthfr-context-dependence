# Does Protein Language Model Error Concentrate in Context-Dependent Variants?

MTHFR context-dependence project. See `config/audit_log.md` for the running
log of every data decision made along the way.

## Setup
    source venv/bin/activate
    pip install -r requirements.txt

In VSCode, select the "Python (mthfr-context)" kernel for notebooks (or
point at venv/bin/python directly if kernel registration didn't run).

## Structure

- `scripts/lib/` — the actual reusable logic (data loading, sequence
  verification, validation checks, stats). Import from here.
- `scripts/0X_*.py` — numbered, run-in-order entry points. Thin wrappers
  around `lib/`. Use these for anything expensive, cached, or load-bearing:
  data audits, ESM-2 scoring (caches to disk — should not live in notebook
  cell state), pre-registered statistical tests.
- `notebooks/` — exploration, plotting, one-off checks. Imports from
  `scripts/lib/` rather than reimplementing anything. Not the place for
  logic that the final result depends on.

## Data
`data/raw/` holds an untouched copy of jweile/mthfrModel (gitignored — large,
and it's reference material, not your work). `data/processed/` holds your
own merged/cleaned tables.

## Pipeline order
Run scripts/0X_*.py in numeric order. See config/audit_log.md for what's
been verified so far.

## Reproducing the headline results

Scope: only the scripts a reader needs to verify the results reported in
`RESULTS.md` / `docs/writeups/PROJECT_SUMMARY_FINAL.md` — not an
exhaustive run-all (the remaining 100+ scripts support secondary
analyses; their records live in `docs/tasks/*/…_LOG.md`). Run in order
with `venv/bin/python3`, in the foreground. Resampling scripts default
to `N_BOOT=10000`; smoke first with a small `N_BOOT`/`N_PERM`
(`SMOKE_ONLY=1` where provided). The model steps (ESM-2/ESM-1v/ThermoMPNN)
need their weights and `data/` inputs present; the four tables backing
the headline numbers are committed (the `.gitignore` H1 exceptions), so
the reported values can also be checked directly without re-running
those steps.

1. `scripts/16_phase5_model_abc.py` → `scripts/17_build_own_context.py`
   — base analysis frame (`phase5_analysis_table.csv`) and the
   per-variant interaction estimate (`own_context_metrics.csv`, e.b).
2. `scripts/32_delta_esm_primary.py` — the primary analysis frame
   (`task32_analysis_table.csv`; its delta_esm × own_e_b finite subset
   is the 10,757-row / 654-position frame every headline number uses)
   and the anchor ρ = −0.088118.
3. `scripts/33_delta_esm_signflip_null.py` — the anchor's sign-flip
   null (p < 1e-4; exact identity checks; null centres on zero).
4. `scripts/53_g1_global_specific_epistasis.py` — global-component
   control (specific-residual ρ = −0.1455).
5. `scripts/71_proteingym_model_comparison.py` — the ProteinGym
   comparison table with the anchor row and the severity baselines
   (`task_AB2_proteingym_model_comparison.csv`; needs
   `data/external/ProteinGym/`).
6. `scripts/68_thermompnn_ddg_epistasis.py` →
   `scripts/77_thermompnnD_double_mutant_interaction.py` — ThermoMPNN
   table and its ρ = −0.0733 vs e.b (n = 9,595; model-inference;
   needs `data/external/ThermoMPNN-D/` and `data/raw/6FCX.pdb`).
7. `scripts/86_ac4_esm1v_five_members.py` →
   `scripts/98_t3_t4_t5_reliability_audit.py` — the lead figure: five
   ESM-1v checkpoints, ρ = +0.882637 (raw WT-background) vs +0.084365
   (background deltas). `98` also reads `task58_150m_check.csv`
   (from `scripts/58_*`, the 150M-parameter check).
8. `scripts/96_b4_debias_interaction.py` →
   `scripts/107_e2_dimer_distance_recompute.py` — the
   beyond-contact-range figure: monomer-only 96.22% (needs step 6's
   table), dimer-aware recompute 95.13% with coordinate counts 59 vs 54.
9. `scripts/72_mthfr_detection_floor.py` — empirical power floor
   (power 1.00 at ρ = 0.05).
10. `scripts/91_a2_disattenuation.py` — the disattenuation
    counterfactual (−0.303 / −0.380; a labeled counterfactual, never a
    finding; needs steps 2 and 7).
11. `scripts/97_holm_family.py` — Holm step-down at family-wise
    α = 0.05 (5/5 core, 8/8 m = 8); its family members' raw p-values
    come from scripts 71, 78, 79, and 83, so those tables must exist.

This review round's response re-derivations (scripts 104–107) and their
corrections are recorded in
`docs/tasks/manuscript-review-response/REVIEW_RESPONSE_LOG.md`.
