# PHASE 2 diagnostics I -- corrections (append-only)

**Written:** 2026-09-29 (OpenCode, executor) · **Doc:** `docs/tasks/phase2-diagnostics-ii-neighbourhood/PHASE2_DIAGNOSTICS_II.md` task D0
**Corrects:** `docs/tasks/phase2-diagnostics-locality-magnitude/PHASE2_DIAGNOSTICS_LOG.md`
**Generator:** `scripts/136_phase2_diag2_corrections.py`

**The earlier log has NOT been edited.** Every correction below is recorded here and in `PHASE2_DIAGNOSTICS_II_LOG.md` only. Line numbers are the REAL line numbers on disk, located by scanning the file for the quoted string, not copied from the planning document.

**Resampling unit for every number in this file: NONE.** Each is a deterministic point value or an exact rank count. No bootstrap and no permutation was performed.

**Wording:** the three outcome words reserved for the frozen `PHASE2_PREREG.md` section-5 test are not used as the label for any result computed here. Where an earlier log is quoted it is inside a block quote and marked as a quote.

---

## Gate D0-G1 (HARD)

| gate | what it checked | result | value |
|---|---|---|---|
| G0.1 table sha256 | match | **PASS** | =none |
| G0.2 A222V rho_full | got -0.08811806424891734 vs -0.088118064 | **PASS** | =2.489e-10 |
| G0.3 A222V rho_H | got -0.09002168303339808 vs -0.090021683 | **PASS** | =3.340e-11 |
| G0.4 p_spec(full) == 2/79 with {G_P254F} | got 0.02531645569620253 = (1+1)/(1+78), beaters ['G_P254F'] vs ['G_P254F'] | **PASS** | =0.000e+00 |
| G0.5 p_spec(H) == 4/79 with {AV_195, AV_220, G_P254F} | got 0.05063291139240506 = (1+3)/(1+78), beaters ['AV_195', 'AV_220', 'G_P254F'] vs ['AV_195', 'AV_220', 'G_P25 | **PASS** | =0.000e+00 |

**D0-G1: PASS (5/5 checks).** The session continued.

---

## C1 — The D7.1 sign-explicit sentence reports the count of placebos AT OR BELOW A222V as if it were the count A222V exceeds

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `more negative than 1 of the 78` -> line(s) 329, 768
  - line 329, quoted verbatim:

    ```
    >>> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 1 of the 78 placebo backgrounds on the full frame and 3 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).
    ```
  - line 768, quoted verbatim:

    ```
    > Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 1 of the 78 placebo backgrounds on the full frame and 3 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| # placebos AT OR BELOW A222V (full) | **1 of 78** | this is what the old sentence printed |
| # placebos AT OR BELOW A222V (H) | **3 of 78** | this is what the old sentence printed |
| A222V more negative than N of 78 (full) | **77 of 78** | target 77 of 78 |
| A222V more negative than N of 78 (H) | **75 of 78** | target 75 of 78 |

**Corrected statement:**

> >>> Substituting the alanine-to-valine change at position 222 for the wild-type residue produces a background-specific NEGATIVE association (Spearman rho = -0.088118 on the full frame, -0.090022 on the held-out H frame) between ESM-2's implied per-variant score shift and measured epistasis, and that association is more negative than 77 of the 78 placebo backgrounds on the full frame and 75 of the 78 on the held-out H frame (rank-based p_spec = 0.025316 and 0.050633 respectively).

**Cite this, not the old sentence.**

---

## C2 — 'the most extreme residual of all 96' is false, and the percentile definition printed alongside it is ambiguous

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `most extreme residual of all 96` -> line(s) 500, 708
  - line 500, quoted verbatim:

    ```
    - **For:** A222V's own position is not on the confound line. It is a mid-pack shifter with an extreme ρ, and after accounting for magnitude it remains the most extreme residual of all 96. The frozen comparison of A222V *against* the null set is not thereby explained away.
    ```
  - line 708, quoted verbatim:

    ```
    So: the one background that most directly challenges the frozen result is the extreme of the shift-magnitude confound, which is a genuine problem for the write-up. But A222V is a *mid-pack* shifter with an *extreme* ρ, and after accounting for magnitude it is still the most extreme residual of all 96. Both facts are true and neither cancels the other.
    ```
- search `96.9th percentile` -> line(s) 479, 487, 701, 702
  - line 479, quoted verbatim:

    ```
    A222V's residual sits at the 96.9th percentile of the 96 background residuals (0 = most negative)
    ```
  - line 487, quoted verbatim:

    ```
    A222V's residual sits at the 96.9th percentile of the 96 background residuals (0 = most negative)
    ```
  - line 701, quoted verbatim:

    ```
    RESIDUAL = -0.059133, at the 96.9th percentile of the 96 residuals
    ```
  - line 702, quoted verbatim:

    ```
    [H]     RESIDUAL = -0.061058, also 96.9th percentile
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| A222V residual (full) | **-0.059133** | target -0.0591 |
| A222V residual (H) | **-0.061058** | target -0.0611 |
| AV_220 residual (full) | **-0.075724** | target -0.0757 |
| AV_220 residual (H) | **-0.084010** | target -0.0840 |
| # backgrounds at or below A222V's residual (full) | **3** | target 3 |
| # backgrounds at or below A222V's residual (H) | **3** | target 3 |
| A222V rank among the 96 + A222V, most negative = 1 (full / H) | **4 / 4** | the earlier log's claim was rank 1; the plan predicts NOT rank 1 -- recomputed rank 4 / 4 confirms the correction |

**Corrected statement:**

> Using D4's exact construction (OLS of rho_b on mean|delta_b| over all 96 backgrounds with an intercept, A222V excluded from the fit), A222V's residual is -0.059133 (full) and -0.061058 (H).  It is NOT the most extreme residual of all 96: 3 background(s) lie at or below it on the full frame -- `AV_220` (V, d=2); `AV_85` (V, d=137); `A222_C` (S, d=0) -- and 3 on H -- `AV_220` (V, d=2); `AV_85` (V, d=137); `A222_C` (S, d=0) -- putting A222V at rank 4 of 97 (full) and rank 4 of 97 (H), counting the most negative as rank 1.  The percentile the log printed is the fraction of the 96 with a residual GREATER than A222V's, so 96.9 refers to the MOST POSITIVE end; the log's parenthetical '(0 = most negative)' describes the opposite end from the one the code computes.

**Cite this, not the old sentence.**

---

## C3 — D3's 'carried entirely by Arm G' reading is backwards; arm-alone p_spec is a post-hoc decomposition

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `carried entirely by Arm G` -> line(s) 742, 814
  - line 742, quoted verbatim:

    ```
    Decomposition only; no p_spec redefined. **The full-frame result is carried entirely by Arm G.** The exhaustive, fitness-blind arm contains no background at or below A222V's full-frame ρ. On H the split reverses: Arm V contributes two of the three (`AV_220`, `AV_195`).
    ```
  - line 814, quoted verbatim:

    ```
    7. **Two structural facts about the arms belong in the write-up.** The full-frame result is carried entirely by Arm G (rank 1/39 in Arm V, 2/41 in Arm G), and the two arms are not severity-matched (Arm G mean +6.79 vs Arm V +4.94).
    ```
- search `exhaustive control agrees` -> line(s) 311
  - line 311, quoted verbatim:

    ```
    **Anything unexpected or worth flagging:** The full-frame comparison is carried entirely by the 40-member uniform random arm. The exhaustive, fitness-blind arm — the one with no selection at all — contains **no** background at or below A222V's full-frame ρ. That is a substantive fact for interpretation and the opposite of what a "the exhaustive control agrees" reading would predict. It does not weaken the frozen result (the frozen test is defined on the pooled 78), but it is exactly the kind of thing the write-up should say rather than let a reader assume. On H, Arm V does contribute two of the three.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| arm-alone k (full|V) | **0** | target 0 |
| arm-alone k (H|V) | **2** | target 2 |
| arm-alone k (full|G) | **1** | target 1 |
| arm-alone k (H|G) | **1** | target 1 |
| arm-alone p (full|V) | **0.025641** | target 0.025641 |
| arm-alone p (H|V) | **0.076923** | target 0.076923 |
| arm-alone p (full|G and H|G) | **0.048780 / 0.048780** | target 0.048780 / 0.048780 |

**Corrected statement:**

> POST-HOC DECOMPOSITION -- the frozen test is defined on the pooled 78; this redefines nothing.  Recomputed from the table: Arm V alone has 0 at-or-below placebos on the full frame (post-hoc p = 0.025641, at or below the frozen threshold 0.05) and 2 on H (post-hoc p = 0.076923, at or below 0.1); Arm G alone has 1 on the full frame (post-hoc p = 0.048780, at or below 0.05) and 1 on H (post-hoc p = 0.048780, at or below 0.1).  'Carried entirely by Arm G' is RETRACTED: on the full frame Arm V's count of 0 out of 38 is rank 1/38 -- the strongest agreement the design-matched arm can give -- and the only full-frame exception lies in Arm G.

**Cite this, not the old sentence.**

---

## C4 — 'its magnitude is the largest in the null set in either direction' is wrong as worded

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `largest in the null set in either direction` -> line(s) 351, 770
  - line 351, quoted verbatim:

    ```
    **Verdict:** **PASS**, and this is a **favourable** result for the Phase 2 write-up, reported as directly as D2's adverse one. The `|ρ|` sensitivity is **numerically identical** to the signed test on both views: `p_spec_abs(full) = p_spec(full) = 0.025316456` and `p_spec_abs(H) = p_spec(H) = 0.050632911`. The reason is visible in the output: **zero** backgrounds are positive with `|ρ| ≥ |ρ_A222V|`, so the two counts coincide. In other words the verdict does **not** depend on the pre-declared one-sided direction at all. A222V's association is not merely the most negative in the null set; its magnitude is the largest in the null set in either direction. That removes one of the two external reviews' specific objections — that a pre-declared direction could be manufacturing the result — on this dataset. It does not address the locality or shift-magnitude concerns, which are separate.
    ```
  - line 770, quoted verbatim:

    ```
    **The |ρ| sensitivity is numerically identical to the signed test on both views** — `p_spec_abs(full) = p_spec(full) = 0.025316456`, `p_spec_abs(H) = p_spec(H) = 0.050632911`. The reason is printed, not asserted: **zero** backgrounds are positive with |ρ| ≥ |ρ_A222V|, so the `>=` count and the `<=` count coincide. **The verdict does not depend on the pre-declared one-sided direction at all** — A222V's magnitude is the largest in the null set in either direction. This removes one of the two external reviews' specific objections, on this dataset.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| rank of |rho_A222V| (full) | **2/79** | target 2/79 |
| rank of |rho_A222V| (H) | **4/79** | target 4/79 |
| # positive placebos reaching that magnitude (full / H) | **0 / 0** | target 0 / 0 |

**Corrected statement:**

> The rank of |rho_A222V| within N u {A222V} is 2/79 (full) and 4/79 (H) -- i.e. 1 and 3 of the 78 placebos have |rho_b| >= |rho_A222V| -- not rank 1.  The SUBSTANTIVE D7 finding stands and is unaffected: 0 and 0 POSITIVE placebos reach that magnitude, so the pre-declared one-sided direction is not driving the result and the |rho| sensitivity is numerically identical to the signed test.

**Cite this, not the old sentence.**

---

## C5 — D8's 'a weaker one' is muddled; the real fragility is the k at which the pooled comparison crosses the thresholds

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `a weaker one` -> line(s) 395
  - line 395, quoted verbatim:

    ```
    **Anything unexpected or worth flagging:** `1/78 = 0.012820513` is **slightly larger** than `1/79 = 0.012658228` — removing a background raises the floor, so the leave-one-out `p_spec` understates the corresponding frozen value by a hair even before the numerator change. The two effects (−0.012496 on full) are almost entirely the numerator going 1 → 0, not the floor. Worth stating so nobody reads the leave-one-out as a "better" or "cleaner" result; it is a weaker one. The `1/78` value quoted in the plan is confirmed exactly.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| leave-one-out p_spec change (full) | **0.025316 -> 0.012821** | target 0.0253 -> 0.0128 |
| (1+2)/79 | **0.0380** | target 0.0380 |
| (1+3)/79 | **0.0506** | target 0.0506 |
| (1+6)/79 | **0.0886** | target 0.0886 |
| (1+7)/79 | **0.1013** | target 0.1013 |
| gap AV_220 (full) | **+0.00352** | target 0.00352 |
| gap AV_195 (full) | **+0.00396** | target 0.00396 |

**Corrected statement:**

> D8's phrase 'it is a weaker one' is muddled: the leave-one-out p_spec FALLS (full 0.025316 -> 0.012821; H 0.050633 -> 0.038462), which is smaller, not weaker.  The relevant fragility is how few additional at-or-below placebos would move the pooled comparison to the frozen thresholds: at or below 0.05 through k=2 (0.0380) and above at k=3 (0.0506); at or below 0.10 through k=6 (0.0886) and above at k=7 (0.1013).  The five nulls that just missed, full frame: `AV_220` (gap +0.00352); `AV_195` (gap +0.00396); `AV_113` (gap +0.01031); `G_Y197V` (gap +0.01124); `AV_85` (gap +0.01689).  On H: `AV_155` (gap +0.00122); `AV_113` (gap +0.00309); `AV_85` (gap +0.00809); `G_L178T` (gap +0.01567); `G_Y197V` (gap +0.01752).  A222V's own position-cluster 95% CI is [-0.1173, -0.0595] (docs/tasks/phase1-corrections-diagnostics/PHASE1_LOG.md:383); it comes from a DIFFERENT bootstrap from any per-background CI and is context, not a test.

**Cite this, not the old sentence.**

---

## C6 — The k-removal 'strengthens the comparison' is mechanical

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `essentially every placebo` -> line(s) 241, 731
  - line 241, quoted verbatim:

    ```
    2. **A222V is nonetheless more negative than essentially every placebo, including the nearest ones.** The nearest placebo to 222 (`AV_220`, d=2) is *less* negative than A222V on the full frame. And critically, removing the near-222 placebos does **not** weaken the pooled comparison — it *strengthens* it (k=10 drives both p_spec values to their floors, 0/69, because the two H-frame beaters `AV_195` and `G_P254F` are themselves among the ten nearest).
    ```
  - line 731, quoted verbatim:

    ```
    Removing near-222 placebos does not weaken the comparison — **it strengthens it**, because two of the three H-frame beaters (`AV_195` at d=27, `G_P254F` at d=32) are themselves among the ten nearest, and at k=10 nothing is left at or below. A222V is more negative than essentially every placebo *including the nearest ones*.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| beaters inside the k=10 removed set | **3/3** | target 3/3 |
| C(10,3) | **120** | target 120 |
| C(78,3) | **76076** | target 76076 |
| C(10,3)/C(78,3) | **0.001577** | target 0.001577 |
| C(20,3)/C(78,3) [second disclosed value] | **0.014985** | no target in the plan |

**Corrected statement:**

> D2's 'k-removal strengthens the comparison' is MECHANICAL, not informative: the k=10 nearest-to-222 removed set contains ALL 3 beaters named in D1 (`AV_195`, `AV_220`, `G_P254F`), so p_spec reaching its floor is guaranteed by construction.  POST-HOC (the beaters were identified after seeing rho; only the distance ranks are fixed in advance), the probability that all 3 beaters fall within the k nearest of the 78 nulls under random placement is C(k,3)/C(78,3): k=10 gives 120/76076 = 0.001577 and k=20 gives 1140/76076 = 0.014985.  Both are reported; neither is selected.

**Cite this, not the old sentence.**

---

## C7 — 'A222V is unusual relative to its own neighbourhood' is not established by the numbers quoted

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `relative to its own neighbourhood / more extreme than its own neighbourhood` -> line(s) 810, 243
  - line 810, quoted verbatim:

    ```
    3. **A locality gradient in ρ_b is real and large (r ≈ +0.70 within the null set alone) and survives region correction.** Position 222's neighbourhood behaves differently from the rest of the protein. This must be disclosed, and it reframes the result: A222V is unusual **relative to its own neighbourhood**, not because its neighbourhood is unlike everywhere else.
    ```
  - line 243, quoted verbatim:

    ```
    **Verdict:** **PASS**, with a result that cuts both ways and must be written up as both. The gradient is real and is a genuine threat to the interpretation "position 222 produces an association unusually unlike other positions" — because *other positions near 222 produce a similar-signed association too*, and the reason A222V is unusual is that it is **more extreme than its own neighbourhood**, not that its neighbourhood is unlike the rest of the protein. The k-removal is the more directly relevant test of the reviews' actual worry ("is the verdict propped up by near-222 placebos?") and its answer is **no** — the verdict is if anything more robust without them. Neither fact cancels the other, and the frozen §5 outcome is untouched: this session reports the gradient, it does not adjudicate it.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| k=10 at-or-below (full) | **1** | target 1 |
| k=10 at-or-below (H) | **3** | target 3 |
| k=10 rank fraction (full) | **0.1818** | target 0.1818 |
| k=10 rank fraction (H) | **0.3636** | target 0.3636 |
| k=20 rank fraction (full / H) | **0.0952 / 0.1905** | no target in the plan |

**Corrected statement:**

> 'A222V is unusual relative to its own neighbourhood' is NOT established.  Recomputed on the k nearest nulls by sequence distance (ties by ascending bg_id, D2's rule R9) as (1+k)/(1+n): k=10 gives 1 at-or-below on the full frame (2/11 = 0.1818) and 3 on H (4/11 = 0.3636); k=20 gives 1 (2/21 = 0.0952) and 3 (4/21 = 0.1905).  These are RANK FRACTIONS, NOT TESTS -- n is tiny.  As reported they cannot distinguish '222-specific' from 'neighbourhood-specific'; they show only that the earlier log's wording overreaches.

**Cite this, not the old sentence.**

---

## C8 — D2's 'including the nearest ones' is true of the full frame and false of H

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `essentially every placebo` -> line(s) 241, 731
  - line 241, quoted verbatim:

    ```
    2. **A222V is nonetheless more negative than essentially every placebo, including the nearest ones.** The nearest placebo to 222 (`AV_220`, d=2) is *less* negative than A222V on the full frame. And critically, removing the near-222 placebos does **not** weaken the pooled comparison — it *strengthens* it (k=10 drives both p_spec values to their floors, 0/69, because the two H-frame beaters `AV_195` and `G_P254F` are themselves among the ten nearest).
    ```
  - line 731, quoted verbatim:

    ```
    Removing near-222 placebos does not weaken the comparison — **it strengthens it**, because two of the three H-frame beaters (`AV_195` at d=27, `G_P254F` at d=32) are themselves among the ten nearest, and at k=10 nothing is left at or below. A222V is more negative than essentially every placebo *including the nearest ones*.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| AV_220 rho (full) | **-0.084598** | A222V -0.088118 |
| AV_220 at or below A222V (full)? | **NO** | plan says the log is wrong only on H |
| AV_220 rho (H) | **-0.094480** | A222V -0.090022 |
| AV_220 at or below A222V (H)? | **YES** | plan says YES |

**Corrected statement:**

> D2's verdict sentence overstates the full-frame case.  Correctly, per view: on the FULL frame `AV_220` (d=2) is at -0.084598 against A222V's -0.088118, so it is NOT at or below A222V (gap +0.003520); on H it is -0.094480 against A222V's -0.090022, so it IS AT OR BELOW A222V (gap -0.004459).  'More negative than essentially every placebo, INCLUDING the nearest ones' is therefore true of the full frame and FALSE of the H frame, where the single nearest placebo is at or below A222V.

**Cite this, not the old sentence.**

---

## C9 — The 'protected files do not exist' flag was a wrong-path check

**Old text, verbatim, with the REAL line numbers in `PHASE2_DIAGNOSTICS_LOG.md`:**

- search `do not exist in this repository` -> line(s) 822
  - line 822, quoted verbatim:

    ```
    - **Two protected paths named in the instructions do not exist in this repository:** `MTHFR_RESULTS_LOG.md` and `PROJECT_SUMMARY_FINAL.md` are not present (`ls` returns "No such file or directory"). I am reporting their absence rather than claiming to have preserved them, per AGENTS §5's rule against citing files not verified to exist. If they are expected to be somewhere else, that is worth checking separately.
    ```

**Recomputed value vs the plan's target:**

| quantity | recomputed | plan target |
|---|---|---|
| docs/tasks/results-log/MTHFR_RESULTS_LOG.md | **EXISTS** | plan predicts it exists |
| docs/writeups/PROJECT_SUMMARY_FINAL.md | **EXISTS** | plan predicts it exists |
| find results | **./docs/tasks/results-log/MTHFR_RESULTS_LOG.md; ./docs/writeups/PROJECT_SUMMARY_FINAL.md** | plan predicts the two paths above |

**Corrected statement:**

> The earlier flag WAS a wrong-path check, not an absence.  Both files exist; Diagnostics I looked for them at the repository root.  `docs/tasks/results-log/MTHFR_RESULTS_LOG.md` EXISTS and `docs/writeups/PROJECT_SUMMARY_FINAL.md` EXISTS, and `find` returns exactly those two paths.  The earlier log's statement that the files 'are not present (ls returns "No such file or directory")' is true only of the ROOT-level paths and is FALSE as a statement about the repository.  Neither file was read into, modified, or touched by this session.

**Cite this, not the old sentence.**

---

## Plan-target disagreements

**None.** Every plan target recomputed to the value the plan states.

