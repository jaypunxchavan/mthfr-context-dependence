# PHASE 2 diagnostics III - corrections, same-site comparison, and the long-range mechanism test

**Written:** 2026-09-29 (Claude, planning) | **Executor:** OpenCode
**Doc lives at:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III.md`
**Log to write:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md`
**Corrections file to write:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_II_CORRECTIONS.md`
**Scripts:** next free numbers. Diagnostics II used 136-139, so expect **140 and up**. Verify with
`ls scripts/*.py | sed 's/.*\///;s/\.py//' | sort -n | tail` before creating anything. Shared helpers go in a
**new** file `scripts/lib/phase2_diag3.py`; do not modify `scripts/lib/phase2_diag.py` or any earlier script.

---

## 0. Why this session exists

Diagnostics II established four things and left three problems.

**Established (verified against the log and independently recomputed):**
- Locality is real and spatial. Spearman(rho_b, d3_CA) = +0.7316 vs +0.7133 for sequence distance on the same
  67 resolved nulls; the three backgrounds that beat A222V on either frame are 3D-near (3D ranks 2, 4, 9).
- After adjusting for shift magnitude (mean|delta_b|), A222V's leave-one-out residual still ranks 3/79 on both
  views (`p_spec_adj` = 3/79 = 0.037975), beaters `{AV_220, AV_85}`.
- Once a distance term is added to a parametric model, A222V's residual turns positive.
- The frozen `PHASE2_PREREG.md` verdict is untouched.

**Problems this session addresses:**
1. **Three label/statement errors in the Diagnostics II log** (D10c's two partial correlations are label-swapped;
   D10b's counts contradict D9's own printed residuals; "not an extrapolation artifact" is overstated). D12 records
   the corrections, append-only, without editing any earlier log.
2. **The design has no distance-matched null.** A222V sits at distance 0, below every null (minimum 2 residues /
   5.06 A), so every distance adjustment is an extrapolation. The only distance-matched comparators are the 18
   same-site Arm S backgrounds, and A222V was never compared to them directly (D13), nor was the raw gradient
   examined without a fitted functional form (D14, D16).
3. **The mechanism is unexamined.** The working hypothesis is that rho_b tracks spatial overlap between a background's
   perturbation footprint and A222V's measured epistasis pattern, not anything epistasis-specific. If so, the gradient
   and the anchor should weaken when target variants near 222 are excluded. If they persist among distal variants,
   the statistic carries long-range information, which is the project's actual claim. D15 tests this, with a
   matched-deletion control so that "fewer rows" cannot masquerade as a mechanism.

**Nothing here touches the frozen `PHASE2_PREREG.md` verdict.** Every task is descriptive. If a result weakens the
anchor, report it as plainly as you would report that it strengthens it.

---

## 1. Rules (from `AGENTS.md`; restated where they bite)

1. **No model scoring. Do not import torch or esm** (and do not import `thermompnn`, which pulls in torch;
   Diagnostics II verified this). Everything needed is on disk.
2. **Expected values in this doc are Claude's own recomputations, not facts.** Where a value is listed as a
   target, recompute it independently. A mismatch means **the doc is wrong**: STOP that item, report both numbers,
   do not force agreement.
3. **Hard reproduction gate first (D12-G1).** If it fails, STOP the whole session.
4. **Resampling units.** Statistics that are one number per background correlated against another number per
   background: resample **backgrounds** (10,000 draws, `SEED=0`, per-background rho_b held fixed). Statistics
   computed inside one background (A222V's own rho on a row subset): resample **target positions** (position
   clusters). State the unit in every docstring.
5. **Pre-register in each script's docstring before its first run:** construction, primary designation,
   gates, what will be reported. Smoke run first, then full. Time the full run; do not guess.
6. **A failed gate means STOP that task, log `FAIL`/`BLOCKED`.** Never loosen a threshold or re-run at higher N to
   chase a result.
7. **Protected, never edited:** `RESULTS.md`, `MTHFR_RESULTS_LOG.md`, `PROJECT_SUMMARY_FINAL.md`, `AGENTS.md`,
   `PHASE2_PREREG.md`, `docs/tasks/phase3b-gb1-regime-map/GB1_REGIME_PREREG.md`, and **every earlier log**
   (`PHASE2_LOG.md`, `PHASE2_DIAGNOSTICS_LOG.md`, `PHASE2_DIAGNOSTICS_II_LOG.md`, and all earlier). Also do not edit
   any earlier script or `scripts/lib/phase2_diag.py`. Corrections live only in this session's log and corrections
   file. Do not touch `docs/tasks/phase3a-gb1-acquisition/` or `docs/tasks/phase3b-gb1-regime-map/`.
   (`MTHFR_RESULTS_LOG.md` is at `docs/tasks/results-log/`; `PROJECT_SUMMARY_FINAL.md` is at `docs/writeups/`.)
8. **Do not commit, stage, or push.**
9. `venv/bin/python3` always. If a small package is missing:
   `venv/bin/python3 -m pip install <pkg> --break-system-packages`, log it; if that fails, `BLOCKED`. Never torch/esm.
   `matplotlib` is optional (D14): if it is not importable, log `SKIPPED` for the figure and do not install it.
10. **Wording.** Never use the frozen outcome words (GENERIC / BEATS / INDETERMINATE) as a label for any result
    computed here. Compare adjusted `p_spec` to the frozen numeric thresholds (0.05 full, 0.10 H) and say only
    "at or below" or "above". Quoting an earlier log verbatim is fine. Rank fractions over tiny n are rank
    fractions, not tests; label them so.
11. Verbatim output in every entry; full output saved to
    `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAG3_<TASK>_FULL_OUTPUT.txt`.
12. If a premise here is wrong (a column, a function, an earlier script's structure), say so plainly and adapt
    transparently. Earlier sessions found the plan wrong on D6 and on the script 126 import; do the same.
13. **Importing earlier scripts.** Import scripts 125, 134, 137, 138, 139 via `importlib` only if their `main()` is
    guarded and importing has no side effects and pulls in no torch. Otherwise transcribe the needed function
    verbatim under a `QUOTED SOURCE` comment with file and line numbers, and gate the transcription against the
    original's printed output, as Diagnostics II did for script 126's parser.

## S1. Logging instructions

Create `PHASE2_DIAGNOSTICS_III_LOG.md` first with this template; append one entry per task **immediately** after
it finishes:

```
## [TASK ID] - [title]
Status: PASS | FAIL | BLOCKED | PARTIAL | SKIPPED
Time started / finished:
What I did:
Actual output (real numbers and quoted source text, not a paraphrase):
Verdict:
Files created/modified:
Anything unexpected or worth flagging:
```

---

## Task D12 - Corrections to Diagnostics II (write FIRST; append-only; no new science)

### D12-G1 (HARD): reproduce Diagnostics II's machinery before correcting anything

All of these must reproduce (tolerance 1e-9 on 9-dp values, 2e-6 on 6-dp values):

| quantity | full | H |
|---|---|---|
| D1 table sha256 | `e397a4429c226f99b8b24ec90ef26ef004a28746b3ab6226a5878de935863796` | same |
| 3D table `background_3d_distance.csv` sha256 | `69914df9c60ba5a98e05d798acc14f22f4effd3dc0b4e24ed0ceb18c333312de` | same |
| A222V rho (re-derived, not hard-coded) | -0.088118064 | -0.090021683 |
| `p_spec` frozen | 2/79 = 0.025316456, beaters `{G_P254F}` | 4/79 = 0.050632911, `{AV_195, AV_220, G_P254F}` |
| D9 primary `r_A` / k / beaters | -0.066425 / 2 / `{AV_220, AV_85}` | -0.068692 / 2 / `{AV_220, AV_85}` |
| D10a joint primary (`log1p(dist_seq)`) `r_A` / k | +0.045227 / 69 | +0.047030 / 70 |
| D11.2 Spearman(rho, d3_CA) on resolved N (n=67) | +0.731577372 | +0.713319366 |
| D11.2 Spearman(rho, dist_seq), same 67 | +0.713293691 | +0.695235 |
| D11.4 3D-log joint `r_A` / k (n=67) | +0.093681 / 67 | +0.098715 / 67 |

If any fails, STOP the whole session and log `FAIL`.

### The corrections (K1-K6)

For each: locate the old text with `grep -n` in `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II_LOG.md`
(do not trust any line number given here), quote it verbatim with its **real** line number(s), recompute the true
quantity, print it next to the target, and write the corrected statement composed from computed variables (no
hand-typed numbers). The earlier log is **read only**. Each correction ends with the line
"Cite this, not the old sentence."

- **K1 - D10c's two partial correlations are label-swapped.** Search strings: `reverse of D4`, `sign flip`,
  `distance, not shift, carries`, `partialled the`, and the D10c side-by-side table. Recompute both partials two
  independent ways: (a) from the pairwise Spearman coefficients via the standard partial-correlation formula, and
  (b) by rank-transforming and residualizing, then correlating residuals. Print each with an unambiguous label
  (`rho ~ dist | shift`, `rho ~ shift | dist`). **Targets (N-only 78):**

  | | full | H |
  |---|---|---|
  | pairwise rho~shift / rho~dist / shift~dist | -0.407276268 / +0.696831550 / -0.449969334 | -0.404595405 / +0.673992906 / -0.441230960 |
  | TRUE `rho ~ dist \| shift` | **+0.629667** | **+0.603747** |
  | TRUE `rho ~ shift \| dist` | **-0.146323** | **-0.161718** |

  The old log printed these two values with the labels transposed (it labelled +0.629667 as `rho~shift|dist` and
  -0.146323 as `rho~dist|shift`). Reproduce the bootstrap CIs (background-level, 10,000 draws, `SEED=0`) and
  report them next to the old ones; targets are full `rho~dist|shift` [+0.472642, +0.742385] and `rho~shift|dist`
  [-0.401778, +0.106788]; H [+0.451631, +0.719109] and [-0.416825, +0.083508]. The point estimates are the
  gate; CI agreement within Monte-Carlo error (about 0.01) is expected but is not a gate. State that the log's
  "sign flip" explanation and its "reverse of D4's reading" are consequences of the swap and do not exist: the
  shift partial keeps the raw sign (-0.407 -> -0.146). Also confirm that D11.4's partials (`rho~d3|shift` = +0.651428,
  `rho~shift|d3` = -0.108073 on n=67 full; +0.627446 and -0.123827 H) were labelled correctly, so that the log's
  statement "D11.4's partials mirror D10c's" is true only **after** this correction.
- **K2 - D10b's counts contradict D9's printed residuals.** Search strings: `D10b`, `neighbourhood rank fractions
  are worse`. The log says D10b uses "D9's primary residuals" and reports 8 of 10 (full) and 9 of 10 (H) among the
  10 nearest at or below A222V (rank fractions 0.8182 / 0.9091), and 18 of 20 / 19 of 20 among the 20 nearest.
  D9's own printed tables list `G_P254F`, `AV_195`, `AV_242`, `G_L178T` as **not** at or below A222V's residual,
  which is incompatible. Do three things and print all three side by side:
  (i) **Read script 138's D10b code and quote, verbatim with file and line numbers, which residual vector it
  used.** (ii) Reproduce the old counts (8, 9, 18, 19) and say which residual vector reproduces them (Claude
  suspects the D10a joint-model residuals, where r_A = +0.045227). (iii) Recompute D10b on **D9's primary
  residuals** as pre-registered. **Targets for (iii), implied by D9's printed lists:** at or below A222V's
  residual among the 10 nearest: 1 (`AV_220`) on both views, rank fraction 2/11 = 0.1818; among the 20 nearest:
  1 on both views, 2/21 = 0.0952. Label all as rank fractions, not tests. State that the old "worse than D0's
  raw-rho version" claim is withdrawn.
- **K3 - "not an extrapolation artifact" is overstated.** Search string: `extrapolation artifact`. Report, for each
  D10a and D11.4 variant, the model's predicted rho at A222V's own covariates and the residual, next to the most
  negative **observed** null rho (full -0.096244, H -0.101954, both `G_P254F`). **Targets (full):**

  | variant | predicted rho at A222V's covariates | r_A |
  |---|---|---|
  | shift-only (LOO fit on N) | -0.0217 | -0.066425 |
  | + linear dist_seq | -0.0544 | -0.033711 |
  | + log1p(dist_seq), dist=0 | **-0.1333** | +0.045227 |
  | + log1p(dist_seq), clamped dist=2 | -0.1071 | +0.019003 |
  | + log1p(d3_CA), d3=0 (n=67) | **-0.1818** | +0.093681 |

  The log-form predictions at distance 0 lie **below every observed null**, so the joint results at those
  points are extrapolations of a fitted surface, whatever the hat value is. A hat value inside the null range
  does not make a point interpolated. State this, and note that only the linear form leaves A222V more extreme
  than predicted.
- **K4 - form dependence.** Search strings: `destroys the adjusted advantage`, `any of the three forms`. Recompute
  and restate the D10a table so the form-dependence is visible: A222V's signed rank and `p_spec_adj` under linear
  dist (**10/79, 0.126582** full; **11/79, 0.139241** H) versus `log1p(dist)` (**70/79, 0.886076** full; **71/79,
  0.898734** H). All are above the frozen thresholds; the magnitudes differ by seven-fold. State that no
  version is a calibrated tail probability and that the direction, not the size, is the robust part.
- **K5 - the garbled sentence in summary section 5.** Search string: `partialled the`. Quote it and replace it
  with a correct statement using K1's corrected values.
- **K6 - D10 flag 3 and the D10 verdict paragraph.** Quote "D10c's answer and D10a's answer point opposite ways" and
  the D10c verdict paragraph and state which parts are void after K1.

**Outputs:** the D12 log entry, and `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` (one section per K item: old quote and
real line numbers, recomputed vs target, corrected statement). Report its sha256.

---

## Task D13 - A222V against its same-site comparators (Arm S), directly

**Why:** the 18 Arm S backgrounds (A222X, X not in {A, V}) are the only backgrounds at distance 0. They are
the distance-matched comparison that no adjustment can supply. They share A222V's site, not its substitution.
The frozen design compared S to the nulls (`D_site`); it never compared A222V to S.

Pre-register in the docstring before running. Descriptive; no p-values, rank fractions only (n = 19).

- **D13.1 raw rho.** A222V's rank within Arm S union {A222V} (rank 1 = most negative) on the full frame and H:
  the count of Arm S members with rho_b at or below A222V's, and the resulting rank fraction
  `(1 + #{S: rho_b <= rho_A}) / (1 + 18)`. List every Arm S member at or below A222V's rho with its rho.
- **D13.2 shift-adjusted residual, exchangeable construction (primary).** Fit OLS `rho ~ a + c*mean|delta|` on
  **all 78 nulls** (the D9 fit; Arm S and A222V are both out of sample). Compute out-of-sample residuals for
  A222V and each Arm S member; rank fraction as above. Sensitivity: D4's all-96 fit (Arm S in sample; A222V out of
  sample), both views.
- **D13.3 what this can and cannot say.** State plainly: Arm S shares the site and differs in substitution, so
  this speaks to substitution-specificity within the site, at n=19; the Grantham gradient over the same 18 was
  NOT RESOLVED (Phase 1b P3, Phase 2 A4). It cannot separate "the residue" from "the region."

**Targets to confirm (from Diagnostics II's D0 C2 output):** `A222_C` is at or below A222V on raw rho
(full -0.093530 vs -0.088118; H -0.090964 vs -0.090022) and on the all-96 residual (full -0.066534 vs -0.059133;
H -0.063441 vs -0.061058). No target is given for how many other Arm S members are; report it.

---

## Task D14 - Model-free gradient bins by 3D distance, including Arm S at 0 A

**Why:** the parametric adjustments disagree wildly (linear vs log) because they extrapolate a fitted form to a
point no null occupies. This task shows the raw picture with no fitted form.

Pre-register in the docstring before running (bins fixed now; do not tune):

- Use `d3_CA` from `data/processed/phase2_diagnostics/background_3d_distance.csv` (verify its sha256). Bins by
  `d3_CA`: **{exactly 0: Arm S}**, **(0, 12]**, **(12, 20]**, **(20, 30]**, **(30, 45]**, **(45, inf)**. Backgrounds
  with `resolved` false (11 nulls) are listed by name and excluded; do not impute.
- Per bin and view: n by arm, mean / median / min / max of rho_b, mean of mean|delta_b| (so the shift covariate is
  visible in every bin), and A222V's rho as a reference line.
- **D14.1 discontinuity check.** Difference of means `mean(rho, Arm S) - mean(rho, nulls in (0, 12])` with an
  independent-groups background-level bootstrap CI (10,000 draws, `SEED=0`); label the bin as n=6 and unstable.
  Also list the six (`G_I192T`, `AV_220`, `AV_155`, `AV_195`, `G_L178T`, `AV_175`, d3_CA 5.06 to 10.54 A).
- **D14.2 post-hoc target check.** Reproduce Claude's calculation from the D2 table: mean rho of the 10
  sequence-nearest nulls is **-0.0557 (full), -0.0591 (H)** against Arm S mean **-0.0652 (full), -0.0702 (H)**.
  Label POST-HOC; it was computed after seeing the data.
- **D14.3 figure.** If `matplotlib` imports, save `data/processed/phase2_diagnostics/rho_vs_d3.png`: rho_b (full)
  vs `d3_CA`, colored by arm (S, V, G), A222V as a horizontal line, beaters annotated. Else `SKIPPED`.

---

## Task D15 - Far-variant restriction: does the anchor survive without variants near 222? (mechanism test)

**Hypothesis under test (Claude's, stated so that it can fail):** rho_b tracks the overlap between the region a
background perturbs and the region where A222V's own epistasis is concentrated. If so, dropping target variants
near 222 should collapse the gradient of rho_b against distance-to-222, and weaken or remove A222V's own rho. If
the gradient and the anchor persist among distal variants, the statistic carries long-range information beyond
spatial overlap. **Either outcome is informative and is reported with equal directness.**

**The confound this must control:** removing rows shrinks every background's row count, which adds noise to every
rho_b and attenuates any cross-background correlation by itself. A drop in the gradient after removing rows
near 222 is therefore uninterpretable without a matched control. **The matched-deletion control below is not
optional.**

### Construction (pre-register before running)

- Start from script 125's usable rows for each background and for A222V (import via `phase2_diag`). A222V's rho is
  re-derived from its own `delta_esm` over the same usable rows, as in D0/D9. Views: full and H.
- **Distances.** Chain-A CA-CA distance from each **frame position** `p` to residue 222, `d3_222(p)`, and from `p` to
  a background's position, `d3_b(p)`, using the structure conventions and loader of script 139 (`data/raw/6FCX.pdb`,
  frame position p = PDB residue number p; positions 2-39, 161-171, 392-396, 652-656 have no chain-A coordinates).
  **Rows at unresolved positions are dropped from every 3D variant, including R = 0**, and their count is reported;
  they are never imputed.
- **Gate D15-G1 (HARD):** the loader reproduces the stored `ca_dist_222` for the 9,595 rows of
  `task77_thermompnnD_doubles.csv` to < 1e-6, and the monomer / dimer-aware far fractions 9,232/9,595 = 96.2168%
  and 9,128/9,595 = 95.1329% (as D11-G1). Also reproduce **unrestricted** baselines: all 96 rho_full and rho_H against
  the D1 table to 1e-9 and A222V's rho to 1e-9.
- **Radii.** 3D `R` in {0, 10, 20, 30} A, all reported, none selected. `R = 0` on resolved rows is the like-for-like
  baseline; the unrestricted all-rows value is also printed for reference.
  - **S1 (primary): far from 222.** Keep rows with `d3_222(p) > R`.
  - **S2 (sensitivity): far from both.** Keep rows with `d3_222(p) > R` **and** `d3_b(p) > R`. Backgrounds at
    unresolved positions drop out of S2 (list them); Arm S and A222V have `d3_b = d3_222`, so S2 = S1 for them.
    S2 has no matched control (per-background row sets differ); label it descriptive.
  - **Sequence sensitivity:** keep rows with `|p - 222| > Rs`, Rs in {25, 50}, S1 only, no unresolved-row issue.
- **Statistics per (variant, R, view):**
  1. Rows retained: min / median / max across backgrounds, and positions retained.
  2. **A222V's rho on the retained rows** with a **position-cluster** bootstrap 95% CI (10,000 draws, `SEED=0`;
     clusters = retained target positions; identity gate: every cluster once reproduces the point estimate to
     1e-12) and whether the CI excludes zero.
  3. **`p_spec`** on the restricted rho_b, frozen construction and direction (`rho_b <= rho_A222V`), N = 78 for S1
     (S2 and 3D use the resolved nulls; state n), with the at-or-below nulls named.
  4. **The gradient:** `Spearman(rho_b, d3_b)` across resolved nulls (n = 67) and across all resolved backgrounds
     (n = 85), background-level bootstrap CI (10,000 draws, `SEED=0`) on the restricted rho_b.
- **Baseline targets at R = 0, unrestricted, N-only resolved (n = 67):** gradient +0.731577372 (full) and
  +0.713319366 (H) (D11.2). A222V rho -0.088118064 / -0.090021683.

### The matched-deletion control (S1 only)

For each R and view, let `k_R` = the number of **positions** the S1 filter removes from the resolved universe (for
the H view, the universe is the H positions). Run `N_DRAW = 200` random deletions (smoke at 20; `SEED=0`): each
draw removes `k_R` positions chosen uniformly without replacement from the same universe (**whole positions,
all their variants**, matching the filter's cluster structure; the same removed set is applied to every background
within a draw so backgrounds are perturbed identically), then recomputes A222V's rho, all 96 rho_b, the gradient
(n = 67) and `p_spec`. Report for each statistic the random-deletion mean and the 2.5th / 97.5th percentiles, the
S1 value, and the fraction of random draws at or below and at or above the S1 value.

- **Gate D15-G2 (HARD):** deleting **zero** positions reproduces the R = 0 baseline exactly, and applying the
  **actual S1 removed set** through the same deletion function reproduces the S1 statistic exactly (|diff| 0).
- **Reporting rule (descriptive, no outcome word):** flag an S1 statistic as "outside the matched-deletion 95%
  range" or "inside it." State that a fall in the gradient that stays inside the matched-deletion range is not
  attributable to the removed positions, and one that falls outside it is.
- Print the `d3_222(p)` distribution of the target positions (percentiles) so the reader sees how many positions
  each R removes. Position 222 itself is not a frame target position; state how many frame positions lie within
  each R of it.

---

## Task D16 - Adjustment with no fitted functional form and no extrapolation (isotonic)

**Why:** D10a's answers range from p_spec_adj 0.13 (linear) to 0.89 (log) to 1.00 (3D-log) because they extrapolate
to distance 0. A monotone (isotonic) fit needs no functional form and, with flat extrapolation at the boundary,
predicts nothing at distance 0 that is not already seen at the nearest null.

Pre-register in the docstring before running. Designate now: **primary = D16b on `d3_CA`**; the rest are reported
side by side, none selected.

- **Method.** `IsotonicRegression(increasing=True, out_of_bounds='clip')` from `sklearn.isotonic` if importable
  (else `scipy.optimize.isotonic_regression` if present; else `BLOCKED`, and do not install). rho is expected to
  increase with distance (more negative near 222), so the increasing constraint is the observed direction.
  **Leave-one-out for nulls:** for each null `b`, refit on the other nulls and predict at `b`'s distance;
  **out-of-sample for A222V and Arm S:** fit on all nulls, predict at distance 0 (flat extrapolation gives the
  fitted value at the smallest null distance). Residual `r = rho - g(distance)`.
- **D16a - raw rho on distance.** Isotonic `rho ~ g(d3_CA)` over the resolved nulls (n = 67). Report, for both
  views: `g(0)` (the fitted step value at the boundary), `r_A`, A222V's signed rank within nulls union {A222V}, the
  nulls at or below `r_A`, `p_spec_adj = (1 + k)/(1 + n)`, and whether it is at or below 0.05 (full) / 0.10 (H).
- **D16b - two-stage, primary.** Stage 1: D9's primary leave-one-out shift residuals (`r^shift`; import script
  137's construction; A222V and Arm S from the fit on all N). Stage 2: isotonic `r^shift ~ g(d3_CA)`, leave-one-out
  for nulls, out-of-sample for A222V and Arm S. Same reporting. Disclose the small optimism that stage 1's fit is
  not refit inside stage 2's leave-one-out.
- **D16c - sequence-distance versions** of D16a and D16b over all 78 nulls (`dist_seq`), as sensitivities.
- **D16d - Arm S under the same fits.** Report each Arm S member's residual under D16b, and A222V's rank within
  Arm S union {A222V} on it (rank fractions; n = 19). This is the direct same-site comparison D13 gives raw, now
  under a shift-and-distance adjustment that needs no extrapolation.
- Print the fitted step function `g` (breakpoints and values) for D16a and D16b so the reader can see where
  the pooled blocks are and what `g(0)` is.

**Limits to state in the docstring and entry:** the near-222 end of `g` rests on about 6 nulls within 10.5 A, so
`g(0)` is set by a handful of points; isotonic pooling makes it a step function; `p_spec_adj` is a rank count on
leave-one-out residuals of overlapping fits, not a calibrated tail probability.

---

## S2. Mandated SUMMARY contents

`## SUMMARY` in this order:
1. **READ THIS FIRST - D15.** The far-variant restriction table across R (S1, both views): A222V's rho with CI, the
   gradient, `p_spec`, each next to its matched-deletion range and the inside/outside flag. Say plainly whether the
   gradient and the anchor persist among distal variants, and whether the result is attributable to the removed
   positions.
2. **D16.** `g(0)`, `r_A`, rank, `p_spec_adj` for D16a and D16b (primary), both views, and D16d's same-site rank.
3. **D13** (A222V vs Arm S, raw and adjusted) and **D14** (binned gradient, discontinuity check, figure status).
4. **D12** corrections K1-K6 as a table: old text, real line numbers, recomputed vs target, corrected statement;
   sha256 of the corrections file.
5. **Plain two-sided statement** of what the data now support: "tied to position 222," "tied to the region around
   222," "a spatial-overlap effect with no long-range content," or "cannot be separated," worded with the same
   directness whichever way it falls.
6. Every gate, PASS/FAIL, value, D12-G1 first.
7. Confirmation that no protected file, earlier log, earlier script or `phase2_diag.py` was edited; nothing was
   committed; no torch/esm/thermompnn import occurred.
8. The single most important entry to read first, with its line number.

---

## What this session is NOT

- Not a revision of the frozen `PHASE2_PREREG.md` verdict or a new decision rule.
- Not new scoring. A spatial-neighbour arm (new backgrounds at the residues within about 10 A of 222) would fix the
  missing distance-matched null properly, but it needs new scoring and a new pre-registration and should follow
  this session, not be smuggled into it.
- Not the write-up. That should follow this session, citing `PHASE2_DIAGNOSTICS_II_CORRECTIONS.md` rather than
  the superseded sentences in the Diagnostics II log.
- Not Carlson, Andrews and Simons (2025)'s rank-statistics method, and not Phase 3.
