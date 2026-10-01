# PHASE 2 diagnostics IV — corrections K11–K16 to the Diagnostics III log

**Written by:** `scripts/152_phase2_diag4_corrections.py` (task D22), from inside the script, so every number is interpolated from a variable parsed at run time and every old sentence is quoted at a line number found by searching the log now.
**Corrects:** `docs/tasks/phase2-diagnostics-iii-mechanism/PHASE2_DIAGNOSTICS_III_LOG.md` — pre-existing lines are **READ ONLY, never edited**; task D22 authorizes exactly ONE append-only, write-LAST addition to that log (performed AFTER this file is written), which only adds lines, so every line number below — referencing the pre-append 1368-line log — stays valid.
All 85 D22 gates PASS (run first; listed at the end of `PHASE2_DIAG4_D22_FULL_OUTPUT.txt`).

---

## K11 — "A222V's position-cluster CI includes zero in all twelve restricted variants"

**Old text, at these REAL line numbers of the pre-append log:**

- `INCLUDES ZERO IN ALL TWELVE` — line 1250:
  > **THE HONEST CAVEAT, stated as prominently as the result: A222V's position-cluster CI INCLUDES ZERO IN ALL TWELVE VARIANTS ON BOTH VIEWS** - R = 0, 10, 20, 30 and both sequence sensitivities, both frames - and in the unrestricted baseline too. This task does not establish A222V's own rho; it shows that whatever signal exists is concentrated near 222 and is not carried by distal variants.
- `Twelve out of twelve` — line 834:
  > - **The honest caveat, and it is not small: A222V's position-cluster CI INCLUDES ZERO in EVERY variant on BOTH frames** - at R = 0, at R = 10, at R = 20, at R = 30, and on both sequence sensitivities, on both views. Twelve out of twelve. That is true of the unrestricted baseline too ([-0.110517, +0.052946] at R = 0 resolved; the doc's own quoted Phase 1 CI [-0.117333, -0.059511] excludes zero only because it used a different bootstrap on the full row set). **I am not claiming A222V's own rho is established by this task; I am reporting that whatever signal is there is concentrated near 222 and is not carried by distal variants.** Reported with the same directness as the gradient result.
- `whatever signal is there` — line 834:
  > - **The honest caveat, and it is not small: A222V's position-cluster CI INCLUDES ZERO in EVERY variant on BOTH frames** - at R = 0, at R = 10, at R = 20, at R = 30, and on both sequence sensitivities, on both views. Twelve out of twelve. That is true of the unrestricted baseline too ([-0.110517, +0.052946] at R = 0 resolved; the doc's own quoted Phase 1 CI [-0.117333, -0.059511] excludes zero only because it used a different bootstrap on the full row set). **I am not claiming A222V's own rho is established by this task; I am reporting that whatever signal is there is concentrated near 222 and is not carried by distal variants.** Reported with the same directness as the gradient result.
- `all twelve` — line 1319:
  > **What is NOT established:** A222V's own rho under restriction. Its position-cluster CI includes zero in **all twelve** restricted variants on both views. And `p_spec_adj` in every family here is a rank count on leave-one-out residuals of overlapping fits - not a calibrated tail probability and not a decision rule.
