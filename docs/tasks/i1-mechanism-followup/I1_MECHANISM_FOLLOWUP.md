# I1 Diagnosis, Mechanism Follow-Up, and Script 35 Retirement

Source: overnight run of REVIEW_TRIAGE.md, completed 43/47 tasks. Two results
from that run change what can honestly be claimed and need direct follow-up
before anything else gets written up as settled:

1. **I1 (the positive control) failed the gate** — p=0.1398, null mean ≈ 87%
   of observed. This bounds every negative finding in Part 5/6 of
   `docs/tasks/results-log/MTHFR_RESULTS_LOG.md`: without a working positive
   control, "ESM-2 fails to use background information" and "the pipeline
   can't detect real epistasis" are indistinguishable.
2. **S2 vs H1a is a real, useful contradiction, not noise.** S2 confirmed the
   atlas calls A222V strongly deleterious; H1a separately found ESM-2 itself
   rates A222V as near-neutral. That's a candidate MECHANISM for the whole
   negative finding, worth testing directly rather than leaving as a flagged
   tension.

Also folded in: script 35's SE-threshold epistatic-set flag is dead (J4a:
FDR 0.91-1.00 at every cutoff even after correction; J4b: the correction
factor itself varies 2.5x by region). It needs to be formally retired and
replaced, not patched further.

---

## Group L — Diagnose and, if possible, fix the I1 gate failure

**Task L1 — Characterize what I1 actually tested and whether the test was fair**
- L1a. Identify the exact script and comparator dataset I1 used. Print the
  dataset's name, source, n, and — from the dataset's OWN source paper or
  documentation, not assumed — the effect size of the epistasis it is known
  to contain. A gate failure on a dataset with weak, borderline epistasis
  is a different finding than a gate failure on a dataset with strong,
  well-established epistasis.
- L1b. Compare the comparator dataset's per-variant measurement precision
  (SE, or replicate count, whatever it reports) against MTHFR's own SE
  distribution (already computed in script 35's output,
  `data/processed/task35_epistatic_set.csv`). If the comparator is noisier
  than MTHFR itself, a gate failure there says little about the MTHFR
  pipeline specifically.
- L1c. Run a simple detectable-effect-size calculation for I1's null test as
  actually constructed: given its n and its null's observed variance, what
  is the smallest true effect this test could reliably detect (power ~0.8)?
  Report whether the comparator dataset's known effect size, from L1a, is
  above or below that floor. This is the single most important number in
  this whole task doc — it tells you whether I1 failed because the pipeline
  has no power, or because the comparator was underpowered for ANY method.

**Task L2 — If L1 shows the comparator was underpowered, find a better one**
- L2a. Search `data/raw/` and anywhere else already on disk for an
  alternative dataset with a LARGER, more established interaction effect
  size (a double-mutant DMS with a bigger reported epistasis term — GB1 is
  the standard reference in this literature and may already be referenced
  in `scripts/lib/` or prior task docs). Prefer something already available
  locally over downloading something new. If nothing suitable exists
  on disk, stop this subtask and report exactly what's missing rather than
  downloading a large new dataset unsupervised.
- L2b. If a suitable comparator is found, rerun the EXACT SAME delta_ESM +
  sign-flip-null pipeline (same code path as script 33, not a rewritten
  version) against it. Report whether it clears the gate this time.
- L2c. If it clears the gate: the pipeline has power, and MTHFR's negative
  result stands as reported. If it STILL fails: the pipeline itself likely
  lacks power regardless of comparator, and that needs to be stated as an
  open limitation, not quietly worked around.

**Task L3 — Draft (do not merge) an epistemic-caveat addendum**
- L3a. Regardless of L1/L2's outcome, write
  `docs/tasks/i1-mechanism-followup/ADDENDUM_I1_CAVEAT.md` — a short, plain
  statement of exactly which claims in `MTHFR_RESULTS_LOG.md` Part 5/6 are
  conditional on I1's outcome, and what the honest one-sentence caveat is
  given whatever L1/L2 found. This is a DRAFT for me to review — do not
  edit `MTHFR_RESULTS_LOG.md`, `RESULTS.md`, or `REVIEW_TRIAGE.md` directly.

---

## Group M — Test the S2/H1a mechanism directly

