# PHASE 2 diagnostics — locality, shift-magnitude, and severity confounds on the BEATS verdict

**Written:** 2026-09-30 (Claude, planning) · **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS.md`
**Log to write:** `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md`
**Scripts:** next free numbers. 128/129 (Phase 3a) and 130 (Phase 2 dedup) are taken, so expect
**131, 132** — verify with `ls scripts/*.py | tail` before creating anything.

---

## 0. Why this session exists

Two independent external reviews of the Phase 2 result ("A222V BEATS NON-SITE BACKGROUNDS,"
`p_spec(full) = 2/79`, `p_spec(H) = 4/79`) converged on the same core worry from different
angles, and both are cheap to test on data that's already on disk — **no model scoring, no new
backgrounds, hours not days.**

**The worry, stated plainly:** the frozen test asks whether A222V's ρ_b is unusual among 78
placebo backgrounds. It does **not** ask whether that unusualness reflects something about
*MTHFR biology at position 222* rather than (a) where 222 happens to sit in the protein, or
(b) how hard ESM-2's representation gets perturbed by that particular substitution, independent
of any biological interaction. Two of the three placebos beating A222V on the held-out set are
`AV_220` (2 positions from 222) and `AV_195` (27 positions away) — so a locality story isn't
obviously uniform, but it isn't obviously ruled out either. This session tests it directly
instead of arguing about it.

**Nothing here touches the frozen `PHASE2_PREREG.md` or its verdict.** Every task below is
**descriptive/exploratory**, reported for interpretation, not permitted to redefine, replace, or
retroactively qualify the primary BEATS outcome. If a confound is real, the write-up changes;
the frozen result stands as logged.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No model scoring of any kind.** Do not import torch or esm. Every quantity used here is
   already computed and sitting in `data/processed/phase2/bg_*.csv`,
   `data/processed/phase2/manifest_dedup.csv`, and `task32_analysis_table.csv`.
2. **Confirm inputs match before recomputing anything** (the Group C lesson from Phase 1, and
   the reason D1 below is a hard gate before D2–D8 run). Never build a new analysis on a
   reimplementation you haven't checked against the numbers already on record.
3. **Position-cluster bootstrap where the unit of analysis is a target variant/position** (as
   Phase 2's own primary analysis used); **background-level bootstrap where the unit of analysis
   is a background** (D2, D4, D6 below correlate one number *per background* against another
   number *per background* — resampling positions within a background is not the right
   uncertainty to propagate there; resampling *which backgrounds* were drawn is). State this
   explicitly in each script's docstring so it's never ambiguous which resampling unit is in use.
4. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold.
5. **Protected files — never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`,
   `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`, `PHASE2_PREREG.md`,
   `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md`, and every earlier session's log.
   **Do not touch anything under `docs/tasks/phase3a-gb1-acquisition/` or
   `docs/tasks/phase3b-gb1-regime-map/`.**
6. **Do not commit, do not push.**
7. `venv/bin/python3` always. No package installs should be needed (pandas/numpy/scipy only); if
   one is missing: `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it.
8. Verbatim output in every entry; full run output saved to
   `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAG_<TASK>_FULL_OUTPUT.txt`.
9. **No decision rule in this session may declare GENERIC / BEATS / INDETERMINATE.** Those words
   belong only to the frozen §5 test. Use plain descriptive language (e.g., "associated,"
   "not distinguishable from noise," "consistent with," "inconsistent with") instead.
10. If a premise here is wrong — e.g., a per-background table doesn't exist where expected, or a
    column name differs from what's assumed — say so plainly and adapt transparently rather than
    forcing the assumption.

## S1. Logging instructions

Create `PHASE2_DIAGNOSTICS_LOG.md` first with this template; append one entry per task
**immediately** after it finishes:

```
## [TASK ID] — [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

---

## Task D1 — Build and gate the canonical per-background ρ_b table (HARD GATE; everything below depends on this)

**Before anything else:** check whether `scripts/125_phase2_analysis.py`'s `--mode phase2` run
already persisted a per-background ρ table to disk (search `data/processed/phase2/` and any
output the A2 task logged). **If it exists, use it, verified by the gate below.** If it does not
exist as a file — likely, since A4's log entry only quoted arm-level summary statistics and four
named backgrounds, not a full 96-row table — **recompute it using script 125's own ρ_b
construction, imported, not reimplemented** (same frame, same delta_b definition, same
exclusion of a background's own position per G-C). Compute ρ_b for all 96 backgrounds on **both**
the full frame and H, plus each background's `position` and `arm` (S/V/G) from the roster.

Write `data/processed/phase2_diagnostics/background_rho_table.csv`
(`bg_id, arm, position, rho_full, rho_H`), report its sha256.

**Gate D1-G1 (HARD):** the reconstructed table must reproduce, exactly or to 1e-9:
- A222V's own ρ: full **−0.088118064**, H **−0.090021683**
- `p_spec(full)` recomputed from the table: **2/79 = 0.025316456**, with exactly **`G_P254F`**
  (ρ_full = **−0.096243863**) as the one null at or below A222V
- `p_spec(H)` recomputed from the table: **4/79 = 0.050632911**, with exactly **`G_P254F`**
  (ρ_H = **−0.101954441**), **`AV_220`** (ρ_H = **−0.094480281**), **`AV_195`**
  (ρ_H = **−0.093420822**) as the three nulls at or below A222V
- Arm-level means/medians/ranges match A4's recorded table exactly:
  full — S mean **−0.065159334**, V mean **−0.019532174**, G mean **−0.000230296**;
  H — S mean **−0.070181243**, V mean **−0.022540725**, G mean **+0.000869556**
  (report medians and ranges too; all must match A4's logged values)

**If D1-G1 fails on any single value, STOP the entire session and log `FAIL`.** Do not proceed
to D2–D8 on a table that doesn't reproduce the frozen analysis's own numbers.

---

## Task D2 — Locality: does ρ_b track distance from position 222?

Pre-register in the docstring before running. Using D1's table, compute
`dist_b = |position_b − 222|` for all 96 backgrounds (background's own position; Arm S's
`dist=0` by construction — report but consider excluding from the correlation, since Arm S isn't
in the null set N and mixing it in would conflate "same site" with "near site"; run **both**
ways — full 96 and N-only (78) — and report both, no selection).

- **Statistic:** `Spearman(rho_b, dist_b)`, computed on (a) the full frame view, (b) the H view,
  each on (i) all 96 backgrounds, (ii) N only (78, excluding Arm S).
- **Inference:** background-level bootstrap (resample the background IDs in the relevant set with
  replacement, 10,000 draws, `SEED=0`, holding each background's already-computed ρ_b fixed),
  95% percentile CI; also a 10,000-shuffle label-permutation p on the same resampled set.
- **Sanity check, printed explicitly:** confirm `dist(AV_220)=2` and `dist(AV_195)=27` from the
  roster (the two H-frame beaters), so the reader can see the raw anecdote next to the systematic
  test rather than only the aggregate correlation.
- **Descriptive follow-up (no decision rule, purely informational):** recompute `p_spec(full)`
  and `p_spec(H)` on **N with the k nearest-to-222 backgrounds removed**, for k = 5 and k = 10
  (two disclosed values, neither selected as "the" answer — matching the project's existing
  practice of reporting several thresholds rather than picking one, e.g. Phase 3a's T4). Report
  exactly which backgrounds are removed at each k, and the resulting p_spec, side by side with
  the original 78-null value. **This does not redefine anything frozen; it is reported so a
  reader can see how sensitive the verdict is to near-222 backgrounds specifically.**

## Task D3 — A222V's rank within Arm V alone and Arm G alone (not pooled)

Using D1's table: report A222V's rank **within Arm V ∪ {A222V}** (n=39) and **within
Arm G ∪ {A222V}** (n=41), separately, on both the full frame and H — i.e., decompose the pooled
2/79 and 4/79 ranks into their two component arms. Arm V is exhaustive and fitness-blind (no
selection at all, confirmed in Phase 1b's P1(b)); Arm G is a seed-0 uniform random draw. Report,
for each arm separately: n, the count of that arm's members at or below A222V's ρ, and the
resulting rank. **Purely descriptive — no p_spec formula is redefined; this is decomposition, not
a new test.**

## Task D4 — Shift-magnitude confound: does ρ_b just track how hard ESM-2 gets perturbed?

**The single highest-leverage task in this session.** If ρ_b is mostly a function of how large a
background's overall representational shift is — independent of any relationship to measured
epistasis — then Phase 2 shows position 222 perturbs ESM-2's representation more than other
positions, which is a property of the model, not evidence about MTHFR.

Pre-register in the docstring before running.
- For each of the 96 backgrounds, compute `mean_abs_delta_b = mean(|delta_b(v)|)` over the same
  usable rows script 125 used to compute that background's ρ_b (same frame, same own-position
  exclusion), on **both** the full frame and H. `delta_b(v) = score_b(v) − esm2_score(v)`, read
  from `data/processed/phase2/bg_<bg_id>.csv` joined against `task32_analysis_table.csv`'s
  `esm2_score` column — the same construction script 125 uses for `delta_b` itself; quote the
  exact join and column names from the script rather than assuming them.
- **Statistic:** `Spearman(rho_b, mean_abs_delta_b)` across all 96 backgrounds, separately on full
  and H.
- **Inference:** background-level bootstrap (10,000 draws, `SEED=0`, background IDs resampled,
  each background's ρ_b and mean_abs_delta_b held fixed per draw), 95% CI; 10,000-shuffle
  permutation p.
- **Also report, descriptively:** where A222V and the four backgrounds named in D1/D2 sit on
  `mean_abs_delta_b` relative to the other 91–95 backgrounds (percentile rank), so a reader can
  see directly whether the specific backgrounds driving the verdict are also the ones with the
  largest raw shifts.

## Task D5 — Does `D_site` survive controlling for shift magnitude?

Follow-on to D4, same run. `D_site = mean(ρ_b, Arm S) − mean(ρ_b, N)` was **−0.055525559**
(CI excluding 0) in the frozen A4 result. Using D4's `mean_abs_delta_b`:
- Residualize `rho_b` on `mean_abs_delta_b` via OLS across all 96 backgrounds (or, if the D4
  correlation is negligible, state plainly that residualizing would change nothing and skip the
  heavier machinery — but only after D4's result is in hand, not before).
- Recompute `D_site_resid = mean(resid, Arm S) − mean(resid, N)`, background-level bootstrap CI,
  10,000 draws, `SEED=0`.
- Report `D_site` and `D_site_resid` side by side, on both full and H. **Descriptive only — this
  does not redefine the frozen D_site.**

## Task D6 — Severity gradient: do more disruptive backgrounds give more negative ρ_b?

Pre-register in the docstring before running. **Locate the right severity proxy from what's on
disk — do not assume a column name.** The candidate is each background's own WT-vs-mutant ESM-2
score — the same `esm2_score` baseline used for every other variant in the frame, evaluated at
the background's *own* (position, mut_aa) — i.e., how severe ESM-2 itself predicts that single
substitution to be, independent of any target variant or any epistasis measurement. Confirm this
value is retrievable for all 96 backgrounds from `task32_analysis_table.csv` (or wherever script
125 reads `esm2_score`) by looking up each background's own (position, mut_aa) row. **If it is
not cleanly retrievable for every background, log exactly which are missing and why, rather than
substituting a different proxy silently.**

- **Statistic:** `Spearman(rho_b, background_severity_b)` across N (the 78 null backgrounds —
  Arm S is excluded here since the question is about the null set specifically, per the reviews'
  framing: "is a severity-matched null the right comparison, or does Arm G's uniform draw miss a
  real gradient"), on both full and H.
- **Inference:** background-level bootstrap (10,000 draws, `SEED=0`), 95% CI; permutation p.
- **Report the distribution of `background_severity_b` across Arm V vs Arm G separately** — if
  the two arms differ systematically in severity, that itself is worth knowing regardless of
  whether it correlates with ρ_b.

## Task D7 — Sign-explicit restatement and a |ρ|-based sensitivity

Two small, cheap additions, same run:
1. **Compose the sign-explicit one-sentence statement** of the Phase 2 result using D1's real
   numbers, e.g. the shape: "Position 222 produces a background-specific *negative* association
   between ESM-2's implied shift and measured epistasis, more negative than N of M placebo
   backgrounds (p_spec = X)" — fill in the actual verified numbers from D1, don't invent
   phrasing. Print it verbatim in the entry.
2. **`p_spec` under `|ρ_b|` instead of signed `ρ_b`** (a disclosed sensitivity, not a
   replacement): `p_spec_abs = (1 + #{b in N : |rho_b| >= |rho_A222V|}) / (1 + |N|)` — note the
   inequality direction flips to `>=` because this asks whether A222V's *magnitude* is unusually
   large in either direction, not whether it's unusually negative. Compute on both full and H.
   Report side by side with the original signed `p_spec` values. **This does not replace the
   frozen one-sided primary test; it isolates how much of the verdict depends on the pre-declared
   direction versus raw magnitude.**

## Task D8 — `G_P254F` leave-one-out fragility

`G_P254F` is the single background keeping `p_spec(full)` off its floor (1/79 = 0.012658);
removing it from N changes the denominator too (|N| becomes 77). Using D1's table:
- Recompute `p_spec(full)` and `p_spec(H)` with `G_P254F` excluded from N (|N| = 77, and note
  whether any *other* background then becomes the new binding one on H, since `G_P254F` was one
  of three H-frame beaters — the other two, `AV_220` and `AV_195`, would still count).
- Report both the original (|N|=78) and leave-one-out (|N|=77) `p_spec` values side by side, on
  full and H, with the exact new floor `1/78 = 0.012821` stated. **Purely descriptive — the
  frozen result is not redefined by removing one background after the fact.**

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order: (1) **READ THIS FIRST** — D4's shift-magnitude correlation (both
full and H), with its CI and whether it's distinguishable from zero, since this is the single
result most likely to change how Phase 2 should be written up; (2) D2's locality correlation and
the `AV_220`/`AV_195` distance sanity check; (3) D3's arm-decomposed ranks; (4) D5's
`D_site` vs `D_site_resid`; (5) D6's severity-gradient result and the Arm V vs Arm G severity
comparison; (6) D7's sign-explicit sentence and the `|ρ|` sensitivity numbers; (7) D8's
leave-one-out `p_spec` values; (8) every gate, PASS/FAIL, value, with D1-G1 first; (9) a plain
statement of what this session changes about how Phase 2 should be interpreted or written up —
if D4 and D2 both come back with CIs comfortably including zero, that is a strong statement in
Phase 2's favor and should be reported with the same directness as a concerning result would be;
(10) confirmation nothing under `phase3a-gb1-acquisition/` or `phase3b-gb1-regime-map/` was
touched, and nothing was committed; (11) the single most important entry to read first, with its
line number.

---

## What this session is NOT

- Not a redefinition of the frozen `PHASE2_PREREG.md` verdict. `A222V BEATS NON-SITE BACKGROUNDS`
  stands as logged regardless of what this session finds; what changes is how it gets written up.
- Not an implementation of Carlson, Andrews & Simons (2025)'s rank-statistics method — that paper
  has already been validated on GB1 by its own authors and is a strong candidate for a future,
  carefully-scoped session (fetch and read the actual paper first, don't implement from
  abstract-level knowledge), but it is not attempted here.
- Not an expansion of Arm G — that would require new scoring and is out of scope for a
  cached-data-only session.
- Not a fix to `RESULTS.md`, and not Phase 3 in any form.