- `all twelve` — line 1368:
  > Read it with **line 828** (R = 10 is INSIDE the matched-deletion range, so nothing at R = 10 is attributable to the removed positions), with the CI caveat printed in the D15 verdict (A222V's position-cluster CI includes zero in **all twelve** restricted variants on both views), and with **section 5 above**, which is the only place the two axes are put together. **That single OUTSIDE flag, on both views at two radii, is the session's main result: it is the first measurement in this project that separates "tied to the residue" from "tied to the spatial neighbourhood of the residue", and it resolves that separation against the long-range reading.**

**Branch decision (pre-registered):** D18-G2 PASS (Phase 1's own routine reproduces the published CI), D18-G1 42/42 PASS, **D18-G3 FAILED on all five row sets** (line 188): script 144's routine sampled cluster labels but counted rows, so every draw used a different row count than the reference. **D15's twelve position-cluster CIs are therefore WITHDRAWN and replaced by D18.5's corrected CIs (N_BOOT=10000, SEED=0, fresh rng per cell).**

**The twelve, corrected beside old (all values parsed from D18's output):**

| cell | corrected CI | excludes zero | old D15 CI | old excludes zero | width corr/old |
|---|---|---|---|---|---|
| full S1 R = 0 | [-0.107547, -0.045843] | **True** | [-0.110517, +0.052946] | no | 0.061703 / 0.163463 (0.38x) |
| full S1 R = 10 | [-0.110958, -0.047323] | **True** | [-0.108943, +0.053475] | no | 0.063634 / 0.162418 (0.39x) |
| full S1 R = 20 | [-0.100593, -0.030938] | **True** | [-0.106446, +0.077385] | no | 0.069655 / 0.183831 (0.38x) |
| full S1 R = 30 | [-0.067875, +0.012911] | **False** | [-0.126369, +0.088052] | no | 0.080787 / 0.214421 (0.38x) |
| full SEQ Rs = 25 | [-0.113697, -0.049861] | **True** | [-0.115971, +0.055396] | no | 0.063836 / 0.171367 (0.37x) |
| full SEQ Rs = 50 | [-0.106218, -0.039834] | **True** | [-0.107525, +0.069562] | no | 0.066384 / 0.177087 (0.37x) |
| H S1 R = 0 | [-0.114432, -0.046209] | **True** | [-0.136966, +0.050697] | no | 0.068223 / 0.187663 (0.36x) |
| H S1 R = 10 | [-0.116434, -0.046886] | **True** | [-0.133307, +0.060709] | no | 0.069547 / 0.194016 (0.36x) |
| H S1 R = 20 | [-0.102800, -0.025367] | **True** | [-0.131090, +0.087967] | no | 0.077433 / 0.219057 (0.35x) |
| H S1 R = 30 | [-0.071605, +0.023131] | **False** | [-0.145818, +0.109530] | no | 0.094736 / 0.255348 (0.37x) |
| H SEQ Rs = 25 | [-0.123753, -0.052020] | **True** | [-0.144621, +0.054462] | no | 0.071733 / 0.199083 (0.36x) |
| H SEQ Rs = 50 | [-0.114467, -0.039157] | **True** | [-0.135943, +0.073553] | no | 0.075311 / 0.209496 (0.36x) |

**Corrected statement.** 10/12 corrected CIs EXCLUDE zero (the old twelve: 0/12). The only two that still include zero are **full S1 R = 30** [-0.067875, +0.012911] and **H S1 R = 30** [-0.071605, +0.023131]. Corrected widths are 0.35–0.39x the old ones. On the R = 0 resolved rows the corrected CI is [-0.107547, -0.045843] and **excludes zero**, so the old sentence's explanation — that Phase 1's CI [-0.1173334458953319, -0.0595113844951173] excluded zero "only because it used a different bootstrap on the full row set" — is wrong: D18-G2 shows Phase 1's own routine reproduces that published CI exactly and D18-G4b shows the corrected routine reproduces it on the full rows (|diff| lo = 0.000e+00, hi = 7.633e-17 (gate < 1e-9)), while on the SAME resolved rows the corrected CI also excludes zero. The old resolved CI included zero because of the **bootstrap defect**, not the row set. What survives the correction: A222V's rho is established (CI excluding zero) at R = 0, 10, 20 and on both sequence sensitivities, and still NOT at R = 30 on either view.

**Cite this, not the old sentence.**

---

## K12 — "The gradient does NOT survive R = 20 A" / "YES at R = 10, NO at R = 20 and R = 30"

**Old text, at these REAL line numbers:**

- `does NOT survive R = 20` — line 829:
  > - **The gradient does NOT survive R = 20 A or R = 30 A.** At R = 20 full, the gradient falls to 0.6621 against a matched-deletion range of [+0.663147, +0.723051] - **OUTSIDE** (below), with 98.5% of random 121-position deletions giving a *higher* gradient. At R = 30 full it collapses to 0.4007 against [+0.615026, +0.731210] - far **OUTSIDE**, 100% of draws higher. The H frame is the same story and slightly worse: 0.6403 at R = 20 (outside, 97.5% higher) and 0.2413 at R = 30 (outside, 100% higher; its own bootstrap CI now includes zero, [-0.006500, +0.461143]).
- `does NOT survive R = 20` — line 1366:
  > > **The gradient does NOT survive R = 20 A or R = 30 A.** At R = 20 full, the gradient falls to 0.6621 against a matched-deletion range of [+0.663147, +0.723051] - **OUTSIDE** (below), with 98.5% of random 121-position deletions giving a *higher* gradient. At R = 30 full it collapses to 0.4007 against [+0.615026, +0.731210] - far **OUTSIDE**, 100% of draws higher.
- `NO at R = 20` — line 1245:
  > **DOES THE GRADIENT PERSIST AMONG DISTAL VARIANTS? YES at R = 10, NO at R = 20 and R = 30.**

**Recomputed from D15's own printed table with rule 11 (value, range, BOTH fractions, distance to nearest bound):**

| view | R | gradient | matched range | frac≤ | frac≥ | distance | D15's printed label | rule-11 flag |
|---|---|---|---|---|---|---|---|---|
| full | 10 | +0.689454255 | [+0.680406565, +0.706900130] | 0.2800 | 0.7200 | 0.009047690 | INSIDE | **INSIDE** |
| full | 20 | +0.662097177 | [+0.663147261, +0.723050983] | 0.0150 | 0.9850 | 0.001050084 | OUTSIDE | **MARGINAL** |
| full | 30 | +0.400678440 | [+0.615026439, +0.731210217] | 0.0000 | 1.0000 | 0.214347999 | OUTSIDE | **OUTSIDE** |
| H | 10 | +0.686580864 | [+0.675493864, +0.702835977] | 0.3750 | 0.6250 | 0.011087000 | INSIDE | **INSIDE** |
| H | 20 | +0.640347202 | [+0.642046793, +0.720171605] | 0.0250 | 0.9750 | 0.001699591 | OUTSIDE | **MARGINAL** |
| H | 30 | +0.241344907 | [+0.602546643, +0.726412751] | 0.0000 | 1.0000 | 0.361201736 | OUTSIDE | **OUTSIDE** |

**Doc targets, recomputed beside:** v full R20 0.662097177 vs 0.662097; lower bound 0.663147261 vs 0.663147; shortfall 0.001050084 vs 0.001; loss from R = 0 0.036376334 vs 0.036; v H R20 0.640347202 vs 0.640347; lower bound 0.642046793 vs 0.642047 — all six within their pre-registered tolerances.

**Corrected statement.** At R = 20 the gradient shortfalls are real but **MARGINAL under rule 11, not OUTSIDE**: full +0.662097177 sits 0.001050084 below its lower bound (distance 0.001050084 ≤ 0.002 AND the one-sided fraction 0.0150 ∈ [0.01, 0.05] — both MARGINAL criteria fire); H +0.640347202 sits 0.001699591 below its bound (distance 0.001699591, fraction 0.0250 — both fire). D15's own printed label for both cells was OUTSIDE; 2 cells are downgraded by rule 11 (full R=20, H R=20). **R = 30 IS the collapse:** full +0.400678440 vs [+0.615026439, +0.731210217] with frac≤ 0.0000 → OUTSIDE (distance 0.214347999); H +0.241344907 vs [+0.602546643, +0.726412751] → OUTSIDE. **R = 10 is INSIDE on both views**, so nothing at R = 10 is attributable to the removed positions (as the log already says at line 828). "NO at R = 20" overstates the R = 20 result: it is MARGINAL, and D21 independently reproduced that flag (3D-k at k = 121/86 → MARGINAL).

**Cite this, not the old sentence.**

---

## K13 — "much more destructive per position"

**Old text, at these REAL line numbers:**

- `much more destructive per position` — line 832:
  > - **The sequence sensitivities disagree with the 3D ones at the same nominal severity.** Removing |p - 222| <= 50 (495 positions retained, full) leaves the gradient at **+0.680934** with a CI excluding zero, versus +0.4007 for the 3D R = 30 filter. Removing |p-222| <= 50 in *sequence* is much more destructive per position than removing 30 A in *space* (247 positions). **The statistic is tracking 3D distance to 222, not sequence distance to 222.**
- `far less destructive` — line 1243:
  > Sequence sensitivities (S1 only, reported, none selected): Rs = 25 leaves the gradient at **+0.695361** (full) / **+0.689215** (H); Rs = 50 leaves it at **+0.680934** / **+0.650045**. Both with CIs excluding zero. **Removing |p-222| <= 50 in sequence (495 positions retained) is far less destructive than removing 30 A in space (247 positions).**

**Script 144's SEQ removal definition, quoted from the source at run time:**

    scripts/144_phase2_diag3_farvariants.py line 569: >>>         for Rs in RS_SEQ:
    scripts/144_phase2_diag3_farvariants.py line 570: >>>             rm = POSV[np.abs(POSV - 222) <= Rs]
    scripts/144_phase2_diag3_farvariants.py line 571: >>>             run(f"S1  SEQ Rs = {Rs}  (keep |p - 222| > {Rs})", view,
    scripts/144_phase2_diag3_farvariants.py line 572: >>>                 resolved & ~np.isin(POSV, rm))

**Recomputed beside the doc's targets:**

| quantity | recomputed | doc target |
|---|---|---|
| positions removed by SEQ Rs=50 | 100 | 100 |
| SEQ drop | 0.017539659 | 0.0175 |
| SEQ per position | 0.00017539659 | 0.000175 |
| 3D drop | 0.297795071 | 0.2978 |
| 3D positions removed | 247 | 247 |
| 3D per position | 0.00120564806 | 0.001206 |

**Corrected statement.** The Rs = 50 sequence window removes **100** resolved positions (595 resolved − 495 retained, confirmed from script 144's definition above and cross-gated to D18.5's cluster counts) and lowers the gradient by **0.017539659** = **1.754e-04 per position**; 3D R = 30 removes **247** positions and lowers it by **0.297795071** = **1.206e-03 per position**. So **per position the 3D removal is 6.87x MORE destructive than the sequence removal** — line 832's "much more destructive per position" has the direction backwards, and it also contradicts its own preceding sentence and the SUMMARY at line 1243 ("far less destructive"), which the numbers DO support as a **total-drop** statement (unequal k: 100 vs 247). Both comparisons — total and per position — say the same thing: the 3D removal is the destructive one at these native windows.


**What D21 adds (equal k, parsed from D21's answer block):** the ordering is NOT stable across k. At the seq50 slot (k = 100) 3D-k is more destructive but **both SEQ-k and 3D-k are INSIDE the RANDOM-100 range → the claim is WITHDRAWN at that slot** (D21 line 680). At the R30 slot (k = 247) **SEQ-k is MORE destructive than 3D-k on both metrics** (gradient drop +0.323615684 vs +0.297795071; rho attenuation +0.058252020 vs +0.049325395) and both are OUTSIDE their RANDOM-247 ranges (D21 line 692). Overall: **SUPPORTED at 0 of 8 slots**, WITHDRAWN (both inside) at 3 of 8 (full: seq25, seq50; H: seq25), flagged-not-decided at the other 5; the two views give the same verdict at every slot: **NO** (D21 overall lines [726, 727]).

**Cite this, not the old sentence.**

---

## K14 — axis conflation: D15 cannot separate residue from neighbourhood

**Old text, at these REAL line numbers:**

- `first measurement in this project that separates` — line 1368:
  > Read it with **line 828** (R = 10 is INSIDE the matched-deletion range, so nothing at R = 10 is attributable to the removed positions), with the CI caveat printed in the D15 verdict (A222V's position-cluster CI includes zero in **all twelve** restricted variants on both views), and with **section 5 above**, which is the only place the two axes are put together. **That single OUTSIDE flag, on both views at two radii, is the session's main result: it is the first measurement in this project that separates "tied to the residue" from "tied to the spatial neighbourhood of the residue", and it resolves that separation against the long-range reading.**
- `the two effects are separable` — line 1317:
  > **The honest reading, and the one I will not soften:** **the two effects are separable, and they are separable because they live on different axes.** What is tied to **position 222** is A222V's *excess over its own site* - a substitution-specificity statement that is unusually robust to every adjustment tried here. What is tied to **the region around 222, in space** is the *gradient itself*, and that gradient is carried by target variants within about 30 A of 222 rather than by distal ones. The statistic is **not** a pure spatial-overlap effect with no long-range content: at R = 30 A a gradient of +0.40 remains, and D15's H-frame CI there even includes zero. It is **not** purely position-specific either: the neighbourhood of 222 behaves systematically like A222V in both sequence and space.
- `Cannot be separated` — line 1310:
  > **"Cannot be separated" - and that is now a measured conclusion rather than an open question, because the two candidate explanations were tested on different axes and only one of them survived its test.**
- `resolves that separation against the long-range reading` — line 1368:
  > Read it with **line 828** (R = 10 is INSIDE the matched-deletion range, so nothing at R = 10 is attributable to the removed positions), with the CI caveat printed in the D15 verdict (A222V's position-cluster CI includes zero in **all twelve** restricted variants on both views), and with **section 5 above**, which is the only place the two axes are put together. **That single OUTSIDE flag, on both views at two radii, is the session's main result: it is the first measurement in this project that separates "tied to the residue" from "tied to the spatial neighbourhood of the residue", and it resolves that separation against the long-range reading.**

**The internal contradiction, first:** the log's own summary opens section 5 with "Cannot be separated" (line 1310) and closes it with "the two effects are separable" (line 1317); line 1368 then calls this "the first measurement in this project that separates ...". Both cannot stand.

**The axis problem (the log's own K8, line 1304):** D15 varies the **target variants'** 3D distance to 222 (`d3_222(p) > R`) and recomputes the gradient; it never varies, restricts or controls the **background's** location. D14 (which bins backgrounds) and D15 (which filters target variants) are, as K8 already recorded, "TWO DIFFERENT AXES". A design that only chooses which target variants are scored cannot separate "tied to position 222" from "tied to the spatial neighbourhood of residue 222": no background is ever moved into or out of 222's neighbourhood, and every same-site comparison (K15 below) is at exactly d3 = 0. **Position 222 versus its neighbourhood remains UNDETERMINED by this design.**

**What D15 and D20 DO show — about where the signal lives AMONG TARGET VARIANTS:**

- D15 (rule 11, corrected flags): removing target variants within 30 A drops the gradient from +0.698473511 to +0.400678440 (full) and +0.688316871 to +0.241344907 (H) — **OUTSIDE the matched-deletion range on both views**; at 20 A both cells are **MARGINAL**, not OUTSIDE (see K12); at 10 A INSIDE on both.
- D20 (each cell against its own size-matched range): the most damaging single-shell removal is **(45,inf)** on both views (19.59% / 17.72% of R = 0, flag **OUTSIDE** both), while the shell that best preserves the gradient alone is **(30,45]** (48.61% / 42.94% retained) yet is itself flagged **OUTSIDE below** its own size-matched range. Gradient and rho orderings DIFFER (4 lines), all four top-two separations OVERLAP (4), and the R = 30 union effect is **4.9x (full) / 6.8x (H)** the sum of the first three shells' individual drops — a **POST-HOC** observation (IV log line 672), so "the signal lives within 30 A" cannot be attributed to any one shell.
- D21 (equal k): "3D, not sequence" is SUPPORTED at 0 of 8 slots (see K13).

**Corrected statement.** What the data support, with the same directness either way: **among target variants, the gradient signal is concentrated in the near-222 region in 3D and in the far shell's removal — and the design cannot say whether that is a property of position 222 itself or of its spatial neighbourhood.** Settling residue vs neighbourhood needs new data cached data cannot supply: **backgrounds placed in the neighbourhood of 222** (same shift machinery, varying background location), so that background location — not just target-variant distance — is manipulated.

**Cite this, not the old sentence.**

---

## K15 — "six independent constructions" / "fifth independent construction"

**Old text, at these REAL line numbers:**

- `independent construction` — line 1077:
  > - **A222V is rank 2 of 19 within Arm S under ALL FOUR models and BOTH views - eight cells, no exceptions.** This is now the fifth independent construction to give the same same-site answer (D13 raw, D13 shift-adjusted, D13 all-96, D16a isotonic, D16b isotonic-shift, M1-M4).
- `independent construction` — line 1284:
  > **D13:** A222V is rank **2/19 within Arm S** - one member (`A222_C`) of 18 is at or below it - and that is unchanged under raw rho, D9's exchangeable shift residual, D4's all-96 residual, D16a, D16b and all four joint models, on both views: **six independent constructions, one answer.** *** Rank fractions, n = 19, not tests. *** It cannot separate "the residue" from "the region".
- `independent construction` — line 1315:
  > - **For "tied to position 222 specifically":** A222V's own rho sits **below the entire Arm S mean** (-0.088 against -0.065, a gap of 0.023 against a site sd of 0.014) and it is the 2nd most negative of 19 same-site backgrounds in **six independent constructions and eight model-view cells, without a single exception** - raw, shift-adjusted exchangeable, all-96 in-sample, isotonic, isotonic two-stage, and all four exact joint models. **There is no 0 A discontinuity** in the model-free picture: the 18 Arm S backgrounds at exactly 0 A sit at the same mean rho as the six 3D-nearest nulls 5-10.5 A away (difference -0.000227, CI includes zero). Restricting to *distal* target variants at R = 10 A changes the gradient by 0.009 and changes nothing that can be attributed to the removed positions.
- `six independent` — line 1284:
  > **D13:** A222V is rank **2/19 within Arm S** - one member (`A222_C`) of 18 is at or below it - and that is unchanged under raw rho, D9's exchangeable shift residual, D4's all-96 residual, D16a, D16b and all four joint models, on both views: **six independent constructions, one answer.** *** Rank fractions, n = 19, not tests. *** It cannot separate "the residue" from "the region".
- `six independent` — line 1315:
  > - **For "tied to position 222 specifically":** A222V's own rho sits **below the entire Arm S mean** (-0.088 against -0.065, a gap of 0.023 against a site sd of 0.014) and it is the 2nd most negative of 19 same-site backgrounds in **six independent constructions and eight model-view cells, without a single exception** - raw, shift-adjusted exchangeable, all-96 in-sample, isotonic, isotonic two-stage, and all four exact joint models. **There is no 0 A discontinuity** in the model-free picture: the 18 Arm S backgrounds at exactly 0 A sit at the same mean rho as the six 3D-nearest nulls 5-10.5 A away (difference -0.000227, CI includes zero). Restricting to *distal* target variants at R = 10 A changes the gradient by 0.009 and changes nothing that can be attributed to the removed positions.

**Why they are one comparison, from D13's own header (parsed at run time):** 18 Arm S members, all at position ['222'], dist_222 = ['0'], d3_CA = ['0.0']; A222V shares them (dist_222 = 0, d3_CA = 0.000). Every distance covariate in M2, M3 and M4 therefore evaluates to the **same value (0) for all 19**, so the within-site ordering under those models depends **only on rho and the shift coefficient** (`mean|delta|`). The ordering can move only through that coefficient — and it does not.

**Each construction's shift coefficient (parsed from D16E's own OLS lines) with A222V's rank:**

| construction | shift coef (full) | shift coef (H) | A222V within-site rank |
|---|---|---|---|
| raw rho (no adjustment) | 0 | 0 | 2/19 (both views) |
| M1 | -0.726287 | -0.774750 | 2/19 (all 8 model-view cells) |
| M2 | -0.363298 | -0.418766 | 2/19 (all 8 model-view cells) |
| M3 | -0.418381 | -0.464836 | 2/19 (all 8 model-view cells) |
| M4 | -0.324445 | -0.338456 | 2/19 (all 8 model-view cells) |

**A222V's shift value itself:** mean&#124;delta&#124; = 0.070330 (full) / 0.069403 (H) — rank **3 of 19** (full) and **3 of 19** (H) among the site's shift values, which span 0.066545–0.105150 (full) and 0.067910–0.107653 (H).  A222V's value is inside that site-level spread, at neither end (its rank is neither 1 nor 19 on either view).

**Corrected statement.** The "6" independent constructions are **one comparison (A222V vs its 18 same-site neighbours) evaluated under shift adjustments with coefficients 0, -0.726287, -0.363298, -0.418381, -0.324445 (full view)** — because all distance terms are constant within the site. Recomputing each construction's within-site residual from its own printed coefficient reproduces A222V's rank **2/19 in all 8 model-view cells** (max &#124;recomputed − printed&#124; = 8.2e-07) and D13's raw 2/19 on both views: that is **ONE comparison that is stable to shift adjustment, not six confirmations**. The plain probability that a random member of 19 exchangeable values ranks 2nd or better is **2/19 = 0.105263** (doc target 0.105; *** rank fraction, n = 19, not a test ***).

**Cite this, not the old sentence.**

---

## K16 — "A222V's own negative association is roughly halved by removing target variants within 30 A"

**Old text, at these REAL line numbers:**

- `roughly halved` — line 1248:
  > **DOES THE ANCHOR PERSIST? Only weakly.** A222V's rho falls monotonically -0.0767 -> -0.0792 -> -0.0659 -> **-0.0274** (full) and -0.0804 -> -0.0821 -> -0.0636 -> **-0.0244** (H); `p_spec` holds at 2/78 = 0.037975 through R = 20 and rises to 0.063291 (full) and 0.101266 (H) at R = 30. **A222V's own negative association is roughly halved by removing target variants within 30 A of 222.**
- `roughly halved` — line 1314:
  > - **Against "tied to position 222 specifically" / for "the region around 222":** the gradient of rho_b against 3D distance is real and large (+0.732 unrestricted), and **removing target variants within 20-30 A of 222 collapses it to +0.400 (full) and +0.241 (H) - outside the matched-deletion range, on both views.** Every distance-aware adjustment puts A222V's `p_spec_adj` **above** the frozen thresholds: isotonic 0.19-0.75, parametric 0.13-1.00. The log1p distance forms **mispredict the entire distance-0 site** (Arm S predicted -0.141 and -0.188 against an observed -0.065, overshoots of 0.076 and 0.123, several times the site's own sd of 0.015) and predict A222V **below every observed null**. A222V's own association is roughly halved by deleting near-222 target variants.
- `is halved` — line 833:
  > - **THE ANCHOR PERSISTS AMONG DISTAL VARIANTS, WEAKENING MONOTONICALLY.** A222V's rho on the retained rows: -0.0767 (R=0) -> -0.0792 (R=10) -> -0.0659 (R=20) -> **-0.0274** (R=30) full; -0.0804 -> -0.0821 -> -0.0636 -> **-0.0244** H. `p_spec` stays at 2/78 = 0.037975 through R = 20 and rises to 4/78 = 0.063291 at R = 30 (full) and 7/78 = 0.101266 (H). **A222V's own negative association is halved by removing target variants within 30 A of 222.**

**Recomputed per D19 (falls from D15's printed rhos; matched ranges and rule-11 flags from D19's summary table):**

| view | rho R=0 | rho R=30 | fall | remaining | matched range (rho) | frac≤ | frac≥ | distance | flag |
|---|---|---|---|---|---|---|---|---|---|
| full | -0.076685523 | -0.027360127 | 64.3217% | 35.68% | [-0.098275992, -0.047691236] | 1.0000 | 0.0000 | 0.020331109 | **OUTSIDE** |
| H | -0.080432398 | -0.024367374 | 69.7045% | 30.30% | [-0.104682320, -0.054086245] | 1.0000 | 0.0000 | 0.029718871 | **OUTSIDE** |

**The other four cells (rule 11):** full R=10 INSIDE, full R=20 INSIDE, H R=10 INSIDE, H R=20 MARGINAL — counts: rho INSIDE 3, OUTSIDE 2, MARGINAL 1 of 6 cells.


**Corrected statement.** At R = 30 A222V's association loses **64.3217% (full) / 69.7045% (H)** of its magnitude — 35.68% / 30.30% remains — so **"roughly halved" UNDERSTATES the fall: it is about two-thirds**. **The fall IS attributable at R = 30**: the restricted rho sits **OUTSIDE** its own matched-deletion range on both views (full value -0.027360127 vs range [-0.098275992, -0.047691236], frac<= 1.0000, frac>= 0.0000, distance to nearest bound 0.020331109; H value -0.024367374 vs range [-0.104682320, -0.054086245], frac<= 1.0000, frac>= 0.0000, distance to nearest bound 0.029718871) — beyond what deleting the same 247 / 172 random positions produces. **It is NOT attributable at R = 10** (INSIDE both views) **nor at R = 20 full** (INSIDE); H R = 20 is **MARGINAL** (value -0.063596629 vs range [-0.096713499, -0.064444959], frac<= 0.9750, frac>= 0.0250, distance to nearest bound 0.000848330). Over all six cells: INSIDE 3, OUTSIDE 2, MARGINAL 1.

**Cite this, not the old sentence.**

---

## Limits of these corrections

- K11 replaces a **withdrawn set of CIs** with D18.5's corrected CIs; the withdrawal is D18's finding (G3 FAILED), not a re- judgement here.
- K12's rule-11 flags are recomputed from D15's **printed** percentiles and fractions using rule 11's decision rule verbatim (flag11, `phase2_diag4.py` lines 419-435). The raw draws are not re-derived in this script; D21's G1g already showed those printed summaries re-derive from the corrected routine to ≤ 4.95e-10 on bounds and exactly on fractions.
- K13's per-position figures compare NATIVE windows (unequal k) as well as D21's equal-k slots; both are stated, neither is substituted for the other.
- K14 is a **category error** (which axis a design manipulates), corrected by pointing at what D15 and D20 measured; the non-additivity number it cites is D20's own POST-HOC observation, labelled as such.
- K15 concerns **how many independent comparisons there are**, not any value: every rank quoted in the old sentences reproduces exactly.
- K16 restates an effect size D19 already computed; no frozen verdict is redefined and no threshold is touched.
- No bootstrap, no permutation, no model scoring; stdlib only. The frozen `PHASE2_PREREG.md` verdicts are untouched by this file.

---

*Generated by `scripts/152_phase2_diag4_corrections.py`; no resampling. Full verbatim output: `PHASE2_DIAG4_D22_FULL_OUTPUT.txt`.*