**Hypothesis:** ESM-2 rates A222V as near-neutral (H1a). If a background
mutation doesn't register as damaging to the model, the model has little
reason to propagate any meaningful correction from it elsewhere — which
would explain a weak/backward delta_ESM signal WITHOUT requiring that ESM-2
"gets epistasis backwards" as a general property. This reframes the finding
from "ESM-2 is wrong about interaction" to "ESM-2 doesn't recognize the
premise," which is a more precise and more defensible claim if it holds.

**Task M1 — Does ESM-2's context-shift strength scale with how damaging it rates the background mutation?**
- M1a. From the already-computed single-mutant WT scoring table
  (`data/processed/esm2_wt_scores.csv` from script 10), select 6-10
  alternate candidate background mutations spanning a range of ESM-2's OWN
  masked-marginal severity rating — from near-neutral (similar to how it
  rates A222V) to strongly damaging (its most negative scores). Pick
  positions distinct from 222 and from each other, spread across the
  protein similarly to how the existing region checks are structured. This
  step uses data already on disk — no new scoring needed yet.
- M1b. For each candidate background b, build the substituted sequence
  (mirroring exactly what script 11 did for A222V) and rescore a FIXED
  SUBSET of ~100-150 other positions in that background — not all 655, to
  keep runtime bounded; use the same subset across all backgrounds b so
  they're comparable. Reuse `scripts/lib/esm_scoring.py`'s existing
  functions; do not write new scoring logic.
- M1c. For each background b, compute `delta_ESM_b` for that subset
  exactly as script 12 computes it for A222V, and summarize its magnitude
  (mean |delta_ESM_b| over the subset).
- M1d. Plot/report: mean |delta_ESM_b| (context-shift strength) against
  S(b|WT) (how damaging ESM-2 itself rates background b), across all
  tested backgrounds including A222V. State plainly: does A222V sit as an
  outlier-LOW point on this relationship (supporting the H1a mechanism —
  A222V triggers unusually little context-shift because the model doesn't
  see it as damaging), or does it sit normally along the trend (mechanism
  not supported, the weak signal needs a different explanation)?
- M1e. Position-cluster bootstrap CI on the M1d correlation, same
  convention as everywhere else in this project.

**Runtime note:** M1b/c involves rescoring roughly 6-10 backgrounds × ~100-150
positions. Time one background's subset first before committing to all of
them (per AGENTS.md §1) — do not assume this is fast just because it reuses
existing code.

---

## Group N — Retire script 35's SE-threshold flag, replace with a nonparametric one

**Task N1 — Formal retirement**
- N1a. Add a clear `DEPRECATED` header to the top of
  `scripts/35_se_threshold_epistasis.py` pointing at J4a/J4b's findings
  (FDR 0.91-1.00 even after correction; correction factor varies 2.5x by
  region). Do not delete the script — it's a documented, informative dead
  end, and the log entry showing WHY it failed has value.
- N1b. `grep -rn "task35_epistatic_set" scripts/` to confirm nothing
  downstream actually reads that file. If something does, flag it — do not
  silently change what it reads.

**Task N2 — Nonparametric replacement**
- N2a. Build a stratifier that sidesteps the miscalibrated-SE problem
  entirely: rank each missense variant's `|e_b|` against the EMPIRICAL
  distribution of synonymous-variant `|e_b|` (the known noise floor,
  already computed) rather than against a parametric SE threshold. E.g.
  percentile rank relative to the synonymous null's ECDF, or an
  empirical-Bayes local FDR using the synonymous distribution as the null
  component directly. This uses the same synonymous-control logic that
  already worked well in Task D1 (winner's-curse checks) instead of the
  per-condition SE values that were shown to be miscalibrated.
- N2b. Recompute the region-level epistatic fractions (mirroring script
  35's original region table) under the new stratifier and compare —
  report whether the qualitative regional pattern changes.
- N2c. Save to `data/processed/task_N2_nonparametric_epistatic_set.csv`,
  distinct from the retired `task35_epistatic_set.csv`.

---

## Suggested execution order

1. **L1** first, always — it's the number that tells you how to interpret
   everything else tonight, including whether M1's eventual result means
   anything.
2. **L2** only if L1c shows the original comparator was genuinely
   underpowered; skip straight to L3 if L1 shows the pipeline itself is the
   problem (no better comparator would fix that).
3. **M1** — independent of L, can run in parallel/either order, but read
   its result in light of whatever L1 found about pipeline sensitivity.
4. **N1, N2** — independent of L and M, no reason to delay.
5. **L3** last, once L1/L2's actual outcome is known, so the caveat
   reflects reality rather than being drafted speculatively.
