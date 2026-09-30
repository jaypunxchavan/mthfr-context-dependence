# PHASE 2 diagnostics II — corrections, shift-adjusted null, and 3D locality

**Written:** 2026-09-29 (Claude, planning) · **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II.md`
**Log to write:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md`
**Corrections file to write:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_CORRECTIONS.md`
**Scripts:** next free numbers. Diagnostics I used 131–135 and `scripts/lib/phase2_diag.py`, so expect
**136 and up**. Verify with `ls scripts/*.py | sort -n | tail` before creating anything.

---

## 0. Why this session exists

Diagnostics I (`PHASE2_DIAGNOSTICS_LOG.md`) produced sound computations and left the frozen
verdict untouched. Claude's read of that log against its own printed numbers found that the
log's *interpretive prose* contradicts its data in several places, and that the session stopped
one step short of the test the second external review actually asked for. Two findings drive
everything below:

1. **Locality is the live threat to "position-222-specific."** In Diagnostics I, ρ_b tracks
   sequence distance from 222 (Spearman +0.697 within the 78 nulls, region-robust), and all three
   backgrounds that beat A222V on either frame (`AV_220` d=2, `AV_195` d=27, `G_P254F` d=32) are
   among the ten nearest nulls. The claim the data currently support is closer to "the effect is
   tied to the region around 222" than "tied to position 222."
2. **Shift magnitude is a large confound** (Spearman(ρ_b, mean|δ_b|) = -0.614 full / -0.613 H),
   and A222V's residual from that line was computed but the frozen `p_spec` construction was never
   *run* on residuals. That run is the shift-matched null the second review requested.

**Nothing here touches the frozen `PHASE2_PREREG.md` verdict.** Every task is descriptive and is
reported so the write-up can state the strongest claim the data actually support. If an
adjustment weakens the result, say so as plainly as you would report that it strengthens it.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No model scoring. Do not import torch or esm.** Everything needed is on disk:
   `data/processed/phase2/bg_*.csv`, `data/processed/phase2_diagnostics/background_rho_table.csv`,
   `data/processed/task32_analysis_table.csv`, `data/raw/6FCX.pdb`, and the helper library
   `scripts/lib/phase2_diag.py`.
2. **Expected values in this doc are Claude's own recomputations, not facts.** Where a value is
   listed as a target, recompute it independently. A mismatch means **the doc is wrong**: STOP
   that item, report both numbers, and do not force agreement. This applies especially to D0.
3. **Confirm inputs before building on them.** The D1 table's sha256 must match on disk
   (`e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796`); hard-stop on mismatch.
4. **Resampling unit.** Where a statistic is one number per background correlated against another
   number per background, resample **backgrounds** (10,000 draws, `SEED=0`, per-background ρ_b held
   fixed), never positions. State the unit in every docstring. The 96 ρ_b share one outcome
   vector (`own_e_b`) and are mutually correlated; table rows are not independent draws.
5. **Pre-register in each script's docstring before its first run:** construction, covariates,
   which variant is primary, gates, and what will be reported. Smoke run first, then full.
6. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold,
   never re-run at higher N to chase a result.
7. **Protected — never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`,
   `AGENTS.md`, `PHASE2_PREREG.md`, `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md`, and
   **every earlier log including `PHASE2_DIAGNOSTICS_LOG.md` and `PHASE2_LOG.md`**. Corrections to
   earlier logs are recorded **only** in this session's log and corrections file. Do not touch
   anything under `docs/tasks/phase3a-gb1-acquisition/` or `docs/tasks/phase3b-gb1-regime-map/`.
8. **Do not commit, stage, or push.**
9. `venv/bin/python3` always. No installs should be needed. If one is:
   `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it. Never torch/esm.
10. **Wording.** Never use the frozen outcome words (GENERIC / BEATS / INDETERMINATE) as the label
    for any result computed here. Compare adjusted `p_spec` to the frozen numeric thresholds
    (0.05 full, 0.10 H) and say only "at or below" or "above" each. Quoting an earlier log
    verbatim is fine.
11. Verbatim output in every entry; full output saved to
    `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAG2_<TASK>_FULL_OUTPUT.txt`.
12. If a premise here is wrong (a column, a file, a function name), say so plainly and adapt
    transparently. Diagnostics I found the plan's premise wrong on D6 and reported it; do the same.

## S1. Logging instructions

Create `PHASE2_DIAGNOSTICS_II_LOG.md` first with this template; append one entry per task
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

## Task D0 — Append-only corrections to Diagnostics I (write FIRST; cheap; no new science)

**Purpose:** record, with recomputed evidence, where `PHASE2_DIAGNOSTICS_LOG.md`'s prose disagrees
with its own printed numbers, so a write-up never cites the wrong sentence. **Do not edit that
log.** Locate each quoted string with `grep -n` (do not trust line numbers given here; the
uploaded copy Claude read may differ by a line from the repo copy) and record the real line
numbers in the corrections file.

**Gate D0-G1 (HARD):** D1 table sha256 matches; A222V's two ρ values re-derived through
`scripts/lib/phase2_diag.py` (script 125's own construction, imported, exactly as D3 did) equal
-0.088118064 (full) and -0.090021683 (H) to 1e-9; `p_spec(full) = 2/79` with beater set
`{G_P254F}`; `p_spec(H) = 4/79` with beater set `{AV_195, AV_220, G_P254F}`. If any fails, STOP the
whole session.

For each item below: quote the old text verbatim with its line number, **recompute** the true
quantity from the D1 table / script-134 machinery, print the recomputed value next to the
target, and write the corrected statement composed from computed variables (no hand-typed
numbers).

- **C1 — the D7.1 "sign-explicit sentence" is inverted.** Old text (search `more negative than 1 of
  the 78`): says A222V's association is "more negative than 1 of the 78 placebo backgrounds on the
  full frame and 3 of the 78 on the held-out H frame." Those numbers are the counts of placebos
  *at or below* A222V's ρ. **Target:** A222V is more negative than **77 of 78** (full) and
  **75 of 78** (H), i.e. `|N| - k`. Produce the corrected sentence, keeping the rest of the
  wording, composed from variables. (The task template that produced this was ambiguous; note that
  in the entry, but the printed sentence must not be reused.)
- **C2 — "the most extreme residual of all 96" is false.** Old text (search `most extreme residual
  of all 96` and `96.9th percentile`; occurs in D4, in summary §1, and in §9 item 2). Using D4's
  exact construction (OLS of ρ_b on mean|δ_b| over all 96 backgrounds with an intercept, A222V
  excluded from the fit; import script 134's build rather than reimplementing): recompute every
  background's residual on both views, rank A222V's residual among them, and **list every
  background whose residual is at or below A222V's**, with arm and distance. **Targets:**
  `AV_220`'s residual is more negative than A222V's on both views (about -0.0757 vs -0.0591 full;
  -0.0840 vs -0.0611 H), so A222V is not rank 1; the log's "96.9th percentile" implies about three
  backgrounds lie beyond it. Also **quote script 134's percentile definition verbatim** (the log's
  phrase "(0 = most negative)" is ambiguous) and state which end 96.9 refers to.
- **C3 — D3's reading ("full-frame result carried entirely by Arm G"; "opposite of what an
  'exhaustive control agrees' reading would predict") is backwards.** Recompute from the table:
  Arm V alone: at-or-below counts 0 (full) and 2 (H); Arm G alone: 1 (full) and 1 (H). Post-hoc,
  arm-alone `p_spec = (1+k)/(1+n_arm)`. **Targets:** Arm V alone = 1/39 = 0.025641 (full) and
  3/39 = 0.076923 (H); Arm G alone = 2/41 = 0.048780 (both). State for each whether it is at or
  below the frozen numeric thresholds. Label the block **POST-HOC DECOMPOSITION — the frozen test
  is defined on the pooled 78; this redefines nothing**. State explicitly that "carried entirely
  by Arm G" is retracted: Arm V's zero count on the full frame is rank 1/39, the strongest
  agreement the design-matched arm could give, and the only full-frame exception lies in Arm G.
- **C4 — "its magnitude is the largest in the null set in either direction" (D7) is wrong as
  worded.** Recompute the rank of |ρ_A222V| within N ∪ {A222V}. **Targets:** 2/79 (full),
  4/79 (H). The substantive D7 finding (zero positive placebos reach |ρ_A222V|, so the one-sided
  direction is not driving `p_spec`) stands; say so.
- **C5 — D8's "a weaker one" is muddled, and D8 misses the real fragility.** Leave-one-out
  `p_spec` falls (0.0253 → 0.0128 full), which is *smaller*, not weaker. The relevant fragility is
  how few additional at-or-below placebos would change the pooled comparison to the frozen
  thresholds. Produce a table for k = 0..8 at-or-below placebos: `(1+k)/79`, and whether it is at or
  below 0.05 and 0.10. **Targets:** at or below 0.05 through k=2 (0.0380), above at k=3
  (0.0506); at or below 0.10 through k=6 (0.0886), above at k=7 (0.1013). Then list the five
  null backgrounds whose ρ lies nearest **above** A222V's (i.e. just missed it), with their gaps,
  on both views. **Targets (full):** `AV_220` gap ≈ 0.00352, `AV_195` gap ≈ 0.00396. For context
  only, quote A222V's own position-cluster 95% CI from `PHASE1_LOG.md` [A1] (search
  `headline row reproduced exactly`; about [-0.1173, -0.0595]), and state that it is a
  different bootstrap from any per-background CI and is context, not a test.
- **C6 — D2's "k-removal strengthens the comparison" is mechanical.** Show that the k=10 removed set
  contains **all three** beaters (`AV_220`, `AV_195`, `G_P254F`), so `p_spec` reaching its floor
  is guaranteed rather than informative. Then compute, **labelled POST-HOC** (the beaters were
  identified after seeing ρ; the distance ranks are fixed in advance), the probability that all
  three beaters fall within the k nearest of the 78 nulls under random placement:
  `C(10,3)/C(78,3)`. **Target:** 120/76076 = 0.001577. Report it for k = 10 and, as a second
  disclosed value, k = 20; select neither.
- **C7 — "A222V is unusual relative to its own neighbourhood" (summary §9 item 3) is not
  established.** Recompute A222V's rank among only the 10 nearest nulls and, as a second value, the
  20 nearest, by sequence distance (ties broken by ascending `bg_id`, D2's rule R9), on both
  views, as `(1+k)/(1+n)`. **Targets (10 nearest):** at-or-below counts 1 (full), 3 (H), i.e.
  2/11 = 0.1818 and 4/11 = 0.3636. Label these **rank fractions, not tests** (n is tiny), and
  state that this cannot distinguish "222-specific" from "neighbourhood-specific" — it shows only
  that the log's wording overreaches.
- **C8 — D2's verdict says A222V is more negative than "essentially every placebo, including the
  nearest ones."** The D2 table itself shows `AV_220` (d=2) at or below A222V's ρ on **H** (-0.0945
  vs -0.0900). Restate correctly for each view.
- **C9 — the "protected files do not exist" flag.** Diagnostics I could not find
  `MTHFR_RESULTS_LOG.md` or `PROJECT_SUMMARY_FINAL.md`. Phase 3a's T7 logged mtimes at
  `docs/tasks/results-log/MTHFR_RESULTS_LOG.md` (2026-09-21) and
  `docs/writeups/PROJECT_SUMMARY_FINAL.md` (2026-09-26). Run `ls -la` on those two exact paths and
  `find . -name MTHFR_RESULTS_LOG.md -o -name PROJECT_SUMMARY_FINAL.md` (excluding `venv`), record
  the results verbatim, and say whether the earlier flag was a wrong-path check. Do not edit either
  file.

**Outputs:** (i) the D0 log entry; (ii) `PHASE2_DIAGNOSTICS_CORRECTIONS.md`, one section per item
C1–C9 with: old quote and real line number, recomputed value and target, corrected statement, and
a final line "Cite this, not the old sentence." Report its sha256.

---

## Task D9 — Shift-adjusted `p_spec`: the frozen construction run on residuals

**Why:** Diagnostics I computed A222V's residual from the shift-magnitude line but never asked the
pooled question on residuals. This is the shift-matched null.

**Pre-register in the docstring before running.** Covariate: `mean_abs_delta_b =
mean(|delta_b(v)|)` over the same usable rows script 125 used for each background's ρ_b, both views,
exactly as D4 built it (import script 134's build; do not reimplement). For A222V, `delta` is its own
`delta_esm` column over the same usable rows (D4: 0.070330 full, 0.069403 H).

**Gate D9-G1 (HARD; tolerance |diff| < 2e-6 because the log prints 6 dp, except correlations 1e-8):**
reproduce D4's printed values before any new analysis.

| quantity | full | H |
|---|---|---|
| Spearman(ρ_b, mean\|δ\|) over 96 | -0.614188823 | -0.612696690 |
| all-96 OLS slope / intercept | -0.896326 / +0.034053 | -0.964705 / +0.037990 |
| A222V mean\|δ\| | 0.070330 | 0.069403 |
| A222V residual (all-96 fit) | -0.059133 | -0.061058 |
| G_P254F mean\|δ\| / residual | 0.208008 / +0.056146 | 0.200143 / +0.053135 |
| AV_220 mean\|δ\| / residual | 0.047893 / -0.075724 | 0.050233 / -0.084010 |
| AV_195 mean\|δ\| / residual | 0.095630 / -0.032500 | 0.098154 / -0.036722 |

If any fails, STOP D9–D11 (D0 may already be done).

**Construction (three variants; the first is primary, designated now, all three reported):**

- **Primary — leave-one-out residuals on N.** For each null `b ∈ N` (78): fit OLS
  `ρ ~ a + c·mean|δ|` on `N \ {b}` and take `b`'s out-of-sample residual `r_b`. For A222V: fit on
  all of N (A222V is not in the fit) and take its out-of-sample residual `r_A`. This makes A222V and
  the nulls **exchangeable** (each residual comes from a fit that excluded that background); using
  in-sample null residuals against an out-of-sample A222V residual would be subtly unfair, and
  that is why this is primary.
- **Sensitivity 1 — in-sample fit on N** (fit once on the 78; nulls' in-sample residuals; A222V
  out-of-sample).
- **Sensitivity 2 — D4's all-96 fit** (includes Arm S; A222V excluded). Ties this task back to
  Diagnostics I.

For each variant and each view: `p_spec_adj = (1 + #{b ∈ N : r_b ≤ r_A}) / (1 + |N|)` (same
form and inequality direction as the frozen test), the identity of every null at or below `r_A`
(with arm, sequence distance, mean|δ|), A222V's `r_A` and signed rank within N ∪ {A222V}, and
whether `p_spec_adj` is at or below the frozen thresholds (0.05 full / 0.10 H). Print the ten
most negative null residuals for the primary variant so the reader can see who lies beyond A222V.
**No resampling in this task (exact rank counts); state that in the docstring.**

**Limits to state in the docstring and the entry:** `mean|δ|` is scale-only and blind to sign
pattern; it and ρ_b are both functions of the same `δ_b` (partial construction overlap); a
survival is not evidence that δ's influence is gone, only that overall magnitude does not account
for the ranking.

---

## Task D10 — Joint adjustment for shift and distance; neighbourhood ranks; partial correlations

**Pre-register in the docstring before running.** Distance is **sequence** distance
`dist_b = |position_b - 222|` (D11 repeats this with 3D distance). A222V has `dist = 0`; the
smallest null distance is 2 (`AV_220`), so A222V sits at the edge of the covariate range — say
so, and report the leverage.

**D10a — joint OLS.** Primary: `ρ ~ a + c1·mean|δ| + c2·log1p(dist)` fit on N, leave-one-out
residuals for nulls, out-of-sample residual for A222V, exactly as D9 primary. `log1p` is chosen
because the gradient is expected to be steep near 222 and flat far away, and it is defined at 0.
Disclosed sensitivities (report all, select none): (i) linear `dist` instead of `log1p(dist)`;
(ii) **clamped** — evaluate A222V at `dist = 2` (the null minimum) instead of 0, which avoids
extrapolation; (iii) shift-only (= D9 primary, for side-by-side). Report `p_spec_adj` and the
at-or-below nulls for each, both views.

**D10b — neighbourhood-restricted ranks on D9's primary residuals.** Among the **k nearest** nulls
(k = 10 and k = 20, both reported, neither selected; ties by ascending `bg_id`), report A222V's
rank fraction `(1 + #{r_b ≤ r_A}) / (1 + k)` on both views. **Rank fractions, not tests**; n is
tiny; label as descriptive.

**D10c — partial rank correlations across N (78).** `Spearman(ρ_b, dist | mean|δ|)` and
`Spearman(ρ_b, mean|δ| | dist)` via the standard partial-correlation formula on the pairwise
Spearman coefficients, background-level bootstrap 95% CI (10,000 draws, `SEED=0`, backgrounds
resampled). **No permutation p** (a naive shuffle of one variable is not valid for a partial
statistic); state that. Purpose: which axis carries the association once the other is held fixed.

---

## Task D11 — 3D structural distance to residue 222

**Why:** locality in D2 is *sequence* distance, which the log itself warns is not structural
locality. `AV_195` (195) and `G_P254F` (254) may be spatial neighbours of 222 even though they are
27 and 32 residues away in sequence. The structure and loading code already exist from the
interface check.

**Structure and conventions (do not assume; quote from scripts 107 and 126):** `data/raw/6FCX.pdb`,
chains A and B, an experimental 2.50 Å X-ray dimer; frame position `p` = PDB residue number `p`
(array index `p - 40`); chain A resolves 40..651 with internal gaps 161–171 and 392–396. Positions
2–39, 161–171, 392–396 and 652–656 have **no chain-A coordinates**; backgrounds there get `NaN`
distances, are **listed by name**, and are never imputed. Residue 222 is resolved in chain A.

**Loader:** import script 126's exact float64 fixed-column parse (or script 107's `load_pdb` only if
it imports without torch/esm). Do not reimplement a parser without gating it.

**Gates D11-G1 (HARD):** (a) mapping: for the 9,595 rows of `task77_thermompnnD_doubles.csv` with a
stored `ca_dist_222`, the recomputed chain-A CA–CA distance to residue 222 reproduces the stored
value to < 1e-6 (the interface check reproduced it to 7.105e-15); (b) reproduce script 107's known
far-from-222 figures from the same structure: monomer far (>10 Å) 9,232/9,595 = 96.22% and
dimer-aware 9,128/9,595 = 95.13%. If either fails, STOP D11.

**D11.1 — distances for the 96 backgrounds.** For each background position `p`: (i) **primary**
`d3_CA` = chain-A CA–CA distance from residue `p` to residue 222; (ii) `d3_dimer` = script 107's
four-pair CA minimum (A222/B222 × Ap/Bp); (iii) `d3_atom` = minimum heavy-atom distance in chain A.
Write `data/processed/phase2_diagnostics/background_3d_distance.csv`
(`bg_id, arm, position, dist_seq, d3_CA, d3_dimer, d3_atom, resolved`) and report its sha256.
List every unresolved background by name and count how many fall in N.

**D11.2 — repeat D2 with 3D distance.** `Spearman(ρ_b, d3_CA)` in the same four views (all-96 and
N-only × full/H) restricted to structure-resolved backgrounds, background-level bootstrap and
10,000-shuffle permutation as in D2, plus the sequence-distance correlation **recomputed on the
identical resolved subset** so the two are comparable (do not compare against D2's numbers, which used
a different n). Report `d3_dimer` and `d3_atom` as sensitivities; select none.

**D11.3 — where are the beaters in space?** Table for `AV_220`, `AV_195`, `G_P254F` and the 10
sequence-nearest nulls: `dist_seq`, `d3_CA`, `d3_dimer`, and each one's rank by 3D distance among
the resolved nulls. Report the 10 nearest nulls **by 3D distance** and mark which are beaters. The
informative fact is whether the beaters are also 3D-near, not whether removing them lowers
`p_spec`. If you compute k-nearest-removal `p_spec` (k = 5, 10 by 3D order), report the beaters
inside each removed set alongside it and label the result mechanical when all beaters are removed.

**D11.4 — joint adjustment with 3D distance.** Repeat D10a's primary construction with
`log1p(d3_CA)` in place of `log1p(dist_seq)` on the resolved subset (state `n`; the denominator
shrinks by the number of unresolved nulls), and D10c's partial correlations with `d3_CA`. Report
`p_spec_adj` on both views against the frozen numeric thresholds only.

**D11.5 — head-to-head.** One table: for the resolved subset, adjusted `p_spec_adj` under
(shift only), (shift + sequence distance), (shift + 3D distance), both views, identical
denominators. Descriptive; no variant is declared "the" answer.

---

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order: (1) **READ THIS FIRST** — D9's primary shift-adjusted `p_spec_adj`
(both views), the nulls at or below A222V's residual, and whether each value is at or below the frozen
thresholds; (2) D10a/D10b/D10c — the joint adjustment, neighbourhood rank fractions, and which axis
carries the association once the other is held fixed; (3) D11 — whether locality is spatial (D11.2),
where the three beaters sit in 3D (D11.3), and the head-to-head table (D11.5); (4) D0 — a table of C1–C9
with old text, recomputed value vs target, and the corrected statement; (5) a plain, two-sided
statement of which claim the data now support — "tied to position 222," "tied to the region around
222," or "cannot be separated" — worded with the same directness whichever way it falls;
(6) every gate, PASS/FAIL, value, D0-G1 first; (7) confirmation nothing protected was edited, no
earlier log was touched, nothing was committed, and no torch/esm import occurred; (8) the single
most important entry to read first, with its line number.

---

## What this session is NOT

- Not a revision of the frozen `PHASE2_PREREG.md` verdict or a new decision rule.
- Not the write-up. The write-up should wait for this session, since it decides which claim is
  defensible; it should cite `PHASE2_DIAGNOSTICS_CORRECTIONS.md` rather than the superseded
  sentences in Diagnostics I.
- Not new scoring, not an expansion of Arm G, not Carlson et al.'s rank-statistics method (still a
  separate, carefully scoped session), and not Phase 3.
